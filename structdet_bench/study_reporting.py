"""Evidence-first public companion for passive study preparation.

One bounded, sanitized tree supplies both JSON and Markdown. Supplied prose,
identities and paths remain in the restricted input; public aliases and digests
retain their associations. No empirical validation or analysis is performed.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, replace
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any, Mapping

from .contracts import CLASS_IDS, Diagnostic, ExactNumber, InputError, freeze
from .local_io import ReadLimits, load_bundle
from .populations import build_populations
from .study_bridge import Compilation, compile_study, _stage
from .study_collection import inspect_collection
from .study_evidence import CONDITIONS, parse_evidence_qualification_bytes
from .study_records import LoadedStudy, _serialize
from .study_review import _StudyView

DISCLOSURE_IDS = (
    "claim_deployment_scope", "structural_relations", "source_transformation_lineage",
    "contamination_exposure", "evaluator_relationships_bias_controls",
    "low_frequency_high_severity", "long_horizon_recovery_override",
    "live_field_evidence", "correction_path_actual_action", "currentness_expiry",
)
_ACTIVITIES = ("core_construction", "external_validation", "human_review", "pilot_collection",
               "main_collection", "analysis", "scientific_release")
# These fields come from strictly typed enums or software-produced codes, never
# arbitrary study prose. Every other string is withheld unless explicitly typed.
_SEMANTIC = frozenset({
    "code", "severity", "reason", "reasons", "restrictions", "membership_reasons", "validity_reasons",
    "scope_restrictions", "claim_restrictions", "fields", "manifest_fields", "field", "record_type",
    "target_record_type", "source_record_type", "profile", "requested_profile", "data_role", "material_role",
    "evidence_policy", "evidence_scope", "allowed_scope", "kind", "status", "state", "disposition",
    "claim_disposition", "assignment_status", "declared_assignment_status", "validity_status", "artifact_role",
    "outcome", "dimension", "contents_state", "version_state", "action_status", "phase", "condition",
    "conditions", "opportunity", "role", "view", "formula_id", "component_id", "compiler_method_id",
    "registered_comparisons_to_recompute", "comparison_id", "cell_ids", "block_id", "structural_class_id",
})
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_CODE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.:-]{0,119}\Z")


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def public_alias(value: str) -> str:
    """Deterministic join key, never a claim of anonymization/authentication."""
    return "ref-" + _sha(value.encode("utf-8"))


def _known(value):
    return value.get("value") if isinstance(value, Mapping) and value.get("state") == "known" else None


def _text(value: str):
    return {"state": "known", "value_sha256": _sha(value.encode("utf-8")),
            "visibility": "restricted_input", "public_text_withheld": True}


def _knowledge(value, *, scalar=False, identity=False, timestamp=False, required=False):
    if not isinstance(value, Mapping) or "state" not in value:
        return {"state": "missing"}
    state = value["state"]
    if state != "known":
        result = {"state": "missing" if required and state == "not_applicable" else state}
        if required and state == "not_applicable":
            result.update(declared_state=state, reason_code="mandatory_evidence_missing")
        if "reason" in value:
            result["reason_sha256"] = _sha(value["reason"].encode("utf-8"))
        return result
    known = value["value"]
    if identity:
        return {"state": state, "public_ref": public_alias(known)}
    if isinstance(known, Mapping) and "record_id" in known:
        return {"state": state, "public_ref": public_alias(known["record_id"]),
                "record_type": known["record_type"], "record_version": known["record_version"]}
    if scalar:
        if isinstance(known, ExactNumber):
            known = {"exact_decimal": known.token}
        return {"state": state, "value": known}
    if timestamp:
        return {"state": state, "value": known}
    if isinstance(known, str):
        return _text(known)
    return {"state": state, "value_sha256": _sha(_serialize(known)), "visibility": "restricted_input"}


def _public(value, key=""):
    """Sanitize trusted assessment trees, including attacker-chosen join IDs.

    Only software-owned keys occur in these result trees. Unknown strings and
    manifest field names still become opaque references. Callers must never
    pass raw records or raw submitted packet objects through this function.
    """
    if isinstance(value, Mapping):
        return {k: _public(v, k) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_public(v, key) for v in value]
    if isinstance(value, ExactNumber):
        return {"exact_decimal": value.token}
    if not isinstance(value, str):
        return value
    if (key == "sha256" or key.endswith("_sha256")) and _HASH.fullmatch(value):
        return value
    if key in {"record_version", "target_record_version", "version"} and value == "0.1":
        return value
    if key in _SEMANTIC and _CODE.fullmatch(value):
        return value
    return public_alias(value)


def _json(value):
    # Insertion order intentionally puts evidence and scope before counts.
    return (json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _plain(value):
    if isinstance(value, Mapping):
        return {key: _plain(child) for key, child in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(child) for child in value]
    if isinstance(value, ExactNumber):
        return {"exact_decimal": value.token}
    return value


def _markdown(tree):
    lines = ["# Study readiness", "", "Passive supplied-record inspection. External authentication and scientific qualification remain separate.", ""]
    role = tree.get("material_role", "unavailable")
    evidence = tree.get("evidence_status", "unavailable")
    compilation = tree.get("compilation", {})
    eligible = compilation.get("eligible", False)
    scope = tree.get("claim_scope", {})
    profile = scope.get("requested_profile", "unavailable")
    lines.extend([f"Material: **{role}**. Evidence: **{evidence}**.", "",
        f"Requested profile: `{profile}`. Compilation: **{'eligible' if eligible else 'withheld'}**.", "",
        "This report describes supplied records and their gaps. No empirical claim or independent validation is established.", "",
        "## Disclosure overview", "", "| Disclosure | Status |", "| --- | --- |"])
    for row in tree.get("ec_disclosures", ()):
        lines.append("| " + row["id"].replace("_", " ") + " | " + row["status"].replace("_", " ") + " |")
    lines.append("")
    lines.extend(["## Study identity and source pins", "", "```json",
        _json(tree.get("study_identity", {})).decode("utf-8").rstrip(), "```", ""])
    cells = tree.get("populations_and_denominators", {}).get("compiled_cells", {}).get("cells", ())
    if cells:
        lines.extend(["## Compiled population overview", "", "Each row is a distinct selected carrier cell. Counts do not establish independent evidence.", "",
            "| Public cell reference | Selected | Classified all | Classified valid |", "| --- | ---: | ---: | ---: |"])
        for cell in cells:
            def number(value):
                return "unavailable" if value is None else str(value)
            lines.append("| " + cell["cell_ref"] + " | " + number(cell["selected_population"]["value"]) + " | "
                + number(cell["populations"]["classified_all"]["count"]) + " | "
                + number(cell["populations"]["classified_valid"]["count"]) + " |")
        lines.append("")
    lines.extend(["## Full public record", "", "Known private text is represented by its digest and remains available in the restricted source. Public aliases preserve associations.", ""])
    for key, value in tree.items():
        lines.extend(["## " + key.replace("_", " ").capitalize(), ""])
        if isinstance(value, (dict, list)):
            lines.extend(["```json", _json(value).decode("utf-8").rstrip(), "```", ""])
        else:
            lines.extend([json.dumps(value, ensure_ascii=True), ""])
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")


@dataclass(frozen=True)
class StudyReadiness:
    readiness: Mapping[str, Any]
    provenance: Mapping[str, Any]
    compilation_manifest: Mapping[str, Any]
    compilation: Compilation = field(repr=False)
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def has_errors(self):
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0

    def with_publication(self, *, analysis_bundle_created: bool, publication_mode: str,
                         restriction: str | None = None):
        """Prepare the prospective receipt committed by atomic CLI publication."""
        if (type(analysis_bundle_created) is not bool or publication_mode not in {"analysis_bundle", "compiled", "readiness_only", "prepare"}
                or (analysis_bundle_created and (not self.compilation.compiled or self.has_errors))):
            raise InputError("invalid_study_publication_status")
        ready, manifest = self.as_dict(), _plain(self.compilation_manifest)
        ready["compilation"]["analysis_bundle_created"] = analysis_bundle_created
        ready["publication"] = {"mode": publication_mode, "analysis_bundle_created": analysis_bundle_created}
        manifest.update(analysis_bundle_created=analysis_bundle_created, publication_mode=publication_mode)
        if restriction:
            if restriction not in {"compilation_bundle_name_unrepresentable", "compilation_sidecar_name_collision", "compilation_withheld"}:
                raise InputError("invalid_study_publication_restriction")
            ready["publication"]["restriction"] = restriction
            manifest["bundle_creation_restriction"] = restriction
        return replace(self, readiness=freeze(ready), compilation_manifest=freeze(manifest))

    def as_dict(self):
        return _plain(self.readiness)

    @property
    def json_bytes(self):
        return _json(self.as_dict())

    @property
    def markdown_bytes(self):
        return _markdown(self.as_dict())

    @property
    def provenance_json_bytes(self):
        return _json(_plain(self.provenance))

    @property
    def compilation_manifest_json_bytes(self):
        return _json(_plain(self.compilation_manifest))


def _activities(records):
    result = []
    for activity in _ACTIVITIES:
        found = [r for r in records if r["record_type"] == "activity_readiness" and r["activity"] == activity]
        result.append({"activity": activity, "status": "supplied_assertions_only" if found else "missing",
            "operational_readiness_established": False, "records": [{
                "record_ref": public_alias(r["record_id"]), "declared_state": r["state"],
                "responsible_operator": _knowledge(r["responsible_operator"], identity=True, required=True),
                "authorization": _knowledge(r["authorization_ref"], required=True),
                "prerequisites": [{"requirement_ref": public_alias(p["requirement_id"]),
                    "mandatory": p["mandatory"], "declared_outcome": p["outcome"],
                    "effective_outcome": "unresolved" if p["mandatory"] and p["outcome"] == "not_applicable" else p["outcome"],
                    "basis": _knowledge(p["basis"], required=p["mandatory"]),
                    "evidence_record_refs": [public_alias(e["record_id"]) for e in p["evidence_refs"]]} for p in r["prerequisites"]],
                "outstanding_requirement_refs": [public_alias(x) for x in r["outstanding_requirements"]]}
                for r in found]})
    return result


def _raw_qualification(view, packet_id):
    if packet_id is None:
        return {}
    snapshot = view.snapshot(packet_id)
    if snapshot is None:
        return {}
    parsed = parse_evidence_qualification_bytes(snapshot.content)
    return {} if parsed.has_errors else parsed.data


def _disclosures(registration, records, assessment, correction, raw_qualification, compiled):
    artifacts = [r for r in records if r["record_type"] == "artifact"]
    reviews = [r for r in records if r["record_type"] in {"human_review", "adjudication"}]
    claims = raw_qualification.get("claims", ())
    evidence = raw_qualification.get("evidence", ())
    openness = any(r["kind"] == "operational_openness" for r in claims)
    longitudinal = registration["protocol"]["longitudinal_input"]
    legacy = _known(registration["protocol"]["legacy_profile_input"])
    legacy_long = bool(compiled and registration["requested_profile"] == "structdet_longitudinal_v1"
                       and legacy and legacy["profile"] == "structdet_longitudinal_v1")
    no_long_claim = (registration["requested_profile"] != "structdet_longitudinal_v1"
        and longitudinal["state"] == "not_applicable" and not openness)
    field = [r for r in evidence if r["purpose"] == "external_presence"]
    frame = registration["frame_definition"]
    currentness = registration["currentness"]
    rows = [
        {"id": DISCLOSURE_IDS[0], "status": "supplied_scope_only", "scope": _text(registration["claim_scope"]),
         "requested_profile": registration["requested_profile"], "deployment_claims": [{
             "claim_ref": public_alias(c["claim_id"]), "kind": c["kind"], "statement": _text(c["statement"]),
             "system": _knowledge(c["system_id"], identity=True, required=True),
             "period": {"state": c["period"]["state"], **({"value": dict(_known(c["period"]))} if _known(c["period"]) else {})}}
             for c in claims], "claim_established": False},
        {"id": DISCLOSURE_IDS[1], "status": "supplied_frame_only", "frame_fields": {k: _knowledge(v, required=True)
            for k, v in frame.items() if k != "load_bearing_invariants"},
         "represented_invariants": [_text(v) for v in frame["load_bearing_invariants"]],
         "omitted_relations": {"state": "unresolved", "reason_code": "no_separate_typed_omissions_assessment"},
         "scope_note": "The declared bounded sorting frame limits interpretation; supplied prose is restricted."},
        {"id": DISCLOSURE_IDS[2], "status": "supplied_lineage_only" if artifacts else "missing", "artifacts": [{
            "artifact_ref": public_alias(r["record_id"]), "source": _knowledge(r["original_source"], required=True),
            "ai_assistance": _knowledge(r["ai_assistance"], required=True),
            "lineage_record_refs": [public_alias(x["record_id"]) for x in r["lineage_refs"]],
            "transformations": [{"transformation_ref": public_alias(t["transformation_id"]),
                "operation": _text(t["operation"]), "operator": _knowledge(t["operator"], identity=True, required=True),
                "performed_at": _knowledge(t["performed_at"], timestamp=True, required=True),
                "output_sha256": t["output_sha256"], "source_record_refs": [public_alias(s["record_id"]) for s in t["source_refs"]]}
                for t in r["transformations"]]} for r in artifacts], "source_authentication_performed": False},
        {"id": DISCLOSURE_IDS[3], "status": "supplied_disclosures_only", "study_exposure": _knowledge(registration["exposure"], required=True),
         "preregistration_exposure": _knowledge(registration["preregistration"]["exposure_at_registration"], required=True),
         "artifact_exposure": [{"artifact_ref": public_alias(r["record_id"]), "exposure": _knowledge(r["exposure"], required=True)} for r in artifacts],
         "contamination_excluded": False},
        {"id": DISCLOSURE_IDS[4], "status": "supplied_review_records_only" if reviews else "missing", "required": True,
         "reviews": [{"review_ref": public_alias(r["record_id"]), "artifact_ref": public_alias(r["artifact_ref"]["record_id"]),
            "artifact_sha256": r["artifact_sha256"], "reviewer_ref": public_alias(r.get("reviewer", r.get("adjudicator"))["reviewer_id"]),
            "entity_kind": r.get("reviewer", r.get("adjudicator"))["entity_kind"],
            "disclosures": {k: _knowledge(r.get("reviewer", r.get("adjudicator"))[k], required=True)
                for k in ("qualifications", "relationships", "exposure", "machine_assistance")},
            "declared_independence": _knowledge(r["independence"]["declared_independent"], scalar=True, required=True),
            "blinding": {"withheld_fields": list(r["blinding"]["withheld_fields"]),
                "limitation_count": len(r["blinding"]["limitations"])} if "blinding" in r else {"state": "not_assessed"}}
            for r in reviews], "actual_human_identity_authenticated": False},
        {"id": DISCLOSURE_IDS[5], "status": "label_conditioned_counts_only" if any(a["membership_admitted"] for a in assessment.get("artifacts", ())) or compiled else "unavailable",
         "fixed_sorting_cells_applicability": "selected_operational_design" if registration["protocol"]["design"] == "sorting_abc" else "outside_selected_operational_design",
         "per_cell_class_counts": _public(assessment.get("cells", ())), "low_frequency_rule": "One or two admitted original artifacts in the fixed 20-position cell.",
         "high_severity_results": {"state": "unavailable", "reason_code": "no_typed_severity_outcome_contract"},
         "numeric_population_source": "populations_and_denominators.compiled_cells", "empirical_tail_claim_established": False},
        {"id": DISCLOSURE_IDS[6], "status": "not_applicable" if no_long_claim else "supplied_input_only" if _known(longitudinal) or legacy_long else "missing",
         "declared_input": _knowledge(longitudinal, required=not no_long_claim and not legacy_long),
         "selected_carrier_route": "legacy_profile_input" if legacy_long else "longitudinal_input" if _known(longitudinal) else None,
         "selected_carrier_ref": public_alias(legacy["artifact_ref"]["record_id"]) if legacy_long else None,
         "justification_code": "explicit_no_longitudinal_claim_in_selected_bounded_profile" if no_long_claim else "longitudinal_evidence_requires_existing_L_analysis",
         "recovery_or_override_established": False},
        {"id": DISCLOSURE_IDS[7], "status": "supplied_scoped_events_only" if field else "missing", "required_for_operational_openness": openness,
         "evidence_refs": [{"evidence_ref": public_alias(e["evidence_id"]), "target_ref": public_alias(e["target_ref"]["record_id"]),
             "source_ref": public_alias(e["source_ref"]["record_id"]), "state": e["state"], "method": e["method"]} for e in field],
         "live_deployment_performance_established": False, "continuing_external_contact_established": False,
         "scope_note": "Model responses alone do not establish live deployment evidence or continuing external contact."},
        {"id": DISCLOSURE_IDS[8], "status": "supplied_actions_only" if correction.get("incidents") else "missing",
         "correction_path": [{"incident_ref": public_alias(r["record_id"]), "action": _knowledge(r["action"], required=True),
             "reviewer_authority": _knowledge(r["reviewer_authority"], required=True),
             "performed_at": _knowledge(r["performed_at"], timestamp=True)} for r in records if r["record_type"] == "correction_incident"],
         "assessment": _public(correction), "actual_action_authenticated": False},
        {"id": DISCLOSURE_IDS[9], "status": currentness["state"], "declared_currentness": currentness["state"],
         "assessed_at": _knowledge(currentness["assessed_at"], timestamp=True, required=True),
         "expires_at": _knowledge(currentness["expires_at"], timestamp=True, required=True),
         "basis": _knowledge(currentness["basis"], required=True), "effective_currentness": "unresolved",
         "fresh_external_review_performed": False},
    ]
    return rows


def _compiled_populations(compilation):
    if not compilation.compiled:
        return {"status": "unavailable", "reason_code": "analysis_bundle_withheld", "cells": []}
    with TemporaryDirectory(prefix="structdet-readiness-populations-") as temporary:
        root = Path(temporary)
        _stage(root, compilation.files)
        bundle = load_bundle(root / compilation.bundle_path, limits=compilation.limits)
        if bundle.has_errors:
            raise InputError("readiness_compiled_inventory_rejected")
        result = build_populations(bundle)
    cells = []
    for cell in result.cells:
        inv = cell.inventory
        cells.append({"cell_ref": public_alias(inv.cell_id), "scope": "selected_compiled_carrier_cell",
            "planned_positions": {"status": inv.plan_status, "value": len(inv.positions) if inv.plan_status == "available" else None,
                "reasons": list(inv.plan_reasons)},
            "recorded_invocations": inv.recorded_invocations, "attempt_status_counts": dict(inv.attempt_status_counts),
            "realizations": {"status": inv.realization_count.status, "value": inv.realization_count.value},
            "selected_population": {"status": inv.selected_count.status, "value": inv.selected_count.value,
                "sample_refs": [public_alias(s) for s in inv.selected_sample_ids]},
            "classification_status_counts": dict(cell.assignment_status_counts),
            "classification_admission_counts": dict(cell.assignment_acceptance_counts),
            "validity_status_counts": dict(cell.validity_status_counts),
            "populations": {name: {"status": p.status, "count": p.count, "class_counts": dict(p.class_counts), "reasons": list(p.reasons)}
                for name, p in cell.populations.items()},
            "coverage": {name: {"numerator": r.numerator, "denominator": r.denominator, "status": r.status, "reason": r.reason}
                for name, r in cell.ratios.items()}})
    return {"status": "available", "numeric_analysis_performed": False, "cells": cells}


def _denominators(view, records, assessment, compilation, registration, collection):
    calls = [r for r in records if r["record_type"] == "collection_ledger"]
    originals = [r for r in calls if _known(r["retry_of"]) is None and _known(r["supersedes"]) is None]
    artifacts = assessment.get("artifacts", ())
    audit = assessment.get("audit", {})
    invalidated = set(compilation.corrections.get("invalidated_record_ids", ()))
    extractions = [r for r in records if r["record_type"] == "extraction"]
    positions = [p for r in extractions for p in r["positions"]]
    stats = {"scope": "current_operational_records", "supplied_call_records": len(calls),
        "original_call_records": len(originals), "retry_call_records": sum(_known(r["retry_of"]) is not None for r in calls),
        "attempt_status_counts": dict(Counter(r["attempt_status"] for r in calls)),
        "known_response_references": sum(_known(r["raw_response_ref"]) is not None for r in originals),
        "acquired_original_responses": sum(bool(_known(r["raw_response_ref"]) and view.artifact(_known(r["raw_response_ref"])["record_id"])[1]) for r in originals),
        "supplied_original_planned_positions": sum(len(r["planned_positions"]) for r in originals),
        "registered_max_calls": _knowledge(registration["protocol"]["budget"]["max_calls"], scalar=True),
        "registered_max_positions": _knowledge(registration["protocol"]["budget"]["max_positions"], scalar=True),
        "qualification_coverage": {"numerator": sum(a["membership_admitted"] for a in artifacts), "denominator": len(artifacts),
            "denominator_scope": "supplied_qualifiable_artifact_records_before_correction_invalidation",
            "effective_current_numerator": sum(a["membership_admitted"] and a["artifact_id"] not in invalidated and a["judgment_id"] not in invalidated for a in artifacts),
            "invalidated_artifact_count": sum(a["artifact_id"] in invalidated for a in artifacts), "status": "available" if artifacts else "undefined",
            "assignment_status_counts": dict(Counter(a["assignment_status"] for a in artifacts)),
            "validity_status_counts": dict(Counter(a["validity_status"] for a in artifacts))},
        "fixed_audit_coverage": {"numerator": sum(r["review_record_complete"] for r in audit.get("fixed_positions", ())),
            "denominator": audit.get("planned_systematic_count"), "denominator_scope": "original_main_fixed_positions",
            "missing_opportunities": audit.get("missing_fixed_opportunities"), "status": "available" if audit else "unavailable"},
        "targeted_audit_coverage": {"numerator": sum(r["review_record_complete"] for r in audit.get("targets", ())),
            "denominator": audit.get("distinct_target_count"), "denominator_scope": "distinct_original_target_artifacts",
            "status": "available" if audit.get("distinct_target_count") else "undefined" if audit else "unavailable"}}
    stats["extractions"] = {"scope": "supplied_current_operational_extraction_records", "records": len(extractions),
        "declared_positions": len(positions), "selection_status_counts": dict(Counter(p["selection"] for p in positions)),
        "completion_status_counts": dict(Counter(p["completion_status"] for p in positions)),
        "selected_realizations": sum(p["selection"] == "selected" for p in positions),
        "linked_artifact_positions": sum(_known(p["artifact_ref"]) is not None for p in positions),
        "extras": sum(len(r["extras"]) for r in extractions),
        "compiled_selection_established": compilation.compiled,
        "sources": [{"extraction_ref": public_alias(r["record_id"]), "call_ref": public_alias(r["collection_ref"]["record_id"]),
            "positions": [{"within_group_index": p["within_group_index"], "selection": p["selection"],
                "completion_status": p["completion_status"], "artifact": _knowledge(p["artifact_ref"]),
                "byte_range": _knowledge(p["byte_range"], scalar=True)} for p in r["positions"]]} for r in extractions]}
    if registration["protocol"]["design"] == "sorting_abc":
        stats["registered_main_design"] = {"planned_calls": 72, "planned_positions": 360, "positions_per_cell": 20,
            "selected_realizations": collection.counts.get("selected_realizations"), "complete_groups": collection.counts.get("complete_groups"),
            "counts": dict(collection.counts), "restrictions": list(collection.restrictions), "pilot_included": False}
    else:
        # Fixed HERO obligations are visible only within their declared design.
        stats["fixed_audit_coverage"]["applicability"] = "outside_selected_operational_design"
        stats["targeted_audit_coverage"]["applicability"] = "outside_selected_operational_design"
    return {"operational": stats, "compiled_cells": _compiled_populations(compilation),
        "denominators_are_separate": True, "scientific_independence_established": False}


def _controls(fields):
    scalar_fields = {"temperature", "top_p", "presence_penalty", "frequency_penalty", "seed", "output_allowance",
        "fresh_context", "tools_requested", "includes_reasoning", "enforced", "previous_outputs_supplied",
        "reference_material_supplied", "output_selection", "automatic_retries", "duration_ms"}
    return {k: _knowledge(v, scalar=k in scalar_fields or isinstance(_known(v), bool)) for k, v in fields.items()}


def _call_controls(records, collection):
    slots = {s["primary_record_id"]: s for s in collection.slots if s["primary_record_id"]}
    rows = []
    for r in records:
        if r["record_type"] != "collection_ledger":
            continue
        slot = slots.get(r["record_id"], {})
        submission = slot.get("submission")
        rows.append({"call_ref": public_alias(r["record_id"]), "phase": r["phase"], "block_id": r["block_id"],
            "condition": r["condition"], "group_index": r["group_index"], "attempt_status": r["attempt_status"],
            "attempted_at": _knowledge(r["attempted_at"], timestamp=True),
            "authorization": _knowledge(r["authorization_ref"], required=True),
            "requested_controls": _controls(submission["requested_controls"]) if submission else {"state": "missing"},
            "actual_controls": _controls(r["controls"]),
            "enforced_controls": _controls(submission["enforced_controls"]) if submission else {"state": "missing"},
            "cap": _controls(submission["cap"]) if submission else {"state": "missing"},
            "context": _controls(submission["context"]) if submission else {"state": "missing"},
            "deployment": {k: _knowledge(v) for k, v in r["deployment"].items()},
            "original_response": _knowledge(r["raw_response_ref"]),
            "restriction_codes": list(slot.get("restrictions", ())), "external_enforcement_authenticated": False})
    return rows


def _spending(records, registration):
    calls = [r for r in records if r["record_type"] == "collection_ledger"]
    amounts = [_known(r["usage"]["monetary_cost"]) for r in calls]
    currencies = [_known(r["usage"]["currency"]) for r in calls]
    if calls and all(v is not None for v in amounts) and all(v is not None for v in currencies) and len(set(currencies)) == 1:
        numbers = [Decimal(v.token if isinstance(v, ExactNumber) else str(v)) for v in amounts]
        high = max((n.adjusted() for n in numbers if n), default=0)
        low = min(n.as_tuple().exponent for n in numbers)
        if max(abs(high), abs(low)) > 4096:
            total_cost = {"state": "unavailable", "reason_code": "exact_cost_total_exceeds_report_number_budget"}
        else:
            with localcontext() as context:
                context.prec = max(1, high - low + 1 + len(str(len(numbers))))
                total = sum(numbers, Decimal(0))
            total_cost = {"state": "known", "value": {"exact_decimal": str(total)}, "currency": _text(currencies[0])}
    else:
        total_cost = {"state": "unavailable", "reason_code": "no_assumed_currency_conversion_or_missing_cost_fill"}
    return {"scope": "all_current_call_records_including_retries_and_failures",
        "denominator": len(calls), "cost_knowledge_counts": dict(Counter(r["usage"]["monetary_cost"]["state"] for r in calls)),
        "monetary_ceiling": _knowledge(registration["protocol"]["budget"]["monetary_ceiling"], scalar=True),
        "currency": _knowledge(registration["protocol"]["budget"]["currency"]),
        "calls": [{"call_ref": public_alias(r["record_id"]), "attempt_status": r["attempt_status"],
            "monetary_cost": _knowledge(r["usage"]["monetary_cost"], scalar=True), "currency": _knowledge(r["usage"]["currency"]),
            "input_tokens": _knowledge(r["usage"]["input_tokens"], scalar=True),
            "output_tokens": _knowledge(r["usage"]["output_tokens"], scalar=True),
            "hidden_reasoning_tokens": _knowledge(r["usage"]["hidden_reasoning_tokens"], scalar=True),
            "compute": _knowledge(r["usage"]["compute"])} for r in calls],
        "total_cost": total_cost,
        "spending_authorized_by_report": False}


def _failure(compilation, diagnostics):
    tree = {"material_role": "unavailable", "evidence_status": "invalid_input", "claim_scope": {"state": "unavailable"},
        "study_identity": {"state": "unavailable"}, "analysis_bundle_created": False,
        "ec_disclosures": [{"id": key, "status": "unavailable", "reason_code": "input_rejected"} for key in DISCLOSURE_IDS],
        "diagnostics": [{"code": d.code, "severity": d.severity} for d in diagnostics],
        "empirical_claim_established": False, "substantive_validation_performed": False, "exit_code": 2}
    return StudyReadiness(freeze(tree), freeze({}), freeze({"compiled": False, "analysis_bundle_created": False,
        "disposition": "withheld", "exit_code": 2}), compilation, tuple(diagnostics))


def inspect_study(loaded: LoadedStudy, *, qualification_packet_id: str | None = None,
                  mapping_receipt_id: str | None = None) -> StudyReadiness:
    """Inspect the selected supplied evidence, with exact public join identities.

    Selection is explicit and never falls back to another packet. All computed
    counts are inventories/qualification results. Existing M/V/L numerical
    analysis and replay remain separate commands.
    """
    compilation = compile_study(loaded, qualification_packet_id=qualification_packet_id,
                                mapping_receipt_id=mapping_receipt_id)
    diagnostics = list(compilation.diagnostics)
    if isinstance(loaded, LoadedStudy):
        diagnostics.extend(loaded.diagnostics)
    try:
        view = _StudyView(loaded)
        superseded = {_known(r["supersedes"])["record_id"] for r in view.records.values() if _known(r["supersedes"])}
        records = [r for r in view.current if r["record_id"] not in superseded]
        registration = next(r for r in records if r["record_type"] == "study_registration")
        raw_qualification = _raw_qualification(view, qualification_packet_id)
        assessment = compilation.qualification
        collection = inspect_collection(loaded)
        if collection:
            diagnostics.extend(collection.diagnostics)
        provenance = {"privacy": {"mode": "opaque_identity_and_path_aliases", "raw_prose": "restricted_input",
            "hashes_prove_identity_only": True, "public_alias_method": "sha256_utf8_full_digest", "anonymity_claimed": False},
            "study_snapshot_sha256": _sha(_serialize(view.raw)), "study_ref": public_alias(view.raw["study_id"]),
            "study_version_ref": public_alias(view.raw["study_version"]),
            "records": [{"record_ref": public_alias(r["record_id"]), "record_type": r["record_type"],
                "record_version": r["record_version"], "study_version_ref": public_alias(r["study_version"]),
                "record_sha256": _sha(_serialize(r)), "current": r in records,
                "lineage_record_refs": [public_alias(x["record_id"]) for x in r["lineage_refs"]],
                "dependency_record_refs": [public_alias(x["record_id"]) for x in r["depends_on"]]}
                for r in view.raw["records"]],
            "packets": [{"packet_ref": public_alias(r.packet_id), "status": r.status,
                "actual_sha256": r.actual_sha256, "actual_size_bytes": r.actual_size_bytes} for r in loaded.attachments],
            "compilation": _public(compilation.provenance)}
        errors = any(d.severity == "error" for d in diagnostics)
        controls = registration["protocol"]["controls"]
        tree = {"material_role": view.raw["material_role"],
            "evidence_status": "fixture_only" if view.fixture or assessment.get("fixture_context") else "supplied_records_require_external_authentication",
            "claim_scope": {"statement": _text(registration["claim_scope"]), "requested_profile": registration["requested_profile"],
                "allowed_public_conclusion": "Passive record consistency, evidence gaps and label-conditioned inventories only.",
                "empirical_claim_established": False, "independent_validation_performed": False},
            "study_identity": {"study_ref": public_alias(view.raw["study_id"]), "study_version_ref": public_alias(view.raw["study_version"]),
                "pins": dict(registration["pins"]), "source_pins": dict(registration["source_pins"]),
                "protocol_ref": public_alias(registration["protocol"]["protocol_id"]),
                "protocol_version_ref": public_alias(registration["protocol"]["protocol_version"]), "evidence_policy": view.raw["evidence_policy"]},
            "acquisition": {"complete": loaded.acquisition_complete, "verified_packets": sum(r.status == "snapshot_verified" for r in loaded.attachments),
                "declared_packets": len(loaded.attachments), "total_read_bytes": loaded.total_read_bytes,
                "packet_status_counts": dict(Counter(r.status for r in loaded.attachments))},
            "compilation": {"eligible": compilation.compiled, "analysis_bundle_created": False, "analysis_performed": False,
                "output_file_count": len(compilation.files), "mapping_errors": _public(compilation.mapping_errors),
                "qualification_packet_ref": public_alias(qualification_packet_id) if qualification_packet_id else None,
                "mapping_receipt_ref": public_alias(mapping_receipt_id) if mapping_receipt_id else None,
                "selection_automatic": False, "broader_claims_restricted": True},
            "activity_readiness": _activities(records),
            "registered_controls": {k: _knowledge(v, scalar=k not in {"hidden_controls", "wrapper_knowledge", "cap_semantics"}) for k, v in controls.items()},
            "call_control_records": _call_controls(records, collection),
            "ec_disclosures": _disclosures(registration, records, assessment, compilation.corrections, raw_qualification, compilation.compiled),
            "five_condition_assessments": [{"claim_ref": public_alias(c["claim_id"]), "kind": c["kind"],
                "conditions": {name: _public(c.get("requirements", {}).get(name, {"outcome": "unresolved", "record_satisfied": False,
                    "restrictions": ["no_scoped_assessment_supplied"]})) for name in CONDITIONS},
                "operational_openness_established": False} for c in assessment.get("claims", ())],
            "populations_and_denominators": _denominators(view, records, assessment, compilation, registration, collection),
            "spending_knowledge": _spending(records, registration),
            "qualification": _public(assessment), "corrections": _public(compilation.corrections),
            "diagnostics": [{"code": d.code, "severity": d.severity} for d in diagnostics],
            "substantive_validation_performed": False, "exit_code": 2 if errors else 0, "report_version": "0.1"}
        tree["qualification"]["fixed_sorting_design_applicability"] = ("selected_operational_design"
            if registration["protocol"]["design"] == "sorting_abc" else "outside_selected_operational_design")
        manifest = _public(compilation.as_dict())
        manifest.update(analysis_bundle_created=False, analysis_performed=False)
        result = StudyReadiness(freeze(tree), freeze(provenance), freeze(manifest), compilation, tuple(diagnostics))
        outputs = (result.json_bytes, result.markdown_bytes, result.provenance_json_bytes, result.compilation_manifest_json_bytes)
        limits = compilation.limits
        if any(len(b) > limits.max_file_bytes for b in outputs) or sum(map(len, outputs)) > limits.max_bundle_bytes:
            raise InputError("study_report_output_budget_exceeded")
        return result
    except (InputError, KeyError, TypeError, ValueError, OSError, ArithmeticError, RecursionError, StopIteration) as exc:
        code = exc.code if isinstance(exc, InputError) else "invalid_study_reporting_context"
        diagnostics.append(Diagnostic(code, "study_reporting", "study_reporting"))
        return _failure(compilation, diagnostics)
