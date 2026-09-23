"""Independent review accounting, evidence-boundary, and privacy regression.

All people and judgments below are invented software fixtures. The tests never
recruit reviewers, execute a candidate, or claim empirical review completion.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import study_records as sr
from structdet_bench import study_review as review
from structdet_bench.contracts import InputError
from structdet_bench.local_io import ReadLimits


FIXTURES = Path(__file__).resolve().parent / "fixtures/phase4"


def K(value=None, state="known"):
    return {"state": state, "value": value} if state == "known" else {
        "state": state, "reason": "Synthetic uncertainty; no real human evidence."}


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n").encode()


def ref(record):
    return {k: record[k] for k in ("record_type", "record_id", "record_version")}


class Fixture:
    """Author temporary evidence independently; never import production builders."""
    def __init__(self, root):
        self.root = Path(root)
        self.data = json.loads((FIXTURES / "review_study.json").read_bytes())
        self.roster = json.loads((FIXTURES / "review_roster.json").read_bytes())
        self.submissions = {}
        for letter in "abcde":
            packet = json.loads((FIXTURES / f"review_initial_{letter}.json").read_bytes())
            self.submissions[f"review-submission-{letter}"] = packet
        (self.root / "study_payload.txt").write_bytes((FIXTURES / "study_payload.txt").read_bytes())
        self.sync()

    def record(self, identifier):
        return next(r for r in self.data["records"] if r["record_id"] == identifier)

    def packet_entry(self, identifier):
        return next(p for p in self.data["packet_inventory"] if p["packet_id"] == identifier)

    def sync(self, *, bind_submissions=True):
        if bind_submissions:
            for packet in self.submissions.values():
                packet["record"] = copy.deepcopy(self.record(packet["record"]["record_id"]))
        for packet_id, data in {"review-roster": self.roster, **self.submissions}.items():
            entry = self.packet_entry(packet_id)
            raw = encoded(data)
            (self.root / entry["location"]["value"]["path"]).write_bytes(raw)
            entry["sha256"] = K(hashlib.sha256(raw).hexdigest())
            entry["size_bytes"] = K(len(raw))
        (self.root / "study.json").write_bytes(encoded(self.data))

    def load(self, *, bind_submissions=True):
        self.sync(bind_submissions=bind_submissions)
        return sr.load_study(self.root / "study.json")

    def assess(self, *, bind_submissions=True):
        return review.inspect_reviews(self.load(bind_submissions=bind_submissions))

    def actor(self, number):
        return self.roster["reviewers"][number - 1]

    def mirror_actor_disclosures(self, number):
        actor = self.actor(number)
        for record in self.data["records"]:
            who = record.get("reviewer", record.get("adjudicator"))
            if who and who["reviewer_id"] == actor["reviewer_id"]:
                for key in ("entity_kind", "qualifications", "relationships", "exposure", "machine_assistance"):
                    who[key] = copy.deepcopy(actor[key])

    def add_submission(self, record, *, exposure=False, schema_issues=()):
        packet_id = "packet-" + record["record_id"]
        record["original_submission_packet"] = K(packet_id)
        self.data["records"].append(record)
        self.submissions[packet_id] = {
            "version": "0.1", "kind": "review_submission", "study_id": self.data["study_id"],
            "study_version": self.data["study_version"], "fixture": True,
            "rubric_id": "bounded_integer_sort_validity_v1", "record": copy.deepcopy(record),
            "prior_label_exposure": K(exposure), "copied_from": K(state="not_applicable"),
            "schema_issues": list(schema_issues)}
        self.data["packet_inventory"].append({
            "packet_id": packet_id, "purpose": "review",
            "location": K({"kind": "local", "path": packet_id + ".json"}),
            "sha256": K(state="unknown"), "size_bytes": K(state="unknown"),
            "record_count": K(1), "format": "json", "verification": "unchecked",
            "verification_ref": K(state="unknown")})
        return record

    def add_revision(self):
        initial = self.record("review-initial-d")
        amendment = copy.deepcopy(initial)
        amendment["record_id"] = "review-revision-d"
        amendment["revision"] = 2
        amendment["submission_stage"] = "revision"
        amendment["submitted_at"] = K("2026-09-23T00:00:00Z")
        amendment["initial_submission_ref"] = K(ref(initial))
        amendment["supersedes"] = K(ref(initial))
        amendment["judgment"] = copy.deepcopy(self.record("review-initial-c")["judgment"])
        return self.add_submission(amendment, exposure=True)

    def add_adjudication(self):
        old = json.loads((FIXTURES / "study_complete.json").read_bytes())
        decision = copy.deepcopy(next(r for r in old["records"] if r["record_type"] == "adjudication"))
        initial = self.record("review-initial-c")
        decision["record_id"] = "review-adjudication-b"
        decision["artifact_ref"] = copy.deepcopy(initial["artifact_ref"])
        decision["artifact_sha256"] = initial["artifact_sha256"]
        decision["initial_review_refs"] = [ref(initial), ref(self.record("review-initial-d"))]
        decision["adjudicator"] = copy.deepcopy(initial["reviewer"])
        actor = self.actor(3)
        for key in ("reviewer_id", "entity_kind", "qualifications", "relationships", "exposure", "machine_assistance"):
            decision["adjudicator"][key] = copy.deepcopy(actor[key])
        decision["independence"] = copy.deepcopy(initial["independence"])
        decision["disagreement"] = "Stipulated original class and validity disagreement."
        decision["basis"] = K("Stipulated reviewed constitutive-relation evidence; no real expert finding.")
        decision["judgment"] = copy.deepcopy(initial["judgment"])
        decision["unresolved_issues"] = []
        decision["submitted_at"] = K("2026-09-24T00:00:00Z")
        return self.add_submission(decision, exposure=True)


def item(assessment, role="CORE-ADJ-A"):
    return next(i for i in assessment.items if i["role_id"] == role)


class ReviewAccountingTests(unittest.TestCase):
    def test_fixed_planned_counts_and_initial_common_item_denominator(self):
        assessed = review.inspect_reviews(sr.load_study(FIXTURES / "review_study.json"))
        expected = json.loads((FIXTURES / "review_expected.json").read_bytes())["initial_agreement"]
        self.assertFalse(assessed.has_errors, assessed.diagnostics)
        for field, value in expected.items():
            with self.subTest(field=field):
                self.assertEqual(assessed.initial_agreement[field], value)
        self.assertEqual(len(assessed.items), 32)
        self.assertEqual(assessed.qualification_status, "fixture_only")
        self.assertIs(assessed.substantive_validation_performed, False)

    def test_missing_reviews_stay_in_planned_inventory(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            f.data["records"] = [r for r in f.data["records"] if r["record_type"] != "human_review"]
            f.submissions.clear()
            f.data["packet_inventory"] = [p for p in f.data["packet_inventory"] if p["packet_id"] in {"payload", "review-roster"}]
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            self.assertEqual(result.initial_agreement["missing_initial_slots"], 64)
            self.assertEqual(result.initial_agreement["pair_denominator"], 0)
            self.assertEqual(result.initial_agreement["planned_pair_denominator"], 32)
            self.assertEqual(result.initial_agreement["supplied_core_items"], 3)

    def test_reused_core_artifact_cannot_duplicate_the_same_agreement_pair(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            f.record("review-core-b")["artifact_ref"] = copy.deepcopy(f.record("review-core-a")["artifact_ref"])
            result = f.assess()
            self.assertTrue(result.has_errors or result.initial_agreement["pair_denominator"] == 1)
            self.assertLessEqual(result.initial_agreement["mechanism_agreements"], 1)

    def test_unresolved_and_unclassified_agreement_remain_categories(self):
        for status, counter in [("unresolved", "unresolved_category_agreements"),
                                ("unclassified", "unclassified_category_agreements")]:
            with self.subTest(status=status), TemporaryDirectory() as directory:
                f = Fixture(directory)
                for letter in "ab":
                    j = f.record("review-initial-" + letter)["judgment"]
                    j["assignment_status"] = status
                    j["structural_class_id"] = K(state="unknown")
                result = f.assess()
                self.assertFalse(result.has_errors, result.diagnostics)
                self.assertEqual(result.initial_agreement[counter], 1)
                self.assertEqual(result.initial_agreement["resolved_class_agreements"], 0)
                self.assertEqual(result.initial_agreement["mechanism_agreements"], 1)
                self.assertEqual(result.initial_agreement["pair_denominator"], 2)

    def test_validity_categories_are_separate_from_class_agreement(self):
        for state in ("valid", "invalid", "undetermined", "not_assessed"):
            with self.subTest(state=state), TemporaryDirectory() as directory:
                f = Fixture(directory)
                for letter in "ab":
                    f.record("review-initial-" + letter)["judgment"]["validity_status"] = state
                result = f.assess()
                self.assertEqual(result.initial_agreement["validity_agreements"], 1)
                self.assertEqual(result.initial_agreement["mechanism_agreements"], 1)
                self.assertEqual(result.initial_agreement["validity_category_counts"][state],
                    sum(r["judgment"]["validity_status"] == state for r in f.data["records"] if r["record_type"] == "human_review"))

    def test_revision_and_adjudication_do_not_rewrite_first_pass_agreement(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            originals = {r["record_id"]: encoded(r) for r in f.data["records"] if r["record_type"] == "human_review"}
            before = dict(f.assess().initial_agreement)
            f.add_revision()
            decision = f.add_adjudication()
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            self.assertEqual(dict(result.initial_agreement), before)
            for identity, raw in originals.items():
                self.assertEqual(encoded(f.record(identity)), raw)
            second = item(result, "CORE-INS-A")
            self.assertEqual(tuple(second["initial_review_ids"]), ("review-initial-c", "review-initial-d"))
            self.assertIn("review-revision-d", second["revision_review_ids"])
            self.assertEqual(second["adjudications"][0]["record_id"], decision["record_id"])

    def test_exact_original_packet_prevents_in_place_amendment(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            f.record("review-initial-b")["judgment"]["validity_status"] = "invalid"
            result = f.assess(bind_submissions=False)
            self.assertTrue(result.has_errors)
            self.assertFalse(item(result)["pair_record_consistent"])


class ReviewIndependenceTests(unittest.TestCase):
    def test_alias_person_machine_and_unknown_identity_cannot_supply_two_humans(self):
        for failure in ("alias", "machine", "unknown_person", "missing_identity_evidence"):
            with self.subTest(failure=failure), TemporaryDirectory() as directory:
                f = Fixture(directory)
                actor = f.actor(2)
                if failure == "alias":
                    actor["person_key"] = copy.deepcopy(f.actor(1)["person_key"])
                elif failure == "machine":
                    actor["entity_kind"] = "machine"
                    f.mirror_actor_disclosures(2)
                elif failure == "unknown_person":
                    actor["person_key"] = K(state="unknown")
                else:
                    actor["identity_evidence"] = K(state="unavailable")
                result = f.assess()
                self.assertFalse(item(result)["pair_record_consistent"])
                self.assertEqual(result.initial_agreement["record_consistent_pairs"], 0)
                self.assertIs(result.substantive_validation_performed, False)

    def test_duplicate_initial_records_do_not_create_extra_qualified_slots(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            duplicate = copy.deepcopy(f.record("review-initial-a"))
            duplicate["record_id"] = "review-duplicate-a"
            f.add_submission(duplicate)
            result = f.assess()
            self.assertFalse(item(result)["pair_record_consistent"])
            self.assertEqual(result.initial_agreement["occupied_initial_slots"], 5)
            self.assertEqual(result.initial_agreement["missing_initial_slots"], 59)
            self.assertEqual(result.initial_agreement["paired_items"], 1)

    def test_copy_exposure_and_unavailable_provenance_never_become_independence(self):
        cases = [("copied_from", K("review-initial-a")), ("copied_from", K(state="unknown")),
                 ("prior_label_exposure", K(True)), ("prior_label_exposure", K(state="unavailable"))]
        for field, value in cases:
            with self.subTest(field=field, value=value), TemporaryDirectory() as directory:
                f = Fixture(directory)
                f.submissions["review-submission-b"][field] = value
                result = f.assess()
                self.assertFalse(item(result)["pair_record_consistent"])
                self.assertTrue(item(result)["initial_record_status"][1]["restrictions"])

    def test_unqualified_related_missing_disclosures_and_missing_lineage_are_restricted(self):
        cases = ("unqualified", "related", "unknown_relationship", "qualifications", "relationships", "exposure", "machine_assistance", "independence_basis", "artifact_source", "artifact_assistance", "artifact_exposure")
        for failure in cases:
            with self.subTest(failure=failure), TemporaryDirectory() as directory:
                f = Fixture(directory)
                actor = f.actor(2)
                if failure == "unqualified":
                    actor["qualification_status"] = "unqualified"
                elif failure in {"related", "unknown_relationship"}:
                    actor["relationship_status"] = "related" if failure == "related" else "unknown"
                elif failure == "independence_basis":
                    f.record("review-initial-b")["independence"]["evidence_refs"] = []
                elif failure.startswith("artifact_"):
                    key = {"artifact_source": "original_source", "artifact_assistance": "ai_assistance", "artifact_exposure": "exposure"}[failure]
                    f.record("review-artifact-a")[key] = K(state="unknown")
                else:
                    actor[failure] = K(state="unknown")
                    f.mirror_actor_disclosures(2)
                result = f.assess()
                self.assertFalse(item(result)["pair_record_consistent"])

    def test_later_blinding_claim_does_not_erase_original_exposure(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            f.submissions["review-submission-d"]["prior_label_exposure"] = K(True)
            amendment = f.add_revision()
            f.submissions[amendment["original_submission_packet"]["value"]]["prior_label_exposure"] = K(False)
            result = f.assess()
            self.assertFalse(item(result, "CORE-INS-A")["pair_record_consistent"])
            self.assertTrue(item(result, "CORE-INS-A")["initial_record_status"][1]["restrictions"])

    def test_prior_draft_exposure_tracks_person_alias_and_chronology(self):
        cases = (("before", False, False), ("before", True, False),
                 ("unknown", False, False), ("after", False, True))
        for chronology, alias, expected_consistent in cases:
            with self.subTest(chronology=chronology, alias=alias), TemporaryDirectory() as directory:
                f = Fixture(directory)
                draft = copy.deepcopy(f.record("review-initial-a"))
                draft["record_id"] = "review-exposed-draft"
                draft["submission_stage"] = "draft"
                draft["submitted_at"] = (K(state="unknown") if chronology == "unknown" else
                    K("2026-09-21T00:00:00Z" if chronology == "before" else "2026-09-23T00:00:00Z"))
                if alias:
                    f.actor(3)["person_key"] = copy.deepcopy(f.actor(1)["person_key"])
                    draft["reviewer"]["reviewer_id"] = f.actor(3)["reviewer_id"]
                f.add_submission(draft, exposure=True)
                result = f.assess()
                self.assertFalse(result.has_errors, result.diagnostics)
                self.assertEqual(item(result)["pair_record_consistent"], expected_consistent)
                self.assertEqual(result.initial_agreement["paired_items"], 2)
                self.assertEqual(result.initial_agreement["mechanism_agreements"], 1)

    def test_expert_adjudicator_must_be_distinct_qualified_and_supported(self):
        for failure in ("alias_initial", "not_expert", "related", "missing_basis"):
            with self.subTest(failure=failure), TemporaryDirectory() as directory:
                f = Fixture(directory)
                adjudication = f.add_adjudication()
                if failure == "alias_initial":
                    f.actor(3)["person_key"] = copy.deepcopy(f.actor(1)["person_key"])
                elif failure == "not_expert":
                    f.actor(3)["qualification_status"] = "qualified"
                elif failure == "related":
                    f.actor(3)["relationship_status"] = "related"
                else:
                    adjudication["basis"] = K(state="unknown")
                result = f.assess()
                decision = item(result, "CORE-INS-A")["adjudications"][0]
                self.assertFalse(decision["record_consistent"])
                self.assertTrue(decision["restrictions"])
                self.assertEqual(result.initial_agreement["mechanism_disagreements"], 1)

    def test_fixture_packets_remain_fixtures_under_nonfixture_parent(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            f.data["material_role"] = "descriptive"
            f.data["evidence_policy"] = "adjudicated_import"
            result = f.assess()
            self.assertEqual(result.qualification_status, "fixture_only")
            self.assertIs(result.substantive_validation_performed, False)

    def test_schema_boundary_conflict_survives_perfect_observed_agreement(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            f.record("review-initial-d")["judgment"] = copy.deepcopy(f.record("review-initial-c")["judgment"])
            f.submissions["review-submission-a"]["schema_issues"] = [{
                "issue_id": "fixture-schema-overlap", "descriptor_ids": ["SORT-ADJ", "SORT-INS"],
                "status": "open", "resolution": K(state="unknown"),
                "evidence_refs": [ref(f.record("review-artifact-a"))]}]
            result = f.assess()
            self.assertEqual(result.initial_agreement["mechanism_agreements"], 2)
            self.assertEqual(result.initial_agreement["pair_denominator"], 2)
            self.assertIn("fixture-schema-overlap", item(result)["unresolved_schema_issue_ids"])
            self.assertTrue(item(result)["restrictions"])


class ReviewIdentityAndInputTests(unittest.TestCase):
    def test_snapshot_content_must_match_its_actual_hash_and_size(self):
        loaded = sr.load_study(FIXTURES / "review_study.json")
        path = "study_payload.txt"
        snapshot = loaded.snapshots[path]
        forged_snapshot = replace(snapshot, content=b"X" * snapshot.size_bytes)
        forged = replace(loaded, snapshots={**loaded.snapshots, path: forged_snapshot})
        result = review.inspect_reviews(forged)
        self.assertTrue(result.has_errors)
        with self.assertRaises(InputError):
            review.build_blind_review_pack(forged, ["review-artifact-a"])

    def test_record_and_roster_disclosure_mismatch_is_rejected(self):
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            f.record("review-initial-b")["reviewer"]["machine_assistance"] = K("Hidden assistance disclosure replacement.")
            result = f.assess()
            self.assertTrue(result.has_errors)
            self.assertFalse(item(result)["pair_record_consistent"])

    def test_artifact_scope_version_and_rubric_bindings_cannot_be_reused(self):
        cases = ("artifact", "hash", "scope", "study_version", "rubric")
        for failure in cases:
            with self.subTest(failure=failure), TemporaryDirectory() as directory:
                f = Fixture(directory)
                r = f.record("review-initial-b")
                if failure == "artifact":
                    r["artifact_ref"] = ref(f.record("review-artifact-b"))
                elif failure == "hash":
                    r["artifact_sha256"] = "0" * 64
                elif failure == "scope":
                    r["scope"]["claim_id"] = "different-claim"
                elif failure == "study_version":
                    f.submissions["review-submission-b"]["study_version"] = "v2"
                else:
                    f.submissions["review-submission-b"]["rubric_id"] = "other-rubric"
                result = f.assess()
                self.assertTrue(result.has_errors or not item(result)["pair_record_consistent"])

    def test_missing_or_corrupt_roster_and_submission_never_qualify(self):
        for packet_id in ("review-roster", "review-submission-b"):
            for failure in ("missing", "corrupt"):
                with self.subTest(packet=packet_id, failure=failure), TemporaryDirectory() as directory:
                    f = Fixture(directory)
                    path = f.root / f.packet_entry(packet_id)["location"]["value"]["path"]
                    if failure == "missing":
                        path.unlink()
                    else:
                        path.write_bytes(path.read_bytes() + b" ")
                    result = review.inspect_reviews(sr.load_study(f.root / "study.json"))
                    self.assertTrue(result.has_errors or not item(result)["pair_record_consistent"])

    def test_roster_strict_grammar_and_physical_limits(self):
        valid = json.loads((FIXTURES / "review_roster.json").read_bytes())
        bad_objects = []
        extra = copy.deepcopy(valid)
        extra["opaque_execution"] = "PRIVATE_SOURCE_SENTINEL"
        bad_objects.append(extra)
        duplicate = copy.deepcopy(valid)
        duplicate["reviewers"].append(copy.deepcopy(duplicate["reviewers"][0]))
        bad_objects.append(duplicate)
        boolean = copy.deepcopy(valid)
        boolean["fixture"] = 1
        bad_objects.append(boolean)
        for data in bad_objects:
            with self.subTest(data=data):
                self.assertTrue(review.parse_reviewer_roster_bytes(encoded(data)).has_errors)
        for raw in (b'{"kind":"reviewer_roster","kind":"reviewer_roster"}', b'{"x":NaN}', b'['*65+b'0'+b']'*65):
            with self.subTest(raw=raw[:70]):
                self.assertTrue(review.parse_reviewer_roster_bytes(raw).has_errors)
        self.assertTrue(review.parse_reviewer_roster_bytes(encoded(valid), ReadLimits(max_file_bytes=100)).has_errors)
        # Twelve envelope records + six physical JSON records + ten unrelated
        # JSONL records + two additional roster rows = thirty logical records.
        # Unrelated acquired records remain in the same declared budget.
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            raw = b"{}\n" * 10
            (f.root / "review_unused.jsonl").write_bytes(raw)
            f.data["packet_inventory"].append({
                "packet_id": "unused-records", "purpose": "evidence",
                "location": K({"kind": "local", "path": "review_unused.jsonl"}),
                "sha256": K(hashlib.sha256(raw).hexdigest()), "size_bytes": K(len(raw)),
                "record_count": K(10), "format": "jsonl", "verification": "unchecked",
                "verification_ref": K(state="unknown")})
            for limit, expected_error in ((29, True), (30, False)):
                with self.subTest(logical_record_limit=limit):
                    f.data["import_budget"]["max_total_records"] = limit
                    loaded = f.load()
                    self.assertFalse(loaded.has_errors, loaded.diagnostics)
                    self.assertEqual(review.inspect_reviews(loaded).has_errors, expected_error)


class BlindReviewExportTests(unittest.TestCase):
    def test_public_pack_omits_identity_labels_condition_and_other_judgments(self):
        loaded = sr.load_study(FIXTURES / "review_study.json")
        pack = review.build_blind_review_pack(loaded, ["review-artifact-a", "review-artifact-b"], pack_id="pack-" + "a" * 32)
        public = b"\n".join(pack.public_files.values())
        restricted = b"\n".join(pack.restricted_files.values())
        for marker in (b"PRIVATE_SOURCE_SENTINEL", b"PRIVATE_MODEL_SENTINEL", b"PRIVATE_CONDITION_SENTINEL",
                       b"PRIVATE_ROLE_SENTINEL", b"PRIVATE_JUDGMENT_SENTINEL", b"review-artifact-a",
                       b"review-initial-a", b"fixture-reviewer-1", b"fixture-person-1", b"CORE-ADJ-A"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, public)
        self.assertIn(b"review-artifact-a", restricted)
        self.assertIn((FIXTURES / "study_payload.txt").read_bytes(), pack.public_files.values())
        self.assertTrue(pack.restricted_files)

    def test_export_writes_separate_fresh_roots_and_preserves_existing_paths(self):
        loaded = sr.load_study(FIXTURES / "review_study.json")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            public, private = root / "public", root / "restricted"
            review.export_blind_review_pack(loaded, ["review-artifact-a"], public, private, pack_id="pack-" + "b" * 32)
            public_before = {str(p.relative_to(public)): p.read_bytes() for p in public.rglob("*") if p.is_file()}
            private_before = {str(p.relative_to(private)): p.read_bytes() for p in private.rglob("*") if p.is_file()}
            self.assertTrue(public_before)
            self.assertTrue(private_before)
            with self.assertRaises(InputError):
                review.export_blind_review_pack(loaded, ["review-artifact-b"], public, private, pack_id="pack-" + "c" * 32)
            self.assertEqual(public_before, {str(p.relative_to(public)): p.read_bytes() for p in public.rglob("*") if p.is_file()})
            self.assertEqual(private_before, {str(p.relative_to(private)): p.read_bytes() for p in private.rglob("*") if p.is_file()})

    def test_overlap_symlink_and_preexisting_target_are_rejected_without_clobber(self):
        loaded = sr.load_study(FIXTURES / "review_study.json")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for public, private in ((root / "same", root / "same"), (root / "outer", root / "outer" / "private")):
                with self.subTest(public=public), self.assertRaises(InputError):
                    review.export_blind_review_pack(loaded, ["review-artifact-a"], public, private)
            existing = root / "existing"
            existing.mkdir()
            (existing / "keep").write_bytes(b"original")
            link = root / "linked"
            link.symlink_to(existing, target_is_directory=True)
            with self.assertRaises(InputError):
                review.export_blind_review_pack(loaded, ["review-artifact-a"], link / "public", root / "private")
            self.assertEqual((existing / "keep").read_bytes(), b"original")
            self.assertFalse((existing / "public").exists())

    def test_missing_duplicate_or_unknown_artifact_cannot_be_silently_exported(self):
        loaded = sr.load_study(FIXTURES / "review_study.json")
        for selection in ([], ["unknown"], ["review-artifact-a", "review-artifact-a"]):
            with self.subTest(selection=selection), self.assertRaises(InputError):
                review.build_blind_review_pack(loaded, selection)
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            (f.root / "study_payload.txt").unlink()
            with self.assertRaises(InputError):
                review.build_blind_review_pack(f.load(), ["review-artifact-a"])

    def test_review_and_export_are_passive_and_source_snapshots_are_immutable(self):
        loaded = sr.load_study(FIXTURES / "review_study.json")
        before = {path: snapshot.content for path, snapshot in loaded.snapshots.items()}
        with patch("subprocess.Popen", side_effect=AssertionError("passive review attempted process execution")), \
                patch("builtins.eval", side_effect=AssertionError("passive review attempted evaluation")):
            review.inspect_reviews(loaded)
            review.build_blind_review_pack(loaded, ["review-artifact-a"], review_kind="sampled_output")
        self.assertEqual(before, {path: snapshot.content for path, snapshot in loaded.snapshots.items()})


if __name__ == "__main__":
    unittest.main()
