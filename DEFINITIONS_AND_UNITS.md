# DEFINITIONS_AND_UNITS

## StructDet-Bench: Measurement Vocabulary and Initial Field Inventory

| Field | Value |
|---|---|
| Document version | 0.1 |
| Date | 2026-09-16 |
| Phase / step | Phase 0 / Step 2 |
| Status | PROPOSED STEP 2 BASELINE; ready for Theory Owner review |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Scope authority | `PROJECT_SCOPE.md`, version 0.1, proposed |
| Decision authority | Theory Owner |
| Implementation authorization | None |

## 1. Reading this contract

The **[Source-derived]**, **[Engineering proposal]**, and **[Owner-approved decision]** labels have the meanings given in `PROJECT_SCOPE.md`, Section 1. A label governs its section unless another basis is stated. SD and SI identify the exact supplied editions registered in `PHASE_0_PLAN.md`.

This document owns terminology, units, and the initial human-readable field inventory. `STRUCTURAL_CLASS_CONTRACT.md` will own task-specific assignment and equivalence rules. `METRICS_SPEC.md` will own complete estimators, denominator procedures, uncertainty, and edge cases. Their future existence or approval is not implied here.

## 2. Source notation and software names

### 2.1 Primary measured objects

**[Source-derived: SD §§3.1-3.7, 5, 11; SI §§3, 6, 8]** The sources use the following objects. **[Engineering proposal; UD-002]** The software names in the final column make their meanings explicit without replacing the notation in either publication.

| Object | Source meaning / notation | Proposed semantic field |
|---|---|---|
| Context | SD: effective conditioning context `C`; SI: task context `C`. | `task_context`; `conditioning_context_ref` |
| Consequence horizon | `T`: the horizon over which relevant consequences are evaluated. | `consequence_horizon` |
| Analytic resolution | SD: `R`; SI: `ρ`. | `analytic_resolution_id`, `analytic_resolution_version` |
| Realization | `Y`: a complete answer, program, plan, or other declared generative realization. | `sample_id`, `output_ref` |
| Structural class | `Z`: the task-relative organization assigned to a realization. | `structural_class_id` |
| Structural map | SD: `π_(C,T,R)`; SI: `φ_(C,T,ρ)`. | `structural_schema_id`, `structural_schema_version` |
| Model state | SD: fixed model parameters; SI: model identity/state `M`. | `model_identifier`, `checkpoint_identifier` |
| Generation protocol | SD uses `D` for decoding/elicitation; SI uses an inference intervention `i` and related sampling specifications. | `generation_protocol_id`, `generation_protocol_version` |
| Reference registry | SI: `ℛ`, an independently constructed registry of required or relevant classes. | `reference_registry_id`, `reference_registry_version` |
| Inference intervention family | SD: `I`; SI: `𝓘`. | `intervention_family_id`, `intervention_family_version` |
| Diagnostic intervention family | SI: `𝓓`; SD describes broader probes, steering, transfer, and limited adaptation. | `diagnostic_family_id` |
| Recursive transition index | SI: `t` indexes documented recursive generations. | `recursive_round_id`, `transition_ref` |

The two context fields are a bookkeeping proposal. `task_context` records the problem, domain, constraints, and evaluation frame; `conditioning_context_ref` records the actual instructions, supplied evidence, history, and generated-prefix dependencies. This split must not conceal a change in the source variable `C`.

A divergence prompt changes conditioning. Comparing it with a baseline requires a declared common evaluation frame and compatible class meanings. Holding only a task name constant is insufficient.

### 2.2 Name collisions and units

**[Engineering proposal; UD-002]** Avoid bare `R`, `rho`, `D`, or `N_eff` as public fields when their meaning is ambiguous.

SD uses `ρ` for a stability threshold in §4.1, whereas SI uses `ρ` for analytic resolution. Use `stability_threshold` and `analytic_resolution` separately. SD's decoding protocol and SI's Gini-Simpson diversity or diagnostic family likewise require distinct names.

`T` must include a domain-appropriate horizon description and, where quantitative, a unit. A time limit, execution-step horizon, and narrative consequence horizon are different specifications. Output token count is not an automatic substitute.

Identifiers and schema versions are labels rather than measurements. A version number alone does not prove compatibility with another version.

## 3. Experimental and software units

**[Engineering proposal; UD-003, UD-005]** The hierarchy below separates computation from observation and statistical replication. SD §9.5 and the governing plan's Step 6 require sampling and prompt-level dependence to remain visible.

| Unit | Definition | Counting rule |
|---|---|---|
| Study | A named question, task suite, conditions, and analysis plan. | A study may contain several generation collections and analysis runs. |
| Analysis run | One execution of the measurement software against identified inputs and configuration. | Re-analysis creates a new run identity, not new model observations. |
| Analysis cell | Realizations sharing one compatible task/schema, prompt block, model-state specification, condition, and generation protocol. | Structural frequencies are formed within a cell and a declared analysis population. |
| Prompt block | A prespecified base problem used to compare conditions with their actual prompt variants recorded. | Repeated outputs from one block do not become additional prompt blocks. |
| Generation call / attempt | One recorded invocation of a generator, successful or failed. | Retries remain distinct attempts linked to their predecessors. |
| Raw response | The complete returned artifact from an attempt. | Preserve it when a response is split into multiple analysis samples. |
| Analysis sample | One prespecified realization `Y` with a stable sample identity. | A response may yield multiple samples only under the declared extraction rule. |
| Coordinated set / dependency group | Samples sharing a generation call, specification, history, or other recorded coupling. | Group membership is preserved; row count does not establish independent replication. |
| Structural assignment | A claim that a sample belongs to a class under one schema/resolution, with evidence and review status. | Re-labeling a sample produces a new assignment version, not a new sample. |
| Recursive round | A documented reproduction/selection/learning transition used by Layer B. | Additional inference calls and repeated analysis runs do not increment it. |

Within-cell calculation uses a sample inventory after declared record validation and extraction. Invalid input records, failed calls, and extraction failures remain in the audit inventory even when they cannot supply a class assignment.

A coordinated request for several mechanisms can legitimately yield several realizations, but its dependence structure remains different from separate single-answer calls. Grouping and resource accounting must travel with the samples. The final comparison and resampling units are selected in Steps 4 and 6.

## 4. Structure, assignment, validity, and grounding

### 4.1 Structural equivalence

**[Source-derived: SD §§3.2-3.6; SI §3.1]** Under the deterministic case:

\[
Z=\pi_{C,T,R}(Y),\qquad
 y_a\sim_{C,T,R}y_b\iff\pi_{C,T,R}(y_a)=\pi_{C,T,R}(y_b).
\]

SI writes the corresponding map as `φ_(C,T,ρ)`. The equality defines class membership under a specified map; validating that map requires consequence-sensitive evidence. Load-bearing distinctions change the declared relevant consequences when intervened upon or substituted.

The sources allow uncertain, hierarchical, overlapping, and probabilistic descriptions where a hard partition is inadequate. Classification uncertainty must remain visible.

**[Engineering proposal; UD-004]** v0.1 accepts hard assignments for cases resolved under the approved task contract. Unresolved and unclassified samples retain their statuses. A parser label, self-description, or embedding cluster cannot automatically become a validated structural class. Specific treatment of hybrids, novel mechanisms, and inconsistent pairwise judgments belongs to Step 3.

### 4.2 Four separate assessments

**[Source-derived: SD §§3.2, 6.5, 9.1; SI §§3.1, 3.4, 8.5, 12]** Structure, validity, consequences, and independent grounding have different evidential requirements.

**[Engineering proposal]** Preserve them as separate records:

| Assessment | Meaning | What it does not establish by itself |
|---|---|---|
| Structural assignment | Which class the realization instantiates at the declared resolution. | Correctness, task success, or independent origin. |
| Output validity | Whether the realization satisfies the declared validity rubric, with its scope of testing stated. | Unique mechanism, full model capacity, or success outside that rubric. |
| Task-success observation | A recorded result on a particular execution, test case, or consequence check. | Universal correctness or algorithm-family membership. |
| External grounding | The evidence or constraints connecting a claim, class, or result to a reference outside the relevant evaluated lineage. | Independence merely from a human/synthetic label or a different provider name. |

For example, identical returned values can support a tested outcome while leaving algorithm-family membership unresolved. A recognizable mechanism may still be implemented incorrectly. A success observation becomes part of a validity assessment only through the declared rubric.

### 4.3 Reference registry and structural exogamy

**[Source-derived: SI §§3.4, 8, 9]** A reference registry records independently constructed required or relevant classes for a task. Structural exogamy requires independent difference to enter, survive processing and selection, and affect the generative lineage. Stored or nominally external material alone does not establish effective presence.

**[Engineering proposal]** Registry coverage always means coverage of that identified registry. It is not an assertion that the registry exhausts every valid mechanism. Record the registry's origin, version, tail designation, and validation evidence. A newly encountered candidate may trigger adjudication or revision; it must not be silently forced into “other” and treated as a verified new class.

## 5. Analysis populations and evidence status

### 5.1 Proposed population views

**[Engineering proposal; UD-003]** Each distribution result carries an `analysis_population` identifier and its denominator. v0.1 exposes two separate views, with unavailable results shown explicitly when evidence is inadequate:

| View | Membership | Interpretation |
|---|---|---|
| `classified_all` | Samples with hard class assignments accepted under the declared assignment-evidence policy, regardless of assessed output validity. | Distribution conditional on accepted classification. |
| `classified_valid` | Members of `classified_all` additionally assessed as valid under the declared rubric. | Distribution conditional on both accepted classification and assessed validity. |

The acceptance policy must distinguish fixture, provisional, and adjudicated evidence. A fixture run can operate on declared fixture labels; it cannot upgrade those labels to independently validated measurements. Step 3 defines the permissible assignment states, and Step 5 defines evidence gates.

Neither view silently represents the full generated population when some outputs are unclassified or validity is undetermined. Counts for exclusions and unresolved cases accompany both views. Per-condition valid-only comparisons must not conceal differences in failure or exclusion rates.

For a chosen population `A`, let `n_A` be its number of samples, `c_z` the number assigned to class `z`, and `p_hat_A(z)=c_z/n_A` when `n_A>0`. This conditional empirical distribution supplies the first-release summaries. It does not estimate an unrestricted model repertoire merely by being normalized.

### 5.2 Accounting and missingness

**[Engineering proposal]** Classification status, validity status, and generation outcome are separate axes. Counts within each axis reconcile to that axis's declared inventory. A sample can be both invalid and structurally classified, so those counts cannot be summed as if mutually exclusive.

Unknown, unavailable, failed, invalid, and unclassified cases do not become structural classes. A zero-class observation from an empty classified population must be labeled with that empty denominator; it cannot be interpreted as zero model capacity. With no classified samples, distributional quantities have no estimable value. Step 4 owns the exact report behavior.

A new content hash does not prove a new observation, and repeated content does not prove a duplicated record. Preserve both sample identity and content identity.

## 6. Support semantics

### 6.1 Finite observed occurrence

**[Source-derived: SI §3.3; SD §5.1]** SI defines finite observed support by appearance. SD's displayed observed-support definition uses an empirical-frequency threshold. Both depend on the generation and sampling protocol.

**[Engineering proposal; UD-002]** Preserve two explicit views under the selected population:

\[
S_{\mathrm{obs,occ}}(A)=\{z:c_z>0\},
\]

\[
S_{\mathrm{obs,freq}}(A,\tau_e)
 =\{z:\widehat p_A(z)\geq\tau_e\},\qquad 0<\tau_e\leq1.
\]

| Proposed field | Meaning |
|---|---|
| `observed_support_size` | Number of classes observed at least once; the SI occurrence convention. |
| `observed_support_size_thresholded` | Number meeting the declared empirical-frequency threshold; the SD-style thresholded view. |
| `min_empirical_frequency` | The threshold `τ_e`, explicitly tied to its denominator. |

An omitted empirical-frequency threshold leaves the thresholded view unevaluated. It does not default to zero or merge the views. Zero-count registry classes remain unobserved. Numerical boundary handling belongs to Step 4.

### 6.2 Expressible support and bounded interventions

**[Source-derived: SD §5.2; SI §§3.3, 8.1]** Expressible support concerns classes that a fixed model can produce at meaningful probability under an admissible inference-intervention family. The source quantity ranges over that family, subject to its probability threshold.

**[Engineering proposal]** A finite intervention study must distinguish:

- the set of interventions allowed by its design;
- the subset actually evaluated;
- classes observed under those evaluated interventions;
- classes supported as meeting a declared probability threshold under an approved estimator.

The empirical union of observed classes can document successful elicitation without estimating the whole thresholded support. Its descriptive name, when implemented, is `observed_intervention_union_size`; this field is deferred from v0.1. A thresholded expressible-support field requires an additional estimator and evidence contract.

Use `min_generation_probability` for a population-probability threshold. It must not be substituted for `min_empirical_frequency`. A single successful sample establishes appearance, not a specified reliable generation probability.

Prompting, tool use, or retrieval may be allowed inference interventions under the source definitions. Their contribution must be recorded. They cannot automatically establish that the same structure was accessible without those aids. Parameter-updating interventions change model state and require a separate study record.

### 6.3 Latent support and recovery

**[Source-derived: SD §§5.3-5.4; SI §3.3]** SD discusses recovery through stronger probes, steering, transfer, and limited adaptation. SI specifies diagnostic interventions on the existing model state and excludes simply injecting the missing solution. Both require stronger evidence than finite observed nonappearance.

**[Engineering proposal; UD-007]** No v0.1 field estimates latent-support size. These diagnostic boundaries remain separately recorded pending a future operational decision. A failed bounded search can be reported as failure under the named search, without declaring absolute representational extinction.

The support-inclusion hierarchy requires compatible interventions and thresholds, as stated in the sources. In particular, a class observed once may still have probability below an expressible-support threshold. Finite occurrence alone cannot certify the thresholded set inclusion.

### 6.4 Three forms of contraction

**[Source-derived: SD §5.4; SI §3.3]** Expression concentration concerns narrow ordinary generation with broader elicitation still possible. Accessibility collapse concerns failures of ordinary admissible elicitation despite stronger recovery evidence. Representational collapse concerns loss assessed through the stronger diagnostic framework.

**[Engineering proposal]** v0.1 can report observed concentration and differences between supplied conditions. It does not automatically assign these failure-state labels. Such labels require the corresponding intervention, diagnostic, and comparison evidence.

## 7. Quantities, units, and cataloged metrics

### 7.1 Core identities

**[Source-derived: SD §§3.7, 9.2; SI §§4, 5.3, 8.2]** Structural entropy and concentration describe different distributional properties:

\[
H_S=-\sum_z p(z)\log p(z),\qquad
\mathrm{SCI}=\sum_z p(z)^2.
\]

SD uses `exp(H_S)` as an effective structural count. SI uses `1/SCI`. The two source definitions are retained separately.

**[Engineering proposal; UD-002]** Use natural logarithms and the following names. First-release calculations use the conditional empirical distribution from Section 5; complete estimator behavior belongs to Step 4.

| Quantity | Proposed field | Unit / convention |
|---|---|---|
| Occurrence-based observed support size | `observed_support_size` | Count of classes. |
| Empirical-frequency-thresholded support size | `observed_support_size_thresholded` | Count of classes; threshold and denominator required. |
| Structural entropy | `structural_entropy_nats` | Nats; natural logarithm. |
| Structural Concentration Index | `structural_concentration_index` | Dimensionless. |
| Shannon-based effective count | `effective_support_shannon` | Effective classes; `exp(H_S)` using nats. |
| Simpson-based effective count | `effective_support_simpson` | Effective classes; `1/SCI`. |
| Gini-Simpson structural diversity | `gini_simpson_diversity` | Dimensionless; `1-SCI`. Reserved for the metric catalog and Layer B unless Step 4 selects reporting. |
| Structural distinct-k | `structural_distinct_k` | Count of classes among a declared k-sample selection/group. Selection and dependence rules required. |

The population, schema, and log base travel with derived effective counts. There is no public field named only `N_eff`. The logarithmic term uses the limiting convention `0 log 0 = 0`; this does not assign a distribution to an empty sample.

### 7.2 Realization variation and classification uncertainty

**[Source-derived: SD §3.7; SI §4]** For a deterministic structural map, the entropy chain rule separates structural entropy from residual variation within a structural class. SD calls the residual realization entropy; SI calls it implementation entropy. Both terms refer to variation remaining after fixing the structural class under the declared context and resolution.

For probabilistic assignment, the additional classification-uncertainty term must remain explicit. Human disagreement, uncertain class membership, and actual distributional diversity cannot be collapsed into one quantity.

**[Engineering proposal]** A lexical, token, hash-based, or within-class distance diagnostic gets its own observable name, normalization, and unit. It cannot be reported as exact `H(Y | Z,C,T,R)`. Step 4 selects the limited v0.1 proxy. P1 requires a prespecified comparison method; raw values in nats and an unrelated distance unit cannot be compared as growth rates without such a method.

### 7.3 Deferred metric vocabulary

**[Source-derived; engineering field separation as noted]** These definitions preserve the source catalog while leaving full estimator design outside Step 2.

| Quantity | Source meaning | Unit and required boundary |
|---|---|---|
| Load-bearing intervention effect | Change in a structural distribution under a matched, consequence-relevant intervention. SD §§3.5-3.6, 9.2. | Unit depends on the prespecified distance; no default causal interpretation from unmatched conditions. |
| Convergence frontier | Maximal stabilized resolution, or a frontier set for partially ordered resolutions. SD §4. | Resolution identifier/set; requires concentration and stability criteria. |
| Structural Half-Life, categorical null | Time for expected Gini-Simpson diversity to halve under the stated fixed-size closed-resampling model. SI §5.4. | Recursive rounds; requires the categorical assumptions and `n>1`. |
| Structural Half-Life, empirical | A fitted or interval-specific summary of measured diversity decline across comparable rounds. SI §8.3. | Recursive rounds; applicable fit and uncertainty must be stated. |
| External Recovery Rate | Fraction of a pre-intervention missing reference set recovered after an independently grounded, validated intervention. SI §8.4. | Fraction, or explicitly formatted percentage; undefined when the missing set is empty. |

**[Engineering proposal]** Keep empirical and null half-life fields separate. “Half-life” must not silently refer to halving Shannon entropy, support count, or task accuracy. Keep categorical sample size separate from token budget, dataset rows, and effective sample size; no automatic conversion is supplied by these sources.

ERR must preserve the evidence used to establish the missing set. Post-intervention appearance alone does not justify relabeling a finite sampling gap as restored representation. An intervention that directly pastes the target answer into the output fails SI's recovery requirement.

## 8. Metadata knowledge and evidence states

**[Engineering proposal]** Every metadata field that permits incomplete information carries a state independently of its value:

| State | Meaning | Example of the distinction |
|---|---|---|
| `known` | A value is supplied with its declaration/evidence basis. | Recorded temperature or an explicit statement that no seed was used. |
| `unknown` | The value has not been established from the supplied material. | Unrecorded upstream ancestry. |
| `unavailable` | A known access, exposure, or collection limitation prevents obtaining the value; a reason is required. | The collection interface did not expose checkpoint identity. |
| `not_applicable` | The field has no role under the declared design; a reason is required. | No recursive round in a fixed-model fixture demonstration. |

A known value can still be merely declared, provisional, or independently checked. Knowledge state and evidence-review status are separate. A literal `false`, zero, or empty reference set is meaningful data only when explicitly established; missing metadata cannot silently become any of them.

An explicit unknown value satisfies honesty requirements, but it does not supply a missing scientific prerequisite. For example, unknown checkpoint identity permits a descriptive sample audit while limiting a claim about a fixed model state.

## 9. Initial field inventory

**[Engineering proposal; UD-001 through UD-006 as applicable]** This is a human-readable semantic inventory. It is not an executable schema or a commitment to one storage layout. Fields may be normalized into linked records rather than repeated on every sample.

“Required” means a value is needed for the identified capability. “Explicit state allowed” means an unknown/unavailable value can be ingested, with the resulting capability limitation reported. Later steps may add justified task-specific fields without silently changing these meanings.

### 9.1 Run, task, and protocol records

| Field / field group | Meaning and requirement |
|---|---|
| `input_schema_version`, `run_id`, `analysis_config_ref` | Required identity of the input vocabulary and this calculation run. Software version is recorded when software exists. |
| `study_id`, `data_role` | Study link and designation such as fixture, pilot, or confirmatory collection. A role label does not establish validity. |
| `task_id`, `task_version`, `task_context` | Required problem/domain specification and constraints. |
| `consequence_horizon` | Required evaluation horizon and applicable unit. |
| `analytic_resolution_id`, `analytic_resolution_version` | Required structural distinction level. |
| `structural_schema_id`, `structural_schema_version` | Required for class-based calculations. |
| `reference_registry_id`, `reference_registry_version` | Required for registry-relative coverage, recovery, and the hero's preregistered reference design; otherwise explicit absence/status. |
| `model_identifier`, `model_family`, `checkpoint_identifier` | Generator identity with separate knowledge/evidence states. Exact checkpoint may be unavailable; fixed-state claims are then restricted. |
| `condition_id`, `generation_protocol_id`, `generation_protocol_version` | Required generation-condition identity. |
| `prompt_block_id`, `prompt_id`, `conditioning_context_ref` | Required links to the base comparison block and actual conditioning material; hidden or missing components are disclosed. |
| `decoding_settings`, `seed` | Recorded generation controls, including any unavailable controls. No defaults invented from a provider or model name. |
| `collection_window`, `sampling_plan_ref`, `budget_record_ref` | Collection timing, intended sample design, and actual resource accounting; required for corresponding comparisons. |
| `intervention_family_id`, `intervention_id`, `changes_model_state` | Conditional fields describing an intervention and whether it updates parameters. |
| `recursive_round_id`, `parent_state_ref`, `transition_ref` | Conditional Layer B fields; required for recursive-transition claims. |

### 9.2 Attempt and realization records

| Field / field group | Meaning and requirement |
|---|---|
| `attempt_id`, `attempt_status`, `retry_of` | Call history including failures and retries; explicit missing history limits attempt-level accounting. |
| `raw_response_ref`, `sample_id`, `output_ref` | Stable links from the received response to each registered realization. Sample IDs must be unique in their declared namespace. |
| `output_content_hash`, `extraction_rule_version` | Content identity and any rule that produces multiple realizations from a response. A hash verifies bytes, not truth or independence. |
| `generation_group_id`, `group_type`, `within_group_index` | Shared-call/set/history grouping and within-group position. Unknown grouping limits independence-sensitive inference. |
| `sample_order`, `shared_context_ref` | Recorded sequence and cross-sample context dependencies where applicable. |
| `completion_status`, `termination_reason` | Whether the intended output completed, was truncated, refused, or failed; detailed vocabulary belongs to the relevant task/input contract. |
| `selection_status`, `selection_reason` | Which preregistered analysis selections include the realization and why. No unrecorded post-result filtering. |

### 9.3 Assignment, validity, and evidence records

| Field / field group | Meaning and requirement |
|---|---|
| `assignment_id`, `assignment_version`, `sample_id` | Required assignment identity and target realization. |
| `structural_class_id`, `assignment_status` | Class value when assigned; explicit unresolved/unclassified treatment otherwise. |
| `assignment_method`, `assignment_review_status` | How the assignment was produced and whether it is fixture, provisional, or adjudicated evidence under the later contract. |
| `classification_uncertainty_ref`, `disagreement_ref` | Evidence of ambiguity or conflicting judgments; absence of a record does not establish agreement. |
| `validity_status`, `validity_rubric_ref` | Separate assessed validity and applicable rubric/version. |
| `task_success_observations_ref` | Concrete test or consequence observations underlying any validity judgment. |
| `evidence_refs`, `external_grounding_status` | Links to the supporting evidence and its assessed relation to an external reference. |
| `role_records_ref`, `lineage_records_ref` | Reference source, generator, extractor/classifier, adjudicator, and validator identities and relationships, including unknown ancestry. |
| `correction_ref`, `supersedes_assignment_id` | Links preserving revisions and affected prior assignments/results. |

Evidence records identify their source, method, referenced material, relevant location or test scope, and review status. Declared independent origin requires supporting records; role labels alone are insufficient.

### 9.4 Result records

| Field / field group | Meaning and requirement |
|---|---|
| `analysis_cell_id`, `analysis_population` | Required identity of the distribution being summarized. |
| `metric_name`, `metric_definition_version` | Unambiguous quantity and applicable estimator contract. |
| `value`, `unit`, `result_status`, `unavailable_reason` | Numeric result only when defined and supported; an unavailable result retains a reason. |
| `population_size`, `class_counts`, `classification_coverage` | Denominator and evidence needed to interpret frequencies. |
| `validity_summary`, `exclusion_summary`, `grouping_summary` | Separate reporting of task/evidence limitations and dependence. |
| `thresholds`, `uncertainty_method_ref` | Applicable thresholds and estimation procedure; no invented confidence interval. |
| `input_refs`, `evidence_status`, `permitted_claim_scope` | Traceability and the boundary of the result's interpretation. |

## 10. Comparability and revision rules

**[Source-derived: SD §§3.2, 5, 9.4-9.6; SI §§8-9]** Structural results depend on context, horizon, resolution, schema, protocol, and evaluation evidence.

**[Engineering proposal]** Default calculation preserves those distinctions. Pooling or differencing requires a declared comparability rule, including how any changes to prompts or schemas preserve the relevant class meanings. Lack of comparability blocks the comparison rather than the separate descriptive reports.

Schema or assignment correction creates a versioned record and identifies affected results for re-analysis. A re-analysis does not enlarge the original sampling budget. Pilot-informed changes remain visible and are separated from subsequent confirmatory evaluation.

Approval of Step 2 fixes the proposed vocabulary subject to the decision register. Step 3 must supply the structural-class contract, and Step 4 must complete the metric contract before affected implementation begins.
