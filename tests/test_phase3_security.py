"""Passive longitudinal inputs, complete replay and safe report publication."""
from __future__ import annotations

from contextlib import ExitStack, redirect_stderr, redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench.contracts import InputError
from structdet_bench.pipeline import analyze_bundle, validate_bundle, write_analysis
from structdet_bench.reporting import plain
from tests.helpers import tagged as K, rewrite_evidence_bundle
from tests.test_phase3_pipeline import (ROOT, HERO, NULL, STAMP, hero_result, null_result,
    content, episode, source_rows, copy_hero, run_cli, write_source)


class PassiveAndPublication(unittest.TestCase):
    def test_hostile_evidence_private_actor_and_paths_never_enter_three_files(self):
        secret = 'PRIVATE_LONGITUDINAL __import__("os").system("run") <script>secret</script>'
        with TemporaryDirectory(prefix='PRIVATE_ROOT_') as tmp:
            p = copy_hero(Path(tmp) / 'input'); observations, evidence, manifest = source_rows(p)
            for row in evidence:
                if row['record_type'] == 'evidence':
                    row['payload']['detail'] = K(secret)
                elif row['record_type'] == 'role':
                    row['payload']['entity_id'] = K(secret)
            write_source(p.parent, observations, evidence, manifest)
            before = {f.name: f.read_bytes() for f in p.parent.iterdir() if f.is_file()}
            with ExitStack() as stack:
                for target in ('socket.socket', 'socket.create_connection', 'urllib.request.urlopen', 'subprocess.Popen', 'os.system', 'builtins.eval'):
                    stack.enter_context(patch(target, side_effect=AssertionError('active operation forbidden')))
                r = analyze_bundle(p, recorded_at=STAMP)
                write_analysis(r, Path(tmp) / 'out', bundle_path=p)
            for body in (r.report_json, r.report_markdown, r.manifest_json):
                self.assertNotIn(b'PRIVATE_LONGITUDINAL', body)
                self.assertNotIn(b'PRIVATE_ROOT_', body)
            self.assertEqual(before, {f.name: f.read_bytes() for f in p.parent.iterdir() if f.is_file()})
            self.assertEqual(r.manifest['model_calls'], 0)
            self.assertEqual(r.manifest['candidate_programs_executed'], 0)

    def test_existing_output_is_immutable_and_only_three_files_are_written(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); output = root / 'out'; r = null_result()
            write_analysis(r, output, bundle_path=NULL)
            previous = {p.name: p.read_bytes() for p in output.iterdir()}
            self.assertEqual(set(previous), {'report.json', 'report.md', 'run_manifest.json'})
            with self.assertRaises(InputError):
                write_analysis(r, output, bundle_path=NULL)
            self.assertEqual(previous, {p.name: p.read_bytes() for p in output.iterdir()})

    def test_atomic_publication_race_keeps_concurrent_writer_and_cleans_staging(self):
        from structdet_bench import local_io
        with TemporaryDirectory() as tmp:
            root = Path(tmp); original = local_io._rename_noreplace
            def race(fd, old, new):
                (root / new).mkdir(); (root / new / 'keep').write_bytes(b'other writer')
                return original(fd, old, new)
            with patch.object(local_io, '_rename_noreplace', side_effect=race):
                with self.assertRaises(InputError):
                    write_analysis(null_result(), root / 'out', bundle_path=NULL)
            self.assertEqual((root / 'out/keep').read_bytes(), b'other writer')
            self.assertFalse(list(root.glob('.structdet-*')))

    def test_serialization_or_file_write_failure_publishes_no_partial_directory(self):
        from structdet_bench import local_io
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(local_io.os, 'write', side_effect=OSError('PRIVATE_WRITE_FAILURE')):
                with self.assertRaises((InputError, OSError)):
                    write_analysis(null_result(), root / 'out', bundle_path=NULL)
            self.assertFalse((root / 'out').exists())
            self.assertFalse(list(root.glob('.structdet-*')))

    def test_symlink_traversal_and_output_under_input_are_refused(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); p = copy_hero(root / 'input')
            (root / 'link').symlink_to(p.parent, target_is_directory=True)
            for destination in (root / 'link/out', p.parent / 'out', '../PRIVATE_ESCAPED'):
                with self.subTest(destination=str(destination)):
                    with self.assertRaises(InputError):
                        write_analysis(null_result(), destination, bundle_path=p)
            self.assertFalse((p.parent / 'out').exists())

    def test_active_commands_remain_unavailable_and_errors_redact_arguments(self):
        for command in ('train', 'generate', 'execute', 'judge', 'recover'):
            r = run_cli(command, '--token=PRIVATE_ARGUMENT')
            self.assertEqual(r.returncode, 2)
            self.assertNotIn(b'PRIVATE_ARGUMENT', r.stdout + r.stderr)

    def test_internal_exception_reports_three_without_traceback_or_publication(self):
        from structdet_bench.cli import main
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / 'out'
            with patch('structdet_bench.pipeline.analyze_bundle', side_effect=RuntimeError('PRIVATE_EXCEPTION')), redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
                code = main(['analyze', '--bundle', str(NULL), '--output-dir', str(output)])
            self.assertEqual(code, 3)
            self.assertNotIn('PRIVATE_EXCEPTION', out.getvalue() + err.getvalue())
            self.assertFalse(output.exists())


class ReplayBoundary(unittest.TestCase):
    def test_duplicate_keys_and_missing_draws_are_input_errors_without_rng_fallback(self):
        original = plain(hero_result().manifest)
        broken = copy.deepcopy(original)
        entry = next(e for e in broken['longitudinal_replay']['entries'] if e['replay'])
        entry['replay']['indices'].pop()
        bodies = [b'{"longitudinal_replay":{},"longitudinal_replay":{}}', json.dumps(broken).encode()]
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'replay.json'
            for body in bodies:
                with self.subTest(body_sha256=hashlib.sha256(body).hexdigest()):
                    path.write_bytes(body)
                    with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('fallback forbidden')):
                        _, code = validate_bundle(HERO, replay_manifest_path=path)
                        r = analyze_bundle(HERO, replay_manifest_path=path)
                    self.assertEqual(code, 2); self.assertEqual(r.exit_code, 2)
                    entries = plain(r.manifest['longitudinal_replay'])['entries']
                    self.assertTrue(all(entry['replay'] is None for entry in entries))

    def test_forged_unavailable_null_matrix_cannot_replace_recorded_2000_draws(self):
        broken = plain(hero_result().manifest)
        entry = next(row for row in broken['longitudinal_replay']['entries'] if row['replay'])
        entry.update(status='unavailable', reasons=['explicit_null_replay'], replay=None)
        def digest(value):
            return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()).hexdigest()
        carrier = broken['longitudinal_replay']
        carrier['sha256'] = digest({k: v for k, v in carrier.items() if k != 'sha256'})
        broken['longitudinal_replay_sha256'] = digest(carrier)
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'replay.json'; path.write_text(json.dumps(broken))
            with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('fallback forbidden')):
                _, code = validate_bundle(HERO, replay_manifest_path=path)
                r = analyze_bundle(HERO, replay_manifest_path=path)
            self.assertEqual(code, 2); self.assertEqual(r.exit_code, 2)

    def test_wrong_replay_profile_context_and_unit_order_are_rejected(self):
        original = plain(hero_result().manifest)
        variants = []
        bad = copy.deepcopy(original); bad['report_profile'] = 'structdet_comparison_v1'; variants.append(bad)
        bad = copy.deepcopy(original); bad['longitudinal_replay']['input_context_sha256'] = '0' * 64; variants.append(bad)
        bad = copy.deepcopy(original)
        next(e for e in bad['longitudinal_replay']['entries'] if e['replay'])['replay']['unit_ids'].reverse(); variants.append(bad)
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'replay.json'
            for bad in variants:
                path.write_text(json.dumps(bad))
                with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('fallback forbidden')):
                    _, code = validate_bundle(HERO, replay_manifest_path=path)
                self.assertEqual(code, 2)

    def test_remote_or_symlink_replay_never_fetches_or_leaks_locator(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); target = root / 'prior.json'; target.write_bytes(hero_result().manifest_json)
            link = root / 'PRIVATE_REPLAY_LINK'; link.symlink_to(target)
            for locator in (link, 'https://private.invalid/?token=PRIVATE_REPLAY_TOKEN'):
                with patch('urllib.request.urlopen', side_effect=AssertionError('network')):
                    r = run_cli('validate', '--bundle', HERO, '--replay-manifest', locator)
                self.assertNotEqual(r.returncode, 0)
                self.assertNotIn(b'PRIVATE_REPLAY', r.stdout + r.stderr)

    def test_old_report_survives_evidence_correction_and_same_old_manifest_replays(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); p = copy_hero(root / 'input'); old = hero_result()
            write_analysis(old, root / 'prior', bundle_path=p)
            original = {f.name: f.read_bytes() for f in (root / 'prior').iterdir()}
            observations, evidence, manifest = source_rows(p)
            next(e for e in evidence if e['record_id'] == 'external-validation')['payload']['state'] = 'withdrawn'
            write_source(p.parent, observations, evidence, manifest)
            current = analyze_bundle(p, recorded_at=STAMP)
            self.assertEqual(episode(current)['external_recovery_rate']['status'], 'unavailable')
            self.assertEqual(episode(current)['missing_classes'], episode(old)['missing_classes'])
            self.assertEqual(episode(current)['confirmed_recovered'], episode(old)['confirmed_recovered'])
            self.assertNotEqual(current.manifest['run_id'], old.manifest['run_id'])
            self.assertEqual(original, {f.name: f.read_bytes() for f in (root / 'prior').iterdir()})
            _, code = validate_bundle(p, replay_manifest_path=root / 'prior/run_manifest.json')
            self.assertEqual(code, 2)
            with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('fresh random fallback')):
                replayed = analyze_bundle(HERO, replay_manifest_path=root / 'prior/run_manifest.json', recorded_at=STAMP)
            self.assertEqual(replayed.exit_code, 0)
            self.assertEqual(content(replayed, 6), content(old, 6))




class FinalResourceAndReplayBoundary(unittest.TestCase):
    def test_replay_bytes_share_the_original_bundle_budget(self):
        from structdet_bench.local_io import load_bundle, ReadLimits
        original = hero_result(); total = load_bundle(HERO).total_read_bytes
        limits = ReadLimits(max_bundle_bytes=total + len(original.manifest_json) - 1)
        with TemporaryDirectory() as tmp:
            saved = Path(tmp) / 'replay.json'; saved.write_bytes(original.manifest_json)
            _, code = validate_bundle(HERO, limits=limits)
            self.assertEqual(code, 0)
            validation, code = validate_bundle(HERO, limits=limits, replay_manifest_path=saved)
        self.assertEqual(code, 2)
        self.assertIn('bundle_size_exceeded', json.dumps(validation))

    def test_hostile_json_depth_numbers_nonfinite_and_duplicate_keys_fail_before_evaluation(self):
        bodies = [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}',
            b'[' * 65 + b'0' + b']' * 65, b'{"x":1e' + b'9' * 1025 + b'}']
        with TemporaryDirectory() as tmp:
            saved = Path(tmp) / 'PRIVATE_HOSTILE.json'
            for body in bodies:
                with self.subTest(sha256=hashlib.sha256(body).hexdigest()):
                    saved.write_bytes(body)
                    with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('fallback')):
                        validation, code = validate_bundle(NULL, replay_manifest_path=saved)
                    self.assertEqual(code, 2)
                    self.assertNotIn('PRIVATE_HOSTILE', json.dumps(validation))

    def test_lower_physical_limits_fail_closed_without_successful_report(self):
        from structdet_bench.local_io import ReadLimits
        for limits in (ReadLimits(max_file_bytes=1), ReadLimits(max_bundle_bytes=1),
                       ReadLimits(max_records=1), ReadLimits(max_line_bytes=1)):
            with self.subTest(limits=limits):
                validation, code = validate_bundle(HERO, limits=limits)
                self.assertEqual(code, 2)
                self.assertEqual(validation['exit_code'], 2)

    def test_recomputed_outer_digests_do_not_authorize_changed_replay_semantics(self):
        def digest(value):
            return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()).hexdigest()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'replay.json'
            for mutation in ('method', 'boolean_index', 'short_matrix', 'request_swap', 'threshold_context'):
                with self.subTest(mutation=mutation):
                    body = plain(hero_result().manifest); carrier = body['longitudinal_replay']
                    entries = [x for x in carrier['entries'] if x['replay']]
                    self.assertTrue(entries)
                    replay = entries[0]['replay']
                    if mutation == 'method': replay['method'] = 'paired_prompt_block_bootstrap_v1'
                    elif mutation == 'boolean_index': replay['indices'][0][0] = True
                    elif mutation == 'short_matrix': replay['indices'].pop()
                    elif mutation == 'request_swap': entries[0]['request_ref']['object_id'] = 'different-request'
                    else: replay['context_sha256'] = '0' * 64
                    replay['sha256'] = digest({k:v for k,v in replay.items() if k != 'sha256'})
                    carrier['sha256'] = digest({k:v for k,v in carrier.items() if k != 'sha256'})
                    body['longitudinal_replay_sha256'] = digest(carrier)
                    path.write_text(json.dumps(body))
                    with patch('structdet_bench.longitudinal_uncertainty.make_replay', side_effect=AssertionError('fallback')):
                        _, code = validate_bundle(HERO, replay_manifest_path=path)
                    self.assertEqual(code, 2)
