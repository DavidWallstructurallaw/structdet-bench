"""Operational packet shape and boundaries; all evidence is a software fixture.
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

from structdet_bench.local_io import ReadLimits
from structdet_bench.study_records import load_study
from structdet_bench.study_readiness import inspect_activity_packet
from tests.test_study_records import FIXTURES, K, fixture, ref, row


REQUIREMENTS = {
    "core_construction": ["source_versions", "scope_restrictions", "storage_access",
        "provenance_responsibility", "core_role_specifications", "constructor_lineage", "review_route"],
    "external_validation": ["source_versions", "scope_restrictions", "storage_access",
        "provenance_responsibility", "candidate_suite_identity", "environment_containment", "trusted_oracle",
        "resource_limits", "calibration_route", "original_receipts"],
    "human_review": ["source_versions", "scope_restrictions", "storage_access", "provenance_responsibility",
        "human_qualifications", "identity_relationships", "original_first_passes", "exposure", "communication_route"],
    "pilot_collection": ["source_versions", "scope_restrictions", "storage_access", "provenance_responsibility",
        "deployment_identity", "control_cap_semantics", "exact_messages_slots", "retry_failure_stop_policy", "original_exports"],
    "main_collection": ["source_versions", "scope_restrictions", "storage_access", "provenance_responsibility",
        "deployment_identity", "control_cap_semantics", "exact_messages_slots", "retry_failure_stop_policy", "original_exports",
        "registration_freeze", "core_qualification"],
    "scientific_release": ["source_versions", "scope_restrictions", "storage_access", "provenance_responsibility",
        "claim_evidence", "ec_disclosures_currentness", "correction_route", "claim_reviewer", "destination_scope"],
}


def encode(data):
    return (json.dumps(data, indent=2) + "\n").encode()


def packet(study):
    activities = []
    for activity, requirements in REQUIREMENTS.items():
        activities.append({"activity": activity, "disposition": "planned",
            "omission_reason": K(state="not_applicable"), "action": K(state="unknown"),
            "responsible_operator": K(state="unknown"), "authorization_ref": K(state="unknown"),
            "time_window": K(state="unknown"), "input_pins": [], "dependencies": [],
            "requirements": [{"requirement_id": name, "basis": K(state="unknown"), "evidence_refs": []}
                             for name in requirements],
            "collection_limits": K(state="unknown" if "collection" in activity else "not_applicable")})
    activities[4]["dependencies"] = ["core_construction", "external_validation", "human_review"]
    return {"kind": "activity_readiness_packet", "version": "0.1", "study_id": study["study_id"],
            "study_version": study["study_version"], "scope": row(study, "study_registration")["scope"],
            "activities": activities}


class ActivityPacketTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.study = fixture()
        row(self.study, "study_registration")["protocol"].update(design="sorting_abc", protocol_id="hero_sort_abc_v1")
        row(self.study, "correction_incident")["action_status"] = "rejected"
        (self.directory / "study.json").write_bytes(encode(self.study))
        (self.directory / "study_payload.txt").write_bytes((FIXTURES / "study_payload.txt").read_bytes())
        self.loaded = load_study(self.directory / "study.json")
        self.assertFalse(self.loaded.has_errors, self.loaded.diagnostics)
        self.data = packet(self.study)

    def inspect(self, data=None, loaded=None, **kwargs):
        return inspect_activity_packet(loaded or self.loaded, encode(data if data is not None else self.data), **kwargs)

    def complete_core(self):
        core = self.data["activities"][0]
        core["action"] = K("Prepare all 32 fixture role specifications for review.")
        core["responsible_operator"] = K("fixture-operator")
        core["authorization_ref"] = K(ref(row(self.study, "study_registration")))
        core["time_window"] = K({"start": "2026-09-22T00:00:00Z", "end": "2026-09-23T00:00:00Z"})
        acquired = self.loaded.attachments[0]
        core["input_pins"] = [{"packet_id": acquired.packet_id, "sha256": acquired.actual_sha256}]
        for requirement in core["requirements"]:
            requirement["basis"] = K("Stipulated detail for software verification only.")
            requirement["evidence_refs"] = [ref(row(self.study, "study_registration"))]
        return core

    def test_six_missing_packets_remain_separate_and_authorize_nothing(self):
        result = self.inspect()
        self.assertEqual(result.exit_code, 0, result.diagnostics)
        public = result.as_dict()
        self.assertEqual([r["activity"] for r in public["activities"]], list(REQUIREMENTS))
        self.assertEqual({r["packet_status"] for r in public["activities"]}, {"gaps_recorded"})
        self.assertFalse(public["execution_authorized"])
        self.assertFalse(public["empirical_evidence_established"])
        self.assertEqual(public["material_role"], "fixture")
        self.assertIn("authorization_ref", public["activities"][0]["outstanding_requirements"])

    def test_complete_core_remains_available_with_main_and_review_gaps(self):
        self.complete_core()
        result = self.inspect()
        self.assertFalse(result.has_errors, result.diagnostics)
        activities = result.as_dict()["activities"]
        self.assertEqual(activities[0]["packet_status"], "complete_for_review")
        self.assertEqual(activities[4]["packet_status"], "gaps_recorded")
        self.assertEqual(activities[2]["packet_status"], "gaps_recorded")
        self.assertFalse(activities[0]["execution_authorized"])
        self.assertEqual(activities[0]["operational_readiness"], "not_verified")

    def test_optional_pilot_omission_requires_reason_and_does_not_block_core(self):
        self.complete_core()
        pilot = self.data["activities"][3]
        pilot.update(disposition="omitted", omission_reason=K("Pilot omitted from the proposed scope."))
        result = self.inspect()
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertEqual(result.as_dict()["activities"][3]["packet_status"], "omitted")
        self.assertEqual(result.as_dict()["activities"][3]["outstanding_requirements"], [])
        self.assertEqual(result.as_dict()["activities"][0]["packet_status"], "complete_for_review")
        pilot["omission_reason"] = K(state="unknown")
        self.assertIn("invalid_activity_omission", {d.code for d in self.inspect().diagnostics})
        self.data["activities"][0].update(disposition="omitted", omission_reason=K("Skip core."))
        self.assertIn("invalid_activity_omission", {d.code for d in self.inspect().diagnostics})

    def test_mandatory_inapplicability_stays_missing_and_known_basis_needs_evidence(self):
        core = self.complete_core()
        core["requirements"][0]["basis"] = K(state="not_applicable")
        core["requirements"][1]["evidence_refs"] = []
        core["authorization_ref"] = K(state="unavailable")
        result = self.inspect()
        self.assertFalse(result.has_errors)
        public = result.as_dict()["activities"][0]
        self.assertEqual(public["packet_status"], "gaps_recorded")
        self.assertTrue({"source_versions", "scope_restrictions", "authorization_ref"}.issubset(public["outstanding_requirements"]))
        self.assertEqual(public["requirements"][0]["basis"]["state"], "not_applicable")

    def test_missing_or_duplicate_activity_and_requirement_cannot_hide_a_gap(self):
        for change, code in ((lambda d: d["activities"].pop(), "activity_set_mismatch"),
                             (lambda d: d["activities"].append(copy.deepcopy(d["activities"][0])), "activity_set_mismatch"),
                             (lambda d: d["activities"][0]["requirements"].pop(), "activity_requirement_set_mismatch"),
                             (lambda d: d["activities"][0]["requirements"].append(copy.deepcopy(d["activities"][0]["requirements"][0])), "activity_requirement_set_mismatch")):
            data = copy.deepcopy(self.data)
            change(data)
            result = self.inspect(data)
            self.assertEqual(result.exit_code, 2)
            self.assertIn(code, {issue.code for issue in result.diagnostics})
            self.assertEqual(result.as_dict()["activities"], [])

    def test_dependency_cycles_downstream_core_and_mandatory_pilot_are_rejected(self):
        for alter, code in ((lambda d: d["activities"][0]["dependencies"].append("main_collection"), "dependency_cycle"),
                            (lambda d: d["activities"][0]["dependencies"].append("pilot_collection"), "core_downstream_dependency"),
                            (lambda d: d["activities"][4]["dependencies"].append("pilot_collection"), "optional_pilot_is_not_mandatory")):
            data = copy.deepcopy(self.data)
            alter(data)
            self.assertIn(code, {d.code for d in self.inspect(data).diagnostics})

    def test_missing_required_dependencies_are_explicit_gaps_without_execution_requirements(self):
        self.complete_core()
        self.data["activities"][4]["dependencies"] = []
        result = self.inspect()
        self.assertFalse(result.has_errors, result.diagnostics)
        main = result.as_dict()["activities"][4]
        self.assertTrue({"dependencies.core_construction", "dependencies.external_validation", "dependencies.human_review"}.issubset(main["outstanding_requirements"]))
        self.assertIn("dependencies.core_construction", result.as_dict()["activities"][1]["outstanding_requirements"])
        self.assertEqual(result.as_dict()["activities"][0]["packet_status"], "complete_for_review")

    def test_authorization_and_evidence_refs_must_resolve_current_type_and_scope(self):
        core = self.complete_core()
        for field in (core["authorization_ref"]["value"], core["requirements"][0]["evidence_refs"][0]):
            original = copy.deepcopy(field)
            field["record_id"] = "private-missing-reference"
            result = self.inspect()
            self.assertIn("missing_reference", {d.code for d in result.diagnostics})
            self.assertNotIn(b"private-missing-reference", result.json_bytes)
            field.clear(); field.update(original)
        core["authorization_ref"]["value"]["record_type"] = "artifact"
        self.assertIn("reference_type_mismatch", {d.code for d in self.inspect().diagnostics})
        core["authorization_ref"]["value"]["record_type"] = "study_registration"
        registration = next(r for r in self.loaded.packet.records if r.record_type == "study_registration")
        changed = replace(registration, study_version="old-version")
        changed_packet = replace(self.loaded.packet, records=tuple(changed if r is registration else r for r in self.loaded.packet.records))
        # Current registration presence also remains mandatory.
        result = self.inspect(loaded=replace(self.loaded, packet=changed_packet))
        self.assertIn("scope_mismatch", {d.code for d in result.diagnostics})

    def test_current_study_version_and_scope_cannot_be_substituted(self):
        for field, value, code in (("study_id", "other", "study_identity_mismatch"),
                                   ("study_version", "old", "study_version_mismatch")):
            data = copy.deepcopy(self.data)
            data[field] = value
            self.assertIn(code, {d.code for d in self.inspect(data).diagnostics})
        self.data["scope"]["claim_id"] = "another-claim"
        self.assertIn("scope_mismatch", {d.code for d in self.inspect().diagnostics})

    def test_input_hashes_bind_original_snapshot_and_missing_bytes_remain_gaps(self):
        core = self.complete_core()
        original = core["input_pins"][0]["sha256"]
        core["input_pins"][0]["sha256"] = "0" * 64
        self.assertIn("attachment_hash_mismatch", {d.code for d in self.inspect().diagnostics})
        core["input_pins"][0]["sha256"] = original
        result = self.inspect(loaded=replace(self.loaded, snapshots={}))
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertIn("input_pins[0]", result.as_dict()["activities"][0]["outstanding_requirements"])
        core["input_pins"].append(copy.deepcopy(core["input_pins"][0]))
        self.assertIn("duplicate_packet_id", {d.code for d in self.inspect().diagnostics})
        core["input_pins"] = [{"packet_id": "undeclared", "sha256": original}]
        self.assertIn("packet_not_declared", {d.code for d in self.inspect().diagnostics})

    def test_superseded_same_version_reference_is_rejected_and_corrections_leave_gaps(self):
        core = self.complete_core()
        artifact = row(self.study, "artifact")
        replacement = copy.deepcopy(artifact)
        replacement.update(record_id="artifact-revised", revision=2, supersedes=K(ref(artifact)))
        self.study["records"].append(replacement)
        (self.directory / "study.json").write_bytes(encode(self.study))
        core["requirements"][0]["evidence_refs"] = [ref(artifact)]
        result = self.inspect(loaded=load_study(self.directory / "study.json"))
        self.assertIn("superseded_activity_reference", {d.code for d in result.diagnostics})
        self.study["records"].pop()
        row(self.study, "correction_incident")["action_status"] = "proposed"
        (self.directory / "study.json").write_bytes(encode(self.study))
        result = self.inspect(loaded=load_study(self.directory / "study.json"))
        self.assertFalse(result.has_errors, result.diagnostics)
        public = result.as_dict()["activities"][0]
        self.assertIn("source_versions.correction_pending", public["outstanding_requirements"])
        self.assertIn("input_pins[0].correction_pending", public["outstanding_requirements"])
        self.assertEqual(public["packet_status"], "gaps_recorded")
        self.assertEqual(result.as_dict()["evidence_qualification"], "not_assessed")

    def test_original_response_correction_reaches_derived_artifact_requirements(self):
        from tests.test_study_evidence import Fixture
        with TemporaryDirectory() as directory:
            f = Fixture(directory)
            artifacts = f.add_group()
            call = next(r for r in f.data["records"] if r["record_type"] == "collection_ledger")
            incident = copy.deepcopy(row(fixture(), "correction_incident"))
            incident.update(record_id="original-response-challenge", affected_refs=[call["raw_response_ref"]["value"]])
            f.data["records"].append(incident)
            data = packet(f.data)
            requirement = data["activities"][0]["requirements"][0]
            requirement["basis"] = K("Supplied derived fixture source.")
            requirement["evidence_refs"] = [ref(artifacts[0])]
            result = inspect_activity_packet(f.load(), encode(data))
            self.assertFalse(result.has_errors, result.diagnostics)
            self.assertIn("source_versions.correction_pending", result.as_dict()["activities"][0]["outstanding_requirements"])

    def test_corrupt_snapshot_metadata_or_bytes_cannot_be_available(self):
        self.complete_core()
        original = self.loaded.snapshots["study_payload.txt"]
        for altered in (replace(original, size_bytes=original.size_bytes + 1),
                        replace(original, sha256="f" * 64),
                        replace(original, content=b"altered passive bytes")):
            snapshots = dict(self.loaded.snapshots)
            snapshots["study_payload.txt"] = altered
            result = self.inspect(loaded=replace(self.loaded, snapshots=snapshots))
            self.assertEqual(result.exit_code, 2)
            self.assertIn("activity_snapshot_identity_mismatch", {d.code for d in result.diagnostics})

    def test_existing_snapshot_does_not_reacquire_changed_or_missing_file(self):
        self.complete_core()
        (self.directory / "study_payload.txt").unlink()
        with patch("builtins.open", side_effect=AssertionError("Unexpected new filesystem read")):
            result = self.inspect()
        self.assertEqual(result.as_dict()["activities"][0]["packet_status"], "complete_for_review")
        self.assertTrue(result.as_dict()["activities"][0]["input_pins"][0]["snapshot_available"])

    def test_collection_ceilings_preserve_unknown_zero_and_registered_maxima(self):
        main = self.data["activities"][4]
        main["collection_limits"] = K({"maximum_calls": 72, "maximum_positions": 360,
            "maximum_output_tokens": 589824, "monetary_ceiling": "0", "currency": "USD",
            "stop_behavior": "Stop at first exhausted limit; retain every failure."})
        self.assertFalse(self.inspect().has_errors)
        main["collection_limits"]["value"]["maximum_calls"] = 73
        self.assertIn("collection_design_limit_exceeded", {d.code for d in self.inspect().diagnostics})
        main["collection_limits"]["value"]["maximum_calls"] = True
        self.assertTrue(self.inspect().has_errors)
        main["collection_limits"] = K(state="unknown")
        public = self.inspect().as_dict()["activities"][4]
        self.assertEqual(public["collection_limits"]["state"], "unknown")
        self.assertIn("collection_limits", public["outstanding_requirements"])

    def test_non_hero_collection_cannot_be_promoted_by_hero_budget_fields(self):
        self.complete_core()
        row(self.study, "study_registration")["protocol"]["design"] = "descriptive"
        (self.directory / "study.json").write_bytes(encode(self.study))
        result = self.inspect(loaded=load_study(self.directory / "study.json"))
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertIn("unsupported_collection_design", result.as_dict()["activities"][4]["outstanding_requirements"])
        self.assertEqual(result.as_dict()["activities"][0]["packet_status"], "complete_for_review")

    def test_invalid_time_order_is_rejected_without_exposing_the_times(self):
        core = self.complete_core()
        core["time_window"] = K({"start": "2026-09-23T00:00:00Z", "end": "2026-09-22T00:00:00Z"})
        result = self.inspect()
        self.assertIn("invalid_time_window", {d.code for d in result.diagnostics})
        self.assertNotIn(b"2026-09-23", result.json_bytes)

    def test_unknown_fields_boolean_authority_and_parser_budget_bypasses_fail(self):
        data = copy.deepcopy(self.data)
        data["execution_authorized"] = True
        self.assertIn("unknown_field", {d.code for d in self.inspect(data).diagnostics})
        for raw, limits, code in ((b'{"kind":"x","kind":"y"}', None, "duplicate_json_key"),
                                 (encode(self.data), ReadLimits(max_file_bytes=64), "file_size_exceeded"),
                                 (encode(self.data), ReadLimits(max_records=10), "record_count_exceeded"),
                                 (encode(self.data), ReadLimits(max_bundle_bytes=1), "bundle_size_exceeded"),
                                 (encode(self.data), ReadLimits(max_bundle_bytes=128*1024*1024), "unsupported_read_limit"),
                                 (b'[[[[0]]]]', ReadLimits(max_depth=2), "json_depth_exceeded")):
            result = inspect_activity_packet(self.loaded, raw, limits)
            self.assertEqual(result.exit_code, 2)
            self.assertIn(code, {d.code for d in result.diagnostics})
            self.assertFalse(result.as_dict()["execution_authorized"])

    def test_aggregate_bytes_include_loaded_study_and_packet_at_exact_boundary(self):
        data = encode(self.data)
        total = self.loaded.total_read_bytes + len(data)
        result = inspect_activity_packet(self.loaded, data, ReadLimits(max_bundle_bytes=total))
        self.assertFalse(result.has_errors, result.diagnostics)
        rejected = inspect_activity_packet(self.loaded, data, ReadLimits(max_bundle_bytes=total - 1))
        self.assertIn("bundle_size_exceeded", {d.code for d in rejected.diagnostics})

    def test_malformed_rows_cannot_amplify_diagnostics_before_budget_check(self):
        data = copy.deepcopy(self.data)
        data["activities"][0]["requirements"] = [{}] * 500
        result = self.inspect(data, limits=ReadLimits(max_records=10))
        self.assertEqual([d.code for d in result.diagnostics], ["record_count_exceeded"])
        self.assertLess(len(result.json_bytes), 2048)
        bounded = self.inspect(data)
        self.assertEqual(len(bounded.diagnostics), 128)
        self.assertEqual(bounded.diagnostics[-1].code, "diagnostic_limit_exceeded")
        self.assertLess(len(bounded.json_bytes), 32 * 1024)

    def test_public_result_is_repeatable_immutable_and_does_not_expose_prose(self):
        core = self.complete_core()
        secret = "PRIVATE_CONTACT_api-key-99"
        core["action"] = K(secret)
        core["responsible_operator"] = K(secret)
        core["requirements"][0]["basis"] = K(secret)
        first, second = self.inspect(), self.inspect()
        self.assertEqual(first.json_bytes, second.json_bytes)
        self.assertNotIn(secret.encode(), first.json_bytes)
        self.assertNotIn(b"fixture-operator", first.json_bytes)
        self.assertNotIn(b"Prepare all", first.json_bytes)
        public = first.as_dict()
        public["execution_authorized"] = True
        self.assertFalse(first.as_dict()["execution_authorized"])
        self.assertEqual(first.as_dict()["input_sha256"], hashlib.sha256(encode(self.data)).hexdigest())
        with self.assertRaises(TypeError):
            first.result["execution_authorized"] = True


if __name__ == "__main__":
    unittest.main()
