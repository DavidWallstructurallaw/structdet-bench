# Evidence qualification attachment, version 0.1

## Acquisition and API

`structdet_bench.study_evidence` supplements the unchanged `STUDY_FORMAT.md`
envelope with one explicitly selected JSON attachment. Its packet-inventory entry
has `purpose: evidence`, `format: json`, and the actual bytes, size and SHA-256.
The bounded study loader acquires it through the existing no-follow local reader.
Every source, receipt, original review and supporting attachment is separately
inventoried. URLs, code, commands and reviewer prose remain passive data.

`parse_evidence_qualification_bytes(data, limits=None)` returns a
`QualificationPacket`. `fixed_audit_positions()` returns the immutable 72-position
main plan. `inspect_study_evidence(loaded, packet_id=None, limits=None)` returns an
`EvidenceAssessment`, with `as_dict()`, `has_errors` and `exit_code`.
No function writes files. Callers may serialize `as_dict()` through their chosen
fresh/no-clobber output route. Step 8 owns command dispatch and publication.

Exit 0 covers well-formed restricted or unresolved records. Exit 2 reports
malformed or contradictory supplied information. Original response-format errors
remain visible from the existing extractor even when partial positions and
missing audit opportunities can still be inspected. An error-bearing report
never establishes complete qualification. No error causes a fallback run.

The complete executable field grammar is the public, fixed
`QUALIFICATION_SCHEMA` constant. It uses exactly the type notation of
`STUDY_FORMAT.md` section 3. All fields are required, unknown keys and duplicate
logical identities fail, binary floats and duplicate JSON keys fail, and the
existing physical/depth/import ceilings apply. `ReadLimits` can only lower them.
The operator partitions an over-budget evidence import; the software neither
truncates logs nor increases limits automatically.

## Attachment fields

| Field | Required contents |
|---|---|
| `kind`, `version` | `evidence_qualification`, `0.1` |
| `packet_id`, `study_id`, `study_version` | Exact selected inventory and current study identities |
| `fixture` | Boolean. A true value retains fixture context even if an outer label says real |
| `pins` | Exact current registration pins, including task, mechanism partition, resolution, registry and validity rubric |
| `evidence` | Evidence rows described below |
| `qualifications` | One selected qualification per artifact, without choosing a preferred judgment automatically |
| `independence` | Scoped endpoint/dimension assessments |
| `audit_flags` | Explicit disputes, reported novel/hybrid candidates and challenged essential evidence |
| `claims` | Named claim scopes and their evidence-linked requirements/components |

An empty array declares no supplied record of that family. It never certifies that
a required activity was performed. Every reference must resolve to the current
study, record type/version and registered task/claim scope. Original records stay
unchanged; known superseded evidence is unavailable for current admission.

Each `evidence` row has `evidence_id`, `target_ref`, `subject_sha256`, `source_ref`,
`reviewer_ref`, `purpose`, `method`, `state`, `basis`, `reachable_branches`,
`constitutive_relations`, `structural_class_id`, `validation_ref`,
`supported_claim_ids`, `system_id`, and `period`.

The subject hash binds exact original artifact bytes for an artifact target.
For another record type, it binds that exact record serialized with the study
canonical serializer. Hashes preserve association and establish no truth or
independent origin. `source_ref` names a readable `artifact` of role `evidence`,
`source`, or `review`; the reviewer must also link it from the original judgment.
`state` is `active`, `challenged`, `withdrawn`, `superseded`, or `unresolved`.
Only active, readable, correctly associated essential evidence can be admitted.

`purpose` is one of `mechanism`, `schema`, `independence`, `audit`,
`external_presence`, `tail_retention`, `correction`, `protocol`, `exposure`.
Mechanism methods reuse `control_flow`, `execution_trace`, `formal_mechanism`,
`counterfactual`, `domain_adjudication`. Additional recorded methods are
`human_inspection`, `documentary`, `output_only`, `self_description`, and
`fixture_declaration`; these alone do not establish a mechanism. The declared
class must agree with the linked reviewer and selected decision. Both branch
coverage and constitutive-relation arguments must be known. An execution-trace
route also needs an associated inspected external receipt, actual supplied
observations, environment/oracle records and a linked mechanism observation.

`reviewer_ref` and `validation_ref` are knowledge-wrapped typed references.
`basis`, branch/relation arguments, and `system_id` use knowledge wrappers.
`structural_class_id` is a wrapped registered class. `period` is a wrapped object
with `start` and `end` timezone-aware timestamps; end must follow start.
`supported_claim_ids` explicitly binds evidence to requested claim IDs.

## Artifact admission and independence

A `qualifications` row contains `artifact_ref`, knowledge-wrapped `judgment_ref`,
`essential_evidence_ids`, `validation_refs`, and `independence_ids`.
The original artifact, pinned frame, concluded judgment and essential mechanism
evidence are checked separately. Draft labels, wrong hashes/classes, missing
branches, unreadable evidence, unresolved decisions and withdrawn evidence cannot
produce accepted membership. `adjudicated_import` requires a concluded
adjudication. Independent first-pass/expert qualifications are separately exposed
for stronger claims. Missing independence does not by itself erase a defensible
label-conditioned imported decision. Fixture contamination blocks real-policy
admission and all empirical claims.

Validity reuses `inspect_validation_receipt`, including actual supplied log rows,
source/conformance, suite, environment and oracle associations. A complete passing
registered suite supports the bounded `valid` record state. A decisive associated
counterexample may support `invalid`; partial logs and harness failures stay
`undetermined`. Missing receipts remain `not_assessed` or `undetermined` according
to the supplied decision. Conflicting receipts cannot be selected by outcome.
Real-policy acceptance also needs the corresponding concluded validity decision.
Validity and mechanism membership remain separate axes, including invalid but
classifiable artifacts and valid but structurally unresolved artifacts.

Each independence row contains `assessment_id`, `left_ref`, `right_ref`,
`dimension`, `outcome`, `basis`, `assessor_ref`, `evidence_ids`, `limitations`.
Dimensions are `reference_construction`, `initial_judgment`, `model_ancestry`,
`validation_method`, and `selection_and_revision`. Outcomes remain
`supported_for_scope`, `not_supported_for_scope`, `unresolved`. The endpoints,
support, assessor, source disclosures and scope must agree; distinct names or
providers supply no automatic support. Known reviewer aliases retain person
identity. These checks never authenticate people, ancestry, or observations.

## Audit and core reports

`audit_flags` rows contain `artifact_ref`, Boolean `relied_on_in_reporting`, and
`reasons`, chosen from `classification_dispute`, `novel_candidate`,
`hybrid_boundary`, `challenged_essential`. Novel/hybrid flags add a mandatory
target when relied on in reporting. Disputes and challenged essential evidence
always remain reviewable. A flagged essential challenge withholds membership.

Automatic low-count selection uses accepted class counts over each unchanged
20-position cell, including classifiable invalid outputs. Unresolved items gain
no class mass. The class-by-condition rule selects an existing occurrence and
records `not_observed` when no accepted occurrence exists. It never forces a
class into the generated sample. The distinct union is bounded by 360 original
main artifacts. Pilot records and extra response regions do not enter that union.
Same bytes under distinct original event/artifact IDs are not deduplicated into
one event. Reusing one original artifact identity in two positions is rejected.

Existing `audit_selection` records link actual initial `human_review` records.
One independently formed qualified review per available selected artifact can
complete its supplied review record. It must be tied to the correct original
position and bytes, with its original submission and roster evidence; the
initial classifier or an alias cannot count as that independent audit. An
unresolved contrary audit withholds the corresponding current assignment or
validity and remains in the queue. Duplicate selections/reviews add no counts.
An unresolved review never becomes an extra generator observation.

Core qualification preserves all 32 planned items, their two original human
first passes, disputes, adjudication, and corresponding membership/validity
evidence. Schema-defining contradictions stay visible. Role titles never impose
an expected empirical class. The core report alone does not establish the full
schema-validation argument, all descriptor pairs, or witness adequacy; these
remain explicit evidence-linked `schema_validation` claim requirements.
An artifact contradicting its proposed family or positive/defect role retains
its actual judgment and leaves that design obligation incomplete; no forced
label fills the missing reference coverage.

## Claim and component reports

Each claim contains `claim_id`, `kind`, `statement`, `artifact_refs`, `system_id`,
`period`, `requirements`, and `components`. Supported kinds are
`label_conditioned`, `validated_measurement`, `empirical_theory`, and
`operational_openness`. The statement is retained in the input and omitted from
the privacy-safe machine summary. No requested claim creates numerical results.

Each requirement has `requirement_id`, `outcome`, `basis`, `assessor_ref`,
`evidence_ids`. Outcomes are `satisfied_for_scope`, `unsatisfied`, `unresolved`,
and justified `not_applicable`. A mandatory condition marked not applicable
cannot pass. Required evidence must match its purpose and named claim.
Source-integrity and independent-validation evidence also needs the associated
scoped independence assessment, including its endpoints and dependency dimension.

| Claim | Additional required record scope |
|---|---|
| Label-conditioned | Admitted labels for the explicitly named artifacts; fixture provenance and independence restrictions retained |
| Validated measurement | `schema_validation`, `independent_validation`, core evidence, relevant sample provenance/independence and mandatory audit |
| Empirical theory | The validated-measurement requirements plus `protocol_compliance`, `exposure_controls` and registered comparison evidence |
| Operational openness | All five conditions: `structural_validity`, `external_presence`, `source_integrity`, `tail_retention`, `corrective_capacity`, tied to the named system and period |

For operational external presence and corrective capacity, associated records
must show performed consequential use/action within the period, with affected
records, original evidence and responsible review. A merely proposed action or
unused retained artifact fails that record check. The semantic adequacy and
authenticity of the supplied action still require substantive human review.

Four architectural components are reported separately: `stable_core`,
`rotating_frontier`, `external_incident`, `tail_registry`. Each has `component_id`,
wrapped `version`, `contents_state` (`supplied`, `known_empty`, `unknown`,
`unavailable`), and `artifact_refs`. Operational records must identify all four
versions. A complete component inventory does not satisfy any EC condition.

`record_complete` means that the scoped supplied links and prerequisites passed
the implemented checks. For a label-conditioned summary, disposition can be
`supported_for_scope`, limited to supplied records. Stronger fixture claims are
`withheld`. Complete external-record claims remain `restricted` with explicit
external-authentication/substantive-review requirements; missing mandatory
support leaves the claim `withheld`. Four satisfied EC conditions cannot pass
the five-condition check. No global integrity score or openness certification is
created. Every report retains `substantive_validation_performed: false`.

Public summaries contain stable join IDs and controlled reason codes, without
original review prose, private person keys, local paths or submitted commands.
Full source evidence stays in the original study workspace for authorized review.
Versioned downstream correction propagation, compilation and replayable study
publication belong to later steps; this module does not perform them.
