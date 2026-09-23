"""Offline command boundaries, transactional publication, and fixture workflow.

All records and programs below are synthetic passive input. No candidate runs.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import stat
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import cli, study_cli as study
from structdet_bench.contracts import InputError, freeze
from structdet_bench.local_io import PublicationError, _rename_noreplace
from tests.helpers import ROOT
from tests.test_study_bridge import mixed
from tests.test_study_review import Fixture


FIXTURES = ROOT / "tests/fixtures/phase4"


def command(arguments):
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = cli.main(arguments)
        except SystemExit as exc:
            code = exc.code
    return code, stdout.getvalue(), stderr.getvalue()


def files_in(directory):
    return sorted(p.relative_to(directory).as_posix() for p in Path(directory).rglob("*") if p.is_file())


def output_bytes():
    return {name: b"{}\n" for name in study.SIDECARS} | {"bundle.json": b"{}\n", "nested/records.jsonl": b"{}\n", "nested/deeper/code.py": b"raise RuntimeError('never execute fixture')\n"}


class PublicationTests(unittest.TestCase):
    def test_private_nested_exact_bytes_and_no_clobber(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            payload = output_bytes()
            destination = root / "output"
            study.publish_study_output(destination, payload, study_path=source / "study.json")
            self.assertEqual(files_in(destination), sorted(payload))
            for name, content in payload.items():
                self.assertEqual((destination / name).read_bytes(), content)
                self.assertEqual(stat.S_IMODE((destination / name).stat().st_mode), 0o600)
            for path in [destination, *[p for p in destination.rglob("*") if p.is_dir()]]:
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700)
            with self.assertRaisesRegex(InputError, "output_already_exists"):
                study.publish_study_output(destination, payload, study_path=source / "study.json")
            self.assertEqual(files_in(destination), sorted(payload))

    def test_invalid_inventory_paths_and_file_directory_collisions_never_stage(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            cases = [({"study_readiness.json": b"{}"}, "invalid_study_output_inventory"),
                (output_bytes() | {"../escape": b"secret"}, "unsafe_local_path"),
                (output_bytes() | {"https://private.example/secret": b"secret"}, "remote_or_drive_path"),
                (output_bytes() | {"nested": b"conflict"}, "study_output_path_collision"),
                (output_bytes() | {"bad\\path": b"secret"}, "unsafe_local_path")]
            for payload, error in cases:
                with self.subTest(error=error):
                    with self.assertRaisesRegex(InputError, error):
                        study.publish_study_output(root / "output", payload, study_path=root / "source/study.json")
                    self.assertEqual(list(root.iterdir()), [])

    def test_output_inside_input_and_symlink_ancestors_are_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source, external = root / "source", root / "external"
            source.mkdir()
            external.mkdir()
            (root / "linked").symlink_to(external, target_is_directory=True)
            for destination, error in [(source / "result", "output_overlaps_input_study"),
                                        (root / "linked/result", "unsafe_or_unreadable_bundle_root")]:
                with self.subTest(error=error):
                    with self.assertRaisesRegex(InputError, error):
                        study.publish_study_output(destination, output_bytes(), study_path=source / "study.json")
            self.assertEqual(list(source.iterdir()), [])
            self.assertEqual(list(external.iterdir()), [])

    def test_competing_output_created_at_commit_is_retained(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            def competing(parent, old, new):
                os.mkdir(new, dir_fd=parent)
                fd = os.open(new + "/competitor.txt", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=parent)
                os.write(fd, b"preserve competing writer")
                os.close(fd)
                return _rename_noreplace(parent, old, new)
            with patch.object(study, "_rename_noreplace", side_effect=competing):
                with self.assertRaisesRegex(InputError, "output_already_exists"):
                    study.publish_study_output(root / "output", output_bytes(), study_path=root / "source/study.json")
            self.assertEqual(list(root.iterdir()), [root / "output"])
            self.assertEqual(files_in(root / "output"), ["competitor.txt"])
            self.assertEqual((root / "output/competitor.txt").read_bytes(), b"preserve competing writer")

    def test_write_failure_and_interrupt_remove_only_uncommitted_stage(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unrelated.txt").write_bytes(b"preserve")
            original = os.write
            for failure in [OSError("private-token"), KeyboardInterrupt()]:
                calls = 0
                def fail_after_write(fd, content):
                    nonlocal calls
                    calls += 1
                    if calls == 3:
                        raise failure
                    return original(fd, content)
                with self.subTest(failure=type(failure).__name__), patch.object(study.os, "write", side_effect=fail_after_write):
                    with self.assertRaises((PublicationError, KeyboardInterrupt)):
                        study.publish_study_output(root / "output", output_bytes(), study_path=root / "source/study.json")
                self.assertEqual(list(root.iterdir()), [root / "unrelated.txt"])
                self.assertEqual((root / "unrelated.txt").read_bytes(), b"preserve")

    def test_postcommit_flush_failure_preserves_complete_output(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            original = os.fsync
            def flush(fd):
                if (root / "output").is_dir():
                    raise OSError("private storage error")
                return original(fd)
            with patch.object(study.os, "fsync", side_effect=flush):
                with self.assertRaisesRegex(PublicationError, "published_durability_unconfirmed"):
                    study.publish_study_output(root / "output", output_bytes(), study_path=root / "source/study.json")
            self.assertEqual(files_in(root / "output"), sorted(output_bytes()))
            self.assertFalse(any(p.name.startswith(".structdet-study-") for p in root.iterdir()))


class CommandTests(unittest.TestCase):
    def test_existing_parser_routes_and_argument_errors_remain_private(self):
        for arguments in [[], ["--version"], ["study"], ["study", "--help"]]:
            with self.subTest(arguments=arguments):
                code, out, err = command(arguments)
                self.assertEqual(code, 0)
                self.assertTrue(out)
                self.assertEqual(err, "")
        with patch("structdet_bench.pipeline.validate_bundle", return_value=({"fixture": True}, 0)) as validation:
            code, out, err = command(["validate", "--bundle", "original.json"])
            self.assertEqual((code, json.loads(out), err), (0, {"fixture": True}, ""))
            validation.assert_called_once_with("original.json")
        parsed = cli.build_parser().parse_args(["analyze", "--bundle", "original.json", "--output-dir", "new", "--replay-manifest", "replay.json"])
        self.assertEqual((parsed.command, parsed.bundle, parsed.output_dir, parsed.replay_manifest), ("analyze", "original.json", "new", "replay.json"))
        for arguments in [["study", "inspect", "--study", "token-secret", "--unexpected", "token-secret"],
                          ["study", "export-review", "--study", "token-secret"],
                          ["study", "prepare", "--stu", "token-secret"]]:
            code, out, err = command(arguments)
            self.assertEqual(code, 2)
            self.assertNotIn("token-secret", out + err)

    def test_inspect_is_deterministic_readonly_and_bounded_on_malformed_input(self):
        source = FIXTURES / "study_partial.json"
        first = command(["study", "inspect", "--study", str(source)])
        second = command(["study", "inspect", "--study", str(source)])
        self.assertEqual(first, second)
        self.assertEqual(first[0], 0)
        self.assertIsInstance(json.loads(first[1]), dict)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            private = root / "credential-secret.json"
            private.write_text('{"secret":"credential-secret",broken', encoding="utf-8")
            code, out, err = command(["study", "inspect", "--study", str(private)])
            self.assertEqual(code, 2)
            self.assertNotIn("credential-secret", out + err)
            self.assertNotIn(str(root), out + err)
            self.assertLess(len(out) + len(err), 1024 * 1024)
            self.assertEqual(list(root.iterdir()), [private])

    def test_partial_prepare_requires_explicit_readiness_only_and_has_four_sidecars(self):
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "output"
            args = ["study", "prepare", "--study", str(FIXTURES / "study_partial.json"), "--output-dir", str(destination)]
            code, out, err = command(args)
            self.assertEqual(code, 2)
            self.assertIn("compilation_withheld", err)
            self.assertFalse(destination.exists())
            code, out, err = command(args + ["--readiness-only"])
            self.assertEqual((code, err), (0, ""))
            self.assertEqual(files_in(destination), sorted(study.SIDECARS))
            self.assertFalse(json.loads(out)["analysis_bundle_created"])
            self.assertFalse(json.loads((destination / "compilation_manifest.json").read_bytes())["analysis_bundle_created"])

    def test_malformed_input_never_publishes_even_readiness_only(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "study.json").write_bytes(b'{"private":"credential-secret",broken')
            code, out, err = command(["study", "prepare", "--study", str(source / "study.json"),
                "--output-dir", str(root / "output"), "--readiness-only"])
            self.assertEqual(code, 2)
            self.assertNotIn("credential-secret", out + err)
            self.assertFalse((root / "output").exists())

    def test_eligible_prepare_exact_payload_then_explicit_readiness_only(self):
        from structdet_bench.study_reporting import inspect_study
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            carrier, *_ = mixed(source)
            assessed = inspect_study(carrier.load())
            self.assertFalse(assessed.has_errors)
            source_before = {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()}
            args = ["study", "prepare", "--study", str(source / "study.json")]
            code, out, err = command(args + ["--output-dir", str(root / "prepared")])
            self.assertEqual((code, err), (0, ""))
            self.assertTrue(json.loads(out)["analysis_bundle_created"])
            ready = json.loads((root / "prepared/study_readiness.json").read_bytes())
            self.assertTrue(ready["compilation"]["analysis_bundle_created"])
            self.assertTrue(ready["publication"]["analysis_bundle_created"])
            self.assertIn('"analysis_bundle_created": true', (root / "prepared/study_readiness.md").read_text())
            self.assertEqual(files_in(root / "prepared"), sorted(set(assessed.compilation.files) | study.SIDECARS))
            for name, content in assessed.compilation.files.items():
                self.assertEqual((root / "prepared" / name).read_bytes(), content)
            code, out, err = command(args + ["--output-dir", str(root / "ready"), "--readiness-only"])
            self.assertEqual((code, err), (0, ""))
            self.assertEqual(files_in(root / "ready"), sorted(study.SIDECARS))
            self.assertFalse(json.loads(out)["analysis_bundle_created"])
            ready = json.loads((root / "ready/study_readiness.json").read_bytes())
            self.assertFalse(ready["compilation"]["analysis_bundle_created"])
            self.assertFalse(ready["publication"]["analysis_bundle_created"])
            self.assertEqual({p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()}, source_before)

    def test_carrier_name_sidecar_collision_and_changed_snapshot_withhold_publication(self):
        from structdet_bench.study_reporting import inspect_study
        with TemporaryDirectory() as directory:
            carrier, *_ = mixed(directory)
            assessed = inspect_study(carrier.load())
            original = assessed.compilation
            for compilation, expected in [
                (replace(original, bundle_path="source.json", files=freeze({"source.json": original.files["bundle.json"]})), "compilation_bundle_name_unrepresentable"),
                (replace(original, files=freeze(dict(original.files) | {"study_readiness.json/private.json": b"{}"})), "compilation_sidecar_name_collision"),
                (replace(original, files=freeze(dict(original.files) | {"records.jsonl": b"tampered\n"})), "compiled_snapshot_identity_mismatch")]:
                with self.subTest(expected=expected):
                    changed = replace(assessed, compilation=compilation)
                    with self.assertRaisesRegex(InputError, expected):
                        study.preparation_files(changed)
                    files, created = study.preparation_files(changed, readiness_only=True)
                    self.assertFalse(created)
                    self.assertEqual(set(files), study.SIDECARS)

    def test_review_export_preserves_blind_mapping_and_drops_private_paths_from_stdout(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            fixture = Fixture(source)
            artifact_id = fixture.record("review-initial-a")["artifact_ref"]["record_id"]
            args = ["study", "export-review", "--study", str(source / "study.json"), "--artifact-id", artifact_id,
                "--output-dir", str(root / "public"), "--restricted-output-dir", str(root / "restricted"),
                "--pack-id", "pack-" + "a" * 32]
            code, out, err = command(args)
            self.assertEqual((code, err), (0, ""))
            result = json.loads(out)
            self.assertEqual(result["public_publication_status"], "completed")
            self.assertEqual(result["restricted_publication_status"], "completed")
            self.assertNotIn(str(root), out)
            self.assertNotIn(artifact_id, out)
            public = json.loads((root / "public/review_instructions.json").read_bytes())
            mapping = json.loads((root / "restricted/restricted_map.json").read_bytes())
            self.assertEqual(public["pack_id"], mapping["pack_id"])
            self.assertEqual(public["items"][0]["item_id"], mapping["items"][0]["item_id"])
            self.assertEqual(mapping["items"][0]["artifact_id"], artifact_id)
            self.assertEqual(stat.S_IMODE((root / "restricted/restricted_map.json").stat().st_mode), 0o600)
            original_mapping = (root / "restricted/restricted_map.json").read_bytes()
            code, out, err = command(args)
            self.assertEqual(code, 2)
            failure = json.loads(err)
            self.assertEqual(failure["public_publication_status"], "not_started")
            self.assertEqual(failure["restricted_publication_status"], "not_started")
            self.assertEqual((root / "restricted/restricted_map.json").read_bytes(), original_mapping)

    def test_review_preflight_input_overlap_and_partial_transaction_states(self):
        from structdet_bench import study_review
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            fixture = Fixture(source)
            artifact_id = fixture.record("review-initial-a")["artifact_ref"]["record_id"]
            base = ["study", "export-review", "--study", str(source / "study.json"), "--artifact-id", artifact_id]
            code, out, err = command(base + ["--output-dir", str(source / "public"), "--restricted-output-dir", str(root / "restricted")])
            self.assertEqual(code, 2)
            self.assertFalse((root / "restricted").exists())
            self.assertFalse((source / "public").exists())
            real_publish = study_review._publish
            def fail_public(target, parent, files, private):
                if not private:
                    raise OSError("credential-secret")
                return real_publish(target, parent, files, private)
            with patch.object(study_review, "_publish", side_effect=fail_public):
                code, out, err = command(base + ["--output-dir", str(root / "public"), "--restricted-output-dir", str(root / "restricted")])
            self.assertEqual(code, 3)
            result = json.loads(err)
            self.assertEqual(result["restricted_publication_status"], "completed")
            self.assertEqual(result["public_publication_status"], "may_have_completed")
            self.assertNotIn("credential-secret", out + err)
            self.assertNotIn(str(root), out + err)
            self.assertFalse((root / "public").exists())
            self.assertTrue((root / "restricted/restricted_map.json").is_file())

    def test_unexpected_failure_and_interruption_have_bounded_public_diagnostics(self):
        args = ["study", "inspect", "--study", "credential-secret.json"]
        for failure in [RuntimeError("credential-secret"), KeyboardInterrupt()]:
            with self.subTest(failure=type(failure).__name__), patch.object(study, "load_study", side_effect=failure):
                code, out, err = command(args)
                self.assertEqual(code, 3)
                self.assertNotIn("credential-secret", out + err)
                self.assertLess(len(err), 512)

    def test_seven_documented_examples_match_exact_cli_outcomes_and_inventories(self):
        root = ROOT / "examples/phase4/offline"
        manifest = json.loads((root / "manifest.json").read_bytes())
        self.assertEqual(len(manifest["cases"]), 7)
        with TemporaryDirectory() as directory:
            outputs = Path(directory)
            for case in manifest["cases"]:
                source = root / case["study_path"]
                for operation in ("inspect", "prepare", "prepare_readiness_only"):
                    expected = case["operations"][operation]
                    destination = outputs / (case["case_id"] + "-" + operation)
                    args = ["study", "inspect" if operation == "inspect" else "prepare", "--study", str(source), *case["extra_options"]]
                    if operation != "inspect":
                        args.extend(["--output-dir", str(destination)])
                    if operation == "prepare_readiness_only":
                        args.append("--readiness-only")
                    with self.subTest(case=case["case_id"], operation=operation):
                        code, out, err = command(args)
                        self.assertEqual(code, expected["exit_code"], err)
                        self.assertEqual(files_in(destination), expected["output_files"])
                        if operation != "inspect" and code == 0:
                            self.assertEqual(json.loads(out)["analysis_bundle_created"], expected["analysis_bundle_created"])
                            actual = json.loads((destination / "compilation_manifest.json").read_bytes())
                            self.assertEqual(actual["analysis_bundle_created"], expected["analysis_bundle_created"])
                        if code != 0:
                            self.assertFalse(destination.exists())
