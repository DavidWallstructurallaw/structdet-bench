# Comparison Record Format

Version 0.2. Implemented scope: **Phase 2 Steps 2 and 3**.

Sections 1 through 9 describe the record-binding layer. Section 10 adds the
separate text-diagnostic layer; CLI/report integration remains deferred to Step 6.

Read with `PHASE_2_PLAN.md` sections 3, 4.2 and 7 (Step 2), `HERO_BENCHMARK_SPEC.md`
sections 7 through 10, `METRICS_SPEC.md` section 10.1, and EC-001. The frozen
scientific contracts, Phase 1 code and original Phase 1 matrix remain unchanged.
Names introduced here are physical record encodings, not additional theory claims.

## 1. Interface and scope

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.comparison_records import review_comparison

bundle = load_bundle("local-study/bundle.json")
review = review_comparison(bundle)
print(review.requested, review.status)
for binding in review.bindings:
    print(binding.block_id, binding.condition_id, binding.cell_id, binding.status)
```

`review_comparison` consumes an already loaded `LoadedBundle`. It performs no new
file reads, model calls, candidate execution, label assignment, population
selection, surface tokenization, numerical contrast, resampling or prediction.
Returned records are immutable. Original input records and snapshots are retained.

The new comparison is opt-in through `analysis_config.extensions.comparison`.
An absent extension returns `not_requested`. A present null, malformed object or
unsupported version returns a requested `contract_error`; it is never ignored as
an absent request by this interface. A malformed main manifest instead returns
`unavailable`, because whether a comparison was requested cannot be established.

The existing M-only CLI/report pipeline is unchanged at this step. Its `validate`
command does not yet claim to validate this new comparison contract. Until Phase 2
Step 6 connects optional dispatch, use the separate API above for comparison
record validation. A valid or invalid comparison cannot change M populations,
class assignments, metrics, denominators or original report behavior.

The returned object includes private supplied metadata and evidence references.
Its default representation hides unrestricted payloads, but it is not the public
redacted report interface. Keep it local; later report integration applies the
existing privacy contract.

## 2. Result vocabulary

| Result | Meaning |
|---|---|
| `not_requested` | The optional comparison field was absent. |
| `unavailable` | The enclosing manifest/configuration could not be established. |
| `contract_error` | Present comparison data violates its physical contract. |
| `record_limited` | Some supplied bindings or facts are unresolved/inconsistent. |
| `record_consistent` | The checked records are consistent at this declared scope. |

Individual `Fact` outcomes are `record_consistent`, `inconsistent`, `unresolved`,
`not_applicable`, or `contract_error`. They retain a stable check name, bounded
reason codes, original observed value, expected value when relevant, source
references and mock status where checked. Unknown values remain unknown.

`ComparisonReview.bindings` retains all 18 main block-condition roles, including
roles with missing or ambiguous cell records. Each `CellBinding` retains separate
facts, frame/cell/study metadata, recorded attempts, extra attempts and the linked
budget. `pairs` contains B-A, C-A and C-B binding facts for each block. These are
compatibility inputs, not calculated contrasts or endpoint eligibility decisions.

Every review explicitly has `independent_validation_performed=False` and
`endpoint_eligibility_evaluated=False`. Record consistency cannot establish that
P1 or P5 is supported, that controls really operated as asserted, or that evidence
is independent. A global limitation must not be used as a blanket veto of every
future comparator: missing B can coexist with intact C-A facts. Step 4 owns the
actual endpoint-specific gates; Step 5 owns the prediction outcomes.

## 3. Required comparison object

Every field below is required. There are no inferred A/B/C roles or optional
scientific controls filled from filenames. Unknown metadata uses the existing
`known`, `unknown`, `unavailable`, or justified `not_applicable` wrapper.
Undeclared fields, including `all_gates_passed` or a material-role override, fail.

| Field | Encoding |
|---|---|
| `comparison_schema_version` | Exactly `"0.1"`. |
| `comparison_id`, `comparison_version` | Safe IDs. The latter identifies the input instance revision. |
| `profile` | Exactly `"hero_sort_abc_v1"`. |
| `blocks` | Exactly six ordered entries, P01 through P06. |
| `pilot_cell_refs` | Zero through three separate typed cell references. |
| `questions` | Nonempty unique subset of `P1`, `P5`. |
| `views` | Exactly `["classified_all", "classified_valid"]`. |
| `evidence` | The seven named reference groups in section 7. |
| `text_method` | The registered method identities in section 8. |
| `resampling` | The future procedure binding in section 8, not executed here. |
| `limits` | All four declared engineering limits in section 8. |
| `revision` | Prior comparison IDs, prior run IDs, tagged reason and changes. |

Material role is inherited from the actual bundle, not trusted from a comparison
claim. A `pilot` bundle cannot be treated as main-study evidence. Pilot references
must remain disjoint from main roles and refer to P00 where the record is present.
Unbound cells remain explicitly listed; they are not pooled into the main target.

One block entry has this shape, repeated for all six registered block IDs:

```json
{
  "block_id": "P01",
  "conditions": {
    "A": {
      "cell_ref": {"record_type":"cell","record_id":"P01-A","record_version":"0.1"},
      "study_record_ref": {"record_type":"evidence","record_id":"study-P01-A","record_version":"0.1"}
    },
    "B": {
      "cell_ref": {"record_type":"cell","record_id":"P01-B","record_version":"0.1"},
      "study_record_ref": {"record_type":"evidence","record_id":"study-P01-B","record_version":"0.1"}
    },
    "C": {
      "cell_ref": {"record_type":"cell","record_id":"P01-C","record_version":"0.1"},
      "study_record_ref": {"record_type":"evidence","record_id":"study-P01-C","record_version":"0.1"}
    }
  }
}
```

Instance cell IDs may vary. Their actual `prompt_block_id`, `condition_id`,
protocol and frame must match the explicit role. A missing referenced record
produces a missing-role fact. Omitting the intended B key or shortening the block
array instead produces a contract error. Duplicate cell IDs or role reuse cannot
be resolved by choosing a convenient copy.

Frame comparison retains domain/context, horizon, resolution, schema/registry
versions, rubric, membership rules and relevant invariants. Equal short identifiers
alone cannot make changed contextual definitions compatible. Model family,
checkpoint, collection-window and serving identities remain separate facts.

## 4. Study observation record

`study_record_ref` refers to an existing typed `evidence` payload. It must have
purpose `observation`, method `study_binding_v1`, the corresponding cell target,
active scoped records and reviewer references. Its ordinary origin, knowledge
type, transformations, access state, conflicts and mock marker remain in the
existing evidence record. The additional physical payload is
`payload.extensions.study_binding`, with exactly these fields:

| Field | Meaning |
|---|---|
| `version` | `"0.1"`. |
| `comparison_id`, `comparison_version`, `block_id`, `condition_id` | Must match the comparison instance and bound role. |
| `protocol_ref` | Typed reference matching the cell's generation protocol. |
| `sent_prompt` | Tagged `artifact_ref` and tagged `attestation_ref`, as below. |
| `visible_system_instruction`, `platform_context`, `reasoning` | Tagged null for explicitly absent context, or a typed artifact/raw-artifact/evidence reference. Unknown is retained. |
| `controls` | All ten requested/enforced control records in section 5. |
| `cap` | Tagged `unit`, `tokenizer`, and `convention`. |
| `budget_ref` | Tagged typed budget reference. |
| `attempts` | Exactly four ordered slot bindings in section 6. |
| `automatic_retries` | Tagged Boolean. Unknown is not assumed false. |
| `deployment` | Tagged `serving_identity`, tagged Boolean `change_detected`, and `evidence_refs`. |
| `deviations` | Array of safe `code`, tagged `detail`, and typed `evidence_refs`. |

A known deployment change is exposed separately. A stable-serving assertion needs
its linked observation record with `extensions.recorded_deployment` equal to the
asserted `serving_identity` and `change_detected` wrappers; a model marketing name does not fill an unknown serving
identity. No mechanism here discovers hidden infrastructure or independently
verifies a provider. Added system instructions are preserved as changed actual
context and must be assessed under the later qualified-comparison rules.

### Prompt content and byte attestations

The exact visible prompt is the frozen opener, common task, A/B or C clause, and
common output instruction, separated by one blank line. The first encoding uses
LF and UTF-8 with no added final newline. The constants are literal transcriptions
of HERO section 7.2; tests derive expected bytes independently from that document.
A/B sent-byte equality is checked separately from conformity to the registered
prompt. C must contain the registered mechanism-divergence clause.

`sent_prompt.artifact_ref` is a tagged artifact/raw-artifact reference already
loaded by the passive reader. `sent_prompt.attestation_ref` is a tagged evidence
reference. No external URL is fetched and no unreadable bytes are replaced with
an empty string. CRLF conversion, whitespace trimming and prompt repair are not
performed for sent-byte checks.

A verified-byte alternative requires an active observation record with method
`verified_sent_bytes_v1`, the bound cell target, a known SHA-256 `subject_hash`,
reviewer references, and `payload.extensions.verified_prompt` containing exactly:
`encoding`, `byte_length`, `comparison_id`, `block_id`, `condition_id`, `protocol_ref`.
Its values must match the expected UTF-8 bytes and protocol. It establishes only
consistency of the supplied attestation, not a new independent observation.

When both local bytes and an attestation are provided, disagreement is retained.
A known but unreadable local artifact is not silently replaced by a favorable
attestation. Where local bytes were explicitly unknown/unavailable and a sufficient
attestation was supplied, that record-only route is identified. The original
reference and access state remain in the loaded bundle.

## 5. Controls, resources and usage

Each of the ten controls is required as:

```json
{
  "requested": {"state":"known","value":0.4},
  "actual": {"state":"unknown"},
  "enforcement": "not_recorded",
  "evidence_refs": []
}
```

`enforcement` is `recorded`, `unsupported`, `hidden`, or `not_recorded`. A requested
value alone cannot establish actual enforcement. A supporting observation's
`extensions.recorded_controls` maps each checked control name to the exact
`requested`, `actual` and `enforcement` fields. Its target, reviewer and decisive
support records must resolve. A Boolean cannot substitute for a numeric value.

| Control | Registered request |
|---|---|
| `temperature` | A/C 0.4, B 1.0. |
| `top_p` | 1.0. |
| `presence_penalty`, `frequency_penalty` | 0 where exposed. |
| `generator_seed` | Known null for no user-fixed seed. |
| `max_output_tokens` | 8192. |
| `tools`, `retrieval`, `history` | False. |
| `best_of` | 1. |

JSON numeric lexemes retain `ExactNumber` values and are compared by exact decimal
value. Unsupported penalties may have justified `not_applicable` requested and
actual states plus `enforcement="unsupported"`; this preserves the source's
“where exposed” condition. An unsupported B temperature limits that manipulation
without automatically invalidating independently sufficient A/C facts.

`cap` preserves actual token unit, tokenizer and cap convention. Different cap
semantics are incompatible facts even when the visible numeric allowance is
8192. A nonblank provider-specific convention is recorded as supplied; equal
labels do not independently validate the provider's actual accounting.

The linked budget's known `planned` object has exact integer fields `calls:4`,
`candidate_positions:20`, `output_cap_per_call:8192`, and scope including the cell.
Its `actual` wrapper is preserved without imputing usage, charges or hidden work.
Input, output and reasoning quantities should retain separate supplied entries
and knowledge states. Unequal actual usage is not an error in planned-resource
matching. No price, equal-compute claim or spending authorization is inferred.

## 6. Attempt and collection-order bindings

Each of four ordered rows contains `group_index`, tagged `attempt_ref`, tagged
`global_order`, and tagged `recorded_at`. Group indices are exactly 1 through 4;
known times must contain a UTC offset. Missing actual attempts are unresolved
slots, not invented calls or observations.

The reference resolves to the corresponding cell, local registered call order,
five planned candidate positions and explicitly primary `retry_of:null`. Failed,
cancelled or unknown attempt states are retained as recorded. A retry cannot
replace the planned primary identity. Repeated use of one attempt reference is
explicitly diagnosed. Other received attempts remain in `extra_attempt_ids`.

For group g and block b, the expected condition permutation is element
`(b+g-2) mod 6` of `ABC, ACB, BAC, BCA, CAB, CBA`. Global ordinal is
`18*(g-1)+3*(b-1)+condition_position+1`. Only supplied order records are checked.
The toolkit does not collect or replay model calls; an asserted ordinal is not
independent evidence of a real historical execution order.

## 7. Evidence, exposure and revision

The seven reference groups are `registration`, `exposure`,
`structural_validation`, `core_audit`, `integrity`, `independence`, and `correction`.
They accept the existing record types shown in `EVIDENCE_KINDS`. Empty groups mean
no corresponding evidence supplied. Typed payload validity, access, conflict,
active/corrected state and decisive references are checked; references are not
replaced with an `all_gates_passed` switch.

The bounded dependency walk follows `evidence_refs` and `reviewer_refs`, not every
lineage edge. A missing, cyclic or conflicted decisive path stays unresolved.
Mock descendants cannot supply nonfixture evidence merely through a nonmock
parent label. Lineage ancestry and transformation history remain retained;
absence of documented ancestry never establishes independence.

A preregistration's `extensions.comparison_registration` has exactly
`comparison_id`, `comparison_version`, `binding_sha256`, tagged
`first_inspected_at`, and tagged `first_collection_at`. The payload's own
`registered_at` is compared with both. It must precede them to support the
prospective timing assertion. Equal, later or unknown times are exposed.
Registration is also tied to the exact current configuration fingerprint.

`configuration_fingerprint` uses domain-tagged compact ASCII-escaped JSON:
objects are sorted key/tagged-value pairs; arrays retain order; exact numeric
lexemes receive a separate tag; other scalars include their Python JSON type.
The UTF-8 representation has no terminal newline and is hashed with SHA-256.
This encoding distinguishes Boolean/integer and numeric-token/string forms.
Its calculation does not verify the authenticity of a date or observation.

Revision records retain old comparison/run IDs, a reason and declared changes.
They never contain mutation instructions. Rebinding the same observations does
not create samples. Actual propagation through numeric comparisons and reports
belongs to later authorized steps. The E requirements of UD-006 remain open.

## 8. Future-method bindings

The text profile stores `extraction_rule_version`, strict UTF-8 encoding,
`surface_lexical_trigram_jaccard_v1`, `unicode_category_version`,
`white_space_version`, and `white_space_sha256`. Table identities can be explicitly
unknown. This step neither installs a table nor tokenizes text; unknown proxy
metadata cannot itself erase independently supported P5 count facts.

The resampling profile stores `paired_prompt_block_bootstrap_v1`, seed 20260917,
2,000 replicates, exact probability strings `0.025`/`0.975`, and
`linear_b_minus_one_v1`. It also stores a tagged independence-assessment reference
and a tagged optional replay artifact. These method names encode the existing
MET/HERO procedure. No random generator, index matrix, quantile or interval is
executed. Replay content is validated in Step 5; a resolvable artifact identity
alone is not a validated replay. Missing dependence records remain unresolved.

The four explicit limits are `max_lexical_units`, `max_pairs`,
`max_trigram_visits`, `max_exact_bits`. The standard declarations are 100000,
100000, 100000000 and 131072 respectively. Step 2 checks positive plain integers
up to 2^31-1 as a bounded transport envelope. Later numerical modules must validate
supported operational limits before execution. Accepted serialization does not
promise arbitrary workloads will execute. No truncation or favorable subsampling
is authorized by a limit.

## 9. Verification and catalogue storage

The temporary comparison fixtures contain 18 explicitly mock cell/protocol
bindings, 72 stipulated attempt records and exact prompt bytes. They contain no
candidate programs, generated realizations, class distribution, score or P1/P5
result. `tests/fixtures/comparison_cases.json` supplies independent adverse-state
expectations. These tests are additional to all predecessor checks.

The Phase 2 matrix retains the complete semantic catalogues and original 503
Phase 1 method identities through two explicit, hash-checked source references.
`pinned_catalogues_v1` expands only from the fixed Phase 1 matrix and scientific
rows; `pinned_predecessor_methods_v1` expands the unique original test-binding
inventory. `tests.phase2_helpers.read_matrix()` exposes the full logical matrix.
Fully expanded JSON remains accepted. Tampered sources or expanded-content hashes
fail; no source path, expression or inferred execution result is configurable.
Actual Step 2 bindings, status, authorization and prior delivery history remain
explicit. Source-linked storage does not modify the frozen Phase 1 matrix, remove
requirements, or count source records as newly executed tests.

The Step 1 gate's synthetic test scenario needed a scoped progression repair:
it now includes synthetic outcomes for every authorized stage, and its negative
empty-binding test explicitly empties that list. Test identities and the failure
conditions are unchanged. Finding P2S2-F01 records the before/after failing cases.
Current-stage success remains distinct from completion of all 26 V obligations.

## 10. Phase 2 Step 3: original-text and matched-pair diagnostics

Step 3 implements `structdet_bench.text_diagnostics`. It consumes the same loaded
byte snapshots and accepted population IDs as M, without re-admitting labels or
running candidate code. The comparison-record interface above remains unchanged.
CLI dispatch and comparison report rendering remain scheduled for Step 6.

### 10.1 Component interfaces and explicit method pins

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.populations import build_populations
from structdet_bench.comparison_records import review_comparison
from structdet_bench.text_diagnostics import (
    method_from_record, limits_from_record, diagnose_cells,
)

bundle = load_bundle("study/bundle.json")
populations = build_populations(bundle)
binding = review_comparison(bundle)
# Only proceed when the comparison configuration itself is resolved.
method = method_from_record(binding.configuration["text_method"])
limits = limits_from_record(binding.configuration["limits"])
diagnostics = diagnose_cells(bundle, populations.cells, method, limits=limits)
```

`method_from_record` requires known extraction/category/White_Space identities.
Unknown method metadata raises a bounded `InputError`; callers must retain the
corresponding comparison restriction. A recognized but mismatching table/profile
produces unavailable diagnostics. No method is silently supplied from a host
that happens to run the code.

The current category table is the standard-library Unicode database **15.1.0**.
The runtime checks `unicodedata.unidata_version == "15.1.0"`; it does not install
or download another database. The separate White_Space table is the 25 code points
in Unicode 15.1.0 PropList, represented by eleven inclusive intervals:

```text
0009..000D 0020 0085 00A0 1680 2000..200A 2028 2029 202F 205F 3000
```

Its `white_space_version` is `15.1.0`. `white_space_sha256` is
`3ec9cc63e7f950c749d0d2159b19bff128966bfc9ee4fc6d37810749309d0604`.
This identifies ASCII-escaped compact key-sorted JSON with keys `property`,
`unicode_version`, and decimal integer `ranges`, plus a final newline. It does
not claim to be the hash of the entire upstream PropList file. The source is
Unicode's versioned PropList-15.1.0, also maintained in the Unicode Consortium's
`unicode-org/unicodetools` repository. U+001C through U+001F, U+200B and U+FEFF
are not White_Space in this profile; a host `str.isspace()` is not substituted.

`TextMethod(extraction_rule_version)` explicitly constructs this supported
profile for component work. It does not assert that an input study registered it.
The accepted Step 2 mock study retains its unknown table declarations until a
later test/study supplies actual pins. Source papers supply the structural versus
realization distinction; MET supplies this particular lexical proxy.

### 10.2 Exact text and boundary behavior

`tokenize_text(bytes, method, limits=...)` uses strict UTF-8. It converts CRLF and
standalone CR to LF, retaining every other code point, case, identifier, literal
and comment. Maximal L*/N*/underscore runs form surface lexical units. Other
non-White_Space code points form individual units. Combining marks remain separate
units; there is no Unicode normalization. Boundary symbols are tagged separately
from all text units, so text spelling `BEGIN`, `end`, or `boundary` cannot collide.
Consecutive padded triples form a set, not a bag.

An empty emitted body, whitespace-only body, inaccessible artifact, malformed
UTF-8 and resource failure have distinct reasons. One lexical unit yields one
trigram. A known truncated region remains truncated and may still be eligible.
The component reads no live path and searches no fence. A supplied output artifact
is the already selected region; a supplied extraction span must have been verified
against the held raw/output bytes. Missing or contradictory span evidence cannot
trigger another extraction, a repaired body, or a neighboring candidate.

Per-sample records retain assignment revision, completion state, extraction/span
status, artifact reference, original-byte hash/size, normalized-text hash,
trigram-set hash/count and surface lexical unit count. Snapshot paths are represented
by locator hashes. The actual held snapshot is checked against its identity;
stale associations and mismatched accepted assignment context are rejected.
No text similarity is used to assign a structural class.

The standalone tokenizer exposes lexical payloads for controlled inspection.
They are excluded from its default representation and must not be exported as an
ordinary public report. Population diagnostic results contain hashes, counts and
references rather than bodies or lexical sequences. They retain a private
`source_cell` reference for later evidence-aware orchestration.

### 10.3 Populations, pairs and fractions

`diagnose_population(bundle, cell, view, method, limits=..., work=...)` handles
one `classified_all` or `classified_valid` view. `diagnose_cells` handles explicitly
supplied cells/views separately, in supplied order, sharing one cumulative budget.
It performs no pooled estimation or A/B/C comparison.

The original accepted denominator `population_size` and IDs remain unchanged.
`eligible_sample_ids`, `eligible_count`, per-sample exclusions, and
`proxy_text_coverage` identify the diagnostic subset. Both surface and structural
pair means use exactly that subset. All unordered distinct-observation pairs are
included. Identical bytes can occur in different observations; tokenization caching
never reduces observation multiplicity or the pair denominator.

Each pair records its two sample IDs, intersection/union counts, exact reduced
distance fraction, structural disagreement and known/unknown same-call relation.
Pair counts and distinct recorded calls establish no independent-replicate count.
The latter remains null. Same-class pairs retain per-class denominators, including
occupied classes with no eligible text or only one eligible text.

Results are `surface_lexical_trigram_distance`,
`within_class_realization_diversity_proxy`, and `structural_pair_non_equivalence`.
Each retains a numeric value plus an exact numerator/denominator, pair denominator,
unit, status, reason and `MET-0.2` identity. The within-class aggregate weights by
pair count. The exact text-subset SCI is recorded only as an identity check; it
never replaces full-population SCI.

With fewer than two eligible texts, pair means are undefined. With all occupied
classes singleton on the text subset, the within-class aggregate is undefined.
An unresolved population/frame or method has unavailable results, not zero pairs.
Ordinary missing/invalid text can reduce coverage while supported M counts remain
unchanged. No quality/coverage threshold or P1/P5 qualification is decided here.

### 10.4 Explicit workload and precision limits

The four limits retain their Step 2 names and defaults: 100,000 lexical units per
text, 100,000 pairs per cell/view, 100,000,000 cumulative trigram visits and 131,072
bits per retained exact numerator/denominator. Overrides must be positive plain
integers no greater than 2^31-1, declared before calculation. They do not authorize
approximation or guarantee completion on every machine.

A lexical-unit limit failure makes the affected text subset unresolved for the
requested diagnostic. The expensive sample is retained and coverage/means become
unavailable, rather than recomputed after dropping it. Pair-count failure is
checked before pair enumeration and withholds the requested pair diagnostics.

A logical trigram visit charges both input-set sizes once for each compared pair;
intersection and union share that charge. The preflight required total is
`(m - 1) * sum_i |G_i|`. Within-class means reuse those distances. If the remaining
shared visit budget is insufficient, surface means are unavailable without partial
enumeration. The exact Q count may remain available on the same fully known subset,
because its finite-count formula needs no trigram visits. A separately supplied
WorkBudget must match the declared maximum; it cannot silently reset mid-run.

Exact rational accumulations and means are checked against the bit limit. A failure
withholds affected means, clears partial pair output, and records actual visits
and completed pair work. There is no floating fallback, text truncation, pair
subsampling or partial-mean renormalization. Supported M results remain available.

### 10.5 Verification and stage maintenance

`tests/fixtures/text_oracles.json` contains independently authored token lists,
trigram sets, source pins and exact pair expectations. MET MF-11 gives 4/5; MF-12
gives Q=1/2 with SCI_text=5/8. MF-13/14 retain singleton and missing-text boundaries.
An unequal-class fixture gives pair-weighted within-class mean 9/10; the unweighted
class mean would be 13/15 and is rejected as a replacement estimator.

P2S3-F01 records four reproduced historical stage-check failures and their narrow
maintenance under PLAN2 section 6.3. Step 2's 93 method identities and prior V
statuses remain recorded, synthetic incomplete-V gates stay failure-sensitive,
and implementation files remain prohibited before their authorized step. No test
identity or scientific oracle is removed. All Phase 1 runtime, tests, contracts,
fixtures, matrix and historical QA remain unchanged.

Step 3 completes the VT-31 and VT-33 component obligations. VT-32, VT-36 and
report/EC integration stay partial until their later prescribed checks. No
prediction, condition contrast, interval, empirical support claim, model call or
candidate execution is produced by this layer.
