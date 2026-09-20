# Longitudinal record format

## Phase 3 Steps 2-6: records, observed trajectories, null models, empirical SHL and support assays

| Field | Value |
|---|---|
| Format document | 0.5 |
| Profile | `structdet_longitudinal_v1` |
| Extension version | `0.1` |
| Component methods | `longitudinal_records_v1`; `observed_longitudinal_v1`; `categorical_null_v1`; `categorical_mixture_selection_v1`; `anchored_log_decay_v1`; `endpoint_log_decay_v1`; `longitudinal_trajectory_sensitivity_v1`; `finite_family_binomial_threshold_v1` |
| Governing approval | `PHASE_3_PLAN.md`, especially sections 3-6, 8, 9 and Steps 2-6 |
| Implementation scope | Passive records, observed trajectories, categorical arithmetic, registered empirical/local SHL with complete-unit sensitivity, and finite-family support assays. Sections 1-9 retain the Step 2 API; sections 10-13 document Steps 3-6. |
| Scientific evidence | Supplied assertions and their dependencies; substantive independent validation is not performed |
| License | CC BY 4.0 under `LICENSING_NOTES.md` |

## 1. Current capability and its boundary

`structdet_bench.longitudinal_records.review_longitudinal(bundle)` inspects an already loaded local bundle. It returns immutable records, scoped issues, retained declarations and an input-context fingerprint. It does not calculate distributions, retention, categorical expectations, half-lives, probability-threshold membership, recovery, or uncertainty. It makes no model, network, training, execution or external evidence-acquisition calls.

The command-line longitudinal dispatch and report schema `0.3` belong to the approved Step 8. This step supplies the component API only. Existing M-only and A/B/C command-line paths retain their existing behavior; they are not claimed to validate a longitudinal request through this new component yet. Until Step 8, callers explicitly invoke the component below and do not interpret an older M report as longitudinal validation.

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.longitudinal_records import review_longitudinal, assert_current

bundle = load_bundle("path/to/bundle.json")
review = review_longitudinal(bundle)
assert_current(review, bundle)
print(review.requested, review.status)
for item in review.objects:
    print(item.ref, item.status, [issue.code for issue in item.issues])
```

All paths in that example are caller-supplied. The component does no file access after loading. The existing safe reader owns acquisition, hash validation, path restrictions and byte snapshots. This document introduces no alternate reader, record envelope, file role or automatic classifier.

### Source relationship

SD section 11 distinguishes fixed-model generation from between-generation dynamics and cautions that local convergence plus reuse alone does not establish support collapse. SI sections 3.3, 3.4 and 6 distinguish support levels, effective external contribution, generation, selection and learning; its categorical propositions in section 5 apply under the declared finite reconstruction assumptions. EC sections 2, 6, 7 and 10 require scoped validity, appropriate evidence, retained lineage and visible uncertainty. The pinned editions and their SHA-256 identities are recorded in `THEORY_SOURCES.md`.

The exact serialization below is the approved plan's engineering realization. It does not attribute these field names or software states to the papers. State names, source counts, complete forms and mock reviewers do not establish learning, independent ancestry, structural exogamy or recovery. No absent class is counted as extinct in this layer.

## 2. Extension activation and header

Place the object at `analysis_config.extensions.longitudinal`. Absence returns `requested=False`, `status=not_requested`. Explicit null, false, a non-object, an unknown version or an invalid required field is a requested contract error. Presence of a `comparison` key alongside `longitudinal`, including a null comparison declaration, is rejected. Use separately pinned requests for the two profiles.

Every header key and each collection below is required. Empty unused collections are written as `[]`. Unknown top-level fields are rejected. This prevents an arbitrary extension from becoming an executable plug-in.

| Key | Shape and meaning |
|---|---|
| `version` | Exact string `0.1`. |
| `profile` | Exact string `structdet_longitudinal_v1`. |
| `study_id` | Stable ID, equal to the enclosing bundle study. |
| `study_version` | Explicit version ID of the study declaration. |
| `data_role` | Existing material-role vocabulary; must equal the enclosing bundle's role. |
| `registered_design_ref` | Knowledge-tagged existing `preregistration` reference. |
| `source_pins` | Exact SD/SI/EC dictionary from `contracts.SOURCE_PINS`; all three pinned identities retained. |
| `method_id` | Exact string `longitudinal_records_v1`. |
| `capabilities` | Unique subset of `observed`, `categorical_null`, `half_life`, `support_assay`, `recovery`. Declaring a capability does not implement or evaluate it. |
| `limits` | Explicit object, optionally empty, containing only lower allowed workload limits from section 8. |
| Collections | `states`, `panels`, `measurements`, `roots`, `transitions`, `trajectories`, `observed_requests`, `null_scenarios`, `shl_requests`, `assays`, `interventions`, `recovery_episodes`, `revisions`, `replays`. |

Malformed core analysis configuration is a separate scoped error. It cannot supply a valid selection merely because its longitudinal extension is well formed. The existing record-file roles remain `observations`, `evidence` and `registry` with their approved formats.

## 3. Common types, versions and evidence

### 3.1 Types used in the tables

`ID` uses the existing bounded identifier contract. `Text` is a nonempty string. Integers are actual integers, never booleans. A timestamp is an explicit-offset ISO timestamp; naive dates do not create an ordering claim. `Digest` means a full lowercase SHA-256.

`K(T)` means the existing knowledge-tagged representation of a value of type T. Known values must pass T's validator. `unknown`, `unavailable`, and justified `not_applicable` retain their original meanings; unavailable and not-applicable states require reasons. A known null is allowed only where `null` is explicitly listed. Unknown does not become a known null, zero, empty ancestor list or false flag.

`Exact` accepts a nonnegative exact JSON number token, a decimal string or an actual integer. `Probability` is strictly positive and at most one. A binary Python float is rejected by direct component validation; the safe JSON reader preserves a decimal token as `ExactNumber` before it reaches this layer. Numeric token lengths and exponents are bounded. These are representation checks only; later steps own normalization and numerical methods.

An object reference is exactly:

```json
{"object_kind":"state","object_id":"S0","object_version":"0.1"}
```

An existing core reference retains its existing exact three keys:

```json
{"record_type":"cell","record_id":"cell1","record_version":"0.1"}
```

The tables abbreviate these as `Ref(kind)` and `Core(type)`. References always carry an explicit kind and version. No filename, timestamp, row order, bare string, lexicographic maximum or latest-version lookup substitutes for this identity.

### 3.2 Object envelope

Every object contains exactly these common fields plus the fields listed for its family:

| Key | Meaning |
|---|---|
| `object_kind` | Singular family name from the schema tables. |
| `object_id` | Stable ID within that kind. |
| `object_version` | Explicit content version ID; distinct from the extension schema version. |
| `evidence` | All six evidence-role lists below, including empty lists. |

One request selects at most one content version per stable kind/ID. Duplicate identical entries and competing versions of the same stable ID are both rejected as ambiguous. This implementation does not choose one or count repeated entries as extra states. Separate pinned analyses preserve older versions. A genuinely distinct state or revision uses its own explicit ID and relationship; a renamed state is not a new observation.

### 3.3 Role-specific evidence dictionary

| Role key | Allowed existing record types |
|---|---|
| `origin` | `source`, `evidence`, `lineage` |
| `process` | `evidence`, `domain_result`, `budget`, `sampling_plan` |
| `independence` | `independence_assessment` |
| `validation` | `evidence`, `domain_result`, `audit`, `domain_suite` |
| `review` | `role`, `adjudication`, `annotation`, `integrity_assessment` |
| `correction` | `correction`, `intake` |

The checker resolves supporting payloads through the existing `EvidenceIndex`. Inactive, unavailable, conflicted, corrected or missing decisive records restrict their consumer. Mock or fixture status is retained down explicit decisive dependencies; it cannot be hidden by changing an upper-level record to nonfixture.

A supporting payload may declare `extensions.longitudinal_target` as an object reference. A directly consumed targeted record must match that object. Its supporting dependencies can have their own targets. This optional declaration strengthens target linkage; its absence provides no independent target-validation guarantee.

Only explicit `evidence_refs` and `reviewer_refs` are traversed as decisive support dependencies. A cycle of these references cannot supply independent support. General parent, later-review, correction-target and revision links remain reviewable without a universal DAG restriction. Every result has `substantive_validation_performed=False`.

## 4. Subject and measurement families

### 4.1 `states`: kind `state`

| Field | Type |
|---|---|
| `state_kind` | `model_system`, `corpus`, or `categorical_scenario` |
| `stage_role` | `probe_output`, `generated_candidates`, `post_preprocessing`, `post_selection`, `training_exposure` |
| `state_time` | `K(timestamp)` |
| `subject_identity` | `K(kind-specific object)` below |
| `ancestor_refs` | `K(list[Ref(state)])` |
| `measurement_refs` | `list[Ref(measurement)]` |

For `model_system`, subject identity contains exactly six tagged fields: `parameter_identity`, `checkpoint_sha256`, `serving_identity`, `retrieval_identity`, `tool_identity`, `system_identity`. All except the digest are `K(Text)`; the digest is `K(Digest or null)`. Model/system state uses `probe_output`.

For `corpus`, identity contains `corpus_identity: K(Text)`, `content_sha256: K(Digest)`, `unit`, and `material_refs: list[Core(artifact or raw_artifact)]`. Unit is one of `documents`, `training_rows`, `tokens`, `weighted_exposures`. A corpus state uses a corpus stage rather than `probe_output`.

For `categorical_scenario`, identity contains `scenario_identity: ID` and a nonempty `classes: list[ID]`. It is a declared abstract scenario, and cannot turn an empirical cell into categorical reconstruction observations.

Known ancestor references are declarations, not certified origins. An unknown ancestor set remains unknown. The ancestry list can retain known transitive ancestors used by a composite transition; it is not automatically inferred from the event graph. State measurements and measurement-state references must agree.

### 4.2 `panels`: kind `panel`

Fields are `frame_ref: Core(frame)`, `protocol_ref: Core(protocol)`, `registry_ref: Core(reference_registry)`, `stage_role`, `view`, `planned_realizations: K(positive integer)` and `selection_rule: K(Text)`.

`view` is `classified_all` or `classified_valid`. A panel is a recurring task/protocol stratum, not a model-generation counter or an independent training replicate.

### 4.3 `measurements`: kind `measurement`

Fields are `state_ref`, `cell_ref: Core(cell)`, `panel_ref: K(Ref(panel))`, `frame_ref`, `protocol_ref`, `registry_ref`, `view`, `data_role`, `planned_realizations: K(positive integer)`, `selection_rule: K(Text)`, `sample_refs: K(list[Core(realization)])`, and `budget_ref: K(Core(budget))`.

The checker binds the actual core cell/frame/protocol/registry identity, version and declared selected IDs. It checks sample-cell association, state backlinks, panel identity/view/stage/budget/rule, material role and known model-parameter identity against the core checkpoint identifier. Selection order and original records are retained, and no classification or validity admission is repeated here.

The declared budget and actual selected inventory remain separate. A numerical matching gate is later work. Unknown or missing data stays visible. The same cell/view cannot be reused as observations of two different states. Two explicitly requested views of one state remain distinct and can use the same underlying observations.

### 4.4 `roots`: kind `root`

Fields are `ancestor_refs: K(list[Ref(root)])`, `dependency_group: K(ID)`, and `independence_ref: K(Core(independence_assessment))`.

Repeated trajectories in the same dependency group never become independent roots through naming. Unknown dependencies are preserved. Even a complete root form returns `independence_established=False`; substantive independence evidence remains a separately reviewed scientific requirement.

## 5. Transitions, explicit paths and clocks

### 5.1 `transitions`: kind `transition`

| Field | Type |
|---|---|
| `transition_kind` | `categorical_reconstruction`, `synthetic_replacement`, `accumulation`, `subset_reuse`, `curation`, `learning_update`, `inference_configuration`, `composite` |
| `parent_refs` | `K(nonempty list[Ref(state)])` |
| `child_ref` | `Ref(state)` |
| `round_distance` | `K(nonnegative integer)` |
| `event_time` | `K(timestamp)` |
| `process_status` | `planned`, `attempted`, `completed`, `failed`, `unknown` |
| `effective_change` | `K(boolean)` |
| `parameter_change` | `K(boolean)` |
| `retained_parameters` | `K(boolean)` |
| `retained_data_refs` | `K(list[Core(artifact or raw_artifact)])` |
| `contributions` | List of contribution records below |
| `external_contribution_refs` | `list[Core(source or evidence)]` |
| `component_refs` | `list[Ref(transition)]`, nonempty for a composite |

Each contribution has exactly `parent_ref`, `weight: K(Exact)`, `unit`, and `evidence`. Unit is `documents`, `training_rows`, `tokens`, `sampling_probability`, or `reproductive_weight`. Each contribution must name an actual parent. A multiple-parent event retains a contribution record for every named parent. Units are not converted or normalized into one another. Matching labels or weights cannot causally assign descendant behavior to one source.

A `categorical_reconstruction` links categorical states, `curation` links corpus states, and `inference_configuration` links model/system states. A `learning_update` produces a model/system state. A completed event requires a process-evidence reference to count as a documented transition; missing or limited supporting records leave history restricted.

`curation` and `inference_configuration` have round distance zero. Other elementary reproduction/learning events have distance one. An inference-only or curation record cannot simultaneously assert changed model parameters. These records preserve process completion, effective change and parameter change separately. A completed update with unchanged known checkpoint bytes retains its documented round. Matching bytes alone do not supply the event.

A composite selects an ordered list of elementary stages, with matching initial parent set, connected successive child/parent records, final child and summed distance. Nested composites are rejected by this initial profile. Component refs on an elementary event are invalid. A missing stage or unsupported component restricts the composite.

Known forward event edges must be acyclic, and known times must be consistent. Conflicting producers, self-cycles, dangling edges, malformed known-child transitions and limited ancestral events restrict affected descendants and selected trajectories. Unrelated states remain independently inspectable. The checker records restrictions rather than deleting defective rows.

### 5.2 `trajectories`: kind `trajectory`

Fields are `state_refs` (nonempty ordered list), `transition_refs` (ordered list), `round_coordinates` (equally long list of `K(nonnegative integer)`), `panel_refs`, `root_ref`, `schedule`, and `registration_ref: K(Core(preregistration))`.

Exactly one selected edge connects each adjacent state pair. A trajectory through a merge explicitly selects its path while the event retains all parents. The checker never chooses a branch from file order or the most recent timestamp. Repeated states/edges and mismatched endpoints are reported.

Adjacent coordinates must differ by the documented transition distance. Missing coordinates are not filled. Equal coordinates are valid for a zero-distance configuration/curation stage. A known two-round interval remains two rounds even when its intermediate measurement was intentionally not taken.

A schedule row has exactly:

```text
state_ref, panel_ref, recursive_round_index: K(integer),
observation_status, measurement_ref: K(Ref(measurement) or null),
reason: K(Text), evidence
```

`observation_status` is `observed`, `missing`, `intentionally_unsampled`, or `planned`. Every selected state/panel slot is explicitly represented once. An observed slot resolves its measurement to the same state/panel. An unobserved slot cannot carry a known measurement; missing and intentionally-unsampled rows preserve their reason. The component reports omitted slots, unexpected slots, unknown clocks and mismatches without backfill, interpolation or extra sample creation.

The preregistration reference and declared date remain visible. Unknown or invalid dates cannot demonstrate prior registration. A date after any known selected state time restricts the registration statement. Date comparison checks declared chronology only and cannot establish that registration actually occurred or that results remained unseen.

## 6. Later-stage requests: structurally validated now, calculated later

The complete required fields of the remaining families follow. All retain the common envelope and role-specific evidence. Shape-valid requests receive `calculation_status=not_evaluated_records_only` where applicable. A declared later capability never authorizes its implementation in Step 2.

| Collection / kind | Additional required fields |
|---|---|
| `observed_requests` / `observed_request` | `state_refs`, `trajectory_ref: K(Ref(trajectory) or null)`, `view`, `support_type: occurrence or empirical_frequency`, `threshold: K(Probability or null)`, `matched_budget: K(positive integer)`, `protected_tail_ref: K(Core(tail))`, `comparison_mode: matched or descriptive`. |
| `null_scenarios` / `null_scenario` | Nonempty `classes`, exact nonnegative `p` vector, `n: K(positive integer)`, nonnegative `steps`, `q: K(vector or null)`, `schedule: K(list[positive integer] or null)`, `assumptions`, `child_counts`. |
| `shl_requests` / `shl_request` | `trajectory_ref`, `start_ref`, `end_ref`, `anchor_ref`, `view`, `fit_mode: local or anchored`, `residual_criterion: K(Exact)`, `panel_refs`, `sensitivity_ref: K(Ref(replay) or null)`, `registration_ref: K(Core(preregistration))`. |
| `assays` / `assay` | `state_ref`, `family_id`, `family_version`, nonempty `intervention_refs`, `success_event: class_membership or valid_class_membership`, `registry_ref`, `tau: Probability`, `alpha: Probability`, `allocation: bonferroni_equal`, `trials`, `iid_evidence_ref: K(Core(independence_assessment or evidence))`. |
| `interventions` / `intervention` | `pre_state_ref`, `post_state_ref`, `intervention_kind: inference_configuration, tools, retrieval, evidence, curation or training`, `parameters_changed: K(boolean)`, `direct_answer_injection: K(boolean)`, `external_refs: list[Core(source, evidence, artifact or raw_artifact)]`. |
| `recovery_episodes` / `recovery_episode` | `pre_assay_ref`, `post_assay_ref`, `intervention_ref`, `registry_ref`, `criterion_version`, `non_injection_ref: K(Core(evidence))`, `external_validation_refs: list[Core(evidence, domain_result or audit)]`. |
| `revisions` / `revision` | `revision_kind: metadata, membership, validity, schema, lineage or independence`, `event_type: correction, distributional_reopening_event or structural_reopening_event`, `affected_refs`, `original_refs: list[Core(artifact or raw_artifact)]`, `old_identity: K(Text)`, `new_identity: K(Text)`, `disposition: received, provisional, applied, rejected or withdrawn`. |
| `replays` / `replay` | `artifact_ref: Core(artifact or raw_artifact)`, `expected_sha256`, `method_id`, `plan_sha256`, `unit_refs: list[Ref(root or trajectory)]`. |

Null `assumptions` has exactly five `K(boolean)` fields: `finite_multinomial`, `fixed_classes`, `closed`, `empirical_reconstruction`, `exogenous_schedule`. `child_counts` is a list of nonnegative integer vectors. The checker checks declared class/vector/schedule dimensions; it does not normalize p, test a probability sum, evaluate a null law, or infer that an empirical lineage satisfies its assumptions.

An assay trial has `trial_id`, `intervention_ref`, `measurement_ref: K(Ref(measurement) or null)`, `sample_ref: K(Core(realization) or null)`, `status: planned, observed, failed, missing or unresolved`, and `evidence`. Observed trials bind to their own assay state, measurement and selected sample. Duplicate trial/sample identities and outside-family references are restricted. Training changes cannot be relabeled fixed-model assay interventions. Missing members remain in the declared inventory. Independent calls, one-position selection, success counts and exact tail decisions are later Step 6 work.

Recovery checks the declared pre/post state endpoints, registry, family/version, success event, tau, alpha and allocation identities. A changed criterion cannot silently redefine the earlier missing set. Numerical equivalence is not substituted for changed criterion tokens in this identity layer. Non-injection and validation refs are retained, without a numeric ERR or certification of recovery.

Revisions preserve affected refs and original material. They add zero model observations and establish no model recovery. Structural reopening is an explicit received/reviewed/applied declaration, not something automatically detected from a version bump. Replay material is passive; its acquired digest is checked without executing or generating its indices.

## 7. Outputs, scoped issues and consumed-context identity

`LongitudinalReview` retains requestedness, status, frozen configuration, method, configuration fingerprint, consumed-input fingerprint, immutable object bindings, issues, limits, workload and bound cell IDs.

Object bindings contain an exact `ObjectRef`, locator, frozen original data, status, issues, retained details and mock-evidence flag. `get(kind, id, version)` resolves only a unique shape-valid version. It never returns a latest version. A semantically limited object remains accessible with its limitations; a contract-error object remains in `objects` but is not returned as resolved by `get`.

Statuses distinguish `not_requested`, `unavailable`, `contract_error`, `record_limited` and `record_consistent`. `record_consistent` certifies neither a statistical result nor empirical truth. Issues have a bounded code, JSON-pointer-like location and severity. Cross-object restrictions do not manufacture an empty probability distribution or erase unrelated descriptive states.

The fingerprint covers actual loaded bytes as well as their declared identities, raw and typed records, full manifest, selected IDs, limits, artifact/access states, diagnostics and acquisition completeness. `assert_current` rejects a review belonging to a different snapshot. A matching display ID, stale declared content hash, unchanged label or changed workload limit cannot bypass it. No source file is reopened to obtain this fingerprint.

Component results retain private evidence and original declarations for controlled local audit. They are not the public redacted JSON/Markdown renderer. That renderer is later Step 8 work and must apply the existing privacy rules. No raw source prose, personal mappings or unrestricted paths should be copied into a public report merely by serializing this internal dataclass.

## 8. Workload and safe-failure rules

| Limit | Default maximum |
|---|---:|
| States | 256 |
| Transitions | 1,024 |
| Trajectories | 64 |
| Panels per trajectory | 64 |
| Measurements and schedule rows per trajectory | 16,384 |
| Nested declaration nodes / decisive evidence visits | 100,000 each |
| Interventions per assay | 16 |
| Categorical classes | 128 |
| Declared trials per intervention cell | 2,048 |
| Tail summands, later numerical stage | 2,000,000 |
| Exact bits, later numerical stage | 262,144 |
| Forecast steps | 10,000 |
| Sensitivity replicates | Exactly 2,000 |

The header uses the exact names in `longitudinal_records.LIMITS`. Callers may lower positive workload limits. They cannot raise them, use a boolean as an integer, request an unknown limit or change the named replicate count. The configuration traversal counts containers and scalar nodes and also respects the existing reader's maximum depth. Decisive-evidence traversal has a separate cumulative visit count under the same `max_link_objects` ceiling.

Exceeding a schema/workload cap is explicit, without truncation, record dropping, float fallback or automatic resampling. Numerical limits are preserved for later consumers; this module does not spend that numerical work or claim those algorithms are implemented.

## 9. Fixture and acceptance mapping

`tests/fixtures/longitudinal_cases.json` is a fully specified mock record template pinned to the approved plan. The base study has states S0, S1 and S2, two completed declared updates with unchanged checkpoint bytes, two measured cells and one intentionally unsampled intermediate panel position. The round sequence stays 0, 1, 2. The base template is supplemented with all fourteen family shapes by the test helper; they do not produce scientific observations.

The test materializer uses the existing safe input format and mock evidence helper. It loads the eight-class registry as a registry file and never executes the candidate contents. Fork, merge, incomplete ancestry, review-cycle, reproduction-cycle, clock, role, version, budget, selected-inventory, stale-context and malformed-request cases carry explicit expected behavior.

| New requirement | This step's tested scope |
|---|---|
| P3-L02 | Opt-in presence, strict version/profile, explicit types, limits, request identities and old-bundle preservation. |
| P3-L03 | Distinct state/stage/corpus/probe units, exact measurement references, views and evidence roles. |
| P3-L04 | Typed reproduction graph, forward order, forks/merges, incomplete and contradictory history, local restriction. |
| P3-L05 | Explicit recursive distances and selected paths, zero-distance interventions, complete planned schedules and known gaps. |

P3-L01 remains the accepted exact-baseline gate. All later L, report and oracle requirements retain their separate status. Software fixtures cannot close UD-006, perform actual human annotation, establish externally validated mechanisms or count model training rounds. Step 2 stops before observed structural calculations in Step 3.

## 10. Phase 3 Step 3: observed trajectories and stage/tail accounting

This section extends the document to revision 0.2. Sections 1-9 continue to define the unchanged Step 2 record API; the new numerical API is separate. Extension/profile version `0.1`, `longitudinal_records_v1`, and all fourteen record families retain their existing meaning. The new component method is `observed_longitudinal_v1`.

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.longitudinal_records import review_longitudinal, ObjectRef
from structdet_bench.populations import build_populations
from structdet_bench.longitudinal import (
    observe_longitudinal, assert_current, combine_root_curves,
)

bundle = load_bundle("path/to/bundle.json")
bindings = review_longitudinal(bundle)
populations = build_populations(bundle)
result = observe_longitudinal(bundle, review=bindings, populations=populations)
assert_current(result, bundle)
for measurement in result.measurements:
    print(measurement.ref, measurement.diversity.status, measurement.diversity.value)
for request in result.requests:
    for pair in request.pairs:
        print(pair.change.retained, pair.change.became_unobserved,
              pair.change.newly_observed,
              pair.change.retention, pair.change.matched_retention_fraction)
```

`review` and `populations` are optional. The component recomputes current record bindings and M populations and checks supplied components for exact equality. It does not accept a matching display ID as a substitute. Actual consumed bytes, record identities, limits, file/access states and input diagnostics remain in the Step 2 context fingerprint. No file is reopened. The original M-only and A/B/C runtimes remain unchanged.

If the longitudinal declaration is absent, the new component returns `not_requested`. Malformed opt-in input retains its contract error. A request containing only future capabilities does not cause observed calculations: the `observed` capability must be explicitly declared. A valid observed analysis returns `available` or `available_with_limitations`, with each numeric value and binding retaining its own status. A limited neighboring object does not automatically erase supported state descriptions.

### 10.1 Per-measurement results and exact diversity

`ObservedStudy.measurements` contains one `Measurement` for each unique shape-valid declared measurement. It retains its state, kind, stage, view, original binding, original `CellPopulations`, distribution, exact diversity, class accounting, evidence issues, binding gate and stronger matching gate. Contract-error declarations remain in `result.review.objects`; they are never silently resolved to the newest version.

The distribution comes from the existing `population_metrics` function on the already admitted `classified_all` or `classified_valid` population. It is never rebuilt by guessing a label, by counting unresolved candidates, or by converting token or source weights into observations. All five original ratios and the two M population views remain accessible through `source_cell`. Class accounting separately shows accepted labels, valid outcomes, invalid outcomes, and unresolved validity.

The new value `gini_simpson_diversity` is the exact complement of the same population's SCI ratio. `Scalar.value` uses `fractions.Fraction` for rational values and an integer for counts. Its numerator, denominator, unit, reasons, qualifiers and `uncertainty_status=not_estimated` are explicit. No Q, entropy, within-class text statistic or bias-corrected diversity is substituted.

| Input state | Observed support | Gini-Simpson diversity |
|---|---|---|
| Counts 3 and 1 | Two occupied classes | `3/8`; original SCI is `5/8`. |
| Nonempty, one occupied class | One | Exactly zero. |
| Known empty accepted population | Occurrence set is empty | `undefined`, with no probability distribution. |
| Unknown selected universe or incompatible state/cell identity | `unavailable` | `unavailable`. |
| Some labels withheld under an otherwise known M population | Accepted subset remains visible | Conditional descriptive value; full-class matching fails. |

A bad state-to-measurement identity prevents attributing the cell's values to that state. Its independently constructed M accounting remains in `source_cell` for audit. Unknown ancestry or missing independent-evidence claims remain separate from the arithmetic over correctly bound observations. Source adoption and consistent forms never become independent structural validation.

### 10.2 Observed sets, exact thresholds and change records

Each `observed_request` retains its explicit state order, view, support type and threshold. `occurrence` uses positive accepted counts. `empirical_frequency` uses the existing exact-decimal threshold implementation and the original accepted-population denominator. Removing low-frequency classes does not renormalize the distribution. A positive threshold cannot count zero-frequency registry entries.

A nonempty population can have an empty thresholded set. An empty classified population has an undefined empirical-frequency threshold evaluation. These states remain distinct. Neither finite occurrence nor an empirical frequency cutoff estimates the probability-based support used by the later assay.

Adjacent requested endpoints are compared within each declared panel. The panel schedule chooses an exact measurement; missing or intentionally unsampled positions do not acquire another measurement merely because an unselected record exists elsewhere in the bundle. Standalone descriptions with no trajectory retain their explicitly supplied state order and report that a recursive clock is unavailable. Multiple competing measurements for the same endpoint/panel are not resolved by file order.

`SetChange` carries both endpoint sets, class-meaning compatibility, matching eligibility, retained IDs, became-unobserved IDs, newly-observed IDs, and the following descriptive values:

```text
observed_retention_fraction = count(intersection) / count(upstream)
observed_loss_fraction      = count(upstream minus downstream) / count(upstream)
observed_support_size_change = count(downstream) - count(upstream)
```

For upstream `{a,b,c}` and downstream `{a,c,d}`, the two fractions are `2/3` and `1/3`; the size change is zero. The unchanged size does not hide loss of `b` and appearance of `d`. A known empty upstream set has undefined retention/loss fractions; an unknown upstream set has unavailable fractions and unavailable set differences.

`retention` and `loss` are explicitly descriptive set arithmetic. If sampling/selection requirements fail but class meanings remain compatible, these fields retain `unmatched_descriptive`. The separate `matched_retention_fraction` and `matched_loss_fraction` properties are unavailable when the matching gate fails. A changed class space or view blocks the set comparison itself. This separates a visible unmatched observation from a claimed matched structural change.

### 10.3 Matching and conditional populations

Matched measurements use the declared budget, independent of Phase 2's 20-output arrangement. The implementation checks the actual first requested positions before class or validity filtering, their original order, attempt associations, selection membership, primary-success status, budget record and protocol identity. Missing positions cannot be filled from a later success. Later unselected positions may remain missing without replacing an otherwise complete earlier requested prefix.

Task/frame, class registry, protocol, selection rule, material role, declared budget and elicitation identity must be compatible. Candidate grouping is retained. Two samples from a common call do not become two independent generation experiments. Changed retrieval, tool, serving or system configuration is exposed separately from the parameter/checkpoint change that a model trajectory is intended to measure. Unknown protocol settings and an unavailable prompt artifact cannot establish matched control.

The primary matched profile requires full accepted hard-class coverage at the fixed budget. Valid-only sensitivity additionally requires complete decisive validity and classified valid observations. Its `validity_conditioned` qualifier and any `varying_valid_denominator` remain visible. This layer does not impose Phase 2's 80%, 90% or 95% thresholds. Per-state M descriptions may remain available when stronger matching fails.

Preregistration checks resolve the supplied active record and compare its declared offset-aware date with state observation times. A late or unknown declaration cannot satisfy this check. Successful chronology checking remains `declared_chronology_only`; software cannot establish that registration actually occurred or results were unseen.

An applied schema/membership/validity revision explicitly targeting a selected old state, measurement or panel flags the matched use as requiring a newly pinned reanalysis. It does not edit historical counts, infer a replacement label, or manufacture an increase in model ability. Full intervention/recut/correction interpretation remains Step 7 work.

### 10.4 Missingness, clocks and recurrence

`Pair` retains both endpoint states and measurements, the named panel, original recursive coordinates, supported elapsed distance, a separate clock gate, and intermediate schedule rows. A known distance of two rounds remains two when the intermediate observation was intentionally not taken. An unknown or inconsistent transition history withholds a recursive-rate interpretation rather than substituting API-call count, filenames or elapsed wall time. No half-life is computed here.

`ClassObservation` retains every registered state/panel slot, including missing, intentionally-unsampled, planned and undeclared/ambiguous slots. It records class count, frequency, observation state, recurrence flag and review availability. Registry classes with no accepted occurrences have zero observed count when that population is known; missing measurements have unknown counts. Empty denominators remain undefined.

The recurrence state is `observed_reappearance` when a previously observed class returns after a known nonappearance. `observed_after_gap` identifies return after unknown intermediate measurements without falsely asserting absence. Intervening gaps remain attached. Empirical-frequency nonappearance is explicitly named `below_empirical_frequency_threshold`, and the enclosing request retains that support type. A class-space identity change resets recurrence comparison rather than creating an automatic reappearance claim. All records retain `model_recovery_established=False` and no latent-extinction conclusion.

### 10.5 Fixed-panel and root curves

Each `Curve` uses exactly its declared panel set for its view at every scheduled state, equal panel weights, and `mean_panel_diversity`. Missing panels and undefined panel distributions cannot be omitted from the mean. A dangling or malformed panel binding retains an unavailable slot in every potentially affected view; its identity is never discarded to calculate a mean over the surviving panels. Individual point values remain separate from complete-grid, matching and clock eligibility. No pooled distribution is used: two single-class panels centered on different classes have mean panel diversity zero even though their pooled class counts would have diversity one half.

For an explicit selection of complete trajectory references, `combine_root_curves(result, refs, view=...)` first uses each curve's fixed-panel means, then equal root weights. The selected references, weights and common time grid are retained. Unknown or duplicate dependency units, multiple paths for one dependent root, reused observed rows, shared root ancestry, different panel sets and incompatible grids restrict the root summary. A missing point is not replaced by an average over the remaining roots.

Root names do not establish independent evidence or randomization. `independent_replicates_established` remains false. A shared fixed model checkpoint alone is not treated as proof that separately recorded draws are dependent. This component computes supplied-unit descriptive means without resampling, fitting, automatic path selection or a population-confidence claim. Later fit/sensitivity requests must add their own registration and dependency evidence.

### 10.6 Protected-tail declarations

The `protected_tail_ref` remains an existing `tail` record reference, with one class ID, original designation, rationale and review references per record. Several designated classes can be linked through `tail.reference_refs` containing other `tail` references; visited identities are not counted repeatedly. A cycle of references cannot multiply protected classes or sample mass. This is an engineering serialization of the approved tail requirement, not a new source definition.

Each tail record includes its exact `reference_registry` reference in `reference_refs` and the following narrowly named metadata extension:

```json
{
  "longitudinal_tail": {
    "registration_ref": {
      "record_type": "preregistration",
      "record_id": "registered-tail-design",
      "record_version": "0.1"
    }
  }
}
```

The preregistration's `material_refs` must explicitly contain that tail record. The tail's original `class_id`, `designation`, `basis`, `disposition` and `review_refs` remain unchanged. Protection is recorded only with a known registered class, nonempty designation/rationale, active `protected` disposition, compatible pinned registry and prior declared registration. Unknown or withdrawn entries stay visible with their reasons; they are not selected again based on favorable results.

Designations remain original labels. Low frequency and high consequence are not inferred from each other. `TailMember` preserves the original designation/rationale and per-time class ledger, plus the availability of review records. `records_available_only` establishes record access, not actual independent review. Observed class review status separately reports admitted records, incomplete classification, no observed member or unavailable data. Mock flags remain visible.

A protected reference class with zero probe occurrences contributes no observation. Tail failure, lack of review or unknown registration does not alter the underlying M distribution or fill a fixed sampling prefix.

### 10.7 Linked corpus-stage accounting

`StageTransition` retains candidate, preprocessing, selection, exposure and probe stage identities, explicit parents/child, declared contribution weights and their original units. It does not combine multiple parents into one inferred upstream probability distribution.

Stage retention is available only for compatible class meanings and a documented single-parent corpus-to-corpus material scope. The process evidence must explicitly bind the input and output artifact identities to that transition, using an existing evidence record's metadata:

```json
{
  "longitudinal_material_scope": {
    "transition_ref": {
      "object_kind": "transition",
      "object_id": "selection-stage-1",
      "object_version": "0.1"
    },
    "input_material_refs": [
      {"record_type":"artifact","record_id":"candidate-corpus","record_version":"0.1"}
    ],
    "output_material_refs": [
      {"record_type":"artifact","record_id":"selected-corpus","record_version":"0.1"}
    ]
  }
}
```

The artifact identities must match the respective corpus declarations and be available through the existing safe loader. The component checks a supplied relationship; it does not inspect prose to invent one. Missing scope, mismatched material units or ambiguous parent attribution withhold the stage-retention scalar while leaving supported per-stage observations visible. A curation event keeps its zero recursive learning distance.

All numeric counts continue to name classified realizations. A source declaration measured in tokens, documents or weighted exposures retains that original unit separately; it does not reweight a realization-count distribution. No result is named universal `structural_transmission`, and no corpus table certifies downstream model expression, effective learning or structural exogamy.

### 10.8 Workload, privacy and current stop

The component uses the existing record/resource ceilings. A conservative bound on materialized measurement/slot/class records and repeated observed-request work is checked against `max_link_objects`. An excess returns explicit `observed_workload_limit` without truncating states, panels, tails or output observations. Exact fixed-unit mean calculations additionally check `max_exact_bits`; no floating approximation replaces an over-limit rational calculation. The existing exact-decimal threshold comparison avoids expanding a huge power-of-ten denominator.

Results are immutable internal audit objects. They retain private declarations, source/evidence links and original populations. Do not dump an internal dataclass into a public report: the longitudinal redacted JSON/Markdown renderer and CLI dispatch remain Step 8 work. Ordinary M and A/B/C commands retain their prior meaning.

Step 3 closes P3-L06 through P3-L10 only after actual tests. P3-L01 through P3-L05 remain inherited. Null forecasts, SHL, trial-probability support, recovery and the final integrated report requirements remain future work. Independent structural validation, actual model experiments, candidate execution, hosted CI and UD-006 are not established by these software fixtures.


## 11. Phase 3 Step 4: exact categorical-null and mixture/selection components

This section adds the source's finite categorical model. Earlier sections' statements about the record-only and observed-only components remain scoped to those APIs. Their behavior, code and original tests have not changed. The profile and extension versions remain `structdet_longitudinal_v1` and `0.1`; no additional record fields or alternative input reader are introduced.

### 11.1 Source definitions and computed quantities

SI sections 5.1-5.6 and Appendix A specify finite closed multinomial reconstruction on an explicit fixed class space: `X_t | p_t ~ Multinomial(n,p_t)` and `p_(t+1)=X_t/n`. EC section 4 has the corresponding closed-evaluation model. The implementation evaluates the following conditional identities:

```text
D(p) = 1 - sum(p_z**2)
E[D_next | p] = (1 - 1/n) * D(p)
Pr(class z absent next | p) = (1 - p_z)**n
L(p,q) = sum((p_z - q_z)**2)
E[L_next | p] = L(p,q) + D(p)/n
```

The initial positive-probability support is explicit. Zero-probability classes receive no smoothing or pseudocounts. No step treats an empirical nonappearance as a true model zero.

For a fixed n, the expected trajectory uses `D0*(1-1/n)**t`. For a declared deterministic, exogenous schedule, it uses `D0*product(1-1/n_j)`. The latter is the engineering extension approved in plan section 4.3. Its expected target-error curve is the telescoping consequence `L0 + D0 - E[D_t]` under the same fixed-target assumptions. A mean n never replaces a supplied schedule, and state-dependent schedules remain unsupported.

Expected concentration is the complement of expected diversity. The module does not label the reciprocal of expected concentration as the expected inverse-Simpson count. Nonlinear transforms of expectations are not silently interchanged with expected transforms.

### 11.2 Bound-bundle API

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.categorical_null import evaluate_categorical_null, assert_current

bundle = load_bundle("path/to/bundle.json")
study = evaluate_categorical_null(bundle)
assert_current(study, bundle)
for entry in study.scenarios:
    print(entry.status, entry.reasons)
    if entry.result is not None:
        print(entry.result.expected_next_diversity)
```

The component consumes the already versioned `null_scenarios` collection and requires the `categorical_null` capability. Missing profile and missing capability are distinct from malformed requested input. Invalid or anonymous scenario rows remain explicit error entries. One defective scenario does not erase another scenario's arithmetic.

The five tagged assumption fields retain their existing names. Fixed-n predictions require `finite_multinomial`, `fixed_classes`, `closed` and `empirical_reconstruction` to be known true. A schedule additionally requires `exogenous_schedule` to be known true. Unknown and false assumptions withhold the conditional null predictions; independently defined parent arithmetic can remain visible. These are declared conditions, not proof that a neural training pipeline satisfies the null.

A known-null q means the optional target was deliberately omitted. Unknown/unavailable q withholds target-specific quantities; it does not invent an initial or uniform target. A malformed target also leaves independently valid diversity quantities intact. A known-null schedule selects fixed n. An unknown schedule cannot silently select fixed n instead. Unknown n without a supplied deterministic schedule remains unavailable and is never inferred from probe counts, tokens, rows or checkpoint size.

A caller-supplied `LongitudinalReview` must match a fresh full review of the same loaded snapshot. The consumed-context fingerprint includes actual bytes and record/limit/access state. Stale or altered contexts are refused without reopening files.

### 11.3 Direct mathematical API

```python
from fractions import Fraction
from structdet_bench.categorical_null import categorical_null, ASSUMPTIONS

assumptions = {name: {"state": "known", "value": True, "evidence_refs": []}
               for name in ASSUMPTIONS}
r = categorical_null(
    ["a", "b"], [Fraction(3, 4), Fraction(1, 4)],
    scenario_id="toy-1", n=4, steps=3, assumptions=assumptions,
    q=[Fraction(1, 2), Fraction(1, 2)], child_counts=[[3, 1]],
)
assert r.parent_diversity.exact_ratio == (3, 8)
assert r.expected_next_target_error.exact_ratio == (7, 32)
```

The Python API accepts exact `Fraction`, integer, `ExactNumber` and bounded finite-decimal-string operands. Binary floats and booleans cannot act as probabilities, n or integer counts. The existing physical bundle schema continues to use its decimal-token representation. Input vectors must have identical declared class order and exactly unit probability sum. Invalid sums are not renormalized. Direct shape/type errors raise bounded `InputError` codes; the bound API retains these as scoped scenario failures.

`scenario_id` is mandatory. `n` is a declared categorical sample size, between 1 and the existing signed-63-bit bound. When a schedule is supplied, n may be unknown (`None` at the direct API), or separately recorded; every actual forecast/count slot uses its supplied schedule entry. `steps` controls the finite forecast horizon. The separately labeled one-step conditional diagnostics can still be evaluated for a fixed n when `steps=0`; no additional trajectory observation is created.

### 11.4 Null timescale, applicability and crossing

For n>1, `structural_half_life_null` computes `log(2)/(-log1p(-1/n))`, with unit `categorical_recursive_rounds` and numerical evaluation `binary64_log1p`. This is a continuous conditional timescale. It does not fit an empirical trajectory or estimate a first realized zero-support time.

The optional integer `null_first_expected_half_crossing` is separately certified by exact rational bracketing. Its calculation is independent of rounding the logarithm and equals the mathematical ceiling when certified. A large n can have a valid finite logarithmic timescale while the integer certificate is unavailable under exact-bit limits. The module records that limitation instead of returning a rounded false integer.

For n=1, the logarithmic SHL is undefined. Positive initial diversity collapses in one categorical transition, recorded as a separate first crossing of 1 and `one_step_collapse_outside_log_domain`. No SHL=0, infinity, n substitution or smoothing is emitted. If D0=0, there is no positive diversity to halve. For n>1 the parameter timescale remains displayable with `conditional_parameter_timescale`; the actual crossing is undefined and `halving_applicability=no_positive_diversity`.

A deterministic schedule has no fixed-n SHL output. `null_schedule_first_half_crossing` searches only its declared steps. Failure to reach one half in that finite schedule remains explicitly unavailable with `not_reached_in_declared_schedule`, without an invented continuation.

### 11.5 Supplied count paths and expectations

Each supplied count vector retains its position and exact original counts, declared n, parent and child distributions, support identities, conditional predictions, realized values and restrictions. A count vector must contain nonnegative actual integers of the proper dimension and sum to its slot's n. Positive child mass on a parent zero is a closed-scenario violation. It remains recorded, rather than being repaired or discarded.

A malformed transition restricts later conditional path interpretations. A later independently valid count vector may still show its own distribution, explicitly without a valid earlier path. Too many supplied rows do not manufacture additional requested transitions; too few rows do not cause a simulated completion. The theoretical forecast from the original parent remains separate from the supplied realization.

A possible child can have higher realized diversity or lower realized target error than its parent. Expected contraction and expected target drift apply to the ensemble of possible transitions, not every path. Likewise, empirical-frequency-thresholded occupancy can increase while exact positive support stays unchanged. The observed component's legal `observed_reappearance` behavior remains untouched.

### 11.6 Explicit mixture and selection

```python
from structdet_bench.categorical_null import mixture_selection

r = mixture_selection(
    ["a", "b"], [1, 0], [0, 1],
    scenario_id="mix-1", class_space_id="toy-space-v1",
    effective_weight="0.5", lambda_unit="effective_preselection_probability",
    weights=[1, 0], weight_unit="reproductive_weight",
)
# candidate = (1/2, 1/2), selected = (1, 0)
```

This direct component evaluates SI section 6's `u=(1-lambda)*p+lambda*e` followed by `selected_z=w_z*u_z/sum(w*u)`. A single supplied class-space identity and ordered class list bind both vectors and all weights. The lambda and weight units in the example are mandatory exact labels for this component. Token share, row share, archive size, vendor count and arbitrary `real_data_ratio` objects are not accepted as substitute units. Lambda remains a declared effective parameter; arithmetic does not certify its empirical provenance.

Nonnegative exact weights need not sum to one. Scaling all of them by the same positive constant leaves the selected distribution unchanged and changes the normalizing mass. Negative weights and incompatible dimensions/units are input errors. Unknown weights, including individual knowledge-tagged unknown entries, preserve an available candidate mixture but withhold the selected distribution. Unknown lambda withholds the candidate mixture as well.

All-zero selected mass makes normalized selection undefined. This includes nonzero weights placed only on classes with zero candidate mass. The zero normalizing mass remains available; the selected distribution stays absent. A newly introduced class may therefore enter the mixture and be removed by selection. The module never fills `next_model_distribution` or certifies structural exogamy, recovery or learning from this arithmetic.

Mixture/selection is a Python component in Step 4. No additional unapproved serialized mixture request, command, data-generating simulation or inference from generic contribution metadata is introduced. Complete longitudinal CLI/report integration remains Step 8.

### 11.7 Results, limits and evidence scope

`NullScenario`, `CountTransition`, `ForecastPoint`, `MixtureSelection` and scalar `Quantity` results are immutable internal audit objects. Exact rational scalar results expose `exact_ratio`. Every scalar names its status, unit, reasons, numerical method and uncertainty state. Optional, unavailable and undefined results keep those distinctions. Original operands, class identities, actual schedules and null assumptions remain attached.

The inherited limits remain effective: at most 128 categorical classes, 10,000 forecast steps, 100,000 direct operand/path nodes and 262,144 bits for constructed exact integer operands, with existing lower-limit support. Direct operands have a conservative 64-level traversal cap before preservation. Decimal tokens retain their 1,024-character and 100,000-exponent bounds, and powers are preflighted before materialization. Rational operations cross-cancel before multiplication and check intermediate products and sums. A conservative estimate may refuse an endpoint rather than allocate beyond its allowance.

An over-limit forecast is unavailable as a whole; no shortened prefix is returned as the complete requested curve. Independently computable one-step, SHL or parent quantities can remain available when a separate endpoint exceeds its exact-work limit. There is no floating fallback for rational probabilities, no class pruning, no lower sample budget substitution, and no random approximation. Nonfinite logarithmic results are withheld with a numerical-failure reason.

These internal objects retain audit declarations, which can be private. The public/redacted report renderer is still later work. No raw dataclass dump is advertised as a public reporting interface.

### 11.8 Acceptance and stop

The new tests independently enumerate tiny multinomial count spaces and compare their probability-weighted diversity, omission and external-error moments with the production formulas. Seven saved null timescales come from a separate 100-digit Decimal log-difference calculation. Multistep and variable-n enumerated chains, legal pathwise increases, zero absorption, thresholded occupancy, bounded arithmetic and mixture/selection edge cases have separate checks.

Step 4 closes P3-L11 through P3-L16 only after actual complete regression. P3-O03 through P3-O08 have explicit arithmetic fixtures, while full longitudinal oracle/report conformance remains Step 9. Earlier requirement and method identities remain intact. Step 4 stops before empirical/local SHL fitting, sensitivity resampling, finite-family expressibility and ERR. All results remain conditional mathematical/software results; UD-006 and substantive independent validation remain outstanding.

## 12. Step 5: registered empirical/local SHL and complete-unit sensitivity

### 12.1 Source definition and engineering implementation

SI section 8.3, page 19 defines empirical Structural Half-Life through approximately geometric Gini-Simpson decline and explicitly calls for local or interval-specific descriptions when the trajectory is non-geometric. The exact categorical SHL in SI section 5.4 remains the separate Step 4 quantity. `PHASE_3_PLAN.md` sections 5.1-5.5 prescribe the anchored four-measured-state estimator, equal measured-time weighting, pre-inspection residual criterion and whole-unit sensitivity. These implementation choices are not attributed to an algorithm specified by the paper.

The new Python APIs are:

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.half_life import fit_half_lives
from structdet_bench.longitudinal_uncertainty import evaluate_longitudinal_sensitivity

bundle = load_bundle("path/to/bundle.json")
fits = fit_half_lives(bundle)
sensitivity = evaluate_longitudinal_sensitivity(bundle, half_lives=fits)
```

Both consume the safe reader's existing snapshots. The longitudinal extension requires `observed` and `half_life` capabilities and explicit `shl_requests`. No generation, training, source acquisition, candidate execution or automatic support assay occurs. CLI dispatch and public report rendering remain Step 8. Existing M-only and A/B/C behavior is unchanged.

### 12.2 Registered fitting window and criterion

The existing Step 2 `shl_request` schema is unchanged. It pins a trajectory, its start/end/anchor states, view, fixed panel list, fit mode, residual criterion, sensitivity reference and preregistration reference. Anchor must equal start. No alternate window, breakpoint, suffix, intercept or panel subset is searched automatically.

The referenced existing `preregistration` payload must have a `extensions.longitudinal_half_life_v1` object containing exactly:

| Field | Required meaning |
|---|---|
| `method` | `anchored_log_decay_v1`. |
| `request_ref` | Exact versioned SHL request object reference. |
| `request_sha256` | `configuration_fingerprint` of the complete pinned SHL request. |
| `trajectory_sha256` | `configuration_fingerprint` of the complete pinned trajectory declaration. |
| `aggregation` | `equal_panel_mean`. |
| `panel_refs` | Exact ordered list from the request. |
| `residual_rationale` | Nonempty predeclared explanation; local-only requests explicitly state that no geometric regime is asserted. |
| `inspection_status` | `registered_before_inspection`. |

`registration_witness(request, trajectory)` computes only the six identity fields through `panel_refs`; it does not create a registration, timestamp or evidence. The originating registration workflow supplies the rationale, inspection declaration, recorded date and supporting evidence. The date must precede all known scoped observations. Missing, late, corrected, inaccessible, conflicted or mock-for-nonfixture registration restricts the qualified result. These checks establish recorded consistency, never the truth of a declaration or independence of its author.

An anchored fit requires a finite positive exact residual criterion and its rationale. There is no default fit threshold. If the criterion cannot be established, the numerical slope/residual diagnostics may remain, but the qualified empirical half-life is unavailable. The explicitly requested two-endpoint calculation can remain visible; unverifiable registration marks it `registration_unverified_endpoint_description`. A local-only request requires its own registered interval to be qualified.

### 12.3 Quantities and applicability

`structural_half_life_interval = delta_t * ln(2) / ln(D_start / D_end)` is available only for positive compatible endpoints, a genuine positive documented round distance and positive decline. It says nothing about unobserved interior dynamics. Positive equality and growth give undefined declining half-life with separate reasons. A zero anchor or zero endpoint does not receive a pseudocount, zero half-life or fabricated infinity.

`structural_half_life_empirical` uses at least four registered measured states, the fixed anchor and equal measured-time weights:

```text
x_i = t_i - t_0
y_i = ln(D_i / D_0)
beta = sum(x_i*y_i) / sum(x_i*x_i), excluding the zero anchor term
SHL_empirical = -ln(2) / beta, when beta is negative and every gate passes
```

The result retains original state IDs, all round coordinates, all diversity values and slot statuses, measured indices, x, log ratios, slope, fitted values, log residuals and maximum absolute log residual. A small local increase is permitted when the predeclared global residual criterion passes. Flat or positive fitted slope has no finite declining half-life. The represented numerical maximum residual is compared inclusively against the exact criterion; implementation tolerance never changes that scientific acceptance boundary.

Only explicitly `intentionally_unsampled` interior slots may be omitted from the fitting rows. Their original round coordinates and schedule remain. A missing expected measurement blocks the global fit. Unknown intervening process blocks a recursive interval rate. Missing panels are never replaced by averaging the surviving panels. Known interventions, external-contribution changes or incompatible recuts inside a supposed unchanged regime restrict the fit. Every root selected for sensitivity receives that regime check, including roots other than the primary request's path. A separate predeclared post-intervention request can have its own new anchor.

`observed_half_crossing_bracket` and `first_observed_zero_bracket` are separate observations, retaining the last measured endpoint before the first observed crossing, the first crossing endpoint and any intervening unobserved IDs. Neither interpolates an exact crossing time. No crossing in the declared observations remains `not_observed`.

`compare_null(fit, null_scenario)` displays an explicitly supplied Step 4 null result beside the empirical result. It never obtains categorical n from a neural probe count, asserts a matched statistical comparison or identifies a causal acceleration mechanism.

### 12.4 Curve aggregation and conditioning

Per-measurement D continues to use the exact original admitted distribution. A curve first averages the fixed panel D values at each measured state. Root sensitivity then equally averages those within-root panel means. Neither operation pools class counts across panels, roots or times. The same fixed set and weights remain in every draw.

Both requested views retain their own original sample/validity accounting. `classified_valid` stays explicitly `validity_conditioned`, including on all recomputed point and draw fits. A corpus-stage curve stays `corpus_stage_not_model_capacity`. The internal `HalfLifeStudy` and `LongitudinalSensitivity.half_lives` retain the original observed study, measurement references, populations and evidence for controlled local audit. Public serialization is not authorized by this component API.

### 12.5 Optional sensitivity plan

A known-null `sensitivity_ref` records uncertainty as not estimated. An unknown reference is unresolved, not a request to choose a bootstrap automatically. A known reference resolves a Step 2 `replay` object whose `method_id` is `longitudinal_trajectory_sensitivity_v1`, `plan_sha256` is the approved Phase 3 plan SHA-256, and acquired artifact digest matches its actual bytes.

That artifact contains the following exact versioned JSON plan, with no indices yet:

| Field | Required content |
|---|---|
| `schema_version`, `plan_version` | `0.1`. |
| `plan_id` | Explicit bounded ID. |
| `method` | `longitudinal_trajectory_sensitivity_v1`. |
| `request_ref`, `request_sha256` | Exact SHL request and its complete configuration fingerprint. |
| `unit` | `probe_panel` or `lineage_root`. |
| `trajectory_refs` | Explicit ordered unique trajectory references. Panel sensitivity names exactly the SHL request's one path; root sensitivity includes that path and every chosen additional path. |
| `panel_refs` | The SHL request's exact ordered fixed panel set. |
| `replicates`, `seed` | Actual integers 2000 and 20260919. |
| `registration_ref` | Existing `preregistration` record. |
| `dependence_ref` | Existing `independence_assessment` record. |

The surrounding replay object's `unit_refs` equals this plan's `trajectory_refs`. For panel sensitivity, the plan's panel list supplies the moving units; the replay object continues to identify their trajectory using the unchanged Step 2 schema.

The registration payload has an additional `extensions.longitudinal_sensitivity_v1` object containing `plan_sha256` (the configuration fingerprint of this plan) and `inspection_status: registered_before_inspection`. Its chronology and decisive evidence are checked.

The independence assessment uses the existing outcome `supported_for_scope` and dimension `conditional_sampling`. Its extension of the same name contains `plan_sha256`, `unit`, exact `unit_ids`, exact `dependency_groups`, actual Boolean `conditional_independence: true`, and nonempty `conditioning`. Missing assumptions, stale binding or unsupported outcome withhold the sensitivity interval. All dependencies retain their mock/material/access/correction status. Software fixtures are expressly `fixture_stipulated`.

For root sensitivity, one path per known stochastic dependency unit is required. Shared stochastic ancestors, reused observations/calls, ambiguous units and incompatible time grids are rejected. A shared fixed checkpoint alone does not establish shared stochastic ancestry. For panel sensitivity, the complete recurring panel moves across all measured times, and shared calls across nominal panels cannot create independent units. There must be at least two eligible units. The interval describes only supplied units under the recorded conditional model, with no all-models or all-prompts confidence guarantee.

### 12.6 Indices, full draw retention and replay

The component uses its own `random.Random(20260919)` instance, records MT19937, the `randrange` API, Python implementation/version and random-state version, and never changes global RNG state. It generates exactly 2000 rows of N integer indices for N selected units. The result includes the complete matrix, zero-based indexing, method, plan identity, consumed-input identity, unit order, seed, count, quantile rule, matrix digest and complete-manifest digest.

Each draw reconstructs the whole time curve by equally weighting its sampled units, then reruns the unchanged requested local/anchored estimator. Every draw retains its index row, exact curve, fit diagnostics, status and reasons. Zero, increasing, non-geometric, missing or numerically failed draws are not removed. If any required draw lacks a finite applicable half-life, the complete interval is unavailable. Failure counts and the point fit remain; no filtered-success interval is computed.

The percentile rule is linear interpolation at `(B-1)*q`, with q=0.025 and 0.975. Logarithmic fits remain numerical quantities; exact binary representations of their finite values are used for interpolation, not a claim of exact logarithmic arithmetic. Intervals are named `resampling_sensitivity`.

Saved full manifests can be supplied as already loaded passive objects:

```python
# Keep the original scientific bundle and plan unchanged.
replayed = evaluate_longitudinal_sensitivity(
    bundle,
    replays={"registered-fit-id": previously_saved_full_replay_manifest},
)
```

Explicit replay mode must supply every requested record. Missing, null, truncated, wrong-unit, wrong-context or corrupted manifests never trigger regeneration. Replay validates and uses the stored indices; it does not call the RNG or demand that the current Python patch version regenerate the same stream. Replacing plan/data/evidence in the scientific bundle changes consumed context and rejects a prior replay. `validate_replay` additionally accepts an externally retained expected manifest digest. Digests preserve identity and do not authenticate the truth or origin of supplied evidence. Loading a replay file and wiring it to the later CLI remains Step 8 work.

### 12.7 Limits, numerical treatment and current test scope

Existing loader limits apply to the already acquired plan artifact. Unit/state counts retain Phase 3 limits; complete recomputation work is checked against `max_tail_summands` using `2000 * N * measured_time_count` before sampling. Rational additions, products, divisions and inputs use the Step 4 exact-bit guard. Limits can be lowered but never silently raised, replaced by floating approximations or met by dropping units/draws.

Near-one diversity ratios use an exact rational difference before `log1p`. Extreme positive ratios use bounded integer logarithms when necessary. Underflow of a nonzero log difference, nonfinite slope, or unrepresentable positive fitted diversity is an explicit numerical failure; none becomes scientific zero or a plateau. All actual round indices are retained. Interval endpoints remain exact fractions even though the logarithmic rate is numerical.

`tests/fixtures/half_life_oracles.json` stores exact input curves, separately computed 95-digit Decimal expected slopes/timescales, deterministic index identity fixtures and independent small-percentile values. Record-driven tests also enter through genuine safe-loaded mock candidate/assignment/validity records and fixed budgets. These are software fixtures, never a model-training experiment or independent validation. P3-L17 through P3-L22 are the Step 5 software requirements. Section 13 adds Step 6 support assays. ERR, automatic P10 decisions, longitudinal CLI and public reports remain later steps.


## 13. Finite-family support assays (Step 6)

### 13.1 Scope and interpretation

The `finite_family_binomial_threshold_v1` method evaluates probability-threshold membership within a finite, explicitly registered intervention family and reference-class universe. SD section 5 and SI sections 3.3/8.1 supply the support distinctions. The fixed-design assay, exact tail procedure and simultaneous error allocation are engineering methods adopted in Phase 3 plan section 6 and Appendix C.

`observed_intervention_union_size` describes accepted classes actually observed under the tested interventions. A single accepted observation can enter this union without establishing generation probability at or above tau. Below-threshold probability can remain positive, and a below-threshold class may have been observed. Neither finite nonappearance nor a below-threshold decision establishes representational extinction, absorbing zero probability, latent support or the unrestricted model repertoire.

All support sets carry `finite_family_scope`, a versioned family identity, `class_universe_ref`, and `coverage_scope: registered_reference_classes`. An exact finite-family support count requires all registered reference-class statuses to be resolved under the registered method and supplied evidence. Otherwise the component retains known-present, known-below and unresolved/unavailable classes with integer set-size bounds. Empty-reference normalization is mathematically undefined. The inherited production registry still requires the supported eight-class frame. An empty declared reference universe cannot bypass that parser: its normalization is undefined and an invalid/missing registry does not receive a validated exact support count.

The component performs no model calls, generated-code execution, training, network activity, external evidence acquisition or independent substantive validation. Fixture declarations remain stipulated software material. Imported conclusions remain conditional on supplied qualified evidence. The public longitudinal CLI/report integration belongs to Step 8; ERR belongs to Step 7.

### 13.2 Fixed trial design and success events

Each eligible independent call contributes one candidate position selected before data inspection. Five candidates returned by one call cannot become five independent Bernoulli trials. The component retains the planned, attempted and completed inventory, exact attempt/sample references, selection position, fixed state and intervention identity.

The inherited wire token `class_membership` denotes structural membership regardless of separately recorded functional validity. The inherited wire token `valid_class_membership` denotes the joint event of membership and satisfaction of the registered validity rubric. This is the event called `valid_class_expression` in plan section 6.2. These two events have different identities and cannot be exchanged across stages.

The unconditional trial denominator includes completed non-successes and unresolved outcomes; it is never a valid-only or successfully-classified-only denominator. Definite refusal/no-output failures require completed original call evidence and a matching registered event. Unperformed scheduled calls, harness loss and missing call evidence prevent fixed-N eligibility. Uncertain classification or unreadable validation of an otherwise inventoried trial is retained as uncertainty where the positive event remains possible.

For each class and intervention the component retains `k_confirmed` and `k_possible`, with `0 <= k_confirmed <= k_possible <= N`. An unresolved event can increase the latter without supplying an invented hard class or a false negative. Optional stopping, adaptive targeting, changing state, reused continuations and unresolved within-cell dependence withhold the built-in probability interpretation. Descriptive observations remain separately reviewable.

### 13.3 Exact decisions and complete multiplicity

The preregistered episode fixes every relevant `(stage, class, intervention)` cell. Its size is J, including planned cells whose later evidence is missing. The component uses the actual explicitly materialized alpha and the exact allocation `delta = alpha / (2 * J)`. Alpha must lie strictly between zero and one; tau is required in `(0, 1]`. Tau has no default and is distinct from an empirical-frequency threshold.

For `B ~ Binomial(N, tau)`, the positive decision uses `P(B >= k_confirmed) <= delta`; the negative decision uses `P(B <= k_possible) < delta`. Rational comparison preserves this intentional equality asymmetry. At `N=4`, `tau=1/2`, `delta=1/16`, four confirmed successes establish the positive decision, while zero possible successes do not establish a below-threshold decision at equality.

A class is `threshold_present` when any eligible registered intervention establishes presence. It is `threshold_below` only when every registered intervention establishes below-threshold status. Missing or ineligible family members cannot be deleted to support a negative conclusion. Unresolved and unavailable decisions retain their reasons. The simultaneous elementary error bound is conditional on the within-cell trial assumptions; the union bound does not require independent tests across classes or cells.

Exact N, success bounds, tau, alpha, J, delta and both tails accompany decisions. At `tau=1`, even all finite successes generally cannot establish probability exactly one under this method. This limitation remains visible.

### 13.4 Resource and snapshot boundaries

The existing safe loader owns all record/artifact acquisition. Component processing uses acquired snapshots and performs no fresh file access. A supplied longitudinal review must belong to the same current input fingerprint. Changing a selected position, sample, state, label, validity record, evidence dependency, registration, threshold or input bytes invalidates prior context.

The approved defaults permit at most 16 interventions per assay, 2,048 trials per exact binomial cell, 2,000,000 elementary exact tail summands over the request and 262,144 bits per constructed exact numerator/denominator. Existing token, exponent, record, depth and link limits continue to apply. Inputs may lower limits. Preflight checks occur before expensive powers or tail sums; a resource failure returns scoped unavailability. It does not select a smaller N, increase alpha, use a normal approximation or change the family.


### 13.5 Component API and retained records

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.support_assays import evaluate_support_assays, assert_current

bundle = load_bundle("path/to/bundle.json")
study = evaluate_support_assays(bundle)
assert_current(study, bundle)
for assay in study.assays:
    print(assay.ref, assay.present_classes, assay.below_classes, assay.size_bounds)
    print(assay.observed_intervention_union_size)
    print(assay.expressible_support_size_finite_family)
```

`SupportAssayStudy` retains the source `LongitudinalReview`, consumed context digest, effective limits, episode J, total actual tail work, typed assay results, status and reasons. Each `AssayResult` retains its state, family/version, original and semantic success-event names, registry reference, class/member inventories, all class/member cells and trial outcomes, class statuses, observed union, conditional support size, normalization and set-size bounds. `substantive_validation_performed`, `latent_support_established` and `model_recovery_established` remain false.

Each `AssayCell` retains a `CellDecision`, planned/attempted/completed/missing counts, the complete trial ledger and eligibility reasons. The decision holds exact `Fraction` operands and tails. Each trial retains the original references, candidate position, confirmed/uncertain outcome and reasons. These objects are internal audit components, with public redaction/serialization deferred to Step 8.

The separately callable arithmetic function is:

```python
from fractions import Fraction
from structdet_bench.support_assays import binomial_threshold

value = binomial_threshold(4, 4, 4,
    tau=Fraction(1, 2), alpha=Fraction(1, 8), J=1)
assert value.status == "threshold_present"
assert value.upper_tail == value.delta == Fraction(1, 16)
```

This helper accepts supplied success bounds and performs conditional arithmetic. It does not establish trial eligibility, registration, class validity or independence. Use `evaluate_support_assays` for the record-bound component.

### 13.6 Preregistration and evidence witnesses

The existing global `registered_design_ref` resolves a qualified `preregistration` record. Its payload extension `support_assay_registration_v1` contains exactly `method`, `inspection_status`, and `stages`. Method is `finite_family_binomial_threshold_v1`, and inspection status is `registered_before_inspection`. Every stage includes `assay_ref`, `design_sha256`, `context_sha256`, ordered `classes`, complete `intervention_refs`, and complete planned `trials`. Every slot includes exactly `trial_id`, `intervention_ref`, `measurement_ref`, `attempt_ref`, and the positive integer `candidate_position`.

The stage inventory remains complete across the requested episode, including missing later stages. Planned N is the number of registered slots per intervention; it does not shrink to the acquired sample count. The registry's class order and identity are checked. The static design digest separates the fixed assay design from subsequently observed status/sample fields. The separate context digest binds the fixed state, intervention and measurement design to the actual core frame, protocol, cell and reference-registry contents and verified conditioning-artifact bytes, excluding subsequent trial outcomes. The preferred `registration_witness(assays, classes, trial_slots, bundle=loaded_bundle)` form prepares these binding fields from an acquired bundle for an external registration workflow; calling it does not create, timestamp or validate a registration.

The existing assay `iid_evidence_ref` supplies a qualified `independence_assessment` or an `evidence` record for independence. Its `support_assay_iid_v1` extension binds the exact `assay_ref` and `design_sha256`, and records actual Boolean assertions for `independent_calls`, `fixed_state`, `fixed_intervention`, `no_adaptive_stopping`, `no_reused_continuations`, and `complete_trial_inventory`. The assessment outcome/purpose must support the stated scope. `iid_witness(assay)` constructs the expected binding shape only; its Boolean values have no independent evidentiary authority.

Qualified supporting records use the existing evidence access, role, version, fixture, conflict, correction and decisive-dependency policies. The assay additionally checks declared `artifact_refs` and `material_refs` against actual acquired snapshot content, size and digest; a retained status label alone does not prove readable material. Missing/contradictory supporting evidence withholds probability claims. Registration chronology is checked against declared state times and any recorded call times. Complete record-shaped claims remain conditional evidence, and mock children retain their fixture limitations.

Determinate refusal/no-output failures additionally require an acquired original call response and a qualified validation evidence record with `support_assay_failure_v1`. Its bound fields are `assay_ref`, `trial_id`, `attempt_ref`, `success_event`, and actual Boolean `determinate_nonexpression: true`. A bare trial status or unsupported prose cannot establish a negative event. Accepted positive expression cannot be overwritten by a conflicting nonexpression declaration. Ordinary completed outputs with unresolved classification remain possible successes even when such a declaration is supplied; qualifying nonexpression is restricted to recorded refusal or a documented completed no-output call.
