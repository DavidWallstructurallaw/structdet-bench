# Readiness only

**Material role: `fixture`; evidence policy: `fixture_only`.**

A registered passive envelope with no supplied artifacts or evidence.

Inspection preserves missing evidence. Normal preparation cannot create a numerical bundle; explicit readiness-only preparation creates four companion files.

All source texts, collection histories, people, qualifications and actions in this directory are stipulated software inputs. No candidate is executed, model called, or human contacted. A software-admitted label does not establish an empirical result.

Run from the repository root. Each destination below must be new and its parent must exist.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/readiness_only/study.json
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/readiness_only/study.json --output-dir readiness_only-prepared
```

Expected inspection exit: **0**. Expected normal preparation exit: **2**.

Request a readiness-only export explicitly:

```bash
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/readiness_only/study.json --readiness-only --output-dir readiness_only-readiness
```

Exact input hashes, flags and every expected output path appear in the case entry in [`../manifest.json`](../manifest.json). A successful analysis produces exactly `report.json`, `report.md` and `run_manifest.json`.
