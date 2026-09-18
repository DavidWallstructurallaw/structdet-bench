"""Step 3 evidence-policy conformance on explicitly artificial records."""
import copy
import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from structdet_bench.evidence import EvidenceIndex, review_evidence
from structdet_bench.local_io import load_bundle
from tests.helpers import evidence_bundle, rewrite_evidence_bundle, support_record, record_ref, tagged

class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.path,self.obs,self.support,self.man=evidence_bundle(self.root,samples=2)
    def result(self,axis='assignment',sample='s1'):
        path=rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)
        return next(a for a in review_evidence(load_bundle(path)).admissions if a.axis==axis and a.sample_id==sample)
    def row(self,identity): return next(r for r in self.obs+self.support if r['record_id']==identity)
    def imported(self): self.path,self.obs,self.support,self.man=evidence_bundle(self.root,policy='adjudicated_import',samples=2)
    def test_fixture_positive_is_only_stipulated(self):
        a=self.result();self.assertEqual(a.status,'accepted');self.assertTrue(a.fixture_context)
        self.assertFalse(a.independent_validation_performed)
    def test_fixture_missing_declaration_is_local(self):
        self.support.remove(self.row('e-a1'))
        self.assertEqual(self.result().status,'withheld');self.assertEqual(self.result(sample='s2').status,'accepted')
        self.assertEqual(self.result('validity').status,'accepted')
    def test_no_pin_never_selects_latest(self):
        self.man['analysis_config']['assignment_pins']=[]
        self.assertEqual(self.result().status,'missing')
    def test_duplicate_pin_even_identical_is_conflict(self):
        self.man['analysis_config']['assignment_pins'].append(copy.deepcopy(self.man['analysis_config']['assignment_pins'][0]))
        self.assertEqual(self.result().status,'conflict')
    def test_duplicate_invalid_record_still_ambiguous(self):
        r=copy.deepcopy(self.row('a1'));del r['assignment_status'];self.obs.append(r)
        self.assertIn('selected_revision_unresolved',self.result().reasons)
    def test_revision_pin_mismatch_is_not_repaired(self):
        self.man['analysis_config']['assignment_pins'][0]['assignment_version']='9'
        self.assertIn('selected_revision_mismatch',self.result().reasons)
    def test_provisional_is_not_admitted(self):
        self.row('a1')['assignment_review_status']='provisional'
        self.assertIn('provisional_judgment',self.result().reasons)
    def test_unresolved_adjudicated_retains_epistemic_state(self):
        r=self.row('a1');r.update(assignment_status='unresolved',structural_class_id=None,assignment_review_status='adjudicated')
        self.assertEqual(self.result().status,'unresolved');self.assertIsNone(self.result().outcome)
    def test_unclassified_stays_unclassified(self):
        self.row('a1').update(assignment_status='unclassified',structural_class_id=None)
        self.assertEqual(self.result().status,'unclassified')
    def test_invalid_validity_does_not_erase_class(self):
        self.row('v1')['validity_status']='invalid';self.row('e-v1')['payload']['assertion']=tagged('invalid')
        self.assertEqual(self.result().status,'accepted');self.assertEqual(self.result('validity').outcome,'invalid')
    def test_undetermined_and_absent_validity_are_distinct(self):
        self.row('v1')['validity_status']='undetermined';self.row('e-v1')['payload']['assertion']=tagged('undetermined')
        self.assertEqual(self.result('validity').outcome,'undetermined')
        self.man['analysis_config']['validity_pins']=[]
        self.assertEqual(self.result('validity').status,'missing')
    def test_not_assessed_does_not_create_invalidity(self):
        self.row('v1')['validity_status']='not_assessed'
        self.assertEqual(self.result('validity').status,'not_assessed');self.assertIsNone(self.result('validity').outcome)
    def test_fixture_policy_cannot_present_empirical_context(self):
        self.man['data_role']='confirmatory'
        self.assertIn('fixture_policy_requires_fixture_context',self.result().reasons)
    def test_wrong_frame_withholds_only_affected_sample(self):
        self.row('a1')['frame_id']='missing'
        self.assertEqual(self.result().status,'withheld');self.assertEqual(self.result(sample='s2').status,'accepted')
    def test_wrong_rubric_withholds_validity_only(self):
        self.row('v1')['validity_rubric_ref']=tagged('other-rubric')
        self.assertEqual(self.result().status,'accepted');self.assertEqual(self.result('validity').status,'withheld')
    def test_conflicting_assertion_is_not_vote(self):
        self.row('e-a1')['payload']['assertion']=tagged('SORT-MERGE')
        self.assertIn('evidence_assertion_mismatch',self.result().reasons)
    def test_explicit_evidence_contradiction_is_preserved(self):
        self.row('e-a1')['payload']['conflict_status']='unresolved'
        self.assertIn('evidence_contradiction',self.result().reasons)
    def test_payload_shape_does_not_certify_evidence(self):
        self.row('e-a1')['payload']={'adjudicated':True}
        self.assertIn('essential_evidence_unresolved',self.result().reasons)
    def test_import_requires_adjudication_record(self):
        self.imported();self.support.remove(self.row('d-a1'))
        self.assertIn('adjudication_record_unresolved',self.result().reasons)
    def test_import_positive_carries_restricted_scientific_scope(self):
        self.imported();a=self.result()
        self.assertEqual(a.status,'accepted');self.assertIn('independent_measurement_not_certified_by_software',a.restrictions)
        self.assertTrue(a.fixture_context);self.assertFalse(a.independent_validation_performed)
    def test_fixture_cannot_validate_import(self):
        self.imported();self.row('e-a1')['payload']['data_role']='fixture'
        self.assertIn('fixture_in_import_evidence',self.result().reasons)
    def test_missing_independence_does_not_remove_mechanism(self):
        self.imported();self.row('a1')['evidence_refs'].append(record_ref('independence_assessment','missing'))
        self.assertEqual(self.result().status,'accepted');self.assertIn('independence_not_established',self.result().restrictions)
    def test_sorted_outputs_do_not_identify_algorithm(self):
        self.imported();self.row('e-a1')['payload']['method']=tagged('execution')
        self.assertIn('inappropriate_validation_method',self.result().reasons)
    def test_model_label_and_embedding_methods_do_not_admit(self):
        self.imported()
        for method in ['self_description','model_judge','embedding_similarity','function_name']:
            self.row('e-a1')['payload']['method']=tagged(method)
            with self.subTest(method=method): self.assertEqual(self.result().status,'withheld')
    def test_execution_record_required_for_coding_validity(self):
        self.imported();self.row('e-v1')['payload']['evidence_refs']=[]
        self.assertIn('missing_execution_record',self.result('validity').reasons)
    def test_timeout_cannot_validate_or_invalidate_program(self):
        self.imported();self.row('result-v1')['payload']['outcome']='timeout'
        self.assertIn('execution_record_unresolved',self.result('validity').reasons)
        self.assertEqual(self.result().status,'accepted')
    def test_wrong_execution_subject_is_detected(self):
        self.imported();self.row('result-v1')['payload']['target_ref']=record_ref('realization','s2')
        self.assertIn('execution_subject_mismatch',self.result('validity').reasons)
    def test_repaired_artifact_cannot_validate_original(self):
        self.imported();self.row('s1')['output_content_hash']=tagged('0'*64)
        self.row('e-a1')['payload']['subject_hash']=tagged('1'*64)
        self.assertIn('evidence_subject_hash_mismatch',self.result().reasons)
    def test_missing_text_is_not_automatic_membership_failure(self):
        self.imported();self.assertEqual(self.row('s1')['output_ref']['state'],'unknown')
        self.assertEqual(self.result().status,'accepted')
    def test_inaccessible_essential_report_withholds_label(self):
        self.row('e-a1')['payload']['access']='withheld'
        self.assertEqual(self.result().status,'withheld')
    def test_cycle_of_evidence_support_is_not_grounding(self):
        self.row('e-a1')['payload']['evidence_refs']=[record_ref('evidence','e-a1')]
        self.assertIn('circular_evidence_support',self.result().reasons)
    def test_imported_outcome_conflict_is_not_ignored(self):
        self.imported();self.row('d-a1')['payload']['outcome']=tagged('SORT-HEAP')
        self.assertIn('adjudication_conflict',self.result().reasons)
    def test_missing_reviewer_is_not_adjudication(self):
        self.imported();self.support.remove(self.row('reviewer'))
        self.assertIn('adjudicator_unresolved',self.result().reasons)

    def test_known_malformed_method_is_controlled(self):
        self.imported();self.row('e-a1')['payload']['method']=tagged({'bad':'type'})
        self.assertIn('inappropriate_validation_method',self.result().reasons)

class CorrectionTests(unittest.TestCase):
    setUp=AdmissionTests.setUp
    result=AdmissionTests.result
    row=AdmissionTests.row
    imported=AdmissionTests.imported
    def correction(self,identity='c1',**changes):
        p=dict(target_refs=[record_ref('evidence','e-a1')],effect='membership',action='withdraw',stage='applied',
               reviewer_refs=[record_ref('role','reviewer')],evidence_refs=[record_ref('evidence','e-v1')],
               reason=tagged('Stipulated identity error'),event_type='correction')
        p.update(changes);r=support_record('correction',identity,**p);self.support.append(r);return r
    def test_withdrawal_preserves_other_assignment_and_validity(self):
        self.correction();self.assertEqual(self.result().status,'withheld')
        self.assertEqual(self.result('validity').status,'accepted');self.assertEqual(self.result(sample='s2').status,'accepted')
    def test_independence_only_withdrawal_keeps_label(self):
        self.correction(effect='independence',target_refs=[record_ref('assignment','a1')])
        self.assertEqual(self.result().status,'accepted');self.assertIn('independence_correction:c1',self.result().restrictions)
    def test_shared_schema_challenge_affects_all_dependent_labels(self):
        self.correction(effect='schema',target_refs=[record_ref('frame','frame1')])
        self.assertEqual(self.result().status,'withheld');self.assertEqual(self.result(sample='s2').status,'withheld')
    def test_rejected_challenge_cannot_withdraw(self):
        self.correction(stage='rejected');self.assertEqual(self.result().status,'accepted')
    def test_pending_challenge_is_explicit(self):
        self.correction(stage='pending');self.assertIn('correction_pending:c1',self.result().reasons)
    def test_revision_with_new_evidence_requires_new_pin(self):
        old=self.row('a1');new=copy.deepcopy(old);new.update(record_id='a1-new',assignment_id='a1-new',assignment_version='0.2',structural_class_id='SORT-HEAP',supersedes_assignment_id=tagged('a1'))
        e=copy.deepcopy(self.row('e-a1'));e.update(record_id='e-new');e['payload'].update(target_ref=record_ref('assignment','a1-new'),assertion=tagged('SORT-HEAP'))
        new['evidence_refs']=[record_ref('evidence','e-new')];self.obs.append(new);self.support.append(e)
        self.assertIn('selected_revision_superseded',self.result().reasons)
        self.man['analysis_config']['assignment_pins'][0].update(assignment_id='a1-new',assignment_version='0.2')
        self.assertEqual(self.result().outcome,'SORT-HEAP')
        result=review_evidence(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)))
        self.assertIn(('assignment','a1'),result.preserved_revision_ids)
    def test_cyclic_revision_link_is_detected(self):
        self.row('a1')['supersedes_assignment_id']=tagged('a1')
        self.assertIn('cyclic_revision_history',self.result().reasons)
    def test_cross_sample_predecessor_does_not_merge_samples(self):
        self.row('a1')['supersedes_assignment_id']=tagged('a2')
        self.assertIn('revision_history_unresolved',self.result().reasons)
    def test_impact_records_link_without_recalculating_metrics(self):
        self.correction();review=review_evidence(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man)))
        c=review.corrections[0];self.assertIn('a1',c.affected_record_ids);self.assertNotIn('a2',c.affected_record_ids)
        self.assertFalse(c.numeric_reanalysis_performed)
    def test_raw_bundle_is_unchanged_by_review(self):
        self.correction();bundle=load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))
        before={k:hashlib.sha256(v.content).hexdigest() for k,v in bundle.snapshots.items()}
        first=review_evidence(bundle);second=review_evidence(bundle)
        self.assertEqual(first,second);self.assertEqual(before,{k:v.sha256 for k,v in bundle.snapshots.items()})
    def test_passive_review_never_invokes_network_or_executes(self):
        bundle=load_bundle(self.path)
        with ExitStack() as stack:
            for name in ['socket.socket','urllib.request.urlopen','subprocess.Popen','builtins.eval','builtins.exec']:
                stack.enter_context(patch(name,side_effect=AssertionError('Unexpected active operation')))
            self.assertTrue(review_evidence(bundle).admissions)
