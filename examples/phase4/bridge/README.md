# Compile an explicitly supplied study profile

The Python API now checks a study's exact legacy input carrier and compiles it
for the established M-only, `hero_sort_abc_v1`, or
`structdet_longitudinal_v1` engine. The offline study CLI is Step 8 work.

```python
from structdet_bench.study_records import load_study
from structdet_bench.study_bridge import compile_study, analyze_compilation

study = load_study("study.json")
compiled = compile_study(
    study,
    qualification_packet_id="qualification",  # Explicit inventoried packet
    mapping_receipt_id="mapping",              # Explicit current ID mapping
)
summary = compiled.as_dict()
if compiled.compiled:
    analysis = analyze_compilation(compiled)
    analysis_receipt = analysis.compilation_receipt
```

Omit either optional selector only when no corresponding new qualification or
operational mapping is supplied. Selectors never auto-pick a packet. An absent
selector cannot authorize a conflicting observation or an accepted assignment.
The result contains immutable `files` and `bundle_path`; these are the complete
validated legacy bundle, retaining exact original names and bytes. Neither API
publishes user output. The analysis result retains the existing JSON, Markdown
and run-manifest bytes plus a separate compilation/analysis receipt.

## Required input

Use `STUDY_FORMAT.md` sections 8.1 through 8.5. The known
`study_registration.protocol.legacy_profile_input` identifies an `artifact`
containing the entire existing bundle declaration. Inventory every record file
and every readable local artifact used by that declaration. Paths resolve from
the carrier's directory inside the finite acquired inventory. No undeclared
host file or external URL is fetched. The original legacy byte and record
limits still apply independently to the compiled set.

Supply all source pins, the selected profile, study/material/evidence-policy
identity, and exact frame/protocol versions. Known frame text and controls must
agree. Unknown operational metadata preserves the carrier's supplied values.
Missing required legacy fields produce a field-level mapping failure and an
empty output set. A well-formed missing carrier has exit code 0 with a withheld
conversion; a contradictory or malformed conversion has exit code 2.

An explicit `compilation_receipt.id_map` connects new operational calls,
extractions, artifacts, judgments and validation receipts to legacy IDs. This
input is a proposed mapping; its claimed success flags supply no authority.
The compiler checks target existence/types, exact original artifact identity,
sample/group/position associations, planned denominators, selected order,
requested and actual comparison controls, and qualified membership/validity.
A known fact cannot disappear into legacy unknown, a smaller selected subset,
a replacement event, or another model/condition. Rejected evidence withholds
the conflicting bundle without silently changing the chosen legacy decision.
Failed retries remain separate attempts and acquire no new main positions.
An over-budget supplied history retains its observations and a claim restriction.
Rejected conversions have an empty output inventory and a withheld disposition.
Unresolved candidate classes and review-status nuances remain in the exact
carrier under its original schema.

A complete carrier can independently contain its own old evidence/support
records. They pass the existing evidence gates. The operational envelope adds
no implied human judgment to them. Stipulated fixtures retain fixture policy
and role. Real evidence-shaped input remains subject to authentication and
accountable substantive review. Numerical availability never establishes an
empirical conclusion or operational openness.

## Revisions and replay

Superseded source bytes, reviews and validation receipts invalidate their
actual dependency closure. An open correction challenge also withholds affected
evidence. Lineage-only links preserve provenance without supplying a dependency.
Replacement links do not automatically qualify new material. New sources need
new byte-bound evidence; new selected decisions need their explicit mapping.
Schema/core revisions identify all 18 A/B/C cells for review and require fresh
qualified mappings before old labels can enter a revised carrier.

`corrections` distinguishes invalidated records, affected artifacts/cells,
original outputs, proposed/performed declarations, and comparisons needing
recalculation. A supplied performed declaration remains unauthenticated.
Stable Core, Rotating Frontier, External Incident and Tail Registry inventories
retain separate versions and affected references. They supply no substitute for
the five EC conditions checked by the evidence module.

`analyze_compilation` runs the entire selected carrier through the existing
engine, retaining both classified views, P1 and both P5 endpoints, restrictions,
uncertainty and contrary outcomes. Its receipt records actual completion and
which registered comparisons remain pending. Existing bundles and reports are
never overwritten.

For longitudinal replay, pass the original run-manifest bytes as
`replay_manifest_bytes`. Reuse an explicitly chosen `run_id` if exact report
identity is required. Bad or empty replay bytes propagate failure; they never
start a fresh resampling run. A supplied longitudinal carrier must contain the
existing fourteen record collections with its actual declared identities and
observations. If both carrier selectors are used, they must identify the same
exact input bytes. A/B/C groups never create training rounds or interventions.

## Fixture verification

`tests/test_study_bridge.py` authors operational fixtures and compares compiled
results with independently supplied old bundles. The mixed M fixture retains
five positions, three classified samples and one valid classified sample,
including invalid-but-classifiable and valid-but-unresolved observations.
The existing full A/B/C and longitudinal fixtures provide exact engine and
replay equivalence checks. The delivery companion includes a materialized
operational fixture, its compiled bundle, field map and analysis receipt.
These are software fixtures, with no actual collection, candidate execution,
human review, or independent empirical validation.
