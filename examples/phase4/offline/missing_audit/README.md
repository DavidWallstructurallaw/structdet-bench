# Missing audit

**Material role: `fixture`; evidence policy: `fixture_only`.**

Five original emitted candidates have stipulated source-bound membership evidence. The fixed audit selection has no supplied human audit.

Missing audit evidence remains visible and restricts stronger claims. Defensible fixture label-conditioned arithmetic remains available. The missing audit does not remove or replace an original realization.

All source texts, collection histories, people, qualifications and actions in this directory are stipulated software inputs. No candidate is executed, model called, or human contacted. A software-admitted label does not establish an empirical result.

Run from the repository root. Each destination below must be new and its parent must exist.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/missing_audit/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/missing_audit/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map --output-dir missing_audit-prepared
```

Expected inspection exit: **0**. Expected normal preparation exit: **0**.

Analyze the prepared local carrier:

```bash
python3.13 -B -S -m structdet_bench analyze --bundle missing_audit-prepared/bundle.json --output-dir missing_audit-analysis
```

Exact input hashes, flags and every expected output path appear in the case entry in [`../manifest.json`](../manifest.json). A successful analysis produces exactly `report.json`, `report.md` and `run_manifest.json`.
