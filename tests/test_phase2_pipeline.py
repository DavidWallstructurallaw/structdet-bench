"""Phase 2 Step 6: text-bearing fixture-to-report tests, never model experiments."""
from __future__ import annotations
import copy
import functools
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from fractions import Fraction as F
from structdet_bench.pipeline import analyze_bundle, validate_bundle, write_analysis
from structdet_bench.reporting import plain, render_json, render_markdown
from tests.phase2_helpers import ROOT, materialize_abc, independent_abc_expected, write_abc
from tests.helpers import tagged, record_ref, artifact_record, materialize_hero

STAMP='2026-09-19T02:00:00+00:00'


@functools.lru_cache(maxsize=1)
def base_result():
    return analyze_bundle(ROOT/'examples/hero_abc/bundle.json', recorded_at=STAMP)


def content(r, n=6): return r.report['sections'][n-1]['content']

def ratio(value):
    if isinstance(value,dict) and 'numerator' in value:return F(value['numerator'],value['denominator'])
    return F(*value['exact_ratio'])


def fixture_rows(p):
    return ([json.loads(x) for x in (p.parent/'records.jsonl').read_text().splitlines()],
            [json.loads(x) for x in (p.parent/'evidence.jsonl').read_text().splitlines()],json.loads(p.read_text()))


class FixtureIntegration(unittest.TestCase):
    def test_complete_72_calls_360_positions_and_both_views(self):
        r=base_result();self.assertEqual(r.exit_code,0)
        self.assertEqual(len(content(r,2)['inventory']),18)
        self.assertEqual(len(content(r,2)['attempts']),72)
        self.assertEqual(sum(x['selected_realization_count']['value'] for x in content(r,2)['inventory']),360)
        self.assertEqual(len(content(r,7)['diagnostics']),36)
        self.assertEqual(len(content(r)['per_block_contrasts']),36)
    def test_every_text_distance_Q_and_within_mean_matches_independent_oracle(self):
        expected=independent_abc_expected();stored=json.loads((ROOT/'examples/hero_abc/expected.json').read_text())
        for d in content(base_result(),7)['diagnostics']:
            e=expected['cells'][d['cell_id']]
            for metric,key in [('surface_lexical_trigram_distance','L'),('structural_pair_non_equivalence','Q'),('within_class_realization_diversity_proxy','within')]:
                self.assertEqual(ratio(d['results'][metric]),e[key]);self.assertEqual(ratio(stored['cells'][d['cell_id']][key]),e[key])
            self.assertEqual(d['pair_count'],190)
    def test_primary_directions_and_degenerate_ranges_are_exact(self):
        r=base_result();p=content(r)['predictions'];self.assertEqual(p['P1']['outcome'],'supporting');self.assertEqual(p['P5']['outcome'],'supporting')
        for k in ['surface_gain','p1_proxy_gain_contrast']:
            d=p['P1']['directions'][k]
            self.assertEqual(ratio(d['mean']),F(8,19));self.assertEqual(ratio(d['lower']),F(8,19));self.assertEqual(ratio(d['upper']),F(8,19))
        self.assertEqual(ratio(p['P1']['directions']['structural_gain']['mean']),0)
        self.assertIn('degenerate_range_is_not_general_certainty',p['P1']['qualifications'])
    def test_p5_comparators_each_retain_valid_distinct20(self):
        p=content(base_result())['predictions'];self.assertEqual({o['condition_pair'] for o in p['P5_comparators']},{'C-A','C-B'})
        for o in p['P5_comparators']:self.assertEqual(ratio(o['directions']['p5_valid_distinct_k_delta']['mean']),1)
    def test_fixture_source_maps_bytes_to_one_current_class(self):
        p=ROOT/'examples/hero_abc/bundle.json';o,_,_=fixture_rows(p)
        labels={r['sample_id']:r['structural_class_id'] for r in o if r['record_type']=='assignment'};mapping={}
        for r in o:
            if r['record_type']=='realization':mapping.setdefault(r['output_content_hash']['value'],set()).add(labels[r['sample_id']])
        self.assertTrue(all(len(s)==1 for s in mapping.values()))
        self.assertEqual(len(list((p.parent).glob('text_*.txt'))),8)
    def test_fixture_registration_prompts_are_actual_declared_passive_bytes(self):
        prompts=json.loads((ROOT/'examples/hero_abc/prompts.json').read_text());self.assertEqual(len(prompts['prompts']),18)
        for b in [f'P{i:02}' for i in range(1,7)]:self.assertEqual(prompts['prompts'][b+'-A'],prompts['prompts'][b+'-B'])
        self.assertTrue(any(x['sha256']==hashlib.sha256((ROOT/'examples/hero_abc/prompts.json').read_bytes()).hexdigest() for x in base_result().manifest['input_refs']))
    def test_fixture_never_becomes_sorting_program_or_empirical_validation(self):
        r=base_result();self.assertEqual(content(r,1)['scope']['data_role'],'fixture')
        self.assertEqual(r.manifest['model_calls'],0);self.assertEqual(r.manifest['candidate_programs_executed'],0)
        self.assertFalse(r.manifest['independent_validation_performed'])
        self.assertTrue(all(x['permitted_claim_scope']=='fixture_only' for x in content(r)['primary_results']))
    def test_repeated_text_keeps_distinct_observations_and_group_dependencies(self):
        d=next(x for x in content(base_result(),7)['diagnostics'] if x['cell_id']=='P01-A' and x['analysis_population']=='classified_all')
        self.assertEqual(len(d['eligible_sample_ids']),20);self.assertEqual(len(d['pairs']),190)
        self.assertIsNone(d['independent_draw_count']);self.assertEqual(sum(p['same_call'] is True for p in d['pairs']),40)
    def test_independent_index_sequence_hash_and_full_matrix_are_stored(self):
        m=base_result().manifest;rs=m['comparison_replay']['replays'];self.assertEqual(len(rs),1)
        self.assertEqual(rs[0]['indices_sha256'],independent_abc_expected()['indices_sha256'])
        self.assertEqual(len(rs[0]['indices']),2000);self.assertTrue(all(len(x)==6 for x in rs[0]['indices']))
        self.assertEqual(m['comparison_replay_sha256'],hashlib.sha256(__import__('structdet_bench.reporting',fromlist=['canonical_bytes']).canonical_bytes(m['comparison_replay'])).hexdigest())
    def test_no_tokens_or_program_bodies_copied_into_report(self):
        r=base_result();self.assertNotIn(b'a b c',r.report_json);self.assertNotIn(b'e f g',r.report_markdown)
        self.assertNotIn(b'MOCK-OBSERVER',r.report_json)
    def test_metric_modules_remain_in_software_identity(self):
        hashes=base_result().manifest['software']['files']
        for name in ['comparison_records.py','text_diagnostics.py','comparisons.py','uncertainty.py','predictions.py','comparison_pipeline.py']:
            self.assertEqual(hashes[name],hashlib.sha256((ROOT/'structdet_bench'/name).read_bytes()).hexdigest())
    def test_report_profile_is_explicit_and_versioned(self):
        r=base_result();self.assertEqual(r.report['report_schema_version'],'0.2');self.assertEqual(r.report['report_profile'],'structdet_comparison_v1')
        self.assertEqual(r.manifest['report_profile'],r.report['report_profile'])
    def test_original_HF00_and_six_variants_keep_M_profile_and_oracles(self):
        with TemporaryDirectory() as t:
            for i in range(7):
                p,e=materialize_hero(Path(t)/str(i),f'HF-{i:02}');r=analyze_bundle(p)
                self.assertEqual(r.exit_code,e['exit_code']);self.assertEqual(r.report['report_schema_version'],'0.1')
                self.assertEqual(r.report['report_profile'],'structdet_measurement_v1');self.assertNotIn('comparison_replay',r.manifest)
                for row in content(r,4)['metrics']:
                    if row['metric_name']=='observed_support_size':self.assertEqual(row['value'],e[row['analysis_population']]['observed_support_size'])


class AdverseStudies(unittest.TestCase):
    def check_variant(self,name):
        with TemporaryDirectory() as t:
            p,e=materialize_abc(Path(t)/'input',name);r=analyze_bundle(p,recorded_at=STAMP);pred=content(r)['predictions']
            self.assertEqual(r.exit_code,e['expected_processing_exit']);self.assertEqual(pred['P1']['outcome'],e['P1']);self.assertEqual(pred['P5']['outcome'],e['P5'])
            return r
    def test_adverse_primary_still_has_processing_success(self):self.check_variant('ABC-CONTRARY')
    def test_mixed_P5_keeps_both_comparators(self):
        r=self.check_variant('ABC-MIXED');p=content(r)['predictions']
        self.assertTrue(p['mixed_comparator_behavior']);self.assertEqual([o['outcome'] for o in p['P5_comparators']],['supporting','contrary'])
    def test_heterogeneous_blocks_have_independent_non_degenerate_interval(self):
        r=self.check_variant('ABC-HETEROGENEOUS');d=content(r)['predictions']['P1']['directions']['p1_proxy_gain_contrast'];e=independent_abc_expected('ABC-HETEROGENEOUS')
        for name,key in [('mean','p1_mean'),('lower','p1_lower'),('upper','p1_upper')]:self.assertEqual(ratio(d[name]),e[key])
        self.assertLess(ratio(d['lower']),0);self.assertGreater(ratio(d['upper']),0);self.assertGreater(ratio(d['mean']),0)
    def test_absent_text_restricts_P1_preserves_P5(self):
        r=self.check_variant('ABC-NO-TEXT');self.assertEqual(sum(x['selected_realization_count']['value'] for x in content(r,2)['inventory']),360)
    def test_B_control_unknown_keeps_complete_C_A_path(self):
        r=self.check_variant('ABC-NO-B-CONTROL');self.assertEqual(content(r)['predictions']['P5_comparators'][0]['outcome'],'supporting')
    def test_missing_block_cannot_be_removed_from_full_target(self):
        r=self.check_variant('ABC-MISSING-BLOCK');p=content(r)['predictions']['P1'];self.assertEqual(len(p['intended_blocks']),6);self.assertLess(len(p['actual_blocks']),6)
    def test_supported_label_revision_recomputes_without_new_samples(self):
        r=self.check_variant('ABC-CORRECTED');self.assertEqual(sum(x['selected_realization_count']['value'] for x in content(r,2)['inventory']),360)
        ids=content(r,8)['preserved_revision_ids'];self.assertIn(('assignment','P01-C-a11'),ids);self.assertIn(('assignment','P01-C-a11-r2'),ids)
        self.assertEqual(content(r,8)['comparison_integrity']['comparison_revision']['prior_run_ids'],('prior-fixture-run',))
    def test_quality_confounded_positive_breadth_stays_visible(self):
        r=self.check_variant('ABC-QUALITY');p=content(r)['predictions']['P5_comparators'][0]
        self.assertEqual(ratio(p['directions']['p5_valid_distinct_k_delta']['mean']),2)
    def test_independence_withdrawal_retains_numbers_restricts_claim(self):
        r=self.check_variant('ABC-INDEPENDENCE-WITHDRAWN');self.assertEqual(content(r,4),content(base_result(),4))
        self.assertEqual(ratio(content(r)['predictions']['P1']['directions']['surface_gain']['mean']),F(8,19))
    def test_text_correction_changes_P1_without_changing_structure(self):
        r=self.check_variant('ABC-TEXT-CHANGED');self.assertEqual(content(r,4),content(base_result(),4))
    def test_unrequested_question_is_not_an_error_or_an_outcome(self):
        r=self.check_variant('ABC-P5-ONLY');self.assertEqual(content(r)['predictions']['P1']['result_status'],'not_requested')
    def test_unregistered_variant_is_not_executable_configuration(self):
        with TemporaryDirectory() as t:
            with self.assertRaises(ValueError):materialize_abc(Path(t)/'x','run-arbitrary-command')


class InputAndReplay(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.path,_=materialize_abc(self.root/'input')
    def edit(self,fun):
        o,s,m=fixture_rows(self.path);fun(o,s,m);return write_abc(self.path.parent,o,s,m)
    def test_validate_checks_comparison_without_numeric_computation(self):
        with patch('structdet_bench.comparison_pipeline.diagnose_cells',side_effect=AssertionError('numeric')),patch('structdet_bench.comparison_pipeline.compare_study',side_effect=AssertionError('numeric')),patch('structdet_bench.comparison_pipeline.resample_study',side_effect=AssertionError('numeric')),patch('structdet_bench.comparison_pipeline.evaluate_predictions',side_effect=AssertionError('numeric')):
            r,code=validate_bundle(self.path)
        self.assertEqual(code,0);self.assertTrue(r['comparison']['requested'])
    def test_M_only_analysis_never_calls_numeric_V_components(self):
        self.edit(lambda o,s,m:m['analysis_config']['extensions'].pop('comparison'))
        with patch('structdet_bench.comparison_pipeline.diagnose_cells',side_effect=AssertionError('V called')):
            r=analyze_bundle(self.path)
        self.assertEqual(r.report['report_profile'],'structdet_measurement_v1')
    def test_malformed_extension_not_ignored(self):
        for val in (False,None,{},[],{'comparison_schema_version':'9'}):
            self.edit(lambda o,s,m:m['analysis_config']['extensions'].update(comparison=val))
            v,code=validate_bundle(self.path);self.assertEqual(code,2)
            r=analyze_bundle(self.path);self.assertEqual(r.exit_code,2);self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated')
    def test_malformed_one_condition_retains_unaffected_comparison(self):
        def damage(o,s,m):
            for r in s:
                if r['record_id']=='study-P01-B':
                    r['payload']['extensions']['study_binding']['controls']['temperature']={}
        self.edit(damage)
        r=analyze_bundle(self.path)
        self.assertEqual(r.exit_code,2)
        self.assertEqual(content(r)['predictions']['P5_comparators'][0]['outcome'],'supporting')
        self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated')
    def test_unknown_text_method_preserves_P5(self):
        self.edit(lambda o,s,m:m['analysis_config']['extensions']['comparison']['text_method'].update(unicode_category_version=tagged(state='unknown')))
        r=analyze_bundle(self.path);self.assertEqual(r.exit_code,0);self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated');self.assertEqual(content(r)['predictions']['P5']['outcome'],'supporting')
    def test_explicit_resource_failure_never_silently_samples_pairs(self):
        self.edit(lambda o,s,m:m['analysis_config']['extensions']['comparison']['limits'].update(max_pairs=1))
        r=analyze_bundle(self.path);self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated');self.assertEqual(content(r)['predictions']['P5']['outcome'],'supporting')
        self.assertTrue(any(d['work']['limit_exceeded'] if 'limit_exceeded' in d['work'] else d['status']!='available' for d in content(r,7)['diagnostics']))
    def add_replay(self,body):
        (self.path.parent/'prior.json').write_bytes(body)
        self.edit(lambda o,s,m:(o.append(artifact_record('prior','prior.json')),m['analysis_config']['extensions']['comparison']['resampling'].update(replay_ref=tagged(record_ref('artifact','prior')))))
    def test_generated_run_manifest_replays_without_rng_calls(self):
        a=base_result();self.add_replay(a.manifest_json)
        with patch('structdet_bench.uncertainty.make_replay',side_effect=AssertionError('must use stored indices')):
            r=analyze_bundle(self.path)
        self.assertEqual(content(r)['predictions'],content(a)['predictions'])
        self.assertEqual(r.manifest['comparison_replay'],a.manifest['comparison_replay'])
    def test_malformed_replay_is_input_error_and_no_fallback(self):
        self.add_replay(b'{"schema_version":"0.1","replays":"run command"}')
        _,code=validate_bundle(self.path);self.assertEqual(code,2)
        with patch('structdet_bench.uncertainty.make_replay',side_effect=AssertionError('fallback')):r=analyze_bundle(self.path)
        self.assertEqual(r.exit_code,2);self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated')
    def test_replay_hash_change_cannot_be_repaired(self):
        obj=plain(base_result().manifest);obj['comparison_replay']['replays'][0]['indices'][0][0]=0
        self.add_replay(json.dumps(obj).encode());r=analyze_bundle(self.path)
        self.assertEqual(r.exit_code,2);self.assertEqual(content(r)['predictions']['P5']['outcome'],'not_evaluated')
    def test_unavailable_replay_is_evidence_limit_not_input_success_claim(self):
        self.edit(lambda o,s,m:m['analysis_config']['extensions']['comparison']['resampling'].update(replay_ref=tagged(state='unknown')))
        r=analyze_bundle(self.path);self.assertEqual(r.exit_code,0);self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated')
    def test_wrong_full_manifest_profile_is_rejected(self):
        obj=plain(base_result().manifest);obj['report_profile']='wrong';self.add_replay(json.dumps(obj).encode())
        _,code=validate_bundle(self.path);self.assertEqual(code,2)
    def test_same_inputs_replay_bytes_and_time_metadata_separately(self):
        a=base_result();b=analyze_bundle(self.path,recorded_at=STAMP)
        self.assertEqual(a.report_json,b.report_json);self.assertEqual(a.report_markdown,b.report_markdown);self.assertEqual(a.manifest_json,b.manifest_json)
    def test_three_file_output_refuses_overwrite_and_retains_original(self):
        a=base_result();out=self.root/'out';write_analysis(a,out,bundle_path=self.path)
        before={p.name:p.read_bytes() for p in out.iterdir()}
        from structdet_bench.contracts import InputError
        with self.assertRaises(InputError):write_analysis(a,out,bundle_path=self.path)
        self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()});self.assertEqual(len(before),3)
    def test_runtime_never_imports_tests_or_contacts_sources(self):
        import ast
        module=ast.parse((ROOT/'structdet_bench/comparison_pipeline.py').read_text())
        self.assertFalse(any(isinstance(x,ast.ImportFrom) and (x.module or '').startswith('tests') for x in ast.walk(module)))
        with patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')),patch('os.system',side_effect=AssertionError('shell')):
            r=analyze_bundle(self.path)
        self.assertEqual(r.exit_code,0)


# Step 7: imported component contexts must identify the same held inputs.
class Step7SnapshotAudit(unittest.TestCase):
    def setUp(self):
        from tests.phase2_helpers import populated_comparison_fixture
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.p,self.o,self.s,self.m=populated_comparison_fixture(self.root)
        for row in self.o:
            if row['record_type']=='realization':row['output_content_hash']=tagged(state='unknown')
            if row['record_type']=='artifact' and row['record_id'].startswith('text-'):
                row['expected_sha256']=tagged(state='unknown')
        write_abc(self.root,self.o,self.s,self.m)
        self.b,self.c,self.d=self.context()
    def context(self):
        from structdet_bench.local_io import load_bundle
        from structdet_bench.populations import build_populations
        from structdet_bench.text_diagnostics import diagnose_cells,method_from_record,limits_from_record
        b=load_bundle(self.p);c=build_populations(b);cfg=b.manifest.data['analysis_config']['extensions']['comparison']
        d=diagnose_cells(b,c.cells,method_from_record(cfg['text_method']),limits=limits_from_record(cfg['limits']))
        return b,c,d
    def comparison(self,b=None,c=None,d=None):
        from structdet_bench.comparisons import compare_study
        return compare_study(self.b if b is None else b,self.c if c is None else c,self.d if d is None else d)
    def p1(self,result):
        return next(x for x in result.blocks if x.block_id=='P01' and x.question=='P1' and x.view=='classified_all')
    def rewrite(self):return write_abc(self.root,self.o,self.s,self.m)
    def test_same_context_keeps_exact_gains(self):
        from structdet_bench.text_diagnostics import text_input_fingerprint
        for d in self.d:self.assertEqual(d.input_context_sha256,text_input_fingerprint(self.b,d.source_cell,d.analysis_population))
        self.assertEqual(self.p1(self.comparison()).values['surface_gain'].exact_ratio,(8,19))
    def test_changed_bytes_reject_old_diagnostic_without_expected_hash(self):
        (self.root/'text-P01-B-s2.txt').write_bytes(b'a b c')
        b,c,d=self.context();stale=self.p1(self.comparison(b,c,self.d));fresh=self.p1(self.comparison(b,c,d))
        self.assertEqual(stale.values['surface_gain'].result_status,'unavailable')
        self.assertIn('text_input_snapshot_mismatch',stale.contrasts['surface_gain'].minuend.number.reasons)
        self.assertEqual(fresh.values['surface_gain'].exact_ratio,(198,475))
    def test_byte_change_does_not_remove_text_independent_P5(self):
        (self.root/'text-P01-B-s2.txt').write_bytes(b'a b c')
        b,c,_=self.context();result=self.comparison(b,c,self.d)
        p5=[x for x in result.blocks if x.block_id=='P01' and x.question=='P5' and x.view=='classified_valid']
        self.assertTrue(all(x.eligible_before_resampling for x in p5))
        self.assertTrue(all(x.values['p5_valid_distinct_k_delta'].value==1 for x in p5))
    def test_unrelated_artifact_does_not_invalidate_consumed_text_context(self):
        self.o.append(artifact_record('unused','unused.txt'));(self.root/'unused.txt').write_bytes(b'unused')
        self.rewrite();b,c,_=self.context()
        self.assertEqual(self.p1(self.comparison(b,c,self.d)).values['surface_gain'].exact_ratio,(8,19))
    def test_missing_then_available_text_requires_new_diagnostic(self):
        f=self.root/'text-P01-B-s2.txt';saved=f.read_bytes();f.unlink()
        b,c,d=self.context();f.write_bytes(saved);fresh_b,fresh_c,_=self.context()
        result=self.p1(self.comparison(fresh_b,fresh_c,d))
        self.assertEqual(result.values['surface_gain'].result_status,'unavailable')
        self.assertFalse(result.eligible_before_resampling)
    def test_duplicate_position_cannot_reuse_old_population(self):
        next(x for x in self.o if x['record_id']=='P01-B-s2')['within_group_index']=tagged(1)
        self.rewrite();b,_,_=self.context();r=self.p1(self.comparison(b,self.c,self.d))
        self.assertFalse(r.eligible_before_resampling)
        self.assertEqual(next(x.status for x in r.gates if x.name=='population_snapshot_binding'),'failed')
    def test_changed_attempt_outcome_cannot_reuse_old_inventory(self):
        next(x for x in self.o if x['record_id']=='call-P01-B-1')['attempt_status']='failed'
        self.rewrite();b,_,_=self.context();r=self.p1(self.comparison(b,self.c,self.d))
        self.assertEqual(next(x.status for x in r.gates if x.name=='population_snapshot_binding'),'failed')
    def test_changed_attempt_plan_cannot_reuse_old_inventory(self):
        next(x for x in self.o if x['record_id']=='call-P01-B-1')['planned_candidate_count']=tagged(4)
        self.rewrite();b,_,_=self.context();r=self.p1(self.comparison(b,self.c,self.d))
        self.assertFalse(r.eligible_before_resampling)
    def test_changed_completion_context_cannot_use_old_diagnostic(self):
        next(x for x in self.o if x['record_id']=='P01-B-s2')['completion_status']='truncated'
        self.rewrite();b,c,_=self.context();r=self.p1(self.comparison(b,c,self.d))
        self.assertEqual(r.values['surface_gain'].result_status,'unavailable')
    def test_unpinned_diagnostic_never_gets_an_inferred_binding(self):
        from dataclasses import replace
        ds=tuple(replace(d,input_context_sha256=None) for d in self.d)
        self.assertFalse(self.p1(self.comparison(d=ds)).eligible_before_resampling)
    def test_context_check_does_not_retokenize_or_reopen_files(self):
        with patch('structdet_bench.text_diagnostics.tokenize_text',side_effect=AssertionError('unexpected tokenization')),patch('builtins.open',side_effect=AssertionError('unexpected file read')),patch('socket.socket',side_effect=AssertionError('network')):
            r=self.comparison()
        self.assertEqual(self.p1(r).values['surface_gain'].exact_ratio,(8,19))
    def test_original_snapshot_still_replays_after_file_change(self):
        old=self.p1(self.comparison()).values
        (self.root/'text-P01-B-s2.txt').write_bytes(b'changed file after acquisition')
        self.assertEqual(self.p1(self.comparison()).values,old)


@functools.lru_cache(maxsize=6)
def audit_variant(name):
    with TemporaryDirectory() as t:
        p,_=materialize_abc(Path(t)/'input',name)
        return analyze_bundle(p,recorded_at=STAMP)


class Step7CorrectionAudit(unittest.TestCase):
    def test_membership_revision_propagates_through_P5_means_intervals_and_outcomes(self):
        old=base_result();new=audit_variant('ABC-CORRECTED')
        self.assertEqual(content(old)['predictions']['P5']['outcome'],'supporting')
        self.assertEqual(content(new)['predictions']['P5']['outcome'],'inconclusive')
        for outcome in content(new)['predictions']['P5_comparators']:
            direction=outcome['directions']['p5_valid_distinct_k_delta']
            self.assertEqual([ratio(direction[k]) for k in ('mean','lower','upper')],[0,0,0])
        self.assertEqual(content(old)['predictions']['P1'],content(new)['predictions']['P1'])
        self.assertEqual(new.manifest['comparison_replay'],old.manifest['comparison_replay'])
        self.assertNotEqual(old.report['input_fingerprint'],new.report['input_fingerprint'])
        self.assertEqual(sum(x['realization_count']['value'] for x in content(new,2)['inventory']),360)
    def test_text_revision_changes_P1_but_not_M_or_P5(self):
        old=base_result();new=audit_variant('ABC-TEXT-CHANGED')
        self.assertEqual(content(new)['predictions']['P1']['outcome'],'inconclusive')
        self.assertEqual(content(old,4),content(new,4))
        self.assertEqual(content(old)['predictions']['P5'],content(new)['predictions']['P5'])
        self.assertEqual(ratio(content(new)['predictions']['P1']['directions']['surface_gain']['mean']),0)
    def test_independence_revision_restricts_claim_without_changing_measured_directions(self):
        old=base_result();new=audit_variant('ABC-INDEPENDENCE-WITHDRAWN')
        self.assertEqual(content(old,4),content(new,4))
        self.assertEqual(content(new)['predictions']['P1']['outcome'],'not_evaluated')
        self.assertEqual(ratio(content(new)['predictions']['P1']['directions']['surface_gain']['mean']),F(8,19))
        self.assertEqual(sum(x['selected_realization_count']['value'] for x in content(new,2)['inventory']),360)
    def test_opposite_results_retain_same_six_blocks_and_comparison_order(self):
        old=base_result();new=audit_variant('ABC-CONTRARY')
        for r in (old,new):
            self.assertEqual(content(r)['predictions']['P1']['actual_blocks'],tuple(f'P{i:02}' for i in range(1,7)))
            self.assertEqual([x['condition_pair'] for x in content(r)['predictions']['P5_comparators']],['C-A','C-B'])
        self.assertEqual(content(new)['predictions']['P1']['outcome'],'contrary')
        self.assertEqual(ratio(content(new)['predictions']['P1']['directions']['surface_gain']['mean']),-F(8,19))
    def test_validity_revision_preserves_all_view_and_rebuilds_valid_pair_membership(self):
        with TemporaryDirectory() as t:
            p,_=materialize_abc(Path(t)/'input');o,s,m=fixture_rows(p)
            vid='P01-B-v2';next(x for x in o if x['record_id']==vid)['validity_status']='invalid'
            next(x for x in s if x['record_id']=='e-'+vid)['payload']['assertion']=tagged('invalid')
            r=analyze_bundle(write_abc(p.parent,o,s,m),recorded_at=STAMP)
            ds={(x['cell_id'],x['analysis_population']):x for x in content(r,7)['diagnostics']}
            all_d=ds['P01-B','classified_all'];valid_d=ds['P01-B','classified_valid']
            self.assertEqual((all_d['pair_count'],valid_d['pair_count']),(190,171))
            self.assertIn('P01-B-s2',all_d['eligible_sample_ids']);self.assertNotIn('P01-B-s2',valid_d['eligible_sample_ids'])
            self.assertEqual(content(r)['predictions']['P1']['outcome'],'supporting')
            self.assertEqual(ratio(content(r)['predictions']['P1_valid_sensitivity']['directions']['surface_gain']['mean']),F(8,19))
    def test_prior_reports_survive_revision_in_a_separate_output_directory(self):
        with TemporaryDirectory() as t:
            root=Path(t);p,_=materialize_abc(root/'input');old=base_result();write_analysis(old,root/'old',bundle_path=p)
            before={f.name:f.read_bytes() for f in (root/'old').iterdir()}
            q,_=materialize_abc(root/'changed','ABC-CORRECTED');new=analyze_bundle(q,recorded_at=STAMP)
            write_analysis(new,root/'new',bundle_path=q)
            self.assertEqual(before,{f.name:f.read_bytes() for f in (root/'old').iterdir()})
            self.assertNotEqual(before['report.json'],(root/'new/report.json').read_bytes())
    def test_missing_B_preserves_full_C_A_but_cannot_claim_full_P5(self):
        r=audit_variant('ABC-NO-B-CONTROL');p=content(r)['predictions']
        self.assertEqual(p['P1']['outcome'],'not_evaluated');self.assertEqual(p['P5']['outcome'],'not_evaluated')
        self.assertEqual(p['P5_comparators'][0]['outcome'],'supporting')
        self.assertEqual(len(p['P5_comparators'][0]['actual_blocks']),6)
