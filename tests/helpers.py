"""Standard-library helpers for trusted tests, not an input execution facility."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "tests" / "phase1_matrix.json"

# All commands are fixed here. No executable or program text comes from input.
_TRUSTED_CASES: dict[str, tuple[str, ...]] = {
    "import": (
        "-c",
        "import structdet_bench; print(structdet_bench.__version__)",
    ),
    "help": ("-m", "structdet_bench", "--help"),
    "version": ("-m", "structdet_bench", "--version"),
    "no_args": ("-m", "structdet_bench"),
    "unknown_option": ("-m", "structdet_bench", "--not-a-real-option"),
    "validate_no_input": ("-m", "structdet_bench", "validate"),
    "analyze_no_input": ("-m", "structdet_bench", "analyze"),
    "runner_help": ("tools/run_phase1_checks.py", "--help"),
}
for _name in ("generate", "train", "execute", "judge", "compare", "recover"):
    _TRUSTED_CASES[_name] = ("-m", "structdet_bench", _name)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_matrix() -> dict[str, Any]:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    for pin in matrix["baseline"]:
        if sha256_file(ROOT / pin["path"]) != pin["sha256"]:
            raise ValueError("Frozen catalogue source mismatch")
    columns = {
        "vf_tests": ("VALIDATION_AND_FALSIFICATION.md", "VT", ["id", "source_delivery", "upstream_anchors", "arrangement", "required_outcome"]),
        "trace_requirements": ("THEORY_TO_CODE_TRACEABILITY.md", "TR", ["id", "origin", "controlling_rule", "planned_responsibility", "vf_ids", "report_groups", "permitted_inference", "limitation"]),
        "report_groups": ("THEORY_TO_CODE_TRACEABILITY.md", "RF", ["id", "required_content", "trace_ids", "vf_ids"]),
    }
    for group, (filename, prefix, fields) in columns.items():
        rows = {row[0]: row for row in source_table(filename, prefix)}
        for entry in matrix[group]:
            key = entry.get("catalogue_row", entry["id"])
            if key != entry["id"] or key not in rows:
                raise ValueError("Mismatched catalogue row")
            for field, value in zip(fields, rows[key]):
                if field == "upstream_anchors":
                    value = [x.strip() for x in value.split(",")]
                elif field in {"vf_ids", "trace_ids", "report_groups"}:
                    value = re.findall({"vf_ids": r"VT-\d{2}", "trace_ids": r"TR-\d{2}", "report_groups": r"RF-\d{2}"}[field], value)
                if field in entry and entry[field] != value:
                    raise ValueError("Catalogue content differs from pinned source")
                entry[field] = value
    for entry in matrix["vf_tests"]:
        entry["trace_ids"] = [r["id"] for r in matrix["trace_requirements"] if entry["id"] in r["vf_ids"]]
        entry["report_groups"] = [r["id"] for r in matrix["report_groups"] if entry["id"] in r["vf_ids"]]
        for tag, record in entry["scope_records"].items():
            record.setdefault("fixture_refs", [])
            record.setdefault("reason", "Partial software record handling or future scoped requirement. No independent E evidence supplied.")
    for group in ("trace_requirements", "report_groups"):
        for entry in matrix[group]:
            entry.setdefault("test_bindings", [])
    return matrix


def baseline_checks(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare local bytes with pinned identities; identity is not validity."""
    checks: list[dict[str, Any]] = []
    for item in matrix["baseline"]:
        relative = Path(item["path"])
        check = {
            "path": item["path"],
            "version": item["version"],
            "expected_sha256": item["sha256"],
            "actual_sha256": None,
            "status": "failed",
        }
        try:
            path = (ROOT / relative).resolve()
            if relative.is_absolute() or path.parent != ROOT:
                raise ValueError("Baseline path must name a file in the project root")
            check["actual_sha256"] = sha256_file(path)
            if check["actual_sha256"] == check["expected_sha256"]:
                check["status"] = "passed"
            else:
                check["reason"] = "baseline_hash_mismatch"
        except (OSError, ValueError) as exc:
            check["reason"] = f"{type(exc).__name__}: {exc}"
        checks.append(check)
    return checks


def source_table(filename: str, prefix: str) -> list[list[str]]:
    """Read the fixed Markdown catalogue rows without changing their text."""
    return [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in (ROOT / filename).read_text(encoding="utf-8").splitlines()
        if re.match(rf"^\| {re.escape(prefix)}-\d+ \|", line)
    ]


def run_trusted_case(case: str) -> subprocess.CompletedProcess[str]:
    """Launch one named, checked-in test command using this interpreter."""
    if case not in _TRUSTED_CASES:
        raise ValueError("Unknown trusted test case; arbitrary commands are forbidden")
    # Deliberately do not pass API keys, model credentials, or PYTHONPATH.
    env = {
        name: os.environ[name]
        for name in ("PATH", "SYSTEMROOT", "WINDIR", "TMP", "TEMP", "TMPDIR")
        if name in os.environ
    }
    env.update({"PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
    return subprocess.run(
        [sys.executable, "-B", "-S", *_TRUSTED_CASES[case]],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=15,
        check=False,
        shell=False,
    )

# Stipulated input records are software fixtures, never human evidence.
def tagged(value: Any = None, *, state: str = "known", reason: str | None = None) -> dict[str, Any]:
    result = {"state": state, "evidence_refs": []}
    if state == "known": result["value"] = value
    if reason is not None: result["reason"] = reason
    return result


def record_ref(kind: str, identity: str) -> dict[str, str]:
    return {"record_type": kind, "record_id": identity, "record_version": "0.1"}


def sample_record(identity: str = "s1", cell: str = "cell1") -> dict[str, Any]:
    return {
        **record_ref("realization", identity), "sample_id": identity, "analysis_cell_id": cell,
        "attempt_id": tagged(state="unknown"), "raw_response_ref": tagged(state="unknown"),
        "output_ref": tagged(state="unknown"), "output_content_hash": tagged(state="unknown"),
        "generation_group_id": tagged(state="unknown"), "within_group_index": tagged(state="unknown"),
        "sample_order": tagged(1), "extraction_rule_version": tagged("fixture-extraction-0.1"),
        "completion_status": "complete",
    }


def assignment_record(identity: str = "assign1", sample: str = "s1", revision: str = "0.1") -> dict[str, Any]:
    return {
        **record_ref("assignment", identity), "assignment_id": identity, "assignment_version": revision,
        "sample_id": sample, "frame_id": "frame1", "assignment_status": "assigned",
        "structural_class_id": "SORT-ADJ", "assignment_review_status": "fixture",
        "assignment_method": tagged("stipulated"), "decision_rationale": tagged("Software fixture only."),
        "evidence_refs": [], "assignment_evidence_policy_id": "fixture_only",
        "assignment_evidence_policy_version": "0.1", "supersedes_assignment_id": tagged(None),
    }


def artifact_record(identity: str = "artifact1", path: str = "body.txt") -> dict[str, Any]:
    return {**record_ref("artifact", identity), "artifact_id": identity,
            "content_ref": tagged({"kind": "local", "path": path}),
            "expected_sha256": tagged(state="unknown"), "knowledge_type": tagged("fixture")}


def minimal_manifest() -> dict[str, Any]:
    frame = {
        **record_ref("frame", "frame1"), "frame_id": "frame1",
        "task_id": "bounded_integer_sort", "task_version": "0.1",
        "analytic_resolution_id": "sorting_mechanism_family", "analytic_resolution_version": "0.1",
        "structural_schema_id": "sorting_mechanism_partition", "structural_schema_version": "0.1",
        "reference_registry_id": "sorting_reference_eight", "reference_registry_version": "0.1",
        "validity_rubric_ref": "bounded_integer_sort_validity_v1",
        "task_context": "Stipulated input-shape fixture for the adopted sorting task.",
        "consequence_horizon": "One complete invocation across the declared input domain.",
        "load_bearing_invariants": ["Role of ordering mechanism."],
        "consequence_signature_spec": "Inspect mechanism, not just returned values.",
        "equivalence_rule_ref": "HERO_BENCHMARK_SPEC.md section 4",
        "admissible_substitutions": "Registered mechanism-preserving variations.",
        "evidence_requirement": "This fixture supplies no independent mechanism evidence.",
        "exceptional_case_rules": "Preserve unresolved and unknown mechanisms.",
        "registration_ref": tagged(state="unknown"),
    }
    protocol = {
        **record_ref("protocol", "protocol1"), "generation_protocol_id": "protocol1",
        "generation_protocol_version": "0.1", "conditioning_context_ref": tagged(state="unknown"),
        "decoding_settings": tagged(state="unknown"),
        "seed": tagged(state="not_applicable", reason="No model invoked for fixture."),
    }
    cell = {
        **record_ref("cell", "cell1"), "analysis_cell_id": "cell1", "frame_id": "frame1",
        "generation_protocol_id": "protocol1", "generation_protocol_version": "0.1",
        "prompt_block_id": "fixture-block1", "prompt_id": "fixture-prompt1", "condition_id": "fixture-condition1",
        "model_identifier": tagged(state="not_applicable", reason="Stipulated fixture, no model."),
        "model_family": tagged(state="unknown"),
        "checkpoint_identifier": tagged(state="unavailable", reason="No checkpoint collected."),
        "collection_window": tagged(state="not_applicable", reason="No empirical collection."),
    }
    return {
        "input_schema_version": "0.1", "bundle_id": "fixture-bundle1", "study_id": "fixture-study1",
        "data_role": "fixture", "frames": [frame], "protocols": [protocol], "cells": [cell],
        "analysis_config": {
            "analysis_config_id": "fixture-config1", "assignment_evidence_policy_id": "fixture_only",
            "assignment_evidence_policy_version": "0.1", "requested_k": [5, 10, 20],
            "selection": [{"analysis_cell_id": "cell1", "selected_sample_ids": tagged(state="unknown"),
                           "sample_order": tagged(state="unknown"), "registered_positions": tagged(state="unknown"),
                           "selection_basis": tagged("Input-shape fixture; no population selected.")}],
            "assignment_pins": [], "validity_pins": [],
        },
        "record_files": [{"role": "observations", "format": "jsonl", "path": "records.jsonl",
                          "expected_sha256": tagged(state="unknown")}],
    }


def write_input_bundle(directory: Path, records: list[dict[str, Any]] | None = None,
                       manifest: dict[str, Any] | None = None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    rows = "".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in (records or []))
    (directory / "records.jsonl").write_bytes(rows.encode("utf-8"))
    (directory / "bundle.json").write_bytes(json.dumps(manifest or minimal_manifest(), ensure_ascii=False, allow_nan=False).encode("utf-8"))
    return directory / "bundle.json"


# Step 3 builders are artificial assertions. No real person or model experiment.
def support_record(kind: str, identity: str, **changes: Any) -> dict[str, Any]:
    from structdet_bench.evidence import SUPPORT_FIELDS, SUPPORT_ENUMS
    p: dict[str, Any] = {
        "payload_version": "0.1", "data_role": "fixture", "mock": True, "state": "active",
        "scope_refs": [record_ref("frame", "frame1")], "origin": tagged("Artificial test record"),
        "knowledge_type": tagged("fixture"), "transformation_refs": [], "evidence_refs": [],
    }
    for name, spec in SUPPORT_FIELDS[kind].items():
        if spec in SUPPORT_ENUMS: p[name] = sorted(SUPPORT_ENUMS[spec])[0]
        elif spec == "tag": p[name] = tagged(state="unknown")
        elif spec == "ref": p[name] = record_ref("realization", "s1")
        elif spec in {"refs", "ids", "texts"}: p[name] = []
        elif spec == "bool": p[name] = False
        elif spec == "object": p[name] = {}
        else: p[name] = "fixture-value"
    p.update(changes)
    return {**record_ref(kind, identity), "payload": p}


def evidence_bundle(root: Path, *, policy: str = "fixture_only", samples: int = 1) -> tuple[Path, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Stipulated fixture or imported-shaped records, always a fixture context."""
    m = minimal_manifest()
    m["analysis_config"]["assignment_evidence_policy_id"] = policy
    observations: list[dict[str, Any]] = []
    supports: list[dict[str, Any]] = []
    imported = policy == "adjudicated_import"
    reviewer = support_record("role", "reviewer", entity_id=tagged("test-person-1"), entity_type="human",
                             role="adjudicator", qualification=tagged("Stipulated test qualification"),
                             method=tagged("inspection"), data_role="descriptive" if imported else "fixture", mock=not imported)
    supports.append(reviewer)
    for i in range(1, samples + 1):
        sid = f"s{i}"; observations.append(sample_record(sid))
        a = assignment_record(f"a{i}", sid)
        a["assignment_evidence_policy_id"] = policy
        a["assignment_review_status"] = "adjudicated" if imported else "fixture"
        v = {**record_ref("validity",f"v{i}"),"validity_id":f"v{i}","validity_version":"0.1", "sample_id":sid,
             "validity_status":"valid","validity_review_status":"adjudicated" if imported else "fixture",
             "validity_rubric_ref":tagged("bounded_integer_sort_validity_v1"),"decision_rationale":tagged("Stipulated fixture decision"),
             "supersedes_validity_id":tagged(None),"evidence_refs":[]}
        for axis, obj, outcome in (("assignment",a,"SORT-ADJ"),("validity",v,"valid")):
            rid = obj["record_id"]; eid = "e-" + rid
            e = support_record("evidence", eid, target_ref=record_ref(axis,rid),
                purpose=("mechanism" if axis == "assignment" else "validity") if imported else "fixture_declaration",
                assertion=tagged(outcome),method=tagged(("control_flow" if axis == "assignment" else "execution") if imported else "stipulated"),
                detail=tagged("Artificial evidence to exercise record routing; not an actual observation."),
                access="readable",conflict_status="none_declared",reviewer_refs=[record_ref("role","reviewer")],
                data_role="descriptive" if imported else "fixture",mock=not imported)
            if imported and axis == "validity":
                suite = support_record("domain_suite", "suite-"+rid, suite_id="suite-"+rid,
                    stage="performed", property="sorting_behavior", environment=tagged("Fixture environment declaration"),
                    oracle_origin=tagged("Stipulated oracle"), data_role="descriptive", mock=False)
                result = support_record("domain_result", "result-"+rid, target_ref=record_ref("realization",sid),
                    suite_ref=record_ref("domain_suite","suite-"+rid), property="sorting_behavior",outcome="passed",
                    environment=tagged("Stipulated environment"),input_manifest=tagged("Stipulated input set"),
                    observations=tagged("No real program was executed; simulated imported result"),data_role="descriptive",mock=False)
                supports.extend([suite,result]);e["payload"]["evidence_refs"]=[record_ref("domain_result","result-"+rid)]
            obj["evidence_refs"]=[record_ref("evidence",eid)];supports.append(e)
            if imported:
                dec = support_record("adjudication","d-"+rid,target_ref=record_ref(axis,rid),
                    decision_state="resolved",outcome=tagged(outcome),reviewer_refs=[record_ref("role","reviewer")],
                    basis_refs=[record_ref("evidence",eid)],data_role="descriptive",mock=False)
                supports.append(dec);obj["evidence_refs"].append(record_ref("adjudication","d-"+rid))
            m["analysis_config"][axis+"_pins"].append({"sample_id":sid,axis+"_id":rid,axis+"_version":"0.1"})
        observations.extend([a,v])
    m["record_files"].append({"role":"evidence","format":"jsonl","path":"evidence.jsonl","expected_sha256":tagged(state="unknown")})
    return rewrite_evidence_bundle(root,observations,supports,m),observations,supports,m


def rewrite_evidence_bundle(root: Path, observations: list[dict[str, Any]], supports: list[dict[str, Any]], manifest: dict[str, Any]) -> Path:
    path=write_input_bundle(root,observations,manifest)
    (root/"evidence.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in supports),encoding="utf-8")
    return path
