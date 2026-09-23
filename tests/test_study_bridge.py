"""Study bridge failure modes and independent fixture equivalence.

Every artifact, review and action in this module is explicitly stipulated.
No generator, supplied program, or reviewer is executed or contacted.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import study_bridge as bridge
from structdet_bench import study_records as sr
from structdet_bench.contracts import SOURCE_PINS, InputError, freeze
from structdet_bench.local_io import ReadLimits, load_bundle
from structdet_bench.pipeline import analyze_bundle
from structdet_bench.populations import build_populations
from tests.helpers import (ROOT, population_bundle, rewrite_evidence_bundle, tagged as T,
                           record_ref as R, artifact_record)
from tests.test_study_evidence import Fixture as EvidenceFixture
from tests.test_study_collection import K, ref, encoded
from tests.phase2_helpers import comparison_fixture

EXPECTED = json.loads((ROOT / "tests/fixtures/phase4/bridge/expected.json").read_bytes())
STAMP = "2026-09-22T00:00:00+00:00"


class Carrier:
    """Independently author the operational envelope around supplied old bytes."""
    def __init__(self, root, profile="m_only", existing=None):
        self.root = Path(root)
        self.f = existing
        self.path = self.root / "carrier/bundle.json"
        source = json.loads((ROOT / "tests/fixtures/phase4/study_partial.json").read_bytes())
        self.artifact_template = copy.deepcopy(next(r for r in json.loads(
            (ROOT / "tests/fixtures/phase4/study_complete.json").read_bytes())["records"] if r["record_type"] == "artifact"))
        self.data = existing.data if existing else source
        if not existing:
            self.data["records"] = [r for r in self.data["records"] if r["record_type"] == "study_registration"]
            self.data["packet_inventory"] = []
        self.registration = self.data["records"][0]
        self.profile = profile
        self.receipt = None
        self.data["import_budget"] = {"max_packets": 4096, "max_total_bytes": 64 * 1024 * 1024, "max_total_records": 100000}
        self.registration["requested_profile"] = profile
        self.registration["protocol"]["design"] = {"m_only": "descriptive", "hero_sort_abc_v1": "sorting_abc", "structdet_longitudinal_v1": "supplied_longitudinal"}[profile]

    def bind_identity(self):
        manifest = json.loads(self.path.read_bytes())
        version = manifest["analysis_config"].get("extensions", {}).get("longitudinal", {}).get("study_version", "v1")
        self.data.update(study_id=manifest["study_id"], study_version=version)
        self.data["prior_study_versions"] = []
        for row in self.data["records"]:
            row.update(study_id=manifest["study_id"], study_version=version)
        frame = manifest["frames"][0]
        for name in self.registration["frame_definition"]:
            self.registration["frame_definition"][name] = copy.deepcopy(frame[name]) if name == "load_bearing_invariants" else K(frame[name])
        self.registration["protocol"]["protocol_version"] = manifest["protocols"][0]["generation_protocol_version"]
        if self.f is None:
            # This envelope adds no collection facts to the supplied old fixture.
            for group in ("controls", "budget"):
                for name in self.registration["protocol"][group]:
                    self.registration["protocol"][group][name] = K(state="unknown")
        elif self.profile == "m_only":
            self.registration["protocol"]["budget"].update(max_calls=K(1), max_positions=K(5), max_output_tokens=K(8192))

    def add_receipt(self):
        template = json.loads((ROOT / "tests/fixtures/phase4/study_complete.json").read_bytes())
        self.receipt = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "compilation_receipt"))
        self.receipt.update(record_id="bridge-map", study_id=self.data["study_id"], study_version=self.data["study_version"],
            analysis_bundle_created=False, disposition="readiness_only", claim_disposition="restricted",
            target_profile=self.profile, outputs=[], mapping_errors=[], input_snapshots=[], id_map=[], evidence_refs=[], depends_on=[])
        self.data["records"].append(self.receipt)
        return self.receipt

    def mapping(self, row, kind, identity):
        if self.receipt is None:
            self.add_receipt()
        self.receipt["id_map"].append({"source_ref": ref(row), "target_record_type": kind, "target_record_id": identity})

    def load(self):
        if self.f:
            self.f.sync()
        self.data["records"] = [r for r in self.data["records"] if r["record_id"] != "legacy-carrier"]
        self.data["packet_inventory"] = [r for r in self.data["packet_inventory"] if not r["packet_id"].startswith("legacy-")]
        for i, path in enumerate(sorted((self.root / "carrier").rglob("*"))):
            if not path.is_file():
                continue
            content = path.read_bytes()
            pid = f"legacy-{i}"
            self.data["packet_inventory"].append({"packet_id": pid, "purpose": "artifact", "format": "bytes",
                "location": K({"kind": "local", "path": path.relative_to(self.root).as_posix()}),
                "sha256": K(hashlib.sha256(content).hexdigest()), "size_bytes": K(len(content)), "record_count": K(0),
                "verification": "unchecked", "verification_ref": K(state="unknown")})
            if path == self.path:
                row = copy.deepcopy(self.artifact_template)
                row.update(record_id="legacy-carrier", artifact_role="source", study_id=self.data["study_id"], study_version=self.data["study_version"],
                    content=K({"packet_id": pid}), sha256=K(hashlib.sha256(content).hexdigest()), size_bytes=K(len(content)), depends_on=[])
                self.data["records"].append(row)
                self.registration["protocol"]["legacy_profile_input"] = K({"artifact_ref": ref(row), "input_schema_version": "0.1", "profile": self.profile})
        (self.root / "study.json").write_bytes(encoded(self.data))
        loaded = sr.load_study(self.root / "study.json")
        if loaded.has_errors:
            raise AssertionError(loaded.diagnostics)
        return loaded

    def compile(self):
        return bridge.compile_study(self.load(), qualification_packet_id="submission-qualification" if self.f else None,
            mapping_receipt_id=self.receipt["record_id"] if self.receipt else None)


def mixed(root):
    expected = EXPECTED["mixed_population"]
    c = Carrier(root)
    _, obs, sup, m = population_bundle(c.path.parent, expected["labels"], validity=expected["validity"], group_sizes=(5,))
    m["source_pins"] = [{"source_id": k, "sha256": v} for k, v in SOURCE_PINS.items()]
    rewrite_evidence_bundle(c.path.parent, obs, sup, m)
    c.bind_identity()
    return c, obs, sup, m


def existing(root, name, profile):
    c = Carrier(root, profile)
    shutil.copytree(ROOT / "examples" / name, c.path.parent)
    manifest = json.loads(c.path.read_bytes())
    if "source_pins" not in manifest:
        manifest["source_pins"] = [{"source_id": k, "sha256": v} for k, v in SOURCE_PINS.items()]
        c.path.write_bytes(encoded(manifest))
    c.bind_identity()
    return c


def operational(root):
    f = EvidenceFixture(root)
    artifacts = f.add_group()
    decisions = [f.qualify(a)[0] for a in artifacts]
    c = Carrier(root, existing=f)
    _, obs, sup, m = population_bundle(c.path.parent, ["SORT-ADJ"] * 5, validity=["not_assessed"] * 5, group_sizes=(5,))
    m["study_id"] = f.data["study_id"]
    m["source_pins"] = [{"source_id": k, "sha256": v} for k, v in SOURCE_PINS.items()]
    call = next(r for r in f.data["records"] if r["record_type"] == "collection_ledger")
    ex = next(r for r in f.data["records"] if r["record_type"] == "extraction")
    by_id = {r["record_id"]: r for r in obs}
    old_call = by_id["call1"]
    call["attempt_id"] = K(old_call["attempt_id"])
    old_call["registered_call_order"] = T(call["registered_call_order"])
    old_call["raw_response_ref"] = T(R("raw_artifact", "original-response"))
    prompt = f.row(call["prompt_ref"]["value"]["record_id"])
    raw = f.row(call["raw_response_ref"]["value"]["record_id"])
    for source, kind, identity in [(prompt, "artifact", "sent-prompt"), (raw, "raw_artifact", "original-response")]:
        path = identity + ".txt"
        (c.path.parent / path).write_bytes(f.packets[source["record_id"]])
        old = artifact_record(identity, path)
        old.update(record_type=kind, expected_sha256=T(source["sha256"]["value"]))
        obs.append(old)
        c.mapping(source, kind, identity)
    cell = m["cells"][0]
    cell.update(prompt_block_id="P01", condition_id="A", prompt_id="sent-prompt",
        model_identifier=T("fixture-model"), model_family=T("fixture-family"))
    protocol = m["protocols"][0]
    protocol.update(conditioning_context_ref=T(R("artifact", "sent-prompt")), seed=T(None),
        decoding_settings=T({"temperature": 0.4, "top_p": 1.0, "presence_penalty": 0, "frequency_penalty": 0, "max_output_tokens": 8192}))
    c.mapping(call, "attempt", "call1")
    c.mapping(call, "cell", "cell1")
    for n, (artifact, decision) in enumerate(zip(artifacts, decisions), 1):
        identity, path = f"body{n}", f"body{n}.txt"
        (c.path.parent / path).write_bytes(f.packets[artifact["record_id"]])
        old = artifact_record(identity, path)
        old["expected_sha256"] = T(artifact["sha256"]["value"])
        obs.append(old)
        by_id[f"s{n}"].update(attempt_id=T(old_call["attempt_id"]), raw_response_ref=T(R("raw_artifact", "original-response")),
            output_ref=T(R("artifact", identity)), output_content_hash=T(artifact["sha256"]["value"]), extraction_rule_version=T("hero_candidates_v1"))
        c.mapping(artifact, "artifact", identity)
        c.mapping(ex, "realization", f"s{n}")
        c.mapping(decision, "assignment", f"a{n}")
        m["analysis_config"]["selection"][0]["registered_positions"]["value"][n-1]["attempt_id"] = T(old_call["attempt_id"])
    rewrite_evidence_bundle(c.path.parent, obs, sup, m)
    c.bind_identity()
    return c, obs, sup, m, artifacts


def errors(result):
    return {r["reason"] for r in result.mapping_errors} | {d.code for d in result.diagnostics if d.severity == "error"}


class CarrierTests(unittest.TestCase):
    def assertCompiled(self, result):
        self.assertTrue(result.compiled, (errors(result), result.mapping_errors))
        self.assertFalse(result.has_errors)
        self.assertFalse(result.as_dict()["substantive_validation_performed"])

    def test_mixed_m_only_preserves_independent_fields_and_engine_bytes(self):
        with TemporaryDirectory() as d:
            c, obs, sup, m = mixed(d)
            result = c.compile()
            self.assertCompiled(result)
            self.assertEqual(result.files["bundle.json"], c.path.read_bytes())
            self.assertEqual(result.files["records.jsonl"], (c.path.parent / "records.jsonl").read_bytes())
            cfg = json.loads(result.files["bundle.json"])["analysis_config"]
            self.assertEqual(cfg["selection"][0]["selected_sample_ids"]["value"], EXPECTED["mixed_population"]["selected_ids"])
            self.assertEqual(len(cfg["selection"][0]["registered_positions"]["value"]), 5)
            rows = [json.loads(line) for line in result.files["records.jsonl"].splitlines()]
            self.assertEqual([r["structural_class_id"] for r in rows if r["record_type"] == "assignment"], EXPECTED["mixed_population"]["labels"])
            self.assertEqual([r["validity_status"] for r in rows if r["record_type"] == "validity"], EXPECTED["mixed_population"]["validity"])
            populations = build_populations(load_bundle(c.path)).cells[0].populations
            self.assertEqual(populations["classified_all"].count, 3)
            self.assertEqual(populations["classified_valid"].count, 1)
            direct = analyze_bundle(c.path, run_id="bridge-fixture", recorded_at=STAMP)
            compiled = bridge.analyze_compilation(result, run_id="bridge-fixture", recorded_at=STAMP)
            self.assertEqual((compiled.report_json, compiled.report_markdown, compiled.manifest_json),
                             (direct.report_json, direct.report_markdown, direct.manifest_json))
            fields = next(r["fields"] for r in result.provenance["field_map"] if r["target_record_type"] == "attempt")
            self.assertTrue(set(EXPECTED["mapping_fields"]["attempt"]) <= set(fields))

    def test_full_comparison_p1_both_p5_views_and_gates_are_identical(self):
        with TemporaryDirectory() as d:
            c = existing(d, "hero_abc", "hero_sort_abc_v1")
            result = c.compile()
            self.assertCompiled(result)
            direct = analyze_bundle(c.path, run_id="bridge-comparison", recorded_at=STAMP)
            compiled = bridge.analyze_compilation(result, run_id="bridge-comparison", recorded_at=STAMP)
            self.assertEqual(compiled.exit_code, 0)
            self.assertEqual(compiled.report_json, direct.report_json)
            self.assertEqual(compiled.report_markdown, direct.report_markdown)
            self.assertEqual(compiled.manifest_json, direct.manifest_json)
            cfg = json.loads(result.files["bundle.json"])["analysis_config"]["extensions"]["comparison"]
            self.assertEqual(cfg["questions"], ["P1", "P5"])
            self.assertEqual(cfg["views"], ["classified_all", "classified_valid"])
            self.assertEqual([b["block_id"] for b in cfg["blocks"]], [f"P{b:02d}" for b in range(1, 7)])

    def test_supplied_longitudinal_and_replay_keep_exact_results(self):
        with TemporaryDirectory() as d:
            c = existing(d, "hero_recursive", "structdet_longitudinal_v1")
            result = c.compile()
            self.assertCompiled(result)
            direct = analyze_bundle(c.path, run_id="bridge-longitudinal", recorded_at=STAMP)
            compiled = bridge.analyze_compilation(result, run_id="bridge-longitudinal", recorded_at=STAMP)
            self.assertEqual(compiled.report_json, direct.report_json)
            self.assertEqual(compiled.manifest_json, direct.manifest_json)
            replay = bridge.analyze_compilation(result, run_id="bridge-longitudinal", recorded_at=STAMP,
                                                replay_manifest_bytes=compiled.manifest_json)
            self.assertEqual(replay.exit_code, 0)
            self.assertEqual(replay.report_json, compiled.report_json)
            self.assertEqual(replay.report_markdown, compiled.report_markdown)

    def test_missing_carrier_is_explicit_gap_without_default_conversion(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            loaded = c.load()
            raw = json.loads(sr.canonical_study_bytes(loaded.packet))
            raw["records"][0]["protocol"]["legacy_profile_input"] = K(state="unknown")
            (Path(d) / "missing.json").write_bytes(encoded(raw))
            result = bridge.compile_study(sr.load_study(Path(d) / "missing.json"))
            self.assertFalse(result.compiled)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("required_legacy_fields_unrepresentable", errors(result))
            self.assertEqual(result.files, {})

    def test_wrong_identity_role_policy_pins_or_frame_cannot_override_registration(self):
        for name in ("study_id", "data_role", "source_pins", "task_context", "assignment_evidence_policy_id"):
            with self.subTest(name=name), TemporaryDirectory() as d:
                c, obs, sup, m = mixed(d)
                if name == "task_context": m["frames"][0][name] = "Contradictory task context"
                elif name == "assignment_evidence_policy_id": m["analysis_config"][name] = "adjudicated_import"
                elif name == "source_pins": m[name] = []
                else: m[name] = "another-study" if name == "study_id" else "descriptive"
                rewrite_evidence_bundle(c.path.parent, obs, sup, m)
                result = c.compile()
                self.assertFalse(result.compiled)
                self.assertEqual(result.exit_code, 2)

    def test_undeclared_record_file_is_not_read_from_original_host(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            loaded = c.load()
            raw = json.loads(sr.canonical_study_bytes(loaded.packet))
            raw["packet_inventory"] = [r for r in raw["packet_inventory"] if not r["location"]["value"]["path"].endswith("records.jsonl")]
            (Path(d) / "missing.json").write_bytes(encoded(raw))
            result = bridge.compile_study(sr.load_study(Path(d) / "missing.json"))
            self.assertFalse(result.compiled)
            self.assertTrue((c.path.parent / "records.jsonl").exists())
            self.assertEqual(result.files, {})

    def test_profile_mismatch_and_missing_longitudinal_records_never_synthesize(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            c.profile = c.registration["requested_profile"] = "structdet_longitudinal_v1"
            c.registration["protocol"]["design"] = "supplied_longitudinal"
            result = c.compile()
            self.assertFalse(result.compiled)
            self.assertIn("known_operational_fact_conflict", errors(result))

    def test_limits_and_tampered_loaded_bytes_fail_closed(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            loaded = c.load()
            result = bridge.compile_study(loaded, limits=ReadLimits(max_bundle_bytes=100))
            self.assertFalse(result.compiled)
            self.assertEqual(result.exit_code, 2)
            snapshots = dict(loaded.snapshots)
            name = next(n for n in snapshots if n.endswith("records.jsonl"))
            snapshots[name] = replace(snapshots[name], content=b"tampered")
            self.assertFalse(bridge.compile_study(replace(loaded, snapshots=freeze(snapshots))).compiled)

    def test_replay_corruption_and_absence_never_fall_back(self):
        with TemporaryDirectory() as d:
            c = existing(d, "hero_recursive", "structdet_longitudinal_v1")
            result = c.compile()
            self.assertCompiled(result)
            for raw in (b"{}", b"{", b""):
                with self.subTest(raw=raw):
                    try:
                        output = bridge.analyze_compilation(result, replay_manifest_bytes=raw)
                    except InputError:
                        pass
                    else:
                        self.assertNotEqual(output.exit_code, 0)

    def test_compiled_file_tamper_cannot_enter_engine(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            result = c.compile()
            self.assertCompiled(result)
            changed = dict(result.files)
            changed["records.jsonl"] += b"\n"
            with self.assertRaisesRegex(InputError, "compiled_snapshot_identity_mismatch"):
                bridge.analyze_compilation(replace(result, files=freeze(changed)))

    def test_two_longitudinal_carriers_must_identify_exact_compatible_input(self):
        with TemporaryDirectory() as d:
            c = existing(d, "hero_recursive", "structdet_longitudinal_v1")
            loaded = c.load()
            data = json.loads(sr.canonical_study_bytes(loaded.packet))
            original = next(r for r in data["records"] if r["record_id"] == "legacy-carrier")
            row = copy.deepcopy(original)
            content = c.path.read_bytes() + b"\n"
            (Path(d) / "other.json").write_bytes(content)
            row.update(record_id="second-carrier", content=K({"packet_id": "other"}), sha256=K(hashlib.sha256(content).hexdigest()), size_bytes=K(len(content)))
            data["records"].append(row)
            data["records"][0]["protocol"]["longitudinal_input"] = K(ref(row))
            entry = copy.deepcopy(data["packet_inventory"][0])
            entry.update(packet_id="other", location=K({"kind": "local", "path": "other.json"}), sha256=copy.deepcopy(row["sha256"]), size_bytes=copy.deepcopy(row["size_bytes"]))
            data["packet_inventory"].append(entry)
            (Path(d) / "two.json").write_bytes(encoded(data))
            result = bridge.compile_study(sr.load_study(Path(d) / "two.json"))
            self.assertFalse(result.compiled)
            self.assertIn("incompatible_longitudinal_carriers", errors(result))


class OperationalTests(unittest.TestCase):
    def test_explicit_qualified_mapping_and_exact_bytes(self):
        with TemporaryDirectory() as d:
            c, obs, sup, m, artifacts = operational(d)
            result = c.compile()
            self.assertTrue(result.compiled, result.as_dict())
            self.assertEqual(result.files["body1.txt"], c.f.packets[artifacts[0]["record_id"]])
            self.assertTrue(result.qualification["fixture_context"])
            self.assertEqual(result.provenance["claim_disposition"], "restricted")

    def test_missing_mapping_and_changed_call_fact_withhold_bundle(self):
        for change in ("mapping", "attempt", "model", "seed", "positions", "group", "extraction", "selection", "order", "denominator", "nonnumeric"):
            with self.subTest(change=change), TemporaryDirectory() as d:
                c, obs, sup, m, artifacts = operational(d)
                byid = {r["record_id"]: r for r in obs}
                if change == "mapping": c.receipt["id_map"] = []
                elif change == "attempt": byid["call1"]["attempt_status"] = "failed"
                elif change == "model": m["cells"][0]["model_identifier"] = T("other")
                elif change == "seed": m["protocols"][0]["seed"] = T(state="unknown")
                elif change == "positions": byid["call1"]["planned_candidate_count"] = T(4)
                elif change == "group": byid["s1"]["generation_group_id"] = T("other-group")
                elif change == "extraction": byid["s1"]["extraction_rule_version"] = T("repaired")
                elif change == "selection": m["analysis_config"]["selection"][0]["selected_sample_ids"]["value"].remove("s1")
                elif change == "order": m["analysis_config"]["selection"][0]["sample_order"]["value"].reverse()
                elif change == "denominator": m["analysis_config"]["selection"][0]["registered_positions"]["value"].pop()
                elif change == "nonnumeric": m["protocols"][0]["decoding_settings"]["value"]["temperature"] = "not-a-number"
                rewrite_evidence_bundle(c.path.parent, obs, sup, m)
                result = c.compile()
                self.assertFalse(result.compiled)
                self.assertEqual(result.exit_code, 2)
                self.assertEqual(list(result.provenance.get("outputs", ())), [])
                self.assertEqual(result.provenance.get("claim_disposition", "withheld"), "withheld")

    def test_stale_or_withdrawn_mechanism_cannot_enter_carrier_assignment(self):
        with TemporaryDirectory() as d:
            c, *_ = operational(d)
            c.f.evidence["evidence"][0]["state"] = "withdrawn"
            result = c.compile()
            self.assertFalse(result.compiled)
            self.assertIn("known_operational_fact_conflict", errors(result))

    def test_original_event_cannot_be_omitted_from_supplied_bundle(self):
        with TemporaryDirectory() as d:
            c, obs, sup, m, _ = operational(d)
            obs[:] = [r for r in obs if r["record_id"] not in {"s5", "a5", "v5"}]
            for axis in ("assignment", "validity"):
                m["analysis_config"][axis+"_pins"] = [p for p in m["analysis_config"][axis+"_pins"] if p["sample_id"] != "s5"]
            for key in ("selected_sample_ids", "sample_order"):
                m["analysis_config"]["selection"][0][key]["value"].remove("s5")
            c.receipt["id_map"] = [r for r in c.receipt["id_map"] if r["target_record_id"] not in {"s5", "a5"}]
            sup[:] = [r for r in sup if r["record_id"] not in {"e-a5", "e-v5"}]
            rewrite_evidence_bundle(c.path.parent, obs, sup, m)
            result = c.compile()
            self.assertFalse(result.compiled)
            self.assertIn("original_selected_position_lost", errors(result))

    def test_correction_dependency_closure_and_proposed_action_boundary(self):
        with TemporaryDirectory() as d:
            c, obs, sup, m, artifacts = operational(d)
            template = json.loads((ROOT / "tests/fixtures/phase4/study_complete.json").read_bytes())
            event = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "correction_incident"))
            event.update(record_id="challenge-current", affected_refs=[ref(artifacts[0])],
                action_status="proposed", performed_at=K(state="unknown"), replacement_refs=[], reanalysis_refs=[], rollback_refs=[], evidence_refs=[])
            c.data["records"].append(event)
            result = c.compile()
            self.assertFalse(result.compiled)
            correction = result.as_dict()["corrections"]
            self.assertIn(artifacts[0]["record_id"], correction["invalidated_record_ids"])
            self.assertIn("label-" + artifacts[0]["record_id"], correction["invalidated_record_ids"])
            self.assertEqual(correction["affected_cells"], EXPECTED["correction"]["candidate_only_cells"])
            self.assertEqual(correction["registered_comparisons_to_recompute"], EXPECTED["correction"]["candidate_only_comparisons"])
            self.assertFalse(correction["incidents"][0]["declared_performed"])
            self.assertFalse(correction["incidents"][0]["performed_record_complete"])

    def test_schema_change_invalidates_all_conditions(self):
        with TemporaryDirectory() as d:
            c, *_ = operational(d)
            template = json.loads((ROOT / "tests/fixtures/phase4/study_complete.json").read_bytes())
            event = copy.deepcopy(next(r for r in template["records"] if r["record_type"] == "correction_incident"))
            event.update(record_id="schema-challenge", affected_refs=[ref(c.registration)], action_status="proposed",
                         performed_at=K(state="unknown"), replacement_refs=[], rollback_refs=[], reanalysis_refs=[], evidence_refs=[])
            c.data["records"].append(event)
            result = c.compile()
            self.assertFalse(result.compiled)
            self.assertTrue(result.corrections["schema_review_required"])
            self.assertEqual(len(result.corrections["affected_cells"]), 18)

    def test_public_metadata_omits_reviewer_prose_and_commands(self):
        with TemporaryDirectory() as d:
            c, *_ = operational(d)
            secret = "PRIVATE-REVIEWER-CONTACT-and-command"
            c.f.notes["original_source"] = K(secret)
            result = c.compile()
            self.assertTrue(result.compiled, result.as_dict())
            self.assertNotIn(secret, json.dumps(result.as_dict()))
            self.assertNotIn(str(Path(d)), json.dumps(result.as_dict()))

    def test_failed_call_retains_five_positions_and_creates_no_realizations(self):
        with TemporaryDirectory() as d:
            f = EvidenceFixture(d)
            call = f.add_call(status="failed", attempt="failed-original")
            c = Carrier(d, existing=f)
            _, obs, sup, m = population_bundle(c.path.parent, [])
            m["study_id"] = f.data["study_id"]
            m["source_pins"] = [{"source_id": k, "sha256": v} for k, v in SOURCE_PINS.items()]
            prompt = f.row(call["prompt_ref"]["value"]["record_id"])
            (c.path.parent / "prompt.txt").write_bytes(f.packets[prompt["record_id"]])
            obs.append(artifact_record("sent-prompt", "prompt.txt"))
            obs.append({**R("attempt", "failed-original"), "attempt_id": "failed-original", "analysis_cell_id": "cell1",
                "attempt_status": "failed", "retry_of": T(None), "raw_response_ref": T(state="unknown"),
                "generation_group_id": T("G1"), "planned_candidate_count": T(5), "registered_call_order": T(1)})
            m["cells"][0].update(prompt_block_id="P01", condition_id="A", model_identifier=T("fixture-model"), model_family=T("fixture-family"))
            m["protocols"][0].update(conditioning_context_ref=T(R("artifact", "sent-prompt")), seed=T(None),
                decoding_settings=T({"temperature": 0.4, "top_p": 1, "presence_penalty": 0, "frequency_penalty": 0, "max_output_tokens": 8192}))
            m["analysis_config"]["selection"][0]["registered_positions"] = T([
                {"generation_group_id": "G1", "registered_call_order": 1, "within_group_index": i, "attempt_id": T("failed-original")} for i in range(1, 6)])
            c.mapping(call, "attempt", "failed-original")
            c.mapping(prompt, "artifact", "sent-prompt")
            rewrite_evidence_bundle(c.path.parent, obs, sup, m)
            c.bind_identity()
            result = c.compile()
            self.assertTrue(result.compiled, (errors(result), result.mapping_errors))
            rows = [json.loads(r) for r in result.files["records.jsonl"].splitlines()]
            self.assertEqual(sum(r["record_type"] == "realization" for r in rows), 0)
            self.assertEqual(json.loads(result.files["bundle.json"])["analysis_config"]["selection"][0]["registered_positions"]["value"],
                             m["analysis_config"]["selection"][0]["registered_positions"]["value"])

    def test_fresh_replacement_review_qualifies_without_erasing_old_review(self):
        with TemporaryDirectory() as d:
            c, obs, sup, m, artifacts = operational(d)
            old = c.f.row("label-" + artifacts[0]["record_id"])
            new = c.f.judge(artifacts[0], suffix="revised")
            new.update(revision=2, supersedes=K(ref(old)))
            c.f.evidence["qualifications"][0]["judgment_ref"] = K(ref(new))
            c.f.evidence["evidence"][0]["reviewer_ref"] = K(ref(new))
            for item in c.receipt["id_map"]:
                if item["source_ref"] == ref(old): item["source_ref"] = ref(new)
            result = c.compile()
            self.assertTrue(result.compiled, (errors(result), result.mapping_errors))
            self.assertIn(old["record_id"], result.corrections["invalidated_record_ids"])
            self.assertNotIn(new["record_id"], result.corrections["invalidated_record_ids"])
            self.assertIn(old, c.data["records"])
            direct = analyze_bundle(c.path, run_id="revised-fixture", recorded_at=STAMP)
            revised = bridge.analyze_compilation(result, run_id="revised-fixture", recorded_at=STAMP)
            self.assertEqual(revised.report_json, direct.report_json)
            self.assertTrue(revised.compilation_receipt["reanalysis_performed"])
            self.assertEqual(tuple(revised.compilation_receipt["pending_registered_comparisons"]), ("P1-B-vs-A", "P5-C-vs-A"))
            self.assertFalse(revised.compilation_receipt["empirical_claim_established"])

    def test_lineage_only_associations_do_not_invalidate_unrelated_evidence(self):
        with TemporaryDirectory() as d:
            c, obs, sup, m, artifacts = operational(d)
            source = c.f.artifact("lineage-source", b"Old source provenance only\n")
            source["artifact_role"] = "source"
            new = c.f.artifact("lineage-new", b"New source provenance only\n")
            new.update(artifact_role="source", revision=2, supersedes=K(ref(source)))
            artifacts[0]["lineage_refs"] = [ref(source)]
            result = c.compile()
            self.assertTrue(result.compiled, (errors(result), result.mapping_errors))
            self.assertIn(source["record_id"], result.corrections["invalidated_record_ids"])
            self.assertNotIn(artifacts[0]["record_id"], result.corrections["invalidated_record_ids"])

    def test_carrier_bytes_never_execute_submitted_code(self):
        with TemporaryDirectory() as d:
            c, *_ = mixed(d)
            loaded = c.load()
            with patch("subprocess.run", side_effect=AssertionError("candidate execution forbidden")), \
                 patch("builtins.eval", side_effect=AssertionError("candidate evaluation forbidden")):
                result = bridge.compile_study(loaded)
            self.assertTrue(result.compiled, (errors(result), result.mapping_errors))

    def test_over_budget_records_restrict_claim_without_erasing_observations(self):
        with TemporaryDirectory() as d:
            c, *_ = operational(d)
            c.registration["protocol"]["budget"].update(max_calls=K(0), max_positions=K(0))
            result = c.compile()
            self.assertTrue(result.compiled, (errors(result), result.mapping_errors))
            self.assertIn("registered_budget_exceeded", result.provenance["scope_restrictions"])
            self.assertEqual(result.provenance["claim_disposition"], "restricted")
            self.assertEqual(sum(json.loads(r)["record_type"] == "realization" for r in result.files["records.jsonl"].splitlines()), 5)

    def test_failed_retry_is_retained_without_allocating_new_main_positions(self):
        with TemporaryDirectory() as d:
            c, obs, sup, m, _ = operational(d)
            original = next(r for r in c.data["records"] if r["record_type"] == "collection_ledger")
            retry = c.f.add_call("retry-call", status="failed", attempt="retry-attempt")
            retry.update(retry_of=K(ref(original)), prompt_ref=copy.deepcopy(original["prompt_ref"]),
                         sent_prompt_sha256=copy.deepcopy(original["sent_prompt_sha256"]))
            obs.append({**R("attempt", "retry-attempt"), "attempt_id": "retry-attempt", "analysis_cell_id": "cell1",
                "attempt_status": "failed", "retry_of": T("call1"), "raw_response_ref": T(state="unknown"),
                "generation_group_id": T("retry-G"), "planned_candidate_count": T(5), "registered_call_order": T(1)})
            c.mapping(retry, "attempt", "retry-attempt")
            rewrite_evidence_bundle(c.path.parent, obs, sup, m)
            result = c.compile()
            self.assertTrue(result.compiled, (errors(result), result.mapping_errors))
            rows = [json.loads(r) for r in result.files["records.jsonl"].splitlines()]
            self.assertEqual(sum(r["record_type"] == "attempt" for r in rows), 2)
            self.assertEqual(sum(r["record_type"] == "realization" for r in rows), 5)
            self.assertEqual(len(json.loads(result.files["bundle.json"])["analysis_config"]["selection"][0]["registered_positions"]["value"]), 5)

    def test_comparison_binding_preserves_requested_actual_cap_and_global_order(self):
        for change in (None, "requested", "cap", "global_order", "history"):
            with self.subTest(change=change), TemporaryDirectory() as d:
                f = EvidenceFixture(d)
                call = f.add_call(attempt="call-P01-A-1", timestamp="2026-09-01T01:00:00+00:00")
                c = Carrier(d, "hero_sort_abc_v1", f)
                _, obs, sup, m = comparison_fixture(c.path.parent)
                m["study_id"] = f.data["study_id"]
                m["source_pins"] = [{"source_id": k, "sha256": v} for k, v in SOURCE_PINS.items()]
                call["deployment"].update(model_identifier=K("MOCK-MODEL"), model_family=K("MOCK-FAMILY"),
                    checkpoint_identifier=K("MOCK-STATE"), deployment_identifier=K("MOCK-DEPLOYMENT"))
                call["controls"]["cap_semantics"] = K("visible_output_only")
                packet = f.submissions[call["record_id"]]
                packet["requested_controls"] = copy.deepcopy(call["controls"])
                packet["cap"].update(tokenizer=K("MOCK-TOKENIZER"), convention=K("visible_output_only"))
                c.mapping(call, "attempt", "call-P01-A-1")
                c.mapping(f.row(call["prompt_ref"]["value"]["record_id"]), "artifact", "prompt-P01-A")
                old_binding = next(s for s in sup if s["record_id"] == "study-P01-A")["payload"]["extensions"]["study_binding"]
                if change == "requested": packet["requested_controls"]["temperature"] = K("0.5")
                elif change == "cap": packet["cap"]["tokenizer"] = K("another-tokenizer")
                elif change == "global_order": call["attempted_at"] = K("2026-09-01T01:00:01+00:00")
                elif change == "history": packet["context"]["previous_outputs_supplied"] = K(True)
                # All 20 positions remain in the old cell even though no sample
                # was emitted. They were not present in the empty helper's plan.
                selected = m["analysis_config"]["selection"][0]
                selected["registered_positions"] = T([{"generation_group_id": f"group-P01-A-{g}",
                    "registered_call_order": g, "within_group_index": n, "attempt_id": T(f"call-P01-A-{g}")}
                    for g in range(1, 5) for n in range(1, 6)])
                rewrite_evidence_bundle(c.path.parent, obs, sup, m)
                c.bind_identity()
                c.registration["protocol"]["budget"].update(max_calls=K(72), max_positions=K(360), max_output_tokens=K(589824))
                result = c.compile()
                if change is None:
                    self.assertTrue(result.compiled, (errors(result), result.mapping_errors))
                else:
                    self.assertFalse(result.compiled)
                    self.assertIn("known_operational_fact_conflict", errors(result))


if __name__ == "__main__":
    unittest.main()
