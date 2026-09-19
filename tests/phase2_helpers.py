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
    storage = value.get("delivery", {}).pop("binding_storage", None)
    if storage is not None:
        if (not isinstance(storage, dict) or set(storage) != {"encoding", "pool", "expanded_sha256"}
                or storage["encoding"] != "explicit_binding_dictionary_v1"):
            raise ValueError("invalid_binding_dictionary")
        pool = storage["pool"]
        if (not isinstance(pool, list) or not 1 <= len(pool) <= 20000
                or any(not isinstance(x, str) or not METHOD_PATTERN.fullmatch(x) for x in pool)
                or pool != sorted(set(pool))):
            raise ValueError("invalid_binding_dictionary_pool")
        def expand(item):
            if isinstance(item, dict):
                for key, child in list(item.items()):
                    if key == "test_bindings" and isinstance(child, dict):
                        if set(child) != {"encoding", "indices", "sha256"} or child["encoding"] != "binding_indices_v1":
                            raise ValueError("invalid_binding_list_reference")
                        indices = child["indices"]
                        if (not isinstance(indices, list) or len(indices) > len(pool)
                                or any(type(i) is not int or not 0 <= i < len(pool) for i in indices)
                                or len(set(indices)) != len(indices)):
                            raise ValueError("invalid_binding_dictionary_index")
                        names = [pool[i] for i in indices]
                        if sha256_bytes(canonical_bytes(names)) != child["sha256"]:
                            raise ValueError("binding_list_hash_mismatch")
                        item[key] = names
                    else:
                        expand(child)
            elif isinstance(item, list):
                for child in item: expand(child)
        expand(value)
        if sha256_bytes(canonical_bytes(value)) != storage["expanded_sha256"]:
            raise ValueError("expanded_binding_matrix_hash_mismatch")
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


def populated_comparison_fixture(root: Path, *, blocks=('P01',), labels=None,
                                 validity=None, texts=None):
    """Trusted Step 4 component fixture with actual text and stipulated labels.

    The full intended six-block role list stays registered. Absent blocks stay
    absent, never silently changing the primary target. Repeated text has one
    consistent structural label. There are no model calls or executed programs.
    """
    from copy import deepcopy
    from tests.helpers import (tagged, record_ref, support_record, artifact_record,
                                sample_record, assignment_record, rewrite_evidence_bundle)
    from structdet_bench.text_diagnostics import WHITE_SPACE_SHA256
    p,o,s,m=comparison_fixture(root)
    cfg=m['analysis_config'];cmp=cfg['extensions']['comparison']
    labels=labels or {};validity=validity or {};texts=texts or {}
    kept={bid+'-'+c for bid in blocks for c in 'ABC'}
    m['cells']=[c for c in m['cells'] if c['analysis_cell_id'] in kept]
    m['protocols']=[r for r in m['protocols'] if r['generation_protocol_id'][9:] in kept]
    cfg['selection']=[r for r in cfg['selection'] if r['analysis_cell_id'] in kept]
    cfg['requested_k']=[5,10,20]
    cmp['text_method'].update(unicode_category_version=tagged('15.1.0'),white_space_version=tagged('15.1.0'),
                               white_space_sha256=tagged(WHITE_SPACE_SHA256))
    o=[r for r in o if r['record_type']!='attempt' or r['analysis_cell_id'] in kept]
    for sel in cfg['selection']:
        cid=sel['analysis_cell_id'];condition=cid[-1]
        labs=list(labels.get(cid, ['SORT-ADJ']*20 if condition!='C' else ['SORT-ADJ']*10+['SORT-INS']*10))
        vals=list(validity.get(cid,['valid']*len(labs)))
        bodies=texts.get(cid)
        if bodies is None:
            bodies=[('a b c' if condition!='B' or i%2==0 else 'a b d') if label in (None,'SORT-ADJ')
                    else 'mechanism '+label+' x' for i,label in enumerate(labs)]
        if len(vals)!=len(labs) or len(bodies)!=len(labs):raise ValueError('bad component fixture dimensions')
        selected=[]
        for i,(label,v,body) in enumerate(zip(labs,vals,bodies),1):
            sid=f'{cid}-s{i}';aid=f'{cid}-a{i}';vid=f'{cid}-v{i}';g=(i-1)//5+1;pos=(i-1)%5+1
            sample=sample_record(sid);sample.update(analysis_cell_id=cid,sample_order=tagged(i),
                attempt_id=tagged(f'call-{cid}-{g}'),generation_group_id=tagged(f'group-{cid}-{g}'),
                within_group_index=tagged(pos),extraction_rule_version=tagged('fixture-original-region-v1'))
            if body is None:
                sample['output_ref']=tagged(state='unavailable',reason='Stipulated missing proxy bytes')
                sample['output_content_hash']=tagged(state='unknown')
            else:
                data=body.encode() if isinstance(body,str) else body
                rid='text-'+sid;fn=rid+'.txt';(root/fn).write_bytes(data)
                artifact=artifact_record(rid,fn);artifact['expected_sha256']=tagged(sha256_bytes(data));o.append(artifact)
                sample['output_ref']=tagged(record_ref('artifact',rid));sample['output_content_hash']=tagged(sha256_bytes(data))
            a=assignment_record(aid,sid);a.update(structural_class_id=label,assignment_status='assigned' if label else 'unresolved')
            val={**record_ref('validity',vid),'validity_id':vid,'validity_version':'0.1','sample_id':sid,
                 'validity_status':v,'validity_review_status':'fixture','validity_rubric_ref':tagged('bounded_integer_sort_validity_v1'),
                 'decision_rationale':tagged('Stipulated Step 4 fixture'),'supersedes_validity_id':tagged(None),'evidence_refs':[]}
            for axis,row,outcome in (('assignment',a,label),('validity',val,v)):
                eid='e-'+row['record_id'];row['evidence_refs']=[record_ref('evidence',eid)]
                s.append(support_record('evidence',eid,target_ref=record_ref(axis,row['record_id']),
                    purpose='fixture_declaration',assertion=tagged(outcome),method=tagged('stipulated'),
                    detail=tagged('Software component fixture; no empirical evidence'),access='readable',conflict_status='none_declared'))
                cfg[axis+'_pins'].append({'sample_id':sid,axis+'_id':row['record_id'],axis+'_version':'0.1'})
            o.extend([sample,a,val]);selected.append(sid)
        sel['selected_sample_ids']=tagged(selected);sel['sample_order']=tagged(selected)
        sel['selection_basis']=tagged('Prospective fixed fixture positions before outcome conditioning')
    return rewrite_evidence_bundle(root,o,s,m),o,s,m


# Step 5 test builders. Every assumed person, assessment and outcome is stipulated.
def paired_summary_fixture(surface=None, structural=None, *, p5=None, pair='B-A',
                           view='classified_all', blocks=None, gated=True,
                           subset=False):
    """Independent exact test arithmetic; no model study or evidence acquisition."""
    from fractions import Fraction
    from structdet_bench.comparisons import BlockSummary, number
    from structdet_bench.contracts import freeze
    ids=tuple(blocks or ('P01','P02','P03','P04','P05','P06'))
    question='P5' if p5 is not None else 'P1'
    def vector(x):
        values=list(x) if isinstance(x,(list,tuple)) else [x]*len(ids)
        if len(values)!=len(ids):raise ValueError('fixture_block_length')
        return [Fraction(v) for v in values]
    if question=='P1':
        a,b=vector(surface or '0'),vector(structural or '0')
        arrays={'surface_gain':a,'structural_gain':b,'p1_proxy_gain_contrast':[x-y for x,y in zip(a,b)]}
        unit='dimensionless_distinct_observation_pair_mean'
    else:
        arrays={'p5_valid_distinct_k_delta':vector(p5)};unit='classes_among_k_realization_prefix'
        view='classified_valid'
    rows={bid:{name:number(name,unit,values[i]) for name,values in arrays.items()} for i,bid in enumerate(ids)}
    means={name:number(name,unit,sum(values,Fraction())/len(ids)) for name,values in arrays.items()}
    full=ids==('P01','P02','P03','P04','P05','P06')
    return BlockSummary(question,pair,view,'available_block_descriptive_subset' if subset else 'full_intended_target',
        ('P01','P02','P03','P04','P05','P06'),ids,freeze({b:('fixture_missing',) for b in ('P01','P02','P03','P04','P05','P06') if b not in ids}),
        freeze({} if gated else {ids[0]:('fixture_endpoint_gate_failed',)}),freeze(means),freeze(rows),full,full and gated)


def add_fixture_dependence(observations, supports, manifest):
    """Add an explicit mock resampling assumption; never independent evidence."""
    from tests.helpers import support_record, record_ref, tagged
    cfg=manifest['analysis_config']['extensions']['comparison']
    evidence=record_ref('evidence','resampling-assumption')
    supports.append(support_record('evidence','resampling-assumption',purpose='observation',
        target_ref=record_ref('role','binding-reviewer'),method=tagged('stipulated_resampling_assumption'),
        reviewer_refs=[record_ref('role','binding-reviewer')]))
    supports.append(support_record('independence_assessment','paired-dependence',
        left_ref=record_ref('cell',manifest['cells'][0]['record_id']),
        right_ref=record_ref('cell',manifest['cells'][-1]['record_id']),
        dimension='paired_prompt_block_resampling',outcome='supported_for_scope',
        criterion=tagged('Stipulated fixed-block applicability, software test only'),
        scope_refs=[record_ref('cell',c['record_id']) for c in manifest['cells']],
        reviewer_refs=[record_ref('role','binding-reviewer')],evidence_refs=[evidence],
        extensions={'paired_block_dependence':{'version':'0.1','block_ids':['P01','P02','P03','P04','P05','P06'],
            'unit':'paired_prompt_block','target':'fixed_wording_suite',
            'cross_block_shared_history':tagged(False),'condition_pairs':['B-A','C-A','C-B']}}))
    cfg['resampling']['dependence_assessment_ref']=tagged(record_ref('independence_assessment','paired-dependence'))


# Step 6 fixture helpers are trusted test utilities; the runtime never imports them.
ABC_WORDS = ('a b c','a b d','e f g','h i j','k l m','n o p','q r s','t u v')
ABC_CLASSES = ('SORT-ADJ','SORT-ADJ','SORT-INS','SORT-SEL','SORT-MERGE','SORT-PIVOT','SORT-HEAP','SORT-COUNT')


def materialize_abc(root: Path, variant='ABC-00'):
    """Copy a pinned fixture, apply only a registered test variant, then rehash.

    No model data are collected. Identity is per stipulated occurrence, while
    repeated exact text always has one current deterministic mechanism label.
    """
    import copy, shutil
    from tests.helpers import tagged, record_ref, support_record
    catalogue=read_json(ROOT/'tests/fixtures/comparison_variants.json')
    choices={r['id']:r for r in catalogue['variants']}
    if variant not in choices: raise ValueError('unregistered_abc_variant')
    source=ROOT/'examples/hero_abc'
    for name,sha in catalogue['base_sha256'].items():
        if sha256_bytes((source/name).read_bytes())!=sha: raise ValueError('abc_fixture_hash_mismatch')
    if root.exists(): raise ValueError('fixture_destination_exists')
    shutil.copytree(source,root)
    m=read_json(root/'bundle.json')
    obs=[json.loads(x) for x in (root/'records.jsonl').read_text().splitlines()]
    sup=[json.loads(x) for x in (root/'evidence.jsonl').read_text().splitlines()]
    cfg=m['analysis_config'];cmp=cfg['extensions']['comparison']
    byid={x['record_id']:x for x in obs};proof={x['record_id']:x for x in sup}
    def set_text(cid,indices):
        for i,n in enumerate(indices,1):
            sid=f'{cid}-s{i}';a=byid[f'{cid}-a{i}'];sample=byid[sid]
            artifact=byid['text-'+sid];body=(root/f'text_{n:02}.txt').read_bytes()
            artifact['content_ref']=tagged({'kind':'local','path':f'text_{n:02}.txt'})
            artifact['expected_sha256']=tagged(sha256_bytes(body));sample['output_content_hash']=tagged(sha256_bytes(body))
            a['structural_class_id']=ABC_CLASSES[n-1]
            proof['e-'+a['record_id']]['payload']['assertion']=tagged(ABC_CLASSES[n-1])
    blocks=[f'P{i:02}' for i in range(1,7)]
    if variant=='ABC-CONTRARY':
        for b in blocks:set_text(b+'-A',[1,2]*10);set_text(b+'-B',[1]*20)
    elif variant=='ABC-MIXED':
        for b in blocks:set_text(b+'-B',[1]*7+[3]*7+[4]*6)
    elif variant=='ABC-HETEROGENEOUS':
        for b in blocks[:2]:set_text(b+'-A',[1,2]*10);set_text(b+'-B',[1]*20)
    elif variant=='ABC-NO-TEXT':
        for row in obs:
            if row['record_type']=='realization':row['output_ref']=tagged(state='unavailable',reason='Stipulated unavailable proxy text')
    elif variant=='ABC-NO-B-CONTROL':
        for b in blocks:
            c=proof['study-'+b+'-B']['payload']['extensions']['study_binding']['controls']['temperature']
            c['actual']=tagged(state='unknown');c['enforcement']='hidden'
            proof['controls-'+b+'-B']['payload']['extensions']['recorded_controls']['temperature']={k:c[k] for k in ('requested','actual','enforcement')}
    elif variant=='ABC-MISSING-BLOCK':
        obs[:]=[r for r in obs if not(r['record_type']=='realization' and r['analysis_cell_id'].startswith('P06'))]
        for sel in cfg['selection']:
            if sel['analysis_cell_id'].startswith('P06'):
                sel['selected_sample_ids']=tagged([]);sel['sample_order']=tagged([])
    elif variant=='ABC-CORRECTED':
        for b in blocks:
            for i in range(11,21):
                old=byid[f'{b}-C-a{i}'];new=copy.deepcopy(old);new.update(record_id=old['record_id']+'-r2',assignment_id=old['record_id']+'-r2',assignment_version='0.2',structural_class_id='SORT-ADJ',supersedes_assignment_id=tagged(old['record_id']))
                eid='e-'+new['record_id'];new['evidence_refs']=[record_ref('evidence',eid)]
                e=copy.deepcopy(proof['e-'+old['record_id']]);e['record_id']=eid;e['payload'].update(target_ref=record_ref('assignment',new['record_id']),assertion=tagged('SORT-ADJ'))
                obs.append(new);sup.append(e)
                pin=next(p for p in cfg['assignment_pins'] if p['sample_id']==old['sample_id']);pin.update(assignment_id=new['record_id'],assignment_version='0.2')
        cmp['revision'].update(prior_comparison_ids=['prior-fixture-comparison'],prior_run_ids=['prior-fixture-run'],reason=tagged('Stipulated correction: all current text_03 occurrences reclassified; no new observations.'),changes=['membership_revision'])
    elif variant=='ABC-QUALITY':
        for b in blocks:
            set_text(b+'-C',[3]*5+[4]*5+[5]*5+[6]*5)
            for i in range(16,21):
                row=byid[f'{b}-C-v{i}'];row['validity_status']='invalid';proof['e-'+row['record_id']]['payload']['assertion']=tagged('invalid')
    elif variant=='ABC-INDEPENDENCE-WITHDRAWN':
        sup.append(support_record('correction','withdrawn-independence',effect='independence',action='withdraw',stage='applied',target_refs=[record_ref('frame','frame1')],reason=tagged('Stipulated evidence withdrawal'),evidence_refs=[record_ref('evidence','resampling-assumption')],reviewer_refs=[record_ref('role','binding-reviewer')]))
    elif variant=='ABC-TEXT-CHANGED':
        (root/'text_02.txt').write_bytes(b'a b c')
        for row in obs:
            if row['record_type']=='artifact' and row['content_ref']['value'].get('path')=='text_02.txt':row['expected_sha256']=tagged(sha256_bytes(b'a b c'))
            if row['record_type']=='realization' and row['analysis_cell_id'].endswith('-B') and int(row['sample_id'].rsplit('s',1)[1])%2==0:row['output_content_hash']=tagged(sha256_bytes(b'a b c'))
    elif variant=='ABC-P5-ONLY':cmp['questions']=['P5']
    elif variant!='ABC-00':raise ValueError('unsupported_registered_variant')
    # The original source and previous variant are never mutated.
    if variant!='ABC-00':
        m['extensions']['fixture_id']=variant
        write_abc(root,obs,sup,m)
    return root/'bundle.json',choices[variant]


def write_abc(root, obs, sup, m):
    """Trusted test serialization; no implicit modification by runtime."""
    from tests.helpers import tagged
    for name,records in (('records.jsonl',obs),('evidence.jsonl',sup)):
        data=b''.join(canonical_bytes(row) for row in records);(root/name).write_bytes(data)
    for f in m['record_files']:f['expected_sha256']=tagged(sha256_bytes((root/f['path']).read_bytes()))
    (root/'bundle.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    return root/'bundle.json'


def independent_abc_expected(variant='ABC-00'):
    """Independent finite enumeration using hand-specified three-word sets.

    Does not import production tokenization, metrics, comparisons, quantiles or
    outcome functions. Random reference uses getrandbits rejection, not randrange.
    """
    from fractions import Fraction as F
    from itertools import combinations
    import random
    indices=[];rng=random.Random(20260917)
    for _ in range(2000):
        row=[]
        while len(row)<6:
            draw=rng.getrandbits(3)
            if draw<6:row.append(draw)
        indices.append(row)
    expected={};p1=[]
    sets=[{('<B>',*s.split()[:2]),tuple(s.split()),(*s.split()[1:],'<E>')} for s in ABC_WORDS]
    for b in range(1,7):
        a=[1]*20;bb=[1,2]*10;c=[1]*10+[3]*10
        if variant=='ABC-CONTRARY' or (variant=='ABC-HETEROGENEOUS' and b<=2):a,bb=bb,a
        if variant=='ABC-MIXED':bb=[1]*7+[3]*7+[4]*6
        values={}
        for cond,seq in [('A',a),('B',bb),('C',c)]:
            pairs=list(combinations(seq,2));n=len(pairs)
            ds=[F(len(sets[x-1]|sets[y-1])-len(sets[x-1]&sets[y-1]),len(sets[x-1]|sets[y-1])) for x,y in pairs]
            q=F(sum(ABC_CLASSES[x-1]!=ABC_CLASSES[y-1] for x,y in pairs),n)
            within=[d for d,(x,y) in zip(ds,pairs) if ABC_CLASSES[x-1]==ABC_CLASSES[y-1]]
            values[cond]={'L':sum(ds,F())/n,'Q':q,'within':sum(within,F())/len(within),'support':len(set(ABC_CLASSES[x-1] for x in seq)), 'pairs':n}
            expected[f'P{b:02}-{cond}']=values[cond]
        p1.append(values['B']['L']-values['A']['L']-(values['B']['Q']-values['A']['Q']))
    sampled=sorted(sum((p1[i] for i in row),F())/6 for row in indices)
    def quant(q):
        rank=q*1999;i=rank.numerator//rank.denominator;t=rank-i
        return sampled[i]+t*(sampled[i+1]-sampled[i])
    return {'cells':expected,'p1_mean':sum(p1,F())/6,'p1_lower':quant(F(1,40)),'p1_upper':quant(F(39,40)),
            'indices_sha256':sha256_bytes(canonical_bytes(indices)), 'data_role':'fixture',
            'oracle_method':'hand_specified_sets_and_independent_fraction_enumeration'}
