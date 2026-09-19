"""Optional offline V orchestration and bounded public projections.

Consumes the same loaded snapshot and accepted M populations. Source bodies,
private actor mappings and unrestricted record prose never enter these exports.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from dataclasses import dataclass, fields
from typing import Any, Mapping
from .contracts import InputError, freeze, is_hash
from .comparison_records import review_comparison, configuration_fingerprint, ComparisonReview
from .comparisons import compare_study
from .text_diagnostics import diagnose_cells, method_from_record, limits_from_record
from .uncertainty import resample_study, read_replays, INTERVAL_SCOPE
from .predictions import evaluate_predictions, CAVEATS
from .reporting import plain, protected, digest

PROFILE = 'structdet_comparison_v1'
LEGACY_PROFILE = 'structdet_measurement_v1'
VERSION = '0.2'


def _opaque(value):
    return {'record_sha256': digest(value), 'disclosure': 'content_omitted_from_ordinary_report'}


def _public_detail(value):
    """Preserve typed numeric controls and references without publishing prose."""
    from .populations import Ratio
    from .contracts import ExactNumber, ThresholdToken
    from decimal import Decimal
    if value is None or type(value) in (bool, int, float):
        return plain(value)
    if isinstance(value, (ExactNumber, ThresholdToken, Decimal, Ratio)):
        return plain(value)
    if isinstance(value, str):
        vocabulary = {'known','unknown','unavailable','not_applicable','recorded','hidden',
                      'unsupported','not_recorded','fixture_only','adjudicated_import',
                      'passed','failed','unresolved','record_consistent','inconsistent',
                      'available','undefined','deferred','not_requested'}
        return value if value in vocabulary or is_hash(value) else _opaque(value)
    if isinstance(value, Mapping):
        if set(value) == {'record_type', 'record_id', 'record_version'}:
            return plain(value)
        if 'state' in value:
            out = protected(value)
            if value.get('state') == 'known' and 'value' in value:
                out['value'] = _public_detail(value['value'])
            return out
        allowed = {'requested','actual','enforcement','evidence_refs','numerator','denominator',
                   'status','reason','value','calls','candidate_positions','output_cap_per_call',
                   'selected','policies','extraction','unit','tokenizer','convention'}
        if set(value) <= allowed:
            return {k: _public_detail(v) for k,v in value.items()}
        return _opaque(value)
    if isinstance(value, (tuple, list)):
        # Whole protocol groups are already disclosed individually in bindings.
        if all(hasattr(x, 'name') and hasattr(x, 'status') for x in value):
            return [{'fact_name': x.name, 'status': x.status, 'record_sha256': digest(x)} for x in value]
        return [_public_detail(x) for x in value]
    return _opaque(value)


def _fact(f):
    return {'name': f.name, 'status': f.status, 'reasons': list(f.reasons),
            'observed': _public_detail(f.observed), 'expected': _public_detail(f.expected),
            'evidence_refs': plain(f.evidence_refs), 'mock': f.mock,
            'substantive_validation_performed': False}


def binding_report(review: ComparisonReview):
    """No source configuration, frame prose, prompt bytes or serving ID leaks."""
    return {'requested': review.requested, 'status': review.status,
            'comparison_id': review.comparison_id, 'data_role': review.material_role,
            'record_facts': [_fact(x) for x in review.facts],
            'bindings': [{'block_id': b.block_id, 'condition_id': b.condition_id,
                          'cell_id': b.cell_id, 'status': b.status,
                          'facts': [_fact(f) for f in b.facts],
                          'recorded_attempt_ids': list(b.recorded_attempt_ids),
                          'extra_attempt_ids': list(b.extra_attempt_ids)} for b in review.bindings],
            'pairs': [{'block_id': p.block_id, 'contrast': p.contrast,
                       'cell_ids': list(p.cell_ids), 'facts': [_fact(f) for f in p.facts]}
                      for p in review.pairs],
            'unbound_cell_ids': list(review.unbound_cell_ids),
            'independent_validation_performed': False}


def comparison_validation(bundle):
    """Record checks only. No tokenizer, metric, resampling or outcome calls."""
    review = review_comparison(bundle)
    if not review.requested:
        return None, ()
    failures = tuple(sorted({reason for fact in
        list(review.facts) + [f for b in review.bindings for f in b.facts] +
        [f for p in review.pairs for f in p.facts]
        if fact.status == 'contract_error' for reason in fact.reasons}))
    if review.status == 'contract_error' and not failures:
        failures = ('comparison_contract_error',)
    if review.status != 'contract_error':
        try:
            read_replays(bundle, review.configuration)
        except InputError as exc:
            # Absence/unavailable evidence is a scoped limitation. A supplied
            # malformed replay remains a processing contract error.
            absent = {'replay_choice_unresolved', 'replay_artifact_unavailable', 'replay_snapshot_missing'}
            if exc.code not in absent:
                failures = tuple(sorted(set(failures + (exc.code,))))
    return binding_report(review), failures


def _gate(g):
    return {'name': g.name, 'status': g.status, 'required': g.required,
            'passes': g.passes, 'reasons': list(g.reasons),
            'observed': _public_detail(g.observed),
            'threshold_ratio': plain(g.threshold_ratio), 'operator': g.operator,
            'observed_record_sha256': digest(g.observed)}


def _contrast(c, operands, contexts):
    refs = {}
    for name in ('minuend', 'subtrahend'):
        obj = plain(getattr(c, name))
        ctx = {k: obj.pop(k) for k in ('selected_ids', 'counted_ids', 'revision_pins')}
        ctx.update(cell_id=obj['cell_id'], view=obj['view'])
        context_id = 'context-' + digest(ctx); contexts[context_id] = ctx
        obj['population_context_ref'] = context_id
        key = 'operand-' + digest(obj)
        operands[key] = obj; refs[name + '_ref'] = key
    return {'name': c.name, 'condition_pair': c.condition_pair, 'view': c.view,
            'result': plain(c.result), 'k': c.k, **refs}


def _block(b, operands, contexts):
    names = ('block_id','question','condition_pair','view','role','cell_ids',
             'values','frequencies','qualifications')
    out = {name: plain(getattr(b, name)) for name in names}
    out.update(contrasts={k: _contrast(v, operands, contexts) for k,v in b.contrasts.items()},
               companions=[_contrast(v, operands, contexts) for v in b.companions],
               gates=[_gate(g) for g in b.gates],
               eligible_before_resampling=b.eligible_before_resampling,
               clean_quality_eligible=b.clean_quality_eligible,
               record_evidence=[_fact(f) for f in b.record_evidence],
               dependency_identity_sha256=digest(b.dependencies),
               independent_validation_performed=False)
    return out


def _identity(s):
    return {k: plain(getattr(s, k)) for k in ('question','condition_pair','view','scope',
                                           'intended_blocks','included_blocks')}


def _summary(s):
    # The component's historical 'not_implemented' marker describes Step 4.
    # Current orchestration records downstream states instead of inheriting it.
    return {f.name: plain(getattr(s, f.name)) for f in fields(s)
            if f.name not in {'prediction_status', 'uncertainty_status'}}


def _outcome(o):
    if o is None:
        return {'result_status': 'not_requested', 'outcome': None, 'reason': 'question_not_requested'}
    return {f.name: plain(getattr(o, f.name)) for f in fields(o) if f.name != 'source'}


def _sensitivity(r):
    return {**_identity(r.source_summary), 'status': r.status,
            'intervals': plain(r.intervals), 'reasons': list(r.reasons),
            'operand_sha256': r.operand_sha256, 'interval_scope': r.interval_scope,
            'caveats': list(r.caveats), 'dependence': plain(r.dependence),
            'replay_sha256': r.replay['sha256'] if r.replay else None,
            'replicate_statistics_sha256': digest({name: [[format(v.numerator, 'x'), format(v.denominator, 'x')]
                for v in values] for name, values in r.replicate_means.items()}),
            'replicate_statistics_encoding': 'signed_hex_ratio_v1',
            'independent_validation_performed': False}


def _diagnostic(d):
    return {f.name: plain(getattr(d, f.name)) for f in fields(d) if f.name != 'source_cell'}


@dataclass(frozen=True)
class ComparisonAttachment:
    sections: Mapping[str, Any]
    replay_collection: Mapping[str, Any]
    methods: Mapping[str, Any]
    failures: tuple[str, ...]


def analyze_comparison(bundle, populations) -> ComparisonAttachment | None:
    """Run the approved components once on a common snapshot, then redact."""
    review = review_comparison(bundle)
    if not review.requested:
        return None
    facts, failures = comparison_validation(bundle)
    cfg = review.configuration
    if not review.bindings:
        content = {'status': 'contract_error', 'binding_review': facts,
                   'predictions': {q: {'outcome': 'not_evaluated', 'reasons': list(failures)} for q in ('P1','P5')},
                   'per_block_contrasts': [], 'equal_block_means': [], 'sensitivity': [],
                   'claim_boundary': 'Requested comparison has invalid declarations; no successful empty study.'}
        return ComparisonAttachment(freeze({'comparison': content, 'text': {'diagnostics': [], 'status': 'unavailable'},
                                            'integrity': {'independent_validation_performed': False}}),
                                    freeze({'schema_version': '0.1', 'replays': []}), freeze({}), failures)
    method_error = None
    try:
        method = method_from_record(cfg['text_method'])
        # Only bound study cells participate; unrelated records cannot consume a
        # shared text-work budget or introduce a different endpoint population.
        order = {b.cell_id: i for i, b in enumerate(review.bindings)}
        cells = tuple(sorted((c for c in populations.cells if c.inventory.cell_id in order),
                             key=lambda c: order[c.inventory.cell_id]))
        diagnostics = diagnose_cells(bundle, cells, method, views=tuple(cfg['views']),
                                     limits=limits_from_record(cfg['limits']))
    except InputError as exc:
        # Unknown method identities restrict text results. Never infer a host
        # method or suppress the separate text-independent P5 computation.
        method_error = exc.code
        diagnostics = ()
    comp = compare_study(bundle, populations, diagnostics)
    sensitivity = resample_study(bundle, comp)
    prediction = evaluate_predictions(sensitivity)
    collection = {'schema_version': '0.1', 'replays': plain(sensitivity.replays)}
    replay_refs = [{k: plain(v) for k, v in r.items() if k != 'indices'} for r in sensitivity.replays]
    methods = {'text': _public_detail(cfg['text_method']),
               'text_identity': plain(diagnostics[0].method.identity) if diagnostics else None,
               'limits': plain(cfg['limits']), 'interval_scope': INTERVAL_SCOPE,
               'resampling': {k: plain(v) for k, v in cfg['resampling'].items()
                              if k not in {'dependence_assessment_ref','replay_ref'}},
               'replay_input_ref': _public_detail(cfg['resampling']['replay_ref'])}
    operands = {}; contexts = {}
    block_records = [_block(b, operands, contexts) for b in comp.blocks]
    content = {'status': comp.status, 'comparison_id': comp.comparison_id,
               'comparison_configuration_sha256': comp.configuration_sha256,
               'input_snapshot_sha256': comp.input_snapshot_sha256,
               'binding_review': facts, 'methods': methods,
               'per_block_contrasts': block_records, 'operand_records': operands, 'population_context_records': contexts,
               'equal_block_means': [_summary(s) for s in comp.summaries],
               'secondary_descriptive_means': [_summary(s) for s in comp.secondary_summaries],
               'sensitivity': [_sensitivity(r) for r in sensitivity.results],
               'replay_manifest_refs': replay_refs,
               'primary_results': [
                   {'question': o.question, 'condition_pair': o.condition_pair, 'view': o.view,
                    'outcome': o.outcome, 'role': o.role, 'permitted_claim_scope': o.permitted_claim_scope,
                    'actual_blocks': list(o.actual_blocks), 'reasons': list(o.reasons),
                    'qualifications': list(o.qualifications)}
                   for o in (prediction.p1_primary, prediction.p1_valid_sensitivity,
                             *prediction.p5_comparators, prediction.p5_full) if o is not None],
               'predictions': {'P1': _outcome(prediction.p1_primary),
                   'P1_valid_sensitivity': _outcome(prediction.p1_valid_sensitivity),
                   'P5_comparators': [_outcome(o) for o in prediction.p5_comparators],
                   'P5': _outcome(prediction.p5_full),
                   'mixed_comparator_behavior': prediction.mixed_comparator_behavior},
               'unbound_cell_ids': list(comp.unbound_cell_ids),
               'diagnostic_issues': list(comp.diagnostic_issues),
               'claim_boundary': 'Fixture outcomes test software routing. Other outcomes remain record-qualified under this fixed task, evaluator lineage and six-wording suite.',
               'caveats': list(CAVEATS)}
    integrity = {'comparison_evidence_refs': plain(cfg['evidence']),
                 'comparison_revision': {'prior_comparison_ids': plain(cfg['revision']['prior_comparison_ids']),
                     'prior_run_ids': plain(cfg['revision']['prior_run_ids']),
                     'reason': protected(cfg['revision']['reason']),
                     'changes': [protected(v) for v in cfg['revision']['changes']]},
                 'correction_rule': 'Rebuild affected text subsets, contrasts, means, intervals and outcomes on pinned inputs. Reuse indices only for identical block identities; preserve old reports.',
                 'independent_validation_performed': False, 'UD_006': 'actual_independent_evidence_outstanding',
                 'deferred_capabilities_unchanged': True}
    return ComparisonAttachment(freeze({'comparison': content,
         'text': {'diagnostics': [_diagnostic(d) for d in diagnostics],
                  'status': 'unavailable' if method_error else 'processed',
                  'method_reasons': [method_error] if method_error else [],
                  'raw_text_and_tokens': 'omitted', 'proxy_is_exact_realization_entropy': False},
         'integrity': integrity}), freeze(collection), freeze(methods), failures)
