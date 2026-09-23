"""Public readiness semantics using supplied synthetic records only.

No model call, candidate execution, reviewer contact, or empirical claim occurs.
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

from structdet_bench import study_reporting as reporting
from structdet_bench.study_records import load_study
from structdet_bench.contracts import InputError
from structdet_bench.local_io import ReadLimits
from tests.test_study_bridge import mixed, operational, existing
from tests.test_study_evidence import Fixture
from tests.test_study_collection import K, ref, encoded
from tests.helpers import ROOT

FIXTURES = ROOT / "tests/fixtures/phase4"


def passive(directory, transform=None):
    data = json.loads((FIXTURES / "study_partial.json").read_bytes())
    if transform:
        transform(data)
    path = Path(directory) / "study.json"
    path.write_bytes(encoded(data))
    return load_study(path)


def inspect_fixture(f, packet=True):
    return reporting.inspect_study(f.load(), qualification_packet_id="submission-qualification" if packet else None)


def inspect_carrier(c):
    return reporting.inspect_study(c.load(), qualification_packet_id="submission-qualification" if c.f else None,
        mapping_receipt_id=c.receipt["record_id"] if c.receipt else None)


def disclosure(result, identifier):
    return next(r for r in result.readiness["ec_disclosures"] if r["id"] == identifier)


def all_public(result):
    return b"\n".join((result.json_bytes, result.markdown_bytes, result.provenance_json_bytes,
                        result.compilation_manifest_json_bytes))


class DisclosureTests(unittest.TestCase):
    def test_partial_has_ten_disclosures_and_mandatory_absence_stays_missing(self):
        with TemporaryDirectory() as d:
            x = reporting.inspect_study(passive(d))
            self.assertFalse(x.has_errors)
            self.assertEqual([r["id"] for r in x.readiness["ec_disclosures"]], list(reporting.DISCLOSURE_IDS))
            self.assertEqual(disclosure(x, "evaluator_relationships_bias_controls")["status"], "missing")
            self.assertEqual(disclosure(x, "live_field_evidence")["status"], "missing")
            self.assertEqual(disclosure(x, "long_horizon_recovery_override")["status"], "not_applicable")
            self.assertFalse(x.readiness["claim_scope"]["empirical_claim_established"])
            self.assertEqual(x.readiness["evidence_status"], "fixture_only")

    def test_required_human_qualification_cannot_be_declared_inapplicable(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            artifact = f.add_group()[0]
            judge, _ = f.qualify(artifact)
            judge["reviewer"]["qualifications"] = K(state="not_applicable")
            f.roster["reviewers"][0]["qualifications"] = K(state="not_applicable")
            x = inspect_fixture(f)
            reviews = disclosure(x, "evaluator_relationships_bias_controls")["reviews"]
            row = next(r for r in reviews if r["review_ref"] == reporting.public_alias(judge["record_id"]))
            self.assertEqual(row["disclosures"]["qualifications"]["state"], "missing")
            self.assertEqual(row["disclosures"]["qualifications"]["declared_state"], "not_applicable")
            self.assertFalse(disclosure(x, "evaluator_relationships_bias_controls")["actual_human_identity_authenticated"])

    def test_longitudinal_legacy_carrier_is_disclosed_as_supplied(self):
        with TemporaryDirectory() as d:
            c = existing(d, "hero_recursive", "structdet_longitudinal_v1")
            c.registration["protocol"]["longitudinal_input"] = K(state="unknown")
            x = inspect_carrier(c)
            self.assertTrue(x.compilation.compiled)
            row = disclosure(x, "long_horizon_recovery_override")
            self.assertEqual(row["status"], "supplied_input_only")
            self.assertEqual(row["selected_carrier_route"], "legacy_profile_input")
            self.assertEqual(row["declared_input"]["state"], "unknown")
            self.assertFalse(row["recovery_or_override_established"])

    def test_missing_requested_longitudinal_input_does_not_become_inapplicable(self):
        def change(data):
            r = data["records"][0]
            r["requested_profile"] = "structdet_longitudinal_v1"
            r["protocol"]["design"] = "supplied_longitudinal"
            r["protocol"]["longitudinal_input"] = K(state="unknown")
        with TemporaryDirectory() as d:
            x = reporting.inspect_study(passive(d, change))
            self.assertEqual(disclosure(x, "long_horizon_recovery_override")["status"], "missing")
            self.assertFalse(x.compilation.compiled)

    def test_openness_requires_all_five_conditions_and_field_evidence(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            artifact = f.add_group()[0]
            judge, _ = f.qualify(artifact)
            f.add_claim(artifact, judge)
            f.evidence["evidence"] = [r for r in f.evidence["evidence"] if r["purpose"] != "external_presence"]
            x = inspect_fixture(f)
            field = disclosure(x, "live_field_evidence")
            self.assertEqual(field["status"], "missing")
            self.assertTrue(field["required_for_operational_openness"])
            self.assertEqual(set(x.readiness["five_condition_assessments"][0]["conditions"]),
                {"structural_validity", "external_presence", "source_integrity", "tail_retention", "corrective_capacity"})
            self.assertFalse(x.readiness["five_condition_assessments"][0]["operational_openness_established"])

    def test_supplied_currentness_is_separate_from_effective_currentness(self):
        def change(data):
            data["records"][0]["currentness"] = {"state": "current", "assessed_at": K("2026-01-01T00:00:00Z"),
                "expires_at": K("2027-01-01T00:00:00Z"), "basis": K("Synthetic supplied judgment.")}
        with TemporaryDirectory() as d:
            x = reporting.inspect_study(passive(d, change))
            row = disclosure(x, "currentness_expiry")
            self.assertEqual(row["declared_currentness"], "current")
            self.assertEqual(row["effective_currentness"], "unresolved")
            self.assertEqual(row["expires_at"]["value"], "2027-01-01T00:00:00Z")
            self.assertFalse(row["fresh_external_review_performed"])


class PopulationTests(unittest.TestCase):
    def test_mixed_population_reuses_original_distinct_denominators(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            x = inspect_carrier(c)
            cell = x.readiness["populations_and_denominators"]["compiled_cells"]["cells"][0]
            self.assertEqual(cell["planned_positions"]["value"], 5)
            self.assertEqual(cell["selected_population"]["value"], 5)
            self.assertEqual(cell["populations"]["classified_all"]["count"], 3)
            self.assertEqual(cell["populations"]["classified_valid"]["count"], 1)
            self.assertEqual(cell["coverage"]["classified_valid_coverage"]["denominator"], 2)
            self.assertEqual(cell["coverage"]["classified_valid_fraction"]["denominator"], 3)
            self.assertEqual(cell["validity_status_counts"]["undetermined"], 1)
            self.assertEqual(cell["validity_status_counts"]["not_assessed"], 1)
            self.assertEqual(x.readiness["qualification"]["fixed_sorting_design_applicability"], "outside_selected_operational_design")

    def test_zero_population_and_undefined_ratio_remain_distinct(self):
        with TemporaryDirectory() as d:
            c, *_ = operational(d)
            x = inspect_carrier(c)
            cell = x.readiness["populations_and_denominators"]["compiled_cells"]["cells"][0]
            self.assertEqual(cell["populations"]["classified_valid"]["count"], 0)
            self.assertEqual(cell["populations"]["classified_valid"]["status"], "available")
            self.assertEqual(cell["coverage"]["classified_valid_coverage"]["status"], "undefined")
            self.assertEqual(cell["coverage"]["valid_fraction_selected"]["status"], "available")
            self.assertEqual(cell["coverage"]["valid_fraction_selected"]["numerator"], 0)

    def test_withheld_carrier_has_unavailable_compiled_population(self):
        with TemporaryDirectory() as d:
            x = reporting.inspect_study(passive(d))
            cells = x.readiness["populations_and_denominators"]["compiled_cells"]
            self.assertEqual(cells["status"], "unavailable")
            self.assertEqual(tuple(cells["cells"]), ())
            self.assertFalse(x.readiness["compilation"]["analysis_bundle_created"])

    def test_failed_call_keeps_positions_responses_and_realizations_separate(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            f.data["records"][0]["protocol"]["design"] = "sorting_abc"
            f.data["records"][0]["requested_profile"] = "hero_sort_abc_v1"
            f.add_call(status="failed")
            x = inspect_fixture(f)
            stats = x.readiness["populations_and_denominators"]["operational"]
            self.assertEqual(stats["original_call_records"], 1)
            self.assertEqual(stats["supplied_original_planned_positions"], 5)
            self.assertEqual(stats["acquired_original_responses"], 0)
            self.assertEqual(stats["registered_main_design"]["planned_calls"], 72)
            self.assertEqual(stats["registered_main_design"]["planned_positions"], 360)
            self.assertEqual(stats["registered_main_design"]["selected_realizations"], 0)
            self.assertEqual(stats["extractions"]["records"], 0)

    def test_fixed_audit_missing_opportunity_keeps_original_denominator(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            for artifact in f.add_group():
                f.qualify(artifact)
            x = inspect_fixture(f)
            stats = x.readiness["populations_and_denominators"]["operational"]
            self.assertEqual(stats["fixed_audit_coverage"]["denominator"], 72)
            self.assertEqual(stats["fixed_audit_coverage"]["numerator"], 0)
            self.assertEqual(stats["fixed_audit_coverage"]["missing_opportunities"], 71)
            self.assertEqual(stats["extractions"]["selected_realizations"], 5)
            self.assertEqual(stats["extractions"]["declared_positions"], 5)

    def test_selection_is_explicit_and_wrong_packet_never_falls_back(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            for artifact in f.add_group():
                f.qualify(artifact)
            loaded = f.load()
            selected = reporting.inspect_study(loaded, qualification_packet_id="submission-qualification")
            omitted = reporting.inspect_study(loaded)
            wrong = reporting.inspect_study(loaded, qualification_packet_id="missing-packet")
            key = "qualification_coverage"
            self.assertEqual(selected.readiness["populations_and_denominators"]["operational"][key]["numerator"], 5)
            self.assertEqual(omitted.readiness["populations_and_denominators"]["operational"][key]["numerator"], 0)
            self.assertTrue(wrong.has_errors)
            self.assertFalse(wrong.compilation.compiled)

    def test_proposed_correction_keeps_extractions_and_invalidates_current_mass(self):
        with TemporaryDirectory() as d:
            c, artifacts, *_ = operational(d)
            template = json.loads((FIXTURES / "study_complete.json").read_bytes())
            incident = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "correction_incident"))
            artifact = next(r for r in c.data["records"] if r["record_type"] == "artifact" and r["artifact_role"] == "candidate")
            incident.update(record_id="report-correction", affected_refs=[ref(artifact)], action_status="proposed",
                performed_at=K(state="unknown"), replacement_refs=[], rollback_refs=[], reanalysis_refs=[], evidence_refs=[])
            c.data["records"].append(incident)
            x = inspect_carrier(c)
            stats = x.readiness["populations_and_denominators"]["operational"]
            self.assertEqual(stats["extractions"]["selected_realizations"], 5)
            self.assertEqual(stats["qualification_coverage"]["numerator"], 5)
            self.assertEqual(stats["qualification_coverage"]["effective_current_numerator"], 4)
            self.assertFalse(x.compilation.compiled)
            correction = disclosure(x, "correction_path_actual_action")
            self.assertFalse(correction["actual_action_authenticated"])
            self.assertFalse(correction["assessment"]["reanalysis_performed"])


class PrivacyAndRenderingTests(unittest.TestCase):
    def test_public_ids_paths_and_prose_are_withheld_but_joins_remain(self):
        secret_id, secret_text = "credential-ID-canary", "secret-person@example.invalid and /private/credential-file"
        def change(data):
            data["study_id"] = secret_id
            for r in data["records"]:
                r["study_id"] = secret_id
            data["records"][1]["record_id"] = "private-artifact-canary"
            data["records"][1]["original_source"] = K(secret_text)
            data["records"][0]["claim_scope"] = secret_text
        with TemporaryDirectory() as d:
            x = reporting.inspect_study(passive(d, change))
            raw = all_public(x)
            for secret in (secret_id, secret_text, "private-artifact-canary", str(Path(d))):
                self.assertNotIn(secret.encode(), raw)
            self.assertEqual(x.readiness["study_identity"]["study_ref"], x.provenance["study_ref"])
            source = disclosure(x, "source_transformation_lineage")["artifacts"][0]
            self.assertIn(source["artifact_ref"], {r["record_ref"] for r in x.provenance["records"]})
            self.assertEqual(source["source"]["value_sha256"], hashlib.sha256(secret_text.encode()).hexdigest())
            self.assertTrue(source["source"]["public_text_withheld"])

    def test_requested_actual_and_enforced_controls_keep_knowledge_privately(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            call = f.add_call(status="failed")
            call["controls"]["temperature"] = K(state="unknown")
            submission = f.submissions[call["record_id"]]
            submission["cap"]["unit"] = K("credential-cap-unit-canary")
            submission["context"]["platform_context"] = K("secret-wrapper-canary")
            submission["context"]["visible_system_instruction_ref"] = copy.deepcopy(call["prompt_ref"])
            x = inspect_fixture(f)
            row = x.readiness["call_control_records"][0]
            self.assertEqual(row["requested_controls"]["temperature"]["value"], "0.4")
            self.assertEqual(row["actual_controls"]["temperature"]["state"], "unknown")
            self.assertIs(row["enforced_controls"]["temperature"]["value"], True)
            self.assertEqual(row["actual_controls"]["hidden_controls"]["state"], "unknown")
            self.assertEqual(row["context"]["visible_system_instruction_ref"]["public_ref"],
                reporting.public_alias(call["prompt_ref"]["value"]["record_id"]))
            for secret in ("credential-cap-unit-canary", "secret-wrapper-canary", call["prompt_ref"]["value"]["record_id"]):
                self.assertNotIn(secret.encode(), all_public(x))

    def test_evidence_scope_and_pins_precede_counts_in_both_formats(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            x = inspect_carrier(c)
            self.assertEqual(list(json.loads(x.json_bytes))[:4], ["material_role", "evidence_status", "claim_scope", "study_identity"])
            md = x.markdown_bytes.decode()
            self.assertLess(md.index("Material: **fixture**"), md.index("Compiled population overview"))
            self.assertLess(md.index("Study identity and source pins"), md.index("Compiled population overview"))
            self.assertIn("| Selected | Classified all | Classified valid |", md)
            self.assertIn("| claim deployment scope |", md)

    def test_json_and_markdown_share_every_public_field_and_are_repeatable(self):
        with TemporaryDirectory() as d:
            loaded = passive(d)
            first, second = reporting.inspect_study(loaded), reporting.inspect_study(loaded)
            self.assertEqual(all_public(first), all_public(second))
            detail = first.markdown_bytes.decode().split("## Full public record", 1)[1]
            recovered = {}
            for chunk in detail.split("\n## ")[1:]:
                title, body = chunk.split("\n", 1)
                key = title.lower().replace(" ", "_")
                body = body.strip()
                if body.startswith("```json\n"):
                    body = body[len("```json\n"):].rsplit("\n```", 1)[0]
                recovered[key] = json.loads(body)
            self.assertEqual(recovered, json.loads(first.json_bytes))

    def test_output_budget_rejection_has_small_complete_failure_receipt(self):
        with TemporaryDirectory() as d:
            loaded = passive(d)
            initial = reporting.inspect_study(loaded)
            tiny = replace(initial.compilation, limits=ReadLimits(max_file_bytes=512))
            with patch.object(reporting, "compile_study", return_value=tiny):
                x = reporting.inspect_study(loaded)
            self.assertTrue(x.has_errors)
            self.assertIn("study_report_output_budget_exceeded", {r.code for r in x.diagnostics})
            self.assertLess(len(x.json_bytes), 5000)
            self.assertEqual(len(x.readiness["ec_disclosures"]), 10)
            self.assertFalse(x.compilation_manifest["analysis_bundle_created"])

    def test_malformed_input_error_does_not_echo_private_path(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "secret-credential-private.json"
            p.write_bytes(b'{"secret-person":"unterminated')
            x = reporting.inspect_study(load_study(p))
            self.assertEqual(x.exit_code, 2)
            self.assertNotIn(b"secret", all_public(x))
            self.assertNotIn(str(Path(d)).encode(), all_public(x))

    def test_publication_receipt_updates_same_tree_and_never_marks_uncompiled_created(self):
        with TemporaryDirectory() as d:
            loaded = passive(d)
            initial = reporting.inspect_study(loaded)
            with self.assertRaises(InputError):
                initial.with_publication(analysis_bundle_created=True, publication_mode="analysis_bundle")
            x = initial.with_publication(analysis_bundle_created=False, publication_mode="readiness_only", restriction="compilation_withheld")
            self.assertFalse(x.readiness["compilation"]["analysis_bundle_created"])
            self.assertEqual(x.readiness["publication"]["restriction"], "compilation_withheld")
            self.assertNotIn("publication", initial.readiness)
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            x = inspect_carrier(c).with_publication(analysis_bundle_created=True, publication_mode="analysis_bundle")
            self.assertTrue(x.readiness["compilation"]["analysis_bundle_created"])
            self.assertTrue(x.compilation_manifest["analysis_bundle_created"])
            self.assertFalse(x.readiness["compilation"]["analysis_performed"])


class SpendingTests(unittest.TestCase):
    def test_known_zero_unknown_and_unavailable_costs_are_distinct(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            one = f.add_call("zero", status="failed")
            two = f.add_call("unknown", status="failed", condition="B")
            three = f.add_call("unavailable", status="failed", condition="C")
            one["usage"].update(monetary_cost=K("0"), currency=K("USD"))
            two["usage"]["monetary_cost"] = K(state="unknown")
            three["usage"]["monetary_cost"] = K(state="unavailable")
            spending = inspect_fixture(f).readiness["spending_knowledge"]
            self.assertEqual(dict(spending["cost_knowledge_counts"]), {"known": 1, "unknown": 1, "unavailable": 1})
            self.assertEqual(spending["calls"][0]["monetary_cost"], {"state": "known", "value": "0"})
            self.assertEqual(spending["total_cost"]["state"], "unavailable")

    def test_exact_cost_total_preserves_long_decimal_and_fraction_oracles(self):
        with TemporaryDirectory() as d:
            f = Fixture(d)
            for index, (condition, amount) in enumerate(zip("ABC", ("123456789012345678901234567890.1", "0.2", "0"))):
                row = f.add_call("cost-" + condition, status="failed", condition=condition)
                row["usage"].update(monetary_cost=K(amount), currency=K("USD"))
            total = inspect_fixture(f).readiness["spending_knowledge"]["total_cost"]
            self.assertEqual(total["state"], "known")
            self.assertEqual(total["value"]["exact_decimal"], "123456789012345678901234567890.3")
        with TemporaryDirectory() as d:
            f = Fixture(d)
            f.add_call(status="failed")["usage"].update(monetary_cost=K("0"), currency=K("USD"))
            self.assertEqual(inspect_fixture(f).readiness["spending_knowledge"]["total_cost"]["value"]["exact_decimal"], "0")


if __name__ == "__main__":
    unittest.main()
