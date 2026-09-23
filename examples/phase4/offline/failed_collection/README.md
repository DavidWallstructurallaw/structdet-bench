# Failed collection

**Material role: `fixture`; evidence policy: `fixture_only`.**

One original collection attempt failed with no raw response. Its five planned positions are retained.

The failed call creates zero emitted realizations. Empty observed populations remain distinct from five invalid candidates, and the fixed denominator is preserved. The eligible fixture bundle supports an explicitly unavailable/empty report.

All source texts, collection histories, people, qualifications and actions in this directory are stipulated software inputs. No candidate is executed, model called, or human contacted. A software-admitted label does not establish an empirical result.

Run from the repository root. Each destination below must be new and its parent must exist.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/failed_collection/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/failed_collection/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map --output-dir failed_collection-prepared
```

Expected inspection exit: **0**. Expected normal preparation exit: **0**.

Analyze the prepared local carrier:

```bash
python3.13 -B -S -m structdet_bench analyze --bundle failed_collection-prepared/bundle.json --output-dir failed_collection-analysis
```

Exact input hashes, flags and every expected output path appear in the case entry in [`../manifest.json`](../manifest.json). A successful analysis produces exactly `report.json`, `report.md` and `run_manifest.json`.
