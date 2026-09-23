# Prepare and inspect a collection

This example prepares a fixed sorting study and inspects supplied exports. It
does not connect to a provider, send prompts, spend money, run candidate programs,
authenticate an operator, or establish an empirical finding.

Use Python 3.13 from the repository root. The following command writes a new
`prepared-collection` directory. An existing destination fails instead of being
overwritten. It creates 72 unattempted call forms, 18 exact prompt files, a plan,
and an initially empty-evidence study envelope.

```bash
python3.13 -B -S - <<'PY'
from pathlib import Path
from structdet_bench.study_collection import collection_template_files

files = collection_template_files("my-study", "v1", phase="main")
target = Path("prepared-collection")
target.mkdir(mode=0o700)
for name, content in files.items():
    with (target / name).open("xb") as stream:
        stream.write(content)
print(f"Prepared {len(files)} files in {target}; no calls were made.")
PY
```

The registration starts as `not_registered`. Requested settings appear in the
plan and submission forms. Every actual control, usage quantity, deployment
identity and enforcement field starts unknown. A requested setting must never
be copied into an actual field without the corresponding observation. The
default import budget is a parser ceiling and authorizes no expenditure.

The optional pilot is a separate call to `collection_template_files` with
`phase="pilot"`, saved to a different new directory and registered separately.
It contains P00 only, six calls and 30 positions. Main material contains P01-P06,
72 calls and 360 positions. The pilot preparation convention applies the rotation
with block index zero: group 1 uses CBA, group 2 uses ABC. HERO specifies the main
rotation; this explicit pilot order is an implementation convention.

Before any separately authorized external collection, an operator must choose
the deployment and document its current control semantics, raw-export ability,
operator, window, retry behavior and maximum authorized expenditure. The
[provider-neutral requirements](COLLECTION_FORMAT.md) describe the required
export without assuming that any provider offers those controls.

For each supplied call, preserve its original response bytes, exact sent prompt
bytes, original attempt identity, observed status and every known retry. Add
their artifact records and bounded local packet entries to `study.json`, using
the existing [study format](../../../STUDY_FORMAT.md). Fill the matching
submission form with the exact same completed ledger record and declare that
JSON packet with purpose `evidence`. A blank preparation form is not evidence of
collection. Additional calls cannot fill failed planned slots.

The inspector also accepts an incomplete study. This command works immediately
on the prepared envelope and later on a completed external export:

```bash
python3.13 -B -S - <<'PY'
from structdet_bench.study_records import load_study
from structdet_bench.study_collection import inspect_collection

result = inspect_collection(load_study("prepared-collection/study.json"))
print(dict(result.counts))
print(result.qualification_status)
print(result.restrictions)
print([d.code for d in result.diagnostics])
PY
```

The initial result reports 72 supplied planning rows, zero actual attempts, zero
selected realizations and zero complete groups. Unknown controls and missing
responses remain explicit restrictions. A failed call without a response creates
zero realizations. A refusal is preserved as a raw response; ordinary refusal
prose is not counted as an extra candidate.

`matched_prefix_eligible` checks the ordered complete-group inventory for k=5,
10 and 20. It does not certify P1/P5, control enforcement, preregistration,
functional validity or structural assignment. Later complete groups never fill
earlier missing positions. Errors must be resolved before relying on imported
extraction records; incomplete responses can still expose their exact descriptive
realizations and limitations.

See [EXTRACTION_FORMAT.md](EXTRACTION_FORMAT.md) for exact headings, fences, byte
spans, empty bodies, ambiguity and truncation. The included
`preregistration_template.json` and `collection_submission_template.json` show
the same unexecuted forms for one main slot. No real provider or human is named.
