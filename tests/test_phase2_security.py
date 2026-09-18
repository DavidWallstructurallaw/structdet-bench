"""Passive comparison inputs, private context, and strict scope boundaries.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import copy
from contextlib import ExitStack
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from tests import phase2_helpers as h
from tests.helpers import tagged, record_ref, rewrite_evidence_bundle, population_bundle
from structdet_bench.comparison_records import review_comparison, configuration_fingerprint, MAX_LINKS
from structdet_bench.local_io import load_bundle
from structdet_bench.populations import build_populations
from structdet_bench.metrics import cell_metrics

class ComparisonBoundaryTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.path,self.obs,self.sup,self.man=h.comparison_fixture(self.root)
    def loaded(self):
        return load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.sup,self.man))
    def test_review_has_no_io_network_model_or_subprocess_operation(self):
        b=self.loaded()
        with ExitStack() as stack:
            for target in ('builtins.open','socket.socket','socket.create_connection','urllib.request.urlopen','subprocess.Popen','os.system'):
                stack.enter_context(patch(target,side_effect=AssertionError('active operation forbidden')))
            r=review_comparison(b)
        self.assertEqual(len(r.bindings),18)
    def test_unknown_external_prompt_is_not_fetched(self):
        artifact=next(x for x in self.obs if x['record_id']=='prompt-P01-A')
        artifact['content_ref']=tagged({'kind':'external','locator':'https://example.invalid/?secret=PRIVATE'})
        b=self.loaded()
        with patch('urllib.request.urlopen',side_effect=AssertionError('external fetch')):r=review_comparison(b)
        a=next(x for x in r.bindings if x.cell_id=='P01-A')
        self.assertEqual(a.status,'record_limited');self.assertNotIn('PRIVATE',repr(r))
    def test_instruction_text_is_only_retained_as_data(self):
        cfg=self.man['analysis_config']['extensions']['comparison'];text='__import__("os").system("DO_NOT_EXECUTE")'
        cfg['revision']['changes']=[text]
        r=review_comparison(self.loaded())
        self.assertEqual(r.configuration['revision']['changes'],(text,));self.assertNotIn(text,repr(r))
    def test_private_context_does_not_leak_in_default_representation(self):
        proof=next(x for x in self.sup if x['record_id']=='study-P01-A')
        proof['payload']['origin']=tagged('PRIVATE_ORIGIN_AND_IDENTITY')
        proof['payload']['detail']=tagged('PRIVATE_DETAIL')
        r=review_comparison(self.loaded())
        self.assertNotIn('PRIVATE_ORIGIN',repr(r));self.assertNotIn('PRIVATE_DETAIL',repr(r))
        # The original loaded bundle retains the evidence; repr is not a public report.
        self.assertEqual(proof['payload']['origin']['value'],'PRIVATE_ORIGIN_AND_IDENTITY')
    def test_malformed_extension_does_not_change_existing_M_populations(self):
        with TemporaryDirectory() as t:
            root=Path(t);p,o,s,m=population_bundle(root,['SORT-ADJ','SORT-INS'])
            b=load_bundle(p);before=cell_metrics(build_populations(b).cells[0])
            m['analysis_config']['extensions']={'comparison':{'all_gates_passed':True}}
            b=load_bundle(rewrite_evidence_bundle(root,o,s,m));r=review_comparison(b)
            after=cell_metrics(build_populations(b).cells[0])
            self.assertEqual(r.status,'contract_error')
            self.assertEqual(before.distributions,after.distributions)
    def test_absent_and_malformed_comparison_are_distinct(self):
        self.man['analysis_config']['extensions']={};a=review_comparison(self.loaded())
        self.man['analysis_config']['extensions']['comparison']=False;b=review_comparison(self.loaded())
        self.assertEqual((a.status,b.status),('not_requested','contract_error'))
        self.assertFalse(a.requested);self.assertTrue(b.requested)
    def test_snapshot_bytes_used_even_if_disk_changes_after_loading(self):
        b=self.loaded();(self.root/'prompt-P01-A.txt').write_bytes(b'changed on disk')
        r=review_comparison(b);a=next(x for x in r.bindings if x.cell_id=='P01-A')
        self.assertEqual(next(f for f in a.facts if f.name=='exact_prompt_assembly').status,'record_consistent')
    def test_raw_artifact_hash_mismatch_stays_scoped(self):
        a=next(x for x in self.obs if x['record_id']=='prompt-P01-B');a['expected_sha256']=tagged('0'*64)
        r=review_comparison(self.loaded());states={x.cell_id:x.status for x in r.bindings}
        self.assertEqual(states['P01-A'],'record_consistent');self.assertEqual(states['P01-C'],'record_consistent')
        self.assertEqual(states['P01-B'],'record_limited')
    def test_source_storage_order_does_not_change_binding_results(self):
        a=review_comparison(self.loaded());self.obs.reverse();self.sup.reverse();b=review_comparison(self.loaded())
        self.assertEqual(a,b)
    def test_exact_configuration_fingerprint_is_type_and_order_safe(self):
        a={'a':1,'b':['number_token','0.4']};b={'b':['number_token','0.4'],'a':1}
        self.assertEqual(configuration_fingerprint(a),configuration_fingerprint(b))
        self.assertNotEqual(configuration_fingerprint({'a':True}),configuration_fingerprint({'a':1}))
        from structdet_bench.contracts import ExactNumber
        self.assertNotEqual(configuration_fingerprint({'a':ExactNumber('0.4')}),configuration_fingerprint({'a':['number_token','0.4']}))
    def test_duplicate_json_keys_fail_in_existing_loader(self):
        self.path.write_bytes(b'{"analysis_config":{},"analysis_config":{}}')
        b=load_bundle(self.path);self.assertTrue(b.has_errors)
        self.assertEqual(review_comparison(b).status,'unavailable')
    def test_dependency_limit_fails_explicitly_without_dropping_cells(self):
        b=self.loaded()
        with patch('structdet_bench.comparison_records.MAX_LINKS',1):r=review_comparison(b)
        # Shape list budget also fails explicitly instead of trimming the input.
        self.assertIn(r.status,('contract_error','record_limited'))
    def test_unknown_payload_code_is_not_an_extension_plugin(self):
        study=next(x for x in self.sup if x['record_id']=='study-P01-A')['payload']['extensions']['study_binding']
        study['execute']='PRIVATE_COMMAND';r=review_comparison(self.loaded())
        self.assertEqual(next(x for x in r.bindings if x.cell_id=='P01-A').status,'contract_error')
        self.assertNotIn('PRIVATE_COMMAND',repr(r))
    def test_future_components_and_output_example_are_not_implemented(self):
        for name in ('text_diagnostics','comparisons','uncertainty','predictions','comparison_pipeline'):
            self.assertFalse((h.ROOT/'structdet_bench'/f'{name}.py').exists())
        self.assertFalse((h.ROOT/'examples/hero_abc').exists())
    def test_declared_replay_is_retained_without_generating_indices(self):
        cfg=self.man['analysis_config']['extensions']['comparison']
        cfg['resampling']['replay_ref']=tagged(record_ref('artifact','absent-replay'))
        r=review_comparison(self.loaded())
        self.assertEqual(r.configuration['resampling']['replay_ref']['value']['record_id'],'absent-replay')
        self.assertFalse(hasattr(r,'resample_indices'));self.assertFalse(hasattr(r,'prediction'))

class DeploymentEvidenceBoundary(unittest.TestCase):
    def test_unrelated_control_evidence_cannot_validate_serving_stability(self):
        with TemporaryDirectory() as d:
            root=Path(d);p,o,s,m=h.comparison_fixture(root)
            proof=next(r for r in s if r['record_id']=='controls-P01-A')
            del proof['payload']['extensions']['recorded_deployment']
            r=review_comparison(load_bundle(rewrite_evidence_bundle(root,o,s,m)))
            a=next(x for x in r.bindings if x.cell_id=='P01-A')
            self.assertEqual(next(f for f in a.facts if f.name=='deployment_unchanged').status,'unresolved')
            self.assertEqual(next(f for f in a.facts if f.name=='control_temperature').status,'record_consistent')
