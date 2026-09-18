"""Passive Phase 2 study binding. No scores, generators, classification or I/O.

Consumes LoadedBundle snapshots and existing EvidenceIndex record checks.
Record consistency does not certify independent evidence or a causal manipulation.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from typing import Any, Mapping
from .contracts import ExactNumber, InputError, freeze, is_hash, is_id, knowledge, validate_ref
from .evidence import EvidenceIndex
from .local_io import LoadedBundle

PROFILE = "hero_sort_abc_v1"
BLOCKS = tuple(f"P{i:02}" for i in range(1, 7))
CONDITIONS = ("A", "B", "C")
PERMUTATIONS = ("ABC", "ACB", "BAC", "BCA", "CAB", "CBA")
MAX_LINKS = 4096
TOP_KEYS = "comparison_schema_version comparison_id comparison_version profile blocks pilot_cell_refs questions views evidence text_method resampling limits revision".split()
STUDY_KEYS = "version comparison_id comparison_version block_id condition_id protocol_ref sent_prompt visible_system_instruction platform_context reasoning controls cap budget_ref attempts automatic_retries deployment deviations".split()
FRAME_FIELDS = "task_id task_version task_context consequence_horizon analytic_resolution_id analytic_resolution_version structural_schema_id structural_schema_version reference_registry_id reference_registry_version validity_rubric_ref load_bearing_invariants consequence_signature_spec equivalence_rule_ref admissible_substitutions evidence_requirement exceptional_case_rules".split()
EVIDENCE_KINDS = {"registration": {"preregistration"}, "exposure": {"exposure"},
    "structural_validation": {"evidence", "domain_suite"}, "core_audit": {"audit", "domain_suite"},
    "integrity": {"integrity_assessment"}, "independence": {"independence_assessment"}, "correction": {"correction"}}
CONTROL_VALUES = {"temperature": None, "top_p": Decimal(1), "presence_penalty": Decimal(0),
    "frequency_penalty": Decimal(0), "generator_seed": None, "max_output_tokens": 8192,
    "tools": False, "retrieval": False, "history": False, "best_of": 1}
# Literal transcription of HERO 7.2, checked independently in tests.
OPENERS = {'P01': 'Implement the sorting function specified below.', 'P02': 'Write implementations for the following integer-sorting task.', 'P03': 'Provide programs that meet this sorting specification.', 'P04': 'Solve the following bounded integer-ordering problem in Python.', 'P05': 'Create implementations of the function described below.', 'P06': 'Produce Python solutions for this list-sorting interface.'}
TASK_TEXT = 'Define sort_values(values) in Python 3.\n\nThe input is a plain list of plain integers. Its length is from 0 through 256 inclusive. Every integer is from 0 through 4095 inclusive. Return a new plain list containing the same integers with the same multiplicities, in nondecreasing order. Do not change the input list. Your program must handle the entire stated domain, including empty lists and repeated values.\n\nAdditional local memory is allowed. There is no requirement to sort in place, preserve the identities of equal records, or meet a particular asymptotic running-time bound. Only integers are supplied.\n\nUse self-contained source with all helper functions included. Do not use imports, sorted, any .sort method, or another external ordering routine. Ordinary loops, recursion, comparisons, integer arithmetic, local containers, and basic built-ins such as len, range, enumerate, list, min, and max are allowed. Do not use randomness, dynamic code execution, reflection, filesystem or network access, subprocesses, or persistent state. Each candidate must work by itself without code from another candidate.'
AB_CLAUSE = 'Produce five versions of a solution to this task.'
C_CLAUSE = 'Produce five solutions to this task using five different ordering mechanisms. Differences only in names, comments, formatting, or local implementation details do not count as different mechanisms. Keep the task and its constraints unchanged.'
OUTPUT_TEXT = 'Return exactly five numbered sections headed ### Candidate 1 through ### Candidate 5, in that order. Each section must contain exactly one fenced python code block holding a complete independent program that defines sort_values(values). Put helpers inside that same code block. Include no prose outside the code blocks apart from the five section headings. Comments inside the code are allowed. Do not supply tests, examples, imports, or a main program.'

@dataclass(frozen=True)
class Fact:
    name: str
    status: str
    reasons: tuple[str, ...] = ()
    observed: Any = field(default=None, repr=False)
    expected: Any = field(default=None, repr=False)
    evidence_refs: tuple[Any, ...] = field(default=(), repr=False)
    mock: bool = False
    substantive_validation_performed: bool = False

@dataclass(frozen=True)
class CellBinding:
    block_id: str
    condition_id: str
    cell_id: str
    status: str
    facts: tuple[Fact, ...]
    frame: Any = field(default=None, repr=False)
    study: Any = field(default=None, repr=False)
    cell: Any = field(default=None, repr=False)
    budget: Any = field(default=None, repr=False)
    recorded_attempt_ids: tuple[str, ...] = ()
    extra_attempt_ids: tuple[str, ...] = ()

@dataclass(frozen=True)
class PairBinding:
    block_id: str
    contrast: str
    cell_ids: tuple[str, str]
    facts: tuple[Fact, ...]
    endpoint_eligibility_evaluated: bool = False

@dataclass(frozen=True)
class ComparisonReview:
    requested: bool
    status: str
    comparison_id: str | None
    material_role: str | None
    configuration: Any = field(repr=False)
    bindings: tuple[CellBinding, ...] = ()
    pairs: tuple[PairBinding, ...] = ()
    facts: tuple[Fact, ...] = ()
    unbound_cell_ids: tuple[str, ...] = ()
    independent_validation_performed: bool = False
    endpoint_eligibility_evaluated: bool = False


def _obj(v, keys):
    if not isinstance(v, Mapping) or set(v) != set(keys): raise InputError("comparison_field_set")
    return v

def _seq(v, maximum=MAX_LINKS):
    if not isinstance(v, (list, tuple)) or len(v) > maximum: raise InputError("comparison_list_or_limit")
    return tuple(v)

def _ref(v, kinds):
    validate_ref(v)
    if v["record_type"] not in kinds: raise InputError("comparison_reference_type")
    return v

def _key(v): return v["record_type"], v["record_id"]

def _tag(v, predicate=lambda _: True):
    k = knowledge(v)
    if k.state == "known" and not predicate(k.value): raise InputError("comparison_known_value_type")
    return k

def _value(v):
    k = knowledge(v)
    return k.value if k.state == "known" else None

def _text(v): return isinstance(v, str) and bool(v.strip())

def _number(v):
    return Decimal(v) if type(v) is int else v.decimal if isinstance(v, ExactNumber) else None

def _time(v):
    k = _tag(v, _text)
    if k.state != "known": return None
    try:
        result = datetime.fromisoformat(k.value)
        if result.tzinfo is None: raise ValueError
        return result
    except ValueError as exc: raise InputError("comparison_timestamp_offset_required") from exc

def _fact(name, okay, observed=None, expected=None, reason=None, refs=(), mock=False):
    status = "unresolved" if okay is None else "record_consistent" if okay else "inconsistent"
    return Fact(name, status, () if okay else (reason or name + "_" + status,),
                freeze(observed), freeze(expected), tuple(freeze(r) for r in refs), mock)

def _state(facts):
    statuses = {f.status for f in facts}
    return "contract_error" if "contract_error" in statuses else "record_limited" if statuses & {"unresolved", "inconsistent"} else "record_consistent"

def registered_prompt_bytes(block: str, condition: str) -> bytes:
    """Registered comparison reference only, never sent. No terminal LF added."""
    if not isinstance(block, str) or block not in OPENERS or condition not in CONDITIONS:
        raise InputError("unsupported_prompt_role")
    return "\n\n".join((OPENERS[block], TASK_TEXT, AB_CLAUSE if condition in ("A", "B") else C_CLAUSE, OUTPUT_TEXT)).encode("utf-8")

def configuration_fingerprint(config: Mapping[str, Any]) -> str:
    """Domain-tagged canonical identity. Preserves exact numeric token spelling."""
    def tagged(v):
        if isinstance(v, Mapping): return ["object", [[k, tagged(x)] for k, x in sorted(v.items())]]
        if isinstance(v, (list, tuple)): return ["array", [tagged(x) for x in v]]
        if isinstance(v, ExactNumber): return ["number_token", v.token]
        return [type(v).__name__, v]
    return hashlib.sha256(json.dumps(tagged(config), ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def _shape(raw):
    c = _obj(raw, TOP_KEYS)
    if c["comparison_schema_version"] != "0.1" or c["profile"] != PROFILE: raise InputError("unsupported_comparison_profile_or_version")
    if not all(is_id(c[k]) for k in ("comparison_id", "comparison_version")): raise InputError("comparison_identity")
    blocks = _seq(c["blocks"], 6)
    if len(blocks) != 6 or tuple(b.get("block_id") if isinstance(b, Mapping) else None for b in blocks) != BLOCKS:
        raise InputError("comparison_fixed_blocks_required")
    for b in blocks:
        _obj(b, {"block_id", "conditions"})
        for e in _obj(b["conditions"], CONDITIONS).values():
            _obj(e, {"cell_ref", "study_record_ref"}); _ref(e["cell_ref"], {"cell"}); _ref(e["study_record_ref"], {"evidence"})
    for ref in _seq(c["pilot_cell_refs"], 3): _ref(ref, {"cell"})
    qs = _seq(c["questions"], 2)
    if not qs or any(q not in ("P1", "P5") for q in qs) or len(set(qs)) != len(qs): raise InputError("comparison_questions")
    if _seq(c["views"], 2) != ("classified_all", "classified_valid"): raise InputError("comparison_required_views")
    for group, refs in _obj(c["evidence"], EVIDENCE_KINDS).items():
        keys = [_key(_ref(r, EVIDENCE_KINDS[group])) for r in _seq(refs)]
        if len(set(keys)) != len(keys): raise InputError("duplicate_comparison_evidence_reference")
    t = _obj(c["text_method"], "extraction_rule_version encoding proxy_version unicode_category_version white_space_version white_space_sha256".split())
    if t["encoding"] != "utf-8" or t["proxy_version"] != "surface_lexical_trigram_jaccard_v1": raise InputError("unsupported_comparison_text_profile")
    for name in ("extraction_rule_version", "unicode_category_version", "white_space_version"): _tag(t[name], is_id)
    _tag(t["white_space_sha256"], is_hash)
    r = _obj(c["resampling"], "method seed replicates probabilities quantile dependence_assessment_ref replay_ref".split())
    if (r["method"] != "paired_prompt_block_bootstrap_v1" or type(r["seed"]) is not int or r["seed"] != 20260917
            or type(r["replicates"]) is not int or r["replicates"] != 2000 or _seq(r["probabilities"], 2) != ("0.025", "0.975")
            or r["quantile"] != "linear_b_minus_one_v1"): raise InputError("unsupported_resampling_profile")
    _tag(r["dependence_assessment_ref"], lambda v: bool(_ref(v, {"independence_assessment"})))
    _tag(r["replay_ref"], lambda v: v is None or bool(_ref(v, {"artifact", "raw_artifact"})))
    lim = _obj(c["limits"], "max_lexical_units max_pairs max_trigram_visits max_exact_bits".split())
    if any(type(v) is not int or not 1 <= v <= 2**31-1 for v in lim.values()): raise InputError("comparison_resource_limits")
    rev = _obj(c["revision"], "prior_comparison_ids prior_run_ids reason changes".split())
    for k in ("prior_comparison_ids", "prior_run_ids"):
        ids = _seq(rev[k])
        if any(not is_id(x) for x in ids) or len(set(ids)) != len(ids): raise InputError("comparison_revision_identity")
    _tag(rev["reason"], _text)
    if any(not _text(x) for x in _seq(rev["changes"])): raise InputError("comparison_revision_changes")
    return freeze(c)

class _Inspector:
    def __init__(self, bundle, config):
        self.bundle, self.cfg = bundle, config
        self.index = EvidenceIndex(bundle)
        self.role = bundle.manifest.data["data_role"]

    def support(self, ref, kinds, target=None):
        """Iterative traversal of decisive edges only; preserve scoped limitations."""
        root = _key(_ref(ref, kinds)); p = self.index.payload(root)
        stack = [(root, False)]; active = set(); complete = set(); errors = []; mock = False
        while stack:
            key, exiting = stack.pop()
            if exiting: active.discard(key); complete.add(key); continue
            if key in active: errors.append("circular_decisive_support"); continue
            if key in complete: continue
            if len(active) + len(complete) >= MAX_LINKS:
                errors.append("comparison_dependency_limit"); break
            active.add(key); stack.append((key, True))
            q = self.index.payload(key)
            if q is None or q["state"] != "active": errors.append("support_missing_ambiguous_or_inactive"); continue
            mock |= q["mock"] or q["data_role"] == "fixture"
            if q.get("access", "readable") != "readable" or q.get("conflict_status") == "unresolved": errors.append("support_unreadable_or_conflicted")
            if self.index.affected(key, {"schema", "membership", "validity", "independence", "metadata"}): errors.append("support_under_correction")
            for name in ("evidence_refs", "reviewer_refs"):
                for v in q.get(name, ()):
                    if name == "reviewer_refs" and v["record_type"] != "role": errors.append("reviewer_reference_type")
                    stack.append((_key(v), False))
        if p is not None and target is not None and ("target_ref" not in p or _key(p["target_ref"]) != target): errors.append("support_target_mismatch")
        if mock and self.role != "fixture": errors.append("mock_evidence_for_nonfixture")
        return p, Fact("support_reference", "unresolved" if errors else "record_consistent", tuple(sorted(set(errors))), evidence_refs=(freeze(ref),), mock=mock)

    def artifact(self, value):
        k = _tag(value, lambda r: bool(_ref(r, {"artifact", "raw_artifact"})))
        if k.state != "known": return None, _fact("prompt_material", None, observed=value)
        refs = (k.value,); key = _key(k.value)
        matches = [a for a in self.bundle.artifacts if a.record_key == ":".join(key)]
        if self.index.get(key) is None or len(matches) != 1 or matches[0].status != "snapshot_read":
            return None, _fact("prompt_material", None, reason="prompt_snapshot_unavailable", refs=refs)
        s = self.bundle.snapshots.get(matches[0].snapshot_path)
        if s is None: return None, _fact("prompt_material", None, refs=refs)
        return s, _fact("prompt_material", True, {"sha256": s.sha256, "bytes": s.size_bytes}, refs=refs)

    def prompt(self, study, block, condition, cell, protocol):
        v = _obj(study["sent_prompt"], ("artifact_ref", "attestation_ref"))
        snapshot, material = self.artifact(v["artifact_ref"])
        expected = registered_prompt_bytes(block, condition); digest = hashlib.sha256(expected).hexdigest()
        hashes = [snapshot.sha256] if snapshot is not None else []; facts = [material]; attested = False
        att = _tag(v["attestation_ref"], lambda r: bool(_ref(r, {"evidence"})))
        if att.state == "known":
            p, linked = self.support(att.value, {"evidence"}, ("cell", cell.record_id)); facts.append(linked)
            okay = False
            if p is not None:
                e = _obj(p.get("extensions", {}).get("verified_prompt"), "encoding byte_length comparison_id block_id condition_id protocol_ref".split())
                _ref(e["protocol_ref"], {"protocol"})
                okay = (linked.status == "record_consistent" and p["purpose"] == "observation" and _value(p["method"]) == "verified_sent_bytes_v1"
                        and bool(p["reviewer_refs"]) and is_hash(_value(p["subject_hash"])) and e["encoding"] == "utf-8"
                        and type(e["byte_length"]) is int and e["byte_length"] == len(expected)
                        and (e["comparison_id"], e["block_id"], e["condition_id"]) == (self.cfg["comparison_id"], block, condition)
                        and _key(e["protocol_ref"]) == ("protocol", protocol.record_id))
            facts.append(_fact("verified_prompt_record", okay, refs=(att.value,), mock=linked.mock))
            if okay:
                hashes.append(_value(p["subject_hash"])); attested = True
        facts.append(_fact("exact_prompt_assembly", all(h == digest for h in hashes) if hashes else None, observed=tuple(hashes), expected=digest))
        context = knowledge(protocol.data["conditioning_context_ref"]); source = knowledge(v["artifact_ref"])
        facts.append(_fact("protocol_prompt_reference", context.value == source.value if context.state == source.state == "known" else True if attested else None))
        if snapshot is None and attested and source.state != "known":
            facts[0] = Fact("prompt_material", "record_consistent", ("attested_bytes_only",), evidence_refs=(att.value,))
        return facts

    def control(self, name, raw, condition, cid):
        c = _obj(raw, ("requested", "actual", "enforcement", "evidence_refs"))
        expected = (Decimal(1) if condition == "B" else Decimal("0.4")) if name == "temperature" else CONTROL_VALUES[name]
        predicate = (lambda v: v is None or type(v) is int) if name == "generator_seed" else (lambda v: type(v) is bool) if type(expected) is bool else (lambda v: _number(v) is not None)
        requested, actual = _tag(c["requested"], predicate), _tag(c["actual"], predicate)
        if c["enforcement"] not in ("recorded", "unsupported", "hidden", "not_recorded"): raise InputError("control_enforcement_state")
        refs = _seq(c["evidence_refs"]); supported = bool(refs); mock = False
        for ref in refs:
            p, linked = self.support(ref, {"evidence"}, ("cell", cid)); mock |= linked.mock
            evidence = p.get("extensions", {}).get("recorded_controls") if p else None
            supported &= (linked.status == "record_consistent" and p is not None and p["purpose"] == "observation"
                          and bool(p["reviewer_refs"]) and isinstance(evidence, Mapping)
                          and evidence.get(name) == {k: c[k] for k in ("requested", "actual", "enforcement")})
        def same(k): return (_number(k.value) if isinstance(expected, (int, Decimal)) and type(expected) is not bool else k.value) == expected
        mismatch = any(k.state == "known" and not same(k) for k in (requested, actual))
        consistent = requested.state == actual.state == "known" and c["enforcement"] == "recorded" and supported
        f = _fact("control_" + name, False if mismatch else True if consistent else None, observed=c,
                  expected=str(expected) if isinstance(expected, Decimal) else expected, refs=refs, mock=mock)
        if name in ("presence_penalty", "frequency_penalty") and requested.state == actual.state == "not_applicable" and c["enforcement"] == "unsupported":
            f = Fact(f.name, "not_applicable", ("penalty_not_exposed",), freeze(c))
        return f

    def bind(self, block, condition, entry, duplicate_ids):
        cellref, proofref = entry["cell_ref"], entry["study_record_ref"]; cid = cellref["record_id"]
        facts = []; frame = study = cell = budget = None; linked = set()
        attempts = tuple(sorted(k[1] for k in self.index.entries if k[0] == "attempt" and (a := self.index.get(k)) is not None and a.data["analysis_cell_id"] == cid))
        try:
            cr = self.index.resolve(cellref)
            if cr is None: facts.append(_fact("expected_cell", None, reason="expected_cell_missing_or_ambiguous"))
            else:
                cell = cr.data
                facts.append(_fact("cell_role", (cell["prompt_block_id"], cell["condition_id"]) == (block, condition)))
                facts.append(_fact("unique_cell_role", cid not in duplicate_ids))
                fr = self.index.get(("frame", cell["frame_id"])); pr = self.index.get(("protocol", cell["generation_protocol_id"]))
                if fr: frame = freeze({k: fr.data[k] for k in FRAME_FIELDS})
                facts.append(_fact("frame_record", None if fr is None else not self.index.affected(("frame", fr.record_id), {"schema", "registry", "membership"})))
                facts.append(_fact("protocol_identity", None if pr is None else pr.data["generation_protocol_version"] == cell["generation_protocol_version"]))
                p, f = self.support(proofref, {"evidence"}, ("cell", cid)); facts.append(f)
                if p is not None:
                    study = _obj(p.get("extensions", {}).get("study_binding"), STUDY_KEYS)
                    facts.append(_fact("study_record_type", p["purpose"] == "observation" and _value(p["method"]) == "study_binding_v1" and bool(p["reviewer_refs"])))
                    facts.append(_fact("study_identity", (study["version"], study["comparison_id"], study["comparison_version"], study["block_id"], study["condition_id"]) == ("0.1", self.cfg["comparison_id"], self.cfg["comparison_version"], block, condition)))
                    _ref(study["protocol_ref"], {"protocol"})
                    facts.append(_fact("study_protocol_reference", _key(study["protocol_ref"]) == ("protocol", cell["generation_protocol_id"])))
                    if pr is not None: facts.extend(self.prompt(study, block, condition, cr, pr))
                    for name in ("visible_system_instruction", "platform_context", "reasoning"):
                        k = _tag(study[name], lambda r: r is None or bool(_ref(r, {"artifact", "raw_artifact", "evidence"})))
                        okay = None
                        if k.state == "known":
                            if k.value is None: okay = True
                            elif k.value["record_type"] == "evidence":
                                _, sub = self.support(k.value, {"evidence"}); okay = sub.status == "record_consistent"
                            else:
                                snap, _ = self.artifact(study[name]); okay = True if snap is not None else None
                        facts.append(_fact(name, okay, observed=study[name]))
                    controls = _obj(study["controls"], CONTROL_VALUES)
                    for name in controls: facts.append(self.control(name, controls[name], condition, cid))
                    if pr:
                        settings = knowledge(pr.data["decoding_settings"])
                        for name in ("temperature", "top_p", "presence_penalty", "frequency_penalty", "max_output_tokens"):
                            r = knowledge(controls[name]["requested"]); v = settings.value.get(name) if settings.state == "known" else None
                            facts.append(_fact("protocol_setting_"+name, _number(v) == _number(r.value) if v is not None and r.state == "known" else None))
                        k = knowledge(pr.data["seed"])
                        facts.append(_fact("protocol_seed", k.value is None if k.state == "known" else None))
                    cap = _obj(study["cap"], ("unit", "tokenizer", "convention"))
                    for name, value in cap.items():
                        k = _tag(value, _text); facts.append(_fact("cap_"+name, True if k.state == "known" else None, observed=value))
                    b = _tag(study["budget_ref"], lambda r: bool(_ref(r, {"budget"})))
                    if b.state == "known":
                        budget, bf = self.support(b.value, {"budget"}); facts.append(bf)
                    expected = {"calls": 4, "candidate_positions": 20, "output_cap_per_call": 8192}
                    planned = knowledge(budget["planned"]) if budget else None
                    good = None
                    if planned and planned.state == "known":
                        good = isinstance(planned.value, Mapping) and set(planned.value) == set(expected) and all(type(x) is int for x in planned.value.values()) and planned.value == expected
                    facts.append(_fact("planned_cell_budget", good, expected=expected))
                    if budget: facts.append(_fact("budget_scope", ("cell", cid) in {_key(r) for r in budget["scope_refs"]}))
                    deployment = _obj(study["deployment"], ("serving_identity", "change_detected", "evidence_refs"))
                    identity = _tag(deployment["serving_identity"], _text)
                    changed = _tag(deployment["change_detected"], lambda v: type(v) is bool)
                    deployment_links = [self.support(r, {"evidence"}, ("cell", cid))
                                        for r in _seq(deployment["evidence_refs"])]
                    expected_deployment = {k: deployment[k] for k in ("serving_identity", "change_detected")}
                    supported = bool(deployment_links) and all(
                        f.status == "record_consistent" and p is not None and p["purpose"] == "observation"
                        and bool(p["reviewer_refs"]) and p.get("extensions", {}).get("recorded_deployment") == expected_deployment
                        for p, f in deployment_links)
                    facts.append(_fact("serving_identity", True if identity.state == "known" and supported else None,
                                       observed=deployment["serving_identity"], refs=deployment["evidence_refs"]))
                    facts.append(_fact("deployment_unchanged", False if changed.state == "known" and changed.value else
                                       True if changed.state == "known" and supported else None,
                                       observed=deployment["change_detected"], refs=deployment["evidence_refs"]))
                    auto = _tag(study["automatic_retries"], lambda v: type(v) is bool)
                    facts.append(_fact("automatic_retries", not auto.value if auto.state == "known" else None, observed=study["automatic_retries"]))
                    rows = _seq(study["attempts"], 4)
                    if len(rows) != 4: raise InputError("four_attempt_bindings_required")
                    for g, row in enumerate(rows, 1):
                        _obj(row, ("group_index", "attempt_ref", "global_order", "recorded_at"))
                        if type(row["group_index"]) is not int or row["group_index"] != g: raise InputError("attempt_binding_order")
                        ar = _tag(row["attempt_ref"], lambda r: bool(_ref(r, {"attempt"})))
                        order = _tag(row["global_order"], lambda v: type(v) is int and v > 0); _time(row["recorded_at"])
                        bi = BLOCKS.index(block)+1
                        expected_order = (g-1)*18+(bi-1)*3+PERMUTATIONS[(bi+g-2)%6].index(condition)+1
                        facts.append(_fact(f"interleave_{g}", order.value == expected_order if order.state == "known" else None, observed=row["global_order"], expected=expected_order))
                        a = self.index.resolve(ar.value) if ar.state == "known" else None
                        if ar.state == "known": linked.add(ar.value["record_id"])
                        good = None
                        if a:
                            retry = knowledge(a.data["retry_of"])
                            good = a.data["analysis_cell_id"] == cid and _value(a.data["registered_call_order"]) == g and _value(a.data["planned_candidate_count"]) == 5 and retry.state == "known" and retry.value is None
                        facts.append(_fact(f"attempt_{g}", good, observed=a.data if a else row))
                    if len(linked) != sum(knowledge(r["attempt_ref"]).state == "known" for r in rows): facts.append(_fact("unique_attempt_slots", False))
                    for deviation in _seq(study["deviations"]):
                        _obj(deviation, ("code", "detail", "evidence_refs")); _tag(deviation["detail"], _text)
                        if not is_id(deviation["code"]): raise InputError("deviation_code")
                        for ref in _seq(deviation["evidence_refs"]): validate_ref(ref)
        except (InputError, KeyError, TypeError, ValueError) as exc:
            facts.append(Fact("study_binding_shape", "contract_error", (exc.code if isinstance(exc, InputError) else "malformed_study_binding",)))
        return CellBinding(block, condition, cid, _state(facts), tuple(facts), frame, freeze(study), cell, budget, attempts, tuple(a for a in attempts if a not in linked))

    def pair(self, left, right):
        facts = [_fact("participant_records", True if left.status == right.status == "record_consistent" else None),
                 _fact("frame_compatibility", left.frame == right.frame if left.frame is not None and right.frame is not None else None)]
        for name in ("model_identifier", "model_family", "checkpoint_identifier", "collection_window"):
            a = knowledge(left.cell[name]) if left.cell else None; b = knowledge(right.cell[name]) if right.cell else None
            facts.append(_fact(name+"_compatibility", a.value == b.value if a and b and a.state == b.state == "known" else None))
        for name in ("visible_system_instruction", "platform_context", "reasoning", "cap.unit", "cap.tokenizer", "cap.convention", "deployment.serving_identity"):
            try:
                def value(binding):
                    v = binding.study
                    for k in name.split("."): v = v[k]
                    return knowledge(v)
                a, b = value(left), value(right)
                okay = a.value == b.value if a.state == b.state == "known" else None
            except (TypeError, KeyError, InputError): okay = None
            facts.append(_fact(name.replace(".", "_")+"_compatibility", okay))
        if (left.condition_id, right.condition_id) == ("B", "A"):
            a = next((f for f in left.facts if f.name == "exact_prompt_assembly"), None)
            b = next((f for f in right.facts if f.name == "exact_prompt_assembly"), None)
            facts.append(_fact("AB_sent_prompt_equality", set(a.observed) == set(b.observed) if a and b and a.observed and b.observed else None))
        return PairBinding(left.block_id, left.condition_id+"-"+right.condition_id, (left.cell_id, right.cell_id), tuple(facts))

    def evidence(self):
        facts = []
        for group, refs in self.cfg["evidence"].items():
            if not refs: facts.append(_fact("evidence_"+group, None, observed=(), reason="evidence_not_supplied"))
            for ref in refs:
                p, link = self.support(ref, EVIDENCE_KINDS[group]); facts.append(link)
                if p is None: continue
                facts.append(Fact("evidence_"+group, link.status, link.reasons, observed=p, evidence_refs=(ref,), mock=link.mock))
                if group == "registration":
                    try:
                        r = _obj(p.get("extensions", {}).get("comparison_registration"), "comparison_id comparison_version binding_sha256 first_inspected_at first_collection_at".split())
                        good = (r["comparison_id"], r["comparison_version"], r["binding_sha256"]) == (self.cfg["comparison_id"], self.cfg["comparison_version"], configuration_fingerprint(self.cfg))
                        facts.append(_fact("registration_binding", good))
                        registered = _time(p["registered_at"])
                        for name in ("first_inspected_at", "first_collection_at"):
                            other = _time(r[name]); facts.append(_fact("registration_before_"+name, registered < other if registered and other else None, observed=(p["registered_at"], r[name])))
                    except (InputError, KeyError, ValueError, TypeError): facts.append(_fact("registration_binding", None))
        for name in ("extraction_rule_version", "unicode_category_version", "white_space_version", "white_space_sha256"):
            k = knowledge(self.cfg["text_method"][name]); facts.append(_fact("text_"+name, True if k.state == "known" else None, observed=self.cfg["text_method"][name]))
        for name, kinds in (("dependence_assessment_ref", {"independence_assessment"}), ("replay_ref", {"artifact", "raw_artifact"})):
            value = self.cfg["resampling"][name]; k = knowledge(value)
            if k.state != "known":
                facts.append(_fact(name, None, observed=value))
            elif k.value is None:
                facts.append(Fact(name, "not_applicable", ("no_replay_requested",), observed=value))
            elif name == "replay_ref":
                # Record identity only. Index content/shape validation is Step 5.
                record = self.index.resolve(k.value)
                facts.append(_fact(name, True if record else None, observed=value, reason="replay_reference_unresolved"))
            else:
                _, f = self.support(k.value, kinds)
                facts.append(Fact(name, f.status, f.reasons, observed=value, evidence_refs=(k.value,), mock=f.mock))
        return tuple(facts)


def review_comparison(bundle: LoadedBundle) -> ComparisonReview:
    """Return scoped records. CLI/report dispatch remains Phase 2 Step 6 work.

    The returned configuration and supplied record details are private audit data,
    not a pre-redacted public report. Keep them local or use the later renderer.
    """
    if not isinstance(bundle, LoadedBundle): raise InputError("loaded_bundle_required")
    if bundle.manifest is None: return ComparisonReview(False, "unavailable", None, None, None)
    data = bundle.manifest.data; role = data.get("data_role"); config = data.get("analysis_config")
    if not isinstance(config, Mapping) or not isinstance(config.get("extensions", {}), Mapping): return ComparisonReview(False, "unavailable", None, role, None)
    if "comparison" not in config.get("extensions", {}): return ComparisonReview(False, "not_requested", None, role, None)
    raw = config["extensions"]["comparison"]
    try: cfg = _shape(raw)
    except (InputError, TypeError, KeyError, ValueError) as exc:
        return ComparisonReview(True, "contract_error", None, role, freeze(raw), facts=(Fact("comparison_shape", "contract_error", (exc.code if isinstance(exc, InputError) else "malformed_comparison",)),))
    inspector = _Inspector(bundle, cfg)
    ids = [e["cell_ref"]["record_id"] for b in cfg["blocks"] for e in b["conditions"].values()]
    duplicates = {x for x in ids if ids.count(x)>1}
    bindings = tuple(inspector.bind(b["block_id"], c, b["conditions"][c], duplicates) for b in cfg["blocks"] for c in CONDITIONS)
    byrole = {(x.block_id, x.condition_id): x for x in bindings}
    pairs = tuple(inspector.pair(byrole[(b,l)], byrole[(b,r)]) for b in BLOCKS for l,r in (("B","A"),("C","A"),("C","B")))
    facts = list(inspector.evidence()); pilots = set()
    for ref in cfg["pilot_cell_refs"]:
        record = inspector.index.resolve(ref); pilots.add(ref["record_id"])
        facts.append(_fact("pilot_disjoint", ref["record_id"] not in ids and (record is None or record.data["prompt_block_id"] == "P00")))
        if record is None: facts.append(_fact("pilot_cell", None))
    if len(pilots) != len(cfg["pilot_cell_refs"]): facts.append(_fact("unique_pilot_cell", False))
    if role == "pilot": facts.append(_fact("main_material_role", False, observed=role, reason="pilot_not_main_study"))
    unbound = tuple(sorted(k[1] for k in inspector.index.entries if k[0]=="cell" and k[1] not in set(ids)|pilots))
    allfacts = facts+[f for b in bindings for f in b.facts]+[f for p in pairs for f in p.facts]
    return ComparisonReview(True, _state(allfacts), cfg["comparison_id"], role, cfg, bindings, pairs, tuple(facts), unbound)
