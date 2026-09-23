"""Additive V report coverage and privacy on explicitly stipulated test material."""
from __future__ import annotations
import json
import hashlib
import html
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from structdet_bench.reporting import plain,render_json,render_markdown,canonical_bytes,_cell
from structdet_bench.pipeline import analyze_bundle
from structdet_bench.contracts import InputError
from tests.test_phase2_pipeline import base_result,content,fixture_rows
from tests.phase2_helpers import ROOT,materialize_abc,write_abc
from tests.helpers import tagged


class ComparisonReportTests(unittest.TestCase):
    def test_both_formats_consume_same_complete_tree(self):
        r=base_result();self.assertEqual(json.loads(r.report_json),plain(r.report));self.assertEqual(render_json(r.report),r.report_json);self.assertEqual(render_markdown(r.report),r.report_markdown)
    def test_primary_values_units_statuses_and_reasons_survive_markdown(self):
        r=base_result();text=r.report_markdown.decode()
        def check(v):
            if isinstance(v,dict):
                for k,x in v.items():
                    if k in {'value','result_status','unit','outcome','mean','lower','upper','reasons','qualifications','actual_blocks'}:self.assertIn(html.escape(json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False),quote=True).replace('|','&#124;'),text)
                    elif isinstance(x,(dict,list)):check(x)
            elif isinstance(v,list):
                for x in v:check(x)
        check(plain(content(r)['predictions']))
    def test_all_contrast_operands_resolve_to_complete_contexts(self):
        c=content(base_result());operands=c['operand_records'];contexts=c['population_context_records']
        for b in c['per_block_contrasts']:
            for v in list(b['contrasts'].values())+list(b['companions']):
                for name in ['minuend_ref','subtrahend_ref']:
                    o=operands[v[name]];ctx=contexts[o['population_context_ref']]
                    self.assertEqual(o['cell_id'],ctx['cell_id']);self.assertEqual(o['view'],ctx['view'])
                    self.assertIn('selected_ids',ctx);self.assertIn('counted_ids',ctx);self.assertIn('revision_pins',ctx)
    def test_gates_retain_exact_ratios_and_requirement_flags(self):
        gates=content(base_result())['per_block_contrasts'][0]['gates'];byname={g['name']:g for g in gates}
        g=byname['B.classification_coverage'];self.assertEqual(g['threshold_ratio'],(9,10));self.assertEqual(g['observed']['numerator'],20);self.assertEqual(g['observed']['denominator'],20)
        self.assertFalse(byname['quality_band']['required'])
    def test_fixed_suite_interval_scope_and_full_target_are_explicit(self):
        for row in content(base_result())['sensitivity']:
            self.assertEqual(row['interval_scope'],'prompt_resampling_sensitivity')
            self.assertEqual(len(row['intended_blocks']),6);self.assertEqual(len(row['included_blocks']),6)
            self.assertTrue(row['caveats']);self.assertFalse(row['independent_validation_performed'])
    def test_method_and_replay_hashes_reference_actual_manifest(self):
        r=base_result();hashes={x['sha256'] for x in r.manifest['comparison_replay']['replays']}
        for s in content(r)['sensitivity']:self.assertIn(s['replay_sha256'],hashes)
        self.assertEqual(content(r)['methods']['text_identity']['unicode_category_version'],'15.1.0')
        for name,sha in r.manifest['report_files'].items():self.assertEqual(sha,hashlib.sha256(r.report_json if name=='report.json' else r.report_markdown).hexdigest())
    def test_indices_stored_once_in_manifest_not_printed_as_text_pairs(self):
        r=base_result();self.assertNotIn('indices',content(r)['replay_manifest_refs'][0]);self.assertEqual(len(r.manifest['comparison_replay']['replays']),1)
        self.assertTrue(content(r)['sensitivity'][0]['replicate_statistics_sha256'])
    def test_eight_sections_and_evidence_precede_numeric_results(self):
        r=base_result();self.assertEqual(len(r.report['sections']),8)
        self.assertLess(r.report_markdown.index(b'Independent scientific validation'),r.report_markdown.index(b'## 4.'))
        self.assertLess(r.report_markdown.index(b'### primary results'),r.report_markdown.index(b'### operand records'))
    def test_five_conjunctive_conditions_and_all_ten_disclosures_remain(self):
        i=content(base_result(),8);self.assertEqual(len(i['five_conditions']),5);self.assertEqual(len(i['ec_reporting_disclosures']),10)
        self.assertEqual(i['ec_reporting_disclosures']['current_until']['state'],'unknown')
        self.assertTrue(all(x['outcome']=='unresolved' for x in i['five_conditions']))
    def test_deferred_layer_remains_null_and_no_overall_score(self):
        r=base_result();self.assertTrue(all(x['value'] is None and x['result_status']=='deferred' and x['prerequisites'] for x in content(r,8)['deferred']))
        self.assertNotIn('overall_score',r.report_json.decode())
    def test_comparison_dependencies_cover_new_downstream_layers(self):
        d=content(base_result(),8)['dependencies'];self.assertEqual(len(d),720)
        self.assertTrue(all('sensitivity' in x['v_dependents'] and 'P1_P5_outcomes' in x['v_dependents'] for x in d))
    def test_absent_E_limits_retained_alongside_supporting_fixture_outcome(self):
        r=base_result();self.assertEqual(content(r)['predictions']['P1']['permitted_claim_scope'],'fixture_only')
        self.assertEqual(content(r,8)['comparison_integrity']['UD_006'],'actual_independent_evidence_outstanding')
        self.assertNotIn(b'not_implemented',json.dumps(plain(content(r))).encode())
    def test_untrusted_prose_and_private_locators_never_become_report_content(self):
        with TemporaryDirectory() as t:
            p,_=materialize_abc(Path(t)/'input');o,s,m=fixture_rows(p)
            secret='PRIVATE_X<script>alert(1)</script> | [leak](https://invalid.test/?secret=1)'
            m['analysis_config']['extensions']['comparison']['revision']['reason']=tagged(secret)
            m['analysis_config']['extensions']['comparison']['revision']['changes']=[secret]
            next(x for x in s if x['record_type']=='role')['payload']['entity_id']=tagged(secret)
            r=analyze_bundle(write_abc(p.parent,o,s,m))
            for data in (r.report_json,r.report_markdown,r.manifest_json):
                self.assertNotIn(b'PRIVATE_X',data);self.assertNotIn(str(p.parent).encode(),data)
    def test_rendering_controls_and_html_cannot_execute(self):
        obj=plain(base_result().report);obj['sections'][5]['content']={'primary_results':[{'outcome':'<script>x</script> | \x1b[31m [x](javascript:alert(1))'}]}
        text=render_markdown(obj)
        self.assertNotIn(b'<script>',text);self.assertNotIn(b'\x1b',text);self.assertIn(b'&lt;script&gt;',text)
    def test_invalid_new_profile_and_nonfinite_are_rejected(self):
        obj={'report_schema_version':'0.2','report_profile':'wrong','sections':plain(base_result().report['sections'])}
        with self.assertRaises(InputError):render_json(obj)
        obj['report_profile']='structdet_comparison_v1';obj['bad']=float('nan')
        with self.assertRaises(InputError):render_markdown(obj)


# The complete source crosswalk includes inherited M and deferred D groups.
from tests.test_pipeline import RF_PATHS as _M_RF_PATHS
AUDIT_RF_PATHS = {k:list(v) for k,v in _M_RF_PATHS.items()}
AUDIT_RF_PATHS.update({
 'RF-21':['sections.6.content.diagnostics.*.eligible_sample_ids','sections.6.content.diagnostics.*.method','sections.6.content.diagnostics.*.proxy_text_coverage','sections.6.content.diagnostics.*.results.surface_lexical_trigram_distance','sections.6.content.diagnostics.*.input_context_sha256'],
 'RF-22':['sections.6.content.diagnostics.*.class_diagnostics','sections.6.content.diagnostics.*.same_class_pair_count','sections.6.content.diagnostics.*.results.within_class_realization_diversity_proxy'],
 'RF-23':['sections.6.content.diagnostics.*.pair_count','sections.6.content.diagnostics.*.pairs','sections.6.content.diagnostics.*.results.structural_pair_non_equivalence'],
 'RF-24':['sections.5.content.predictions.P1','sections.5.content.predictions.P1_valid_sensitivity','sections.5.content.per_block_contrasts.*.values','sections.5.content.operand_records'],
 'RF-25':['sections.5.content.predictions.P5_comparators','sections.5.content.predictions.P5','sections.5.content.secondary_descriptive_means'],
 'RF-26':['sections.5.content.equal_block_means.*.intended_blocks','sections.5.content.equal_block_means.*.included_blocks','sections.5.content.equal_block_means.*.missing_blocks','sections.5.content.equal_block_means.*.block_values','sections.5.content.equal_block_means.*.weighting'],
 'RF-27':['sections.5.content.sensitivity.*.intervals','sections.5.content.sensitivity.*.interval_scope','sections.5.content.methods.resampling','sections.5.content.replay_manifest_refs'],
 'RF-28':['sections.5.content.per_block_contrasts.*.gates','sections.5.content.per_block_contrasts.*.qualifications','sections.5.content.predictions'],
})


def audit_paths(test,value,path):
    if not path:return
    part,*rest=path.split('.')
    if part=='*':
        test.assertIsInstance(value,list)
        for item in value:audit_paths(test,item,'.'.join(rest))
    else:
        if isinstance(value,list):test.assertLess(int(part),len(value));child=value[int(part)]
        else:test.assertIn(part,value);child=value[part]
        audit_paths(test,child,'.'.join(rest))


class Step7ReportAudit(unittest.TestCase):
    def test_all_source_report_groups_have_a_current_location(self):
        from tests.helpers import source_table
        r=plain(base_result().report)
        self.assertEqual(set(AUDIT_RF_PATHS),{row[0] for row in source_table('THEORY_TO_CODE_TRACEABILITY.md','RF')})
        for rid,paths in AUDIT_RF_PATHS.items():
            for path in paths:
                with self.subTest(group=rid,path=path):audit_paths(self,r,path)
    def test_RF21_RF23_have_real_same_subset_pair_values_not_null_slots(self):
        from tests.test_phase2_pipeline import ratio
        from fractions import Fraction
        ds=content(base_result(),7)['diagnostics'];self.assertEqual(len(ds),36)
        for d in ds:
            self.assertEqual(d['pair_count'],190);self.assertEqual(len(d['pairs']),190)
            self.assertEqual(d['eligible_count'],len(d['eligible_sample_ids']))
            self.assertEqual(d['results']['surface_lexical_trigram_distance']['pair_denominator'],d['results']['structural_pair_non_equivalence']['pair_denominator'])
            self.assertEqual(ratio(d['results']['structural_pair_non_equivalence']),Fraction(sum(x['structurally_different'] for x in d['pairs']),190))
            self.assertEqual(len(d['input_context_sha256']),64)
    def test_RF22_retains_singleton_and_pair_weighted_denominators(self):
        for d in content(base_result(),7)['diagnostics']:
            self.assertEqual(sum(c['pair_count'] for c in d['class_diagnostics']),d['same_class_pair_count'])
            self.assertEqual(d['results']['within_class_realization_diversity_proxy']['pair_denominator'],d['same_class_pair_count'])
        from structdet_bench.text_diagnostics import TextMethod,diagnose_population
        from structdet_bench.local_io import load_bundle
        from structdet_bench.populations import build_populations
        from tests.test_text_diagnostics import text_fixture
        with TemporaryDirectory() as t:
            p,*_=text_fixture(Path(t),['a b c'])
            b=load_bundle(p);d=diagnose_population(b,build_populations(b).cells[0],'classified_all',TextMethod('fixture-original-region-v1'))
            self.assertEqual(d.results['within_class_realization_diversity_proxy'].result_status,'undefined')
            self.assertEqual(d.same_class_pair_count,0)
    def test_RF21_RF23_missing_text_preserves_reason_and_original_denominator(self):
        from tests.test_phase2_pipeline import audit_variant
        r=audit_variant('ABC-NO-TEXT')
        for d in content(r,7)['diagnostics']:
            self.assertEqual(d['population_size'],20);self.assertEqual(d['eligible_count'],0)
            self.assertEqual(d['proxy_text_coverage']['denominator'],20)
            self.assertEqual(d['results']['surface_lexical_trigram_distance']['result_status'],'undefined')
            self.assertTrue(d['results']['surface_lexical_trigram_distance']['reasons'])
        self.assertEqual(content(r)['predictions']['P5']['outcome'],'supporting')
    def test_RF24_RF25_retain_primary_and_sensitivity_roles_and_exact_operands(self):
        c=content(base_result());p=c['predictions']
        self.assertEqual(p['P1']['role'],'primary');self.assertEqual(p['P1_valid_sensitivity']['role'],'prespecified_valid_sensitivity')
        self.assertEqual(p['P5']['view'],'classified_valid')
        self.assertEqual(len(p['P5_comparators']),2)
        for b in c['per_block_contrasts']:
            for con in b['contrasts'].values():
                operands=[c['operand_records'][con[k]] for k in ('minuend_ref','subtrahend_ref')]
                self.assertEqual(operands[0]['number']['unit'],operands[1]['number']['unit'])
                if b['question']=='P5':self.assertTrue(all(o['k']==20 for o in operands))
    def test_RF26_RF28_missing_block_is_explicit_not_a_changed_target(self):
        from tests.test_phase2_pipeline import audit_variant
        r=audit_variant('ABC-MISSING-BLOCK')
        for summary in content(r)['equal_block_means']:
            self.assertEqual(len(summary['intended_blocks']),6);self.assertIn('P06',summary['missing_blocks'])
            self.assertFalse(summary['full_target_complete']);self.assertEqual(summary['weighting'],'equal_prompt_block')
        self.assertEqual(content(r)['predictions']['P1']['outcome'],'not_evaluated')
        self.assertTrue(content(r)['predictions']['P1']['reasons'])
    def test_RF27_index_references_resolve_for_each_interval(self):
        r=base_result();replays={x['sha256']:x for x in r.manifest['comparison_replay']['replays']}
        for sensitivity in content(r)['sensitivity']:
            replay=replays[sensitivity['replay_sha256']]
            self.assertEqual(len(replay['indices']),2000)
            self.assertEqual(sensitivity['included_blocks'],replay['block_ids'])
            for interval in sensitivity['intervals'].values():
                self.assertEqual(interval['replicate_count'],2000);self.assertEqual(interval['interval_scope'],'prompt_resampling_sensitivity')
        self.assertNotIn('p_value',str(content(r)['predictions']))
    def test_RF28_quality_flag_never_discards_positive_breadth(self):
        from tests.test_phase2_pipeline import audit_variant,ratio
        r=audit_variant('ABC-QUALITY');p=content(r)['predictions']['P5_comparators'][0]
        self.assertEqual(p['outcome'],'not_evaluated');self.assertEqual(ratio(p['directions']['p5_valid_distinct_k_delta']['mean']),2)
        self.assertTrue(any(not g['passes'] and 'validity_floor' in g['name'] for b in content(r)['per_block_contrasts'] if b['question']=='P5' for g in b['gates']))
    def test_RF15_RF34_all_four_operational_outcomes_have_equal_public_scope(self):
        from tests.test_phase2_pipeline import audit_variant
        arrangements=[base_result(),audit_variant('ABC-CONTRARY'),audit_variant('ABC-HETEROGENEOUS'),audit_variant('ABC-NO-TEXT')]
        self.assertEqual([content(r)['predictions']['P1']['outcome'] for r in arrangements],['supporting','contrary','inconclusive','not_evaluated'])
        for r in arrangements:
            p=plain(content(r)['predictions']['P1'])
            self.assertEqual(p['permitted_claim_scope'],'fixture_only');self.assertFalse(p['independent_validation_performed'])
            for key in ('outcome','reasons','qualifications','actual_blocks'):
                self.assertIn(_cell(p[key]).encode(),r.report_markdown)
    def test_RF35_all_D_prerequisites_survive_active_V_reporting(self):
        required={'expressible_support','latent_support','convergence_frontier','structural_half_life_null','structural_half_life_empirical','external_recovery_rate','probabilistic_structural_assignment','exact_realization_entropy'}
        rows={x['metric_name']:x for x in content(base_result(),8)['deferred']}
        self.assertTrue(required<=set(rows))
        for name in required:
            self.assertIsNone(rows[name]['value']);self.assertEqual(rows[name]['result_status'],'deferred');self.assertTrue(rows[name]['prerequisites'])
    def test_RF36_current_fingerprints_match_both_complete_reports(self):
        r=base_result()
        self.assertEqual(json.loads(r.report_json),plain(r.report))
        self.assertEqual(render_markdown(r.report),r.report_markdown)
        for name,data in (('report.json',r.report_json),('report.md',r.report_markdown)):
            self.assertEqual(hashlib.sha256(data).hexdigest(),r.manifest['report_files'][name])
        self.assertEqual(content(r,8)['redaction']['source_bytes_modified'],False)


class Step7ECAudit(unittest.TestCase):
    def modified(self,edit):
        with TemporaryDirectory() as t:
            p,_=materialize_abc(Path(t)/'input');o,s,m=fixture_rows(p);edit(p,o,s,m)
            return analyze_bundle(write_abc(p.parent,o,s,m))
    def test_EC01_arithmetic_does_not_validate_structural_or_distributional_cut(self):
        r=base_result();i=content(r,8)
        self.assertEqual(content(r)['predictions']['P1']['outcome'],'supporting')
        self.assertFalse(content(r,1)['scope']['independent_validation_performed'])
        self.assertIn('deployment representativeness',content(r,1)['task']['known_omitted_conditions'])
        self.assertTrue(all(x['outcome']=='unresolved' for x in i['five_conditions']))
    def test_EC02_four_conditions_never_become_operational_openness(self):
        from tests.helpers import support_record,record_ref
        from structdet_bench.contracts import INTEGRITY_CONDITIONS
        def edit(p,o,s,m):
            requirements={key:{'outcome':'satisfied_for_scope','reason':'Mock assertion','evidence_refs':[record_ref('evidence','resampling-assumption')]} for key in INTEGRITY_CONDITIONS[1:]}
            s.append(support_record('integrity_assessment','four-only',claim_kind='operational_openness',claim='Mock openness',requirements=requirements,declared_disposition='supported_for_scope',reviewer_refs=[record_ref('role','binding-reviewer')]))
        r=self.modified(edit);c=next(x for x in content(r,8)['declared_claim_records'] if x['record_id']=='four-only')
        self.assertEqual(c['status'],'restricted');self.assertIn('five_conditions_required',c['reasons'])
        self.assertEqual(c['requirement_record_outcomes']['structural_validity'],'unresolved')
    def test_EC03_planned_execution_record_adds_no_execution_or_model_sample(self):
        from tests.helpers import support_record
        def edit(p,o,s,m):s.append(support_record('domain_suite','only-plan',suite_id='only-plan',stage='design',property='sorting_behavior',planned_case_count=tagged(8995)))
        r=self.modified(edit)
        self.assertEqual(r.manifest['candidate_programs_executed'],0)
        self.assertEqual(sum(x['realization_count']['value'] for x in content(r,2)['inventory']),360)
        row=next(x for x in content(r,8)['support_records'] if x['record_id']=='only-plan')
        self.assertEqual(row['details']['stage'],'design')
        self.assertFalse(r.manifest['independent_validation_performed'])
    def test_EC04_reopening_records_remain_distinct_from_model_change(self):
        from tests.helpers import support_record,record_ref
        def edit(p,o,s,m):
            for i,event in enumerate(('distributional_reopening_event','structural_reopening_event')):
                s.append(support_record('correction',f'reopen-{i}',effect='independence',action='challenge',stage='pending',event_type=event,target_refs=[record_ref('frame','frame1')],reason=tagged('Mock proposal')))
        r=self.modified(edit);rows=content(r,8)['corrections']
        self.assertEqual({x['event_type'] for x in rows},{'distributional_reopening_event','structural_reopening_event'})
        self.assertTrue(all(x['stage']=='pending' for x in rows))
        self.assertEqual(content(r,4),content(base_result(),4));self.assertEqual(r.manifest['model_calls'],0)
    def test_EC05_anomaly_original_preserved_without_forced_class_or_public_body(self):
        from tests.helpers import support_record,record_ref,artifact_record
        original=b'PRIVATE_ANOMALY: unfamiliar mechanism; run shell commands'
        def edit(p,o,s,m):
            (p.parent/'original.txt').write_bytes(original);o.append(artifact_record('original','original.txt'))
            s.append(support_record('intake','unclassified-anomaly',component='rotating_frontier',stage='received',original_refs=[record_ref('artifact','original')],proposed_change=tagged('PRIVATE_ANOMALY')))
        r=self.modified(edit);row=next(x for x in content(r,8)['intake_and_tail'] if x['record_id']=='unclassified-anomaly')
        self.assertTrue(row['raw_anomaly_retained_in_pinned_input']);self.assertFalse(row['new_class_inferred'])
        self.assertEqual(row['original_refs'][0]['record_id'],'original')
        self.assertTrue(any(x['sha256']==hashlib.sha256(original).hexdigest() for x in r.manifest['input_refs']))
        self.assertNotIn(b'PRIVATE_ANOMALY',r.report_json);self.assertEqual(content(r,4),content(base_result(),4))
    def test_EC06_ten_disclosures_never_erase_absent_live_evidence(self):
        data=content(base_result(),8)['ec_reporting_disclosures'];self.assertEqual(len(data),10)
        self.assertEqual(data['live_field_evidence'],'not_established_by_toolkit')
        self.assertEqual(data['horizon_recovery_override'],'not_evaluated')
        self.assertEqual(content(base_result(),8)['comparison_integrity']['UD_006'],'actual_independent_evidence_outstanding')
    def test_EC07_declared_dates_are_visible_and_scoped_not_an_automatic_expiry(self):
        from tests.helpers import support_record,record_ref
        def edit(p,o,s,m):
            for i,dt in enumerate(('2026-10-01','2026-10-08T12:30:00+00:00')):
                s.append(support_record('integrity_assessment',f'dated-{i}',claim_kind='validated_measurement',claim='Scoped mock declaration',requirements={},declared_disposition='restricted',assessed_at=tagged('2026-09-10'),current_until=tagged(dt),reviewer_refs=[record_ref('role','binding-reviewer')],scope_refs=[record_ref('cell','P01-'+'AB'[i])]))
        r=self.modified(edit);rows=content(r,8)['declared_claim_records']
        self.assertEqual([x['current_until']['value'] for x in rows],['2026-10-01','2026-10-08T12:30:00+00:00'])
        self.assertEqual([x['scope_refs'][0]['record_id'] for x in rows],['P01-A','P01-B'])
        self.assertTrue(all(x['substantive_claim']=='not_certified_by_software' for x in rows))
        disclosure=content(r,8)['ec_reporting_disclosures']['current_until']
        self.assertEqual(disclosure['state'],'unknown');self.assertEqual(len(disclosure['scoped_declarations']),2)
        self.assertIn(b'2026-10-01',r.report_markdown)
    def test_EC07_unknown_or_invalid_dates_have_no_invented_lifetime(self):
        from structdet_bench.pipeline import _declared_date
        self.assertEqual(_declared_date(tagged(state='unknown'))['state'],'unknown')
        for value in ('2026-02-30','PRIVATE<script>','2026-10-01TPRIVATE00:00:00Z'):
            data=_declared_date(tagged(value));self.assertNotIn('value',data)
            self.assertNotIn('PRIVATE',json.dumps(data));self.assertEqual(data['state'],'known')
        self.assertEqual(_declared_date(tagged('2026-10-01T12:30:00Z'))['value'],'2026-10-01T12:30:00Z')
    def test_EC08_reference_and_source_volume_never_multiply_observations(self):
        from tests.helpers import support_record
        def edit(p,o,s,m):
            for i in range(3):s.append(support_record('source',f'external-name-{i}',source_id=f'nominal-{i}',sha256=tagged(state='unknown')))
        r=self.modified(edit)
        self.assertEqual(len(content(r,5)['reference_coverage']['registered_class_ids']),8)
        self.assertEqual(len(content(r,2)['attempts']),72)
        self.assertEqual(sum(x['realization_count']['value'] for x in content(r,2)['inventory']),360)
        self.assertTrue(all(x['outcome']=='unresolved' for x in content(r,8)['five_conditions']))
