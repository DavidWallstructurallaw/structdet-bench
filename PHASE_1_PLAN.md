# PHASE_1_PLAN

## StructDet-Bench: First Offline Measurement Implementation

| Field | Value |
|---|---|
| Document version | 0.1 |
| Record date | 2026-09-17; no exact local decision timestamp asserted |
| Status | PROPOSED PHASE 1 PLAN; ready for Theory Owner review |
| Decision authority | Theory Owner |
| Baseline | The eleven Phase 0 files identified in Appendix A, including the Step 8 corrections |
| Phase 0 acceptance | Recorded in Section 1 from the owner's response to the final-review handoff |
| Current authorization | Prepare `PHASE_1_PLAN.md` only |
| Implementation authorization | Not received in the present instruction |
| Target capability | M: first executable offline fixture/imported-record measurement path |
| Additional v0.1 comparison capability | V: outside this implementation phase |
| Repository operations, publication, model calls, spending | Not authorized |
| Dependencies on the other two toolkits | None |

## 1. Authorization and governing material

### 1.1 Actual owner instruction

Following delivery of `PHASE_0_APPROVAL.md`, the proposed next action was to approve the consolidated baseline, including the audit corrections, and request a Phase 1 plan. The owner replied:

> 可以，给我PHASE_1_PLAN.md

In that context, this records acceptance of the identified Phase 0 baseline for progression and authorization to prepare this plan. The accepted corrections are AF-001, AF-002, and AF-003 in APPROVAL §5 and UD §7. This instruction does not begin implementation, create a repository, authorize remote writes, or approve the engineering proposals first introduced below.

`PHASE_0_APPROVAL.md` retains its historical READY FOR OWNER REVIEW header and pending fields. This later decision is recorded here; none of the eleven Phase 0 files is rewritten. Their exact identities appear in Appendix A.

Approval of this plan adopts its bounded engineering choices. Execution additionally requires an instruction identifying the step or named batch to perform. A single instruction may approve the plan and authorize a named implementation batch. No repeated approval of unchanged Phase 0 scientific decisions is required.

### 1.2 Authority and references

The reference keys used in this plan are:

| Key | File |
|---|---|
| APPROVAL | `PHASE_0_APPROVAL.md` |
| PLAN0 | `PHASE_0_PLAN.md` |
| SCOPE | `PROJECT_SCOPE.md` |
| DEF | `DEFINITIONS_AND_UNITS.md` |
| SC | `STRUCTURAL_CLASS_CONTRACT.md` |
| MET | `METRICS_SPEC.md` |
| EI | `EVALUATION_INTEGRITY.md` |
| HERO | `HERO_BENCHMARK_SPEC.md` |
| TRACE | `THEORY_TO_CODE_TRACEABILITY.md` |
| VF | `VALIDATION_AND_FALSIFICATION.md` |
| UD | `UNRESOLVED_DECISIONS.md` |

References identify the frozen editions in Appendix A. SD and SI retain the source identities recorded in APPROVAL §4. The governing implementation contracts already preserve their distinctions; this plan does not independently verify the publications cited inside those sources.

**[Owner-approved baseline]** Scientific definitions, evidence policies, populations, formulas, sampling semantics, and claim boundaries come from the adopted Phase 0 contracts. In particular, APPROVAL §6 defines M separately from V, actual external evidence E, and deferred capabilities D.

**[Engineering proposal]** The package layout, physical input envelope, CLI, test organization, operational limits, execution steps, and new output artifacts below are implementation choices submitted for approval. They do not acquire the status of source-derived scientific claims.

An explicit later owner decision can authorize a revision. A changed scientific meaning requires the affected contract revision and impact assessment; it cannot be hidden inside a code refactor or silently resolved by this plan.

## 2. Phase objective and release boundary

### 2.1 Required working result

Implement this complete path:

**Declared local JSON/JSONL bundle → passive input and identity checks → imported evidence-policy handling → attempt/sample/selection accounting → classified populations and fixed prefixes → core structural calculations → JSON and Markdown reports.**

This phase must end with an executable fixture demonstration and the applicable M conformance tests. A scaffold alone is insufficient. The calculation path must also handle imported adjudication records under their actual evidence limits. [APPROVAL §§6.1-6.4; SCOPE §4.1]

The registered hero frame remains:

| Identity | Adopted value |
|---|---|
| Task | `bounded_integer_sort`, version `0.1` |
| Resolution | `sorting_mechanism_family`, version `0.1` |
| Structural schema | `sorting_mechanism_partition`, version `0.1` |
| Reference registry | `sorting_reference_eight`, version `0.1` |
| Validity rubric | `bounded_integer_sort_validity_v1` |
| Class IDs | `SORT-ADJ`, `SORT-INS`, `SORT-SEL`, `SORT-MERGE`, `SORT-PIVOT`, `SORT-HEAP`, `SORT-COUNT`, `SORT-RADIX` |

Class meanings and eligible implementation variations remain exactly those in HERO §§3-5 and SC. Phase 1 transports and checks classification records; it does not inspect an arbitrary program and discover its algorithm family. Abstract A/B/C arithmetic fixtures remain test objects, without adding another supported benchmark domain.

### 2.2 Included capabilities

| Area | Required Phase 1 capability |
|---|---|
| Input | Local JSON metadata/configuration and JSONL records, explicit versions, linked identities, declared access states, and passive byte checks. |
| Evidence | Separate `fixture_only` and `adjudicated_import`; pin assignment/validity revisions; preserve unresolved, provisional, withheld, restricted, and unknown evidence. |
| Inventory | Planned attempts and candidate positions versus actual responses and realizations; retries, extraction associations, missingness, unallocated records, grouping, and registered order. |
| Populations | `classified_all` and `classified_valid`, plus every applicable count and ratio in MET §4.3. |
| Distribution metrics | Occurrence support, optional empirical-threshold support, entropy in nats, SCI, Shannon effective support, and Simpson effective support. |
| Prefixes | Prespecified distinct-k and accumulation tables, with selected IDs, counted samples, dependency groups, incomplete-position restrictions, and no backfilling. |
| Integrity records | Scoped role/lineage, reference, annotation, domain-validation, exposure, intake/tail, and correction records; handling tests remain separate from substantive validation. |
| Correction | Re-run a pinned corrected bundle, preserve original observation identities and prior results, and identify affected M outputs and claim scopes. |
| Reporting | Per-cell JSON and Markdown, matching states and meanings, input/configuration identities, limits, evidence restrictions, and V/E/D capability boundaries. |
| Verification | Applicable M portions of the existing VT catalogue, independent arithmetic oracles, negative cases, security checks, and repeatable local end-to-end execution. |

No default pooled model score is introduced. Different compatible cells may receive separate descriptive reports; condition differencing and cross-block aggregation remain V work. [SCOPE §6.1; MET §§3-7; TRACE §5]

### 2.3 Explicit exclusions

Phase 1 must not implement PC-06, PC-07, or PC-08: lexical/within-class diagnostics, structural pair comparisons, A/B/C contrasts, quality/coverage study gates, P1/P5 decision logic, or prompt-block resampling. Their existing contract definitions remain available for later work, without numeric placeholder implementations.

Also excluded are automatic structural classifiers, embedding clustering, LLM judges, provider/API adapters, live model collection, training, generated-program execution, a sorting-program sandbox, automatic artifact repair, external recruitment, probability-thresholded expressible support, latent diagnostics, frontier or convergence-cause estimation, SHL, ERR, soft-label scoring, new task families, dashboards, services, databases, telemetry, and automatic remote retrieval.

No separate headline `gini_simpson_diversity` estimator is added. Its catalog meaning remains recorded, while M reports the core fields already selected in MET §2.

The phase does not complete v0.1's V comparison capability or the empirical hero study. The planned 72 calls, 360 candidate positions, 32-program reference design, and 8,995-case domain suite are evidence-design records, not work to be executed by this phase. [APPROVAL §§6.5-7; HERO §2.1]

## 3. Engineering approach submitted for approval

### 3.1 Minimal local package

Use a small Python package named `structdet_bench`, with `python -m structdet_bench` as the primary local entry point. Proposed distribution metadata name: `structdet-bench`; initial development version: `0.1.0.dev0`. This development label must not imply that all v0.1 capabilities exist.

Use Python 3.11 or later as the proposed language floor. Record the exact interpreter actually used. Passing checks on one interpreter supports only that tested-environment statement; no untested compatibility matrix is claimed.

The runtime and conformance harness use the Python standard library. Use typed record objects, explicit validators, `unittest`, exact integer/rational operations where required, and stable floating-point summation. No mandatory model library, numerical framework, online schema resolver, or external test service is needed.

`pyproject.toml` provides package/build metadata. A conventional setuptools build may be configured as a development convenience, without runtime dependencies. Building or installing must not silently fetch dependencies. An unavailable local build frontend can leave the optional packaging check unperformed while the direct module path and required M checks proceed. Any later distribution claim requires its actual packaging test. The plan does not select current third-party versions or authorize installation.

No license is inherited from Recursive Integrity Toolkit. Public distribution and its license choice remain separate owner decisions. Source PDFs retain their own licenses and are not copied into package data, fixtures, or build outputs.

### 3.2 Logical responsibilities and modules

| Planned responsibility | Proposed code location | Boundary |
|---|---|---|
| Shared identifiers, vocabulary, capability states | `structdet_bench/contracts.py` | Mirror approved meanings; provide explicit absence of V/D estimators. |
| Typed record and version checks | `structdet_bench/records.py` | No hidden semantic classification or default completion of missing scientific metadata. |
| PC-01 passive local input | `structdet_bench/local_io.py` | Read declared bytes and check identity/access; never execute or retrieve external content. |
| PC-02 inventories | `structdet_bench/inventory.py` | Account for attempts, realizations, missing positions, groups, selection, and pinned order. |
| PC-03 and M part of PC-09 | `structdet_bench/evidence.py` | Apply imported evidence-policy rules and preserve scoped assessments/corrections. |
| PC-04 populations and prefixes | `structdet_bench/populations.py` | Select before conditioning on labels or validity; no count inflation or backfilling. |
| PC-05 core mathematics | `structdet_bench/metrics.py` | Pure calculations on accepted unweighted counts and identified prefixes. |
| M orchestration | `structdet_bench/pipeline.py` | Assemble the preceding steps without model calls, classification, execution, or V comparisons. |
| PC-10 reporting | `structdet_bench/reporting.py` | One result representation drives JSON and Markdown; no independent interpretation in a renderer. |
| Local command interface | `structdet_bench/cli.py`, `__main__.py` | Thin argument handling and local orchestration. |

TRACE's PC/EP identifiers remain the authoritative responsibility map. Combining responsibilities in this small package does not combine their evidence standards. No EP-01/02/03 execution module is created.

### 3.3 Physical input contract

The physical encoding is documented in `INPUT_FORMAT.md` and tested together with the validators. It binds DEF §9, SC §6, EI §3, HERO §11.3, and TRACE §4 without changing their semantics.

Use a declared bundle root containing:

| File role | Proposed physical representation |
|---|---|
| Bundle manifest | `bundle.json`: input-schema version, frame/protocol/cell declarations or pinned references, analysis configuration, assignment/validity revision selections, registered order/positions, and explicitly listed record files. |
| Observation and assessment records | `records.jsonl`: typed attempt, raw-artifact, realization, assignment, and validity records, joined by stable IDs. |
| Supporting records | `evidence.jsonl`: typed artifacts, roles, lineage, independent-assessment, annotation, domain-suite, audit, exposure, integrity, intake/tail, and correction records. |
| Other supplied material | Explicitly declared local references with identities/access states. External locators are inert metadata. |

These names describe the hero fixture layout. A manifest may list other relative filenames with the same declared roles; the loader performs no directory crawling or automatic discovery. Record type/version dispatch is a fixed allowlist. Unknown required schema versions and unsupported record kinds are diagnosed, rather than guessed into a familiar shape.

Keep incomplete metadata as a tagged state/value/reason/evidence object. Assignment status, review status, validity assessment, knowledge state, calculation state, test outcome, and claim disposition remain separate axes. Declared evidence stays declared; a complete form never supplies independent validation.

Preserve finite-decimal threshold tokens exactly, including a decimal-string input form. Reject duplicate JSON object keys, nonfinite numbers, malformed IDs, and booleans used where an integer count or k is required. No arithmetic tolerance applies to identity, membership, integer counts, or threshold inclusion.

Do not implement arbitrary schema mapping, executable transformations, plugins, remote JSON references, or a generic user-programmable expression language. Structural records can be imported without the original program body when the relevant policy and evidence permit the requested calculation. Missing source text and hashes retain their actual states.

### 3.4 Operational safety limits

Proposed default parsing limits are 16 MiB per file, 64 MiB per bundle, 1 MiB per JSONL record line, 100,000 typed records per bundle, and JSON nesting depth 64. They are engineering resource limits, separate from the hero's input domain, validation envelope, and experimental budgets. Tests use small configured limits to exercise boundaries.

A declared override is recorded before reading/analysis. Exceeding a limit produces an explicit diagnostic and unavailable affected calculation; it never silently truncates a file, drops a suffix of observations, or samples a smaller population. Actual implementation must document any additional parser/platform limitation rather than claiming these bounds constitute a security sandbox.

The loader accepts regular files explicitly contained in the selected bundle root. Resolve paths and reject traversal, symlink escape, device/pipe inputs, implicit environment expansion, and remote schemes for local reads. Restricted or absent evidence references can remain metadata with the corresponding limitation. No access-control service is added.

Read each accepted artifact into a pinned byte snapshot within the resource bound, and compute identity from those analyzed bytes. A checksum mismatch restricts that artifact and its dependents; it cannot be repaired by rewriting the expected checksum. Literal source text is passive data, even when it contains instructions or executable-looking content.

Output goes only to the explicitly selected output directory. Reject paths that overwrite inputs, frozen contracts, or an existing report set. Publish a complete report set only after successful serialization, using temporary files and cleanup on failure. No background watcher or automatic file mutation is permitted.

### 3.5 Proposed command and result surface

The intended commands, implemented only in their assigned steps, are:

```text
python -m structdet_bench --help
python -m structdet_bench --version
python -m structdet_bench validate --bundle PATH/bundle.json
python -m structdet_bench analyze --bundle PATH/bundle.json --output-dir PATH
```

The bundle carries the analysis configuration, including the evidence policy, revision pins, optional exact empirical threshold, and requested k values. CLI defaults must not invent experiment controls or silently alter the selected population. No `generate`, `train`, `execute`, `judge`, `compare`, or `recover` command is provided.

A completed analysis writes `report.json`, `report.md`, and `run_manifest.json`. The manifest links the exact analyzed bytes, configuration, software/interpreter identities, report fingerprints, and allowed execution metadata. No self-referential manifest hash is required.

Proposed exit meanings: 0 for completed processing with honestly reported numeric/evidence states; 2 for input/configuration contract failure, including unsafe path requests; 3 for local I/O or internal execution failure. An ordinary missing independent-evidence claim, a defined zero, or a known undefined metric does not cause a software failure. A malformed record must not be made successful by reporting it as empty data. Where safe, error output retains the supported inventory and affected scope.

Known timestamps, roots, execution identifiers, and other run-specific metadata are kept separate from deterministic metric payloads. The same pinned bundle/configuration and supplied analysis identity must reproduce canonical report values and ordering. Replay checks name any intentionally variable manifest fields. No claim of reproducible model generation follows.

## 4. File permissions and immutable baseline

All implementation paths below are relative to the explicitly selected local project root. They do not name an existing GitHub repository. No files at these paths are created by generating this plan.

Before Step 1, verify the eleven baseline files against Appendix A. If a new local workspace is authorized, exact byte-for-byte staging of those supplied files is allowed; after staging they are read-only. A mismatch must be investigated before treating that workspace as the approved baseline. PDFs can remain outside the software workspace; their recorded identities suffice for ordinary implementation, and they must not be bundled for redistribution.

Each step may write only the rows assigned to it in this ledger, plus the explicitly listed generated verification outputs. New paths require a finding-specific amendment or explicit owner authorization. This ledger is the exhaustive implementation allowlist, not a suggestion to create every file in Step 1.

| Exact path | Normal write steps | Purpose |
|---|---|---|
| `pyproject.toml` | 1 | Minimal local package metadata; no runtime dependency growth. |
| `.gitignore` | 1, 6 | Exclude caches, build products, private local inputs, and transient execution outputs. |
| `README.md` | 1, 6, 8 | Accurate current capability, local commands, evidence limits, final M status. |
| `INPUT_FORMAT.md` | 2, 3, 4, 6 | Physical encoding of the approved semantic fields and supported error behavior. |
| `structdet_bench/__init__.py` | 1 | Package/development version and narrow public surface. |
| `structdet_bench/__main__.py` | 1, 6 | Local module entry. |
| `structdet_bench/cli.py` | 1, 6 | Scaffold help/version first; working validate/analyze only in Step 6. |
| `structdet_bench/contracts.py` | 2, 3, 5, 6 | Identities, vocabulary, fixed capabilities, and contract bindings. |
| `structdet_bench/records.py` | 2, 3, 4 | Typed input/results and exact record validation. |
| `structdet_bench/local_io.py` | 2, 6 | Bounded local reads and safe output transaction support. |
| `structdet_bench/evidence.py` | 3 | Admission, scoped integrity records, and correction dependencies. |
| `structdet_bench/inventory.py` | 4 | Planned/actual inventories, identities, grouping, order. |
| `structdet_bench/populations.py` | 4 | Accepted populations, coverage, prefixes and accumulation. |
| `structdet_bench/metrics.py` | 5 | Approved M calculations and numerical checks. |
| `structdet_bench/pipeline.py` | 6 | Fixture/import-to-report orchestration and re-analysis. |
| `structdet_bench/reporting.py` | 6 | Common JSON/Markdown result rendering. |
| `tests/__init__.py` | 1 | Test package identity. |
| `tests/helpers.py` | 1, 2, 3, 4, 5, 6, 7 | Deterministic test-only builders and temporary-workspace helpers. |
| `tests/phase1_matrix.json` | 1, 2, 3, 4, 5, 6, 7, 8 | Full VT/TRACE applicability, concrete test bindings, and honest unimplemented scopes. |
| `tests/test_scaffold.py` | 1 | Import, version/help, baseline identity, and early capability honesty. |
| `tests/test_records.py` | 2, 3 | Record states, versions, identity conflicts, and pins. |
| `tests/test_local_io.py` | 2, 6 | Strict parsing, byte identity, resource bounds, and output safety. |
| `tests/test_evidence.py` | 3 | Fixture/import separation, local evidence failures, and correction records. |
| `tests/test_inventory.py` | 4 | Attempt/sample reconciliation, group positions, artifact association. |
| `tests/test_populations.py` | 4, 5 | Population/rate/prefix oracles and no-backfill rules. |
| `tests/test_metrics.py` | 5 | Exact arithmetic, thresholds, tolerances, and invariances. |
| `tests/test_reporting.py` | 6 | JSON/Markdown parity, privacy, result states, unavailable capabilities. |
| `tests/test_pipeline.py` | 6, 7 | Original hero, pinned variants, imported-record and correction paths. |
| `tests/test_integrity_records.py` | 3, 7 | Annotation/domain/audit/intake record gates without substantive E certification. |
| `tests/test_security.py` | 2, 6, 7 | Passive-input boundary, paths, no network/child execution, safe rendering. |
| `tests/fixtures/record_cases.json` | 2, 3, 4 | Explicit negative and incomplete-record arrangements. |
| `tests/fixtures/integrity_cases.json` | 3, 7 | Mock role/evidence/domain/audit/exposure/correction cases. |
| `tests/fixtures/arithmetic_oracles.json` | 5 | Independent exact count expressions and expected states. |
| `tests/fixtures/hero_variants.json` | 6 | HF-01 through HF-06 identities, exact changes, and independently stipulated expectations. |
| `examples/sorting_reference_eight.json` | 2, 3 | Faithful machine-readable copy of the adopted task/schema/registry and its actual validation status. |
| `examples/hero_hf00/bundle.json` | 6 | Original HF-00 frame, configuration, order, and file identities. |
| `examples/hero_hf00/records.jsonl` | 6 | Twenty stipulated samples and their original group/assignment/validity records. |
| `examples/hero_hf00/evidence.jsonl` | 6 | Explicit fixture declarations and honest missing empirical evidence. |
| `examples/hero_hf00/expected.json` | 6 | Pinned arithmetic, prefix, accounting, and state oracle independent of implementation output. |
| `tools/run_phase1_checks.py` | 1, 7 | Local standard-library test runner and scope-aware result recording. |
| `PHASE_1_COMPLETION.md` | 8 | Actual completion assessment and later handoff; never prefilled as passed. |

**Step 7 corrective exception:** a documented defect found during integration may be repaired in an already-created Phase 1 file from this ledger and its directly affected tests. The review note must identify the failing requirement, exact changed paths, and before/after evidence. This exception does not authorize new functionality, new paths, altered scientific contracts, or changes to the frozen Phase 0 files. Step 8 permits no code repair; a repair returns the work to the corresponding authorized step or this Step 7 procedure.

The plan itself stays read-only during execution. An owner-authorized plan amendment is a separate revision.

### 4.1 Generated verification outputs

The test runner may write only these named retained QA artifacts, plus isolated temporary files removed after tests:

- `artifacts/phase1/test_results.json`
- `artifacts/phase1/test_output.txt`
- `artifacts/phase1/hero_hf00/report.json`
- `artifacts/phase1/hero_hf00/report.md`
- `artifacts/phase1/hero_hf00/run_manifest.json`

They are actual execution products, not additional hand-authored specifications. Test results retain step/scope and actual environment; later runs may replace these working QA captures only while their prior run identities and relevant owner-reviewed delivery evidence remain retained. User analysis outputs use their separately selected directories and must not overwrite earlier reports.

No `.github/workflows` file, hosted CI run, commit, push, package publication, Docker image, or new dependency project is required by this phase. A future hosted workflow can invoke the local suite after separate repository/CI authorization. The local runner makes that integration possible without claiming it already exists.

## 5. Execution rules

Before each step, read its governing contracts, verify the baseline and applicable earlier deliverables, and check the explicit instruction authorizes that step. Within an authorized batch, preserve dependency order and each step's acceptance evidence.

Each step must provide its changed-file list, commands/checks actually run, actual results, evidence limitations, and remaining blockers. A brief conversation review note is sufficient; do not create a new planning document for each step. `tests/phase1_matrix.json` records bindings and scope, while executed outcomes belong to the QA result artifact.

New tests are written with the feature, not deferred wholesale to Step 7. Earlier tests rerun after dependent changes. Expected outputs come from the frozen formulas and fixtures, not from calling the production calculation and treating its answer as the oracle.

Default progression stops after the authorized step for review. An owner may authorize a named batch to reduce handoffs. Missing external reviewers, a model account, completion of another toolkit, or a favorable theory result never creates an M implementation stop. Actual security failures, scientific ambiguity, or scope changes retain the scoped stop rules in Section 10.

## 6. Step-by-step implementation

### Step 1. Establish the minimal package and verification harness

**Prerequisites:** this plan approved; explicit authorization for Step 1; identified local workspace and matching Phase 0 files.

**Allowed writes:** Step 1 rows in Section 4. No record ingestion, metrics, or false demo output is implemented here.

**Work:** Create importable package metadata, help/version entry points, standard-library test discovery, test-result recording, and the full applicability inventory for all 54 VF test IDs. Populate test bindings only when real tests exist. Other entries remain not implemented/not run for their proper scope. Record baseline fingerprints and the exact interpreter/environment. README must say scaffold status at this stage.

The local runner must report zero discovered tests and missing required bindings explicitly. An empty discovery cannot pass a milestone. It may launch the fixed trusted CLI for subprocess integration tests without a shell; this test-only facility must never accept a candidate program or input-supplied command.

**Acceptance:** imports/help/version work in the recorded local interpreter; no invented audit command success; no network or model credentials needed; baseline identity check passes; scaffold tests execute and report their actual results. No M completion or empirical statement is made.

**Stop:** deliver the scaffold and check record. Missing optional build tooling is recorded separately; it does not require a network install or prevent the direct module path.

### Step 2. Implement versioned records and passive local ingestion

**Prerequisites:** Step 1 accepted, or included in an explicitly authorized dependent batch. Read DEF §§3-5,8-10; SC §§3-6; MET §§3-4,7; EI §3; HERO §§3-4,11.3.

**Allowed writes:** Step 2 rows in Section 4.

**Work:** Implement the physical input envelope, fixed typed-record dispatch, tagged knowledge states, versions and reference pins, strict JSON/JSONL parsing, bounded local resolution, analyzed-byte fingerprints, and unallocated/invalid-record diagnostics. Transcribe the adopted eight-class registry as definitions with its actual evidence state. Preserve incomplete identities when supported inventory remains possible.

The loader may validate record content and references. It must not classify mechanism from code, infer absent lineage, equate sorted outputs with a family, generate expected validity, or normalize an unknown field into a default experiment control. Record/schema conflicts restrict their real dependent scope.

**Acceptance:** foundational VT-01/02/06/14/19 and corresponding record portions execute, with missing essential frame versus local missing metadata distinguished. Threshold decimal representations survive parsing. Duplicate object keys, unsafe paths, nonfinite values, oversized data, and unsupported versions fail explicitly without trimming. Readable declared local artifacts can be read; external locators cannot trigger retrieval.

**Stop:** deliver validators, physical input documentation, registry transcription, and tests. No claim that the taxonomy or example programs have independently been validated.

### Step 3. Implement imported evidence admission and scoped integrity records

**Prerequisites:** Step 2 accepted. Read SC §§5-8,10-12; EI §§3-11; MET §4.4; VF VT-04/15-18/21-30/47.

**Allowed writes:** Step 3 rows in Section 4.

**Work:** Implement `fixture_only` and `adjudicated_import` admission, unique assignment/validity revision pins, separate validity acceptance, explicit unresolved/provisional states, conflicting evidence handling, and versioned correction links. Keep fixture declarations separate from empirical membership evidence. A real-looking `adjudicated` string without the scoped record cannot pass admission.

Support typed evidence, role, independence, annotation, domain/audit, exposure, frontier/incident/tail, and claim records as passive input. Assess their schema consistency and declared requirement outcomes; do not judge natural-language rationale or independently certify the underlying observations. A supported imported-label calculation can coexist with a restricted independence claim. Do not use a universal acyclic-graph rule for all lineage relations.

Local membership-evidence failure with a valid shared frame withholds the affected assignment only. Independence-only withdrawal preserves separately supported class/validity evidence. Known-empty intake, unreviewed reference design, and mock reviewer records must remain distinguishable from actual external evidence.

**Acceptance:** VT-04 and relevant M record gates in VT-15-18/21-30/47 have executable checks. Mock outcomes remain marked mock, including an imported supported-for-scope assertion used to exercise routing. Two sessions by one person or exposed initial judgments do not satisfy the independent core requirement. Tests of a designed 32-role core, 28 descriptor pairs, or domain-suite manifest do not claim that any program was validated.

**Stop:** deliver evidence handling and scoped-gate tests. UD-006 stays open for actual E fulfillment and does not block the next implementation step.

### Step 4. Implement inventories, accepted populations, and fixed prefixes

**Prerequisites:** Step 3 accepted. Read DEF §§3,5; MET §§4,6-7; HERO §§7-8,11; VF §§4-5.

**Allowed writes:** Step 4 rows in Section 4.

**Work:** Build input/attempt inventories, actual unique realization inventories, and selected inventory U before label/validity conditioning. Preserve missing candidate positions, extra outputs, failures, retries, shared groups, original sequence, and exact artifact association. A failed five-candidate call creates a failed attempt and five planned positions, not five fabricated observations.

Construct `classified_all` and `classified_valid` and MET's exact coverage/validity ratios. Count repeated bytes as repeated observations only when genuine identities differ. Refuse ambiguous IDs or unresolved revision choices without guessing the latest label. Freeze order from explicit input, never from storage ordering or ID sorting.

Implement prespecified distinct-k and accumulation membership. Keep general descriptive prefixes separate from HERO's complete intended-group endpoints. A missing early intended position cannot be filled from later groups. An existing but unclassified prefix can have class count zero; a missing prefix is unavailable. No support arithmetic or full report renderer is required yet.

**Acceptance:** VT-02/03/05/06/10-12 and the M association portion of VT-36 pass their current inventory tests. MF-07 reproduces all five ratios; MF-10 respects k=2/4/6/7 and group boundaries. Unknown order affects prefix results while leaving supported whole-cell counts available. No validity-conditioned backfill or automatic sample exclusion is used.

**Stop:** deliver inventories/populations and the executable accounting tests, with unsupported comparisons still absent.

### Step 5. Implement the core metrics and independent arithmetic oracles

**Prerequisites:** Step 4 accepted. Read MET §§3-7,12.1-12.3,14; VF §5.1-5.2; APPROVAL §6.3.

**Allowed writes:** Step 5 rows in Section 4.

**Work:** Implement occurrence support, requested empirical-threshold support, structural entropy in nats, SCI, separate Shannon/Simpson effective counts, and the accepted prefix/accumulation results. Use the unfiltered accepted denominator for thresholding and unrounded values for derived metrics. Compare an exact decimal threshold a/b by `b*c_z >= a*n_A`.

Keep counts and memberships exact. Use MET's absolute `1e-12` plus relative `1e-10` convention only for noninteger numerical checks. Empty accepted populations, missing frame, malformed thresholds, omitted thresholds, and a real one-class distribution must keep their different states. No pseudocount, unseen-class estimator, posterior mass, weight, or material-value clamping is added.

Populate arithmetic oracles from exact expressions and independently checked counts. Exercise class renaming, storage-order invariance, zero-count registry additions, and conservation/range inequalities. Numerical-boundary corrections, if any, retain the recorded reason required by MET §7.

**Acceptance:** VT-07-11 and applicable metric parts of VT-05/06/13 pass, including unequal-count fixtures that distinguish the two effective quantities. No arithmetic implementation calls the renderer for rounding or derives expected test values from its own output. No V or D estimator is introduced merely because a formula is short.

**Stop:** deliver the working core and numerical tests. The package is still not marked end-to-end complete until the report path runs in Step 6.

### Step 6. Complete the hero fixture-to-report and imported-record CLI paths

**Prerequisites:** Step 5 accepted. Read HERO §11; MET §§3,7,14; EI §§6,10-11; VF §5.2; TRACE §4.

**Allowed writes:** Step 6 rows in Section 4 and named QA outputs in §4.1.

**Work:** Implement the thin validate/analyze commands, pipeline, common result representation, JSON/Markdown renderers, safe output writes, and run manifests. Materialize HF-00 and the explicitly pinned HF-01 through HF-06 variants. Add a small mock `adjudicated_import` path through the same code, preserving its mock role.

For HF-00, use the exact four-by-five sequence in HERO §11.1. Keep source program text unspecified: no invented lexical result, functional test success, real model identity, real generation charge, or completed annotation. Explicit fixture stipulations support its labels/validity. A stable fixture artifact identity must not be misrepresented as a hash of an actual sorting program.

Each variant starts from the unchanged original sequence and has its own fixture/version identity, exact change, input fingerprint, and independent expected result. A deterministic test-only builder may materialize variants from a pinned base plus declared JSON changes; the resulting variant manifest is pinned before analysis. This builder is never an input-configurable runtime transformation engine.

Render in HERO §11.2 order. M reports show V diagnostics/comparisons and D estimators as unimplemented/deferred with null values and reasons, not plausible zeroes or P1/P5 outcomes. Preserve evidence restrictions before the numeric tables. Redaction omits raw source bodies, sensitive identity mappings, absolute private paths, and unrestricted evidence prose from ordinary reports; it retains scoped IDs and access limitations. Escape Markdown/HTML-active text without modifying source bytes or class meanings.

Corrections run against new pinned configuration/evidence while leaving original samples, groups, budgets, and previous results unchanged. Recalculate all affected M fields and mark V dependents as outside this phase. Do not reconstruct corrected sample membership from aggregate counts alone.

**Acceptance:** HF-00 matches Section 7; HF-01 through HF-06, EI's four-sample correction, and the independence-only correction retain their correct denominators and claim states. VT-13/17-20/30/36/46 and M portions of VT-51-54 execute. Reports match on values, units, scope, statuses, and reasons; Markdown display rounding never changes the JSON value. Realize a local end-to-end command with no network, model call, or candidate execution.

**Stop:** deliver the executable demo, examples, reporting path, and actual test evidence. This is the first usable M path; integrated completion still requires Steps 7-8.

### Step 7. Complete M conformance, safety, and reproducibility coverage

**Prerequisites:** Step 6 accepted. Read APPROVAL §6.4, all applicable VF catalogue entries, and TRACE §§3-5.

**Allowed writes:** Step 7 rows and the finding-limited correction exception in Section 4; named QA outputs in §4.1. No additional feature or new file family is authorized.

**Work:** Complete every applicable M requirement's concrete test binding. Inspect the full 54-ID inventory and the 40 TR/36 RF map so V/E/D absence is deliberate, not accidentally omitted. Strengthen integration tests for shared-frame versus local-evidence failure, passive hostile input, attempted outbound operations, restricted reports, typed lineage cycles, annotation exposure, reference/tail intake, artifact associations, and correction history.

Exercise M domain/audit record gates using expressly synthetic records. For an imported full functional-suite manifest, verify the prescribed 781 + 18 + 8,192 + 4 identities/constructions and actual coverage states when supplied; do not run candidates against those inputs. Test empty/partial evidence and decisive imported counterexamples without treating a timeout as proof of nontermination. An omitted empirical suite never blocks HF-00.

Run the full local suite in a fresh temporary output location. Replay the same frozen input/configuration and compare canonical report contents; isolate explicitly declared execution metadata. The runner reports exact test names, expected/actual disposition, environment, source/fixture versions, and scope. A standard-library test command remains usable independently of the runner.

**Acceptance:** all 37 applicable M test families in Section 8 have their M responsibilities exercised and passing; no missing M test is hidden as an expected failure or a V deferral. E portions remain not performed. Repeated execution reproduces the promised content, safe input/output boundaries hold in the tested environment, and every M report field links to its contract and tests. Local results are never described as GitHub-hosted CI results.

**Stop:** deliver integrated evidence and any finding-specific repairs. A safety failure or changed scientific meaning must be resolved before final audit; no favorable model result is required.

### Step 8. Final audit and bounded completion handoff

**Prerequisites:** Step 7 accepted; all applicable local checks actually run.

**Allowed writes:** only `PHASE_1_COMPLETION.md`, final state/binding annotations in `tests/phase1_matrix.json`, the README's factual status section, and refreshed named QA outputs. No implementation or fixture repairs in this step.

**Work:** Verify the immutable baseline and approved plan, exact changed-file allowlist, package behavior, fixture identities/oracles, complete M test evidence, report parity, deferred boundaries, and missing E evidence. Record code/input/output fingerprints, environment, actual commands/results, any justified out-of-scope tests, and unresolved limitations. Check that documentation, fixture metadata, and report headlines agree on the capability and evidence actually delivered.

`PHASE_1_COMPLETION.md` must distinguish first-milestone conformance from owner acceptance, public release, full v0.1 completion, hosted CI, independently validated measurement, and actual theory experiments. Record those later actions as unperformed unless their separate evidence exists.

**Acceptance:** every criterion in Section 11 is either fulfilled with actual evidence or reported as a concrete blocker. A failed mandatory check prevents a completed status. The owner receives the working M tool and an accurate audit, not a promise of unexecuted tests.

**Stop:** deliver Phase 1 for review. Do not start V, a Phase 2 plan, repository operations, model collection, generated-code execution, or publication without the next instruction.

## 7. Required fixture and arithmetic acceptance

### 7.1 HF-00: original hero fixture

The unchanged registered sequence is:

| Group | Position 1 | Position 2 | Position 3 | Position 4 | Position 5 |
|---|---|---|---|---|---|
| F-G1 | MERGE | PIVOT | MERGE | HEAP | COUNT |
| F-G2 | MERGE | PIVOT | MERGE | HEAP | RADIX |
| F-G3 | MERGE | PIVOT | MERGE | PIVOT | COUNT |
| F-G4 | MERGE | PIVOT | MERGE | PIVOT | HEAP |

Shorthand maps to the exact `SORT-...` IDs. Both views contain twenty accepted fixture-valid observations under the original stipulations. The three other registry classes remain visible with zero observed count.

| Output | Required HF-00 value |
|---|---|
| Positive counts, MERGE/PIVOT/HEAP/COUNT/RADIX | `(8, 6, 3, 2, 1)` |
| Selected / classified-all / classified-valid | `20 / 20 / 20` |
| Occurrence support | 5 |
| Thresholded support, exact threshold 0.10 | 4 |
| Distinct-5 / distinct-10 / distinct-20 | `4 / 5 / 5` |
| SCI | `57/200` |
| Entropy | `ln(20) - [8 ln(8) + 6 ln(6) + 3 ln(3) + 2 ln(2)] / 20` |
| Entropy, displayed approximation | 1.392321254757429 nats |
| Shannon effective support | `exp(H)`, approximately 4.024180367609189 |
| Simpson effective support | `200/57`, approximately 3.508771929824561 |
| P1/P5 or prompt-block interval | No empirical result or interval established; V estimator absent in this phase |
| Source-text diagnostics | No numeric value; no actual fixture program text specified |
| Scientific status | Stipulated software demonstration, with missing E evidence explicit |

Exact expressions control expected values. Mathematical checks on hypothetical count arrays cannot substitute for the actual fixture-to-report execution. [HERO §11.1; VF §5.2]

### 7.2 Pinned variants and adverse cases

| Fixture | Required change and check |
|---|---|
| HF-01 | G2 position 5 remains classifiable RADIX but becomes fixture-invalid. All-view stays at 20; valid-view has 19, counts `(8,6,3,2)`, support 4, prefixes `4/4/4`. |
| HF-02 | That valid observation becomes classification-unresolved. Selected count remains 20; both classified views have 19; validity fraction remains 1. |
| HF-03 | Its assignment is provisional. Accepted arithmetic matches HF-02 but status and withholding reason remain different. |
| HF-04 | Its essential fixture declaration cannot be resolved. Withhold only that assignment when the shared frame remains valid; keep separately supported validity. |
| HF-05 | That candidate was not emitted. Actual realizations total 19. Full actual-sample counts remain descriptive; intended matched distinct-10/20 are unavailable, with no later replacement. |
| HF-06 | A new pinned assignment changes that observation from RADIX to COUNT. Counts become `(8,6,3,3)`, support 4, SCI `59/200`; original HF-00 remains preserved. |
| MF-07 / MF-10 | Exact six-sample coverage and no-backfill prefix cases from MET §12. |
| EI §10.2 | Four-sample original/withheld/corrected evidence sequence. SCI follows `1/2`, `5/9`, `5/8`; selected count and separately established validity remain four. |
| Independence-only withdrawal | Same accepted membership and arithmetic, revised independent-claim disposition. |
| Shared-frame failure | Affected structural metrics unavailable, supported inventories retained; never recoded as zero support. |

For the applicable nineteen-classified-record distribution, SCI is `113/361` and entropy is `ln(19) - [8 ln(8) + 6 ln(6) + 3 ln(3) + 2 ln(2)]/19`. Use those explicit oracles; do not copy HF-00's denominator after a withdrawal. An all-unclassified selected prefix has zero observed classes with appropriate coverage, while an absent prefix remains unavailable. [VF §§5.1-5.2]

No variant can silently mutate the original example or fabricate an external evidence record. Tests use mocks and stipulated inputs with explicit roles. Contrary imported observations and insufficient evidence must pass honest-handling tests without being relabeled as a defect in the model.

## 8. Test obligations and scope accounting

### 8.1 Existing catalogue remains authoritative

Keep all 54 VT IDs in `tests/phase1_matrix.json`. There are **37 test families with applicable M responsibilities**, listed below. Their M parts must be implemented and run by phase completion. The same ID's E or V portion remains separately outstanding. The other 17 families are outside M and must retain their actual deferred/unperformed state.

The matrix maps each test family to concrete test method names, controlling contract/version, fixture identity, M/V/E/D responsibility, TR rows, RF groups, and justified scope exclusions. Actual execution results are stored separately. A passed mock gate does not mark the whole M/E family substantively validated. Step 7 verifies that every M-bearing requirement among the 40 TR rows and 36 RF groups has its proper binding.

| VF ID | Required M check | Principal proposed test file(s) |
|---|---|---|
| VT-01 | Preserve metadata, evidence, calculation, and missingness axes; scoped frame failure. | `tests/test_records.py`, `tests/test_reporting.py` |
| VT-02 | Genuine repeated observations versus duplicate/conflicting identities and pinned revisions. | `tests/test_records.py`, `tests/test_inventory.py` |
| VT-03 | Attempt/response/position reconciliation, failures, extras, and retries; no V study analysis. | `tests/test_inventory.py` |
| VT-04 | Fixture/import policy separation; local evidence failure versus claim restriction. | `tests/test_evidence.py`, `tests/test_pipeline.py` |
| VT-05 | Both populations and exact MF-07 ratios. | `tests/test_populations.py` |
| VT-06 | Empty/unclassified/invalid/one-class/malformed distinctions. | `tests/test_records.py`, `tests/test_metrics.py` |
| VT-07 | Independent exact arithmetic tables and zero registry counts. | `tests/test_metrics.py` |
| VT-08 | Exact threshold boundaries and omitted/invalid/empty states. | `tests/test_metrics.py` |
| VT-09 | Numerical ranges, finite values, precision, and effective-count inequalities. | `tests/test_metrics.py` |
| VT-10 | Class-renaming and storage-order invariance; actual sequence changes. | `tests/test_metrics.py`, `tests/test_populations.py` |
| VT-11 | Fixed-prefix boundaries, missing order, partial groups, and no backfill. | `tests/test_populations.py` |
| VT-12 | Intended-position and group completeness for prefix inventory; no V comparison engine. | `tests/test_inventory.py`, `tests/test_populations.py` |
| VT-13 | Exact original hero and separately pinned variants. | `tests/test_pipeline.py` |
| VT-14 | Shared-frame identity/compatibility failures without erasing valid separate cells. | `tests/test_records.py`, `tests/test_populations.py` |
| VT-15 | Imported membership evidence gate; no semantic adjudication by software. | `tests/test_evidence.py` |
| VT-16 | Hybrid/new-to-registry/contradictory records retain unresolved status and no extra mass. | `tests/test_evidence.py` |
| VT-17 | Corrected evidence/populations and all affected M calculations; preserved originals. | `tests/test_evidence.py`, `tests/test_pipeline.py` |
| VT-18 | Independence-only correction restricts claims without unsupported label changes. | `tests/test_evidence.py`, `tests/test_pipeline.py` |
| VT-19 | Passive local input, hostile text, no automatic outbound/exec behavior, private evidence. | `tests/test_local_io.py`, `tests/test_security.py` |
| VT-20 | JSON/Markdown values, units, populations, reasons, and claim parity. | `tests/test_reporting.py` |
| VT-21 | Typed lineage and missing ancestry; no nominal independence or universal DAG rule. | `tests/test_integrity_records.py` |
| VT-22 | Initial reviewer identity/exposure/disagreement and scope of core/audit requirements. | `tests/test_integrity_records.py` |
| VT-23 | Known-empty, unused, contrary intake and tail/registry dispositions without count inflation. | `tests/test_integrity_records.py` |
| VT-24 | Actual timing, inspection, assistance, and exposure states; hashes prove identity only. | `tests/test_integrity_records.py` |
| VT-25 | Imported descriptor/witness/pair-review records and missing validation, not actual schema validation. | `tests/test_integrity_records.py` |
| VT-26 | Imported 8,995-case suite-manifest identity/count/construction checks, not execution. | `tests/test_integrity_records.py` |
| VT-27 | Imported validity coverage, counterexamples, and oracle scope; no truth from a status label. | `tests/test_integrity_records.py` |
| VT-28 | Imported runtime/harness/containment outcomes distinguished from decisive invalidity. | `tests/test_integrity_records.py`, `tests/test_security.py` |
| VT-29 | Core/audit/reference record accounting, nonreplacement of missing review positions. | `tests/test_integrity_records.py` |
| VT-30 | Fixture/calculation/measurement/release authority boundaries; no unrelated prerequisite. | `tests/test_pipeline.py`, `tests/test_reporting.py` |
| VT-36 | Exact supplied artifact-to-sample association; absence/empty/truncated distinctions. | `tests/test_inventory.py`, `tests/test_pipeline.py` |
| VT-46 | Original/variant M fixture-to-report path and RF links, with V absent. | `tests/test_pipeline.py`, `tests/test_reporting.py` |
| VT-47 | Record completeness and scoped withholding only; independent E review remains unperformed. | `tests/test_integrity_records.py` |
| VT-51 | No expressible/latent/intervention-union/soft-label/exact-realization-entropy estimates. | `tests/test_reporting.py` |
| VT-52 | No frontier, convergence cause, intervention effect, or transmission estimates. | `tests/test_reporting.py` |
| VT-53 | No SHL estimator or synthetic recursive-round interpretation. | `tests/test_reporting.py` |
| VT-54 | No ERR estimator or invented recovery evidence. | `tests/test_reporting.py` |

VT-31 through VT-35, VT-37 through VT-45, and VT-48 through VT-50 have no Phase 1 M implementation obligation. Their V/E responsibilities stay unimplemented/unperformed. Absence must be recorded; they must not be counted among passed M checks or implemented as convenient extras.

The 82 upstream checks mapped in VF §8 remain mapped there. This plan does not rename, remove, or reclassify a scientific test. Physical test bindings can contain multiple methods per VT, and one method may exercise several compatible assertions. Count test families and actual methods separately.

### 8.2 Independent oracles and test evidence

Expected counts, ratios, threshold membership, sample IDs, group positions, and review dispositions are exact. Numerical expected values use the adopted exact expressions and MET's tolerance. At least the unequal-frequency cases must distinguish Shannon and Simpson counts. Passing only balanced distributions is insufficient.

A future test result records the VT/scope and actual method; contract and fixture versions/hashes; action/configuration; expected versus actual result; tolerance when applicable; interpreter/environment; and pass/fail/not-run/inapplicable disposition with reason. Any added engineering-only checks have separate names and origin, without pretending they were source requirements.

No mandatory M behavior may be hidden behind skipped tests, placeholder assertions, expected-failure markers, fabricated external evidence, or a runner that discovers only the already-passing subset. Runtime safety tests and numerical tests remain distinct. A security boundary observation demonstrates the tested path, not proof that the software is invulnerable.

### 8.3 Local regression and CI boundary

The required local regression interface is:

```text
python -m unittest discover -s tests -v
python tools/run_phase1_checks.py
```

The runner must fail final milestone acceptance when an applicable M binding is missing or failed, even if discovery itself exits successfully. It records rather than executes E work. The application runtime does not import the harness or acquire its trusted-process-launch facilities.

A later authorized CI service may invoke these same commands in a recorded environment. This plan supplies no hosted runner, workflow credentials, remote action versions, execution record, or publication permission. Optional local build checks are reported separately from mandatory module execution.

## 9. Cross-cutting integrity and reporting requirements

### 9.1 The Step 8 corrections remain active

**AF-001:** withhold a locally unsupported assignment and recompute the supported subset when the common frame remains valid. Preserve the original selected inventory and separately supported validity. A shared-frame defect can restrict a broader scope. [MET §4.4; VF VT-04/14]

**AF-002:** endpoint requirements stay endpoint-specific. V's text gates are not implemented here and cannot invalidate an M count merely because the source text is unavailable. Missing material that is essential to membership itself still has its ordinary evidence consequence. The later P5/P1 distinction remains in the frozen V contracts. [VF §§4,6]

**AF-003:** explicitly declared local input may be read passively. Remote locators remain metadata, and no candidate content or attached instructions can execute. [TRACE PC-01; VF VT-19]

### 9.2 M report field coverage

RF-01 through RF-20 are supported according to their applicable inputs and scope. Required metadata can be unknown/unavailable when the contract permits it, with affected claims restricted. RF-29 through RF-34 and RF-36 retain their M evidence, correction, interpretation, and readable-report responsibilities. RF-35 preserves D prerequisites and absent estimates.

RF-21 through RF-28 belong primarily to V. Phase 1 must clearly identify those computations as outside the implemented slice rather than fabricate diagnostics, contrasts, study gates, or intervals. Point estimates may remain available with uncertainty `not_estimated` or `unavailable` and an appropriate reason, as required by MET §3.2. An imported study designation or a single fixture block does not activate a V calculation.

A report must not imply externally established independent validation just because imported records contain that phrase. State the assessed scope, origin of the assessment, evidence access, and any machine-checkable or supplied substantive limitation. A fixture/mocked assessment cannot override its material role.

### 9.3 Revisions and reproducibility

Inputs, schemas, assignments, validity assessments, and corrections are pinned. Do not select an unrecorded latest revision or overwrite past outputs. Re-analysis uses a new identity where the configuration/evidence changes and preserves the original observation history. A repeat of the same pinned analysis is replay, not another generated sample.

Maintain a direct dependency list from accepted evidence/assignments to cells, metrics, prefixes, reports, and scoped claims. For M, explicit in-memory/local record associations suffice; no general lineage service or graph database is required. A schema-level issue must identify all affected M cells rather than just the favorable ones.

The registry's existence, two declarations named reviewer, a hash, a successful parse, and a deterministic test runner each establish only their actual observable property. They do not supply independent origin, valid structure, reliable model capacity, or the truth of an empirical prediction. [SC §§10-12; EI §§3-11]

## 10. Stop rules and blocker classification

| Situation | Required action | What may continue |
|---|---|---|
| Current instruction authorizes planning only | Deliver this plan and stop. | No implementation step. |
| Baseline hash mismatch or uncertain target workspace | Identify exact mismatched/ambiguous files before relying on them; obtain the correct baseline or explicit revision. | Unaffected document review. No silent reset or overwrite of an existing project. |
| Scientific definition, denominator, family boundary, or evidence meaning would need changing | Stop the affected implementation, document the conflict and proposed amendment, and obtain owner authorization. | Independently valid already-authorized work. |
| Needed code path is outside the file ledger | Request a finding-specific plan amendment before writing it. | Work within the authorized scope. |
| Local missing class evidence with a valid common frame | Withhold that assignment, retain inventory, and recalculate supported subsets. | Other supported calculations and fixture development. |
| Missing independent E evidence, model access, reviewer, or empirical collection | Restrict the corresponding scientific claim and retain UD-006/open evidence status. | All authorized M implementation and honest qualified reporting. |
| Unimplemented V/D capability | Report its absent/deferred boundary; do not create a fake result or implement it early. | M completion. |
| Safety violation, unexpected network/child-process behavior, or input/output overwrite | Stop the affected run, preserve safe diagnostics, repair under the authorized step, rerun required regressions. | Unaffected review only; no completed safety status until resolved. |
| Invalid input or resource limit | Report validation failure/affected unavailability and actual retained inventory. | Other supported scopes where no shared defect exists; never silent truncation. |
| Mandatory M test fails or is not implemented | Fix within permitted paths or report an implementation blocker. | No final M-complete declaration. |
| Optional packaging tool or hosted CI unavailable | Record the unperformed optional/deployment check; do not auto-install or fabricate a hosted result. | Required direct-module execution and local M checks. |
| Imported labels or an eventual model result disagree with the theory | Preserve the observations and apply the same evidence rules. | Honest calculation. No mandatory favorable scientific result. |
| Step 8 discovers a code/fixture defect | Return to the appropriate authorized repair step; preserve the failed audit finding. | Final completed status waits for repair and regression. |

Do not add a new numbered scientific decision for an absent API key, a future feature, an uncollected observation, or another toolkit's incomplete implementation. The plan's own engineering choices are reviewed together; small internal refactors within the allowed files need no new scientific approval when they preserve meaning, interfaces, and tests.

## 11. Final deliverables and acceptance

### 11.1 Required delivery set

Deliver the Phase 1 files from Section 4 that were authorized and implemented, the HF-00 example and independent expected oracle, the separately pinned variant design, the actual local QA outputs, and `PHASE_1_COMPLETION.md`. Keep the eleven approved Phase 0 artifacts intact alongside or clearly associated with the implementation.

The completion record must contain:

| Required record | Content |
|---|---|
| Authority | Plan version, actual execution authorizations, owner-approved changes, and exact local workspace. |
| Capability | M functionality actually delivered; V/E/D functions still absent; no full-v0.1 claim. |
| Identity | Baseline/plan/software/fixture/result fingerprints and actual tested interpreter/environment. |
| File audit | New/changed paths against the allowlist; finding-specific repairs and invariant baseline check. |
| Tests | Actual command output, concrete M bindings and results, all 54 VT scope dispositions, TR/RF coverage, limitations, and optional checks not performed. |
| Demonstration | Working local HF-00 invocation, accepted counts/metrics/prefixes, report locations, and replay result. |
| Adverse handling | Actual tests for evidence withdrawal, missing/empty data, version conflicts, unresolved mechanisms, and safe input. |
| Scientific limits | UD-006's outstanding actual evidence, UD-007 and other deferred work, and no empirical P1/P5 result from fixtures. |
| Operational limits | Packaging status, no unclaimed hosted CI, no remote writes/publication/model call/candidate execution. |
| Decision | Completed for owner review only if mandatory checks passed; otherwise explicit incomplete/blocked state. |
| Next boundary | V comparison work or another requested phase requires its own instruction; no automatic transition. |

### 11.2 Phase 1 exit checklist

- [ ] The accepted eleven-file Phase 0 baseline and plan identities are verified, with all authorized amendments recorded.
- [ ] Local `validate` and `analyze` paths run through the real M pipeline in the tested interpreter.
- [ ] Both evidence policies and all distinct knowledge/review/validity/calculation/claim axes are preserved.
- [ ] Attempt, actual realization, selection, group, position, prefix, and population accounting follow the contracts without backfill.
- [ ] All seven selected metric families, both views, exact thresholds, and all empty/error conventions are implemented.
- [ ] HF-00 and its six variants match the independent oracles; EI's correction and independence-only withdrawal behave correctly.
- [ ] All 37 applicable M test families have passing concrete checks; V/E/D parts are separately unperformed/out of scope.
- [ ] The 40 TR and 36 RF inventories have explicit M bindings or the appropriate approved non-M disposition.
- [ ] JSON/Markdown meanings match, reports are reproducible under the declared replay boundary, and private/passive input safeguards pass their actual tests.
- [ ] No V/D estimator, automatic classifier, model call, candidate runner, remote retrieval, or unrelated toolkit dependency has been introduced.
- [ ] Actual verification artifacts and an accurate completion record are delivered; no mandatory test is merely planned.

The seven selected metric families are occurrence support, empirical-threshold support, entropy, SCI, Shannon effective support, Simpson effective support, and structural distinct-k. Accounting ratios are additional mandatory context, not a new overall score.

Phase 1 is complete when this first instrument works on identified supplied evidence and fixtures, with its measurement limits visible. Actual independent evidence may later support stronger claims; its current absence cannot prevent this bounded implementation from reaching completion.

## 12. Review and immediate next action

This plan requests approval of the bounded M implementation, proposed local package/encoding/CLI choices, exact file permissions, eight execution steps, and acceptance rules above. It does not ask to reopen the adopted scientific design or wait for another project.

After approval, the next executable action is **Step 1**, or an explicitly named batch starting with Step 1. This delivery creates no implementation file, test result, model observation, repository, or hosted workflow.

**Stop point for the current instruction: deliver `PHASE_1_PLAN.md` for review.**

## Appendix A. Verified Phase 0 baseline

The following fingerprints were recomputed from the supplied files while preparing this plan. The first ten match APPROVAL §3. The eleventh identifies the delivered approval record itself. Historical status headers remain unchanged; Section 1 records the later progression decision.

| File | Version | SHA-256 |
|---|---|---|
| `PHASE_0_PLAN.md` | 0.1 | `5df37f3fef1d012d462a116d7839909c9379dfe6d59a1b3356cae004bcfac6a4` |
| `PROJECT_SCOPE.md` | 0.1 | `2eec02825c8df4281cc538d00dcb809907dc2eb8a2b1b73b597cbab17d975a11` |
| `DEFINITIONS_AND_UNITS.md` | 0.1 | `a3da3e356a21f59468178050944baf58787edd65204fbf40b3b1742cd38104ab` |
| `STRUCTURAL_CLASS_CONTRACT.md` | 0.1 | `00ba09dd879f5fe02a3302a6f1ad36bda1c6b7e2723562f5f62ec85fed125328` |
| `METRICS_SPEC.md` | 0.2 | `23b45934e87767ca87e56b97aa4e1d1abdd49e27187d0b9c5a336ca516a96edb` |
| `EVALUATION_INTEGRITY.md` | 0.1 | `50c5529c16164ee53e4d99502ed1ec24202f36152b36281870bf285185672dc3` |
| `HERO_BENCHMARK_SPEC.md` | 0.1 | `d1a0849d888a35ae3c9bd552bb920ee46417b7eeb4f8b687f8b5825e6fb851b2` |
| `THEORY_TO_CODE_TRACEABILITY.md` | 0.2 | `1b94c402804c1167bfc5c04b45a86364ac5061bc41273b87a36f184991bbeec2` |
| `VALIDATION_AND_FALSIFICATION.md` | 0.2 | `6aaa5b01290d3c6b9746f20d47c2092c038587d72d7e090ee3ad73438794ef00` |
| `UNRESOLVED_DECISIONS.md` | 0.7 | `5539ebbf859d0d423845fceb8b9ceda065f05e202d86d2ae662912aa2632a412` |
| `PHASE_0_APPROVAL.md` | 0.1 | `0d09da04ffd07568b1657ebc92c9b46fc09a489b9dde843fb1b424d048213db7` |

The theory PDF identities also match APPROVAL §4:

**SD:** `The Structural Determinacy of LLM Generation_ Active Structure, Convergence Frontiers, and the Misreading of Randomness.pdf`

SHA-256: `357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32`

**SI:** `Structural Inbreeding in Synthetic Data.pdf`

SHA-256: `80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a`

These fingerprints establish identity only. No publication cited inside the theory files was independently verified for this planning task. No theory PDF was modified or included in a software distribution.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-17 | Initial Phase 1 plan following the owner's acceptance/progression instruction; defines only the M offline implementation, eight steps, exact file boundaries, 37 M test-family obligations, preserved Phase 0 identities, and separate V/E/D and operational gates. No implementation performed. |
