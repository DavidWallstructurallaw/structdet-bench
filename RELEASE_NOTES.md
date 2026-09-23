# StructDet-Bench 0.1.0 release candidate

Prepared 2026-09-23. A public Git tag, GitHub release or package-registry
publication is a separate action; these notes describe the prepared software.

StructDet-Bench is an offline toolkit for task-relative structural measurement
of recorded LLM outputs. Supply local files, validate or inspect them, then run
the documented analysis command. Start with the complete example in
[README.md](README.md); it requires no model account or API key.

## Included capabilities

- M measurement: structural classes, support, SCI and related diversity measures,
  with explicit populations and missing or unavailable states.
- V registered comparisons: paired conditions, sensitivity and retained sampling
  identities.
- L longitudinal analysis: trajectories, finite-family support assays, local
  structural half-life, conditional recovery and revision invalidation.
- Exact replay: input, method, software, unit order and stored draws remain
  checked. Missing or corrupt requested replay information cannot start a fresh run.
- Passive study workflow: evidence inspection, blind review exports, original
  record preservation, correction tracking, compatible M/V/L compilation and
  readiness reports with all ten EC disclosures.

Analysis retains the established `report.json`, `report.md` and
`run_manifest.json` outputs. Publication requires a fresh output directory;
existing output is refused. Submitted code and responses remain passive input
to the toolkit. Model calls and candidate execution occur outside it.

## Runtime and distribution

The supported reference environment is CPython 3.13.5 / Unicode 15.1.0 on Linux;
the package declares Python `==3.13.*` and has no third-party runtime dependencies.
Secure file access requires POSIX descriptor support, and atomic publication
requires Linux `renameat2`. Unsupported environments fail closed.

Source examples use `python3.13 -B -S -m structdet_bench`. A separately installed
package uses `python3.13 -m structdet_bench` with its installation environment
active. `-S` suppresses installed site packages and is therefore reserved for
the source invocation shown in the examples.

Building requires `setuptools>=77`. Software and tooling use Apache-2.0;
project specifications and benchmark documentation use CC BY 4.0. License
texts, notices and attribution records are included. Original theory PDFs and
the private trial material are excluded from the software distribution.

## Verification and trial scope

The preceding Phase 4 software handoff recorded 2,004 passing canonical methods,
17 passing release checks and 53 passing build/install checks on the source and
artifacts identified in its retained receipts. Release qualification for updated
artifacts is recorded separately against their actual identities. The permanent
architecture is canonical regression, release qualification and an inactive
historical archive; see [VERIFICATION.md](VERIFICATION.md).

The limited real-material trial subsequently completed five screenshot-derived
programs, each passing all 8,995 existing HERO functional inputs: 44,975 candidate
input executions with zero failures. Passive CLI validation and analysis also
succeeded. Proposed structural labels remain provisional, and formal SCI is
undefined for the empty admitted classification population. These observations
cover the saved transcriptions and finite input set. Full registered condition
comparisons, independent human review and scientific validation remain pending.
See [LIMITED_TRIAL.md](LIMITED_TRIAL.md).

The owner accepted this limited trial scope for software closeout. Additional
sample collection is optional and is not a prerequisite for this software
release. Earlier phase records and the original Step 11 disposition remain
unchanged historical evidence. [PHASE_4_COMPLETION.md](PHASE_4_COMPLETION.md)
distinguishes the original handoff, subsequent trial and publication state.

Earlier replay manifests retain their exact original software identity. Keep
that software with the manifests; this release introduces no permissive replay
migration or resampling fallback. Fixture correctness, software verification and
the limited trial supply no universal model-capacity or theory-validation claim.
