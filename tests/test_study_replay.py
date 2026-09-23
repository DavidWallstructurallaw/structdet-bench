"""Current study bridge replay and original-response conformance.

The prior canonical suites own numerical oracles and individual replay parser
rules. These cases protect the added study boundary and immutable snapshots.
Every input is an authored fixture. No candidate program is executed.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import longitudinal_uncertainty as uncertainty
from structdet_bench import study_bridge as bridge
from structdet_bench import study_records as records
from structdet_bench import study_reporting as reporting
from structdet_bench.contracts import InputError
from tests.helpers import ROOT
from tests.test_study_bridge import STAMP, existing, mixed, operational
from tests.test_study_collection import K, encoded, ref


def digest(value):
    """Independently encode the documented manifest digest convention."""
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False) + "\n").encode()).hexdigest()


def rehash_manifest(manifest):
    collection = manifest["longitudinal_replay"]
    for entry in collection["entries"]:
        replay = entry["replay"]
        if replay is not None:
            replay["sha256"] = digest({k: v for k, v in replay.items() if k != "sha256"})
    collection["sha256"] = digest({k: v for k, v in collection.items() if k != "sha256"})
    manifest["longitudinal_replay_sha256"] = digest(collection)


class StudyReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.carrier = existing(Path(cls.directory.name) / "original", "hero_recursive", "structdet_longitudinal_v1")
        cls.compilation = cls.carrier.compile()
        if not cls.compilation.compiled:
            raise AssertionError(cls.compilation.as_dict())
        cls.original = bridge.analyze_compilation(cls.compilation, run_id="study-replay", recorded_at=STAMP)
        if cls.original.exit_code != 0:
            raise AssertionError(cls.original.exit_code)

    def replay(self, body, compilation=None):
        return bridge.analyze_compilation(compilation or self.compilation,
            run_id="study-replay", recorded_at=STAMP, replay_manifest_bytes=body)

    def test_relocated_reordered_envelope_keeps_carrier_replay_and_original_indices(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "relocated"
            shutil.copytree(self.carrier.root, target)
            data = json.loads((target / "study.json").read_bytes())
            data["records"].reverse()
            data["packet_inventory"].reverse()
            # Envelope storage is administrative. Registered order inside the
            # exact scientific carrier and the stored draws remain unchanged.
            (target / "study.json").write_bytes(encoded(data))
            compiled = bridge.compile_study(records.load_study(target / "study.json"))
            self.assertTrue(compiled.compiled, compiled.as_dict())
            self.assertEqual(compiled.files, self.compilation.files)
            # After acquisition, replay uses this immutable compilation. It
            # must not silently reopen the now unavailable original carrier.
            shutil.rmtree(target)
            with patch.object(uncertainty, "make_replay", side_effect=AssertionError("fresh replay draw")):
                replayed = self.replay(self.original.manifest_json, compiled)
            self.assertEqual(replayed.exit_code, 0)
            self.assertEqual(replayed.report_json, self.original.report_json)
            self.assertEqual(replayed.report_markdown, self.original.report_markdown)
            before, after = json.loads(self.original.manifest_json), json.loads(replayed.manifest_json)
            # Both calls use the same runtime and explicit time. Only the
            # administrative acquisition receipt for the supplied replay differs.
            self.assertIsNone(before.pop("replay_source"))
            self.assertIsNotNone(after.pop("replay_source"))
            self.assertEqual(after, before)
            self.assertTrue(replayed.compilation_receipt["replay_requested"])
            self.assertFalse(replayed.compilation_receipt["empirical_claim_established"])
            self.assertFalse(target.exists())

    def test_bridge_rejects_rehashed_replay_identity_changes_without_rng(self):
        cases = {
            "software": "longitudinal_replay_software_mismatch",
            "source": "longitudinal_replay_method_identity",
            "configuration": "longitudinal_replay_input_identity",
            "seed": "longitudinal_replay_method_or_context",
            "unit_order": "longitudinal_replay_units",
            "changed_saved_index": "longitudinal_replay_index_digest",
            "boolean_index": "longitudinal_replay_indices",
        }
        for change, expected_error in cases.items():
            with self.subTest(change=change):
                saved = json.loads(self.original.manifest_json)
                replay = next(e["replay"] for e in saved["longitudinal_replay"]["entries"] if e["replay"])
                if change == "software":
                    saved["software"]["version"] = "other-software"
                elif change == "source":
                    saved["source_pins"][next(iter(saved["source_pins"]))] = "0" * 64
                elif change == "configuration":
                    saved["analysis_config_sha256"] = "0" * 64
                elif change == "seed":
                    replay["seed"] += 1
                elif change == "unit_order":
                    replay["unit_ids"].reverse()
                elif change == "changed_saved_index":
                    # Retain the recorded draw identity, but rewrite all outer
                    # hashes. A changed valid integer still breaks that identity.
                    replay["indices"][0][0] = 1 - replay["indices"][0][0]
                else:
                    replay["indices"][0][0] = True
                    replay["indices_sha256"] = digest(replay["indices"])
                rehash_manifest(saved)
                with patch.object(uncertainty, "make_replay", side_effect=AssertionError("fresh replay draw")):
                    result = self.replay(encoded(saved))
                self.assertEqual(result.exit_code, 2)
                self.assertIn(expected_error.encode(), result.report_json)
                self.assertTrue(result.compilation_receipt["replay_requested"])
                self.assertFalse(result.compilation_receipt["analysis_performed"])
                self.assertFalse(result.compilation_receipt["reanalysis_performed"])

    def test_semantically_equal_reencoded_carrier_cannot_reuse_old_input_identity(self):
        with TemporaryDirectory() as tmp:
            current = existing(tmp, "hero_recursive", "structdet_longitudinal_v1")
            source = current.path
            previous = source.read_bytes()
            source.write_bytes(previous + b"\n")
            compiled = current.compile()
            self.assertTrue(compiled.compiled, compiled.as_dict())
            self.assertNotEqual(compiled.files, self.compilation.files)
            with patch.object(uncertainty, "make_replay", side_effect=AssertionError("fresh replay draw")):
                result = self.replay(self.original.manifest_json, compiled)
            self.assertEqual(result.exit_code, 2)
            self.assertIn(b"longitudinal_replay_input_identity", result.report_json)
            self.assertEqual(source.read_bytes(), previous + b"\n")


class ExplicitReplayBoundaryTests(unittest.TestCase):
    def test_explicit_empty_replay_is_rejected_without_fresh_generation(self):
        # M does not support replay. An explicit empty request must stay an
        # error rather than quietly executing a fresh supported M analysis.
        with TemporaryDirectory() as tmp:
            carrier, *_ = mixed(tmp)
            compiled = carrier.compile()
            self.assertTrue(compiled.compiled, compiled.as_dict())
            with patch.object(uncertainty, "make_replay", wraps=uncertainty.make_replay) as generation:
                with self.assertRaisesRegex(InputError, "replay_requires_longitudinal_profile"):
                    bridge.analyze_compilation(compiled, replay_manifest_bytes=b"")
            generation.assert_not_called()


class OriginalResponseCorrectionTests(unittest.TestCase):
    def test_response_correction_invalidates_descendants_and_preserves_original_snapshot(self):
        with TemporaryDirectory() as tmp:
            carrier, _, _, _, artifacts = operational(tmp)
            before = carrier.compile()
            self.assertTrue(before.compiled, before.as_dict())
            original = bridge.analyze_compilation(before, run_id="response-correction", recorded_at=STAMP)
            self.assertEqual(original.exit_code, 0)
            response = before.files["original-response.txt"]
            extraction = next(r for r in carrier.data["records"] if r["record_type"] == "extraction")
            raw_record = carrier.f.row(extraction["raw_response_ref"]["value"]["record_id"])
            cursor, pieces = 0, []
            for index, position in enumerate(extraction["positions"], 1):
                span = position["byte_range"]["value"]
                body = before.files[f"body{index}.txt"]
                self.assertEqual(body, response[span["start"]:span["end"]])
                pieces.extend((response[cursor:span["start"]], body))
                cursor = span["end"]
            pieces.append(response[cursor:])
            self.assertEqual(b"".join(pieces), response)
            self.assertEqual(hashlib.sha256(response).hexdigest(), extraction["raw_response_sha256"]["value"])
            template = json.loads((ROOT / "tests/fixtures/phase4/study_complete.json").read_bytes())
            incident = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "correction_incident"))
            incident.update(record_id="challenge-original-response", affected_refs=[ref(raw_record)],
                action_status="proposed", performed_at=K(state="unknown"), replacement_refs=[],
                reanalysis_refs=[], rollback_refs=[], evidence_refs=[])
            carrier.data["records"].append(incident)
            after = carrier.compile()
            invalid = set(after.corrections["invalidated_record_ids"])
            self.assertIn(extraction["record_id"], invalid)
            self.assertTrue({a["record_id"] for a in artifacts} <= invalid)
            self.assertTrue({"label-" + a["record_id"] for a in artifacts} <= invalid)
            self.assertFalse(after.compiled)
            self.assertFalse(after.corrections["reanalysis_performed"])
            readiness = reporting.inspect_study(carrier.load(),
                qualification_packet_id="submission-qualification", mapping_receipt_id=carrier.receipt["record_id"])
            stats = readiness.readiness["populations_and_denominators"]["operational"]
            self.assertEqual(stats["extractions"]["selected_realizations"], 5)
            self.assertEqual(stats["qualification_coverage"]["numerator"], 5)
            self.assertEqual(stats["qualification_coverage"]["effective_current_numerator"], 0)
            with patch.object(bridge, "analyze_bundle", side_effect=AssertionError("withheld input reached engine")):
                with self.assertRaisesRegex(InputError, "compilation_withheld"):
                    bridge.analyze_compilation(after)
            self.assertEqual(before.files["original-response.txt"], response)
            retained = bridge.analyze_compilation(before, run_id="response-correction", recorded_at=STAMP)
            self.assertEqual(retained.report_json, original.report_json)
            self.assertEqual(retained.report_markdown, original.report_markdown)
            self.assertEqual(retained.manifest_json, original.manifest_json)
            self.assertFalse(after.corrections["incidents"][0]["declared_performed"])

    def test_candidate_challenge_keeps_unrelated_siblings_current(self):
        with TemporaryDirectory() as tmp:
            carrier, _, _, _, artifacts = operational(tmp)
            template = json.loads((ROOT / "tests/fixtures/phase4/study_complete.json").read_bytes())
            incident = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "correction_incident"))
            incident.update(record_id="challenge-one-candidate", affected_refs=[ref(artifacts[0])],
                action_status="proposed", performed_at=K(state="unknown"), replacement_refs=[],
                reanalysis_refs=[], rollback_refs=[], evidence_refs=[])
            carrier.data["records"].append(incident)
            result = carrier.compile()
            self.assertFalse(result.compiled)
            invalid = set(result.corrections["invalidated_record_ids"])
            self.assertIn(artifacts[0]["record_id"], invalid)
            self.assertIn("label-" + artifacts[0]["record_id"], invalid)
            for sibling in artifacts[1:]:
                self.assertNotIn(sibling["record_id"], invalid)
                self.assertNotIn("label-" + sibling["record_id"], invalid)
            readiness = reporting.inspect_study(carrier.load(),
                qualification_packet_id="submission-qualification", mapping_receipt_id=carrier.receipt["record_id"])
            stats = readiness.readiness["populations_and_denominators"]["operational"]
            self.assertEqual(stats["extractions"]["selected_realizations"], 5)
            self.assertEqual(stats["qualification_coverage"]["effective_current_numerator"], 4)


if __name__ == "__main__":
    unittest.main()
