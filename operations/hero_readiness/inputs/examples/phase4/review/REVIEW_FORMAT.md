# Passive review packet contract, version 0.1

## Scope

This contract implements Phase 4 Step 4 and P4-W12 through P4-W16. The unchanged
`STUDY_FORMAT.md` sections 6.6 and 6.7 define the authoritative `human_review` and
`adjudication` record fields. `HERO_BENCHMARK_SPEC.md` sections 3 through 6 and
`EVALUATION_INTEGRITY.md` define the task, judgment categories and independence
requirements. This document adds a bounded representation for restricted identity
records and original submissions using existing declared evidence packets.

No part of this interface performs domain validation, contacts people, executes
candidate code, authenticates identity, infers a mechanism from an output, or
selects an agreement estimator or acceptance threshold.

## Loading and physical limits

Use `load_study(path)` and pass its `LoadedStudy` to `inspect_reviews`. Inventory
entries for the following packets use existing `purpose: "review"` and
`format: "json"`. Each packet must be declared before acquisition and have a
known SHA-256 and size for local verification. External, absent or unverified
packets remain unavailable. Nothing is fetched automatically.

The inherited limits remain 16 MiB per file, 64 MiB per import, 1 MiB per JSON
line, 100,000 records, depth 64 and 1,024 characters per numeric token. Logical
roster rows and schema-issue rows also count against the study's declared record
budget during review inspection. Generated public and restricted output is
jointly bounded. Duplicate JSON keys, unknown fields, nonfinite numbers,
unpaired surrogates, traversal and symlinks are rejected by the inherited
parsers and snapshot reader. Source bytes are rehashed before reliance.

Below, `K(type)` uses the existing explicit knowledge grammar: a known value has
exactly `state` and `value`; `unknown`, `unavailable` and `not_applicable` have
`state` and a nonblank `reason`. Text assertions remain assertions.

## Restricted reviewer roster

`parse_reviewer_roster_bytes(bytes, limits=None)` returns a `ReviewPacket` with
immutable `data`, diagnostics, `has_errors`, and `exit_code`.

The exact top-level fields are:

| Field | Contract |
| --- | --- |
| `version` | `"0.1"` |
| `kind` | `"reviewer_roster"` |
| `study_id`, `study_version` | Exact study identifiers |
| `fixture` | Actual JSON Boolean |
| `reviewers` | Array of the exact rows below, unique by `reviewer_id` |

| Reviewer field | Contract |
| --- | --- |
| `reviewer_id` | Pseudonymous record identity |
| `person_key` | `K(id)` for the controlled real-person association |
| `entity_kind` | `human`, `machine`, or `unknown` |
| `identity_evidence` | `K(text)` identifying controlled identity evidence |
| `qualifications` | `K(text)` preserving relevant expertise |
| `qualification_status` | `qualified`, `expert`, `unqualified`, or `unknown` |
| `relationships` | `K(text)` preserving relevant relationships and lineage |
| `relationship_status` | `independent`, `related`, or `unknown` for this scope |
| `exposure` | `K(text)` preserving exposure history and limitations |
| `machine_assistance` | `K(text)` preserving disclosed assistance |

Two aliases may share one `person_key`; they still represent one claimed person.
Different keys do not establish two real people. The reviewer object's identity
kind and four textual disclosures must exactly match the linked roster row.
An unsupported independence claim, missing ancestry/relationship disclosure, or
missing identity evidence never becomes independence. The applicable relationship
and independence dimensions must be explained in the supplied disclosures and
study record's evidence links. A shared rubric alone does not establish a shared
evaluated lineage. A human who discloses machine assistance remains a human;
the actual relationship and exposure evidence determines claim restrictions.

Raw identities, contacts and unrestricted private notes belong only in controlled
records. Public source examples contain no real identity evidence.

## Original submission packets

`parse_review_submission_bytes(bytes, limits=None)` parses these exact fields:

| Field | Contract |
| --- | --- |
| `version` | `"0.1"` |
| `kind` | `"review_submission"` |
| `study_id`, `study_version` | Exact study identifiers |
| `fixture` | Actual JSON Boolean |
| `rubric_id` | `bounded_integer_sort_validity_v1` |
| `record` | Entire exact `human_review` or `adjudication` study record |
| `prior_label_exposure` | `K(bool)` describing prior label/other-judgment exposure |
| `copied_from` | `K(id)` identifying a copied submission, or explicit nonknown state |
| `schema_issues` | Array of the exact issue rows below |

The enclosing record's `original_submission_packet` identifies this packet.
Its complete embedded record must agree with the envelope record. The original
packet's physical hash is checked, then canonical equality checks the complete
record without losing distinctions between booleans and numbers. This prevents
changing a first-pass judgment while retaining its original association. An
amendment has a new record identity, revision and original packet; its
`initial_submission_ref` preserves the initial submission. Adjudication retains
the exact initial review references. Neither changes the initial counts.

For an initial record, a known false prior-exposure value and explicit
`copied_from: {"state": "not_applicable", "reason": ...}` are required for
record consistency. Unknown copying or exposure remains restricted. A known
earlier exposed draft or alias for the same person and artifact remains
operative. Unknown chronology cannot erase exposure. Clearly later exposure
does not retroactively alter the preserved first pass. Creating another blind
pack cannot reset any exposure record.

Original bytes and identifiers provide a consistency check, not a trusted
timestamp or authenticated submission channel. Preservation of originals and
accountable external identity and independence review remain required.

## Schema issues and expert decisions

Each issue has exactly `issue_id`, nonempty unique `descriptor_ids`,
`status` (`open` or `resolved`), `resolution: K(text)`, and `evidence_refs` using
existing typed study references. A resolved declaration needs a known resolution
and nonempty resolvable evidence. Issue evidence must have the same study version
and scope as its submission.

An open issue from a preserved initial submission stays visible. A later
`resolved` assertion cannot itself erase that original contradiction. This
version conservatively retains the corresponding restriction pending an
accountable schema/case correction and scope-specific qualification review.
It does not manufacture a majority vote, independent finding, or automatic
schema revision. High agreement cannot clear an open schema boundary.

An expert decision needs a distinct claimed human identity, an `expert` roster
qualification, relevant independence evidence, known expert basis, original
submission and the preserved first passes. A core decision must identify its
complete unambiguous pair. Unknown identities, same-person aliases, missing basis
and unresolved issues remain restricted. Initial evidence restrictions propagate
to adjudication, including for sampled outputs. A third matching label alone
does not supply independent expert adjudication.

## Inspection results and denominators

`inspect_reviews(loaded)` returns an immutable `ReviewAssessment`:

- `reviews` preserves disposition and restrictions for all current human review
  and adjudication records, including sampled outputs.
- A successful inspection's `items` lists all 32 planned core roles with artifact availability,
  original review identities, separate amendment identities, original agreement,
  expert decisions and restrictions.
- `initial_agreement` records the counts below.
- `unresolved_schema_issue_ids` retains open schema findings.
- `qualification_status` is `fixture_only` or `external_authentication_required`.
- `substantive_validation_performed` is always false.

The planned denominator is 32 distinct core roles and 64 initial opportunities.
Missing material and missing submissions retain their planned positions. The
number of known artifact references is reported separately from physically
available artifact bytes. Reusing an artifact identity for two current core
roles is rejected, so one pair cannot be counted twice. Distinct artifact
identities can legitimately have equal byte hashes.

Exactly two supplied original first passes define a paired item. Three or more
are ambiguous; the tool does not select a favorable pair. Category counts retain
every initial record. A separate `pair_denominator` reports the common item set;
`planned_pair_denominator` remains 32. `record_consistent_pairs` is separate
from these supplied-record agreement counts. Exposed, uncertain or disputed
initial judgments are not filtered away to inflate agreement.

Membership comparison uses `(assignment_status, structural_class_id)`. Validity
comparison separately uses `valid`, `invalid`, `undetermined`, or `not_assessed`.
The output includes mechanism agreements/disagreements, validity
agreements/disagreements and joint agreements. Resolved-class agreements,
unresolved-category agreements and unclassified-category agreements are distinct
counts. Agreement on an unresolved category does not become an accepted class.
No percentage, coefficient, threshold or population-error estimator is selected.

The study's fixture status and any checked fixture roster/submission propagate
to inspection and review exports. Changing a parent declaration cannot promote
a fixture child into an authentic review. Complete nonfixture records still
require external authentication and substantive E03/E04 review.

## Blind output and safe publication

`build_blind_review_pack(loaded, artifact_ids, pack_id=None, review_kind="core")`
returns `BlindReviewPack.public_files` and `.restricted_files`, as immutable
path-to-byte mappings. The optional pack identity must have form
`pack-` followed by 32 lowercase hexadecimal characters. Item pseudonyms are
new random identities; source hashes are never used as pseudonyms. The selected
item order is shuffled to avoid disclosing the fixed core-role order.

Public output contains only `review_instructions.json`, `review_form.json` and
flat `item-<random-id>.txt` files. Metadata uses fixed fields, full trusted task,
rubric and descriptors, item pseudonyms and explicit limitations. It does not
interpolate original paths, artifact IDs, model/condition/role labels, roster
contents or other reviewers' decisions. Original source bytes remain exact and
may contain intrinsic identifying clues. No text is silently sanitized, renamed
or rewritten to claim perfect blinding.

`restricted_map.json` preserves original selection positions, byte identities,
artifact records, related review/exposure associations and linked restricted
rosters. New reviewer assignments and access history are empty because this
operation performs no distribution or contact. Existing exposure remains in the
associated original records.

`export_blind_review_pack` adds two destination arguments after `artifact_ids`:
public directory, then restricted directory. Parents must already exist. The
destinations must be fresh and disjoint; neither may contain the other. No-follow
parent descriptors and the existing atomic no-replace rename primitive prevent
symlink traversal and output replacement. Restricted directories/files have
modes 0700/0600, public directories/files 0755/0644.

Both destinations are checked first. The restricted directory is published
before public output. A two-directory publication cannot be atomic across all
filesystems. On failure, `ReviewPublicationError`, an `InputError` subclass,
reports `restricted_status` and `public_status` as `not_started`,
`may_have_completed`, or `completed`. A completed restricted map is retained
if public publication fails. The exporter never deletes another writer's output
to simulate rollback; choose fresh destinations for an accountable retry.
