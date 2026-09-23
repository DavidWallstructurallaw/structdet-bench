"""Bounded passive extraction of the registered five-position response format.

All ranges address the original bytes. This module never parses or runs Python,
repairs a response, chooses among competing blocks, or assigns validity/classes.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re

from .contracts import Diagnostic, InputError
from .local_io import ReadLimits
from .study_records import _limits

RULE_VERSION = "hero_candidates_v1"
_ATX = re.compile(rb"^ {0,3}#{1,6}(?:[ \t]+|$)")
_HEADING = re.compile(rb"^ {0,3}### Candidate ([0-9]+)[ \t]*$")
_CANDIDATE = re.compile(rb"^ {0,3}#{1,6}[ \t]+candidate\b", re.I)
_OPEN = re.compile(rb"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")


def _diagnostic(code, position=None, severity="error"):
    path = "response" if position is None else f"positions[{position - 1}]"
    return Diagnostic(code, "study_extraction", "study_extraction", path,
                      severity=severity)


@dataclass(frozen=True)
class ByteRange:
    """Zero-based, end-exclusive offsets in the original raw response."""
    start: int
    end: int

    def as_dict(self):
        return {"start": self.start, "end": self.end}


@dataclass(frozen=True)
class ExtractionPosition:
    within_group_index: int
    selection: str
    heading: str | None
    fence: str | None
    byte_range: ByteRange | None
    content: bytes | None = field(repr=False)
    completion_status: str = "unknown"
    limitations: tuple[str, ...] = ()

    @property
    def sha256(self):
        return None if self.content is None else hashlib.sha256(self.content).hexdigest()

    def as_dict(self):
        return {"within_group_index": self.within_group_index,
                "selection": self.selection, "heading": self.heading,
                "fence": self.fence,
                "byte_range": None if self.byte_range is None else self.byte_range.as_dict(),
                "sha256": self.sha256,
                "size_bytes": None if self.content is None else len(self.content),
                "completion_status": self.completion_status,
                "limitations": list(self.limitations)}


@dataclass(frozen=True)
class ExtractionExtra:
    heading: str | None
    byte_range: ByteRange
    content: bytes = field(repr=False)
    reason: str = "unselected_material"

    @property
    def sha256(self):
        return hashlib.sha256(self.content).hexdigest()

    def as_dict(self):
        return {"heading": self.heading, "byte_range": self.byte_range.as_dict(),
                "sha256": self.sha256, "size_bytes": len(self.content),
                "reason": self.reason}


@dataclass(frozen=True)
class ExtractionResult:
    rule_version: str
    raw_response_sha256: str | None
    size_bytes: int | None
    positions: tuple[ExtractionPosition, ...]
    extras: tuple[ExtractionExtra, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    group_complete: bool = False
    order_established: bool = False

    @property
    def has_errors(self):
        return any(item.severity == "error" for item in self.diagnostics)

    @property
    def realized_count(self):
        return sum(row.selection == "selected" for row in self.positions)

    def as_dict(self):
        """JSON-ready receipt. Content stays in raw bytes; ranges/hashes bind it."""
        return {"rule_version": self.rule_version,
                "raw_response_sha256": self.raw_response_sha256,
                "size_bytes": self.size_bytes,
                "positions": [row.as_dict() for row in self.positions],
                "extras": [row.as_dict() for row in self.extras],
                "diagnostics": [{"code": row.code, "field": row.field,
                                 "severity": row.severity} for row in self.diagnostics],
                "group_complete": self.group_complete,
                "order_established": self.order_established,
                "realized_count": self.realized_count,
                "functional_validity_assessed": False,
                "structural_membership_assessed": False}


def result_dict(result: ExtractionResult):
    return result.as_dict()


def _lines(raw, limits, start=0):
    """Scan without allocating an unbounded list for newline-heavy responses."""
    while start < len(raw):
        stop = raw.find(b"\n", start)
        end = len(raw) if stop < 0 else stop + 1
        if end - start > limits.max_line_bytes:
            raise InputError("line_size_exceeded")
        body = raw[start:end]
        if body.endswith(b"\n"):
            body = body[:-1]
            if body.endswith(b"\r"):
                body = body[:-1]
        yield start, end, body
        start = end


def _heading(line, limits):
    candidate = bool(_CANDIDATE.match(line))
    numbers = re.findall(rb"[0-9]+", line) if candidate else []
    if any(len(number) > limits.max_number_chars for number in numbers):
        raise InputError("number_token_too_long")
    mentions = {int(number) for number in numbers if len(number) <= 2}
    mentions.intersection_update(range(1, 6))
    match = _HEADING.fullmatch(line)
    number = None
    if match:
        token = match.group(1)
        # No enormous integer conversion is needed to identify the five slots.
        if len(token) == 1 and token in (b"1", b"2", b"3", b"4", b"5"):
            number = int(token)
        elif token == b"0" or not token.startswith(b"0"):
            return {"heading": line.decode("utf-8"), "number": None,
                    "affected": set(), "reason": "unrequested_candidate_heading"}
    if number is not None:
        return {"heading": line.decode("utf-8"), "number": number,
                "affected": set(), "reason": None}
    return {"heading": line.decode("utf-8"), "number": None,
            "affected": (mentions or set(range(1, 6))) if candidate else set(),
            "reason": "ambiguous_candidate_heading" if candidate else "unexpected_heading"}


def _sections(raw, limits):
    sections = []
    current = {"heading": None, "number": None, "affected": set(),
               "reason": "response_preamble", "start": 0, "blocks": [],
               "ambiguous": False}
    opened = None
    pending = False
    events = 5  # The permanent plan inventory also consumes the logical budget.

    def charge():
        nonlocal events
        events += 1
        if events > limits.max_records:
            raise InputError("record_count_exceeded")

    if events > limits.max_records:
        raise InputError("record_count_exceeded")
    for start, end, line in _lines(raw, limits):
        if opened is not None:
            stripped = line.lstrip(b" ")
            indentation = len(line) - len(stripped)
            run = len(stripped) - len(stripped.lstrip(opened["marker"]))
            closes = (indentation <= 3 and run >= opened["length"]
                      and not stripped[run:].strip(b" \t"))
            if closes:
                charge()
                current["blocks"].append({**opened, "end": start,
                                           "close_end": end, "truncated": False})
                opened, pending = None, False
            elif _CANDIDATE.match(line):
                # Closed-fence comments are source bytes, including their digit
                # strings. Interpret potential headings only if closure is absent.
                pending = True
            continue
        if _ATX.match(line):
            charge()
            current["end"] = start
            sections.append(current)
            current = {**_heading(line, limits), "start": end, "blocks": [],
                       "ambiguous": False}
            continue
        match = _OPEN.fullmatch(line)
        if match:
            marker, info = match.groups()
            # Backticks in a backtick info string cannot open a Markdown fence.
            if marker.startswith(b"`") and b"`" in info:
                continue
            charge()
            opened = {"marker": marker[:1], "length": len(marker),
                      "open_start": start, "start": end,
                      "fence": line.decode("utf-8"),
                      "python": info.strip(b" \t").lower() == b"python"}
    current["end"] = len(raw)
    if opened is not None:
        if pending:
            current["ambiguous"] = True
            if current["number"] is not None:
                current["affected"].add(current["number"])
            for _, _, line in _lines(raw, limits, opened["start"]):
                if not _CANDIDATE.match(line):
                    continue
                charge()
                heading = _heading(line, limits)
                if heading["number"] is not None:
                    current["affected"].add(heading["number"])
                current["affected"].update(heading["affected"])
        current["blocks"].append({**opened, "end": len(raw),
                                   "close_end": len(raw), "truncated": True})
    sections.append(current)
    return sections


def extract_response_bytes(raw: bytes, *, limits: ReadLimits | None = None) -> ExtractionResult:
    """Identify original text at fixed positions without constructing missing samples.

    Physical/encoding failures return five withheld plan rows and no realization.
    A unique malformed body can be selected as exact incomplete material; its
    extraction failure never asserts a program's scientific or functional label.
    """
    raw_hash = None
    size = len(raw) if isinstance(raw, bytes) else None
    try:
        limits = _limits(limits)
        if not isinstance(raw, bytes):
            raise InputError("input_not_bytes")
        if len(raw) > limits.max_file_bytes:
            raise InputError("file_size_exceeded")
        if len(raw) > limits.max_bundle_bytes:
            raise InputError("bundle_size_exceeded")
        raw_hash = hashlib.sha256(raw).hexdigest()
        try:
            raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise InputError("invalid_utf8") from exc
        if raw.startswith(b"\xef\xbb\xbf"):
            raise InputError("utf8_bom_not_supported")
        sections = _sections(raw, limits)
    except InputError as exc:
        rows = tuple(ExtractionPosition(i, "withheld", None, None, None, None,
                                        "unknown", (exc.code,)) for i in range(1, 6))
        return ExtractionResult(RULE_VERSION, raw_hash, size, rows,
                                diagnostics=(_diagnostic(exc.code),))

    issues, extras = [], []
    by_number = {i: [] for i in range(1, 6)}
    affected = set()
    observed_order = []
    for section in sections:
        affected.update(section["affected"])
        if section["number"] is not None:
            by_number[section["number"]].append(section)
            observed_order.append(section["number"])
        if section["ambiguous"]:
            issues.append(_diagnostic("unclosed_fence_heading_ambiguity", section["number"]))
        elif section["reason"] and (section["heading"] is not None
                                     or raw[section["start"]:section["end"]].strip()):
            issues.append(_diagnostic(section["reason"]))
    for number, occurrences in by_number.items():
        if len(occurrences) > 1:
            affected.add(number)
            issues.append(_diagnostic("duplicate_candidate_heading", number))

    rows = []
    for number in range(1, 6):
        occurrences = by_number[number]
        if number in affected:
            rows.append(ExtractionPosition(number, "withheld", None, None, None, None,
                                            "unknown", ("ambiguous_position",)))
            continue
        if not occurrences:
            rows.append(ExtractionPosition(number, "missing", None, None, None, None,
                                            "unknown", ("candidate_not_emitted",)))
            issues.append(_diagnostic("missing_candidate_heading", number))
            continue
        section = occurrences[0]
        blocks = section["blocks"]
        limitations = []
        fence = None
        status = "failed"
        start, end = section["start"], section["end"]
        if len(blocks) != 1:
            limitations.append("missing_code_fence" if not blocks else "multiple_code_fences")
        elif not blocks[0]["python"]:
            limitations.append("non_python_code_fence")
            fence = blocks[0]["fence"]
        else:
            block = blocks[0]
            fence = block["fence"]
            start, end = block["start"], block["end"]
            status = "truncated" if block["truncated"] else "complete"
            if block["truncated"]:
                limitations.append("unclosed_final_code_fence")
            if (raw[section["start"]:block["open_start"]].strip(b" \t\r\n")
                    or raw[block["close_end"]:section["end"]].strip(b" \t\r\n")):
                limitations.append("prose_outside_code_fence")
        content = raw[start:end]
        if not content.strip():
            limitations.append("empty_candidate_body")
        for code in limitations:
            issues.append(_diagnostic(code, number))
        rows.append(ExtractionPosition(number, "selected", section["heading"], fence,
                                        ByteRange(start, end), content, status,
                                        tuple(limitations)))

    for section in sections:
        number = section["number"]
        reason = section["reason"]
        if section["ambiguous"]:
            reason = "unclosed_fence_heading_ambiguity"
        elif number in affected:
            reason = "ambiguous_position_occurrence"
        elif number is not None:
            continue
        content = raw[section["start"]:section["end"]]
        if section["heading"] is None and not content.strip():
            continue
        extras.append(ExtractionExtra(section["heading"],
                                      ByteRange(section["start"], section["end"]),
                                      content, reason or "unselected_material"))

    order = not affected and observed_order == sorted(set(observed_order))
    if observed_order != sorted(set(observed_order)):
        issues.append(_diagnostic("candidate_heading_order"))
    complete = (order and not issues and all(row.selection == "selected"
                                            and row.completion_status == "complete" for row in rows))
    return ExtractionResult(RULE_VERSION, raw_hash, size, tuple(rows), tuple(extras),
                            tuple(issues), complete, order)
