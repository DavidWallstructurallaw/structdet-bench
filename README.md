# StructDet-Bench

A local-first measurement project for task-relative structural support in model
generation and, in later work, its recursive dynamics.

## Current status

**Phase 1 Step 1: scaffold only. Version `0.1.0.dev0`.**

The package imports and exposes help and version information. The local
standard-library QA harness records actual results, verifies the frozen
baseline, and inventories all 54 VF test families, 40 TR requirements, and
36 RF report groups. Scaffold checks have their own engineering identities.

No record ingestion, structural classification, validity adjudication, metric
calculation, `validate`/`analyze` command, hero report, comparison, model call,
or generated-program execution is implemented at this step. The development
version does not claim that the M milestone or the full v0.1 product is complete.

## Run locally

Use Python 3.11 or later from this project directory. Runtime and tests use only
the standard library. No installation, API key, account, or network connection
is required for these commands:

```text
python -m structdet_bench --help
python -m structdet_bench --version
python -m structdet_bench
```

Calling the module with no arguments prints help. Unsupported commands and
arguments exit with code 2 rather than producing a fake successful audit.
The primary interface is the Python module; no installed command alias is added.

The exact tested interpreter and platform are recorded in the QA captures.
A successful run on that interpreter does not claim a tested multi-version or
cross-platform compatibility matrix.

## Verify Step 1

```text
python -m unittest discover -s tests -v
python tools/run_phase1_checks.py --scope scaffold
```

The first command runs the discovered tests. The second additionally checks
baseline identities and scope-aware acceptance, and saves the results.
A Step 1 pass requires actual discovered, completed, passing scaffold tests.
Zero tests, missing required scaffold bindings, errors, failures, skips, expected
failures, and unexpected successes cannot pass that acceptance gate.

The final M gate deliberately remains stricter:

```text
python tools/run_phase1_checks.py
```

Its default scope is `phase1`. **At Step 1, exit code 1 is expected** because the
37 M-bearing scientific test families and their implementation bindings are
unfinished. Executing this gate only checks readiness; it neither implements
later steps nor produces a Phase 1 completion record. The output lists the
missing bindings even when the selected scaffold gate passes.

Runner exit codes are 0 for the requested gate passing, 1 for failed or
incomplete acceptance, and 2 for a harness/configuration/I/O error. These are QA
outcomes, separate from scientific result states and evidence dispositions.

## Verification records

The two retained QA captures are:

```text
artifacts/phase1/test_results.json
artifacts/phase1/test_output.txt
```

The JSON contains a `runs` array. Subsequent runs retain previous run identities,
results, source fingerprints, and transcripts inside these captures. Corrupt
history is rejected instead of silently overwritten. Durations, timestamps,
absolute workspace paths, and run IDs describe execution and can differ on
replay. A run's hashes identify the source bytes used for that run.

`tests/phase1_matrix.json` contains applicability and real method bindings;
execution outcomes belong to the QA captures. M/V/E/D scopes remain separate:
M is the first offline implementation, V the later comparison capability,
E independently supplied substantive evidence, and D deferred estimators.
Every VF entry currently has no scientific implementation binding. An inventory
entry, metadata validation, or passed harness self-test supplies no independent
structural-measurement evidence.

Harness unit tests include synthetic results to check rejected/skipped/empty
cases. These are engineering fixtures for the runner and never fulfill a VF
scientific test. The application's runtime does not import the test harness.
Trusted CLI integration tests launch only fixed checked-in commands, using the
same interpreter, without a shell or inherited model credentials. The runner
accepts no candidate program or input-supplied executable.

## Governing baseline and authorization

The eleven Phase 0 files and `PHASE_1_PLAN.md` accompany this working tree as
byte-for-byte frozen copies. Their expected versions and hashes are recorded in
the applicability matrix and checked against the actual files. Historical
pending/proposed headers remain intact; later owner decisions are recorded
without rewriting those documents.

The owner's instruction `很好，给我phase 1 step 1` approved the delivered plan and
authorized Step 1 only. Repository publication was subsequently authorized when the
owner created and supplied the official GitHub repository. That later publication
authorization does not authorize model collection, spending, package publication,
or later-step implementation. No other toolkit is required. Start with
`PHASE_1_PLAN.md`, particularly Sections 4 and 6.

The proposed first completed M milestone will consume supplied local records,
apply the approved evidence policies, construct populations and prefixes,
calculate core metrics, and report JSON/Markdown. That path remains future work.
Actual independent evidence under UD-006 and deferred latent diagnostics under
UD-007 retain their existing scope restrictions.

## Packaging and licensing

The original Step 1 handoff recorded that **No public software license has been selected**. Repository publication subsequently selected the mixed-license structure described below. The Step 1 `pyproject.toml` metadata remains frozen without a package-license field; adding distribution metadata belongs to a later packaging-authorized step and does not change the root repository license.

`pyproject.toml` supplies minimal setuptools metadata with an explicit package
allowlist and no runtime dependencies. This delivery uses direct module
execution. No wheel, source-distribution, installation, or publication test is
claimed. Packaging is optional and must be separately tested before making a
distribution claim. No build frontend or dependency is automatically installed.

A later authorized local packaging check must use already available tools and
disable dependency fetching and build isolation. Do not use a package install
command that silently resolves dependencies from a network. Missing optional
build tooling does not block the direct module path.

The repository uses a mixed-license structure:

```text
Code, test code, tooling, and code-adjacent configuration: Apache-2.0
Project specifications and benchmark documentation: CC BY 4.0
Repository-created fixture/example data: CC BY 4.0 unless marked otherwise
Theory publications: retain their stated licenses
Third-party assets: retain their original licenses
```

See `LICENSE`, `LICENSING_NOTES.md`, `NOTICE`, `THEORY_SOURCES.md`, and
`THIRD_PARTY_NOTICES.md`. The theory PDFs retain their own licenses and are
excluded from the public repository; their identities remain recorded in the
frozen specifications and QA matrix. Repository publication does not authorize
package-registry publication.
