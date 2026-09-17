"""Versioned Step 2 input vocabulary. No estimators or adjudication.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re
from types import MappingProxyType
from typing import Any, Mapping

INPUT_SCHEMA_VERSION = RECORD_VERSION = "0.1"
KNOWLEDGE_STATES = frozenset({"known", "unknown", "unavailable", "not_applicable"})
ASSIGNMENT_STATES = frozenset({"assigned", "unresolved", "unclassified"})
REVIEW_STATES = frozenset({"fixture", "provisional", "adjudicated"})
VALIDITY_STATES = frozenset({"valid", "invalid", "undetermined", "not_assessed"})
RESULT_STATES = frozenset({"available", "undefined", "unavailable", "not_requested", "deferred"})
EVIDENCE_POLICIES = frozenset({"fixture_only", "adjudicated_import"})
DATA_ROLES = frozenset({"fixture", "pilot", "confirmatory", "descriptive"})
REQUIREMENT_OUTCOMES = frozenset({"satisfied_for_scope", "unsatisfied", "unresolved", "not_applicable"})
CLAIM_DISPOSITIONS = frozenset({"supported_for_scope", "restricted", "withheld"})
INTEGRITY_CONDITIONS = ("structural_validity", "external_presence", "source_integrity", "tail_retention", "corrective_capacity")
CORE_RECORD_TYPES = frozenset({"frame", "protocol", "cell", "attempt", "realization", "assignment", "validity", "artifact", "raw_artifact", "reference_registry"})
SUPPORT_RECORD_TYPES = frozenset({"evidence", "role", "lineage", "independence_assessment", "annotation", "adjudication", "domain_suite", "domain_result", "audit", "exposure", "integrity_assessment", "intake", "tail", "correction", "preregistration", "budget", "sampling_plan", "source"})
RECORD_TYPES = CORE_RECORD_TYPES | SUPPORT_RECORD_TYPES
CLASS_IDS = ("SORT-ADJ", "SORT-INS", "SORT-SEL", "SORT-MERGE", "SORT-PIVOT", "SORT-HEAP", "SORT-COUNT", "SORT-RADIX")
HERO_IDENTITIES = MappingProxyType({
    "task_id": "bounded_integer_sort", "task_version": "0.1",
    "analytic_resolution_id": "sorting_mechanism_family", "analytic_resolution_version": "0.1",
    "structural_schema_id": "sorting_mechanism_partition", "structural_schema_version": "0.1",
    "reference_registry_id": "sorting_reference_eight", "reference_registry_version": "0.1",
    "validity_rubric_ref": "bounded_integer_sort_validity_v1",
})
SOURCE_PINS = MappingProxyType({
    "SD": "357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32",
    "SI": "80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a",
    "EC": "002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950",
})
ADDENDUM_PIN = "31d2387ff2867e67e07adf60bca723b6783d0c3155b905d5477d2f844e1d9ce8"
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
DECIMAL_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z")

class InputError(ValueError):
    """Expected input failure, with bounded text independent of input contents."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)

@dataclass(frozen=True)
class Diagnostic:
    code: str
    scope: str
    source: str
    field: str = ""
    line: int | None = None
    severity: str = "error"

@dataclass(frozen=True)
class ExactNumber:
    """Fractional/exponent JSON number, preserving the original lexeme."""
    token: str
    def __post_init__(self) -> None:
        if not isinstance(self.token, str) or not DECIMAL_RE.fullmatch(self.token):
            raise InputError("invalid_number")
        try:
            if not Decimal(self.token).is_finite():
                raise InputError("nonfinite_number")
        except InvalidOperation as exc:
            raise InputError("invalid_number") from exc
    @property
    def decimal(self) -> Decimal:
        return Decimal(self.token)

@dataclass(frozen=True)
class ThresholdToken:
    token: str
    representation: str
    @property
    def decimal(self) -> Decimal:
        return Decimal(self.token)

def threshold_token(value: Any, max_chars: int = 1024) -> ThresholdToken:
    if isinstance(value, ExactNumber):
        token, source = value.token, "json_number"
    elif type(value) is int:
        token, source = str(value), "json_number"
    elif isinstance(value, str):
        token, source = value, "decimal_string"
    else:
        raise InputError("invalid_threshold")
    if len(token) > max_chars or not DECIMAL_RE.fullmatch(token):
        raise InputError("invalid_threshold")
    try:
        number = Decimal(token)
        if not number.is_finite() or not Decimal(0) < number <= Decimal(1):
            raise InputError("invalid_threshold")
    except InvalidOperation as exc:
        raise InputError("invalid_threshold") from exc
    return ThresholdToken(token, source)

def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze(v) for v in value)
    return value

def is_id(value: Any) -> bool:
    return isinstance(value, str) and ID_RE.fullmatch(value) is not None

def is_hash(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None

def in_enum(value: Any, values: Any) -> bool:
    return isinstance(value, str) and value in values

def validate_ref(value: Any) -> None:
    if not isinstance(value, Mapping) or set(value) != {"record_type", "record_id", "record_version"}:
        raise InputError("invalid_reference")
    if not in_enum(value["record_type"], RECORD_TYPES) or not is_id(value["record_id"]):
        raise InputError("invalid_reference")
    if value["record_version"] != RECORD_VERSION:
        raise InputError("unsupported_reference_version")

@dataclass(frozen=True)
class Knowledge:
    state: str
    value: Any
    reason: str | None
    evidence_refs: tuple[Any, ...]

def knowledge(value: Any) -> Knowledge:
    if not isinstance(value, Mapping) or set(value) - {"state", "value", "reason", "evidence_refs"}:
        raise InputError("invalid_knowledge")
    state, reason = value.get("state"), value.get("reason")
    if not in_enum(state, KNOWLEDGE_STATES):
        raise InputError("invalid_knowledge_state")
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise InputError("invalid_knowledge_reason")
    if state in {"unavailable", "not_applicable"} and reason is None:
        raise InputError("missing_knowledge_reason")
    if state == "known" and "value" not in value:
        raise InputError("missing_known_value")
    if state != "known" and value.get("value") is not None:
        raise InputError("value_in_unknown_state")
    refs = value.get("evidence_refs", [])
    if not isinstance(refs, (list, tuple)):
        raise InputError("invalid_evidence_refs")
    for ref in refs:
        validate_ref(ref)
    return Knowledge(state, freeze(value.get("value")), reason, tuple(freeze(r) for r in refs))
