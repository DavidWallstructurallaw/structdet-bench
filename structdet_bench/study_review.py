"""Passive first-pass review records and privacy-separated review material.

Byte identity and complete supplied records never authenticate a person or an
independent review. No submitted artifact, command, or reviewer prose is run.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import os
from pathlib import Path
import re
import secrets
from typing import Any, Mapping

from .contracts import Diagnostic, InputError, freeze
from .local_io import ReadLimits, relative_parts, _rename_noreplace
from .study_records import (LoadedStudy, RECORD_TYPES, _limits, _physical,
                            _preflight, _serialize, _validate)
from .study_validation import FAMILIES, RUBRIC_ID, reference_specifications

CORE_ROLE_IDS = tuple(f"CORE-{family}-{variant}" for family in FAMILIES
                      for variant in ("A", "B", "D")) + tuple(
                          f"CORE-X{number:02d}" for number in range(1, 9))
WITHHELD_FIELDS = ("model", "condition", "proposed_role", "other_judgments")
_K = lambda value: {"knowledge": value}
_ENUM = lambda *values: {"enum": list(values)}
_BASE = {"version": {"literal": "0.1"}, "study_id": "id", "study_version": "id",
         "fixture": "bool"}
_ROSTER_ROW = {"object": {
    "reviewer_id": "id", "person_key": _K("id"),
    "entity_kind": _ENUM("human", "machine", "unknown"),
    "identity_evidence": _K("text"), "qualifications": _K("text"),
    "qualification_status": _ENUM("qualified", "expert", "unqualified", "unknown"),
    "relationships": _K("text"),
    "relationship_status": _ENUM("independent", "related", "unknown"),
    "exposure": _K("text"), "machine_assistance": _K("text")}}
ROSTER_SCHEMA = {"object": {**_BASE, "kind": {"literal": "reviewer_roster"},
                            "reviewers": {"array": _ROSTER_ROW}}}
SUBMISSION_SCHEMA = {"object": {**_BASE, "kind": {"literal": "review_submission"},
    "rubric_id": {"literal": RUBRIC_ID}, "record": "record",
    "prior_label_exposure": _K("bool"), "copied_from": _K("id"),
    "schema_issues": {"array": {"object": {
        "issue_id": "id", "descriptor_ids": {"array": "class_id"},
        "status": _ENUM("open", "resolved"), "resolution": _K("text"),
        "evidence_refs": {"array": {"reference": list(RECORD_TYPES)}}}}}}}


def _known(value):
    return value.get("value") if isinstance(value, Mapping) and value.get("state") == "known" else None


def _diag(code, path="", severity="error"):
    return Diagnostic(code, "study_review", "study_review", path, severity=severity)


@dataclass(frozen=True)
class ReviewPacket:
    data: Any = field(default=None, repr=False)
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def has_errors(self):
        return any(item.severity == "error" for item in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0


def _parse_packet(data, schema, limits=None):
    issues = []
    raw = None
    try:
        limits = _limits(limits)
        raw = _physical(data, limits)
        _preflight(raw, limits)
        _validate(raw, schema, "packet", issues)
        if not issues:
            rows = raw.get("reviewers", raw.get("schema_issues", []))
            if len(rows) > limits.max_records:
                raise InputError("record_count_exceeded")
            key = "reviewer_id" if "reviewers" in raw else "issue_id"
            if len({row[key] for row in rows}) != len(rows):
                raise InputError("duplicate_review_identity")
            if "record" in raw:
                record = raw["record"]
                if record["record_type"] not in {"human_review", "adjudication"}:
                    raise InputError("review_submission_type_mismatch")
                if any(record[name] != raw[name] for name in ("study_id", "study_version")):
                    raise InputError("review_submission_scope_mismatch")
                for row in raw["schema_issues"]:
                    if (not row["descriptor_ids"] or
                            len(set(row["descriptor_ids"])) != len(row["descriptor_ids"])):
                        raise InputError("schema_issue_descriptor_mismatch")
                    if row["status"] == "resolved" and (
                            _known(row["resolution"]) is None or not row["evidence_refs"]):
                        raise InputError("schema_issue_resolution_missing")
    except (InputError, TypeError, ValueError, RecursionError) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_review_packet"))
    return ReviewPacket(freeze(raw) if not issues else None, tuple(issues))


def parse_reviewer_roster_bytes(data: bytes, limits: ReadLimits | None = None) -> ReviewPacket:
    """Parse the restricted roster. Same person keys may identify known aliases."""
    return _parse_packet(data, ROSTER_SCHEMA, limits)


def parse_review_submission_bytes(data: bytes, limits: ReadLimits | None = None) -> ReviewPacket:
    """Parse an original submission, preserving its exact declared record."""
    return _parse_packet(data, SUBMISSION_SCHEMA, limits)


class _StudyView:
    def __init__(self, loaded):
        if (not isinstance(loaded, LoadedStudy) or loaded.has_errors or loaded.packet is None
                or loaded.packet.has_errors):
            raise InputError("invalid_loaded_study")
        self.loaded, self.raw = loaded, loaded.packet.data
        self.records = {record["record_id"]: record for record in self.raw["records"]}
        self.current = tuple(record for record in self.raw["records"]
                             if record["study_version"] == self.raw["study_version"])
        self.inventory = {row["packet_id"]: row for row in self.raw["packet_inventory"]}
        self.inspections = {row.packet_id: row for row in loaded.attachments}
        self._snapshot_cache = {}
        self.fixture = self.raw["evidence_policy"] == "fixture_only" or self.raw["material_role"] == "fixture"

    def snapshot(self, packet_id):
        if packet_id in self._snapshot_cache:
            return self._snapshot_cache[packet_id]
        entry, inspection = self.inventory.get(packet_id), self.inspections.get(packet_id)
        if entry is None or inspection is None or inspection.status != "snapshot_verified":
            return None
        location = _known(entry["location"])
        if location is None or location["kind"] != "local":
            return None
        snap = self.loaded.snapshots.get(location["path"])
        if snap is None or snap.sha256 != _known(entry["sha256"]) or snap.size_bytes != _known(entry["size_bytes"]):
            return None
        if (not isinstance(snap.content, bytes) or len(snap.content) != snap.size_bytes
                or hashlib.sha256(snap.content).hexdigest() != snap.sha256):
            raise InputError("review_snapshot_content_mismatch")
        self._snapshot_cache[packet_id] = snap
        return snap

    def artifact(self, artifact_id):
        record = self.records.get(artifact_id)
        if record is None or record["record_type"] != "artifact" or record["study_version"] != self.raw["study_version"]:
            return None, None
        content = _known(record["content"])
        snap = self.snapshot(content["packet_id"]) if content else None
        if snap and (_known(record["sha256"]) not in (None, snap.sha256)
                     or _known(record["size_bytes"]) not in (None, snap.size_bytes)):
            raise InputError("artifact_hash_mismatch")
        return record, snap


@dataclass(frozen=True)
class ReviewAssessment:
    diagnostics: tuple[Diagnostic, ...]
    items: tuple[Mapping[str, Any], ...]
    initial_agreement: Mapping[str, Any]
    qualification_status: str
    unresolved_schema_issue_ids: tuple[str, ...] = ()
    substantive_validation_performed: bool = False
    reviews: tuple[Mapping[str, Any], ...] = ()

    @property
    def has_errors(self):
        return any(item.severity == "error" for item in self.diagnostics)

    @property
    def exit_code(self):
        return 2 if self.has_errors else 0


def inspect_reviews(loaded: LoadedStudy) -> ReviewAssessment:
    """Count preserved initial categories and inspect supplied independence paths.

    The denominator is all 32 planned core items and 64 initial opportunities.
    Exact paired originals also have a separately reported common-item count.
    No estimator, cutoff, or empirical qualification is selected by this API.
    """
    issues, items, open_schema = [], [], set()
    counts = {"expected_core_items": 32, "expected_initial_slots": 64,
              "supplied_core_items": 0, "missing_core_items": 32,
              "available_core_artifact_items": 0, "unavailable_core_artifact_items": 0,
              "initial_records": 0, "occupied_initial_slots": 0,
              "missing_initial_slots": 64, "paired_items": 0,
              "unpaired_items": 32, "record_consistent_pairs": 0,
              "mechanism_agreements": 0, "mechanism_disagreements": 0,
              "resolved_class_agreements": 0, "unresolved_category_agreements": 0,
              "unclassified_category_agreements": 0, "validity_agreements": 0,
              "validity_disagreements": 0, "joint_agreements": 0,
              "pair_denominator": 0, "planned_pair_denominator": 32,
              "mechanism_category_counts": {},
              "validity_category_counts": {state: 0 for state in
                  ("valid", "invalid", "undetermined", "not_assessed")},
              "agreement_estimated": False}
    fixture = False
    public_reviews = ()
    try:
        view = _StudyView(loaded)
        fixture = view.fixture
        roster_cache, submission_cache = {}, {}
        logical_records = len(view.raw["records"]) + sum(
            entry.checked_record_count or 0 for entry in loaded.attachments)

        def packet(packet_id, kind):
            nonlocal fixture, logical_records
            cache = roster_cache if kind == "roster" else submission_cache
            if packet_id in cache:
                return cache[packet_id]
            snap = view.snapshot(packet_id)
            if snap is None:
                cache[packet_id] = None
                return None
            parsed = (parse_reviewer_roster_bytes if kind == "roster" else
                      parse_review_submission_bytes)(snap.content)
            issues.extend(parsed.diagnostics)
            raw = parsed.data
            if raw is not None:
                if any(raw[name] != view.raw[name] for name in ("study_id", "study_version")):
                    issues.append(_diag("review_packet_scope_mismatch"))
                    raw = None
                else:
                    fixture |= raw["fixture"]
                    # The loader has already counted each JSON object as one
                    # packet record, plus every unrelated acquired JSONL row.
                    # Replace that envelope count with the logical roster rows;
                    # add separately represented schema issues to submissions.
                    logical_records += (max(1, len(raw["reviewers"])) - 1 if kind == "roster"
                                        else len(raw["schema_issues"]))
                    if logical_records > min(100000, view.raw["import_budget"]["max_total_records"]):
                        raise InputError("budget_exceeded_partition_required")
            cache[packet_id] = raw
            return raw

        def inspect_record(record, expert=False):
            restrictions = []
            who = record["adjudicator" if expert else "reviewer"]
            roster = packet(_known(who["roster_packet_id"]), "roster")
            person = None
            if roster is None:
                restrictions.append("reviewer_roster_unavailable")
            else:
                row = next((row for row in roster["reviewers"] if row["reviewer_id"] == who["reviewer_id"]), None)
                if row is None:
                    restrictions.append("reviewer_identity_unresolved")
                else:
                    for name in ("entity_kind", "qualifications", "relationships", "exposure", "machine_assistance"):
                        if _serialize(who[name]) != _serialize(row[name]):
                            issues.append(_diag("reviewer_disclosure_mismatch"))
                            restrictions.append("reviewer_disclosure_mismatch")
                    person = _known(row["person_key"])
                    if person is None or _known(row["identity_evidence"]) is None:
                        restrictions.append("reviewer_identity_unresolved")
                    if row["entity_kind"] != "human":
                        restrictions.append("reviewer_not_human")
                    if row["qualification_status"] not in ({"expert"} if expert else {"qualified", "expert"}):
                        restrictions.append("expert_qualification_missing" if expert else "reviewer_qualification_missing")
                    if row["relationship_status"] != "independent":
                        restrictions.append("reviewer_relationship_unresolved_or_related")
            if who["entity_kind"] != "human":
                restrictions.append("reviewer_not_human")
            for name in ("qualifications", "relationships", "exposure", "machine_assistance"):
                if _known(who[name]) is None:
                    restrictions.append("reviewer_" + name + "_unavailable")
            if (_known(record["independence"]["declared_independent"]) is not True
                    or not record["independence"]["evidence_refs"]):
                restrictions.append("independence_evidence_unavailable")
            if record["independence"]["limitations"]:
                restrictions.append("independence_limitations_declared")
            if _known(record["submitted_at"]) is None:
                restrictions.append("submission_time_unavailable")
            submission = packet(_known(record["original_submission_packet"]), "submission")
            schema_ids = []
            if submission is None:
                restrictions.append("original_submission_unavailable")
            elif _serialize(submission["record"]) != _serialize(record):
                restrictions.append("original_submission_mismatch")
                issues.append(_diag("original_submission_mismatch"))
            else:
                if not expert and record["submission_stage"] == "initial" and _known(submission["prior_label_exposure"]) is not False:
                    restrictions.append("initial_label_exposure_or_unknown")
                if submission["copied_from"]["state"] != "not_applicable":
                    restrictions.append("copied_or_unresolved_submission")
                for row in submission["schema_issues"]:
                    for ref in row["evidence_refs"]:
                        target = view.records.get(ref["record_id"])
                        if (target is None or target["record_type"] != ref["record_type"]
                                or target["study_version"] != record["study_version"]
                                or target["scope"] != record["scope"]):
                            issues.append(_diag("schema_issue_evidence_unresolved"))
                    # A resolved assertion in a later packet never erases an open
                    # original. Resolution needs a separately accountable audit.
                    if row["status"] == "open":
                        schema_ids.append(row["issue_id"])
                        open_schema.add(row["issue_id"])
            artifact, snap = view.artifact(record["artifact_ref"]["record_id"])
            if snap is None:
                restrictions.append("reviewed_artifact_unavailable")
            elif snap.sha256 != record["artifact_sha256"]:
                restrictions.append("reviewed_artifact_hash_mismatch")
                issues.append(_diag("reviewed_artifact_hash_mismatch"))
            if artifact:
                for name in ("original_source", "ai_assistance", "exposure"):
                    if _known(artifact[name]) is None:
                        restrictions.append("artifact_" + name + "_unavailable")
            if _known(record["judgment"]["rationale"]) is None or not record["judgment"]["evidence_refs"]:
                restrictions.append("judgment_basis_unavailable")
            if expert:
                if _known(record["basis"]) is None:
                    restrictions.append("expert_basis_unavailable")
                if record["unresolved_issues"]:
                    restrictions.append("adjudication_unresolved")
            return {"review_id": record["record_id"], "status": "records_consistent_pending_authentication" if not restrictions else "restricted",
                    "restrictions": tuple(dict.fromkeys(restrictions)),
                    "person_key": person, "schema_ids": tuple(schema_ids),
                    "prior_label_exposure": submission["prior_label_exposure"] if submission else None}

        # Scope all inspection, including sampled-output reviews, to the current
        # study. Historical versions remain records without inflating this count.
        inspected = {}
        for record in view.current:
            if record["record_type"] in {"human_review", "adjudication"}:
                inspected[record["record_id"]] = inspect_record(record, record["record_type"] == "adjudication")
        for record in view.current:
            if record["record_type"] not in {"human_review", "adjudication"}:
                continue
            detail = inspected[record["record_id"]]
            reasons = list(detail["restrictions"])
            if record["record_type"] == "human_review" and record["submission_stage"] == "initial":
                # Another alias or earlier draft cannot erase known exposure.
                for earlier in view.current:
                    if (earlier["record_type"] != "human_review" or earlier["record_id"] == record["record_id"]
                            or earlier["artifact_ref"] != record["artifact_ref"]):
                        continue
                    before = inspected[earlier["record_id"]]
                    same_person = (detail["person_key"] is not None and detail["person_key"] == before["person_key"]
                                   or earlier["reviewer"]["reviewer_id"] == record["reviewer"]["reviewer_id"])
                    if not same_person or _known(before["prior_label_exposure"]) is not True:
                        continue
                    then, now = _known(earlier["submitted_at"]), _known(record["submitted_at"])
                    if then is None or now is None or datetime.fromisoformat(then.replace("Z", "+00:00")) <= datetime.fromisoformat(now.replace("Z", "+00:00")):
                        reasons.append("earlier_label_exposure_not_cleared")
            detail["restrictions"] = tuple(dict.fromkeys(reasons))
            detail["status"] = "restricted" if reasons else "records_consistent_pending_authentication"
        for record in view.current:
            if record["record_type"] != "adjudication":
                continue
            detail = inspected[record["record_id"]]
            reasons = list(detail["restrictions"])
            originals = [inspected.get(ref["record_id"]) for ref in record["initial_review_refs"]]
            if not originals or any(original is None or original["restrictions"] for original in originals):
                reasons.append("adjudication_initial_evidence_restricted")
            if detail["person_key"] is None or any(original and original["person_key"] == detail["person_key"] for original in originals):
                reasons.append("adjudicator_not_distinct_independent_expert")
            detail["restrictions"] = tuple(dict.fromkeys(reasons))
            detail["status"] = "restricted" if reasons else "records_consistent_pending_authentication"
        superseded_catalogs = {_known(record["supersedes"])["record_id"] for record in view.current
                              if record["record_type"] == "core_catalog" and _known(record["supersedes"])}
        catalogs = {}
        for record in view.current:
            if record["record_type"] == "core_catalog" and record["record_id"] not in superseded_catalogs:
                if record["role_id"] in catalogs:
                    raise InputError("ambiguous_core_role")
                catalogs[record["role_id"]] = record
        assigned_artifacts = [_known(record["artifact_ref"])["record_id"] for record in catalogs.values()
                              if _known(record["artifact_ref"]) is not None]
        if len(assigned_artifacts) != len(set(assigned_artifacts)):
            raise InputError("core_artifact_reused")
        used_artifacts = set()
        for role_id in CORE_ROLE_IDS:
            catalog = catalogs.get(role_id)
            reference = _known(catalog["artifact_ref"]) if catalog else None
            artifact_id = reference["record_id"] if reference else None
            restrictions = []
            artifact_available = False
            if artifact_id is not None:
                if artifact_id in used_artifacts:
                    restrictions.append("core_artifact_reused")
                used_artifacts.add(artifact_id)
                counts["supplied_core_items"] += 1
                _, snap = view.artifact(artifact_id)
                artifact_available = snap is not None
                counts["available_core_artifact_items" if artifact_available else "unavailable_core_artifact_items"] += 1
                if not artifact_available:
                    restrictions.append("core_artifact_bytes_unavailable")
                for name in ("source", "ai_assistance", "exposure"):
                    if _known(catalog[name]) is None:
                        restrictions.append("core_" + name + "_unavailable")
            else:
                restrictions.append("core_artifact_missing")
            reviews = [record for record in view.current if record["record_type"] == "human_review"
                       and record["artifact_ref"]["record_id"] == artifact_id]
            initial = [record for record in reviews if record["submission_stage"] == "initial"]
            revisions = [record for record in reviews if record["submission_stage"] == "revision"]
            initial_status = [inspected[record["record_id"]] for record in initial]
            counts["initial_records"] += len(initial)
            counts["occupied_initial_slots"] += min(2, len(initial))
            for record in initial:
                judgment = record["judgment"]
                category = judgment["assignment_status"]
                if category == "assigned":
                    category += ":" + _known(judgment["structural_class_id"])
                categories = counts["mechanism_category_counts"]
                categories[category] = categories.get(category, 0) + 1
                counts["validity_category_counts"][judgment["validity_status"]] += 1
            same_mechanism = same_validity = None
            consistent = False
            if len(initial) == 2:
                counts["paired_items"] += 1
                left, right = [record["judgment"] for record in initial]
                same_mechanism = (left["assignment_status"], _known(left["structural_class_id"])) == (
                    right["assignment_status"], _known(right["structural_class_id"]))
                same_validity = left["validity_status"] == right["validity_status"]
                counts["mechanism_agreements" if same_mechanism else "mechanism_disagreements"] += 1
                counts["validity_agreements" if same_validity else "validity_disagreements"] += 1
                counts["joint_agreements"] += int(same_mechanism and same_validity)
                if same_mechanism:
                    name = {"assigned": "resolved_class_agreements", "unresolved": "unresolved_category_agreements",
                            "unclassified": "unclassified_category_agreements"}[left["assignment_status"]]
                    counts[name] += 1
                people = [row["person_key"] for row in initial_status]
                if people[0] is None or people[1] is None:
                    restrictions.append("distinct_human_identity_unresolved")
                elif people[0] == people[1]:
                    restrictions.append("same_person_initial_pair")
                if initial[0]["reviewer"]["reviewer_id"] == initial[1]["reviewer"]["reviewer_id"]:
                    restrictions.append("same_reviewer_initial_pair")
                consistent = (not restrictions and all(not row["restrictions"] for row in initial_status))
                counts["record_consistent_pairs"] += int(consistent)
                if not same_mechanism or not same_validity:
                    restrictions.append("initial_disagreement_retained")
            else:
                restrictions.append("initial_pair_missing" if len(initial) < 2 else "initial_pair_ambiguous")
            adjudications = []
            for record in view.current:
                if record["record_type"] != "adjudication" or record["artifact_ref"]["record_id"] != artifact_id:
                    continue
                detail = inspected[record["record_id"]]
                reasons = list(detail["restrictions"])
                if {ref["record_id"] for ref in record["initial_review_refs"]} != {row["record_id"] for row in initial} or len(initial) != 2:
                    reasons.append("adjudication_initial_pair_mismatch")
                if detail["person_key"] is None or detail["person_key"] in {row["person_key"] for row in initial_status}:
                    reasons.append("adjudicator_not_distinct_independent_expert")
                if not consistent:
                    reasons.append("adjudication_initial_evidence_restricted")
                detail["restrictions"] = tuple(dict.fromkeys(reasons))
                detail["status"] = "restricted" if reasons else "records_consistent_pending_authentication"
                adjudications.append({"record_id": record["record_id"], "record_consistent": not reasons,
                                      "restrictions": tuple(dict.fromkeys(reasons)), "judgment": record["judgment"]})
            role_schema = tuple(sorted({ident for row in initial_status for ident in row["schema_ids"]}
                                       | {ident for record in view.current if record["record_type"] == "adjudication"
                                          and record["artifact_ref"]["record_id"] == artifact_id
                                          for ident in inspected[record["record_id"]]["schema_ids"]}))
            if role_schema:
                restrictions.append("schema_defining_contradiction_unresolved")
            items.append(freeze({"role_id": role_id, "artifact_id": artifact_id,
                "artifact_available": artifact_available,
                "initial_review_ids": tuple(row["record_id"] for row in initial),
                "revision_review_ids": tuple(row["record_id"] for row in revisions),
                "initial_record_status": tuple({key: row[key] for key in ("review_id", "status", "restrictions")} for row in initial_status),
                "pair_record_consistent": consistent, "mechanism_agreement": same_mechanism,
                "validity_agreement": same_validity, "adjudications": tuple(adjudications),
                "unresolved_schema_issue_ids": role_schema, "restrictions": tuple(dict.fromkeys(restrictions))}))
        # Public diagnostics contain no supplied identity, private text or path.
        for detail in inspected.values():
            for code in detail["restrictions"]:
                issues.append(_diag(code, severity="warning"))
        public_reviews = tuple(freeze({key: detail[key] for key in ("review_id", "status", "restrictions")})
                               for detail in inspected.values())
        if open_schema:
            issues.append(_diag("schema_defining_contradiction_unresolved", severity="warning"))
    except (InputError, KeyError, TypeError, ValueError) as exc:
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "invalid_review_context"))
    counts["missing_core_items"] = 32 - counts["supplied_core_items"]
    counts["missing_initial_slots"] = 64 - counts["occupied_initial_slots"]
    counts["unpaired_items"] = 32 - counts["paired_items"]
    counts["pair_denominator"] = counts["paired_items"]
    return ReviewAssessment(tuple(issues), tuple(items), freeze(counts),
                            "fixture_only" if fixture else "external_authentication_required",
                            tuple(sorted(open_schema)), reviews=public_reviews)


@dataclass(frozen=True)
class BlindReviewPack:
    public_files: Mapping[str, bytes] = field(repr=False)
    restricted_files: Mapping[str, bytes] = field(repr=False)
    pack_id: str


class ReviewPublicationError(InputError):
    """Publication failed; expose bounded transaction state for local recovery."""
    def __init__(self, code, restricted_status, public_status):
        super().__init__(code)
        self.restricted_status = restricted_status
        self.public_status = public_status


def review_form(review_kind="core"):
    if review_kind not in {"core", "sampled_output", "adjudication"}:
        raise InputError("invalid_review_kind")
    return {"version": "0.1", "submission_stage": "draft", "review_kind": review_kind,
        "completion_status": "blank_form", "substantive_validation_performed": False,
        "instructions": ["Return an original independent first pass before discussion.",
            "Record membership and validity separately; unresolved answers are legitimate.",
            "Record prior label or other-review exposure and machine assistance accurately.",
            "Submit real identity evidence through the separately controlled roster channel.",
            "A later amendment receives a new identity and retains the original submission.",
            "For adjudication, identify the preserved first passes, expert basis, and remaining issues."],
        "fields_to_complete": ["pseudonymous_item_id", "reviewer_id", "submitted_at",
            "qualifications", "relationships", "exposure", "machine_assistance",
            "independence_evidence", "membership_status_and_class_if_assigned",
            "validity_status", "rationale_and_exact_evidence_references", "schema_boundary_issues"],
        "membership_categories": ["assigned", "unresolved", "unclassified"],
        "validity_categories": ["valid", "invalid", "undetermined", "not_assessed"],
        "rubric_id": RUBRIC_ID}


def build_blind_review_pack(loaded: LoadedStudy, artifact_ids, *, pack_id=None,
                           review_kind="core") -> BlindReviewPack:
    """Construct exact-byte material and an allowlisted public metadata surface.

    Private metadata is never interpolated into public text or filenames. Source
    bytes remain untouched and can reveal mechanism, authorship or exposure.
    """
    view = _StudyView(loaded)
    review_assessment = inspect_reviews(loaded)
    if review_assessment.has_errors:
        raise InputError("invalid_review_context")
    fixture_only = review_assessment.qualification_status == "fixture_only"
    if not isinstance(artifact_ids, (tuple, list)) or not artifact_ids or len(artifact_ids) > 100000:
        raise InputError("invalid_review_selection")
    if any(not isinstance(value, str) for value in artifact_ids) or len(set(artifact_ids)) != len(artifact_ids):
        raise InputError("duplicate_or_invalid_review_selection")
    if review_kind not in {"core", "sampled_output"}:
        raise InputError("invalid_review_kind")
    pack_id = "pack-" + secrets.token_hex(16) if pack_id is None else pack_id
    if not isinstance(pack_id, str) or re.fullmatch(r"pack-[0-9a-f]{32}", pack_id) is None:
        raise InputError("nonopaque_review_pack_identity")
    public, rows, mapping = {}, [], []
    total = 0
    selected = list(enumerate(artifact_ids, 1))
    secrets.SystemRandom().shuffle(selected)
    for selection_position, artifact_id in selected:
        artifact, snap = view.artifact(artifact_id)
        if artifact is None or artifact["artifact_role"] not in {"core_positive", "core_defect", "core_boundary", "candidate", "source"}:
            raise InputError("review_artifact_role_mismatch")
        if snap is None:
            raise InputError("reviewed_artifact_unavailable")
        pseudonym = "item-" + secrets.token_hex(16)
        while pseudonym + ".txt" in public:
            pseudonym = "item-" + secrets.token_hex(16)
        name = pseudonym + ".txt"
        public[name] = snap.content
        total += snap.size_bytes
        rows.append({"item_id": pseudonym, "path": name})
        mapping.append({"item_id": pseudonym, "artifact_id": artifact_id,
            "original_selection_position": selection_position,
            "artifact_sha256": snap.sha256, "artifact_size_bytes": snap.size_bytes,
            "original_artifact": artifact,
            "related_records": [record for record in view.current
                if record["record_type"] in {"human_review", "adjudication", "core_catalog", "audit_selection"}
                and (_known(record.get("artifact_ref")) or record.get("artifact_ref", {})).get("record_id") == artifact_id]})
    spec = reference_specifications()["descriptor_reviews.json"]
    public["review_instructions.json"] = _serialize({"version": "0.1", "pack_id": pack_id,
        "task_id": "bounded_integer_sort", "task_version": "0.1", "rubric_id": RUBRIC_ID,
        "task": "Self-contained Python 3 source defining sort_values(values), with every helper included in this artifact. Return a fresh plain list containing the same plain integer multiset in nondecreasing order; preserve the input. Input is a plain list of plain integers, length 0 through 256 and values 0 through 4095, inclusive. Boolean and arbitrary object inputs are outside the domain. One program handles the declared domain. Tagged-record stability, constant-space complexity and speed rankings are outside this task.",
        "permitted_operations": "Ordinary loops, recursion, comparisons, integer arithmetic and bit operations, local containers and built-ins such as len, range, enumerate, list, min and max. Auxiliary storage and local helpers are permitted.",
        "prohibited_operations": ["imports", "sorted", "any .sort delegation", "external or opaque ordering routines", "dynamic source execution", "reflection used to bypass restrictions", "randomness", "filesystem, network or process access", "persistent cross-call state", "shared implementation with another candidate"],
        "validity_rubric": {"valid": "Complete original program, evidenced source/interface and operation conformance, successful complete registered 8995-case suite in an identified independently reviewed external environment. Bounded tested validity does not prove universal correctness. A formal alternative needs explicit proof assumptions and comparability review.",
            "invalid": "A decisive evidenced task violation such as an admissible-input counterexample, exception, mutation or forbidden delegation, linked to exact artifact bytes.",
            "undetermined": "Missing essential evidence, harness or environment failure, or resource exhaustion without a decisive task violation. A timeout alone never proves mathematical nontermination.",
            "not_assessed": "No validity assessment was performed.",
            "property_checks": ["fresh_plain_list", "plain_integers", "length_preserved", "nondecreasing", "multiplicity_preserved", "input_unchanged"]},
        "common_assignment_rule": spec["common_assignment_rule"],
        "common_permitted_operations": spec["common_permitted_operations"],
        "descriptors": spec["descriptors"], "items": rows,
        "withheld_fields": list(WITHHELD_FIELDS),
        "limitations": ["Original artifact bytes are unchanged and may reveal mechanism, source, names or condition clues.",
            "Metadata blinding cannot undo any reviewer exposure that occurred earlier.",
            "The separate controlled mapping retains source and exposure records; do not redistribute it.",
            "Independent review and submission authenticity have not been established by creating this pack."],
        "fixture_only": fixture_only, "substantive_validation_performed": False})
    public["review_form.json"] = _serialize(review_form(review_kind))
    roster_ids = {_known(who["roster_packet_id"]) for item in mapping for record in item["related_records"]
                  for who in [record.get("reviewer", record.get("adjudicator"))] if who is not None}
    roster_rows = []
    for packet_id in sorted(pid for pid in roster_ids if pid is not None):
        snap = view.snapshot(packet_id)
        parsed = parse_reviewer_roster_bytes(snap.content) if snap else None
        if parsed and parsed.has_errors:
            raise InputError("invalid_reviewer_roster")
        roster_rows.append({"packet_id": packet_id, "status": "locally_checked_supplied_roster" if parsed else "unavailable",
                            "roster": parsed.data if parsed else None})
    restricted = {"restricted_map.json": _serialize({"version": "0.1", "kind": "restricted_review_mapping",
        "pack_id": pack_id, "study_id": view.raw["study_id"], "study_version": view.raw["study_version"],
        "fixture_only": fixture_only, "items": mapping,
        "reviewer_rosters": roster_rows, "reviewer_assignments": [], "access_history": [],
        "disclosures": ["No person has been contacted or assigned by this export.",
                         "No new access or absence of prior exposure is asserted."]})}
    limits = _limits(None)
    for content in (public["review_instructions.json"], public["review_form.json"], *restricted.values()):
        _physical(content, limits)
        total += len(content)
    if total > limits.max_bundle_bytes:
        raise InputError("bundle_size_exceeded")
    return BlindReviewPack(freeze(public), freeze(restricted), pack_id)


def _parent_fd(target):
    target = Path(target)
    if ".." in target.parts:
        raise InputError("unsafe_local_path")
    target = target.absolute()
    relative_parts(target.name)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open("/", flags)
    try:
        for component in target.parent.parts[1:]:
            relative_parts(component)
            child = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        try:
            os.stat(target.name, dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise InputError("output_exists")
        return target, fd
    except BaseException:
        os.close(fd)
        raise


def _publish(target, parent, files, private):
    """Publish one complete directory using the established no-clobber primitive."""
    stage = ".review-stage-" + secrets.token_hex(16)
    stage_fd = None
    try:
        os.mkdir(stage, 0o700, dir_fd=parent)
        stage_fd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        for name, content in files.items():
            relative_parts(name)
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=stage_fd)
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fchmod(stream.fileno(), 0o600 if private else 0o644)
                os.fsync(stream.fileno())
        os.fchmod(stage_fd, 0o700 if private else 0o755)
        os.fsync(stage_fd)
        _rename_noreplace(parent, stage, target.name)
        stage = None
        os.fsync(parent)
    finally:
        if stage_fd is not None:
            if stage is not None:
                for name in files:
                    try:
                        os.unlink(name, dir_fd=stage_fd)
                    except FileNotFoundError:
                        pass
            os.close(stage_fd)
        if stage is not None:
            os.rmdir(stage, dir_fd=parent)


def export_blind_review_pack(loaded: LoadedStudy, artifact_ids, public_directory,
                            restricted_directory, *, pack_id=None, review_kind="core"):
    """Publish separate fresh sibling or disjoint directories without overwrites.

    Both destinations are preflighted before publication. Restricted output is
    published first with mode 0700/0600. If public publication subsequently fails,
    the restricted map is retained, allowing accountable recovery. There is no
    cross-filesystem two-directory atomicity claim and no unsafe rollback delete.
    """
    public = Path(public_directory).absolute()
    private = Path(restricted_directory).absolute()
    if public == private or public in private.parents or private in public.parents:
        raise InputError("review_output_separation_required")
    pack = build_blind_review_pack(loaded, artifact_ids, pack_id=pack_id, review_kind=review_kind)
    public_fd = private_fd = None
    private_status = public_status = "not_started"
    try:
        public, public_fd = _parent_fd(public_directory)
        private, private_fd = _parent_fd(restricted_directory)
        private_status = "may_have_completed"
        _publish(private, private_fd, pack.restricted_files, True)
        private_status = "completed"
        public_status = "may_have_completed"
        _publish(public, public_fd, pack.public_files, False)
        public_status = "completed"
        return {"pack_id": pack.pack_id, "public_directory": str(public),
                "restricted_directory": str(private), "item_count": len(artifact_ids),
                "substantive_validation_performed": False}
    except (InputError, OSError) as exc:
        raise ReviewPublicationError(exc.code if isinstance(exc, InputError) else "unsafe_or_unavailable_output_path",
                                     private_status, public_status) from exc
    finally:
        if public_fd is not None:
            os.close(public_fd)
        if private_fd is not None:
            os.close(private_fd)
