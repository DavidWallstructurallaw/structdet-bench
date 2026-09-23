"""Passive collection planning and inspection of supplied original records.

No request is sent, no candidate is executed, and no assertion authenticates an
external operation. All imported bytes come from the bounded study loader.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import hashlib
from typing import Any, Mapping

from .contracts import Diagnostic, ExactNumber, InputError, freeze, is_id
from .local_io import ReadLimits
from .study_records import (LoadedStudy, FAMILY_SCHEMAS, RECORD_TYPES,
                            _limits, _physical, _preflight, _serialize, _validate)
from .study_review import _StudyView

OPENERS = {
    "P00": "Prepare Python implementations for this bounded sorting task.",
    "P01": "Implement the sorting function specified below.",
    "P02": "Write implementations for the following integer-sorting task.",
    "P03": "Provide programs that meet this sorting specification.",
    "P04": "Solve the following bounded integer-ordering problem in Python.",
    "P05": "Create implementations of the function described below.",
    "P06": "Produce Python solutions for this list-sorting interface.",
}
TASK_TEXT = """Define sort_values(values) in Python 3.

The input is a plain list of plain integers. Its length is from 0 through 256 inclusive. Every integer is from 0 through 4095 inclusive. Return a new plain list containing the same integers with the same multiplicities, in nondecreasing order. Do not change the input list. Your program must handle the entire stated domain, including empty lists and repeated values.

Additional local memory is allowed. There is no requirement to sort in place, preserve the identities of equal records, or meet a particular asymptotic running-time bound. Only integers are supplied.

Use self-contained source with all helper functions included. Do not use imports, sorted, any .sort method, or another external ordering routine. Ordinary loops, recursion, comparisons, integer arithmetic, local containers, and basic built-ins such as len, range, enumerate, list, min, and max are allowed. Do not use randomness, dynamic code execution, reflection, filesystem or network access, subprocesses, or persistent state. Each candidate must work by itself without code from another candidate."""
ORDINARY_CLAUSE = "Produce five versions of a solution to this task."
MECHANISM_CLAUSE = "Produce five solutions to this task using five different ordering mechanisms. Differences only in names, comments, formatting, or local implementation details do not count as different mechanisms. Keep the task and its constraints unchanged."
OUTPUT_TEXT = "Return exactly five numbered sections headed ### Candidate 1 through ### Candidate 5, in that order. Each section must contain exactly one fenced python code block holding a complete independent program that defines sort_values(values). Put helpers inside that same code block. Include no prose outside the code blocks apart from the five section headings. Comments inside the code are allowed. Do not supply tests, examples, imports, or a main program."
PERMUTATIONS = ("ABC", "ACB", "BAC", "BCA", "CAB", "CBA")
CONTROL_SCHEMA = FAMILY_SCHEMAS["collection_ledger"]["object"]["controls"]
CONTROL_NAMES = tuple(CONTROL_SCHEMA["object"])
_K = lambda value: {"knowledge": value}
_REF = {"reference": list(RECORD_TYPES)}
SUBMISSION_SCHEMA = {"object": {
    "kind": {"literal": "collection_submission"}, "version": {"literal": "0.1"},
    "study_id": "id", "study_version": "id", "fixture": "bool", "record": "record",
    "requested_controls": CONTROL_SCHEMA,
    "enforced_controls": {"object": {name: _K("bool") for name in CONTROL_NAMES}},
    "cap": {"object": {"unit": _K("text"), "tokenizer": _K("text"),
        "convention": _K("text"), "includes_reasoning": _K("bool"), "enforced": _K("bool")}},
    "context": {"object": {
        "visible_system_instruction_ref": _K({"reference": ["artifact"]}),
        "platform_context": _K("text"), "reasoning_configuration": _K("text"),
        "previous_outputs_supplied": _K("bool"), "reference_material_supplied": _K("bool"),
        "output_selection": _K({"enum": ["none", "reranked", "best_of", "other"]}),
        "automatic_retries": _K("nonnegative"), "duration_ms": _K("exact_nonnegative")}},
    "deployment_window": {"object": {"start": _K("timestamp"), "end": _K("timestamp")}},
    "evidence_refs": {"array": _REF}}}


def _known(value):
    return value.get("value") if isinstance(value, Mapping) and value.get("state") == "known" else None


def _unknown(reason="Not supplied; preparation does not observe an external operation."):
    return {"state": "unknown", "reason": reason}


def _known_wrapper(value):
    return {"state": "known", "value": value}


def _diag(code, path="", severity="error"):
    return Diagnostic(code, "study_collection", "study_collection", path, severity=severity)


def prompt_bytes(block_id: str, condition: str) -> bytes:
    """Exact HERO assembly, UTF-8, LF, no trailing newline after final text."""
    if block_id not in OPENERS or condition not in ("A", "B", "C"):
        raise InputError("invalid_collection_prompt_identity")
    clause = MECHANISM_CLAUSE if condition == "C" else ORDINARY_CLAUSE
    return "\n\n".join((OPENERS[block_id], TASK_TEXT, clause, OUTPUT_TEXT)).encode("utf-8")


def _requested_controls(condition):
    return {"temperature": _known_wrapper("1.0" if condition == "B" else "0.4"),
            "top_p": _known_wrapper("1.0"), "presence_penalty": _known_wrapper("0"),
            "frequency_penalty": _known_wrapper("0"), "seed": _known_wrapper(None),
            "output_allowance": _known_wrapper(8192),
            "cap_semantics": _unknown("The operator must specify one actual token-cap convention."),
            "fresh_context": _known_wrapper(True), "tools_requested": _known_wrapper(False),
            "hidden_controls": _unknown(), "wrapper_knowledge": _unknown()}


def collection_plan(phase: str = "main") -> Mapping[str, Any]:
    """Materialize one disjoint design, with group then block then condition order.

    The pilot uses b=0 in the registered rotation, g=1,2. Its order is explicit
    preparation convention; the six-block main order is fixed by HERO section 7.4.
    """
    if phase not in ("main", "pilot"):
        raise InputError("invalid_collection_phase")
    calls = []
    for group in range(1, 5 if phase == "main" else 3):
        for block in (range(1, 7) if phase == "main" else (0,)):
            block_id = f"P{block:02d}"
            for condition in PERMUTATIONS[(block + group - 2) % 6]:
                calls.append({"slot_id": f"{phase}-{block_id}-{condition}-G{group}",
                    "phase": phase, "block_id": block_id, "condition": condition,
                    "group_index": group, "registered_call_order": len(calls) + 1,
                    "planned_positions": (1, 2, 3, 4, 5),
                    "sample_orders": tuple((group - 1) * 5 + n for n in range(1, 6)),
                    "prompt_sha256": hashlib.sha256(prompt_bytes(block_id, condition)).hexdigest(),
                    "requested_controls": _requested_controls(condition)})
    return freeze({"phase": phase, "calls": calls, "planned_calls": len(calls),
                   "planned_positions": len(calls) * 5, "max_output_tokens": len(calls) * 8192,
                   "software_preparation_only": True})


@dataclass(frozen=True)
class CollectionPacket:
    data: Any = field(default=None, repr=False)
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def has_errors(self):
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0


def parse_collection_submission_bytes(data: bytes, limits: ReadLimits | None = None) -> CollectionPacket:
    """Parse a typed export packet, keeping requested and observed values separate."""
    issues, raw = [], None
    try:
        limits = _limits(limits)
        raw = _physical(data, limits)
        _preflight(raw, limits)
        _validate(raw, SUBMISSION_SCHEMA, "packet", issues)
        if not issues:
            record = raw["record"]
            if record["record_type"] != "collection_ledger":
                raise InputError("collection_submission_type_mismatch")
            if any(record[key] != raw[key] for key in ("study_id", "study_version")):
                raise InputError("collection_submission_scope_mismatch")
            start, end = (_known(raw["deployment_window"][key]) for key in ("start", "end"))
            if start and end and _time(start) > _time(end):
                raise InputError("deployment_window_reversed")
    except (InputError, TypeError, ValueError, RecursionError) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_collection_packet"))
    return CollectionPacket(freeze(raw) if not issues else None, tuple(issues))


def _time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _blank(schema):
    """Construct reasoned missing fields without inventing external observations."""
    if isinstance(schema, Mapping):
        if "knowledge" in schema:
            return _unknown()
        if "object" in schema:
            return {key: _blank(value) for key, value in schema["object"].items()}
        if "array" in schema:
            return []
        if "literal" in schema:
            return schema["literal"]
    raise InputError("template_requires_explicit_value")


def _common(record_type, record_id, study_id, study_version):
    return {"record_type": record_type, "record_id": record_id, "record_version": "0.1",
            "revision": 1, "study_id": study_id, "study_version": study_version,
            "scope": {"claim_id": "hero-fixed-suite", "task_id": "bounded_integer_sort", "task_version": "0.1"},
            "depends_on": [], "lineage_refs": [],
            "supersedes": {"state": "not_applicable", "reason": "New unexecuted preparation record."}}


def collection_templates(study_id="study", study_version="v1", phase="main") -> dict:
    """Return passive preregistration, ledger and typed export forms, with no I/O."""
    if not is_id(study_id) or not is_id(study_version):
        raise InputError("invalid_study_identity")
    plan, ledgers, submissions = collection_plan(phase), [], []
    for slot in plan["calls"]:
        row = _common("collection_ledger", slot["slot_id"], study_id, study_version)
        for key, schema in FAMILY_SCHEMAS["collection_ledger"]["object"].items():
            if key in ("phase", "block_id", "condition", "group_index", "registered_call_order", "planned_positions"):
                row[key] = list(slot[key]) if key == "planned_positions" else slot[key]
            elif key == "attempt_status":
                row[key] = "not_attempted"
            else:
                row[key] = _blank(schema)
        ledgers.append(row)
        submission = {key: _blank(schema) for key, schema in SUBMISSION_SCHEMA["object"].items()
                      if key not in {"study_id", "study_version", "fixture", "record"}}
        submission.update(study_id=study_id, study_version=study_version, fixture=False,
                          record=row, requested_controls=_requested_controls(slot["condition"]))
        submissions.append(submission)
    registration = _common("study_registration", f"registration-{phase}", study_id, study_version)
    schema = FAMILY_SCHEMAS["study_registration"]["object"]
    for key in ("source_pins", "pins", "frame_definition", "exposure"):
        registration[key] = _blank(schema[key])
    registration.update(claim_scope="Prepared HERO fixed-suite design; no external study has been registered or collected.",
                        requested_profile="hero_sort_abc_v1")
    protocol = schema["protocol"]["object"]
    registration["protocol"] = {key: _blank(value) for key, value in protocol.items()
                                if key not in ("protocol_id", "protocol_version", "design")}
    registration["protocol"].update(protocol_id=f"hero-{phase}", protocol_version="0.1", design="sorting_abc")
    registration["protocol"]["budget"].update(max_calls=_known_wrapper(plan["planned_calls"]),
        max_positions=_known_wrapper(plan["planned_positions"]), max_output_tokens=_known_wrapper(plan["max_output_tokens"]))
    registration["preregistration"] = {"status": "not_registered", "registered_at": _unknown(),
                                       "evidence_refs": [], "exposure_at_registration": _unknown()}
    registration["currentness"] = {"state": "unresolved", "assessed_at": _unknown(),
                                     "expires_at": _unknown(), "basis": _unknown()}
    return {"plan": plan, "registration": registration, "ledger": ledgers, "submissions": submissions}


def collection_template_files(study_id="study", study_version="v1", phase="main") -> Mapping[str, bytes]:
    """Return bounded flat filenames and ready-to-save bytes, without any I/O.

    Study rows are unattempted preparations. Submission files become importable
    evidence only after the operator supplies actual records and declares each
    completed file in that study's packet inventory.
    """
    templates = collection_templates(study_id, study_version, phase)
    envelope = {"study_schema_version": "0.1", "study_id": study_id,
        "study_version": study_version, "prior_study_versions": [],
        "evidence_policy": "adjudicated_import", "material_role": "pilot" if phase == "pilot" else "descriptive",
        "packet_inventory": [], "import_budget": {"max_packets": 1000,
            "max_total_bytes": 64 * 1024 * 1024, "max_total_records": 100000},
        "records": [templates["registration"], *templates["ledger"]]}
    files = {"study.json": _serialize(envelope), "collection_plan.json": _serialize(templates["plan"])}
    for slot, submission in zip(templates["plan"]["calls"], templates["submissions"]):
        files[f"submission-{slot['slot_id']}.json"] = _serialize(submission)
        files[f"prompt-{slot['block_id']}-{slot['condition']}.txt"] = prompt_bytes(slot["block_id"], slot["condition"])
    limits = _limits(None)
    if max(map(len, files.values())) > limits.max_file_bytes or sum(map(len, files.values())) > limits.max_bundle_bytes:
        raise InputError("collection_output_budget_exceeded")
    return freeze(files)


@dataclass(frozen=True)
class CollectionAssessment:
    diagnostics: tuple[Diagnostic, ...]
    slots: tuple[Mapping[str, Any], ...]
    history: tuple[Mapping[str, Any], ...]
    counts: Mapping[str, Any]
    cells: tuple[Mapping[str, Any], ...]
    restrictions: tuple[str, ...]
    preregistration: Mapping[str, Any]
    qualification_status: str = "external_authentication_required"
    software_verification_only: bool = True
    substantive_validation_performed: bool = False

    @property
    def has_errors(self):
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0


def _numeric(value):
    if isinstance(value, ExactNumber):
        return Decimal(value.token)
    return Decimal(str(value))


def _same_known(left, right):
    if left.get("state") != "known" or right.get("state") != "known":
        return False
    a, b = left["value"], right["value"]
    if a is None or b is None or isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    try:
        return _numeric(a) == _numeric(b)
    except (ValueError, ArithmeticError):
        return a == b


def inspect_collection(loaded: LoadedStudy, phase: str = "main") -> CollectionAssessment:
    """Inspect a fixed planned population without running or replacing attempts.

    A match establishes supplied-record consistency only. Provider identity,
    prospective registration and actual enforcement require external evidence.
    """
    from .study_extraction import extract_response_bytes, result_dict

    plan = collection_plan(phase)
    issues, slots, history, cells, restrictions = [], [], [], [], set()
    counts = {"planned_calls": plan["planned_calls"], "planned_positions": plan["planned_positions"],
              "max_output_tokens": plan["max_output_tokens"], "supplied_slots": 0,
              "missing_slots": plan["planned_calls"], "actual_attempt_records": 0,
              "selected_realizations": 0, "extra_realizations": 0, "complete_groups": 0,
              "failed_calls_without_response": 0, "observed_automatic_retries": 0, "unselected_regions": 0,
              "supplied_attempt_records": 0, "unknown_attempt_status_records": 0}
    preregistration, fixture = {}, False
    try:
        view = _StudyView(loaded)
        fixture = view.fixture
        budget = view.raw["import_budget"]
        limits = _limits(None)
        record_limit = min(limits.max_records, budget["max_total_records"])
        logical_records = len(view.raw["records"]) + sum(row.checked_record_count or 0 for row in loaded.attachments)
        if (logical_records > record_limit or loaded.total_read_bytes > min(limits.max_bundle_bytes, budget["max_total_bytes"])
                or sum(len(snap.content) for snap in loaded.snapshots.values()) > min(limits.max_bundle_bytes, budget["max_total_bytes"])):
            raise InputError("budget_exceeded_partition_required")
        submissions = {}
        for packet_id, entry in view.inventory.items():
            if entry["purpose"] != "evidence" or entry["format"] != "json":
                continue
            snap = view.snapshot(packet_id)
            if snap is None:
                continue
            candidate = _physical(snap.content, limits)
            if not isinstance(candidate, Mapping) or candidate.get("kind") != "collection_submission":
                continue
            parsed = parse_collection_submission_bytes(snap.content, limits)
            issues.extend(parsed.diagnostics)
            if parsed.has_errors:
                continue
            raw = parsed.data
            logical_records += 1  # nested original ledger row, beyond its JSON envelope
            if logical_records > record_limit:
                raise InputError("budget_exceeded_partition_required")
            record = raw["record"]
            if (raw["study_id"] != view.raw["study_id"] or record["record_id"] not in view.records
                    or _serialize(record) != _serialize(view.records[record["record_id"]])):
                issues.append(_diag("collection_original_record_mismatch"))
                continue
            if any(ref["record_id"] not in view.records or
                   view.records[ref["record_id"]]["record_type"] != ref["record_type"] or
                   view.records[ref["record_id"]]["study_version"] != raw["study_version"] or
                   view.records[ref["record_id"]]["scope"] != record["scope"]
                   for ref in raw["evidence_refs"]):
                issues.append(_diag("collection_submission_reference_mismatch"))
                continue
            fixture |= raw["fixture"]
            submissions.setdefault(record["record_id"], []).append(raw)

        current = [record for record in view.current if record["record_type"] == "collection_ledger"]
        all_attempts = [record for record in view.raw["records"] if record["record_type"] == "collection_ledger"]
        history = [{"record": record,
                    "in_current_phase": record["study_version"] == view.raw["study_version"] and record["phase"] == phase,
                    "typed_submission_count": len(submissions.get(record["record_id"], ())) }
                   for record in all_attempts]
        by_slot, attempt_ids, response_ids = {}, {}, {}
        for record in all_attempts:
            key = (record["phase"], record["block_id"], record["condition"], record["group_index"])
            identity_key = (record["study_version"], *key)
            if record["study_version"] == view.raw["study_version"]:
                by_slot.setdefault(key, []).append(record)
            aid, rid = _known(record["attempt_id"]), _known(record["raw_response_ref"])
            if aid:
                attempt_ids.setdefault(aid, set()).add(identity_key)
            if rid:
                # Artifact identities denote declared response events. Equal
                # bytes, even deduplicated storage, do not prove event identity.
                response_ids.setdefault(rid["record_id"], set()).add((identity_key, aid))
        registration = next(record for record in view.current if record["record_type"] == "study_registration")
        preregistration = {"declared": registration["preregistration"], "exposure": registration["exposure"],
                          "chronology": "unknown", "external_authentication_required": True}
        restrictions.add("external_authentication_required")
        if registration["protocol"]["design"] != "sorting_abc":
            restrictions.add("registration_design_differs")
        for name, expected in (("max_calls", plan["planned_calls"]), ("max_positions", plan["planned_positions"]),
                               ("max_output_tokens", plan["max_output_tokens"])):
            supplied = _known(registration["protocol"]["budget"][name])
            if supplied is None:
                restrictions.add("registration_budget_incomplete")
            elif supplied != expected:
                restrictions.add("registration_planned_budget_differs")
        if registration["preregistration"]["status"] != "prospectively_registered":
            restrictions.add("prospective_registration_not_supplied")
        if not registration["preregistration"]["evidence_refs"]:
            restrictions.add("registration_evidence_missing")
        if _known(registration["preregistration"]["exposure_at_registration"]) is None:
            restrictions.add("registration_exposure_unknown")

        observed_times, signatures = [], {}
        for slot in plan["calls"]:
            key = (phase, slot["block_id"], slot["condition"], slot["group_index"])
            records = by_slot.get(key, [])
            originals = [row for row in records if _known(row["retry_of"]) is None and _known(row["supersedes"]) is None]
            row_restrictions = set()
            out = {**slot, "record_ids": tuple(row["record_id"] for row in records),
                   "primary_record_id": None, "attempt_status": "not_supplied",
                   "emitted_positions": 0, "extraction": None, "group_complete": False,
                   "restrictions": (), "actual_controls": None, "usage": None, "deployment": None,
                   "submission": None}
            counts["supplied_attempt_records"] += sum(row["attempt_status"] != "not_attempted" for row in records)
            counts["unknown_attempt_status_records"] += sum(row["attempt_status"] == "unknown" for row in records)
            counts["actual_attempt_records"] += sum(row["attempt_status"] in ("succeeded", "failed") or
                (row["attempt_status"] == "cancelled" and _known(row["attempt_id"]) is not None) for row in records)
            if records:
                counts["supplied_slots"] += 1
            else:
                row_restrictions.add("planned_call_not_supplied")
            if len(originals) != 1:
                row_restrictions.add("original_attempt_missing" if not originals else "multiple_original_attempts")
                if len(originals) > 1:
                    issues.append(_diag("multiple_original_attempts"))
            else:
                record = originals[0]
                out.update(primary_record_id=record["record_id"], attempt_status=record["attempt_status"],
                           actual_controls=record["controls"], usage=record["usage"], deployment=record["deployment"])
                if len(records) > 1:
                    row_restrictions.add("retry_or_revision_history_present")
                if any(record[name]["state"] != "not_applicable" for name in ("retry_of", "supersedes")):
                    row_restrictions.add("original_attempt_provenance_unknown")
                if record["registered_call_order"] != slot["registered_call_order"]:
                    issues.append(_diag("registered_call_order_mismatch"))
                    row_restrictions.add("registered_call_order_mismatch")
                aid, rid = _known(record["attempt_id"]), _known(record["raw_response_ref"])
                if aid is None and record["attempt_status"] != "not_attempted":
                    row_restrictions.add("actual_attempt_identity_unknown")
                if aid and len(attempt_ids[aid]) > 1:
                    issues.append(_diag("actual_attempt_identity_reused"))
                    row_restrictions.add("actual_attempt_identity_reused")
                response_key = rid["record_id"] if rid else None
                if response_key and len(response_ids[response_key]) > 1:
                    issues.append(_diag("raw_response_identity_reused"))
                    row_restrictions.add("raw_response_identity_reused")
                if record["attempt_status"] in ("not_attempted", "unknown"):
                    row_restrictions.add("actual_attempt_not_established")
                when = _known(record["attempted_at"])
                if when:
                    observed_times.append((slot["registered_call_order"], _time(when)))
                elif record["attempt_status"] != "not_attempted":
                    row_restrictions.add("attempt_time_unknown")
                carriers = submissions.get(record["record_id"], ())
                carrier = carriers[0] if len(carriers) == 1 else None
                if len(carriers) > 1:
                    issues.append(_diag("duplicate_collection_submission"))
                if carrier is None:
                    row_restrictions.add("typed_control_evidence_missing")
                else:
                    out["submission"] = carrier
                    _inspect_controls(record, slot, carrier, row_restrictions)
                    system_ref = _known(carrier["context"]["visible_system_instruction_ref"])
                    if system_ref:
                        target = view.records.get(system_ref["record_id"])
                        if (target is None or target["record_type"] != "artifact" or
                                target["study_version"] != record["study_version"] or target["scope"] != record["scope"]):
                            issues.append(_diag("collection_context_reference_mismatch"))
                        _, system_snapshot = view.artifact(system_ref["record_id"])
                        if system_snapshot is None:
                            row_restrictions.add("visible_system_instruction_bytes_unavailable")
                    auto = _known(carrier["context"]["automatic_retries"])
                    if auto is not None:
                        counts["observed_automatic_retries"] += auto
                    signatures.setdefault(slot["block_id"], []).append((record, carrier))
                prompt_ref = _known(record["prompt_ref"])
                prompt_artifact, prompt = view.artifact(prompt_ref["record_id"]) if prompt_ref else (None, None)
                if (prompt is None or _known(prompt_artifact["sha256"]) != prompt.sha256
                        or _known(prompt_artifact["size_bytes"]) != prompt.size_bytes):
                    row_restrictions.add("sent_prompt_bytes_unavailable")
                elif prompt.content != prompt_bytes(slot["block_id"], slot["condition"]):
                    row_restrictions.add("sent_prompt_bytes_differ")
                if prompt and _known(record["sent_prompt_sha256"]) != prompt.sha256:
                    issues.append(_diag("sent_prompt_identity_mismatch"))
                    row_restrictions.add("sent_prompt_identity_mismatch")
                if _known(record["deployment"]["drift"]) not in ("none", "no_change_detected"):
                    row_restrictions.add("deployment_drift_unresolved")
                if any(_known(record["deployment"][field]) is None for field in ("model_identifier", "model_family", "deployment_identifier")):
                    row_restrictions.add("deployment_identity_incomplete")
                if _known(record["deployment"]["checkpoint_identifier"]) is None:
                    row_restrictions.add("checkpoint_identity_unknown")
                artifact, response = view.artifact(rid["record_id"]) if rid else (None, None)
                if response is None:
                    row_restrictions.add("raw_response_unavailable")
                    if record["attempt_status"] == "failed" and rid is None:
                        counts["failed_calls_without_response"] += 1
                elif _known(artifact["sha256"]) != response.sha256 or _known(artifact["size_bytes"]) != response.size_bytes:
                    row_restrictions.add("raw_response_identity_incomplete")
                else:
                    extracted = extract_response_bytes(response.content)
                    issues.extend(extracted.diagnostics)
                    logical_records += len(extracted.positions) + len(extracted.extras)
                    if logical_records > record_limit:
                        raise InputError("budget_exceeded_partition_required")
                    out["extraction"] = result_dict(extracted)
                    out["emitted_positions"] = sum(pos.selection == "selected" for pos in extracted.positions)
                    out["group_complete"] = extracted.group_complete and extracted.order_established
                    if not out["group_complete"]:
                        row_restrictions.add("incomplete_or_ambiguous_group")
                    prior_issue_count = len(issues)
                    _check_supplied_extraction(view, record, response, extracted, issues)
                    if len(issues) != prior_issue_count:
                        row_restrictions.add("supplied_extraction_inconsistent")
                    counts["selected_realizations"] += out["emitted_positions"]
                    counts["unselected_regions"] += len(extracted.extras)
                    counts["extra_realizations"] += sum(extra.reason == "unrequested_candidate_heading" for extra in extracted.extras)
                    counts["complete_groups"] += out["group_complete"]
            out["restrictions"] = tuple(sorted(row_restrictions))
            restrictions.update(row_restrictions)
            slots.append(out)

        counts["missing_slots"] = counts["planned_calls"] - counts["supplied_slots"]
        if any(later <= earlier for (_, earlier), (_, later) in zip(observed_times, observed_times[1:])):
            restrictions.add("observed_call_order_unestablished")
        registered_at = _known(registration["preregistration"]["registered_at"])
        all_phase_times = [_time(_known(row["attempted_at"])) for row in current
                           if row["phase"] == phase and _known(row["attempted_at"])]
        if registered_at and all_phase_times:
            retrospective = _time(registered_at) >= min(all_phase_times)
            preregistration["chronology"] = "retrospective_or_simultaneous" if retrospective else "supplied_times_consistent"
            if retrospective:
                restrictions.add("registration_not_before_collection")
        pairs = [pair for block_pairs in signatures.values() for pair in block_pairs]
        if pairs and any(_control_signature(row, carrier) != _control_signature(*pairs[0]) for row, carrier in pairs[1:]):
            restrictions.add("matched_control_convention_differs_or_unknown")
        deployed = {tuple(_known(row["deployment"][name]) for name in ("model_identifier", "checkpoint_identifier", "deployment_identifier"))
                    for row in current if row["phase"] == phase and row["attempt_status"] != "not_attempted"}
        if len(deployed) > 1:
            restrictions.add("deployment_changed")
        for block in (range(1, 7) if phase == "main" else (0,)):
            for condition in "ABC":
                groups = [slot for slot in slots if slot["block_id"] == f"P{block:02d}" and slot["condition"] == condition]
                cells.append({"block_id": f"P{block:02d}", "condition": condition,
                    "planned_positions": len(groups) * 5, "groups": tuple(row["slot_id"] for row in groups),
                    "matched_prefix_eligible": {str(k): len(groups) >= k // 5 and all(
                        row["group_complete"] and not any(code in row["restrictions"] for code in
                            ("retry_or_revision_history_present", "actual_attempt_identity_reused", "raw_response_identity_reused", "registered_call_order_mismatch",
                             "original_attempt_provenance_unknown", "actual_attempt_not_established", "actual_attempt_identity_unknown",
                             "supplied_extraction_inconsistent"))
                        for row in groups[:k // 5]) for k in (5, 10, 20)},
                    "prefix_scope": "ordered_complete_group_inventory_only"})
        # Avoid an output amplification loophole from many duplicated references.
        if len(_serialize({"slots": slots, "history": history, "cells": cells})) > limits.max_bundle_bytes:
            raise InputError("collection_output_budget_exceeded")
    except (InputError, KeyError, TypeError, ValueError, ArithmeticError, RecursionError, StopIteration) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_collection_inspection"))
    status = "fixture_only" if fixture else "external_authentication_required"
    return CollectionAssessment(tuple(issues), tuple(freeze(slots)), tuple(freeze(history)), freeze(counts),
                                tuple(freeze(cells)), tuple(sorted(restrictions)), freeze(preregistration), status)


def _inspect_controls(record, slot, carrier, restrictions):
    actual, requested, expected = record["controls"], carrier["requested_controls"], slot["requested_controls"]
    for name in ("temperature", "top_p", "presence_penalty", "frequency_penalty", "seed", "output_allowance", "fresh_context", "tools_requested"):
        if not _same_known(requested[name], expected[name]):
            restrictions.add(f"requested_{name}_differs_or_unknown")
        if not _same_known(actual[name], requested[name]):
            restrictions.add(f"actual_{name}_differs_or_unknown")
        if _known(carrier["enforced_controls"][name]) is not True:
            restrictions.add(f"{name}_enforcement_unestablished")
    if any(_known(carrier["cap"][name]) is None for name in ("unit", "tokenizer", "convention", "includes_reasoning")):
        restrictions.add("cap_semantics_incomplete")
    if _known(carrier["cap"]["unit"]) != "model_token":
        restrictions.add("cap_unit_incompatible_or_unknown")
    if _known(carrier["cap"]["enforced"]) is not True:
        restrictions.add("cap_enforcement_unestablished")
    if not _same_known(actual["cap_semantics"], requested["cap_semantics"]):
        restrictions.add("requested_actual_cap_convention_differs_or_unknown")
    if _known(actual["cap_semantics"]) != _known(carrier["cap"]["convention"]):
        restrictions.add("cap_convention_binding_differs")
    context = carrier["context"]
    for name in ("previous_outputs_supplied", "reference_material_supplied"):
        if _known(context[name]) is not False:
            restrictions.add(f"{name}_not_excluded")
    if _known(context["output_selection"]) != "none":
        restrictions.add("output_selection_not_excluded")
    if _known(context["automatic_retries"]) != 0:
        restrictions.add("automatic_retries_present_or_unknown")
    if any(_known(context[name]) is None for name in ("platform_context", "reasoning_configuration")):
        restrictions.add("platform_context_incomplete")
    if any(_known(actual[name]) is None for name in ("hidden_controls", "wrapper_knowledge")):
        restrictions.add("actual_hidden_or_wrapper_context_unknown")
    if context["visible_system_instruction_ref"]["state"] != "not_applicable":
        restrictions.add("visible_system_instruction_requires_protocol_assessment")
    when, start, end = _known(record["attempted_at"]), _known(carrier["deployment_window"]["start"]), _known(carrier["deployment_window"]["end"])
    if not start or not end:
        restrictions.add("deployment_window_unknown")
    elif when and not (_time(start) <= _time(when) <= _time(end)):
        restrictions.add("attempt_outside_deployment_window")


def _control_signature(record, carrier):
    # Temperature intentionally differs for B; prompt condition clauses differ for C.
    def normalize(value):
        if isinstance(value, Mapping):
            if "state" in value:
                return ("known", normalize(value["value"])) if value["state"] == "known" else ("unestablished",)
            return tuple((key, normalize(child)) for key, child in sorted(value.items()))
        if isinstance(value, (tuple, list)):
            return tuple(normalize(child) for child in value)
        return value
    controls = {}
    for key, value in record["controls"].items():
        if key == "temperature":
            continue
        if key in ("top_p", "presence_penalty", "frequency_penalty", "seed", "output_allowance") and _known(value) is not None:
            controls[key] = ("known", _numeric(value["value"]))
        else:
            controls[key] = normalize(value)
    window = tuple((key, _time(value["value"]) if _known(value) else None)
                   for key, value in sorted(carrier["deployment_window"].items()))
    return (tuple(sorted(controls.items())), normalize(carrier["cap"]),
            normalize({key: value for key, value in carrier["context"].items()
                       if key not in ("duration_ms", "automatic_retries")}), window)


def _check_supplied_extraction(view, ledger, source, extracted, issues):
    """Check pre-existing extraction records against the actual original byte spans."""
    for record in view.current:
        if record["record_type"] != "extraction" or record["collection_ref"]["record_id"] != ledger["record_id"]:
            continue
        if _known(record["raw_response_sha256"]) != source.sha256:
            issues.append(_diag("extraction_raw_response_identity_mismatch"))
        if _known(record["raw_response_ref"]) != _known(ledger["raw_response_ref"]):
            issues.append(_diag("extraction_raw_response_reference_mismatch"))
        for supplied, actual in zip(record["positions"], extracted.positions):
            span = _known(supplied["byte_range"])
            actual_span = None if actual.byte_range is None else {"start": actual.byte_range.start, "end": actual.byte_range.end}
            if supplied["selection"] != actual.selection or span != actual_span or supplied["completion_status"] != actual.completion_status:
                issues.append(_diag("supplied_extraction_rule_mismatch"))
            if (_known(supplied["heading"]) != actual.heading or _known(supplied["fence"]) != actual.fence
                    or not set(actual.limitations).issubset(supplied["limitations"])):
                issues.append(_diag("supplied_extraction_metadata_mismatch"))
            ref = _known(supplied["artifact_ref"])
            if actual.selection == "selected" and ref:
                artifact, snap = view.artifact(ref["record_id"])
                if snap is None:
                    issues.append(_diag("extracted_candidate_bytes_unavailable"))
                elif snap.content != actual.content:
                    issues.append(_diag("extracted_candidate_bytes_mismatch"))
                elif _known(artifact["sha256"]) != snap.sha256 or _known(artifact["size_bytes"]) != snap.size_bytes:
                    issues.append(_diag("extracted_candidate_identity_incomplete"))
        expected_extras = [(extra.heading, extra.byte_range.start, extra.byte_range.end, extra.reason) for extra in extracted.extras]
        supplied_extras = [(_known(extra["heading"]), extra["byte_range"]["start"], extra["byte_range"]["end"], extra["reason"]) for extra in record["extras"]]
        if supplied_extras != expected_extras:
            issues.append(_diag("supplied_extraction_extras_mismatch"))
