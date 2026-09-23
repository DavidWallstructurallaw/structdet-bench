# HERO operational preparation

This reconstructed Step 10 packet is a reviewable set of plans and explicit resource gaps for `hero-operational-preparation/prep-v1`. All six external activities are **`not_performed`**. The original interrupted Step 10 files were unavailable after workspace maintenance; these files are newly reconstructed from the verified Step 9 software and adopted specifications. No lost file's exact byte identity or lost test run is claimed.

## What to open

| File | Purpose |
|---|---|
| `core_construction.md` | All 32 roles, construction lineage/rights and later qualification. |
| `external_validation.md` | Exact 8,995-test suite, proposed containment/resources and missing execution evidence. |
| `human_review.md` | Actual two-human first-pass requirements, blinding, relationships and original records. |
| `pilot_collection.md` | Optional six-call P00 activity, kept separate from main. |
| `main_collection.md` | Fixed 72-call/360-position main plan, freeze and missing resources. |
| `scientific_release.md` | Proposed main P1/P5 claims, review, EC disclosures and publication gaps. |
| `readiness_gaps.json` | Explicit missing operators, resources, evidence, budgets and activation scope. |
| `input_manifest.json` | Byte identity of 17 actual preparatory inputs. |
| `study.json` | Passive study envelope with draft registration, source artifacts and six blocked activities. |
| `activity_packet.json` | Strict aggregate packet used by the existing readiness API. |
| `activity_assessment.json` | Reconstructed packet's fresh passive assessment, with six gap records. |
| `collection/main/`, `collection/pilot/` | Deterministically materialized exact messages, slots and controls. |

`material_role: descriptive` describes this unexecuted preparation envelope; it does not claim an observed descriptive study. `evidence_policy: adjudicated_import` selects the existing evidence rules for future supplied evidence; it does not claim adjudication has occurred. Registration remains `not_registered`. All source artifacts are plans/specifications, and no `candidate` or accepted core artifact is present. `blocked` means the external action is unavailable with current resources, while its packet is prepared.

## Inspect locally

Run from the repository root using the supported Python environment:

```sh
python3.13 -B -S -m structdet_bench study inspect --study operations/hero_readiness/study.json
python3.13 -B -S -m structdet_bench study prepare --study operations/hero_readiness/study.json --readiness-only --output-dir hero-readiness-output
```

The output directory must be new. Readiness-only export writes four companion files with `analysis_bundle_created: false`. It sends no requests and executes no candidate code.

Assess the concrete six-activity packet with the existing API:

```sh
python3.13 -B -S - <<'PYCODE'
from pathlib import Path
from structdet_bench.study_records import load_study
from structdet_bench.study_readiness import inspect_activity_packet
root = Path('operations/hero_readiness')
loaded = load_study(str(root / 'study.json'))
assert not loaded.has_errors, loaded.diagnostics
result = inspect_activity_packet(loaded, (root / 'activity_packet.json').read_bytes())
assert result.exit_code == 0, result.diagnostics
print(result.json_bytes.decode('utf-8'), end='')
PYCODE
```

Expected: `status: assessed`, six `packet_status: gaps_recorded` activities, all execution/empirical/authentication flags false. Exit zero reports valid records with gaps, not permission or operational readiness. Exact source prose is retained in the input, while the public assessment hashes private values; those hashes do not authenticate anyone.

## Preparation, dependencies and limits

Core-only preparation can proceed while main is blocked. Both actual validation and human review require real core bytes. Pilot execution would use the same core/validation/review prerequisites, but pilot preparation is independent and pilot omission never blocks main. The proposed main scientific release depends on main collection; a later narrower core-only claim needs a separately scoped/versioned packet.

Known design ceilings are 6 pilot calls/30 positions/49,152 declared output units, and 72 main calls/360 positions/589,824 declared output units. Actual provider controls, cap units, hidden reasoning/input costs, prices, currency and maximum expenditure remain unknown. Therefore the strict packet's collection-limit object is unknown, with the known design caps preserved separately. Unknown spending is not zero; no expenditure is authorized.

The user authorized local preparation and recovery. No actual external operator, reviewer, provider or hostile-code environment has been selected or invented. The proposed 512 MiB/30 CPU-second/60 elapsed-second envelope is uncalibrated. It does not authorize running candidates on the analyst host. No original model export, human judgment or empirical result exists here. Original plan language describes the historical proposal; subsequent adoption and the active verification-consolidation policy govern engineering work.

No new runtime, permanent phase-specific runner, approval hierarchy or numerical definition is introduced. Passing format tests and the retained Step 9 scientific regression establish software behavior within their recorded scope. Empirical evidence remains pending. The separately retained Step 11 disposition and final software handoff must preserve this distinction.
