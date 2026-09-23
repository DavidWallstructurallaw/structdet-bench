# Supplied longitudinal

**Material role: `fixture`; evidence policy: `fixture_only`.**

An explicitly selected longitudinal carrier contains the existing hero_recursive stipulated states, transitions, evidence and complete-unit sensitivity plan.

The supplied L profile preserves its own registered units and replay identity. A/B/C conditions are never synthesized into longitudinal rounds. Computed trajectory, half-life and recovery outputs remain fixture demonstrations.

All source texts, collection histories, people, qualifications and actions in this directory are stipulated software inputs. No candidate is executed, model called, or human contacted. A software-admitted label does not establish an empirical result.

Run from the repository root. Each destination below must be new and its parent must exist.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/supplied_longitudinal/study.json
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/supplied_longitudinal/study.json --output-dir supplied_longitudinal-prepared
```

Expected inspection exit: **0**. Expected normal preparation exit: **0**.

Analyze the prepared local carrier:

```bash
python3.13 -B -S -m structdet_bench analyze --bundle supplied_longitudinal-prepared/bundle.json --output-dir supplied_longitudinal-analysis
```

Exact input hashes, flags and every expected output path appear in the case entry in [`../manifest.json`](../manifest.json). A successful analysis produces exactly `report.json`, `report.md` and `run_manifest.json`.
