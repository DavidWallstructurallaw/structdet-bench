# Passive collection records, version 0.1

The existing `collection_ledger` and `extraction` records in `STUDY_FORMAT.md`
remain unchanged. `study_collection` adds exact planning and a typed JSON
attachment called `collection_submission`. This attachment retains the original
ledger row and carries details that the earlier actual-controls summary cannot
represent. Parsing and byte matching establish supplied-record consistency.
External authenticity and scientific qualification remain unperformed.

## Exact plan and prompt bytes

`prompt_bytes(block_id, condition)` returns the HERO section 7.2 strings joined
by exactly two LF bytes between opener, common task, condition clause and output
format. The common task preserves its internal blank lines. The assembly is
UTF-8, has no BOM, uses LF, and has no final newline after the output-format text.
A/B prompts for a block are byte identical. C changes only the condition clause.
There are no model names, algorithm lists, reference implementations or desired
metric values in these prompts.

`collection_plan(phase="main")` returns an immutable mapping. It enumerates group
g=1..4, then block b=1..6, then permutation `(b+g-2) mod 6` from
`ABC, ACB, BAC, BCA, CAB, CBA`. Each row has a stable descriptive slot ID, explicit
registered call order, positions `[1,2,3,4,5]`, and cell sample orders
`5*(g-1)+i`. File order cannot redefine the sample order.

| Phase | Blocks | Groups per cell | Calls | Positions | Planned output allowance |
|---|---|---:|---:|---:|---:|
| Main | P01-P06 | 4 | 72 | 360 | 589824 model-token units |
| Optional pilot | P00 | 2 | 6 | 30 | 49152 model-token units |

The pilot's explicit preparation order uses b=0 in the same rotation, CBA then
ABC. HERO fixes the main order; this pilot order is an implementation convention.
The two phases have disjoint identities and reports. Main comparisons never use
pilot outputs. These ceilings match planned calls, candidate positions and
output allowance; they do not establish equal actual tokens, compute or cost.

## Typed original submission

Declare one locally supplied JSON file per original submission in the finite
study packet inventory with `purpose="evidence"`, `format="json"`, a known SHA256
and byte size, and a safe local path. The file has exactly these top-level fields:

| Field | Meaning |
|---|---|
| `kind`, `version` | `collection_submission`, `0.1` |
| `study_id`, `study_version`, `fixture` | Scope and explicit fixture status |
| `record` | Exact original `collection_ledger` record, including common fields |
| `requested_controls` | Same eleven named knowledge fields as the ledger controls |
| `enforced_controls` | Same eleven names, each a Boolean knowledge field |
| `cap` | `unit`, `tokenizer`, `convention` as text knowledge; `includes_reasoning`, `enforced` as Boolean knowledge |
| `context` | Fields listed below |
| `deployment_window` | `start` and `end`, each timestamp knowledge |
| `evidence_refs` | Existing typed references resolving to this version and scope |

All knowledge values use the existing known/unknown/unavailable/not_applicable
grammar with reasons for nonknown values. No field is optional. The attached
record must match the envelope record exactly; a packet cannot rewrite its
attempt status, response association or controls. Duplicate submissions are
rejected. The bounded original file remains available for audit.

The eleven control names are `temperature`, `top_p`, `presence_penalty`,
`frequency_penalty`, `seed`, `output_allowance`, `cap_semantics`, `fresh_context`,
`tools_requested`, `hidden_controls` and `wrapper_knowledge`. Ledger controls
describe actual observations; the added carrier separates requests and evidence
of enforcement. Known no-fixed-seed is an explicitly known JSON null. It differs
from an unknown seed policy. Equivalent exact decimal lexemes compare
numerically; different absence reasons do not create an observed control change.

The proposed settings are temperature 0.4 for A/C and 1.0 for B, top-p 1.0,
penalties zero where exposed, no user-fixed seed, output allowance 8192, fresh
context and no tools requested. The normalized cap unit for this design is
`model_token`. Other actual units remain visible and restrict matching. The
tokenizer and visible-only versus reasoning-inclusive convention must be
recorded. Unsupported or unenforced temperature cannot become a verified
temperature intervention. A narrower A/C comparison requires its own explicit
scope and qualification.

`context` contains:

- `visible_system_instruction_ref`: knowledge of an artifact reference; a known
  reference must resolve within the current scope/version. A declared absence is
  `not_applicable` with a reason. A supplied visible instruction remains a
  disclosed protocol change requiring assessment.
- `platform_context` and `reasoning_configuration`: text knowledge. Unknown
  ledger `hidden_controls` or `wrapper_knowledge` remains a restriction even when
  a platform description is supplied.
- `previous_outputs_supplied` and `reference_material_supplied`: Boolean
  knowledge, preserving history and exposure limits.
- `output_selection`: knowledge of `none`, `reranked`, `best_of`, or `other`.
- `automatic_retries`: nonnegative-integer knowledge. Unknown is not zero.
- `duration_ms`: nonnegative exact-number knowledge.

## Provider-neutral export requirements

The independently operated collection system must export the exact visible
user/system bytes, raw response bytes, attempt and request IDs where accessible,
timestamps, failure/refusal/termination status, and observable retries. Preserve
the first response and its planned slot even if later material is more useful.
Disable automatic retries where possible; disclose inaccessible retry history.

Record actual interface parameter names and meanings in supporting evidence,
including whether temperature is exposed and enforced, token-cap unit and
reasoning inclusion, hidden wrappers, selection/reranking, deployment/checkpoint
identity, drift observations and one collection window. The ledger's drift
text values `none` or `no_change_detected` report supplied absence assertions;
other or unknown values require assessment. Neither string independently proves
deployment stability.

Record input, output and hidden reasoning tokens separately; retain compute,
charges and currency only where known. Unknown quantities are never summed as
zero. `actual_attempt_records` counts supplied succeeded/failed rows and
cancelled rows with a known attempt identity. `supplied_attempt_records` also
retains unknown attempt-status rows, separately counted as
`unknown_attempt_status_records`. None of these counters authenticates a remote
event.

The preregistration record retains declared status, original time, evidence and
exposure. Chronology examines every retained current-version attempt in the
selected phase, including retries and revisions. A supplied time preceding all
attempts produces `supplied_times_consistent`, which still requires external
authentication. A later/equal registration time reports
`retrospective_or_simultaneous`; locally created hashes cannot repair it.

## History, selection and bounded inspection

`inspect_collection(load_study(path), phase="main")` reads no extra paths. It uses
the loader's immutable snapshots and independently verifies the actual used
bytes against their declared identities. Existing no-follow acquisition,
per-file, total-byte, line, depth, number and record bounds remain in force.
All acquired attachment records count toward the study budget, including unused
JSONL rows; nested original ledger rows and extracted positions/extras also
consume the logical budget. Overruns require an explicit partitioned import.

Every supplied attempt across retained versions and phases remains in history.
A slot with several possible original attempts is withheld, with no success
preference. Explicit retry/revision rows cannot replace the original. Unknown
retry or supersession provenance permits tentative descriptive inspection but
withholds matched prefix eligibility. Reuse of one actual attempt ID across
slots or one original response artifact ID across attempts is rejected. Distinct
response artifact identities may legitimately have equal bytes or share
deduplicated storage; storage equality alone does not merge events or prove
their independence.

The output always retains the selected phase's full planned slot population.
No response means no realized candidates. `selected_realizations` counts actual
identified emitted positions, including emitted empty/malformed bodies under
the extraction rule. `unselected_regions` includes all preserved extra raw
regions; `extra_realizations` counts only sections with an identifiable
unrequested candidate heading. Unselected prose and refusal preambles never
become candidate observations. None of these fields assesses functional
validity or structural membership.

Existing supplied extraction records are checked against the original response
identity, exact selected bytes, headings, fences, offsets, completion status,
required limitations and unselected-region associations. Later descriptive
limitations may be added; required observed limitations cannot be removed.
See [EXTRACTION_FORMAT.md](EXTRACTION_FORMAT.md) for the pinned extraction grammar.

The permanent [canonical suite](../../../VERIFICATION.md) owns these behaviors.
No phase-specific gate, historical runner, minimum test count or new approval
identity is introduced.
