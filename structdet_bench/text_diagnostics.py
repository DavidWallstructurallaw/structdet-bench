"""Pinned lexical-trigram and matched-pair diagnostics on passive snapshots.

MET 8-9; PHASE_2_PLAN 3.2-3.3, 4.3, Step 3. No label inference,
file access, program execution, condition contrast, or statistical interval.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from typing import Any, Mapping
import unicodedata

from .contracts import InputError, freeze, is_id, knowledge, validate_ref
from .local_io import LoadedBundle
from .populations import CellPopulations, Ratio

PROXY_VERSION = "surface_lexical_trigram_jaccard_v1"
CATEGORY_VERSION = WHITE_SPACE_VERSION = "15.1.0"
# Unicode PropList-15.1.0, White_Space: 25 code points in 11 intervals.
# https://www.unicode.org/Public/15.1.0/ucd/PropList.txt
WHITE_SPACE_RANGES = ((9, 13), (32, 32), (133, 133), (160, 160),
                     (5760, 5760), (8192, 8202), (8232, 8232),
                     (8233, 8233), (8239, 8239), (8287, 8287), (12288, 12288))
BEGIN = ("boundary", "begin")
END = ("boundary", "end")
SURFACE = "surface_lexical_trigram_distance"
WITHIN = "within_class_realization_diversity_proxy"
STRUCTURAL = "structural_pair_non_equivalence"
METHOD_FIELDS = ("extraction_rule_version", "encoding", "proxy_version",
                 "unicode_category_version", "white_space_version", "white_space_sha256")
LIMIT_FIELDS = ("max_lexical_units", "max_pairs", "max_trigram_visits", "max_exact_bits")


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# This digest identifies this versioned interval encoding, not the whole source file.
WHITE_SPACE_SHA256 = _hash(_canonical({"property": "White_Space", "unicode_version":
                                     WHITE_SPACE_VERSION, "ranges": WHITE_SPACE_RANGES}))


@dataclass(frozen=True)
class TextMethod:
    extraction_rule_version: str
    encoding: str = "utf-8"
    proxy_version: str = PROXY_VERSION
    unicode_category_version: str = CATEGORY_VERSION
    white_space_version: str = WHITE_SPACE_VERSION
    white_space_sha256: str = WHITE_SPACE_SHA256

    def __post_init__(self) -> None:
        if any(not isinstance(getattr(self, key), str) for key in METHOD_FIELDS):
            raise InputError("text_method_value_type")
        if not is_id(self.extraction_rule_version):
            raise InputError("extraction_version_unresolved")

    @property
    def identity(self) -> Mapping[str, str]:
        return freeze({key: getattr(self, key) for key in METHOD_FIELDS})


def method_from_record(record: Mapping[str, Any]) -> TextMethod:
    """No host-table fallback for unknown or mismatching registered identities."""
    if not isinstance(record, Mapping) or set(record) != set(METHOD_FIELDS):
        raise InputError("text_method_field_set")
    values = {}
    for name in METHOD_FIELDS:
        if name in {"encoding", "proxy_version"}:
            values[name] = record[name]
        else:
            state = knowledge(record[name])
            if state.state != "known":
                raise InputError("text_method_metadata_unresolved")
            values[name] = state.value
    return TextMethod(**values)


@dataclass(frozen=True)
class DiagnosticLimits:
    max_lexical_units: int = 100_000
    max_pairs: int = 100_000
    max_trigram_visits: int = 100_000_000
    max_exact_bits: int = 131_072

    def __post_init__(self) -> None:
        if any(type(getattr(self, key)) is not int or not 1 <= getattr(self, key) <= 2**31-1
               for key in LIMIT_FIELDS):
            raise InputError("invalid_text_diagnostic_limits")


def limits_from_record(record: Mapping[str, Any]) -> DiagnosticLimits:
    if not isinstance(record, Mapping) or set(record) != set(LIMIT_FIELDS):
        raise InputError("text_limit_field_set")
    return DiagnosticLimits(**record)


@dataclass
class WorkBudget:
    """One explicitly shared run budget; no hidden reset between cells/views.

    A logical visit is one input-set element charged per compared pair. Set
    intersection/union counts share that charge; within-class means reuse it.
    This is a deterministic workload convention, not a hardware-operation count.
    """
    max_trigram_visits: int
    visits: int = 0

    def __post_init__(self) -> None:
        if (type(self.max_trigram_visits) is not int or not 1 <= self.max_trigram_visits <= 2**31-1
                or type(self.visits) is not int or not 0 <= self.visits <= self.max_trigram_visits):
            raise InputError("invalid_text_work_budget")


def _method_reasons(method: TextMethod) -> tuple[str, ...]:
    reasons = []
    if method.encoding != "utf-8": reasons.append("unsupported_text_encoding")
    if method.proxy_version != PROXY_VERSION: reasons.append("unsupported_proxy_version")
    if method.unicode_category_version != CATEGORY_VERSION: reasons.append("unicode_category_version_mismatch")
    if unicodedata.unidata_version != CATEGORY_VERSION: reasons.append("host_unicode_category_version_mismatch")
    if method.white_space_version != WHITE_SPACE_VERSION: reasons.append("white_space_version_mismatch")
    if method.white_space_sha256 != WHITE_SPACE_SHA256: reasons.append("white_space_identity_mismatch")
    return tuple(reasons)


@dataclass(frozen=True)
class Tokenization:
    status: str
    reasons: tuple[str, ...]
    original_sha256: str
    original_bytes: int
    normalized_sha256: str | None
    lexical_unit_count: int | None
    observed_lexical_units: int
    trigram_sha256: str | None
    units: tuple[str, ...] = field(repr=False)
    trigrams: frozenset = field(repr=False)
    method: TextMethod
    resource_failure: bool = False
    lexical_unit: str = "surface_lexical_unit"


def tokenize_text(data: bytes, method: TextMethod, *, limits: DiagnosticLimits | None = None) -> Tokenization:
    """Tokenize the whole submitted region or return an explicit failure.

    Lexical payloads are inspection-only fields, excluded from default repr.
    Callers must not export them as ordinary public reports.
    """
    if not isinstance(data, bytes) or not isinstance(method, TextMethod):
        raise InputError("invalid_text_component")
    limits = DiagnosticLimits() if limits is None else limits
    if not isinstance(limits, DiagnosticLimits): raise InputError("invalid_text_diagnostic_limits")
    initial = dict(original_sha256=_hash(data), original_bytes=len(data), normalized_sha256=None,
                   lexical_unit_count=None, observed_lexical_units=0, trigram_sha256=None,
                   units=(), trigrams=frozenset(), method=method)
    reasons = _method_reasons(method)
    if reasons: return Tokenization("unavailable", reasons, **initial)
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return Tokenization("ineligible", ("invalid_utf8",), **initial)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    initial["normalized_sha256"] = _hash(normalized.encode("utf-8"))
    if not normalized:
        initial["lexical_unit_count"] = 0
        return Tokenization("ineligible", ("empty_emitted_text",), **initial)
    units: list[str] = []
    start: int | None = None
    for i, char in enumerate(normalized):
        word = char == "_" or unicodedata.category(char)[0] in ("L", "N")
        if word:
            if start is None: start = i
            continue
        if start is not None:
            units.append(normalized[start:i]); start = None
        cp = ord(char)
        if not any(a <= cp <= b for a, b in WHITE_SPACE_RANGES): units.append(char)
        if len(units) > limits.max_lexical_units:
            initial["observed_lexical_units"] = len(units)
            return Tokenization("unavailable", ("max_lexical_units_exceeded",), **initial, resource_failure=True)
    if start is not None: units.append(normalized[start:])
    initial["observed_lexical_units"] = len(units)
    if len(units) > limits.max_lexical_units:
        return Tokenization("unavailable", ("max_lexical_units_exceeded",), **initial, resource_failure=True)
    initial["lexical_unit_count"] = len(units)
    if not units: return Tokenization("ineligible", ("whitespace_only_text",), **initial)
    padded = [BEGIN] + [("text", unit) for unit in units] + [END]
    trigrams = frozenset(zip(padded, padded[1:], padded[2:]))
    initial.update(units=tuple(units), trigrams=trigrams, trigram_sha256=_hash(_canonical(sorted(trigrams))))
    return Tokenization("eligible", (), **initial)


@dataclass(frozen=True)
class DiagnosticValue:
    metric_name: str
    result_status: str
    value: float | None
    exact_ratio: tuple[int, int] | None
    pair_denominator: int | None
    reasons: tuple[str, ...] = ()
    unit: str = "dimensionless_distinct_observation_pair_mean"
    metric_definition_version: str = "MET-0.2"
    uncertainty_status: str = "not_estimated"


def _value(name: str, fraction: Fraction | None, denominator: int | None,
           reason: str | None = None, *, unavailable: bool = False) -> DiagnosticValue:
    return DiagnosticValue(name, "unavailable" if unavailable else "undefined" if fraction is None else "available",
                           float(fraction) if fraction is not None else None,
                           (fraction.numerator, fraction.denominator) if fraction is not None else None,
                           denominator, (reason,) if reason else ())


def _checked(value: Fraction, limits: DiagnosticLimits) -> Fraction:
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > limits.max_exact_bits:
        raise InputError("max_exact_bits_exceeded")
    return value


@dataclass(frozen=True)
class SampleText:
    sample_id: str
    class_id: str
    status: str
    reasons: tuple[str, ...]
    completion_status: str | None
    assignment_id: str | None
    assignment_version: str | None
    group_id: str | None
    attempt_id: str | None
    artifact_ref: tuple[str, str, str] | None = None
    snapshot_locator_sha256: str | None = None
    original_sha256: str | None = None
    original_bytes: int | None = None
    normalized_sha256: str | None = None
    trigram_sha256: str | None = None
    lexical_unit_count: int | None = None
    observed_lexical_units: int = 0
    trigram_count: int | None = None
    span_status: str = "not_supplied"
    resource_failure: bool = False


@dataclass(frozen=True)
class PairObservation:
    left_sample_id: str
    right_sample_id: str
    intersection_size: int
    union_size: int
    distance_ratio: tuple[int, int]
    structurally_different: bool
    same_call: bool | None


@dataclass(frozen=True)
class ClassDiagnostic:
    class_id: str
    population_count: int
    eligible_sample_ids: tuple[str, ...]
    pair_count: int | None
    mean: DiagnosticValue


@dataclass(frozen=True)
class TextDiagnostics:
    cell_id: str
    analysis_population: str
    status: str
    reasons: tuple[str, ...]
    method: TextMethod
    limits: DiagnosticLimits
    population_size: int | None
    population_sample_ids: tuple[str, ...]
    eligible_sample_ids: tuple[str, ...]
    eligible_count: int | None
    text_subset_complete: bool
    proxy_text_coverage: Ratio
    pair_count: int | None
    same_class_pair_count: int | None
    samples: tuple[SampleText, ...]
    pairs: tuple[PairObservation, ...]
    class_diagnostics: tuple[ClassDiagnostic, ...]
    results: Mapping[str, DiagnosticValue]
    text_sci_ratio: tuple[int, int] | None
    dependency_counts: Mapping[str, int]
    work: Mapping[str, Any]
    source_cell: CellPopulations = field(repr=False)
    independent_draw_count: None = None
    independent_validation_performed: bool = False
    qualification: str = "Descriptive proxy; zero distance does not establish structural equivalence."


def _known(value: Any) -> Any:
    k = knowledge(value)
    return k.value if k.state == "known" else None


def _records(bundle: LoadedBundle) -> dict[tuple[str, str], list[Any]]:
    rows: dict[tuple[str, str], list[Any]] = defaultdict(list)
    for entry in bundle.records:
        raw = entry.raw
        if isinstance(raw, Mapping) and isinstance(raw.get("record_type"), str) and isinstance(raw.get("record_id"), str):
            rows[(raw["record_type"], raw["record_id"])].append(entry.record)
    return rows


def _one(rows: dict, key: tuple[str, str]) -> Any:
    found = rows.get(key, ())
    return found[0] if len(found) == 1 else None


def _sample_text(bundle, rows, cell, sid, decision, method, limits, cache):
    record = _one(rows, ("realization", sid))
    assoc = [a for a in cell.inventory.associations if a.sample_id == sid]
    base = SampleText(sid, decision.outcome, "unavailable", (), None, decision.record_id,
                      decision.revision, None, None)
    def fail(reason): return replace(base, status="ineligible", reasons=(reason,)), None
    if record is None: return fail("sample_identity_unresolved")
    d = record.data
    if d["analysis_cell_id"] != cell.inventory.cell_id: return fail("sample_cell_mismatch")
    base = replace(base, completion_status=d["completion_status"], group_id=_known(d["generation_group_id"]),
                   attempt_id=_known(d["attempt_id"]))
    if len(assoc) != 1: return fail("sample_association_unresolved")
    a = assoc[0]
    base = replace(base, span_status=a.span_status)
    if a.reasons: return fail("sample_association_contradiction")
    for key in ("raw_response_ref", "output_ref", "output_content_hash", "extraction_rule_version"):
        if getattr(a, key) != d[key]: return fail("accepted_association_context_mismatch")
    if a.span_status in {"mismatch", "unavailable"}: return fail("declared_extraction_span_unverified")
    if _known(d["extraction_rule_version"]) != method.extraction_rule_version:
        return fail("extraction_version_mismatch_or_unknown")
    state = knowledge(d["output_ref"])
    if state.state != "known": return fail("output_ref_" + state.state)
    ref = state.value
    try: validate_ref(ref)
    except InputError: return fail("invalid_output_reference")
    if ref["record_type"] != "artifact": return fail("output_reference_wrong_type")
    base = replace(base, artifact_ref=(ref["record_type"], ref["record_id"], ref["record_version"]))
    if _one(rows, (ref["record_type"], ref["record_id"])) is None: return fail("artifact_identity_unresolved")
    inspections = [i for i in bundle.artifacts if i.record_key == ref["record_type"] + ":" + ref["record_id"]]
    if len(inspections) != 1: return fail("artifact_inspection_unresolved")
    inspection = inspections[0]
    if inspection.status != "snapshot_read": return fail("artifact_" + inspection.status)
    snapshot = bundle.snapshots.get(inspection.snapshot_path)
    if snapshot is None: return fail("snapshot_missing")
    base = replace(base, snapshot_locator_sha256=_hash(snapshot.path.encode("utf-8")),
                   original_sha256=snapshot.sha256, original_bytes=snapshot.size_bytes)
    # Validate the held bytes, without reading a path or repairing metadata.
    if (len(snapshot.content) != snapshot.size_bytes or _hash(snapshot.content) != snapshot.sha256
            or inspection.actual_sha256 != snapshot.sha256): return fail("snapshot_identity_conflict")
    declared_hash = _known(d["output_content_hash"])
    if declared_hash is not None and declared_hash != snapshot.sha256: return fail("output_hash_mismatch")
    t = cache.get(snapshot.sha256)
    if t is None:
        t = tokenize_text(snapshot.content, method, limits=limits)
        cache[snapshot.sha256] = t
    base = replace(base, status=t.status, reasons=t.reasons, normalized_sha256=t.normalized_sha256,
                   trigram_sha256=t.trigram_sha256, lexical_unit_count=t.lexical_unit_count,
                   observed_lexical_units=t.observed_lexical_units,
                   trigram_count=len(t.trigrams) if t.status == "eligible" else None,
                   resource_failure=t.resource_failure)
    return base, t if t.status == "eligible" else None


def diagnose_population(bundle: LoadedBundle, cell: CellPopulations, view: str,
                        method: TextMethod, *, limits: DiagnosticLimits | None = None,
                        work: WorkBudget | None = None) -> TextDiagnostics:
    """Consume accepted IDs from one M view. Never recompute/admit a label.

    Share WorkBudget across every view/cell in a comparison run. Without one,
    this explicitly standalone call owns its own budget. No numeric endpoint
    gate or scientific comparison is performed here.
    """
    if not isinstance(bundle, LoadedBundle) or not isinstance(cell, CellPopulations) or not isinstance(method, TextMethod):
        raise InputError("invalid_text_diagnostic_component")
    if view not in ("classified_all", "classified_valid") or view not in cell.populations:
        raise InputError("invalid_text_population")
    limits = DiagnosticLimits() if limits is None else limits
    if not isinstance(limits, DiagnosticLimits): raise InputError("invalid_text_diagnostic_limits")
    work = work if work is not None else WorkBudget(limits.max_trigram_visits)
    if not isinstance(work, WorkBudget) or work.max_trigram_visits != limits.max_trigram_visits:
        raise InputError("text_work_budget_mismatch")
    work.__post_init__()
    start_visits = work.visits
    pop = cell.populations[view]
    ids = pop.sample_ids
    rows = _records(bundle)
    decisions = {d.sample_id: d for d in cell.admissions if d.axis == "assignment" and d.status == "accepted"}
    errors = list(pop.reasons) if pop.status != "available" else []
    n = pop.count
    if pop.status != "available": errors.append("population_unavailable")
    if len(set(ids)) != len(ids) or any(s not in decisions for s in ids): errors.append("population_identity_conflict")
    if not errors:
        actual = Counter(decisions[s].outcome for s in ids)
        if any(type(v) is not int or v < 0 for v in pop.class_counts.values()) or actual != Counter({k:v for k,v in pop.class_counts.items() if v}):
            errors.append("population_count_conflict")
    if not errors:
        for sid in ids:
            decision = decisions[sid]
            assignment = _one(rows, ("assignment", decision.record_id))
            if (assignment is None or assignment.data["sample_id"] != sid
                    or assignment.data["assignment_version"] != decision.revision
                    or assignment.data["structural_class_id"] != decision.outcome):
                errors.append("accepted_assignment_context_mismatch")
                break
    method_errors = _method_reasons(method)
    errors.extend(method_errors)
    samples = []; tokenized = {}; cache = {}
    if not errors:
        for sid in ids:
            sample, t = _sample_text(bundle, rows, cell, sid, decisions[sid], method, limits, cache)
            samples.append(sample)
            if t is not None: tokenized[sid] = t
    subset_complete = not errors and not any(s.resource_failure for s in samples)
    if any(s.resource_failure for s in samples): errors.append("max_lexical_units_exceeded")
    eligible = tuple(s for s in ids if s in tokenized)
    m = len(eligible) if subset_complete else None
    coverage = Ratio(m, n, "unavailable", "text_subset_unavailable") if m is None or n is None else (
        Ratio(m, n, "undefined", "empty_population") if n == 0 else Ratio(m, n, "available"))
    groups = {z: tuple(s for s in eligible if decisions[s].outcome == z)
              for z, count in pop.class_counts.items() if count > 0}
    p = m*(m-1)//2 if m is not None else None
    within_p = sum(len(x)*(len(x)-1)//2 for x in groups.values()) if m is not None else None
    names = (SURFACE, WITHIN, STRUCTURAL)
    results = {name: _value(name, None, within_p if name == WITHIN else p,
                           errors[0] if errors else "fewer_than_two_eligible_texts", unavailable=bool(errors)) for name in names}
    pair_rows = []; class_sums = {z: Fraction() for z in groups}
    class_values = {}; dependency = Counter(); required_visits = None; enumerated = 0; sci = None
    if m is not None and m > 0:
        sci_f = Fraction(sum(len(x)**2 for x in groups.values()), m*m)
        try:
            _checked(sci_f, limits); sci = (sci_f.numerator, sci_f.denominator)
        except InputError: pass
    if p is not None and p > limits.max_pairs:
        errors.append("max_pairs_exceeded")
        results = {name: _value(name, None, within_p if name == WITHIN else p, "max_pairs_exceeded", unavailable=True) for name in names}
    elif p:
        try:
            q = _checked(Fraction(p-within_p, p), limits)
            results[STRUCTURAL] = _value(STRUCTURAL, q, p)
        except InputError as exc:
            errors.append(exc.code); results[STRUCTURAL] = _value(STRUCTURAL, None, p, exc.code, unavailable=True)
        required_visits = (m-1)*sum(len(tokenized[s].trigrams) for s in eligible)
        if required_visits > work.max_trigram_visits - work.visits:
            errors.append("max_trigram_visits_exceeded")
            for name in (SURFACE, WITHIN):
                results[name] = _value(name, None, within_p if name == WITHIN else p,
                                       "max_trigram_visits_exceeded", unavailable=True)
        else:
            total = Fraction(); within_total = Fraction()
            samples_by_id = {s.sample_id: s for s in samples}
            try:
                for left, right in combinations(eligible, 2):
                    a, b = tokenized[left].trigrams, tokenized[right].trigrams
                    work.visits += len(a)+len(b)
                    intersection = len(a & b); union = len(a)+len(b)-intersection
                    distance = _checked(Fraction(union-intersection, union), limits)
                    total = _checked(total+distance, limits)
                    different = decisions[left].outcome != decisions[right].outcome
                    if not different:
                        z = decisions[left].outcome
                        class_sums[z] = _checked(class_sums[z]+distance, limits)
                        within_total = _checked(within_total+distance, limits)
                    sa, sb = samples_by_id[left], samples_by_id[right]
                    same = (sa.attempt_id == sb.attempt_id) if sa.attempt_id and sb.attempt_id else (
                        True if sa.group_id is not None and sa.group_id == sb.group_id else None)
                    dependency["same_call" if same else "distinct_recorded_calls" if same is False else "unknown_call_relation"] += 1
                    pair_rows.append(PairObservation(left, right, intersection, union,
                                                     (distance.numerator, distance.denominator), different, same))
                    enumerated += 1
                results[SURFACE] = _value(SURFACE, _checked(total/p, limits), p)
                results[WITHIN] = _value(WITHIN, _checked(within_total/within_p, limits) if within_p else None,
                                        within_p, None if within_p else "no_within_class_pairs")
                for z, members in groups.items():
                    pz = len(members)*(len(members)-1)//2
                    class_values[z] = _value(WITHIN, _checked(class_sums[z]/pz, limits) if pz else None,
                                             pz, None if pz else "no_within_class_pairs")
            except InputError as exc:
                errors.append(exc.code)
                # Partial arithmetic is never a replacement estimator.
                pair_rows = []; dependency.clear(); class_values.clear()
                for name in (SURFACE, WITHIN):
                    results[name] = _value(name, None, within_p if name == WITHIN else p, exc.code, unavailable=True)
    elif not errors:
        results[WITHIN] = _value(WITHIN, None, within_p, "no_within_class_pairs")
    classes = []
    for z, members in groups.items():
        pz = len(members)*(len(members)-1)//2 if m is not None else None
        mean = class_values.get(z)
        if mean is None:
            affected = results[WITHIN].result_status == "unavailable"
            reason = results[WITHIN].reasons[0] if affected else "no_within_class_pairs"
            mean = _value(WITHIN, None, pz, reason, unavailable=affected)
        classes.append(ClassDiagnostic(z, pop.class_counts[z], members, pz, mean))
    return TextDiagnostics(cell.inventory.cell_id, view, "unavailable" if errors else "available",
        tuple(sorted(set(errors))), method, limits, n, ids, eligible, m, subset_complete, coverage,
        p, within_p, tuple(samples), tuple(pair_rows), tuple(classes), freeze(results), sci,
        freeze(dict(dependency)), freeze({"required_trigram_visits": required_visits,
        "visits_before": start_visits, "visits_after": work.visits,
        "visits_this_diagnostic": work.visits-start_visits, "enumerated_pairs": enumerated,
        "pair_table_complete": len(pair_rows) == p if p is not None else False,
        "unique_snapshot_tokenizations": len(cache),
        "text_sci_status": "available" if sci is not None else "undefined" if m == 0 else "unavailable"}), cell)


def diagnose_cells(bundle: LoadedBundle, cells: tuple[CellPopulations, ...], method: TextMethod,
                   *, views: tuple[str, ...] = ("classified_all", "classified_valid"),
                   limits: DiagnosticLimits | None = None) -> tuple[TextDiagnostics, ...]:
    """A diagnostic-only batch sharing one cumulative budget in supplied order.

    Retains cells and both populations separately; no pooling or A/B/C inference.
    """
    if (not isinstance(cells, (tuple, list)) or any(not isinstance(c, CellPopulations) for c in cells)
            or len({c.inventory.cell_id for c in cells}) != len(cells)
            or not isinstance(views, (tuple, list)) or not views
            or any(v not in ("classified_all", "classified_valid") for v in views)
            or len(set(views)) != len(views)):
        raise InputError("invalid_text_diagnostic_batch")
    limits = DiagnosticLimits() if limits is None else limits
    if not isinstance(limits, DiagnosticLimits): raise InputError("invalid_text_diagnostic_limits")
    if not isinstance(bundle, LoadedBundle) or not isinstance(method, TextMethod):
        raise InputError("invalid_text_diagnostic_component")
    work = WorkBudget(limits.max_trigram_visits)
    return tuple(diagnose_population(bundle, c, v, method, limits=limits, work=work)
                 for c in cells for v in views)
