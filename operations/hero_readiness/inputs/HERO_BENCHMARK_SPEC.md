# HERO_BENCHMARK_SPEC

## StructDet-Bench: Bounded Integer Sorting Strategy Benchmark

| Field | Value |
|---|---|
| Document version | 0.1 |
| Record date | 2026-09-17 |
| Phase / step | Phase 0 / Step 6 |
| Status | PROPOSED STEP 6 CONTRACT; ready for Theory Owner review |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Approved input contracts | Scope, definitions, structural-class contract, metrics, and evaluation integrity; each version 0.1 |
| Approval evidence | OA-002 through OA-005 in the decision register |
| Decision register | `UNRESOLVED_DECISIONS.md`, version 0.5 |
| Decision authority | Theory Owner |
| Authorized deliverables | This specification and the decision-register update |
| Implementation / repository / collection / execution / publication authorization | None |

## 1. Authority and source basis

**[Owner-approved decision]** The owner approved the Step 5 delivery and instructed: “可以，继续step 6” (“Yes, continue with Step 6”). OA-005 records approval of `EVALUATION_INTEGRITY.md`, version 0.1, and register version 0.4. It authorizes this task specification and the register update. The six preceding plan/specification files remain unchanged; their original status headers are historical delivery metadata.

**[Engineering proposal]** This document selects one task family and its first study design. It owns the concrete domain, mechanism classes, reference/validation design, prompt suite, conditions, sampling budget, extraction, and task-specific comparison gates. The existing documents retain their authority over terminology, assignment states, estimators, independence, and correction. No formula, evidence state, or release boundary is silently replaced here.

The labels **[Source-derived]**, **[Engineering proposal]**, and **[Owner-approved decision]** retain their existing meanings. An engineering label governs the following section until another basis is stated. Proposed requirements use “must” without implying that this newly delivered document has been approved.

| Source | Contribution used in this step |
|---|---|
| SD §§3.2-3.6, 7 | Task-, horizon-, and resolution-relative structural distinctions; consequence-sensitive validation. |
| SD §§5, 6.5, 9.1-9.5 | Finite support, separate validity, Tier 1 algorithm mechanisms, annotation, and prompt-level analysis. |
| SD §9.7, P1 and P5 | Temperature stratification and explicit non-equivalent-mechanism generation as testable predictions. |
| SD §9.6; SI §§8.5-8.6, 9 | Independent evaluation, role/lineage records, tail protection, and correction. |
| SI §§3.1-3.3, 8.1-8.2, 12 | Task-bounded classes, observed-support limits, concentration, and limits of finite evidence. |

SD and SI are the supplied PDF editions and fingerprints registered in the plan. SD's P1/P5 table is on PDF page 21; SI's Tier 1 table and core protocol are on page 20. The papers suggest algorithm-family evaluation but do not specify this integer domain, eight-class registry, Python interface, prompts, temperatures, budgets, tests, or audit quotas. Those choices are engineering proposals in this document. The referenced publications inside the papers have not been independently verified here.

This specification and its illustrative material are AI-assisted. Neither document approval nor formal-looking test descriptions establish independent reference construction. Actual reference, annotation, audit, and experiment evidence remains outstanding under UD-006.

## 2. First task and delivery boundary

**[Engineering proposal; UD-004 hero component]** Select **bounded nonnegative integer sorting**, under an algorithm-mechanism resolution. Graph traversal, path planning, search, scheduling, and open-ended generation remain outside this first task family.

The bounded domain permits comparison-driven, full-key-counting, and digit-driven solutions without requiring a comparison-only interface, an asymptotic runtime class, in-place operation, or stability. The registry is a declared starting reference, not an exhaustive list of possible sorting mechanisms.

The study asks two limited questions:

1. Under identical task instructions, how do the approved surface and structural diagnostics change when the recorded temperature setting changes?
2. At a fixed number of planned calls and requested candidate positions, does an explicit request for different mechanisms yield greater observed valid structural breadth, with quality and coverage reported separately?

### 2.1 Three distinct work products

| Product | What it contains | What it establishes |
|---|---|---|
| First executable milestone | One offline fixture bundle and the approved core calculations/reporting path. | Software behavior on stipulated inputs after implementation is separately authorized. |
| v0.1 comparison capability | Import, analysis, and reporting for the A/B/C collection format below. | Calculations on supplied outputs and accepted evidence; interpretation depends on evidence gates. |
| Actual empirical hero study | A separately authorized, registered collection with independent validation and the Step 7 interpretation contract. | A bounded comparison for the named model deployment, task, suite, and protocol. |

No model/provider is selected and no API adapter, live classifier, execution engine, training loop, or external recruitment is added. An implementer can build the fixture path without obtaining a model account or recruiting reviewers. Real comparisons require their actual inputs and evidence.

## 3. Task, horizon, resolution, and validity frame

### 3.1 Task identity and admissible domain

**[Engineering proposal]** Use these semantic identifiers, subject to owner approval. They are human-readable contracts, not executable schemas.

| Field | Proposed value / meaning |
|---|---|
| `task_id` / `task_version` | `bounded_integer_sort` / `0.1` |
| `analytic_resolution_id` / version | `sorting_mechanism_family` / `0.1` |
| `structural_schema_id` / version | `sorting_mechanism_partition` / `0.1` |
| `reference_registry_id` / version | `sorting_reference_eight` / `0.1` |
| `validity_rubric_ref` | `bounded_integer_sort_validity_v1`, specified in Section 5 |
| Language/interface | Self-contained Python 3 source defining `sort_values(values)`; interpreter and environment pinned in any imported execution evidence. |
| Input | A plain list of plain integers, length 0 through 256 inclusive; each value 0 through 4095 inclusive. Booleans and arbitrary objects are outside the input domain. |
| Output | A new plain list containing exactly the input integers with the same multiplicities, in nondecreasing order. The caller's input list must remain unchanged. |
| Duplicate handling | Preserve multiplicities. Stability of tagged records is outside this task because the interface contains only integers. |
| Auxiliary space | Permitted. The function may allocate lists, counts, buckets, and other ordinary local structures. |
| Performance requirement | No algorithmic complexity target or speed ranking. A future safety envelope limits validation resources separately. |
| Generality | One program must handle the whole declared input domain, not one displayed example or one known test vector. |
| Realization | One candidate's original program text, including its local helpers and comments, extracted by Section 8. |

The input range accommodates a full-key frequency table of 4096 counters and a genuinely multi-stage digit method. Discriminating inputs include values above 255. No hidden negative-key, unbounded-key, record-stability, or constant-space condition invalidates an advertised class.

### 3.2 Operation and artifact constraints

**[Engineering proposal]** Programs may use ordinary loops, recursion, comparisons, integer arithmetic/bit operations, local containers, and ordinary built-ins such as `len`, `range`, `enumerate`, `list`, `min`, and `max`. Helper functions must be included in the same candidate. Basic copying, local storage, and container access do not themselves determine a structural class.

The generation task prohibits imports, `sorted`, any `.sort` delegation, external/opaque ordering routines, dynamic source execution, reflection used to bypass restrictions, randomness, filesystem/network/process access, and persistent cross-call state. It permits no shared implementation between the five candidates. A candidate must remain self-contained when separated from the other four.

These are task constraints and inspection targets, not a claim that string matching can enforce them. Renaming a prohibited operation does not make it permitted. Built-in ordering delegation may violate validity while also leaving its mechanism unresolved. An ordinary self-implemented heap, count table, or radix pass is eligible.

### 3.3 Consequence horizon and mechanism resolution

**[Source-derived: SD §§3.2, 3.6; SI §3.1]** Structural distinctions depend on the declared consequences and resolution. Matching final sorted values alone cannot distinguish algorithm mechanisms at the selected resolution.

**[Engineering proposal]** The consequence horizon is one complete sorting invocation, assessed across the stated input domain. The mechanism signature concerns how ordering information is acquired, maintained, and used to place values. The observation scope includes nontrivial reachable branches and imported mechanism-relevant traces or equivalent formal/inspection evidence.

| Signature dimension | Declared consequence-bearing question |
|---|---|
| Ordering decision | What operation determines which values precede others: adjacent comparison, prefix placement, rescanning selection, pivot relation, run merge, maintained heap order, whole-key address, or digit refinement? |
| Maintained organization | Which invariant makes subsequent ordering steps possible? |
| Decomposition and recombination | Are subproblems formed by position, pivot outcome, digit, or another declared rule, and how are they combined? |
| Branch applicability | Does the same family organize all reachable nontrivial cases, allowing only the variations declared below? |
| Information transport | How does the mechanism preserve and move the values or their multiplicities while building the ordered output? |

Identifiers, comments, helper layout, recursion versus an equivalent explicit work stack, local copying, and representation details are ignored when they preserve the class's declared organization. Exact comparison counts, wall-clock time, all control-flow details, and fine subfamilies are outside this resolution. They must not be used to split a class after results are inspected.

The resource timeout is a validation safeguard; it does not define `T`. A resource overrun limits the tested assessment and does not prove mathematical nontermination.

## 4. Structural class registry and membership contract

### 4.1 Common assignment rule

**[Engineering proposal]** Assign one of the eight IDs below only when the observed artifact instantiates that descriptor and the evidence addresses all relevant reachable branches. The same family ID defines the proposed equivalence class at this resolution. This rule still requires schema-level validation of the abstraction and sample-level evidence under `STRUCTURAL_CLASS_CONTRACT.md`, Sections 4-6.

No class is assigned from a function name, a comment, a model explanation, or identical returned values alone. No new class is created automatically for an unknown output. Correct solutions outside the current schema remain eligible task solutions, with unresolved structural membership and retained evidence.

All descriptors apply to the entire domain in Section 3. They allow empty/singleton handling, a direct size-two comparison, copying, and a verified already-ordered fast path. Such operations must not implement a second general sorting strategy. An insertion routine on subproblems larger than two, a fallback to another family, or a data-dependent strategy switch is a hybrid unless already covered by a uniquely applicable descriptor.

### 4.2 Eight proposed descriptors

**[Engineering proposal]** The IDs are stable labels within this schema. Their meanings come from the criteria below, not from familiar algorithm names alone.

| ID / family | Constitutive membership rule | Permitted variation at this resolution | Discriminating evidence and boundary |
|---|---|---|---|
| `SORT-ADJ` / adjacent sweep | Repeated traversals compare adjacent positions and move local inversions across an active interval until the interval is ordered or a no-change condition is reached. The sweep/active-interval organization determines progress. | Left/right direction, alternating directions, shrinking boundaries, and an early no-change exit. | Inspect sweep-level progress and adjacent inversion handling. Adjacent swaps inside placement of one incoming value into a growing sorted prefix are evaluated under `SORT-INS`, rather than labeled by the swap instruction alone. |
| `SORT-INS` / sorted-prefix insertion | A contiguous ordered prefix grows by selecting the next not-yet-inserted value and locating/inserting it within that prefix, preserving prefix order before the next value is admitted. | Shifts versus adjacent moves; linear versus binary search for the insertion location; equivalent list representations. | Establish the outer prefix-growth invariant and placement dependency. Gap-scheduled passes over interleaved subsequences are outside this descriptor. An insertion helper inside another full-size strategy does not create a second observation. |
| `SORT-SEL` / rescanning extremum selection | Each output/frontier step obtains the next minimum or maximum by examining the current unsorted region afresh, then removes or places that value and advances the ordered region. | Minimum/maximum direction; swapping into a boundary or removing into a fresh output list. | Trace or inspect a fresh extremum selection from the remaining region. A maintained heap/tournament used to obtain the next extremum belongs to `SORT-HEAP` when its descriptor holds. |
| `SORT-MERGE` / ordered-run merge | Subsets/runs are ordered and then combined by choosing among run frontiers while preserving each run's internal order. Progressive ordered merging performs the general recombination. | Top-down or bottom-up organization, explicit stack, natural-run discovery, and equivalent merge storage. | Establish ordered runs, their formation, and frontier-based merge decisions. Natural-run discovery may reverse a monotone descending run; using another general sorter on runs larger than two is a hybrid under this schema. |
| `SORT-PIVOT` / pivot partition | A key-selected pivot partitions a nontrivial region by comparisons to that pivot; recursively or iteratively sorting the resulting regions and placing/combining them establishes order. | Pivot selection; two-way/three-way partition; in-place/copying; recursion/explicit stack. | Establish pivot-dependent partition predicates, subproblem boundaries, and recombination. Position-based splitting followed by ordered merging is `SORT-MERGE`. Bit/digit-defined decomposition without a key-selected pivot is considered under `SORT-RADIX`. |
| `SORT-HEAP` / maintained heap extraction | A heap-order relation is established and maintained while successive root extrema are extracted or placed to build the sorted result. | Min/max heap, bottom-up/incremental heap construction, local array/tree representation, and output direction. | Establish heap-order maintenance and its role in each extraction. A fresh full-region extremum scan with no maintained heap is `SORT-SEL`. External heap libraries are prohibited by the task. |
| `SORT-COUNT` / full-key frequency ordering | Full key values address frequency/position information; scanning the full-key order, with multiplicity expansion or cumulative positions, determines the result. | Fixed 4096-key or observed-range table, ascending key-range scan, frequency expansion or cumulative placement. | Establish whole-key addressing and numeric-order traversal. Sorting a dictionary's distinct keys with another general sorting mechanism is a hybrid. A single distribution over the complete key is counting at this resolution, even when described as one-pass radix. |
| `SORT-RADIX` / multi-stage digit refinement | Proper parts of the key drive multiple reachable refinement stages or digit-recursive subdivisions; significance/order-preservation relations combine them into full-key order. Full ordering is not decided by one complete-key table. | Least-significant-first passes with required order preservation; most-significant-first subdivision; explicit bit/digit widths; equivalent bucket/count storage. | Verify at least one permitted nontrivial input exercises multiple proper-digit stages and the significance/ordering dependencies. Whole-key counting in one stage is `SORT-COUNT`. A counting operation used only inside proper-digit refinement is a component of this family, not a separate full-key mechanism. |

### 4.3 Defects, hybrids, and unknown mechanisms

**[Engineering proposal]** Class membership concerns the implemented organization, not the intended repaired program. A defect confined to an empty-input return, caller-input preservation, final transfer, or similar interface detail may leave enough evidence for a class assignment while causing `invalid` validity. If a defect removes a constitutive relation, the class cannot be retained merely because the author named it.

For each adjudicated artifact, record whether the defect is outside or inside the descriptor's constitutive relation, and why. An unstable least-significant-digit routine, for example, cannot be accepted solely on its radix label; reviewers must decide whether the required refinement organization is actually present. An unimplemented sketch or truncated decisive branch is not mentally completed.

| Situation | Proposed treatment |
|---|---|
| One applicable descriptor with sufficient evidence | One accepted assignment, subject to the named evidence policy. |
| Generic helper used within a class's declared mechanism | Classify the whole program at this resolution; no component-count inflation. |
| Two general mechanisms selected by a reachable branch | `unresolved` / `hybrid_boundary`, unless a future approved schema supplies a suitable composite class. |
| Gap-scheduled insertion or another eligible unregistered mechanism | `unresolved` / `novel_candidate`; “novel” means new to this registry, not newly invented historically. |
| Two descriptors remain plausible | `unresolved` with the conflicting criteria and evidence. No first-match or desired-score tie-break. |
| Opaque ordering delegation | Preserve any known validity violation; retain unresolved/unclassified mechanism status as justified. |
| Empty, malformed, refused, or incomplete material | Preserve completion/format evidence and apply the general classification/validity rules. It contributes no invented failure class. |

Only new evidence and versioned revision can add a class or change a boundary. Re-analysis must consider all affected conditions. An unresolved but valid solution stays in validity accounting and the frontier review record; it cannot silently disappear as an invalid or out-of-domain sample.

### 4.4 Schema validation and nontrivial witnesses

**[Engineering proposal]** For every class, require two independently reviewed reference realizations with an allowed implementation variation, membership arguments, and witness observations or equivalent formal evidence. At least two nontrivial input shapes must exercise the defining operation. Output-only tests do not satisfy this requirement.

The following witness set is proposed for imported mechanism evidence. These lists are test-design inputs, not executed traces or empirical results.

| Witness ID | Input or input construction | Intended discrimination |
|---|---|---|
| W-01 | `[7, 1, 6, 2, 5, 3, 4, 0]` | Multiple placements/sweeps/selections/partitions/merges; avoids already-ordered trivial paths. |
| W-02 | `[3, 1, 3, 0, 2, 0, 2, 1]` | Duplicate transport, equal-pivot handling, count multiplicity, and repeated-key dependencies. |
| W-03 | `[256, 1, 4095, 255, 16, 0, 257, 4094]` | Whole-key ordering versus proper-digit refinement across digit boundaries. |
| W-04 | `[0, 1, 2, 3, 7, 6, 5, 4]` | Run formation, sorted-prefix progress, and adaptation/branch inspection. |

At minimum, discriminate `ADJ/INS`, `SEL/HEAP`, `MERGE/PIVOT`, and `COUNT/RADIX` using role/control dependencies rather than names. Reference validation must also examine all 28 unordered pairs of the eight descriptors for overlapping rules, recording a distinguishing argument or an unresolved overlap. This is a descriptor review, not a demand for all-pairs empirical program execution.

Counterfactual checks include a same-class renaming/helper-layout change and a mechanism-changing replacement such as a fresh scan replacing a maintained heap, or a whole-key table replacing digit refinement. The latter can preserve final correct outputs while changing the declared mechanism signature. Record exact artifacts and consequences; a written intention to perform these checks is not their completion.

## 5. Separate validity rubric and domain evidence

### 5.1 Assessment scope

**[Engineering proposal]** `bounded_integer_sort_validity_v1` has separate recorded dimensions: source/interface conformance, permitted operations and self-containment, input-domain handling, observed functional correctness, and assessed input preservation. The final `validity_status` retains the approved `valid`, `invalid`, `undetermined`, and `not_assessed` vocabulary.

An accepted `valid` assessment requires a complete original program, evidenced conformance inspection, and successful execution of the full registered functional suite in the declared external environment. It means **valid under this bounded rubric and tested scope**. Finite testing does not establish universal correctness over every possible list in the whole domain. An equivalent exhaustive/formal validation route would require its own identified proof assumptions and comparability review rather than silently replacing this rubric.

A proven counterexample, observed exception on an admissible input, observed input mutation, or clear forbidden delegation supports `invalid`. A harness failure, missing environment evidence, absent test results, or resource exhaustion without a decisive task violation supports `undetermined`, with the limitation identified. A timeout alone cannot certify mathematical nontermination.

### 5.2 Functional oracle

**[Engineering proposal]** For each admissible input, the trusted external validator checks that the returned value is a fresh plain list of plain integers, its length matches the input, every adjacent output pair is nondecreasing, the integer-frequency mapping matches the original input, and the original caller list remains unchanged. The oracle uses these declared properties rather than trusting another submitted sorting program or a generator's claimed expected answer.

The validator's own implementation, property interpretation, and artifact/input association require independent review under `EVALUATION_INTEGRITY.md`. A property written here, or a deterministic implementation of it, does not itself certify that review. Oracle checks and return-object identity observations remain outside the untrusted candidate's authority.

### 5.3 Registered functional suite

**[Engineering proposal]** Define the complete suite by the constructions below. The exact ordered input manifest and its hash must be materialized and reviewed before collection-dependent validity judgments. This phase creates no executable input generator or candidate code.

| Segment | Construction | Number |
|---|---|---|
| V-SMALL | Every list of lengths 0, 1, 2, 3, and 4 over the ordered alphabet `[0, 1, 255, 256, 4095]`; lengths ascending, then lexicographic order. | 781 |
| V-SHAPE | For each length `n` in `[8, 64, 256]`, the six patterns below in the stated order. | 18 |
| V-KEY | Singleton `[x]` and two-element `[4095-x, x]` for each `x` from 0 through 4095, in increasing x order, singleton first. | 8192 |
| V-STAGE | W-01, W-02, W-03, and W-04 in that order. | 4 |
| **Total** | Repeated equal inputs arising from different constructions retain their test IDs and purpose. | **8995** |

V-SHAPE uses these six deterministic patterns, with zero-based index `i` from 0 through `n-1`:

1. Increasing: value `i`.
2. Decreasing: value `n-1-i`.
3. Alternating extremes: `0` at even i and `4095` at odd i.
4. Equal values: `256` everywhere.
5. Distributed values: `(73*i + 19) modulo 4096`.
6. Repeated digit boundaries: repeat `[255, 256, 4095, 0, 257, 1, 4094, 16]` and take its first n entries.

This suite intentionally covers every allowed key in small inputs and larger ordering patterns without pretending to exhaust all length-256 lists. It contains no sampled random tests, so no hidden test-generation distribution must be inferred. Passing it remains bounded evidence. Other challenge cases can be retained as externally sourced incidents, with corrections and any expanded rubric versioned.

The suite does not require 8995 new model outputs. Each candidate program is checked on these inputs in a separately authorized external validation process. v0.1 only imports that process's evidence. Short-circuiting after a decisive counterexample may establish `invalid` with its scope recorded; claiming `valid` requires complete suite coverage. Execution batching may reduce overhead only when test identities, input isolation, evidence, and limits are preserved.

## 6. Core reference set, independent annotation, and audit

### 6.1 A 32-artifact core specification

**[Source-derived: SD §9.4; SI §§8.5-8.6]** Preserve two independent human first-pass annotations for the named core validity set and Tier 1 domain validation plus sampled human audit. The sources supply no universal numeric quota.

**[Engineering proposal]** The initial core is a **32-artifact design**, not 32 existing validated programs. Its material must be supplied under separate authorization with origin and exposure records. Proposed set ID: `sorting_core_32`, version `0.1`.

| IDs / count | Required content | Required review |
|---|---|---|
| `CORE-<family>-A/B`, 16 | Two correct reference implementations per class, showing a permitted variation. Suggested contrasts: sweep direction; linear/binary insertion search; min/max selection; top-down/bottom-up merge; two-/three-way pivot; min/max heap; count expansion/cumulative placement; least-/most-significant-digit refinement. | Two independent initial human assignments and validity judgments; class-specific mechanism argument/witnesses; full functional suite or a separately approved proof route. |
| `CORE-<family>-D`, 8 | One defective artifact per class in which an independently established mechanism remains identifiable but a concrete interface/boundary/copy/transport error makes the output invalid. Each defect must be checked against that class's constitutive relations. | Two initial judgments, explicit counterexample, and agreement/adjudication on why class membership is preserved or why the proposed case must be revised. |
| `CORE-X01` through `CORE-X08`, 8 | The boundary/negative cases listed below. | Two initial judgments under the same states and rubric; unresolved outcomes remain legitimate when justified. |

The boundary cases are: insertion implemented by adjacent swaps versus sweep organization; fresh selection versus a maintained heap; positional merge versus pivot partition; full-key counting advertised as one-pass radix; an unregistered general hybrid; an eligible gap-scheduled strategy outside this registry; opaque built-in sorting delegation; and a misleading/unused algorithm fragment with an incomplete decisive path. The actual artifacts must isolate the intended issue rather than rely on these titles as expected ground truth.

These case specifications do not preassign empirical labels. If independent review overturns a proposed expected distinction, preserve the finding and correct the schema or case before relying on it. No numerical agreement threshold can excuse an unresolved schema-defining contradiction. Initial per-item decisions, disagreements, and adjudication changes remain visible; post-consensus agreement is not initial agreement.

Reference construction must document AI assistance and any relationship to the evaluated lineage. Independently checked domain constraints can add an external evidential path without erasing the original design's derivation. Missing core material or reviewers restricts validated-measurement claims, not the future fixture implementation.

### 6.2 Review of actual generated outputs

**[Engineering proposal]** Each accepted empirical assignment requires an evidence-linked mechanism judgment; each accepted valid assessment requires the rubric evidence. The toolkit imports these records. It does not infer classifications from the function's name or run a model judge.

For the complete main collection in Section 7, the sampled human audit selects **one planned candidate position from each five-position generation group**, giving 72 planned audit positions across 72 calls. This is a position-balanced systematic audit, not an estimator of population error. For one-based block index b, condition index c (`A=1`, `B=2`, `C=3`), and group index g, select position:

`1 + ((b + c + g - 3) modulo 5)`.

Selection is fixed before output inspection. A missing selected position is recorded as a missing audit opportunity and is not replaced by a more convenient candidate. Per-group completion and output-format issues are reviewed separately. At least one qualified human independently reviews each available selected artifact, blind to the initial label and condition where feasible, using the applicable domain evidence.

Additional targeted audit covers every unresolved classification dispute or novel/hybrid candidate relied on in reporting, every challenged essential evidence record, and all observed low-count accepted cases where a class appears once or twice in a 20-realization cell. It also covers at least one observed occurrence of each registered class in each condition across the suite, where available. Overlapping selections are reviewed once with all selection reasons recorded.

These targeted additions never become extra generator observations or a random-error estimate. The audit can cover all outputs in a difficult batch; its maximum distinct main-study artifact count is 360. Incomplete mandatory audit coverage restricts the corresponding validated comparison. No audit expense or personnel engagement is authorized here.

Core reviewers may participate in broader roles after their independent core first passes are preserved. A disputed case is escalated to an independent domain expert under the approved integrity contract. No fictional reviewer identities or completed annotations are supplied by this document.

### 6.3 Reference protection and open correction

**[Engineering proposal]** All eight reference families receive a positive preservation quota: the two distinct positive core variants and one reviewed defect/boundary record per family must remain accessible with their version history. `SORT-COUNT` and `SORT-RADIX` additionally receive explicit protection for the whole-key/digit boundary and W-03 evidence. This designation preserves a contrast the task permits; it does not assert these classes are empirically rare or superior.

“Appeared once or twice” is a task-cell-specific audit trigger, not a model-wide rarity claim or a frequency filter. Zero observed count never triggers confirmatory resampling until the class appears. The registry remains open to eligible unregistered mechanisms through the frontier and incident records. Admitted new classes or disputed boundaries require versioned, cross-condition re-analysis under the existing correction contract.

## 7. A/B/C generation design and fixed suite

### 7.1 Matched coordinated sets

**[Engineering proposal; UD-005 concrete design]** All three conditions request **five candidates in one fresh call**. Thus A, B, and C have the same coordinated-set size and output format. A uses ordinary “five versions” wording. B uses exactly A's visible prompt with a higher declared temperature. C changes only the request for variation, explicitly asking for different mechanisms, and uses A's decoding settings.

This choice avoids comparing C's five-answer coordinated call against A's five unrelated one-answer calls. The five candidates within each call remain dependent. Repeated groups have fresh contexts with no previous outputs supplied. Statistical records preserve groups, prompts, conditions, and any other known coupling. Fresh contexts alone do not establish perfect statistical independence.

| Parameter | A: ordinary versions | B: higher temperature | C: different mechanisms |
|---|---|---|---|
| Candidate positions requested per call | 5 | 5 | 5 |
| Visible prompt | Common assembly with A clause | Byte-identical to A for the same block | Common assembly with C clause |
| Proposed temperature | 0.4 | 1.0 | 0.4 |
| Proposed top-p | 1.0 | 1.0 | 1.0 |
| Presence/frequency penalties | 0 where exposed | Same as A | Same as A |
| Generator seed | No user-fixed seed requested; record actual control/status | Same policy | Same policy |
| Maximum output allowance | 8192 model-token units under one recorded cap convention | Same | Same |
| Tools/retrieval | None requested | None | None |
| History | Fresh call; no previous samples or reference implementations | Same | Same |
| Output selection or best-of | No reranking or chosen-best response | Same | Same |

These values are proposed experimental settings, not claims about any provider's supported range. Unsupported or hidden controls must be recorded accurately. A deployment that cannot expose a meaningful A-to-B temperature manipulation cannot supply that P1 experiment. It may supply a qualified A/C comparison when its controls and evidence support that narrower use. No alternative manipulation is silently called temperature.

### 7.2 Exact visible prompt assembly

**[Engineering proposal]** Construct the user prompt as the selected block opener, one blank line, the common task text, one blank line, the condition clause, one blank line, and the common output-format text. Use LF line endings and record the actual sent bytes. Bracketed descriptive labels in this document are not sent. No registry, algorithm list, reference code, adjudication rule, previous answer, or desired metric outcome is included.

The six fixed main-study openers are:

| Block | Exact opener |
|---|---|
| P01 | `Implement the sorting function specified below.` |
| P02 | `Write implementations for the following integer-sorting task.` |
| P03 | `Provide programs that meet this sorting specification.` |
| P04 | `Solve the following bounded integer-ordering problem in Python.` |
| P05 | `Create implementations of the function described below.` |
| P06 | `Produce Python solutions for this list-sorting interface.` |

These are six fixed prompt phrasings of one task, not six independent task families or a random sample of all prompts. Their relevance is limited to this declared suite.

**Common task text:**

```text
Define sort_values(values) in Python 3.

The input is a plain list of plain integers. Its length is from 0 through 256 inclusive. Every integer is from 0 through 4095 inclusive. Return a new plain list containing the same integers with the same multiplicities, in nondecreasing order. Do not change the input list. Your program must handle the entire stated domain, including empty lists and repeated values.

Additional local memory is allowed. There is no requirement to sort in place, preserve the identities of equal records, or meet a particular asymptotic running-time bound. Only integers are supplied.

Use self-contained source with all helper functions included. Do not use imports, sorted, any .sort method, or another external ordering routine. Ordinary loops, recursion, comparisons, integer arithmetic, local containers, and basic built-ins such as len, range, enumerate, list, min, and max are allowed. Do not use randomness, dynamic code execution, reflection, filesystem or network access, subprocesses, or persistent state. Each candidate must work by itself without code from another candidate.
```

**A and B condition clause:**

```text
Produce five versions of a solution to this task.
```

**C condition clause:**

```text
Produce five solutions to this task using five different ordering mechanisms. Differences only in names, comments, formatting, or local implementation details do not count as different mechanisms. Keep the task and its constraints unchanged.
```

**Common output-format text:**

```text
Return exactly five numbered sections headed ### Candidate 1 through ### Candidate 5, in that order. Each section must contain exactly one fenced python code block holding a complete independent program that defines sort_values(values). Put helpers inside that same code block. Include no prose outside the code blocks apart from the five section headings. Comments inside the code are allowed. Do not supply tests, examples, imports, or a main program.
```

A and B use no additional visible system instruction in the proposed direct-collection profile. Any unavoidable platform/system instructions, formatting wrapper, reasoning configuration, or hidden context are recorded with their knowledge/access states. A locally added visible instruction must be identical across the three conditions and frozen in the run binding; it changes the actual prompt protocol and must be disclosed. No claim of a fully controlled context is made when a material part is unknown.

The shared code-only format may constrain generation. It is part of the benchmark condition and is not generalized to unrestricted prose. Comments remain in the surface diagnostic under the approved tokenizer. The code's apparent algorithm name is never the label source.

### 7.3 Pilot and main collection budgets

**[Source-derived: SD §9.5]** SD describes twenty generations per prompt-condition cell as a low-cost starting point and prefers fifty or more for tail analysis. It also requires prompt-level aggregation and recognition of finite support. Those counts do not by themselves establish independent draws or adequate statistical power.

**[Engineering proposal]** The hero adopts a small fixed-suite main collection: **six blocks × three conditions × four calls × five requested candidates**. It is not a comprehensive tail or latent-capacity experiment.

| Collection | Prompt blocks | Calls per block-condition | Planned calls | Requested candidate positions | Maximum output-token allowance |
|---|---|---|---|---|---|
| Separate optional pilot | P00 only | 2 | 6 | 30 | 49,152 |
| Main fixed suite | P01-P06 | 4 | 72 | 360 | 589,824 |
| Total when the pilot is authorized too | Disjoint pilot/main material | As above | 78 | 390 | 638,976 |

Pilot opener P00 is `Prepare Python implementations for this bounded sorting task.` The other prompt components and provisional controls are the same. Pilot data checks formatting feasibility, truncation, environment operation, and reference/rubric application. Its outputs remain marked `pilot`. Any resulting prompt, limit, schema, or rubric change must be versioned before the new main design is frozen. No pilot output is silently reused as main evidence.

These are ceilings and design counts, not actual usage or a cost quote. Input tokens, hidden/reasoning-token charges, server-side work, and annotation/validation costs are additional or differently defined resources. No dollar spend is authorized. The owner separately selects a collection method and spending ceiling before any paid operation. The main collection need not occur to build the offline software.

Each main block-condition has four dependency groups and twenty requested positions. Prefix values are fixed at **k = 5, 10, 20**, with **k = 20 the primary P5 endpoint**. The first two values are secondary accumulation diagnostics. Observed support and the core distribution metrics use the declared complete cell inventory; optional thresholded support uses `min_empirical_frequency = 0.10` as a separately labeled descriptive view. Thresholding never filters the primary sample or hides low-count classes.

This choice yields twenty candidate positions from four coordinated calls per cell. It must not be described as twenty independent generation calls, nor as fifty-sample tail evidence. A later larger-budget study requires its own registration; collection does not automatically expand because the initial results are unclear.

### 7.4 Collection order and no adaptive continuation

**[Engineering proposal]** Within each cell, order groups 1 through 4 and positions 1 through 5. That order determines `sample_order`; file storage order does not.

For external collection, cycle group index g first, then block index b. Within each block/group, use the condition permutation at index `(b + g - 2) modulo 6` in this zero-based list:

`ABC, ACB, BAC, BCA, CAB, CBA`.

This rotates A/B/C ordering across the six blocks. Keep collection within one declared deployment window; record timestamps and any detected model/control change. Interleaving reduces one simple order confound by design, but does not prove the absence of deployment drift. Cross-block shared generation history or material serving changes require a comparability assessment under the metric contract.

Execute no collection in Phase 0. In a future authorized main study, issue one attempt per planned call slot and disable automatic retries where possible. Failure, refusal, truncation, poor quality, repeated mechanisms, or an inconvenient result never earns a replacement call. Provider-side automatic retries are recorded where observable; unknown attempts remain unknown. A necessary revised collection receives a new identity and registration, preserving the abandoned material and reason.

## 8. Response extraction, missingness, and budget interpretation

### 8.1 Original artifacts and candidate positions

**[Engineering proposal]** Preserve the complete raw response and attempt identity. The requested headings identify positions 1 through 5. Each unique, unambiguous heading owns the body until the next heading or response end. A candidate's ordinary extraction is the exact contents of its single fenced Python code block, preserving comments, literals, whitespace, and code bytes. Fences and section headings are excluded from that text region; the original bytes and offsets remain auditable.

Multiple code blocks, duplicated/out-of-range headings, absent headings, or ambiguous association are recorded as format/extraction failures. Do not select the best block, merge candidate sections, invent a heading, or repair code. A uniquely titled malformed candidate body can be retained as an invalid/incomplete candidate artifact with its original body and extraction limitation; it cannot be converted into a completed program.

An unclosed final code fence may produce a uniquely identified truncated candidate text from its opening fence to response end, with `completion_status` and extraction status recorded. Whether its partial mechanism can be assigned depends on actual evidence under the structural contract. A quoted intended implementation or a reviewer-supplied completion is never substituted.

A known emitted empty candidate body is an empty artifact, with no usable surface text or structural assignment. A candidate position never emitted has no realization. A failed call without a response has no five artificial failure samples. Keep a five-position **plan inventory** separate from the realized-sample inventory.

If extra unrequested candidates appear, preserve them in the raw/unselected inventory and record the deviation. Do not add them to the planned k budget. If the first five positions cannot be associated unambiguously, withhold the affected grouped comparison rather than inventing a selection order.

### 8.2 Selection before outcomes

**[Engineering proposal]** For a complete cell, the selected main sequence consists of the four groups in registered order, each with five observed candidate positions. Apply `classified_all` and `classified_valid` only after this selection. Invalid, provisional, unresolved, and unclassified material is never replaced with a later success.

Group format/completion is reported separately from each program's functional validity. A complete correct candidate does not become functionally invalid solely because another candidate in its call is missing. The call can fail the five-position format requirement while supporting some individual descriptive observations.

For a damaged cell, keep supported descriptive core summaries on actual identified realizations. The primary P1 comparison also uses the full planned twenty-position cells; incomplete groups restrict it to qualified descriptive comparison. A numeric prefix exists only if it contains at least k actual selected realizations with established order. For the registered matched study, a prefix must additionally contain the intended **first complete groups**: group 1 for k=5; groups 1-2 for k=10; groups 1-4 for k=20. Missing positions cannot be compressed away so later groups fill the planned prefix. The ordinary metric may remain descriptive under its own rule, while this study's matched-group endpoint is withheld.

This distinction preserves the approved estimator and its study-specific eligibility gate. A complete twenty-position cell with no accepted classifications can legitimately report distinct-20 equal to zero with zero classified coverage. A nineteen-realization cell cannot report a completed matched distinct-20 count.

### 8.3 Resource matching and actual accounting

**[Engineering proposal]** The primary design matches planned group count, requested output positions, visible format, model state where established, and output-token allowance. C's explicit mechanism clause is longer than A's; actual input/output tokens, latency, hidden computation, and charges are not guaranteed equal. Report them where known.

Use the phrase **matched planned calls, candidate positions, and output allowance**. A claim of equal actual tokens, equal compute, or equal dollar cost requires additional measured evidence and is outside this first experiment's primary target. Do not truncate outputs after generation to equalize token totals.

| Resource/evidence record | Required meaning |
|---|---|
| Planned and actual attempts | Planned slot, actual attempt, failure, retry/automatic-retry status, raw-response linkage. |
| Planned and actual candidate positions | Requested positions, emitted/identified artifacts, absent/ambiguous positions, extras, group completeness. |
| Token allowance | Requested cap, unit/tokenizer, whether it covers visible output only or includes hidden reasoning, and whether the control was enforced. |
| Actual usage | Input/output/reasoning quantities separately where exposed; unknown or unavailable components retain their states. |
| Other resource records | Collection duration, service changes, validation environment limits, and review effort where collected. |
| Monetary authorization | Separately granted spending ceiling and actual known charges, or explicit absence of authorization. No price is inferred here. |

If a control's effective behavior differs across conditions, the matched-control claim is restricted. If temperature is merely declared but not exposed/enforced, preserve the data as qualified observations rather than certifying a temperature intervention.

## 9. Run binding and preregistration before an empirical collection

**[Engineering proposal]** This generic specification has no hidden dependence on a particular vendor. A future collector completes the following run binding before any main output is inspected. These are empirical-instance metadata, not unresolved implementation rules for the offline reader.

| Binding | Required value or explicit limitation |
|---|---|
| Model/deployment | Identifier, family, checkpoint or immutable deployment identity where accessible; exact unavailable components and window. |
| Interface controls | Actual parameter names/semantics, supported temperature values, top-p/penalties, output cap, tools/history, reasoning settings, automatic retries. |
| Prompt assembly | Sent user/system content, hashes, block-to-condition mapping, unavoidable hidden context. |
| Material identities | Task/schema/rubric, registry/core/test manifest, extraction version, annotation/audit plan, analysis settings. |
| Collection | Main/pilot designation, order, intended attempt manifest, group/position IDs, timestamps, budget and separate spend authorization. |
| Evidence plan | Reference provenance, responsible roles, actual review arrangements, calibration if any model assistance is used, and known open requirements. |
| Analysis plan | k grid and primary endpoint; evidence policies; coverage/quality gates; resampling setup; outcome interpretation contract from Step 7. |
| Exposure | What task/reference/pilot material each role or system has seen, and what remains unknown. |

No exact checkpoint or opaque provider behavior is invented to complete a form. An available deployment identifier can support an appropriately limited deployed-system comparison; it cannot support an unqualified fixed-parameter causal claim when stability is unknown.

The main study is **preregistered fixed-suite evaluation** only when the identities, design, and Step 7 criteria were fixed before the relevant observations. Earlier exposure or design changes require an exploratory/re-analysis label for the affected inference. A hash created after inspection does not provide earlier registration.

## 10. Analysis, quality gates, and permitted interpretation

### 10.1 Endpoint map

**[Engineering proposal]** All calculations use the approved `METRICS_SPEC.md`, version 0.1. This section selects study endpoints and gates without creating alternative estimators.

| Output | Selection and population | Role |
|---|---|---|
| Support, H, SCI, both effective counts | Declared cell inventory; `classified_all` and `classified_valid` separately. | Core descriptive measurement with counts and evidence. |
| Thresholded observed support | Empirical-frequency threshold 0.10; same identified conditional denominator. | Secondary descriptive view; no filtering of primary counts. |
| Distinct-k | Ordered complete-group prefixes at k=5, 10, 20; both views. | Accumulation; k=20 is primary for P5. |
| Surface/structural pair diagnostics | The same eligible-text subset within each population, as defined in the metric contract. | Paired-level surface versus structural comparison. |
| P1 | B-A surface gain, B-A structural-pair gain, and their approved gain contrast; primary `classified_all`. | Restricted test of P1 at these two settings and this proxy/resolution. |
| P1 sensitivity | Repeat the same diagnostics on `classified_valid`, when defined. | Discloses validity-conditioned behavior; does not replace the primary view. |
| P5 | C-A and C-B valid distinct-20 differences, separately; all-classified counterparts and validity accounting alongside. | Observed valid breadth at the registered planned budget. |
| Within-class proxy | Per-class values and the approved pair-weighted aggregate, with pair counts. | Secondary realization diagnostic; changing class composition remains visible. |

The class-pair statistic and the lexical-trigram distance must be evaluated on identical eligible samples within each condition. Entropy remains in nats and is not subtracted from lexical distance. No new implementation of frontier location, expressible-support estimation, SHL, ERR, or latent diagnosis is selected.

### 10.2 Fixed-suite aggregation and uncertainty

**[Engineering proposal]** The intended main summary uses all six registered blocks with equal block weight. Candidate rows and within-call pairs are never treated as independent prompt replicates. Do not pool class labels across blocks to create a single enlarged support count.

Use the approved 2,000 paired prompt-block resamples, nominal 95% percentile endpoints, and exact quantile convention. Proposed resampling seed: **20260917**, with the actual random-generator implementation/version and resample-index replay record pinned by the later software. The same resample-index manifest is used for linked P1 component summaries on the same block set.

For this fixed wording suite, label the result **`prompt_resampling_sensitivity`**. It is not a confidence interval for all prompts, tasks, users, or future model versions. It conditions on the collected within-block outputs and does not quantify all stochastic generation uncertainty. Unknown cross-block shared history or other dependence can make even this sensitivity calculation inappropriate; preserve the limitation rather than switching estimators silently.

If an endpoint is undefined or ineligible for any intended block, the full registered claim is restricted. A separately labeled descriptive summary of all available blocks may be provided with the missing block list and reasons. It cannot replace the intended six-block target or use different block sets for the two components of P1. With fewer than two compatible blocks, the resampling interval is unavailable under the approved metric contract.

### 10.3 Prespecified coverage and quality bands

**[Engineering proposal]** The following thresholds are design safeguards selected here, not values supplied by SD or SI and not proofs that the missing evidence is harmless. Apply them to every participating cell of a claimed main comparison, using exact counts and fractions. Crossing a gate limits interpretation; it does not erase the cell or overwrite a calculable result.

| Gate | Proposed main-study requirement |
|---|---|
| Planned group completion | All four registered groups have five identifiable candidate positions for either primary matched P1 or P5 comparison; P5 additionally uses the fixed distinct-20 prefix. |
| Accepted classification coverage | At least 0.90 of selected realizations in `classified_all`. |
| Decisive validity coverage | At least 0.95 of selected realizations have accepted valid/invalid assessments. |
| Valid-output structural coverage | At least 0.90 of accepted valid realizations have accepted class assignments, when the valid denominator exists. |
| Text coverage for pair contrasts | At least 0.95 of the applicable classified population has usable original proxy text, with at least two eligible realizations. |
| P5 quality floor | Accepted `valid_fraction_selected` is at least 0.80 in each compared cell. |
| P5 matched-quality band | Absolute C-versus-comparator difference in `valid_fraction_selected` is at most 0.10 in every paired block. |
| Evidence | Applicable membership, independent core/audit, schema, exposure, and integrity requirements are satisfied for the claimed scope. |
| Comparison frame | Domain, resolution, class meanings, rubric, extraction, material role, and recorded controls remain compatible. |

The P5 band operationalizes a limited quality match based on the accepted validity rubric. It does not establish exact quality equivalence or matching of every program property. C may have higher breadth and much higher validity while exceeding the band; report both observations and restrict the matched-quality claim instead of discarding C's valid outputs.

For P1, display the quality band and floor as diagnostics, with any B-A quality loss explicit. SD's P1 permits a quality decrease at high temperature. Such a decrease must be discussed alongside all-classified and valid-only results; the experiment must not hide the failure or relabel it as measured creativity. A clean quality-comparable P1 interpretation additionally requires the same floor/band. The raw P1 operands remain reportable when calculable even if that additional description is unavailable.

A baseline surface distance of at least **0.95** triggers a prespecified `surface_proxy_near_ceiling` diagnostic. A distinct-k count reaching all eight currently registered families triggers a registry-ceiling note, not a claim of complete model support. These are interpretation flags; they never trigger post-result proxy replacement, new classes, changed temperatures, extra sampling, or favorable subset selection.

Even above the coverage thresholds, unknown/unresolved mechanisms can affect the observed distribution. Reports identify them and avoid treating the accepted subset as the unrestricted generative distribution. The thresholds are not a missing-data correction method.

### 10.4 Outcomes and multiplicity boundary

**[Source-derived: SD §9.7]** The predictions must admit contrary evidence. P1 concerns differential change at surface and structural levels; P5 concerns non-equivalent output breadth at matched quality. Software correctness cannot depend on their direction.

**[Engineering proposal]** Register two question families in advance: P1's joint examination of positive surface gain and the surface-minus-structural gain contrast, and P5's two separate C-A/C-B primary distinct-20 contrasts. k=5/k=10, thresholded support, individual class plots/tables, and other companion diagnostics are secondary. They cannot be promoted to primary endpoints after observing the results.

For P1, a positive contrast without positive surface gain does not satisfy the proposed pattern. For P5, C improving over A but not over B does not establish the full registered two-comparator pattern. A negative, null, mixed, saturated, quality-confounded, or inadequately measured result remains reportable.

This small fixed-suite study does not claim familywise significance from multiple nominal intervals. All registered primary contrasts and their sensitivity ranges must be shown together; no minimum-p selection or favorable endpoint selection is permitted. Step 7 will map these registered operands, gates, and dependence limits to explicit supporting/contrary/inconclusive **fixed-suite operational** decisions and tests. No claim of statistical confirmation across a prompt population is authorized by this document.

Changing those endpoints, their priority, the quality bands, or collection design at Step 7 requires an explicit proposal rather than a silent edit to this contract. Step 7 may complete the decision/test mapping without changing the established metric formulas.

### 10.5 Claims withheld by design

**[Engineering proposal]** This hero cannot establish total model structural capacity, latent extinction, representational recovery, a universal convergence frontier, collapse from recursive training, safety across domains, or an overall intelligence/creativity ranking. It has no training transitions, external-recovery experiment, model-general sample, or universal structural ontology.

A C output from a previously unobserved class documents appearance under that prompt condition. It does not by itself establish a meaningful-probability expressible-support threshold or creation of new representation. Comparisons of A/B/C source lineages concern evaluation integrity; using one generator for the three paired conditions is part of the within-deployment design, not evidence that the independent reference/validation requirements have been met.

## 11. First fixture and expected report structure

### 11.1 Non-executable fixture manifest

**[Engineering proposal]** The first milestone should implement a small **fixture-only** path under this task/schema, followed by the existing negative/conformance checks. The table below stipulates twenty candidate records in four groups; it is not a model collection or an assertion that valid reference programs already exist. Future fixture payloads and their labels/validity are explicitly synthetic/stipulated and must retain that origin.

For this calculation fixture only, all twenty assignments and validity records are stipulated as accepted under `fixture_only`. Family shorthand in the table maps to the full `SORT-...` IDs. There is one prompt block and one fixture condition, so no multi-prompt inference or empirical A/B/C result follows.

| Group | Position 1 | Position 2 | Position 3 | Position 4 | Position 5 |
|---|---|---|---|---|---|
| F-G1 | MERGE | PIVOT | MERGE | HEAP | COUNT |
| F-G2 | MERGE | PIVOT | MERGE | HEAP | RADIX |
| F-G3 | MERGE | PIVOT | MERGE | PIVOT | COUNT |
| F-G4 | MERGE | PIVOT | MERGE | PIVOT | HEAP |

Expected full-cell counts are `(8, 6, 3, 2, 1)` for those five occupied classes. The other registered classes have zero observed fixture count and are not deleted from the registry.

| Fixture quantity | Expected value / condition |
|---|---|
| Selected and accepted population sizes | 20 in each approved view, under the stipulation above. |
| Occurrence support | 5 classes. |
| Thresholded support at 0.10 | 4 classes; the count-two class meets the exact threshold. |
| Distinct-5, distinct-10, distinct-20 | 4, 5, 5 respectively, using the fixed group/position prefix. |
| SCI | 0.285. |
| Structural entropy | Approximately 1.392321254757429 nats. |
| Shannon effective count | Approximately 4.024180367609189. |
| Simpson effective count | `200/57`, approximately 3.508771929824561. |
| Inter-prompt uncertainty | Unavailable for this single-block fixture. |
| Surface diagnostic | Requires the actual future fixture text; no value is invented here. |
| Empirical interpretation | None; this is a prescribed arithmetic fixture. |

Separate named variants must exercise an invalid-but-classifiable sample, unresolved hybrid, provisional label, missing decisive evidence, missing candidate position, and evidence correction. Each variant has its own pinned manifest; never mutate the fixture to make one test pass while leaving its declared expected values unchanged. Step 7 supplies complete test links and any additional expected calculations.

### 11.2 Required report order

**[Engineering proposal]** The first readable report should present:

1. The task, material role, actual evidence status, pinned versions, and permitted claim scope.
2. Planned attempts/positions versus actual responses/realizations, including completion, extraction, exclusions, and grouping.
3. Separate classification and validity accounting, with unresolved and withheld evidence visible.
4. Per-cell class counts and the core metrics in both approved views, with denominators.
5. The prespecified prefix/accumulation table and protected-reference coverage.
6. For a supplied A/B/C study, both P1 components and contrast, both P5 contrasts, quality/coverage gates, and fixed-suite uncertainty limitations.
7. Class-specific/within-class surface diagnostics and any ceiling or composition warnings.
8. Integrity, reference/audit coverage, exposure, correction status, unavailable/deferred quantities, and release restrictions.

The corresponding JSON output retains the semantic fields already specified in the preceding contracts. A missing independent evidence gate must be prominent before the results can be mistaken for independently validated observations. No rendered chart or hosted dashboard is required; tables are sufficient for the first milestone.

### 11.3 Additional study-specific semantic records

**[Engineering proposal]** Reuse existing task, protocol, grouping, evidence, and result fields. The following content can be represented through their linked manifests without adding another required Phase 0 document:

| Record content | Purpose |
|---|---|
| Planned call slot and five-position inventory | Distinguish planned resources from actual realized samples and preserve missing positions. |
| Group-format/extraction outcome | Record duplicate/absent headings, extras, missing fences, and exact text-region associations. |
| Domain-suite identity and coverage | Identify all registered input tests, observations, counterexamples, harness failures, and unperformed checks. |
| Mechanism-signature evidence | Link defining operations/branches, witness observations, descriptor version, and reviewer decision. |
| Core/reference coverage | Map the 32 artifact roles and eight descriptors to actual evidence or explicit missing material. |
| Audit-position and targeted-selection records | Preserve preselected positions, missing selections, added reviews, and distinct-artifact counts. |
| Study comparison gates | Link quality, coverage, group completion, matched-control status, and reasons restricting a named comparison. |

These records are evidence and selection metadata. They do not introduce a universal independence score, new latent-support estimator, or automatic classifier.

## 12. External validation safety and execution boundary

### 12.1 Offline v0.1 behavior

**[Owner-approved decision: PROJECT_SCOPE.md §§4-5]** The first milestone and v0.1 do not execute generated programs. Candidate source, imported traces, proofs, logs, and evidence attachments are passive inputs. Their presence cannot trigger Python evaluation, shell commands, macros, model calls, remote retrieval, or automatic dependency installation.

**[Engineering proposal]** Any runtime evidence used for the empirical hero comes from a separately authorized external validation process. This document specifies the required isolation and recorded envelope before such evidence can be accepted; it neither implements that process nor authorizes its operation.

### 12.2 Proposed external execution profile

**[Engineering proposal]** A future validator must use an independently reviewed isolation boundary suitable for hostile code, such as a hardened VM/microVM or equivalently justified execution service. A Python subprocess, restricted globals, source blacklist, or an ordinary container by itself is not evidence that the required boundary has been achieved.

| Area | Required envelope and record |
|---|---|
| Host separation | No execution directly in the analyst's host environment; no host home directory, project tree, device access, credentials, or secrets available to the candidate. |
| Network | Denied inbound/outbound access, including local metadata endpoints; no automatic package/network access. |
| Filesystem | Candidate has no discretionary file access; trusted harness has read-only candidate/input material and bounded ephemeral working space. No persistent state between candidate artifacts. |
| Processes and privilege | No candidate process spawning, privilege escalation, host interfaces, or uncontrolled threads. Concurrency policy and enforcement must be documented. |
| Memory | Proposed 512 MiB maximum guest/candidate working envelope, with trusted-oracle separation recorded. |
| Time | Proposed per-artifact functional-suite envelope: 30 CPU seconds and 60 elapsed seconds; separate mechanism traces have a separately declared envelope. |
| Output/storage | Candidate diagnostic output capped at 64 KiB; trusted result protocol permits at most the declared 256 returned integer values per test; bounded ephemeral storage, proposed 16 MiB. |
| Interpreter | Pinned Python 3 implementation/patch version and image identity; no assertion that a named version is current or secure merely from its name. |
| Isolation reset | Fresh candidate state between independent tests, or an independently reviewed equivalent reset preserving evidence; state-sharing/harness behavior is recorded. |
| Evidence | Original source hash, input/test ID, environment/configuration identity, trusted observations, termination status, limits, and validator provenance. |

These numerical limits are proposed safety budgets, not validated performance findings. Before main collection claims rely on them, the reference set must demonstrate that the envelope accommodates all eight correct reference families on the full suite. A timeout caused by an inadequate envelope must not selectively remove a slower family. Revise and freeze the profile before the affected main validation, or retain undetermined validity and its claim restriction. No profiling or candidate execution occurs in Phase 0.

Trusted validation code and its oracle must be outside the candidate's control. Isolating code execution does not establish that the oracle is scientifically correct; verifying the oracle does not establish containment. Both evidence paths are required for the respective claims.

### 12.3 Failure dispositions

**[Engineering proposal]** Record malformed source, prohibited capability attempts, parse failures, exceptions, output protocol failures, timeout/memory limits, sandbox/harness failures, and missing evidence separately. A demonstrated task violation may establish invalidity. A failed containment check stops execution and the affected empirical validation, while the passive offline fixture/analysis path remains available after its own authorization.

Never silently repair or execute a repaired artifact under the original sample ID. Diagnostic repairs, if later authorized, have new artifact identities and cannot replace the original generation in the registered primary analysis.

## 13. Evaluation openness and evidence-dependent release

**[Engineering proposal]** Apply the approved four-component contract within this one sorting family:

| Component | Hero-specific contents and boundary |
|---|---|
| Stable Core | Pinned task/schema/rubric, the 32-artifact reference design, actual validated reference material when supplied, and the functional/witness manifests. |
| Rotating Structural Frontier | Eligible unregistered mechanisms, hybrids, new differentiating cases, and failed class boundaries. Intake retains evidence without immediate count inflation. |
| External Incident Stream | Independently supplied or explicitly non-independent reports of misclassification, oracle errors, hidden branch behavior, format/cost confounds, or unsafe validation. |
| Versioned Tail Registry | Preservation quotas from Section 6.3, known-zero observations, cell-specific low-count audit flags, and successor dispositions after schema changes. |

No live service or monitoring task is created. A prepared ledger or empty intake does not prove ongoing external correction. An AI-assisted source or fixture keeps its derivation after human editing. Different model labels do not certify reference independence.

At delivery, all actual empirical material remains unprovided: no 32-program core, independent annotation pair, 72-call output collection, validated execution environment, or sampled human audit has been completed by this phase. Their absence is an evidence gap under UD-006. Approving the design settles the applicable rules; it cannot establish their fulfillment.

An empirical release must identify whether it supports fixture demonstration, qualified imported-label description, validated structural measurement, or a named P1/P5 comparison. A narrower authorized report may preserve useful calculations with prominent limitations. No self-issued approval of a source-conformant or statistically general result is permitted.

## 14. Step 6 conformance checks and handoff

### 14.1 Future checks to map in Step 7

**[Engineering proposal]** These are non-executable requirements. They supplement, rather than replace, the existing structural, metric, and integrity checks.

| ID | Required future check |
|---|---|
| HB-T01 | Domain endpoints, empty input, duplicates, high keys, and new-list/input-preservation requirements have unambiguous test observations. |
| HB-T02 | The domain and operation rules admit each of the eight reference mechanisms; no hidden stability, in-place, comparison-only, or complexity condition excludes one. |
| HB-T03 | ADJ/INS, SEL/HEAP, MERGE/PIVOT, and COUNT/RADIX distinctions use the declared organizing relations rather than names or final outputs. |
| HB-T04 | All descriptor-pair overlaps are reviewed; unresolved schema contradictions restrict affected assignments rather than invoking rule order. |
| HB-T05 | Permitted helpers/base cases and general hybrids follow their preregistered boundaries; counting inside digit refinement is not another sample. |
| HB-T06 | Invalid but recognizable mechanisms and defects destroying membership receive different evidence-backed dispositions. |
| HB-T07 | An eligible unregistered solution can be valid while structurally unresolved; it remains in coverage and frontier records. |
| HB-T08 | The functional manifest contains the specified 8995 cases with stable IDs, valid ranges, and preserved duplicate-case identity. Passing remains a bounded claim. |
| HB-T09 | The core records show actual material/annotation coverage; 32 planned roles are not reported as 32 validated programs. |
| HB-T10 | The audit selects the frozen candidate positions, preserves missing selections and targeted reasons, and never inflates generator sample counts. |
| HB-T11 | A/B sent prompts match exactly for a block; C differs by the registered clause; common constraints remain identical. |
| HB-T12 | All conditions use five-position coordinated groups with recorded dependencies; row expansion cannot create independent calls or blocks. |
| HB-T13 | Collection has 72 main call slots, 360 requested positions, and the stated cap accounting; optional pilot material stays separate. |
| HB-T14 | Failed calls, missing candidates, partial responses, extras, and ambiguous headings follow the extraction and no-replacement rules. |
| HB-T15 | k=5/10/20 selects the intended complete first groups; a missing early position cannot be backfilled from a later group. |
| HB-T16 | Fixture counts, thresholds, prefixes, entropy, SCI, and both effective counts match the Section 11 stipulations. |
| HB-T17 | Unknown model controls or cap semantics restrict only supported comparisons; no hidden default creates a temperature or equal-cost claim. |
| HB-T18 | P1 operands use the same eligible set and blocks; positive contrast with negative surface gain cannot satisfy the registered pattern. |
| HB-T19 | P5 reports both C-A and C-B at distinct-20 with the quality/coverage gates; favorable secondary k cannot replace the primary endpoint. |
| HB-T20 | Fixed-suite resampling remains sensitivity analysis; incomplete or dependent blocks cannot yield an unqualified population interval. |
| HB-T21 | A source, class, rubric, or label correction identifies all affected conditions and results without turning old samples into new observations. |
| HB-T22 | Untrusted program/evidence content remains passive in v0.1; imported runtime evidence retains separate containment and scientific-validation requirements. |
| HB-T23 | An adverse, null, ceiling-limited, or unmeasured result remains reportable; test success never requires the model to favor P1/P5. |
| HB-T24 | Specification approval does not authorize collection, spending, execution, implementation, independent-evidence acceptance, or publication. |

### 14.2 Review requested and next step

**[Engineering proposal]** Owner review of this Step 6 delivery covers the bounded sorting task, eight proposed descriptors, concrete reference/validation design, matched five-candidate A/B/C groups, six fixed prompt blocks, four calls per block-condition, fixed k grid, resource/extraction rules, quality/coverage bands, and external-validation boundary.

This is the hero component of UD-004 and the concrete study-design component of UD-005. UD-005 retains the Step 7 theory/test and interpretation mapping. UD-006's protocol is approved through OA-005; its actual-evidence component remains open. UD-007 remains deferred.

After approval and an instruction to proceed, **Step 7** may create `THEORY_TO_CODE_TRACEABILITY.md` and `VALIDATION_AND_FALSIFICATION.md`, and update the register. It maps the approved contracts and HB-T01 through HB-T24 to planned components, test specifications, report fields, and bounded interpretations. The integrated audit remains Step 8; final Phase 0 approval and explicit implementation authorization remain later gates.

No other toolkit completion is required. This delivery stops at Step 6.
