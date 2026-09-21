"""Populated and absent longitudinal report semantics, with JSON/Markdown parity."""
from __future__ import annotations

import copy
import hashlib
import html
import json
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from structdet_bench.contracts import CLASS_IDS, InputError, INTEGRITY_CONDITIONS
from structdet_bench.reporting import plain, render_json, render_markdown
from tests.helpers import support_record, record_ref as C, tagged as K, rewrite_evidence_bundle
from tests.test_phase3_pipeline import (ROOT, HERO, NULL, STAMP, hero_result, null_result,
    content, dictionaries, has_fields, fraction, episode, fit, curve_case, recovery_case,
    source_rows, copy_hero, write_source)
from structdet_bench.pipeline import analyze_bundle


def parity(test, result, records):
    """Check real field values rather than an empty wildcard or renderer snapshot."""
    test.assertTrue(records)
    markdown = result.report_markdown.decode()
    for record in records:
        test.assertIsInstance(record, dict)
        test.assertTrue(record)
        for key, value in record.items():
            token = html.escape(json.dumps(value, ensure_ascii=True, sort_keys=True,
                separators=(',', ':'), allow_nan=False), quote=True).replace('|', '&#124;')
            test.assertIn(token, markdown, key)


class LongitudinalReportGroups(unittest.TestCase):
    def test_RF01_profile_sources_methods_and_fixture_claim_scope(self):
        r = hero_result(); scope = content(r, 1)
        self.assertEqual(scope['scope']['permitted_claim_scope'], 'fixture_only')
        self.assertFalse(scope['scope']['phase3_complete'])
        self.assertFalse(scope['scope']['independent_validation_performed'])
        self.assertEqual(len(scope['source_pins']), 3)
        self.assertIn('finite_family_binomial_threshold_v1', scope['methods'].values())
        self.assertIn('actual_independent_evidence_outstanding', scope['scope'].values())
        parity(self, r, [scope['scope'], scope['methods']])
        self.assertNotIn('recovery', content(null_result(), 1)['requested_capabilities'])

    def test_RF02_states_stages_identities_measurement_refs_and_absent_neural_states(self):
        r = hero_result(); state_rows = content(r, 2)['states']
        self.assertGreaterEqual(len(state_rows), 6)
        self.assertTrue(all(row['ref']['object_kind'] == 'state' for row in state_rows))
        for row in state_rows:
            self.assertIn('state_kind', row['declaration'])
            self.assertIn('stage_role', row['declaration'])
            self.assertIn('subject_identity', row['declaration'])
            self.assertIn('measurement_refs', row['declaration'])
        parity(self, r, [state_rows[0]['declaration']])
        null_states = content(null_result(), 2)['states']
        self.assertEqual(null_states, [])

    def test_RF03_lineage_paths_clocks_and_actual_missing_schedule(self):
        r = hero_result(); records = content(r, 2)
        self.assertTrue(records['transitions']); self.assertTrue(records['trajectories']); self.assertTrue(records['roots'])
        self.assertTrue(any(len(x['declaration']['state_refs']) >= 4 for x in records['trajectories']))
        for row in records['trajectories']:
            self.assertIn('round_coordinates', row['declaration']); self.assertIn('schedule', row['declaration'])
        fork = next(row['declaration'] for row in records['states'] if row['ref']['object_id'] == 'T-fork')
        self.assertEqual(fork['ancestor_refs']['value'][0]['object_id'], 'T-S1')
        parity(self, r, [records['trajectories'][-1]['declaration']])
        gap = curve_case('gap'); slots = has_fields(content(gap, 2)['trajectories'], 'observation_status', 'measurement_ref')
        missing = [row for row in slots if row['observation_status'] == 'missing']
        self.assertEqual(len(missing), 1); self.assertIsNone(missing[0]['measurement_ref']['value'])
        parity(self, gap, missing)

    def test_RF04_population_denominators_budgets_and_absent_measurement(self):
        r = hero_result(); rows = content(r, 2)['inventories']
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row['classified_all_count'], len(row['selected_sample_ids']))
            self.assertGreater(row['planned_positions'], 0)
            self.assertLessEqual(row['classified_valid_count'], row['classified_all_count'])
            self.assertIn('ratios', row); self.assertIn('requested_sample_ids', row)
        parity(self, r, [rows[0]])
        self.assertEqual(content(null_result(), 2)['inventories'], [])
        self.assertEqual(content(null_result(), 3)['status'], 'not_requested')

    def test_RF05_observed_diversity_sets_tail_and_undefined_empty_population(self):
        r = hero_result(); measurements = content(r, 3)['measurements']
        self.assertTrue(measurements)
        self.assertEqual(set(content(r, 3)['views']), {'classified_all', 'classified_valid'})
        self.assertTrue(all('diversity' in row and 'distribution' in row for row in measurements))
        parity(self, r, [measurements[0]['diversity']])
        requests = content(r, 4)['observed_requests']
        self.assertTrue(requests)
        self.assertTrue(has_fields(requests, 'became_unobserved', 'newly_observed', 'retention'))
        protected = next(row for row in requests if row['ref']['object_id'] == 'T-obs')['tails']
        self.assertEqual(len(protected), 1)
        self.assertEqual(protected[0]['class_id'], 'SORT-SEL')
        self.assertEqual([row['count'] for row in protected[0]['observations']], [1, 0, None, 1])
        self.assertEqual(protected[0]['observations'][-1]['recurrence'], 'observed_reappearance')
        parity(self, r, protected[0]['observations'])
        self.assertEqual(content(null_result(), 3)['measurements'], [])
        self.assertEqual(content(null_result(), 4)['observed_requests'], [])

    def test_RF06_stage_records_do_not_turn_training_exposure_into_probe_samples(self):
        r = hero_result(); rows = content(r, 4)['stage_transitions']
        self.assertTrue(rows)
        self.assertTrue(any('training_exposure' in json.dumps(row) for row in rows))
        self.assertTrue(any('generated_candidates' in json.dumps(row) for row in rows))
        selected = next(row for row in rows if row['child_ref']['object_id'] == 'C-S1')
        exposed = next(row for row in rows if row['child_ref']['object_id'] == 'C-S2')
        self.assertEqual(fraction(selected['changes'][0][2]['retention']), F(2, 3))
        self.assertEqual(fraction(exposed['changes'][0][2]['retention']), F(1))
        self.assertFalse(selected['model_expression_established'])
        self.assertFalse(exposed['causal_parent_assignment_performed'])
        parity(self, r, [selected, exposed])
        self.assertEqual(content(null_result(), 4)['stage_transitions'], [])
        self.assertEqual(r.manifest['model_calls'], 0)

    def test_RF07_categorical_exact_arithmetic_assumptions_and_missing_target(self):
        r = null_result(); records = content(r, 4)['categorical_scenarios']
        self.assertTrue(records)
        rows = [x['result'] for x in records if x['result'] is not None]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row['distribution_scope'], 'explicit_finite_categorical_scenario')
            self.assertFalse(row['empirical_pipeline_matches_null'])
            self.assertFalse(row['substantive_validation_performed'])
            self.assertEqual(row['simulated_draws'], 0)
            if row['scenario_id'] == 'balanced-two':
                self.assertEqual(fraction(row['expected_next_diversity']), F(1, 4))
                self.assertEqual([fraction(x['expected_diversity']) for x in row['forecast']], [F(1, 2**(i+1)) for i in range(4)])
                self.assertEqual(fraction(row['structural_half_life_null']), F(1))
                self.assertTrue(all(fraction(v) == F(1, 4) for v in row['omission_probabilities'].values()))
        with TemporaryDirectory() as tmp:
            manifest = json.loads(NULL.read_text()); path = Path(tmp) / 'bundle.json'
            for declaration, status in ((K(None), 'not_requested'), (K(state='unknown'), 'unavailable')):
                for scenario in manifest['analysis_config']['extensions']['longitudinal']['null_scenarios']:
                    scenario['q'] = declaration
                path.write_text(json.dumps(manifest))
                absent = analyze_bundle(path, recorded_at=STAMP)
                balanced = next(x['result'] for x in content(absent, 4)['categorical_scenarios']
                    if x['binding']['ref']['object_id'] == 'balanced-two')
                self.assertIsNone(balanced['target'])
                self.assertEqual(balanced['target_status'], status)
                self.assertIsNone(balanced['target_error']['value'])
                parity(self, absent, [balanced['target_error']])
        parity(self, r, [rows[0]['expected_next_diversity'], rows[0]['structural_half_life_null']])
        self.assertEqual({row['scenario_id'] for row in rows}, {'balanced-two', 'open-refusal'})
        refused = next(row for row in rows if row['scenario_id'] == 'open-refusal')
        self.assertIsNone(refused['expected_next_diversity']['value'])
        self.assertEqual(refused['forecast_status'], 'unavailable')
        self.assertEqual(content(curve_case('stable'), 4)['categorical_scenarios'], [])

    def test_RF08_fit_residuals_window_rounds_and_zero_crossing_absence(self):
        r = curve_case('decline'); f = fit(r)
        self.assertEqual(f['state_ids'], ['S0', 'S1', 'S2', 'S3'])
        self.assertEqual(f['times'], [0, 1, 2, 3])
        self.assertEqual(len(f['log_residuals']), 4)
        self.assertEqual(f['first_zero']['status'], 'not_observed')
        self.assertFalse(f['half_crossing']['exact_crossing_time_estimated'])
        parity(self, r, [f['empirical'], f['interval'], f['half_crossing']])
        self.assertEqual(content(null_result(), 5)['half_life'], [])
        self.assertEqual(content(null_result(), 5)['half_life_status'], 'not_requested')

    def test_RF09_sensitivity_complete_draw_statuses_grid_and_absent_interval(self):
        r = hero_result(); rows = content(r, 5)['sensitivity']
        self.assertEqual(len(rows), 1); row = rows[0]
        self.assertEqual(len(row['draws']), 2000)
        self.assertEqual([x['index'] for x in row['draws']], list(range(2000)))
        self.assertEqual(row['interval_scope'], 'resampling_sensitivity')
        self.assertFalse(row['population_confidence_established'])
        self.assertFalse(row['filtered_success_interval_computed'])
        self.assertFalse(row['training_lineage_variability_estimated'])
        self.assertEqual(row['round_grid'], [0, 1, 2, 3])
        parity(self, r, [row['draws'][0], row['draws'][-1]])
        self.assertEqual(content(null_result(), 5)['sensitivity'], [])
        self.assertEqual(content(null_result(), 5)['sensitivity_status'], 'not_requested')

    def test_RF10_assay_N_k_threshold_tails_and_absent_assays(self):
        r = hero_result(); assays = content(r, 6)['assays']
        self.assertEqual(len(assays), 2)
        for assay in assays:
            self.assertEqual(len(assay['intervention_refs']), 8)
            self.assertEqual(assay['success_event'], 'class_membership')
            self.assertEqual(assay['J'], 128)
            self.assertEqual(fraction(assay['alpha']), F(1, 8))
            self.assertEqual(fraction(assay['delta']), F(1, 2048))
            decision = assay['cells'][0]['decision']
            self.assertEqual(decision['N'], 12)
            self.assertIsNotNone(decision['upper_tail']); self.assertIsNotNone(decision['lower_tail'])
            positive = [cell['decision'] for cell in assay['cells'] if cell['decision']['k_confirmed'] == 12]
            negative = [cell['decision'] for cell in assay['cells'] if cell['decision']['k_possible'] == 0]
            self.assertTrue(positive); self.assertTrue(negative)
            self.assertTrue(all(fraction(item['upper_tail']) == F(1, 4096) for item in positive))
            self.assertTrue(all(fraction(item['lower_tail']) == F(1, 4096) for item in negative))
            parity(self, r, [decision])
        self.assertEqual(content(null_result(), 6)['assays'], [])
        self.assertEqual(content(null_result(), 6)['assay_status'], 'not_requested')

    def test_RF11_expressible_sets_reference_denominator_and_unresolved_state(self):
        r = hero_result(); pre, post = content(r, 6)['assays']
        self.assertEqual(pre['present_classes'], list(CLASS_IDS[:6]))
        self.assertEqual(post['present_classes'], list(CLASS_IDS[:7]))
        self.assertEqual(fraction(pre['reference_normalized_support']), F(3, 4))
        self.assertEqual(fraction(post['reference_normalized_support']), F(7, 8))
        self.assertFalse(pre['latent_support_established'])
        parity(self, r, [pre['reference_normalized_support'], post['reference_normalized_support']])
        uncertain = recovery_case('pre_unknown')
        self.assertEqual(content(uncertain, 6)['assays'][0]['unresolved_classes'], [CLASS_IDS[5]])
        parity(self, uncertain, [episode(uncertain)['external_recovery_rate']])

    def test_RF12_missing_recovered_sets_and_partial_unavailable_rate(self):
        r = hero_result(); row = episode(r)
        self.assertEqual(len(row['missing_classes']), 2)
        self.assertEqual(len(row['confirmed_recovered']), 1)
        parity(self, r, [row['external_recovery_rate']])
        partial = recovery_case('partial'); p = episode(partial)
        self.assertIsNone(p['external_recovery_rate']['value'])
        self.assertEqual([fraction(x) for x in p['partial_information_bounds']], [F(1, 3), F(2, 3)])
        parity(self, partial, [p['external_recovery_rate'], {'partial_information_bounds': p['partial_information_bounds']}])

    def test_RF13_all_five_exogamy_stages_and_no_inferred_causal_claim(self):
        r = hero_result(); e = episode(r)
        self.assertEqual({x['stage'] for x in e['stages']}, {'entry', 'preprocessing', 'selection', 'exposure', 'expression'})
        self.assertTrue(e['changes_model_parameters'])
        self.assertFalse(e['model_recovery_established'])
        self.assertTrue(all(not x['inferred_from_score'] for x in e['stages']))
        self.assertTrue(e['gates'])
        parity(self, r, e['stages'])
        self.assertEqual(content(null_result(), 6)['recovery'], [])
        self.assertEqual(content(null_result(), 6)['recovery_status'], 'not_requested')

    def test_RF14_recut_originals_dependencies_and_zero_new_observations(self):
        r = recovery_case('recut'); section = content(r, 7)
        self.assertTrue(section['revisions'])
        self.assertTrue(section['dependencies'])
        self.assertTrue(section['original_anomalies_retained'])
        self.assertFalse(section['prior_results_overwritten'])
        self.assertEqual(section['new_samples_created_by_reclassification'], 0)
        self.assertEqual(section['new_recursive_rounds_created_by_reclassification'], 0)
        parity(self, r, [section['revisions'][0]])
        self.assertEqual(content(null_result(), 7)['revisions'], [])

    def test_RF15_five_conditions_ten_disclosures_and_no_invented_expiry(self):
        r = hero_result(); section = content(r, 8)
        self.assertEqual({x['condition'] for x in section['five_conditions']}, set(INTEGRITY_CONDITIONS))
        self.assertTrue(all(x['outcome'] == 'unresolved' for x in section['five_conditions']))
        self.assertEqual(len(section['ec_reporting_disclosures']), 10)
        self.assertEqual(section['ec_reporting_disclosures']['current_until']['state'], 'unknown')
        self.assertEqual(section['ec_reporting_disclosures']['live_field_evidence'], 'not_established_by_toolkit')
        self.assertFalse(section['currentness']['declared_expiry_is_certification'])
        self.assertIn('deployment_representativeness', section['omitted_conditions'])
        parity(self, r, [section['ec_reporting_disclosures'], section['currentness']])

    def test_RF16_processing_limits_redaction_and_separate_publication_scope(self):
        r = hero_result(); first = content(r, 1); last = content(r, 8)
        self.assertEqual(first['processing']['exit_code'], 0)
        self.assertEqual(first['effective_limits']['sensitivity_replicates'], 2000)
        self.assertTrue(first['frozen_baseline'])
        self.assertEqual(last['workflow_status']['repository_delivery'], 'not_assessed_by_command')
        self.assertEqual(last['workflow_status']['owner_acceptance'], 'not_assessed_by_command')
        self.assertFalse(last['redaction']['source_bytes_modified'])
        self.assertIn('repository publication', ' '.join(last['release_restrictions']))
        self.assertNotIn('overall_score', r.report)
        self.assertNotIn('inbreeding_score', r.report)
        parity(self, r, [first['processing'], last['redaction']])
        self.assertEqual(content(null_result(), 5)['half_life_status'], 'not_requested')


class RenderingAndCurrentness(unittest.TestCase):
    def test_complete_JSON_tree_and_eight_markdown_sections_have_same_values(self):
        from structdet_bench.reporting import LONGITUDINAL_SECTION_TITLES
        r = hero_result()
        self.assertEqual(json.loads(r.report_json), plain(r.report))
        self.assertEqual(render_json(r.report), r.report_json)
        self.assertEqual(render_markdown(r.report), r.report_markdown)
        for number, title in enumerate(LONGITUDINAL_SECTION_TITLES, 1):
            self.assertIn(f'## {number}. {title}'.encode(), r.report_markdown)
        self.assertLess(r.report_markdown.index(b'Independent scientific validation'), r.report_markdown.index(b'## 3.'))

    def test_schema_profile_wrong_order_nonfinite_and_unknown_content_keys_fail(self):
        base = plain(null_result().report)
        invalids = []
        r = copy.deepcopy(base); r['report_profile'] = 'structdet_comparison_v1'; invalids.append(r)
        r = copy.deepcopy(base); r['sections'][0], r['sections'][1] = r['sections'][1], r['sections'][0]; invalids.append(r)
        r = copy.deepcopy(base); r['sections'][0]['content']['nonfinite'] = float('inf'); invalids.append(r)
        r = copy.deepcopy(base); r['sections'][0]['content']['<script>private</script>'] = 1; invalids.append(r)
        for report in invalids:
            with self.assertRaises(InputError): render_json(report)
            with self.assertRaises(InputError): render_markdown(report)

    def test_declared_scoped_dates_survive_both_formats_without_certification(self):
        with TemporaryDirectory() as tmp:
            p = copy_hero(Path(tmp) / 'input'); observations, evidence, manifest = source_rows(p)
            evidence.append(support_record('integrity_assessment', 'dated-longitudinal',
                claim_kind='validated_measurement', claim='Mock scoped currentness only', requirements={},
                declared_disposition='restricted', assessed_at=K('2026-09-10'), current_until=K('2026-10-01'),
                reviewer_refs=[C('role', 'reviewer')], scope_refs=[C('cell', 'c0p0')]))
            r = analyze_bundle(write_source(p.parent, observations, evidence, manifest), recorded_at=STAMP)
        rows = [x for x in content(r, 8)['declared_claim_records'] if x['record_id'] == 'dated-longitudinal']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['current_until']['value'], '2026-10-01')
        self.assertEqual(rows[0]['assessed_at']['value'], '2026-09-10')
        self.assertEqual(rows[0]['scope_refs'][0]['record_id'], 'c0p0')
        self.assertEqual(rows[0]['substantive_claim'], 'not_certified_by_software')
        parity(self, r, rows)


class FinalReportConformance(unittest.TestCase):
    def test_all_ten_named_EC_disclosures_and_five_conditions_survive_absent_capabilities(self):
        expected = {'capability_and_scope', 'structural_cut_and_known_omissions',
            'source_and_transformation_lineage', 'exposure_and_bias_controls', 'evaluator_identity',
            'class_and_tail_outcomes', 'horizon_recovery_override', 'live_field_evidence',
            'correction_path', 'current_until'}
        for result in (hero_result(), null_result()):
            row = content(result, 8)
            self.assertEqual(set(row['ec_reporting_disclosures']), expected)
            self.assertEqual({x['condition'] for x in row['five_conditions']}, set(INTEGRITY_CONDITIONS))
            self.assertEqual(len(row['five_conditions']), 5)
            self.assertTrue(all(x['outcome'] == 'unresolved' for x in row['five_conditions']))
            self.assertFalse(row['currentness']['declared_expiry_is_certification'])
            self.assertIn('complete_expressible_or_latent_repertoire', row['omitted_conditions'])
            parity(self, result, [row['ec_reporting_disclosures'], row['currentness'], row['workflow_status']])

    def test_distinct_ERR_absence_states_keep_exact_sets_and_denominators_in_both_formats(self):
        cases = ((hero_result(), 'available'), (recovery_case('empty'), 'undefined'),
            (recovery_case('pre_unknown'), 'unavailable'), (recovery_case('partial'), 'unavailable'))
        for result, status in cases:
            with self.subTest(status=status, input=result.manifest['input_fingerprint']):
                row = episode(result)
                self.assertEqual(row['external_recovery_rate']['status'], status)
                if status != 'available': self.assertIsNone(row['external_recovery_rate']['value'])
                parity(self, result, [{k: row[k] for k in ('missing_classes', 'confirmed_recovered',
                    'unresolved_post', 'external_recovery_rate', 'partial_information_bounds')}])
        self.assertEqual(content(null_result(), 6)['recovery_status'], 'not_requested')
        self.assertEqual(content(null_result(), 6)['recovery'], [])
        parity(self, null_result(), [{'recovery_status': 'not_requested', 'recovery': []}])

    def test_correction_and_recut_reports_preserve_audit_refs_without_new_observation_claims(self):
        for name in ('membership', 'recut', 'derivative', 'injection'):
            with self.subTest(variant=name):
                result = recovery_case(name); changes = content(result, 7)
                self.assertEqual(episode(result)['external_recovery_rate']['status'], 'unavailable')
                self.assertFalse(changes['prior_results_overwritten'])
                self.assertEqual(changes['new_samples_created_by_reclassification'], 0)
                self.assertEqual(changes['new_recursive_rounds_created_by_reclassification'], 0)
                parity(self, result, [episode(result)['external_recovery_rate']])
                # Top-level record lists render as individual tables. Check every
                # dependency, revision and impact record in its actual table form.
                for key in ('dependencies', 'revisions', 'correction_impacts'):
                    if changes[key]: parity(self, result, changes[key])
                parity(self, result, [{key: value for key, value in changes.items()
                    if key not in {'dependencies', 'revisions', 'correction_impacts'}}])
                self.assertEqual(json.loads(result.report_json), plain(result.report))

    def test_sanitized_processing_failure_retains_eight_sections_and_disclosures(self):
        with TemporaryDirectory() as tmp:
            p = copy_hero(Path(tmp) / 'input'); observations, evidence, manifest = source_rows(p)
            manifest['analysis_config']['extensions']['longitudinal'] = False
            result = analyze_bundle(write_source(p.parent, observations, evidence, manifest), recorded_at=STAMP)
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(len(result.report['sections']), 8)
        self.assertEqual(content(result, 1)['processing']['exit_code'], 2)
        self.assertEqual(len(content(result, 8)['ec_reporting_disclosures']), 10)
        self.assertFalse(content(result, 1)['scope']['phase3_complete'])
        parity(self, result, [content(result, 1)['processing'], content(result, 8)['workflow_status']])
