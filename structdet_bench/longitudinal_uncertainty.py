"""Opt-in complete-panel/root resampling sensitivity for registered SHL fits.

PHASE_3_PLAN.md 5.5: 2000 private-RNG draws, fixed seed 20260919, complete
indices, unchanged time grid and all failures retained. No confidence claim,
training, remote access, candidate execution, family assay or ERR calculation.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field, replace
from fractions import Fraction
import hashlib
import json
import math
import platform
import random
import re
from typing import Any, Mapping

from .contracts import InputError, freeze, is_hash, is_id, validate_ref
from .comparison_records import configuration_fingerprint
from .local_io import LoadedBundle, parse_json_bytes
from .evidence import EvidenceIndex
from . import longitudinal as lg, longitudinal_records as lr, half_life as hl
from .categorical_null import _Exact, _limits, _number

METHOD="longitudinal_trajectory_sensitivity_v1"
PLAN_VERSION="0.1"
APPROVED_PLAN_SHA256="1ca74fbba06bea44f2b656b3f4e6b46b0c6747cf13640c3f1ea29c69ef3d6352"
SEED=20260919
REPLICATES=2000
QUANTILE="linear_b_minus_one_v1"
PROBABILITIES=("0.025","0.975")
EVIDENCE_KEY="longitudinal_sensitivity_v1"


@dataclass(frozen=True)
class Draw:
    index: int
    selected_indices: tuple[int,...]
    curve: tuple[Fraction | None,...]
    fit: hl.CurveFit | None
    status: str
    reasons: tuple[str,...]


@dataclass(frozen=True)
class Sensitivity:
    request_ref: lr.ObjectRef | None
    status: str
    reasons: tuple[str,...]
    unit: str | None = None
    unit_ids: tuple[str,...] = ()
    point_fit: hl.CurveFit | None = None
    interval: tuple[float,float] | None = None
    draws: tuple[Draw,...] = field(default=(),repr=False)
    failure_counts: Mapping[str,int] = field(default_factory=lambda:freeze({}))
    replay: Mapping[str,Any] | None = field(default=None,repr=False)
    plan: Any = field(default=None,repr=False)
    dependency_status: str = "unresolved"
    interval_scope: str = "resampling_sensitivity"
    uncertainty_status: str = "not_estimated"
    substantive_validation_performed: bool = False
    population_confidence_established: bool = False
    filtered_success_interval_computed: bool = False
    training_lineage_variability_estimated: bool = False
    view: str | None = None
    stage_roles: tuple[str,...] = ()
    source_point_fit: hl.CurveFit | None = None
    unit_values: tuple[tuple[Fraction | None,...],...] = field(default=(),repr=False)
    round_grid: tuple[int | None,...] = ()
    unit_weights: tuple[Fraction,...] = ()


@dataclass(frozen=True)
class LongitudinalSensitivity:
    requested: bool
    status: str
    input_context_sha256: str | None
    results: tuple[Sensitivity,...]
    method: str = METHOD
    substantive_validation_performed: bool = False
    half_lives: hl.HalfLifeStudy | None = field(default=None,repr=False)


def _require(ok,code):
    if not ok:raise InputError(code)


def _plain(v):
    if isinstance(v,Mapping):return {k:_plain(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [_plain(x) for x in v]
    return v


def _hash(v):
    return hashlib.sha256((json.dumps(_plain(v),sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode()).hexdigest()


def _unit_ids(ids):
    _require(isinstance(ids,(tuple,list)) and 2<=len(ids)<=64,"at_least_two_bounded_units_required")
    _require(all(is_id(x) for x in ids) and len(set(ids))==len(ids),"sensitivity_unit_identity")
    return tuple(ids)


def make_replay(unit_ids, *, unit, context_sha256, plan_sha256) -> Mapping[str,Any]:
    ids=_unit_ids(unit_ids)
    _require(unit in {"probe_panel","lineage_root"} and is_hash(context_sha256) and is_hash(plan_sha256),"sensitivity_replay_identity")
    rng=random.Random(SEED)
    rows=[[rng.randrange(len(ids)) for _ in ids] for _ in range(REPLICATES)]
    record={"schema_version":PLAN_VERSION,"method":METHOD,"seed":SEED,"replicates":REPLICATES,"index_base":0,
        "unit":unit,"unit_ids":list(ids),"context_sha256":context_sha256,"plan_sha256":plan_sha256,
        "quantile":QUANTILE,"probabilities":list(PROBABILITIES),
        "rng":{"algorithm":"MT19937","api":"random.Random.randrange","implementation":platform.python_implementation(),
               "python_version":platform.python_version(),"state_version":random.Random.VERSION},
        "indices":rows,"indices_sha256":_hash(rows)}
    record["sha256"]=_hash(record)
    return freeze(record)


def validate_replay(raw,unit_ids,*,unit,context_sha256,plan_sha256,expected_sha256=None):
    """Verify the saved integer matrix, never regenerate it to decide equality."""
    ids=_unit_ids(unit_ids)
    fields={"schema_version","method","seed","replicates","index_base","unit","unit_ids","context_sha256","plan_sha256",
            "quantile","probabilities","rng","indices","indices_sha256","sha256"}
    _require(isinstance(raw,Mapping) and set(raw)==fields,"longitudinal_replay_fields")
    constants={"schema_version":PLAN_VERSION,"method":METHOD,"seed":SEED,"replicates":REPLICATES,"index_base":0,
               "unit":unit,"context_sha256":context_sha256,"plan_sha256":plan_sha256,"quantile":QUANTILE}
    _require(all(type(raw[k]) is type(v) and raw[k]==v for k,v in constants.items()),"longitudinal_replay_method_or_context")
    _require(isinstance(raw["unit_ids"],(tuple,list)) and tuple(raw["unit_ids"])==ids,"longitudinal_replay_units")
    _require(isinstance(raw["probabilities"],(tuple,list)) and tuple(raw["probabilities"])==PROBABILITIES,"longitudinal_replay_quantiles")
    rng=raw["rng"]
    _require(isinstance(rng,Mapping) and set(rng)=={"algorithm","api","implementation","python_version","state_version"},"longitudinal_replay_rng")
    _require(rng["algorithm"]=="MT19937" and rng["api"]=="random.Random.randrange" and rng["implementation"]=="CPython"
             and isinstance(rng["python_version"],str) and bool(re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}",rng["python_version"]))
             and type(rng["state_version"]) is int and rng["state_version"]==3,"longitudinal_replay_rng")
    rows=raw["indices"]
    _require(isinstance(rows,(tuple,list)) and len(rows)==REPLICATES,"longitudinal_replay_draw_count")
    _require(all(isinstance(row,(tuple,list)) and len(row)==len(ids)
             and all(type(i) is int and 0<=i<len(ids) for i in row) for row in rows),"longitudinal_replay_indices")
    _require(is_hash(raw["indices_sha256"]) and raw["indices_sha256"]==_hash(rows),"longitudinal_replay_index_digest")
    _require(is_hash(raw["sha256"]) and raw["sha256"]==_hash({k:v for k,v in raw.items() if k!="sha256"}),"longitudinal_replay_digest")
    if expected_sha256 is not None:
        _require(is_hash(expected_sha256) and raw["sha256"]==expected_sha256,"longitudinal_replay_expected_digest")
    return freeze(raw)


def percentile(values,q:Fraction,*,limits=None) -> float:
    """Linear interpolation of finite computed fits, preserving binary operands."""
    exact=_Exact(_limits(limits))
    _require(isinstance(values,(list,tuple)) and 1<=len(values)<=REPLICATES and isinstance(q,Fraction) and 0<=q<=1,"longitudinal_percentile_input")
    _require(all(type(x) in (int,float) and math.isfinite(x) for x in values),"longitudinal_percentile_nonfinite")
    vals=sorted(exact.fraction(Fraction(x)) for x in values)
    h=exact.mul(Fraction(len(vals)-1),q);lo=h.numerator//h.denominator;weight=h-lo
    value=vals[lo] if weight==0 else exact.add(vals[lo],exact.mul(weight,exact.add(vals[lo+1],-vals[lo])))
    result=float(value)
    _require(math.isfinite(result) and (value==0 or result!=0),"longitudinal_percentile_numeric_range")
    return result


def resample_curves(unit_curves,times,*,state_ids,unit_ids,unit,max_abs_log_residual,context_sha256,plan_sha256,
                    dependency_reasons=(),fit_gate_reasons=(),fit_mode="anchored",replay=None,expected_replay_sha256=None,limits=None) -> Sensitivity:
    """Numerical primitive with explicit unit records. No evidence certification.

    Every generated/saved row yields a Draw, including failed fits. There is no
    success-only percentile or retry. Missing input units block the procedure.
    """
    lim=_limits(limits);exact=_Exact(lim);ids=_unit_ids(unit_ids)
    _require(unit in {"probe_panel","lineage_root"},"longitudinal_sensitivity_unit")
    _require(isinstance(unit_curves,(tuple,list)) and len(unit_curves)==len(ids),"sensitivity_curve_unit_count")
    _require(isinstance(times,(tuple,list)) and 2<=len(times)<=lim["max_states"],"sensitivity_time_count")
    _require(all(isinstance(c,(tuple,list)) and len(c)==len(times) for c in unit_curves),"sensitivity_common_time_grid")
    _require(is_hash(context_sha256) and is_hash(plan_sha256),"sensitivity_context_required")
    curves=tuple(tuple(None if x is None else _number(x,exact) for x in c) for c in unit_curves)
    _require(all(x is None or 0<=x<=1 for c in curves for x in c),"sensitivity_diversity_range")
    def mean(row):
        return tuple(None if any(curves[i][t] is None for i in row) else exact.div(exact.sum(curves[i][t] for i in row),Fraction(len(row))) for t in range(len(times)))
    point_values=mean(range(len(ids)))
    point=hl.analyze_curve(times,point_values,state_ids=state_ids,fit_mode=fit_mode,max_abs_log_residual=max_abs_log_residual,limits=lim,
                           regime_reasons=fit_gate_reasons,
                           aggregation="mean_root_panel_diversity" if unit=="lineage_root" else "mean_panel_diversity")
    reasons=list(dependency_reasons)+list(fit_gate_reasons)
    if any(x is None for c in curves for x in c):reasons.append("incomplete_common_unit_curve")
    if any(t is None for t in times):reasons.append("sensitivity_time_grid_unknown")
    if REPLICATES*len(ids)*len(times)>lim["max_tail_summands"]:reasons.append("sensitivity_recompute_work_limit")
    if len(ids) > (lim["max_trajectories"] if unit=="lineage_root" else lim["max_panels_per_trajectory"]):reasons.append("sensitivity_unit_work_limit")
    if reasons:
        return Sensitivity(None,"unavailable",hl._reasons(reasons),unit,ids,point,dependency_status="unresolved",unit_values=curves,round_grid=tuple(times),unit_weights=tuple(Fraction(1,len(ids)) for _ in ids))
    saved=make_replay(ids,unit=unit,context_sha256=context_sha256,plan_sha256=plan_sha256) if replay is None else validate_replay(
        replay,ids,unit=unit,context_sha256=context_sha256,plan_sha256=plan_sha256,expected_sha256=expected_replay_sha256)
    draws=[]; failures=Counter()
    for i,row in enumerate(saved["indices"]):
        curve=()
        try:
            curve=mean(row)
            fit=hl.analyze_curve(times,curve,state_ids=state_ids,fit_mode=fit_mode,max_abs_log_residual=max_abs_log_residual,limits=lim,
                aggregation=point.aggregation)
            target=fit.empirical if fit_mode=="anchored" else fit.interval
            status,why=target.status,target.reasons
        except (InputError,TypeError,ValueError,OverflowError) as e:
            fit=None;status="unavailable";why=(getattr(e,"code","sensitivity_fit_failure"),)
        draws.append(Draw(i,tuple(row),curve,fit,status,why))
        if status!="available":
            for reason in why or (status,):failures[reason]+=1
    interval=None;reason=()
    if failures:reason=("complete_interval_unavailable_due_to_failed_draws",)
    elif (point.empirical if fit_mode=="anchored" else point.interval).status!="available":
        reason=("point_fit_not_applicable",)
    else:
        try:
            vals=[(d.fit.empirical if fit_mode=="anchored" else d.fit.interval).value for d in draws]
            interval=(percentile(vals,Fraction(1,40),limits=lim),percentile(vals,Fraction(39,40),limits=lim))
        except (InputError,TypeError,ValueError,OverflowError) as e:
            reason=(getattr(e,"code","sensitivity_percentile_failure"),)
    return Sensitivity(None,"available" if interval is not None else "unavailable",reason,unit,ids,point,interval,tuple(draws),
        freeze(dict(failures)),saved,dependency_status="explicit_arithmetic_units_only",uncertainty_status="resampling_sensitivity",
        training_lineage_variability_estimated=unit=="lineage_root",unit_values=curves,round_grid=tuple(times),unit_weights=tuple(Fraction(1,len(ids)) for _ in ids))


def _read_plan(bundle,review,request):
    ref=lg._value(request.original["sensitivity_ref"])
    rb=lg._resolve(review,ref) if ref is not None else None
    _require(rb is not None and rb.status=="record_consistent","sensitivity_plan_binding_unavailable")
    d=rb.data
    _require(d["method_id"]==METHOD and d["plan_sha256"]==APPROVED_PLAN_SHA256,"sensitivity_plan_method_identity")
    key=d["artifact_ref"]["record_type"]+":"+d["artifact_ref"]["record_id"]
    entries=[a for a in bundle.artifacts if a.record_key==key]
    _require(len(entries)==1 and entries[0].status=="snapshot_read","sensitivity_plan_artifact_unavailable")
    snapshot=bundle.snapshots.get(entries[0].snapshot_path)
    _require(snapshot is not None and hashlib.sha256(snapshot.content).hexdigest()==d["expected_sha256"],"sensitivity_plan_actual_bytes_mismatch")
    p=parse_json_bytes(snapshot.content,bundle.limits)
    keys={"schema_version","plan_id","plan_version","method","request_ref","request_sha256","unit","trajectory_refs","panel_refs",
          "replicates","seed","registration_ref","dependence_ref"}
    _require(isinstance(p,Mapping) and set(p)==keys,"sensitivity_plan_field_set")
    _require(p["schema_version"]==PLAN_VERSION and p["plan_version"]==PLAN_VERSION and p["method"]==METHOD
             and is_id(p["plan_id"]) and p["unit"] in {"probe_panel","lineage_root"},"sensitivity_plan_profile")
    _require(type(p["replicates"]) is int and p["replicates"]==REPLICATES and type(p["seed"]) is int and p["seed"]==SEED,"sensitivity_plan_seed_or_count")
    lr._ref("shl_request")(p["request_ref"])
    _require(lg._ref(p["request_ref"])==request.ref and p["request_sha256"]==configuration_fingerprint(request.original),"sensitivity_fit_request_identity")
    for name,kind in (("trajectory_refs","trajectory"),("panel_refs","panel")):
        lr._list(lr._ref(kind),1,64)(p[name])
        _require(len({lg._ref(x) for x in p[name]})==len(p[name]),"sensitivity_duplicate_declared_unit")
    _require(tuple(lg._ref(x) for x in p["panel_refs"])==request.prepared.panel_refs,"sensitivity_registered_panel_set")
    _require(tuple(lg._ref(x) for x in d["unit_refs"])==tuple(lg._ref(x) for x in p["trajectory_refs"]),"sensitivity_replay_unit_binding")
    validate_ref(p["registration_ref"]); validate_ref(p["dependence_ref"])
    _require(p["registration_ref"]["record_type"]=="preregistration" and p["dependence_ref"]["record_type"]=="independence_assessment","sensitivity_evidence_role")
    return freeze(p)


def _units(study,request,plan):
    """Build complete registered units, never pool candidate counts."""
    prepared=request.prepared; review=study.review; reasons=[]
    trajectories=tuple(lg._ref(x) for x in plan["trajectory_refs"])
    unit=plan["unit"]
    # Keep only the explicitly intentionally-unsampled common times out of the
    # fitted grid. Full source schedule remains in PreparedCurve and context.
    measured=tuple(i for i,s in enumerate(prepared.statuses) if s!="intentionally_unsampled")
    times=tuple(prepared.times[i] for i in measured)
    state_ids=tuple(prepared.state_refs[i].object_id for i in measured)
    groups=[]
    if unit=="probe_panel":
        _require(trajectories==(prepared.trajectory_ref,),"panel_sensitivity_single_path_required")
        ids=tuple(p.object_id for p in prepared.panel_refs)
        curves=tuple(tuple(c[i] for i in measured) for c in prepared.panel_values)
        groups=list(ids)
        seen=set()
        for refs in prepared.measurement_refs:
            calls=set()
            for mr in refs:
                m=study.measurement(mr) if mr else None
                if m and m.source_cell:
                    calls.update(a.attempt_id for a in m.source_cell.inventory.associations if a.sample_id in m.source_cell.inventory.selected_sample_ids and a.attempt_id is not None)
            if seen & calls:reasons.append("shared_panel_call_dependency")
            seen.update(calls)
    else:
        _require(prepared.trajectory_ref in trajectories,"root_sensitivity_base_path_not_selected")
        combined=lg.combine_root_curves(study,trajectories,view=prepared.view)
        reasons+=list(combined.gate.reasons)
        ids=[];curves=[];sample_seen=set();call_seen=set();root_states=[]
        for tr in trajectories:
            candidates=[c for c in study.curves if c.trajectory_ref==tr and c.view==prepared.view]
            _require(len(candidates)==1,"root_sensitivity_curve_unavailable")
            c=candidates[0];ids.append(c.root_ref.object_id);groups.append(lg._value(c.dependency_group))
            _require(c.panel_refs==prepared.panel_refs,"root_sensitivity_panel_set_mismatch")
            selected=[]
            for time in times:
                matches=[point for point in c.points if point.round_index==time]
                _require(len(matches)==1,"root_sensitivity_time_grid_mismatch")
                selected.append(matches[0])
            path_binding=review.get("trajectory",tr.object_id,tr.object_version)
            full_path=tuple(lg._ref(x) for x in path_binding.data["state_refs"])
            lo,hi=full_path.index(selected[0].state_ref),full_path.index(selected[-1].state_ref)
            reasons+=list(hl.regime_restrictions(review,full_path[lo:hi+1],prepared.panel_refs,tr,request.ref))
            curves.append(tuple(p.mean_panel_diversity.value if p.mean_panel_diversity.status=="available" else None for p in selected))
            samples=set();calls=set()
            for point in selected:
                root_states.append(review.get("state",point.state_ref.object_id,point.state_ref.object_version))
                for mr in point.measurement_refs:
                    m=study.measurement(mr) if mr else None
                    if m and m.source_cell:
                        samples.update(m.source_cell.inventory.selected_sample_ids)
                        calls.update(a.attempt_id for a in m.source_cell.inventory.associations if a.sample_id in m.source_cell.inventory.selected_sample_ids and a.attempt_id is not None)
            if samples & sample_seen:reasons.append("reused_root_observations")
            if calls & call_seen:reasons.append("shared_root_call_dependency")
            sample_seen.update(samples);call_seen.update(calls)
        ids=tuple(ids);curves=tuple(curves)
    _unit_ids(ids)
    return ids,curves,times,state_ids,tuple(groups),hl._reasons(reasons)


def _dependency(bundle,study,request,plan,ids,groups):
    review=study.review; index=EvidenceIndex(bundle);role=review.configuration["data_role"]
    reasons=list(hl.support_gate(index,plan["dependence_ref"],"sensitivity_dependence",role,review.limits))
    reasons+=list(hl.support_gate(index,plan["registration_ref"],"sensitivity_registration",role,review.limits))
    states=[]
    for tref in plan["trajectory_refs"]:
        tr=lg._resolve(review,tref)
        if tr:states.extend(lg._resolve(review,x) for x in tr.data["state_refs"])
    reasons+=list(lg._registration(index,plan["registration_ref"],states,data_role=role).reasons)
    plan_hash=configuration_fingerprint(plan)
    registration=index.payload((plan["registration_ref"]["record_type"],plan["registration_ref"]["record_id"]))
    witness=registration.get("extensions",{}).get(EVIDENCE_KEY) if registration else None
    if not isinstance(witness,Mapping) or set(witness)!={"plan_sha256","inspection_status"} or witness["plan_sha256"]!=plan_hash or witness["inspection_status"]!="registered_before_inspection":
        reasons.append("sensitivity_registration_not_bound")
    payload=index.payload((plan["dependence_ref"]["record_type"],plan["dependence_ref"]["record_id"]))
    assessment=payload.get("extensions",{}).get(EVIDENCE_KEY) if payload else None
    expected={"plan_sha256":plan_hash,"unit":plan["unit"],"unit_ids":list(ids),"dependency_groups":list(groups),"conditional_independence":True}
    if not isinstance(assessment,Mapping) or set(assessment)!=set(expected)|{"conditioning"}:
        reasons.append("sensitivity_dependency_assessment_missing")
    else:
        for k,value in expected.items():
            v=assessment[k]
            if k in {"unit_ids","dependency_groups"}:
                if not isinstance(v,(list,tuple)) or tuple(v)!=tuple(value):reasons.append("sensitivity_dependency_assessment_mismatch")
            elif type(v) is not type(value) or v!=value:reasons.append("sensitivity_dependency_assessment_mismatch")
        if not isinstance(assessment["conditioning"],str) or not assessment["conditioning"].strip():reasons.append("sensitivity_conditioning_missing")
    if payload and (payload.get("outcome")!="supported_for_scope" or payload.get("dimension")!="conditional_sampling"):
        reasons.append("sensitivity_sampling_independence_unresolved")
    return hl._reasons(reasons),"fixture_stipulated" if payload and (payload["mock"] or payload["data_role"]=="fixture") else "record_supported_conditional_only"


def evaluate_longitudinal_sensitivity(bundle:LoadedBundle,*,half_lives:hl.HalfLifeStudy|None=None,replays=None) -> LongitudinalSensitivity:
    """Use unchanged scientific bundle plus optional saved manifests by request ID.

    Replay manifests are passive already-loaded objects. Replacing the input
    bundle's plan or data changes context and cannot silently reuse old indices.
    CLI and safe loading of the optional replay carrier remain Step 8 work.
    """
    _require(isinstance(bundle,LoadedBundle),"loaded_bundle_required")
    fresh=hl.fit_half_lives(bundle)
    if fresh.observed.review.configuration is None and fresh.observed.review.status!="not_requested":
        return LongitudinalSensitivity(fresh.observed.review.requested,fresh.observed.review.status,fresh.input_context_sha256,())
    if half_lives is not None:
        hl.assert_current(half_lives,bundle)
        _require(half_lives==fresh,"altered_half_life_sensitivity_context")
    _require(replays is None or isinstance(replays,Mapping),"replay_mapping_required")
    known={r.ref.object_id for r in fresh.results if r.ref}
    if replays is not None:_require(set(replays)<=known,"replay_for_unknown_request")
    results=[];requested=False
    for r in fresh.results:
        point=r.fit
        tag=r.original.get("sensitivity_ref") if isinstance(r.original,Mapping) else None
        if isinstance(tag,Mapping) and tag.get("state")=="known" and tag.get("value")==None:
            if replays is not None and r.ref and r.ref.object_id in replays:raise InputError("replay_for_unrequested_sensitivity")
            results.append(Sensitivity(r.ref,"not_requested",(),point_fit=point));continue
        requested=True
        try:
            _require(r.prepared is not None,"sensitivity_fit_binding_unavailable")
            _require(isinstance(tag,Mapping) and tag.get("state")=="known" and tag.get("value") is not None,"sensitivity_request_unresolved")
            plan=_read_plan(bundle,fresh.observed.review,r)
            ids,curves,times,states,groups,reasons=_units(fresh.observed,r,plan)
            dependency,dep_status=_dependency(bundle,fresh.observed,r,plan,ids,groups)
            prereqs=tuple(reasons)+tuple(dependency)+r.prepared.endpoint_reasons+r.prepared.regime_reasons+r.prepared.registration_reasons
            replay=None
            if replays is not None:
                _require(r.ref.object_id in replays,"explicit_replay_missing_for_request")
                replay=replays[r.ref.object_id]
                _require(replay is not None,"explicit_null_replay")
            result=resample_curves(curves,times,state_ids=states,unit_ids=ids,unit=plan["unit"],max_abs_log_residual=r.prepared.criterion,
                context_sha256=configuration_fingerprint({"input":fresh.input_context_sha256,"request":r.original,"plan":plan}),
                plan_sha256=configuration_fingerprint(plan),dependency_reasons=prereqs,fit_gate_reasons=tuple(reasons)+r.prepared.endpoint_reasons+r.prepared.regime_reasons+r.prepared.registration_reasons,fit_mode=r.prepared.fit_mode,replay=replay,limits=fresh.observed.review.limits)
            def qualify(fit):
                if fit is None:return None
                return replace(fit,interval=replace(fit.interval,qualifiers=r.prepared.qualifiers),
                               empirical=replace(fit.empirical,qualifiers=r.prepared.qualifiers),uncertainty_status="resampling_sensitivity")
            results.append(replace(result,request_ref=r.ref,plan=plan,dependency_status=dep_status if not dependency else "unresolved",
                point_fit=qualify(result.point_fit),draws=tuple(replace(d,fit=qualify(d.fit)) for d in result.draws),
                view=r.prepared.view,stage_roles=r.prepared.stage_roles,source_point_fit=r.fit))
        except (InputError,KeyError,TypeError,ValueError,OverflowError) as e:
            results.append(Sensitivity(r.ref,"unavailable",(getattr(e,"code","longitudinal_sensitivity_binding_failure"),),point_fit=point))
    status="not_requested" if not requested else "available" if all(r.status in {"available","not_requested"} for r in results) else "available_with_limitations"
    return LongitudinalSensitivity(requested,status,fresh.input_context_sha256,tuple(results),half_lives=fresh)


def assert_current(study:LongitudinalSensitivity,bundle:LoadedBundle)->None:
    _require(isinstance(study,LongitudinalSensitivity) and study.input_context_sha256==lr.input_fingerprint(bundle),"stale_longitudinal_sensitivity_context")
