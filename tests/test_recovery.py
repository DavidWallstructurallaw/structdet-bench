"""Passive Step 7 recovery fixtures and independently specified set oracles.

All records and interventions are stipulated software fixtures. Positive output
checks exercise conditional arithmetic and never certify actual model recovery.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import copy
from dataclasses import replace
from fractions import Fraction as F
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
from tests.test_longitudinal import materialize_observed, R, O, E
from tests import phase3_helpers as gate


class RecoveryFixture(unittest.TestCase):
    """Actual source records, outputs, calls, classifications and dated evidence."""
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.build(evidence=self.__class__.__name__ != 'FixtureOracleTests')

    def build(self, case='half', *, evidence=True):
        catalogue = json.loads((ROOT / 'tests/fixtures/recovery_cases.json').read_text())
        self.case = next(c for c in catalogue['cases'] if c['id'] == case)
        panels = []
        for class_id in CLASS_IDS:
            rows = []
            for stage in ('pre', 'post'):
                status = self.case[stage][list(CLASS_IDS).index(class_id)]
                rows.append(([class_id] * 12) if status == 'present' else
                            ([CLASS_IDS[0]] * 6 + [class_id] * 6) if status == 'unresolved' else
                            [CLASS_IDS[0]] * 12)
            panels.append(rows)
        self.obs, self.sup, self.man = materialize_observed(self.root, panels)
        self.cfg = self.man['analysis_config']['extensions']['longitudinal']
        self.cfg['states'][1]['subject_identity']['value']['checkpoint_sha256'] = K('b' * 64)
        self.cfg['capabilities'] += ['support_assay', 'recovery']
        self.cfg['assays'] = []
        self.cfg['interventions'] = []
        self.obs = [r for r in self.obs if r['record_type'] != 'attempt']
        self.slots = {}
        self.family_pairs = []
        for stage, tag in enumerate(('pre', 'post')):
            trials = []
            self.slots[tag] = []
            for panel, class_id in enumerate(CLASS_IDS):
                identity = f'I{stage}p{panel}'
                member = O('intervention', identity, pre_state_ref=R('state', f'S{stage}'),
                    post_state_ref=R('state', f'S{stage}'), intervention_kind='inference_configuration',
                    parameters_changed=K(False), direct_answer_injection=K(False), external_refs=[])
                self.cfg['interventions'].append(member)
                selection = self.man['analysis_config']['selection'][stage * len(CLASS_IDS) + panel]
                positions = []
                for pos, sid in enumerate(selection['selected_sample_ids']['value'], 1):
                    aid, gid, tid = f'call{stage}-{panel}-{pos}', f'group{stage}-{panel}-{pos}', f'trial{stage}-{panel}-{pos}'
                    raw, output = f'raw-{aid}', f'output-{sid}'
                    content = f'Stipulated candidate {sid}; software fixture only.\n'.encode()
                    (self.root / f'{output}.txt').write_bytes(content)
                    (self.root / f'{raw}.json').write_text(json.dumps({'candidate_position': 1, 'output': content.decode()}))
                    self.obs.extend([artifact_record(output, f'{output}.txt'), artifact_record(raw, f'{raw}.json')])
                    self.row('realization', sid).update(attempt_id=K(aid), generation_group_id=K(gid), within_group_index=K(1),
                        raw_response_ref=K(C('artifact', raw)), output_ref=K(C('artifact', output)),
                        output_content_hash=K(hashlib.sha256(content).hexdigest()))
                    self.obs.append({**C('attempt', aid), 'attempt_id': aid, 'analysis_cell_id': f'c{stage}p{panel}',
                        'attempt_status': 'succeeded', 'retry_of': K(None), 'raw_response_ref': K(C('artifact', raw)),
                        'generation_group_id': K(gid), 'planned_candidate_count': K(1), 'registered_call_order': K(pos)})
                    positions.append({'generation_group_id': gid, 'registered_call_order': pos,
                        'within_group_index': 1, 'attempt_id': K(aid)})
                    self.slots[tag].append({'trial_id': tid, 'intervention_ref': R('intervention', identity),
                        'measurement_ref': R('measurement', f'M{stage}p{panel}'), 'attempt_ref': C('attempt', aid), 'candidate_position': 1})
                    trials.append({'trial_id': tid, 'intervention_ref': R('intervention', identity),
                        'measurement_ref': K(R('measurement', f'M{stage}p{panel}')), 'sample_ref': K(C('realization', sid)),
                        'status': 'observed', 'evidence': E()})
                selection['registered_positions'] = K(positions)
            assay = O('assay', tag, state_ref=R('state', f'S{stage}'), family_id='paired-eight-prompts', family_version='0.1',
                intervention_refs=[R('intervention', f'I{stage}p{p}') for p in range(8)], success_event='class_membership',
                registry_ref=C('reference_registry', 'sorting_reference_eight'), tau='0.5', alpha='0.125',
                allocation='bonferroni_equal', trials=trials, iid_evidence_ref=K(C('evidence', f'{tag}-iid')))
            self.cfg['assays'].append(assay)
            self.sup.append(self.evidence(f'{tag}-iid', purpose='independence',
                extensions={sa.IID_KEY: sa.iid_witness(assay)}))
        self.pre, self.post = self.cfg['assays']
        self.intervention = O('intervention', 'treatment', pre_state_ref=R('state', 'S0'), post_state_ref=R('state', 'S1'),
            intervention_kind='training', parameters_changed=K(True), direct_answer_injection=K(False), external_refs=[])
        self.cfg['interventions'].append(self.intervention)
        self.episode = O('recovery_episode', 'recover', pre_assay_ref=R('assay', 'pre'), post_assay_ref=R('assay', 'post'),
            intervention_ref=R('intervention', 'treatment'), registry_ref=C('reference_registry', 'sorting_reference_eight'),
            criterion_version='finite_family_binomial_threshold_v1', non_injection_ref=K(C('evidence', 'non-injection')),
            external_validation_refs=[C('evidence', 'external-validation')])
        self.cfg['recovery_episodes'] = [self.episode]
        self.seal_assays()
        if evidence:
            self.add_recovery_evidence()

    def row(self, kind, identity):
        return next(r for r in self.obs if r['record_type'] == kind and r['record_id'] == identity)

    def support(self, identity):
        return next(r for r in self.sup if r['record_id'] == identity)

    def evidence(self, identity, *, purpose='observation', extensions=None, **kw):
        return support_record('evidence', identity, target_ref=C('cell', 'c1p0'), purpose=purpose,
            assertion=K(True), method=K('stipulated_source_inspection'), detail=K('Fixture only; no model or learning action.'),
            access='readable', conflict_status='none_declared', reviewer_refs=[C('role', 'reviewer')],
            extensions=extensions or {}, **kw)

    def bundle(self):
        return load_bundle(rewrite_evidence_bundle(self.root, self.obs, self.sup, self.man))

    def seal_assays(self):
        self.support('registration')['payload'].setdefault('extensions', {})[sa.REGISTRATION_KEY] = sa.registration_witness(
            self.cfg['assays'], list(CLASS_IDS), self.slots, bundle=self.bundle())
        for assay in self.cfg['assays']:
            self.support(f"{assay['object_id']}-iid")['payload']['extensions'][sa.IID_KEY] = sa.iid_witness(assay)

    def add_recovery_evidence(self):
        from structdet_bench import recovery as rc
        for identity, content in (('training-material', 'Stipulated instructional material, distinct from evaluation.\n'),
                                  ('evaluation-material', 'Distinct held-out evaluation material.\n'),
                                  ('recovery-review', 'Stipulated reviewer findings; software fixture only.\n')):
            (self.root / f'{identity}.txt').write_text(content)
            self.obs.append(artifact_record(identity, f'{identity}.txt'))
        self.sup.append(support_record('source', 'external-source', source_id='external-grounded-source',
            locator=K('Stipulated source outside the simulated system'), origin=K('Fixture independently grounded material'),
            knowledge_type=K('stipulated_grounded_observation'), evidence_refs=[C('artifact', 'training-material')]))
        self.intervention['external_refs'] = [C('source', 'external-source')]
        self.sup.append(support_record('independence_assessment', 'grounding', left_ref=C('source', 'external-source'),
            right_ref=C('artifact', 'evaluation-material'), dimension='structural_grounding', outcome='supported_for_scope',
            criterion=K('Stipulated independent grounding for the registered evaluation scope'),
            reviewer_refs=[C('role', 'reviewer')]))
        self.intervention['evidence']['independence'] = [C('independence_assessment', 'grounding')]
        self.sup.extend([self.evidence('non-injection', purpose='independence'),
                         self.evidence('external-validation', purpose='validity')])
        for identity, assertion in (('non-injection', 'no_direct_answer_substitution'),
                                    ('external-validation', 'post_intervention_expression_validated')):
            self.support(identity)['payload'].update(assertion=K(assertion), artifact_refs=[C('artifact', 'recovery-review')])
        for stage in ('entry', 'preprocessing', 'selection', 'exposure', 'expression'):
            identity = f'stage-{stage}'
            record = self.evidence(identity)
            record['payload'].update(assertion=K('stage_supported'), artifact_refs=[C('artifact', 'recovery-review')])
            self.sup.append(record)
            self.episode['evidence']['process'].append(C('evidence', identity))
        self.seal_assays()
        self.seal_recovery()

    def seal_recovery(self, **changes):
        from structdet_bench import recovery as rc
        bundle = self.bundle()
        defaults = dict(hypothesis='Stipulated recovery of missing registered classes after grounded training',
            permitted_exposure_refs=[C('artifact', 'training-material')],
            evaluation_material_refs=[C('artifact', 'evaluation-material')],
            member_pairs=[{'pre': R('intervention', f'I0p{p}'), 'post': R('intervention', f'I1p{p}')} for p in range(8)])
        defaults.update(changes)
        witness = rc.registration_witness(self.episode, bundle=bundle, **defaults)
        self.support('registration')['payload']['extensions'][rc.REGISTRATION_KEY] = {
            'method': rc.METHOD, 'inspection_status': 'registered_before_inspection', 'episodes': [witness]}
        self.seal_evidence()

    def seal_evidence(self):
        from structdet_bench import recovery as rc
        # Role-independent substrate identity is shared; each statement remains
        # separate and no final assay or recovery number enters the source data.
        witness = rc.evidence_witness(self.episode, 'grounding', bundle=self.bundle())
        for identity, role in [('grounding', 'grounding'), ('non-injection', 'non_injection'),
                               ('external-validation', 'external_validation')] + [(f'stage-{s}', s)
                                    for s in ('entry', 'preprocessing', 'selection', 'exposure', 'expression')]:
            item = copy.deepcopy(witness)
            item['role'] = role
            self.support(identity)['payload'].setdefault('extensions', {})[rc.EVIDENCE_KEY] = item

    def study(self, **kw):
        from structdet_bench import recovery as rc
        return rc.evaluate_recovery(self.bundle(), **kw)

    def result(self):
        return self.study().episodes[0]



class FixtureOracleTests(RecoveryFixture):
    def test_fixture_registry_is_the_original_eight_classes(self):
        c = json.loads((ROOT / 'tests/fixtures/recovery_cases.json').read_text())
        self.assertEqual(c['plan_sha256'], gate.PLAN_SHA256)
        self.assertEqual(tuple(c['classes']), CLASS_IDS)
        self.assertEqual(c['scope'], 'stipulated_software_fixtures_only')

    def test_half_oracle_uses_real_loader_and_exact_threshold_trials(self):
        result = sa.evaluate_support_assays(self.bundle())
        self.assertEqual(result.J, 128)
        self.assertEqual(set(result.assays[0].present_classes), set(CLASS_IDS[:6]))
        self.assertEqual(set(result.assays[0].below_classes), set(CLASS_IDS[6:]))
        self.assertEqual(set(result.assays[1].present_classes), set(CLASS_IDS[:7]))
        self.assertEqual(set(result.assays[1].below_classes), {CLASS_IDS[7]})
        self.assertTrue(all(c.N == 12 for a in result.assays for c in a.cells))
        self.assertEqual(result.assays[0].delta, F(1, 2048))

    def test_catalogue_arithmetic_is_independent_set_intersection(self):
        catalogue = json.loads((ROOT / 'tests/fixtures/recovery_cases.json').read_text())
        for case in catalogue['cases']:
            with self.subTest(case=case['id']):
                pre = {c for c, s in zip(CLASS_IDS, case['pre']) if s == 'present'}
                post = {c for c, s in zip(CLASS_IDS, case['post']) if s == 'present'}
                if 'unresolved' in case['pre']:
                    self.assertIsNone(case['denominator'])
                    continue
                missing = set(CLASS_IDS) - pre
                self.assertEqual(case['denominator'], len(missing))
                recovered = missing & post
                if case['err'] is not None:
                    self.assertEqual(F(*case['err']), F(len(recovered), len(missing)))
                if case['bounds'] is not None:
                    unresolved = {c for c, s in zip(CLASS_IDS, case['post']) if s == 'unresolved'} & missing
                    self.assertEqual(tuple(F(*v) for v in case['bounds']),
                        (F(len(recovered), len(missing)), F(len(recovered) + len(unresolved), len(missing))))


class MissingSetTests(RecoveryFixture):
    def test_eight_classes_six_pre_one_of_two_missing_recovered(self):
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'available', r)
        self.assertEqual(r.external_recovery_rate.value, F(1, 2))
        self.assertEqual(set(r.pre_present), set(CLASS_IDS[:6]))
        self.assertEqual(set(r.missing_classes), set(CLASS_IDS[6:]))
        self.assertEqual(r.confirmed_recovered, (CLASS_IDS[6],))
        self.assertEqual(r.post_below, (CLASS_IDS[7],))
        self.assertIsNone(r.partial_information_bounds)
        self.assertEqual(r.evidence_status, 'fixture_only')
        self.assertFalse(r.model_recovery_established)

    def test_known_empty_missing_set_is_undefined_not_zero_or_one(self):
        self.build('empty')
        r = self.result()
        self.assertEqual(r.missing_classes, ())
        self.assertEqual(r.external_recovery_rate.status, 'undefined')
        self.assertIsNone(r.external_recovery_rate.value)
        self.assertIn('empty_missing_reference_set', r.external_recovery_rate.reasons)

    def test_pre_uncertainty_never_creates_a_missing_denominator(self):
        self.build('pre_unknown')
        r = self.result()
        self.assertIsNone(r.missing_classes)
        self.assertEqual(r.pre_unresolved, (CLASS_IDS[5],))
        self.assertEqual(set(r.pre_below), set(CLASS_IDS[6:]))
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertIsNone(r.external_recovery_rate.value)
        self.assertIsNone(r.partial_information_bounds)

    def test_partial_post_is_separate_deterministic_information_bounds(self):
        self.build('partial')
        r = self.result()
        self.assertEqual(set(r.missing_classes), set(CLASS_IDS[5:]))
        self.assertEqual(r.confirmed_recovered, (CLASS_IDS[5],))
        self.assertEqual(r.unresolved_post, (CLASS_IDS[6],))
        self.assertEqual(r.post_below, (CLASS_IDS[7],))
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertIsNone(r.external_recovery_rate.value)
        self.assertEqual(r.partial_information_bounds, (F(1, 3), F(2, 3)))

    def test_resolved_no_recovery_is_exact_zero(self):
        self.build('none_recovered')
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'available')
        self.assertEqual(r.external_recovery_rate.value, F(0))
        self.assertEqual(r.confirmed_recovered, ())

    def test_resolved_full_recovery_is_exact_one(self):
        self.build('all_recovered')
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'available')
        self.assertEqual(r.external_recovery_rate.value, F(1))
        self.assertEqual(set(r.confirmed_recovered), set(CLASS_IDS[6:]))

    def test_unresolved_post_class_outside_missing_set_does_not_block_err(self):
        for trial in self.post['trials'][12:18]:
            sid = trial['sample_ref']['value']['record_id']
            aid = f'a{sid[1:]}'
            self.row('assignment', aid)['structural_class_id'] = CLASS_IDS[0]
            self.support(f'e-{aid}')['payload']['assertion'] = K(CLASS_IDS[0])
        self.seal_evidence()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'available')
        self.assertEqual(r.external_recovery_rate.value, F(1, 2))
        self.assertEqual(r.unresolved_post, ())

    def test_unavailable_pre_iid_cannot_be_treated_as_all_missing(self):
        self.support('pre-iid')['payload']['state'] = 'withdrawn'
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertIsNone(r.missing_classes)
        self.assertIsNone(r.partial_information_bounds)

    def test_missing_post_artifact_is_unknown_not_negative(self):
        for trial in self.post['trials'][72:84]:
            sid = trial['sample_ref']['value']['record_id']
            (self.root / f'output-{sid}.txt').unlink()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertIn(CLASS_IDS[6], r.unresolved_post)
        self.assertNotIn(CLASS_IDS[6], r.post_below)


class RecoveryEvidenceTests(RecoveryFixture):
    def test_nominal_different_source_name_without_grounding_is_unavailable(self):
        self.support('external-source')['payload']['origin'] = K('Different vendor, separate interface')
        self.intervention['evidence']['independence'] = []
        self.seal_recovery()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertEqual(set(r.missing_classes), set(CLASS_IDS[6:]))
        self.assertEqual(r.confirmed_recovered, (CLASS_IDS[6],))

    def test_derivative_source_independence_outcome_withholds_qualified_rate(self):
        self.support('grounding')['payload']['outcome'] = 'not_supported_for_scope'
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertEqual(r.confirmed_recovered, (CLASS_IDS[6],))

    def test_unknown_grounding_criterion_withholds_qualified_rate(self):
        self.support('grounding')['payload']['criterion'] = K(state='unknown')
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_direct_answer_copying_withholds_qualified_rate(self):
        self.intervention['direct_answer_injection'] = K(True)
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_unknown_noninjection_is_not_permission_to_assume_no_injection(self):
        self.support('non-injection')['payload']['assertion'] = K(state='unknown')
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_noninjection_review_conflict_is_retained(self):
        self.support('non-injection')['payload']['conflict_status'] = 'unresolved'
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_external_validation_withdrawal_preserves_assay_sets(self):
        before = self.result()
        self.support('external-validation')['payload']['state'] = 'withdrawn'
        after = self.result()
        self.assertEqual(after.external_recovery_rate.status, 'unavailable')
        self.assertEqual(after.pre_present, before.pre_present)
        self.assertEqual(after.missing_classes, before.missing_classes)
        self.assertEqual(after.confirmed_recovered, before.confirmed_recovered)

    def test_unqualified_reviewer_cannot_support_intervention_gate(self):
        self.support('reviewer')['payload']['qualification'] = K(state='unknown')
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_unavailable_indispensable_evidence_artifact_blocks_qualified_rate(self):
        (self.root / 'recovery-review.txt').unlink()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_exposure_identical_to_scored_material_cannot_qualify(self):
        (self.root / 'evaluation-material.txt').write_bytes((self.root / 'training-material.txt').read_bytes())
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_malformed_recovery_registration_preserves_separately_valid_assay_facts(self):
        from structdet_bench import recovery as rc
        registration = self.support('registration')['payload']['extensions'][rc.REGISTRATION_KEY]
        registration['episodes'][0]['permitted_exposure_refs'] = [None]
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertIsNone(r.external_recovery_rate.value)
        self.assertEqual(set(r.pre_present), set(CLASS_IDS[:6]))
        self.assertEqual(set(r.missing_classes), set(CLASS_IDS[6:]))
        self.assertEqual(set(r.pre_assay.observed_intervention_union), set(CLASS_IDS[:6]))
        self.assertEqual(set(r.post_assay.observed_intervention_union), set(CLASS_IDS[:7]))
        self.assertEqual(set(r.post_assay.present_classes), set(CLASS_IDS[:7]))
        self.assertTrue(any(g.name == 'registration' and g.status == 'unavailable' for g in r.gates))

    def test_posthoc_registration_cannot_supply_qualified_missing_set_episode(self):
        from structdet_bench import recovery as rc
        self.support('registration')['payload']['extensions'][rc.REGISTRATION_KEY]['inspection_status'] = 'registered_after_inspection'
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_nonmock_parent_cannot_promote_mock_indispensable_child(self):
        self.cfg['data_role'] = 'descriptive'
        self.man['data_role'] = 'descriptive'
        for measurement in self.cfg['measurements']:
            measurement['data_role'] = 'descriptive'
        for record in self.sup:
            record['payload'].update(data_role='descriptive', mock=False)
        child = self.evidence('mock-descendant')
        self.sup.append(child)
        self.support('grounding')['payload']['evidence_refs'].append(C('evidence', 'mock-descendant'))
        self.seal_assays()
        self.seal_recovery()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertTrue(any('mock' in reason for g in r.gates for reason in g.reasons), r.gates)
        self.assertFalse(r.substantive_validation_performed)
        self.assertFalse(r.model_recovery_established)

    def test_withdrawn_evidence_inside_tagged_origin_cannot_be_ignored(self):
        self.sup.append(self.evidence('withdrawn-origin'))
        self.support('withdrawn-origin')['payload']['state'] = 'withdrawn'
        self.support('external-source')['payload']['origin']['evidence_refs'] = [C('evidence', 'withdrawn-origin')]
        self.seal_recovery()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertTrue(any('inactive' in why for g in r.gates for why in g.reasons), r.gates)

    def test_grounding_source_knowledge_type_remains_required(self):
        self.support('external-source')['payload']['knowledge_type'] = K(state='unknown')
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_forged_external_expressibility_labels_do_not_replace_builtin_assays(self):
        self.support('external-validation')['payload']['extensions']['externally_reviewed_support'] = {
            'expressible_pre': list(CLASS_IDS), 'expressible_post': list(CLASS_IDS), 'external_recovery_rate': '1'}
        self.support('pre-iid')['payload']['state'] = 'withdrawn'
        r = self.result()
        self.assertIsNone(r.missing_classes)
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')


class CompatibilityTests(RecoveryFixture):
    def test_unknown_resealed_criterion_version_cannot_select_another_estimator(self):
        self.episode['criterion_version'] = 'invented-unreviewed-method-v2'
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_changed_success_event_blocks_cross_stage_rate(self):
        self.post['success_event'] = 'valid_class_membership'
        self.seal_assays()
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_changed_probability_threshold_is_a_different_missing_set_criterion(self):
        self.post['tau'] = '0.4'
        self.seal_assays()
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_changed_family_cannot_be_selected_after_post_results(self):
        self.post['family_id'] = 'post-selected-prompts'
        self.seal_assays()
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_wrong_checkpoint_cannot_attribute_another_models_recovery(self):
        self.man['cells'][8]['checkpoint_identifier'] = K('wrong-model-checkpoint')
        self.seal_assays()
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_training_intervention_requires_changed_parameter_or_checkpoint_identity(self):
        self.cfg['states'][1]['subject_identity']['value']['parameter_identity'] = K('theta-0')
        self.cfg['states'][1]['subject_identity']['value']['checkpoint_sha256'] = K('a' * 64)
        for cell in self.man['cells'][8:]:
            cell['checkpoint_identifier'] = K('theta-0')
        self.seal_assays()
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_training_intervention_cannot_claim_fixed_old_parameters(self):
        self.intervention['parameters_changed'] = K(False)
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_inference_tools_support_explicit_assisted_system_scope(self):
        self.intervention.update(intervention_kind='tools', parameters_changed=K(False))
        post = self.cfg['states'][1]['subject_identity']['value']
        post['parameter_identity'] = K('theta-0')
        post['checkpoint_sha256'] = K('a' * 64)
        post['tool_identity'] = K('new-grounded-tool')
        for cell in self.man['cells'][8:]:
            cell['checkpoint_identifier'] = K('theta-0')
        self.seal_assays()
        self.seal_recovery(changes_tools=True)
        r = self.result()
        self.assertEqual(r.external_recovery_rate.value, F(1, 2), r)
        self.assertFalse(r.changes_model_parameters)
        self.assertTrue(r.changes_tools)
        self.assertFalse(r.model_recovery_established)

    def test_changed_tool_identity_without_declaration_is_not_silent_recovery(self):
        self.cfg['states'][1]['subject_identity']['value']['tool_identity'] = K('undeclared-tool')
        self.seal_assays()
        self.seal_recovery()
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')


class StageAndCorrectionTests(RecoveryFixture):
    def revision(self, kind='schema', event='structural_reopening_event', *, disposition='applied', affected=None):
        (self.root / 'original-anomaly.txt').write_text('Original unclosed anomaly; no class assignment.\n')
        self.obs.append(artifact_record('original-anomaly', 'original-anomaly.txt'))
        r = O('revision', 'revision1', revision_kind=kind, event_type=event,
            affected_refs=affected or [R('assay', 'post')], original_refs=[C('artifact', 'original-anomaly')],
            old_identity=K('sorting-cut-v0.1'), new_identity=K('proposed-sorting-cut-v0.2'), disposition=disposition)
        self.cfg['revisions'].append(r)
        return r

    def test_five_exogamy_stages_are_retained_separately(self):
        r = self.result()
        self.assertEqual(len(r.stages), 5)
        self.assertEqual({s.stage for s in r.stages}, {'entry', 'preprocessing', 'selection', 'exposure', 'expression'})

    def test_selection_survival_cannot_be_inferred_from_before_after_score(self):
        self.episode['evidence']['process'].remove(C('evidence', 'stage-selection'))
        self.seal_recovery()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertEqual(r.confirmed_recovered, (CLASS_IDS[6],))

    def test_explicit_false_exposure_descendant_overrules_stage_support_assertion(self):
        self.sup.append(support_record('exposure', 'denied-exposure', subject_ref=C('source', 'external-source'),
            role_ref=C('role', 'reviewer'), stage='training', material_refs=[C('artifact', 'training-material')],
            exposed=K(False)))
        self.support('stage-exposure')['payload']['evidence_refs'].append(C('exposure', 'denied-exposure'))
        self.seal_evidence()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertEqual(next(s for s in r.stages if s.stage == 'exposure').status, 'unavailable')

    def test_explicit_no_selection_stage_keeps_its_own_not_applicable_status(self):
        from structdet_bench import recovery as rc
        payload = self.support('stage-selection')['payload']
        payload['assertion'] = K('stage_not_applicable')
        payload['detail'] = K('Registered fixture exposure used all material without a selection operation.')
        self.seal_evidence()
        payload['extensions'][rc.EVIDENCE_KEY]['outcome'] = 'not_applicable'
        r = self.result()
        self.assertEqual(r.external_recovery_rate.value, F(1, 2))
        stage = next(s for s in r.stages if s.stage == 'selection')
        self.assertEqual(stage.status, 'not_applicable')
        self.assertFalse(stage.inferred_from_score)

    def test_indispensable_exposure_stage_cannot_be_declared_not_applicable(self):
        from structdet_bench import recovery as rc
        payload = self.support('stage-exposure')['payload']
        payload['assertion'] = K('stage_not_applicable')
        self.seal_evidence()
        payload['extensions'][rc.EVIDENCE_KEY]['outcome'] = 'not_applicable'
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_failed_entry_evidence_does_not_erase_valid_expression_evidence(self):
        self.support('stage-entry')['payload']['state'] = 'withdrawn'
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertEqual(r.confirmed_recovered, (CLASS_IDS[6],))

    def test_schema_recut_cannot_turn_old_samples_into_recovery(self):
        self.revision()
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertIsNone(r.external_recovery_rate.value)

    def test_original_anomaly_and_both_cut_identities_remain_reviewable(self):
        self.revision()
        study = self.study()
        self.assertEqual(len(study.revisions), 1)
        r = study.revisions[0]
        self.assertEqual(r.old_identity['value'], 'sorting-cut-v0.1')
        self.assertEqual(r.new_identity['value'], 'proposed-sorting-cut-v0.2')
        self.assertEqual(r.original_refs[0]['record_id'], 'original-anomaly')
        self.assertEqual(r.original_availability, (True,))
        self.assertEqual((r.new_model_samples, r.new_recursive_rounds), (0, 0))
        self.assertFalse(r.model_recovery_established)

    def test_distributional_reopening_record_does_not_create_new_samples(self):
        self.revision(kind='metadata', event='distributional_reopening_event', affected=[R('root', 'R1')])
        study = self.study()
        self.assertEqual(study.revisions[0].event_type, 'distributional_reopening_event')
        self.assertEqual(study.revisions[0].new_model_samples, 0)
        self.assertEqual(study.episodes[0].external_recovery_rate.value, F(1, 2))

    def test_rejected_schema_proposal_does_not_invalidate_unchanged_cut(self):
        self.revision(disposition='rejected')
        self.assertEqual(self.result().external_recovery_rate.value, F(1, 2))

    def test_unrelated_revision_leaves_episode_available(self):
        self.revision(kind='metadata', event='correction', affected=[R('root', 'R1')])
        self.assertEqual(self.result().external_recovery_rate.value, F(1, 2))

    def test_claim_only_independence_correction_preserves_descriptive_sets(self):
        before = self.result()
        self.revision(kind='independence', event='correction', affected=[R('intervention', 'treatment')])
        after = self.result()
        self.assertEqual(after.external_recovery_rate.status, 'unavailable')
        self.assertEqual(after.pre_present, before.pre_present)
        self.assertEqual(after.missing_classes, before.missing_classes)
        self.assertEqual(after.confirmed_recovered, before.confirmed_recovered)

    def test_membership_correction_reaches_dependent_results_and_preserves_unrelated_panels(self):
        self.sup.append(support_record('correction', 'withdraw-classification',
            target_refs=[C('assignment', 'a169')], effect='membership', action='withdraw', stage='applied',
            reviewer_refs=[C('role', 'reviewer')], reason=K('Stipulated assignment withdrawal'), event_type='correction'))
        study = self.study()
        impact = next(i for i in study.correction_impacts if i.correction_id == 'withdraw-classification')
        changed = set(impact.invalidated_result_refs)
        preserved = set(impact.preserved_result_refs)
        self.assertTrue(any('distribution' in r and 'M1p6' in r for r in changed), changed)
        self.assertTrue(any('err' in r and 'recover' in r for r in changed), changed)
        self.assertTrue(any('distribution' in r and 'M0p0' in r for r in preserved), preserved)
        self.assertTrue(any('distribution' in r and 'M1p0' in r for r in preserved), preserved)
        self.assertFalse(any('M0p0' in r or 'M1p0' in r for r in changed), changed)
        self.assertFalse(impact.old_results_overwritten)
        self.assertEqual((impact.new_model_samples, impact.new_recursive_rounds), (0, 0))

    def test_reanalysis_creates_no_new_trials_samples_or_recursive_rounds(self):
        bundle = self.bundle()
        from structdet_bench import recovery as rc
        records_before = bundle.records
        configuration_before = copy.deepcopy(self.cfg)
        a = rc.evaluate_recovery(bundle)
        b = rc.evaluate_recovery(bundle)
        self.assertEqual(a, b)
        self.assertEqual(bundle.records, records_before)
        self.assertEqual(self.cfg, configuration_before)
        self.assertEqual(len([r for r in self.obs if r['record_type'] == 'realization']), 192)
        self.assertEqual(len(self.cfg['states']), 2)
        self.assertEqual(len(self.cfg['transitions']), 1)


class SnapshotAndScopeTests(RecoveryFixture):
    def test_absent_profile_is_not_requested(self):
        del self.man['analysis_config']['extensions']['longitudinal']
        self.assertEqual(self.study().status, 'not_requested')

    def test_recovery_capability_not_requested_has_no_numeric_rate(self):
        self.cfg['capabilities'].remove('recovery')
        r = self.study()
        self.assertEqual(r.status, 'not_requested')
        self.assertFalse(r.episodes)

    def test_wrong_bundle_type_is_rejected(self):
        from structdet_bench import recovery as rc
        with self.assertRaises(InputError):
            rc.evaluate_recovery({})

    def test_malformed_profile_is_controlled_error(self):
        self.man['analysis_config']['extensions']['longitudinal'] = None
        self.assertEqual(self.study().status, 'contract_error')

    def test_stale_assays_cannot_be_reused_after_underlying_assignment_changes(self):
        from structdet_bench import recovery as rc
        b = self.bundle()
        old = sa.evaluate_support_assays(b)
        self.row('assignment', 'a169')['structural_class_id'] = CLASS_IDS[0]
        self.support('e-a169')['payload']['assertion'] = K(CLASS_IDS[0])
        with self.assertRaises(InputError):
            rc.evaluate_recovery(self.bundle(), assays=old)
        self.assertEqual(rc.evaluate_recovery(b, assays=old).episodes[0].external_recovery_rate.value, F(1, 2))

    def test_forged_cached_assay_sets_are_rejected_even_with_original_fingerprint(self):
        from structdet_bench import recovery as rc
        b = self.bundle()
        old = sa.evaluate_support_assays(b)
        invented = replace(old.assays[1], present_classes=tuple(CLASS_IDS), below_classes=())
        forged = replace(old, assays=(old.assays[0], invented))
        with self.assertRaises(InputError):
            rc.evaluate_recovery(b, assays=forged)

    def test_fresh_evaluation_rejects_changed_training_bytes_under_old_witnesses(self):
        (self.root / 'training-material.txt').write_text('Replaced training material under the original record identity.\n')
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertEqual(set(r.missing_classes), set(CLASS_IDS[6:]))

    def test_fresh_evaluation_rejects_changed_evaluation_bytes_under_old_witnesses(self):
        (self.root / 'evaluation-material.txt').write_text('Replaced held-out evaluation under the original record identity.\n')
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_fresh_evaluation_rejects_changed_review_bytes_under_old_witnesses(self):
        (self.root / 'recovery-review.txt').write_text('Different review material under the same artifact identity.\n')
        self.assertEqual(self.result().external_recovery_rate.status, 'unavailable')

    def test_classification_revision_requires_renewed_recovery_review(self):
        # Change a class outside M. Set arithmetic remains one of two; the old
        # review is still stale because it inspected the prior observation set.
        self.row('assignment', 'a109')['structural_class_id'] = CLASS_IDS[0]
        self.support('e-a109')['payload']['assertion'] = K(CLASS_IDS[0])
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertEqual(r.confirmed_recovered, (CLASS_IDS[6],))
        self.seal_evidence()
        self.assertEqual(self.result().external_recovery_rate.value, F(1, 2))

    def test_widened_registered_exposure_requires_renewed_noninjection_and_validation_review(self):
        from structdet_bench import recovery as rc
        prior = {r['record_id']: copy.deepcopy(r['payload']['extensions'][rc.EVIDENCE_KEY])
                 for r in self.sup if rc.EVIDENCE_KEY in r['payload'].get('extensions', {})}
        (self.root / 'additional-exposure.txt').write_text('Additional permitted instructional material.\n')
        self.obs.append(artifact_record('additional-exposure', 'additional-exposure.txt'))
        self.seal_recovery(permitted_exposure_refs=[C('artifact', 'training-material'), C('artifact', 'additional-exposure')])
        for identity, witness in prior.items():
            self.support(identity)['payload']['extensions'][rc.EVIDENCE_KEY] = witness
        r = self.result()
        self.assertEqual(r.external_recovery_rate.status, 'unavailable')
        self.assertTrue(any(g.name in {'non_injection', 'external_validation'} and g.status == 'unavailable' for g in r.gates))
        self.seal_evidence()
        self.assertEqual(self.result().external_recovery_rate.value, F(1, 2))

    def test_stale_recovery_result_rejects_same_display_id_changed_material(self):
        from structdet_bench import recovery as rc
        before = self.bundle()
        result = rc.evaluate_recovery(before)
        (self.root / 'training-material.txt').write_text('Changed material under same display identity.\n')
        with self.assertRaises(InputError):
            rc.assert_current(result, self.bundle())
        rc.assert_current(result, before)

    def test_postload_evaluation_performs_no_file_network_or_process_operations(self):
        from structdet_bench import recovery as rc
        b = self.bundle()
        with patch('builtins.open', side_effect=AssertionError('new file read')), \
             patch('socket.socket', side_effect=AssertionError('network operation')), \
             patch('subprocess.Popen', side_effect=AssertionError('process execution')):
            result = rc.evaluate_recovery(b)
        self.assertEqual(result.episodes[0].external_recovery_rate.value, F(1, 2))


class SuppliedComponentTests(unittest.TestCase):
    """Exercise real populated four-state curve and fit inputs to the consumer."""
    def setUp(self):
        from tests.test_half_life import RecordFixture
        self.f = RecordFixture()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        from structdet_bench import longitudinal as lg, half_life as hl
        self.bundle = self.f.bundle()
        self.review = lr.review_longitudinal(self.bundle)
        self.observed = lg.observe_longitudinal(self.bundle, review=self.review)
        self.fits = hl.fit_half_lives(self.bundle, observed=self.observed)
        self.assertEqual(len(self.observed.measurements), 4)
        self.assertEqual(self.fits.results[0].fit.empirical.status, 'available')

    def test_supplied_current_review_observed_and_nonempty_fit_roundtrip(self):
        from structdet_bench import recovery as rc
        result = rc.evaluate_recovery(self.bundle, review=self.review, observed=self.observed, fits=self.fits)
        self.assertEqual(result.observed, self.observed)
        self.assertEqual(result.fits, self.fits)
        self.assertEqual(result.observed.measurements[0].diversity.value, F(1, 2))
        self.assertGreater(result.fits.results[0].fit.empirical.value, 0)
        self.assertFalse(result.episodes)

    def test_forged_review_with_current_snapshot_is_rejected(self):
        from structdet_bench import recovery as rc
        with self.assertRaises(InputError):
            rc.evaluate_recovery(self.bundle, review=replace(self.review, status='invented'))

    def test_forged_observed_value_with_original_context_is_rejected(self):
        from structdet_bench import recovery as rc
        first = self.observed.measurements[0]
        forged = replace(self.observed, measurements=(replace(first,
            diversity=replace(first.diversity, value=F(3, 4))),) + self.observed.measurements[1:])
        with self.assertRaises(InputError):
            rc.evaluate_recovery(self.bundle, observed=forged)

    def test_forged_empirical_fit_with_original_context_is_rejected(self):
        from structdet_bench import recovery as rc
        first = self.fits.results[0]
        forged = replace(self.fits, results=(replace(first,
            fit=replace(first.fit, empirical=replace(first.fit.empirical, value=999))),))
        with self.assertRaises(InputError):
            rc.evaluate_recovery(self.bundle, observed=self.observed, fits=forged)

    def test_old_observed_and_fit_are_rejected_after_actual_classification_change(self):
        from structdet_bench import recovery as rc
        row = next(r for r in self.f.obs if r['record_type'] == 'assignment' and r['record_id'] == 'a1')
        row['structural_class_id'] = CLASS_IDS[1]
        self.f.support('e-a1')['payload']['assertion'] = K(CLASS_IDS[1])
        fresh = self.f.bundle()
        for supplied in ({'review': self.review}, {'observed': self.observed}, {'fits': self.fits}):
            with self.subTest(component=next(iter(supplied))), self.assertRaises(InputError):
                rc.evaluate_recovery(fresh, **supplied)
        old = rc.evaluate_recovery(self.bundle, observed=self.observed, fits=self.fits)
        self.assertEqual(old.fits, self.fits)


if __name__ == '__main__':
    unittest.main()
