"""Phase 2 Step 4: scoped gates, same-unit contrasts and equal-block means.

MET 10-11.2; HERO 8-10; VF 5.3, 6.2. Consumes passive loaded records and
previously established populations/diagnostics. No text extraction, sampling,
model calls, intervals, prediction verdicts, or public-report serialization.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction
import math
from typing import Any, Mapping

from .comparison_records import (BLOCKS, ComparisonReview, CellBinding, Fact,
                                 configuration_fingerprint, review_comparison)
from .contracts import CLASS_IDS, InputError, freeze, knowledge
from .evidence import EvidenceIndex
from .local_io import LoadedBundle
from .inventory import build_inventory
from .metrics import CORE_NAMES, cell_metrics
from .populations import CellPopulations, PopulationCollection, Prefix, Ratio, prefix
from .text_diagnostics import (SURFACE, STRUCTURAL, WITHIN, DiagnosticValue,
                               TextDiagnostics, limits_from_record, method_from_record, text_input_fingerprint)

P1_NAMES = ('surface_gain', 'structural_gain', 'p1_proxy_gain_contrast')
VIEWS = ('classified_all', 'classified_valid')
PASS_STATES = frozenset({'passed', 'conditional_not_applicable', 'fixture_stipulated'})
PAIR_UNIT = 'dimensionless_distinct_observation_pair_mean'


@dataclass(frozen=True)
class Gate:
    name: str
    status: str
    required: bool = True
    reasons: tuple[str, ...] = ()
    observed: Any = field(default=None, repr=False)
    threshold_ratio: tuple[int, int] | None = None
    operator: str | None = None

    @property
    def passes(self) -> bool:
        return self.status in PASS_STATES


@dataclass(frozen=True)
class Number:
    metric_name: str
    unit: str
    result_status: str
    value: int | float | None
    exact_ratio: tuple[int, int] | None = None
    reasons: tuple[str, ...] = ()
    uncertainty_status: str = 'not_estimated'
    metric_definition_version: str = 'MET-0.2'


@dataclass(frozen=True)
class Operand:
    cell_id: str
    view: str
    metric_name: str
    number: Number
    selected_ids: tuple[str, ...]
    counted_ids: tuple[str, ...]
    population_size: int | None
    revision_pins: tuple[tuple[str, str, str | None, str | None], ...]
    k: int | None = None
    method: Any = field(default=None, repr=False)
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class Contrast:
    name: str
    condition_pair: str
    view: str
    minuend: Operand
    subtrahend: Operand
    result: Number
    k: int | None = None


@dataclass(frozen=True)
class BlockComparison:
    block_id: str
    question: str
    condition_pair: str
    view: str
    role: str
    cell_ids: tuple[str, str]
    gates: tuple[Gate, ...]
    contrasts: Mapping[str, Contrast]
    values: Mapping[str, Number]
    companions: tuple[Contrast, ...]
    frequencies: tuple[Mapping[str, Any], ...]
    qualifications: tuple[str, ...]
    sources: tuple[CellBinding, CellBinding] = field(repr=False)
    record_evidence: tuple[Fact, ...] = field(repr=False)
    dependencies: Any = field(repr=False)
    uncertainty_status: str = 'not_estimated'
    prediction_status: str = 'not_implemented'
    independent_validation_performed: bool = False

    @property
    def eligible_before_resampling(self) -> bool:
        return (all(g.passes for g in self.gates if g.required)
                and all(v.result_status == 'available' for v in self.values.values()))

    @property
    def clean_quality_eligible(self) -> bool:
        return self.eligible_before_resampling and all(g.passes for g in self.gates
                    if 'validity_floor' in g.name or g.name == 'quality_band')


@dataclass(frozen=True)
class BlockSummary:
    question: str
    condition_pair: str
    view: str
    scope: str
    intended_blocks: tuple[str, ...]
    included_blocks: tuple[str, ...]
    missing_blocks: Mapping[str, tuple[str, ...]]
    gate_failures: Mapping[str, tuple[str, ...]]
    means: Mapping[str, Number]
    block_values: Mapping[str, Mapping[str, Number]]
    full_target_complete: bool
    eligible_before_resampling: bool
    subset_rule: str = 'all_intended_blocks_with_jointly_defined_compatible_operands'
    weighting: str = 'equal_prompt_block'
    uncertainty_status: str = 'not_estimated'
    prediction_status: str = 'not_implemented'


@dataclass(frozen=True)
class Comparisons:
    requested: bool
    status: str
    comparison_id: str | None
    configuration_sha256: str | None
    material_role: str | None
    review: ComparisonReview = field(repr=False)
    blocks: tuple[BlockComparison, ...] = ()
    summaries: tuple[BlockSummary, ...] = ()
    unbound_cell_ids: tuple[str, ...] = ()
    diagnostic_issues: tuple[str, ...] = ()
    independent_validation_performed: bool = False
    uncertainty_status: str = 'not_estimated'
    prediction_status: str = 'not_implemented'
    secondary_summaries: tuple[BlockSummary, ...] = ()
    input_snapshot_sha256: str | None = None


def _reasons(items) -> tuple[str, ...]:
    return tuple(sorted(set(items)))


def _check_bits(value: Fraction, bits: int) -> Fraction:
    if type(bits) is not int or not 1 <= bits <= 2**31-1:
        raise InputError('invalid_comparison_exact_limit')
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > bits:
        raise InputError('max_exact_bits_exceeded')
    return value


def number(name: str, unit: str, value: Fraction | int | float | None = None, *,
           status: str = 'available', reasons=(), max_exact_bits: int = 131072) -> Number:
    """Exact values stay exact; undefined or unavailable values never become zero."""
    if status != 'available':
        return Number(name, unit, status, None, None, _reasons(reasons))
    try:
        if type(value) is int: value = Fraction(value)
        if isinstance(value, Fraction):
            _check_bits(value, max_exact_bits)
            result = float(value)
            if not math.isfinite(result): raise InputError('nonfinite_comparison_value')
            # Do not let an exact nonzero direction silently become floating zero.
            if result == 0 and value: raise InputError('comparison_float_underflow')
            return Number(name, unit, 'available', value.numerator if value.denominator == 1 else result,
                          (value.numerator, value.denominator))
        if type(value) is not float or not math.isfinite(value):
            raise InputError('nonfinite_or_invalid_comparison_value')
        return Number(name, unit, 'available', 0.0 if value == 0 else value)
    except (InputError, OverflowError) as exc:
        return Number(name, unit, 'unavailable', None, None,
                      (exc.code if isinstance(exc, InputError) else 'comparison_numeric_overflow',))


def _numeric(n: Number):
    return Fraction(*n.exact_ratio) if n.exact_ratio is not None else n.value


def difference(left: Number, right: Number, name: str, *, max_exact_bits=131072) -> Number:
    """left - right; only identical metric units and estimands may be subtracted."""
    if not isinstance(left, Number) or not isinstance(right, Number):
        raise InputError('comparison_number_required')
    if left.metric_name != right.metric_name or left.unit != right.unit:
        return number(name, left.unit, status='unavailable', reasons=('incompatible_metric_or_unit',))
    bad = _reasons(left.reasons + right.reasons)
    if left.result_status != 'available' or right.result_status != 'available':
        state = 'undefined' if all(x.result_status in {'available', 'undefined'} for x in (left, right)) else 'unavailable'
        return number(name, left.unit, status=state, reasons=bad + ('operand_not_available',))
    return number(name, left.unit, _numeric(left)-_numeric(right), max_exact_bits=max_exact_bits)


def ratio_gate(name: str, ratio: Ratio, threshold: Fraction, *, required=True,
               conditional_empty=False, maximum=False) -> Gate:
    if not isinstance(ratio, Ratio) or not isinstance(threshold, Fraction) or not 0 <= threshold <= 1:
        raise InputError('invalid_ratio_gate')
    t = (threshold.numerator, threshold.denominator)
    op = '<=' if maximum else '>='
    observed = freeze({'numerator': ratio.numerator, 'denominator': ratio.denominator,
                       'status': ratio.status, 'reason': ratio.reason})
    valid = (type(ratio.numerator) is int and type(ratio.denominator) is int
             and 0 <= ratio.numerator <= ratio.denominator)
    if conditional_empty and valid and ratio.denominator == 0 and ratio.status == 'undefined':
        return Gate(name, 'conditional_not_applicable', required, ('no_valid_output_denominator',), observed, t, op)
    if not valid or ratio.denominator == 0 or ratio.status != 'available':
        return Gate(name, 'unresolved', required, ('ratio_not_available',), observed, t, op)
    okay = ratio.value <= threshold if maximum else ratio.value >= threshold
    return Gate(name, 'passed' if okay else 'failed', required, () if okay else ('threshold_not_met',), observed, t, op)


def _state_gate(name, okay, *, required=True, reasons=(), observed=None):
    status = 'unresolved' if okay is None else 'passed' if okay else 'failed'
    return Gate(name, status, required, () if okay else _reasons(reasons or (name+'_not_established',)), freeze(observed))


def _fact_gate(name, facts, *, required=True):
    facts = tuple(facts)
    bad = [f for f in facts if f.status not in {'record_consistent', 'not_applicable'}]
    return _state_gate(name, bool(facts) and not bad, required=required,
                       reasons=tuple(f.name+':'+(r or f.status) for f in bad for r in (f.reasons or (f.status,)))
                       or ('required_record_facts_absent',), observed=tuple(facts))


def _known(v):
    try:
        k = knowledge(v)
        return k.value if k.state == 'known' else None
    except InputError:
        return None


def _operand(cell, cid, view, key, value, *, ids=None, k=None, method=None) -> Operand:
    if cell is None:
        return Operand(cid, view, key, (value if isinstance(value, Number) else number(key, value, status='unavailable', reasons=('expected_cell_unavailable',))), (), (), None, (), k)
    pop = cell.populations[view]
    pins = tuple((a.axis, a.sample_id, a.record_id, a.revision) for a in cell.admissions)
    return Operand(cid, view, key, value, cell.inventory.selected_sample_ids,
                   pop.sample_ids if ids is None else tuple(ids), pop.count, pins, k, method)


def _from_metric(m):
    val = Fraction(*m.exact_ratio) if m.exact_ratio is not None else m.value
    return number(m.metric_name, m.unit, val, status=m.result_status, reasons=m.reasons)


def _text_context(diag, cell, method, limits, bundle) -> tuple[str, ...]:
    if diag is None: return ('text_diagnostic_not_supplied',)
    if cell is None or diag.source_cell != cell or diag.population_sample_ids != cell.populations[diag.analysis_population].sample_ids:
        return ('text_population_or_revision_mismatch',)
    if diag.input_context_sha256 != text_input_fingerprint(bundle, cell, diag.analysis_population):
        return ('text_input_snapshot_mismatch',)
    if method is None or diag.method != method: return ('registered_text_method_mismatch',)
    if diag.limits != limits: return ('registered_text_limits_mismatch',)
    if diag.eligible_count is not None and (diag.eligible_count != len(diag.eligible_sample_ids)
            or len(set(diag.eligible_sample_ids)) != diag.eligible_count
            or not set(diag.eligible_sample_ids) <= set(diag.population_sample_ids)
            or diag.pair_count != diag.eligible_count*(diag.eligible_count-1)//2):
        return ('diagnostic_subset_or_pair_count_mismatch',)
    return ()


def _text_operand(cell, cid, view, key, diag, errors):
    if errors:
        val = number(key, PAIR_UNIT, status='unavailable', reasons=errors)
    else:
        d = diag.results.get(key)
        val = number(key, PAIR_UNIT, status='unavailable', reasons=('diagnostic_value_absent',)) if d is None else number(
            key, d.unit, Fraction(*d.exact_ratio) if d.exact_ratio is not None else d.value,
            status=d.result_status, reasons=d.reasons, max_exact_bits=diag.limits.max_exact_bits)
    return _operand(cell, cid, view, key, val, ids=diag.eligible_sample_ids if diag is not None else (), method=diag.method.identity if diag is not None else None)


def _prefix_operand(cell, cid, view, k):
    if cell is None: return _operand(None, cid, view, 'structural_distinct_k', 'classes_among_k_realization_prefix', k=k)
    p = prefix(cell, k, view, mode='hero')
    val = number('structural_distinct_k', p.unit, p.distinct_count, status=p.status, reasons=p.reasons)
    return _operand(cell, cid, view, 'structural_distinct_k', val, ids=p.counted_sample_ids, k=k)


def _contrast(left, right, name, pair, compatible, bits):
    result = difference(left.number, right.number, name, max_exact_bits=bits) if compatible else number(
        name, left.number.unit, status='unavailable', reasons=('comparison_incompatible',))
    return Contrast(name, pair, left.view, left, right, result, left.k)


def ceiling_flags(baseline: Number | None, prefix_counts=()) -> tuple[str, ...]:
    """Prespecified diagnostics only; no endpoint substitution or adaptive action."""
    flags=[]
    if baseline is not None and baseline.result_status=='available' and _numeric(baseline)>=Fraction(19,20):
        flags.append('surface_proxy_near_ceiling')
    if any(type(n) is int and n==len(CLASS_IDS) for n in prefix_counts):
        flags.append('registered_class_ceiling_observed')
    return tuple(flags)


def _context_matches(bundle, cell, index):
    """Reject stale caller-supplied contexts; do not silently repair their labels."""
    cid=cell.inventory.cell_id
    configs=bundle.manifest.data.get('analysis_config', {}) if bundle.manifest else {}
    selections=[x for x in configs.get('selection', ()) if x['analysis_cell_id']==cid]
    if len(selections)!=1: return False
    selection=selections[0]
    requested=_known(selection['selected_sample_ids'])
    if requested is not None and tuple(requested)!=cell.inventory.requested_sample_ids: return False
    order=_known(selection['sample_order'])
    if order is not None and cell.inventory.order is not None and tuple(order)!=cell.inventory.order: return False
    associations={a.sample_id:a for a in cell.inventory.associations}
    for sid in cell.inventory.selected_sample_ids:
        r=index.get(('realization',sid));a=associations.get(sid)
        if r is None or a is None or r.data['analysis_cell_id']!=cid: return False
        for key in ('raw_response_ref','output_ref','output_content_hash','extraction_rule_version'):
            if r.data[key]!=getattr(a,key): return False
    for a in cell.admissions:
        actual=index.admit(a.axis,a.sample_id)
        # Population admission also withholds a known bad artifact association.
        assoc=associations.get(a.sample_id)
        if assoc is not None and assoc.reasons:
            if a.status!='withheld': return False
        elif actual!=a: return False
    return True


def _cell_gates(cell, binding, index, question):
    label = binding.condition_id
    if cell is None: return [_state_gate(label+'.selected_scope', False, reasons=('expected_cell_unavailable',))]
    inv = cell.inventory
    p = prefix(cell, 20, mode='hero')
    gates = [_state_gate(label+'.intended_positions', p.status == 'available' and inv.selected_count.value == 20,
              reasons=p.reasons or ('selected_count_not_twenty',), observed={'selected': inv.selected_count,
              'prefix': p, 'groups': inv.groups, 'attempts': inv.recorded_attempt_ids, 'extra_attempts': binding.extra_attempt_ids}),
             _state_gate(label+'.input_cell_identity', binding.cell == inv.identity,
                         reasons=('population_binding_identity_mismatch',))]
    for key, threshold, conditional in (('classification_coverage',Fraction(9,10),False),
               ('decisive_validity_coverage',Fraction(19,20),False),('classified_valid_coverage',Fraction(9,10),True)):
        gates.append(ratio_gate(label+'.'+key, cell.ratios[key], threshold, conditional_empty=conditional))
    gates.append(ratio_gate(label+'.validity_floor', cell.ratios['valid_fraction_selected'], Fraction(4,5), required=question=='P5'))
    # Each supplied selected position must use the registered extraction rule.
    # Checking the rule identity never requires the optional proxy bytes.
    methods = tuple(_known(a.extraction_rule_version) for a in inv.associations if a.sample_id in set(inv.selected_sample_ids))
    gates.append(_state_gate(label+'.extraction_identity', bool(methods) and all(x is not None for x in methods) and len(set(methods))==1,
                             observed=methods))
    policies = []
    for a in cell.admissions:
        if a.axis != 'assignment' or a.record_id is None: continue
        r = index.get(('assignment',a.record_id))
        if r is not None: policies.append((r.data['assignment_evidence_policy_id'],r.data['assignment_evidence_policy_version']))
    gates.append(_state_gate(label+'.evidence_policy', bool(policies) and len(set(policies))==1,
                             observed=tuple(policies)))
    return gates


def _evidence_gate(review, cells, index, bindings):
    """Inspect supplied scoped records. Never certify their truth or independence."""
    if review.material_role == 'fixture':
        fixture = all(c is not None and c.admissions and all(a.fixture_context for a in c.admissions) for c in cells)
        issues=[] if fixture else ['fixture_admission_context_missing']
        # Missing real E is permitted for explicitly stipulated software cases.
        # A supplied contradictory registration remains contradictory in a fixture.
        if review.configuration['evidence']['registration']:
            reg=[f for f in review.facts if f.name.startswith('registration_')]
            if len(reg)<3 or any(f.status!='record_consistent' for f in reg):
                issues.append('supplied_fixture_registration_unresolved')
        relevant={('cell',b.cell_id) for b in bindings}|{('frame',b.cell['frame_id']) for b in bindings if b.cell}
        if any(index.affected(k,{'independence','schema','membership','validity'}) for k in relevant):
            issues.append('active_evidence_correction')
        return Gate('evidence_scope', 'fixture_stipulated' if not issues else 'unresolved', True,
                    _reasons(issues+['fixture_only_no_empirical_validation']))
    errors=[]; retained=[]; supplied_audits=0
    if review.material_role != 'confirmatory': errors.append('nonconfirmatory_or_reanalysis_scope')
    cfg=review.configuration
    if cfg['revision']['prior_run_ids'] or cfg['revision']['prior_comparison_ids']:
        errors.append('reanalysis_not_new_confirmation')
    roles={'cell':{b.cell_id for b in bindings}, 'frame':{b.cell['frame_id'] for b in bindings if b.cell}}
    def scoped(p):
        return any(r['record_id'] in roles.get(r['record_type'],set()) for r in p['scope_refs'])
    groups=('registration','exposure','structural_validation','core_audit','integrity','independence')
    facts=review.facts
    for group in groups:
        supplied=[f for f in facts if f.name=='evidence_'+group]
        if not supplied or not cfg['evidence'][group]: errors.append(group+'_not_supplied');continue
        selected=[f for f in supplied if isinstance(f.observed,Mapping) and scoped(f.observed)]
        if not selected: errors.append(group+'_scope_not_established')
        for f in selected:
            p=f.observed
            retained.append(f)
            if f.status!='record_consistent' or f.mock: errors.append(group+'_record_limited')
            ref=f.evidence_refs[0] if f.evidence_refs else None
            if ref is None: errors.append(group+'_reference_missing');continue
            key=(ref['record_type'],ref['record_id'])
            if group=='structural_validation':
                # Registered family distinctions need their actual reference/core review.
                if key[0]!='domain_suite' or index.reference_check(key).status!='record_consistent':
                    errors.append('structural_reference_review_unresolved')
            if group=='core_audit':
                supplied_audits += int(key[0]=='audit')
                gate=index.audit_check(key) if key[0]=='audit' else index.reference_check(key)
                if gate.status!='record_consistent' or gate.mock: errors.append('core_or_audit_unresolved')
            if group=='integrity':
                gate=index.claim_check(key)
                if (gate.status!='declared_record_consistent' or p['declared_disposition']!='supported_for_scope'
                        or p['claim_kind'] not in {'validated_measurement','empirical_theory'}):
                    errors.append('scoped_comparison_claim_unresolved')
                if (not {'structural_validity','source_integrity'} <= set(p['requirements'])
                        or any(p['requirements'].get(key,{}).get('outcome')!='satisfied_for_scope' for key in ('structural_validity','source_integrity'))
                        or any(x.get('outcome') not in {'satisfied_for_scope','not_applicable'} for x in p['requirements'].values())):
                    errors.append('unresolved_integrity_requirement')
            if group=='independence' and p['outcome']!='supported_for_scope': errors.append('independence_not_supported')
            if group=='exposure' and ((_known(p['exposed']) is True and p['stage'] in {'pilot','calibration','before_initial'}) or _known(p['exposed']) is None):
                errors.append('exposure_requires_scope_review')
    if not supplied_audits: errors.append('actual_sample_audit_not_supplied')
    registration=[f for f in facts if f.name.startswith('registration_')]
    if len(registration)<3 or any(f.status!='record_consistent' for f in registration): errors.append('prospective_registration_unresolved')
    if any(a.restrictions for c in cells if c is not None for a in c.admissions): errors.append('admission_claim_restrictions')
    relevant={('cell',b.cell_id) for b in bindings}|{('frame',b.cell['frame_id']) for b in bindings if b.cell}
    if any(index.affected(k,{'independence','schema','membership','validity'}) for k in relevant): errors.append('active_evidence_correction')
    return _state_gate('evidence_scope', not errors, reasons=errors, observed=tuple(retained))


def _mean(name, values, bits):
    first=values[0]
    if any(x.metric_name!=first.metric_name or x.unit!=first.unit for x in values):
        return number(name,first.unit,status='unavailable',reasons=('incompatible_mean_units_or_estimands',))
    try:
        if all(v.exact_ratio is not None for v in values):
            total=Fraction()
            for v in values: total=_check_bits(total+Fraction(*v.exact_ratio),bits)
            return number(name,first.unit,_check_bits(total/len(values),bits),max_exact_bits=bits)
        return number(name,first.unit,math.fsum(float(v.value) for v in values)/len(values))
    except (InputError, OverflowError) as exc:
        return number(name,first.unit,status='unavailable',reasons=(exc.code if isinstance(exc,InputError) else 'comparison_numeric_overflow',))


def summarize_blocks(blocks: tuple[BlockComparison,...], intended_blocks=BLOCKS, *,
                     descriptive_subset=False, max_exact_bits=131072) -> BlockSummary:
    """All linked P1 components share one block set. Never select on effect sign."""
    if (not isinstance(blocks,(tuple,list)) or not blocks or any(not isinstance(b,BlockComparison) for b in blocks)
            or type(descriptive_subset) is not bool or not isinstance(intended_blocks,(tuple,list))
            or not intended_blocks or any(not isinstance(b,str) for b in intended_blocks)
            or len(set(intended_blocks))!=len(intended_blocks)):
        raise InputError('invalid_block_summary_input')
    first=blocks[0]; identity=(first.question,first.condition_pair,first.view)
    if any((b.question,b.condition_pair,b.view)!=identity or set(b.values)!=set(first.values) for b in blocks):
        raise InputError('mixed_endpoint_summary')
    byid={b.block_id:b for b in blocks}
    if len(byid)!=len(blocks) or not set(byid)<=set(intended_blocks): raise InputError('duplicate_or_unintended_summary_block')
    missing={}; failures={}; included=[]
    for bid in intended_blocks:
        b=byid.get(bid)
        if b is None: missing[bid]=('expected_block_missing',);continue
        failed=tuple(g.name+':'+reason for g in b.gates if g.required and not g.passes for reason in (g.reasons or (g.status,)))
        if failed: failures[bid]=failed
        if all(v.result_status=='available' for v in b.values.values()): included.append(bid)
        else: missing[bid]=_reasons(r for v in b.values.values() if v.result_status!='available' for r in (v.reasons or (v.result_status,)))
    complete=not missing
    registered_target=tuple(intended_blocks)==BLOCKS
    if (complete or descriptive_subset) and included:
        means={name:_mean(name,[byid[b].values[name] for b in included],max_exact_bits) for name in first.values}
    else:
        reason='no_defined_paired_blocks' if not included else 'incomplete_intended_block_set'
        means={name:number(name,v.unit,status='unavailable',reasons=(reason,)) for name,v in first.values.items()}
    return BlockSummary(*identity,'available_block_descriptive_subset' if descriptive_subset else 'full_intended_target' if registered_target else 'declared_descriptive_target',
            tuple(intended_blocks),tuple(included),freeze(missing),freeze(failures),freeze(means),
            freeze({b:byid[b].values for b in included}),complete and registered_target,
            complete and registered_target and not failures and all(v.result_status=='available' for v in means.values()))


def comparison_input_fingerprint(bundle: LoadedBundle) -> str:
    """Bind a computed comparison to its actual immutable acquired input context.

    Snapshot identities, parser limits, artifact states and diagnostics are part
    of this binding. Only the digest travels downstream, never private bodies.
    """
    if not isinstance(bundle, LoadedBundle):
        raise InputError('loaded_comparison_bundle_required')
    return configuration_fingerprint({
        'snapshots': [(key, snap.sha256, snap.size_bytes)
                      for key, snap in sorted(bundle.snapshots.items())],
        'limits': vars(bundle.limits),
        'artifacts': [vars(item) for item in bundle.artifacts],
        'diagnostics': [vars(item) for item in bundle.diagnostics],
        'acquisition_complete': bundle.acquisition_complete,
    })


def compare_study(bundle: LoadedBundle, populations: PopulationCollection,
                  diagnostics: tuple[TextDiagnostics,...] = (), *, include_descriptive_subset=False) -> Comparisons:
    """Compare supplied M contexts and Step 3 outputs; no acquisition or resampling.

    Private audit records and operands are retained in this component result.
    CLI/report dispatch and public redaction remain Phase 2 Step 6.
    """
    if (not isinstance(bundle,LoadedBundle) or not isinstance(populations,PopulationCollection)
            or type(include_descriptive_subset) is not bool or not isinstance(diagnostics,(tuple,list))
            or any(not isinstance(d,TextDiagnostics) for d in diagnostics)):
        raise InputError('invalid_comparison_component')
    review=review_comparison(bundle)
    if review.configuration is None or not review.bindings:
        return Comparisons(review.requested,review.status,review.comparison_id,None,review.material_role,review)
    cfg=review.configuration; limits=limits_from_record(cfg['limits']); bits=limits.max_exact_bits
    try: method=method_from_record(cfg['text_method'])
    except InputError: method=None
    index=EvidenceIndex(bundle)
    cells={c.inventory.cell_id:c for c in populations.cells}
    if len(cells)!=len(populations.cells): raise InputError('duplicate_population_cell')
    diagnostic_map={}
    for d in diagnostics:
        key=(d.cell_id,d.analysis_population)
        if key in diagnostic_map: raise InputError('duplicate_text_diagnostic')
        diagnostic_map[key]=d
    binding_map={(b.block_id,b.condition_id):b for b in review.bindings}
    # Recheck inventories against the current held records, including attempt
    # history, planned slots, ordinals and extraction associations. A previously
    # accepted population cannot certify a changed invocation/position history.
    current_inventory = {c.cell_id: c for c in build_inventory(bundle).cells}
    context_ok={cid: c.inventory == current_inventory.get(cid) and _context_matches(bundle,c,index)
                for cid,c in cells.items()}
    metrics={cid:cell_metrics(c,min_empirical_frequency='0.10') for cid,c in cells.items()}
    results=[]; issues=[]
    for pair in review.pairs:
        left_name,right_name=pair.contrast.split('-')
        question='P1' if pair.contrast=='B-A' else 'P5'
        if question not in cfg['questions']: continue
        bindings=(binding_map[(pair.block_id,left_name)],binding_map[(pair.block_id,right_name)])
        a,b=(cells.get(binding.cell_id) for binding in bindings)
        for view in VIEWS:
            gates=[]
            for c,bd in zip((a,b),bindings): gates.extend(_cell_gates(c,bd,index,question))
            frame_facts=[f for f in pair.facts if f.name=='frame_compatibility']
            gates.append(_fact_gate('shared_frame',frame_facts))
            cell_facts=[]
            for bd in bindings:
                ignored=set()
                for p in ('presence_penalty','frequency_penalty'):
                    if any(f.name=='control_'+p and f.status=='not_applicable' for f in bd.facts): ignored.add('protocol_setting_'+p)
                cell_facts.extend(f for f in bd.facts if f.name not in ignored)
            # The Step 2 participant status summarizes all cell facts, including
            # legitimately unexposed penalties. Evaluate the underlying facts
            # here after their documented conditional handling, and retain the
            # original aggregate in record_evidence for audit.
            pair_facts=[f for f in pair.facts if f.name!='participant_records']
            gates.append(_fact_gate('protocol_and_resource_records',cell_facts+pair_facts))
            # Known contradictions are incompatible. Missing control/hidden-state
            # evidence may leave a labeled descriptive contrast, never a passed gate.
            contradictions=[f for f in cell_facts+pair_facts if f.status in {'inconsistent','contract_error'}]
            same_frame=bool(frame_facts) and all(f.status=='record_consistent' for f in frame_facts)
            identity_ok=all(c is not None and c.inventory.identity==bd.cell and context_ok[bd.cell_id] for c,bd in zip((a,b),bindings))
            gates.append(_state_gate('population_snapshot_binding',identity_ok,reasons=('population_snapshot_or_revision_mismatch',)))
            extraction=tuple(_known(x.extraction_rule_version) for c in (a,b) if c for x in c.inventory.associations if x.sample_id in c.inventory.selected_sample_ids)
            extraction_ok=(bool(extraction) and None not in extraction and len(set(extraction))==1
                           and extraction[0]==_known(cfg['text_method']['extraction_rule_version']))
            policies=set()
            for c in (a,b):
                if c:
                    for adm in c.admissions:
                        r=index.get(('assignment',adm.record_id)) if adm.axis=='assignment' and adm.record_id else None
                        if r: policies.add((r.data['assignment_evidence_policy_id'],r.data['assignment_evidence_policy_version']))
            gates.append(_state_gate('shared_extraction_policy',extraction_ok and len(policies)==1,observed={'extraction':extraction,'policies':tuple(sorted(policies))}))
            compatible=same_frame and identity_ok and extraction_ok and len(policies)==1 and not contradictions
            gates.append(_state_gate('arithmetic_compatibility',compatible,reasons=('incompatible_participant_records',),observed=tuple(contradictions)))
            va=a.ratios['valid_fraction_selected'] if a else Ratio(None,None,'unavailable')
            vb=b.ratios['valid_fraction_selected'] if b else Ratio(None,None,'unavailable')
            gap=abs(va.value-vb.value) if va.status==vb.status=='available' else None
            gates.append(ratio_gate('quality_band',Ratio(gap.numerator,gap.denominator,'available') if gap is not None else Ratio(None,None,'unavailable'),Fraction(1,10),required=question=='P5',maximum=True))
            gates.append(_evidence_gate(review,(a,b),index,bindings))
            dg=[diagnostic_map.get((bd.cell_id,view)) for bd in bindings]
            errs=[_text_context(d,c,method,limits,bundle) for d,c in zip(dg,(a,b))]
            for bd,error in zip(bindings,errs): issues.extend(bd.cell_id+':'+view+':'+e for e in error)
            if question=='P1':
                for d,error,bd in zip(dg,errs,bindings):
                    rr=d.proxy_text_coverage if d is not None and not error else Ratio(None,None,'unavailable')
                    gates.append(ratio_gate(bd.condition_id+'.proxy_text_coverage',rr,Fraction(19,20)))
                    gates.append(_state_gate(bd.condition_id+'.minimum_text_pairs',not error and d is not None and d.eligible_count is not None and d.eligible_count>=2))
                    gates.append(_state_gate(bd.condition_id+'.common_text_subset',not error and d is not None and d.text_subset_complete
                                  and all(d.results[k].pair_denominator==d.pair_count for k in (SURFACE,STRUCTURAL))))
            contrasts={}; vals={}; qualifications=[]; companions=[]
            if question=='P1':
                for key,name in ((SURFACE,'surface_gain'),(STRUCTURAL,'structural_gain')):
                    ops=[_text_operand(c,bd.cell_id,view,key,d,error) for c,bd,d,error in zip((a,b),bindings,dg,errs)]
                    con=_contrast(*ops,name,pair.contrast,compatible,bits);contrasts[name]=con;vals[name]=con.result
                x,y=vals['surface_gain'],vals['structural_gain']
                # The sole authorized cross-estimand combination is G = dL - dQ.
                if x.result_status==y.result_status=='available':
                    vals[P1_NAMES[2]]=number(P1_NAMES[2],PAIR_UNIT,_numeric(x)-_numeric(y),max_exact_bits=bits)
                else: vals[P1_NAMES[2]]=number(P1_NAMES[2],PAIR_UNIT,status='unavailable',reasons=('linked_p1_operands_not_available',))
                base=contrasts['surface_gain'].subtrahend.number
                qualifications.extend(ceiling_flags(base))
                if va.status==vb.status=='available' and va.value<vb.value: qualifications.append('B_minus_A_validity_loss')
            else:
                name='p5_valid_distinct_k_delta' if view=='classified_valid' else 'structural_distinct_k_delta'
                ops=[_prefix_operand(c,bd.cell_id,view,20) for c,bd in zip((a,b),bindings)]
                con=_contrast(*ops,name,pair.contrast,compatible,bits);contrasts[name]=con;vals[name]=con.result
                if any(op.number.value==len(CLASS_IDS) for op in ops): qualifications.append('registered_class_ceiling_observed')
            for key in CORE_NAMES:
                ops=[]
                for c,bd in zip((a,b),bindings):
                    n=_from_metric(metrics[bd.cell_id].distributions[view].results[key]) if c else number(key,'unknown',status='unavailable',reasons=('expected_cell_unavailable',))
                    ops.append(_operand(c,bd.cell_id,view,key,n,method={'min_empirical_frequency': '0.10'} if key=='observed_support_size_thresholded' else None))
                companions.append(_contrast(*ops,key+'_delta',pair.contrast,compatible,bits))
            for key in ('classification_coverage','decisive_validity_coverage','valid_fraction_selected',
                        'classified_valid_coverage','classified_valid_fraction'):
                ops=[]
                for c,bd in zip((a,b),bindings):
                    ratio=c.ratios[key] if c else Ratio(None,None,'unavailable')
                    val=number(key,'fraction_'+key,ratio.value,status=ratio.status,reasons=(ratio.reason,) if ratio.reason else (),max_exact_bits=bits)
                    ops.append(_operand(c,bd.cell_id,view,key,val,method={'numerator':ratio.numerator,'denominator':ratio.denominator}))
                companions.append(_contrast(*ops,key+'_delta',pair.contrast,compatible,bits))
            for k in (5,10,20):
                ops=[_prefix_operand(c,bd.cell_id,view,k) for c,bd in zip((a,b),bindings)]
                companions.append(_contrast(*ops,'structural_distinct_k_delta',pair.contrast,compatible,bits))
                if any(op.number.value==len(CLASS_IDS) for op in ops): qualifications.append('registered_class_ceiling_observed')
            for key in (SURFACE,STRUCTURAL,WITHIN):
                ops=[_text_operand(c,bd.cell_id,view,key,d,error) for c,bd,d,error in zip((a,b),bindings,dg,errs)]
                companions.append(_contrast(*ops,key+'_delta',pair.contrast,compatible,bits))
            freq=[]
            for klass in CLASS_IDS:
                row={'class_id':klass,'view':view,'block_id':pair.block_id,'condition_pair':pair.contrast,'unit':'class_frequency'}
                values=[]
                for c,bd,side in zip((a,b),bindings,('minuend','subtrahend')):
                    p=c.populations[view] if c else None;n=p.count if p else None;count=p.class_counts.get(klass) if p and p.status=='available' else None
                    val=number('class_frequency','class_frequency',Fraction(count,n) if n else None,
                               status='available' if n else 'undefined' if n==0 else 'unavailable',
                               reasons=() if n else ('empty_or_unavailable_classified_denominator',),max_exact_bits=bits)
                    row[side]=freeze({'cell_id':bd.cell_id,'count':count,'denominator':n,'frequency':val});values.append(val)
                row['delta']=difference(*values,'class_frequency_delta',max_exact_bits=bits) if compatible else number('class_frequency_delta','class_frequency',status='unavailable',reasons=('comparison_incompatible',))
                freq.append(freeze(row))
            if any(adm.restrictions for c in (a,b) if c for adm in c.admissions): qualifications.append('supplied_evidence_claim_restrictions')
            if not all(g.passes for g in gates if g.required): qualifications.append('descriptive_numbers_do_not_establish_endpoint_eligibility')
            if question=='P1' and not all(g.passes for g in gates if 'validity_floor' in g.name or g.name=='quality_band'):
                qualifications.append('clean_quality_comparable_P1_unavailable')
            dependencies=freeze({'call_groups':tuple(c.inventory.groups if c else () for c in (a,b)),
                'cross_cell_groups':populations.inventory.cross_cell_groups,
                'resampling_record':cfg['resampling'], 'dependent_pair_count_is_not_replication':True})
            results.append(BlockComparison(pair.block_id,question,pair.contrast,view,
                'primary' if (question=='P1' and view=='classified_all') or (question=='P5' and view=='classified_valid') else 'sensitivity_or_companion',
                pair.cell_ids,tuple(gates),freeze(contrasts),freeze(vals),tuple(companions),tuple(freq),_reasons(qualifications),bindings,
                review.facts+pair.facts,dependencies))
    summaries=[]; secondary=[]
    for identity in dict.fromkeys((r.question,r.condition_pair,r.view) for r in results):
        rows=tuple(r for r in results if (r.question,r.condition_pair,r.view)==identity)
        summaries.append(summarize_blocks(rows,max_exact_bits=bits))
        if include_descriptive_subset and not summaries[-1].full_target_complete:
            summaries.append(summarize_blocks(rows,descriptive_subset=True,max_exact_bits=bits))
        for name,k in dict.fromkeys((c.name,c.k) for c in rows[0].companions):
            derived=[]
            for b in rows:
                c=next(c for c in b.companions if (c.name,c.k)==(name,k))
                derived.append(replace(b,question='secondary:'+name+(':'+str(k) if k is not None else ''),
                    role='secondary_descriptive_only', values=freeze({name:c.result}),
                    gates=tuple(g for g in b.gates if g.name in {'arithmetic_compatibility','population_snapshot_binding'})))
            secondary.append(summarize_blocks(tuple(derived),max_exact_bits=bits))
            if include_descriptive_subset and not secondary[-1].full_target_complete:
                secondary.append(summarize_blocks(tuple(derived),descriptive_subset=True,max_exact_bits=bits))
    return Comparisons(True,'contract_error'  if review.status=='contract_error' else 'processed',review.comparison_id,
                       configuration_fingerprint(cfg),review.material_role,review,tuple(results),tuple(summaries),
                       review.unbound_cell_ids,_reasons(issues),secondary_summaries=tuple(secondary),
                       input_snapshot_sha256=comparison_input_fingerprint(bundle))
