"""Step 4 conformance from stipulated records and independent count oracles.

No model outputs, independent reviewers or candidate execution are supplied.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import ast
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import comparisons as mod
from structdet_bench.comparisons import (BLOCKS, P1_NAMES, Gate, Number, compare_study,
    difference, number, ratio_gate, summarize_blocks)
from structdet_bench.comparison_records import review_comparison
from structdet_bench.contracts import InputError, freeze
from structdet_bench.local_io import load_bundle
from structdet_bench.populations import Ratio, build_populations
from structdet_bench.text_diagnostics import (diagnose_cells, method_from_record,
    limits_from_record, SURFACE, STRUCTURAL)
from tests.helpers import ROOT, tagged, record_ref, rewrite_evidence_bundle, support_record
from tests.phase2_helpers import populated_comparison_fixture, read_matrix


def select(out, pair='B-A', view='classified_all', block='P01'):
    return next(x for x in out.blocks if (x.block_id,x.condition_pair,x.view)==(block,pair,view))


def gate(block,name): return next(g for g in block.gates if g.name==name)


class ExactGateTests(unittest.TestCase):
    def test_source_pinned_gate_cases(self):
        data=json.loads((ROOT/'tests/fixtures/comparison_cases.json').read_text())
        for file,digest in data['gate_source_pins'].items():
            self.assertEqual(hashlib.sha256((ROOT/file).read_bytes()).hexdigest(),digest)
        for c in data['gate_cases']:
            with self.subTest(case=c['case_id']):
                g=ratio_gate(c['name'],Ratio(*c['observed'],c['ratio_status']),Fraction(*c['threshold']),
                             maximum=c.get('maximum',False),conditional_empty=c.get('conditional',False))
                self.assertEqual(g.status,c['expected'])
                self.assertEqual(g.observed['numerator'],c['observed'][0])
                self.assertEqual(g.observed['denominator'],c['observed'][1])
    def test_classification_exact_equality(self):
        self.assertTrue(ratio_gate('coverage',Ratio(18,20,'available'),Fraction(9,10)).passes)
        self.assertFalse(ratio_gate('coverage',Ratio(17,20,'available'),Fraction(9,10)).passes)
    def test_decisive_validity_equality(self):
        self.assertTrue(ratio_gate('decisive',Ratio(19,20,'available'),Fraction(19,20)).passes)
        self.assertFalse(ratio_gate('decisive',Ratio(18,20,'available'),Fraction(19,20)).passes)
    def test_conditional_zero_preserves_undefined(self):
        g=ratio_gate('valid',Ratio(0,0,'undefined'),Fraction(9,10),conditional_empty=True)
        self.assertEqual(g.status,'conditional_not_applicable');self.assertEqual(g.observed['status'],'undefined')
        self.assertIsNone(Ratio(0,0,'undefined').value)
    def test_unknown_is_not_conditional_nonapplicability(self):
        g=ratio_gate('valid',Ratio(None,None,'unavailable'),Fraction(9,10),conditional_empty=True)
        self.assertEqual(g.status,'unresolved');self.assertFalse(g.passes)
    def test_invalid_count_types_are_not_accepted(self):
        for ratio in [Ratio(True,20,'available'),Ratio(21,20,'available'),Ratio(-1,20,'available'),
                      Ratio(0,0,'available'),Ratio(0.9,1,'available'),Ratio(20,20,'unknown')]:
            self.assertFalse(ratio_gate('bad',ratio,Fraction(9,10)).passes)
    def test_threshold_comparison_keeps_more_precision_than_float(self):
        n=10**40
        self.assertTrue(ratio_gate('x',Ratio(9*n,10*n,'available'),Fraction(9,10)).passes)
        self.assertFalse(ratio_gate('x',Ratio(9*n-1,10*n,'available'),Fraction(9,10)).passes)
    def test_nonrequired_quality_still_records_failure(self):
        g=ratio_gate('quality',Ratio(0,20,'available'),Fraction(4,5),required=False)
        self.assertFalse(g.required);self.assertFalse(g.passes);self.assertEqual(g.status,'failed')
    def test_gate_api_types_and_unknowns(self):
        for args in [('x',{},Fraction(1,2)),('x',Ratio(1,2,'available'),.5),('x',Ratio(1,2,'available'),Fraction(2))]:
            with self.assertRaises(InputError):ratio_gate(*args)


class ArithmeticTests(unittest.TestCase):
    def test_subtracts_in_requested_direction_exactly(self):
        a=number('L','pair',Fraction(1,10));b=number('L','pair',Fraction(3,10))
        self.assertEqual(difference(b,a,'gain').exact_ratio,(1,5))
        self.assertEqual(difference(a,b,'gain').exact_ratio,(-1,5))
    def test_units_and_estimands_cannot_be_mixed(self):
        a=number('entropy','nats',0.7);b=number('distance','pair',.7)
        self.assertEqual(difference(a,b,'bad').result_status,'unavailable')
        self.assertEqual(difference(a,number('other_entropy','nats',.2),'bad').result_status,'unavailable')
    def test_undefined_unavailable_and_zero_differ(self):
        a=number('L','pair',Fraction(0));b=number('L','pair',status='undefined')
        self.assertEqual(difference(a,a,'delta').value,0)
        self.assertEqual(difference(a,b,'delta').result_status,'undefined')
        self.assertEqual(difference(a,number('L','pair',status='unavailable'),'delta').result_status,'unavailable')
    def test_no_tolerance_redefines_a_small_difference(self):
        a=number('L','pair',Fraction(1,10));b=number('L','pair',Fraction(1,10)+Fraction(1,10**30))
        d=difference(b,a,'delta');self.assertEqual(d.exact_ratio,(1,10**30));self.assertGreater(d.value,0)
    def test_exact_limit_failure_never_returns_a_partial_difference(self):
        a=number('L','pair',Fraction(1,17));b=number('L','pair',Fraction(1,19))
        d=difference(a,b,'delta',max_exact_bits=5)
        self.assertEqual(d.result_status,'unavailable');self.assertIsNone(d.value)
        self.assertIn('max_exact_bits_exceeded',d.reasons)
    def test_nonfinite_or_unrepresentable_numbers_are_withheld(self):
        for v in (float('inf'),float('nan'),True,None,Fraction(1,10**400)):
            self.assertEqual(number('x','unit',v).result_status,'unavailable')
    def test_float_entropy_differences_are_not_display_rounded(self):
        a=number('H','nats',math.log(2));b=number('H','nats',math.log(3))
        self.assertEqual(difference(b,a,'delta').value,math.log(3)-math.log(2))
    def test_surface_ceiling_exactly_point_nine_five_is_only_a_flag(self):
        value=number('L','pair',Fraction(19,20))
        self.assertIn('surface_proxy_near_ceiling',mod.ceiling_flags(value))
        self.assertEqual(value.exact_ratio,(19,20))
        self.assertEqual(mod.ceiling_flags(number('L','pair',Fraction(19,20)-Fraction(1,10**30))),())
        self.assertEqual(mod.ceiling_flags(number('L','pair',status='unavailable')),())

    def test_wrong_number_api_rejected(self):
        with self.assertRaises(InputError):difference({},number('L','pair',1),'delta')


class StudyFixture(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
    def build(self,**kwargs):
        self.path,self.obs,self.support,self.man=populated_comparison_fixture(self.root,**kwargs)
        return self.get()
    def get(self,*,no_text=False,subset=True):
        self.path=rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)
        self.bundle=load_bundle(self.path);self.pops=build_populations(self.bundle)
        r=review_comparison(self.bundle)
        self.ds=() if no_text else diagnose_cells(self.bundle,self.pops.cells,method_from_record(r.configuration['text_method']),limits=limits_from_record(r.configuration['limits']))
        return compare_study(self.bundle,self.pops,self.ds,include_descriptive_subset=subset)
    def study(self,cid):
        return next(x['payload']['extensions']['study_binding'] for x in self.support if x['record_id']=='study-'+cid)
    def sample(self,cid,i):return next(r for r in self.obs if r['record_id']==f'{cid}-s{i}')


class EndpointTests(StudyFixture):
    def test_real_text_operands_produce_independent_eight_nineteenths(self):
        out=self.build();p=select(out)
        # 10 vs 10 texts: 100 differing pairs, distance 4/5; 190 pairs total.
        self.assertEqual(p.values['surface_gain'].exact_ratio,(8,19))
        self.assertEqual(p.values['structural_gain'].exact_ratio,(0,1))
        self.assertEqual(p.values['p1_proxy_gain_contrast'].exact_ratio,(8,19))
        self.assertTrue(p.eligible_before_resampling)
        self.assertEqual(p.contrasts['surface_gain'].minuend.population_size,20)
        self.assertEqual(len(p.contrasts['surface_gain'].minuend.counted_ids),20)
        self.assertEqual(p.prediction_status,'not_implemented')
    def test_p5_both_comparators_and_views_keep_names_and_budget(self):
        out=self.build()
        for pair in ('C-A','C-B'):
            p=select(out,pair,'classified_valid');self.assertEqual(p.values['p5_valid_distinct_k_delta'].exact_ratio,(1,1))
            self.assertTrue(p.eligible_before_resampling);self.assertEqual(p.role,'primary')
            con=p.contrasts['p5_valid_distinct_k_delta'];self.assertEqual(con.k,20)
            self.assertEqual(len(con.minuend.selected_ids),20)
            self.assertEqual(select(out,pair).role,'sensitivity_or_companion')
    def test_remove_all_proxy_text_does_not_veto_p5(self):
        self.build(texts={c:[None]*20 for c in ('P01-A','P01-B','P01-C')})
        out=self.get()
        self.assertFalse(select(out).eligible_before_resampling)
        for pair in ('C-A','C-B'):
            p=select(out,pair,'classified_valid');self.assertTrue(p.eligible_before_resampling)
            self.assertEqual(p.values['p5_valid_distinct_k_delta'].value,1)
            self.assertFalse(any('proxy_text_coverage' in g.name for g in p.gates))
    def test_no_diagnostic_computation_is_required_for_p5(self):
        self.build();out=self.get(no_text=True)
        self.assertTrue(select(out,'C-A','classified_valid').eligible_before_resampling)
        self.assertFalse(select(out).eligible_before_resampling)
    def test_proxy_table_mismatch_limits_p1_without_p5_change(self):
        self.build();self.man['analysis_config']['extensions']['comparison']['text_method']['white_space_sha256']=tagged('0'*64)
        out=self.get();self.assertFalse(select(out).eligible_before_resampling)
        self.assertEqual(select(out).values['surface_gain'].result_status,'unavailable')
        self.assertTrue(select(out,'C-A','classified_valid').eligible_before_resampling)
    def test_complete_unclassified_is_known_zero_not_missing_position(self):
        out=self.build(labels={c:[None]*20 for c in ('P01-A','P01-B','P01-C')})
        p=select(out,'C-A','classified_valid')
        self.assertTrue(gate(p,'C.intended_positions').passes)
        self.assertEqual(p.values['p5_valid_distinct_k_delta'].value,0)
        self.assertFalse(gate(p,'C.classification_coverage').passes)
        self.assertFalse(p.eligible_before_resampling)
    def test_nineteen_positions_do_not_become_matched_twenty(self):
        out=self.build(labels={'P01-A':['SORT-ADJ']*19})
        p=select(out,'C-A','classified_valid');self.assertFalse(gate(p,'A.intended_positions').passes)
        self.assertEqual(p.values['p5_valid_distinct_k_delta'].result_status,'unavailable')
        self.assertEqual(len(p.contrasts['p5_valid_distinct_k_delta'].subtrahend.selected_ids),19)
        self.assertFalse(select(out).eligible_before_resampling)
    def test_incomplete_last_group_preserves_earlier_companion(self):
        out=self.build(labels={'P01-A':['SORT-ADJ']*19})
        p=select(out,'C-A','classified_valid')
        ks={c.k:c.result for c in p.companions if c.name=='structural_distinct_k_delta'}
        self.assertEqual(ks[5].result_status,'available');self.assertEqual(ks[20].result_status,'unavailable')
    def test_low_quality_primary_p1_remains_separate_from_clean_description(self):
        out=self.build(validity={'P01-A':['valid']*16+['invalid']*4,'P01-B':['valid']*13+['invalid']*7})
        p=select(out);self.assertTrue(p.eligible_before_resampling);self.assertFalse(p.clean_quality_eligible)
        self.assertIn('clean_quality_comparable_P1_unavailable',p.qualifications)
        self.assertIn('B_minus_A_validity_loss',p.qualifications)
        self.assertFalse(gate(p,'B.validity_floor').required);self.assertFalse(gate(p,'quality_band').required)
    def test_zero_valid_outputs_all_view_can_remain_descriptive_and_eligible(self):
        out=self.build(validity={c:['invalid']*20 for c in ('P01-A','P01-B','P01-C')})
        p=select(out);self.assertTrue(p.eligible_before_resampling)
        self.assertEqual(gate(p,'A.classified_valid_coverage').status,'conditional_not_applicable')
        self.assertFalse(select(out,view='classified_valid').eligible_before_resampling)
        self.assertFalse(select(out,'C-A','classified_valid').eligible_before_resampling)
    def test_p5_quality_floor_and_band_are_exact_per_block(self):
        out=self.build(validity={'P01-A':['valid']*16+['invalid']*4,'P01-C':['valid']*18+['invalid']*2})
        p=select(out,'C-A','classified_valid');self.assertTrue(p.eligible_before_resampling)
        self.assertTrue(gate(p,'quality_band').passes);self.assertEqual(gate(p,'quality_band').observed['numerator'],1)
        self.assertEqual(gate(p,'quality_band').observed['denominator'],10)
    def test_superior_validity_can_fail_match_without_deleting_successes(self):
        out=self.build(validity={'P01-A':['valid']*17+['invalid']*3})
        p=select(out,'C-A','classified_valid');self.assertFalse(p.eligible_before_resampling)
        self.assertFalse(gate(p,'quality_band').passes)
        self.assertEqual(p.values['p5_valid_distinct_k_delta'].value,1)
        self.assertEqual(p.contrasts['p5_valid_distinct_k_delta'].minuend.population_size,20)
    def test_text_coverage_at_nineteen_of_twenty_is_accepted(self):
        out=self.build(texts={'P01-A':['a b c']*19+[None]})
        p=select(out);self.assertTrue(gate(p,'A.proxy_text_coverage').passes)
        self.assertTrue(p.eligible_before_resampling)
        self.assertEqual(len(p.contrasts['surface_gain'].subtrahend.counted_ids),19)
        self.assertEqual(p.contrasts['surface_gain'].subtrahend.counted_ids,p.contrasts['structural_gain'].subtrahend.counted_ids)
    def test_insufficient_text_coverage_keeps_numbers_but_restricts_primary(self):
        out=self.build(texts={'P01-A':['a b c']*18+[None]*2})
        p=select(out);self.assertFalse(gate(p,'A.proxy_text_coverage').passes)
        self.assertEqual(p.values['surface_gain'].result_status,'available')
        self.assertFalse(p.eligible_before_resampling)
    def test_decisive_validity_and_classification_failures_not_hidden(self):
        out=self.build(labels={'P01-A':['SORT-ADJ']*17+[None]*3},validity={'P01-B':['valid']*18+['undetermined']*2})
        p=select(out);self.assertFalse(gate(p,'A.classification_coverage').passes)
        self.assertFalse(gate(p,'B.decisive_validity_coverage').passes)
        self.assertFalse(p.eligible_before_resampling)
    def test_valid_only_sensitivity_uses_its_own_subsets(self):
        out=self.build(validity={'P01-B':['valid' if i%2==0 else 'invalid' for i in range(20)]})
        a=select(out);v=select(out,view='classified_valid')
        self.assertEqual(a.values['surface_gain'].exact_ratio,(8,19))
        self.assertEqual(v.values['surface_gain'].exact_ratio,(0,1))
        self.assertEqual(len(v.contrasts['surface_gain'].minuend.counted_ids),10)
    def test_core_companions_keep_units_and_class_aligned_zeros(self):
        out=self.build();p=select(out,'C-A','classified_valid')
        h=next(x for x in p.companions if x.name=='structural_entropy_nats_delta')
        self.assertEqual(h.result.unit,'nats');self.assertAlmostEqual(h.result.value,math.log(2))
        rows={r['class_id']:r for r in p.frequencies}
        self.assertEqual(rows['SORT-MERGE']['minuend']['frequency'].value,0)
        self.assertEqual(rows['SORT-INS']['delta'].exact_ratio,(1,2))
        self.assertEqual(rows['SORT-ADJ']['delta'].exact_ratio,(-1,2))
    def test_registry_ceiling_is_a_flag_without_new_classes(self):
        from structdet_bench.contracts import CLASS_IDS
        labels=list(CLASS_IDS)*2+list(CLASS_IDS[:4])
        out=self.build(labels={'P01-C':labels});p=select(out,'C-A','classified_valid')
        self.assertIn('registered_class_ceiling_observed',p.qualifications)
        self.assertEqual(len(p.frequencies),8)
    def test_workload_exhaustion_does_not_change_p5(self):
        self.build();self.man['analysis_config']['extensions']['comparison']['limits']['max_pairs']=1
        out=self.get();self.assertFalse(select(out).eligible_before_resampling)
        self.assertTrue(select(out,'C-A','classified_valid').eligible_before_resampling)
        self.assertEqual(select(out).values['surface_gain'].result_status,'unavailable')
    def test_finite_exact_limit_failure_retains_operands(self):
        self.build();self.man['analysis_config']['extensions']['comparison']['limits']['max_exact_bits']=3
        out=self.get();p=select(out)
        self.assertFalse(p.eligible_before_resampling)
        self.assertEqual(p.values['surface_gain'].result_status,'unavailable')
        self.assertEqual(p.contrasts['surface_gain'].minuend.population_size,20)


class CompatibilityTests(StudyFixture):
    def test_missing_c_does_not_veto_p1(self):
        self.build();self.man['cells']=[c for c in self.man['cells'] if c['condition_id']!='C']
        out=self.get();self.assertTrue(select(out).eligible_before_resampling)
        self.assertFalse(select(out,'C-A','classified_valid').eligible_before_resampling)
    def test_unsupported_b_temperature_leaves_ca(self):
        self.build();self.study('P01-B')['controls']['temperature']['enforcement']='unsupported'
        out=self.get();self.assertFalse(select(out).eligible_before_resampling)
        self.assertFalse(select(out,'C-B','classified_valid').eligible_before_resampling)
        self.assertTrue(select(out,'C-A','classified_valid').eligible_before_resampling)
        self.assertEqual(select(out).contrasts['surface_gain'].minuend.number.result_status,'available')
    def test_incompatible_cap_units_withhold_tagged_contrast_only(self):
        self.build();self.study('P01-B')['cap']['convention']=tagged('includes_hidden_reasoning')
        out=self.get();p=select(out)
        self.assertEqual(p.values['surface_gain'].result_status,'unavailable')
        self.assertEqual(p.contrasts['surface_gain'].minuend.number.result_status,'available')
        self.assertTrue(select(out,'C-A','classified_valid').eligible_before_resampling)
    def test_unknown_checkpoint_retains_qualified_arithmetic(self):
        self.build();self.man['cells'][1]['checkpoint_identifier']=tagged(state='unknown')
        out=self.get();p=select(out)
        self.assertEqual(p.values['surface_gain'].result_status,'available');self.assertFalse(p.eligible_before_resampling)
        self.assertIn('descriptive_numbers_do_not_establish_endpoint_eligibility',p.qualifications)
    def test_known_checkpoint_change_withholds_tagged_contrast(self):
        self.build();self.man['cells'][1]['checkpoint_identifier']=tagged('DIFFERENT')
        p=select(self.get());self.assertEqual(p.values['surface_gain'].result_status,'unavailable')
    def test_shared_frame_mismatch_preserves_individual_metrics(self):
        self.build();fr=deepcopy(self.man['frames'][0]);fr.update(record_id='frame2',frame_id='frame2',task_context='Different specified domain')
        self.man['frames'].append(fr);self.man['cells'][1]['frame_id']='frame2'
        for r in self.obs:
            if r['record_type']=='assignment' and r['sample_id'].startswith('P01-B-'):r['frame_id']='frame2'
        for r in self.support:
            if r['record_id'].startswith('e-P01-B-'):r['payload']['scope_refs']=[record_ref('frame','frame2')]
        out=self.get();p=select(out)
        self.assertFalse(gate(p,'shared_frame').passes)
        self.assertEqual(p.values['surface_gain'].result_status,'unavailable')
        self.assertEqual(p.contrasts['surface_gain'].minuend.number.result_status,'available')
    def test_stale_populations_cannot_reuse_old_label_evidence(self):
        self.build();oldpops=self.pops;oldds=self.ds
        next(r for r in self.support if r['record_id']=='e-P01-A-a1')['payload']['state']='withdrawn'
        fresh=load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))
        out=compare_study(fresh,oldpops,oldds)
        self.assertFalse(gate(select(out),'population_snapshot_binding').passes)
        self.assertEqual(select(out).values['surface_gain'].result_status,'unavailable')
    def test_stale_text_diagnostic_is_not_rebound_to_new_population(self):
        self.build();oldds=self.ds
        next(r for r in self.support if r['record_id']=='e-P01-A-a1')['payload']['state']='withdrawn'
        out=self.get();new=compare_study(self.bundle,self.pops,oldds)
        self.assertEqual(select(new).values['surface_gain'].result_status,'unavailable')
        self.assertIn('text_population_or_revision_mismatch',select(new).contrasts['surface_gain'].subtrahend.number.reasons)
    def test_raw_text_change_requires_recomputed_diagnostics(self):
        self.build();old=self.ds
        self.sample('P01-A',1)['output_ref']=tagged(state='unavailable',reason='Removed proxy')
        self.get();out=compare_study(self.bundle,self.pops,old)
        self.assertEqual(select(out).values['surface_gain'].result_status,'unavailable')
    def test_duplicate_diagnostic_or_population_context_rejected(self):
        self.build()
        with self.assertRaises(InputError):compare_study(self.bundle,self.pops,self.ds+(self.ds[0],))
        with self.assertRaises(InputError):compare_study(self.bundle,replace(self.pops,cells=self.pops.cells+(self.pops.cells[0],)),self.ds)
    def test_wrong_method_context_is_not_silently_relabelled(self):
        self.build();bad=replace(self.ds[0],method=replace(self.ds[0].method,unicode_category_version='14.0.0'))
        ds=(bad,)+self.ds[1:];out=compare_study(self.bundle,self.pops,ds)
        self.assertEqual(select(out).values['surface_gain'].result_status,'unavailable')
        self.assertTrue(select(out,'C-A','classified_valid').eligible_before_resampling)
    def test_missing_or_inconsistent_extraction_blocks_count_comparison(self):
        self.build();self.sample('P01-C',1)['extraction_rule_version']=tagged('other-method')
        p=select(self.get(),'C-A','classified_valid')
        self.assertEqual(p.values['p5_valid_distinct_k_delta'].result_status,'unavailable')
    def test_question_omission_preserves_nonrequested_scope(self):
        self.build();self.man['analysis_config']['extensions']['comparison']['questions']=['P5']
        out=self.get();self.assertTrue(all(b.question=='P5' for b in out.blocks))
    def test_no_comparison_and_invalid_comparison_return_scoped_states(self):
        self.build();del self.man['analysis_config']['extensions']['comparison']
        bundle=load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man));p=build_populations(bundle)
        out=compare_study(bundle,p);self.assertFalse(out.requested);self.assertEqual(out.status,'not_requested')
        self.man['analysis_config']['extensions']['comparison']={}
        bundle=load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man));out=compare_study(bundle,build_populations(bundle))
        self.assertTrue(out.requested);self.assertEqual(out.status,'contract_error');self.assertEqual(out.blocks,())
    def test_private_records_and_actual_usage_retained_without_equality_claim(self):
        self.build();budget=next(x['payload'] for x in self.support if x['record_id']=='budget-P01-C');budget['actual']=tagged({'tokens':123,'hidden':None})
        p=select(self.get(),'C-A','classified_valid');self.assertTrue(p.eligible_before_resampling)
        self.assertEqual(p.sources[0].budget['actual']['value']['tokens'],123)
        self.assertNotIn('tokens',p.values)
    def test_unknown_dependence_is_retained_without_fabricated_interval(self):
        out=self.build();p=select(out)
        self.assertEqual(p.dependencies['resampling_record']['dependence_assessment_ref']['state'],'unknown')
        self.assertEqual(p.uncertainty_status,'not_estimated');self.assertFalse(hasattr(p,'confidence_interval'))
    def test_full_pipeline_components_remain_passive_after_loading(self):
        self.build()
        with ExitStack() as st:
            for name in ('builtins.open','socket.socket','urllib.request.urlopen','subprocess.Popen','os.system'):
                st.enter_context(patch(name,side_effect=AssertionError('unexpected active operation')))
            out=compare_study(self.bundle,self.pops,self.ds)
        self.assertTrue(select(out).eligible_before_resampling)
    def test_input_bytes_and_existing_m_contexts_not_modified(self):
        self.build();before={p.name:p.read_bytes() for p in self.root.iterdir()};state=repr(self.pops)
        out=compare_study(self.bundle,self.pops,self.ds)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.iterdir()});self.assertEqual(state,repr(self.pops))
        self.assertFalse(out.independent_validation_performed)
    def test_storage_order_does_not_create_a_different_experimental_order(self):
        old=self.build();self.obs.reverse();self.support.reverse();new=self.get()
        self.assertEqual(select(old).values,select(new).values)
        self.assertEqual(select(old).contrasts['surface_gain'].minuend.counted_ids,select(new).contrasts['surface_gain'].minuend.counted_ids)
    def test_nonfixture_declared_labels_do_not_supply_independent_evidence(self):
        self.build();self.man['data_role']='confirmatory'
        out=self.get();p=select(out)
        self.assertFalse(gate(p,'evidence_scope').passes)
        self.assertFalse(p.independent_validation_performed)
        self.assertIn('registration_not_supplied',gate(p,'evidence_scope').reasons)
    def test_independence_only_correction_keeps_arithmetic_and_restrictions(self):
        before=self.build()
        self.support.append(support_record('correction','independence-fix',effect='independence',action='withdraw',stage='applied',
            target_refs=[record_ref('frame','frame1')],reason=tagged('Stipulated independence claim withdrawn'),
            evidence_refs=[record_ref('evidence','e-P01-A-a1')],reviewer_refs=[record_ref('role','binding-reviewer')]))
        after=self.get();a,b=select(before),select(after)
        self.assertEqual(a.values,b.values)
        self.assertIn('supplied_evidence_claim_restrictions',b.qualifications)
        self.assertFalse(b.independent_validation_performed)
    def test_unsupported_penalties_keep_their_conditional_role(self):
        self.build()
        for cid in ('P01-A','P01-B'):
            for key in ('presence_penalty','frequency_penalty'):
                c=self.study(cid)['controls'][key]
                c['requested']=c['actual']=tagged(state='not_applicable',reason='Penalty control not exposed')
                c['enforcement']='unsupported'
        out=self.get();self.assertTrue(select(out).eligible_before_resampling)
    def test_stale_pair_membership_cannot_have_a_forged_denominator(self):
        self.build();broken=replace(self.ds[0],pair_count=1000)
        out=compare_study(self.bundle,self.pops,(broken,)+self.ds[1:])
        self.assertEqual(select(out).values['surface_gain'].result_status,'unavailable')
    def test_deployment_contradiction_does_not_get_global_ca_veto(self):
        self.build();self.study('P01-B')['deployment']['change_detected']=tagged(True)
        out=self.get();self.assertFalse(select(out).eligible_before_resampling)
        self.assertTrue(select(out,'C-A','classified_valid').eligible_before_resampling)

    def test_supplied_fixture_registration_cannot_hide_post_inspection(self):
        self.build()
        from tests.test_comparison_records import Fixture
        other=Fixture();other.cfg=self.man['analysis_config']['extensions']['comparison'];other.sup=self.support
        payload=other.registration()
        good=self.get();self.assertTrue(select(good).eligible_before_resampling)
        payload['registered_at']=tagged('2026-09-03T01:00:00+00:00')
        bad=self.get();self.assertFalse(gate(select(bad),'evidence_scope').passes)
        self.assertEqual(select(good).values,select(bad).values)
    def test_independence_correction_limits_claim_without_erasing_counts(self):
        self.build()
        self.support.append(support_record('correction','claim-fix',effect='independence',action='withdraw',stage='applied',
            target_refs=[record_ref('frame','frame1')],reason=tagged('Stipulated claim withdrawal'),
            evidence_refs=[record_ref('evidence','e-P01-A-a1')],reviewer_refs=[record_ref('role','binding-reviewer')]))
        out=self.get();p=select(out,'C-A','classified_valid')
        self.assertEqual(p.values['p5_valid_distinct_k_delta'].value,1)
        self.assertFalse(p.eligible_before_resampling)
        self.assertIn('active_evidence_correction',gate(p,'evidence_scope').reasons)

    def test_known_retry_keeps_record_and_does_not_add_sample(self):
        self.build();s=self.study('P01-A');s['automatic_retries']=tagged(True)
        out=self.get();p=select(out)
        self.assertFalse(p.eligible_before_resampling)
        self.assertEqual(len(p.contrasts['surface_gain'].subtrahend.selected_ids),20)


class SummaryTests(StudyFixture):
    def test_one_block_full_target_missing_and_opt_in_subset(self):
        out=self.build();summ=[s for s in out.summaries if s.condition_pair=='B-A' and s.view=='classified_all']
        full,sub=summ
        self.assertEqual(full.means['surface_gain'].result_status,'unavailable')
        self.assertEqual(full.included_blocks,('P01',));self.assertEqual(len(full.missing_blocks),5)
        self.assertFalse(full.full_target_complete);self.assertFalse(full.eligible_before_resampling)
        self.assertEqual(sub.means['surface_gain'].exact_ratio,(8,19))
        self.assertEqual(sub.scope,'available_block_descriptive_subset');self.assertEqual(sub.uncertainty_status,'not_estimated')
    def test_descriptive_subset_is_not_created_without_explicit_request(self):
        self.build();out=self.get(subset=False)
        self.assertEqual(len(out.summaries),6)
        self.assertTrue(all(s.scope=='full_intended_target' for s in out.summaries))
    def test_six_actual_text_blocks_have_exact_equal_block_means(self):
        out=self.build(blocks=BLOCKS)
        for s in out.summaries:
            self.assertEqual(s.included_blocks,BLOCKS);self.assertTrue(s.full_target_complete);self.assertTrue(s.eligible_before_resampling)
            expected=(8,19) if s.question=='P1' else (1,1)
            name='surface_gain' if s.question=='P1' else next(iter(s.means))
            self.assertEqual(s.means[name].exact_ratio,expected)
        self.assertEqual(len(out.summaries),6)
    def test_heterogeneous_actual_blocks_have_joint_means_without_row_weighting(self):
        out=self.build(blocks=('P01','P02'),texts={'P02-B':['a b c']*20})
        s=next(s for s in out.summaries if s.scope=='available_block_descriptive_subset' and s.condition_pair=='B-A' and s.view=='classified_all')
        self.assertEqual(s.included_blocks,('P01','P02'));self.assertEqual(s.means['surface_gain'].exact_ratio,(4,19))
        self.assertEqual(s.means['p1_proxy_gain_contrast'].exact_ratio,(4,19))
    def test_no_cherry_pick_of_positive_blocks_or_pooled_entropy(self):
        out=self.build();p=select(out)
        def fake(bid,surf,struct):
            return replace(p,block_id=bid,values=freeze({'surface_gain':number('surface_gain','pair',surf),
                'structural_gain':number('structural_gain','pair',struct),
                'p1_proxy_gain_contrast':number('p1_proxy_gain_contrast','pair',surf-struct)}))
        first=fake('X',Fraction(1,10),Fraction(0));second=fake('Y',Fraction(3,10),Fraction(0))
        # Explicitly limited MF-18 arithmetic fixture; no full-six claim.
        s=summarize_blocks((first,second),('X','Y'))
        self.assertEqual(s.means['surface_gain'].exact_ratio,(1,5))
        second=fake('Y',Fraction(-3,10),Fraction(0));s=summarize_blocks((first,second),('X','Y'))
        self.assertEqual(s.means['surface_gain'].exact_ratio,(-1,10));self.assertEqual(s.included_blocks,('X','Y'))
        self.assertEqual(s.weighting,'equal_prompt_block')
    def test_linked_p1_missing_operand_uses_identical_block_set(self):
        out=self.build();p=select(out)
        missing=replace(p,block_id='P02',values=freeze({**p.values,'structural_gain':number('structural_gain','pair',status='undefined')}))
        s=summarize_blocks((p,missing),descriptive_subset=True)
        self.assertEqual(s.included_blocks,('P01',))
        self.assertEqual(s.means['surface_gain'].exact_ratio,(8,19));self.assertIn('P02',s.missing_blocks)
    def test_failed_quality_does_not_select_a_favorable_subset(self):
        out=self.build();p=select(out,'C-A','classified_valid');bad=replace(p,block_id='P02',gates=p.gates+(Gate('extra_quality','failed'),))
        s=summarize_blocks((p,bad),('P01','P02'))
        self.assertEqual(s.included_blocks,('P01','P02'));self.assertEqual(s.means['p5_valid_distinct_k_delta'].value,1)
        self.assertIn('P02',s.gate_failures);self.assertFalse(s.eligible_before_resampling)
    def test_p5_comparators_keep_different_missing_block_lists(self):
        self.build(blocks=('P01','P02'));self.man['cells']=[r for r in self.man['cells'] if r['record_id']!='P02-B']
        out=self.get();summ={s.condition_pair:s for s in out.summaries if s.view=='classified_valid' and s.scope=='available_block_descriptive_subset'}
        self.assertEqual(summ['C-A'].included_blocks,('P01','P02'))
        self.assertEqual(summ['C-B'].included_blocks,('P01',))
    def test_bad_summary_scopes_and_duplicate_blocks_rejected(self):
        out=self.build();p=select(out)
        for rows,ids in [((p,p),BLOCKS),((p,),('P02',)),((p,select(out,'C-A','classified_valid')),BLOCKS),((p,),('P01','P01'))]:
            with self.assertRaises(InputError):summarize_blocks(rows,ids)
    def test_zero_available_blocks_yields_unavailable_not_zero_mean(self):
        out=self.build();p=select(out);bad=replace(p,values=freeze({k:number(k,v.unit,status='unavailable') for k,v in p.values.items()}))
        s=summarize_blocks((bad,),descriptive_subset=True)
        self.assertEqual(s.included_blocks,());self.assertIsNone(s.means['surface_gain'].value)
    def test_secondary_means_do_not_require_missing_p1_text(self):
        self.build(blocks=BLOCKS);out=self.get(no_text=True)
        mean=next(s for s in out.secondary_summaries if s.question=='secondary:structural_entropy_nats_delta'
                  and s.condition_pair=='C-A' and s.view=='classified_valid')
        self.assertAlmostEqual(mean.means['structural_entropy_nats_delta'].value,math.log(2))
        self.assertEqual(mean.included_blocks,BLOCKS)
        self.assertFalse(next(s for s in out.summaries if s.question=='P1').eligible_before_resampling)
    def test_two_block_declared_target_cannot_become_six_block_claim(self):
        out=self.build();p=select(out);second=replace(p,block_id='P02')
        s=summarize_blocks((p,second),('P01','P02'))
        self.assertEqual(s.means['surface_gain'].exact_ratio,(8,19))
        self.assertFalse(s.full_target_complete);self.assertFalse(s.eligible_before_resampling)
        self.assertEqual(s.scope,'declared_descriptive_target')
    def test_unequal_population_sizes_never_reweight_blocks(self):
        out=self.build(blocks=('P01','P02'),labels={'P02-A':['SORT-ADJ']*19,'P02-B':['SORT-ADJ']*19},
                       texts={'P02-B':['a b c']*19})
        s=next(s for s in out.summaries if s.scope=='available_block_descriptive_subset' and s.condition_pair=='B-A' and s.view=='classified_all')
        self.assertEqual(s.means['surface_gain'].exact_ratio,(4,19))
        self.assertIn('P02',s.gate_failures)

    def test_summary_limit_failure_has_no_float_fallback(self):
        out=self.build();p=select(out);s=summarize_blocks((p,),('P01',),max_exact_bits=3)
        self.assertIsNone(s.means['surface_gain'].value);self.assertFalse(s.eligible_before_resampling)


class Step4MatrixTests(unittest.TestCase):
    def test_current_step_and_all_actual_bindings(self):
        m=read_matrix()
        deliveries=m['delivery'].get('history',[])+[m['delivery']]
        self.assertEqual(len([x for x in deliveries if x['step']==4]),1)
        self.assertGreaterEqual(m['delivery']['step'],4)
        actual=[]
        for cls in ast.parse((ROOT/'tests/test_comparisons.py').read_text()).body:
            if isinstance(cls,ast.ClassDef):actual.extend('tests.test_comparisons.'+cls.name+'.'+f.name for f in cls.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_'))
        self.assertEqual(set(m['stage_bindings']['4']['test_bindings']),set(actual))
    def test_no_prediction_bootstrap_or_report_orchestrator_implemented(self):
        step=read_matrix()['delivery']['step']
        for name, first_step in (('uncertainty',5),('predictions',5),('comparison_pipeline',6)):
            self.assertEqual((ROOT/'structdet_bench'/f'{name}.py').exists(), step>=first_step)
        self.assertFalse(hasattr(mod,'resample'));self.assertFalse(hasattr(mod,'decide_p1'))
    def test_all_source_identities_and_external_evidence_boundaries_retained(self):
        m=read_matrix();self.assertEqual(len(m['vt_obligations']),26)
        self.assertEqual(m['evidence_status'],'not_supplied');self.assertEqual(m['deferred_status'],'deferred')
        self.assertEqual(len(m['catalogues']['vt']),54);self.assertEqual(len(m['predecessor']['test_ids']),503)
