# Verification

`tools/check.py` is the stable verification entry point. Its canonical regression
suite discovers current behavior tests directly. It does not execute inherited
phase gates or require historical test names to survive. The owner's
`VERIFICATION_POLICY.md` governs selection and future maintenance.

## Everyday development

Use the supported CPython 3.13 / Unicode 15.1.0 environment for the existing text
methods. Verification captures the actual interpreter, command, platform, source
bytes and executable modes. Output paths must be new, with an existing parent,
and must be outside the source tree.

```bash
python3.13 -B -S tools/check.py canonical --output-dir ../checks --jobs 4
python3.13 -B -S tools/check.py canonical --output-dir ../review-checks --select tests.test_study_review
python3.13 -B -S tools/check.py canonical --output-dir ../numeric-checks --select tests.test_metrics --select tests.test_populations
```

`--select` accepts an exact module, class or method prefix and can be repeated.
An unknown selection, empty discovery or test import error fails explicitly.
The report records the selected scope. A partial run never claims full-suite
coverage. Modules stay intact within workers so module and class fixtures retain
their normal lifecycle. `--jobs` supports 1 through 8 workers.

`result.json` records the actual discovered methods and actual outcomes, the
current source identity, command, elapsed time and environment. Consoles and
worker results are retained beside it. Failure, error, skip, expected failure,
unexpected success, missing results and duplicate identities all prevent success.
Source changes during execution also prevent success. Existing output is refused;
results from an earlier run are never overwritten. This is a bounded current-run
record, with no cumulative journal chain or inherited identity annotations.

Workers and clean-source results are checked against the parent's actual
discovery, selection, source and interpreter identity, environment and command.
A temporary invocation ID associates each child with that run. The parent checks
every outcome and release check again; a `passed` summary cannot substitute for
them. Imported receipts have finite byte and nesting bounds. These checks detect
stale or inconsistent execution records within the trusted development workflow;
they do not authenticate a self-consistent externally edited receipt.

Ordinary `python3.13 -B -S -m unittest discover -s tests -t .` discovers the same
current test tree. Use the stable checker when a saved scoped result and strict
nonpassing-outcome policy are required.

## Release qualification

```bash
python3.13 -B -S tools/check.py release --archive ../source-candidate.zip --output-dir ../release-checks --jobs 8
```

The ZIP must contain the complete source under `structdet-bench/`. Qualification
checks archive paths, duplicate entries, file kinds and size limits, then verifies
that extracted source bytes and executable modes equal the current source. It
executes the complete canonical suite once from that clean extracted copy, then
checks the `hero_recursive` and `categorical_null` validate/analyze/replay routes,
exact output inventories, replay report equality and refusal to overwrite an
existing output. It confirms the source and input archive remain unchanged.

For a later enclosing delivery archive containing that identical source, retain
this exact-source execution receipt and check the final archive identity plus
relevant extracted CLI/feature smoke tests. A second complete run is needed only
when source or a relevant environment changes, or another distinct release risk
requires it. Package builds are a separate applicable release check: this source
workflow reports `package_build: not_requested_source_delivery` and does not
claim a wheel or installed-package validation.

Verification paths and the source candidate are trusted developer inputs. Runtime
input sandboxing, publication race resistance and no-follow candidate reading
remain independently tested in the production I/O and security suites. The checker
never runs submitted sorting programs, calls a model, contacts a reviewer, or
publishes a repository.

## Behavior-to-suite mapping

| Distinct behavior or control | Current home |
|---|---|
| M classes, support, SCI/diversity, threshold and denominator rules, population/prefix accounting, missing states | Canonical: metrics, populations, inventory, evidence, records and integrity tests; existing numerical expectations unchanged |
| V paired comparison, lexical diagnostics, sensitivity, saved-index replay and prediction limits | Canonical: comparisons, uncertainty, predictions, text diagnostics and Phase 2 behavior/security/report integration tests |
| L trajectories, categorical support, finite-family assays, empirical/local half-life, recovery, revisions, recuts, panel/root and clock/window context | Canonical: longitudinal modules, support assays, half-life, recovery and Phase 3 behavior/security/report integration tests |
| Independent arithmetic and decimal oracles, fixture source identity | Canonical: existing arithmetic/SHL oracle tests and fixture-specific source references; no expected scientific value was relaxed |
| Record schemas, strict malformed input, bounded/no-follow reads, privacy, replay identity and prevention of fresh fallback | Canonical: records, local I/O, security and M/V/L replay neighbors |
| Source report catalogue coverage and JSON/Markdown meaning | Canonical: report path checks now read the scientific source catalogue directly, without phase matrices |
| Passive study records, fixed sorting inputs, receipt evidence bounds, independent-review records, planned collection, exact extraction, evidence admission and fixed/targeted audit selection | Canonical: study_records, study_validation, study_review, study_collection, study_extraction and study_evidence tests; positive fixtures never establish real independent validation |
| Exact M/V/L study compilation, operational/carrier contradictions, missing planned positions, qualification and dependency revisions | Canonical: study_bridge tests and existing numerical/profile/replay neighbors; exact carrier bytes and field maps preserve populations, both comparison views and longitudinal input identities |
| Offline study commands, readiness and all ten EC disclosures, public JSON/Markdown parity, restricted review exports, and atomic study preparation | Canonical: study_cli and study_reporting tests, including documented fixture workflows; release qualification retains clean-source execution and original M/V/L report/replay checks |
| Adversarial source/reviewer/attachment text stays passive, bounded complete logs preserve every original test identity, and over-limit packets never truncate into accepted evidence (W35/W36) | Canonical: study_security, study_records, study_validation, study_review and extraction tests |
| Exact carrier replay, source/method/configuration/order/index identity, and retained versus invalidated correction snapshots (W37) | Canonical: study_replay, study_bridge and existing M/V/L replay/security tests |
| Activity-specific operating dependencies, missing resources and optional pilot omission (W39 software) | Canonical: study_readiness tests; packet completeness is for review and never grants operational authority |
| Package metadata, standard-library import, command boundaries | Canonical: `test_verification.PackageAndCommandTests` |
| Real recorder outcomes, failed fixtures, empty/duplicate/missing discovery and selection errors | Canonical: `test_verification.RecorderTests` |
| Worker and clean-run results bound to actual discovery, exact current source, runtime and invocation (W38) | Canonical: verification receipt tests; actual current run and clean release qualification retain their own complete per-method outcomes |
| Current source bytes/modes, source drift, new output paths, ZIP traversal/duplicate/link rejection | Canonical: verification control tests; release: actual source/archive comparison and clean execution |
| Documented examples, reproducibility, no-overwrite publication, release artifact identity | Release qualification, with runtime security regression retained in canonical |
| Old phase approvals, predecessor method totals, stage bind-all tests, matrix expansion/pins, inherited gates, cumulative journal/reconciliation machinery | Inactive historical archive; original bytes and real past execution evidence remain in the unchanged Step 3 delivery |
| Current remote publication, owner acceptance, completed empirical study | Separate actions and evidence; never certified by a passing verification run |
| Exact local archive and source identity with separate software, empirical and remote states (W40 software) | Reuse verification/archive tests and release qualification; final phase handoff and owner acceptance remain separate deliverables |

## Consolidation boundary

The four administrative test modules (`test_scaffold` and `test_phase2_gate`
through `test_phase4_gate`), their four runners and the exclusive Phase 4 helper
were retired from active source. Meaningful current recorder, package, source,
archive and output controls were migrated to the stable tests above. Historical
matrix/identity classes embedded in scientific test files were also retired.
Their surrounding scientific tests remain active, including the independently
derived decimal SHL oracle formerly beside categorical matrix checks.

Two former checks about whether later-phase modules existed now check the actual
behavior they protected: passive record review does not predict or resample, and
observed fixture analysis does not claim independent validation. Report catalogue
coverage still tests actual output paths; it no longer requires correspondence
with a historical acceptance matrix.

The old matrices, metadata and shared helper files remain archival/support code.
Normal tests do not call their historical gate, identity or expansion functions.
Removing those remaining unused helper functions is optional cleanup, not an
additional prerequisite for current capability work. Historical completion
counts are facts about earlier deliveries, never targets for this suite.

Phase 4 Step 8 adds the opt-in offline study CLI, evidence-first readiness and
provenance reports, ten EC disclosures, fresh-directory preparation, and documented
fixture workflows (W31 through W34). Public summaries preserve restricted source
associations without disclosing raw identities or evidence prose. Complete carrier
payloads remain restricted exact inputs. Existing analysis report schemas and
replay behavior remain supported through the original commands.

Step 7 supplies exact legacy-profile compilation, operational mappings,
dependency-aware correction, and existing-engine reanalysis/replay (W26 through
W30). It preserves Step 6 evidence-linked membership and validity qualification,
72 fixed main audit positions, deduplicated targeted audits, scoped independence
checks, and five conjunctive EC conditions kept separate from four architectural
components (W21 through W25). It reuses Step 5's exact prompts and collection plans, external collection-record
inspection, and original-response extraction (W17 through W20). It extends
the Step 4 evaluator/review/adjudication processing (W12 through W16) and the
Step 3 record, fixed-input and receipt behavior (W04 through W11).
The applicable tests verify software contracts. Step 9 completes conformance and
reproducibility checks (W35 through W38) and passive activity-packet assessment
(W39 software). Existing archive/source controls and explicit completion states
cover W40 software handling without a new runtime handoff engine. The reconstructed Step 10 operating packets and Step 12 local handoff
use this existing verification architecture. The completion document and delivery
verification report identify their actual fulfillment and results. Real review,
independent validation and substantive E evidence remain unperformed. Retained
Step 9 results remain historical results, and reconstructed materials receive
fresh checks. Final clean release qualification records the current environment
and frozen source; it cannot certify remote publication or owner acceptance.

The older plan's W01 source reconciliation remains historical evidence. W02's
permanent predecessor-name/count requirement is superseded by the adopted policy;
current supported M/V/L behavior stays in canonical regression. W03's truthful
software/evidence separation is preserved in the checker and study reports.
W04 through W34 map to the current record, evidence, numerical, integration and
CLI behavior above. Requirement labels are documentation, not another runner or
an independently passing approval layer. Implementation coverage for W39/W40 and actual packet/archive fulfillment
are reported separately in the final completion document. This preserves the
handoff distinction without adding a phase runner or cumulative gate.

Future small changes use affected tests, relevant numerical oracles and integration
neighbors. Shared semantic changes use the full canonical suite. Packaging changes
use release qualification. Documentation-only edits do not trigger scientific
execution unless they change executable authority. Mutation checks should target
a few distinct high-value failure modes and retain any surviving mutation for
analysis; test-count growth alone is never a quality measure.

## Local source version and package checks

The final local handoff declares version `0.1.0` and Python `==3.13.*`,
matching the supported CPython 3.13 / Unicode 15.1.0 contract. Its final delivery
report separately records any actual build/install checks. The stable source
release check's `package_build: not_requested_source_delivery` value describes
that checker alone; a separate build receipt is required for a build claim.
No package-registry publication or remote Git tag is implied by this version.

Software identity remains an exact replay requirement. Earlier manifests retain
their original source/version context and are not automatically migrated to
`0.1.0`. Their successful old executions remain historical evidence. New example
runs and their replay use the final software's own manifests.

Source qualification uses `-B -S`. Installed package checks use `-I -B` so that
isolated execution can import the installed package with site packages available.
Each receipt records its actual command and environment; the two invocation
scopes are not conflated.
