#!/usr/bin/env python3
"""Phase 3 local QA: inherited M/V, current scaffold and longitudinal L scopes.

New journals go only to artifacts/phase3. Offline receipts are never described as
fresh GitHub observations. No candidate execution, model calls or real E evidence.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys
import tempfile
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests import phase3_helpers as h
from tools import run_phase1_checks as mr
from tools import run_phase2_checks as vr
from tests import phase2_helpers as vh


def _fulfilled(row, actual):
    bindings = row.get("test_bindings", [])
    failed = [i for i in bindings if actual.get(i) != "passed"]
    okay = row.get("implementation_status") == "implemented" and bool(bindings) and not failed
    return {"id": row["id"], "implementation_status": row.get("implementation_status"),
            "test_bindings": bindings, "missing_or_nonpassing": failed,
            "execution_status": "passed" if okay else "not_run" if not bindings else "not_passed",
            "required_by_step": row["required_by_step"], "substantive_validation_performed": False}


def assess_gate(matrix, discovered, records, *, scope, predecessor_ids, inherited_m, inherited_v,
                reconciliation, inventory, matrix_errors=(), pin_errors=()):
    if scope not in {"current", "phase3"}:
        raise ValueError("invalid_phase3_scope")
    errors = list(matrix_errors) + list(pin_errors)
    if not isinstance(discovered, list) or any(not isinstance(i, str) for i in discovered):
        errors.append("invalid_discovery"); discovered = []
    valid_records = isinstance(records, list) and all(isinstance(r, dict) and isinstance(r.get("test_id"), str)
                                                     and isinstance(r.get("outcome"), str) for r in records)
    if not valid_records:
        errors.append("invalid_execution_records"); records = []
    actual = {r["test_id"]: r["outcome"] for r in records}
    if not discovered: errors.append("zero_discovered_tests")
    if len(set(discovered)) != len(discovered) or len(actual) != len(records): errors.append("duplicate_test_identity")
    if set(discovered) != set(actual): errors.append("discovery_execution_mismatch")
    if any(x != "passed" for x in actual.values()): errors.append("executed_tests_not_passed")
    missing = [i for i in predecessor_ids if actual.get(i) != "passed"]
    if missing: errors.append("predecessor_test_missing_or_nonpassing")
    m_ok = inherited_m.get("requested_gate_passed") is True and inherited_m.get("phase1_m_complete") is True
    v_ok = inherited_v.get("requested_gate_passed") is True and inherited_v.get("phase2_v_complete") is True
    if not m_ok: errors.append("inherited_M_not_passed")
    if not v_ok: errors.append("inherited_V_not_passed")
    step = matrix["delivery"]["step"]
    stage_errors = []
    for i in range(1, min(step, 9) + 1):
        row = matrix["stage_bindings"][str(i)]
        bs = row["test_bindings"]
        if row["implementation_status"] != "implemented" or not bs or any(actual.get(x) != "passed" for x in bs):
            stage_errors.append(f"stage_{i}_not_verified")
    errors += stage_errors
    scaffold_ok = not errors
    groups = {g: [_fulfilled(r, actual) for r in matrix[g]] for g in ("longitudinal", "reports", "oracles")}
    due = [r["id"] for rows in groups.values() for r in rows
           if r["required_by_step"] <= step and r["execution_status"] != "passed"]
    all_missing = [r["id"] for rows in groups.values() for r in rows if r["execution_status"] != "passed"]
    saved = h.inspect_reconciliation(reconciliation, inventory)
    l_ok = scaffold_ok and not all_missing and step >= 9 and saved["record_consistent"]
    if due: errors.append("current_L_requirements_incomplete")
    if scope == "phase3":
        if all_missing: errors.append("full_L_requirements_incomplete")
        if step < 9: errors.append("integrated_L_verification_not_reached")
    if not saved["record_consistent"]: errors.append("exact_phase2_baseline_sync_unverified")
    return {"requested_scope": scope, "requested_gate_passed": not errors,
            "local_scaffold_passed": scaffold_ok, "phase3_step": step,
            "phase1_m_complete": m_ok, "phase2_v_complete": v_ok,
            "phase3_l_software_complete": l_ok, "saved_baseline_receipt": saved,
            "current_repository_delivery": "separate_live_audit_required",
            "discovered_count": len(discovered),
            "outcome_counts": dict(sorted(Counter(r["outcome"] for r in records).items())),
            "missing_predecessor_ids": missing, "unresolved_current_ids": due,
            "unresolved_l_ids": [r["id"] for r in groups["longitudinal"] if r["execution_status"] != "passed"],
            "unresolved_full_ids": all_missing, "requirements": groups,
            "reasons": sorted(set(errors)), "substantive_validation_performed": False,
            "final_owner_acceptance": "not_established_by_software_tests"}


def annotate_results(matrix, records, m, v, *, environment):
    result = vr.annotated_results(v, records, m)
    links = {}
    for group in ("longitudinal", "reports", "oracles"):
        for row in matrix[group]:
            for method in row["test_bindings"]: links.setdefault(method, []).append(row["id"] + "/L_software")
    for stage, row in matrix["stage_bindings"].items():
        for method in row["test_bindings"]: links.setdefault(method, []).append("P3-S" + stage + "/scaffold")
    for row in result:
        row.update(phase3_requirement_bindings=sorted(set(links.get(row["test_id"], []))),
                   expected_outcome="passed", actual_outcome=row["outcome"],
                   environment=environment, execution_phase=3,
                   material_role="software_fixture_or_gate_test",
                   input_oracle_identity_ref="file_fingerprints",
                   phase3_plan_identity={"path": "PHASE_3_PLAN.md", "sha256": h.PLAN_SHA256},
                   substantive_validation_performed=False)
    return result


def _summary(journal):
    header = "Phase 3 execution index. Full immutable runs are referenced below.\n"
    return (header + "".join(f"{r['run_id']} exit={r['exit_code']} counts={json.dumps(r['outcome_counts'],sort_keys=True)} "
                            f"run={r['run_path']} sha256={r['run_sha256']} bytes={r['run_bytes']} "
                            f"console={r['console_path']} sha256={r['console_sha256']} bytes={r['console_bytes']}\n"
                            for r in journal["runs"])).encode()


def _record_hash(value):
    return h.digest(h.canonical({k: v for k, v in value.items() if k != "entry_sha256"}))


def check_journal(directory: Path):
    h.regular_path(directory)
    index, summary = directory / "test_results.json", directory / "test_output.txt"
    for p in (index, summary): h.regular_path(p)
    if index.exists() != summary.exists(): raise ValueError("qa_index_pair_incomplete")
    if not index.exists():
        data = {"schema_version": "0.1", "phase": 3, "storage": "immutable_history_index", "runs": []}
    else:
        data = h.read_json(index)
        if (not isinstance(data, dict) or set(data) != {"schema_version", "phase", "storage", "runs"}
                or data["schema_version"] != "0.1" or data["phase"] != 3
                or data["storage"] != "immutable_history_index" or not isinstance(data["runs"], list)):
            raise ValueError("invalid_qa_index")
        if summary.read_bytes() != _summary(data): raise ValueError("qa_summary_changed")
    seen = set(); previous = None
    for row in data["runs"]:
        rid = row.get("run_id")
        if (not isinstance(rid, str) or not re.fullmatch(r"[0-9a-f]{32}", rid) or rid in seen
                or row.get("previous_entry_sha256") != previous or row.get("entry_sha256") != _record_hash(row)):
            raise ValueError("qa_history_chain_invalid")
        for name, filename in (("run", "run.json"), ("console", "console.txt"), ("files", "file_manifest.json")):
            relative = f"history/{rid}/{filename}"
            if row.get(name + "_path") != relative: raise ValueError("qa_history_path_changed")
            path = directory / relative; h.regular_path(path)
            if not path.is_file() or path.stat().st_size != row[name + "_bytes"] or h.digest(path.read_bytes()) != row[name + "_sha256"]:
                raise ValueError("qa_history_bytes_changed")
        seen.add(rid); previous = row["entry_sha256"]
    history = directory / "history"; h.regular_path(history)
    if history.exists() and {p.name for p in history.iterdir()} != seen:
        raise ValueError("qa_unindexed_or_missing_history")
    return data


def append_journal(directory: Path, run: dict):
    """Never rewrite earlier full runs. Interrupted publication is detected.

    Index and summary replacement is not a two-file atomic transaction. An
    incomplete pair or orphan run stops future appends instead of hiding history.
    """
    h.regular_path(directory); directory.mkdir(parents=True, exist_ok=True)
    journal = check_journal(directory)
    rid = run.get("run_id")
    if (not isinstance(rid, str) or not re.fullmatch(r"[0-9a-f]{32}", rid)
            or rid in {r["run_id"] for r in journal["runs"]} or not isinstance(run.get("console_output"), str)):
        raise ValueError("invalid_or_duplicate_run_id")
    history = directory / "history"; history.mkdir(mode=0o700, exist_ok=True)
    target = history / rid; target.mkdir(mode=0o700)
    blobs = {"run.json": h.canonical(run), "console.txt": run["console_output"].encode(),
             "file_manifest.json": h.canonical(run.get("file_fingerprints", {}))}
    for name, data in blobs.items():
        with open(target / name, "xb") as f:
            os.chmod(target / name, 0o600); f.write(data); f.flush(); os.fsync(f.fileno())
    entry = {"run_id": rid, "exit_code": run["exit_code"],
             "outcome_counts": run["acceptance"]["outcome_counts"],
             "previous_entry_sha256": journal["runs"][-1]["entry_sha256"] if journal["runs"] else None}
    for key, name in (("run", "run.json"), ("console", "console.txt"), ("files", "file_manifest.json")):
        entry.update({key + "_path": f"history/{rid}/{name}", key + "_sha256": h.digest(blobs[name]),
                      key + "_bytes": len(blobs[name])})
    entry["entry_sha256"] = _record_hash(entry)
    new = {**journal, "runs": journal["runs"] + [entry]}
    staged = []
    try:
        for destination, data in ((directory / "test_output.txt", _summary(new)),
                                  (directory / "test_results.json", h.canonical(new))):
            with tempfile.NamedTemporaryFile(dir=directory, delete=False) as f:
                temporary = Path(f.name); staged.append((temporary, destination))
                os.chmod(temporary, 0o600); f.write(data); f.flush(); os.fsync(f.fileno())
        for src, dst in staged: os.replace(src, dst)
    finally:
        for src, _ in staged: src.unlink(missing_ok=True)


def inherited_assessments(discovered, outcomes):
    m, v = vh.load_phase1_matrix(), vh.read_matrix()
    me = mr.validate_matrix(m)
    me += [x["path"] for x in mr.baseline_checks(m) if x["status"] != "passed"]
    mg = mr.assess_gate(m, discovered, outcomes, scope="phase1", identity_errors=me)
    vg = vr.assess_gate(v, discovered, outcomes, scope="phase2", predecessor_gate=mg,
        reconciliation=vh.read_json(ROOT / "artifacts/phase2/baseline_reconciliation.json"),
        matrix_errors=vh.validate_matrix(v),
        pin_failures=[x["path"] for x in vh.identity_checks(v) if x["status"] != "passed"])
    return m, v, mg, vg


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--scope", choices=("current", "phase3"), default="phase3")
    args = parser.parse_args(argv)
    try:
        matrix = h.load_matrix()
        matrix_errors = h.validate_matrix(matrix)
        if matrix_errors:
            sys.stderr.write("Phase 3 matrix invalid: " + ", ".join(matrix_errors) + "\n")
            return 2
        inventory = h.inventory_record(); ids = h.predecessor_ids()
        checks = h.current_identity_checks()
        pins = [r["path"] for r in checks if r["status"] != "passed"]
        recpath = ROOT / "artifacts/phase3/baseline_reconciliation.json"
        receipt = h.read_json(recpath) if recpath.exists() else None
        # Detect damaged history before paying for another test execution.
        check_journal(ROOT / "artifacts/phase3")
        begin = datetime.now(timezone.utc).isoformat(); start = time.monotonic()
        suite = unittest.TestLoader().discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
        discovered, outcomes, console = mr.execute_suite(suite)
        m, v, mg, vg = inherited_assessments(discovered, outcomes)
        result = assess_gate(matrix, discovered, outcomes, scope=args.scope, predecessor_ids=ids,
            inherited_m=mg, inherited_v=vg, reconciliation=receipt, inventory=inventory,
            matrix_errors=matrix_errors, pin_errors=pins)
        # Both scope assessments consume this same real execution. They are
        # decisions over one run, not two additional fabricated test runs.
        alternate = assess_gate(matrix, discovered, outcomes,
            scope="phase3" if args.scope == "current" else "current", predecessor_ids=ids,
            inherited_m=mg, inherited_v=vg, reconciliation=receipt, inventory=inventory,
            matrix_errors=matrix_errors, pin_errors=pins)
        code = 0 if result["requested_gate_passed"] else 1
        files = {p.relative_to(ROOT).as_posix(): h.digest(p.read_bytes()) for p in sorted(ROOT.rglob("*"))
                 if p.is_file() and not p.is_symlink() and not set(p.relative_to(ROOT).parts) & {".git", "__pycache__", "artifacts"}}
        environment = {"python": sys.version, "platform": platform.platform(),
                       "no_site": bool(sys.flags.no_site), "bytecode_disabled": bool(sys.dont_write_bytecode)}
        footer = (f"\nPhase 3 scope: {args.scope}\nLocal scaffold passed: {result['local_scaffold_passed']}\n"
                  f"Inherited M: {mg['requested_gate_passed']}; V: {vg['requested_gate_passed']}\n"
                  f"Unfinished L requirements: {len(result['unresolved_l_ids'])}\n"
                  f"Baseline receipt: {result['saved_baseline_receipt']['assurance']}\n"
                  f"Current repository delivery: {result['current_repository_delivery']}\n"
                  f"Gate reasons: {', '.join(result['reasons']) or 'none'}\nRunner exit: {code}\n")
        run = {"schema_version": "0.1", "execution_phase": 3, "implementation_step": matrix["delivery"]["step"],
               "run_id": uuid.uuid4().hex, "started_at_utc": begin, "elapsed_seconds": time.monotonic() - start,
               "command": [sys.executable, "tools/run_phase3_checks.py", "--scope", args.scope],
               "environment": environment, "authorization": matrix["delivery"]["authorization"],
               "exit_code": code, "file_fingerprints": files, "baseline_checks": checks,
               "discovered_test_ids": discovered,
               "test_results": annotate_results(matrix, outcomes, m, v, environment=environment),
               "inherited_M": mg, "inherited_V": vg, "acceptance": result,
               "alternate_scope_assessment": alternate,
               "alternate_assessment_basis": "same_executed_method_records_no_additional_run",
               "console_output": console + footer,
               "substantive_validation_performed": False, "model_calls": 0, "candidate_programs_executed": 0,
               "github_actions_run": False}
        append_journal(ROOT / "artifacts/phase3", run)
        sys.stdout.write(console + footer)
        return code
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        sys.stderr.write("Phase 3 QA input, identity or history failure; no success claimed.\n")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
