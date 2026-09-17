"""Independent membership/ratio/prefix oracles from MET and HERO."""
from __future__ import annotations
import ast
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench.contracts import CLASS_IDS, InputError
from structdet_bench.local_io import load_bundle
from structdet_bench.populations import build_populations, prefix, accumulation
from tests.helpers import ROOT, population_bundle, rewrite_evidence_bundle, support_record, tagged, record_ref

A,B,C = 'SORT-ADJ','SORT-INS','SORT-MERGE'


class PopulationTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.path,self.obs,self.support,self.man=population_bundle(self.root,[A,A,B,B,None,C],
            validity=['valid','valid','invalid','undetermined','valid','valid'],group_sizes=(3,3))
        self.record('assignment','a6')['assignment_review_status']='provisional'
    def record(self,kind,rid):return next(r for r in self.obs if r['record_type']==kind and r['record_id']==rid)
    def get(self):return build_populations(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)))
    def cell(self):return self.get().cells[0]

    def test_mf07_exact_memberships(self):
        c=self.cell()
        self.assertEqual(c.populations['classified_all'].sample_ids,('s1','s2','s3','s4'))
        self.assertEqual(c.populations['classified_valid'].sample_ids,('s1','s2'))
        self.assertEqual({k:v for k,v in c.populations['classified_all'].class_counts.items() if v},{A:2,B:2})
    def test_mf07_all_five_ratios_keep_unreduced_accounting(self):
        c=self.cell();expected={
            'classification_coverage':(4,6),'valid_fraction_selected':(4,6),'decisive_validity_coverage':(5,6),
            'classified_valid_coverage':(2,4),'classified_valid_fraction':(2,4)}
        for name,(n,d) in expected.items():
            r=c.ratios[name];self.assertEqual((r.numerator,r.denominator),(n,d))
            self.assertEqual(r.value,Fraction(n,d));self.assertEqual(r.status,'available')
    def test_axes_overlap_and_each_reconciles_to_selected_inventory(self):
        c=self.cell()
        for counts in (c.assignment_status_counts,c.assignment_acceptance_counts,c.assignment_review_counts,c.validity_status_counts,c.validity_acceptance_counts):
            self.assertEqual(sum(counts.values()),6)
        self.assertEqual(c.validity_status_counts['undetermined'],1)
        self.assertEqual(c.assignment_acceptance_counts['unresolved'],1)
        self.assertEqual(c.assignment_acceptance_counts['withheld'],1)
        self.assertTrue(c.reason_counts_are_multireason)
    def test_validity_does_not_fill_unresolved_or_provisional_class(self):
        c=self.cell();self.assertNotIn('s5',c.populations['classified_all'].sample_ids)
        self.assertNotIn('s6',c.populations['classified_valid'].sample_ids)
        self.assertEqual(c.populations['classified_all'].class_counts[C],0)
    def test_registry_zeros_remain_and_never_add_observations(self):
        p=self.cell().populations['classified_all']
        self.assertEqual(tuple(p.class_counts),CLASS_IDS);self.assertEqual(sum(p.class_counts.values()),p.count)
    def test_known_empty_selection_has_undefined_ratios(self):
        sel=self.man['analysis_config']['selection'][0];sel['selected_sample_ids']=tagged([]);sel['sample_order']=tagged([])
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,0)
        self.assertTrue(all(r.status=='undefined' and r.value is None for r in c.ratios.values()))
    def test_wholly_unclassified_selection_remains_known_zero(self):
        for r in self.obs:
            if r['record_type']=='assignment':r.update(assignment_status='unclassified',structural_class_id=None)
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,0)
        self.assertEqual(c.ratios['classification_coverage'].value,Fraction(0,6))
        self.assertEqual(c.ratios['classified_valid_fraction'].status,'undefined')
    def test_all_invalid_can_still_have_structural_population(self):
        self.path,self.obs,self.support,self.man=population_bundle(self.root,[A]*4,validity=['invalid']*4)
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,4)
        self.assertEqual(c.populations['classified_valid'].count,0)
        self.assertEqual(c.ratios['classified_valid_coverage'].status,'undefined')
        self.assertEqual(c.ratios['decisive_validity_coverage'].value,1)
    def test_one_class_is_distinct_from_no_class(self):
        self.path,self.obs,self.support,self.man=population_bundle(self.root,[A]*4)
        c=self.cell();self.assertEqual(c.populations['classified_all'].class_counts[A],4)
        self.assertEqual(prefix(c,4).distinct_count,1)
    def test_missing_assignment_pin_has_no_latest_fallback(self):
        self.man['analysis_config']['assignment_pins']=[]
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,0)
        self.assertEqual(c.assignment_acceptance_counts['missing'],6)
        self.assertEqual(c.ratios['valid_fraction_selected'].value,Fraction(4,6))
    def test_conflicting_pin_is_local(self):
        self.man['analysis_config']['assignment_pins'].append(copy.deepcopy(self.man['analysis_config']['assignment_pins'][0]))
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,3)
        self.assertEqual(c.inventory.selected_count.value,6)
    def test_missing_validity_does_not_become_invalid(self):
        self.man['analysis_config']['validity_pins']=[]
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,4)
        self.assertEqual(c.validity_status_counts,{'missing':6})
        self.assertEqual(c.ratios['decisive_validity_coverage'].value,0)
    def test_missing_essential_class_evidence_preserves_other_samples(self):
        self.record('assignment','a1')['evidence_refs']=[record_ref('evidence','missing')]
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,3)
        self.assertEqual(c.inventory.selected_count.value,6)
        self.assertEqual(c.ratios['valid_fraction_selected'].value,Fraction(4,6))
    def test_missing_text_does_not_become_zero_coverage(self):
        self.record('realization','s1')['output_ref']=tagged(state='unavailable',reason='Not supplied')
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,4)
    def test_unknown_order_leaves_whole_cell_population_available(self):
        sel=self.man['analysis_config']['selection'][0];sel['sample_order']=tagged(state='unknown')
        for r in self.obs:
            if r['record_type']=='realization':r['sample_order']=tagged(state='unknown')
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,4)
        self.assertEqual(prefix(c,2).status,'unavailable')
    def test_unknown_selection_is_unavailable_not_empty(self):
        self.man['analysis_config']['selection'][0]['selected_sample_ids']=tagged(state='unknown')
        c=self.cell();self.assertIsNone(c.populations['classified_all'].count)
        self.assertEqual(c.ratios['classification_coverage'].status,'unavailable')
    def test_shared_schema_failure_is_unavailable_not_zero_classes(self):
        self.man['frames'][0]['structural_schema_version']='wrong'
        c=self.cell();self.assertEqual(c.inventory.selected_count.value,6)
        self.assertEqual(c.populations['classified_all'].status,'unavailable')
        self.assertIsNone(prefix(c,2).distinct_count)
    def test_schema_correction_scopes_class_and_validity_separately(self):
        self.support.append(support_record('correction','c1',effect='schema',action='challenge',stage='applied',
            target_refs=[record_ref('frame','frame1')],evidence_refs=[record_ref('evidence','e-a1')],
            reviewer_refs=[record_ref('role','reviewer')],reason=tagged('Stipulated defect')))
        c=self.cell();self.assertIsNone(c.populations['classified_all'].count)
        self.assertEqual(c.ratios['valid_fraction_selected'].value,Fraction(4,6))
    def test_independence_only_correction_preserves_counts(self):
        self.support.append(support_record('correction','c1',effect='independence',action='withdraw',stage='applied',
            target_refs=[record_ref('assignment','a1')],evidence_refs=[record_ref('evidence','e-a1')],
            reviewer_refs=[record_ref('role','reviewer')],reason=tagged('Stipulated dependency')))
        c=self.cell();self.assertEqual(c.populations['classified_all'].count,4)
        self.assertTrue(any('independence_correction:c1' in d.restrictions for d in c.admissions))
    def test_old_and_corrected_populations_keep_sample_identity(self):
        before=self.cell();old=self.record('assignment','a3');new=copy.deepcopy(old)
        new.update(record_id='a3new',assignment_id='a3new',assignment_version='0.2',structural_class_id=A,
                   supersedes_assignment_id=tagged('a3'),evidence_refs=[record_ref('evidence','newbasis')])
        e=copy.deepcopy(next(r for r in self.support if r['record_id']=='e-a3'))
        e.update(record_id='newbasis');e['payload'].update(target_ref=record_ref('assignment','a3new'),assertion=tagged(A))
        self.obs.append(new);self.support.append(e)
        self.man['analysis_config']['assignment_pins'][2].update(assignment_id='a3new',assignment_version='0.2')
        after=self.cell();self.assertEqual(before.inventory.selected_sample_ids,after.inventory.selected_sample_ids)
        self.assertEqual(before.populations['classified_all'].class_counts[A],2)
        self.assertEqual(after.populations['classified_all'].class_counts[A],3)
    def test_renaming_supported_class_ids_preserves_population_counts(self):
        before=self.cell();swap={A:C,B:A,C:B}
        for r in self.obs:
            if r['record_type']=='assignment' and r['structural_class_id'] in swap:
                r['structural_class_id']=swap[r['structural_class_id']]
        for r in self.support:
            if r['record_type']=='evidence' and r['payload']['assertion'].get('value') in swap:
                r['payload']['assertion']['value']=swap[r['payload']['assertion']['value']]
        after=self.cell()
        for view in before.populations:
            self.assertEqual(before.populations[view].sample_ids,after.populations[view].sample_ids)
            self.assertEqual(sorted(before.populations[view].class_counts.values()),sorted(after.populations[view].class_counts.values()))
    def test_other_cell_survives_malformed_frame_and_no_pooling(self):
        frame=copy.deepcopy(self.man['frames'][0]);frame.update(record_id='frame2',frame_id='frame2')
        cell=copy.deepcopy(self.man['cells'][0]);cell.update(record_id='cell2',analysis_cell_id='cell2',frame_id='frame2')
        self.man['frames'].append(frame);self.man['cells'].append(cell)
        self.man['analysis_config']['selection'].append({'analysis_cell_id':'cell2','selected_sample_ids':tagged([]),
            'sample_order':tagged([]),'registered_positions':tagged([]),'selection_basis':tagged('Known empty fixture cell')})
        self.man['frames'][0]['structural_schema_version']='bad'
        result=self.get();self.assertEqual(len(result.cells),2)
        self.assertEqual(result.cells[0].populations['classified_all'].status,'unavailable')
        self.assertEqual(result.cells[1].populations['classified_all'].count,0)
    def test_inputs_remain_unchanged_and_results_are_immutable(self):
        path=rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir()}
        out=build_populations(load_bundle(path))
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir()})
        with self.assertRaises(TypeError):out.cells[0].populations['classified_all'].class_counts[A]=42
    def test_no_io_or_model_calls_in_population_pass(self):
        bundle=load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))
        with patch('builtins.open',side_effect=AssertionError('No IO')),patch('socket.socket',side_effect=AssertionError('No network')):
            self.assertEqual(build_populations(bundle).cells[0].populations['classified_all'].count,4)


class PrefixTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.path,self.obs,self.support,self.man=population_bundle(self.root,[A,A,B,None,C,B],
            validity=['valid','valid','invalid','valid','valid','valid'],group_sizes=(3,3))
    def cell(self):return build_populations(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))).cells[0]
    def test_mf10_exact_prefix_oracles(self):
        c=self.cell()
        for k,allc,validc,na,nv in ((2,1,1,2,2),(4,2,1,3,2),(6,3,3,5,4)):
            p,q=prefix(c,k),prefix(c,k,'classified_valid')
            self.assertEqual((p.distinct_count,q.distinct_count,p.counted_samples,q.counted_samples),(allc,validc,na,nv))
        self.assertEqual(prefix(c,7).status,'unavailable');self.assertIsNone(prefix(c,7).distinct_count)
    def test_partial_group_flag_is_descriptive_only(self):
        p=prefix(self.cell(),2);self.assertEqual(p.partial_group_ids,('G1',))
        self.assertEqual(p.status,'available');self.assertIsNone(p.independent_draw_count)
    def test_invalid_or_unresolved_positions_are_not_backfilled(self):
        p=prefix(self.cell(),4,'classified_valid')
        self.assertEqual(p.selected_sample_ids,('s1','s2','s3','s4'));self.assertEqual(p.counted_sample_ids,('s1','s2'))
    def test_actual_order_change_may_change_prefix(self):
        before=prefix(self.cell(),2)
        order=['s1','s3','s2','s4','s5','s6'];self.man['analysis_config']['selection'][0]['sample_order']=tagged(order)
        for r in self.obs:
            if r['record_type']=='realization':r['sample_order']=tagged(order.index(r['sample_id'])+1)
        self.assertEqual(before.distinct_count,1);self.assertEqual(prefix(self.cell(),2).distinct_count,2)
    def test_storage_order_change_cannot_change_prefix(self):
        before=accumulation(self.cell(),[2,4,6]);self.obs.reverse();self.support.reverse()
        self.assertEqual(before,accumulation(self.cell(),[2,4,6]))
    def test_available_unclassified_prefix_has_count_zero(self):
        for r in self.obs:
            if r['record_type']=='assignment':r.update(assignment_status='unclassified',structural_class_id=None)
        p=prefix(self.cell(),6);self.assertEqual((p.status,p.distinct_count,p.counted_samples),('available',0,0))
    def test_invalid_and_omitted_k_have_distinct_outcomes(self):
        c=self.cell();self.assertEqual(prefix(c,None).status,'not_requested')
        for k in (True,0,-1,1.5,'2'):
            with self.assertRaises(InputError):prefix(c,k)
    def test_invalid_view_and_mode_fail_explicitly(self):
        c=self.cell()
        for view in ('all_outputs', [], None):
            with self.assertRaises(InputError):prefix(c,2,view)
        for mode in ('comparison', {}, None):
            with self.assertRaises(InputError):prefix(c,2,mode=mode)
    def test_grid_preserved_and_not_sorted_after_results(self):
        c=self.cell()
        for ks in ([4,2],[2,2],[False],None):
            with self.assertRaises(InputError):accumulation(c,ks)
        out=accumulation(c,[2,4,6,7]);self.assertEqual([p.k for p in out],[2,2,4,4,6,6,7,7])
    def test_accumulation_monotonicity_on_fixed_assignments(self):
        c=self.cell()
        for view in ('classified_all','classified_valid'):
            counts=[prefix(c,k,view).distinct_count for k in range(1,7)]
            self.assertEqual(counts,sorted(counts))


class HeroEndpointTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        labels=['MERGE','PIVOT','MERGE','HEAP','COUNT', 'MERGE','PIVOT','MERGE','HEAP','RADIX',
                'MERGE','PIVOT','MERGE','PIVOT','COUNT','MERGE','PIVOT','MERGE','PIVOT','HEAP']
        self.path,self.obs,self.support,self.man=population_bundle(self.root,['SORT-'+s for s in labels],group_sizes=(5,5,5,5))
    def cell(self):return build_populations(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))).cells[0]
    def test_hero_membership_5_10_20_matches_frozen_design(self):
        c=self.cell()
        self.assertEqual([prefix(c,k,mode='hero').distinct_count for k in (5,10,20)],[4,5,5])
        self.assertEqual(sorted(v for v in c.populations['classified_all'].class_counts.values() if v),[1,2,3,6,8])
        self.assertEqual(c.inventory.recorded_invocations,4)
    def test_missing_g2_p5_allows_descriptive_but_not_matched_prefix(self):
        self.obs[:]=[r for r in self.obs if not (r['record_type']=='realization' and r['record_id']=='s10')]
        sel=self.man['analysis_config']['selection'][0]
        for key in ('selected_sample_ids','sample_order'):sel[key]['value'].remove('s10')
        c=self.cell();self.assertEqual(c.inventory.selected_count.value,19)
        self.assertEqual(prefix(c,5,mode='hero').distinct_count,4)
        self.assertEqual(prefix(c,10).status,'available')
        self.assertEqual(prefix(c,10,mode='hero').status,'unavailable')
        self.assertEqual(prefix(c,20,mode='hero').status,'unavailable')
        self.assertEqual(prefix(c,10).selected_sample_ids[-1],'s11')
    def test_empty_classified_complete_twenty_is_legitimate_zero(self):
        for r in self.obs:
            if r['record_type']=='assignment':r.update(assignment_status='unclassified',structural_class_id=None)
        p=prefix(self.cell(),20,mode='hero');self.assertEqual((p.status,p.distinct_count),('available',0))
    def test_last_group_failure_does_not_erase_earlier_endpoint(self):
        ids={f's{i}' for i in range(16,21)}
        self.obs[:]=[r for r in self.obs if not (r['record_type']=='realization' and r['record_id'] in ids)]
        next(r for r in self.obs if r['record_id']=='call4')['attempt_status']='failed'
        sel=self.man['analysis_config']['selection'][0]
        for key in ('selected_sample_ids','sample_order'):sel[key]=tagged([s for s in sel[key]['value'] if s not in ids])
        c=self.cell();self.assertEqual(prefix(c,10,mode='hero').distinct_count,5)
        self.assertEqual(prefix(c,20,mode='hero').status,'unavailable')
    def test_unclassified_position_is_kept_without_replacement(self):
        next(r for r in self.obs if r['record_id']=='a10').update(assignment_status='unresolved',structural_class_id=None)
        c=self.cell();self.assertEqual(prefix(c,10,mode='hero').distinct_count,4)
        self.assertEqual(len(prefix(c,10,mode='hero').selected_sample_ids),10)
    def test_supplementary_single_candidate_k_is_not_hero_endpoint(self):
        c=self.cell();self.assertEqual(prefix(c,4).status,'available')
        self.assertEqual(prefix(c,4,mode='hero').status,'unavailable')
    def test_same_group_records_are_not_independent_draws(self):
        p=prefix(self.cell(),5,mode='hero');self.assertEqual(p.group_ids,('G1',))
        self.assertEqual(p.counted_samples,5);self.assertIsNone(p.independent_draw_count)
    def test_wrong_primary_attempt_blocks_matching_group(self):
        next(r for r in self.obs if r['record_id']=='s1')['attempt_id']=tagged('call2')
        c=self.cell();self.assertEqual(prefix(c,5,mode='hero').status,'unavailable')
        self.assertEqual(c.inventory.realization_count.value,20)
        self.assertIn('duplicate_selected_origin',c.inventory.selection_reasons)
    def test_group_plan_cannot_be_inferred_from_twenty_rows(self):
        self.man['analysis_config']['selection'][0]['registered_positions']=tagged(state='unknown')
        for r in self.obs:
            if r['record_type']=='attempt':r['planned_candidate_count']=tagged(state='unknown')
        c=self.cell();self.assertEqual(prefix(c,20).status,'available')
        self.assertEqual(prefix(c,20,mode='hero').status,'unavailable')


class AdversePopulationTests(unittest.TestCase):
    def test_actual_empty_input_has_no_invented_observations(self):
        with TemporaryDirectory() as t:
            root=Path(t);path,_,_,_=population_bundle(root,[])
            c=build_populations(load_bundle(path)).cells[0]
            self.assertEqual(c.inventory.realization_count.value,0)
            self.assertEqual(c.populations['classified_all'].count,0)
            self.assertEqual(prefix(c,1).status,'unavailable')
    def test_local_failed_adjudication_never_withholds_entire_population(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A,B])
            next(r for r in sup if r['record_id']=='e-a3')['payload']['state']='withdrawn'
            c=build_populations(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertEqual(c.populations['classified_all'].count,2)
            self.assertEqual(c.ratios['classification_coverage'].value,Fraction(2,3))
            self.assertEqual(c.ratios['valid_fraction_selected'].value,1)
    def test_association_error_withholds_both_affected_axes_without_deleting_sample(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A])
            next(r for r in obs if r['record_id']=='s1')['extensions']={'extraction_span':{'byte_start':-1,'byte_end':5}}
            c=build_populations(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertEqual(c.inventory.selected_count.value,2)
            self.assertEqual(c.populations['classified_all'].count,1)
            self.assertEqual(c.populations['classified_valid'].count,1)
    def test_missing_text_is_not_automatic_missing_artifact_identity(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A])
            next(r for r in obs if r['record_id']=='s1')['output_ref']=tagged(state='unavailable',reason='Controlled external record only')
            c=build_populations(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertEqual(c.populations['classified_valid'].count,2)
    def test_later_unrecorded_attempt_does_not_block_first_hero_endpoint(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A]*20,group_sizes=(5,5,5,5))
            obs[:]=[r for r in obs if r['record_id']!='call4']
            c=build_populations(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertEqual(prefix(c,5,mode='hero').status,'available')
            self.assertEqual(prefix(c,20,mode='hero').status,'unavailable')
    def test_repeated_call_without_new_identity_never_adds_sample(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A],group_sizes=(2,))
            r=copy.deepcopy(next(r for r in obs if r['record_id']=='call1'));r.update(record_id='call-retry',attempt_id='call-retry',retry_of=tagged('call1'))
            obs.append(r)
            c=build_populations(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertEqual(c.inventory.recorded_invocations,2);self.assertEqual(c.populations['classified_all'].count,2)
    def test_reference_registry_and_incident_never_add_model_samples(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A])
            sup.append(support_record('intake','incident1',stage='received',component='external_incident',proposed_change=tagged('Candidate new class')))
            c=build_populations(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertEqual(c.populations['classified_all'].count,1);self.assertFalse(c.independent_validation_performed)
    def test_public_surface_stops_before_metrics_and_comparisons(self):
        from structdet_bench import populations, inventory
        for module in (populations,inventory):
            for name in ('entropy','sci','effective_support','bootstrap','compare','render_report','generate','execute'):
                self.assertFalse(hasattr(module,name))


class Step4MatrixTests(unittest.TestCase):
    def test_step4_progress_and_bindings_cover_executed_methods(self):
        m=json.loads((ROOT/'tests/phase1_matrix.json').read_text())
        actual=[]
        for module in ('test_inventory','test_populations'):
            for cls in ast.parse((ROOT/'tests'/f'{module}.py').read_text()).body:
                if isinstance(cls,ast.ClassDef):
                    actual.extend(f'tests.{module}.{cls.name}.{f.name}' for f in cls.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_'))
        self.assertEqual(set(m['step4_acceptance']['test_bindings']),set(actual))
        self.assertEqual(len(m['step4_acceptance']['test_bindings']),len(actual))
        self.assertEqual(m['delivery_progress']['step'],4)
        self.assertFalse(m['delivery_progress']['phase1_complete'])
        self.assertIn('snapshot',m['current_step_scope'])
    def test_prior_requirement_and_source_identities_remain_intact(self):
        from tests.helpers import load_matrix, baseline_checks
        m=load_matrix()
        self.assertTrue(all(x['status']=='passed' for x in baseline_checks(m)))
        self.assertEqual(len(m['vf_tests']),54);self.assertEqual(len(m['trace_requirements']),40)
        self.assertEqual(len(m['report_groups']),36);self.assertEqual(sum(x['m_required'] for x in m['vf_tests']),37)
        self.assertEqual(len(m['ec001_supplement']['requirements']),8)
        for x in m['vf_tests']:
            for scope,rec in x['scope_records'].items():
                if scope!='M':self.assertEqual(rec['test_bindings'],[])
