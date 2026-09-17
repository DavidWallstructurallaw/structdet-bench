# EVALUATION_INTEGRITY

## StructDet-Bench: Evidence Lineage, Independent Validation, and Corrective Capacity

| Field | Value |
|---|---|
| Document version | 0.1 |
| Date | 2026-09-16 |
| Phase / step | Phase 0 / Step 5 |
| Status | PROPOSED STEP 5 CONTRACT; ready for Theory Owner review |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Approved input contracts | `PROJECT_SCOPE.md`, `DEFINITIONS_AND_UNITS.md`, `STRUCTURAL_CLASS_CONTRACT.md`, and `METRICS_SPEC.md`, each version 0.1 |
| Approval evidence | OA-002, OA-003, and OA-004 in the decision register |
| Decision authority | Theory Owner |
| Decision register | `UNRESOLVED_DECISIONS.md`, version 0.4 |
| Authorized deliverables | This contract and the decision-register update |
| Implementation / repository / experiment authorization | None |

## 1. Authority, sources, and scope

**[Owner-approved decision: OA-004]** The owner approved the delivered Step 4 metric contract and instructed continuation to Step 5. The five preceding plan/specification files remain read-only. Their original proposed-status headers remain historical delivery metadata; the decision register records the later approvals.

**[Engineering proposal]** This document owns evaluation-role records, lineage and independence evidence, independent validation requirements, the four open-evaluation components, and evidence-dependent claim/release gates. It extends the existing evidence-field inventory without changing its meanings. Structural membership and assignment acceptance remain governed by `STRUCTURAL_CLASS_CONTRACT.md`; calculations, populations, and numeric result states remain governed by `METRICS_SPEC.md`.

The labels **[Source-derived]**, **[Engineering proposal]**, and **[Owner-approved decision]** retain their established meanings. A label governs its section until another basis is stated. Proposed requirements use “must” to define the contract submitted for review; they do not self-approve it.

| Source | Supplied edition and relevant locations |
|---|---|
| SD | Xiangyu Guo. *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness*. August 2026, 27 pages. §§3.2-3.6, 5, 7, 9.1, 9.4-9.6, 12. |
| SI | Xiangyu Guo. *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*. August 2026, version 1.0, 31 pages. §§3.1, 3.3-3.4, 8.5-8.6, 9, 11.3-11.7, 12. |

The source identities and SHA-256 fingerprints remain those in the plan. SD §9.6 is on PDF page 20; SD §9.4 is on page 19. SI's Tier 1 table and core protocol are on page 20, and its four-condition Evaluation Closure table is on page 21. These supplied editions are the basis of this contract. Publications referenced inside them have not been independently checked here.

**[Engineering proposal]** The first release remains offline and import-based. This contract requires no live judge, crawler, annotation service, graph database, automatic recruitment, hosted incident system, or completion of either other toolkit. Linked local records and human-reviewed evidence are sufficient representations. It authorizes no actual collection, generated-code execution, publication, or software implementation.

## 2. The four governing conditions

**[Source-derived: SD §9.6; SI §9]** The supplied papers identify four conditions: **External Presence, Source Integrity, Tail Retention, and Corrective Capacity**. They also specify four open-evaluation components: **Stable Core, Rotating Structural Frontier, External Incident Stream, and Versioned Tail Registry**. The conditions and components are related but distinct.

**[Engineering proposal]** Use the following condition-level record. Do not collapse it into an overall integrity score or infer one condition from another.

| Condition | Required evidence in this project | Limitation to expose |
|---|---|---|
| External Presence | Origin of reference cases and distinctions; their intake, review, inclusion/exclusion, and actual use in validation or revision. | Material merely stored, or entirely filtered out, has not established effective corrective presence. |
| Source Integrity | Role and artifact identities, known ancestry, transformations, shared dependencies, exposure history, and scoped independence assessments. | Different names, providers, people, filenames, or deterministic tools do not by themselves establish independent evidence. |
| Tail Retention | Versioned designations of rare/relevant classes, their evidence and review coverage, protected reference cases, and explicit disposition after revisions. | A class unobserved in a finite generated sample is not thereby absent from the model. Reference preservation cannot force observed frequency. |
| Corrective Capacity | Traceable challenge, adjudication, correction, impact assessment, and re-analysis of affected records and claims. | A correction process described on paper does not establish that a particular real incident was corrected. |

The source's distinction between nominal sources and effective structural difference is preserved. SI §3.4 discusses entry, survival through preprocessing/selection, and effects on model learning. v0.1 has no training update: its narrower observable is whether external evidence enters the evaluation and can change reference definitions, assignments, or conclusions. This must not be reported as measured training exogamy or model recovery.

## 3. Evidence and lineage records

### 3.1 Common identity and knowledge rules

**[Owner-approved decision: OA-002 through OA-004]** Reuse the metadata states `known`, `unknown`, `unavailable`, and justified `not_applicable`. Keep assignment status, review status, validity, evidence acceptance, and numeric availability separate. A known assertion may still be only declared. A hash identifies bytes, not independent origin or truth.

**[Engineering proposal]** The following tables are semantic requirements, not executable schemas. Records can be normalized and linked through the existing `role_records_ref`, `lineage_records_ref`, `evidence_refs`, `disagreement_ref`, and `correction_ref` fields. Public reports may use stable pseudonyms and scoped summaries; the retained audit record must still distinguish actual entities and evidence.

Missing upstream ancestry is represented by an explicit unknown/unavailable relationship or frontier. An artifact with no recorded parents cannot automatically become an independently grounded root. Evidence references that cannot be resolved locally retain their access state and limit the affected conclusion; the toolkit does not retrieve them automatically.

### 3.2 Minimum record families

**[Engineering proposal]** Every integrity claim must link to the records needed for its scope.

| Record | Minimum content |
|---|---|
| Role assignment | `role_record_id`; role; actual entity identifier and type; task/study/sample scope; relevant dates; material accessed; material produced; decision responsibility; AI/tool assistance; declared conflicts or overlapping roles. |
| Evidence artifact | `evidence_id` and revision; originator; source locator and relevant passage/test scope; content identity where available; acquisition and creation records; method; assumptions; review state; access restrictions; supported assertions. |
| Lineage relation | `lineage_record_id`; subject and upstream artifact/entity references; relation type; relevant version/time; knowledge state; evidence basis; reviewer; unresolved upstream information. |
| Independence assessment | `independence_assessment_id`; the exact two roles, artifacts, or evidence paths being compared; assessed dependency dimension; supported scope; evidence and contrary evidence; unknowns; reasoned outcome; assessor and review date. |
| Exposure record | Artifact/version; exposed person/model/role; what was accessible or actually used; stage and time where known; evidence basis; whether exposure was part of the intended generation protocol, calibration, pilot work, or later review. |
| Annotation/adjudication record | Stable annotator identity; material and rubric versions; independent initial decision; evidence/rationale; later consultation; disagreement; adjudication outcome; replacement/withdrawal links. |
| Integrity assessment | Pinned study/run/result scope; requested claims; applicable requirements; evidence references; requirement outcomes; limitations; disposition and responsible reviewer. |

Relation types may describe derivation, copying, paraphrase, model generation, retrieval, shared source, annotation, selection, validation, or correction. Relations have typed meanings and evidential status; an edge does not imply every other dependency. An evidence reference cycle must not be accepted as independent support solely because every node cites another node. Historical/revision cycles or repeated review interactions are recorded according to their meanings rather than subjected to an invented universal acyclicity rule.

Source transformations retain both the originating artifact and the transformed artifact. Human editing, translation, a second model's summary, or a deterministic parser does not erase the preceding lineage. Independently obtained measurements or checks can add another supporting path without rewriting the original path as independent.

### 3.3 Scoped independence

**[Source-derived: SD §§9.4, 9.6; SI §§3.4, 7.4, 8.6, 9]** Nominal plurality can share a structural genealogy. The evaluation must expose the relationships among generators, classifiers, judges, sources, and correction channels.

**[Engineering proposal]** Independence is assessed relative to a specific dependency and claim, rather than stored as a universal boolean property of a source. At minimum, distinguish:

| Dimension | Question and required record |
|---|---|
| Reference construction | Were case content, class definitions, or expected answers derived from the evaluated lineage? Record origin and construction history. |
| Initial judgment | Did annotators form their initial decisions without seeing one another's answers or a suggested label? Record access and first-pass annotations. |
| Model ancestry | Are base-model, training-data, post-training, reward, or generator relationships known? Preserve each established relationship and unknown boundary separately. |
| Validation method | Does the validator test the claimed consequence through an evidenced rule or observation, or reproduce an upstream assertion? Record specification, tool/proof scope, and oracle origin. |
| Selection and revision | Could external findings enter review and affect the accepted schema or labels without being screened solely by the evaluated lineage? Record selection responsibility and disposition. |

An assessment outcome is `supported_for_scope`, `not_supported_for_scope`, or `unresolved`, with reasons. Non-applicability uses the established metadata state with justification. These outcomes govern an independence claim; they do not replace the knowledge state or assignment review state.

A shared publicly stated mathematical rule does not alone prove circular judgment. Two reviewers may use a common registered rubric while independently inspecting evidence. Conversely, two reviewers repeating the same model-generated answer are not made independent by their separate names. Assess the actual derivation and decision path.

A reference independently documented outside the current evaluated generation can provide external grounding even when the model's historical exposure to that reference is unknown. Such evidence does not establish that the reference was absent from pretraining. Unknown pretraining overlap restricts an exposure-sensitive claim without automatically nullifying every scoped domain check. Neither lack of documented overlap nor different provider labels proves zero overlap.

## 4. Roles and separation of judgment

### 4.1 Required roles

**[Source-derived: SD §9.4; SI §§8.6-9]** Preserve the reference source, generator, structural extractor/classifier, adjudicator, and validator as distinguishable roles. Human initial annotations and final adjudication must remain traceable.

**[Engineering proposal]** A person or tool can have several disclosed roles; several names for one entity do not create additional independent roles.

| Role | Responsibility | Essential evidence | Boundary |
|---|---|---|---|
| Reference source / curator | Establish the task, relevant distinctions, reference cases, and their selection. | Source artifacts, derivation records, selection rationale, class/registry versions, exposure history. | An AI-drafted reference remains AI-assisted; adoption by the owner does not certify independent origin. |
| Generator | Produce the evaluated realization under the declared protocol. | Actual model/family/checkpoint states, prompts, controls, attempt/group records, output identities. | Self-description can propose a mechanism claim but cannot validate it. |
| Structural extractor / classifier | Describe candidate mechanisms and apply the approved membership procedure. | Exact artifact, method/version, evidence locations, proposed labels, assistance and exposure records. | Provisional classifications remain outside standard accepted populations. |
| Human annotator | Form a recorded initial membership/validity judgment under the specified rubric. | Distinct identity, competence for the scoped task, initial answer, evidence, access/blinding record. | Repeated sessions by one person remain one annotator. |
| Adjudicator | Resolve disagreements or conclude that a decision remains unresolved. | Conflicting initial records, applicable rules, additional evidence, independence assessment, final rationale. | Agreement, majority vote, or owner approval alone cannot repair missing mechanism evidence. |
| Validator | Check class distinctions or output consequences using the declared formal, executable, or domain route. | Test/proof/inspection specification, assumptions, artifact identity, observations and independently grounded reference. | Passing output tests cannot silently establish an algorithmic mechanism. |

The owner may also act as curator, implementer, or a qualified reviewer when those roles and dependencies are disclosed. Ownership grants product-decision authority; independent-evidence requirements remain claim-specific. No institutional affiliation, journal approval, or organizational label substitutes for evidence.

### 4.2 Prohibited sole-lineage validation

**[Source-derived: SI §8.6, continued on PDF p.21; SD §§9.4, 9.6]** One model instance or closely related lineage must not be the sole generator, structural classifier, judge, and final validator of an empirical structural-support claim.

**[Engineering proposal]** The exclusion follows the evidence path. Splitting one lineage across prompts, personas, APIs, or services does not establish the required separation. A deterministic tool whose decisive oracle was copied from that lineage also requires an independent validation basis. Tool execution can contribute real evidence when its rule and tested consequence are independently grounded; deterministic behavior alone establishes only repeatability of that operation.

The first release may import model-assisted provisional work, but it neither calls the model nor promotes its labels automatically. The approved `adjudicated_import` policy still requires essential membership evidence and a concluded procedure. Qualified label-conditioned arithmetic may remain possible without the stronger independence claim, subject to Section 6.

## 5. Independent annotation and Tier 1 validation

### 5.1 Preserve both supplied protocols

**[Source-derived: SD §9.4, p.19]** SD's robust protocol calls for at least two independent human annotators for core validity sets, blinding to model identity and output source where possible, separation of generator/provisional classifier/final adjudicator, calibration before cross-family model judging, independent expert handling of disagreements, consequence-sensitive checks, and reporting of agreement and sensitivity.

**[Source-derived: SI §§8.5-8.6, p.20]** SI's Tier 1 design uses execution traces, proofs, formal specifications, simulator states, or mechanically testable mechanisms, together with sampled human audit. Its core protocol requires externally constructed benchmark cases, independent adjudication, consequence-sensitive validation, and an Evaluation Closure audit before release.

**[Engineering proposal]** For the source-conformant Tier 1 validation path, retain both obligations. The named core validity set receives at least two independent human first-pass annotations; the broader imported collection has the declared mechanical/formal/domain evidence and a specified sampled human audit. The two sets may overlap when both sampling and review requirements are met. These requirements do not automatically demand two human labels for every generated realization.

The papers do not supply a universal audit sample size, passing agreement threshold, coverage quota, or deployment schedule. Step 6 must specify the applicable core set and audit design; Step 7 must connect them to the named claims and tests. No unstated percentage or number is introduced here.

### 5.2 Core validity set and sampled audit contract

**[Engineering proposal]** Before an empirical validation claim, record:

| Requirement | Evidence field or reference |
|---|---|
| Named validation population and material role | `validation_set_id`, version, member IDs, fixture/reference/pilot/evaluation origin, and target claim. |
| Covered distinctions and difficult cases | Coverage map to approved class boundaries, same-class substitutions, different-mechanism contrasts, defects, hybrids, and protected-tail cases where applicable. |
| Selection rule | `audit_sampling_plan_ref`, selection timing, actual selected IDs, selection basis, additions/removals, and reasons. |
| Two independent core annotations | Two distinct human identities, their initial annotation records, competence statements, and independence/access assessments. |
| Tier 1 validation | `domain_validation_ref`: rule/proof/test scope, oracle/source lineage, exact artifacts, environment where relevant, observations, and limitations. |
| Blind review | `blinding_record_ref`: what was withheld, what remained visible, prior exposure, and unavoidable disclosure. |
| Disagreement handling | `disagreement_ref` and `adjudication_ref`: original decisions, unresolved cases, evidence used, responsible independent expert, and final disposition. |
| Review coverage and sensitivity | `annotation_summary_ref`, `judge_calibration_ref` when applicable, `sensitivity_evidence_ref`, and unperformed or inapplicable checks with reasons. |

The validation set must exercise the selected task's actual structural distinctions, not only clean examples that the proposed classifier already handles. A valid new mechanism remains eligible for review even when it is absent from the existing reference list. Reference-set coverage does not establish that the taxonomy is exhaustive.

Targeted audit of rare, uncertain, or high-consequence cases is allowed and must be identified as targeted. It cannot be reported as an unweighted random estimate of overall classification error. Audit additions never augment the original generator sample count. Reviewing every disputed item does not alone establish error-free undisputed items.

### 5.3 Independent first pass, adjudication, and blinding

**[Engineering proposal]** Initial human annotations must be preserved before consensus discussion. For a claimed independent first pass, annotators must not receive the other annotator's answer or a provisional model label. Common task instructions and the approved rubric are permitted and recorded. Any label exposure is disclosed and narrows the independence claim; a later blind relabeling cannot erase the prior exposure.

Blinding should hide model identity, output-source labels, and condition identity where feasible without altering decisive mechanism evidence. A separate review rendering must retain a mapping to the original output. The surface-distance diagnostic continues to use the approved original extraction/text rules; a blinded rendering cannot silently change its input.

Disagreement is routed to an independent domain expert with access to the conflicting records and relevant consequence evidence. That expert's overlap with earlier roles is disclosed. An unresolved disagreement stays unresolved when no defensible adjudication or independent expert evidence is available. A third vote alone is not a substitute for a supported decision.

Two agreeing labels establish agreement on the checked material, not independent truth. The record must retain whether agreement concerned class membership, validity, a pairwise equivalence, or a schema boundary. Class uncertainty must not become additional structural mass.

### 5.4 Agreement, judge calibration, and sensitivity reporting

**[Engineering proposal]** Preserve initial paired annotations, their common item set, missing/unresolved responses, disagreement categories, and adjudication changes. Imported agreement summaries must name their denominator and method; agreement calculated after consensus is identified as post-adjudication agreement. No new automatic inter-rater estimator is added to v0.1 by this contract.

A model-assisted judgment procedure used as empirical evidence needs calibration records against independent human/domain evidence under the relevant task, property, prompt, and model version. Record calibration material, prior exposure, disagreement by relevant slice, and limits on transfer to other tasks or versions. A model used only to propose unaccepted candidates is disclosed as provisional assistance; that role cannot claim calibrated judgment accuracy.

SD's judge-family and schema-version sensitivity requirements remain visible. Record actual alternative judgments/re-analyses when performed. With no model judge, judge-family sensitivity can be `not_applicable` with that reason. With only one applicable judge or schema analysis, mark the relevant sensitivity as not established; do not invent zero sensitivity or full protocol compliance. Such a gap limits the sensitivity or robustness claim and is assessed against the particular validation claim in Section 6. Step 5 does not add deferred soft-classification or sensitivity engines to v0.1.

## 6. Calculation, measurement, and empirical-claim gates

### 6.1 Separate calculation permission from scientific interpretation

**[Owner-approved decision: PROJECT_SCOPE.md §§6-7; structural contract §§6, 12; METRICS_SPEC.md §§3-4]** A calculation can be available while stronger empirical interpretations remain unsupported. Missing essential class evidence withholds the affected assignment under its policy. Missing independence evidence may instead restrict a label-conditioned summary. Neither case permits invented classes or hidden exclusions.

**[Engineering proposal]** Apply gates at the result/claim scope. A defect in one trace, one classifier, or one schema does not automatically invalidate unrelated evidence. Conversely, a shared defective rule may affect many otherwise independent-looking records. Record the impact rather than inferring it from a global label.

| Output or claim | Minimum basis | Permitted conclusion and boundary |
|---|---|---|
| Fixture-based software demonstration | Authorized implementation, explicitly stipulated fixture inputs, correct identity/denominator handling, and applicable software tests. | The software follows the supplied contract on those inputs. No measured model behavior or independent scientific validity is established. |
| Qualified imported-label summary | `adjudicated_import` membership/validity acceptance, pinned evidence, and correct arithmetic; remaining independence gaps disclosed. | Describes this evidence-qualified classified subset. It cannot be labeled independently validated solely because records say adjudicated. |
| Validated structural measurement | Approved task/class/rubric, actual schema-level and sample-level evidence, applicable independent annotation/domain audit, and a scoped integrity assessment. | The stated classes/consequences are supported within the audited domain and evidence coverage. No universal validity, full repertoire, or unseen-case guarantee follows. |
| Empirical P1/P5 or another named theory comparison | Valid measurement plus the approved hero design, prespecified controls, valid grouping/budgets, approved analysis, exposure record, and treatment of contrary/inconclusive outcomes. | Bears on the specified prediction under the documented model/protocol/task. A general causal or population claim needs its own design support. |
| Full conformity to the declared source protocol | Requirement-by-requirement evidence for the applicable declared protocol, with no unmet requirement disguised as non-applicability. | A procedural statement about that scope. It is neither a truth guarantee nor an overall quality rating. |

A qualified descriptive report can be prepared or released under a separate authorization with its limitations prominent. The missing evidence prohibits the unsupported claim, not every possible communication about the work. Specification approval and software release do not themselves approve any empirical publication or incur annotation/model-call expenses.

### 6.2 Requirement assessment and claim disposition

**[Engineering proposal]** An `integrity_assessment_ref` can be linked through the existing result evidence fields. It must identify the exact requested assertion, affected results/populations, protocol version, applicable requirements, evidence, unknowns, departures, and responsible assessment.

Each requirement receives `satisfied_for_scope`, `unsatisfied`, `unresolved`, or justified `not_applicable`. These are requirement outcomes, not metric values. An unperformed mandatory check is unresolved or unsatisfied, rather than non-applicable. A claimed independent contribution must have a supporting independence assessment under Section 3.3.

The claim disposition is `supported_for_scope`, `restricted`, or `withheld`, with an explicit allowed wording/scope and outstanding requirements. It does not override `result_status`. A metric may remain `available` while the claim of independent validation is withheld. Owner approval can change a product decision or authorize a declared departure; it cannot make absent evidence present or relabel a departure as source conformity.

### 6.3 Current evidence and development boundary

**[Engineering proposal]** At this Step 5 delivery, the available project materials are the theory sources, approved specifications, and constructed examples/check requirements. Document preparation is AI-assisted. No independent human annotation pair, calibrated judge, source-validated hero registry, empirical model collection, or actual correction incident has been supplied by this phase.

The document-review activity is not an independent annotator set. UD-006's evidence component therefore remains open. Its protocol component is submitted here for owner review. Missing evidence limits later empirical claims; it does not block Step 6 specification or subsequently authorized fixture implementation. Deferred Layer B recovery and latent-support capabilities retain their existing boundaries.

## 7. Minimal open-evaluation architecture

**[Source-derived: SD §9.6; SI §9]** The benchmark combines a stable reference with a changing frontier, independently supplied incidents, and preserved rare structure.

**[Engineering proposal]** Represent the four components through versioned local records. No live operational service is required in Phase 0 or v0.1. A component definition or empty intake ledger demonstrates a supported record path, not evidence of continuous external input.

| Component | Minimum contract-level contents | Update and analysis rule |
|---|---|---|
| Stable Core | Pinned task/class/rubric/registry versions; reference cases and their provenance; expected distinctions; validation evidence and known limits. | Preserve regression comparability. Correct mistakes by new versions and impact review, not silent edits or permanent freezing of known errors. |
| Rotating Structural Frontier | Candidate distinctions, new failures, out-of-schema mechanisms, reference origin, exposure history, evidence, and review disposition. | Review within the approved task family first. New task families require a scope decision. Candidate intake does not automatically create a counted class or revise a confirmatory run. |
| External Incident Stream | Stable incident ID; submitter/observer and origin states; affected artifact; allegation/observation; supplied evidence; receipt order; review responsibility and disposition. | Accept manual local submissions, including contradictory findings. Independently observed status must be established, not inferred from the word external. No monitoring or automatic collection is promised. |
| Versioned Tail Registry | Class/schema link; protected designation; rarity or consequence basis; reference/audit cases; validation state; coverage requirements; changes and unresolved evidence. | Preserve review access and explicit disposition across versions. Neither reference inclusion nor targeted review adds mass to a generated-output distribution. |

A material may participate in more than one component using the same underlying identity. Multiple registry entries, incident copies, or reports of the same event do not multiply independent evidence. Each benchmark release identifies the component versions and any known-empty, unknown, or unavailable contents.

The frontier/intake workflow is **received → assessed → reviewed → accepted, rejected with reasons, or left unresolved → versioned effect where warranted**. This describes a human-reviewed record process. It does not create a new automatic classifier or presume that every submission deserves admission.

Claims about ongoing openness require actual intake/disposition history over a declared period. The existence of a form, a repository, or this contract does not establish that history.

## 8. Effective external presence and tail protection

### 8.1 Evidence must retain a route to consequential review

**[Source-derived: SI §§3.4, 9, 11.1, 11.7; SD §9.6]** External material has corrective significance when it can survive processing and alter evaluation. Tail retention protects rare relevant classes against disappearance beneath aggregate results.

**[Engineering proposal]** For each reference or incident contribution relied on in an openness claim, preserve its received form, transformations, selection decision, retained distinction, reviewer access, and resulting use or reasoned non-use. Evidence can support, contradict, or leave a question unresolved. Selection must not depend solely on agreement with the evaluated model or the desired P1/P5 result.

A reviewer must be able to challenge the class schema as well as individual labels. A rejected submission retains the reason and relevant evidence; the record must permit reconsideration when new evidence appears. Malformed or out-of-scope submissions need not become valid cases, but their rejection cannot silently be reported as absence of external contradiction.

### 8.2 Reference and audit protection

**[Engineering proposal]** Tail entries distinguish a class that is rare in a specified observed population from one designated important because of its consequences. Rarity needs a population/protocol or independently sourced reference basis. Importance needs a task-relevant rationale. Neither designation proves the other.

Step 6 must state which reference classes are protected, the case/audit coverage required for them, and how coverage deficits are handled. SI's minimum-tail-quota requirement remains visible as a reference/validation-design obligation. This step does not invent numerical quotas. Positive coverage requirements must not be implemented by repeatedly sampling the generator until a desired class appears in the confirmatory batch.

The approved fixed-budget/prefix rules remain unchanged. Targeted elicitation, extra review, or specially built rare cases are separately identified activities. They may supply validation evidence or exploratory material, but they cannot replace failed or unclassified samples in a frozen generation prefix.

For protected classes, retain available class counts and existing validity/classification accounting under the declared views. An unobserved reference class has observed count zero when that inventory is known; an unresolved novel candidate has no accepted class count. Neither becomes a proof of latent extinction. First-release reporting does not introduce new retention-rate, worst-slice score, or SHL estimators. Longitudinal tail curves remain within the deferred capability boundaries; the records preserve the evidence needed for later work.

### 8.3 Changing the registry

**[Engineering proposal]** Protection does not make an erroneous class permanent. A disconfirmed, merged, redefined, or inapplicable entry can be changed through an evidenced revision. Preserve its old designation, source, decision, class mapping, and affected reference/audit requirements. Do not silently remove a class because the tested system performs poorly or because it complicates annotation.

If an existing class splits, carry forward the protection question to the successor definitions and decide it explicitly. Previously unresolved cases must be reconsidered where the new distinction applies. Changing reference coverage alone affects registry-relative interpretation; empirical frequencies change only when their accepted samples or class meanings actually change.

## 9. AI assistance, exposure, and contamination

**[Source-derived: SD §§9.1, 9.4, 9.6; SI §§8.6, 9, 11.3-11.4]** Benchmark construction, judging, and revision must preserve source lineage and exposure. Model-generated cases are synthetic evidence with disclosed origin.

**[Engineering proposal]** Disclose AI involvement in specifications, reference construction, prompt drafting, code/proof suggestions, provisional labels, adjudication assistance, and report preparation when it contributes to the evidential path. Record the actual operation and available model/version information. Unknown details remain unknown. A generated artifact does not become externally constructed merely because a person approves, reformats, or renames it.

An independent domain check can establish a scoped property of an AI-assisted artifact. Preserve both facts: the artifact's AI-assisted origin and the separate validation evidence. Validation may strengthen the property claim without proving historical source independence or benchmark novelty.

Maintain exposure distinctions among reference construction, calibration, pilot inspection, confirmatory collection, and re-analysis. A model presented with a reference solution, class label, or mechanism specification is conditioned on that material. This may be an intended protocol, including structural-divergence prompting, but the report must preserve it. A known public reference is not automatically unsuitable; it cannot support a claim of unseen performance without the relevant evidence.

Record suspected and established contamination separately. Content similarity alone can prompt review but does not prove shared ancestry. Identical hashes establish identical bytes, while independent creation, copying, and benchmark exposure still depend on their records. A claim of post-cutoff evidence requires the relevant event and model-cutoff evidence; date labels alone are insufficient when the cutoff is unavailable.

Calibration or pilot material used to change prompts, classes, thresholds, or acceptance criteria cannot silently serve as untouched confirmation of those choices. Corrections to previously analyzed data produce labeled re-analysis under Section 10. Counterexamples and unfavorable findings must retain the same access to review as favorable findings.

All submitted content is passive evidence. Instructions embedded in an output, incident attachment, or copied report have no authority to change the task contract, run commands, contact a service, or alter file permissions. The first release imports existing execution reports without executing their programs. Step 6 owns any future safe-validation design, and execution remains outside the approved v0.1 scope.

## 10. Correction procedure and downstream impact

### 10.1 Required correction record

**[Owner-approved decision: structural contract §§10-12; METRICS_SPEC.md §14]** Revisions retain historical evidence, task/class/assignment versions, selected inventories, and affected analysis results. Re-analysis is not new sampling.

**[Engineering proposal]** Each correction must identify the trigger, evidence, affected versioned objects, responsible review, scope of impact, replacement or unresolved status, and the disposition of dependent claims. The minimum dependency path remains:

**Evidence / rule / registry correction → affected assignments or reference meanings → affected populations and denominators → metrics / diagnostics / comparisons → report and claim revision.**

An impact review records which steps of this path actually change. A correction to source independence can restrict an empirical claim while leaving defensible imported-label arithmetic unchanged. Withdrawal of essential membership evidence requires withholding or re-adjudicating the affected assignment. A broken schema-level rule may invalidate the entire affected class space. No universal “all results invalid” or “numbers unchanged, therefore no issue” shortcut is allowed.

Freeze a historical result with its original inputs and evidence state. Mark its release/claim disposition as superseded, withdrawn, restricted, or awaiting re-analysis as appropriate. These are artifact/claim dispositions, not additional numeric `result_status` values. A revised run follows the existing available/undefined/unavailable conventions.

For re-analysis, pin replacement evidence and assignment revisions, rebuild the selected/accepted populations, recalculate all dependent outputs, and reassess every affected condition. Preserve the original sample IDs, group memberships, ordering, attempts, and resource budget. A repair to a generated program creates a transformed artifact and cannot retrospectively validate the original output.

### 10.2 Constructed correction scenario

**[Engineering example]** The following is a non-executable fixture specification, not an observed experiment or an independent annotation result. Classes A and B are hypothetical and select no hero taxonomy. Four selected realizations, s1 through s4, retain unchanged task/schema, ordering, and separately supported valid assessments.

Initially, accepted assignments are A, A, B, B. A review then finds that the decisive mechanism evidence attached to s4 refers to the wrong artifact. The original evidence is withdrawn; s4's class is withheld while reviewed. Later, sufficient new mechanism evidence under the unchanged rule supports class A for s4. The source-validity evidence was separate and remains intact throughout this scenario.

| Field | Original record | Pending re-adjudication | Corrected record |
|---|---|---|---|
| Selected realizations | 4 | 4 | 4 |
| Accepted class counts | A: 2, B: 2 | A: 2, B: 1 | A: 3, B: 1 |
| Accepted classified population | 4 | 3 | 4 |
| Classification coverage | 1 | 0.75 | 1 |
| Selected realizations established valid | 4 | 4 | 4 |
| Accepted classified-valid population | 4 | 3 | 4 |
| Observed support size | 2 | 2 | 2 |
| Structural entropy, nats | ln(2), approximately 0.693147 | approximately 0.636514 | approximately 0.562335 |
| SCI | 0.5 | 5/9 | 0.625 |
| Effective support, Shannon | 2 | approximately 1.889882 | approximately 1.754765 |
| Effective support, Simpson | 2 | 1.8 | 1.6 |

Both approved population views coincide on the accepted samples in each column, but their denominator changes during review. The selected validity fraction remains 1; invalidating the class evidence did not establish output invalidity. The withheld sample remains in the inventory. No later output replaces it in a fixed prefix.

The correction propagates beyond the displayed core statistics: same-class pair membership, within-class surface diagnostics, any affected condition contrasts, and downstream uncertainty summaries require re-analysis against the same original observations. No numerical values for those unspecified diagnostics are invented here.

The observed support count staying at 2 does not justify retaining the old concentration result. The changed concentration does not demonstrate recursive support loss, model adaptation, or successful recovery: the change was in classification evidence for an unchanged collection. If new evidence had not resolved s4, its unresolved state and the three-sample conditional result would remain visible.

A schema split or merge follows the same impact procedure but additionally changes class-space identity. It cannot be reconstructed from aggregate counts without sufficient sample-level evidence, and all applicable conditions require consistent reassessment.

## 11. Integrity review and reporting

### 11.1 Minimum report attachment

**[Engineering proposal]** The human-readable report and machine-readable evidence metadata must expose the following at their proper scope, reusing existing result/accounting fields where available:

| Report item | Required meaning |
|---|---|
| Data and calculation role | Fixture, pilot, confirmatory collection, or re-analysis basis, plus the actual evidence policy; no automatic promotion by filename. |
| Roles and known dependencies | Identities or auditable pseudonyms; disclosed AI assistance; shared paths and unknown ancestry. |
| Reference and component versions | Stable Core, frontier, incident, and tail registry versions or explicit contents/access state. |
| Validation coverage | Schema/sample evidence, core human annotation and sampled audit records, disagreements, adjudication, and limits. |
| Exposure and calibration | Intended conditioning, prior inspection, judge calibration where applicable, and contamination evidence or unknowns. |
| Four-condition assessment | Evidence and limitations for each condition separately; no synthetic overall score. |
| Correction status | Known outstanding challenges, affected result scope, superseded evidence, and re-analysis disposition. |
| Permitted claims | Evidence-supported wording/scope, restrictions, unmet requirements, and authorizing release decision where one exists. |

A brief headline cannot imply independent validation while burying its absence only in an appendix. Conversely, a missing independence claim does not require replacing a supported count with a fabricated unavailable number. The calculation and interpretation axes remain separate.

Sensitive identity mappings or restricted reference materials may stay private while retaining stable IDs and access-controlled evidence. A public omission has an explicit verification limitation. It must not be reported as an unknown fact when the fact is known internally, or as publicly reproducible evidence when readers lack access. This is a reporting requirement; no access-control service is introduced by Phase 0.

### 11.2 Pre-release review order

**[Engineering proposal]** A future review first checks input identities and evidence-policy acceptance, then role/lineage and validation evidence, then exposure and component dispositions, then correction dependencies and the exact requested claims. The reviewer records requirement outcomes under Section 6.2.

A completed record-presence check establishes only record completeness. Independent origin, class validity, and adequate adjudication require substantive evidence review; software cannot infer them from a complete form. Review can return a restricted or withheld claim without demanding that the system agree with the theory prediction.

Software release and empirical result release remain separate owner-authorized actions. A fixture release may document missing empirical capabilities honestly. A later empirical release pins its own evidence baseline and does not inherit scientific validation from a previous software release.

## 12. Future conformance and scenario checks

**[Engineering proposal]** These are non-executable requirements for Step 7 and later authorized implementation. No implementation tests or empirical audits are claimed here. Their purpose is to make the record/claim behavior testable without requiring favorable model results.

| Check | Required future outcome |
|---|---|
| EI-T01: Nominal plurality | Two provider labels with unresolved ancestry do not produce an automatic independent-evidence claim. |
| EI-T02: Preserved transformation | A copied, paraphrased, translated, human-edited, or parsed artifact retains its upstream derivation. |
| EI-T03: Unknown roots | Missing parents remain an unknown lineage boundary rather than a certified independent source. |
| EI-T04: Sole-lineage loop | A sole generator/classifier/judge/validator lineage withholds the independent empirical claim; a labeled fixture path remains possible. |
| EI-T05: Independent annotation | Two sessions by one person or labels exposed before the initial pass cannot satisfy the two-independent-human core requirement. |
| EI-T06: Core and sampled audit scope | Tier 1 mechanical evidence and sampled audit are preserved alongside the SD core requirement; two annotations for every output are not silently invented. |
| EI-T07: Disagreement | Initial disagreements remain visible after adjudication; unresolved cases do not gain accepted structural mass or disappear from inventory. |
| EI-T08: Calibration and sensitivity | Missing calibration or unperformed sensitivity is not converted to a successful check or zero sensitivity. Provisional AI suggestions remain separately identified. |
| EI-T09: Calculation versus claim | Supported imported-label arithmetic may remain available while its independent-validation claim is restricted. Missing essential mechanism evidence still withholds the affected label. |
| EI-T10: Actual external presence | An empty intake record or stored unused source does not establish ongoing external corrective contribution. |
| EI-T11: Tail protection | Protected/novel cases remain reviewable; rare-case audit additions do not backfill a generation prefix or change the original budget. |
| EI-T12: Versioned registry revision | Removal, split, or merger preserves old entries, reasons, evidence, and affected-result scope; reference changes alone do not invent observed class counts. |
| EI-T13: Exposure | Pilot/calibration exposure and intended reference conditioning remain visible; unknown pretraining exposure cannot become a never-seen claim. |
| EI-T14: Scoped correction | The Section 10.2 scenario changes the correct denominators and dependent values without changing sample identities, validity facts, or generation count. |
| EI-T15: Broad rule defect | A defective shared schema/validator rule identifies all affected records and conditions; revising only a favorable slice fails the contract. |
| EI-T16: Independence-only correction | Withdrawal of an independence assertion updates claim scope even when separately sufficient membership evidence leaves counts unchanged. |
| EI-T17: Passive and private evidence | Imported attachments cannot trigger code/network actions; redacted evidence keeps its real access limitation without claiming public reproducibility. |
| EI-T18: Approval is not evidence | Approving this protocol does not close UD-006's run-specific evidence gap, approve a study result, or authorize implementation/publication. |

## 13. Step 5 acceptance and next gate

**[Engineering proposal]** This submission provides the evidence fields, scoped independence rules, source-specific validation obligations, four-condition/four-component implementation contract, correction example, and claim gates required by Step 5.

| Item | Disposition at delivery |
|---|---|
| Prior scope, definitions, structural-class contract, and metric contract | Approved through OA-004; unchanged. |
| Integrity protocol component of UD-006 | Proposed here; awaiting owner review. |
| Run-specific independent evidence | Outstanding; approving the protocol cannot close it. |
| Hero family, concrete eligible classes, core/audit set, prompts, budgets, and validation route | Step 6 under UD-004/UD-005 and the evidence requirements of UD-006. |
| Complete test mapping and empirical interpretation rules | Step 7. |
| Phase 1, repository, model calls, external evidence collection, generated-code execution, or publication | Not authorized by this step. |

After owner approval and an instruction to continue, Step 6 may create `HERO_BENCHMARK_SPEC.md` and update the decision register. It selects one Tier 1 family; sorting remains the plan's proposal, not an already approved taxonomy. The present deliverables stop at Step 5.
