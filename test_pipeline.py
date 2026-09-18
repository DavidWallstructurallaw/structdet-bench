"""End-to-end fixtures and CLI. Source programs and real annotators are absent."""
from __future__ import annotations
import copy
import tempfile
from contextlib import ExitStack
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench.pipeline import analyze_bundle, validate_bundle, write_analysis
from structdet_bench.reporting import plain
from structdet_bench.contracts import InputError
from tests.helpers import (ROOT, materialize_hero, tagged, population_bundle, rewrite_evidence_bundle,
                           evidence_bundle, support_record, record_ref)

STAMP = "2026-09-17T23:00:00+00:00"


def section(result, n):
    return plain(result.report)["sections"][n-1]["content"]


def numeric(result, view="classified_all"):
    return {r["metric_name"]: r for r in section(result,4)["metrics"] if r["analysis_population"]==view}


class HeroPipelineTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
    def fixture(self,id_="HF-00"):
        return materialize_hero(self.root/id_,id_)
    def check_expected(self,id_):
        p,e=self.fixture(id_);before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.parent.iterdir()}
        r=analyze_bundle(p,recorded_at=STAMP)
        self.assertEqual(r.exit_code,e['exit_code'])
        inv=section(r,2)['inventory'][0]
        self.assertEqual(inv['realization_count']['value'],e['actual_realizations'])
        self.assertEqual(inv['selected_realization_count']['value'],e['selected'])
        self.assertEqual(inv['planned_positions'],20)
        for view in ('classified_all','classified_valid'):
            actual=numeric(r,view);expected=e[view]
            self.assertTrue(all(m['population_size']==expected['population_size'] for m in actual.values()))
            for key,value in expected.items():
                if key=='population_size':continue
                got=actual[key]
                self.assertEqual(got['result_status'],'available')
                if isinstance(value,dict):
                    self.assertEqual(got['exact_ratio'],[value['numerator'],value['denominator']])
                elif isinstance(value,str):
                    self.assertLessEqual(abs(got['value']-float(Decimal(value))),1e-12+1e-10*abs(float(value)))
                else:self.assertEqual(got['value'],value)
            prefs=[x for x in section(r,5)['prefixes'] if x['analysis_population']==view]
            self.assertEqual([x['value'] for x in prefs],e['prefix_all' if view=='classified_all' else 'prefix_valid'])
            for x in prefs:
                if x['value'] is None:self.assertEqual(x['result_status'],'unavailable')
        self.assertEqual(section(r,1)['scope']['permitted_claim_scope'],'fixture_only')
        self.assertFalse(r.manifest['independent_validation_performed'])
        self.assertEqual(r.manifest['model_calls'],0)
        self.assertEqual(before,{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.parent.iterdir()})
        return r
    def test_hf00_original_twenty_record_workflow(self):self.check_expected('HF-00')
    def test_hf01_invalid_but_classifiable(self):
        r=self.check_expected('HF-01');self.assertEqual(section(r,3)['accounting'][0]['valid_fraction_selected']['numerator'],19)
    def test_hf02_unresolved_class_keeps_validity(self):
        r=self.check_expected('HF-02');self.assertEqual(section(r,3)['accounting'][0]['valid_fraction_selected']['numerator'],20)
    def test_hf03_provisional_label_has_distinct_reason(self):
        r=self.check_expected('HF-03')
        a=next(x for x in section(r,3)['admissions'] if x['axis']=='assignment' and x['sample_id']=='s10')
        self.assertIn('provisional_judgment',a['reasons'])
    def test_hf04_missing_evidence_is_local_limit(self):
        r=self.check_expected('HF-04')
        self.assertIn('missing_reference',[d['code'] for d in section(r,2)['diagnostics']])
        self.assertEqual(section(r,3)['accounting'][0]['valid_fraction_selected']['numerator'],20)
    def test_hf05_missing_position_is_not_backfilled(self):
        r=self.check_expected('HF-05');self.assertEqual(section(r,2)['inventory'][0]['missing_position_count'],1)
    def test_hf06_new_assignment_preserves_old_identity(self):
        r=self.check_expected('HF-06')
        refs=section(r,8)['preserved_revision_ids']
        self.assertIn(['assignment','a10'],refs);self.assertIn(['assignment','a10-r2'],refs)
        self.assertTrue(section(r,8)['corrections'][0]['m_fields_recomputed_from_pinned_input'])
        self.assertFalse(section(r,8)['corrections'][0]['prior_results_modified'])
    def test_pinned_base_remains_byte_identical_after_all_variants(self):
        before={p.name:p.read_bytes() for p in (ROOT/'examples/hero_hf00').iterdir()}
        for i in range(7):self.fixture(f'HF-{i:02}')
        self.assertEqual(before,{p.name:p.read_bytes() for p in (ROOT/'examples/hero_hf00').iterdir()})
    def test_materializer_refuses_unregistered_variant(self):
        with self.assertRaises(ValueError):materialize_hero(self.root/'x','arbitrary-user-transform')
    def test_hf00_materialization_matches_pinned_original(self):
        p,_=self.fixture()
        for f in p.parent.iterdir():self.assertEqual(f.read_bytes(),(ROOT/'examples/hero_hf00'/f.name).read_bytes())
    def test_program_text_and_generation_cost_are_never_invented(self):
        r=self.check_expected('HF-00')
        for a in section(r,2)['output_associations']:
            self.assertEqual(a['output_ref']['state'],'unavailable')
            self.assertEqual(a['output_content_hash']['state'],'not_applicable')
        self.assertEqual(r.manifest['candidate_programs_executed'],0)
    def test_replay_canonical_reports_and_manifest_time(self):
        p,_=self.fixture();a=analyze_bundle(p,recorded_at=STAMP);b=analyze_bundle(p,recorded_at=STAMP)
        self.assertEqual(a.report_json,b.report_json);self.assertEqual(a.report_markdown,b.report_markdown)
        self.assertEqual(a.manifest_json,b.manifest_json)
        c=analyze_bundle(p,recorded_at='2026-09-18T00:00:00+00:00')
        self.assertEqual(a.report_json,c.report_json)
        one,two=plain(a.manifest),plain(c.manifest);one.pop('recorded_at_utc');two.pop('recorded_at_utc');self.assertEqual(one,two)
    def test_explicit_run_identity_changes_metadata_not_metrics(self):
        p,_=self.fixture();a=analyze_bundle(p,run_id='analysis-1');b=analyze_bundle(p,run_id='analysis-2')
        self.assertEqual(section(a,4),section(b,4));self.assertNotEqual(a.report['run_id'],b.report['run_id'])
    def test_invalid_run_identity_and_naive_time_rejected(self):
        p,_=self.fixture()
        with self.assertRaises(InputError):analyze_bundle(p,run_id='../../private')
        with self.assertRaises(InputError):analyze_bundle(p,recorded_at='2026-09-17')
    def test_input_changes_get_new_fingerprint_without_overwriting_old_report(self):
        p,_=self.fixture();a=analyze_bundle(p);write_analysis(a,self.root/'first',bundle_path=p)
        original=(self.root/'first/report.json').read_bytes()
        q,_=self.fixture('HF-06');b=analyze_bundle(q);write_analysis(b,self.root/'second',bundle_path=q)
        self.assertNotEqual(a.report['input_fingerprint'],b.report['input_fingerprint'])
        self.assertEqual((self.root/'first/report.json').read_bytes(),original)
    def test_validate_has_no_metric_calculation(self):
        p,_=self.fixture()
        with patch('structdet_bench.pipeline.cell_metrics',side_effect=AssertionError('unexpected calculation')):
            result,code=validate_bundle(p)
        self.assertEqual(code,0);self.assertNotIn('structural_entropy',json.dumps(result))
    def test_report_hashes_identify_actual_written_bytes(self):
        p,_=self.fixture();r=analyze_bundle(p);write_analysis(r,self.root/'out',bundle_path=p)
        m=json.loads((self.root/'out/run_manifest.json').read_text())
        for name,sha in m['report_files'].items():self.assertEqual(hashlib.sha256((self.root/'out'/name).read_bytes()).hexdigest(),sha)
        self.assertNotIn('run_manifest.json',m['report_files'])


class AdversePipelineTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
    def build(self,labels):
        self.path,self.obs,self.sup,self.m=population_bundle(self.root/'input',labels)
    def get(self):
        p=rewrite_evidence_bundle(self.root/'input',self.obs,self.sup,self.m)
        return analyze_bundle(p)
    def test_empty_selected_inventory_has_zero_support_and_undefined_entropy(self):
        self.build([]);r=self.get();self.assertEqual(r.exit_code,0)
        self.assertEqual(numeric(r)['observed_support_size']['value'],0)
        self.assertEqual(numeric(r)['structural_entropy_nats']['result_status'],'undefined')
    def test_nonempty_unclassified_inventory_is_not_empty_study(self):
        self.build([None]*4);r=self.get()
        self.assertEqual(section(r,2)['inventory'][0]['selected_realization_count']['value'],4)
        self.assertEqual(numeric(r)['observed_support_size']['value'],0)
    def test_missing_shared_frame_withholds_distribution_keeps_inventory(self):
        self.build(['SORT-ADJ']*2);del self.m['frames'][0]['task_context'];r=self.get()
        self.assertEqual(r.exit_code,2);self.assertEqual(numeric(r)['observed_support_size']['result_status'],'unavailable')
        self.assertEqual(section(r,2)['inventory'][0]['realization_count']['value'],2)
    def test_malformed_manifest_is_error_not_empty_success(self):
        p=self.root/'bad.json';p.write_bytes(b'broken')
        r=analyze_bundle(p);self.assertEqual(r.exit_code,2);self.assertEqual(section(r,4)['metrics'],[])
    def test_malformed_analysis_object_retains_safe_error_report(self):
        self.build(['SORT-ADJ']);self.m['analysis_config']=[]
        r=self.get();self.assertEqual(r.exit_code,2)
    def test_unknown_prefix_mode_not_guessed_into_success(self):
        self.build(['SORT-ADJ']);self.m['analysis_config']['extensions']={'prefix_mode':'mystery'}
        r=self.get();self.assertEqual(r.exit_code,2);self.assertEqual(section(r,5)['prefixes'],[])
    def test_invalid_threshold_is_contract_failure_not_zero(self):
        self.build(['SORT-ADJ']);self.m['analysis_config']['empirical_threshold']=False
        r=self.get();self.assertEqual(r.exit_code,2)
        self.assertEqual(numeric(r)['observed_support_size_thresholded']['result_status'],'unavailable')
    def test_omitted_threshold_keeps_not_requested(self):
        self.build(['SORT-ADJ']);r=self.get();self.assertEqual(numeric(r)['observed_support_size_thresholded']['result_status'],'not_requested')
    def test_mock_imported_adjudication_uses_same_pipeline(self):
        p,o,s,m=evidence_bundle(self.root/'input',policy='adjudicated_import',samples=2)
        sel=m['analysis_config']['selection'][0];sel['selected_sample_ids']=tagged(['s1','s2']);sel['sample_order']=tagged(['s1','s2'])
        for i,x in enumerate([x for x in o if x['record_type']=='realization'],1):x['sample_order']=tagged(i)
        r=analyze_bundle(rewrite_evidence_bundle(self.root/'input',o,s,m))
        self.assertEqual(r.exit_code,0);self.assertEqual(numeric(r)['observed_support_size']['value'],1)
        self.assertEqual(section(r,1)['scope']['permitted_claim_scope'],'fixture_only')
        self.assertTrue(all(a['fixture_context'] for a in section(r,3)['admissions']))
    def test_independence_only_correction_does_not_erase_supported_counts(self):
        self.build(['SORT-ADJ','SORT-ADJ','SORT-INS']);a=self.get()
        self.sup.append(support_record('correction','c-independence',effect='independence',action='withdraw',stage='applied',
            target_refs=[record_ref('frame','frame1')],prior_result_ids=[a.report['run_id']],
            reason=tagged('Mock independent-claim withdrawal'),reviewer_refs=[record_ref('role','reviewer')],evidence_refs=[record_ref('evidence','e-a1')]))
        b=self.get();self.assertEqual(section(a,4),section(b,4))
        self.assertTrue(any(x['restrictions'] for x in section(b,3)['admissions']))
        self.assertTrue(section(b,8)['correction_impacts'][0]['claim_only'])
    def test_four_sample_evidence_correction_exact_sequence(self):
        self.build(['SORT-ADJ','SORT-ADJ','SORT-INS','SORT-INS']);old=self.get()
        proof=next(r for r in self.sup if r['record_id']=='e-a4');proof['payload']['state']='withdrawn';pending=self.get()
        previous=next(r for r in self.obs if r['record_id']=='a4');new=copy.deepcopy(previous)
        new.update(record_id='a4-r2',assignment_id='a4-r2',assignment_version='0.2',structural_class_id='SORT-ADJ',
                   supersedes_assignment_id=tagged('a4'),evidence_refs=[record_ref('evidence','e-a4-r2')])
        ep=copy.deepcopy(proof);ep['record_id']='e-a4-r2';ep['payload'].update(state='active',target_ref=record_ref('assignment','a4-r2'),assertion=tagged('SORT-ADJ'))
        self.obs.append(new);self.sup.append(ep)
        next(p for p in self.m['analysis_config']['assignment_pins'] if p['sample_id']=='s4').update(assignment_id='a4-r2',assignment_version='0.2')
        corrected=self.get()
        self.assertEqual([numeric(r)['structural_concentration_index']['exact_ratio'] for r in [old,pending,corrected]],[[1,2],[5,9],[5,8]])
        for r in [old,pending,corrected]:self.assertEqual(section(r,3)['accounting'][0]['valid_fraction_selected']['numerator'],4)
    def test_duplicate_record_is_error_not_a_second_observation(self):
        self.build(['SORT-ADJ']);self.obs.append(copy.deepcopy(self.obs[0]));r=self.get()
        self.assertEqual(r.exit_code,2);self.assertEqual(numeric(r)['observed_support_size']['result_status'],'unavailable')
    def test_unknown_model_identity_does_not_destroy_arithmetic(self):
        self.build(['SORT-ADJ']);self.m['cells'][0]['model_identifier']=tagged(state='unknown')
        r=self.get();self.assertEqual(r.exit_code,0);self.assertEqual(numeric(r)['observed_support_size']['value'],1)
    def test_hash_mismatch_is_not_repaired_by_pipeline(self):
        self.build(['SORT-ADJ']);self.m['record_files'][0]['expected_sha256']=tagged('0'*64)
        r=self.get();self.assertEqual(r.exit_code,2)
        self.assertEqual(self.m['record_files'][0]['expected_sha256']['value'],'0'*64)


class CommandIntegrationTests(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.bundle,_=materialize_hero(self.root/'input')
    def run_cli(self,*args):
        env={k:os.environ[k] for k in ['PATH','TMPDIR'] if k in os.environ}
        env['PYTHONDONTWRITEBYTECODE']='1'
        return subprocess.run([sys.executable,'-B','-S','-m','structdet_bench',*args],cwd=ROOT,env=env,
                              capture_output=True,text=True,timeout=30,check=False)
    def test_validate_command_success_and_no_writes(self):
        before=set(self.root.rglob('*'));r=self.run_cli('validate','--bundle',str(self.bundle))
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(set(self.root.rglob('*')),before)
        self.assertFalse(json.loads(r.stdout)['independent_validation_performed'])
    def test_analyze_command_publishes_three_files(self):
        r=self.run_cli('analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out'))
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(set(p.name for p in (self.root/'out').iterdir()),{'report.json','report.md','run_manifest.json'})
    def test_analyze_refuses_existing_output(self):
        (self.root/'out').mkdir();(self.root/'out/keep').write_text('keep')
        r=self.run_cli('analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out'))
        self.assertEqual(r.returncode,2);self.assertEqual((self.root/'out/keep').read_text(),'keep')
    def test_invalid_input_has_exit_two_and_safe_diagnostics(self):
        self.bundle.write_bytes(b'{invalid');r=self.run_cli('validate','--bundle',str(self.bundle))
        self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stdout)['exit_code'],2)
    def test_missing_arguments_do_not_echo_sensitive_paths(self):
        r=self.run_cli('analyze','--secret=PRIVATE_DATA')
        self.assertEqual(r.returncode,2);self.assertNotIn('PRIVATE_DATA',r.stderr)
    def test_unimplemented_commands_remain_errors(self):
        for name in ['generate','compare','train','execute','judge','recover']:
            with self.subTest(name=name):self.assertEqual(self.run_cli(name).returncode,2)
    def test_contract_error_report_can_be_written_without_success_claim(self):
        self.bundle.write_bytes(b'{invalid');r=self.run_cli('analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out'))
        self.assertEqual(r.returncode,2);self.assertFalse(json.loads((self.root/'out/report.json').read_text())['sections'][0]['content']['scope']['independent_validation_performed'])
    def test_internal_failure_returns_three_without_traceback(self):
        from structdet_bench.cli import main
        from contextlib import redirect_stderr
        import io
        err=io.StringIO()
        with patch('structdet_bench.pipeline.analyze_bundle',side_effect=RuntimeError('PRIVATE')),redirect_stderr(err):
            self.assertEqual(main(['analyze','--bundle',str(self.bundle),'--output-dir',str(self.root/'out')]),3)
        self.assertNotIn('PRIVATE',err.getvalue());self.assertNotIn('Traceback',err.getvalue())


# Step 6: output transactions operate on fully serialized, fixed-name bytes.
class OutputTransactionTests(unittest.TestCase):
    def setUp(self):
        from structdet_bench.local_io import publish_report_set
        self.publish=publish_report_set
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.input=self.root/'input';self.input.mkdir()
        self.bundle=self.input/'bundle.json';self.bundle.write_text('{}')
        self.files={'report.json':b'{}\n','report.md':b'# report\n','run_manifest.json':b'{}\n'}
    def test_publishes_exact_complete_set(self):
        out=self.root/'out';self.publish(out,self.files,bundle_path=self.bundle)
        self.assertEqual({p.name:p.read_bytes() for p in out.iterdir()},self.files)
    def test_existing_file_and_empty_directory_are_not_replaced(self):
        for name,kind in [('file','file'),('directory','directory')]:
            out=self.root/name
            out.write_text('old') if kind=='file' else out.mkdir()
            with self.assertRaises(InputError):self.publish(out,self.files,bundle_path=self.bundle)
            self.assertTrue(out.exists())
            if kind=='file':self.assertEqual(out.read_text(),'old')
    def test_output_inside_input_is_rejected(self):
        for out in [self.input,self.input/'new']:
            with self.assertRaises(InputError):self.publish(out,self.files,bundle_path=self.bundle)
        self.assertEqual(list(self.input.iterdir()),[self.bundle])
    def test_output_symlink_and_symlink_parent_are_rejected(self):
        linked=self.root/'link';linked.symlink_to(self.input,target_is_directory=True)
        for out in [linked,linked/'out']:
            with self.assertRaises(InputError):self.publish(out,self.files,bundle_path=self.bundle)
    def test_remote_expanding_and_traversing_output_paths_are_rejected(self):
        for out in ['https://example.test/private','~/report','$HOME/report','../out','a\\b','a\nsecret']:
            with self.assertRaises(InputError):self.publish(out,self.files,bundle_path=self.bundle)
    def test_only_fixed_three_filenames_are_allowed(self):
        for files in [{'../outside':b''},{**self.files,'extra':b''},{**self.files,'report.md':'notbytes'}]:
            with self.assertRaises(InputError):self.publish(self.root/'out',files,bundle_path=self.bundle)
    def test_missing_parent_does_not_create_an_implicit_tree(self):
        with self.assertRaises(InputError):self.publish(self.root/'absent/out',self.files,bundle_path=self.bundle)
        self.assertFalse((self.root/'absent').exists())
    def test_interrupted_write_cleans_staging(self):
        from structdet_bench.local_io import PublicationError
        with patch('os.write',side_effect=OSError('private failure')):
            with self.assertRaises(PublicationError):self.publish(self.root/'out',self.files,bundle_path=self.bundle)
        self.assertEqual({p.name for p in self.root.iterdir()},{'input'})
    def test_short_writes_are_retried_without_truncation(self):
        original=os.write
        with patch('os.write',side_effect=lambda fd,data:original(fd,data[:1])):
            self.publish(self.root/'out',self.files,bundle_path=self.bundle)
        self.assertEqual({p.name:p.read_bytes() for p in (self.root/'out').iterdir()},self.files)
    def test_zero_length_write_is_failure_and_cleanup(self):
        from structdet_bench.local_io import PublicationError
        with patch('os.write',return_value=0):
            with self.assertRaises(PublicationError):self.publish(self.root/'out',self.files,bundle_path=self.bundle)
        self.assertFalse((self.root/'out').exists())
        self.assertFalse(list(self.root.glob('.structdet-*')))
    def test_complete_staging_precedes_atomic_publish(self):
        from structdet_bench import local_io
        original=local_io._rename_noreplace
        def check(fd,old,new):
            self.assertFalse((self.root/'out').exists())
            self.assertEqual({p.name:p.read_bytes() for p in (self.root/old).iterdir()},self.files)
            return original(fd,old,new)
        with patch.object(local_io,'_rename_noreplace',side_effect=check):self.publish(self.root/'out',self.files,bundle_path=self.bundle)
    def test_racing_target_is_preserved_and_staging_cleaned(self):
        from structdet_bench import local_io
        original=local_io._rename_noreplace
        def race(fd,old,new):
            (self.root/new).mkdir();(self.root/new/'keep').write_bytes(b'concurrent')
            return original(fd,old,new)
        with patch.object(local_io,'_rename_noreplace',side_effect=race):
            with self.assertRaises(InputError):self.publish(self.root/'out',self.files,bundle_path=self.bundle)
        self.assertEqual((self.root/'out/keep').read_bytes(),b'concurrent')
        self.assertFalse(list(self.root.glob('.structdet-*')))
    def test_unsupported_atomic_operation_has_no_overwrite_fallback(self):
        with patch('structdet_bench.local_io._rename_noreplace',side_effect=InputError('atomic_publication_unavailable')):
            with self.assertRaises(InputError):self.publish(self.root/'out',self.files,bundle_path=self.bundle)
        self.assertFalse((self.root/'out').exists());self.assertFalse(list(self.root.glob('.structdet-*')))
    def test_private_permissions_do_not_depend_on_umask(self):
        old=os.umask(0)
        try:self.publish(self.root/'out',self.files,bundle_path=self.bundle)
        finally:os.umask(old)
        import stat
        self.assertEqual(stat.S_IMODE((self.root/'out').stat().st_mode),0o700)
        self.assertTrue(all(stat.S_IMODE(p.stat().st_mode)==0o600 for p in (self.root/'out').iterdir()))


class PipelineBoundaryTests(unittest.TestCase):
    def test_full_pipeline_never_runs_candidate_or_fetches_remote(self):
        from tests.helpers import materialize_hero
        from structdet_bench.pipeline import analyze_bundle,write_analysis
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path,_=materialize_hero(root/'input')
            with ExitStack() as stack:
                for name in ('socket.socket','socket.create_connection','urllib.request.urlopen','subprocess.Popen','os.system'):
                    stack.enter_context(patch(name,side_effect=AssertionError('unexpected active operation')))
                result=analyze_bundle(path);write_analysis(result,root/'out',bundle_path=path)
            self.assertEqual(result.exit_code,0)
            self.assertEqual(result.manifest['candidate_programs_executed'],0)
    def test_external_locator_remains_inert_and_private_in_report(self):
        from structdet_bench.pipeline import analyze_bundle
        from tests.helpers import population_bundle,rewrite_evidence_bundle,tagged,artifact_record
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path,obs,sup,m=population_bundle(root,['SORT-ADJ'])
            a=artifact_record('remote');a['content_ref']=tagged({'kind':'external','locator':'https://example.test/?token=PRIVATE_TOKEN'})
            obs.append(a)
            result=analyze_bundle(rewrite_evidence_bundle(root,obs,sup,m))
            self.assertNotIn(b'PRIVATE_TOKEN',result.report_json)
            self.assertIn(b'external_not_fetched',result.report_json)
    def test_serialization_failure_never_creates_output(self):
        from tests.helpers import materialize_hero
        from structdet_bench.pipeline import analyze_bundle
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path,_=materialize_hero(root/'input')
            with patch('structdet_bench.pipeline.render_json',side_effect=ValueError('fixture serialization failure')):
                with self.assertRaises(ValueError):analyze_bundle(path)
            self.assertFalse((root/'out').exists())
    def test_validate_does_not_write_any_inputs(self):
        from tests.helpers import materialize_hero
        from structdet_bench.pipeline import validate_bundle
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path,_=materialize_hero(root/'input')
            before={p.name:p.read_bytes() for p in path.parent.iterdir()}
            result,code=validate_bundle(path)
            self.assertEqual(code,0);self.assertEqual(before,{p.name:p.read_bytes() for p in path.parent.iterdir()})


# Paths are an explicit serialization crosswalk, not a new scientific schema.
# An asterisk checks every existing row; absence states are exercised separately.
RF_PATHS = {
 'RF-01':['run_id','input_schema_version','study_id','sections.0.content.analysis_config_ref'],
 'RF-02':['sections.0.content.frames.*.task_id','sections.0.content.frames.*.task_context','sections.0.content.frames.*.consequence_horizon'],
 'RF-03':['sections.0.content.frames.*.analytic_resolution_id','sections.0.content.frames.*.structural_schema_version'],
 'RF-04':['sections.0.content.frames.*.reference_registry_id','sections.4.content.reference_coverage','sections.7.content.intake_and_tail'],
 'RF-05':['sections.0.content.protocols.*.model_identifier','sections.0.content.protocols.*.checkpoint_identifier'],
 'RF-06':['sections.0.content.protocols.*.generation_protocol_version','sections.0.content.protocols.*.condition_id','sections.0.content.protocols.*.decoding_settings','sections.0.content.protocols.*.seed'],
 'RF-07':['sections.0.content.protocols.*.collection_window','sections.0.content.protocols.*.budget_record_ref','sections.0.content.protocols.*.sampling_plan_ref'],
 'RF-08':['sections.1.content.attempts.*.attempt_id','sections.1.content.attempts.*.attempt_status','sections.1.content.attempts.*.retry_of','sections.1.content.attempts.*.raw_response_ref'],
 'RF-09':['sections.1.content.output_associations.*.sample_id','sections.1.content.output_associations.*.raw_response_ref','sections.1.content.output_associations.*.output_content_hash','sections.1.content.output_associations.*.span_status'],
 'RF-10':['sections.1.content.groups','sections.1.content.output_associations.*.group_type','sections.1.content.output_associations.*.shared_context_ref','sections.1.content.inventory.*.sample_order'],
 'RF-11':['sections.1.content.output_associations.*.completion_status','sections.1.content.output_associations.*.termination_reason','sections.1.content.output_associations.*.selection_status','sections.1.content.inventory.*.excluded_sample_ids'],
 'RF-12':['sections.2.content.admissions.*.assignment_id','sections.2.content.admissions.*.assignment_version','sections.2.content.admissions.*.structural_class_id','sections.2.content.admissions.*.classification_uncertainty_ref'],
 'RF-13':['sections.2.content.admissions.*.validity_status','sections.2.content.admissions.*.validity_rubric_ref','sections.7.content.integrity_record_references.domain_validation_ref'],
 'RF-14':['sections.2.content.admissions.*.evidence_refs','sections.7.content.support_records.*.scope_refs','sections.7.content.support_records.*.details'],
 'RF-15':['sections.3.content.metrics.*.metric_name','sections.3.content.metrics.*.unit','sections.3.content.metrics.*.result_status','sections.3.content.metrics.*.unavailable_reason','sections.3.content.metrics.*.evidence_status'],
 'RF-16':['sections.3.content.distributions.*.population_size','sections.3.content.distributions.*.class_counts','sections.3.content.distributions.*.accepted_sample_ids'],
 'RF-17':['sections.2.content.accounting.*.classification_coverage','sections.2.content.accounting.*.classified_valid_coverage','sections.2.content.accounting.*.valid_fraction_selected','sections.2.content.accounting.*.decisive_validity_coverage','sections.2.content.accounting.*.classified_valid_fraction'],
 'RF-18':['sections.3.content.metrics','sections.3.content.numerical_policy'],
 'RF-19':['sections.3.content.distributions.*.min_empirical_frequency','sections.3.content.distributions.*.exact_frequencies'],
 'RF-20':['sections.4.content.prefixes.*.k','sections.4.content.prefixes.*.counted_samples','sections.4.content.prefixes.*.selected_sample_ids','sections.4.content.prefixes.*.partial_group_ids'],
 'RF-21':['sections.6.content.diagnostics'],'RF-22':['sections.6.content.diagnostics'],
 'RF-23':['sections.5.content.comparisons'],'RF-24':['sections.5.content.comparisons'],
 'RF-25':['sections.5.content.comparisons'],'RF-26':['sections.5.content.comparisons'],
 'RF-27':['sections.5.content.comparisons'],'RF-28':['sections.5.content.comparisons'],
 'RF-29':['sections.7.content.five_conditions','sections.7.content.declared_claim_records','sections.7.content.integrity_record_references.integrity_assessment_ref'],
 'RF-30':['sections.7.content.support_checks.*.details','sections.7.content.integrity_record_references.annotation_summary_ref','sections.7.content.integrity_record_references.audit_sampling_plan_ref'],
 'RF-31':['sections.7.content.intake_and_tail'],'RF-32':['sections.7.content.integrity_record_references.blinding_record_ref','sections.7.content.integrity_record_references.judge_calibration_ref','sections.7.content.integrity_record_references.sensitivity_evidence_ref'],
 'RF-33':['sections.7.content.corrections','sections.7.content.correction_impacts','sections.7.content.dependencies'],
 'RF-34':['sections.0.content.input_refs','sections.0.content.scope.permitted_claim_scope','sections.7.content.release_restrictions'],
 'RF-35':['sections.7.content.deferred.*.prerequisites'],'RF-36':['sections','sections.7.content.redaction'],
}


def assert_report_path(test, value, path):
    if not path:return
    part,*rest=path.split('.')
    if part=='*':
        test.assertIsInstance(value,list)
        for item in value:assert_report_path(test,item,'.'.join(rest))
    else:
        if isinstance(value,list):
            test.assertLess(int(part),len(value));child=value[int(part)]
        else:
            test.assertIn(part,value);child=value[part]
        assert_report_path(test,child,'.'.join(rest))


class Step7ReportIntegration(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.p,_=materialize_hero(self.root/'input')
    def test_all_36_report_groups_have_explicit_paths(self):
        from tests.helpers import load_matrix
        r=analyze_bundle(self.p);obj=plain(r.report);m=load_matrix()
        self.assertEqual(set(RF_PATHS),{x['id'] for x in m['report_groups']})
        self.assertEqual(sum(x['m_applicable'] for x in m['report_groups']),28)
        for group,paths in RF_PATHS.items():
            for path in paths:
                with self.subTest(group=group,path=path):assert_report_path(self,obj,path)
        self.assertEqual(m['step7_acceptance']['report_paths'],RF_PATHS)
    def test_every_m_metric_retains_denominator_status_and_source_scope(self):
        r=analyze_bundle(self.p)
        for row in section(r,4)['metrics']:
            self.assertEqual(row['population_size'],20);self.assertIn(row['analysis_population'],('classified_all','classified_valid'))
            self.assertEqual(row['permitted_claim_scope'],'fixture_only');self.assertEqual(row['uncertainty_status'],'not_estimated')
        self.assertEqual(len(section(r,2)['attempts']),4)
    def test_typed_lineage_exposure_and_annotation_survive_redaction(self):
        obs=[json.loads(x) for x in (self.p.parent/'records.jsonl').read_text().splitlines()]
        sup=[json.loads(x) for x in (self.p.parent/'evidence.jsonl').read_text().splitlines()];m=json.loads(self.p.read_text())
        for f in m['record_files']:f['expected_sha256']=tagged(state='unknown')
        sup += [support_record('lineage','l1',subject_ref=record_ref('role','reviewer'),parent_ref=tagged(state='unknown'),relation='translated_from',knowledge_state='unknown'),
                support_record('exposure','x1',subject_ref=record_ref('role','reviewer'),role_ref=record_ref('role','reviewer'),stage='post_inspection',exposed=tagged(True),material_refs=[])]
        result=analyze_bundle(rewrite_evidence_bundle(self.p.parent,obs,sup,m))
        rows={x['record_id']:x for x in section(result,8)['support_records']}
        self.assertEqual(rows['l1']['details']['relation'],'translated_from')
        self.assertEqual(rows['l1']['details']['parent_ref']['state'],'unknown')
        self.assertTrue(rows['x1']['details']['exposed']['value']);self.assertEqual(rows['x1']['details']['stage'],'post_inspection')
        self.assertNotIn('test-person-1',result.report_json.decode())
    def test_empty_then_received_and_acted_intake_never_adds_samples(self):
        for stage in ('empty','received','acted','rejected'):
            with self.subTest(stage=stage):
                root=self.root/stage;p,o,s,m=population_bundle(root,['SORT-ADJ'])
                s.append(support_record('intake','incident',component='external_incident',stage=stage,proposed_change=tagged('PRIVATE_ORIGINAL_ANOMALY')))
                r=analyze_bundle(rewrite_evidence_bundle(root,o,s,m));self.assertEqual(section(r,8)['intake_and_tail'][0]['stage'],stage)
                self.assertEqual(section(r,2)['inventory'][0]['realization_count']['value'],1)
                self.assertNotIn(b'PRIVATE_ORIGINAL_ANOMALY',r.report_json)
    def test_domain_coverage_details_are_visible_and_fixture_stays_fixture(self):
        from tests.helpers import complete_functional_fixture
        p,o,s,m=complete_functional_fixture(self.root/'functional')
        r=analyze_bundle(p)
        checks=[x for x in section(r,8)['support_checks'] if 'complete_suite_coverage' in x['details']]
        self.assertTrue(checks);self.assertTrue(checks[0]['details']['complete_suite_coverage'])
        self.assertEqual(checks[0]['details']['tested_count'],8995);self.assertFalse(checks[0]['substantive_validation_performed'])
        self.assertEqual(section(r,1)['scope']['data_role'],'fixture')
    def test_all_deferred_prerequisites_visible_without_estimator(self):
        r=analyze_bundle(self.p);deferred={x['metric_name']:x for x in section(r,8)['deferred']}
        for name in ('exact_realization_entropy','convergence_provenance','structural_transmission','structural_half_life_null','external_recovery_rate'):
            self.assertIsNone(deferred[name]['value']);self.assertTrue(deferred[name]['prerequisites'])
        self.assertIn('empty denominator is undefined',deferred['external_recovery_rate']['prerequisites'])
        self.assertIn('n > 1',deferred['structural_half_life_null']['prerequisites'])
    def test_correction_dependencies_identify_both_views_without_resampling(self):
        p,_=materialize_hero(self.root/'corrected','HF-06');r=analyze_bundle(p)
        ds=section(r,8)['dependencies'];self.assertEqual(len(ds),40)
        self.assertTrue(all(d['dependent_m_metrics'] and d['dependent_m_prefixes']==[5,10,20] for d in ds))
        self.assertTrue(all(d['v_dependents']=='not_implemented' for d in ds))
        self.assertEqual(section(r,2)['inventory'][0]['selected_realization_count']['value'],20)
    def test_shared_schema_challenge_affects_all_its_cells_not_other_frames(self):
        p,o,s,m=population_bundle(self.root/'cells',['SORT-ADJ','SORT-INS','SORT-MERGE'])
        cell=m['cells'][0]
        for num in (2,3):
            clone=copy.deepcopy(cell);clone.update(record_id=f'cell{num}',analysis_cell_id=f'cell{num}');m['cells'].append(clone)
        m['cells'][2]['frame_id']='frame2';fr=copy.deepcopy(m['frames'][0]);fr.update(record_id='frame2',frame_id='frame2');m['frames'].append(fr)
        original=copy.deepcopy(m['analysis_config']['selection'][0]);m['analysis_config']['selection']=[]
        for i in (1,2,3):
            sid=f's{i}';next(x for x in o if x['record_id']==sid)['analysis_cell_id']=f'cell{i}'
            sel=copy.deepcopy(original);sel.update(analysis_cell_id=f'cell{i}',selected_sample_ids=tagged([sid]),sample_order=tagged([sid]));m['analysis_config']['selection'].append(sel)
        next(x for x in o if x['record_id']=='a3')['frame_id']='frame2'
        for x in s:
            if x['record_id'] in ('e-a3','e-v3'):x['payload']['scope_refs']=[record_ref('frame','frame2')]
        s.append(support_record('correction','c-schema',effect='schema',action='challenge',stage='applied',target_refs=[record_ref('frame','frame1')],reason=tagged('Mock shared defect'),evidence_refs=[record_ref('evidence','e-a1')],reviewer_refs=[record_ref('role','reviewer')]))
        r=analyze_bundle(rewrite_evidence_bundle(p.parent,o,s,m))
        states={x['analysis_cell_id']:x['result_status'] for x in section(r,4)['metrics'] if x['metric_name']=='observed_support_size' and x['analysis_population']=='classified_all'}
        self.assertEqual(states,{'cell1':'unavailable','cell2':'unavailable','cell3':'available'})
    def test_relocated_input_replays_all_canonical_content(self):
        import shutil
        a=analyze_bundle(self.p,recorded_at=STAMP);other=self.root/'moved'
        shutil.copytree(self.p.parent,other);b=analyze_bundle(other/'bundle.json',recorded_at=STAMP)
        self.assertEqual(a.report_json,b.report_json);self.assertEqual(a.report_markdown,b.report_markdown)
        self.assertEqual(a.manifest_json,b.manifest_json)
    def test_metadata_time_never_changes_content_or_creates_observation(self):
        a=analyze_bundle(self.p,recorded_at=STAMP);b=analyze_bundle(self.p,recorded_at='2026-09-18T02:00:00+00:00')
        self.assertEqual(a.report_json,b.report_json);self.assertEqual(a.report_markdown,b.report_markdown)
        ma,mb=plain(a.manifest),plain(b.manifest);ma.pop('recorded_at_utc');mb.pop('recorded_at_utc');self.assertEqual(ma,mb)
    def test_registered_sources_and_original_fixture_hashes_still_match(self):
        from tests.helpers import load_matrix,baseline_checks
        m=load_matrix();self.assertTrue(all(x['status']=='passed' for x in baseline_checks(m)))
        for d in m['ec001_supplement']['documents']:
            self.assertEqual(hashlib.sha256((ROOT/d['path']).read_bytes()).hexdigest(),d['sha256'])
        self.assertEqual(len(m['ec001_supplement']['requirements']),8)


class Step7GateTests(unittest.TestCase):
    """Gate unit tests use synthetic pass records, never empirical assertions."""
    def test_missing_ec_binding_cannot_pass_full_gate(self):
        from tests.test_scaffold import HarnessTests, assess_gate
        matrix,ids,records=HarnessTests.synthetic_gate_inputs()
        del matrix['step7_acceptance']['evidence_checks']['EC-C02']
        result=assess_gate(matrix,ids,records,scope='phase1')
        self.assertFalse(result['requested_gate_passed'])
        self.assertIn('EC-C02',result['unresolved_ec_m_ids'])
    def test_nonpassing_ec_binding_cannot_be_overridden(self):
        from tests.test_scaffold import HarnessTests, assess_gate
        matrix,ids,records=HarnessTests.synthetic_gate_inputs()
        matrix['step7_acceptance']['evidence_checks']['EC-C03']['test_bindings']=['tests.not_executed.test_missing']
        self.assertFalse(assess_gate(matrix,ids,records,scope='phase1')['requested_gate_passed'])
    def test_complete_mock_gate_is_M_only_and_not_final_approval(self):
        from tests.test_scaffold import HarnessTests, assess_gate
        matrix,ids,records=HarnessTests.synthetic_gate_inputs()
        result=assess_gate(matrix,ids,records,scope='phase1')
        self.assertTrue(result['phase1_m_complete'])
        self.assertEqual(len(result['ec_m_results']),8)
        self.assertFalse(result['empirical_validation_performed'])
        self.assertEqual(result['phase1_final_owner_approval'],'not_established_by_software_tests')
    def test_test_records_have_expected_actual_scope_and_no_E_claim(self):
        from tests.test_scaffold import HarnessTests, _runner
        matrix,ids,records=HarnessTests.synthetic_gate_inputs()
        rows=_runner.annotate_results(matrix,records)
        self.assertEqual(rows[0]['expected_outcome'],'passed')
        self.assertEqual(rows[0]['actual_outcome'],'passed')
        self.assertTrue(rows[0]['requirement_bindings'])
        self.assertTrue(all(x.endswith('/M') for x in rows[0]['requirement_bindings']))
        self.assertFalse(rows[0]['substantive_validation_performed'])
    def test_ec_scope_cannot_be_promoted_to_empirical_evidence(self):
        from tests.helpers import load_matrix
        from tests.test_scaffold import validate_matrix
        m=load_matrix();m['step7_acceptance']['evidence_checks']['EC-C01']['evidence_status']='validated'
        self.assertTrue(validate_matrix(m))
