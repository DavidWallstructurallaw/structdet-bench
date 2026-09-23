"""Opt-in passive study commands and private atomic output publication.

Prepared payloads retain original supplied bytes and may contain private data.
The companion sidecars expose bounded, pseudonymous readiness information.
No provider, candidate, reviewer, or external service is invoked.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import os
from pathlib import Path
import re
import sys
import uuid

from .contracts import InputError
from .local_io import LocalReader, PublicationError, ReadLimits, _rename_noreplace, relative_parts
from .study_records import _serialize, load_study


SIDECARS = frozenset({"study_readiness.json", "study_readiness.md", "provenance_map.json", "compilation_manifest.json"})


def add_parser(commands, parser_class):
    study = commands.add_parser("study", allow_abbrev=False,
        help="Inspect passive study records, export blind review material, or prepare an analysis bundle")
    operations = study.add_subparsers(dest="study_command", parser_class=parser_class)
    inspect = operations.add_parser("inspect", allow_abbrev=False,
        help="Print a bounded readiness summary without writing files")
    prepare = operations.add_parser("prepare", allow_abbrev=False,
        help="Publish a new private study preparation directory")
    for command in (inspect, prepare):
        command.add_argument("--study", required=True, help="Local study.json and its explicit finite inventory")
        command.add_argument("--qualification-packet-id", help="Explicit evidence qualification packet ID")
        command.add_argument("--mapping-receipt-id", help="Explicit compilation mapping receipt ID")
    prepare.add_argument("--output-dir", required=True, help="New directory outside the input study, in an existing parent")
    prepare.add_argument("--readiness-only", action="store_true", help="Publish exactly four sidecars and no analysis payload")
    review = operations.add_parser("export-review", allow_abbrev=False,
        help="Publish blind material and a separate restricted original identity map")
    review.add_argument("--study", required=True, help="Local study.json")
    review.add_argument("--artifact-id", action="append", required=True, help="Original artifact ID; repeat for every selected item")
    review.add_argument("--output-dir", required=True, help="New public review directory outside the study")
    review.add_argument("--restricted-output-dir", required=True, help="Separate new restricted identity-map directory")
    review.add_argument("--pack-id", help="Optional opaque identity: pack- followed by 32 lowercase hexadecimal digits")
    review.add_argument("--review-kind", choices=("core", "sampled_output"), default="core")
    study.set_defaults(_study_parser=study)


def _target_path(output_dir, study_path):
    name = os.fspath(output_dir)
    if (not isinstance(name, str) or not name or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", name)
            or any(c in name for c in ("\\", "$", "~"))
            or any(ord(c) < 32 or ord(c) == 127 for c in name)):
        raise InputError("unsafe_output_path")
    target = Path(name)
    if ".." in target.parts or target.name in {"", ".", ".."}:
        raise InputError("unsafe_output_path")
    target = target.absolute()
    source_root = Path(study_path).absolute().parent
    if target == source_root or source_root in target.parents or target in source_root.parents:
        raise InputError("output_overlaps_input_study")
    return target


def _inventory(files):
    return [{"path": name, "sha256": hashlib.sha256(content).hexdigest(), "size_bytes": len(content)}
            for name, content in sorted(files.items())]


def _directory_fd(root_fd, parts):
    """Open every generated directory component without following symlinks."""
    fd = os.dup(root_fd)
    try:
        for part in parts:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def publish_study_output(output_dir, files, *, study_path):
    """Write a complete fixed-sidecar directory with optional exact nested input.

    A held no-follow parent descriptor anchors publication. All staged files and
    directories are private. No-replace rename is the only visibility commit;
    a failed/interrupted precommit removes only this call's tracked stage.
    """
    if (not isinstance(files, Mapping) or not SIDECARS <= set(files)
            or any(not isinstance(name, str) or not isinstance(content, bytes) for name, content in files.items())
            or (set(files) != SIDECARS and "bundle.json" not in files)):
        raise InputError("invalid_study_output_inventory")
    if len(files) > 100000 or sum(map(len, files.values())) > 128 * 1024 * 1024:
        raise InputError("study_output_size_exceeded")
    directories = set()
    for name in files:
        parts = relative_parts(name)
        if len(parts) > 64:
            raise InputError("study_output_path_depth_exceeded")
        directories.update("/".join(parts[:n]) for n in range(1, len(parts)))
    if directories & set(files):
        raise InputError("study_output_path_collision")
    target = _target_path(output_dir, study_path)
    with LocalReader(target.parent, ReadLimits()) as holder:
        parent = holder._fd
        try:
            os.stat(target.name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise InputError("output_already_exists")
        stage = ".structdet-study-" + uuid.uuid4().hex
        opened = None
        created = published = False
        written, made_dirs = [], []
        try:
            os.mkdir(stage, mode=0o700, dir_fd=parent)
            created = True
            opened = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            for directory in sorted(directories, key=lambda name: (name.count("/"), name)):
                parts = directory.split("/")
                fd = _directory_fd(opened, parts[:-1])
                try:
                    os.mkdir(parts[-1], mode=0o700, dir_fd=fd)
                finally:
                    os.close(fd)
                made_dirs.append(directory)
            for filename in sorted(files):
                parts = filename.split("/")
                containing = _directory_fd(opened, parts[:-1])
                try:
                    fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 mode=0o600, dir_fd=containing)
                finally:
                    os.close(containing)
                written.append(filename)
                try:
                    data = memoryview(files[filename])
                    while data:
                        count = os.write(fd, data)
                        if count <= 0:
                            raise PublicationError("short_output_write")
                        data = data[count:]
                    os.fsync(fd)
                finally:
                    os.close(fd)
            # Flush child directories before the top-level commit.
            for directory in sorted(made_dirs, key=lambda name: (-name.count("/"), name)):
                fd = _directory_fd(opened, directory.split("/"))
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            os.fsync(opened)
            _rename_noreplace(parent, stage, target.name)
            published = True
            os.fsync(parent)
        except InputError:
            raise
        except OSError as exc:
            raise PublicationError("published_durability_unconfirmed" if published else "output_write_failed") from exc
        finally:
            if not published and opened is not None:
                for filename in reversed(written):
                    parts = filename.split("/")
                    containing = _directory_fd(opened, parts[:-1])
                    try:
                        os.unlink(parts[-1], dir_fd=containing)
                    except FileNotFoundError:
                        pass
                    finally:
                        os.close(containing)
                for directory in reversed(made_dirs):
                    parts = directory.split("/")
                    containing = _directory_fd(opened, parts[:-1])
                    try:
                        os.rmdir(parts[-1], dir_fd=containing)
                    finally:
                        os.close(containing)
            if opened is not None:
                os.close(opened)
            if created and not published:
                os.rmdir(stage, dir_fd=parent)


def preparation_files(assessment, *, readiness_only=False):
    """Assemble deterministic public sidecars plus eligible exact private bytes."""
    if assessment.has_errors:
        raise InputError("study_input_rejected")
    compilation = assessment.compilation
    restriction = None
    if not compilation.compiled:
        restriction = "compilation_withheld"
    elif compilation.bundle_path != "bundle.json":
        restriction = "compilation_bundle_name_unrepresentable"
    elif any(name.split("/", 1)[0] in SIDECARS for name in compilation.files):
        restriction = "compilation_sidecar_name_collision"
    if restriction is not None and not readiness_only:
        raise InputError(restriction)
    created = not readiness_only and restriction is None
    assessment = assessment.with_publication(analysis_bundle_created=created,
        publication_mode="readiness_only" if readiness_only else "analysis_bundle", restriction=restriction)
    files = {"study_readiness.json": assessment.json_bytes,
             "study_readiness.md": assessment.markdown_bytes,
             "provenance_map.json": _serialize(assessment.provenance)}
    if created:
        expected = {row["path"]: (row["sha256"], row["size_bytes"]) for row in compilation.provenance["outputs"]}
        actual = {row["path"]: (row["sha256"], row["size_bytes"]) for row in _inventory(compilation.files)}
        if actual != expected:
            raise InputError("compiled_snapshot_identity_mismatch")
        files.update(compilation.files)
    manifest = dict(assessment.compilation_manifest)
    manifest.update(analysis_bundle_created=created,
        publication_mode="readiness_only" if readiness_only else "analysis_bundle",
        bundle_creation_restriction=restriction,
        analysis_bundle_path="bundle.json" if created else None,
        companion_files=sorted(SIDECARS),
        exact_payload_file_count=len(compilation.files) if created else 0,
        publication_permissions="owner_only",
        original_payload_privacy="Exact supplied bytes may contain private data; authorize access before sharing.")
    # Payload path aliases and byte identities are already present in the public
    # compiler provenance. Do not expose original payload filenames here.
    manifest["sidecar_sha256"] = {name: hashlib.sha256(files[name]).hexdigest() for name in sorted(SIDECARS - {"compilation_manifest.json"})}
    files["compilation_manifest.json"] = _serialize(manifest)
    return files, created


def run_command(args):
    if args.study_command is None:
        args._study_parser.print_help()
        return 0
    try:
        loaded = load_study(args.study)
        if args.study_command == "export-review":
            from .study_review import ReviewPublicationError, export_blind_review_pack
            _target_path(args.output_dir, args.study)
            _target_path(args.restricted_output_dir, args.study)
            try:
                result = export_blind_review_pack(loaded, args.artifact_id, args.output_dir,
                    args.restricted_output_dir, pack_id=args.pack_id, review_kind=args.review_kind)
            except ReviewPublicationError as exc:
                sys.stderr.write(_serialize({"error": exc.code, "restricted_publication_status": exc.restricted_status,
                    "public_publication_status": exc.public_status}).decode("utf-8"))
                preflight = exc.restricted_status == exc.public_status == "not_started"
                return 2 if preflight and exc.code in {"output_exists", "output_already_exists", "unsafe_local_path"} else 3
            sys.stdout.write(_serialize({key: result[key] for key in ("pack_id", "item_count", "substantive_validation_performed")} |
                {"restricted_publication_status": "completed", "public_publication_status": "completed"}).decode("utf-8"))
            return 0
        from .study_reporting import inspect_study
        assessment = inspect_study(loaded, qualification_packet_id=args.qualification_packet_id,
                                   mapping_receipt_id=args.mapping_receipt_id)
        if args.study_command == "inspect":
            sys.stdout.write(assessment.json_bytes.decode("utf-8"))
            return assessment.exit_code
        files, created = preparation_files(assessment, readiness_only=args.readiness_only)
        publish_study_output(args.output_dir, files, study_path=args.study)
        sys.stdout.write(_serialize({"study_outputs_published": True, "analysis_bundle_created": created,
            "publication_mode": "readiness_only" if args.readiness_only else "analysis_bundle",
            "output_file_count": len(files), "processing_exit_code": assessment.exit_code,
            "empirical_claim_established": False, "substantive_validation_performed": False}).decode("utf-8"))
        return assessment.exit_code
    except InputError as exc:
        sys.stderr.write("error: " + exc.code + "\n")
        return 2
    except PublicationError as exc:
        sys.stderr.write("error: " + exc.code + "\n")
        return 3
    except KeyboardInterrupt:
        sys.stderr.write(_serialize({"error": "operation_interrupted",
            "publication_status": "inspect_destination_before_retry"}).decode("utf-8"))
        return 3
    except Exception:
        sys.stderr.write("error: local_io_or_internal_failure\n")
        return 3
