"""Phase 1 Step 5: finite, unweighted structural-count calculations.

Specification: METRICS_SPEC.md v0.2, sections 3-7 and 12; VF sections 5.1-5.2.
`count_metrics` is a count-table arithmetic component, not a model assessment.
`cell_metrics` consumes an already established CellPopulations, retaining it as
an immutable provenance/accounting reference. `prefix_metric` retains the exact
Step 4 prefix, including missing positions, exclusions and shared-call groups.
The later report layer must bind these components to its run and input manifest;
this module does not read inputs, render reports, pool cells or estimate intervals.

Optional thresholds use the existing exact-decimal input vocabulary. Omission
and explicit null differ. Large negative exponents are compared as factored
integers, never expanded to an enormous denominator or rounded to binary zero.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal
from fractions import Fraction
import math
from typing import Any, Mapping

from .contracts import ExactNumber, InputError, ThresholdToken, freeze, is_id, threshold_token
from .populations import CellPopulations, Population, Prefix, accumulation, prefix

METRIC_DEFINITION_VERSION = "MET-0.2"
ABS_TOL = 1e-12
REL_TOL = 1e-10
# Computation limits, not experimental sampling limits. No trimming on overflow.
MAX_COUNT_BITS = 4096
MAX_CLASS_ENTRIES = 100_000
_OMITTED = object()
CORE_NAMES = (
    "observed_support_size", "observed_support_size_thresholded",
    "structural_entropy_nats", "structural_concentration_index",
    "effective_support_shannon", "effective_support_simpson",
)
_UNITS = dict(zip(CORE_NAMES, (
    "classes", "classes", "nats", "dimensionless", "effective_classes", "effective_classes",
)))
_ESTIMATORS = dict(zip(CORE_NAMES, (
    "positive_integer_class_count", "exact_empirical_frequency_threshold",
    "unsmoothed_empirical_shannon_entropy", "unsmoothed_empirical_collision_probability",
    "exp_unrounded_entropy_nats", "reciprocal_unrounded_concentration",
)))


@dataclass(frozen=True)
class NumericCorrection:
    metric_name: str
    original_value: float
    stored_value: float
    reason: str


@dataclass(frozen=True)
class Metric:
    metric_name: str
    value: int | float | None
    result_status: str
    unit: str
    estimator: str
    reasons: tuple[str, ...] = ()
    qualifiers: tuple[str, ...] = ()
    exact_ratio: tuple[int, int] | None = None
    corrections: tuple[NumericCorrection, ...] = ()
    metric_definition_version: str = METRIC_DEFINITION_VERSION
    uncertainty_status: str = "not_estimated"
    uncertainty_method: str | None = None


@dataclass(frozen=True)
class Threshold:
    requested: bool
    status: str
    token: str | None = None
    representation: str | None = None
    coefficient: int | None = None
    denominator_power10: int | None = None
    exact_ratio: tuple[int, int] | None = None
    reason: str | None = None
    comparison: str = "10**denominator_power10 * c_z >= coefficient * n_A"


@dataclass(frozen=True)
class DistributionMetrics:
    population_size: int | None
    class_counts: Mapping[str, int]
    exact_frequencies: Mapping[str, tuple[int, int]]
    threshold: Threshold
    results: Mapping[str, Metric]
    input_diagnostics: tuple[str, ...] = ()
    computation_scope: str = "supplied_count_table_only"
    independent_validation_performed: bool = False


@dataclass(frozen=True)
class PrefixMetric:
    source_prefix: Prefix = field(repr=False)
    result: Metric


@dataclass(frozen=True)
class CellMetrics:
    source_cell: CellPopulations = field(repr=False)
    distributions: Mapping[str, DistributionMetrics]
    prefixes: tuple[PrefixMetric, ...]
    evidence_status: str = "supplied_record_checks_only"
    permitted_claim_scope: str = "finite_sample_label_conditioned_summary"
    independent_validation_performed: bool = False


def _metric(name: str, value: int | float | None, status: str = "available", **kw: Any) -> Metric:
    return Metric(name, value, status, _UNITS[name], _ESTIMATORS[name], **kw)


def _threshold(value: Any) -> Threshold:
    if value is _OMITTED:
        return Threshold(False, "not_requested", reason="threshold_not_requested")
    try:
        if isinstance(value, ThresholdToken):
            if not isinstance(value.representation, str) or value.representation not in {"json_number", "decimal_string"}:
                raise InputError("invalid_threshold")
            parsed = threshold_token(value.token)
            parsed = ThresholdToken(parsed.token, value.representation)
        else:
            parsed = threshold_token(value)
        parts = Decimal(parsed.token).as_tuple()
        digits = list(parts.digits)
        exponent = parts.exponent
        while len(digits) > 1 and digits[-1] == 0:
            digits.pop()
            exponent += 1
        coefficient = int("".join(str(d) for d in digits))
        # A positive decimal <= 1 has a nonpositive exponent after normalization.
        power = -exponent
        if power < 0:
            raise InputError("invalid_threshold")
        ratio = None
        if power <= 4096:
            fraction = Fraction(coefficient, 10 ** power)
            ratio = (fraction.numerator, fraction.denominator)
        return Threshold(True, "available", parsed.token, parsed.representation, coefficient, power, ratio)
    except (InputError, ValueError, OverflowError):
        return Threshold(True, "unavailable", reason="invalid_threshold")


def _passes(count: int, total: int, threshold: Threshold) -> bool:
    """Exact integer cross multiplication with bounded, factored powers of ten."""
    if count == 0:
        return False
    right = threshold.coefficient * total
    left_digits = len(str(count)) + threshold.denominator_power10
    right_digits = len(str(right))
    if left_digits != right_digits:
        return left_digits > right_digits
    # Equality of digit lengths bounds this power by the size of supplied counts.
    return count * 10 ** threshold.denominator_power10 >= right


def _checked_counts(counts: Any, total: Any) -> tuple[dict[str, int] | None, str | None]:
    if not isinstance(counts, Mapping) or type(total) is not int or total < 0:
        return None, "invalid_count_table"
    if len(counts) > MAX_CLASS_ENTRIES or total.bit_length() > MAX_COUNT_BITS:
        return None, "arithmetic_resource_limit"
    for key, value in counts.items():
        if not is_id(key) or type(value) is not int or value < 0:
            return None, "invalid_count_table"
        if value.bit_length() > MAX_COUNT_BITS:
            return None, "arithmetic_resource_limit"
    if sum(counts.values()) != total:
        return None, "count_conservation_failed"
    return dict(sorted(counts.items())), None


def _blocked(counts: Mapping[str, int], total: int | None, threshold: Threshold,
             reasons: tuple[str, ...]) -> DistributionMetrics:
    results = {name: _metric(name, None, "unavailable", reasons=reasons) for name in CORE_NAMES}
    if not threshold.requested:
        results[CORE_NAMES[1]] = _metric(CORE_NAMES[1], None, "not_requested", reasons=("threshold_not_requested",))
    elif threshold.status != "available":
        results[CORE_NAMES[1]] = _metric(CORE_NAMES[1], None, "unavailable", reasons=(threshold.reason,))
    return DistributionMetrics(total, freeze(counts), freeze({}), threshold, freeze(results), reasons)


def _bounded(name: str, value: float, low: float, high: float) -> Metric:
    """Only representational boundary corrections within the adopted tolerance."""
    if not all(math.isfinite(x) for x in (value, low, high)) or low > high:
        return _metric(name, None, "unavailable", reasons=("numerical_check_failed",))
    corrections = []
    original = value
    if value < low or value > high:
        boundary = low if value < low else high
        if abs(value - boundary) > ABS_TOL + REL_TOL * abs(boundary):
            return _metric(name, None, "unavailable", reasons=("numerical_check_failed",))
        value = boundary
        corrections.append(NumericCorrection(name, original, value, "within_tolerance_range_boundary"))
    if value == 0.0 and math.copysign(1.0, value) < 0:
        corrections.append(NumericCorrection(name, value, 0.0, "signed_negative_zero"))
        value = 0.0
    return _metric(name, value, corrections=tuple(corrections))


def count_metrics(counts: Mapping[str, int], population_size: int, *,
                  min_empirical_frequency: Any = _OMITTED) -> DistributionMetrics:
    """Evaluate a declared count table. This helper does not admit raw labels.

    Nonnegative integer counts must sum exactly to population_size. Invalid tables
    return unavailable component values, never an empty-distribution substitute.
    Invalid thresholds affect their own optional quantity, not other estimators.
    The full accepted denominator is retained even when no class meets threshold.
    """
    threshold = _threshold(min_empirical_frequency)
    table, error = _checked_counts(counts, population_size)
    if error:
        total = population_size if type(population_size) is int and population_size >= 0 else None
        return _blocked({}, total, threshold, (error,))
    total = population_size
    positive = sorted(c for c in table.values() if c > 0)
    support = len(positive)
    qualifiers = ("empty_classified_population",) if total == 0 else ()
    results = {CORE_NAMES[0]: _metric(CORE_NAMES[0], support, qualifiers=qualifiers)}
    threshold_name = CORE_NAMES[1]
    if not threshold.requested:
        results[threshold_name] = _metric(threshold_name, None, "not_requested", reasons=("threshold_not_requested",))
    elif threshold.status != "available":
        results[threshold_name] = _metric(threshold_name, None, "unavailable", reasons=(threshold.reason,))
    elif not total:
        results[threshold_name] = _metric(threshold_name, None, "undefined", reasons=("empty_classified_population",))
    else:
        results[threshold_name] = _metric(threshold_name, sum(_passes(c, total, threshold) for c in table.values()))
    frequencies = {key: (value, total) for key, value in table.items()} if total else {}
    if not total:
        for name in CORE_NAMES[2:]:
            results[name] = _metric(name, None, "undefined", reasons=("empty_classified_population",))
    else:
        probabilities = [c / total for c in positive]
        good_normalization = (all(math.isfinite(p) and p > 0 for p in probabilities)
                              and abs(math.fsum(probabilities) - 1.0) <= ABS_TOL + REL_TOL)
        if not good_normalization:
            for name in CORE_NAMES[2:]:
                results[name] = _metric(name, None, "unavailable", reasons=("numerical_check_failed",))
        else:
            h_name, sci_name, sh_name, si_name = CORE_NAMES[2:]
            try:
                entropy = math.fsum(-p * math.log(p) for p in probabilities)
                results[h_name] = _bounded(h_name, entropy, 0.0, math.log(support))
            except (ValueError, OverflowError):
                results[h_name] = _metric(h_name, None, "unavailable", reasons=("numerical_check_failed",))
            collision = Fraction(sum(c * c for c in positive), total * total)
            sci = float(collision)
            results[sci_name] = _bounded(sci_name, sci, 1.0 / support, 1.0)
            if results[sci_name].result_status == "available":
                r = results[sci_name]
                results[sci_name] = Metric(**{**vars(r), "exact_ratio": (collision.numerator, collision.denominator)})
            for name, parent, operation in ((sh_name, h_name, math.exp), (si_name, sci_name, lambda v: 1.0 / v)):
                if results[parent].result_status != "available":
                    results[name] = _metric(name, None, "unavailable", reasons=("upstream_numerical_check_failed",))
                    continue
                try:
                    results[name] = _bounded(name, operation(results[parent].value), 1.0, float(support))
                except (ValueError, OverflowError, ZeroDivisionError):
                    results[name] = _metric(name, None, "unavailable", reasons=("numerical_check_failed",))
            if results[si_name].result_status == "available":
                r = results[si_name]
                results[si_name] = Metric(**{**vars(r), "exact_ratio": (collision.denominator, collision.numerator)})
            if results[sh_name].result_status == results[si_name].result_status == "available":
                sh, si = results[sh_name].value, results[si_name].value
                if si - sh > ABS_TOL + REL_TOL * abs(sh):
                    for name in (sh_name, si_name):
                        results[name] = _metric(name, None, "unavailable", reasons=("numerical_check_failed",))
    return DistributionMetrics(total, freeze(table), freeze(frequencies), threshold, freeze(results),
                               (threshold.reason,) if threshold.status == "unavailable" else ())


def population_metrics(population: Population, *, min_empirical_frequency: Any = _OMITTED) -> DistributionMetrics:
    """Evaluate one already accepted view without reclassifying or reweighting it."""
    if not isinstance(population, Population):
        raise InputError("invalid_population_component")
    if population.status != "available":
        return _blocked({}, None, _threshold(min_empirical_frequency), population.reasons or ("population_unavailable",))
    ids = population.sample_ids
    if (not isinstance(ids, tuple) or any(not is_id(s) for s in ids)
            or len(set(ids)) != len(ids)):
        return _blocked({}, None, _threshold(min_empirical_frequency), ("population_identity_conflict",))
    return count_metrics(population.class_counts, len(ids), min_empirical_frequency=min_empirical_frequency)


def prefix_metric(value: Prefix) -> PrefixMetric:
    """Expose the accepted Step 4 endpoint, preserving its original k and status."""
    if not isinstance(value, Prefix):
        raise InputError("invalid_prefix_component")
    name = "structural_distinct_k"
    result = Metric(name, value.distinct_count if value.status == "available" else None, value.status, value.unit, value.selection_rule,
                    value.reasons, ("empty_classified_prefix",) if value.status == "available" and not value.counted_sample_ids else ())
    if value.status == "available":
        table, error = _checked_counts(value.class_counts, len(value.counted_sample_ids))
        if (error or type(value.distinct_count) is not int or type(value.k) is not int or value.k <= 0
                or len(value.selected_sample_ids) != value.k
                or len(set(value.selected_sample_ids)) != value.k
                or len(set(value.counted_sample_ids)) != len(value.counted_sample_ids)
                or not set(value.counted_sample_ids).issubset(value.selected_sample_ids)
                or value.distinct_count != sum(c > 0 for c in (table or {}).values())):
            result = Metric(name, None, "unavailable", value.unit, value.selection_rule, ("prefix_conservation_failed",))
    return PrefixMetric(value, result)


def cell_metrics(cell: CellPopulations, *, min_empirical_frequency: Any = _OMITTED,
                 ks: tuple[int, ...] | list[int] = (), prefix_mode: str = "descriptive") -> CellMetrics:
    """In-memory arithmetic on Step 4 output, with no I/O or report orchestration.

    `source_cell` retains the frame/protocol/cell references, selected inventory,
    accepted revisions, evidence restrictions, all five coverage ratios, statuses,
    groups and original ordering. No cross-cell aggregation is performed. The
    caller retains the pinned input bundle required to resolve those references.
    """
    if not isinstance(cell, CellPopulations):
        raise InputError("invalid_cell_component")
    if not isinstance(prefix_mode, str) or prefix_mode not in {"descriptive", "hero"}:
        raise InputError("unsupported_prefix_mode")
    distributions = {view: population_metrics(cell.populations[view], min_empirical_frequency=min_empirical_frequency)
                     for view in ("classified_all", "classified_valid")}
    if cell.inventory.selected_count.status == "available" and cell.inventory.selected_count.value == 0:
        for view, summary in distributions.items():
            values = dict(summary.results)
            observed = values[CORE_NAMES[0]]
            if observed.result_status == "available":
                values[CORE_NAMES[0]] = replace(observed, qualifiers=observed.qualifiers + ("empty_selected_inventory",))
                distributions[view] = replace(summary, results=freeze(values))
    points = tuple(prefix_metric(p) for p in accumulation(cell, ks, mode=prefix_mode))
    return CellMetrics(cell, freeze(distributions), points)
