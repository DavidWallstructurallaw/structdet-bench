# Passive response extraction

`structdet_bench.study_extraction.extract_response_bytes(raw, *, limits=None)`
implements the operational recognition of `hero_candidates_v1` under
`HERO_BENCHMARK_SPEC.md` Sections 7.2 and 8. It consumes supplied bytes and returns
an immutable `ExtractionResult`. It does not contact a model, parse or run the
programs, repair source, assign a mechanism, or decide functional validity.

The receipt always has five ordered **plan** rows. Its selected rows are the
identified realizations. A call without a response must remain a call without a
response: the collection inspector does not create five artificial artifacts or
pass invented bytes to the extractor. Supplying an actual empty response is a
different event, which has a hash but no candidate headings or realizations.

## Recognition grammar

These are explicit implementation choices for recognizing the requested format.
They do not change the task, mechanism classes, validity rubric, or estimators.

- Input is strict UTF-8 without a byte-order mark. LF and CRLF line endings are
  recognized and remain unchanged in every retained region.
- The expected heading has the text `### Candidate N`, with one ASCII space
  between its words, and a canonical decimal number from 1 through 5. Up to
  three leading ASCII spaces and trailing spaces or tabs are accepted. Heading
  case is significant. The registered order is 1, 2, 3, 4, 5.
- Any ATX heading with one through six hashes, up to three leading spaces, and
  whitespace after the hashes bounds the preceding section outside a fence.
  Other headings are deviations. A candidate-like malformed heading, including
  one naming multiple positions, cannot supply a repaired position. Its body is
  retained in the unselected inventory. Its named planned positions are withheld;
  when no position can be established, all five are withheld.
- An exact numbered heading outside the planned range, including 0 and 6, is an
  unrequested extra. It never increases the planned five-position budget.
- A code fence opens with at least three consecutive backticks or tildes, with
  up to three leading ASCII spaces. Its only information token must be `python`,
  ignoring case and surrounding spaces or tabs. Backticks in a backtick fence's
  information string cannot open that fence.
- A closing fence uses the same character, at least the opening run length,
  up to three leading spaces, and no other text beyond spaces or tabs. Opening
  and closing lines are excluded from the ordinary code region. Content is never
  dedented or normalized.
- Contents inside a closed fence are opaque original bytes. A comment or string
  containing `### Candidate 2` inside that fence remains part of its program.
  Numeric-token limits for recognized headings do not apply to program literals
  or comments.

Ordinary extraction selects the exact contents of one Python fence belonging to
one unique heading. Non-whitespace text outside that sole fence is recorded as a
format deviation, while the uniquely associated code bytes remain selected.

A body with no fence, multiple fences, or a non-Python fence is retained in full
as an identified incomplete artifact with `completion_status: "failed"` and an
extraction limitation. No block is preferred, combined, or silently discarded.
That status describes the extraction and completion problem, and supplies no
functional-validity or structural-membership judgment.

An unclosed final Python fence can yield a truncated region from immediately
after its opening line through the response end. If that unclosed fence contains
apparent later candidate headings, association is ambiguous: affected positions
are withheld and the original body remains unselected. A later matching closing
fence closes its current fence according to the grammar; intervening
candidate-looking lines remain its contents. The resulting missing positions and
format deviations are still reported. No later position is fabricated or used
to fill an earlier gap.

## Exact byte ranges

`ByteRange(start, end)` uses zero-based, end-exclusive offsets in the raw response.
For this byte string:

```python
raw = b"### Candidate 1\n```python\nx = 1\n```\n"
```

the selected content is `b"x = 1\n"`, and its range is `{"start": 26, "end": 32}`.
For every retained position or extra:

```python
item.content == raw[item.byte_range.start:item.byte_range.end]
```

Offsets count UTF-8 bytes, including every CR and LF. They do not count decoded
characters. The original response hash and each retained region's SHA-256 make
the association auditable. Original heading/fence text and all remaining bytes
stay available in the raw response.

## Missingness and group accounting

| Supplied situation | Plan row | Realization and limitation |
| --- | --- | --- |
| No heading for position 2 | `missing` | No content, range, or artifact is fabricated. |
| A unique heading with an emitted empty body | `selected` | An empty artifact is retained; the extraction limitation remains explicit. |
| A closed empty Python fence | `selected` | The exact empty code region is retained. A closed extraction boundary supplies no usable program text. |
| A unique malformed body | `selected` | Its full original body is retained with failed extraction completion. |
| Duplicate or ambiguously associated position | `withheld` | Competing original bodies stay in the unselected inventory. |
| Unrequested candidate 6 | No added plan row | Its body stays unselected and the format deviation remains visible. |

Whitespace-only bodies preserve their exact whitespace bytes. Empty or malformed
artifacts never acquire a structural assignment through this parser.

`realized_count` counts selected identified artifacts, including an explicitly
empty or incomplete one. `order_established` describes the unambiguous registered
ordering of the identified requested headings. `group_complete` requires all
five selected positions with complete extraction, registered heading order, and
no format/extraction limitations. It is a group-format result. An individually
complete program remains separately assessable when another position is absent.
None of these fields asserts functional validity, independent generation, or
eligibility for a scientific conclusion.

## Limits and receipt API

The extractor reuses `ReadLimits`, allowing stricter limits and rejecting raised
project ceilings. Defaults are 16 MiB per response, 64 MiB aggregate input,
1 MiB per physical line, 100,000 logical parsing events, and 1,024 characters per
recognized heading's numeric token. The five plan rows consume five logical
events. Heading and fence boundaries also consume events. Closed-fence program
lines remain passive bytes. The collection loader separately enforces the
aggregate limits across the study's acquired attachments and operational rows.

Physical or encoding failure returns five withheld rows and no realizations.
The response hash is available after the size checks succeed; an input rejected
before hashing has no claimed hash. A resource-limit failure never triggers an
alternate extraction strategy or code execution.

`result.as_dict()` or `result_dict(result)` returns a JSON-ready receipt with
positions, extras, ranges, hashes, sizes, statuses, and diagnostics. Original
content bytes remain accessible in the frozen dataclasses and the raw artifact;
they are omitted from this JSON receipt. `has_errors` concerns extraction
diagnostics. The receipt explicitly records that functional validity and
structural membership were not assessed.
