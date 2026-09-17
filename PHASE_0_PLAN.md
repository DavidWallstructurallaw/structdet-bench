# PHASE_0_PLAN

## StructDet-Bench: Minimal Scientific Contract

| Field | Value |
|---|---|
| Document version | 0.1 |
| Date | 2026-09-16 |
| Status | PROPOSED PLAN; awaiting Theory Owner approval |
| Project | StructDet-Bench |
| Phase | Phase 0: measurement and implementation contracts |
| Decision authority | Theory Owner |
| Current authorized deliverable | `PHASE_0_PLAN.md` only |
| Implementation authorization | None |
| Dependency on other toolkit completion | None |

## 1. Purpose and authorization

Phase 0 establishes the minimum scientific and software contracts required to build a working StructDet-Bench prototype. Its central deliverable is a traceable agreement about the measured object, structural classification, metric semantics, validation, and permitted conclusions.

The intended transition is:

**Approved measurement contract → first executable Tier 1 benchmark → broader measurement and experimental capabilities.**

Completion of Recursive Integrity Toolkit or Source Integrity Toolkit is not an entry condition. This project may develop independently. Future component sharing requires a separate compatibility decision and must preserve StructDet-Bench's measurement semantics.

This plan authorizes no repository creation, commit, publication, implementation code, paid model calls, model training, or execution of generated programs. After approval, Phase 0 proceeds through the document steps below. Each step ends with an owner review gate unless the owner explicitly authorizes a named batch.

Approval of this plan does not approve documents that have yet to be written. Approval of the completed Phase 0 baseline establishes readiness for implementation; starting Phase 1 requires an explicit instruction to proceed.

## 2. Source basis and authority

### 2.1 Governing theory sources

| ID | Source | Relevant contribution |
|---|---|---|
| SD | Xiangyu Guo. *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness*. August 2026. Supplied 27-page PDF. | Task-relative structural equivalence; active structure; structural and realization entropy; convergence frontiers; support hierarchy; validity; convergence provenance; benchmark design. |
| SI | Xiangyu Guo. *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*. August 2026, version 1.0. Supplied 31-page PDF. | Cross-generation structural support; closed-resampling results; Structural Half-Life; structural exogamy; External Recovery Rate; benchmark protocol; Evaluation Closure. |

References such as `[SD, §9.4]` identify sections in these supplied editions. These PDFs are the theoretical basis for this phase. Their references to other publications do not constitute independent verification of those publications within this project.

### 2.2 Source-to-contract map

| Contract area | Source locations |
|---|---|
| Task, horizon, resolution, equivalence, load-bearingness | SD §§3.2-3.6; SI §3.1 |
| Structural entropy and classification uncertainty | SD §3.7; SI §4 |
| Convergence frontier | SD §4 |
| Observed, expressible, and latent support | SD §5; SI §3.3 |
| Validity and convergence provenance | SD §§6.5-6.6 |
| Recursive dynamics and categorical baseline | SI §§5-6 |
| Metrics and experiment design | SD §§9.1-9.5; SI §8 |
| Evaluation Closure | SD §9.6; SI §9 |
| Predictions and contrary evidence | SD §9.7; SI §10 |
| Boundaries of inference | SD §§11-12; SI §12 |

### 2.3 Authority and unresolved source differences

Latest explicit owner decisions govern product scope and implementation choices. The supplied sources govern descriptions of their theoretical claims. An engineering choice must be identified as an implementation proposal until approved.

Each substantive requirement must be identified as **source-derived**, **engineering proposal**, or **owner-approved decision**, with its origin recorded. A departure from a source requirement must remain visible as a declared limitation or owner-approved departure. It must never be attributed to the source.

Source differences, missing definitions, and unresolved measurement choices go into `UNRESOLVED_DECISIONS.md`. They must not be silently harmonized or replaced by general knowledge.

The following source-level distinctions require explicit treatment:

- SD uses `R` for analytic resolution; SI uses `ρ` and also introduces a reference registry. Software fields must distinguish `analytic_resolution` from `reference_registry` while preserving source notation in the theory mapping.
- SD defines effective support using `exp(H_S)`. SI defines an effective class number using `1/SCI`. These quantities must receive separate names and fields. Their shared use of an effective-count label does not make them interchangeable. [SD, §3.7; SI, §§5.3, 8.2]
- SD defines observed support using an empirical-frequency threshold; SI defines its finite-sample observed support by class appearance. The contract must identify the chosen rule and preserve any separate thresholded view. Observed occurrence and passing a probability threshold must not be silently conflated. [SD, §5.1; SI, §3.3]

## 3. Project boundary and first implementation slice

### 3.1 Two measurement layers

**Layer A: Structural Determinacy.** Measure the distribution of task-relevant structural classes under a declared model, context, horizon, resolution, and generation protocol.

**Layer B: Structural Inbreeding.** Measure how comparable structural distributions change across documented recursive rounds or model updates, including retention, concentration, and independently grounded recovery.

SD explicitly separates these within-model and cross-generation questions. SI develops the second layer. A single fixed-model output batch cannot establish a recursive training trajectory. [SD, §11; SI, §§5-6, 8]

### 3.2 Proposed delivery sequence

Phase 0 must catalog the full metric family discussed for this project. The proposed first executable slice is deliberately narrower:

- One Tier 1 task family with a validated structural-class contract.
- Precollected outputs and explicitly labeled fixtures as supported inputs.
- Observed support, concentration, structural entropy, both effective-count definitions, and structural distinct-k.
- Separate validity, classification coverage, disagreement, and unavailable-result reporting.
- A preregistered comparison of ordinary generation, higher-temperature generation, and explicit structural-divergence prompting.

Intervention-based support estimation, frontier inference, recursive trajectories, SHL, and ERR remain part of the project. Their first-release status must be decided in Phase 0. Cataloging them does not automatically authorize their immediate implementation.

This sequencing is an engineering proposal. `PROJECT_SCOPE.md` must record the approved v0.1 boundary and the smaller Phase 1 milestone separately.

### 3.3 Phase 0 economy

Use the eleven documents below. Keep one authoritative location for each definition or rule and cross-reference it elsewhere. Deferred features require a source reference, prerequisites, and a reason for deferral; they do not require a complete implementation design.

Do not introduce additional documents, task families, services, or dependency projects without a concrete need and owner approval.

## 4. Required Phase 0 artifacts

All paths are project-root-relative names. During document-only work they may be delivered as standalone files. Repository writes require separate authorization.

| File | Authoritative responsibility |
|---|---|
| `PHASE_0_PLAN.md` | Execution order, file permissions, gates, and exit conditions. |
| `PROJECT_SCOPE.md` | Product purpose, first release and first milestone, interfaces, non-goals, and allowed claims. |
| `DEFINITIONS_AND_UNITS.md` | Variables, notation, support semantics, units, thresholds, and terminology. |
| `STRUCTURAL_CLASS_CONTRACT.md` | Equivalence rules, classification, consequence validation, ambiguity, and schema revisions. |
| `METRICS_SPEC.md` | Estimands, estimators, denominators, required evidence, uncertainty, and report fields. |
| `EVALUATION_INTEGRITY.md` | Source and role lineage, independent validation, tail retention, and correction procedures. |
| `HERO_BENCHMARK_SPEC.md` | First task family, reference classes, conditions, sampling, validation, and expected report structure. |
| `THEORY_TO_CODE_TRACEABILITY.md` | Theory-to-definition-to-component-to-test-to-report mapping. Components remain planned. |
| `VALIDATION_AND_FALSIFICATION.md` | Future software tests, measurement validation, experimental controls, and interpretation of outcomes. |
| `UNRESOLVED_DECISIONS.md` | Concrete decisions, alternatives, recommendations, blocker classification, and resolution records. |
| `PHASE_0_APPROVAL.md` | Audited baseline, actual owner approval status, and bounded Phase 1 handoff. |

## 5. Execution protocol

### 5.1 Common rules

Before each step, read the approved documents on which it depends. Previously approved documents remain read-only unless their revision is explicitly authorized.

Each step must deliver its named files and a short review note containing changed files, checks completed, unresolved blockers, and the next proposed step. Review notes can remain in the conversation; they do not create another required artifact.

The decision register may be updated in Steps 2-8. It records actual ambiguities or necessary choices. Speculative improvements and distant features must not become artificial blockers.

At the end of each step, stop for owner review. A request to revise the current step authorizes that revision only. A named batch authorization may combine steps while preserving their acceptance checks and dependency order.

### Step 1. Establish the Phase 0 plan

**Allowed write:** `PHASE_0_PLAN.md`.

**Work:** Define the source basis, deliverables, execution sequence, scope controls, testing obligations, and approval rules.

**Acceptance:** The plan provides a path to implementation without requiring either other toolkit to finish. All later writes are bounded. No unproduced artifact is represented as complete or approved.

**Gate:** Present this plan and await approval before creating Step 2 documents.

### Step 2. Define scope, terminology, and the decision register

**Allowed writes:** `PROJECT_SCOPE.md`, `DEFINITIONS_AND_UNITS.md`, `UNRESOLVED_DECISIONS.md`.

**Work:**

1. Separate Layer A, Layer B, the v0.1 release, and the first executable milestone.
2. Define `C`, `T`, analytic resolution, `Y`, `Z`, generation protocol, model identity, reference registry, intervention family, and recursive round.
3. Preserve distinctions between observed support, support elicited through bounded interventions, and latent support. Document what finite experiments can establish. [SD, §5; SI, §3.3]
4. Separate valid output, structural-class assignment, task success, and external grounding. Concentration and validity require separate reporting. [SD, §6.5; SI, §12]
5. Propose the minimum interface: local structured inputs, configuration, and machine-readable plus human-readable reports. Put the initial record-field inventory in this document set; do not add a separate schema document.

The field inventory must cover task/schema version, model/checkpoint identifier, condition, prompt and sample identifiers, output reference, decoding settings, generation/grouping metadata, class assignment, validity, and evidence references. Known, unknown, and unavailable metadata must remain distinguishable.

**Acceptance:** A reader can identify exactly what a run measures, its unit of analysis, the applicable support claim, and its unavailable conclusions. The two effective-count definitions and the resolution/reference-registry notation are unambiguous.

**Gate:** Owner approves the first implementation boundary and core definitions, or requests changes.

### Step 3. Establish the structural-class contract

**Allowed writes:** `STRUCTURAL_CLASS_CONTRACT.md`, `UNRESOLVED_DECISIONS.md`.

**Work:** Require every benchmark task to declare:

- Context, consequence horizon, analytic resolution, and load-bearing invariants.
- The equivalence rule and its intended consequence signature.
- Evidence needed for class assignment and the validation method.
- Treatment of hybrids, novel mechanisms, ambiguous cases, invalid outputs, and unclassified outputs.
- Classification mode and uncertainty reporting.
- Schema version, preregistration point, and revision/re-evaluation procedure.

Structural equivalence must be supported by the task's functional or causal organization. Lexical similarity, embeddings, model self-descriptions, or a parser's label alone cannot establish it. [SD, §§3.2, 9.1; SI, §3.1]

For the proposed algorithm task, distinguish **program correctness** from **algorithm-family membership**. Identical returned values do not establish identical mechanisms. Class membership needs mechanism-relevant evidence, such as inspectable control/data flow, appropriately instrumented traces, or independent adjudication.

The recommended initial mode is a task-specific deterministic partition for adjudicated cases, with explicit unresolved cases. Probabilistic and overlapping modes remain in the theory catalog unless selected for implementation. Ambiguous assignments must never be converted automatically into extra structural classes.

Pairwise equivalence judgments also require consistency handling. An inconsistent set of pairwise judgments cannot be silently converted into a definitive partition.

**Acceptance:** The document includes conceptual examples of different wording with the same structure, similar wording with a different structure, invalid output, and unresolved classification. Each example states which evidence supports its treatment. Every proposed hero class has a route to consequence-sensitive validation.

**Gate:** Owner approves the classification contract. Task-specific class choices may remain pending Step 6.

### Step 4. Specify metrics and permitted conclusions

**Allowed writes:** `METRICS_SPEC.md`, `UNRESOLVED_DECISIONS.md`.

**Work:** For every implemented metric, define the measured quantity, estimator, input population, denominator, unit, assumptions, uncertainty, edge cases, output field, and prohibited inference.

Record the logarithm base, zero-probability convention, support thresholds, and finite-sample estimation rule. Natural logarithms with entropy in nats are the recommended convention; `exp(H_S)` requires that convention, or an explicitly equivalent base conversion.

Catalog the full family with a proposed implementation status:

| Metric family | Proposed status | Required distinction |
|---|---|---|
| Observed Structural Support Size | First executable slice | Sampled class count versus total model capacity. |
| Structural entropy and SCI | First executable slice | Estimates under a fixed classification and sampling protocol; validity reported separately. |
| Effective structural counts | First executable slice | `exp(H_S)` and `1/SCI` remain separately named. |
| Structural distinct-k | First executable slice | Define k, sampling/replacement rule, and grouping. |
| Within-class realization diversity | Limited first-slice diagnostic | Explicit observable proxy; no claim to exact full realization entropy. |
| Expressible support | Catalog; implementation decision required | Evidence from a bounded intervention family versus exhaustive support. |
| Load-bearing intervention effect | Catalog; implementation decision required | Matched intervention and prespecified distributional distance. |
| Frontier location | Later capability unless selected | Resolution ordering, concentration threshold, stability tests, and repeated evidence. |
| SHL and recursive retention | Layer B | Empirical trajectory versus categorical null; compatible round definitions. |
| ERR | Layer B or separately declared recovery study | Missing reference set, independent intervention, validated recovery, and undefined empty denominator. |

Sources: SD §§3.7, 4, 9.2; SI §§5.4, 8.1-8.4.

A field named only `N_eff` is insufficient when both definitions are supported. Recommended implementation names are `effective_support_shannon` and `effective_support_simpson`; these names require approval.

Define which results use all generated outputs and which are conditional on valid, classified outputs. Always expose excluded, invalid, ambiguous, failed, and unclassified counts. Missing classifications must not be treated as observed structural classes or silently dropped from coverage reporting.

Observed nonappearance must remain protocol-bounded. Successful elicitation supports demonstrated availability; failed finite elicitation alone does not establish latent extinction. Inference-only interventions and interventions that update model parameters require different run records. [SD, §5; SI, §§3.3, 8.4]

**Acceptance:** Each first-slice metric can be calculated and checked from a small fully specified fixture. Units and denominators are explicit. Deferred metrics carry prerequisites rather than fabricated values. No universal collapse, intelligence, or integrity score is introduced.

**Gate:** Owner approves the first-slice metric set and reporting semantics.

### Step 5. Define evaluation integrity

**Allowed writes:** `EVALUATION_INTEGRITY.md`, `UNRESOLVED_DECISIONS.md`.

**Work:** Define evidence and lineage records for the reference source, generator, structural extractor/classifier, adjudicator, and validator.

Preserve the four Evaluation Closure conditions in these supplied papers: **External Presence, Source Integrity, Tail Retention, and Corrective Capacity**. Define a minimal implementation of the Stable Core, Rotating Structural Frontier, External Incident Stream, and Versioned Tail Registry at the contract level. [SD, §9.6; SI, §9]

The contract must state:

- Different model or provider names do not prove independent evidence. Unknown ancestry remains unknown.
- A model lineage cannot serve as the sole generator, classifier, judge, and final validator.
- AI-assisted construction or labeling must be disclosed; deterministic processing alone does not establish independent origin.
- SD's core validity protocol calls for at least two independent human annotators, with disagreement and adjudication procedures. SI's Tier 1 design combines executable/formal validation with sampled human audit. These requirements must remain visible. [SD, §9.4; SI, §§8.5-8.6]
- Prototype fixture testing, validated measurement, and publishable empirical findings have different evidence requirements. Outstanding independent validation can block empirical claims while allowing clearly labeled software development.
- Corrections may revise classes, labels, and reference coverage, and must identify affected results for re-evaluation. Revisions preserve historical versions and comparability limits.

**Acceptance:** Every required independence or validation claim has an evidence field. The document identifies what can proceed during prototype development and what must wait for additional evidence. A correction scenario demonstrates how a mistaken classification affects downstream metrics.

**Gate:** Owner approves the integrity requirements and evidence-dependent release gates.

### Step 6. Lock the hero benchmark

**Allowed writes:** `HERO_BENCHMARK_SPEC.md`, `UNRESOLVED_DECISIONS.md`.

**Work:** Select one Tier 1 task family. The proposed starting point is an **Algorithm Strategy Benchmark**, initially limited to sorting. Graph traversal, path planning, search, and scheduling remain expansion candidates.

Sorting remains a proposed choice until this step is approved. The document must establish input domain, valid outputs, algorithmic constraints, class definitions, and mechanism-validation procedures. Domain restrictions must make the advertised alternatives genuinely eligible; they must not accidentally exclude classes through unstated key-type, memory, stability, or range assumptions.

Specify three conditions:

**A. Ordinary generation.** A fixed baseline protocol.

**B. Higher-temperature generation.** Matched task and prompt conditions with a declared decoding change.

**C. Structural-divergence generation.** Explicit requests for non-equivalent mechanisms under a declared protocol.

Prespecify prompt templates, model/decoding metadata, sample budgets, output grouping, retry rules, generation limits, validity checks, exclusions, and the budget-matching policy. Unsupported provider controls must be recorded as unavailable.

If Condition C generates coordinated sets of answers, its outputs must not be analyzed as independent draws equivalent to Condition A's single-answer calls. The comparison unit and resource accounting must make this distinction explicit.

The experiment targets SD's P1 and P5. P1 compares changes at surface and structural levels; the analysis must prespecify comparable effect summaries rather than subtracting quantities with incompatible units. P5 compares structural breadth while accounting for validity and generation resources. [SD, §9.7]

Set a small prompt suite and an aggregation method. Repeated outputs from one prompt provide limited evidence about other prompts. SD recommends prompt-level aggregation and uncertainty estimation. Pilot outputs must be separated from confirmatory evaluation, with any post-pilot changes versioned. [SD, §9.5]

For generated code, specify isolation, resource limits, prohibited capabilities, and handling of unsafe or nonterminating submissions before execution is implemented. Generated programs must never run directly in the host environment with unrestricted filesystem, network, or process access.

**Acceptance:** Another implementer could reproduce the planned task, classification, comparison, and report without inventing a missing scientific rule. The plan distinguishes a fixture-based software demonstration from an actual model experiment. No empirical results are invented and no experiment is run in Phase 0.

**Gate:** Owner approves the hero benchmark and all first-milestone execution prerequisites.

### Step 7. Map theory to implementation and specify tests

**Allowed writes:** `THEORY_TO_CODE_TRACEABILITY.md`, `VALIDATION_AND_FALSIFICATION.md`, `UNRESOLVED_DECISIONS.md`.

**Work:** Create a traceability row for each first-slice requirement:

**Source section or approved design decision → definition → planned component → test specification → report field → permitted inference → limitation.**

Planned component names must not imply existing code. They may cover input validation, class/evidence handling, metric calculation, comparison, provenance, and reporting without fixing a large repository architecture.

Specify future tests using the matrix in Section 6. Separate mathematical/software correctness, structural-measurement validity, and empirical outcomes.

P1 and P5 remain testable predictions. Contradictory or inconclusive results must be reportable without changing categories, filtering rules, or success criteria after inspection. Passing software tests must never require an evaluated model to confirm either prediction. [SD, §9.7]

**Acceptance:** Every first-slice report field has a test and an inference boundary. Every named prediction has an operational comparison, relevant controls, and rules for interpreting contrary or inconclusive evidence.

**Gate:** Owner approves traceability and the validation plan.

### Step 8. Perform the integrated Phase 0 audit

**Allowed writes:** `UNRESOLVED_DECISIONS.md`; corrective revisions to the eight specification documents created in Steps 2-7, limited to explicitly identified audit findings.

`PHASE_0_PLAN.md` remains read-only unless the owner authorizes a plan amendment. Do not create `PHASE_0_APPROVAL.md` during this step.

**Work:** Check cross-document consistency, source fidelity, definitions, metric formulas, denominator policies, task eligibility, classification evidence, evaluation roles, test coverage, and claim boundaries.

For each correction, report the finding, affected documents, proposed resolution, and whether it changes an approved scope or scientific decision. Such changes require renewed owner approval before the affected baseline is frozen.

Classify remaining decisions as:

| Class | Effect |
|---|---|
| Implementation-blocking | Prevents the bounded Phase 1 milestone from being implemented correctly or safely. |
| Empirical-claim-blocking | Allows identified prototype work but blocks a specified scientific or publication claim. |
| Deferred | Outside the approved milestone; does not delay Phase 1. |

**Acceptance:** No unresolved implementation blocker remains. Other open items have explicit effects, owners, and evidence requirements. Cosmetic expansion and distant ambitions do not become new exit conditions.

**Gate:** Present the audit and await owner acceptance before preparing the approval record.

### Step 9. Prepare the approval record and Phase 1 handoff

**Allowed write:** `PHASE_0_APPROVAL.md`.

**Work:** Record the audited baseline, approved scope, source identities, document versions, remaining claim restrictions, and the first implementation milestone.

Include hashes of the ten preceding Phase 0 documents. The approval document records its own revision separately and must not contain a self-referential file hash.

Record actual approval evidence only. Until the owner explicitly approves this baseline, use **READY FOR OWNER REVIEW**, with approval fields left pending. Do not self-approve the project or infer final approval from approval of earlier steps.

The handoff must name the first executable capability, its required tests, deferred features, allowed initial claims, and any unfulfilled evidence requirements. Any detailed Phase 1 execution plan is a subsequent deliverable outside Phase 0.

**Acceptance:** The baseline is identifiable and reproducible. Readiness, actual approval, and permission to begin implementation are distinguishable.

**Gate:** Deliver the approval record and stop. After explicit owner approval and instruction to proceed, Phase 1 may begin without waiting for either other toolkit.

## 6. Required testing specifications

Phase 0 defines these tests and expected outcomes in prose or non-executable fixture tables. It does not create test code or claim that implementation tests have passed.

| Test area | Minimum required specification |
|---|---|
| Mathematical fixtures | One occupied class; balanced classes; unequal frequencies; zero-count reference classes; explicit expected support, entropy, SCI, and both effective counts. |
| Effective-count distinction | An unequal-frequency fixture for which `exp(H_S)` and `1/SCI` differ, preventing accidental interchange. |
| Order and labeling invariance | Aggregate distribution metrics survive input reordering and bijective class renaming; order-sensitive distinct-k procedures declare their behavior. |
| Missing and invalid evidence | Empty input, wholly invalid outputs, mixed validity, unclassified outputs, conflicting labels, and explicit unavailable metrics. |
| Structural equivalence | Same structure with different realization; different mechanism with similar wording; hybrids; unresolved equivalence; consequence-sensitive checks. |
| Validity separation | A concentrated valid batch, a concentrated invalid batch, and a diverse batch containing invalid outputs remain distinguishable. |
| Protocol comparability | Different schema versions, prompt groups, checkpoints, budgets, output-set dependencies, or decoding conditions cannot be silently pooled. |
| Correction propagation | A label or class revision identifies affected results and creates a versioned re-evaluation path. |
| Reproducibility | Input/configuration/schema identity; deterministic calculations; recorded seeds for any stochastic estimator; explicit limits on provider reproducibility. |
| Execution safety | Unsafe, nonterminating, malformed, or resource-exceeding generated programs have specified outcomes before execution support is enabled. |
| Deferred metric boundaries | SHL requires a suitable trajectory and explicit null assumptions; ERR has no numeric value when its missing-reference denominator is empty. |
| Prediction testing | P1/P5 comparisons can return supporting, contrary, or inconclusive evidence independently of software test success. |

Uncertainty procedures must respect the actual sampling design. A batch of dependent generations cannot acquire an artificial independent sample size through formatting or row expansion.

## 7. Stop rules and prohibited advance work

### 7.1 Immediate stop conditions

Stop the affected step and present the exact blocker when a necessary source is unavailable, a structural distinction lacks a validation route, an input population or denominator remains ambiguous, a required prior decision is unresolved, or the next action exceeds the step's file permissions.

Also stop the affected capability when it requires unsupported independence claims, unsafe generated-code execution, post-result changes to confirmatory criteria, or access/expense the owner has not authorized.

An empirical validation gap blocks the corresponding empirical claim. It need not block unrelated specification work or clearly labeled fixture-based implementation once authorized. Deferred Layer B or open-ended-domain questions must not hold the first Tier 1 milestone indefinitely.

### 7.2 Prohibited during Phase 0

Do not write package code, tests, runners, executable schemas, provider adapters, CI workflows, training scripts, web interfaces, or automatic structural classifiers. Human-readable field tables and non-executable examples are allowed.

Do not call model APIs, incur costs, run generated programs, produce benchmark scores, alter either other toolkit, create or commit a repository, or publish the supplied PDFs under this plan.

Do not add a universal structural-intelligence or collapse score. Do not infer hidden ancestry, full latent support, or representational extinction from an output batch. Do not convert the categorical closed-resampling results into an unconditional neural-training forecast. [SD, §§5, 12; SI, §§5.7, 12]

## 8. Phase 0 exit conditions

The baseline is ready for final approval when all eleven artifacts exist and the following conditions hold:

- [ ] The theory sources and their exact editions are recorded.
- [ ] Layer A, Layer B, v0.1 scope, and the first implementation milestone are separated.
- [ ] Context, horizon, resolution, class assignment, validity, and support semantics are defined.
- [ ] Structural equivalence has a task-specific validation route; uncertainty and disagreement remain visible.
- [ ] Every first-slice metric has an estimator, unit, denominator, edge-case rule, and permitted inference.
- [ ] The two effective-count definitions have distinct names and tests.
- [ ] One hero task family, its eligible classes, and its safe validation approach are approved.
- [ ] P1/P5 protocols, resource accounting, analysis units, and interpretation rules are prespecified.
- [ ] Evaluation lineage, independent validation requirements, tail retention, and correction procedures are documented.
- [ ] Each first-slice requirement maps to a planned component, test, and report field.
- [ ] The integrated audit has no unresolved implementation blocker.
- [ ] Deferred features and outstanding empirical-claim requirements remain explicit.
- [ ] The final approval record identifies the exact baseline and accurately records owner approval status.

**Phase 0 succeeds when an implementer can build the first measurement pipeline without inventing its scientific meaning during coding.** Favorable experimental results are not an exit condition.

## Appendix A. Supplied source fingerprints

These SHA-256 values identify the supplied files used to prepare this plan. They establish file identity only.

**SD**

File: `The Structural Determinacy of LLM Generation_ Active Structure, Convergence Frontiers, and the Misreading of Randomness.pdf`

SHA-256: `357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32`

**SI**

File: `Structural Inbreeding in Synthetic Data.pdf`

SHA-256: `80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a`
