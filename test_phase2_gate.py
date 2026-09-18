"""Phase 2 Step 1 gate tests; synthetic gates are explicitly software fixtures.

No test below supplies empirical evidence or an actual remote read-back. The
actual preflight record is assessed separately by the command-line runner.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tests import phase2_helpers as h
from tools import run_phase2_checks as runner


def synthetic_inputs():
    """Unit-test inputs to gate logic, not executed-run/publication evidence."""
    matrix = h.read_matrix()
    ids = matrix["predecessor"]["test_ids"] + matrix["stage_bindings"]["1"]["test_bindings"]
    records = [{"test_id": name, "outcome": "passed"} for name in ids]
    remote = {"repository": "DavidWallstructurallaw/structdet-bench", "archive_sha256": h.ARCHIVE_SHA256,
              "project_inventory_sha256": h.INVENTORY_SHA256, "scope": "all_67_original_project_files",
              "status": "remote_verified", "accepted_phase1_commit": "1" * 40, "readback_complete": True,
              "remote_files": copy.deepcopy(matrix["predecessor"]["file_manifest"]),
              "fixture_only": True}
    return matrix, ids, records, {"requested_gate_passed": True, "phase1_m_complete": True}, remote


def gate(scope="current", edit=None):
    matrix, ids, records, previous, remote = synthetic_inputs()
    if edit:
        edit(matrix, ids, records, previous, remote)
    return runner.assess_gate(matrix, ids, records, scope=scope, predecessor_gate=previous, reconciliation=remote)


class CatalogueTests(unittest.TestCase):
    def test_matrix_preserves_source_catalogues_and_all_26_v_obligations(self):
        matrix = h.read_matrix()
        self.assertEqual(h.validate_matrix(matrix), [])
        self.assertEqual(matrix["catalogues"], h.expected_catalogues())
        self.assertEqual([e["id"] for e in matrix["vt_obligations"]], list(h.V_IDS))
        self.assertEqual([len(matrix["catalogues"][g]) for g in ("vt", "tr", "rf")], [54, 40, 36])
        self.assertEqual(len(matrix["ec_requirements"]), 8)

    def test_original_503_methods_and_matrix_are_preserved(self):
        m = h.read_matrix()
        self.assertEqual(len(m["predecessor"]["test_ids"]), 503)
        self.assertEqual(h.sha256_bytes((h.ROOT / "tests/phase1_matrix.json").read_bytes()), h.PHASE1_MATRIX_SHA256)
        self.assertEqual(h.load_phase1_matrix()["current_step"], 7)
        self.assertEqual(m["delivery"]["phase"], 2)

    def test_current_inherited_file_identities_match(self):
        checks = h.identity_checks(h.read_matrix())
        self.assertTrue(checks)
        self.assertTrue(all(x["status"] == "passed" for x in checks))
        self.assertIn("PHASE_2_PLAN.md", [x["path"] for x in checks])

    def test_wrong_source_row_or_scope_is_rejected(self):
        m = h.read_matrix(); m["catalogues"]["vt"][0]["source_row_sha256"] = "0" * 64
        self.assertIn("catalogue_differs_from_pinned_source", h.validate_matrix(m))
        m = h.read_matrix(); m["catalogues"]["vt"][46]["evidence_status"] = "verified"
        self.assertIn("catalogue_differs_from_pinned_source", h.validate_matrix(m))

    def test_missing_duplicate_and_renamed_v_requirements_are_rejected(self):
        for mutation in (lambda rows: rows.pop(), lambda rows: rows.append(copy.deepcopy(rows[0])),
                         lambda rows: rows[0].update(id="VT-99")):
            m = h.read_matrix(); mutation(m["vt_obligations"])
            self.assertIn("vt_obligations:identity_set_changed", h.validate_matrix(m))

    def test_bad_or_duplicate_binding_lists_are_rejected(self):
        for bindings in (None, "test", ["not a method"], ["tests.test_phase2_gate.GateTests.test_stage_pass_is_separate_from_full_v"] * 2):
            m = h.read_matrix(); m["engineering_requirements"][0]["test_bindings"] = bindings
            self.assertTrue(h.validate_matrix(m))

    def test_implemented_without_real_bindings_is_rejected(self):
        m = h.read_matrix(); m["vt_obligations"][0]["implementation_status"] = "implemented"
        self.assertIn("VT-03:empty_bindings", h.validate_matrix(m))

    def test_E_and_D_cannot_be_promoted(self):
        for field, value in (("evidence_status", "validated"), ("deferred_status", "implemented")):
            m = h.read_matrix(); m[field] = value
            self.assertIn("empirical_or_deferred_scope_changed", h.validate_matrix(m))
        m = h.read_matrix(); m["ec_requirements"][0]["evidence_status"] = "satisfied"
        self.assertTrue(h.validate_matrix(m))

    def test_missing_or_changed_predecessor_method_is_rejected(self):
        m = h.read_matrix(); m["predecessor"]["test_ids"].pop()
        self.assertIn("predecessor_test_id_inventory_changed", h.validate_matrix(m))

    def test_approved_plan_change_is_rejected(self):
        m = h.read_matrix(); m["approved_plan"]["sha256"] = "0" * 64
        self.assertIn("approved_plan_identity", h.validate_matrix(m))

    def test_nonobject_or_unknown_matrix_version_is_controlled(self):
        for value in (None, [], False, "matrix"):
            self.assertEqual(h.validate_matrix(value), ["phase2_matrix_not_object"])
        m = h.read_matrix(); m["schema_version"] = "9"
        self.assertIn("phase2_matrix_identity", h.validate_matrix(m))

    def test_json_duplicate_keys_and_nonfinite_are_refused(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "m.json"
            for b in (b'{"a":1,"a":2}', b'{"a":NaN}', b'[] trailing'):
                p.write_bytes(b)
                with self.assertRaises(ValueError): h.read_json(p)

    def test_no_new_comparison_runtime_module_exists_in_step1(self):
        current = h.read_matrix()["delivery"]
        if current["step"] == 1:
            for name in ("comparison_records", "text_diagnostics", "comparisons", "uncertainty", "predictions", "comparison_pipeline"):
                self.assertFalse((h.ROOT / "structdet_bench" / (name + ".py")).exists())
            self.assertEqual(current["authorization"]["owner_instruction"], "批准，开始")
        else:
            first = [x for x in current.get("history", []) if x["step"] == 1]
            self.assertEqual(len(first), 1)
            self.assertEqual(first[0]["authorization"]["owner_instruction"], "批准，开始")
        for name in ("generate", "train", "execute", "judge", "recover"):
            self.assertFalse((h.ROOT / "structdet_bench" / (name + ".py")).exists())


class GateTests(unittest.TestCase):
    def test_stage_pass_is_separate_from_full_v(self):
        current = gate(); full = gate("phase2")
        self.assertTrue(current["requested_gate_passed"])
        self.assertTrue(current["harness_checks_passed"])
        self.assertFalse(current["phase2_v_complete"])
        self.assertFalse(full["requested_gate_passed"])
        self.assertEqual(full["unresolved_v_ids"], list(h.V_IDS))

    def test_empty_discovery_fails_both_scopes(self):
        for scope in ("current", "phase2"):
            out = gate(scope, lambda m, ids, rows, p, r: (ids.clear(), rows.clear()))
            self.assertFalse(out["requested_gate_passed"])
            self.assertIn("zero_discovered_tests", out["reasons"])

    def test_duplicate_discovery_or_execution_fails(self):
        for edit in (lambda m, ids, rows, p, r: ids.append(ids[0]),
                     lambda m, ids, rows, p, r: rows.append(copy.deepcopy(rows[0]))):
            out = gate(edit=edit)
            self.assertIn("duplicate_test_identity", out["reasons"])
            self.assertFalse(out["requested_gate_passed"])

    def test_unexecuted_discovered_test_is_not_a_pass(self):
        out = gate(edit=lambda m, ids, rows, p, r: rows.pop())
        self.assertIn("discovery_and_execution_do_not_match", out["reasons"])

    def test_extra_execution_record_is_rejected(self):
        out = gate(edit=lambda m, ids, rows, p, r: rows.append({"test_id": "extra", "outcome": "passed"}))
        self.assertIn("discovery_and_execution_do_not_match", out["reasons"])

    def test_failure_error_skip_expected_failure_and_unexpected_success_fail(self):
        for status in ("failed", "error", "skipped", "expected_failure", "unexpected_success", "not_completed"):
            out = gate(edit=lambda m, ids, rows, p, r: rows[-1].update(outcome=status))
            self.assertFalse(out["requested_gate_passed"], status)
            self.assertIn("executed_tests_not_passed", out["reasons"])

    def test_missing_predecessor_test_fails_even_with_nominal_M_pass(self):
        out = gate(edit=lambda m, ids, rows, p, r: (ids.pop(0), rows.pop(0)))
        self.assertIn("missing_or_nonpassing_predecessor_tests", out["reasons"])

    def test_M_gate_failure_blocks_both_scopes(self):
        for scope in ("current", "phase2"):
            out = gate(scope, lambda m, ids, rows, p, r: p.update(phase1_m_complete=False))
            self.assertIn("predecessor_M_gate_not_passed", out["reasons"])
            self.assertFalse(out["requested_gate_passed"])

    def test_missing_stage_binding_fails_current_acceptance(self):
        out = gate(edit=lambda m, ids, rows, p, r: m["stage_bindings"]["1"]["test_bindings"].clear())
        self.assertIn("stage_1_not_verified", out["reasons"])

    def test_binding_to_unrun_method_fails(self):
        out = gate(edit=lambda m, ids, rows, p, r: m["engineering_requirements"][0].update(test_bindings=["tests.test_absent.Missing.test_missing"]))
        self.assertIn("current_stage_requirements_incomplete", out["reasons"])
        self.assertFalse(out["harness_checks_passed"])

    def test_partial_implementation_does_not_count_as_complete(self):
        out = gate(edit=lambda m, ids, rows, p, r: m["engineering_requirements"][0].update(implementation_status="partial"))
        self.assertFalse(out["requested_gate_passed"])

    def test_passed_harness_cannot_hide_pending_remote_baseline(self):
        out = gate(edit=lambda m, ids, rows, p, r: r.update(status="pending", accepted_phase1_commit=None, readback_complete=False))
        self.assertTrue(out["harness_checks_passed"])
        self.assertTrue(out["phase1_m_complete"])
        self.assertFalse(out["requested_gate_passed"])
        self.assertIn("phase1_remote_sync_pending", out["reasons"])

    def test_partial_remote_file_inventory_cannot_pass(self):
        out = gate(edit=lambda m, ids, rows, p, r: r["remote_files"].pop("tests/phase1_matrix.json"))
        self.assertIn("remote_original_file_inventory_not_matched", out["reasons"])

    def test_blob_creation_is_not_branch_publication(self):
        out = gate(edit=lambda m, ids, rows, p, r: r.update(status="blobs_created", accepted_phase1_commit=None))
        self.assertFalse(out["repository_delivery_complete"])

    def test_wrong_repository_or_baseline_is_rejected(self):
        for key, value in (("repository", "other/repo"), ("archive_sha256", "0" * 64), ("project_inventory_sha256", "0" * 64)):
            out = gate(edit=lambda m, ids, rows, p, r: r.update({key: value}))
            self.assertFalse(out["requested_gate_passed"])

    def test_unknown_gate_scope_fails_explicitly(self):
        with self.assertRaises(ValueError): gate("anything")

    def test_pin_failure_blocks_acceptance(self):
        m, ids, rows, p, r = synthetic_inputs()
        out = runner.assess_gate(m, ids, rows, scope="current", predecessor_gate=p, reconciliation=r,
                                 pin_failures=["frozen_file_changed"])
        self.assertIn("frozen_file_changed", out["reasons"])

    def test_records_never_certify_E_or_owner_acceptance(self):
        result = gate()
        self.assertFalse(result["empirical_validation_performed"])
        self.assertEqual(result["final_owner_acceptance"], "not_established_by_software_tests")
        self.assertTrue(all(not r["substantive_validation_performed"] for rows in result["requirements"].values() for r in rows))

    def test_preflight_state_is_retained_without_assuming_sync(self):
        path = h.ROOT / "artifacts/phase2/baseline_reconciliation.json"
        record = h.read_json(path)
        errors = h.reconciliation_checks(record, h.read_matrix()["predecessor"]["file_manifest"])
        if record["status"] == "pending":
            self.assertIn("phase1_remote_sync_pending", errors)
        else:
            self.assertEqual(errors, [])


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(); self.addCleanup(self.temp.cleanup); self.directory = Path(self.temp.name)

    def run_record(self, name="run-1"):
        return {"run_id": name, "console_output": "Actual mock recorder fixture\n", "test_results": [], "fixture_only": True}

    def test_two_runs_retain_first_record_and_chain(self):
        runner.append_journal(self.directory, self.run_record())
        old = h.read_json(self.directory / "test_results.json")["runs"][0]
        runner.append_journal(self.directory, self.run_record("run-2"))
        data = h.read_json(self.directory / "test_results.json")
        self.assertEqual(data["runs"][0], old)
        self.assertEqual(data["runs"][1]["previous_record_sha256"], old["record_sha256"])
        self.assertEqual(len(data["runs"]), 2)

    def test_duplicate_run_refused_without_modifying_files(self):
        runner.append_journal(self.directory, self.run_record())
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        with self.assertRaises(ValueError): runner.append_journal(self.directory, self.run_record())
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_corrupt_json_is_not_overwritten(self):
        runner.append_journal(self.directory, self.run_record())
        p = self.directory / "test_results.json"; p.write_bytes(b'broken')
        with self.assertRaises(ValueError): runner.append_journal(self.directory, self.run_record("next"))
        self.assertEqual(p.read_bytes(), b'broken')

    def test_changed_old_result_breaks_chain(self):
        runner.append_journal(self.directory, self.run_record())
        p = self.directory / "test_results.json"; data = h.read_json(p)
        data["runs"][0]["console_output"] = "rewritten success"
        p.write_bytes(h.canonical_bytes(data))
        with self.assertRaises(ValueError): runner.append_journal(self.directory, self.run_record("next"))

    def test_changed_or_missing_console_fails_closed(self):
        runner.append_journal(self.directory, self.run_record())
        p = self.directory / "test_output.txt"; p.write_bytes(b"rewritten")
        with self.assertRaises(ValueError): runner.append_journal(self.directory, self.run_record("next"))
        p.unlink()
        with self.assertRaises(ValueError): runner.append_journal(self.directory, self.run_record("next"))

    def test_missing_journal_with_existing_console_is_not_reset(self):
        (self.directory / "test_output.txt").write_bytes(b"prior")
        with self.assertRaises(ValueError): runner.append_journal(self.directory, self.run_record())
        self.assertEqual((self.directory / "test_output.txt").read_bytes(), b"prior")

    def test_symlink_history_is_not_followed(self):
        outside = self.directory / "outside"; outside.write_bytes(b"unchanged")
        (self.directory / "test_results.json").symlink_to(outside)
        with self.assertRaises(ValueError): runner.append_journal(self.directory, self.run_record())
        self.assertEqual(outside.read_bytes(), b"unchanged")

    def test_nonfinite_new_run_has_no_written_capture(self):
        r = self.run_record(); r["value"] = float("nan")
        with self.assertRaises(ValueError): runner.append_journal(self.directory, r)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_write_failure_preserves_existing_history(self):
        runner.append_journal(self.directory, self.run_record())
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        with patch.object(runner.os, "fsync", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError): runner.append_journal(self.directory, self.run_record("next"))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})


class RecorderTests(unittest.TestCase):
    def test_failure_and_skip_results_are_actual_recorder_states(self):
        class Recorded(unittest.TestCase):
            def test_fail(self): self.fail("fixture failure")
            @unittest.skip("fixture skip")
            def test_skip(self): pass
            @unittest.expectedFailure
            def test_expected(self): self.fail("fixture expected")
        ids, records, console = runner.prior.execute_suite(unittest.defaultTestLoader.loadTestsFromTestCase(Recorded))
        self.assertEqual(len(ids), 3)
        self.assertEqual({r["outcome"] for r in records}, {"failed", "skipped", "expected_failure"})
        self.assertIn("fixture failure", console)

    def test_setup_error_is_retained_even_without_test_start(self):
        class Broken(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise RuntimeError("setup fixture")
            def test_unused(self): pass
        ids, records, _ = runner.prior.execute_suite(unittest.defaultTestLoader.loadTestsFromTestCase(Broken))
        self.assertEqual(len(ids), 1)
        self.assertEqual(records[0]["outcome"], "error")
        self.assertEqual(records[0]["record_kind"], "fixture_error")

    def test_annotation_records_scope_oracle_and_expected_actual(self):
        m = h.read_matrix(); p = h.load_phase1_matrix(); name = m["stage_bindings"]["1"]["test_bindings"][0]
        records = runner.annotated_results(m, [{"test_id": name, "outcome": "passed"}], p)
        row = records[0]
        self.assertEqual(row["expected_outcome"], row["actual_outcome"])
        self.assertFalse(row["substantive_validation_performed"])
        self.assertIn("tests/phase2_matrix.json", row["configuration_refs"])
        self.assertEqual(row["source_and_oracle_manifest_ref"], "file_fingerprints")

    def test_help_does_not_discover_or_execute_tests(self):
        with patch.object(runner.prior, "execute_suite", side_effect=AssertionError("unexpected execution")):
            with self.assertRaises(SystemExit) as exit:
                runner.main(["--help"])
        self.assertEqual(exit.exception.code, 0)

    def test_gate_evaluation_performs_no_network_process_or_input_execution(self):
        args = synthetic_inputs()
        with patch("socket.socket", side_effect=AssertionError("network")), \
             patch("subprocess.Popen", side_effect=AssertionError("process")), \
             patch("builtins.eval", side_effect=AssertionError("eval")):
            out = runner.assess_gate(args[0], args[1], args[2], scope="current", predecessor_gate=args[3], reconciliation=args[4])
        self.assertTrue(out["harness_checks_passed"])

    def test_no_production_imports_from_phase2_test_helpers(self):
        for p in (h.ROOT / "structdet_bench").glob("*.py"):
            self.assertNotIn("phase2_helpers", p.read_text())
            self.assertNotIn("run_phase2_checks", p.read_text())
