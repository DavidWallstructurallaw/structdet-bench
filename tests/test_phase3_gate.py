"""Phase 3 scaffold tests. Synthetic gate records never establish actual evidence.

No test creates model outputs, computes a longitudinal estimator, or performs a
network read-back. Real predecessor and current runs are recorded by the runner.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tests import phase3_helpers as h
from tools import run_phase3_checks as runner


def synthetic_receipt():
    """Stipulated objects for receipt-validator unit tests; no GitHub activity."""
    inventory = h.inventory_record()
    commit = '1' * 40; tree = inventory['git_tree_sha']
    return {'schema_version': '0.1', 'subject': h.SUBJECT, 'repository': h.REPOSITORY,
            'archive_sha256': h.ARCHIVE_SHA256, 'inventory_sha256': h.INVENTORY_SHA256,
            'status': 'remote_verified', 'fixture_only': False, 'readback_complete': True,
            'verified_files': copy.deepcopy(inventory['files']), 'verified_tree': tree,
            'verified_commit': commit, 'branch': 'unit-fixture',
            'readback_evidence_refs': ['unit-test-only'],
            'readbacks': {'ref': {'ref': 'refs/heads/unit-fixture', 'object': {'type': 'commit', 'sha': commit}},
                          'commit': {'sha': commit, 'tree': {'sha': tree}}}}


def synthetic_gate():
    matrix = h.load_matrix(); ids = h.predecessor_ids()
    # Always a hypothetical Step 1 gate, even when the real project advances.
    matrix['delivery']['step'] = 1
    for group in ('longitudinal', 'reports', 'oracles'):
        for row in matrix[group]: row.update(implementation_status='not_implemented', test_bindings=[])
    for n, row in matrix['stage_bindings'].items():
        if n != '1': row.update(implementation_status='not_implemented', test_bindings=[])
    methods = matrix['stage_bindings']['1']['test_bindings']
    ids = sorted(set(ids + methods))
    # This fabricated completion tests gate mechanics, not the real P3-L01 state.
    matrix['longitudinal'][0].update(implementation_status='implemented', test_bindings=[methods[0]])
    records = [{'test_id': i, 'outcome': 'passed'} for i in ids]
    return dict(matrix=matrix, discovered=ids, records=records, scope='current', predecessor_ids=h.predecessor_ids(),
                inherited_m={'requested_gate_passed': True, 'phase1_m_complete': True},
                inherited_v={'requested_gate_passed': True, 'phase2_v_complete': True},
                reconciliation=synthetic_receipt(), inventory=h.inventory_record())


class MatrixTests(unittest.TestCase):
    def test_actual_catalogues_preserve_40_16_24_plan_rows(self):
        m = h.load_matrix(); self.assertEqual(h.validate_matrix(m), [])
        catalogues = h.plan_catalogues()
        self.assertEqual([len(catalogues[g]) for g in ('longitudinal', 'reports', 'oracles')], [40,16,24])
        for group, specs in catalogues.items():
            self.assertEqual([{k:r[k] for k in s} for r,s in zip(m[group],specs)],specs)

    def test_all_longitudinal_capabilities_start_unimplemented(self):
        m=h.load_matrix()
        initial = m['delivery']['initialization']
        self.assertEqual(initial['step'], 1)
        self.assertEqual(initial['counts'], {'longitudinal':40, 'reports':16, 'oracles':24})
        self.assertEqual(initial['implementation_status'], 'not_implemented')
        self.assertEqual(initial['test_bindings'], [])
        if m['delivery']['step'] == 1:
            self.assertTrue(all(r['implementation_status']=='not_implemented' and r['test_bindings']==[]
                                for g in ('longitudinal','reports','oracles') for r in m[g] if r['id'] != 'P3-L01'))
            first = m['longitudinal'][0]
            if first['implementation_status'] == 'implemented':
                receipt = h.read_json(h.ROOT/'artifacts/phase3/baseline_reconciliation.json')
                self.assertTrue(h.inspect_reconciliation(receipt, h.inventory_record())['record_consistent'])

    def test_plan_is_the_exact_approved_copy(self):
        self.assertEqual(h.digest((h.ROOT/'PHASE_3_PLAN.md').read_bytes()),h.PLAN_SHA256)
        m=h.load_matrix();m['approved_plan']['sha256']='0'*64
        self.assertIn('approved_plan_identity',h.validate_matrix(m))

    def test_source_wording_change_is_rejected(self):
        m=h.load_matrix();m['longitudinal'][0]['requirement']='relaxed'
        self.assertIn('P3-L01:source_row_changed',h.validate_matrix(m))

    def test_missing_duplicate_or_renamed_requirements_are_rejected(self):
        for group in ('longitudinal','reports','oracles'):
            for operation in ('remove','duplicate','rename'):
                m=h.load_matrix()
                if operation=='remove':m[group].pop()
                elif operation=='duplicate':m[group].append(copy.deepcopy(m[group][0]))
                else:m[group][0]['id']='wrong'
                self.assertTrue(h.validate_matrix(m),(group,operation))

    def test_required_by_step_cannot_be_delayed(self):
        m=h.load_matrix();m['longitudinal'][0]['required_by_step']=9
        self.assertIn('P3-L01:source_row_changed',h.validate_matrix(m))

    def test_empty_bindings_cannot_implement_requirement(self):
        m=h.load_matrix()
        self.assertEqual(h.validate_matrix(m), [])
        m['longitudinal'][0].update(implementation_status='implemented', test_bindings=[])
        self.assertIn('P3-L01:empty_bindings',h.validate_matrix(m))

    def test_invalid_duplicate_and_nonlist_bindings_are_rejected(self):
        method=h.load_matrix()['stage_bindings']['1']['test_bindings'][0]
        for bs in (None,'test',[],['arbitrary'],[method,method]):
            m=h.load_matrix();m['stage_bindings']['1']['test_bindings']=bs
            self.assertTrue(h.validate_matrix(m),bs)

    def test_stage_bool_unknown_version_and_missing_authorization_fail(self):
        for key,value in (('step',True),('step',0),('step',11),('authorization',None)):
            m=h.load_matrix();m['delivery'][key]=value;self.assertTrue(h.validate_matrix(m))
        m=h.load_matrix();m['schema_version']='2';self.assertIn('matrix_identity',h.validate_matrix(m))

    def test_nonobject_matrix_fails_closed(self):
        for value in (None,[],False,'matrix'):
            self.assertEqual(h.validate_matrix(value),['phase3_matrix_not_object'])

    def test_E_and_owner_acceptance_never_promoted(self):
        m=h.load_matrix();m['evidence_status']='validated';self.assertTrue(h.validate_matrix(m))
        m=h.load_matrix();m['delivery']['final_owner_acceptance']='approved';self.assertTrue(h.validate_matrix(m))
        m=h.load_matrix();m['longitudinal'][0]['scope']='E';self.assertTrue(h.validate_matrix(m))

    def test_no_future_stage_bound(self):
        m=h.load_matrix();m['delivery']['step']=1
        m['stage_bindings']['2']=copy.deepcopy(m['stage_bindings']['1'])
        self.assertIn('future_stage_bound',h.validate_matrix(m))

    def test_historical_catalogues_and_both_matrices_are_unchanged(self):
        inventory=h.inventory_record();by={r['path']:r for r in inventory['files']}
        for p in ('tests/phase1_matrix.json','tests/phase2_matrix.json'):
            self.assertEqual(h.digest((h.ROOT/p).read_bytes()),by[p]['sha256'])
        m=h.load_matrix();m['legacy_catalogue_identity']['vt']='0'*64
        self.assertIn('historical_catalogues_changed',h.validate_matrix(m))

    def test_stage_bindings_name_every_actual_new_method(self):
        import ast
        classes=ast.parse((h.ROOT/'tests/test_phase3_gate.py').read_text()).body
        names=sorted('tests.test_phase3_gate.'+c.name+'.'+f.name for c in classes if isinstance(c,ast.ClassDef)
                     for f in c.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_'))
        matrix = h.load_matrix()
        all_bindings = {i for r in matrix['stage_bindings'].values() for i in r['test_bindings']}
        self.assertTrue(set(names) <= all_bindings)
        if matrix['delivery']['step'] == 1:
            self.assertEqual(sorted(matrix['stage_bindings']['1']['test_bindings']), names)


class IdentityTests(unittest.TestCase):
    def test_predecessor_1018_ids_and_all_114_files_are_pinned(self):
        self.assertEqual(len(h.predecessor_ids()),1018)
        inv=h.inventory_record();self.assertEqual(len(inv['files']),114)
        self.assertEqual(h.inventory_digest(inv['files']),h.INVENTORY_SHA256)
        self.assertEqual(sum(r['size_bytes'] for r in inv['files']),40699373)

    def test_current_readonly_predecessor_files_are_exact(self):
        results=h.current_identity_checks()
        if h.load_matrix()['delivery']['step'] == 1: self.assertEqual(len(results),113)
        self.assertTrue(all(r['status']=='passed' for r in results))

    def test_inventory_duplicate_path_and_traversal_fail(self):
        rows=copy.deepcopy(h.inventory_record()['files'])
        with self.assertRaises(ValueError):h.inventory_digest(rows+[copy.deepcopy(rows[0])])
        for path in ('../x','/etc/x','a//x','a/./x','a\\x','x\n'):
            bad=copy.deepcopy(rows);bad[0]['path']=path
            with self.assertRaises(ValueError):h.inventory_digest(bad)

    def test_changed_captured_test_id_is_rejected(self):
        actual=h.read_json(h.IDS_PATH);actual['ids'][0]='tests.test_fake.Test.test_changed'
        with patch.object(h,'read_json',return_value=actual):
            with self.assertRaises(ValueError):h.predecessor_ids()

    def test_git_tree_matches_independent_git_hash_object(self):
        # Known published Git empty-tree and empty-blob identities, plus direct
        # independent one-entry serialization. No process or network is invoked.
        self.assertEqual(h.git_tree([]),'4b825dc642cb6eb9a060e54bf8d69288fbee4904')
        self.assertEqual(h.git_blob(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
        blob=h.git_blob(b'abc\n');body=b'100644 file\0'+bytes.fromhex(blob)
        expected=hashlib.sha1(b'tree '+str(len(body)).encode()+b'\0'+body).hexdigest()
        self.assertEqual(h.git_tree([{'path':'file','git_blob_sha':blob}]),expected)

    def test_git_tree_order_is_canonical_and_conflicts_fail(self):
        rows=[{'path':p,'git_blob_sha':h.git_blob(p.encode())} for p in ('a/x','a.txt','z')]
        self.assertEqual(h.git_tree(rows),h.git_tree(list(reversed(rows))))
        for extra in ({'path':'a','git_blob_sha':h.git_blob(b'bad')},rows[0]):
            with self.assertRaises(ValueError):h.git_tree(rows+[extra])

    def test_strict_QA_json_rejects_duplicate_nonfinite_and_symlinks(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'record.json'
            for content in (b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":1e9999}',b'{} trailing',b'\xef\xbb\xbf{}'):
                p.write_bytes(content)
                with self.assertRaises(ValueError):h.read_json(p)
            p.write_text('{}');link=root/'link';link.symlink_to(p)
            with self.assertRaises(ValueError):h.read_json(link)

    def test_qa_symlink_ancestor_rejected(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);real=root/'real';real.mkdir();(real/'x.json').write_text('{}')
            (root/'linked').symlink_to(real,target_is_directory=True)
            with self.assertRaises(ValueError):h.read_json(root/'linked/x.json')


class GateTests(unittest.TestCase):
    def test_synthetic_current_pass_does_not_mean_complete_L_or_live_delivery(self):
        data=synthetic_gate();out=runner.assess_gate(**data)
        self.assertTrue(out['requested_gate_passed']);self.assertTrue(out['local_scaffold_passed'])
        self.assertFalse(out['phase3_l_software_complete'])
        self.assertEqual(out['current_repository_delivery'],'separate_live_audit_required')
        data['scope']='phase3';self.assertFalse(runner.assess_gate(**data)['requested_gate_passed'])

    def test_empty_discovery_fails(self):
        d=synthetic_gate();d['discovered']=[];d['records']=[]
        out=runner.assess_gate(**d);self.assertFalse(out['requested_gate_passed'])
        self.assertIn('zero_discovered_tests',out['reasons'])

    def test_duplicate_discovery_or_execution_fails(self):
        for key in ('discovered','records'):
            d=synthetic_gate();d[key].append(copy.deepcopy(d[key][0]))
            self.assertIn('duplicate_test_identity',runner.assess_gate(**d)['reasons'])

    def test_unexecuted_or_extra_execution_record_fails(self):
        for extra in (False,True):
            d=synthetic_gate()
            if extra:d['records'].append({'test_id':'extra','outcome':'passed'})
            else:d['records'].pop()
            self.assertIn('discovery_execution_mismatch',runner.assess_gate(**d)['reasons'])

    def test_every_nonpassing_status_blocks_acceptance(self):
        for status in ('failed','error','skipped','expected_failure','unexpected_success','not_completed','other'):
            d=synthetic_gate();d['records'][-1]['outcome']=status
            self.assertFalse(runner.assess_gate(**d)['requested_gate_passed'],status)

    def test_missing_predecessor_cannot_hide_behind_nominal_MV_pass(self):
        d=synthetic_gate();name=d['predecessor_ids'][0]
        d['discovered'].remove(name);d['records']=[r for r in d['records'] if r['test_id']!=name]
        self.assertIn('predecessor_test_missing_or_nonpassing',runner.assess_gate(**d)['reasons'])

    def test_inherited_M_or_V_failure_blocks_current(self):
        for key in ('inherited_m','inherited_v'):
            d=synthetic_gate();d[key]['requested_gate_passed']=False
            self.assertFalse(runner.assess_gate(**d)['requested_gate_passed'])

    def test_unexecuted_binding_and_empty_stage_cannot_pass(self):
        for bindings in ([],['tests.test_fake.Missing.test_absent']):
            d=synthetic_gate();d['matrix']['stage_bindings']['1']['test_bindings']=bindings
            self.assertIn('stage_1_not_verified',runner.assess_gate(**d)['reasons'])

    def test_implemented_label_without_execution_does_not_complete_L01(self):
        d=synthetic_gate();d['matrix']['longitudinal'][0]['test_bindings']=['tests.test_fake.Missing.test_absent']
        self.assertIn('P3-L01',runner.assess_gate(**d)['unresolved_current_ids'])

    def test_baseline_pin_or_matrix_errors_block(self):
        for key in ('pin_errors','matrix_errors'):
            d=synthetic_gate();d[key]=['deliberate_error']
            self.assertIn('deliberate_error',runner.assess_gate(**d)['reasons'])

    def test_pending_remote_blocks_current_but_not_local_scaffold(self):
        d=synthetic_gate();d['reconciliation']['status']='pending'
        out=runner.assess_gate(**d)
        self.assertTrue(out['local_scaffold_passed']);self.assertFalse(out['requested_gate_passed'])
        self.assertIn('exact_phase2_baseline_sync_unverified',out['reasons'])

    def test_actual_40_unimplemented_duties_are_not_marked_passed(self):
        d=synthetic_gate()
        d['matrix']['longitudinal'][0].update(implementation_status='not_implemented',test_bindings=[])
        out=runner.assess_gate(**d)
        self.assertEqual(len(out['unresolved_l_ids']),40)
        self.assertFalse(out['substantive_validation_performed'])
        self.assertEqual(out['final_owner_acceptance'],'not_established_by_software_tests')

    def test_unknown_scope_and_malformed_execution_are_controlled(self):
        d=synthetic_gate();d['scope']='other'
        with self.assertRaises(ValueError):runner.assess_gate(**d)
        d=synthetic_gate();d['records']=[{}]
        self.assertIn('invalid_execution_records',runner.assess_gate(**d)['reasons'])

    def test_setup_error_from_actual_unittest_runner_is_retained(self):
        class Broken(unittest.TestCase):
            @classmethod
            def setUpClass(cls):raise RuntimeError('stipulated setup error')
            def test_not_reached(self):pass
        ids,rows,console=runner.mr.execute_suite(unittest.defaultTestLoader.loadTestsFromTestCase(Broken))
        self.assertTrue(any(r['outcome']=='error' for r in rows))
        self.assertIn('stipulated setup error',console)
        d=synthetic_gate();d['discovered']+=ids;d['records']+=rows
        self.assertFalse(runner.assess_gate(**d)['requested_gate_passed'])

    def test_annotations_preserve_actual_outcomes_and_scoped_bindings(self):
        d=synthetic_gate();m=runner.vh.load_phase1_matrix();v=runner.vh.read_matrix()
        records=runner.annotate_results(d['matrix'],d['records'][-2:],m,v,environment={'fixture':True})
        for r in records:
            self.assertEqual(r['expected_outcome'],'passed');self.assertEqual(r['actual_outcome'],r['outcome'])
            self.assertEqual(r['execution_phase'],3);self.assertFalse(r['substantive_validation_performed'])
            self.assertEqual(r['phase3_plan_identity']['sha256'],h.PLAN_SHA256)


class ReconciliationTests(unittest.TestCase):
    def test_old_phase1_receipt_and_published_boolean_are_insufficient(self):
        old=h.read_json(h.ROOT/'artifacts/phase2/baseline_reconciliation.json')
        out=h.inspect_reconciliation(old,h.inventory_record())
        self.assertFalse(out['record_consistent']);self.assertIn('reconciliation_subject',out['errors'])
        self.assertFalse(h.inspect_reconciliation({'published':True},h.inventory_record())['record_consistent'])

    def test_offline_good_receipt_never_claims_current_remote(self):
        out=h.inspect_reconciliation(synthetic_receipt(),h.inventory_record())
        self.assertTrue(out['record_consistent']);self.assertFalse(out['current_branch_verified'])
        self.assertEqual(out['assurance'],'offline_saved_receipt_only')

    def test_wrong_repo_scope_inventory_or_archive_is_rejected(self):
        for key,value in (('repository','other/repo'),('subject','phase1'),('inventory_sha256','0'*64),('archive_sha256','0'*64)):
            r=synthetic_receipt();r[key]=value
            self.assertFalse(h.inspect_reconciliation(r,h.inventory_record())['record_consistent'])

    def test_missing_file_and_wrong_tree_rejected(self):
        r=synthetic_receipt();r['verified_files'].pop()
        self.assertFalse(h.inspect_reconciliation(r,h.inventory_record())['record_consistent'])
        r=synthetic_receipt();r['verified_tree']='0'*40
        self.assertFalse(h.inspect_reconciliation(r,h.inventory_record())['record_consistent'])

    def test_commit_and_branch_linkage_must_match(self):
        r=synthetic_receipt();r['readbacks']['ref']['object']['sha']='2'*40
        self.assertIn('readback_link_mismatch',h.inspect_reconciliation(r,h.inventory_record())['errors'])

    def test_mock_receipt_cannot_be_actual_delivery_evidence(self):
        r=synthetic_receipt();r['fixture_only']=True
        self.assertIn('remote_receipt_not_actual_evidence',h.inspect_reconciliation(r,h.inventory_record())['errors'])

    def test_fresh_observation_is_a_separate_required_input(self):
        r=synthetic_receipt();out=h.match_current_observation(r,None,h.inventory_record())
        self.assertFalse(out['observed_subject_matches']);self.assertIn('live_observation_missing',out['errors'])

    def test_changed_live_ref_or_truncated_tree_is_rejected(self):
        r=synthetic_receipt();inv=h.inventory_record()
        obs={'origin':'connector_readback','subject':h.SUBJECT,'repository':h.REPOSITORY,
             'commit':r['verified_commit'],'tree':inv['git_tree_sha'],'files':inv['files'],
             'truncated':False,'fixture_only':False,'evidence_refs':['unit-test-only']}
        out=h.match_current_observation(r,obs,inv)
        self.assertTrue(out['observed_subject_matches']);self.assertFalse(out['network_request_performed'])
        obs['commit']='2'*40
        self.assertIn('live_ref_moved_or_tree_changed',h.match_current_observation(r,obs,inv)['errors'])
        obs['commit']=r['verified_commit'];obs['truncated']=True
        self.assertFalse(h.match_current_observation(r,obs,inv)['observed_subject_matches'])


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'qa'
    def run_record(self,number=1):
        return {'run_id':f'{number:032x}','exit_code':1,'console_output':'Stipulated test log\n',
                'file_fingerprints':{'sample':'0'*64},'acceptance':{'outcome_counts':{'passed':1}}}

    def test_append_preserves_prior_full_run_bytes(self):
        runner.append_journal(self.root,self.run_record())
        path=self.root/'history'/f'{1:032x}'/'run.json';before=path.read_bytes()
        runner.append_journal(self.root,self.run_record(2));self.assertEqual(path.read_bytes(),before)
        self.assertEqual(len(runner.check_journal(self.root)['runs']),2)

    def test_missing_full_run_cannot_be_replaced_by_summary(self):
        runner.append_journal(self.root,self.run_record())
        (self.root/'history'/f'{1:032x}'/'run.json').unlink()
        with self.assertRaises(ValueError):runner.check_journal(self.root)

    def test_modified_full_console_is_detected(self):
        runner.append_journal(self.root,self.run_record())
        (self.root/'history'/f'{1:032x}'/'console.txt').write_text('changed')
        with self.assertRaises(ValueError):runner.check_journal(self.root)

    def test_duplicate_run_id_refused(self):
        runner.append_journal(self.root,self.run_record())
        with self.assertRaises(ValueError):runner.append_journal(self.root,self.run_record())

    def test_traversal_and_nonopaque_run_ids_are_refused(self):
        for name in ('../outside','x/y','not-a-uuid','A'*32,'1'*33):
            r=self.run_record();r['run_id']=name
            with self.assertRaises(ValueError):runner.append_journal(self.root,r)

    def test_tampered_index_chain_is_detected(self):
        runner.append_journal(self.root,self.run_record());p=self.root/'test_results.json'
        obj=json.loads(p.read_text());obj['runs'][0]['exit_code']=0;p.write_bytes(h.canonical(obj))
        with self.assertRaises(ValueError):runner.check_journal(self.root)

    def test_interrupted_index_publication_fails_next_append(self):
        with patch('tools.run_phase3_checks.os.replace',side_effect=OSError('injected index failure')):
            with self.assertRaises(OSError):runner.append_journal(self.root,self.run_record())
        with self.assertRaises(ValueError):runner.append_journal(self.root,self.run_record(2))

    def test_symlink_journal_or_history_is_rejected(self):
        self.root.mkdir();outside=self.root.parent/'outside';outside.mkdir()
        (self.root/'history').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError):runner.append_journal(self.root,self.run_record())

    def test_incomplete_index_pair_is_rejected(self):
        self.root.mkdir();(self.root/'test_output.txt').write_text('without index')
        with self.assertRaises(ValueError):runner.check_journal(self.root)

    def test_full_runs_have_actual_hash_and_size_references(self):
        runner.append_journal(self.root,self.run_record());r=runner.check_journal(self.root)['runs'][0]
        for kind in ('run','console','files'):
            b=(self.root/r[kind+'_path']).read_bytes()
            self.assertEqual(h.digest(b),r[kind+'_sha256']);self.assertEqual(len(b),r[kind+'_bytes'])


class BoundaryTests(unittest.TestCase):
    def test_no_longitudinal_runtime_has_been_created(self):
        step = h.load_matrix()['delivery']['step']
        stages = {'longitudinal_records':2, 'longitudinal':3, 'categorical_null':4,
                  'half_life':5, 'longitudinal_uncertainty':5, 'support_assays':6,
                  'recovery':7, 'longitudinal_pipeline':8}
        for name, first_step in stages.items():
            if step < first_step:
                self.assertFalse((h.ROOT/'structdet_bench'/(name+'.py')).exists())
        for name in ('generate', 'train', 'execute', 'judge'):
            self.assertFalse((h.ROOT/'structdet_bench'/(name+'.py')).exists())

    def test_gate_assessment_has_no_network_process_or_file_side_effect(self):
        d=synthetic_gate()
        with patch('socket.socket',side_effect=AssertionError('network')), \
             patch('subprocess.Popen',side_effect=AssertionError('process')), \
             patch('builtins.open',side_effect=AssertionError('file')):
            out=runner.assess_gate(**d)
        self.assertTrue(out['local_scaffold_passed'])

    def test_runner_scopes_are_only_current_and_phase3(self):
        import contextlib,io
        for scope in ('phase2','generate','train'):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:runner.main(['--scope',scope])
            self.assertEqual(caught.exception.code,2)

    def test_invalid_matrix_never_executes_or_appends_success(self):
        import contextlib,io
        with patch.object(h,'load_matrix',return_value=None),patch.object(runner.mr,'execute_suite') as execute, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(['--scope','current']),2)
            execute.assert_not_called()
