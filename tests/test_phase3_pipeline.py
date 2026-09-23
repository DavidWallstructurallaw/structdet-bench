"""Step 8 source-record integration oracles; fixture processing is not E evidence.

The independent expectations below come from explicit class counts and set
operations. Production report snapshots are never used as numerical oracles.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter
import copy
from decimal import Decimal, localcontext
from fractions import Fraction as F
import functools
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench.contracts import CLASS_IDS, InputError
from structdet_bench.pipeline import analyze_bundle, validate_bundle, write_analysis
from structdet_bench.reporting import plain
from tests.helpers import ROOT, rewrite_evidence_bundle, tagged as K

STAMP = '2026-09-20T00:00:00+00:00'
HERO = ROOT / 'examples/hero_recursive/bundle.json'
NULL = ROOT / 'examples/categorical_null/bundle.json'


def content(result, section):
    return plain(result.report['sections'][section - 1]['content'])


def dictionaries(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from dictionaries(item)
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from dictionaries(item)


def has_fields(value, *fields):
    return [row for row in dictionaries(value) if all(k in row for k in fields)]


def fraction(value):
    if isinstance(value, dict) and 'value' in value:
        return fraction(value['value'])
    if isinstance(value, dict) and 'numerator' in value:
        return F(value['numerator'], value['denominator'])
    return F(value)


def episode(result):
    rows = has_fields(content(result, 6), 'external_recovery_rate', 'missing_classes')
    if len(rows) != 1:
        raise AssertionError('one explicit recovery episode required')
    return rows[0]


def fit(result):
    rows = has_fields(content(result, 5)['half_life'], 'empirical', 'interval', 'diversities')
    if len(rows) != 1:
        raise AssertionError('one explicit fitted curve required')
    return rows[0]


@functools.lru_cache(maxsize=1)
def hero_result():
    return analyze_bundle(HERO, recorded_at=STAMP)


@functools.lru_cache(maxsize=1)
def null_result():
    return analyze_bundle(NULL, recorded_at=STAMP)


def source_rows(path):
    return ([json.loads(line) for line in (path.parent / 'records.jsonl').read_text().splitlines()],
            [json.loads(line) for line in (path.parent / 'evidence.jsonl').read_text().splitlines()],
            json.loads(path.read_text()))


def write_source(root, observations, evidence, manifest):
    """Keep the fixture's explicit physical file pins truthful after source edits."""
    path = rewrite_evidence_bundle(root, observations, evidence, manifest)
    for entry in manifest['record_files']:
        file = root / entry['path']
        entry['expected_sha256'] = K(hashlib.sha256(file.read_bytes()).hexdigest())
    path.write_text(json.dumps(manifest, ensure_ascii=False) + '\n')
    return path


def copy_hero(root):
    shutil.copytree(HERO.parent, root)
    return root / 'bundle.json'


def run_cli(*args):
    return subprocess.run([sys.executable, '-B', '-S', '-m', 'structdet_bench', *map(str, args)],
        cwd=ROOT, env={k: v for k, v in os.environ.items() if k in {'PATH', 'TMPDIR'}},
        capture_output=True, timeout=240)


@functools.lru_cache(maxsize=12)
def recovery_case(name):
    from tests.test_recovery import RecoveryFixture, StageAndCorrectionTests
    from tests.helpers import support_record, record_ref as C
    variants = {'derivative', 'injection', 'recut', 'membership', 'injected_score'}
    with TemporaryDirectory() as tmp:
        case = StageAndCorrectionTests() if name == 'recut' else RecoveryFixture()
        case.root = Path(tmp); case.build('half' if name in variants else name)
        if name == 'derivative':
            case.support('grounding')['payload']['outcome'] = 'not_supported_for_scope'
        elif name == 'injection':
            case.intervention['direct_answer_injection'] = K(True); case.seal_recovery()
        elif name == 'injected_score':
            case.support('pre-iid')['payload']['state'] = 'withdrawn'
            case.support('external-validation')['payload']['extensions']['externally_reviewed_support'] = {
                'expressible_pre': list(CLASS_IDS), 'expressible_post': list(CLASS_IDS), 'external_recovery_rate': '1'}
        elif name == 'recut':
            case.revision()
        elif name == 'membership':
            case.sup.append(support_record('correction', 'withdraw-classification',
                target_refs=[C('assignment', 'a169')], effect='membership', action='withdraw', stage='applied',
                reviewer_refs=[C('role', 'reviewer')], reason=K('Stipulated assignment withdrawal'), event_type='correction'))
        return analyze_bundle(rewrite_evidence_bundle(case.root, case.obs, case.sup, case.man), recorded_at=STAMP)


@functools.lru_cache(maxsize=8)
def curve_case(name):
    from tests.test_half_life import RecordFixture, COUNTS
    from tests.test_longitudinal import A, B
    counts = {'decline': COUNTS, 'stable': [COUNTS[0]] * 4,
        'growth': list(reversed(COUNTS)), 'zero': COUNTS[:3] + [[A] * 32],
        'nongeometric': [COUNTS[0]] * 3 + [COUNTS[3]], 'gap': COUNTS}[name]
    with TemporaryDirectory() as tmp:
        case = RecordFixture(); case.root = Path(tmp); case.build(panels=[counts])
        if name == 'gap':
            case.missing(1); case.seal()
        return analyze_bundle(rewrite_evidence_bundle(case.root, case.obs, case.sup, case.man), recorded_at=STAMP)


class SourceRecordIntegration(unittest.TestCase):
    def test_schema_profile_eight_sections_and_three_outputs(self):
        r = hero_result()
        self.assertEqual(r.exit_code, 0)
        self.assertEqual(r.report['report_schema_version'], '0.3')
        self.assertEqual(r.report['report_profile'], 'structdet_longitudinal_v1')
        self.assertEqual([x['number'] for x in r.report['sections']], list(range(1, 9)))
        self.assertEqual(set(r.manifest['report_files']), {'report.json', 'report.md'})
        for name, body in (('report.json', r.report_json), ('report.md', r.report_markdown)):
            self.assertEqual(r.manifest['report_files'][name], hashlib.sha256(body).hexdigest())

    def test_hero_assay_source_has_192_single_position_calls(self):
        observations, _, manifest = source_rows(HERO)
        assays = manifest['analysis_config']['extensions']['longitudinal']['assays']
        self.assertEqual(len(assays), 2)
        sample_ids = {t['sample_ref']['value']['record_id'] for a in assays for t in a['trials']}
        self.assertEqual(len(sample_ids), 192)
        selected = [r for r in observations if r['record_type'] == 'realization' and r['record_id'] in sample_ids]
        self.assertEqual(len(selected), 192)
        self.assertEqual(len({r['attempt_id']['value'] for r in selected}), 192)
        self.assertTrue(all(r['within_group_index']['value'] == 1 for r in selected))

    def test_half_ERR_uses_original_eight_class_missing_set(self):
        e = episode(hero_result())
        self.assertEqual(set(e['pre_present']), set(CLASS_IDS[:6]))
        self.assertEqual(set(e['missing_classes']), set(CLASS_IDS[6:]))
        self.assertEqual(e['confirmed_recovered'], [CLASS_IDS[6]])
        self.assertEqual(fraction(e['external_recovery_rate']), F(1, 2))
        self.assertEqual(e['external_recovery_rate']['status'], 'available')
        self.assertIsNone(e['partial_information_bounds'])
        self.assertFalse(e['model_recovery_established'])

    def test_assay_exact_threshold_decisions_preserve_full_multiplicity(self):
        study = content(hero_result(), 6)['assays']
        rows = has_fields(study, 'N', 'k_confirmed', 'k_possible', 'delta', 'J')
        self.assertEqual(len(rows), 128)
        self.assertTrue(all(row['N'] == 12 and row['J'] == 128 for row in rows))
        self.assertTrue(all(fraction(row['tau']) == F(1, 2) for row in rows))
        self.assertTrue(all(fraction(row['delta']) == F(1, 2048) for row in rows))
        self.assertTrue(any(row['k_confirmed'] == 12 for row in rows))
        self.assertTrue(any(row['k_possible'] == 0 for row in rows))

    def test_count_derived_diversity_and_independent_log_fit(self):
        f = fit(curve_case('decline'))
        expected = [F(1, 2), F(135, 512), F(15, 128), F(31, 512)]
        self.assertEqual([fraction(x) for x in f['diversities']], expected)
        self.assertEqual(f['times'], [0, 1, 2, 3])
        with localcontext() as context:
            context.prec = 80
            values = [Decimal(x.numerator) / Decimal(x.denominator) for x in expected]
            beta = sum(Decimal(i) * (v.ln() - values[0].ln()) for i, v in enumerate(values)) / Decimal(14)
            expected_shl = -Decimal(2).ln() / beta
        self.assertAlmostEqual(f['empirical']['value'], float(expected_shl), places=12)
        self.assertEqual(f['empirical']['status'], 'available')

    def test_stable_growth_zero_and_nongeometric_have_distinct_reasons(self):
        wanted = {'stable': 'no_decay_on_interval', 'growth': 'growth_on_interval',
            'zero': 'zero_ending_diversity', 'nongeometric': 'non_geometric_registered_residual_exceeded'}
        for name, reason in wanted.items():
            with self.subTest(case=name):
                r = curve_case(name); f = fit(r)
                self.assertEqual(r.exit_code, 0)
                self.assertIsNone(f['empirical']['value'])
                self.assertIn(reason, f['interval']['reasons'] + f['empirical']['reasons'])
        z = fit(curve_case('zero'))
        self.assertEqual(z['first_zero']['left_id'], 'S2')
        self.assertEqual(z['first_zero']['right_id'], 'S3')
        self.assertFalse(z['first_zero']['exact_crossing_time_estimated'])

    def test_missing_expected_state_keeps_clock_gap_and_other_values(self):
        r = curve_case('gap'); f = fit(r)
        self.assertEqual(r.exit_code, 0)
        self.assertEqual(f['times'], [0, 1, 2, 3])
        self.assertIsNone(f['diversities'][1])
        self.assertEqual(fraction(f['diversities'][2]), F(15, 128))
        self.assertIn('missing_expected_measurement', f['empirical']['reasons'])
        self.assertIsNone(f['empirical']['value'])

    def test_empty_missing_set_is_undefined_and_keeps_zero_denominator(self):
        e = episode(recovery_case('empty'))
        self.assertEqual(e['missing_classes'], [])
        self.assertEqual(e['external_recovery_rate']['status'], 'undefined')
        self.assertIsNone(e['external_recovery_rate']['value'])
        self.assertIn('empty_missing_reference_set', e['external_recovery_rate']['reasons'])

    def test_unknown_pre_has_no_exact_missing_denominator(self):
        e = episode(recovery_case('pre_unknown'))
        self.assertIsNone(e['missing_classes'])
        self.assertEqual(e['pre_unresolved'], [CLASS_IDS[5]])
        self.assertEqual(e['external_recovery_rate']['status'], 'unavailable')
        self.assertIsNone(e['partial_information_bounds'])

    def test_partial_post_bounds_are_separate_exact_one_third_two_thirds(self):
        e = episode(recovery_case('partial'))
        self.assertEqual(set(e['missing_classes']), set(CLASS_IDS[5:]))
        self.assertEqual(e['confirmed_recovered'], [CLASS_IDS[5]])
        self.assertEqual(e['unresolved_post'], [CLASS_IDS[6]])
        self.assertEqual(e['post_below'], [CLASS_IDS[7]])
        self.assertEqual([fraction(x) for x in e['partial_information_bounds']], [F(1, 3), F(2, 3)])
        self.assertIsNone(e['external_recovery_rate']['value'])
        self.assertFalse(e['partial_bounds_are_confidence_interval'])

    def test_derivative_grounding_and_direct_injection_withhold_qualified_recovery(self):
        for name in ('derivative', 'injection'):
            with self.subTest(case=name):
                result = recovery_case(name); e = episode(result)
                self.assertEqual(result.exit_code, 0)
                self.assertEqual(e['external_recovery_rate']['status'], 'unavailable')
                self.assertIsNone(e['external_recovery_rate']['value'])
                self.assertEqual(set(e['missing_classes']), set(CLASS_IDS[6:]))
                self.assertFalse(e['model_recovery_established'])

    def test_injected_final_score_cannot_replace_missing_trial_evidence(self):
        r = recovery_case('injected_score'); e = episode(r)
        self.assertIsNone(e['missing_classes'])
        self.assertIsNone(e['external_recovery_rate']['value'])
        self.assertEqual(e['external_recovery_rate']['status'], 'unavailable')
        self.assertFalse(e['model_recovery_established'])

    def test_schema_recut_preserves_original_anomaly_without_creating_recovery(self):
        r = recovery_case('recut'); e = episode(r); section = content(r, 7)
        self.assertEqual(e['external_recovery_rate']['status'], 'unavailable')
        self.assertEqual(len(section['revisions']), 1)
        revision = section['revisions'][0]
        self.assertEqual(revision['revision_kind'], 'schema')
        self.assertEqual(revision['original_refs'][0]['record_id'], 'original-anomaly')
        self.assertEqual(revision['original_availability'], [True])
        self.assertEqual((revision['new_model_samples'], revision['new_recursive_rounds']), (0, 0))
        self.assertFalse(revision['model_recovery_established'])

    def test_membership_correction_invalidates_dependents_and_preserves_unrelated_panels(self):
        r = recovery_case('membership'); changes = content(r, 7)['correction_impacts']
        impact = next(row for row in changes if row['correction_id'] == 'withdraw-classification')
        changed = impact['invalidated_result_refs']; preserved = impact['preserved_result_refs']
        self.assertTrue(any('distribution' in ref and 'M1p6' in ref for ref in changed))
        self.assertTrue(any('err' in ref and 'recover' in ref for ref in changed))
        self.assertTrue(any('distribution' in ref and 'M0p0' in ref for ref in preserved))
        self.assertFalse(impact['old_results_overwritten'])
        self.assertEqual((impact['new_model_samples'], impact['new_recursive_rounds']), (0, 0))
        self.assertIsNone(episode(r)['external_recovery_rate']['value'])

    def test_fixture_provenance_never_becomes_experiment_or_model_recovery(self):
        r = hero_result()
        self.assertEqual(r.manifest['model_calls'], 0)
        self.assertEqual(r.manifest['candidate_programs_executed'], 0)
        self.assertFalse(r.manifest['independent_validation_performed'])
        e = episode(r)
        self.assertEqual(e['evidence_status'], 'fixture_only')
        self.assertEqual((e['new_model_samples'], e['new_recursive_rounds']), (0, 0))
        self.assertFalse(e['structural_exogamy_certified'])

    def test_registered_variants_have_independent_source_rules(self):
        catalogue = json.loads((ROOT / 'tests/fixtures/longitudinal_variants.json').read_text())
        self.assertEqual(catalogue['scope'], 'stipulated_software_fixtures_only')
        self.assertEqual(len({v['id'] for v in catalogue['variants']}), len(catalogue['variants']))
        self.assertTrue(all(v['source_edit'] and v['independent_expected'] for v in catalogue['variants']))
        self.assertTrue({'empty', 'pre_unknown', 'partial', 'decline', 'stable', 'growth', 'zero', 'nongeometric', 'gap'} <= {v['id'] for v in catalogue['variants']})


class ReplayAndCommands(unittest.TestCase):
    def test_manifest_preserves_all_2000_complete_indices_and_independent_hash(self):
        r = hero_result(); carrier = plain(r.manifest['longitudinal_replay'])
        entries = [e for e in carrier['entries'] if e['replay'] is not None]
        self.assertEqual(len(entries), 1)
        replay = entries[0]['replay']; rows = replay['indices']
        self.assertEqual(len(rows), 2000)
        self.assertEqual(len(replay['unit_ids']), 2)
        self.assertTrue(all(len(row) == 2 and all(type(i) is int and 0 <= i < 2 for i in row) for row in rows))
        body = (json.dumps(rows, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()
        self.assertEqual(replay['indices_sha256'], hashlib.sha256(body).hexdigest())
        oracle = json.loads((ROOT / 'tests/fixtures/half_life_oracles.json').read_text())
        self.assertEqual(rows[:len(oracle['replay_first_rows'])], oracle['replay_first_rows'])

    def test_full_manifest_replay_uses_saved_indices_without_rng(self):
        a = hero_result()
        with TemporaryDirectory() as tmp:
            saved = Path(tmp) / 'prior.json'; saved.write_bytes(a.manifest_json)
            with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('fresh random fallback')):
                b = analyze_bundle(HERO, recorded_at=STAMP, replay_manifest_path=saved)
        self.assertEqual(b.exit_code, 0)
        self.assertEqual(content(a, 5), content(b, 5))
        self.assertEqual(content(a, 6), content(b, 6))
        self.assertEqual(a.manifest['longitudinal_replay'], b.manifest['longitudinal_replay'])

    def test_validate_does_not_compute_observed_null_fit_assay_or_recovery(self):
        from contextlib import ExitStack
        from structdet_bench import longitudinal_pipeline as lp
        with ExitStack() as stack:
            for module, name in ((lp.lg, 'observe_longitudinal'), (lp.cn, 'evaluate_categorical_null'), (lp.hl, 'fit_half_lives'), (lp.lu, 'evaluate_longitudinal_sensitivity'), (lp.sa, 'evaluate_support_assays'), (lp.rc, 'evaluate_recovery')):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError('numeric component during validate')))
            result, code = validate_bundle(HERO)
        self.assertEqual(code, 0)
        self.assertTrue(result['longitudinal']['requested'])
        self.assertEqual(result['validation_profile'], 'structdet_longitudinal_v1')

    def test_cli_validate_and_analyze_publish_complete_three_file_set(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / 'out'
            validated = run_cli('validate', '--bundle', HERO)
            self.assertEqual(validated.returncode, 0, validated.stderr)
            self.assertTrue(json.loads(validated.stdout)['longitudinal']['requested'])
            result = run_cli('analyze', '--bundle', NULL, '--output-dir', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in output.iterdir()}, {'report.json', 'report.md', 'run_manifest.json'})
            self.assertEqual(json.loads((output / 'report.json').read_text())['report_schema_version'], '0.3')

    def test_cli_replay_manifest_is_accepted_by_existing_analyze_command(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); saved = root / 'replay.json'; saved.write_bytes(hero_result().manifest_json)
            result = run_cli('analyze', '--bundle', HERO, '--replay-manifest', saved, '--output-dir', root / 'out')
            self.assertEqual(result.returncode, 0, result.stderr)
            replayed = json.loads((root / 'out/run_manifest.json').read_text())
            self.assertEqual(replayed['longitudinal_replay'], plain(hero_result().manifest['longitudinal_replay']))

    def test_malformed_declaration_is_error_not_absent_profile(self):
        with TemporaryDirectory() as tmp:
            p = copy_hero(Path(tmp) / 'input'); observations, evidence, manifest = source_rows(p)
            manifest['analysis_config']['extensions']['longitudinal'] = False
            write_source(p.parent, observations, evidence, manifest)
            v, code = validate_bundle(p); r = analyze_bundle(p)
            self.assertEqual(code, 2); self.assertEqual(r.exit_code, 2)
            self.assertTrue(v['longitudinal']['requested'])
            self.assertEqual(r.report['report_profile'], 'structdet_longitudinal_v1')

    def test_old_M_and_ABC_profiles_preserve_numerical_and_deferred_meanings(self):
        from tests.helpers import materialize_hero
        from tests.test_phase2_pipeline import base_result, content as old_content, ratio
        with TemporaryDirectory() as tmp:
            p, expected = materialize_hero(Path(tmp) / 'm')
            result = analyze_bundle(p)
        self.assertEqual(result.report['report_schema_version'], '0.1')
        self.assertEqual(result.report['report_profile'], 'structdet_measurement_v1')
        for row in old_content(result, 4)['metrics']:
            if row['metric_name'] == 'observed_support_size':
                self.assertEqual(row['value'], expected[row['analysis_population']]['observed_support_size'])
        abc = base_result()
        self.assertEqual(abc.report['report_schema_version'], '0.2')
        self.assertEqual(ratio(old_content(abc)['predictions']['P1']['directions']['surface_gain']['mean']), F(8, 19))
        self.assertNotIn('longitudinal_replay', abc.manifest)
        deferred = {x['metric_name']: x for x in old_content(abc, 8)['deferred']}
        self.assertEqual(deferred['external_recovery_rate']['result_status'], 'deferred')
        self.assertIsNone(deferred['structural_half_life_empirical']['value'])


class FinalWorkflowConformance(unittest.TestCase):
    def test_full_canonical_reports_and_manifest_replay_without_any_new_randomness(self):
        variable = {'recorded_at_utc', 'python_version', 'python_implementation', 'platform', 'replay_source'}
        with TemporaryDirectory() as tmp:
            saved = Path(tmp) / 'replay.json'
            for path, original in ((HERO, hero_result()), (NULL, null_result())):
                with self.subTest(profile=path.parent.name):
                    saved.write_bytes(original.manifest_json)
                    with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('random fallback')):
                        replayed = analyze_bundle(path, replay_manifest_path=saved, recorded_at=STAMP)
                    self.assertEqual(replayed.exit_code, 0)
                    self.assertEqual(replayed.report_json, original.report_json)
                    self.assertEqual(replayed.report_markdown, original.report_markdown)
                    before, after = plain(original.manifest), plain(replayed.manifest)
                    self.assertEqual(set(before['replay_variable_fields']), variable)
                    self.assertEqual({k:v for k,v in before.items() if k not in variable},
                                     {k:v for k,v in after.items() if k not in variable})
                    self.assertIsNotNone(after['replay_source'])

    def test_confirmatory_header_cannot_promote_mock_descendants_to_independent_evidence(self):
        with TemporaryDirectory() as tmp:
            p = copy_hero(Path(tmp) / 'input'); observations, evidence, manifest = source_rows(p)
            manifest['data_role'] = 'confirmatory'
            r = analyze_bundle(write_source(p.parent, observations, evidence, manifest), recorded_at=STAMP)
        scope = content(r, 1)['scope']; last = content(r, 8)
        self.assertEqual(scope['data_role'], 'confirmatory')
        self.assertFalse(scope['independent_validation_performed'])
        self.assertFalse(scope['phase3_complete'])
        self.assertEqual(scope['permitted_claim_scope'], 'supplied_record_finite_scope')
        self.assertTrue(any(row['mock'] for row in last['support_checks']))
        self.assertTrue(all(row['outcome'] == 'unresolved' for row in last['five_conditions']))
        self.assertEqual(last['workflow_status']['repository_delivery'], 'not_assessed_by_command')
        self.assertEqual(last['ec_reporting_disclosures']['live_field_evidence'], 'not_established_by_toolkit')
        self.assertIn('latent_support', content(r, 1)['quantities_not_activated'])
        self.assertEqual(r.manifest['model_calls'], 0)
        self.assertEqual(r.manifest['candidate_programs_executed'], 0)
