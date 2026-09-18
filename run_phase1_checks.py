#!/usr/bin/env python3
"""Trusted local QA runner. Default acceptance requires the complete M scope.

Use --scope scaffold to assess Step 1 only. Neither mode implements a later
step, runs a model, executes candidate programs, or supplies external evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import re
import sys
import tempfile
import time
from typing import Any
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.helpers import baseline_checks, load_matrix, sha256_file, source_table


class RecordingResult(unittest.TextTestResult):
    """Retain individual outcomes, including skips and expected failures."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.records: list[dict[str, Any]] = []
        self._active: dict[str, dict[str, Any]] = {}

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self._active[test.id()] = {
            "test_id": test.id(),
            "outcome": "not_completed",
            "elapsed_seconds": None,
            "details": [],
            "_start": time.perf_counter(),
        }

    def _mark(self, test: unittest.TestCase, outcome: str, detail: str = "") -> None:
        item = self._active.get(test.id())
        if item is None:
            # unittest reports class/module setup and teardown failures through
            # an ErrorHolder that receives no startTest/stopTest pair.
            self.records.append({
                "test_id": test.id(),
                "outcome": outcome,
                "elapsed_seconds": 0.0,
                "details": [detail] if detail else [],
                "record_kind": "fixture_error",
            })
            return
        item["outcome"] = outcome
        if detail:
            item["details"].append(detail)

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self._mark(test, "passed")

    def addFailure(self, test: unittest.TestCase, err: Any) -> None:
        super().addFailure(test, err)
        self._mark(test, "failed", self._exc_info_to_string(err, test))

    def addError(self, test: unittest.TestCase, err: Any) -> None:
        super().addError(test, err)
        self._mark(test, "error", self._exc_info_to_string(err, test))

    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self._mark(test, "skipped", reason)

    def addExpectedFailure(self, test: unittest.TestCase, err: Any) -> None:
        super().addExpectedFailure(test, err)
        self._mark(test, "expected_failure", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self._mark(test, "unexpected_success")

    def addSubTest(self, test: unittest.TestCase, subtest: Any, err: Any) -> None:
        super().addSubTest(test, subtest, err)
        if err is not None:
            self._mark(test, "failed", self._exc_info_to_string(err, test))

    def stopTest(self, test: unittest.TestCase) -> None:
        item = self._active.pop(test.id())
        item["elapsed_seconds"] = time.perf_counter() - item.pop("_start")
        self.records.append(item)
        super().stopTest(test)


def flatten(suite: unittest.TestSuite) -> list[str]:
    ids: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            ids.extend(flatten(item))
        else:
            ids.append(item.id())
    return ids


def execute_suite(suite: unittest.TestSuite) -> tuple[list[str], list[dict[str, Any]], str]:
    ids = flatten(suite)
    stream = io.StringIO()
    result = unittest.TextTestRunner(
        stream=stream, verbosity=2, resultclass=RecordingResult
    ).run(suite)
    return ids, result.records, stream.getvalue()


def validate_matrix(matrix: dict[str, Any]) -> list[str]:
    """Validate the checked-in applicability map, without running E work."""
    errors: list[str] = []
    if matrix.get("schema_version") != "0.1":
        errors.append("Unsupported QA matrix schema")
    for field, prefix, count in (
        ("vf_tests", "VT", 54),
        ("trace_requirements", "TR", 40),
        ("report_groups", "RF", 36),
    ):
        items = matrix.get(field, [])
        ids = [entry.get("id") for entry in items]
        if sorted(ids) != [f"{prefix}-{n:02}" for n in range(1, count + 1)]:
            errors.append(f"{field}: missing, duplicated, or unexpected identities")
    expected_m = {row[0] for row in source_table("PHASE_1_PLAN.md", "VT")}
    actual_m = {entry["id"] for entry in matrix["vf_tests"] if entry["m_required"] is True}
    if expected_m != actual_m or len(expected_m) != 37:
        errors.append("M applicability differs from PHASE_1_PLAN section 8.1")
    source_vt = {r[0]: r for r in source_table("VALIDATION_AND_FALSIFICATION.md", "VT")}
    vt_ids = set(source_vt)
    tr_ids = {e["id"] for e in matrix["trace_requirements"]}
    rf_ids = {e["id"] for e in matrix["report_groups"]}
    for entry in matrix["vf_tests"]:
        original = source_vt.get(entry["id"])
        if original is None:
            continue
        tags = set(re.findall(r"\b[MVED]\b", original[1]))
        if set(entry["scope_records"]) != tags:
            errors.append(f"{entry['id']}: scope tags changed")
        if not set(entry["trace_ids"]) <= tr_ids or not set(entry["report_groups"]) <= rf_ids:
            errors.append(f"{entry['id']}: unresolved trace/report link")
        for tag, record in entry["scope_records"].items():
            bindings = record.get("test_bindings", [])
            if tag != "M" and bindings:
                errors.append(f"{entry['id']}/{tag}: outside-scope executable binding")
            if tag == "M" and any("test_scaffold." in name for name in bindings):
                errors.append(f"{entry['id']}: scaffold check cannot fulfill an M family")
            if not isinstance(bindings, list) or any(not isinstance(x, str) for x in bindings):
                errors.append(f"{entry['id']}/{tag}: malformed bindings")
    for entry in matrix["trace_requirements"]:
        expected = bool(set(entry["vf_ids"]) & expected_m)
        if entry["m_applicable"] is not expected:
            errors.append(f"{entry['id']}: wrong M applicability")
        if not set(entry["vf_ids"]) <= vt_ids or not set(entry["report_groups"]) <= rf_ids:
            errors.append(f"{entry['id']}: unresolved VF/report link")
    for entry in matrix["report_groups"]:
        number = int(entry["id"].split("-")[1])
        if entry["m_applicable"] is not (number <= 20 or number >= 29):
            errors.append(f"{entry['id']}: wrong M applicability")
        if not set(entry["vf_ids"]) <= vt_ids or not set(entry["trace_ids"]) <= tr_ids:
            errors.append(f"{entry['id']}: unresolved VF/trace link")
    if {e["id"] for e in matrix["engineering_requirements"]} != {
        f"ENG-{n:02}" for n in range(1, 6)
    }:
        errors.append("Scaffold acceptance requirements missing or renamed")
    if len(matrix.get("baseline", [])) != 12:
        errors.append("Expected eleven Phase 0 files and one execution plan")
    if matrix.get("current_step", 0) >= 7:
        supplement = matrix.get("step7_acceptance", {}).get("evidence_checks", {})
        if not isinstance(supplement, dict) or set(supplement) != {f"EC-C{i:02d}" for i in range(1,9)}:
            errors.append("EC-001 M record checks missing or renamed")
        else:
            for ident, entry in supplement.items():
                bindings = entry.get("test_bindings")
                if (entry.get("scope") != "M_only" or entry.get("evidence_status") != "not_supplied"
                        or not isinstance(bindings, list) or not bindings
                        or any(not isinstance(v,str) or not v.startswith("tests.") or ".test_" not in v for v in bindings)):
                    errors.append(ident + ": invalid M-only supplemental bindings")
    return errors


def assess_gate(
    matrix: dict[str, Any],
    discovered: list[str],
    records: list[dict[str, Any]],
    *,
    scope: str,
    identity_errors: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate acceptance; planned bindings and empty discovery cannot pass."""
    if scope not in {"scaffold", "phase1"}:
        raise ValueError("Unknown acceptance scope")
    reasons = list(identity_errors or [])
    counts = Counter(discovered)
    by_id = {record["test_id"]: record["outcome"] for record in records}
    if not discovered:
        reasons.append("zero_discovered_tests")
    if any(count != 1 for count in counts.values()) or len(by_id) != len(records):
        reasons.append("duplicate_test_identity")
    if set(discovered) != set(by_id):
        reasons.append("discovery_and_execution_do_not_match")
    not_passed = sorted(name for name, state in by_id.items() if state != "passed")
    if not_passed:
        reasons.append("executed_tests_not_passed")
    missing_eng: list[str] = []
    bad_bindings: list[str] = []
    for entry in matrix["engineering_requirements"]:
        bindings = entry["test_bindings"]
        if not bindings:
            missing_eng.append(entry["id"])
        for name in bindings:
            if by_id.get(name) != "passed":
                bad_bindings.append(name)
    if missing_eng:
        reasons.append("missing_scaffold_requirement_binding")
    if bad_bindings:
        reasons.append("scaffold_binding_not_passed")

    unresolved_m: list[str] = []
    family_results: list[dict[str, Any]] = []
    for entry in matrix["vf_tests"]:
        outcomes: dict[str, Any] = {}
        for tag, spec in entry["scope_records"].items():
            bindings = spec["test_bindings"]
            if tag != "M":
                outcomes[tag] = {
                    "execution_status": "not_run",
                    "disposition": spec["implementation_status"],
                    "reason": spec["reason"],
                }
            else:
                bad = [name for name in bindings if by_id.get(name) != "passed"]
                implemented = spec["implementation_status"] == "implemented"
                okay = bool(bindings) and implemented and not bad
                if not okay:
                    unresolved_m.append(entry["id"])
                outcomes[tag] = {
                    "execution_status": "passed" if okay else "not_run" if not bindings else "not_passed",
                    "implementation_status": spec["implementation_status"],
                    "test_bindings": bindings,
                    "missing_or_nonpassing_bindings": bad,
                    "reason": "M handling checks only; no substantive E evidence." if okay else spec["reason"],
                }
        family_results.append({"id": entry["id"], "m_required": entry["m_required"], "scopes": outcomes})

    missing_trace: list[str] = []
    for field in ("trace_requirements", "report_groups"):
        for entry in matrix[field]:
            if entry["m_applicable"]:
                bindings = entry["test_bindings"]
                if (
                    entry["implementation_status"] != "implemented"
                    or not bindings
                    or any(by_id.get(name) != "passed" for name in bindings)
                ):
                    missing_trace.append(entry["id"])
    ec_results = []
    missing_ec = []
    if matrix.get("current_step", 0) >= 7:
        supplemental = matrix.get("step7_acceptance", {}).get("evidence_checks", {})
        for i in range(1,9):
            ident = f"EC-C{i:02d}"
            entry = supplemental.get(ident, {})
            bindings = entry.get("test_bindings", [])
            okay = (entry.get("scope") == "M_only" and entry.get("evidence_status") == "not_supplied"
                    and bool(bindings) and all(by_id.get(name) == "passed" for name in bindings))
            if not okay: missing_ec.append(ident)
            ec_results.append({"id":ident,"scope":"M_only","execution_status":"passed" if okay else "not_passed",
                               "test_bindings":bindings,"substantive_E_evidence_supplied":False})
    if scope == "phase1":
        if missing_ec: reasons.append("missing_or_nonpassing_EC_M_bindings")
        if unresolved_m:
            reasons.append("missing_or_nonpassing_required_M_bindings")
        if missing_trace:
            reasons.append("missing_or_nonpassing_M_trace_report_bindings")
    final_eligible = not reasons and not unresolved_m and not missing_trace and not missing_ec
    return {
        "requested_scope": scope,
        "requested_gate_passed": not reasons,
        "phase1_m_complete": final_eligible,
        "reasons": reasons,
        "discovered_count": len(discovered),
        "outcome_counts": dict(sorted(Counter(by_id.values()).items())),
        "nonpassing_test_ids": not_passed,
        "missing_scaffold_requirements": missing_eng,
        "bad_scaffold_bindings": sorted(set(bad_bindings)),
        "required_m_family_count": sum(e["m_required"] for e in matrix["vf_tests"]),
        "unresolved_m_family_ids": unresolved_m,
        "unresolved_m_trace_report_ids": missing_trace,
        "family_results": family_results,
        "ec_m_results": ec_results,
        "unresolved_ec_m_ids": missing_ec,
        "phase1_final_owner_approval": "not_established_by_software_tests",
        "empirical_validation_performed": False,
    }


def annotate_results(matrix: dict[str, Any], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Bind actual outcomes to current scoped contracts; do not manufacture E work."""
    links = {}
    for row in matrix["vf_tests"]:
        for scope, spec in row["scope_records"].items():
            for name in spec["test_bindings"]:
                links.setdefault(name, set()).add(row["id"] + "/" + scope)
    for group in ("trace_requirements", "report_groups"):
        for row in matrix[group]:
            for name in row["test_bindings"]:
                links.setdefault(name, set()).add(row["id"] + "/M")
    for ident, row in matrix.get("step7_acceptance", {}).get("evidence_checks", {}).items():
        for name in row["test_bindings"]: links.setdefault(name, set()).add(ident + "/M")
    return [{**row, "expected_outcome":"passed", "actual_outcome":row["outcome"],
             "requirement_bindings":sorted(links.get(row["test_id"], ())),
             "evidence_scope":"software_fixture_only", "substantive_validation_performed":False}
            for row in records]


def append_journal(directory: Path, run: dict[str, Any]) -> None:
    """Keep prior runs inside the two allowed QA captures; refuse corrupt history."""
    directory.mkdir(parents=True, exist_ok=True)
    journal_path = directory / "test_results.json"
    text_path = directory / "test_output.txt"
    if journal_path.is_symlink() or text_path.is_symlink():
        raise ValueError("QA captures must not be symlinks")
    journal: dict[str, Any] = {"schema_version": "0.1", "runs": []}
    if journal_path.exists():
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
        if journal.get("schema_version") != "0.1" or not isinstance(journal.get("runs"), list):
            raise ValueError("Invalid prior QA journal; refusing overwrite")
        if any(not isinstance(old, dict) or not isinstance(old.get("console_output"), str) or not isinstance(old.get("run_id"), str) for old in journal["runs"]):
            raise ValueError("Invalid prior QA run; refusing overwrite")
    if any(old["run_id"] == run["run_id"] for old in journal["runs"]):
        raise ValueError("Duplicate QA run identity")
    journal["runs"].append(run)
    texts = [f"=== {r['run_id']} ===\n{r['console_output']}" for r in journal["runs"]]
    payloads = [
        (journal_path, json.dumps(journal, ensure_ascii=False, indent=2, allow_nan=False) + "\n"),
        (text_path, "\n".join(texts)),
    ]
    temporary: list[tuple[Path, Path]] = []
    try:
        for target, content in payloads:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=directory, delete=False) as handle:
                handle.write(content)
                temporary.append((Path(handle.name), target))
        for source, target in temporary:
            os.replace(source, target)
    finally:
        for source, _ in temporary:
            source.unlink(missing_ok=True)


def environment_record() -> dict[str, Any]:
    tools: dict[str, Any] = {}
    for name in ("setuptools", "pip", "build", "wheel"):
        try:
            tools[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            tools[name] = None
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "working_directory": str(ROOT),
        "optional_tools_present": tools,
        "packaging_check": {
            "status": "not_run",
            "reason": "This Phase 1 delivery uses direct module execution. No build/install or distribution test performed; no dependency installation authorized.",
        },
        "compatibility_claim": "Only this recorded interpreter and environment were tested.",
    }


def file_fingerprints() -> dict[str, str]:
    paths = [p for p in ROOT.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix in {".py", ".json", ".toml", ".md"} and "artifacts" not in p.relative_to(ROOT).parts and "__pycache__" not in p.relative_to(ROOT).parts]
    paths.append(ROOT / ".gitignore")
    return {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in sorted(set(paths))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--scope", choices=("scaffold", "phase1"), default="phase1",
        help="Acceptance gate only. Default phase1 fails until all mandatory M bindings pass.",
    )
    args = parser.parse_args(argv)
    try:
        matrix = load_matrix()
        errors = validate_matrix(matrix)
        identities = baseline_checks(matrix)
        errors.extend(f"baseline_failed:{r['path']}" for r in identities if r["status"] != "passed")
        suite = unittest.TestLoader().discover(
            start_dir=str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT)
        )
        discovered, records, text = execute_suite(suite)
        records = annotate_results(matrix, records)
        gate = assess_gate(matrix, discovered, records, scope=args.scope, identity_errors=errors)
        code = 0 if gate["requested_gate_passed"] else 1
        text += (
            f"\nRequested gate: {args.scope}\n"
            f"Requested gate passed: {gate['requested_gate_passed']}\n"
            f"Phase 1 M complete: {gate['phase1_m_complete']}\n"
            f"Unresolved M families ({len(gate['unresolved_m_family_ids'])}): "
            + ", ".join(gate["unresolved_m_family_ids"]) + "\n"
            + "Gate reasons: " + (", ".join(gate["reasons"]) or "none") + "\n"
            + f"Runner exit code: {code}\n"
        )
        run = {
            "run_id": str(uuid.uuid4()),
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "execution_phase": 1,
            "implementation_step": matrix["current_step"],
            "command": [sys.executable, "tools/run_phase1_checks.py", "--scope", args.scope],
            "exit_code": code,
            "authorization": matrix["authorization"],
            "environment": environment_record(),
            "baseline_verification": identities,
            "matrix_validation_errors": errors,
            "file_fingerprints": file_fingerprints(),
            "fixture_versions": {p.relative_to(ROOT).as_posix(): sha256_file(p)
                for base in (ROOT / "tests/fixtures", ROOT / "examples")
                for p in sorted(base.rglob("*")) if p.is_file() and not p.is_symlink()},
            "scientific_source_pins": matrix["theory_sources"] + [matrix["ec001_supplement"]["source"]],
            "discovered_test_ids": discovered,
            "test_results": records,
            "acceptance": gate,
            "console_output": text,
        }
        directory = ROOT / "artifacts" / "phase1"
        if directory.resolve() != directory:
            raise ValueError("QA directory must remain within the fixed local workspace")
        append_journal(directory, run)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"QA harness error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(text, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
