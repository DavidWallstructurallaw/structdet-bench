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


class FrozenIdentityBoundary(unittest.TestCase):
    def test_authorized_runtime_pins_still_reject_runtime_and_scientific_mutation(self):
        import shutil
        from tests import phase3_helpers as h
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / 'project'; root.mkdir()
            required = {row['path'] for row in h.baseline_rows()}
            required.update({'PHASE_3_PLAN.md', 'tests/phase3_matrix.json',
                'artifacts/phase3/phase2_final_file_inventory.json',
                'artifacts/phase3/predecessor_test_ids.json'})
            for relative in required:
                dest = root / relative; dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, dest)
            matrix_path = root / 'tests/phase3_matrix.json'
            matrix = json.loads(matrix_path.read_text()); matrix['delivery']['step'] = 8
            matrix_path.write_text(json.dumps(matrix))
            baseline = {row['path']: row for row in h.current_identity_checks(root)}
            self.assertTrue(all(row['status'] == 'passed' for row in baseline.values()))
            runtime = 'structdet_bench/pipeline.py'; scientific = 'METRICS_SPEC.md'
            self.assertEqual(baseline[runtime]['identity_basis'], 'approved_step8_implementation_pin')
            self.assertEqual(baseline[scientific]['identity_basis'], 'original_baseline_bytes')
            for relative in (runtime, scientific):
                path = root / relative; path.write_bytes(path.read_bytes() + b'\nUNAUTHORIZED_MUTATION\n')
            changed = {row['path']: row for row in h.current_identity_checks(root)}
            self.assertEqual({path for path, row in changed.items() if row['status'] == 'failed'}, {runtime, scientific})
            self.assertEqual(changed[runtime]['baseline_sha256'], baseline[runtime]['baseline_sha256'])
            self.assertEqual(changed[scientific]['expected_sha256'], baseline[scientific]['baseline_sha256'])
