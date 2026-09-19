# Longitudinal record format

## Phase 3 Step 2: versioned declarations and lineage binding

| Field | Value |
|---|---|
| Format document | 0.1 |
| Profile | `structdet_longitudinal_v1` |
| Extension version | `0.1` |
| Component method | `longitudinal_records_v1` |
| Governing approval | `PHASE_3_PLAN.md`, especially sections 3, 8, 9 and Step 2 |
| Implementation scope | Passive record shape, identity and relationship checks |
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
