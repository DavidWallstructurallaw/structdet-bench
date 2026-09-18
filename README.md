# StructDet-Bench

An offline toolkit for task-relative structural measurement of recorded LLM outputs.

## Current delivery

Phase 1's complete offline measurement implementation is now synchronized to
GitHub. Commit `fef1dd05a91d5bec2286ed1b75917659e696fe23` restores all 77 supplied
upload-package paths, including every one of the 67 byte-exact Phase 1 final files.
The user's upload commit is preserved as its parent. Frozen scientific documents,
the original Phase 1 matrix, original tests, fixtures and Phase 1 QA history remain
unchanged. `PHASE_1_COMPLETION.md` retains its historical local-delivery status;
`artifacts/phase2/baseline_reconciliation.json` records the later remote resolution.

Phase 2 Step 1 adds its separate verification framework. The inherited 503 tests
and 47 framework tests pass, for 550 in total. The current-stage gate passes with
verified baseline delivery; the full Phase 2 gate remains incomplete because its
26 V obligations and later integration are not implemented. No Step 2 runtime work
has started. Software checks do not supply independent empirical validation.

The current read-back and execution summary is in
`artifacts/phase2/verification_manifest.json`. The companion accepted-delivery ZIP
contains complete fresh logs and replay evidence. Existing Phase 2 journals retain
the earlier blocked runs exactly; those are historical results, not this acceptance.
Subsequent local runner invocations append their actual outcomes to that history.

## Run locally

Use the standard-library module path from this directory. No API key or model
account is required, and no package installation is needed.

```bash
python -m structdet_bench --help
python -m structdet_bench --version
python -m structdet_bench validate --bundle examples/hero_hf00/bundle.json
python -m structdet_bench analyze --bundle examples/hero_hf00/bundle.json --output-dir hf00-output
```

The output parent must already exist; `hf00-output` itself must not exist. The
command writes `report.json`, `report.md` and `run_manifest.json` together. For a
second run choose a new directory. Existing reports and source inputs are never
overwritten. A malformed bundle can produce a safe diagnostic report with exit 2;
that report does not declare processing success.

Current secure input reads require POSIX no-follow descriptor operations. Atomic
no-replace report publication additionally requires Linux `renameat2` support in
the host C library, kernel and filesystem. Unsupported publication fails safely;
there is no overwrite fallback. Tested interpreter/platform are recorded in the
actual QA artifacts, rather than inferred from the Python >=3.11 language floor.

## What the demo establishes

HF-00 contains twenty stipulated records, in the exact four groups of five from
the approved benchmark specification. Its observed counts are 8, 6, 3, 2 and 1.
The expected support is 5, support at threshold 0.10 is 4, and SCI is 57/200.
Shannon and Simpson effective class counts are reported separately.

These are **software fixtures**. No sorting-program source, actual model output,
API charge, completed human annotation or execution-validation result is supplied.
The demo checks computation and evidence-record handling. It supplies no empirical
P1/P5 finding, deployment assurance or estimate of full model capacity.

Imported classification/validity records follow the same pipeline under the
selected evidence policy. A record-consistent imported assertion remains a
supplied assertion, with independent scientific validation explicitly unperformed
by the toolkit. Unknown metadata and unsupported conclusions are retained.

## Reports and privacy

Reports separate planned calls and positions from actual realizations, preserve
fixed prefixes without backfilling, show both classified populations and their
five coverage ratios, and keep evidence restrictions ahead of numerical results.
Unavailable/deferred comparisons and estimators have null values and reasons.

Ordinary reports omit raw bodies, private identity mappings, paths and unrestricted
evidence prose. Hashed references and scoped record IDs retain local audit links.
A public report alone cannot reproduce privately retained evidence.

## Tests

```bash
python -B -S -m unittest discover -s tests -t . -v
python -B -S tools/run_phase2_checks.py --scope current
python -B -S tools/run_phase2_checks.py --scope phase2
```

The current-stage command also executes the inherited M gate and should return 0.
The full Phase 2 command should return 1 with explicit unimplemented V obligations.
Neither command edits Phase 1 QA files. They append hash-chained Phase 2 execution
records. Missing, skipped, expected-failure and unexecuted bindings cannot pass.
The historical Phase 1 runner and matrix remain available, but fresh project QA
should use the Phase 2 runner to preserve the pinned Phase 1 journals.

The tested direct-module environment is CPython 3.13.5 / Linux, with third-party
site loading disabled. No GitHub Actions, model call, candidate-program execution,
independent annotation or package publication forms part of this acceptance.
Later development steps still require their own execution instruction.

## Sources and licensing

Read `PHASE_1_PLAN.md` with the frozen Phase 0 contracts and
`EVALUATION_CLOSURE_ADDENDUM.md`. `THEORY_SOURCES.md` pins SD, SI and EC.
Source adoption is not empirical validation.

Code, tools, tests and code-adjacent configuration use Apache-2.0; project
specifications and benchmark documentation use CC BY 4.0 as detailed in
`LICENSING_NOTES.md`. Theory publications retain their original licenses and are
not included as PDFs. Third-party terms remain in `THIRD_PARTY_NOTICES.md`.

Historical license note: Step 1 originally stated “No public software license has been selected”. The owner later adopted the mixed licensing described above; that earlier statement is not the current license status.
