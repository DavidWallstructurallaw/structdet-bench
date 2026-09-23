"""Construct the frozen trusted sorting input inventory; never run candidates."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from structdet_bench.contracts import InputError
from structdet_bench.study_validation import materialize_sorting_inputs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, help='New output directory; existing paths are rejected.')
    args = parser.parse_args(argv)
    try:
        result = materialize_sorting_inputs(args.output_dir)
    except InputError as exc:
        print(json.dumps({'status': 'rejected', 'code': exc.code}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps({'status': 'materialized', **result}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
