"""P3 Step 4: independent finite-state enumeration and conditional arithmetic.

These are mathematical/software fixtures, not sampled model outputs. Oracles use
separate count enumeration or high-precision logarithms, never production output.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import ast
import copy
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
from itertools import product
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import categorical_null as cn
from structdet_bench import longitudinal_records as lr
from structdet_bench.contracts import ExactNumber, InputError, freeze
from structdet_bench.local_io import load_bundle
from tests.helpers import ROOT, tagged as K, rewrite_evidence_bundle
from tests.test_longitudinal_records import materialize, O
from tests import phase3_helpers as gh

ORACLES = ROOT / 'tests/fixtures/categorical_null_oracles.json'


def assumptions(**changes):
    a = {k: K(True) for k in cn.ASSUMPTIONS}
    a.update({k: K(v) if type(v) is bool else v for k,v in changes.items()})
    return a


def scenario(p=('0.5','0.5'), n=2, steps=3, **kw):
    a = kw.pop('assumptions', assumptions())
    classes = kw.pop('classes', tuple('c'+str(i) for i in range(len(p))))
    return cn.categorical_null(classes,p,scenario_id=kw.pop('scenario_id','null-toy'),n=n,steps=steps,assumptions=a,**kw)


def mix(p=(1,0), e=(0,1), lam='0.5', w=(1,0), **kw):
    return cn.mixture_selection(kw.pop('classes',('a','b')),p,e,scenario_id=kw.pop('scenario_id','mix-toy'),
        class_space_id=kw.pop('class_space_id','toy-space-v1'),effective_weight=lam,weights=w,
        lambda_unit=kw.pop('lambda_unit','effective_preselection_probability'),
        weight_unit=kw.pop('weight_unit','reproductive_weight'),**kw)


def independent_outcomes(p, n):
    """Tiny trusted enumeration using factorial probabilities and count moments."""
    for counts in product(range(n+1),repeat=len(p)):
        if sum(counts)!=n:
            continue
        mass=F(math.factorial(n))
        for count, probability in zip(counts,p):
            mass *= probability**count / math.factorial(count)
        child=tuple(F(x,n) for x in counts)
        yield counts,mass,child


def enum_moments(p,n,q=None):
    total=F(0);div=F(0);err=F(0);omission=[F(0)]*len(p)
    for counts,mass,child in independent_outcomes(p,n):
        total+=mass
        div+=mass*(1-sum(x*x for x in child))
        if q is not None:
            err+=mass*sum((x-y)**2 for x,y in zip(child,q))
        for i,x in enumerate(counts):
            if x==0:omission[i]+=mass
    return total,div,err,tuple(omission)


class ProbabilityContractTests(unittest.TestCase):
    def test_explicit_fraction_and_decimal_representations_agree(self):
        results=[scenario(p=p) for p in [(F(3,4),F(1,4)),('0.75','0.25'),(ExactNumber('7.5e-1'),ExactNumber('0.250'))]]
        self.assertTrue(all(r.parent==(F(3,4),F(1,4)) for r in results))
        self.assertEqual(results[0].forecast,results[2].forecast)
    def test_invalid_probability_totals_not_normalized(self):
        for p in [(0,0),('0.1','0.1'),(1,1),('0.5','0.499999999999999999999999999')]:
            with self.assertRaises(InputError):scenario(p)
    def test_negative_probability_is_rejected(self):
        for p in [(-1,2),(F(-1,2),F(3,2)),('-0.1','1.1')]:
            with self.assertRaises(InputError):scenario(p)
    def test_binary_float_and_bool_do_not_become_probabilities(self):
        for p in [(0.5,0.5),(True,0),(Decimal('.5'),Decimal('.5'))]:
            with self.assertRaises(InputError):scenario(p)
    def test_empty_duplicate_and_unsafe_class_ids_rejected(self):
        for cs in [[],['a','a'],['a','../x'],['a',True],['a','']]:
            with self.assertRaises(InputError):scenario(classes=cs)
    def test_mismatched_probability_dimension_rejected(self):
        with self.assertRaises(InputError):scenario(classes=['a','b','c'])
    def test_boolean_float_missing_or_nonpositive_n_not_inferred(self):
        for n in [True,False,0,-1,2.0,'2',None,{'tokens':2},2**63]:
            with self.assertRaises(InputError):scenario(n=n)
    def test_unknown_or_missing_assumptions_not_fabricated(self):
        r=scenario(assumptions=assumptions(closed=K(state='unknown')))
        self.assertEqual(r.forecast_status,'unavailable');self.assertEqual(r.parent_diversity.value,F(1,2))
        with self.assertRaises(InputError):scenario(assumptions={})
    def test_false_assumptions_withhold_null_not_parent_arithmetic(self):
        for key in cn.ASSUMPTIONS[:4]:
            r=scenario(assumptions=assumptions(**{key:False}))
            self.assertEqual(r.expected_next_diversity.status,'unavailable')
            self.assertEqual(r.positive_support,('c0','c1'));self.assertEqual(r.forecast,())
    def test_nonboolean_assumption_is_contract_error(self):
        for v in [K(1),K('true'),True,None]:
            with self.assertRaises(InputError):scenario(assumptions={**assumptions(),'closed':v})
    def test_fixed_n_does_not_need_exogenous_schedule_assumption(self):
        r=scenario(assumptions=assumptions(exogenous_schedule=K(state='unknown')))
        self.assertEqual(r.assumption_status,'satisfied_for_declared_model')
    def test_steps_must_be_bounded_actual_integer(self):
        for steps in [True,-1,1.0,'1',10001]:
            with self.assertRaises(InputError):scenario(steps=steps)
    def test_zero_steps_retains_only_initial_point(self):
        r=scenario(steps=0)
        self.assertEqual(len(r.forecast),1);self.assertEqual(r.forecast[0].round_index,0)
        self.assertEqual(r.expected_next_diversity.value,F(1,4))
    def test_scenario_identity_required(self):
        for identity in ['',False,'a/b']:
            with self.assertRaises(InputError):scenario(scenario_id=identity)
    def test_operands_are_immutable_and_preserve_original_tokens(self):
        p=['0.50','5e-1'];a=assumptions();r=scenario(p,assumptions=a)
        p[0]='1';a['closed']=K(False)
        self.assertEqual(r.original_operands['p'],('0.50','5e-1'))
        self.assertTrue(r.assumptions['closed']['value'])
        with self.assertRaises(TypeError):r.assumptions['closed']=K(False)
    def test_no_pseudocounts_in_zero_classes(self):
        r=scenario((F(1,2),F(1,2),0),classes=['a','b','z'])
        self.assertEqual(r.parent[2],0);self.assertEqual(r.positive_support,('a','b'))
        self.assertEqual(r.omission_probabilities['z'].value,1)
    def test_zero_decimal_with_large_allowed_exponent_stays_zero(self):
        r=scenario(('0e100000',1))
        self.assertEqual(r.parent,(F(0),F(1)))
    def test_limit_configuration_cannot_raise_or_change_method(self):
        for lim in [{'max_exact_bits':262145},{'max_exact_bits':True},{'max_states':0},{'other':1},{'sensitivity_replicates':1},[]]:
            with self.assertRaises(InputError):scenario(limits=lim)
    def test_direct_cycle_and_opaque_object_fail_before_freeze(self):
        q=[];q.append(q)
        with self.assertRaises(InputError):scenario(q=q)
        with self.assertRaises(InputError):scenario(q=object())


class EnumerationTests(unittest.TestCase):
    def test_pinned_independent_oracles(self):
        f=json.loads(ORACLES.read_text())
        for row in f['moments']:
            p=tuple(F(*x) for x in row['p']);q=tuple(F(*x) for x in row['q']) if row.get('q') else None
            kwargs={} if q is None else {'q':q}
            r=scenario(p,n=row['n'],**kwargs)
            self.assertEqual(r.parent_diversity.value,F(*row['D']))
            self.assertEqual(r.expected_next_diversity.value,F(*row['next_D']))
            self.assertEqual([x.value for x in r.omission_probabilities.values()],[F(*v) for v in row['omission']])
            if q is not None:
                self.assertEqual(r.target_error.value,F(*row['L']))
                self.assertEqual(r.expected_next_target_error.value,F(*row['next_L']))
    def test_three_two_draw_outcomes_have_independent_probabilities(self):
        actual=list(independent_outcomes((F(1,2),F(1,2)),2))
        self.assertEqual([r[1] for r in actual],[F(1,4),F(1,2),F(1,4)])
        self.assertEqual(enum_moments((F(1,2),F(1,2)),2)[1],F(1,4))
    def test_exhaustive_small_distributions_match_multinomial_moments(self):
        for parts in product(range(5),repeat=3):
            if sum(parts)!=4:continue
            p=tuple(F(x,4) for x in parts);q=(F(1,3),)*3
            for n in range(1,5):
                mass,D,L,om=enum_moments(p,n,q)
                r=scenario(p,n=n,q=q,steps=2)
                self.assertEqual(mass,1);self.assertEqual(r.expected_next_diversity.value,D)
                self.assertEqual(r.expected_next_target_error.value,L)
                self.assertEqual(tuple(x.value for x in r.omission_probabilities.values()),om)
    def test_multiple_rounds_agree_with_enumerated_chain(self):
        states={(F(1,2),F(1,2)):F(1)}
        r=scenario(steps=4)
        for t in range(5):
            D=sum(mass*(1-sum(x*x for x in state)) for state,mass in states.items())
            self.assertEqual(D,r.forecast[t].expected_diversity)
            nxt={}
            for parent,weight in states.items():
                for _,mass,child in independent_outcomes(parent,2):
                    nxt[child]=nxt.get(child,F(0))+weight*mass
            states=nxt
    def test_diversity_and_concentration_exact_complements(self):
        r=scenario(('0.9','0.1'),n=7,steps=8)
        self.assertEqual(r.parent_diversity.value+r.parent_concentration.value,1)
        for point in r.forecast:self.assertEqual(point.expected_diversity+point.expected_concentration,1)
    def test_rare_omission_greater_than_common_omission(self):
        r=scenario(('0.1','0.5','0.4'),n=4)
        self.assertEqual(r.omission_probabilities['c0'].value,F(6561,10000))
        self.assertEqual(r.omission_probabilities['c1'].value,F(1,16))
        self.assertGreater(r.omission_probabilities['c0'].value,r.omission_probabilities['c1'].value)
    def test_omission_for_probability_zero_and_one(self):
        r=scenario((0,1),n=37)
        self.assertEqual([x.value for x in r.omission_probabilities.values()],[F(1),F(0)])
    def test_shannon_or_effective_count_not_used_as_diversity(self):
        r=scenario(('0.75','0.25'),n=4)
        self.assertEqual(r.parent_diversity.value,F(3,8))
        self.assertNotEqual(r.parent_diversity.value,1/r.parent_concentration.value)
        self.assertFalse(hasattr(r,'empirical_half_life'))
    def test_class_renaming_preserves_scalars_not_identity(self):
        a=scenario();b=scenario(classes=['x','y'])
        self.assertEqual(a.forecast,b.forecast);self.assertNotEqual(a.positive_support,b.positive_support)
    def test_simultaneous_class_permutation_preserves_aligned_results(self):
        a=scenario(('0.8','0.2'),classes=['a','b'],q=('0.6','0.4'))
        b=scenario(('0.2','0.8'),classes=['b','a'],q=('0.4','0.6'))
        self.assertEqual(a.forecast,b.forecast)
        self.assertEqual(dict(a.omission_probabilities),dict(b.omission_probabilities))
    def test_expected_SCI_not_expected_inverse_effective_count(self):
        r=scenario(n=2)
        expected_simpson=sum(mass/(sum(x*x for x in child)) for _,mass,child in independent_outcomes((F(1,2),F(1,2)),2))
        self.assertNotEqual(1/r.forecast[1].expected_concentration,expected_simpson)
        self.assertFalse(hasattr(r.forecast[1],'expected_effective_count'))
    def test_no_production_sampling_or_enumeration(self):
        for name in ['simulate','sample','enumerate_outcomes','train','generate','fit','bootstrap']:
            self.assertFalse(hasattr(cn,name))
        with patch('random.random',side_effect=AssertionError('draw')):
            self.assertEqual(scenario().simulated_draws,0)


class TargetTests(unittest.TestCase):
    def test_external_target_never_defaults_to_initial_or_uniform(self):
        r=scenario(('0.9','0.1'))
        self.assertIsNone(r.target);self.assertEqual(r.target_status,'not_requested')
        self.assertIsNone(r.forecast[-1].expected_target_error)
    def test_explicit_unknown_target_not_omitted(self):
        r=scenario(q=None)
        self.assertEqual(r.target_status,'unavailable');self.assertEqual(r.expected_next_target_error.status,'unavailable')
        self.assertEqual(r.expected_next_diversity.value,F(1,4))
    def test_malformed_target_does_not_poison_independent_D(self):
        for q in [(1,1),('0.5',),(-1,2),[0.5,0.5]]:
            r=scenario(q=q)
            self.assertEqual(r.target_status,'unavailable');self.assertEqual(r.parent_diversity.value,F(1,2))
            self.assertIsNone(r.expected_next_target_error.value)
    def test_drift_p_three_quarters_q_half(self):
        r=scenario(('0.75','0.25'),n=4,q=('0.5','0.5'))
        self.assertEqual(r.target_error.value,F(1,8));self.assertEqual(r.expected_next_target_error.value,F(7,32))
    def test_target_equal_parent_still_drifts_in_expectation(self):
        r=scenario(q=('0.5','0.5'),n=4)
        self.assertEqual(r.target_error.value,0);self.assertEqual(r.expected_next_target_error.value,F(1,8))
    def test_forecast_error_telescopes_by_lost_expected_D(self):
        r=scenario(('0.75','0.25'),n=4,q=('0.2','0.8'),steps=8)
        for x in r.forecast:
            self.assertEqual(x.expected_target_error,r.target_error.value+r.parent_diversity.value-x.expected_diversity)
    def test_target_changes_only_target_endpoints(self):
        a=scenario(q=('0.5','0.5'));b=scenario(q=(1,0))
        self.assertEqual(a.expected_next_diversity,b.expected_next_diversity)
        self.assertNotEqual(a.target_error,b.target_error)
    def test_zero_diversity_has_zero_drift_increment(self):
        r=scenario((1,0),q=('0.2','0.8'),n=9)
        self.assertEqual(r.expected_next_target_error.value,r.target_error.value)
    def test_q_does_not_establish_deployment_reference(self):
        r=scenario(q=(1,0))
        self.assertFalse(r.substantive_validation_performed);self.assertFalse(r.empirical_pipeline_matches_null)
        self.assertFalse(hasattr(r,'omitted_deployment_mass'))


class HalfLifeTests(unittest.TestCase):
    def test_n_two_source_timescale_exactly_one(self):
        r=scenario(n=2)
        self.assertEqual(r.structural_half_life_null.value,1.0)
        self.assertEqual(r.null_first_expected_half_crossing.value,1)
    def test_log_timescales_agree_with_pinned_high_precision_oracles(self):
        for case in json.loads(ORACLES.read_text())['shl']:
            r=scenario(n=case['n'],steps=1)
            expected=float(Decimal(case['value']))
            self.assertLessEqual(abs(r.structural_half_life_null.value-expected),1e-12+1e-10*abs(expected))
    def test_continuous_timescale_and_integer_crossing_differ(self):
        r=scenario(n=3)
        self.assertGreater(r.structural_half_life_null.value,1)
        self.assertLess(r.structural_half_life_null.value,2)
        self.assertEqual(r.null_first_expected_half_crossing.value,2)
    def test_integer_crossing_certified_without_rounded_log(self):
        with patch.object(cn.math,'log',return_value=99.0):
            r=scenario(n=3)
        self.assertEqual(r.null_first_expected_half_crossing.value,2)
    def test_small_n_integer_crossing_has_exact_brackets(self):
        for n in range(2,30):
            k=scenario(n=n,steps=0).null_first_expected_half_crossing.value
            self.assertLessEqual(F(n-1,n)**k,F(1,2))
            self.assertGreater(F(n-1,n)**(k-1),F(1,2))
    def test_n_one_outside_formula_and_one_step_collapse(self):
        r=scenario(n=1)
        self.assertEqual(r.structural_half_life_null.status,'undefined');self.assertIsNone(r.structural_half_life_null.value)
        self.assertEqual(r.null_first_expected_half_crossing.value,1)
        self.assertEqual(r.halving_applicability,'one_step_collapse_outside_log_domain')
        self.assertEqual(r.forecast[1].expected_diversity,0)
    def test_zero_D_keeps_parameter_timescale_but_no_halving(self):
        r=scenario((1,0),n=2)
        self.assertEqual(r.structural_half_life_null.value,1)
        self.assertIn('conditional_parameter_timescale',r.structural_half_life_null.qualifiers)
        self.assertEqual(r.halving_applicability,'no_positive_diversity')
        self.assertEqual(r.null_first_expected_half_crossing.status,'undefined')
    def test_n_one_and_zero_D_have_separate_reasons(self):
        r=scenario((1,0),n=1)
        self.assertEqual(r.structural_half_life_null.reasons,('n_one_outside_log_domain',))
        self.assertEqual(r.null_first_expected_half_crossing.reasons,('no_positive_initial_diversity',))
    def test_large_n_stable_log_without_subtractive_rounding(self):
        r=scenario(n=2**63-1,steps=1)
        self.assertEqual(1.0-1.0/(2**63-1),1.0)
        self.assertTrue(math.isfinite(r.structural_half_life_null.value))
        self.assertEqual(r.null_first_expected_half_crossing.status,'unavailable')
        self.assertEqual(r.forecast_status,'available')
    def test_nonfinite_log_result_is_withheld(self):
        with patch.object(cn.math,'log',return_value=float('inf')):
            r=scenario()
        self.assertEqual(r.structural_half_life_null.status,'unavailable')
        self.assertEqual(r.null_first_expected_half_crossing.value,1)
        self.assertEqual(r.expected_next_diversity.value,F(1,4))
    def test_log_error_does_not_change_exact_scenario(self):
        with patch.object(cn.math,'log1p',side_effect=ValueError('bad log')):
            r=scenario()
        self.assertIsNone(r.structural_half_life_null.value);self.assertEqual(r.forecast[1].expected_diversity,F(1,4))
    def test_named_timescale_units_and_no_empirical_claim(self):
        q=scenario().structural_half_life_null
        self.assertEqual(q.name,'structural_half_life_null');self.assertEqual(q.unit,'categorical_recursive_rounds')
        self.assertEqual(q.evaluation,'binary64_log1p');self.assertEqual(q.uncertainty_status,'not_estimated')


class ScheduleTests(unittest.TestCase):
    def test_two_then_four_multiplier_three_eighths(self):
        r=scenario(n=None,steps=2,schedule=(2,4))
        self.assertEqual(r.forecast[-1].retained_multiplier,F(3,8))
        self.assertEqual(r.forecast[-1].expected_diversity,F(3,16))
        self.assertEqual(r.mode,'deterministic_schedule')
    def test_mean_n_cannot_replace_registered_schedule(self):
        a=scenario(steps=2,schedule=(2,4));b=scenario(n=3,steps=2)
        self.assertNotEqual(a.forecast[-1].expected_diversity,b.forecast[-1].expected_diversity)
    def test_supplied_n_does_not_override_explicit_schedule(self):
        a=scenario(n=999,steps=2,schedule=(2,4));b=scenario(n=None,steps=2,schedule=(2,4))
        self.assertEqual(a.forecast,b.forecast);self.assertEqual(a.n,999)
    def test_schedule_never_reports_fixed_n_SHL(self):
        r=scenario(steps=2,schedule=(4,4))
        self.assertEqual(r.structural_half_life_null.status,'not_requested')
        self.assertEqual(r.null_first_expected_half_crossing.name,'null_schedule_first_half_crossing')
    def test_first_schedule_crossing_uses_actual_sequence(self):
        r=scenario(steps=3,schedule=(4,4,2))
        self.assertEqual(r.null_first_expected_half_crossing.value,3)
    def test_crossing_outside_schedule_never_extrapolated(self):
        r=scenario(steps=2,schedule=(4,4))
        self.assertIsNone(r.null_first_expected_half_crossing.value)
        self.assertIn('not_reached_in_declared_schedule',r.null_first_expected_half_crossing.reasons)
    def test_schedule_with_n_one_has_absorbed_future_D(self):
        r=scenario(steps=3,schedule=(4,1,10))
        self.assertEqual([x.expected_diversity for x in r.forecast],[F(1,2),F(3,8),0,0])
        self.assertEqual(r.null_first_expected_half_crossing.value,2)
    def test_adaptive_schedule_rejected_for_product_formula(self):
        r=scenario(steps=2,schedule=(2,4),assumptions=assumptions(exogenous_schedule=False))
        self.assertEqual(r.forecast_status,'unavailable');self.assertEqual(r.forecast,())
        self.assertIn('exogenous_schedule_not_satisfied',r.reasons)
    def test_unknown_schedule_assumption_is_not_deterministic(self):
        r=scenario(steps=2,schedule=(2,4),assumptions=assumptions(exogenous_schedule=K(state='unknown')))
        self.assertEqual(r.assumption_status,'unavailable')
    def test_schedule_shape_and_members_strict(self):
        for sched in [(2,), (2,4,5), (True,2), (0,2), ('2',4), (2.0,4)]:
            with self.assertRaises(InputError):scenario(steps=2,schedule=sched)
    def test_zero_length_schedule_only_initial_state(self):
        r=scenario(n=None,steps=0,schedule=())
        self.assertEqual(len(r.forecast),1);self.assertIsNone(r.null_first_expected_half_crossing.value)
    def test_variable_schedule_target_drift_matches_enumeration(self):
        q=(F(1),F(0));states={(F(1,2),F(1,2)):F(1)}
        r=scenario(n=None,steps=2,schedule=(2,4),q=q)
        for n in (2,4):
            out={}
            for p,weight in states.items():
                for _,mass,child in independent_outcomes(p,n):out[child]=out.get(child,F(0))+weight*mass
            states=out
        expected=sum(mass*sum((x-y)**2 for x,y in zip(p,q)) for p,mass in states.items())
        self.assertEqual(r.forecast[-1].expected_target_error,expected)


class PathTests(unittest.TestCase):
    def test_possible_realized_diversity_increase_is_legal(self):
        r=scenario(('0.9','0.1'),n=2,steps=1,child_counts=((1,1),))
        t=r.child_transitions[0]
        self.assertEqual(t.status,'consistent_with_null');self.assertTrue(t.realized_diversity_increased)
        self.assertEqual(t.child_diversity.value,F(1,2));self.assertEqual(t.expected_child_diversity.value,F(9,100))
    def test_child_on_zero_parent_is_explicit_violation_and_retained(self):
        r=scenario((1,0),n=2,steps=1,child_counts=((1,1),))
        t=r.child_transitions[0]
        self.assertEqual(t.status,'inconsistent');self.assertEqual(t.violates_absorption,('c1',))
        self.assertEqual(t.child,(F(1,2),F(1,2)));self.assertEqual(t.supplied_counts,(1,1))
    def test_later_count_after_absorption_cannot_reopen_null(self):
        r=scenario(n=2,steps=3,child_counts=((2,0),(2,0),(1,1)))
        self.assertEqual([x.status for x in r.child_transitions],['consistent_with_null','consistent_with_null','inconsistent'])
    def test_count_sum_error_never_normalized(self):
        t=scenario(n=2,steps=1,child_counts=((2,1),)).child_transitions[0]
        self.assertEqual(t.supplied_counts,(2,1));self.assertIsNone(t.child)
        self.assertIn('child_count_sum_mismatch',t.reasons)
    def test_negative_fractional_boolean_and_text_counts_invalid(self):
        for counts in [(True,1),(0.5,1.5),(-1,3),('1',1),(None,2)]:
            t=scenario(steps=1,child_counts=(counts,)).child_transitions[0]
            self.assertEqual(t.status,'inconsistent');self.assertEqual(t.supplied_counts,counts)
    def test_count_dimension_error_does_not_delete_row(self):
        r=scenario(steps=2,child_counts=((1,),(1,1)))
        self.assertEqual(len(r.child_transitions),2);self.assertEqual(r.child_transitions[0].status,'inconsistent')
        self.assertEqual(r.child_transitions[1].child_diversity.value,F(1,2))
        self.assertEqual(r.child_transitions[1].expected_child_diversity.status,'unavailable')
    def test_extra_count_vector_not_given_extra_transition(self):
        r=scenario(steps=1,child_counts=((1,1),(1,1)))
        self.assertEqual(len(r.forecast),2);self.assertIn('child_outside_requested_transitions',r.child_transitions[1].reasons)
    def test_fewer_supplied_counts_do_not_fabricate_path(self):
        r=scenario(steps=5,child_counts=((1,1),))
        self.assertEqual(len(r.child_transitions),1);self.assertEqual(len(r.forecast),6)
    def test_variable_schedule_validates_each_count_n(self):
        r=scenario(n=None,steps=2,schedule=(2,4),child_counts=((1,1),(3,1)))
        self.assertTrue(all(x.status=='consistent_with_null' for x in r.child_transitions))
        self.assertEqual([x.n for x in r.child_transitions],[2,4])
    def test_supplied_path_does_not_replace_unconditional_forecast(self):
        a=scenario(n=2,steps=2);b=scenario(n=2,steps=2,child_counts=((2,0),(2,0)))
        self.assertEqual(a.forecast,b.forecast)
        self.assertEqual(b.child_transitions[1].expected_child_diversity.value,0)
        self.assertEqual(b.forecast[2].expected_diversity,F(1,8))
    def test_external_error_may_improve_on_individual_path(self):
        r=scenario(('0.9','0.1'),n=2,q=('0.5','0.5'),steps=1,child_counts=((1,1),))
        t=r.child_transitions[0]
        self.assertLess(t.child_target_error.value,r.target_error.value)
        self.assertGreater(t.expected_child_target_error.value,r.target_error.value)
    def test_thresholded_occupancy_can_increase_without_new_exact_support(self):
        r=scenario(('0.6','0.3','0.1'),n=10,steps=1,child_counts=((5,3,2),))
        t=r.child_transitions[0]
        self.assertTrue(t.support_nonexpanding)
        self.assertEqual(sum(x>=F(1,5) for x in t.parent),2)
        self.assertEqual(sum(x>=F(1,5) for x in t.child),3)
    def test_unknown_assumptions_do_not_claim_path_conformance(self):
        r=scenario(steps=1,child_counts=((1,1),),assumptions=assumptions(closed=K(state='unknown')))
        t=r.child_transitions[0];self.assertEqual(t.status,'unavailable')
        self.assertIsNone(t.support_nonexpanding);self.assertEqual(t.child_diversity.value,F(1,2))
    def test_invalid_path_does_not_erase_parent_expectation(self):
        r=scenario((1,0),steps=1,child_counts=((1,1),))
        self.assertEqual(r.expected_next_diversity.value,0);self.assertEqual(r.forecast_status,'available')
        self.assertIn('supplied_path_restricted',r.reasons)


class MixtureTests(unittest.TestCase):
    def test_new_external_class_can_be_removed_by_zero_selection(self):
        r=mix()
        self.assertEqual(r.candidate,(F(1,2),F(1,2)));self.assertEqual(r.selected,(F(1),F(0)))
        self.assertEqual(r.added_candidate_classes,('b',));self.assertEqual(r.removed_by_selection,('b',))
    def test_all_zero_weights_give_undefined_selection(self):
        r=mix(w=(0,0))
        self.assertEqual(r.status,'undefined');self.assertEqual(r.selection_mass.value,0)
        self.assertIsNone(r.selected);self.assertEqual(r.candidate,(F(1,2),F(1,2)))
    def test_nonzero_weights_only_on_zero_mass_still_undefined(self):
        r=mix(lam=0,w=(0,1))
        self.assertEqual(r.status,'undefined');self.assertIsNone(r.selected)
    def test_unknown_weights_keep_candidate_without_selected_output(self):
        for weights in [None,(1,None),(K(1),K(state='unknown'))]:
            r=mix(w=weights);self.assertEqual(r.candidate,(F(1,2),F(1,2)))
            self.assertIsNone(r.selected);self.assertIn('selection_weights_unknown',r.reasons)
    def test_unknown_lambda_is_not_source_volume(self):
        for lam in [None,K(state='unknown')]:
            r=mix(lam=lam);self.assertIsNone(r.candidate)
            self.assertIn('effective_preselection_weight_unknown',r.reasons)
    def test_invalid_lambda_and_probability_units_rejected(self):
        for lam in [-1,'1.1',True,.5]:
            with self.assertRaises(InputError):mix(lam=lam)
        for unit in ['tokens','rows','real_data_ratio','source_count']:
            with self.assertRaises(InputError):mix(lambda_unit=unit)
    def test_incompatible_reproductive_units_rejected(self):
        for unit in ['tokens','documents','unknown',None]:
            with self.assertRaises(InputError):mix(weight_unit=unit)
    def test_negative_weights_rejected(self):
        for w in [(-1,1),(F(-1,2),1),('1','-0.1')]:
            with self.assertRaises(InputError):mix(w=w)
    def test_bad_weight_shape_and_types_rejected(self):
        for w in [(1,), (1,2,3), (True,1), (0.5,1), {'a':1,'b':0}]:
            with self.assertRaises(InputError):mix(w=w)
    def test_explicit_lambda_zero_and_one(self):
        self.assertEqual(mix(lam=0,w=(1,1)).candidate,(F(1),F(0)))
        self.assertEqual(mix(lam=1,w=(1,1)).candidate,(F(0),F(1)))
    def test_positive_common_weight_scaling_invariant(self):
        a=mix(w=(2,3));b=mix(w=(200,300))
        self.assertEqual(a.selected,b.selected);self.assertNotEqual(a.selection_mass.value,b.selection_mass.value)
    def test_independent_general_mixture_formula(self):
        p=(F(3,4),F(1,4));e=(F(1,4),F(3,4));lam=F(1,3);w=(F(2),F(5))
        candidate=tuple((1-lam)*x+lam*y for x,y in zip(p,e))
        weights=tuple(x*y for x,y in zip(candidate,w));total=sum(weights)
        r=mix(p,e,lam,w)
        self.assertEqual(r.candidate,candidate);self.assertEqual(r.selected,tuple(x/total for x in weights))
    def test_parent_external_distributions_not_silently_normalized(self):
        for p,e in [((2,0),(0,1)),((1,0),(0,0)),((1,0),(0,-1))]:
            with self.assertRaises(InputError):mix(p,e)
    def test_registry_does_not_add_probability_mass(self):
        r=mix((1,0,0),(0,1,0),'0.5',(1,1,1),classes=['a','b','c'])
        self.assertEqual(r.candidate[2],0);self.assertEqual(r.selected[2],0)
    def test_no_selected_dataset_to_neural_model_map(self):
        r=mix(w=(1,1))
        self.assertIsNone(r.next_model_distribution);self.assertFalse(r.structural_exogamy_established)
        self.assertFalse(r.substantive_validation_performed)
    def test_class_space_and_operand_identity_are_preserved(self):
        r=mix(lam='0.5000')
        self.assertEqual(r.class_space_id,'toy-space-v1');self.assertEqual(r.original_operands['effective_weight'],'0.5000')
        self.assertEqual(r.parameter_scope,'declared_effective_preselection_weight')
    def test_mixture_never_changes_null_absorption_rule(self):
        m=mix(w=(1,1));n=scenario((1,0),steps=1,child_counts=((1,1),))
        self.assertEqual(m.selected,(F(1,2),F(1,2)))
        self.assertEqual(n.child_transitions[0].status,'inconsistent')
    def test_mixture_arguments_copy_not_alias(self):
        p=[1,0];weights=[1,1];r=mix(p=p,w=weights)
        p[0]=0;weights[0]=99
        self.assertEqual(r.original_operands['p'],(1,0));self.assertEqual(r.weights,(F(1),F(1)))


class ResourceTests(unittest.TestCase):
    def test_decimal_preflight_precedes_huge_power(self):
        with patch.object(cn._Exact,'power',side_effect=AssertionError('must not construct')) as power:
            with self.assertRaises(InputError):scenario(('1e-100000',1),limits={'max_exact_bits':128})
        power.assert_not_called()
    def test_fraction_input_size_limit_precedes_arithmetic(self):
        with self.assertRaises(InputError):scenario((F(1,2**1000),1),limits={'max_exact_bits':128})
    def test_forecast_limit_withholds_whole_requested_curve(self):
        r=scenario(n=3,steps=100,limits={'max_exact_bits':32})
        self.assertEqual(r.forecast_status,'unavailable');self.assertEqual(r.forecast,())
        self.assertEqual(r.expected_next_diversity.value,F(1,3))
    def test_omission_limit_does_not_force_approximation_or_hide_D(self):
        r=scenario(n=100000,steps=1,limits={'max_exact_bits':128})
        self.assertTrue(all(x.status=='unavailable' for x in r.omission_probabilities.values()))
        self.assertEqual(r.parent_diversity.value,F(1,2));self.assertEqual(r.forecast_status,'available')
        self.assertTrue(math.isfinite(r.structural_half_life_null.value))
    def test_forecast_count_limit_rejects_before_expansion(self):
        with self.assertRaises(InputError):scenario(steps=5,limits={'max_forecast_steps':4})
    def test_class_and_path_work_limits_are_explicit(self):
        with self.assertRaises(InputError):scenario(limits={'max_categorical_classes':1})
        with self.assertRaises(InputError):scenario(child_counts=((1,1),)*20,limits={'max_link_objects':20})
    def test_nonfinite_tokens_and_child_values_never_publish(self):
        for v in ['NaN','Infinity','-Infinity','1e100001']:
            with self.assertRaises(InputError):scenario((v,1))
        with self.assertRaises(InputError):scenario(child_counts=((float('inf'),0),))
    def test_resource_failure_keeps_no_fake_zero_scalar(self):
        r=scenario(n=100000,steps=1,limits={'max_exact_bits':128})
        q=r.omission_probabilities['c0'];self.assertIsNone(q.value);self.assertNotEqual(q.status,'available')
    def test_internal_bounded_power_keeps_zero_and_one_shortcuts(self):
        a=cn._Exact(cn._limits({'max_exact_bits':16}))
        self.assertEqual(a.power(F(0),2**63-1),0);self.assertEqual(a.power(F(1),2**63-1),1)
        self.assertEqual(a.power(F(0),0),1)
    def test_no_process_network_or_file_after_operands_supplied(self):
        with patch('builtins.open',side_effect=AssertionError('file')),patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):
            self.assertEqual(scenario().expected_next_diversity.value,F(1,4))
            self.assertEqual(mix().selected,(F(1),F(0)))


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.obs,self.sup,self.man=materialize(self.root)
        self.cfg=self.man['analysis_config']['extensions']['longitudinal']
        self.cfg['capabilities'].append('categorical_null')
        self.cfg['null_scenarios']=[O('null_scenario','N1',classes=['a','b'],p=['0.5','0.5'],n=K(2),steps=3,q=K(None),schedule=K(None),assumptions=assumptions(),child_counts=[])]
    def bundle(self):return load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.sup,self.man))
    def test_existing_null_records_reach_formula_without_new_reader(self):
        r=cn.evaluate_categorical_null(self.bundle());self.assertEqual(r.scenarios[0].result.parent_diversity.value,F(1,2))
        self.assertEqual(r.scenarios[0].evidence_status,'fixture_only')
    def test_old_bundle_absence_keeps_not_requested(self):
        self.man['analysis_config']['extensions']={}
        r=cn.evaluate_categorical_null(self.bundle());self.assertFalse(r.requested);self.assertEqual(r.status,'not_requested')
    def test_longitudinal_without_null_capability_is_not_requested(self):
        self.cfg['capabilities']=['observed'];self.cfg['null_scenarios']=[]
        self.assertEqual(cn.evaluate_categorical_null(self.bundle()).status,'not_requested')
    def test_explicit_null_profile_not_successful_absence(self):
        self.man['analysis_config']['extensions']['longitudinal']=None
        r=cn.evaluate_categorical_null(self.bundle());self.assertTrue(r.requested);self.assertEqual(r.status,'contract_error')
    def test_q_unknown_remains_unavailable_in_bound_result(self):
        self.cfg['null_scenarios'][0]['q']=K(state='unknown')
        r=cn.evaluate_categorical_null(self.bundle()).scenarios[0].result
        self.assertEqual(r.target_status,'unavailable');self.assertEqual(r.expected_next_diversity.value,F(1,4))
    def test_unknown_n_is_unavailable_not_inferred_from_probe_count(self):
        self.cfg['null_scenarios'][0]['n']=K(state='unknown')
        r=cn.evaluate_categorical_null(self.bundle()).scenarios[0]
        self.assertEqual(r.status,'unavailable');self.assertIsNone(r.result)
    def test_unknown_schedule_never_falls_back_to_fixed_n(self):
        self.cfg['null_scenarios'][0]['schedule']=K(state='unknown')
        r=cn.evaluate_categorical_null(self.bundle()).scenarios[0]
        self.assertEqual(r.status,'unavailable');self.assertIn('categorical_schedule_declaration_unknown',r.reasons)
    def test_one_bad_scenario_does_not_drop_other_scenario(self):
        second=copy.deepcopy(self.cfg['null_scenarios'][0]);second['object_id']='N2';second['p']=['0.1','0.1'];self.cfg['null_scenarios'].append(second)
        r=cn.evaluate_categorical_null(self.bundle())
        self.assertEqual(len(r.scenarios),2);self.assertEqual(r.scenarios[0].result.forecast_status,'available')
        self.assertEqual(r.scenarios[1].status,'contract_error')
    def test_duplicate_null_identity_preserved_as_errors(self):
        self.cfg['null_scenarios'].append(copy.deepcopy(self.cfg['null_scenarios'][0]))
        r=cn.evaluate_categorical_null(self.bundle())
        self.assertEqual(len(r.scenarios),2);self.assertTrue(all(x.result is None for x in r.scenarios))
    def test_old_M_populations_remain_exactly_unchanged(self):
        from structdet_bench.populations import build_populations
        b=self.bundle();before=build_populations(b);cn.evaluate_categorical_null(b)
        self.assertEqual(build_populations(b),before)
    def test_empirical_observed_recurring_class_not_subject_to_absorption(self):
        from structdet_bench import longitudinal as lg
        from structdet_bench.metrics import count_metrics
        a=lg.support_set(count_metrics({'a':1,'b':0},1));b=lg.support_set(count_metrics({'a':1,'b':1},2))
        change=lg.set_change(a,b)
        self.assertEqual(change.newly_observed,('b',))
    def test_old_review_rejected_after_probability_change(self):
        b=self.bundle();old=lr.review_longitudinal(b)
        self.cfg['null_scenarios'][0]['p']=['0.9','0.1']
        with self.assertRaises(InputError):cn.evaluate_categorical_null(self.bundle(),review=old)
    def test_old_result_rejected_after_loaded_bytes_change(self):
        b=self.bundle();r=cn.evaluate_categorical_null(b);snaps=dict(b.snapshots);key=next(iter(snaps))
        snaps[key]=replace(snaps[key],content=snaps[key].content+b' ')
        with self.assertRaises(InputError):cn.assert_current(r,replace(b,snapshots=freeze(snaps)))
    def test_matching_context_hash_cannot_hide_forged_review(self):
        b=self.bundle();old=lr.review_longitudinal(b)
        with self.assertRaises(InputError):cn.evaluate_categorical_null(b,review=replace(old,status='forged'))
    def test_loaded_limits_part_of_currentness(self):
        b=self.bundle();r=cn.evaluate_categorical_null(b)
        with self.assertRaises(InputError):cn.assert_current(r,replace(b,limits=replace(b.limits,max_records=10)))
    def test_no_bundle_io_after_safe_loader(self):
        b=self.bundle()
        with patch('builtins.open',side_effect=AssertionError('file')),patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):
            self.assertEqual(cn.evaluate_categorical_null(b).scenarios[0].result.expected_next_diversity.value,F(1,4))
    def test_real_claim_flag_never_inferred_from_complete_form(self):
        r=cn.evaluate_categorical_null(self.bundle())
        self.assertFalse(r.substantive_validation_performed)
        self.assertFalse(r.scenarios[0].result.empirical_pipeline_matches_null)
    def test_wrong_bundle_type_controlled(self):
        with self.assertRaises(InputError):cn.evaluate_categorical_null({})
    def test_prior_results_immutable_after_new_scenario_request(self):
        r=cn.evaluate_categorical_null(self.bundle())
        self.cfg['null_scenarios'][0]['p']=['0.9','0.1']
        self.assertEqual(r.scenarios[0].result.parent,(F(1,2),F(1,2)))
    def test_withdrawn_evidence_remains_limitation_not_verified_experiment(self):
        self.cfg['null_scenarios'][0]['evidence']['origin']=self.cfg['states'][0]['evidence']['origin']
        next(x for x in self.sup if x['record_id']=='origin')['payload']['state']='withdrawn'
        r=cn.evaluate_categorical_null(self.bundle()).scenarios[0]
        self.assertEqual(r.status,'available_with_limitations');self.assertTrue(r.reasons)
        self.assertFalse(r.result.substantive_validation_performed)


class MatrixTests(unittest.TestCase):
    def test_actual_step4_methods_all_bound(self):
        m=gh.load_matrix();self.assertEqual(gh.validate_matrix(m),[])
        tree=ast.parse((ROOT/'tests/test_categorical_null.py').read_text())
        ids={f'tests.test_categorical_null.{c.name}.{f.name}' for c in tree.body if isinstance(c,ast.ClassDef) for f in c.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_')}
        self.assertEqual(set(m['stage_bindings']['4']['test_bindings']),ids)
    def test_only_L11_through_L16_newly_completed(self):
        m=gh.load_matrix();done={r['id'] for r in m['longitudinal'] if r['implementation_status']=='implemented'}
        self.assertTrue({f'P3-L{i:02}' for i in range(1,17)}<=done)
        if m['delivery']['step']==4:self.assertEqual(len(done),16)
    def test_frozen_sources_and_prior_matrices_unchanged(self):
        self.assertTrue(all(x['status']=='passed' for x in gh.current_identity_checks()))
        f=json.loads(ORACLES.read_text());self.assertEqual(f['plan_sha256'],gh.PLAN_SHA256)
        self.assertEqual(f['source_pins'],dict(lr.SOURCE_PINS));self.assertEqual(f['data_role'],'fixture')
    def test_independent_saved_log_oracles_match_decimal_derivation(self):
        f=json.loads(ORACLES.read_text())
        with localcontext() as ctx:
            ctx.prec=100
            for row in f['shl']:
                n=Decimal(row['n']);ref=Decimal(2).ln()/(n.ln()-(n-1).ln())
                self.assertLess(abs(ref-Decimal(row['value'])),Decimal('1e-70'))
    def test_future_runtime_and_E_status_not_advanced(self):
        m=gh.load_matrix();self.assertEqual(m['evidence_status'],'not_supplied')
        for name,step in [('half_life',5),('support_assays',6),('recovery',7),('longitudinal_pipeline',8)]:
            if m['delivery']['step']<step:self.assertFalse((ROOT/'structdet_bench'/(name+'.py')).exists())


class AuditEdgeTests(unittest.TestCase):
    def test_unrequested_path_target_stays_not_requested(self):
        t=scenario(steps=1,child_counts=((1,1),)).child_transitions[0]
        self.assertEqual(t.child_target_error.status,'not_requested')
        self.assertEqual(t.expected_child_target_error.status,'not_requested')
    def test_unknown_path_target_remains_unavailable(self):
        t=scenario(steps=1,child_counts=((1,1),),q=None).child_transitions[0]
        self.assertEqual(t.child_target_error.status,'unavailable')
    def test_missing_scenario_id_keeps_error_row(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);obs,sup,man=materialize(root)
            cfg=man['analysis_config']['extensions']['longitudinal'];cfg['capabilities'].append('categorical_null')
            cfg['null_scenarios']=[{'object_kind':'null_scenario'}]
            out=cn.evaluate_categorical_null(load_bundle(rewrite_evidence_bundle(root,obs,sup,man)))
            self.assertEqual(len(out.scenarios),1);self.assertEqual(out.scenarios[0].status,'contract_error')
    def test_selecting_zero_probability_mass_retains_zero_before_undefined(self):
        out=mix(p=(1,0),e=(1,0),lam='0.8',w=(0,2))
        self.assertEqual(out.selection_mass.exact_ratio,(0,1));self.assertIsNone(out.selected)
    def test_invalid_direct_path_is_not_repaired_to_match_n(self):
        t=scenario(n=3,steps=1,child_counts=((2,2),)).child_transitions[0]
        self.assertIsNone(t.child);self.assertEqual(t.supplied_counts,(2,2))
    def test_mixture_exact_fractional_weights_not_rounded(self):
        r=mix(w=(F(1,3),F(2,3)))
        self.assertEqual(r.selected,(F(1,3),F(2,3)))
