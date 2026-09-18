"""Offline input-to-report orchestration for the first measurement milestone.

No generated program is executed and no classification is inferred. Current
numeric results use the imported evidence policy; wider claims remain restricted.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from dataclasses import dataclass, fields
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import platform
from typing import Any, Mapping

from . import __version__
from .contracts import (ADDENDUM_PIN, CLASS_IDS, HERO_IDENTITIES, INTEGRITY_CONDITIONS,
                        SOURCE_PINS, InputError, freeze, is_id, is_hash, knowledge)
from .evidence import EvidenceIndex, review_evidence
from .inventory import build_inventory
from .local_io import LoadedBundle, ReadLimits, load_bundle, publish_report_set
from .metrics import cell_metrics
from .populations import build_populations
from .reporting import (REPORT_VERSION, SECTION_TITLES, canonical_bytes, diagnostic_records,
                        digest, plain, protected, render_json, render_markdown)

# Missing linked evidence is an evidential limitation. Invalid encodings, duplicate
# identities, version conflicts, resource failures and malformed records remain
# processing failures even when supported subpopulations can still be reported.
EVIDENTIAL_DIAGNOSTICS = frozenset({"missing_reference", "invalid_reference_target"})
V_FIELDS = ("surface_lexical_trigram_distance", "within_class_realization_diversity_proxy",
            "structural_pair_non_equivalence", "p1_proxy_gain_contrast",
            "p5_valid_distinct_k_delta", "prompt_resampling_sensitivity")
D_FIELDS = ("observed_intervention_union_size", "gini_simpson_diversity",
            "expressible_support", "latent_support", "convergence_frontier",
            "structural_half_life_null", "structural_half_life_empirical",
            "external_recovery_rate", "probabilistic_structural_assignment")


@dataclass(frozen=True)
class Analysis:
    report: Mapping[str, Any]
    manifest: Mapping[str, Any]
    report_json: bytes
    report_markdown: bytes
    manifest_json: bytes
    exit_code: int


def _software() -> dict[str, Any]:
    # This fixed list names installed implementation files, never input-supplied
    # paths. Tests and the optional benchmark documentation are not imported.
    root = Path(__file__).parent
    names = ("__init__.py", "__main__.py", "cli.py", "contracts.py", "records.py",
             "local_io.py", "evidence.py", "inventory.py", "populations.py",
             "metrics.py", "pipeline.py", "reporting.py")
    hashes = {n: hashlib.sha256((root / n).read_bytes()).hexdigest() for n in names}
    return {"version": __version__, "implementation_sha256": digest(hashes), "files": hashes}


def _input_refs(bundle: LoadedBundle) -> list[dict[str, Any]]:
    return [{"input_id": f"input-{i:04}", "locator_sha256": digest(name),
             "sha256": s.sha256, "size_bytes": s.size_bytes}
            for i, (name, s) in enumerate(sorted(bundle.snapshots.items()), 1)]


def _reference(value: Any) -> Any:
    if isinstance(value, Mapping) and value.get("state") == "known":
        v = value.get("value")
        if is_hash(v):
            return {"state": "known", "value": v}
        if isinstance(v, Mapping) and set(v) == {"record_type", "record_id", "record_version"}:
            return {"state": "known", "value": plain(v)}
    return protected(value)


def _mode(bundle: LoadedBundle) -> tuple[str, tuple[str, ...]]:
    if bundle.manifest is None:
        return "descriptive", ()
    config = bundle.manifest.data["analysis_config"]
    if not isinstance(config, Mapping):
        return "descriptive", ("invalid_analysis_configuration",)
    ext = config.get("extensions", {})
    if not isinstance(ext, Mapping):
        return "descriptive", ("invalid_analysis_configuration",)
    mode = ext.get("prefix_mode", "descriptive")
    if not isinstance(mode, str) or mode not in {"descriptive", "hero"}:
        return "descriptive", ("unsupported_prefix_mode",)
    return mode, ()


def _processing(bundle: LoadedBundle, review: Any, extra: tuple[str, ...] = ()) -> tuple[int, list[str]]:
    failures = [d.code for d in bundle.diagnostics
                if d.severity == "error" and d.code not in EVIDENTIAL_DIAGNOSTICS]
    for check in review.support_checks:
        if check.status == "payload_unresolved":
            failures.extend(check.reasons or ("support_payload_unresolved",))
    failures.extend(extra)
    return (2 if failures else 0), sorted(set(failures))


def validate_bundle(path: str | Path, *, limits: ReadLimits | None = None) -> tuple[dict[str, Any], int]:
    """Passive validation. No distribution calculations or report files."""
    bundle = load_bundle(path, limits=limits)
    review = review_evidence(bundle)
    _, extra = _mode(bundle)
    code, failures = _processing(bundle, review, extra)
    inventory = build_inventory(bundle)
    return {"validation_schema_version": "0.1", "exit_code": code,
            "validation_scope": "record_consistency_only", "input_refs": _input_refs(bundle),
            "contract_failures": failures, "diagnostics": diagnostic_records(bundle.diagnostics),
            "input_acquisition_complete": bundle.acquisition_complete,
            "input_row_count": inventory.input_row_count,
            "cell_count": len(inventory.cells), "malformed_row_count": inventory.malformed_row_count,
            "evidence_status": "supplied_record_checks_only",
            "support_checks": [{"record_id": c.record_id, "status": c.status,
                                "reasons": c.reasons, "mock": c.mock} for c in review.support_checks],
            "independent_validation_performed": False}, code


def _unimplemented(name: str, scope: str) -> dict[str, Any]:
    return {"metric_name": name, "value": None,
            "result_status": "unavailable" if scope == "V" else "deferred",
            "reason": "not_implemented_in_phase1" if scope == "V" else "deferred_capability",
            "capability_scope": scope, "uncertainty_status": "not_estimated"}


def analyze_bundle(path: str | Path, *, limits: ReadLimits | None = None,
                   run_id: str | None = None, recorded_at: str | None = None) -> Analysis:
    """Compute a read-only snapshot. Output publication is a separate operation."""
    if run_id is not None and not is_id(run_id):
        raise InputError("invalid_run_id")
    bundle = load_bundle(path, limits=limits)
    review = review_evidence(bundle)
    collection = build_populations(bundle)
    index = EvidenceIndex(bundle)
    mode, extra = _mode(bundle)
    code, failures = _processing(bundle, review, extra)
    input_refs = _input_refs(bundle)
    software = _software()
    manifest = bundle.manifest
    raw_config = manifest.data["analysis_config"] if manifest else {}
    config = raw_config if isinstance(raw_config, Mapping) else {}
    configuration_sha = digest(config)
    input_sha = digest(input_refs)
    rid = run_id or "run-" + digest({"input": input_sha, "config": configuration_sha,
                                     "software": software["implementation_sha256"]})[:40]
    role = manifest.data["data_role"] if manifest else "unavailable"
    scope = "fixture_only" if role == "fixture" else "finite_sample_label_conditioned_summary"
    config_bad = extra or (manifest and any(d.scope == "analysis_config" for d in manifest.diagnostics))
    frame_rows = []; protocol_rows = []; inventory_rows = []; associations = []
    accounting = []; assignment_rows = []; class_rows = []; metric_rows = []; prefix_rows = []
    group_rows = []; position_rows = []; empty_or_missing = []
    for cell in collection.cells:
        inv = cell.inventory; identity = inv.identity; cid = inv.cell_id
        frame = index.get(("frame", identity.get("frame_id", "")))
        proto = index.get(("protocol", identity.get("generation_protocol_id", "")))
        f = frame.data if frame else {}
        frame_rows.append({"analysis_cell_id": cid, "frame_id": identity.get("frame_id"),
                          **{k: f.get(k) for k in HERO_IDENTITIES},
                          "task_context": protected(f.get("task_context")),
                          "consequence_horizon": protected(f.get("consequence_horizon")),
                          "frame_status": inv.frame_status, "frame_reasons": inv.frame_reasons})
        protocol_rows.append({"analysis_cell_id": cid,
            **{k: identity.get(k) for k in ("generation_protocol_id", "generation_protocol_version",
                                          "condition_id", "prompt_block_id", "prompt_id")},
            **{k: protected(identity.get(k)) for k in ("model_identifier", "model_family", "checkpoint_identifier", "collection_window")},
            **{k: protected(proto.data.get(k)) if proto else {"state": "unavailable"}
               for k in ("conditioning_context_ref", "decoding_settings", "seed")}})
        inventory_rows.append({"analysis_cell_id": cid, "realization_count": plain(inv.realization_count),
            "selected_realization_count": plain(inv.selected_count), "requested_sample_ids": inv.requested_sample_ids,
            "selected_sample_ids": inv.selected_sample_ids, "excluded_sample_ids": inv.excluded_sample_ids,
            "ambiguous_sample_ids": inv.ambiguous_sample_ids, "selection_status": inv.selection_status,
            "selection_reasons": inv.selection_reasons, "selection_basis": protected(inv.selection_basis),
            "attempt_status_counts": inv.attempt_status_counts, "recorded_attempt_ids": inv.recorded_attempt_ids,
            "recorded_invocations": inv.recorded_invocations, "attempt_history_status": inv.attempt_history_status,
            "retry_links": {k: protected(v) for k, v in inv.retry_links.items()},
            "planned_positions": len(inv.positions) if inv.plan_status == "available" else None,
            "plan_status": inv.plan_status, "plan_reasons": inv.plan_reasons,
            "missing_position_count": sum(p.status == "missing" for p in inv.positions),
            "extra_sample_ids": inv.extra_sample_ids, "completion_counts": inv.completion_counts,
            "sample_order": inv.order, "order_source": inv.order_source, "order_reasons": inv.order_reasons,
            "extraction_rule_counts": inv.extraction_rule_counts})
        for g in inv.groups:
            group_rows.append({"analysis_cell_id": cid, **plain(g), "independent_draw_count": None})
        for p in inv.positions:
            position_rows.append({"analysis_cell_id": cid, **plain(p)})
        for a in inv.associations:
            associations.append({"analysis_cell_id": cid, "sample_id": a.sample_id,
                "attempt_id": a.attempt_id, "generation_group_id": a.group_id, "within_group_index": a.position,
                "raw_response_ref": _reference(a.raw_response_ref), "output_ref": _reference(a.output_ref),
                "output_content_hash": _reference(a.output_content_hash),
                "extraction_rule_version": protected(a.extraction_rule_version),
                "span_status": a.span_status, "reasons": a.reasons})
        for d in cell.admissions:
            r = index.get((d.axis, d.record_id)) if d.record_id else None
            assignment_rows.append({"analysis_cell_id": cid, **plain(d),
                "evidence_refs": plain(r.data.get("evidence_refs", ())) if r else [],
                "review_status": r.data.get("assignment_review_status" if d.axis == "assignment" else "validity_review_status") if r else None})
        accounting.append({"analysis_cell_id": cid,
            "classified_all_count": cell.populations["classified_all"].count,
            "classified_valid_count": cell.populations["classified_valid"].count,
            **{k: plain(v) for k, v in cell.ratios.items()},
            "assignment_status_counts": cell.assignment_status_counts,
            "assignment_review_counts": cell.assignment_review_counts,
            "assignment_acceptance_counts": cell.assignment_acceptance_counts,
            "validity_status_counts": cell.validity_status_counts,
            "validity_acceptance_counts": cell.validity_acceptance_counts,
            "withholding_reason_counts": cell.withholding_reason_counts,
            "reason_counts_are_multireason": True})
        kwargs = {}
        if "empirical_threshold" in config:
            kwargs["min_empirical_frequency"] = config["empirical_threshold"]
        ks = config.get("requested_k", ()) if not config_bad else ()
        result = cell_metrics(cell, ks=ks, prefix_mode=mode, **kwargs)
        for view, distribution in result.distributions.items():
            pop = cell.populations[view]
            class_rows.append({"analysis_cell_id": cid, "analysis_population": view,
                "population_size": distribution.population_size, "class_counts": distribution.class_counts,
                "exact_frequencies": distribution.exact_frequencies, "accepted_sample_ids": pop.sample_ids,
                "min_empirical_frequency": plain(distribution.threshold), "input_diagnostics": distribution.input_diagnostics})
            for metric in distribution.results.values():
                metric_rows.append({"analysis_cell_id": cid, "analysis_population": view,
                    "population_size": distribution.population_size, **plain(metric),
                    "evidence_status": "supplied_record_checks_only", "permitted_claim_scope": scope})
        for p in result.prefixes:
            pref = p.source_prefix
            prefix_rows.append({"analysis_cell_id": cid, "analysis_population": pref.view, "k": pref.k,
                "mode": pref.mode, **plain(p.result), "selected_sample_ids": pref.selected_sample_ids,
                "counted_sample_ids": pref.counted_sample_ids, "counted_samples": pref.counted_samples,
                "class_counts": pref.class_counts, "group_ids": pref.group_ids,
                "partial_group_ids": pref.partial_group_ids, "ungrouped_sample_ids": pref.ungrouped_sample_ids,
                "excluded_admissions": plain(pref.excluded_admissions), "independent_draw_count": None})
        if not ks:
            empty_or_missing.append({"analysis_cell_id": cid, "result_status": "unavailable" if config_bad else "not_requested",
                                     "reason": "invalid_analysis_configuration" if config_bad else "k_not_requested"})
    # Payloads are never copied wholesale. These are identity/status summaries,
    # not private annotation text, person mappings, or a flattened source corpus.
    support_rows = []; intake_rows = []; correction_rows = []; claim_rows = []
    for key, record in sorted(index.support.items()):
        p = record.payload
        support_rows.append({"record_type": key[0], "record_id": key[1], "record_version": record.record.record_version,
            "state": p["state"], "data_role": p["data_role"], "mock": p["mock"],
            "origin": protected(p["origin"]), "knowledge_type": protected(p["knowledge_type"]),
            "transformation_refs": p["transformation_refs"], "evidence_refs": p["evidence_refs"],
            "scope_refs": p["scope_refs"], "payload_sha256": digest(p), "access": p.get("access", "not_declared")})
        if key[0] in {"intake", "tail"}:
            intake_rows.append({"record_type": key[0], "record_id": key[1], "state": p["state"],
                "component": p.get("component", "tail_registry"), "stage": p.get("stage"),
                "original_refs": p.get("original_refs", p.get("reference_refs", ())),
                "disposition": protected(p.get("disposition")), "mock": p["mock"],
                "raw_anomaly_retained_in_pinned_input": True, "new_class_inferred": False})
        if key[0] == "correction":
            correction_rows.append({"correction_id": key[1], "effect": p["effect"], "action": p["action"],
                "stage": p["stage"], "event_type": p["event_type"], "target_refs": p["target_refs"],
                "replacement_refs": p["replacement_refs"], "prior_result_ids": p["prior_result_ids"],
                "reason": protected(p["reason"]), "m_fields_recomputed_from_pinned_input": True,
                "v_dependents": "not_implemented", "prior_results_modified": False})
    for check in review.claim_checks:
        p = index.payload(("integrity_assessment", check.record_id))
        outcomes = check.details.get("requirement_record_outcomes", {})
        claim_rows.append({"record_id": check.record_id, "status": check.status, "reasons": check.reasons,
            "declared_disposition": p["declared_disposition"] if p else None, "mock": check.mock,
            "requirement_record_outcomes": {k: outcomes.get(k, "unresolved") for k in INTEGRITY_CONDITIONS},
            "current_until": protected(p["current_until"]) if p else {"state": "unknown"},
            "assessed_at": protected(p["assessed_at"]) if p else {"state": "unknown"},
            "substantive_claim": "not_certified_by_software"})
    integrity_states = [{"condition": name, "outcome": "unresolved",
                         "reason": "no_substantive_independent_validation_performed_by_toolkit",
                         "declared_assessments": [x["record_id"] for x in claim_rows]}
                        for name in INTEGRITY_CONDITIONS]
    checks = [{"record_id": c.record_id, "status": c.status, "reasons": c.reasons,
               "mock": c.mock, "substantive_validation_performed": False,
               "details_sha256": digest(c.details)} for c in review.support_checks]
    omitted = ["deployment representativeness", "all-input program correctness", "long-horizon behavior",
               "causal attribution to recursive training", "complete expressible or latent repertoire"]
    sections = [
        {"scope": {"data_role": role, "permitted_claim_scope": scope,
                   "assignment_evidence_policy_id": config.get("assignment_evidence_policy_id"),
                   "evidence_status": "supplied_record_checks_only", "independent_validation_performed": False,
                   "ud_006": "actual_independent_evidence_outstanding", "phase1_complete": False},
         "task": {"description": "Sort a new list of 0 to 256 integers in [0,4095], preserving multiplicity and the original input. Algorithm-mechanism resolution; membership is imported from evidence, not inferred from returned values.",
                  "known_omitted_conditions": omitted}, "frames": frame_rows, "protocols": protocol_rows,
         "processing": {"exit_code": code, "contract_failures": failures,
                        "input_acquisition_complete": bundle.acquisition_complete},
         "source_pins": dict(SOURCE_PINS), "ec_001_sha256": ADDENDUM_PIN,
         "input_refs": input_refs, "analysis_config_ref": {"sha256": configuration_sha, "analysis_config_id": config.get("analysis_config_id")}},
        {"inventory": inventory_rows, "groups": group_rows, "positions": position_rows,
         "output_associations": associations,
         "unallocated_inventory": {"input_row_count": collection.inventory.input_row_count,
             "malformed_row_count": collection.inventory.malformed_row_count,
             "input_record_type_counts": collection.inventory.input_record_type_counts,
             "unallocated_record_count": len(collection.inventory.unallocated_rows),
             "duplicate_identities": collection.inventory.duplicate_identities,
             "cross_cell_groups": collection.inventory.cross_cell_groups},
         "diagnostics": diagnostic_records(bundle.diagnostics)},
        {"accounting": accounting, "admissions": assignment_rows},
        {"distributions": class_rows, "metrics": metric_rows,
         "numerical_policy": {"log_base": "e", "absolute_tolerance": 1e-12, "relative_tolerance": 1e-10,
                              "counts_and_threshold_membership": "exact", "uncertainty_status": "not_estimated"}},
        {"prefixes": prefix_rows, "unrequested_prefixes": empty_or_missing,
         "reference_coverage": {"registered_class_ids": CLASS_IDS, "registry_version": "0.1",
             "status": "definition_inventory_only", "independent_validation": "not_performed_by_toolkit",
             "zero_count_entries_retained": True, "reference_items_are_model_samples": False}},
        {"comparisons": [_unimplemented(n, "V") for n in V_FIELDS[2:]],
         "claim_boundary": "No P1/P5 support, contradiction, quality gate, matched-budget or interval conclusion is computed in Phase 1."},
        {"diagnostics": [_unimplemented(n, "V") for n in V_FIELDS[:2]],
         "source_text_status": "No source-text metric is implemented; HF fixtures contain no program bodies."},
        {"five_conditions": integrity_states, "declared_claim_records": claim_rows,
         "support_records": support_rows, "support_checks": checks, "intake_and_tail": intake_rows,
         "corrections": correction_rows, "correction_impacts": plain(review.corrections),
         "preserved_revision_ids": review.preserved_revision_ids,
         "ec_reporting_disclosures": {"capability_and_scope": "section_1", "structural_cut_and_known_omissions": "section_1",
             "source_and_transformation_lineage": "support_records_and_pinned_input", "exposure_and_bias_controls": "declared_records_only",
             "evaluator_identity": "record_ids_only_private_mappings_omitted", "class_and_tail_outcomes": "sections_4_and_5",
             "horizon_recovery_override": "not_evaluated", "live_field_evidence": "not_established_by_toolkit",
             "correction_path": "new_pinned_input_and_new_output_directory_prior_results_preserved",
             "current_until": {"state": "unknown", "reason": "No toolkit-established expiry; supplied declarations remain scoped."}},
         "deferred": [_unimplemented(n, "D") for n in D_FIELDS],
         "release_restrictions": ["No empirical validation or deployment certification.", "No package publication or hosted CI performed by this command.",
                                  "Phase 1 integrated acceptance and final audit remain pending."],
         "redaction": {"raw_bodies": "omitted", "private_identity_mappings": "omitted", "private_paths": "hashed",
                       "unrestricted_evidence_prose": "hashed", "source_bytes_modified": False,
                       "limitation": "Hashes and supplied record IDs permit local audit; a public report alone cannot reproduce withheld evidence."}},
    ]
    report = {"report_schema_version": REPORT_VERSION, "run_id": rid,
              "study_id": manifest.data["study_id"] if manifest else None,
              "bundle_id": manifest.data["bundle_id"] if manifest else None,
              "input_schema_version": manifest.data["input_schema_version"] if manifest else None,
              "input_fingerprint": input_sha, "software_version": __version__,
              "implementation_sha256": software["implementation_sha256"],
              "sections": [{"number": i, "title": title, "content": content}
                           for i, (title, content) in enumerate(zip(SECTION_TITLES, sections), 1)]}
    report = plain(report)
    out_json, out_md = render_json(report), render_markdown(report)
    now = recorded_at or datetime.now(timezone.utc).isoformat()
    # Explicit supplied time is metadata, not an experiment time or currentness grant.
    if not isinstance(now, str) or len(now) > 64:
        raise InputError("invalid_recorded_at")
    try:
        supplied_time = datetime.fromisoformat(now.replace("Z", "+00:00"))
        if supplied_time.tzinfo is None or supplied_time.utcoffset().total_seconds() != 0:
            raise ValueError("UTC timestamp required")
    except ValueError as exc:
        raise InputError("invalid_recorded_at") from exc
    run_manifest = {"run_manifest_version": "0.1", "run_id": rid, "recorded_at_utc": now,
        "input_refs": input_refs, "input_fingerprint": input_sha, "analysis_config_sha256": configuration_sha,
        "software": software, "python_version": platform.python_version(), "python_implementation": platform.python_implementation(),
        "platform": platform.system(), "read_limits": plain(bundle.limits), "total_read_bytes": bundle.total_read_bytes,
        "processing_exit_code": code, "input_acquisition_complete": bundle.acquisition_complete,
        "report_files": {"report.json": hashlib.sha256(out_json).hexdigest(), "report.md": hashlib.sha256(out_md).hexdigest()},
        "replay_variable_fields": ["recorded_at_utc", "python_version", "python_implementation", "platform"],
        "source_pins": dict(SOURCE_PINS), "ec_001_sha256": ADDENDUM_PIN,
        "independent_validation_performed": False, "model_calls": 0, "candidate_programs_executed": 0,
        "output_publication": "complete_directory_atomic_noreplace"}
    return Analysis(freeze(report), freeze(run_manifest), out_json, out_md, canonical_bytes(run_manifest), code)


def write_analysis(analysis: Analysis, output_dir: str | Path, *, bundle_path: str | Path) -> None:
    """Never overwrite inputs or an existing run. Serialization already succeeded."""
    if not isinstance(analysis, Analysis):
        raise InputError("invalid_analysis_result")
    publish_report_set(output_dir, {"report.json": analysis.report_json, "report.md": analysis.report_markdown,
                                   "run_manifest.json": analysis.manifest_json}, bundle_path=bundle_path)
