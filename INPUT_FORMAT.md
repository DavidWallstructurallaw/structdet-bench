# Input and Evidence Format

Version: 0.2. Input schema: `0.1`. Record envelope: `0.1`. Evidence payload: `0.1`.

This document specifies the implemented **passive input layer**. Read it with
`PHASE_1_PLAN.md`, the frozen Phase 0 contracts, and
`EVALUATION_CLOSURE_ADDENDUM.md`. None of those scientific contracts is changed.
The module accepts records and inspects their shape, identity and byte references.
The passive loader does not admit evidence. Step 3 provides a separate
record-qualified admission pass. Neither API classifies programs, builds analysis
populations, calculates metrics, or produces a benchmark report.

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

`python -m structdet_bench` still offers only help and version commands. The
`validate` and `analyze` CLI commands belong to Step 6 and are unavailable here.

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
These QA files are not benchmark inputs. Current owner authorization covers
Step 3 and completion of the outstanding repository synchronization, not Step 4.
