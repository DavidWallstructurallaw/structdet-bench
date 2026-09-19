"""Thin offline validate/analyze commands. No provider or candidate execution."""
from __future__ import annotations
import argparse
from collections.abc import Sequence
import sys
from . import __version__
from .contracts import InputError


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's normal errors echo user-controlled arguments, potentially
        # including private paths or credentials. Keep the public diagnostic fixed.
        self.print_usage(sys.stderr)
        self.exit(2, "error: invalid or incomplete command arguments; use --help\n")


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(prog="python -m structdet_bench", allow_abbrev=False,
        description="StructDet-Bench: offline record validation and structural measurement.",
        epilog="Optional Phase 2 comparisons use the declared bundle extension. No model calls, code execution or independent scientific certification.")
    parser.add_argument("--version", action="version", version=f"StructDet-Bench {__version__}")
    commands = parser.add_subparsers(dest="command", parser_class=Parser)
    validate = commands.add_parser("validate", allow_abbrev=False, help="Check local records without writing reports")
    validate.add_argument("--bundle", required=True, help="Local bundle.json")
    analyze = commands.add_parser("analyze", allow_abbrev=False, help="Write a new JSON/Markdown report set")
    analyze.add_argument("--bundle", required=True, help="Local bundle.json")
    analyze.add_argument("--output-dir", required=True, help="New directory in an existing parent, outside the input bundle")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    from .pipeline import analyze_bundle, validate_bundle, write_analysis
    from .reporting import canonical_bytes
    from .local_io import PublicationError
    try:
        if args.command == "validate":
            report, code = validate_bundle(args.bundle)
            sys.stdout.write(canonical_bytes(report).decode("utf-8"))
            return code
        result = analyze_bundle(args.bundle)
        write_analysis(result, args.output_dir, bundle_path=args.bundle)
        sys.stdout.write(canonical_bytes({"run_id": result.report["run_id"],
            "processing_exit_code": result.exit_code, "report_set_published": True,
            "independent_validation_performed": False}).decode("utf-8"))
        return result.exit_code
    except InputError as exc:
        sys.stderr.write("error: " + exc.code + "\n")
        return 2
    except PublicationError as exc:
        sys.stderr.write("error: " + exc.code + "\n")
        return 3
    except Exception:
        # Do not leak input bodies, local paths, identity mappings or stack values.
        # The caller can use the Python API in a controlled debugging environment.
        sys.stderr.write("error: local_io_or_internal_failure\n")
        return 3
