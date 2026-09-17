# STRUCTURAL_CLASS_CONTRACT

## StructDet-Bench: Structural Equivalence, Assignment Evidence, and Revision

| Field | Value |
|---|---|
| Document version | 0.1 |
| Date | 2026-09-16 |
| Phase / step | Phase 0 / Step 3 |
| Status | PROPOSED STEP 3 CONTRACT; ready for Theory Owner review |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Approved Step 2 baseline | `PROJECT_SCOPE.md` and `DEFINITIONS_AND_UNITS.md`, both version 0.1; approval recorded in OA-002 |
| Decision authority | Theory Owner |
| Decision register | `UNRESOLVED_DECISIONS.md`, version 0.2 |
| Current authorization | Create this contract and update the decision register |
| Implementation / repository / experiment authorization | None |

## 1. Authority, sources, and document responsibility

**[Owner-approved decision]** OA-002 records approval of the delivered Step 2 baseline and its UD-001 through UD-003 recommendations, followed by authorization to proceed with Step 3. The plan and both Step 2 specification files remain unchanged. Their earlier proposed-status headers describe their original delivery; the decision register supplies the subsequent approval record.

This document owns structural equivalence, admissible assignment evidence, classification states, unresolved cases, and schema/assignment revision. The definitions and population meanings in `DEFINITIONS_AND_UNITS.md` remain authoritative. Complete metric estimators belong to Step 4; evaluation independence requirements belong to Step 5; the actual hero task and classes belong to Step 6. Those documents have not yet been produced.

The labels **[Source-derived]**, **[Engineering proposal]**, and **[Owner-approved decision]** retain their Step 2 meanings. An engineering proposal applies until another basis is stated. Proposed requirements use “must” to specify the submitted contract, without implying owner approval.

| Source basis | Contract responsibility |
|---|---|
| SD §§3.2-3.6; SI §3.1 | Context-, horizon-, and resolution-relative equivalence; consequence-sensitive validation. |
| SD §3.7; SI §4.2 | Keep classification uncertainty distinct from structural and realization variation. |
| SD §§6.5, 9.1; SI §§8.5, 12 | Separate structural membership, output validity, and scope of validation. |
| SD §§7, 9.4; SI §§3.1, 8.6 | Predictive and counterfactual checks, independent adjudication, and evidence-backed classification. |
| SD §9.6; SI §9 | Revision, reannotation, lineage visibility, and correction of mistaken categories. |

SD and SI identify the supplied editions and fingerprints registered in the plan. The sources supply principles and measurement objects; the field names, state vocabulary, and workflow below are engineering proposals. No external references within the PDFs have been independently verified in this step.

## 2. Measurement object and first-release classification mode

### 2.1 A structural map and an evidential assignment are distinct objects

**[Source-derived: SD §3.2; SI §3.1]** The deterministic case assigns a realization to a task-bounded structural class. The source notation and equivalence equation are preserved in `DEFINITIONS_AND_UNITS.md`, Section 4.1. The scientific burden includes validating the map through consequences, substitution, intervention, and independent adjudication.

**[Engineering proposal]** A task schema defines the intended class meanings. An assignment record states what the available evidence establishes about one realization under that schema. The measurement process may leave a realization unresolved even when a deterministic structural description would exist with sufficient evidence.

The first release therefore uses a deterministic partition for resolved cases and an explicitly incomplete evidential assignment process. It must not complete the partition by giving every unknown output a residual class. A numeric class-distribution result is conditional on the accepted classified population, as approved in Step 2.

One eligible realization contributes at most one accepted hard class assignment to a given task/schema/resolution and evidence-policy view. Several annotations, repeated reviews, or a new assignment version do not create additional realizations.

### 2.2 Implemented mode and deferred modes

**[Owner-approved decision: OA-002; PROJECT_SCOPE.md §4]** The first milestone and v0.1 import recorded outputs and hard assignments. They do not implement a general structural classifier or execute submitted programs.

**[Engineering proposal; UD-004, contract component]** The proposed mode is `adjudicated_hard_partition_with_unresolved`. This is a semantic mode identifier, not an executable schema declaration.

Probabilistic membership, overlapping classes, and multi-label descriptions remain in the theory catalog. Candidate sets or confidence statements may be retained as evidence attachments, but v0.1 must not convert them to fractional class counts, choose their maximum automatically, or treat annotator disagreement as additional structural diversity. A future soft-assignment implementation requires its own estimator and uncertainty contract. [SD §§3.2, 3.7; SI §§3.1, 4.2]

## 3. Required task-level declarations

**[Engineering proposal]** Every benchmark task used for structural calculations must supply the following human-readable contract. The approved Step 2 fields are reused. Additional names below identify semantic requirements; storage layout and executable schemas remain outside Phase 0.

| Declaration | Required content |
|---|---|
| Task identity and context | `task_id`, `task_version`, `task_context`: problem, admissible input domain, constraints, and what constitutes one realization. |
| Actual conditioning | `conditioning_context_ref`: the supplied prompt, evidence, history, and known dependencies. Unknown components remain explicit. |
| Consequence horizon | `consequence_horizon`: which consequences are evaluated, over which domain/horizon, with applicable units. A resource cutoff and a consequence horizon must be distinguished. |
| Analytic resolution | `analytic_resolution_id` and version: which causal, functional, relational, or mechanism distinctions count; which implementation details are ignored. |
| Load-bearing invariants | Named relations or properties to be preserved within a class, including why each matters to this task. Visible salience or frequency alone is insufficient. |
| Consequence signature | `consequence_signature_spec`: observables or adjudicable consequences corresponding to the invariants, their observation conditions, and tolerances or decision rules. |
| Equivalence rule | `equivalence_rule_ref`: the rule connecting the invariants and their evidence to same-class and different-class decisions. |
| Admissible substitutions | Changes expected to preserve the relevant structure and changes capable of distinguishing mechanisms, within the declared domain. |
| Evidence requirement | Allowed evidence types, the required scope of each, and the assignment decision procedure. |
| Exceptional-case rules | Invalid and incomplete outputs, hybrids, novel candidates, opaque dependencies, and unresolved evidence. |
| Separate validity rubric | `validity_rubric_ref`: task success, completeness, permitted operations, and applicable correctness checks. Validity must not be inferred from a class label. |
| Version and registration | Structural-schema identity/version, relevant registry identity/version, preregistration record, and the correction procedure. |

The consequence signature corresponds to SD's `Φ_T(C,y)`. The software contract need not compute a universal consequence function or the supremum in SD's load-bearingness definition. It must identify an executable, inspectable, formal, or adjudicable route for the selected task and disclose the tested scope. This operational choice does not replace the source definition. [SD §3.6]

### 3.1 Resolution discipline

**[Source-derived: SD §§3.2, 3.6; SI §3.1]** The same outputs can be equivalent at one resolution and different at another. Class meanings depend on the declared consequences and task frame.

**[Engineering proposal]** The task must distinguish properties defining membership from properties checked only by the validity rubric. For example, a mechanism-level contract may admit a recognizable but defective implementation to a mechanism class while recording its invalidity separately. It must state which defects preserve that mechanism and which invalidate the membership evidence.

A structural class cannot acquire a new distinction because a result would otherwise show too little or too much diversity. Unmeasured properties stay outside the claim. A finer analysis requires a separately identified resolution and the necessary validation evidence.

At a sorting-output resolution, equal returned sequences can answer the selected equivalence question. At an algorithm-mechanism resolution, those returned sequences leave the central membership question unanswered. The task contract must state which question is being measured.

### 3.2 Cross-condition compatibility

**[Engineering proposal]** Ordinary, higher-temperature, and structural-divergence conditions retain their actual conditioning records. A common task name does not establish a common class space. Step 6 must identify a shared evaluation frame and explain why class meanings remain compatible across the selected conditions.

A condition that changes permitted operations, input domain, validity constraints, or the relevant horizon may change the admissible structure space. Its outputs require a compatibility decision before a shared-distribution comparison. Separate descriptive reports may remain possible. This step does not select prompts or budgets.

## 4. Required class descriptors and validation routes

### 4.1 Class descriptor

**[Engineering proposal]** Each approved class in a task schema must have a descriptor with the following contents:

| Descriptor item | Required meaning |
|---|---|
| Identity | Stable `structural_class_id` within an identified schema/version; human-readable name kept separate. |
| Membership rule | Mechanism or organization that must be instantiated, expressed as inspectable criteria. Naming a familiar algorithm is insufficient. |
| Constitutive relations | Relevant control/data dependencies, decomposition, decision rule, or causal relations and their applicability conditions. |
| Permitted variation | Changes of presentation or implementation that preserve membership at this resolution, with justification. |
| Boundary and distinguishing evidence | Nearest potentially confusable classes; evidence or consequences that distinguish them. |
| Domain of application | Inputs, assumptions, horizon, and dependencies under which the rule applies. |
| Defect and hybrid policy | Conditions under which an invalid or composite realization remains classifiable, requires another defined class, or becomes unresolved. |
| Validation route | Planned substitution, functional-invariance, intervention, formal/trace, or independent-adjudication checks. |
| Validation record | Available evidence, scope, unresolved findings, reviewer provenance, and status. A plan for validation is distinct from completed validation. |
| Reference role | Link to the reference registry where applicable, including required/relevant/tail designations and their origin. |

A membership rule must make it possible for contrary evidence to overturn an assignment. It must not reduce to “the judge says this is class A,” observed frequency, a model name, or an unvalidated text cluster.

Descriptors must establish how unique membership is decided at the selected resolution. If a realization satisfies two incompatible class rules and no preregistered, consequence-justified boundary resolves the overlap, its assignment remains unresolved. A rule ordering chosen after seeing the output cannot manufacture a unique class. This does not require the registry to enumerate every possible mechanism.

### 4.2 Validation has two levels

**[Source-derived: SD §§7, 9.1, 9.4; SI §§3.1, 8.6]** A structural abstraction must have consequence-sensitive value. Assignments need evidence under that abstraction.

**[Engineering proposal]** Separate:

**Schema-level validation:** Do the selected distinctions preserve the declared invariants within classes and differentiate meaningful mechanisms or consequences across classes? Can the criteria be applied to new realizations without inventing a new interpretation for each output?

**Sample-level validation:** Does this specific realization satisfy the membership criteria, and do the cited evidence records support that decision at the claimed scope?

Every proposed hero class must have a schema-level validation route before Step 6 is approved. Actual class-validation and independent sample evidence are required for corresponding empirical claims. Missing empirical evidence does not prevent a clearly labeled fixture implementation after separate implementation authorization.

Finite tests must retain their limits. A few traces do not establish every possible program behavior; inspection of a declared mechanism does not prove universal correctness. Formal evidence must identify its assumptions and verified scope. The task can use bounded evidence without describing it as exhaustive proof.

### 4.3 Class schema and reference registry

**[Source-derived: SI §§3.1, 8; SD §9.6]** The structural map is task-bounded, and the reference registry records required or relevant classes. The evaluation must remain capable of revising its categories.

**[Engineering proposal]** The structural schema owns class meanings and membership rules. The reference registry owns reference inclusion and designations. These can link to the same class descriptors, but their roles and versions remain separate.

Lack of membership in the current registry does not prove an output invalid or structurally impossible. A candidate outside the current schema receives a review record rather than an invented residual class. Registry coverage can only describe the identified registry; no exhaustiveness claim is implied.

## 5. Admissible evidence and algorithm-specific safeguards

**[Source-derived: SD §§3.2, 9.1-9.4; SI §§3.1, 8.5-8.6]** Structural evidence can include counterfactual substitution, functional invariance, causal intervention, formal or executable checks, and independent adjudication. The sources distinguish structural equivalence from lexical or embedding similarity.

**[Engineering proposal]** Evidence must be tied to the exact realization, applicable class descriptor, observation conditions, and review record.

| Evidence type | Possible contribution | Required limitation |
|---|---|---|
| Inspectable control/data flow | Supports the presence and causal role of a mechanism in the submitted artifact. | Comments, names, unused fragments, or unreachable branches alone do not establish implemented membership. |
| Instrumented execution trace | Shows mechanism-relevant operations or dependencies for specified inputs and an identified environment. | A trace covers its recorded execution; it cannot silently stand for all branches or the full input domain. |
| Formal or mechanistic argument | Establishes a declared property under identified assumptions. | The proof target must match the class distinction; output correctness alone may leave mechanism unspecified. |
| Counterfactual or substitution evidence | Tests whether permitted changes preserve invariants or structural changes alter relevant consequences. | Changes, controls, observation scope, and results must be recorded. |
| Independent human/domain adjudication | Resolves membership using cited criteria and evidence. | Reviewer identity, procedure, disagreement, and provenance remain necessary; human authorship alone does not establish independence. |
| Model suggestion, parser label, embedding similarity | May propose candidates or help locate material for review. | Cannot alone establish structural equivalence or independently validated membership. |
| Output tests or generator self-description | Output tests may support a scoped validity assessment; self-description may identify a claim to investigate. | Matching returned values and assertions about an algorithm do not establish algorithm-family membership. |

The first release imports such records. It does not implement a live parser/classifier, call a judge model, or execute generated code. Imported execution evidence must identify the output content, test inputs, environment, observations, and evidence origin. Its presence does not authorize execution inside this project.

For algorithm-family analysis, a task-specific evidence rule must address reachable control flow, data transformation, relevant branches, and dependency behavior to the extent needed by its resolution. An opaque library call remains unresolved at that resolution when its mechanism cannot be established. A separate dependency-level class would require an explicitly approved resolution and class definition.

A repaired program is a changed artifact. Analysis must retain the original realization and distinguish any separately recorded transformation; it must not substitute repaired behavior as evidence that the original generation was valid or instantiated the corrected mechanism.

## 6. Assignment records, states, and acceptance

### 6.1 Required record contents

**[Engineering proposal]** Extend the Step 2 assignment inventory only as needed to express this contract. An assignment record must link the sample and output identity; task/schema/resolution versions; proposed or committed class; evidence and relevant locations; method and decision rationale; classifier/reviewer roles; uncertainty or disagreement; and revision lineage.

The record also identifies an `assignment_evidence_policy_id` and version. This policy determines whether a label can enter a named analysis view. It does not replace the separate lineage and empirical-claim gates in Step 5.

Each stored revision has a unique `assignment_id`, an explicit `assignment_version`, and `supersedes_assignment_id` when applicable. Revisions retain `sample_id`. A run pins the exact assignment revisions it uses; it must not resolve a mutable “latest label” differently on re-analysis.

### 6.2 Assignment and review axes

**[Engineering proposal]** Use separate axes:

| `assignment_status` | Meaning | Class treatment |
|---|---|---|
| `assigned` | A specific hard class is asserted under the named schema. | A class ID is present. Inclusion still requires the applicable evidence policy. |
| `unresolved` | Classification was attempted, but the rule or evidence does not support a unique accepted decision. | No committed class ID. Candidate IDs and reasons may be retained outside counts. |
| `unclassified` | No applicable classification has been completed or established. | No committed class ID; record the reason. |

| `assignment_review_status` | Meaning | Inference boundary |
|---|---|---|
| `fixture` | A declared label or outcome created for a software demonstration or test specification. | Does not establish empirical classification or independent validation. |
| `provisional` | A candidate judgment awaiting the required review/evidence checks. | Preserved for review; excluded from the two standard metric views. |
| `adjudicated` | The named decision procedure has concluded, with an evidence-linked decision record. | Can include an explicitly unresolved outcome. Independence and source-protocol compliance still require their own evidence. |

An `assigned`/`provisional` record may contain a proposed class ID without contributing a count. An `unresolved`/`adjudicated` record states that review concluded without a defensible unique class. These combinations keep workflow completion separate from epistemic resolution.

A review-state change requires a new record revision. A self-declared `adjudicated` string without the supporting record does not satisfy the evidence policy.

### 6.3 Separate validity axis

**[Engineering proposal]** `validity_status` has the following semantic outcomes: `valid` under the named rubric, `invalid` under that rubric, `undetermined` after inconclusive assessment, and `not_assessed` when no assessment was performed. Evidence, test scope, and rubric version accompany assessed outcomes.

These are assessment outcomes, distinct from the metadata knowledge states `known`, `unknown`, `unavailable`, and justified `not_applicable`. Missing validity records must not be converted to an observed invalidity or an invented successful assessment.

Membership does not imply validity. A failed test does not automatically erase identifiable mechanism evidence. Conversely, an error that changes a load-bearing relation cannot be ignored to preserve an expected algorithm-family label. The task descriptor's defect policy decides whether the remaining evidence supports membership.

### 6.4 Evidence policies for the initial slice

**[Engineering proposal]** Define two bounded policies, without adding a new scoring capability:

| Policy | Acceptance for calculations | Permitted interpretation |
|---|---|---|
| `fixture_only` | Schema-consistent, explicitly designated fixture assignments and fixture validity records. | Software demonstration under stipulated inputs. |
| `adjudicated_import` | Imported adjudicated assignments with applicable membership evidence, a unique selected revision, and no unresolved contradiction affecting the assignment. | Label-conditioned summaries of the supported classified subset; stronger empirical interpretation also requires Step 5 evidence gates. |

Fixture and empirical assignments must not be silently mixed in one distribution. A real output used in a fixture exercise retains its original provenance and any stipulated label is identified as such. Relabeling an inadequate empirical study as a fixture cannot establish its missing evidence.

Adjudicated records with missing essential membership evidence are withheld from `adjudicated_import`, with a reason. Missing independent lineage evidence may instead restrict empirical claims while leaving a supported, explicitly qualified label-conditioned summary possible. Step 5 owns the exact independence gate; this contract does not certify it in advance.

### 6.5 Connection to approved population views

**[Owner-approved decision: OA-002, UD-003]** `classified_all` and `classified_valid` retain the meanings in `DEFINITIONS_AND_UNITS.md`, Section 5.

**[Engineering proposal]** Apply them after evidence-policy acceptance:

| Case | `classified_all` | `classified_valid` | Additional record |
|---|---|---|---|
| Accepted hard assignment; accepted validity assessment is `valid` | Included | Included | Evidence and both rubric/schema identities. |
| Accepted hard assignment; assessed `invalid` | Included | Excluded | Invalidity reason and test scope. |
| Accepted hard assignment; validity undetermined, not assessed, or unavailable | Included | Excluded | Exact validity/evidence limitation. |
| Assigned but provisional, conflicting, superseded, or lacking essential membership evidence | Excluded | Excluded | Rejection/review reason retained. |
| Unresolved or unclassified | Excluded | Excluded | Candidate evidence and status retained. |

The validity assessment used for the valid view must itself satisfy the declared evidence policy; fixture validity cannot silently validate an empirical assignment. No row disappearance is implied by exclusion from a metric view. Counts by classification, validity, completion, selection, and evidence acceptance remain separate and reconcile to their respective inventories. Step 4 owns the exact denominators and unavailable-result behavior.

## 7. Exceptional outputs and unresolved mechanisms

**[Engineering proposal]** The reason vocabulary below describes cases; these reasons are never structural class IDs. It may be represented in the existing uncertainty/disagreement references or a scoped `classification_reason` field.

| Case | Required treatment |
|---|---|
| Invalid but recognizable mechanism | Assign only if the declared defect policy and mechanism evidence still establish membership. Retain invalidity separately. |
| Defect changes the defining relation | Test against other approved descriptors if evidence permits; otherwise retain unresolved classification. Do not classify the intended, repaired, or advertised algorithm in place of the observed artifact. |
| Hybrid covered by a preregistered composite class | Assign to that one class only if its rule is unambiguous and disjoint at the selected resolution. Components do not become extra samples. |
| Hybrid without an applicable unique class | `unresolved`, with `hybrid_boundary` reason and component evidence. A “dominant mechanism” rule is permitted only if preregistered and justified at the selected resolution. |
| Apparently new mechanism | `unresolved`, with `novel_candidate` reason; preserve description and differentiating evidence for schema review. This label makes no claim of historical novelty. |
| Several existing classes remain plausible | `unresolved`, with `insufficient_discrimination` or `conflicting_evidence` and the candidate set. Do not break the tie using score direction. |
| Opaque dependency or unavailable decisive branch evidence | `unresolved` when candidate mechanisms are plausible; otherwise `unclassified`. Record what is unknown or unavailable. |
| Incomplete or truncated output | Preserve completion status. A class may be assigned only when the task's completeness/defect rule permits it and evidence supports the observed artifact; validity is separate. |
| Refusal, empty response, or no applicable realization | Retain attempt/completion history and `unclassified` where a sample exists. Do not create a “refusal mechanism” solely to increase support. |
| Output outside the preregistered task domain | Apply the recorded selection rule and preserve the excluded sample. Out-of-scope status must not be used for an inconvenient but eligible rare structure. |
| Classification not attempted | `unclassified`, with `not_assessed` reason. It is distinct from attempted but inconclusive review. |

A completed hybrid may still fall within an existing class when all additional operations are explicitly non-load-bearing at this resolution. That judgment needs the same evidence as other assignments. A multi-mechanism response can yield multiple realizations only under the extraction/grouping rule approved for the study; classification must not invent extra observations afterward.

An apparent new class triggers versioned review under Section 10. Neither a universal `other` bucket nor one automatically unique class per unknown output is allowed. Both approaches would impose an unsupported structural partition.

## 8. Pairwise judgments and partition consistency

**[Source-derived: SD §9.1; SI §3.1]** Pairwise substitution judgments can support task-bounded structural families. Equality under a validated deterministic map defines an equivalence relation.

**[Engineering proposal]** Pairwise evidence records identify the ordered sample pair, schema/resolution, common evaluation conditions, applicable invariants, evidence, and review status. Outcomes are `equivalent`, `non_equivalent`, `unresolved`, or `not_comparable`. The last two outcomes establish neither equivalence nor difference.

Accepted pairwise evidence must be consistent with a reflexive, symmetric, transitive partition on the comparable resolved cases. An observation that two behaviors are within a numerical tolerance on one test does not by itself supply an equivalence relation over all realizations. The registered class rule must address that distinction.

For an adjudicated record claiming A equivalent to B and B equivalent to C, another adjudicated record claiming A non-equivalent to C exposes an inconsistency. The procedure must:

1. Check task/schema/resolution and evidence versions, sample identity, observation conditions, and transcription errors.
2. Identify whether the conflict concerns a sample judgment or the class definition itself.
3. Preserve the original judgments and request evidence-linked adjudication or a versioned schema correction.
4. Withhold affected assignments from an accepted partition until resolved. Valid unaffected subsets may remain reportable with their coverage and limitations.

A schema-level defect that undermines all class meanings blocks results relying on that schema. A local label conflict need not stop unrelated, adequately supported cells. The impact assessment must justify the distinction.

Do not resolve contradictions by majority vote alone, first/last label wins, nearest-cluster assignment, or unexamined connected-component closure. A connected path of tentative similarities must not erase an explicit contradictory judgment. Missing pairwise evidence must not be converted into `non_equivalent`.

Direct class-rule assignments do not require an exhaustive all-pairs comparison. Where several realized pairs are checked, the check set and its coverage are recorded. A consistent set of checked pairs does not certify all unexamined pairs or validate an otherwise unsupported ontology.

## 9. Conceptual cases for later fixtures

**[Engineering proposal]** These are constructed acceptance examples, not model observations, benchmark results, or approved hero classes. Names such as mechanism A/B denote hypothetical descriptors. Actual task/domain rules and evidence must be approved in Step 6. Each example specifies the evidence that would support the stated treatment.

| Case | Declared frame and evidence | Expected contractual treatment |
|---|---|---|
| CC-01: Different wording, same mechanism | At a mechanism resolution, two realizations differ in names, comments, and presentation. Inspection under a registered descriptor establishes the same relevant control/data dependencies; permitted substitutions preserve its signature. | One structural class, subject to evidence acceptance; realization variation remains separately measurable. |
| CC-02: Similar wording, different mechanism | Two descriptions use the same opening and claim to sort a sequence. The recorded implementations instantiate different decomposition/recombination rules, and a prespecified mechanism-sensitive inspection or trace distinguishes them. | Different classes only if both rules belong to validated, distinct descriptors. Wording similarity has no deciding role. |
| CC-03: Matching returned values, unresolved family | Both outputs pass recorded input/output tests, but the only available mechanism evidence is their self-description or an opaque call. | Tests may support scoped validity; algorithm-family membership remains unresolved or unclassified. No mechanism is inferred from the result alone. |
| CC-04: Recognizable but invalid implementation | The hypothetical descriptor explicitly separates decomposition strategy from complete element preservation. Inspection establishes the strategy, while a recorded output test demonstrates a loss of an element within that descriptor's allowed defect boundary. | Classifiable in `classified_all`; excluded from `classified_valid`. If the defect changes the constitutive decomposition, the premise fails and membership must be reconsidered. |
| CC-05: Unregistered hybrid | A realization selects mechanism A or B by an input-dependent branch, and the current schema has no applicable composite rule. | Unresolved hybrid with branch evidence; neither two observations nor an automatically new class. |
| CC-06: Novel candidate | Evidence describes an eligible mechanism distinguishable from the registered ones, but its own boundary and validity have not been adjudicated. | Preserve a novel-candidate record and review it. No immediate increase in accepted support and no deletion of the candidate. |
| CC-07: Pairwise contradiction | Same-frame accepted judgments report A~B, B~C, and A not equivalent to C. | Withhold affected partition assignments pending adjudication; retain the contradictory evidence. |
| CC-08: Misleading label and unused fragment | A program announces mechanism A and contains an unused fragment resembling A. Reachable control/data flow supports only a different registered mechanism B. | Use evidence for B if adequate. The heading and unused fragment cannot establish A. |
| CC-09: Truncation hides a decisive step | Partial output is compatible with several mechanisms; its unfinished portion would determine which applies. | Preserve truncation and unresolved classification. Do not complete the program mentally and count that completion. |
| CC-10: Same class, uncertain validity | Accepted mechanism evidence exists; validity was not assessed or tests were inconclusive. | Included in the all-classified view only; disclose the validity limitation. |

These cases establish how a future implementation should handle evidence. They do not assert that the hypothetical memberships have already been independently validated. Cases involving inspection, traces, or tests describe imported evidence requirements; nothing is executed in Phase 0.

## 10. Preregistration, schema versions, and new distinctions

### 10.1 Freeze before confirmatory classification

**[Source-derived: SD §§9.1, 9.4, 9.6; SI §§8.6, 9]** Structural criteria should be declared before inspecting evaluated outputs wherever feasible, while correction must remain possible.

**[Engineering proposal]** Before a confirmatory collection is classified, record the task/schema/resolution and registry versions, class descriptors, exceptional-case rules, evidence policy, selected validation procedure, responsible roles, and actual registration/exposure history. The study's more detailed sampling freeze belongs to Step 6.

Schema design may use clearly designated pilot or reference material with disclosed origin. Material used to choose class boundaries cannot silently become untouched confirmatory evidence for those same choices. If evaluated outputs have already been inspected, disclose the exposure and limit the analysis to the design that can actually be supported.

A timestamp and file hash establish the identity and recorded order of the declared artifact. They do not by themselves establish independent origin, lack of benchmark exposure, or absence of undocumented prior inspection.

### 10.2 Version rules

**[Engineering proposal]** Distinguish input-format version, structural-schema version, resolution version, reference-registry version, and assignment revision. A class name alone is never a sufficient join key for measurement compatibility.

| Change | Required action |
|---|---|
| Editorial clarification with unchanged meaning | Record a revision and explicit semantic-compatibility statement, with reviewed rationale. |
| Correction of one assignment under unchanged rules | Create a new assignment record; retain the prior record and affected run references. |
| Split, merge, or change of class meaning | Create a new structural-schema version and explicit old/new mapping or non-mappability record. Re-adjudicate affected samples. |
| New eligible mechanism | Review evidence and boundaries, then add it only through an approved schema/registry revision. |
| Changed horizon, domain, or load-bearing resolution | Treat as a potentially different measurement object; do not silently reuse old memberships. |
| Changed registry membership/designation | Version the registry; re-evaluate any affected registry-relative interpretation. |

New versions do not automatically qualify for pooling. A class split cannot be reconstructed from old aggregate counts without supporting sample-level evidence. Identically named classes in different versions may have different meanings.

### 10.3 Keep correction open without retroactive confirmation

**[Engineering proposal]** Preserve the original frozen analysis. A later correction or new class produces a separately identified re-analysis with its exposure and revision basis stated. Reassess all affected conditions, including previously unresolved cases; selective revision of only the favorable condition is prohibited.

Affected old claims may need to be marked superseded or withheld. A revised analysis of the same observations remains a re-analysis, without acquiring a new sample size or untouched confirmatory status. Additional independently collected evidence is needed for a fresh confirmatory claim where the revised criteria were learned from the original observations.

Rare valid candidates must not disappear because they fit the current schema poorly or lower average performance. Retain their evidence for revision and the later tail registry. The precise independent-review and release requirements belong to Step 5.

## 11. Correction propagation and evidence withdrawal

**[Source-derived: SD §9.6; SI §9]** Corrective capacity includes revising mistaken categories, labels, and evaluation records, with re-evaluation after correction.

**[Engineering proposal]** Every correction record identifies the trigger and evidence, affected task/schema/class/assignment versions, responsible decision, replacement or unresolved status, impacted runs, and re-analysis disposition.

The minimum dependency path is:

**Evidence or schema correction → affected assignments → accepted populations → dependent metrics/comparisons → revised report or explicit unavailability.**

This is a specification for later implementation, not a claim that a propagation engine exists. Step 5 owns governance and lineage checks; this document owns classification dependencies.

Withdrawal of an essential trace, proof, or adjudication record requires reassessing the affected assignments. Contradictory or superseded evidence stays in the audit history. If an alternative sufficient basis remains, retain membership only with a new evidence-linked decision; otherwise withhold it. The input sample remains available and its absence from the accepted population must be visible.

An exact content hash links evidence to bytes. It does not establish the truth of the evidence or the independence of two copied reports. Those properties require their own records.

## 12. Downstream reporting obligations and inference boundaries

**[Engineering proposal]** A class-based result must identify the selected schema/resolution, evidence policy, exact assignment revisions, accepted population, validity rubric, and unresolved/excluded evidence. The report must distinguish provisional suggestions, fixtures, adjudicated imports, and the actual status of independent validation.

The reporting path must preserve:

- counts of assigned, unresolved, and unclassified realizations;
- evidence-acceptance and conflict reasons;
- validity/completion/selection accounting on their separate axes;
- original sample/group identities and correction links.

Step 4 defines numerical denominators, coverage summaries, uncertainty, and zero-population behavior. No score or estimator is introduced by this document. Provisional votes, candidate class lists, missing evidence, and registry entries without observed samples do not contribute occupied classes.

**[Source-derived: SD §§5, 6.5, 12; SI §§3.3, 12]** These assignments do not establish full model capacity, latent-support extinction, validity from concentration, or recursive collapse from one fixed-model batch. Source labels and nominal role separation do not establish independent structural evidence.

## 13. Future conformance checks

**[Engineering proposal]** These are non-executable requirements for Step 7 and later implementation. No implementation tests have been run. CC references identify the constructed examples above.

| Check | Required future outcome |
|---|---|
| SC-T01: Declared measurement frame | Missing task/schema/resolution or an essential membership rule blocks affected structural calculations, while inventory review remains available. |
| SC-T02: Within-class substitutions | Approved non-load-bearing presentation changes preserve the expected class when their evidence and applicability conditions hold. CC-01. |
| SC-T03: Mechanism-sensitive difference | Similar wording cannot erase validated mechanism differences. CC-02. |
| SC-T04: Correctness/membership separation | Equal returned values cannot establish an unobserved algorithm family. CC-03. |
| SC-T05: Invalid/undetermined validity | Recognizable invalid outputs and valid-unassessed outputs receive the correct separate population treatment. CC-04, CC-10. |
| SC-T06: Hybrids and new candidates | Unresolved composites and candidate mechanisms remain review records, without fractional, duplicate, or automatically new class counts. CC-05, CC-06. |
| SC-T07: Pairwise inconsistency | A contradictory equivalence triangle prevents accepted affected partition assignments; unrelated supported cells are not automatically discarded. CC-07. |
| SC-T08: Labels and irrelevant code | Self-description and unused fragments cannot override mechanism evidence. CC-08. |
| SC-T09: Incomplete output | A missing decisive operation is not fabricated during assignment. CC-09. |
| SC-T10: Evidence-policy isolation | Provisional or inadequately supported labels cannot enter standard views; fixture results cannot be relabeled as validated empirical results. |
| SC-T11: Assignment uniqueness | Duplicate/superseded/conflicting revisions do not multiply sample counts; the selected revision is explicit. |
| SC-T12: Version compatibility | Same-named classes from incompatible schemas cannot be silently pooled; splits require sample-level reassessment. |
| SC-T13: Correction propagation | An evidence or schema correction identifies impacted assignments/results and preserves the original analysis history. |
| SC-T14: Group preservation | Class assignment or adjudication never converts coordinated samples into independent calls. |
| SC-T15: Uncertainty preservation | Unknown evidence or unresolved membership is retained without a numeric sentinel class, inferred agreement, or invented confidence. |
| SC-T16: Passive input boundary | Importing code and execution evidence does not run the code or authorize remote evaluation. |

Passing these eventual checks demonstrates contract-following software. Actual scientific measurement validity and prediction outcomes require their separate evidence.

## 14. Step 3 acceptance and handoff

**[Engineering proposal]** This submission supplies the task/class requirements, evidence routes, state vocabulary, paired-population interface, exceptional-case rules, pairwise consistency procedure, conceptual examples, and versioned correction obligations required by the plan's Step 3.

The current approval request is the **contract component of UD-004**. No algorithm list, hero family, input domain, provider, sampling budget, independent annotation set, or empirical result is approved by this document.

| Item | Current disposition |
|---|---|
| Step 2 scope, core definitions, and population meanings | Approved through OA-002; unchanged. |
| General structural-class contract | Proposed here; awaiting owner review. |
| Concrete hero class descriptors and validation routes | Due in Step 6 under UD-004; not a blocker to Step 4 specification. |
| Full estimators, denominators, proxy, and statistical procedures | Due in Step 4 and the Step 6 experiment design under UD-005. |
| Independent validation evidence | Remains open under UD-006; limits corresponding empirical claims. |
| Soft assignments and latent diagnostics | Deferred under the approved scope; no added entry condition. |
| Implementation and experiments | Remain unauthorized. |

Approval of this step would fix the proposed classification contract and permit the next expressly authorized step. It would not resolve the hero-task portion of UD-004, supply independent empirical evidence, or authorize code. The next planned artifact is `METRICS_SPEC.md` in Step 4, accompanied only by the permitted decision-register update.
