# PROJECT_SCOPE

## StructDet-Bench: Product and First-Release Boundary

| Field | Value |
|---|---|
| Document version | 0.1 |
| Date | 2026-09-16 |
| Phase / step | Phase 0 / Step 2 |
| Status | PROPOSED STEP 2 BASELINE; ready for Theory Owner review |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Decision authority | Theory Owner |
| Authorization received | Proceed with Step 2 and deliver its three documents |
| Implementation / repository authorization | None |
| Related Step 2 files | `DEFINITIONS_AND_UNITS.md`; `UNRESOLVED_DECISIONS.md` |

## 1. Authority and source use

**[Owner-approved decision]** The owner's instruction to proceed authorizes Step 2 under the supplied plan. It does not approve the recommendations in these newly written documents or authorize a later step. The original plan remains unchanged; its earlier status header is preserved. The authorization record is in `UNRESOLVED_DECISIONS.md`, Section 2.

The following labels identify the basis of requirements throughout this document set:

- **[Source-derived]**: a definition, claim, or requirement from the supplied theory, with a section reference.
- **[Engineering proposal]**: a proposed product, naming, implementation, or reporting choice awaiting approval.
- **[Owner-approved decision]**: an instruction actually received from the owner.

A label governs its section until a different label is given. A mixed section identifies which part comes from which basis. Proposed requirements use “must” to describe the contract being submitted for approval; this wording does not self-approve the contract.

Source IDs follow `PHASE_0_PLAN.md`, Section 2:

| ID | Supplied source |
|---|---|
| SD | Xiangyu Guo. *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness*. August 2026. 27-page PDF. |
| SI | Xiangyu Guo. *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*. August 2026, version 1.0. 31-page PDF. |

Their file fingerprints match the plan. This step uses these supplied editions; it does not independently verify publications cited inside them. Unsettled source-to-software choices remain visible in the decision register.

## 2. Product purpose

**[Source-derived: SD §§3-5, 9, 11; SI §§3, 8]** StructDet-Bench concerns task-relative structural classes, their distributions under generation protocols, and their preservation or contraction across recursive systems. Context, consequence horizon, and analytic resolution determine which differences matter. Observed output variation, expressible support, and latent support require different evidence.

**[Engineering proposal]** StructDet-Bench will be a local, auditable measurement toolkit and benchmark specification. Its first release will accept recorded outputs and evidence-backed structural assignments, then produce protocol-bounded structural summaries and comparisons. A result must remain traceable to its input population, task/schema version, assignment evidence, and calculation convention.

The core user questions are:

1. Which task-relevant structural classes appeared under the recorded conditions, and how concentrated were their frequencies?
2. How did those observed distributions differ across prespecified generation conditions, alongside validity and realization-level variation?
3. With additional evidence in later capabilities, which classes remain elicitable, survive recursive reuse, or return after independently grounded intervention?

## 3. Scientific layers

### 3.1 Layer A: Structural Determinacy

**[Source-derived: SD §§3-6, 9]** The object is a structural distribution under a declared model and generation protocol. This layer addresses structural entropy, realization freedom, convergence at different resolutions, intervention effects, and the distinction between concentration and validity.

**[Engineering proposal]** The first implementation targets this layer through finite, classified output samples. It must identify the actual conditioning context and preserve any uncertainty about model identity or generation controls. A descriptive sample result cannot establish the full model distribution.

### 3.2 Layer B: Structural Inbreeding

**[Source-derived: SD §11; SI §§5-6, 8]** This layer concerns changes in structural support across recursive data, selection, and learning transitions. SI supplies a closed categorical resampling baseline and a broader accounting framework for neural training, preservation, and external correction.

**[Engineering proposal]** Layer B remains part of the project, with dedicated later capabilities. Comparisons between arbitrary checkpoints may show differences; a recursive-training interpretation additionally requires documented transitions and lineage. Repeated calls to a fixed model do not constitute recursive training rounds.

### 3.3 Relationship to the other toolkits

**[Owner-approved decision: governing plan §§1, 3]** Completion of Recursive Integrity Toolkit or Source Integrity Toolkit is not a prerequisite. No work on either repository is authorized here.

**[Engineering proposal]** StructDet-Bench retains ownership of its structural-class, sampling, and inference contracts. Later reuse of configuration, provenance, or reporting components requires an explicit compatibility decision. A shared component must preserve these contracts; component reuse cannot establish scientific validity by itself.

## 4. Delivery boundaries submitted for approval

### 4.1 Phase 1: first executable milestone

**[Engineering proposal; decision UD-001]** Build one offline, fixture-based Tier 1 measurement path after Phase 0 approval and a separate instruction to implement:

**Recorded realizations and assignment evidence -> input checks -> declared analysis populations -> structural summaries -> JSON and Markdown report.**

The milestone includes one task family, one approved structural resolution, imported hard assignments, explicit unresolved cases, and the following core summaries:

| First-milestone capability | Boundary |
|---|---|
| Observed structural support | Occurrence count, with a separately labeled empirical-frequency-thresholded view when requested. |
| Structural entropy and SCI | Finite-sample summaries within a declared classified population. |
| Effective structural counts | Separate Shannon-based and Simpson-based fields. |
| Structural distinct-k | One prespecified grouping and selection rule, to be finalized in Step 4. |
| Validity and classification accounting | Paired classified-all and classified-valid views, plus unresolved and unclassified counts. |
| Evidence and reporting | Recorded origin, assignment provenance, sample/group identity, unavailable conclusions, and reproducible analysis metadata. |

Fixture labels and expected calculations may exercise the software before independent empirical validation is available. Fixture output must be identified as a software demonstration. This milestone does not require real model calls, a live classifier, generated-code execution, or favorable results for a theory prediction.

The hero task is selected in Step 6. Sorting is the plan's proposed starting point, with no algorithm classes approved by this document.

### 4.2 Proposed v0.1 release

**[Engineering proposal; decisions UD-001, UD-005]** v0.1 expands the first milestone into an offline Layer A comparison workflow for that same task family:

| Area | Required v0.1 boundary |
|---|---|
| Inputs | Local structured records, configuration, recorded outputs, assignments, validity records, and evidence references. |
| Conditions | Ordinary generation, a declared higher-temperature condition, and explicit structural-divergence prompting, using precollected outputs. |
| Core calculations | All first-milestone summaries, calculated separately by compatible cell and analysis population. |
| Realization diagnostic | A limited, explicitly named surface/within-class proxy selected in Step 4. It cannot be labeled exact realization entropy. |
| Comparisons | Class occupancy and frequency comparisons, validity summaries, and the prespecified surface/structure comparison needed for P1/P5. |
| Statistical reporting | Sampling design, grouping, and a prespecified uncertainty procedure where its requirements are met. Unsupported inference is marked unavailable. |
| Auditability | Input/configuration identities, evidence lineage, classification coverage, and version-aware correction/re-analysis records. |
| Interfaces | Local command-line workflow and machine-readable JSON plus human-readable Markdown reports. |

A/B/C condition comparisons remain finite observed comparisons. v0.1 does not certify a complete or probability-thresholded expressible repertoire simply because more classes appear under Condition C.

P1 and P5 are scientific targets from SD §9.7. The software must permit supporting, contrary, and inconclusive findings. Passing software tests is independent of which result a model produces.

### 4.3 Cataloged capabilities outside the proposed v0.1 implementation

**[Engineering proposal; source references and prerequisites below]** These capabilities retain their place in the project. Their unfinished implementation details do not delay the bounded first milestone.

| Capability | Source basis | Prerequisites for a later implementation | Reason for current deferral |
|---|---|---|---|
| Probability-thresholded expressible-support estimation | SD §5; SI §§3.3, 8.1 | Admissible intervention family, probability threshold, repeated evidence, uncertainty procedure, compatible task frame. | Observed occurrence alone does not establish reliable elicitation at a specified probability. |
| Load-bearing intervention effects and convergence provenance | SD §§3.5-3.6, 6.6 | Matched interventions, consequence validation, prespecified distance and controls. | Descriptive A/B/C comparisons provide a narrower first release. |
| Convergence frontier | SD §4 | Validated resolution ordering, thresholds, stability definition, repeated tests. | One resolution and one output batch cannot locate the frontier. |
| Recursive retention and Structural Half-Life | SI §§5-6, 8.3 | Comparable rounds, documented transitions, suitable trajectory, explicit categorical-null assumptions. | First release has no training or recursive experiment runner. |
| External Recovery Rate | SI §8.4 | Reference registry, measured missing set, independently grounded intervention, validated post-intervention recoverability. | Recovery evidence requires a separate study; it can also be studied outside a multi-round trajectory. |
| Latent-support diagnostics | SD §§5.3-5.4; SI §3.3 | Approved diagnostic family and protection against reintroducing the missing solution. | Diagnostic boundaries require a separate decision; see UD-007. |
| Probabilistic, overlapping, or multi-label structural scoring | SD §§3.2, 3.7; SI §§3.1, 4.2 | Assignment-uncertainty model, validation, and compatible estimators. | First release uses adjudicated hard assignments with unresolved cases retained. |
| Semi-structured and open-ended task families | SD §9.3; SI §8.5 | Domain-specific structural contracts, independent adjudication, and disagreement handling. | One Tier 1 family provides the first validation target. |

Full realization entropy remains a theoretical quantity. No direct estimator of it is promised for v0.1; the selected proxy has its own name and limits.

## 5. Input and interface contract

**[Engineering proposal; UD-001]** Begin with JSON metadata/configuration and JSONL record collections. These format choices are submitted for approval, without an executable schema at this step. CSV, provider adapters, hosted services, and automatic retrieval are outside this initial release boundary.

The input bundle has five conceptual parts: task/protocol descriptions, recorded realizations, structural assignments, validity observations, and evidence/role records. Their authoritative initial field inventory is in `DEFINITIONS_AND_UNITS.md`, Section 9.

Outputs must preserve the distinction between a known value, an unknown value, and unavailable metadata. An input may support a limited audit even when it cannot support a fixed-model comparison or a scientific conclusion. Missing a scientific prerequisite limits the affected result; it does not manufacture a value.

Generated content is treated as data. The first release does not execute submitted code. Imported execution reports retain their origin and validation status. Local parsing and hashing establish only the properties they actually check.

Raw outputs and private evidence stay local by default. Human-readable reports should use identifiers and controlled excerpts rather than automatically copying entire inputs. Exact redaction behavior belongs to later implementation planning.

## 6. Result and claim contract

### 6.1 Required result identity

**[Engineering proposal]** Every structural summary must identify the task/schema, model identity status, actual protocol/condition, prompt block, grouping rule, analysis population, sample count, assignment evidence status, and calculation convention. The detailed vocabulary is authoritative in `DEFINITIONS_AND_UNITS.md`.

A run may contain several cells. There is no default pooled “model score.” Cross-cell aggregation requires the comparison contract from Steps 4 and 6.

### 6.2 Permitted interpretations

**[Source-derived: SD §§5, 6.5, 9.5; SI §§3.3, 8, 12]** Finite observations support protocol-bounded claims. Classification uncertainty, validity, and recoverability require separate evidence.

**[Engineering proposal]** Reports may state that specified classes appeared in a declared classified sample, that their empirical frequencies were concentrated, or that a prespecified condition produced a different observed distribution. Statements about valid structural breadth use the validity-conditioned view and disclose excluded or undetermined cases.

The standard form is:

> Observed structural support in analysis population A, under task/schema S and protocol P, based on n classified realizations. Classification coverage and validity are reported separately.

Numeric values are inserted only after authorized implementation and actual input analysis. This specification contains no benchmark results.

### 6.3 Unavailable conclusions

**[Source-derived: SD §§5, 6.5, 11-12; SI §§5.7, 12]** A narrow output sample cannot establish full model capacity, latent extinction, incorrectness solely from concentration, or an unconditional neural-training collapse rate.

**[Engineering proposal]** v0.1 must not present an overall structural-intelligence, integrity, or collapse score; identify hidden ancestry as fact; treat model self-description as verified structural membership; or count unresolved labels as new structural classes. It must not claim that different vendors establish independent evidence.

A descriptive difference across model versions is insufficient for a causal attribution to recursive training. A post-intervention appearance is insufficient to claim that a previously absent representation has been restored.

## 7. Development, measurement, and empirical-claim gates

**[Source-derived: SD §§9.4-9.6; SI §§8.5-9]** These sources require independent validation and visible lineage. SD specifies at least two independent human annotators for core validity sets; SI's Tier 1 design combines executable/formal validation with sampled human audit. Both requirements remain visible for Step 5.

**[Engineering proposal; UD-006]** Three evidence levels must remain distinct:

| Level | What may be established | Additional gate |
|---|---|---|
| Fixture-based software demonstration | Calculations and reporting follow the specified inputs and contracts. | Authorized implementation and passing software tests. |
| Validated structural measurement | Class assignments and task consequences have the required supporting evidence. | Approved structural contract and integrity protocol, with actual evidence. |
| Empirical theory comparison | A prespecified model experiment bears on P1/P5 or another named prediction. | Valid measurement plus appropriate sampling, controls, analysis, and claim review. |

AI-assisted fixtures retain that origin. Deterministic processing does not convert them into independently sourced evidence. Missing independent empirical evidence can limit scientific claims while allowing separately authorized implementation to proceed.

Software release and empirical publication require their own authorizations. This document authorizes neither.

## 8. Step 2 review boundary and later ownership

**[Engineering proposal]** Approval requested at this gate covers the proposed first milestone, v0.1 boundary, core terminology, and field semantics, together with the recommendations identified for Step 2 in the decision register.

Later documents retain their designated authority:

| Later step | Decision owned there |
|---|---|
| Step 3 | Structural equivalence, class evidence, ambiguity, hybrids, and schema correction. |
| Step 4 | Complete metric estimators, denominators, edge cases, uncertainty, and the realization proxy. |
| Step 5 | Evaluation lineage, independent validation, tail protection, and correction requirements. |
| Step 6 | One hero task, eligible classes, A/B/C protocols, budgets, and safe validation design. |
| Step 7 | Theory-to-component traceability and test/falsification specifications. |

A later step that requires changing an approved scope or definition must request that revision explicitly. These Step 2 files do not create or approve any of the later artifacts.
