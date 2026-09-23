"""Independent exact probability oracles and passive-record support assays.

Trial histories and evidence are stipulated software fixtures. Enumerating all
binary sequences independently supplies expected probabilities. No fixture is
an actual model experiment, real-world independence finding or latent assay.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import support_assays as sa, longitudinal_records as lr
from structdet_bench.contracts import CLASS_IDS, InputError, freeze
from structdet_bench.local_io import load_bundle
from tests.helpers import ROOT, support_record, artifact_record, rewrite_evidence_bundle, tagged as K, record_ref as C
from tests.test_longitudinal import materialize_observed, A, B, R, O, E
from tests import phase3_helpers as gate


def enumerate_tails(n, p, lo, hi):
    """Sum individual Bernoulli sequence weights, with no binomial routine."""
    upper = lower = F(0)
    for sequence in product((0, 1), repeat=n):
        mass = F(1)
        for bit in sequence:
            mass *= p if bit else 1 - p
        if sum(sequence) >= lo:
            upper += mass
        if sum(sequence) <= hi:
            lower += mass
    return upper, lower


class ExactTailTests(unittest.TestCase):
    def decision(self, n=4, lo=4, hi=4, **kw):
        return sa.binomial_threshold(n, lo, hi, tau=kw.pop('tau', F(1, 2)),
                                    alpha=kw.pop('alpha', F(1, 8)), J=kw.pop('J', 1), **kw)

    def test_oracle_file_matches_independent_binary_sequence_enumeration(self):
        data = json.loads((ROOT / 'tests/fixtures/support_assay_oracles.json').read_text())
        self.assertEqual(data['plan_sha256'], gate.PLAN_SHA256)
        self.assertEqual(data['scope'], 'stipulated_exact_software_oracles_only')
        self.assertEqual(len(data['cases']), 12)
        for case in data['cases']:
            with self.subTest(case=case['id']):
                p, alpha = F(*case['tau']), F(*case['alpha'])
                up, low = enumerate_tails(case['N'], p, case['k_confirmed'], case['k_possible'])
                self.assertEqual((up, low), (F(*case['upper_tail']), F(*case['lower_tail'])))
                self.assertEqual(alpha / (2 * case['J']), F(*case['delta']))
                r = self.decision(case['N'], case['k_confirmed'], case['k_possible'], tau=p, alpha=alpha, J=case['J'])
                self.assertEqual((r.upper_tail, r.lower_tail, r.delta), (up, low, F(*case['delta'])))
                self.assertEqual(r.status, case['status'])

    def test_inclusive_positive_and_strict_negative_differ_at_exact_equality(self):
        positive = self.decision()
        negative = self.decision(lo=0, hi=0)
        self.assertEqual(positive.upper_tail, positive.delta)
        self.assertEqual(negative.lower_tail, negative.delta)
        self.assertEqual(positive.status, 'threshold_present')
        self.assertEqual(negative.status, 'unresolved')

    def test_no_display_tolerance_can_move_equality(self):
        epsilon = F(1, 10**35)
        self.assertEqual(self.decision(alpha=F(1, 8) - epsilon).status, 'unresolved')
        self.assertEqual(self.decision(alpha=F(1, 8) + epsilon).status, 'threshold_present')
        self.assertEqual(self.decision(lo=0, hi=0, alpha=F(1, 8) + epsilon).status, 'threshold_below')
        self.assertEqual(self.decision(lo=0, hi=0, alpha=F(1, 8) - epsilon).status, 'unresolved')

    def test_all_small_count_intervals_match_enumeration(self):
        for n in range(1, 7):
            for p in (F(1, 4), F(1, 2), F(3, 4)):
                for lo in range(n + 1):
                    for hi in range(lo, n + 1):
                        r = self.decision(n, lo, hi, tau=p, J=3)
                        up, low = enumerate_tails(n, p, lo, hi)
                        self.assertEqual((r.upper_tail, r.lower_tail), (up, low))
                        expected = 'threshold_present' if up <= F(1, 48) else 'threshold_below' if low < F(1, 48) else 'unresolved'
                        self.assertEqual(r.status, expected, (n, p, lo, hi))

    def test_unknown_outcomes_enlarge_possible_count_without_false_failures(self):
        results = [self.decision(lo=0, hi=k, tau=F(3, 4)) for k in (0, 1, 2, 4)]
        self.assertEqual([r.lower_tail for r in results], [F(1, 256), F(13, 256), F(67, 256), F(1)])
        self.assertEqual([r.status for r in results], ['threshold_below', 'threshold_below', 'unresolved', 'unresolved'])
        self.assertTrue(all(r.k_confirmed == 0 for r in results))

    def test_multiplicity_includes_planned_cells(self):
        a, b = self.decision(J=1), self.decision(J=2)
        self.assertEqual((a.delta, b.delta), (F(1, 16), F(1, 32)))
        self.assertEqual((a.status, b.status), ('threshold_present', 'unresolved'))

    def test_tau_one_all_successes_does_not_establish_probability_one(self):
        r = self.decision(tau=F(1))
        self.assertEqual(r.upper_tail, 1)
        self.assertEqual(r.status, 'unresolved')
        self.assertEqual(self.decision(lo=3, hi=3, tau=F(1)).status, 'threshold_below')
        self.assertEqual(self.decision(lo=3, hi=4, tau=F(1)).status, 'unresolved')

    def test_one_observation_is_not_threshold_support(self):
        r = self.decision(1, 1, 1, alpha=F(1, 20))
        self.assertEqual((r.N, r.k_confirmed, r.k_possible), (1, 1, 1))
        self.assertEqual(r.status, 'unresolved')

    def test_invalid_counts_and_probabilities_cannot_supply_decision(self):
        cases = [(0, 0, 0, {}), (4, 2, 1, {}), (4, -1, 1, {}), (4, 0, 5, {}),
                 (True, 0, 1, {}), (4, 4, 4, {'tau': 0}), (4, 4, 4, {'tau': F(2)}),
                 (4, 4, 4, {'alpha': 0}), (4, 4, 4, {'alpha': 1}),
                 (4, 4, 4, {'J': 0}), (4, 4, 4, {'J': True}),
                 (4, 4, 4, {'tau': 0.5}), (4, 4, 4, {'tau': 'NaN'})]
        for n, lo, hi, kw in cases:
            with self.subTest(n=n, lo=lo, hi=hi, kw=kw):
                try:
                    r = self.decision(n, lo, hi, **kw)
                except (InputError, ValueError):
                    continue
                self.assertEqual(r.status, 'unavailable')

    def test_exact_workload_limits_produce_unavailability_without_approximation(self):
        r = self.decision(64, 64, 64, limits={'max_exact_bits': 32})
        self.assertEqual(r.status, 'unavailable')
        self.assertIsNone(r.upper_tail)
        self.assertIsNone(r.lower_tail)
        self.assertEqual(r.N, 64)

    def test_huge_exponent_and_trial_count_are_bounded_before_computation(self):
        for kw in ({'tau': '1e-1000000000'}, {'n': 10**12}):
            n = kw.pop('n', 4)
            try:
                r = self.decision(n, n, n, **kw)
            except (InputError, ValueError):
                continue
            self.assertEqual(r.status, 'unavailable')


class RecordFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.build()

    def build(self, labels=None, *, validity=None, interventions=1, success_event='class_membership', tau='0.5'):
        labels = [A] * 16 if labels is None else labels
        panels = [[list(labels)] for _ in range(interventions)]
        self.obs, self.sup, self.man = materialize_observed(self.root, panels, validity=validity)
        self.cfg = self.man['analysis_config']['extensions']['longitudinal']
        self.cfg['capabilities'].append('support_assay')
        self.cfg['assays'] = []
        self.cfg['interventions'] = []
        self.obs = [r for r in self.obs if r['record_type'] != 'attempt']
        self.slots = {'assay': []}
        trials = []
        for j in range(interventions):
            intervention = R('intervention', f'I{j}')
            self.cfg['interventions'].append(O('intervention', f'I{j}',
                pre_state_ref=R('state', 'S0'), post_state_ref=R('state', 'S0'),
                intervention_kind='inference_configuration', parameters_changed=K(False),
                direct_answer_injection=K(False), external_refs=[]))
            selection = self.man['analysis_config']['selection'][j]
            positions = []
            for pos, sid in enumerate(selection['selected_sample_ids']['value'], 1):
                aid, gid, tid = f'call{j}-{pos}', f'group{j}-{pos}', f'trial{j}-{pos}'
                row = self.row('realization', sid)
                output = f'Stipulated candidate {sid}; fixture only.\n'.encode()
                output_name, raw_name = f'output-{sid}.txt', f'raw-{aid}.json'
                (self.root / output_name).write_bytes(output)
                (self.root / raw_name).write_text(json.dumps({'candidate_position': 1, 'output': output.decode()}))
                self.obs.extend([artifact_record(f'output-{sid}', output_name), artifact_record(f'raw-{aid}', raw_name)])
                row.update(attempt_id=K(aid), generation_group_id=K(gid), within_group_index=K(1),
                    raw_response_ref=K(C('artifact', f'raw-{aid}')), output_ref=K(C('artifact', f'output-{sid}')),
                    output_content_hash=K(hashlib.sha256(output).hexdigest()))
                self.obs.append({**C('attempt', aid), 'attempt_id': aid,
                    'analysis_cell_id': f'c0p{j}', 'attempt_status': 'succeeded',
                    'retry_of': K(None), 'raw_response_ref': K(C('artifact', f'raw-{aid}')),
                    'generation_group_id': K(gid), 'planned_candidate_count': K(1), 'registered_call_order': K(pos)})
                positions.append({'generation_group_id': gid, 'registered_call_order': pos,
                                  'within_group_index': 1, 'attempt_id': K(aid)})
                self.slots['assay'].append({'trial_id': tid, 'intervention_ref': intervention,
                    'measurement_ref': R('measurement', f'M0p{j}'),
                    'attempt_ref': C('attempt', aid), 'candidate_position': 1})
                trials.append({'trial_id': tid, 'intervention_ref': intervention,
                    'measurement_ref': K(R('measurement', f'M0p{j}')),
                    'sample_ref': K(C('realization', sid)), 'status': 'observed', 'evidence': E()})
            selection['registered_positions'] = K(positions)
        self.assay = O('assay', 'assay', state_ref=R('state', 'S0'), family_id='fixed-prompts', family_version='0.1',
            intervention_refs=[R('intervention', f'I{j}') for j in range(interventions)],
            success_event=success_event, registry_ref=C('reference_registry', 'sorting_reference_eight'),
            tau=tau, alpha='0.125', allocation='bonferroni_equal', trials=trials,
            iid_evidence_ref=K(C('evidence', 'assay-iid')))
        self.cfg['assays'].append(self.assay)
        self.sup.append(support_record('evidence', 'assay-iid',
            target_ref=C('cell', 'c0p0'), purpose='independence', assertion=K(True),
            method=K('stipulated_fixed_independent_calls'), detail=K('Fixture only; no real model was run.'),
            access='readable', conflict_status='none_declared', reviewer_refs=[C('role', 'reviewer')],
            extensions={}))
        self.seal()

    def seal(self, classes=None):
        reg = self.support(self.cfg['registered_design_ref']['value']['record_id'])
        reg['payload'].setdefault('extensions', {})[sa.REGISTRATION_KEY] = sa.registration_witness(
            self.cfg['assays'], list(CLASS_IDS) if classes is None else classes, self.slots,
            bundle=self.bundle())
        self.support('assay-iid')['payload']['extensions'][sa.IID_KEY] = sa.iid_witness(self.assay)

    def row(self, kind, identity):
        return next(r for r in self.obs if r['record_type'] == kind and r['record_id'] == identity)

    def support(self, identity):
        return next(r for r in self.sup if r['record_id'] == identity)

    def bundle(self):
        return load_bundle(rewrite_evidence_bundle(self.root, self.obs, self.sup, self.man))

    def study(self):
        return sa.evaluate_support_assays(self.bundle())

    def result(self):
        return self.study().assays[0]

    def cell(self, class_id=A, intervention=0, result=None):
        return next(c for c in (result or self.result()).cells
                    if c.class_id == class_id and c.intervention_ref.object_id == f'I{intervention}')

    def registration(self):
        return self.support(self.cfg['registered_design_ref']['value']['record_id'])['payload']['extensions'][sa.REGISTRATION_KEY]

    def nonexpression_witness(self, index):
        trial = self.assay['trials'][index]
        slot = self.slots['assay'][index]
        eid = f'nonexpression-{index}'
        self.sup.append(support_record('evidence', eid, target_ref=slot['attempt_ref'],
            purpose='observation', assertion=K(True), method=K('stipulated_call_inspection'),
            detail=K('Fixture nonexpression assertion, no actual model experiment.'),
            access='readable', conflict_status='none_declared', reviewer_refs=[C('role', 'reviewer')],
            extensions={sa.FAILURE_KEY: {'assay_ref': R('assay', 'assay'),
                'trial_id': trial['trial_id'], 'attempt_ref': slot['attempt_ref'],
                'success_event': self.assay['success_event'], 'determinate_nonexpression': True}}))
        trial['evidence']['validation'].append(C('evidence', eid))

    def drop_trial(self, index=0, status='missing'):
        trial = self.assay['trials'][index]
        trial.update(status=status, sample_ref=K(None))


class IntegrationTests(RecordFixture):
    def test_complete_loaded_records_resolve_finite_reference_support(self):
        r = self.result()
        self.assertEqual(r.present_classes, (A,))
        self.assertEqual(set(r.below_classes), set(CLASS_IDS) - {A})
        self.assertEqual(r.J, 8)
        self.assertEqual(r.delta, F(1, 128))
        self.assertEqual(r.expressible_support_size_finite_family.value, 1)
        self.assertEqual(r.reference_normalized_support.value, F(1, 8))
        self.assertEqual(self.cell(result=r).decision.N, 16)
        self.assertEqual(self.cell(result=r).decision.k_confirmed, 16)

    def test_observed_union_survives_unresolved_probability_support(self):
        self.build([A])
        r = self.result()
        self.assertEqual(r.observed_intervention_union, (A,))
        self.assertEqual(r.present_classes, ())
        self.assertEqual(set(r.unresolved_classes), set(CLASS_IDS))
        self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_ordinary_empirical_frequency_threshold_does_not_replace_tau(self):
        before = self.result()
        self.man['analysis_config']['empirical_threshold'] = '0.99'
        after = self.result()
        self.assertEqual(before.present_classes, after.present_classes)
        self.assertEqual(before.delta, after.delta)
        self.assertEqual(self.cell(result=after).decision.tau, F(1, 2))

    def test_missing_trial_does_not_reduce_fixed_N_or_supply_failure(self):
        self.drop_trial()
        r = self.result()
        d = self.cell(result=r).decision
        self.assertEqual(d.N, 16)
        self.assertEqual(d.status, 'unavailable')
        self.assertNotIn(B, r.below_classes)
        self.assertEqual(r.observed_intervention_union, (A,))

    def test_deleted_trial_cannot_shrink_registered_inventory(self):
        self.assay['trials'].pop()
        r = self.result()
        self.assertEqual(self.cell(result=r).decision.N, 16)
        self.assertEqual(self.cell(result=r).decision.status, 'unavailable')
        self.assertFalse(r.below_classes)

    def test_planned_or_unperformed_trials_are_unavailable(self):
        self.drop_trial(status='planned')
        d = self.cell().decision
        self.assertEqual(d.N, 16)
        self.assertEqual(d.status, 'unavailable')

    def test_unknown_classification_counts_as_possible_not_confirmed(self):
        self.build([A] * 15 + [None])
        d = self.cell().decision
        self.assertEqual((d.N, d.k_confirmed, d.k_possible), (16, 15, 16))
        self.assertEqual(d.status, 'threshold_present')
        other = self.cell(B).decision
        self.assertEqual((other.k_confirmed, other.k_possible), (0, 1))

    def test_unreadable_class_evidence_remains_possible(self):
        self.support('e-a1')['payload']['access'] = 'unavailable'
        d = self.cell().decision
        self.assertEqual((d.N, d.k_confirmed, d.k_possible), (16, 15, 16))

    def test_membership_and_valid_expression_have_distinct_events(self):
        self.build(validity=['invalid'] * 16)
        membership = self.result()
        self.assertEqual(membership.present_classes, (A,))
        self.build(validity=['invalid'] * 16, success_event='valid_class_membership')
        valid = self.result()
        self.assertEqual(valid.present_classes, ())
        self.assertEqual(set(valid.below_classes), set(CLASS_IDS))
        d = self.cell(result=valid).decision
        self.assertEqual((d.N, d.k_confirmed, d.k_possible), (16, 0, 0))

    def test_unreadable_validity_does_not_shrink_denominator_or_become_negative(self):
        self.build(success_event='valid_class_membership')
        self.support('e-v1')['payload']['access'] = 'unavailable'
        d = self.cell().decision
        self.assertEqual((d.N, d.k_confirmed, d.k_possible), (16, 15, 16))

    def test_changed_event_without_new_registration_is_unavailable(self):
        self.assay['success_event'] = 'valid_class_membership'
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_valid_only_measurement_cannot_supply_unconditional_denominator(self):
        self.cfg['measurements'][0]['view'] = 'classified_valid'
        self.cfg['panels'][0]['view'] = 'classified_valid'
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_five_candidates_from_one_call_are_not_five_independent_trials(self):
        self.build([A] * 5)
        first = self.row('attempt', 'call0-1')
        first['planned_candidate_count'] = K(5)
        for i in range(1, 6):
            self.row('realization', f's{i}').update(attempt_id=K('call0-1'), generation_group_id=K('group0-1'), within_group_index=K(i))
            self.slots['assay'][i-1].update(attempt_ref=C('attempt', 'call0-1'), candidate_position=i)
        self.seal()
        r = self.result()
        self.assertEqual(self.cell(result=r).decision.status, 'unavailable')
        self.assertFalse(r.present_classes)

    def test_one_preregistered_candidate_from_multi_output_call_is_allowed(self):
        for row in self.obs:
            if row['record_type'] == 'attempt':
                row['planned_candidate_count'] = K(5)
        self.assertEqual(self.result().present_classes, (A,))

    def test_unregistered_candidate_position_cannot_be_selected_after_inspection(self):
        self.row('realization', 's1')['within_group_index'] = K(2)
        self.row('attempt', 'call0-1')['planned_candidate_count'] = K(2)
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_optional_stopping_and_unknown_iid_withhold_probability_claims(self):
        witness = self.support('assay-iid')['payload']['extensions'][sa.IID_KEY]
        witness['no_adaptive_stopping'] = False
        r = self.result()
        self.assertEqual(self.cell(result=r).decision.status, 'unavailable')
        self.assertEqual(r.observed_intervention_union, (A,))
        witness['no_adaptive_stopping'] = True
        self.assay['iid_evidence_ref'] = K(state='unknown')
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_reused_continuations_and_call_dependence_withhold_probability_claims(self):
        witness = self.support('assay-iid')['payload']['extensions'][sa.IID_KEY]
        for key in ('no_reused_continuations', 'independent_calls', 'fixed_state', 'fixed_intervention', 'complete_trial_inventory'):
            witness[key] = False
            self.assertEqual(self.cell().decision.status, 'unavailable', key)
            witness[key] = True

    def test_changed_tau_or_family_version_cannot_reuse_preregistration(self):
        self.assay['tau'] = '0.75'
        self.assertEqual(self.cell().decision.status, 'unavailable')
        self.assay['tau'] = '0.5'
        self.assay['family_version'] = '0.2'
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_registration_after_observation_does_not_validate_fixed_design(self):
        self.support(self.cfg['registered_design_ref']['value']['record_id'])['payload']['registered_at'] = K('2030-01-01T00:00:00+00:00')
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_missing_registration_witness_preserves_descriptive_union(self):
        self.support(self.cfg['registered_design_ref']['value']['record_id'])['payload']['extensions'].pop(sa.REGISTRATION_KEY)
        r = self.result()
        self.assertEqual(r.observed_intervention_union, (A,))
        self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_state_change_and_training_member_are_not_fixed_state_assays(self):
        self.cfg['interventions'][0]['parameters_changed'] = K(True)
        self.assertEqual(self.cell().decision.status, 'unavailable')
        self.cfg['interventions'][0].update(parameters_changed=K(False), intervention_kind='training')
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_changed_model_parameter_identity_is_not_silently_fixed(self):
        self.cfg['states'][0]['subject_identity']['value']['parameter_identity'] = K('different-theta')
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_present_is_existential_but_below_requires_every_family_member(self):
        self.build(interventions=2)
        for trial in self.assay['trials'][16:]:
            trial.update(status='missing', sample_ref=K(None))
        r = self.result()
        self.assertEqual(r.present_classes, (A,))
        self.assertEqual(r.below_classes, ())
        self.assertEqual(r.J, 16)
        self.assertEqual(r.delta, F(1, 256))
        self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_all_family_members_below_allows_negative_conclusion(self):
        self.build(interventions=2)
        r = self.result()
        self.assertEqual(set(r.below_classes), set(CLASS_IDS) - {A})
        self.assertEqual(r.present_classes, (A,))
        self.assertEqual(r.expressible_support_size_finite_family.value, 1)

    def test_unperformed_entire_intervention_stays_in_family_and_multiplicity(self):
        self.build(interventions=2)
        self.assay['trials'] = self.assay['trials'][:16]
        r = self.result()
        self.assertEqual(r.J, 16)
        self.assertEqual(r.below_classes, ())
        self.assertEqual(self.cell(intervention=1, result=r).decision.N, 16)
        self.assertEqual(self.cell(intervention=1, result=r).decision.status, 'unavailable')

    def test_deleting_planned_family_member_cannot_make_below_easier(self):
        self.build(interventions=2)
        self.assay['intervention_refs'].pop()
        self.assay['trials'] = self.assay['trials'][:16]
        r = self.result()
        self.assertFalse(r.below_classes)
        self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_registered_missing_stage_stays_in_episode_J(self):
        stage = copy.deepcopy(self.registration()['stages'][0])
        stage['assay_ref'] = R('assay', 'post')
        self.registration()['stages'].append(stage)
        r = self.result()
        self.assertEqual(r.J, 16)
        self.assertEqual(r.delta, F(1, 256))

    def test_registered_class_omission_cannot_narrow_reference_universe(self):
        self.registration()['stages'][0]['classes'] = [A]
        r = self.result()
        self.assertIsNone(r.expressible_support_size_finite_family.value)
        self.assertFalse(r.below_classes)
        self.assertFalse(r.present_classes)

    def test_false_iid_assertion_or_unreadable_basis_blocks_numeric_claim(self):
        evidence = self.support('assay-iid')['payload']
        evidence['assertion'] = K(False)
        self.assertEqual(self.cell().decision.status, 'unavailable')
        evidence['assertion'] = K(True)
        evidence['access'] = 'unavailable'
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_tau_one_keeps_class_unresolved_despite_every_observed_success(self):
        self.build(tau='1')
        r = self.result()
        self.assertEqual(r.observed_intervention_union, (A,))
        self.assertEqual(r.present_classes, ())
        self.assertIn(A, r.unresolved_classes)
        self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_finite_family_and_reference_universe_qualifiers_remain_visible(self):
        r = self.result()
        self.assertTrue(r.finite_family_scope)
        self.assertEqual(r.coverage_scope, 'registered_reference_classes')
        self.assertIsNotNone(r.class_universe_ref)
        self.assertEqual(r.size_bounds, (1, 1))
        self.assertFalse(self.study().substantive_validation_performed)

    def test_partial_set_bounds_retain_unavailable_reference_classes(self):
        self.build(interventions=2)
        for trial in self.assay['trials'][16:]:
            trial.update(status='missing', sample_ref=K(None))
        r = self.result()
        self.assertEqual(r.present_classes, (A,))
        self.assertEqual(r.size_bounds, (1, 8))
        self.assertIsNone(r.expressible_support_size_finite_family.value)
        self.assertIsNone(r.reference_normalized_support.value)
        unknown = set(r.unresolved_classes) | set(r.unavailable_classes)
        self.assertEqual(unknown, set(CLASS_IDS) - {A})

    def test_empty_registry_has_undefined_normalization(self):
        # The inherited eight-class profile rejects an empty registry; the
        # empty denominator still must never be displayed as numeric coverage.
        self.seal(classes=[])
        path = self.root / 'registry.json'
        registry = json.loads(path.read_text())
        registry['classes'] = []
        path.write_text(json.dumps(registry))
        r = self.result()
        self.assertEqual(r.reference_normalized_support.status, 'undefined')
        self.assertIsNone(r.reference_normalized_support.value)
        self.assertEqual(r.size_bounds, (0, 0))
        self.assertIsNone(r.expressible_support_size_finite_family.value)
        self.assertFalse(r.present_classes)

    def test_pre_post_reuse_cannot_fabricate_new_observations(self):
        post = copy.deepcopy(self.assay)
        post['object_id'] = 'post'
        post['iid_evidence_ref'] = K(C('evidence', 'post-iid'))
        for trial in post['trials']:
            trial['trial_id'] = 'post-' + trial['trial_id']
        self.slots['post'] = copy.deepcopy(self.slots['assay'])
        for slot in self.slots['post']:
            slot['trial_id'] = 'post-' + slot['trial_id']
        self.cfg['assays'].append(post)
        iid = copy.deepcopy(self.support('assay-iid'))
        iid['record_id'] = 'post-iid'
        iid['payload']['extensions'][sa.IID_KEY] = sa.iid_witness(post)
        self.sup.append(iid)
        self.seal()
        study = self.study()
        self.assertEqual(len(study.assays), 2)
        for r in study.assays:
            self.assertFalse(r.present_classes)
            self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_failed_call_label_alone_cannot_supply_negative_evidence(self):
        self.assay['trials'][0].update(status='failed', sample_ref=K(None))
        self.row('attempt', 'call0-1')['attempt_status'] = 'failed'
        r = self.result()
        self.assertFalse(r.below_classes)
        self.assertEqual(self.cell(result=r).decision.status, 'unavailable')

    def test_no_assays_or_registered_stages_is_not_requested(self):
        self.cfg['assays'] = []
        self.support(self.cfg['registered_design_ref']['value']['record_id'])['payload']['extensions'].pop(sa.REGISTRATION_KEY)
        r = self.study()
        self.assertFalse(r.requested)
        self.assertEqual(r.status, 'not_requested')

    def test_malformed_profile_and_wrong_bundle_are_controlled(self):
        with self.assertRaises(InputError):
            sa.evaluate_support_assays({})
        self.man['analysis_config']['extensions']['longitudinal'] = None
        self.assertEqual(self.study().status, 'contract_error')

    def test_refusal_needs_scoped_nonexpression_evidence_and_original_call(self):
        self.row('realization', 's1')['completion_status'] = 'refused'
        without = self.cell().decision
        self.assertEqual((without.N, without.k_confirmed, without.k_possible), (16, 15, 16))
        (self.root / 'response.json').write_text('{"refusal": "No candidate output"}\n')
        self.obs.append(artifact_record('call-response', 'response.json'))
        self.row('attempt', 'call0-1')['raw_response_ref'] = K(C('artifact', 'call-response'))
        self.row('realization', 's1')['raw_response_ref'] = K(C('artifact', 'call-response'))
        trial = self.assay['trials'][0]
        proof = support_record('evidence', 'nonexpression', target_ref=C('attempt', 'call0-1'),
            purpose='observation', assertion=K(True), method=K('stipulated_call_inspection'),
            detail=K('A completed fixture refusal has no generated candidate.'), access='readable',
            conflict_status='none_declared', reviewer_refs=[C('role', 'reviewer')],
            extensions={sa.FAILURE_KEY: {'assay_ref': R('assay', 'assay'),
                'trial_id': trial['trial_id'], 'attempt_ref': C('attempt', 'call0-1'),
                'success_event': 'class_membership', 'determinate_nonexpression': True}})
        self.sup.append(proof)
        trial['evidence']['validation'].append(C('evidence', 'nonexpression'))
        with_proof = self.cell().decision
        self.assertEqual((with_proof.N, with_proof.k_confirmed, with_proof.k_possible), (16, 15, 15))
        self.row('attempt', 'call0-1')['raw_response_ref'] = K(state='unknown')
        self.assertEqual(self.cell().decision.k_possible, 16)

    def test_nonexpression_witness_cannot_override_accepted_positive_outputs(self):
        self.build([A] * 8)
        for i in range(8):
            self.nonexpression_witness(i)
        r = self.result()
        self.assertFalse(r.below_classes)
        self.assertIsNone(r.expressible_support_size_finite_family.value)
        self.assertEqual(self.cell(result=r).decision.k_possible, 8)

    def test_nonexpression_witness_cannot_turn_unknown_classification_negative(self):
        self.build([None] * 8)
        for i in range(8):
            self.nonexpression_witness(i)
        r = self.result()
        self.assertFalse(r.below_classes)
        self.assertEqual(self.cell(result=r).decision.k_confirmed, 0)
        self.assertEqual(self.cell(result=r).decision.k_possible, 8)

    def test_missing_or_tampered_raw_snapshot_cannot_supply_nonexpression(self):
        self.build([A] * 8)
        for i in range(8):
            self.row('realization', f's{i+1}')['completion_status'] = 'refused'
            self.nonexpression_witness(i)
        bundle = self.bundle()
        self.assertEqual(set(sa.evaluate_support_assays(bundle).assays[0].below_classes), set(CLASS_IDS))
        raw_paths = {a.snapshot_path for a in bundle.artifacts if a.record_key.startswith('artifact:raw-')}
        self.assertEqual(len(raw_paths), 8)
        missing = replace(bundle, snapshots=freeze({p: snap for p, snap in bundle.snapshots.items() if p not in raw_paths}))
        tampered = replace(bundle, snapshots=freeze({p: replace(snap, content=b'changed bytes under old digest')
            if p in raw_paths else snap for p, snap in bundle.snapshots.items()}))
        for candidate in (missing, tampered):
            with self.subTest(case='missing' if candidate is missing else 'tampered'):
                r = sa.evaluate_support_assays(candidate).assays[0]
                self.assertFalse(r.below_classes)
                self.assertEqual(self.cell(result=r).decision.k_possible, 8)

    def test_stale_loaded_context_cannot_be_reused_after_label_change(self):
        bundle = self.bundle()
        previous = sa.evaluate_support_assays(bundle)
        self.row('assignment', 'a1')['structural_class_id'] = B
        self.support('e-a1')['payload']['assertion'] = K(B)
        fresh = self.bundle()
        with self.assertRaises(InputError):
            sa.assert_current(previous, fresh)
        with self.assertRaises(InputError):
            sa.evaluate_support_assays(fresh, review=previous.review)

    def test_changed_tools_or_protocol_cannot_reuse_registered_state_identity(self):
        identity = self.cfg['states'][0]['subject_identity']['value']
        old = copy.deepcopy(identity['tool_identity'])
        identity['tool_identity'] = K('new-tool-context')
        self.assertEqual(self.cell().decision.status, 'unavailable')
        identity['tool_identity'] = old
        self.man['protocols'][0]['decoding_settings'] = K({'temperature': '0.1', 'max_output_tokens': 8192})
        self.assertEqual(self.cell().decision.status, 'unavailable')

    def test_changed_registry_meaning_under_same_id_requires_new_registration(self):
        path = self.root / 'registry.json'
        registry = json.loads(path.read_text())
        registry['classes'][0]['membership_rule'] = 'A different structural mechanism under the same class name.'
        path.write_text(json.dumps(registry))
        r = self.result()
        self.assertFalse(r.present_classes)
        self.assertFalse(r.below_classes)
        self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_changed_prompt_bytes_under_same_artifact_id_requires_new_registration(self):
        (self.root / 'prompt.txt').write_text('A different elicitation request under unchanged display identifiers.\n')
        r = self.result()
        self.assertFalse(r.present_classes)
        self.assertFalse(r.below_classes)
        self.assertIsNone(r.expressible_support_size_finite_family.value)

    def test_ineligible_iid_does_not_perform_unbudgeted_tail_arithmetic(self):
        self.support('assay-iid')['payload']['extensions'][sa.IID_KEY]['independent_calls'] = False
        bundle = self.bundle()
        with patch.object(sa, '_tails', side_effect=AssertionError('ineligible tail computation')) as tails:
            r = sa.evaluate_support_assays(bundle)
        self.assertEqual(tails.call_count, 0)
        self.assertEqual(r.tail_summands, 0)
        self.assertFalse(r.assays[0].present_classes)

    def test_sample_and_attempt_raw_response_mismatch_blocks_trial_identity(self):
        self.build([A] * 8)
        (self.root / 'original.txt').write_text('The registered original call.')
        (self.root / 'different.txt').write_text('Another call entirely.')
        self.obs.extend([artifact_record('original-response', 'original.txt'),
                         artifact_record('different-response', 'different.txt')])
        self.row('attempt', 'call0-1')['raw_response_ref'] = K(C('artifact', 'original-response'))
        self.row('realization', 's1')['raw_response_ref'] = K(C('artifact', 'different-response'))
        r = self.result()
        self.assertFalse(r.present_classes)
        self.assertEqual(self.cell(result=r).decision.status, 'unavailable')

    def test_unreadable_selected_output_cannot_supply_confirmed_success(self):
        self.build([A] * 8)
        self.obs.append(artifact_record('missing-output', 'does-not-exist.txt'))
        self.row('realization', 's1')['output_ref'] = K(C('artifact', 'missing-output'))
        r = self.result()
        self.assertFalse(r.present_classes)
        self.assertEqual((self.cell(result=r).decision.N,
                          self.cell(result=r).decision.k_confirmed,
                          self.cell(result=r).decision.k_possible), (8, 7, 8))

    def test_declared_tail_budget_is_shared_across_registered_cells(self):
        self.cfg['limits']['max_tail_summands'] = 20
        r = self.study()
        self.assertLessEqual(r.tail_summands, 20)
        self.assertTrue(any(c.decision.status == 'unavailable' for c in r.assays[0].cells))
        self.assertIsNone(r.assays[0].expressible_support_size_finite_family.value)

    def test_loaded_assay_evaluation_has_no_file_network_or_process_side_effect(self):
        bundle = self.bundle()
        with patch('builtins.open', side_effect=AssertionError('file')), \
             patch('socket.socket', side_effect=AssertionError('network')), \
             patch('subprocess.Popen', side_effect=AssertionError('process')):
            result = sa.evaluate_support_assays(bundle)
        self.assertEqual(result.assays[0].present_classes, (A,))

    def test_trial_outcomes_are_not_mutated_by_evaluation(self):
        before = copy.deepcopy(self.assay)
        self.result()
        self.assertEqual(self.assay, before)


if __name__ == '__main__':
    unittest.main()
