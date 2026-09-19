# Comparison Record Format

Version 0.4. Implemented scope: **Phase 2 Steps 2 through 5**.

Sections 1 through 9 describe the record-binding layer. Section 10 adds the
separate text-diagnostic layer. Section 11 adds endpoint gates, contrasts and
block summaries. Section 12 adds paired sensitivity and P1/P5 decisions;
CLI/report integration remains deferred to Step 6.

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

## 11. Step 4 endpoint gates, contrasts and block summaries

The implementation is `structdet_bench.comparisons`. The controlling rules are
PLAN2 sections 3.4-3.5 and Step 4, MET sections 10-11.2, HERO sections 8-10 and
VF sections 5.3 and 6.2. This layer consumes the original loaded snapshot, accepted
M populations and Step 3 diagnostics. It neither changes the structural partition
nor reconstructs labels from public reports.

### 11.1 Interface and returned scope

```python
from structdet_bench.local_io import load_bundle
from structdet_bench.populations import build_populations
from structdet_bench.comparison_records import review_comparison
from structdet_bench.text_diagnostics import (
    diagnose_cells, method_from_record, limits_from_record,
)
from structdet_bench.comparisons import compare_study

bundle = load_bundle("local-study/bundle.json")
populations = build_populations(bundle)
review = review_comparison(bundle)
if review.configuration is None:
    raise ValueError("No supported comparison configuration")
config = review.configuration
diagnostics = diagnose_cells(
    bundle, populations.cells,
    method_from_record(config["text_method"]),
    limits=limits_from_record(config["limits"]),
)
result = compare_study(bundle, populations, diagnostics)
for block in result.blocks:
    print(block.block_id, block.condition_pair, block.view)
    print(block.values, block.eligible_before_resampling)
```

A count-only caller can omit `diagnostics`. P5 then retains its supported count
comparisons. Requested P1 quantities expose missing diagnostic prerequisites.
No text is fetched, re-extracted or synthesized inside `compare_study`.

The result contains the actual comparison configuration identity, material role,
record review, all intended block/condition roles, per-block operands, gates,
qualifications, dependencies, primary summaries and secondary summaries. Unknown
and unbound cells remain in the supplied review. The status `processed` describes
component processing, including limited results; it does not assert that every
endpoint is eligible. Requested malformed configurations retain `contract_error`.

Each `Number` retains a name, unit, result status, exact fraction where available,
unrounded numerical value, and reasons. Each `Operand` identifies its cell, view,
selected and counted sample IDs, original population size, both axes' revision
pins, prefix k where relevant, and method metadata. Thresholded support companions
identify their fixed secondary threshold 0.10. Every subtraction retains both
operands even when the contrast is withheld.

These component records retain private provenance and metadata for local audit.
They are not a public redacted report. The comparison CLI and report attachment
remain deferred to Phase 2 Step 6.

### 11.2 Exact, endpoint-specific gates

| Gate | Exact test | Applicability |
|---|---|---|
| Intended positions | Twenty selected realizations in the original four groups of five; the HERO prefix must be complete and unambiguous. | Primary P1/P5. |
| Classification coverage | Accepted classified / selected >= 9/10. | Both questions. |
| Decisive validity coverage | Accepted valid or invalid / selected >= 19/20. | Both questions. |
| Valid-output structural coverage | Classified-valid / accepted valid >= 9/10 when that denominator exists. | Both questions, conditional denominator rule. |
| Proxy text coverage | Eligible text / the relevant classified view >= 19/20, with at least two texts. | P1 and its valid-only sensitivity. |
| Validity floor | Accepted valid / selected >= 4/5. | Required for P5; separately recorded quality diagnostic for primary P1. |
| Matched quality | Absolute difference in compared cells' valid fractions <= 1/10. | C-A and C-B separately for P5; diagnostic for primary B-A P1. |
| Shared frame/policy | Compatible context, horizon, task/schema/rubric meanings, extraction, material and evidence policy. | Each affected contrast. |
| Controls and resources | Participating cell and pair records support the registered manipulation and planned-resource match. | Each affected comparator. |
| Evidence scope | Appropriate scoped supplied evidence, or explicitly stipulated fixture treatment. | Evidence-qualified eligibility; no real validation is performed. |

Counts are compared as exact fractions. At n=20, 18 classified samples and 19
decisive validity assessments meet their respective thresholds. With 16 valid
outputs, 15 classifiable-valid samples meet 9/10; 14 do not. Text coverage 19/20
meets 19/20, but 17/18 and 18/19 do not. The P5 floor passes at 16/20, and its
quality band passes at a 2/20 difference and fails at 3/20. These cases are pinned
in `tests/fixtures/comparison_cases.json` alongside the earlier binding fixtures.

A valid-output coverage denominator of zero stays `undefined` in the original
ratio and yields `conditional_not_applicable` for that particular gate. It is
never relabeled zero or one. P5 still fails its separate validity floor. Primary
P1 can remain eligible with determined invalid outputs if its own classification,
text and other prerequisites hold, with the quality deterioration exposed.

`Gate.status` is `passed`, `failed`, `unresolved`,
`conditional_not_applicable`, or `fixture_stipulated`. Required versus diagnostic
status is explicit. `eligible_before_resampling` requires all of the relevant
required gates and all primary quantities to be available. The additional
`clean_quality_eligible` property also requires the quality floor and band.
Neither property asserts a supported theory result or an available interval.

Each P5 comparator is independent of the other comparator's missing role. An
unusable B control can leave C-A eligible. Missing C can leave B-A intact. Proxy
text loss, a Unicode-table problem or exhausted surface-work budget cannot veto
P5 when its own identity, membership and validity evidence remain sufficient.
Material essential to those separate judgments retains its ordinary consequence.

A legitimately unexposed presence/frequency penalty retains its justified
non-applicability. The Step 2 aggregate participant status is retained as evidence;
Step 4 evaluates its underlying facts with this explicit conditional rule instead
of letting a redundant unresolved aggregate veto the exception. Other unknown
controls remain unresolved. Equal planned allowances never assert equal actual
token use, hidden compute, money or latency.

### 11.3 Compatible arithmetic and evidence-qualified interpretation

Known incompatible frame, prompt, control, cap or serving records withhold the
corresponding contrast while retaining separate supported operand values. Missing
checkpoint or hidden-control evidence can leave a qualified descriptive contrast
available, with the stronger endpoint gate restricted. A single bad condition
cannot erase independently sufficient comparator records.

The component checks that supplied populations still correspond to the loaded
selection, original sample associations and exact admitted revisions. It also
checks the diagnostic's source population, method, workload limits, eligible IDs
and pair denominator. Stale contexts are rejected, without automatic re-admission
through a weaker path or silent rebinding of old diagnostics. Changes require the
caller to recompute the appropriate upstream component on the revised input.

All ordinary differences require identical metric names and units. Entropy
contrasts remain in nats; concentration, support and effective counts keep their
own meanings. A generic subtraction cannot combine entropy and lexical distance.
The one explicitly authorized cross-estimand expression is the registered P1 G.
Exact arithmetic observes the declared bit bound; nonfinite or unstable numerical
results are withheld. Neither silent truncation nor a floating fallback is used
to rescue an over-limit exact calculation.

Fixture gates describe stipulated software cases and preserve
`independent_validation_performed=False`. Absent real human or field evidence does
not prevent fixture development. A supplied contradictory fixture registration
still restricts its gate, and an active independence correction can restrict the
claim while leaving justified arithmetic unchanged.

For nonfixture data, the evidence gate retains registration timing and
configuration binding, the participant-scoped structural/core/audit records,
exposure and independence records, integrity assessment and active corrections.
Referenced checks must have their required content; an `all_gates_passed` boolean
is not accepted. Mandatory structural-validity and source-integrity requirements
cannot be waived with `not_applicable`. A descriptive/pilot or revised collection
cannot silently become a new confirmatory sample. These inspections establish
record consistency only. They never certify the truth of an imported claim,
conduct the reported execution or annotation, close UD-006, or establish ongoing
operational openness from offline records.

### 11.4 Per-block quantities and companion diagnostics

P1 uses `classified_all` as its primary view. Within each condition, the surface
mean L and structural pair non-equivalence Q use the exact same eligible texts and
unordered pairs. The per-block values are:

```text
surface_gain = L_B - L_A
structural_gain = Q_B - Q_A
p1_proxy_gain_contrast = surface_gain - structural_gain
```

The original M population and its coverage remain separate. The valid-only view
is a labeled sensitivity, with its own text subset and denominators. Negative or
zero structural gain is retained. No directional verdict is produced here.

P5's primary view is `classified_valid`, with separate C-A and C-B differences in
the original intended distinct-20 prefix. The all-classified view and k=5/10 are
companions. There is no best-of selection, replacement of a missing candidate,
quality equalization by deleting successes, or extra sampling after a repeated
mechanism. A complete but wholly unclassified prefix can have a known zero count;
a missing intended position cannot be repaired by a later group's output.

Companions include same-unit differences in the six core M quantities, all five
coverage ratios, k=5/10/20 structural distinctness and the available Step 3 means.
Class-aligned tables retain all eight registered classes, original counts, each
view's denominator, exact frequencies and compared-cell differences. Reference
zeros are distinguished from an undefined frequency in an empty classified
population. No automatic new class is created.

`surface_proxy_near_ceiling` applies at baseline surface distance >=19/20.
Observing all eight registered classes produces a registry-ceiling qualification.
These are interpretation flags only. They cannot replace an endpoint, trigger an
extra sample or imply that the registry exhausts the model's repertoire.

### 11.5 Equal-block summaries and explicit attrition

Full primary summaries use the intended ordered P01-P06 block list. Every block
receives equal weight, regardless of its number of accepted outputs or pairs.
P1's two gains and G share one included block set. Each P5 comparator preserves
its own set, missing-block reasons and failed eligibility gates.

The default does not provide a substitute mean for an incomplete full target.
An explicit `include_descriptive_subset=True` request additionally returns an
`available_block_descriptive_subset`: all intended blocks with jointly defined,
compatible operands, without selecting on sign or favorability. It retains the
original intended list and exact missing reasons. Its subset rule is recorded;
it cannot impersonate the six-block result. Numerically defined blocks with a
quality or evidence restriction remain visible with that restriction, rather than
being silently excluded to improve a mean.

`BlockSummary` contains intended/included block IDs, missing reasons, gate
failures, per-block values, means and the separate full-target/eligibility states.
Zero available blocks yield unavailable means. A custom smaller list passed to
`summarize_blocks` is explicitly `declared_descriptive_target`, even if complete;
it cannot establish completion of the registered six-block design.

`secondary_summaries` applies the same equal-block arithmetic separately to each
companion quantity and k. A secondary entropy contrast can remain available when
missing text prevents P1. Its availability supplies no primary P1/P5 claim. Mean
per-block entropy is never replaced by entropy of pooled counts, and a mean
structural count is never replaced by the union of classes over prompts.

All group associations, possible shared cross-cell dependencies, original budget
and supplied resampling records remain attached. Pairs and candidate rows do not
become statistical replicates. Intervals, resample-index generation, dependence-
qualified uncertainty and final P1/P5 outcomes remain Phase 2 Step 5 work.

### 11.6 Test history and stop boundary

P2S4-F01 records the two reproduced Step 3 historical-stage assertion conflicts.
The unchanged test identities now require a unique retained Step 3 delivery and
contiguous earlier-stage history including Steps 1 and 2. Exact method-binding,
predecessor, evidence and deferred-scope checks remain in place. The original
failure output, applied patch and before/after fingerprints accompany the delivery.
The repair follows PLAN2 section 6.3 and changes no scientific contract.

Step 4 adds component gate/contrast/summary coverage. VT-31 and VT-33 retain their
Step 3 implemented status; the remaining applicable V families continue to await
their complete later-step checks. All substantive E duties stay unperformed and
D capabilities remain deferred. This layer supplies no provider client, candidate
execution, automatic classifier, public report dispatch or Step 5 verdict.

## 12. Step 5 paired sensitivity and operational decisions

Interface progression: v0.4. The scientific baseline, primary endpoints, coverage
and quality rules are unchanged. Sections 10 and 11 describe predecessor layers;
their historical statements about deferred Step 5 work remain historical.

```python
from structdet_bench.uncertainty import resample_study
from structdet_bench.predictions import evaluate_predictions

# bundle and comparisons must refer to the same acquired input snapshot.
sensitivity = resample_study(bundle, comparisons)
results = evaluate_predictions(sensitivity)
```

These component APIs consume immutable local records. They do not read new files,
execute candidates, call models, change labels or publish reports. Comparison
CLI/report dispatch and inclusion of replay data in `run_manifest.json` remain
Phase 2 Step 6. The existing M-only CLI is unchanged.

### 12.1 Index manifests and deterministic replay

`make_replay(ordered_block_ids)` uses a private `random.Random(20260917)` and
`randrange(P)` to produce exactly 2,000 rows, each containing P zero-based indices
sampled with replacement. P is between two and six in this bounded design. One
row selects complete paired blocks; it never samples candidate rows or pairs.
The complete ordered block list, indices, seed, method, statistic, quantile rule,
probabilities, RNG algorithm/API, implementation, Python version and RNG state
version are retained. The RNG is MT19937 with state version 3. Global RNG state
is untouched.

Canonical replay bytes use UTF-8 JSON with ASCII escaping, sorted object keys,
compact separators and one final newline. `indices_sha256` hashes the complete
index array. `sha256` hashes the manifest except its own `sha256` field.
`validate_replay` checks every field, exact dimensions, strict integer indices,
method/version/seed, ordered block identities, both hashes and an optional expected
manifest identity. Booleans cannot represent indices or numeric version fields.
Unknown RNG algorithms, methods and malformed version records are rejected.

Replay uses stored indices rather than regenerating them with the current RNG.
An older declared runtime version therefore remains replayable when its supported
method and pinned metadata are intact. Changing metadata without updating the
identity fails; an externally pinned expected digest additionally detects any
replacement with a new self-consistent record. Hashes establish byte/record
identity, not authenticity or independent origin.

A known-null comparison `resampling.replay_ref` requests fresh generation.
Unknown/unavailable replay choice is not silently treated as known-null. A known
artifact reference must resolve to an already acquired, loader-checked snapshot
whose `schema_version` is `0.1` and whose `replays` field is an array of
complete manifest objects. The collection contains one to twelve distinct ordered block sets. A requested
missing, malformed, inaccessible or mismatched replay is not replaced by new
random indices. External locators stay passive. Linked P1 quantities always use
one common manifest; other endpoints on the same ordered block set reuse it.
A different block subset receives a distinct identity and cannot impersonate the
six-block target. Reanalysis of corrected values on the same declared blocks may
reuse indices, but recomputes every replicate statistic and its operand identity.

### 12.2 Record-qualified dependence assessment

The existing `independence_assessment` referenced by
`resampling.dependence_assessment_ref` has dimension
`paired_prompt_block_resampling`, a supported-for-scope outcome, an active readable
support path, known criterion, resolvable subject/reviewer/evidence references,
and scope references covering the participating cells. Its extension is:

```json
{
  "paired_block_dependence": {
    "version": "0.1",
    "block_ids": ["P01","P02","P03","P04","P05","P06"],
    "unit": "paired_prompt_block",
    "target": "fixed_wording_suite",
    "cross_block_shared_history": {"state":"known","value":false,"evidence_refs":[]},
    "condition_pairs": ["B-A","C-A","C-B"]
  }
}
```

These are physical encodings of the adopted dependence requirement. The declared
condition-pair scope can be narrower when only some comparisons are supported.
The original evidence pass's support traversal is reused, including downstream
mock, unreadable, conflicted and corrected evidence. Record consistency does not
independently certify the judgment. Fixture assumptions remain fixture-only.

Observable shared generation groups or shared context across different included
blocks override a blanket declaration of independence. Within-block dependence is
retained by resampling the entire block. Unsupported cross-block dependence gives
an unavailable interval; no higher-level cluster estimator is substituted.
Unknown or missing support does not create an interval merely because six blocks
have names. All returned records keep `independent_validation_performed=false`.

### 12.3 Statistics, quantiles and numerical scope

Each row computes the equal-block mean for every linked component. Complete
unrounded values and exact ratios are used; binary float inputs, when present,
are interpreted as their exact represented binary values with that provenance
explicit. Original means are checked against the actual block values. P1's
`surface_gain`, `structural_gain` and `p1_proxy_gain_contrast` share the same block
set and draw; the latter must equal the first minus the second in every block.

The 0.025 and 0.975 quantiles use `h=(2000-1)*q`, giving zero-based ranks 49.975 and
1949.025. Linear interpolation is exact rational arithmetic where supplied data
permit it. Boundary equality remains equality, not a tolerance-defined effect.
Invalid/nonfinite operands, mismatched units, stale means, exact-arithmetic limit
failure and diagnosed sign/representation instability withhold the affected
linked interval rather than discarding replicates or returning an approximate
substitute. No truncated replay can qualify as the registered 2,000-replicate run.

The output is `prompt_resampling_sensitivity`, conditional on these recorded
within-block outputs. It supplies no prompt-population confidence, familywise
significance, ontology validity or total-generation uncertainty. One block retains
its descriptive number and has no interval. A separately requested descriptive
subset of at least two blocks can have its own supported range, but cannot yield a
full six-block verdict. Numerically defined quality-limited blocks remain in the
descriptive calculation with their limitations; they are never deleted to improve
an effect. A degenerate range does not imply general certainty.

### 12.4 P1/P5 outcomes

`evaluate_predictions` preserves all registered primaries and the separate
valid-only P1 sensitivity. Each endpoint requires its existing eligibility and a
supported six-block interval. Positive retention is strictly `mean>0 and lower>0`;
negative retention is strictly `mean<0 and upper<0`. A touching or crossing zero
range is inconclusive. A diagnosed precision limitation is not evaluated.

P1 is supporting only when surface gain and the gain contrast both retain positive
directions; either retained negative direction is contrary. Otherwise an evaluable
comparison is inconclusive. A positive contrast formed from two decreasing
quantities cannot establish surface growth. Clean-quality failure and adverse
valid-only sensitivity qualify the original primary; they do not replace it.

P5 separately evaluates the valid distinct-20 C-A and C-B comparisons. Both
supporting gives a supporting full pattern. With both evaluable, any contrary
member gives a contrary full pattern; otherwise any inconclusive member gives an
inconclusive full pattern. Either not evaluated makes the full pattern not
evaluated, while the narrower available member remains visible. Mixed comparator
behavior is a qualification, not a fifth top-level outcome. All-view counts,
k=5/10, thresholded support or alternative labels cannot replace these primaries.

Surface >=0.95 and eight-class registry ceiling flags survive unchanged. No proxy
switch, additional sampling, effect-size threshold or overall score is introduced.
Small positive effects remain explicitly small. Fixture outcomes retain
`fixture_only`; empirical scopes cannot be obtained by copying mock assumptions.

### 12.5 Corrective integration and retained history

P2S5-F02 reproduced a stale-input failure: changing an evidence record while
retaining the same comparison configuration could let an old comparison feed a
new resampling run. `Comparisons.input_snapshot_sha256` now binds acquired snapshot
identities, parser limits, artifact states and diagnostics. A downstream mismatch
withholds intervals, preserving old descriptive results without applying them to
the changed input. This is an input-identity repair under PLAN2 section 6.3. No
metric, denominator or evidence threshold changed. Corrected analyses must rebuild
comparisons before resampling, even when they intentionally reuse index draws.

P2S5-F01 retains the Step 4 tests' history and component-boundary assertions while
allowing the now-authorized Step 5 modules. Original test identities, arithmetic
oracles and all frozen contracts are retained. The exact failure reproduction and
before/after patches accompany the delivery. VT-39 is complete at component scope;
the other outcome/report families remain partial until their specified integrated
report tests. No Phase 2 Step 6 work is authorized by this handoff.


### 12.6 Verification binding storage

The Phase 2 matrix now stores repeated test method names through a finite explicit
string dictionary. Each indexed binding list carries its own decoded hash, and
the complete decoded matrix has a separate pinned hash. The helper expands this
representation before the unchanged catalogue, predecessor and gate checks.
All method identities, ordering, requirement assignments and history remain
identical to the retained expanded representation. No method is discovered,
imported, inferred or automatically added by dictionary expansion. Invalid indices,
booleans, duplicate references, edited pools and mismatched hashes fail closed.
The full readable decoded matrix is retained with the delivery verification files.
This is lossless QA storage; it changes no runtime or scientific requirement.

Operand fingerprints use the named `signed_hex_ratio_v1` encoding for exact
numerators and denominators. This avoids decimal integer-string expansion limits
without reducing precision or changing interpreter-wide resource limits. Stored
interval values and their exact ratios retain the original arithmetic meaning.
