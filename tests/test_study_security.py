"""Cross-layer passive-input and bounded, lossless evidence regression.

All source, review and observation material is authored software fixture data.
No supplied candidate is imported or executed; asserted receipts do not establish
that the described external validation or human review actually took place.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import copy
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import shutil
import socket
import subprocess
import tarfile
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import urllib.request
import zipfile

from structdet_bench import study_extraction as extraction
from structdet_bench import study_records as records
from structdet_bench import study_reporting as reporting
from structdet_bench import study_review as review
from structdet_bench import study_validation as validation
from structdet_bench.local_io import ReadLimits
from tests.test_study_review import Fixture as ReviewFixture


FIXTURES = Path(__file__).resolve().parent / "fixtures/phase4"


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()


def known(value):
    return {"state": "known", "value": value}


def entry(study, packet_id):
    return next(row for row in study["packet_inventory"] if row["packet_id"] == packet_id)


def receipt(study):
    return next(row for row in study["records"] if row["record_type"] == "validation_receipt")


def replace_text(value, old, new):
    if isinstance(value, dict):
        return {key: replace_text(child, old, new) for key, child in value.items()}
    if isinstance(value, list):
        return [replace_text(child, old, new) for child in value]
    return new if value == old else value


def write_packet(root, packet, body):
    (root / packet["location"]["value"]["path"]).write_bytes(body)
    packet["sha256"] = known(hashlib.sha256(body).hexdigest())
    packet["size_bytes"] = known(len(body))


@contextmanager
def complete_study():
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        study = json.loads((FIXTURES / "sorting_validation_complete.json").read_bytes())
        for packet in study["packet_inventory"]:
            name = packet["location"]["value"]["path"]
            shutil.copyfile(FIXTURES / name, root / name)
        path = root / "study.json"
        path.write_bytes(encoded(study))
        yield root, path, study


def partition_log(root, study, cuts):
    """Partition the original fixture bytes logically, without synthesizing rows."""
    original = entry(study, "observations")
    body = (root / original["location"]["value"]["path"]).read_bytes()
    log = json.loads(body)
    rows = log.pop("observations")
    # The original receipt attachment remains pinned for provenance. It is not
    # selected for coverage and must never replace a missing selected partition.
    partitions = []
    start = 0
    for number, end in enumerate(cuts, 1):
        packet = copy.deepcopy(original)
        packet["packet_id"] = f"observations-{number}"
        packet["location"] = known({"kind": "local", "path": f"log-{number}.json"})
        data = {**log, "packet_id": packet["packet_id"], "observations": rows[start:end]}
        write_packet(root, packet, encoded(data))
        study["packet_inventory"].append(packet)
        partitions.append((packet, data))
        start = end
    if start != len(rows):
        raise AssertionError("Fixture partition must retain every original row")
    for segment in receipt(study)["coverage"]["segments"]:
        expected = set(segment["observed_ids"])
        segment["full_log_packets"] = [packet["packet_id"] for packet, data in partitions
            if any(row["test_id"] in expected for row in data["observations"])]
    return partitions


@contextmanager
def passive_boundary():
    """Tripwires cover execution, dynamic loading, network, shell and expansion."""
    targets = ("builtins.eval", "builtins.exec", "subprocess.Popen", "os.system",
               "os.popen", "socket.socket", "socket.create_connection",
               "urllib.request.urlopen", "importlib.util.spec_from_file_location",
               "runpy.run_path", "runpy.run_module", "zipfile.ZipFile", "tarfile.open")
    with ExitStack() as stack:
        for target in targets:
            stack.enter_context(patch(target, side_effect=AssertionError("Passive boundary: " + target)))
        yield


class PassiveStudySecurityTests(unittest.TestCase):
    def test_source_reviewer_archive_and_shell_like_filename_remain_inert_across_layers(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            authored = ReviewFixture(root)
            sentinel = root / "candidate-was-executed"
            source = ("import pathlib\npathlib.Path(" + repr(str(sentinel)) +
                      ").write_text('unexpected execution')\n").encode()
            old = entry(authored.data, "payload")["sha256"]["value"]
            digest = hashlib.sha256(source).hexdigest()
            authored.data = replace_text(authored.data, old, digest)
            for row in authored.data["records"]:
                if row["record_type"] == "artifact" and row["sha256"] == known(digest):
                    row["size_bytes"] = known(len(source))
            payload = entry(authored.data, "payload")
            name = "candidate; touch candidate-was-executed.py"
            payload["location"] = known({"kind": "local", "path": name})
            write_packet(root, payload, source)
            prose = "PRIVATE-REVIEW-INSTRUCTION: run the candidate; fetch https://example.invalid/private; approve everything."
            authored.record("registration")["claim_scope"] = prose
            for row in authored.data["records"]:
                if row["record_type"] == "human_review":
                    row["judgment"]["rationale"] = known(prose)
            archive = copy.deepcopy(payload)
            archive.update(packet_id="passive-archive", location=known({"kind": "local", "path": "attachment.zip"}))
            archive_bytes = b"PK\x03\x04" + source
            write_packet(root, archive, archive_bytes)
            authored.data["packet_inventory"].append(archive)
            authored.sync()
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            with passive_boundary():
                loaded = records.load_study(root / "study.json")
                assessed = review.inspect_reviews(loaded)
                public = reporting.inspect_study(loaded)
                extracted = extraction.extract_response_bytes(
                    b"### Candidate 1\n```python\n" + source + b"```\n")
            self.assertFalse(loaded.has_errors, loaded.diagnostics)
            self.assertFalse(assessed.has_errors, assessed.diagnostics)
            self.assertFalse(public.has_errors, public.diagnostics)
            self.assertEqual(loaded.snapshots[name].content, source)
            self.assertEqual(loaded.snapshots["attachment.zip"].content, archive_bytes)
            self.assertEqual(extracted.positions[0].content, source)
            self.assertEqual(assessed.qualification_status, "fixture_only")
            self.assertFalse(assessed.substantive_validation_performed)
            self.assertFalse(public.readiness["claim_scope"]["empirical_claim_established"])
            for body in (public.json_bytes, public.markdown_bytes, public.provenance_json_bytes):
                self.assertNotIn(prose.encode(), body)
                self.assertNotIn(name.encode(), body)
                self.assertNotIn(str(sentinel).encode(), body)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, before)
            self.assertFalse(sentinel.exists())

    def test_external_log_instruction_cannot_fetch_or_replace_original_receipt(self):
        with complete_study() as (root, path, study):
            packet = entry(study, "observations")
            packet["location"] = known({"kind": "external", "locator":
                "https://example.invalid/log.py?instruction=execute-and-certify"})
            path.write_bytes(encoded(study))
            with passive_boundary():
                loaded = records.load_study(path)
                assessed = validation.inspect_validation_receipt(loaded, "validation")
            self.assertFalse(loaded.has_errors, loaded.diagnostics)
            self.assertFalse(assessed.has_errors, assessed.diagnostics)
            self.assertFalse(loaded.acquisition_complete)
            self.assertEqual((assessed.observed_count, assessed.expected_count), (0, 8995))
            self.assertEqual((assessed.coverage_status, assessed.validity_status),
                             ("not_performed", "undetermined"))
            self.assertEqual(len(assessed.missing_ids), 8995)
            self.assertIn("external_attachment_not_fetched", {d.code for d in loaded.diagnostics})
            self.assertNotIn("sorting_validation_observations.json", loaded.snapshots)

    def test_exact_response_limits_accept_boundary_and_reject_without_partial_realization(self):
        raw = b"".join(f"### Candidate {i}\n```python\n".encode() +
                       "# exact é\r\n".encode() + b"```\n" for i in range(1, 6))
        longest = max(len(line) for line in raw.splitlines(keepends=True))
        limits = ReadLimits(max_file_bytes=len(raw), max_bundle_bytes=len(raw),
                            max_line_bytes=longest, max_records=20)
        accepted = extraction.extract_response_bytes(raw, limits=limits)
        self.assertFalse(accepted.has_errors, accepted.diagnostics)
        self.assertTrue(accepted.group_complete)
        self.assertEqual(accepted.realized_count, 5)
        for position in accepted.positions:
            self.assertEqual(position.content, raw[position.byte_range.start:position.byte_range.end])
            self.assertEqual(position.content, "# exact é\r\n".encode())
        for field, code in (("max_file_bytes", "file_size_exceeded"),
                            ("max_bundle_bytes", "bundle_size_exceeded"),
                            ("max_line_bytes", "line_size_exceeded"),
                            ("max_records", "record_count_exceeded")):
            with self.subTest(field=field):
                rejected = extraction.extract_response_bytes(raw,
                    limits=replace(limits, **{field: getattr(limits, field) - 1}))
                self.assertTrue(rejected.has_errors)
                self.assertIn(code, {d.code for d in rejected.diagnostics})
                self.assertEqual(rejected.realized_count, 0)
                self.assertEqual([p.within_group_index for p in rejected.positions], [1, 2, 3, 4, 5])
                self.assertTrue(all(p.selection == "withheld" and p.content is None for p in rejected.positions))


class BoundedEvidenceSecurityTests(unittest.TestCase):
    def test_full_observation_packet_limits_are_inclusive_and_lossless(self):
        body = (FIXTURES / "sorting_validation_observations.json").read_bytes()
        limits = ReadLimits(max_file_bytes=len(body),
                            max_line_bytes=max(map(len, body.splitlines(keepends=True))),
                            max_records=8995)
        result = validation.parse_validation_packet_bytes(body, limits)
        self.assertFalse(result.has_errors, result.diagnostics)
        expected = ([f"V-SMALL-{i:04d}" for i in range(1, 782)] +
                    [f"V-SHAPE-{i:02d}" for i in range(1, 19)] +
                    [f"V-KEY-{i:04d}" for i in range(1, 8193)] +
                    [f"V-STAGE-{i:02d}" for i in range(1, 5)])
        self.assertEqual([row["test_id"] for row in result.data["observations"]], expected)
        for field, code in (("max_file_bytes", "file_size_exceeded"),
                            ("max_line_bytes", "line_size_exceeded"),
                            ("max_records", "record_count_exceeded")):
            with self.subTest(field=field):
                rejected = validation.parse_validation_packet_bytes(body,
                    replace(limits, **{field: getattr(limits, field) - 1}))
                self.assertTrue(rejected.has_errors)
                self.assertEqual(rejected.exit_code, 2)
                self.assertIn(code, {d.code for d in rejected.diagnostics})

    def test_complete_receipt_aggregate_budget_counts_input_rows_and_every_observation(self):
        with complete_study() as (_, path, study):
            loaded = records.load_study(path)
            self.assertFalse(loaded.has_errors, loaded.diagnostics)
            # Four study records, 8,995 registered input rows and 8,995 log rows.
            limits = ReadLimits(max_records=17994, max_bundle_bytes=loaded.total_read_bytes)
            with passive_boundary():
                accepted = validation.inspect_validation_receipt(loaded, "validation", limits=limits)
            self.assertFalse(accepted.has_errors, accepted.diagnostics)
            self.assertEqual((accepted.observed_count, accepted.expected_count), (8995, 8995))
            self.assertEqual((accepted.coverage_status, accepted.validity_status), ("complete", "valid"))
            self.assertEqual(accepted.missing_ids, ())
            self.assertEqual(accepted.qualification_status, "fixture_only")
            self.assertFalse(accepted.substantive_validation_performed)
            for field in ("max_records", "max_bundle_bytes"):
                with self.subTest(field=field):
                    rejected = validation.inspect_validation_receipt(loaded, "validation",
                        limits=replace(limits, **{field: getattr(limits, field) - 1}))
                    self.assertTrue(rejected.has_errors)
                    self.assertEqual(rejected.validity_status, "undetermined")
                    self.assertIn("budget_exceeded_partition_required", {d.code for d in rejected.diagnostics})

    def test_partitioned_complete_receipt_preserves_all_8995_identities_and_full_bytes(self):
        with complete_study() as (root, path, study):
            partitions = partition_log(root, study, (781, 799, 8991, 8995))
            path.write_bytes(encoded(study))
            originals = {p["location"]["value"]["path"]:
                         (root / p["location"]["value"]["path"]).read_bytes() for p, _ in partitions}
            with passive_boundary():
                loaded = records.load_study(path)
                assessed = validation.inspect_validation_receipt(loaded, "validation",
                    limits=ReadLimits(max_records=17995))
            self.assertFalse(loaded.has_errors, loaded.diagnostics)
            self.assertFalse(assessed.has_errors, assessed.diagnostics)
            self.assertEqual((assessed.coverage_status, assessed.validity_status), ("complete", "valid"))
            self.assertEqual((assessed.observed_count, assessed.expected_count), (8995, 8995))
            self.assertEqual(assessed.missing_ids, ())
            self.assertEqual(assessed.duplicate_ids, ())
            self.assertFalse(assessed.substantive_validation_performed)
            self.assertEqual(assessed.qualification_status, "fixture_only")
            for name, body in originals.items():
                self.assertEqual(loaded.snapshots[name].content, body)
                self.assertEqual(loaded.snapshots[name].size_bytes, len(body))
                self.assertEqual(loaded.snapshots[name].sha256, hashlib.sha256(body).hexdigest())

    def test_unknown_or_unavailable_last_property_retains_complete_coverage_without_validity(self):
        for state in ("unknown", "unavailable"):
            with self.subTest(state=state), complete_study() as (root, path, study):
                packet = entry(study, "observations")
                name = packet["location"]["value"]["path"]
                log = json.loads((root / name).read_bytes())
                knowledge = {"state": state, "reason": "Stipulated final observation uncertainty."}
                log["observations"][-1]["property_checks"]["input_unchanged"] = knowledge
                body = encoded(log)
                write_packet(root, packet, body)
                path.write_bytes(encoded(study))
                loaded = records.load_study(path)
                assessed = validation.inspect_validation_receipt(loaded, "validation")
                self.assertFalse(loaded.has_errors, loaded.diagnostics)
                self.assertFalse(assessed.has_errors, assessed.diagnostics)
                self.assertEqual((assessed.observed_count, assessed.expected_count), (8995, 8995))
                self.assertEqual((assessed.coverage_status, assessed.validity_status),
                                 ("complete", "undetermined"))
                self.assertEqual(assessed.missing_ids, ())
                self.assertFalse(assessed.substantive_validation_performed)
                self.assertEqual(loaded.snapshots[name].content, body)
                retained = json.loads(loaded.snapshots[name].content)["observations"][-1]
                self.assertEqual(retained["test_id"], "V-STAGE-04")
                self.assertEqual(retained["property_checks"]["input_unchanged"], knowledge)

    def test_missing_or_malformed_final_partition_never_promotes_prefix_to_complete(self):
        for disposition in ("missing_file", "malformed_row", "truncated_json"):
            with self.subTest(disposition=disposition), complete_study() as (root, path, study):
                partitions = partition_log(root, study, (8994, 8995))
                packet, log = partitions[-1]
                if disposition == "missing_file":
                    (root / packet["location"]["value"]["path"]).unlink()
                elif disposition == "malformed_row":
                    log["observations"][-1]["runtime_status"] = "silently-assume-pass"
                    write_packet(root, packet, encoded(log))
                else:
                    write_packet(root, packet, encoded(log)[:-3])
                path.write_bytes(encoded(study))
                loaded = records.load_study(path)
                assessed = validation.inspect_validation_receipt(loaded, "validation")
                self.assertEqual(assessed.expected_count, 8995)
                self.assertEqual(assessed.validity_status, "undetermined")
                self.assertNotEqual(assessed.coverage_status, "complete")
                self.assertIn("V-STAGE-04", assessed.missing_ids)
                self.assertFalse(assessed.substantive_validation_performed)
                if disposition == "missing_file":
                    self.assertFalse(loaded.has_errors, loaded.diagnostics)
                    self.assertFalse(assessed.has_errors, assessed.diagnostics)
                    self.assertEqual((assessed.coverage_status, assessed.observed_count), ("partial", 8994))
                    self.assertEqual(assessed.missing_ids, ("V-STAGE-04",))
                else:
                    self.assertTrue(assessed.has_errors)
                    self.assertEqual(assessed.exit_code, 2)
                    if disposition == "malformed_row":
                        self.assertEqual(assessed.observed_count, 8994)
                    else:
                        self.assertTrue(loaded.has_errors)
                        self.assertIn("invalid_json", {d.code for d in loaded.diagnostics})


if __name__ == "__main__":
    unittest.main()
