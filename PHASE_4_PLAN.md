# StructDet-Bench Phase 4 Plan

> Engineering precedence: `VERIFICATION_POLICY.md` supersedes this plan's cumulative historical test identities, inherited phase gate execution, and recurring administrative pin requirements. `VERIFICATION.md` describes the current canonical regression, release qualification, and inactive historical archive. The numbered scientific capability scopes and evidence limits below remain applicable.

## Empirical Study Preparation, Evidence Integration, and Controlled Validation

**Document version:** 0.1  
**Prepared:** 2026-09-21  
**Status:** Proposed plan, awaiting owner adoption; implementation has not started.  
**Project:** StructDet-Bench  
**Predecessor:** Phase 3 Step 10, commit `8988b3ca41ee9e62f98d80309bee7f4d8d794fe6`.

This plan turns the approved sorting study and evidence rules into a usable offline research workflow. Phase 4 adds study registration, reference-material accounting, independent review records, collection and extraction records, external-validation receipts, and compilation into the existing analysis profiles. A separately activated empirical stage can use those tools for the first bounded sorting study when actual reviewers, suitable external execution, collection access, and an approved budget are available.

This document contains proposed engineering decisions. Scientific definitions and study-design choices inherited from the approved contracts retain their existing authority. A plan, a generated reference draft, a test fixture, and a completed independent observation have different evidential roles throughout the workflow.

The present request authorizes preparation and delivery of this plan. It does not start Step 1. Later instructions to start a numbered implementation step authorize its stated local work and ordinary reversible verification. Separate operational activities are assessed against the authorization already present in the session; authorization is not requested twice.

## 1. Outcome and completion model

### 1.1 Intended usable outcome

A researcher can prepare a pinned study workspace, see exactly which planned artifacts and evidence are missing, distribute blind review material through an authorized channel, import original external records, and compile eligible observations for the established StructDet-Bench analysis commands. Every reported label, validity judgment, selected realization, and restriction can be traced to its source and revision.

The first empirical target remains `bounded_integer_sort/0.1`, with the fixed A/B/C design in `HERO_BENCHMARK_SPEC.md`. Phase 4 implements that design's operational records. It does not redefine structural equivalence, select a new ontology, change the approved metrics, or expand the study into model training.

The concrete architecture is **offline preparation and evidence import**. Collection and hostile-program validation occur in separately authorized external processes. No provider-specific live API adapter or executable candidate runner is added to the toolkit in this phase.

### 1.2 Separate statuses

The completion document and study reports must expose these independent facts:

| Status axis | Meaning and completion evidence |
|---|---|
| Software implementation | Phase 4 requirements P4-W01 through P4-W40, actual tests, inherited M/V/L gates, and clean replay. |
| Study readiness | Readiness for each named activity: core construction, external validation, human review, pilot collection, main collection, analysis, or release. |
| Empirical evidence | P4-E01 through P4-E12 assessed for a named study version and claim; actual records, missing evidence, and justified scope restrictions. |
| Repository delivery | Locally prepared, remotely delivered, and remote tree verified are separate observations. |
| Owner acceptance | A distinct owner decision; neither test success nor a branch write establishes it. |

Two bounded handoffs are possible. A software handoff completes the offline workflow with all software requirements passing while the empirical study remains explicitly pending or restricted. A study handoff additionally supplies the actual qualified evidence and only those conclusions it supports. The phrase “Phase 4 complete” must always identify which handoff occurred.

UD-006's approved procedure remains in force. Actual evidence can satisfy its requirements for a specified claim, domain, version, and period; Phase 4 cannot close it globally for all future studies. UD-007 remains deferred. The new workflow supplies no latent-capacity estimator or diagnostic-recovery claim.

## 2. Frozen predecessor and source authority

### 2.1 Verified starting point

Planning-time read-only checks established the following baseline. The verification companion contains the file inventory, archive checks, source identities, and remote read receipts.

| Item | Verified identity or scope |
|---|---|
| Delivery branch | `phase3-step10-delivery` |
| Delivery commit | `8988b3ca41ee9e62f98d80309bee7f4d8d794fe6` |
| Delivery tree | `170f0e7905da47562b5811487a42736d2db586c4` |
| Sole parent | `179590347ba037cca636876ce3ec5563d6b778f7` |
| Current `main` | `9ea6fef61fb68cf8a9b0d07987080e37a6fb5850`; it is an older baseline and is not the Phase 4 starting tree. |
| Project inventory | 180 source/delivery files; every local file matches the frozen Step 10 manifest, final local archive, and remote blob. Interpreter caches are excluded from the project inventory and separately listed. |
| Inventory SHA-256 | `153de535257bdb67202264b5d1f2b61f708b13bc0841e35ed0993dace4b281f3` |
| Inventory encoding | UTF-8, path-sorted rows: SHA-256, two spaces, relative path, LF. |
| Step 10 local archive | `StructDet-Bench_Phase3_Step10_Local.zip`; 65,745,823 bytes; 381 entries; CRC checks passed. |
| Archive SHA-256 | `9edbad00cc363daff5a94119072203e894075e76ce9a5f9e6a166d7e9f4d9423` |
| Phase 3 plan SHA-256 | `1ca74fbba06bea44f2b656b3f4e6b46b0c6747cf13640c3f1ea29c69ef3d6352` |

The inherited current and clean runs are `9c20c5d7beec4311a981d1e149663f58` and `bf8d609c243f49ebab1507ca236e2889`. Each contains 1,817 unique discovered methods, all passed, including the original 1,018 Phase 2 methods. All 40 Phase 3 L obligations, 16 report groups, and 24 oracle groups passed their actual bindings. The planning audit verified the six referenced run/console/subject-receipt files by byte size and SHA-256. It did not rerun those tests.

Phase 3's implementation remains Step 9. Step 10 finalized four administrative paths: `PHASE_3_COMPLETION.md`, `README.md`, `LONGITUDINAL_FORMAT.md`, and `artifacts/phase3/verification_manifest.json`. The other 176 files remained unchanged. Preserve this distinction when describing tested code and final administrative delivery.

The supported predecessor environment was CPython 3.13.5, Unicode 15.1.0, Linux 6.18.44 x86_64 with glibc 2.39, using `-B -S`. Phase 4 initially retains this declared software verification environment. It is not a security certification or a declaration of the current/latest interpreter. An external candidate validator has its own independently reviewed environment identity.

### 2.2 Authority order

Apply the following sources together, resolving apparent conflicts explicitly:

1. The owner's explicit decisions and `PHASE_0_APPROVAL.md`, including the approved procedure for UD-006.
2. The pinned original theory sources, `PROJECT_SCOPE.md`, `DEFINITIONS_AND_UNITS.md`, `STRUCTURAL_CLASS_CONTRACT.md`, `METRICS_SPEC.md`, `EVALUATION_INTEGRITY.md`, `VALIDATION_AND_FALSIFICATION.md`, and `HERO_BENCHMARK_SPEC.md`.
3. `BASELINE_UPDATE_EC_001.md` and `EVALUATION_CLOSURE_ADDENDUM.md`, including the narrowly identified five-condition update.
4. Existing physical contracts `INPUT_FORMAT.md`, `COMPARISON_FORMAT.md`, and `LONGITUDINAL_FORMAT.md`, and the completed Phase 1 through Phase 3 implementation/evidence.
5. This plan's additive workflow design and the future `STUDY_FORMAT.md` and `EMPIRICAL_PROTOCOL.md` within its scope.

If implementing a proposed record would require changing an approved meaning, record a proposed amendment and its consequences before changing that meaning. A new document cannot silently override a frozen contract. Keep the original documents, plans, completion records, matrices, and historical run evidence intact.

### 2.3 Source-to-workflow crosswalk

The following page numbers refer to the supplied PDF files. SD, SI, and EC denote their titles in Appendix A. Source inspection included extracted text and rendered SD p.19, SI p.20, and EC p.13.

| Source requirement | Phase 4 consequence | Main checks |
|---|---|---|
| SD §9.4, p.19: independent human core annotation, blinding, role separation, disagreement and adjudication | Preserve two genuine independent initial human records for every core artifact; use an independent expert for disputes; record limitations to blinding. | W12-W16; E03-E04 |
| SD §9.7 and approved prediction mapping: claims must admit contrary evidence | Keep the fixed P1/P5 operands and all registered outcomes, including negative, null, mixed, and inconclusive results. | W29-W30; E09 |
| SI §§8.5-8.6, pp.19-20: Tier 1 domain evidence, sampled human audit, lineage separation, counterfactual checks | Import functional and mechanism evidence separately; audit the fixed main positions plus targeted cases; retain external contribution and substitution evidence. | W08-W11, W21-W25; E02-E07 |
| EC §6, pp.9-10: type-appropriate validation | An execution claim needs actual execution evidence; functional agreement alone cannot establish mechanism membership. | W10-W11, W22-W24; E02, E05 |
| EC §7, pp.10-11: five conjunctive conditions | Track Structural Validity, External Presence, Source Integrity, Tail Retention, and Corrective Capacity separately for each claimed scope. | W25-W27, W33; E10-E11 |
| EC §10, p.13: ten reporting disclosures | Display all ten fields, including absent live/field evidence, correction action, and currentness limits. | W33; E11-E12 |

The four architectural components remain Stable Core, Rotating Structural Frontier, External Incident Stream, and Versioned Tail Registry. They are distinct from the five conditions. An operational openness claim requires all five applicable conditions. Missing mandatory evidence cannot become `not_applicable`, and four satisfied conditions cannot compensate for an unresolved fifth condition.

## 3. Scope and invariants

### 3.1 Additive capabilities

Phase 4 supplies a versioned study envelope; passive reference and validation manifests; blind review packages; immutable initial annotations and adjudication records; planned call and candidate-position ledgers; exact response extraction; evidence qualification; compilation to existing input profiles; readable readiness and provenance outputs; and a documented external operating procedure.

The default empirical route is the sorting A/B/C hero. A supplied longitudinal study can be compiled only through an explicitly selected existing longitudinal profile, with actual state, transition, trial, and evidence records required by `LONGITUDINAL_FORMAT.md`. A/B/C conditions and repeated collection groups are never synthesized into training rounds, recovery interventions, or half-life observations.

The Source Integrity Toolkit and Recursive Integrity Toolkit remain separate projects. A compatible export can be mapped as an explicitly identified external input. This plan introduces no cross-project dependency, shared score, automatic connector installation, or transfer of another project's claim authority.

### 3.2 Preserved semantics

| Dimension | Required behavior |
|---|---|
| Structural assignment | Reuse the existing assignment states, descriptor meanings, branch evidence, and population rules. An accepted assignment needs the applicable evidence. |
| Validity | Preserve `valid`, `invalid`, `undetermined`, and `not_assessed`. A resource timeout alone does not prove nontermination or task invalidity. |
| Knowledge | Preserve `known`, `unknown`, `unavailable`, and justified `not_applicable`; unknown evidence does not become false or zero. |
| Evidence policy | Preserve `fixture_only` and `adjudicated_import`. Fixtures retain stipulated provenance in every export. |
| Requirement outcome | Preserve `satisfied_for_scope`, `unsatisfied`, `unresolved`, and justified `not_applicable`. |
| Claim disposition | Preserve `supported_for_scope`, `restricted`, and `withheld`, separately from numeric availability. |
| Existing metrics | Reuse M/V/L calculations, units, denominators, thresholds, undefined cases, uncertainty conventions, and report semantics. |
| Corrections | New versions preserve originals and identify affected artifacts, evidence, assignments, cells, comparisons, and reports. |
| Data handling | Source code, model responses, attachments, imported traces, and reviewer text remain passive data. |

Missing essential membership evidence withholds the corresponding accepted assignment under `adjudicated_import`. Missing independent-review evidence can restrict a stronger claim while label-conditioned arithmetic remains available under the existing rules. The workflow must preserve both distinctions.

### 3.3 Work outside the implementation scope

This phase adds no model training, automatic classifier or model judge, online collection API, candidate execution facility, installed sandbox, new metric family, adaptive sampling, automatic schema expansion, hosted dashboard, hosted CI claim, or automatic publication/merge. It makes no universal capacity, creativity, collapse, causal recovery, or intelligence ranking claim.

Actual collection, reference construction, human review, and external validation can occur in Step 11 only within their concrete operational scope. Preparing records for those activities is ordinary implementation work in the earlier steps.

## 4. Fixed first-study design

### 4.1 Domain, classes, and reference materials

Pin all five identifiers:

| Role | Identifier |
|---|---|
| Task | `bounded_integer_sort/0.1` |
| Resolution | `sorting_mechanism_family/0.1` |
| Schema | `sorting_mechanism_partition/0.1` |
| Registry | `sorting_reference_eight/0.1` |
| Validity rubric | `bounded_integer_sort_validity_v1` |

The task is self-contained Python 3 `sort_values(values)`: a plain list of plain integers, excluding booleans, length 0 through 256, values 0 through 4095; return a fresh plain list in nondecreasing order with the same multiplicities and unchanged caller input. Preserve the approved exclusions on imports, built-in/external ordering, dynamic execution, reflection bypass, randomness, file/network/process access, and persistent cross-call state. These task restrictions do not constitute containment.

The eight registered IDs are `SORT-ADJ`, `SORT-INS`, `SORT-SEL`, `SORT-MERGE`, `SORT-PIVOT`, `SORT-HEAP`, `SORT-COUNT`, and `SORT-RADIX`. Their full constitutive descriptors and permitted variations remain in HERO §4.2. Names, comments, plausible explanations, and correct outputs alone cannot select a family.

Materialize a catalog for `sorting_core_32/0.1`:

| Core roles | Count | Evidence required before the intended role is accepted |
|---|---:|---|
| `CORE-<family>-A/B` | 16 | Two implementations per class with a permitted variation, membership arguments, witnesses, complete validity evidence, and two independent human initial judgments per artifact. |
| `CORE-<family>-D` | 8 | A concrete defect and counterexample, plus evidence that the defining mechanism remains identifiable or a recorded revision of the proposed case. |
| `CORE-X01` through `CORE-X08` | 8 | The eight specified boundary/negative cases in HERO §6.1, with actual evidence and legitimate unresolved outcomes retained. |

The `<family>` component uses the eight suffixes `ADJ`, `INS`, `SEL`, `MERGE`, `PIVOT`, `HEAP`, `COUNT`, and `RADIX`. A catalog slot is not an artifact and an artifact is not a validated reference. Core construction is a later operational activity; Step 3 prepares all 32 role specifications without inventing completed programs or labels.

All 32 actual artifacts need two distinct human initial records, at least 64 item-level first-pass records in total. This does not require 64 people. Multiple AI agents, model personas, or repeat judgments by one person do not meet the two-human requirement. Preserve the original first passes before discussion; report initial agreement and disagreements separately from adjudicated results.

Schema review must examine all 28 unordered descriptor pairs, the `ADJ/INS`, `SEL/HEAP`, `MERGE/PIVOT`, and `COUNT/RADIX` distinctions, and at least two nontrivial shapes for each positive reference. Use W-01 through W-04 exactly as declared in HERO §4.4, including W-03 for the whole-key versus proper-digit boundary. Record actual same-class renaming/helper-layout checks and mechanism-changing substitutions. Written check intentions do not satisfy execution or review evidence.

Reference retention preserves the two positive variants and a reviewed defect/boundary record for every family. `SORT-COUNT` and `SORT-RADIX` retain explicit W-03 and boundary protection. This is a reference-design obligation, without an inference of empirical rarity or superiority.

### 4.2 Functional validation inventory

Generate the approved ordered list of **8,995 test identities** without RNG:

| Segment | Construction and order | Count |
|---|---|---:|
| V-SMALL | Lengths 0 through 4 over `[0, 1, 255, 256, 4095]`, length order then lexicographic order. | 781 |
| V-SHAPE | Lengths 8, 64, 256, each with the six ordered patterns in HERO §5.3. | 18 |
| V-KEY | Each x from 0 through 4095, singleton `[x]` then `[4095-x, x]`. | 8,192 |
| V-STAGE | W-01, W-02, W-03, W-04 in order. | 4 |

Retain repeated equal lists under their distinct test IDs and purposes. The trusted external oracle checks fresh plain-list identity, plain-integer elements, length, adjacent ordering, frequency preservation, and unchanged caller input. Oracle implementation and artifact/input association require independent review.

An accepted `valid` record requires complete suite coverage plus source/interface/operation conformance under the declared rubric. A decisive counterexample can establish scoped invalidity without running the remainder. Harness failure, incomplete coverage, or resource exhaustion without a decisive violation remains limited evidence. Passing 8,995 inputs is bounded tested evidence and is not exhaustive correctness over every permitted list. Any alternative proof route needs identified assumptions and a separately approved comparability decision.

### 4.3 Calls, controls, and budgets

All conditions request five candidates in one fresh coordinated call. A and B have byte-identical visible prompts for a given block; their declared temperature differs. C uses the exact mechanism-variation clause from HERO §7.2 and A's controls. Materialize the source's exact openers, common task text, clauses, and output format without paraphrasing them.

| Control | A | B | C |
|---|---|---|---|
| Temperature | 0.4 | 1.0 | 0.4 |
| Top-p | 1.0 | 1.0 | 1.0 |
| Presence/frequency penalties | 0 where exposed | Same | Same |
| Candidate positions per call | 5 | 5 | 5 |
| Output allowance | 8,192 model-token units | Same | Same |
| Seed | No user-fixed seed requested | Same policy | Same policy |
| Context/tools | Fresh context, no prior outputs, no tools requested | Same | Same |

Record exposed and hidden controls, actual cap semantics, actual sent bytes, system/developer wrapper knowledge, deployment identity and drift, output selection, time, request IDs, and observable retries. Do not invent inaccessible provider details. A deployment without a meaningful temperature manipulation cannot support the registered P1 experiment; any narrower A/C use needs an explicitly scoped registration.

| Collection | Calculation | Calls | Planned positions | Maximum declared output allowance |
|---|---|---:|---:|---:|
| Optional pilot P00 | 1 block × 3 conditions × 2 groups | 6 | 30 | 49,152 |
| Main P01-P06 | 6 blocks × 3 conditions × 4 groups | 72 | 360 | 589,824 |
| Combined maximum | Pilot plus main | 78 | 390 | 638,976 |

These are planned output allowances. Actual output, input, hidden reasoning, compute, and monetary cost are separate records; unavailable quantities remain unknown. No model, provider, price, or monetary ceiling is selected by this plan. Step 10 prepares a concrete operating packet using current verified provider information if an operation is requested.

Follow the registered main order: group index g first, block b second, and condition permutation `(b + g - 2) modulo 6` from `[ABC, ACB, BAC, BCA, CAB, CBA]`. Keep all planned slots. One registered attempt belongs to each slot; disable automatic retries where possible and disclose hidden retry uncertainty. Failed calls, refusals, poor quality, and duplicate mechanisms do not trigger replacement sampling.

Each cell contains 20 planned positions from four coordinated calls. Candidates within a call are dependent. The fixed prefixes are k=5, 10, and 20 in group/position order, with P5 primary k=20. Missing positions never compress later observations into an earlier prefix. Nineteen realizations do not form a complete distinct-20 result. A complete 20-realization cell with no accepted classes can have an observed classified count of zero with zero classification coverage under the existing rules.

### 4.4 Extraction and audit

Preserve each original response before extraction. Associate a position only through the exact registered unique heading and fence rules. Keep candidate bytes, whitespace, comments, source hash, and byte offsets. Do not select a preferred fence, repair code, complete a truncated program, renumber positions, or discard inconvenient outputs. Retain raw extras without adding them to the selected population. A uniquely identifiable truncated body has its actual extent and limitation recorded.

Distinguish an emitted empty realization, an absent position, a refusal with a response, and a failed call with no response. The last case does not create five fictitious failures. The extraction specification in HERO §8 remains authoritative.

Select one planned human-audit position for every main group using `1 + ((b + c + g - 3) modulo 5)`, with b=1..6, c=`A=1,B=2,C=3`, and g=1..4. This produces 72 planned positions. A missing selected artifact remains a missing audit opportunity. Each available selection receives at least one qualified independent human review, blind to initial label and condition where feasible.

Targeted audit additionally covers relied-upon unresolved disputes or novel/hybrid candidates, challenged essential evidence, all accepted class occurrences with count one or two in a 20-realization cell, and at least one observed occurrence of each class per condition across the suite where available. Deduplicate artifact identity while retaining every selection reason. The maximum is 360 distinct main artifacts. These reviews create no extra generator observations and estimate no random population error rate.

### 4.5 Analysis and claim limits

Reuse the implemented P1 and P5 decision mapping and numerical oracles. P1 uses B-A surface gain, structural-pair gain, and their contrast, with `classified_all` primary and `classified_valid` sensitivity. P5 reports C-A and C-B valid distinct-20 contrasts separately, with all-classified companions and validity accounting. Surface and structural pair diagnostics use identical eligible samples.

Use equal weights over the six fixed blocks, the existing 2,000 paired block resamples, seed 20260917, and the established generator/quantile convention and replay manifest. Label ranges `prompt_resampling_sensitivity`. Do not treat 360 positions as independent prompts or generalize a six-phrasing sensitivity range to a prompt population. Missing/incompatible blocks restrict the registered full-suite claim; a descriptive subset must identify every omission and keep linked P1 components on the same block set.

Preserve the main gates from HERO §10.3: complete planned groups; classification coverage at least 0.90; decisive validity coverage at least 0.95; valid-output structural coverage at least 0.90 when defined; usable proxy text at least 0.95 with at least two eligible realizations; P5 valid fraction at least 0.80 and absolute paired quality difference at most 0.10. Evidence and comparison-frame requirements also apply. For P1, the floor/band retain their existing diagnostic and qualified-interpretation roles. Do not silently make a P5-only gate determine all raw P1 availability.

The 0.10 frequency threshold is a secondary descriptive view. Surface distance at least 0.95 and observation of all eight registered families retain their ceiling diagnostics. Neither diagnostic authorizes another proxy, new families, more sampling, or favorable subset selection. Report all primary contrasts together, preserve contrary evidence, and make no familywise-significance claim from multiple nominal ranges.

## 5. Proposed record architecture

### 5.1 Study envelope and evidence graph

Add a separate `study_schema_version: "0.1"` envelope in `STUDY_FORMAT.md`. It is an operational format; compiled analysis bundles retain their existing input/profile versions. Step 2 fixes the complete field-level grammar, enumerations, foreign keys, error codes, and canonical serialization before later modules depend on it.

| Record family | Required content |
|---|---|
| Study registration | Immutable study/version identity; claim scope; source/task/schema/registry/rubric pins; material role; requested existing analysis profile; exact protocol; preregistration record; exposure and currentness. |
| Activity readiness | Activity identity; concrete prerequisites; evidence references; outstanding requirements; responsible operator; authorization reference where applicable. |
| Core catalog | All 32 stable role IDs; desired contrast; actual artifact reference or explicit missing material; source/AI assistance; exposure; version and supersession. |
| Artifact | Exact original bytes or a locally supplied bounded file; SHA-256 and size; original source; transformations; role; identity distinct from label. |
| Validation receipt | Artifact and suite hashes; test-ID coverage; trusted observations and counterexamples; conformance review; environment/oracle identity; limits; termination and harness status. |
| Human review | Real reviewer identity in a restricted roster; qualifications and relationships; blinding/exposure; independent initial submission; mechanism and validity judgments; evidence references. |
| Adjudication | Preserved initial submissions; disagreement; independent expert and basis; resulting decision; unresolved issues; scope/version; no overwritten first pass. |
| Collection ledger | Every planned call and candidate position; order/control identity; actual attempt and original response association; failure/retry/drift records; actual usage knowledge. |
| Extraction | Exact heading/fence association, byte ranges, retained extras, completion/format limitations, selected versus missing positions. |
| Audit selection | Systematic position formula, targeted reasons, missing opportunities, distinct artifact counts, actual review links. |
| Correction/incident | Challenge and provenance; affected references; reviewer authority; proposed versus performed action; supersession; rollback and re-analysis links. |
| Compilation receipt | Input snapshots and versions; accepted/withheld dispositions; original-to-compiled ID map; target profile; output hashes; unresolved scope restrictions. |

Require unique identities, explicit revision relationships, reference types, and compatible scope/version pins. Reject cycles in supersession or dependency edges where the relation requires acyclicity. Preserve admissible source-lineage relationships without assuming that all relationships form one acyclic graph. Unknown fields, duplicate keys, nonfinite numbers, ambiguous paths, and inconsistent references fail with stable diagnostics under the declared physical grammar.

Hashes identify supplied bytes. They do not prove that a human reviewed them, that execution occurred, or that a registration predates inspection. Each such assertion requires a provenance-bearing record and an appropriate independent evidential path.

### 5.2 Bounded local reading

Reuse the established safe snapshot and no-follow reading behavior. Retain the existing limits: 16 MiB per file, 64 MiB per bundle, 1 MiB per line, 100,000 records, nesting depth 64, and numeric-token length 1,024. Phase 4 does not raise those limits or add a weaker reader fallback.

Full main validation can involve up to 3,238,200 candidate/test observations (360 × 8,995). Keep execution records in bounded external evidence packets and retain a lossless ordered coverage representation with exact segment counts, suite identity, and full-log hashes. A small coverage summary is not accepted as proof of supplied or reviewed full logs. Distinguish locally verified content, verified external receipt, and unavailable attachment.

Each import operation declares a finite packet inventory and byte/record budget before reading. Validate large collections as bounded packets with linked verification receipts; any downstream reliance records exactly which packet contents or external attestations were checked. The compiled legacy bundle must independently satisfy its original limits. Excess content is rejected with a partitioning diagnostic; it is never truncated, silently sampled, or dropped to achieve a pass. Do not add automatic archive expansion or remote URL fetching.

### 5.3 Review privacy and independence

Blind packs contain pseudonymous artifact IDs and required task/descriptor/rubric information, without candidate model, condition, proposed role labels, or another reviewer's decisions where those can be withheld. A separate restricted mapping records originals, assignments, and access/exposure history. Actual artifact content can reveal its mechanism or source; report this limit rather than claiming perfect blinding.

Review-pack generation does not contact anyone. It cannot make a previously exposed reviewer unexposed. Imported records distinguish draft forms, genuine initial submissions, revisions, and adjudication. A missing reviewer, copied first pass, same-person duplicate, or unavailable independence record remains visible. Machine assistance must be disclosed; automated agreement cannot supply human independence.

Software checks record consistency, distinct claimed identities, provenance links, and qualification dispositions. It cannot establish that two real people performed independent reviews merely from supplied JSON fields. Authenticity and substantive independence require the actual evidence and accountable review in P4-E03 and P4-E04.

Raw identity/contact details, credentials, and unrestricted private review notes are excluded from public fixtures and source archives. Study exports disclose evaluator qualifications and relationships at a level sufficient to assess the claim, with controlled identity evidence retained when public naming is inappropriate. Privacy redaction must retain a versioned original association and disclose its effect on verification.

### 5.4 Compilation and correction behavior

Compile qualified observations into the existing M-only, comparison, or longitudinal input profile. Map records explicitly, reuse existing validation/evidence functions, and preserve original text bytes, selected positions, grouping, denominators, material roles, and policy decisions. Use existing numerical and reporting implementations after compilation.

When an input cannot be represented without losing an essential distinction, produce an explicit mapping error or withhold that compiled claim. Do not insert an apparently valid default, create a fabricated accepted assignment, or change the legacy schema implicitly. A separately reviewed format amendment is required for an indispensable new legacy field.

Corrections identify their dependency closure. A changed artifact invalidates its attached execution/review association unless new evidence binds the new bytes. A revised descriptor triggers review of every affected condition. Preserve prior bundles and reports as historical versions and create new outputs. A planned corrective action remains distinct from an actually performed correction.

## 6. User workflow and deliverables

### 6.1 Proposed CLI surface

The exact arguments below are proposed Phase 4 interfaces, not commands available at planning time:

```text
python -B -S -m structdet_bench study inspect --study STUDY.json
python -B -S -m structdet_bench study export-review --study STUDY.json --output-dir NEW_REVIEW_DIR
python -B -S -m structdet_bench study prepare --study STUDY.json --output-dir NEW_STUDY_DIR
python -B -S -m structdet_bench analyze --bundle NEW_STUDY_DIR/bundle.json --output-dir NEW_REPORT_DIR
```

`inspect` validates supplied passive records and writes a bounded readiness summary to stdout; it does not fetch missing evidence. `export-review` creates a blind package and a separately located restricted identity map. `prepare` produces a compatible analysis bundle only when its necessary representation requirements hold; broader claim restrictions remain in its evidence records and sidecar disclosures.

Use fresh destinations and the existing atomic/no-clobber publication principles. Complete validation before publishing final output. Errors leave no apparently complete bundle. Step 2 fixes the exit-code distinction between malformed/unrepresentable input and a well-formed study with unresolved evidence. A restricted study must be inspectable without being presented as complete.

The existing `analyze` command and its established three-file output remain compatible. Study preparation has its own manifest and fixed semantic outputs: `study_readiness.json`, `study_readiness.md`, `provenance_map.json`, `compilation_manifest.json`, and, when compilation is eligible, `bundle.json` plus its explicitly inventoried passive payload files. A noncompilable study may produce readiness-only outputs through the documented mode, with an explicit `analysis_bundle_created: false` result. No empty successful analysis bundle is fabricated.

### 6.2 Reporting requirements

Put the actual material role, evidence status, claim scope, and study/version pins before numerical results. Retain the required report order from HERO §11.2 and the established analysis output. A Phase 4 companion provides operational detail without silently revising the old report versions.

All ten EC disclosures must be represented: claim/deployment scope; represented and omitted structural relations; source/transformation lineage; contamination/exposure; evaluator identity/relationships/bias controls; per-class low-frequency/high-severity results where supported; relevant long-horizon/recovery/override evidence; live/field evidence; correction path and actual action; and a currentness/expiry date or explicitly unresolved currentness judgment.

For this bounded sorting study, a justified lack of a longitudinal claim can make the corresponding requirement inapplicable. Missing required human review or missing field evidence for an operational openness claim cannot be marked inapplicable. A real model response in this study does not establish live deployment performance or continuing external contact.

Reports show planned calls, responses, extracted realizations, selected populations, classifications, validity decisions, evidence coverage, audit coverage, and spending knowledge with separate denominators. All-zero, unavailable, undetermined, unassessed, and missing values retain their original distinctions.

### 6.3 Planned source deliverables

The principal new documents are `STUDY_FORMAT.md`, `EMPIRICAL_PROTOCOL.md`, and the final `PHASE_4_COMPLETION.md`. The new modules and bounded file families are specified in Section 9. Fixtures exercise the entire offline route, including failures and corrections, with conspicuous `fixture_only` provenance. Actual study workspaces and restricted identities are delivered separately from public software fixtures.

Every step produces its exact local change set, acceptance evidence, unresolved limitations, and a reviewable handoff. Remote delivery follows only the owner's applicable instruction. A prepared update archive or patch is a local artifact; it does not itself authorize a remote branch write or merge.

## 7. Ordered implementation plan

Each step begins with the preceding handoff and its source identity. “Pass” below refers to the stated software checks unless actual empirical evidence is expressly required. New implementation must remain within Section 9's file ledger. A defect found in a completed component returns to its responsible implementation step with an explicit correction record.

### Step 1. Establish the Phase 4 baseline and verification scaffold

**Purpose:** Make every subsequent change accountable to the final Phase 3 delivery.

Create an isolated local source copy from the verified Step 10 tree. Place the adopted plan in that copy, record its hash and the owner's adoption reference, capture all 1,817 predecessor test IDs, and create `tests/phase4_matrix.json`, `tests/phase4_helpers.py`, `tests/test_phase4_gate.py`, and `tools/run_phase4_checks.py`. Keep the original Phase 1 through Phase 3 matrices and histories unchanged.

The new runner distinguishes current-step coverage, complete Phase 4 software coverage, inherited M/V/L fulfillment, empirical evidence, repository delivery, and owner acceptance. Bind tests only after implementation exists and actual methods have been discovered. The full Phase 4 software gate remains incomplete at this stage.

**Acceptance:** P4-W01 through P4-W03; exact predecessor inventory reconciliation; all inherited methods present; actual inherited regression result; negative tests for removed method IDs, unbound requirements, duplicate outcomes, stale identities, and an incomplete later-stage matrix. No empirical pass is inferred.

**Handoff:** Baseline inventory and immutable predecessor references, populated requirement inventory, current-step journal, and the exact local delta. No baseline repair is hidden in this step.

### Step 2. Freeze the operational study format

**Purpose:** Define data meaning before building producers and importers.

Write `STUDY_FORMAT.md` and implement the separate study-envelope parser and semantic validation. Specify record grammar, scope/version relations, field knowledge states, collection positions, coverage encoding, reviewer/adjudication records, readiness states, compilation outcomes, correction relationships, diagnostics, and canonical serialization. Define deterministic packet budgets and how separately checked evidence packets are linked.

Document an explicit crosswalk from each compiled field to the existing input/profile field. Where the existing format cannot represent a required distinction, resolve the proposed operational representation before proceeding; do not enlarge an existing accepted meaning.

**Acceptance:** P4-W04 through P4-W07. Positive parsing and round-trip cases; duplicate-key/ID rejection; type and reference mismatches; unknown version; malicious local paths; missing attachment handling; size/depth/number limits; scope contradictions. Test missing evidence as well-formed uncertainty where the grammar permits it.

**Handoff:** A stable study-format version and fixture examples for complete, partial, and malformed packets. These are labeled software fixtures.

### Step 3. Prepare reference and external-validation specifications

**Purpose:** Turn the approved task into exact review and validation inventories.

Materialize the 32 core role specifications, the eight descriptor identifiers, W-01 through W-04, all 28 descriptor-pair review entries, preservation quotas, and the exact 8,995-input manifest. Produce a deterministic trusted input-materialization tool. This tool constructs integers and lists; it does not load or execute candidate source.

Implement passive validation-receipt parsing and coverage checks. Define complete coverage, duplicate/missing IDs, decisive counterexamples, conformance review, environment/oracle association, separate mechanism observations, and partial/harness-failure outcomes. Preserve core artifact slots as missing until actual construction or supplied evidence fills them under Step 11's applicable authorization.

**Acceptance:** P4-W08 through P4-W11. Independently enumerated segment counts and boundary examples; stable input order and hashes; repeated equal inputs retained under distinct IDs; tampered suite/artifact hashes rejected; complete versus partial coverage; an invalid counterexample; a correct-output receipt without mechanism evidence unable to certify class membership.

**Handoff:** Reference catalog, deterministic input inventory, receipt contract, and core/environment readiness gaps. No actual 32-program validation or candidate execution is claimed.

### Step 4. Implement independent review and adjudication records

**Purpose:** Preserve genuine first-pass evidence and make disagreements actionable.

Implement blind-pack construction, restricted identity mapping, reviewer qualifications/relationships/exposure, independent first submissions, separately versioned amendments, and expert adjudication records. Provide core and sampled-output review forms with separate mechanism and validity judgments. Collect only information needed to evaluate identity, expertise, independence, and the claimed decision.

Record initial agreement using the existing contract's stated categories and missingness; publish counts and denominators. Do not select a new agreement estimator or acceptance threshold. Schema-defining contradictions remain unresolved even with high observed agreement.

**Acceptance:** P4-W12 through P4-W16. Two distinct human-role records preserved; same-person duplicates and AI personas cannot qualify as two humans; initial records survive adjudication; blind outputs omit restricted mappings; prior exposure remains disclosed; unresolved disagreement restricts the applicable claim.

**Handoff:** Passive review packs and import examples. No person is contacted and no fixture identity is described as a real reviewer.

### Step 5. Implement planned collection and exact extraction

**Purpose:** Preserve the registered unit of observation and the original generated material.

Materialize pilot/main slots and exact prompt assemblies from HERO §7.2. Implement the external collection-record import, controls/usage knowledge, original-response storage association, one-attempt ledger, and registered heading/fence extraction rules. Preserve call failures, refusals, missing positions, extras, truncated bodies, duplicate headings, drift, and retry evidence.

Do not add a network collector. The operator-facing external procedure explains what the chosen collection system must export, what controls it must expose for the proposed comparison, and which unavailable fields restrict the claim.

**Acceptance:** P4-W17 through P4-W20. Exact A/B prompt identity and C-only clause change; 72 main calls/360 positions; 6 optional pilot calls/30 positions; correct order; exact byte-span reconstruction; malformed/duplicate fence cases; no repair, best-of selection, retry replacement, or missing-position compression.

**Handoff:** Passive preregistration and collection templates, extraction fixtures, and provider-neutral export requirements. No model calls or expenditure occur.

### Step 6. Qualify evidence and select human audits

**Purpose:** Connect available evidence to the precise labels and claims it can support.

Implement the 72 fixed audit positions and deduplicated targeted reasons. Link core review, actual artifact provenance, domain receipts, membership judgments, independence evidence, and applicable claim requirements. Preserve the five EC condition assessments and the distinction between essential membership evidence and broader independence restrictions.

Track evidence qualification per artifact, per cell, per comparison, and per named operational openness claim. No global “integrity score” is introduced. A satisfied JSON flag without its necessary evidence association fails qualification; authentic evidence must still be evaluated by the responsible human role.

**Acceptance:** P4-W21 through P4-W25. Audit formula enumeration; missing fixed selection retained; count-one/two cases and observed class-by-condition coverage; overlapping reasons deduplicated; all 360 main artifacts as a valid maximum; fixture promotion denied; missing domain or independence evidence handled at the correct scope; four-of-five EC conditions unable to support operational openness.

**Handoff:** Evidence and audit coverage reports, explicit claim restrictions, and unresolved-review queues.

### Step 7. Compile existing profiles and propagate corrections

**Purpose:** Make the operational records usable by the established analyses without changing their meaning.

Implement explicit compilation to the existing M-only, comparison, and declared longitudinal profiles. Preserve original artifact bytes, stable IDs, planned groups/positions, missingness, evidence policy, and scope. Reuse existing numerical implementations and acceptance rules. Imported longitudinal records must actually contain the required longitudinal identities and observations.

Implement dependency-aware correction and supersession. Preserve old records and reports; detect stale labels or receipts after source/schema revisions; recompute the same registered comparisons across affected conditions when qualified revised inputs exist.

**Acceptance:** P4-W26 through P4-W30. Hand-authored expected bundle fields independent of the compiler; identical old-engine results for equivalent existing fixtures; invalid-but-classifiable and valid-but-unresolved cases; failed-call/missing-position cases; P1 and both P5 endpoints with inherited gates; no synthetic training transitions; correction invalidation and stale evidence rejection.

**Handoff:** Compiled fixture bundles, field-level provenance maps, correction receipts, and compatibility evidence.

### Step 8. Complete the offline CLI and study disclosures

**Purpose:** Make the workflow usable and its limitations visible.

Add the opt-in `study` CLI dispatcher and the three proposed study commands. Complete atomic output publication, readiness/provenance JSON and Markdown, privacy-safe errors, and role-appropriate review exports. Write `EMPIRICAL_PROTOCOL.md` and factual usage documentation in `README.md`. Preserve existing CLI behavior and report files.

Provide complete fixture-only examples for readiness without evidence, qualified synthetic imports, disputed membership, failed collection, missing audit, stale correction, and an explicitly supplied longitudinal import. Each example states its material role before results and has an exact expected output inventory.

**Acceptance:** P4-W31 through P4-W34. CLI fixtures across valid/partial/error paths; no-clobber and interrupted-publication checks; the ten EC disclosures; no secret/identity leakage in public errors; repeatable output semantics; original M-only/A/B/C/longitudinal reports and replay behavior preserved.

**Handoff:** Documented end-to-end offline workflow and reviewable example outputs.

### Step 9. Complete software conformance and reproducibility

**Purpose:** Establish the full Phase 4 software gate against exact code and data.

Complete all W requirements, adversarial evidence-input cases, parser and publication boundaries, original-response reconstruction, correction propagation, and report/bridge equivalence. Exercise bounded large-log coverage without executing candidate programs. Produce actual current and clean source runs with complete per-method outcomes and all inherited M/V/L obligations reassessed using current actual results.

The clean copy contains only the declared deliverable files. Record interpreter, Unicode, environment, command, input/oracle identities, test discovery, actual outcomes, and before/after subject fingerprints. Retain negative, null, mixed, and missing-evidence cases independently of the desired study result.

**Acceptance:** P4-W35 through P4-W38 and all P4-W01 through P4-W34. Every software obligation bound and actually passed; all 1,817 predecessor IDs retained and passed; no skip/failure/error/expected-failure/unexpected-success accepted as fulfillment. No empirical evidence requirement is converted into a skipped software test.

**Handoff:** Software-complete candidate with actual current and clean run receipts, complete requirement coverage, reproducibility limits, and outstanding empirical requirements. Stop optional testing once the required gates and concrete risks are resolved.

### Step 10. Prepare concrete activity-readiness packets

**Purpose:** Make any later external action specific enough to authorize and execute responsibly.

Prepare separate readiness packets for core construction, external validation, human review, optional pilot collection, main collection, and scientific release. Fill known identities and evidence; mark unsupplied operators, reviewers, infrastructure, provider details, prices, and budget as missing. No fictional resources or implied availability are permitted.

For a proposed collection, identify the actual deployment, supported controls and cap semantics, exact messages, intended slots, maximum expenditure, retry policy, raw-export capability, schedule, and authorized operator. Verify provider-specific information against current primary documentation when such a choice is made. For hostile-program execution, require the independently reviewed envelope in Section 10.2 and a concrete operator/environment. For review, identify real qualified people and relationships before any authorized contact.

**Acceptance:** P4-W39. Each activity has a complete dependency list, explicit evidence status, concrete action description, and an authorization reference or outstanding authorization need. A blocked main collection does not block preparation of core-only work. Optional pilot omission is recorded honestly.

**Handoff:** A reviewable operational packet or a precise readiness-gap register. Missing external resources permit a bounded software handoff with E pending; they never authorize fabricated evidence.

### Step 11. Perform the scoped empirical workflow when activated

**Purpose:** Supply actual external evidence for the first registered study.

This stage is conditional on the applicable existing or newly supplied operational authorization and actual resources. Its sequence is:

1. **Core construction and qualification.** Obtain the 32 actual artifacts with source/assistance lineage; validate the external environment and oracle; collect domain/mechanism evidence; preserve two independent human first passes per item; adjudicate disputes; address all 28 descriptor-pair reviews and actual counterfactual checks. Resolve schema-defining contradictions before relying on the schema.
2. **Envelope calibration and optional pilot.** Establish that the approved execution envelope accommodates all eight correct reference families on the full suite. If a pilot is activated, register its P00 controls and keep every pilot output separate from the main study. Record problems and versioned changes.
3. **Main freeze.** Freeze the exact main registration, accepted reference/schema/rubric versions, collection/extraction/validation procedures, roles, budget, analysis conventions, and exposure record before main output inspection. A timestamp created after inspection is not prospective registration.
4. **Collection.** Execute only the authorized registered slots through the external collector; preserve original exports and failures. Stop at the declared resource limit or a concrete safety/authorization failure. Do not refill slots or change endpoints after viewing results.
5. **Validation, classification, and audit.** Use the authorized external validator, evidence-linked membership judgments, systematic and targeted human audits, and independent adjudication. Preserve unresolved mechanisms and invalid samples in their proper populations.
6. **Analysis and claim review.** Import the evidence, compile the fixed study, run existing analyses, retain all registered results, assess P4-E01 through P4-E12, and prepare the scoped report and correction record.

The gating order avoids requiring collected outputs before collection is possible. Core qualification and prospective main registration are prerequisites to a fully qualified main study. Output-specific judgments and audits occur after the actual outputs exist. Analysis of an incomplete or already supplied study can still produce explicit restricted/descriptive results without claiming this sequence was completed prospectively.

**Acceptance:** Actual E evidence, with each item assessed for the claim that needs it. Software test success is not a substitute. An unsatisfied item leaves the related claim restricted/withheld. If the stage is unactivated or blocked, record `not_performed`, the missing resources and affected claims, and proceed only to the clearly labeled software handoff in Step 12.

**Handoff:** Either original qualified study evidence and a scoped empirical report, or an explicit empirical-pending record. There is no obligation to obtain a favorable P1/P5 result.

### Step 12. Final audit and bounded Phase 4 handoff

**Purpose:** Deliver an exact, reproducible package with accurate completion status.

Freeze the software subject. Run the required final current/clean verification against the final implementation if it differs from the last fully verified subject or if the final gate requires a fresh run. Reuse still-applicable exact-subject evidence with explicit identity and date; never present reuse as a new execution. Record administrative changes after testing separately, with proof that tested implementation files are unchanged.

Write `PHASE_4_COMPLETION.md`, finalize factual `README.md` status and the Phase 4 verification manifest, produce final archive inventories/hashes, and verify the actual archive contents and the documented CLI routes from the packaged source. The QA runner's matrix delivery stage must truthfully distinguish the last implementation stage from final administration. No new numerical test total is promised in advance.

**Acceptance:** P4-W40; complete current and clean software evidence; inherited gates; exact write-ledger reconciliation; replayable report/provenance outputs; immutable histories; explicit E/readiness/remote/owner statuses. Any runtime defect returns to its responsible step before repackaging.

**Handoff:** Local software archive, verification companion, completion document, and a reviewable GitHub update package if requested. Actual study evidence is a separate scoped package with appropriate identity redaction. If remote delivery is authorized, verify its exact branch, commit, tree, parent, and all delivered blobs by fresh reads. Merging to `main`, publication, and final owner acceptance remain distinct actions.

## 8. Acceptance inventories

### 8.1 Software requirements

The 40 IDs below are the fixed Phase 4 software inventory. Step 1 creates their matrix rows as planned, with no invented test bindings. Each row requires actual discovered tests and independent expected cases by its due step. Test counts reflect real unique methods, not the number of labels or repeated runs.

| ID | Due step | Requirement and decisive positive/negative case |
|---|---:|---|
| P4-W01 | 1 | Exact Step 10 source reconciliation; a changed/missing/extra deliverable file fails identity review. |
| P4-W02 | 1 | Retain all 1,817 predecessor IDs and M/V/L bindings; removal or nonpassing execution blocks inheritance. |
| P4-W03 | 1 | Truthful current/full/software/E gate separation; unimplemented or unbound later requirements cannot pass full software. |
| P4-W04 | 2 | Strict study envelope and pinned versions; reject unknown version, duplicate key, malformed number, and wrong record type. |
| P4-W05 | 2 | Typed references and compatible claim scope; reject wrong-artifact/wrong-study links and forbidden revision cycles. |
| P4-W06 | 2 | Knowledge, validity, policy, requirement, and claim states retain meaning; unknown cannot become zero/false. |
| P4-W07 | 2 | Bounded safe snapshots; reject traversal, symlinks, over-limit content, and unbounded/automatic remote reads. |
| P4-W08 | 3 | Exact 8,995 ordered test IDs and values; preserve repeated equal values and reject duplicate/missing identities. |
| P4-W09 | 3 | All 32 core roles, eight families, 28 pair reviews, W-01..W-04, and retention quotas; missing material stays missing. |
| P4-W10 | 3 | Validity receipt coverage and oracle/environment association; complete pass, decisive invalidity, and harness/partial cases remain distinct. |
| P4-W11 | 3 | Mechanism versus functional evidence; identical outputs cannot certify a family, and forged artifact associations fail. |
| P4-W12 | 4 | Blind review export and restricted map separation; exported label/source/condition leakage is detected. |
| P4-W13 | 4 | Required distinct human-role identities and preserved initial records per core artifact; known same-person/AI substitution fails, and authenticity remains an E03 obligation. |
| P4-W14 | 4 | Qualifications, lineage, assistance, exposure, and limitations preserved; missing ancestry never becomes independence. |
| P4-W15 | 4 | Independent expert adjudication and immutable first passes; consensus cannot overwrite initial disagreement. |
| P4-W16 | 4 | Initial agreement/missingness accounting and schema contradictions; a high agreement fraction cannot clear an unresolved boundary. |
| P4-W17 | 5 | Exact prompt/control materialization and pilot/main separation; changed A/B prompt bytes or cap conventions restrict comparability. |
| P4-W18 | 5 | Fixed calls, order, positions, and attempt history; no replacement, missing-prefix compression, or five fabricated realizations after failed call. |
| P4-W19 | 5 | Exact original-response extraction; duplicate/missing headings, multiple fences, extras, and truncation follow the pinned rule. |
| P4-W20 | 5 | Actual controls, deployment, drift, usage, and preregistration knowledge; inaccessible values remain unknown and retrospective records stay disclosed. |
| P4-W21 | 6 | Enumerate 72 fixed audit positions and targeted deduplication; missing selections persist and reviews add no observations. |
| P4-W22 | 6 | Qualified membership assignment; absent essential evidence withholds acceptance and retains unresolved eligible artifacts. |
| P4-W23 | 6 | Accepted validity under the exact rubric; missing suite/source conformance cannot become `valid`. |
| P4-W24 | 6 | Real-versus-fixture and independence qualification; a stipulated fixture cannot be promoted to empirical truth. |
| P4-W25 | 6 | Five conjunctive EC conditions and four distinct architectural components; four satisfied conditions cannot support operational openness. |
| P4-W26 | 7 | Complete dependency-aware correction; changed source/schema invalidates stale evidence and identifies every affected condition. |
| P4-W27 | 7 | Frontier, external incidents, protected references, and actual-action distinctions; an unacted-on correction cannot count as performed. |
| P4-W28 | 7 | Explicit old-profile compilation and provenance; stable IDs/bytes/populations preserved and lossy mappings rejected. |
| P4-W29 | 7 | Existing metrics, P1/P5 operands, gates, uncertainty, and companion views unchanged; hand-authored equivalent bundles agree. |
| P4-W30 | 7 | Longitudinal profile requires actual longitudinal records; A/B/C groups cannot manufacture transitions or recovery evidence. |
| P4-W31 | 8 | Opt-in study CLI with existing CLI compatibility; malformed/partial/eligible operations have documented outcomes. |
| P4-W32 | 8 | Fresh-directory atomic publication, fixed output inventories, and rollback; failure creates no apparently complete study bundle. |
| P4-W33 | 8 | Evidence-first disclosure, ten EC fields, and correct denominators; mandatory missing evidence cannot become N/A. |
| P4-W34 | 8 | Readiness/provenance/review outputs preserve privacy and original associations; restricted maps and credentials do not leak. |
| P4-W35 | 9 | Passive-data boundary under adversarial source, attachment, and reviewer text; no import/eval/shell/model/network side effects. |
| P4-W36 | 9 | Bounded large evidence packets and lossless coverage; over-budget input rejected without silent truncation or missing-log promotion. |
| P4-W37 | 9 | Deterministic semantic replay and exact input identities; altered seed/index/source/configuration rejected where replay requires identity. |
| P4-W38 | 9 | Actual current/clean outcomes and inherited gates bound to the tested subject; fabricated summaries and stale receipts rejected. |
| P4-W39 | 10 | Activity-specific operational packets and dependency checks; blocked main collection still permits authorized core-only work. |
| P4-W40 | 12 | Exact final archives and truthful completion axes; remote/owner/E completion cannot be inferred from local software success. |

W39 and W40 cover packet/handoff machinery and evidence handling. Their implementation and negative tests must be ready by Step 9 for a full software candidate; their actual final packet and archive fulfillments occur at Steps 10 and 12. Until those deliverables exist, the final handoff gate remains incomplete. The matrix must represent implementation coverage and actual deliverable fulfillment as separate fields.

### 8.2 Actual evidence requirements

These are evidence review items, not Python test counts. Every item has claim scope, required evidence references, responsible reviewer, actual outcome, and unresolved limitations. An item can be inapplicable only when the named claim genuinely excludes its subject under the approved contracts.

| ID | Evidence needed for the applicable claim |
|---|---|
| P4-E01 | Prospective study registration, exact scope/design/version pins, actual control semantics, and exposure history; retrospective material explicitly identified. |
| P4-E02 | Actual 32-artifact core with source/assistance lineage, defining mechanism evidence, full required functional coverage for positives, and concrete negative/boundary evidence. |
| P4-E03 | Two distinct qualified independent human initial judgments for every core item, with actual submissions and blinding/relationship disclosures. |
| P4-E04 | Qualified independent adjudication, all descriptor-pair reviews, actual counterfactual/substitution checks, and resolution or retained consequences of schema contradictions. |
| P4-E05 | Independently reviewed oracle and execution isolation, exact image/configuration and source/test association, full-suite feasibility across all eight correct families, and authentic validation receipts. |
| P4-E06 | Actual authorized original collection records, exact prompts/controls/order/attempts, failures/missingness, actual deployment/usage knowledge, and pilot/main separation. |
| P4-E07 | Actual systematic and targeted human audit coverage, accepted sample-level membership/validity evidence, disputes, and missing audit opportunities. |
| P4-E08 | Complete extraction/selection/provenance chain with original artifacts, no unauthorized substitution, and a reproducible compiled bundle. |
| P4-E09 | All registered analysis operands and outcomes, applicable quality/coverage/comparison gates, fixed-suite sensitivity limits, and contrary or inconclusive results retained. |
| P4-E10 | Real independently grounded contributions, source/exposure integrity, and class-specific protected-reference retention within the claimed period; ongoing contact only when evidenced. |
| P4-E11 | Scoped five-condition assessment, real correction evidence for claims of performed correction, ten EC disclosures, and limits on any operational openness claim. |
| P4-E12 | Responsible claim review, explicit currentness/expiry, permitted release scope, owner decision where required, and correction/retraction route with actual authorities. |

A first bounded study need not establish ongoing deployment openness. Its report must state the narrower claim and outstanding external/field evidence. Real sorting outputs alone cannot satisfy E10/E11 for an operational evaluation system.

### 8.3 Independent expected cases and runner behavior

Use independently authored expected fixtures for record meaning, selection order, extraction spans, qualification, and compiled fields. Expected values must not be obtained by calling the same implementation under test. Reuse the frozen numerical oracles for existing metrics; do not rewrite their expected values to accommodate a changed compiler.

The runner records every discovered method exactly once per run, every actual outcome, required matrix binding, and predecessor membership. Zero discovery, duplicate IDs, missing bindings, missing outcomes, nonpassing required methods, stale source/oracle hashes, or a mismatched runtime block the corresponding software gate. Repeated current/clean runs do not multiply the unique-method total.

The proposed runner interface exposes `--scope current` and `--scope phase4`; `phase4` means all implemented software requirements, with final-deliverable fulfillment separately reported. Neither scope implies substantive E. New journals and manifests belong to `artifacts/phase4` or an external verification companion. Do not invoke an older runner in a way that overwrites its preserved historical artifacts. Reuse its pure gate logic with actual outcomes where feasible, preserving the distinction between the immutable predecessor reconciliation and the new current-file inventory.

Record direct execution evidence for the final archive CLI checks. Output comparisons may normalize only individually enumerated administrative metadata fields, with field names and reasons in the comparison receipt. All scientific values, evidence dispositions, original text, selected identities, and generated replay indices remain exact. An unexplained difference is a finding.

## 9. File authority and change ledger

### 9.1 New source paths

This is a bounded proposed file ledger. Generated groups must be expanded into exact paths in the step's manifest before the files are created. No wildcard grants authority to alter unrelated project files.

| Paths | First step | Permitted purpose |
|---|---:|---|
| `PHASE_4_PLAN.md` | 1 | Exact adopted plan copy; later amendments retain versions and owner decisions. |
| `STUDY_FORMAT.md` | 2 | New operational envelope and field-level bridge contract. |
| `EMPIRICAL_PROTOCOL.md` | 8 | External operating sequence, roles, evidence, and readiness procedure. |
| `PHASE_4_COMPLETION.md` | 12 | Final factual handoff and all completion axes. |
| `structdet_bench/study_records.py` | 2 | Strict passive record parsing and semantic validation. |
| `structdet_bench/study_validation.py` | 3 | Input inventory and passive domain/coverage receipt handling. |
| `structdet_bench/study_review.py` | 4 | Blind material, first-pass review, and adjudication records. |
| `structdet_bench/study_collection.py` | 5 | Planned slots, prompt bytes, import, and exact extraction. |
| `structdet_bench/study_evidence.py` | 6 | Qualification, audits, and scoped integrity assessments. |
| `structdet_bench/study_bridge.py` | 7 | Existing-profile compilation, provenance, and correction closure. |
| `structdet_bench/study_reporting.py` | 8 | Readiness, provenance, and EC companion outputs. |
| `structdet_bench/study_cli.py` | 8 | Opt-in offline study commands. |
| `tools/materialize_sorting_inputs.py` | 3 | Trusted deterministic input/catalog materialization; no candidate execution. |
| `tools/run_phase4_checks.py` | 1 | New QA runner and local evidence recording. |
| `tests/phase4_matrix.json`, `tests/phase4_helpers.py` | 1 | New requirement inventory, predecessor IDs, and verification helpers. |
| `tests/test_phase4_gate.py` | 1 | Gate and inherited-evidence checks. |
| `tests/test_study_records.py` | 2 | Grammar, scope, references, and limits. |
| `tests/test_study_validation.py` | 3 | Input enumeration, coverage, and passive receipt checks. |
| `tests/test_study_review.py` | 4 | Review, blinding, independence handling, and adjudication. |
| `tests/test_study_collection.py` | 5 | Exact prompts, slots, responses, and extraction. |
| `tests/test_study_evidence.py` | 6 | Qualification, audit, and five-condition handling. |
| `tests/test_study_bridge.py` | 7 | Old-profile equivalence, correction, and longitudinal boundaries. |
| `tests/test_study_reporting.py`, `tests/test_study_cli.py` | 8 | Outputs, disclosure, privacy, and command compatibility. |
| `tests/test_phase4_security.py`, `tests/test_phase4_replay.py` | 9 | Adversarial passive inputs, bounded packets, and replay. |
| `tests/fixtures/phase4/` | 2 onward | Exact enumerated fixture files for the listed requirements, with expected outputs and stipulated provenance. |
| `examples/phase4/` | 8 | Exact enumerated fixture workspaces and expected output manifests. |
| `artifacts/phase4/` | 1 onward | New requirement/verification manifests and step identities; large journals may live in the external verification package. |

The reference catalog and deterministic suite manifest reside in an explicitly enumerated passive subdirectory of `examples/phase4/reference_spec/`. They contain specifications and inputs. Actual core programs, collected responses, execution logs, reviewer identities, and empirical study records live in separately identified study workspaces. They are not automatically added to the source repository.

### 9.2 Existing-path changes

Routine planned existing-file changes are limited to:

| Path | Step | Change |
|---|---:|---|
| `structdet_bench/cli.py` | 8 | Thin dispatch for the new `study` commands; preserve existing argument behavior and errors. |
| `README.md` | 8 and 12 | Factual Phase 4 usage and completion status, keeping inherited capability/evidence limits accurate. |

No metric, population, comparison, longitudinal, recovery, support-assay, source-pin, or legacy physical-format change is planned. Retain `pyproject.toml`, package version, licensing, and original report versions unless a separately documented concrete need arises.

A proven compatibility defect in an existing implementation may require a minimal correction during Steps 2 through 9. Before editing, record the reproducer, affected contract, exact path, proposed change, and required regression; preserve the scientific meaning and all predecessor method IDs. This is ordinary corrective work already implied by implementing the authorized step, unless it changes approved scientific scope. Do not rewrite frozen documents, historical matrices, or expected scientific oracles as a workaround. A scientific-scope change requires a specific amendment decision.

### 9.3 Evidence integrity and final administration

Retain every step's before/after file manifest, current test evidence, amendment/finding records, and resolved limitations. Historical run journals are append-only. Final administrative edits identify exact files and preserve the tested implementation fingerprint. The plan itself is outside the frozen 180-file source tree until Step 1 is started.

The final verification companion contains the source inventory, actual run/console/subject receipts, binding outcomes, CLI comparisons, archive identities, and remote read evidence where applicable. It must not contain credentials, restricted reviewer mappings, or copyrighted source PDFs merely to demonstrate a hash match. Keep original scientific source identities and existing approved source references.

## 10. Operational activation and execution limits

### 10.1 Activity-specific prerequisites

Plan adoption and step implementation are separate from authorizing expenditure, contacting people, or executing hostile candidate programs. Before an external action, use any authorization already supplied in the session. If it is missing, first prepare the concrete action and its artifacts, then request only the missing decision and explain its source in HERO §§6 and 12 or the applicable owner instruction.

| Activity | Concrete prerequisites | Work permitted while it is unavailable |
|---|---|---|
| Core construction | Named construction method/operator, source rights and lineage, task/schema version, permitted resources, actual authorization for construction. | Prepare the full 32-role catalog, review forms, suite, and missing-material inventory. |
| Hostile-program validation | Independently reviewed isolation and oracle, pinned environment, limits, actual source/input identities, authorized operator and execution scope. | Validate passive record structure, input manifest, receipt association, and coverage fixtures. |
| Human review | Actual qualified reviewers, disclosed relationships/exposure, appropriate blinding, concrete review pack, authorized engagement/contact where needed. | Generate blind packs and restricted maps; validate imported records already supplied. |
| Pilot collection | Named deployment and control semantics, P00 registration, six specified slots, collection access, concrete maximum spend and authorization. | Prepare prompts, ledger, and export requirements. |
| Main collection | Qualified core and feasible validator; main preregistration; actual control support; 72 specified slots; exact budget/operator/window; applicable authorization. | Produce readiness gaps and analyze supplied data under accurate restrictions. |
| Scientific release | Qualified claim-specific evidence, full disclosures and currentness, accountable claim review, destination/content and applicable release authorization. | Produce a local reviewable report and correction record. |
| Remote code delivery | Exact source delta, verified archive, target branch/repository, existing or new owner instruction for the write. | Prepare a local patch/update archive and compare remote state by read-only calls. |

An already supplied historical dataset may be imported with its actual provenance even if prospective registration is absent. The report must preserve that absence and avoid describing a retrospective analysis as the registered prospective study. Missing authorization for a new operation does not prevent passive review of evidence the user has already supplied.

No reviewers, operators, deployment, external isolation service, monetary budget, actual core material, or main-study observations have been established by this planning turn. Their fields are outstanding prerequisites with named consequences, rather than fictitious completed resources.

### 10.2 External execution envelope inherited from HERO §12

The toolkit continues to treat all candidate code as passive. If actual external execution is later authorized, require a boundary suitable for hostile code, with independent review. A Python subprocess, restricted globals, a source blacklist, or an ordinary container alone does not establish that boundary.

| Area | Required record and proposed baseline envelope |
|---|---|
| Isolation | Hardened VM/microVM or equivalently justified service; no execution in the analyst host environment. |
| Host access | No candidate access to host home, project tree, devices, credentials, secrets, or host interfaces. |
| Network | Denied inbound/outbound access, including metadata endpoints; no automatic package access. |
| Filesystem | No discretionary candidate file access; trusted read-only source/input material; bounded ephemeral space. |
| Process/privilege | No candidate process spawning, privilege escalation, or uncontrolled threads; documented enforcement and concurrency. |
| Memory | Proposed 512 MiB guest/candidate working envelope, with trusted-oracle separation recorded. |
| Time | Proposed 30 CPU seconds and 60 elapsed seconds per artifact's functional suite; separate declared mechanism-trace envelope. |
| Output/storage | Candidate diagnostics at most 64 KiB; trusted result protocol bounded to 256 returned integers per test; proposed 16 MiB ephemeral storage. |
| Interpreter/image | Exact Python implementation/patch version, image identity, dependencies, configuration, and independent review evidence. |
| Reset | Fresh candidate state between independent tests or an independently reviewed equivalent; no persistent state across artifacts. |
| Receipts | Exact source/test hashes, environment/configuration, oracle identity, trusted observations, termination, limits, and validator provenance. |

These are inherited proposed budgets, not measured performance findings. Actual positive references from all eight families must show that the profile is adequate. If the profile cannot accommodate a family, revise and freeze it before the affected main validation or preserve `undetermined` validity and corresponding restrictions. Do not selectively drop slow families. A revised envelope is recorded with scope and comparability consequences.

Containment and oracle correctness require different evidence. A failure of containment stops the affected execution activity. A harness failure is recorded separately from a task violation. The passive offline workflow can continue on its own safe, authorized scope.

### 10.3 Concrete run authorization record

Before any requested collection or execution, Step 10 prepares a record containing:

1. Activity ID, study version, exact action, operator, authorized time window, and existing authorization reference or missing decision.
2. Exact source/prompt/input/slot manifest hashes; target deployment or execution environment; actual controls and unavailable settings.
3. Maximum calls, positions, output allowance, monetary ceiling and currency where applicable, paid resource limits, and stop behavior.
4. Original export and receipt format, retry policy, failure preservation, storage destination, access restrictions, and provenance responsibilities.
5. Required prerequisite evidence, actual qualification state, unresolved limits, and the specific claims that will remain restricted.

The authorization record must not contain credentials. The operator supplies them through the service's supported secure mechanism when needed. A budget ceiling does not authorize extra calls outside the registered design. If a ceiling stops collection early, retain the incomplete study and its restrictions.

### 10.4 Registration and amendment timing

Retain the actual chronology: reference development, pilot registration and outputs if any, changes, main freeze, collection, validation, audit, analysis, and release decision. Preregistration evidence includes an independently checkable timestamp or equivalent provenance, plus the exact registered bytes and exposure history. A locally generated timestamp and hash alone cannot establish pre-inspection timing.

A main-design change after exposure creates a new version and its actual registration status. Preserve old aborted/partial versions. Do not combine pilot outputs into main cells, replace unfavorable outputs, substitute repaired code under the original artifact ID, or promote a secondary endpoint to primary after inspection. A separately authorized diagnostic repair has a new artifact identity and stays outside the original primary generation population.

## 11. Responsibilities, risks, and blocker treatment

### 11.1 Roles

| Role | Responsibility |
|---|---|
| Owner / theory owner | Adopt the plan and scientific amendments; decide the scoped claim and final acceptance under existing authority. |
| Implementer | Build the offline workflow, preserve contracts, produce exact artifacts and actual software evidence. |
| Study operator | Maintain registration, collection/validation action scope, chronology, original records, budget, and stopping rules. |
| External validator and oracle reviewer | Establish their respective containment and domain-checking evidence; provide authentic receipts and failures. |
| Two independent core annotators | Submit independent initial judgments on every core item with qualifications, relationships, and exposure disclosed. |
| Independent adjudicator | Resolve disputed essential cases with domain evidence, retaining unresolved findings where needed. |
| Sampled-output auditor | Review actual systematic/targeted selections independently of provisional decisions where feasible. |
| Release reviewer / accountable authority | Evaluate claim-specific E and EC disclosures, currentness, correction route, and permitted release scope. |

One person can occupy compatible later roles under the existing integrity contract, after independent first passes are preserved. Role names do not establish independence, and this document appoints no person or service.

### 11.2 Concrete risks and responses

| Risk | Detection and required response |
|---|---|
| An older `main` is used as the starting point | Verify commit/tree and all 180 predecessor files before Step 1. Reconcile the intended branch explicitly. |
| Operational metadata loses an existing distinction | Test hand-authored profile mappings; reject lossy compilation and record an amendment need where necessary. |
| Review labels leak through filenames or role hints | Pseudonymize pack identities, separate restricted maps, and audit exported bytes; disclose unavoidable content/exposure clues. |
| Missing real core/review/environment resources | Keep a precise readiness gap; complete the offline software handoff and leave empirical qualification pending. |
| Candidate evidence exceeds parser budgets | Use finite bounded packet inventories and verified receipts; preserve full-log associations; reject over-limit import without truncation. |
| Functional success is mistaken for mechanism evidence | Require constitutive-relation and branch evidence, descriptor-pair review, and counterfactual witnesses. |
| Provider controls/caps differ from the registered design | Verify actual semantics before activation; restrict the unsupported comparison or register a new scoped design. |
| Full-suite limits favor faster families | Calibrate with all eight positive reference families before main validation; version inadequate limits. |
| Exposure or drift undermines comparison | Preserve chronology/control/deployment knowledge and affected-block limitations; no silent replacement or estimator change. |
| Corrected source retains old review/execution claims | Invalidate dependency-bound evidence and compile a new version with an explicit re-analysis record. |
| Gate passes through fixture flags or run summaries alone | Require real bindings, exact subject receipts, authentic evidence provenance, and separate human claim review. |
| Documentation suggests operational openness from a lab study | Show all five conditions and ten disclosures for the actual scope, including absent ongoing external/field evidence. |

### 11.3 Blocker classes

A software blocker is an incorrect implementation, missing mandatory binding, incompatible format, failed inherited regression, unsafe passive handling, or inconsistent source identity. Fix it before the affected software gate passes.

An empirical blocker is missing actual material, human independence, domain evidence, control support, registration, or audit coverage. It restricts the affected empirical claim and the activities whose prerequisites depend on it. It does not erase calculable descriptive values or prevent unrelated offline implementation.

An operational blocker is missing action authorization, access, qualified operator, suitable execution environment, budget, or permitted release destination. Finish the local preparation and identify the exact next action and outstanding requirement. Do not attempt circumvention or substitute invented evidence.

A delivery blocker is an unverified or failed archive/remote operation. Describe the actual local and remote status separately. Automatic approval-review rejection, if encountered, must be reported with the rejected action and stated reason; do not characterize it as successful delivery.

## 12. Final deliverables and exit criteria

### 12.1 Software handoff

The final local source package includes the adopted plan, new format/protocol documentation, implemented modules, exact fixture/example files, original contracts and code, all predecessor tests, new W bindings, and `PHASE_4_COMPLETION.md`. The verification package includes the full source inventory, actual current/clean journals and subject receipts, original oracle references, end-to-end CLI/replay results, file-change reconciliation, and actual final archive hashes.

Carry the existing Step 10 local archive forward once in the local historical evidence package or preserve an explicitly resolvable durable predecessor reference with its exact hash and documented retrieval. Do not claim a self-contained archive unless all required predecessor evidence is actually included. The smaller GitHub update package can omit large historical/raw evidence only with explicit manifest references and accurate scope.

Software handoff requires:

1. All 40 W requirements implemented and tested, plus actual W39 readiness packets and W40 final-deliverable fulfillment.
2. Every predecessor method retained and passed; inherited M/V/L obligations passed with actual current outcomes; no weakened scientific oracle or contract.
3. Exact source and artifact identity, supported-runtime evidence, clean replay, bounded input/publication behavior, and no unexplained output differences.
4. Original-response, evidence, selection, correction, and privacy distinctions preserved through the documented workflow.
5. Empirical readiness and E outcomes reported accurately, including `not_performed` activities and missing resources.
6. Repository delivery and owner acceptance described only to the extent actually established.

An actual new empirical dataset is not required for this bounded software handoff. Its absence must be prominent in the title/status and completion document.

### 12.2 Empirical study handoff

If Step 11 is activated, deliver the study registration and chronology, actual core and source lineage, domain/environment/oracle evidence, original independent reviews and adjudication associations, raw collection and extraction records, audit coverage, compiled analysis inputs, complete registered outputs, ten EC disclosures, scoped E assessment, currentness, and correction route.

Use a separate study evidence package. Publicly shareable content and restricted identity/original evidence are explicitly inventoried with access conditions. Redacted files receive their own hashes and transformation records; a public redaction cannot masquerade as the original complete evidence.

A supported bounded P1/P5 interpretation requires all evidence and quality conditions applicable to that exact comparison. If a result is null, contrary, mixed, or inconclusive, it remains a legitimate study output. If evidence is insufficient, deliver the observations and restricted conclusions with the missing evidence named. No study package can establish UD-007, universal structural capacity, recursive-training collapse, or ongoing deployment openness without their distinct contracts and evidence.

### 12.3 Immediate next action after plan adoption

The next implementation action is **Phase 4 Step 1: baseline and verification scaffold**. Its first source is the verified Phase 3 Step 10 delivery tree. The present planning delivery creates no Phase 4 module, changes no predecessor source file, performs no new full regression run, makes no model call, executes no candidate, contacts no reviewer, and writes no remote repository.

## Appendix A. Pinned original sources

| Code | Supplied title | Pages | SHA-256 |
|---|---|---:|---|
| SD | The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness | 27 | `357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32` |
| SI | Structural Inbreeding in Synthetic Data | 31 | `80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a` |
| EC | Evaluation Closure: Benchmark Inbreeding and the Design of Open AI Evaluation | 16 | `002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950` |

The supplied PDF contents and the project's approved source integration determine this plan's theoretical basis. Outside works cited within those PDFs are not independently verified by this planning exercise. The source PDFs and extracted full text are not redistributed in the planning verification package.

## Appendix B. Planning verification and decision record

The companion `StructDet-Bench_Phase4_Plan_Verification.zip` contains this exact plan, the 180-file predecessor inventory, source identities, fresh read-only remote receipts, the planning baseline audit, and document consistency checks. It records file identity and plan QA; it contains no newly completed Phase 4 implementation, human study, model collection, or candidate execution evidence.

| Decision | Resolution in this plan |
|---|---|
| Phase 4 purpose | Operationalize the approved first study and evidence workflow; retain existing numerical/scientific definitions. |
| Implementation architecture | Passive provider-neutral preparation/import and existing-profile compilation; external collection/validation separately operated. |
| First empirical design | Original bounded sorting task, eight classes, 32-role core, 8,995 inputs, fixed pilot/main A/B/C design. |
| Step count | Twelve: baseline, format, reference/validation specification, review, collection/extraction, qualification, bridge, CLI, conformance, readiness, conditional empirical work, final audit. |
| Acceptance inventory | Forty software requirements plus twelve claim-scoped real-evidence items, with no predicted test-method total. |
| Missing operational resources | Explicit prerequisites prepared at Step 10; absence permits an accurately labeled software handoff. |
| Source changes this turn | Zero changes to the frozen 180-file predecessor. Plan and planning verification are standalone artifacts. |
| Future scope changes | A concrete amendment with affected contracts, evidence, and approval basis; no silent metric or study redesign. |

## Revision history

| Version | Date | Change | Authority status |
|---|---|---|---|
| 0.1 | 2026-09-21 | Initial Phase 4 plan based on the verified Phase 3 Step 10 delivery and three pinned theory sources. | Proposed for owner adoption; no implementation or empirical activity started. |
