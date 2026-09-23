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
import re
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
LONGITUDINAL_REPORT_VERSION = "0.3"
LONGITUDINAL_REPORT_PROFILE = "structdet_longitudinal_v1"
LONGITUDINAL_SECTION_TITLES = (
    "Scope, source/method identities, requested quantities and evidence limitations",
    "States, stages, lineage/path, clocks, probe/trial inventories, budgets and gaps",
    "Per-state structural distributions, both views, coverage and protected-tail records",
    "Observed retention/recurrence, stage accounting and separately labeled categorical scenarios",
    "Empirical/local SHL, geometric-fit diagnostics, sensitivity, non-applicability and crossing brackets",
    "Finite-family assays, pre/post missing sets, recovery gates, ERR and partial-information states",
    "Anomalies, distributional/structural reopening, corrections and affected-result dependencies",
    "Five-condition integrity, ten EC disclosures, omitted conditions, currentness and release restrictions",
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
    if not isinstance(obj, dict):
        raise InputError("invalid_report_structure")
    version = obj.get("report_schema_version")
    if type(version) is not str or version not in {REPORT_VERSION, "0.2", LONGITUDINAL_REPORT_VERSION}:
        raise InputError("invalid_report_structure")
    longitudinal = version == LONGITUDINAL_REPORT_VERSION
    titles = LONGITUDINAL_SECTION_TITLES if longitudinal else SECTION_TITLES
    sections = obj.get("sections")
    if (not isinstance(sections, list) or len(sections) != len(titles)
            or any(not isinstance(s, dict) for s in sections)
            or [s.get("title") for s in sections] != list(titles)):
        raise InputError("invalid_report_structure")
    if version == "0.2" and obj.get("report_profile") != "structdet_comparison_v1":
        raise InputError("invalid_comparison_report_profile")
    if longitudinal:
        if obj.get("report_profile") != LONGITUDINAL_REPORT_PROFILE:
            raise InputError("invalid_longitudinal_report_profile")
        if any(type(s.get("number")) is not int or s["number"] != i
               or not isinstance(s.get("content"), dict)
               or any(re.fullmatch(r"[a-z][a-z0-9_]*", key) is None for key in s["content"])
               for i, s in enumerate(sections, 1)):
            raise InputError("invalid_report_structure")
    elif obj.get("report_profile") == LONGITUDINAL_REPORT_PROFILE:
        # A longitudinal tree cannot acquire the earlier profile's meaning.
        raise InputError("invalid_longitudinal_report_profile")
    return obj


def render_json(report: Any) -> bytes:
    obj = _check_tree(report)
    if obj['report_schema_version'] in {'0.2', LONGITUDINAL_REPORT_VERSION}:
        # Complete machine-readable tree, with shared operand/context records.
        # Compact encoding avoids multiplying the size of large paired studies.
        return canonical_bytes(obj)
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
        for key, value in sorted(section["content"].items(), key=lambda kv: ({"scope":0,"primary_results":1,"predictions":2,"sensitivity":3,"equal_block_means":4}.get(kv[0],5), kv[0])):
            lines += ["### " + html.escape(key).replace("_", " "), ""]
            if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                columns = sorted({k for row in value for k in row})
                short = columns
                if len(columns) > 8:
                    priority = ("question", "condition_pair", "view", "outcome", "block_id", "analysis_cell_id", "analysis_population", "metric_name", "sample_id", "axis", "k", "value", "unit", "result_status", "status", "reasons", "population_size")
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
