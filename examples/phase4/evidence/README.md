# Evidence qualification and audit selection

This offline API inspects supplied study records. It performs no collection,
candidate execution, human review or empirical validation. The study CLI and
analysis-bundle compilation remain later implementation steps.

For an existing study workspace, run from the project root:

```bash
python3.13 -B -S - <<'PY'
import json
from structdet_bench.study_records import load_study
from structdet_bench.study_evidence import inspect_study_evidence

loaded = load_study('../my-study/study.json')
# Use the exact inventory ID of the supplied evidence_qualification attachment.
result = inspect_study_evidence(loaded, packet_id='qualification')
print(json.dumps(result.as_dict(), indent=2))
raise SystemExit(result.exit_code)
PY
```

Omitting `packet_id` inspects the available original positions with qualification
evidence missing. It admits no default labels. An explicitly named packet must
be inventoried; absent, corrupt, mismatched and unavailable information never
triggers collection or fresh evidence generation.

For an immediately executable fixture-only demonstration, replace the example's
load call with `load_study('tests/fixtures/phase4/collection/collection_study.json')`
and omit `packet_id`. Expected: 72 fixed audit opportunities, all missing;
zero distinct audit targets and zero emitted positions; no admitted membership,
no evaluated P1/P5 prediction, and `substantive_validation_performed: false`.
This path reads the supplied fixture and prints a report without creating files.

The report separates:

- each artifact's admitted membership, bounded validity and claim restrictions;
- all fixed audit positions, including missing or uninspectable opportunities;
- deduplicated targets with every selection reason and linked review IDs;
- the 18 main cells and the two registered condition comparisons;
- the 32 planned core items, unresolved review queue and requested claim scopes.

The systematic formula is `1 + ((b + c + g - 3) % 5)` with one-based block,
condition and group indices. Targeted review includes reported novel/hybrid
candidates, unresolved disputes, challenged essential evidence, all count-one/
count-two accepted cases per 20-position cell, and an observed representative
of each class in each condition. An already selected representative is reused;
remaining ties use original registered call and candidate order. Reviews add
zero generator observations. No audit-error-rate estimator is provided.

`record_complete` describes linked supplied records. Authentication and substantive
review remain external responsibilities. Fixtures cannot establish empirical
truth. A label-conditioned record summary can remain available with independent
validation restricted. A claimed `valid` result requires the existing complete
8995-input rubric inspection; output agreement alone supplies no mechanism label.

See [EVIDENCE_FORMAT.md](EVIDENCE_FORMAT.md) for the exact attachment and report
boundaries. Direct regression: `python3.13 -B -S -m unittest tests.test_study_evidence`.
