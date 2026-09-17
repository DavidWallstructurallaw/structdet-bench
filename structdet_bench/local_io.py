"""Bounded, passive local snapshots. No input execution, output writes or network.

The secure reader requires POSIX descriptor-relative no-follow operations.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
from types import MappingProxyType
from typing import Any, Mapping
from .contracts import Diagnostic, ExactNumber, InputError, SOURCE_PINS, SUPPORT_RECORD_TYPES, knowledge
from .records import Manifest, RecordEntry, inspect_references, parse_manifest, parse_record

@dataclass(frozen=True)
class ReadLimits:
    max_file_bytes: int = 16 * 1024 * 1024
    max_bundle_bytes: int = 64 * 1024 * 1024
    max_line_bytes: int = 1024 * 1024
    max_records: int = 100_000
    max_depth: int = 64
    max_number_chars: int = 1024
    def __post_init__(self) -> None:
        if any(type(v) is not int or v < 1 for v in vars(self).values()):
            raise InputError("invalid_read_limit")
        if self.max_depth > 128 or self.max_number_chars > 4096:
            raise InputError("unsupported_parser_limit")

@dataclass(frozen=True)
class ByteSnapshot:
    path: str
    size_bytes: int
    sha256: str
    content: bytes = field(repr=False)

@dataclass(frozen=True)
class ArtifactInspection:
    record_key: str
    status: str
    snapshot_path: str | None
    expected_sha256: str | None
    actual_sha256: str | None

@dataclass(frozen=True)
class LoadedBundle:
    manifest: Manifest | None = field(repr=False)
    records: tuple[RecordEntry, ...] = field(repr=False)
    snapshots: Mapping[str, ByteSnapshot] = field(repr=False)
    artifacts: tuple[ArtifactInspection, ...]
    diagnostics: tuple[Diagnostic, ...]
    limits: ReadLimits
    total_read_bytes: int
    acquisition_complete: bool
    @property
    def has_errors(self) -> bool:
        return any(d.severity == "error" for d in self.diagnostics)

def parse_json_bytes(data: bytes, limits: ReadLimits | None = None) -> Any:
    limits = limits or ReadLimits()
    if not isinstance(data, bytes):
        raise InputError("input_not_bytes")
    if len(data) > limits.max_file_bytes:
        raise InputError("file_size_exceeded")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise InputError("invalid_utf8") from exc
    if text.startswith("\ufeff"):
        raise InputError("utf8_bom_not_supported")
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > limits.max_depth:
                raise InputError("json_depth_exceeded")
        elif char in "]}":
            depth -= 1
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in items:
            if key in result:
                raise InputError("duplicate_json_key")
            result[key] = value
        return result
    def number(token: str, integer: bool = False) -> Any:
        if len(token) > limits.max_number_chars:
            raise InputError("number_token_too_long")
        return int(token) if integer else ExactNumber(token)
    def nonfinite(_: str) -> None:
        raise InputError("nonfinite_number")
    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_int=lambda t: number(t, True),
                           parse_float=number, parse_constant=nonfinite)
    except InputError:
        raise
    except (ValueError, RecursionError) as exc:
        raise InputError("invalid_json") from exc
    queue = [value]
    while queue:
        node = queue.pop()
        if isinstance(node, dict):
            queue.extend(node.keys())
            queue.extend(node.values())
        elif isinstance(node, list):
            queue.extend(node)
        elif isinstance(node, str):
            try:
                node.encode("utf-8", errors="strict")
            except UnicodeEncodeError as exc:
                raise InputError("unpaired_unicode_surrogate") from exc
    return value

def relative_parts(path: str) -> tuple[str, ...]:
    if not isinstance(path, str) or not path or path.startswith(("/", "~")):
        raise InputError("unsafe_local_path")
    if "\\" in path or "$" in path or any(ord(c) < 32 or ord(c) == 127 for c in path):
        raise InputError("unsafe_local_path")
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", path):
        raise InputError("remote_or_drive_path")
    parts = tuple(path.split("/"))
    if any(p in {"", ".", ".."} or ":" in p for p in parts):
        raise InputError("unsafe_local_path")
    return parts

class LocalReader:
    """A held root descriptor and immutable snapshots; all symlinks rejected."""
    def __init__(self, root: Path, limits: ReadLimits) -> None:
        self.limits, self.total = limits, 0
        self.snapshots: dict[str, ByteSnapshot] = {}
        self._fd: int | None = None
        if os.name != "posix" or any(not hasattr(os, k) for k in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")) or os.open not in os.supports_dir_fd:
            raise InputError("safe_local_open_unavailable")
        root = Path(root)
        if ".." in root.parts:
            raise InputError("unsafe_bundle_root")
        root = root.absolute()
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        fd = None
        try:
            fd = os.open(root.anchor, flags)
            for part in root.parts[1:]:
                nxt = os.open(part, flags, dir_fd=fd)
                os.close(fd)
                fd = nxt
            self._fd = fd
        except OSError as exc:
            if fd is not None:
                os.close(fd)
            raise InputError("unsafe_or_unreadable_bundle_root") from exc
    def __enter__(self) -> LocalReader:
        return self
    def __exit__(self, *_: Any) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
    def read(self, path: str) -> ByteSnapshot:
        parts = relative_parts(path)
        if self._fd is None:
            raise InputError("closed_local_reader")
        if path in self.snapshots:
            return self.snapshots[path]
        parent, fd = os.dup(self._fd), None
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        try:
            for part in parts[:-1]:
                nxt = os.open(part, flags, dir_fd=parent)
                os.close(parent)
                parent = nxt
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0), dir_fd=parent)
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise InputError("not_regular_file")
            if before.st_size > self.limits.max_file_bytes:
                raise InputError("file_size_exceeded")
            if self.total + before.st_size > self.limits.max_bundle_bytes:
                raise InputError("bundle_size_exceeded")
            chunks, size = [], 0
            while True:
                remain = min(self.limits.max_file_bytes - size, self.limits.max_bundle_bytes - self.total)
                chunk = os.read(fd, min(65536, remain + 1))
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                self.total += len(chunk)
                if size > self.limits.max_file_bytes:
                    raise InputError("file_size_exceeded")
                if self.total > self.limits.max_bundle_bytes:
                    raise InputError("bundle_size_exceeded")
            after = os.fstat(fd)
            identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
            if identity(before) != identity(after) or size != after.st_size:
                raise InputError("file_changed_during_read")
            data = b"".join(chunks)
            snap = ByteSnapshot(path, size, hashlib.sha256(data).hexdigest(), data)
            self.snapshots[path] = snap
            return snap
        except OSError as exc:
            raise InputError("unsafe_or_unreadable_local_file") from exc
        finally:
            if fd is not None:
                os.close(fd)
            os.close(parent)

def _lines(data: bytes, limit: int) -> Any:
    stream, index = io.BytesIO(data), 0
    while True:
        line = stream.readline(limit + 1)
        if not line:
            return
        index += 1
        if len(line) > limit:
            if not line.endswith(b"\n"):
                while True:
                    tail = stream.readline(limit + 1)
                    if not tail or tail.endswith(b"\n"):
                        break
            yield index, None
        else:
            yield index, line

def load_bundle(manifest_path: str | Path, *, limits: ReadLimits | None = None) -> LoadedBundle:
    """Inspect input, not scientific acceptance. Errors retain their actual scope."""
    limits = limits or ReadLimits()
    manifest, reader = None, None
    entries: list[RecordEntry] = []
    issues: list[Diagnostic] = []
    artifacts: list[ArtifactInspection] = []
    complete, count = True, 0
    def error(exc: InputError, scope: str, source: str, line: int | None = None) -> None:
        issues.append(Diagnostic(exc.code, scope, source, line=line))
    def hash_check(expected: Any, snap: ByteSnapshot, scope: str, source: str) -> bool:
        k = knowledge(expected)
        if k.state == "known" and k.value != snap.sha256:
            issues.append(Diagnostic("content_hash_mismatch", scope, source, "expected_sha256"))
            return False
        return True
    try:
        name = os.fspath(manifest_path)
        if not isinstance(name, str) or not name or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", name) or any(c in name for c in ("\\", "$", "~")) or any(ord(c) < 32 or ord(c) == 127 for c in name):
            raise InputError("unsafe_manifest_path")
        path = Path(name)
        if ".." in path.parts:
            raise InputError("unsafe_manifest_path")
        reader = LocalReader(path.parent, limits)
        with reader:
            snap = reader.read(path.name)
            manifest = parse_manifest(parse_json_bytes(snap.content, limits), path.name, max_records=limits.max_records)
            entries.extend(manifest.declarations)
            issues.extend(manifest.diagnostics)
            count = len(entries)
            for pin in manifest.data.get("source_pins", ()):
                if SOURCE_PINS.get(pin["source_id"]) != pin["sha256"]:
                    issues.append(Diagnostic("source_pin_mismatch", "source", path.name))
            for i, spec in enumerate(manifest.data["record_files"]):
                location = f"record_file:{i}"
                try:
                    relative_parts(spec["path"])
                    location = spec["path"]
                    if location == path.name:
                        raise InputError("manifest_listed_as_record_file")
                    snap = reader.read(location)
                    hash_check(spec["expected_sha256"], snap, "file", location)
                    rows = [(None, snap.content)] if spec["format"] == "json" else _lines(snap.content, limits.max_line_bytes)
                    allowed = ({"reference_registry"} if spec["role"] == "registry" else
                               SUPPORT_RECORD_TYPES | {"artifact"} if spec["role"] == "evidence" else
                               {"attempt", "artifact", "raw_artifact", "realization", "assignment", "validity"})
                    for line, data in rows:
                        if count >= limits.max_records:
                            raise InputError("record_count_exceeded")
                        count += 1
                        try:
                            if data is None:
                                raise InputError("jsonl_line_size_exceeded")
                            raw = parse_json_bytes(data, limits)
                            e = parse_record(raw, location, line)
                            if e.record and e.record.record_type not in allowed:
                                d = Diagnostic("record_file_role_mismatch", "record", location, line=line)
                                e = replace(e, record=None, diagnostics=(*e.diagnostics, d))
                            entries.append(e)
                            issues.extend(e.diagnostics)
                        except InputError as exc:
                            complete = False
                            d = Diagnostic(exc.code, "record", location, line=line)
                            entries.append(RecordEntry(location, line, None, None, (d,)))
                            issues.append(d)
                except InputError as exc:
                    complete = False
                    error(exc, "file", location)
            by_key: dict[tuple[str, str], list[ArtifactInspection]] = {}
            for e in entries:
                r = e.record
                if r is None or r.record_type not in {"artifact", "raw_artifact"}:
                    continue
                key = f"{r.record_type}:{r.record_id}"
                loc, exp = knowledge(r.data["content_ref"]), knowledge(r.data["expected_sha256"])
                expected = exp.value if exp.state == "known" else None
                status, actual, local = loc.state, None, None
                if loc.state != "known":
                    issues.append(Diagnostic("artifact_content_" + loc.state, "artifact", key, severity="warning"))
                elif loc.value["kind"] == "external":
                    status = "external_not_fetched"
                    issues.append(Diagnostic(status, "artifact", key, severity="warning"))
                else:
                    try:
                        local = loc.value["path"]
                        snap = reader.read(local)
                        actual = snap.sha256
                        status = "snapshot_read" if hash_check(r.data["expected_sha256"], snap, "artifact", key) else "hash_mismatch"
                    except InputError as exc:
                        complete = False
                        error(exc, "artifact", key)
                        status, local = "unavailable", None
                a = ArtifactInspection(key, status, local, expected, actual)
                artifacts.append(a)
                by_key.setdefault((r.record_type, r.record_id), []).append(a)
            for e in entries:
                if e.record and e.record.record_type == "realization":
                    r = e.record
                    ref, exp = knowledge(r.data["output_ref"]), knowledge(r.data["output_content_hash"])
                    if ref.state == "known" and exp.state == "known":
                        found = by_key.get((ref.value["record_type"], ref.value["record_id"]), [])
                        if len(found) == 1 and found[0].actual_sha256 is not None and found[0].actual_sha256 != exp.value:
                            issues.append(Diagnostic("sample_content_hash_mismatch", "sample", f"realization:{r.record_id}"))
            issues.extend(inspect_references(tuple(entries), manifest))
    except InputError as exc:
        complete = False
        error(exc, "bundle", "bundle")
    snapshots = MappingProxyType(dict(reader.snapshots)) if reader else MappingProxyType({})
    return LoadedBundle(manifest, tuple(entries), snapshots, tuple(artifacts), tuple(issues), limits, reader.total if reader else 0, complete)
