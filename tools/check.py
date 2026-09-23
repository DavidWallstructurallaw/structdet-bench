#!/usr/bin/env python3
"""Stable offline regression and release qualification for trusted project tests.

This development tool never executes submitted candidate programs or establishes
empirical validation. Results describe only the identified software execution.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import secrets
import stat
import subprocess
import sys
import tempfile
import time
import unicodedata
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       indent=2) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def environment():
    executable = Path(sys.executable).resolve()
    return {'implementation': platform.python_implementation(), 'python': platform.python_version(),
            'unicode': unicodedata.unidata_version, 'platform': platform.platform(),
            'executable': str(executable), 'executable_sha256': digest(executable.read_bytes()),
            'bytecode_disabled': bool(sys.dont_write_bytecode), 'site_disabled': bool(sys.flags.no_site)}


def no_symlinks(path):
    path = Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('symlink_path')
    return path


def source_identity(root=ROOT):
    root = no_symlinks(root)
    rows = []
    for base, directories, files in os.walk(root, followlinks=False):
        base = Path(base)
        for name in list(directories):
            p = base / name
            if p.is_symlink():
                raise ValueError('symlink_source')
            if name == '.git':
                directories.remove(name)
        for name in files:
            p = base / name
            mode = p.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise ValueError('nonregular_source')
            relative = p.relative_to(root)
            if '__pycache__' in relative.parts and p.suffix == '.pyc':
                continue
            data = p.read_bytes()
            rows.append({'path': relative.as_posix(), 'sha256': digest(data), 'size_bytes': len(data),
                         'git_mode': '100755' if mode & 0o111 else '100644'})
    rows.sort(key=lambda r: r['path'])
    if not rows:
        raise ValueError('empty_source')
    return {'sha256': digest(canonical(rows)), 'files': rows}


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def discover(select=(), root=ROOT):
    loader = unittest.TestLoader()
    suite = loader.discover(str(Path(root) / 'tests'), top_level_dir=str(root))
    if loader.errors:
        raise ValueError('test_import_error: ' + '\n'.join(loader.errors))
    cases = list(flatten(suite))
    ids = [test.id() for test in cases]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('empty_or_duplicate_discovery')
    for prefix in select:
        if not any(name == prefix or name.startswith(prefix + '.') for name in ids):
            raise ValueError('unknown_selection: ' + prefix)
    if select:
        cases = [case for case in cases if any(case.id() == p or case.id().startswith(p + '.') for p in select)]
    return sorted(cases, key=lambda case: case.id())


class Recorder(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self._started = {}

    def startTest(self, test):
        super().startTest(test)
        self._started[test.id()] = time.monotonic()

    def record(self, test, outcome, details=''):
        self.records.append({'test_id': test.id(), 'outcome': outcome, 'details': details,
                             'elapsed_seconds': max(0, time.monotonic() - self._started.get(test.id(), time.monotonic()))})

    def addSuccess(self, test):
        super().addSuccess(test); self.record(test, 'passed')

    def addFailure(self, test, err):
        super().addFailure(test, err); self.record(test, 'failed', self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err); self.record(test, 'error', self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason); self.record(test, 'skipped', reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err); self.record(test, 'expected_failure', self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test); self.record(test, 'unexpected_success')

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.record(test, 'failed', self._exc_info_to_string(err, subtest))


def assess(discovered, records):
    errors = []
    if (not isinstance(discovered, list) or any(not isinstance(name, str) or not name for name in discovered)
            or not isinstance(records, list)):
        return ['malformed_execution_record']
    if not discovered:
        errors.append('zero_discovery')
    if len(discovered) != len(set(discovered)):
        errors.append('duplicate_discovery')
    if any(not isinstance(r, dict) or set(r) != {'test_id', 'outcome', 'details', 'elapsed_seconds'}
           or not isinstance(r['test_id'], str) or not isinstance(r['outcome'], str)
           or not isinstance(r['details'], str) or type(r['elapsed_seconds']) not in (int, float)
           or not 0 <= r['elapsed_seconds'] < float('inf') for r in records):
        return ['malformed_execution_record']
    ids = [r['test_id'] for r in records]
    if len(ids) != len(set(ids)):
        errors.append('duplicate_execution')
    if set(ids) != set(discovered):
        errors.append('missing_or_extra_execution')
    if any(r['outcome'] != 'passed' for r in records):
        errors.append('nonpassing_execution')
    return errors


def same_json(left, right):
    """Compare JSON identity without Python's bool/integer equivalence."""
    try:
        return canonical(left) == canonical(right)
    except (TypeError, ValueError, OverflowError, RecursionError):
        return False


def assess_execution(expected, result):
    if not isinstance(result, dict) or set(result) != {'discovered', 'records', 'errors', 'passed'}:
        return ['malformed_execution_summary']
    errors = assess(result['discovered'], result['records'])
    if not same_json(result['discovered'], expected):
        errors.append('execution_selection_mismatch')
    if result['passed'] is not True or result['errors'] != []:
        errors.append('nonpassing_execution_summary')
    return errors


def assess_canonical_receipt(result, *, expected_source, expected_environment,
                             expected_selection, expected_discovered,
                             expected_execution_id=None, expected_command=None):
    """Review current software outcomes against independently supplied identities.

    The invocation ID correlates a child process with its parent; it is neither
    authentication nor a historical approval identity. A self-consistent edited
    receipt cannot establish that execution happened outside this trusted runner.
    """
    if not isinstance(result, dict):
        return ['malformed_canonical_receipt']
    errors = assess_execution(expected_discovered, result.get('canonical'))
    if (result.get('schema_version') != '1' or result.get('suite') != 'canonical'
            or result.get('passed') is not True or result.get('errors') != []):
        errors.append('nonpassing_canonical_receipt')
    for key, expected in (('source_identity', expected_source), ('environment', expected_environment),
                          ('selection', list(expected_selection))):
        if not same_json(result.get(key), expected):
            errors.append(key + '_mismatch')
    for key, expected in (('source_unchanged', True), ('environment_unchanged', True),
                          ('software_verification_only', True), ('substantive_validation_performed', False),
                          ('remote_publication_verified', False)):
        if result.get(key) is not expected:
            errors.append(key + '_mismatch')
    identity = result.get('execution_id')
    if (not isinstance(identity, str) or len(identity) != 32
            or any(char not in '0123456789abcdef' for char in identity)
            or (expected_execution_id is not None and identity != expected_execution_id)):
        errors.append('execution_id_mismatch')
    command = result.get('command')
    if (not isinstance(command, list) or not command
            or any(not isinstance(arg, str) for arg in command)
            or (expected_command is not None and command != expected_command)):
        errors.append('command_mismatch')
    elapsed = result.get('elapsed_seconds')
    if type(elapsed) not in (int, float) or not 0 <= elapsed < float('inf'):
        errors.append('malformed_elapsed_seconds')
    return errors


def assess_release_receipt(result, *, expected_source, expected_environment,
                          expected_discovered, expected_archive_sha256,
                          canonical_receipt, expected_command=None):
    """Review the release result and its directly associated clean execution."""
    errors = assess_canonical_receipt(canonical_receipt, expected_source=expected_source,
        expected_environment=expected_environment, expected_selection=[],
        expected_discovered=expected_discovered)
    if not isinstance(result, dict):
        return errors + ['malformed_release_receipt']
    if (result.get('schema_version') != '1' or result.get('suite') != 'release'
            or result.get('passed') is not True
            or result.get('package_build') != 'not_requested_source_delivery'):
        errors.append('nonpassing_release_receipt')
    for key, expected in (('source_identity', expected_source), ('environment', expected_environment),
                          ('archive_sha256', expected_archive_sha256)):
        if not same_json(result.get(key), expected):
            errors.append(key + '_mismatch')
    for key, expected in (('environment_unchanged', True), ('software_verification_only', True),
                          ('substantive_validation_performed', False), ('remote_publication_verified', False)):
        if result.get(key) is not expected:
            errors.append(key + '_mismatch')
    if isinstance(canonical_receipt, dict):
        for outer, inner in (('canonical', 'canonical'), ('canonical_execution_id', 'execution_id'),
                             ('canonical_command', 'command')):
            if not same_json(result.get(outer), canonical_receipt.get(inner)):
                errors.append('release_' + outer + '_mismatch')
    expected_checks = []
    for example in ('hero_recursive', 'categorical_null'):
        expected_checks.extend({'check': f'{example}_command_{index}', 'passed': True, 'exit_code': 0}
                               for index in range(4))
        expected_checks.extend({'check': example + '_' + name, 'passed': True}
                               for name in ('output_inventory', 'replayed_reports_equal', 'no_overwrite'))
    expected_checks.extend({'check': name, 'passed': True}
                           for name in ('clean_source_unchanged', 'working_source_unchanged', 'archive_unchanged'))
    if not same_json(result.get('release_checks'), expected_checks):
        errors.append('release_checks_mismatch')
    command = result.get('command')
    if (not isinstance(command, list) or not command or any(not isinstance(arg, str) for arg in command)
            or (expected_command is not None and command != expected_command)):
        errors.append('command_mismatch')
    elapsed = result.get('elapsed_seconds')
    if type(elapsed) not in (int, float) or not 0 <= elapsed < float('inf'):
        errors.append('malformed_elapsed_seconds')
    return errors


def read_receipt(path):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError('duplicate_receipt_key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('nonfinite_receipt_number')
    with no_symlinks(path).open('rb') as handle:
        data = handle.read(64 * 1024 * 1024 + 1)
    if len(data) > 64 * 1024 * 1024:
        raise ValueError('receipt_limit_exceeded')
    try:
        result = json.loads(data, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except RecursionError as error:
        raise ValueError('receipt_nesting_limit_exceeded') from error
    pending = [(result, 0)]
    while pending:
        value, depth = pending.pop()
        if isinstance(value, (dict, list)):
            if depth >= 64:
                raise ValueError('receipt_nesting_limit_exceeded')
            children = value.values() if isinstance(value, dict) else value
            pending.extend((child, depth + 1) for child in children)
    return result


def execute(suite, stream):
    expected = [test.id() for test in flatten(suite)]
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Recorder).run(suite)
    return {'discovered': expected, 'records': result.records, 'errors': assess(expected, result.records),
            'passed': not assess(expected, result.records)}


def write_new(path, value):
    with Path(path).open('xb') as handle:
        handle.write(canonical(value))


def worker_receipt_errors(part, spec, command):
    if not isinstance(part, dict):
        return ['malformed_worker_receipt']
    errors = assess_execution(spec['selection'], part.get('canonical'))
    for key in ('execution_id', 'selection', 'source_sha256', 'environment'):
        if not same_json(part.get(key), spec[key]):
            errors.append('worker_' + key + '_mismatch')
    if part.get('source_unchanged') is not True or part.get('environment_unchanged') is not True:
        errors.append('worker_identity_changed')
    if part.get('command') != command:
        errors.append('worker_command_mismatch')
    return errors


def run_worker(spec_path, result_path):
    spec = read_receipt(spec_path)
    if (not isinstance(spec, dict)
            or set(spec) != {'execution_id', 'selection', 'source_sha256', 'environment'}
            or not isinstance(spec['selection'], list)
            or not spec['selection'] or any(not isinstance(name, str) or not name for name in spec['selection'])
            or len(set(spec['selection'])) != len(spec['selection'])
            or not isinstance(spec['execution_id'], str) or len(spec['execution_id']) != 32
            or any(char not in '0123456789abcdef' for char in spec['execution_id'])):
        raise ValueError('malformed_worker_specification')
    before, runtime = source_identity(), environment()
    if spec['source_sha256'] != before['sha256'] or not same_json(spec['environment'], runtime):
        raise ValueError('worker_requested_identity_mismatch')
    available = {case.id(): case for case in discover(spec['selection'])}
    if set(available) != set(spec['selection']):
        raise ValueError('worker_selection_mismatch')
    execution = execute(unittest.TestSuite(available[name] for name in spec['selection']), sys.stdout)
    result = {'execution_id': spec['execution_id'], 'selection': spec['selection'],
              'source_sha256': before['sha256'], 'environment': runtime,
              'source_unchanged': before == source_identity(),
              'environment_unchanged': same_json(runtime, environment()),
              'command': list(sys.orig_argv), 'canonical': execution}
    write_new(result_path, result)
    return 0 if not worker_receipt_errors(result, spec, list(sys.orig_argv)) else 1


def run_canonical(root, output, select=(), jobs=1, execution_id=None):
    started = time.monotonic()
    root = Path(root)
    execution_id = execution_id or secrets.token_hex(16)
    runtime = environment()
    if root != ROOT:
        # Execute the fixed trusted checker from the extracted project, so its
        # imports and software identity cannot accidentally resolve to this tree.
        before = source_identity(root)
        if before != source_identity(ROOT):
            raise ValueError('extracted_canonical_source_mismatch')
        expected = [case.id() for case in discover(select)]
        if output.exists() or not output.parent.is_dir():
            raise ValueError('extracted_canonical_output_must_be_new')
        command = [sys.executable, '-B', '-S', str(root / 'tools/check.py'), 'canonical',
                   '--output-dir', str(output), '--jobs', str(jobs), '--_execution-id', execution_id]
        for prefix in select:
            command += ['--select', prefix]
        process = subprocess.run(command, cwd=root, capture_output=True, check=False)
        if not (output / 'result.json').is_file():
            raise ValueError('extracted_canonical_missing_result')
        result = read_receipt(output / 'result.json')
        errors = assess_canonical_receipt(result, expected_source=before,
            expected_environment=runtime, expected_selection=select, expected_discovered=expected,
            expected_execution_id=execution_id, expected_command=command)
        if process.returncode != 0:
            errors.append('extracted_canonical_process_failed')
        if source_identity(root) != before or not same_json(runtime, environment()):
            errors.append('extracted_canonical_identity_changed')
        if errors:
            raise ValueError('extracted_canonical_receipt_rejected: ' + ','.join(errors))
        return result
    before = source_identity(root)
    cases = discover(select, root)
    names = [case.id() for case in cases]
    output.mkdir()
    if jobs == 1:
        with (output / 'console.txt').open('w', encoding='utf-8') as stream:
            execution = execute(unittest.TestSuite(cases), stream)
    else:
        groups = [[] for _ in range(min(jobs, len(names)))]; modules = {}
        for name in names:
            modules.setdefault(name.rsplit('.', 2)[0], []).append(name)
        for values in sorted(modules.values(), key=len, reverse=True):
            min(groups, key=len).extend(values)
        workers = []
        for index, group in enumerate(groups):
            if not group:
                continue
            spec = output / f'worker_{index}_selection.json'
            result_path = output / f'worker_{index}_result.json'
            specification = {'execution_id': execution_id, 'selection': group,
                             'source_sha256': before['sha256'], 'environment': runtime}
            write_new(spec, specification)
            stream = (output / f'worker_{index}_console.txt').open('wb')
            command = [sys.executable, '-B', '-S', str(root / 'tools/check.py'),
                       '--_worker', str(spec), str(result_path)]
            process = subprocess.Popen(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT)
            workers.append((process, stream, result_path, specification, command))
        records, errors = [], []
        for process, stream, result_path, specification, command in workers:
            code = process.wait(); stream.close()
            if not result_path.is_file():
                errors.append('missing_worker_result'); continue
            try:
                part = read_receipt(result_path)
                part_errors = worker_receipt_errors(part, specification, command)
            except (ValueError, OSError, UnicodeError):
                errors.append('malformed_worker_receipt'); continue
            errors.extend(part_errors)
            # Retain actual failures as outcomes when the worker's current-run
            # identity is intact. A stale worker is kept only as its raw receipt.
            if (not any(error.startswith('worker_') or error == 'malformed_worker_receipt' for error in part_errors)
                    and not {'malformed_execution_record', 'malformed_execution_summary',
                             'execution_selection_mismatch'}.intersection(part_errors)
                    and isinstance(part.get('canonical'), dict)
                    and isinstance(part['canonical'].get('records'), list)):
                records.extend(part['canonical']['records'])
            if code or part_errors:
                errors.append('worker_failed')
        errors += assess(names, records)
        execution = {'discovered': names, 'records': records, 'errors': errors, 'passed': not errors}
    after = source_identity(root)
    errors = list(execution['errors'])
    if before != after:
        errors.append('source_changed_during_execution')
    runtime_unchanged = same_json(runtime, environment())
    if not runtime_unchanged:
        errors.append('environment_changed_during_execution')
    result = {'schema_version': '1', 'suite': 'canonical', 'selection': list(select),
              'execution_id': execution_id, 'passed': not errors, 'errors': errors, 'environment': runtime,
              'environment_unchanged': runtime_unchanged,
              'source_identity': before, 'source_unchanged': before == after,
              'command': list(sys.orig_argv), 'elapsed_seconds': time.monotonic() - started,
              'canonical': execution, 'software_verification_only': True,
              'substantive_validation_performed': False, 'remote_publication_verified': False}
    write_new(output / 'result.json', result)
    return result


def extract_source(archive, destination):
    """Check the whole ZIP namespace, then extract only the source tree."""
    names = set(); files = []; total = 0
    with zipfile.ZipFile(archive) as package:
        for item in package.infolist():
            name = item.filename
            path = PurePosixPath(name)
            if (not name or name.startswith('/') or '\\' in name or ':' in name
                    or any(part in ('', '.', '..') for part in name.rstrip('/').split('/'))
                    or name.rstrip('/') in names):
                raise ValueError('unsafe_or_duplicate_archive_path')
            names.add(name.rstrip('/'))
            mode = item.external_attr >> 16
            if mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError('nonregular_archive_entry')
            total += item.file_size
            if total > 512 * 1024 * 1024 or len(names) > 10000:
                raise ValueError('archive_limit_exceeded')
            if path.parts[0] == 'structdet-bench' and not item.is_dir():
                if len(path.parts) < 2:
                    raise ValueError('invalid_source_root')
                files.append((item, path))
        if not files:
            raise ValueError('missing_archive_source')
        destination.mkdir()
        for item, path in files:
            target = destination.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as handle:
                handle.write(package.read(item))
            target.chmod(0o755 if (item.external_attr >> 16) & 0o111 else 0o644)
    return destination / 'structdet-bench'


def smoke_examples(root, output):
    """Exercise documented offline examples and exact saved-index replay."""
    output.mkdir()
    checks = []
    for example in ('hero_recursive', 'categorical_null'):
        bundle = root / 'examples' / example / 'bundle.json'
        fresh, replay = output / example, output / (example + '_replay')
        commands = [
            ['validate', '--bundle', str(bundle)],
            ['analyze', '--bundle', str(bundle), '--output-dir', str(fresh)],
            ['validate', '--bundle', str(bundle), '--replay-manifest', str(fresh / 'run_manifest.json')],
            ['analyze', '--bundle', str(bundle), '--replay-manifest', str(fresh / 'run_manifest.json'), '--output-dir', str(replay)],
        ]
        for index, args in enumerate(commands):
            process = subprocess.run([sys.executable, '-B', '-S', '-m', 'structdet_bench', *args], cwd=root, capture_output=True)
            (output / f'{example}_{index}.stdout').write_bytes(process.stdout)
            (output / f'{example}_{index}.stderr').write_bytes(process.stderr)
            checks.append({'check': f'{example}_command_{index}', 'passed': process.returncode == 0, 'exit_code': process.returncode})
            if process.returncode:
                return checks
        expected = {'report.json', 'report.md', 'run_manifest.json'}
        checks.append({'check': example + '_output_inventory', 'passed': {p.name for p in fresh.iterdir()} == expected == {p.name for p in replay.iterdir()}})
        checks.append({'check': example + '_replayed_reports_equal', 'passed': all((fresh / name).read_bytes() == (replay / name).read_bytes() for name in ('report.json', 'report.md'))})
        before = {p.name: digest(p.read_bytes()) for p in fresh.iterdir()}
        process = subprocess.run([sys.executable, '-B', '-S', '-m', 'structdet_bench', *commands[1]], cwd=root, capture_output=True)
        checks.append({'check': example + '_no_overwrite', 'passed': process.returncode == 2 and before == {p.name: digest(p.read_bytes()) for p in fresh.iterdir()}})
    return checks


def run_release(archive, output, jobs=1):
    started = time.monotonic()
    runtime = environment()
    before = source_identity()
    archive = no_symlinks(archive)
    archive_sha = digest(archive.read_bytes())
    output.mkdir()
    with tempfile.TemporaryDirectory(prefix='structdet-release-') as temporary:
        clean = extract_source(archive, Path(temporary) / 'extracted')
        if source_identity(clean) != before:
            raise ValueError('archive_source_mismatch')
        canonical_result = run_canonical(clean, output / 'canonical', jobs=jobs)
        checks = smoke_examples(clean, output / 'examples')
        checks.append({'check': 'clean_source_unchanged', 'passed': source_identity(clean) == before})
    checks += [{'check': 'working_source_unchanged', 'passed': source_identity() == before},
               {'check': 'archive_unchanged', 'passed': digest(archive.read_bytes()) == archive_sha}]
    runtime_unchanged = same_json(runtime, environment())
    result = {'schema_version': '1', 'suite': 'release',
              'passed': canonical_result['passed'] and all(row['passed'] for row in checks) and runtime_unchanged,
              'source_identity': before, 'environment': runtime, 'environment_unchanged': runtime_unchanged,
              'canonical': canonical_result['canonical'], 'canonical_execution_id': canonical_result['execution_id'],
              'canonical_command': canonical_result['command'],
              'release_checks': checks, 'archive_sha256': archive_sha,
              'command': list(sys.orig_argv), 'elapsed_seconds': time.monotonic() - started,
              'software_verification_only': True, 'substantive_validation_performed': False,
              'remote_publication_verified': False, 'package_build': 'not_requested_source_delivery'}
    write_new(output / 'result.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--_worker', nargs=2, help=argparse.SUPPRESS)
    parser.add_argument('--_execution-id', help=argparse.SUPPRESS)
    parser.add_argument('suite', nargs='?', choices=('canonical', 'release'))
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--select', action='append', default=[], help='Exact test, class or module prefix (canonical only).')
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--jobs', type=int, choices=range(1, 9), default=1)
    args = parser.parse_args(argv)
    if args._execution_id is not None and (len(args._execution_id) != 32
            or any(char not in '0123456789abcdef' for char in args._execution_id)):
        parser.error('invalid execution identity')
    if args._worker:
        try:
            return run_worker(*args._worker)
        except (ValueError, OSError, UnicodeError) as error:
            print('Verification worker failed: ' + str(error), file=sys.stderr)
            return 2
    if not args.suite or args.output_dir is None:
        parser.error('suite and --output-dir are required')
    if args.suite == 'release' and (args.archive is None or args.select):
        parser.error('release requires --archive and does not accept partial selection')
    if args.suite == 'canonical' and args.archive is not None:
        parser.error('--archive applies only to release')
    try:
        output = no_symlinks(args.output_dir)
        if output.exists() or not output.parent.is_dir():
            raise ValueError('output_must_be_new_with_existing_parent')
        if output == ROOT or ROOT in output.parents:
            raise ValueError('verification_output_must_be_outside_source')
        result = (run_canonical(ROOT, output, args.select, args.jobs, args._execution_id) if args.suite == 'canonical'
                  else run_release(args.archive, output, args.jobs))
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        print('Verification failed: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps({'suite': args.suite, 'passed': result['passed'],
                      'tests': len(result['canonical']['discovered']), 'result': str(output / 'result.json')}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
