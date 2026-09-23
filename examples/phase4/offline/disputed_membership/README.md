# Disputed membership

**Material role: `fixture`; evidence policy: `fixture_only`.**

The original fixture judgment assigns SORT-ADJ, while a separately retained synthetic audit assigns SORT-HEAP to the same first candidate bytes.

The unresolved disagreement withholds that membership. The explicitly supplied carrier still requests its old accepted assignment, so conversion fails as a known conflict. The original candidate, both reviews and fixed position remain available for inspection.

All source texts, collection histories, people, qualifications and actions in this directory are stipulated software inputs. No candidate is executed, model called, or human contacted. A software-admitted label does not establish an empirical result.

Run from the repository root. Each destination below must be new and its parent must exist.

```bash
python3.13 -B -S -m structdet_bench study inspect --study examples/phase4/offline/disputed_membership/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map
python3.13 -B -S -m structdet_bench study prepare --study examples/phase4/offline/disputed_membership/study.json --qualification-packet-id submission-qualification --mapping-receipt-id bridge-map --output-dir disputed_membership-prepared
```

Expected inspection exit: **2**. Expected normal preparation exit: **2**.

The conflicting current carrier is withheld. Both preparation modes leave the destination absent. Preserve the original evidence and supply a separately identified corrected carrier/mapping before attempting compilation again.

Exact input hashes, flags and every expected output path appear in the case entry in [`../manifest.json`](../manifest.json). A successful analysis produces exactly `report.json`, `report.md` and `run_manifest.json`.
