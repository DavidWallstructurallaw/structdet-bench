"""Phase 2 trusted verification helpers. No production or empirical operations.

The matrix records future obligations. This module verifies their identities
against pinned source tables; it never infers implementation from a label.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from tests.helpers import ROOT, load_matrix as load_phase1_matrix, source_table

MATRIX_PATH = ROOT / "tests/phase2_matrix.json"
PLAN_SHA256 = "17452ec510cdd31ee960806c6140142dcb411a76ebd87aa138afbdbc6ec639cc"
PHASE1_MATRIX_SHA256 = "aea567fadfce3befa7c47a133e5bdf4cc27af413e16daddccfc405b67aacd1cf"
PREDECESSOR_IDS_SHA256 = "6301ae91d0ea4ed99da217bab6ce36604d616950a2ed4041228bb4a22460f084"
ARCHIVE_SHA256 = "9a38bbd53424ff80d4b8c745774df1b69d1e9bac400320c2fced00669fcaadf4"
INVENTORY_SHA256 = "381966c3d892b7b258cc11af72df1339c44c327fb654972fc6e302c56efd3e8f"
V_IDS = ("VT-03", "VT-12", "VT-14", "VT-17", "VT-18", "VT-19", "VT-20", "VT-24",
         "VT-31", "VT-32", "VT-33", "VT-34", "VT-35", "VT-36", "VT-37", "VT-38",
         "VT-39", "VT-40", "VT-41", "VT-42", "VT-43", "VT-44", "VT-45", "VT-46",
         "VT-47", "VT-50")
METHOD_PATTERN = re.compile(r"^tests\.test_[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.test_[A-Za-z0-9_]+$")
ROOT_KEYS = {"schema_version", "project", "phase", "approved_plan", "delivery",
             "predecessor", "catalogues", "vt_obligations", "trace_requirements",
             "report_groups", "ec_requirements", "engineering_requirements", "stage_bindings",
             "limits", "evidence_status", "deferred_status"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def read_json(path: Path) -> Any:
    """Strict trusted QA JSON, bounded and without object-key overwrites."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("qa_file_not_regular")
    if path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("qa_file_limit")
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError("duplicate_qa_json_key")
            out[key] = value
        return out
    def reject(_):
        raise ValueError("nonfinite_qa_json")
    return json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=reject)


def read_matrix() -> dict[str, Any]:
    value = read_json(MATRIX_PATH)
    if not isinstance(value, dict):
        raise ValueError("phase2_matrix_not_object")
    return expand_matrix(value)


def expand_matrix(value: dict[str, Any]) -> dict[str, Any]:
    """Expand only two explicit pinned-source references, preserving all duties.

    No executable expression or configurable path is accepted. The original
    Phase 1 matrix supplies method identities, never Phase 2 execution outcomes.
    """
    import copy
    value = copy.deepcopy(value)
    desc = value.get("catalogues")
    if isinstance(desc, dict) and desc.get("encoding") == "pinned_catalogues_v1":
        if set(desc) != {"encoding", "source_sha256", "expanded_sha256"} or desc["source_sha256"] != PHASE1_MATRIX_SHA256:
            raise ValueError("invalid_catalogue_reference")
        result = expected_catalogues()
        if sha256_bytes(canonical_bytes(result)) != desc["expanded_sha256"]:
            raise ValueError("catalogue_expansion_hash_mismatch")
        value["catalogues"] = result
    predecessor = value.get("predecessor")
    if isinstance(predecessor, dict) and isinstance(predecessor.get("test_ids"), dict):
        desc = predecessor["test_ids"]
        if desc != {"encoding": "pinned_predecessor_methods_v1", "source_sha256": PHASE1_MATRIX_SHA256,
                    "expanded_sha256": PREDECESSOR_IDS_SHA256}:
            raise ValueError("invalid_method_reference")
        if sha256_bytes((ROOT / "tests/phase1_matrix.json").read_bytes()) != PHASE1_MATRIX_SHA256:
            raise ValueError("predecessor_matrix_changed")
        found = set()
        def collect(v):
            if isinstance(v, dict):
                if isinstance(v.get("test_bindings"), list): found.update(v["test_bindings"])
                for child in v.values(): collect(child)
            elif isinstance(v, list):
                for child in v: collect(child)
        collect(load_phase1_matrix())
        ids = sorted(found)
        if sha256_bytes(("\n".join(ids) + "\n").encode()) != PREDECESSOR_IDS_SHA256:
            raise ValueError("predecessor_method_expansion_mismatch")
        predecessor["test_ids"] = ids
    return value


def expected_catalogues() -> dict[str, list[dict[str, Any]]]:
    """Preserve source row text and original M/V/E/D tags, never edit them."""
    if sha256_bytes((ROOT / "PHASE_2_PLAN.md").read_bytes()) != PLAN_SHA256:
        raise ValueError("approved_phase2_plan_changed")
    if sha256_bytes((ROOT / "tests/phase1_matrix.json").read_bytes()) != PHASE1_MATRIX_SHA256:
        raise ValueError("predecessor_matrix_changed")
    prior = load_phase1_matrix()
    specs = (("vt", "vf_tests", "VALIDATION_AND_FALSIFICATION.md", "VT"),
             ("tr", "trace_requirements", "THEORY_TO_CODE_TRACEABILITY.md", "TR"),
             ("rf", "report_groups", "THEORY_TO_CODE_TRACEABILITY.md", "RF"))
    catalogues = {}
    for key, field, filename, prefix in specs:
        rows = {row[0]: row for row in source_table(filename, prefix)}
        result = []
        for item in prior[field]:
            row = {"id": item["id"], "source_file": filename,
                   "source_row_sha256": sha256_bytes(canonical_bytes(rows[item["id"]]))}
            if key == "vt":
                row.update(scopes=sorted(item["scope_records"]),
                           m_regression=bool(item["m_required"]),
                           v_required="V" in item["scope_records"],
                           evidence_status="not_supplied" if "E" in item["scope_records"] else "not_applicable",
                           deferred_status="deferred" if "D" in item["scope_records"] else "not_applicable")
            else:
                row.update(vf_ids=item["vf_ids"], m_regression=bool(item["m_applicable"]),
                           v_required=bool(set(item["vf_ids"]) & set(V_IDS)))
                row["report_groups" if key == "tr" else "trace_ids"] = item["report_groups" if key == "tr" else "trace_ids"]
            result.append(row)
        catalogues[key] = result
    if [e["id"] for e in catalogues["vt"] if e["v_required"]] != list(V_IDS):
        raise ValueError("source_v_scope_changed")
    return catalogues


def _binding_errors(bindings: Any, name: str, *, empty_allowed: bool = True) -> list[str]:
    if not isinstance(bindings, list) or any(not isinstance(x, str) or not METHOD_PATTERN.fullmatch(x) for x in bindings):
        return [name + ":malformed_bindings"]
    result = []
    if len(set(bindings)) != len(bindings):
        result.append(name + ":duplicate_bindings")
    if not empty_allowed and not bindings:
        result.append(name + ":empty_bindings")
    return result


def validate_matrix(matrix: Any) -> list[str]:
    """Fail closed on malformed, renamed or missing requirements and scope drift."""
    if not isinstance(matrix, dict):
        return ["phase2_matrix_not_object"]
    errors = []
    if set(matrix) != ROOT_KEYS:
        errors.append("phase2_matrix_field_set")
    if matrix.get("schema_version") != "0.1" or matrix.get("phase") != 2 or matrix.get("project") != "StructDet-Bench":
        errors.append("phase2_matrix_identity")
    if matrix.get("approved_plan") != {"path": "PHASE_2_PLAN.md", "sha256": PLAN_SHA256}:
        errors.append("approved_plan_identity")
    if matrix.get("evidence_status") != "not_supplied" or matrix.get("deferred_status") != "deferred":
        errors.append("empirical_or_deferred_scope_changed")
    delivery = matrix.get("delivery", {})
    if not isinstance(delivery, dict):
        return errors + ["delivery_not_object"]
    step = delivery.get("step")
    if type(step) is not int or not 1 <= step <= 8 or delivery.get("phase") != 2:
        errors.append("invalid_phase2_step"); step = 1
    if delivery.get("final_owner_acceptance") != "not_established_by_software_tests":
        errors.append("owner_acceptance_not_a_test_result")
    if not isinstance(delivery.get("authorization"), dict) or not delivery["authorization"].get("owner_instruction"):
        errors.append("missing_authorization")
    try:
        expected = expected_catalogues()
    except (ValueError, OSError, KeyError):
        return errors + ["frozen_source_identity_failure"]
    if matrix.get("catalogues") != expected:
        errors.append("catalogue_differs_from_pinned_source")
    pred = matrix.get("predecessor", {})
    if not isinstance(pred, dict):
        return errors + ["predecessor_not_object"]
    if (pred.get("matrix_sha256") != PHASE1_MATRIX_SHA256 or pred.get("archive_sha256") != ARCHIVE_SHA256
            or pred.get("project_inventory_sha256") != INVENTORY_SHA256):
        errors.append("predecessor_identity_changed")
    ids = pred.get("test_ids", [])
    errors += _binding_errors(ids, "predecessor")
    if len(ids) != 503 or ids != sorted(set(ids)) or pred.get("test_ids_sha256") != PREDECESSOR_IDS_SHA256 or sha256_bytes(("\n".join(ids) + "\n").encode()) != PREDECESSOR_IDS_SHA256:
        errors.append("predecessor_test_id_inventory_changed")
    # Future stages may change only explicitly authorized predecessor files.
    if not isinstance(pred.get("file_manifest"), dict) or len(pred["file_manifest"]) != 67:
        errors.append("predecessor_file_inventory_incomplete")
    else:
        try:
            lines = "".join(value["sha256"] + "  " + path + "\n" for path, value in sorted(pred["file_manifest"].items()))
            if sha256_bytes(lines.encode()) != INVENTORY_SHA256:
                errors.append("predecessor_file_inventory_changed")
        except (TypeError, KeyError):
            errors.append("predecessor_file_inventory_malformed")
    groups = {
        "vt_obligations": list(V_IDS),
        "trace_requirements": [x["id"] for x in expected["tr"] if x["v_required"]],
        "report_groups": [x["id"] for x in expected["rf"] if x["v_required"]],
        "ec_requirements": [f"EC-C{x:02d}" for x in range(1, 9)],
        "engineering_requirements": [f"P2-ENG-{x:02d}" for x in range(1, 9)],
    }
    for group, expected_ids in groups.items():
        entries = matrix.get(group, [])
        if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
            errors.append(group + ":malformed"); continue
        if [e.get("id") for e in entries] != expected_ids:
            errors.append(group + ":identity_set_changed")
        for row in entries:
            ident = str(row.get("id"))
            if row.get("implementation_status") not in {"not_implemented", "partial", "implemented"}:
                errors.append(ident + ":invalid_implementation_state")
            if row.get("evidence_status") != "not_supplied":
                errors.append(ident + ":fixture_cannot_supply_E")
            due = 1 if group == "engineering_requirements" and ident in {f"P2-ENG-{i:02d}" for i in range(1, 7)} else 7
            if type(row.get("required_by_step")) is not int or row["required_by_step"] != due:
                errors.append(ident + ":invalid_due_step")
            errors += _binding_errors(row.get("test_bindings"), ident,
                                       empty_allowed=row.get("implementation_status") != "implemented")
    stages = matrix.get("stage_bindings", {})
    if not isinstance(stages, dict) or set(stages) != {str(i) for i in range(1, 9)}:
        errors.append("stage_bindings_missing")
    elif any(not isinstance(s, dict) for s in stages.values()):
        errors.append("stage_bindings_malformed")
    else:
        for number, row in stages.items():
            errors += _binding_errors(row.get("test_bindings"), "stage" + number,
                                       empty_allowed=int(number) > step)
            if row.get("implementation_status") not in {"not_implemented", "partial", "implemented"}:
                errors.append("stage" + number + ":invalid_state")
    limits = matrix.get("limits", {})
    if not isinstance(limits, dict) or limits.get("test_timeout_seconds") != 120:
        errors.append("unknown_harness_limit_profile")
    return sorted(set(errors))


def identity_checks(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare current immutable pins without running or fetching anything."""
    pins = {"PHASE_2_PLAN.md": PLAN_SHA256,
            "tests/phase1_matrix.json": PHASE1_MATRIX_SHA256}
    for path, entry in matrix["predecessor"]["file_manifest"].items():
        # The whole inherited tree is immutable for this initial harness step,
        # except the specifically permitted README handoff. QA is never replaced.
        if matrix["delivery"]["step"] == 1 and path != "README.md":
            pins[path] = entry["sha256"]
        elif path in matrix["predecessor"]["immutable_paths"]:
            pins[path] = entry["sha256"]
    results = []
    for relative, expected in sorted(pins.items()):
        actual = None
        path = ROOT / relative
        try:
            if path.is_symlink() or not path.is_file():
                raise ValueError("nonregular_pin")
            actual = sha256_bytes(path.read_bytes())
        except (OSError, ValueError):
            pass
        results.append({"path": relative, "expected_sha256": expected,
                        "actual_sha256": actual, "status": "passed" if actual == expected else "failed"})
    return results


def reconciliation_checks(record: Any, file_manifest: dict[str, Any]) -> list[str]:
    """Inspect the stored connector read-back; no network or guessed completion."""
    if not isinstance(record, dict):
        return ["baseline_reconciliation_missing"]
    errors = []
    if record.get("archive_sha256") != ARCHIVE_SHA256 or record.get("project_inventory_sha256") != INVENTORY_SHA256:
        errors.append("reconciliation_baseline_identity")
    if record.get("repository") != "DavidWallstructurallaw/structdet-bench":
        errors.append("reconciliation_repository_mismatch")
    if record.get("status") != "remote_verified":
        errors.append("phase1_remote_sync_pending")
    if record.get("scope") != "all_67_original_project_files":
        errors.append("reconciliation_scope_incomplete")
    if record.get("readback_complete") is not True:
        errors.append("remote_readback_incomplete")
    commit = record.get("accepted_phase1_commit")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        errors.append("accepted_phase1_commit_missing")
    if record.get("remote_files") != file_manifest:
        errors.append("remote_original_file_inventory_not_matched")
    return sorted(set(errors))


def comparison_fixture(root: Path, *, role="fixture"):
    """Mock study records only. Prompts are transcribed independently from HERO.

    Creates no candidate programs, classifications or empirical observations.
    All temporary inputs and reviewer/control records are explicitly stipulated.
    """
    from copy import deepcopy
    from tests.helpers import minimal_manifest, tagged, record_ref, support_record, artifact_record, rewrite_evidence_bundle
    root.mkdir(parents=True, exist_ok=True)
    m = minimal_manifest(); cell = deepcopy(m["cells"][0]); protocol = deepcopy(m["protocols"][0])
    m["cells"] = []; m["protocols"] = []; m["data_role"] = role
    cfg = m["analysis_config"]; cfg["selection"] = []; cfg["assignment_pins"] = []; cfg["validity_pins"] = []; cfg["requested_k"] = []
    m["record_files"].append({"role":"evidence","format":"jsonl","path":"evidence.jsonl","expected_sha256":tagged(state="unknown")})
    text = (ROOT/"HERO_BENCHMARK_SPEC.md").read_text().split("### 7.2 Exact visible prompt assembly")[1].split("### 7.3")[0]
    openers = dict(re.findall(r"\| (P0[1-6]) \| `([^`]+)` \|", text))
    task, ab, c, output = re.findall(r"```text\n(.*?)\n```", text, re.S)
    o = []; s = [support_record("role","binding-reviewer",entity_type="human",role="fixture-observer",entity_id=tagged("MOCK-OBSERVER"))]; blocks = []
    permutations = ("ABC","ACB","BAC","BCA","CAB","CBA")
    for b, (bid, opener) in enumerate(openers.items(),1):
        block = {"block_id":bid,"conditions":{}}
        for cond in "ABC":
            cid = bid+"-"+cond; pid = "protocol-"+cid; aid = "prompt-"+cid; eid = "study-"+cid
            cr = deepcopy(cell); cr.update(record_id=cid,analysis_cell_id=cid,prompt_block_id=bid,prompt_id=aid,condition_id=cond,generation_protocol_id=pid,
                model_identifier=tagged("MOCK-MODEL"),model_family=tagged("MOCK-FAMILY"),checkpoint_identifier=tagged("MOCK-STATE"),collection_window=tagged("MOCK-WINDOW"));m["cells"].append(cr)
            settings = {"temperature":1.0 if cond=="B" else 0.4,"top_p":1.0,"presence_penalty":0,"frequency_penalty":0,"max_output_tokens":8192}
            pr = deepcopy(protocol);pr.update(record_id=pid,generation_protocol_id=pid,decoding_settings=tagged(settings),seed=tagged(None),conditioning_context_ref=tagged(record_ref("artifact",aid)));m["protocols"].append(pr)
            content = "\n\n".join((opener,task,ab if cond in "AB" else c,output)).encode();(root/(aid+".txt")).write_bytes(content)
            ar = artifact_record(aid,aid+".txt");ar["expected_sha256"]=tagged(sha256_bytes(content));o.append(ar)
            proofref=record_ref("evidence","controls-"+cid)
            values=dict(settings,generator_seed=None,tools=False,retrieval=False,history=False,best_of=1)
            controls={k:{"requested":tagged(v),"actual":tagged(v),"enforcement":"recorded","evidence_refs":[proofref]} for k,v in values.items()}
            s.append(support_record("evidence","controls-"+cid,target_ref=record_ref("cell",cid),purpose="observation",method=tagged("recorded_control_observation"),
                reviewer_refs=[record_ref("role","binding-reviewer")],extensions={"recorded_controls":{k:{p:v[p] for p in ("requested","actual","enforcement")} for k,v in controls.items()},"recorded_deployment":{"serving_identity":tagged("MOCK-DEPLOYMENT"),"change_detected":tagged(False)}}))
            budgetref=record_ref("budget","budget-"+cid)
            s.append(support_record("budget","budget-"+cid,scope_refs=[record_ref("cell",cid)],planned=tagged({"calls":4,"candidate_positions":20,"output_cap_per_call":8192}),actual=tagged(state="unknown")))
            attempts=[]
            for g in range(1,5):
                rid=f"call-{cid}-{g}";o.append({**record_ref("attempt",rid),"attempt_id":rid,"analysis_cell_id":cid,"attempt_status":"succeeded",
                    "raw_response_ref":tagged(state="unknown"),"retry_of":tagged(None),"generation_group_id":tagged(f"group-{cid}-{g}"),"planned_candidate_count":tagged(5),"registered_call_order":tagged(g)})
                order=(g-1)*18+(b-1)*3+permutations[(b+g-2)%6].index(cond)+1
                attempts.append({"group_index":g,"attempt_ref":tagged(record_ref("attempt",rid)),"global_order":tagged(order),"recorded_at":tagged("2026-09-01T01:00:00+00:00")})
            study={"version":"0.1","comparison_id":"comparison-fixture","comparison_version":"0.1","block_id":bid,"condition_id":cond,"protocol_ref":record_ref("protocol",pid),
                "sent_prompt":{"artifact_ref":tagged(record_ref("artifact",aid)),"attestation_ref":tagged(state="unknown")},
                "visible_system_instruction":tagged(None),"platform_context":tagged(None),"reasoning":tagged(None),"controls":controls,
                "cap":{"unit":tagged("model_tokens"),"tokenizer":tagged("MOCK-TOKENIZER"),"convention":tagged("visible_output_only")},
                "budget_ref":tagged(budgetref),"attempts":attempts,"automatic_retries":tagged(False),"deployment":{"serving_identity":tagged("MOCK-DEPLOYMENT"),"change_detected":tagged(False),"evidence_refs":[proofref]},"deviations":[]}
            s.append(support_record("evidence",eid,target_ref=record_ref("cell",cid),purpose="observation",method=tagged("study_binding_v1"),reviewer_refs=[record_ref("role","binding-reviewer")],
                scope_refs=[record_ref("cell",cid),record_ref("protocol",pid)],artifact_refs=[record_ref("artifact",aid)],extensions={"study_binding":study}))
            block["conditions"][cond]={"cell_ref":record_ref("cell",cid),"study_record_ref":record_ref("evidence",eid)}
            cfg["selection"].append({"analysis_cell_id":cid,"selected_sample_ids":tagged([]),"sample_order":tagged([]),"registered_positions":tagged(state="unknown"),"selection_basis":tagged("No generated observations in this fixture")})
        blocks.append(block)
    comparison={"comparison_schema_version":"0.1","comparison_id":"comparison-fixture","comparison_version":"0.1","profile":"hero_sort_abc_v1","blocks":blocks,"pilot_cell_refs":[],"questions":["P1","P5"],"views":["classified_all","classified_valid"],
        "evidence":{k:[] for k in ("registration","exposure","structural_validation","core_audit","integrity","independence","correction")},
        "text_method":{"extraction_rule_version":tagged("fixture-original-region-v1"),"encoding":"utf-8","proxy_version":"surface_lexical_trigram_jaccard_v1","unicode_category_version":tagged(state="unknown"),"white_space_version":tagged(state="unknown"),"white_space_sha256":tagged(state="unknown")},
        "resampling":{"method":"paired_prompt_block_bootstrap_v1","seed":20260917,"replicates":2000,"probabilities":["0.025","0.975"],"quantile":"linear_b_minus_one_v1","dependence_assessment_ref":tagged(state="unknown"),"replay_ref":tagged(None)},
        "limits":{"max_lexical_units":100000,"max_pairs":100000,"max_trigram_visits":100000000,"max_exact_bits":131072},
        "revision":{"prior_comparison_ids":[],"prior_run_ids":[],"reason":tagged(state="not_applicable",reason="Initial fixture"),"changes":[]}}
    cfg.setdefault("extensions",{})["comparison"]=comparison
    return rewrite_evidence_bundle(root,o,s,m),o,s,m
