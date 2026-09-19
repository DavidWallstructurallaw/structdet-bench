"""VF 6-7 fixed-suite P1/P5 operational decisions on paired sensitivity.

The four outcomes are conditional on supplied evidence. No significance, model
capacity, latent extinction, practical-importance or overall-score estimator.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from .comparison_records import BLOCKS
from .comparisons import P1_NAMES
from .contracts import InputError, freeze
from .uncertainty import (CAVEATS, INTERVAL_SCOPE, REPLICATES, Sensitivity,
                          StudySensitivity, scalar)

OUTCOMES = ('supporting','contrary','inconclusive','not_evaluated')
P5_NAME = 'p5_valid_distinct_k_delta'


@dataclass(frozen=True)
class Outcome:
    question: str
    condition_pair: str
    view: str
    role: str
    outcome: str
    intended_blocks: tuple[str,...]
    actual_blocks: tuple[str,...]
    directions: Mapping[str,Any]
    reasons: tuple[str,...]
    qualifications: tuple[str,...]
    permitted_claim_scope: str
    clean_quality_comparable: bool | None = None
    source: Sensitivity | None = field(default=None,repr=False)
    independent_validation_performed: bool = False


@dataclass(frozen=True)
class PredictionResults:
    comparison_id: str | None
    requested_questions: tuple[str,...]
    p1_primary: Outcome | None
    p1_valid_sensitivity: Outcome | None
    p5_comparators: tuple[Outcome,...]
    p5_full: Outcome | None
    mixed_comparator_behavior: bool
    descriptive_subset_results: tuple[Outcome,...]
    source: StudySensitivity = field(repr=False)
    caveats: tuple[str,...] = CAVEATS
    independent_validation_performed: bool = False


def _sign(x): return 'positive' if x>0 else 'negative' if x<0 else 'zero'


def evaluate_endpoint(result: Sensitivity, *, material_role: str,
                      qualifications=(), clean_quality_comparable=None) -> Outcome:
    """Strict zero, joint P1 criteria, and no favorable secondary substitution."""
    if not isinstance(result,Sensitivity) or not isinstance(material_role,str) or material_role not in {'fixture','pilot','descriptive','confirmatory'}:
        raise InputError('invalid_prediction_input')
    summary=result.source_summary;question=summary.question
    if question not in {'P1','P5'}: raise InputError('unregistered_primary_question')
    primary=(question=='P1' and summary.view=='classified_all') or (question=='P5' and summary.view=='classified_valid')
    role='primary' if primary else 'prespecified_valid_sensitivity' if question=='P1' else 'companion_only'
    names=P1_NAMES if question=='P1' else (P5_NAME,) if summary.view=='classified_valid' else ('structural_distinct_k_delta',)
    reasons=list(result.reasons);directions={}
    if summary.condition_pair not in ({'B-A'} if question=='P1' else {'C-A','C-B'}): reasons.append('incorrect_primary_comparator')
    if summary.view not in {'classified_all','classified_valid'}: reasons.append('incorrect_population_view')
    if summary.intended_blocks!=BLOCKS or summary.included_blocks!=BLOCKS or not summary.full_target_complete or summary.scope!='full_intended_target':
        reasons.append('full_six_block_target_not_available')
    if not summary.eligible_before_resampling or summary.gate_failures:
        reasons.append('required_endpoint_gates_not_satisfied')
    if result.status!='available' or result.interval_scope!=INTERVAL_SCOPE:
        reasons.append('required_prompt_sensitivity_unavailable')
    if result.dependence is None or not result.dependence.permits_interval or result.dependence.block_ids!=summary.included_blocks:
        reasons.append('resampling_dependence_not_supported')
    if material_role!='fixture' and result.dependence is not None and result.dependence.fixture:
        reasons.append('fixture_assumptions_cannot_support_real_study')
    if material_role in {'pilot','descriptive'}:
        reasons.append('nonconfirmatory_scope')
    for name in names:
        row={'observed_direction':'unavailable','retained_direction':'unavailable',
             'mean':summary.means.get(name),'lower':None,'upper':None}
        try:
            mean=scalar(summary.means[name]);row['observed_direction']=_sign(mean)
            interval=result.intervals.get(name)
            if interval is None: raise InputError('missing_required_component_interval')
            if (scalar(interval['mean'])!=mean or interval['replicate_count']!=REPLICATES
                    or interval['block_count']!=len(summary.included_blocks)
                    or interval['interval_scope']!=INTERVAL_SCOPE or interval['nominal_level']!='0.95'
                    or result.replay is None or interval['replay_sha256']!=result.replay['sha256']):
                raise InputError('interval_identity_or_mean_mismatch')
            if any((interval[k].metric_name,interval[k].unit)!=(name,summary.means[name].unit) for k in ('mean','lower','upper')):
                raise InputError('interval_metric_or_unit_mismatch')
            lower,upper=scalar(interval['lower']),scalar(interval['upper'])
            if lower>upper: raise InputError('interval_bounds_reversed')
            row.update(lower=interval['lower'],upper=interval['upper'],
                       retained_direction='positive' if mean>0 and lower>0 else 'negative' if mean<0 and upper<0 else 'not_retained',
                       degenerate=lower==upper)
        except (InputError,KeyError,TypeError,ValueError) as exc:
            reasons.append(name+':'+(exc.code if isinstance(exc,InputError) else 'invalid_direction_record'))
        directions[name]=freeze(row)
    if question=='P1' and all(directions[n]['observed_direction']!='unavailable' for n in P1_NAMES):
        if scalar(summary.means[P1_NAMES[0]])-scalar(summary.means[P1_NAMES[1]])!=scalar(summary.means[P1_NAMES[2]]):
            reasons.append('p1_gain_identity_mismatch')
    if reasons:
        outcome='not_evaluated'
    else:
        required=(P1_NAMES[0],P1_NAMES[2]) if question=='P1' else names
        signs=[directions[n]['retained_direction'] for n in required]
        outcome='supporting' if all(x=='positive' for x in signs) else 'contrary' if 'negative' in signs else 'inconclusive'
        if outcome=='contrary': reasons.extend('negative_retained:'+n for n in required if directions[n]['retained_direction']=='negative')
        if outcome=='inconclusive': reasons.append('required_strict_direction_not_retained')
    flags=set(qualifications)
    if any(x.get('degenerate') for x in directions.values()): flags.add('degenerate_range_is_not_general_certainty')
    if question=='P1' and clean_quality_comparable is False: flags.add('clean_quality_comparable_P1_unavailable')
    flags.add('sign_does_not_establish_practical_importance')
    scope='fixture_only' if material_role=='fixture' else 'record_qualified_fixed_suite' if outcome!='not_evaluated' else 'descriptive_only_restricted'
    return Outcome(question,summary.condition_pair,summary.view,role,outcome,summary.intended_blocks,
                   summary.included_blocks,freeze(directions),tuple(sorted(set(reasons))),tuple(sorted(flags)),scope,
                   clean_quality_comparable if question=='P1' else None,result)


def combine_p5(comparators: tuple[Outcome,...], *, material_role: str) -> tuple[Outcome,bool]:
    """The full two-comparator pattern cannot inherit only its favorable member."""
    if (not isinstance(comparators,(tuple,list)) or len(comparators)!=2
            or any(not isinstance(x,Outcome) or x.question!='P5' or x.view!='classified_valid'
                   or x.outcome not in OUTCOMES for x in comparators)
            or {x.condition_pair for x in comparators}!={'C-A','C-B'}):
        raise InputError('both_registered_p5_comparators_required')
    byid={x.condition_pair:x for x in comparators};a,b=byid['C-A'],byid['C-B']
    states=(a.outcome,b.outcome)
    mixed=len(set(states))>1
    result='not_evaluated' if 'not_evaluated' in states else 'contrary' if 'contrary' in states else 'supporting' if states==('supporting','supporting') else 'inconclusive'
    reasons=tuple('C-A:'+x for x in a.reasons)+tuple('C-B:'+x for x in b.reasons)
    flags=set(a.qualifications+b.qualifications)
    if mixed: flags.add('mixed_comparator_behavior')
    scope='fixture_only' if material_role=='fixture' else 'record_qualified_fixed_suite' if result!='not_evaluated' else 'descriptive_only_restricted'
    actual=tuple(x for x in BLOCKS if x in a.actual_blocks and x in b.actual_blocks)
    return Outcome('P5','C-A_and_C-B','classified_valid','full_pattern',result,BLOCKS,actual,
        freeze({'C-A':a.directions,'C-B':b.directions}),tuple(sorted(set(reasons))),tuple(sorted(flags)),scope),mixed


def evaluate_predictions(study: StudySensitivity) -> PredictionResults:
    """Consume Step 5 results; no reclassification, sampling or report writing."""
    if not isinstance(study,StudySensitivity): raise InputError('study_sensitivity_required')
    comp=study.comparisons;cfg=comp.review.configuration
    if not comp.requested or cfg is None:
        return PredictionResults(comp.comparison_id,(),None,None,(),None,False,(),study)
    if study.configuration_sha256!=comp.configuration_sha256: raise InputError('prediction_configuration_mismatch')
    results={};subsets=[]
    for item in study.results:
        s=item.source_summary
        if not any(s==x for x in comp.summaries): raise InputError('stale_or_foreign_sensitivity_summary')
        identity=(s.question,s.condition_pair,s.view,s.scope)
        if identity in results: raise InputError('duplicate_prediction_summary')
        rows=[b for b in comp.blocks if (b.question,b.condition_pair,b.view)==identity[:3]]
        flags=tuple(f for b in rows for f in b.qualifications)
        clean=(len(rows)==6 and all(b.clean_quality_eligible for b in rows)) if s.question=='P1' else None
        out=evaluate_endpoint(item,material_role=comp.material_role,qualifications=flags,clean_quality_comparable=clean)
        results[identity]=out
        if s.scope!='full_intended_target': subsets.append(out)
    def get(question,pair,view):
        key=(question,pair,view,'full_intended_target')
        if key in results:return results[key]
        return Outcome(question,pair,view,'primary','not_evaluated',BLOCKS,(),freeze({}),
                       ('required_primary_summary_missing',),(), 'fixture_only' if comp.material_role=='fixture' else 'descriptive_only_restricted')
    p1=get('P1','B-A','classified_all') if 'P1' in cfg['questions'] else None
    valid=get('P1','B-A','classified_valid') if p1 else None
    if p1 and valid and p1.outcome!=valid.outcome:
        p1=replace(p1,qualifications=tuple(sorted(set(p1.qualifications+('valid_only_sensitivity_disagrees_or_unavailable',)))))
    p5=tuple(get('P5',p,'classified_valid') for p in ('C-A','C-B')) if 'P5' in cfg['questions'] else ()
    full,mixed=combine_p5(p5,material_role=comp.material_role) if p5 else (None,False)
    return PredictionResults(comp.comparison_id,tuple(cfg['questions']),p1,valid,p5,full,mixed,tuple(subsets),study)
