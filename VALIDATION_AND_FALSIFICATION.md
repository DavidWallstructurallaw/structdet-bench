# VALIDATION_AND_FALSIFICATION

## StructDet-Bench: Software Conformance, Measurement Evidence, and Bounded Prediction Tests

| Field | Value |
|---|---|
| Document version | 0.2 |
| Record date | 2026-09-17 |
| Phase / step | Phase 0 / Step 8; corrective revision of the Step 7 validation contract |
| Status | AUDIT-CORRECTED PROPOSAL; Step 8 owner acceptance pending |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Input baseline | Approved scope, definitions, structural-class contract, evaluation integrity, and hero specification v0.1; metric contract v0.1 with the separately identified Step 8 revision v0.2 pending acceptance |
| Approval evidence | Version 0.1 adopted in OA-007; this finding-limited revision remains pending under `UNRESOLVED_DECISIONS.md` v0.7 |
| Companion | `THEORY_TO_CODE_TRACEABILITY.md`, version 0.2, audit-corrected proposal |
| Decision authority | Theory Owner |
| Implementation / repository / model collection / generated-code execution | Not authorized |

## 1. Purpose, authority, and evidence status

**[Step 8 audit revision: AF-001, AF-002, AF-003]** Version 0.1 was adopted in OA-007. This finding-limited revision aligns local assignment failure handling, endpoint-specific text gates, and passive local input access with the approved upstream contracts. It retains all 54 test IDs, 82 upstream mappings, 14 outcome fixtures, metric formulas, budgets, and decision thresholds. No implementation test or empirical validation is executed by this document revision. The original Step 7 submission/handoff text below is retained as history; the register governs current approval and the next gate. These corrections await Step 8 owner acceptance.

**[Owner-approved decision: OA-006]** The owner instructed continuation to Step 7 after the Step 6 delivery. The adopted task, metrics, sampling design, coverage bands, integrity requirements, and release boundary remain unchanged. This document proposes their future test mapping and completes the outcome rules assigned to Step 7. It neither performs the integrated Step 8 audit nor issues final Phase 0 approval.

**[Source-derived]** SD §§3.2-3.7, 5, 6.5, 7, and 9 require task-relative structural distinctions, separation of validity and concentration, protocol-bounded inference, meaningful validation, and testable predictions. SI §§3-6, 8-9, and 12 distinguish finite observed support, recursive dynamics, external recovery, and independent evaluation. References identify the supplied editions in the governing plan; cited outside publications have not been independently verified here.

**[Engineering proposal]** The numbered tests, fixtures, field mappings, and outcome categories below are specifications for later work. Every test in this delivery has execution status **NOT RUN**. Constructed numbers stipulate an oracle for future software checks, not model outputs, independent annotations, or empirical support for a prediction.

The abbreviations PLAN, SCOPE, DEF, SC, MET, EI, and HERO refer to the filenames defined in the companion document. Its PC/EP identifiers are planned responsibilities, not existing software. Its M/V/E/D tags are used here: first milestone, added v0.1 comparison, actual external evidence, and deferred capability respectively.

## 2. Three separate validation questions

| Layer | Question | What success can establish | What it cannot establish |
|---|---|---|---|
| Software and mathematical conformance | Do identities, accepted populations, formulas, ordering, states, and reports follow the contract on known inputs? | Correct behavior for the checked cases, with reproducible calculation evidence. | The truth of stipulated class labels, independent reference construction, or an empirical prediction. |
| Structural-measurement validity | Do class distinctions and assignments track the declared consequence-bearing mechanisms? | An evidence-supported abstraction and assignments within the reviewed domain and scope. | Complete model capacity, an exhaustive ontology, or correctness outside the tested/formal scope. |
| Empirical prediction evaluation | Under the registered design, what happened to the selected P1/P5 endpoints? | Supporting, contrary, or inconclusive fixed-suite evidence under this operationalization. | Population-wide statistical confirmation, a universal model ranking, or recursive/latent claims not studied. |

**[Engineering proposal]** A model producing adverse results must not make the software suite fail. A software defect must not be interpreted as empirical falsification. An unsupported structural map restricts both favorable and adverse structural claims, while preserving the actual artifacts and reasons for restriction.

Passing a sorted-output oracle leaves mechanism membership unresolved unless the class evidence also supports it. Conversely, an identifiable mechanism may coexist with an invalid implementation. These principles govern the same checks regardless of the result's direction. [SD §§3.2, 6.5, 7; SI §§3.1, 8.5]

No current reviewer pair, 32-program validated core, 8995-case execution record, 72-call empirical collection, or independently reviewed runtime environment is supplied by this phase. UD-006 remains open for the corresponding evidence.

## 3. Test records and milestone gates

### 3.1 Required record for a future check

**[Engineering proposal]** A future test result must pin its test ID/version, applicable contract versions, fixture or evidence identity, material role, selected sample/assignment revisions, configuration, action, expected result, actual result, tolerance where applicable, and disposition. External-evidence checks also name the people/tools, independence scope, observations, disagreements, and unresolved findings.

A test result may be passed, failed, not run, or inapplicable with a justified scope reason. Those are test-run outcomes; they do not replace MET's numeric result states, EI's claim dispositions, or Section 6's prediction outcomes. Mock review records are labeled mocks even when a record-handling test passes.

Expected labels cannot be obtained from the same calculation being tested. Arithmetic oracles use the approved exact expressions and independent hand-recomputable examples. Structural ground truth requires the separately reviewed evidence in SC/EI/HERO. Neither a reference implementation nor a statistical package is added as a mandatory dependency by this document.

### 3.2 Gates by delivery

| Gate | Required work | Work expressly not required at that gate |
|---|---|---|
| First offline milestone | Applicable M checks, including the twenty-record hero fixture, negative evidence/accounting cases, passive input, report parity, and truthful absent-capability reporting. | PC-06 through PC-08, real model calls, actual independent annotation, generated-code execution, or either other toolkit. |
| v0.1 offline comparison capability | Applicable V checks, complete fixture paths for diagnostics/comparisons/replay, and the M regressions. | Favorable model results or an unqualified empirical claim. |
| Validated structural measurement | Actual applicable E evidence under the adopted schema, rubric, independent core/audit, and scoped integrity assessment. | A finding that agrees with the theory. |
| Registered empirical P1/P5 interpretation | Valid measurement plus the actual frozen study, controls, grouping, gates, and outcome rules in Section 6. | Statistical generalization beyond the fixed suite, or Layer B and latent measurements. |

For M/E or V/E checks in the catalogue, M/V means validating record handling and withholding unsupported claims; E means actually obtaining and reviewing the substantive evidence. They must receive separate result records. A claim restriction is not a reason to invent missing evidence or delay unrelated authorized fixture work.

## 4. Future test catalogue

**[Engineering proposal]** These 54 checks consolidate the upstream requirements without changing their meaning. SC-T, MF, EI-T, and HB-T refer to the already specified checks/fixtures in SC §13, MET §12, EI §12, and HERO §14.1. All are future checks; the upstream-to-test index is in Section 8.
| ID | Delivery / evidence | Upstream anchors | Arrangement or action for later work | Required future outcome |
|---|---|---|---|---|
| VT-01 | M | SC-T01, SC-T15 | Supply complete metadata, then known zero/false, unknown, unavailable-with-reason, and justified not-applicable variants. | Preserve distinct knowledge/evidence/result axes. Missing an essential frame blocks affected metrics, not inventory. A fabricated default never completes metadata. |
| VT-02 | M | SC-T11, SC-T14 | Supply repeated bytes with distinct genuine sample IDs, copied/conflicting IDs, and multiple assignment revisions. | Keep genuine repeated observations; reject/withhold ambiguous identities. Pin one accepted revision without increasing samples, calls, or groups. |
| VT-03 | M/V | MF-16, HB-T12, HB-T13, HB-T14 | Supply a planned five-position call, a failed call, a partial response, extras, and explicit retry history. | Planned positions, attempts, responses, and actual realizations reconcile separately. No five artificial failure samples or independence from row splitting. |
| VT-04 | M | SC-T10, EI-T09 | Supply fixture, provisional, adjudicated-with-evidence, and adjudicated-string-only assignments, including one local evidence failure in an otherwise valid cell. | Enforce fixture_only/adjudicated_import separately. Withhold the affected assignment, retain the selected inventory, and recalculate the supported subset as in HF-04. Do not invalidate the whole cell for this local failure. Preserve qualified arithmetic when only the stronger independence claim is unsupported; VT-14 covers defects in the shared frame. |
| VT-05 | M | MF-07, SC-T05 | Use MET MF-07 and separately accepted validity records for all six selected realizations. | Reproduce both populations and all five ratios in MET. Unresolved-valid and provisional-valid observations stay visible without entering class mass. |
| VT-06 | M | MF-06, MF-08, MF-09, SC-T15 | Distinguish no observations, no accepted classes, all-classified-invalid, a genuine one-class distribution, and invalid input metadata. | Known empty occurrence sets count zero; undefined distributions/rates use null. All-view invalid mechanisms can be concentrated. Malformed/conflicting input is not an empty dataset. |
| VT-07 | M | MF-01, MF-02, MF-03, MF-04, MF-05 | Use the exact count tables in MET and Section 5.1. | Support, entropy, SCI, and both effective counts match the exact oracles. Zero-count reference entries do not change a distribution; unequal counts distinguish effective quantities. |
| VT-08 | M | MF-03, MF-05, HB-T16 | Use thresholds 0.25/0.250001/0.80 for (3,1), 0.2 for (1,4), omitted/malformed thresholds, and an empty population. | Use exact rational inclusion and original denominator. Omitted, invalid, undefined, and available zero differ. Thresholding leaves unthresholded entropy/SCI unchanged. |
| VT-09 | M | MF-01, MF-02, MF-03, HB-T16 | Use exact counts and rounded display versions; test range, finite-value, normalization, and effective-count inequalities. | Counts/thresholds are exact; float comparisons use MET absolute 1e-12 plus relative 1e-10. Derived fields use unrounded values. Material violations are withheld, not silently clamped. |
| VT-10 | M | MF-05, MF-10 | Bijectively rename classes and reorder stored rows while retaining sample-order metadata; then change the actual registered order in a separate fixture. | Distribution metrics are invariant to renaming/storage order. Recorded prefixes are invariant to storage order but can change when the actual sequence changes. |
| VT-11 | M | MF-10, SC-T14 | Use MET MF-10, k=2/4/6/7, missing order, invalid k, and a descriptive partial-group prefix. | Preserve the specified counts, no valid-only backfill, no shrink-to-fit, and the partial-group flag. Unknown order limits prefixes without erasing supported full-cell metrics. |
| VT-12 | V; M inventory | HB-T14, HB-T15 | Remove an early planned candidate while later groups remain; compare ordinary metric availability with the hero matched-group gate. | Later positions never repair a damaged first group. Descriptive actual-sample summaries can remain; registered k=5/10/20 endpoints require the intended complete first groups. |
| VT-13 | M | HB-T16 | Use HERO Section 11 and the separately pinned variants in Section 5.2. | Reproduce original and variant denominators, support, prefixes, entropy, SCI, and effective counts. Variants do not silently mutate the base oracle. |
| VT-14 | M/V | SC-T01, SC-T12, MF-15 | Remove required class metadata or combine identical class names under incompatible domains, horizons, schema versions, or rubric meanings. | Withhold affected class calculations/comparisons as appropriate; retain supported individual inventories/cells. No name-based semantic compatibility. |
| VT-15 | M/E | SC-T02, SC-T03, SC-T04, SC-T05, SC-T08, SC-T09 | Import same-mechanism/different-text evidence, different-mechanism/similar-text evidence, matching outputs only, misleading comments, and a missing decisive branch. | Record policy follows evidenced membership, not labels, wording, final results, or mental completion. Actual validation of the examples requires external evidence; fixture labels establish software behavior only. |
| VT-16 | M/E | SC-T06, SC-T07, SC-T15, HB-T05, HB-T07 | Supply a composite mechanism, eligible unregistered mechanism, multiple candidate labels, and a contradictory equivalence triangle. | Retain unresolved evidence without fractional mass, a default residual class, or transitive clustering of contradictions. An eligible novel-to-registry solution can remain valid. |
| VT-17 | M; V dependents | SC-T13, MF-20, EI-T14, EI-T15, HB-T21 | Apply MET MF-20 and EI Section 10.2, including a wrong-artifact trace and a schema-level defect affecting several conditions. | Pin corrected evidence, rebuild populations, recompute every dependent metric/prefix/pair/contrast, and retain superseded reports. No new observations or favorable-only repairs. |
| VT-18 | M/V | EI-T16 | Withdraw only an independence assertion while separately sufficient membership/validity evidence stays intact. | Keep justified count calculations unchanged and revise affected claim scope. Do not invent a label withdrawal or leave the independent-validation claim intact. |
| VT-19 | M/V | SC-T16, EI-T17, HB-T22 | Supply declared readable local inputs, source text, hostile-looking instructions, external locators, and restricted evidence as passive data in an instrumented future test environment. | Permit the declared passive local reads. Perform no candidate execution, shell invocation, model call, automatic remote retrieval, or dependency installation. An external locator cannot trigger a fetch. Private/access-limited evidence is not advertised as publicly reproducible. |
| VT-20 | M/V | EI-T09, EI-T17 | Render the same fixture with available, undefined, unavailable, not-requested, and deferred fields in JSON and Markdown. | Both preserve values, units, populations, reasons, and claims. No NaN/infinity/sentinel zero, omitted adverse endpoint, or independent-validation headline contradicted only in an appendix. |
| VT-21 | M/E | EI-T01, EI-T02, EI-T03, EI-T04 | Use different vendor names sharing known derivation, missing parents, edited/translated copies, and a sole-lineage citation/validation loop. | Preserve typed relationships and unknown ancestry. Do not infer independence from names, transformations, missing edges, or citation cycles; do not impose an unapproved universal acyclic-graph rule. |
| VT-22 | M/E | EI-T05, EI-T06, EI-T07, EI-T08 | Provide one person in two sessions, two exposed initial labels, independent-first-pass records, unresolved disputes, and absent calibration/sensitivity. | Record requirements correctly. Preserve initial decisions and disagreements. Two independent core annotations and Tier 1 sampled audit remain separate from a universal two-reviewers-per-output requirement. |
| VT-23 | M/E | EI-T10, EI-T11, EI-T12 | Provide a known-empty intake, stored-but-unused source, reviewed contrary incident, protected reference class, and a registry removal/split. | Distinguish record availability from effective external use. Preserve versioned disposition and low-count review; never add registry/audit artifacts to generator counts. |
| VT-24 | M/V/E | EI-T13 | Provide pre-inspection registration, post-inspection hashes, pilot-tuned rules, intended conditioning, and unknown pretraining exposure. | Preserve actual timing/exposure. No post-hoc untouched-confirmatory or never-seen claim. Approval dates and hash identity never supply missing exposure evidence. |
| VT-25 | M/E | HB-T01, HB-T02, HB-T03, HB-T04, HB-T05, HB-T06 | Check the adopted domain and eight descriptors, all 28 descriptor pairs, W-01 through W-04, admissible variants, and defect boundaries. | Records identify the actual evidence or missing review. No hidden constraint excludes a family; unresolved defining overlap restricts affected membership. Actual schema validation is an E activity. |
| VT-26 | M/E | HB-T08 | Inspect an imported ordered test manifest against V-SMALL, V-SHAPE, V-KEY, V-STAGE and their counts. | Require 781+18+8192+4=8995 test IDs with the prescribed domain and constructions. Equal inputs with different purposes retain IDs. A manifest is not execution evidence. |
| VT-27 | M/E | HB-T01, HB-T09 | Supply property observations, full versus incomplete suite coverage, plain-list/type/multiplicity/input-preservation checks, and oracle review records. | A valid assessment needs the adopted rubric and actual evidence. A decisive counterexample can establish invalidity before full completion; passing recorded cases does not prove every possible list. |
| VT-28 | M/E | HB-T22 | Import records for timeout, memory limit, exception, forbidden capability, bad oracle, containment failure, a repaired artifact, and an envelope that excludes a correct reference family. | Separate decisive task violations from undetermined runtime/harness outcomes. Timeout alone is not nontermination proof. Keep containment and scientific-validity evidence distinct; never execute or substitute repairs. The external envelope must accommodate all eight correct reference families before it supports the main validity claim; revise/freeze it prospectively or retain the limitation. |
| VT-29 | M/E | HB-T09, HB-T10, EI-T11 | Check the 32 core roles, frozen one-position-per-group audit, missing audit positions, low-count cases, targeted overlap, and registry coverage. | Design counts never masquerade as reviewed artifacts. Audit selection follows HERO; missing positions are not replaced. Deduplicate review work by artifact without changing model sample count or claiming random-error estimation. |
| VT-30 | M | EI-T18, HB-T24 | Request calculation, independent-validation, collection, implementation, and publication claims from a specification-only or fixture-only bundle. | Enforce separate authorizations/evidence. Other toolkit completion, actual reviewers, and unimplemented V/D features are not prerequisites to the bounded M demonstration. |
| VT-31 | V | MF-11 | Use a b c / a b d, identical text, CRLF/LF, one lexical unit, empty/whitespace-only text, punctuation, case, underscores, and recorded Unicode tables. | Reproduce 4/5 in MF-11; retain original bytes and fixed normalization. Empty token sequences are ineligible. Text units are not provider tokens; no case-folding/comment stripping or structural-label inference. |
| VT-32 | V | MF-13, MF-14 | Vary usable-text counts, singleton classes, missing-text reasons, per-class pair weights, and computation limits. | Both pair diagnostics share exactly A_text. Core counts can remain unchanged. Undefined pair/within-class denominators stay null; no text replacement, silent truncation, or pair subsampling. |
| VT-33 | V | MF-12 | Use four eligible labels A,A,A,B and then three singleton classes. | Distinct-pair non-equivalence is 1/2 for the first case, distinct from 1-SCI=3/8. Check the same-subset finite-count identity and pair count without treating pairs as independent observations. |
| VT-34 | V/E | MF-15, HB-T17 | Compare frames with unknown or changed checkpoint, unsupported temperature, different output cap semantics, hidden context, or incompatible schema. | Preserve actual limitations. Withhold unsupported matched/temperature claims without replacing a control or inventing equal compute. A qualified A/C comparison can remain when B is unusable. |
| VT-35 | V/E | HB-T11, HB-T12, HB-T13, HB-T17 | Inspect the six openers, A/B byte equality, C clause, four five-position groups per cell, interleaving, pilot separation, and registered controls. | Require 72 main calls/360 planned positions, optional separate six-call/30-position pilot, and documented requested/enforced 8192 cap semantics. Never infer actual usage or permission to spend. |
| VT-36 | V; M association | HB-T14 | Supply exact code fences/offsets, a uniquely truncated candidate, duplicate/missing headings, extras, empty emitted body, and an absent position. | Preserve exact association and distinct absence/empty/truncation states. No best-block selection, source repair, shared-code completion, or compression of missing positions. |
| VT-37 | V | HB-T18, HB-T19 | Use the exact coverage/floor/band boundary cases in Section 5.3, including complete but unclassified cells, a nineteen-realization cell, and a complete evidence-backed cell lacking only proxy text. | Apply adopted rational count gates per participating cell and endpoint. Equality at thresholds passes. Text coverage restricts pair-based P1, while count-based P5 retains its own applicable gates. Missing denominators remain undefined; calculable numbers survive a failed interpretation gate with the restriction visible. |
| VT-38 | V | HB-T18, HB-T19, MF-19 | Supply compatible per-condition operands with explicit units and k. | Compute B-A surface/structural gains and their contrast, plus separate C-A/C-B valid distinct-20 deltas. Entropy is not subtracted from lexical distance; linked operands use the same block set. |
| VT-39 | V | MF-18 | Replay the stipulated two-block draws, then a 2000-index replay record and the declared quantile rule. | Equal-block means match 0.1/0.2/0.3 in the toy replay. Preserve whole paired blocks, seed/RNG/replay identity, and linear-interpolated 0.025/0.975 endpoints; no row resampling or selective discarded replicates. |
| VT-40 | V | MF-16, MF-17, MF-23, HB-T20 | Use one block, missing conditions, endpoint-specific available blocks, unequal generated row counts, and unsupported cross-block dependence. | Withhold unsupported intervals/full-target claims. Show any descriptive complete-block subset explicitly; do not reweight by rows, fabricate blocks, or subtract means from different sets. |
| VT-41 | V | HB-T20 | Use six fixed phrasings and a degenerate replay interval where all block contrasts are equal. | Label prompt_resampling_sensitivity, not population confidence. A narrow interval cannot repair label uncertainty, within-prompt generation uncertainty, or nonrepresentative prompts. |
| VT-42 | V | MF-19, MF-24, HB-T18, HB-T23 | Feed Section 7 P1 supportive, reversed, false-favorable, null, and interval-straddling records. | Return the declared joint operational outcome, both gains, and reasons. Positive contrast without positive surface gain never qualifies; contrary results are a successful reporting test. |
| VT-43 | V | MF-24, HB-T19, HB-T23 | Feed Section 7 P5 both-positive, mixed-positive/negative, positive/tie, reversed, and incomplete-comparator records; then withhold only the proxy text while retaining all P5 evidence and prerequisites. | Report both primary comparisons and the full-pattern rule. The proxy-only variant keeps the same count-based P5 outcome and explicitly unavailable text diagnostics; a failed P1 text gate cannot act as a global P5 veto. One favorable comparator or secondary prefix cannot replace the full target; a missing actual prerequisite is not an observed zero. |
| VT-44 | V | HB-T18, HB-T19 | Use positive all-classified P1 with adverse valid-only sensitivity, quality deterioration, and P5 breadth gains outside the quality band. | Keep original primaries and sensitivities. Distinguish a P1 observed pattern from a clean quality-comparable account; restrict unmatched-quality P5 without deleting or equalizing valid outputs. |
| VT-45 | V | HB-T23 | Use surface baseline >=0.95, observed support at all eight registered classes, and favorable secondary k or thresholded support with adverse primary outcomes. | Show ceiling limitations and every primary endpoint; no proxy/class/temperature switch, extra sampling, population significance, or cherry-picked secondary claim. |
| VT-46 | M/V | HB-T16, HB-T21 | Run future fixture-to-report checks for the base hero and correction variants, then a supplied full A/B/C fixture bundle. | Every applicable RF field resolves to the pinned evidence/result; report order and JSON/Markdown match. The first one-block fixture has no empirical A/B/C result or automatic interval. |
| VT-47 | E; M/V record gates | SC-T02, SC-T03, SC-T04, EI-T06, EI-T07, EI-T08, EI-T09, HB-T09 | Actually review schema/witness evidence, independent core judgments, oracle evidence, generated-output audit, and correction/exposure records. | Substantive reviewers can affirm, overturn, or leave a classification unresolved. Record scope and disagreements. Software mock acceptance is never recorded as this evidence check passing. |
| VT-48 | E | HB-T11, HB-T17, HB-T18, HB-T20, HB-T23 | Conduct an independently evidenced, authorized registered P1 comparison under the unchanged hero protocol and Section 6 rules. | Publish all operands and qualifications under separate release authorization, whether supporting, contrary, inconclusive, or not evaluable. No forced favorable empirical outcome. |
| VT-49 | E | HB-T19, HB-T20, HB-T23 | Conduct an independently evidenced, authorized registered P5 comparison with both comparators and the adopted quality/coverage gates. | Describe valid breadth at the planned resource match, with actual usage disclosed. Results cannot claim unmeasured compute efficiency, complete support, or newly created representation. |
| VT-50 | V/E | MF-24, HB-T23, SC-T06 | Introduce adverse results and documented challenges to labels, schema, proxy, or controls; apply the same review to favorable results. | Freeze originals and record any symmetric evidence-driven revision. Neither treating every adverse result as a bug nor retaining favorable results under invalid measurement is permitted. |
| VT-51 | M/D | SC-T15 | Request expressible/latent support, an intervention union, soft-label counts, or exact realization entropy from the first-slice bundle. | Return the documented deferred boundary. One-off appearance, failed finite search, uncertain posterior labels, and a lexical proxy cannot fabricate these quantities. |
| VT-52 | M/D | SC-T01 | Request a frontier, convergence cause, load-bearing intervention estimate, or structural transmission from one fixed-resolution A/B/C fixture. | Preserve deferred status and prerequisite descriptions. Do not infer a frontier or causal mechanism merely from distribution changes. |
| VT-53 | M/D | MF-22 | Request SHL from one batch, inference calls mislabeled as rounds, corpus size substituted for n, or a non-geometric empirical trajectory. | No numeric v0.1 estimate. A future null needs SI categorical assumptions/n>1; an empirical fit needs compatible rounds and suitable regime, with distinct fields. Neural data need not obey closed-support monotonicity. |
| VT-54 | M/D | MF-21 | Request ERR for an empty missing reference set, unsupported pre/post expressibility, or direct answer injection. | No numeric v0.1 ERR. A future empty denominator is undefined rather than 0 or 1; recovery requires the independently grounded, validated SI definition. |

## 5. Mathematical and accounting oracles

### 5.1 Core arithmetic

**[Adopted engineering conventions: MET §§5-7,12]** Exact expressions govern; displayed decimals are illustrations. Counts, eligibility, IDs, and threshold membership have no floating-point tolerance. For noninteger arithmetic use the adopted absolute `1e-12` plus relative `1e-10` convention. No pseudo-counts, unseen-class correction, class weights, or posterior assignments enter the first release.

| Positive class counts | Occurrence support | Entropy, nats | SCI | Shannon effective count | Simpson effective count |
|---|---|---|---|---|---|
| `(4)` | 1 | 0 | 1 | 1 | 1 |
| `(2,2)` | 2 | `ln(2)` | `1/2` | 2 | 2 |
| `(3,1)` | 2 | `ln(4) - (3/4)ln(3)` | `5/8` | `4 / 3^(3/4)` | `8/5` |
| `(1,1,1)` | 3 | `ln(3)` | `1/3` | 3 | 3 |
| `(3,1,0)` | 2 | Same as `(3,1)` | Same | Same | Same |
| Empty accepted population | 0 with population-size-zero qualifier | Undefined | Undefined | Undefined | Undefined |

An empty or wholly unclassified population must remain distinguishable from the one-class case. Missing essential schema data instead makes affected metrics unavailable. Thresholded support on `(3,1)` is 2 at 0.25, 1 at 0.250001, and 0 at 0.80, without changing the population used by other metrics. For a requested threshold on an empty population, the ratio is undefined; with no threshold request it is not requested.

For MF-07, preserve the exact accounting: selected=6, classified-all=4 with `(2,2)`, classified-valid=2 with `(2)`, classification coverage `4/6`, valid fraction `4/6`, decisive validity coverage `5/6`, valid-output classification coverage `2/4`, and classified-valid fraction `2/4`. These overlapping axes must not be summed into a fictional partition.

### 5.2 Twenty-record hero and separately identified variants

**[Adopted baseline: HERO §11.1; Step 7 engineering fixture extensions]** The base sequence remains the four groups already defined in HERO. Its counts in the order MERGE, PIVOT, HEAP, COUNT, RADIX are `(8,6,3,2,1)`. Use the unchanged original sequence for every variant unless the variant explicitly removes an observation. Each has its own fixture identity; none is an empirical model collection.

| Variant | Stipulated change | Required populations and prefix behavior |
|---|---|---|
| HF-00 | Original twenty records, all fixture-classified and fixture-valid. | Both views n=20, support=5, thresholded support at 0.10=4; distinct-5/10/20 = 4/5/5. |
| HF-01 | The sole RADIX record at G2 position 5 has an accepted invalid assessment while its fixture class remains accepted. | All-view unchanged. Valid-view n=19, counts `(8,6,3,2)`, support=4, distinct-5/10/20 = 4/4/4; selected validity fraction 19/20. |
| HF-02 | That RADIX record remains valid but classification is unresolved. | Both class views n=19, counts `(8,6,3,2)`, support=4; selected inventory=20, selected validity fraction=1, classification coverage=19/20; prefixes 4/4/4. |
| HF-03 | That label is proposed/provisional instead of unresolved. | Same accepted class arithmetic as HF-02; review/status and withholding reasons differ. The candidate label never adds a class. |
| HF-04 | That record asserts a class but its required fixture label/declaration reference is missing or cannot be resolved. | Withhold the assignment with its actual record-integrity reason; do not convert a missing declaration into output invalidity. Same accepted-count arithmetic as HF-02 when all other records remain accepted. |
| HF-05 | G2 position 5 was never emitted. | Planned=20, actual=19. Supported full actual-sample counts `(8,6,3,2)` remain descriptive. Matched distinct-5=4; matched distinct-10 and distinct-20 are unavailable. Later groups do not fill the absent position. |
| HF-06 | Under a new supported fixture assignment revision, that record changes from RADIX to COUNT. | Both views n=20, counts `(8,6,3,3)`, support=4, thresholded support=4; prefixes 4/4/4. Original HF-00 results remain in history. |

HF-04 checks required fixture declaration integrity; it does not impose empirical mechanism validation on fixture-only labels. Its shared frame remains valid, so the other 19 accepted assignments retain calculable metrics rather than producing a whole-cell unavailable result. VT-04 separately tests mock adjudicated-import records, including missing decisive mechanism evidence. VT-14 covers a shared-frame failure that actually prevents a valid population from being formed. Those mock records remain test material and cannot establish an empirical measurement. No distribution silently mixes fixture and empirical assignments.

The arithmetic oracle for HF-00 is `SCI=57/200=0.285`, `H≈1.392321254757429`, Shannon effective count `≈4.024180367609189`, and Simpson effective count `200/57≈3.508771929824561`.

For the nineteen-classified-record distribution in HF-01's valid view and HF-02 through HF-05 where applicable:

`SCI=113/361`,

`H=ln(19) - [8 ln(8) + 6 ln(6) + 3 ln(3) + 2 ln(2)] / 19`,

Shannon effective count `exp(H)` and Simpson effective count `361/113`.

For HF-06:

`SCI=59/200`,

`H=ln(20) - [8 ln(8) + 6 ln(6) + 6 ln(3)] / 20`,

Shannon effective count `exp(H)` and Simpson effective count `200/59`.

Source texts have not been specified for these class-count fixtures. They therefore have no invented lexical or within-class distance. The single-block base fixture has no empirical A/B/C outcome or prompt-block interval.

### 5.3 Exact study-gate boundaries

**[Adopted engineering thresholds: HERO §10.3]** A complete primary cell has twenty actual positions in the intended four groups. The count inequalities below are consequences of those adopted thresholds, not new quality criteria.

| Gate | Boundary check on a twenty-position cell |
|---|---|
| Classification coverage at least 0.90 | 18 accepted classes pass; 17 fail. |
| Decisive validity coverage at least 0.95 | 19 accepted valid/invalid assessments pass; 18 fail. |
| Valid-output structural coverage at least 0.90 | With 16 accepted valid outputs, 15 classifiable-valid pass and 14 fail. When no valid denominator exists, disclose the undefined ratio and apply its stated conditional role. |
| Text coverage at least 0.95, with at least two eligible realizations | With n=20 classified samples, m=19 usable texts pass. With n=18 or n=19, every classified sample must have text to meet the 0.95 fraction. At least two eligible realizations are required. |
| P5 valid fraction at least 0.80 | 16 valid outputs pass; 15 fail. |
| P5 per-block absolute quality difference at most 0.10 | A difference of 2 valid outputs out of 20 passes; a difference of 3 fails. |
| Complete planned groups | Nineteen actual realizations never become a completed matched twenty-position endpoint. |
| Surface ceiling diagnostic | Baseline surface distance exactly 0.95 triggers the existing flag; it does not alter the numeric metric or sampling plan. |

All relevant cells must satisfy the comparison's requirements; suite averages cannot conceal a failed cell. Numeric gates qualify interpretation and never erase the underlying data. Even passing coverage does not remove possible missing-class bias.

### 5.4 Proxy, pairing, and replay oracles

MET MF-11's padded trigram sets for `a b c` and `a b d` intersect once and have union size five, so distance is `4/5`. Identical sets have distance zero. No same-class claim follows from either value. One lexical unit is eligible through the fixed beginning/end markers; empty tokens are ineligible.

For labels A,A,A,B on four text-eligible samples there are six unordered pairs, three structurally different; pair non-equivalence is `1/2`, whereas `1-SCI=3/8`. Both pair diagnostics use that same four-sample subset. If only two samples have text, recalculate both diagnostics on those two, retain class metrics on their original population, and report the changed diagnostic coverage.

For the one-based block names in MET MF-18, contrast records 0.1 and 0.3 yield 0.1, 0.2, and 0.3 under draws `(1,1)`, `(1,2)`, and `(2,2)`. A replay record must declare its indexing convention. This toy calculation is not a two-block empirical recommendation.

For the declared 2000-replicate quantile rule, the interpolation ranks are 49.975 and 1949.025 in the sorted zero-indexed array. A synthetic array `v[j]=j/1999` returns 0.025 and 0.975. This tests interpolation only; it does not claim the array came from a real bootstrap. A full resampling check must additionally verify its actual 2000-draw replay manifest, RNG/version, and mean statistic.

## 6. P1/P5 fixed-suite interpretation contract

### 6.1 What is fixed and what this step adds

**[Source-derived: SD §9.7]** P1 predicts greater surface than structural diversity growth when temperature increases. P5 predicts more non-equivalent outputs under explicit structural branching at matched quality.

**[Owner-approved design: MET §§10-11; HERO §§7-10]** Preserve A/B/C, six fixed phrasings, four five-position calls per cell, primary k=20, the two paired P1 gains, both P5 comparisons, all coverage/quality bands, and the 2000-resample sensitivity method. The proposed collection seed policy, tokenizer, proxy, reference classes, and requested resources remain unchanged.

**[Engineering proposal]** This step adds a deterministic, bounded interpretation layer using the already adopted zero-direction target and sensitivity outputs. It adds no p-value, minimum practically important effect, equivalence margin, significance claim, new endpoint, or new experiment. No separate hypothesis test is silently substituted for the approved sensitivity procedure.

A prediction-decision record contains the named endpoint/question, intended block list, actual compatible operands, mean changes, sensitivity ranges when justified, gate assessment, operational outcome, reasons, ceiling/quality qualifications, material role, and the separate integrity/claim disposition. These are report contents, not an additional scalar metric or replacement for `result_status`.

Use four operational outcomes:

| Outcome | Meaning |
|---|---|
| `supporting` | The required registered directions are positive and retained across the declared nominal sensitivity ranges, under the stated operationalization. |
| `contrary` | At least one required direction is negative and retained across its sensitivity range, with the full required comparison evaluable. |
| `inconclusive` | Evaluable data do not meet either directional rule, including ties, zero-touching/straddling ranges, or unresolved mixed magnitudes. |
| `not_evaluated` | The intended evidence-qualified comparison lacks required data, comparability, evidence, or the applicable interval. Preserve qualified numeric/descriptive results separately. |

These outcomes are not software-test pass/fail states or population-level statistical verdicts. On stipulated fixtures, the outcome evaluator can be tested under stipulated gate records, while every output remains a fixture with no empirical claim. An actual study cannot obtain an evidence-qualified outcome by copying those stipulated records.

### 6.2 Common eligibility and uncertainty

For the full fixed-suite operational outcome, require the actual registered identities/exposure, relevant independent structural evidence, compatible frame, complete intended primary cells, all applicable coverage gates, and six defined paired blocks. Confirm the intended control manipulation and actual resource limitations for the named claim. Missing a B temperature control can restrict P1 while leaving a separately qualified C-A comparison available.

**[Audit clarification: AF-002; HERO §10.3 and MET §§8.3,10.4]** Applicability is recorded for each named comparison, rather than copied from one run-wide pass/fail state. P1's surface and structural pair diagnostics require the approved text coverage and common text subset. P5's count-based `classified_valid` distinct-20 endpoint requires the approved group, classification, validity, quality, frame, and evidence gates; it does not additionally require proxy-text availability. A missing proxy representation can leave P5 evaluable when the original artifact identity and independently sufficient membership/validity evidence remain established. This exception never admits a sample whose missing material also prevents its class or validity from being accepted. Report unavailable text diagnostics and their reasons alongside any supported P5 result. The P1 quality floor/band retains its separate diagnostic or clean-quality-description role.

Use equal block weights and the same replay-index manifest for linked P1 gains and contrast, seed 20260917 with the actual RNG/version and replay identity recorded. Each linked mean uses the same six blocks. The already adopted interval remains nominal 95% **prompt_resampling_sensitivity**, conditional on the recorded within-block outputs. It does not estimate all model-generation, label, ontology, or prompt-population uncertainty.

If supported descriptive operands exist but resampling assumptions or enough compatible blocks are absent, show their directions with the exact limitation. Do not fabricate a full-scope outcome or population interval. An available-block subset remains separately named and never replaces the six-block target.

Let `mean(x)`, `lower(x)`, and `upper(x)` be the equal-block mean and its declared sensitivity bounds. Define positive-direction retention as `mean(x)>0` and `lower(x)>0`, and negative-direction retention as `mean(x)<0` and `upper(x)<0`. Zero equality fails either strict directional rule. Numerical tolerance does not redefine the scientific zero boundary; calculations use unrounded stored values and expose precision limitations. A diagnosed numerical sign instability withholds the affected decision until corrected; it is not a new effect-size threshold.

This is an operational sensitivity convention, not a confidence-level theorem. A very small positive value remains small and must be displayed as such; no practical importance follows merely from its sign. A degenerate interval adds no general certainty.

### 6.3 P1 rule

Use the approved primary `classified_all` view. For each block:

`surface_gain = surface(B) - surface(A)`;

`structural_gain = structural_pair(B) - structural_pair(A)`;

`gain_contrast = surface_gain - structural_gain`.

Each condition's surface and structural diagnostics share the identical text-eligible sample set. Aggregate all three quantities over the same six blocks. Entropy and SCI remain separate companion quantities.

| Condition after eligibility | P1 operational outcome |
|---|---|
| Positive-direction retention for both surface_gain and gain_contrast | `supporting` for the registered joint proxy pattern. |
| Negative-direction retention for either surface_gain or gain_contrast | `contrary` to at least one required direction; identify which one. |
| Neither row applies | `inconclusive`; report means, bounds, and whether the observed direction is positive, tied, mixed, or negative. |

A positive gain contrast obtained because both diagnostics decreased cannot satisfy the predicted surface increase. Structural gain itself may be zero or negative; no extra requirement that it must rise is added. A contrary outcome can concern failed surface increase, faster structural growth, or both, and the distinction must remain explicit.

Repeat on `classified_valid` only as the prespecified sensitivity, when defined. It cannot replace the primary outcome. If that view differs, show the discrepancy and the changed accepted population. P1 allows a quality decrease in the source prediction; the HERO floor/band therefore remains a diagnostic for the primary pattern and a requirement for an additional **clean quality-comparable** description. An adverse valid-only result or quality decline qualifies the story; it cannot be hidden or described as measured useful creativity.

The baseline surface >=0.95 flag remains visible. It does not change these directional calculations. A ceiling-flagged supporting or contrary label must say it concerns this bounded proxy and finite headroom; lack of observed proxy growth cannot alone establish absence of underlying realization freedom. A ceiling or poor result never authorizes changing the proxy, temperature, categories, or sample budget after inspection.

### 6.4 P5 rule

Use the registered `classified_valid` distinct-20 endpoint, fixed complete-group prefixes, the adopted count-based classification/validity coverage requirements, and the per-cell validity floor and per-block absolute quality band. Apply the endpoint-specific eligibility rule in Section 6.2; proxy text is required for a requested pair diagnostic, not for this structural-count endpoint itself. Record actual resource use and use the phrase **matched planned calls, candidate positions, and output allowance**; do not claim equal actual compute or cost.

For each block, calculate `C-A` and `C-B` separately. Class counts in the all-view and k=5/10 accumulation values remain companion/secondary outputs. No replacement of failed or unclassified candidates is allowed.

For each eligible comparator, positive-direction retention gives `supporting`, negative-direction retention gives `contrary`, and other evaluable outcomes give `inconclusive`. An ineligible comparator is `not_evaluated` for the intended matched-quality claim, even if its descriptive difference is positive.

| Both registered comparisons | Full P5 operational pattern |
|---|---|
| Both eligible and both supporting | `supporting`. |
| Both eligible and at least one contrary | `contrary` to the full two-comparator pattern; retain mixed results explicitly. |
| Both eligible, neither contrary, but at least one inconclusive | `inconclusive`, including a tie against one comparator. |
| Either comparator not evaluated | `not_evaluated` for the full pattern; report each available narrower comparison. |

An observed tie is a lack of observed advantage at this endpoint. Without an equivalence design it does not prove equal capabilities. A positive mean with a zero-straddling sensitivity range is reported as directional but inconclusive under this convention. A larger C valid count outside the quality band remains useful descriptive information and does not justify deleting C successes to force a quality match.

### 6.5 Multiplicity, interpretation, and falsification boundaries

Report the complete P1 joint operands and both P5 primaries together. There is no familywise significance claim from nominal sensitivity ranges and no selection of whichever comparison looks best. Secondary k, thresholded support, individual classes, and within-class diagnostics cannot replace a registered primary. No overall model/theory score is computed.

A valid contrary finding supplies evidence against the corresponding source prediction **under this task, deployment, proxy, resolution, and collection design**. Repeated well-measured contrary findings would warrant revising the predictive account rather than coding them away. A single fixed sorting suite cannot settle every task or the separate recursive-support theory. Exact entropy identities or categorical results under their assumptions are not falsified by an unrelated neural observation.

An inconclusive finding identifies the unresolved operational question; it is not automatically evidence for or against all of Structural Determinacy. Explain the actual limitation without inventing a retrospective escape condition. The result record must preserve both favorable and adverse evidence under identical review and correction rules.

## 7. Outcome and correction fixtures

**[Engineering proposal]** These are non-executable decision-layer fixtures. Unless a row says otherwise, stipulate valid compatibility/evidence records solely for testing the routing logic. They do not assert real independence. Repeated identical block changes in all six blocks produce the displayed degenerate sensitivity ranges under any replay. Rows with explicit nondegenerate bounds stipulate the summary record and test only the decision layer, not a completed resampling run.
| Fixture | Stipulated input | Expected operational disposition | Required reporting |
|---|---|---|---|
| OF-01 | P1: every block surface gain +0.10, structural gain 0, contrast +0.10. | supporting | Positive surface and positive contrast; keep the result labeled fixture. |
| OF-02 | P1: every block surface gain +0.10, structural gain +0.20, contrast -0.10. | contrary | Surface rises, but structural gain exceeds it under this operationalization. |
| OF-03 | P1: every block surface gain -0.10, structural gain -0.20, contrast +0.10. | contrary | The required surface increase fails; never infer support from contrast alone. |
| OF-04 | P1: both gains and contrast exactly zero. | inconclusive | No observed directional change; no equivalence or full-capacity conclusion. |
| OF-05 | P1: positive mean gains but an explicit relevant sensitivity range includes zero. | inconclusive | Positive observed direction does not meet the proposed sensitivity-retention rule. |
| OF-06 | P1: A surface 0.96, B 0.98, structural gain 0 in each block. | supporting with ceiling qualification | Retain the near-ceiling flag and limited headroom; do not replace the proxy. |
| OF-07 | P1: all-view meets OF-01; valid-only sensitivity is adverse and/or the quality floor/band fails. | primary supporting; qualified interpretation | Keep the separate sensitivity and quality deterioration prominent; withhold a clean quality-comparable account. |
| OF-08 | P5: every block valid distinct-20 C-A=+2 and C-B=+1, adopted gates met. | both and full pattern supporting | Show both comparisons and their scoped planned-resource match. |
| OF-09 | P5: every block C-A=+1 and C-B=-1, adopted gates met. | mixed; full pattern contrary | The better A comparison cannot conceal the worse B comparison. |
| OF-10 | P5: every block C-A=+1 and C-B=0. | full pattern inconclusive | A partial observed advantage does not establish both registered directions. |
| OF-11 | P5: every block C-A=-1 and C-B=-2. | both and full pattern contrary | Reporting the adverse result correctly passes the future software test. |
| OF-12 | P5: positive breadth differences, but C validity 19/20 versus comparator 16/20. | matched-quality comparison not evaluated | Difference 3/20 exceeds 0.10; preserve the positive breadth and validity observations. |
| OF-13 | Missing primary cell/block, unsupported B control, absent required independent evidence, or unsupported replay assumptions. | not evaluated for affected full scope | Preserve qualified numbers; do not convert missingness to a null result. A narrower supported comparator can remain. |
| OF-14 | Primary outcome adverse/inconclusive but secondary k=5, an alternative label scheme, or thresholded support is favorable. | original primary outcome retained | No endpoint or ontology replacement. A justified later revision is a separately identified re-analysis. |

The intervals and distances in these decision fixtures are stipulated summaries where no text bundle is supplied. They must not be presented as measured lexical variation or empirical uncertainty. A later end-to-end comparison fixture needs its own actual text/label inputs and independently specified arithmetic oracle; deriving its expected result from the production reporter would be circular testing.

For correction regression, retain MET MF-20 and EI §10.2 as separate fixtures. The latter moves accepted counts `(2,2)` to `(2,1)` while one assignment is reviewed, then to `(3,1)` under corrected evidence. Selected sample count remains four; classification coverage moves `1 → 3/4 → 1`; SCI moves `1/2 → 5/9 → 5/8`. Separately supported validity stays intact. Recompute dependent diagnostics, contrasts, and claim assessments without inventing unspecified lexical values. Independence-only withdrawal changes the claim when its separately sufficient class evidence remains unchanged.

## 8. Upstream coverage index

**[Engineering proposal]** Every previously named conformance requirement is mapped below. Its original definition remains authoritative. Multiple new checks can test different software/evidence portions of one requirement; this index does not turn the number of checks into an integrity score.
| Upstream check / fixture | Mapped future checks |
|---|---|
| SC-T01 | VT-01, VT-14, VT-52 |
| SC-T02 | VT-15, VT-47 |
| SC-T03 | VT-15, VT-47 |
| SC-T04 | VT-15, VT-47 |
| SC-T05 | VT-05, VT-15 |
| SC-T06 | VT-16, VT-50 |
| SC-T07 | VT-16 |
| SC-T08 | VT-15 |
| SC-T09 | VT-15 |
| SC-T10 | VT-04 |
| SC-T11 | VT-02 |
| SC-T12 | VT-14 |
| SC-T13 | VT-17 |
| SC-T14 | VT-02, VT-11 |
| SC-T15 | VT-01, VT-06, VT-16, VT-51 |
| SC-T16 | VT-19 |
| MF-01 | VT-07, VT-09 |
| MF-02 | VT-07, VT-09 |
| MF-03 | VT-07, VT-08, VT-09 |
| MF-04 | VT-07 |
| MF-05 | VT-07, VT-08, VT-10 |
| MF-06 | VT-06 |
| MF-07 | VT-05 |
| MF-08 | VT-06 |
| MF-09 | VT-06 |
| MF-10 | VT-10, VT-11 |
| MF-11 | VT-31 |
| MF-12 | VT-33 |
| MF-13 | VT-32 |
| MF-14 | VT-32 |
| MF-15 | VT-14, VT-34 |
| MF-16 | VT-03, VT-40 |
| MF-17 | VT-40 |
| MF-18 | VT-39 |
| MF-19 | VT-38, VT-42 |
| MF-20 | VT-17 |
| MF-21 | VT-54 |
| MF-22 | VT-53 |
| MF-23 | VT-40 |
| MF-24 | VT-42, VT-43, VT-50 |
| EI-T01 | VT-21 |
| EI-T02 | VT-21 |
| EI-T03 | VT-21 |
| EI-T04 | VT-21 |
| EI-T05 | VT-22 |
| EI-T06 | VT-22, VT-47 |
| EI-T07 | VT-22, VT-47 |
| EI-T08 | VT-22, VT-47 |
| EI-T09 | VT-04, VT-20, VT-47 |
| EI-T10 | VT-23 |
| EI-T11 | VT-23, VT-29 |
| EI-T12 | VT-23 |
| EI-T13 | VT-24 |
| EI-T14 | VT-17 |
| EI-T15 | VT-17 |
| EI-T16 | VT-18 |
| EI-T17 | VT-19, VT-20 |
| EI-T18 | VT-30 |
| HB-T01 | VT-25, VT-27 |
| HB-T02 | VT-25 |
| HB-T03 | VT-25 |
| HB-T04 | VT-25 |
| HB-T05 | VT-16, VT-25 |
| HB-T06 | VT-25 |
| HB-T07 | VT-16 |
| HB-T08 | VT-26 |
| HB-T09 | VT-27, VT-29, VT-47 |
| HB-T10 | VT-29 |
| HB-T11 | VT-35, VT-48 |
| HB-T12 | VT-03, VT-35 |
| HB-T13 | VT-03, VT-35 |
| HB-T14 | VT-03, VT-12, VT-36 |
| HB-T15 | VT-12 |
| HB-T16 | VT-08, VT-09, VT-13, VT-46 |
| HB-T17 | VT-34, VT-35, VT-48 |
| HB-T18 | VT-37, VT-38, VT-42, VT-44, VT-48 |
| HB-T19 | VT-37, VT-38, VT-43, VT-44, VT-49 |
| HB-T20 | VT-40, VT-41, VT-48, VT-49 |
| HB-T21 | VT-17, VT-46 |
| HB-T22 | VT-19, VT-28 |
| HB-T23 | VT-42, VT-43, VT-45, VT-48, VT-49, VT-50 |
| HB-T24 | VT-30 |

PLAN §6's minimum test areas are covered as follows:

| Required area | Future checks |
|---|---|
| Mathematical fixtures and unequal effective counts | VT-07, VT-08, VT-09, VT-13 |
| Label/order invariance | VT-10, VT-11 |
| Missing, invalid, and conflicting evidence | VT-01 through VT-06, VT-14, VT-16 |
| Structural equivalence and consequence-sensitive validation | VT-15, VT-16, VT-25, VT-47 |
| Validity separation | VT-05, VT-06, VT-15, VT-27 |
| Protocol, schema, budget, and dependency comparability | VT-03, VT-12, VT-14, VT-34 through VT-40 |
| Correction propagation | VT-17, VT-18, VT-46 |
| Reproducibility | VT-02, VT-09, VT-10, VT-20, VT-24, VT-31, VT-39 |
| Execution safety and failure handling | VT-19, VT-27, VT-28, VT-36 |
| Deferred metric boundaries | VT-51 through VT-54 |
| Predictions independent of software success | VT-38, VT-42 through VT-45, VT-48 through VT-50 |

The companion RF index maps every first-slice output group to these checks and its permitted inference. No additional schema/compiler, live experiment runner, or automated scientific judge is implied by the mapping.

## 9. Failure, revision, and stop dispositions

**[Audit clarification: AF-001 and AF-002]** Local membership-evidence failure withholds the affected assignment and rebuilds the supported population under MET §4.4. Stop a distribution-level calculation when its shared identity, frame, denominator, or numerical prerequisites fail in a way that prevents a valid accepted subset. Retain supported inventories, subsets, and unrelated cells. Evaluate comparison gates for each endpoint, retaining count-based results when only optional or separately required text diagnostics are unavailable. Stop an affected empirical claim when its own measurement, comparability, independence, or collection requirements fail; preserve any justified descriptive result. Stop all unapproved execution or spending rather than trying to repair authorization through metadata.

If an adverse result has valid evidence and design, report it. It is not an implementation defect by default. If an actual schema/oracle/label defect is found, identify the evidence, affected versions and all conditions, preserve the frozen original, and issue the approved correction/re-analysis path. Apply the same rule to favorable findings. New thresholds, classes, proxies, or endpoints learned from those observations cannot retroactively acquire untouched confirmatory status.

A future record of software tests passing must list exactly which M/V checks ran. A future measurement review must list exactly which E requirements were satisfied for the claim. No amount of fixture coverage closes UD-006 automatically. Deferred capabilities do not become implementation blockers unless their inclusion is separately approved.

## 10. Step 7 acceptance and next step

This step submits the traceability/test mapping, separately labeled software/evidence gates, and bounded P1/P5 outcome rules for owner review. It retains the adopted formulas, task classes, sample budget, threshold bands, and multiplicity boundary. All 54 future checks, the HF/OF examples, and external evidence activities remain unexecuted by this phase.

Approval resolves UD-005's remaining Step 7 design component without accepting missing empirical evidence or approving a study result. The next authorized step, when requested, is Step 8's integrated consistency audit. It must review source fidelity, field coverage, definitions, denominators, classification, safety, sampling, inference, and remaining blockers across the whole document set.

The final `PHASE_0_APPROVAL.md` is reserved for Step 9 after acceptance of that audit. Phase 1 implementation, repository writes, model calls, generated-code execution, spending, and publication remain separately authorized actions.
