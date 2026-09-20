"""Independent complete-unit indices, fit failure, replay and evidence tests.

Mock evidence exercises record gates only. No new empirical generations exist.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import ast
import copy
from dataclasses import replace
from fractions import Fraction as F
import hashlib
import json
import random
import unittest
from unittest.mock import patch

from structdet_bench import half_life as h, longitudinal_uncertainty as u, longitudinal as lg
from structdet_bench.contracts import InputError, freeze
from structdet_bench.comparison_records import configuration_fingerprint
from tests.helpers import ROOT, support_record, artifact_record, tagged as K, record_ref as C
from tests.test_half_life import RecordFixture, COUNTS, GEOMETRIC, R, O, gate

IDS=('r1','r2'); STATES=('s0','s1','s2','s3')


def resample(curves=None,**kw):
    return u.resample_curves(curves or [GEOMETRIC,GEOMETRIC],[0,2,4,6],state_ids=STATES,
        unit_ids=kw.pop('unit_ids',IDS),unit=kw.pop('unit','probe_panel'),
        max_abs_log_residual=kw.pop('max_abs_log_residual','0.1'),context_sha256='a'*64,plan_sha256='b'*64,**kw)


def saved():return u.make_replay(IDS,unit='probe_panel',context_sha256='a'*64,plan_sha256='b'*64)
def validate(record,**kw):return u.validate_replay(record,IDS,unit='probe_panel',context_sha256='a'*64,plan_sha256='b'*64,**kw)
def plain(value):return u._plain(value)


class IndexTests(unittest.TestCase):
    def test_complete_2000_by_N_matrix_and_seed_identity(self):
        r=saved();self.assertEqual((r['replicates'],r['seed']),(2000,20260919));self.assertEqual(len(r['indices']),2000)
        self.assertTrue(all(len(row)==2 for row in r['indices']));self.assertNotEqual(r['method'],'paired_prompt_block_bootstrap_v1')
    def test_saved_first_rows_match_pinned_independent_fixture(self):
        expected=json.loads((ROOT/'tests/fixtures/half_life_oracles.json').read_text())['replay_first_rows']
        self.assertEqual([list(x) for x in saved()['indices'][:len(expected)]],expected)
    def test_private_rng_leaves_global_state_unchanged(self):
        random.seed(999);before=random.getstate();saved();self.assertEqual(before,random.getstate())
    def test_repeated_generation_is_byte_identical(self):self.assertEqual(saved(),saved())
    def test_replay_does_not_call_RNG(self):
        r=saved()
        with patch.object(u.random,'Random',side_effect=AssertionError('regenerated')):self.assertEqual(validate(r),r)
    def test_replay_does_not_require_current_python_version(self):
        r=plain(saved());r['rng']['python_version']='3.14.0';r['sha256']=u._hash({k:v for k,v in r.items() if k!='sha256'})
        self.assertEqual(validate(r)['rng']['python_version'],'3.14.0')
    def test_wrong_method_seed_replicates_and_bool_fail(self):
        for k,v in [('method','other'),('seed',20260917),('replicates',1999),('index_base',False)]:
            r=plain(saved());r[k]=v
            with self.assertRaises(InputError):validate(r)
    def test_missing_draw_is_not_regenerated(self):
        r=plain(saved());r['indices'].pop()
        with self.assertRaises(InputError):validate(r)
    def test_short_row_and_out_of_bounds_indices_rejected(self):
        for row in ([0],[0,2],[0,True],[0,-1],[0,0.0]):
            r=plain(saved());r['indices'][0]=row
            with self.assertRaises(InputError):validate(r)
    def test_changed_indices_without_digest_fail(self):
        r=plain(saved());r['indices'][0][0]=1-r['indices'][0][0]
        with self.assertRaises(InputError):validate(r)
    def test_changed_payload_digest_is_not_trusted(self):
        r=plain(saved());r['sha256']='0'*64
        with self.assertRaises(InputError):validate(r)
    def test_external_expected_digest_checked(self):
        r=saved();self.assertEqual(validate(r,expected_sha256=r['sha256']),r)
        with self.assertRaises(InputError):validate(r,expected_sha256='0'*64)
    def test_changed_context_or_unit_order_fail(self):
        for k,v in [('context_sha256','c'*64),('plan_sha256','d'*64),('unit_ids',['r2','r1']),('unit','lineage_root')]:
            r=plain(saved());r[k]=v
            with self.assertRaises(InputError):validate(r)
    def test_extra_fields_and_non_mapping_rejected(self):
        for r in (None,[],False,dict(plain(saved()),execute='do it')):
            with self.assertRaises(InputError):validate(r)
    def test_rng_metadata_not_an_unchecked_label(self):
        for k,v in [('algorithm','PCG64'),('api','choices'),('state_version',True),('python_version','any'),('implementation','unknown')]:
            r=plain(saved());r['rng'][k]=v
            with self.assertRaises(InputError):validate(r)
    def test_single_duplicate_and_huge_unit_sets_rejected(self):
        for ids in (['r'],['r','r'],[f'r{i}' for i in range(65)]):
            with self.assertRaises(InputError):u.make_replay(ids,unit='probe_panel',context_sha256='a'*64,plan_sha256='b'*64)
    def test_full_replay_is_immutable(self):
        with self.assertRaises(TypeError):saved()['seed']=0


class NumericalTests(unittest.TestCase):
    def test_equal_curves_produce_degenerate_interval(self):
        r=resample();self.assertEqual(r.status,'available');self.assertEqual(r.interval,(2,2));self.assertEqual(len(r.draws),2000)
        self.assertFalse(r.population_confidence_established)
    def test_whole_curve_moves_together(self):
        curves=[GEOMETRIC,[x/2 for x in GEOMETRIC]];r=resample(curves)
        for d in r.draws[:20]:
            expected=tuple(sum(curves[i][t] for i in d.selected_indices)/2 for t in range(4))
            self.assertEqual(d.curve,expected);self.assertEqual(d.fit.empirical.value,2)
    def test_heterogeneous_geometric_units_have_nondegenerate_interval(self):
        other=[F(1,2),F(1,8),F(1,32),F(1,128)];r=resample([GEOMETRIC,other],max_abs_log_residual='0.3')
        self.assertEqual(r.status,'available',r.reasons);self.assertEqual(r.interval,(1,2));self.assertNotIn(r.point_fit.empirical.value,(1,2))
    def test_flat_draws_are_retained_without_success_only_interval(self):
        r=resample([GEOMETRIC,[F(1,2)]*4],max_abs_log_residual='1')
        self.assertIsNone(r.interval);self.assertEqual(len(r.draws),2000);self.assertGreater(r.failure_counts.get('no_declining_fitted_slope',0),0)
        self.assertTrue(any(d.status=='available' for d in r.draws));self.assertFalse(r.filtered_success_interval_computed)
    def test_zero_draws_are_retained(self):
        r=resample([GEOMETRIC,[0]*4]);self.assertIsNone(r.interval);self.assertIn('zero_diversity_in_fit_window',r.failure_counts)
    def test_non_geometric_draws_are_retained(self):
        other=[F(1,2),F(1,2),F(1,2),F(1,16)];r=resample([GEOMETRIC,other],max_abs_log_residual='0.01')
        self.assertIn('non_geometric_registered_residual_exceeded',r.failure_counts);self.assertEqual(len(r.draws),2000)
    def test_growth_draws_are_not_negative_half_lives(self):
        r=resample([GEOMETRIC,list(reversed(GEOMETRIC))],max_abs_log_residual='1')
        self.assertIsNone(r.interval);self.assertTrue(all(d.fit.empirical.value is None or d.fit.empirical.value>0 for d in r.draws))
    def test_unknown_dependence_retains_descriptive_point_without_RNG(self):
        with patch.object(u.random,'Random',side_effect=AssertionError('must not sample')):
            r=resample(dependency_reasons=['unknown_grouping'])
        self.assertEqual(r.point_fit.empirical.value,2);self.assertEqual(r.draws,());self.assertIsNone(r.interval)
    def test_incomplete_common_grid_not_filled(self):
        r=resample([GEOMETRIC,[F(1,2),None,F(1,8),F(1,16)]]);self.assertIn('incomplete_common_unit_curve',r.reasons);self.assertEqual(r.draws,())
    def test_budget_refusal_does_not_reduce_2000_draw_count(self):
        r=resample(limits={'max_tail_summands':100});self.assertIn('sensitivity_recompute_work_limit',r.reasons);self.assertEqual(r.draws,())
    def test_limits_apply_to_unit_count(self):
        r=resample(limits={'max_panels_per_trajectory':1});self.assertIn('sensitivity_unit_work_limit',r.reasons)
    def test_exact_means_do_not_pool_different_counts(self):
        r=resample([[F(1,2),F(1,4),F(1,8),F(1,16)],[F(1,4),F(1,8),F(1,16),F(1,32)]])
        self.assertEqual(r.point_fit.diversities,(F(3,8),F(3,16),F(3,32),F(3,64)))
    def test_root_and_panel_units_have_distinct_scope_flags(self):
        p=resample();r=resample(unit='lineage_root')
        self.assertFalse(p.training_lineage_variability_estimated);self.assertTrue(r.training_lineage_variability_estimated)
        self.assertFalse(r.substantive_validation_performed)
    def test_numerical_replay_exactly_repeats_all_draws(self):
        first=resample()
        with patch.object(u.random,'Random',side_effect=AssertionError('regeneration')):second=resample(replay=first.replay)
        self.assertEqual(first.draws,second.draws);self.assertEqual(first.interval,second.interval)
    def test_small_matrix_percentile_oracle(self):
        self.assertAlmostEqual(u.percentile([1,3,5,9],F(1,40)),1.15)
        self.assertAlmostEqual(u.percentile([1,3,5,9],F(39,40)),8.7)
    def test_percentile_never_drops_nan_or_none(self):
        for xs in ([1,None],[1,float('nan')],[1,float('inf')],[True,2]):
            with self.assertRaises(InputError):u.percentile(xs,F(1,2))
    def test_2000_quantile_indices_use_B_minus_one(self):
        values=list(range(2000));self.assertAlmostEqual(u.percentile(values,F(1,40)),49.975);self.assertAlmostEqual(u.percentile(values,F(39,40)),1949.025)
    def test_invalid_curve_dimensions_or_numeric_units_fail(self):
        for cs in ([GEOMETRIC],[[F(1,2)],GEOMETRIC],[[True]*4,GEOMETRIC],[[2]*4,GEOMETRIC]):
            with self.assertRaises(InputError):resample(cs)
    def test_local_endpoint_sensitivity_supported_separately(self):
        r=resample(fit_mode='local');self.assertEqual(r.interval,(2,2));self.assertTrue(all(d.fit.empirical.status=='not_requested' for d in r.draws))
    def test_every_required_draw_failure_is_counted(self):
        r=resample(max_abs_log_residual=None);self.assertEqual(len(r.draws),2000);self.assertTrue(all(d.status!='available' for d in r.draws));self.assertIsNone(r.interval)


class SensitivityFixture(RecordFixture):
    def setUp(self):
        super().setUp();self.build([COUNTS,COUNTS])
    def split_roots(self):
        self.build([COUNTS+COUNTS])
        t=self.cfg['trajectories'][0];other=copy.deepcopy(t)
        t.update(state_refs=t['state_refs'][:4],transition_refs=t['transition_refs'][:3],round_coordinates=[K(i) for i in range(4)],schedule=t['schedule'][:4])
        other.update(R('trajectory','path2'),state_refs=other['state_refs'][4:],transition_refs=other['transition_refs'][4:],round_coordinates=[K(i) for i in range(4)],schedule=other['schedule'][4:],root_ref=R('root','R2'))
        for i,slot in enumerate(other['schedule']):slot['recursive_round_index']=K(i)
        self.cfg['trajectories'].append(other)
        self.cfg['states'][4]['ancestor_refs']=K([]);self.cfg['transitions']=[x for x in self.cfg['transitions'] if x['object_id']!='T4']
        root=copy.deepcopy(self.cfg['roots'][0]);root.update(R('root','R2'),dependency_group=K('root2'));self.cfg['roots'].append(root)
        req=self.cfg['observed_requests'][0];req['state_refs']=req['state_refs'][:4]
        self.req['end_ref']=R('state','S3');self.seal()
    def add_plan(self,unit='probe_panel'):
        self.req['sensitivity_ref']=K(R('replay','sens-plan'));self.seal()
        self.plan={'schema_version':'0.1','plan_id':'fixture-sensitivity','plan_version':'0.1','method':u.METHOD,
            'request_ref':R('shl_request','fit'),'request_sha256':configuration_fingerprint(self.req),'unit':unit,
            'trajectory_refs':[R('trajectory','path')] if unit=='probe_panel' else [R('trajectory','path'),R('trajectory','path2')],
            'panel_refs':self.req['panel_refs'],'replicates':2000,'seed':20260919,
            'registration_ref':C('preregistration','fit-reg'),'dependence_ref':C('independence_assessment','sampling-assessment')}
        self.obs.append(artifact_record('sensitivity-plan-artifact','sensitivity-plan.json'))
        self.cfg['replays']=[O('replay','sens-plan',artifact_ref=C('artifact','sensitivity-plan-artifact'),expected_sha256='0'*64,
            method_id=u.METHOD,plan_sha256=gate.PLAN_SHA256,unit_refs=self.plan['trajectory_refs'])]
        self.sup.append(support_record('independence_assessment','sampling-assessment',left_ref=C('frame','frame1'),right_ref=C('protocol','protocol1'),
            dimension='conditional_sampling',outcome='supported_for_scope',criterion=K('Explicit stipulated conditional sampling model.'),reviewer_refs=[C('role','reviewer')],extensions={}))
        self.plan_seal()
    def plan_seal(self):
        data=(json.dumps(self.plan,sort_keys=True,indent=2)+'\n').encode();(self.root/'sensitivity-plan.json').write_bytes(data)
        self.cfg['replays'][0]['expected_sha256']=hashlib.sha256(data).hexdigest()
        sha=configuration_fingerprint(self.plan)
        self.support('fit-reg')['payload']['extensions'][u.EVIDENCE_KEY]={'plan_sha256':sha,'inspection_status':'registered_before_inspection'}
        ids=[x['object_id'] for x in self.plan['panel_refs']] if self.plan['unit']=='probe_panel' else ['R1','R2']
        groups=ids if self.plan['unit']=='probe_panel' else ['shared-root1','root2']
        self.support('sampling-assessment')['payload']['extensions'][u.EVIDENCE_KEY]={'plan_sha256':sha,'unit':self.plan['unit'],'unit_ids':ids,
            'dependency_groups':groups,'conditional_independence':True,'conditioning':'Fixed initial checkpoint and reference, separately sampled mock units.'}
    def sensitivity(self,**kw):return u.evaluate_longitudinal_sensitivity(self.bundle(),**kw).results[0]


class IntegrationTests(SensitivityFixture):
    def test_full_passive_record_to_panel_sensitivity(self):
        self.add_plan();r=self.sensitivity();self.assertEqual(r.status,'available',r.reasons);self.assertEqual(len(r.draws),2000)
        self.assertEqual(r.dependency_status,'fixture_stipulated');self.assertFalse(r.training_lineage_variability_estimated)
    def test_explicit_none_is_not_requested(self):
        r=self.sensitivity();self.assertEqual(r.status,'not_requested');self.assertEqual(r.point_fit.empirical.status,'available')
    def test_unknown_request_does_not_guess_resampling(self):
        self.req['sensitivity_ref']=K(state='unknown');self.seal();self.assertIn('sensitivity_request_unresolved',self.sensitivity().reasons)
    def test_missing_plan_artifact_is_unavailable(self):
        self.add_plan();(self.root/'sensitivity-plan.json').unlink();r=self.sensitivity();self.assertEqual(r.status,'unavailable');self.assertEqual(r.draws,())
    def test_bad_raw_plan_digest_is_rejected(self):
        self.add_plan();self.cfg['replays'][0]['expected_sha256']='0'*64;self.assertEqual(self.sensitivity().status,'unavailable')
    def test_changed_resampling_seed_cannot_refresh_as_new_method(self):
        self.add_plan();self.plan['seed']=20260917;self.plan_seal();self.assertIn('sensitivity_plan_seed_or_count',self.sensitivity().reasons)
    def test_unknown_unit_not_resolved_by_name(self):
        self.add_plan();self.plan['unit']='candidate';self.plan_seal();self.assertEqual(self.sensitivity().status,'unavailable')
    def test_less_than_two_panels_does_not_invent_units(self):
        self.build([COUNTS]);self.add_plan();self.assertIn('at_least_two_bounded_units_required',self.sensitivity().reasons)
    def test_missing_sampling_assessment_withholds_interval_not_point(self):
        self.add_plan();self.support('sampling-assessment')['payload']['outcome']='unresolved';r=self.sensitivity()
        self.assertIsNone(r.interval);self.assertEqual(r.point_fit.empirical.status,'available');self.assertEqual(r.draws,())
    def test_sampling_assessment_binds_exact_plan(self):
        self.add_plan();self.support('sampling-assessment')['payload']['extensions'][u.EVIDENCE_KEY]['plan_sha256']='0'*64
        self.assertIn('sensitivity_dependency_assessment_mismatch',self.sensitivity().reasons)
    def test_no_implicit_conditioning_model(self):
        self.add_plan();self.support('sampling-assessment')['payload']['extensions'][u.EVIDENCE_KEY]['conditioning']=''
        self.assertIn('sensitivity_conditioning_missing',self.sensitivity().reasons)
    def test_unregistered_plan_never_generates_indices(self):
        self.add_plan();self.support('fit-reg')['payload']['extensions'].pop(u.EVIDENCE_KEY)
        with patch.object(u.random,'Random',side_effect=AssertionError('unregistered sampling')):r=self.sensitivity()
        self.assertIn('sensitivity_registration_not_bound',r.reasons)
    def test_two_root_trajectories_preserve_fixed_initial_checkpoint(self):
        self.split_roots();self.add_plan('lineage_root');r=self.sensitivity();self.assertEqual(r.status,'available',r.reasons)
        self.assertEqual(r.unit_ids,('R1','R2'));self.assertTrue(r.training_lineage_variability_estimated);self.assertFalse(r.population_confidence_established)
    def test_duplicate_dependent_root_is_not_replication(self):
        self.split_roots();self.cfg['roots'][1]['dependency_group']=K('shared-root1');self.add_plan('lineage_root')
        self.assertIn('multiple_paths_per_dependent_root',self.sensitivity().reasons)
    def test_known_shared_stochastic_ancestry_blocks_root_interval(self):
        self.split_roots();self.cfg['roots'][1]['ancestor_refs']=K([R('root','R1')]);self.add_plan('lineage_root')
        self.assertIn('shared_root_ancestry',self.sensitivity().reasons)
    def test_intervention_on_second_root_blocks_unchanged_regime(self):
        self.split_roots();self.add_plan('lineage_root')
        self.cfg['interventions'].append(O('intervention','second-root-treatment',pre_state_ref=R('state','S5'),post_state_ref=R('state','S6'),intervention_kind='training',parameters_changed=K(False),direct_answer_injection=K(False),external_refs=[]))
        r=self.sensitivity();self.assertEqual(r.status,'unavailable');self.assertIn('intervention_inside_unchanged_regime',r.reasons)
    def test_conditioned_view_survives_into_all_resampled_fits(self):
        self.build([COUNTS,COUNTS],view='classified_valid');self.add_plan();r=self.sensitivity()
        self.assertIn('validity_conditioned',r.point_fit.empirical.qualifiers)
        self.assertTrue(all('validity_conditioned' in d.fit.empirical.qualifiers for d in r.draws))
    def test_unknown_root_group_cannot_be_guessed(self):
        self.split_roots();self.cfg['roots'][1]['dependency_group']=K(state='unknown');self.add_plan('lineage_root')
        self.assertEqual(self.sensitivity().status,'unavailable')
    def test_root_grid_mismatch_not_interpolated(self):
        self.split_roots();self.cfg['trajectories'][1]['round_coordinates']=[K(i+1) for i in range(4)];self.add_plan('lineage_root')
        self.assertEqual(self.sensitivity().status,'unavailable')
    def test_saved_replay_reproduces_full_record_driven_result(self):
        self.add_plan();first=self.sensitivity()
        self.assertIsNotNone(first.replay,first.reasons)
        with patch.object(u.random,'Random',side_effect=AssertionError('regenerated')):second=self.sensitivity(replays={'fit':plain(first.replay)})
        self.assertEqual(first.draws,second.draws);self.assertEqual(first.interval,second.interval)
    def test_explicit_missing_replay_never_regenerates(self):
        self.add_plan()
        with patch.object(u.random,'Random',side_effect=AssertionError('regenerated')):r=self.sensitivity(replays={})
        self.assertIn('explicit_replay_missing_for_request',r.reasons)
    def test_unknown_replay_request_id_rejected(self):
        with self.assertRaises(InputError):self.sensitivity(replays={'not-a-request':{}})
    def test_modified_bundle_rejects_saved_context(self):
        self.add_plan();first=self.sensitivity();self.support('sampling-assessment')['payload']['criterion']=K('Revised premise')
        second=self.sensitivity(replays={'fit':first.replay});self.assertIn('longitudinal_replay_method_or_context',second.reasons)
    def test_supplied_changed_half_life_component_rejected(self):
        b=self.bundle();r=h.fit_half_lives(b)
        with self.assertRaises(InputError):u.evaluate_longitudinal_sensitivity(b,half_lives=replace(r,status='other'))
    def test_malformed_longitudinal_does_not_disappear(self):
        self.man['analysis_config']['extensions']['longitudinal']=None
        r=u.evaluate_longitudinal_sensitivity(self.bundle());self.assertEqual(r.status,'contract_error');self.assertTrue(r.requested)
    def test_everything_after_load_is_passive(self):
        self.add_plan();b=self.bundle()
        with patch('builtins.open',side_effect=AssertionError('file')),patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):
            r=u.evaluate_longitudinal_sensitivity(b)
        self.assertEqual(r.results[0].status,'available',r.results[0].reasons)
    def test_wrong_replay_plan_object_units_fail(self):
        self.add_plan();self.cfg['replays'][0]['unit_refs']=[R('root','R1')]
        self.assertIn('sensitivity_replay_unit_binding',self.sensitivity().reasons)
    def test_no_drop_of_incomplete_panel(self):
        self.add_plan();self.missing(1);self.plan['request_sha256']=configuration_fingerprint(self.req);self.plan_seal()
        r=self.sensitivity();self.assertEqual(r.status,'unavailable');self.assertEqual(r.draws,())
    def test_no_model_or_source_independence_certificate(self):
        self.add_plan();r=self.sensitivity();self.assertFalse(r.substantive_validation_performed);self.assertEqual(r.interval_scope,'resampling_sensitivity')


class MatrixTests(unittest.TestCase):
    def test_stage_binds_all_current_methods_without_touching_old_matrix(self):
        m=gate.load_matrix();self.assertEqual(gate.validate_matrix(m),[])
        tree=ast.parse((ROOT/'tests/test_longitudinal_uncertainty.py').read_text())
        ids={f'tests.test_longitudinal_uncertainty.{c.name}.{f.name}' for c in tree.body if isinstance(c,ast.ClassDef) for f in c.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_')}
        self.assertTrue(ids<=set(m['stage_bindings']['5']['test_bindings']))
    def test_only_L17_through_L22_are_newly_closed_at_step5(self):
        m=gate.load_matrix()
        if m['delivery']['step']==5:
            self.assertEqual({r['id'] for r in m['longitudinal'] if r['implementation_status']=='implemented'},{f'P3-L{i:02}' for i in range(1,23)})
    def test_scientific_sources_and_predecessor_identities_unchanged(self):
        self.assertTrue(all(r['status']=='passed' for r in gate.current_identity_checks()))
