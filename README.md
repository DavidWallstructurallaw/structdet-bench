# StructDet-Bench

An offline toolkit for task-relative structural measurement of recorded LLM outputs.

## Current delivery

Phase 2's offline comparison instrument has completed its local Step 8 final
audit. All 1,018 discovered tests pass, including the inherited M requirements,
all 26 applicable V families, 27 V trace rows, 29 V report groups, eight EC record
checks and eight engineering requirements. Final owner acceptance remains pending.
`PHASE_2_COMPLETION.md` records the reviewed scope and exact implementation basis.

The optional A/B/C path supports actual passive text input, scoped evidence and
quality checks, fixed paired-block sensitivity intervals, bounded P1/P5 outcomes,
and complete index replay. Omitting the comparison extension retains the M-only
measurement profile. Demo outputs remain explicitly marked software fixtures.

Repository delivery is separately pending: the last Step 8 connector read-back of
`main` and `phase2-step7-sync` points to Step 5 commit `74544e9`. The complete local
Step 6/7 implementation and this closeout have not been published to those branches.
Use the final local package for this reviewed version; do not infer remote
completion from a local passing gate or from staged Git objects. See the current
`artifacts/phase2/verification_manifest.json` and companion publication receipt.

## Run locally

Use the standard-library module path from this directory. No model account,
API key or package installation is required.

```bash
python -m structdet_bench --help
python -m structdet_bench validate --bundle examples/hero_hf00/bundle.json
python -m structdet_bench analyze --bundle examples/hero_hf00/bundle.json --output-dir hf00-output
python -m structdet_bench validate --bundle examples/hero_abc/bundle.json
python -m structdet_bench analyze --bundle examples/hero_abc/bundle.json --output-dir abc-output
```

Each output parent must exist; each new output directory must not exist. The
command publishes exactly `report.json`, `report.md` and `run_manifest.json`
without overwriting earlier runs. The full comparison index matrices are inside
the run manifest, alongside their identities. A declared local prior manifest can
be replayed through `comparison.resampling.replay_ref`; see
`COMPARISON_FORMAT.md` section 13.

The comparison extension selects schema 0.2 / `structdet_comparison_v1`.
Omitting it retains schema 0.1 / `structdet_measurement_v1`. Legacy M-only
absence fields describe that profile rather than a global absence of V code.
`validate` performs record and replay checks without numerical comparisons.
Contrary and inconclusive outcomes can correctly return processing exit 0;
malformed input returns 2, and unexpected internal/publication failure returns 3.

Secure input reading requires POSIX no-follow descriptor operations. Atomic
no-overwrite output publication requires Linux `renameat2` support. Unsupported
platforms fail closed; native Windows/macOS compatibility is not claimed. The
actual interpreter/platform is recorded in each verification receipt.

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
The full Phase 2 command now returns 0 when the reviewed M/V obligations and all
executed tests pass. Its repository check covers historical Phase 1 reconciliation;
current implementation publication requires a separate branch/tree read-back.
Neither command edits Phase 1 QA files. They append hash-chained Phase 2 execution
records. Missing, skipped, expected-failure and unexecuted bindings cannot pass.
The historical Phase 1 runner and matrix remain available, but fresh project QA
should use the Phase 2 runner to preserve the pinned Phase 1 journals.

The tested direct-module environment is CPython 3.13.5 / Linux, with third-party
site loading disabled. No GitHub Actions, model call, candidate-program execution,
independent annotation or package publication forms part of this acceptance.
The implementation matrix retains Step 7 as its verified code/test stage. Step 8
is an administrative final audit, with no new test identity or scientific change.
Later phases, collection and publication still require separate authorization.

## Sources and licensing

Read `PHASE_1_PLAN.md` with the frozen Phase 0 contracts and
`EVALUATION_CLOSURE_ADDENDUM.md`. `THEORY_SOURCES.md` pins SD, SI and EC.
Source adoption is not empirical validation.

Code, tools, tests and code-adjacent configuration use Apache-2.0; project
specifications and benchmark documentation use CC BY 4.0 as detailed in
`LICENSING_NOTES.md`. Theory publications retain their original licenses and are
not included as PDFs. Third-party terms remain in `THIRD_PARTY_NOTICES.md`.

Historical license note: Step 1 originally stated “No public software license has been selected”. The owner later adopted the mixed licensing described above; that earlier statement is not the current license status.

## Comparison fixture and evidence boundary

The ABC texts are illustrative strings with stipulated mechanisms and validity.
They are not executed or independently validated sorting programs. Seventy-two
call records denote mock fixture positions, not real API invocations. Shared bytes
have distinct stipulated occurrences with a consistent current mechanism label.
No private source bodies, tokens or actor mappings are published in the reports.

The base fixture yields P1's lexical increase and G of 8/19, with zero structural
pair increase, and both P5 valid distinct-20 differences of +1. These expected
values exercise software. The heterogeneous variant has a positive mean and a
range spanning zero; it must remain inconclusive. Independent reference sets and
fraction enumeration are retained in the test helpers and pinned fixture oracles.

Intervals describe sensitivity within the fixed six-wording suite. They do not
establish population-level confidence, deployment readiness, full expressible or
latent support, model recovery, or the truth of the proposed theory. UD-006 remains
open for actual independent evidence. No hosted CI or package publication is added.
