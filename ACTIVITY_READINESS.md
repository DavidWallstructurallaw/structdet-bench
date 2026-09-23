# Activity preparation packets

An activity packet describes the supplied details and missing resources for six
external activities. Its assessment helps a person review the proposed work.
`complete_for_review` means the required packet fields and associations are
present. It does not authenticate evidence, establish operational readiness,
grant permission or start an activity.

[The concrete HERO operating package](operations/hero_readiness/README.md)
provides six activity packets and explicit resource gaps. All external
activities remain `not_performed`. The example below is a fixture with missing
resources. No operator, provider, budget or reviewer is
invented. Ordinary study inspection and analysis continue to use the commands in
[README.md](README.md).

## Assess a packet

```python
from structdet_bench.study_records import load_study
from structdet_bench.study_readiness import inspect_activity_packet
from structdet_bench.local_io import ReadLimits

loaded = load_study("STUDY.json")
limits = ReadLimits()
with open("ACTIVITY_PACKET.json", "rb") as stream:
    assessment = inspect_activity_packet(
        loaded, stream.read(limits.max_file_bytes + 1), limits=limits)
print(assessment.json_bytes.decode("utf-8"), end="")
```

The assessment exposes `as_dict()`, `json_bytes`, `diagnostics`, `has_errors` and
`exit_code`. Exit 0 can contain readiness gaps; exit 2 means malformed or
contradictory input. The immutable acquired study snapshot is reused without
reopening its files. No supplied program, attachment or instruction is executed.

## Make a fixture with explicit gaps

Run this from the project directory in the supported Python environment. It
prints an assessment and creates no output files. It imports no test helpers.

```bash
python3.13 -B -S - <<'PY'
import json
from structdet_bench.study_records import load_study
from structdet_bench.study_readiness import (
    ACTIVITIES, ACTIVITY_REQUIREMENTS, COMMON_REQUIREMENTS,
    MINIMUM_DEPENDENCIES, inspect_activity_packet,
)

loaded = load_study("examples/phase4/offline/readiness_only/study.json")
assert not loaded.has_errors, loaded.diagnostics
study = loaded.packet.data
registration = next(r.data for r in loaded.packet.records
                    if r.record_type == "study_registration"
                    and r.study_version == study["study_version"])

def missing(state="unknown"):
    return {"state": state, "reason": "No operational resource supplied in this fixture."}

activities = []
for activity in ACTIVITIES:
    activities.append({
        "activity": activity, "disposition": "planned",
        "omission_reason": missing("not_applicable"),
        "action": missing(), "responsible_operator": missing(),
        "authorization_ref": missing(), "time_window": missing(),
        "input_pins": [],
        "dependencies": list(MINIMUM_DEPENDENCIES.get(activity, ())),
        "requirements": [
            {"requirement_id": name, "basis": missing(), "evidence_refs": []}
            for name in COMMON_REQUIREMENTS + ACTIVITY_REQUIREMENTS[activity]
        ],
        "collection_limits": missing(
            "unknown" if activity in ("pilot_collection", "main_collection")
            else "not_applicable"),
    })
packet = {
    "kind": "activity_readiness_packet", "version": "0.1",
    "study_id": study["study_id"], "study_version": study["study_version"],
    "scope": dict(registration["scope"]), "activities": activities,
}
raw = (json.dumps(packet, indent=2) + "\n").encode("utf-8")
assessment = inspect_activity_packet(loaded, raw)
assert assessment.exit_code == 0, assessment.diagnostics
print(assessment.json_bytes.decode("utf-8"), end="")
PY
```

The expected top-level status is `assessed`. Each of the six rows has
`packet_status: gaps_recorded`; `execution_authorized` and empirical/authentication
flags remain false. The source example is descriptive, so planned collection also
reports an unsupported collection-design gap. No 72-call design is silently
imposed on that study.

## Packet fields and evidence

The version 0.1 grammar is `ACTIVITY_PACKET_SCHEMA` in
`structdet_bench/study_readiness.py`. Every declared field is required; unknown
fields, duplicate JSON keys and malformed values fail. The envelope has exactly
one row for each activity below, with the current study identity, version and
registration scope.

| Activity | Required basis beyond shared source, scope, storage and provenance details |
|---|---|
| `core_construction` | Core role specifications, constructor lineage and review route |
| `external_validation` | Candidate/suite identity, containment, oracle, finite resources, calibration route and original receipts |
| `human_review` | Qualifications, relationships, original first passes, exposure and communication route |
| `pilot_collection` | Deployment, control/cap semantics, exact messages/slots, retry/failure/stop policy and original exports |
| `main_collection` | Collection details above, registration freeze and core qualification |
| `scientific_release` | Claim evidence, EC/currentness disclosures, correction route, claim reviewer and destination scope |

Each row declares its action, responsible operator, authorization reference, time
window, exact input packet hashes, dependencies, requirement bases/evidence
references, disposition and collection limits. Knowledge values use the existing
`known`/`unknown`/`unavailable`/`not_applicable` wrappers. A mandatory missing value
or evidence reference remains a gap when marked not applicable. Known references
use `record_type`, `record_id` and `record_version`; they must resolve in the
current study scope. An authorization reference is a supplied record to review,
not an independently verified grant of authority. Keep credentials out of packets.

Superseded references are rejected. References and input packets affected by the
existing operational correction graph create named gaps. This check reuses the
bridge's derivation rules without compiling a bundle. Evidence-qualification
packet extensions and actual independence remain `not_assessed` here. A complete
packet cannot replace the qualification and claim review in the study workflow.

Validation and human-review preparation declare a dependency on core material.
Main collection declares core construction, external validation and human review.
These are prerequisites to the proposed activity, not a demand that downstream
work has already happened before preparing its packet. Missing main resources
do not block core preparation. A scientific release for a narrower core claim
does not automatically require main collection.

Only `pilot_collection` can use `disposition: omitted`, with a known omission
reason. Main collection cannot make this optional pilot mandatory. An invalid
dependency cycle or contradictory omission is rejected.

Planned collection in this packet version supports the explicitly registered
`sorting_abc` / `hero_sort_abc_v1` design. Limits include maximum calls, positions,
output tokens, monetary ceiling, currency and stop behavior. The pilot caps are
6 calls/30 positions; main caps are 72/360. Aggregate output ceilings are 49,152
tokens for pilot and 589,824 for main, derived from 8,192 times the registered
call count. This API checks aggregate ceilings. These are upper bounds, not measured
usage or authorized spending. Known zero remains zero; unknown cost stays unknown.
Other designs cannot become complete for collection through this packet format.

## Bounds and public output

`ReadLimits` can lower the established byte, line, depth and record budgets.
Aggregate bytes include the new packet and already acquired study data; acquired
snapshots also obey the per-file limit. Record accounting includes every JSON
object in the new packet, study records and checked attachment records. Long
arrays and malformed objects are checked before detailed shape diagnostics;
diagnostics are capped at 128. Exceeded limits reject input without truncating it
into an apparently complete packet.

Public output hashes free text, operator identities and private values, and uses
deterministic aliases for record joins. Exact originals remain in the controlled
input packet. These aliases are not anonymity or authentication. A present
snapshot with contradictory bytes, hash or size is malformed; genuinely missing
bytes remain an explicit gap. A passing fixture establishes software behavior
only. See [EMPIRICAL_PROTOCOL.md](EMPIRICAL_PROTOCOL.md) for the actual external
workflow and evidence responsibilities.
