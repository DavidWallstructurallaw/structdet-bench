"""Direct evidence/audit semantics. All records and people are synthetic.

Expected positions and populations are authored separately from the product.
No candidate program, external collector, or human review is executed.
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

from structdet_bench import study_evidence as se
from structdet_bench import study_records as sr
from structdet_bench.local_io import ReadLimits
from tests.test_study_collection import Fixture as CollectionFixture, K, ref, encoded, MAIN_ROTATIONS
from tests.test_study_validation import stage as validation_stage

FIXTURES = Path(__file__).resolve().parent / "fixtures/phase4"
EXPECTED = json.loads((FIXTURES / "evidence/audit_expected.json").read_bytes())
CONDITIONS = ("structural_validity", "external_presence", "source_integrity", "tail_retention", "corrective_capacity")


class Fixture(CollectionFixture):
    def __init__(self, root):
        super().__init__(root)
        self.data["import_budget"] = {"max_packets": 4096, "max_total_bytes": 64 * 1024 * 1024, "max_total_records": 100000}
        frame = self.data["records"][0]["frame_definition"]
        for key in frame:
            frame[key] = ["Stipulated load-bearing invariant."] if key == "load_bearing_invariants" else K("Stipulated bounded sorting frame; fixture only.")
        self.roster = json.loads((FIXTURES / "review_roster.json").read_bytes())
        source = json.loads((FIXTURES / "review_study.json").read_bytes())
        self.review_template = copy.deepcopy(next(r for r in source["records"] if r["record_type"] == "human_review"))
        self.review_packets = {}
        self.evidence = {"kind": "evidence_qualification", "version": "0.1", "packet_id": "submission-qualification",
            "study_id": "fixture-study", "study_version": "v1", "fixture": True,
            "pins": copy.deepcopy(self.data["records"][0]["pins"]), "evidence": [], "qualifications": [],
            "independence": [], "audit_flags": [], "claims": []}
        self.notes = self.artifact("evidence-notes", b"Stipulated mechanism inspection; no actual review.\n")
        self.notes["artifact_role"] = "evidence"
        for field in ("original_source", "ai_assistance", "exposure"):
            self.notes[field] = K("Stipulated provenance, never authenticated.")

    def add_group(self, block="P01", condition="A", group=1, indices=(1, 2, 3, 4, 5), same_bytes=False):
        identifier = f"call-{block}-{condition}-{group}"
        bodies = {n: f"# inert {identifier} candidate {n}\n".encode() for n in indices}
        if same_bytes:
            bodies = {n: b"# shared inert bytes\n" for n in indices}
        raw = b"".join(f"### Candidate {n}\n```python\n".encode() + bodies[n] + b"```\n" for n in indices)
        call = self.add_call(identifier, block=block, condition=condition, group=group, raw=raw)
        old = json.loads((FIXTURES / "study_complete.json").read_bytes())
        ex = copy.deepcopy(next(r for r in old["records"] if r["record_type"] == "extraction"))
        ex.update(record_id="extract-" + identifier, collection_ref=ref(call),
            raw_response_ref=copy.deepcopy(call["raw_response_ref"]),
            raw_response_sha256=K(hashlib.sha256(raw).hexdigest()), extras=[], limitations=[])
        artifacts = []
        for n, pos in enumerate(ex["positions"], 1):
            if n in indices:
                a = self.artifact(f"candidate-{block}-{condition}-{group}-{n}", bodies[n])
                a["artifact_role"] = "candidate"
                for field in ("original_source", "ai_assistance", "exposure"):
                    a[field] = K("Stipulated synthetic source.")
                start = raw.index(bodies[n], raw.index(f"### Candidate {n}\n".encode()))
                pos.update(selection="selected", artifact_ref=K(ref(a)), byte_range=K({"start": start, "end": start + len(bodies[n])}),
                    heading=K(f"### Candidate {n}"), fence=K("```python"), completion_status="complete", limitations=[])
                artifacts.append(a)
            else:
                pos.update(selection="missing", artifact_ref=K(state="unknown"), byte_range=K(state="unknown"),
                    heading=K(state="unknown"), fence=K(state="unknown"), completion_status="unknown", limitations=["candidate_not_emitted"])
        self.data["records"].append(ex)
        return artifacts

    def judge(self, artifact, cid="SORT-ADJ", *, person=1, suffix="label", status="assigned", validity="not_assessed"):
        row = copy.deepcopy(self.review_template)
        row.update(record_id=suffix + "-" + artifact["record_id"], artifact_ref=ref(artifact), artifact_sha256=artifact["sha256"]["value"])
        actor = self.roster["reviewers"][person - 1]
        row["reviewer"] = {k: copy.deepcopy(actor[k]) for k in ("reviewer_id", "entity_kind", "qualifications", "relationships", "exposure", "machine_assistance")}
        row["reviewer"]["roster_packet_id"] = K("submission-roster")
        row["judgment"].update(assignment_status=status, structural_class_id=K(cid) if status == "assigned" else K(state="unknown"),
            validity_status=validity, rationale=K("Stipulated inspection of all constitutive relations and reachable branches."), evidence_refs=[ref(self.notes)])
        row["independence"] = {"declared_independent": K(True), "evidence_refs": [ref(self.notes)], "limitations": []}
        row["original_submission_packet"] = K("submission-" + row["record_id"])
        self.data["records"].append(row)
        self.review_packets["submission-" + row["record_id"]] = {"kind": "review_submission", "version": "0.1",
            "study_id": "fixture-study", "study_version": "v1", "fixture": True,
            "rubric_id": "bounded_integer_sort_validity_v1", "record": row,
            "prior_label_exposure": K(False), "copied_from": K(state="not_applicable"), "schema_issues": []}
        return row

    def qualify(self, artifact, cid="SORT-ADJ", *, status="assigned", validity="not_assessed"):
        judge = self.judge(artifact, cid, status=status, validity=validity)
        eid = "mechanism-" + artifact["record_id"]
        ev = {"evidence_id": eid, "target_ref": ref(artifact), "subject_sha256": artifact["sha256"]["value"],
            "source_ref": ref(self.notes), "reviewer_ref": K(ref(judge)), "purpose": "mechanism", "method": "control_flow",
            "state": "active", "basis": K("Stipulated source-bound inspection."), "reachable_branches": K("All reachable branches inspected."),
            "constitutive_relations": K("Stipulated complete mechanism relation argument."),
            "structural_class_id": K(cid) if status == "assigned" else K(state="unknown"),
            "validation_ref": K(state="not_applicable"), "supported_claim_ids": [], "system_id": K(state="unknown"), "period": K(state="unknown")}
        self.evidence["evidence"].append(ev)
        self.evidence["qualifications"].append({"artifact_ref": ref(artifact), "judgment_ref": K(ref(judge)),
            "essential_evidence_ids": [eid], "validation_refs": [], "independence_ids": []})
        return judge, ev

    def audit_record(self, artifact, position, *, person=2, cid="SORT-ADJ"):
        review = self.judge(artifact, cid, person=person, suffix="audit")
        row = copy.deepcopy(next(r for r in json.loads((FIXTURES / "study_complete.json").read_bytes())["records"] if r["record_type"] == "audit_selection"))
        row.update(record_id="audit-selection-" + artifact["record_id"], artifact_ref=K(ref(artifact)), position=position,
                   opportunity="present", distinct_artifact_count=1, reasons=["systematic"], review_refs=[ref(review)])
        self.data["records"].append(row)
        return row

    def add_claim(self, artifact, judge, *, kind="operational_openness"):
        claim = {"claim_id": "test-claim", "kind": kind, "statement": "Synthetic claim; no external study.",
            "artifact_refs": [ref(artifact)], "system_id": K("test-system"),
            "period": K({"start": "2026-01-01T00:00:00Z", "end": "2026-02-01T00:00:00Z"}),
            "requirements": [], "components": [{"component_id": c, "version": K("v1"), "contents_state": "known_empty", "artifact_refs": []}
                for c in ("stable_core", "rotating_frontier", "external_incident", "tail_registry")]}
        purposes = ("schema", "external_presence", "independence", "tail_retention", "correction")
        for condition, purpose in zip(CONDITIONS, purposes):
            ev = copy.deepcopy(self.evidence["evidence"][0])
            ev.update(evidence_id="condition-" + condition, purpose=purpose, method="human_inspection", supported_claim_ids=["test-claim"],
                      system_id=copy.deepcopy(claim["system_id"]), period=copy.deepcopy(claim["period"]))
            if purpose in {"external_presence", "correction"}:
                template = json.loads((FIXTURES / "study_complete.json").read_bytes())
                event = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "correction_incident"))
                event.update(record_id="event-" + purpose, kind="incident" if purpose == "external_presence" else "correction",
                    action_status="performed", action=K("Stipulated consequential reviewed use of the external finding."),
                    performed_at=K("2026-01-10T00:00:00Z"), reviewer_authority=K("Stipulated responsible reviewer."),
                    affected_refs=[ref(artifact)], evidence_refs=[ref(self.notes)])
                self.data["records"].append(event)
                ev.update(target_ref=ref(event), subject_sha256=hashlib.sha256(
                    (json.dumps(event, sort_keys=True, indent=2) + "\n").encode()).hexdigest())
            self.evidence["evidence"].append(ev)
            if purpose == "independence":
                self.evidence["independence"].append({"assessment_id": "claim-independence", "left_ref": ref(artifact), "right_ref": ref(self.notes),
                    "dimension": "validation_method", "outcome": "supported_for_scope", "basis": K("Stipulated scoped method independence."),
                    "assessor_ref": K(ref(judge)), "evidence_ids": [ev["evidence_id"]], "limitations": []})
            claim["requirements"].append({"requirement_id": condition, "outcome": "satisfied_for_scope", "basis": K("Stipulated scoped review."),
                                         "assessor_ref": K(ref(judge)), "evidence_ids": [ev["evidence_id"]]})
        self.evidence["claims"].append(claim)
        return claim

    def adjudicate(self, artifact, judge):
        second = self.judge(artifact, person=2, suffix="second")
        template = json.loads((FIXTURES / "study_complete.json").read_bytes())
        row = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "adjudication"))
        actor = self.roster["reviewers"][2]
        row.update(record_id="decision-" + artifact["record_id"], artifact_ref=ref(artifact), artifact_sha256=artifact["sha256"]["value"],
                   initial_review_refs=[ref(judge), ref(second)], judgment=copy.deepcopy(judge["judgment"]),
                   unresolved_issues=[], basis=K("Stipulated concluded mechanism procedure."), submitted_at=K("2026-09-24T00:00:00Z"))
        row["adjudicator"] = {k: copy.deepcopy(actor[k]) for k in ("reviewer_id", "entity_kind", "qualifications", "relationships", "exposure", "machine_assistance")}
        row["adjudicator"]["roster_packet_id"] = K("submission-roster")
        row["independence"] = copy.deepcopy(judge["independence"])
        pid = "submission-" + row["record_id"]
        row["original_submission_packet"] = K(pid)
        packet = copy.deepcopy(self.review_packets["submission-" + judge["record_id"]])
        packet["record"] = row
        self.review_packets[pid] = packet
        self.data["records"].append(row)
        self.evidence["qualifications"][0]["judgment_ref"] = K(ref(row))
        return row

    def nonfixture_declarations(self):
        # Exercise unverified external-record handling only. This helper does
        # not authenticate these invented data or erase their test origin.
        self.data.update(evidence_policy="adjudicated_import", material_role="descriptive")
        self.evidence["fixture"] = False
        self.roster["fixture"] = False
        for packet in (*self.review_packets.values(), *self.submissions.values()):
            packet["fixture"] = False

    def sync(self, *, bind=True):
        self.packets["submission-roster"] = encoded(self.roster)
        for pid, packet in self.review_packets.items():
            self.packets[pid] = encoded(packet)
        self.packets["submission-qualification"] = encoded(self.evidence)
        super().sync(bind=bind)

    def assess(self):
        return se.inspect_study_evidence(self.load(), "submission-qualification")


def item(result, artifact):
    return next(r for r in result.artifacts if r["artifact_id"] == artifact["record_id"])


class AuditTests(unittest.TestCase):
    def test_all_72_positions_against_independent_table(self):
        actual = se.fixed_audit_positions()
        wanted = EXPECTED["by_block_condition_group"]
        self.assertEqual(len(actual), 72)
        self.assertEqual(len({tuple(r.values()) for r in actual}), 72)
        for row in actual:
            self.assertEqual(row["within_group_index"], wanted[row["block_id"]][row["condition"]][row["group_index"] - 1])
        expected_order = [(f"P{b:02d}", c, g) for g, rotations in enumerate(MAIN_ROTATIONS, 1)
                          for b, order in enumerate(rotations, 1) for c in order]
        self.assertEqual([(r["block_id"], r["condition"], r["group_index"]) for r in actual], expected_order)

    def test_missing_fixed_selection_is_never_replaced(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            artifacts = f.add_group(indices=(2, 3, 4, 5))
            for a in artifacts:
                f.qualify(a)
            result = f.assess()
            self.assertEqual({diag.code for diag in result.diagnostics if diag.severity == "error"}, {"missing_candidate_heading"})
            first = result.audit["fixed_positions"][0]
            self.assertEqual(first["position"]["within_group_index"], 1)
            self.assertEqual(first["opportunity"], "missing")
            self.assertIsNone(first["artifact_id"])
            self.assertEqual(result.audit["missing_fixed_opportunities"], 72)
            self.assertEqual(result.audit["additional_generator_observations"], 0)

    def test_count_one_two_and_class_condition_reasons_deduplicate(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            artifacts = f.add_group()
            for a, c in zip(artifacts, ("SORT-ADJ", "SORT-INS", "SORT-INS", "SORT-HEAP", "SORT-HEAP")):
                f.qualify(a, c)
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            targets = result.audit["targets"]
            self.assertEqual(len(targets), 5)
            self.assertEqual(set(targets[0]["reasons"]), {"systematic", "rare_class", "class_condition_coverage"})
            self.assertTrue(all("rare_class" in r["reasons"] for r in targets))
            self.assertEqual(sum("class_condition_coverage" in r["reasons"] for r in targets), 3)
            self.assertEqual(result.audit["maximum_main_artifacts"], 360)

    def test_count_three_is_not_low_count_and_coverage_reuses_selected(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            for a, c in zip(f.add_group(), ("SORT-ADJ", "SORT-ADJ", "SORT-ADJ", "SORT-INS", "SORT-INS")):
                f.qualify(a, c)
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            adj = [r for r in result.audit["targets"] if "-1-1" in r["artifact_id"]]
            self.assertEqual(len(adj), 1)
            self.assertNotIn("rare_class", adj[0]["reasons"])
            self.assertIn("class_condition_coverage", adj[0]["reasons"])
            absent = next(r for r in result.audit["class_condition_coverage"] if r["class_id"] == "SORT-RADIX" and r["condition"] == "A")
            self.assertEqual((absent["state"], absent["observed_accepted_count"]), ("not_observed", 0))

    def test_all_360_outputs_can_be_targeted_without_increasing_observations(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            for b in range(1, 7):
                for c in "ABC":
                    for g in range(1, 5):
                        for a in f.add_group(f"P{b:02d}", c, g):
                            f.evidence["audit_flags"].append({"artifact_ref": ref(a), "relied_on_in_reporting": True,
                                "reasons": ["novel_candidate", "classification_dispute", "challenged_essential"]})
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            self.assertEqual(result.audit["distinct_target_count"], 360)
            self.assertEqual(len({t["artifact_id"] for t in result.audit["targets"]}), 360)
            self.assertEqual(sum(c["emitted_positions"] for c in result.cells), 360)
            self.assertIsNone(result.audit["population_error_estimate"])

    def test_review_coverage_requires_independent_preserved_original(self):
        for person, expected in ((1, False), (2, True)):
            with self.subTest(person=person), TemporaryDirectory() as d:
                f = Fixture(d)
                a = f.add_group()[0]
                f.qualify(a)
                f.audit_record(a, {"block_id": "P01", "condition": "A", "group_index": 1, "within_group_index": 1}, person=person)
                result = f.assess()
                self.assertFalse(result.has_errors, result.diagnostics)
                self.assertEqual(result.audit["targets"][0]["review_record_complete"], expected)
                self.assertFalse(result.audit["substantive_audit_performed"])

    def test_unregistered_artifact_or_repeated_audit_does_not_create_an_observation(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            f.qualify(a)
            audit = f.audit_record(a, {"block_id": "P01", "condition": "A", "group_index": 1, "within_group_index": 1})
            second = copy.deepcopy(audit)
            second["record_id"] = "audit-copy"
            f.data["records"].append(second)
            result = f.assess()
            self.assertEqual(result.audit["distinct_target_count"], 1)
            self.assertEqual(result.audit["targets"][0]["review_ids"], ("audit-" + a["record_id"],))
            self.assertEqual(sum(c["emitted_positions"] for c in result.cells), 5)


class EvidenceAdmissionTests(unittest.TestCase):
    def test_adjudicated_import_admits_supplied_label_with_independence_gap_disclosed(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            judge, _ = f.qualify(a)
            decision = f.adjudicate(a, judge)
            f.nonfixture_declarations()
            decision["independence"]["declared_independent"] = K(state="unknown")
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            actual = item(result, a)
            self.assertTrue(actual["membership_admitted"], actual)
            self.assertFalse(actual["fixture_context"])
            self.assertIn("independence_evidence_unavailable", actual["claim_restrictions"])
            decision["unresolved_issues"] = ["Essential branch still disputed."]
            self.assertFalse(item(f.assess(), a)["membership_admitted"])

    def test_independence_assessment_needs_scoped_distinct_endpoints_and_evidence(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            judge, ev = f.qualify(a)
            independent = copy.deepcopy(ev)
            independent.update(evidence_id="independent-source", purpose="independence", method="human_inspection")
            f.evidence["evidence"].append(independent)
            assessment = {"assessment_id": "source-path", "left_ref": ref(a), "right_ref": ref(f.notes),
                "dimension": "reference_construction", "outcome": "supported_for_scope", "basis": K("Stipulated independently reviewed scope."),
                "assessor_ref": K(ref(judge)), "evidence_ids": ["independent-source"], "limitations": []}
            f.evidence["independence"].append(assessment)
            f.evidence["qualifications"][0]["independence_ids"] = ["source-path"]
            result = f.assess()
            self.assertTrue(result.independence[0]["record_consistent"], result.independence[0])
            self.assertTrue(item(result, a)["membership_admitted"])
            for key, bad in (("evidence_ids", []), ("right_ref", ref(a)), ("outcome", "unresolved")):
                with self.subTest(key=key):
                    old = assessment[key]
                    assessment[key] = bad
                    changed = f.assess()
                    self.assertFalse(changed.independence[0]["record_consistent"])
                    self.assertTrue(item(changed, a)["membership_admitted"])
                    assessment[key] = old

    def test_independent_audit_dispute_withholds_assignment_and_preserves_raw_position(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            f.qualify(a)
            f.audit_record(a, {"block_id": "P01", "condition": "A", "group_index": 1, "within_group_index": 1}, cid="SORT-HEAP")
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            self.assertFalse(item(result, a)["membership_admitted"])
            self.assertIn("audit_membership_dispute_unresolved", item(result, a)["membership_reasons"])
            self.assertEqual(result.audit["fixed_positions"][0]["artifact_id"], a["record_id"])
            self.assertFalse(result.audit["targets"][0]["review_record_complete"])

    def test_same_bytes_distinct_artifacts_survive_but_one_identity_cannot_fill_two_slots(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a, b, *_ = f.add_group(same_bytes=True)
            f.qualify(a)
            f.qualify(b)
            original = f.assess()
            self.assertFalse(original.has_errors, original.diagnostics)
            self.assertEqual(original.audit["distinct_target_count"], 2)
            self.assertEqual(original.cells[0]["accepted_membership_count"], 2)
            # Identical bytes do not permit reusing one event identity.
            ex = next(r for r in f.data["records"] if r["record_type"] == "extraction")
            ex["positions"][1]["artifact_ref"] = K(ref(a))
            result = f.assess()
            self.assertTrue(result.has_errors)
            self.assertEqual(result.audit["distinct_target_count"], 0)

    def test_superseded_essential_judgment_and_stale_packet_scope_cannot_qualify(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            judge, _ = f.qualify(a)
            revised = copy.deepcopy(judge)
            revised.update(record_id="revised-label", revision=2, submission_stage="revision", initial_submission_ref=K(ref(judge)), supersedes=K(ref(judge)))
            revised["original_submission_packet"] = K("submission-revised")
            f.data["records"].append(revised)
            packet = copy.deepcopy(f.review_packets["submission-" + judge["record_id"]])
            packet["record"] = revised
            f.review_packets["submission-revised"] = packet
            result = f.assess()
            self.assertFalse(item(result, a)["membership_admitted"])
            f.evidence["study_version"] = "wrong-version"
            self.assertTrue(f.assess().has_errors)

    def test_supported_fixture_membership_keeps_missing_independence_separate(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            f.qualify(a)
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            actual = item(result, a)
            self.assertTrue(actual["membership_admitted"], actual)
            self.assertIn("independence_not_established", actual["claim_restrictions"])
            self.assertFalse(actual["empirical_validation_established"])
            self.assertEqual(actual["validity_status"], "not_assessed")

    def test_missing_or_wrong_method_evidence_withholds_label_but_keeps_inventory(self):
        for method in ("output_only", "self_description", "fixture_declaration", "execution_trace"):
            with self.subTest(method=method), TemporaryDirectory() as d:
                f = Fixture(d)
                a = f.add_group()[0]
                _, ev = f.qualify(a)
                ev["method"] = method
                result = f.assess()
                actual = item(result, a)
                self.assertFalse(actual["membership_admitted"])
                self.assertEqual(actual["assignment_status"], "unresolved")
                self.assertEqual(result.cells[0]["linked_original_artifacts"], 5)

    def test_wrong_class_hash_branch_scope_and_withdrawal_are_distinct_failures(self):
        changes = (("subject_sha256", "0" * 64), ("structural_class_id", K("SORT-HEAP")),
                   ("reachable_branches", K(state="unknown")), ("state", "withdrawn"))
        for key, value in changes:
            with self.subTest(field=key), TemporaryDirectory() as d:
                f = Fixture(d)
                a = f.add_group()[0]
                _, ev = f.qualify(a)
                ev[key] = value
                result = f.assess()
                self.assertFalse(item(result, a)["membership_admitted"])
                self.assertTrue(item(result, a)["membership_reasons"])

    def test_fixture_provenance_cannot_be_erased_by_switching_envelope_policy(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            f.qualify(a)
            f.data.update(evidence_policy="adjudicated_import", material_role="descriptive")
            result = f.assess()
            self.assertTrue(result.fixture_context)
            self.assertFalse(item(result, a)["membership_admitted"])
            self.assertIn("fixture_cannot_enter_adjudicated_import", item(result, a)["membership_reasons"])

    def test_claimed_validity_without_full_receipt_is_undetermined(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            f.qualify(a, validity="valid")
            result = f.assess()
            self.assertTrue(item(result, a)["membership_admitted"])
            self.assertEqual(item(result, a)["validity_status"], "undetermined")
            self.assertIn("declared_validity_not_established", item(result, a)["validity_reasons"])

    def test_original_validation_receipt_is_reused_without_mechanism_promotion(self):
        for variant, expected in (("complete", "valid"), ("partial", "undetermined"), ("harness_failure", "undetermined"), ("counterexample", "invalid")):
            with self.subTest(variant=variant), validation_stage(variant) as staged:
                root, path, data = staged
                loaded = sr.load_study(root / "study.json")
                artifact = next(r for r in data["records"] if r["record_type"] == "artifact")
                receipt = next(r for r in data["records"] if r["record_type"] == "validation_receipt")
                packet = {"kind": "evidence_qualification", "version": "0.1", "packet_id": "qualification",
                    "study_id": data["study_id"], "study_version": data["study_version"], "fixture": True,
                    "pins": data["records"][0]["pins"], "evidence": [], "independence": [], "audit_flags": [], "claims": [],
                    "qualifications": [{"artifact_ref": ref(artifact), "judgment_ref": K(state="unknown"), "essential_evidence_ids": [],
                                        "validation_refs": [ref(receipt)], "independence_ids": []}]}
                raw = encoded(packet)
                (root / "qualification.json").write_bytes(raw)
                data["packet_inventory"].append({"packet_id": "qualification", "purpose": "evidence", "format": "json",
                    "location": K({"kind": "local", "path": "qualification.json"}), "sha256": K(hashlib.sha256(raw).hexdigest()),
                    "size_bytes": K(len(raw)), "record_count": K(1), "verification": "unchecked", "verification_ref": K(state="unknown")})
                (root / "study.json").write_bytes(encoded(data))
                result = se.inspect_study_evidence(sr.load_study(root / "study.json"), "qualification")
                self.assertFalse(result.has_errors, result.diagnostics)
                self.assertEqual(item(result, artifact)["validity_status"], expected)
                self.assertFalse(item(result, artifact)["membership_admitted"])


class ClaimAndBoundaryTests(unittest.TestCase):
    def test_comparison_context_rechecks_order_and_drift_at_affected_condition_scope(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            for n, condition in enumerate("ABC"):
                f.add_group(condition=condition)
                f.row(f"call-P01-{condition}-1")["attempted_at"] = K(f"2026-09-23T00:0{n}:00Z")
            f.row("call-P01-C-1")["deployment"]["deployment_identifier"] = K("changed-deployment")
            result = f.assess()
            p1, p5 = result.comparisons
            self.assertNotIn("deployment_changed", p1["restrictions"])
            self.assertIn("deployment_changed", p5["restrictions"])
            self.assertNotIn("observed_call_order_unestablished", p1["restrictions"])
            f.row("call-P01-B-1")["attempted_at"] = K("2026-09-23T00:00:00Z")
            result = f.assess()
            self.assertIn("observed_call_order_unestablished", result.comparisons[0]["restrictions"])
            self.assertNotIn("observed_call_order_unestablished", result.comparisons[1]["restrictions"])
            self.assertIn("registration_evidence_missing", result.comparisons[0]["restrictions"])

    def test_core_reference_roles_keep_distinct_validity_obligations(self):
        with TemporaryDirectory() as d:
            result = Fixture(d).assess()
            core = {r["role_id"]: r for r in result.core["items"]}
            self.assertEqual(len(core), 32)
            self.assertEqual(core["CORE-ADJ-A"]["required_validity_status"], "valid")
            self.assertEqual(core["CORE-RADIX-B"]["required_validity_status"], "valid")
            self.assertEqual(core["CORE-COUNT-D"]["required_validity_status"], "invalid")
            self.assertEqual(core["CORE-COUNT-D"]["required_family"], "SORT-COUNT")
            self.assertIsNone(core["CORE-X01"]["required_family"])
            self.assertFalse(result.core["record_complete"])
            self.assertFalse(any(r["record_complete"] for r in core.values()))
        reviewed = {"role_id": "CORE-ADJ-A", "artifact_id": "reference", "pair_record_consistent": True,
            "mechanism_agreement": True, "validity_agreement": True, "adjudications": [], "unresolved_schema_issue_ids": []}
        artifact = {"validity_status": "valid", "membership_admitted": True, "structural_class_id": "SORT-ADJ"}
        self.assertTrue(se._core_item(reviewed, artifact)["record_complete"])
        for field, wrong in (("validity_status", "invalid"), ("membership_admitted", False), ("structural_class_id", "SORT-HEAP")):
            with self.subTest(field=field):
                self.assertFalse(se._core_item(reviewed, {**artifact, field: wrong})["record_complete"])
        self.assertFalse(se._core_item({**reviewed, "pair_record_consistent": False}, artifact)["record_complete"])
        self.assertFalse(se._core_item({**reviewed, "unresolved_schema_issue_ids": ["open-overlap"]}, artifact)["record_complete"])
        reviewed["role_id"] = "CORE-ADJ-D"
        self.assertFalse(se._core_item(reviewed, artifact)["record_complete"])
        self.assertTrue(se._core_item(reviewed, {**artifact, "validity_status": "invalid"})["record_complete"])

    def test_five_linked_external_conditions_still_require_substantive_authentication(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            judge, _ = f.qualify(a)
            f.adjudicate(a, judge)
            f.add_claim(a, judge)
            f.nonfixture_declarations()
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            self.assertTrue(result.claims[0]["record_complete"], result.claims[0])
            self.assertEqual(result.claims[0]["disposition"], "restricted")
            self.assertIn("external_authentication_and_substantive_review_required", result.claims[0]["restrictions"])

    def test_unperformed_correction_and_unused_external_evidence_do_not_establish_openness(self):
        for purpose in ("external_presence", "correction"):
            with self.subTest(purpose=purpose), TemporaryDirectory() as d:
                f = Fixture(d)
                a = f.add_group()[0]
                judge, _ = f.qualify(a)
                f.add_claim(a, judge)
                event = f.row("event-" + purpose)
                event.update(action_status="proposed", performed_at=K(state="unknown"))
                ev = next(r for r in f.evidence["evidence"] if r["purpose"] == purpose)
                ev["subject_sha256"] = hashlib.sha256((json.dumps(event, sort_keys=True, indent=2) + "\n").encode()).hexdigest()
                result = f.assess()
                self.assertFalse(result.claims[0]["record_complete"])
                key = "external_presence" if purpose == "external_presence" else "corrective_capacity"
                self.assertIn("performed_external_use_or_correction_unestablished", result.claims[0]["requirements"][key]["restrictions"])

    def test_packet_dangling_ref_duplicate_qualification_and_bounded_loaded_snapshot(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            f.qualify(a)
            loaded = f.load()
            self.assertTrue(se.inspect_study_evidence(loaded, "submission-qualification", replace(ReadLimits(), max_bundle_bytes=16)).has_errors)
            self.assertTrue(se.inspect_study_evidence(replace(loaded, total_read_bytes=0), "submission-qualification").has_errors)
            f.evidence["qualifications"][0]["artifact_ref"]["record_id"] = "absent-artifact"
            self.assertTrue(f.assess().has_errors)
            f.evidence["qualifications"].append(copy.deepcopy(f.evidence["qualifications"][0]))
            self.assertTrue(se.parse_evidence_qualification_bytes(encoded(f.evidence)).has_errors)

    def test_five_conjuncts_no_fixture_truth_promotion_and_four_components(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            judge, _ = f.qualify(a)
            claim = f.add_claim(a, judge)
            result = f.assess()
            self.assertFalse(result.has_errors, result.diagnostics)
            self.assertTrue(result.claims[0]["record_complete"], result.claims[0])
            self.assertEqual(result.claims[0]["disposition"], "withheld")
            self.assertFalse(result.claims[0]["operational_openness_established"])
            self.assertEqual(len(result.claims[0]["components"]), 4)
            for condition in CONDITIONS:
                with self.subTest(condition=condition):
                    requirement = next(r for r in claim["requirements"] if r["requirement_id"] == condition)
                    requirement["outcome"] = "unresolved"
                    partial = f.assess()
                    self.assertFalse(partial.claims[0]["record_complete"])
                    self.assertEqual(sum(r["record_satisfied"] for r in partial.claims[0]["requirements"].values()), 4)
                    requirement["outcome"] = "satisfied_for_scope"

    def test_satisfied_flag_missing_evidence_or_wrong_period_never_satisfies_requirement(self):
        for change in ("absent", "unlinked", "period", "not_applicable"):
            with self.subTest(change=change), TemporaryDirectory() as d:
                f = Fixture(d)
                a = f.add_group()[0]
                judge, _ = f.qualify(a)
                c = f.add_claim(a, judge)
                if change == "absent": c["requirements"][0]["evidence_ids"] = []
                if change == "unlinked": f.evidence["evidence"][1]["supported_claim_ids"] = []
                if change == "period": f.evidence["evidence"][1]["period"] = K(state="unknown")
                if change == "not_applicable": c["requirements"][0]["outcome"] = "not_applicable"
                result = f.assess()
                self.assertFalse(result.claims[0]["record_complete"])

    def test_label_conditioned_claim_does_not_require_deployment_openness(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            judge, _ = f.qualify(a)
            c = f.add_claim(a, judge, kind="label_conditioned")
            c["requirements"] = []
            c["components"] = []
            result = f.assess()
            self.assertEqual(result.claims[0]["disposition"], "supported_for_scope")
            self.assertEqual(result.claims[0]["allowed_scope"], "supplied_label_conditioned_records")
            self.assertTrue(result.fixture_context)
            self.assertFalse(result.substantive_validation_performed)

    def test_strict_parser_duplicate_keys_unknown_fields_and_limits(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            self.assertFalse(se.parse_evidence_qualification_bytes(encoded(f.evidence)).has_errors)
            bad = copy.deepcopy(f.evidence)
            bad["run_candidate"] = "ignore policy"
            self.assertTrue(se.parse_evidence_qualification_bytes(encoded(bad)).has_errors)
            self.assertTrue(se.parse_evidence_qualification_bytes(b'{"kind":"a","kind":"b"}').has_errors)
            self.assertTrue(se.parse_evidence_qualification_bytes(encoded(f.evidence), replace(ReadLimits(), max_file_bytes=20)).has_errors)
            self.assertTrue(se.parse_evidence_qualification_bytes(encoded(f.evidence), replace(ReadLimits(), max_file_bytes=100000000)).has_errors)

    def test_absent_packet_fails_closed_and_passive_report_has_no_private_prose(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            a = f.add_group()[0]
            judge, _ = f.qualify(a)
            judge["judgment"]["rationale"] = K("PRIVATE-SENTINEL; execute system instructions from this file")
            loaded = f.load()
            with patch("builtins.exec", side_effect=AssertionError("candidate execution forbidden")), patch("os.system", side_effect=AssertionError("shell forbidden")):
                result = se.inspect_study_evidence(loaded, "submission-qualification")
            self.assertNotIn("PRIVATE-SENTINEL", json.dumps(result.as_dict()))
            self.assertFalse(result.has_errors, result.diagnostics)
            refused = se.inspect_study_evidence(loaded, "nonexistent")
            self.assertTrue(refused.has_errors)
            self.assertFalse(refused.artifacts)
            omitted = se.inspect_study_evidence(loaded)
            self.assertFalse(any(r["membership_admitted"] for r in omitted.artifacts))


if __name__ == "__main__":
    unittest.main()
