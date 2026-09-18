"""Step 4: exact accepted populations, coverage and prespecified prefixes.

Uses the existing evidence policy. No entropy, SCI, thresholded support,
resampling, comparison, model inference or report rendering is implemented here.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import Any, Mapping

from .contracts import CLASS_IDS, InputError, freeze
from .evidence import Admission, EvidenceIndex
from .inventory import CellInventory, Inventory, build_inventory
from .local_io import LoadedBundle


@dataclass(frozen=True)
class Ratio:
    numerator: int | None
    denominator: int | None
    status: str
    reason: str | None = None

    @property
    def value(self) -> Fraction | None:
        return Fraction(self.numerator, self.denominator) if self.status == "available" else None


def _ratio(numerator: int | None, denominator: int | None) -> Ratio:
    if numerator is None or denominator is None:
        return Ratio(numerator, denominator, "unavailable", "inventory_unavailable")
    if denominator == 0:
        return Ratio(numerator, denominator, "undefined", "empty_denominator")
    return Ratio(numerator, denominator, "available")


@dataclass(frozen=True)
class Population:
    name: str
    status: str
    sample_ids: tuple[str, ...]
    class_counts: Mapping[str, int]
    reasons: tuple[str, ...] = ()

    @property
    def count(self) -> int | None:
        return len(self.sample_ids) if self.status == "available" else None


@dataclass(frozen=True)
class CellPopulations:
    inventory: CellInventory
    populations: Mapping[str, Population]
    admissions: tuple[Admission, ...]
    ratios: Mapping[str, Ratio]
    assignment_status_counts: Mapping[str, int]
    assignment_acceptance_counts: Mapping[str, int]
    assignment_review_counts: Mapping[str, int]
    validity_status_counts: Mapping[str, int]
    validity_acceptance_counts: Mapping[str, int]
    withholding_reason_counts: Mapping[str, int]
    reason_counts_are_multireason: bool = True
    independent_validation_performed: bool = False


@dataclass(frozen=True)
class PopulationCollection:
    inventory: Inventory
    cells: tuple[CellPopulations, ...]


@dataclass(frozen=True)
class Prefix:
    cell_id: str
    view: str
    k: int | None
    mode: str
    status: str
    selected_sample_ids: tuple[str, ...]
    counted_sample_ids: tuple[str, ...]
    class_counts: Mapping[str, int]
    distinct_count: int | None
    reasons: tuple[str, ...]
    group_ids: tuple[str, ...]
    partial_group_ids: tuple[str, ...]
    ungrouped_sample_ids: tuple[str, ...]
    excluded_admissions: tuple[Admission, ...] = field(repr=False)
    independent_draw_count: None = None
    unit: str = "classes_among_k_realization_prefix"
    selection_rule: str = "prespecified_prefix_without_replacement"

    @property
    def counted_samples(self) -> int | None:
        return len(self.counted_sample_ids) if self.status == "available" else None


def build_populations(bundle: LoadedBundle) -> PopulationCollection:
    """Selection is resolved before reading outcomes; every cell stays separate."""
    inventories = build_inventory(bundle)
    index = EvidenceIndex(bundle)
    results = []
    for inv in inventories.cells:
        decisions = []
        assoc_errors = {a.sample_id: a.reasons for a in inv.associations if a.reasons}
        for sid in inv.selected_sample_ids:
            for axis in ("assignment", "validity"):
                decision = index.admit(axis, sid)
                if sid in assoc_errors:
                    decision = replace(decision, status="withheld", outcome=None,
                                       reasons=tuple(sorted(set(decision.reasons + assoc_errors[sid]))))
                decisions.append(decision)
        by_axis = {(d.axis, d.sample_id): d for d in decisions}
        base_reasons = inv.selection_reasons + inv.frame_reasons
        class_ok = not base_reasons
        all_ids = tuple(s for s in inv.selected_sample_ids if by_axis[("assignment",s)].status == "accepted")
        valid_ids = tuple(s for s in inv.selected_sample_ids
                          if by_axis[("validity",s)].status == "accepted" and by_axis[("validity",s)].outcome == "valid")
        decisive_ids = tuple(s for s in inv.selected_sample_ids
                             if by_axis[("validity",s)].status == "accepted" and by_axis[("validity",s)].outcome in {"valid","invalid"})
        valid_set = set(valid_ids)
        good_ids = tuple(s for s in all_ids if s in valid_set)
        populations = {}
        for name, ids in (("classified_all",all_ids),("classified_valid",good_ids)):
            counts = {c:0 for c in CLASS_IDS}
            for sid in ids: counts[by_axis[("assignment",sid)].outcome] += 1
            populations[name] = Population(name, "available" if class_ok else "unavailable",
                ids if class_ok else (), freeze(counts if class_ok else {}), tuple(sorted(set(base_reasons))))
        # Validity is a parallel axis. A broken structural frame does not create
        # a zero-size distribution; its class-conditioned ratios are unavailable.
        n = inv.selected_count.value
        all_n = populations["classified_all"].count
        good_n = populations["classified_valid"].count
        valid_n = len(valid_ids) if inv.selection_status == "available" else None
        decisive_n = len(decisive_ids) if inv.selection_status == "available" else None
        ratios = {
            "classification_coverage": _ratio(all_n,n),
            "valid_fraction_selected": _ratio(valid_n,n),
            "decisive_validity_coverage": _ratio(decisive_n,n),
            "classified_valid_coverage": _ratio(good_n,valid_n),
            "classified_valid_fraction": _ratio(good_n,all_n),
        }
        statuses = Counter(); acceptance = Counter(); reviews = Counter(); validity = Counter(); v_accept = Counter(); reasons = Counter()
        for d in decisions:
            # Input-status accounting survives a failed frame/admission gate.
            # Resolve only an explicit, unique revision; never guess the latest.
            pins = bundle.manifest.data["analysis_config"].get(d.axis + "_pins", ())
            choices = [p for p in pins if p["sample_id"] == d.sample_id]
            rec = index.get((d.axis, choices[0][d.axis + "_id"])) if len(choices) == 1 else None
            if rec and (rec.data["sample_id"] != d.sample_id or rec.data[d.axis + "_version"] != choices[0][d.axis + "_version"]):
                rec = None
            if d.axis == "assignment":
                statuses[rec.data["assignment_status"] if rec else "missing_or_unavailable"] += 1
                reviews[rec.data["assignment_review_status"] if rec else "missing_or_unavailable"] += 1
                acceptance[d.status] += 1
            else:
                v_accept[d.status] += 1
                validity[d.outcome if d.status == "accepted" else d.status] += 1
            reasons.update(d.reasons)
        results.append(CellPopulations(inv, freeze(populations), tuple(decisions), freeze(ratios),
            freeze(dict(statuses)), freeze(dict(acceptance)), freeze(dict(reviews)), freeze(dict(validity)),
            freeze(dict(v_accept)), freeze(dict(reasons))))
    return PopulationCollection(inventories, tuple(results))


def prefix(cell: CellPopulations, k: int | None, view: str = "classified_all", *, mode: str = "descriptive") -> Prefix:
    """One fixed prefix, with an additional complete-group gate for HERO mode."""
    if not isinstance(view, str) or view not in {"classified_all","classified_valid"}: raise InputError("unsupported_population_view")
    if not isinstance(mode, str) or mode not in {"descriptive","hero"}: raise InputError("unsupported_prefix_mode")
    if k is not None and (type(k) is not int or k <= 0): raise InputError("invalid_requested_k")
    inv = cell.inventory; pop = cell.populations[view]
    reasons: list[str] = []; chosen: tuple[str, ...] = ()
    status = "available"
    if k is None:
        status = "not_requested"; reasons.append("k_not_requested")
    elif pop.status != "available":
        status = "unavailable"; reasons.extend(pop.reasons)
    elif inv.order is None:
        status = "unavailable"; reasons.extend(inv.order_reasons or ("missing_sample_order",))
    elif len(inv.order) < k:
        status = "unavailable"; reasons.append("insufficient_prefix_length")
    else:
        chosen = inv.order[:k]
    if status == "available" and mode == "hero":
        groups = sorted((g for g in inv.groups if g.planned_count is not None), key=lambda g: g.call_order or 0)
        if (k not in {5,10,20} or inv.plan_status != "available" or len(groups) != 4
                or [g.call_order for g in groups] != [1,2,3,4] or any(g.planned_count != 5 for g in groups)):
            reasons.append("hero_plan_unavailable")
        else:
            early = groups[:k//5]
            if any(not g.position_complete for g in early): reasons.append("intended_groups_incomplete")
            positions = [p for p in inv.positions if p.call_order <= k//5]
            intended = tuple(p.sample_ids[0] for p in positions if p.status == "present")
            if len(intended) != k or intended != chosen:
                reasons.append("intended_prefix_mismatch")
            if not all(s in inv.selected_sample_ids for s in intended): reasons.append("intended_position_not_selected")
        if reasons: status = "unavailable"
    included = set(chosen)
    group_ids = []; partial = []
    for g in inv.groups:
        subset = included.intersection(g.sample_ids)
        if not subset: continue
        group_ids.append(g.group_id)
        if subset != set(g.sample_ids) or (g.planned_count is not None and len(subset) < g.planned_count):
            partial.append(g.group_id)
    ungrouped = tuple(s for s in chosen if s in inv.ungrouped_sample_ids)
    pop_ids = set(pop.sample_ids)
    counted = tuple(s for s in chosen if s in pop_ids) if status == "available" else ()
    counts = {c:0 for c in CLASS_IDS} if status == "available" else {}
    assignment = {d.sample_id:d for d in cell.admissions if d.axis == "assignment"}
    for s in counted: counts[assignment[s].outcome] += 1
    excluded = tuple(d for d in cell.admissions if d.sample_id in included and d.sample_id not in counted)
    return Prefix(inv.cell_id,view,k,mode,status,chosen,counted,freeze(counts),
                  sum(c>0 for c in counts.values()) if status == "available" else None,
                  tuple(sorted(set(reasons))),tuple(group_ids),tuple(partial),ungrouped,excluded)


def accumulation(cell: CellPopulations, ks: tuple[int, ...] | list[int], *, mode: str = "descriptive") -> tuple[Prefix, ...]:
    """Use the requested increasing grid unchanged; no adaptive k selection."""
    if not isinstance(ks,(tuple,list)) or any(type(k) is not int or k <= 0 for k in ks):
        raise InputError("invalid_accumulation_grid")
    if list(ks) != sorted(set(ks)): raise InputError("invalid_accumulation_grid")
    return tuple(prefix(cell,k,v,mode=mode) for k in ks for v in ("classified_all","classified_valid"))
