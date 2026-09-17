"""Step 4 input/attempt/selection/group checks on stipulated records."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench.inventory import build_inventory
from structdet_bench.local_io import load_bundle, ReadLimits
from tests.helpers import population_bundle, rewrite_evidence_bundle, tagged, record_ref, artifact_record

A = "SORT-ADJ"


class InventoryTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.path,self.obs,self.support,self.man=population_bundle(self.root,[A]*10,group_sizes=(5,5))
    def raw(self,kind,rid):
        return next(r for r in self.obs if r["record_type"]==kind and r["record_id"]==rid)
    def get(self):
        return build_inventory(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)))
    def selection(self): return self.man["analysis_config"]["selection"][0]
    def remove_samples(self,ids):
        self.obs[:]=[r for r in self.obs if not (r['record_type']=='realization' and r['record_id'] in ids)]
        sel=self.selection()
        for f in ('selected_sample_ids','sample_order'):
            sel[f]=tagged([s for s in sel[f]['value'] if s not in ids])

    def test_attempts_and_realizations_are_separate(self):
        inv=self.get();c=inv.cells[0]
        self.assertEqual(c.realization_count.value,10);self.assertEqual(c.recorded_invocations,2)
        self.assertEqual(c.attempt_status_counts,{'succeeded':2});self.assertEqual(len(c.positions),10)
        self.assertFalse(inv.scientific_independence_established)
    def test_failed_five_candidate_call_does_not_create_samples(self):
        self.remove_samples({f's{i}' for i in range(6,11)})
        self.raw('attempt','call2')['attempt_status']='failed'
        c=self.get().cells[0]
        self.assertEqual(c.realization_count.value,5);self.assertEqual(c.selected_count.value,5)
        self.assertEqual(sum(p.status=='missing' for p in c.positions),5)
        self.assertEqual(c.attempt_status_counts,{'succeeded':1,'failed':1})
    def test_unattempted_slot_is_not_an_invocation(self):
        self.remove_samples({f's{i}' for i in range(6,11)})
        self.raw('attempt','call2')['attempt_status']='not_attempted'
        c=self.get().cells[0]
        self.assertEqual(c.recorded_invocations,1);self.assertEqual(len(c.positions),10)
    def test_retry_is_preserved_without_adding_planned_slots(self):
        r=copy.deepcopy(self.raw('attempt','call1'));r.update(record_id='retry1',attempt_id='retry1',retry_of=tagged('call1'))
        self.obs.append(r);c=self.get().cells[0]
        self.assertEqual(len(c.recorded_attempt_ids),3);self.assertEqual(len(c.positions),10)
        self.assertEqual(c.retry_links['retry1']['value'],'call1')
        self.assertIn('group_has_retry_history',c.groups[0].reasons)
    def test_unknown_attempt_history_is_not_one_call_per_sample(self):
        self.obs[:]=[r for r in self.obs if r['record_type']!='attempt']
        for r in self.obs:
            if r['record_type']=='realization':r['attempt_id']=tagged(state='unknown')
        self.selection()['registered_positions']=tagged(state='unknown')
        c=self.get().cells[0]
        self.assertEqual(c.recorded_invocations,0);self.assertEqual(c.attempt_history_status,'unknown')
        self.assertEqual(c.realization_count.value,10)
    def test_original_storage_order_is_not_experimental_sequence(self):
        before=self.get().cells[0];self.obs.reverse();after=self.get().cells[0]
        self.assertEqual(before.order,after.order);self.assertEqual(before.selected_sample_ids,after.selected_sample_ids)
    def test_repeated_bytes_with_distinct_positions_remain_observations(self):
        for r in self.obs:
            if r['record_type']=='realization':r['output_content_hash']=tagged('0'*64)
        c=self.get().cells[0]
        self.assertEqual(c.realization_count.value,10);self.assertEqual(c.selected_count.value,10)
    def test_duplicate_id_is_ambiguous_never_deduplicated_silently(self):
        self.obs.append(copy.deepcopy(self.raw('realization','s1')))
        inv=self.get();c=inv.cells[0]
        self.assertIsNone(c.realization_count.value);self.assertIsNone(c.selected_count.value)
        self.assertIn('s1',c.ambiguous_sample_ids);self.assertIn(('realization','s1'),inv.duplicate_identities)
    def test_duplicate_malformed_id_remains_ambiguous(self):
        r=copy.deepcopy(self.raw('realization','s1'));del r['completion_status'];self.obs.append(r)
        self.assertIsNone(self.get().cells[0].selected_count.value)
    def test_unknown_cell_remains_unallocated(self):
        self.raw('realization','s1')['analysis_cell_id']='absent'
        inv=self.get();self.assertEqual(len(inv.unallocated_rows),1)
        self.assertIn('selected_identity_unresolved',inv.cells[0].selection_reasons)
    def test_missing_requested_sample_cannot_create_observation(self):
        self.obs[:]=[r for r in self.obs if not (r['record_type']=='realization' and r['record_id']=='s1')]
        c=self.get().cells[0]
        self.assertEqual(c.realization_count.value,9);self.assertIsNone(c.selected_count.value)
        self.assertIn('s1',c.requested_sample_ids);self.assertNotIn('s1',c.selected_sample_ids)
    def test_unknown_selection_is_not_automatically_all(self):
        self.selection()['selected_sample_ids']=tagged(state='unknown')
        c=self.get().cells[0];self.assertEqual(c.realization_count.value,10)
        self.assertIsNone(c.selected_count.value);self.assertIn('selection_unknown',c.selection_reasons)
    def test_known_empty_selection_is_zero_with_exclusions(self):
        self.selection()['selected_sample_ids']=tagged([]);self.selection()['sample_order']=tagged([])
        c=self.get().cells[0];self.assertEqual(c.selected_count.value,0);self.assertEqual(len(c.excluded_sample_ids),10)
    def test_extra_output_is_preserved_unselected(self):
        r=copy.deepcopy(self.raw('realization','s5'));r.update(record_id='extra',sample_id='extra',within_group_index=tagged(6))
        self.obs.append(r);c=self.get().cells[0]
        self.assertEqual(c.realization_count.value,11);self.assertEqual(c.selected_count.value,10)
        self.assertEqual(c.extra_sample_ids,('extra',));self.assertIn('extra',c.excluded_sample_ids)
    def test_selecting_extra_output_cannot_extend_planned_budget(self):
        self.raw('realization','s5')['within_group_index']=tagged(6)
        c=self.get().cells[0];self.assertIsNone(c.selected_count.value)
        self.assertIn('selected_unrequested_candidate',c.selection_reasons)
    def test_same_attempt_position_cannot_count_twice_under_two_ids(self):
        self.raw('realization','s2')['within_group_index']=tagged(1)
        c=self.get().cells[0]
        self.assertIn('duplicate_selected_origin',c.selection_reasons)
        self.assertEqual(c.positions[0].status,'ambiguous')
    def test_unknown_order_does_not_erase_selection(self):
        self.selection()['sample_order']=tagged(state='unknown')
        for r in self.obs:
            if r['record_type']=='realization':r['sample_order']=tagged(state='unknown')
        c=self.get().cells[0];self.assertIsNone(c.order);self.assertEqual(c.selected_count.value,10)
    def test_recorded_ordinals_can_supply_order(self):
        self.selection()['sample_order']=tagged(state='unknown');self.obs.reverse()
        c=self.get().cells[0];self.assertEqual(c.order,tuple(f's{i}' for i in range(1,11)))
        self.assertEqual(c.order_source,'recorded_sample_order')
    def test_conflicting_order_sources_are_not_resolved_by_preference(self):
        self.selection()['sample_order']['value'].reverse()
        c=self.get().cells[0];self.assertIsNone(c.order);self.assertIn('conflicting_sample_order',c.order_reasons)
    def test_partial_explicit_order_is_unavailable(self):
        self.selection()['sample_order']['value'].pop()
        self.assertIn('order_inventory_mismatch',self.get().cells[0].order_reasons)
    def test_duplicate_planned_position_is_unavailable(self):
        self.selection()['registered_positions']['value'].append(copy.deepcopy(self.selection()['registered_positions']['value'][0]))
        c=self.get().cells[0];self.assertEqual(c.plan_status,'unavailable')
        self.assertIn('duplicate_planned_position',c.plan_reasons)
    def test_plan_without_attempt_records_does_not_invent_attempts(self):
        self.obs[:]=[r for r in self.obs if r['record_type']!='attempt']
        for p in self.selection()['registered_positions']['value']:p['attempt_id']=tagged(state='unknown')
        c=self.get().cells[0];self.assertEqual(len(c.positions),10);self.assertEqual(c.recorded_attempt_ids,())
    def test_primary_attempt_metadata_can_supply_plan(self):
        self.selection()['registered_positions']=tagged(state='unknown')
        c=self.get().cells[0];self.assertEqual(c.plan_status,'available');self.assertEqual(len(c.positions),10)
    def test_large_attempt_count_does_not_expand_unbounded_positions(self):
        self.selection()['registered_positions']=tagged(state='unknown')
        self.raw('attempt','call1')['planned_candidate_count']=tagged(10**30)
        c=self.get().cells[0];self.assertIn('position_plan_limit_exceeded',c.plan_reasons)
        self.assertEqual(c.positions,())
    def test_private_and_missing_text_do_not_zero_inventory(self):
        self.raw('realization','s1')['output_ref']=tagged(state='unavailable',reason='Private')
        c=self.get().cells[0];self.assertEqual(c.selected_count.value,10)
        self.assertEqual(c.associations[0].output_ref['state'],'unavailable')
    def test_known_empty_and_truncated_emissions_remain_samples(self):
        self.raw('realization','s1')['completion_status']='truncated'
        c=self.get().cells[0];self.assertEqual(c.selected_count.value,10);self.assertEqual(c.completion_counts['truncated'],1)
    def test_frame_failure_is_scoped_and_distinct_from_empty(self):
        self.man['frames'][0]['structural_schema_version']='wrong'
        c=self.get().cells[0];self.assertEqual(c.frame_status,'unavailable');self.assertEqual(c.selected_count.value,10)
    def test_protocol_mismatch_is_frame_error(self):
        self.man['cells'][0]['generation_protocol_version']='wrong'
        self.assertIn('protocol_version_mismatch',self.get().cells[0].frame_reasons)
    def test_malformed_observation_retains_row_and_complete_count_uncertainty(self):
        path=rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)
        with (self.root/'records.jsonl').open('ab') as f:f.write(b'broken\n')
        c=build_inventory(load_bundle(path)).cells[0]
        self.assertIsNone(c.realization_count.value);self.assertEqual(c.selected_count.value,10)
        self.assertTrue(c.unresolved_rows)
    def test_wrong_record_file_hash_cannot_supply_selected_identity(self):
        self.man['record_files'][0]['expected_sha256']=tagged('0'*64)
        c=self.get().cells[0];self.assertIsNone(c.selected_count.value)
        self.assertEqual(len(c.unresolved_rows),10)
    def test_attempt_cell_mismatch_is_preserved(self):
        self.raw('attempt','call1')['analysis_cell_id']='different'
        c=self.get().cells[0]
        self.assertIn('attempt_cell_mismatch',next(a for a in c.associations if a.sample_id=='s1').reasons)
    def test_position_plan_mutations_have_controlled_diagnostics(self):
        for bad in (None,False,{},[],{'generation_group_id':[]},'private data'):
            self.selection()['registered_positions']=tagged([bad])
            c=self.get().cells[0];self.assertIn('invalid_position_plan',c.plan_reasons)
    def test_no_io_after_loading(self):
        bundle=load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))
        with patch('builtins.open',side_effect=AssertionError('No new reads')):
            self.assertEqual(build_inventory(bundle).cells[0].selected_count.value,10)


class ArtifactAssociationTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.path,self.obs,self.support,self.man=population_bundle(self.root,[A],group_sizes=(1,))
        self.sample=next(r for r in self.obs if r['record_type']=='realization')
        self.attempt=next(r for r in self.obs if r['record_type']=='attempt')
        raw=artifact_record('raw','raw.bin');raw['record_type']='raw_artifact'
        output=artifact_record('out','out.bin');self.obs.extend([raw,output])
        self.rawbytes='αHEAD\nbody\r\nTAIL'.encode();self.body=b'body\r\n'
        self.start=self.rawbytes.index(self.body)
        (self.root/'raw.bin').write_bytes(self.rawbytes);(self.root/'out.bin').write_bytes(self.body)
        self.sample.update(raw_response_ref=tagged(record_ref('raw_artifact','raw')),
            output_ref=tagged(record_ref('artifact','out')),output_content_hash=tagged(hashlib.sha256(self.body).hexdigest()),
            extensions={'extraction_span':{'byte_start':self.start,'byte_end':self.start+len(self.body)}})
        self.attempt['raw_response_ref']=tagged(record_ref('raw_artifact','raw'))
    def association(self):
        return build_inventory(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))).cells[0].associations[0]
    def test_exact_byte_region_keeps_unicode_and_crlf(self):
        a=self.association();self.assertEqual(a.span_status,'bytes_match');self.assertEqual(a.reasons,())
    def test_character_offsets_cannot_replace_byte_offsets(self):
        self.sample['extensions']['extraction_span']['byte_start']-=1
        self.assertEqual(self.association().span_status,'mismatch')
    def test_raw_response_mismatch_cannot_be_repaired_by_neighbor(self):
        extra=artifact_record('raw2','raw.bin');extra['record_type']='raw_artifact';self.obs.append(extra)
        self.sample['raw_response_ref']=tagged(record_ref('raw_artifact','raw2'))
        self.assertIn('raw_response_association_mismatch',self.association().reasons)
    def test_truncated_known_text_can_be_associated_without_completion(self):
        self.sample['completion_status']='truncated'
        self.assertEqual(self.association().span_status,'bytes_match')
    def test_empty_emitted_region_is_real_bytes_not_missing_slot(self):
        (self.root/'out.bin').write_bytes(b'');self.sample['output_content_hash']=tagged(hashlib.sha256(b'').hexdigest())
        self.sample['extensions']['extraction_span']['byte_end']=self.start
        self.assertEqual(self.association().span_status,'bytes_match')
    def test_missing_raw_is_unavailable_not_an_extraction_guess(self):
        (self.root/'raw.bin').unlink()
        self.assertEqual(self.association().span_status,'unavailable')
    def test_negative_bool_and_oversized_spans_are_controlled(self):
        for span in ({'byte_start':True,'byte_end':1},{'byte_start':-1,'byte_end':2}, {'byte_start':0,'byte_end':10**30}):
            self.sample['extensions']['extraction_span']=span
            self.assertIn(self.association().span_status,{'unavailable','mismatch'})


class AdditionalInventoryTests(unittest.TestCase):
    def test_duplicate_group_position_with_unknown_attempt_is_unresolved(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A],group_sizes=(2,))
            for r in obs:
                if r['record_type']=='realization':r.update(attempt_id=tagged(state='unknown'),within_group_index=tagged(1))
            c=build_inventory(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertIn('duplicate_selected_origin',c.selection_reasons)
    def test_shared_group_across_cells_is_retained_without_pooling(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A],group_sizes=(2,))
            cell=copy.deepcopy(m['cells'][0]);cell.update(record_id='cell2',analysis_cell_id='cell2',condition_id='C')
            m['cells'].append(cell)
            next(r for r in obs if r['record_type']=='realization' and r['record_id']=='s2')['analysis_cell_id']='cell2'
            out=build_inventory(load_bundle(rewrite_evidence_bundle(root,obs,sup,m)))
            self.assertEqual(out.cross_cell_groups,{'G1':('cell1','cell2')})
            self.assertEqual(len(out.cells),2);self.assertFalse(out.scientific_independence_established)
    def test_malformed_manifest_stays_unavailable_not_successful_empty_study(self):
        with TemporaryDirectory() as t:
            root=Path(t);(root/'bundle.json').write_bytes(b'broken')
            out=build_inventory(load_bundle(root/'bundle.json'))
            self.assertFalse(out.acquisition_complete);self.assertTrue(out.input_diagnostics)
    def test_extra_later_failure_does_not_contaminate_known_selected_ids(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A])
            bad=copy.deepcopy(obs[0]);bad.update(record_id='unselected',sample_id='unselected');del bad['completion_status'];obs.append(bad)
            c=build_inventory(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertIsNone(c.realization_count.value);self.assertEqual(c.selected_count.value,2)
    def test_absent_future_attempt_preserves_earlier_group_plan(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A]*20,group_sizes=(5,5,5,5))
            obs[:]=[r for r in obs if r['record_id']!='call4']
            c=build_inventory(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertEqual(c.plan_status,'available');self.assertTrue(c.groups[0].position_complete)
            self.assertFalse(c.groups[3].position_complete)
    def test_declared_output_offsets_cannot_add_a_new_realization_twice(self):
        with TemporaryDirectory() as t:
            root=Path(t);_,obs,sup,m=population_bundle(root,[A,A])
            raw=artifact_record('raw','raw.bin');raw['record_type']='raw_artifact';obs.extend([raw,artifact_record('out','out.bin')])
            (root/'raw.bin').write_bytes(b'abc');(root/'out.bin').write_bytes(b'abc')
            for r in obs:
                if r['record_type']=='realization':
                    r.update(raw_response_ref=tagged(record_ref('raw_artifact','raw')),output_ref=tagged(record_ref('artifact','out')),
                             extensions={'extraction_span':{'byte_start':0,'byte_end':3}})
            c=build_inventory(load_bundle(rewrite_evidence_bundle(root,obs,sup,m))).cells[0]
            self.assertIn('duplicate_selected_origin',c.selection_reasons)
