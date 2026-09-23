"""Passive preparation of six separately scoped operational activity packets.

Completeness means the supplied details are present for human review. This module
does not authenticate evidence or authorization and never starts an activity.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from typing import Any, Mapping

from .contracts import Diagnostic, InputError, freeze
from .local_io import ReadLimits
from .study_records import (COMMON_FIELDS, RECORD_TYPES, LoadedStudy, _cycle,
                            _known, _limits, _physical, _serialize, _validate)

ACTIVITIES = ("core_construction", "external_validation", "human_review",
              "pilot_collection", "main_collection", "scientific_release")
COMMON_REQUIREMENTS = ("source_versions", "scope_restrictions", "storage_access",
                       "provenance_responsibility")
ACTIVITY_REQUIREMENTS = {
    "core_construction": ("core_role_specifications", "constructor_lineage", "review_route"),
    "external_validation": ("candidate_suite_identity", "environment_containment",
                            "trusted_oracle", "resource_limits", "calibration_route",
                            "original_receipts"),
    "human_review": ("human_qualifications", "identity_relationships", "original_first_passes",
                     "exposure", "communication_route"),
    "pilot_collection": ("deployment_identity", "control_cap_semantics", "exact_messages_slots",
                         "retry_failure_stop_policy", "original_exports"),
    "main_collection": ("deployment_identity", "control_cap_semantics", "exact_messages_slots",
                        "retry_failure_stop_policy", "original_exports", "registration_freeze",
                        "core_qualification"),
    "scientific_release": ("claim_evidence", "ec_disclosures_currentness", "correction_route",
                           "claim_reviewer", "destination_scope"),
}
MINIMUM_DEPENDENCIES = {
    "external_validation": ("core_construction",),
    "human_review": ("core_construction",),
    "main_collection": ("core_construction", "external_validation", "human_review"),
}

_REF = {"reference": sorted(RECORD_TYPES)}
_KNOWLEDGE_TEXT = {"knowledge": "text"}
ACTIVITY_PACKET_SCHEMA = {"object": {
    "kind": {"literal": "activity_readiness_packet"}, "version": {"literal": "0.1"},
    "study_id": "id", "study_version": "id", "scope": COMMON_FIELDS["scope"],
    "activities": {"array": {"object": {
        "activity": {"enum": list(ACTIVITIES)},
        "disposition": {"enum": ["planned", "omitted"]},
        "omission_reason": _KNOWLEDGE_TEXT,
        "action": _KNOWLEDGE_TEXT,
        "responsible_operator": {"knowledge": "id"},
        "authorization_ref": {"knowledge": _REF},
        "time_window": {"knowledge": {"object": {"start": "timestamp", "end": "timestamp"}}},
        "input_pins": {"array": {"object": {"packet_id": "id", "sha256": "hash"}}},
        "dependencies": {"array": {"enum": list(ACTIVITIES)}},
        "requirements": {"array": {"object": {
            "requirement_id": {"enum": sorted(set(COMMON_REQUIREMENTS).union(
                *(set(items) for items in ACTIVITY_REQUIREMENTS.values())))},
            "basis": _KNOWLEDGE_TEXT, "evidence_refs": {"array": _REF}}}},
        "collection_limits": {"knowledge": {"object": {
            "maximum_calls": "nonnegative", "maximum_positions": "nonnegative",
            "maximum_output_tokens": "nonnegative", "monetary_ceiling": "exact_nonnegative",
            "currency": "id", "stop_behavior": "text"}}},
    }}},
}}


def _diag(code: str, path: str = "activity_packet") -> Diagnostic:
    return Diagnostic(code, "study", "study", path)


class _Issues(list):
    def append(self, item):
        if len(self) >= 128:
            raise InputError("diagnostic_limit_exceeded")
        super().append(item)


def _packet_object_count(raw, bounds):
    """Count even malformed objects before recursive shape diagnostics expand."""
    count, pending = 0, [raw]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            count += 1
            if count > bounds.max_records:
                raise InputError("record_count_exceeded")
            pending.extend(item.values())
        elif isinstance(item, list):
            # A long scalar or nested-list array must also stay bounded.
            if len(item) > bounds.max_records:
                raise InputError("record_count_exceeded")
            pending.extend(item)
    return count


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _alias(value: str) -> str:
    return "ref-" + _hash(value.encode("utf-8"))


def _public_knowledge(value: Mapping[str, Any]) -> dict[str, Any]:
    # Even apparently innocuous operator/action/amount/time prose can disclose
    # credentials or private identities. Exact originals stay in the input.
    if value["state"] == "known":
        return {"state": "known", "value_sha256": _hash(_serialize(value["value"]))}
    return {"state": value["state"], "reason_sha256": _hash(value["reason"].encode("utf-8"))}


def _public_ref(value: Mapping[str, str]) -> dict[str, str]:
    return {"record_type": value["record_type"], "record_version": value["record_version"],
            "record_alias": _alias(value["record_id"])}


@dataclass(frozen=True)
class ActivityPacketAssessment:
    """Bounded public result; no asserted field can grant execution authority."""

    result: Mapping[str, Any] = field(repr=False)
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "error" for issue in self.diagnostics)

    @property
    def exit_code(self) -> int:
        return 2 if self.has_errors else 0

    @property
    def json_bytes(self) -> bytes:
        return _serialize(self.result) + b"\n"

    def as_dict(self) -> dict[str, Any]:
        return json.loads(self.json_bytes)


def inspect_activity_packet(loaded: LoadedStudy, data: bytes,
                            limits: ReadLimits | None = None) -> ActivityPacketAssessment:
    """Check details for review against an already acquired, current study.

    Six rows are required, independently assessed. Known input hashes must match
    the acquired snapshots; a missing attachment remains a gap. Typed evidence
    and authorization references must resolve to nonsuperseded records in this
    scope. Known operational correction dependencies remain explicit gaps.
    The function reads no files and performs no collection, execution or contact.
    """
    issues: list[Diagnostic] = _Issues()
    result: dict[str, Any] = {
        "kind": "activity_readiness_assessment", "version": "0.1",
        "status": "malformed", "activities": [],
        "execution_authorized": False, "substantive_validation_performed": False,
        "external_evidence_authenticated": False, "empirical_evidence_established": False,
        "interpretation": "packet_completeness_only",
    }
    try:
        bounds = _limits(limits)
        raw = _physical(data, bounds)
        count = _packet_object_count(raw, bounds)
        _validate(raw, ACTIVITY_PACKET_SCHEMA, "activity_packet", issues)
        if issues:
            return _finish(result, issues)
        _physical(_serialize(raw) + b"\n", bounds)
        if not isinstance(loaded, LoadedStudy) or loaded.packet is None or loaded.has_errors or loaded.packet.has_errors:
            raise InputError("invalid_study_for_activity_packet")
        acquired_bytes = sum(len(snapshot.content) for snapshot in loaded.snapshots.values())
        if max(acquired_bytes, loaded.total_read_bytes) + len(data) > bounds.max_bundle_bytes:
            raise InputError("bundle_size_exceeded")
        if any(len(snapshot.content) > bounds.max_file_bytes for snapshot in loaded.snapshots.values()):
            raise InputError("file_size_exceeded")
        if count + len(loaded.packet.records) + sum(item.checked_record_count or 0 for item in loaded.attachments) > bounds.max_records:
            raise InputError("record_count_exceeded")
        study = loaded.packet.data
        if raw["study_id"] != study["study_id"]:
            issues.append(_diag("study_identity_mismatch"))
        if raw["study_version"] != study["study_version"]:
            issues.append(_diag("study_version_mismatch"))
        registrations = [r.data for r in loaded.packet.records if r.record_type == "study_registration"
                         and r.study_version == study["study_version"]]
        if len(registrations) != 1 or raw["scope"] != registrations[0]["scope"]:
            issues.append(_diag("scope_mismatch"))
        names = [row["activity"] for row in raw["activities"]]
        if len(names) != len(ACTIVITIES) or set(names) != set(ACTIVITIES):
            issues.append(_diag("activity_set_mismatch"))
        if issues:
            return _finish(result, issues)

        records = {r.record_id: r for r in loaded.packet.records}
        inventory = {r["packet_id"]: r for r in study["packet_inventory"]}
        observed = {r.packet_id: r for r in loaded.attachments}
        # Reuse the existing operational dependency rules without compiling or
        # inspecting candidate code. Evidence-qualification packet extensions
        # remain outside this preparatory assessment.
        from .study_bridge import _corrections
        from .study_review import _StudyView
        view = _StudyView(loaded)
        invalidated = set(_corrections(view, {})["invalidated_record_ids"])
        superseded = {_known(r.data["supersedes"])["record_id"] for r in loaded.packet.records
                      if _known(r.data["supersedes"]) is not None}
        affected_packets = {_known(r.data["content"])["packet_id"] for r in loaded.packet.records
                            if r.record_id in invalidated and r.record_type == "artifact"
                            and _known(r.data["content"]) is not None}
        protocol = registrations[0]["protocol"]
        hero_collection = protocol["design"] == "sorting_abc" and protocol["protocol_id"] == "hero_sort_abc_v1"
        graph = {row["activity"]: tuple(row["dependencies"]) for row in raw["activities"]}
        if _cycle(graph):
            issues.append(_diag("dependency_cycle"))

        def check_ref(reference, path):
            target = records.get(reference["record_id"])
            if target is None:
                issues.append(_diag("missing_reference", path))
            elif target.record_type != reference["record_type"] or target.record_version != reference["record_version"]:
                issues.append(_diag("reference_type_mismatch", path))
            elif target.study_version != study["study_version"]:
                issues.append(_diag("reference_version_mismatch", path))
            elif target.data["scope"] != raw["scope"]:
                issues.append(_diag("scope_mismatch", path))
            elif target.record_id in superseded:
                issues.append(_diag("superseded_activity_reference", path))
            return reference["record_id"] not in invalidated

        for index, row in enumerate(raw["activities"]):
            path = f"activity_packet.activities[{index}]"
            activity = row["activity"]
            omitted = row["disposition"] == "omitted"
            gaps: list[str] = []
            if omitted:
                if activity != "pilot_collection" or row["omission_reason"]["state"] != "known":
                    issues.append(_diag("invalid_activity_omission", path))
            elif row["omission_reason"]["state"] != "not_applicable":
                issues.append(_diag("state_contradiction", path + ".omission_reason"))
            if len(row["dependencies"]) != len(set(row["dependencies"])):
                issues.append(_diag("duplicate_value", path + ".dependencies"))
            # A packet describes dependencies before those external activities
            # occur. Their incomplete packets do not prevent this preparation.
            if activity == "core_construction" and row["dependencies"]:
                issues.append(_diag("core_downstream_dependency", path + ".dependencies"))
            if activity == "main_collection" and "pilot_collection" in row["dependencies"]:
                issues.append(_diag("optional_pilot_is_not_mandatory", path + ".dependencies"))
            if not omitted:
                gaps.extend("dependencies." + needed for needed in MINIMUM_DEPENDENCIES.get(activity, ())
                            if needed not in row["dependencies"])
            for key in ("action", "responsible_operator", "authorization_ref", "time_window"):
                if not omitted and row[key]["state"] != "known":
                    gaps.append(key)
            authorization = _known(row["authorization_ref"])
            if authorization is not None:
                if not check_ref(authorization, path + ".authorization_ref") and not omitted:
                    gaps.append("authorization_ref.correction_pending")
            window = _known(row["time_window"])
            if window is not None and datetime.fromisoformat(window["end"].replace("Z", "+00:00")) <= datetime.fromisoformat(window["start"].replace("Z", "+00:00")):
                issues.append(_diag("invalid_time_window", path + ".time_window"))

            pins = [pin["packet_id"] for pin in row["input_pins"]]
            if len(pins) != len(set(pins)):
                issues.append(_diag("duplicate_packet_id", path + ".input_pins"))
            if not omitted and not pins:
                gaps.append("input_pins")
            public_pins = []
            for ordinal, pin in enumerate(row["input_pins"]):
                field_path = f"{path}.input_pins[{ordinal}]"
                entry = inventory.get(pin["packet_id"])
                item = observed.get(pin["packet_id"])
                available = False
                if entry is None:
                    issues.append(_diag("packet_not_declared", field_path))
                else:
                    expected = _known(entry["sha256"])
                    actual = item.actual_sha256 if item is not None else None
                    if expected is not None and expected != pin["sha256"] or actual is not None and actual != pin["sha256"]:
                        issues.append(_diag("attachment_hash_mismatch", field_path))
                    location = _known(entry["location"])
                    supplied = (loaded.snapshots.get(location["path"])
                                if location and location["kind"] == "local" else None)
                    if supplied is not None and (
                            not isinstance(supplied.content, bytes)
                            or len(supplied.content) != supplied.size_bytes
                            or _hash(supplied.content) != supplied.sha256
                            or _known(entry["size_bytes"]) not in (None, supplied.size_bytes)
                            or item is not None and (item.actual_sha256 not in (None, supplied.sha256)
                                                    or item.actual_size_bytes not in (None, supplied.size_bytes))):
                        issues.append(_diag("activity_snapshot_identity_mismatch", field_path))
                        snapshot = None
                    else:
                        snapshot = view.snapshot(pin["packet_id"])
                    if snapshot is not None:
                        if _hash(snapshot.content) != pin["sha256"]:
                            issues.append(_diag("attachment_hash_mismatch", field_path))
                        else:
                            available = True
                    if not available and not omitted:
                        gaps.append(f"input_pins[{ordinal}]")
                    if pin["packet_id"] in affected_packets and not omitted:
                        gaps.append(f"input_pins[{ordinal}].correction_pending")
                public_pins.append({"packet_alias": _alias(pin["packet_id"]), "sha256": pin["sha256"],
                                    "snapshot_available": available,
                                    "operational_correction_pending": pin["packet_id"] in affected_packets})

            expected_requirements = set(COMMON_REQUIREMENTS + ACTIVITY_REQUIREMENTS[activity])
            req_ids = [req["requirement_id"] for req in row["requirements"]]
            if len(req_ids) != len(expected_requirements) or set(req_ids) != expected_requirements:
                issues.append(_diag("activity_requirement_set_mismatch", path + ".requirements"))
            public_requirements = []
            for ordinal, req in enumerate(row["requirements"]):
                ref_path = f"{path}.requirements[{ordinal}].evidence_refs"
                refs = [tuple(reference[key] for key in ("record_type", "record_id", "record_version"))
                        for reference in req["evidence_refs"]]
                if len(refs) != len(set(refs)):
                    issues.append(_diag("duplicate_value", ref_path))
                current_refs = [check_ref(reference, f"{ref_path}[{position}]")
                                for position, reference in enumerate(req["evidence_refs"])]
                if not omitted and (req["basis"]["state"] != "known" or not refs):
                    gaps.append(req["requirement_id"])
                if not omitted and not all(current_refs):
                    gaps.append(req["requirement_id"] + ".correction_pending")
                public_requirements.append({"requirement_id": req["requirement_id"],
                    "basis": _public_knowledge(req["basis"]),
                    "evidence_refs": [_public_ref(reference) for reference in req["evidence_refs"]]})

            collection = activity in ("pilot_collection", "main_collection")
            if collection and not omitted and not hero_collection:
                gaps.append("unsupported_collection_design")
            limits_value = _known(row["collection_limits"])
            if not omitted and collection and limits_value is None:
                gaps.append("collection_limits")
            if not collection and row["collection_limits"]["state"] != "not_applicable":
                issues.append(_diag("collection_limits_outside_collection", path + ".collection_limits"))
            if collection and hero_collection and limits_value is not None:
                calls, positions = (6, 30) if activity == "pilot_collection" else (72, 360)
                if (limits_value["maximum_calls"] > calls or limits_value["maximum_positions"] > positions
                        or limits_value["maximum_output_tokens"] > calls * 8192):
                    issues.append(_diag("collection_design_limit_exceeded", path + ".collection_limits"))

            public = {"activity": activity, "disposition": row["disposition"],
                      "packet_status": "omitted" if omitted else "gaps_recorded" if gaps else "complete_for_review",
                      "outstanding_requirements": gaps, "dependencies": list(row["dependencies"]),
                      "requirements": public_requirements, "input_pins": public_pins,
                      "execution_authorized": False, "operational_readiness": "not_verified"}
            for key in ("action", "responsible_operator", "authorization_ref", "time_window",
                        "omission_reason", "collection_limits"):
                public[key] = _public_knowledge(row[key])
            if authorization is not None:
                public["authorization_ref"]["reference"] = _public_ref(authorization)
            result["activities"].append(public)

        result.update({"status": "assessed", "study_alias": _alias(study["study_id"]),
                       "study_version_alias": _alias(study["study_version"]),
                       "material_role": study["material_role"], "evidence_policy": study["evidence_policy"],
                       "input_sha256": _hash(data),
                       "collection_design": "hero_sort_abc_v1" if hero_collection else "unsupported_for_collection",
                       "correction_scope": "operational_record_dependencies",
                       "evidence_qualification": "not_assessed",
                       "dependency_interpretation": "declared_activity_dependencies_not_execution_fulfillment"})
    except (InputError, TypeError, ValueError, RecursionError, KeyError) as exc:
        # Keep a controlled final failure even if shape findings hit their cap.
        code = exc.code if isinstance(exc, InputError) else "invalid_activity_packet"
        if len(issues) >= 128:
            issues[-1] = _diag(code)
        else:
            issues.append(_diag(code))
    return _finish(result, issues)


def _finish(result: dict[str, Any], issues: list[Diagnostic]) -> ActivityPacketAssessment:
    if issues:
        result["status"] = "malformed"
        # Partial positive rows cannot be mistaken for accepted input when a
        # different record invalidates the packet.
        result["activities"] = []
    result["diagnostics"] = [{"code": item.code, "field": item.field,
                              "severity": item.severity} for item in issues]
    return ActivityPacketAssessment(freeze(result), tuple(issues))
