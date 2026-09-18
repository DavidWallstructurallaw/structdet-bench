#!/usr/bin/env python3
"""Run trusted complete discovery and assess Phase 2 stage/V acceptance.

This runner imports the unchanged Phase 1 M gate. It never calls a provider,
executes submitted programs, mutates Phase 1 QA history or performs E activities.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
from typing import Any
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests import phase2_helpers as helpers
from tools import run_phase1_checks as prior


def _obligation(row: dict[str, Any], actual: dict[str, str]) -> dict[str, Any]:
    bindings = row.get("test_bindings", [])
    bad = [name for name in bindings if actual.get(name) != "passed"]
    okay = row.get("implementation_status") == "implemented" and bool(bindings) and not bad
    return {"id": row["id"], "implementation_status": row["implementation_status"],
            "execution_status": "passed" if okay else "not_run" if not bindings else "not_passed",
            "test_bindings": bindings, "missing_or_nonpassing_bindings": bad,
            "required_by_step": row["required_by_step"], "substantive_validation_performed": False}


def assess_gate(matrix: dict[str, Any], discovered: list[str], records: list[dict[str, Any]], *,
                scope: str, predecessor_gate: dict[str, Any], reconciliation: Any,
                matrix_errors: list[str] | None = None,
                pin_failures: list[str] | None = None) -> dict[str, Any]:
    """Only executed, unique, passing methods count. A stage is not full V."""
    if scope not in {"current", "phase2"}:
        raise ValueError("unknown_phase2_gate_scope")
    reasons = list(matrix_errors or ()) + list(pin_failures or ())
    ids = Counter(discovered)
    actual = {row["test_id"]: row["outcome"] for row in records}
    if not discovered:
        reasons.append("zero_discovered_tests")
    if any(n != 1 for n in ids.values()) or len(actual) != len(records):
        reasons.append("duplicate_test_identity")
    if set(discovered) != set(actual):
        reasons.append("discovery_and_execution_do_not_match")
    if any(outcome != "passed" for outcome in actual.values()):
        reasons.append("executed_tests_not_passed")
    missing_prior = [name for name in matrix["predecessor"]["test_ids"] if actual.get(name) != "passed"]
    if missing_prior:
        reasons.append("missing_or_nonpassing_predecessor_tests")
    m_ok = predecessor_gate.get("requested_gate_passed") is True and predecessor_gate.get("phase1_m_complete") is True
    if not m_ok:
        reasons.append("predecessor_M_gate_not_passed")
    remote_errors = helpers.reconciliation_checks(reconciliation, matrix["predecessor"]["file_manifest"])
    step = matrix["delivery"]["step"]
    requirement_results = {}
    current_unfinished = []; all_unfinished = []
    for group in ("vt_obligations", "trace_requirements", "report_groups", "ec_requirements", "engineering_requirements"):
        results = [_obligation(row, actual) for row in matrix[group]]
        requirement_results[group] = results
        for row in results:
            if row["execution_status"] != "passed":
                all_unfinished.append(row["id"])
                if row["required_by_step"] <= step:
                    current_unfinished.append(row["id"])
    stage_errors = []
    for number in range(1, step + 1):
        row = matrix["stage_bindings"][str(number)]
        if row["implementation_status"] != "implemented" or not row["test_bindings"] or any(actual.get(x) != "passed" for x in row["test_bindings"]):
            stage_errors.append(f"stage_{number}_not_verified")
    harness_passed = not reasons and not current_unfinished and not stage_errors
    final_v_complete = not reasons and not all_unfinished and step >= 7 and not stage_errors
    if current_unfinished:
        reasons.append("current_stage_requirements_incomplete")
    reasons.extend(stage_errors)
    if scope == "phase2":
        if all_unfinished:
            reasons.append("full_V_or_engineering_requirements_incomplete")
        if step < 7:
            reasons.append("integrated_V_verification_not_reached")
    reasons.extend(remote_errors)
    return {
        "requested_scope": scope, "requested_gate_passed": not reasons,
        "phase2_step": step, "harness_checks_passed": harness_passed,
        "phase1_m_complete": m_ok, "phase2_v_complete": final_v_complete and not remote_errors,
        "repository_delivery_complete": not remote_errors,
        "reasons": sorted(set(reasons)), "discovered_count": len(discovered),
        "outcome_counts": dict(sorted(Counter(row["outcome"] for row in records).items())),
        "missing_or_nonpassing_predecessor_tests": missing_prior,
        "unresolved_current_ids": sorted(current_unfinished),
        "unresolved_v_ids": [row["id"] for row in requirement_results["vt_obligations"] if row["execution_status"] != "passed"],
        "unresolved_full_ids": sorted(all_unfinished), "requirements": requirement_results,
        "empirical_validation_performed": False,
        "final_owner_acceptance": "not_established_by_software_tests",
    }


def annotated_results(matrix: dict[str, Any], records: list[dict[str, Any]],
                      phase1_matrix: dict[str, Any]) -> list[dict[str, Any]]:
    base = prior.annotate_results(phase1_matrix, records)
    links = {}
    for group in ("vt_obligations", "trace_requirements", "report_groups", "ec_requirements", "engineering_requirements"):
        for row in matrix[group]:
            suffix = "ENG" if group == "engineering_requirements" else "V_software"
            for name in row["test_bindings"]:
                links.setdefault(name, set()).add(row["id"] + "/" + suffix)
    for record in base:
        name = record["test_id"]
        record["phase2_requirement_bindings"] = sorted(links.get(name, ()))
        record["expected_outcome"] = "passed"
        record["actual_outcome"] = record["outcome"]
        record["configuration_refs"] = ["tests/phase2_matrix.json", "PHASE_2_PLAN.md"]
        record["source_and_oracle_manifest_ref"] = "file_fingerprints"
        record["tolerance"] = {"absolute": 1e-12, "relative": 1e-10,
                               "scope": "noninteger numerical assertions only; identities and counts exact"}
    return base


def _entry_hash(record: dict[str, Any]) -> str:
    return helpers.sha256_bytes(helpers.canonical_bytes({k: v for k, v in record.items() if k != "record_sha256"}))


def _text(runs: list[dict[str, Any]]) -> bytes:
    return "".join(f"=== {r['run_id']} ===\n{r['console_output']}\n" for r in runs).encode("utf-8")


def append_journal(directory: Path, run: dict[str, Any]) -> None:
    """Append hash-chained runs; edited, corrupt or missing history fails closed.

    Two-file publication is not an OS-atomic transaction. A interrupted replace
    is detected on the next invocation; no damaged history is silently repaired.
    """
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "test_results.json"; text = directory / "test_output.txt"
    if directory.is_symlink() or path.is_symlink() or text.is_symlink():
        raise ValueError("qa_history_symlink")
    if path.exists() != text.exists():
        raise ValueError("qa_history_pair_incomplete")
    journal = helpers.read_json(path) if path.exists() else {"schema_version": "0.1", "phase": 2, "runs": []}
    if (not isinstance(journal, dict) or set(journal) != {"schema_version", "phase", "runs"}
            or journal["schema_version"] != "0.1" or journal["phase"] != 2 or not isinstance(journal["runs"], list)):
        raise ValueError("invalid_qa_history")
    previous = None; seen = set()
    for old in journal["runs"]:
        if (not isinstance(old, dict) or not isinstance(old.get("run_id"), str)
                or not isinstance(old.get("console_output"), str) or old["run_id"] in seen
                or old.get("previous_record_sha256") != previous or old.get("record_sha256") != _entry_hash(old)):
            raise ValueError("qa_history_chain_invalid")
        previous = old["record_sha256"]; seen.add(old["run_id"])
    if text.exists() and text.read_bytes() != _text(journal["runs"]):
        raise ValueError("qa_console_history_changed")
    if not isinstance(run.get("run_id"), str) or not isinstance(run.get("console_output"), str) or run["run_id"] in seen:
        raise ValueError("invalid_or_duplicate_run_id")
    item = dict(run, previous_record_sha256=previous)
    item["record_sha256"] = _entry_hash(item)
    output = {**journal, "runs": journal["runs"] + [item]}
    staged = []
    try:
        for target, content in ((text, _text(output["runs"])), (path, helpers.canonical_bytes(output))):
            with tempfile.NamedTemporaryFile(dir=directory, delete=False) as handle:
                # Register the temporary path before any operation that can fail.
                staged.append((Path(handle.name), target))
                os.chmod(handle.name, 0o600); handle.write(content); handle.flush(); os.fsync(handle.fileno())
        for source, target in staged:
            os.replace(source, target)
    finally:
        for source, _ in staged:
            source.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--scope", choices=("current", "phase2"), default="phase2")
    args = parser.parse_args(argv)
    try:
        matrix = helpers.read_matrix()
        errors = helpers.validate_matrix(matrix)
        if errors:
            sys.stderr.write("Invalid Phase 2 verification matrix: " + ", ".join(errors) + "\n")
            return 2
        identities = helpers.identity_checks(matrix)
        p1 = helpers.load_phase1_matrix()
        p1_errors = prior.validate_matrix(p1)
        p1_errors += [x["path"] for x in prior.baseline_checks(p1) if x["status"] != "passed"]
        reconciliation_path = ROOT / "artifacts/phase2/baseline_reconciliation.json"
        reconciliation = helpers.read_json(reconciliation_path) if reconciliation_path.exists() else None
        suite = unittest.TestLoader().discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
        discovered, outcomes, console = prior.execute_suite(suite)
        p1_gate = prior.assess_gate(p1, discovered, outcomes, scope="phase1", identity_errors=p1_errors)
        result = assess_gate(matrix, discovered, outcomes, scope=args.scope, predecessor_gate=p1_gate,
                             reconciliation=reconciliation, matrix_errors=errors,
                             pin_failures=[x["path"] + ":baseline_mismatch" for x in identities if x["status"] != "passed"])
        exit_code = 0 if result["requested_gate_passed"] else 1
        summary = (f"\nRequested Phase 2 scope: {args.scope}\n"
                   f"Harness checks passed: {result['harness_checks_passed']}\n"
                   f"Predecessor M gate passed: {result['phase1_m_complete']}\n"
                   f"Repository delivery complete: {result['repository_delivery_complete']}\n"
                   f"Full V complete: {result['phase2_v_complete']}\n"
                   f"Unimplemented V obligations: {len(result['unresolved_v_ids'])}\n"
                   f"Gate reasons: {', '.join(result['reasons']) or 'none'}\nRunner exit code: {exit_code}\n")
        files = {p.relative_to(ROOT).as_posix(): helpers.sha256_bytes(p.read_bytes()) for p in ROOT.rglob("*")
                 if p.is_file() and not p.is_symlink() and "artifacts" not in p.relative_to(ROOT).parts
                 and "__pycache__" not in p.parts and ".git" not in p.parts}
        run = {"run_id": str(uuid.uuid4()), "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
               "execution_phase": 2, "implementation_step": matrix["delivery"]["step"],
               "command": [sys.executable, "tools/run_phase2_checks.py", "--scope", args.scope],
               "exit_code": exit_code, "authorization": matrix["delivery"]["authorization"],
               "environment": {"python": sys.version, "platform": platform.platform(),
                               "no_site": bool(sys.flags.no_site), "bytecode_disabled": bool(sys.dont_write_bytecode)},
               "source_and_fixture_role": "software_record_and_fixture_tests_only",
               "file_fingerprints": files, "baseline_verification": identities,
               "discovered_test_ids": discovered, "test_results": annotated_results(matrix, outcomes, p1),
               "predecessor_M_acceptance": p1_gate, "acceptance": result,
               "console_output": console + summary, "empirical_validation_performed": False,
               "model_calls": 0, "candidate_programs_executed": 0}
        append_journal(ROOT / "artifacts/phase2", run)
        sys.stdout.write(console + summary)
        return exit_code
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        sys.stderr.write("Phase 2 verification failed: invalid input, identity or QA history; no success claimed.\n")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
