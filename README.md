# StructDet-Bench

**Measure which solution structures appear, how concentrated they are, and how
they change across recorded LLM outputs.**

Different wording is easy to notice. How many different solution mechanisms are
actually represented? StructDet-Bench analyzes supplied structural assignments
under an explicit task and evaluation frame. It reports observed support,
concentration, compatible comparisons and qualified longitudinal results, with
inspectable JSON and Markdown reports and strict replay.

The current reference workflow uses **sorting-mechanism records**. You supply the
structural classes, assignments and supporting evidence; unresolved cases remain
visible. The toolkit runs offline. Model collection, candidate execution and
independent human review take place outside it. Applying structural measurement
to other tasks requires admissible task definitions, assignment evidence and any
necessary implementation work.

| Your question | Supported profile |
|---|---|
| Which admitted mechanisms appear, and how concentrated are they? | **M:** measurement, observed support, SCI and related diversity measures. |
| How do registered conditions differ under a compatible frame? | **V:** registered comparisons, sensitivity and retained sampling identities. |
| How do recorded states change over time? | **L:** trajectories, finite-family support assays, local structural half-life and qualified recovery. |

These workflows can support research on LLM output diversity, repetitive solution
strategies and synthetic-data diversity when the required structural records are
available. Recorded repeated generation, rewriting and recursive training retain
their actual process identities.

## Install and run the smallest example

Use **Linux with CPython 3.13 and Unicode 15.1.0**. The verified reference runtime
is **CPython 3.13.5**. The commands below use `python3.13`, its standard `venv`/`pip`
modules and `unzip`; the toolkit has no third-party runtime dependencies. No model
account or API key is needed.

From the [v0.1.0 release](https://github.com/DavidWallstructurallaw/structdet-bench/releases/tag/v0.1.0),
download these two attachments into the same new working directory:

- `structdet_bench-0.1.0-py3-none-any.whl`: the installable package.
- `structdet-bench-v0.1.0-source.zip`: the complete source, examples and documentation.

The wheel does not contain the examples. Open a terminal in the directory
containing both downloads and run:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./structdet_bench-0.1.0-py3-none-any.whl
unzip structdet-bench-v0.1.0-source.zip
.venv/bin/python -m structdet_bench validate --bundle structdet-bench/examples/hero_hf00/bundle.json
.venv/bin/python -m structdet_bench analyze --bundle structdet-bench/examples/hero_hf00/bundle.json --output-dir hf00-output
```

Both toolkit commands should exit `0`. Open `hf00-output/report.md` for the
readable result; `report.json` holds the structured result and `run_manifest.json`
records run identity. Analysis creates exactly these three files. Use a fresh
output directory each time, with an existing parent: an existing destination is
refused to protect previous results.

**HF-00 is a software fixture with `data_role: fixture` and evidence policy
`fixture_only`.** It stipulates twenty classified, valid observations, supplies
no source programs and makes zero model calls. Its assignments contain eight
MERGE, six PIVOT, three HEAP, two COUNT and one RADIX observation. For both the
`classified_all` and `classified_valid` populations, the report gives:

| Result | Value | Meaning within this fixture |
|---|---|---|
| Classified population | `20` | Twenty admitted fixture observations contribute to the distribution. |
| Observed support | `5` | Five mechanism classes are represented. |
| Structural Concentration Index (SCI) | `57/200 = 0.285` | Sum of squared class shares: `(8² + 6² + 3² + 2² + 1²) / 20²`. Higher values mean greater concentration under the same measurement frame. |
| Support at threshold `0.10` | `4` | Four classes have a share of at least 10%; the single RADIX observation has a 5% share. |

The independent arithmetic is retained in
[expected.json](examples/hero_hf00/expected.json). These results demonstrate the
software's calculation on stipulated input; they establish no empirical model
comparison or independently validated mechanism classification.

### Run directly from source

For source work, extract the same complete source archive. No package
installation is required. Starting in the parent of the extracted
`structdet-bench` directory, run:

```bash
cd structdet-bench
python3.13 -B -S -m structdet_bench validate --bundle examples/hero_hf00/bundle.json
python3.13 -B -S -m structdet_bench analyze --bundle examples/hero_hf00/bundle.json --output-dir hf00-source-output
```

The remaining command examples below run **from this source directory**.
`-S` is for direct source execution; omit it when using an installed package.

## Prepare your own input

For an M measurement, copy the existing
[HF-00 directory](examples/hero_hf00) as a format template. Its three input files
are `bundle.json`, `records.jsonl` and `evidence.jsonl`; `expected.json` is only an
example oracle. Replace the fixture identities, observations and evidence with
your own records. Preserve the declared task meaning and record links.

| Where to edit | What you must supply |
|---|---|
| `bundle.json`: identity and frame | `input_schema_version`, `bundle_id`, `study_id`, `data_role`, and `frames` describing the task, mechanism classes and evaluation scope. The currently supported frame is HERO bounded integer sorting. |
| `bundle.json`: protocol and cells | `protocols` and `cells` link the prompt, condition, model metadata and generation protocol to each analysis cell. Keep unknown or unavailable metadata explicit. |
| `bundle.json`: analysis and file inventory | `analysis_config` selects samples, registered positions, ordering, assignment/validity revisions and the evidence policy. `record_files` lists local payload paths and their hash states. Update declared hashes after editing payloads. |
| `records.jsonl` | Actual attempt and realization records, supplied structural assignments, separate validity decisions and artifact references. An unresolved assignment contributes no guessed class. |
| `evidence.jsonl` | The supporting records required by your declared policy: review/adjudication, domain results, audits and other evidence as applicable. Labels or a successful CLI exit do not supply independent evidence. |

Real material uses its appropriate `pilot`, `descriptive` or `confirmatory` role
and the `adjudicated_import` evidence policy. Changing a fixture's role or setting
an assignment to `adjudicated` does not create the required evidence. Keep
provisional review and undetermined validity states when that is what the record
supports. `extensions` and theory `source_pins` are optional; core required fields
remain present even when their permitted values encode unknown information.

[INPUT_FORMAT.md](INPUT_FORMAT.md) lists the exact required fields, optional
fields, state wrappers, file rules and evidence contracts.
[STRUCTURAL_CLASS_CONTRACT.md](STRUCTURAL_CLASS_CONTRACT.md) explains the
classification duties. For compatible registered comparisons or longitudinal
records, use [hero_abc](examples/hero_abc) with
[COMPARISON_FORMAT.md](COMPARISON_FORMAT.md), or
[hero_recursive](examples/hero_recursive) with
[LONGITUDINAL_FORMAT.md](LONGITUDINAL_FORMAT.md).

Validate your edited bundle, then analyze it into a fresh destination using the
same commands as HF-00 with your bundle and output paths. A valid partial input
can retain unresolved cases and unavailable metrics. Read the population and
evidence qualifiers before interpreting a value: `support: 0` for an empty
admitted classified population does not mean the submitted outputs contain no
structure. [LIMITED_TRIAL.md](LIMITED_TRIAL.md) records this distinction on actual
supplied material.

## Use the complete study workflow

A study envelope adds a finite local file inventory, evidence inspection, blind
review exports, exact compilation, correction tracking and readiness disclosures.
The following existing example covers inspection, preparation and analysis.
Its material role is `fixture` and evidence policy is `fixture_only`; observations
and reviewers are stipulated software inputs.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/qualified_synthetic/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/qualified_synthetic/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map --output-dir study-prepared
python3.13 -B -S -m structdet_bench analyze --bundle study-prepared/bundle.json --output-dir study-analysis
```

Use a new destination each time; its parent must already exist. The prepared
package contains `bundle.json`, its exact passive payloads and four companion
files: `study_readiness.json`, `study_readiness.md`, `provenance_map.json` and
`compilation_manifest.json`. Analysis creates exactly `report.json`, `report.md`
and `run_manifest.json`.

Read the material role, evidence status, claim scope and study version before
interpreting numerical results. This example admits five stipulated labels for
fixture arithmetic. It supplies no empirical P1/P5 finding or complete study.
Its validity remains `not_assessed`; outstanding study and audit obligations stay
visible.

### Choose the input route

| Input you have | Command and meaning |
|---|---|
| A study envelope with a finite local packet inventory | `study inspect --study STUDY.json` checks records, acquired evidence and readiness; it prints sanitized JSON. Select supplied qualification/mapping records explicitly with `--qualification-packet-id` and `--mapping-receipt-id`. |
| A partial well-formed study | `study prepare --study STUDY.json --readiness-only --output-dir NEW_DIR` writes the four companion files and sets `analysis_bundle_created: false`. |
| A study with an explicitly supplied compatible M/V/L carrier | `study prepare --study STUDY.json --output-dir NEW_DIR` checks the original correspondence and publishes the exact numerical bundle plus companions when eligible. |
| An existing M/V/L bundle | `validate --bundle BUNDLE.json`, then `analyze --bundle BUNDLE.json --output-dir NEW_DIR`. Existing formats and report files remain supported. |
| Original artifacts to review | `study export-review` creates blind material and a separately controlled identity map, as shown below. |

The study envelope records identity/version pins, registration, material role,
evidence policy, original events and a bounded inventory of local files. See
[STUDY_FORMAT.md](STUDY_FORMAT.md) for the physical grammar and exact legacy
crosswalk. Compilation requires the entire explicitly declared legacy carrier;
it does not infer a numerical study from incomplete registration records. The
carrier must be named `bundle.json` for CLI publication, and its payload paths
must not collide with the four companion filenames. Readiness inspection remains
available for a well-formed carrier that cannot use that publication layout.

Source code, responses and imported traces remain passive data. The toolkit does
not call providers, execute submitted candidates, assign reviewers or fetch
remote attachments. [EMPIRICAL_PROTOCOL.md](EMPIRICAL_PROTOCOL.md) describes the
roles, actual evidence and activity readiness needed for external work.

### Export review material

This runnable example selects one synthetic candidate. Both destination parents
must exist, and both destinations must be fresh and separate.

```bash
python3.13 -B -S -m structdet_bench study export-review --study examples/phase4/offline/qualified_synthetic/study.json --artifact-id candidate-P01-A-1-1 --review-kind sampled_output --output-dir review-public --restricted-output-dir review-restricted
```

The public package contains `review_instructions.json`, `review_form.json` and
one randomly named `item-<32 hex digits>.txt` per selected artifact. Its exact
item inventory is in the instructions. The separate restricted package contains
`restricted_map.json`, preserving original associations and supplied identity
records. Repeat `--artifact-id` to select more artifacts. An optional
`--pack-id pack-<32 hex digits>` is a public opaque join key shared by the two
packages; it must contain no personal identity.

The export prepares blank review work. It establishes no completed human review.
Unchanged artifact content can expose mechanism, authorship or prior context;
metadata blinding cannot undo that exposure. The restricted directory is
published first. If public publication fails, the error reports both transaction
states; an already committed restricted map can remain. Inspect those states
and destinations before retrying with new paths. Keep the restricted mapping under
appropriate access control and send material only through an authorized channel.

## Read report states, handle errors and replay

| Result | Interpretation |
|---|---|
| Exit `0` | Processing succeeded. Evidence or scientific conclusions can still be restricted, unresolved or unavailable. Read the reported states. |
| Exit `2` | Malformed/contradictory input, ineligible normal preparation, invalid arguments or an existing ordinary output destination. No new successful bundle is fabricated. |
| Exit `3` | Local I/O/internal/publication failure. Review-export publication failures include bounded public/restricted transaction states for recovery. |
| `analysis_bundle_created: false` | The operation produced no numerical bundle, including an explicit readiness-only export of an otherwise eligible study. |
| `substantive_validation_performed: false` | The software has not authenticated actual execution, real reviewer independence or an empirical claim. |

Readiness-only mode cannot bypass malformed records or conflicting current
mappings. Publication uses fresh directories and atomic no-overwrite operations.
Supported secure input acquisition requires POSIX no-follow descriptor operations;
publication requires Linux `renameat2`. Unsupported environments fail closed.

Reports preserve planned positions, emitted realizations, classified populations,
validity and audit denominators separately. Missing positions never backfill
fixed prefixes. Zero, missing, unavailable, undetermined and not assessed retain
their distinct meanings. The study companion exposes all ten EC disclosures and
five scoped conditions. Numeric availability alone never supplies missing
independent evidence.

For an explicit L import, retained replay verifies input, methods, software,
registered unit order and stored draw/index identity:

```bash
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/supplied_longitudinal/study.json --output-dir longitudinal-prepared
python3.13 -B -S -m structdet_bench analyze --bundle longitudinal-prepared/bundle.json --output-dir longitudinal-analysis
python3.13 -B -S -m structdet_bench validate --bundle longitudinal-prepared/bundle.json --replay-manifest longitudinal-analysis/run_manifest.json
python3.13 -B -S -m structdet_bench analyze --bundle longitudinal-prepared/bundle.json --replay-manifest longitudinal-analysis/run_manifest.json --output-dir longitudinal-replay
```

Missing or corrupt requested replay data never triggers fresh sampling. The A/B/C
comparison profile uses its declared `comparison.resampling.replay_ref` route;
see [COMPARISON_FORMAT.md](COMPARISON_FORMAT.md). L replay and categorical,
finite-family, half-life and recovery limits are specified in
[LONGITUDINAL_FORMAT.md](LONGITUDINAL_FORMAT.md). A/B/C conditions and repeated
collection groups do not become longitudinal rounds.

Ordinary reports omit raw bodies, private actor mappings and unrestricted
reviewer prose. The prepared carrier retains its original payload bytes and may
contain restricted evidence. Treat the whole prepared directory as a controlled
input package; sharing a sanitized report does not authorize sharing its sources.

## Examples and verification

[Seven complete study examples](examples/phase4/offline/README.md) cover empty
readiness, qualified synthetic imports, disputed membership, failed collection,
missing audit, stale correction and supplied L. Their manifest gives exact input
hashes, command options, expected exits and output inventories. Existing
`examples/hero_hf00`, `examples/hero_abc`, `examples/hero_recursive` and
`examples/categorical_null` remain available for the established profiles.

```bash
python3.13 -B -S tools/check.py canonical --output-dir ../canonical-checks --jobs 4
python3.13 -B -S tools/check.py canonical --output-dir ../study-checks --select tests.test_study_cli --select tests.test_study_reporting
```

[VERIFICATION.md](VERIFICATION.md) describes canonical regression, release
qualification and the inactive historical archive. Select tests according to the
changed behavior; use release qualification for a release candidate or packaging
change. Recorded fixture correctness and software verification remain separate
from empirical evidence, independent validation, repository publication and
owner acceptance. Historical results and handoff identities are retained in
[PHASE_2_COMPLETION.md](PHASE_2_COMPLETION.md),
[PHASE_3_COMPLETION.md](PHASE_3_COMPLETION.md) and [history/README.md](history/README.md).

This software release uses version `0.1.0`. M/V/L analysis and the
offline study workflow are implemented. Six concrete activity-readiness packets
and a resource-gap register prepare later external work. Packet completeness
means ready for review and grants no operational permission. See the
[activity packets and readiness-gap register](operations/hero_readiness/README.md)
for the prepared materials and outstanding resources.

A limited real-material trial is complete: five programs transcribed from
user-supplied model-response screenshots each passed the existing 8,995 HERO
functional inputs, and their passive CLI intake succeeded. The five proposed
mechanism labels remain provisional. [LIMITED_TRIAL.md](LIMITED_TRIAL.md)
records the finite scope, provenance limits and separate retained evidence.
Full registered model comparisons, independent review and scientific validation
remain pending. No further sample collection is required for this software
release. [PHASE_4_COMPLETION.md](PHASE_4_COMPLETION.md) records the software
handoff and subsequent trial; [RELEASE_NOTES.md](RELEASE_NOTES.md) describes
the release scope. The [Releases page](https://github.com/DavidWallstructurallaw/structdet-bench/releases)
provides publication status and downloadable artifacts.

Replay checks software identity strictly. A manifest produced with an earlier
software version must be replayed with its exact recorded software; retain that
source alongside the manifest. The new version does not silently accept or
resample an incompatible replay request.

## Scientific and licensing boundaries

Observed support is task/frame/population relative. These examples establish no
full expressible or latent support, universal model capacity, population-level
confidence, actual model recovery, deployment assurance or truth of the theory.
UD-006 remains claim-specific and requires actual independent evidence; the
UD-007 latent-support diagnostic remains deferred.

[THEORY_SOURCES.md](THEORY_SOURCES.md) pins the adopted SD, SI and EC publications;
[EVALUATION_CLOSURE_ADDENDUM.md](EVALUATION_CLOSURE_ADDENDUM.md) preserves the
five-condition update. Source adoption does not establish empirical validation.
Code, tools, tests and adjacent configuration use Apache-2.0. Project
specifications and benchmark documentation use CC BY 4.0. See
[LICENSING_NOTES.md](LICENSING_NOTES.md) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The original theory PDFs retain
their licenses and are excluded from this software package.
