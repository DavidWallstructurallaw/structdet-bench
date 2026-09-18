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
