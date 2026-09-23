"""Step 5 arithmetic, applicability and real passive-record integration tests.

All inputs are stipulated fixtures. Decimal count/log identities independently
supply the oracle; none of these tests runs a model or validates a real lineage.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import ast
import copy
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import half_life as h, longitudinal as lg, longitudinal_records as lr
from structdet_bench.contracts import InputError, freeze
from structdet_bench.local_io import load_bundle
from structdet_bench.comparison_records import configuration_fingerprint
from tests.helpers import ROOT, support_record, rewrite_evidence_bundle, tagged as K, record_ref as C
from tests.test_longitudinal import materialize_observed, A, B, R, O
from tests import phase3_helpers as gate

GEOMETRIC=[F(1,2),F(1,4),F(1,8),F(1,16)]
COUNTS=[[A]*16+[B]*16,[A]*27+[B]*5,[A]*30+[B]*2,[A]*31+[B]]


def curve(values=GEOMETRIC, times=None, **kw):
    return h.analyze_curve(times or list(range(len(values))),values,state_ids=[f's{i}' for i in range(len(values))],
        max_abs_log_residual=kw.pop('max_abs_log_residual','0.1'),**kw)


class ArithmeticTests(unittest.TestCase):
    def test_plan_geometric_irregular_round_oracle(self):
        r=curve(times=[0,2,4,6]);self.assertEqual(r.empirical.value,2);self.assertEqual(r.interval.value,2)
        self.assertEqual(r.x,(0,2,4,6));self.assertEqual(r.max_abs_log_residual,0)
    def test_local_decline_uses_actual_elapsed_rounds(self):
        r=curve([F(1,2),F(1,4)],[4,10],fit_mode='local')
        self.assertEqual(r.interval.value,6);self.assertEqual(r.empirical.status,'not_requested')
    def test_four_registered_measured_states_required(self):
        r=curve(GEOMETRIC[:3]);self.assertIn('at_least_four_registered_measurements_required',r.empirical.reasons)
        self.assertEqual(r.interval.value,1)
    def test_flat_interval_is_undefined_not_infinity(self):
        r=curve([F(1,2)]*4);self.assertEqual(r.interval.status,'undefined');self.assertIsNone(r.interval.value)
        self.assertIn('no_decay_on_interval',r.interval.reasons);self.assertEqual(r.slope,0)
    def test_growth_retained_without_negative_half_life(self):
        r=curve(list(reversed(GEOMETRIC)));self.assertIn('growth_on_interval',r.interval.reasons)
        self.assertGreater(r.slope,0);self.assertIsNone(r.empirical.value)
    def test_zero_anchor_is_not_pseudocounted(self):
        r=curve([0,F(1,4),F(1,8),F(1,16)]);self.assertIn('zero_starting_diversity',r.interval.reasons)
        self.assertIn('zero_diversity_in_fit_window',r.empirical.reasons)
    def test_zero_endpoint_retains_bracket_without_zero_half_life(self):
        r=curve([F(1,2),F(1,4),F(1,8),0]);self.assertIn('zero_ending_diversity',r.interval.reasons)
        self.assertEqual(r.first_zero.left_id,'s2');self.assertEqual(r.first_zero.right_id,'s3');self.assertIsNone(r.interval.value)
    def test_half_crossing_records_observed_bracket_only(self):
        r=curve([F(1,2),F(2,5),F(1,5),F(1,10)],[0,2,5,10]);b=r.half_crossing
        self.assertEqual((b.left_time,b.right_time),(2,5));self.assertFalse(b.exact_crossing_time_estimated)
    def test_no_observed_crossing_never_invents_later_time(self):
        r=curve([F(1,2),F(49,100),F(48,100),F(47,100)]);self.assertEqual(r.half_crossing.status,'not_observed')
    def test_missing_inner_observation_blocks_fit_not_endpoint_summary(self):
        r=curve([F(1,2),None,F(1,8),F(1,16)]);self.assertIn('missing_expected_measurement',r.empirical.reasons)
        self.assertEqual(r.interval.value,1);self.assertEqual(r.half_crossing.intervening_ids,('s1',))
    def test_intentionally_unsampled_round_remains_in_clock(self):
        r=curve([F(1,2),None,F(1,4),F(1,8),F(1,16)],[0,1,2,4,6],slot_statuses=['available','intentionally_unsampled','available','available','available'])
        self.assertEqual(r.empirical.value,2);self.assertEqual(r.measured_indices,(0,2,3,4));self.assertEqual(r.times,(0,1,2,4,6))
    def test_missing_endpoint_unavailable_not_empty(self):
        r=curve([F(1,2),F(1,4),F(1,8),None]);self.assertEqual(r.interval.status,'unavailable');self.assertIsNone(r.interval.value)
    def test_unknown_round_never_filled_from_position(self):
        r=curve(times=[0,1,None,3]);self.assertIn('recursive_coordinate_unknown',r.interval.reasons)
    def test_reversed_clock_rejected(self):
        self.assertIn('recursive_clock_reversed',curve(times=[0,2,1,3]).interval.reasons)
    def test_equal_measured_times_block_anchored_fit(self):
        r=curve(times=[0,1,1,3]);self.assertIn('distinct_measured_rounds_required',r.empirical.reasons)
    def test_zero_distance_has_no_recursive_rate(self):
        self.assertIn('nonpositive_recursive_distance',curve([F(1,2),F(1,4)],[1,1]).interval.reasons)
    def test_positive_criterion_required_no_default(self):
        for criterion in (None,0,'0','bad',True,0.1):
            r=curve(max_abs_log_residual=criterion);self.assertEqual(r.empirical.status,'unavailable',criterion);self.assertEqual(r.interval.value,1)
    def test_non_geometric_curve_preserves_endpoint_summary(self):
        r=curve([F(1,2),F(1,2),F(1,2),F(1,16)],max_abs_log_residual='0.01')
        self.assertIn('non_geometric_registered_residual_exceeded',r.empirical.reasons);self.assertEqual(r.interval.value,1)
    def test_small_local_growth_can_pass_registered_residual(self):
        r=curve([F(1,2),F(1,4),F(26,100),F(1,8)],max_abs_log_residual='0.35')
        self.assertEqual(r.empirical.status,'available');self.assertGreater(r.diversities[2],r.diversities[1])
    def test_missing_regime_criterion_retains_slope_and_residuals(self):
        r=curve(max_abs_log_residual=None);self.assertIsNotNone(r.slope);self.assertEqual(len(r.log_residuals),4);self.assertIsNone(r.empirical.value)
    def test_residual_equality_is_exact_without_tolerance(self):
        values=[F(1,2),F(3,10),F(1,8),F(1,16)];r=curve(values)
        boundary=F.from_float(r.max_abs_log_residual)
        self.assertEqual(curve(values,max_abs_log_residual=boundary).empirical.status,'available')
        self.assertEqual(curve(values,max_abs_log_residual=boundary-F(1,10**30)).empirical.status,'unavailable')
    def test_anchor_remains_fixed_not_fitted_intercept(self):
        r=curve([F(3,5),F(1,4),F(1,8),F(1,16)],max_abs_log_residual='1')
        self.assertEqual(r.fitted_values[0],float(F(3,5)));self.assertEqual(r.log_residuals[0],0)
    def test_time_shift_changes_no_rate(self):
        self.assertEqual(curve(times=[0,2,4,6]).empirical.value,curve(times=[100,102,104,106]).empirical.value)
    def test_scale_of_diversity_changes_no_rate(self):
        self.assertEqual(curve().empirical.value,curve([x/4 for x in GEOMETRIC]).empirical.value)
    def test_endpoints_do_not_assume_geometric_interior(self):
        a=curve();b=curve([F(1,2),F(2,5),F(2,5),F(1,16)],max_abs_log_residual='0.01')
        self.assertEqual(a.interval.value,b.interval.value);self.assertNotEqual(a.empirical.status,b.empirical.status)
    def test_nonfinite_math_never_becomes_scientific_zero(self):
        with patch.object(h.math,'log1p',return_value=float('nan')):r=curve()
        self.assertEqual(r.empirical.status,'unavailable');self.assertIsNone(r.empirical.value)
    def test_exp_underflow_is_explicit(self):
        with patch.object(h.math,'exp',return_value=0.0):r=curve()
        self.assertIn('fitted_diversity_numeric_range',r.empirical.reasons)
    def test_tiny_exact_decline_is_not_flattened(self):
        d=10**100;r=curve([F(1,2),F(d-1,2*d)],[0,1],fit_mode='local')
        self.assertEqual(r.interval.status,'available');self.assertGreater(r.interval.value,10**90)
    def test_unrepresentable_log_difference_withheld(self):
        d=10**400;r=curve([F(1,2),F(d-1,2*d)],[0,1],fit_mode='local')
        self.assertEqual(r.interval.status,'unavailable');self.assertNotIn('no_decay_on_interval',r.interval.reasons)
    def test_very_small_positive_diversity_not_zero(self):
        r=curve([F(1,2**1100),F(1,2**1101)],[0,1],fit_mode='local');self.assertEqual(r.interval.value,1)
    def test_exact_resource_limit_no_floating_fallback(self):
        with self.assertRaises(InputError):curve([F(1,2**100),F(1,2**101)],[0,1],limits={'max_exact_bits':32})
    def test_large_coordinate_squares_are_guarded(self):
        r=curve(times=[0,2**60,2**61,2**62],limits={'max_exact_bits':64});self.assertEqual(r.empirical.status,'unavailable')
    def test_missing_process_blocks_rate_but_preserves_values(self):
        r=curve(endpoint_reasons=['undocumented_process']);self.assertEqual(r.diversities,tuple(GEOMETRIC));self.assertIn('undocumented_process',r.empirical.reasons)
    def test_regime_veto_does_not_erase_interval(self):
        r=curve(regime_reasons=['intervention']);self.assertEqual(r.interval.value,1);self.assertIn('intervention',r.empirical.reasons)
    def test_source_oracle_file_independently_rederived(self):
        data=json.loads((ROOT/'tests/fixtures/half_life_oracles.json').read_text())
        self.assertEqual(data['plan_sha256'],gate.PLAN_SHA256)
        for case in data['cases']:
            vals=[F(*x) for x in case['values']];r=curve(vals,case['times'],max_abs_log_residual=case['criterion'])
            with localcontext() as ctx:
                ctx.prec=90;t=case['times'];d=[Decimal(x.numerator)/Decimal(x.denominator) for x in vals]
                logs=[x.ln()-d[0].ln() for x in d];xs=[Decimal(x-t[0]) for x in t]
                beta=sum(x*y for x,y in zip(xs,logs))/sum(x*x for x in xs)
                expected=-Decimal(2).ln()/beta
                self.assertLess(abs(expected-Decimal(case['empirical'])),Decimal('1e-75'))
                self.assertAlmostEqual(r.slope,float(beta),places=12)
                if r.empirical.value is not None:self.assertAlmostEqual(r.empirical.value,float(expected),places=11)
    def test_null_comparison_is_explicit_and_noncausal(self):
        from structdet_bench.categorical_null import categorical_null
        assumptions={k:K(True) for k in ('finite_multinomial','fixed_classes','closed','empirical_reconstruction','exogenous_schedule')}
        null=categorical_null(['a','b'],['0.5','0.5'],scenario_id='N',n=2,steps=2,assumptions=assumptions)
        r=h.compare_null(curve(),null);self.assertEqual(r.null.value,1);self.assertFalse(r.validated_rate_comparison);self.assertFalse(r.causal_acceleration_established)
    def test_invalid_dimensions_and_ids_fail_closed(self):
        for kw in ({'times':[0],'diversities':[1],'state_ids':['s']},{'times':[0,1],'diversities':[1,1],'state_ids':['s','s']},
                   {'times':[0,True],'diversities':[1,1],'state_ids':['a','b']}):
            with self.assertRaises(InputError):h.analyze_curve(**kw)
    def test_out_of_range_diversity_and_floats_rejected(self):
        for x in (True,-1,F(3,2),0.5,'NaN'):
            with self.assertRaises((InputError,ValueError)):curve([x,F(1,4)])
    def test_unsampled_label_cannot_hide_supplied_value(self):
        with self.assertRaises(InputError):curve(slot_statuses=['available','intentionally_unsampled','available','available'])
    def test_input_lists_are_not_mutated_or_retained_mutably(self):
        x=list(GEOMETRIC);r=curve(x);x[0]=F(1);self.assertEqual(r.diversities[0],F(1,2))


class RecordFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.build()
    def build(self,panels=None,view='classified_all',validity=None):
        self.obs,self.sup,self.man=materialize_observed(self.root,panels or [COUNTS],view=view,validity=validity)
        self.cfg=self.man['analysis_config']['extensions']['longitudinal'];self.cfg['capabilities'].append('half_life')
        n=len((panels or [COUNTS])[0]);self.req=O('shl_request','fit',trajectory_ref=R('trajectory','path'),start_ref=R('state','S0'),anchor_ref=R('state','S0'),end_ref=R('state',f'S{n-1}'),
            view=view,fit_mode='anchored',residual_criterion=K('0.15'),panel_refs=[R('panel',f'P{i}') for i in range(len(panels or [COUNTS]))],sensitivity_ref=K(None),registration_ref=K(C('preregistration','fit-reg')))
        self.cfg['shl_requests']=[self.req]
        self.sup.append(support_record('preregistration','fit-reg',registration_id='fit-design',registered_at=K('2026-01-01T00:00:00+00:00'),material_refs=[],extensions={}))
        self.seal()
    def seal(self):
        witness=h.registration_witness(self.req,self.cfg['trajectories'][0])
        witness.update(residual_rationale='Prespecified fixture log-error bound; no fit-window search.',inspection_status='registered_before_inspection')
        self.support('fit-reg')['payload']['extensions'][h.REGISTRATION_KEY]=witness
    def support(self,id):return next(r for r in self.sup if r['record_id']==id)
    def bundle(self):return load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.sup,self.man))
    def result(self):return h.fit_half_lives(self.bundle()).results[0]
    def missing(self,i,status='missing'):
        for slot in self.cfg['trajectories'][0]['schedule']:
            if slot['state_ref']==R('state',f'S{i}'):slot.update(observation_status=status,measurement_ref=K(None))
        self.seal()


class IntegrationTests(RecordFixture):
    def test_real_loaded_records_reach_registered_fit(self):
        r=self.result();self.assertEqual(r.status,'available',r.reasons);self.assertEqual(r.fit.diversities[0],F(1,2))
        self.assertEqual(r.prepared.panel_refs,(lr.ObjectRef('panel','P0','0.1'),));self.assertFalse(r.fit.substantive_validation_performed)
    def test_no_requests_is_not_requested(self):
        self.cfg['shl_requests']=[];r=h.fit_half_lives(self.bundle());self.assertFalse(r.requested);self.assertEqual(r.status,'not_requested')
    def test_unsupported_bundle_type_rejected(self):
        with self.assertRaises(InputError):h.fit_half_lives({})
    def test_missing_request_identity_is_retained(self):
        del self.req['object_id'];r=h.fit_half_lives(self.bundle());self.assertEqual(len(r.results),1);self.assertEqual(r.results[0].status,'unavailable')
    def test_malformed_extension_is_not_successful_absence(self):
        self.man['analysis_config']['extensions']['longitudinal']=None;r=h.fit_half_lives(self.bundle());self.assertEqual(r.status,'contract_error')
    def test_registration_digest_detects_changed_criterion(self):
        self.req['residual_criterion']=K('0.2');r=self.result();self.assertIn('fit_registration_binding_mismatch',r.fit.empirical.reasons)
    def test_registration_after_observation_is_limited(self):
        self.support('fit-reg')['payload']['registered_at']=K('2030-01-01T00:00:00+00:00');self.assertIn('registration_after_observation',self.result().reasons)
    def test_unverified_registration_marks_retained_interval_as_exploratory(self):
        self.support('fit-reg')['payload']['registered_at']=K('2030-01-01T00:00:00+00:00')
        r=self.result();self.assertIn('registration_unverified_endpoint_description',r.fit.interval.qualifiers)
    def test_missing_rationale_blocks_qualified_global_fit(self):
        self.support('fit-reg')['payload']['extensions'][h.REGISTRATION_KEY]['residual_rationale']=''
        self.assertIn('fit_residual_rationale_missing',self.result().reasons)
    def test_exploratory_window_cannot_replace_registered_window(self):
        self.req['start_ref']=self.req['anchor_ref']=R('state','S1');r=self.result();self.assertEqual(r.status,'unavailable')
        self.assertIn('fit_registration_binding_mismatch',r.fit.empirical.reasons)
    def test_changing_anchor_without_start_is_rejected(self):
        self.req['anchor_ref']=R('state','S1');self.assertEqual(self.result().status,'unavailable')
    def test_full_panel_set_is_fixed_not_pooled(self):
        self.build([COUNTS,COUNTS]);r=self.result();self.assertEqual(r.fit.diversities[0],F(1,2));self.assertEqual(len(r.prepared.panel_values),2)
    def test_missing_panel_never_means_surviving_panel_average(self):
        self.build([COUNTS,COUNTS]);slot=self.cfg['trajectories'][0]['schedule'][2];slot.update(observation_status='missing',measurement_ref=K(None));self.seal()
        r=self.result();self.assertEqual(r.status,'unavailable');self.assertIsNone(r.prepared.values[1])
    def test_duplicate_requested_panel_is_rejected(self):
        self.req['panel_refs']*=2;self.seal();self.assertIn('fit_fixed_panel_set_required',self.result().reasons)
    def test_unrequested_panel_not_inserted_to_repair_missing(self):
        self.req['panel_refs']=[R('panel','absent')];self.seal();self.assertEqual(self.result().status,'unavailable')
    def test_missing_interior_preserves_local_endpoint(self):
        self.missing(1);r=self.result();self.assertEqual(r.fit.interval.status,'available');self.assertEqual(r.fit.empirical.status,'unavailable')
    def test_documented_unsampled_with_four_measured_points(self):
        self.build([COUNTS[:1]+[COUNTS[0]]+COUNTS[1:]]);self.missing(1,'intentionally_unsampled')
        # Explicit uneven round coordinates remain part of the requested curve.
        self.req['residual_criterion']=K('0.5');self.seal();r=self.result()
        self.assertEqual(len(r.fit.measured_indices),4);self.assertEqual(r.fit.times,(0,1,2,3,4));self.assertEqual(r.fit.empirical.status,'available')
    def test_undocumented_update_blocks_recursive_rate(self):
        self.cfg['transitions'][1]['evidence']['process']=[];self.seal();r=self.result();self.assertIn('transition_history_unresolved',r.fit.interval.reasons)
    def test_known_intervention_blocks_unchanged_geometric_regime(self):
        self.cfg['interventions'].append(O('intervention','recover',pre_state_ref=R('state','S1'),post_state_ref=R('state','S2'),intervention_kind='training',parameters_changed=K(False),direct_answer_injection=K(False),external_refs=[]))
        r=self.result();self.assertIn('intervention_inside_unchanged_regime',r.fit.empirical.reasons);self.assertEqual(r.fit.interval.status,'available')
    def test_separate_post_intervention_suffix_is_allowed(self):
        self.build([[COUNTS[0]]+COUNTS]);self.req['start_ref']=self.req['anchor_ref']=R('state','S1')
        self.cfg['interventions'].append(O('intervention','old',pre_state_ref=R('state','S0'),post_state_ref=R('state','S1'),intervention_kind='training',parameters_changed=K(False),direct_answer_injection=K(False),external_refs=[]))
        self.seal();r=self.result();self.assertEqual(r.status,'available',r.reasons);self.assertEqual(r.fit.state_ids,('S1','S2','S3','S4'))
    def test_unknown_sensitivity_keeps_not_estimated_explicit(self):
        self.req['sensitivity_ref']=K(state='unknown');self.seal();r=self.result();self.assertEqual(r.fit.uncertainty_status,'unknown_not_estimated')
    def test_valid_only_view_is_conditioned_and_denominators_preserved(self):
        self.build(view='classified_valid');r=self.result();self.assertIn('validity_conditioned',r.fit.empirical.qualifiers)
    def test_zero_valid_population_cannot_fit(self):
        self.build(view='classified_valid',validity=['invalid']*128);r=self.result();self.assertEqual(r.status,'unavailable')
    def test_corpus_stage_fit_cannot_become_model_capacity(self):
        for s in self.cfg['states']:
            s.update(state_kind='corpus',stage_role='training_exposure',subject_identity=K({'corpus_identity':K(s['object_id']),'content_sha256':K('a'*64),'unit':'training_rows','material_refs':[]}))
        for p in self.cfg['panels']:p['stage_role']='training_exposure'
        for t in self.cfg['transitions']:t['transition_kind']='synthetic_replacement'
        self.seal();r=self.result();self.assertIn('corpus_stage_not_model_capacity',r.fit.empirical.qualifiers)
    def test_stale_raw_bytes_invalidate_fit(self):
        b=self.bundle();r=h.fit_half_lives(b);snaps=dict(b.snapshots);key=next(iter(snaps));snaps[key]=replace(snaps[key],content=snaps[key].content+b' ')
        with self.assertRaises(InputError):h.assert_current(r,replace(b,snapshots=freeze(snaps)))
    def test_modified_observed_component_is_rejected(self):
        b=self.bundle();o=lg.observe_longitudinal(b)
        with self.assertRaises(InputError):h.fit_half_lives(b,observed=replace(o,status='altered'))
    def test_same_observed_component_accepted_without_I_O(self):
        b=self.bundle();o=lg.observe_longitudinal(b)
        with patch('builtins.open',side_effect=AssertionError('I/O')),patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):
            self.assertEqual(h.fit_half_lives(b,observed=o).results[0].status,'available')
    def test_inactive_registration_dependency_is_not_hidden(self):
        self.support('fit-reg')['payload']['evidence_refs']=[C('evidence','process1')];self.support('process1')['payload']['state']='withdrawn'
        self.assertEqual(self.result().status,'unavailable')
    def test_local_request_needs_its_own_registered_window(self):
        self.req['fit_mode']='local';self.seal();r=self.result();self.assertEqual(r.status,'available');self.assertEqual(r.fit.empirical.status,'not_requested')
        self.support('fit-reg')['payload']['extensions']={};self.assertEqual(self.result().status,'unavailable')


