"""VF OF-01..14 decision oracles. Conditional fixtures, never model findings."""
from __future__ import annotations
import ast
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
import unittest

from structdet_bench import predictions as p
from structdet_bench import uncertainty as u
from structdet_bench.comparison_records import BLOCKS
from structdet_bench.comparisons import number
from structdet_bench.contracts import InputError,freeze
from tests.helpers import ROOT
from tests.phase2_helpers import paired_summary_fixture,read_matrix


def result(surface='0.10',structural='0',**kwargs):
    s=paired_summary_fixture(surface,structural,**kwargs)
    return u.summarize_sensitivity(s,u.DependenceCheck('fixture_stipulated',s.included_blocks,fixture=True))


def decide(r,**kwargs): return p.evaluate_endpoint(r,material_role='fixture',**kwargs)


class OracleTests(unittest.TestCase):
    def test_all_fourteen_source_outcomes(self):
        data=json.loads((ROOT/'tests/fixtures/prediction_oracles.json').read_text())
        self.assertEqual([x['fixture_id'] for x in data['cases']],[f'OF-{i:02}' for i in range(1,15)])
        for case in data['cases']:
            x=case['inputs']
            with self.subTest(fixture=case['fixture_id']):
                if case['question']=='P1':
                    flags=['surface_proxy_near_ceiling'] if case['fixture_id']=='OF-06' else []
                    r=result(x['surface'],x['structural'],gated=x.get('gated',True))
                    out=decide(r,qualifications=flags,clean_quality_comparable=x.get('clean_quality',True))
                    if case['fixture_id']=='OF-05':
                        self.assertGreater(u.scalar(r.source_summary.means['surface_gain']),0)
                        self.assertLess(u.scalar(r.intervals['surface_gain']['lower']),0)
                        self.assertGreater(u.scalar(r.intervals['surface_gain']['upper']),0)
                    if case['fixture_id']=='OF-07':
                        other=decide(result(x['valid_surface'],x['valid_structural'],view='classified_valid'))
                        self.assertEqual(other.outcome,'contrary');self.assertEqual(other.role,'prespecified_valid_sensitivity')
                else:
                    comps=tuple(decide(result(p5=x[k],pair=k,gated=x.get('gated',True))) for k in ('C-A','C-B'))
                    out,mixed=p.combine_p5(comps,material_role='fixture')
                    if case['fixture_id']=='OF-09':self.assertTrue(mixed)
                    if case['fixture_id']=='OF-12':
                        self.assertEqual(abs(Fraction(*x['C_valid'])-Fraction(*x['comparator_valid'])),Fraction(3,20))
                        self.assertGreater(u.scalar(comps[0].source.source_summary.means['p5_valid_distinct_k_delta']),0)
                self.assertEqual(out.outcome,case['expected']);self.assertEqual(out.permitted_claim_scope,'fixture_only')
                self.assertFalse(out.independent_validation_performed)
                for flag in case['qualifications']:
                    if flag!='positive_mean_range_crosses_zero':self.assertIn(flag,out.qualifications)
    def test_source_files_pinned_without_revision(self):
        data=json.loads((ROOT/'tests/fixtures/prediction_oracles.json').read_text())
        for name,digest in data['source_pins'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
    def test_positive_contrast_with_declining_surface_is_contrary(self):
        out=decide(result('-0.1','-0.2'))
        self.assertEqual(out.outcome,'contrary')
        self.assertIn('negative_retained:surface_gain',out.reasons)
        self.assertEqual(out.directions['p1_proxy_gain_contrast']['retained_direction'],'positive')
    def test_negative_structural_gain_can_support_joint_prediction(self):
        self.assertEqual(decide(result('0.1','-0.2')).outcome,'supporting')
    def test_strict_zero_does_not_add_equivalence_claim(self):
        out=decide(result('0','0'))
        self.assertEqual(out.outcome,'inconclusive');self.assertEqual(out.directions['surface_gain']['observed_direction'],'zero')
        self.assertNotIn('equivalent',repr(out))
    def test_exact_small_effect_keeps_small_magnitude(self):
        out=decide(result('1e-30','0'))
        self.assertEqual(out.outcome,'supporting')
        self.assertEqual(out.directions['surface_gain']['mean'].exact_ratio,(1,10**30))
        self.assertIn('sign_does_not_establish_practical_importance',out.qualifications)
    def test_numerical_sign_instability_withholds(self):
        out=decide(result('1e-400','0'));self.assertEqual(out.outcome,'not_evaluated')
    def test_negative_tiny_effect_is_not_treated_as_zero(self):
        out=decide(result('-1e-30','0'));self.assertEqual(out.outcome,'contrary')
    def test_quality_flag_never_replaces_primary(self):
        out=decide(result(),clean_quality_comparable=False)
        self.assertEqual(out.outcome,'supporting');self.assertFalse(out.clean_quality_comparable)
        self.assertIn('clean_quality_comparable_P1_unavailable',out.qualifications)
    def test_ceiling_qualifies_support_and_contrary_symmetrically(self):
        for value,expected in [('0.02','supporting'),('-0.02','contrary')]:
            out=decide(result(value),qualifications=['surface_proxy_near_ceiling','registered_class_ceiling_observed'])
            self.assertEqual(out.outcome,expected);self.assertIn('surface_proxy_near_ceiling',out.qualifications)
    def test_degenerate_range_does_not_establish_certainty(self):
        out=decide(result());self.assertIn('degenerate_range_is_not_general_certainty',out.qualifications)
    def test_missing_gate_keeps_directions_separate(self):
        out=decide(result(gated=False));self.assertEqual(out.outcome,'not_evaluated')
        self.assertEqual(out.directions['surface_gain']['observed_direction'],'positive')
        self.assertEqual(out.directions['surface_gain']['retained_direction'],'positive')
    def test_missing_one_p5_comparator_preserves_other(self):
        a=decide(result(p5=2,pair='C-A'));b=decide(result(p5=1,pair='C-B',gated=False))
        full,mixed=p.combine_p5((a,b),material_role='fixture')
        self.assertEqual(a.outcome,'supporting');self.assertEqual(full.outcome,'not_evaluated');self.assertTrue(mixed)
    def test_reversed_comparator_storage_order_does_not_change_pattern(self):
        a=decide(result(p5=1,pair='C-A'));b=decide(result(p5=-1,pair='C-B'))
        self.assertEqual(p.combine_p5((a,b),material_role='fixture'),p.combine_p5((b,a),material_role='fixture'))
    def test_incomplete_and_duplicate_p5_inputs_rejected(self):
        a=decide(result(p5=1,pair='C-A'))
        for xs in ((),(a,),(a,a)):
            with self.assertRaises(InputError):p.combine_p5(xs,material_role='fixture')
    def test_four_outcome_vocabulary_has_no_mixed_fifth_state(self):
        self.assertEqual(p.OUTCOMES,('supporting','contrary','inconclusive','not_evaluated'))
    def test_subset_never_replaces_six_block_primary(self):
        out=decide(result(['0.1','0.3'],'0',blocks=('P01','P03'),subset=True))
        self.assertEqual(out.outcome,'not_evaluated');self.assertIn('full_six_block_target_not_available',out.reasons)
        self.assertEqual(out.actual_blocks,('P01','P03'))
    def test_single_block_has_direction_but_no_verdict(self):
        out=decide(result('0.1',blocks=('P01',),subset=True))
        self.assertEqual(out.outcome,'not_evaluated');self.assertEqual(out.directions['surface_gain']['observed_direction'],'positive')
    def test_confirmatory_label_does_not_promote_fixture_assumption(self):
        out=p.evaluate_endpoint(result(),material_role='confirmatory')
        self.assertEqual(out.outcome,'not_evaluated');self.assertIn('fixture_assumptions_cannot_support_real_study',out.reasons)
    def test_pilot_and_descriptive_cannot_claim_confirmation(self):
        for role in ('pilot','descriptive'):
            out=p.evaluate_endpoint(result(),material_role=role)
            self.assertEqual(out.outcome,'not_evaluated');self.assertIn('nonconfirmatory_scope',out.reasons)
    def test_secondary_question_cannot_replace_registered_primary(self):
        r=result();r=replace(r,source_summary=replace(r.source_summary,question='secondary:k5'))
        with self.assertRaises(InputError):decide(r)
    def test_no_pvalues_population_confidence_or_overall_score(self):
        for module in (p,u):
            for attr in ('p_value','familywise_significance','overall_score','train','execute','generate_candidates'):
                self.assertFalse(hasattr(module,attr))
    def test_wrong_prediction_api_type_rejected(self):
        with self.assertRaises(InputError):p.evaluate_predictions({})
        with self.assertRaises(InputError):p.evaluate_endpoint({},material_role='fixture')


class IntervalBoundaryTests(unittest.TestCase):
    """Explicit range fixtures test strict-boundary routing, not resampling adequacy."""
    def substitute(self,r,name,*,lower=None,upper=None,**changes):
        intervals={k:dict(v) for k,v in r.intervals.items()};row=intervals[name];unit=row['mean'].unit
        if lower is not None:row['lower']=number(name,unit,Fraction(lower))
        if upper is not None:row['upper']=number(name,unit,Fraction(upper))
        row.update(changes)
        return replace(r,intervals=freeze(intervals))
    def test_positive_lower_touches_zero_is_inconclusive(self):
        r=self.substitute(result(),'surface_gain',lower='0')
        self.assertEqual(decide(r).outcome,'inconclusive')
    def test_negative_upper_touches_zero_is_inconclusive(self):
        r=result('-0.1','-0.2');r=self.substitute(r,'surface_gain',upper='0')
        self.assertEqual(decide(r).outcome,'inconclusive')
    def test_crossing_interval_is_inconclusive(self):
        r=self.substitute(result(),'p1_proxy_gain_contrast',lower='-0.1')
        self.assertEqual(decide(r).outcome,'inconclusive')
    def test_negative_required_direction_wins_over_other_inconclusive(self):
        r=result('-0.1','-0.2');r=self.substitute(r,'p1_proxy_gain_contrast',lower='-0.2')
        self.assertEqual(decide(r).outcome,'contrary')
    def test_reversed_bounds_are_unavailable(self):
        r=self.substitute(result(),'surface_gain',lower='0.2',upper='0.1')
        self.assertEqual(decide(r).outcome,'not_evaluated')
    def test_missing_required_interval_is_not_zero(self):
        r=result();rows=dict(r.intervals);del rows['surface_gain']
        out=decide(replace(r,intervals=freeze(rows)));self.assertEqual(out.outcome,'not_evaluated')
        self.assertEqual(out.directions['surface_gain']['observed_direction'],'positive')
    def test_foreign_replay_or_wrong_replica_count_rejected(self):
        for changes in ({'replay_sha256':'0'*64},{'replicate_count':1999},{'block_count':5},{'interval_scope':'population_confidence'}):
            r=self.substitute(result(),'surface_gain',**changes)
            self.assertEqual(decide(r).outcome,'not_evaluated')
    def test_interval_mean_must_equal_registered_mean(self):
        r=self.substitute(result(),'surface_gain',mean=number('surface_gain','u',Fraction(1,5)))
        self.assertEqual(decide(r).outcome,'not_evaluated')


class Step5MatrixTests(unittest.TestCase):
    def test_stage_bindings_cover_every_actual_new_method(self):
        m=read_matrix();actual=[]
        for mod in ('test_uncertainty','test_predictions'):
            for cls in ast.parse((ROOT/'tests'/f'{mod}.py').read_text()).body:
                if isinstance(cls,ast.ClassDef):
                    actual.extend(f'tests.{mod}.{cls.name}.{method.name}' for method in cls.body if isinstance(method,ast.FunctionDef) and method.name.startswith('test_'))
        self.assertEqual(set(actual),set(m['stage_bindings']['5']['test_bindings']))
        self.assertGreaterEqual(m['delivery']['step'],5);self.assertEqual(len(m['predecessor']['test_ids']),503)
        deliveries=m['delivery'].get('history',[])+[m['delivery']]
        self.assertEqual(len([x for x in deliveries if x['step']==5]),1)
    def test_only_completed_replay_family_closes_without_final_report(self):
        m=read_matrix();vt={x['id']:x for x in m['vt_obligations']}
        self.assertEqual(vt['VT-39']['implementation_status'],'implemented')
        for i in ('VT-40','VT-41','VT-42','VT-43','VT-44','VT-45','VT-50'):
            self.assertEqual(vt[i]['implementation_status'],'partial')
        self.assertEqual((ROOT/'structdet_bench/comparison_pipeline.py').exists(),m['delivery']['step']>=6)
    def test_scope_keeps_real_evidence_unperformed(self):
        m=read_matrix();self.assertEqual(m['evidence_status'],'not_supplied');self.assertEqual(m['deferred_status'],'deferred')
        self.assertEqual(len(m['catalogues']['vt']),54);self.assertEqual(len(m['catalogues']['rf']),36)


class BindingEncodingTests(unittest.TestCase):
    def test_dictionary_is_explicit_and_expands_without_introspection(self):
        from tests import phase2_helpers as h
        raw=h.read_json(h.MATRIX_PATH);decoded=h.expand_matrix(raw)
        storage=raw['delivery']['binding_storage']
        self.assertEqual(storage['encoding'],'explicit_binding_dictionary_v1')
        self.assertEqual(decoded,h.expand_matrix(decoded))
        self.assertEqual(len(decoded['stage_bindings']['5']['test_bindings']),len(set(decoded['stage_bindings']['5']['test_bindings'])))
        self.assertTrue(all(isinstance(x,str) for x in decoded['stage_bindings']['5']['test_bindings']))
    def test_corrupt_index_bool_and_pool_entries_fail(self):
        import copy
        from tests import phase2_helpers as h
        raw=h.read_json(h.MATRIX_PATH)
        for i in (-1,True,999999):
            bad=copy.deepcopy(raw);bad['stage_bindings']['5']['test_bindings']['indices'][0]=i
            with self.assertRaises(ValueError):h.expand_matrix(bad)
        bad=copy.deepcopy(raw);bad['delivery']['binding_storage']['pool'][0]='__import__("os")'
        with self.assertRaises(ValueError):h.expand_matrix(bad)
    def test_binding_hash_and_complete_matrix_hash_fail_closed(self):
        import copy
        from tests import phase2_helpers as h
        raw=h.read_json(h.MATRIX_PATH)
        bad=copy.deepcopy(raw);bad['stage_bindings']['5']['test_bindings']['sha256']='0'*64
        with self.assertRaises(ValueError):h.expand_matrix(bad)
        bad=copy.deepcopy(raw);bad['delivery']['binding_storage']['expanded_sha256']='0'*64
        with self.assertRaises(ValueError):h.expand_matrix(bad)
    def test_dictionary_never_marks_external_evidence_as_performed(self):
        m=read_matrix()
        self.assertEqual(m['evidence_status'],'not_supplied')
        self.assertEqual(m['deferred_status'],'deferred')
        self.assertTrue(all(x['evidence_status']=='not_supplied' for x in m['vt_obligations']))
