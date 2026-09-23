# Qualified synthetic

**Material role: `fixture`; evidence policy: `fixture_only`.**

Five inert candidate texts have explicit original collection/extraction associations, stipulated mechanism evidence and current legacy assignment mappings. One fixed-position audit has a consistent second synthetic review.

All five labels qualify under fixture policy for M arithmetic. Validity remains not_assessed. The small supplied group does not complete the 72-call study or its human-audit obligations; scientific claims remain restricted.

All source texts, collection histories, people, qualifications and actions in this directory are stipulated software inputs. No candidate is executed, model called, or human contacted. A software-admitted label does not establish an empirical result.

Run from the repository root. Each destination below must be new and its parent must exist.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/qualified_synthetic/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/qualified_synthetic/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map --output-dir qualified_synthetic-prepared
```

Expected inspection exit: **0**. Expected normal preparation exit: **0**.

Analyze the prepared local carrier:

```bash
python3.13 -B -S -m structdet_bench analyze --bundle qualified_synthetic-prepared/bundle.json --output-dir qualified_synthetic-analysis
```

Exact input hashes, flags and every expected output path appear in the case entry in [`../manifest.json`](../manifest.json). A successful analysis produces exactly `report.json`, `report.md` and `run_manifest.json`.
