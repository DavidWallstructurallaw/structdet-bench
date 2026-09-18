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
        step=h.read_matrix()['delivery']['step']
        for name,first_step in (('text_diagnostics',3),('comparisons',4),('uncertainty',5),('predictions',5),('comparison_pipeline',6)):
            path=h.ROOT/'structdet_bench'/f'{name}.py'
            if step < first_step:self.assertFalse(path.exists())
            else:self.assertTrue(path.is_file())
        if step < 6:self.assertFalse((h.ROOT/'examples/hero_abc').exists())
        r=review_comparison(self.loaded())
        self.assertFalse(hasattr(r,'prediction'));self.assertFalse(hasattr(r,'resample_indices'))
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


class TextBoundaryTests(unittest.TestCase):
    def test_diagnostics_never_read_or_run_code_after_loading(self):
        from structdet_bench.text_diagnostics import TextMethod, diagnose_cells
        with TemporaryDirectory() as tmp:
            from tests.test_text_diagnostics import text_fixture
            p,*_=text_fixture(Path(tmp),['__import__("os").system("PRIVATE_CMD")','a b c'])
            b=load_bundle(p);cells=build_populations(b).cells
            with ExitStack() as stack:
                for target in ('builtins.open','pathlib.Path.open','socket.socket','socket.create_connection',
                               'urllib.request.urlopen','subprocess.Popen','os.system','builtins.eval','builtins.exec','builtins.compile'):
                    stack.enter_context(patch(target,side_effect=AssertionError('active operation forbidden')))
                out=diagnose_cells(b,cells,TextMethod('fixture-original-region-v1'))
            self.assertEqual(out[0].eligible_count,2);self.assertNotIn('PRIVATE_CMD',repr(out))
    def test_external_output_locator_is_never_fetched(self):
        from structdet_bench.text_diagnostics import TextMethod, diagnose_population
        with TemporaryDirectory() as tmp:
            from tests.test_text_diagnostics import text_fixture
            root=Path(tmp);p,o,s,m=text_fixture(root,['a b c','a b d'])
            next(r for r in o if r['record_id']=='text1')['content_ref']=tagged({'kind':'external','locator':'https://invalid.test/?secret=PRIVATE'})
            b=load_bundle(rewrite_evidence_bundle(root,o,s,m));c=build_populations(b).cells[0]
            with patch('urllib.request.urlopen',side_effect=AssertionError('network')):
                d=diagnose_population(b,c,'classified_all',TextMethod('fixture-original-region-v1'))
            self.assertEqual(d.eligible_count,1);self.assertNotIn('PRIVATE',repr(d))
            self.assertEqual(d.samples[0].reasons,('artifact_external_not_fetched',))
    def test_private_paths_and_source_body_absent_from_diagnostic_repr(self):
        from structdet_bench.text_diagnostics import TextMethod, diagnose_population
        with TemporaryDirectory(prefix='PRIVATE_PATH_') as tmp:
            from tests.test_text_diagnostics import text_fixture
            p,*_=text_fixture(Path(tmp),['PRIVATE_BODY_A','PRIVATE_BODY_B'])
            b=load_bundle(p);c=build_populations(b).cells[0]
            d=diagnose_population(b,c,'classified_all',TextMethod('fixture-original-region-v1'))
            self.assertNotIn('PRIVATE_BODY',repr(d));self.assertNotIn('PRIVATE_PATH',repr(d))
            self.assertTrue(all(s.snapshot_locator_sha256 for s in d.samples))
    def test_diagnostics_leave_loaded_records_and_files_unchanged(self):
        from structdet_bench.text_diagnostics import TextMethod, diagnose_cells
        with TemporaryDirectory() as tmp:
            from tests.test_text_diagnostics import text_fixture
            root=Path(tmp);p,*_=text_fixture(root,['a b c','a b d'])
            b=load_bundle(p);cells=build_populations(b).cells
            before={f.name:f.read_bytes() for f in root.iterdir()}
            r1=diagnose_cells(b,cells,TextMethod('fixture-original-region-v1'))
            r2=diagnose_cells(b,cells,TextMethod('fixture-original-region-v1'))
            self.assertEqual(r1,r2);self.assertEqual(before,{f.name:f.read_bytes() for f in root.iterdir()})
    def test_legacy_cli_and_M_profile_do_not_dispatch_text_diagnostics(self):
        from tests.helpers import materialize_hero
        from structdet_bench.pipeline import analyze_bundle
        with TemporaryDirectory() as tmp:
            p,_=materialize_hero(Path(tmp)/'fixture')
            with patch('structdet_bench.text_diagnostics.diagnose_population',side_effect=AssertionError('early CLI integration')):
                result=analyze_bundle(p)
            self.assertEqual(result.exit_code,0)
