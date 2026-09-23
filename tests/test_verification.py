"""Current verification controls, independent of historical phase identities.

Synthetic outcomes below test the recorder; they never constitute scientific
observations or a completed production execution.
SPDX-License-Identifier: Apache-2.0
"""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch
import zipfile

import structdet_bench
from structdet_bench import cli
from tools import check
from tests.helpers import ROOT, run_trusted_case


class PackageAndCommandTests(unittest.TestCase):
    def test_standard_library_import_and_metadata_agree(self):
        result = run_trusted_case('import')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), structdet_bench.__version__)
        metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        self.assertEqual(metadata['project']['version'], structdet_bench.__version__)
        self.assertEqual(metadata['project']['name'], 'structdet-bench')
        self.assertEqual(metadata['project']['dependencies'], [])

    def test_distribution_contains_only_runtime_package(self):
        settings = tomllib.loads((ROOT / 'pyproject.toml').read_text())['tool']['setuptools']
        self.assertEqual(settings['packages'], ['structdet_bench'])
        self.assertFalse(settings['include-package-data'])
        self.assertNotIn('package-data', settings)
        self.assertFalse(list((ROOT / 'structdet_bench').rglob('*.pdf')))

    def test_help_version_and_argument_errors(self):
        for case in ('help', 'version', 'no_args'):
            result = run_trusted_case(case)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, '')
        for case in ('unknown_option', 'validate_no_input', 'analyze_no_input', 'generate', 'train', 'execute', 'judge', 'compare', 'recover'):
            result = run_trusted_case(case)
            self.assertEqual(result.returncode, 2, case)
            self.assertIn('error:', result.stderr)

    def test_help_and_version_have_no_network_or_process_effect(self):
        with ExitStack() as stack:
            for name in ('socket.socket', 'socket.create_connection', 'urllib.request.urlopen', 'subprocess.Popen', 'os.system'):
                stack.enter_context(patch(name, side_effect=AssertionError(name)))
            stack.enter_context(redirect_stdout(io.StringIO()))
            stack.enter_context(redirect_stderr(io.StringIO()))
            for argv in (['--help'], ['--version']):
                with self.assertRaises(SystemExit) as caught:
                    cli.main(argv)
                self.assertEqual(caught.exception.code, 0)
            self.assertEqual(cli.main([]), 0)
        with self.assertRaises(ValueError):
            run_trusted_case('python -c "print(123)"')


class RecorderTests(unittest.TestCase):
    def run_cases(self, case):
        return check.execute(unittest.defaultTestLoader.loadTestsFromTestCase(case), io.StringIO())

    def test_each_actual_nonpassing_outcome_is_rejected(self):
        class Outcomes(unittest.TestCase):
            def test_pass(self): pass
            def test_fail(self): self.fail('fixture failure')
            def test_error(self): raise RuntimeError('fixture error')
            @unittest.skip('fixture skip')
            def test_skip(self): pass
            @unittest.expectedFailure
            def test_expected(self): self.fail('expected')
            @unittest.expectedFailure
            def test_unexpected(self): pass
        result = self.run_cases(Outcomes)
        self.assertFalse(result['passed'])
        self.assertEqual({row['outcome'] for row in result['records']},
                         {'passed', 'failed', 'error', 'skipped', 'expected_failure', 'unexpected_success'})

    def test_subtest_and_setup_errors_cannot_become_a_pass(self):
        class Subtest(unittest.TestCase):
            def test_bad(self):
                with self.subTest(value=1): self.assertEqual(1, 2)
        class Setup(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise RuntimeError('fixture setup failure')
            def test_never_run(self): pass
        for case in (Subtest, Setup):
            result = self.run_cases(case)
            self.assertFalse(result['passed'])
            self.assertTrue(result['records'])
            self.assertNotIn('passed', {row['outcome'] for row in result['records']})

    def test_missing_extra_duplicate_or_malformed_results_fail_closed(self):
        row = {'test_id': 'a', 'outcome': 'passed', 'details': '', 'elapsed_seconds': 0.0}
        self.assertEqual(check.assess(['a'], [row]), [])
        for ids, rows in (([], []), (['a', 'a'], [row]), (['a'], []),
                          (['b'], [row]), (['a'], [row, row]), (['a'], [{'test_id': 'a'}])):
            self.assertTrue(check.assess(ids, rows))
        for elapsed in (True, -1, float('nan'), float('inf')):
            bad = dict(row, elapsed_seconds=elapsed)
            self.assertTrue(check.assess(['a'], [bad]))

    def test_full_discovery_has_no_retired_gate_chain_or_zero_selection(self):
        names = [test.id() for test in check.discover()]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(names)
        retired = ('tests.test_scaffold.', 'tests.test_phase2_gate.', 'tests.test_phase3_gate.', 'tests.test_phase4_gate.')
        self.assertFalse(any(name.startswith(retired) for name in names))
        with self.assertRaisesRegex(ValueError, 'unknown_selection'):
            check.discover(['tests.no_such_module'])
        selected = check.discover(['tests.test_metrics'])
        self.assertTrue(selected)
        self.assertTrue(all(case.id().startswith('tests.test_metrics.') for case in selected))

    def test_discovery_import_failure_and_duplicate_ids_are_rejected(self):
        class Good(unittest.TestCase):
            def test_ok(self): pass
        case = Good('test_ok')
        with patch.object(unittest.TestLoader, 'discover', return_value=unittest.TestSuite([case, case])):
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                check.discover()
        def broken(loader, *args, **kwargs):
            loader.errors.append('actual import problem')
            return unittest.TestSuite([case])
        with patch.object(unittest.TestLoader, 'discover', broken):
            with self.assertRaisesRegex(ValueError, 'test_import_error'):
                check.discover()

    def test_help_and_invalid_cli_never_execute_tests(self):
        with patch.object(check, 'run_canonical', side_effect=AssertionError('executed')), patch.object(check, 'run_release', side_effect=AssertionError('executed')):
            for argv in (['--help'], ['release', '--output-dir', '/tmp/unused'], ['canonical', '--archive', '/tmp/a.zip', '--output-dir', '/tmp/unused']):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    check.main(argv)

    def test_parallel_execution_preserves_module_fixture_lifecycle(self):
        # Two independent fixed trusted cases exercise subprocess partitioning,
        # import origin, callback outcomes and source identity without recursion.
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'run'
            result = check.run_canonical(ROOT, output,
                ('tests.test_verification.PackageAndCommandTests.test_standard_library_import_and_metadata_agree',
                 'tests.test_metrics.Thresholds'), jobs=2)
            self.assertTrue(result['passed'], result['errors'])
            self.assertTrue(result['source_unchanged'])
            self.assertEqual(check.assess(result['canonical']['discovered'], result['canonical']['records']), [])
            self.assertFalse(result['substantive_validation_performed'])
            self.assertFalse(result['remote_publication_verified'])


class SourceAndOutputTests(unittest.TestCase):
    def test_current_bytes_modes_and_inventory_all_participate_in_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); p = root / 'module.py'; p.write_bytes(b'one'); p.chmod(0o644)
            first = check.source_identity(root)
            p.write_bytes(b'two'); self.assertNotEqual(first, check.source_identity(root))
            p.write_bytes(b'one'); p.chmod(0o755); self.assertNotEqual(first, check.source_identity(root))
            p.chmod(0o644); (root / 'extra.txt').write_bytes(b'new'); self.assertNotEqual(first, check.source_identity(root))
            (root / 'extra.txt').unlink(); self.assertEqual(first, check.source_identity(root))

    def test_symlinks_and_concealed_nonbytecode_are_not_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'source'; root.mkdir()
            cache = root / '__pycache__'; cache.mkdir()
            (cache / 'concealed.txt').write_bytes(b'content')
            self.assertEqual(check.source_identity(root)['files'][0]['path'], '__pycache__/concealed.txt')
            (root / 'link').symlink_to(cache, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink_source'):
                check.source_identity(root)

    def test_existing_or_symlink_output_is_refused_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); old = root / 'old'; old.mkdir(); (old / 'keep').write_bytes(b'kept')
            link = root / 'link'; link.symlink_to(old, target_is_directory=True)
            for output in (old, link, link / 'new'):
                with patch.object(check, 'run_canonical', side_effect=AssertionError('executed')), redirect_stderr(io.StringIO()):
                    self.assertEqual(check.main(['canonical', '--output-dir', str(output)]), 2)
            self.assertEqual((old / 'keep').read_bytes(), b'kept')
            self.assertFalse((old / 'new').exists())
            path = root / 'result.json'; path.write_bytes(b'prior')
            with self.assertRaises(FileExistsError): check.write_new(path, {'new': 'value'})
            self.assertEqual(path.read_bytes(), b'prior')

    def test_source_drift_during_execution_blocks_success(self):
        class Good(unittest.TestCase):
            def test_ok(self): pass
        with tempfile.TemporaryDirectory() as temporary, patch.object(check, 'discover', return_value=[Good('test_ok')]), patch.object(check, 'source_identity', side_effect=[{'sha256':'a','files':[]},{'sha256':'b','files':[]} ]):
            result = check.run_canonical(ROOT, Path(temporary) / 'out')
        self.assertFalse(result['passed'])
        self.assertIn('source_changed_during_execution', result['errors'])


class ReceiptTests(unittest.TestCase):
    """Synthetic receipt tampering tests do not constitute scientific runs."""
    def receipt(self):
        class Good(unittest.TestCase):
            def test_ok(self): pass
        execution = check.execute(unittest.TestSuite([Good('test_ok')]), io.StringIO())
        receipt = {'schema_version': '1', 'suite': 'canonical', 'selection': [],
                   'passed': True, 'errors': [], 'canonical': execution,
                   'execution_id': 'a' * 32, 'command': ['trusted-python', '-B', '-S', 'tools/check.py'],
                   'elapsed_seconds': 1.0, 'source_identity': {'sha256': 'b' * 64, 'files': []},
                   'environment': {'python': 'fixture', 'bytecode_disabled': True},
                   'source_unchanged': True, 'environment_unchanged': True,
                   'software_verification_only': True, 'substantive_validation_performed': False,
                   'remote_publication_verified': False}
        expected = {'expected_source': receipt['source_identity'],
                    'expected_environment': receipt['environment'], 'expected_selection': [],
                    'expected_discovered': execution['discovered'],
                    'expected_execution_id': receipt['execution_id'], 'expected_command': receipt['command']}
        return receipt, copy.deepcopy(expected)

    def test_aggregate_pass_cannot_replace_complete_actual_outcomes(self):
        original, expected = self.receipt()
        self.assertEqual(check.assess_canonical_receipt(original, **expected), [])
        damaged = []
        for records in ([], [original['canonical']['records'][0]] * 2, {}, 'passed', None):
            receipt = copy.deepcopy(original); receipt['canonical']['records'] = records
            damaged.append(receipt)
        for outcome in ('failed', 'error', 'skipped', 'expected_failure', 'unexpected_success', 'success'):
            receipt = copy.deepcopy(original); receipt['canonical']['records'][0]['outcome'] = outcome
            damaged.append(receipt)
        receipt = copy.deepcopy(original); receipt['canonical'] = {'passed': True, 'tests': 1}
        damaged.append(receipt)
        for receipt in damaged:
            with self.subTest(receipt=receipt):
                self.assertTrue(check.assess_canonical_receipt(receipt, **expected))

    def test_changed_scope_source_runtime_invocation_and_command_fail(self):
        original, expected = self.receipt()
        for field, value in (('selection', ['tests.partial']), ('execution_id', 'c' * 32),
                             ('command', ['other-python']), ('source_unchanged', False),
                             ('environment_unchanged', False), ('source_identity', {'sha256': 'old'}),
                             ('environment', {'python': 'stale', 'bytecode_disabled': True})):
            with self.subTest(field=field):
                receipt = copy.deepcopy(original); receipt[field] = value
                self.assertTrue(check.assess_canonical_receipt(receipt, **expected))
        receipt = copy.deepcopy(original)
        receipt['canonical']['discovered'] = ['invented.test']
        receipt['canonical']['records'][0]['test_id'] = 'invented.test'
        self.assertIn('execution_selection_mismatch', check.assess_canonical_receipt(receipt, **expected))

    def test_boolean_number_and_malformed_summary_types_fail_closed(self):
        original, expected = self.receipt()
        for field, value in (('passed', 1), ('errors', False), ('source_unchanged', 1),
                             ('environment_unchanged', 1), ('execution_id', 3),
                             ('command', 'trusted-python'), ('elapsed_seconds', True),
                             ('elapsed_seconds', float('nan')), ('elapsed_seconds', float('inf')),
                             ('elapsed_seconds', -1), ('canonical', None)):
            with self.subTest(field=field, value=value):
                receipt = copy.deepcopy(original); receipt[field] = value
                self.assertTrue(check.assess_canonical_receipt(receipt, **expected))
        receipt = copy.deepcopy(original); receipt['environment']['bytecode_disabled'] = 1
        self.assertIn('environment_mismatch', check.assess_canonical_receipt(receipt, **expected))
        for discovery in ('a', {}, [None], [True], [['nested']], [''], None):
            self.assertTrue(check.assess(discovery, []))
        receipt = copy.deepcopy(original); receipt['canonical']['passed'] = 1
        self.assertTrue(check.assess_canonical_receipt(receipt, **expected))

    def test_scientific_or_remote_promotion_cannot_be_a_software_receipt(self):
        original, expected = self.receipt()
        for field in ('software_verification_only', 'substantive_validation_performed', 'remote_publication_verified'):
            receipt = copy.deepcopy(original); receipt[field] = not receipt[field]
            self.assertIn(field + '_mismatch', check.assess_canonical_receipt(receipt, **expected))
            receipt[field] = int(original[field])
            self.assertIn(field + '_mismatch', check.assess_canonical_receipt(receipt, **expected))

    def test_strict_receipt_reader_rejects_duplicate_nonfinite_and_deep_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'receipt.json'
            for data in (b'{"passed":false,"passed":true}', b'{"elapsed_seconds":NaN}',
                         b'{"elapsed_seconds":Infinity}', b'{"unfinished":', b'[' * 2000 + b'0' + b']' * 2000):
                path.write_bytes(data)
                with self.assertRaises(ValueError): check.read_receipt(path)
            path.write_bytes(b'{"passed":true}')
            self.assertEqual(check.read_receipt(path), {'passed': True})

    def test_worker_requested_source_or_runtime_mismatch_prevents_execution(self):
        original, expected = self.receipt()
        spec = {'execution_id': original['execution_id'], 'selection': expected['expected_discovered'],
                'source_sha256': original['source_identity']['sha256'], 'environment': original['environment']}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'spec.json'
            for field, value in (('source_sha256', 'old'), ('environment', {'python': 'stale'})):
                damaged = copy.deepcopy(spec); damaged[field] = value
                path.write_bytes(check.canonical(damaged))
                with patch.object(check, 'source_identity', return_value=original['source_identity']), \
                     patch.object(check, 'environment', return_value=original['environment']), \
                     patch.object(check, 'discover', side_effect=AssertionError('executed')):
                    with self.assertRaisesRegex(ValueError, 'worker_requested_identity_mismatch'):
                        check.run_worker(path, Path(temporary) / 'result.json')
                self.assertFalse((Path(temporary) / 'result.json').exists())

    def test_parallel_parent_rejects_stale_missing_and_fabricated_workers(self):
        class First(unittest.TestCase):
            def test_ok(self): pass
        class Second(unittest.TestCase):
            def test_ok(self): pass
        cases = [First('test_ok'), Second('test_ok')]
        original, _ = self.receipt()
        for corruption in ('missing', 'malformed', 'execution_id', 'source_sha256', 'selection', 'environment',
                           'records', 'malformed_records', 'failed_outcome', 'nonzero'):
            def launch(command, **kwargs):
                spec = check.read_receipt(command[-2]); path = Path(command[-1])
                records = [{'test_id': name, 'outcome': 'passed', 'details': '', 'elapsed_seconds': 0.0}
                           for name in spec['selection']]
                part = dict(spec, source_unchanged=True, environment_unchanged=True, command=command,
                            canonical={'discovered': spec['selection'], 'records': records, 'passed': True, 'errors': []})
                if corruption == 'missing': pass
                elif corruption == 'malformed': path.write_bytes(b'{"incomplete":')
                else:
                    if corruption == 'records': part['canonical']['records'] = []
                    elif corruption == 'malformed_records': part['canonical']['records'] = [True]
                    elif corruption == 'failed_outcome': part['canonical']['records'][0]['outcome'] = 'failed'
                    elif corruption == 'nonzero': pass
                    elif corruption == 'selection': part['selection'] = ['other.test']
                    elif corruption == 'environment': part['environment'] = {'python': 'old'}
                    else: part[corruption] = '0' * 32
                    path.write_bytes(check.canonical(part))
                return type('Process', (), {'wait': lambda self: int(corruption == 'nonzero')})()
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as temporary, \
                 patch.object(check, 'discover', return_value=cases), \
                 patch.object(check, 'source_identity', return_value=original['source_identity']), \
                 patch.object(check, 'environment', return_value=original['environment']), \
                 patch.object(check.subprocess, 'Popen', side_effect=launch):
                result = check.run_canonical(ROOT, Path(temporary) / 'run', jobs=2)
                self.assertFalse(result['passed'])
                self.assertTrue(result['errors'])
                if corruption == 'failed_outcome':
                    self.assertEqual(len(result['canonical']['records']), len(cases))
                    self.assertIn('failed', {row['outcome'] for row in result['canonical']['records']})
                elif corruption == 'malformed_records':
                    self.assertEqual(result['canonical']['records'], [])

    def test_clean_parent_rechecks_receipt_instead_of_trusting_passed(self):
        original, _ = self.receipt()
        class Good(unittest.TestCase):
            def test_ok(self): pass
        case = Good('test_ok')
        for corruption in ('source_identity', 'environment', 'execution_id', 'selection', 'canonical', 'remote_publication_verified'):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as temporary:
                clean = Path(temporary) / 'clean'; clean.mkdir()
                output = Path(temporary) / 'result'
                def run(command, **kwargs):
                    receipt = copy.deepcopy(original)
                    receipt['execution_id'] = command[command.index('--_execution-id') + 1]
                    receipt['command'] = command
                    receipt['canonical']['discovered'] = [case.id()]
                    receipt['canonical']['records'][0]['test_id'] = case.id()
                    if corruption == 'remote_publication_verified': receipt[corruption] = True
                    elif corruption == 'canonical': receipt['canonical']['records'] = []
                    elif corruption == 'selection': receipt[corruption] = ['partial']
                    else: receipt[corruption] = 'stale'
                    output.mkdir(); check.write_new(output / 'result.json', receipt)
                    return subprocess.CompletedProcess(command, 0, b'', b'')
                with patch.object(check, 'source_identity', return_value=original['source_identity']), \
                     patch.object(check, 'environment', return_value=original['environment']), \
                     patch.object(check, 'discover', return_value=[case]), \
                     patch.object(check.subprocess, 'run', side_effect=run):
                    with self.assertRaisesRegex(ValueError, 'extracted_canonical_receipt_rejected'):
                        check.run_canonical(clean, output)

    def test_release_requires_exact_clean_receipt_and_each_release_check(self):
        child, expected = self.receipt()
        release = {'schema_version': '1', 'suite': 'release', 'passed': True,
                   'source_identity': child['source_identity'], 'environment': child['environment'],
                   'environment_unchanged': True, 'canonical': child['canonical'],
                   'canonical_execution_id': child['execution_id'], 'canonical_command': child['command'],
                   'archive_sha256': 'd' * 64, 'command': ['release-command'], 'elapsed_seconds': 1,
                   'software_verification_only': True, 'substantive_validation_performed': False,
                   'remote_publication_verified': False, 'package_build': 'not_requested_source_delivery'}
        names = ['hero_recursive_command_0', 'hero_recursive_command_1', 'hero_recursive_command_2',
                 'hero_recursive_command_3', 'hero_recursive_output_inventory', 'hero_recursive_replayed_reports_equal',
                 'hero_recursive_no_overwrite', 'categorical_null_command_0', 'categorical_null_command_1',
                 'categorical_null_command_2', 'categorical_null_command_3', 'categorical_null_output_inventory',
                 'categorical_null_replayed_reports_equal', 'categorical_null_no_overwrite',
                 'clean_source_unchanged', 'working_source_unchanged', 'archive_unchanged']
        release['release_checks'] = [dict(check=name, passed=True, **({'exit_code': 0} if '_command_' in name else {})) for name in names]
        args = {key: expected[key] for key in ('expected_source', 'expected_environment', 'expected_discovered')}
        args.update(expected_archive_sha256='d' * 64, canonical_receipt=child, expected_command=release['command'])
        self.assertEqual(check.assess_release_receipt(release, **args), [])
        for field, value in (('canonical_execution_id', 'old'), ('canonical_command', ['old-command']),
                             ('canonical', {'passed': True}), ('archive_sha256', 'old'),
                             ('passed', 1), ('remote_publication_verified', True),
                             ('substantive_validation_performed', True), ('software_verification_only', False),
                             ('environment_unchanged', False), ('release_checks', [])):
            with self.subTest(field=field):
                damaged = copy.deepcopy(release); damaged[field] = value
                self.assertTrue(check.assess_release_receipt(damaged, **args))
        for operation in ('missing', 'duplicate', 'nonpassing', 'boolean_exit', 'integer_pass'):
            damaged = copy.deepcopy(release)
            if operation == 'missing': damaged['release_checks'].pop()
            elif operation == 'duplicate': damaged['release_checks'][-1] = damaged['release_checks'][0]
            elif operation == 'nonpassing': damaged['release_checks'][0]['passed'] = False
            elif operation == 'boolean_exit': damaged['release_checks'][0]['exit_code'] = False
            else: damaged['release_checks'][0]['passed'] = 1
            self.assertTrue(check.assess_release_receipt(damaged, **args))
        narrowed = copy.deepcopy(child); narrowed['selection'] = ['partial']
        args['canonical_receipt'] = narrowed
        self.assertTrue(check.assess_release_receipt(release, **args))


class ArchiveTests(unittest.TestCase):
    def archive(self, path, rows):
        with zipfile.ZipFile(path, 'w') as package:
            for name, data, mode in rows:
                item = zipfile.ZipInfo(name); item.external_attr = mode << 16
                package.writestr(item, data)

    def test_archive_content_and_executable_modes_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); archive = root / 'source.zip'
            self.archive(archive, [('structdet-bench/a.py', b'alpha', stat.S_IFREG | 0o755), ('structdet-bench/sub/data.json', b'{}', stat.S_IFREG | 0o644)])
            extracted = check.extract_source(archive, root / 'out')
            rows = check.source_identity(extracted)['files']
            self.assertEqual([(row['path'], row['git_mode']) for row in rows], [('a.py','100755'),('sub/data.json','100644')])
            self.assertEqual((extracted / 'a.py').read_bytes(), b'alpha')

    def test_traversal_absolute_duplicate_and_symlink_archives_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            unsafe = [('structdet-bench/../escape', stat.S_IFREG), ('/absolute', stat.S_IFREG), ('structdet-bench//a', stat.S_IFREG), ('structdet-bench/link', stat.S_IFLNK)]
            for index, (name, mode) in enumerate(unsafe):
                archive = root / f'bad{index}.zip'; self.archive(archive, [(name, b'x', mode)])
                with self.assertRaises(ValueError):check.extract_source(archive, root / f'out{index}')
            archive = root / 'duplicate.zip'
            with __import__('warnings').catch_warnings():
                __import__('warnings').simplefilter('ignore', UserWarning)
                self.archive(archive,[('structdet-bench/a',b'one',stat.S_IFREG),('structdet-bench/a',b'two',stat.S_IFREG)])
            with self.assertRaisesRegex(ValueError,'duplicate'):check.extract_source(archive,root/'dupout')
            self.assertFalse((root / 'escape').exists())

    def test_wrong_archive_source_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); archive = root / 'wrong.zip'
            self.archive(archive, [('structdet-bench/a', b'x', stat.S_IFREG | 0o644)])
            with patch.object(check,'run_canonical',side_effect=AssertionError('executed')):
                with self.assertRaisesRegex(ValueError,'archive_source_mismatch'):
                    check.run_release(archive,root/'release')
