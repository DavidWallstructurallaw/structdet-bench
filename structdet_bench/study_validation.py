"""Bounded passive sorting validation records and trusted input construction.

No candidate is imported or executed. A checked supplied observation is distinct
from an authenticated external execution or an accepted mechanism judgment.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import product, combinations
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
from typing import Any, Mapping
from .contracts import CLASS_IDS, Diagnostic, InputError, freeze
from .evidence import FUNCTIONAL_PROPERTIES, RUNTIME_STATES, _json_hash
from .local_io import ReadLimits, relative_parts
from .study_records import (LoadedStudy, RECORD_TYPES, _limits, _physical,
                            _preflight, _validate, _serialize, _attachment_records)

SUITE_ID = "sorting_functional_suite"
SUITE_VERSION = "0.1"
SUITE_SHA256 = "4b8dce8c2523bc953286bf853a0e17764e8fbaa6c71cc024b4e60d39feb17c11"
SEGMENT_COUNTS = {"V-SMALL": 781, "V-SHAPE": 18, "V-KEY": 8192, "V-STAGE": 4}
FAMILIES = ("ADJ", "INS", "SEL", "MERGE", "PIVOT", "HEAP", "COUNT", "RADIX")
WITNESSES = ((7, 1, 6, 2, 5, 3, 4, 0), (3, 1, 3, 0, 2, 0, 2, 1),
             (256, 1, 4095, 255, 16, 0, 257, 4094), (0, 1, 2, 3, 7, 6, 5, 4))
RUBRIC_ID = "bounded_integer_sort_validity_v1"


def sorting_inputs() -> list[dict[str, Any]]:
    """Materialize only trusted integer descriptions, retaining repeated values."""
    rows = []
    def add(segment, values, index, width):
        rows.append({"test_id": f"{segment}-{index:0{width}d}",
                     "segment": segment, "input": list(values)})
    index = 0
    for length in range(5):
        for values in product([0, 1, 255, 256, 4095], repeat=length):
            index += 1
            add("V-SMALL", values, index, 4)
    index = 0
    for length in (8, 64, 256):
        boundary = [255, 256, 4095, 0, 257, 1, 4094, 16]
        patterns = [list(range(length)), list(reversed(range(length))),
                    [0 if i % 2 == 0 else 4095 for i in range(length)],
                    [256] * length, [(73 * i + 19) % 4096 for i in range(length)],
                    [boundary[i % 8] for i in range(length)]]
        for values in patterns:
            index += 1
            add("V-SHAPE", values, index, 2)
    for value in range(4096):
        add("V-KEY", [value], 2 * value + 1, 4)
        add("V-KEY", [4095 - value, value], 2 * value + 2, 4)
    for index, values in enumerate(WITNESSES, 1):
        add("V-STAGE", values, index, 2)
    return rows


def sorting_manifest() -> dict[str, Any]:
    rows = sorting_inputs()
    return {"version": "0.1", "tests": rows, "sha256": _json_hash(rows)}


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _diag(code: str, path: str = "", severity: str = "error") -> Diagnostic:
    return Diagnostic(code, "study_validation", "study_validation", path, severity=severity)


@dataclass(frozen=True)
class Inspection:
    diagnostics: tuple[Diagnostic, ...]
    @property
    def has_errors(self):
        return any(d.severity == "error" for d in self.diagnostics)
    @property
    def exit_code(self):
        return 2 if self.has_errors else 0


@dataclass(frozen=True)
class ManifestInspection(Inspection):
    test_count: int = 0
    sha256: str | None = None


def validate_sorting_manifest(raw_or_bytes: Any, limits: ReadLimits | None = None) -> ManifestInspection:
    """Accept exact legacy manifest or canonical tests array, inspecting all IDs."""
    issues = []
    count, digest = 0, None
    try:
        limits = _limits(limits)
        raw = _physical(raw_or_bytes, limits) if isinstance(raw_or_bytes, bytes) else raw_or_bytes
        _preflight(raw, limits)
        if not isinstance(raw_or_bytes, bytes):
            _physical(_serialize(raw), limits)
        rows = raw
        declared = None
        if isinstance(raw, Mapping):
            if set(raw) != {"version", "tests", "sha256"} or raw.get("version") != "0.1":
                raise InputError("functional_manifest_malformed")
            rows, declared = raw["tests"], raw["sha256"]
        _validate(rows, {"array": {"object": {"test_id": "id", "segment": "id",
                                              "input": {"array": "nonnegative"}}}}, "tests", issues)
        if issues:
            return ManifestInspection(tuple(issues))
        count = len(rows)
        if count > limits.max_records:
            raise InputError("record_count_exceeded")
        ids = [r["test_id"] for r in rows]
        if len(ids) != len(set(ids)):
            issues.append(_diag("functional_manifest_duplicate_id"))
        if count != 8995:
            issues.append(_diag("functional_manifest_count_mismatch"))
        expected = sorting_inputs()
        if any(a["test_id"] != b["test_id"] or a["segment"] != b["segment"]
               for a, b in zip(rows, expected)):
            issues.append(_diag("functional_manifest_identity_or_order_mismatch"))
        if any(tuple(a["input"]) != tuple(b["input"]) for a, b in zip(rows, expected)):
            issues.append(_diag("functional_manifest_construction_mismatch"))
        digest = _json_hash(rows)
        if digest != SUITE_SHA256 or (declared is not None and declared != digest):
            issues.append(_diag("functional_manifest_hash_mismatch"))
    except (InputError, ValueError, TypeError, RecursionError) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "functional_manifest_malformed"))
    return ManifestInspection(tuple(issues), count, digest)


def materialize_sorting_inputs(destination: str | Path) -> dict[str, Any]:
    """Publish a fixed two-file directory atomically without replacing any path.

    POSIX no-follow directory walking and Linux renameat2(RENAME_NOREPLACE) are
    required. An unavailable primitive fails closed; no candidate path is read.
    """
    target = Path(destination).absolute()
    if ".." in target.parts or target.name in {"", ".", ".."}:
        raise InputError("unsafe_local_path")
    relative_parts(target.name)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open("/", flags)
    stage = None
    stage_fd = None
    try:
        for component in target.parent.parts[1:]:
            relative_parts(component)
            child = os.open(component, flags, dir_fd=parent)
            os.close(parent)
            parent = child
        try:
            os.stat(target.name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise InputError("output_exists")
        rows = sorting_inputs()
        data = _canonical(rows)
        digest = hashlib.sha256(data).hexdigest()
        if digest != SUITE_SHA256:
            raise InputError("internal_suite_identity_mismatch")
        manifest = {"version": "0.1", "suite_id": SUITE_ID, "suite_version": SUITE_VERSION,
                    "test_count": len(rows), "segment_counts": dict(SEGMENT_COUNTS),
                    "inputs_path": "sorting_inputs.json", "sha256": digest}
        outputs = {"sorting_inputs.json": data, "sorting_manifest.json": _canonical(manifest)}
        stage = ".sorting-stage-" + secrets.token_hex(12)
        os.mkdir(stage, 0o700, dir_fd=parent)
        stage_fd = os.open(stage, flags, dir_fd=parent)
        for name, content in outputs.items():
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=stage_fd)
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fchmod(stream.fileno(), 0o644)
                os.fsync(stream.fileno())
        os.fchmod(stage_fd, 0o755)
        os.fsync(stage_fd)
        libc = ctypes.CDLL(None, use_errno=True)
        rename = getattr(libc, "renameat2", None)
        if rename is None:
            raise InputError("atomic_directory_publish_unavailable")
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(parent, os.fsencode(stage), parent, os.fsencode(target.name), 1) != 0:
            error = ctypes.get_errno()
            if error == errno.EEXIST:
                raise InputError("output_exists")
            raise InputError("atomic_directory_publish_failed")
        stage = None
        os.fsync(parent)
        return {"directory": str(target), "test_count": 8995, "sha256": digest,
                "files": [{"path": name, "sha256": hashlib.sha256(content).hexdigest(),
                           "size_bytes": len(content)} for name, content in outputs.items()]}
    except OSError as exc:
        raise InputError("unsafe_or_unavailable_output_path") from exc
    finally:
        if stage_fd is not None:
            if stage is not None:
                for name in ("sorting_inputs.json", "sorting_manifest.json"):
                    try:
                        os.unlink(name, dir_fd=stage_fd)
                    except FileNotFoundError:
                        pass
            os.close(stage_fd)
        if stage is not None:
            os.rmdir(stage, dir_fd=parent)
        os.close(parent)


_REF = lambda kind: {"reference": [kind]}
_K = lambda spec: {"knowledge": spec}
_SCOPE = {"object": {"claim_id": "id", "task_id": {"literal": "bounded_integer_sort"},
                      "task_version": {"literal": "0.1"}}}
VIOLATION_PROPERTIES = (*FUNCTIONAL_PROPERTIES, "syntax", "prohibited_capability", "exception", "output_protocol")
_VIOLATION_SCHEMA = {"object": {"property": {"enum": list(VIOLATION_PROPERTIES)},
    "observed_violation": {"literal": True},
    "evidence_refs": {"array": {"reference": sorted(RECORD_TYPES)}}}}
_OBSERVATION_SCHEMA = {"object": {"test_id": "id",
    "runtime_status": {"enum": sorted(RUNTIME_STATES)},
    "property_checks": {"object": {p: _K("bool") for p in FUNCTIONAL_PROPERTIES}},
    "violation": _K(_VIOLATION_SCHEMA)}}
VALIDATION_PACKET_SCHEMA = {"object": {
    "validation_packet_version": {"literal": "0.1"}, "packet_id": "id",
    "study_id": "id", "study_version": "id", "receipt_ref": _REF("validation_receipt"),
    "artifact_ref": _REF("artifact"), "artifact_sha256": "hash", "suite_sha256": "hash",
    "scope": _SCOPE, "rubric_id": {"literal": RUBRIC_ID},
    "environment_configuration_sha256": "hash", "environment_image_sha256": "hash",
    "environment_id": "id", "oracle_id": "id", "oracle_source_sha256": "hash",
    "environment_check": {"object": {
        "containment_status": {"enum": ["passed", "failed", "not_assessed"]},
        "accommodated_class_ids": {"array": "class_id"},
        "isolation_review_ref": _REF("human_review"), "oracle_review_ref": _REF("human_review")}},
    "observations": {"array": _OBSERVATION_SCHEMA}}}


@dataclass(frozen=True)
class ValidationPacket(Inspection):
    data: Any = field(default=None, repr=False)


def parse_validation_packet_bytes(data: bytes, limits: ReadLimits | None = None) -> ValidationPacket:
    issues = []
    raw = None
    try:
        limits = _limits(limits)
        raw = _physical(data, limits)
        _validate(raw, VALIDATION_PACKET_SCHEMA, "validation_packet", issues)
        if not issues and len(raw["observations"]) > limits.max_records:
            issues.append(_diag("record_count_exceeded"))
        if not issues:
            ids = [r["test_id"] for r in raw["observations"]]
            if len(ids) != len(set(ids)):
                issues.append(_diag("coverage_duplicate_test_id"))
            classes = raw["environment_check"]["accommodated_class_ids"]
            if len(classes) != len(set(classes)):
                issues.append(_diag("duplicate_environment_class_id"))
        if raw is not None:
            raw = freeze(raw)
    except (InputError, TypeError, ValueError, RecursionError) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_validation_packet"))
    return ValidationPacket(tuple(issues), raw)


@dataclass(frozen=True)
class ValidationAssessment(Inspection):
    receipt_id: str = ""
    validity_status: str = "undetermined"
    coverage_status: str = "not_performed"
    observed_count: int = 0
    expected_count: int = 8995
    missing_ids: tuple[str, ...] = ()
    duplicate_ids: tuple[str, ...] = ()
    mechanism_status: str = "unresolved"
    mechanism_observations: tuple[Any, ...] = field(default=(), repr=False)
    evidence_policy: str = "unknown"
    material_role: str = "unknown"
    qualification_status: str = "external_authentication_required"
    substantive_validation_performed: bool = False


def _known(value):
    return value.get("value") if isinstance(value, Mapping) and value.get("state") == "known" else None


def inspect_validation_receipt(loaded: LoadedStudy, receipt_id: str,
                               limits: ReadLimits | None = None) -> ValidationAssessment:
    """Inspect actual bounded snapshots, never promote summaries to full logs.

    Returned validity is the supported state of supplied records under this
    bounded rubric. External authenticity and human conduct are not established.
    """
    issues = []
    def bad(code, path="", severity="error"):
        issues.append(_diag(code, path, severity))
    expected = sorting_inputs()
    expected_ids = tuple(r["test_id"] for r in expected)
    row_index = {r["test_id"]: (i, r["segment"]) for i, r in enumerate(expected)}
    observed_ids, duplicates, mechanism = [], [], ()
    policy, role, validity, coverage = "unknown", "unknown", "undetermined", "not_performed"
    try:
        limits = _limits(limits)
        if not isinstance(loaded, LoadedStudy) or loaded.packet is None:
            raise InputError("study_packet_unavailable")
        if loaded.has_errors or loaded.packet.has_errors:
            issues.extend(loaded.diagnostics)
            raise InputError("study_packet_rejected")
        study = loaded.packet.data
        policy, role = study["evidence_policy"], study["material_role"]
        records = {r["record_id"]: r for r in study["records"]}
        rec = records.get(receipt_id)
        if rec is None or rec["record_type"] != "validation_receipt":
            raise InputError("validation_receipt_missing")
        if rec["scope"]["task_id"] != "bounded_integer_sort" or rec["scope"]["task_version"] != "0.1":
            raise InputError("validation_scope_mismatch")
        mechanism = tuple(rec["mechanism_observations"])
        inventory = {p["packet_id"]: p for p in study["packet_inventory"]}
        acquired = {p.packet_id: p for p in loaded.attachments}
        inspected_packets = {}
        total_records = len(study["records"])
        total_bytes = sum(len(snap.content) for snap in loaded.snapshots.values())
        if total_bytes != loaded.total_read_bytes:
            raise InputError("validation_snapshot_inventory_mismatch")
        if total_bytes > min(limits.max_bundle_bytes, study["import_budget"]["max_total_bytes"]):
            raise InputError("budget_exceeded_partition_required")
        inventory_paths = {_known(p["location"])["path"]: p for p in inventory.values()
                           if _known(p["location"]) and _known(p["location"])["kind"] == "local"}
        for path, acquired_snapshot in loaded.snapshots.items():
            if (len(acquired_snapshot.content) != acquired_snapshot.size_bytes
                    or hashlib.sha256(acquired_snapshot.content).hexdigest() != acquired_snapshot.sha256):
                raise InputError("validation_snapshot_hash_mismatch")
            if acquired_snapshot.size_bytes > limits.max_file_bytes:
                raise InputError("file_size_exceeded")
            if path in inventory_paths:
                form = inventory_paths[path]["format"]
                total_records += _attachment_records(acquired_snapshot.content, form, limits)
            else:
                _physical(acquired_snapshot.content, limits)
        if total_records > min(limits.max_records, study["import_budget"]["max_total_records"]):
            raise InputError("budget_exceeded_partition_required")
        def snapshot(packet_id):
            nonlocal total_records, total_bytes
            if packet_id in inspected_packets:
                return inspected_packets[packet_id]
            entry, status = inventory.get(packet_id), acquired.get(packet_id)
            if entry is None or status is None or status.status != "snapshot_verified":
                bad("validation_attachment_unavailable", severity="warning")
                inspected_packets[packet_id] = None
                return None
            location = _known(entry["location"])
            if location is None or location["kind"] != "local":
                bad("validation_attachment_unavailable", severity="warning")
                inspected_packets[packet_id] = None
                return None
            snap = loaded.snapshots.get(location["path"])
            if (snap is None or hashlib.sha256(snap.content).hexdigest() != snap.sha256
                    or len(snap.content) != snap.size_bytes or snap.sha256 != _known(entry["sha256"])
                    or snap.size_bytes != _known(entry["size_bytes"])):
                raise InputError("validation_snapshot_hash_mismatch")
            if snap.size_bytes > limits.max_file_bytes or total_bytes > min(limits.max_bundle_bytes, study["import_budget"]["max_total_bytes"]):
                raise InputError("budget_exceeded_partition_required")
            inspected_packets[packet_id] = snap
            return snap
        def ref_ok(ref):
            target = records.get(ref["record_id"])
            if target and target["record_type"] in {"validation_receipt", "human_review", "adjudication"}:
                if target["artifact_ref"] != rec["artifact_ref"] or target["artifact_sha256"] != rec["artifact_sha256"]:
                    return False
            return bool(target and target["record_type"] == ref["record_type"]
                        and target["record_version"] == ref["record_version"]
                        and target["study_id"] == rec["study_id"]
                        and target["study_version"] == rec["study_version"]
                        and target["scope"] == rec["scope"])
        def review_ok(ref):
            if ref is None or not ref_ok(ref):
                return False
            review = records[ref["record_id"]]
            return bool(review["record_type"] == "human_review"
                and review["artifact_ref"] == rec["artifact_ref"]
                and review["artifact_sha256"] == rec["artifact_sha256"]
                and review["reviewer"]["entity_kind"] == "human"
                and review["submission_stage"] in {"initial", "revision"}
                and _known(review["reviewer"]["qualifications"])
                and _known(review["independence"]["declared_independent"]) is True
                and _known(review["judgment"]["rationale"])
                and review["judgment"]["evidence_refs"])
        suite = rec["suite"]
        if (suite["suite_id"] != SUITE_ID or suite["suite_version"] != SUITE_VERSION
                or suite["manifest_sha256"] != SUITE_SHA256 or suite["expected_test_count"] != 8995):
            raise InputError("validation_suite_identity_mismatch")
        source = records[rec["artifact_ref"]["record_id"]]
        content = _known(source["content"])
        source_snap = snapshot(content["packet_id"]) if content else None
        source_ok = source_snap is not None and source_snap.sha256 == rec["artifact_sha256"]
        if source_snap is not None and not source_ok:
            raise InputError("validation_artifact_hash_mismatch")
        if not source_ok:
            bad("validation_artifact_unavailable", severity="warning")
        manifest_ids = []
        for packet_id, entry in inventory.items():
            if _known(entry["sha256"]) == SUITE_SHA256:
                snap = snapshot(packet_id)
                if snap is not None:
                    checked = validate_sorting_manifest(snap.content, limits)
                    issues.extend(checked.diagnostics)
                    if not checked.has_errors:
                        manifest_ids.append(packet_id)
                        total_records += checked.test_count - 1
                        if total_records > min(limits.max_records, study["import_budget"]["max_total_records"]):
                            raise InputError("budget_exceeded_partition_required")
        if not manifest_ids:
            bad("validation_manifest_attachment_unavailable", severity="warning")
        segments = rec["coverage"]["segments"]
        if (tuple(s["segment_id"] for s in segments) != tuple(SEGMENT_COUNTS)
                or any(s["expected_count"] != SEGMENT_COUNTS[s["segment_id"]] for s in segments)):
            raise InputError("validation_segment_inventory_mismatch")
        packet_ids = list(dict.fromkeys(pid for s in segments for pid in s["full_log_packets"]))
        observations = []
        packets = {}
        environment_ok = True
        for packet_id in packet_ids:
            snap = snapshot(packet_id)
            if snap is None:
                continue
            if inventory[packet_id]["format"] != "json":
                raise InputError("validation_packet_format_mismatch")
            packet = parse_validation_packet_bytes(snap.content, limits)
            issues.extend(packet.diagnostics)
            if packet.has_errors:
                continue
            header = packet.data
            expected_header = {"packet_id": packet_id, "study_id": rec["study_id"],
                "study_version": rec["study_version"],
                "receipt_ref": {"record_type": "validation_receipt", "record_id": rec["record_id"], "record_version": rec["record_version"]},
                "artifact_ref": rec["artifact_ref"], "artifact_sha256": rec["artifact_sha256"],
                "suite_sha256": SUITE_SHA256, "scope": rec["scope"], "rubric_id": RUBRIC_ID}
            if any(header[k] != value for k, value in expected_header.items()):
                raise InputError("validation_packet_association_mismatch")
            for field_name, bound in (("environment_configuration_sha256", _known(rec["environment"]["configuration_sha256"])),
                                      ("environment_image_sha256", _known(rec["environment"]["image_sha256"])),
                                      ("environment_id", _known(rec["environment"]["environment_id"])),
                                      ("oracle_id", _known(rec["oracle"]["oracle_id"])),
                                      ("oracle_source_sha256", _known(rec["oracle"]["source_sha256"]))):
                if bound is None:
                    environment_ok = False
                elif header[field_name] != bound:
                    raise InputError("validation_environment_or_oracle_mismatch")
            env = header["environment_check"]
            if (env["containment_status"] != "passed" or set(env["accommodated_class_ids"]) != set(CLASS_IDS)):
                environment_ok = False
            for field_name, bound in (("isolation_review_ref", _known(rec["environment"]["isolation_review_ref"])),
                                      ("oracle_review_ref", _known(rec["oracle"]["review_ref"]))):
                if bound is None:
                    environment_ok = False
                elif env[field_name] != bound:
                    raise InputError("validation_review_association_mismatch")
            total_records += len(header["observations"]) - 1
            if total_records > min(limits.max_records, study["import_budget"]["max_total_records"]):
                raise InputError("budget_exceeded_partition_required")
            packets[packet_id] = header
            observations.extend((packet_id, row) for row in header["observations"])
        observed_ids = [row["test_id"] for _, row in observations]
        seen = set()
        for test_id in observed_ids:
            if test_id in seen and test_id not in duplicates:
                duplicates.append(test_id)
            seen.add(test_id)
        if duplicates:
            bad("coverage_duplicate_test_id")
        if any(test_id not in row_index for test_id in observed_ids):
            bad("validation_unknown_test_id")
        else:
            indices = [row_index[tid][0] for tid in observed_ids]
            if indices != sorted(indices):
                bad("validation_test_order_mismatch")
        for segment in segments:
            actual = tuple(row["test_id"] for pid, row in observations
                           if pid in segment["full_log_packets"] and row["test_id"] in row_index
                           and row_index[row["test_id"]][1] == segment["segment_id"])
            if actual != tuple(segment["observed_ids"]):
                missing_segment_packets = any(pid not in packets for pid in segment["full_log_packets"])
                bad("validation_declared_coverage_mismatch", severity="warning" if missing_segment_packets else "error")
        coverage = "complete" if tuple(observed_ids) == expected_ids else "partial" if observed_ids else "not_performed"
        if rec["coverage"]["declared_status"] != coverage:
            bad("validation_declared_coverage_mismatch", severity="warning" if len(packets) < len(packet_ids) else "error")
        # Summaries are optional, but a supplied known assertion must agree with
        # the actual linked row. They never create observations or coverage.
        actual_by_id = {row["test_id"]: (pid, row) for pid, row in observations}
        for declared in rec["trusted_observations"]:
            actual = actual_by_id.get(declared["test_id"])
            if actual is None:
                bad("validation_trusted_observation_unmatched")
                continue
            pid, row = actual
            declared_packet = _known(declared["evidence_packet_id"])
            if declared_packet is not None and declared_packet != pid:
                bad("validation_trusted_observation_association_mismatch")
            runtime = row["runtime_status"]
            row_pass = runtime == "completed" and all(_known(row["property_checks"][p]) is True for p in FUNCTIONAL_PROPERTIES) and row["violation"]["state"] == "not_applicable"
            matches = {"pass": row_pass,
                "violation": _known(row["violation"]) is not None,
                "harness_failure": runtime in {"harness_error", "containment_failure", "oracle_error"},
                "resource_exhausted": runtime in {"timeout", "memory_limit"},
                "undetermined": not row_pass and _known(row["violation"]) is None}
            if not matches[declared["outcome"]]:
                bad("validation_trusted_observation_contradiction")
        conformance = rec["conformance_review"]
        conformance_ok = bool(conformance["outcome"] == "satisfied_for_scope"
            and _known(conformance["basis"]) and conformance["evidence_refs"]
            and review_ok(_known(conformance["reviewer_ref"])))
        environment_ok = bool(environment_ok
            and all(_known(rec["environment"][f]) for f in ("environment_id", "image_sha256", "configuration_sha256"))
            and all(_known(rec["oracle"][f]) for f in ("oracle_id", "source_sha256"))
            and review_ok(_known(rec["environment"]["isolation_review_ref"]))
            and review_ok(_known(rec["oracle"]["review_ref"])))
        if not conformance_ok:
            bad("validation_conformance_unresolved", severity="warning")
        if not environment_ok:
            bad("validation_environment_or_oracle_unresolved", severity="warning")
        complete_pass = bool(observations) and all(row["runtime_status"] == "completed"
            and all(_known(row["property_checks"][p]) is True for p in FUNCTIONAL_PROPERTIES)
            and row["violation"]["state"] == "not_applicable" for _, row in observations)
        decisive = False
        for packet_id, row in observations:
            violation = _known(row["violation"])
            if violation is None:
                continue
            prop = violation["property"]
            expected_runtime = {"syntax": "exception", "prohibited_capability": "prohibited_capability",
                                "exception": "exception", "output_protocol": "output_protocol_failure"}
            supported = (row["runtime_status"] == "completed" and _known(row["property_checks"][prop]) is False
                         if prop in FUNCTIONAL_PROPERTIES else row["runtime_status"] == expected_runtime[prop])
            if not supported or not violation["evidence_refs"] or not all(ref_ok(r) for r in violation["evidence_refs"]):
                bad("validation_counterexample_unsubstantiated")
                continue
            declared = [c for c in rec["counterexamples"] if c["observation_packet_id"] == packet_id
                        and c["input_packet_id"] in manifest_ids and c["test_id"] == row["test_id"]
                        and c["violation"] == prop]
            if declared and row["test_id"] in row_index:
                decisive = True
            else:
                bad("validation_counterexample_association_mismatch")
        for declared in rec["counterexamples"]:
            if not any(pid == declared["observation_packet_id"] and row["test_id"] == declared["test_id"]
                       and _known(row["violation"]) is not None
                       and _known(row["violation"])["property"] == declared["violation"]
                       and declared["input_packet_id"] in manifest_ids for pid, row in observations):
                bad("validation_counterexample_association_mismatch")
        errors = any(d.severity == "error" for d in issues)
        if not errors and source_ok and manifest_ids and environment_ok:
            if decisive:
                validity = "invalid"
            elif (coverage == "complete" and complete_pass and conformance_ok
                  and rec["termination"] == "completed" and rec["harness_status"] == "ok"):
                validity = "valid"
        if rec["validity_status"] in {"valid", "invalid"} and validity != rec["validity_status"]:
            bad("validation_claim_not_established", severity="warning")
        if not observed_ids and rec["validity_status"] == "not_assessed":
            validity = "not_assessed"
        if mechanism:
            bad("mechanism_observations_require_separate_review", severity="warning")
        else:
            bad("functional_evidence_does_not_certify_mechanism", severity="warning")
    except (InputError, KeyError, TypeError, ValueError) as exc:
        bad(exc.code if isinstance(exc, InputError) else "invalid_validation_receipt")
    if any(d.severity == "error" for d in issues):
        validity = "undetermined"
    observed_set = set(observed_ids)
    return ValidationAssessment(tuple(issues), receipt_id, validity, coverage, len(observed_ids), 8995,
        tuple(tid for tid in expected_ids if tid not in observed_set), tuple(duplicates),
        "unresolved", mechanism, policy, role,
        "fixture_only" if policy == "fixture_only" else "external_authentication_required", False)


_REFERENCE_SPECIFICATIONS = {'core_catalog.json': {'actual_artifact_count': 0,
                       'actual_human_review_count': 0,
                       'catalog_id': 'sorting_core_32',
                       'catalog_version': '0.1',
                       'empirical_validation_performed': False,
                       'material_role': 'reference_specification',
                       'required_initial_item_reviews': 64,
                       'roles': [{'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'sweep direction',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-ADJ'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-ADJ-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'sweep direction',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-ADJ'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-ADJ-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-ADJ'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-ADJ-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'linear/binary insertion search',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-INS'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-INS-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'linear/binary insertion search',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-INS'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-INS-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-INS'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-INS-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'min/max selection',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-SEL'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-SEL-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'min/max selection',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-SEL'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-SEL-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-SEL'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-SEL-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'top-down/bottom-up merge',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-MERGE'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-MERGE-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'top-down/bottom-up merge',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-MERGE'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-MERGE-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-MERGE'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-MERGE-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'two-/three-way pivot',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-PIVOT'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-PIVOT-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'two-/three-way pivot',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-PIVOT'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-PIVOT-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-PIVOT'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-PIVOT-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'min/max heap',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-HEAP'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-HEAP-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'min/max heap',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-HEAP'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-HEAP-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-HEAP'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-HEAP-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'count expansion/cumulative placement',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-COUNT'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-COUNT-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'count expansion/cumulative placement',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-COUNT'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-COUNT-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-COUNT'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-COUNT-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'least-/most-significant-digit refinement',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-RADIX'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-RADIX-A',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'least-/most-significant-digit refinement',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-RADIX'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'mechanism_membership_argument',
                                                   'constitutive_relation_review',
                                                   'complete_validity_evidence',
                                                   'two_nontrivial_witness_shapes'],
                                  'role_id': 'CORE-RADIX-B',
                                  'role_kind': 'positive_variant',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Concrete interface, boundary, copy or transport '
                                                      'defect; inspect whether the defining mechanism '
                                                      'remains identifiable.',
                                  'evidence_refs': [],
                                  'proposed_family': {'state': 'known', 'value': 'SORT-RADIX'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'decisive_counterexample',
                                                'constitutive_relation_review',
                                                   'preserved_mechanism_or_case_revision'],
                                  'role_id': 'CORE-RADIX-D',
                                  'role_kind': 'identifiable_defect',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Insertion implemented by adjacent swaps versus sweep '
                                                      'organization.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X01',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Fresh selection versus a maintained heap.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X02',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Positional merge versus pivot partition.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X03',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Full-key counting advertised as one-pass radix.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X04',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'An unregistered general hybrid.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X05',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'An eligible gap-scheduled strategy outside this '
                                                      'registry.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X06',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'Opaque built-in sorting delegation.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X07',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'},
                                 {'accepted_assignment': {'reason': 'Planned reference specification. Actual '
                                                                    'artifact or evidence has not been '
                                                                    'supplied.',
                                                          'state': 'unknown'},
                                  'accepted_validity': {'reason': 'Planned reference specification. Actual '
                                                                  'artifact or evidence has not been '
                                                                  'supplied.',
                                                        'state': 'unknown'},
                                  'artifact_ref': {'reason': 'Planned reference specification. Actual '
                                                             'artifact or evidence has not been supplied.',
                                                   'state': 'unknown'},
                                  'desired_contrast': 'A misleading or unused algorithm fragment with an '
                                                      'incomplete decisive path.',
                                  'evidence_refs': [],
                                  'proposed_family': {'reason': 'Planned reference specification. Actual '
                                                                'artifact or evidence has not been supplied.',
                                                      'state': 'unknown'},
                                  'requirements': ['two_distinct_human_initial_judgments',
                                                   'origin_and_exposure',
                                                   'actual_boundary_evidence',
                                                   'legitimate_unresolved_outcomes_preserved'],
                                  'role_id': 'CORE-X08',
                                  'role_kind': 'boundary_negative',
                                  'role_status': 'missing'}],
                       'version': '0.1'},
 'descriptor_reviews.json': {'common_assignment_rule': 'Assign only when a uniquely applicable descriptor '
                                                       'organizes all relevant reachable branches; names, '
                                                       'comments, output agreement and hypothetical repaired '
                                                       'programs cannot select a family.',
                             'common_permitted_operations': 'Empty/singleton handling, direct size-two '
                                                            'comparison, copying, and a verified '
                                                            'already-ordered fast path are permitted only '
                                                            'without a second general sorting strategy.',
                             'counterfactual_requirements': [{'artifact_refs': [],
                                                              'evidence_refs': [],
                                                              'kind': 'same_class_renaming_and_helper_layout',
                                                              'status': 'missing'},
                                                             {'artifact_refs': [],
                                                              'evidence_refs': [],
                                                              'kind': 'mechanism_changing_substitution',
                                                              'status': 'missing'}],
                             'descriptor_pairs': [{'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-ADJ',
                                                   'mandatory_distinction': True,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-INS'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-ADJ',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-SEL'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-ADJ',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-MERGE'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-ADJ',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-PIVOT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-ADJ',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-HEAP'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-ADJ',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-COUNT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-ADJ',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-RADIX'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-INS',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-SEL'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-INS',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-MERGE'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-INS',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-PIVOT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-INS',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-HEAP'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-INS',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-COUNT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-INS',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-RADIX'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-SEL',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-MERGE'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-SEL',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-PIVOT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-SEL',
                                                   'mandatory_distinction': True,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-HEAP'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-SEL',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-COUNT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-SEL',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-RADIX'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-MERGE',
                                                   'mandatory_distinction': True,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-PIVOT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-MERGE',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-HEAP'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-MERGE',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-COUNT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-MERGE',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-RADIX'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-PIVOT',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-HEAP'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-PIVOT',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-COUNT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-PIVOT',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-RADIX'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-HEAP',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-COUNT'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-HEAP',
                                                   'mandatory_distinction': False,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-RADIX'},
                                                  {'distinguishing_argument': {'reason': 'Planned reference '
                                                                                         'specification. '
                                                                                         'Actual artifact or '
                                                                                         'evidence has not '
                                                                                         'been supplied.',
                                                                               'state': 'unknown'},
                                                   'evidence_refs': [],
                                                   'left_class_id': 'SORT-COUNT',
                                                   'mandatory_distinction': True,
                                                   'review_status': 'missing',
                                                   'right_class_id': 'SORT-RADIX'}],
                             'descriptors': [{'class_id': 'SORT-ADJ',
                                              'constitutive_rule': 'Repeated traversals compare adjacent '
                                                                   'positions and move local inversions '
                                                                   'across an active interval until the '
                                                                   'interval is ordered or a no-change '
                                                                   'condition is reached. The '
                                                                   'sweep/active-interval organization '
                                                                   'determines progress.',
                                              'discriminating_evidence': 'Inspect sweep-level progress and '
                                                                         'adjacent inversion handling. '
                                                                         'Adjacent swaps inside placement of '
                                                                         'one incoming value into a growing '
                                                                         'sorted prefix are evaluated under '
                                                                         '`SORT-INS`, rather than labeled by '
                                                                         'the swap instruction alone.',
                                              'family': 'adjacent sweep',
                                              'permitted_variation': 'Left/right direction, alternating '
                                                                     'directions, shrinking boundaries, and '
                                                                     'an early no-change exit.'},
                                             {'class_id': 'SORT-INS',
                                              'constitutive_rule': 'A contiguous ordered prefix grows by '
                                                                   'selecting the next not-yet-inserted '
                                                                   'value and locating/inserting it within '
                                                                   'that prefix, preserving prefix order '
                                                                   'before the next value is admitted.',
                                              'discriminating_evidence': 'Establish the outer prefix-growth '
                                                                         'invariant and placement '
                                                                         'dependency. Gap-scheduled passes '
                                                                         'over interleaved subsequences are '
                                                                         'outside this descriptor. An '
                                                                         'insertion helper inside another '
                                                                         'full-size strategy does not create '
                                                                         'a second observation.',
                                              'family': 'sorted-prefix insertion',
                                              'permitted_variation': 'Shifts versus adjacent moves; linear '
                                                                     'versus binary search for the insertion '
                                                                     'location; equivalent list '
                                                                     'representations.'},
                                             {'class_id': 'SORT-SEL',
                                              'constitutive_rule': 'Each output/frontier step obtains the '
                                                                   'next minimum or maximum by examining the '
                                                                   'current unsorted region afresh, then '
                                                                   'removes or places that value and '
                                                                   'advances the ordered region.',
                                              'discriminating_evidence': 'Trace or inspect a fresh extremum '
                                                                         'selection from the remaining '
                                                                         'region. A maintained '
                                                                         'heap/tournament used to obtain the '
                                                                         'next extremum belongs to '
                                                                         '`SORT-HEAP` when its descriptor '
                                                                         'holds.',
                                              'family': 'rescanning extremum selection',
                                              'permitted_variation': 'Minimum/maximum direction; swapping '
                                                                     'into a boundary or removing into a '
                                                                     'fresh output list.'},
                                             {'class_id': 'SORT-MERGE',
                                              'constitutive_rule': 'Subsets/runs are ordered and then '
                                                                   'combined by choosing among run frontiers '
                                                                   "while preserving each run's internal "
                                                                   'order. Progressive ordered merging '
                                                                   'performs the general recombination.',
                                              'discriminating_evidence': 'Establish ordered runs, their '
                                                                         'formation, and frontier-based '
                                                                         'merge decisions. Natural-run '
                                                                         'discovery may reverse a monotone '
                                                                         'descending run; using another '
                                                                         'general sorter on runs larger than '
                                                                         'two is a hybrid under this schema.',
                                              'family': 'ordered-run merge',
                                              'permitted_variation': 'Top-down or bottom-up organization, '
                                                                     'explicit stack, natural-run discovery, '
                                                                     'and equivalent merge storage.'},
                                             {'class_id': 'SORT-PIVOT',
                                              'constitutive_rule': 'A key-selected pivot partitions a '
                                                                   'nontrivial region by comparisons to that '
                                                                   'pivot; recursively or iteratively '
                                                                   'sorting the resulting regions and '
                                                                   'placing/combining them establishes '
                                                                   'order.',
                                              'discriminating_evidence': 'Establish pivot-dependent '
                                                                         'partition predicates, subproblem '
                                                                         'boundaries, and recombination. '
                                                                         'Position-based splitting followed '
                                                                         'by ordered merging is '
                                                                         '`SORT-MERGE`. Bit/digit-defined '
                                                                         'decomposition without a '
                                                                         'key-selected pivot is considered '
                                                                         'under `SORT-RADIX`.',
                                              'family': 'pivot partition',
                                              'permitted_variation': 'Pivot selection; two-way/three-way '
                                                                     'partition; in-place/copying; '
                                                                     'recursion/explicit stack.'},
                                             {'class_id': 'SORT-HEAP',
                                              'constitutive_rule': 'A heap-order relation is established and '
                                                                   'maintained while successive root extrema '
                                                                   'are extracted or placed to build the '
                                                                   'sorted result.',
                                              'discriminating_evidence': 'Establish heap-order maintenance '
                                                                         'and its role in each extraction. A '
                                                                         'fresh full-region extremum scan '
                                                                         'with no maintained heap is '
                                                                         '`SORT-SEL`. External heap '
                                                                         'libraries are prohibited by the '
                                                                         'task.',
                                              'family': 'maintained heap extraction',
                                              'permitted_variation': 'Min/max heap, bottom-up/incremental '
                                                                     'heap construction, local array/tree '
                                                                     'representation, and output direction.'},
                                             {'class_id': 'SORT-COUNT',
                                              'constitutive_rule': 'Full key values address '
                                                                   'frequency/position information; scanning '
                                                                   'the full-key order, with multiplicity '
                                                                   'expansion or cumulative positions, '
                                                                   'determines the result.',
                                              'discriminating_evidence': 'Establish whole-key addressing and '
                                                                         'numeric-order traversal. Sorting a '
                                                                         "dictionary's distinct keys with "
                                                                         'another general sorting mechanism '
                                                                         'is a hybrid. A single distribution '
                                                                         'over the complete key is counting '
                                                                         'at this resolution, even when '
                                                                         'described as one-pass radix.',
                                              'family': 'full-key frequency ordering',
                                              'permitted_variation': 'Fixed 4096-key or observed-range '
                                                                     'table, ascending key-range scan, '
                                                                     'frequency expansion or cumulative '
                                                                     'placement.'},
                                             {'class_id': 'SORT-RADIX',
                                              'constitutive_rule': 'Proper parts of the key drive multiple '
                                                                   'reachable refinement stages or '
                                                                   'digit-recursive subdivisions; '
                                                                   'significance/order-preservation '
                                                                   'relations combine them into full-key '
                                                                   'order. Full ordering is not decided by '
                                                                   'one complete-key table.',
                                              'discriminating_evidence': 'Verify at least one permitted '
                                                                         'nontrivial input exercises '
                                                                         'multiple proper-digit stages and '
                                                                         'the significance/ordering '
                                                                         'dependencies. Whole-key counting '
                                                                         'in one stage is `SORT-COUNT`. A '
                                                                         'counting operation used only '
                                                                         'inside proper-digit refinement is '
                                                                         'a component of this family, not a '
                                                                         'separate full-key mechanism.',
                                              'family': 'multi-stage digit refinement',
                                              'permitted_variation': 'Least-significant-first passes with '
                                                                     'required order preservation; '
                                                                     'most-significant-first subdivision; '
                                                                     'explicit bit/digit widths; equivalent '
                                                                     'bucket/count storage.'}],
                             'empirical_validation_performed': False,
                             'material_role': 'reference_specification',
                             'schema_id': 'sorting_mechanism_partition',
                             'schema_version': '0.1',
                             'version': '0.1'},
 'preservation_quotas.json': {'empirical_validation_performed': False,
                              'interpretation': 'Reference-design protection does not establish empirical '
                                                'rarity or superiority.',
                              'material_role': 'reference_specification',
                              'quotas': [{'class_id': 'SORT-ADJ',
                                          'planned_defect_role': 'CORE-ADJ-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': [],
                                          'protected_witness_ids': [],
                                          'required_positive_roles': ['CORE-ADJ-A', 'CORE-ADJ-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1},
                                         {'class_id': 'SORT-INS',
                                          'planned_defect_role': 'CORE-INS-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': [],
                                          'protected_witness_ids': [],
                                          'required_positive_roles': ['CORE-INS-A', 'CORE-INS-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1},
                                         {'class_id': 'SORT-SEL',
                                          'planned_defect_role': 'CORE-SEL-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': [],
                                          'protected_witness_ids': [],
                                          'required_positive_roles': ['CORE-SEL-A', 'CORE-SEL-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1},
                                         {'class_id': 'SORT-MERGE',
                                          'planned_defect_role': 'CORE-MERGE-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': [],
                                          'protected_witness_ids': [],
                                          'required_positive_roles': ['CORE-MERGE-A', 'CORE-MERGE-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1},
                                         {'class_id': 'SORT-PIVOT',
                                          'planned_defect_role': 'CORE-PIVOT-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': [],
                                          'protected_witness_ids': [],
                                          'required_positive_roles': ['CORE-PIVOT-A', 'CORE-PIVOT-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1},
                                         {'class_id': 'SORT-HEAP',
                                          'planned_defect_role': 'CORE-HEAP-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': [],
                                          'protected_witness_ids': [],
                                          'required_positive_roles': ['CORE-HEAP-A', 'CORE-HEAP-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1},
                                         {'class_id': 'SORT-COUNT',
                                          'planned_defect_role': 'CORE-COUNT-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': ['CORE-X04'],
                                          'protected_witness_ids': ['W-03'],
                                          'required_positive_roles': ['CORE-COUNT-A', 'CORE-COUNT-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1},
                                         {'class_id': 'SORT-RADIX',
                                          'planned_defect_role': 'CORE-RADIX-D',
                                          'positive_variant_minimum': 2,
                                          'protect_version_history': True,
                                          'protected_boundary_role_ids': ['CORE-X04'],
                                          'protected_witness_ids': ['W-03'],
                                          'required_positive_roles': ['CORE-RADIX-A', 'CORE-RADIX-B'],
                                          'retention_status': 'missing',
                                          'reviewed_defect_or_boundary_minimum': 1}],
                              'version': '0.1'},
 'readiness_gaps.json': {'actual_initial_item_reviews': 0,
                         'actual_input_count': 8995,
                         'candidate_execution_performed': False,
                         'core_construction': 'not_started',
                         'empirical_validation_performed': False,
                         'external_validation': 'not_started',
                         'gaps': [{'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'actual_core_material'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'origin_and_exposure'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'independent_human_initial_reviews'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'descriptor_pair_reviews'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'witness_observations'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'same_class_counterfactuals'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'mechanism_changing_substitutions'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'oracle_implementation_review'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'artifact_input_association_review'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'containment_review'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'all_eight_families_accommodated'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'execution_authorization'},
                                  {'evidence_refs': [],
                                   'outcome': 'unresolved',
                                   'requirement_id': 'full_external_validation_logs'}],
                         'human_review': 'not_started',
                         'material_role': 'reference_specification',
                         'missing_core_role_count': 32,
                         'required_initial_item_reviews': 64,
                         'scope': 'Specifications and passive import checks only. No 32-program validation, '
                                  'empirical taxonomy qualification or external conduct is claimed.',
                         'version': '0.1'},
 'witnesses.json': {'empirical_validation_performed': False,
                    'material_role': 'reference_specification',
                    'version': '0.1',
                    'witnesses': [{'evidence_refs': [],
                                   'input': [7, 1, 6, 2, 5, 3, 4, 0],
                                   'observation_status': 'not_performed',
                                   'purpose': 'Multiple placements, sweeps, selections, partitions and '
                                              'merges, avoiding already-ordered trivial paths.',
                                   'witness_id': 'W-01'},
                                  {'evidence_refs': [],
                                   'input': [3, 1, 3, 0, 2, 0, 2, 1],
                                   'observation_status': 'not_performed',
                                   'purpose': 'Duplicate transport, equal-pivot handling, count multiplicity '
                                              'and repeated-key dependencies.',
                                   'witness_id': 'W-02'},
                                  {'evidence_refs': [],
                                   'input': [256, 1, 4095, 255, 16, 0, 257, 4094],
                                   'observation_status': 'not_performed',
                                   'purpose': 'Whole-key ordering versus proper-digit refinement across '
                                              'digit boundaries.',
                                   'witness_id': 'W-03'},
                                  {'evidence_refs': [],
                                   'input': [0, 1, 2, 3, 7, 6, 5, 4],
                                   'observation_status': 'not_performed',
                                   'purpose': 'Run formation, sorted-prefix progress and adaptation or '
                                              'branch inspection.',
                                   'witness_id': 'W-04'}]}}


def reference_specifications() -> dict[str, Any]:
    """Return fresh approved role specifications, never completed references."""
    return json.loads(json.dumps(_REFERENCE_SPECIFICATIONS))


def inspect_reference_specifications(specifications: Any, limits: ReadLimits | None = None) -> Inspection:
    issues = []
    try:
        limits = _limits(limits)
        _preflight(specifications, limits)
        _physical(_serialize(specifications), limits)
        if not isinstance(specifications, Mapping) or set(specifications) != set(_REFERENCE_SPECIFICATIONS):
            raise InputError("reference_specification_inventory_mismatch")
        for name, expected in _REFERENCE_SPECIFICATIONS.items():
            # Canonical text also distinguishes native boolean and integer values.
            if _serialize(specifications[name]) != _serialize(expected):
                issues.append(_diag("reference_specification_mismatch", name))
    except (InputError, ValueError, TypeError) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_reference_specification"))
    return Inspection(tuple(issues))
