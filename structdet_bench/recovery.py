"""Evidence-qualified finite-family recovery and passive correction accounting.

All quantities are conditional on supplied records. No model calls, candidate
execution, new observations, independent validation or causal verdict occurs.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
from typing import Any, Mapping

from .contracts import InputError, SUPPORT_RECORD_TYPES, freeze, knowledge, validate_ref
from .comparison_records import configuration_fingerprint
from .categorical_null import Quantity
from .evidence import EvidenceIndex
from .local_io import LoadedBundle
from . import longitudinal_records as lr, longitudinal as lg, support_assays as sa, half_life as hl

METHOD = "finite_family_evidence_qualified_recovery_v1"
REGISTRATION_KEY = "recovery_registration_v1"
EVIDENCE_KEY = "recovery_evidence_v1"
STAGES = ("entry", "preprocessing", "selection", "exposure", "expression")
QUALIFIERS = ("finite_family_threshold_support", "unweighted_reference_classes",
              "conditional_on_supplied_evidence", "not_latent_repertoire",
              "no_causal_superiority_verdict")


def _require(ok, code):
    if not ok: raise InputError(code)


def _reasons(items):
    return tuple(sorted(set(items)))


def _value(tag):
    k = knowledge(tag)
    return k.value if k.state == "known" else None


def _nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def _oref(row):
    return {k: row[k] for k in ("object_kind", "object_id", "object_version")}


def _resolve(review, ref):
    return review.get(ref["object_kind"], ref["object_id"], ref["object_version"])


def _core_key(ref):
    validate_ref(ref)
    return ref["record_type"], ref["record_id"]


def _plain(value):
    if isinstance(value, Mapping): return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [_plain(v) for v in value]
    return value


def _link_limit(bundle):
    raw = bundle.manifest.data["analysis_config"]["extensions"]["longitudinal"]["limits"].get("max_link_objects", lr.LIMITS["max_link_objects"])
    _require(type(raw) is int and 1 <= raw <= lr.LIMITS["max_link_objects"], "recovery_link_limit_invalid")
    return raw


@dataclass(frozen=True)
class EvidenceGate:
    name: str
    status: str
    reasons: tuple[str, ...] = ()
    evidence_refs: tuple[Any, ...] = field(default=(), repr=False)
    mock_evidence: bool = False
    substantive_validation_performed: bool = False


@dataclass(frozen=True)
class ExogamyStage:
    stage: str
    status: str
    gate: EvidenceGate
    original_records: tuple[Any, ...] = field(default=(), repr=False)
    inferred_from_score: bool = False


@dataclass(frozen=True)
class RevisionRecord:
    ref: lr.ObjectRef
    revision_kind: str
    event_type: str
    disposition: str
    old_identity: Any
    new_identity: Any
    affected_refs: tuple[lr.ObjectRef, ...]
    original_refs: tuple[Any, ...]
    original_availability: tuple[bool, ...]
    evidence: Any = field(repr=False)
    reasons: tuple[str, ...] = ()
    new_model_samples: int = 0
    new_recursive_rounds: int = 0
    model_recovery_established: bool = False


@dataclass(frozen=True, order=True)
class DependencyLink:
    source: str
    target: str


@dataclass(frozen=True)
class CorrectionImpact:
    correction_id: str
    effect: str
    status: str
    source_nodes: tuple[str, ...]
    dependent_nodes: tuple[str, ...]
    invalidated_result_refs: tuple[str, ...]
    restricted_claim_refs: tuple[str, ...]
    preserved_result_refs: tuple[str, ...]
    claim_only: bool
    old_results_overwritten: bool = False
    new_model_samples: int = 0
    new_recursive_rounds: int = 0


@dataclass(frozen=True)
class RecoveryEpisode:
    ref: lr.ObjectRef | None
    status: str
    external_recovery_rate: Quantity
    reasons: tuple[str, ...] = ()
    pre_assay: sa.AssayResult | None = field(default=None, repr=False)
    post_assay: sa.AssayResult | None = field(default=None, repr=False)
    pre_present: tuple[str, ...] = ()
    pre_below: tuple[str, ...] = ()
    pre_unresolved: tuple[str, ...] = ()
    missing_classes: tuple[str, ...] | None = None
    confirmed_recovered: tuple[str, ...] = ()
    post_below: tuple[str, ...] = ()
    unresolved_post: tuple[str, ...] = ()
    partial_information_bounds: tuple[Fraction, Fraction] | None = None
    gates: tuple[EvidenceGate, ...] = ()
    stages: tuple[ExogamyStage, ...] = ()
    changes_model_parameters: bool | None = None
    changes_tools: bool | None = None
    changes_retrieval: bool | None = None
    changes_conditioning: bool | None = None
    pre_state_ref: lr.ObjectRef | None = None
    post_state_ref: lr.ObjectRef | None = None
    intervention_ref: lr.ObjectRef | None = None
    configuration_identities: Any = field(default=None, repr=False)
    source_records: tuple[Any, ...] = field(default=(), repr=False)
    registration: Any = field(default=None, repr=False)
    evidence_status: str = "unavailable"
    expression_scope: str = "unavailable"
    method: str = METHOD
    assay_method: str = sa.METHOD
    qualifiers: tuple[str, ...] = QUALIFIERS
    partial_bounds_are_confidence_interval: bool = False
    substantive_validation_performed: bool = False
    model_recovery_established: bool = False
    structural_exogamy_certified: bool = False
    new_model_samples: int = 0
    new_recursive_rounds: int = 0


@dataclass(frozen=True)
class RecoveryStudy:
    requested: bool
    status: str
    input_context_sha256: str | None
    review: lr.LongitudinalReview = field(repr=False)
    episodes: tuple[RecoveryEpisode, ...] = ()
    revisions: tuple[RevisionRecord, ...] = ()
    dependencies: tuple[DependencyLink, ...] = ()
    correction_impacts: tuple[CorrectionImpact, ...] = ()
    reasons: tuple[str, ...] = ()
    assays: sa.SupportAssayStudy | None = field(default=None, repr=False)
    observed: lg.ObservedStudy | None = field(default=None, repr=False)
    fits: hl.HalfLifeStudy | None = field(default=None, repr=False)
    method: str = METHOD
    substantive_validation_performed: bool = False
    model_recovery_established: bool = False
    new_model_samples: int = 0
    new_recursive_rounds: int = 0


def context_fingerprint(episode, bundle: LoadedBundle) -> str:
    """Pin declared evaluation meaning, not observed outcomes or review conclusions.

    Helpers construct identity tokens only. They do not preregister an episode
    or assert that its material is independent or free of answer substitution.
    """
    _require(isinstance(bundle, LoadedBundle) and bundle.manifest is not None, "loaded_bundle_required")
    cfg = bundle.manifest.data["analysis_config"]["extensions"]["longitudinal"]
    def resolve(ref):
        rows = [r for collection in lr.FAMILIES for r in cfg[collection] if isinstance(r, Mapping) and _oref(r) == ref]
        _require(len(rows) == 1, "recovery_context_object_unresolved")
        return lr.ObjectBinding(lr._key(ref), "", rows[0])
    index = EvidenceIndex(bundle)
    rows = [episode]
    assays = [resolve(episode[k]) for k in ("pre_assay_ref", "post_assay_ref")]
    intervention = resolve(episode["intervention_ref"])
    _require(intervention is not None and all(assays), "recovery_endpoint_unresolved")
    rows.append(intervention.data)
    for a in assays:
        rows.append({k: v for k, v in a.data.items() if k not in {"trials", "evidence", "iid_evidence_ref"}})
        state = resolve(a.data["state_ref"])
        _require(state is not None, "recovery_state_unresolved")
        rows.append(state.data)
        for member in a.data["intervention_refs"]:
            b = resolve(member)
            _require(b is not None, "recovery_family_member_unresolved")
            rows.append(b.data)
        for mr in state.data["measurement_refs"]:
            m = resolve(mr)
            _require(m is not None, "recovery_measurement_unresolved")
            rows.append({k: m.data[k] for k in ("state_ref", "panel_ref", "frame_ref", "protocol_ref", "registry_ref", "view", "selection_rule")})
            for k in ("frame_ref", "protocol_ref", "registry_ref"):
                c = index.resolve(m.data[k]); _require(c is not None, "recovery_core_identity_unresolved")
                rows.append(c.data)
    static_material = _material_identity(bundle, intervention.data["external_refs"])
    return configuration_fingerprint({"method": METHOD, "evaluation_context": rows, "intervention_material": static_material})


def _material_identity(bundle, refs, *, index=None):
    """Snapshot identity for explicit material/source ancestry, without new I/O."""
    index = index or EvidenceIndex(bundle); pending = list(refs); seen = set(); result = []
    while pending:
        ref = pending.pop(); key = _core_key(ref)
        if key in seen: continue
        seen.add(key)
        _require(len(seen) <= _link_limit(bundle), "recovery_material_workload_limit")
        rec = index.resolve(ref)
        if rec is None: result.append({"key": key, "status": "unavailable"}); continue
        if key[0] in {"artifact", "raw_artifact"}:
            acquired = [a for a in bundle.artifacts if a.record_key == ":".join(key)]
            result.append({"record": rec.data, "acquisition": [vars(a) for a in acquired],
                "snapshots": [{"size": len(bundle.snapshots[a.snapshot_path].content),
                    "sha256": hashlib.sha256(bundle.snapshots[a.snapshot_path].content).hexdigest()}
                    for a in acquired if a.snapshot_path in bundle.snapshots]})
        else:
            p = index.payload(key)
            if p is not None:
                payload = _plain(p)
                payload.get("extensions", {}).pop(EVIDENCE_KEY, None)
                payload.get("extensions", {}).pop(REGISTRATION_KEY, None)
                if not payload.get("extensions"): payload.pop("extensions", None)
                result.append({"key": key, "payload": payload})
                for name in ("evidence_refs", "transformation_refs", "material_refs", "artifact_refs", "reference_artifact_refs"):
                    pending.extend(p.get(name, ()))
    return sorted(result, key=configuration_fingerprint)


def evidence_subject_fingerprint(episode, bundle):
    """Bind retrospective reviews to current observations and indispensable bytes.

    This token is never part of a before-inspection registration. Recovery
    witness extensions are removed to avoid requiring a self-referential hash.
    """
    cfg = bundle.manifest.data["analysis_config"]["extensions"]["longitudinal"]
    assay_refs = {lr._key(episode[k]) for k in ("pre_assay_ref", "post_assay_ref")}
    assays = [a for a in cfg["assays"] if lr._key(a) in assay_refs]
    samples = {_value(t["sample_ref"])["record_id"] for a in assays for t in a["trials"] if _value(t["sample_ref"])}
    pending = list(_ref_walk(episode))
    treatment = next((i for i in cfg["interventions"] if _oref(i) == episode["intervention_ref"]), None)
    if treatment: pending.extend(_ref_walk(treatment))
    for a in assays: pending.extend(_ref_walk(a))
    index = EvidenceIndex(bundle); seen = set(); rows = []
    for entry in bundle.records:
        r = entry.record
        if r and r.record_type in {"assignment", "validity"} and r.data.get("sample_id") in samples:
            pending.append({"record_type": r.record_type, "record_id": r.record_id, "record_version": r.record_version})
    while pending:
        ref = pending.pop()
        if "record_type" not in ref: continue
        key = _core_key(ref)
        if key in seen: continue
        seen.add(key)
        _require(len(seen) <= _link_limit(bundle), "recovery_subject_workload_limit")
        rec = index.resolve(ref)
        if rec is None: rows.append({"key": key, "status": "unavailable"}); continue
        plain = _plain(rec.data)
        payload = plain.get("payload")
        if payload:
            payload.get("extensions", {}).pop(EVIDENCE_KEY, None)
            payload.get("extensions", {}).pop(REGISTRATION_KEY, None)
            if not payload.get("extensions"): payload.pop("extensions", None)
        rows.append(plain)
        if key[0] in {"artifact", "raw_artifact"}: rows.extend(_material_identity(bundle, [ref], index=index))
        pending.extend(_ref_walk(plain))
    registration_ref = _value(cfg["registered_design_ref"])
    registration = index.payload(_core_key(registration_ref)) if registration_ref else None
    container = registration.get("extensions", {}).get(REGISTRATION_KEY) if registration else None
    registered_scope = [w for w in container.get("episodes", ()) if isinstance(w, Mapping) and w.get("episode_ref") == _oref(episode)] if isinstance(container, Mapping) else []
    return configuration_fingerprint({"method": METHOD, "assays": assays, "registered_recovery_scope": registered_scope,
        "reviewed_records": sorted(rows, key=configuration_fingerprint)})


def registration_witness(episode, *, bundle, hypothesis, permitted_exposure_refs,
                         evaluation_material_refs, member_pairs, changes_tools=False,
                         changes_retrieval=False, changes_conditioning=False):
    """Return one identity-bound row for a separately supplied registration."""
    return {"episode_ref": _oref(episode), "context_sha256": context_fingerprint(episode, bundle),
            "hypothesis": hypothesis, "permitted_exposure_refs": _plain(permitted_exposure_refs),
            "evaluation_material_refs": _plain(evaluation_material_refs), "member_pairs": _plain(member_pairs),
            "material_sha256": configuration_fingerprint(_material_identity(bundle, list(permitted_exposure_refs) + list(evaluation_material_refs))),
            "changes_tools": changes_tools, "changes_retrieval": changes_retrieval,
            "changes_conditioning": changes_conditioning}


def evidence_witness(episode, role, *, bundle, outcome="supported"):
    return {"episode_ref": _oref(episode), "context_sha256": context_fingerprint(episode, bundle),
            "subject_sha256": evidence_subject_fingerprint(episode, bundle), "role": role, "outcome": outcome}


_DEPENDENCIES = ("evidence_refs", "reviewer_refs", "transformation_refs", "artifact_refs",
                 "material_refs", "exposure_refs", "basis_refs", "annotation_refs",
                 "reference_artifact_refs", "reviewed_refs")


def _inspect(index, refs, role, data_role, limits):
    """Follow indispensable evidence, preserving child mock and access states."""
    pending = [(r, False) for r in refs]; active = set(); done = set()
    reasons = []; mock = False
    while pending:
        ref, leave = pending.pop()
        try: key = _core_key(ref)
        except (InputError, KeyError, TypeError):
            reasons.append(role + "_reference_invalid"); continue
        if leave: active.discard(key); done.add(key); continue
        if key in active: reasons.append(role + "_circular_decisive_evidence"); continue
        if key in done: continue
        if len(done) + len(active) >= limits["max_link_objects"]:
            reasons.append(role + "_evidence_limit"); break
        record = index.resolve(ref)
        if record is None: reasons.append(role + "_reference_unresolved"); continue
        active.add(key); pending.append((ref, True))
        if key[0] in {"artifact", "raw_artifact"}:
            if not sa._artifact_available(index.bundle, ref): reasons.append(role + "_artifact_unavailable")
            continue
        if key[0] not in SUPPORT_RECORD_TYPES:
            reasons.append(role + "_decisive_record_type_invalid"); continue
        p = index.payload(key)
        if p is None: reasons.append(role + "_payload_unavailable"); continue
        ismock = p["mock"] or p["data_role"] == "fixture"; mock |= ismock
        if data_role != "fixture" and ismock: reasons.append(role + "_mock_for_nonfixture")
        if p["state"] != "active" or p.get("access", "readable") != "readable" or p.get("conflict_status") == "unresolved":
            reasons.append(role + "_inactive_unreadable_or_conflicted")
        if any(not _nonblank(_value(p[k])) for k in ("origin", "knowledge_type")):
            reasons.append(role + "_provenance_unknown")
        if index.affected(key, {"metadata", "independence", "schema", "registry", "membership", "validity"}):
            reasons.append(role + "_under_correction")
        if key[0] == "role":
            if any(not _nonblank(_value(p[k])) for k in ("entity_id", "qualification", "method")) or p["entity_type"] == "unknown":
                reasons.append(role + "_reviewer_unqualified")
        if key[0] == "independence_assessment":
            if p["outcome"] != "supported_for_scope" or not _nonblank(_value(p["criterion"])):
                reasons.append(role + "_independence_unsupported")
            if not p["reviewer_refs"]: reasons.append(role + "_reviewer_missing")
        if key[0] == "domain_result":
            if p["outcome"] != "passed": reasons.append(role + "_validation_not_passed")
            pending.append((p["suite_ref"], False))
        if key[0] in {"audit", "domain_suite"} and p["stage"] != "performed":
            reasons.append(role + "_validation_not_performed")
        if key[0] == "audit" and (not p["reviewed_refs"] or set(map(_core_key, p["planned_refs"])) - set(map(_core_key, p["reviewed_refs"]))):
            reasons.append(role + "_audit_incomplete")
        if key[0] == "adjudication" and p["decision_state"] != "resolved": reasons.append(role + "_adjudication_unresolved")
        if key[0] == "lineage" and p["knowledge_state"] != "known": reasons.append(role + "_lineage_unknown")
        if key[0] == "exposure":
            if type(_value(p["exposed"])) is not bool: reasons.append(role + "_exposure_unknown")
            elif role == "exposure" and _value(p["exposed"]) is not True: reasons.append("exposure_not_performed")
            pending.append((p["role_ref"], False))
        for name in _DEPENDENCIES:
            pending.extend((r, False) for r in p.get(name, ()))
        for value in p.values():
            if isinstance(value, Mapping) and "state" in value:
                pending.extend((r, False) for r in value.get("evidence_refs", ()))
    return _reasons(reasons), mock


def _gate(name, reasons=(), refs=(), mock=False):
    rs = _reasons(reasons)
    return EvidenceGate(name, "eligible" if not rs else "unavailable", rs, tuple(freeze(r) for r in refs), mock)


def _scoped_gate(index, refs, role, episode, context, data_role, limits, allow_na=False, subject=None):
    reasons, mock = _inspect(index, refs, role, data_role, limits); reasons = list(reasons)
    if not refs: reasons.append(role + "_evidence_missing")
    outcomes = []
    cfg = index.bundle.manifest.data["analysis_config"]["extensions"]["longitudinal"]
    post_assay = next((a for a in cfg["assays"] if _oref(a) == episode["post_assay_ref"]), None)
    post_samples = {_core_key(_value(t["sample_ref"])) for t in post_assay["trials"] if _value(t["sample_ref"])} if post_assay else set()
    post_measurements = {lr._key(_value(t["measurement_ref"])) for t in post_assay["trials"] if _value(t["measurement_ref"])} if post_assay else set()
    post_cells = {_core_key(m["cell_ref"]) for m in cfg["measurements"] if lr._key(m) in post_measurements}
    for ref in refs:
        p = index.payload(_core_key(ref))
        if p is None: continue
        w = p.get("extensions", {}).get(EVIDENCE_KEY)
        required = {"episode_ref", "context_sha256", "subject_sha256", "role", "outcome"}
        if not isinstance(w, Mapping) or set(w) != required:
            reasons.append(role + "_witness_missing_or_malformed"); continue
        if w["episode_ref"] != _oref(episode) or w["context_sha256"] != context or w["role"] != role:
            reasons.append(role + "_scope_mismatch")
        if w["subject_sha256"] != subject: reasons.append(role + "_reviewed_subject_changed")
        outcome = w["outcome"]
        if not isinstance(outcome, str): reasons.append(role + "_assessment_unsupported"); continue
        outcomes.append(outcome)
        if outcome != "supported" and not (allow_na and outcome == "not_applicable"):
            reasons.append(role + "_assessment_unsupported")
        kind = ref["record_type"]
        if role == "grounding":
            if kind != "independence_assessment" or p.get("dimension") != "structural_grounding":
                reasons.append("grounding_structural_independence_required")
        elif kind == "evidence":
            expected = {"non_injection": "no_direct_answer_substitution", "external_validation": "post_intervention_expression_validated"}.get(role,
                "stage_not_applicable" if outcome == "not_applicable" else "stage_supported")
            if _value(p["assertion"]) != expected: reasons.append(role + "_assertion_mismatch")
            purpose = "validity" if role == "external_validation" else "independence" if role == "non_injection" else "observation"
            if p["purpose"] != purpose: reasons.append(role + "_purpose_mismatch")
            if not _nonblank(_value(p["method"])) or not _nonblank(_value(p["detail"])): reasons.append(role + "_method_or_detail_missing")
            if not p["artifact_refs"]: reasons.append(role + "_material_missing")
            if not p["reviewer_refs"]: reasons.append(role + "_reviewer_missing")
            if role in {"external_validation", "expression", "non_injection"} and _core_key(p["target_ref"]) not in post_samples | post_cells:
                reasons.append(role + "_post_subject_mismatch")
        elif role == "external_validation" and kind in {"domain_result", "audit"}:
            if not p["evidence_refs"]: reasons.append("validation_review_evidence_missing")
            if kind == "domain_result":
                target = _core_key(p["target_ref"]); sample = index.get(target)
                if target not in post_samples or sample is None: reasons.append("external_validation_post_subject_mismatch")
                elif _value(p["subject_hash"]) is None or _value(p["subject_hash"]) != _value(sample.data["output_content_hash"]):
                    reasons.append("external_validation_post_subject_hash_mismatch")
            else:
                reviewed = {_core_key(r) for r in p["reviewed_refs"]}
                if not reviewed or not reviewed <= post_samples | post_cells:
                    reasons.append("external_validation_post_subject_mismatch")
        else: reasons.append(role + "_evidence_type_invalid")
    if len(set(outcomes)) > 1: reasons.append(role + "_assessment_conflict")
    return _gate(role, reasons, refs, mock), outcomes


def _registration(index, review, episode, context, states):
    # Optional evidence extensions are not core schema fields. Malformed
    # review metadata must fail its gate without discarding valid assay facts.
    try:
        return _registered_episode(index, review, episode, context, states)
    except (InputError, KeyError, TypeError, ValueError, AttributeError) as exc:
        return _gate("registration", ("recovery_registration_malformed",
            getattr(exc, "code", "recovery_registration_binding_error"))), None


def _registered_episode(index, review, episode, context, states):
    ref = _value(review.configuration["registered_design_ref"])
    reasons, mock = _inspect(index, [ref] if ref else [], "registration", review.configuration["data_role"], review.limits)
    reasons = list(reasons)
    reasons.extend(lg._registration(index, ref, states, data_role=review.configuration["data_role"]).reasons)
    p = index.payload(_core_key(ref)) if ref else None
    container = p.get("extensions", {}).get(REGISTRATION_KEY) if p else None
    witness = None
    if not isinstance(container, Mapping) or set(container) != {"method", "inspection_status", "episodes"}:
        reasons.append("recovery_registration_missing_or_malformed")
    elif container["method"] != METHOD or container["inspection_status"] != "registered_before_inspection" or not isinstance(container["episodes"], (list, tuple)):
        reasons.append("recovery_registration_method_or_timing")
    else:
        rows = [w for w in container["episodes"] if isinstance(w, Mapping) and w.get("episode_ref") == _oref(episode)]
        if len(rows) != 1: reasons.append("recovery_registration_episode_missing_or_ambiguous")
        else:
            witness = rows[0]
            required = {"episode_ref", "context_sha256", "material_sha256", "hypothesis", "permitted_exposure_refs", "evaluation_material_refs", "member_pairs",
                        "changes_tools", "changes_retrieval", "changes_conditioning"}
            if set(witness) != required: reasons.append("recovery_registration_shape")
            elif witness["context_sha256"] != context: reasons.append("recovery_registration_context_mismatch")
            if not _nonblank(witness.get("hypothesis")): reasons.append("recovery_hypothesis_missing")
            if any(type(witness.get(k)) is not bool for k in ("changes_tools", "changes_retrieval", "changes_conditioning")):
                reasons.append("recovery_configuration_change_unknown")
            hashes = []
            for key in ("permitted_exposure_refs", "evaluation_material_refs"):
                refs = witness.get(key)
                if not isinstance(refs, (list, tuple)) or not refs:
                    reasons.append("recovery_" + key + "_missing"); hashes.append(set()); continue
                rs, mk = _inspect(index, refs, key, review.configuration["data_role"], review.limits); reasons.extend(rs); mock |= mk
                if any(not isinstance(r, Mapping) or r.get("record_type") not in {"artifact", "raw_artifact"} for r in refs):
                    reasons.append("recovery_material_artifacts_required"); hashes.append(set()); continue
                hashes.append({a.actual_sha256 for a in index.bundle.artifacts if any(a.record_key == r["record_type"] + ":" + r["record_id"] for r in refs) and a.actual_sha256})
            if len(hashes) == 2 and hashes[0] & hashes[1]: reasons.append("recovery_evaluation_exposure_material_overlap")
            if witness.get("material_sha256") != configuration_fingerprint(_material_identity(index.bundle,
                    list(witness.get("permitted_exposure_refs", ())) + list(witness.get("evaluation_material_refs", ())))):
                reasons.append("recovery_registered_material_changed")
    return _gate("registration", reasons, [ref] if ref else (), mock), witness


def _frame_signature(index, measurement):
    frame = index.resolve(measurement.data["frame_ref"])
    protocol = index.resolve(measurement.data["protocol_ref"])
    _require(frame is not None and protocol is not None, "recovery_evaluation_scope_unresolved")
    # Record identifiers can differ between sampled states; scientific fields cannot.
    ignored = {"record_type", "record_id", "record_version", "frame_id", "generation_protocol_id", "generation_protocol_version", "extensions"}
    return configuration_fingerprint({"frame": {k:v for k,v in frame.data.items() if k not in ignored},
                                      "protocol": {k:v for k,v in protocol.data.items() if k not in ignored},
                                      "view": measurement.data["view"]})


def _compatibility(review, index, episode, pre, post, intervention, witness):
    # Evidence withdrawal can restrict a claim while leaving the compared
    # class meanings intact. General record issues have their own gate.
    reasons = []
    d = episode.data; a = _resolve(review, d["pre_assay_ref"]); b = _resolve(review, d["post_assay_ref"])
    if d["criterion_version"] != sa.METHOD: reasons.append("recovery_criterion_version_unsupported")
    if a is None or b is None or intervention is None or pre is None or post is None:
        return _gate("compatibility", reasons + ["recovery_endpoint_unavailable"])
    x = intervention.data
    if a.data["state_ref"] != x["pre_state_ref"] or b.data["state_ref"] != x["post_state_ref"]:
        reasons.append("recovery_endpoint_binding_mismatch")
    for key in ("registry_ref", "family_id", "family_version", "success_event", "tau", "alpha", "allocation"):
        if a.data[key] != b.data[key]: reasons.append("recovery_criterion_binding_mismatch")
    if d["registry_ref"] != a.data["registry_ref"] or pre.classes != post.classes or not pre.classes:
        reasons.append("recovery_reference_universe_mismatch")
    if pre.J != post.J or pre.delta != post.delta: reasons.append("recovery_allocation_mismatch")
    pairs = witness.get("member_pairs") if isinstance(witness, Mapping) else None
    if not isinstance(pairs, (list, tuple)) or not pairs:
        reasons.append("recovery_registered_family_pairing_missing")
    else:
        try:
            _require(all(isinstance(p, Mapping) and set(p) == {"pre", "post"} for p in pairs), "recovery_family_pairing_shape")
            before = [lr._key(p["pre"]) for p in pairs]; after = [lr._key(p["post"]) for p in pairs]
            _require(len(set(before)) == len(before) and len(set(after)) == len(after) and set(before) == set(pre.intervention_refs) and set(after) == set(post.intervention_refs), "recovery_family_pairing_incomplete")
            for pair in pairs:
                left = _resolve(review, pair["pre"]); right = _resolve(review, pair["post"])
                _require(left is not None and right is not None, "recovery_family_pairing_unresolved")
                for key in ("intervention_kind", "parameters_changed", "direct_answer_injection", "external_refs"):
                    _require(left.data[key] == right.data[key], "recovery_family_member_meaning_changed")
                signatures = []
                for assay, member in ((a, pair["pre"]), (b, pair["post"])):
                    values = set()
                    for tr in assay.data["trials"]:
                        if tr["intervention_ref"] != member: continue
                        mr = _value(tr["measurement_ref"]); measured = _resolve(review, mr) if mr else None
                        if measured: values.add(_frame_signature(index, measured))
                    signatures.append(values)
                _require(signatures[0] and signatures[0] == signatures[1], "recovery_task_horizon_resolution_or_protocol_changed")
        except (InputError, TypeError, KeyError) as exc:
            reasons.append(getattr(exc, "code", "recovery_family_pairing_shape"))
    return _gate("compatibility", reasons)


def _configuration(review, intervention, witness):
    reasons = []; flags = [None] * 4; identities = None
    if intervention is None: return _gate("configuration", ["recovery_intervention_unavailable"]), flags, identities
    d = intervention.data
    pre = _resolve(review, d["pre_state_ref"]); post = _resolve(review, d["post_state_ref"])
    flags[0] = _value(d["parameters_changed"])
    for j, key in enumerate(("changes_tools", "changes_retrieval", "changes_conditioning"), 1):
        flags[j] = witness.get(key) if isinstance(witness, Mapping) else None
    if any(type(v) is not bool for v in flags): reasons.append("recovery_configuration_change_unknown")
    if pre is None or post is None or pre.data["state_kind"] != "model_system" or post.data["state_kind"] != "model_system":
        reasons.append("recovery_model_system_endpoints_required")
    else:
        left = _value(pre.data["subject_identity"]); right = _value(post.data["subject_identity"])
        identities = freeze({"pre": left, "post": right})
        if left is None or right is None: reasons.append("recovery_state_identity_unknown")
        else:
            for fields, declared in ((("parameter_identity", "checkpoint_sha256"), flags[0]), (("tool_identity",), flags[1]),
                                     (("retrieval_identity",), flags[2]), (("system_identity",), flags[3])):
                if any(knowledge(left[k]).state != "known" or knowledge(right[k]).state != "known" for k in fields):
                    reasons.append("recovery_state_identity_unknown"); continue
                changed = any(_value(left[k]) != _value(right[k]) for k in fields)
                if type(declared) is bool and changed != declared: reasons.append("recovery_configuration_change_mismatch")
            if any(knowledge(s["serving_identity"]).state != "known" for s in (left, right)):
                reasons.append("recovery_serving_identity_unknown")
            elif _value(left["serving_identity"]) != _value(right["serving_identity"]):
                reasons.append("recovery_serving_identity_changed_without_registered_dimension")
        if pre.ref == post.ref: reasons.append("recovery_distinct_state_identities_required")
    if flags[0] is False and not any(v is True for v in flags[1:]): reasons.append("recovery_no_identified_system_change")
    if d["intervention_kind"] == "training" and flags[0] is not True: reasons.append("recovery_training_state_change_missing")
    if d["intervention_kind"] == "tools" and flags[1] is not True: reasons.append("recovery_tool_change_missing")
    if d["intervention_kind"] == "retrieval" and flags[2] is not True: reasons.append("recovery_retrieval_change_missing")
    if _value(d["direct_answer_injection"]) is not False: reasons.append("recovery_direct_answer_injection_unresolved_or_present")
    return _gate("configuration", reasons), flags, identities


def _node(ref):
    if isinstance(ref, lr.ObjectRef): return "object:" + ref.object_kind + ":" + ref.object_id + "@" + ref.object_version
    if "object_kind" in ref: return _node(lr._key(ref))
    return "core:" + ref["record_type"] + ":" + ref["record_id"]


def _result(kind, ref):
    return "result:" + kind + ":" + ref.object_id + "@" + ref.object_version


def _ref_walk(value):
    if isinstance(value, Mapping):
        if set(value) == {"record_type", "record_id", "record_version"} or set(value) == {"object_kind", "object_id", "object_version"}:
            yield value
        else:
            for v in value.values(): yield from _ref_walk(v)
    elif isinstance(value, (list, tuple)):
        for v in value: yield from _ref_walk(v)


def _descendants(adjacency, starts):
    todo = deque(starts); seen = set(starts)
    while todo:
        for child in adjacency.get(todo.popleft(), ()):
            if child not in seen: seen.add(child); todo.append(child)
    return seen


def _dependencies(bundle, review, index):
    links = set()
    def link(a, b):
        if a != b:
            edge = DependencyLink(a, b)
            _require(edge in links or len(links) < review.limits["max_link_objects"], "recovery_dependency_workload_limit")
            links.add(edge)
    for entry in bundle.records:
        rec = entry.record
        if rec is None: continue
        target = "core:" + rec.record_type + ":" + rec.record_id
        if rec.record_type in SUPPORT_RECORD_TYPES:
            p = index.payload((rec.record_type, rec.record_id))
            if p:
                for name in _DEPENDENCIES:
                    for ref in p.get(name, ()): link(_node(ref), target)
                if rec.record_type == "domain_result": link(_node(p["suite_ref"]), target)
                # Metadata evidence tags have decisive evidence references too.
                for value in p.values():
                    if isinstance(value, Mapping) and "state" in value:
                        for ref in value.get("evidence_refs", ()): link(_node(ref), target)
        else:
            for ref in _ref_walk(rec.data): link(_node(ref), target)
        if rec.record_type in {"assignment", "validity"}:
            sid = rec.data.get("sample_id")
            if sid:
                link("core:realization:" + sid, target)
                link(target, "population:" + sid)
        if rec.record_type == "realization":
            link(target, "population:" + rec.record_id)
            cid = rec.data.get("analysis_cell_id")
            if cid: link("core:cell:" + cid, target)
        if rec.record_type == "cell":
            for name, kind in (("frame_id", "frame"), ("generation_protocol_id", "protocol")):
                if rec.data.get(name): link("core:" + kind + ":" + rec.data[name], target)
    for obj in review.objects:
        if obj.ref is None or obj.status == "contract_error": continue
        target = _node(obj.ref)
        kind = obj.ref.object_kind
        for name, value in obj.data.items():
            # A state lists its measurements for bookkeeping; a measurement's
            # observed class counts do not redefine its parameter identity.
            # Ancestor state observations likewise are not new child samples.
            if kind == "state" and name in {"measurement_refs", "ancestor_refs"}: continue
            if kind == "revision": continue
            for ref in _ref_walk(value):
                if ref.get("record_type") == "realization": link("population:" + ref["record_id"], target)
                else: link(_node(ref), target)
        outputs = {"measurement": ("distribution", "observed_support"), "observed_request": ("retention",),
                   "trajectory": ("curve",), "shl_request": ("fit", "sensitivity"),
                   "assay": ("assay",), "recovery_episode": ("missing_set", "err", "allowed_claim")}.get(kind, ())
        for output in outputs: link(target, _result(output, obj.ref))
        if kind == "recovery_episode":
            for field in ("pre_assay_ref", "post_assay_ref"):
                link(_result("assay", lr._key(obj.data[field])), target)
            link(_result("missing_set", obj.ref), _result("err", obj.ref))
            link(_result("err", obj.ref), _result("allowed_claim", obj.ref))
        if kind == "shl_request":
            link(_result("curve", lr._key(obj.data["trajectory_ref"])), target)
        if kind == "trajectory":
            for state_ref in obj.data["state_refs"]:
                state = _resolve(review, state_ref)
                if state:
                    for mr in state.data["measurement_refs"]:
                        link(_result("distribution", lr._key(mr)), _result("curve", obj.ref))
        if kind == "assay":
            for tr in obj.data["trials"]:
                mr = _value(tr["measurement_ref"])
                if mr: link(_result("observed_support", lr._key(mr)), _result("assay", obj.ref))
    _require(len(links) <= review.limits["max_link_objects"], "recovery_dependency_workload_limit")
    adjacency = defaultdict(set)
    for link_ in links: adjacency[link_.source].add(link_.target)
    all_results = {link_.target for link_ in links if link_.target.startswith("result:")}
    impacts = []
    def impact(identity, effect, status, starts, active):
        descendants = _descendants(adjacency, starts) if active else set()
        results = descendants & all_results
        claim_only = effect in {"independence", "metadata"}
        restricted = {r for r in results if r.split(":")[1] in {"assay", "missing_set", "err", "allowed_claim"}}
        invalidated = set() if claim_only else results - {r for r in results if r.split(":")[1] == "allowed_claim"}
        impacts.append(CorrectionImpact(identity, effect, status, tuple(sorted(starts)), tuple(sorted(descendants)),
            tuple(sorted(invalidated)), tuple(sorted(restricted)), tuple(sorted(all_results - invalidated - restricted)), claim_only))
    for key, record in sorted(index.correctors.items()):
        p = record.payload
        active = p["stage"] != "rejected" and p["action"] != "annotate"
        impact(key[1], p["effect"], p["stage"], {_node(r) for r in p["target_refs"]}, active)
    for obj in review.objects:
        if not obj.ref or obj.ref.object_kind != "revision" or obj.status == "contract_error": continue
        d = obj.data
        impact(obj.ref.object_id, d["revision_kind"], d["disposition"], {_node(r) for r in d["affected_refs"]},
               d["disposition"] in {"received", "provisional", "applied"})
    return tuple(sorted(links)), tuple(impacts)


def _revisions(review, bundle):
    rows = []
    for obj in review.objects:
        if not obj.ref or obj.ref.object_kind != "revision" or obj.status == "contract_error": continue
        d = obj.data; reasons = [i.code for i in obj.issues]
        available = tuple(sa._artifact_available(bundle, r) for r in d["original_refs"])
        if not d["original_refs"]: reasons.append("revision_original_material_missing")
        if not all(available): reasons.append("revision_original_material_unavailable")
        rows.append(RevisionRecord(obj.ref, d["revision_kind"], d["event_type"], d["disposition"],
            d["old_identity"], d["new_identity"], tuple(lr._key(r) for r in d["affected_refs"]),
            tuple(d["original_refs"]), available, d["evidence"], _reasons(reasons)))
    return tuple(rows)


def _episode(bundle, review, index, obj, assays, impacts):
    d = obj.data; role = review.configuration["data_role"]; limits = review.limits
    pre = next((a for a in assays.assays if a.ref == lr._key(d["pre_assay_ref"])), None)
    post = next((a for a in assays.assays if a.ref == lr._key(d["post_assay_ref"])), None)
    intervention = _resolve(review, d["intervention_ref"])
    prestate = _resolve(review, vars(pre.state_ref)) if pre and pre.state_ref else None
    poststate = _resolve(review, vars(post.state_ref)) if post and post.state_ref else None
    context = context_fingerprint(d, bundle)
    subject = evidence_subject_fingerprint(d, bundle)
    reggate, witness = _registration(index, review, d, context, [prestate, poststate])
    compatibility = _compatibility(review, index, obj, pre, post, intervention, witness)
    configgate, flags, identities = _configuration(review, intervention, witness)
    gates = [reggate, compatibility, configgate,
             _gate("episode_record", (i.code for i in obj.issues))]
    ip = intervention.data if intervention else None
    refs = tuple(ip["external_refs"]) if ip else ()
    source_reasons, source_mock = _inspect(index, refs, "source", role, limits); source_reasons = list(source_reasons)
    if not refs: source_reasons.append("recovery_external_material_missing")
    source_rows = []
    for ref in refs:
        rec = index.resolve(ref)
        if rec: source_rows.append(rec.data)
        payload = index.payload(_core_key(ref))
        if payload and any(not _nonblank(_value(payload[k])) for k in ("origin", "knowledge_type")):
            source_reasons.append("recovery_source_origin_or_knowledge_type_unknown")
    if not any(r["record_type"] in {"source", "evidence"} for r in refs): source_reasons.append("recovery_external_source_lineage_missing")
    gates.append(_gate("source", source_reasons, refs, source_mock))
    grounding_refs = tuple(ip["evidence"]["independence"]) if ip else ()
    grounding, _ = _scoped_gate(index, grounding_refs, "grounding", d, context, role, limits, subject=subject)
    # The IA identifies material and evaluation subjects explicitly. A vendor
    # name cannot substitute for an ancestry/structural-grounding review.
    grounding_reasons = list(grounding.reasons)
    exposure_refs = witness.get("permitted_exposure_refs", ()) if isinstance(witness, Mapping) else ()
    evaluation_refs = witness.get("evaluation_material_refs", ()) if isinstance(witness, Mapping) else ()
    permitted_keys = {_core_key(r) for r in refs + tuple(exposure_refs)}
    evaluation_keys = {_core_key(r) for r in evaluation_refs}
    for r in grounding_refs:
        p = index.payload(_core_key(r))
        if p and (p.get("left_ref") is None or p.get("right_ref") is None or
                  not ({_core_key(p["left_ref"]), _core_key(p["right_ref"])} & permitted_keys) or
                  not ({_core_key(p["left_ref"]), _core_key(p["right_ref"])} & evaluation_keys)):
            grounding_reasons.append("grounding_subject_scope_mismatch")
    gates.append(_gate("grounding", grounding_reasons, grounding_refs, grounding.mock_evidence))
    nr = _value(d["non_injection_ref"])
    ng, _ = _scoped_gate(index, (nr,) if nr else (), "non_injection", d, context, role, limits, subject=subject)
    vg, _ = _scoped_gate(index, d["external_validation_refs"], "external_validation", d, context, role, limits, subject=subject)
    gates += [ng, vg]
    stages = []
    for name in STAGES:
        stage_refs = []
        for r in d["evidence"]["process"]:
            p = index.payload(_core_key(r)); w = p.get("extensions", {}).get(EVIDENCE_KEY) if p else None
            if isinstance(w, Mapping) and w.get("role") == name: stage_refs.append(r)
        # Entry, actual exposure and expression are indispensable. An explicit
        # no-preprocessing/no-selection record can represent an omitted stage.
        gate, outcomes = _scoped_gate(index, stage_refs, name, d, context, role, limits, allow_na=name in {"preprocessing", "selection"}, subject=subject)
        status = "unavailable" if gate.reasons else "not_applicable" if outcomes and outcomes[0] == "not_applicable" else "supported_for_scope"
        stages.append(ExogamyStage(name, status, gate, tuple(index.get(_core_key(r)).data for r in stage_refs if index.get(_core_key(r)))))
        gates.append(gate)
    impacted = [x for x in impacts if _node(obj.ref) in x.dependent_nodes]
    correction_reasons = []
    for impact in impacted:
        if impact.effect == "schema": correction_reasons.append("recovery_recut_requires_new_common_schema_assignments")
        elif impact.effect in {"membership", "validity", "lineage"}: correction_reasons.append("recovery_affected_inputs_require_reanalysis")
        elif impact.effect == "independence": correction_reasons.append("recovery_independence_claim_under_correction")
        elif impact.effect == "metadata": correction_reasons.append("recovery_metadata_claim_under_correction")
    gates.append(_gate("correction", correction_reasons))
    pre_present = pre.present_classes if pre else ()
    pre_below = pre.below_classes if pre else ()
    classes = pre.classes if pre else ()
    pre_unresolved = tuple(c for c in classes if c not in set(pre_present) | set(pre_below))
    missing = tuple(c for c in classes if c in pre_below) if pre and classes and not pre_unresolved and set(classes) == set(pre_present) | set(pre_below) else None
    recovered = tuple(c for c in missing or () if post and c in post.present_classes)
    post_below = tuple(c for c in missing or () if post and c in post.below_classes)
    unresolved = tuple(c for c in missing or () if c not in set(recovered) | set(post_below))
    if compatibility.status != "eligible":
        # Incompatible assays retain separate sets, without calling an
        # intersection under changed meanings confirmed recovered support.
        recovered = (); post_below = (); unresolved = missing or ()
    reasons = [r for g in gates for r in g.reasons]
    value = None; bounds = None; status = "unavailable"
    if missing is None: reasons.append("pre_missing_reference_set_unresolved")
    elif not missing:
        status = "undefined"; reasons.append("empty_missing_reference_set")
    elif compatibility.status != "eligible": reasons.append("recovery_comparison_unavailable")
    elif unresolved:
        reasons.append("post_missing_class_status_unresolved")
        bounds = (Fraction(len(recovered), len(missing)), Fraction(len(recovered) + len(unresolved), len(missing)))
    elif not reasons:
        status = "available"; value = Fraction(len(recovered), len(missing))
    if missing == () and compatibility.status != "eligible": status = "unavailable"
    fixture = role == "fixture" or any(g.mock_evidence for g in gates) or any(a and a.evidence_status == "fixture_only" for a in (pre, post))
    evidence_status = "fixture_only" if fixture else "supplied_evidence_conditional"
    quantity = Quantity("external_recovery_rate", value, status, reasons=_reasons(reasons),
        qualifiers=QUALIFIERS + (("fixture_only",) if fixture else ()), uncertainty_status="finite_family_assay_decisions_with_episode_bonferroni_allocation")
    return RecoveryEpisode(obj.ref, status, quantity, _reasons(reasons), pre, post, pre_present, pre_below,
        pre_unresolved, missing, recovered, post_below, unresolved, bounds, tuple(gates), tuple(stages),
        *flags, pre.state_ref if pre else None, post.state_ref if post else None, intervention.ref if intervention else None,
        identities, tuple(source_rows), freeze(witness), evidence_status,
        "new_model_state_expression" if flags[0] is True else "assisted_system_expression")


def evaluate_recovery(bundle: LoadedBundle, *, review=None, assays=None, observed=None, fits=None) -> RecoveryStudy:
    """Compute only record-derived finite-family ERR, checking all supplied inputs."""
    _require(isinstance(bundle, LoadedBundle), "loaded_bundle_required")
    fresh = lr.review_longitudinal(bundle)
    if review is not None:
        if fresh.configuration is not None: lr.assert_current(review, bundle)
        _require(review == fresh, "altered_longitudinal_binding")
    current_assays = sa.evaluate_support_assays(bundle)
    if assays is not None:
        sa.assert_current(assays, bundle); _require(assays == current_assays, "altered_support_assay_context")
    current_observed = None; current_fits = None
    if observed is not None or fits is not None:
        current_observed = lg.observe_longitudinal(bundle)
    if observed is not None:
        lg.assert_current(observed, bundle); _require(observed == current_observed, "altered_observed_recovery_context")
    if fits is not None:
        hl.assert_current(fits, bundle); current_fits = hl.fit_half_lives(bundle, observed=current_observed)
        _require(fits == current_fits, "altered_half_life_recovery_context")
    if not fresh.requested or fresh.configuration is None:
        return RecoveryStudy(fresh.requested, fresh.status, fresh.input_context_sha256, fresh,
            reasons=tuple(i.code for i in fresh.issues), assays=current_assays, observed=current_observed, fits=current_fits)
    index = EvidenceIndex(bundle); revisions = _revisions(fresh, bundle)
    try: dependencies, impacts = _dependencies(bundle, fresh, index)
    except InputError as exc:
        return RecoveryStudy(True, "unavailable", fresh.input_context_sha256, fresh, revisions=revisions,
            reasons=(exc.code,), assays=current_assays, observed=current_observed, fits=current_fits)
    if "recovery" not in fresh.configuration["capabilities"]:
        return RecoveryStudy(False, "not_requested", fresh.input_context_sha256, fresh, revisions=revisions,
            dependencies=dependencies, correction_impacts=impacts, assays=current_assays, observed=current_observed, fits=current_fits)
    rows = [o for o in fresh.objects if o.ref and o.ref.object_kind == "recovery_episode" or o.locator.startswith(lr.BASE + "/recovery_episodes/")]
    results = []
    for obj in rows:
        try:
            _require(obj.ref is not None and obj.status != "contract_error", "recovery_episode_contract_error")
            results.append(_episode(bundle, fresh, index, obj, current_assays, impacts))
        except (InputError, KeyError, TypeError, ValueError, AttributeError) as exc:
            reasons = (getattr(exc, "code", "recovery_binding_error"),)
            results.append(RecoveryEpisode(obj.ref, "unavailable", Quantity("external_recovery_rate", reasons=reasons), reasons))
    status = "not_requested" if not rows else "available" if all(r.status == "available" for r in results) else "available_with_limitations"
    return RecoveryStudy(bool(rows), status, fresh.input_context_sha256, fresh, tuple(results), revisions, dependencies,
        impacts, _reasons(r for result in results for r in result.reasons), current_assays, current_observed, current_fits)


def assert_current(study: RecoveryStudy, bundle: LoadedBundle) -> None:
    _require(isinstance(study, RecoveryStudy) and study.input_context_sha256 == lr.input_fingerprint(bundle), "stale_recovery_context")
