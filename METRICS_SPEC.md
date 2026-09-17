# METRICS_SPEC

## StructDet-Bench: Estimators, Denominators, Diagnostics, and Permitted Conclusions

| Field | Value |
|---|---|
| Document version | 0.2 |
| Date | 2026-09-17 |
| Phase / step | Phase 0 / Step 8; corrective revision of the Step 4 contract |
| Status | AUDIT-CORRECTED PROPOSAL; Step 8 owner acceptance pending |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Approved input contracts | `PROJECT_SCOPE.md`, `DEFINITIONS_AND_UNITS.md`, and `STRUCTURAL_CLASS_CONTRACT.md`, each version 0.1 |
| Approval evidence | Version 0.1 adopted in OA-004; OA-007 authorizes finding-limited Step 8 corrections, without approving them in advance |
| Decision register | `UNRESOLVED_DECISIONS.md`, version 0.7, audit finding AF-001 |
| Decision authority | Theory Owner |
| Authorized revision | AF-001 in §§4.4 and 7, with the corresponding clarification in the validation specification |
| Implementation / repository / experiment authorization | None |

## 1. Authority and source fidelity

**[Step 8 audit revision: AF-001]** Version 0.1 was adopted through OA-004. Version 0.2 distinguishes a local assignment exclusion from a failure of the shared analysis frame, aligning §§4.4 and 7 with the already approved structural-class contract and HF-04. It changes no formula, denominator definition, evidence policy, threshold, or release scope. The original Step 4 submission and handoff language below is retained as delivery history; the current approval state and next gate are recorded in `UNRESOLVED_DECISIONS.md` v0.7. The correction awaits Step 8 owner acceptance.

**[Owner-approved decision]** The owner approved the delivered general structural-class contract and instructed continuation to Step 4. OA-003 records that authorization. Previously approved files remain unchanged. Their original proposed-status headers describe their earlier delivery; the register records the subsequent approvals.

**[Engineering proposal]** This document owns metric estimators, calculation populations, numerical conventions, diagnostic definitions, uncertainty procedures, result fields, and permitted interpretations. Its new procedures require owner approval. It does not select a hero taxonomy, collect observations, run a benchmark, implement software, or approve an empirical claim.

The labels **[Source-derived]**, **[Engineering proposal]**, and **[Owner-approved decision]** retain the meanings established in the Step 2 baseline. A label governs its section until another basis is stated. An engineering derivation is identified as such even when it uses quantities defined by the sources.

| Source ID | Supplied edition and relevant locations |
|---|---|
| SD | *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness*. August 2026, 27 pages. §§3.2-3.7, 4-5, 6.5-6.6, 9.1-9.7, 11-12. |
| SI | *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*. August 2026, version 1.0, 31 pages. §§3-6, 8-9, 12. |

Source identities and SHA-256 fingerprints remain those in the plan. References to other publications inside these PDFs are not independently verified by this step.

**[Source-derived]** The papers define structural entropy, concentration, support, effective class quantities, and a benchmark program. They require separate validity reporting, protocol-bounded support claims, uncertainty disclosure, and evidence against evaluation closure. [SD §§3.7, 5, 6.5, 9; SI §§3.3, 4, 8-9]

**[Engineering proposal]** The papers do not prescribe the particular lexical tokenizer, fixed-prefix distinct-k selection, paired-distance contrast, percentile-bootstrap implementation, or result-state vocabulary below. Those are explicit software and experimental choices submitted here. They must not be attributed to either paper as an already established estimator.

## 2. Capability and delivery matrix

**[Owner-approved decision: OA-002]** The first milestone is an offline fixture-based measurement path. v0.1 adds the same-task A/B/C comparison workflow using precollected outputs. Live generation, automatic structural classification, generated-code execution, and Layer B experiments remain outside this release.

**[Engineering proposal]** The following dispositions complete the metric boundary without expanding it into another task family or execution service.

| Family / public field | Delivery disposition | Required interpretation |
|---|---|---|
| Population, classification, validity, exclusion, and grouping accounting | First milestone, mandatory | Describes the actual inventory and accepted subsets. |
| `observed_support_size` | First milestone | Occurrence count in an identified classified population. |
| `observed_support_size_thresholded` | First milestone, when requested | Count passing a declared empirical-frequency threshold. |
| `structural_entropy_nats` | First milestone | Plug-in entropy of the conditional empirical class distribution. |
| `structural_concentration_index` | First milestone | Plug-in sum of squared empirical class frequencies. |
| `effective_support_shannon` | First milestone | Exponential of entropy in nats. |
| `effective_support_simpson` | First milestone | Reciprocal of the concentration index. |
| `structural_distinct_k` and a prespecified prefix table | First milestone | Observed accepted classes in a fixed k-realization prefix; coverage accompanies every count. |
| `surface_lexical_trigram_distance` | v0.1 diagnostic | Average surface-token-trigram Jaccard distance over explicitly identified realization pairs. |
| `within_class_realization_diversity_proxy` | v0.1 diagnostic | The same surface distance restricted to pairs sharing an accepted class. |
| `structural_pair_non_equivalence` | v0.1 comparison diagnostic | Fraction of distinct observed pairs with different accepted classes; separate from SCI. |
| Per-block condition differences and paired prompt summaries | v0.1 | Descriptive or evidence-qualified comparisons with actual resource and grouping records. |
| Paired prompt-block resampling intervals | v0.1, evidence-dependent | Sampling interval or fixed-suite resampling sensitivity, with the distinction declared. |
| `gini_simpson_diversity` | Catalog / later Layer B output | `1-SCI` remains defined; no separate first-release headline or additional estimator is selected. |
| Expressible support, intervention union, frontier, convergence provenance, structural transmission | Deferred | Prerequisites in Section 13; no fabricated values. |
| Recursive retention, SHL, ERR, latent diagnostics, soft classification | Deferred | Preserve the source distinctions and approved scope. |

No overall intelligence, collapse, integrity, or creativity score is introduced. No averaging across unrelated tasks or resolutions produces a default model score.

## 3. Common result contract

### 3.1 Result identity and evidence

**[Engineering proposal]** Every scalar or table result carries, directly or through immutable references:

| Field group | Required content |
|---|---|
| Metric identity | `metric_name`, `metric_definition_version`, unit, estimator or selection rule. |
| Measurement frame | Task, horizon, resolution, structural-schema versions, and applicable registry version. |
| Generation identity | Model/checkpoint knowledge states, condition, actual protocol, prompt block, collection identity. |
| Analysis identity | `run_id`, `analysis_cell_id`, `analysis_population`, selected sample IDs or their immutable manifest. |
| Evidence | Assignment-policy identity, pinned assignment revisions, validity rubric/evidence policy, evidence and lineage references. |
| Denominator | Selected inventory count, accepted population size, class counts, and any diagnostic-specific subset or pair count. |
| Dependencies | Group identities, shared-call/history dependencies, sample order, and applicable budget records. |
| Calculation convention | Log base, threshold, k, text-proxy version, numerical policy, aggregation or uncertainty configuration as applicable. |
| Interpretation | `result_status`, reason when not numeric, `evidence_status`, `permitted_claim_scope`, and separate uncertainty status. |

A numeric value can be exactly calculated from imported labels while the empirical interpretation remains restricted. An `available` result does not certify an independent reference, correct ontology, or complete model capacity.

### 3.2 Result states

**[Engineering proposal]** Keep calculation status distinct from metadata knowledge states and from assignment/review states.

| `result_status` | Meaning | Numeric `value` |
|---|---|---|
| `available` | The requested quantity is defined and calculable for the identified inputs. | A finite number, integer, or defined structured result. |
| `undefined` | Known inputs produce no mathematical value for this estimand, such as an empty distribution denominator. | Null. |
| `unavailable` | Missing evidence, incompatible data, or a computation limit prevents the requested calculation or inference. | Null. |
| `not_requested` | An optional calculation has not been selected, for example thresholded support without a threshold. | Null. |
| `deferred` | The capability belongs to the catalog and is outside the approved implementation slice. | Null. |

Undefined and unavailable results have a reason and retain known counts. Examples include `empty_classified_population`, `insufficient_pairs`, `missing_sample_order`, `incompatible_schema`, `insufficient_prefix_length`, `missing_text`, `unsupported_dependence`, and `numerical_check_failed`.

Input-contract violations are validation failures. They block affected results with an explicit reason; they do not become scientific zeroes. A nonempty input containing conflicting sample identities must not be relabeled as an empty dataset.

Use null rather than NaN, infinity, a negative sentinel, or a fabricated zero. A zero-valued count remains allowed when its counted set is known to be empty. Sections 5-7 state the particular empty-set rules.

An uncertainty record separately states `available`, `not_estimated`, or `unavailable`, with its method and scope. A point estimate may remain available without a confidence interval.

## 4. Inventories, populations, and denominators

### 4.1 Establish inventories before calculating classes

**[Engineering proposal]** Retain three distinct accounting layers:

1. **Input and attempt inventory.** Imported rows, malformed records, calls/attempts, failures, retries, returned responses, and extraction outcomes, to the extent actually recorded.
2. **Realization inventory for a cell.** Unique identifiable realizations belonging to that cell before the declared analysis selection.
3. **Selected realization inventory `U`.** Realizations admitted by the prespecified selection/extraction rules, before classification or validity conditioning.

Let `N_inventory` be the second count and `N_selected=|U|` the third. Report the selection exclusions separately. All generated records must remain traceable; outputs without enough metadata to enter a cell stay in an unallocated inventory, rather than disappearing from the run.

Missing attempt history is recorded as unknown or unavailable. It cannot be reconstructed by assuming that each returned realization required exactly one successful call. A failed call without a realization remains a call failure; it does not acquire an invented output or class.

Repeated bytes with different genuine sample IDs remain repeated observations. A copied record with the same sample identity is not another observation. Duplicated or conflicting IDs require explicit input resolution; the metric layer does not silently choose one. Assignment revisions never increase the sample count.

### 4.2 The two approved class populations

**[Owner-approved decision: OA-002; OA-003]** Use the population meanings and evidence policies already approved:

\[
A_{\mathrm{all}}=\{i\in U: \text{a unique hard assignment is accepted under the selected policy}\},
\]

\[
A_{\mathrm{valid}}=\{i\in A_{\mathrm{all}}: \text{an accepted assessment is valid under the named rubric}\}.
\]

Their public names remain `classified_all` and `classified_valid`. `fixture_only` and `adjudicated_import` remain separate evidence policies. Provisional labels and unresolved contradictions cannot enter either standard population.

**[Engineering proposal]** For one chosen population `A`, define:

\[
n_A=|A|,\qquad c_z=|\{i\in A:Z_i=z\}|,\qquad
\widehat p_A(z)=c_z/n_A\quad(n_A>0).
\]

Counts must satisfy `sum_z c_z = n_A`. They are unweighted nonnegative integer counts. First-release metrics have no undocumented sample weighting, class weighting, fractional assignments, or pseudo-counts. A weighted future analysis requires its own contract.

A provisional or unresolved candidate label contributes no structural mass. A registered class with no accepted observations has count zero. Adding a reference-registry entry does not alter the empirical distribution.

### 4.3 Mandatory accounting alongside each cell

**[Engineering proposal]** Store counts as authoritative integers; derive displayed rates from the specified denominators.

| Summary field | Numerator / denominator or meaning | Empty-denominator rule |
|---|---|---|
| `selected_realization_count` | `N_selected` | Known empty inventory gives 0. |
| `classified_all_count` | `n_all` | Known empty accepted set gives 0. |
| `classified_valid_count` | `n_valid` | Known empty accepted-valid set gives 0. |
| `classification_coverage` | `n_all / N_selected` | Undefined when `N_selected=0`. |
| `valid_fraction_selected` | Number of selected realizations with an accepted `valid` assessment, divided by `N_selected` | Undefined when `N_selected=0`. |
| `decisive_validity_coverage` | Number of selected realizations with accepted `valid` or `invalid` assessments, divided by `N_selected` | Undefined when `N_selected=0`. |
| `classified_valid_coverage` | `n_valid` divided by the selected count with accepted `valid` assessments | Undefined when no selected validity assessment is accepted as valid. |
| `classified_valid_fraction` | `n_valid / n_all` | Undefined when `n_all=0`. |
| `assignment_status_counts` | `assigned`, `unresolved`, `unclassified`, plus explicitly missing/unavailable status records in the accounting layer | Missing records are not recoded as an observed classification outcome. |
| `assignment_acceptance_counts` | Accepted and withheld assignments, with reasons and review-state counts | Withholding reasons may overlap; state whether a tally is multi-reason. |
| `validity_status_counts` | Accepted `valid`, `invalid`, `undetermined`, `not_assessed`, plus missing/withheld assessment evidence | A missing assessment is not automatically `invalid` or `not_assessed`. |
| `completion_summary`, `selection_summary`, `attempt_summary` | Their own mutually exclusive inventories where known | Unknown histories remain nonnumeric, with reasons. |
| `grouping_summary` | Number, membership, size, order, and known dependencies of generation groups | Unknown independence is never converted to independent draws. |

`valid_fraction_selected` reports the fraction established as valid in the selected inventory. When assessments are incomplete, it does not estimate the unassessed outputs' validity. `classified_valid_fraction` reports an observed conditional fraction, not success among all calls.

Counts on different axes overlap. An invalid realization can be structurally classified. Adding invalid, unresolved, and failed-call counts as though they partition one population is prohibited.

Class frequencies always display both the conditional denominator `n_A` and its coverage relative to `N_selected`. Changes in classification acceptance or validity can change a conditional distribution without demonstrating that the generator changed its unconditional distribution.

### 4.4 Eligibility and computation gates

**[Audit correction: AF-001; implementing SC §§6.4-6.5 and 8]** When the shared evaluation frame and selected inventory remain valid, missing essential membership evidence or unresolved conflicting labels withhold the affected assignment only. Rebuild `classified_all` and `classified_valid` from the remaining accepted records, preserve `N_selected` and all withholding reasons, and report the resulting conditional metrics and coverage. No replacement sample, default class, or inference of output invalidity is introduced. If no accepted assignments remain, the known empty-set and undefined-distribution rules in Section 7 apply.

An unsupported or incompatible shared schema, an ambiguous population identity, or a schema-level defect that prevents formation of a valid accepted subset blocks the affected distribution. Incompatible evidence policies cannot be pooled; separately identified, internally consistent populations may still be reported. Retain supported inventories, subsets, and unrelated cells, and state the precise scope of the failure. A local exclusion must not be silently promoted to a cell-wide failure, and a defective shared frame must not be disguised as a valid empty population.

Missing a later empirical-independence requirement may restrict the claim without invalidating the arithmetic of an appropriately labeled imported-label summary. The adopted evaluation-integrity contract owns that evidence gate.

No automatic completion, output repair, reclassification, or remote retrieval occurs in the metric path. The first release analyzes the recorded artifact and imported evidence.

## 5. Core distribution metrics

### 5.1 Shared conventions and interpretation

**[Owner-approved decision: OA-002, UD-002]** Natural logarithms, nats, separate effective-count names, and occurrence/thresholded support views are retained.

**[Engineering proposal]** Use the unsmoothed empirical distribution from Section 4.2. These calculations are exact functionals of the supplied count table, subject to floating-point arithmetic. They are finite-sample plug-in summaries of a model distribution, rather than certified measurements of its full support. No unseen-class estimator or bias correction is selected for v0.1.

Changing sampling budgets, assignment coverage, or generation-group composition can change the summaries. Sampling uncertainty is separate from arithmetic precision and from uncertainty in class validity. Individual-cell distribution metrics receive no automatic population confidence interval in the first milestone. Section 11 governs the narrower v0.1 comparison interval.

Let `s=|{z:c_z>0}|` for a nonempty population. A bijective renaming of class IDs and reordering of input storage must preserve all metrics in this section.

### 5.2 Occurrence-based observed support

**[Source-derived: SI §§3.3, 8.1]** Finite observed support records classes that appear in the experiment.

**[Engineering proposal]**

\[
\texttt{observed\_support\_size}(A)=\sum_z \mathbf 1[c_z>0].
\]

| Property | Contract |
|---|---|
| Population | One declared `A`; accepted assignments only. |
| Unit | Integer count of classes. |
| Range | `0 <= s <= n_A`; for `n_A>0`, `s>=1`. |
| Empty population | Available count 0 with `population_size=0` and explicit empty-population qualifier. Distributional metrics remain undefined. |
| Uncertainty | Records sampled occurrence. No inference that all other classes have zero model probability. |
| Required context | Sample count, class counts, protocol, coverage, evidence policy, schema, and available prefix accumulation table. |
| Prohibited inference | Total model capacity, representational extinction, or proof that the registered ontology is complete. |

A report displaying zero must say that no accepted classes were observed in the specified population. It must not say that the model has no structures.

### 5.3 Empirical-frequency-thresholded support

**[Source-derived: SD §5.1]** SD's observed-support definition uses an empirical-frequency threshold. It remains distinct from the occurrence convention.

**[Engineering proposal]** For requested `min_empirical_frequency = tau_e`, with `0 < tau_e <= 1`:

\[
\texttt{observed\_support\_size\_thresholded}(A,\tau_e)
=\sum_z\mathbf 1[c_z>0\ \text{and}\ c_z/n_A\geq\tau_e].
\]

The denominator is the full chosen classified population. Removing classes below threshold and renormalizing the remainder before this calculation is prohibited. The threshold does not filter the entropy or SCI population.

Treat the declared finite-decimal threshold as an exact rational `a/b`, using its canonical decimal representation. Decide membership by `b*c_z >= a*n_A`; do not compare rounded displayed frequencies or use a floating-point epsilon to decide threshold inclusion. Exact equality is included. The original threshold and denominator remain in the result.

| Situation | Required result |
|---|---|
| Threshold omitted | `not_requested`, null value. |
| Threshold outside `(0,1]` or malformed | Input validation failure; affected result unavailable. |
| Requested threshold and `n_A=0` | `undefined`, null value; empirical frequencies have no denominator. |
| Nonempty population, no class meets threshold | Available integer 0. |
| Known zero-count registry class | Does not pass a positive threshold. |

This is an empirical-frequency rule. Passing it does not establish that the model's population generation probability exceeds the same number. `min_generation_probability` remains a different, deferred support-estimation parameter.

### 5.4 Structural entropy

**[Source-derived: SD §§3.7, 9.2; SI §§4, 8.2]** Entropy is calculated over structural classes.

**[Engineering proposal]**

\[
\widehat H_S(A)=-\sum_{z:c_z>0}\frac{c_z}{n_A}\ln\frac{c_z}{n_A}.
\]

Public field: `structural_entropy_nats`. Unit: nats. Use `0 ln 0 = 0` for explicitly recorded zero-count classes; this convention does not define a distribution when `n_A=0`.

For `n_A>0`, `0 <= H_hat_S <= ln(s)`. One occupied class gives zero. An empty classified population produces `undefined`, null value. A missing structural map produces `unavailable`, rather than zero entropy.

No term for provisional labels, uncertain candidate classes, or unobserved registry entries is added. This estimator does not calculate total output entropy or residual realization entropy. Low entropy cannot by itself establish truth, validity, utility, or the cause of convergence.

### 5.5 Structural Concentration Index

**[Source-derived: SD §9.2; SI §§5.3, 8.2]** SCI is the sum of squared class probabilities.

**[Engineering proposal]**

\[
\widehat{\mathrm{SCI}}(A)=\sum_z\widehat p_A(z)^2
=\frac{\sum_z c_z^2}{n_A^2}.
\]

Public field: `structural_concentration_index`. Unit: dimensionless. For a nonempty population, `1/s <= SCI <= 1`. One occupied class gives 1. Empty populations produce `undefined`, null value.

This plug-in value equals the probability of drawing matching classes when sampling twice independently **with replacement from the finite empirical population**. It includes the possibility of drawing the same recorded realization twice. It is not the observed fraction of matching pairs of distinct records; Section 9 gives that separate diagnostic.

No finite-sample correction is silently applied. A high SCI describes concentration in the chosen population and does not certify structural inbreeding or poor output quality.

### 5.6 Separate effective class quantities

**[Source-derived: SD §§3.7, 9.2; SI §§5.3, 8.2]** Preserve both source definitions:

\[
\texttt{effective\_support\_shannon}=\exp(\widehat H_S),
\qquad
\texttt{effective\_support\_simpson}=1/\widehat{\mathrm{SCI}}.
\]

**[Engineering proposal]** Both have unit `effective_classes`. They are real-valued distribution summaries, not integer counts of observed classes. Compute them from unrounded values from the same population and convention. Do not use a public field named only `N_eff`.

Both are undefined for an empty classified population. For a nonempty population they lie between 1 and `s`. Under the hard finite distribution, the consistency relation is:

\[
1\leq \texttt{effective\_support\_simpson}
\leq \texttt{effective\_support\_shannon}\leq s\leq n_A.
\]

This relation is a mathematical consistency check, not an additional empirical claim. Unequal class frequencies generally give different effective quantities, as Fixture MF-03 demonstrates. Agreement on a balanced fixture is insufficient to test their distinction.

## 6. Structural distinct-k and sample accumulation

### 6.1 Fixed-prefix selection

**[Source-derived: SD §9.2]** Structural distinct-k counts occupied structural classes among k generations. The supplied definition leaves the selection and grouping procedure to the benchmark design.

**[Engineering proposal]** The initial selection rule is `prespecified_prefix_without_replacement`. Define a stable ordered sequence of selected realizations in one cell **before looking at classification or validity**. The sequence comes from recorded collection/extraction order or a preregistered explicit list of sample IDs. Storage order and lexicographic ID order cannot silently substitute for an experimental ordering.

For positive integer `k`, let `U_k` be the first k realizations in this sequence. For view `A`, let `A_k=A intersect U_k`. Then:

\[
\texttt{structural\_distinct\_k}(A,U_k)
=\left|\{Z_i:i\in A_k\}\right|.
\]

The report contains the target `k`, selected realization IDs, `counted_samples=|A_k|`, view, classification/validity exclusions, dependency groups, and selection rule. It must retain the unit **classes among a k-realization prefix**, rather than classes among k successfully classified or valid outputs.

Do not replace an invalid, unresolved, or unclassified realization with a later successful one. Such replacement changes the budget and conditioning. An actual new sample request also changes the recorded resource use and cannot be performed by the analysis software.

### 6.2 Boundaries and grouping

**[Engineering proposal]**

| Situation | Required treatment |
|---|---|
| `k` omitted | `not_requested`. |
| `k` noninteger or `k<=0` | Invalid request; no automatic conversion. |
| Ordered selected inventory contains fewer than k realizations | `unavailable`, `insufficient_prefix_length`; do not silently shrink k. |
| Ordering cannot be established | `unavailable`, `missing_sample_order`; full-population metrics can remain available. |
| k-realization prefix exists, but no assignment enters the chosen view | Available count 0, with `counted_samples=0` and explicit qualification. |
| All k realizations enter the view | Count ranges from 1 to k and equals occurrence support on that prefix. |
| Prefix cuts a coordinated group | Descriptive count allowed with the partial-group flag; no matched-group inference unless the approved design permits that selection. |

A cell prefix can include multiple calls or coordinated sets. Group membership is preserved. Distinct-k does not establish k independent draws.

A k-realization budget is also distinct from k attempted calls or a token budget. Failed calls without realizations remain in attempt accounting. Comparisons requiring equal cost must use the Step 6 resource design; equal k alone does not establish it.

### 6.3 Accumulation table

**[Engineering proposal implementing SD §9.5]** Repeat the same fixed-prefix metric at a prespecified increasing list of k values. A tabular accumulation output is sufficient; no plotting service is required. Report both approved views and their accepted-sample counts at every prefix.

For a fixed pinned assignment version, the class count cannot decrease as an existing prefix is extended. A revised schema or corrected label creates a new curve and analysis identity. It does not rewrite the previous curve as though its classification had never changed.

Counts for registered rare classes can accompany the table when registry designations are supplied. A flat curve in a finite sequence cannot establish exhaustive support or latent extinction. A table point that cannot be evaluated remains unavailable; selecting a new k grid after inspecting results is identified as exploratory.

## 7. Numerical policy and empty-data behavior

**[Engineering proposal]** Counts, IDs, population membership, and threshold decisions are exact discrete objects. Floating-point tolerances apply only to numerical function evaluation and comparison, not to eligibility, thresholds, or class identity.

Use the following initial conformance convention for noninteger expected values: absolute tolerance `1e-12` plus relative tolerance `1e-10`. Preserve unrounded numeric values in the machine-readable report. Human-readable display rounding must not feed back into another estimator.

All core calculations must use nonnegative counts and finite normalized frequencies. Sum probabilities and entropy terms with a numerically stable summation procedure. Zero-count terms may be skipped. A result outside its mathematical range by more than the tolerance is withheld with `numerical_check_failed`. A boundary correction within tolerance, including conversion of signed negative zero to zero, must be recorded if it changes a stored numeric value. Never clamp a materially incorrect value merely to make a test pass.

| Known situation | Occurrence support | H / SCI / effective counts | Other required context |
|---|---|---|---|
| No selected realizations | 0 with empty-inventory qualifier | Undefined | Coverage ratios with zero denominator undefined. |
| Selected realizations exist, none accepted as classified | 0 with zero-classified qualifier | Undefined | Preserve all unresolved/withheld counts. |
| All accepted realizations invalid | `classified_all` may have positive support; `classified_valid` has 0 | All-view values may be defined; valid-view values undefined | Expose the invalidity and validity coverage. |
| One accepted class | 1 | H=0, SCI=1, both effective counts=1 | Sample count and evidence scope remain visible. |
| Missing model checkpoint but valid imported class records | Descriptive summary may be available | Same | Fixed-checkpoint causal claims remain restricted. |
| Local missing membership evidence or conflicting assignment; shared frame remains valid | Recompute on remaining accepted assignments; 0 when none remain | Recompute on remaining accepted assignments; undefined when none remain | Preserve selected inventory, withheld reasons, separately supported validity, and revised coverage. |
| Shared frame/schema defect prevents a valid accepted population from being identified | Affected metric unavailable | Affected metric unavailable | Retain supported inventories or separately valid populations. Do not report a defective frame as zero support. |

No software test should require a model's outputs to have low or high entropy. Tests validate adherence to formulas, evidence rules, and reporting boundaries.

## 8. Limited realization-level diagnostic

### 8.1 Selected observable and limits

**[Source-derived: SD §§3.7, 9.2; SI §4]** Variation within a structural class is distinct from structural variation. The papers name realization/implementation entropy and call for within-class variation measurement; they do not specify the proxy selected here.

**[Engineering proposal; UD-005 metric component]** v0.1 uses a **surface lexical-trigram Jaccard distance**, with one deterministic tokenizer and no model calls. Its purpose is a transparent, bounded surface diagnostic for supplied textual realizations. It neither assigns structural classes nor estimates exact `H(Y | Z,C,T,R)`.

The diagnostic is sensitive to word/identifier changes, punctuation, local order, comments, and included explanatory prose. Its tokenization ignores whitespace distinctions. Repeated identical trigrams contribute once to the set. It cannot detect every syntactic, semantic, or implementation difference. In code, ignored whitespace may itself be load-bearing; the independent structural contract must still handle that consequence. A zero proxy distance never establishes structural equivalence.

### 8.2 Text and tokenizer contract

**[Engineering proposal]** Use proxy identifier `surface_lexical_trigram_jaccard_v1`.

| Stage | Fixed rule |
|---|---|
| Text source | The registered textual realization or a text region specified by the task's extraction rule before outcome inspection. Use the same extraction rule across compared conditions. |
| Decoding | UTF-8 text or text already decoded with its encoding recorded. Decoding failure or inaccessible content yields missing proxy evidence. |
| Minimal normalization | Convert CRLF and standalone CR line endings to LF. Preserve case, identifiers, literals, punctuation, comments, and Unicode code points. No transliteration, stemming, renaming, comment removal, or semantic rewriting. |
| Lexical units | Each maximal contiguous run of Unicode letters, numbers, or underscore is one unit. Every other non-whitespace code point is a single unit. Whitespace separates units and is not itself a unit. |
| Unicode definition | Record the Unicode-property-table version. Letters use General Category `L*`; numbers use `N*`; whitespace uses the recorded `White_Space` property. Differing table versions require a compatibility check. |
| Boundary markers | Add one distinguished beginning marker and one distinguished ending marker. They are internal symbols that cannot collide with a text unit. |
| Trigram set | Take the set of all ordered triples of consecutive padded units. Empty token sequences are ineligible. One nonempty lexical unit already yields a defined trigram through the two boundary markers. |

This lexical tokenizer is a declared analysis convention, not the generator's tokenizer. Report its unit as a **surface lexical unit**. Do not label its unit counts as provider tokens. Original hashes remain separate from normalized text and proxy identities.

Let `G_i` be the nonempty trigram set of eligible realization i. Define:

\[
d_{\mathrm{surf}}(i,j)=1-\frac{|G_i\cap G_j|}{|G_i\cup G_j|}.
\]

It lies in `[0,1]`. Identical sets give 0; disjoint sets give 1. Boundary padding and set membership are fixed across all conditions. They cannot be tuned after examining P1/P5 results.

### 8.3 Common eligible subset and all-pair average

**[Engineering proposal]** For a chosen class population `A`, let `A_text` be its subset with usable proxy text. This is a diagnostic subset of an approved view, not a replacement definition of `classified_all` or `classified_valid`.

Report `m=|A_text|`, `proxy_text_coverage=m/n_A` when `n_A>0`, missing-text reasons, sample IDs, and the unordered pair count `P=m(m-1)/2`. Compute:

\[
\texttt{surface\_lexical\_trigram\_distance}
=\frac{1}{P}\sum_{i<j,\ i,j\in A_{\mathrm{text}}}d_{\mathrm{surf}}(i,j).
\]

With fewer than two eligible realizations, the pair average is undefined. Missing text cannot be converted to an empty string to create an artificial zero or maximum distance. Text unavailability does not by itself change otherwise supported core class counts.

The first release computes all eligible pairs for the declared small task slice. If a declared computation limit is exceeded, the diagnostic is unavailable with the limit recorded. It must not silently subsample pairs or truncate text. A future approximate estimator would need a separate approved method and field identity.

### 8.4 Within-class variation

**[Engineering proposal]** For each occupied class z, let `m_z` be its eligible-text count and `P_z=m_z(m_z-1)/2`. Where `P_z>0`, report:

\[
\overline d_{\mathrm{surf},z}
=\frac{1}{P_z}\sum_{i<j:Z_i=Z_j=z}d_{\mathrm{surf}}(i,j).
\]

The aggregate is explicitly pair-weighted:

\[
\texttt{within\_class\_realization\_diversity\_proxy}
=\frac{\sum_{z:P_z>0}P_z\overline d_{\mathrm{surf},z}}
       {\sum_z P_z}.
\]

Report the denominator, per-class pair counts, and per-class values. A singleton class has no within-class pair estimate. If all classes are singletons, the aggregate is undefined, not zero variation. Missing text and singleton classes stay visible.

The pair weighting can emphasize frequent classes. Cross-condition changes in this aggregate can reflect class-composition changes as well as within-class changes. Class-specific comparisons require the same class meaning and adequate paired evidence; no causal interpretation follows from this aggregate alone.

## 9. Matched structural pair diagnostic

**[Engineering proposal]** To compare surface and structural changes over the same observations, define the structural indicator on the same distinct pairs in `A_text`:

\[
d_{\mathrm{struct}}(i,j)=\mathbf 1[Z_i\ne Z_j],
\]

\[
\texttt{structural\_pair\_non\_equivalence}
=\frac{1}{P}\sum_{i<j}d_{\mathrm{struct}}(i,j)
=1-\frac{\sum_z m_z(m_z-1)}{m(m-1)}.
\]

It is a dimensionless observed pair fraction in `[0,1]`, undefined for `m<2`. Every pair uses accepted hard labels and the same text-eligible subset as the surface diagnostic. It remains a sample-pair statistic even when the original generations are dependent.

For `m>1`, it equals `m/(m-1) * (1-SCI_text)`, where `SCI_text` is calculated on that exact subset. This identity is an engineering derivation from finite counts. It does not rename or replace the approved plug-in SCI on the full population.

For counts `(3,1)` on four eligible observations, `1-SCI=3/8`, while the distinct-pair non-equivalence fraction is `1/2`. Treating those numbers as the same estimator would be an error.

Two distances sharing `[0,1]` have a declared common reporting scale; this does not make lexical and structural differences intrinsically commensurate. Section 10 limits the interpretation of their gain contrast to the selected proxy and resolution.

## 10. Condition comparisons and P1/P5 operational targets

### 10.1 Compatibility and resource gate

**[Source-derived: SD §§3.2, 5, 9.5, 9.7]** Structural comparisons depend on task, context, resolution, generation protocol, and sample design. P1 and P5 are empirical predictions, not conditions for software correctness.

**[Engineering proposal]** A comparison requires an explicit shared evaluation frame, compatible class meanings, evidence policies, validity rubrics, ordering and extraction rules, and identified sampling units. Actual A/B/C conditioning differences remain recorded.

A difference can be calculated descriptively without justifying a causal claim. Changes in model state, input domain, instruction content, exposure, sample budget, or classification coverage remain potential explanations until controlled by the approved design.

For budget-matched P1/P5 analyses, Step 6 must fix the selected prefixes, complete-group handling, attempt/retry policy, response/token limits, and what constitutes matched resources. Record actual attempts, returned samples, unavailable responses, and resource measurements where available. No top-up restricted to successes is permitted.

If the conditions are incompatible, keep their separate descriptive results and withhold the affected contrast. If only a descriptive subset comparison is possible, label it explicitly. A numerical quality or coverage tolerance for an empirical decision belongs to the prespecified Hero Benchmark and validation plan, not a hidden default here.

### 10.2 Per-block differences

**[Engineering proposal]** For compatible condition summaries of the same metric and population, report `metric(condition_2) - metric(condition_1)` in that metric's own unit, with both operands and identities. Do not subtract entropy in nats from a lexical distance. Do not pool class IDs across prompt blocks to manufacture a larger support count.

Frequency-table comparisons align semantically compatible class IDs. A class absent from an otherwise valid empirical count table gets a frequency of zero in that table. A class withheld because its evidence is unresolved remains unclassified evidence, not an inferred zero model probability.

### 10.3 P1: surface and structural gain contrast

**[Source-derived: SD §9.7, P1]** Raising temperature under a fixed prompt is predicted to raise token/lexical diversity faster than structural diversity; very high temperature may reduce quality.

**[Engineering proposal; restricted operationalization]** Use A as baseline and B as the prespecified higher-temperature condition. In each prompt block b, use the same resource-selection rule and compute both pair diagnostics on the identical eligible samples within each condition:

\[
\Delta_{\mathrm{surf},b}=L_{B,b}-L_{A,b},\qquad
\Delta_{\mathrm{struct},b}=Q_{B,b}-Q_{A,b},
\]

where `L` is the Section 8.3 surface distance and `Q` is the Section 9 pair fraction. Define:

\[
G_b=\Delta_{\mathrm{surf},b}-\Delta_{\mathrm{struct},b}.
\]

Public contrast field: `p1_proxy_gain_contrast`, with both component changes mandatory. The primary descriptive view is `classified_all`; repeat on `classified_valid` as a validity-conditioned sensitivity when its required pairs exist. Core entropy and SCI changes remain separate companion results.

This contrast tests a particular surface-proxy/structural-resolution relationship. It is not a universal unit-free growth law or a direct estimate of realization entropy. It must be described as evidence consistent with or contrary to P1 **under the declared operationalization**, subject to the measurement and experimental gates.

A positive `G_b` alone is insufficient. For example, both distances could decrease, with the structural distance decreasing more. An interpretation favoring the predicted pattern requires positive surface change and a positive contrast under the approved uncertainty and quality/coverage conditions. Report decreases, saturation, validity loss, and missing-pair cases explicitly. A proxy already at its ceiling may make this operational test uninformative; it does not authorize a post-result proxy replacement.

Confirmation thresholds, multiplicity policy, prompt sampling, and final supporting/contrary/inconclusive decision rules remain due in Steps 6-7. The metric code never changes the schema or excludes inconvenient outputs to obtain a favorable contrast.

### 10.4 P5: valid structural breadth at a declared budget

**[Source-derived: SD §9.7, P5]** Explicit non-equivalent mechanism generation is predicted to produce more non-equivalent outputs than ordinary versions or higher-temperature sampling at matched quality.

**[Engineering proposal]** The first-release breadth target is the `classified_valid` distinct-k count in the same prespecified k-realization prefix, with `classified_all` and full coverage/validity accounting alongside it. For each block, report C minus A and C minus B separately:

\[
\Delta^{C-A}_{\mathrm{valid},b}(k)
=D^{C}_{\mathrm{valid},b}(k)-D^{A}_{\mathrm{valid},b}(k),
\]

with the corresponding C-B contrast. Public field: `p5_valid_distinct_k_delta`, carrying the explicit condition pair and k.

This counts validated, accepted structural breadth within the recorded prefix. It never refills the prefix until k valid outputs have been obtained. Withholding classifications or missing validity can reduce this observed breadth, which is why coverage and evidence acceptance must accompany the number.

A coordinated C set may supply several realizations, but they stay within their recorded call/group. Equal row count alone does not establish matched quality, cost, or independence. The actual group and budget design belongs to Step 6. A larger observed count under C cannot certify probability-thresholded expressible support or a change in the fixed model's latent representation.

## 11. Aggregation and uncertainty

### 11.1 What is and is not estimated

**[Source-derived: SD §9.5]** Results should aggregate over prompts and preserve dependence. SD proposes prompt-level bootstrap intervals, hierarchical estimation, and related designs; it does not prescribe one universal sample count or interval algorithm.

**[Engineering proposal]** Core first-milestone summaries are deterministic calculations on stipulated observations. They have no automatic confidence interval. v0.1 selects one bounded uncertainty method for prespecified condition differences: **paired prompt-block resampling**.

This method treats a block's recorded within-condition outputs and their group dependencies as fixed when resampling blocks. It characterizes between-block variation for the stated design. It does not, by itself, estimate all within-prompt generation uncertainty, uncertainty about unknown classes, or label/schema uncertainty.

Annotator disagreement, withdrawn evidence, proxy saturation, and structural-schema sensitivity remain separate report limitations. They cannot be repaired by increasing the number of bootstrap replicates.

### 11.2 Equal-block summaries

**[Engineering proposal]** Let `d_b` be a prespecified, defined per-block contrast for b in the comparison set of P blocks. The default summary is:

\[
\overline d=P^{-1}\sum_{b=1}^{P}d_b.
\]

Each block has equal weight. A block with more generated samples does not acquire more cross-prompt weight. This mean is a mean of block-specific quantities; it is not the entropy or support of a pooled class distribution.

Record the intended block list, included block list, all missing contrasts and reasons, and the resulting comparison scope. A descriptive complete-block subset summary is allowed only when its subset rule and attrition are explicit. It does not silently replace the intended confirmatory target. Different endpoints may have different available blocks; their means must not be subtracted as though based on one matched set.

For P1, aggregate the two gains and `G_b` over the same blocks. For P5, identify the exact blocks used for each named condition contrast. No output-dependent block weighting or automatic removal of outliers is selected.

### 11.3 Paired prompt-block resampling procedure

**[Engineering proposal]** The proposed initial procedure is:

| Item | Fixed contract |
|---|---|
| Unit | A complete prompt block with all of its paired condition summaries and generation-group dependencies. |
| Eligibility | At least two defined blocks; evidence that block-level resampling is appropriate for the declared target. Fewer blocks or unsupported cross-block dependence makes the interval unavailable. |
| Replicates | 2,000 resamples, each selecting P block indices with replacement from the P included blocks. |
| Statistic | Recalculate the equal-block mean from the selected paired contrast records. No row-level reclassification or sample-level resampling. |
| Reproducibility | Record the integer seed, actual random-generator implementation/version, configuration, and an immutable resample-index manifest or equivalent replay record. Exact index-generation implementation is recorded when authorized software exists. |
| Interval | Nominal 95% percentile endpoints at probabilities 0.025 and 0.975 of the sorted 2,000 replicate means. |
| Quantile convention | For sorted zero-indexed values `v[0]...v[B-1]`, use `h=(B-1)*q` and linear interpolation between the adjacent ranks; an integer h selects that rank. |
| Failures | Do not discard problematic replicates selectively. An inconsistent or undefined configured statistic blocks that interval pending explicit correction. |

Two blocks are only the minimum for a nontrivial block-resampling calculation; this is not an empirical adequacy guarantee. Display the actual block count and the limited scope of small suites. More bootstrap replicates cannot replace more independently informative blocks.

Where blocks were sampled from a documented target prompt population under an appropriate design, an interval may be described as a prompt-sampling interval with its assumptions. For a fixed convenience suite, label it `prompt_resampling_sensitivity`; do not claim population confidence merely because the interval is numeric. With one block, keep its descriptive contrast and mark the block interval unavailable.

Cross-block shared histories or coordinated generation can violate the proposed resampling unit. Such evidence requires an approved higher-level grouping design or withholding the interval. This first-release contract does not silently switch to a different cluster model.

A narrow or degenerate interval does not establish ontology validity or general model certainty. Formal prediction decisions and multiplicity handling remain subject to the preregistered Step 6-7 design.

## 12. Non-executable fixtures and expected outcomes

**[Engineering proposal]** These are constructed arithmetic and state-handling specifications. Symbols such as A, B, and C stand for stipulated class IDs under a hypothetical valid fixture schema. They are not an approved hero taxonomy, collected outputs, model scores, or completed implementation tests. Decimal values are rounded illustrations; formulas and exact fractions govern.

### 12.1 Core arithmetic fixtures

| Fixture | Positive class counts | Observed support | H in nats | SCI | Shannon effective classes | Simpson effective classes |
|---|---|---|---|---|---|---|
| MF-01: single class | `(4)` | 1 | 0 | 1 | 1 | 1 |
| MF-02: balanced pair | `(2,2)` | 2 | `ln(2)` | `1/2` | 2 | 2 |
| MF-03: unequal pair | `(3,1)` | 2 | `ln(4) - (3/4)ln(3)` ≈ 0.562335144619 | `5/8` | `4 / 3^(3/4)` ≈ 1.754765350603 | `8/5` = 1.6 |
| MF-04: three singletons | `(1,1,1)` | 3 | `ln(3)` | `1/3` | 3 | 3 |
| MF-05: unobserved registry entry | Counts `(3,1,0)` in registry `{A,B,C}` | 2 | Same as MF-03 | Same as MF-03 | Same as MF-03 | Same as MF-03 |
| MF-06: no accepted classes | Selected records exist; `n_A=0` | 0 with empty-classified qualifier | Undefined | Undefined | Undefined | Undefined |

For MF-03, `tau_e=0.25` gives thresholded support 2; `tau_e=0.250001` gives 1; `tau_e=0.80` gives 0. The unthresholded entropy and SCI remain unchanged.

For counts `(1,4)`, `tau_e=0.2` includes both classes by exact equality for the first class. A rounded display of a frequency cannot change the result. An omitted threshold returns `not_requested`; zero is an invalid threshold.

### 12.2 Classification and validity accounting fixture

**MF-07.** Six selected fixture realizations have the following recorded states. All indicated accepted assessments satisfy the fixture policy. The sixth provisional assignment is deliberately not accepted.

| Sample | Assignment | Review / acceptance | Validity |
|---|---|---|---|
| 1 | A | Accepted fixture | Valid |
| 2 | A | Accepted fixture | Valid |
| 3 | B | Accepted fixture | Invalid |
| 4 | B | Accepted fixture | Undetermined |
| 5 | Unresolved | No accepted hard class | Valid |
| 6 | Proposed C | Provisional; excluded | Valid |

Expected outcomes:

- `classified_all`: n=4, counts `(2,2)`, support 2, H=`ln(2)`, SCI=`1/2`.
- `classified_valid`: n=2, counts `(2)`, support 1, H=0, SCI=1.
- `classification_coverage=4/6`; `valid_fraction_selected=4/6`; `decisive_validity_coverage=5/6`; `classified_valid_coverage=2/4`; `classified_valid_fraction=2/4`.
- The unresolved sample and provisional C remain visible. C contributes no occupied class. Validity does not complete a missing structural assignment.

**MF-08.** Four accepted same-class realizations, all invalid: the all-view has support 1 and H=0; the valid-view has support 0 with undefined distribution metrics. Reclassifying failure as diversity zero across both views would be incorrect.

**MF-09.** A selected inventory with only unresolved labels: occurrence support is 0 with `n_A=0`, while entropy/SCI/effective counts remain undefined. This must remain distinguishable from MF-01's genuine concentrated empirical distribution.

### 12.3 Fixed-prefix fixture

**MF-10.** Prespecified order: `A(valid), A(valid), B(invalid), unresolved(valid), C(valid), B(valid)`. All specific class labels in this example are accepted fixtures.

| Request | All-view distinct-k | Valid-view distinct-k | Accepted all / valid counts in prefix |
|---|---|---|---|
| k=2 | 1 | 1 | 2 / 2 |
| k=4 | 2 | 1 | 3 / 2 |
| k=6 | 3 | 3 | 5 / 4 |
| k=7 | Unavailable | Unavailable | Insufficient prefix length; no shrink-to-six rule. |

Input-file reordering preserves these results when recorded sequence metadata is unchanged. Changing the actual experimental order can legitimately change a prefix result. Replacing the invalid third record with a later valid record is prohibited.

### 12.4 Surface and pair fixtures

**MF-11.** Texts `a b c` and `a b d` produce padded trigram sets `{(BEGIN,a,b),(a,b,c),(b,c,END)}` and `{(BEGIN,a,b),(a,b,d),(b,d,END)}`. Their intersection has size 1 and union size 5, giving surface distance `4/5`.

If both carry the same stipulated accepted class, structural pair non-equivalence is 0 and the within-class proxy is `4/5`. This demonstrates arithmetic compatibility between same-class assignment and nonzero surface variation, without claiming any empirical model behavior.

**MF-12.** Four eligible records with classes `(A,A,A,B)` give structural pair non-equivalence `3/6=1/2`. Their SCI is `5/8`. This fixture prevents confusing distinct-pair disagreement with `1-SCI=3/8`.

**MF-13.** Every eligible sample belongs to a different class. The overall surface pair average can be defined, but no within-class pair exists, so the within-class proxy is undefined. With only one eligible text, both pair averages and structural pair non-equivalence are undefined.

**MF-14.** Two accepted class records have inaccessible text and two have usable text. Core count metrics use all four accepted records. Pair diagnostics use the same two-record text subset for both surface and structural values, report text coverage `2/4`, and expose the missing-text reasons. They must not compare a two-record lexical diagnostic with a four-record structural pair diagnostic.

### 12.5 Comparison, correction, and deferred-capability checks

| Fixture | Required future outcome |
|---|---|
| MF-15: unrelated class/schema versions | Separate cell summaries may be calculated; an unsupported pooled comparison is unavailable. |
| MF-16: coordinated group | Five realizations from one call retain one dependency group. They do not become five independent blocks for an interval. |
| MF-17: one prompt block | Per-block contrasts may be available; a prompt-block resampling interval is unavailable. |
| MF-18: explicit paired resample | Given two stipulated block contrasts 0.1 and 0.3, index draws `(1,1)`, `(1,2)`, and `(2,2)` yield means 0.1, 0.2, and 0.3. This is a replay fixture, not a recommendation for a two-block empirical study. |
| MF-19: false favorable contrast | Surface gain `-0.10`, structural gain `-0.20`, contrast `+0.10`: a positive contrast cannot be labeled the predicted increase in surface variation. |
| MF-20: assignment correction | Correcting `(A,A,A,B)` to `(A,A,A,A)` under supported evidence changes support 2 to 1, H to 0, and SCI to 1 in a new analysis. Old reports and sample identities remain preserved. |
| MF-21: empty recovery denominator | A future ERR calculation with a genuinely empty missing-reference set has no numeric value. v0.1 reports the capability as deferred. |
| MF-22: unqualified half-life | No recursive trajectory or identified categorical scenario yields no SHL value. Corpus size or a single output batch cannot substitute. |
| MF-23: complete-block attrition | A missing condition is disclosed; a mean over remaining complete blocks identifies its changed scope and cannot silently become the planned confirmatory result. |
| MF-24: adverse prediction outcome | Valid data can show no gain or greater gain for the baseline. Software succeeds when it reports that outcome faithfully. |

These fixtures transfer to the Step 7 validation document. They do not introduce a test suite, execute generated code, or establish independent annotation evidence.

## 13. Deferred metric catalog and prerequisites

### 13.1 Support, interventions, and the frontier

**[Source-derived with engineering disposition]** Keep these quantities available as documented future objects. Their fields are not implemented numeric outputs in v0.1.

| Capability | Source object | Prerequisites and inference boundary |
|---|---|---|
| `observed_intervention_union_size` | Finite union of classes actually elicited under evaluated interventions; an engineering descriptive field linked to SD §5 / SI §3.3. | Named tested subset of an admissible intervention family, compatible class frame, recorded interventions and samples. It does not estimate the full thresholded expressible support. |
| Expressible support / SSS_expr | Classes produced at a stated generation-probability threshold under an admissible inference family. SD §5.2; SI §§3.3, 8.1. | Probability estimator, repeated evidence, intervention coverage, uncertainty, fixed-model identity, and separation from the empirical-frequency threshold. The supplied sources do not specify one complete finite-sample estimator. |
| Registry-normalized expressible support | `cardinality(S_expr intersect reference_registry) / cardinality(reference_registry)`. SI §8.1. | Validated expressible set and registry; empty registry makes the ratio undefined. Occurrence coverage cannot silently replace this quantity. |
| Load-bearing intervention effect | Distributional change under a matched structural intervention. SD §§3.5-3.6, 9.2. | Consequence-sensitive intervention, controls, chosen distance/threshold, repeated evidence. A/B/C descriptive differences alone do not identify load-bearingness. |
| Convergence provenance | Profile of changes under interventions on candidate convergence constraints. SD §6.6. | Matched interventions and evidence separating candidate mechanisms. Low entropy alone identifies no cause. |
| Convergence frontier | Maximal stabilized resolution, or frontier set for partially ordered resolutions. SD §4. | Validated resolution order, concentration/stability thresholds, repeated perturbation and sampling evidence. One hard partition cannot supply a frontier. |
| Structural transmission | How upstream specification variation survives in output structural classes. SD §9.2. | Linked specifications/outputs, independent coding at both stages, a prespecified transmission measure. The source does not prescribe one universal estimator. |
| Latent support | Recovery under stronger diagnostics with explicit limits on injected information. SD §§5.3-5.4; SI §3.3. | Dedicated diagnostic/recovery contract, tracked model-state effects and contamination controls; UD-007 remains deferred. |

The support-inclusion hierarchy requires compatible thresholds and intervention families. Finite one-off appearance cannot certify membership in a higher probability-thresholded set.

### 13.2 Recursive retention and Structural Half-Life

**[Source-derived: SI §§5.3-5.4, 8.3]** SI defines Gini-Simpson diversity `D_t=1-sum_z p_t(z)^2`. Under its fixed-size closed categorical resampling model:

\[
\mathbb E[D_t]=(1-1/n)^tD_0,
\qquad
\mathrm{SHL}_0(n)=\frac{\ln 2}{-\ln(1-1/n)},\quad n>1.
\]

SI's empirical specification fits an approximately geometric diversity decline as:

\[
D_t\approx D_0\,2^{-t/\mathrm{SHL}_{\mathrm{emp}}}.
\]

**[Engineering proposal; deferred]** Preserve separate `structural_half_life_null` and `structural_half_life_empirical` names, with units of documented recursive rounds. A meaningful diversity-halving interpretation additionally needs positive starting diversity. `n` in the null model is its categorical resampling size; it is not automatically the number of corpus rows, tokens, model parameters, or analysis samples in a neural experiment.

An empirical fit needs comparable round/schema definitions, class evidence, trajectory uncertainty, an approved fitting interval, and model-fit checks. Non-geometric, flat, increasing, or interrupted trajectories must not be forced into a positive finite half-life. The source permits local or interval-specific summaries. No fitted estimator or fitting software is selected at this step.

Later retention and rare-class-loss reports must distinguish observed nonappearance from validated representational loss, and preservation from reopening. Real neural transitions may add structure; the closed categorical model's support non-expansion cannot be imposed as a universal data-validation rule on neural experiments. [SI §§5.7, 6, 12]

### 13.3 External Recovery Rate

**[Source-derived: SI §8.4]** Let the pre-intervention missing reference set be `M=reference_registry minus S_expr_pre`. Then:

\[
\mathrm{ERR}=\frac{|M\cap S_{\mathrm{expr}}^{\mathrm{post}}|}{|M|}.
\]

ERR is undefined when `M` is empty. An intervention must be independently grounded, recovery externally validated, and the target answer must not be directly pasted into the output as a substitute for recovered ability.

**[Engineering proposal; deferred]** An ERR study requires a fixed registry, prespecified pre/post support criteria, assessed missing-set evidence, intervention provenance, model-state-change records, and a validation design for expression after intervention. No v0.1 number is supplied. A nonempty unobserved finite sample tail is not automatically a validated missing expressible set. Parameters updated during an intervention identify a changed model state; they cannot be described as an inference-only test on an unchanged model.

### 13.4 Soft classification and full realization entropy

**[Source-derived: SD §3.7; SI §4.2]** Probabilistic class assignments introduce a separate classification-uncertainty term in the entropy decomposition. That uncertainty cannot be silently counted as structural breadth.

**[Engineering proposal; deferred]** The initial hard-label metrics never replace unresolved samples with posterior mass or infer full residual entropy by subtracting a surface proxy from another summary. Exact realization entropy, semantic entropy, posterior-class entropy, and overlapping-class estimators require their own evidence and estimator contracts. Their absence does not block the approved hard-assignment first milestone.

## 14. Correction, reproducibility, and conformance requirements

**[Owner-approved decision: OA-003; structural contract §§10-12]** Corrections preserve histories and identify affected assignments, populations, metrics, comparisons, and reports. Re-analysis supplies no new model observations.

**[Engineering proposal]** A run pins input/configuration identity, class/rubric versions, exact assignment revisions, sequence/extraction rules, text-proxy version, and any bootstrap replay identity. Revising evidence, class membership, validity, or selection rebuilds affected denominators before calculating dependent results. A changed schema cannot be applied only to the condition that benefits from it.

Each downstream artifact records whether its prior result is retained, superseded, unavailable, or awaiting re-analysis. Reusing a report value after its required evidence has been withdrawn is prohibited. A reference change affects only metrics whose semantics depend on that reference, unless it also changes the structural map or assignments.

Future implementation conformance must establish the following, with Step 7 providing the final traceability mapping:

| Requirement | Expected evidence / future check |
|---|---|
| One population definition per result | Exact sample and assignment manifest; denominator reconciliation. |
| Distinct core estimators | MF-01 through MF-06, including unequal effective counts and exact threshold boundaries. |
| Validity and evidence separation | MF-07 through MF-09 and structural-contract checks SC-T05, SC-T10, SC-T15. |
| Stable prefix selection | MF-10; no classification/validity top-up; sample order and groups preserved. |
| Proxy identity and pair denominators | MF-11 through MF-14; tokenizer fixtures, empty/short text, and text-coverage handling. |
| Safe and reproducible interpretation | MF-15 through MF-24; explicit unsupported, adverse, and missing-evidence outcomes. |
| Numerical behavior | Count exactness, probability/range checks, unrounded derived calculations, and declared tolerances. |
| Label and ordering invariance | Bijective class renaming and input-storage reorder preserve applicable summaries; genuine prefix-order changes are distinguished. |
| Evidence withdrawal and re-analysis | Affected-view reconstruction, report invalidation, old-version retention, and no artificial sample increase. |
| Passive input processing | No generator calls, judge calls, code execution, or remote retrieval through a metric input. |

The checks here are specifications, not completed tests. No favorable empirical prediction is required for any software conformance check.

## 15. Step 4 acceptance and next gate

**[Engineering proposal]** The approval request covers the metric/diagnostic component of UD-005: the complete first-slice estimator rules, denominator accounting, fixed-prefix distinct-k, limited realization proxy, matched pair contrast, and bounded prompt-level comparison/uncertainty method.

The following remain at their existing gates:

| Item | Disposition |
|---|---|
| Step 2 scope, notation, populations, and first-release boundary | Approved in OA-002; unchanged. |
| General classification contract | Approved in OA-003; unchanged. |
| This metric and diagnostic contract | Proposed; awaiting owner review. |
| Integrity roles, independence rules, and release evidence requirements | Step 5, UD-006. |
| Hero family, eligible classes, prompts, k grid, budgets, actual group design, and empirical coverage/quality criteria | Step 6, UD-004 and UD-005. |
| Complete test mapping and supporting/contrary/inconclusive decision specification | Step 7, UD-005. |
| Actual independent experimental evidence | Outstanding under UD-006; approval of formulas cannot supply it. |
| Deferred metric estimators and latent diagnostics | Outside the first milestone; no new blocking dependency. |

After approval and instruction to continue, Step 5 creates `EVALUATION_INTEGRITY.md` and updates the decision register. Neither future content approval nor implementation permission is inferred from the current step.
