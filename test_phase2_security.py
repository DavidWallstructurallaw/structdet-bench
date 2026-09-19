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


class Step6CommandBoundaries(unittest.TestCase):
    """Run the trusted CLI only; fixture programs are never executed."""
    def setUp(self):
        import tempfile
        from pathlib import Path
        from tests.phase2_helpers import materialize_abc
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.bundle,_=materialize_abc(self.root/'input')
    def run_cli(self,*args):
        import subprocess,sys,os
        from tests.phase2_helpers import ROOT
        return subprocess.run([sys.executable,'-B','-S','-m','structdet_bench',*args],cwd=ROOT,
             env={k:v for k,v in os.environ.items() if k in {'PATH','TMPDIR'}},capture_output=True,timeout=120)
    def test_validate_reads_comparison_without_writing_or_resampling(self):
        import json
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        r=self.run_cli('validate','--bundle',str(self.bundle));self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue(json.loads(r.stdout)['comparison']['requested'])
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_analyze_produces_only_fixed_three_files(self):
        import json
        r=self.run_cli('analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out'))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual({p.name for p in (self.root/'out').iterdir()},{'report.json','report.md','run_manifest.json'})
        m=json.loads((self.root/'out/run_manifest.json').read_text());self.assertEqual(len(m['comparison_replay']['replays'][0]['indices']),2000)
    def test_malformed_comparison_returns_two_and_preserves_error_report(self):
        import json
        m=json.loads(self.bundle.read_text());m['analysis_config']['extensions']['comparison']=False;self.bundle.write_text(json.dumps(m))
        r=self.run_cli('analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out'))
        self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stdout)['processing_exit_code'],2)
    def test_existing_output_directory_never_overwritten(self):
        (self.root/'out').mkdir();(self.root/'out/keep').write_bytes(b'unchanged')
        r=self.run_cli('analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out'))
        self.assertEqual(r.returncode,2);self.assertEqual((self.root/'out/keep').read_bytes(),b'unchanged')
    def test_active_commands_and_private_argument_echo_remain_disabled(self):
        for name in ('compare','generate','execute','train','judge'):
            r=self.run_cli(name,'--token=PRIVATE_SENTINEL');self.assertEqual(r.returncode,2);self.assertNotIn(b'PRIVATE_SENTINEL',r.stderr)
    def test_local_comparison_exception_is_three_without_sensitive_traceback(self):
        from unittest.mock import patch
        from contextlib import redirect_stderr
        from structdet_bench.cli import main
        import io
        err=io.StringIO()
        with patch('structdet_bench.comparison_pipeline.analyze_comparison',side_effect=RuntimeError('PRIVATE_SENTINEL')),redirect_stderr(err):
            code=main(['analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out')])
        self.assertEqual(code,3);self.assertNotIn('PRIVATE_SENTINEL',err.getvalue());self.assertFalse((self.root/'out').exists())


class Step7SecurityAudit(unittest.TestCase):
    """Whole V path remains passive with controlled adverse local material."""
    def setUp(self):
        from tests.phase2_helpers import materialize_abc
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.p,_=materialize_abc(self.root/'input')
    def edit(self,fn):
        from tests.test_phase2_pipeline import fixture_rows
        from tests.phase2_helpers import write_abc
        o,s,m=fixture_rows(self.p);fn(o,s,m);return write_abc(self.p.parent,o,s,m)
    def test_hostile_evidence_and_text_never_execute_or_contact_sources(self):
        from structdet_bench.pipeline import analyze_bundle,write_analysis
        from tests.test_phase2_pipeline import content
        secret='PRIVATE_PAYLOAD __import__("os").system("echo forbidden")'
        self.edit(lambda o,s,m:next(x for x in s if x['record_type']=='evidence')['payload'].update(detail=tagged(secret)))
        with ExitStack() as stack:
            for target in ('socket.socket','socket.create_connection','urllib.request.urlopen','subprocess.Popen','os.system','builtins.eval'):
                stack.enter_context(patch(target,side_effect=AssertionError('active operation forbidden')))
            r=analyze_bundle(self.p);write_analysis(r,self.root/'out',bundle_path=self.p)
        self.assertEqual(r.exit_code,0);self.assertEqual(r.manifest['model_calls'],0)
        self.assertEqual(r.manifest['candidate_programs_executed'],0)
        for data in (r.report_json,r.report_markdown,r.manifest_json):self.assertNotIn(b'PRIVATE_PAYLOAD',data)
        self.assertEqual(content(r)['predictions']['P1']['outcome'],'supporting')
    def test_external_replay_remains_inert_and_has_no_generated_fallback(self):
        from tests.helpers import artifact_record
        from structdet_bench.pipeline import analyze_bundle
        from tests.test_phase2_pipeline import content
        def attach(o,s,m):
            a=artifact_record('external-replay');a['content_ref']=tagged({'kind':'external','locator':'https://invalid.test/?token=PRIVATE_REPLAY'})
            o.append(a);m['analysis_config']['extensions']['comparison']['resampling']['replay_ref']=tagged(record_ref('artifact','external-replay'))
        self.edit(attach)
        with patch('urllib.request.urlopen',side_effect=AssertionError('network')),patch('structdet_bench.uncertainty.make_replay',side_effect=AssertionError('unrequested replacement')):
            r=analyze_bundle(self.p)
        self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated')
        self.assertFalse(r.manifest['comparison_replay']['replays'])
        self.assertNotIn(b'PRIVATE_REPLAY',r.report_json+r.report_markdown+r.manifest_json)
    def test_replay_duplicate_key_failure_preserves_M_without_numeric_fallback(self):
        from tests.helpers import artifact_record
        from structdet_bench.pipeline import analyze_bundle
        from tests.test_phase2_pipeline import content
        (self.p.parent/'broken-replay.json').write_bytes(b'{"schema_version":"0.1","schema_version":"9","replays":[]}')
        self.edit(lambda o,s,m:(o.append(artifact_record('bad-replay','broken-replay.json')),m['analysis_config']['extensions']['comparison']['resampling'].update(replay_ref=tagged(record_ref('artifact','bad-replay')))))
        with patch('structdet_bench.uncertainty.make_replay',side_effect=AssertionError('fallback')):r=analyze_bundle(self.p)
        self.assertEqual(r.exit_code,2);self.assertEqual(content(r)['predictions']['P5']['outcome'],'not_evaluated')
        self.assertEqual(sum(x['selected_realization_count']['value'] for x in content(r,2)['inventory']),360)
    def test_V_publication_race_keeps_other_writer_and_cleans_staging(self):
        from tests.test_phase2_pipeline import base_result
        from structdet_bench.pipeline import write_analysis
        from structdet_bench.contracts import InputError
        from structdet_bench import local_io
        rename=local_io._rename_noreplace
        def race(fd,old,new):
            (self.root/new).mkdir();(self.root/new/'keep').write_bytes(b'concurrent writer')
            return rename(fd,old,new)
        with patch.object(local_io,'_rename_noreplace',side_effect=race):
            with self.assertRaises(InputError):write_analysis(base_result(),self.root/'out',bundle_path=self.p)
        self.assertEqual((self.root/'out/keep').read_bytes(),b'concurrent writer')
        self.assertFalse(list(self.root.glob('.structdet-*')))
    def test_V_output_symlink_and_traversal_are_rejected(self):
        from tests.test_phase2_pipeline import base_result
        from structdet_bench.pipeline import write_analysis
        from structdet_bench.contracts import InputError
        (self.root/'link').symlink_to(self.p.parent,target_is_directory=True)
        for out in (self.root/'link/out',self.p.parent/'out','../escaped'):
            with self.subTest(out=str(out)):
                with self.assertRaises(InputError):write_analysis(base_result(),out,bundle_path=self.p)
        self.assertFalse((self.p.parent/'out').exists())
    def test_pair_resource_failure_preserves_full_intended_target_and_P5(self):
        from structdet_bench.pipeline import analyze_bundle
        from tests.test_phase2_pipeline import content
        self.edit(lambda o,s,m:m['analysis_config']['extensions']['comparison']['limits'].update(max_pairs=1))
        r=analyze_bundle(self.p);c=content(r)
        self.assertEqual(c['predictions']['P1']['outcome'],'not_evaluated')
        self.assertEqual(c['predictions']['P5']['outcome'],'supporting')
        self.assertEqual(len(c['equal_block_means'][0]['intended_blocks']),6)
        self.assertEqual(sum(x['selected_realization_count']['value'] for x in content(r,2)['inventory']),360)
        for d in content(r,7)['diagnostics']:
            self.assertEqual(d['eligible_count'],20)
            self.assertNotEqual(d['results']['surface_lexical_trigram_distance']['result_status'],'available')
    def test_combined_file_identity_and_expiry_checks_are_passive(self):
        from structdet_bench.pipeline import _declared_date
        from structdet_bench.text_diagnostics import text_input_fingerprint
        from tests.test_phase2_pipeline import Step7SnapshotAudit
        case=Step7SnapshotAudit();case.setUp()
        try:
            b,p,d=case.context()
            with patch('builtins.open',side_effect=AssertionError('I/O')),patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):
                self.assertEqual(len(text_input_fingerprint(b,p.cells[0],'classified_all')),64)
                date=_declared_date(tagged('2026-10-01'))
                secret=_declared_date(tagged('PRIVATE_DATE<script>run()</script>'))
            self.assertEqual(date['value'],'2026-10-01')
            self.assertNotIn('PRIVATE_DATE',json.dumps(secret))
        finally:case.doCleanups()
