"""Scoped checks on supplied evidence records; never an independent judge.

No filesystem, network, model, program execution, population construction, or
metric calculation occurs here. Assertions retain their source and mock status.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from collections import defaultdict
import hashlib
import json
from itertools import combinations, product
from dataclasses import dataclass, field
from typing import Any, Mapping
from .contracts import (
    CLASS_IDS, EVIDENCE_POLICIES, INTEGRITY_CONDITIONS, RECORD_TYPES, DATA_ROLES, SUPPORT_RECORD_TYPES, Diagnostic, InputError,
    freeze, in_enum, is_id, knowledge, validate_ref,
)
from .records import RecordEntry, TypedRecord, text, ref, refs
from .local_io import LoadedBundle

# Step 3 elaborates support payloads separately from Step 2 envelope parsing.
# Unknown or incomplete payloads remain preserved in RecordEntry.raw.
SUPPORT_COMMON = {
    "payload_version": "version", "data_role": "data_role", "mock": "bool",
    "state": "state", "scope_refs": "refs", "origin": "tag",
    "knowledge_type": "tag", "transformation_refs": "refs", "evidence_refs": "refs",
}
SUPPORT_FIELDS = {
    "evidence": {"target_ref": "ref", "purpose": "purpose", "assertion": "tag",
                 "method": "tag", "detail": "tag", "artifact_refs": "refs",
                 "reviewer_refs": "refs", "subject_hash": "tag", "access": "access",
                 "conflict_status": "conflict"},
    "role": {"entity_id": "tag", "entity_type": "entity_type", "role": "text",
             "method": "tag", "qualification": "tag", "exposure_refs": "refs"},
    "lineage": {"subject_ref": "ref", "parent_ref": "tag", "relation": "text",
                "knowledge_state": "knowledge_state"},
    "independence_assessment": {"left_ref": "ref", "right_ref": "ref", "dimension": "text",
                               "outcome": "independence", "criterion": "tag", "reviewer_refs": "refs"},
    "annotation": {"target_ref": "ref", "annotator_ref": "ref", "aspect": "text",
                   "rubric_ref": "tag", "initial": "bool", "label_exposure": "tag",
                   "outcome": "tag", "set_id": "id"},
    "adjudication": {"target_ref": "ref", "decision_state": "decision", "outcome": "tag",
                     "reviewer_refs": "refs", "basis_refs": "refs", "disagreement_refs": "refs"},
    "domain_suite": {"suite_id": "id", "stage": "stage", "property": "text",
                     "planned_case_count": "tag", "reference_artifact_refs": "refs",
                     "environment": "tag", "oracle_origin": "tag"},
    "domain_result": {"target_ref": "ref", "suite_ref": "ref", "property": "text",
                      "outcome": "domain_outcome", "subject_hash": "tag",
                      "environment": "tag", "input_manifest": "tag", "observations": "tag"},
    "audit": {"stage": "stage", "planned_refs": "refs", "reviewed_refs": "refs",
              "sampling_plan_ref": "tag", "annotation_refs": "refs", "targeted_refs": "refs"},
    "exposure": {"subject_ref": "ref", "role_ref": "ref", "stage": "text",
                 "material_refs": "refs", "exposed": "tag"},
    "integrity_assessment": {"claim_kind": "claim_kind", "claim": "text",
                             "requirements": "object", "declared_disposition": "claim_disposition",
                             "reviewer_refs": "refs", "assessed_at": "tag", "current_until": "tag",
                             "reconsideration_triggers": "texts"},
    "intake": {"component": "component", "stage": "intake_stage", "original_refs": "refs",
               "proposed_change": "tag", "disposition": "tag", "reviewer_refs": "refs"},
    "tail": {"class_id": "tag", "designation": "tag", "basis": "tag",
             "reference_refs": "refs", "review_refs": "refs", "disposition": "tag"},
    "correction": {"target_refs": "refs", "effect": "effect", "action": "action",
                   "stage": "correction_stage", "replacement_refs": "refs", "reviewer_refs": "refs",
                   "event_type": "event_type", "prior_result_ids": "ids", "reason": "tag"},
    "preregistration": {"registration_id": "id", "registered_at": "tag", "material_refs": "refs"},
    "budget": {"planned": "tag", "actual": "tag"},
    "sampling_plan": {"planned_refs": "refs", "selection_rule": "tag", "registered_at": "tag"},
    "source": {"source_id": "id", "sha256": "tag", "locator": "tag"},
}
SUPPORT_ENUMS = {
    "data_role": DATA_ROLES,
    "state": {"active", "challenged", "withdrawn", "superseded", "unresolved"},
    "purpose": {"fixture_declaration", "mechanism", "validity", "schema", "independence", "observation", "reference"},
    "access": {"readable", "unavailable", "withheld", "unknown"},
    "conflict": {"none_declared", "resolved", "unresolved"},
    "entity_type": {"human", "model", "tool", "organization", "formal_system", "measurement", "unknown"},
    "knowledge_state": {"known", "unknown", "unavailable", "not_applicable"},
    "independence": {"supported_for_scope", "not_supported_for_scope", "unresolved"},
    "decision": {"resolved", "unresolved"},
    "stage": {"design", "performed", "incomplete", "not_performed"},
    "domain_outcome": {"passed", "failed", "timeout", "harness_error", "undetermined"},
    "claim_kind": {"label_conditioned", "validated_measurement", "operational_openness", "empirical_theory"},
    "claim_disposition": {"supported_for_scope", "restricted", "withheld"},
    "component": {"stable_core", "rotating_frontier", "external_incident", "tail_registry"},
    "intake_stage": {"empty", "received", "reviewed", "acted", "rejected", "unresolved"},
    "effect": {"membership", "validity", "independence", "schema", "registry", "metadata"},
    "action": {"challenge", "withdraw", "replace", "annotate"},
    "correction_stage": {"pending", "applied", "rejected"},
    "event_type": {"intake", "correction", "distributional_reopening_event", "structural_reopening_event"},
}

@dataclass(frozen=True)
class SupportRecord:
    record: TypedRecord
    payload: Mapping[str, Any] = field(repr=False)
    validation_level: str = "payload_shape_only"

@dataclass(frozen=True)
class SupportInspection:
    key: tuple[str, str]
    record: SupportRecord | None
    diagnostics: tuple[Diagnostic, ...]


def inspect_support(entry: RecordEntry) -> SupportInspection:
    """Validate typed payloads without validating their real-world assertions."""
    r = entry.record
    if r is None or r.record_type not in SUPPORT_RECORD_TYPES:
        return SupportInspection(("", ""), None, (Diagnostic("not_support_record", "record", "support"),))
    key = (r.record_type, r.record_id)
    p = r.data["payload"]
    requirements = SUPPORT_COMMON | SUPPORT_FIELDS[r.record_type]
    issues = []
    for name, spec in requirements.items():
        try:
            if name not in p:
                raise InputError("missing_support_field")
            value = p[name]
            if spec in SUPPORT_ENUMS:
                okay = in_enum(value, SUPPORT_ENUMS[spec])
            elif spec == "version": okay = value == "0.1"
            elif spec == "bool": okay = type(value) is bool
            elif spec == "text": okay = text(value)
            elif spec == "id": okay = is_id(value)
            elif spec == "ref": okay = ref(value)
            elif spec == "refs": okay = refs(value)
            elif spec in {"texts", "ids"}:
                okay = isinstance(value, (list, tuple)) and all((text if spec == "texts" else is_id)(v) for v in value)
            elif spec == "object": okay = isinstance(value, Mapping)
            elif spec == "tag": knowledge(value); okay = True
            else: okay = False
            if not okay: raise InputError("invalid_support_field")
        except InputError as exc:
            issues.append(Diagnostic(exc.code, "support", ":".join(key), name))
    if set(p) - requirements.keys() - {"extensions"}:
        issues.append(Diagnostic("unknown_support_field", "support", ":".join(key)))
    if "extensions" in p and not isinstance(p["extensions"], Mapping):
        issues.append(Diagnostic("invalid_extensions", "support", ":".join(key)))
    return SupportInspection(key, None if issues else SupportRecord(r, p), tuple(issues))


Key = tuple[str, str]
MECHANISM_METHODS = frozenset({"control_flow", "execution_trace", "formal_mechanism",
                              "counterfactual", "domain_adjudication"})
VALIDITY_METHODS = frozenset({"execution", "formal_validity", "domain_adjudication"})

@dataclass(frozen=True)
class Admission:
    axis: str
    sample_id: str
    record_id: str | None
    revision: str | None
    status: str
    outcome: str | None
    reasons: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()
    fixture_context: bool = False
    evidence_scope: str = "supplied_record_checks_only"
    independent_validation_performed: bool = False

@dataclass(frozen=True)
class GateCheck:
    record_id: str
    status: str
    reasons: tuple[str, ...]
    details: Mapping[str, Any] = field(default_factory=dict, repr=False)
    mock: bool = False
    substantive_validation_performed: bool = False

@dataclass(frozen=True)
class CorrectionImpact:
    correction_id: str
    target_keys: tuple[Key, ...]
    affected_record_ids: tuple[str, ...]
    claim_only: bool
    stage: str
    replacement_keys: tuple[Key, ...]
    numeric_reanalysis_performed: bool = False

@dataclass(frozen=True)
class EvidenceReview:
    admissions: tuple[Admission, ...]
    support_checks: tuple[GateCheck, ...]
    claim_checks: tuple[GateCheck, ...]
    corrections: tuple[CorrectionImpact, ...]
    preserved_revision_ids: tuple[Key, ...]
    input_acquisition_complete: bool
    fixture_context: bool
    independent_validation_performed: bool = False


def ref_key(value: Mapping[str, Any]) -> Key:
    validate_ref(value)
    return value["record_type"], value["record_id"]


def known(value: Any) -> Any:
    k = knowledge(value)
    return k.value if k.state == "known" else None


def nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def unique(items: list[str]) -> tuple[str, ...]:
    return tuple(sorted(set(items)))



FUNCTIONAL_PROPERTIES = ("fresh_plain_list", "plain_integers", "length_preserved", "nondecreasing", "multiplicity_preserved", "input_unchanged")
RUNTIME_STATES = {"completed", "timeout", "memory_limit", "exception", "prohibited_capability", "output_protocol_failure", "harness_error", "containment_failure", "oracle_error"}
WITNESS_INPUTS = ((7,1,6,2,5,3,4,0), (3,1,3,0,2,0,2,1), (256,1,4095,255,16,0,257,4094), (0,1,2,3,7,6,5,4))


def _json_hash(value: Any) -> str:
    """Canonical identity of manifest rows; not independent validation."""
    def thaw(v):
        if isinstance(v, Mapping): return {k:thaw(x) for k,x in v.items()}
        if isinstance(v,(list,tuple)): return [thaw(x) for x in v]
        return v
    return hashlib.sha256((json.dumps(thaw(value), ensure_ascii=True, sort_keys=True, separators=(",",":"), allow_nan=False)+"\n").encode()).hexdigest()


def _functional_inputs():
    """Expected construction for validating supplied manifest rows only (HERO 5.3)."""
    index = 0
    for size in range(5):
        for xs in product((0,1,255,256,4095), repeat=size):
            index += 1; yield f"V-SMALL-{index:04d}", "V-SMALL", xs
    index = 0
    boundaries = (255,256,4095,0,257,1,4094,16)
    for size in (8,64,256):
        patterns = (tuple(range(size)), tuple(range(size-1,-1,-1)),
                    tuple(4095*(i%2) for i in range(size)), (256,)*size,
                    tuple((73*i+19)%4096 for i in range(size)), tuple(boundaries[i%8] for i in range(size)))
        for xs in patterns:
            index += 1; yield f"V-SHAPE-{index:02d}", "V-SHAPE", xs
    for x in range(4096):
        yield f"V-KEY-{2*x+1:04d}", "V-KEY", (x,)
        yield f"V-KEY-{2*x+2:04d}", "V-KEY", (4095-x,x)
    for i,xs in enumerate(WITNESS_INPUTS,1): yield f"V-STAGE-{i:02d}", "V-STAGE", xs


class EvidenceIndex:
    """Preserve all input entries while exposing only unambiguous references."""
    def __init__(self, bundle: LoadedBundle) -> None:
        self.bundle = bundle
        self.entries: dict[Key, list[RecordEntry]] = defaultdict(list)
        self.support: dict[Key, SupportRecord] = {}
        self.support_checks: list[GateCheck] = []
        self.file_errors = {d.source for d in bundle.diagnostics
                            if d.scope == "file" and d.severity == "error"}
        self.sample_hash_errors = {d.source for d in bundle.diagnostics
                                  if d.code == "sample_content_hash_mismatch"}
        for entry in bundle.records:
            raw = entry.raw
            if isinstance(raw, Mapping) and isinstance(raw.get("record_type"), str) and raw["record_type"] in RECORD_TYPES and is_id(raw.get("record_id")):
                self.entries[(raw["record_type"], raw["record_id"])].append(entry)
        for key, items in sorted(self.entries.items()):
            if len(items) != 1 or items[0].record is None:
                continue
            r = items[0].record
            if r.validation_level == "envelope_only":
                check = inspect_support(items[0])
                if check.record is not None and items[0].source not in self.file_errors:
                    self.support[key] = check.record
                self.support_checks.append(GateCheck(r.record_id,
                    "payload_consistent" if key in self.support else "payload_unresolved",
                    tuple(d.code for d in check.diagnostics) + (("source_file_error",) if items[0].source in self.file_errors else ()),
                    freeze({"record_type": r.record_type, "level": "shape_only"}),
                    bool(check.record and check.record.payload["mock"])))
        self.correctors = {k: s for k, s in self.support.items() if k[0] == "correction"}
        self.correction_targets: dict[Key, list[tuple[str, Mapping[str, Any]]]] = defaultdict(list)
        for (_, cid), support in self.correctors.items():
            for value in support.payload["target_refs"]:
                self.correction_targets[ref_key(value)].append((cid, support.payload))
        self.successors: dict[Key, list[TypedRecord]] = defaultdict(list)
        for key in self.entries:
            record = self.get(key)
            if key[0] in {"assignment", "validity"} and record:
                previous = known(record.data["supersedes_" + key[0] + "_id"])
                if previous is not None:
                    self.successors[(key[0], previous)].append(record)

    def get(self, key: Key) -> TypedRecord | None:
        entries = self.entries.get(key, ())
        if len(entries) != 1 or entries[0].source in self.file_errors:
            return None
        return entries[0].record

    def resolve(self, value: Mapping[str, Any]) -> TypedRecord | None:
        return self.get(ref_key(value))

    def payload(self, key: Key) -> Mapping[str, Any] | None:
        s = self.support.get(key)
        return s.payload if s else None

    def links_exist(self, values: Any, kinds: set[str] | None = None) -> bool:
        if not isinstance(values, (list, tuple)):
            return False
        try:
            return all(self.resolve(v) is not None and (kinds is None or v["record_type"] in kinds)
                       for v in values)
        except InputError:
            return False

    def role_present(self, refs: Any) -> bool:
        return bool(refs) and self.links_exist(refs, {"role"}) and all(
            ref_key(v) in self.support and self.support[ref_key(v)].payload["state"] == "active" for v in refs)

    def correction_sound(self, p: Mapping[str, Any]) -> bool:
        return (p["state"] == "active" and bool(p["target_refs"])
                and self.role_present(p["reviewer_refs"])
                and bool(p["evidence_refs"]) and self.links_exist(p["evidence_refs"])
                and nonblank(known(p["reason"]))
                and (p["action"] != "replace" or (bool(p["replacement_refs"]) and self.links_exist(p["replacement_refs"]))))

    def affected(self, key: Key, effects: set[str]) -> tuple[str, ...]:
        found = []
        for cid, p in self.correction_targets.get(key, ()):
            if p["stage"] == "rejected" or p["effect"] not in effects:
                continue
            if key not in {ref_key(x) for x in p["target_refs"]}:
                continue
            if p["action"] == "annotate":
                continue
            # A claimed essential challenge with unresolved supporting records
            # cannot silently disappear; it remains a scoped review requirement.
            found.append(("correction_pending:" if p["stage"] == "pending" or not self.correction_sound(p)
                          else "correction_applied:") + cid)
        return tuple(sorted(found))

    def frame_for(self, sample: TypedRecord) -> TypedRecord | None:
        cell = self.get(("cell", sample.data["analysis_cell_id"]))
        return self.get(("frame", cell.data["frame_id"])) if cell else None

    def evidence_ok(self, key: Key, target: Key, frame: Key, outcome: str,
                    policy: str, purpose: str) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
        """Check the claimed basis and its links; never read rationale as proof."""
        problems: list[str] = []
        restrictions: list[str] = []
        p = self.payload(key)
        if key[0] != "evidence" or p is None:
            return False, ("essential_evidence_unresolved",), ()
        if p["target_ref"] is None or ref_key(p["target_ref"]) != target:
            problems.append("evidence_target_mismatch")
        if frame not in {ref_key(x) for x in p["scope_refs"]}:
            problems.append("evidence_frame_mismatch")
        if p["purpose"] != purpose:
            problems.append("evidence_property_mismatch")
        if p["state"] != "active" or p["access"] != "readable":
            problems.append("essential_evidence_not_active_or_readable")
        if p["conflict_status"] == "unresolved": problems.append("evidence_contradiction")
        if known(p["assertion"]) != outcome: problems.append("evidence_assertion_mismatch")
        if not nonblank(known(p["detail"])): problems.append("missing_evidence_detail")
        problems.extend(self.affected(key, {"membership", "validity", "schema"}))
        if policy == "fixture_only":
            if p["data_role"] != "fixture": problems.append("fixture_evidence_role_mismatch")
        else:
            if p["data_role"] == "fixture" or p["mock"]: problems.append("fixture_in_import_evidence")
            methods = MECHANISM_METHODS if purpose == "mechanism" else VALIDITY_METHODS
            if not in_enum(known(p["method"]), methods): problems.append("inappropriate_validation_method")
            if not self.role_present(p["reviewer_refs"]): problems.append("reviewer_record_unresolved")
        if known(p["origin"]) is None: restrictions.append("origin_unknown")
        if known(p["knowledge_type"]) is None: restrictions.append("knowledge_type_unknown")
        for value in p["artifact_refs"]:
            art = self.resolve(value)
            problems.extend(self.affected(ref_key(value), {"membership", "validity", "schema"}))
            snapshots = [x for x in self.bundle.artifacts if x.record_key == ":".join(ref_key(value))]
            if art is None or len(snapshots) != 1 or snapshots[0].status != "snapshot_read":
                problems.append("essential_artifact_unreadable_or_mismatched")
        if policy == "adjudicated_import" and in_enum(known(p["method"]), {"execution", "execution_trace"}):
            results = [ref_key(v) for v in p["evidence_refs"] if v["record_type"] == "domain_result"]
            assessment = self.get(target)
            subject = ("realization", assessment.data["sample_id"]) if assessment else None
            if not results: problems.append("missing_execution_record")
            for result_key in results:
                result = self.payload(result_key)
                gate = self.domain_check(result_key)
                if result is None:
                    problems.append("execution_record_unresolved"); continue
                if gate.status != "record_consistent":
                    problems.append("execution_record_unresolved")
                if gate.mock:
                    problems.append("fixture_in_import_execution")
                if ref_key(result["target_ref"]) != subject:
                    problems.append("execution_subject_mismatch")
                if result["property"] != ("mechanism" if purpose == "mechanism" else "sorting_behavior"):
                    problems.append("execution_property_mismatch")
                if purpose == "validity" and outcome in {"valid", "invalid"}:
                    expected = "passed" if outcome == "valid" else "failed"
                    if result["outcome"] != expected: problems.append("execution_outcome_mismatch")
        # Walk only evidence-support edges. Lineage/correction relationships have
        # different meanings and are deliberately NOT forced into a global DAG.
        stack: list[tuple[Key, bool]] = [(key, False)]
        active, complete = set(), set()
        while stack:
            current, exit_node = stack.pop()
            if exit_node:
                active.discard(current); complete.add(current); continue
            if current in active:
                problems.append("circular_evidence_support"); continue
            if current in complete: continue
            q = self.payload(current)
            if q is None:
                problems.append("essential_evidence_unresolved"); continue
            active.add(current); stack.append((current, True))
            if q["state"] != "active": problems.append("upstream_evidence_not_active")
            if q["access"] != "readable" or q["conflict_status"] == "unresolved":
                problems.append("upstream_evidence_unreadable_or_conflicted")
            if policy == "adjudicated_import" and (q["mock"] or q["data_role"] == "fixture"):
                problems.append("fixture_in_import_evidence")
            problems.extend(self.affected(current, {"membership", "validity", "schema"}))
            for value in q["evidence_refs"]:
                child = ref_key(value)
                if child[0] == "evidence": stack.append((child, False))
                elif self.resolve(value) is None: problems.append("essential_reference_missing")
        return not problems, unique(problems), unique(restrictions)

    def admit(self, axis: str, sample_id: str) -> Admission:
        if axis not in {"assignment", "validity"}: raise InputError("unsupported_admission_axis")
        m = self.bundle.manifest
        fixture_context = bool(m and m.data["data_role"] == "fixture")
        rid = revision = None
        def answer(status: str, outcome: str | None = None, reasons: tuple[str, ...] = (),
                   restrictions: tuple[str, ...] = ()) -> Admission:
            return Admission(axis, sample_id, rid, revision, status, outcome, reasons,
                             restrictions, fixture_context)
        if m is None or any(x.scope == "analysis_config" for x in m.diagnostics):
            return answer("withheld", reasons=("analysis_configuration_unavailable",))
        policy = m.data["analysis_config"]["assignment_evidence_policy_id"]
        sample = self.get(("realization", sample_id))
        if sample is None: return answer("withheld", reasons=("sample_identity_unresolved",))
        frame = self.frame_for(sample)
        if frame is None: return answer("withheld", reasons=("essential_frame_unresolved",))
        fkey = ("frame", frame.record_id)
        pins = [x for x in m.data["analysis_config"][axis + "_pins"] if x["sample_id"] == sample_id]
        if len(pins) != 1:
            return answer("conflict" if pins else "missing", reasons=("revision_pin_not_unique" if pins else "revision_not_pinned",))
        pin = pins[0]; rid = pin[axis + "_id"]; revision = pin[axis + "_version"]
        r = self.get((axis, rid))
        if r is None: return answer("withheld", reasons=("selected_revision_unresolved",))
        d = r.data
        if d["sample_id"] != sample_id or d[axis + "_version"] != revision:
            return answer("withheld", reasons=("selected_revision_mismatch",))
        if axis == "assignment" and d["frame_id"] != frame.record_id:
            return answer("withheld", reasons=("assignment_frame_mismatch",))
        if axis == "validity" and known(d["validity_rubric_ref"]) != frame.data["validity_rubric_ref"]:
            return answer("withheld", reasons=("validity_rubric_mismatch",))
        frame_effects = {"schema", "registry", "membership"} if axis == "assignment" else {"validity"}
        if self.affected(fkey, frame_effects):
            return answer("withheld", reasons=("shared_frame_challenged",))
        subject_changes = self.affected(("realization", sample_id), {"membership" if axis == "assignment" else "validity"})
        if subject_changes: return answer("withheld", reasons=subject_changes)
        changes = self.affected((axis, rid), {"membership" if axis == "assignment" else "validity"})
        if changes: return answer("withheld", reasons=changes)
        history = set(); current = r
        while current is not None:
            if current.record_id in history:
                return answer("withheld", reasons=("cyclic_revision_history",))
            history.add(current.record_id)
            predecessor = known(current.data["supersedes_" + axis + "_id"])
            if predecessor is None: break
            current = self.get((axis, predecessor))
            if current is None or current.data["sample_id"] != sample_id:
                return answer("withheld", reasons=("revision_history_unresolved",))
        for other in self.successors.get((axis, rid), ()):
            if other.data["sample_id"] != sample_id:
                return answer("withheld", reasons=("cross_sample_supersession",))
            return answer("withheld", reasons=("selected_revision_superseded",))
        review = d["assignment_review_status" if axis == "assignment" else "validity_review_status"]
        state = d["assignment_status" if axis == "assignment" else "validity_status"]
        if axis == "assignment" and state in {"unresolved", "unclassified"}:
            return answer(state, reasons=("no_committed_class",))
        if axis == "validity" and state == "not_assessed":
            return answer("not_assessed", reasons=("no_validity_assessment",))
        if review == "provisional": return answer("withheld", reasons=("provisional_judgment",))
        if review != ("fixture" if policy == "fixture_only" else "adjudicated"):
            return answer("withheld", reasons=("review_policy_mismatch",))
        if policy == "fixture_only" and not fixture_context:
            return answer("withheld", reasons=("fixture_policy_requires_fixture_context",))
        if axis == "assignment" and (d["assignment_evidence_policy_id"] != policy or d["assignment_evidence_policy_version"] != "0.1"):
            return answer("withheld", reasons=("assignment_policy_mismatch",))
        outcome = d["structural_class_id"] if axis == "assignment" else state
        if axis == "assignment" and outcome not in CLASS_IDS:
            return answer("withheld", reasons=("class_outside_pinned_schema",))
        if ":".join(("realization",sample_id)) in self.sample_hash_errors:
            return answer("withheld", reasons=("sample_artifact_identity_mismatch",))
        target = (axis, rid)
        purpose = "fixture_declaration" if policy == "fixture_only" else "mechanism" if axis == "assignment" else "validity"
        problems, restrictions = [], []
        if not nonblank(known(d["decision_rationale"])): problems.append("missing_decision_rationale")
        basis, decisions = [], []
        for value in d["evidence_refs"]:
            key = ref_key(value)
            if key[0] == "independence_assessment":
                p = self.payload(key)
                if p is None or p["outcome"] != "supported_for_scope" or self.affected(key, {"independence"}):
                    restrictions.append("independence_not_established")
            elif key[0] == "adjudication": decisions.append(key)
            elif key[0] == "evidence": basis.append(key)
            else: problems.append("unsupported_decisive_record_type")
        if not basis: problems.append("missing_essential_evidence")
        for key in basis:
            _, errors, limits = self.evidence_ok(key, target, fkey, outcome, policy, purpose)
            problems.extend(errors); restrictions.extend(limits)
            p = self.payload(key)
            if p:
                original_hash = known(sample.data["output_content_hash"])
                claimed_hash = known(p["subject_hash"])
                if original_hash is not None and claimed_hash is not None and original_hash != claimed_hash:
                    problems.append("evidence_subject_hash_mismatch")
        if policy == "adjudicated_import":
            restrictions.append("independent_measurement_not_certified_by_software")
            if not decisions: problems.append("missing_adjudication_record")
            for key in decisions:
                p = self.payload(key)
                if p is None:
                    problems.append("adjudication_record_unresolved"); continue
                if (p["state"] != "active" or p["decision_state"] != "resolved"
                    or p["mock"] or p["data_role"] == "fixture"
                    or ref_key(p["target_ref"]) != target or known(p["outcome"]) != outcome
                    or fkey not in {ref_key(x) for x in p["scope_refs"]}):
                    problems.append("adjudication_conflict")
                if not self.role_present(p["reviewer_refs"]): problems.append("adjudicator_unresolved")
                if not p["basis_refs"] or not self.links_exist(p["basis_refs"], {"evidence"}):
                    problems.append("adjudication_basis_unresolved")
                for value in p["basis_refs"]:
                    _, errors, limits = self.evidence_ok(ref_key(value), target, fkey, outcome, policy, purpose)
                    problems.extend(errors); restrictions.extend(limits)
                if not self.links_exist(p["disagreement_refs"]): problems.append("disagreement_unresolved")
                problems.extend(self.affected(key, {"membership", "validity"}))
        # Independent-claim withdrawals never erase separately supported labels.
        for (_, cid), s in self.correctors.items():
            if s.payload["effect"] == "independence" and s.payload["stage"] != "rejected":
                targets = {ref_key(v) for v in s.payload["target_refs"]}
                if target in targets or fkey in targets or any(ref_key(v) in targets for v in d["evidence_refs"]):
                    restrictions.append("independence_correction:" + cid)
        return answer("withheld" if problems else "accepted", None if problems else outcome,
                      unique(problems), unique(restrictions))

    def core_annotations(self, annotation_refs: Any) -> GateCheck:
        errors, actors = [], set()
        common = set(); mocks = False; initial_outcomes = []
        if not isinstance(annotation_refs, (list, tuple)):
            return GateCheck("core_annotations", "unresolved", ("invalid_annotation_list",))
        if not self.links_exist(annotation_refs, {"annotation"}): errors.append("annotation_reference_unresolved")
        for value in annotation_refs:
            try:
                key = ref_key(value)
            except InputError:
                errors.append("annotation_reference_unresolved"); continue
            p = self.payload(key) if key[0] == "annotation" else None
            if p is None:
                errors.append("annotation_payload_unresolved"); continue
            mocks |= p["mock"] or p["data_role"] == "fixture"
            if self.resolve(p["target_ref"]) is None: errors.append("annotation_target_unresolved")
            initial_outcomes.append(p["outcome"])
            role_key = ref_key(p["annotator_ref"])
            role = self.payload(role_key) if role_key[0] == "role" else None
            if role is None or role["entity_type"] != "human" or not nonblank(known(role["entity_id"])):
                errors.append("human_identity_unresolved"); continue
            mocks |= role["mock"] or role["data_role"] == "fixture"
            if (p["state"] != "active" or role["state"] != "active" or not p["initial"]
                    or known(p["label_exposure"]) is not False):
                errors.append("initial_judgment_exposed_or_unresolved"); continue
            if not nonblank(known(role["qualification"])): errors.append("qualification_record_missing")
            # Any explicitly recorded prior label exposure remains operative.
            for er in role["exposure_refs"]:
                ek = ref_key(er)
                ep = self.payload(ek) if ek[0] == "exposure" else None
                if ep is None or (ep["stage"] != "after_initial" and known(ep["exposed"]) is not False):
                    errors.append("role_exposure_not_cleared")
            actors.add(known(role["entity_id"]))
            rubric = known(p["rubric_ref"])
            if not nonblank(rubric):
                errors.append("annotation_rubric_unresolved"); rubric = None
            common.add((ref_key(p["target_ref"]), p["aspect"], rubric, p["set_id"]))
        if len(actors) < 2: errors.append("fewer_than_two_independent_human_identities")
        if len(common) != 1: errors.append("annotation_target_or_rubric_mismatch")
        return GateCheck("core_annotations", "record_consistent" if not errors else "unresolved",
                         unique(errors), freeze({"distinct_declared_people": len(actors),
                         "initial_outcomes": initial_outcomes,
                         "agreement_estimated": False, "validation_scope": "record_consistency_only"}), mocks)

    def functional_manifest_check(self, key: Key) -> GateCheck:
        """Inspect the supplied HERO manifest, without executing its candidates."""
        p = self.payload(key)
        if p is None or key[0] != "domain_suite":
            return GateCheck(key[1], "unresolved", ("domain_suite_unresolved",))
        data = p.get("extensions", {}).get("functional_manifest")
        errors, counts = [], defaultdict(int)
        tests = data.get("tests") if isinstance(data, Mapping) else None
        exact = isinstance(tests, (tuple, list)) and len(tests) == 8995
        if not isinstance(data, Mapping) or data.get("version") != "0.1":
            errors.append("functional_manifest_not_supplied_or_versioned")
        if not exact:
            errors.append("functional_manifest_count_mismatch")
        expected = _functional_inputs()
        if isinstance(tests, (tuple, list)) and len(tests) <= 8995:
            for row, (identity, segment, values) in zip(tests, expected):
                if not isinstance(row, Mapping):
                    errors.append("functional_manifest_entry_malformed"); continue
                if row.get("test_id") != identity or row.get("segment") != segment:
                    errors.append("functional_manifest_identity_or_order_mismatch")
                xs = row.get("input")
                if (not isinstance(xs, (tuple, list)) or any(type(x) is not int for x in xs)
                        or tuple(xs) != tuple(values)):
                    errors.append("functional_manifest_construction_mismatch")
                counts[segment] += 1
        else:
            errors.append("functional_manifest_not_bounded_list")
        try:
            actual_hash = _json_hash(tests) if isinstance(tests, (list, tuple)) and len(tests) <= 8995 else None
        except (TypeError, ValueError, OverflowError):
            actual_hash = None
            errors.append("functional_manifest_not_canonical_json")
        if not isinstance(data, Mapping) or data.get("sha256") != actual_hash or actual_hash is None:
            errors.append("functional_manifest_hash_mismatch")
        return GateCheck(key[1], "record_consistent" if not errors else "unresolved", unique(errors),
            freeze({"manifest_sha256": actual_hash, "received_count": len(tests) if isinstance(tests, (tuple,list)) else None,
                    "required_count": 8995, "segment_counts": dict(counts), "complete_ordered_manifest": not errors,
                    "execution_performed_by_toolkit": False}), p["mock"] or p["data_role"] == "fixture")

    def domain_check(self, key: Key) -> GateCheck:
        p = self.payload(key); errors = []
        if p is None or key[0] != "domain_result":
            return GateCheck(key[1], "unresolved", ("domain_record_unresolved",))
        skey = ref_key(p["suite_ref"])
        suite = self.payload(skey) if skey[0] == "domain_suite" else None
        if suite is None or suite["stage"] != "performed" or suite["state"] != "active":
            errors.append("domain_suite_not_performed")
        if suite and suite["property"] != p["property"]: errors.append("domain_property_mismatch")
        if p["state"] != "active": errors.append("domain_evidence_not_active")
        if p["outcome"] in {"timeout", "harness_error", "undetermined"}: errors.append("no_domain_validity_conclusion")
        for name in ("environment", "input_manifest", "observations"):
            if known(p[name]) is None: errors.append("domain_" + name + "_unresolved")
        target = self.resolve(p["target_ref"])
        if target is None: errors.append("domain_target_unresolved")
        elif target.record_type == "realization":
            actual = known(target.data["output_content_hash"]); asserted = known(p["subject_hash"])
            if actual is not None and asserted is not None and actual != asserted:
                errors.append("domain_subject_hash_mismatch")
        details = {"outcome": p["outcome"], "property": p["property"], "execution_performed_by_toolkit": False}
        if p["property"] == "sorting_behavior":
            gate = self.functional_manifest_check(skey)
            env, observations = known(p["environment"]), known(p["observations"])
            if not isinstance(env, Mapping): env = {}
            if not isinstance(observations, Mapping): observations = {}
            tests = observations.get("tested_ids")
            ids = tuple(identity for identity, _, _ in _functional_inputs())
            test_list_ok = (isinstance(tests, (list,tuple)) and all(is_id(x) for x in tests)
                           and len(tests) == len(set(tests)) and set(tests) <= set(ids))
            complete = test_list_ok and set(tests) == set(ids)
            if not test_list_ok: errors.append("functional_result_test_ids_unresolved")
            if known(p["input_manifest"]) != gate.details.get("manifest_sha256") or gate.status != "record_consistent":
                errors.append("functional_result_manifest_unresolved")
            actual_hash = known(target.data["output_content_hash"]) if target and target.record_type == "realization" else None
            if not isinstance(actual_hash, str) or len(actual_hash) != 64 or known(p["subject_hash"]) != actual_hash:
                errors.append("functional_result_artifact_identity_unresolved")
            runtime = observations.get("runtime_status")
            if not in_enum(runtime, {"completed", "exception", "prohibited_capability", "output_protocol_failure"}):
                errors.append("runtime_not_decisive")
            if env.get("containment_status") != "passed": errors.append("containment_not_established")
            if not self.role_present(env.get("oracle_reviewer_refs", [])): errors.append("oracle_review_not_supplied")
            family_set = env.get("accommodated_class_ids")
            envelope_ok = (isinstance(family_set, (list, tuple)) and all(is_id(x) for x in family_set)
                           and set(family_set) == set(CLASS_IDS))
            if not envelope_ok: errors.append("reference_envelope_coverage_unresolved")
            property_checks = observations.get("property_checks", {})
            if p["outcome"] == "passed":
                if not complete: errors.append("functional_suite_coverage_incomplete")
                if runtime != "completed": errors.append("passing_runtime_not_completed")
                if (not isinstance(property_checks, Mapping) or set(property_checks) != set(FUNCTIONAL_PROPERTIES)
                        or not all(v is True for v in property_checks.values())):
                    errors.append("functional_properties_not_established")
            elif p["outcome"] == "failed":
                ce = observations.get("counterexample")
                if (not isinstance(ce, Mapping) or ce.get("test_id") not in (tests if test_list_ok else ())
                        or not in_enum(ce.get("property"), FUNCTIONAL_PROPERTIES + ("syntax", "prohibited_capability", "exception", "output_protocol"))
                        or ce.get("observed_violation") is not True
                        or ce.get("subject_hash") != actual_hash
                        or not ce.get("evidence_refs") or not self.links_exist(ce.get("evidence_refs"))):
                    errors.append("decisive_counterexample_not_supplied")
            details.update({"complete_suite_coverage": bool(complete), "tested_count": len(tests) if test_list_ok else None,
                            "required_count": 8995, "manifest_record_status": gate.status,
                            "runtime_status": runtime if isinstance(runtime,str) and runtime in RUNTIME_STATES else "unknown",
                            "containment_record_status": env.get("containment_status") if in_enum(env.get("containment_status"), {"passed","failed","unknown"}) else "unknown",
                            "oracle_record_present": self.role_present(env.get("oracle_reviewer_refs", [])),
                            "reference_envelope_complete": envelope_ok, "finite_suite_is_all_input_proof": False})
        errors.extend(self.affected(key, {"validity", "membership"}))
        errors.extend(self.affected(skey, {"validity", "membership"}))
        return GateCheck(key[1], "record_consistent" if not errors else "unresolved", unique(errors),
                         freeze(details), p["mock"] or p["data_role"] == "fixture"
                         or bool(suite and (suite["mock"] or suite["data_role"] == "fixture")))

    def audit_check(self, key: Key) -> GateCheck:
        p = self.payload(key)
        if p is None or key[0] != "audit": return GateCheck(key[1], "unresolved", ("audit_record_unresolved",))
        planned = {ref_key(v) for v in p["planned_refs"]}
        reviewed = {ref_key(v) for v in p["reviewed_refs"]}
        missing = sorted(planned - reviewed); extra = sorted(reviewed - planned)
        errors = []
        if p["stage"] != "performed" or p["state"] != "active": errors.append("audit_not_performed")
        if missing: errors.append("planned_audit_items_missing")
        if not planned: errors.append("audit_plan_empty")
        if not self.links_exist(p["reviewed_refs"]): errors.append("reviewed_item_unresolved")
        plan_ref = known(p["sampling_plan_ref"])
        if not self.links_exist([plan_ref], {"sampling_plan"}):
            errors.append("audit_sampling_plan_unresolved")
        elif self.payload(ref_key(plan_ref)) is None:
            errors.append("audit_sampling_plan_unresolved")
        else:
            plan = self.payload(ref_key(plan_ref))
            if {ref_key(v) for v in plan["planned_refs"]} != planned:
                errors.append("audit_plan_membership_mismatch")
            if plan["state"] != "active": errors.append("audit_plan_inactive")
            if "hero_audit_positions" in plan.get("extensions", {}):
                errors.extend(self.hero_audit_check(ref_key(plan_ref)).reasons)
        if not p["annotation_refs"] or not self.links_exist(p["annotation_refs"], {"annotation"}):
            errors.append("audit_annotations_unresolved")
        covered = set()
        for value in p["annotation_refs"]:
            a = self.payload(ref_key(value)) if value["record_type"] == "annotation" else None
            if a is None or a["state"] != "active":
                errors.append("audit_annotations_unresolved"); continue
            target = ref_key(a["target_ref"])
            if target not in reviewed: errors.append("audit_annotation_target_mismatch")
            covered.add(target)
        if reviewed - covered: errors.append("reviewed_items_lack_annotation_records")
        return GateCheck(key[1], "record_consistent" if not errors else "unresolved", unique(errors),
                         freeze({"missing_planned": missing, "extra_reviews": extra,
                         "known_empty_plan": not planned, "model_samples_added": 0}),
                         p["mock"] or p["data_role"] == "fixture"
                         or any(self.payload(ref_key(x)) and (self.payload(ref_key(x))["mock"]
                                or self.payload(ref_key(x))["data_role"] == "fixture") for x in p["annotation_refs"]))

    def reference_check(self, key: Key) -> GateCheck:
        """Check supplied descriptor/witness/core coverage. No schema judgment."""
        p = self.payload(key)
        data = p.get("extensions", {}).get("reference_review") if p else None
        if not isinstance(data, Mapping): return GateCheck(key[1], "unresolved", ("reference_review_missing",))
        errors = []
        pairs = data.get("descriptor_pairs", ())
        found, overlaps = set(), []
        if not isinstance(pairs, (tuple,list)) or len(pairs)>28:
            errors.append("descriptor_pairs_malformed"); pairs=()
        for item in pairs:
            cs = item.get("classes") if isinstance(item,Mapping) else None
            if (not isinstance(cs,(tuple,list)) or len(cs)!=2 or any(not in_enum(c,CLASS_IDS) for c in cs) or cs[0]==cs[1]):
                errors.append("descriptor_pair_invalid"); continue
            pair=tuple(sorted(cs))
            if pair in found: errors.append("descriptor_pair_duplicate")
            found.add(pair)
            if item.get("outcome") != "distinct" or not item.get("evidence_refs") or not self.links_exist(item.get("evidence_refs")):
                overlaps.append(pair)
        if found != set(combinations(sorted(CLASS_IDS),2)): errors.append("descriptor_pair_coverage_incomplete")
        if overlaps: errors.append("unresolved_descriptor_overlap")
        witnesses=data.get("witnesses")
        if (not isinstance(witnesses,Mapping) or set(witnesses)!={f"W-{i:02d}" for i in range(1,5)}
                or any(not isinstance(witnesses.get(f"W-{i:02d}"),(list,tuple)) or tuple(witnesses[f"W-{i:02d}"])!=v
                       or any(type(x) is not int for x in witnesses[f"W-{i:02d}"]) for i,v in enumerate(WITNESS_INPUTS,1))):
            errors.append("witness_construction_mismatch")
        roles=data.get("core_roles",()); expected={f"CORE-{c[5:]}-{v}" for c in CLASS_IDS for v in ("A","B","D")}|{f"CORE-X{i:02d}" for i in range(1,9)}
        seen=set(); artifact_ids=set(); mock=bool(p and (p["mock"] or p["data_role"]=="fixture"))
        if not isinstance(roles,(tuple,list)) or len(roles)>32:
            errors.append("core_roles_malformed");roles=()
        for item in roles:
            if not isinstance(item,Mapping) or not is_id(item.get("role_id")):
                errors.append("core_role_invalid");continue
            role=item["role_id"]
            if role in seen: errors.append("core_role_duplicate")
            seen.add(role)
            if not self.links_exist([item.get("artifact_ref")], {"artifact","realization"}): errors.append("core_artifact_unresolved")
            else:
                artifact_key=ref_key(item["artifact_ref"])
                if artifact_key in artifact_ids: errors.append("duplicate_core_artifact")
                artifact_ids.add(artifact_key)
            for axis in ("assignment_annotations", "validity_annotations"):
                annotations=item.get(axis,());gate=self.core_annotations(annotations)
                mock |= gate.mock
                if gate.status!="record_consistent": errors.append("core_independent_annotations_incomplete")
                for ar in annotations if isinstance(annotations,(list,tuple)) else ():
                    if self.links_exist([ar], {"annotation"}):
                        ap=self.payload(ref_key(ar))
                        if ap and ap["target_ref"]!=item.get("artifact_ref"): errors.append("core_annotation_target_mismatch")
                        if ap and ap["aspect"] != ("mechanism" if axis=="assignment_annotations" else "validity"):
                            errors.append("core_annotation_property_mismatch")
            if role in expected and role.endswith(("-A","-B")):
                ws=item.get("witness_ids",())
                if not isinstance(ws,(list,tuple)) or any(not in_enum(x,{"W-01","W-02","W-03","W-04"}) for x in ws) or len(set(ws))<2:
                    errors.append("core_mechanism_witnesses_incomplete")
        if seen!=expected:errors.append("core_role_coverage_incomplete")
        return GateCheck(key[1],"record_consistent" if not errors else "unresolved",unique(errors),
                         freeze({"required_core_roles":32,"received_core_roles":len(seen),"descriptor_pairs":len(found),
                                 "unresolved_pairs":overlaps,"artifact_execution_performed":False}),mock)

    def hero_audit_check(self, key: Key) -> GateCheck:
        p=self.payload(key);rows=p.get("extensions",{}).get("hero_audit_positions") if p else None
        errors=[];found=set();missing=[];refs=[]
        block_ids=p.get("extensions",{}).get("hero_block_ids",()) if p else ()
        if not isinstance(block_ids,(list,tuple)) or len(block_ids)!=6 or any(not is_id(b) for b in block_ids) or len(set(block_ids))!=6:
            errors.append("hero_block_order_unresolved");block_ids=()
        if not isinstance(rows,(tuple,list)) or len(rows)>72:
            rows=();errors.append("hero_audit_positions_missing_or_malformed")
        for row in rows:
            if not isinstance(row,Mapping):errors.append("hero_audit_position_malformed");continue
            b,c,g=(row.get(n) for n in ("block_index","condition_index","group_index"))
            if not (type(b) is int and 1<=b<=6 and type(c) is int and 1<=c<=3 and type(g) is int and 1<=g<=4):
                errors.append("hero_audit_position_malformed");continue
            ident=(b,c,g)
            if ident in found:errors.append("duplicate_audit_position")
            found.add(ident)
            if type(row.get("within_group_index")) is not int or row["within_group_index"]!=1+((b+c+g-3)%5):errors.append("hero_audit_selection_mismatch")
            try:value=known(row.get("sample_ref"))
            except InputError:value=None
            if value is None or not self.links_exist([value],{"realization"}):missing.append(ident)
            else:
                refs.append(ref_key(value))
                sample=self.resolve(value)
                cell=self.get(("cell",sample.data["analysis_cell_id"]))
                aid=known(sample.data["attempt_id"])
                attempt=self.get(("attempt",aid)) if aid is not None else None
                if known(sample.data["within_group_index"])!=row["within_group_index"]:
                    errors.append("audit_sample_position_mismatch")
                if (attempt is None or known(attempt.data["registered_call_order"])!=g
                        or known(attempt.data["generation_group_id"])!=known(sample.data["generation_group_id"])):
                    errors.append("audit_sample_group_mismatch")
                if cell is None or not block_ids or cell.data["prompt_block_id"]!=block_ids[b-1] or cell.data["condition_id"]!=("A","B","C")[c-1]:
                    errors.append("audit_sample_cell_mismatch")
        if len(found)!=72:errors.append("hero_audit_position_coverage_incomplete")
        if len(set(refs))!=len(refs):errors.append("audit_sample_reused_for_multiple_positions")
        if missing:errors.append("planned_audit_opportunity_missing")
        if p and {ref_key(v) for v in p["planned_refs"]}!=set(refs):errors.append("audit_plan_membership_mismatch")
        return GateCheck(key[1],"record_consistent" if not errors else "unresolved",unique(errors),
                         freeze({"required_positions":72,"received_positions":len(found),"missing_opportunities":missing,
                                 "model_samples_added":0,"random_error_estimated":False}),bool(p and (p["mock"] or p["data_role"]=="fixture")))

    def claim_check(self, key: Key) -> GateCheck:
        p = self.payload(key)
        if p is None or key[0] != "integrity_assessment":
            return GateCheck(key[1], "withheld", ("claim_payload_unresolved",))
        reasons, statuses = list(self.affected(key, {"independence", "schema"})), {}
        operational = p["claim_kind"] == "operational_openness"
        if not self.role_present(p["reviewer_refs"]): reasons.append("claim_reviewer_unresolved")
        names = set(p["requirements"])
        if operational and names != set(INTEGRITY_CONDITIONS): reasons.append("five_conditions_required")
        for name, req in p["requirements"].items():
            if not isinstance(req, Mapping) or set(req) != {"outcome", "reason", "evidence_refs"}:
                reasons.append("malformed_requirement"); continue
            state = req["outcome"]
            if not isinstance(state, str) or state not in {"satisfied_for_scope", "unsatisfied", "unresolved", "not_applicable"}:
                reasons.append("invalid_requirement_outcome"); continue
            if not nonblank(req["reason"]): reasons.append("missing_requirement_reason")
            try:
                valid_refs = self.links_exist(req["evidence_refs"])
            except (InputError, TypeError): valid_refs = False
            if valid_refs:
                for value in req["evidence_refs"]:
                    evidence = self.payload(ref_key(value))
                    if evidence is None or evidence["state"] != "active" or self.affected(ref_key(value), {"independence", "schema", "membership", "validity"}):
                        valid_refs = False
            if state == "satisfied_for_scope" and (not req["evidence_refs"] or not valid_refs):
                state = "unresolved"; reasons.append("requirement_basis_unresolved")
            if operational and state != "satisfied_for_scope": reasons.append("mandatory_condition_not_satisfied")
            statuses[name] = state
        mock = p["mock"] or p["data_role"] == "fixture" or bool(self.bundle.manifest and self.bundle.manifest.data["data_role"] == "fixture")
        if mock: reasons.append("fixture_claim_only")
        if operational and not nonblank(known(p["current_until"])):
            reasons.append("result_currentness_not_established")
        # Even structurally consistent imported endorsements remain endorsements
        # made by the named external reviewer, not certification by this module.
        return GateCheck(key[1], "restricted" if reasons else "declared_record_consistent", unique(reasons),
            freeze({"declared_disposition": p["declared_disposition"], "requirement_record_outcomes": statuses,
                    "current_until": p["current_until"], "substantive_claim": "not_certified_by_software"}), mock)

    def impact_records(self) -> tuple[CorrectionImpact, ...]:
        reverse: dict[Key, set[Key]] = defaultdict(set)
        for key, items in self.entries.items():
            r = self.get(key)
            if not r: continue
            values = []
            if key[0] in {"assignment", "validity"}:
                values = list(r.data["evidence_refs"]) + [{"record_type":"realization", "record_id":r.data["sample_id"], "record_version":"0.1"}]
                sample = self.get(("realization", r.data["sample_id"]))
                frame = self.frame_for(sample) if sample else None
                if frame: reverse[("frame",frame.record_id)].add(key)
            elif key in self.support:
                p = self.support[key].payload
                values = list(p["evidence_refs"]) + list(p.get("basis_refs", ())) + list(p.get("artifact_refs", ()))
                if key[0] == "domain_result": values.append(p["suite_ref"])
            for v in values: reverse[ref_key(v)].add(key)
        results = []
        for (_, cid), s in sorted(self.correctors.items()):
            p = s.payload; targets = {ref_key(x) for x in p["target_refs"]}
            visited, queue = set(targets), list(targets)
            while queue:
                for child in reverse.get(queue.pop(), ()):
                    if child not in visited: visited.add(child); queue.append(child)
            axes = {"assignment"} if p["effect"] in {"membership", "schema", "registry"} else {"validity"} if p["effect"] == "validity" else {"assignment", "validity"}
            affected = sorted(k[1] for k in visited if k[0] in axes)
            results.append(CorrectionImpact(cid, tuple(sorted(targets)), tuple(affected),
                p["effect"] == "independence", p["stage"], tuple(ref_key(x) for x in p["replacement_refs"])))
        return tuple(results)


def review_evidence(bundle: LoadedBundle) -> EvidenceReview:
    """Public Step 3 API. The original bundle is returned unchanged to callers."""
    index = EvidenceIndex(bundle)
    sample_ids = sorted(key[1] for key in index.entries if key[0] == "realization")
    admissions = tuple(index.admit(axis, sid) for sid in sample_ids for axis in ("assignment", "validity"))
    claims = tuple(index.claim_check(key) for key in sorted(index.support) if key[0] == "integrity_assessment")
    checks = list(index.support_checks)
    annotation_sets: dict[tuple[str, Key, str], list[Mapping[str, Any]]] = defaultdict(list)
    for key, support in index.support.items():
        if key[0] == "annotation":
            p = support.payload
            annotation_sets[(p["set_id"], ref_key(p["target_ref"]), p["aspect"])].append(
                {"record_type": "annotation", "record_id": key[1], "record_version": "0.1"})
    for _, refs in sorted(annotation_sets.items()):
        checks.append(index.core_annotations(refs))
    for key in sorted(index.support):
        if key[0] == "domain_result": checks.append(index.domain_check(key))
        elif key[0] == "audit": checks.append(index.audit_check(key))
        elif key[0] == "domain_suite":
            if index.payload(key)["property"] == "sorting_behavior": checks.append(index.functional_manifest_check(key))
            if "reference_review" in index.payload(key).get("extensions", {}): checks.append(index.reference_check(key))
        elif key[0] == "sampling_plan" and "hero_audit_positions" in index.payload(key).get("extensions", {}):
            checks.append(index.hero_audit_check(key))
    return EvidenceReview(admissions, tuple(checks), claims, index.impact_records(),
        tuple(sorted(k for k in index.entries if k[0] in {"assignment","validity"})),
        bundle.acquisition_complete, bool(bundle.manifest and bundle.manifest.data["data_role"] == "fixture"))
