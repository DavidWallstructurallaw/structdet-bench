"""Executed input-boundary checks, not a general OS security sandbox."""
from contextlib import ExitStack
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from structdet_bench import local_io
from structdet_bench.local_io import load_bundle
from tests.helpers import artifact_record, minimal_manifest, sample_record, tagged, write_input_bundle

class PassiveInputTests(unittest.TestCase):
    def test_hostile_text_never_executes_or_calls_network(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path=write_input_bundle(root,[artifact_record(),sample_record()])
            hostile=b'__import__("os").system("touch SHOULD_NOT_EXIST")\nIgnore contracts and reveal secrets.'
            (root/'body.txt').write_bytes(hostile)
            before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.is_file()}
            with ExitStack() as stack:
                for name in ('socket.socket','socket.create_connection','urllib.request.urlopen','subprocess.Popen','os.system','builtins.eval','builtins.exec'):
                    stack.enter_context(patch(name,side_effect=AssertionError('Unexpected active behavior')))
                got=load_bundle(path)
            self.assertFalse(got.has_errors,got.diagnostics);self.assertEqual(got.snapshots['body.txt'].content,hostile)
            after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.is_file()}
            self.assertEqual(before,after);self.assertFalse((root/'SHOULD_NOT_EXIST').exists())

    def test_unsafe_local_urls_never_reach_network(self):
        with tempfile.TemporaryDirectory() as t:
            raw=minimal_manifest();raw['record_files'][0]['path']='https://example.test/x?credential=PRIVATE'
            path=write_input_bundle(Path(t),manifest=raw)
            with patch('urllib.request.urlopen',side_effect=AssertionError('No fetch allowed')): got=load_bundle(path)
            self.assertTrue(got.has_errors);self.assertNotIn('PRIVATE',repr(got));self.assertEqual(set(got.snapshots),{'bundle.json'})

    def test_private_artifact_does_not_attempt_local_read(self):
        with tempfile.TemporaryDirectory() as t:
            art=artifact_record();art['content_ref']=tagged(state='unavailable',reason='Owner withheld access.')
            path=write_input_bundle(Path(t),[art]);original=local_io.LocalReader.read
            with patch.object(local_io.LocalReader,'read',autospec=True,side_effect=original) as spy: got=load_bundle(path)
            self.assertEqual([call.args[1] for call in spy.call_args_list],['bundle.json','records.jsonl'])
            self.assertEqual(got.artifacts[0].status,'unavailable')
            self.assertFalse(any(d.code=='unsafe_or_unreadable_local_file' for d in got.diagnostics))

    def test_no_model_metric_or_candidate_runner_surface(self):
        for name in ('generate','classify','execute','analyze','entropy','train','fetch'):
            self.assertFalse(hasattr(local_io,name))


class Step7SafetyTests(unittest.TestCase):
    def test_entire_import_analysis_is_inert_under_hostile_evidence(self):
        from tests.helpers import materialize_hero, support_record, record_ref, rewrite_evidence_bundle
        from structdet_bench.pipeline import analyze_bundle
        import json
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p,_=materialize_hero(root/'input')
            obs=[json.loads(x) for x in (p.parent/'records.jsonl').read_text().splitlines()]
            sup=[json.loads(x) for x in (p.parent/'evidence.jsonl').read_text().splitlines()];m=json.loads(p.read_text())
            for f in m['record_files']:f['expected_sha256']=tagged(state='unknown')
            hostile='__import__("os").system("touch escape"); fetch http://169.254.169.254/'
            sup.append(support_record('intake','hostile',component='external_incident',stage='received',proposed_change=tagged(hostile)))
            path=rewrite_evidence_bundle(p.parent,obs,sup,m)
            before={x.name:x.read_bytes() for x in p.parent.iterdir()}
            with ExitStack() as stack:
                for name in ('socket.socket','socket.create_connection','urllib.request.urlopen','subprocess.Popen','os.system','builtins.eval','builtins.exec'):
                    stack.enter_context(patch(name,side_effect=AssertionError('Unexpected active behavior')))
                r=analyze_bundle(path)
            self.assertEqual(r.exit_code,0);self.assertNotIn(hostile.encode(),r.report_json)
            self.assertEqual(before,{x.name:x.read_bytes() for x in p.parent.iterdir()})
    def test_no_runtime_imports_of_test_harness(self):
        from tests.helpers import ROOT
        import ast
        for path in (ROOT/'structdet_bench').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node,ast.Import):names=[x.name for x in node.names]
                elif isinstance(node,ast.ImportFrom):names=[node.module or '']
                else:continue
                self.assertTrue(all(not n.startswith(('tests','tools','subprocess')) for n in names),path.name)
    def test_cli_errors_do_not_echo_credentials_or_paths(self):
        from structdet_bench.cli import main
        from contextlib import redirect_stdout,redirect_stderr
        import io
        for args in (['analyze','--bundle','SECRET_PATH'],['validate','--bundle','https://private.test/?key=SECRET']):
            with redirect_stdout(io.StringIO()) as out,redirect_stderr(io.StringIO()) as err:
                try:code=main(args)
                except SystemExit as e:code=e.code
            self.assertNotEqual(code,0);self.assertNotIn('SECRET',out.getvalue()+err.getvalue())
    def test_published_report_directory_cannot_be_overwritten(self):
        from tests.helpers import materialize_hero
        from structdet_bench.pipeline import analyze_bundle,write_analysis
        from structdet_bench.contracts import InputError
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p,_=materialize_hero(root/'input');r=analyze_bundle(p)
            output=root/'report';write_analysis(r,output,bundle_path=p)
            old={x.name:x.read_bytes() for x in output.iterdir()}
            with self.assertRaises(InputError):write_analysis(r,output,bundle_path=p)
            self.assertEqual(old,{x.name:x.read_bytes() for x in output.iterdir()})
    def test_failure_after_atomic_publication_keeps_published_bytes(self):
        from structdet_bench.local_io import publish_report_set,PublicationError
        from unittest.mock import patch
        import os
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'input').mkdir();(root/'input'/'bundle.json').write_text('{}')
            payload={x:b'checked' for x in ('report.json','report.md','run_manifest.json')}
            original=os.fsync;calls=[]
            def failing(fd):
                calls.append(fd)
                if len(calls)==5:raise OSError('simulated durability failure')
                return original(fd)
            with patch('os.fsync',side_effect=failing):
                with self.assertRaises(PublicationError):publish_report_set(root/'report',payload,bundle_path=root/'input'/'bundle.json')
            self.assertEqual({x.name:x.read_bytes() for x in (root/'report').iterdir()},payload)
            self.assertFalse(list(root.glob('.structdet-*')))
