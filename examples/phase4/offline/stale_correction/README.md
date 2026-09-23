# Stale correction

**Material role: `fixture`; evidence policy: `fixture_only`.**

A current correction incident challenges the first candidate and its dependent evidence. The action is proposed; no performed correction or replacement evidence is supplied.

Dependency invalidation reaches the current assignment and affected comparison obligations. The old carrier is withheld. Proposed correction does not become performed correction or a successful reanalysis.

All source texts, collection histories, people, qualifications and actions in this directory are stipulated software inputs. No candidate is executed, model called, or human contacted. A software-admitted label does not establish an empirical result.

Run from the repository root. Each destination below must be new and its parent must exist.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/stale_correction/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/stale_correction/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map --output-dir stale_correction-prepared
```

Expected inspection exit: **2**. Expected normal preparation exit: **2**.

The conflicting current carrier is withheld. Both preparation modes leave the destination absent. Preserve the original evidence and supply a separately identified corrected carrier/mapping before attempting compilation again.

Exact input hashes, flags and every expected output path appear in the case entry in [`../manifest.json`](../manifest.json). A successful analysis produces exactly `report.json`, `report.md` and `run_manifest.json`.
