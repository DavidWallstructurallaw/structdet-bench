# PHASE_0_APPROVAL

## StructDet-Bench: Audited Baseline and Bounded Phase 1 Handoff

| Field | Value |
|---|---|
| Document version | 0.1 |
| Record date | 2026-09-17; no exact local decision timestamp asserted |
| Phase / step | Phase 0 / Step 9 |
| Status | READY FOR OWNER REVIEW |
| Decision authority | Theory Owner |
| Governing plan | `PHASE_0_PLAN.md`, version 0.1 |
| Baseline presented | Ten preceding documents identified in Section 3, including the Step 8 corrections |
| Preparation authorization | Received: owner requested generation of `PHASE_0_APPROVAL.md` |
| Final consolidated baseline approval | PENDING |
| Phase 1 implementation authorization | Not received |
| Current permitted write | `PHASE_0_APPROVAL.md` only |
| Dependency on either other toolkit | None |

## 1. Purpose and authority

This record identifies the exact Phase 0 baseline submitted for final approval and hands off the first executable capability without expanding its scope. It completes the eleven-document review set required by the governing plan. It contains no implementation, detailed Phase 1 execution plan, benchmark result, or independent-validation certificate. [PLAN §§4-5, Step 9]

The technical readiness conclusion is bounded: the Step 8 audit identified no unresolved technical design blocker for the first offline milestone in the corrected candidate baseline. Final owner approval and permission to implement remain separate from that conclusion. [UD §7.1]

Source-derived requirements retain their origin. Engineering choices adopted through the earlier owner decisions remain product decisions. This record consolidates their identities and gates; it introduces no new metric, structural class, threshold, study budget, test requirement, or mandatory project artifact.

Reference keys follow the existing contracts: PLAN, SCOPE, DEF, SC, MET, EI, HERO, TRACE, and VF refer to their correspondingly titled files in Section 3; UD refers to `UNRESOLVED_DECISIONS.md`. SD and SI identify the supplied publications in Section 4. Section references use the frozen versions listed here.

## 2. Actual authorization and pending approval

### 2.1 Prior decisions

The frozen register records the following sequence. Its detailed quotes, scope statements, and earlier delivery fingerprints remain authoritative. [UD §2]

| Record | Adopted content / authorized progression |
|---|---|
| OA-001 | Proceed under the Phase 0 plan with the Step 2 documents. |
| OA-002 | Adopt Step 2 scope, definitions, and UD-001 through UD-003; proceed to Step 3. |
| OA-003 | Adopt the general structural-class contract; proceed to Step 4. |
| OA-004 | Adopt the metric/diagnostic contract; proceed to Step 5. |
| OA-005 | Adopt the integrity protocol, while retaining its actual-evidence gap; proceed to Step 6. |
| OA-006 | Adopt the bounded sorting task and concrete A/B/C design; proceed to Step 7. |
| OA-007 | Adopt Step 7 traceability and validation rules; authorize the integrated Step 8 audit and finding-limited corrections. |

The Step 8 delivery presented AF-001 through AF-003, the revised contracts, and the audit. It identified preparation of this record as the next action.

### 2.2 Latest instruction

The owner then instructed:

> 生成 `PHASE_0_APPROVAL.md`

This instruction authorizes preparation of Step 9 from the delivered audit baseline. The request and its context are recorded here because Step 9 permits no update to the decision register. It advances preparation to this final-review record; no separate, explicitly worded consolidated-baseline approval or implementation instruction has been received.

Accordingly, this document uses **READY FOR OWNER REVIEW**. The ten-file manifest and AF-001 through AF-003 are presented together for the final decision. Their final acceptance can be covered by one explicit approval of this identified baseline; no additional round of technical design is imposed.

### 2.3 Final approval fields

| Approval field | Recorded value |
|---|---|
| Owner's final baseline decision | PENDING |
| Approver | PENDING |
| Approval date / identifying instruction | PENDING |
| Approved baseline identity | PENDING; candidate is the exact manifest in Section 3 |
| Final acceptance of the Step 8 audit and AF-001/002/003 | PENDING as part of the consolidated baseline decision |
| Instruction to prepare a detailed Phase 1 plan | Not received |
| Instruction to begin implementation | Not received |
| Repository creation / commits / publication | Not authorized |
| Model calls / spending / generated-program execution | Not authorized |

Earlier files retain historical proposed-status headers and references to the decisions pending when they were written. The register supplies their subsequent approvals; this record supplies the later Step 9 preparation context. Those historical headers neither undo an actual approval nor establish an approval that has not occurred. No preceding file is rewritten to normalize its header.

## 3. Exact baseline manifest

SHA-256 values below were recomputed from the actual supplied bytes during Step 9. The first nine match the Step 8 delivery table in UD §7.6; the tenth identifies the delivered register itself.

| File | Version | SHA-256 | Approval / revision history |
|---|---|---|---|
| `PHASE_0_PLAN.md` | 0.1 | `5df37f3fef1d012d462a116d7839909c9379dfe6d59a1b3356cae004bcfac6a4` | Governing plan; execution under it recorded from OA-001 |
| `PROJECT_SCOPE.md` | 0.1 | `2eec02825c8df4281cc538d00dcb809907dc2eb8a2b1b73b597cbab17d975a11` | Adopted in OA-002 |
| `DEFINITIONS_AND_UNITS.md` | 0.1 | `a3da3e356a21f59468178050944baf58787edd65204fbf40b3b1742cd38104ab` | Adopted in OA-002 |
| `STRUCTURAL_CLASS_CONTRACT.md` | 0.1 | `00ba09dd879f5fe02a3302a6f1ad36bda1c6b7e2723562f5f62ec85fed125328` | Adopted in OA-003 |
| `METRICS_SPEC.md` | 0.2 | `23b45934e87767ca87e56b97aa4e1d1abdd49e27187d0b9c5a336ca516a96edb` | v0.1 adopted in OA-004; v0.2 carries AF-001 |
| `EVALUATION_INTEGRITY.md` | 0.1 | `50c5529c16164ee53e4d99502ed1ec24202f36152b36281870bf285185672dc3` | Adopted in OA-005 |
| `HERO_BENCHMARK_SPEC.md` | 0.1 | `d1a0849d888a35ae3c9bd552bb920ee46417b7eeb4f8b687f8b5825e6fb851b2` | Adopted in OA-006 |
| `THEORY_TO_CODE_TRACEABILITY.md` | 0.2 | `1b94c402804c1167bfc5c04b45a86364ac5061bc41273b87a36f184991bbeec2` | v0.1 adopted in OA-007; v0.2 carries AF-003 |
| `VALIDATION_AND_FALSIFICATION.md` | 0.2 | `6aaa5b01290d3c6b9746f20d47c2092c038587d72d7e090ee3ad73438794ef00` | v0.1 adopted in OA-007; v0.2 carries AF-001/002/003 |
| `UNRESOLVED_DECISIONS.md` | 0.7 | `5539ebbf859d0d423845fceb8b9ceda065f05e202d86d2ae662912aa2632a412` | Step 8 register and integrated-audit snapshot |

The manifest covers all ten preceding Phase 0 documents. This approval record is the eleventh artifact; its revision is identified by its own version and revision history, without a self-referential hash.

Fingerprints establish file identity only. They do not establish when experimental criteria were registered, whether annotations are independent, whether evidence is true, or whether a scientific claim is valid. Future empirical registration retains its own timing and evidence requirements. [EI §9; VF VT-24]

If any manifest file changes, this record no longer identifies that changed file as the same baseline. An authorized revision must preserve the prior identity, name the reason and affected contracts/results, and obtain any approval required by PLAN. Superseded reports and evidence remain traceable.

## 4. Supplied theory identities

| ID | Supplied edition | Primary role |
|---|---|---|
| SD | Xiangyu Guo. *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness*. August 2026; supplied 27-page PDF. | Task-relative structural classes, entropy, convergence, support hierarchy, validity, and StructDet-Bench design. |
| SI | Xiangyu Guo. *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*. August 2026; version 1.0; supplied 31-page PDF. | Cross-generation support, categorical resampling baseline, structural exogamy, SHL, ERR, and evaluation integrity. |

**SD file:** `The Structural Determinacy of LLM Generation_ Active Structure, Convergence Frontiers, and the Misreading of Randomness.pdf`

**SHA-256:** `357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32`

**SI file:** `Structural Inbreeding in Synthetic Data.pdf`

**SHA-256:** `80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a`

Both fingerprints match PLAN Appendix A. The publications retain their own stated licenses. This record grants no permission to redistribute them or publish a repository.

The supplied editions and the project contracts form this record's basis. References to outside works inside the PDFs are not independently verified by this phase. Source notation and approved software conventions remain distinguished, including SD's resolution `R`, SI's resolution `ρ`, and the separately named reference registry. [PLAN §2; DEF §2]

## 5. Integrated audit disposition

The full integrated audit remains in UD §7. This table identifies the exact corrections included in the candidate baseline, without reopening adopted scientific choices.

| Finding | Included resolution | Affected candidate files | Preserved boundary |
|---|---|---|---|
| AF-001 | Withhold a locally unsupported assignment and recompute supported subsets when the shared frame remains valid. Retain original selection and coverage. A defective shared frame can restrict the wider calculation. | MET v0.2; VF v0.2 | No evidence waiver, new denominator, or global invalidation caused solely by one local failure. |
| AF-002 | Apply text eligibility to the endpoint that needs it. Missing proxy text can restrict P1 while leaving evidence-backed P5 count comparisons evaluable under their own requirements. | VF v0.2 | Class, validity, quality, independence, and other applicable gates remain unchanged. |
| AF-003 | Permit passive reads of declared local inputs. External locators remain metadata unless their materials are separately supplied locally. | TRACE v0.2; VF v0.2 | No input execution, automatic remote retrieval, model call, or dependency installation. |

The audit preserved the task, formulas, unweighted populations, exact thresholds, sampling design, quality bands, and interpretation rules. It retained 40 traceability rows, 36 report-field groups, 54 future checks, and mappings for all 82 upstream checks/fixtures. These are specification inventories, not passed implementation tests. [UD §§7.2-7.4; TRACE §§3-4; VF §§4, 8]

Final acceptance of this manifest includes these identified revisions. There is no additional unresolved scientific decision hidden in the corrections.

## 6. Scope handed off

### 6.1 Measurement layers and delivery levels

Layer A measures structural distributions under declared generation conditions. Layer B concerns support dynamics across documented recursive transitions. The first milestone and v0.1 implement a bounded Layer A path; Layer B remains a later capability. Repeated fixed-model inference calls do not become recursive-training rounds. [SCOPE §§3-4]

| Tag | Delivery boundary |
|---|---|
| M | First executable milestone: offline fixtures/imported records, core calculations, evidence/population accounting, and JSON/Markdown reporting. |
| V | Additional v0.1 offline capability: precollected A/B/C comparisons, the declared surface diagnostic, and paired fixed-suite resampling sensitivity. |
| E | Actual independent domain/annotation evidence and an authorized empirical collection. Record handling can be tested in M/V without satisfying E. |
| D | Deferred estimators or capabilities. M/V must report their absence honestly. |

These are the existing TRACE §1.2 tags. They do not authorize simultaneous implementation of every level.

### 6.2 First executable capability

After final approval and an explicit implementation instruction, build:

**Recorded realizations and imported hard-assignment evidence → passive local input and identity checks → selected populations and fixed prefixes → core structural calculations → JSON and Markdown reports.**

Inputs use the approved local JSON/JSONL interface. `fixture_only` and `adjudicated_import` retain separate acceptance rules. Classification, review, validity, metadata knowledge, calculation status, and claim disposition remain distinct. The two population views are `classified_all` and `classified_valid`. Missing and unresolved records remain visible in the selection and coverage accounting. [SCOPE §§4.1, 5; SC §6; MET §§3-4]

The core includes occurrence support; separately requested empirical-threshold support; entropy in nats; SCI; `effective_support_shannon`; `effective_support_simpson`; and fixed-prefix `structural_distinct_k`. Exact estimators, denominators, null cases, and tolerances remain in MET §§5-7 and VF §5.

Shannon and Simpson effective counts keep separate names. An empty accepted population has observed occurrence count zero with its qualifier, while its distribution entropy and concentration are undefined. Neither a zero nor an unavailable value may be silently replaced by the other.

The bounded task is `bounded_integer_sort`, version 0.1, with the `sorting_mechanism_partition` version 0.1 and eight-class reference registry specified in HERO §§3-4. Its domain is a plain integer list of length 0 through 256 with values 0 through 4095. The result is a new nondecreasing list preserving multiplicities, with the input unchanged. All artifact restrictions and membership boundaries remain those in HERO; this summary does not replace them.

### 6.3 Required first fixture

HERO §11 and VF §5.2 specify twenty stipulated records in four five-position groups, one fixture condition, and one prompt block. They are not collected model observations.

| Fixture result | Expected value |
|---|---|
| Positive class counts | `(8, 6, 3, 2, 1)` |
| Selected and accepted sizes | 20 in both views under the original fixture stipulations |
| Occurrence support | 5 |
| Thresholded support at 0.10 | 4 |
| Distinct-5 / distinct-10 / distinct-20 | 4 / 5 / 5 |
| SCI | `57/200` |
| Structural entropy | Approximately 1.392321254757429 nats |
| Shannon effective count | Approximately 4.024180367609189 |
| Simpson effective count | `200/57` |
| Empirical comparison / inter-prompt inference | Not established by this single-block fixture |

Exact contracts control rounded illustrations. Separate pinned variants cover invalid-but-classifiable records, unresolved/provisional assignments, local evidence loss, missing positions, and correction. Their expected inventories must not be substituted into the original fixture.

### 6.4 Required test handoff

Applicable **M portions** of VF's existing tests govern the first milestone:

| Existing checks | First-milestone responsibility |
|---|---|
| VT-01 through VT-06 | Identity, evidence-policy, group/inventory, population, validity, and empty/error-state handling. |
| VT-07 through VT-13 | Arithmetic, thresholds, effective counts, ordering, prefix inventory, and hero fixture/variant behavior. VT-12 applies here to its M inventory portion. |
| VT-14 through VT-18 | Frame compatibility, imported evidence records, unresolved cases, and correction of calculations or claim scope. |
| VT-19 through VT-24 | Passive input safety, report parity, provenance, annotation/intake records, and actual timing/exposure states. |
| VT-25 through VT-30 | Task/reference/domain/audit record handling and truthful gate enforcement; no fabricated substantive validation. |
| VT-36, VT-46, VT-47 | M artifact association, fixture-to-report path, and evidence-record gates. |
| VT-51 through VT-54 | Honest boundaries for deferred support, frontier, recursive, and recovery quantities. |

For M/E, M/V, and M/D entries, implement and test only the responsibility assigned to M at this gate. Actual E review and V calculations retain their own deliverables. A mock evidence-handling success cannot be recorded as successful independent annotation or domain validation. [VF §3.2]

A future completion report must identify applicable test results and justified inapplicability, preserve expected/actual evidence, and show reproducible reporting. Favorable P1/P5 results, live model access, reviewer recruitment, and completion of either other toolkit are not first-milestone acceptance conditions.

### 6.5 Later v0.1 comparison boundary

The already adopted empirical design remains six fixed prompt blocks, three conditions, four five-position calls per cell: 72 planned calls and 360 candidate positions, with a separate optional pilot. A uses the normal prompt at the proposed temperature 0.4; B uses the same prompt at 1.0; C requests different mechanisms at A's setting. These are planned controls, not executed calls or guaranteed provider capabilities. [HERO §§7-9]

V implements analysis of appropriately supplied records, including the lexical-trigram Jaccard diagnostic, matched structural comparisons, primary valid distinct-20, and the adopted paired fixed-suite resampling procedure. It does not add a provider adapter or generated-code runner.

P1 retains both surface-change and relative structural-change conditions. P5 retains both C/A and C/B comparisons and their applicable coverage/quality gates. Supporting, contrary, inconclusive, and not-evaluable results remain reportable. These operational outcomes and fixed-suite sensitivity limits are governed by VF §§6-7; the approval record changes none of them.

## 7. Remaining evidence and deferred work

| Item | Current state and responsible authority | Effect on handoff |
|---|---|---|
| UD-001 through UD-005 | Design decisions resolved through OA-002 to OA-007; Theory Owner reviews the final corrected manifest. | No unresolved technical design blocker identified for M in the Step 8 audit. |
| UD-006: integrity protocol | Adopted in OA-005; Theory Owner retains protocol/claim authority. | Required record and claim-handling rules remain part of M/V. |
| UD-006: actual evidence | OPEN. Later identified independent annotators, domain validators, and collector must supply applicable evidence; Theory Owner accepts the scoped claim. | Blocks only unsupported measurement/empirical assertions. Does not prevent separately authorized fixture implementation. |
| Later empirical run binding | Actual model/provider, controls, registered artifacts/resources, collection and validation permissions remain to be supplied under HERO §9. | Needed before the corresponding empirical work; no model selection or expenditure is required for M. |
| UD-007 | OPEN and deferred; resolve when the Theory Owner selects latent diagnostics. | No latent-support estimator in v0.1; no delay to M. |

No actual validated 32-program core, independent initial annotation pair, 8,995-case execution record, sampled generated-output audit, calibrated judge study, independently reviewed execution environment, or pilot/main model collection has been supplied by Phase 0. Document preparation is AI-assisted. Review of these documents does not constitute the required independent annotation exercise. [UD §6; EI §§5-6; HERO §§5-6; VF §2]

The two independent human initial annotations apply to the named core validity set; Tier 1 retains domain evidence and sampled human audit. These requirements do not expand into two reviewers for every generated output. Missing ancestry is recorded with its scope rather than converted into invented independence or a universal stop.

Deferred work includes probability-thresholded expressible support, latent diagnostics, soft/overlapping scoring, convergence frontiers and provenance, load-bearing intervention estimators, structural transmission, recursive retention/SHL, ERR, additional task families, live adapters, training, and execution services. Prerequisites remain cataloged in SCOPE §4.3 and MET §13. No completion of those designs is required for M.

## 8. Initial claim and safety boundaries

A tested fixture implementation may establish that the software follows its contract on the identified stipulated inputs. A qualified imported-label calculation may describe the accepted subset with its evidence limitations. Independently validated structural measurement and empirical theory comparisons require the additional scoped evidence and authorizations in EI §6.1.

The first milestone cannot establish full model capacity, complete expressible/latent support, representational extinction, recursive collapse, an exact realization-entropy estimate, independent evidence from vendor names, or a universal structural-intelligence/creativity/integrity score. Concentration remains separate from validity.

The approved implementation boundary is local and passive: read supplied materials as data, preserve controlled access and evidence references, and never execute candidate programs or instructions inside inputs. Remote locators cannot trigger retrieval. No source PDF redistribution, publication, repository operation, paid call, external recruitment, or real experiment is authorized by generating or approving this document alone. [PLAN §§1, 7; SCOPE §§5-7; EI §6; HERO §12]

## 9. Exit-condition assessment

The following checks concern specification readiness. They do not certify actual experimental evidence.

| Phase 0 condition | Disposition / controlling record |
|---|---|
| Exact source editions and identities | Recorded in Section 4; hashes match PLAN Appendix A. |
| Layer A/B, M/V/E/D, and interfaces | Defined in SCOPE, MET, and TRACE; bounded handoff in Section 6. |
| Context, horizon, resolution, support, units, validity, and uncertainty | Defined in DEF and SC; source differences remain explicit. |
| Every first-slice estimator has scope, denominator, edge-case rule, and inference boundary | MET and VF; AF-001 is included in the candidate. |
| Separate effective counts and their tests | MET; VF VT-07 through VT-09. |
| One hero family, classification evidence route, and external safety design | HERO; actual independent fulfillment remains UD-006. |
| Prespecified P1/P5 units, resource accounting, gates, and outcome handling | HERO and VF; AF-002 retains endpoint-specific applicability. |
| Lineage, independent review, tail retention, and correction | EI, SC, TRACE, and VF; outstanding evidence remains visible. |
| Requirement/component/test/report traceability | 40 TR rows, 36 RF groups, 54 VT checks, and 82 upstream mappings identified. |
| Integrated audit and remaining technical blockers | Audit complete for review; no unresolved technical design blocker identified for M in the corrected candidate. |
| Deferred and empirical-claim restrictions | Preserved in Section 7 and UD-006/UD-007. |
| Eleven required artifacts | This record completes the document set; all ten preceding identities appear in Section 3. |
| Actual final approval and permission to implement | PENDING / not received, as recorded in Section 2.3. |

The documentary baseline is ready for an explicit final decision. No empirical success condition or new dependency project is added to Phase 0 exit.

## 10. Verification performed for this record

Step 9 checks comprise reading the governing plan and supplied contracts; verifying versions and required-file presence; recomputing all ten document fingerprints and both PDF fingerprints; comparing them with the prior manifests; checking the TR/RF/VT inventories and 82 upstream mappings; checking this record's references and Markdown structure; and confirming that all preceding files remained byte-for-byte unchanged.

The hero arithmetic was independently recalculated as document QA against the stipulated counts. This does not execute benchmark software, candidate source, the 8,995-input suite, or any of the 54 future tests.

No independent annotation, calibrated model judgment, actual resampling study, model call, training, repository change, publication, or expenditure was performed in this step. The full integrated scientific-contract audit remains the Step 8 record; this preparation does not relabel it as completed empirical validation.

## 11. Final decision and next authorized action

The requested decision is approval of the exact ten-file baseline in Section 3, including the Step 8 audit corrections, while preserving the remaining evidence and deferred restrictions. This document's final approval fields remain pending until that explicit decision is received.

After approval, a separate instruction can authorize a detailed Phase 1 execution plan or bounded implementation. A planning instruction authorizes its named document, not implementation code. PLAN requires an explicit instruction to begin implementation; a detailed Phase 1 plan, if requested, is a subsequent deliverable outside Phase 0 and is not created here.

The first implementation objective remains the M fixture-to-report capability in Section 6. There is no requirement to wait for Recursive Integrity Toolkit or Source Integrity Toolkit. Further operational permissions retain their declared scope; file completeness and owner approval cannot substitute for missing scientific evidence.

**Stop point: deliver this approval record for review. No Phase 1 action is initiated.**

## 12. Revision history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-17 | Initial Step 9 final-review record; identifies the audited ten-file baseline and source fingerprints, records actual preparation authorization, preserves pending final approval and implementation permission, and hands off the bounded offline milestone without changing earlier files. |
