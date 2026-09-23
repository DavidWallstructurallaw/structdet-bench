"""Lossless passive study compilation into the existing M/V/L contracts.

Only explicitly inventoried snapshots enter a private temporary workspace.
Original carrier bytes, scientific parameters and evidence gates are retained.
No submitted program is executed, no evidence is synthesized, and no public
output is written. Publication and human authentication are separate activities.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Any, Mapping

from .contracts import Diagnostic, ExactNumber, InputError, freeze
from .local_io import ReadLimits, load_bundle, relative_parts
from .pipeline import Analysis, analyze_bundle, validate_bundle
from .study_collection import inspect_collection
from .study_evidence import inspect_study_evidence, parse_evidence_qualification_bytes
from .study_records import LoadedStudy, _limits, _references, _serialize
from .study_review import _StudyView


def _known(value):
    return value.get("value") if isinstance(value, Mapping) and value.get("state") == "known" else None


def _ref(row):
    return {key: row[key] for key in ("record_type", "record_id", "record_version")}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _key(row):
    return row["record_type"], row["record_id"]


def _decimal(value):
    return value.decimal if isinstance(value, ExactNumber) else Decimal(str(value))


def _equal(left, right, numeric=False):
    if numeric and left is not None and right is not None:
        try:
            return _decimal(left) == _decimal(right)
        except (ArithmeticError, ValueError, TypeError):
            return False
    return _serialize(left) == _serialize(right)


def _time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _closure(graph, seeds):
    found, pending = set(seeds), deque(seeds)
    while pending:
        for child in graph.get(pending.popleft(), ()):
            if child not in found:
                found.add(child)
                pending.append(child)
    return found


def _qualification_packet(view, packet_id, limits):
    if packet_id is None:
        return {}
    snapshot = view.snapshot(packet_id)
    if snapshot is None:
        return {}
    parsed = parse_evidence_qualification_bytes(snapshot.content, limits)
    if parsed.has_errors:
        raise InputError("qualification_packet_rejected")
    return parsed.data


def _corrections(view, qualification):
    """Follow actual dependencies, never lineage-only or replacement edges.

    Supersession invalidates the old subject and dependants. A replacement is
    fresh only when its own ordinary references and qualification are fresh.
    Cyclic evidence associations are safe because closure visits each ID once.
    """
    records, graph = view.records, defaultdict(set)
    registrations = {r["study_version"]: r for r in records.values() if r["record_type"] == "study_registration"}
    for row in records.values():
        if row["record_type"] != "correction_incident":
            for path, ref in _references(row):
                if row["record_type"] == "extraction" and path.startswith(".positions["):
                    # Selected artifacts are outputs of the extraction. Source
                    # or extraction corrections invalidate their evidence;
                    # challenging one output does not invalidate its siblings.
                    if any(p["selection"] == "selected" and _known(p["artifact_ref"]) == ref
                           for p in row["positions"]):
                        graph[row["record_id"]].add(ref["record_id"])
                    continue
                if not path.startswith((".lineage_refs[", ".supersedes.")):
                    graph[ref["record_id"]].add(row["record_id"])
        # A schema/core revision reaches every observation in that version,
        # even if a caller omitted a redundant explicit depends_on edge.
        if row["record_type"] != "study_registration":
            graph[registrations[row["study_version"]]["record_id"]].add(row["record_id"])
    evidence = {r["evidence_id"]: r for r in qualification.get("evidence", ())}
    for row in qualification.get("qualifications", ()):
        aid = row["artifact_ref"]["record_id"]
        refs = [*row["validation_refs"]]
        if _known(row["judgment_ref"]):
            refs.append(_known(row["judgment_ref"]))
        for eid in row["essential_evidence_ids"]:
            ev = evidence.get(eid)
            if ev:
                refs.append(ev["source_ref"])
                if _known(ev["reviewer_ref"]):
                    refs.append(_known(ev["reviewer_ref"]))
        for ref in refs:
            graph[ref["record_id"]].add(aid)
    seeds, changes = set(), []
    schema_changed = False
    for row in records.values():
        old_ref = _known(row["supersedes"])
        if old_ref:
            old = records[old_ref["record_id"]]
            seeds.add(old["record_id"])
            schema_changed |= row["record_type"] in {"study_registration", "core_catalog"}
            changes.append({"kind": "supersession", "source_id": old["record_id"], "replacement_id": row["record_id"]})
    incidents = []
    for row in view.current:
        if row["record_type"] != "correction_incident":
            continue
        affected = {ref["record_id"] for ref in row["affected_refs"]}
        active = row["action_status"] != "rejected"
        if active:
            seeds.update(affected)
            schema_changed |= any(records[r]["record_type"] in {"study_registration", "core_catalog"} for r in affected)
        readable = bool(row["evidence_refs"]) and all(
            records[r["record_id"]]["record_type"] == "artifact" and view.artifact(r["record_id"])[1] is not None
            for r in row["evidence_refs"])
        incidents.append({"incident_id": row["record_id"], "kind": row["kind"],
            "action_status": row["action_status"], "declared_performed": row["action_status"] == "performed",
            "performed_record_complete": row["action_status"] == "performed" and readable
                and _known(row["reviewer_authority"]) is not None,
            "affected_record_ids": sorted(affected),
            "replacement_record_ids": [r["record_id"] for r in row["replacement_refs"]],
            "rollback_record_ids": [r["record_id"] for r in row["rollback_refs"]],
            "reanalysis_record_ids": [r["record_id"] for r in row["reanalysis_refs"]],
            "requires_resolution": active, "actual_action_authenticated": False})
    invalid = _closure(graph, seeds)
    affected_artifacts = {rid for rid in invalid if records[rid]["record_type"] == "artifact"}
    affected_artifacts.update(records[rid]["artifact_ref"]["record_id"] for rid in invalid
        if records[rid]["record_type"] in {"human_review", "adjudication", "validation_receipt"})
    # Changes to the accepted reference partition affect all conditions; no
    # condition can keep its former favorable cut while another is revised.
    cells = set()
    for row in records.values():
        if row["record_type"] == "collection_ledger" and row["record_id"] in invalid:
            cells.add((row["block_id"], row["condition"]))
        if row["record_type"] == "extraction" and (row["record_id"] in invalid or any(
                _known(p["artifact_ref"]) and _known(p["artifact_ref"])["record_id"] in affected_artifacts for p in row["positions"])):
            call = records[row["collection_ref"]["record_id"]]
            cells.add((call["block_id"], call["condition"]))
    if schema_changed:
        cells.update((f"P{b:02d}", c) for b in range(1, 7) for c in "ABC")
    comparisons = []
    for name, conditions in (("P1-B-vs-A", "AB"), ("P5-C-vs-A", "AC")):
        if any(b != "P00" and c in conditions for b, c in cells):
            comparisons.append(name)
    return {"invalidated_record_ids": sorted(invalid), "schema_review_required": schema_changed,
        "affected_artifact_ids": sorted(affected_artifacts),
        "affected_cells": [{"block_id": b, "condition": c} for b, c in sorted(cells)],
        "registered_comparisons_to_recompute": comparisons, "supersessions": changes,
        "incidents": incidents,
        "historical_output_refs": [{"receipt_id": r["record_id"], "outputs": [
            {"role": o["role"], "sha256": o["sha256"], "size_bytes": o["size_bytes"]} for o in r["outputs"]]}
            for r in records.values() if r["record_type"] == "compilation_receipt" and r["record_id"] in invalid],
        "architectural_components": [{"claim_id": c["claim_id"], "components": [
            {"component_id": x["component_id"], "version_state": x["version"]["state"],
             "version": _known(x["version"]), "contents_state": x["contents_state"],
             "artifact_ids": [r["record_id"] for r in x["artifact_refs"]],
             "invalidated_artifact_ids": [r["record_id"] for r in x["artifact_refs"] if r["record_id"] in invalid]}
            for x in c["components"]]} for c in qualification.get("claims", ())],
        "prior_outputs_preserved": True, "reanalysis_performed": False,
        "substantive_validation_performed": False}


@dataclass(frozen=True)
class Compilation:
    diagnostics: tuple[Diagnostic, ...] = ()
    mapping_errors: tuple[Mapping[str, Any], ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    corrections: Mapping[str, Any] = field(default_factory=dict)
    qualification: Mapping[str, Any] = field(default_factory=dict)
    files: Mapping[str, bytes] = field(default_factory=dict, repr=False)
    bundle_path: str | None = None
    limits: ReadLimits = field(default_factory=ReadLimits, repr=False)
    substantive_validation_performed: bool = False

    @property
    def has_errors(self):
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0

    @property
    def compiled(self):
        return bool(self.files) and self.bundle_path in self.files and not self.mapping_errors and not self.has_errors

    def as_dict(self):
        # Files and evidence prose stay in the restricted exact input snapshot.
        return json.loads(_serialize({"version": "0.1", "compiled": self.compiled,
            "disposition": "eligible" if self.compiled else "withheld", "exit_code": self.exit_code,
            "mapping_errors": self.mapping_errors,
            "diagnostics": [{"code": d.code, "severity": d.severity} for d in self.diagnostics],
            "provenance": self.provenance, "corrections": self.corrections, "qualification": self.qualification,
            "substantive_validation_performed": False}))


def _stage(root, files):
    for name, content in files.items():
        parts = relative_parts(name)
        target = root.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(content)


class _Compiler:
    def __init__(self, loaded, packet_id, receipt_id, limits):
        self.view = _StudyView(loaded)
        self.limits = _limits(limits)
        self.registration = next(r for r in self.view.current if r["record_type"] == "study_registration")
        self.profile = self.registration["requested_profile"]
        self.assessment = inspect_study_evidence(loaded, packet_id, limits)
        self.issues = list(self.assessment.diagnostics)
        self.errors, self.provenance = [], {}
        self.scope_restrictions = set()
        self.q = _qualification_packet(self.view, packet_id, limits)
        self.submissions = {}
        if self.profile == "hero_sort_abc_v1" and any(r["record_type"] == "collection_ledger" for r in self.view.current):
            self.submissions = {s["primary_record_id"]: s["submission"] for s in inspect_collection(loaded).slots
                                if s["primary_record_id"] and s["submission"]}
        self.correction = _corrections(self.view, self.q)
        self.invalid = set(self.correction["invalidated_record_ids"])
        self.superseded = {_known(r["supersedes"])["record_id"] for r in self.view.records.values() if _known(r["supersedes"])}
        self.current = [r for r in self.view.current if r["record_id"] not in self.superseded]
        self.maps = defaultdict(list)
        self.receipt = None
        if receipt_id is not None:
            self.receipt = self.view.records.get(receipt_id)
            if (self.receipt is None or self.receipt["record_type"] != "compilation_receipt"
                    or self.receipt["study_version"] != self.view.raw["study_version"]):
                raise InputError("compilation_mapping_receipt_unavailable")
            if receipt_id in self.invalid:
                self.fail("id_map", "compilation_mapping_receipt_stale", self.receipt)
            for item in self.receipt["id_map"]:
                key = item["target_record_type"], item["target_record_id"]
                if item["source_ref"] in self.maps[key]:
                    raise InputError("duplicate_compilation_mapping")
                self.maps[key].append(item["source_ref"])
            for snapshot in self.receipt["input_snapshots"]:
                actual = self.view.snapshot(snapshot["packet_id"])
                if actual is None or actual.sha256 != snapshot["sha256"] or snapshot["study_version"] != self.view.raw["study_version"]:
                    self.fail("input_snapshots", "stale_compilation_input", self.receipt)

    def fail(self, field, reason, source=None, *, missing=False):
        row = {"field": field, "reason": reason, "source_ref": _ref(source or self.registration)}
        if row not in self.errors:
            self.errors.append(row)
            self.issues.append(Diagnostic(reason, "study_bridge", "study_bridge", field,
                                          severity="warning" if missing else "error"))

    def check(self, field, left, right, source=None, *, numeric=False):
        if not _equal(left, right, numeric):
            self.fail(field, "known_operational_fact_conflict", source)

    def known(self, field, left, right, source=None, *, numeric=False):
        # A known null is a real seed/retry observation, not unknown knowledge.
        if isinstance(left, Mapping) and left.get("state") == "known":
            if not isinstance(right, Mapping) or right.get("state") != "known":
                self.fail(field, "known_operational_fact_lost", source)
            else:
                self.check(field, left["value"], right["value"], source, numeric=numeric)

    def mapped(self, row, kind=None):
        refs = self.maps.get(_key(row), ())
        return [self.view.records[r["record_id"]] for r in refs if kind is None or r["record_type"] == kind]

    def artifact_match(self, op_ref, old_ref, field, source):
        if not isinstance(op_ref, Mapping) or op_ref.get("state") != "known":
            return
        op = op_ref["value"]
        legacy = _known(old_ref)
        if legacy is None or op not in self.maps.get((legacy["record_type"], legacy["record_id"]), ()):
            self.fail(field, "artifact_identity_mapping_missing", source)

    def select_carrier(self):
        protocol = self.registration["protocol"]
        descriptor = _known(protocol["legacy_profile_input"])
        longitudinal = _known(protocol["longitudinal_input"])
        reference = descriptor["artifact_ref"] if descriptor else longitudinal if self.profile == "structdet_longitudinal_v1" else None
        if reference is None:
            self.fail("legacy_profile_input", "required_legacy_fields_unrepresentable", missing=True)
            return None
        carrier, snap = self.view.artifact(reference["record_id"])
        if carrier is None or snap is None:
            self.fail("legacy_profile_input", "legacy_carrier_unavailable", missing=True)
            return None
        if carrier["record_id"] in self.invalid:
            self.fail("legacy_profile_input", "legacy_carrier_stale", carrier)
        if descriptor and longitudinal:
            other, other_snap = self.view.artifact(longitudinal["record_id"])
            if other_snap is None or other_snap.content != snap.content:
                self.fail("longitudinal_input", "incompatible_longitudinal_carriers")
        return carrier, snap

    def carrier_files(self, snap):
        # Stage only verified inventory members under the carrier's root.
        # The legacy reader cannot reach any uninventoried host path.
        parent = PurePosixPath(snap.path).parent
        files, packets = {}, {}
        for pid in self.view.inventory:
            member = self.view.snapshot(pid)
            if member is None:
                continue
            path = PurePosixPath(member.path)
            if not path.is_relative_to(parent):
                continue
            relative = path.relative_to(parent).as_posix()
            relative_parts(relative)
            if relative in files and files[relative] != member.content:
                raise InputError("carrier_inventory_collision")
            files[relative] = member.content
            packets[relative] = pid
        return files, packets

    def identity(self, bundle):
        m = bundle.manifest.data
        self.check("study_id", self.view.raw["study_id"], m["study_id"])
        self.check("data_role", self.view.raw["material_role"], m["data_role"])
        if self.assessment.fixture_context and m["data_role"] != "fixture":
            self.fail("data_role", "fixture_cannot_enter_nonfixture_carrier")
        cfg = m["analysis_config"]
        self.check("assignment_evidence_policy_id", self.view.raw["evidence_policy"], cfg["assignment_evidence_policy_id"])
        self.check("assignment_evidence_policy_version", "0.1", cfg["assignment_evidence_policy_version"])
        self.check("source_pins", self.registration["source_pins"], {p["source_id"]: p["sha256"] for p in m.get("source_pins", ())})
        self.pins = {kind: {p[kind + "_id"] for p in cfg[kind + "_pins"]} for kind in ("assignment", "validity")}
        attempts = [e.record.data for e in bundle.records if e.record and e.record.record_type == "attempt"]
        for name, amount in (("max_calls", len(attempts)), ("max_positions", sum(
                _known(a["planned_candidate_count"]) or 0 for a in attempts))):
            ceiling = _known(self.registration["protocol"]["budget"][name])
            if ceiling is not None and amount > ceiling:
                # A supplied over-budget history remains an observation. It
                # restricts the registered claim without deleting its data.
                self.scope_restrictions.add("registered_budget_exceeded")
        for protocol in m["protocols"]:
            self.check("protocol.version", self.registration["protocol"]["protocol_version"], protocol["generation_protocol_version"])
            controls = self.registration["protocol"]["controls"]
            self.known("protocol.seed", controls["seed"], protocol["seed"])
            settings = _known(protocol["decoding_settings"])
            for name, target in (("temperature", "temperature"), ("top_p", "top_p"), ("presence_penalty", "presence_penalty"),
                                 ("frequency_penalty", "frequency_penalty"), ("output_allowance", "max_output_tokens")):
                if name == "temperature" and self.registration["protocol"]["design"] == "sorting_abc":
                    continue  # The fixed condition-specific temperatures apply.
                right = {"state": "known", "value": settings[target]} if isinstance(settings, Mapping) and target in settings else {}
                self.known("protocol." + name, controls[name], right, numeric=True)
        for frame in m["frames"]:
            for name, value in self.registration["pins"].items():
                self.check("frame." + name, value, frame[name])
            for name, value in self.registration["frame_definition"].items():
                if name == "load_bearing_invariants":
                    if value:
                        self.check("frame." + name, value, frame[name])
                elif value["state"] == "known":
                    self.check("frame." + name, value["value"], frame[name])
        ext = cfg.get("extensions", {})
        active = {key for key in ("comparison", "longitudinal") if key in ext}
        expected = {"m_only": set(), "hero_sort_abc_v1": {"comparison"}, "structdet_longitudinal_v1": {"longitudinal"}}[self.profile]
        self.check("requested_profile", sorted(expected), sorted(active))
        if "longitudinal" in active:
            longitudinal = ext["longitudinal"]
            for name in ("study_id", "study_version"):
                self.check("longitudinal." + name, self.view.raw[name], longitudinal[name])
            self.check("longitudinal.data_role", self.view.raw["material_role"], longitudinal["data_role"])
            self.check("longitudinal.source_pins", self.registration["source_pins"], longitudinal["source_pins"])
            if self.registration["protocol"]["design"] != "supplied_longitudinal":
                self.fail("longitudinal", "explicit_longitudinal_design_required")

    def mappings(self, bundle):
        self.legacy = {_key(e.record.data): e.record.data for e in bundle.records if e.record is not None}
        self.samples = {r["sample_id"]: r for r in self.legacy.values() if r["record_type"] == "realization"}
        self.cells = {c["analysis_cell_id"]: c for c in bundle.manifest.data["cells"]}
        self.selections = {r["analysis_cell_id"]: r for r in bundle.manifest.data["analysis_config"]["selection"]}
        allowed = {"frame": {"study_registration"}, "protocol": {"study_registration", "collection_ledger"},
            "cell": {"study_registration", "collection_ledger"}, "attempt": {"collection_ledger"},
            "realization": {"extraction"}, "assignment": {"human_review", "adjudication"},
            "validity": {"validation_receipt", "human_review", "adjudication"},
            "artifact": {"artifact"}, "raw_artifact": {"artifact"}}
        original_artifacts = defaultdict(set)
        for key, refs in self.maps.items():
            if key not in self.legacy:
                self.fail("id_map", "legacy_mapping_target_missing", self.receipt)
            for ref in refs:
                row = self.view.records[ref["record_id"]]
                if key[0] in allowed and row["record_type"] not in allowed[key[0]]:
                    self.fail("id_map", "mapping_record_type_conflict", row)
                if key[0] in {"artifact", "raw_artifact"}:
                    original_artifacts[row["record_id"]].add(key)
                if row["record_id"] in self.invalid or row["record_id"] in self.superseded:
                    self.fail("id_map", "stale_mapping_source", row)
        if any(len(targets) > 1 for targets in original_artifacts.values()):
            self.fail("id_map", "original_artifact_identity_duplicated")
        # An operational event cannot disappear into an unrelated carrier.
        mapped = {ref["record_id"] for refs in self.maps.values() for ref in refs}
        for row in self.current:
            if row["record_type"] in {"collection_ledger", "extraction"} and row["record_id"] not in mapped:
                self.fail("id_map", "operational_event_unmapped", row)
        inspections = {r.record_key: r for r in bundle.artifacts}
        for old in self.legacy.values():
            if old["record_type"] in {"artifact", "raw_artifact"}:
                for op in self.mapped(old, "artifact"):
                    _, snap = self.view.artifact(op["record_id"])
                    actual = inspections.get(old["record_type"] + ":" + old["record_id"])
                    if snap is None or actual is None or actual.actual_sha256 != snap.sha256:
                        self.fail("artifact.content", "mapped_artifact_bytes_conflict", op)
                    elif op["artifact_role"] == "raw_response" and old["record_type"] != "raw_artifact":
                        self.fail("artifact.role", "raw_response_role_conflict", op)
            elif old["record_type"] == "protocol":
                for op in self.mapped(old, "study_registration"):
                    self.check("protocol.version", op["protocol"]["protocol_version"], old["generation_protocol_version"], op)
                    self.known("protocol.seed", op["protocol"]["controls"]["seed"], old["seed"], op)

    def call(self, row):
        matches = [old for old in self.legacy.values() if old["record_type"] == "attempt" and _ref(row) in self.maps.get(_key(old), ())]
        if len(matches) != 1:
            self.fail("attempt", "call_requires_one_original_attempt_mapping", row)
            return None
        old = matches[0]
        self.known("attempt_id", row["attempt_id"], {"state": "known", "value": old["attempt_id"]}, row)
        if row["attempt_status"] != "unknown":
            self.check("attempt_status", row["attempt_status"], old["attempt_status"], row)
        self.known("planned_candidate_count", {"state": "known", "value": len(row["planned_positions"])}, old["planned_candidate_count"], row)
        self.artifact_match(row["raw_response_ref"], old["raw_response_ref"], "attempt.raw_response_ref", row)
        retry = _known(row["retry_of"])
        if retry:
            prior = _known(old["retry_of"])
            if prior is None or not any(ref["record_id"] == retry["record_id"] for ref in self.maps.get(("attempt", prior), ())):
                self.fail("retry_of", "retry_history_mapping_conflict", row)
        elif row["retry_of"]["state"] == "known":
            self.known("retry_of", row["retry_of"], old["retry_of"], row)
        cell = self.cells[old["analysis_cell_id"]]
        self.check("cell.prompt_block_id", row["block_id"], cell["prompt_block_id"], row)
        self.check("cell.condition_id", row["condition"], cell["condition_id"], row)
        for name in ("model_identifier", "model_family", "checkpoint_identifier"):
            self.known("cell." + name, row["deployment"][name], cell[name], row)
        protocol = self.legacy[("protocol", cell["generation_protocol_id"])]
        self.check("protocol.version", self.registration["protocol"]["protocol_version"], protocol["generation_protocol_version"], row)
        self.artifact_match(row["prompt_ref"], protocol["conditioning_context_ref"], "protocol.conditioning_context_ref", row)
        settings = _known(protocol["decoding_settings"])
        for name, target in (("temperature", "temperature"), ("top_p", "top_p"), ("presence_penalty", "presence_penalty"),
                             ("frequency_penalty", "frequency_penalty"), ("output_allowance", "max_output_tokens")):
            if row["controls"][name]["state"] == "known":
                right = {"state": "known", "value": settings[target]} if isinstance(settings, Mapping) and target in settings else {}
                self.known("protocol." + name, row["controls"][name], right, row, numeric=True)
        self.known("protocol.seed", row["controls"]["seed"], protocol["seed"], row)
        if self.profile == "hero_sort_abc_v1" and row["phase"] == "main" and retry is None:
            self.binding(row, old, cell)
        else:
            self.known("registered_call_order", {"state": "known", "value": row["registered_call_order"]}, old["registered_call_order"], row)
        selection = self.selections.get(old["analysis_cell_id"], {})
        planned = _known(selection.get("registered_positions"))
        group = _known(old["generation_group_id"])
        if retry is not None:
            # Extra attempts preserve history and never acquire new main slots.
            return old
        if planned is None or group is None:
            self.fail("registered_positions", "original_planned_positions_unrepresentable", row)
        else:
            positions = [p for p in planned if p["generation_group_id"] == group]
            if (len(positions) != len(row["planned_positions"])
                    or [p["within_group_index"] for p in positions] != list(row["planned_positions"])
                    or any(_known(p["attempt_id"]) != old["attempt_id"]
                           or p["registered_call_order"] != _known(old["registered_call_order"]) for p in positions)):
                self.fail("registered_positions", "original_planned_positions_conflict", row)
        return old

    def binding(self, row, attempt, cell):
        bindings = [r["payload"].get("extensions", {}).get("study_binding") for r in self.legacy.values()
                    if r["record_type"] == "evidence"]
        bindings = [b for b in bindings if b and b["block_id"] == row["block_id"] and b["condition_id"] == row["condition"]]
        if len(bindings) != 1:
            self.fail("study_binding", "unambiguous_study_binding_required", row)
            return
        binding = bindings[0]
        entries = [a for a in binding["attempts"] if a["group_index"] == row["group_index"]]
        if len(entries) != 1:
            self.fail("study_binding.attempts", "original_group_mapping_conflict", row)
            return
        entry = entries[0]
        self.known("study_binding.attempt_ref", {"state": "known", "value": _ref(attempt)}, entry["attempt_ref"], row)
        self.known("study_binding.global_order", {"state": "known", "value": row["registered_call_order"]}, entry["global_order"], row)
        if row["attempted_at"]["state"] == "known":
            if entry["recorded_at"]["state"] != "known" or _time(row["attempted_at"]["value"]) != _time(entry["recorded_at"]["value"]):
                self.fail("study_binding.recorded_at", "known_operational_fact_conflict", row)
        self.artifact_match(row["prompt_ref"], binding["sent_prompt"]["artifact_ref"], "study_binding.sent_prompt", row)
        for op, old, numeric in (("temperature", "temperature", True), ("top_p", "top_p", True),
                ("presence_penalty", "presence_penalty", True), ("frequency_penalty", "frequency_penalty", True),
                ("output_allowance", "max_output_tokens", True), ("tools_requested", "tools", False), ("seed", "generator_seed", True)):
            self.known("study_binding.controls." + old, row["controls"][op], binding["controls"][old]["actual"], row, numeric=numeric)
        self.known("study_binding.serving_identity", row["deployment"]["deployment_identifier"], binding["deployment"]["serving_identity"], row)
        self.known("study_binding.cap.convention", row["controls"]["cap_semantics"], binding["cap"]["convention"], row)
        supplied = self.submissions.get(row["record_id"])
        if supplied:
            for op, old, numeric in (("temperature", "temperature", True), ("top_p", "top_p", True),
                    ("presence_penalty", "presence_penalty", True), ("frequency_penalty", "frequency_penalty", True),
                    ("output_allowance", "max_output_tokens", True), ("tools_requested", "tools", False), ("seed", "generator_seed", True)):
                self.known("study_binding.requested." + old, supplied["requested_controls"][op], binding["controls"][old]["requested"], row, numeric=numeric)
                enforced = _known(supplied["enforced_controls"][op])
                if enforced is False and binding["controls"][old]["enforcement"] == "recorded":
                    self.fail("study_binding.enforcement." + old, "known_operational_fact_conflict", row)
            for name in ("tokenizer", "convention"):
                self.known("study_binding.cap." + name, supplied["cap"][name], binding["cap"][name], row)
            unit = _known(supplied["cap"]["unit"])
            if unit is not None:
                translated = {"model_token": "model_tokens"}.get(unit, unit)
                self.known("study_binding.cap.unit", {"state": "known", "value": translated}, binding["cap"]["unit"], row)
            context = supplied["context"]
            self.known("study_binding.history", context["previous_outputs_supplied"], binding["controls"]["history"]["actual"], row)
            for source, target in (("platform_context", "platform_context"), ("reasoning_configuration", "reasoning")):
                self.known("study_binding." + target, context[source], binding[target], row)
            auto = _known(context["automatic_retries"])
            if auto is not None:
                self.known("study_binding.automatic_retries", {"state": "known", "value": auto > 0}, binding["automatic_retries"], row)
            if _known(context["output_selection"]) == "none":
                self.known("study_binding.best_of", {"state": "known", "value": 1}, binding["controls"]["best_of"]["actual"], row)
            system = _known(context["visible_system_instruction_ref"])
            if system:
                _, snap = self.view.artifact(system["record_id"])
                if snap is None:
                    self.fail("study_binding.visible_system_instruction", "system_instruction_bytes_unavailable", row, missing=True)
                else:
                    self.known("study_binding.visible_system_instruction", {"state": "known", "value": snap.content.decode("utf-8")}, binding["visible_system_instruction"], row)
        # Free-text drift accounts and cap disclosures without an equivalent
        # legacy field are retained in the versioned operational sidecar input.

    def events(self):
        calls = {}
        for row in self.current:
            if row["record_type"] == "collection_ledger":
                calls[row["record_id"]] = self.call(row)
        for row in self.current:
            if row["record_type"] != "extraction":
                continue
            call = calls.get(row["collection_ref"]["record_id"])
            if call is None:
                continue
            samples = [s for s in self.samples.values() if _known(s["attempt_id"]) == call["attempt_id"]]
            retry = _known(self.view.records[row["collection_ref"]["record_id"]]["retry_of"])
            expected = {p["within_group_index"]: p for p in row["positions"]}
            seen = set()
            for sample in samples:
                n = _known(sample["within_group_index"])
                position = expected.get(n)
                if n in seen or position is None or position["selection"] != "selected" or _known(position["artifact_ref"]) is None:
                    self.fail("realization.within_group_index", "missing_or_duplicate_position_fabricated", row)
                    continue
                seen.add(n)
                self.artifact_match(position["artifact_ref"], sample["output_ref"], "realization.output_ref", row)
                self.artifact_match(row["raw_response_ref"], sample["raw_response_ref"], "realization.raw_response_ref", row)
                self.known("realization.generation_group_id", call["generation_group_id"], sample["generation_group_id"], row)
                self.known("realization.extraction_rule_version", {"state": "known", "value": row["rule_version"]}, sample["extraction_rule_version"], row)
                self.check("realization.completion_status", position["completion_status"], sample["completion_status"], row)
                if _ref(row) not in self.maps.get(_key(sample), ()):
                    self.fail("realization", "position_mapping_missing", row)
                selection = self.selections.get(sample["analysis_cell_id"], {})
                selected = _known(selection.get("selected_sample_ids"))
                order = _known(selection.get("sample_order"))
                if retry is not None:
                    if selected is None or sample["sample_id"] in selected:
                        self.fail("selection", "retry_cannot_replace_original_positions", row)
                elif selected is None or order is None or sample["sample_id"] not in selected or sample["sample_id"] not in order:
                    self.fail("selection", "original_selected_position_lost", row)
            if seen != {p["within_group_index"] for p in row["positions"] if p["selection"] == "selected" and _known(p["artifact_ref"])}:
                self.fail("realization", "original_selected_position_lost", row)
            order = _known(self.selections.get(call["analysis_cell_id"], {}).get("sample_order"))
            if order is not None and retry is None:
                observed = [s["sample_id"] for s in sorted(samples, key=lambda s: _known(s["within_group_index"]) or 0)]
                if [sid for sid in order if sid in observed] != observed:
                    self.fail("sample_order", "original_position_order_conflict", row)
        self.call_map = calls

    def qualifications(self):
        assessments = {r["artifact_id"]: r for r in self.assessment.artifacts}
        schema_changed = self.correction["schema_review_required"]
        for old in self.legacy.values():
            if old["record_type"] not in {"assignment", "validity"}:
                continue
            if old["record_id"] not in self.pins[old["record_type"]]:
                # Superseded decisions stay in the carrier's historical record
                # inventory; only explicitly pinned decisions can supply mass.
                continue
            sample = self.samples.get(old["sample_id"])
            output = _known(sample["output_ref"]) if sample else None
            artifacts = self.maps.get((output["record_type"], output["record_id"]), ()) if output else ()
            artifacts = [r for r in artifacts if r["record_type"] == "artifact"]
            if not artifacts:
                if schema_changed:
                    self.fail(old["record_type"], "schema_revision_requires_fresh_qualified_mapping")
                continue
            if len(artifacts) != 1:
                self.fail(old["record_type"], "ambiguous_original_artifact_mapping")
                continue
            aid = artifacts[0]["record_id"]
            result = assessments.get(aid)
            if result is None or aid in self.invalid:
                self.fail(old["record_type"], "qualified_subject_unavailable_or_stale", self.view.records[aid])
                continue
            if old["record_type"] == "assignment":
                self.check("assignment.assignment_status", result["assignment_status"], old["assignment_status"], self.view.records[aid])
                if old["assignment_status"] == "assigned":
                    self.check("assignment.structural_class_id", result["structural_class_id"], old["structural_class_id"], self.view.records[aid])
                judgment = result["judgment_id"]
                if judgment and not any(ref["record_id"] == judgment for ref in self.maps.get(_key(old), ())):
                    self.fail("assignment", "qualified_judgment_mapping_missing", self.view.records[aid])
            else:
                self.check("validity.validity_status", result["validity_status"], old["validity_status"], self.view.records[aid])
                if old["validity_status"] in {"valid", "invalid"} and not all(any(
                        ref["record_id"] == rid for ref in self.maps.get(_key(old), ())) for rid in result["validity_receipt_ids"]):
                    self.fail("validity", "qualified_validity_mapping_missing", self.view.records[aid])

    def run(self):
        chosen = self.select_carrier()
        if chosen is None:
            return self.result()
        carrier, snapshot = chosen
        staged, packet_map = self.carrier_files(snapshot)
        manifest_name = PurePosixPath(snapshot.path).name
        with TemporaryDirectory(prefix="structdet-study-bridge-") as temporary:
            root = Path(temporary)
            _stage(root, staged)
            path = root / manifest_name
            bundle = load_bundle(path, limits=self.limits)
            if bundle.has_errors or bundle.manifest is None or not bundle.acquisition_complete:
                for diagnostic in bundle.diagnostics:
                    if diagnostic.severity == "error":
                        self.fail("legacy_profile_input", diagnostic.code, carrier)
                if not self.errors:
                    self.fail("legacy_profile_input", "carrier_acquisition_incomplete", carrier)
                return self.result()
            validation, exit_code = validate_bundle(path, limits=self.limits)
            if exit_code:
                self.fail("legacy_profile_input", "legacy_validation_rejected", carrier)
                return self.result()
            self.identity(bundle)
            self.mappings(bundle)
            self.events()
            self.qualifications()
            files = {name: snap.content for name, snap in bundle.snapshots.items()}
            # Input hashes are identities, not existence-based fallback values.
            if any(name not in packet_map or files[name] != staged[name] for name in files):
                raise InputError("legacy_read_outside_declared_inventory")
            field_map = []
            for entry in bundle.records:
                record = entry.record
                if record is None:
                    continue
                declaration = entry.source.split("#", 1)[0]
                field_map.append({"target_record_type": record.record_type, "target_record_id": record.record_id,
                    "target_record_version": record.data["record_version"], "fields": sorted(record.data),
                    "source_packet_id": packet_map[declaration], "source_location": entry.line,
                    "source_declaration": entry.source.split("#", 1)[1] if "#" in entry.source else None,
                    "source_record_refs": self.maps.get(_key(record.data), ())})
            self.provenance = {"study_id": self.view.raw["study_id"], "study_version": self.view.raw["study_version"],
                "bundle_id": bundle.manifest.data["bundle_id"], "profile": self.profile,
                "compiler_method_id": "exact_legacy_carrier_v1",
                "compiler_software_sha256": _sha(Path(__file__).read_bytes()),
                "data_role": self.view.raw["material_role"], "evidence_policy": self.view.raw["evidence_policy"],
                "carrier_ref": _ref(carrier), "carrier_sha256": snapshot.sha256,
                "manifest_fields": sorted(bundle.manifest.data), "field_map": field_map,
                "input_snapshots": [{"packet_id": pid, "sha256": snap.sha256, "size_bytes": snap.size_bytes}
                    for pid in sorted(self.view.inventory) if (snap := self.view.snapshot(pid)) is not None],
                "study_snapshot_sha256": _sha(_serialize(self.view.raw)),
                "outputs": [{"path": name, "sha256": _sha(content), "size_bytes": len(content)} for name, content in sorted(files.items())],
                "operational_only_record_refs": [_ref(r) for r in self.current if r["record_id"] not in {
                    ref["record_id"] for refs in self.maps.values() for ref in refs}],
                "original_bytes_preserved": True, "scientific_parameters_preserved": True,
                "fixture_context": self.assessment.fixture_context,
                "claim_disposition": "restricted", "evidence_scope": "supplied_record_checks_only",
                "scope_restrictions": sorted(self.scope_restrictions),
                "authentication_required": True, "empirical_claim_established": False,
                "legacy_validation_exit_code": exit_code}
            return self.result(files, manifest_name)

    def result(self, files=None, bundle_path=None):
        if self.errors or any(d.severity == "error" for d in self.issues):
            files, bundle_path = {}, None
            if self.provenance:
                self.provenance.update(outputs=[], claim_disposition="withheld")
        out = Compilation(tuple(self.issues), tuple(freeze(self.errors)), freeze(self.provenance), freeze(self.correction),
            freeze(self.assessment.as_dict()), freeze(files or {}), bundle_path, self.limits)
        if len(_serialize(out.as_dict())) + sum(map(len, out.files.values())) > self.limits.max_bundle_bytes:
            raise InputError("compilation_output_budget_exceeded")
        return out


def compile_study(loaded: LoadedStudy, *, qualification_packet_id: str | None = None,
                  mapping_receipt_id: str | None = None, limits: ReadLimits | None = None) -> Compilation:
    """Check and retain an exact carrier, or return explicit mapping failures.

    No packet/receipt is auto-selected. Missing carrier fields withhold conversion
    as a well-formed readiness gap; contradictions are errors. A carrier's own
    accepted fixture/evidence records remain subject to the existing M/V/L gates.
    Every overlapping new operational observation must agree with its carrier.
    """
    compiler = None
    try:
        compiler = _Compiler(loaded, qualification_packet_id, mapping_receipt_id, limits)
        return compiler.run()
    except (InputError, KeyError, TypeError, ValueError, OSError, RecursionError, StopIteration) as exc:
        code = exc.code if isinstance(exc, InputError) else "invalid_compilation_context"
        return Compilation((Diagnostic(code, "study_bridge", "study_bridge"),),
            corrections=freeze(compiler.correction) if compiler else freeze({}),
            qualification=freeze(compiler.assessment.as_dict()) if compiler else freeze({}))


@dataclass(frozen=True)
class CompiledAnalysis(Analysis):
    compilation_receipt: Mapping[str, Any] = field(default_factory=dict)


def analyze_compilation(compilation: Compilation, *, run_id=None, recorded_at=None,
                        replay_manifest_bytes: bytes | None = None):
    """Delegate unchanged to the established analysis/replay engine.

    Reanalysis always computes the entire registered carrier, including every
    affected condition and endpoint. No selective favorable correction exists.
    Replay failures propagate; they never trigger a fresh stochastic run.
    """
    if not isinstance(compilation, Compilation) or not compilation.compiled:
        raise InputError("compilation_withheld")
    expected = {r["path"]: (r["sha256"], r["size_bytes"]) for r in compilation.provenance["outputs"]}
    actual = {name: (_sha(content), len(content)) for name, content in compilation.files.items()}
    if actual != expected:
        raise InputError("compiled_snapshot_identity_mismatch")
    if replay_manifest_bytes is not None and (not isinstance(replay_manifest_bytes, bytes)
            or len(replay_manifest_bytes) > compilation.limits.max_file_bytes):
        raise InputError("invalid_replay_snapshot")
    with TemporaryDirectory(prefix="structdet-compiled-analysis-") as temporary:
        root = Path(temporary)
        source = root / "source"
        source.mkdir()
        _stage(source, compilation.files)
        replay_path = None
        if replay_manifest_bytes is not None:
            replay_path = root / "replay.json"
            replay_path.write_bytes(replay_manifest_bytes)
        analysis = analyze_bundle(source / compilation.bundle_path, limits=compilation.limits,
            run_id=run_id, recorded_at=recorded_at, replay_manifest_path=replay_path)
        performed = analysis.exit_code == 0
        affected = compilation.corrections["registered_comparisons_to_recompute"]
        recomputed = list(affected) if performed and compilation.provenance["profile"] == "hero_sort_abc_v1" else []
        receipt = {"study_id": compilation.provenance["study_id"], "study_version": compilation.provenance["study_version"],
            "profile": compilation.provenance["profile"], "carrier_sha256": compilation.provenance["carrier_sha256"],
            "engine_exit_code": analysis.exit_code, "analysis_performed": performed,
            "reanalysis_performed": performed and bool(compilation.corrections["supersessions"] or compilation.corrections["incidents"]),
            "recomputed_registered_comparisons": recomputed,
            "pending_registered_comparisons": [name for name in affected if name not in recomputed],
            "report_sha256": _sha(analysis.report_json), "run_manifest_sha256": _sha(analysis.manifest_json),
            "replay_requested": replay_manifest_bytes is not None, "prior_outputs_preserved": True,
            "empirical_claim_established": False, "substantive_validation_performed": False}
        return CompiledAnalysis(**vars(analysis), compilation_receipt=freeze(receipt))
