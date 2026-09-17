"""Step 1 engineering checks. None is a substitute for a VF scientific test."""

from __future__ import annotations

from contextlib import ExitStack, redirect_stderr, redirect_stdout
import copy
import io
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import tomllib
import unittest
from unittest.mock import patch

import structdet_bench
from structdet_bench import cli
from tests.helpers import ROOT, baseline_checks, load_matrix, run_trusted_case, source_table
# Load this fixed trusted file rather than a possibly installed "tools" package.
_runner_spec = importlib.util.spec_from_file_location(
    "structdet_trusted_qa_runner", ROOT / "tools" / "run_phase1_checks.py"
)
assert _runner_spec is not None and _runner_spec.loader is not None
_runner = importlib.util.module_from_spec(_runner_spec)
_runner_spec.loader.exec_module(_runner)
append_journal = _runner.append_journal
assess_gate = _runner.assess_gate
execute_suite = _runner.execute_suite
validate_matrix = _runner.validate_matrix


class PackageTests(unittest.TestCase):
    def test_import_under_standard_library_only(self) -> None:
        result = run_trusted_case("import")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), structdet_bench.__version__)
        self.assertEqual(result.stderr, "")

    def test_version_matches_metadata(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(structdet_bench.__version__, "0.1.0.dev0")
        self.assertEqual(metadata["project"]["version"], structdet_bench.__version__)
        self.assertEqual(metadata["project"]["name"], "structdet-bench")
        self.assertEqual(metadata["project"]["requires-python"], ">=3.11")

    def test_metadata_has_no_runtime_dependencies(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["project"]["dependencies"], [])
        self.assertNotIn("scripts", metadata["project"])
        self.assertNotIn("license", metadata["project"])
        self.assertEqual(metadata["build-system"]["requires"], ["setuptools"])

    def test_distribution_excludes_tests_docs_and_pdfs(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        settings = metadata["tool"]["setuptools"]
        self.assertEqual(settings["packages"], ["structdet_bench"])
        self.assertFalse(settings["include-package-data"])
        self.assertNotIn("package-data", settings)
        self.assertFalse(list((ROOT / "structdet_bench").rglob("*.pdf")))

    def test_no_public_analysis_api(self) -> None:
        self.assertEqual(structdet_bench.__all__, ["__version__"])
        for name in ("analyze", "generate", "classify", "train"):
            self.assertFalse(hasattr(structdet_bench, name), name)


class CommandTests(unittest.TestCase):
    def test_help(self) -> None:
        result = run_trusted_case("help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--help", result.stdout)
        self.assertIn("--version", result.stdout)
        if load_matrix()["current_step"] < 6:
            self.assertIn("scaffold", result.stdout)
            self.assertIn("No ingestion", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_version(self) -> None:
        result = run_trusted_case("version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "StructDet-Bench 0.1.0.dev0\n")
        self.assertEqual(result.stderr, "")

    def test_no_arguments_show_help(self) -> None:
        result = run_trusted_case("no_args")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)
        self.assertNotIn('"observed_support_size"', result.stdout)

    def test_validate_and_analyze_require_input_or_are_unavailable(self) -> None:
        for case in ("validate_no_input", "analyze_no_input"):
            with self.subTest(case=case):
                result = run_trusted_case(case)
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_forbidden_commands_are_rejected(self) -> None:
        for command in ("generate", "train", "execute", "judge", "compare", "recover"):
            with self.subTest(command=command):
                result = run_trusted_case(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_unknown_option_is_error(self) -> None:
        result = run_trusted_case("unknown_option")
        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)

    def test_runtime_help_and_version_do_not_use_network_or_child_processes(self) -> None:
        # Narrow boundary test of these paths, not a general security proof.
        with ExitStack() as stack:
            for name in ("socket.socket", "socket.create_connection", "urllib.request.urlopen", "subprocess.Popen", "os.system"):
                stack.enter_context(patch(name, side_effect=AssertionError("Unexpected runtime I/O: " + name)))
            stack.enter_context(redirect_stdout(io.StringIO()))
            stack.enter_context(redirect_stderr(io.StringIO()))
            for argv in (["--help"], ["--version"]):
                with self.assertRaises(SystemExit) as context:
                    cli.main(argv)
                self.assertEqual(context.exception.code, 0)
            self.assertEqual(cli.main([]), 0)

    def test_trusted_helper_rejects_arbitrary_commands(self) -> None:
        with self.assertRaises(ValueError):
            run_trusted_case("python -c 'print(123)'")


class BaselineTests(unittest.TestCase):
    def test_all_baseline_hashes_match(self) -> None:
        checks = baseline_checks(load_matrix())
        self.assertEqual(len(checks), 12)
        self.assertTrue(all(row["status"] == "passed" for row in checks), checks)

    def test_expected_hashes_match_plan_appendix(self) -> None:
        matrix = load_matrix()
        text = (ROOT / "PHASE_1_PLAN.md").read_text(encoding="utf-8")
        expected = {
            name: (version.strip(), digest)
            for name, version, digest in re.findall(
                r"^\| `([^`]+\.md)` \| ([^|]+) \| `([0-9a-f]{64})` \|$", text, re.M
            )
        }
        actual = {
            row["path"]: (row["version"], row["sha256"])
            for row in matrix["baseline"] if row["role"] == "frozen_phase0"
        }
        self.assertEqual(len(expected), 11)
        self.assertEqual(actual, expected)

    def test_matrix_preserves_vf_catalogue(self) -> None:
        matrix = {row["id"]: row for row in load_matrix()["vf_tests"]}
        for row in source_table("VALIDATION_AND_FALSIFICATION.md", "VT"):
            actual = matrix[row[0]]
            self.assertEqual(actual["source_delivery"], row[1])
            self.assertEqual(actual["upstream_anchors"], [s.strip() for s in row[2].split(",")])
            self.assertEqual(actual["arrangement"], row[3])
            self.assertEqual(actual["required_outcome"], row[4])

    def test_matrix_preserves_trace_catalogue(self) -> None:
        matrix = {row["id"]: row for row in load_matrix()["trace_requirements"]}
        for row in source_table("THEORY_TO_CODE_TRACEABILITY.md", "TR"):
            actual = matrix[row[0]]
            self.assertEqual(actual["origin"], row[1])
            self.assertEqual(actual["controlling_rule"], row[2])
            self.assertEqual(actual["planned_responsibility"], row[3])
            self.assertEqual(actual["vf_ids"], re.findall(r"VT-\d{2}", row[4]))
            self.assertEqual(actual["report_groups"], re.findall(r"RF-\d{2}", row[5]))
            self.assertEqual(actual["permitted_inference"], row[6])
            self.assertEqual(actual["limitation"], row[7])

    def test_matrix_preserves_report_catalogue(self) -> None:
        matrix = {row["id"]: row for row in load_matrix()["report_groups"]}
        for row in source_table("THEORY_TO_CODE_TRACEABILITY.md", "RF"):
            actual = matrix[row[0]]
            self.assertEqual(actual["required_content"], row[1])
            self.assertEqual(actual["trace_ids"], re.findall(r"TR-\d{2}", row[2]))
            self.assertEqual(actual["vf_ids"], re.findall(r"VT-\d{2}", row[3]))

    def test_all_54_scope_dispositions_and_37_m_families(self) -> None:
        matrix = load_matrix()
        self.assertEqual(len(matrix["vf_tests"]), 54)
        expected_m = {row[0] for row in source_table("PHASE_1_PLAN.md", "VT")}
        actual_m = {row["id"] for row in matrix["vf_tests"] if row["m_required"]}
        self.assertEqual(len(actual_m), 37)
        self.assertEqual(actual_m, expected_m)
        for row in matrix["vf_tests"]:
            self.assertEqual(set(row["scope_records"]), set(re.findall(r"\b[MVED]\b", row["source_delivery"])))
            for scope, status in row["scope_records"].items():
                self.assertIn("implementation_status", status)
                self.assertNotIn("execution_status", status)
                if scope in {"E", "D"}:
                    self.assertEqual(status["test_bindings"], [])

    def test_matrix_validation(self) -> None:
        self.assertEqual(validate_matrix(load_matrix()), [])
        bad = copy.deepcopy(load_matrix())
        bad["vf_tests"][0]["m_required"] = False
        self.assertTrue(validate_matrix(bad))

    def test_readme_scope_is_explicit(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("PHASE_1_PLAN.md", readme)
        self.assertIn("No public software license has been selected", readme)
        if load_matrix()["current_step"] < 6:
            self.assertIn("scaffold only", readme)
            self.assertIn("exit code 1 is expected", readme)


class HarnessTests(unittest.TestCase):
    @staticmethod
    def synthetic_gate_inputs() -> tuple[dict, list[str], list[dict]]:
        """Mock a fully bound gate to test its logic, without altering the matrix."""
        matrix = copy.deepcopy(load_matrix())
        test_id = "tests.synthetic_gate_fixture.check"
        for row in matrix["engineering_requirements"]:
            row["test_bindings"] = [test_id]
        for row in matrix["vf_tests"]:
            if row["m_required"]:
                row["scope_records"]["M"]["implementation_status"] = "implemented"
                row["scope_records"]["M"]["test_bindings"] = [test_id]
        for field in ("trace_requirements", "report_groups"):
            for row in matrix[field]:
                if row["m_applicable"]:
                    row["implementation_status"] = "implemented"
                    row["test_bindings"] = [test_id]
        return matrix, [test_id], [{"test_id": test_id, "outcome": "passed"}]

    def test_empty_discovery_fails_both_gates(self) -> None:
        matrix, _, _ = self.synthetic_gate_inputs()
        ids, records, _ = execute_suite(unittest.TestSuite())
        for scope in ("scaffold", "phase1"):
            gate = assess_gate(matrix, ids, records, scope=scope)
            self.assertFalse(gate["requested_gate_passed"])
            self.assertIn("zero_discovered_tests", gate["reasons"])
            self.assertFalse(gate["phase1_m_complete"])

    def test_missing_scaffold_binding_fails(self) -> None:
        matrix, ids, records = self.synthetic_gate_inputs()
        matrix["engineering_requirements"][0]["test_bindings"] = []
        gate = assess_gate(matrix, ids, records, scope="scaffold")
        self.assertFalse(gate["requested_gate_passed"])
        self.assertIn("ENG-01", gate["missing_scaffold_requirements"])

    def test_missing_m_bindings_fail_final_gate(self) -> None:
        matrix, ids, records = self.synthetic_gate_inputs()
        matrix["vf_tests"][0]["scope_records"]["M"]["test_bindings"] = []
        step = assess_gate(matrix, ids, records, scope="scaffold")
        final = assess_gate(matrix, ids, records, scope="phase1")
        self.assertTrue(step["requested_gate_passed"])
        self.assertFalse(step["phase1_m_complete"])
        self.assertFalse(final["requested_gate_passed"])
        self.assertEqual(final["unresolved_m_family_ids"], ["VT-01"])

    def test_missing_trace_binding_fails_final_gate(self) -> None:
        matrix, ids, records = self.synthetic_gate_inputs()
        matrix["trace_requirements"][0]["test_bindings"] = []
        gate = assess_gate(matrix, ids, records, scope="phase1")
        self.assertFalse(gate["requested_gate_passed"])
        self.assertIn("TR-01", gate["unresolved_m_trace_report_ids"])

    def test_skipped_test_is_not_accepted(self) -> None:
        class SyntheticSkip(unittest.TestCase):
            def runTest(self) -> None:
                self.skipTest("synthetic runner check")
        ids, records, _ = execute_suite(unittest.TestSuite([SyntheticSkip()]))
        self.assertEqual(records[0]["outcome"], "skipped")
        gate = assess_gate(load_matrix(), ids, records, scope="scaffold")
        self.assertFalse(gate["requested_gate_passed"])

    def test_expected_failure_is_not_accepted(self) -> None:
        class SyntheticExpectedFailure(unittest.TestCase):
            @unittest.expectedFailure
            def runTest(self) -> None:
                self.fail("synthetic runner check")
        ids, records, _ = execute_suite(unittest.TestSuite([SyntheticExpectedFailure()]))
        self.assertEqual(records[0]["outcome"], "expected_failure")
        gate = assess_gate(load_matrix(), ids, records, scope="scaffold")
        self.assertFalse(gate["requested_gate_passed"])

    def test_failure_and_error_are_recorded(self) -> None:
        class SyntheticFailure(unittest.TestCase):
            def runTest(self) -> None:
                self.fail("synthetic assertion failure")
        class SyntheticError(unittest.TestCase):
            def runTest(self) -> None:
                raise ValueError("synthetic harness error")
        _, records, text = execute_suite(unittest.TestSuite([SyntheticFailure(), SyntheticError()]))
        self.assertEqual([r["outcome"] for r in records], ["failed", "error"])
        self.assertIn("synthetic assertion failure", text)
        self.assertTrue(all(r["elapsed_seconds"] >= 0 for r in records))

    def test_subtest_failure_is_recorded(self) -> None:
        class SyntheticSubTest(unittest.TestCase):
            def runTest(self) -> None:
                with self.subTest(part="intentional failure"):
                    self.assertEqual(1, 2)
        _, records, _ = execute_suite(unittest.TestSuite([SyntheticSubTest()]))
        self.assertEqual(records[0]["outcome"], "failed")
        self.assertTrue(records[0]["details"])

    def test_class_fixture_error_is_recorded(self) -> None:
        class SyntheticSetupError(unittest.TestCase):
            @classmethod
            def setUpClass(cls) -> None:
                raise RuntimeError("synthetic setup error")

            def test_unreachable(self) -> None:
                self.fail("This body must not execute after setup failure")

        suite = unittest.TestLoader().loadTestsFromTestCase(SyntheticSetupError)
        ids, records, text = execute_suite(suite)
        self.assertEqual(len(ids), 1)
        self.assertEqual(records[0]["outcome"], "error")
        self.assertEqual(records[0]["record_kind"], "fixture_error")
        self.assertIn("synthetic setup error", text)
        gate = assess_gate(load_matrix(), ids, records, scope="scaffold")
        self.assertFalse(gate["requested_gate_passed"])
        self.assertIn("discovery_and_execution_do_not_match", gate["reasons"])

    def test_unexpected_success_is_not_accepted(self) -> None:
        class SyntheticUnexpectedSuccess(unittest.TestCase):
            @unittest.expectedFailure
            def runTest(self) -> None:
                self.assertEqual(2 + 2, 4)
        ids, records, _ = execute_suite(unittest.TestSuite([SyntheticUnexpectedSuccess()]))
        self.assertEqual(records[0]["outcome"], "unexpected_success")
        gate = assess_gate(load_matrix(), ids, records, scope="scaffold")
        self.assertFalse(gate["requested_gate_passed"])

    def test_required_m_skip_blocks_final_gate(self) -> None:
        matrix, ids, records = self.synthetic_gate_inputs()
        skipped_id = "tests.synthetic_gate_fixture.skipped_M"
        matrix["vf_tests"][0]["scope_records"]["M"]["test_bindings"] = [skipped_id]
        ids.append(skipped_id)
        records.append({"test_id": skipped_id, "outcome": "skipped"})
        gate = assess_gate(matrix, ids, records, scope="phase1")
        self.assertFalse(gate["requested_gate_passed"])
        self.assertIn("VT-01", gate["unresolved_m_family_ids"])
        self.assertIn(skipped_id, gate["nonpassing_test_ids"])

    def test_duplicate_discovery_fails(self) -> None:
        matrix, ids, records = self.synthetic_gate_inputs()
        gate = assess_gate(matrix, ids + ids, records, scope="scaffold")
        self.assertFalse(gate["requested_gate_passed"])
        self.assertIn("duplicate_test_identity", gate["reasons"])

    def test_broken_binding_fails(self) -> None:
        matrix, ids, records = self.synthetic_gate_inputs()
        matrix["engineering_requirements"][0]["test_bindings"] = ["tests.absent.check"]
        gate = assess_gate(matrix, ids, records, scope="scaffold")
        self.assertFalse(gate["requested_gate_passed"])
        self.assertIn("tests.absent.check", gate["bad_scaffold_bindings"])

    def test_future_evidence_is_not_executed(self) -> None:
        matrix, ids, records = self.synthetic_gate_inputs()
        gate = assess_gate(matrix, ids, records, scope="phase1")
        self.assertTrue(gate["requested_gate_passed"])
        self.assertFalse(gate["empirical_validation_performed"])
        actual = {row["id"]: row for row in gate["family_results"]}
        self.assertEqual(actual["VT-47"]["scopes"]["E"]["execution_status"], "not_run")
        self.assertEqual(actual["VT-51"]["scopes"]["D"]["execution_status"], "not_run")

    def test_journal_retains_prior_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            append_journal(path, {"run_id": "synthetic-1", "console_output": "first\n", "exit_code": 1})
            append_journal(path, {"run_id": "synthetic-2", "console_output": "second\n", "exit_code": 0})
            actual = json.loads((path / "test_results.json").read_text(encoding="utf-8"))
            self.assertEqual([r["run_id"] for r in actual["runs"]], ["synthetic-1", "synthetic-2"])
            text = (path / "test_output.txt").read_text(encoding="utf-8")
            self.assertIn("first", text)
            self.assertIn("second", text)
            with self.assertRaises(ValueError):
                append_journal(path, {"run_id": "synthetic-2", "console_output": "duplicate"})

    def test_corrupt_journal_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            journal = path / "test_results.json"
            journal.write_bytes(b"not valid JSON")
            with self.assertRaises(ValueError):
                append_journal(path, {"run_id": "synthetic", "console_output": "test"})
            self.assertEqual(journal.read_bytes(), b"not valid JSON")

    def test_runner_help_does_not_run_tests(self) -> None:
        paths = [ROOT / "artifacts" / "phase1" / name for name in ("test_results.json", "test_output.txt")]
        before = [path.read_bytes() if path.exists() else None for path in paths]
        result = run_trusted_case("runner_help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--scope", result.stdout)
        after = [path.read_bytes() if path.exists() else None for path in paths]
        self.assertEqual(before, after)
        self.assertNotIn("Ran ", result.stdout)


if __name__ == "__main__":
    unittest.main()
