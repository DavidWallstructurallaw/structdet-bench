# Input and Evidence Format

Version: 0.5. Input schema: `0.1`. Record envelope: `0.1`. Evidence payload: `0.1`.

This document describes the current passive input, evidence, inventory, metric and
report interfaces through Phase 2 Step 6. Read it with `PHASE_1_PLAN.md`, the frozen
Phase 0 contracts, and `EVALUATION_CLOSURE_ADDENDUM.md`. Those contracts retain their
approved bytes. Physical support extensions below encode already approved
requirements; they do not certify an imported assertion or add a new estimator.

The loader reads and checks records. The separate evidence pass decides record-
qualified admission. Inventory and metric components operate on the accepted
scope. `validate` and `analyze` are available through the CLI; Section 12 describes
the report path. Section 13 documents the Step 7 integrated record checks.

## 1. Interface and limits

The Python API is available from `structdet_bench.local_io`:

```python
from structdet_bench.local_io import ReadLimits, load_bundle

bundle = load_bundle("local-study/bundle.json", limits=ReadLimits())
for diagnostic in bundle.diagnostics:
    print(diagnostic.code, diagnostic.scope)
```

`load_bundle` returns a `LoadedBundle` containing the parsed manifest, immutable
record entries, byte snapshots, artifact inspections, scoped diagnostics, effective
limits, and read-byte accounting. `has_errors` is an input diagnostic summary.
`acquisition_complete` records whether acquisition/parsing was completed within
limits. Neither property establishes scientific validity or analysis readiness.
A shape-valid record may have unresolved references, unknown metadata or unsupported
assertions. Evidence admission belongs to Step 3.

`python -m structdet_bench` provides help, version, `validate` and `analyze`.
The input loader remains passive; exposing a CLI does not authorize execution of
candidate programs or automatic retrieval of external evidence.

| Bound | Default |
|---|---|
| One file | 16 MiB |
| Aggregate bytes actually read | 64 MiB |
| One JSONL line, including its terminator when present | 1 MiB |
| Total records including embedded declarations | 100,000 |
| JSON nesting depth | 64 |
| One number token | 1,024 characters |

Use a `ReadLimits` value to specify overrides before loading. Its values are
returned in the result. Depth above 128 and numeric token limits above 4,096 are
rejected explicitly. Limits cannot be zero, negative or boolean. No exceeded
limit authorizes sampling or silent truncation. Previously acquired records and
snapshots remain available with the failure and actual scope disclosed.

The secure reader requires POSIX descriptor-relative, no-follow file operations.
When unavailable, it reports `safe_local_open_unavailable` without falling back
to a weaker reader. This delivery is tested on its recorded Linux environment;
Windows compatibility and an OS-level security sandbox are not claimed.

## 2. Bundle manifest

The manifest is a strict UTF-8 JSON object. Its parent directory is the bundle
root. It explicitly lists record files; there is no directory crawl or discovery.

| Required field | Meaning |
|---|---|
| `input_schema_version` | Exactly `"0.1"`. |
| `bundle_id`, `study_id` | Stable identifiers, with no inferred approval or provenance. |
| `data_role` | `fixture`, `pilot`, `confirmatory`, or `descriptive`. A declaration does not prove that role's scientific prerequisites. |
| `frames` | Array of frame records with the task, horizon, resolution and schema. |
| `protocols` | Array of generation-protocol records. |
| `cells` | Array associating frame, protocol, prompt block, condition and model metadata. |
| `analysis_config` | Evidence-policy identity, intended order/selection and revision pins; recorded without executing the future analysis. |
| `record_files` | Explicit file-role declarations. |

Optional fields are `extensions` (an object) and `source_pins` (an array of
`{"source_id": "EC", "sha256": "..."}` objects). Duplicate source IDs fail.
Supplied source pins are compared with the SD/SI/EC identities from the approved
source manifest. Omitted pins remain omitted. The loader never downloads a PDF.

A file declaration has exactly four fields:

```json
{
  "role": "observations",
  "format": "jsonl",
  "path": "records.jsonl",
  "expected_sha256": {"state": "unknown", "evidence_refs": []}
}
```

| Role | Format | Permitted records |
|---|---|---|
| `observations` | `jsonl` | Attempts, realizations, assignments, validity, artifacts and raw artifacts. |
| `evidence` | `jsonl` | The supporting envelopes in Section 6 and artifact records. |
| `registry` | `json` | One reference-registry object. |

Paths must be relative local paths. Repeated file declarations, a manifest listed
as its own record file, wrong roles and unsupported formats are diagnosed.
The manifest may be named something other than `bundle.json`.

## 3. Identities, values and references

Every record has `record_type`, `record_id`, and `record_version`. Version must
be `"0.1"`. IDs match `[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}`. Each core record's
specialized ID must equal `record_id`; examples include `sample_id`,
`assignment_id` and `artifact_id`. Record revisions are distinct from envelope
version. Revision choices are explicit, never an automatic latest-version rule.

A reference has exactly these fields:

```json
{"record_type": "artifact", "record_id": "output-1", "record_version": "0.1"}
```

The metadata wrapper is:

```json
{"state": "known", "value": 0, "evidence_refs": []}
```

| State | Rule |
|---|---|
| `known` | `value` must be present. Explicit `0`, `false`, empty values and `null` remain distinguishable from unknown, subject to the field's type rules. |
| `unknown` | A non-null value is forbidden. A reason may be supplied. |
| `unavailable` | A nonblank reason is required; a non-null value is forbidden. |
| `not_applicable` | A nonblank reason is required; a non-null value is forbidden. |

Optional `evidence_refs` contains typed references. A `known` assertion is an
assertion present in input, not independent verification of its contents.
Knowledge, assignment, review, validity, result and claim status are different axes.
Unknown generation controls, checkpoints, ordering, evidence, or parentage are
never completed with guessed defaults.

## 4. Core records

All rows also require the common envelope above. Optional extensions must be an
object. Undeclared core fields fail instead of being interpreted as executable
transforms. See `records.py`'s fixed `REQUIRED` and `OPTIONAL` inventories for the
exact validator-level field lists.

| Type | Required payload fields |
|---|---|
| `frame` | `frame_id`, task identity/version, `task_context`, `consequence_horizon`, resolution identity/version, structural-schema identity/version, reference-registry identity/version, `validity_rubric_ref`, `load_bearing_invariants`, `consequence_signature_spec`, `equivalence_rule_ref`, `admissible_substitutions`, `evidence_requirement`, `exceptional_case_rules`, tagged `registration_ref`. |
| `protocol` | `generation_protocol_id`, `generation_protocol_version`, tagged `conditioning_context_ref`, `decoding_settings`, `seed`. |
| `cell` | `analysis_cell_id`, `frame_id`, protocol identity/version, `prompt_block_id`, `prompt_id`, `condition_id`, tagged `model_identifier`, `model_family`, `checkpoint_identifier`, `collection_window`. |
| `attempt` | `attempt_id`, `analysis_cell_id`, `attempt_status`, tagged `raw_response_ref`, `retry_of`, `generation_group_id`, `planned_candidate_count`, `registered_call_order`. |
| `realization` | `sample_id`, `analysis_cell_id`, tagged `attempt_id`, `raw_response_ref`, `output_ref`, `output_content_hash`, `generation_group_id`, `within_group_index`, `sample_order`, `extraction_rule_version`; `completion_status`. |
| `assignment` | `assignment_id`, `assignment_version`, `sample_id`, `frame_id`, `assignment_status`, `structural_class_id`, `assignment_review_status`, tagged `assignment_method`, `decision_rationale`, `supersedes_assignment_id`; `evidence_refs`, policy identity/version. |
| `validity` | `validity_id`, `validity_version`, `sample_id`, `validity_status`, `validity_review_status`, tagged `validity_rubric_ref`, `decision_rationale`, `supersedes_validity_id`; `evidence_refs`. |
| `artifact`, `raw_artifact` | `artifact_id`, tagged `content_ref`, `expected_sha256`, `knowledge_type`. |
| `reference_registry` | Registry identity/version, `frame`, eight class descriptors, tagged `validation_status`, `provenance`, `source_fragments`. |

The first supported frame uses the exact identities declared by HERO: task
`bounded_integer_sort`, resolution `sorting_mechanism_family`, schema
`sorting_mechanism_partition`, registry `sorting_reference_eight`, all version
`0.1`, and rubric `bounded_integer_sort_validity_v1`. Its contextual statements
must still be supplied. Matching these names does not independently validate
those statements or the mechanism map.

`examples/sorting_reference_eight.json` is a literal, source-hash-linked
transcription of the approved eight descriptors and selected scope paragraphs.
Its validation status is `not_performed`. Its eight entries are reference
categories, not eight generated observations or eight validated programs.

Assignment states are `assigned`, `unresolved`, and `unclassified`. An assigned
record needs a class ID. The other two states require `structural_class_id: null`;
candidate IDs can remain in `candidate_class_ids` without adding structural mass.
Review states are `fixture`, `provisional`, and `adjudicated`. A string saying
adjudicated does not admit the record into an accepted population at this step.

Validity states are `valid`, `invalid`, `undetermined`, and `not_assessed`.
An invalid program can have an asserted recognizable class; its actual admission
will be decided by the next evidence layer. The input reader does not execute it.

Attempt states are `succeeded`, `failed`, `cancelled`, `not_attempted`, and `unknown`.
Completion states are `complete`, `truncated`, `refused`, `failed`, and `unknown`. A failed five-candidate call is never converted into five invented
realizations. This step preserves supplied associations, not extraction or repairs.

## 5. Configuration and exact thresholds

`analysis_config` requires:

- `analysis_config_id`;
- `assignment_evidence_policy_id`: `fixture_only` or `adjudicated_import`;
- `assignment_evidence_policy_version`: `"0.1"`;
- `requested_k`: distinct positive integers, never booleans;
- `selection`: one record per selected cell, with `analysis_cell_id` and tagged
  `selected_sample_ids`, `sample_order`, `registered_positions`, `selection_basis`;
- `assignment_pins` and `validity_pins`: arrays of sample/revision selections.

Optional `empirical_threshold` and `extensions` are also supported. `known`
control metadata does not supply control-enforcement evidence.

A pin has `sample_id`, `assignment_id`, `assignment_version`, or the corresponding
validity ID/version fields. Duplicate or contradictory selections are diagnosed;
all supplied record revisions remain retained. Storage order is not a substitute
for scientific sample order.

Optional `empirical_threshold` accepts an exact finite JSON number or decimal
string in `(0, 1]`, for example `0.10` or `"0.10"`. Decimal and exponent tokens
are preserved as `ExactNumber`/`ThresholdToken` values; they are not converted
through binary floating point. String whitespace, fractions such as `"1/2"`,
NaN, infinity, zero, values above one and booleans are rejected. This step stores
and validates the requested threshold; it does not calculate thresholded support.

## 6. Supporting evidence and EC-001

The supporting types are `evidence`, `role`, `lineage`, `independence_assessment`,
`annotation`, `adjudication`, `domain_suite`, `domain_result`, `audit`, `exposure`,
`integrity_assessment`, `intake`, `tail`, `correction`, `preregistration`, `budget`,
`sampling_plan`, and `source`.

They use an envelope with the three identity fields, `payload` as an object and
optional `extensions`. They have `validation_level="envelope_only"`. Their
contents are retained without natural-language judgment, arbitrary code execution,
a universal lineage DAG assumption, or promotion into empirical evidence.

EC-001's five conditions, source/role relationships, unknown expiry, original
anomalies and distributional/structural reopening records can be carried in these
payloads. Their transport does not certify independence, openness, structural
validity, actual correction, or model recovery. Receipt of a record is separate
from evidence admission and the later report/claim checks.

## 7. Byte acquisition and diagnostics

A known local artifact locator is `{"kind":"local","path":"output.txt"}`.
A known external locator is `{"kind":"external","locator":"https://..."}`.
Both appear inside `content_ref`'s tagged value. External references are never
fetched. Unknown, unavailable and non-applicable material remain explicitly so.
An expected hash is a tagged lowercase, 64-character SHA-256 string.

Local reads use a held root directory descriptor and no-follow descriptor-relative
operations. All symlink components, including the root ancestry, are rejected.
Traversal, drive/remote schemes, environment expansion, device/pipe/directory
inputs, control characters, and ambiguous relative paths are rejected. A regular
file's identity/size/modification observations are checked across reading.
Analyzed bytes receive their own SHA-256 snapshot. Subsequent references to the
same path within the load use that immutable snapshot, not newly read bytes.

Raw artifact bytes may be binary. JSON and JSONL must be valid UTF-8 without a BOM,
unpaired Unicode surrogate, duplicate object key, nonfinite constant or trailing
JSON document. Escaped duplicate key spellings are duplicates. Finite exponent
numbers outside a binary float's range remain exact finite values. A JSONL blank
line is a malformed record; an empty file contains zero records.

Diagnostics identify `bundle`, `file`, `record`, `identity`, `frame`, `cell`,
`sample`, `assignment`, `validity`, `artifact`, `source` or `analysis_config`
scope as applicable. Examples include `duplicate_json_key`,
`unsupported_input_schema_version`, `duplicate_record_identity`,
`ambiguous_reference`, `source_pin_mismatch`, `content_hash_mismatch`,
`record_count_exceeded`, and `safe_local_open_unavailable`.

An invalid row stays attached to its source and line, with original bytes retained
in the acquired file snapshot. Later valid rows may remain readable. A malformed
file cannot be reported as a valid empty data set. Expected and observed hashes
remain separate on mismatch; the expected value is not rewritten to make it pass.
These diagnostics are input facts, not Step 3 evidence dispositions or metric
availability decisions. Private bytes and asserted identities remain sensitive;
inspect and redact them before external sharing. A safe diagnostic representation
does not replace the later report privacy contract.

## 8. Test catalogue representation

`tests/phase1_matrix.json` keeps all 54 VT, 40 TR and 36 RF identities, scope
statuses and actual method bindings. Its `pinned_source_rows_v1` convention links
long catalogue prose and its derived links to the exact local frozen VF/TRACE/Phase 1 plan rows. The helper explicitly supplies documentary scope-reason and empty fixture-reference defaults; required test bindings remain in the matrix. The trusted
`tests.helpers.load_matrix` checks source hashes and expands those rows. It never
fetches content, changes a test disposition or evaluates a supplied expression.
The legacy fully expanded representation is still readable. Direct JSON readers
can inspect scope/binding records; use the helper for full source-row prose.

The source-reference representation is checked against the frozen source tables
for exact catalogue text and link preservation. It does not remove requirements
or weaken the full Phase 1 gate. Step 2's foundational coverage is recorded as
partial for whole M families. All empirical-evidence scopes remain unperformed.


## 10. Step 3 evidence-record review

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.evidence import review_evidence

bundle = load_bundle("local-study/bundle.json")
review = review_evidence(bundle)
for result in review.admissions:
    print(result.sample_id, result.axis, result.status, result.reasons)
```

This API consumes the immutable loaded snapshot. It performs no I/O, subprocess,
model call, metric computation, population selection, or code execution. Original
entries and bytes remain unchanged. It returns per-sample assignment/validity
admissions, support-record checks, restricted claim checks, and correction
relationships for later consumers. Analysis populations belong to Step 4.

### Typed support payloads

The input loader still marks these records `envelope_only`. `inspect_support`
in `evidence.py` is the explicit second pass. Its `SUPPORT_COMMON`,
`SUPPORT_FIELDS`, and `SUPPORT_ENUMS` define every supported field and type.
Incomplete envelopes are preserved but cannot become decisive evidence merely
because they have a record ID.

Every support payload requires `payload_version: "0.1"`, `data_role`, `mock`,
`state`, `scope_refs`, tagged `origin`, tagged `knowledge_type`,
`transformation_refs`, and `evidence_refs`. Unknown top-level payload fields fail;
extra passive material can be retained in `extensions`. All 18 Step 2 supporting
record types have typed payload schemas. The shared record reference has exactly
`record_type`, `record_id`, and `record_version`. Required unknown metadata uses
explicit tagged states; no default supplies an absent fact.

Evidence records additionally supply target, property, assertion, method, detail,
artifact and reviewer references, subject hash, access and conflict state.
Adjudication records supply target, concluded decision, outcome, reviewer, bases
and disagreement references. Their exact fields are listed in the executable
schemas and exercised by mock examples in `tests/fixtures/integrity_cases.json`
and the named tests. Payload-shape success is not substantive verification.

### Admission and separate validity

Both assessment axes require one exact selected revision pin. Missing pins give
`missing`, duplicate pins give `conflict`, and missing/mismatching selected
revisions give `withheld`. The module never chooses a newer label automatically.
Historical revisions remain retained. A superseded selected revision is withheld;
a later analysis must explicitly pin its replacement. Historical replay uses its
original bundle and evidence state.

`fixture_only` requires a fixture context and fixture review, plus an active,
readable `fixture_declaration` matching the assessment, frame and stipulated
outcome. Missing its declaration withholds that assessment only.

`adjudicated_import` requires the appropriate review state, matching mechanism or
validity evidence, and a resolved adjudication with reviewer and supporting
records. Provisional decisions, unresolved contradictions and essential missing
records cannot be promoted. Mock or fixture decisive evidence cannot validate an
empirical import. Tests may contain synthetic imported-shaped fields, always
inside a visibly fixture-based test context. They supply no real human evidence.

Mechanism method labels allowed by this contract are `control_flow`,
`execution_trace`, `formal_mechanism`, `counterfactual`, and
`domain_adjudication`. Validity methods are `execution`, `formal_validity`, and
`domain_adjudication`. Execution and trace assertions require matching imported
domain records and a performed, active suite with subject, tested property,
environment, input manifest and observations. Timeout/harness failures cannot
establish validity or invalidity. The software checks the records and their
relations; it does not perform or independently certify those observations.

A correct sorted result, algorithm name, embedding score, or model self-report
alone does not establish mechanism membership. Missing independent lineage can
restrict a stronger claim while preserving separately supported membership.
Missing output text alone does not erase independently supplied mechanism
records, but an essential unreadable artifact or mismatching subject hash blocks
its dependent assessment. Invalid, undetermined, not assessed, and absent
validity remain distinct from the structural assignment.

### Independence, scope and corrections

Core annotation records retain actual declared person identities, first-pass
labels, qualification/exposure records, target, rubric and set. Two sessions by
one person cannot satisfy a two-person requirement. Earlier exposure is retained;
later discussion does not rewrite an independent initial pass. Agreement itself
is not a truth test, and disagreements remain recorded. Every returned check
states that substantive validation was not performed by this module.

Audit records preserve planned positions, actual reviews, missing planned items,
extra targeted reviews and their annotation links. Additional review never adds a
model sample. The 32-program core, 28 planned contrasts and 8,995 functional check
inputs remain designs until actual corresponding evidence is supplied.

An operational-openness claim needs all five EC-001 conditions with scoped
support. Missing evidence or a mandatory condition marked not_applicable cannot
be averaged into success. Declared reviewer dispositions are separate from this
software's restricted record checks. Unknown expiry remains unknown; no default
lifetime or deployment-validity assertion is added. Source, lineage, tail and
intake records preserve supplied origin, unknown ancestry, raw references and
review states without inferring a new class or hidden independence.

Correction targets are exact record references. Membership withdrawal affects
its dependent assignment; validity withdrawal affects its dependent validity;
independence-only withdrawal restricts the relevant claim without erasing
separately supported membership. A shared structural-schema challenge affects
classifications across that frame while separately supported validity under an
unchanged rubric remains distinct. A missing/invalid shared frame prevents the
corresponding checks. Applied, pending and rejected corrections remain separate.
Impact records link affected assessments; no metrics are recalculated here.

Evidence-support cycles and revision cycles are checked at their actual edges.
Historical lineage/review relationships are not forced into a universal DAG.
A reclassified sample keeps its identity and never becomes an extra observation.

### Delivery and QA provenance

The previous Step 2 ZIP was incomplete because its packaging stopped at a file
permission failure. This complete working tree was restored from the intact
Step 1 archive, verified Step 2 runtime blobs, EC-001 and retained test sources.
The three Step 2 runtime modules and I/O/security tests match the earlier
execution fingerprints. The helper/catalogue representation, selected test
metadata and registry transcription were reconstructed and freshly tested;
they are not represented as byte-identical to every earlier uncommitted object.
All 12 frozen scientific/plan documents retain their approved fingerprints.

The matrix's `catalogue_row` values resolve prose and links from the pinned
scientific tables only after their hashes pass. Incorrect row IDs and changed
source files fail. Scope dispositions and actual test bindings stay explicit.
Whole M families remain partial while downstream populations/metrics/report
requirements are unfinished. E evidence is never supplied by fixture tests.

GitHub retains concise run summaries and companion-archive fingerprints in the
two QA capture files. The delivery ZIP retains the complete original Step 1,
Step 2 and current Step 3 journals and console captures in `verification/`.
A summary is explicitly labeled and never presented as the full journal.
Run identities, commands, outcomes and original-byte fingerprints are preserved.
The unchanged QA runner can append ordinary full runs to the summarized journal.
These QA files are not benchmark inputs. That delivery authorization covered Step 3 and the outstanding repository
synchronization. The later Step 4 instruction and its scope are recorded below.


## 11. Step 4 inventories, populations, and fixed prefixes

The owner's instruction `可以，Phase 1 Step 4  开始` accepts the Step 3 handoff
and authorizes this layer plus its GitHub publication. The governing reference is
`PHASE_1_PLAN.md` Section 6, Step 4; MET Sections 4, 6, 7 and MF-07/MF-10;
HERO Sections 7, 8, 11; and the VF accounting oracles. Frozen contracts and
EC-001 are unchanged. The first working inventory is an operation on imported
records, with no new observations, automatic extraction, scoring of natural
language evidence, comparison, or empirical validation.

### 11.1 Public Python interface

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.inventory import build_inventory
from structdet_bench.populations import build_populations, prefix, accumulation

bundle = load_bundle("local-study/bundle.json")
inventory = build_inventory(bundle)
analysis = build_populations(bundle)
for cell in analysis.cells:
    all_view = cell.populations["classified_all"]
    valid_view = cell.populations["classified_valid"]
    print(cell.inventory.cell_id, all_view.status, all_view.count)
    print(cell.ratios["classification_coverage"])
    descriptive = prefix(cell, 5, "classified_all")
    intended = prefix(cell, 5, "classified_all", mode="hero")
    table = accumulation(cell, [5, 10, 20])
```

These operations perform no new file reads. Results are immutable snapshots with
identities, reasons and references; the original loaded bundle remains unchanged.
The command-line interface still exposes only help/version until Step 6.
The separate `Ratio.value` property yields an exact `fractions.Fraction` or `None`;
its unreduced numerator and denominator remain in the record. JSON/Markdown
serialization is a later capability, so passing these dataclasses directly to a
generic JSON serializer is not the report interface.

### 11.2 Inventories and explicit selection

`Inventory` retains physical input-row counts, malformed rows, typed-record
counts, unallocated realization locations, duplicate identities, shared group
IDs across cells, input diagnostics, and acquisition completeness. A physical
row count never becomes a count of generated samples. Each cell retains the
received declaration and separates the following:

| Object | Meaning |
|---|---|
| `identified_sample_ids` | Unambiguous, shape-valid realization identities allocated to this cell, independent of labels/quality. Canonical ID order here is for set representation only. |
| `realization_count` | Complete identifiable inventory count, or unavailable when malformed/ambiguous observation records prevent that claim. Identified IDs remain visible. |
| `requested_sample_ids` | The explicitly supplied selection list, before any class or validity decision. |
| `selected_sample_ids`, `selected_count` | The resolved selection set, with unavailable count/reasons when its declared identity is ambiguous. A resolvable partial list cannot silently become a completed requested selection. |
| `excluded_sample_ids` | Identified received realizations outside the explicit selection list. Their original metadata and exclusion rationale remain in the bundle; selection basis accompanies the cell. |
| `recorded_attempt_ids`, status counts, retry links | Recorded attempted/not-attempted/cancelled/unknown entries. Missing histories remain unknown. |
| `recorded_invocations` | Count only of recorded `succeeded` and `failed` invocations. It is not an estimated total including unseen attempts or ambiguous cancellations. |
| Planned positions and groups | Expected candidate positions, their observed member IDs, missing/ambiguous state, and scoped completeness reasons. |

The selection entry's `selected_sample_ids` must be a known, unique list to
establish U. A known empty list establishes a selected count of zero. An unknown
list does not select every received row. `selection_basis` must identify the
selection rule; this explanation alone does not prove preregistration. Config
errors and a missing requested identity make affected selection unavailable.
Independently resolved selections in other cells remain usable.

Copies with one duplicated ID remain ambiguous, even if one copied row is
malformed. Distinct recorded observations may contain identical bytes. Two IDs
claiming the same attempt/position, group/position, or verified raw byte region
cannot supply two genuine selected observations without resolving the conflict.
A label revision supplies no additional realization. Extras stay in the received
inventory and cannot extend the planned budget. An explicit attempt to select a
known unrequested position is diagnosed rather than silently edited.

`realization_count` can be unavailable while a smaller explicitly named selection
remains fully identifiable. Conversely, a valid inventory does not establish an
unknown selection. Record-file identity failures retain their affected source
scope. A malformed observation of unknown ownership prevents complete inventory
claims; a missing unrelated evidence artifact does not invent lost observations.

### 11.3 Order, groups, and planned slots

Selection-list membership is separate from experimental order. A known
`sample_order` list names the complete selected sequence. Alternatively, complete,
unique positive `sample_order` values on realizations establish their ordering.
Conflicting supplied order sources are unavailable; neither filename order nor
lexicographic ID order resolves them. Missing order leaves supported whole-cell
populations and ratios available while preventing prefix claims.

`registered_positions`, when known, is an array of these objects:

```json
{
  "generation_group_id": "G1",
  "registered_call_order": 1,
  "within_group_index": 1,
  "attempt_id": {"state": "known", "value": "call1", "evidence_refs": []}
}
```

Call/position indices are positive integers, never booleans. Each group has one
call order and one declared primary attempt identity or explicit unknown.
Positions are contiguous from 1 within each registered group. A known null
attempt records no linked actual invocation; it creates no observation. The
plan is capped by the bundle's existing record limit before expansion.

When no position array is supplied, explicitly recorded primary attempts can
supply planned positions through `planned_candidate_count`,
`registered_call_order`, and `generation_group_id`. An explicit `retry_of: null`
identifies a primary attempt; unknown retry status cannot be assumed primary.
Retries retain links and resource history without adding a replacement planned
slot. Row count alone cannot supply a plan. A missing linked attempt restricts
its group rather than invalidating intact earlier groups.

Groups retain all known received members, attempt IDs, planned size, order and
completeness reasons. A failed five-candidate call may have five missing planned
positions and zero realizations. `recorded_invocations`, group count and sample
count remain different units. Shared group IDs across cells remain visible as a
possible cross-cell dependency, with no automatic pooling or independence claim.

### 11.4 Artifact association

Every realization retains its exact supplied attempt ID, raw-response reference,
output reference/hash, extraction version and group position. Known disagreement
between sample and attempt cell/group/raw-response identity is diagnosed. No
nearest neighbor, different candidate, repaired code or replacement call is used.

For imported exact-region evidence, `realization.extensions.extraction_span`
optionally contains `byte_start` and `byte_end`. They are zero-based byte offsets
with an exclusive end, relative to the referenced raw-response snapshot. The
inventory pass compares that region with the referenced output snapshot when
both are available and readable. It neither strips text nor extracts/replaces a
new candidate. UTF-8 multibyte characters, whitespace and line endings are
preserved. Empty emitted regions and truncated but identified artifacts remain
distinct from a never-emitted position.

`span_status` is `not_supplied`, `bytes_match`, `unavailable`, or `mismatch`.
`bytes_match` establishes only the recorded byte association. Unknown/inaccessible
text remains explicit. A known association contradiction withholds the affected
sample's dependent judgments without deleting its inventory entry; an unperformed
optional byte check does not by itself reject independently sufficient imported
membership evidence. This layer supplies no semantic classification.

### 11.5 Population and coverage outputs

The supplied Step 3 evidence policy is applied to the selected U. Both views keep
zero-count entries for all eight pinned classes and exact unweighted counts.
`classified_all` contains accepted hard assignments. `classified_valid` contains
those assignments whose separately accepted validity assessment is `valid`.
Unknown, unclassified, provisional or disputed labels add no class mass.

| Ratio | Authoritative numerator / denominator |
|---|---|
| `classification_coverage` | Accepted hard assignments / selected realizations. |
| `valid_fraction_selected` | Selected realizations established valid / selected realizations. |
| `decisive_validity_coverage` | Selected realizations established valid or invalid / selected realizations. |
| `classified_valid_coverage` | Classified-valid / selected realizations established valid. |
| `classified_valid_fraction` | Classified-valid / classified-all. |

A known zero denominator produces `undefined` and a null value; missing selection
or a shared-frame defect produces `unavailable` at the affected scope. Frame
failure cannot be reported as a legitimate zero-class distribution. A local
missing class declaration with an otherwise valid frame reduces accepted class
coverage without changing U or implying output invalidity. An independence-only
withdrawal restricts claims while preserving separately supported labels.

Assignment status, review state, acceptance, validity and completion have separate
counts. Missing assessments are not automatically invalid or not-assessed.
Withholding reasons may overlap and are marked multi-reason. Each valid accounting
axis reconciles to the selected count independently; adding different axes would
double-count records. Where a requested selection is unresolved, recorded subset
counts are partial inventories and cannot be reported as complete-U rates.

### 11.6 Descriptive and HERO prefix modes

`prefix` implements `prespecified_prefix_without_replacement`. For positive k,
it first takes the first k selected realizations in established order, then
intersects that prefix with the chosen accepted view. It returns IDs, class
counts, counted-sample count, exact distinct-class count, excluded judgments,
group membership, partial-group flags, and reasons. It never takes the first k
valid or classified successes. A descriptive prefix may cut a coordinated group,
with that limitation visible. k remains a realization budget, not a call budget.

An existing k-prefix with no accepted classes returns available class count zero.
Fewer than k actual selected realizations gives unavailable, with no shrink-to-fit.
An omitted k is not-requested; boolean/nonpositive/noninteger k is rejected.
`accumulation` preserves a supplied strictly increasing k grid and both views;
it cannot choose a favorable new grid or perform extrapolation.

`mode="hero"` adds the adopted four-group, five-position rule. Only k=5,10,20 are
HERO endpoints. The intended first 1,2,4 groups, respectively, must have their
complete unambiguous actual positions and agree with the original selected
sequence. Missing G2 position 5 can leave a descriptive first-ten-actual-outputs
summary available, but the matched first-ten-position endpoint is unavailable.
G3 cannot fill the G2 gap. An intact first group can still support k=5 when a
later group is incomplete. Group completeness is separate from program validity.
No A/B/C comparison, quality-matching decision, confidence interval or claim about
independent draws is computed here.

### 11.7 Progress and preserved earlier tests

`tests/phase1_matrix.json` adds a versioned `delivery_progress` record and
`step4_acceptance` with actual test method bindings. The legacy `current_step=3`
field is retained as the earlier catalogue snapshot because a preserved Step 3
regression explicitly asserts that value. `delivery_progress.step=4` identifies
the current delivery; the legacy value is not a claim that Step 4 is absent.
The old authorization is retained as snapshot history; the new instruction is
recorded under `delivery_progress.authorization`. No old test or gate is disabled,
rewritten or satisfied with substituted execution records. A later authorized
harness revision can migrate the legacy stage readers.

All original 54 VT identities, 40 TR requirements, 36 RF groups and 37 M-bearing
families remain intact. This delivery adds binding evidence for the Step 4
accounting portions without declaring the entire M milestone complete. Actual
runs, commands, environment and results are recorded separately from requirements.
The unchanged README remains the preceding Step 3 handoff; this section records
the current Step 4 API within the plan's allowed documentation paths. README and
CLI integration are scheduled for Step 6. No metrics implementation, publication
to a package registry, GitHub-hosted CI or substantive E evidence is added here.

## Step 6 addendum: complete local reporting path

Document progression: v0.4, 2026-09-17. Earlier schema identities and scientific
contracts remain unchanged. This section adds CLI/output bindings to the existing
record semantics; it does not redefine classes, validity or any estimator.

`python -m structdet_bench validate --bundle PATH/bundle.json` reads the passive
bundle and emits a redacted validation JSON object to stdout. It writes no files
and computes no structural metrics. `analyze --bundle PATH --output-dir NEW_DIR`
connects the existing evidence, inventory, population and metric modules and
writes a three-file report set. No generator, judge, code-execution or comparison
command is supplied.

### Prefix configuration

`analysis_config.extensions.prefix_mode` may be `descriptive` or `hero`.
Absent mode selects the already-supported descriptive-prefix interpretation; HF-00
explicitly requests `hero`. The requested k grid still comes from `requested_k`.
An unrecognized mode is an input failure and cannot silently fall back to a
successful analysis. No other extension becomes a runtime transformation rule.

### Errors versus evidential restrictions

Missing linked evidence can withhold a local assignment while leaving other
accepted records calculable. HF-04 therefore completes processing with a visible
missing-reference diagnostic and nineteen classified records. Malformed input,
duplicate identities, incompatible versions, invalid configurations and resource
failures return exit 2. Where serialization and output paths remain safe, an error
report preserves supported inventory and affected scopes. It is explicitly marked
with processing exit 2, even when a remaining descriptive quantity is available.
Known mathematical undefinedness and absent independent validation alone do not
make software processing fail. Unexpected local I/O/internal failures use exit 3
and bounded public diagnostics without private argument values or tracebacks.

### Common report tree and field coverage

`report.json` and `report.md` render the same eight ordered sections required by
HERO section 11.2. Scalars retain names, units, statuses, reasons, denominators and
unrounded stored values. Markdown uses readable summary tables with expandable
complete records. It HTML-escapes cell content and serializes control characters;
raw source content is not rendered as active Markdown or HTML.

RF-01 through RF-20 map to sections 1 through 5; RF-21 through RF-28 remain explicit
unimplemented V slots in sections 6 and 7; RF-29 through RF-36 map to the scoped
integrity/disclosure/correction and unavailable-capability records in section 8.
EC-001's five conditions remain conjunctive, and all ten reporting disclosures
are present. Imported review declarations never become toolkit certifications.
Unknown result expiry stays explicit. Reopening event names remain record content;
no automatic taxonomy change or model recovery is inferred.

The report binds every result to a cell and accepted population, with pinned
revision IDs, selected and counted sample IDs, shared groups and exact threshold
metadata. Input filenames and private roots are replaced by hashed locator
identities. Ordinary reports preserve scoped record IDs and readable metadata
states while withholding raw bodies, person mappings and unrestricted prose.
Exact local inputs remain necessary to inspect those privately retained records.

### Run manifest and replay

`run_manifest.json` records input byte hashes, configuration identity, source-code
file fingerprints, software/interpreter identifiers, operational limits and report
hashes. It does not hash itself. Input fingerprints identify the actual byte
snapshots, not independently validated observations or nonexistent fixture program
text. The default run ID is a deterministic digest of input, configuration and
implementation identity. The API permits an explicit safe run ID.

The same pinned input/configuration/implementation produces byte-identical JSON
and Markdown. The run-manifest UTC recording time and recorded interpreter/platform
are identified variable metadata. Supplied recording time must include a UTC
offset; it is not an asserted model-collection date. `recorded_at` can be pinned
for replay tests. No reproducible-model-generation claim follows.

### Output transaction

All three files must serialize before publication. The writer accepts only the
three fixed filenames and limits the combined payload to 128 MiB, with explicit
failure rather than truncation. The caller's output parent must exist. The output
is a new directory outside the input bundle tree. Existing files, directories and
symlinks are not replaced, including a concurrently created target.

The writer holds a no-follow descriptor for the parent, writes a private sibling
staging directory, synchronizes the files, then publishes with Linux
`renameat2(RENAME_NOREPLACE)`. Directory/file permissions are 0700/0600. Failed
pre-publication writes remove staging content. A synchronization error after the
atomic rename reports durability uncertainty and leaves the complete published
set intact. There is no destructive fallback on unsupported platforms/filesystems.
The low-level contract is documented in Linux `rename(2)` and Python's `os`
documentation; network filesystems and hostile OS/root-level actors are not covered
by a general sandbox or universal durability guarantee.

### Fixture identities and correction

`examples/hero_hf00/` contains the original four-by-five fixture as three input
files plus an independent `expected.json`. `tests/fixtures/hero_variants.json`
pins the base file hashes and six separately named changes with their own oracles.
Only the trusted test helper materializes these variants. Its output manifest and
record hashes are finalized before analysis; it cannot be invoked by input data
or the runtime CLI. All variants retain explicit fixture origin.

A corrected input is analyzed into a new output directory. Old input/output bytes,
sample identities and budgets remain unchanged. Current M fields are recomputed,
while V dependents stay unimplemented. HF-06 records a supported label revision;
it does not assert structural reopening or model learning. A separate
independence-only correction retains supported arithmetic and records the narrower
claim status.

### Approved test-maintenance amendment

The owner approved `STEP6-TEST-MAINTENANCE-001` for `tests/test_metrics.py`.
The three historical stage assertions now check that arithmetic leaves HF-00 files
unchanged, that the Step 5 delivery remains uniquely recorded, and that the
effective current step/authorization matches current delivery metadata. All test
identities and arithmetic assertions are preserved. The exact approved patch and
before/after fingerprints are recorded in the delivery evidence; the existing
matrix retains both the original request and its resolution.

The complete current regression contains 450 passing tests with no skips.
The end-to-end Step 6 path is implemented; full Phase 1 integration and final
completion remain Steps 7 and 8. This amendment does not authorize those steps
or change any frozen scientific contract.


## 13. Step 7 integrated evidence-record checks

These are physical encodings of HERO sections 5, 7 and 12, EI and EC-001. They
apply when the corresponding supplied record claims the relevant coverage. They
are not prerequisites for the clearly stipulated HF-00 software fixture.

### 13.1 Ordered functional-suite manifest

A `domain_suite` payload for `sorting_behavior` can carry
`extensions.functional_manifest` with `version: "0.1"`, `tests`, and `sha256`.
Each test row has `test_id`, `segment`, and the exact integer `input` list. The
canonical digest is SHA-256 of ASCII-escaped, key-sorted compact JSON of `tests`
plus one newline. The required 8,995 rows are the prescribed 781 V-SMALL, 18
V-SHAPE, 8,192 V-KEY and four V-STAGE cases, in their registered order.

The encoding uses `V-SMALL-0001` through `V-SMALL-0781`, `V-SHAPE-01` through
`V-SHAPE-18`, `V-KEY-0001` through `V-KEY-8192`, and `V-STAGE-01` through
`V-STAGE-04`. These suffixes are project serialization choices. The input
constructions and four witnesses come from the frozen HERO specification. Equal
input lists with different test IDs retain their separate purposes. Boolean values
cannot stand in for integer entries. Missing, repeated, reordered or modified rows
are unresolved, with their actual count and reason retained.

The toolkit reconstructs the expected input descriptions only to check the
supplied manifest. It does not execute any program against them.

### 13.2 Imported runtime and property observations

A sorting `domain_result` identifies the exact realization hash and suite-manifest
hash. Its known `observations` value is a record with `tested_ids`,
`runtime_status`, `property_checks`, and, where needed, `counterexample`.
A claimed pass requires coverage of every required ID, `runtime_status: completed`
and six explicitly true property checks: `fresh_plain_list`, `plain_integers`,
`length_preserved`, `nondecreasing`, `multiplicity_preserved`, `input_unchanged`.
The original full-suite denominator is retained.

A decisive imported failure may occur before the suite is complete. Its
counterexample must identify a tested case, violated property, explicit
`observed_violation`, exact subject hash and supporting evidence references.
Syntax, prohibited capability, exception and output-protocol violations can be
recorded explicitly. Timeout, memory limit, harness, containment and oracle error
remain different outcomes and cannot alone establish invalidity or nontermination.

The known environment record carries `containment_status`, `oracle_reviewer_refs`
and `accommodated_class_ids`. A complete imported validity claim needs the declared
passed containment check, resolvable oracle review and all eight reference
families. These are inspections of supplied records, not independent execution or
proof of the environment's behavior. Mock/fixture evidence on a decisive child path
cannot be promoted by a nonmock parent declaration. Missing essential evidence
withholds the affected judgment; it does not erase separately supported samples.

### 13.3 Reference and audit coverage

A supplied `domain_suite` may carry `extensions.reference_review` with
`descriptor_pairs`, `witnesses` and `core_roles`. The check inspects all 28
unordered descriptor pairs, the four exact W-01 through W-04 witness inputs and
the 32 prescribed core roles. Core IDs are `CORE-<family without SORT->-A/B/D`
and `CORE-X01` through `CORE-X08`. Every core entry links its distinct material,
assignment annotations and validity annotations. Positive A/B entries identify at
least two witnesses. Initial human identities, exposure and target/rubric agreement
are checked as records. Unresolved pair overlap and missing material remain visible.
A complete mock record arrangement remains mock and supplies no actual program,
expert annotation or independently validated taxonomy.

A `sampling_plan` may carry `extensions.hero_audit_positions` and
`extensions.hero_block_ids`. The latter declares the ordered six prompt-block IDs.
The former has 72 rows, each with `block_index`, `condition_index`, `group_index`,
`within_group_index`, and tagged `sample_ref`. Indices are one-based; conditions
1, 2 and 3 refer to A, B and C. The selected within-group position is exactly
`1 + ((block_index + condition_index + group_index - 3) % 5)`.
The sample's cell, group, attempt and position must agree. A missing opportunity
cannot be filled by a repeated sample or a targeted extra review. These records
add zero model observations. Generic audit records must agree with their actual
linked sampling plan, and reviewed items require corresponding annotation records.

### 13.4 Report and gate interpretation

Public reports retain typed source relationships, role and evidence references,
review/coverage states, sampled positions and correction dependencies. Raw bodies,
private actor mappings, unconstrained prose and locators remain protected. Known
absence is reported explicitly rather than hidden behind only a payload digest.
Deferred V/D quantities have their own null entries and named prerequisites.

The QA matrix links the original 54 VT, 40 TR and 36 RF identities to the current
M tests. Eight EC supplemental record checks are separately bound. Gate success
means that the applicable software/record-handling checks passed. All substantive
E duties remain unperformed, and Step 8 final audit/owner approval remains pending.
Historical Step 2 through Step 6 deliveries and earlier failed executions remain
part of the record. No old test identity or arithmetic oracle is removed.


## 14. Phase 2 Step 6 current CLI and report integration

The current executable includes the optional offline comparison workflow described
in COMPARISON_FORMAT.md section 13. Earlier step-specific paragraphs above retain
their historical scope. Supply analysis_config.extensions.comparison to request
the schema-0.2 structdet_comparison_v1 report; omit it for the explicit schema-0.1
M-only profile. validate checks records and replay shapes without numerical
comparison. analyze writes the same three fixed output files, including the full
used resampling indices inside run_manifest.json. Source bodies and private actor
mappings remain withheld. No generation, execution, remote retrieval or independent
scientific verification is added. Existing input and record schemas remain 0.1.
