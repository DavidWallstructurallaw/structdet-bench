# StructDet-Bench

An offline toolkit for task-relative structural measurement of recorded LLM outputs.

## Current delivery

The local Phase 1 Step 8 audit is complete for owner review. All 503 existing tests
and the full first-milestone M gate pass in the recorded environment. The scope is
37 M-bearing VT families, 33 applicable TR rows, 28 RF groups and eight EC-001
M-only record checks. See `PHASE_1_COMPLETION.md` for the actual exit criteria,
source/implementation/fixture identities, commands, evidence and limitations.

Final owner acceptance remains pending. The local delivery contains the reviewed
Step 7 implementation; Step 8 adds no runtime, test, fixture or matrix changes.
Full v0.1 comparisons and actual independent validation are outside this milestone.

**Repository delivery remains pending.** The last verified GitHub main is Step 6
commit `8cd0fe6`; it must not be represented as containing this local Step 7/8 tree.
The full source, audit matrix and verification history are retained in the local
archive. Local test success is neither a hosted CI result nor proof of remote
synchronization. No Phase 2 work or package release has started.

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
python -B -S -m unittest tests.test_pipeline tests.test_reporting -v
python tools/run_phase1_checks.py --scope scaffold
python tools/run_phase1_checks.py
```

The complete current suite passes without skips. Both gate commands return exit 0
for the current M scope. The full gate requires every applicable M and EC record
binding to have actually passed; missing, skipped, expected-failure or unexecuted
bindings cannot pass it. Each result records expected/actual outcome, contract
links, source/fixture fingerprints and environment. Final Phase 1 approval remains
a separate Step 8 decision. `tests/phase1_matrix.json` preserves historical snapshots
and current bindings; the raw historical `current_step` field is not the effective
delivery step used by the runner.
GitHub QA captures are retained summaries; the companion delivery archive contains
the full actual execution journals.

## Sources and licensing

Read `PHASE_1_PLAN.md` with the frozen Phase 0 contracts and
`EVALUATION_CLOSURE_ADDENDUM.md`. `THEORY_SOURCES.md` pins SD, SI and EC.
Source adoption is not empirical validation.

Code, tools, tests and code-adjacent configuration use Apache-2.0; project
specifications and benchmark documentation use CC BY 4.0 as detailed in
`LICENSING_NOTES.md`. Theory publications retain their original licenses and are
not included as PDFs. Third-party terms remain in `THIRD_PARTY_NOTICES.md`.

Historical license note: Step 1 originally stated “No public software license has been selected”. The owner later adopted the mixed licensing described above; that earlier statement is not the current license status.
