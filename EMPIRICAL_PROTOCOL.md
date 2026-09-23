# StructDet-Bench external study protocol

**Current material/evidence boundary:** the shipped examples are `fixture_only`
software inputs. The toolkit implements offline preparation, supplied-record
inspection and analysis. Actual study registration, collection, external
candidate validation, independent human review and empirical findings require
their own original evidence. Creating a packet establishes none of those events.

This operating guide implements the adopted Phase 4 workflow within the frozen
[HERO_BENCHMARK_SPEC.md](HERO_BENCHMARK_SPEC.md),
[STUDY_FORMAT.md](STUDY_FORMAT.md), existing M/V/L formats and
[EVALUATION_CLOSURE_ADDENDUM.md](EVALUATION_CLOSURE_ADDENDUM.md). It changes no
structural definition, metric, denominator or evidence requirement.

## 1. Roles and activity readiness

A study custodian pins versions, retains originals and controls restricted data.
A collection operator obtains authorized original responses. A separately
qualified external validator provides the reviewed execution environment,
oracle and original test records. Actual human reviewers provide original
independent first passes; a qualified independent expert resolves disputes where
possible. An accountable claim reviewer evaluates the claim-specific evidence
and disclosure limits. Record identity, relationships, exposure and assistance
for each actual participant through the controlled roster/evidence channel.

A single supplied JSON identity does not authenticate a person. Two model agents
or two aliases of the same person do not satisfy two-human independence. Preserve
first passes before discussion and retain unresolved disagreement after
adjudication. Source labels, hashes and declared approvals alone cannot supply
independence or execution evidence.

| Activity | Required concrete basis before carrying it out |
|---|---|
| Core construction | Named task/schema/registry version, all 32 role specifications, identified constructor, artifact lineage and review route. |
| External validation | Actual operator, independently reviewed environment and trusted oracle, exact candidate and suite hashes, containment/resource controls and evidence retention. |
| Human review | Qualified real participants, identity and relationship evidence, original-first-pass procedure, exposure assessment and authorized communication route. |
| Pilot collection | Explicit optional P00 registration, chosen deployment and controls, exact prompts, eligible operator, bounded spend and retry/export procedure. |
| Main collection | Fixed P01-P06 order and original 72 calls/360 positions, prospectively scoped registration or disclosed timing limitation, tested export workflow, concrete deployment and authorization. |
| Analysis | Current original records, eligible evidence and explicit compatible carrier, preserved missing positions, current assignment/validity pins and original mappings. |
| Scientific release | Claim-specific qualified evidence, all disclosures/currentness, accountable claim review and applicable destination/publication authorization. |

Record these activities separately as ready, restricted, blocked or not assessed.
A parsing success, generated blank form or numeric report cannot make an
unperformed external activity ready. Step 10 prepares concrete operating packets;
Step 11 performs only an activated, resourced and authorized scope. A software
handoff can leave empirical work explicitly pending.

[ACTIVITY_READINESS.md](ACTIVITY_READINESS.md) documents the passive packet
assessment API for these six external activities. It checks concrete supplied
details and current input associations, keeps missing prerequisites visible and
assesses each activity separately. `complete_for_review` describes the packet's
contents. Operational readiness and authorization still require the applicable
real decisions and evidence.

## 2. Prepare and preserve the study inputs

Create a versioned `study.json` with exact source/task/resolution/schema/registry/
rubric pins, claim scope, requested profile, registration timing and explicit
knowledge states. Declare a finite local packet inventory with byte and record
budgets before import. Each original source, raw response, review submission and
execution receipt has its own identity, bytes, hash and provenance. Equal bytes
can belong to different original events. A redacted derivative gets a new
identity and a transformation association.

Keep unknown, unavailable and justified not-applicable states distinct. Required
missing evidence remains missing. The reader rejects undeclared/unsafe paths,
symlinks, oversized packets and malformed JSON. It does not expand archives,
fetch remote URLs or run any supplied source. Limits and canonical byte rules
are in `STUDY_FORMAT.md` §§2 and 7.

Inspect a local workspace without publishing files:

```bash
python3.13 -B -S -m structdet_bench study inspect --study STUDY.json --qualification-packet-id QUALIFICATION_ID --mapping-receipt-id MAPPING_ID
```

The optional IDs select actual inventoried records explicitly. Omit a selector
only when that corresponding packet/receipt is absent or unnecessary; the
software does not invent one. `inspect` prints a sanitized readiness tree. Its
opaque record aliases support internal report joins without publishing the
original private identity map or evidence prose. A well-formed partial study can
return exit 0 while reporting restricted evidence and unavailable conclusions.

## 3. Construct references, validate externally and review

The fixed sorting core has 32 catalog roles: 16 positive variants, eight
mechanism-preserving defects and eight specified boundary cases. Catalog slots
remain unfilled until actual artifacts and evidence exist. Preserve all eight
families, all 28 descriptor-pair reviews and W-01 through W-04, including W-03
for whole-key versus proper-digit discrimination. Names, explanations and correct
outputs alone never establish mechanism membership.

An actual validator must use the approved external envelope: deny network,
secrets, host filesystem/process access and privilege escalation; enforce finite
resources, reviewed isolation and fresh candidate state; keep the trusted
harness/oracle outside candidate control. The toolkit neither installs that
containment nor verifies its real-world suitability from an asserted flag.
Source-level task restrictions alone do not provide containment.

The fixed ordered suite has 8,995 test identities: 781 V-SMALL, 18 V-SHAPE,
8,192 V-KEY and four V-STAGE. Preserve repeated equal inputs under distinct test
IDs. Accepted tested validity requires complete original coverage plus evidenced
source/interface/operation conformance and the reviewed environment/oracle.
A decisive counterexample can support scoped invalidity. Harness failure,
incomplete coverage or a timeout without a decisive violation remains limited
or undetermined evidence. Complete suite success is bounded tested evidence.
An alternative proof route needs explicit assumptions and approved comparability.

Supply mechanism arguments and functional validation evidence separately.
Preserve full-log identities, coverage order, actual artifact associations and
which packet contents or external attestations were checked. A short coverage
summary cannot stand in for required full logs.

Each of the 32 core artifacts needs two independent actual human initial
reviews, at least 64 item-level first passes. Export blind material with explicit
artifact IDs and separate fresh destinations:

```bash
python3.13 -B -S -m structdet_bench study export-review --study STUDY.json --artifact-id ARTIFACT_ID --review-kind core --output-dir NEW_PUBLIC_DIR --restricted-output-dir NEW_RESTRICTED_DIR
```

Repeat `--artifact-id` as needed. Use `sampled_output` for original output audits.
The public export has instructions, a blank form and randomly pseudonymized exact
artifact bytes. The restricted map retains original IDs, selection positions,
related records and supplied rosters. Its actual public inventory is listed in
`review_instructions.json`. Optional `--pack-id` accepts only a public opaque
`pack-<32 hex digits>` join key. Exporting sends no material to anyone. The restricted map is committed first.
If public publication fails, the error reports both destination states and an
already committed restricted map can remain. Inspect the reported state and
destinations before choosing new paths; do not assume that failure removed
committed evidence.

Record unavoidable source/content clues and previous exposure; pseudonyms cannot
undo either. Maintain access history through the controlled operating process.
Import each original review submission before any amendment or adjudication.
Record membership and validity independently; preserve legitimate unresolved,
unclassified, undetermined and not-assessed decisions. Keep each revision and
its superseded original.

## 4. Collect, extract and audit original positions

The registered main design contains six blocks, three conditions and four
coordinated calls per cell: 72 calls and 360 planned candidate positions. Optional
P00 adds six calls and 30 positions. Each call requests five candidates and an
8,192 model-token output allowance; maximum declared output allowances are
589,824 main or 638,976 with pilot. These limits are distinct from actual output,
input, hidden reasoning, compute and monetary expenditure, whose knowledge
states must be retained.

Use the exact HERO prompts and order. A and B share byte-identical visible
prompts within a block; their requested temperatures are 0.4 and 1.0. C uses the
registered mechanism-variation clause with A's controls. Keep requested, exposed,
actual and hidden controls separate, including system/wrapper knowledge, cap
semantics, deployment identity/drift, timestamps, request IDs, selection and
observable retries. A deployment without meaningful temperature control cannot
support registered P1. Any narrower scope needs an explicit registration.

Preserve the original response before extraction. Apply the exact heading/fence
rules and zero-based, end-exclusive byte ranges. Retain source whitespace,
comments, extras, empty or truncated emitted bodies and missing positions. Never
repair code, choose a preferred fence, renumber candidates or replace failed,
refused or inconvenient observations. Retries remain separate history and do not
allocate replacement main positions. A failed call without a response produces
zero realizations while preserving its five planned positions.

Fixed k=5, 10 and 20 prefixes use original group/position order. Missing positions
do not compress later observations into an earlier prefix. Nineteen realizations
cannot provide a complete distinct-20 result.

The systematic audit selects one fixed position per main group using
`1 + ((b + c + g - 3) modulo 5)`, with b=1..6, A/B/C mapped to c=1/2/3 and g=1..4.
Missing selected artifacts remain missing opportunities. Targeted audit also
covers relied-upon disputes, novel/hybrid cases, challenged essential evidence,
classes observed once or twice within a 20-realization cell and available
class/condition coverage. Deduplicate original artifact identity while retaining
all selection reasons; at most 360 main artifacts are reviewed. These audits add
no generator observations and estimate no random population error rate.

## 5. Compile, analyze and handle corrections

`study prepare` imports an explicitly declared whole legacy carrier. Every
referenced local payload must be in the acquired finite inventory. Known study,
method, frame, collection, extraction and current evidence facts must agree;
original selected events and fixed denominators cannot disappear. Explicit typed
mappings preserve the operational-to-numerical associations. The prepared bundle
has `bundle.json` at its root and exact original payload bytes. A differently
named original carrier or a payload path that collides with any companion
filename cannot be published as a numerical study by this CLI. Explicit
readiness-only mode can describe a well-formed publication-layout restriction
without rewriting the original bytes.

```bash
python3.13 -B -S -m structdet_bench study prepare --study STUDY.json --qualification-packet-id QUALIFICATION_ID --mapping-receipt-id MAPPING_ID --output-dir NEW_PREPARED_DIR
python3.13 -B -S -m structdet_bench analyze --bundle NEW_PREPARED_DIR/bundle.json --output-dir NEW_REPORT_DIR
```

Normal preparation without an eligible carrier returns 2 and publishes no new
bundle. A well-formed readiness gap can be exported with `--readiness-only`;
this always creates only `study_readiness.json`, `study_readiness.md`,
`provenance_map.json` and `compilation_manifest.json`, even if a carrier could be
compiled. Malformed or contradictory input remains an error in either mode.
Destinations must be fresh, with existing parents. Publication is atomic and
refuses overwrite; the controlled prepared package can contain raw evidence.

Existing `analyze` produces exactly `report.json`, `report.md` and
`run_manifest.json`. Longitudinal explicit replay uses `--replay-manifest` on
`validate` or `analyze`; comparison replay uses the declared comparison
`replay_ref`. Input, method, software, registered unit order and complete stored
index identities must match. Missing/corrupt requested replay fails without a
fresh sampling fallback. See the root README for runnable L replay commands.

Correction incidents retain the challenged subject, action status, authority,
actual evidence, affected records/cells/comparisons, replacements, rollbacks and
reanalysis references. Proposed action never becomes performed action. Current
challenges and revisions invalidate dependent results; fresh evidence and current
mappings are required. A schema/core change triggers the affected condition and
comparison review. Keep previous reports and carrier identities, then recompute
the entire selected registered analysis. An M-only reanalysis cannot close
outstanding P1/P5 or longitudinal obligations.

## 6. Disclosures and claim review

Study readiness JSON and Markdown share one sanitized disclosure tree. Material
role, evidence status, scope and version precede numerical summaries. Count
planned calls/positions, responses, extracted realizations, selected populations,
classifications, validity and audit coverage with explicit separate denominators.
Do not convert unknown spending or missing evidence into zero.

| EC disclosure | Required retained distinction |
|---|---|
| Claim and deployment scope | Exact study/version and claim/system/period; unverified supplied scope remains an assertion. |
| Structural relations | Represented relations, omitted relations and relevant resolution/registry limits. |
| Source and transformation lineage | Original source identity, transformations, contribution and acquisition/evidence limits. |
| Contamination and exposure | Known prior access, overlap, assistance, hidden context and unresolved exposure. |
| Evaluators and bias controls | Qualified roles, relationships, independence evidence, blinding and exposure limits, with private identities controlled. |
| Low-frequency and high-severity results | Per-class information only where supplied/supported; missing severity assessment stays unavailable. |
| Long-horizon, recovery and override evidence | Actual supplied relevant evidence; justified absence of a longitudinal claim can be inapplicable. |
| Live or field evidence | Actual field evidence and continuing contact where required; a recorded model response alone supplies neither. |
| Correction path and actual action | Proposed, performed, rejected and unresolved action; evidence, dependency invalidation and remaining recomputation. |
| Currentness or expiry | Assessed date, expiry and scoped basis, or an explicitly unresolved currentness judgment. |

Assess the five EC conditions separately: Structural Validity, External Presence,
Source Integrity, Tail Retention and Corrective Capacity. They are conjunctive
for an operational openness claim. The four architectural components, Stable
Core, Rotating Structural Frontier, External Incident Stream and Versioned Tail
Registry, retain their own content/version states. Four satisfied conditions do
not compensate for an unresolved fifth. Required missing human review or field
evidence cannot become not applicable.

Preserve contrary, null, mixed and inconclusive registered outcomes. P1 and both
P5 contrasts, primary and sensitivity populations, uncertainty conventions,
observed/expressible/latent distinctions and existing M/V/L evidence gates remain
unchanged. A record-consistent import, passing fixture or complete numerical
report cannot establish an empirical conclusion or globally close UD-006.
UD-007's latent diagnostic remains deferred.

## Concrete operating preparation

[The HERO preparation package](operations/hero_readiness/README.md) separates core
construction, external validation, human review, optional pilot, main collection
and scientific release. It supplies exact specification identities, intended
prompts and slot records. Actual operators, independent reviewers, deployment,
reviewed execution environment, prices, budget and time windows remain missing.
All six external activities are `not_performed`. Source bytes and format checks
do not establish prospective registration, empirical evidence or independent
validation. Missing main resources do not prevent core-only preparation.
