# StructDet-Bench

**Phase 1 Step 3: passive local inputs and imported evidence-record checks.**
Version `0.1.0.dev0`. The CLI remains **scaffold only**, with help and version.
The Python APIs provide `load_bundle` and `review_evidence`; no metric engine,
model calls, automatic structural classifier, or program execution is present.

```text
python -m structdet_bench --help
python -m unittest discover -s tests -v
python -m unittest tests.test_evidence tests.test_integrity_records -v
python tools/run_phase1_checks.py --scope scaffold
```

The final Phase 1 gate remains incomplete; **exit code 1 is expected** from
`python tools/run_phase1_checks.py` until the later M steps are implemented.
Tests check software behavior on stipulated records, not independent human
judgment, actual program correctness, or theory confirmation. UD-006 remains open.
See `INPUT_FORMAT.md` for APIs, record schemas, acceptance and correction rules.

## Governing material

Use the eleven frozen Phase 0 files, `PHASE_1_PLAN.md`, and EC-001's
`EVALUATION_CLOSURE_ADDENDUM.md` and `BASELINE_UPDATE_EC_001.md`. Their historical
approval headers remain intact. The original baseline uses SD/SI; EC-001 adds
Evaluation Closure without rewriting those documents. Step 3 does not authorize
Step 4, metrics, model collection, spending, or generated-code execution.

## Evidence handling

`fixture_only` and `adjudicated_import` are separate policies. Missing decisive
membership evidence withholds the affected assignment. Independence-only gaps
restrict a stronger claim without necessarily removing a supported imported
label. Annotation identity, exposure, validity, structural class and numeric
availability are separate concepts. All independent/scientific validation flags
remain false in these software fixtures.

Runtime and tests use the standard library. The passive reader requires the
recorded POSIX no-follow/descriptor operations; no untested native-Windows
compatibility or system sandbox is claimed. Build/install, hosted CI and package
registry publication have not been run by this step.

## Publication and licensing

The original Step 1 record said: **No public software license has been selected**.
Later owner-authorized repository publication adopted this mixed-license split:

Code, test code, tooling and configuration: Apache-2.0.
Project specifications, documentation and repository-created example data:
CC BY 4.0 unless specifically marked otherwise.
Theory publications and third-party assets retain their stated licenses.
The three theory PDFs are excluded from the public software repository.
See `LICENSE`, `LICENSES/`, `NOTICE`, `LICENSING_NOTES.md`, and `THEORY_SOURCES.md`.

The local delivery is complete through Step 3 and includes retained QA history.
Remote publication is confirmed by its actual commit and verification record;
local test success alone is not evidence of a GitHub branch update.
