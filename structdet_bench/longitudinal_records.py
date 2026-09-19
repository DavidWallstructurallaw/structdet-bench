"""Versioned passive longitudinal declarations and scoped lineage binding.

No metrics, assays, training, classification, acquisition or code execution.
Record consistency describes supplied declarations, never independent truth.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
from typing import Any, Mapping

from .contracts import (DATA_ROLES, SOURCE_PINS, SUPPORT_RECORD_TYPES, ExactNumber,
                        InputError, freeze, is_hash, is_id, knowledge, validate_ref)
from .comparison_records import configuration_fingerprint
from .evidence import EvidenceIndex
from .local_io import LoadedBundle

PROFILE = "structdet_longitudinal_v1"
VERSION = "0.1"
METHOD = "longitudinal_records_v1"
BASE = "#/analysis_config/extensions/longitudinal"
VIEWS = ("classified_all", "classified_valid")
STAGES = ("probe_output", "generated_candidates", "post_preprocessing", "post_selection", "training_exposure")
CAPABILITIES = ("observed", "categorical_null", "half_life", "support_assay", "recovery")
LIMITS = freeze(dict(max_states=256, max_transitions=1024, max_trajectories=64,
    max_panels_per_trajectory=64, max_measurements=16384, max_link_objects=100000,
    max_interventions_per_assay=16, max_categorical_classes=128, max_trials_per_cell=2048,
    max_tail_summands=2000000, max_exact_bits=262144, max_forecast_steps=10000,
    sensitivity_replicates=2000))
FAMILIES = freeze(dict(states="state", panels="panel", measurements="measurement", roots="root",
    transitions="transition", trajectories="trajectory", observed_requests="observed_request",
    null_scenarios="null_scenario", shl_requests="shl_request", assays="assay",
    interventions="intervention", recovery_episodes="recovery_episode", revisions="revision", replays="replay"))
EVIDENCE_ROLES = freeze(dict(origin=("source", "evidence", "lineage"),
    process=("evidence", "domain_result", "budget", "sampling_plan"),
    independence=("independence_assessment",), validation=("evidence", "domain_result", "audit", "domain_suite"),
    review=("role", "adjudication", "annotation", "integrity_assessment"), correction=("correction", "intake")))
TRANSITIONS = ("categorical_reconstruction", "synthetic_replacement", "accumulation", "subset_reuse",
               "curation", "learning_update", "inference_configuration", "composite")
COMMON = {"object_kind", "object_id", "object_version", "evidence"}


@dataclass(frozen=True)
class ObjectRef:
    object_kind: str
    object_id: str
    object_version: str


@dataclass(frozen=True)
class Issue:
    code: str
    locator: str
    severity: str = "unresolved"


@dataclass(frozen=True)
class ObjectBinding:
    ref: ObjectRef | None
    locator: str
    data: Any = field(repr=False)
    status: str = "record_consistent"
    issues: tuple[Issue, ...] = ()
    details: Any = field(default=None, repr=False)
    mock_evidence: bool = False
    substantive_validation_performed: bool = False


@dataclass(frozen=True)
class LongitudinalReview:
    requested: bool
    status: str
    configuration: Any = field(repr=False)
    input_context_sha256: str | None = None
    configuration_sha256: str | None = None
    objects: tuple[ObjectBinding, ...] = ()
    issues: tuple[Issue, ...] = ()
    limits: Any = field(default=None, repr=False)
    work: Any = field(default=None, repr=False)
    bound_cell_ids: tuple[str, ...] = ()
    method: str = METHOD
    statistics_computed: bool = False
    substantive_validation_performed: bool = False

    def get(self, kind: str, identity: str, version: str) -> ObjectBinding | None:
        """Resolve only one exact, shape-valid version. No latest-version fallback."""
        ref = ObjectRef(kind, identity, version)
        found = [x for x in self.objects if x.ref == ref and x.status != "contract_error"]
        return found[0] if len(found) == 1 else None


def _require(condition, code):
    if not condition:
        raise InputError(code)


def _object(v, keys):
    _require(isinstance(v, Mapping) and set(v) == set(keys), "longitudinal_field_set")
    return v


def _text(v):
    _require(isinstance(v, str) and bool(v.strip()), "longitudinal_text_required")


def _id(v):
    _require(is_id(v), "longitudinal_id_required")


def _bool(v):
    _require(type(v) is bool, "longitudinal_boolean_required")


def _integer(v, minimum=0, maximum=2**63-1):
    _require(type(v) is int and minimum <= v <= maximum, "longitudinal_integer_or_limit")


def _enum(*values):
    def check(v):
        _require(isinstance(v, str) and v in values, "longitudinal_enum")
    return check


def _list(check, minimum=0, maximum=100000):
    def validate(v):
        _require(isinstance(v, (tuple, list)) and minimum <= len(v) <= maximum, "longitudinal_list_or_limit")
        for x in v:
            check(x)
    return validate


def _nullable(check):
    def validate(v):
        if v is not None:
            check(v)
    return validate


def _tag(check):
    def validate(v):
        k = knowledge(v)
        if k.state == "known":
            check(k.value)
    return validate


def _value(v):
    k = knowledge(v)
    return k.value if k.state == "known" else None


def _hash(v):
    _require(is_hash(v), "longitudinal_digest_required")


def _time(v):
    _text(v)
    try:
        t = datetime.fromisoformat(v)
    except (ValueError, OverflowError) as exc:
        raise InputError("longitudinal_timestamp_required") from exc
    _require(t.tzinfo is not None and t.utcoffset() is not None, "longitudinal_time_offset_required")


def _decimal(v, *, positive=False, probability=False):
    # Shape validation only. No tail sum, fit, normalization or threshold decision.
    if isinstance(v, ExactNumber):
        token = v.token
    elif type(v) is int:
        _integer(v); token = str(v)
    else:
        _require(isinstance(v, str), "longitudinal_exact_number_required"); token = v
    _require(len(token) <= 1024, "longitudinal_number_limit")
    ExactNumber(token)
    try:
        d = Decimal(token)
        _require(abs(d.as_tuple().exponent) <= 100000, "longitudinal_exponent_limit")
        _require(d > 0 if positive else d >= 0, "longitudinal_number_range")
        if probability:
            _require(d <= 1, "longitudinal_probability_range")
    except (InvalidOperation, OverflowError) as exc:
        raise InputError("longitudinal_number_range") from exc


def _prob(v):
    _decimal(v, positive=True, probability=True)


def _core(*kinds):
    def validate(v):
        validate_ref(v)
        _require(v["record_type"] in kinds, "longitudinal_core_reference_kind")
    return validate


def _ref(*kinds):
    def validate(v):
        _object(v, ("object_kind", "object_id", "object_version"))
        _require(v["object_kind"] in kinds, "longitudinal_reference_kind")
        _id(v["object_id"]); _id(v["object_version"])
    return validate


def _key(v):
    return ObjectRef(v["object_kind"], v["object_id"], v["object_version"])


def _shape(v, fields):
    _object(v, fields)
    for key, check in fields.items():
        check(v[key])


def _evidence(v):
    _object(v, EVIDENCE_ROLES)
    for role, kinds in EVIDENCE_ROLES.items():
        _list(_core(*kinds))(v[role])


def _subject(v, kind):
    if kind == "model_system":
        _shape(v, {k: _tag(_text) for k in ("parameter_identity", "serving_identity", "retrieval_identity", "tool_identity", "system_identity")} |
               {"checkpoint_sha256": _tag(_nullable(_hash))})
    elif kind == "corpus":
        _shape(v, dict(corpus_identity=_tag(_text), content_sha256=_tag(_hash),
            unit=_enum("documents", "training_rows", "tokens", "weighted_exposures"),
            material_refs=_list(_core("artifact", "raw_artifact"))))
    else:
        _shape(v, dict(scenario_identity=_id, classes=_list(_id, 1, 128)))


def _schedule(v):
    _shape(v, dict(state_ref=_ref("state"), panel_ref=_ref("panel"),
        recursive_round_index=_tag(_integer),
        observation_status=_enum("observed", "missing", "intentionally_unsampled", "planned"),
        measurement_ref=_tag(_nullable(_ref("measurement"))), reason=_tag(_text), evidence=_evidence))


def _contribution(v):
    _shape(v, dict(parent_ref=_ref("state"), weight=_tag(_decimal),
        unit=_enum("documents", "training_rows", "tokens", "sampling_probability", "reproductive_weight"), evidence=_evidence))


def _trial(v):
    _shape(v, dict(trial_id=_id, intervention_ref=_ref("intervention"),
        measurement_ref=_tag(_nullable(_ref("measurement"))), sample_ref=_tag(_nullable(_core("realization"))),
        status=_enum("planned", "observed", "failed", "missing", "unresolved"), evidence=_evidence))


def _schemas(limits):
    s = _ref("state"); m = _ref("measurement"); p = _ref("panel"); tr = _ref("trajectory")
    # Later estimators consume these requests. This module validates declarations only.
    return {
        "state": dict(state_kind=_enum("model_system", "corpus", "categorical_scenario"),
            stage_role=_enum(*STAGES), state_time=_tag(_time), subject_identity=lambda _: None,
            ancestor_refs=_tag(_list(s)), measurement_refs=_list(m)),
        "panel": dict(frame_ref=_core("frame"), protocol_ref=_core("protocol"), registry_ref=_core("reference_registry"),
            stage_role=_enum(*STAGES), view=_enum(*VIEWS), planned_realizations=_tag(lambda x:_integer(x,1)), selection_rule=_tag(_text)),
        "measurement": dict(state_ref=s, cell_ref=_core("cell"), panel_ref=_tag(p), frame_ref=_core("frame"),
            protocol_ref=_core("protocol"), registry_ref=_core("reference_registry"), view=_enum(*VIEWS),
            data_role=_enum(*DATA_ROLES), planned_realizations=_tag(lambda x:_integer(x,1)),
            selection_rule=_tag(_text), sample_refs=_tag(_list(_core("realization"))), budget_ref=_tag(_core("budget"))),
        "root": dict(ancestor_refs=_tag(_list(_ref("root"))), dependency_group=_tag(_id),
            independence_ref=_tag(_core("independence_assessment"))),
        "transition": dict(transition_kind=_enum(*TRANSITIONS), parent_refs=_tag(_list(s,1)), child_ref=s,
            round_distance=_tag(_integer), event_time=_tag(_time),
            process_status=_enum("planned", "attempted", "completed", "failed", "unknown"),
            effective_change=_tag(_bool), parameter_change=_tag(_bool), retained_parameters=_tag(_bool),
            retained_data_refs=_tag(_list(_core("artifact", "raw_artifact"))),
            contributions=_list(_contribution), external_contribution_refs=_list(_core("source", "evidence")),
            component_refs=_list(_ref("transition"))),
        "trajectory": dict(state_refs=_list(s,1,limits["max_states"]), transition_refs=_list(_ref("transition")),
            round_coordinates=_list(_tag(_integer),1,limits["max_states"]),
            panel_refs=_list(p,0,limits["max_panels_per_trajectory"]), root_ref=_ref("root"),
            schedule=_list(_schedule,0,limits["max_measurements"]), registration_ref=_tag(_core("preregistration"))),
        "observed_request": dict(state_refs=_list(s), trajectory_ref=_tag(_nullable(tr)), view=_enum(*VIEWS),
            support_type=_enum("occurrence", "empirical_frequency"), threshold=_tag(_nullable(_prob)),
            matched_budget=_tag(lambda x:_integer(x,1)), protected_tail_ref=_tag(_core("tail")),
            comparison_mode=_enum("matched", "descriptive")),
        "null_scenario": dict(classes=_list(_id,1,limits["max_categorical_classes"]),
            p=_list(_decimal,1,limits["max_categorical_classes"]), n=_tag(lambda x:_integer(x,1)),
            steps=lambda x:_integer(x,0,limits["max_forecast_steps"]),
            q=_tag(_nullable(_list(_decimal,1,limits["max_categorical_classes"]))),
            schedule=_tag(_nullable(_list(lambda x:_integer(x,1),0,limits["max_forecast_steps"]))),
            assumptions=lambda x:_shape(x,{k:_tag(_bool) for k in ("finite_multinomial", "fixed_classes", "closed", "empirical_reconstruction", "exogenous_schedule")}),
            child_counts=_list(_list(_integer,1,limits["max_categorical_classes"]),0,limits["max_forecast_steps"])),
        "shl_request": dict(trajectory_ref=tr, start_ref=s, end_ref=s, anchor_ref=s, view=_enum(*VIEWS),
            fit_mode=_enum("local", "anchored"), residual_criterion=_tag(_decimal), panel_refs=_list(p),
            sensitivity_ref=_tag(_nullable(_ref("replay"))), registration_ref=_tag(_core("preregistration"))),
        "assay": dict(state_ref=s, family_id=_id, family_version=_id,
            intervention_refs=_list(_ref("intervention"),1,limits["max_interventions_per_assay"]),
            success_event=_enum("class_membership", "valid_class_membership"), registry_ref=_core("reference_registry"),
            tau=_prob, alpha=_prob, allocation=_enum("bonferroni_equal"), trials=_list(_trial),
            iid_evidence_ref=_tag(_core("independence_assessment", "evidence"))),
        "intervention": dict(pre_state_ref=s, post_state_ref=s,
            intervention_kind=_enum("inference_configuration", "tools", "retrieval", "evidence", "curation", "training"),
            parameters_changed=_tag(_bool), direct_answer_injection=_tag(_bool),
            external_refs=_list(_core("source", "evidence", "artifact", "raw_artifact"))),
        "recovery_episode": dict(pre_assay_ref=_ref("assay"), post_assay_ref=_ref("assay"),
            intervention_ref=_ref("intervention"), registry_ref=_core("reference_registry"), criterion_version=_id,
            non_injection_ref=_tag(_core("evidence")), external_validation_refs=_list(_core("evidence", "domain_result", "audit"))),
        "revision": dict(revision_kind=_enum("metadata", "membership", "validity", "schema", "lineage", "independence"),
            event_type=_enum("correction", "distributional_reopening_event", "structural_reopening_event"),
            affected_refs=_list(_ref(*FAMILIES.values())), original_refs=_list(_core("artifact", "raw_artifact")),
            old_identity=_tag(_text), new_identity=_tag(_text),
            disposition=_enum("received", "provisional", "applied", "rejected", "withdrawn")),
        "replay": dict(artifact_ref=_core("artifact", "raw_artifact"), expected_sha256=_hash,
            method_id=_id, plan_sha256=_hash, unit_refs=_list(_ref("root", "trajectory"))),
    }


def input_fingerprint(bundle: LoadedBundle) -> str:
    """Hash actual loaded bytes and typed/raw context, with no file reopening."""
    _require(isinstance(bundle, LoadedBundle), "loaded_bundle_required")
    return configuration_fingerprint({"domain": METHOD, "manifest": bundle.manifest.data if bundle.manifest else None,
        "records": [(r.source,r.line,r.raw,r.record.data if r.record else None) for r in bundle.records],
        "snapshots": [(k,s.sha256,s.size_bytes,len(s.content),hashlib.sha256(s.content).hexdigest()) for k,s in sorted(bundle.snapshots.items())],
        "limits": vars(bundle.limits), "artifacts": [vars(a) for a in bundle.artifacts],
        "diagnostics": [vars(d) for d in bundle.diagnostics], "complete": bundle.acquisition_complete})


def assert_current(review: LongitudinalReview, bundle: LoadedBundle) -> None:
    _require(isinstance(review, LongitudinalReview) and review.input_context_sha256 == input_fingerprint(bundle),
             "stale_longitudinal_context")


def _walk(value):
    """Iterative bounded-shape walk. Caller has checked depth and total size."""
    pending = [(value, "")]
    while pending:
        v,path = pending.pop()
        if isinstance(v, Mapping):
            yield v,path
            pending.extend((x,path+"/"+k) for k,x in reversed(tuple(v.items())))
        elif isinstance(v, (tuple,list)):
            pending.extend((x,path+"/"+str(i)) for i,x in reversed(tuple(enumerate(v))))


def _preflight(raw, depth_limit):
    _require(isinstance(raw, Mapping), "longitudinal_object_required")
    header = {"version","profile","study_id","study_version","data_role","registered_design_ref", "source_pins","method_id","capabilities","limits"}
    _object(raw,header|set(FAMILIES))
    _require(raw["version"] == VERSION and raw["profile"] == PROFILE, "unsupported_longitudinal_profile_or_version")
    _id(raw["study_id"]); _id(raw["study_version"]); _enum(*DATA_ROLES)(raw["data_role"])
    _require(raw["source_pins"] == SOURCE_PINS and raw["method_id"] == METHOD, "longitudinal_source_or_method_identity")
    _tag(_core("preregistration"))(raw["registered_design_ref"])
    _list(_enum(*CAPABILITIES))(raw["capabilities"])
    _require(len(set(raw["capabilities"])) == len(raw["capabilities"]), "duplicate_longitudinal_capability")
    _require(isinstance(raw["limits"],Mapping) and not set(raw["limits"])-set(LIMITS), "longitudinal_limit_fields")
    limits = dict(LIMITS)
    for k,v in raw["limits"].items():
        _integer(v,1,LIMITS[k]); limits[k]=v
    _require(limits["sensitivity_replicates"] == 2000, "longitudinal_replicate_identity")
    count=0; pending=[(raw,0)]
    # LoadedBundle is normally a tree. An explicit traversal cap also bounds
    # manually constructed cyclic/aliased component inputs without recursion.
    while pending:
        v,depth=pending.pop(); count+=1
        _require(count <= limits["max_link_objects"], "longitudinal_link_object_limit")
        _require(depth <= depth_limit, "longitudinal_depth_limit")
        if isinstance(v,Mapping):
            _require(all(isinstance(k,str) for k in v), "longitudinal_key_type")
            pending.extend((x,depth+1) for x in v.values())
        elif isinstance(v,(tuple,list)):
            pending.extend((x,depth+1) for x in v)
    for name in FAMILIES:
        _list(lambda _:None)(raw[name])
    for name,lim in (("states","max_states"),("transitions","max_transitions"),("trajectories","max_trajectories"),("measurements","max_measurements")):
        _require(len(raw[name])<=limits[lim], "longitudinal_"+name+"_limit")
    return limits,count


class _Review:
    def __init__(self,bundle,raw,limits):
        self.bundle,self.raw,self.limits=bundle,raw,limits
        self.index=EvidenceIndex(bundle)
        self.rows=[]; self.by={}; self.issues=defaultdict(list); self.details=defaultdict(dict); self.mock=defaultdict(bool)
        schemas=_schemas(limits)
        for name,kind in FAMILIES.items():
            for i,data in enumerate(raw[name]):
                loc=BASE+"/"+name+"/"+str(i); ref=None
                try:
                    _require(isinstance(data,Mapping), "longitudinal_record_object")
                    _id(data.get("object_id")); _id(data.get("object_version"))
                    ref=ObjectRef(kind,data["object_id"],data["object_version"])
                    _require(data.get("object_kind")==kind,"longitudinal_object_kind")
                    _shape(data,{"object_kind":_enum(kind),"object_id":_id,"object_version":_id,"evidence":_evidence}|schemas[kind])
                    if kind=="state":
                        _tag(lambda x:_subject(x,data["state_kind"]))(data["subject_identity"])
                        identity=_value(data["subject_identity"])
                        if identity is not None and data["state_kind"]=="categorical_scenario":
                            _require(len(identity["classes"]) <= limits["max_categorical_classes"], "categorical_state_class_limit")
                except (InputError,TypeError,ValueError,KeyError) as exc:
                    self.issues[loc].append(Issue(exc.code if isinstance(exc,InputError) else "malformed_longitudinal_record",loc,"contract_error"))
                self.rows.append((ref,loc,data))
        counts=Counter((r.object_kind,r.object_id) for r,_,_ in self.rows if r)
        for ref,loc,data in self.rows:
            if ref and counts[(ref.object_kind,ref.object_id)]>1:
                self.add(loc,"duplicate_or_conflicting_object_identity",severity="contract_error")
            if ref and not self.issues[loc]: self.by[ref]=(loc,data)
        self.bad_descendants=set()
        self.support_visits=0

    def add(self,loc,code,field="",severity="unresolved"):
        issue=Issue(code,loc+("/"+field if field else ""),severity)
        if issue not in self.issues[loc]:self.issues[loc].append(issue)

    def lookup(self,ref):
        return self.by.get(_key(ref))

    def core(self,ref):
        return self.index.resolve(ref)

    def support(self,ref,loc,field):
        """Check recorded dependencies; review/lineage cycles are not DAG edges."""
        pending=[(ref,False)]; active=set(); done=set(); first_key=(ref["record_type"],ref["record_id"])
        while pending:
            r,exit_=pending.pop(); key=(r["record_type"],r["record_id"])
            if exit_:active.discard(key);done.add(key);continue
            if key in active:
                self.add(loc,"circular_decisive_evidence",field);continue
            if key in done:continue
            self.support_visits+=1
            if self.support_visits>self.limits["max_link_objects"]:
                self.add(loc,"evidence_link_limit",field);return
            active.add(key);pending.append((r,True))
            record=self.core(r)
            if record is None:
                self.add(loc,"core_reference_unresolved",field);continue
            if key[0] in SUPPORT_RECORD_TYPES:
                p=self.index.payload(key)
                if p is None:
                    self.add(loc,"evidence_payload_unresolved",field);continue
                self.mock[loc] |= p["mock"] or p["data_role"]=="fixture"
                if p["state"]!="active" or p.get("access","readable")!="readable" or p.get("conflict_status")=="unresolved":
                    self.add(loc,"evidence_inactive_unreadable_or_conflicted",field)
                if self.index.affected(key,{"metadata","independence","schema","membership","validity"}):
                    self.add(loc,"evidence_under_correction",field)
                target=p.get("extensions",{}).get("longitudinal_target")
                current=next((r for r,l,_ in self.rows if l==loc),None)
                if key==first_key and target is not None and (not isinstance(target,Mapping) or current is None or dict(target)!=vars(current)):
                    self.add(loc,"evidence_longitudinal_target_mismatch",field)
                # parent_ref, correction target and review relations are retained
                # for audit; only explicit decisive dependencies recurse here.
                for n in ("evidence_refs","reviewer_refs"):
                    pending.extend((x,False) for x in p.get(n,()))
            elif key[0] in {"artifact","raw_artifact"}:
                a=[x for x in self.bundle.artifacts if x.record_key==key[0]+":"+key[1]]
                if len(a)!=1 or a[0].status!="snapshot_read":self.add(loc,"artifact_not_acquired",field)
        if self.mock[loc] and self.raw["data_role"]!="fixture":self.add(loc,"mock_evidence_for_nonfixture",field)

    def links(self):
        for ref,loc,data in self.rows:
            if not ref or ref not in self.by:continue
            for v,path in _walk(data):
                if set(v)=={"object_kind","object_id","object_version"}:
                    if _key(v) not in self.by:self.add(loc,"object_reference_unresolved",path.lstrip("/"))
                elif set(v)=={"record_type","record_id","record_version"}:
                    if self.core(v) is None:self.add(loc,"core_reference_unresolved",path.lstrip("/"))
                    if v["record_type"] in SUPPORT_RECORD_TYPES or v["record_type"] in {"artifact","raw_artifact"}:
                        self.support(v,loc,path.lstrip("/"))
        r=_value(self.raw["registered_design_ref"])
        if r is None:self.add(BASE,"registered_design_unresolved","registered_design_ref")
        else:self.support(r,BASE,"registered_design_ref")

    def measurements(self):
        used=defaultdict(list)
        selections=self.bundle.manifest.data["analysis_config"]["selection"]
        for ref,(loc,d) in self.by.items():
            if ref.object_kind=="panel":
                self.details[loc]["role"]="recurring_probe_stratum_not_training_replicate"
            if ref.object_kind!="measurement":continue
            state=self.lookup(d["state_ref"]);cell=self.core(d["cell_ref"])
            used[(d["cell_ref"]["record_id"],d["view"])].append((loc,_key(d["state_ref"])))
            detail=self.details[loc]
            detail.update(cell_ref=d["cell_ref"],view=d["view"],binding_level="record_identity_only_no_population_admission")
            for name in ("budget_ref",):
                v=_value(d[name])
                if v is not None:self.support(v,loc,name)
            if d["data_role"]!=self.raw["data_role"]:self.add(loc,"measurement_material_role_mismatch",severity="inconsistent")
            if state and ref not in {_key(x) for x in state[1]["measurement_refs"]}:
                self.add(loc,"measurement_not_linked_by_state",severity="inconsistent")
            if cell is None:continue
            frame=self.core(d["frame_ref"]);prot=self.core(d["protocol_ref"]);reg=self.core(d["registry_ref"])
            if d["frame_ref"]["record_id"]!=cell.data["frame_id"]:self.add(loc,"measurement_frame_mismatch",severity="inconsistent")
            if d["protocol_ref"]["record_id"]!=cell.data["generation_protocol_id"] or (prot and prot.data["generation_protocol_version"]!=cell.data["generation_protocol_version"]):
                self.add(loc,"measurement_protocol_mismatch",severity="inconsistent")
            if frame and reg and (frame.data["reference_registry_id"]!=reg.data["reference_registry_id"] or frame.data["reference_registry_version"]!=reg.data["reference_registry_version"]):
                self.add(loc,"measurement_registry_mismatch",severity="inconsistent")
            detail.update(frame=frame.data if frame else None,protocol=prot.data if prot else None,
                          registry=reg.data if reg else None,cell=cell.data)
            if state:
                sd=state[1];identity=_value(sd["subject_identity"])
                if sd["state_kind"]=="categorical_scenario":self.add(loc,"categorical_state_cannot_bind_empirical_cell",severity="inconsistent")
                elif sd["state_kind"]=="model_system" and identity is not None:
                    declared=_value(identity["parameter_identity"]);recorded=_value(cell.data["checkpoint_identifier"])
                    if declared is not None and recorded is not None and declared!=recorded:
                        self.add(loc,"measurement_model_state_mismatch",severity="inconsistent")
                    detail["model_parameter_identity"]=identity["parameter_identity"]
            ss=[s for s in selections if s["analysis_cell_id"]==cell.record_id]
            selected=_value(ss[0]["selected_sample_ids"]) if len(ss)==1 else None
            declared=_value(d["sample_refs"])
            detail["selected_sample_ids"]=selected
            if selected is None or declared is None:self.add(loc,"measurement_selection_unresolved","sample_refs")
            else:
                ids=[x["record_id"] for x in declared]
                if len(ids)!=len(set(ids)) or set(ids)!=set(selected):self.add(loc,"measurement_selected_identity_mismatch",severity="inconsistent")
                for x in declared:
                    record=self.core(x)
                    if record and record.data["analysis_cell_id"]!=cell.record_id:self.add(loc,"sample_cell_mismatch",severity="inconsistent")
            if len(ss)==1 and _value(d["selection_rule"])!=_value(ss[0]["selection_basis"]):
                self.add(loc,"selection_rule_mismatch",severity="inconsistent")
            if _value(d["planned_realizations"]) is None:self.add(loc,"measurement_budget_unresolved","planned_realizations")
            # Sampling deficits are retained for later matched-population gates.
            detail["planned_realizations"]=d["planned_realizations"]
            panel=_value(d["panel_ref"])
            if panel is not None and self.lookup(panel):
                pd=self.lookup(panel)[1]
                for k in ("frame_ref","protocol_ref","registry_ref","view","planned_realizations","selection_rule"):
                    if d[k]!=pd[k]:self.add(loc,"panel_binding_mismatch",k,"inconsistent")
                if state and state[1]["stage_role"]!=pd["stage_role"]:self.add(loc,"panel_stage_mismatch",severity="inconsistent")
        for entries in used.values():
            if len({s for _,s in entries})>1:
                for loc,_ in entries:self.add(loc,"same_measurement_reused_as_new_state",severity="inconsistent")

    def states(self):
        for ref,(loc,d) in self.by.items():
            if ref.object_kind=="root":
                self.details[loc].update(independence_established=False,dependency_group=d["dependency_group"])
                if _value(d["dependency_group"]) is None:self.add(loc,"dependency_group_unknown")
                if _value(d["ancestor_refs"]) is None:self.add(loc,"root_ancestry_unknown")
                x=_value(d["independence_ref"])
                if x is not None:self.support(x,loc,"independence_ref")
                continue
            if ref.object_kind!="state":continue
            k=d["state_kind"];stage=d["stage_role"]
            if (k=="model_system" and stage!="probe_output") or (k=="corpus" and stage=="probe_output"):
                self.add(loc,"state_stage_unit_mismatch",severity="inconsistent")
            self.details[loc].update(state_kind=k,stage_role=stage,independence_established=False)
            if _value(d["subject_identity"]) is None:self.add(loc,"subject_identity_unknown")
            if _value(d["ancestor_refs"]) is None:self.add(loc,"state_ancestry_unknown")
            self.details[loc]["ancestry_status"]="unresolved" if _value(d["ancestor_refs"]) is None else "declared_only"
            for x in d["measurement_refs"]:
                found=self.lookup(x)
                if found and _key(found[1]["state_ref"])!=ref:self.add(loc,"state_measurement_target_mismatch",severity="inconsistent")

    def transitions(self):
        adjacency=defaultdict(set);incoming=defaultdict(list); edge_rows=[]
        for ref,(loc,d) in self.by.items():
            if ref.object_kind!="transition":continue
            parents=_value(d["parent_refs"]);child=_key(d["child_ref"]);distance=_value(d["round_distance"])
            detail=self.details[loc];detail.update(process_status=d["process_status"],effective_change=d["effective_change"],
                parameter_change=d["parameter_change"],round_distance=d["round_distance"],independence_established=False)
            if d["process_status"]!="completed":self.add(loc,"transition_not_completed")
            if not d["evidence"]["process"]:self.add(loc,"transition_process_evidence_missing")
            if parents is None:self.add(loc,"transition_parents_unknown")
            elif len({_key(p) for p in parents})!=len(parents):self.add(loc,"duplicate_parent",severity="inconsistent")
            if child not in self.by:self.add(loc,"transition_child_unresolved")
            if distance is None:self.add(loc,"recursive_distance_unknown")
            kind=d["transition_kind"]
            if kind in {"curation","inference_configuration"}:
                if distance is not None and distance!=0:self.add(loc,"nonreproduction_clock_increment",severity="inconsistent")
                if _value(d["parameter_change"]) is True:self.add(loc,"fixed_parameter_intervention_changed_parameters",severity="inconsistent")
            elif kind!="composite" and distance is not None and distance!=1:
                self.add(loc,"single_transition_distance_must_be_one",severity="inconsistent")
            if kind!="composite" and d["component_refs"]:self.add(loc,"components_on_noncomposite",severity="inconsistent")
            contribution_keys=[_key(x["parent_ref"]) for x in d["contributions"]]
            if len(set(contribution_keys))!=len(contribution_keys):self.add(loc,"duplicate_parent_contribution",severity="inconsistent")
            if parents is not None and not set(contribution_keys)<={_key(p) for p in parents}:
                self.add(loc,"contribution_not_a_parent",severity="inconsistent")
            if parents and len(parents)>1 and set(contribution_keys)!={_key(p) for p in parents}:
                self.add(loc,"merge_contributions_incomplete")
            for x in d["external_contribution_refs"]:self.support(x,loc,"external_contribution_refs")
            if parents is not None:
                known_parents=[_key(p) for p in parents]
                self.details[loc]["parents"]=tuple(known_parents)
                for p in known_parents:
                    if p not in self.by:self.add(loc,"transition_parent_unresolved")
                    if p==child:self.add(loc,"reproduction_self_cycle",severity="inconsistent")
                    adjacency[p].add(child)
                    if p in self.by and child in self.by:
                        pd,cd=self.by[p][1],self.by[child][1]
                        pk,ck=pd["state_kind"],cd["state_kind"]
                        required={"categorical_reconstruction":"categorical_scenario", "inference_configuration":"model_system", "curation":"corpus"}.get(kind)
                        if required and (pk!=required or ck!=required):self.add(loc,"transition_state_kind_mismatch",severity="inconsistent")
                        if kind=="learning_update" and ck!="model_system":self.add(loc,"learning_target_not_model_state",severity="inconsistent")
                        pi,ci=_value(pd["subject_identity"]),_value(cd["subject_identity"])
                        if pk==ck=="model_system" and pi is not None and ci is not None:
                            ph,ch=_value(pi["checkpoint_sha256"]),_value(ci["checkpoint_sha256"])
                            change=_value(d["parameter_change"])
                            if ph and ch and change is not None and (ph!=ch)!=change:
                                self.add(loc,"parameter_change_identity_conflict",severity="inconsistent")
                        pt,ct=_value(pd["state_time"]),_value(cd["state_time"])
                        et=_value(d["event_time"])
                        if pt and ct and datetime.fromisoformat(pt)>datetime.fromisoformat(ct):self.add(loc,"backward_state_time",severity="inconsistent")
                        if et and ((pt and datetime.fromisoformat(et)<datetime.fromisoformat(pt)) or (ct and datetime.fromisoformat(et)>datetime.fromisoformat(ct))):
                            self.add(loc,"event_outside_state_times",severity="inconsistent")
                        anc=_value(cd["ancestor_refs"])
                        if anc is not None and p not in {_key(a) for a in anc}:self.add(loc,"child_parent_declaration_conflict",severity="inconsistent")
            if kind!="composite":incoming[child].append((ref,loc))
            edge_rows.append((ref,loc,d,child))
        # Kahn residual is precisely a cycle or a descendant blocked by one.
        nodes=set(adjacency)|{c for cs in adjacency.values() for c in cs};indegree={n:0 for n in nodes}
        for cs in adjacency.values():
            for c in cs:indegree[c]+=1
        q=deque(n for n in nodes if indegree[n]==0)
        while q:
            for c in adjacency[q.popleft()]:
                indegree[c]-=1
                if indegree[c]==0:q.append(c)
        cycles={n for n in nodes if indegree[n]>0}
        for ref,loc,d,child in edge_rows:
            if child in cycles:self.add(loc,"reproduction_cycle_or_descendant",severity="inconsistent")
            if len(incoming[child])>1 and d["transition_kind"]!="composite":self.add(loc,"ambiguous_producing_transition",severity="inconsistent")
            if d["transition_kind"]=="composite":self.composite(ref,loc,d)
        # A shape-invalid transition may still name a well-typed child. Preserve
        # that declared uncertainty in descendant history without guessing a parent.
        malformed_children=set()
        for ref,loc,d in self.rows:
            if ref and ref.object_kind=="transition" and ref not in self.by:
                try:
                    _ref("state")(d["child_ref"]);malformed_children.add(_key(d["child_ref"]))
                except (InputError,TypeError,KeyError):pass
        invalid={child for _,loc,_,child in edge_rows if self.issues[loc]} | malformed_children
        pending=list(invalid)
        while pending:
            for c in adjacency[pending.pop()]:
                if c not in invalid:invalid.add(c);pending.append(c)
        self.bad_descendants=invalid
        for ref,loc,d,child in edge_rows:
            if child in invalid and not self.issues[loc]:self.add(loc,"ancestral_transition_unresolved")
        for s in invalid:
            if s in self.by:self.details[self.by[s][0]]["ancestry_status"]="restricted_by_transition_history"

    def composite(self,ref,loc,d):
        parts=d["component_refs"]
        if not parts:self.add(loc,"composite_stages_missing");return
        if len({_key(x) for x in parts})!=len(parts):self.add(loc,"duplicate_composite_stage",severity="inconsistent")
        total=0;previous=None;last=None
        for x in parts:
            part=self.lookup(x)
            if part is None:self.add(loc,"composite_stage_unresolved");return
            p=part[1]
            if p["transition_kind"]=="composite":self.add(loc,"nested_composite_not_supported",severity="inconsistent");return
            parents=_value(p["parent_refs"])
            if p["process_status"]!="completed" or not p["evidence"]["process"] or self.issues[part[0]]:
                self.add(loc,"composite_stage_not_documented")
            if previous is None:
                if parents!=_value(d["parent_refs"]):self.add(loc,"composite_parent_mismatch",severity="inconsistent")
            elif parents is None or previous not in {_key(y) for y in parents}:self.add(loc,"composite_stage_path_mismatch",severity="inconsistent")
            delta=_value(p["round_distance"])
            if delta is None:self.add(loc,"composite_distance_unknown");return
            total+=delta;previous=_key(p["child_ref"]);last=previous
        if last!=_key(d["child_ref"]) or total!=_value(d["round_distance"]):self.add(loc,"composite_distance_or_child_mismatch",severity="inconsistent")
        self.details[loc]["component_round_distance"]=total

    def trajectories(self):
        for ref,(loc,d) in self.by.items():
            if ref.object_kind!="trajectory":continue
            states=[_key(x) for x in d["state_refs"]];edges=[_key(x) for x in d["transition_refs"]]
            coordinates=[_value(x) for x in d["round_coordinates"]]
            detail=self.details[loc];detail.update(selected_path=tuple(states),declared_round_coordinates=d["round_coordinates"],schedule=d["schedule"],
                independent_replicate_established=False,interpolated_observations=0)
            if len(set(states))!=len(states):self.add(loc,"trajectory_repeated_state",severity="inconsistent")
            if len(set(edges))!=len(edges):self.add(loc,"trajectory_repeated_transition",severity="inconsistent")
            if len(coordinates)!=len(states) or len(edges)!=len(states)-1:
                self.add(loc,"trajectory_path_lengths",severity="inconsistent");continue
            if any(c is None for c in coordinates):self.add(loc,"trajectory_clock_unresolved")
            for i,e in enumerate(edges):
                part=self.by.get(e)
                if part is None:self.add(loc,"trajectory_transition_unresolved");continue
                el,ed=part;parents=_value(ed["parent_refs"])
                if parents is None or states[i] not in {_key(x) for x in parents} or _key(ed["child_ref"])!=states[i+1]:
                    self.add(loc,"selected_branch_path_mismatch",severity="inconsistent")
                delta=_value(ed["round_distance"])
                if self.issues[el] or states[i+1] in self.bad_descendants:self.add(loc,"trajectory_lineage_restricted")
                if delta is not None and coordinates[i] is not None and coordinates[i+1] is not None and coordinates[i+1]-coordinates[i]!=delta:
                    self.add(loc,"trajectory_clock_distance_mismatch",severity="inconsistent")
            panels=[_key(x) for x in d["panel_refs"]]
            if len(set(panels))!=len(panels):self.add(loc,"duplicate_trajectory_panel",severity="inconsistent")
            root=self.lookup(d["root_ref"])
            if root:
                detail["dependency_group"]=root[1]["dependency_group"]
                if _value(root[1]["dependency_group"]) is None:self.add(loc,"trajectory_dependency_unknown")
            reg=_value(d["registration_ref"])
            if reg is None:self.add(loc,"trajectory_registration_unknown")
            else:
                self.support(reg,loc,"registration_ref")
                payload=self.index.payload((reg["record_type"],reg["record_id"]))
                registered=_value(payload["registered_at"]) if payload else None
                if registered is not None:
                    try:
                        _time(registered)
                        declared=datetime.fromisoformat(registered)
                        known_times=[_value(self.by[x][1]["state_time"]) for x in states if x in self.by]
                        if any(t is not None and declared>datetime.fromisoformat(t) for t in known_times):
                            self.add(loc,"trajectory_registration_after_state",severity="inconsistent")
                    except InputError:
                        self.add(loc,"trajectory_registration_time_unresolved")
                else:self.add(loc,"trajectory_registration_time_unresolved")
            seen=set();slots=[]
            for i,slot in enumerate(d["schedule"]):
                path="schedule/"+str(i);s,p=_key(slot["state_ref"]),_key(slot["panel_ref"]);key=(s,p)
                if key in seen:self.add(loc,"duplicate_observation_slot",path,"inconsistent")
                seen.add(key)
                if s not in states or p not in panels:self.add(loc,"observation_outside_selected_path",path,"inconsistent")
                elif _value(slot["recursive_round_index"])!=coordinates[states.index(s)]:self.add(loc,"observation_clock_mismatch",path,"inconsistent")
                mr=_value(slot["measurement_ref"]);status=slot["observation_status"]
                if status=="observed":
                    mb=self.lookup(mr) if mr else None
                    if mb is None:self.add(loc,"observed_measurement_unresolved",path)
                    else:
                        ml,md=mb
                        if _key(md["state_ref"])!=s or _value(md["panel_ref"])!=slot["panel_ref"]:self.add(loc,"observation_measurement_mismatch",path,"inconsistent")
                        if self.issues[ml]:self.add(loc,"scheduled_measurement_limited",path)
                elif mr is not None:self.add(loc,"measurement_on_unobserved_slot",path,"inconsistent")
                if status in {"missing","intentionally_unsampled"} and _value(slot["reason"]) is None:self.add(loc,"missingness_reason_unresolved",path)
                slots.append((s,p,status))
            absent={(s,p) for s in states for p in panels}-seen
            if absent:self.add(loc,"observation_schedule_incomplete")
            detail["undeclared_slots"]=tuple(sorted(absent,key=repr));detail["slot_statuses"]=tuple(slots)

    def requests(self):
        group_caps={"observed_request":"observed","null_scenario":"categorical_null","shl_request":"half_life","assay":"support_assay","recovery_episode":"recovery"}
        for ref,(loc,d) in self.by.items():
            kind=ref.object_kind
            if kind in group_caps:
                if group_caps[kind] not in self.raw["capabilities"]:self.add(loc,"request_capability_not_declared",severity="inconsistent")
                self.details[loc]["calculation_status"]="not_evaluated_records_only"
            if kind=="intervention":
                if d["intervention_kind"]=="inference_configuration" and _value(d["parameters_changed"]) is True:
                    self.add(loc,"inference_intervention_parameter_change",severity="inconsistent")
            if kind=="observed_request":
                th=_value(d["threshold"])
                if d["support_type"]=="occurrence" and th is not None:self.add(loc,"threshold_on_occurrence_request",severity="inconsistent")
                if d["support_type"]=="empirical_frequency" and th is None:self.add(loc,"frequency_threshold_unknown")
            elif kind=="null_scenario":
                n=len(d["classes"])
                if len(set(d["classes"]))!=n or len(d["p"])!=n or any(len(x)!=n for x in d["child_counts"]):self.add(loc,"categorical_vector_identity",severity="inconsistent")
                q=_value(d["q"]);schedule=_value(d["schedule"])
                if q is not None and len(q)!=n:self.add(loc,"categorical_target_dimension",severity="inconsistent")
                if schedule is not None and len(schedule)!=d["steps"]:self.add(loc,"categorical_schedule_length",severity="inconsistent")
            elif kind=="shl_request":
                t=self.lookup(d["trajectory_ref"])
                if t:
                    path=[_key(x) for x in t[1]["state_refs"]]
                    keys=[_key(d[k]) for k in ("start_ref","anchor_ref","end_ref")]
                    if any(x not in path for x in keys) or (all(x in path for x in keys) and not path.index(keys[0])==path.index(keys[1])<path.index(keys[2])):
                        self.add(loc,"fit_window_or_anchor_mismatch",severity="inconsistent")
            elif kind=="assay":
                ids=[x["trial_id"] for x in d["trials"]];families={_key(x) for x in d["intervention_refs"]}
                if len(set(ids))!=len(ids) or len(families)!=len(d["intervention_refs"]):self.add(loc,"duplicate_assay_identity",severity="inconsistent")
                counts=Counter(_key(x["intervention_ref"]) for x in d["trials"])
                if any(n>self.limits["max_trials_per_cell"] for n in counts.values()):self.add(loc,"assay_trial_limit",severity="contract_error")
                if not set(counts)<=families:self.add(loc,"trial_outside_assay_family",severity="inconsistent")
                for member in d["intervention_refs"]:
                    spec=self.lookup(member)
                    if spec:
                        ip=spec[1]
                        if ip["pre_state_ref"]!=d["state_ref"]:
                            self.add(loc,"assay_intervention_state_mismatch",severity="inconsistent")
                        if ip["intervention_kind"]=="training" or _value(ip["parameters_changed"]) is True:
                            self.add(loc,"assay_intervention_not_fixed_model",severity="inconsistent")
                samples=[_value(x["sample_ref"]) for x in d["trials"] if _value(x["sample_ref"]) is not None]
                if len({(s["record_type"],s["record_id"]) for s in samples})!=len(samples):self.add(loc,"duplicate_assay_observation",severity="inconsistent")
                for i,trial in enumerate(d["trials"]):
                    sample=_value(trial["sample_ref"])
                    mr=_value(trial["measurement_ref"]); measured=self.lookup(mr) if mr else None
                    if trial["status"]=="observed" and measured is None:
                        self.add(loc,"observed_trial_measurement_missing",f"trials/{i}")
                    if measured:
                        md=measured[1]
                        if md["state_ref"]!=d["state_ref"]:
                            self.add(loc,"assay_trial_state_mismatch",f"trials/{i}","inconsistent")
                        listed=_value(md["sample_refs"])
                        if sample is not None and listed is not None and sample not in listed:
                            self.add(loc,"assay_trial_sample_mismatch",f"trials/{i}","inconsistent")
                    if trial["status"]=="observed" and sample is None:self.add(loc,"observed_trial_sample_missing",f"trials/{i}")
                    if trial["status"] in {"planned","missing"} and sample is not None:self.add(loc,"sample_on_unobserved_trial",f"trials/{i}","inconsistent")
            elif kind=="recovery_episode":
                pre=self.lookup(d["pre_assay_ref"]);post=self.lookup(d["post_assay_ref"]);change=self.lookup(d["intervention_ref"])
                if pre and post and change:
                    if pre[1]["state_ref"]!=change[1]["pre_state_ref"] or post[1]["state_ref"]!=change[1]["post_state_ref"]:
                        self.add(loc,"recovery_endpoint_binding_mismatch",severity="inconsistent")
                    for name in ("registry_ref","success_event","tau","family_id","family_version","alpha","allocation"):
                        if pre[1][name]!=post[1][name]:self.add(loc,"recovery_criterion_binding_mismatch",name,"inconsistent")
                    if pre[1]["registry_ref"]!=d["registry_ref"]:self.add(loc,"recovery_registry_binding_mismatch",severity="inconsistent")
            elif kind=="revision":
                self.details[loc].update(new_model_samples=0,model_recovery_established=False)
            elif kind=="replay":
                self.support(d["artifact_ref"],loc,"artifact_ref")
                key=d["artifact_ref"]["record_type"]+":"+d["artifact_ref"]["record_id"]
                a=[x for x in self.bundle.artifacts if x.record_key==key]
                if len(a)==1 and a[0].actual_sha256 is not None and a[0].actual_sha256!=d["expected_sha256"]:self.add(loc,"replay_artifact_digest_mismatch",severity="inconsistent")

    def finish(self):
        self.links();self.measurements();self.states();self.transitions();self.trajectories();self.requests()
        objects=[]
        for ref,loc,data in self.rows:
            issues=tuple(self.issues[loc]);status=_status(issues)
            objects.append(ObjectBinding(ref,loc,freeze(data),status,issues,freeze(self.details[loc]),self.mock[loc]))
        return tuple(objects)


def _status(issues):
    return "contract_error" if any(i.severity=="contract_error" for i in issues) else "record_limited" if issues else "record_consistent"


def review_longitudinal(bundle: LoadedBundle) -> LongitudinalReview:
    """Inspect opt-in declarations. CLI dispatch remains authorized Step 8 work.

    A malformed profile never reports successful absence here. Private raw data
    and locators are for audit; this is not the public/redacted report renderer.
    """
    _require(isinstance(bundle,LoadedBundle),"loaded_bundle_required")
    if bundle.manifest is None:return LongitudinalReview(False,"unavailable",None)
    config=bundle.manifest.data.get("analysis_config")
    if not isinstance(config,Mapping) or not isinstance(config.get("extensions",{}),Mapping):
        return LongitudinalReview(False,"unavailable",None)
    ext=config.get("extensions",{})
    if "longitudinal" not in ext:return LongitudinalReview(False,"not_requested",None)
    raw=ext["longitudinal"]
    try:
        _require("comparison" not in ext,"conflicting_comparison_and_longitudinal_profiles")
        _require(not any(d.scope == "analysis_config" for d in bundle.manifest.diagnostics),
                 "longitudinal_core_analysis_config_invalid")
        limits,count=_preflight(raw,bundle.limits.max_depth)
        _require(raw["data_role"]==bundle.manifest.data["data_role"],"longitudinal_material_role_mismatch")
        _require(raw["study_id"]==bundle.manifest.data["study_id"],"longitudinal_study_identity_mismatch")
    except (InputError,KeyError,TypeError,ValueError) as exc:
        return LongitudinalReview(True,"contract_error",None,issues=(Issue(exc.code if isinstance(exc,InputError) else "malformed_longitudinal_profile",BASE,"contract_error"),))
    cfg=freeze(raw);inspector=_Review(bundle,cfg,limits);objects=inspector.finish()
    issues=tuple(i for values in inspector.issues.values() for i in values)
    cells=tuple(sorted({d["cell_ref"]["record_id"] for r,(_,d) in inspector.by.items() if r.object_kind=="measurement"}))
    return LongitudinalReview(True,_status(issues),cfg,input_fingerprint(bundle),configuration_fingerprint(cfg),objects,issues,
        freeze(limits),freeze({"configuration_nodes":count,"objects":len(objects),"registered_states":len(cfg["states"]),
                              "registered_transitions":len(cfg["transitions"]),"evidence_dependency_visits":inspector.support_visits}),cells)
