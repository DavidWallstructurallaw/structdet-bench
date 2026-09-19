"""Fixed paired prompt-block sensitivity and passive index replay.

MET 11.3, HERO 10.2, VF 5.4/6.2, Phase 2 plan 3.6/4.4.
No new observations, candidate execution, network, row bootstrap or label review.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import json
import math
import platform
import random
import re
from typing import Any, Mapping

from .comparison_records import BLOCKS, configuration_fingerprint
from .comparisons import (BlockSummary, Comparisons, Number, P1_NAMES, number, comparison_input_fingerprint)
from .contracts import InputError, freeze, is_hash, is_id, knowledge
from .evidence import EvidenceIndex
from .local_io import LoadedBundle, parse_json_bytes

METHOD = 'paired_prompt_block_bootstrap_v1'
STATISTIC = 'equal_prompt_block_mean_v1'
QUANTILE = 'linear_b_minus_one_v1'
INTERVAL_SCOPE = 'prompt_resampling_sensitivity'
SEED, REPLICATES = 20260917, 2000
PROBABILITIES = ('0.025', '0.975')
LIMIT = 131072
CAVEATS = ('fixed_wording_suite_not_prompt_population_confidence',
           'conditional_on_recorded_within_block_outputs',
           'no_label_schema_or_total_generation_uncertainty_estimated',
           'no_familywise_significance_or_practical_importance_claim')


def _canonical(value):
    def plain(x):
        if isinstance(x, Mapping): return {k: plain(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [plain(v) for v in x]
        return x
    return (json.dumps(plain(value), sort_keys=True, ensure_ascii=True,
                       separators=(',', ':'), allow_nan=False)+'\n').encode('utf-8')


def _hash(value): return hashlib.sha256(_canonical(value)).hexdigest()


def _blocks(block_ids):
    if (not isinstance(block_ids, (list, tuple)) or not 1 <= len(block_ids) <= 6
            or any(not is_id(x) for x in block_ids) or len(set(block_ids)) != len(block_ids)):
        raise InputError('invalid_replay_block_ids')
    return tuple(block_ids)


def _bits(x, limit):
    if type(limit) is not int or not 1 <= limit <= 2**31-1:
        raise InputError('invalid_uncertainty_exact_limit')
    if max(abs(x.numerator).bit_length(), x.denominator.bit_length()) > limit:
        raise InputError('uncertainty_exact_limit_exceeded')
    return x


def scalar(value: Number, *, limit=LIMIT) -> Fraction:
    """Exact stored ratio or the exact represented binary float; never round signs."""
    if not isinstance(value, Number) or value.result_status != 'available':
        raise InputError('uncertainty_operand_unavailable')
    if type(value.value) not in (int, float) or not math.isfinite(value.value):
        raise InputError('nonfinite_uncertainty_operand')
    if value.exact_ratio is not None:
        r = value.exact_ratio
        if (not isinstance(r, (tuple, list)) or len(r) != 2
                or any(type(v) is not int for v in r) or r[1] <= 0):
            raise InputError('invalid_exact_uncertainty_ratio')
        x = _bits(Fraction(*r), limit)
        try: rendered = float(x)
        except OverflowError as exc: raise InputError('uncertainty_numeric_overflow') from exc
        if (not math.isfinite(rendered) or (x != 0 and rendered == 0)
                or rendered != value.value):
            raise InputError('numerical_sign_or_representation_instability')
    else:
        x = Fraction(value.value)
    return _bits(x, limit)


def make_replay(block_ids) -> Mapping[str, Any]:
    """Generate exactly 2000 rows with an isolated RNG. No global state changes."""
    ids = _blocks(block_ids)
    if len(ids) < 2: raise InputError('fewer_than_two_blocks')
    rng = random.Random(SEED)
    rows = [[rng.randrange(len(ids)) for _ in ids] for _ in range(REPLICATES)]
    raw = {'schema_version': '0.1', 'method': METHOD, 'seed': SEED,
           'replicates': REPLICATES, 'index_base': 0, 'block_ids': list(ids),
           'statistic': STATISTIC, 'quantile': QUANTILE,
           'probabilities': list(PROBABILITIES),
           'rng': {'algorithm': 'MT19937', 'api': 'random.Random.randrange',
                   'implementation': platform.python_implementation(),
                   'python_version': platform.python_version(),
                   'state_version': random.Random.VERSION},
           'indices': rows, 'indices_sha256': _hash(rows)}
    raw['sha256'] = _hash(raw)
    return freeze(raw)


def validate_replay(raw, block_ids, *, expected_sha256=None) -> Mapping[str, Any]:
    """Replay trusts validated stored indices, not a future RNG's regeneration.

    A digest identifies the declared metadata and indices, not their authenticity.
    An imported replay additionally keeps its loader-checked artifact identity.
    """
    ids = _blocks(block_ids)
    keys = {'schema_version','method','seed','replicates','index_base','block_ids',
            'statistic','quantile','probabilities','rng','indices','indices_sha256','sha256'}
    if not isinstance(raw, Mapping) or set(raw) != keys:
        raise InputError('replay_field_set')
    constants = {'schema_version':'0.1','method':METHOD,'seed':SEED,'replicates':REPLICATES,
                 'index_base':0,'statistic':STATISTIC,'quantile':QUANTILE}
    if (any(raw[k] != v or type(raw[k]) is not type(v) for k,v in constants.items())
            or not isinstance(raw['probabilities'], (list,tuple))
            or tuple(raw['probabilities']) != PROBABILITIES):
        raise InputError('replay_method_or_seed_mismatch')
    if _blocks(raw['block_ids']) != ids or len(ids) < 2:
        raise InputError('replay_block_order_or_scope_mismatch')
    rng = raw['rng']
    if (not isinstance(rng, Mapping) or set(rng) != {'algorithm','api','implementation','python_version','state_version'}
            or rng['algorithm'] != 'MT19937' or rng['api'] != 'random.Random.randrange'
            or not isinstance(rng['implementation'], str)
            or rng['implementation'] not in {'CPython','PyPy'}
            or not isinstance(rng['python_version'],str)
            or not re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',rng['python_version'])
            or type(rng['state_version']) is not int or rng['state_version'] != 3):
        raise InputError('replay_rng_metadata_invalid')
    rows = raw['indices']
    if (not isinstance(rows,(list,tuple)) or len(rows)!=REPLICATES
            or any(not isinstance(row,(list,tuple)) or len(row)!=len(ids)
                   or any(type(i) is not int or not 0 <= i < len(ids) for i in row) for row in rows)):
        raise InputError('replay_index_dimensions_or_values')
    if not is_hash(raw['indices_sha256']) or raw['indices_sha256'] != _hash(rows):
        raise InputError('replay_index_hash_mismatch')
    if not is_hash(raw['sha256']) or raw['sha256'] != _hash({k:v for k,v in raw.items() if k!='sha256'}):
        raise InputError('replay_manifest_hash_mismatch')
    if expected_sha256 is not None and (not is_hash(expected_sha256) or expected_sha256 != raw['sha256']):
        raise InputError('replay_expected_identity_mismatch')
    return freeze(raw)


def replicate_means(values, indices, *, limit=LIMIT) -> tuple[Fraction, ...]:
    """Arithmetic primitive for toy or real draws; this alone is no full interval."""
    if (not isinstance(values,(tuple,list)) or not 1 <= len(values) <= 6
            or not isinstance(indices,(tuple,list)) or not 1 <= len(indices) <= REPLICATES):
        raise InputError('invalid_replicate_input')
    xs = [scalar(v,limit=limit) for v in values]
    if len({(v.metric_name,v.unit) for v in values}) != 1:
        raise InputError('incompatible_replicate_units_or_estimands')
    result=[]
    for row in indices:
        if (not isinstance(row,(tuple,list)) or len(row)!=len(xs)
                or any(type(i) is not int or not 0 <= i < len(xs) for i in row)):
            raise InputError('invalid_replicate_row')
        total=Fraction()
        for i in row: total=_bits(total+xs[i],limit)
        result.append(_bits(total/len(xs),limit))
    return tuple(result)


def percentile(values, q: Fraction, *, limit=LIMIT) -> Fraction:
    """Exactly h=(B-1)*q with linear interpolation. No selective omissions."""
    if (not isinstance(values,(list,tuple)) or not 1 <= len(values) <= REPLICATES
            or not isinstance(q,Fraction) or not 0 <= q <= 1
            or any(type(v) not in (int,Fraction) for v in values)):
        raise InputError('invalid_percentile_values_or_probability')
    ordered=sorted(_bits(Fraction(x),limit) for x in values)
    h=(len(ordered)-1)*q; lo=h.numerator//h.denominator; weight=h-lo
    if weight == 0: return ordered[lo]
    return _bits(ordered[lo]+_bits(weight*(ordered[lo+1]-ordered[lo]),limit),limit)


@dataclass(frozen=True)
class DependenceCheck:
    status: str
    block_ids: tuple[str,...]
    reasons: tuple[str,...] = ()
    evidence_refs: tuple[Any,...] = field(default=(),repr=False)
    fixture: bool = False
    substantive_validation_performed: bool = False

    @property
    def permits_interval(self): return self.status in {'record_supported','fixture_stipulated'}


@dataclass(frozen=True)
class Sensitivity:
    source_summary: BlockSummary = field(repr=False)
    status: str
    intervals: Mapping[str,Any]
    replicate_means: Mapping[str,tuple[Fraction,...]] = field(repr=False)
    replay: Mapping[str,Any] | None = field(default=None,repr=False)
    dependence: DependenceCheck | None = None
    reasons: tuple[str,...] = ()
    operand_sha256: str | None = None
    interval_scope: str = INTERVAL_SCOPE
    caveats: tuple[str,...] = CAVEATS
    independent_validation_performed: bool = False


@dataclass(frozen=True)
class StudySensitivity:
    comparisons: Comparisons = field(repr=False)
    results: tuple[Sensitivity,...]
    replays: tuple[Mapping[str,Any],...]
    configuration_sha256: str | None
    independent_validation_performed: bool = False


def summarize_sensitivity(summary: BlockSummary, dependence: DependenceCheck, *,
                          replay=None, expected_sha256=None, limit=LIMIT) -> Sensitivity:
    """Use one manifest and one block set for every linked component.

    Comparison eligibility is preserved separately from descriptive intervals;
    quality/evidence failures do not silently delete arithmetically defined blocks.
    """
    if not isinstance(summary,BlockSummary) or not isinstance(dependence,DependenceCheck):
        raise InputError('invalid_sensitivity_component')
    rows=summary.block_values; ids=summary.included_blocks
    reasons=[]; manifest=None; draws={}; output={}; digest=None
    try:
        _blocks(ids)
        if len(ids)<2: raise InputError('fewer_than_two_blocks')
        if dependence.block_ids!=ids or not dependence.permits_interval:
            raise InputError('unsupported_or_unresolved_cross_block_dependence')
        if summary.weighting!='equal_prompt_block': raise InputError('wrong_block_weighting')
        if set(rows)!=set(ids) or not set(ids)<=set(summary.intended_blocks):
            raise InputError('summary_block_membership_mismatch')
        if not summary.full_target_complete and summary.scope=='full_intended_target':
            raise InputError('incomplete_full_target_no_silent_subset')
        names=tuple(summary.means)
        if not names or any(set(rows[b])!=set(names) for b in ids): raise InputError('linked_component_set_mismatch')
        if summary.question=='P1' and set(names)!=set(P1_NAMES): raise InputError('p1_component_set_mismatch')
        if summary.question=='P1':
            for b in ids:
                if scalar(rows[b][P1_NAMES[0]],limit=limit)-scalar(rows[b][P1_NAMES[1]],limit=limit)!=scalar(rows[b][P1_NAMES[2]],limit=limit):
                    raise InputError('p1_linked_contrast_mismatch')
        manifest=make_replay(ids) if replay is None else validate_replay(replay,ids,expected_sha256=expected_sha256)
        for name in names:
            values=[rows[b][name] for b in ids]
            mean=replicate_means(values,[list(range(len(ids)))],limit=limit)[0]
            if scalar(summary.means[name],limit=limit)!=mean:
                raise InputError('stale_summary_mean')
            draws[name]=replicate_means(values,manifest['indices'],limit=limit)
            bounds=[percentile(draws[name],Fraction(q),limit=limit) for q in PROBABILITIES]
            nums=[number(name,summary.means[name].unit,x,max_exact_bits=limit) for x in bounds]
            if any(n.result_status!='available' for n in nums):
                raise InputError('numerical_sign_or_representation_instability')
            output[name]=freeze({'mean':summary.means[name], 'lower':nums[0], 'upper':nums[1],
                'nominal_level':'0.95','interval_scope':INTERVAL_SCOPE,'replay_sha256':manifest['sha256'],
                'replicate_count':REPLICATES,'block_count':len(ids),'degenerate':bounds[0]==bounds[1],
                'input_representation':'exact_ratios' if all(n.exact_ratio is not None for n in values) else 'exact_represented_binary_values'})
        # The declared arithmetic limit can exceed Python's decimal-rendering
        # limit. Signed hexadecimal is exact and does not change process limits.
        digest=_hash({'encoding':'signed_hex_ratio_v1','blocks':ids,
            'values':{b:{n:{'unit':rows[b][n].unit,
                'ratio_hex':[format(v,'x') for v in
                    scalar(rows[b][n],limit=limit).as_integer_ratio()]}
                for n in names} for b in ids}})
    except (InputError,OverflowError) as exc:
        reasons.append(exc.code if isinstance(exc,InputError) else 'uncertainty_numeric_overflow')
        # No one linked primary may inherit a selectively shortened set of draws.
        output={};draws={}
    return Sensitivity(summary,'unavailable' if reasons else 'available',freeze(output),freeze(draws),
                       manifest,dependence,tuple(reasons),digest)


def check_dependence(bundle: LoadedBundle, comparisons: Comparisons,
                     summary: BlockSummary) -> DependenceCheck:
    """Inspect an explicit scoped assessment plus observable shared-call evidence."""
    ids=summary.included_blocks; errors=[]; refs=(); fixture=comparisons.material_role=='fixture'
    try:
        cfg=comparisons.review.configuration
        if cfg is None: raise InputError('comparison_configuration_missing')
        current=bundle.manifest.data['analysis_config']['extensions']['comparison']
        if configuration_fingerprint(current)!=comparisons.configuration_sha256:
            raise InputError('stale_comparison_configuration')
        value=knowledge(cfg['resampling']['dependence_assessment_ref'])
        if value.state!='known' or not isinstance(value.value,Mapping):
            raise InputError('dependence_assessment_not_supplied')
        ref=value.value;refs=(ref,);index=EvidenceIndex(bundle)
        from .comparison_records import _Inspector
        p, linked = _Inspector(bundle, cfg).support(ref, {'independence_assessment'})
        if (not p or linked.status!='record_consistent'
                or p['state']!='active' or p['outcome']!='supported_for_scope'
                or index.affected((ref['record_type'],ref['record_id']),{'independence','metadata'})):
            raise InputError('dependence_assessment_unresolved')
        if (p['mock'] or p['data_role']=='fixture' or linked.mock) and not fixture:
            raise InputError('mock_dependence_cannot_validate_empirical_scope')
        detail=p.get('extensions',{}).get('paired_block_dependence')
        keys={'version','block_ids','unit','target','cross_block_shared_history','condition_pairs'}
        if (p['dimension']!='paired_prompt_block_resampling' or not isinstance(detail,Mapping)
                or set(detail)!=keys or detail['version']!='0.1'
                or detail['unit']!='paired_prompt_block' or detail['target']!='fixed_wording_suite'
                or _blocks(detail['block_ids'])!=BLOCKS
                or not isinstance(detail['condition_pairs'],(list,tuple))
                or summary.condition_pair not in detail['condition_pairs']
                or len(set(detail['condition_pairs']))!=len(detail['condition_pairs'])
                or any(x not in {'B-A','C-A','C-B'} for x in detail['condition_pairs'])):
            raise InputError('dependence_scope_or_unit_mismatch')
        if knowledge(detail['cross_block_shared_history']).state!='known' or knowledge(detail['cross_block_shared_history']).value is not False:
            raise InputError('cross_block_history_not_cleared')
        rows=[r for r in comparisons.blocks if (r.question,r.condition_pair,r.view)==(summary.question,summary.condition_pair,summary.view) and r.block_id in ids]
        if len(rows)!=len(ids): raise InputError('dependence_block_records_missing')
        groups={}; shared={}; cells=set()
        for row in rows:
            for source in row.sources: cells.add(source.cell_id)
            for side in row.dependencies['call_groups']:
                for group in side: groups.setdefault(group.group_id,set()).add(row.block_id)
            for con in row.contrasts.values():
                for operand in (con.minuend,con.subtrahend):
                    for sid in operand.selected_ids:
                        sample=index.get(('realization',sid))
                        if sample is None: continue
                        context=sample.data.get('shared_context_ref')
                        if context is not None:
                            k=knowledge(context)
                            if k.state!='known': errors.append('cross_block_context_unresolved')
                            elif k.value is not None: shared.setdefault(_hash(k.value),set()).add(row.block_id)
        if any(len(s)>1 for s in list(groups.values())+list(shared.values())):
            raise InputError('observed_cross_block_shared_generation')
        scoped={r['record_id'] for r in p['scope_refs'] if r['record_type']=='cell'}
        if not cells<=scoped: raise InputError('dependence_cell_scope_incomplete')
        if not p['reviewer_refs'] or not p['evidence_refs']: raise InputError('dependence_review_or_evidence_missing')
        criterion=knowledge(p['criterion'])
        if criterion.state!='known' or not isinstance(criterion.value,str) or not criterion.value.strip():
            raise InputError('dependence_criterion_not_established')
        if index.resolve(p['left_ref']) is None or index.resolve(p['right_ref']) is None:
            raise InputError('dependence_subject_unresolved')
    except (InputError,KeyError,TypeError,ValueError) as exc:
        errors.append(exc.code if isinstance(exc,InputError) else 'invalid_dependence_record')
    return DependenceCheck('unavailable' if errors else 'fixture_stipulated' if fixture else 'record_supported',
                           tuple(ids),tuple(sorted(set(errors))),tuple(freeze(r) for r in refs),fixture)


def read_replays(bundle, configuration):
    """Passive replay transport: collection or the prior three-file run manifest."""
    value=knowledge(configuration['resampling']['replay_ref'])
    if value.state!='known': raise InputError('replay_choice_unresolved')
    if value.value is None: return None
    ref=value.value;key=ref['record_type']+':'+ref['record_id']
    artifacts=[a for a in bundle.artifacts if a.record_key==key]
    if len(artifacts)!=1 or artifacts[0].status!='snapshot_read': raise InputError('replay_artifact_unavailable')
    snap=bundle.snapshots.get(artifacts[0].snapshot_path)
    if snap is None: raise InputError('replay_snapshot_missing')
    raw=parse_json_bytes(snap.content)
    if isinstance(raw, Mapping) and 'run_manifest_version' in raw:
        if (raw.get('run_manifest_version') != '0.1'
                or raw.get('report_profile') != 'structdet_comparison_v1'
                or not isinstance(raw.get('comparison_replay'), Mapping)
                or raw.get('comparison_replay_sha256') != _hash(raw['comparison_replay'])):
            raise InputError('invalid_run_manifest_replay_envelope')
        raw = raw['comparison_replay']
    if (not isinstance(raw,Mapping) or set(raw)!={'schema_version','replays'} or raw['schema_version']!='0.1'
            or not isinstance(raw['replays'],(list,tuple)) or not 1<=len(raw['replays'])<=12):
        raise InputError('invalid_replay_collection')
    result={}
    for item in raw['replays']:
        if not isinstance(item,Mapping): raise InputError('invalid_replay_collection_item')
        ids=_blocks(item.get('block_ids'))
        if ids in result: raise InputError('duplicate_replay_block_set')
        result[ids]=validate_replay(item,ids)
    return result


def _imported_replays(bundle, comparisons):
    return read_replays(bundle, comparisons.review.configuration)


def resample_study(bundle: LoadedBundle, comparisons: Comparisons) -> StudySensitivity:
    """Component API; runtime CLI and final report dispatch remain Step 6."""
    if not isinstance(bundle,LoadedBundle) or not isinstance(comparisons,Comparisons):
        raise InputError('invalid_study_sensitivity_input')
    if not comparisons.requested or comparisons.review.configuration is None:
        return StudySensitivity(comparisons,(),(),comparisons.configuration_sha256)
    supplied=None; replay_error=None; cache={};results=[]
    try:
        if comparisons.input_snapshot_sha256 != comparison_input_fingerprint(bundle):
            raise InputError('comparison_snapshot_mismatch')
        supplied=_imported_replays(bundle,comparisons)
    except InputError as exc: replay_error=exc.code
    limit=comparisons.review.configuration['limits']['max_exact_bits']
    for summary in comparisons.summaries:
        dep=check_dependence(bundle,comparisons,summary);ids=summary.included_blocks
        replay=None; error=replay_error
        if len(ids)>=2 and dep.permits_interval and not error:
            if supplied is not None:
                replay=supplied.get(ids)
                if replay is None: error='no_replay_for_exact_block_set'
            else:
                if ids not in cache: cache[ids]=make_replay(ids)
                replay=cache[ids]
        if error:
            results.append(Sensitivity(summary,'unavailable',freeze({}),freeze({}),None,dep,(error,)))
        else:
            results.append(summarize_sensitivity(summary,dep,replay=replay,limit=limit))
    used={r.replay['sha256']:r.replay for r in results if r.replay is not None}
    return StudySensitivity(comparisons,tuple(results),tuple(used.values()),comparisons.configuration_sha256)
