"""Observed, task-bounded structural trajectories and stage/tail accounting.

Consumes the original M admissions and the versioned Step 2 bindings. This is
finite-sample description, never a probability-support assay, categorical
forecast, causal transmission estimator, half-life, or recovery measurement.
No I/O occurs here. Original populations, missing slots and evidence survive.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from fractions import Fraction
from typing import Any, Mapping

from .contracts import CLASS_IDS, InputError, freeze, is_id, knowledge
from .evidence import EvidenceIndex
from .local_io import LoadedBundle
from . import longitudinal_records as lr
from .metrics import DistributionMetrics, population_metrics, _passes
from .populations import CellPopulations, Population, PopulationCollection, build_populations

METHOD = "observed_longitudinal_v1"
SUPPORT_TYPES = ("occurrence", "empirical_frequency")
UNITS = "classified_realizations"


@dataclass(frozen=True)
class Scalar:
    name: str
    value: Fraction | int | None
    status: str
    unit: str
    numerator: int | None = None
    denominator: int | None = None
    reasons: tuple[str, ...] = ()
    qualifiers: tuple[str, ...] = ()
    uncertainty_status: str = "not_estimated"


@dataclass(frozen=True)
class Gate:
    status: str
    reasons: tuple[str, ...] = ()
    qualifiers: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObservedSet:
    status: str
    members: tuple[str, ...] | None
    support_type: str
    population_size: int | None
    threshold: Any = field(default=None, repr=False)
    reasons: tuple[str, ...] = ()
    qualifiers: tuple[str, ...] = ()
    probability_support_established: bool = False


@dataclass(frozen=True)
class Measurement:
    ref: lr.ObjectRef
    state_ref: lr.ObjectRef
    panel_ref: lr.ObjectRef | None
    state_kind: str
    stage_role: str
    view: str
    binding: lr.ObjectBinding = field(repr=False)
    state: lr.ObjectBinding | None = field(repr=False)
    source_cell: CellPopulations | None = field(repr=False)
    distribution: DistributionMetrics = field(repr=False)
    diversity: Scalar
    binding_gate: Gate
    matched_gate: Gate
    class_accounting: Mapping[str, Any] = field(repr=False)
    evidence_issues: tuple[lr.Issue, ...] = field(repr=False)
    unit: str = UNITS
    substantive_validation_performed: bool = False


@dataclass(frozen=True)
class SetChange:
    upstream: ObservedSet
    downstream: ObservedSet
    meaning_gate: Gate
    matching_gate: Gate
    retained: tuple[str, ...] | None
    became_unobserved: tuple[str, ...] | None
    newly_observed: tuple[str, ...] | None
    retention: Scalar
    loss: Scalar
    size_change: Scalar
    causal_transmission_established: bool = False
    model_recovery_established: bool = False

    @property
    def matched_retention_fraction(self):
        return self.retention if self.matching_gate.status=="eligible" else _scalar(
            "matched_observed_retention_fraction",status="unavailable",reasons=self.matching_gate.reasons)

    @property
    def matched_loss_fraction(self):
        return self.loss if self.matching_gate.status=="eligible" else _scalar(
            "matched_observed_loss_fraction",status="unavailable",reasons=self.matching_gate.reasons)


@dataclass(frozen=True)
class Pair:
    upstream_ref: lr.ObjectRef
    downstream_ref: lr.ObjectRef
    panel_ref: lr.ObjectRef | None
    upstream_measurement_ref: lr.ObjectRef | None
    downstream_measurement_ref: lr.ObjectRef | None
    change: SetChange
    upstream_round: int | None
    downstream_round: int | None
    elapsed_rounds: int | None
    clock_gate: Gate
    intermediate_slots: tuple[Any, ...] = field(repr=False)


@dataclass(frozen=True)
class ClassObservation:
    class_id: str
    state_ref: lr.ObjectRef
    panel_ref: lr.ObjectRef | None
    round_index: int | None
    measurement_ref: lr.ObjectRef | None
    slot_status: str
    count: int | None
    frequency: Scalar
    observation_state: str
    recurrence: str
    intervening_gap_refs: tuple[lr.ObjectRef, ...] = ()
    review_availability: str = "not_established"


@dataclass(frozen=True)
class TailMember:
    class_id: str | None
    tail_ref: Any = field(repr=False)
    designation: Any = field(repr=False)
    rationale: Any = field(repr=False)
    registry_ref: Any = field(repr=False)
    registration_ref: Any = field(repr=False)
    registration_gate: Gate
    review_availability: str
    review_refs: tuple[Any, ...] = field(repr=False)
    observations: tuple[ClassObservation, ...] = ()
    mock_evidence: bool = False
    substantive_validation_performed: bool = False


@dataclass(frozen=True)
class CurvePoint:
    state_ref: lr.ObjectRef
    round_index: int | None
    panel_refs: tuple[lr.ObjectRef, ...]
    measurement_refs: tuple[lr.ObjectRef | None, ...]
    slot_statuses: tuple[str, ...]
    panel_diversities: tuple[Scalar, ...]
    mean_panel_diversity: Scalar


@dataclass(frozen=True)
class Curve:
    trajectory_ref: lr.ObjectRef
    root_ref: lr.ObjectRef
    dependency_group: Any = field(repr=False)
    view: str
    panel_refs: tuple[lr.ObjectRef, ...]
    points: tuple[CurvePoint, ...]
    matching_gate: Gate
    clock_gate: Gate
    weights: tuple[Fraction, ...]
    independent_replicate_established: bool = False
    pooled_counts_used: bool = False


@dataclass(frozen=True)
class RootCurve:
    trajectory_refs: tuple[lr.ObjectRef, ...]
    view: str
    round_grid: tuple[int | None, ...]
    values: tuple[Scalar, ...]
    weights: tuple[Fraction, ...]
    gate: Gate
    independent_replicates_established: bool = False
    pooled_counts_used: bool = False


@dataclass(frozen=True)
class Request:
    ref: lr.ObjectRef | None
    status: str
    reasons: tuple[str, ...]
    support_type: str | None
    view: str | None
    declared_state_refs: tuple[lr.ObjectRef, ...]
    sets: tuple[tuple[lr.ObjectRef, ObservedSet], ...]
    pairs: tuple[Pair, ...]
    observations: tuple[ClassObservation, ...]
    tails: tuple[TailMember, ...]
    tail_gate: Gate
    original: Any = field(repr=False)


@dataclass(frozen=True)
class StageTransition:
    transition_ref: lr.ObjectRef
    transition_kind: str
    parent_refs: tuple[lr.ObjectRef, ...]
    child_ref: lr.ObjectRef
    stage_roles: tuple[str, ...]
    contributions: Any = field(repr=False)
    material_scope_gate: Gate
    changes: tuple[tuple[lr.ObjectRef, lr.ObjectRef, SetChange], ...]
    stages: tuple[tuple[lr.ObjectRef, str, tuple[lr.ObjectRef, ...]], ...]
    causal_parent_assignment_performed: bool = False
    model_expression_established: bool = False


@dataclass(frozen=True)
class ObservedStudy:
    requested: bool
    status: str
    input_context_sha256: str | None
    review: lr.LongitudinalReview = field(repr=False)
    populations: PopulationCollection | None = field(repr=False)
    measurements: tuple[Measurement, ...] = ()
    requests: tuple[Request, ...] = ()
    curves: tuple[Curve, ...] = ()
    stage_transitions: tuple[StageTransition, ...] = ()
    reasons: tuple[str, ...] = ()
    method: str = METHOD
    statistics_computed: bool = False
    substantive_validation_performed: bool = False

    def measurement(self, ref: lr.ObjectRef) -> Measurement | None:
        found = [m for m in self.measurements if m.ref == ref]
        return found[0] if len(found) == 1 else None


def _reasons(items) -> tuple[str, ...]:
    return tuple(sorted(set(items)))


def _gate(reasons=(), qualifiers=()) -> Gate:
    r = _reasons(reasons)
    return Gate("unavailable" if r else "eligible", r, _reasons(qualifiers))


def _value(tag):
    try:
        k = knowledge(tag)
        return k.value if k.state == "known" else None
    except InputError:
        return None


def _ref(value):
    return lr.ObjectRef(value["object_kind"], value["object_id"], value["object_version"])


def _resolve(review, value):
    if not isinstance(value, Mapping):
        return None
    return review.get(value["object_kind"], value["object_id"], value["object_version"])


def _scalar(name, value=None, status="available", unit="dimensionless", reasons=(), qualifiers=()):
    q = Fraction(value) if value is not None else None
    return Scalar(name, value, status, unit, q.numerator if q is not None else None,
                  q.denominator if q is not None else None, _reasons(reasons), _reasons(qualifiers))


def _mean(name, values, *, max_bits=262144):
    if not values:
        return _scalar(name, status="undefined", reasons=("empty_mean_unit_set",))
    bad = [s for s in values if s.status != "available"]
    if bad:
        status = "unavailable" if any(s.status == "unavailable" for s in bad) else "undefined"
        return _scalar(name, status=status, reasons=("incomplete_fixed_unit_mean",)+tuple(r for s in bad for r in s.reasons))
    total = Fraction(0)
    for v in values:
        total += v.value
        if max(total.numerator.bit_length(), total.denominator.bit_length()) > max_bits:
            return _scalar(name, status="unavailable", reasons=("exact_workload_limit",))
    total /= len(values)
    if max(total.numerator.bit_length(), total.denominator.bit_length()) > max_bits:
        return _scalar(name, status="unavailable", reasons=("exact_workload_limit",))
    return _scalar(name, total)


def diversity(distribution: DistributionMetrics) -> Scalar:
    """Complement the exact SCI for its original population; never use Q."""
    if not isinstance(distribution, DistributionMetrics):
        raise InputError("distribution_metrics_required")
    sci = distribution.results["structural_concentration_index"]
    if sci.result_status != "available":
        return _scalar("gini_simpson_diversity", status=sci.result_status, reasons=sci.reasons)
    if sci.exact_ratio is None:
        return _scalar("gini_simpson_diversity", status="unavailable", reasons=("exact_SCI_unavailable",))
    numerator, denominator = sci.exact_ratio
    if type(numerator) is not int or type(denominator) is not int or not 0 <= numerator <= denominator or denominator <= 0:
        return _scalar("gini_simpson_diversity", status="unavailable", reasons=("invalid_exact_SCI",))
    return _scalar("gini_simpson_diversity", Fraction(denominator-numerator, denominator))


def support_set(distribution: DistributionMetrics, support_type="occurrence") -> ObservedSet:
    if not isinstance(distribution, DistributionMetrics) or support_type not in SUPPORT_TYPES:
        raise InputError("observed_support_component_required")
    name = "observed_support_size" if support_type == "occurrence" else "observed_support_size_thresholded"
    metric = distribution.results[name]
    threshold = distribution.threshold if support_type == "empirical_frequency" else None
    if metric.result_status != "available":
        return ObservedSet(metric.result_status, None, support_type, distribution.population_size, threshold, metric.reasons)
    counts = distribution.class_counts
    members = tuple(sorted(c for c, n in counts.items() if n > 0 and
        (support_type == "occurrence" or _passes(n, distribution.population_size, threshold))))
    if len(members) != metric.value:
        return ObservedSet("unavailable", None, support_type, distribution.population_size, threshold, ("set_count_conservation_failed",))
    return ObservedSet("available", members, support_type, distribution.population_size, threshold,
                       qualifiers=("observed_under_declared_protocol", "finite_classified_subset"))


def set_change(upstream: ObservedSet, downstream: ObservedSet, *, meaning_gate=Gate("eligible"), matching_gate=Gate("eligible")) -> SetChange:
    """Pure set arithmetic on declared compatible observed sets, not ancestry."""
    if not isinstance(upstream, ObservedSet) or not isinstance(downstream, ObservedSet) or not isinstance(meaning_gate,Gate) or not isinstance(matching_gate,Gate):
        raise InputError("observed_sets_required")
    reasons = list(meaning_gate.reasons)
    if meaning_gate.status != "eligible" and not reasons:reasons.append("meaning_compatibility_unavailable")
    if upstream.support_type != downstream.support_type or upstream.threshold != downstream.threshold:
        reasons.append("support_criterion_mismatch")
    for s in (upstream, downstream):
        if s.status != "available" or s.members is None:
            reasons.extend(s.reasons or ("observed_set_unavailable",))
        elif len(set(s.members)) != len(s.members) or not all(is_id(x) for x in s.members):
            reasons.append("observed_set_identity_conflict")
    mg = _gate(reasons, meaning_gate.qualifiers)
    if reasons:
        bad = _scalar("observed_retention_fraction", status="unavailable", reasons=reasons)
        return SetChange(upstream, downstream, mg, matching_gate, None, None, None, bad,
            _scalar("observed_loss_fraction", status="unavailable", reasons=reasons),
            _scalar("observed_support_size_change", status="unavailable", unit="classes", reasons=reasons))
    a, b = set(upstream.members), set(downstream.members)
    keep, lost, new = tuple(sorted(a & b)), tuple(sorted(a-b)), tuple(sorted(b-a))
    assert len(keep)+len(lost) == len(a) and len(keep)+len(new) == len(b)
    status = "available" if a else "undefined"
    rs = () if a else ("empty_upstream_observed_set",)
    qualifiers = ("unmatched_descriptive",) if matching_gate.status != "eligible" else ()
    return SetChange(upstream, downstream, mg, matching_gate, keep, lost, new,
        _scalar("observed_retention_fraction", Fraction(len(keep),len(a)) if a else None, status, reasons=rs,qualifiers=qualifiers),
        _scalar("observed_loss_fraction", Fraction(len(lost),len(a)) if a else None,status,reasons=rs,qualifiers=qualifiers),
        _scalar("observed_support_size_change",len(b)-len(a),unit="classes",qualifiers=qualifiers))


def _blocked_population(view, reasons):
    return Population(view,"unavailable",(),freeze({}),_reasons(reasons))


def _knowledge_resolved(tag):
    try:
        return knowledge(tag).state in {"known", "not_applicable"}
    except InputError:
        return False


def _registration(index, ref, states, *, data_role="fixture") -> Gate:
    if ref is None or index.resolve(ref) is None:
        return _gate(("registration_unresolved",))
    p = index.payload((ref["record_type"],ref["record_id"]))
    if p is None or p["state"] != "active":
        return _gate(("registration_inactive_or_unreadable",))
    value = _value(p.get("registered_at"))
    try:
        stamp = datetime.fromisoformat(value)
        if stamp.utcoffset() is None:raise ValueError
    except (ValueError,TypeError,AttributeError):
        return _gate(("registration_time_unknown",))
    reasons=[]
    if data_role!="fixture" and (p["mock"] or p["data_role"]=="fixture"):reasons.append("mock_registration_for_nonfixture")
    if index.affected((ref["record_type"],ref["record_id"]),{"metadata","independence"}):reasons.append("registration_under_correction")
    for state in states:
        t = _value(state.data["state_time"]) if state else None
        if t is None:reasons.append("state_time_unknown_for_registration")
        elif stamp > datetime.fromisoformat(t):reasons.append("registration_after_observation")
    return _gate(reasons, ("declared_chronology_only",))


def _fixed_budget(cell, declared_budget) -> Gate:
    inv=cell.inventory; reasons=[]
    if type(declared_budget) is not int or declared_budget <= 0:
        return _gate(("matched_budget_unresolved",))
    if inv.selection_status != "available" or inv.selected_count.value != declared_budget:
        reasons.append("selected_budget_mismatch")
    if inv.plan_status != "available" or len(inv.positions) < declared_budget:
        reasons.append("requested_position_plan_unavailable")
    positions=inv.positions[:declared_budget]
    if any(p.status != "present" for p in positions):reasons.append("requested_position_missing_or_ambiguous")
    intended=tuple(p.sample_ids[0] for p in positions if p.status=="present")
    if len(intended)!=declared_budget or inv.order!=intended:
        reasons.append("first_requested_positions_not_preserved")
    if set(intended)!=set(inv.selected_sample_ids):reasons.append("selected_position_set_mismatch")
    associations={a.sample_id:a for a in inv.associations}
    for p in positions:
        if p.status=="present":
            assoc=associations.get(p.sample_ids[0])
            if assoc is None or assoc.attempt_id!=p.attempt_id or p.attempt_id is None:
                reasons.append("position_attempt_unresolved")
    return _gate(reasons)


def _measurement(bundle, review, index, m, cells, shared_groups) -> Measurement:
    d=m.data; state=_resolve(review,d["state_ref"]); panel=_value(d["panel_ref"])
    p=cells.get(d["cell_ref"]["record_id"]);view=d["view"]
    hard=[]; limitations=[i.code for i in m.issues]
    if state is None:hard.append("state_binding_unavailable")
    elif state.status=="contract_error" or any(i.code=="state_stage_unit_mismatch" for i in state.issues):
        hard.append("state_kind_stage_invalid")
    hard_codes={"measurement_model_state_mismatch","measurement_frame_mismatch","measurement_protocol_mismatch",
        "measurement_registry_mismatch","measurement_selected_identity_mismatch","measurement_selection_unresolved",
        "sample_cell_mismatch","same_measurement_reused_as_new_state","measurement_not_linked_by_state"}
    hard += [i.code for i in m.issues if i.code in hard_codes]
    if p is None:hard.append("measurement_cell_unavailable")
    if m.status=="contract_error":hard.append("measurement_contract_error")
    # A broken source declaration restricts claims; it does not rewrite a
    # separately evidence-admitted M population. Broken cell/version identity does.
    for name in ("cell_ref","frame_ref","protocol_ref","registry_ref"):
        if index.resolve(d[name]) is None:hard.append("measurement_core_identity_unresolved")
    dist=population_metrics(_blocked_population(view,hard) if hard else p.populations[view])
    gate_reasons=list(hard)+limitations
    budget=_value(d["planned_realizations"])
    if p:
        gate_reasons+=list(_fixed_budget(p,budget).reasons)
        if p.ratios["classification_coverage"].value!=1:gate_reasons.append("incomplete_primary_classification")
        if view=="classified_valid":
            if p.ratios["decisive_validity_coverage"].value!=1:gate_reasons.append("incomplete_decisive_validity")
            if p.ratios["classified_valid_coverage"].value not in {Fraction(1),None}:gate_reasons.append("incomplete_valid_classification")
            if p.ratios["valid_fraction_selected"].numerator == 0:gate_reasons.append("empty_valid_conditioned_population")
        for aid in {x.attempt_id for x in p.inventory.positions[:budget if type(budget) is int else 0]}:
            a=index.get(("attempt",aid)) if aid else None
            if a is None or a.data["attempt_status"]!="succeeded" or _value(a.data["retry_of"]) is not None:
                gate_reasons.append("matched_attempt_not_primary_success")
        if any(a.group_id in shared_groups for a in p.inventory.associations):
            gate_reasons.append("cross_cell_generation_group")
    protocol=index.resolve(d["protocol_ref"])
    if protocol:
        for name in ("conditioning_context_ref","decoding_settings","seed"):
            if not _knowledge_resolved(protocol.data[name]):gate_reasons.append("actual_protocol_unresolved")
        prompt_ref=_value(protocol.data["conditioning_context_ref"])
        artifacts=[a for a in bundle.artifacts if isinstance(prompt_ref,Mapping) and a.record_key==prompt_ref["record_type"]+":"+prompt_ref["record_id"]]
        if len(artifacts)!=1 or artifacts[0].status!="snapshot_read":gate_reasons.append("actual_prompt_artifact_unavailable")
    if state:
        ident=_value(state.data["subject_identity"])
        if ident is None:gate_reasons.append("subject_identity_unresolved")
        elif state.data["state_kind"]=="model_system":
            for k in ("parameter_identity","serving_identity","retrieval_identity","tool_identity","system_identity"):
                if not _knowledge_resolved(ident[k]):gate_reasons.append("model_system_identity_unresolved")
    budgetref=_value(d["budget_ref"])
    bp=index.payload((budgetref["record_type"],budgetref["record_id"])) if budgetref and index.resolve(budgetref) else None
    plan=_value(bp["planned"]) if bp else None
    if not isinstance(plan,Mapping) or plan.get("realizations")!=budget:gate_reasons.append("budget_record_not_bound")
    gate_reasons+=list(_registration(index,_value(review.configuration["registered_design_ref"]),[state],data_role=review.configuration["data_role"]).reasons)
    for change in review.objects:
        if change.ref and change.ref.object_kind=="revision" and change.status!="contract_error":
            cd=change.data
            if cd["disposition"]=="applied" and cd["revision_kind"] in {"schema","membership","validity"}:
                affected={_ref(x) for x in cd["affected_refs"]}
                if m.ref in affected or _ref(d["state_ref"]) in affected or (panel and _ref(panel) in affected):
                    gate_reasons.append("applied_revision_requires_pinned_reanalysis")
    evidence_issues=tuple(m.issues)+tuple(state.issues if state else ())
    registry=index.resolve(d["registry_ref"])
    if registry is None or {x["structural_class_id"] for x in registry.data["classes"]}!=set(CLASS_IDS):
        gate_reasons.append("registry_class_meanings_unavailable")
    accounting={}
    if p:
        for c in CLASS_IDS:
            hits=[a for a in p.admissions if a.axis=="assignment" and a.status=="accepted" and a.outcome==c]
            vs={a.sample_id:a for a in p.admissions if a.axis=="validity"}
            accounting[c]={"classified_all_count":len(hits),"valid_count":sum(vs[a.sample_id].status=="accepted" and vs[a.sample_id].outcome=="valid" for a in hits),
                "invalid_count":sum(vs[a.sample_id].status=="accepted" and vs[a.sample_id].outcome=="invalid" for a in hits),
                "validity_unresolved_count":sum(vs[a.sample_id].status!="accepted" or vs[a.sample_id].outcome=="undetermined" for a in hits)}
    return Measurement(m.ref,_ref(d["state_ref"]),_ref(panel) if panel else None,
        state.data["state_kind"] if state else "unknown",state.data["stage_role"] if state else "unknown",view,m,state,p,dist,diversity(dist),
        _gate(hard),_gate(gate_reasons,("validity_conditioned",) if view=="classified_valid" else ()),freeze(accounting),evidence_issues)


def _meanings(a,b):
    reasons=[]
    if a is None or b is None:return _gate(("endpoint_measurement_unavailable",))
    if a.binding_gate.status!="eligible" or b.binding_gate.status!="eligible":reasons.append("endpoint_binding_unavailable")
    if a.view!=b.view:reasons.append("population_view_mismatch")
    for k in ("frame_ref","registry_ref"):
        if a.binding.data[k]!=b.binding.data[k]:reasons.append("class_meaning_identity_mismatch")
    return _gate(reasons)


def _match(a,b, *,budget=None,stage=False):
    reasons=list(_meanings(a,b).reasons);qualifiers=[]
    if a is None or b is None:return _gate(reasons)
    reasons+=list(a.matched_gate.reasons)+list(b.matched_gate.reasons)
    da,db=a.binding.data,b.binding.data
    for k in ("protocol_ref","selection_rule","data_role","planned_realizations"):
        if da[k]!=db[k]:reasons.append(k+"_mismatch")
    if not stage and (a.stage_role!=b.stage_role or a.state_kind!=b.state_kind):reasons.append("state_kind_or_stage_mismatch")
    if budget is not None and (_value(da["planned_realizations"])!=budget or _value(db["planned_realizations"])!=budget):reasons.append("request_budget_mismatch")
    if a.source_cell and b.source_cell:
        for k in ("prompt_id","prompt_block_id","condition_id"):
            if a.source_cell.inventory.identity[k]!=b.source_cell.inventory.identity[k]:reasons.append("elicitation_cell_identity_mismatch")
        n=_value(da["planned_realizations"])
        if type(n) is int:
            shape=lambda m:tuple((p.call_order,p.index) for p in m.source_cell.inventory.positions[:n])
            if shape(a)!=shape(b):reasons.append("candidate_dependence_plan_mismatch")
            def groupshape(m):
                active={p.group_id for p in m.source_cell.inventory.positions[:n]}
                return tuple((g.call_order,g.planned_count) for g in sorted(m.source_cell.inventory.groups,key=lambda g:g.call_order or 0) if g.group_id in active)
            if groupshape(a)!=groupshape(b):reasons.append("candidate_dependence_plan_mismatch")
        if a.view=="classified_valid":
            qualifiers.append("validity_conditioned")
            if a.distribution.population_size!=b.distribution.population_size:qualifiers.append("varying_valid_denominator")
    if a.state and b.state and a.state_kind==b.state_kind=="model_system":
        ia,ib=(_value(m.state.data["subject_identity"]) for m in (a,b))
        if ia is None or ib is None:reasons.append("subject_identity_unresolved")
        else:
            for k in ("serving_identity","retrieval_identity","tool_identity","system_identity"):
                if ia[k]!=ib[k]:reasons.append("nonparameter_system_change")
    return _gate(reasons,qualifiers)


def _set(m, support_type, threshold):
    if m is None:return ObservedSet("unavailable",None,support_type,None,reasons=("measurement_missing",))
    if support_type=="occurrence":return support_set(m.distribution)
    population=m.source_cell.populations[m.view] if m.source_cell and m.binding_gate.status=="eligible" else _blocked_population(m.view,m.binding_gate.reasons)
    return support_set(population_metrics(population,min_empirical_frequency=threshold),support_type)


def _slots(review, trajectory, view, measurements):
    if trajectory is None:return []
    d=trajectory.data;output=[];by={m.ref:m for m in measurements}
    schedule={}
    for slot in d["schedule"]:
        schedule.setdefault((_ref(slot["state_ref"]),_ref(slot["panel_ref"])),[]).append(slot)
    for i,s in enumerate(d["state_refs"]):
        for p in d["panel_refs"]:
            panel=_resolve(review,p)
            if panel is not None and panel.data["view"]!=view:continue
            matches=schedule.get((_ref(s),_ref(p)),[])
            slot=matches[0] if len(matches)==1 else None
            mr=_value(slot["measurement_ref"]) if slot else None
            m=by.get(_ref(mr)) if panel is not None and mr and slot["observation_status"]=="observed" else None
            if m and (m.state_ref!=_ref(s) or m.panel_ref!=_ref(p)):m=None
            coord=_value(d["round_coordinates"][i]) if i<len(d["round_coordinates"]) else None
            output.append((_ref(s),_ref(p),coord,"panel_binding_unavailable" if panel is None else slot["observation_status"] if slot else "undeclared_or_ambiguous",m))
    return output


def _clock(trajectory,start,end,review):
    if trajectory is None:return None,None,None,_gate(("recursive_path_not_supplied",)),()
    path=[_ref(x) for x in trajectory.data["state_refs"]]
    if start not in path or end not in path or path.index(end)<=path.index(start):
        return None,None,None,_gate(("selected_path_order_mismatch",)),()
    ai,bi=path.index(start),path.index(end);coords=trajectory.data["round_coordinates"]
    a=_value(coords[ai]) if ai<len(coords) else None;b=_value(coords[bi]) if bi<len(coords) else None
    reasons=[]
    if a is None or b is None:reasons.append("recursive_distance_unresolved")
    distance=0
    for i in range(ai,bi):
        ed=trajectory.data["transition_refs"]
        part=_resolve(review,ed[i]) if i<len(ed) else None
        if part is None or part.status!="record_consistent":reasons.append("transition_history_unresolved");continue
        if _value(part.data["parent_refs"]) is None or path[i] not in {_ref(x) for x in _value(part.data["parent_refs"])} or _ref(part.data["child_ref"])!=path[i+1]:
            reasons.append("selected_branch_mismatch")
        dt=_value(part.data["round_distance"])
        if dt is None:reasons.append("recursive_distance_unresolved")
        else:distance+=dt
    if a is not None and b is not None and b-a!=distance:reasons.append("recursive_distance_mismatch")
    intermediate=tuple(x for x in trajectory.data["schedule"] if _ref(x["state_ref"]) in path[ai+1:bi])
    return a,b,b-a if not reasons else None,_gate(reasons),intermediate


def _observations(slots,support_type,threshold,classes):
    rows=[];history={}
    for s,p,t,status,m in slots:
        observed=_set(m,support_type,threshold)
        for c in classes:
            key=(p,c);seen,absent,gaps,identity=history.get(key,(False,False,[],None))
            current=(m.binding.data["frame_ref"],m.binding.data["registry_ref"],m.view) if m else None
            if identity is not None and current is not None and current!=identity:
                seen,absent,gaps=False,False,[]
            count=m.distribution.class_counts.get(c) if m and m.binding_gate.status=="eligible" and m.distribution.population_size is not None else None
            n=m.distribution.population_size if m else None
            freq=_scalar("class_frequency",Fraction(count,n) if count is not None and n else None,
                "available" if count is not None and n else "undefined" if count is not None and n==0 else "unavailable",
                reasons=() if count is not None and n else ("empty_classified_population",) if n==0 else ("measurement_unavailable",))
            review_state="unavailable" if m is None else "classification_incomplete" if m.source_cell and m.source_cell.ratios["classification_coverage"].value!=1 else "admitted_class_records_only" if count else "no_observed_member"
            recurrence="none"
            if status!="observed" or observed.status!="available":
                state="unavailable";gaps=gaps+[s]
            elif c in observed.members:
                state="observed" if support_type=="occurrence" else "at_or_above_empirical_threshold"
                recurrence="observed_reappearance" if seen and absent else "observed_after_gap" if seen and gaps else "none"
                rows.append(ClassObservation(c,s,p,t,m.ref if m else None,status,count,freq,state,recurrence,tuple(gaps),review_state))
                history[key]=(True,False,[],current)
                continue
            else:
                state="unobserved_under_protocol" if support_type=="occurrence" else "below_empirical_frequency_threshold"
                absent=absent or seen
            rows.append(ClassObservation(c,s,p,t,m.ref if m else None,status,count,freq,state,recurrence,tuple(gaps),review_state))
            history[key]=(seen,absent,gaps,current or identity)
    return tuple(rows)


def _tail_ledger(index,review,request,slots,observations):
    initial=_value(request.data["protected_tail_ref"])
    if initial is None:return (),Gate("not_requested",("protected_tail_not_declared",))
    pending=[initial];seen=set();members=[];reasons=[]
    states=[_resolve(review,x) for x in request.data["state_refs"]]
    while pending:
        ref=pending.pop(0);key=(ref["record_type"],ref["record_id"],ref["record_version"])
        if key in seen:continue
        if len(seen)>=review.limits["max_link_objects"]:
            reasons.append("tail_link_limit");break
        seen.add(key);raw=index.resolve(ref);p=index.payload(key[:2]) if raw else None
        if p is None:
            reasons.append("tail_record_unavailable")
            members.append(TailMember(None,ref,None,None,None,None,_gate(("tail_record_unavailable",)),"unavailable",()))
            continue
        errors=[];classid=_value(p["class_id"]);designation=_value(p["designation"]);basis=_value(p["basis"])
        if classid not in CLASS_IDS:errors.append("tail_class_identity_unresolved")
        if not isinstance(designation,str) or not designation.strip():errors.append("tail_designation_unresolved")
        if not isinstance(basis,str) or not basis.strip():errors.append("tail_rationale_unresolved")
        if p["state"]!="active" or _value(p["disposition"])!="protected":errors.append("tail_not_currently_protected")
        regrefs=[r for r in p["reference_refs"] if r["record_type"]=="reference_registry"]
        reg=regrefs[0] if len(regrefs)==1 else None
        expected=[m.binding.data["registry_ref"] for *_,m in slots if m]
        if reg is None or index.resolve(reg) is None or any(reg!=x for x in expected):errors.append("tail_registry_mismatch_or_missing")
        declarations=p.get("extensions",{}).get("longitudinal_tail")
        prereg=declarations.get("registration_ref") if isinstance(declarations,Mapping) and set(declarations)=={"registration_ref"} else None
        if not isinstance(prereg,Mapping) or set(prereg)!={"record_type","record_id","record_version"} or prereg.get("record_type")!="preregistration":prereg=None
        rg=_registration(index,prereg,states,data_role=review.configuration["data_role"]);errors+=list(rg.reasons)
        registration=index.payload((prereg["record_type"],prereg["record_id"])) if prereg and index.resolve(prereg) else None
        if registration is None or not any(r==ref for r in registration["material_refs"]):errors.append("tail_not_in_registered_materials")
        checks=[];mock=p["mock"] or p["data_role"]=="fixture"
        for r in p["review_refs"]:
            obj=index.resolve(r);rp=index.payload((r["record_type"],r["record_id"])) if obj else None
            checks.append(rp is not None and rp["state"]=="active" and rp.get("access","readable")=="readable")
            if rp:mock |= rp["mock"] or rp["data_role"]=="fixture"
        availability="records_available_only" if checks and all(checks) else "unavailable" if checks else "not_supplied"
        members.append(TailMember(classid if classid in CLASS_IDS else None,freeze(ref),p["designation"],p["basis"],freeze(reg),freeze(prereg),
            _gate(errors,rg.qualifiers),availability,tuple(p["review_refs"]),tuple(o for o in observations if o.class_id==classid),mock))
        reasons+=errors
        pending.extend(r for r in p["reference_refs"] if r["record_type"]=="tail")
    return tuple(members),_gate(reasons)


def _request(review,index,r,measurements):
    if r.ref is None or r.status=="contract_error":
        return Request(r.ref,"unavailable",("request_contract_error",),None,None,(),(),(),(),(),Gate("not_requested"),r.data)
    d=r.data;view=d["view"];stype=d["support_type"];threshold=_value(d["threshold"])
    states=tuple(_ref(x) for x in d["state_refs"])
    if len(set(states))!=len(states):return Request(r.ref,"unavailable",("duplicate_requested_state",),stype,view,states,(),(),(),(),Gate("not_requested"),d)
    tr=_resolve(review,_value(d["trajectory_ref"]))
    slots=_slots(review,tr,view,measurements)
    if tr is None:
        slots=[(s,m.panel_ref,None,"observed",m) for s in states for m in measurements if m.state_ref==s and m.view==view]
        slots += [(s,None,None,"missing",None) for s in states if not any(x[0]==s for x in slots)]
    reasons=[]
    if tr and any(s not in {_ref(x) for x in tr.data["state_refs"]} for s in states):reasons.append("requested_state_outside_trajectory")
    if any(i.severity == "inconsistent" for i in r.issues):reasons.append("request_binding_inconsistent")
    by={(s,p):m for s,p,_,_,m in slots};panels=tuple(dict.fromkeys(p for _,p,*_ in slots))
    sets=tuple((m.ref,_set(m,stype,threshold)) for s in states for ss,_,_,status,m in slots if ss==s and status=="observed" and m is not None)
    pairs=[]
    for a,b in zip(states,states[1:]):
        for p in panels:
            am,bm=by.get((a,p)),by.get((b,p)); meanings=_meanings(am,bm)
            # With no shared declared panel, several measurements cannot be
            # selected by storage order. Keep the context rather than pool it.
            if any(sum(m.state_ref==s and m.panel_ref==p and m.view==view for m in measurements)>1 for s in (a,b)):
                meanings=_gate(meanings.reasons+("ambiguous_endpoint_measurement",))
            match=_match(am,bm,budget=_value(d["matched_budget"]))
            if d["comparison_mode"]=="descriptive":match=_gate(match.reasons+("descriptive_comparison_requested",),match.qualifiers)
            elif _value(d["matched_budget"]) is None:match=_gate(match.reasons+("matched_budget_unresolved",),match.qualifiers)
            start,end,distance,clock,intermediate=_clock(tr,a,b,review)
            pairs.append(Pair(a,b,p,am.ref if am else None,bm.ref if bm else None,
                set_change(_set(am,stype,threshold),_set(bm,stype,threshold),meaning_gate=meanings,matching_gate=match),start,end,distance,clock,intermediate))
    observations=_observations(slots,stype,threshold,CLASS_IDS)
    tails,tg=_tail_ledger(index,review,r,slots,observations)
    if not states:reasons.append("empty_requested_state_set")
    if not sets:reasons.append("no_observed_measurements")
    return Request(r.ref,"unavailable" if reasons else "available",_reasons(reasons),stype,view,states,sets,tuple(pairs),observations,tails,tg,d)


def _curve(review,t,view,measurements):
    slots=_slots(review,t,view,measurements)
    panels=tuple(_ref(p) for p in t.data["panel_refs"] if (pb:=_resolve(review,p)) is None or pb.data["view"]==view)
    points=[];reasons=[];by_panel={};clock_reasons=[]
    if any(_resolve(review,p) is None for p in t.data["panel_refs"]):
        reasons.append("declared_panel_binding_unavailable")
    for s in t.data["state_refs"]:
        sr=_ref(s);subset=[x for x in slots if x[0]==sr];values=[];refs=[]
        for _,p,_,status,m in subset:
            val=m.diversity if m else _scalar("gini_simpson_diversity",status="unavailable",reasons=(status,))
            values.append(val);refs.append(m.ref if m else None)
            if m:
                reasons+=list(m.matched_gate.reasons)
                if p in by_panel:reasons+=list(_match(by_panel[p],m).reasons)
                else:by_panel[p]=m
        point=CurvePoint(sr,subset[0][2] if subset else None,panels,tuple(refs),tuple(x[3] for x in subset),tuple(values),
                         _mean("mean_panel_diversity",values,max_bits=review.limits["max_exact_bits"]))
        points.append(point)
    if not panels:reasons.append("no_declared_panels_for_view")
    for a,b in zip(t.data["state_refs"],t.data["state_refs"][1:]):clock_reasons+=list(_clock(t,_ref(a),_ref(b),review)[3].reasons)
    for issue in t.issues:
        if issue.code in {"duplicate_trajectory_panel","duplicate_observation_slot","observation_outside_selected_path","trajectory_path_lengths","trajectory_repeated_state","observation_schedule_incomplete"}:
            reasons.append(issue.code)
    return Curve(t.ref,_ref(t.data["root_ref"]),t.details.get("dependency_group"),view,panels,tuple(points),
        _gate(reasons,("validity_conditioned",) if view=="classified_valid" else ()),_gate(clock_reasons),
        tuple(Fraction(1,len(panels)) for _ in panels))


def _stage_links(review,measurements,index):
    result=[]
    for t in review.objects:
        if not t.ref or t.ref.object_kind!="transition" or t.status=="contract_error":continue
        d=t.data;parentdata=_value(d["parent_refs"]);parents=tuple(_ref(x) for x in parentdata or ())
        child=_ref(d["child_ref"]);allrefs=parents+(child,)
        states=[review.get(x.object_kind,x.object_id,x.object_version) for x in allrefs]
        reasons=[];changes=[]
        if not parents:reasons.append("stage_parents_unknown")
        if t.status!="record_consistent":reasons.append("stage_transition_limited")
        if any(s is None or s.data["state_kind"]!="corpus" for s in states):reasons.append("not_linked_corpus_stages")
        units=[]
        if any(s and any(i.code in {"artifact_not_acquired","subject_identity_unknown","core_reference_unresolved"} for i in s.issues) for s in states):
            reasons.append("corpus_material_evidence_unavailable")
        for state in states:
            ident=_value(state.data["subject_identity"]) if state else None
            if state and state.data["state_kind"]=="corpus" and ident is not None:
                units.append(ident["unit"])
                if not ident["material_refs"]:reasons.append("corpus_material_scope_unlinked")
            else:reasons.append("corpus_identity_unresolved")
        if len(set(units))>1:reasons.append("corpus_stage_unit_mismatch")
        if states and all(st and st.data["state_kind"]=="corpus" for st in states):
            inputs=[x for st in states[:-1] for x in ((_value(st.data["subject_identity"]) or {}).get("material_refs",()))]
            outputs=(_value(states[-1].data["subject_identity"]) or {}).get("material_refs",())
            mappings=[]
            for ref in d["evidence"]["process"]:
                payload=index.payload((ref["record_type"],ref["record_id"])) if index.resolve(ref) else None
                record=payload.get("extensions",{}).get("longitudinal_material_scope") if payload else None
                if isinstance(record,Mapping):mappings.append(record)
            expected={"transition_ref":vars(t.ref),"input_material_refs":tuple(inputs),"output_material_refs":tuple(outputs)}
            if not any(dict(rec)==expected for rec in mappings):
                reasons.append("stage_material_mapping_not_supplied")
        # A merge preserves each parent. Matching an output label cannot supply
        # a unique causal source or a synthetic union-of-parents denominator.
        if len(parents)>1:reasons.append("multi_parent_causal_scope_not_established")
        for pa in parents:
            aa=[m for m in measurements if m.state_ref==pa];bb=[m for m in measurements if m.state_ref==child]
            for a in aa:
                candidates=[b for b in bb if b.view==a.view]
                if len(candidates)!=1:continue
                b=candidates[0];mg=_gate(_meanings(a,b).reasons+tuple(reasons))
                changes.append((a.ref,b.ref,set_change(_set(a,"occurrence",None),_set(b,"occurrence",None),
                    meaning_gate=mg,matching_gate=_gate(("stage_retention_not_matched_model_probe",)))))
        stages=tuple((x,s.data["stage_role"] if s else "unknown",tuple(m.ref for m in measurements if m.state_ref==x)) for x,s in zip(allrefs,states))
        result.append(StageTransition(t.ref,d["transition_kind"],parents,child,tuple(s[1] for s in stages),d["contributions"],_gate(reasons),tuple(changes),stages))
    return tuple(result)


def observe_longitudinal(bundle: LoadedBundle, *, review: lr.LongitudinalReview | None=None,
                         populations: PopulationCollection | None=None) -> ObservedStudy:
    """Describe the requested observed layer, with no inference from future requests.

    Supplied components must equal current recomputation, including actual bytes
    and full M admission/inventory context. A nominal matching ID is insufficient.
    """
    if not isinstance(bundle,LoadedBundle):raise InputError("loaded_bundle_required")
    fresh=lr.review_longitudinal(bundle)
    if review is not None:
        lr.assert_current(review,bundle)
        if review!=fresh:raise InputError("altered_longitudinal_binding")
    review=fresh
    if not review.requested or review.configuration is None:
        return ObservedStudy(review.requested,review.status,review.input_context_sha256,review,None,
                             reasons=tuple(i.code for i in review.issues))
    if "observed" not in review.configuration["capabilities"]:
        return ObservedStudy(True,"not_requested",review.input_context_sha256,review,None,
                             reasons=("observed_capability_not_declared",))
    work = (len(review.configuration["measurements"])*len(CLASS_IDS) +
        sum(len(t["state_refs"])*max(1,len(t["panel_refs"]))*len(CLASS_IDS)
            for t in review.configuration["trajectories"] if isinstance(t,Mapping) and isinstance(t.get("state_refs"),(tuple,list)) and isinstance(t.get("panel_refs"),(tuple,list))))
    work *= 1+len(review.configuration["observed_requests"])
    if work > review.limits["max_link_objects"]:
        return ObservedStudy(True,"unavailable",review.input_context_sha256,review,None,reasons=("observed_workload_limit",))
    current=build_populations(bundle)
    if populations is not None and (not isinstance(populations,PopulationCollection) or populations!=current):
        raise InputError("stale_longitudinal_populations")
    index=EvidenceIndex(bundle);cells={c.inventory.cell_id:c for c in current.cells}
    summaries=tuple(_measurement(bundle,review,index,m,cells,current.inventory.cross_cell_groups) for m in review.objects
                    if m.ref and m.ref.object_kind=="measurement" and m.status!="contract_error")
    requests=tuple(_request(review,index,r,summaries) for r in review.objects if r.ref and r.ref.object_kind=="observed_request")
    trajectories=[t for t in review.objects if t.ref and t.ref.object_kind=="trajectory" and t.status!="contract_error"]
    curves=tuple(_curve(review,t,view,summaries) for t in trajectories for view in lr.VIEWS
                 if any((_resolve(review,p) is None or _resolve(review,p).data["view"]==view) for p in t.data["panel_refs"]))
    outcome="available_with_limitations" if review.issues or any(r.status!="available" for r in requests) else "available"
    return ObservedStudy(True,outcome,review.input_context_sha256,review,current,summaries,requests,curves,
                         _stage_links(review,summaries,index),tuple(i.code for i in review.issues),statistics_computed=bool(summaries))


def assert_current(study: ObservedStudy,bundle: LoadedBundle) -> None:
    if not isinstance(study,ObservedStudy) or study.input_context_sha256!=lr.input_fingerprint(bundle):
        raise InputError("stale_observed_longitudinal_context")


def combine_root_curves(study: ObservedStudy, trajectory_refs: tuple[lr.ObjectRef,...], *, view="classified_all") -> RootCurve:
    """Equal means on an explicit fixed path-per-dependency-unit selection.

    This descriptive component neither infers independent roots nor resamples.
    The chosen units and common grid are retained; missing units are not dropped.
    """
    if not isinstance(study,ObservedStudy) or not isinstance(trajectory_refs,(list,tuple)) or view not in lr.VIEWS:
        raise InputError("root_curve_request_required")
    refs=tuple(trajectory_refs)
    if any(not isinstance(x,lr.ObjectRef) or x.object_kind!="trajectory" or not is_id(x.object_id) or not is_id(x.object_version) for x in refs):raise InputError("trajectory_references_required")
    reasons=[];curves=[]
    if not refs or len(set(refs))!=len(refs):reasons.append("empty_or_duplicate_root_path_selection")
    if len(refs)>lr.LIMITS["max_trajectories"]:raise InputError("root_curve_workload_limit")
    for ref in refs:
        found=[c for c in study.curves if c.trajectory_ref==ref and c.view==view]
        if len(found)!=1:reasons.append("selected_curve_unavailable")
        else:curves.append(found[0])
    groups=[_value(c.dependency_group) for c in curves]
    if None in groups:reasons.append("root_dependency_unknown")
    if len(set(groups))!=len(groups) or len({c.root_ref for c in curves})!=len(curves):reasons.append("multiple_paths_per_dependent_root")
    seen_samples=set();seen_ancestors=set()
    for curve in curves:
        samples=set()
        for point in curve.points:
            for mr in point.measurement_refs:
                m=study.measurement(mr) if mr else None
                if m and m.source_cell:samples.update(m.source_cell.inventory.selected_sample_ids)
        if samples & seen_samples:reasons.append("reused_root_observations")
        seen_samples.update(samples)
        root=study.review.get(curve.root_ref.object_kind,curve.root_ref.object_id,curve.root_ref.object_version)
        if root:
            anc=_value(root.data["ancestor_refs"])
            if anc is None:reasons.append("root_ancestry_unknown")
            else:
                current={_ref(r) for r in anc}|{curve.root_ref}
                if current & seen_ancestors:reasons.append("shared_root_ancestry")
                seen_ancestors.update(current)
    grid=tuple(p.round_index for p in curves[0].points) if curves else ()
    panels=curves[0].panel_refs if curves else ()
    if None in grid:reasons.append("root_time_grid_unknown")
    for curve in curves:
        if tuple(p.round_index for p in curve.points)!=grid:reasons.append("root_time_grid_mismatch")
        if curve.panel_refs!=panels:reasons.append("root_panel_set_mismatch")
        reasons+=list(curve.matching_gate.reasons)+list(curve.clock_gate.reasons)
    values=[]
    for i in range(len(grid)):
        values.append(_scalar("mean_root_panel_diversity",status="unavailable",reasons=reasons) if reasons else
            _mean("mean_root_panel_diversity",[c.points[i].mean_panel_diversity for c in curves],
                  max_bits=study.review.limits["max_exact_bits"]))
    return RootCurve(refs,view,grid,tuple(values),tuple(Fraction(1,len(refs)) for _ in refs),
                     _gate(reasons,("declared_root_units_only","independence_not_established","finite_sample_bias_not_corrected")))
