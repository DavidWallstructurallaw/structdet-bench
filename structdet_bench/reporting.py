"""One redacted report tree for JSON and Markdown. No source-text execution.

The ordinary report deliberately omits raw bodies, private paths, identity
mappings and unrestricted evidence prose. Content hashes preserve local links.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from dataclasses import fields, is_dataclass
from decimal import Decimal
from fractions import Fraction
import hashlib
import html
import json
import math
from typing import Any, Mapping
from .contracts import ExactNumber, InputError, Knowledge, ThresholdToken

REPORT_VERSION = "0.1"
SECTION_TITLES = (
    "Task, evidence and permitted claim scope",
    "Attempts, positions and actual realizations",
    "Classification and validity accounting",
    "Per-cell structural metrics",
    "Fixed prefixes and reference coverage",
    "Study comparisons and uncertainty",
    "Surface and within-class diagnostics",
    "Integrity, corrections and release restrictions",
)


def plain(value: Any) -> Any:
    """Lossless JSON-compatible conversion of trusted result objects, not redaction."""
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise InputError("nonfinite_report_value")
        return value
    if isinstance(value, (ExactNumber, ThresholdToken)):
        return {"exact_decimal": value.token}
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise InputError("nonfinite_report_value")
        return {"exact_decimal": str(value)}
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if is_dataclass(value):
        return {f.name: plain(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, Mapping):
        if not all(isinstance(k, str) for k in value):
            raise InputError("invalid_report_key")
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(x) for x in value]
    raise InputError("unsupported_report_value")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(plain(value), ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def protected(value: Any) -> dict[str, Any]:
    """Retain knowledge/access states; never publish a supplied free-text value."""
    if value is None:
        return {"state": "unavailable", "reason": "record_not_supplied"}
    raw = plain(value)
    state = raw.get("state", "known") if isinstance(raw, dict) else "known"
    result = {"state": state, "record_sha256": digest(raw),
              "disclosure": "content_omitted_from_ordinary_report"}
    if isinstance(raw, dict):
        result["reason_supplied"] = bool(raw.get("reason"))
        result["evidence_refs"] = raw.get("evidence_refs", [])
        if state == "known":
            v = raw.get("value")
            if v is None or type(v) in (bool, int):
                result["value"] = v
    return result


def diagnostic_records(diagnostics: Any) -> list[dict[str, Any]]:
    """Diagnostic locations can contain private filenames; export hashed locators."""
    result = []
    for d in diagnostics:
        result.append({"code": d.code, "scope": d.scope, "severity": d.severity,
                       "source_ref": "locator-" + digest(d.source)[:24],
                       "line": d.line, "field": d.field})
    return result


def _check_tree(report: Any) -> dict[str, Any]:
    obj = plain(report)
    if (not isinstance(obj, dict) or obj.get("report_schema_version") != REPORT_VERSION
            or not isinstance(obj.get("sections"), list)
            or [s.get("title") for s in obj["sections"]] != list(SECTION_TITLES)):
        raise InputError("invalid_report_structure")
    return obj


def render_json(report: Any) -> bytes:
    obj = _check_tree(report)
    return (json.dumps(obj, ensure_ascii=True, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def _cell(value: Any) -> str:
    # Quotes/escapes also make control characters visible. No raw HTML or link
    # syntax from input can gain structural authority over this document.
    text = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    text = html.escape(text, quote=True).replace("|", "&#124;")
    return "<code>" + text + "</code>"


def render_markdown(report: Any) -> bytes:
    obj = _check_tree(report)
    lines = ["# StructDet-Bench offline measurement report", "",
             "**Scope: supplied records only. Independent scientific validation is not performed by this tool.**", ""]
    meta = {k: v for k, v in obj.items() if k != "sections"}
    lines += ["| Field | Value |", "|---|---|"]
    lines += [f"| {_cell(k)} | {_cell(v)} |" for k, v in sorted(meta.items())]
    for section in obj["sections"]:
        lines += ["", f"## {section['number']}. {section['title']}", ""]
        for key, value in sorted(section["content"].items(), key=lambda kv: (kv[0] != "scope", kv[0])):
            lines += ["### " + html.escape(key).replace("_", " "), ""]
            if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                columns = sorted({k for row in value for k in row})
                short = columns
                if len(columns) > 8:
                    priority = ("analysis_cell_id", "analysis_population", "metric_name", "sample_id", "axis", "k", "value", "unit", "result_status", "status", "reasons", "population_size")
                    short = [k for k in priority if k in columns][:8]
                    if not short:
                        short = columns[:5]
                lines += ["| " + " | ".join(_cell(k) for k in short) + " |",
                          "| " + " | ".join("---" for _ in short) + " |"]
                for row in value:
                    lines.append("| " + " | ".join(_cell(row.get(k)) for k in short) + " |")
                if short != columns:
                    lines += ["", "<details><summary>Complete structured records, including identities and limitations</summary>", ""]
                    for i, row in enumerate(value, 1):
                        lines += [f"Record {i}", "", "| Field | Value |", "|---|---|"]
                        lines += [f"| {_cell(k)} | {_cell(row.get(k))} |" for k in columns]
                        lines.append("")
                    lines += ["</details>"]
            elif isinstance(value, dict):
                lines += ["| Field | Value |", "|---|---|"]
                lines += [f"| {_cell(k)} | {_cell(v)} |" for k, v in sorted(value.items())]
            else:
                lines += [_cell(value)]
            lines.append("")
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")
