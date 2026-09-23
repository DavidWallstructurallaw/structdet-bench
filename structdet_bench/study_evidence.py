"""Evidence-linked admission and fixed human-audit selection for passive studies.

Only supplied records are checked. No human, provenance claim, program, or
scientific conclusion is authenticated by this module.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from typing import Any, Mapping

from .contracts import CLASS_IDS, Diagnostic, InputError, freeze
from .evidence import MECHANISM_METHODS
from .local_io import ReadLimits
from .study_collection import _control_signature, collection_plan, inspect_collection
from .study_records import (FAMILY_SCHEMAS, LoadedStudy, RECORD_TYPES, _limits,
                            _physical, _preflight, _references, _serialize, _validate)
from .study_review import _StudyView, inspect_reviews
from .study_validation import inspect_validation_receipt

CONDITIONS = ("structural_validity", "external_presence", "source_integrity",
              "tail_retention", "corrective_capacity")
COMPONENTS = ("stable_core", "rotating_frontier", "external_incident", "tail_registry")
REQUIREMENTS = (*CONDITIONS, "schema_validation", "independent_validation",
                "protocol_compliance", "exposure_controls")
DIMENSIONS = ("reference_construction", "initial_judgment", "model_ancestry",
              "validation_method", "selection_and_revision")
_K = lambda value: {"knowledge": value}
_E = lambda *values: {"enum": list(values)}
_R = lambda *values: {"reference": list(values)}
_A = lambda value: {"array": value}
_REF = _R(*sorted(RECORD_TYPES))
_ART = _R("artifact")
_JUDGE = _R("human_review", "adjudication")
_PERIOD = {"object": {"start": "timestamp", "end": "timestamp"}}
_ASSESSMENT = {"outcome": _E("satisfied_for_scope", "unsatisfied", "unresolved", "not_applicable"),
               "basis": _K("text"), "assessor_ref": _K(_JUDGE), "evidence_ids": _A("id")}

# This attachment supplements the fixed study envelope. It cannot change its
# scientific pins, artifact bytes, original judgments, or registered positions.
QUALIFICATION_SCHEMA = {"object": {
    "kind": {"literal": "evidence_qualification"}, "version": {"literal": "0.1"},
    "packet_id": "id", "study_id": "id", "study_version": "id", "fixture": "bool",
    "pins": FAMILY_SCHEMAS["study_registration"]["object"]["pins"],
    "evidence": _A({"object": {
        "evidence_id": "id", "target_ref": _REF, "subject_sha256": "hash",
        "source_ref": _ART, "reviewer_ref": _K(_JUDGE),
        "purpose": _E("mechanism", "schema", "independence", "audit", "external_presence",
                      "tail_retention", "correction", "protocol", "exposure"),
        "method": _E(*sorted(MECHANISM_METHODS), "human_inspection", "documentary",
                     "output_only", "self_description", "fixture_declaration"),
        "state": _E("active", "challenged", "withdrawn", "superseded", "unresolved"),
        "basis": _K("text"), "reachable_branches": _K("text"),
        "constitutive_relations": _K("text"), "structural_class_id": _K("class_id"),
        "validation_ref": _K(_R("validation_receipt")),
        "supported_claim_ids": _A("id"), "system_id": _K("id"), "period": _K(_PERIOD)}}),
    "qualifications": _A({"object": {
        "artifact_ref": _ART, "judgment_ref": _K(_JUDGE),
        "essential_evidence_ids": _A("id"), "validation_refs": _A(_R("validation_receipt")),
        "independence_ids": _A("id")}}),
    "independence": _A({"object": {
        "assessment_id": "id", "left_ref": _REF, "right_ref": _REF,
        "dimension": _E(*DIMENSIONS), "outcome": _E("supported_for_scope", "not_supported_for_scope", "unresolved"),
        "basis": _K("text"), "assessor_ref": _K(_JUDGE),
        "evidence_ids": _A("id"), "limitations": _A("text")}}),
    "audit_flags": _A({"object": {
        "artifact_ref": _ART, "relied_on_in_reporting": "bool",
        "reasons": _A(_E("classification_dispute", "novel_candidate", "hybrid_boundary", "challenged_essential"))}}),
    "claims": _A({"object": {
        "claim_id": "id", "kind": _E("label_conditioned", "validated_measurement", "empirical_theory", "operational_openness"),
        "statement": "text", "artifact_refs": _A(_ART), "system_id": _K("id"), "period": _K(_PERIOD),
        "requirements": _A({"object": {"requirement_id": _E(*REQUIREMENTS), **_ASSESSMENT}}),
        "components": _A({"object": {
            "component_id": _E(*COMPONENTS), "version": _K("id"),
            "contents_state": _E("supplied", "known_empty", "unknown", "unavailable"),
            "artifact_refs": _A(_ART)}})}})}}


def _known(value):
    return value.get("value") if isinstance(value, Mapping) and value.get("state") == "known" else None


def _diag(code, severity="error"):
    return Diagnostic(code, "study_evidence", "study_evidence", severity=severity)


def _unique(values):
    return tuple(sorted(set(values)))


def _time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class QualificationPacket:
    data: Any = field(default=None, repr=False)
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def has_errors(self):
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0


def parse_evidence_qualification_bytes(data: bytes, limits: ReadLimits | None = None) -> QualificationPacket:
    """Strict shape/identity checks. A complete form is still supplied evidence."""
    issues, raw = [], None
    try:
        limits = _limits(limits)
        raw = _physical(data, limits)
        _preflight(raw, limits)
        _validate(raw, QUALIFICATION_SCHEMA, "packet", issues)
        if not issues:
            count = 0
            for family, key in (("evidence", "evidence_id"), ("qualifications", "artifact_ref"),
                                ("independence", "assessment_id"), ("audit_flags", "artifact_ref"), ("claims", "claim_id")):
                rows = raw[family]
                count += len(rows)
                ids = [_serialize(row[key]) for row in rows]
                if len(ids) != len(set(ids)):
                    raise InputError("duplicate_qualification_identity")
            for claim in raw["claims"]:
                for family, key in (("requirements", "requirement_id"), ("components", "component_id")):
                    count += len(claim[family])
                    ids = [r[key] for r in claim[family]]
                    if len(ids) != len(set(ids)):
                        raise InputError("duplicate_claim_requirement_or_component")
            for row in (*raw["claims"], *raw["evidence"]):
                period = _known(row["period"])
                if period and _time(period["end"]) <= _time(period["start"]):
                    raise InputError("qualification_period_reversed_or_empty")
            if count > limits.max_records:
                raise InputError("record_count_exceeded")
            _physical(_serialize(raw), limits)
    except (InputError, TypeError, ValueError, RecursionError) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_qualification_packet"))
    return QualificationPacket(freeze(raw) if not issues else None, tuple(issues))


def fixed_audit_positions() -> tuple[Mapping[str, Any], ...]:
    """HERO 6.2: all 72 main positions, before seeing any observations."""
    return tuple(freeze({"block_id": call["block_id"], "condition": call["condition"],
        "group_index": call["group_index"], "within_group_index":
        1 + ((int(call["block_id"][1:]) + "ABC".index(call["condition"]) + 1 + call["group_index"] - 3) % 5)})
        for call in collection_plan()["calls"])


@dataclass(frozen=True)
class EvidenceAssessment:
    diagnostics: tuple[Diagnostic, ...] = ()
    artifacts: tuple[Mapping[str, Any], ...] = ()
    audit: Mapping[str, Any] = field(default_factory=dict)
    cells: tuple[Mapping[str, Any], ...] = ()
    comparisons: tuple[Mapping[str, Any], ...] = ()
    claims: tuple[Mapping[str, Any], ...] = ()
    core: Mapping[str, Any] = field(default_factory=dict)
    independence: tuple[Mapping[str, Any], ...] = ()
    review_queue: tuple[Mapping[str, Any], ...] = ()
    fixture_context: bool = False
    evidence_scope: str = "supplied_record_checks_only"
    substantive_validation_performed: bool = False

    @property
    def has_errors(self):
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0

    def as_dict(self):
        # No record prose, real person keys, private paths or original bytes are
        # exposed. Stable artifact/review/claim IDs are intentional join keys.
        out = {key: getattr(self, key) for key in (
            "artifacts", "audit", "cells", "comparisons", "claims", "core", "independence",
            "review_queue", "fixture_context", "evidence_scope", "substantive_validation_performed")}
        out["diagnostics"] = [{"code": d.code, "severity": d.severity} for d in self.diagnostics]
        out["exit_code"] = self.exit_code
        return json.loads(_serialize(out))


def _position(row):
    return (row["block_id"], row["condition"], row["group_index"], row["within_group_index"])


class _Qualification:
    def __init__(self, loaded, packet_id, limits):
        self.view = _StudyView(loaded)
        self.limits = _limits(limits)
        if (sum(len(s.content) for s in loaded.snapshots.values()) != loaded.total_read_bytes
                or loaded.total_read_bytes > min(self.limits.max_bundle_bytes, self.view.raw["import_budget"]["max_total_bytes"])
                or any(len(s.content) > self.limits.max_file_bytes for s in loaded.snapshots.values())):
            raise InputError("evidence_snapshot_budget_or_inventory_mismatch")
        self.issues = []
        self.registration = next(r for r in self.view.current if r["record_type"] == "study_registration")
        self.collection = inspect_collection(loaded)
        self.review = inspect_reviews(loaded)
        self.issues.extend(self.collection.diagnostics)
        self.issues.extend(self.review.diagnostics)
        self.review_index = {r["review_id"]: r for r in self.review.reviews}
        self.fixture = (self.view.fixture or self.review.qualification_status == "fixture_only"
                        or self.collection.qualification_status == "fixture_only")
        self.raw = {key: () for key in ("evidence", "qualifications", "independence", "audit_flags", "claims")}
        self.validation_cache = {}
        self.evidence_cache = {}
        self.superseded = {_known(r["supersedes"])["record_id"] for r in self.view.current if _known(r["supersedes"])}
        if packet_id is not None:
            entry = self.view.inventory.get(packet_id)
            snap = self.view.snapshot(packet_id)
            if entry is None:
                raise InputError("qualification_packet_not_in_inventory")
            if entry["purpose"] != "evidence" or entry["format"] != "json":
                raise InputError("qualification_packet_kind_mismatch")
            if snap is None:
                self.issues.append(_diag("qualification_packet_unavailable", "warning"))
            else:
                parsed = parse_evidence_qualification_bytes(snap.content, self.limits)
                if parsed.has_errors:
                    raise InputError("qualification_packet_rejected")
                raw = parsed.data
                if (raw["packet_id"] != packet_id or any(raw[k] != self.view.raw[k] for k in ("study_id", "study_version"))
                        or raw["pins"] != self.registration["pins"]):
                    raise InputError("qualification_scope_or_pins_mismatch")
                logical = len(self.view.raw["records"]) + sum(a.checked_record_count or 0 for a in loaded.attachments)
                logical += sum(len(raw[key]) for key in self.raw) + sum(
                    len(c["requirements"]) + len(c["components"]) for c in raw["claims"])
                if logical > min(self.limits.max_records, self.view.raw["import_budget"]["max_total_records"]):
                    raise InputError("budget_exceeded_partition_required")
                self.raw = raw
                self.fixture |= raw["fixture"]
                for _, reference in _references(raw, "packet"):
                    target = self.view.records.get(reference["record_id"])
                    if (target is None or target["record_type"] != reference["record_type"]
                            or target["record_version"] != reference["record_version"]
                            or target["study_version"] != self.view.raw["study_version"]
                            or target["scope"] != self.registration["scope"]):
                        raise InputError("qualification_reference_scope_mismatch")
        self.evidence = {r["evidence_id"]: r for r in self.raw["evidence"]}
        self.qualifications = {r["artifact_ref"]["record_id"]: r for r in self.raw["qualifications"]}
        self.independence = {r["assessment_id"]: r for r in self.raw["independence"]}

    def resolve(self, ref):
        if ref is None:
            return None
        row = self.view.records.get(ref["record_id"])
        if (row is None or row["record_type"] != ref["record_type"] or row["record_version"] != ref["record_version"]
                or row["study_version"] != self.view.raw["study_version"] or row["scope"] != self.registration["scope"]
                or row["record_id"] in self.superseded):
            return None
        return row

    def decision_problems(self, row, independent=False):
        if row is None or row["record_type"] not in {"human_review", "adjudication"}:
            return ("judgment_unavailable",)
        detail = self.review_index.get(row["record_id"])
        if detail is None:
            return ("judgment_uninspected",)
        # Initial independence and shared ancestry constrain scientific claims.
        # Preserved substantive decisions have a separate admission boundary.
        essential = ("original_submission", "reviewed_artifact", "judgment_basis", "reviewer_identity",
                     "reviewer_roster", "reviewer_not_human", "reviewer_qualification",
                     "reviewer_disclosure", "expert_qualification", "expert_basis", "adjudication_unresolved")
        reasons = [r for r in detail["restrictions"] if independent or r.startswith(essential)]
        if row["record_type"] == "human_review" and row["submission_stage"] == "draft":
            reasons.append("provisional_judgment")
        if row["record_id"] in self.superseded:
            reasons.append("judgment_superseded")
        return _unique(reasons)

    def person(self, row):
        who = row["adjudicator" if row["record_type"] == "adjudication" else "reviewer"]
        snap = self.view.snapshot(_known(who["roster_packet_id"]))
        if snap is None:
            return None
        raw = _physical(snap.content, self.limits)
        return next((_known(r["person_key"]) for r in raw.get("reviewers", ()) if r["reviewer_id"] == who["reviewer_id"]), None)

    def validation(self, ref):
        row = self.resolve(ref)
        if row is None or row["record_type"] != "validation_receipt":
            return None
        key = row["record_id"]
        if key not in self.validation_cache:
            result = inspect_validation_receipt(self.view.loaded, key, self.limits)
            self.issues.extend(result.diagnostics)
            self.validation_cache[key] = result
        return self.validation_cache[key]

    def evidence_problems(self, identifier, *, target=None, purpose=None, independent=False):
        key = (identifier, target, purpose, independent)
        if key in self.evidence_cache:
            return self.evidence_cache[key]
        row = self.evidence.get(identifier)
        if row is None:
            return ("essential_evidence_missing",)
        reasons = []
        subject = self.resolve(row["target_ref"])
        source = self.resolve(row["source_ref"])
        if subject is None or target is not None and subject["record_id"] != target:
            reasons.append("evidence_target_unresolved_or_mismatched")
        elif subject["record_type"] == "artifact":
            _, snap = self.view.artifact(subject["record_id"])
            if snap is None or row["subject_sha256"] != snap.sha256:
                reasons.append("essential_subject_bytes_unavailable_or_mismatched")
        elif row["subject_sha256"] != hashlib.sha256(_serialize(subject)).hexdigest():
            reasons.append("essential_subject_record_mismatched")
        _, source_snap = self.view.artifact(source["record_id"]) if source else (None, None)
        if source_snap is None or source["artifact_role"] not in {"evidence", "source", "review"}:
            reasons.append("essential_evidence_bytes_unavailable")
        if row["state"] != "active":
            reasons.append("essential_evidence_not_active")
        if _known(row["basis"]) is None:
            reasons.append("essential_evidence_basis_missing")
        if purpose and row["purpose"] != purpose:
            reasons.append("evidence_purpose_mismatch")
        reviewer = self.resolve(_known(row["reviewer_ref"]))
        reasons.extend(self.decision_problems(reviewer, independent))
        if reviewer and row["source_ref"] not in reviewer["judgment"]["evidence_refs"]:
            reasons.append("evidence_not_linked_by_reviewer")
        if purpose == "mechanism":
            if row["method"] not in MECHANISM_METHODS:
                reasons.append("method_does_not_establish_mechanism")
            if any(_known(row[f]) is None for f in ("reachable_branches", "constitutive_relations")):
                reasons.append("essential_mechanism_scope_missing")
            if reviewer and (reviewer["artifact_ref"] != row["target_ref"] or reviewer["artifact_sha256"] != row["subject_sha256"]):
                reasons.append("mechanism_review_subject_mismatch")
            if (_known(row["structural_class_id"]) is None or reviewer and
                    _known(row["structural_class_id"]) != _known(reviewer["judgment"]["structural_class_id"])):
                reasons.append("mechanism_class_association_mismatch")
            if row["method"] == "execution_trace":
                receipt = self.resolve(_known(row["validation_ref"]))
                checked = self.validation(_known(row["validation_ref"]))
                packet = _known(source["content"]) if source else None
                if (receipt is None or checked is None or checked.has_errors or checked.observed_count == 0
                        or receipt["artifact_ref"] != row["target_ref"] or packet is None
                        or not any(_known(m["evidence_packet_id"]) == packet["packet_id"] for m in receipt["mechanism_observations"])
                        or any(d.code == "validation_environment_or_oracle_unresolved" for d in checked.diagnostics)):
                    reasons.append("execution_trace_receipt_unestablished")
        if independent and source and any(_known(source[f]) is None for f in ("original_source", "ai_assistance", "exposure")):
            reasons.append("evidence_origin_or_exposure_unknown")
        result = _unique(reasons)
        self.evidence_cache[key] = result
        return result

    def independence_result(self, row):
        reasons = []
        left, right = self.resolve(row["left_ref"]), self.resolve(row["right_ref"])
        if left is None or right is None or left["record_id"] == right["record_id"]:
            reasons.append("independence_endpoints_unresolved_or_same")
        if row["outcome"] != "supported_for_scope" or _known(row["basis"]) is None or row["limitations"]:
            reasons.append("independence_not_established")
        reasons.extend(self.decision_problems(self.resolve(_known(row["assessor_ref"])), True))
        if not row["evidence_ids"]:
            reasons.append("independence_evidence_missing")
        for identifier in row["evidence_ids"]:
            reasons.extend(self.evidence_problems(identifier, purpose="independence", independent=True))
            evidence = self.evidence.get(identifier)
            if evidence and evidence["target_ref"] not in (row["left_ref"], row["right_ref"]):
                reasons.append("independence_evidence_scope_mismatch")
        if left and right and left["record_type"] in {"human_review", "adjudication"} and right["record_type"] in {"human_review", "adjudication"}:
            if self.person(left) is None or self.person(left) == self.person(right):
                reasons.append("independence_persons_unresolved_or_same")
        return {"assessment_id": row["assessment_id"], "dimension": row["dimension"],
                "declared_outcome": row["outcome"], "record_consistent": not reasons,
                "restrictions": _unique(reasons), "authentication_required": True}

    def qualify(self, artifact, independence):
        aid = artifact["record_id"]
        row = self.qualifications.get(aid)
        _, snap = self.view.artifact(aid)
        member, validity, restrictions = [], [], []
        if snap is None:
            member.append("artifact_bytes_unavailable")
        if artifact["record_id"] in self.superseded:
            member.append("artifact_superseded")
        frame = self.registration["frame_definition"]
        if any(_known(value) is None for key, value in frame.items() if key != "load_bearing_invariants") or not frame["load_bearing_invariants"]:
            member.append("essential_frame_unresolved")
        if any(r["artifact_ref"]["record_id"] == aid and "challenged_essential" in r["reasons"] for r in self.raw["audit_flags"]):
            member.append("essential_evidence_challenge_unresolved")
        for name in ("original_source", "ai_assistance", "exposure"):
            if _known(artifact[name]) is None:
                restrictions.append("artifact_" + name + "_unavailable")
        decision = self.resolve(_known(row["judgment_ref"])) if row else None
        member.extend(self.decision_problems(decision))
        if decision and (decision["artifact_ref"]["record_id"] != aid or snap is not None and decision["artifact_sha256"] != snap.sha256):
            member.append("judgment_subject_mismatch")
            decision = None
        if self.view.raw["evidence_policy"] == "adjudicated_import":
            if self.fixture:
                member.append("fixture_cannot_enter_adjudicated_import")
                validity.append("fixture_cannot_enter_adjudicated_import")
            if decision and decision["record_type"] != "adjudication":
                member.append("adjudication_record_required")
        essential = row["essential_evidence_ids"] if row else ()
        if not essential:
            member.append("essential_membership_evidence_missing")
        for identifier in essential:
            member.extend(self.evidence_problems(identifier, target=aid, purpose="mechanism"))
            evidence = self.evidence.get(identifier)
            if decision and evidence and evidence["source_ref"] not in decision["judgment"]["evidence_refs"]:
                member.append("decision_essential_evidence_unlinked")
            if decision and evidence and _known(evidence["structural_class_id"]) != _known(decision["judgment"]["structural_class_id"]):
                member.append("decision_mechanism_class_mismatch")
        status = decision["judgment"]["assignment_status"] if decision else "unclassified"
        class_id = _known(decision["judgment"]["structural_class_id"]) if decision else None
        assigned = status == "assigned" and not member
        values, receipt_ids = set(), []
        for ref in row["validation_refs"] if row else ():
            receipt = self.resolve(ref)
            if receipt is None or receipt["artifact_ref"]["record_id"] != aid:
                validity.append("validity_receipt_scope_mismatch")
                continue
            checked = self.validation(ref)
            receipt_ids.append(receipt["record_id"])
            if checked.has_errors:
                validity.append("validity_receipt_rejected")
            if self.view.raw["evidence_policy"] == "adjudicated_import" and receipt["provenance"]["authenticity"] == "stipulated_fixture":
                validity.append("fixture_cannot_enter_adjudicated_import")
            if not checked.has_errors and checked.validity_status in {"valid", "invalid"}:
                values.add(checked.validity_status)
        if len(values) > 1:
            validity.append("contradictory_validity_receipts")
        if not receipt_ids:
            validity.append("validity_receipt_missing")
        valid_state = next(iter(values)) if len(values) == 1 and not validity else "undetermined"
        if not receipt_ids and (decision is None or decision["judgment"]["validity_status"] == "not_assessed"):
            valid_state = "not_assessed"
        if decision and decision["judgment"]["validity_status"] in {"valid", "invalid"} and valid_state != decision["judgment"]["validity_status"]:
            validity.append("declared_validity_not_established")
            valid_state = "undetermined"
        if self.view.raw["evidence_policy"] == "adjudicated_import" and (decision is None or decision["record_type"] != "adjudication"):
            validity.append("adjudication_record_required")
            if valid_state in {"valid", "invalid"}:
                valid_state = "undetermined"
        elif self.view.raw["evidence_policy"] == "adjudicated_import" and decision and (
                self.decision_problems(decision) or decision["judgment"]["validity_status"] != valid_state):
            validity.append("validity_adjudication_unestablished")
            if valid_state in {"valid", "invalid"}:
                valid_state = "undetermined"
        ids = row["independence_ids"] if row else ()
        if not ids:
            restrictions.append("independence_not_established")
        for identifier in ids:
            independent = self.independence.get(identifier)
            if (identifier not in independence or not independence[identifier]["record_consistent"]
                    or independent is None or not any(r["record_id"] == aid for r in (independent["left_ref"], independent["right_ref"]))):
                restrictions.append("independence_not_established_for_artifact")
        if decision:
            restrictions.extend(self.decision_problems(decision, True))
        return {"artifact_id": aid, "artifact_role": artifact["artifact_role"], "bytes_available": snap is not None,
                "judgment_id": decision["record_id"] if decision else None, "declared_assignment_status": status,
                "assignment_status": "assigned" if assigned else "unresolved" if status in {"assigned", "unresolved"} else "unclassified",
                "membership_admitted": assigned, "structural_class_id": class_id if assigned else None,
                "membership_reasons": _unique(member), "validity_status": valid_state,
                "validity_receipt_ids": _unique(receipt_ids), "validity_reasons": _unique(validity),
                "independence_ids": _unique(ids), "claim_restrictions": _unique(restrictions),
                "fixture_context": self.fixture, "empirical_validation_established": False}

    def positions(self):
        extractions = defaultdict(list)
        for row in self.view.current:
            if row["record_type"] == "extraction" and row["record_id"] not in self.superseded:
                extractions[row["collection_ref"]["record_id"]].append(row)
        result, used = [], defaultdict(list)
        slots = {(s["block_id"], s["condition"], s["group_index"]): s for s in self.collection.slots}
        for call in collection_plan()["calls"]:
            slot = slots.get((call["block_id"], call["condition"], call["group_index"]))
            inspected = slot is not None
            if slot is None:
                slot = {**call, "primary_record_id": None, "extraction": None, "restrictions": ()}
            declarations = extractions.get(slot["primary_record_id"], ())
            for n in range(1, 6):
                pos = {key: slot[key] for key in ("block_id", "condition", "group_index")}
                pos["within_group_index"] = n
                actual = slot["extraction"]["positions"][n - 1] if slot["extraction"] else None
                aid, opportunity = None, "missing" if inspected else "unavailable"
                if actual and actual["selection"] == "selected":
                    opportunity = "unavailable"
                    if len(declarations) == 1 and "supplied_extraction_inconsistent" not in slot["restrictions"]:
                        ref = _known(declarations[0]["positions"][n - 1]["artifact_ref"])
                        artifact = self.resolve(ref)
                        if artifact and self.view.artifact(artifact["record_id"])[1] is not None:
                            aid, opportunity = artifact["record_id"], "present"
                elif actual and actual["selection"] == "withheld":
                    opportunity = "withheld"
                row = {"position": pos, "artifact_id": aid, "opportunity": opportunity,
                       "emitted": bool(actual and actual["selection"] == "selected")}
                result.append(row)
                if aid:
                    used[aid].append(row)
        for duplicates in used.values():
            if len(duplicates) > 1:
                self.issues.append(_diag("main_artifact_identity_reused"))
                for row in duplicates:
                    row.update(artifact_id=None, opportunity="withheld")
        return result

    def audit(self, positions, artifacts):
        fixed = {_position(p) for p in fixed_audit_positions()}
        reasons = defaultdict(set)
        pos_by_artifact = {p["artifact_id"]: p for p in positions if p["artifact_id"]}
        fixed_rows = []
        for row in positions:
            if _position(row["position"]) in fixed:
                fixed_rows.append(row)
                if row["artifact_id"]:
                    reasons[row["artifact_id"]].add("systematic")
        cell_classes, condition_classes = defaultdict(list), defaultdict(list)
        for aid, pos in pos_by_artifact.items():
            item = artifacts[aid]
            if item["membership_admitted"]:
                p, cid = pos["position"], item["structural_class_id"]
                cell_classes[(p["block_id"], p["condition"], cid)].append(aid)
                condition_classes[(p["condition"], cid)].append(aid)
            q = self.qualifications.get(aid)
            if q and any(self.evidence.get(e, {}).get("state") == "challenged" for e in q["essential_evidence_ids"]):
                reasons[aid].add("challenged_essential")
            judgments = [r for r in self.view.current if r["record_type"] == "human_review" and r["artifact_ref"]["record_id"] == aid and r["submission_stage"] == "initial"]
            categories = {(r["judgment"]["assignment_status"], _known(r["judgment"]["structural_class_id"])) for r in judgments}
            if len(categories) > 1 and not item["membership_admitted"]:
                reasons[aid].add("classification_dispute")
        for row in self.raw["audit_flags"]:
            aid = row["artifact_ref"]["record_id"]
            if aid in pos_by_artifact:
                for reason in row["reasons"]:
                    if reason in {"classification_dispute", "challenged_essential"} or row["relied_on_in_reporting"]:
                        reasons[aid].add(reason)
        for occurrences in cell_classes.values():
            if 1 <= len(occurrences) <= 2:
                for aid in occurrences:
                    reasons[aid].add("rare_class")
        # Reuse an already selected occurrence if possible, then use original
        # registered call/position order. This convention requires no resampling.
        coverage = []
        for condition in "ABC":
            for cid in sorted(CLASS_IDS):
                candidates = condition_classes.get((condition, cid), [])
                chosen = next((aid for aid in candidates if aid in reasons), candidates[0] if candidates else None)
                if chosen:
                    reasons[chosen].add("class_condition_coverage")
                coverage.append({"condition": condition, "class_id": cid, "observed_accepted_count": len(candidates),
                                 "selected_artifact_id": chosen, "state": "selected" if chosen else "not_observed"})
        records = defaultdict(list)
        for row in self.view.current:
            if row["record_type"] == "audit_selection" and row["record_id"] not in self.superseded:
                if row["position"]["block_id"] == "P00":
                    continue
                if "systematic" in row["reasons"] and _position(row["position"]) not in fixed:
                    self.issues.append(_diag("audit_systematic_position_mismatch"))
                ref = _known(row["artifact_ref"])
                aid = ref["record_id"] if ref else None
                if aid in pos_by_artifact and _position(row["position"]) == _position(pos_by_artifact[aid]["position"]):
                    records[aid].append(row)
                elif row["opportunity"] == "present":
                    self.issues.append(_diag("audit_position_not_original_observation"))
        targets = []
        for aid in pos_by_artifact:
            if aid not in reasons:
                continue
            reviews = {ref["record_id"]: ref for row in records[aid] for ref in row["review_refs"]}
            okay, limitations = [], []
            judge_id = artifacts[aid]["judgment_id"]
            judge = self.view.records.get(judge_id)
            origin_reviews = [judge] if judge else []
            if judge and judge["record_type"] == "adjudication":
                origin_reviews.extend(self.resolve(r) for r in judge["initial_review_refs"])
            origin_people = {self.person(r) for r in origin_reviews if r}
            for rid, ref in reviews.items():
                review = self.resolve(ref)
                problem = list(self.decision_problems(review, True))
                if review is not None:
                    if review["artifact_ref"]["record_id"] != aid or review["submission_stage"] != "initial":
                        problem.append("audit_review_scope_or_stage_mismatch")
                    if self.person(review) is None or self.person(review) in origin_people:
                        problem.append("audit_not_independent_of_initial_judgment")
                    if judge and review["judgment"] != judge["judgment"]:
                        left, right = review["judgment"], judge["judgment"]
                        if (left["assignment_status"], _known(left["structural_class_id"]), left["validity_status"]) != (
                                right["assignment_status"], _known(right["structural_class_id"]), right["validity_status"]):
                            problem.append("audit_judgment_dispute_unresolved")
                if not problem:
                    okay.append(rid)
                limitations.extend(problem)
            if not reviews:
                limitations.append("mandatory_audit_review_missing")
            targets.append({"artifact_id": aid, "position": pos_by_artifact[aid]["position"],
                "reasons": _unique(reasons[aid]), "review_ids": _unique(reviews), "record_consistent_review_ids": _unique(okay),
                "review_record_complete": bool(okay) and "audit_judgment_dispute_unresolved" not in limitations,
                "restrictions": _unique(limitations), "authentication_required": True})
        target_index = {r["artifact_id"]: r for r in targets}
        return {"formula_id": "hero_systematic_positions_v1", "phase": "main", "pilot_records_excluded": True,
            "planned_systematic_count": 72,
            "fixed_positions": tuple({**r, "review_record_complete": bool(r["artifact_id"] and target_index[r["artifact_id"]]["review_record_complete"])} for r in fixed_rows),
            "missing_fixed_opportunities": sum(r["opportunity"] == "missing" for r in fixed_rows),
            "unavailable_or_withheld_fixed_opportunities": sum(r["opportunity"] in {"unavailable", "withheld"} for r in fixed_rows),
            "targets": tuple(targets), "distinct_target_count": len(targets), "maximum_main_artifacts": 360,
            "class_condition_coverage": tuple(coverage), "additional_generator_observations": 0,
            "population_error_estimate": None, "substantive_audit_performed": False}

    def retain_audit_challenges(self, positions, artifacts):
        """An evidence-linked contrary audit cannot leave a label silently accepted.

        This checks current direct associations only. Versioned downstream
        correction, recut compilation and re-analysis belong to the bridge.
        """
        by_artifact = {p["artifact_id"]: p for p in positions if p["artifact_id"]}
        for row in self.view.current:
            if row["record_type"] != "audit_selection" or row["record_id"] in self.superseded:
                continue
            ref = _known(row["artifact_ref"])
            aid = ref["record_id"] if ref else None
            if aid not in by_artifact or _position(row["position"]) != _position(by_artifact[aid]["position"]):
                continue
            item = artifacts[aid]
            judge = self.view.records.get(item["judgment_id"])
            if judge is None:
                continue
            for reference in row["review_refs"]:
                review = self.resolve(reference)
                if self.decision_problems(review, True) or review["artifact_ref"]["record_id"] != aid:
                    continue
                if self.person(review) is None or self.person(review) == self.person(judge):
                    continue
                if judge["record_type"] == "adjudication" and reference in judge["initial_review_refs"]:
                    continue
                left, right = review["judgment"], judge["judgment"]
                if (left["assignment_status"], _known(left["structural_class_id"])) != (right["assignment_status"], _known(right["structural_class_id"])):
                    item.update(membership_admitted=False, structural_class_id=None, assignment_status="unresolved",
                        membership_reasons=_unique((*item["membership_reasons"], "audit_membership_dispute_unresolved")))
                if left["validity_status"] != right["validity_status"]:
                    item.update(validity_status="undetermined", validity_reasons=_unique((*item["validity_reasons"], "audit_validity_dispute_unresolved")))

    def requirement(self, row, claim):
        reasons = []
        if row is None:
            return {"outcome": "unresolved", "record_satisfied": False, "restrictions": ("mandatory_requirement_missing",)}
        if row["outcome"] != "satisfied_for_scope":
            reasons.append("mandatory_requirement_not_satisfied")
        if _known(row["basis"]) is None or not row["evidence_ids"]:
            reasons.append("requirement_evidence_or_basis_missing")
        reasons.extend(self.decision_problems(self.resolve(_known(row["assessor_ref"])), True))
        purpose = {"structural_validity": "schema", "external_presence": "external_presence", "source_integrity": "independence",
                   "tail_retention": "tail_retention", "corrective_capacity": "correction", "schema_validation": "schema",
                   "independent_validation": "independence", "protocol_compliance": "protocol", "exposure_controls": "exposure"}[row["requirement_id"]]
        for identifier in row["evidence_ids"]:
            reasons.extend(self.evidence_problems(identifier, purpose=purpose, independent=True))
            ev = self.evidence.get(identifier)
            if purpose == "independence" and not any(identifier in assessment["evidence_ids"]
                    and self.independence_result(assessment)["record_consistent"] for assessment in self.raw["independence"]):
                reasons.append("scoped_independence_assessment_missing")
            if ev and claim["claim_id"] not in ev["supported_claim_ids"]:
                reasons.append("requirement_claim_scope_mismatch")
            if ev and claim["kind"] == "operational_openness" and (
                    _known(ev["system_id"]) != _known(claim["system_id"]) or _known(ev["period"]) != _known(claim["period"])):
                reasons.append("requirement_system_or_period_mismatch")
            if ev and claim["kind"] == "operational_openness" and purpose in {"external_presence", "correction"}:
                event = self.resolve(ev["target_ref"])
                period = _known(claim["period"])
                if (event is None or event["record_type"] != "correction_incident"
                        or event["action_status"] != "performed" or _known(event["action"]) is None
                        or not event["affected_refs"] or ev["source_ref"] not in event["evidence_refs"]
                        or _known(event["reviewer_authority"]) is None):
                    reasons.append("performed_external_use_or_correction_unestablished")
                elif period is None or _known(event["performed_at"]) is None or not (
                        _time(period["start"]) <= _time(_known(event["performed_at"])) <= _time(period["end"])):
                    reasons.append("performed_event_outside_claim_period")
        return {"outcome": row["outcome"], "record_satisfied": not reasons, "restrictions": _unique(reasons)}

    def claims(self, artifacts, core, audit, comparisons):
        results = []
        for claim in self.raw["claims"]:
            required = ()
            if claim["kind"] in {"validated_measurement", "empirical_theory"}:
                required = ("schema_validation", "independent_validation")
            if claim["kind"] == "empirical_theory":
                required += ("protocol_compliance", "exposure_controls")
            if claim["kind"] == "operational_openness":
                required = CONDITIONS
            rows = {r["requirement_id"]: r for r in claim["requirements"]}
            requirements = {key: self.requirement(rows.get(key), claim) for key in required}
            restrictions = []
            ids = tuple(ref["record_id"] for ref in claim["artifact_refs"])
            if not ids:
                restrictions.append("claim_artifact_scope_missing")
            if any(aid not in artifacts or not artifacts[aid]["membership_admitted"] for aid in ids):
                restrictions.append("claim_membership_unqualified")
            if any(not r["record_satisfied"] for r in requirements.values()):
                restrictions.append("mandatory_claim_evidence_unestablished")
            if claim["kind"] in {"validated_measurement", "empirical_theory"}:
                if not core["record_complete"]:
                    restrictions.append("core_validation_incomplete")
                if any(artifacts.get(aid, {}).get("validity_status") not in {"valid", "invalid"} for aid in ids):
                    restrictions.append("claim_domain_validation_incomplete")
                if any(artifacts.get(aid, {}).get("claim_restrictions", ("missing",)) for aid in ids):
                    restrictions.append("sample_independence_or_provenance_unestablished")
                if any(not r["review_record_complete"] for r in audit["targets"] if r["artifact_id"] in ids):
                    restrictions.append("mandatory_audit_incomplete")
            if claim["kind"] == "empirical_theory" and any(not c["record_complete"] for c in comparisons):
                restrictions.append("registered_comparison_evidence_incomplete")
            components = {c["component_id"]: c for c in claim["components"]}
            if claim["kind"] == "operational_openness":
                if _known(claim["system_id"]) is None or _known(claim["period"]) is None:
                    restrictions.append("operational_system_or_period_missing")
                if set(components) != set(COMPONENTS):
                    restrictions.append("architectural_components_missing")
                if any(_known(c["version"]) is None for c in components.values()):
                    restrictions.append("architectural_component_version_unavailable")
            component_report = []
            for key in COMPONENTS:
                c = components.get(key)
                if c and c["contents_state"] == "supplied" and (not c["artifact_refs"] or any(
                        self.resolve(ref) is None or self.view.artifact(ref["record_id"])[1] is None for ref in c["artifact_refs"])):
                    restrictions.append("component_contents_unavailable")
                component_report.append({"component_id": key, "version_id": _known(c["version"]) if c else None,
                                         "version_state": c["version"]["state"] if c else "unknown",
                                         "contents_state": c["contents_state"] if c else "unknown"})
            complete = not restrictions
            if self.fixture and claim["kind"] != "label_conditioned":
                restrictions.append("fixture_cannot_establish_empirical_claim")
            elif claim["kind"] != "label_conditioned":
                restrictions.append("external_authentication_and_substantive_review_required")
            disposition = "supported_for_scope" if claim["kind"] == "label_conditioned" and complete else (
                "restricted" if complete and not self.fixture else "withheld")
            results.append({"claim_id": claim["claim_id"], "kind": claim["kind"], "artifact_ids": _unique(ids),
                "requirements": requirements, "components": component_report, "record_complete": complete,
                "disposition": disposition, "restrictions": _unique(restrictions),
                "allowed_scope": "supplied_label_conditioned_records" if disposition == "supported_for_scope" else "record_inspection_only",
                "operational_openness_established": False, "substantive_validation_performed": False})
        return results


def _core_item(item, artifact):
    """Evaluate a design obligation without overwriting the observed judgment."""
    role = item["role_id"]
    required_validity = "invalid" if role.endswith("-D") else "valid" if role.endswith(("-A", "-B")) else None
    required_family = None if role.startswith("CORE-X") else "SORT-" + role.split("-")[1]
    resolved = (item["mechanism_agreement"] and item["validity_agreement"]
                or any(a["record_consistent"] for a in item["adjudications"]))
    return {"role_id": role, "artifact_id": item["artifact_id"],
        "required_validity_status": required_validity, "required_family": required_family,
        "record_complete": bool(item["pair_record_consistent"] and resolved and not item["unresolved_schema_issue_ids"]
            and artifact and artifact["validity_status"] in {"valid", "invalid"}
            and (required_validity is None or artifact["validity_status"] == required_validity)
            and (required_family is None or artifact["structural_class_id"] == required_family)
            and (role.startswith("CORE-X") or artifact["membership_admitted"]))}


def _comparison_context(collection, records, conditions):
    all_local = {reason for slot in collection.slots for reason in slot["restrictions"]}
    shared = set(collection.restrictions) - all_local - {
        "external_authentication_required", "observed_call_order_unestablished",
        "matched_control_convention_differs_or_unknown", "deployment_changed"}
    selected = [slot for slot in collection.slots if slot["condition"] in conditions]
    shared.update(reason for slot in selected for reason in slot["restrictions"])
    actual = [(records[slot["primary_record_id"]], slot["submission"]) for slot in selected
              if slot["primary_record_id"] in records]
    times = [_time(_known(row["attempted_at"])) for row, _ in actual if _known(row["attempted_at"])]
    if any(later <= earlier for earlier, later in zip(times, times[1:])):
        shared.add("observed_call_order_unestablished")
    signatures = [_control_signature(row, submission) for row, submission in actual if submission]
    if signatures and any(s != signatures[0] for s in signatures[1:]):
        shared.add("matched_control_convention_differs_or_unknown")
    deployments = {tuple(_known(row["deployment"][name]) for name in
        ("model_identifier", "checkpoint_identifier", "deployment_identifier")) for row, _ in actual if row["attempt_status"] != "not_attempted"}
    if len(deployments) > 1:
        shared.add("deployment_changed")
    return _unique(shared)


def inspect_study_evidence(loaded: LoadedStudy, packet_id: str | None = None,
                           limits: ReadLimits | None = None) -> EvidenceAssessment:
    """Inspect a current packet and select audits, with no fallback qualification.

    Omit packet_id to inspect missing evidence and fixed audit opportunities.
    An explicitly named absent/unreadable packet never supplies default labels.
    """
    q = None
    try:
        q = _Qualification(loaded, packet_id, limits)
        independent = {r["assessment_id"]: q.independence_result(r) for r in q.raw["independence"]}
        artifacts = {r["record_id"]: q.qualify(r, independent) for r in q.view.current
                     if r["record_type"] == "artifact" and r["artifact_role"] in {"candidate", "core_positive", "core_defect", "core_boundary", "source"}
                     and r["record_id"] not in q.superseded}
        if any(aid not in artifacts for aid in q.qualifications):
            q.issues.append(_diag("qualification_artifact_scope_mismatch"))
        positions = q.positions()
        q.retain_audit_challenges(positions, artifacts)
        audit = q.audit(positions, artifacts)
        core_rows = [_core_item(item, artifacts.get(item["artifact_id"])) for item in q.review.items]
        core = {"planned_items": 32, "items": core_rows, "record_complete": len(core_rows) == 32
                    and not q.review.unresolved_schema_issue_ids and all(r["record_complete"] for r in core_rows),
                "unresolved_schema_issue_ids": q.review.unresolved_schema_issue_ids, "authentication_required": True}
        cells = []
        for block in (f"P{n:02d}" for n in range(1, 7)):
            for condition in "ABC":
                group = [p for p in positions if p["position"]["block_id"] == block and p["position"]["condition"] == condition]
                ids = [p["artifact_id"] for p in group if p["artifact_id"]]
                members = [artifacts[aid] for aid in ids]
                selected = [r for r in audit["targets"] if r["position"]["block_id"] == block and r["position"]["condition"] == condition]
                systematic = [r for r in audit["fixed_positions"] if r["position"]["block_id"] == block and r["position"]["condition"] == condition]
                reasons = []
                if len(ids) != 20:
                    reasons.append("original_position_inventory_incomplete")
                if any(not r["membership_admitted"] for r in members):
                    reasons.append("membership_incomplete")
                if any(r["validity_status"] not in {"valid", "invalid"} for r in members):
                    reasons.append("validity_incomplete")
                if any(r["claim_restrictions"] for r in members):
                    reasons.append("sample_independence_or_provenance_unestablished")
                if any(not r["review_record_complete"] for r in (*selected, *systematic)):
                    reasons.append("mandatory_audit_incomplete")
                cells.append({"block_id": block, "condition": condition, "planned_positions": 20,
                    "emitted_positions": sum(p["emitted"] for p in group), "linked_original_artifacts": len(ids),
                    "accepted_membership_count": sum(m["membership_admitted"] for m in members),
                    "class_counts": {cid: sum(m["structural_class_id"] == cid for m in members) for cid in sorted(CLASS_IDS)},
                    "validity_counts": dict(Counter(m["validity_status"] for m in members)),
                    "record_complete": not reasons, "restrictions": _unique(reasons), "fixture_context": q.fixture})
        comparisons = []
        for name, conditions in (("P1-B-vs-A", ("A", "B")), ("P5-C-vs-A", ("A", "C"))):
            affected = [c for c in cells if c["condition"] in conditions]
            restrictions = [reason for c in affected for reason in c["restrictions"]]
            restrictions.extend(_comparison_context(q.collection, q.view.records, conditions))
            if q.collection.preregistration.get("chronology") != "supplied_times_consistent":
                restrictions.append("prospective_registration_chronology_unestablished")
            if not core["record_complete"]:
                restrictions.append("core_validation_incomplete")
            comparisons.append({"comparison_id": name, "conditions": conditions,
                "cell_ids": tuple(c["block_id"] + ":" + c["condition"] for c in affected),
                "record_complete": not restrictions, "restrictions": _unique(restrictions),
                "prediction_evaluated": False, "empirical_claim_established": False})
        claims = q.claims(artifacts, core, audit, comparisons)
        if any(d.severity == "error" for d in q.issues):
            core["record_complete"] = False
            for row in (*cells, *comparisons, *claims):
                row["record_complete"] = False
                row["restrictions"] = _unique((*row["restrictions"], "supplied_study_has_errors"))
            for row in claims:
                row.update(disposition="withheld", allowed_scope="record_inspection_only")
        queue = [{"artifact_id": aid, "reasons": _unique((*a["membership_reasons"], *a["validity_reasons"]))}
                 for aid, a in artifacts.items() if a["membership_reasons"] or a["validity_reasons"]]
        queue.extend({"artifact_id": r["artifact_id"], "reasons": r["restrictions"]} for r in audit["targets"] if not r["review_record_complete"])
        result = EvidenceAssessment(tuple(q.issues), tuple(freeze(list(artifacts.values()))), freeze(audit), tuple(freeze(cells)),
            tuple(freeze(comparisons)), tuple(freeze(claims)), freeze(core), tuple(freeze(list(independent.values()))), tuple(freeze(queue)), q.fixture)
        if len(_serialize(result.as_dict())) > q.limits.max_bundle_bytes:
            raise InputError("evidence_output_budget_exceeded")
        return result
    except (InputError, KeyError, TypeError, ValueError, RecursionError, StopIteration) as exc:
        issues = list(q.issues) if q else []
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_evidence_context"))
        return EvidenceAssessment(tuple(issues), fixture_context=q.fixture if q else False)
