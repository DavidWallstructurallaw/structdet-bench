# PHASE_2_PLAN

## StructDet-Bench: Offline Condition Comparisons and Bounded P1/P5 Evaluation

| Field | Value |
|---|---|
| Document version | 0.1 |
| Record date | 2026-09-18; no exact time of an owner decision is asserted |
| Status | **PROPOSED; READY FOR OWNER REVIEW** |
| Decision authority | Theory Owner |
| Present instruction | Prepare `PHASE_2_PLAN.md` |
| Implementation authorization in this instruction | None |
| Working baseline | The supplied final local Phase 1 delivery, identified in Appendix A |
| Repository | `DavidWallstructurallaw/structdet-bench` |
| Repository status checked during planning | `main` at `8cd0fe659c9e515f76195164b8923395f8c4ca31`, the Step 6 delivery; final local Phase 1 synchronization remains outstanding |
| Phase target | Implement the already specified V comparison layer while preserving the completed M measurement layer |
| Empirical evidence E | Actual independent evidence remains separate; UD-006 is not closed by software tests |
| Deferred capability D | Remains outside this phase |
| Current delivery | This plan only; no implementation, repository write, model call, candidate execution, or spending |
| Other toolkit dependencies | None |

## 1. Authority, sources, and baseline

### 1.1 Owner instruction and progression

Following the Phase 1 local completion handoff, the owner asked whether the next action was Phase 2 planning, then requested:

> 给我 PHASE_2_PLAN.md

This authorizes planning from the delivered Phase 1 local baseline. It records acceptance of that handoff for progression, including its explicit distinction between completed local M checks and unfinished GitHub delivery. It does not approve the new engineering choices first proposed in this document, authorize their implementation, or make missing repository or empirical evidence present.

`PHASE_1_COMPLETION.md` retains its historical status fields and exact bytes. Its final-review history, the accepted Step 6 test-maintenance amendment, and the Step 7 corrective findings remain auditable. No earlier document is silently rewritten to record this later instruction.

Approval of this plan adopts its engineering choices. Execution additionally requires an instruction identifying a step or a named dependent batch. One instruction may approve the plan and authorize that step or batch. Unchanged scientific definitions do not require repeated approval.

### 1.2 Controlling references

| Key | Controlling material | Role in Phase 2 |
|---|---|---|
| PLAN0 / APPROVAL | `PHASE_0_PLAN.md`; `PHASE_0_APPROVAL.md` | Baseline authority and M/V/E/D boundaries. |
| SCOPE | `PROJECT_SCOPE.md` | Offline first release; same Tier 1 task; separation from other toolkits. |
| DEF | `DEFINITIONS_AND_UNITS.md` | Task, horizon, resolution, identities, populations, units, and metadata states. |
| SC | `STRUCTURAL_CLASS_CONTRACT.md` | Accepted structural membership, uncertainty, validity separation, and revision. |
| MET | `METRICS_SPEC.md`, v0.2 | Core estimators; §§8-11 surface/pair diagnostics, contrasts and resampling; §12 fixtures; §14 corrections. |
| EI | `EVALUATION_INTEGRITY.md` | Roles, lineage, independent annotation, evidence-dependent claims and corrections. |
| HERO | `HERO_BENCHMARK_SPEC.md` | Bounded-integer sorting; A/B/C prompts, groups, budgets, controls, quality/coverage gates, and report order. |
| TRACE | `THEORY_TO_CODE_TRACEABILITY.md`, v0.2 | The 40 TR requirements and 36 RF report groups. |
| VF | `VALIDATION_AND_FALSIFICATION.md`, v0.2 | The 54 VT families; exact gate boundaries; P1/P5 outcomes and OF-01 through OF-14. |
| UD | `UNRESOLVED_DECISIONS.md`, v0.7 | Historical decisions; outstanding E evidence and deferred latent diagnostics. |
| EC-001 | `EVALUATION_CLOSURE_ADDENDUM.md`; `BASELINE_UPDATE_EC_001.md`; `THEORY_SOURCES.md` | Five conjunctive conditions, anomaly preservation, reopening distinctions and ten disclosures. |
| PLAN1 / COMPLETE1 | `PHASE_1_PLAN.md`; `PHASE_1_COMPLETION.md` | Existing implementation, accepted maintenance, local completion and remaining remote handoff. |
| IMPL1 | Final local source, fixtures, input documentation, test matrix and QA runner | Actual interfaces to extend, not a hypothetical replacement architecture. |

All references mean the pinned editions in Appendix A. The precedence relationship is: explicit authorized revisions, the identified scientific baseline read with EC-001, this plan's approved implementation choices, then code and tests. A disagreement in code never automatically changes the scientific contract.

### 1.3 Theory sources and scope of use

| Source | Relevant supplied locations | Source-level role |
|---|---|---|
| SD: *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness* | §§3.2-3.7, 5, 6.5, 9.1-9.7, 11-12; particularly pp.18-21 | Task-relative structural distributions; separate realization variation; prompt-level aggregation; P1 and P5. |
| SI: *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*, v1.0 | §§3-5, 8-9, 12; particularly pp.7-12 and 18-21 | Observed/expressible/latent distinctions, concentration, separate effective counts and recursive-support boundaries. |
| EC: *Evaluation Closure: Benchmark Inbreeding and the Design of Open AI Evaluation* | §§2, 4.4-4.5, 6-7, 9-10; particularly pp.3-4, 7-11 and 13 | Structural validity, type-appropriate constraints, five conditions, two reopening mechanisms and reporting duties. |

**Source-derived:** SD's prediction table on p.21 supplies the P1 temperature-stratification and P5 structural-divergence questions. SI's recursive categorical results apply to their stated resampling model. EC distinguishes evidence about a bounded probe from wider deployment claims.

**Previously adopted engineering contracts:** The particular lexical-trigram tokenizer, pair statistic, six-prompt sorting design, numerical thresholds, 2,000-replicate percentile procedure and four prediction-outcome labels come from MET/HERO/VF. They must not be attributed to the papers as if the papers specified those implementation choices.

**Engineering proposals in this plan:** New module names, extension encoding, test organization, replay transport, runtime limits and execution order are submitted here. They implement the adopted quantities without changing their scientific meaning. References cited inside the three papers have not been independently researched for this planning task. No new theoretical source is added.

### 1.4 Baseline state actually used

COMPLETE1 and its retained execution journals report 503 passing tests, a passing complete M gate, 37 M-bearing VT families, 33 M-applicable TR rows, 28 M-applicable RF groups and eight EC record-check groups. These are predecessor results, not Phase 2 test results.

During preparation of this plan, the final ZIP was read successfully, its CRC check passed, and the available pinned project files were checked against COMPLETE1. The standalone completion record matches the copy in the final ZIP. The source and software were inspected; no Phase 2 implementation or fresh software test run is claimed.

The local deliverable contains 67 project files plus separate verification history. The connected repository was read again and still exposes Step 6 on `main`. Local completion and remote publication therefore remain different facts.

**Mandatory implementation preflight:** Before changing Phase 2 runtime code, complete the outstanding exact Phase 1 synchronization and remote read-back in Step 1. The same operation must preserve any intervening owner changes rather than replacing a live branch with an assumed old tree. This is a delivery-integrity gate, not a demand for independent empirical evidence or another toolkit's completion.

## 2. Objective and explicit boundaries

### 2.1 Required working result

Extend the existing path:

`local inputs -> evidence -> inventories -> accepted populations -> core metrics -> reports`

with:

`explicit comparison binding -> original-text diagnostics -> endpoint-specific compatibility and gates -> paired block contrasts -> equal-block summaries -> replayable sensitivity ranges -> bounded P1/P5 outcomes`.

For a complete, explicitly fixture-labeled A/B/C package, the tool must produce a full comparison report from actual local text and label inputs. A real imported study follows the same arithmetic, with its actual evidence limitations. Missing independent evidence may withhold its evidence-qualified outcome while leaving justified descriptive numbers available.

Phase 2 completes the planned offline V software workflow for the adopted sorting task. It does not conduct the empirical P1/P5 study, validate the taxonomy itself, or certify general model capability.

### 2.2 Included capabilities

| Capability | Phase 2 requirement |
|---|---|
| Comparison binding | Explicit task/schema/protocol/cell/block mapping, primary endpoints, material roles, exposure and controls. |
| Text identity and eligibility | Read declared local snapshots; preserve original output association, extraction/encoding versions and absence reasons. |
| Surface diagnostic | `surface_lexical_trigram_distance` using `surface_lexical_trigram_jaccard_v1`. |
| Within-class diagnostic | Per-class pair counts/distances and the pair-weighted `within_class_realization_diversity_proxy`. |
| Matched structural pair diagnostic | `structural_pair_non_equivalence` on the same text-eligible observations and pairs. |
| Compatibility and gates | Frame, group completion, coverage, quality, controls, resources, evidence and dependence assessed per requested endpoint. |
| Contrasts | Same-unit condition differences; P1 B-A surface/structural gains and their contrast; P5 C-A and C-B valid distinct-20 deltas. |
| Aggregation | Equal-block means with intended, included and missing block sets exposed. |
| Sensitivity | 2,000 paired prompt-block resamples, seed 20260917, specified quantiles, stored index replay and bounded interpretation. |
| Decisions | VF's `supporting`, `contrary`, `inconclusive`, `not_evaluated`, with primary/sensitivity and narrow/full scopes preserved. |
| Reports and correction | Complete RF coverage for implemented V outputs, ten EC disclosures, safe JSON/Markdown parity and recomputation after relevant evidence revisions. |
| Regression | Preserve the existing M behavior and predecessor test identities; add concrete V and engineering tests. |

Core entropy, SCI, effective support and observed support differences are companion descriptive outputs in their original units. They do not replace the registered P1 pair contrast or P5 distinct-20 endpoint. Threshold 0.10 and k=5/10 retain their secondary roles.

### 2.3 Exclusions

The phase includes no model-provider client, API key handling, paid generation, candidate-program execution, compiler/test sandbox, remote retrieval, automatic evidence collection, LLM judge, automatic structural classifier or label repair. It supplies no training loop, cross-toolkit service, database, dashboard, hosted CI, container platform, package distribution or native cross-platform port.

Keep all D entries deferred: expressible and latent support, observed intervention unions, probabilistic/overlapping assignment, exact realization entropy, convergence frontiers or provenance, load-bearing causal intervention effects, structural transmission, recursive retention, either SHL, ERR, and a new Gini-Simpson headline. P1's structural-pair calculation is not permission to expose every algebraically related deferred estimator.

No p-values, significance-star interface, familywise significance claim, equivalence test, effect-size cutoff, unseen-class correction, imputation, inverse-probability weighting, learned similarity metric, semantic embedding, adaptive prompting or post-result endpoint selection is introduced.

### 2.4 Acceptance axes

| Axis | What can be completed here | What remains separate |
|---|---|---|
| M regression | Existing measurement behavior still passes its applicable checks. | Historical approvals and reports remain historical. |
| V implementation | Correct computation, gate routing, uncertainty replay, outcomes and reporting on identified fixtures/imports. | The truth of imported scientific assertions. |
| E fulfillment | Preserve supplied records and detect missing/inconsistent evidence. | Actual independent schema/sample review and actual model experiments; VT-47/E, VT-48/E and VT-49/E cannot pass from fixtures. |
| Repository delivery | Authorized commits and verified remote file identities. | Local verification alone cannot establish remote delivery. |
| Final acceptance | Completion record submitted after actual conformance. | Owner acceptance and any release/empirical-publication decision. |

## 3. Scientific and statistical contract to preserve

This section is an implementation checklist of adopted MET/HERO/VF requirements. Equations, thresholds and outcomes below are not new design choices.

### 3.1 Study frame, grouping and material role

The main design is P01-P06, A/B/C, four fresh coordinated calls per block-condition, five intended candidate positions per call: 18 cells, 72 planned calls, 360 planned candidate positions. These design counts never imply calls were actually made. The optional P00 pilot has six calls and 30 positions; it stays outside main summaries.

The task remains bounded integer sorting, with list length 0-256 and values 0-4095, the adopted eight mechanism descriptors, and the separate validity rubric. There is no automatic taxonomy expansion. A newly encountered mechanism follows SC and EC-001's review/revision path.

The shared evaluation frame stays fixed while the registered generation manipulation changes. A/B have byte-identical sent visible prompts in each block; C changes the prescribed variation clause. The six exact openers and common task/output text are those in HERO §7.2. Matching identifiers alone does not prove the supplied sent content matches that assembly.

The design settings remain A/C temperature 0.4 and B 1.0, top-p 1.0, zero penalties where exposed, no user-fixed generator seed, common 8192 output-token allowance under an identified cap convention, no requested tools/retrieval/history/best-of. Requested settings, actual enforcement, hidden/unsupported controls, reasoning settings and observed deployment changes remain distinguishable.

Preserve HERO §7.4's interleaving record: group g, then block b, with condition permutation index `(b + g - 2) mod 6` in `ABC, ACB, BAC, BCA, CAB, CBA`. The software audits imported records; it does not issue calls in this order. No recorded failure, retry, refusal, truncation or repeated mechanism earns a replacement observation.

Primary matching means **matched planned calls, candidate positions, and output allowance**. It does not mean equal actual input tokens, hidden compute, latency or monetary cost. C's prompt clause is longer. Unknown usage stays unknown; a changed cap convention is an actual compatibility issue.

Only each named endpoint's participating cells determine its eligibility. Missing C need not erase a supported A/B P1 comparison. Unsupported B controls may leave C-A available while P1, C-B or full P5 are restricted. The full-study inventory must nevertheless disclose every missing cell and deviation.

### 3.2 Original text and lexical units

Use the already selected realization or the prospectively declared exact extraction region. For HERO's ordinary extraction, the source is the contents of its single fenced Python block, excluding headings/fences and preserving code, comments, literals and original offsets. A uniquely identified truncated final block remains truncated. Empty emitted bodies, never-emitted positions and inaccessible text are different states.

Do not choose the best fence, infer headings, concatenate fragments, repair code, complete helpers from another candidate, or extract a different region after seeing labels or scores. Ambiguous association restricts the affected result. The phase adds verification/consumption of imported regions, not a general extraction-and-repair service.

The fixed proxy steps are:

1. Decode the registered text with its encoding recorded. Use strict UTF-8 for the proposed first physical text profile. Other imported encodings need an explicitly supported, versioned decoder; no guessing or replacement characters.
2. Convert CRLF and standalone CR to LF. Preserve every other code point, case, identifier, literal, punctuation mark and comment. No Unicode normalization, transliteration, stemming, renaming or case folding.
3. A maximal contiguous run of Unicode categories `L*`, `N*` or underscore forms one surface lexical unit. Every other non-whitespace code point is one unit. Whitespace is the versioned Unicode `White_Space` property.
4. Add one collision-proof beginning symbol and one collision-proof ending symbol. They are distinct internal symbols, not ordinary strings that can occur in submitted text.
5. Form a set of consecutive ordered triples. Empty lexical sequences are ineligible; a one-unit sequence yields one trigram through the boundary symbols. Repeated identical trigrams count once.

Record proxy version, Unicode category-table version, `White_Space` table version and table identity. A generic host whitespace predicate cannot silently replace the required property. Different tables trigger a compatibility assessment. Original-byte hashes remain distinct from normalized-text or trigram identities. Surface lexical units are not provider tokens. [MET §§8.1-8.2; VT-31]

### 3.3 Common subset and pair denominators

For each approved population A, retain the original denominator n_A. Its usable-text subset is A_text, with m observations. Record its exact membership, exclusion reasons, `proxy_text_coverage=m/n_A` when defined, and unordered distinct-observation pair count `P=m(m-1)/2`.

For nonempty trigram sets G_i and G_j:

`d_surf(i,j) = 1 - |G_i intersection G_j| / |G_i union G_j|`.

The all-pair surface mean is the sum over all eligible unordered pairs divided by P. The structural-pair mean on those same observations is:

`Q = 1 - sum_z m_z(m_z-1) / [m(m-1)]`.

Keep identical membership for these two diagnostics within each condition and view. Do not compare a two-text surface statistic with a four-label structural statistic. Pair counts and same-call pairs do not become independent statistical replicates.

Within each class, use `P_z=m_z(m_z-1)/2`. Its mean is undefined when P_z=0. The combined within-class proxy is `sum_z(P_z * class_mean_z) / sum_z P_z`, not an equal-class average. Show singleton classes, per-class eligible counts and composition changes.

With m<2, the corresponding pair means are mathematically undefined. If every occupied class is a singleton, the within-class aggregate is undefined even though overall surface and structural-pair means can exist. Inaccessible text is not an empty string. Resource exhaustion makes affected diagnostics unavailable and must not be disguised as ordinary missing-text attrition.

The finite-sample identity `Q = m/(m-1) * (1-SCI_text)` holds on that exact subset when m>1. It does not replace full-population SCI. For A,A,A,B, Q=1/2 while `1-SCI=3/8`. [MET §§8.3-9; VF §5.4]

### 3.4 Endpoint-specific numeric and evidence gates

Apply each applicable condition to every participating cell or paired block. Use exact count fractions; suite means cannot hide failed individual cells.

| Gate | Required rule | Applicability |
|---|---|---|
| Intended primary positions | Four intended groups of five identifiable candidates per participating cell. | Primary matched P1 and P5. |
| Classification coverage | At least 0.90 of selected U accepted into `classified_all`. | Both primary questions. |
| Decisive validity coverage | At least 0.95 of U has accepted valid/invalid assessments. | Both primary questions. |
| Valid-output structural coverage | At least 0.90 of accepted valid realizations are classifiable, when the valid denominator exists. | Both; retain its conditional denominator rule. |
| Proxy text coverage | At least 0.95 of the applicable classified population, and at least two eligible texts. | Pair-based P1 and its requested sensitivity; not an additional P5 count prerequisite. |
| Validity floor | `valid_fraction_selected >= 0.80`. | P5; diagnostic for primary P1 and required for an added clean quality-comparable P1 description. |
| Matched-quality band | Absolute compared-cell valid-fraction difference <=0.10 within every paired block. | C-A and C-B separately for P5; B-A for a clean quality-comparable P1 description. |
| Shared frame | Compatible task/domain, horizon, resolution, class meanings, evidence policy, rubric, extraction and material role. | Each affected contrast. |
| Controls/resources | Evidence appropriate to the named manipulation and planned-resource match. | Each named manipulation/comparator. |
| Independent evidence | Applicable schema, core/audit, exposure and integrity evidence under EI/VF. | Evidence-qualified empirical outcomes; fixtures remain stipulated. |
| Resampling | Defined block contrasts, appropriate block unit and replay assumptions. | Interval and full fixed-suite outcome, not every descriptive count. |

At n=20, 18 accepted assignments pass the classification gate; 17 fail. Nineteen decisive validity assessments pass; 18 fail. With 16 valid outputs, 15 classifiable-valid pass and 14 fail. Nineteen of 20 usable texts pass the text gate, but at n_A=18 or 19 all classified observations need text to reach 0.95. P5 passes its floor at 16/20 and its quality band at a difference of 2/20; a difference of 3/20 fails. Equality at an adopted threshold passes. [VF §5.3]

An undefined valid-output coverage ratio is exposed with its conditional applicability; do not silently set it to zero or one. Zero valid outputs necessarily fail P5's floor, but the primary P1 prediction permits quality deterioration and must follow VF's separate quality role.

**AF-001:** a local evidence failure with a valid shared frame changes its affected accepted subset, not the entire study by default.

**AF-002:** a missing proxy representation does not veto P5 when artifact identity and independently sufficient membership/validity remain available. Material essential to those judgments retains its ordinary consequence. A shared unsupported frame can still restrict a broader set of endpoints.

**AF-003:** declared local inputs may be read passively; remote references and embedded instructions cannot initiate actions.

### 3.5 Per-block contrasts and full-target summaries

For each block b:

`surface_gain_b = L_B,b - L_A,b`

`structural_gain_b = Q_B,b - Q_A,b`

`p1_proxy_gain_contrast_b = surface_gain_b - structural_gain_b`.

Primary P1 uses `classified_all`; repeat on `classified_valid` only as a labeled sensitivity. Structural gain is not required to be positive. Entropy differences stay in nats and cannot be subtracted from lexical distance.

P5 uses the complete intended `classified_valid` distinct-20 prefix:

`p5_valid_distinct_k_delta(C,A,b,20) = D_valid,C,b(20) - D_valid,A,b(20)`

and separately C-B. Retain all-view counterparts and k=5/10 as companions. Never refill to obtain 20 classified or valid successes.

The registered primary summary needs six defined, compatible paired blocks, with equal block weights. Each per-block result retains both operands, its own unit, source cells, selection, accepted revisions and gates. A mean of per-block entropies is not a pooled entropy; a mean distinct count is not a union of classes across prompts.

All linked P1 operands, component means and gain contrast must use the same block set. Each P5 comparator names its own exact block set. Qualified available-block summaries retain their intended/full list, actual list, missing reasons and changed scope. They cannot replace the six-block outcome. No automatic outlier removal, inverse-size weighting or favorable subset search is allowed. [MET §§10-11; HERO §10]

### 3.6 Resampling and reproducibility

The method is fixed: 2,000 resamples of P whole paired prompt blocks, each of length P with replacement, equal-block mean statistic, seed 20260917, nominal 95% percentile endpoints at 0.025 and 0.975. Preserve the block's internal outputs and shared-call dependencies; do not resample candidate rows or text pairs.

The minimum P=2 permits a nontrivial calculation; it is not an adequacy claim. With one block, show its descriptive contrast and unavailable block interval. Unsupported cross-block shared history or unresolved dependence can withhold an interval even with six rows named blocks. Do not silently substitute a different cluster estimator.

For sorted zero-indexed replicate means, `h=(B-1)*q`, with linear interpolation between adjacent ranks. At B=2000 the ranks are 49.975 and 1949.025. Integer ranks select the exact member. Do not delete problematic replicates or lower B to fit a limit.

Use one index manifest for linked P1 gains and contrast on the same ordered block set. The proposed implementation also reuses that manifest for other linked quantities on the identical set, including both eligible P5 comparators, while retaining separate endpoint identities. A different subset gets its own explicitly identified replay and cannot impersonate the full target.

Record the integer seed, actual RNG algorithm/runtime version, block order, every resample index or an equally complete replay record, B, quantile rule, statistic and their hashes. Replay validates these bindings before using the indices. The numeric code never evaluates a supplied expression or deserializes an executable random-generator object.

For this fixed six-wording suite, use **`prompt_resampling_sensitivity`**. Do not label the range population confidence, familywise confirmation or total model uncertainty. It conditions on the recorded within-block outcomes and leaves schema, label and generation uncertainty separate. [MET §11.3; HERO §10.2; VF §§5.4,6.2]

### 3.7 Outcome rules and meaning

After the required endpoint eligibility and full-suite interval exist, positive-direction retention means `mean>0 AND lower>0`; negative-direction retention means `mean<0 AND upper<0`. Equality with zero satisfies neither rule. Test tolerances do not create an effect-size threshold or redefine scientific zero. Use unrounded values and withhold numerically unstable signs pending correction.

| Question | Adopted operational rule |
|---|---|
| P1 | `supporting` when both surface gain and gain contrast retain positive directions; `contrary` when either retains a negative direction; otherwise `inconclusive`. Missing required eligibility or interval gives `not_evaluated`. |
| Each P5 comparator | Positive retention -> `supporting`; negative retention -> `contrary`; other evaluable results -> `inconclusive`; missing an actual prerequisite -> `not_evaluated`. |
| Full P5 | Both eligible and supporting -> `supporting`; both eligible and at least one contrary -> `contrary`; both eligible, no contrary and at least one inconclusive -> `inconclusive`; either not evaluated -> `not_evaluated`. |

Mixed P5 results are explicitly reported as mixed comparator behavior, while the full-pattern field keeps VF's four-value vocabulary. No fifth top-level `mixed` outcome or numeric overall score is added. An observed tie does not prove equivalent capabilities.

P1's valid-only sensitivity or quality deterioration can qualify a supporting all-view pattern without replacing it. A positive gain contrast made from two declining diagnostics cannot establish a surface increase. P5 breadth outside its quality band remains descriptive evidence without a matched-quality verdict.

Baseline surface distance >=0.95 activates `surface_proxy_near_ceiling`. Reaching all eight registered classes produces a registry-ceiling note. These flags qualify the interpretation but do not change the direction rules, replace the proxy, create classes or justify extra sampling. Show all registered primaries together and keep all secondary outputs secondary.

For a fixture, an outcome is a conditional test of the rule on stipulated evidence, with `fixture_only` scope and no empirical validation. For nonfixture data, a positive arithmetic pattern cannot bypass missing independent evidence or registration. Preserve descriptive directions separately when the evidence-qualified outcome is `not_evaluated`. [VF §§6-7]

### 3.8 Integrity, correction and scope

Retain EC-001's Structural Validity, External Presence, Source Integrity, Tail Retention and Corrective Capacity. They are conjunctive for an operational-openness claim; no scalar average substitutes for them. A narrow offline comparison does not require inventing live deployment evidence, and missing such evidence must not block fixture development.

Keep anomaly originals/references, uncertainty and dispositions. `unclassified` can mean several different evidential problems and does not automatically establish novelty. Distributional reopening, structural reopening, classification correction and model recovery remain different events. None is inferred merely from a new hash, class name or favorable score.

A class/validity/text/selection correction rebuilds the actual dependent diagnostic subsets, pair counts, contrasts, block sets, ranges and outcomes. Re-evaluate all affected conditions symmetrically. An independence-only correction can restrict a claim without changing justified arithmetic. Old inputs and reports remain intact; the revised analysis gets its own identity and linkage. The same observations do not become a new confirmatory sample. [MET §14; EI §10; EC-001 §§5-7]

## 4. Engineering design submitted for approval

### 4.1 Extend the existing package

Use the standard-library, local-package approach already delivered. Add narrow modules rather than replacing the input/evidence/population stack.

| Responsibility | Proposed module | Existing interfaces reused |
|---|---|---|
| Typed comparison binding and supplied study facts | `structdet_bench/comparison_records.py` | `LoadedBundle`, tagged knowledge states, `EvidenceIndex`, frame/protocol and role records. |
| Text eligibility, normalization, trigrams and pair diagnostics | `structdet_bench/text_diagnostics.py` | Immutable artifact snapshots, existing accepted population membership and original association records. |
| Compatibility, endpoint gates, per-block contrasts and means | `structdet_bench/comparisons.py` | `CellPopulations`, `cell_metrics`, `prefix(..., mode="hero")`, evidence/validity ratios. |
| Paired-block resampling and exact replay validation | `structdet_bench/uncertainty.py` | Defined paired contrasts; no input acquisition or label admission. |
| Deterministic P1/P5 outcome routing | `structdet_bench/predictions.py` | Typed gate, contrast, range and material-role records; no model judging. |
| Comparison orchestration and report attachments | `structdet_bench/comparison_pipeline.py` | The already loaded bundle, accepted populations, current analysis tree and safe renderer. |

The existing `metrics.py` remains the M arithmetic authority. The default plan does not modify `inventory.py`, `populations.py`, `evidence.py`, `records.py` or the core metric formulas. Reuse their results rather than admitting labels twice through a weaker path. A discovered predecessor defect follows the corrective rule in §6.3.

Do not import `tests` into the runtime or introduce a circular dependency between the M pipeline and V modules. The M pipeline can invoke the V orchestration after it has established its immutable input and population context. V returns typed results and report content; it does not run M again from a serialized public report.

### 4.2 Versioned optional comparison extension

Proposed physical interface: an optional, explicitly named `analysis_config.extensions.comparison` object, with its own `comparison_schema_version: "0.1"`. The outer input/record schema remains 0.1. The validator owns all recognized fields and rejects malformed or unsupported versions at the affected comparison scope.

The object identifies an instance of the existing HERO design, not a programmable estimator. Its required semantic groups are:

| Group | Required contents |
|---|---|
| Identity | Comparison ID/version; profile `hero_sort_abc_v1`; actual material role inherited from the bundle. |
| Intended study | Ordered P01-P06 block IDs, each expected A/B/C cell reference, requested primary questions and companion views. Missing referenced cells retain explicit status. |
| Protocol evidence | References to registered prompt/conditioning content, model/deployment identity, planned controls and actual enforcement, interleaving/attempt policy, cap semantics and usage. |
| Evidence basis | Typed references to registration/exposure, scoped structural validation, core/audit, integrity and correction records. No free `all_gates_passed` switch. |
| Text method | Registered extraction version, encoding profile, proxy identity and actual Unicode-table identities. |
| Resampling | Procedure/version, seed 20260917, B=2000, probabilities and quantile convention, dependence assessment, and optional previously produced replay indices with their identity. |
| Calculation limits | Prespecified resource limits; no data-dependent threshold or sample budget. |
| Revision | Prior comparison/run references, changes and reason; no mutation instruction. |

Exact field spelling and examples are documented in `COMPARISON_FORMAT.md` in Step 2. This plan fixes their meaning and bounded profile. Instance cell IDs can differ; their block/condition roles must match explicit declarations. Do not infer A/B/C from filenames or sort rows to manufacture order.

Use existing typed evidence payloads and their passive `extensions` for additional structured study facts. Keep original source artifacts and versioned transformation links. New schema support does not auto-complete hidden controls, pretraining exposure or independent review.

An absent comparison extension follows the legacy M-only path with its existing absent-V boundary. A present valid extension explicitly requests the new path. It cannot activate provider calls, candidate execution or arbitrary plug-ins. An unsupported extension cannot be silently ignored while claiming the requested comparison succeeded.

### 4.3 Text, Unicode and numerical implementation choices

The first physical profile consumes already extracted UTF-8 output artifacts. References must resolve to the same immutable byte snapshots and identities used by the record layer. A stored raw-response span may verify extraction; it cannot silently create a repaired output. Text parsing is passive.

Use versioned built-in Unicode property data: category lookup from an explicitly recorded standard-library Unicode database, with a separately pinned `White_Space` interval table in `text_diagnostics.py`. Freeze and test the exact table/versions before evaluating a comparison. Do not silently substitute the host default when the input requests another version. This is a representation of MET's tokenizer, not a new tokenizer choice.

Use collision-proof tagged boundary symbols. Retain exact integer intersection/union counts and exact structural pair counts. The proposed reference arithmetic uses rational values for finite pair means, differences, equal-block means and linear-interpolated quantiles where representable within the declared resource bound. This makes cancellation and the strict zero boundary inspectable. Store the public finite numeric value together with exact-ratio evidence or a pinned exact intermediate when applicable. No public arbitrary-precision object or executable serialization is required.

The adopted `1e-12 + 1e-10 * abs(expected)` tolerance remains a noninteger test/range convention, not a scientific decision margin. Exact integers, memberships, fractions and threshold inclusions must match exactly. Do not derive expected results by calling production diagnostics or the renderer.

Proposed default additional V limits are 100,000 surface lexical units per realization, 100,000 eligible pairs per cell/view diagnostic, 100,000,000 cumulative trigram-set elements visited across pair operations in a comparison run, and 131,072 bits for a retained exact numerator or denominator. Preflight the known work where possible and account for the actual work consistently. These are engineering ceilings, not scientific cutoffs. They may be overridden only through a recorded configuration fixed before calculation, within validated implementation limits.

On a limit failure, withhold affected V results and record the limit and retained scope. Do not cut a text, omit an expensive sample, subsample pairs, renormalize the remainder or silently switch to floating/approximate estimators. Supported M results and unrelated V endpoints remain usable. Reuse of identical snapshot/trigram calculations may reduce work; it never reduces observation multiplicity or pair denominators.

### 4.4 Resample transport

Proposed generator: a private `random.Random(seed)` instance with a recorded implementation/runtime version, using `randrange(P)` to generate each of P indices for each of B=2000 replicates. Do not use the process-global RNG or a hidden seed. This is an explicit engineering choice under MET's recorded-RNG requirement.

Persist the complete zero-based index matrix, ordered block identifiers, method identity, seed, B, quantile definition and hash in `run_manifest.json`. The comparison report references it and reports the interval scope. A replay consumes validated integer indices instead of depending on a future RNG implementation reproducing them.

All linked P1 quantities use the same row of indices at every replicate. Replaying a corrected outcome on the same block set may reuse the registered index matrix, but must recompute the replicate statistics. If block membership or eligibility changes, the previous matrix cannot be silently rebound to another list; create an explicitly scoped new analysis or withhold the full target.

### 4.5 CLI and report integration

Retain the existing commands:

`python -m structdet_bench validate --bundle <bundle.json>`

`python -m structdet_bench analyze --bundle <bundle.json> --output-dir <new-directory>`.

An explicitly supplied comparison extension activates V analysis in `analyze`. No additional `compare` command is required by this phase; the historical unsupported-command tests can remain intact. `validate` checks declarations, identity and record relationships without calculating distances, bootstrap statistics or prediction outcomes.

The output remains exactly `report.json`, `report.md`, and `run_manifest.json`, through the existing no-overwrite writer. Embed replay data in the manifest rather than weakening that writer to accept arbitrary filenames.

Populate the existing eight-section reporting structure. RF-21 through RF-28 become real V results when requested and supported; other RF groups retain their M/evidence/revision role. A V-enabled report uses an explicitly versioned additive report contract. The M-only path preserves its previous supported semantics and absence states. Historical reports are never overwritten. Re-running under changed source-code fingerprints may change run IDs and metadata without changing the M arithmetic; do not claim cross-version byte identity.

Declare the selected report profile explicitly. Legacy M-profile absence records describe that profile, not the capabilities of the entire newer executable. A V-enabled report uses `not_requested` for an omitted optional calculation, `unavailable` for missing prerequisites, `undefined` for a known empty mathematical denominator, and `deferred` only for D capabilities. Current capability metadata must not say the implemented V layer is globally unimplemented. Any genuinely progression-specific old assertion follows the narrow maintenance rule in §6.2.

Extend the fixed software-fingerprint inventory to every new runtime module and Unicode table that affects comparison results. Record proxy and RNG versions, exact block/pair identities, gates, all primary outcomes, qualifications and resample replay references. Pair/trigram tokens and unrestricted program text are not automatically printed. The audit link can use sample IDs and hashes without publishing private evidence or identity mappings.

Maintain processing exit codes: 0 for correctly processed supported/restricted/undefined results, including a contrary scientific pattern; 2 for input/configuration contract violations; 3 for unexpected local I/O/internal failure. A material evidence limitation can produce `not_evaluated` with processing success. A malformed input is not converted into a successful empty study. Each unaffected calculable scope is retained with the error clearly exposed.

### 4.6 Test and history organization

Create `tests/phase2_matrix.json`, `tests/phase2_helpers.py`, and `tools/run_phase2_checks.py`. The new matrix references the exact predecessor matrix and scientific rows; it does not repurpose the Phase 1 raw `current_step=3` snapshot or overwrite effective Phase 1 Step 7 history.

The Phase 2 runner performs ordinary complete discovery, retains concrete executed method IDs, and evaluates both the preserved M gate and new V/engineering bindings. Existing `tests.helpers.load_matrix()` and the Phase 1 gate can be reused without relaxing their M-only semantics. Phase 2 success is not established by setting a catalogue flag to implemented.

Keep all 54 VT, 40 TR, 36 RF and eight EC supplement identities. The Phase 2 matrix records 26 V-bearing VT obligations listed in §8.1, actual test bindings, M regression references and unperformed E/deferred D status separately. Do not erase the predecessor's correct statement that V was absent at that time.

## 5. File permissions

### 5.1 Read-only baseline

The twelve original planning/scientific files, three EC/source records, `PHASE_1_COMPLETION.md`, licensing bundle, original HF-00 inputs/expected values, eight-class transcription and old fixture oracles retain their approved bytes. Appendix A identifies them and the final archive. No PDF is redistributed.

`PHASE_2_PLAN.md` is also read-only once approved. A later plan amendment is separately versioned and approved. Original Phase 1 QA files and their past run IDs are preserved; new runs are captured under Phase 2 paths or in isolated replay copies rather than replacing history.

Step 1 may stage and publish **exact existing bytes** for every project entry under `structdet-bench/` in the pinned Phase 1 final archive. This is the exhaustive synchronization input manifest, not a permission to invent new Phase 1 files. Remote differences not explained by the accepted delivery require review before replacement.

### 5.2 Exhaustive ordinary write ledger

Paths are relative to the explicitly selected project root. Numbers refer to the Phase 2 steps in §7. New paths outside this ledger require a finding-specific amendment. Listed files are created when needed, not automatically all in Step 1.

| Exact path | Normal steps | Purpose and restriction |
|---|---|---|
| `README.md` | 1, 6, 8 | Factual handoff status, CLI examples and final bounded capability. |
| `INPUT_FORMAT.md` | 2, 3, 6 | Add cross-references/current interface details; preserve historical scientific meanings. |
| `COMPARISON_FORMAT.md` | 2, 3, 4, 5, 6, 8 | Explicit comparison encoding, method identities, states, gates and replay. |
| `structdet_bench/contracts.py` | 2, 3, 5, 6 | Add comparison/version vocabulary only; retain all M identities and source pins. |
| `structdet_bench/comparison_records.py` | 2 | Typed, passive instance configuration and evidence references. |
| `structdet_bench/text_diagnostics.py` | 3 | Exact approved text/proxy and pair accounting. |
| `structdet_bench/comparisons.py` | 4 | Endpoint-specific gates, same-unit contrasts and equal-block aggregation. |
| `structdet_bench/uncertainty.py` | 5 | Paired replay generation/validation, replicate statistics and quantiles. |
| `structdet_bench/predictions.py` | 5 | VF outcome routing, narrow/full scope and qualifications. |
| `structdet_bench/comparison_pipeline.py` | 6 | V orchestration on loaded M contexts; report attachments. |
| `structdet_bench/pipeline.py` | 6 | Explicit optional dispatch, provenance inventory and V report integration. |
| `structdet_bench/reporting.py` | 6 | Additive V serialization/rendering without M information loss. |
| `structdet_bench/cli.py` | 6 | Current help and declared optional-comparison behavior; no active commands. |
| `tests/phase2_helpers.py` | 1, 2, 3, 4, 5, 6, 7 | Trusted temporary builders and new matrix loading; no production imports from tests. |
| `tests/phase2_matrix.json` | 1, 2, 3, 4, 5, 6, 7, 8 | Requirements, real bindings, authorization history and scope records. |
| `tools/run_phase2_checks.py` | 1, 7 | Current-stage/full V gate, predecessor M regression, real QA recording. |
| `tests/test_phase2_gate.py` | 1, 7 | Empty/partial/missing/failed gate behavior, catalogue fidelity and history. |
| `tests/test_comparison_records.py` | 2 | Encoding, identity, roles, controls, pilot and material distinctions. |
| `tests/test_text_diagnostics.py` | 3 | Tokenizer, property versions, exact pairs, missing text and limits. |
| `tests/test_comparisons.py` | 4 | Group/frame/control/quality gates, operands, block sets and averages. |
| `tests/test_uncertainty.py` | 5 | Seeds/replay, whole-block behavior, quantiles and dependence failures. |
| `tests/test_predictions.py` | 5 | All OF outcomes, strict zero, qualifications and evidence restriction. |
| `tests/test_phase2_pipeline.py` | 6, 7 | Complete A/B/C workflow, adverse fixtures and symmetric corrections. |
| `tests/test_phase2_reporting.py` | 6, 7 | All applicable RF/EC fields, parity, units, privacy and outcomes. |
| `tests/test_phase2_security.py` | 2, 3, 5, 6, 7 | Passive text/replay/metadata, safe outputs and bounded resource behavior. |
| `tests/fixtures/comparison_cases.json` | 2, 4 | Explicit incomplete/incompatible instance records and exact gate cases. |
| `tests/fixtures/text_oracles.json` | 3 | Fixed lexical-unit/trigram/pair expected values and version cases. |
| `tests/fixtures/resampling_oracles.json` | 5 | Independent toy draws, full replay checks and quantile expectations. |
| `tests/fixtures/prediction_oracles.json` | 5 | Faithful OF-01 through OF-14 and explicitly identified boundary extensions. |
| `tests/fixtures/comparison_variants.json` | 6 | Pinned full A/B/C fixture changes and independent expectations. |
| `examples/hero_abc/bundle.json` | 6 | Complete fixture study/selection/configuration with source and method pins. |
| `examples/hero_abc/records.jsonl` | 6 | Stipulated 72-call/360-position design and actual fixture realization records. |
| `examples/hero_abc/evidence.jsonl` | 6 | Explicit mock/fixture origin, scoped gate evidence and missing real E. |
| `examples/hero_abc/prompts.json` | 6 | Passive exact prompt-assembly material, loaded only as a declared artifact. |
| `examples/hero_abc/expected.json` | 6 | Independent count/text/contrast/outcome expectations, never production-generated answers. |
| `examples/hero_abc/text_01.txt` | 6 | Passive stipulated realization text. |
| `examples/hero_abc/text_02.txt` | 6 | Passive stipulated realization text. |
| `examples/hero_abc/text_03.txt` | 6 | Passive stipulated realization text. |
| `examples/hero_abc/text_04.txt` | 6 | Passive stipulated realization text. |
| `examples/hero_abc/text_05.txt` | 6 | Passive stipulated realization text. |
| `examples/hero_abc/text_06.txt` | 6 | Passive stipulated realization text. |
| `examples/hero_abc/text_07.txt` | 6 | Passive stipulated realization text. |
| `examples/hero_abc/text_08.txt` | 6 | Passive stipulated realization text. |
| `PHASE_2_COMPLETION.md` | 8 | Actual final evidence, disposition, limitations and later handoff. |

The eight fixture-text paths permit a compact complete study with shared byte-identical artifacts where separately identified occurrences legitimately repeat. A shared text file never establishes independent observations; the fixture supplies distinct planned occurrences and explicitly stipulated labels. Identical bytes under the same fixed frame must not receive contradictory deterministic class assignments just to manufacture a desired test outcome. Additional adversarial texts and complete heterogeneous study arrangements may be materialized by trusted test helpers in temporary directories, never by runtime instructions in a bundle.

No routine change to `pyproject.toml`, package version, `__init__.py`, `__main__.py`, `.gitignore`, the secure writer, original test helpers, Phase 1 matrix or Phase 1 runner is necessary. No new dependency or release version is implied.

### 5.3 Named generated verification outputs

The following are generated by actual authorized preflight/tests or reporting, not hand-authored success claims:

| Exact output | Purpose |
|---|---|
| `artifacts/phase2/baseline_reconciliation.json` | Pinned archive/files, accepted source commit, remote/local differences and exact synchronization outcome. |
| `artifacts/phase2/baseline_test_results.json` | Actual predecessor replay in a disposable copy; no rewriting Phase 1 history. |
| `artifacts/phase2/test_results.json` | Append-retained current-stage/full-scope QA journal with actual method outcomes. |
| `artifacts/phase2/test_output.txt` | Actual console record with preceding relevant runs retained. |
| `artifacts/phase2/hero_abc/report.json` | Generated complete comparison fixture report. |
| `artifacts/phase2/hero_abc/report.md` | The corresponding human-readable report. |
| `artifacts/phase2/hero_abc/run_manifest.json` | Inputs, software/method pins, index replay and output hashes. |
| `artifacts/phase2/verification_manifest.json` | Actual final file/replay/remote checks and limitations. |

Temporary test inputs and replay workspaces may be created only by trusted tests and removed or preserved as explicitly identified verification evidence. User analysis outputs use their separately chosen new directory, never these repository QA paths by automatic default.

Large complete journals may remain in a companion archive with hashes and explicitly labeled repository summaries, as in Phase 1. Summaries must retain truthful run identities, statuses and access limitations. A staged blob, a constructed tree or an archive path does not establish a branch commit. Remote publication evidence is recorded separately after successful read-back. Self-referential hashes are not fabricated.

## 6. Execution discipline and maintenance

### 6.1 Step records and approvals

Each step delivers its actual changed-file list, prerequisite check, commands run, test outcomes, scope limits and remaining blockers. The matrix records requirements/bindings; generated journals record executions. A short handoff note is sufficient. No new planning document is required for every step.

Stop at the authorized boundary. Later steps are not authorized because the earlier step passed or because their code would be convenient. Missing a real model account, actual independent reviewers, another toolkit or favorable P1/P5 data does not prevent authorized software implementation.

### 6.2 Preserving existing tests without permanent historical-state failures

The original 503 test identities and their assertions about science, arithmetic, evidence and safety remain regression obligations. The new comparison path is opt-in so legacy M-only tests of absent V results can continue to test that specific path.

If a preserved test explicitly asserts a global development stage, a fixed implementation-file inventory or universal nonexistence of V functionality, the following narrow maintenance is authorized by approval of this plan: revise that assertion to check the historical M-only profile and its preserved delivery record, plus a separate assertion for the now authorized V-enabled profile. Keep the same test ID, underlying scientific/security property, original oracle and failure sensitivity. Do not merely delete the old assertion, remove the test from discovery or replace it with an implementation output as oracle.

This exception can affect existing `tests/test_scaffold.py`, `tests/test_metrics.py`, `tests/test_pipeline.py`, `tests/test_reporting.py`, `tests/test_populations.py`, `tests/test_integrity_records.py`, and `tests/helpers.py` only when an actual failure demonstrates that exact progression conflict. Record before/after, the failing requirement and replacement coverage in the Phase 2 journal/matrix. It does not authorize changing `tests/phase1_matrix.json` or rewriting earlier approvals. A different defect uses §6.3 or needs an amendment.

### 6.3 Corrective exception

During Steps 2-7, a demonstrated integration defect may be repaired in an already-created file from this ledger or an existing Phase 1 implementation/test file that the new path directly depends on. Record a finding ID, source requirement, exact paths, minimal failing case, reason for the repair, before/after evidence and regression scope. No new function outside the phase, no altered denominator, class meaning, primary endpoint or evidence requirement is authorized by this exception.

Do not use the exception to implement future capabilities earlier than their step. Required behavior with an ambiguous scientific specification returns to owner review instead of being decided by a patch.

**Step 8 permits no production, test, fixture or oracle repair.** A final audit finding returns to the appropriate repair step, followed by regression and a renewed final audit. Administrative completion cannot turn a failing code path into an accepted one.

## 7. Step-by-step implementation

### Step 1. Reconcile the Phase 1 baseline and establish Phase 2 verification

**Prerequisites:** This plan approved; explicit Step 1 instruction; access to the identified final local archive and target repository.

**Read:** COMPLETE1, PLAN1, Appendix A, current repository branch/tree, predecessor matrix and its actual journals.

**Allowed writes:** Exact Phase 1 staging/publication from §5.1, Step 1 rows in §5.2, and named §5.3 preflight/QA outputs. No Phase 2 runtime module.

**Work:** Confirm archive integrity and every staged file's identity. Replay the predecessor full tests/M gate in a disposable working copy. Reconcile the live repository against the accepted final local tree. Publish missing Step 7 code/tests and Step 8 documentation as separately reviewable, content-exact commits with no history rewrite; preserve or explicitly resolve any intervening changes. Read back the branch, commit and complete tree and compare bytes or Git blob identities to the exact local manifest. Retain publication limitations rather than guessing success.

Then establish the Phase 2 matrix, trusted helper and runner. Preserve all original catalogues and E/D boundaries. Enumerate all 26 V obligations, new engineering checks and concrete bindings as they actually become available. The full Phase 2 gate must fail for missing implementation even if its initial harness tests pass. Validate empty discovery, missing/duplicate/unexecuted/skipped/expected-failure bindings and the distinction between stage acceptance and final V completion.

**Acceptance:** The exact Phase 1 baseline is identified locally and in the confirmed remote history; its predecessor checks actually pass in the recorded environment; all pending differences have a documented disposition. Phase 2 scaffold checks pass; the full V gate remains incomplete with its real missing obligations. No fabricated baseline SHA or altered approved hash.

**Stop:** Deliver preflight and harness results. If exact remote synchronization is still unresolved, stop before Phase 2 runtime development and report the specific missing artifacts/action. Existing authority covers completion of that delivery; no user-supplied backup is required when the pinned archive is available.

### Step 2. Implement explicit comparison records and study bindings

**Prerequisites:** Step 1 accepted, including baseline reconciliation, or an authorized dependent batch.

**Read:** DEF; MET §§3-4,10.1; HERO §§7-10; VF VT-03/14/24/34/35/47; EC-001 §§3-6.

**Allowed writes:** Step 2 ledger rows and actual QA outputs.

**Work:** Implement the optional typed comparison extension, block/condition/cell references, profile/version checks, material role, requested/enforced controls, resource meanings, registration/exposure and scoped evidence links. Preserve a missing expected cell rather than silently shortening the main block list. Check exact prompt assembly and A/B equality against supplied content or explicit verified-byte records, with unresolved material exposed. Store all declared deviations without automatically calling them causal control.

Represent endpoint gate inputs without computing a distance or a scientific verdict. Use existing evidence records for independence/validation claims. A user-supplied Boolean cannot substitute for those records. Keep unrelated M metadata and supported inventory usable when a comparison extension is malformed, while the requested comparison reports a contract failure.

**Acceptance:** Correct and malformed extensions, incompatible versions/frames, duplicate roles, changed cap semantics, unsupported B temperature, pilot contamination, post-inspection registration and unknown deployment controls have explicit scoped outcomes. A/C facts survive an unusable B binding where independently sufficient. All relevant M tests still pass. No tokenizer, contrast, bootstrap, outcome or report renderer is implemented early.

**Stop:** Deliver `COMPARISON_FORMAT.md`, record validation, tests and current bindings.

### Step 3. Implement original-text, all-pair and within-class diagnostics

**Prerequisites:** Step 2 accepted.

**Read:** MET §§8-9,12.4; HERO §8.1; VF VT-31/32/33/36; existing artifact association and snapshots.

**Allowed writes:** Step 3 ledger rows and actual QA outputs.

**Work:** Freeze and identify Unicode tables; implement the exact tokenizer, noncolliding boundary markers, trigram sets, text eligibility, all unordered pairs, same-class pair groups, Q, per-class means and pair-weighted aggregate. Reuse existing accepted IDs; never infer a structural label from the text. Retain original/normalized identities, per-sample text status, pair/sample counts, snapshot linkage and computation limits.

**Acceptance:** MF-11 yields 4/5. MF-12 yields Q=1/2 with the separate SCI relation. MF-13/14 preserve singleton/missing-text boundaries and original M counts. CRLF/CR normalization, case, comments, underscores, digits, Unicode categories/combining marks, boundary-like text, property-version mismatch, whitespace-only and one-unit input all have pinned expectations. Empty, inaccessible, malformed decoding and oversized text remain different outcomes. No silent pair subsampling or resource-driven sample removal. Production operations remain passive after loading.

**Stop:** Deliver diagnostic functions, exact text oracles, documentation and tests. No A/B/C inference or interval is produced yet.

### Step 4. Implement comparison gates, contrasts and equal-block summaries

**Prerequisites:** Step 3 accepted.

**Read:** MET §§10-11.2; HERO §§8-10; VF §§5.3,6.2-6.5 and VT-12/14/34-38/40/44/45.

**Allowed writes:** Step 4 ledger rows and actual QA outputs.

**Work:** Build per-endpoint compatibility and gate records, preserving requested and actual resources. Apply exact rational thresholds. Construct B-A surface gain, B-A structural-pair gain and G on identical eligible subsets per condition; C-A and C-B valid distinct-20 deltas separately. Add same-unit companion differences and class-aligned frequency tables without pooling prompt classes.

Compute equal-block means with complete intended versus explicit descriptive-subset distinctions. Preserve all linked P1 operands on a common block set. Missing groups cannot be backfilled; label/validity exclusions cannot change the original selected positions. No quality equalization by deleting successes. A proxy-text failure cannot globally veto P5.

**Acceptance:** Every VF §5.3 equality/below-boundary case passes its expected rule. The 19-realization and complete-unclassified cases differ. An otherwise sufficient P5 fixture with only proxy text removed keeps its count-based gate and values. Primary P1 remains separately qualified when its clean-quality diagnostics fail. Incompatible frame or endpoint-specific control failures preserve supported separate numbers. Same-unit differences and block means match independent expected fractions; no intervals or directional outcome labels are invented before Step 5.

**Stop:** Deliver gates, per-block outputs, attrition accounting and tests.

### Step 5. Implement paired replay and P1/P5 operational decisions

**Prerequisites:** Step 4 accepted.

**Read:** MET §11.3; HERO §§10.2-10.4; VF §§5.4,6-7 and VT-39-45/50; §3.6-3.7 above.

**Allowed writes:** Step 5 ledger rows and actual QA outputs.

**Work:** Generate/validate the fixed 2,000-row index manifest; preserve whole paired blocks and link all P1 components to one replay. Compute replicate means, exact specified quantiles and the correct sensitivity label. Preserve missing/dependent-block restrictions, numerical failures and all original operands.

Implement the four-value decision rules with strict zero signs. Keep two separate P5 comparators and the full-pattern result. Retain valid-only P1 sensitivity, clean-quality status, ceiling flags and descriptive values when the evidence-qualified outcome is unavailable. Fixture stipulations may exercise the route but cannot support a real-study claim.

**Acceptance:** MF-18's toy means and VF's quantile oracle match independently. Full replay has exactly 2,000 by P validated indices; corrupted indices, wrong block sets, inconsistent version/seed metadata, unknown dependencies and selective replica omission fail. One-block contrasts have no interval. Linked components replay together. All OF-01 through OF-14 give their specified outcomes and qualifications. Zero touching/straddling is inconclusive; precision instability is exposed; small magnitude is not described as practical importance. Contrary results pass the software tests when reported correctly.

**Stop:** Deliver uncertainty, decision modules, independent oracles and tests. No empirical study has been run.

### Step 6. Complete fixture-to-report and CLI comparison integration

**Prerequisites:** Step 5 accepted.

**Read:** HERO §11.2; TRACE RF-01 through RF-36; MET §14; EI §§10-11; EC-001 §§5-7; existing pipeline/report/security interfaces.

**Allowed writes:** Step 6 ledger rows, narrow progression maintenance under §6.2 when demonstrated, and actual QA outputs.

**Work:** Materialize the new 18-cell, 360-position A/B/C fixture with real passive text bytes, proper source/role declarations and independent expected results. Use explicitly marked illustrative texts and stipulated mechanisms/validity. The tool must not treat them as independently verified sorting programs or new model calls. Preserve the original HF-00 and HF-01 through HF-06 unchanged.

Connect the optional comparison path to `validate`/`analyze`, report tree and software fingerprint. Add real V results, gate/outcome evidence and complete replay identity. Populate all primary comparisons and source limits in both formats. Generate a new report directory with the existing three-file atomic transaction. Add complete adverse, mixed, absent-text, absent-control, missing-block and correction variants in temporary test material.

**Acceptance:** A fresh checkout can analyze `examples/hero_abc/bundle.json` and reproduce independently specified counts, distances, contrasts and decisions. This must test actual text-to-diagnostic calculation, not just pass hand-written summary bounds to the decision layer. A separate heterogeneous fixture exercises nondegenerate ranges and block pairing. Every original Phase 1 fixture remains valid in its M-only mode. `validate` performs no numeric comparison; unsupported active commands remain unavailable. JSON/Markdown share values, units, status, block sets, reasons and claims. Successful negative/inconclusive scientific results use processing exit 0; malformed inputs remain errors. Existing output and input bytes are not overwritten.

**Stop:** Deliver the complete V workflow and actual report artifacts. Do not mark final Phase 2 conformance complete before Step 7.

### Step 7. Complete integrated V conformance, safety and reproducibility

**Prerequisites:** Step 6 accepted.

**Read:** All implemented V requirements in §8, the Phase 1 M gate, EC supplement, complete file ledger and correction contract.

**Allowed writes:** Step 7 ledger rows, documented corrective repairs under §6.3, and actual QA outputs. No new scientific scope.

**Work:** Audit every V-bearing VT row and applicable TR/RF/EC responsibility against actual executed methods, including inherited record gates. Fill real coverage gaps instead of attaching one trivial test to unrelated requirements. Exercise both complete and missing/withheld report paths. Re-run all predecessor tests and the preserved M gate. Verify input snapshots, known unknowns, safe text/replay processing, no active operations, file/limit handling, software fingerprints, output transaction and correction dependency propagation.

Replay in a clean extracted directory without third-party site-package loading. Compare reports at identical input/configuration/method/software identities; allow only declared variable manifest fields. Read back the exact published implementation tree after authorized commits and distinguish that result from local execution. Preserve prior failures and finding-limited repair patches.

**Acceptance:** All 26 V obligations have real passing software/record-handling bindings; no applicable M regression or V/engineering requirement is unimplemented, skipped, expected-failed or unresolved. All original identities and E/D limits remain. Paired replay, proxy/table compatibility, full/partial endpoint gates and correction cases pass. Full Phase 2 V and predecessor M gates return 0. This does not establish E fulfillment or final owner acceptance.

**Stop:** Deliver integrated verification for review. A substantive security or scientific ambiguity remains a blocker at its actual scope.

### Step 8. Final audit and bounded completion handoff

**Prerequisites:** Step 7 accepted; all local M/V checks and remote implementation identity available, or any remaining delivery limitation explicitly unresolved rather than certified.

**Read:** This plan, actual matrix/journals, predecessor completion, source pins, fixture/report/replay manifests and current repository.

**Allowed writes:** `PHASE_2_COMPLETION.md`, factual README/COMPARISON_FORMAT closeout, administrative new-matrix completion metadata and actual QA outputs. No code, test, fixture or oracle repair.

**Work:** Recheck scientific/fixture identity, allowable changes, all M/V obligations, V report coverage, the eight EC supplements, output reproducibility and true E/D status. Re-run final checks and archive replay. Record local completion, repository delivery, owner acceptance and empirical status separately. Include the exact code/test/fixture identities, instructions, all limitations, unresolved matters and next authorized boundary.

**Acceptance:** No mandatory local software/record-handling requirement remains unmet. Completion explicitly distinguishes the finished offline comparison instrument from unperformed independent validation and actual model studies. The final repository commit is read back against the delivered tree, or remote delivery remains plainly pending. A locally complete phase must not be described as fully delivered on GitHub without that evidence.

**Stop:** Deliver completion and verified package for owner review. No Phase 3 plan, implementation, collection, hosting or empirical publication begins automatically.

## 8. Mandatory conformance and oracle inventory

### 8.1 All 26 V-bearing VT obligations

The IDs and scientific meanings remain those in VF §4. This table assigns their Phase 2 software portions; E portions are never marked fulfilled by these tests.

| VT | Phase 2 implementation/check | Principal steps |
|---|---|---|
| VT-03 | Calls, failed/retried attempts, intended positions and dependency groups remain correct in comparisons. | 2, 4, 6, 7 |
| VT-12 | Intended-group endpoints cannot use later groups to fill missing early positions. | 4, 6 |
| VT-14 | Incompatible/missing domains, horizons, schema/rubric meanings restrict affected comparisons. | 2, 4, 7 |
| VT-17 | Revisions recompute pair subsets, comparisons, means, intervals and decisions without new samples. | 6, 7 |
| VT-18 | Independence-only withdrawal updates claim scope while retaining justified arithmetic. | 4, 6, 7 |
| VT-19 | Text, replay, metadata and external references remain passive/private as required. | 2, 3, 5, 6, 7 |
| VT-20 | JSON/Markdown preserve all V result states, operands, units, reasons and evidence scope. | 6, 7 |
| VT-24 | Registration, actual exposure and post-hoc/re-analysis distinctions survive comparison reporting. | 2, 4, 6 |
| VT-31 | Exact proxy tokenization, versioned Unicode, normalization, boundaries and MF-11. | 3 |
| VT-32 | Common text subset, missing-text counts, singleton/within-class denominators and limits. | 3, 6 |
| VT-33 | Exact distinct-pair statistic and finite-count identity on the same text subset. | 3 |
| VT-34 | Deployment/control/cap/schema limitations; preserve a qualified C-A path when B is unusable. | 2, 4, 6 |
| VT-35 | Six exact openers, A/B byte equality, C clause, groups, interleaving, pilot and controls. | 2, 4, 6 |
| VT-36 | Exact extracted-text association and empty/absent/truncated/ambiguous cases, without repairs. | 3, 6, 7 |
| VT-37 | All exact per-endpoint coverage/floor/band boundaries, including text-independent P5. | 4, 6 |
| VT-38 | Correct operands/signs/units for P1, both P5 deltas and linked block sets. | 4, 5 |
| VT-39 | MF-18, full 2,000-index replay, mean statistic and fixed percentile interpolation. | 5 |
| VT-40 | One/missing/dependent blocks, equal weighting, explicit attrition and no pseudoreplication. | 4, 5, 6 |
| VT-41 | Fixed-suite sensitivity wording and degenerate ranges with limited evidential meaning. | 5, 6 |
| VT-42 | P1 joint directions, false-favorable contrast, ties and zero-straddling outcomes. | 5, 6 |
| VT-43 | Two P5 comparators, full-pattern routing, proxy-only failure and incomplete prerequisites. | 5, 6 |
| VT-44 | Adverse valid-only P1/quality diagnostics and P5 outside quality match remain visible. | 4, 5, 6 |
| VT-45 | Surface/registry ceiling flags; no secondary-endpoint or ontology substitution. | 4, 5, 6 |
| VT-46 | Complete original/variant M and full A/B/C V fixture-to-report paths, fields and correction. | 6, 7 |
| VT-47/V record gates | Actual supplied schema/core/audit/exposure/independence evidence limits the claimed comparison; test routing only. | 2, 4, 5, 7 |
| VT-50/V | Adverse results and measurement challenges get symmetric preservation/re-analysis. | 5, 6, 7 |

VT-01/02/04-11/13/15/16/21-23/25-30 and VT-51-54 retain their applicable M regression duties. Their relevant results also support V without changing the source scope labels. VT-48 and VT-49 remain actual E experiments, unperformed. D estimates remain deferred even after all V tests pass.

### 8.2 TR/RF and EC mapping

TR-16 through TR-24 carry the new proxy, pairing, controls, P1/P5, gates, aggregation and outcome behavior. TR-04/06-09/15/25-35 retain the necessary identity, evidence, scope, correction and reporting interfaces. Keep every original TR row and an explicit Phase 2 applicability rationale; no source row is removed because it was already implemented in M.

RF-21 through RF-28 must have active numeric/state/record tests, not merely existence of null slots. RF-01 through RF-20 continue to identify actual source scopes and counts. RF-29 through RF-34 and RF-36 carry integrity, uncertainty, correction, permissions, outcome limits and parity. RF-35 retains all D prerequisites without numerical implementations. Every applicable report field gets both a supported-content check and a missing/withheld-state check where meaningful.

Retain EC-C01 through EC-C08 as separately identified supplemental software duties. Extend their record/claim checks to V: five-condition evidence, correct artifact type, original anomaly links, distinct reopening effects, all ten disclosures, unknown expiry, and separation of evaluation items from generated samples. A passed supplemental software test is not EC independent-evidence fulfillment.

### 8.3 Independent oracle sets

| Oracle family | Required arrangement and expected behavior |
|---|---|
| Text and pairs | MET MF-11 through MF-14 and tokenizer cases. Explicit token/trigram/intersection/union values; same-subset Q and pair-weighting. |
| Exact gates | Every VF §5.3 boundary plus undefined denominators, complete-unclassified and incomplete-position cases. |
| Pair means | Include unequal within-class sizes so pair weighting differs from an equal-class mean. |
| Block arithmetic | MF-18's 0.1/0.3 means; same-unit contrasts with unequal row counts and deliberately missing paired conditions. |
| Quantiles | The independently constructed `v[j]=j/1999` array yields 0.025/0.975; clearly labeled as a quantile-only oracle. |
| Actual replay | A complete 2,000-row manifest and separately calculated expected means/quantiles, not just a repeat of the production RNG. |
| Prediction routing | All OF-01 through OF-14, including false-favorable P1, mixed P5, ties, missing evidence and quality-confounded breadth. |
| Actual end-to-end | Full text-bearing A/B/C inputs with independent expected calculations; at least one heterogeneous block arrangement exercises nondegenerate sensitivity. |
| Re-analysis | Class/validity/text/evidence changes, same observation IDs, changed pair/block dependencies, preserved original reports. |
| Scientific limits | Matching arithmetic with missing E remains restricted; fixture-only supporting output never becomes an empirical result. |

The two-block and quantile-only fixtures are limited software checks. OF rows that stipulate means/bounds test only decision routing. They cannot substitute for the text-bearing end-to-end fixture or the complete replay test. A separately calculated oracle uses hand-counted sets, exact fractions or an independent enumerating path; it may not invoke the production diagnostic or report generator to manufacture its expected answer.

Do not promise a future number of individual tests. The mandatory obligations are identified now; actual method/subcase counts are recorded at execution. Repeated archive runs, 12,000 block-index entries and thousands of data combinations are not thousands of independently executed test methods or empirical observations.

### 8.4 Acceptance runner behavior

Proposed interface:

`python -B -S -m unittest discover -s tests -t . -v`

`python -B -S tools/run_phase2_checks.py --scope current`

`python -B -S tools/run_phase2_checks.py --scope phase2`.

These are future commands until implemented. `current` checks the explicitly authorized completed stage and all predecessor regressions; `phase2` requires the entire implemented V obligation set, new engineering checks and passing M gate. Neither succeeds with empty discovery or bindings to nonexistent/unrun methods. E records are inspected but E activities are not executed by the runner.

Each actual test result records requirement/scope, method, input/configuration/oracle identities, expected/actual disposition, relevant tolerance, environment and reason for failure/not-run. Missing tests, skipped mandatory checks, expected failures, overwritten history or mismatched frozen source rows must prevent final acceptance. Substantive outcomes remain independent of test success.

## 9. Security, reproducibility and delivery checks

The inherited passive-input boundary remains mandatory. Tokenizing a code file must never import, execute or compile it. Unsafe serialization formats, dynamic expression evaluation, shell strings and candidate-controlled file writes are outside the input language. New structured prompt/replay artifacts use the strict existing JSON rules and declared local snapshots.

Exercise hostile-looking comments, instructions, markup, URLs, malformed Unicode, embedded boundary-like strings and private locators. They remain data; logs and public reports do not expose private paths, raw bodies or actor mappings. Safe visible IDs do not prove independent origin. No networking or child-process activity may originate from analysis; trusted CLI tests invoke only fixed repository commands.

Do not weaken POSIX no-follow reads, hash checks, snapshot immutability, fixed output filenames, private output permissions or atomic no-replace publication. Resource limits never justify truncation. A privacy or security test does not certify an OS sandbox or immunity against every host-level adversary.

Reproducibility pins inputs, selected/pair/block membership, revisions, Unicode/proxy versions, seed/index replay, statistic, quantile method and all runtime implementation files. Compare JSON/Markdown byte-for-byte only under the same pins and supported environment. Recording time, interpreter/platform identity and intentional run IDs have declared meanings; they must not be broadly ignored to conceal numerical changes.

The current predecessor platform is Linux with Python 3.13.5. Reusing the standard-library design does not validate native Windows/macOS, another Unicode version, different filesystem semantics or a package installation path. New platform support requires its own design/authorization and evidence. No dependency installation, build, hosted CI or release is a hidden prerequisite for the direct-module path.

For repository handoff, use an explicit parent, non-destructive update and read-back. A successful local suite or a tool response creating a blob is insufficient. If the branch advances concurrently, reconcile rather than force-reset. Preserve exact content; do not retype shortened versions of large approved documents or matrices to work around a transfer limit.

## 10. Stop rules and blocker classification

| Situation | Required action | Permitted continuation |
|---|---|---|
| Planning-only request | Deliver this plan and stop. | Read/hash checks needed for planning only. |
| Missing/mismatched local baseline | Identify exact files, recover from the pinned available archive or request a specific authorized revision. Do not change expected hashes. | Unaffected document review. |
| Step 1 final Phase 1 remote handoff unresolved | Retain exact artifacts and outstanding differences; finish verified synchronization before V runtime edits. | Preflight/harness work within Step 1, not an assumed remote completion. |
| Concurrent repository changes | Preserve and reconcile them against explicit parent/file identities. | Nonconflicting authorized work. No force reset. |
| A scientific rule would change | Stop the affected behavior and seek a specific contract amendment with impact assessment. | Unaffected authorized implementation. |
| A path/function is outside the ledger or maintenance exception | Request a targeted amendment. | Existing allowed tasks. |
| Local class/text/evidence failure | Apply the existing scoped acceptance/subset/gate rules. | Supported other values and endpoints; no fabricated zero or top-up. |
| Actual independent E evidence absent | Withhold the affected empirical claim, expose the gap and preserve UD-006. | All authorized V development and explicit fixture/descriptive work. |
| Incomplete/dependent blocks | Withhold affected full-target intervals/outcomes; expose any separately allowed descriptive subset. | Supported cell results and narrower comparators. |
| Numeric sign instability/resource exhaustion | Record affected unavailability, actual count/limit and precision issue; no silent approximation or clamping of material errors. | Independent unaffected results. |
| Contrary/inconclusive scientific pattern | Preserve it and apply the same evidence standards and routing. | Correct software execution; no search for a favorable alternative endpoint. |
| Safety/privacy/overwrite failure | Stop affected processing, preserve safe evidence, repair under authorization and rerun regressions. | Unaffected review; no accepted security claim until resolved. |
| Mandatory M/V test missing or failing | Correct within scope or report the exact blocker. | No final local software-complete declaration. |
| Optional CI/build/provider access unavailable | Record absence; do not install or fabricate results. | Required local direct-module conformance. |
| Final audit needs code/test/oracle repair | Return to the relevant execution/repair step and repeat final audit. | Administrative review only until conformance is restored. |

Do not create scientific uncertainty tickets for ordinary unavailable API keys or the absence of other toolkits. Explicit unknown instance facts are data states, not reasons to invent defaults. Small refactors within the approved module scope need no new scientific approval when behavior, interfaces and tests are preserved.

## 11. Final deliverables and exit criteria

### 11.1 Deliverable set

The completed phase delivers the extended runnable package; current README, input and comparison formats; original M fixtures plus a separately identified text-bearing A/B/C fixture; independent text/gate/replay/decision oracles; all relevant tests; the Phase 2 matrix and runner; real generated comparison reports and manifests; retained execution/correction history; and `PHASE_2_COMPLETION.md`.

The repository and any companion archive must identify the same final code/test/fixture baseline. Complete large journals may be delivered in the companion archive with verifiable summary links. Theory PDFs and private user evidence are not bundled for public redistribution.

### 11.2 Final checklist

| Requirement | Evidence needed at exit |
|---|---|
| Exact predecessor and authority | Completed baseline reconciliation, source pins, preserved Phase 1 completion/history and approved plan. |
| M preservation | All applicable predecessor checks still pass, with no removed scientific assertion or hidden skipped test. |
| V method fidelity | MET proxy/pair arithmetic, exact gates, correct contrasts, same-block aggregation and fixed replay/quantiles implemented. |
| Correct outcomes | OF fixtures and end-to-end supportive/adverse/mixed/incomplete cases preserve VF's four-value decision semantics. |
| Complete catalogue coverage | All 26 V software/record obligations, applicable TR/RF mapping and eight EC supplement duties have actual passing bindings. |
| E/D separation | No actual model study, independent annotation or deferred estimator is claimed from software completion. |
| Practical operation | Existing CLI commands run the full comparison package and produce the three-file report set. |
| Adverse and missing data | No backfill, forced quality match, silent attrition, proxy-only P5 veto or scientifically meaningful zero replaced by a tolerance. |
| Corrections | All actually dependent V outputs are recalculated under new pinned evidence while old records remain intact. |
| Security/privacy | Passive input/replay, bounded processing, private-data protection and no-overwrite transaction tested. |
| Reproducibility | Clean extraction, full gate, original input hashes and report/replay checks in a recorded supported environment. |
| Delivery | Final branch/commit/tree read back against the local file manifest, or any remaining remote debt explicitly not accepted as complete. |
| Final review | Actual completion document supplied, with owner acceptance not pre-entered. |

No actual favorable P1/P5 result is required. A completed implementation can report `contrary`, `inconclusive`, or `not_evaluated` correctly. Software validation, empirical measurement, repository delivery and final approval each have their own evidence.

## 12. Review and immediate next action

The approval request covers this bounded V implementation, engineering interfaces, file ledger, runtime limits, replay representation, regression-maintenance rules and eight-step execution plan. All adopted scientific formulas, thresholds, primary endpoints, evidence distinctions and D exclusions remain unchanged.

After approval, the first action is **Phase 2 Step 1: exact Phase 1 repository reconciliation and the Phase 2 verification scaffold**. This plan does not perform that synchronization, start Step 1, write a repository file or authorize subsequent model collection.


## Appendix A. Verified planning baseline

### A.1 Archive and complete project identity

This archive supplies the exact implementation baseline. Its outer `verification/` directory preserves audit and history; its `structdet-bench/` directory contains the 67 project files. Source comparisons in this plan used those project bytes, not a reconstruction from earlier chat summaries.

| Item | Identity |
|---|---|
| Final local archive | `StructDet-Bench_Phase1_Final_Local.zip` |
| Archive size | 4,330,507 bytes |
| Archive SHA-256 | `9a38bbd53424ff80d4b8c745774df1b69d1e9bac400320c2fced00669fcaadf4` |
| Project file count | 67 |
| Project inventory SHA-256 | `381966c3d892b7b258cc11af72df1339c44c327fb654972fc6e302c56efd3e8f` |
| Last observed remote main | `8cd0fe659c9e515f76195164b8923395f8c4ca31` |

The project-inventory hash is defined over UTF-8 bytes of sorted lines `sha256 + two ASCII spaces + relative POSIX path + LF`, one line per file under `structdet-bench/`, with no directory entries. File contents are not normalized. This defines a reproducible complete inventory without a circular self-hash for this new plan.

The remote ref was read through the connected GitHub tool during preparation on 2026-09-18. It identifies the earlier Step 6 tree; the full local project inventory above is not claimed to exist on that branch. Step 1 must re-read the ref before any write.

### A.2 Scientific, authority and completion documents

| File | Edition / role | SHA-256 |
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
| `PHASE_1_PLAN.md` | 0.1 | `4a4137d1fa444c212af71740e439624c341ed485584ee3878e358f1e9424f704` |
| `PHASE_1_COMPLETION.md` | 0.1 | `8a93f1f0f3a31740c68b1d4f5661e073f7a8798cf47a7e1696207ccd579e09b5` |
| `EVALUATION_CLOSURE_ADDENDUM.md` | 0.1 | `31d2387ff2867e67e07adf60bca723b6783d0c3155b905d5477d2f844e1d9ce8` |
| `BASELINE_UPDATE_EC_001.md` | EC-001 | `c4a876c86b97bec68ab2691704fe37e40bbee16a94bfdf3a08c783e450c982a2` |
| `THEORY_SOURCES.md` | EC-001 source manifest | `33554654857da067870221d5d882fb5ef06cf005b8624079dda986085068d83e` |

The complete Phase 1 source, test, fixture, licensing and QA inventory is fixed by A.1. The following files are especially relevant to Phase 2 handoff and compatibility; their hashes are observations of the supplied final local tree, not authorization to replace a conflicting live repository file without review.

### A.3 Implementation and fixture anchors

| File | SHA-256 |
|---|---|
| `README.md` | `e1235a3662224073f43722a23dd1afad23b70624c97ee0ac17055b4bdc07ef32` |
| `INPUT_FORMAT.md` | `a1ede587cea09cfb231bb62980fe183276d24b4166524239bbcb5f040add4b97` |
| `tests/phase1_matrix.json` | `aea567fadfce3befa7c47a133e5bdf4cc27af413e16daddccfc405b67aacd1cf` |
| `tests/helpers.py` | `935f6cd9b5d34637da2a1b441152b5ce9e14467c4c8b2b71db8416291494d539` |
| `tools/run_phase1_checks.py` | `a187a0d676879341ca982cc36a16c6505a0f56bed3f08a64d2a7ffb6f5c6a68e` |
| `structdet_bench/contracts.py` | `a9d88b10d13afa0ddc967804d90b9ac48679eaf45e9aed5d5ead16880e93440a` |
| `structdet_bench/local_io.py` | `2e38fa7a23c398488a6691a47511526dc26c0109ea048bc85baa7bcceabb81f3` |
| `structdet_bench/records.py` | `c34bacbd1f0c7db490b596ff6334e8fe44c3d9425cbcaeb8473a0e99e0620046` |
| `structdet_bench/evidence.py` | `bdf8e3f1c7c190dcb0052202e2d90ed8dbf1a5c00826c7b5c784b1f96026fa61` |
| `structdet_bench/inventory.py` | `c9f03643944d3096aa276bd6bebc52df49cb9b907af254a317a843fb7c72d554` |
| `structdet_bench/populations.py` | `33d53b4698bfe69f9a2ae7acd5532e349d3db7773a45b7533e7378c3ee9044f1` |
| `structdet_bench/metrics.py` | `f4bbe94e755d2870cbf07c4488834aaa29d2adba16270c30f9549b23f4f69ff4` |
| `structdet_bench/pipeline.py` | `e2788f8349f6721faa89025435b14310727f302ba670de628afab5c0fc7140e6` |
| `structdet_bench/reporting.py` | `7214af51dad2e8bfaa92f4c17b09946b487e07c41248961212cc380a5ddd6361` |
| `structdet_bench/cli.py` | `43dd287b7dcc77335365ad730609229ffd663fbdfc7b231dd5d10eb5e8856de8` |
| `examples/hero_hf00/bundle.json` | `24660f96852e3fa14c933906fe2dfa904d5ca2a1cefc2cadd8d7fbfb51c77202` |
| `examples/hero_hf00/records.jsonl` | `a541b14061296e716056788c8354b9c3d97a34cdb7064cae310c0eb5df9d7535` |
| `examples/hero_hf00/evidence.jsonl` | `f1944e7642e57978bb8603b534bc38b15b61189345e46e7f1436410db723f966` |
| `examples/hero_hf00/expected.json` | `01649df89ea1bbc0c3201508b516112ad3ca4c6bfd971ac5b624eef95fb8b346` |
| `examples/sorting_reference_eight.json` | `f8fd72ee7c186fa16cc6f6706ace159d090e259ba73a979d743b0863c8a2950a` |
| `tests/fixtures/arithmetic_oracles.json` | `8ad46461b17f0128309cb37aafb9b8ce77d72a89b3fb589c65068f2a30cd65cf` |
| `tests/fixtures/hero_variants.json` | `2c60560f69673acce60f4f27e0e7943ca9aebd3feb3ccbed6b22c1b2603ab57c` |

### A.4 Theory source identities

| ID | Supplied file | Pages | SHA-256 |
|---|---|---:|---|
| SD | `The Structural Determinacy of LLM Generation_ Active Structure, Convergence Frontiers, and the Misreading of Randomness.pdf` | 27 | `357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32` |
| SI | `Structural Inbreeding in Synthetic Data.pdf` | 31 | `80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a` |
| EC | `Evaluation Closure Benchmark Inbreeding and the Design of Open AI Evaluation(1).pdf` | 16 | `002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950` |

The supplied PDFs retain their own licenses and are not part of the proposed source-code or fixture delivery. Their third-party references were not independently verified for this plan. The licensed project specifications and source manifest remain the implementation reference path.

## Appendix B. Source-to-plan navigation

| Adopted requirement | Primary location | Plan implementation location |
|---|---|---|
| Structural and realization distributions; observed capacity boundary | SD §§3.7,5,9; SI §§3-4,8 | §§1.3,2,3.2-3.3 |
| Exact lexical proxy and paired subsets | MET §§8-9; VF VT-31-33 | §§3.2-3.3,4.3; Step 3 |
| Main A/B/C setup and no replacement | HERO §§7-9; VF VT-03/12/34-36 | §§3.1,4.2; Steps 2,4,6 |
| Coverage and quality applicability | HERO §10.3; VF §§5.3,6.2; AF-002 | §3.4; Step 4 |
| Per-block P1/P5 and equal-block means | MET §§10-11.2; HERO §10.1 | §3.5; Step 4 |
| Resampling and quantiles | MET §11.3; HERO §10.2; VF §5.4 | §§3.6,4.4; Step 5 |
| Four outcomes and multiplicity boundaries | VF §§6-7 | §3.7; Step 5 |
| Role/evidence and openness | EI §§3-11; EC-001 §§3-7 | §§2.4,3.8,4.2,8.2 |
| Corrective propagation | SC §§10-12; MET §14; EI §10 | §§3.8,7,8.3 |
| JSON/Markdown and field mapping | HERO §11.2; TRACE §4; EC-001 §6 | §§4.5,8.2; Steps 6-8 |
| Predecessor preservation and pending publication | COMPLETE1 §§1,4,6-8 and appendices | §§1.4,5,6; Step 1 |

## Revision history

| Version | Change | Authorization and execution status |
|---|---|---|
| 0.1 | Initial Phase 2 offline V implementation plan, grounded in the final local Phase 1 baseline and existing MET/HERO/VF/EC contracts. | Planning requested by the owner. Proposed engineering choices await approval. No Phase 2 implementation, repository write, model experiment, candidate execution or spending performed by this document. |
