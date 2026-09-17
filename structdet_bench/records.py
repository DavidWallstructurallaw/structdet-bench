"""Fixed record dispatch and input identity validation. No evidence admission.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from typing import Any, Mapping
from .contracts import (
    ASSIGNMENT_STATES, CLASS_IDS, DATA_ROLES, EVIDENCE_POLICIES, HERO_IDENTITIES,
    INPUT_SCHEMA_VERSION, RECORD_TYPES, RECORD_VERSION, REVIEW_STATES,
    SUPPORT_RECORD_TYPES, VALIDITY_STATES, Diagnostic, InputError, ThresholdToken,
    freeze, in_enum, is_hash, is_id, knowledge, threshold_token, validate_ref,
)

@dataclass(frozen=True)
class TypedRecord:
    record_type: str
    record_id: str
    record_version: str
    data: Mapping[str, Any] = field(repr=False)
    validation_level: str = "record_shape"

@dataclass(frozen=True)
class AttemptRecord(TypedRecord):
    pass

@dataclass(frozen=True)
class RealizationRecord(TypedRecord):
    pass

@dataclass(frozen=True)
class AssignmentRecord(TypedRecord):
    pass

@dataclass(frozen=True)
class ValidityRecord(TypedRecord):
    pass

@dataclass(frozen=True)
class ArtifactRecord(TypedRecord):
    pass

@dataclass(frozen=True)
class RecordEntry:
    source: str
    line: int | None
    raw: Any = field(repr=False)
    record: TypedRecord | None
    diagnostics: tuple[Diagnostic, ...] = ()
    @property
    def shape_valid(self) -> bool:
        return self.record is not None

@dataclass(frozen=True)
class Manifest:
    data: Mapping[str, Any] = field(repr=False)
    declarations: tuple[RecordEntry, ...]
    threshold: ThresholdToken | None
    diagnostics: tuple[Diagnostic, ...]

# Every required metadata field must be present, even when its tagged value is
# explicitly unknown. Optional metadata is never completed by a guessed default.
REQUIRED = {k: frozenset(v.split()) for k, v in {
    "frame": "frame_id task_id task_version task_context consequence_horizon analytic_resolution_id analytic_resolution_version structural_schema_id structural_schema_version reference_registry_id reference_registry_version validity_rubric_ref load_bearing_invariants consequence_signature_spec equivalence_rule_ref admissible_substitutions evidence_requirement exceptional_case_rules registration_ref",
    "protocol": "generation_protocol_id generation_protocol_version conditioning_context_ref decoding_settings seed",
    "cell": "analysis_cell_id frame_id generation_protocol_id generation_protocol_version prompt_block_id prompt_id condition_id model_identifier model_family checkpoint_identifier collection_window",
    "attempt": "attempt_id analysis_cell_id attempt_status retry_of raw_response_ref generation_group_id planned_candidate_count registered_call_order",
    "realization": "sample_id analysis_cell_id attempt_id raw_response_ref output_ref output_content_hash generation_group_id within_group_index sample_order extraction_rule_version completion_status",
    "assignment": "assignment_id assignment_version sample_id frame_id assignment_status structural_class_id assignment_review_status assignment_method decision_rationale evidence_refs assignment_evidence_policy_id assignment_evidence_policy_version supersedes_assignment_id",
    "validity": "validity_id validity_version sample_id validity_status validity_rubric_ref validity_review_status evidence_refs decision_rationale supersedes_validity_id",
    "artifact": "artifact_id content_ref expected_sha256 knowledge_type",
    "raw_artifact": "artifact_id content_ref expected_sha256 knowledge_type",
    "reference_registry": "reference_registry_id reference_registry_version frame classes validation_status provenance source_fragments",
}.items()}
OPTIONAL = {k: frozenset(v.split()) for k, v in {
    "frame": "registry_ref", "protocol": "shared_context_ref sampling_plan_ref intervention_ref",
    "cell": "budget_record_ref recursive_round_id parent_state_ref transition_ref",
    "attempt": "termination_reason budget_record_ref",
    "realization": "shared_context_ref termination_reason selection_status selection_reason group_type",
    "assignment": "candidate_class_ids classification_uncertainty_ref disagreement_ref role_records_ref correction_ref output_content_hash",
    "validity": "task_success_observations_ref role_records_ref correction_ref",
    "artifact": "transformation_history external_locator artifact_role",
    "raw_artifact": "transformation_history external_locator artifact_role",
    "reference_registry": "",
}.items()}
ALIASES = dict(zip(REQUIRED, ("frame_id", "generation_protocol_id", "analysis_cell_id", "attempt_id", "sample_id", "assignment_id", "validity_id", "artifact_id", "artifact_id", "reference_registry_id")))
COMMON = {"record_type", "record_version", "record_id", "extensions"}

def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def positive(value: Any) -> bool:
    return type(value) is int and value > 0

def ref(value: Any) -> bool:
    validate_ref(value)
    return True

def artifact_ref(value: Any) -> bool:
    return ref(value) and value["record_type"] in {"artifact", "raw_artifact"}

def refs(value: Any) -> bool:
    return isinstance(value, (tuple, list)) and all(ref(v) for v in value)

def locator(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    if value.get("kind") == "local":
        return set(value) == {"kind", "path"} and text(value["path"])
    return value.get("kind") == "external" and set(value) == {"kind", "locator"} and text(value["locator"])

def parse_record(raw: Any, source: str, line: int | None = None) -> RecordEntry:
    issues: list[Diagnostic] = []
    def bad(code: str, name: str = "", scope: str = "record") -> None:
        issues.append(Diagnostic(code, scope, source, name, line))
    def done(record: TypedRecord | None = None) -> RecordEntry:
        return RecordEntry(source, line, freeze(raw), record, tuple(issues))
    if not isinstance(raw, Mapping):
        bad("record_not_object")
        return done()
    kind = raw.get("record_type")
    if not in_enum(kind, RECORD_TYPES):
        bad("unsupported_record_type")
    if raw.get("record_version") != RECORD_VERSION:
        bad("unsupported_record_version")
    if not is_id(raw.get("record_id")):
        bad("invalid_record_id")
    if "extensions" in raw and not isinstance(raw["extensions"], Mapping):
        bad("invalid_extensions")
    if issues:
        return done()
    if kind in SUPPORT_RECORD_TYPES:
        if set(raw) - COMMON - {"payload"} or not isinstance(raw.get("payload"), Mapping):
            bad("invalid_support_envelope")
        return done(None if issues else TypedRecord(kind, raw["record_id"], RECORD_VERSION, freeze(raw), "envelope_only"))
    for name in sorted(REQUIRED[kind] - raw.keys()):
        bad("missing_required_field", name)
    if set(raw) - COMMON - REQUIRED[kind] - OPTIONAL[kind]:
        bad("unknown_record_field")
    if raw.get(ALIASES[kind]) != raw["record_id"]:
        bad("identity_alias_mismatch", ALIASES[kind])
    if issues:
        return done()
    def check(name: str, predicate: Any) -> None:
        try:
            if not predicate(raw[name]):
                bad("invalid_field", name)
        except InputError as exc:
            bad(exc.code, name)
    def tagged(name: str, predicate: Any = lambda _: True) -> None:
        def valid(v: Any) -> bool:
            k = knowledge(v)
            return k.state != "known" or predicate(k.value)
        check(name, valid)
    if kind == "frame":
        for name in sorted(REQUIRED[kind] - {"registration_ref", "load_bearing_invariants"}):
            check(name, text)
        check("load_bearing_invariants", lambda v: isinstance(v, (list, tuple)) and bool(v) and all(text(x) for x in v))
        tagged("registration_ref", ref)
        for name, expected in HERO_IDENTITIES.items():
            if raw[name] != expected:
                bad("unsupported_frame_identity", name, "frame")
    elif kind == "protocol":
        for name in ("generation_protocol_id", "generation_protocol_version"):
            check(name, is_id)
        tagged("conditioning_context_ref", artifact_ref)
        tagged("decoding_settings", lambda v: isinstance(v, Mapping))
        tagged("seed", lambda v: v is None or type(v) is int)
    elif kind == "cell":
        for name in sorted(REQUIRED[kind] - {"model_identifier", "model_family", "checkpoint_identifier", "collection_window"}):
            check(name, is_id)
        for name in ("model_identifier", "model_family", "checkpoint_identifier"):
            tagged(name, text)
        tagged("collection_window")
    elif kind == "attempt":
        check("analysis_cell_id", is_id)
        check("attempt_status", lambda v: in_enum(v, {"succeeded", "failed", "cancelled", "not_attempted", "unknown"}))
        tagged("retry_of", lambda v: v is None or is_id(v))
        tagged("raw_response_ref", artifact_ref)
        tagged("generation_group_id", is_id)
        tagged("planned_candidate_count", lambda v: type(v) is int and v >= 0)
        tagged("registered_call_order", positive)
    elif kind == "realization":
        check("analysis_cell_id", is_id)
        for name in ("attempt_id", "generation_group_id", "extraction_rule_version"):
            tagged(name, is_id)
        for name in ("raw_response_ref", "output_ref"):
            tagged(name, artifact_ref)
        tagged("output_content_hash", is_hash)
        for name in ("sample_order", "within_group_index"):
            tagged(name, positive)
        check("completion_status", lambda v: in_enum(v, {"complete", "truncated", "refused", "failed", "unknown"}))
    elif kind == "assignment":
        for name in ("sample_id", "frame_id", "assignment_version"):
            check(name, is_id)
        check("assignment_status", lambda v: in_enum(v, ASSIGNMENT_STATES))
        check("assignment_review_status", lambda v: in_enum(v, REVIEW_STATES))
        check("assignment_evidence_policy_id", lambda v: in_enum(v, EVIDENCE_POLICIES))
        check("assignment_evidence_policy_version", lambda v: v == "0.1")
        for name in ("assignment_method", "decision_rationale"):
            tagged(name, text)
        check("evidence_refs", refs)
        tagged("supersedes_assignment_id", lambda v: v is None or is_id(v))
        if raw["assignment_status"] == "assigned":
            check("structural_class_id", is_id)
        elif raw["structural_class_id"] is not None:
            bad("class_on_unresolved_assignment", "structural_class_id")
    elif kind == "validity":
        for name in ("sample_id", "validity_version"):
            check(name, is_id)
        check("validity_status", lambda v: in_enum(v, VALIDITY_STATES))
        check("validity_review_status", lambda v: in_enum(v, REVIEW_STATES))
        for name in ("validity_rubric_ref", "decision_rationale"):
            tagged(name, text)
        check("evidence_refs", refs)
        tagged("supersedes_validity_id", lambda v: v is None or is_id(v))
    elif kind in {"artifact", "raw_artifact"}:
        tagged("content_ref", locator)
        tagged("expected_sha256", is_hash)
        tagged("knowledge_type", text)
    elif kind == "reference_registry":
        check("reference_registry_id", lambda v: v == HERO_IDENTITIES["reference_registry_id"])
        check("reference_registry_version", lambda v: v == "0.1")
        check("frame", lambda v: isinstance(v, Mapping) and all(v.get(k) == x for k, x in HERO_IDENTITIES.items()))
        check("classes", lambda v: isinstance(v, (list, tuple)) and all(isinstance(c, Mapping) for c in v) and tuple(c.get("structural_class_id") for c in v) == CLASS_IDS)
        if isinstance(raw["classes"], (tuple, list)):
            for c in raw["classes"]:
                if not isinstance(c, Mapping) or not all(text(c.get(k)) for k in ("name", "membership_rule", "permitted_variation", "distinguishing_evidence")):
                    bad("invalid_class_descriptor", "classes")
        tagged("validation_status", text)
        check("provenance", lambda v: isinstance(v, Mapping))
        check("source_fragments", lambda v: isinstance(v, Mapping) and all(text(x) for x in v.values()))
    for name in sorted(OPTIONAL[kind] & raw.keys()):
        if name == "registry_ref":
            check(name, lambda v: ref(v) and v["record_type"] == "reference_registry")
        elif name == "candidate_class_ids":
            check(name, lambda v: isinstance(v, (list, tuple)) and all(is_id(x) for x in v))
        elif name == "transformation_history":
            check(name, refs)
        else:
            tagged(name)
    cls = {"attempt": AttemptRecord, "realization": RealizationRecord, "assignment": AssignmentRecord,
           "validity": ValidityRecord, "artifact": ArtifactRecord, "raw_artifact": ArtifactRecord}.get(kind, TypedRecord)
    return done(None if issues else cls(kind, raw["record_id"], RECORD_VERSION, freeze(raw)))

def _config(value: Any) -> ThresholdToken | None:
    fields = {"analysis_config_id", "assignment_evidence_policy_id", "assignment_evidence_policy_version", "requested_k", "selection", "assignment_pins", "validity_pins"}
    if not isinstance(value, Mapping) or fields - value.keys() or set(value) - fields - {"empirical_threshold", "extensions"}:
        raise InputError("invalid_analysis_config")
    if not is_id(value["analysis_config_id"]) or not in_enum(value["assignment_evidence_policy_id"], EVIDENCE_POLICIES) or value["assignment_evidence_policy_version"] != "0.1":
        raise InputError("unsupported_evidence_policy")
    if "extensions" in value and not isinstance(value["extensions"], Mapping):
        raise InputError("invalid_extensions")
    ks = value["requested_k"]
    if not isinstance(ks, (list, tuple)) or not all(positive(k) for k in ks) or len(set(ks)) != len(ks):
        raise InputError("invalid_requested_k")
    if not isinstance(value["selection"], (tuple, list)):
        raise InputError("invalid_selection")
    seen: set[str] = set()
    for s in value["selection"]:
        if not isinstance(s, Mapping) or set(s) != {"analysis_cell_id", "selected_sample_ids", "sample_order", "registered_positions", "selection_basis"} or not is_id(s["analysis_cell_id"]):
            raise InputError("invalid_selection")
        if s["analysis_cell_id"] in seen:
            raise InputError("duplicate_selection_cell")
        seen.add(s["analysis_cell_id"])
        for name in ("selected_sample_ids", "sample_order", "registered_positions", "selection_basis"):
            k = knowledge(s[name])
            if k.state != "known":
                continue
            if name == "selection_basis":
                valid = text(k.value)
            else:
                valid = isinstance(k.value, (tuple, list))
                if valid and name != "registered_positions":
                    valid = all(is_id(x) for x in k.value) and len(set(k.value)) == len(k.value)
            if not valid:
                raise InputError("invalid_selection_value")
    for kind in ("assignment", "validity"):
        pins = value[kind + "_pins"]
        if not isinstance(pins, (tuple, list)):
            raise InputError("invalid_revision_pins")
        for pin in pins:
            if not isinstance(pin, Mapping) or set(pin) != {"sample_id", kind + "_id", kind + "_version"} or not all(is_id(v) for v in pin.values()):
                raise InputError("invalid_revision_pin")
    return threshold_token(value["empirical_threshold"]) if "empirical_threshold" in value else None

def parse_manifest(raw: Any, source: str = "bundle.json", *, max_records: int = 100_000) -> Manifest:
    required = {"input_schema_version", "bundle_id", "study_id", "data_role", "frames", "protocols", "cells", "analysis_config", "record_files"}
    if not isinstance(raw, Mapping) or required - raw.keys() or set(raw) - required - {"extensions", "source_pins"}:
        raise InputError("invalid_manifest")
    if raw["input_schema_version"] != INPUT_SCHEMA_VERSION:
        raise InputError("unsupported_input_schema_version")
    if not is_id(raw["bundle_id"]) or not is_id(raw["study_id"]) or not in_enum(raw["data_role"], DATA_ROLES):
        raise InputError("invalid_manifest_identity")
    if "extensions" in raw and not isinstance(raw["extensions"], Mapping):
        raise InputError("invalid_extensions")
    if not positive(max_records):
        raise InputError("invalid_record_limit")
    entries: list[RecordEntry] = []
    for name, kind in (("frames", "frame"), ("protocols", "protocol"), ("cells", "cell")):
        if not isinstance(raw[name], (tuple, list)):
            raise InputError("invalid_declarations")
        for i, value in enumerate(raw[name]):
            if len(entries) >= max_records:
                raise InputError("record_count_exceeded")
            e = parse_record(value, f"{source}#{name}:{i}")
            if isinstance(value, Mapping) and value.get("record_type") != kind:
                e = replace(e, record=None, diagnostics=(*e.diagnostics, Diagnostic("wrong_declaration_type", "manifest", source, name)))
            entries.append(e)
    issues = [d for e in entries for d in e.diagnostics]
    threshold = None
    try:
        threshold = _config(raw["analysis_config"])
    except InputError as exc:
        issues.append(Diagnostic(exc.code, "analysis_config", source))
    files, seen = raw["record_files"], set()
    if not isinstance(files, (tuple, list)):
        raise InputError("invalid_record_files")
    for item in files:
        if not isinstance(item, Mapping) or set(item) != {"role", "format", "path", "expected_sha256"}:
            raise InputError("invalid_file_declaration")
        if not in_enum(item["role"], {"observations", "evidence", "registry"}) or item["format"] != ("json" if item["role"] == "registry" else "jsonl") or not text(item["path"]):
            raise InputError("invalid_file_declaration")
        if item["path"] in seen:
            raise InputError("duplicate_file_declaration")
        seen.add(item["path"])
        k = knowledge(item["expected_sha256"])
        if k.state == "known" and not is_hash(k.value):
            raise InputError("invalid_expected_hash")
    pins, seen = raw.get("source_pins", []), set()
    if not isinstance(pins, (tuple, list)):
        raise InputError("invalid_source_pins")
    for pin in pins:
        if not isinstance(pin, Mapping) or set(pin) != {"source_id", "sha256"} or not is_id(pin["source_id"]) or not is_hash(pin["sha256"]):
            raise InputError("invalid_source_pin")
        if pin["source_id"] in seen:
            raise InputError("duplicate_source_pin")
        seen.add(pin["source_id"])
    return Manifest(freeze(raw), tuple(entries), threshold, tuple(issues))

def inspect_references(entries: tuple[RecordEntry, ...], manifest: Manifest) -> tuple[Diagnostic, ...]:
    """Check references; never choose a winner, admit a label, or create samples."""
    index: dict[tuple[str, str], list[TypedRecord]] = defaultdict(list)
    counts: Counter = Counter()
    issues: list[Diagnostic] = []
    for e in entries:
        if isinstance(e.raw, Mapping) and in_enum(e.raw.get("record_type"), RECORD_TYPES) and is_id(e.raw.get("record_id")):
            counts[(e.raw["record_type"], e.raw["record_id"])] += 1
        if e.record:
            index[(e.record.record_type, e.record.record_id)].append(e.record)
    for key, n in counts.items():
        if n > 1:
            issues.append(Diagnostic("duplicate_record_identity", "identity", ":".join(key)))
    def get(kind: str, identity: str, source: str, field_name: str) -> TypedRecord | None:
        found = index.get((kind, identity), [])
        n = counts[(kind, identity)]
        if len(found) != 1 or n != 1:
            code = "ambiguous_reference" if n > 1 else "invalid_reference_target" if n else "missing_reference"
            issues.append(Diagnostic(code, "record", source, field_name))
            return None
        return found[0]
    def walk(value: Any, source: str, name: str) -> None:
        if isinstance(value, Mapping):
            if set(value) == {"record_type", "record_id", "record_version"}:
                try:
                    validate_ref(value)
                except InputError as exc:
                    issues.append(Diagnostic(exc.code, "record", source, name))
                    return
                get(value["record_type"], value["record_id"], source, name)
            else:
                for v in value.values():
                    walk(v, source, name)
        elif isinstance(value, (tuple, list)):
            for v in value:
                walk(v, source, name)
    for entry in entries:
        r = entry.record
        if r is None:
            continue
        d, kind, source = r.data, r.record_type, f"{r.record_type}:{r.record_id}"
        for name, value in d.items():
            if name not in {"extensions", "payload", "source_fragments", "provenance"}:
                walk(value, source, name)
        if kind == "cell":
            get("frame", d["frame_id"], source, "frame_id")
            p = get("protocol", d["generation_protocol_id"], source, "generation_protocol_id")
            if p and p.data["generation_protocol_version"] != d["generation_protocol_version"]:
                issues.append(Diagnostic("protocol_version_mismatch", "cell", source))
        if kind in {"attempt", "realization"}:
            get("cell", d["analysis_cell_id"], source, "analysis_cell_id")
        if kind == "realization":
            a = knowledge(d["attempt_id"])
            if a.state == "known":
                p = get("attempt", a.value, source, "attempt_id")
                if p and p.data["analysis_cell_id"] != d["analysis_cell_id"]:
                    issues.append(Diagnostic("attempt_cell_mismatch", "record", source))
        if kind in {"assignment", "validity"}:
            s = get("realization", d["sample_id"], source, "sample_id")
            if s:
                cells = index.get(("cell", s.data["analysis_cell_id"]), [])
                if len(cells) == 1:
                    c = cells[0]
                    if kind == "assignment" and d["frame_id"] != c.data["frame_id"]:
                        issues.append(Diagnostic("assignment_frame_mismatch", "assignment", source))
                    if kind == "validity":
                        fs = index.get(("frame", c.data["frame_id"]), [])
                        k = knowledge(d["validity_rubric_ref"])
                        if len(fs) == 1 and k.state == "known" and fs[0].data["validity_rubric_ref"] != k.value:
                            issues.append(Diagnostic("validity_rubric_mismatch", "validity", source))
        if kind == "assignment":
            f = get("frame", d["frame_id"], source, "frame_id")
            if f and d["assignment_status"] == "assigned" and d["structural_class_id"] not in CLASS_IDS:
                issues.append(Diagnostic("class_outside_pinned_schema", "assignment", source))
    if any(d.scope == "analysis_config" for d in manifest.diagnostics):
        return tuple(issues)
    for kind in ("assignment", "validity"):
        seen: set[str] = set()
        for pin in manifest.data["analysis_config"][kind + "_pins"]:
            source = f"{kind}_pin:{pin['sample_id']}"
            if pin["sample_id"] in seen:
                issues.append(Diagnostic("conflicting_revision_pins", "sample", source))
            seen.add(pin["sample_id"])
            r = get(kind, pin[kind + "_id"], source, kind + "_id")
            if r and (r.data["sample_id"] != pin["sample_id"] or r.data[kind + "_version"] != pin[kind + "_version"]):
                issues.append(Diagnostic("revision_pin_mismatch", "sample", source))
    return tuple(issues)
