"""Stipulated record-binding checks, not empirical or numerical comparison tests.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import ast
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from tests import phase2_helpers as h
from tests.helpers import tagged, record_ref, support_record, rewrite_evidence_bundle
from structdet_bench.comparison_records import review_comparison, registered_prompt_bytes, configuration_fingerprint
from structdet_bench.local_io import load_bundle


def fact(binding, name):
    return next(x for x in binding.facts if x.name == name)

class Fixture(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.path,self.obs,self.sup,self.man=h.comparison_fixture(self.root)
        self.cfg=self.man['analysis_config']['extensions']['comparison']
    def review(self):
        return review_comparison(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.sup,self.man)))
    def study(self,cid='P01-A'):
        return next(x['payload']['extensions']['study_binding'] for x in self.sup if x['record_id']=='study-'+cid)
    def binding(self,cid='P01-A',result=None):
        return next(x for x in (result or self.review()).bindings if x.cell_id==cid)
    def row(self,kind,id_):
        return next(x for x in self.obs+self.sup+self.man['cells']+self.man['protocols']+self.man['frames'] if x['record_type']==kind and x['record_id']==id_)
    def registration(self):
        ref=record_ref('preregistration','registration1');self.cfg['evidence']['registration']=[ref]
        # Independent canonical implementation for the identity oracle.
        def v(x):
            if isinstance(x,dict):return ['object',[[k,v(value)] for k,value in sorted(x.items())]]
            if isinstance(x,list):return ['array',[v(i) for i in x]]
            return [type(x).__name__,x]
        digest=hashlib.sha256(json.dumps(v(self.cfg),ensure_ascii=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        registration={'comparison_id':self.cfg['comparison_id'],'comparison_version':'0.1','binding_sha256':digest,
                      'first_inspected_at':tagged('2026-09-02T01:00:00+00:00'),'first_collection_at':tagged('2026-09-01T01:00:00+00:00')}
        self.sup.append(support_record('preregistration','registration1',registered_at=tagged('2026-08-31T01:00:00+00:00'),extensions={'comparison_registration':registration}))
        return self.sup[-1]['payload']

class ShapeTests(Fixture):
    def test_complete_six_blocks_bind_all_eighteen_cells(self):
        r=self.review();self.assertEqual(len(r.bindings),18);self.assertEqual(len(r.pairs),18)
        self.assertTrue(all(x.status=='record_consistent' for x in r.bindings));self.assertEqual(r.status,'record_limited')
        self.assertFalse(r.independent_validation_performed);self.assertFalse(r.endpoint_eligibility_evaluated)
    def test_absent_extension_is_not_requested(self):
        del self.man['analysis_config']['extensions']['comparison'];r=self.review()
        self.assertFalse(r.requested);self.assertEqual(r.status,'not_requested')
    def test_null_extension_is_requested_contract_error(self):
        self.man['analysis_config']['extensions']['comparison']=None;r=self.review()
        self.assertTrue(r.requested);self.assertEqual(r.status,'contract_error')
    def test_unknown_version_and_profile_fail(self):
        for key in ('comparison_schema_version','profile'):
            old=self.cfg[key];self.cfg[key]='unsupported';self.assertEqual(self.review().status,'contract_error');self.cfg[key]=old
    def test_boolean_approval_flag_rejected(self):
        self.cfg['all_gates_passed']=True;self.assertEqual(self.review().status,'contract_error')
    def test_material_role_cannot_be_overridden_in_comparison(self):
        self.cfg['material_role']='confirmatory';self.assertEqual(self.review().status,'contract_error')
    def test_missing_block_is_not_silently_shortened(self):
        self.cfg['blocks'].pop();self.assertEqual(self.review().status,'contract_error')
    def test_reordered_blocks_fail(self):
        self.cfg['blocks'].reverse();self.assertEqual(self.review().status,'contract_error')
    def test_missing_expected_cell_retains_its_role(self):
        self.man['cells']=[x for x in self.man['cells'] if x['record_id']!='P01-B'];r=self.review()
        self.assertEqual(len(r.bindings),18);self.assertEqual(self.binding('P01-B',r).status,'record_limited')
        self.assertEqual(self.binding('P01-A',r).status,'record_consistent')
        pair=next(x for x in r.pairs if x.block_id=='P01' and x.contrast=='C-A')
        self.assertTrue(all(f.status=='record_consistent' for f in pair.facts))
    def test_missing_condition_role_is_schema_error(self):
        del self.cfg['blocks'][0]['conditions']['B'];self.assertEqual(self.review().status,'contract_error')
    def test_duplicate_cell_reference_restricts_both_roles(self):
        self.cfg['blocks'][0]['conditions']['B']['cell_ref']=record_ref('cell','P01-A')
        b=self.review().bindings[:2];self.assertTrue(all(fact(x,'unique_cell_role').status=='inconsistent' for x in b))
    def test_wrong_record_reference_type_fails(self):
        self.cfg['blocks'][0]['conditions']['A']['cell_ref']=record_ref('role','reviewer');self.assertEqual(self.review().status,'contract_error')
    def test_duplicate_cell_identity_never_selects_one(self):
        self.man['cells'].append(copy.deepcopy(self.man['cells'][0]));self.assertEqual(fact(self.binding(),'expected_cell').status,'unresolved')
    def test_changed_frame_is_detected_per_pair(self):
        fr=copy.deepcopy(self.man['frames'][0]);fr.update(record_id='frame2',frame_id='frame2',consequence_horizon='Changed');self.man['frames'].append(fr)
        self.row('cell','P01-B')['frame_id']='frame2';r=self.review()
        pairs={x.contrast:x for x in r.pairs if x.block_id=='P01'}
        self.assertEqual(fact(pairs['B-A'],'frame_compatibility').status,'inconsistent')
        self.assertEqual(fact(pairs['C-A'],'frame_compatibility').status,'record_consistent')
    def test_bad_study_shape_is_local(self):
        self.study('P01-B')['unknown_instruction']='run';r=self.review()
        self.assertEqual(self.binding('P01-B',r).status,'contract_error');self.assertEqual(self.binding('P01-A',r).status,'record_consistent')
    def test_role_mismatch_is_explicit(self):
        self.row('cell','P01-A')['prompt_block_id']='P00';self.assertEqual(fact(self.binding(),'cell_role').status,'inconsistent')
    def test_supported_question_subsets_and_unknown_question(self):
        self.cfg['questions']=['P1'];self.assertNotEqual(self.review().status,'contract_error')
        self.cfg['questions']=['P9'];self.assertEqual(self.review().status,'contract_error')
    def test_invalid_limits_do_not_change_approved_budget(self):
        for value in (0,-1,False,2**31,1.5):
            self.cfg['limits']['max_pairs']=value;self.assertEqual(self.review().status,'contract_error')
    def test_future_method_parameters_are_stored_without_execution(self):
        r=self.review();self.assertEqual(r.configuration['resampling']['replicates'],2000)
        self.assertFalse(hasattr(r,'replicate_means'));self.assertFalse(hasattr(r,'distances'))
    def test_invalid_future_profile_is_not_ignored(self):
        self.cfg['resampling']['seed']=2026;self.assertEqual(self.review().status,'contract_error')
    def test_input_role_and_revision_history_retained(self):
        self.cfg['revision'].update(prior_run_ids=['old-run'],prior_comparison_ids=['old-comparison'],reason=tagged('Review correction'),changes=['Same observations, amended binding'])
        r=self.review();self.assertEqual(r.material_role,'fixture');self.assertEqual(r.configuration['revision']['prior_run_ids'],('old-run',))
    def test_top_level_type_mutations_are_controlled(self):
        baseline=copy.deepcopy(self.cfg)
        for key in baseline:
            for value in (None,False,[],{}):
                self.man['analysis_config']['extensions']['comparison']={**baseline,key:value}
                with self.subTest(key=key,value=value): self.assertIn(self.review().status,('contract_error','record_limited'))
    def test_missing_manifest_and_wrong_public_input(self):
        b=load_bundle(self.path);self.assertEqual(review_comparison(replace(b,manifest=None)).status,'unavailable')
        with self.assertRaises(ValueError):review_comparison(self.path)

class PromptControlTests(Fixture):
    def test_all_six_openers_and_clauses_match_independent_source(self):
        for b in range(1,7):
            for c in 'ABC':self.assertEqual((self.root/f'prompt-P{b:02}-{c}.txt').read_bytes(),registered_prompt_bytes(f'P{b:02}',c))
        r=self.review();self.assertTrue(all(fact(p,'AB_sent_prompt_equality').status=='record_consistent' for p in r.pairs if p.contrast=='B-A'))
    def test_crlf_or_extra_newline_is_not_silently_normalized(self):
        p=self.root/'prompt-P01-B.txt';p.write_bytes(p.read_bytes()+b'\n');self.row('artifact','prompt-P01-B')['expected_sha256']=tagged(state='unknown')
        self.assertEqual(fact(self.binding('P01-B'),'exact_prompt_assembly').status,'inconsistent')
    def test_wrong_c_clause_fails_even_matching_A(self):
        (self.root/'prompt-P01-C.txt').write_bytes((self.root/'prompt-P01-A.txt').read_bytes());self.row('artifact','prompt-P01-C')['expected_sha256']=tagged(state='unknown')
        self.assertEqual(fact(self.binding('P01-C'),'exact_prompt_assembly').status,'inconsistent')
    def test_unavailable_prompt_stays_unresolved(self):
        self.row('artifact','prompt-P01-A')['content_ref']=tagged(state='unavailable',reason='No supplied bytes')
        self.assertEqual(fact(self.binding(),'exact_prompt_assembly').status,'unresolved')
    def test_verified_byte_record_can_supply_missing_prompt(self):
        study=self.study();study['sent_prompt']['artifact_ref']=tagged(state='unknown')
        ref=record_ref('evidence','attestation1');study['sent_prompt']['attestation_ref']=tagged(ref)
        content=(self.root/'prompt-P01-A.txt').read_bytes()
        self.sup.append(support_record('evidence','attestation1',purpose='observation',target_ref=record_ref('cell','P01-A'),
            method=tagged('verified_sent_bytes_v1'),subject_hash=tagged(hashlib.sha256(content).hexdigest()),reviewer_refs=[record_ref('role','binding-reviewer')],
            extensions={'verified_prompt':{'encoding':'utf-8','byte_length':len(content),'comparison_id':'comparison-fixture','block_id':'P01','condition_id':'A','protocol_ref':record_ref('protocol','protocol-P01-A')}}))
        self.assertEqual(fact(self.binding(),'exact_prompt_assembly').status,'record_consistent')
        self.assertEqual(fact(self.binding(),'prompt_material').reasons,('attested_bytes_only',))
    def test_unsupported_B_temperature_preserves_A_C_facts(self):
        control=self.study('P01-B')['controls']['temperature'];control['actual']=tagged(state='unknown');control['enforcement']='unsupported'
        r=self.review();self.assertEqual(fact(self.binding('P01-B',r),'control_temperature').status,'unresolved')
        pair=next(x for x in r.pairs if x.block_id=='P01' and x.contrast=='C-A');self.assertTrue(all(x.status=='record_consistent' for x in pair.facts))
    def test_actual_temperature_mismatch_is_not_hidden_by_requested(self):
        self.study('P01-B')['controls']['temperature']['actual']=tagged(0.4)
        self.assertEqual(fact(self.binding('P01-B'),'control_temperature').status,'inconsistent')
    def test_enforcement_without_observation_record_is_unresolved(self):
        self.study()['controls']['temperature']['evidence_refs']=[]
        self.assertEqual(fact(self.binding(),'control_temperature').status,'unresolved')
    def test_wrong_control_observation_target_is_unresolved(self):
        self.row('evidence','controls-P01-A')['payload']['target_ref']=record_ref('cell','P01-B')
        self.assertEqual(fact(self.binding(),'control_temperature').status,'unresolved')
    def test_control_observation_must_match_actual_declared_fields(self):
        self.row('evidence','controls-P01-A')['payload']['extensions']['recorded_controls']['temperature']['actual']=tagged(0.6)
        self.assertNotEqual(fact(self.binding(),'control_temperature').status,'record_consistent')
    def test_bool_cannot_stand_for_number(self):
        self.study()['controls']['temperature']['requested']=tagged(True);self.assertEqual(self.binding().status,'contract_error')
    def test_user_fixed_generator_seed_is_deviation(self):
        self.study()['controls']['generator_seed']['actual']=tagged(1)
        self.assertEqual(fact(self.binding(),'control_generator_seed').status,'inconsistent')
    def test_protocol_control_disagreement_retained(self):
        self.row('protocol','protocol-P01-A')['decoding_settings']['value']['temperature']=0.8
        self.assertEqual(fact(self.binding(),'protocol_setting_temperature').status,'inconsistent')
    def test_hidden_context_unknown_is_not_known_empty(self):
        self.study()['platform_context']=tagged(state='unknown')
        self.assertEqual(fact(self.binding(),'platform_context').status,'unresolved')
    def test_missing_model_identity_limits_compatibility(self):
        self.row('cell','P01-B')['checkpoint_identifier']=tagged(state='unknown');r=self.review()
        pair=next(x for x in r.pairs if x.block_id=='P01' and x.contrast=='B-A')
        self.assertEqual(fact(pair,'checkpoint_identifier_compatibility').status,'unresolved')
    def test_changed_cap_convention_is_scoped(self):
        self.study('P01-B')['cap']['convention']=tagged('including_reasoning');r=self.review()
        pairs={x.contrast:x for x in r.pairs if x.block_id=='P01'}
        self.assertEqual(fact(pairs['B-A'],'cap_convention_compatibility').status,'inconsistent')
        self.assertEqual(fact(pairs['C-A'],'cap_convention_compatibility').status,'record_consistent')
    def test_usage_unknown_does_not_mean_zero_or_equal_spending(self):
        b=self.binding();self.assertEqual(b.budget['actual']['state'],'unknown');self.assertNotIn('equal_compute',repr(b))
    def test_distinct_actual_usage_does_not_change_planned_budget(self):
        self.row('budget','budget-P01-A')['payload']['actual']=tagged({'input_tokens':tagged(123),'cost':tagged(state='unknown')})
        self.assertEqual(fact(self.binding(),'planned_cell_budget').status,'record_consistent')
    def test_known_budget_mismatch_is_not_rewritten(self):
        self.row('budget','budget-P01-A')['payload']['planned']['value']['candidate_positions']=19
        self.assertEqual(fact(self.binding(),'planned_cell_budget').status,'inconsistent')
    def test_penalties_not_exposed_stay_not_applicable(self):
        ctl=self.study()['controls']['presence_penalty'];ctl.update(requested=tagged(state='not_applicable',reason='Not exposed'),actual=tagged(state='not_applicable',reason='Not exposed'),enforcement='unsupported')
        self.assertEqual(fact(self.binding(),'control_presence_penalty').status,'not_applicable')

class EvidenceOrderTests(Fixture):
    def test_interleaving_is_exact_all_72_positions(self):
        r=self.review();facts=[f for b in r.bindings for f in b.facts if f.name.startswith('interleave_')]
        self.assertEqual(len(facts),72);self.assertTrue(all(f.status=='record_consistent' for f in facts))
        self.assertEqual(sorted(f.observed['value'] for f in facts),list(range(1,73)))
    def test_bad_interleaving_order_detected(self):
        self.study()['attempts'][0]['global_order']=tagged(72)
        self.assertEqual(fact(self.binding(),'interleave_1').status,'inconsistent')
    def test_failed_attempt_is_retained_not_five_samples(self):
        self.row('attempt','call-P01-A-1')['attempt_status']='failed';b=self.binding()
        self.assertEqual(fact(b,'attempt_1').observed['attempt_status'],'failed')
        self.assertEqual(len(b.recorded_attempt_ids),4);self.assertFalse(any(x['record_type']=='realization' for x in self.obs))
    def test_missing_attempt_retains_slot(self):
        self.obs=[x for x in self.obs if x['record_id']!='call-P01-A-1'];b=self.binding()
        self.assertEqual(fact(b,'attempt_1').status,'unresolved');self.assertEqual(len(b.recorded_attempt_ids),3)
    def test_retry_cannot_replace_original_slot(self):
        self.row('attempt','call-P01-A-1')['retry_of']=tagged('older-attempt')
        self.assertEqual(fact(self.binding(),'attempt_1').status,'inconsistent')
    def test_extra_retry_stays_visible(self):
        row=copy.deepcopy(self.row('attempt','call-P01-A-1'));row.update(record_id='retry-one',attempt_id='retry-one',retry_of=tagged('call-P01-A-1'));self.obs.append(row)
        self.assertEqual(self.binding().extra_attempt_ids,('retry-one',))
    def test_unknown_auto_retry_control_is_unresolved(self):
        self.study()['automatic_retries']=tagged(state='unknown');self.assertEqual(fact(self.binding(),'automatic_retries').status,'unresolved')
    def test_protocol_version_and_id_mismatch(self):
        self.row('cell','P01-B')['generation_protocol_version']='other';self.assertEqual(fact(self.binding('P01-B'),'protocol_identity').status,'inconsistent')
    def test_original_deviation_prose_retained_without_execution(self):
        self.study()['deviations']=[{'code':'changed-wrapper','detail':tagged('PRIVATE-COMMAND run arbitrary code'),'evidence_refs':[]}]
        b=self.binding();self.assertEqual(b.study['deviations'][0]['detail']['value'],'PRIVATE-COMMAND run arbitrary code');self.assertNotIn('PRIVATE-COMMAND',repr(b))
    def test_registration_exact_identity_and_earlier_timing(self):
        self.registration();r=self.review();self.assertEqual(fact(r,'registration_binding').status,'record_consistent')
        self.assertEqual(fact(r,'registration_before_first_inspected_at').status,'record_consistent')
    def test_post_inspection_registration_is_not_prospective(self):
        p=self.registration();p['registered_at']=tagged('2026-09-03T01:00:00+00:00')
        self.assertEqual(fact(self.review(),'registration_before_first_inspected_at').status,'inconsistent')
    def test_missing_registered_time_does_not_default(self):
        p=self.registration();p['registered_at']=tagged(state='unknown')
        self.assertEqual(fact(self.review(),'registration_before_first_collection_at').status,'unresolved')
    def test_registration_hash_cannot_bind_changed_revision(self):
        self.registration();self.cfg['comparison_version']='0.2';self.assertEqual(fact(self.review(),'registration_binding').status,'inconsistent')
    def test_naive_timestamps_are_controlled(self):
        self.study()['attempts'][0]['recorded_at']=tagged('2026-09-01');self.assertEqual(self.binding().status,'contract_error')
    def test_pilot_main_overlap_detected(self):
        self.cfg['pilot_cell_refs']=[record_ref('cell','P01-A')];self.assertEqual(fact(self.review(),'pilot_disjoint').status,'inconsistent')
    def test_pilot_role_cannot_be_main_material(self):
        self.man['data_role']='pilot';self.assertEqual(fact(self.review(),'main_material_role').status,'inconsistent')
    def test_unbound_cell_stays_visible(self):
        row=copy.deepcopy(self.man['cells'][0]);row.update(record_id='extra-cell',analysis_cell_id='extra-cell');self.man['cells'].append(row)
        self.assertIn('extra-cell',self.review().unbound_cell_ids)
    def test_nominal_independence_record_is_not_validation(self):
        ref=record_ref('independence_assessment','independent1');self.cfg['evidence']['independence']=[ref]
        self.sup.append(support_record('independence_assessment','independent1',outcome='supported_for_scope'))
        r=self.review();self.assertFalse(r.independent_validation_performed);self.assertTrue(fact(r,'evidence_independence').mock)
    def test_mock_child_cannot_be_promoted_by_parent(self):
        self.man['data_role']='descriptive';self.row('evidence','study-P01-A')['payload'].update(data_role='descriptive',mock=False)
        self.assertIn('mock_evidence_for_nonfixture',fact(self.binding(),'support_reference').reasons)
    def test_withdrawn_support_is_restricted(self):
        self.row('evidence','controls-P01-A')['payload']['state']='withdrawn'
        self.assertEqual(fact(self.binding(),'control_temperature').status,'unresolved')
    def test_circular_decisive_evidence_fails_without_recursion(self):
        p=self.row('evidence','controls-P01-A')['payload'];p['evidence_refs']=[record_ref('evidence','controls-P01-A')]
        self.assertEqual(fact(self.binding(),'control_temperature').status,'unresolved')
    def test_duplicate_typed_evidence_reference_fails(self):
        ref=record_ref('preregistration','r1');self.cfg['evidence']['registration']=[ref,ref]
        self.assertEqual(self.review().status,'contract_error')
    def test_fixture_does_not_claim_full_P1_or_P5(self):
        r=self.review();self.assertFalse(r.endpoint_eligibility_evaluated)
        self.assertTrue(all(not p.endpoint_eligibility_evaluated for p in r.pairs))
    def test_original_ids_and_all_existing_inputs_unchanged(self):
        p=rewrite_evidence_bundle(self.root,self.obs,self.sup,self.man);before={x.name:x.read_bytes() for x in self.root.iterdir()}
        b=load_bundle(p);r=review_comparison(b);self.assertEqual(before,{x.name:x.read_bytes() for x in self.root.iterdir()})
        with self.assertRaises(TypeError):r.configuration['comparison_id']='changed'

class Step2CatalogueTests(unittest.TestCase):
    def test_stage_two_binds_all_current_record_and_security_methods(self):
        m=h.read_matrix();actual=[]
        for module in ('test_comparison_records','test_phase2_security'):
            for cls in ast.parse((h.ROOT/'tests'/f'{module}.py').read_text()).body:
                if isinstance(cls,ast.ClassDef):
                    actual.extend(f'tests.{module}.{cls.name}.{f.name}' for f in cls.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_'))
        self.assertEqual(m['delivery']['step'],2)
        self.assertEqual(set(m['stage_bindings']['2']['test_bindings']),set(actual))
        self.assertEqual(len(m['stage_bindings']['2']['test_bindings']),len(actual))
        self.assertEqual([x['step'] for x in m['delivery']['history']],[1])
    def test_pinned_representation_expands_identical_catalogues_and_503_methods(self):
        raw=h.read_json(h.MATRIX_PATH);m=h.read_matrix()
        self.assertEqual(m['catalogues'],h.expected_catalogues())
        self.assertEqual(len(m['predecessor']['test_ids']),503)
        self.assertEqual(h.sha256_bytes(('\n'.join(m['predecessor']['test_ids'])+'\n').encode()),h.PREDECESSOR_IDS_SHA256)
        self.assertEqual(h.expand_matrix(m),m)
        self.assertEqual(raw['catalogues']['expanded_sha256'],h.sha256_bytes(h.canonical_bytes(m['catalogues'])))
    def test_tampered_encoding_cannot_redirect_source_or_hide_requirement(self):
        raw=h.read_json(h.MATRIX_PATH)
        for field in ('source_sha256','expanded_sha256'):
            bad=copy.deepcopy(raw);bad['catalogues'][field]='0'*64
            with self.assertRaises(ValueError):h.expand_matrix(bad)
        bad=copy.deepcopy(raw);bad['predecessor']['test_ids']['source_sha256']='0'*64
        with self.assertRaises(ValueError):h.expand_matrix(bad)
    def test_step_two_record_coverage_does_not_complete_full_V_or_E(self):
        m=h.read_matrix();self.assertEqual(h.validate_matrix(m),[])
        self.assertTrue(all(x['implementation_status']!='implemented' for x in m['vt_obligations']))
        self.assertTrue(all(x['evidence_status']=='not_supplied' for x in m['vt_obligations']))
        self.assertEqual(len(m['vt_obligations']),26)

class DeploymentBindingTests(Fixture):
    def test_known_B_drift_is_explicit_without_erasing_AC(self):
        self.study('P01-B')['deployment']['change_detected']=tagged(True);r=self.review()
        self.assertEqual(fact(self.binding('P01-B',r),'deployment_unchanged').status,'inconsistent')
        self.assertEqual(self.binding('P01-A',r).status,'record_consistent')
        self.assertEqual(self.binding('P01-C',r).status,'record_consistent')
    def test_unknown_serving_identity_is_not_filled_from_model_alias(self):
        self.study()['deployment']['serving_identity']=tagged(state='unknown');a=self.binding()
        self.assertEqual(fact(a,'serving_identity').status,'unresolved')
        self.assertEqual(a.cell['model_identifier']['value'],'MOCK-MODEL')
    def test_claimed_stable_serving_needs_recorded_evidence(self):
        self.study()['deployment']['evidence_refs']=[]
        self.assertEqual(fact(self.binding(),'deployment_unchanged').status,'unresolved')
    def test_equal_model_names_cannot_hide_different_serving_identity(self):
        self.study('P01-B')['deployment']['serving_identity']=tagged('MOCK-OTHER-DEPLOYMENT');r=self.review()
        p=next(x for x in r.pairs if x.block_id=='P01' and x.contrast=='B-A')
        self.assertEqual(fact(p,'deployment_serving_identity_compatibility').status,'inconsistent')
    def test_missing_replay_stays_unresolved_without_index_generation(self):
        self.cfg['resampling']['replay_ref']=tagged(record_ref('artifact','missing'))
        r=self.review();self.assertEqual(fact(r,'replay_ref').status,'unresolved')
        self.assertFalse(hasattr(r,'resample_indices'))

class PinnedCaseTests(Fixture):
    def test_checked_in_adverse_binding_cases_have_independent_expected_states(self):
        data=h.read_json(h.ROOT/'tests/fixtures/comparison_cases.json')
        self.assertEqual(data['data_role'],'fixture');self.assertEqual(data['source_plan_sha256'],h.PLAN_SHA256)
        self.assertEqual(len({c['case_id'] for c in data['cases']}),len(data['cases']))
        for case in data['cases']:
            with self.subTest(case=case['case_id']):
                target=self.cfg if case['container']=='comparison' else self.study('P01-B')
                for key in case['path'][:-1]:target=target[key]
                key=case['path'][-1];old=copy.deepcopy(target[key]);target[key]=copy.deepcopy(case['value'])
                r=self.review()
                if 'expected_review_status' in case:self.assertEqual(r.status,case['expected_review_status'])
                elif 'expected_binding_fact' in case:self.assertEqual(fact(self.binding('P01-B',r),case['expected_binding_fact']).status,case['expected_status'])
                else:
                    pair=next(p for p in r.pairs if p.block_id=='P01' and p.contrast=='B-A')
                    self.assertEqual(fact(pair,case['expected_pair_fact']).status,case['expected_status'])
                target[key]=old
