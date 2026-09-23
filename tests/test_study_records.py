"""Independent passive-study grammar, meaning, and acquisition checks.

The fixtures and expected values are stipulated software examples. They do not
assert that any person reviewed material or that any candidate was executed.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import study_records as sr
from structdet_bench.contracts import InputError
from structdet_bench.local_io import ReadLimits


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "phase4"


def fixture(name="complete"):
    return json.loads((FIXTURES / ("study_" + name + ".json")).read_bytes())


def row(data, kind):
    return next(value for value in data["records"] if value["record_type"] == kind)


def ref(record):
    return {key: record[key] for key in ("record_type", "record_id", "record_version")}


def K(value=None, *, state="known", reason="Stipulated fixture uncertainty."):
    return {"state": state, "value": value} if state == "known" else {"state": state, "reason": reason}


class Assertions:
    def assert_valid(self, data, **kwargs):
        result = sr.parse_study(data, **kwargs)
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertEqual(result.exit_code, 0)
        return result

    def assert_invalid(self, data, code=None, *, byte_input=False, **kwargs):
        result = (sr.parse_study_bytes if byte_input else sr.parse_study)(data, **kwargs)
        self.assertTrue(result.has_errors, result.diagnostics)
        self.assertEqual(result.exit_code, 2)
        if code is not None:
            self.assertIn(code, {issue.code for issue in result.diagnostics})
        return result


class StrictBytesTests(Assertions, unittest.TestCase):
    def test_duplicate_top_level_and_escaped_keys_are_rejected(self):
        for raw in (b'{"study_id":"a","study_id":"b"}', b'{"a":1,"\\u0061":2}'):
            with self.subTest(raw=raw):
                self.assert_invalid(raw, "duplicate_json_key", byte_input=True)

    def test_duplicate_nested_keys_are_rejected_before_semantics(self):
        self.assert_invalid(b'{"records":[{"record_id":"a","record_id":"b"}]}',
                            "duplicate_json_key", byte_input=True)

    def test_nonfinite_json_constants_never_enter_records(self):
        for token in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(token=token):
                self.assert_invalid(b'{"value":' + token + b'}', "nonfinite_number", byte_input=True)

    def test_malformed_number_tokens_are_rejected(self):
        for token in (b"01", b"+1", b".1", b"1.", b"1e", b"--1", b"0x01"):
            with self.subTest(token=token):
                self.assert_invalid(b'{"value":' + token + b'}', "invalid_json", byte_input=True)

    def test_utf8_bom_invalid_utf8_and_unpaired_surrogate_are_rejected(self):
        for raw, code in ((b"\xff", "invalid_utf8"), (b"\xef\xbb\xbf{}", "utf8_bom_not_supported"),
                          (b'{"value":"\\ud800"}', "unpaired_unicode_surrogate")):
            with self.subTest(code=code):
                self.assert_invalid(raw, code, byte_input=True)

    def test_trailing_junk_empty_and_multiple_documents_are_rejected(self):
        for raw in (b"", b"{} {}", b'{"x":1,}', b"//comment\n{}", b"null junk"):
            with self.subTest(raw=raw):
                self.assert_invalid(raw, "invalid_json", byte_input=True)

    def test_bytes_api_does_not_coerce_text_to_input_bytes(self):
        self.assert_invalid("{}", "input_not_bytes", byte_input=True)

    def test_number_token_default_limit_is_enforced(self):
        self.assert_invalid(b'{"value":' + b"1" * 1025 + b'}', "number_token_too_long", byte_input=True)

    def test_depth_default_limit_is_enforced(self):
        self.assert_invalid(b"[" * 65 + b"0" + b"]" * 65, "json_depth_exceeded", byte_input=True)

    def test_lowered_numeric_depth_and_file_limits_are_enforced(self):
        for raw, limits, code in ((b'{"x":12345}', ReadLimits(max_number_chars=4), "number_token_too_long"),
                                  (b'[[[0]]]', ReadLimits(max_depth=2), "json_depth_exceeded"),
                                  (b'{"x":1}', ReadLimits(max_file_bytes=3), "file_size_exceeded")):
            with self.subTest(code=code):
                self.assert_invalid(raw, code, byte_input=True, limits=limits)

    def test_nonobject_envelopes_are_controlled_errors(self):
        for raw in (None, False, 0, [], "study"):
            with self.subTest(raw=raw):
                self.assert_invalid(raw)

    def test_larger_reader_limits_cannot_expand_the_frozen_contract(self):
        for key, value in (("max_file_bytes", 16 * 1024 * 1024 + 1),
                           ("max_bundle_bytes", 64 * 1024 * 1024 + 1),
                           ("max_line_bytes", 1024 * 1024 + 1), ("max_records", 100001),
                           ("max_depth", 65), ("max_number_chars", 1025)):
            with self.subTest(key=key):
                self.assert_invalid(fixture(), limits=ReadLimits(**{key: value}))


class EnvelopeTests(Assertions, unittest.TestCase):
    def test_unknown_envelope_and_record_versions_have_no_fallback(self):
        for field, target in (("study_schema_version", "envelope"), ("record_version", "record")):
            data = fixture()
            (data if target == "envelope" else data["records"][0])[field] = "99.0"
            with self.subTest(target=target):
                self.assert_invalid(data)

    def test_every_envelope_field_is_required(self):
        original = fixture()
        for key in original:
            data = copy.deepcopy(original)
            del data[key]
            with self.subTest(key=key):
                self.assert_invalid(data)

    def test_unknown_fields_are_rejected_in_every_record_family(self):
        data = fixture()
        data["run_command"] = "passive malicious text"
        self.assert_invalid(data)
        for index, original in enumerate(fixture()["records"]):
            data = fixture()
            data["records"][index]["opaque_extension"] = {"execute": "never"}
            with self.subTest(kind=original["record_type"]):
                self.assert_invalid(data)

    def test_record_fields_are_required_not_silently_defaulted(self):
        original = fixture()
        for index, value in enumerate(original["records"]):
            for key in value:
                data = copy.deepcopy(original)
                del data["records"][index][key]
                with self.subTest(kind=value["record_type"], key=key):
                    self.assert_invalid(data)

    def test_null_boolean_array_and_string_cannot_replace_record_objects(self):
        for value in (None, False, [], "artifact"):
            data = fixture()
            data["records"][0] = value
            with self.subTest(value=value):
                self.assert_invalid(data)

    def test_unknown_record_type_is_not_an_opaque_extension(self):
        data = fixture()
        data["records"][0]["record_type"] = "candidate_execution"
        self.assert_invalid(data)

    def test_duplicate_record_identity_is_rejected(self):
        data = fixture()
        data["records"].append(copy.deepcopy(data["records"][0]))
        self.assert_invalid(data)

    def test_duplicate_id_across_different_record_families_is_rejected(self):
        data = fixture()
        data["records"][1]["record_id"] = data["records"][0]["record_id"]
        self.assert_invalid(data)

    def test_record_and_study_ids_use_an_explicit_nonempty_grammar(self):
        for value in ("", "white space", "../escape", "a\nprivate", "a" * 257, 3, True, None):
            data = fixture()
            data["records"][0]["record_id"] = value
            with self.subTest(value=value):
                self.assert_invalid(data)

    def test_revision_is_a_positive_plain_integer(self):
        for value in (True, False, None, "1", 0, -1, 1.0):
            data = fixture()
            data["records"][0]["revision"] = value
            with self.subTest(value=value):
                self.assert_invalid(data)

    def test_each_declared_study_version_needs_its_registration(self):
        data = fixture()
        data["prior_study_versions"] = ["unregistered-history"]
        self.assert_invalid(data)

    def test_duplicate_prior_versions_and_current_as_prior_are_rejected(self):
        for value in (["previous", "previous"], [fixture()["study_version"]]):
            data = fixture()
            data["prior_study_versions"] = value
            self.assert_invalid(data)

    def test_parse_result_does_not_alias_mutable_input(self):
        data = fixture()
        result = self.assert_valid(data)
        old = result.data["study_id"]
        data["study_id"] = "changed-after-parsing"
        data["records"][0]["record_id"] = "changed-after-parsing"
        self.assertEqual(result.data["study_id"], old)
        self.assertNotEqual(result.data["records"][0]["record_id"], "changed-after-parsing")
        with self.assertRaises(TypeError):
            result.data["study_id"] = "mutation"
        with self.assertRaises(TypeError):
            result.data["records"][0]["record_id"] = "mutation"

    def test_parsing_has_no_file_network_or_process_side_effects(self):
        data = fixture()
        with patch("builtins.open", side_effect=AssertionError("file access")), \
             patch("socket.socket", side_effect=AssertionError("network access")), \
             patch("subprocess.Popen", side_effect=AssertionError("process execution")):
            self.assert_valid(data)

    def test_direct_python_cycles_fail_without_recursion_or_serialization_crash(self):
        data = fixture()
        data["records"].append(data)
        self.assert_invalid(data)
        values = []
        values.append(values)
        self.assert_invalid(values)

    def test_direct_python_float_has_no_silent_decimal_coercion(self):
        data = fixture()
        row(data, "collection_ledger")["controls"]["temperature"] = K(0.4)
        self.assert_invalid(data, "invalid_json_value")


class FixtureAndCanonicalTests(Assertions, unittest.TestCase):
    def test_complete_twelve_family_fixture_matches_independent_expected_facts(self):
        expected = fixture("expected")["complete"]
        result = self.assert_valid(fixture())
        data = result.data
        self.assertEqual(len(result.records), expected["record_count"])
        self.assertEqual([value["record_type"] for value in data["records"]], expected["record_types"])
        for key in ("study_id", "study_version", "evidence_policy", "material_role"):
            self.assertEqual(data[key], expected[key])
        self.assertEqual(len(data["packet_inventory"]), expected["packet_count"])
        self.assertFalse(result.substantive_validation_performed)
        self.assertFalse(row(data, "compilation_receipt")["analysis_bundle_created"])

    def test_partial_fixture_preserves_explicit_missing_content(self):
        expected = fixture("expected")["partial"]
        result = self.assert_valid(fixture("partial"))
        self.assertEqual(len(result.records), expected["record_count"])
        self.assertEqual(len(result.data["packet_inventory"]), expected["packet_count"])
        self.assertEqual(row(result.data, "artifact")["content"]["state"], expected["content_state"])
        self.assertFalse(result.substantive_validation_performed)

    def test_malformed_fixture_has_the_hand_authored_failure_disposition(self):
        expected = fixture("expected")["malformed"]
        result = self.assert_invalid(fixture("malformed"), expected["diagnostic_code"])
        self.assertEqual(result.exit_code, expected["exit_code"])

    def test_canonical_bytes_match_independent_json_grammar(self):
        data = fixture()
        expected = (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        self.assertEqual(sr.canonical_study_bytes(data), expected)
        self.assertEqual(sr.canonical_study_bytes(self.assert_valid(data)), expected)

    def test_canonical_round_trip_preserves_record_and_position_order(self):
        data = fixture()
        data["records"].reverse()
        one = sr.canonical_study_bytes(data)
        result = sr.parse_study_bytes(one)
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertEqual(sr.canonical_study_bytes(result), one)
        self.assertEqual([r["record_id"] for r in result.data["records"]], [r["record_id"] for r in data["records"]])
        self.assertEqual(list(row(result.data, "collection_ledger")["planned_positions"]), [1, 2, 3, 4, 5])

    def test_canonical_unicode_is_utf8_and_does_not_change_supplied_text(self):
        data = fixture()
        text = "原始文本 e\u0301 é 😀\r\n  keep spaces  "
        row(data, "artifact")["original_source"] = K(text)
        result = sr.parse_study_bytes(sr.canonical_study_bytes(data))
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertEqual(row(result.data, "artifact")["original_source"]["value"], text)
        self.assertIn("原始文本".encode(), sr.canonical_study_bytes(data))

    def test_exact_number_lexeme_and_decimal_string_remain_distinct(self):
        data = fixture()
        row(data, "collection_ledger")["controls"]["temperature"] = K("0.4000")
        raw = json.dumps(data).encode().replace(b'"0.4000"', b'4.000e-1')
        result = sr.parse_study_bytes(raw)
        self.assertFalse(result.has_errors, result.diagnostics)
        encoded = sr.canonical_study_bytes(result)
        self.assertIn(b'"value": 4.000e-1', encoded)
        self.assertNotIn(b'"value": "4.000e-1"', encoded)
        self.assertIn(b'"value": "0.4000"', sr.canonical_study_bytes(data))

    def test_large_finite_exponent_does_not_turn_into_float_infinity(self):
        data = fixture()
        row(data, "collection_ledger")["controls"]["temperature"] = K("finite-token")
        raw = json.dumps(data).encode().replace(b'"finite-token"', b'1e309')
        result = sr.parse_study_bytes(raw)
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertIn(b'"value": 1e309', sr.canonical_study_bytes(result))

    def test_canonicalization_rejects_malformed_records(self):
        with self.assertRaises(InputError):
            sr.canonical_study_bytes(fixture("malformed"))


class ReferenceTests(Assertions, unittest.TestCase):
    def test_typed_reference_rejects_bare_id_null_and_extra_fields(self):
        for value in ("artifact-source", None, dict(ref(row(fixture(), "artifact")), extra=True)):
            data = fixture()
            row(data, "validation_receipt")["artifact_ref"] = value
            self.assert_invalid(data)

    def test_each_reference_identity_component_is_required(self):
        for key in ("record_type", "record_id", "record_version"):
            data = fixture()
            del row(data, "validation_receipt")["artifact_ref"][key]
            self.assert_invalid(data)

    def test_wrong_record_family_cannot_satisfy_artifact_reference(self):
        data = fixture()
        row(data, "validation_receipt")["artifact_ref"] = ref(row(data, "activity_readiness"))
        self.assert_invalid(data)

    def test_missing_reference_and_wrong_version_never_choose_another_target(self):
        for field, value in (("record_id", "not-present"), ("record_version", "0.2")):
            data = fixture()
            row(data, "validation_receipt")["artifact_ref"][field] = value
            self.assert_invalid(data)

    def test_record_from_another_study_is_rejected(self):
        data = fixture()
        row(data, "artifact")["study_id"] = "foreign-study"
        self.assert_invalid(data, "study_identity_mismatch")

    def test_undeclared_study_version_is_rejected(self):
        data = fixture()
        row(data, "artifact")["study_version"] = "foreign-version"
        self.assert_invalid(data, "study_version_mismatch")

    def test_claim_task_and_task_version_scope_contradictions_are_rejected(self):
        for field in ("claim_id", "task_id", "task_version"):
            data = fixture()
            row(data, "artifact")["scope"][field] = "incompatible"
            with self.subTest(field=field):
                self.assert_invalid(data, "scope_mismatch")

    def test_receipt_review_and_adjudication_hashes_bind_exact_artifact_bytes(self):
        for kind in ("validation_receipt", "human_review", "adjudication"):
            data = fixture()
            row(data, kind)["artifact_sha256"] = "f" * 64
            with self.subTest(kind=kind):
                self.assert_invalid(data, "artifact_hash_mismatch")

    def test_correct_hash_does_not_make_wrong_artifact_reference_equivalent(self):
        data = fixture()
        other = copy.deepcopy(row(data, "artifact"))
        other["record_id"] = "other-artifact"
        other["sha256"] = K("e" * 64)
        other["content"] = K(state="unknown")
        data["records"].append(other)
        row(data, "validation_receipt")["artifact_ref"] = ref(other)
        self.assert_invalid(data, "artifact_hash_mismatch")

    def test_dependency_cycle_fails_even_when_all_references_exist(self):
        data = fixture()
        first, second = row(data, "artifact"), row(data, "validation_receipt")
        first["depends_on"] = [ref(second)]
        second["depends_on"] = [ref(first)]
        self.assert_invalid(data, "dependency_cycle")

    def test_self_dependency_fails(self):
        data = fixture()
        record = row(data, "artifact")
        record["depends_on"] = [ref(record)]
        self.assert_invalid(data, "dependency_cycle")

    def test_admissible_lineage_cycle_is_not_confused_with_dependency_cycle(self):
        data = fixture()
        first, second = row(data, "artifact"), row(data, "validation_receipt")
        first["lineage_refs"] = [ref(second)]
        second["lineage_refs"] = [ref(first)]
        self.assert_valid(data)


class MeaningTests(Assertions, unittest.TestCase):
    def test_known_zero_unknown_and_unavailable_keep_distinct_meanings(self):
        data = fixture()
        usage = row(data, "collection_ledger")["usage"]
        usage["output_tokens"] = K(0)
        usage["input_tokens"] = K(state="unknown")
        usage["hidden_reasoning_tokens"] = K(state="unavailable", reason="Not supplied by external operator.")
        result = self.assert_valid(data)
        saved = row(result.data, "collection_ledger")["usage"]
        self.assertEqual(saved["output_tokens"]["value"], 0)
        self.assertEqual(saved["input_tokens"]["state"], "unknown")
        self.assertEqual(saved["hidden_reasoning_tokens"]["state"], "unavailable")
        self.assertNotIn("value", saved["input_tokens"])
        self.assertNotIn("value", saved["hidden_reasoning_tokens"])

    def test_known_false_is_preserved_as_boolean_not_missingness(self):
        data = fixture()
        row(data, "human_review")["independence"]["declared_independent"] = K(False)
        result = self.assert_valid(data)
        self.assertIs(row(result.data, "human_review")["independence"]["declared_independent"]["value"], False)
        self.assertFalse(result.substantive_validation_performed)

    def test_unknown_state_cannot_carry_false_zero_or_null_value(self):
        for value in (False, 0, None):
            data = fixture()
            row(data, "collection_ledger")["usage"]["input_tokens"] = dict(state="unknown", reason="Unprovided.", value=value)
            self.assert_invalid(data, "value_in_unknown_state")

    def test_known_state_requires_value_and_unknown_states_require_reason(self):
        for value in ({"state": "known"}, {"state": "unknown"}, {"state": "unavailable"},
                      {"state": "not_applicable"}, {"state": "unknown", "reason": ""}):
            data = fixture()
            row(data, "artifact")["original_source"] = value
            self.assert_invalid(data)

    def test_unknown_knowledge_state_extra_keys_and_nonobject_are_rejected(self):
        for value in (None, False, 0, "unknown", {"state": "assumed", "reason": "No evidence."},
                      {"state": "known", "value": "source", "default": True}):
            data = fixture()
            row(data, "artifact")["original_source"] = value
            self.assert_invalid(data)

    def test_boolean_null_negative_and_decimal_cannot_replace_plain_count(self):
        for value in (True, False, None, -1, "0", "1.5"):
            data = fixture()
            row(data, "collection_ledger")["usage"]["output_tokens"] = K(value)
            self.assert_invalid(data)

    def test_null_is_allowed_only_for_the_explicit_seed_semantics(self):
        result = self.assert_valid(fixture())
        self.assertIsNone(row(result.data, "collection_ledger")["controls"]["seed"]["value"])
        data = fixture()
        row(data, "collection_ledger")["controls"]["fresh_context"] = K(None)
        self.assert_invalid(data)

    def test_probability_and_nonnegative_exact_fields_enforce_domain(self):
        for field, value in (("top_p", "1.01"), ("top_p", "-0.01"), ("temperature", "-1")):
            data = fixture()
            row(data, "collection_ledger")["controls"][field] = K(value)
            self.assert_invalid(data)

    def test_all_four_validity_states_remain_distinct_from_assignment(self):
        for state in ("valid", "invalid", "undetermined", "not_assessed"):
            data = fixture()
            row(data, "human_review")["judgment"]["validity_status"] = state
            result = self.assert_valid(data)
            judgment = row(result.data, "human_review")["judgment"]
            self.assertEqual(judgment["validity_status"], state)
            self.assertEqual(judgment["assignment_status"], "unresolved")

    def test_invalid_but_assigned_and_valid_but_unresolved_are_representable(self):
        data = fixture()
        judgment = row(data, "human_review")["judgment"]
        judgment.update(assignment_status="assigned", structural_class_id=K("SORT-ADJ"), validity_status="invalid")
        self.assert_valid(data)
        judgment.update(assignment_status="unresolved", structural_class_id=K(state="unknown"), validity_status="valid")
        self.assert_valid(data)

    def test_inapplicable_optional_requirement_needs_justification(self):
        data = fixture()
        readiness = row(data, "activity_readiness")
        readiness["prerequisites"].append(dict(requirement_id="longitudinal-claim", mandatory=False,
            outcome="not_applicable", evidence_refs=[], basis=K("No longitudinal claim requested.")))
        self.assert_valid(data)
        readiness["prerequisites"][-1]["basis"] = K(state="unknown")
        self.assert_invalid(data)

    def test_missing_mandatory_requirement_cannot_be_marked_inapplicable(self):
        data = fixture()
        requirement = row(data, "activity_readiness")["prerequisites"][0]
        requirement.update(outcome="not_applicable", basis=K("Evidence is missing."))
        self.assert_invalid(data, "state_contradiction")

    def test_fixture_policy_and_material_role_cannot_be_silently_promoted(self):
        data = fixture()
        data["evidence_policy"] = "adjudicated_import"
        self.assert_invalid(data, "fixture_policy_mismatch")

    def test_claim_restriction_does_not_create_an_analysis_bundle(self):
        for disposition in ("restricted", "withheld"):
            data = fixture()
            row(data, "compilation_receipt")["claim_disposition"] = disposition
            result = self.assert_valid(data)
            receipt = row(result.data, "compilation_receipt")
            self.assertEqual(receipt["claim_disposition"], disposition)
            self.assertFalse(receipt["analysis_bundle_created"])
        data = fixture()
        row(data, "compilation_receipt")["analysis_bundle_created"] = True
        self.assert_invalid(data, "state_contradiction")

    def test_unknown_enumerations_do_not_collapse_to_available_defaults(self):
        for kind, field in (("validation_receipt", "validity_status"), ("compilation_receipt", "claim_disposition"),
                            ("activity_readiness", "state"), ("correction_incident", "action_status")):
            data = fixture()
            row(data, kind)[field] = "success"
            self.assert_invalid(data)

    def test_proposed_correction_is_preserved_without_performed_timestamp(self):
        result = self.assert_valid(fixture())
        correction = row(result.data, "correction_incident")
        self.assertEqual(correction["action_status"], "proposed")
        self.assertEqual(correction["performed_at"]["state"], "unknown")
        self.assertFalse(result.substantive_validation_performed)

    def test_missing_positions_keep_all_five_registered_indices(self):
        result = self.assert_valid(fixture())
        positions = row(result.data, "extraction")["positions"]
        self.assertEqual([p["within_group_index"] for p in positions], [1, 2, 3, 4, 5])
        self.assertEqual([p["selection"] for p in positions], ["missing"] * 5)
        self.assertEqual(row(result.data, "collection_ledger")["attempt_status"], "not_attempted")

    def test_duplicate_out_of_range_and_boolean_positions_are_rejected(self):
        for positions in ([1, 1, 2, 3, 4], [1, 2, 3, 4, 6], [True, 2, 3, 4, 5]):
            data = fixture()
            row(data, "collection_ledger")["planned_positions"] = positions
            self.assert_invalid(data)

    def test_duplicate_observation_ids_and_false_complete_coverage_are_rejected(self):
        data = fixture()
        coverage = row(data, "validation_receipt")["coverage"]
        coverage["segments"][0]["observed_ids"] = ["T01", "T01"]
        coverage["declared_status"] = "partial"
        self.assert_invalid(data, "coverage_duplicate_test_id")
        coverage["segments"][0]["observed_ids"] = ["T01"]
        coverage["declared_status"] = "complete"
        self.assert_invalid(data, "coverage_count_mismatch")

    def test_nested_unknown_fields_have_no_unvalidated_extension_channel(self):
        paths = [("study_registration", "protocol", "controls"), ("human_review", "reviewer"),
                 ("validation_receipt", "coverage"), ("collection_ledger", "usage"),
                 ("activity_readiness", "prerequisites", 0)]
        for path in paths:
            data = fixture()
            value = row(data, path[0])
            for key in path[1:]:
                value = value[key]
            value["extensions"] = {"unvalidated": True}
            self.assert_invalid(data, "unknown_field")


class RevisionTests(Assertions, unittest.TestCase):
    def test_supersession_requires_same_record_family_and_earlier_revision(self):
        data = fixture()
        row(data, "artifact")["supersedes"] = K(ref(row(data, "validation_receipt")))
        self.assert_invalid(data)
        data = fixture()
        newer = copy.deepcopy(row(data, "artifact"))
        newer["record_id"] = "artifact-later"
        newer["supersedes"] = K(ref(row(data, "artifact")))
        data["records"].append(newer)
        self.assert_invalid(data, "supersession_revision_order")

    def test_supersession_cycles_are_rejected(self):
        data = fixture()
        first = row(data, "artifact")
        second = copy.deepcopy(first)
        second["record_id"] = "second-artifact"
        second["revision"] = 2
        second["supersedes"] = K(ref(first))
        first["supersedes"] = K(ref(second))
        data["records"].append(second)
        self.assert_invalid(data)

    def test_declared_historical_revision_keeps_original_and_replacement(self):
        data = fixture()
        data["prior_study_versions"] = ["v0"]
        old_registration = copy.deepcopy(row(data, "study_registration"))
        old_registration.update(record_id="registration-old", study_version="v0")
        previous = copy.deepcopy(row(data, "artifact"))
        previous.update(record_id="artifact-old", study_version="v0")
        current = row(data, "artifact")
        current.update(revision=2, supersedes=K(ref(previous)))
        data["records"].extend([old_registration, previous])
        result = self.assert_valid(data)
        self.assertEqual(len(result.records), 14)
        row(data, "validation_receipt")["artifact_ref"] = ref(previous)
        self.assert_invalid(data, "study_version_mismatch")

    def test_long_acyclic_dependency_chain_does_not_hit_python_recursion_limit(self):
        data = fixture("partial")
        data["import_budget"]["max_total_records"] = 5000
        data["import_budget"]["max_total_bytes"] = 16 * 1024 * 1024
        previous = None
        template = row(data, "artifact")
        for index in range(1100):
            current = copy.deepcopy(template)
            current["record_id"] = "chain-" + str(index)
            current["depends_on"] = [] if previous is None else [ref(previous)]
            data["records"].append(current)
            previous = current
        self.assert_valid(data)


class PacketTests(Assertions, unittest.TestCase):
    def test_packet_inventory_and_explicit_finite_budgets_are_required(self):
        for field in ("packet_inventory", "import_budget"):
            data = fixture()
            del data[field]
            self.assert_invalid(data)

    def test_budget_fields_are_plain_bounded_integers(self):
        for field in ("max_packets", "max_total_bytes", "max_total_records"):
            for value in (True, False, None, "100", -1, 1.5):
                data = fixture()
                data["import_budget"][field] = value
                with self.subTest(field=field, value=value):
                    self.assert_invalid(data)

    def test_zero_packet_budget_cannot_import_an_existing_packet(self):
        data = fixture()
        data["import_budget"]["max_packets"] = 0
        self.assert_invalid(data, "budget_exceeded_partition_required")

    def test_packet_bytes_and_total_records_obey_declared_budget(self):
        for field, value in (("max_total_bytes", 1), ("max_total_records", 1)):
            data = fixture()
            data["import_budget"][field] = value
            self.assert_invalid(data, "budget_exceeded_partition_required")

    def test_inventory_unknown_fields_and_duplicate_ids_are_rejected(self):
        data = fixture()
        data["packet_inventory"][0]["fallback_url"] = "https://example.invalid/secret"
        self.assert_invalid(data, "unknown_field")
        data = fixture()
        data["packet_inventory"].append(copy.deepcopy(data["packet_inventory"][0]))
        self.assert_invalid(data, "duplicate_packet_id")

    def test_two_packet_ids_cannot_alias_one_local_path(self):
        data = fixture()
        other = copy.deepcopy(data["packet_inventory"][0])
        other["packet_id"] = "same-path-another-id"
        data["packet_inventory"].append(other)
        self.assert_invalid(data, "duplicate_packet_path")

    def test_undeclared_artifact_content_packet_is_rejected(self):
        data = fixture()
        row(data, "artifact")["content"] = K({"packet_id": "not-in-inventory"})
        self.assert_invalid(data, "packet_not_declared")

    def test_packet_and_artifact_size_and_hash_pins_must_agree(self):
        for field, value in (("sha256", "f" * 64), ("size_bytes", 999)):
            data = fixture()
            data["packet_inventory"][0][field] = K(value)
            self.assert_invalid(data)

    def test_unknown_inventory_metadata_stays_explicit_in_memory(self):
        for field in ("sha256", "size_bytes", "record_count"):
            data = fixture()
            data["packet_inventory"][0][field] = K(state="unknown")
            result = self.assert_valid(data)
            self.assertEqual(result.data["packet_inventory"][0][field]["state"], "unknown")
            self.assertFalse(result.substantive_validation_performed)

    def test_local_path_grammar_rejects_traversal_drive_urls_and_expansion(self):
        bad_paths = ("../private", "/etc/passwd", "a/../private", "./payload", "a//payload",
                     "https://example.invalid/source", "file:///private", "C:/private", "//host/share",
                     "~/secret", "$HOME/secret", "a\\b", "a\x00b", "a\nb", "a:b")
        for path in bad_paths:
            data = fixture()
            data["packet_inventory"][0]["location"] = K({"kind": "local", "path": path})
            with self.subTest(path=path):
                self.assert_invalid(data)

    def test_url_is_passive_external_locator_only(self):
        data = fixture()
        data["packet_inventory"][0]["location"] = K({"kind": "external", "locator": "https://example.invalid/evidence.zip"})
        result = self.assert_valid(data)
        self.assertFalse(result.substantive_validation_performed)

    def test_coverage_cannot_reference_undeclared_full_log_packets(self):
        data = fixture()
        row(data, "validation_receipt")["coverage"]["segments"][0]["full_log_packets"] = ["unlisted-log"]
        self.assert_invalid(data, "packet_not_declared")

    def test_external_verification_label_is_unverified_without_external_checks(self):
        data = fixture()
        packet = data["packet_inventory"][0]
        packet["location"] = K({"kind": "external", "locator": "urn:fixture:unavailable-packet"})
        packet["verification"] = "verified_external_receipt"
        packet["verification_ref"] = K(ref(row(data, "study_registration")))
        result = self.assert_valid(data)
        self.assertIn("unverified_attachment", {issue.code for issue in result.diagnostics})
        self.assertFalse(result.substantive_validation_performed)


class SnapshotTests(Assertions, unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = fixture()
        self.payload = (FIXTURES / "study_payload.txt").read_bytes()
        (self.root / "study_payload.txt").write_bytes(self.payload)

    def write(self):
        path = self.root / "study.json"
        path.write_text(json.dumps(self.data, indent=2) + "\n")
        return path

    def load(self, **kwargs):
        return sr.load_study(self.write(), **kwargs)

    def payload_bytes(self, content):
        digest = hashlib.sha256(content).hexdigest()
        self.payload = content
        (self.root / "study_payload.txt").write_bytes(content)
        packet = self.data["packet_inventory"][0]
        packet.update(sha256=K(digest), size_bytes=K(len(content)))
        row(self.data, "artifact").update(sha256=K(digest), size_bytes=K(len(content)))
        for kind in ("validation_receipt", "human_review", "adjudication"):
            row(self.data, kind)["artifact_sha256"] = digest

    def test_local_snapshot_has_exact_bytes_hash_and_size(self):
        result = self.load()
        self.assertFalse(result.has_errors, result.diagnostics)
        snap = result.snapshots["study_payload.txt"]
        expected = fixture("expected")["complete"]
        self.assertEqual(snap.content, self.payload)
        self.assertEqual(snap.sha256, expected["payload_sha256"])
        self.assertEqual(snap.size_bytes, expected["payload_size_bytes"])
        self.assertFalse(result.substantive_validation_performed)

    def test_missing_local_attachment_is_inspectable_uncertainty(self):
        (self.root / "study_payload.txt").unlink()
        result = self.load()
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("attachment_unavailable", {issue.code for issue in result.diagnostics})
        self.assertNotIn("study_payload.txt", result.snapshots)
        self.assertFalse(result.substantive_validation_performed)

    def test_changed_attachment_hash_is_malformed_not_unknown(self):
        (self.root / "study_payload.txt").write_bytes(b"x" * len(self.payload))
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertEqual(result.exit_code, 2)
        self.assertIn("attachment_hash_mismatch", {issue.code for issue in result.diagnostics})

    def test_changed_attachment_size_is_rejected(self):
        (self.root / "study_payload.txt").write_bytes(b"different length")
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertIn("attachment_size_mismatch", {issue.code for issue in result.diagnostics})

    def test_snapshot_remains_immutable_after_source_path_is_replaced(self):
        result = self.load()
        self.assertFalse(result.has_errors, result.diagnostics)
        snap = result.snapshots["study_payload.txt"]
        (self.root / "study_payload.txt").write_bytes(b"replacement")
        self.assertEqual(snap.content, self.payload)
        with self.assertRaises(TypeError):
            result.snapshots["study_payload.txt"] = None

    def test_only_declared_local_files_are_read(self):
        (self.root / "unlisted-private.txt").write_bytes(b"never read")
        result = self.load()
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertEqual(set(result.snapshots), {"study.json", "study_payload.txt"})

    def test_external_urls_are_never_fetched_or_promoted(self):
        self.data["packet_inventory"][0]["location"] = K({"kind": "external", "locator": "https://example.invalid/secret.zip"})
        self.data["packet_inventory"][0]["verification"] = "verified_external_receipt"
        self.data["packet_inventory"][0]["verification_ref"] = K(ref(row(self.data, "study_registration")))
        path = self.write()
        with patch("urllib.request.urlopen", side_effect=AssertionError("URL fetched")), \
             patch("socket.socket", side_effect=AssertionError("network access")):
            result = sr.load_study(path)
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertIn("external_attachment_not_fetched", {issue.code for issue in result.diagnostics})
        self.assertNotIn("study_payload.txt", result.snapshots)
        self.assertEqual(result.attachments[0].declared_verification, "verified_external_receipt")
        self.assertEqual(result.attachments[0].status, "external_not_fetched")
        self.assertFalse(result.acquisition_complete)
        self.assertFalse(result.substantive_validation_performed)

    def test_zip_signature_and_source_code_are_passive_bytes(self):
        self.payload_bytes(b'PK\x03\x04raise RuntimeError("no execution or expansion")\n')
        path = self.write()
        with patch("zipfile.ZipFile", side_effect=AssertionError("archive expanded")), \
             patch("tarfile.open", side_effect=AssertionError("archive expanded")), \
             patch("subprocess.Popen", side_effect=AssertionError("candidate executed")):
            result = sr.load_study(path)
        self.assertFalse(result.has_errors, result.diagnostics)
        self.assertEqual(result.snapshots["study_payload.txt"].content, self.payload)

    def test_symlink_attachment_and_symlink_ancestor_are_rejected(self):
        original = self.root / "original.txt"
        original.write_bytes(self.payload)
        target = self.root / "study_payload.txt"
        target.unlink()
        target.symlink_to(original)
        result = self.load()
        self.assertTrue(result.has_errors)
        target.unlink()
        target.write_bytes(self.payload)
        (self.root / "linked").symlink_to(self.root, target_is_directory=True)
        self.data["packet_inventory"][0]["location"]["value"]["path"] = "linked/study_payload.txt"
        self.assertTrue(self.load().has_errors)

    def test_symlink_study_file_and_root_are_rejected(self):
        path = self.write()
        linked = self.root / "linked.json"
        linked.symlink_to(path)
        self.assertTrue(sr.load_study(linked).has_errors)
        with TemporaryDirectory() as other:
            alias = Path(other) / "root"
            alias.symlink_to(self.root, target_is_directory=True)
            self.assertTrue(sr.load_study(alias / "study.json").has_errors)

    def test_directory_and_fifo_attachments_are_errors_without_blocking(self):
        target = self.root / "study_payload.txt"
        target.unlink()
        target.mkdir()
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertIn("not_regular_file", {issue.code for issue in result.diagnostics})
        target.rmdir()
        os.mkfifo(target)
        self.assertTrue(self.load().has_errors)

    def test_change_during_attachment_read_is_detected(self):
        path = self.write()
        target = self.root / "study_payload.txt"
        original = os.read
        changed = False
        def mutate(fd, count):
            nonlocal changed
            data = original(fd, count)
            if not changed and data == self.payload:
                changed = True
                target.write_bytes(self.payload + b"mutation")
            return data
        with patch("os.read", side_effect=mutate):
            result = sr.load_study(path)
        self.assertTrue(changed)
        self.assertTrue(result.has_errors)
        self.assertIn("file_changed_during_read", {issue.code for issue in result.diagnostics})

    def test_unsupported_safe_open_platform_has_no_fallback_reader(self):
        path = self.write()
        with patch("os.supports_dir_fd", set()):
            result = sr.load_study(path)
        self.assertTrue(result.has_errors)
        self.assertFalse(result.snapshots)

    def test_declared_budget_is_checked_before_any_attachment_read(self):
        self.data["import_budget"]["max_total_bytes"] = 1
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertNotIn("study_payload.txt", result.snapshots)

    def test_actual_per_file_size_limit_rejects_without_truncation(self):
        self.payload_bytes(b"a" * (16 * 1024 * 1024 + 1))
        self.data["import_budget"]["max_total_bytes"] = 64 * 1024 * 1024
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertNotIn("study_payload.txt", result.snapshots)

    def test_json_attachment_duplicate_keys_and_nonobject_jsonl_are_errors(self):
        for content, fmt, count in ((b'{"a":1,"a":2}\n', "json", 1), (b'null\n', "jsonl", 1)):
            self.payload_bytes(content)
            self.data["packet_inventory"][0].update(format=fmt, record_count=K(count))
            result = self.load()
            self.assertTrue(result.has_errors, result.diagnostics)

    def test_jsonl_count_and_line_budget_are_independently_enforced(self):
        self.payload_bytes(b'{"test":"one"}\n{"test":"two"}\n')
        self.data["packet_inventory"][0].update(format="jsonl", record_count=K(1))
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertIn("attachment_record_count_mismatch", {issue.code for issue in result.diagnostics})
        self.data["packet_inventory"][0]["record_count"] = K(2)
        result = self.load()
        self.assertFalse(result.has_errors, result.diagnostics)
        self.payload_bytes(b'{"text":"' + b"x" * (1024 * 1024) + b'"}\n')
        self.data["packet_inventory"][0]["record_count"] = K(1)
        self.data["import_budget"]["max_total_bytes"] = 4 * 1024 * 1024
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertIn("line_size_exceeded", {issue.code for issue in result.diagnostics})

    def test_error_diagnostics_do_not_echo_private_locator_contents(self):
        secret = "PRIVATE-IDENTITY-DO-NOT-PRINT"
        self.data["packet_inventory"][0]["location"] = K({"kind": "local", "path": "../" + secret})
        result = self.load()
        self.assertTrue(result.has_errors)
        self.assertNotIn(secret, repr(result.diagnostics))

    def test_unknown_packet_pins_do_not_bypass_known_artifact_hash_and_size(self):
        for content in (b"x" * len(self.payload), b"different-length"):
            self.data = fixture()
            packet = self.data["packet_inventory"][0]
            packet.update(sha256=K(state="unknown"), size_bytes=K(state="unknown"))
            self.assert_valid(self.data)
            (self.root / "study_payload.txt").write_bytes(content)
            result = self.load()
            self.assertTrue(result.has_errors, result.diagnostics)
            self.assertIn("artifact_hash_mismatch", {issue.code for issue in result.diagnostics})

    def test_actual_snapshot_binds_receipt_hash_when_metadata_hashes_are_unknown(self):
        for kind in ("validation_receipt", "human_review", "adjudication"):
            self.data = fixture()
            self.data["records"] = [r for r in self.data["records"] if r["record_type"] not in
                ({"validation_receipt", "human_review", "adjudication"} - {kind})]
            self.data["packet_inventory"][0]["sha256"] = K(state="unknown")
            row(self.data, "artifact")["sha256"] = K(state="unknown")
            row(self.data, kind)["artifact_sha256"] = "f" * 64
            self.assert_valid(self.data)
            result = self.load()
            with self.subTest(kind=kind):
                self.assertTrue(result.has_errors, result.diagnostics)
                self.assertIn("artifact_hash_mismatch", {issue.code for issue in result.diagnostics})

    def test_actual_snapshot_binds_sent_prompt_hash_when_metadata_hashes_are_unknown(self):
        self.data["records"] = [r for r in self.data["records"] if r["record_type"] not in
            {"validation_receipt", "human_review", "adjudication"}]
        self.data["packet_inventory"][0]["sha256"] = K(state="unknown")
        artifact = row(self.data, "artifact")
        artifact.update(sha256=K(state="unknown"), artifact_role="prompt")
        row(self.data, "core_catalog")["artifact_ref"] = K(state="unknown")
        row(self.data, "collection_ledger").update(prompt_ref=K(ref(artifact)), sent_prompt_sha256=K("f" * 64))
        self.assert_valid(self.data)
        result = self.load()
        self.assertTrue(result.has_errors, result.diagnostics)
        self.assertIn("artifact_hash_mismatch", {issue.code for issue in result.diagnostics})

    def test_actual_snapshot_binds_extracted_response_hash_when_metadata_hashes_are_unknown(self):
        self.data["records"] = [r for r in self.data["records"] if r["record_type"] not in
            {"validation_receipt", "human_review", "adjudication"}]
        self.data["packet_inventory"][0]["sha256"] = K(state="unknown")
        artifact = row(self.data, "artifact")
        artifact.update(sha256=K(state="unknown"), artifact_role="raw_response")
        row(self.data, "core_catalog")["artifact_ref"] = K(state="unknown")
        row(self.data, "collection_ledger").update(raw_response_ref=K(ref(artifact)), attempt_status="succeeded")
        row(self.data, "extraction").update(raw_response_ref=K(ref(artifact)), raw_response_sha256=K("f" * 64))
        self.assert_valid(self.data)
        result = self.load()
        self.assertTrue(result.has_errors, result.diagnostics)
        self.assertIn("artifact_hash_mismatch", {issue.code for issue in result.diagnostics})


class IdentityAssociationTests(Assertions, unittest.TestCase):
    def test_receipt_hash_must_match_known_packet_hash_when_artifact_hash_is_unknown(self):
        data = fixture()
        row(data, "artifact")["sha256"] = K(state="unknown")
        row(data, "validation_receipt")["artifact_sha256"] = "f" * 64
        self.assert_invalid(data, "artifact_hash_mismatch")

    def test_human_revision_cannot_reuse_initial_identity_for_changed_artifact_bytes(self):
        data = fixture()
        row(data, "artifact")["sha256"] = K(state="unknown")
        data["packet_inventory"][0]["sha256"] = K(state="unknown")
        initial = row(data, "human_review")
        initial["submission_stage"] = "initial"
        later = copy.deepcopy(initial)
        later.update(record_id="review-revised", revision=2, submission_stage="revision",
                     artifact_sha256="f" * 64, initial_submission_ref=K(ref(initial)), supersedes=K(ref(initial)))
        data["records"].append(later)
        self.assert_invalid(data, "state_contradiction")

    def test_prompt_response_and_selected_candidate_require_the_right_artifact_role(self):
        for field in ("prompt_ref", "raw_response_ref"):
            data = fixture()
            row(data, "collection_ledger")[field] = K(ref(row(data, "artifact")))
            row(data, "collection_ledger")["attempt_status"] = "succeeded"
            self.assert_invalid(data, "reference_type_mismatch")
        data = fixture()
        data["records"] = [r for r in data["records"] if r["record_type"] != "audit_selection"]
        raw_response = copy.deepcopy(row(data, "artifact"))
        raw_response.update(record_id="raw-response", artifact_role="raw_response")
        data["records"].append(raw_response)
        row(data, "collection_ledger").update(raw_response_ref=K(ref(raw_response)), attempt_status="succeeded")
        row(data, "extraction").update(raw_response_ref=K(ref(raw_response)), raw_response_sha256=raw_response["sha256"])
        position = row(data, "extraction")["positions"][0]
        position.update(selection="selected", artifact_ref=K(ref(row(data, "artifact"))), byte_range=K({"start": 0, "end": 1}))
        self.assert_valid(data)
        row(data, "core_catalog")["artifact_ref"] = K(state="unknown")
        row(data, "artifact")["artifact_role"] = "review"
        self.assert_invalid(data, "reference_type_mismatch")

    def test_audit_present_cannot_replace_a_known_missing_extraction_position(self):
        data = fixture()
        row(data, "audit_selection").update(artifact_ref=K(ref(row(data, "artifact"))),
            opportunity="present", distinct_artifact_count=1)
        self.assert_invalid(data)

    def test_audit_review_links_bind_artifact_identity_even_for_identical_bytes(self):
        data = fixture()
        data["records"] = [r for r in data["records"] if r["record_type"] not in {"collection_ledger", "extraction"}]
        audit = row(data, "audit_selection")
        audit.update(artifact_ref=K(ref(row(data, "artifact"))), opportunity="present", distinct_artifact_count=1,
                     review_refs=[ref(row(data, "human_review"))])
        self.assert_valid(data)
        other = copy.deepcopy(row(data, "artifact"))
        other["record_id"] = "other-artifact-same-bytes"
        data["records"].append(other)
        row(data, "human_review")["artifact_ref"] = ref(other)
        self.assert_invalid(data)

    def test_conformance_review_reference_binds_the_validated_artifact_and_hash(self):
        data = fixture()
        row(data, "validation_receipt")["conformance_review"]["reviewer_ref"] = K(ref(row(data, "human_review")))
        self.assert_valid(data)
        other = copy.deepcopy(row(data, "artifact"))
        other["record_id"] = "other-conformance-target"
        data["records"].append(other)
        row(data, "human_review")["artifact_ref"] = ref(other)
        self.assert_invalid(data)
        data = fixture()
        row(data, "validation_receipt")["conformance_review"]["reviewer_ref"] = K(ref(row(data, "human_review")))
        row(data, "artifact")["sha256"] = K(state="unknown")
        data["packet_inventory"][0]["sha256"] = K(state="unknown")
        row(data, "human_review")["artifact_sha256"] = "f" * 64
        self.assert_invalid(data)

    def test_known_claims_for_one_artifact_must_agree_without_available_bytes(self):
        data = fixture()
        row(data, "artifact")["sha256"] = K(state="unknown")
        data["packet_inventory"][0]["sha256"] = K(state="unknown")
        data["packet_inventory"][0]["location"] = K(state="unavailable", reason="Original bytes are not supplied.")
        self.assert_valid(data)
        row(data, "human_review")["artifact_sha256"] = "f" * 64
        self.assert_invalid(data, "artifact_hash_mismatch")
