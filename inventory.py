"""Step 4: inventories and declared selection before outcome conditioning.

All inputs are already-loaded passive records. No model call, extraction repair,
file access, classification, metric engine, or inference about independence.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Mapping

from .contracts import InputError, RECORD_TYPES, freeze, is_id, knowledge
from .evidence import EvidenceIndex
from .local_io import LoadedBundle
from .records import TypedRecord


@dataclass(frozen=True)
class Count:
    value: int | None
    status: str = "available"
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class Association:
    sample_id: str
    attempt_id: str | None
    group_id: str | None
    position: int | None
    raw_response_ref: Any = field(repr=False)
    output_ref: Any = field(repr=False)
    output_content_hash: Any = field(repr=False)
    extraction_rule_version: Any = field(repr=False)
    span_status: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Position:
    group_id: str
    call_order: int
    index: int
    attempt_id: str | None
    sample_ids: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class Group:
    group_id: str
    sample_ids: tuple[str, ...]
    attempt_ids: tuple[str, ...]
    planned_count: int | None
    call_order: int | None
    position_complete: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class CellInventory:
    cell_id: str
    identity: Mapping[str, Any] = field(repr=False)
    frame_status: str
    frame_reasons: tuple[str, ...]
    realization_count: Count
    identified_sample_ids: tuple[str, ...]
    ambiguous_sample_ids: tuple[str, ...]
    unresolved_rows: tuple[tuple[str, int | None], ...]
    attempt_status_counts: Mapping[str, int]
    recorded_attempt_ids: tuple[str, ...]
    recorded_invocations: int
    attempt_history_status: str
    retry_links: Mapping[str, Any] = field(repr=False)
    selection_status: str
    selection_reasons: tuple[str, ...]
    requested_sample_ids: tuple[str, ...]
    selected_sample_ids: tuple[str, ...]
    selected_count: Count
    excluded_sample_ids: tuple[str, ...]
    selection_basis: Any = field(repr=False)
    order: tuple[str, ...] | None
    order_source: str | None
    order_reasons: tuple[str, ...]
    groups: tuple[Group, ...]
    ungrouped_sample_ids: tuple[str, ...]
    positions: tuple[Position, ...]
    plan_status: str
    plan_reasons: tuple[str, ...]
    extra_sample_ids: tuple[str, ...]
    associations: tuple[Association, ...]
    completion_counts: Mapping[str, int]
    extraction_rule_counts: Mapping[str, int]


@dataclass(frozen=True)
class Inventory:
    cells: tuple[CellInventory, ...]
    input_row_count: int
    malformed_row_count: int
    input_record_type_counts: Mapping[str, int]
    unallocated_rows: tuple[tuple[str, int | None], ...]
    duplicate_identities: tuple[tuple[str, str], ...]
    cross_cell_groups: Mapping[str, tuple[str, ...]]
    acquisition_complete: bool
    input_diagnostics: tuple[Any, ...]
    scientific_independence_established: bool = False


def tagged_value(value: Any) -> Any:
    """Read already typed metadata; malformed data cannot become a default."""
    try:
        obj = knowledge(value)
        return obj.value if obj.state == "known" else None
    except InputError:
        return None


def _reasons(items: Any) -> tuple[str, ...]:
    return tuple(sorted(set(items)))


def _association(index: EvidenceIndex, sample: TypedRecord) -> Association:
    d = sample.data
    aid = tagged_value(d["attempt_id"])
    gid = tagged_value(d["generation_group_id"])
    pos = tagged_value(d["within_group_index"])
    problems: list[str] = []
    attempt = index.get(("attempt", aid)) if aid else None
    if aid and attempt is None:
        problems.append("attempt_reference_unresolved")
    if attempt:
        if attempt.data["analysis_cell_id"] != d["analysis_cell_id"]:
            problems.append("attempt_cell_mismatch")
        expected_group = tagged_value(attempt.data["generation_group_id"])
        if gid and expected_group and expected_group != gid:
            problems.append("attempt_group_mismatch")
        raw = tagged_value(d["raw_response_ref"])
        parent = tagged_value(attempt.data["raw_response_ref"])
        if raw is not None and parent is not None and raw != parent:
            problems.append("raw_response_association_mismatch")
        if attempt.data["attempt_status"] == "not_attempted":
            problems.append("output_from_unattempted_slot")
    span_status = "not_supplied"
    span = d.get("extensions", {}).get("extraction_span")
    if span is not None:
        if (not isinstance(span, Mapping) or set(span) != {"byte_start", "byte_end"}
                or any(type(v) is not int for v in span.values())
                or not 0 <= span["byte_start"] <= span["byte_end"]):
            span_status = "unavailable"
            problems.append("invalid_extraction_span")
        else:
            snapshots = []
            for name in ("raw_response_ref", "output_ref"):
                ref = tagged_value(d[name])
                matches = [a for a in index.bundle.artifacts if ref is not None
                           and a.record_key == ref["record_type"] + ":" + ref["record_id"]]
                snap = None
                if len(matches) == 1 and matches[0].status == "snapshot_read":
                    snap = index.bundle.snapshots.get(matches[0].snapshot_path)
                snapshots.append(snap)
            raw_snap, output_snap = snapshots
            if raw_snap is None or output_snap is None:
                span_status = "unavailable"
            elif span["byte_end"] > raw_snap.size_bytes or raw_snap.content[span["byte_start"]:span["byte_end"]] != output_snap.content:
                span_status = "mismatch"
                problems.append("extraction_span_mismatch")
            else:
                span_status = "bytes_match"
    return Association(sample.record_id, aid, gid, pos, d["raw_response_ref"],
                       d["output_ref"], d["output_content_hash"], d["extraction_rule_version"],
                       span_status, _reasons(problems))


def _positions(selection: Mapping[str, Any] | None, attempts: list[TypedRecord],
               samples: list[TypedRecord], limit: int) -> tuple[tuple[Position, ...], str, tuple[str, ...], str]:
    """A position plan is separate from emitted samples. Retries add no slots."""
    raw = tagged_value(selection["registered_positions"]) if selection else None
    definitions: list[tuple[str, int, int, str | None]] = []
    problems: list[str] = []
    source = "declared_positions"
    if raw is not None:
        if not isinstance(raw, (list, tuple)) or len(raw) > limit:
            return (), "unavailable", ("invalid_position_plan",), source
        for p in raw:
            if (not isinstance(p, Mapping) or set(p) != {"generation_group_id", "registered_call_order", "within_group_index", "attempt_id"}
                    or not is_id(p["generation_group_id"])
                    or type(p["registered_call_order"]) is not int or p["registered_call_order"] <= 0
                    or type(p["within_group_index"]) is not int or p["within_group_index"] <= 0):
                return (), "unavailable", ("invalid_position_plan",), source
            try:
                aid = knowledge(p["attempt_id"])
            except InputError:
                return (), "unavailable", ("invalid_position_attempt",), source
            if aid.state == "known" and aid.value is not None and not is_id(aid.value):
                return (), "unavailable", ("invalid_position_attempt",), source
            definitions.append((p["generation_group_id"], p["registered_call_order"], p["within_group_index"],
                                aid.value if aid.state == "known" else None))
    else:
        source = "recorded_primary_attempts"
        for a in attempts:
            d = a.data
            retry = knowledge(d["retry_of"])
            if retry.state != "known":
                problems.append("attempt_plan_unresolved")
                continue
            if retry.value is not None:
                continue
            group, order, count = (tagged_value(d[k]) for k in ("generation_group_id", "registered_call_order", "planned_candidate_count"))
            if group is None or order is None or count is None:
                problems.append("attempt_plan_unresolved")
                continue
            if count + len(definitions) > limit:
                return (), "unavailable", ("position_plan_limit_exceeded",), source
            definitions.extend((group, order, i, a.record_id) for i in range(1, count + 1))
        if not attempts:
            return (), "unknown", ("position_plan_not_supplied",), source
    keys = [(g, i) for g, _, i, _ in definitions]
    if len(set(keys)) != len(keys):
        problems.append("duplicate_planned_position")
    group_specs: dict[str, set[tuple[int, str | None]]] = defaultdict(set)
    group_positions: dict[str, list[int]] = defaultdict(list)
    order_groups: dict[int, set[str]] = defaultdict(set)
    for g, order, position, aid in definitions:
        group_specs[g].add((order, aid)); order_groups[order].add(g)
        group_positions[g].append(position)
    if any(len(s) != 1 for s in group_specs.values()) or any(len(s) != 1 for s in order_groups.values()):
        problems.append("conflicting_planned_group")
    attempts_by_id = {a.record_id: a for a in attempts}
    for group, spec in group_specs.items():
        positions = group_positions[group]
        if sorted(positions) != list(range(1, len(positions) + 1)):
            problems.append("noncontiguous_planned_positions")
        for order, aid in spec:
            a = attempts_by_id.get(aid)
            if a:
                d = a.data
                retry = knowledge(d["retry_of"])
                if retry.state != "known" or retry.value is not None:
                    problems.append("retry_cannot_be_primary_slot")
                for field_name, expected in (("generation_group_id", group), ("registered_call_order", order),
                                              ("planned_candidate_count", len(positions))):
                    actual = tagged_value(d[field_name])
                    if actual is not None and actual != expected:
                        problems.append("attempt_plan_conflict")
    located: dict[tuple[str, int], list[str]] = defaultdict(list)
    for s in samples:
        gid = tagged_value(s.data["generation_group_id"])
        i = tagged_value(s.data["within_group_index"])
        if gid is not None and i is not None:
            located[(gid, i)].append(s.record_id)
    result = []
    for group, order, i, aid in sorted(definitions, key=lambda p: (p[1], p[2], p[0])):
        ids = tuple(sorted(located[(group, i)]))
        result.append(Position(group, order, i, aid, ids,
                               "missing" if not ids else "present" if len(ids) == 1 else "ambiguous"))
    return tuple(result), "unavailable" if problems else "available", _reasons(problems), source


def build_inventory(bundle: LoadedBundle) -> Inventory:
    """Build each cell separately. Canonical ID sorting is never sampling order."""
    index = EvidenceIndex(bundle)
    cell_ids = sorted(k[1] for k in index.entries if k[0] == "cell")
    types = Counter(); unallocated = []; uncertain = []; declared_by_cell = defaultdict(list)
    for e in bundle.records:
        raw = e.raw
        kind = raw.get("record_type") if isinstance(raw, Mapping) else None
        types[kind if isinstance(kind, str) and kind in RECORD_TYPES else "unrecognized"] += 1
        if kind == "realization" and isinstance(raw, Mapping):
            cid = raw.get("analysis_cell_id")
            if is_id(cid) and cid in cell_ids:
                declared_by_cell[cid].append(e)
            else:
                unallocated.append((e.source, e.line))
        elif e.record is None and e.line is not None and raw is None:
            # This physical line may hide an observation from any cell. Evidence
            # file damage does not make otherwise known observations disappear.
            specs = bundle.manifest.data["record_files"] if bundle.manifest else ()
            if any(s["path"] == e.source and s["role"] == "observations" for s in specs):
                uncertain.append((e.source, e.line))
    unknown_observation_file = False
    if bundle.manifest:
        for spec in bundle.manifest.data["record_files"]:
            if spec["role"] == "observations" and any(d.scope == "file" and d.source == spec["path"] for d in bundle.diagnostics):
                unknown_observation_file = True
    global_groups: dict[str, set[str]] = defaultdict(set)
    cells = []
    for cid in cell_ids:
        cell = index.get(("cell", cid)); frame = None; frame_errors = []
        if cell is None:
            frame_errors.append("cell_identity_unresolved")
        else:
            frame = index.get(("frame", cell.data["frame_id"]))
            protocol = index.get(("protocol", cell.data["generation_protocol_id"]))
            if frame is None:
                frame_errors.append("frame_identity_unresolved")
            elif index.affected(("frame", frame.record_id), {"schema", "registry", "membership"}):
                frame_errors.append("shared_frame_challenged")
            if protocol is None:
                frame_errors.append("protocol_identity_unresolved")
            elif protocol.data["generation_protocol_version"] != cell.data["generation_protocol_version"]:
                frame_errors.append("protocol_version_mismatch")
        samples = []; bad_rows = list(uncertain); ambiguous = set()
        for e in declared_by_cell[cid]:
            raw = e.raw; sid = raw.get("record_id")
            if is_id(sid) and len(index.entries.get(("realization", sid), ())) > 1:
                ambiguous.add(sid)
            s = index.get(("realization", sid)) if is_id(sid) else None
            if s is None:
                bad_rows.append((e.source, e.line))
            else:
                samples.append(s)
        # Only unique, fully identifiable records appear here; bad rows survive
        # in the separate ledger and make the complete inventory count unknown.
        samples.sort(key=lambda r: r.record_id)
        ids = tuple(s.record_id for s in samples)
        id_set = set(ids)
        inv_errors = []
        if bad_rows or ambiguous: inv_errors.append("unresolved_realization_inventory")
        if unknown_observation_file: inv_errors.append("observation_file_incomplete")
        inventory_count = Count(None if inv_errors else len(ids), "unavailable" if inv_errors else "available", _reasons(inv_errors))
        attempts = [r for key in index.entries if key[0] == "attempt" and (r := index.get(key))
                    and r.data["analysis_cell_id"] == cid]
        attempts.sort(key=lambda r: r.record_id)
        associations = tuple(_association(index, s) for s in samples)
        config = bundle.manifest.data["analysis_config"] if bundle.manifest else None
        config_bad = not config or any(d.scope == "analysis_config" for d in bundle.manifest.diagnostics)
        chosen = [] if config_bad else [s for s in config["selection"] if s["analysis_cell_id"] == cid]
        selection = chosen[0] if len(chosen) == 1 else None
        sel_errors = []; requested: tuple[str, ...] = (); selected = ()
        if selection is None:
            sel_errors.append("selection_not_declared")
        else:
            chosen_ids = tagged_value(selection["selected_sample_ids"])
            if chosen_ids is None:
                sel_errors.append("selection_unknown")
            else:
                requested = tuple(chosen_ids)
                if any(s not in id_set for s in requested):
                    sel_errors.append("selected_identity_unresolved")
                selected = tuple(sorted(set(requested).intersection(ids)))
            basis = tagged_value(selection["selection_basis"])
            if not isinstance(basis, str) or not basis.strip(): sel_errors.append("selection_basis_unresolved")
        positions, plan_status, plan_errors, _ = _positions(selection, attempts, samples, bundle.limits.max_records)
        plan_keys = {(p.group_id, p.index) for p in positions}
        extras = tuple(a.sample_id for a in associations if plan_status == "available" and a.group_id is not None
                       and a.position is not None and (a.group_id, a.position) not in plan_keys)
        if set(selected).intersection(extras): sel_errors.append("selected_unrequested_candidate")
        # Duplicate origin declarations cannot supply two genuine observations.
        origins = defaultdict(list)
        for a in associations:
            if a.attempt_id is not None and a.position is not None:
                origins[("attempt", a.attempt_id, a.position)].append(a.sample_id)
            if a.group_id is not None and a.position is not None:
                origins[("group", a.group_id, a.position)].append(a.sample_id)
            sample = index.get(("realization", a.sample_id))
            span = sample.data.get("extensions", {}).get("extraction_span") if sample else None
            raw_ref = tagged_value(a.raw_response_ref)
            if (a.span_status == "bytes_match" and raw_ref is not None and span is not None):
                origins[("span", raw_ref["record_type"], raw_ref["record_id"],
                         span["byte_start"], span["byte_end"])].append(a.sample_id)
        if any(len(set(v).intersection(selected)) > 1 for v in origins.values()):
            sel_errors.append("duplicate_selected_origin")
        order = None; order_source = None; order_errors = []
        if not sel_errors:
            if not selected:
                order = (); order_source = "empty_selected_set"
            else:
                explicit = tagged_value(selection["sample_order"])
                by_sample = {s.record_id: tagged_value(s.data["sample_order"]) for s in samples}
                if explicit is not None:
                    if set(explicit) != set(selected) or len(explicit) != len(selected):
                        order_errors.append("order_inventory_mismatch")
                    else:
                        candidate = tuple(explicit)
                        known_orders = [by_sample[s] for s in candidate if by_sample[s] is not None]
                        if known_orders != sorted(set(known_orders)):
                            order_errors.append("conflicting_sample_order")
                        else:
                            order = candidate; order_source = "explicit_selection_order"
                elif all(by_sample[s] is not None for s in selected):
                    ords = [by_sample[s] for s in selected]
                    if len(set(ords)) != len(ords): order_errors.append("conflicting_sample_order")
                    else:
                        order = tuple(sorted(selected, key=lambda s: by_sample[s])); order_source = "recorded_sample_order"
                else:
                    order_errors.append("missing_sample_order")
        else:
            order_errors.append("selection_unavailable")
        groups = []; grouped = defaultdict(list); ungrouped = []
        for a in associations:
            if a.group_id is None: ungrouped.append(a.sample_id)
            else:
                grouped[a.group_id].append(a.sample_id); global_groups[a.group_id].add(cid)
        positions_by_group = defaultdict(list)
        for position in positions: positions_by_group[position.group_id].append(position)
        attempts_by_group = defaultdict(list)
        attempt_ids = {a.record_id for a in attempts}
        for a in attempts: attempts_by_group[tagged_value(a.data["generation_group_id"])].append(a)
        group_names = set(grouped) | set(positions_by_group)
        by_association = {a.sample_id: a for a in associations}
        for gid in sorted(group_names):
            planned = positions_by_group[gid]
            errs = list(plan_errors)
            related = attempts_by_group[gid]
            if any(p.attempt_id is not None and p.attempt_id not in attempt_ids for p in planned):
                errs.append("planned_attempt_not_recorded")
            if not planned: errs.append("group_plan_unknown")
            if any(p.status != "present" for p in planned): errs.append("group_positions_incomplete")
            for p in planned:
                for sid in p.sample_ids:
                    a = by_association[sid]
                    errs.extend(a.reasons)
                    if p.attempt_id is not None and a.attempt_id != p.attempt_id:
                        errs.append("position_attempt_mismatch")
            if len([a for a in related if tagged_value(a.data["retry_of"]) is not None]) > 0:
                errs.append("group_has_retry_history")
            count = len(planned) if plan_status == "available" else None
            groups.append(Group(gid, tuple(sorted(grouped[gid])), tuple(a.record_id for a in related), count,
                                planned[0].call_order if planned else None,
                                bool(planned) and plan_status == "available" and not errs, _reasons(errs)))
        states = Counter(a.data["attempt_status"] for a in attempts)
        selected_set = set(selected)
        requested_set = set(requested)
        selected_records = [s for s in samples if s.record_id in selected_set]
        completions = Counter(s.data["completion_status"] for s in selected_records)
        extraction = Counter(tagged_value(s.data["extraction_rule_version"]) or "unknown" for s in selected_records)
        cells.append(CellInventory(cid, freeze(dict(cell.data) if cell else {}),
            "unavailable" if frame_errors else "available", _reasons(frame_errors), inventory_count, ids,
            tuple(sorted(ambiguous)), tuple(bad_rows), freeze(dict(states)), tuple(a.record_id for a in attempts),
            sum(states[s] for s in ("succeeded", "failed")),
            "recorded_only" if attempts else "unknown", freeze({a.record_id: a.data["retry_of"] for a in attempts}),
            "unavailable" if sel_errors else "available", _reasons(sel_errors), requested, selected,
            Count(None if sel_errors else len(selected), "unavailable" if sel_errors else "available", _reasons(sel_errors)),
            tuple(s for s in ids if s not in requested_set), freeze(selection["selection_basis"] if selection else {"state":"unknown"}),
            order, order_source, _reasons(order_errors), tuple(groups), tuple(ungrouped), positions, plan_status, plan_errors,
            extras, associations, freeze(dict(completions)), freeze(dict(extraction))))
    return Inventory(tuple(cells), len(bundle.records), sum(e.record is None for e in bundle.records),
        freeze(dict(types)), tuple(unallocated), tuple(sorted(k for k,v in index.entries.items() if len(v)>1)),
        freeze({k:tuple(sorted(v)) for k,v in global_groups.items() if len(v)>1}), bundle.acquisition_complete, bundle.diagnostics)
