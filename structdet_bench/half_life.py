"""Registered interval and anchored descriptive Gini-Simpson decay.

SI 8.3 supplies the geometric model. The four-state anchored estimator and
residual rule are engineering choices in PHASE_3_PLAN.md 5.1-5.4. No training,
probability-support inference, causal acceleration claim, file or network I/O.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import math
from typing import Any, Mapping

from .contracts import InputError, freeze, is_id
from .comparison_records import configuration_fingerprint
from .evidence import EvidenceIndex
from .local_io import LoadedBundle
from . import longitudinal as lg, longitudinal_records as lr
from .categorical_null import _Exact, _number, _limits, NullScenario

METHOD = "anchored_log_decay_v1"
INTERVAL_METHOD = "endpoint_log_decay_v1"
REGISTRATION_KEY = "longitudinal_half_life_v1"
UNIT = "recursive_rounds"
CAVEATS = ("conditional_descriptive_timescale", "finite_sample_bias_not_corrected",
           "no_causal_acceleration_inference", "independent_validation_not_performed")


@dataclass(frozen=True)
class Estimate:
    name: str
    value: float | None
    status: str
    reasons: tuple[str, ...] = ()
    unit: str = UNIT
    method: str = METHOD
    qualifiers: tuple[str, ...] = CAVEATS


@dataclass(frozen=True)
class Crossing:
    name: str
    status: str
    baseline: Fraction | None
    left_id: str | None = None
    right_id: str | None = None
    left_time: int | None = None
    right_time: int | None = None
    left_value: Fraction | None = None
    right_value: Fraction | None = None
    intervening_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    exact_crossing_time_estimated: bool = False


@dataclass(frozen=True)
class CurveFit:
    state_ids: tuple[str, ...]
    times: tuple[int | None, ...]
    diversities: tuple[Fraction | None, ...]
    slot_statuses: tuple[str, ...]
    measured_indices: tuple[int, ...]
    interval: Estimate
    empirical: Estimate
    half_crossing: Crossing
    first_zero: Crossing
    x: tuple[int, ...] = ()
    log_ratios: tuple[float, ...] = ()
    slope: float | None = None
    fitted_values: tuple[float, ...] = ()
    log_residuals: tuple[float, ...] = ()
    max_abs_log_residual: float | None = None
    residual_criterion: Fraction | None = None
    aggregation: str = "explicit_curve_arithmetic"
    uncertainty_status: str = "not_estimated"
    substantive_validation_performed: bool = False


@dataclass(frozen=True)
class PreparedCurve:
    request_ref: lr.ObjectRef
    trajectory_ref: lr.ObjectRef
    panel_refs: tuple[lr.ObjectRef, ...]
    state_refs: tuple[lr.ObjectRef, ...]
    times: tuple[int | None, ...]
    values: tuple[Fraction | None, ...]
    statuses: tuple[str, ...]
    panel_values: tuple[tuple[Fraction | None, ...], ...]
    measurement_refs: tuple[tuple[lr.ObjectRef | None, ...], ...]
    endpoint_reasons: tuple[str, ...]
    regime_reasons: tuple[str, ...]
    registration_reasons: tuple[str, ...]
    criterion: Any = field(repr=False)
    fit_mode: str = "anchored"
    view: str = "classified_all"
    stage_roles: tuple[str, ...] = ()
    uncertainty_status: str = "not_estimated"
    qualifiers: tuple[str, ...] = CAVEATS


@dataclass(frozen=True)
class FittedRequest:
    ref: lr.ObjectRef | None
    status: str
    reasons: tuple[str, ...]
    prepared: PreparedCurve | None = field(default=None, repr=False)
    fit: CurveFit | None = None
    original: Any = field(default=None, repr=False)


@dataclass(frozen=True)
class HalfLifeStudy:
    requested: bool
    status: str
    input_context_sha256: str | None
    results: tuple[FittedRequest, ...] = ()
    reasons: tuple[str, ...] = ()
    observed: lg.ObservedStudy | None = field(default=None, repr=False)
    method: str = METHOD
    substantive_validation_performed: bool = False


@dataclass(frozen=True)
class NullComparison:
    empirical: Estimate
    null: Any
    null_scenario_id: str
    status: str = "side_by_side_descriptive_only"
    matched_neural_n_inferred: bool = False
    validated_rate_comparison: bool = False
    causal_acceleration_established: bool = False


def _reasons(items):
    return tuple(sorted(set(items)))


def _require(ok, code):
    if not ok:
        raise InputError(code)


def _estimate(name, value=None, status="available", reasons=(), *, method=METHOD):
    if value is not None and (not math.isfinite(value) or value <= 0):
        value, status, reasons = None, "unavailable", tuple(reasons) + ("half_life_numerical_range",)
    return Estimate(name, value, status, _reasons(reasons), method=method)


def _log_ratio(a: Fraction, b: Fraction, exact: _Exact) -> float:
    """Preserve an exact near-one difference before any binary conversion."""
    ratio = exact.div(a, b)
    if ratio == 1:
        return 0.0
    if Fraction(1, 2) <= ratio <= 2:
        difference = exact.add(ratio, Fraction(-1))
        delta = float(difference)
        _require(delta != 0.0, "log_ratio_below_numeric_resolution")
        value = math.log1p(delta)
    else:
        value = math.log(ratio.numerator) - math.log(ratio.denominator)
    _require(math.isfinite(value) and value != 0.0, "log_ratio_numerical_range")
    _require((value > 0) == (ratio > 1), "log_ratio_direction_error")
    return value


def _crossing(ids, times, values, statuses, *, zero=False):
    name = "first_observed_zero_bracket" if zero else "observed_half_crossing_bracket"
    base = values[0] if values else None
    if base is None or base <= 0 or statuses[0] != "available":
        return Crossing(name, "unavailable", base, reasons=("positive_observed_anchor_required",))
    target = Fraction(0) if zero else base / 2
    previous = 0
    for i in range(1, len(values)):
        if statuses[i] != "available" or values[i] is None:
            continue
        if values[i] <= target:
            return Crossing(name, "observed", base, ids[previous], ids[i], times[previous], times[i],
                values[previous], values[i], ids[previous+1:i],
                ("observed_endpoints_only_no_interpolation",) + (("intervening_unobserved_states",) if i-previous > 1 else ()))
        previous = i
    return Crossing(name, "not_observed", base, reasons=("no_observed_crossing_in_declared_window",))


def analyze_curve(times, diversities, *, state_ids, slot_statuses=None, fit_mode="anchored",
                  max_abs_log_residual=None, endpoint_reasons=(), regime_reasons=(),
                  criterion_reasons=(), limits=None, aggregation="explicit_curve_arithmetic") -> CurveFit:
    """Bounded numerical primitive. Supplied curves alone prove no experiment.

    Only explicitly intentionally-unsampled states may be omitted from an
    anchored fit. They remain in the returned schedule and clock. A missing
    expected interior observation blocks the global fit, not valid endpoints.
    """
    lim = _limits(limits); exact = _Exact(lim)
    _require(isinstance(times, (list, tuple)) and isinstance(diversities, (list, tuple))
             and isinstance(state_ids, (list, tuple)), "half_life_curve_sequences_required")
    _require(2 <= len(times) <= lim["max_states"] and len(times) == len(diversities) == len(state_ids), "half_life_curve_dimensions")
    ids = tuple(state_ids)
    _require(all(is_id(x) for x in ids) and len(set(ids)) == len(ids), "half_life_state_identity")
    _require(fit_mode in ("local", "anchored"), "half_life_fit_mode")
    for t in times:
        _require(t is None or type(t) is int and 0 <= t < 2**63, "half_life_round_coordinate")
    vals = tuple(None if d is None else _number(d, exact) for d in diversities)
    _require(all(d is None or 0 <= d <= 1 for d in vals), "half_life_diversity_range")
    statuses = tuple(slot_statuses) if slot_statuses is not None else tuple("missing" if d is None else "available" for d in vals)
    allowed = {"available", "missing", "planned", "intentionally_unsampled", "unavailable", "undefined"}
    _require(len(statuses) == len(vals) and all(type(s) is str and s in allowed for s in statuses), "half_life_slot_status")
    _require(all((s == "available") == (d is not None) for s,d in zip(statuses, vals)), "half_life_slot_value_mismatch")
    endpoint = list(endpoint_reasons); regime = list(regime_reasons); criteria = list(criterion_reasons)
    _require(all(type(s) is str for s in endpoint + regime + criteria), "half_life_reason_type")
    known_times = [t for t in times if t is not None]
    if len(known_times) != len(times): endpoint.append("recursive_coordinate_unknown")
    if any(a > b for a,b in zip(known_times, known_times[1:])): endpoint.append("recursive_clock_reversed")
    if statuses[0] != "available" or statuses[-1] != "available": endpoint.append("endpoint_diversity_unavailable")
    dt = times[-1]-times[0] if times[0] is not None and times[-1] is not None else None
    if dt is not None and dt <= 0: endpoint.append("nonpositive_recursive_distance")
    interval = _estimate("structural_half_life_interval", status="unavailable", reasons=endpoint, method=INTERVAL_METHOD)
    if not endpoint:
        a,b = vals[0], vals[-1]
        why = "zero_starting_diversity" if a == 0 else "zero_ending_diversity" if b == 0 else "no_decay_on_interval" if a == b else "growth_on_interval" if b > a else None
        if why:
            interval = _estimate(interval.name, status="undefined", reasons=(why,), method=INTERVAL_METHOD)
        else:
            try:
                value = dt * math.log(2.0) / _log_ratio(a, b, exact)
                interval = _estimate(interval.name, value, method=INTERVAL_METHOD)
            except (InputError, OverflowError, ValueError, ZeroDivisionError) as e:
                interval = _estimate(interval.name, status="unavailable", reasons=(getattr(e,"code","half_life_numerical_range"),), method=INTERVAL_METHOD)
    measured = tuple(i for i,s in enumerate(statuses) if s != "intentionally_unsampled")
    criterion = None
    if fit_mode == "anchored":
        try:
            criterion = _number(max_abs_log_residual, exact)
            _require(criterion > 0, "positive_residual_criterion_required")
        except (InputError, TypeError, ValueError, OverflowError) as e:
            criteria.append(getattr(e, "code", "positive_residual_criterion_required"))
    empirical = _estimate("structural_half_life_empirical", status="not_requested" if fit_mode == "local" else "unavailable")
    x=(); logs=(); beta=None; fitted=(); residuals=(); maximum=None
    if fit_mode == "anchored":
        failures = list(endpoint) + regime
        if len(measured) < 4: failures.append("at_least_four_registered_measurements_required")
        if any(statuses[i] != "available" for i in measured): failures.append("missing_expected_measurement")
        if any(vals[i] == 0 for i in measured): failures.append("zero_diversity_in_fit_window")
        selected_times = [times[i] for i in measured]
        if any(t is None for t in selected_times): failures.append("fit_time_unavailable")
        elif any(a >= b for a,b in zip(selected_times,selected_times[1:])): failures.append("distinct_measured_rounds_required")
        if failures:
            empirical = _estimate(empirical.name, status="unavailable", reasons=failures+criteria)
        else:
            try:
                x = tuple(times[i]-times[0] for i in measured)
                logs = tuple(_log_ratio(vals[i], vals[0], exact) for i in measured)
                denominator = exact.sum([exact.mul(Fraction(t),Fraction(t)) for t in x[1:]])
                beta = math.fsum(t*y for t,y in zip(x[1:], logs[1:])) / float(denominator)
                _require(math.isfinite(beta), "nonfinite_fitted_slope")
                residuals = tuple(y-beta*t for t,y in zip(x,logs))
                _require(all(math.isfinite(r) for r in residuals), "nonfinite_log_residual")
                maximum = max(abs(r) for r in residuals)
                base_float = float(vals[0]); _require(base_float > 0 and math.isfinite(base_float), "anchor_numeric_underflow")
                fitted = tuple(math.exp(beta*t)*base_float for t in x)
                _require(all(math.isfinite(d) and d > 0 for d in fitted), "fitted_diversity_numeric_range")
                if beta >= 0:
                    empirical = _estimate(empirical.name,status="undefined",reasons=("no_declining_fitted_slope",)+tuple(criteria))
                elif criteria:
                    empirical = _estimate(empirical.name,status="unavailable",reasons=criteria)
                elif Fraction.from_float(maximum) > criterion:
                    empirical = _estimate(empirical.name,status="unavailable",reasons=("non_geometric_registered_residual_exceeded",))
                else:
                    empirical = _estimate(empirical.name,-math.log(2.0)/beta)
            except (InputError, OverflowError, ValueError, ZeroDivisionError) as e:
                empirical = _estimate(empirical.name,status="unavailable",reasons=(getattr(e,"code","half_life_numerical_range"),))
    return CurveFit(ids,tuple(times),vals,statuses,measured,interval,empirical,
        _crossing(ids,times,vals,statuses),_crossing(ids,times,vals,statuses,zero=True),
        x,logs,beta,fitted,residuals,maximum,criterion,aggregation)


def support_gate(index, ref, role, data_role, limits) -> tuple[str,...]:
    """Reuse existing evidence records, retaining actual decisive dependencies."""
    if ref is None:
        return (role+"_reference_missing",)
    todo=[(ref,False)]; active=set(); done=set(); reasons=[]; count=0
    while todo:
        r,exit_=todo.pop()
        try:
            from .contracts import validate_ref, SUPPORT_RECORD_TYPES
            validate_ref(r); key=(r["record_type"],r["record_id"])
        except (InputError, KeyError, TypeError):
            reasons.append(role+"_reference_invalid"); continue
        if exit_: active.discard(key); done.add(key); continue
        if key in active: reasons.append(role+"_circular_support"); continue
        if key in done: continue
        count+=1
        if count > limits["max_link_objects"]: return (role+"_evidence_limit",)
        rec=index.resolve(r)
        if rec is None: reasons.append(role+"_reference_unresolved"); continue
        if key[0] not in SUPPORT_RECORD_TYPES: reasons.append(role+"_support_type_invalid"); continue
        p=index.payload(key)
        if p is None: reasons.append(role+"_payload_unavailable"); continue
        if p["state"]!="active" or p.get("access","readable")!="readable" or p.get("conflict_status")=="unresolved":
            reasons.append(role+"_inactive_unreadable_or_conflicted")
        if data_role!="fixture" and (p["mock"] or p["data_role"]=="fixture"): reasons.append(role+"_mock_for_nonfixture")
        if index.affected(key,{"metadata","independence","schema","membership","validity"}): reasons.append(role+"_under_correction")
        active.add(key); todo.append((r,True))
        for k in ("evidence_refs","reviewer_refs"):
            todo.extend((x,False) for x in p.get(k,()))
    return _reasons(reasons)


def registration_witness(request, trajectory) -> dict:
    """Identity fields to be recorded by an external preregistration workflow.

    Computing these identifiers never creates, dates or validates a registration.
    """
    return {"method":METHOD,"request_ref":{k:request[k] for k in ("object_kind","object_id","object_version")},
            "request_sha256":configuration_fingerprint(request),
            "trajectory_sha256":configuration_fingerprint(trajectory),
            "aggregation":"equal_panel_mean","panel_refs":request["panel_refs"]}


def regime_restrictions(review,selected,panels,trajectory_ref,request_ref):
    """Check every chosen lineage's full requested span, not just the anchor path."""
    selected=tuple(selected); selected_set=set(selected); start=selected[0]; reasons=[]
    for obj in review.objects:
        if not obj.ref or obj.status=="contract_error":continue
        if obj.ref.object_kind=="intervention":
            a,b=lg._ref(obj.data["pre_state_ref"]),lg._ref(obj.data["post_state_ref"])
            if a!=b and a in selected_set and b in selected_set:reasons.append("intervention_inside_unchanged_regime")
        elif obj.ref.object_kind=="transition":
            if lg._ref(obj.data["child_ref"]) in selected_set-{start} and obj.data["external_contribution_refs"]:
                reasons.append("external_contribution_inside_unchanged_regime")
        elif obj.ref.object_kind=="revision" and obj.data["disposition"]=="applied" and obj.data["revision_kind"]=="schema":
            affected={lg._ref(x) for x in obj.data["affected_refs"]}
            if affected & (selected_set|set(panels)|{trajectory_ref,request_ref}):reasons.append("recut_inside_fit_scope")
    return _reasons(reasons)


def prepare_curve(bundle, study, request) -> PreparedCurve:
    review=study.review; d=request.data
    trajectory=lg._resolve(review,d["trajectory_ref"])
    _require(trajectory is not None and trajectory.status!="contract_error","fit_trajectory_unavailable")
    path=tuple(lg._ref(s) for s in trajectory.data["state_refs"])
    start,end,anchor=(lg._ref(d[k]) for k in ("start_ref","end_ref","anchor_ref"))
    _require(start in path and end in path and start==anchor and path.index(start)<path.index(end),"fit_window_or_anchor_mismatch")
    selected=path[path.index(start):path.index(end)+1]
    panels=tuple(lg._ref(p) for p in d["panel_refs"])
    _require(bool(panels) and len(panels)==len(set(panels)),"fit_fixed_panel_set_required")
    declared={lg._ref(p) for p in trajectory.data["panel_refs"]}
    _require(set(panels)<=declared,"fit_panel_outside_registered_path")
    for p in panels:
        pb=review.get(p.object_kind,p.object_id,p.object_version)
        _require(pb is not None and pb.status!="contract_error" and pb.data["view"]==d["view"],"fit_panel_binding_unavailable")
    index=EvidenceIndex(bundle); role=review.configuration["data_role"]
    registration=lg._value(d["registration_ref"])
    reg_reasons=list(support_gate(index,registration,"fit_registration",role,review.limits))
    states=[review.get(s.object_kind,s.object_id,s.object_version) for s in selected]
    reg_reasons+=list(lg._registration(index,registration,states,data_role=role).reasons)
    p=index.payload((registration["record_type"],registration["record_id"])) if registration and index.resolve(registration) else None
    witness=p.get("extensions",{}).get(REGISTRATION_KEY) if p else None
    expected=registration_witness(d,trajectory.data)
    if not isinstance(witness,Mapping) or set(witness)!=set(expected)|{"residual_rationale","inspection_status"}:
        reg_reasons.append("fit_registration_binding_missing")
    else:
        if any(witness[k]!=v for k,v in expected.items()): reg_reasons.append("fit_registration_binding_mismatch")
        if not isinstance(witness["residual_rationale"],str) or not witness["residual_rationale"].strip(): reg_reasons.append("fit_residual_rationale_missing")
        if witness["inspection_status"]!="registered_before_inspection": reg_reasons.append("fit_registration_not_prespecified")
    slots=lg._slots(review,trajectory,d["view"],study.measurements)
    endpoint=[]; regime=[]; vals=[]; times=[]; statuses=[]; matrix=[[] for _ in panels]; refs=[[] for _ in panels]; by_panel=[[] for _ in panels]
    for si,s in enumerate(selected):
        ptvals=[]; slot_states=[]
        coord=lg._value(trajectory.data["round_coordinates"][path.index(s)])
        times.append(coord)
        for j,panel in enumerate(panels):
            found=[x for x in slots if x[0]==s and x[1]==panel]
            slot=found[0] if len(found)==1 else None
            status=slot[3] if slot else "undeclared_or_ambiguous"; m=slot[4] if slot else None
            scalar=m.diversity if m else lg._scalar("gini_simpson_diversity",status="unavailable",reasons=(status,))
            value=scalar.value if scalar.status=="available" else None
            matrix[j].append(value); refs[j].append(m.ref if m else None); by_panel[j].append(m)
            ptvals.append(scalar); slot_states.append(status)
            local_reasons=list(m.matched_gate.reasons) if m else ([] if status=="intentionally_unsampled" else ["expected_panel_measurement_missing"])
            if m is not None and scalar.status!="available":local_reasons.append("panel_diversity_unavailable")
            regime+=local_reasons
            if si in {0,len(selected)-1}:endpoint+=local_reasons
        scalar=lg._mean("mean_panel_diversity",ptvals,max_bits=review.limits["max_exact_bits"])
        vals.append(scalar.value if scalar.status=="available" else None)
        statuses.append("available" if scalar.status=="available" else "intentionally_unsampled" if all(x=="intentionally_unsampled" for x in slot_states) else "missing")
        if "intentionally_unsampled" in slot_states and statuses[-1]!="intentionally_unsampled":regime.append("incomplete_common_panel_schedule")
    for members in by_panel:
        endpoint+=list(lg._match(members[0],members[-1]).reasons)
        anchor_measurement=members[0]
        for m in members:
            if m is not None:regime+=list(lg._match(anchor_measurement,m).reasons)
    clock=lg._clock(trajectory,start,end,review)[3]; endpoint+=list(clock.reasons)
    # Contract/path defects are never repaired by selecting another branch.
    dangerous={"trajectory_path_lengths","trajectory_repeated_state","trajectory_repeated_transition","duplicate_trajectory_panel","duplicate_observation_slot","observation_outside_selected_path","observation_clock_mismatch","observation_measurement_mismatch","measurement_on_unobserved_slot","observation_schedule_incomplete"}
    endpoint += [i.code for i in trajectory.issues if i.code in dangerous]
    endpoint += [i.code for i in request.issues if not i.locator.endswith("/residual_criterion")]
    regime += list(regime_restrictions(review,selected,panels,trajectory.ref,request.ref))
    sens=d["sensitivity_ref"]
    uncertainty="not_estimated" if sens["state"]=="known" and sens.get("value") is None else "requested_separately" if sens["state"]=="known" else "unknown_not_estimated"
    qualifiers=CAVEATS+(("validity_conditioned",) if d["view"]=="classified_valid" else ())
    if any(s and s.data["state_kind"]=="corpus" for s in states):qualifiers+=("corpus_stage_not_model_capacity",)
    return PreparedCurve(request.ref,trajectory.ref,panels,selected,tuple(times),tuple(vals),tuple(statuses),
        tuple(tuple(v) for v in matrix),tuple(tuple(v) for v in refs),_reasons(endpoint),_reasons(regime),_reasons(reg_reasons),
        lg._value(d["residual_criterion"]),d["fit_mode"],d["view"],tuple(s.data["stage_role"] if s else "unknown" for s in states),uncertainty,qualifiers)


def fit_prepared(prepared: PreparedCurve, limits=None) -> CurveFit:
    from dataclasses import replace
    _require(isinstance(prepared,PreparedCurve),"prepared_half_life_curve_required")
    fit=analyze_curve(prepared.times,prepared.values,state_ids=[s.object_id for s in prepared.state_refs],slot_statuses=prepared.statuses,
        fit_mode=prepared.fit_mode,max_abs_log_residual=prepared.criterion,
        endpoint_reasons=prepared.endpoint_reasons,regime_reasons=prepared.regime_reasons,
        criterion_reasons=prepared.registration_reasons,limits=limits,aggregation="mean_panel_diversity")
    # A local request also needs a registered window, but an anchored request's
    # missing regime criterion never erases the separate endpoint arithmetic.
    if prepared.fit_mode=="local" and prepared.registration_reasons:
        fit=replace(fit,interval=_estimate(fit.interval.name,status="unavailable",reasons=prepared.registration_reasons,method=INTERVAL_METHOD))
    return replace(fit,interval=replace(fit.interval,qualifiers=prepared.qualifiers+(("registration_unverified_endpoint_description",) if prepared.registration_reasons else ())),
        empirical=replace(fit.empirical,qualifiers=prepared.qualifiers),uncertainty_status=prepared.uncertainty_status)


def fit_half_lives(bundle: LoadedBundle, *, observed: lg.ObservedStudy | None=None) -> HalfLifeStudy:
    _require(isinstance(bundle,LoadedBundle),"loaded_bundle_required")
    fresh=lg.observe_longitudinal(bundle)
    if observed is not None:
        lg.assert_current(observed,bundle)
        _require(observed==fresh,"altered_observed_half_life_context")
    review=fresh.review
    if review.configuration is None:return HalfLifeStudy(review.requested,review.status,review.input_context_sha256,reasons=tuple(i.code for i in review.issues),observed=fresh)
    rows=[x for x in review.objects if x.ref and x.ref.object_kind=="shl_request" or x.locator.startswith(lr.BASE+"/shl_requests/")]
    if not rows:return HalfLifeStudy(False,"not_requested",review.input_context_sha256,observed=fresh)
    results=[]
    for r in rows:
        try:
            _require("half_life" in review.configuration["capabilities"],"half_life_capability_not_declared")
            _require(r.ref is not None and r.status!="contract_error","half_life_request_contract_error")
            prepared=prepare_curve(bundle,fresh,r); fit=fit_prepared(prepared,review.limits)
            target=fit.empirical if prepared.fit_mode=="anchored" else fit.interval
            results.append(FittedRequest(r.ref,target.status,target.reasons,prepared,fit,r.data))
        except (InputError,KeyError,TypeError,ValueError,OverflowError) as e:
            results.append(FittedRequest(r.ref,"unavailable",(getattr(e,"code","half_life_binding_error"),),original=r.data))
    status="available" if all(x.status=="available" for x in results) else "available_with_limitations"
    return HalfLifeStudy(True,status,review.input_context_sha256,tuple(results),observed=fresh)


def assert_current(study: HalfLifeStudy, bundle: LoadedBundle) -> None:
    _require(isinstance(study,HalfLifeStudy) and study.input_context_sha256==lr.input_fingerprint(bundle),"stale_half_life_context")


def compare_null(fit: CurveFit, null: NullScenario) -> NullComparison:
    _require(isinstance(fit,CurveFit) and isinstance(null,NullScenario),"explicit_empirical_and_null_results_required")
    return NullComparison(fit.empirical, null.structural_half_life_null, null.scenario_id)
