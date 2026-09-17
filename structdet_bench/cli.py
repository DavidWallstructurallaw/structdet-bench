"""Help and version only. No input loading or analysis is performed here."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the current scaffold interface without discovering plugins."""
    parser = argparse.ArgumentParser(
        prog="python -m structdet_bench",
        description=(
            "StructDet-Bench: Phase 1 Step 1 scaffold. "
            "Only help and version are available. "
            "No ingestion, structural classification, metrics, or audit runs "
            "are implemented."
        ),
        epilog=(
            "The development version does not mean the M milestone or all "
            "v0.1 capabilities are complete. No model credentials are needed."
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--version", action="version", version=f"StructDet-Bench {__version__}"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Display help by default; argparse rejects all unavailable commands."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
