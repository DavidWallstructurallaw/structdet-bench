# THEORY_TO_CODE_TRACEABILITY

## StructDet-Bench: Source, Contract, Planned Component, Test, and Report Links

| Field | Value |
|---|---|
| Document version | 0.2 |
| Record date | 2026-09-17 |
| Phase / step | Phase 0 / Step 8; corrective revision of the Step 7 mapping |
| Status | AUDIT-CORRECTED PROPOSAL; Step 8 owner acceptance pending |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Input baseline | Approved scope, definitions, structural-class contract, evaluation integrity, and hero specification v0.1; metric contract v0.1 with the separately identified Step 8 revision v0.2 pending acceptance |
| Approval evidence | Version 0.1 adopted in OA-007; this finding-limited revision remains pending under `UNRESOLVED_DECISIONS.md` v0.7 |
| Companion specification | `VALIDATION_AND_FALSIFICATION.md`, version 0.2, audit-corrected proposal |
| Decision authority | Theory Owner |
| Authorized revision | AF-003 in PC-01; existing test links and report groups are retained |
| Implementation / repository / collection / execution authorization | None |

## 1. Authority and how to read the mapping

**[Step 8 audit revision: AF-003]** OA-007 adopts the delivered Step 7 version 0.1 and authorizes the integrated audit. Version 0.2 clarifies PC-01's passive local-read boundary without adding a retriever, execution capability, component, report field, or test ID. This correction awaits Step 8 owner acceptance. The original Step 7 submission and handoff language below is retained as history; its originally proposed mapping was subsequently approved in OA-007. Current sequencing and pending audit acceptance are governed by the register.

**[Owner-approved decision: OA-006]** Following the Step 6 delivery, the owner instructed: “继续step 7” (“Continue with Step 7”). The decision register records adoption of the delivered hero contract and authorization for this step. Previously approved files remain unchanged. Their earlier proposed-status headers are historical delivery metadata; subsequent approval is recorded in the register.

**[Engineering proposal]** This document completes the plan's required chain:

**Source or approved design decision → authoritative definition → planned responsibility → future check → report content → permitted inference → limitation.**

All components and checks below are planned. A row supplies traceability, not evidence that code exists or a test passed. The companion document supplies test arrangements, expected outcomes, and prediction-decision rules. No package paths, executable schemas, provider adapters, or repository architecture are created here.

The markers distinguish origins: **S** means source-derived; **A** means an engineering choice adopted before the Step 7 submission; **P** marks mapping or interpretation originally proposed in Step 7 and adopted through OA-007. The separately identified Step 8 correction remains pending audit acceptance. Source-derived formulas retain their source attribution after adoption. A software convention does not become a theorem through approval.

### 1.1 Source and contract keys

| Key | Authoritative material |
|---|---|
| SD | Xiangyu Guo, *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness*. Supplied August 2026, 27-page PDF. |
| SI | Xiangyu Guo, *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*. Supplied August 2026, version 1.0, 31-page PDF. |
| PLAN | `PHASE_0_PLAN.md` |
| SCOPE | `PROJECT_SCOPE.md` |
| DEF | `DEFINITIONS_AND_UNITS.md` |
| SC | `STRUCTURAL_CLASS_CONTRACT.md` |
| MET | `METRICS_SPEC.md` |
| EI | `EVALUATION_INTEGRITY.md` |
| HERO | `HERO_BENCHMARK_SPEC.md` |
| VF | `VALIDATION_AND_FALSIFICATION.md` |

The supplied PDF identities match PLAN Appendix A. Source references identify these editions, not independently verified versions of works cited inside them. In particular, SD §9.7, PDF page 21, supplies P1/P5; SI §§8.5-8.6, PDF page 20, supplies the tiered validation and core protocol. HERO's eight classes, Python domain, budgets, temperatures, audit quotas, and MET's lexical proxy are adopted engineering choices.

### 1.2 Delivery tags

| Tag | Scope |
|---|---|
| M | First executable milestone: offline fixture/imported-record core calculations and reporting, after separate implementation authorization. |
| V | Additional v0.1 offline comparison capability: text diagnostics, matched-condition summaries, and declared resampling sensitivity. |
| E | Actual independent domain validation or empirical study evidence. Record handling can be tested in M/V; substantive fulfillment requires separately supplied evidence. |
| D | Deferred capability. M/V must preserve its unavailable/deferred boundary, without implementing its estimator. |

Tags describe responsibility, not an instruction to implement all rows together. No E requirement silently becomes a prerequisite to M's stipulated-label demonstration. No record-completeness test substitutes for E evidence.

## 2. Planned responsibilities

**[Engineering proposal]** These identifiers are logical responsibilities, not existing modules or mandatory directories. Implementation planning may combine them while preserving every contract.
| ID | Planned responsibility | Delivery | Boundary |
|---|---|---|---|
| PC-01 | Local input and identity validation | M | Read declared local inputs passively to validate linked metadata, record IDs, hashes, versions, and access states. Never execute input content or automatically fetch remote content. An external locator remains metadata unless its material is separately supplied as an authorized local input. |
| PC-02 | Attempt, artifact, and selection accounting | M; V study checks | Preserve planned versus actual calls/positions, raw-to-sample associations, extraction, grouping, and ordering. |
| PC-03 | Imported class and evidence-policy handling | M | Check pinned assignments against declared records and policy. No automatic mechanism discovery, independent-truth judgment, or live judge. |
| PC-04 | Population and prefix construction | M | Build the two approved views and fixed prefixes; expose coverage and withheld records. |
| PC-05 | Core count/distribution calculations | M | Implement the specified unweighted count functionals and numerical rules. |
| PC-06 | Passive textual diagnostics | V | Apply the registered tokenizer and pair calculations to the identified text subset. |
| PC-07 | Comparison eligibility and endpoint calculation | V | Check the adopted frame/resource/coverage rules; compute registered contrasts without replacing endpoints. |
| PC-08 | Block aggregation and replay | V | Equal-block summaries and the specified paired resampling procedure; no automatic population inference. |
| PC-09 | Evidence, revision, and claim records | M; V dependent results | Carry lineage, exposure, claim assessments, and correction dependencies. Substantive assessments remain evidence-linked human/domain decisions. |
| PC-10 | JSON and Markdown reporting | M; V sections when supplied | Preserve numeric and evidential states, provenance, field identities, and permitted wording across both outputs. |
| EP-01 | External schema and domain validation | E | Validate descriptors, witnesses, functional oracle, and applicable environment outside the toolkit; no execution engine is selected. |
| EP-02 | Independent annotation and integrity review | E | Supply actual independent initial judgments, audits, adjudication, calibration where applicable, and scoped claim assessments. |
| EP-03 | Registered external model collection | E | Supply actual prompts, controls, calls, artifacts, and resource records under separate authorization; no model provider is selected. |

## 3. Requirement-to-result traceability

**[Engineering proposal]** Each row names a source or adopted design, its controlling definition, the responsibility that would implement or validate it, future test IDs from VF §4, and report groups from Section 4. Rows can share a test; no first-release quantity may exist only in an untested narrative summary. The inference and limitation columns apply to every field referenced by that row.
| ID | Origin | Definition / controlling rule | Planned responsibility | Future checks | Report groups | Permitted inference | Limitation |
|---|---|---|---|---|---|---|---|
| TR-01 | A: PLAN §§2,5; SCOPE §1 | Source/contract identity and actual approval | PC-01, PC-09 | VT-01, VT-24, VT-30 | RF-01, RF-33 | Identify the exact source and contract used. | Hashes and owner adoption do not establish empirical validity. |
| TR-02 | S: SD §§3.2-3.6; SI §3.1; A: DEF §§2,4; SC §3 | Task, horizon, resolution, and structural map | PC-01, PC-03; EP-01 | VT-14, VT-15, VT-25 | RF-02, RF-03 | A measurement under the declared distinction level. | No universal ontology or mechanism inference from final outputs alone. |
| TR-03 | S: SD §3.7; SI §§4,8.2; A: DEF §§2,7 | Separate notation and effective-count meanings | PC-01, PC-05 | VT-07, VT-08, VT-09 | RF-18, RF-19 | Report the selected mathematical quantity in its unit. | No ambiguous N_eff or interchange of probability and empirical thresholds. |
| TR-04 | A: DEF §3; MET §4.1; HERO §§7-8 | Calls, realizations, groups, blocks, and analysis runs | PC-01, PC-02 | VT-02, VT-03, VT-35, VT-36 | RF-07, RF-08, RF-09, RF-10 | Reconcile actual observations and their dependencies. | Rows, repeated analyses, and repeated labels are not independent calls. |
| TR-05 | A: DEF §8; MET §3 | Knowledge, calculation, review, and claim axes | PC-01, PC-09, PC-10 | VT-01, VT-06, VT-20 | RF-12, RF-15, RF-29 | A computable number can accompany a restricted claim. | Unknown, undefined, invalid, and zero retain different meanings. |
| TR-06 | S: SD §§3.2,9.4; SI §§3.1,8.6; A: SC §§4-6 | Hard membership and evidence acceptance | PC-03; EP-01, EP-02 | VT-04, VT-15, VT-47 | RF-12, RF-14 | An evidence-accepted class within a named policy. | A provisional suggestion, label string, or self-description cannot suffice. |
| TR-07 | S: SD §6.5; SI §12; A: SC §§6.3,6.5; MET §4.2 | Classification and validity remain separate | PC-03, PC-04 | VT-05, VT-06, VT-13, VT-15 | RF-13, RF-16, RF-17 | Describe classified-all and classified-valid subsets separately. | Concentration neither proves validity nor excuses hidden failure filtering. |
| TR-08 | S: SD §§3.2,9.6; SI §§3.1,9; A: SC §§7-8; HERO §4 | Hybrids, new mechanisms, and partition conflicts | PC-03, PC-09; EP-01 | VT-16, VT-25, VT-50 | RF-12, RF-30, RF-31 | Preserve an unresolved candidate for review. | No invented other class, transitive closure, or forced first-match label. |
| TR-09 | A: DEF §5; MET §4 | Inventory, population, and coverage denominators | PC-02, PC-04, PC-10 | VT-05, VT-06, VT-37 | RF-11, RF-16, RF-17 | Conditional frequencies with selection/evidence coverage. | Different axes overlap; missing labels do not estimate unconditional frequencies. |
| TR-10 | S: SI §§3.3,8.1; A: DEF §6.1; MET §5.2 | Occurrence-based observed support | PC-05 | VT-06, VT-07, VT-13 | RF-18 | Classes observed at least once in the accepted population. | Empty-population zero and finite nonappearance say nothing about total capacity. |
| TR-11 | S: SD §5.1; A: DEF §6.1; MET §5.3 | Empirical-frequency-thresholded support | PC-05 | VT-08, VT-13 | RF-19 | Classes passing the declared exact empirical threshold. | Threshold omission, empty denominator, and no passing classes differ; no renormalization. |
| TR-12 | S: SD §§3.7,9.2; SI §§4,8.2; A: MET §5.4 | Unsmoothed structural entropy in nats | PC-05 | VT-06, VT-07, VT-09, VT-10 | RF-18 | Entropy of the identified empirical class distribution. | No total-output entropy, full repertoire, or validity inference. |
| TR-13 | S: SD §9.2; SI §§5.3,8.2; A: MET §5.5 | Plug-in SCI | PC-05 | VT-07, VT-09, VT-33 | RF-18 | Concentration under empirical with-replacement sampling. | Distinct-record pair disagreement is a different statistic. |
| TR-14 | S: SD §§3.7,9.2; SI §§5.3,8.2; A: MET §5.6 | Shannon and Simpson effective class counts | PC-05 | VT-07, VT-09, VT-13 | RF-18 | Two differently weighted effective quantities. | Neither is an integer repertoire count; use unrounded source values. |
| TR-15 | S: SD §§9.2,9.5; A: MET §6; HERO §8.2 | Fixed-prefix distinct-k and accumulation | PC-02, PC-04, PC-05 | VT-10, VT-11, VT-12, VT-13 | RF-20 | Observed classes within the fixed selected prefix. | No valid-only top-up, missing-position compression, or latent-tail extinction claim. |
| TR-16 | S: SD §3.7; SI §4; A: MET §8 | Lexical-trigram diagnostic and text subset | PC-06 | VT-31, VT-32 | RF-21 | The specified surface distance on usable original text. | No structural classification or exact realization entropy from the proxy. |
| TR-17 | S: SD §9.2; A: MET §8.4 | Within-class pair-weighted realization proxy | PC-06 | VT-31, VT-32 | RF-22 | Surface variation among accepted same-class pairs. | Singletons have no pair estimate; changing class composition affects the aggregate. |
| TR-18 | A: MET §9 | Distinct-pair structural non-equivalence | PC-06 | VT-32, VT-33 | RF-23 | Observed class disagreement on the same text-eligible pairs. | No substitution of 1-SCI or independent-replicate claim for pair count. |
| TR-19 | S: SD §§3.2,9.5; A: MET §10.1; HERO §§7-10 | Cross-condition compatibility and actual controls | PC-07; EP-03 | VT-14, VT-34, VT-35 | RF-05, RF-06, RF-28 | A contrast within the documented common frame. | Unknown temperature behavior blocks a temperature claim; separate summaries can remain. |
| TR-20 | S: SD §9.7 P1; A: MET §10.3; HERO §10; P: VF §6 | B-A surface gain, structural gain, and their contrast | PC-06, PC-07, PC-08, PC-10 | VT-38, VT-42, VT-44, VT-48 | RF-24, RF-26, RF-28 | Fixed-suite evidence relative to the registered proxy/resolution. | Positive contrast alone is insufficient; no universal growth-rate or creativity verdict. |
| TR-21 | S: SD §9.7 P5; A: MET §10.4; HERO §10; P: VF §6 | C-A and C-B valid distinct-20 comparisons | PC-04, PC-07, PC-08, PC-10 | VT-37, VT-38, VT-43, VT-49 | RF-25, RF-28 | Observed valid breadth at matched planned calls/positions/allowance. | Both comparators and validity bands matter; not equal actual compute or full expressible support. |
| TR-22 | A: HERO §§7.3,10.3; MET §§4,10 | Coverage, quality, ceiling, and resource flags | PC-07, PC-10 | VT-12, VT-35, VT-37, VT-44, VT-45 | RF-07, RF-17, RF-28 | Identify the exact eligible and restricted comparison scope. | Passing a numerical band does not repair unknown classes or establish exact quality equality. |
| TR-23 | S: SD §9.5; A: MET §11; HERO §10.2 | Equal-block summaries and paired replay | PC-08 | VT-39, VT-40, VT-41 | RF-26, RF-27 | A fixed-suite mean and prompt-resampling sensitivity. | No row-level pseudoreplication, missing-block substitution, or population confidence claim. |
| TR-24 | S: SD §9.7; A: HERO §10.4; P: VF §§6-7 | Outcome decision and multiplicity boundary | PC-07, PC-10 | VT-42, VT-43, VT-45, VT-50 | RF-24, RF-25, RF-28, RF-34 | Supporting, contrary, or inconclusive operational outcomes with limitations. | No minimum-p selection, post-result endpoint switch, or test requiring theory agreement. |
| TR-25 | S: SD §9.3; SI §8.5; A: HERO §§3-4 | Eight-family bounded sorting frame | PC-01, PC-03; EP-01 | VT-14, VT-25, VT-47 | RF-02, RF-03, RF-30 | A mechanism judgment inside the adopted domain. | No automatic classifier; registry inclusion is neither empirical validation nor completeness. |
| TR-26 | S: SI §8.5; A: HERO §§5,12 | Functional suite and separately validated oracle | PC-03, PC-09; EP-01 | VT-26, VT-27, VT-28 | RF-13, RF-14, RF-30 | Validity under the 8995-case rubric and evidenced scope. | Planned cases are not executed cases; finite passing tests do not prove all-domain correctness. |
| TR-27 | S: SD §9.4; SI §§8.5-8.6; A: EI §5; HERO §6 | Core annotations and generated-output audit | PC-09; EP-02 | VT-22, VT-29, VT-47 | RF-30, RF-32 | Actual independent review for the named set and role. | Two sessions by one person, exposed labels, and planned quotas do not satisfy it. |
| TR-28 | S: SD §9.6; SI §§3.4,9; A: EI §§3-4,9 | Role, lineage, transformation, and exposure records | PC-09; EP-02 | VT-21, VT-22, VT-24 | RF-14, RF-29, RF-32 | Scoped known dependencies and evidence gaps. | Names, hashes, absent parents, and deterministic tools do not prove independence. |
| TR-29 | S: SD §9.6; SI §9; A: EI §§2,7; HERO §13 | Four conditions and four versioned components | PC-09, PC-10; EP-02 | VT-21, VT-23, VT-47 | RF-04, RF-29, RF-31 | Describe records and actual evaluated contributions separately. | An empty intake or form does not demonstrate ongoing external correction. |
| TR-30 | S: SI §§3.4,9; A: EI §8; HERO §6.3 | Tail preservation and external candidate intake | PC-09; EP-02 | VT-16, VT-23, VT-29 | RF-04, RF-30, RF-31 | Preserve required evidence and review new distinctions. | Reference quotas and targeted audit cannot add generated observations. |
| TR-31 | S: SD §9.6; SI §9; A: SC §§10-11; MET §14; EI §10 | Versioned correction and all affected results | PC-03, PC-04, PC-09, PC-10 | VT-17, VT-18, VT-46 | RF-12, RF-16, RF-33, RF-34 | A corrected analysis of the same observations. | No fresh sample count, selective condition repair, or automatic new confirmation. |
| TR-32 | A: EI §6; SCOPE §7 | Calculation versus scientific claim | PC-09, PC-10; EP-02 | VT-04, VT-20, VT-22, VT-47 | RF-15, RF-29, RF-34 | Fixture arithmetic, qualified labels, and validated measurement remain separable. | Approval, completeness, or a passing software suite cannot supply external evidence. |
| TR-33 | A: SCOPE §§4-5; SC §5; HERO §§8,12 | Passive processing and original-artifact fidelity | PC-01, PC-02, PC-10 | VT-19, VT-28, VT-36 | RF-09, RF-11, RF-36 | Read recorded artifacts and imported results without executing them. | No automatic repair, retrieval, installation, model call, or untrusted execution. |
| TR-34 | A: MET §§3,14; HERO §11.2; EI §11 | Report parity, provenance, and reproducibility | PC-01, PC-08, PC-09, PC-10 | VT-09, VT-20, VT-39, VT-46 | RF-01, RF-15, RF-27, RF-34, RF-36 | Replay a calculation from pinned evidence and method. | Provider repeatability and public access are separate from local arithmetic reproducibility. |
| TR-35 | A: PLAN §§1,5,7; SCOPE §§4,7 | Authorization and milestone boundary | PC-09, PC-10 | VT-19, VT-30 | RF-01, RF-34, RF-35 | Identify the authorized document or fixture work. | No implementation, spending, independent-evidence acceptance, or release by implication. |
| TR-36 | S: SD §5; SI §§3.3,8.1; A: DEF §6; MET §13.1 | Deferred expressible/latent support and intervention union | PC-10; future responsibility undecided | VT-51 | RF-35 | Report actual appearances without a larger support claim. | No probability-threshold certification or hidden representation diagnosis in v0.1. |
| TR-37 | S: SD §§3.5-4,6.6,9.2; A: MET §13.1 | Deferred frontier, intervention, provenance, transmission | PC-10; future responsibility undecided | VT-52 | RF-35 | Identify future prerequisites and current absence of estimates. | A/B/C differences at one resolution do not identify the frontier or convergence cause. |
| TR-38 | S: SD §11; SI §§5-6,8.3; A: MET §13.2 | Deferred recursive trajectories and separate SHL quantities | PC-10; future responsibility undecided | VT-53 | RF-35 | Retain the categorical-null and empirical distinction. | No training rounds from inference calls; no unconditional neural collapse forecast. |
| TR-39 | S: SI §8.4; A: MET §13.3 | Deferred External Recovery Rate | PC-10; future responsibility undecided | VT-54 | RF-35 | Preserve missing-set, grounding, and recovery requirements. | No numeric v0.1 ERR, direct-answer injection, or zero/one for an empty denominator. |
| TR-40 | S: SD §3.7; SI §4.2; A: MET §13.4 | Deferred soft labels and exact realization entropy | PC-03, PC-10; future estimator undecided | VT-16, VT-51 | RF-12, RF-35 | Expose unclassified or probabilistic evidence as such. | No posterior mass in hard-label counts or entropy inferred by subtracting a lexical proxy. |

## 4. Report-field coverage index

**[Engineering proposal]** Every first-slice result must carry its semantic identity directly or through pinned local references. The grouped slots below cover the initial DEF field inventory and additions in SC, MET, EI, and HERO. They do not prescribe JSON nesting or create an executable schema. Exact names already adopted upstream retain their spelling and meanings. Descriptive contents without an adopted scalar name remain linked record contents; implementation must not invent a new metric to fill them.

The trace links supply each group's inference boundary; tests exercise both available content and missing/withheld cases. Optional and deferred records appear with their actual state rather than invented values. A new public result field added during implementation needs a corresponding contract/test mapping before release.
| Group | Field names or required record contents | Inference-boundary rows | Future checks |
|---|---|---|---|
| RF-01 | `input_schema_version`, `run_id`, `analysis_config_ref`, `study_id`, `data_role`; software version when it exists, input/configuration identities | TR-01, TR-34, TR-35 | VT-01, VT-20, VT-30 |
| RF-02 | `task_id`, `task_version`, `task_context`, `consequence_horizon` | TR-02, TR-25 | VT-14, VT-25 |
| RF-03 | `analytic_resolution_id`, `analytic_resolution_version`, `structural_schema_id`, `structural_schema_version` | TR-02, TR-08, TR-25 | VT-14, VT-16, VT-25 |
| RF-04 | `reference_registry_id`, `reference_registry_version`; stable-core/frontier/incident/tail component versions and reference designations | TR-29, TR-30 | VT-23, VT-29 |
| RF-05 | `model_identifier`, `model_family`, `checkpoint_identifier` with knowledge/evidence states | TR-19, TR-28 | VT-01, VT-21, VT-34 |
| RF-06 | `condition_id`, `generation_protocol_id`, `generation_protocol_version`, `prompt_block_id`, `prompt_id`, `conditioning_context_ref`, `decoding_settings`, `seed` | TR-04, TR-19 | VT-03, VT-24, VT-34, VT-35 |
| RF-07 | `collection_window`, `sampling_plan_ref`, `budget_record_ref`; planned/enforced cap and unit, actual input/output/reasoning usage, charges and access limitations | TR-04, TR-22 | VT-03, VT-34, VT-35 |
| RF-08 | `attempt_id`, `attempt_status`, `retry_of`, `attempt_summary`; planned slots and actual response linkage | TR-04 | VT-02, VT-03, VT-35 |
| RF-09 | `raw_response_ref`, `sample_id`, `output_ref`, `output_content_hash`, `extraction_rule_version`; exact text-region association | TR-04, TR-33 | VT-02, VT-19, VT-36 |
| RF-10 | `generation_group_id`, `group_type`, `within_group_index`, `sample_order`, `shared_context_ref`, `grouping_summary` | TR-04, TR-15 | VT-03, VT-11, VT-12, VT-40 |
| RF-11 | `completion_status`, `termination_reason`, `selection_status`, `selection_reason`, `completion_summary`, `selection_summary`, `exclusion_summary`; plan/realization difference | TR-09, TR-33 | VT-03, VT-06, VT-12, VT-36 |
| RF-12 | `assignment_id`, `assignment_version`, `structural_class_id`, `assignment_status`, `assignment_method`, `assignment_review_status`, `assignment_evidence_policy_id`; policy version, `classification_uncertainty_ref`, `disagreement_ref` | TR-06, TR-08, TR-31, TR-40 | VT-04, VT-15, VT-16, VT-17 |
| RF-13 | `validity_status`, `validity_rubric_ref`, `task_success_observations_ref`, `validity_summary`; domain-suite/counterexample/environment evidence | TR-07, TR-26 | VT-05, VT-06, VT-26, VT-27, VT-28 |
| RF-14 | `evidence_refs`, `external_grounding_status`, `role_records_ref`, `lineage_records_ref`; evidence, role, lineage, and scoped independence-assessment identities | TR-06, TR-26, TR-28 | VT-04, VT-15, VT-21, VT-22 |
| RF-15 | `analysis_cell_id`, `analysis_population`, `metric_name`, `metric_definition_version`, `value`, `unit`, `result_status`, `unavailable_reason`, `evidence_status`; uncertainty state and reason | TR-05, TR-32, TR-34 | VT-01, VT-06, VT-20, VT-41 |
| RF-16 | `population_size`, `class_counts`, pinned selected/accepted sample and assignment manifests | TR-07, TR-09, TR-31 | VT-02, VT-05, VT-17 |
| RF-17 | `selected_realization_count`, `classified_all_count`, `classified_valid_count`, `classification_coverage`, `valid_fraction_selected`, `decisive_validity_coverage`, `classified_valid_coverage`, `classified_valid_fraction`, `assignment_status_counts`, `assignment_acceptance_counts`, `validity_status_counts` | TR-07, TR-09, TR-22 | VT-05, VT-06, VT-37 |
| RF-18 | `observed_support_size`, `structural_entropy_nats`, `structural_concentration_index`, `effective_support_shannon`, `effective_support_simpson` | TR-03, TR-10, TR-12, TR-13, TR-14 | VT-06, VT-07, VT-09, VT-10, VT-13 |
| RF-19 | `observed_support_size_thresholded`, `min_empirical_frequency`, `thresholds`; exact threshold and unfiltered denominator | TR-03, TR-11 | VT-08, VT-13 |
| RF-20 | `structural_distinct_k`; k, selected IDs, `counted_samples`, population, prefix rule, partial-group flag, accumulation and zero-count reference rows | TR-15 | VT-10, VT-11, VT-12, VT-13 |
| RF-21 | `surface_lexical_trigram_distance`; text source/proxy/Unicode versions, eligible IDs, lexical-unit counts where reported, `proxy_text_coverage`, m and pair denominator | TR-16 | VT-31, VT-32 |
| RF-22 | `within_class_realization_diversity_proxy`; per-class eligible counts, pair counts and distances, pair-weighted denominator and composition limits | TR-17 | VT-31, VT-32 |
| RF-23 | `structural_pair_non_equivalence`; same eligible sample/pair identity as the surface calculation | TR-18 | VT-32, VT-33 |
| RF-24 | `p1_proxy_gain_contrast`; A/B operands, both gains, primary all-view and valid-view sensitivity, exact block set | TR-20, TR-24 | VT-38, VT-42, VT-44, VT-48 |
| RF-25 | `p5_valid_distinct_k_delta`; C-A/C-B separately, k=20 primary, all-view companions and k=5/10 secondary labels | TR-21, TR-24 | VT-38, VT-43, VT-49 |
| RF-26 | Per-block contrasts and equal-block means; intended/included/missing block lists and reasons | TR-20, TR-23 | VT-38, VT-39, VT-40 |
| RF-27 | `uncertainty_method_ref`; resample count/seed, RNG version, replay manifest, quantile convention, interval bounds and `prompt_resampling_sensitivity` scope | TR-23, TR-34 | VT-39, VT-40, VT-41 |
| RF-28 | Study gate records: frame, complete groups, classification/validity/text coverage, quality floor/band, controls/resources, `surface_proxy_near_ceiling`, registry-ceiling note | TR-19, TR-20, TR-21, TR-22, TR-24 | VT-12, VT-34, VT-37, VT-42, VT-43, VT-44, VT-45 |
| RF-29 | `integrity_assessment_ref`; requested claim, applicable requirements/outcomes, four-condition evidence and limitations, claim disposition | TR-05, TR-28, TR-29, TR-32 | VT-21, VT-22, VT-23, VT-47 |
| RF-30 | `audit_sampling_plan_ref`, `domain_validation_ref`, `annotation_summary_ref`, `disagreement_ref`, `adjudication_ref`; actual core/witness/descriptor/audit coverage | TR-08, TR-25, TR-26, TR-27, TR-30 | VT-22, VT-25, VT-26, VT-27, VT-29, VT-47 |
| RF-31 | Frontier/incident intake, preserved-tail role and successor dispositions, actual use and reasoned non-use | TR-08, TR-29, TR-30 | VT-16, VT-23, VT-29 |
| RF-32 | `blinding_record_ref`, `judge_calibration_ref`, `sensitivity_evidence_ref`; exposure, initial judgment, assistance and scoped independence records | TR-27, TR-28 | VT-22, VT-24, VT-47 |
| RF-33 | `correction_ref`, `supersedes_assignment_id`; pinned old/new evidence, affected runs, artifact/claim disposition, approval evidence | TR-01, TR-31 | VT-17, VT-18, VT-24 |
| RF-34 | `input_refs`, `permitted_claim_scope`; operational outcome/reasons from VF §6, unresolved evidence, qualification, and release authorization when supplied | TR-24, TR-31, TR-32, TR-34, TR-35 | VT-20, VT-30, VT-42, VT-43, VT-47, VT-50 |
| RF-35 | Deferred capability entries; conditional `intervention_family_id`, `intervention_family_version`, `intervention_id`, `changes_model_state`, `min_generation_probability`, `diagnostic_family_id`, `recursive_round_id`, `parent_state_ref`, `transition_ref`; `observed_intervention_union_size`, `gini_simpson_diversity`, `structural_half_life_null`, `structural_half_life_empirical` remain catalog entries; no v0.1 support/frontier/SHL/ERR estimates | TR-35, TR-36, TR-37, TR-38, TR-39, TR-40 | VT-30, VT-51, VT-52, VT-53, VT-54 |
| RF-36 | Readable report order, machine/readable parity, access/redaction limitations, missing-data and computation-limit reasons | TR-33, TR-34 | VT-19, VT-20, VT-32, VT-46 |

## 5. Coverage and change rules

**[Engineering proposal]** Before a future release, an implementer must demonstrate that each applicable TR/RF group has its referenced conformance checks implemented or a declared, approved scope exclusion. The checks' software and external-evidence portions stay separately identified in VF. A mock claim assessment can test routing; it cannot fulfill an independent review requirement.

The first milestone covers the M path and truthful reporting of V/E/D absence. It does not require implementing PC-06 through PC-08 or running EP-01 through EP-03. The v0.1 comparison release adds the V path, using fixtures or supplied observations with their actual evidence status. An empirical P1/P5 claim additionally needs E evidence. Completion of either other toolkit is irrelevant to these gates.

A later code refactor may change component names without changing scientific meaning. Changes to a denominator, accepted population, class boundary, proxy, endpoint, numerical convention, or claim rule require an explicit contract revision and impact assessment. Update tests and all affected reports together. Existing class names or metric names cannot conceal changed meanings.

The full upstream check register is mapped in VF §8. This document does not close the Step 8 integrated audit, prepare the final approval record, or grant Phase 1 authorization. No component is marked implemented and no future test is marked passed.

## 6. Step 7 review and next gate

Review covers this traceability structure and the companion validation/interpretation rules, recorded as the remaining Step 7 component of UD-005. The adopted metrics, hero budget, thresholds, and task boundaries remain unchanged. UD-006's actual-evidence gap and UD-007's deferred diagnostic boundary remain open.

After owner approval and an instruction to continue, Step 8 performs the integrated Phase 0 audit under the plan's limited corrective-write permission. Any scope or scientific change identified there still requires its explicit finding and renewed approval. Step 9's final baseline/approval record remains a separate later deliverable.
