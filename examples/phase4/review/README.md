# Independent review material

These materials support passive review preparation and inspection. The forms are
blank drafts. They contain no actual reviewer identity, candidate program, human
judgment, adjudication or empirical evidence.

The API accepts an existing bounded study envelope through `load_study`. It
preserves the study format's separate membership and validity judgments and
links original first passes, amendments and adjudications to exact artifact
bytes. See `REVIEW_FORMAT.md` for the packet grammar and interpretation.

```python
from structdet_bench.study_records import load_study
from structdet_bench.study_review import inspect_reviews, export_blind_review_pack

study = load_study("my-study/study.json")
assessment = inspect_reviews(study)
if assessment.has_errors:
    raise ValueError("Correct the study or review packet diagnostics first")

print(dict(assessment.initial_agreement))
print(assessment.qualification_status)

# Both parents must exist. Each final directory must be fresh and separate.
result = export_blind_review_pack(
    study, ["artifact-001", "artifact-002"],
    "out/blind-review", "controlled/restricted-review")
```

Only the public directory is suitable for distribution to the intended reviewer.
The restricted directory contains original associations and identity evidence.
Creating files does not send them, assign a person, or record that anyone received
them. Engage actual reviewers through an appropriately authorized process.

The public directory contains randomly ordered, pseudonymously named exact source
bytes, the complete task and mechanism descriptors, validity instructions and a
blank form. Source code can reveal its origin or mechanism. Names, comments and
other source evidence remain unchanged; limitations to blinding stay explicit.
The pack never imports private source/condition/role metadata or other judgments
into its public metadata. Keep the restricted map separate.

For core review, use `core_review_form.json`. For an already selected output,
use `sampled_output_review_form.json`; selecting audit positions is a separate
capability. Use `adjudication_form.json` for a qualified independent expert's
subsequent decision. Complete the applicable study records and the restricted
submission packet instead of treating an edited blank form as evidence.

The examples in `tests/fixtures/phase4/review_*` are explicitly fictional software
fixtures. Their claimed human roles and judgments exercise handling only.
