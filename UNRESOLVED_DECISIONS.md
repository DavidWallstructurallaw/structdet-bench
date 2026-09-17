# UNRESOLVED_DECISIONS

## StructDet-Bench: Phase 0 Decision and Authorization Register

| Field | Value |
|---|---|
| Document version | 0.7 |
| Record date | 2026-09-17 |
| Phase / step | Phase 0 / Step 8 |
| Status | ACTIVE REGISTER; Step 7 approved; integrated Step 8 audit and three corrective revisions awaiting owner acceptance |
| Decision authority | Theory Owner |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Related files | `PROJECT_SCOPE.md`; `DEFINITIONS_AND_UNITS.md`; `STRUCTURAL_CLASS_CONTRACT.md`; `METRICS_SPEC.md`; `EVALUATION_INTEGRITY.md`; `HERO_BENCHMARK_SPEC.md`; `THEORY_TO_CODE_TRACEABILITY.md`; `VALIDATION_AND_FALSIFICATION.md` |
| Implementation authorization | None |

## 1. Register rules

**[Owner-approved decision: governing plan §§5, 7]** This register records actual decisions and their specific effects. It does not turn future capabilities into prerequisites for unrelated work.

**[Owner-approved decision: OA-007]** The delivered Step 7 traceability and validation contracts have been approved. Prior specification approvals remain in force. The authorized current action is the integrated Step 8 audit, finding-limited corrections to the eight eligible specifications, and this register update. The governing plan remains read-only.

**[Audit proposal]** Step 7's mapping and fixed-suite outcome convention are adopted in OA-007. Findings AF-001 through AF-003 align existing contracts without changing the adopted task, formulas, denominators, experiment, bands, or source requirements. Their corrective text and this audit await owner acceptance. An OPEN evidence component remains open until the scoped evidence is supplied and reviewed. Source-derived requirements remain attributed; an operational choice never becomes a source definition. UD-006's approved protocol and outstanding independent evidence remain separate.

Approval of a specification does not supply missing empirical evidence or authorize implementation. An entry may have separately tracked components when the existing plan schedules their decisions at different steps. This avoids treating a pending hero-task selection as a reason to withhold review of the general classification contract.

Blocker classes follow the governing plan:

| Class | Effect |
|---|---|
| Implementation-blocking | Must be resolved before the affected Phase 1 capability is implemented correctly or safely. It does not automatically block the next planned specification step. |
| Empirical-claim-blocking | Allows identified prototype work, while withholding the specified scientific interpretation until evidence is supplied. |
| Deferred | Outside the bounded milestone; has no effect on starting that milestone. |

The “due gate” identifies when a decision is required. Routine work assigned to a later step remains at that step. Missing independent evidence is not silently treated as a product-design failure.

## 2. Actual authorization record

### OA-001: Proceed with Step 2

This is the historical authorization record at Step 2 entry. The then-pending approval and later-step fields below are superseded, where stated, by OA-002 through OA-007.

**[Owner-approved decision]** After the next action was described as approving the plan and generating `PROJECT_SCOPE.md`, `DEFINITIONS_AND_UNITS.md`, and `UNRESOLVED_DECISIONS.md`, the owner instructed: “可以，继续” (“Yes, continue”).

| Field | Record |
|---|---|
| Conversation date | 2026-09-16 |
| Authorized action | Execute Phase 0 Step 2 under the supplied plan and deliver its three files. |
| Source plan identity | Version 0.1; SHA-256 below. |
| Step 2 content approval | Pending review of the delivered files. |
| Step 3 authorization | Not yet received. |
| Phase 1 / repository / experiment authorization | Not received. |

Plan SHA-256:

`5df37f3fef1d012d462a116d7839909c9379dfe6d59a1b3356cae004bcfac6a4`

The plan's original “PROPOSED PLAN” header predates this conversation authorization. Its bytes have been preserved because Step 2 permits writes only to its three deliverables. This record supplies the subsequent authorization context without rewriting the plan or manufacturing approval of future documents.

**[Engineering verification record]** The supplied SD and SI file hashes match the fingerprints in the plan. No independent validation of their cited external publications was performed in this step.

### OA-002: Approve Step 2 and proceed with Step 3

This historical record describes Step 3 entry. Its then-pending Step 3 review and Step 4 authorization fields are superseded by OA-003 below.

**[Owner-approved decision]** The preceding delivery identified the three Step 2 files, requested approval of the recommendations in UD-001 through UD-003, and stated that approval would lead to `STRUCTURAL_CLASS_CONTRACT.md` plus an updated decision register. The owner replied: “可以，继续” (“Yes, continue”).

| Field | Record |
|---|---|
| Conversation date | 2026-09-16 |
| Approved content | Delivered Step 2 versions 0.1 of `PROJECT_SCOPE.md`, `DEFINITIONS_AND_UNITS.md`, and this register; recommended decisions UD-001 through UD-003. |
| Authorized next action | Execute Phase 0 Step 3: create `STRUCTURAL_CLASS_CONTRACT.md` and update `UNRESOLVED_DECISIONS.md`. |
| Preserved files | `PHASE_0_PLAN.md`, `PROJECT_SCOPE.md`, and `DEFINITIONS_AND_UNITS.md`; no revision requested. |
| Step 3 content approval | Pending review of the newly delivered contract. |
| Step 4 authorization | Not yet received. |
| Phase 1 / repository / model-call / experiment authorization | Not received. |

The approved Step 2 file identities are:

| File | Approved version | SHA-256 |
|---|---|---|
| `PROJECT_SCOPE.md` | 0.1 | `2eec02825c8df4281cc538d00dcb809907dc2eb8a2b1b73b597cbab17d975a11` |
| `DEFINITIONS_AND_UNITS.md` | 0.1 | `a3da3e356a21f59468178050944baf58787edd65204fbf40b3b1742cd38104ab` |
| `UNRESOLVED_DECISIONS.md` | 0.1, before this update | `95fcfab5a7326fea52dd8bd19229559a5cc1eb8d7767f69c6862e9792fe5b072` |

The final row identifies the prior delivered register, not this version's own bytes. The Step 2 specification headers remain unchanged as historical delivery metadata. This record establishes their approval without expanding the current step's write permissions.

**[Scope of approval]** The approval fixes the first milestone/release boundary, source conventions, conceptual observation units, paired population views, and metadata meanings. It does not approve unproduced classification procedures, complete estimators, hero-task classes, or empirical claims. Those items retain their scheduled gates below.

### OA-003: Approve the Step 3 general contract and proceed with Step 4

This historical record describes Step 4 entry. Its then-pending Step 4 approval and Step 5 authorization fields are superseded by OA-004 below.

**[Owner-approved decision]** The preceding delivery presented `STRUCTURAL_CLASS_CONTRACT.md`, version 0.1, and the updated register, requested approval of UD-004's general-contract component, and stated that the next step would create `METRICS_SPEC.md` and update this register. The owner replied: “可以，继续” (“Yes, continue”).

| Field | Record |
|---|---|
| Conversation date | 2026-09-16 |
| Approved content | Delivered Step 3 structural-class contract version 0.1 and register version 0.2; recommendation A for UD-004's general-contract component. |
| Authorized current action | Execute Phase 0 Step 4: create `METRICS_SPEC.md` and update `UNRESOLVED_DECISIONS.md`. |
| Preserved files | The plan, scope, definitions, and structural-class contract; no revision requested. |
| Step 4 content approval | Pending review of the newly delivered metric specification. |
| Step 5 authorization | Not yet received. |
| Phase 1 / repository / model-call / experiment authorization | Not received. |

The approved Step 3 file identities are:

| File | Approved version | SHA-256 |
|---|---|---|
| `STRUCTURAL_CLASS_CONTRACT.md` | 0.1 | `00ba09dd879f5fe02a3302a6f1ad36bda1c6b7e2723562f5f62ec85fed125328` |
| `UNRESOLVED_DECISIONS.md` | 0.2, before this update | `a5c49cbd2b43656d6946def9fc546ba7e9bd4d36af4af479d3a821c3623e0b90` |

The register fingerprint identifies the prior delivered version, not this version's own bytes. The structural contract's original proposed-status header remains historical delivery metadata; this authorization record supplies its later approval.

**[Scope of approval]** The hard-assignment mode with unresolved cases, task-bounded evidence contract, separate assignment/review/validity axes, fixture/adjudicated-import acceptance policies, and revision/correction rules are adopted. The approval does not select a hero family or algorithm list, approve this new metric specification, establish independent experimental evidence, or authorize implementation.

### OA-004: Approve the Step 4 metric contract and proceed with Step 5

This historical record describes Step 5 entry. Its then-pending Step 5 approval and Step 6 authorization fields are superseded by OA-005 below.

**[Owner-approved decision]** The preceding delivery presented `METRICS_SPEC.md`, version 0.1, and register version 0.3, requested approval of UD-005's metric/diagnostic component, and stated that the next step would create `EVALUATION_INTEGRITY.md` and update this register. The owner replied: “可以，继续step 5” (“Yes, continue with Step 5”).

| Field | Record |
|---|---|
| Conversation date | 2026-09-16 |
| Approved content | Delivered Step 4 metric specification version 0.1 and register version 0.3; UD-005's metric/diagnostic recommendation. |
| Authorized current action | Execute Phase 0 Step 5: create `EVALUATION_INTEGRITY.md` and update `UNRESOLVED_DECISIONS.md`. |
| Preserved files | The plan, scope, definitions, structural-class contract, and metric specification; no revision requested. |
| Step 5 content approval | Pending review of the newly delivered integrity contract. |
| Step 6 authorization | Not yet received. |
| Phase 1 / repository / model-call / evidence-collection / experiment / publication authorization | Not received. |

The approved Step 4 file identities are:

| File | Approved version | SHA-256 |
|---|---|---|
| `METRICS_SPEC.md` | 0.1 | `ec75688060b7f2937ff480ebb1f8cfd8fe96ec920962e5ff404a1367fe9a7c0f` |
| `UNRESOLVED_DECISIONS.md` | 0.3, before this update | `05b023b451a5fb5700bfbbbe88377c5395ba908943e08cb886f5b8fdd3b8fe7e` |

The register fingerprint identifies the preceding delivered version, not this version's own bytes. The metric specification's original proposed-status header remains historical delivery metadata; this record establishes its later approval without changing the approved file.

**[Scope of approval]** The first-slice estimator and denominator rules, explicit result states, fixed-prefix distinct-k, lexical-trigram surface diagnostic, separate structural pair diagnostic, bounded P1/P5 contrast conventions, and paired prompt-block uncertainty procedure are adopted. The approval does not select a hero taxonomy, model/provider, collection budget, core validation set, audit sample, or actual experiment. It does not establish independent annotation evidence, approve this new integrity contract, or authorize implementation.

### OA-005: Approve the Step 5 integrity protocol and proceed with Step 6

**[Owner-approved decision]** The preceding delivery presented `EVALUATION_INTEGRITY.md`, version 0.1, and register version 0.4, requested approval of UD-006's protocol component, and identified `HERO_BENCHMARK_SPEC.md` plus this register as the next deliverables. The owner replied: “可以，继续step 6” (“Yes, continue with Step 6”).

| Field | Record |
|---|---|
| Record date | 2026-09-17; the exact local timestamp of the owner's message is not asserted. |
| Approved content | Delivered Step 5 integrity contract version 0.1 and register version 0.4; Option A for UD-006's protocol component. |
| Authorized current action | Execute Phase 0 Step 6: create `HERO_BENCHMARK_SPEC.md` and update `UNRESOLVED_DECISIONS.md`. |
| Preserved files | The plan, scope, definitions, structural-class contract, metric specification, and integrity contract; no revision requested. |
| Step 6 content approval | Pending review of the newly delivered hero specification. |
| Step 7 authorization | Not yet received. |
| Phase 1 / repository / model-call / evidence-collection / execution / publication authorization | Not received. |

The approved Step 5 file identities are:

| File | Approved version | SHA-256 |
|---|---|---|
| `EVALUATION_INTEGRITY.md` | 0.1 | `50c5529c16164ee53e4d99502ed1ec24202f36152b36281870bf285185672dc3` |
| `UNRESOLVED_DECISIONS.md` | 0.4, before this update | `6a8b776ab18a563f7ee2928dbd20872feae1bede5897c7d51a07d0fe1b80d457` |

The register fingerprint identifies the preceding delivered version, not this version's own bytes. The integrity contract's original proposed-status header remains historical delivery metadata; this record establishes its later approval without changing the approved file.

**[Scope of approval]** The four-condition/four-component integrity design, scoped provenance and independence records, role separation, core independent annotation and Tier 1 audit obligations, evidence-dependent claim gates, and correction rules are adopted. This approval supplies no actual reference corpus, independent annotations, experimental outputs, validation environment, or audit findings. It does not approve the new hero choices or grant collection, execution, implementation, spending, or publication permission.

### OA-006: Approve the Step 6 hero contract and proceed with Step 7

**[Owner-approved decision]** The preceding delivery presented `HERO_BENCHMARK_SPEC.md`, version 0.1, and register version 0.5, requested review of UD-004's hero-task and UD-005's concrete experiment-design components, and identified Step 7's two specifications as the next deliverables. The owner replied: “继续step 7” (“Continue with Step 7”).

| Field | Record |
|---|---|
| Record date | 2026-09-17; the exact local timestamp of the owner's message is not asserted. |
| Approved content | Delivered Step 6 hero contract version 0.1 and register version 0.5; the recommended bounded sorting task and concrete A/B/C study design. |
| Authorized current action | Execute Phase 0 Step 7: create `THEORY_TO_CODE_TRACEABILITY.md` and `VALIDATION_AND_FALSIFICATION.md`, and update `UNRESOLVED_DECISIONS.md`. |
| Preserved files | The plan, scope, definitions, structural-class contract, metric specification, evaluation integrity, and hero specification; no revision requested. |
| Step 7 content approval | Pending review of the newly delivered mapping and validation specifications. |
| Step 8 authorization | Not yet received. |
| Phase 1 / repository / model-call / evidence-collection / execution / spending / publication authorization | Not received. |

The approved Step 6 file identities are:

| File | Approved version | SHA-256 |
|---|---|---|
| `HERO_BENCHMARK_SPEC.md` | 0.1 | `d1a0849d888a35ae3c9bd552bb920ee46417b7eeb4f8b687f8b5825e6fb851b2` |
| `UNRESOLVED_DECISIONS.md` | 0.5, before this update | `1f82e03d43061845eca0293e490c1749fdfb99fa52f30704e2128c5fa860b2ac` |

The register fingerprint identifies the preceding delivered version, not this version's own bytes. The hero's original proposed-status header remains historical delivery metadata; this record establishes its later approval without modifying the file.

**[Scope of approval]** The bounded integer domain, eight descriptors, reference/core and functional-suite design, audit plan, matched five-position A/B/C calls, six blocks, four calls per cell, primary distinct-20 endpoint, secondary prefixes, resource/extraction rules, coverage/quality bands, and external-validation profile are adopted. This settles their design, not the actual evidence. It supplies no validated program, independent annotation, collected model output, calibrated validator, empirical result, or operational authorization. Step 7 completes the scheduled traceability/test and outcome-rule mapping without changing those adopted choices.

### OA-007: Approve Step 7 and proceed with the integrated Step 8 audit

**[Owner-approved decision]** The preceding delivery submitted `THEORY_TO_CODE_TRACEABILITY.md` and `VALIDATION_AND_FALSIFICATION.md`, each version 0.1, with register version 0.6, and identified Step 8 as the integrated audit after approval. The owner instructed: “可以，继续step 8” (“Yes, continue with Step 8”).

| Field | Record |
|---|---|
| Record date | 2026-09-17; no exact local decision timestamp asserted |
| Approved content | Delivered Step 7 mapping and validation contracts v0.1; UD-005's remaining traceability, test-mapping, and fixed-suite outcome convention; preceding register v0.6. |
| Authorized current action | Perform the Step 8 integrated audit, update this register, and make explicitly finding-linked corrections within the eight permitted specification documents. |
| Preserved authority | The plan remains read-only. Earlier source identities and scientific/scope decisions remain controlling unless an explicitly proposed change receives renewed approval. |
| Step 8 corrections and audit acceptance | Pending review of this delivery; authorization to audit does not pre-approve its findings or revisions. |
| Step 9 approval-record preparation | Not yet authorized. `PHASE_0_APPROVAL.md` is not created in Step 8. |
| Phase 1 / repository / collection / execution / spending / publication | Not authorized. |

The approved Step 7 file identities, before this audit, are:

| File | Approved version | SHA-256 |
|---|---|---|
| `THEORY_TO_CODE_TRACEABILITY.md` | 0.1 | `b479d5a5e347d76e93276635d950bc860da62995af0a76718f07282235844d03` |
| `VALIDATION_AND_FALSIFICATION.md` | 0.1 | `bd0d49d5d27b687f77d16a9e09b7bed856f90f7905fc93e87781eb7f391fa6f5` |
| `UNRESOLVED_DECISIONS.md` | 0.6, before this update | `4ba21ed0f8d0e6214d42f8cba29a9f7fa9be612daa0219f7bd008c927560ecdd` |

The register fingerprint identifies the preceding delivered version, not this version's own bytes. Approval adopts the specified 40-row/36-group mapping, 54 future checks, and bounded P1/P5 outcome rules. It supplies no implemented test, independent annotation, collected sample, or scientific result. The Step 8 dispositions below distinguish the approved baseline, proposed corrective wording, remaining evidence, and later authorization gates.

## 3. Decision index

| ID | Decision | Current status | Blocker class | Due gate |
|---|---|---|---|---|
| UD-001 | First milestone, v0.1 scope, and offline interface | RESOLVED; recommendation approved in OA-002 | Implementation-blocking; resolved | Step 2 review complete |
| UD-002 | Source conventions, field names, and units | RESOLVED; recommendation approved in OA-002 | Implementation-blocking; resolved | Step 2 review complete; detailed estimator contract approved in OA-004 |
| UD-003 | Observation units, population views, and metadata semantics | RESOLVED; recommendation approved in OA-002 | Implementation-blocking; resolved | Step 2 review complete; detailed contracts approved in OA-003/OA-004 |
| UD-004 | Structural-class contract and hero family | RESOLVED; general contract approved in OA-003 and hero contract in OA-006 | Implementation-blocking; design resolved | Step 6 review complete; actual evidence under UD-006 |
| UD-005 | Metric procedures, realization proxy, and P1/P5 comparison design | RESOLVED; metrics OA-004, study design OA-006, mapping and outcome convention OA-007 | Implementation-blocking design components resolved; audit corrections await acceptance | Step 7 review complete; Step 8 audit review now |
| UD-006 | Integrity protocol and independent evidence for empirical claims | PARTIALLY RESOLVED; protocol approved in OA-005; actual independent evidence outstanding | Empirical-claim-blocking for the unsupported scoped claim | Actual evidence before corresponding empirical claim |
| UD-007 | Latent-support diagnostic boundary | OPEN; deferred | Deferred | Before a future latent-support capability |

UD-001 through UD-005 have their scheduled design decisions resolved through OA-002 to OA-007. Finding-specific corrective wording in Section 7 still awaits Step 8 owner acceptance. UD-006's integrity protocol remains approved in OA-005, with actual independent evidence outstanding. Reviewers, provider access, and a real model collection are not prerequisites for subsequent specification or separately authorized fixture implementation.

## 4. Resolved Step 2 decisions

### UD-001: First milestone and v0.1 boundary

**Basis:** [Engineering proposal], implementing the measurement layers and task tiers in SD §§9, 11 and SI §§8-9. The sources do not prescribe a package release schedule or file formats.

**Question:** How much measurement and execution capability belongs in the first executable milestone and the first release?

**Options and consequences:**

| Option | Consequence |
|---|---|
| A. Offline first milestone; v0.1 adds one-task A/B/C comparison | Delivers auditable calculations using recorded outputs and assignments. Live generation and execution stay outside the package boundary. |
| B. Add generation adapters and an execution harness to v0.1 | Adds provider, security, reproducibility, and resource-management contracts before release. |
| C. Include Layer B and recovery estimators in v0.1 | Also requires comparable recursive trajectories, recovery evidence, and additional estimator validation. |

**Recommendation:** Option A. First milestone: core structural summaries on fixtures with evidence and population accounting. v0.1: the same core plus precollected A/B/C comparisons, a limited realization proxy, and integrity-aware reporting. Use JSON/JSONL inputs and JSON/Markdown outputs through a local command-line workflow. These interface choices are engineering proposals.

**Affected files:** `PROJECT_SCOPE.md`, Sections 4-5; `DEFINITIONS_AND_UNITS.md`, Sections 7-9.

**Blocker class:** Implementation-blocking for release scope; no block on completing Step 2.

**Owner decision:** Approved in OA-002 on 2026-09-16. Option A and the recommended JSON/JSONL input, JSON/Markdown output, local offline interface are adopted as the Step 2 baseline. The owner authorized Step 3 specification only; implementation and empirical claims remain unauthorized.

**Status:** RESOLVED; approved at Step 2 scope.

### UD-002: Preserve source conventions without ambiguous public fields

**Basis:** [Source-derived] SD §§3.7, 4.1, 5.1 and SI §§3.3, 5.3, 8.2; [Engineering proposal] names and default display conventions.

**Question:** How should software expose the coexisting notation, observed-support definitions, and effective-count definitions?

**Source record:**

| Topic | SD | SI |
|---|---|---|
| Analytic resolution | `R`; `ρ` also appears as a stability threshold. | `ρ`; `ℛ` is the reference registry. |
| Observed support | Empirical-frequency-thresholded set. | Set of classes appearing in the finite sample. |
| Effective structural count | `exp(H_S)`. | `1/SCI`. |

**Options and consequences:** Occurrence-based or thresholded support can be the primary display, provided both retain distinct names, denominators, and thresholds. Logarithm bases can differ only with explicit units and the corresponding effective-count conversion. The plan already requires the two effective counts to remain separate; merging them is not an available baseline option.

**Recommendation:** Use descriptive resolution/registry/stability fields; `observed_support_size` for occurrence and `observed_support_size_thresholded` for the separately requested thresholded view. Use natural logarithms, entropy in nats, `effective_support_shannon`, and `effective_support_simpson`. Preserve source notation in traceability references. Keep empirical-frequency and model-probability thresholds separately named.

**Consequence:** The two observed-support views may return different counts, and the two effective counts may differ. These differences remain interpretable rather than being hidden by a shared label.

**Affected files:** `DEFINITIONS_AND_UNITS.md`, Sections 2, 6-7; corresponding scope summaries.

**Blocker class:** Implementation-blocking for formulas and public meanings.

**Due gate:** Step 2 for names and meanings. Step 4 for numerical tolerances, complete estimators, and edge-case tests.

**Owner decision:** Approved in OA-002 on 2026-09-16. The recommended names, occurrence/threshold distinction, natural logarithms/nats, separate effective counts, and separate probability thresholds are adopted without rewriting either source definition. Numerical procedures and complete estimators remain Step 4 work.

**Status:** RESOLVED; approved at Step 2 scope.

### UD-003: Observation units, population views, and missing metadata

**Basis:** [Source-derived] SD §§6.5, 9.4-9.5 and SI §§4.2, 8; [Engineering proposal] explicit populations, records, and missingness vocabulary. The sources do not supply the full ingestion schema or one universal exclusion policy.

**Question:** Which observations and accepted assignments contribute to each result, and how are dependencies and missing evidence represented?

**Options and consequences:**

| Option | Consequence |
|---|---|
| A. Paired `classified_all` and `classified_valid` views with full accounting | Keeps concentration and validity separate while making each conditional denominator visible. |
| B. One prespecified conditional population with a separate validity audit | Produces fewer result blocks; interpretations depend more heavily on the selected population and comparison design. |

Both options must preserve unresolved/unclassified cases, failed attempts, sample-group dependence, and explicit knowledge states. Silent deletion or counting unknown assignments as new classes conflicts with the governing plan.

**Recommendation:** Option A. Treat study, analysis run, prompt block, call, realization, coordinated set, assignment version, and recursive round as distinct units. Use `known`, `unknown`, `unavailable`, and justified `not_applicable` metadata states, separately from evidence-review status. Require explicit group identity or an explicit uncertainty statement.

**Consequence:** Descriptive calculations can proceed on supported subsets while the report withholds unsupported full-population or independence claims. Valid-only results remain accompanied by failure, exclusion, and classification coverage information.

**Affected files:** `DEFINITIONS_AND_UNITS.md`, Sections 3-5 and 8-10; `PROJECT_SCOPE.md`, Sections 4 and 6.

**Blocker class:** Implementation-blocking for observation and denominator semantics.

**Due gate:** Step 2 for the conceptual contract. Step 3 determines acceptable assignment states; Step 4 completes denominator, empty-population, uncertainty, and grouping procedures. Approval here does not approve those unproduced procedures.

**Owner decision:** Approved in OA-002 on 2026-09-16. Option A and the recommended observation units, paired views, knowledge states, and explicit grouping semantics are adopted. Detailed assignment acceptance is submitted in Step 3; denominator and uncertainty procedures remain Step 4 work.

**Status:** RESOLVED; approved at Step 2 scope.

## 5. Current and scheduled Phase 0 decisions

### UD-004: Structural-class contract and hero family

**Basis:** [Source-derived] SD §§3.2-3.6, 7, 9.1, 9.3-9.6 and SI §§3.1, 4.2, 8.5-9; [Engineering proposal] task-specific hard assignments, evidence states, exceptional-case handling, and versioned corrections.

**Question:** What contract establishes defensible structural membership, and which single Tier 1 task supplies its first concrete implementation?

This existing item has two components because the governing plan assigns the general contract to Step 3 and concrete task selection to Step 6. It remains one decision item; approval of one component does not approve the other.

#### Contract component: approved after Step 3

**Options and consequences:**

| Option | Consequence |
|---|---|
| A. Deterministic hard assignments for resolved cases, with unresolved evidence retained | Preserves the approved first-release scope and permits auditable classification-conditioned summaries. |
| B. Probabilistic or overlapping class scoring in the first release | Requires a revision of the approved scope, assignment-uncertainty model, estimators, and validation before implementation. |

**Recommendation adopted:** Option A, specified by `STRUCTURAL_CLASS_CONTRACT.md`, version 0.1. The approved contract includes:

- task-bounded invariants, consequence signatures, membership evidence, and separate class-schema/sample validation;
- `assigned`, `unresolved`, and `unclassified` outcomes, separate from `fixture`, `provisional`, and `adjudicated` review states;
- fixture-only and adjudicated-import evidence policies feeding the approved `classified_all` and `classified_valid` views;
- separate validity outcomes, including recognizable but invalid mechanisms when the declared descriptor permits them;
- explicit handling of hybrids, apparent novelty, opaque dependencies, incomplete outputs, and contradictory pairwise judgments;
- preregistration, versioned correction, sample-level re-adjudication, and affected-result review.

The mode does not implement a classifier, execute generated code, or certify independence from a review-state string. Provisional labels do not enter the standard metric views. Conceptual examples and future checks are not actual validation evidence.

**Owner decision:** Approved in OA-003 on 2026-09-16. Option A and the delivered general-contract version 0.1 are adopted. Actual independent validation and concrete hero-class descriptors remain at their separate gates.

**Component status:** RESOLVED; general contract approved.

#### Hero-task component: approved after Step 6

**Options and consequences:**

| Option | Consequence |
|---|---|
| A. Bounded integer sorting with eight mechanism families and explicit unresolved cases | Gives the one-family offline prototype a concrete domain and meaningful algorithm boundaries, while keeping independent validation and new-class review visible. |
| B. A smaller selected algorithm list | Reduces reference work but can leave common eligible solutions unclassified; coverage and resulting inference limits must be accepted explicitly. |
| C. Substitute another Tier 1 task or add several tasks | Substitution requires a complete replacement validation route; multiple families require a scope change. |

**Recommendation:** Adopt Option A through `HERO_BENCHMARK_SPEC.md`, version 0.1. The proposed domain is Python sorting of lists of length 0-256 containing integers 0-4095, with a fresh sorted list and input preservation. Additional local memory is permitted; there is no comparison-only, in-place, stability, or asymptotic-complexity requirement.

The proposed classes are adjacent sweep, sorted-prefix insertion, rescanning extremum selection, ordered-run merge, pivot partition, maintained heap extraction, full-key frequency ordering, and multi-stage digit refinement. The descriptors specify constitutive relations, allowed variants, confusable boundaries, defect/hybrid handling, and schema/sample validation routes. An eligible unregistered mechanism can remain valid while structurally unresolved.

The proposal defines a 32-artifact reference/core design, a 8995-input bounded functional suite, mechanism witnesses, positive reference quotas, sampled/targeted human audit, and imported external-validation safeguards. These are future material/evidence requirements, not existing validated programs or completed tests. The task does not add execution or automatic classification to v0.1.

**Owner decision:** Approved in OA-006, recorded on 2026-09-17. The delivered hero contract version 0.1 and the recommended bounded sorting domain, classes, and validation design are adopted. Actual independent validation remains under UD-006.

**Component status:** RESOLVED; hero-task design approved. Its actual reference/annotation/execution evidence is separately tracked under UD-006.

**Affected files:** Approved `STRUCTURAL_CLASS_CONTRACT.md` and `HERO_BENCHMARK_SPEC.md`, each version 0.1.

**Blocker class:** Implementation-blocking design decision, now resolved. Actual empirical validation remains a separate claim gate.

**Overall status:** RESOLVED. The general structural-class and concrete hero contracts are approved; this does not close UD-006 or authorize implementation.

### UD-005: Metric procedures, realization proxy, and P1/P5 comparison design

**Basis:** [Source-derived] SD §§3.7, 5, 9.2, 9.5, 9.7 and SI §§3.3, 5.3, 8; [Engineering proposal] finite-sample procedures, diagnostics, and experimental implementation choices.

**Question:** Which complete estimator rules, matched conditions, independent units, resource accounting, realization proxy, and uncertainty procedures make the first-slice results and P1/P5 comparisons interpretable?

This item now records the metric details assigned by the plan to Step 4, alongside its existing comparison-design responsibility. It preserves the names, population meanings, and release boundary approved in UD-001 through UD-003. It does not reopen those resolved choices or introduce an additional numbered blocker.

#### Metric and diagnostic component: approved after Step 4

**Options and consequences:** The unsmoothed empirical core can be implemented with exact count/threshold semantics and separate undefined results. Distinct-k could use several selection methods; the current proposal chooses one fixed-prefix method so an implementer need not invent a sampler. Surface proxies measure different observables and may saturate. A transparent lexical-distance proxy limits the empirical interpretation to that observable, while a semantic/model-based proxy would require additional validation and scope decisions.

**Recommendation adopted:** `METRICS_SPEC.md`, version 0.1, with the following explicit engineering choices:

- exact unweighted accepted-class counts; approved occurrence/thresholded support distinction, nats, SCI, and separately named effective counts;
- explicit denominators, accepted-validity and classification coverage, result-state vocabulary, and empty-set/empty-distribution separation;
- prespecified-prefix distinct-k, with no backfill for invalid or unclassified realizations and visible generation-group dependencies;
- a deterministic surface lexical-trigram Jaccard proxy, reported on an identified text-eligible subset and within accepted classes;
- a separate distinct-pair structural non-equivalence fraction on the same subset, without changing the plug-in SCI definition;
- an explicitly proxy-relative P1 gain contrast, validity-aware fixed-budget P5 breadth contrasts, and equal-block summaries;
- a bounded paired prompt-block resampling method with recorded replay information, separating sampling inference from fixed-suite sensitivity;
- 24 non-executable fixture/check specifications, plus deferred-metric prerequisites without invented values.

**Consequences and limits:** The lexical proxy cannot establish structural equivalence or exact realization entropy. A positive P1 contrast alone cannot establish the predicted increase. Prefix counts and equal k do not by themselves establish equal cost or independent observations. The interval does not repair uncertain classification or missing external evidence. Future hero-specific sampling, quality, coverage, and claim criteria remain required before an empirical comparison.

**Owner decision:** Approved in OA-004 on 2026-09-16. The delivered metric/diagnostic version 0.1 and its recommended procedures are adopted. Concrete experiment design and actual independent evidence remain at their separate gates.

**Component status:** RESOLVED; metric/diagnostic contract approved.

#### Concrete experiment-design component: approved after Step 6

**Options and consequences:** Single-answer and coordinated-set designs are both possible but have different conditioning and dependence. Matching all conditions as five-answer calls preserves a common set size while retaining within-call dependence. A larger suite or sample budget could add evidence at additional cost; the first bounded experiment cannot claim comprehensive support or population-level generality.

**Recommendation adopted:** The Step 6 design in `HERO_BENCHMARK_SPEC.md`, version 0.1:

- six fixed prompt phrasings of the same sorting task; four fresh five-candidate calls per block-condition;
- A ordinary five-version prompting, B the byte-identical prompt with proposed temperature 1.0 instead of 0.4, and C an explicit different-mechanism clause with A's controls;
- 72 planned main calls and 360 requested candidate positions, with an optional disjoint six-call/30-position pilot;
- proposed 8192 output-token allowance per call under a recorded unit/cap convention, with actual input, output, hidden-computation, and spending limitations disclosed;
- fixed complete-group prefixes k=5, 10, 20, primary P5 at k=20, and a secondary empirical-frequency threshold of 0.10;
- stable extraction and interleaved collection order, no outcome-based retries or missing-position backfill, and separate planned/actual inventories;
- registered coverage and matched-quality bands, all primary P1/P5 operands, fixed-suite prompt-resampling sensitivity, and all registered comparisons reported without endpoint selection;
- concrete reference/audit selection and passive imported validation evidence, without live generation or execution support.

**Consequences and limits:** Equal requested positions and output allowance do not establish equal actual tokens, compute, or cost. Twenty positions in a cell come from four dependent five-answer calls. A control not supported by the selected deployment cannot become a temperature intervention by declaration. Missing groups, classification, or validity affect the registered interpretation and remain visible. Actual model/provider selection, controls, exposure, costs, and evidence are run-binding requirements before collection; they do not prevent an offline fixture implementation.

**Owner decision:** Approved in OA-006, recorded on 2026-09-17. The delivered concrete experiment design is adopted. No collection or expense is authorized. The Step 7 interpretation/test component below maps these choices without changing them.

**Component status:** RESOLVED; concrete study design approved. Its traceability/interpretation component was subsequently adopted in OA-007 below.

#### Traceability and interpretation/test component: approved after Step 7

**Question:** Which planned responsibilities, future tests, report fields, and fixed-suite outcome rules implement the approved definitions without introducing a new estimator or silently changing the experiment?

**Options and consequences:** A sign-of-mean narrative alone would omit the approved sensitivity context and could obscure mixed comparator results. Promoting the nominal intervals to population or familywise significance would exceed this fixed-suite design. A prespecified operational direction/sensitivity rule retains the adopted estimators and gives supporting, contrary, inconclusive, and not-evaluated outcomes distinct meanings.

**Recommendation adopted in OA-007:** `THEORY_TO_CODE_TRACEABILITY.md` and `VALIDATION_AND_FALSIFICATION.md`, each version 0.1, with:

- 40 source/adopted-decision trace rows and 36 report-field groups linked to planned responsibilities, future checks, permitted inferences, and limitations;
- 54 future conformance/evidence checks covering all 82 existing SC-T, MF, EI-T, and HB-T checks/fixtures, with software handling separated from actual external evidence;
- separate first-milestone, v0.1-comparison, validated-measurement, and empirical-claim gates;
- exact core/hero arithmetic, separate missing/invalid/provisional/corrected hero variants, coverage-boundary cases, and surface/pair/replay oracles;
- P1 supporting only when both the positive surface gain and positive surface-minus-structural gain contrast are retained across the adopted fixed-suite sensitivity ranges; robust negative required directions are contrary, and ties/zero-touching ranges remain inconclusive;
- separate P5 C-A/C-B primary distinct-20 decisions under the adopted gates, with both needed for the full supporting pattern and mixed/comparator-missing outcomes exposed;
- 14 constructed outcome-routing fixtures, symmetric treatment of favorable/adverse evidence, explicit near-ceiling and quality qualifications, and no p-value, familywise-significance claim, endpoint switch, or outcome-dependent test success;
- current deferred support/frontier/SHL/ERR boundaries preserved without implementing or numerically filling those capabilities.

**Consequences and limits:** The new outcome convention is an engineering decision about the registered proxy and finite fixed suite. It does not make sensitivity ranges into confidence intervals for all prompts, estimate every uncertainty source, or establish practical importance from a positive sign. Mock evidence and stipulated outcomes do not satisfy independent validation. Actual adverse results remain legitimate scientific findings at their supported scope.

**Owner decision:** Approved in OA-007, recorded on 2026-09-17, with authorization to perform the integrated Step 8 audit. No implementation, model collection, candidate execution, reviewer engagement, spending, or release has been authorized. The finding-linked v0.2 revisions are separately pending audit acceptance.

**Component status:** RESOLVED; delivered Step 7 traceability and validation/interpretation specifications approved in OA-007.

**Affected files:** Approved metric, hero, traceability, and validation contracts v0.1. Step 8 proposes v0.2 of the metric, traceability, and validation files only for AF-001 through AF-003; the hero contract remains byte-for-byte v0.1. Section 7 records the exact correction scope and identities.

**Blocker class:** Implementation-blocking design component, now resolved. Acceptance of the integrated audit and subsequent final-approval/implementation gates remain explicit authorizations; they are separate from missing empirical evidence or other-toolkit completion.

**Overall status:** RESOLVED. Metric/diagnostic procedures, concrete study design, and the Step 7 mapping/outcome convention are approved. Step 8 corrective wording remains subject to the audit-review gate in Section 7.

## 6. Evidence-dependent and deferred items

### UD-006: Integrity protocol and independent evidence for empirical structural claims

**Basis:** [Source-derived] SD §§9.4-9.6 and SI §§3.4, 8.5-9. SD specifies at least two independent human annotators for core validity sets; SI's Tier 1 design combines mechanical/formal evidence with sampled human audit. Both sources require visible lineage and a correction-capable evaluation. [Engineering proposal] scoped evidence records, claim gates, local component records, and correction-impact handling.

**Question:** Which integrity protocol governs empirical structural claims, and what actual evidence satisfies that protocol for the specific experiment or measurement?

The protocol and evidence components have distinct completion conditions. Approving the protocol can resolve its design while leaving actual annotation, reference, and experiment evidence outstanding. No extra numbered blocker is created.

#### Protocol component: approved after Step 5

**Options and consequences:**

| Option | Consequence |
|---|---|
| A. Preserve both source protocols and separate arithmetic, validated measurement, and empirical claims | Allows honest fixture implementation and qualified imported-label summaries while requiring actual scoped evidence for stronger claims. |
| B. Treat deterministic processing, separate provider names, or a single human review as sufficient independent validation | Would depart from the supplied requirements and cannot be represented as source-conformant merely for convenience. |
| C. Require a recruited independent team and full knowledge of every upstream corpus before any software work | Would extend empirical evidence requirements into unrelated development gates and exceed the approved bounded implementation plan. |

**Recommendation adopted:** Option A through `EVALUATION_INTEGRITY.md`, version 0.1. Its operational requirements include:

- the four supplied conditions: External Presence, Source Integrity, Tail Retention, and Corrective Capacity;
- source, role, transformation, lineage, exposure, and scoped independence records, preserving unknown ancestry without treating every unknown as a global stop;
- distinguishable reference, generator, classifier, human annotator, adjudicator, and validator roles, without a sole-lineage final validation path;
- at least two independent human initial annotations for the named core validity set, plus Tier 1 domain evidence and sampled human audit, with concrete selection and coverage set in Step 6;
- disclosure of AI assistance, calibration/exposure limits, original disagreement records, and unperformed sensitivity checks;
- separate fixture, qualified imported-label, validated-measurement, and empirical-comparison claims, with the existing calculation states unchanged;
- minimal versioned local records for Stable Core, Rotating Structural Frontier, External Incident Stream, and Versioned Tail Registry;
- correction impact on evidence, assignments, populations, metrics, comparisons, reports, and claims, including a constructed four-sample scenario;
- 18 non-executable future integrity checks, without a new metric, live service, implementation, or empirical result.

**Consequences and limits:** This protocol does not require two annotations on every generated output or perfect knowledge of all model ancestry. It also does not waive source requirements for claims that need them. Different names, approval strings, and deterministic processing do not establish independent evidence. A qualified report may disclose limitations; it may not imply that missing validation has been performed. No extra overall integrity score or automatic truth/ancestry detector is introduced.

**Affected files:** Approved integrity and hero contracts v0.1; approved validation contract v0.1 with its pending Step 8 clarification v0.2; future empirical report metadata. No Step 8 correction waives this protocol or supplies its outstanding evidence.

**Owner decision:** Approved in OA-005, recorded on 2026-09-17. The owner accepted the delivered Step 5 contract and authorized Step 6. Option A and the integrity contract version 0.1 are adopted.

**Component status:** RESOLVED; integrity protocol approved. This approval does not settle the evidence component below.

#### Run-specific evidence component: outstanding

**Current evidence:** The approved Step 2-7 contracts and pending Step 8 corrections contain source-based requirements and explicitly constructed examples. Preparation and this document audit are AI-assisted. No actual 32-program core, independent human annotation pair, main/pilot model collection, sampled human audit, calibrated judge study, or independently validated execution environment has been supplied by this phase. OA-002 through OA-007 approve specifications; document checks, future test definitions, and stipulated arithmetic do not supply the missing evidence.

**Recommendation:** After separate authorization for the relevant activity, attach the actual reference construction, roles/lineage, independent core annotations, domain validation, sampled audit, exposure, disagreement/adjudication, and claim assessment records. Evaluate requirements against the named task, collection, analysis population, and claim. Missing essential membership evidence withholds the affected assignment; missing independence can instead restrict its stronger empirical interpretation when a qualified imported-label calculation remains justified.

**Evidence needed to close:** Actual evidence satisfying the approved integrity protocol and applicable approved hero design for an explicitly identified claim. Unknown or unavailable facts retain their scope. A limited finding may remain reportable with a correspondingly limited claim; it cannot certify complete source-protocol conformity.

**Owner decision:** No actual empirical-evidence acceptance has been requested or received. A future decision must identify the specific evidence and claim scope.

**Component status:** OPEN; empirical-claim-blocking for the corresponding unsupported claim. No block on subsequently authorized specification/audit work, or on fixture implementation after Phase 0 and explicit implementation authorization.

**Overall blocker class:** Empirical-claim-blocking; the approved protocol defines claim-handling requirements within Phase 0. A later missing implementation-critical representation rule would need its own explicit impact finding; absent independent people or data are not automatically implementation blockers.

**Overall status:** PARTIALLY RESOLVED; protocol approved in OA-005 and actual independent evidence outstanding.

### UD-007: Latent-support diagnostic boundaries

**Basis:** [Source-derived] SD §§5.3-5.4 and SI §3.3; [Engineering proposal] defer implementation pending a dedicated contract.

**Question:** How will a future diagnostic distinguish recovery from existing model information from learning a missing structure through the diagnostic intervention itself?

**Source record:** SD includes stronger probes, targeted steering, transfer, and limited adaptation. SI describes diagnostics on the existing model state and excludes simply injecting the missing solution. Neither supplied edition provides a complete executable adaptation/contamination protocol for this toolkit.

**Options and consequences:** Restricting an initial diagnostic to frozen-model probes narrows the operational question. A broader controlled-adaptation design requires additional records and controls for information introduced by the diagnostic. Either choice must preserve the source distinction between observed, expressible, and latent support.

**Recommendation:** Keep both source descriptions in the definitions and implement no latent-support estimator in v0.1. Resolve this item only when that capability is explicitly selected.

**Affected files:** `DEFINITIONS_AND_UNITS.md`, Section 6.3; future diagnostic specification if authorized.

**Blocker class:** Deferred. No effect on Phase 0 completion for the proposed first milestone.

**Owner decision:** No immediate decision requested.

**Status:** OPEN; deferred.

## 7. Step 8 integrated audit and acceptance record

### 7.1 Scope, method, and conclusion

**[Audit record]** The audit covers all ten currently existing Phase 0 documents and the two supplied theory PDFs. It checks the plan's write boundary, actual approval sequence, definitions, source conventions, class/evidence rules, metrics and denominators, task eligibility, sampling, validation, traceability, correction paths, and limits on conclusions. Source checking uses the supplied editions and relevant rendered pages; it does not independently verify the external publications cited by those editions.

**Conclusion for the proposed corrected baseline:** No unresolved technical design blocker was identified for the bounded offline first milestone. Three wording conflicts or scope ambiguities were found and corrected in three specification files. These are findings AF-001 through AF-003 below; their acceptance remains pending. No new scientific decision, estimator, task, threshold, budget, capability, test ID, or compulsory project artifact is proposed. This conclusion does not authorize implementation or certify empirical validity.

The audit preserves the distinction between the M fixture/imported-record core, the V comparison capability, actual E evidence, and D deferred work. Completion of Recursive Integrity Toolkit or Source Integrity Toolkit remains unnecessary for these gates.

### 7.2 Finding-specific corrections

| Finding | Observed issue and controlling contract | Corrective resolution and affected locations | Change to approved scope or scientific decision? | Current disposition |
|---|---|---|---|---|
| AF-001: local evidence failure versus invalid shared frame | MET §§4.4 and 7 could block a whole distribution for one unresolved assignment or missing membership record. SC §§6.4-6.5 and 8, EI §10.2, and VF HF-04 already require local withholding and recalculation on a supported subset when the frame is valid. | MET v0.2 §§4.4/7 separate local assignment exclusion from a genuinely defective shared frame. VF v0.2 VT-04, HF-04 explanatory text, and §9 make the same boundary explicit. Original selected inventory and separately sufficient validity evidence remain intact. | No. Aligns the failure scope with existing accepted-population rules. No new exclusion policy, count formula, or evidence waiver. | Corrective text prepared; owner audit acceptance pending. |
| AF-002: endpoint-specific text eligibility | VF §6.4 referred broadly to all coverage requirements. That wording could apply HERO's text-for-pair-contrasts threshold to count-based P5, even though HERO §10.3 and MET MF-14 separate text diagnostics from supported class counts. | VF v0.2 §§6.2/6.4 and 9, VT-37/VT-43, identify each endpoint's applicable gates. Missing proxy text can withhold P1 while leaving evidence-backed P5 counts/comparisons evaluable. Missing material that also invalidates class/validity evidence still triggers the original restrictions. | No. Preserves the existing gate values and their specified applicability. No reduced class, validity, independence, or quality requirement. | Clarification prepared; owner audit acceptance pending. |
| AF-003: passive local input access | TRACE PC-01 said never retrieve input content without limiting retrieval to remote content. Read literally, this could prohibit the local input reads needed by the adopted offline interface, while SC/EI/HERO prohibit execution and automatic remote access. | TRACE v0.2 PC-01 and VF v0.2 VT-19 permit declared passive local reads and explicitly prohibit automatic remote retrieval or executing inputs. External locators remain metadata unless material is separately supplied locally. | No. Restates the existing local-first boundary. No network adapter, dependency installation, or execution path. | Clarification prepared; owner audit acceptance pending. |

Header versions, companion references, audit-origin notes, and this register are updated to identify these corrections. Existing earlier-step submission/handoff paragraphs are retained as history, with their later approvals and current gate explicitly identified. They do not create an additional approval loop.

Original file fingerprints retained for reviewing the exact correction delta:

| Corrected file | Prior version | Prior SHA-256 |
|---|---|---|
| `METRICS_SPEC.md` | 0.1 | `ec75688060b7f2937ff480ebb1f8cfd8fe96ec920962e5ff404a1367fe9a7c0f` |
| `THEORY_TO_CODE_TRACEABILITY.md` | 0.1 | `b479d5a5e347d76e93276635d950bc860da62995af0a76718f07282235844d03` |
| `VALIDATION_AND_FALSIFICATION.md` | 0.1 | `bd0d49d5d27b687f77d16a9e09b7bed856f90f7905fc93e87781eb7f391fa6f5` |

### 7.3 Integrated consistency results

| Audit area | Checked basis and result | Remaining boundary |
|---|---|---|
| Authority and file permissions | OA-007 resolves the delivered Step 7 component. Only MET, TRACE, VF, and this register change; every correction is linked above. Plan and both source PDFs retain their hashes. | Audit acceptance, Step 9, final approval, and implementation authorization are still distinct future gates. |
| Source definitions | SD's entropy-effective count and SI's concentration-effective count retain separate names. Occurrence/empirical-threshold/model-probability support, observed/expressible/latent support, and source resolution/registry notation remain distinct. | No reconciliation by rewriting either source; latent-diagnostic choice remains UD-007. |
| Count and numerical rules | Fixed unweighted populations, original denominators, exact threshold comparisons, natural-log units, effective counts, empty/undefined/unavailable states, and rounding rules remain consistent after AF-001. | Arithmetic is conditional on accepted records, not certification of the original model distribution. |
| Classification and validity | Hard class assignments, fixture versus adjudicated policies, imported membership evidence, separate validity, hybrid/new-class intake, and versioned correction routes agree. AF-001 makes the failure extent explicit. | Actual mechanism and independent evidence are still required for stronger claims. |
| One-task eligibility | The bounded integer domain and allowed operations leave each of the eight declared mechanisms eligible in principle. No hidden stability, in-place, or complexity requirement was added. | Descriptor overlap review, real reference programs, oracle validation, and execution evidence remain E work; no claim that they have been completed. |
| Sampling and resources | Six fixed blocks, three conditions, four calls per cell, five positions per call, fixed k=5/10/20, incomplete-group handling, no backfill, pilot separation, and planned caps reconcile. | Planned output allowance is not equal actual cost or compute. Model/provider identity and control availability bind only a later authorized collection. |
| Comparison interpretation | P1's joint proxy directions, P5's two primary comparisons, exact bands, fixed-suite paired resampling, and four outcome states remain unchanged. AF-002 prevents a diagnostic-specific gate from becoming a global veto. | No prompt-population/familywise significance, latent capacity, useful creativity, or universal growth claim is licensed. |
| Evaluation integrity | External Presence, Source Integrity, Tail Retention, Corrective Capacity, the four local record components, independent core annotation, sampled audit, and effective correction remain represented. | Approved protocols and AI-assisted documents do not close UD-006. |
| Correction propagation | Original identities, label/rubric/evidence references, revised populations, metrics, contrasts, claims, and superseded records remain linked. No re-analysis creates new samples or a new confirmatory collection. | Any later scientific-rule change still needs explicit impact review and approval. |
| Traceability and tests | 40 TR rows, 36 RF groups, and 54 VT checks retain valid references; all 82 upstream requirements remain mapped. AF-001/002/003 clarify existing checks rather than adding new IDs. | Tests are specifications. None of the 54 implementation checks or E activities is recorded as run. |
| Local execution boundary | AF-003 makes local reads consistent with passive analysis and remote/execution prohibitions. Future external validation preserves separate containment and scientific-oracle requirements. | No runner, sandbox implementation, candidate execution, provider adapter, or live scientific judge is introduced. |
| Document structure | File references, table widths, defined IDs, comparison constants, revision identities, and source fingerprints were checked. The only planned Phase 0 artifact not yet present is the Step 9 approval record. | Its absence is intentional at this gate; Phase 0 is not declared finally completed. |

### 7.4 Arithmetic and document-check evidence

**[Document QA record]** Checks performed during this audit include source-page/formula review, document cross-reference and ID checks, Markdown table checks, count/denominator arithmetic checks, and byte-level comparison against the supplied baseline. They do not execute benchmark software or generated programs.

| Stipulated quantity | Independently recomputed value or identity |
|---|---|
| Base count fixture `(8,6,3,2,1)` | n=20; occurrence support=5; threshold 0.10 support=4; SCI=57/200; entropy=1.392321254757429 nats; Shannon effective count=4.024180367609189; Simpson effective count=200/57. |
| One local assignment withheld `(8,6,3,2)` | n=19 within the original 20 selected realizations; SCI=113/361; entropy=1.256637906749007 nats. HF-04 retains these supported-subset calculations. |
| Evidence-corrected base `(8,6,3,3)` | n=20; SCI=59/200; entropy=1.2968441295132072 nats; original sample inventory unchanged. |
| Integrity correction example | Selected n=4 throughout; accepted SCI progresses 1/2, 5/9, 5/8 for counts `(2,2)`, `(2,1)`, `(3,1)`. |
| Functional-suite design | 781 + 18 + 8192 + 4 = 8995 distinct test IDs. This is a manifest design count, not executed test coverage. |
| Main collection plan | 6 × 3 × 4 = 72 call slots; 72 × 5 = 360 requested candidate positions; output-cap total 72 × 8192 = 589824. |
| Optional pilot and combined allowance | 6 calls / 30 positions / cap 49152; combined 78 calls / 390 positions / cap 638976. No call or expenditure occurred. |
| Declared quantile interpolation | For 2000 ordered replicates, zero-index ranks `(2000-1)×0.025=49.975` and `(2000-1)×0.975=1949.025`. No real resampling experiment was performed. |

The fixed rules were also checked for unchanged temperatures 0.4/1.0, primary k=20, the 0.90/0.95 coverage requirements, 0.80 validity floor, 0.10 quality band, and seed/replay convention. No result-dependent adjustment was made.

### 7.5 Remaining items and effects

| Item | Classification and owner | Requirement and effect |
|---|---|---|
| Technical design decisions for bounded M | Implementation-blocking design items UD-001 through UD-005 are resolved; Theory Owner accepts the audit corrections. | No new unresolved implementation-design question was identified. Current corrections and audit still require acceptance before Step 9. This is not permission to write implementation. |
| UD-006: actual independent measurement/experiment evidence | Empirical-claim-blocking; Theory Owner controls scoped claim acceptance, with actual independent annotators/domain validators identified when engaged. | Supply the required reference construction, independent first-pass labels, oracle/domain validation, sampled audit, exposure/lineage, and actual collection evidence for the named claim. None is supplied by this audit. Fixture work can proceed after its separate implementation authorization. |
| Later empirical run binding | Run-specific empirical-claim prerequisite within the existing HERO §9 / UD-006 workflow; Theory Owner and the later collector. | Freeze actual model/provider/controls, artifact identities, registered resources, and collection/validation authorization before the relevant observations. No model choice or spending decision is required for offline fixture implementation. |
| UD-007 and other deferred capabilities | Deferred; Theory Owner when selecting that capability. | Latent diagnostics, bounded-intervention probability estimation, frontier, SHL/ERR, recursive training, soft classes, live adapters, and broader domains remain outside the bounded implementation. Existing prerequisite records are retained. |
| Final approval and operational permission | Authorization gates, not empirical evidence; Theory Owner. | Step 9 may be prepared only after audit acceptance. The final baseline review and an explicit instruction to implement remain later. No approval or evidence is inferred from document completeness. |

No new numbered UD is added for a missing reviewer, provider account, uncollected observation, future feature, or an intentionally uncreated Step 9 document.

### 7.6 Reviewed delivery identities

These fingerprints identify the Step 8 candidate document set for review. They are not a final approval/freeze record. Current register v0.7 is intentionally excluded from this hash table to avoid self-reference; OA-007 records its preceding v0.6 identity. Step 9, if authorized, will fingerprint all ten preceding files including this delivered register.

| File | Version | Disposition | SHA-256 |
|---|---|---|---|
| `PHASE_0_PLAN.md` | 0.1 | Unchanged; governing plan | `5df37f3fef1d012d462a116d7839909c9379dfe6d59a1b3356cae004bcfac6a4` |
| `PROJECT_SCOPE.md` | 0.1 | Unchanged; approved in OA-002 | `2eec02825c8df4281cc538d00dcb809907dc2eb8a2b1b73b597cbab17d975a11` |
| `DEFINITIONS_AND_UNITS.md` | 0.1 | Unchanged; approved in OA-002 | `a3da3e356a21f59468178050944baf58787edd65204fbf40b3b1742cd38104ab` |
| `STRUCTURAL_CLASS_CONTRACT.md` | 0.1 | Unchanged; approved in OA-003 | `00ba09dd879f5fe02a3302a6f1ad36bda1c6b7e2723562f5f62ec85fed125328` |
| `METRICS_SPEC.md` | 0.2 | AF-001 corrective proposal; acceptance pending | `23b45934e87767ca87e56b97aa4e1d1abdd49e27187d0b9c5a336ca516a96edb` |
| `EVALUATION_INTEGRITY.md` | 0.1 | Unchanged; approved in OA-005 | `50c5529c16164ee53e4d99502ed1ec24202f36152b36281870bf285185672dc3` |
| `HERO_BENCHMARK_SPEC.md` | 0.1 | Unchanged; approved in OA-006 | `d1a0849d888a35ae3c9bd552bb920ee46417b7eeb4f8b687f8b5825e6fb851b2` |
| `THEORY_TO_CODE_TRACEABILITY.md` | 0.2 | AF-003 corrective proposal; acceptance pending | `1b94c402804c1167bfc5c04b45a86364ac5061bc41273b87a36f184991bbeec2` |
| `VALIDATION_AND_FALSIFICATION.md` | 0.2 | AF-001/002/003 corrective proposal; acceptance pending | `6aaa5b01290d3c6b9746f20d47c2092c038587d72d7e090ee3ad73438794ef00` |

The SD and SI PDF fingerprints remain those verified against PLAN Appendix A. The audit makes no modification to either publication.

### 7.7 Owner review and stop point

Review requested: accept or revise findings AF-001 through AF-003, the corresponding v0.2 contracts, and the integrated audit dispositions. The adopted scientific/product decisions are preserved; any requested alteration to them must be separately identified before freezing the affected baseline.

Current state: **AUDIT COMPLETE FOR REVIEW; OWNER ACCEPTANCE PENDING**. There is no recorded Step 8 acceptance, Step 9 preparation authorization, final Phase 0 approval, Phase 1 execution instruction, repository write, model call, expense, program execution, independent-evidence acceptance, or publication.

After actual owner acceptance and instruction to continue, the next permitted Phase 0 action is Step 9: create only `PHASE_0_APPROVAL.md` under the governing plan. Its initial status must distinguish readiness from actual final approval and implementation permission. This delivery stops at Step 8.

## 8. Revision record

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-16 | Step 2 proposed scope/definition decisions and OA-001 authorization record. |
| 0.2 | 2026-09-16 | Record OA-002; resolve UD-001 through UD-003 at their approved scope; submit UD-004's general contract component; preserve its pending hero-task component and all outstanding evidence/deferred items. |
| 0.3 | 2026-09-16 | Record OA-003 and prior-file fingerprints; approve UD-004's general contract while retaining hero-task selection; submit UD-005's Step 4 estimator/diagnostic component; preserve later experiment-design and empirical-evidence gates. |
| 0.4 | 2026-09-16 | Record OA-004 and Step 4 fingerprints; resolve UD-005's metric/diagnostic component; submit UD-006's integrity protocol while retaining its actual-evidence gap; preserve Step 6 task/design and Step 7 test gates. |
| 0.5 | 2026-09-17 | Record OA-005 and Step 5 fingerprints; resolve UD-006's integrity-protocol component while preserving the actual-evidence gap; submit UD-004's bounded sorting/class proposal and UD-005's matched A/B/C design; retain Step 7 mapping and all implementation/collection gates. |
| 0.6 | 2026-09-17 | Record OA-006 and Step 6 fingerprints; resolve UD-004's hero design and UD-005's concrete study design; submit the Step 7 traceability, 54-check validation catalogue, and bounded P1/P5 outcome convention; preserve independent-evidence, integrated-audit, final-approval, and implementation gates. |
| 0.7 | 2026-09-17 | Record OA-007 and Step 7 fingerprints; resolve UD-005's mapping/outcome component; complete the integrated audit for review; propose AF-001/002/003 corrective wording in MET/TRACE/VF v0.2, preserving all scientific/scope decisions; retain UD-006 evidence and UD-007 deferral, with Step 8 acceptance and Step 9 still pending. |

This Step 8 update revises the register and the three finding-linked specifications identified in Section 7. The plan, scope, definitions, structural-class contract, integrity contract, hero specification, and both theory PDFs remain byte-for-byte unchanged. The integrated document audit and limited document/arithmetic QA are completed for review. No implementation test, candidate-code execution, independent annotation exercise, model experiment, repository change, owner acceptance of this audit, final Phase 0 approval, or publication action is recorded as completed.
