"""Independent exact-byte extraction and missing-position regression.

All response bytes are passive, authored software fixtures. No candidate is run.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from structdet_bench.contracts import InputError
from structdet_bench.local_io import ReadLimits
from structdet_bench import study_extraction as extraction

FIXTURES = Path(__file__).resolve().parent / "fixtures/phase4/collection"


def section(number, body=b"pass\n", *, closed=True):
    return (f"### Candidate {number}\n```python\n".encode() + body +
            (b"```\n" if closed else b""))


def result(raw):
    return extraction.extract_response_bytes(raw)


class ExactByteExtractionTests(unittest.TestCase):
    def test_original_spans_utf8_crlf_whitespace_and_empty_are_exact(self):
        raw = (FIXTURES / "exact_response.txt").read_bytes()
        expected = json.loads((FIXTURES / "exact_expected.json").read_bytes())
        observed = result(raw)
        self.assertFalse(observed.group_complete)
        self.assertTrue(any(d.code == "empty_candidate_body" for d in observed.diagnostics))
        self.assertTrue(observed.order_established)
        self.assertEqual(len(observed.positions), 5)
        self.assertFalse(observed.extras)
        for position, want in zip(observed.positions, expected["positions"]):
            with self.subTest(position=want["within_group_index"]):
                self.assertEqual(position.within_group_index, want["within_group_index"])
                self.assertEqual(position.selection, "selected")
                self.assertEqual(position.completion_status, "complete")
                self.assertEqual((position.byte_range.start, position.byte_range.end),
                                 (want["start"], want["end"]))
                self.assertEqual(position.content, want["content"].encode("utf8"))
                self.assertEqual(position.content, raw[want["start"]:want["end"]])

    def test_absent_response_and_emitted_empty_are_different(self):
        missing = result(b"")
        empty = result(section(1, b""))
        self.assertFalse(missing.group_complete)
        self.assertEqual([p.within_group_index for p in missing.positions], [1, 2, 3, 4, 5])
        self.assertTrue(all(p.selection == "missing" and p.content is None and
                            p.byte_range is None for p in missing.positions))
        first = empty.positions[0]
        self.assertEqual(first.selection, "selected")
        self.assertEqual(first.content, b"")
        self.assertEqual(first.byte_range.start, first.byte_range.end)
        self.assertIsNone(empty.positions[1].content)

    def test_missing_middle_position_does_not_renumber_later_emissions(self):
        observed = result(b"".join(section(i, f"# {i}\n".encode()) for i in (1, 3, 4, 5)))
        self.assertFalse(observed.group_complete)
        self.assertEqual(observed.positions[1].selection, "missing")
        self.assertIsNone(observed.positions[1].content)
        self.assertEqual(observed.positions[2].content, b"# 3\n")
        self.assertEqual(observed.positions[4].content, b"# 5\n")

    def test_duplicates_withhold_affected_slot_and_preserve_both_candidates(self):
        raw = section(1, b"# first\n") + section(1, b"# second\n") + section(2)
        observed = result(raw)
        self.assertFalse(observed.group_complete)
        self.assertFalse(observed.order_established)
        self.assertEqual(observed.positions[0].selection, "withheld")
        self.assertIsNone(observed.positions[0].content)
        extra_bytes = b"\n".join(extra.content for extra in observed.extras)
        self.assertIn(b"# first\n", extra_bytes)
        self.assertIn(b"# second\n", extra_bytes)
        for extra in observed.extras:
            self.assertEqual(extra.content, raw[extra.byte_range.start:extra.byte_range.end])

    def test_multiple_fences_preserve_whole_malformed_body_without_selection(self):
        raw = b"### Candidate 1\n```python\n# broken\n```\n```python\n# better\n```\n"
        observed = result(raw)
        first = observed.positions[0]
        self.assertFalse(observed.group_complete)
        self.assertNotEqual(first.completion_status, "complete")
        self.assertEqual(first.selection, "selected")
        self.assertEqual(first.content, raw[len(b"### Candidate 1\n"):])
        self.assertTrue(first.limitations)
        self.assertIn(b"# broken", first.content)
        self.assertIn(b"# better", first.content)

    def test_unique_unfenced_body_is_not_repaired_or_completed(self):
        raw = b"### Candidate 1\ndef sort_values(values):\n return values\n"
        observed = result(raw)
        first = observed.positions[0]
        self.assertFalse(observed.group_complete)
        self.assertNotEqual(first.completion_status, "complete")
        self.assertEqual(first.content, raw[len(b"### Candidate 1\n"):])
        self.assertTrue(first.limitations)

    def test_unrequested_heading_preserves_extra_without_adding_plan_position(self):
        raw = b"".join(section(i) for i in range(1, 6)) + section(6, b"# extra\n")
        observed = result(raw)
        self.assertEqual(len(observed.positions), 5)
        self.assertFalse(observed.group_complete)
        self.assertTrue(all(p.selection == "selected" for p in observed.positions))
        self.assertTrue(any(b"# extra\n" in e.content for e in observed.extras))
        self.assertNotIn(b"# extra", b"".join(p.content for p in observed.positions))

    def test_out_of_order_positions_remain_identified_but_format_fails(self):
        observed = result(b"".join(section(i, f"# {i}\n".encode()) for i in (2, 1, 3, 4, 5)))
        self.assertFalse(observed.group_complete)
        self.assertEqual(observed.positions[0].content, b"# 1\n")
        self.assertEqual(observed.positions[1].content, b"# 2\n")

    def test_final_unclosed_fence_retains_truncated_original_bytes(self):
        body = b'def sort_values(values):\r\n    return ["\xc3\xa9"'
        raw = b"".join(section(i) for i in range(1, 5)) + section(5, body, closed=False)
        observed = result(raw)
        last = observed.positions[4]
        self.assertEqual(last.selection, "selected")
        self.assertEqual(last.completion_status, "truncated")
        self.assertEqual(last.content, body)
        self.assertEqual(last.byte_range.end, len(raw))
        self.assertFalse(observed.group_complete)

    def test_unclosed_fence_with_later_heading_cannot_invent_association(self):
        raw = section(1, b"# unfinished\n", closed=False) + b"### Candidate 2\n# later\n"
        observed = result(raw)
        self.assertFalse(observed.group_complete)
        self.assertFalse(observed.order_established)
        self.assertNotEqual(observed.positions[0].completion_status, "complete")
        self.assertNotEqual(observed.positions[1].completion_status, "complete")
        self.assertTrue(observed.extras or any(p.limitations for p in observed.positions))

    def test_heading_inside_closed_code_is_not_a_new_candidate(self):
        body = (b'"""\n### Candidate 2\n"""\n# keep this literal\n' +
                b"### Candidate " + b"9" * 1025 + b"\n")
        observed = result(section(1, body) + section(2, b"# actual two\n"))
        self.assertEqual(observed.positions[0].content, body)
        self.assertEqual(observed.positions[1].content, b"# actual two\n")
        self.assertNotEqual(observed.positions[0].selection, "withheld")

    def test_malformed_heading_alias_does_not_silently_become_expected_heading(self):
        for heading in (b"### Candidate 01\n", b"### Candidate 1: revised\n"):
            with self.subTest(heading=heading):
                observed = result(heading + b"```python\npass\n```\n")
                self.assertFalse(observed.group_complete)
                self.assertNotEqual(observed.positions[0].completion_status, "complete")
                self.assertTrue(observed.extras or observed.positions[0].limitations)

    def test_fence_spelling_and_closed_marker_lengths_preserve_code(self):
        raw = b"   ### Candidate 1  \r\n  ~~~~ Python\t\r\n# x\r\n  ~~~~~ \r\n"
        first = result(raw).positions[0]
        self.assertEqual(first.content, b"# x\r\n")
        self.assertEqual(first.completion_status, "complete")

    def test_nonpython_fence_and_prose_never_silently_pass_full_format(self):
        for raw in (section(1).replace(b"```python", b"```javascript"),
                    b"Here is the answer.\n" + b"".join(section(i) for i in range(1, 6)),
                    b"".join(section(i) for i in range(1, 6)) + b"Done.\n"):
            with self.subTest(raw=raw[:40]):
                observed = result(raw)
                self.assertFalse(observed.group_complete)
                self.assertTrue(observed.diagnostics or any(p.limitations for p in observed.positions))

    def test_size_line_and_record_budgets_reject_before_unbounded_parsing(self):
        cases = [(b"12345", ReadLimits(max_file_bytes=4)),
                 (b"12345\n", ReadLimits(max_line_bytes=4)),
                 (b"".join(section(i) for i in range(1, 6)), ReadLimits(max_records=2))]
        for raw, limits in cases:
            with self.subTest(limits=limits):
                observed=extraction.extract_response_bytes(raw, limits=limits)
                self.assertTrue(observed.has_errors)
                self.assertTrue(all(p.selection == "withheld" and p.content is None for p in observed.positions))
        self.assertTrue(extraction.extract_response_bytes("not bytes").has_errors)

    def test_candidate_program_remains_inert(self):
        with TemporaryDirectory() as directory:
            sentinel = Path(directory) / "must-not-exist"
            body = ("from pathlib import Path\nPath(" + repr(str(sentinel)) +
                    ").write_text('executed')\n").encode()
            observed = result(section(1, body))
            self.assertEqual(observed.positions[0].content, body)
            self.assertFalse(sentinel.exists())


if __name__ == "__main__":
    unittest.main()
