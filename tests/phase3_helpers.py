"""Phase 3 trusted QA identities. No longitudinal runtime or scientific inference.

The pinned plan supplies the requirement wording. Receipt inspection is explicitly
an offline consistency check; a current GitHub observation is a separate action.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN_SHA256 = "1ca74fbba06bea44f2b656b3f4e6b46b0c6747cf13640c3f1ea29c69ef3d6352"
ARCHIVE_SHA256 = "c641744502bdf18bed73758e1e14d923179289fbc2a9283c71b9ed94e8a903ac"
INVENTORY_SHA256 = "d51a7af01df864c5e2a9c3b812d084a43c75711a9e0ea739b10b21b9b090eba5"
PREDECESSOR_IDS_SHA256 = "b7fcf24384f8d7953aaf03f04a1d11bb882883ea6da3ccb2d69e8e2ea1b8844a"
REPOSITORY = "DavidWallstructurallaw/structdet-bench"
SUBJECT = "phase2_final_114_v1"
MATRIX_PATH = ROOT / "tests/phase3_matrix.json"
INVENTORY_PATH = ROOT / "artifacts/phase3/phase2_final_file_inventory.json"
IDS_PATH = ROOT / "artifacts/phase3/predecessor_test_ids.json"
METHOD = re.compile(r"tests\.test_[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.test_[A-Za-z0-9_]+\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
MAX_QA_BYTES = 32 * 1024 * 1024

# Exact implementation identities for the approved Step 8 ordinary-write paths.
# The historical 114-file inventory and all scientific pins retain their bytes.
STEP8_IMPLEMENTATION_PINS = {'structdet_bench/cli.py': '5df07e8991c1af105877336c55b5a3a1f05db69945544654d8e664ec84814704', 'structdet_bench/pipeline.py': '9ded7c505ec4a9ad213ea4d3840066594dece5277cd21ac07315aea0a24c86f2', 'structdet_bench/reporting.py': '9e22bd778c92a5e55cee25522b5864bd428a1f33e40b703a3627f3d64f461587'}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def regular_path(path: Path) -> None:
    """Reject symlink ancestors as well as a symlink leaf in trusted QA paths."""
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("qa_symlink_path")


def read_json(path: Path) -> Any:
    regular_path(path)
    if not path.is_file() or path.stat().st_size > MAX_QA_BYTES:
        raise ValueError("qa_file_unavailable_or_limit")
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError("duplicate_qa_key")
            out[key] = value
        return out
    def bad(_):
        raise ValueError("nonfinite_qa_number")
    def finite(token):
        value = float(token)
        if not math.isfinite(value):
            raise ValueError("nonfinite_qa_number")
        return value
    return json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=bad, parse_float=finite)


def plan_text(root: Path = ROOT) -> str:
    path = root / "PHASE_3_PLAN.md"
    regular_path(path)
    data = path.read_bytes()
    if digest(data) != PLAN_SHA256:
        raise ValueError("approved_phase3_plan_changed")
    return data.decode("utf-8")


def plan_catalogues(root: Path = ROOT) -> dict[str, list[dict[str, Any]]]:
    """Extract exact source-table cells; no generated or inferred requirements."""
    text = plan_text(root)
    result = {"longitudinal": [], "reports": [], "oracles": []}
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        row = [x.strip() for x in line.strip("|").split("|")]
        if re.fullmatch(r"P3-L\d\d", row[0]):
            if len(row) != 4:
                raise ValueError("malformed_L_source_row")
            steps = [int(x) for x in re.findall(r"\d+", row[3])]
            # Step 10 is administrative; software obligations must be ready by 9.
            result["longitudinal"].append({"id": row[0], "anchor": row[1],
                "requirement": row[2], "primary_steps": row[3],
                "required_by_step": min(max(steps), 9)})
        elif re.fullmatch(r"P3-RF\d\d", row[0]):
            if len(row) != 3:
                raise ValueError("malformed_RF_source_row")
            result["reports"].append({"id": row[0], "requirement": row[1],
                                     "l_anchors": row[2], "required_by_step": 9})
        elif re.match(r"O\d\d: ", row[0]):
            if len(row) != 2:
                raise ValueError("malformed_oracle_source_row")
            result["oracles"].append({"id": "P3-" + row[0][:3], "title": row[0],
                                     "requirement": row[1], "required_by_step": 9})
    for group, prefix, count in (("longitudinal", "P3-L", 40),
                                 ("reports", "P3-RF", 16), ("oracles", "P3-O", 24)):
        if [x["id"] for x in result[group]] != [f"{prefix}{i:02}" for i in range(1, count + 1)]:
            raise ValueError("source_catalogue_identity")
    return result


def baseline_rows(root: Path = ROOT) -> list[dict[str, Any]]:
    text = plan_text(root)
    rows = re.findall(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$", text, re.M)
    output = [{"path": p, "size_bytes": int(n), "sha256": s} for p, n, s in rows]
    if len(output) != 114 or inventory_digest(output) != INVENTORY_SHA256:
        raise ValueError("predecessor_plan_inventory_changed")
    return output


def safe_relative(path: Any) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    p = PurePosixPath(path)
    return (not p.is_absolute() and str(p) == path and
            all(x not in {"", ".", ".."} for x in p.parts) and
            not any(ord(c) < 32 or ord(c) == 127 for c in path))


def inventory_digest(rows: list[dict[str, Any]]) -> str:
    if (not isinstance(rows, list) or any(not isinstance(r, dict) or
            not safe_relative(r.get("path")) or not isinstance(r.get("sha256"), str) or
            not SHA256.fullmatch(r["sha256"]) or type(r.get("size_bytes")) is not int or
            r["size_bytes"] < 0 for r in rows)):
        raise ValueError("invalid_file_inventory")
    paths = [r["path"] for r in rows]
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate_inventory_path")
    return digest("".join(f'{r["sha256"]}  {r["path"]}\n'
                          for r in sorted(rows, key=lambda r: r["path"])).encode())


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def git_tree(rows: list[dict[str, Any]]) -> str:
    """Independently construct Git tree identity from exact paths and blob IDs."""
    tree = {}
    for row in rows:
        path, sha = row.get("path"), row.get("git_blob_sha")
        if not safe_relative(path) or not isinstance(sha, str) or not SHA1.fullmatch(sha):
            raise ValueError("invalid_git_entry")
        node = tree
        parts = PurePosixPath(path).parts
        for part in parts[:-1]:
            if part in node and not isinstance(node[part], dict):
                raise ValueError("git_file_directory_conflict")
            node = node.setdefault(part, {})
        if parts[-1] in node:
            raise ValueError("duplicate_git_entry")
        node[parts[-1]] = sha
    def encode(node):
        entries = []
        for name, value in node.items():
            is_dir = isinstance(value, dict)
            sha = encode(value) if is_dir else value
            mode = b"40000" if is_dir else b"100644"
            nb = name.encode("utf-8")
            entries.append((nb + (b"/" if is_dir else b""), mode + b" " + nb + b"\0" + bytes.fromhex(sha)))
        body = b"".join(body for _, body in sorted(entries))
        return hashlib.sha1(b"tree " + str(len(body)).encode() + b"\0" + body).hexdigest()
    return encode(tree)


def predecessor_ids(root: Path = ROOT) -> list[str]:
    record = read_json(root / "artifacts/phase3/predecessor_test_ids.json")
    ids = record.get("ids") if isinstance(record, dict) else None
    if (not isinstance(ids, list) or len(ids) != 1018 or any(not isinstance(i, str) or not METHOD.fullmatch(i) for i in ids) or
            ids != sorted(set(ids)) or
            digest(("\n".join(ids) + "\n").encode()) != PREDECESSOR_IDS_SHA256 or
            record.get("sha256") != PREDECESSOR_IDS_SHA256):
        raise ValueError("predecessor_test_identity_changed")
    return ids


def inventory_record(root: Path = ROOT) -> dict[str, Any]:
    obj = read_json(root / "artifacts/phase3/phase2_final_file_inventory.json")
    expected = baseline_rows(root)
    if (not isinstance(obj, dict) or obj.get("subject") != SUBJECT or
            obj.get("archive_sha256") != ARCHIVE_SHA256 or
            obj.get("inventory_sha256") != INVENTORY_SHA256 or
            [{k: r.get(k) for k in ("path", "size_bytes", "sha256")} for r in obj.get("files", [])] != expected or
            obj.get("git_tree_sha") != git_tree(obj.get("files", []))):
        raise ValueError("predecessor_inventory_record_changed")
    return obj


def current_identity_checks(root: Path = ROOT) -> list[dict[str, Any]]:
    checks = []
    step = read_json(root / "tests/phase3_matrix.json")["delivery"]["step"]
    for row in baseline_rows(root):
        if row["path"] == "README.md":
            continue  # Ordinary Step 1 factual update; original bytes remain pinned.
        actual = None
        try:
            path = root / row["path"]; regular_path(path)
            actual = digest(path.read_bytes())
        except (OSError, ValueError):
            pass
        expected = (STEP8_IMPLEMENTATION_PINS.get(row["path"], row["sha256"])
                    if type(step) is int and step >= 8 else row["sha256"])
        checks.append({"path": row["path"], "expected_sha256": expected,
                       "baseline_sha256": row["sha256"],
                       "identity_basis": "approved_step8_implementation_pin" if expected != row["sha256"] else "original_baseline_bytes",
                       "actual_sha256": actual, "status": "passed" if actual == expected else "failed"})
    # The approved plan, exact baseline manifest and captured method IDs are also checked.
    inventory_record(root); predecessor_ids(root)
    return checks


def load_matrix(root: Path = ROOT) -> dict[str, Any]:
    return read_json(root / "tests/phase3_matrix.json")


def binding_errors(bindings: Any, name: str, *, required: bool = False) -> list[str]:
    if not isinstance(bindings, list) or any(not isinstance(i, str) or not METHOD.fullmatch(i) for i in bindings):
        return [name + ":invalid_bindings"]
    errors = []
    if len(set(bindings)) != len(bindings): errors.append(name + ":duplicate_bindings")
    if required and not bindings: errors.append(name + ":empty_bindings")
    return errors


def _validate_matrix(matrix: Any, root: Path = ROOT) -> list[str]:
    if not isinstance(matrix, dict):
        return ["phase3_matrix_not_object"]
    expected_keys = {"schema_version", "project", "phase", "approved_plan", "delivery", "predecessor",
                     "longitudinal", "reports", "oracles", "stage_bindings", "evidence_status", "legacy_catalogue_identity"}
    errors = []
    if set(matrix) != expected_keys: errors.append("matrix_field_set")
    if matrix.get("schema_version") != "0.1" or matrix.get("phase") != 3 or matrix.get("project") != "StructDet-Bench":
        errors.append("matrix_identity")
    if matrix.get("approved_plan") != {"path": "PHASE_3_PLAN.md", "sha256": PLAN_SHA256}:
        errors.append("approved_plan_identity")
    if matrix.get("evidence_status") != "not_supplied": errors.append("empirical_evidence_is_separate")
    d = matrix.get("delivery")
    if not isinstance(d, dict): return errors + ["delivery_not_object"]
    step = d.get("step")
    if type(step) is not int or not 1 <= step <= 10: errors.append("invalid_step"); step = 1
    if d.get("phase") != 3 or d.get("final_owner_acceptance") != "not_established_by_software_tests":
        errors.append("delivery_scope_changed")
    if d.get("initialization") != {"step": 1, "counts": {"longitudinal": 40, "reports": 16, "oracles": 24},
                                    "implementation_status": "not_implemented", "test_bindings": []}:
        errors.append("initialization_history_changed")
    auth = d.get("authorization")
    if not isinstance(auth, dict) or not auth.get("owner_instruction"):
        errors.append("authorization_missing")
    expected_predecessor = {"archive_sha256": ARCHIVE_SHA256, "inventory_sha256": INVENTORY_SHA256,
                           "test_ids_sha256": PREDECESSOR_IDS_SHA256, "file_count": 114, "test_count": 1018,
                           "inventory_path": "artifacts/phase3/phase2_final_file_inventory.json",
                           "test_ids_path": "artifacts/phase3/predecessor_test_ids.json"}
    if matrix.get("predecessor") != expected_predecessor: errors.append("predecessor_identity")
    try:
        expected = plan_catalogues(root)
        from tests.phase2_helpers import expected_catalogues
        legacy = {k: digest(canonical(v)) for k, v in expected_catalogues().items()}
        if matrix.get("legacy_catalogue_identity") != legacy: errors.append("historical_catalogues_changed")
    except (OSError, ValueError, KeyError, TypeError):
        return errors + ["pinned_catalogue_unavailable"]
    for group in ("longitudinal", "reports", "oracles"):
        rows = matrix.get(group)
        if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
            errors.append(group + ":invalid_rows"); continue
        if [r.get("id") for r in rows] != [r["id"] for r in expected[group]]:
            errors.append(group + ":identities_changed"); continue
        for row, spec in zip(rows, expected[group]):
            name = row["id"]
            if any(row.get(k) != v for k, v in spec.items()): errors.append(name + ":source_row_changed")
            status = row.get("implementation_status")
            if status not in {"not_implemented", "partial", "implemented"}: errors.append(name + ":invalid_status")
            errors += binding_errors(row.get("test_bindings"), name, required=status == "implemented")
            if row.get("scope") != "L_software" or row.get("evidence_status") != "not_supplied":
                errors.append(name + ":scope_promoted")
            if status == "not_implemented" and row.get("test_bindings"):
                errors.append(name + ":unimplemented_has_bindings")
            first = int(re.findall(r"\d+", spec.get("primary_steps", "8"))[0])
            if status == "implemented" and first > step: errors.append(name + ":future_stage_implemented")
    stages = matrix.get("stage_bindings")
    if not isinstance(stages, dict) or set(stages) != {str(i) for i in range(1, 10)}:
        errors.append("stage_catalogue_changed")
    else:
        for n, r in stages.items():
            if not isinstance(r, dict): errors.append("stage_" + n + ":invalid"); continue
            status = r.get("implementation_status")
            if status not in {"not_implemented", "implemented"}: errors.append("stage_" + n + ":invalid_status")
            errors += binding_errors(r.get("test_bindings"), "stage_" + n, required=status == "implemented")
            if int(n) > step and (status != "not_implemented" or r.get("test_bindings")):
                errors.append("future_stage_bound")
    return sorted(set(errors))


def validate_matrix(matrix: Any, root: Path = ROOT) -> list[str]:
    """Malformed trusted metadata produces a failure, never an unhandled pass."""
    try:
        return _validate_matrix(matrix, root)
    except (TypeError, ValueError, KeyError, AttributeError):
        return ["matrix_shape_invalid"]


def inspect_reconciliation(record: Any, inventory: dict[str, Any]) -> dict[str, Any]:
    """Check a saved exact-baseline receipt, never claim a fresh remote lookup."""
    errors = []
    if not isinstance(record, dict):
        return {"record_consistent": False, "errors": ["phase2_reconciliation_missing"],
                "current_branch_verified": False, "assurance": "offline_saved_receipt_only"}
    for key, expected in (("schema_version", "0.1"), ("subject", SUBJECT), ("repository", REPOSITORY),
                          ("archive_sha256", ARCHIVE_SHA256), ("inventory_sha256", INVENTORY_SHA256)):
        if record.get(key) != expected: errors.append("reconciliation_" + key)
    if record.get("status") != "remote_verified": errors.append("phase2_final_sync_pending")
    if record.get("fixture_only") is not False: errors.append("remote_receipt_not_actual_evidence")
    if record.get("readback_complete") is not True: errors.append("readback_incomplete")
    if record.get("verified_files") != inventory["files"]: errors.append("remote_114_files_not_matched")
    if record.get("verified_tree") != inventory["git_tree_sha"]: errors.append("remote_tree_not_matched")
    commit = record.get("verified_commit")
    if not isinstance(commit, str) or not SHA1.fullmatch(commit): errors.append("verified_commit_missing")
    readbacks = record.get("readbacks")
    if not isinstance(readbacks, dict):
        errors.append("readbacks_missing")
    else:
        ref, obj = readbacks.get("ref"), readbacks.get("commit")
        if not isinstance(ref, dict) or not isinstance(obj, dict):
            errors.append("readback_objects_missing")
        else:
            target = ref.get("object", {})
            tree = obj.get("tree", {})
            if (not isinstance(target, dict) or not isinstance(tree, dict) or
                    ref.get("ref") != "refs/heads/" + str(record.get("branch")) or
                    target.get("type") != "commit" or target.get("sha") != commit or
                    obj.get("sha") != commit or tree.get("sha") != record.get("verified_tree")):
                errors.append("readback_link_mismatch")
    if not isinstance(record.get("readback_evidence_refs"), list) or not record.get("readback_evidence_refs"):
        errors.append("readback_evidence_missing")
    return {"record_consistent": not errors, "errors": sorted(set(errors)),
            "current_branch_verified": False, "assurance": "offline_saved_receipt_only",
            "scope": SUBJECT, "current_phase3_publication": "separate_live_audit_required"}


def match_current_observation(record: Any, observation: Any, inventory: dict[str, Any]) -> dict[str, Any]:
    """Pure comparison for a caller's independently acquired fresh read-back.

    This is not an online client and cannot authenticate a caller's assertion.
    The final delivery audit must retain the actual connector responses.
    """
    saved = inspect_reconciliation(record, inventory)
    errors = list(saved["errors"])
    if not isinstance(record, dict):
        record = {}
    if not isinstance(observation, dict) or observation.get("origin") != "connector_readback":
        errors.append("live_observation_missing")
    else:
        if observation.get("subject") != SUBJECT or observation.get("repository") != REPOSITORY:
            errors.append("live_subject_mismatch")
        if observation.get("commit") != record.get("verified_commit") or observation.get("tree") != inventory["git_tree_sha"]:
            errors.append("live_ref_moved_or_tree_changed")
        if observation.get("files") != inventory["files"] or observation.get("truncated") is not False:
            errors.append("live_file_inventory_incomplete")
        if observation.get("fixture_only") is not False or not observation.get("evidence_refs"):
            errors.append("live_evidence_not_actual")
    return {"observed_subject_matches": not errors, "errors": sorted(set(errors)),
            "scope": "supplied_connector_observation_comparison", "network_request_performed": False,
            "phase3_publication_established": False}
