"""Independent fixed collection plan and supplied-attempt evidence regression.

Synthetic records only. Tests never contact a model or execute candidate source.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import copy
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from structdet_bench import study_records as sr
from structdet_bench import study_collection as collection
from structdet_bench.contracts import InputError
from structdet_bench.local_io import ReadLimits

FIXTURES = Path(__file__).resolve().parent / "fixtures/phase4/collection"
OPENERS = {
    "P00": b"Prepare Python implementations for this bounded sorting task.",
    "P01": b"Implement the sorting function specified below.",
    "P02": b"Write implementations for the following integer-sorting task.",
    "P03": b"Provide programs that meet this sorting specification.",
    "P04": b"Solve the following bounded integer-ordering problem in Python.",
    "P05": b"Create implementations of the function described below.",
    "P06": b"Produce Python solutions for this list-sorting interface.",
}
A_CLAUSE = b"Produce five versions of a solution to this task."
C_CLAUSE = b"Produce five solutions to this task using five different ordering mechanisms. Differences only in names, comments, formatting, or local implementation details do not count as different mechanisms. Keep the task and its constraints unchanged."
MAIN_ROTATIONS = (
    ("ABC", "ACB", "BAC", "BCA", "CAB", "CBA"),
    ("ACB", "BAC", "BCA", "CAB", "CBA", "ABC"),
    ("BAC", "BCA", "CAB", "CBA", "ABC", "ACB"),
    ("BCA", "CAB", "CBA", "ABC", "ACB", "BAC"),
)


def K(value=None, state="known"):
    return {"state": state, "value": value} if state == "known" else {
        "state": state, "reason": "Synthetic unknown; no external operation is authenticated."}


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n").encode()


def ref(row):
    return {key: row[key] for key in ("record_type", "record_id", "record_version")}


def prompt(block="P01", condition="A"):
    original = (FIXTURES / "prompt_p01_a.txt").read_bytes()
    actual = original.replace(OPENERS["P01"], OPENERS[block], 1)
    return actual.replace(A_CLAUSE, C_CLAUSE) if condition == "C" else actual


def response(*indices):
    return b"".join(f"### Candidate {n}\n```python\n# inert {n}\n```\n".encode() for n in indices)


def main_order(block, condition, group):
    return (group - 1) * 18 + (int(block[1:]) - 1) * 3 + MAIN_ROTATIONS[group-1][int(block[1:])-1].index(condition) + 1


class Fixture:
    """Independent envelope and packet author; production templates are not used."""
    def __init__(self, root):
        self.root = Path(root)
        self.data = json.loads((FIXTURES / "collection_study.json").read_bytes())
        self.row_template = copy.deepcopy(next(r for r in self.data["records"] if r["record_type"] == "collection_ledger"))
        self.artifact_template = next(r for r in json.loads((FIXTURES.parent / "study_complete.json").read_bytes())["records"] if r["record_type"] == "artifact")
        self.data["records"] = [r for r in self.data["records"] if r["record_type"] == "study_registration"]
        self.packets = {}
        self.submissions = {}

    def artifact(self, identifier, raw):
        record = copy.deepcopy(self.artifact_template)
        record.update(record_id=identifier, content=K({"packet_id": identifier}),
                      sha256=K(hashlib.sha256(raw).hexdigest()), size_bytes=K(len(raw)),
                      artifact_role="raw_response")
        self.data["records"].append(record)
        self.packets[identifier] = raw
        return record

    def add_call(self, identifier="call-one", *, block="P01", condition="A", group=1,
                 status="succeeded", raw=None, attempt=None, timestamp="2026-09-23T00:00:00Z"):
        row = copy.deepcopy(self.row_template)
        row.update(record_id=identifier, block_id=block, condition=condition,
                   group_index=group, registered_call_order=main_order(block, condition, group),
                   attempt_status=status, attempt_id=K(attempt or "attempt-" + identifier),
                   attempted_at=K(timestamp), request_id=K("request-" + identifier))
        row["controls"] = {
            "temperature": K("1.0" if condition == "B" else "0.4"), "top_p": K("1.0"),
            "presence_penalty": K("0"), "frequency_penalty": K("0"), "seed": K(None),
            "output_allowance": K(8192), "cap_semantics": K("visible_output_tokens"),
            "fresh_context": K(True), "tools_requested": K(False),
            "hidden_controls": K(state="unknown"), "wrapper_knowledge": K(state="unknown")}
        for name in row["deployment"]:
            row["deployment"][name] = K(state="unknown")
        row["deployment"].update(model_identifier=K("fixture-model"),
                                 model_family=K("fixture-family"), deployment_identifier=K("fixture-deployment"),
                                 drift=K("No drift reported in synthetic record."))
        prompt_artifact = self.artifact("prompt-" + identifier, prompt(block, condition))
        prompt_artifact["artifact_role"] = "prompt"
        row["prompt_ref"] = K(ref(prompt_artifact))
        row["sent_prompt_sha256"] = copy.deepcopy(prompt_artifact["sha256"])
        row["raw_response_ref"] = K(state="unknown")
        if raw is not None:
            row["raw_response_ref"] = K(ref(self.artifact("response-" + identifier, raw)))
        self.data["records"].append(row)
        self.submissions[identifier] = self.submission(row)
        return row

    def add_extraction(self, ledger):
        record=copy.deepcopy(next(r for r in json.loads((FIXTURES.parent / "study_complete.json").read_bytes())["records"] if r["record_type"] == "extraction"))
        source=self.row(ledger["raw_response_ref"]["value"]["record_id"])
        raw=self.packets[source["content"]["value"]["packet_id"]]
        record.update(record_id="extraction-"+ledger["record_id"], collection_ref=ref(ledger),
                      raw_response_ref=copy.deepcopy(ledger["raw_response_ref"]),
                      raw_response_sha256=copy.deepcopy(source["sha256"]),limitations=[])
        for number,position in enumerate(record["positions"],1):
            body=f"# inert {number}\n".encode()
            begin=raw.index(body)
            artifact=self.artifact(f"candidate-{number}",body)
            artifact["artifact_role"]="candidate"
            position.update(selection="selected",artifact_ref=K(ref(artifact)),heading=K(f"### Candidate {number}"),
                fence=K("```python"),byte_range=K({"start":begin,"end":begin+len(body)}),
                completion_status="complete",limitations=[])
        self.data["records"].append(record)
        return record

    def submission(self, row):
        return {"kind": "collection_submission", "version": "0.1",
            "study_id": self.data["study_id"], "study_version": self.data["study_version"],
            "fixture": True, "record": copy.deepcopy(row),
            "requested_controls": copy.deepcopy(row["controls"]),
            "enforced_controls": {name: K(True) for name in row["controls"]},
            "cap": {"unit": K("model_token"), "tokenizer": K("fixture-tokenizer"),
                    "convention": K("visible_output_tokens"), "includes_reasoning": K(False), "enforced": K(True)},
            "context": {"visible_system_instruction_ref": K(state="not_applicable"),
                "platform_context": K(state="unknown"), "reasoning_configuration": K(state="unknown"),
                "previous_outputs_supplied": K(False), "reference_material_supplied": K(False),
                "output_selection": K("none"), "automatic_retries": K(0), "duration_ms": K("0")},
            "deployment_window": {"start": K("2026-09-22T00:00:00Z"), "end": K("2026-09-24T00:00:00Z")},
            "evidence_refs": []}

    def row(self, identifier):
        return next(r for r in self.data["records"] if r["record_id"] == identifier)

    def sync(self, *, bind=True):
        for identifier, submission in self.submissions.items():
            if bind:
                submission["record"] = copy.deepcopy(self.row(identifier))
            self.packets["submission-" + identifier] = encoded(submission)
        entries=[]
        for identifier, raw in self.packets.items():
            is_json = identifier.startswith("submission-")
            filename = identifier + (".json" if is_json else ".txt")
            (self.root / filename).write_bytes(raw)
            entries.append({"packet_id": identifier, "purpose": "evidence" if is_json else "artifact",
                "location": K({"kind": "local", "path": filename}),
                "sha256": K(hashlib.sha256(raw).hexdigest()), "size_bytes": K(len(raw)),
                "record_count": K(1 if is_json else 0), "format": "json" if is_json else "bytes",
                "verification": "unchecked", "verification_ref": K(state="unknown")})
        self.data["packet_inventory"] = entries
        (self.root / "study.json").write_bytes(encoded(self.data))

    def load(self, *, bind=True):
        self.sync(bind=bind)
        loaded=sr.load_study(self.root / "study.json")
        if loaded.has_errors or loaded.packet.has_errors:
            raise AssertionError((loaded.diagnostics, loaded.packet.diagnostics))
        return loaded

    def assess(self, *, bind=True):
        return collection.inspect_collection(self.load(bind=bind))


def slot(observed, block="P01", condition="A", group=1):
    return next(s for s in observed.slots if s["block_id"] == block and
                s["condition"] == condition and s["group_index"] == group)


def cell(observed, block="P01", condition="A"):
    return next(c for c in observed.cells if c["block_id"] == block and c["condition"] == condition)


class CollectionPlanTests(unittest.TestCase):
    def test_exact_prompt_materialization_and_only_condition_clause_changes(self):
        for block in OPENERS:
            with self.subTest(block=block):
                a, b, c = (collection.prompt_bytes(block, condition) for condition in "ABC")
                self.assertEqual(a, prompt(block))
                self.assertEqual(b, a)
                self.assertEqual(c, prompt(block, "C"))
                self.assertEqual(c.replace(C_CLAUSE, A_CLAUSE), a)
                self.assertNotIn(b"\r", a)
                self.assertFalse(a.endswith(b"\n"))
        for args in (("P07", "A"), ("P01", "D")):
            with self.assertRaises(InputError):
                collection.prompt_bytes(*args)

    def test_fixed_main_order_positions_controls_and_budget(self):
        plan = collection.collection_plan()
        self.assertEqual((plan["planned_calls"], plan["planned_positions"], plan["max_output_tokens"]),
                         (72, 360, 589824))
        expected=[]
        for group, rotations in enumerate(MAIN_ROTATIONS, 1):
            for block, letters in enumerate(rotations, 1):
                expected.extend((f"P{block:02d}", condition, group) for condition in letters)
        self.assertEqual([(r["block_id"], r["condition"], r["group_index"]) for r in plan["calls"]], expected)
        self.assertEqual([r["registered_call_order"] for r in plan["calls"]], list(range(1,73)))
        for row in plan["calls"]:
            self.assertEqual(tuple(row["planned_positions"]), (1, 2, 3, 4, 5))
            g = row["group_index"]
            self.assertEqual(tuple(row["sample_orders"]), tuple(range(g*5-4, g*5+1)))
            controls=row["requested_controls"]
            self.assertEqual(Decimal(controls["temperature"]["value"]), Decimal("1.0" if row["condition"] == "B" else "0.4"))
            self.assertEqual(controls["output_allowance"], K(8192))
            self.assertEqual(controls["seed"], K(None))
        self.assertTrue(plan["software_preparation_only"])

    def test_optional_pilot_is_separate_and_preparation_is_not_observed_data(self):
        plan=collection.collection_plan("pilot")
        self.assertEqual((plan["planned_calls"], plan["planned_positions"], plan["max_output_tokens"]), (6,30,49152))
        self.assertTrue(all(r["block_id"] == "P00" and r["phase"] == "pilot" for r in plan["calls"]))
        self.assertEqual({r["group_index"] for r in plan["calls"]}, {1,2})
        self.assertFalse({r["slot_id"] for r in plan["calls"]} & {r["slot_id"] for r in collection.collection_plan()["calls"]})
        forms=collection.collection_templates("synthetic", "v1")
        self.assertEqual(len(forms["ledger"]),72)
        for row in forms["ledger"]:
            self.assertEqual(row["attempt_status"],"not_attempted")
            self.assertNotEqual(row["raw_response_ref"]["state"],"known")
            self.assertTrue(all(v["state"] != "known" for v in row["controls"].values()))
        self.assertEqual(forms["registration"]["preregistration"]["status"],"not_registered")
        for packet in forms["submissions"][:1]:
            parsed=collection.parse_collection_submission_bytes(encoded(packet))
            self.assertFalse(parsed.has_errors, parsed.diagnostics)


class CollectionInspectionTests(unittest.TestCase):
    def test_missing_plan_and_failed_without_response_never_fabricate_realizations(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            observed=f.assess()
            self.assertEqual((observed.counts["planned_calls"],observed.counts["planned_positions"]),(72,360))
            self.assertEqual((observed.counts["supplied_slots"],observed.counts["missing_slots"]),(0,72))
            self.assertEqual(observed.counts["selected_realizations"],0)
            f.add_call(status="failed")
            failed=f.assess()
            self.assertEqual(failed.counts["actual_attempt_records"],1)
            self.assertEqual(failed.counts["selected_realizations"],0)
            self.assertEqual(failed.counts["complete_groups"],0)
            self.assertEqual(len(failed.slots),72)
            self.assertFalse(any(cell(failed)["matched_prefix_eligible"].values()))
            self.assertIs(failed.substantive_validation_performed,False)
            f.add_call("refusal",condition="B",raw=b"I cannot provide an answer.\n")
            refused=f.assess()
            self.assertEqual(refused.counts["selected_realizations"],0)
            self.assertEqual(refused.counts["extra_realizations"],0)
            f.add_call("unknown-status",condition="C",status="unknown")
            unknown=f.assess()
            self.assertEqual(unknown.counts["actual_attempt_records"],refused.counts["actual_attempt_records"])
            self.assertEqual(unknown.counts["unknown_attempt_status_records"],1)
            self.assertEqual(unknown.counts["selected_realizations"],0)

    def test_later_complete_groups_cannot_fill_missing_first_group_prefix(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            f.add_call("g1", group=1, raw=response(1,2,4,5))
            for group in (2,3,4):
                f.add_call(f"g{group}",group=group,raw=response(1,2,3,4,5))
            observed=f.assess()
            self.assertEqual(observed.counts["selected_realizations"],19)
            self.assertEqual(observed.counts["complete_groups"],3)
            self.assertEqual(cell(observed)["matched_prefix_eligible"], {"5":False,"10":False,"20":False})
            self.assertEqual(slot(observed)["emitted_positions"],4)

    def test_complete_first_groups_have_exact_prefix_eligibility_regardless_file_order(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            for group in (2,1):
                f.add_call(f"g{group}",group=group,raw=response(1,2,3,4,5))
            observed=f.assess()
            self.assertEqual(cell(observed)["matched_prefix_eligible"], {"5":True,"10":True,"20":False})
            self.assertEqual(observed.counts["selected_realizations"],10)
            f.data["records"].reverse()
            shuffled=f.assess()
            self.assertEqual(shuffled.counts,observed.counts)
            self.assertEqual(cell(shuffled),cell(observed))

    def test_retry_success_cannot_replace_failed_original_attempt(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            initial=f.add_call("original",status="failed")
            retry=f.add_call("retry",raw=response(1,2,3,4,5),timestamp="2026-09-23T00:01:00Z")
            retry["retry_of"]=K(ref(initial))
            observed=f.assess()
            self.assertEqual(observed.counts["actual_attempt_records"],2)
            self.assertEqual(observed.counts["selected_realizations"],0)
            self.assertFalse(cell(observed)["matched_prefix_eligible"]["5"])
            self.assertTrue(slot(observed)["restrictions"])
            self.assertEqual(set(slot(observed)["record_ids"]),{"original","retry"})

    def test_multiple_unlinked_attempts_and_revisions_cannot_choose_success(self):
        for revision in (False,True):
            with self.subTest(revision=revision),TemporaryDirectory() as directory:
                f=Fixture(directory)
                initial=f.add_call("failed",status="failed")
                later=f.add_call("later",raw=response(1,2,3,4,5),timestamp="2026-09-23T00:01:00Z")
                if revision:
                    later["revision"]=2
                    later["supersedes"]=K(ref(initial))
                observed=f.assess()
                self.assertEqual(observed.counts["actual_attempt_records"],2)
                self.assertEqual(observed.counts["selected_realizations"],0)
                self.assertFalse(cell(observed)["matched_prefix_eligible"]["5"])

    def test_actual_attempt_and_response_identity_reuse_restricts_affected_slots(self):
        for reuse in ("attempt", "response"):
            with self.subTest(reuse=reuse), TemporaryDirectory() as directory:
                f=Fixture(directory)
                one=f.add_call("one",raw=response(1,2,3,4,5))
                two=f.add_call("two",condition="B",raw=response(1,2,3,4,5))
                if reuse == "attempt":
                    two["attempt_id"]=copy.deepcopy(one["attempt_id"])
                else:
                    two["raw_response_ref"]=copy.deepcopy(one["raw_response_ref"])
                observed=f.assess()
                code="actual_attempt_identity_reused" if reuse == "attempt" else "raw_response_identity_reused"
                self.assertIn(code,slot(observed)["restrictions"])
                self.assertIn(code,slot(observed,condition="B")["restrictions"])
                self.assertFalse(cell(observed)["matched_prefix_eligible"]["5"])
                self.assertFalse(cell(observed,condition="B")["matched_prefix_eligible"]["5"])

        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            f.add_call("one",raw=response(1,2,3,4,5))
            f.add_call("two",condition="B",raw=response(1,2,3,4,5))
            f.row("response-two")["content"]=copy.deepcopy(f.row("response-one")["content"])
            observed=f.assess()
            for condition in "AB":
                self.assertNotIn("raw_response_identity_reused",slot(observed,condition=condition)["restrictions"])
                self.assertTrue(cell(observed,condition=condition)["matched_prefix_eligible"]["5"])

    def test_prompt_mismatch_and_original_packet_rewrite_cannot_be_certified(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            row=f.add_call(raw=response(1,2,3,4,5))
            f.packets["prompt-call-one"]=prompt()+b"\n"
            artifact=f.row("prompt-call-one")
            artifact["sha256"]=K(hashlib.sha256(f.packets["prompt-call-one"]).hexdigest())
            artifact["size_bytes"]=K(len(f.packets["prompt-call-one"]))
            row["sent_prompt_sha256"]=copy.deepcopy(artifact["sha256"])
            mismatch=f.assess()
            self.assertIn("sent_prompt_bytes_differ",slot(mismatch)["restrictions"])
            f.submissions["call-one"]["record"]["attempt_id"]=K("different-original")
            rewritten=f.assess(bind=False)
            self.assertTrue(rewritten.has_errors)

    def test_snapshot_content_is_verified_and_cannot_be_swapped_under_old_hash(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            f.add_call(raw=response(1,2,3,4,5))
            loaded=f.load()
            snapshots=dict(loaded.snapshots)
            key=next(k for k in snapshots if k.endswith("response-call-one.txt"))
            snapshot=snapshots[key]
            snapshots[key]=replace(snapshot,content=snapshot.content.replace(b"inert",b"other"))
            forged=replace(loaded,snapshots=snapshots)
            observed=collection.inspect_collection(forged)
            self.assertTrue(observed.has_errors)
            self.assertEqual(observed.counts["selected_realizations"],0)

    def test_unknown_controls_hidden_retries_and_fixture_never_become_effective_claims(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            row=f.add_call(raw=response(1,2,3,4,5))
            row["controls"]["temperature"]=K(state="unknown")
            row["deployment"]["checkpoint_identifier"]=K(state="unavailable")
            submission=f.submissions["call-one"]
            submission["context"]["automatic_retries"]=K(state="unknown")
            submission["cap"]["enforced"]=K(state="unknown")
            observed=f.assess()
            self.assertIn("actual_temperature_differs_or_unknown",slot(observed)["restrictions"])
            self.assertIn("automatic_retries_present_or_unknown",slot(observed)["restrictions"])
            self.assertIn("cap_enforcement_unestablished",slot(observed)["restrictions"])
            self.assertIn("checkpoint_identity_unknown",slot(observed)["restrictions"])
            self.assertEqual(observed.qualification_status,"fixture_only")
            self.assertIs(observed.substantive_validation_performed,False)
            self.assertTrue(observed.software_verification_only)
            self.assertEqual(submission["context"]["automatic_retries"]["state"],"unknown")
            f.data.update(evidence_policy="adjudicated_import",material_role="descriptive")
            child_fixture=f.assess()
            self.assertEqual(child_fixture.qualification_status,"fixture_only")
            f.add_call("b-cap",condition="B",raw=response(1,2,3,4,5))
            f.submissions["b-cap"]["cap"]["convention"]=K("total_tokens_including_reasoning")
            unequal=f.assess()
            self.assertIn("matched_control_convention_differs_or_unknown",unequal.restrictions)
            self.assertIn("cap_convention_binding_differs",slot(unequal,condition="B")["restrictions"])

    def test_supplied_extraction_association_and_candidate_bytes_match_original(self):
        for changed in ("heading","fence","limitations","candidate_bytes","span"):
            with self.subTest(changed=changed),TemporaryDirectory() as directory:
                f=Fixture(directory)
                raw=response(1,2,3,4,5)
                if changed == "limitations":
                    raw=raw.replace(b"```\n### Candidate 2",b"```\nUnrequested prose.\n### Candidate 2",1)
                ledger=f.add_call(raw=raw)
                receipt=f.add_extraction(ledger)
                if changed == "limitations":
                    receipt["positions"][0]["limitations"]=["prose_outside_code_fence"]
                baseline=f.assess()
                if changed == "limitations":
                    self.assertEqual([d.code for d in baseline.diagnostics],["prose_outside_code_fence"])
                else:
                    self.assertFalse(baseline.has_errors,baseline.diagnostics)
                if changed == "candidate_bytes":
                    f.packets["candidate-1"]=b"# repaired\n"
                    artifact=f.row("candidate-1")
                    artifact["sha256"]=K(hashlib.sha256(f.packets["candidate-1"]).hexdigest())
                    artifact["size_bytes"]=K(len(f.packets["candidate-1"]))
                elif changed == "span":
                    receipt["positions"][0]["byte_range"]["value"]["start"]+=1
                else:
                    receipt["positions"][0][changed]=[] if changed == "limitations" else K("incorrect association")
                observed=f.assess()
                self.assertTrue(observed.has_errors)
                self.assertTrue(any(d.code.startswith("supplied_extraction_") or d.code == "extracted_candidate_bytes_mismatch" for d in observed.diagnostics))

    def test_registration_chronology_preserves_retrospective_unknown_and_retry_times(self):
        for registered, expected in (("2026-09-22T23:00:00Z", "supplied_times_consistent"),
                                     ("2026-09-23T00:00:00Z", "retrospective_or_simultaneous"),
                                     ("2026-09-23T01:00:00Z", "retrospective_or_simultaneous"),
                                     (None, "unknown")):
            with self.subTest(registered=registered), TemporaryDirectory() as directory:
                f=Fixture(directory)
                f.add_call(raw=response(1,2,3,4,5))
                registration=f.row("registration")["preregistration"]
                registration["registered_at"]=K(registered) if registered else K(state="unknown")
                observed=f.assess()
                self.assertEqual(observed.preregistration["chronology"],expected)
                self.assertTrue(observed.preregistration["external_authentication_required"])
                if expected == "retrospective_or_simultaneous":
                    self.assertIn("registration_not_before_collection",observed.restrictions)
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            original=f.add_call("original",status="failed",timestamp="2026-09-23T01:00:00Z")
            retry=f.add_call("earlier-retry",timestamp="2026-09-22T00:00:00Z",raw=response(1,2,3,4,5))
            retry["retry_of"]=K(ref(original))
            f.row("registration")["preregistration"]["registered_at"]=K("2026-09-23T00:00:00Z")
            observed=f.assess()
            self.assertEqual(observed.preregistration["chronology"],"retrospective_or_simultaneous")
            self.assertIn("registration_not_before_collection",observed.restrictions)

    def test_unknown_retry_origin_cannot_establish_original_matched_group(self):
        for field in ("retry_of","supersedes"):
            with self.subTest(field=field),TemporaryDirectory() as directory:
                f=Fixture(directory)
                row=f.add_call(raw=response(1,2,3,4,5))
                row[field]=K(state="unknown")
                observed=f.assess()
                self.assertFalse(cell(observed)["matched_prefix_eligible"]["5"])
                self.assertEqual(observed.counts["actual_attempt_records"],1)

    def test_logical_packet_rows_and_unused_attachments_share_import_budget(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            f.add_call(raw=response(1,2,3,4,5))
            # One unused acquired JSONL record plus the typed carrier envelope
            # are physical inputs; its nested ledger row is a further logical row.
            f.sync()
            extra=b'{"fixture_only": true}\n'
            (f.root / "unused.jsonl").write_bytes(extra)
            f.data["packet_inventory"].append({"packet_id":"unused", "purpose":"evidence",
                "location":K({"kind":"local","path":"unused.jsonl"}),
                "sha256":K(hashlib.sha256(extra).hexdigest()),"size_bytes":K(len(extra)),
                "record_count":K(1),"format":"jsonl","verification":"unchecked","verification_ref":K(state="unknown")})
            physical_count=len(f.data["records"])+2
            f.data["import_budget"]["max_total_records"]=physical_count
            (f.root / "study.json").write_bytes(encoded(f.data))
            loaded=sr.load_study(f.root / "study.json")
            self.assertFalse(loaded.has_errors,loaded.diagnostics)
            self.assertFalse(loaded.packet.has_errors,loaded.packet.diagnostics)
            observed=collection.inspect_collection(loaded)
            self.assertTrue(observed.has_errors)
            self.assertIn("budget_exceeded_partition_required",[d.code for d in observed.diagnostics])

    def test_submission_parser_rejects_scope_type_duplicates_and_limits(self):
        with TemporaryDirectory() as directory:
            f=Fixture(directory)
            f.add_call()
            packet=f.submissions["call-one"]
            self.assertFalse(collection.parse_collection_submission_bytes(encoded(packet)).has_errors)
            wrong=copy.deepcopy(packet);wrong["study_id"]="wrong-study"
            self.assertTrue(collection.parse_collection_submission_bytes(encoded(wrong)).has_errors)
            wrong=copy.deepcopy(packet);wrong["context"]["automatic_retries"]=K(-1)
            self.assertTrue(collection.parse_collection_submission_bytes(encoded(wrong)).has_errors)
            raw=encoded(packet).replace(b'"version": "0.1",',b'"version": "0.1", "version": "0.1",',1)
            self.assertTrue(collection.parse_collection_submission_bytes(raw).has_errors)
            self.assertTrue(collection.parse_collection_submission_bytes(encoded(packet),ReadLimits(max_file_bytes=4)).has_errors)


if __name__ == "__main__":
    unittest.main()
