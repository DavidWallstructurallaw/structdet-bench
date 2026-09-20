"""Passive longitudinal profile orchestration and bounded public projections.

The numerical components consume one immutable safe-loaded bundle. Replay is an
optional separately acquired run manifest, never an executable input or a reason
to regenerate missing indices. Scientific limitations are distinct from malformed
input. SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import platform
from types import SimpleNamespace
from typing import Mapping

from . import __version__
from .contracts import ADDENDUM_PIN, INTEGRITY_CONDITIONS, SOURCE_PINS, InputError, freeze
from .evidence import EvidenceIndex, review_evidence
from .comparison_records import configuration_fingerprint
from .inventory import build_inventory
from .local_io import LocalReader, parse_json_bytes
from .reporting import canonical_bytes, diagnostic_records, digest, plain, protected, render_json, render_markdown
from . import longitudinal_records as lr, longitudinal as lg, categorical_null as cn
from . import half_life as hl, longitudinal_uncertainty as lu, support_assays as sa, recovery as rc

PROFILE = lr.PROFILE
VERSION = "0.3"
METHOD = "longitudinal_pipeline_v1"
METHODS = freeze({"records": lr.METHOD, "observed": lg.METHOD, "categorical_null": cn.METHOD,
    "half_life": hl.METHOD, "local_half_life": hl.INTERVAL_METHOD, "sensitivity": lu.METHOD,
    "support_assay": sa.METHOD, "recovery": rc.METHOD, "pipeline": METHOD})
FROZEN_PREDECESSOR = freeze({"phase": 3, "step": 7, "file_count": 153,
    "git_tree_sha": "6e7a371b10ce7e9922485482bcf88b3c8b031416",
    "commit_sha": "e56d83d0a47fdfea7e1d4707c7d20e3acdfa25ea",
    "archive_sha256": "b25d9f63f81bc70b265d2e82182f1e4800a0ae500abe29d1e36d642c6f1e5ab0",
    "approved_phase3_plan_sha256": lu.APPROVED_PLAN_SHA256,
    "scope": "historical_frozen_delivery_not_current_repository_assertion"})


def _require(ok, code):
    if not ok:
        raise InputError(code)


def requested(bundle):
    """Presence, including malformed/null declarations, selects this profile."""
    if bundle.manifest is None:
        return False
    cfg = bundle.manifest.data.get("analysis_config")
    ext = cfg.get("extensions") if isinstance(cfg, Mapping) else None
    return isinstance(ext, Mapping) and "longitudinal" in ext


def software_identity():
    from .pipeline import _software
    result = _software()
    names = ("longitudinal_records.py", "longitudinal.py", "categorical_null.py", "half_life.py",
             "longitudinal_uncertainty.py", "support_assays.py", "recovery.py", "longitudinal_pipeline.py")
    hashes = dict(result["files"])
    root = Path(__file__).parent
    hashes.update({name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names})
    return {"version": __version__, "implementation_sha256": digest(hashes), "files": hashes}


_OMIT = {"review", "populations", "source_cell", "original", "original_operands", "observed", "fits", "half_lives",
         "pre_assay", "post_assay", "registration", "plan"}
_PRIVATE = {"selection_rule", "selection_basis", "old_identity", "new_identity", "designation",
            "rationale", "configuration_identities", "reason", "conditioning"}


def _retained_record(value):
    """Keep source record identities while withholding arbitrary payload prose."""
    from .pipeline import _metadata_details
    if not isinstance(value, Mapping):
        return protected(value)
    ref = {k: value.get(k) for k in ("record_type", "record_id", "record_version")}
    result = {"record_ref": ref, "record_sha256": digest(value),
              "original_record_retained_in_pinned_input": True}
    payload = value.get("payload")
    if isinstance(payload, Mapping):
        result["payload_sha256"] = digest(payload)
        result.update({k: plain(payload[k]) for k in ("state", "data_role", "mock", "access") if k in payload})
        result.update({k: protected(payload[k]) for k in ("origin", "knowledge_type") if k in payload})
        result.update({k: plain(payload[k]) for k in ("evidence_refs", "transformation_refs", "scope_refs") if k in payload})
        result["details"] = _metadata_details(ref["record_type"], payload)
    else:
        result["content"] = protected(value)
    return result


def _public(value, key=None):
    """Project trusted typed results; source payloads are never copied wholesale."""
    if key in _PRIVATE:
        return protected(value)
    if key in {"source_records", "original_records"}:
        return [_retained_record(x) for x in value]
    if key == "subject_identity":
        result = protected(value)
        if isinstance(value, Mapping) and value.get("state") == "known" and isinstance(value.get("value"), Mapping):
            result["components"] = {k: _public(v) if k in {"checkpoint_sha256", "material_refs", "unit", "classes"}
                                    else protected(v) for k, v in value["value"].items()}
        return result
    if isinstance(value, lr.Issue):
        return {"code": value.code, "severity": value.severity, "locator_sha256": digest(value.locator)}
    if isinstance(value, lr.ObjectBinding):
        return binding_record(value)
    if is_dataclass(value):
        return {f.name: _public(getattr(value, f.name), f.name) for f in fields(value)
                if f.name not in _OMIT and f.name != "locator"}
    if isinstance(value, Mapping):
        # Knowledge reasons may contain unrestricted input prose. Keep state,
        # typed operands/references and evidence, with only the reason protected.
        return {k: _public(v, k) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_public(x, key) for x in value]
    return plain(value)


def binding_record(obj):
    result = {"ref": plain(obj.ref), "status": obj.status, "issues": _public(obj.issues),
              "locator_sha256": digest(obj.locator), "mock_evidence": obj.mock_evidence,
              "substantive_validation_performed": False}
    # Only shape-valid objects enter the semantic projection. Failed raw objects
    # can contain arbitrary keys, free text and private paths.
    if obj.ref is not None and obj.status != "contract_error":
        result["declaration"] = _public(obj.data)
    else:
        result["declaration"] = protected(obj.data)
    return result


def binding_report(review):
    return {"requested": review.requested, "status": review.status,
            "input_context_sha256": review.input_context_sha256,
            "configuration_sha256": review.configuration_sha256,
            "issues": _public(review.issues), "objects": [binding_record(x) for x in review.objects],
            "limits": plain(review.limits), "work": plain(review.work),
            "bound_cell_ids": list(review.bound_cell_ids), "statistics_computed": False,
            "substantive_validation_performed": False}


def _sensitivity_requests(review):
    if review.configuration is None or "half_life" not in review.configuration["capabilities"]:
        return ()
    return tuple(x for x in review.objects if x.ref and x.ref.object_kind == "shl_request" and x.status != "contract_error"
                 and not (isinstance(x.data.get("sensitivity_ref"), Mapping)
                          and x.data["sensitivity_ref"].get("state") == "known"
                          and x.data["sensitivity_ref"].get("value") is None))


def _plan(bundle, review, obj):
    # _read_plan checks only declarative/artifact identity; this stub supplies the
    # panel refs from the request without constructing a numerical curve or fit.
    request = SimpleNamespace(ref=obj.ref, original=obj.data,
        prepared=SimpleNamespace(panel_refs=tuple(lg._ref(x) for x in obj.data["panel_refs"])))
    return lu._read_plan(bundle, review, request)


def _plan_replay_identity(bundle, review, obj):
    plan = _plan(bundle, review, obj)
    if plan["unit"] == "probe_panel":
        ids = tuple(x["object_id"] for x in plan["panel_refs"])
    else:
        rows = [lg._resolve(review, x) for x in plan["trajectory_refs"]]
        _require(all(x is not None for x in rows), "replay_trajectory_binding_unavailable")
        ids = tuple(x.data["root_ref"]["object_id"] for x in rows)
    return plan, ids, configuration_fingerprint({"input": review.input_context_sha256, "request": obj.data, "plan": plan})


def _record_replay_blockers(bundle, review, obj):
    """Prove source-gated absence without calculating an observed curve or fit."""
    tag = obj.data.get("sensitivity_ref")
    if not isinstance(tag, Mapping) or tag.get("state") != "known" or tag.get("value") is None:
        return ("sensitivity_request_unresolved",)
    try:
        plan, ids, _ = _plan_replay_identity(bundle, review, obj)
        if plan["unit"] == "probe_panel":
            groups = ids
        else:
            trajectories = [lg._resolve(review, x) for x in plan["trajectory_refs"]]
            roots = [lg._resolve(review, x.data["root_ref"]) for x in trajectories]
            _require(all(x is not None for x in roots), "replay_root_binding_unavailable")
            groups = tuple(lg._value(x.data["dependency_group"]) for x in roots)
        reasons, _ = lu._dependency(bundle, SimpleNamespace(review=review), obj, plan, ids, groups)
        return reasons
    except InputError as exc:
        return (exc.code,)


def _expected_files(bundle):
    return [{"role": x["role"], "expected_sha256": _public(x["expected_sha256"]), "locator_sha256": digest(x["path"])}
            for x in bundle.manifest.data["record_files"]]


def _artifact_acquisition(bundle):
    return [{"record_key": x.record_key, "status": x.status, "expected_sha256": x.expected_sha256,
             "actual_sha256": x.actual_sha256, "locator_sha256": digest(x.snapshot_path) if x.snapshot_path else None}
            for x in bundle.artifacts]


def read_replay_manifest(path, bundle, review, software):
    """Acquire a passive bounded carrier using the same no-follow reader."""
    if path is None:
        return None, None
    _require(review.configuration is not None, "replay_requires_valid_longitudinal_profile")
    p = Path(path)
    with LocalReader(p.parent, bundle.limits) as reader:
        snapshot = reader.read(p.name)
    _require(bundle.total_read_bytes + snapshot.size_bytes <= bundle.limits.max_bundle_bytes,
             "bundle_size_exceeded")
    carrier = parse_json_bytes(snapshot.content, bundle.limits)
    _require(isinstance(carrier, Mapping) and carrier.get("report_profile") == PROFILE
             and carrier.get("run_manifest_version") == VERSION, "longitudinal_replay_manifest_profile")
    _require(carrier.get("software") == software, "longitudinal_replay_software_mismatch")
    _require(carrier.get("source_pins") == dict(SOURCE_PINS) and carrier.get("ec_001_sha256") == ADDENDUM_PIN
             and carrier.get("longitudinal_methods") == METHODS, "longitudinal_replay_method_identity")
    from .pipeline import _input_refs
    _require(carrier.get("input_refs") == _input_refs(bundle)
             and carrier.get("analysis_config_sha256") == digest(bundle.manifest.data["analysis_config"])
             and carrier.get("read_limits") == plain(bundle.limits), "longitudinal_replay_input_identity")
    _require(carrier.get("input_fingerprint") == digest(_input_refs(bundle))
             and carrier.get("input_context_sha256") == review.input_context_sha256
             and carrier.get("longitudinal_limits") == plain(review.limits)
             and carrier.get("expected_record_files") == _expected_files(bundle)
             and carrier.get("artifact_acquisition") == _artifact_acquisition(bundle)
             and carrier.get("input_acquisition_complete") == bundle.acquisition_complete
             and type(carrier.get("processing_exit_code")) is int and carrier["processing_exit_code"] == 0,
             "longitudinal_replay_manifest_coherence")
    collection = carrier.get("longitudinal_replay")
    keys = {"schema_version", "profile", "input_context_sha256", "configuration_sha256", "implementation_sha256", "entries", "sha256"}
    _require(isinstance(collection, Mapping) and set(collection) == keys, "longitudinal_replay_collection_fields")
    _require(collection["schema_version"] == "0.1" and collection["profile"] == PROFILE
             and collection["input_context_sha256"] == review.input_context_sha256
             and collection["configuration_sha256"] == review.configuration_sha256
             and collection["implementation_sha256"] == software["implementation_sha256"], "longitudinal_replay_collection_context")
    _require(collection["sha256"] == digest({k: v for k, v in collection.items() if k != "sha256"})
             and carrier.get("longitudinal_replay_sha256") == digest(collection), "longitudinal_replay_collection_digest")
    entries = collection["entries"]
    expected = _sensitivity_requests(review)
    _require(isinstance(entries, (tuple, list)) and len(entries) == len(expected), "longitudinal_replay_complete_request_set")
    replays = {}
    for entry, obj in zip(entries, expected):
        _require(isinstance(entry, Mapping) and set(entry) == {"request_ref", "status", "reasons", "replay"}, "longitudinal_replay_entry_fields")
        _require(entry["request_ref"] == plain(obj.ref), "longitudinal_replay_request_order")
        _require(entry["status"] in {"available", "unavailable"} and isinstance(entry["reasons"], (tuple, list))
                 and all(isinstance(x, str) and len(x) <= 200 for x in entry["reasons"]), "longitudinal_replay_entry_status")
        saved = entry["replay"]
        if saved is None:
            _require(entry["status"] == "unavailable", "longitudinal_replay_missing_indices")
            blockers = _record_replay_blockers(bundle, review, obj)
            _require(bool(set(blockers) & set(entry["reasons"]))
                     and not any(x.startswith(("explicit_", "longitudinal_replay_", "replay_for_")) for x in entry["reasons"]),
                     "longitudinal_replay_missing_indices")
            # An explicit non-null sentinel prevents all generation paths. The
            # independently verified source gate returns before matrix use; if
            # it unexpectedly does not, component replay validation rejects it.
            saved = freeze({"source_gated_no_indices": True})
        else:
            plan, ids, context = _plan_replay_identity(bundle, review, obj)
            lu.validate_replay(saved, ids, unit=plan["unit"], context_sha256=context, plan_sha256=configuration_fingerprint(plan))
        replays[obj.ref.object_id] = saved
    return freeze(replays), freeze({"sha256": snapshot.sha256, "size_bytes": snapshot.size_bytes,
                                   "locator_sha256": digest(str(path)), "collection": collection})


_ABSENT_PLAN = {"sensitivity_plan_binding_unavailable", "sensitivity_plan_artifact_unavailable", "sensitivity_request_unresolved"}


def longitudinal_validation(bundle, *, replay_manifest_path=None, review=None, software=None):
    """Shape, provenance and replay checks only; no numerical estimator calls."""
    review = lr.review_longitudinal(bundle) if review is None else review
    failures = {x.code for x in review.issues if x.severity == "contract_error"}
    if review.status == "contract_error" and not failures:
        failures.add("longitudinal_contract_error")
    for obj in _sensitivity_requests(review):
        tag = obj.data.get("sensitivity_ref")
        if not isinstance(tag, Mapping) or tag.get("state") != "known" or tag.get("value") is None:
            continue
        try:
            _plan(bundle, review, obj)
        except InputError as exc:
            if exc.code not in _ABSENT_PLAN:
                failures.add(exc.code)
    replay = receipt = None
    if replay_manifest_path is not None:
        try:
            replay, receipt = read_replay_manifest(replay_manifest_path, bundle, review, software or software_identity())
        except InputError as exc:
            failures.add(exc.code)
    report = binding_report(review)
    report["replay_status"] = "not_supplied" if replay_manifest_path is None else "contract_error" if receipt is None else "structure_and_context_verified"
    return report, tuple(sorted(failures)), replay, receipt


def validate_snapshot(bundle, *, replay_manifest_path=None):
    from .pipeline import _input_refs, _mode, _processing
    evidence = review_evidence(bundle)
    _, extra = _mode(bundle)
    report, errors, _, _ = longitudinal_validation(bundle, replay_manifest_path=replay_manifest_path)
    code, failures = _processing(bundle, evidence, extra + errors)
    inventory = build_inventory(bundle)
    return {"validation_schema_version": VERSION, "validation_profile": PROFILE, "exit_code": code,
        "validation_scope": "record_consistency_and_replay_structure_only", "longitudinal": report,
        "input_refs": _input_refs(bundle), "contract_failures": failures, "diagnostics": diagnostic_records(bundle.diagnostics),
        "input_acquisition_complete": bundle.acquisition_complete, "input_row_count": inventory.input_row_count,
        "cell_count": len(inventory.cells), "malformed_row_count": inventory.malformed_row_count,
        "evidence_status": "supplied_record_checks_only", "statistics_computed": False,
        "support_checks": [{"record_id": x.record_id, "status": x.status, "reasons": list(x.reasons), "mock": x.mock}
                           for x in evidence.support_checks], "independent_validation_performed": False}, code


def _measurements(observed):
    if observed is None:
        return []
    result = []
    for row in observed.measurements:
        data = _public(row)
        cell = row.source_cell
        if cell:
            inv = cell.inventory
            data["inventory"] = {"cell_id": inv.cell_id, "selected_sample_ids": list(inv.selected_sample_ids),
                "requested_sample_ids": list(inv.requested_sample_ids), "excluded_sample_ids": list(inv.excluded_sample_ids),
                "recorded_attempt_ids": list(inv.recorded_attempt_ids), "planned_positions": len(inv.positions),
                "plan_status": inv.plan_status, "plan_reasons": list(inv.plan_reasons),
                "positions": _public(inv.positions), "groups": _public(inv.groups),
                "classified_all_count": cell.populations["classified_all"].count,
                "classified_valid_count": cell.populations["classified_valid"].count,
                "ratios": _public(cell.ratios), "assignment_status_counts": plain(cell.assignment_status_counts),
                "validity_status_counts": plain(cell.validity_status_counts)}
        result.append(data)
    return result


def _sensitivity(result):
    record = _public(result)
    record.pop("replay", None)
    record["replay_sha256"] = result.replay["sha256"] if result.replay else None
    record["complete_indices_location"] = "run_manifest.longitudinal_replay.entries"
    record["draws"] = [{"index": x.index, "selected_indices": list(x.selected_indices), "curve": plain(x.curve),
        "status": x.status, "reasons": list(x.reasons),
        "interval_half_life": _public(x.fit.interval) if x.fit else None,
        "empirical_half_life": _public(x.fit.empirical) if x.fit else None,
        "max_abs_log_residual": x.fit.max_abs_log_residual if x.fit else None} for x in result.draws]
    record["plan_identity"] = digest(result.plan) if result.plan else None
    return record


def _integrity(bundle, evidence, review):
    from .pipeline import _declared_date, _metadata_details, _check_details
    index = EvidenceIndex(bundle)
    claims = []
    for check in evidence.claim_checks:
        payload = index.payload(("integrity_assessment", check.record_id))
        claims.append({"record_id": check.record_id, "status": check.status, "reasons": list(check.reasons), "mock": check.mock,
            "requirement_record_outcomes": {k: check.details.get("requirement_record_outcomes", {}).get(k, "unresolved") for k in INTEGRITY_CONDITIONS},
            "current_until": _declared_date(payload["current_until"]) if payload else {"state": "unknown"},
            "assessed_at": _declared_date(payload["assessed_at"]) if payload else {"state": "unknown"},
            "scope_refs": plain(payload["scope_refs"]) if payload else [], "substantive_claim": "not_certified_by_software"})
    supports = [{"record_type": k[0], "record_id": k[1], "record_version": r.record.record_version,
        "state": r.payload["state"], "data_role": r.payload["data_role"], "mock": r.payload["mock"],
        "payload_sha256": digest(r.payload), "details": _metadata_details(k[0], r.payload),
        "evidence_refs": plain(r.payload["evidence_refs"]), "transformation_refs": plain(r.payload["transformation_refs"])}
        for k, r in sorted(index.support.items())]
    return {"five_conditions": [{"condition": x, "outcome": "unresolved", "declared_assessments": [r["record_id"] for r in claims],
             "reason": "no_substantive_independent_validation_performed_by_toolkit"} for x in INTEGRITY_CONDITIONS],
        "declared_claim_records": claims, "support_records": supports,
        "support_checks": [{"record_id": x.record_id, "status": x.status, "reasons": list(x.reasons), "mock": x.mock,
                            "details": _check_details(x.details)} for x in evidence.support_checks],
        "ec_reporting_disclosures": {"capability_and_scope": "section_1", "structural_cut_and_known_omissions": "sections_1_3_7",
            "source_and_transformation_lineage": "sections_2_7_and_pinned_input", "exposure_and_bias_controls": "sections_6_8_declared_records_only",
            "evaluator_identity": "record_ids_only_private_mappings_omitted", "class_and_tail_outcomes": "sections_3_4_6",
            "horizon_recovery_override": "declared_horizon_and_qualified_finite_family_recovery_only",
            "live_field_evidence": "not_established_by_toolkit", "correction_path": "new_pinned_input_new_output_directory_prior_results_preserved",
            "current_until": {"state": "unknown", "scoped_declarations": [{"record_id": x["record_id"], "current_until": x["current_until"], "scope_refs": x["scope_refs"]} for x in claims]}},
        "omitted_conditions": ["deployment_representativeness", "all_input_program_correctness", "long_horizon_behavior",
            "causal_attribution_to_recursive_training", "complete_expressible_or_latent_repertoire"],
        "currentness": {"input_context_sha256": review.input_context_sha256, "declared_expiry_is_certification": False,
                       "future_evidence_status": "unknown"},
        "release_restrictions": ["No empirical or deployment certification.", "No model calls, training or candidate execution.",
            "Local software processing and repository publication are separate outcomes.", "Phase 3 Step 9 final conformance is outside this command."],
        "redaction": {"raw_bodies": "omitted", "private_identity_mappings": "omitted", "private_paths": "hashed",
            "unrestricted_evidence_prose": "hashed", "source_bytes_modified": False,
            "limitation": "Full reproduction requires the retained local evidence; a public report cannot reconstruct withheld material."}}


def analyze_snapshot(bundle, *, run_id=None, recorded_at=None, replay_manifest_path=None):
    from .pipeline import Analysis, _input_refs, _mode, _processing
    from .reporting import LONGITUDINAL_SECTION_TITLES
    review = lr.review_longitudinal(bundle)
    evidence = review_evidence(bundle)
    software = software_identity()
    binding, errors, replays, replay_receipt = longitudinal_validation(bundle,
        replay_manifest_path=replay_manifest_path, review=review, software=software)
    # Transport provenance belongs to validation/the run manifest. The canonical
    # scientific report remains identical when the same complete indices replay.
    binding.pop("replay_status", None)
    _, extra = _mode(bundle)
    code, failures = _processing(bundle, evidence, extra + errors)
    cfg = review.configuration
    capabilities = tuple(cfg["capabilities"]) if cfg else ()
    observed = categorical = fitted = sensitivity = assays = recovery = None
    revisions = dependencies = impacts = ()
    if code == 0 and cfg is not None:
        if "observed" in capabilities:
            observed = lg.observe_longitudinal(bundle, review=review)
        if "categorical_null" in capabilities:
            categorical = cn.evaluate_categorical_null(bundle, review=review)
            failures.extend(r for x in categorical.scenarios if x.status == "contract_error" for r in x.reasons)
        if "half_life" in capabilities:
            fitted = hl.fit_half_lives(bundle, observed=observed)
            if _sensitivity_requests(review):
                sensitivity = lu.evaluate_longitudinal_sensitivity(bundle, half_lives=fitted, replays=replays)
        if "support_assay" in capabilities:
            assays = sa.evaluate_support_assays(bundle, review=review)
        if "recovery" in capabilities:
            recovery = rc.evaluate_recovery(bundle, review=review, assays=assays)
            if assays is None:
                assays = recovery.assays
            revisions, dependencies, impacts = recovery.revisions, recovery.dependencies, recovery.correction_impacts
        else:
            revisions = rc._revisions(review, bundle)
            dependencies, impacts = rc._dependencies(bundle, review, EvidenceIndex(bundle))
    failures = sorted(set(failures))
    code = 2 if failures else code
    entries = []
    by_id = {x.request_ref.object_id: x for x in sensitivity.results if x.request_ref} if sensitivity else {}
    for obj in _sensitivity_requests(review):
        result = by_id.get(obj.ref.object_id)
        entries.append({"request_ref": plain(obj.ref), "status": result.status if result else "unavailable",
            "reasons": list(result.reasons) if result else ["processing_contract_error"], "replay": plain(result.replay) if result else None})
    if replay_receipt is not None:
        # This catches a supplied null/missing draw matrix even when an upstream
        # scientific gate returns early; explicit replay can never trigger RNG.
        if entries != plain(replay_receipt["collection"]["entries"]):
            failures = sorted(set(failures + ["longitudinal_replay_result_mismatch"]))
            code = 2
    replay_collection = {"schema_version": "0.1", "profile": PROFILE,
        "input_context_sha256": review.input_context_sha256, "configuration_sha256": review.configuration_sha256,
        "implementation_sha256": software["implementation_sha256"], "entries": entries}
    replay_collection["sha256"] = digest(replay_collection)
    input_refs = _input_refs(bundle)
    input_sha = digest(input_refs)
    config_sha = digest(bundle.manifest.data["analysis_config"])
    rid = run_id or "run-" + digest({"input": input_sha, "config": config_sha, "software": software["implementation_sha256"]})[:40]
    objects = {name: [binding_record(x) for x in review.objects if x.ref and x.ref.object_kind == kind]
               for name, kind in lr.FAMILIES.items()}
    measures = _measurements(observed)
    role = bundle.manifest.data["data_role"]
    sections = [
        {"scope": {"data_role": role, "permitted_claim_scope": "fixture_only" if role == "fixture" else "supplied_record_finite_scope",
             "evidence_status": "supplied_record_checks_only", "independent_validation_performed": False,
             "phase3_complete": False, "ud_006": "actual_independent_evidence_outstanding"},
         "processing": {"exit_code": code, "contract_failures": failures, "input_acquisition_complete": bundle.acquisition_complete},
         "source_pins": dict(SOURCE_PINS), "ec_001_sha256": ADDENDUM_PIN, "methods": plain(METHODS),
         "requested_capabilities": list(capabilities), "input_refs": input_refs,
         "frozen_baseline": plain(FROZEN_PREDECESSOR),
         "effective_limits": plain(review.limits), "read_limits": plain(bundle.limits),
         "quantities_not_activated": ["latent_support", "complete_arbitrary_family_expressibility", "causal_transmission", "aggregate_inbreeding_score"]},
        {"binding_review": binding, **{k: objects[k] for k in ("states", "panels", "measurements", "roots", "transitions", "trajectories")},
         "inventories": [x["inventory"] for x in measures if "inventory" in x], "diagnostics": diagnostic_records(bundle.diagnostics)},
        {"status": observed.status if observed else "not_requested", "measurements": measures,
         "curves": _public(observed.curves) if observed else [], "views": list(lr.VIEWS), "population_unit": lg.UNITS},
        {"observed_requests": _public(observed.requests) if observed else [],
         "stage_transitions": _public(observed.stage_transitions) if observed else [],
         "categorical_status": categorical.status if categorical else "not_requested",
         "categorical_scenarios": _public(categorical.scenarios) if categorical else [],
         "scenario_scope": "explicit_finite_categorical_arithmetic_no_neural_rate_inference"},
        {"half_life_status": fitted.status if fitted else "not_requested", "half_life": _public(fitted.results) if fitted else [],
         "sensitivity_status": sensitivity.status if sensitivity else "not_requested",
         "sensitivity": [_sensitivity(x) for x in sensitivity.results] if sensitivity else [],
         "uncertainty_limit": "Resampling sensitivity is conditional on registered complete units; no population confidence or model training variability is inferred."},
        {"assay_status": assays.status if assays else "not_requested", "assays": _public(assays.assays) if assays else [],
         "recovery_status": recovery.status if recovery else "not_requested", "recovery": _public(recovery.episodes) if recovery else [],
         "scope": "finite_registered_family_and_reference_registry_only"},
        {"revisions": _public(revisions), "dependencies": _public(dependencies), "correction_impacts": _public(impacts),
         "original_anomalies_retained": True, "new_samples_created_by_reclassification": 0,
         "new_recursive_rounds_created_by_reclassification": 0, "prior_results_overwritten": False},
        _integrity(bundle, evidence, review)]
    sections[7]["workflow_status"] = {"local_software_processing": "success" if code == 0 else "contract_error",
        "local_processing_exit_code": code, "repository_delivery": "not_assessed_by_command",
        "owner_acceptance": "not_assessed_by_command"}
    report = {"report_schema_version": VERSION, "report_profile": PROFILE, "run_id": rid,
        "study_id": bundle.manifest.data["study_id"], "bundle_id": bundle.manifest.data["bundle_id"],
        "input_schema_version": bundle.manifest.data["input_schema_version"], "input_fingerprint": input_sha,
        "input_context_sha256": review.input_context_sha256, "software_version": __version__,
        "implementation_sha256": software["implementation_sha256"],
        "capabilities": {"longitudinal": "implemented_optional", "empirical_validation": "not_performed"},
        "sections": [{"number": i, "title": title, "content": content} for i, (title, content) in enumerate(zip(LONGITUDINAL_SECTION_TITLES, sections), 1)]}
    out_json, out_md = render_json(report), render_markdown(report)
    now = recorded_at or datetime.now(timezone.utc).isoformat()
    _require(isinstance(now, str) and len(now) <= 64, "invalid_recorded_at")
    try:
        t = datetime.fromisoformat(now.replace("Z", "+00:00"))
        _require(t.tzinfo is not None and t.utcoffset().total_seconds() == 0, "invalid_recorded_at")
    except ValueError as exc:
        raise InputError("invalid_recorded_at") from exc
    manifest = {"run_manifest_version": VERSION, "report_profile": PROFILE, "run_id": rid, "recorded_at_utc": now,
        "input_refs": input_refs, "input_fingerprint": input_sha, "input_context_sha256": review.input_context_sha256,
        "analysis_config_sha256": config_sha, "software": software, "source_pins": dict(SOURCE_PINS), "ec_001_sha256": ADDENDUM_PIN,
        "python_version": platform.python_version(), "python_implementation": platform.python_implementation(), "platform": platform.system(),
        "read_limits": plain(bundle.limits), "longitudinal_limits": plain(review.limits), "total_read_bytes": bundle.total_read_bytes,
        "processing_exit_code": code, "input_acquisition_complete": bundle.acquisition_complete,
        "expected_record_files": _expected_files(bundle), "artifact_acquisition": _artifact_acquisition(bundle),
        "longitudinal_methods": plain(METHODS), "longitudinal_replay": replay_collection,
        "longitudinal_replay_sha256": digest(replay_collection),
        "replay_source": {k: plain(v) for k, v in replay_receipt.items() if k != "collection"} if replay_receipt else None,
        "report_files": {"report.json": hashlib.sha256(out_json).hexdigest(), "report.md": hashlib.sha256(out_md).hexdigest()},
        "replay_variable_fields": ["recorded_at_utc", "python_version", "python_implementation", "platform", "replay_source"],
        "independent_validation_performed": False, "model_calls": 0, "candidate_programs_executed": 0,
        "output_publication": "complete_directory_atomic_noreplace"}
    out_manifest = canonical_bytes(manifest)
    _require(sum(map(len, (out_json, out_md, out_manifest))) <= 128 * 1024 * 1024, "report_size_exceeded")
    return Analysis(freeze(report), freeze(manifest), out_json, out_md, out_manifest, code)
