"""Exact finite categorical scenarios and explicit mixture/selection accounting.

SI sections 5, 6 and Appendix A; PHASE_3_PLAN sections 4 and 8.6. Formula
expectations are conditional on declared closed reconstruction assumptions.
No random draws, candidate execution, empirical SHL fit or neural update map.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from math import gcd
import math
from typing import Any, Mapping

from .contracts import ExactNumber, InputError, freeze, is_id, knowledge
from .local_io import LoadedBundle
from . import longitudinal_records as lr

METHOD = "categorical_null_v1"
MIXTURE_METHOD = "categorical_mixture_selection_v1"
UNIT = "categorical_recursive_rounds"
ASSUMPTIONS = ("finite_multinomial", "fixed_classes", "closed", "empirical_reconstruction", "exogenous_schedule")
_UNSET = object()


@dataclass(frozen=True)
class Quantity:
    name: str
    value: Fraction | int | float | None = None
    status: str = "unavailable"
    unit: str = "dimensionless"
    reasons: tuple[str, ...] = ()
    qualifiers: tuple[str, ...] = ()
    evaluation: str = "exact_rational"
    uncertainty_status: str = "not_estimated"

    @property
    def exact_ratio(self) -> tuple[int, int] | None:
        if isinstance(self.value, Fraction):
            return self.value.numerator, self.value.denominator
        if type(self.value) is int:
            return self.value, 1
        return None


@dataclass(frozen=True)
class ForecastPoint:
    round_index: int
    transition_n: int | None
    retained_multiplier: Fraction
    expected_diversity: Fraction
    expected_concentration: Fraction
    expected_target_error: Fraction | None


@dataclass(frozen=True)
class CountTransition:
    index: int
    n: int | None
    supplied_counts: tuple[Any, ...]
    parent: tuple[Fraction, ...] | None
    child: tuple[Fraction, ...] | None
    parent_support: tuple[str, ...] | None
    child_support: tuple[str, ...] | None
    child_diversity: Quantity
    expected_child_diversity: Quantity
    child_target_error: Quantity
    expected_child_target_error: Quantity
    omission_probabilities: Mapping[str, Quantity]
    status: str
    reasons: tuple[str, ...] = ()
    violates_absorption: tuple[str, ...] = ()
    support_nonexpanding: bool | None = None
    realized_diversity_increased: bool | None = None


@dataclass(frozen=True)
class NullScenario:
    scenario_id: str
    classes: tuple[str, ...]
    parent: tuple[Fraction, ...]
    positive_support: tuple[str, ...]
    n: int | None
    requested_steps: int
    schedule: tuple[int, ...] | None
    mode: str
    assumptions: Mapping[str, Any]
    assumption_status: str
    original_operands: Mapping[str, Any] = field(repr=False)
    parent_diversity: Quantity
    parent_concentration: Quantity
    expected_next_diversity: Quantity
    omission_probabilities: Mapping[str, Quantity]
    target: tuple[Fraction, ...] | None
    target_status: str
    target_error: Quantity
    expected_next_target_error: Quantity
    structural_half_life_null: Quantity
    null_first_expected_half_crossing: Quantity
    halving_applicability: str
    forecast: tuple[ForecastPoint, ...]
    forecast_status: str
    forecast_reasons: tuple[str, ...]
    child_transitions: tuple[CountTransition, ...]
    status: str
    reasons: tuple[str, ...]
    limits: Mapping[str, int]
    method: str = METHOD
    distribution_scope: str = "explicit_finite_categorical_scenario"
    source_pins: Mapping[str, str] = field(default_factory=lambda: lr.SOURCE_PINS)
    substantive_validation_performed: bool = False
    empirical_pipeline_matches_null: bool = False
    simulated_draws: int = 0


@dataclass(frozen=True)
class MixtureSelection:
    scenario_id: str
    class_space_id: str
    classes: tuple[str, ...]
    parent: tuple[Fraction, ...]
    external: tuple[Fraction, ...]
    effective_weight: Fraction | None
    weight_unit: str
    lambda_unit: str
    weights: tuple[Fraction | None, ...] | None
    candidate: tuple[Fraction, ...] | None
    candidate_support: tuple[str, ...] | None
    selection_mass: Quantity
    selected: tuple[Fraction, ...] | None
    selected_support: tuple[str, ...] | None
    added_candidate_classes: tuple[str, ...] | None
    removed_by_selection: tuple[str, ...] | None
    status: str
    reasons: tuple[str, ...]
    original_operands: Mapping[str, Any] = field(repr=False)
    limits: Mapping[str, int]
    method: str = MIXTURE_METHOD
    parameter_scope: str = "declared_effective_preselection_weight"
    next_model_distribution: None = None
    structural_exogamy_established: bool = False
    substantive_validation_performed: bool = False


@dataclass(frozen=True)
class ScenarioBinding:
    binding: lr.ObjectBinding
    result: NullScenario | None
    status: str
    reasons: tuple[str, ...] = ()
    evidence_status: str = "declared_only"


@dataclass(frozen=True)
class CategoricalStudy:
    requested: bool
    status: str
    input_context_sha256: str | None
    review: lr.LongitudinalReview = field(repr=False)
    scenarios: tuple[ScenarioBinding, ...] = ()
    reasons: tuple[str, ...] = ()
    method: str = METHOD
    substantive_validation_performed: bool = False


class _Limit(InputError):
    def __init__(self):
        super().__init__("categorical_exact_resource_limit")


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise InputError(code)


def _limits(value) -> Mapping[str, int]:
    _require(value is None or isinstance(value, Mapping), "categorical_limits_required")
    result = dict(lr.LIMITS)
    for key, v in (value or {}).items():
        _require(key in result and type(v) is int and 1 <= v <= result[key], "categorical_limit_invalid")
        if key == "sensitivity_replicates":
            _require(v == result[key], "categorical_limit_invalid")
        result[key] = v
    return freeze(result)


class _Exact:
    """Bound each constructed integer; cross-cancel before products and powers.

    Conservative product-size preflight can refuse an otherwise small final
    value. The refusal is visible and never triggers a floating approximation.
    """
    def __init__(self, limits):
        self.bits = limits["max_exact_bits"]

    def integer(self, v):
        if abs(v).bit_length() > self.bits:
            raise _Limit()
        return v

    def fraction(self, x):
        self.integer(x.numerator); self.integer(x.denominator)
        return x

    def product(self, a, b):
        if not a or not b:
            return 0
        if abs(a) == 1:
            return self.integer(a * b)
        if abs(b) == 1:
            return self.integer(a * b)
        if abs(a).bit_length() + abs(b).bit_length() > self.bits:
            raise _Limit()
        return self.integer(a * b)

    def add(self, a, b):
        g = gcd(a.denominator, b.denominator)
        left = self.product(a.numerator, b.denominator // g)
        right = self.product(b.numerator, a.denominator // g)
        # Sum itself allocates at most one extra bit; enforce before publishing.
        num = self.integer(left + right)
        den = self.product(a.denominator, b.denominator // g)
        return self.fraction(Fraction(num, den))

    def mul(self, a, b):
        g = gcd(abs(a.numerator), b.denominator)
        h = gcd(abs(b.numerator), a.denominator)
        return self.fraction(Fraction(self.product(a.numerator // g, b.numerator // h),
                                     self.product(a.denominator // h, b.denominator // g)))

    def div(self, a, b):
        _require(b != 0, "categorical_zero_divisor")
        return self.mul(a, Fraction(b.denominator, b.numerator))

    def sum(self, values):
        total = Fraction(0)
        for x in values:
            total = self.add(total, x)
        return total

    def power(self, x, exponent):
        if not exponent:
            return self.fraction(Fraction(1))
        if x in (0, 1):
            return self.fraction(x)
        # Integer lower bound avoids building a huge power merely to reject it.
        if max(abs(x.numerator).bit_length() - 1, x.denominator.bit_length() - 1) * exponent >= self.bits:
            raise _Limit()
        result = Fraction(1)
        while exponent:
            if exponent & 1:
                result = self.mul(result, x)
            exponent >>= 1
            if exponent:
                x = self.mul(x, x)
        return result


def _snapshot(raw, limits):
    """Bound passive direct-API operands before preserving an immutable copy."""
    stack = [(raw, 0)]; count = 0
    while stack:
        v, depth = stack.pop(); count += 1
        _require(count <= limits["max_link_objects"] and depth <= 64, "categorical_operand_work_limit")
        if isinstance(v, Mapping):
            _require(all(isinstance(k,str) for k in v), "categorical_operand_key")
            stack.extend((x,depth+1) for x in v.values())
        elif isinstance(v,(list,tuple)):
            stack.extend((x,depth+1) for x in v)
        elif isinstance(v,Fraction):
            _Exact(limits).fraction(v)
        elif isinstance(v,ExactNumber):
            _require(len(v.token) <= 1024, "categorical_exact_number_required")
        elif type(v) is int:
            _require(v.bit_length() <= max(64,limits["max_exact_bits"]), "categorical_operand_work_limit")
        elif type(v) is float:
            _require(math.isfinite(v), "categorical_nonfinite_operand")
        else:
            _require(v is None or type(v) in (str,bool), "categorical_operand_type")
    return freeze(raw)


def _number(value, a: _Exact) -> Fraction:
    if isinstance(value, Fraction):
        x = a.fraction(value)
    elif type(value) is int:
        x = a.fraction(Fraction(a.integer(value)))
    else:
        token = value.token if isinstance(value, ExactNumber) else value
        _require(isinstance(token, str) and len(token) <= 1024, "categorical_exact_number_required")
        ExactNumber(token)
        d = Decimal(token); t = d.as_tuple()
        _require(abs(t.exponent) <= 100000, "categorical_exponent_limit")
        coefficient = int(''.join(str(x) for x in t.digits))
        if coefficient == 0:
            x = Fraction(0)
        else:
            power = abs(t.exponent)
            # 3 is a rigorous lower bound for log2(10). Per-product upper guards
            # below finish the check without ever materializing an enormous power.
            if 3 * power >= a.bits:
                raise _Limit()
            ten = a.power(Fraction(10), power)
            c = Fraction(a.integer(-coefficient if t.sign else coefficient))
            x = a.mul(c, ten) if t.exponent >= 0 else a.div(c, ten)
    _require(x >= 0, "categorical_negative_operand")
    return x


def _classes(classes, lim):
    _require(isinstance(classes, (tuple, list)) and 1 <= len(classes) <= lim["max_categorical_classes"],
             "categorical_class_space_required")
    _require(all(is_id(c) for c in classes), "categorical_class_id_invalid")
    _require(len(set(classes)) == len(classes), "categorical_duplicate_class")
    return tuple(classes)


def _vector(values, classes, a):
    _require(isinstance(values, (tuple, list)) and len(values) == len(classes), "categorical_vector_dimension")
    return tuple(_number(v, a) for v in values)


def _distribution(values, classes, a):
    p = _vector(values, classes, a)
    _require(a.sum(p) == 1, "categorical_probability_total_not_one")
    return p


def _n(n):
    _require(type(n) is int and 1 <= n <= 2**63 - 1, "categorical_sample_size_invalid")
    return n


def _support(classes, p):
    return tuple(c for c, x in zip(classes, p) if x > 0)


def _diversity(p, a):
    return a.add(Fraction(1), -a.sum(a.mul(x, x) for x in p))


def _distance(p, q, a):
    return a.sum(a.mul(d, d) for d in (a.add(x, -y) for x, y in zip(p, q)))


def _quantity(name, value=None, *, status=None, reasons=(), unit="dimensionless", qualifiers=(), evaluation="exact_rational"):
    return Quantity(name, value, status or ("available" if value is not None else "unavailable"), unit,
                    tuple(sorted(set(reasons))), tuple(qualifiers), evaluation)


def _calculate(name, fn, *, unit="dimensionless", qualifiers=()):
    try:
        return _quantity(name, fn(), unit=unit, qualifiers=qualifiers)
    except _Limit as exc:
        return _quantity(name, reasons=(exc.code,), unit=unit, qualifiers=qualifiers)


def _assumptions(raw, scheduled):
    _require(isinstance(raw, Mapping) and set(raw) == set(ASSUMPTIONS), "categorical_assumption_fields")
    values = {}
    for name, value in raw.items():
        k = knowledge(value)
        if k.state == "known":
            _require(type(k.value) is bool, "categorical_assumption_boolean")
            values[name] = k.value
        else:
            values[name] = None
    required = ASSUMPTIONS if scheduled else ASSUMPTIONS[:4]
    return tuple(name + ("_unknown" if values[name] is None else "_not_satisfied")
                 for name in required if values[name] is not True)


def _operand_value(raw):
    if isinstance(raw, Mapping):
        k = knowledge(raw)
        return k.value if k.state == "known" else None
    return raw


def _half_life(n, d, scheduled, allowed, a):
    name = "structural_half_life_null"
    crossing_name = "null_schedule_first_half_crossing" if scheduled else "null_first_expected_half_crossing"
    if not allowed:
        return (_quantity(name, reasons=("null_assumptions_unresolved",), unit=UNIT),
                _quantity(crossing_name, reasons=("null_assumptions_unresolved",), unit=UNIT), "unavailable")
    if scheduled:
        return (_quantity(name, status="not_requested", reasons=("variable_schedule_not_fixed_n_SHL",), unit=UNIT),
                _quantity(crossing_name, unit=UNIT), "no_positive_diversity" if d == 0 else "schedule_specific")
    if n == 1:
        applicable = "no_positive_diversity" if d == 0 else "one_step_collapse_outside_log_domain"
        crossing = (_quantity(crossing_name, 1, unit=UNIT) if d is not None and d > 0 else
                    _quantity(crossing_name, status="undefined", reasons=("no_positive_initial_diversity",), unit=UNIT))
        return _quantity(name, status="undefined", reasons=("n_one_outside_log_domain",), unit=UNIT), crossing, applicable
    qualifiers = ("conditional_parameter_timescale",) if d == 0 else ()
    try:
        value = math.log(2.0) / -math.log1p(-1.0 / n)
        if not math.isfinite(value) or value <= 0:
            raise ArithmeticError
        shl = _quantity(name, value, unit=UNIT, qualifiers=qualifiers, evaluation="binary64_log1p")
    except (ArithmeticError, ValueError):
        shl = _quantity(name, reasons=("categorical_log_numerical_failure",), unit=UNIT, evaluation="binary64_log1p")
    if d is None or d == 0:
        return shl, _quantity(crossing_name, status="undefined" if d == 0 else "unavailable",
            reasons=("no_positive_initial_diversity" if d == 0 else "initial_diversity_unavailable",), unit=UNIT), \
            "no_positive_diversity" if d == 0 else "unavailable"
    # Exact integer bracket, independent of rounded log/ceil. Large n may have a
    # valid finite SHL but no certified integer crossing within exact-bit limits.
    def first():
        ratio = a.fraction(Fraction(n - 1, n)); low, high = 0, 1
        half = Fraction(1, 2)
        while a.power(ratio, high) > half:
            low, high = high, high * 2
        while high - low > 1:
            mid = (low + high) // 2
            if a.power(ratio, mid) <= half:
                high = mid
            else:
                low = mid
        return high
    return shl, _calculate(crossing_name, first, unit=UNIT), "positive_initial_diversity"


def _path(classes, p, q, counts, ns, allowed, a, target_requested):
    result = []; parent = p; viable = bool(allowed)
    for i, raw in enumerate(counts):
        n = ns[i] if i < len(ns) else None
        reasons = []; child = None; lost = (); nonexpanding = None; increased = None
        valid_shape = isinstance(raw, (tuple, list)) and len(raw) == len(classes)
        if not valid_shape:
            reasons.append("child_count_dimension")
        elif any(type(x) is not int or not 0 <= x <= 2**63 - 1 for x in raw):
            reasons.append("child_count_integer_required")
        elif n is None:
            reasons.append("child_outside_requested_transitions")
        elif sum(raw) != n:
            reasons.append("child_count_sum_mismatch")
        else:
            try:
                child = tuple(a.fraction(Fraction(x, n)) for x in raw)
            except _Limit as exc:
                reasons.append(exc.code)
        base = _calculate("child_diversity", lambda: _diversity(child, a)) if child is not None else _quantity("child_diversity", reasons=reasons)
        target = (_calculate("child_target_error", lambda: _distance(child, q, a)) if child is not None and q is not None else
                  _quantity("child_target_error", reasons=("child_or_target_unavailable",)))
        if not target_requested:
            target = _quantity("child_target_error", status="not_requested")
        if not viable:
            reasons.append("prior_path_or_assumptions_unavailable")
        expected = _quantity("conditional_expected_child_diversity", reasons=("path_or_parent_unavailable",))
        etarget = _quantity("conditional_expected_child_target_error", reasons=("path_or_target_unavailable",))
        if not target_requested:
            etarget = _quantity("conditional_expected_child_target_error", status="not_requested")
        omissions = {}
        if viable and parent is not None and n is not None:
            pd = _calculate("parent_diversity", lambda: _diversity(parent, a))
            if pd.value is not None:
                expected = _calculate("conditional_expected_child_diversity", lambda: a.mul(Fraction(n - 1, n), pd.value))
                if q is not None:
                    etarget = _calculate("conditional_expected_child_target_error", lambda: a.add(_distance(parent, q, a), a.div(pd.value, Fraction(n))))
                if base.value is not None:
                    increased = base.value > pd.value
            omissions = {c: _calculate("next_step_omission_probability", lambda x=x: a.power(a.add(Fraction(1), -x), n)) for c, x in zip(classes, parent)}
            if child is not None:
                lost = tuple(c for c, x, y in zip(classes, parent, child) if x == 0 and y > 0)
                nonexpanding = not lost
                if lost:
                    reasons.append("positive_child_from_parent_zero")
        state = "inconsistent" if any(r.startswith("child_") or r == "positive_child_from_parent_zero" for r in reasons) else "unavailable" if reasons else "consistent_with_null"
        result.append(CountTransition(i + 1, n, tuple(raw) if isinstance(raw, (tuple, list)) else (raw,), parent, child,
            _support(classes, parent) if parent is not None else None, _support(classes, child) if child is not None else None,
            base, expected, target, etarget, freeze(omissions), state, tuple(reasons), lost, nonexpanding, increased))
        viable = viable and state == "consistent_with_null"
        parent = child  # preserve the supplied child, never repair or interpolate.
    return tuple(result)


def categorical_null(classes, p, *, scenario_id: str, n, steps: int, assumptions,
                     q=_UNSET, schedule=_UNSET, child_counts=(), limits=None) -> NullScenario:
    """Evaluate an explicitly declared scenario. Invalid direct inputs raise InputError.

    Exact Fraction operands are allowed in this Python API. The existing bundle
    format retains its stricter decimal-token representation. No default n, p,
    target, assumptions, or class space is inferred from empirical observations.
    """
    _require(is_id(scenario_id), "categorical_scenario_identity")
    lim = _limits(limits); a = _Exact(lim); classes = _classes(classes, lim)
    original = _snapshot(dict(classes=classes,p=p,n=n,steps=steps,assumptions=assumptions,child_counts=child_counts,
        q={"requested":q is not _UNSET,"value":None if q is _UNSET else q},
        schedule={"requested":schedule is not _UNSET,"value":None if schedule is _UNSET else schedule}),lim)
    _require(type(steps) is int and 0 <= steps <= lim["max_forecast_steps"], "categorical_forecast_steps")
    _require(isinstance(child_counts, (list, tuple)), "categorical_child_counts_required")
    _require(len(child_counts) <= lim["max_forecast_steps"] and
             sum(len(x) if isinstance(x, (tuple, list)) else 1 for x in child_counts) <= lim["max_link_objects"], "categorical_path_work_limit")
    # Reject arbitrary/cyclic child payloads before freezing them for the audit.
    _require(all(isinstance(row, (list, tuple)) and all(type(v) in (int, bool, str, float, type(None)) for v in row) for row in child_counts), "categorical_child_payload")
    parent = _distribution(p, classes, a)
    scheduled = schedule is not _UNSET and schedule is not None
    if scheduled:
        _require(isinstance(schedule, (tuple, list)) and len(schedule) == steps, "categorical_schedule_length")
        ns = tuple(_n(v) for v in schedule)
        if n is not None:
            _n(n)  # retained but never substituted for a supplied schedule.
    else:
        _n(n); ns = (n,) * steps
    assumption_reasons = _assumptions(assumptions, scheduled)
    allowed = not assumption_reasons
    d = _calculate("gini_simpson_diversity", lambda: _diversity(parent, a))
    sci = _calculate("structural_concentration_index", lambda: a.sum(a.mul(x, x) for x in parent))
    initial_n = ns[0] if ns else (None if scheduled else n)
    one = (_calculate("conditional_expected_next_diversity", lambda: a.mul(d.value, Fraction(initial_n - 1, initial_n)))
           if allowed and initial_n is not None and d.value is not None else _quantity("conditional_expected_next_diversity", reasons=("null_conditions_or_first_n_unavailable",)))
    omissions = {c: (_calculate("next_step_omission_probability", lambda x=x: a.power(a.add(Fraction(1), -x), initial_n))
                    if allowed and initial_n is not None else _quantity("next_step_omission_probability", reasons=("null_conditions_or_first_n_unavailable",))) for c, x in zip(classes, parent)}
    target = None; target_reason = ()
    if q is _UNSET:
        target_status = "not_requested"
    elif q is None:
        target_status = "unavailable"; target_reason = ("external_target_unknown",)
    else:
        try:
            target = _distribution(q, classes, a); target_status = "available"
        except InputError as exc:
            target_status = "unavailable"; target_reason = ("invalid_external_target", exc.code)
    target_error = (_calculate("squared_target_error", lambda: _distance(parent, target, a)) if target is not None else
                    _quantity("squared_target_error", status=target_status, reasons=target_reason))
    next_error = (_calculate("conditional_expected_next_target_error", lambda: a.add(target_error.value, a.div(d.value, Fraction(initial_n))))
                  if allowed and initial_n is not None and d.value is not None and target_error.value is not None else
                  _quantity("conditional_expected_next_target_error", status="not_requested" if q is _UNSET else "unavailable", reasons=target_reason or ("null_conditions_or_target_unavailable",)))
    shl, crossing, applicability = _half_life(n, d.value, scheduled, allowed, a)
    forecast = (); f_reasons = (); f_status = "available"
    if not allowed or d.value is None:
        f_reasons = assumption_reasons or d.reasons; f_status = "unavailable"
    else:
        try:
            rows = []; multiplier = Fraction(1)
            for i in range(steps + 1):
                if i:
                    multiplier = a.mul(multiplier, Fraction(ns[i-1] - 1, ns[i-1]))
                ed = a.mul(d.value, multiplier)
                el = None if target_error.value is None else a.add(target_error.value, a.add(d.value, -ed))
                rows.append(ForecastPoint(i, None if i == 0 else ns[i-1], multiplier, ed, a.add(Fraction(1), -ed), el))
            forecast = tuple(rows)
            if scheduled:
                if d.value == 0:
                    crossing = _quantity("null_schedule_first_half_crossing", status="undefined", reasons=("no_positive_initial_diversity",), unit=UNIT)
                else:
                    hits = [r.round_index for r in rows[1:] if r.retained_multiplier <= Fraction(1,2)]
                    crossing = (_quantity("null_schedule_first_half_crossing", hits[0], unit=UNIT) if hits else
                                _quantity("null_schedule_first_half_crossing", reasons=("not_reached_in_declared_schedule",), unit=UNIT))
        except _Limit as exc:
            # The requested curve is atomic. No successful-looking truncated prefix.
            f_status = "unavailable"; f_reasons = (exc.code,)
            if scheduled:
                crossing = _quantity("null_schedule_first_half_crossing", reasons=f_reasons, unit=UNIT)
    path = _path(classes, parent, target, child_counts, ns, allowed, a, q is not _UNSET)
    reasons = list(assumption_reasons) + list(target_reason) + list(f_reasons)
    quantities = (d, sci, one, target_error, next_error, shl, crossing, *omissions.values())
    reasons += [r for x in quantities if x.status == "unavailable" for r in x.reasons]
    if any(x.status != "consistent_with_null" for x in path):
        reasons.append("supplied_path_restricted")
    return NullScenario(scenario_id, classes, parent, _support(classes,parent), n, steps, ns if scheduled else None,
        "deterministic_schedule" if scheduled else "fixed_n", freeze(assumptions), "satisfied_for_declared_model" if allowed else "unavailable",
        freeze(original), d, sci, one, freeze(omissions), target, target_status, target_error, next_error, shl, crossing,
        applicability, forecast, f_status, f_reasons, path, "available_with_limitations" if reasons else "available",
        tuple(sorted(set(reasons))), lim)


def mixture_selection(classes, p, e, *, scenario_id: str, class_space_id: str,
                      effective_weight, lambda_unit: str, weights, weight_unit: str, limits=None) -> MixtureSelection:
    """Explicit u=(1-lambda)p+lambda*e, then w*u / sum(w*u).

    This API has no neural-learning output. Unknown weights preserve candidate
    arithmetic but cannot supply a selected distribution or an exogamy claim.
    """
    _require(is_id(scenario_id) and is_id(class_space_id), "categorical_scenario_identity")
    _require(lambda_unit == "effective_preselection_probability", "categorical_effective_weight_unit")
    _require(weight_unit == "reproductive_weight", "categorical_selection_weight_unit")
    lim = _limits(limits); a = _Exact(lim); classes = _classes(classes, lim)
    original = _snapshot(dict(classes=classes,p=p,e=e,effective_weight=effective_weight,weights=weights,
        lambda_unit=lambda_unit,weight_unit=weight_unit),lim)
    parent = _distribution(p, classes, a); external = _distribution(e, classes, a)
    raw_lam = _operand_value(effective_weight)
    lam = None if raw_lam is None else _number(raw_lam, a)
    _require(lam is None or lam <= 1, "categorical_effective_weight_range")
    _require(weights is None or isinstance(weights, (tuple,list)) and len(weights)==len(classes), "categorical_weight_dimension")
    parsed = None if weights is None else tuple(None if _operand_value(x) is None else _number(_operand_value(x), a) for x in weights)
    candidate = selected = None; reasons=[]
    mass = _quantity("selection_normalizing_mass", reasons=("selection_operands_unknown",), unit="reproductive_weight")
    if lam is None:
        reasons.append("effective_preselection_weight_unknown")
    else:
        try:
            candidate = tuple(a.add(a.mul(a.add(Fraction(1), -lam), x), a.mul(lam, y)) for x, y in zip(parent,external))
            _require(a.sum(candidate) == 1, "categorical_mixture_conservation_failure")
            if parsed is None or any(x is None for x in parsed):
                reasons.append("selection_weights_unknown")
            else:
                terms = tuple(a.mul(x, y) for x,y in zip(candidate,parsed))
                total = a.sum(terms); mass = _quantity("selection_normalizing_mass", total, unit="reproductive_weight")
                if total == 0:
                    reasons.append("zero_selected_mass")
                else:
                    selected = tuple(a.div(x,total) for x in terms)
                    _require(a.sum(selected) == 1, "categorical_selection_conservation_failure")
        except _Limit as exc:
            reasons.append(exc.code)
    ps = set(_support(classes,parent)); cs = None if candidate is None else _support(classes,candidate)
    ss = None if selected is None else _support(classes,selected)
    return MixtureSelection(scenario_id,class_space_id,classes,parent,external,lam,weight_unit,lambda_unit,parsed,
        candidate,cs,mass,selected,ss,None if cs is None else tuple(c for c in cs if c not in ps),
        None if cs is None or ss is None else tuple(c for c in cs if c not in ss),
        "undefined" if mass.value == 0 else "unavailable" if reasons else "available",tuple(reasons),
        original,lim)


def evaluate_categorical_null(bundle: LoadedBundle, *, review: lr.LongitudinalReview | None=None) -> CategoricalStudy:
    """Bind existing null declarations; no changes to the old loader or CLI."""
    _require(isinstance(bundle,LoadedBundle), "loaded_bundle_required")
    fresh = lr.review_longitudinal(bundle)
    if review is not None:
        lr.assert_current(review,bundle)
        _require(review == fresh, "altered_longitudinal_binding")
    if not fresh.requested or fresh.configuration is None:
        return CategoricalStudy(fresh.requested,fresh.status,fresh.input_context_sha256,fresh,
                                reasons=tuple(i.code for i in fresh.issues))
    if "categorical_null" not in fresh.configuration["capabilities"]:
        return CategoricalStudy(True,"not_requested",fresh.input_context_sha256,fresh,reasons=("categorical_null_capability_not_declared",))
    results=[]
    for b in fresh.objects:
        if b.ref is None:
            if b.locator.startswith(lr.BASE + "/null_scenarios/"):
                results.append(ScenarioBinding(b,None,"contract_error",tuple(i.code for i in b.issues)))
            continue
        if b.ref.object_kind != "null_scenario":
            continue
        if b.status == "contract_error":
            results.append(ScenarioBinding(b,None,"contract_error",tuple(i.code for i in b.issues))); continue
        d=b.data
        # Known null means the optional q/schedule was deliberately omitted;
        # unknown/unavailable is retained and never changed into that omission.
        qk, sk = knowledge(d["q"]), knowledge(d["schedule"])
        try:
            if sk.state != "known":
                raise InputError("categorical_schedule_declaration_unknown")
            if sk.value is None and knowledge(d["n"]).state != "known":
                raise InputError("categorical_sample_size_unknown")
            result=categorical_null(d["classes"], d["p"], scenario_id=b.ref.object_id,
                n=_operand_value(d["n"]), steps=d["steps"], assumptions=d["assumptions"],
                q=_UNSET if qk.state=="known" and qk.value is None else qk.value if qk.state=="known" else None,
                schedule=_UNSET if sk.value is None else sk.value, child_counts=d["child_counts"], limits=fresh.limits)
            issues=tuple(i.code for i in b.issues)
            results.append(ScenarioBinding(b,result,"available_with_limitations" if issues else result.status,issues,
                "fixture_only" if b.mock_evidence or fresh.configuration["data_role"]=="fixture" else "declared_only"))
        except InputError as exc:
            results.append(ScenarioBinding(b,None,"unavailable" if "resource_limit" in exc.code or "unknown" in exc.code else "contract_error",(exc.code,)))
    status="available_with_limitations" if fresh.issues or any(x.status!="available" for x in results) else "available"
    return CategoricalStudy(True,status,fresh.input_context_sha256,fresh,tuple(results),tuple(i.code for i in fresh.issues))


def assert_current(study: CategoricalStudy, bundle: LoadedBundle) -> None:
    _require(isinstance(study,CategoricalStudy) and study.input_context_sha256 == lr.input_fingerprint(bundle),
             "stale_categorical_null_context")
