"""Exact, finite-family threshold assays on the immutable loaded snapshot.

PHASE_3_PLAN sections 6 and 8.6 and Appendix C. All probability statements
are conditional on supplied fixed-design, independent-call and label evidence.
No sampling, candidate execution, acquisition, latent extinction or recovery.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, replace
from datetime import datetime
from fractions import Fraction
import hashlib
from math import comb, gcd
from typing import Any, Mapping

from .contracts import CLASS_IDS, InputError, freeze, is_id, knowledge, validate_ref
from .comparison_records import configuration_fingerprint
from .evidence import EvidenceIndex
from .local_io import LoadedBundle
from .inventory import _association
from .categorical_null import Quantity, _Exact, _Limit, _limits, _number
from .half_life import support_gate as _base_support_gate
from . import longitudinal as lg, longitudinal_records as lr

METHOD = "finite_family_binomial_threshold_v1"
REGISTRATION_KEY = "support_assay_registration_v1"
IID_KEY = "support_assay_iid_v1"
FAILURE_KEY = "support_assay_failure_v1"
ASSUMPTIONS = ("independent_calls", "fixed_state", "fixed_intervention",
               "no_adaptive_stopping", "no_reused_continuations", "complete_trial_inventory")
QUALIFIERS = ("finite_family_scope", "registered_reference_classes",
              "conditional_on_supplied_sampling_and_label_evidence", "not_latent_repertoire",
              "below_threshold_is_not_zero_probability")


def _require(ok, code):
    if not ok:
        raise InputError(code)


def _reasons(items):
    return tuple(sorted(set(items)))


def _value(tag):
    k = knowledge(tag)
    return k.value if k.state == "known" else None


def _oref(row):
    return {k: row[k] for k in ("object_kind", "object_id", "object_version")}


def _copy_plain(value):
    if isinstance(value,Mapping): return {k:_copy_plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [_copy_plain(v) for v in value]
    return value


def _resolve(review, ref):
    return review.get(ref["object_kind"], ref["object_id"], ref["object_version"])


def support_gate(index, ref, role, data_role, limits):
    """Retain prior checks and verify declared decisive artifact snapshots."""
    reasons = list(_base_support_gate(index,ref,role,data_role,limits))
    pending = [ref] if ref else []; seen = set()
    while pending:
        item = pending.pop()
        try:
            validate_ref(item); key = (item["record_type"],item["record_id"])
        except (InputError,TypeError,KeyError):
            reasons.append(role+"_artifact_reference_invalid"); continue
        if key in seen: continue
        seen.add(key)
        if len(seen) > limits["max_link_objects"]:
            reasons.append(role+"_evidence_limit"); break
        if key[0] in {"artifact","raw_artifact"}:
            if not _artifact_available(index.bundle,item): reasons.append(role+"_artifact_unavailable")
            continue
        payload = index.payload(key)
        if payload:
            for field in ("evidence_refs","reviewer_refs","artifact_refs","material_refs"):
                pending.extend(payload.get(field,()))
    return _reasons(reasons)


@dataclass(frozen=True)
class CellDecision:
    N: int
    k_confirmed: int
    k_possible: int
    tau: Fraction | None
    alpha: Fraction | None
    J: int
    delta: Fraction | None
    upper_tail: Fraction | None
    lower_tail: Fraction | None
    status: str
    reasons: tuple[str, ...] = ()
    tail_summands: int = 0
    method: str = METHOD
    qualifiers: tuple[str, ...] = QUALIFIERS


@dataclass(frozen=True)
class TrialResult:
    trial_id: str
    status: str
    sample_ref: Any
    attempt_ref: Any
    measurement_ref: Any
    candidate_position: int
    outcome: str
    attempted: bool
    completed: bool
    reasons: tuple[str, ...] = ()
    gate_reasons: tuple[str, ...] = ()
    class_id: str | None = None
    validity: str | None = None
    mock_evidence: bool = False
    locator: str = ""


@dataclass(frozen=True)
class AssayCell:
    class_id: str
    intervention_ref: lr.ObjectRef
    decision: CellDecision
    trials: tuple[TrialResult, ...]
    planned_count: int
    attempted_count: int
    completed_count: int
    missing_count: int
    status: str
    reasons: tuple[str, ...] = ()

    @property
    def N(self):
        return self.decision.N

    @property
    def k_confirmed(self):
        return self.decision.k_confirmed

    @property
    def k_possible(self):
        return self.decision.k_possible


@dataclass(frozen=True)
class ClassResult:
    class_id: str
    status: str
    intervention_statuses: tuple[tuple[lr.ObjectRef, str], ...]
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssayResult:
    ref: lr.ObjectRef
    state_ref: lr.ObjectRef | None
    family_id: str | None
    family_version: str | None
    success_event: str | None
    class_universe_ref: Any
    classes: tuple[str, ...]
    intervention_refs: tuple[lr.ObjectRef, ...]
    cells: tuple[AssayCell, ...]
    class_results: tuple[ClassResult, ...]
    present_classes: tuple[str, ...]
    below_classes: tuple[str, ...]
    unresolved_classes: tuple[str, ...]
    unavailable_classes: tuple[str, ...]
    observed_intervention_union: tuple[str, ...]
    observed_intervention_union_size: Quantity
    expressible_support_size_finite_family: Quantity
    reference_normalized_support: Quantity
    size_bounds: tuple[int, int]
    tau: Fraction | None
    alpha: Fraction | None
    J: int
    delta: Fraction | None
    status: str
    reasons: tuple[str, ...]
    evidence_status: str
    registration_ref: Any = field(repr=False)
    iid_evidence_ref: Any = field(repr=False)
    design_sha256: str | None = None
    finite_family_scope: bool = True
    coverage_scope: str = "registered_reference_classes"
    semantic_success_event: str | None = None
    qualifiers: tuple[str, ...] = QUALIFIERS
    substantive_validation_performed: bool = False
    latent_support_established: bool = False
    model_recovery_established: bool = False


@dataclass(frozen=True)
class SupportAssayStudy:
    requested: bool
    status: str
    input_context_sha256: str | None
    review: lr.LongitudinalReview = field(repr=False)
    assays: tuple[AssayResult, ...] = ()
    reasons: tuple[str, ...] = ()
    J: int = 0
    tail_summands: int = 0
    limits: Any = field(default=None, repr=False)
    method: str = METHOD
    substantive_validation_performed: bool = False
    finite_family_scope: bool = True


class _Work:
    def __init__(self, limits):
        self.limits = limits
        self.summands = 0

    def consume(self, n):
        if self.summands + n > self.limits["max_tail_summands"]:
            raise _Limit()
        self.summands += n


def _compare(x, y, a, strict=False):
    # Cancel common factors before constructing exact comparison products.
    g = gcd(x.numerator, y.numerator)
    h = gcd(x.denominator, y.denominator)
    if not g:
        return False if strict else True
    left = a.product(x.numerator // g, y.denominator // h)
    right = a.product(y.numerator // g, x.denominator // h)
    return left < right if strict else left <= right


def _tails(N, kL, kU, tau, arithmetic, work):
    count = N-kL+1+kU+1
    work.consume(count)
    if tau == 1:
        return Fraction(1), Fraction(int(kU == N)), count
    b, p = tau.denominator, tau.numerator
    q = b-p
    # This conservative preflight bounds each pow before its construction.
    if N * b.bit_length() > arithmetic.bits:
        raise _Limit()
    denominator = arithmetic.integer(pow(b, N))
    def tail(indices):
        total = 0
        for k in indices:
            coefficient = arithmetic.integer(comb(N, k))
            left = arithmetic.integer(pow(p, k))
            right = arithmetic.integer(pow(q, N-k))
            term = arithmetic.product(arithmetic.product(coefficient, left), right)
            total = arithmetic.integer(total + term)
        return arithmetic.fraction(Fraction(total, denominator))
    return tail(range(kL, N+1)), tail(range(kU+1)), count


def binomial_threshold(N, k_confirmed, k_possible, *, tau, alpha, J, limits=None,
                       _work=None) -> CellDecision:
    """Exact component arithmetic, conditional on caller-supplied valid k bounds.

    Invalid types/counts raise InputError. Resource refusal is an unavailable
    result, with no normal approximation or substituted sampling parameters.
    This direct arithmetic helper does not establish sampling eligibility.
    """
    lim = _limits(limits)
    _require(type(N) is int and 0 <= N <= lim["max_trials_per_cell"], "assay_trial_count_or_limit")
    _require(type(k_confirmed) is int and type(k_possible) is int and
             0 <= k_confirmed <= k_possible <= N, "assay_success_bounds_invalid")
    _require(type(J) is int and 1 <= J <= lim["max_link_objects"], "assay_multiplicity_invalid")
    a = _Exact(lim); t = al = delta = None
    work = _work if _work is not None else _Work(lim)
    before = work.summands
    try:
        t = _number(tau, a); al = _number(alpha, a)
        _require(0 < t <= 1, "assay_tau_invalid")
        _require(0 < al < 1, "assay_alpha_invalid")
        delta = a.div(al, Fraction(a.integer(2*J)))
        if not N:
            return CellDecision(N, k_confirmed, k_possible, t, al, J, delta, None, None,
                                "unavailable", ("untested_intervention",))
        upper, lower, used = _tails(N, k_confirmed, k_possible, t, a, work)
        status = ("threshold_present" if _compare(upper, delta, a) else
                  "threshold_below" if _compare(lower, delta, a, strict=True) else "unresolved")
        reasons = ("tau_one_cannot_establish_probability_one",) if t == 1 and status == "unresolved" else ()
        return CellDecision(N, k_confirmed, k_possible, t, al, J, delta, upper, lower, status, reasons, used)
    except InputError as exc:
        if isinstance(exc, _Limit) or "exponent_limit" in exc.code:
            return CellDecision(N, k_confirmed, k_possible, t, al, J, delta, None, None,
                                "unavailable", ("assay_exact_resource_limit",), work.summands-before)
        raise


def design_fingerprint(assay) -> str:
    """Hash the prespecified criterion/family/state; omit measured outcomes."""
    keys = ("object_kind", "object_id", "object_version", "state_ref", "family_id", "family_version",
            "intervention_refs", "success_event", "registry_ref", "tau", "alpha", "allocation")
    return configuration_fingerprint({k: assay[k] for k in keys})


def _artifact_hashes(bundle):
    return {a.record_key:a.actual_sha256 for a in bundle.artifacts if _artifact_available(bundle,
        dict(record_type=a.record_key.split(":",1)[0],record_id=a.record_key.split(":",1)[1],record_version="0.1"))}


def _context_fingerprint(assay, slots, configuration, core_records, artifact_hashes=None):
    """Bind design contents while excluding observed samples and trial outcomes."""
    if configuration is None or core_records is None:
        return None
    references = [assay["state_ref"], *assay["intervention_refs"], *[s["measurement_ref"] for s in slots]]
    references = {lr._key(r) for r in references}
    rows = [r for name in ("states", "interventions", "measurements") for r in configuration[name]]
    result = []; core_refs = set()
    for ref in sorted(references, key=lambda r: (r.object_kind,r.object_id,r.object_version)):
        found = [r for r in rows if lr._key(r) == ref]
        _require(len(found) == 1, "assay_context_identity_unavailable")
        row = dict(found[0])
        if ref.object_kind == "measurement":
            for key in ("sample_refs", "evidence"):
                row.pop(key, None)
            for key in ("cell_ref", "frame_ref", "protocol_ref", "registry_ref"):
                r = row[key]; core_refs.add((r["record_type"],r["record_id"]))
        elif ref.object_kind == "state":
            for key in ("measurement_refs", "evidence", "ancestor_refs", "state_time"):
                row.pop(key, None)
        result.append(row)
    core_refs.add((assay["registry_ref"]["record_type"],assay["registry_ref"]["record_id"]))
    prompt_refs = set()
    for kind, identity in sorted(core_refs):
        found = [r for r in core_records if r.get("record_type") == kind and r.get("record_id") == identity]
        _require(len(found) == 1, "assay_context_core_unavailable")
        result.append(found[0])
        if kind == "protocol":
            prompt = _value(found[0]["conditioning_context_ref"])
            _require(prompt is not None,"assay_context_prompt_unavailable")
            prompt_refs.add((prompt["record_type"],prompt["record_id"]))
    for kind, identity in sorted(prompt_refs):
        key = kind+":"+identity
        found = [r for r in core_records if r.get("record_type") == kind and r.get("record_id") == identity]
        _require(len(found) == 1 and artifact_hashes is not None and key in artifact_hashes,"assay_context_prompt_unavailable")
        result.append(dict(artifact=found[0],snapshot_sha256=artifact_hashes[key]))
    return configuration_fingerprint(result)


def registration_witness(assays, classes, trial_slots, *, configuration=None, core_records=None, artifact_hashes=None, bundle=None) -> dict:
    """Prepare identity fields for an external preregistration workflow.

    `classes` is one ordered registry class sequence, or a map by assay ID.
    `trial_slots` maps assay IDs to the complete preselected call inventory.
    Computing this object does not create, date or validate a registration.
    """
    if bundle is not None:
        _require(isinstance(bundle,LoadedBundle) and bundle.manifest is not None,"loaded_bundle_required")
        configuration = bundle.manifest.data["analysis_config"]["extensions"]["longitudinal"]
        core_records = [e.record.data for e in bundle.records if e.record]
        artifact_hashes = _artifact_hashes(bundle)
    return {"method": METHOD, "inspection_status": "registered_before_inspection", "stages": [
        {"assay_ref": _oref(d), "design_sha256": design_fingerprint(d),
         "classes": list(classes[d["object_id"]] if isinstance(classes, Mapping) else classes),
         "intervention_refs": _copy_plain(d["intervention_refs"]), "trials": _copy_plain(trial_slots[d["object_id"]]),
         "context_sha256": _context_fingerprint(d,trial_slots[d["object_id"]],configuration,core_records,artifact_hashes)} for d in assays]}


def iid_witness(assay) -> dict:
    """Identity-bound assertions for supplied independence evidence, not proof."""
    return {"assay_ref": _oref(assay), "design_sha256": design_fingerprint(assay),
            **{k: True for k in ASSUMPTIONS}}


def _registration(review, index):
    ref = _value(review.configuration["registered_design_ref"])
    reasons = list(support_gate(index, ref, "assay_registration", review.configuration["data_role"], review.limits))
    p = index.payload((ref["record_type"], ref["record_id"])) if ref else None
    w = p.get("extensions", {}).get(REGISTRATION_KEY) if p else None
    try:
        _require(isinstance(w, Mapping) and set(w) == {"method", "inspection_status", "stages"}, "assay_registration_binding_missing")
        _require(w["method"] == METHOD and w["inspection_status"] == "registered_before_inspection", "assay_registration_not_prespecified")
        _require(isinstance(w["stages"], (tuple, list)) and bool(w["stages"]), "assay_registered_stage_inventory_required")
        stages = []; ids = set(); work = 0; J = 0
        for stage in w["stages"]:
            _require(isinstance(stage, Mapping) and set(stage) == {"assay_ref", "design_sha256", "context_sha256", "classes", "intervention_refs", "trials"}, "assay_registered_stage_shape")
            lr._ref("assay")(stage["assay_ref"]); key = lr._key(stage["assay_ref"])
            _require(key not in ids, "assay_registered_stage_duplicate"); ids.add(key)
            lr._hash(stage["design_sha256"])
            classes = stage["classes"]
            _require(isinstance(classes, (tuple,list)) and len(classes) <= len(CLASS_IDS) and all(c in CLASS_IDS for c in classes) and len(classes) == len(set(classes)), "assay_registered_class_universe")
            members = stage["intervention_refs"]
            _require(isinstance(members, (tuple,list)) and 1 <= len(members) <= review.limits["max_interventions_per_assay"], "assay_registered_family_limit")
            for member in members: lr._ref("intervention")(member)
            keys = [lr._key(m) for m in members]
            _require(len(keys) == len(set(keys)), "assay_registered_family_duplicate")
            slots = stage["trials"]
            _require(isinstance(slots, (tuple,list)), "assay_registered_trial_inventory")
            trial_ids = set(); counts = Counter()
            for slot in slots:
                _require(isinstance(slot, Mapping) and set(slot) == {"trial_id", "intervention_ref", "measurement_ref", "attempt_ref", "candidate_position"}, "assay_registered_trial_shape")
                _require(is_id(slot["trial_id"]) and slot["trial_id"] not in trial_ids, "assay_registered_trial_duplicate")
                trial_ids.add(slot["trial_id"]); lr._ref("intervention")(slot["intervention_ref"])
                lr._ref("measurement")(slot["measurement_ref"]); validate_ref(slot["attempt_ref"])
                _require(slot["attempt_ref"]["record_type"] == "attempt", "assay_registered_attempt_required")
                _require(type(slot["candidate_position"]) is int and 1 <= slot["candidate_position"] <= 2**63-1, "assay_candidate_position_invalid")
                k = lr._key(slot["intervention_ref"])
                _require(k in keys, "assay_registered_trial_outside_family")
                counts[k] += 1
            _require(all(n <= review.limits["max_trials_per_cell"] for n in counts.values()), "assay_trial_count_or_limit")
            work += 1 + len(classes)*len(members) + 5*len(slots)
            _require(work <= review.limits["max_link_objects"], "assay_registration_work_limit")
            J += len(classes)*len(members); stages.append(stage)
        return ref, tuple(stages), J, _reasons(reasons)
    except (InputError, KeyError, TypeError) as exc:
        reasons.append(getattr(exc, "code", "assay_registration_malformed"))
        return ref, (), 0, _reasons(reasons)


def _iid(index, assay, role, limits):
    ref = _value(assay["iid_evidence_ref"])
    reasons = list(support_gate(index, ref, "assay_iid", role, limits))
    p = index.payload((ref["record_type"], ref["record_id"])) if ref else None
    if p is None:
        return ref, _reasons(reasons + ["assay_iid_basis_missing"])
    if ref["record_type"] == "independence_assessment":
        if p["outcome"] != "supported_for_scope": reasons.append("assay_independence_not_supported")
    elif p.get("purpose") != "independence" or _value(p["assertion"]) is not True:
        reasons.append("assay_independence_not_supported")
    w = p.get("extensions", {}).get(IID_KEY)
    if not isinstance(w, Mapping) or set(w) != set(iid_witness(assay)):
        reasons.append("assay_iid_binding_missing")
    else:
        expected = iid_witness(assay)
        if w["assay_ref"] != expected["assay_ref"] or w["design_sha256"] != expected["design_sha256"]:
            reasons.append("assay_iid_binding_mismatch")
        reasons += ["assay_assumption_" + k + "_unsupported" for k in ASSUMPTIONS if w[k] is not True]
    return ref, _reasons(reasons)


def _artifact_available(bundle, ref):
    if ref is None: return False
    rows = [a for a in bundle.artifacts if a.record_key == ref["record_type"]+":"+ref["record_id"]]
    if len(rows) != 1 or rows[0].status != "snapshot_read": return False
    artifact = rows[0]; snapshot = bundle.snapshots.get(artifact.snapshot_path)
    return bool(snapshot and snapshot.size_bytes == len(snapshot.content) and
                snapshot.sha256 == artifact.actual_sha256 == hashlib.sha256(snapshot.content).hexdigest() and
                (artifact.expected_sha256 is None or artifact.expected_sha256 == snapshot.sha256))


def _failure(index, bundle, assay, trial, slot, role, limits):
    """A determinate nonexpression needs a scoped declaration and original call."""
    attempt = index.resolve(slot["attempt_ref"])
    if attempt is None or not _artifact_available(bundle, _value(attempt.data["raw_response_ref"])):
        return False
    expected = {"assay_ref": _oref(assay), "trial_id": trial["trial_id"], "attempt_ref": slot["attempt_ref"],
                "success_event": assay["success_event"], "determinate_nonexpression": True}
    for ref in trial["evidence"]["validation"]:
        if ref["record_type"] != "evidence" or support_gate(index, ref, "assay_failure", role, limits): continue
        p = index.payload((ref["record_type"], ref["record_id"]))
        if p and p.get("purpose") == "observation" and _value(p["assertion"]) is True and p.get("extensions", {}).get(FAILURE_KEY) == expected:
            return True
    return False


def _trial(bundle, review, index, assay, trial, slot, duplicate_calls, duplicate_groups, registration_ref):
    reasons = []; gates = []
    sr = _value(trial["sample_ref"]) if trial else None
    measurement = _resolve(review, slot["measurement_ref"])
    attempt = index.resolve(slot["attempt_ref"])
    attempted = bool(attempt and attempt.data["attempt_status"] in {"succeeded", "failed"})
    completed = bool(attempt and attempt.data["attempt_status"] == "succeeded")
    if trial is None:
        gates.append("registered_trial_missing")
    else:
        if trial["intervention_ref"] != slot["intervention_ref"]: gates.append("trial_intervention_not_registered")
        if _value(trial["measurement_ref"]) != slot["measurement_ref"]: gates.append("trial_measurement_not_registered")
        if trial["status"] in {"planned", "missing"}: gates.append("fixed_N_trial_unperformed_or_missing")
        for refs in trial["evidence"].values():
            for ref in refs:
                if ref["record_type"] not in {"artifact", "raw_artifact"}:
                    reasons += list(support_gate(index, ref, "assay_trial", review.configuration["data_role"], review.limits))
    if measurement is None:
        gates.append("assay_measurement_unavailable")
    else:
        md = measurement.data
        gates += [i.code for i in measurement.issues]
        if md["state_ref"] != assay["state_ref"]: gates.append("assay_trial_state_mismatch")
        if md["registry_ref"] != assay["registry_ref"]: gates.append("assay_trial_registry_mismatch")
        if md["view"] != "classified_all": gates.append("assay_requires_unconditioned_trial_view")
        if sr is not None and sr not in (_value(md["sample_refs"]) or ()): gates.append("assay_trial_sample_not_measured")
    if attempt is None:
        gates.append("assay_attempt_unavailable")
    else:
        ad = attempt.data
        if measurement and ad["analysis_cell_id"] != measurement.data["cell_ref"]["record_id"]: gates.append("assay_attempt_cell_mismatch")
        if ad["retry_of"]["state"] != "known" or _value(ad["retry_of"]) is not None: gates.append("assay_reused_or_unknown_continuation")
        if not completed: gates.append("assay_call_not_completed")
        planned = _value(ad["planned_candidate_count"])
        if type(planned) is not int or planned < slot["candidate_position"]: gates.append("assay_candidate_position_outside_call")
        if ad["generation_group_id"]["state"] != "known": gates.append("assay_call_group_unknown")
        if slot["attempt_ref"]["record_id"] in duplicate_calls: gates.append("multiple_trials_from_same_call")
        if _value(ad["generation_group_id"]) in duplicate_groups: gates.append("reused_generation_group")
        call_time = ad.get("extensions", {}).get("call_started_at")
        if call_time is not None:
            rp = index.payload((registration_ref["record_type"], registration_ref["record_id"])) if registration_ref else None
            try:
                start = datetime.fromisoformat(call_time); registered = datetime.fromisoformat(_value(rp["registered_at"]))
                if start.utcoffset() is None or registered.utcoffset() is None: raise ValueError
                if start < registered: gates.append("assay_registration_after_call")
            except (TypeError, ValueError, KeyError): gates.append("assay_call_time_unavailable")
    sample = index.resolve(sr) if sr else None
    class_id = validity = None; mock = False
    if sample is not None:
        sd = sample.data
        association = _association(index,sample)
        gates += list(association.reasons)
        if _value(sd["attempt_id"]) != slot["attempt_ref"]["record_id"]: gates.append("assay_selected_call_mismatch")
        if _value(sd["within_group_index"]) != slot["candidate_position"]: gates.append("assay_selected_position_mismatch")
        if attempt and _value(sd["generation_group_id"]) != _value(attempt.data["generation_group_id"]): gates.append("assay_selected_group_mismatch")
        if measurement and sd["analysis_cell_id"] != measurement.data["cell_ref"]["record_id"]: gates.append("assay_selected_cell_mismatch")
        assign = index.admit("assignment", sample.record_id); valid = index.admit("validity", sample.record_id)
        class_id = assign.outcome if assign.status == "accepted" else None
        validity = valid.outcome if valid.status == "accepted" and valid.outcome in {"valid", "invalid"} else None
        mock = assign.fixture_context or valid.fixture_context
        reasons += list(assign.reasons)
        if assay["success_event"] == "valid_class_membership": reasons += list(valid.reasons)
        for admission in (assign,valid) if assay["success_event"] == "valid_class_membership" else (assign,):
            record = index.get((admission.axis,admission.record_id)) if admission.record_id else None
            if record:
                problems = []
                for ref in record.data["evidence_refs"]:
                    problems += list(support_gate(index,ref,"assay_label",review.configuration["data_role"],review.limits))
                if problems:
                    reasons += problems
                    if admission.axis == "assignment": class_id = None
                    else: validity = None
        # Contradictory completion claims cannot supply an accepted expression.
        if sd["completion_status"] in {"failed", "unknown", "refused"}:
            class_id = validity = None; reasons.append("assay_output_completion_unresolved")
        output_ref = _value(sd["output_ref"])
        if not _artifact_available(bundle,output_ref):
            class_id = validity = None; reasons.append("assay_selected_output_artifact_unavailable")
    else:
        reasons.append("assay_selected_output_unavailable")
    if trial and trial["status"] == "unresolved":
        class_id = validity = None
        reasons.append("assay_trial_outcome_unresolved")
    failure = bool(trial and completed and _failure(index, bundle, assay, trial, slot, review.configuration["data_role"], review.limits))
    if failure and class_id is not None and (assay["success_event"] == "class_membership" or validity == "valid"):
        failure = False; class_id = validity = None
        reasons.append("assay_nonexpression_conflicts_with_accepted_expression")
    if failure:
        is_refusal = sample is not None and sample.data["completion_status"] == "refused"
        is_no_output = sample is None and trial["status"] == "failed" and trial["sample_ref"]["state"] == "known" and _value(trial["sample_ref"]) is None
        if not (is_refusal or is_no_output):
            failure = False
            reasons.append("assay_nonexpression_without_refusal_or_no_output")
    # Evidence defects affect labels, not the registered denominator. They can
    # never turn unreadable validation into a definite failed Bernoulli event.
    if any(r.startswith("assay_trial_") for r in reasons): class_id = validity = None; failure = False
    outcome = "failure" if failure else "unresolved"
    return TrialResult(slot["trial_id"], trial["status"] if trial else "missing", freeze(sr), freeze(slot["attempt_ref"]),
        freeze(slot["measurement_ref"]), slot["candidate_position"], outcome, attempted, completed,
        _reasons(reasons), _reasons(gates), class_id, validity, mock,
        "registered_design/"+assay["object_id"]+"/trials/"+slot["trial_id"])


def _class_trial(trial, class_id, event):
    if trial.outcome == "failure": return trial
    if event == "valid_class_membership" and trial.validity == "invalid": outcome = "failure"
    elif trial.class_id is None: outcome = "unresolved"
    elif trial.class_id != class_id: outcome = "failure"
    elif event == "class_membership" or trial.validity == "valid": outcome = "success"
    else: outcome = "unresolved"
    return replace(trial, outcome=outcome)


def _assay(bundle, review, index, binding, stage, J, reg_ref, reg_reasons, work, duplicate_calls, duplicate_groups):
    d = binding.data; reasons = list(reg_reasons)
    reasons += [i.code for i in binding.issues if not "/trials/" in i.locator]
    classes = tuple(stage["classes"]); members = tuple(lr._key(x) for x in stage["intervention_refs"])
    if stage["design_sha256"] != design_fingerprint(d) or stage["intervention_refs"] != d["intervention_refs"]:
        reasons.append("assay_registration_design_mismatch")
    try:
        current_context = _context_fingerprint(d,stage["trials"],review.configuration,
            [e.record.data for e in bundle.records if e.record],_artifact_hashes(bundle))
        if stage.get("context_sha256") != current_context:
            reasons.append("assay_registration_context_mismatch")
    except InputError as exc:
        reasons.append(exc.code)
    registry = index.resolve(d["registry_ref"])
    if registry is None:
        reasons.append("assay_registry_unavailable")
    else:
        actual = tuple(x["structural_class_id"] for x in registry.data["classes"])
        if actual != classes: reasons.append("assay_registered_registry_mismatch")
        if index.affected(("reference_registry", registry.record_id), {"schema", "registry", "metadata"}): reasons.append("assay_registry_under_correction")
    state = _resolve(review, d["state_ref"])
    if state is None or state.data["state_kind"] != "model_system": reasons.append("assay_fixed_model_state_required")
    else:
        identity = _value(state.data["subject_identity"])
        if identity is None or any(not lg._knowledge_resolved(identity[k]) for k in ("parameter_identity", "serving_identity", "retrieval_identity", "tool_identity", "system_identity")):
            reasons.append("assay_model_identity_unresolved")
        reasons += [i.code for i in state.issues]
    reasons += list(lg._registration(index, reg_ref, [state], data_role=review.configuration["data_role"]).reasons)
    iid_ref, iid_reasons = _iid(index, d, review.configuration["data_role"], review.limits); reasons += list(iid_reasons)
    listed = {t["trial_id"]: t for t in d["trials"]}
    expected = {t["trial_id"] for t in stage["trials"]}
    if set(listed)-expected: reasons.append("unregistered_assay_trials")
    if len(listed) != len(d["trials"]): reasons.append("duplicate_assay_trial_identity")
    # One episode has one common alpha. It is checked by the caller.
    calls = {}; base_trials = []
    for slot in stage["trials"]:
        tr = _trial(bundle, review, index, d, listed.get(slot["trial_id"]), slot, duplicate_calls, duplicate_groups, reg_ref)
        base_trials.append((lr._key(slot["intervention_ref"]), tr))
    cells = []; results = []; observed = set()
    tau = alpha = delta = None
    for member in members:
        md = _resolve(review, vars(member)); local = list(reasons)
        if md is None: local.append("assay_intervention_unavailable")
        else:
            local += [i.code for i in md.issues]
            x = md.data
            if x["pre_state_ref"] != d["state_ref"] or x["post_state_ref"] != d["state_ref"]:
                local.append("assay_intervention_changed_state")
            if x["intervention_kind"] == "training" or _value(x["parameters_changed"]) is not False:
                local.append("assay_intervention_not_fixed_model")
        trials = tuple(t for m,t in base_trials if m == member)
        local += [r for t in trials for r in t.gate_reasons]
        protocols = set()
        for t in trials:
            measurement = _resolve(review,t.measurement_ref)
            if measurement:
                cell = index.resolve(measurement.data["cell_ref"])
                if cell:
                    signature = {k:cell.data[k] for k in ("frame_id","generation_protocol_id","generation_protocol_version",
                        "prompt_block_id","prompt_id","condition_id","model_identifier","checkpoint_identifier")}
                    protocols.add(configuration_fingerprint(signature))
        if len(protocols) > 1: local.append("assay_intervention_protocol_not_stationary")
        for class_id in classes:
            ct = tuple(_class_trial(t, class_id, d["success_event"]) for t in trials)
            kL = sum(t.outcome == "success" for t in ct); kU = sum(t.outcome != "failure" for t in ct)
            if any(t.outcome == "success" and not t.gate_reasons for t in ct): observed.add(class_id)
            try:
                if local:
                    a = _Exact(review.limits); t = _number(d["tau"],a); al = _number(d["alpha"],a)
                    _require(0 < t <= 1 and 0 < al < 1, "assay_probability_invalid")
                    per_tail = a.div(al,Fraction(a.integer(2*J))) if J else None
                    dec = CellDecision(len(ct),kL,kU,t,al,J,per_tail,None,None,"unavailable",_reasons(local))
                else:
                    dec = binomial_threshold(len(ct), kL, kU, tau=d["tau"], alpha=d["alpha"], J=J, limits=review.limits, _work=work)
            except InputError as exc:
                dec = CellDecision(len(ct), kL, kU, None, None, J, None, None, None, "unavailable", (exc.code,))
            tau, alpha, delta = dec.tau, dec.alpha, dec.delta
            cells.append(AssayCell(class_id, member, dec, ct, len(ct), sum(t.attempted for t in ct), sum(t.completed for t in ct),
                                   sum(not t.completed or t.status in {"missing", "planned"} for t in ct), dec.status, dec.reasons))
    # Empty registries have an exact empty registered support, but require gates.
    if not classes:
        try:
            arithmetic = _Exact(review.limits); tau = _number(d["tau"], arithmetic); alpha = _number(d["alpha"], arithmetic)
            _require(0 < tau <= 1 and 0 < alpha < 1, "assay_probability_invalid")
            delta = arithmetic.div(alpha, Fraction(2*J)) if J else None
        except InputError as exc: reasons.append(exc.code)
    for c in classes:
        cc = [x for x in cells if x.class_id == c]; statuses = [x.status for x in cc]
        status = ("threshold_present" if "threshold_present" in statuses else "threshold_below" if all(s == "threshold_below" for s in statuses)
                  else "unavailable" if all(s == "unavailable" for s in statuses) else "unresolved")
        results.append(ClassResult(c, status, tuple((x.intervention_ref, x.status) for x in cc), _reasons(r for x in cc for r in x.reasons)))
    present = tuple(x.class_id for x in results if x.status == "threshold_present")
    below = tuple(x.class_id for x in results if x.status == "threshold_below")
    unresolved = tuple(x.class_id for x in results if x.status == "unresolved")
    unavailable = tuple(x.class_id for x in results if x.status == "unavailable")
    complete = not unresolved and not unavailable and not reasons
    size = Quantity("expressible_support_size_finite_family", len(present) if complete else None,
                    "available" if complete else "unavailable", "classes", () if complete else ("registered_class_statuses_not_resolved",), QUALIFIERS)
    norm = Quantity("reference_normalized_support", Fraction(len(present),len(classes)) if complete and classes else None,
                    "undefined" if not classes else "available" if complete else "unavailable", reasons=("empty_reference_registry",) if not classes else () if complete else ("registered_class_statuses_not_resolved",), qualifiers=QUALIFIERS)
    status = "available" if complete else "available_with_limitations"
    all_reasons = _reasons(reasons + [r for x in cells for r in x.reasons])
    return AssayResult(binding.ref, lr._key(d["state_ref"]), d["family_id"], d["family_version"], d["success_event"], d["registry_ref"], classes, members,
        tuple(cells), tuple(results), present, below, unresolved, unavailable, tuple(c for c in classes if c in observed),
        Quantity("observed_intervention_union_size", len(observed), "available", "classes", qualifiers=("finite_observed_union_only",)),
        size, norm, (len(present),len(classes)-len(below)), tau, alpha, J, delta, status, all_reasons,
        "fixture_only" if review.configuration["data_role"] == "fixture" or binding.mock_evidence else "conditional_on_supplied_evidence",
        freeze(reg_ref), freeze(iid_ref), design_fingerprint(d), semantic_success_event="valid_class_expression" if d["success_event"] == "valid_class_membership" else "class_membership")


def _missing(stage, J, ref, reasons):
    classes = tuple(stage["classes"]); members = tuple(lr._key(m) for m in stage["intervention_refs"])
    quantity = Quantity("expressible_support_size_finite_family", reasons=reasons, qualifiers=QUALIFIERS)
    return AssayResult(lr._key(stage["assay_ref"]), None, None, None, None, None, classes, members, (),
        tuple(ClassResult(c,"unavailable",tuple((m,"unavailable") for m in members),reasons) for c in classes),
        (), (), (), classes, (), Quantity("observed_intervention_union_size", reasons=reasons), quantity,
        Quantity("reference_normalized_support", reasons=reasons), (0,len(classes)), None,None,J,None,"unavailable",reasons,
        "unavailable",freeze(ref),None,stage["design_sha256"])


def evaluate_support_assays(bundle: LoadedBundle, *, review: lr.LongitudinalReview | None = None) -> SupportAssayStudy:
    """Bind complete registered assay inventory to this exact loaded snapshot."""
    _require(isinstance(bundle, LoadedBundle), "loaded_bundle_required")
    fresh = lr.review_longitudinal(bundle)
    if review is not None:
        lr.assert_current(review, bundle); _require(review == fresh, "altered_longitudinal_binding")
    if not fresh.requested or fresh.configuration is None:
        return SupportAssayStudy(fresh.requested, fresh.status, fresh.input_context_sha256, fresh,
                                 reasons=tuple(i.code for i in fresh.issues))
    if "support_assay" not in fresh.configuration["capabilities"]:
        return SupportAssayStudy(True,"not_requested",fresh.input_context_sha256,fresh,reasons=("support_assay_capability_not_declared",),limits=fresh.limits)
    index = EvidenceIndex(bundle); reg_ref, stages, J, reg_reasons = _registration(fresh, index)
    actual = [o for o in fresh.objects if o.ref and o.ref.object_kind == "assay"]
    if not stages:
        if not fresh.configuration["assays"]:
            return SupportAssayStudy(False,"not_requested",fresh.input_context_sha256,fresh,
                                     reasons=("no_assays_requested",),limits=fresh.limits)
        # Descriptive fallback retains admitted declared samples. Inferred call
        # positions here never become a prespecified probability inventory.
        results = []; work = _Work(fresh.limits)
        for obj in actual:
            if obj.status == "contract_error": continue
            d = obj.data; registry = index.resolve(d["registry_ref"])
            classes = tuple(x["structural_class_id"] for x in registry.data["classes"]) if registry else ()
            slots = []
            for tr in d["trials"]:
                sample_ref = _value(tr["sample_ref"]); sample = index.resolve(sample_ref) if sample_ref else None
                measurement_ref = _value(tr["measurement_ref"])
                if measurement_ref is None: continue
                aid = _value(sample.data["attempt_id"]) if sample else None
                position = _value(sample.data["within_group_index"]) if sample else None
                slots.append(dict(trial_id=tr["trial_id"],intervention_ref=tr["intervention_ref"],measurement_ref=measurement_ref,
                    attempt_ref=dict(record_type="attempt",record_id=aid or "unavailable:"+tr["trial_id"],record_version="0.1"),
                    candidate_position=position or 1))
            stage = freeze(dict(assay_ref=vars(obj.ref),design_sha256=design_fingerprint(d),context_sha256=None,
                               classes=classes,intervention_refs=d["intervention_refs"],trials=slots))
            results.append(_assay(bundle,fresh,index,obj,stage,0,reg_ref,reg_reasons or ("assay_registration_unavailable",),work,set(),set()))
        return SupportAssayStudy(True,"unavailable",fresh.input_context_sha256,fresh,
            tuple(results),reg_reasons,J,limits=fresh.limits)
    registered = {lr._key(s["assay_ref"]) for s in stages}
    extra = [o for o in actual if o.ref not in registered]
    if extra: reg_reasons = _reasons(reg_reasons + ("assay_outside_registered_episode",))
    # Alpha is episode-wide; never reduce J to tested or successful stages.
    alphas = []
    for s in stages:
        b = _resolve(fresh,s["assay_ref"])
        if b and b.status != "contract_error":
            try: alphas.append(_number(b.data["alpha"],_Exact(fresh.limits)))
            except InputError: pass
    if len(set(alphas)) > 1: reg_reasons = _reasons(reg_reasons + ("assay_episode_alpha_mismatch",))
    slots = [slot for s in stages for slot in s["trials"]]
    calls = Counter(slot["attempt_ref"]["record_id"] for slot in slots)
    groups = Counter()
    for slot in slots:
        a = index.resolve(slot["attempt_ref"])
        if a and _value(a.data["generation_group_id"]) is not None: groups[_value(a.data["generation_group_id"])] += 1
    duplicate_calls = {k for k,v in calls.items() if v > 1}; duplicate_groups = {k for k,v in groups.items() if v > 1}
    work = _Work(fresh.limits); results = []
    for s in stages:
        b = _resolve(fresh,s["assay_ref"])
        if b is None or b.status == "contract_error":
            results.append(_missing(s,J,reg_ref,("registered_assay_missing_or_malformed",))); continue
        results.append(_assay(bundle,fresh,index,b,s,J,reg_ref,reg_reasons,work,duplicate_calls,duplicate_groups))
    reasons = _reasons(reg_reasons + tuple(r for x in results for r in x.reasons))
    status = "available" if results and all(x.status == "available" for x in results) else "available_with_limitations"
    return SupportAssayStudy(True,status,fresh.input_context_sha256,fresh,tuple(results),reasons,J,work.summands,fresh.limits)


def assert_current(study: SupportAssayStudy, bundle: LoadedBundle) -> None:
    _require(isinstance(study,SupportAssayStudy) and study.input_context_sha256 == lr.input_fingerprint(bundle), "stale_support_assay_context")
