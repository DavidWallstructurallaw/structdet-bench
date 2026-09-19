"""Exact replay oracles and adverse record checks, entirely software fixtures."""
from __future__ import annotations
import copy
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import uncertainty as u
from structdet_bench.comparison_records import BLOCKS, review_comparison
from structdet_bench.comparisons import compare_study, number
from structdet_bench.contracts import InputError, freeze
from structdet_bench.local_io import load_bundle
from structdet_bench.populations import build_populations
from structdet_bench.text_diagnostics import diagnose_cells, method_from_record, limits_from_record
from tests.helpers import ROOT, tagged, record_ref, artifact_record, rewrite_evidence_bundle
from tests.phase2_helpers import (paired_summary_fixture, populated_comparison_fixture,
                                  add_fixture_dependence)


def mutable(x): return json.loads(u._canonical(x))


def reseal(raw):
    raw['indices_sha256']=u._hash(raw['indices'])
    raw['sha256']=u._hash({k:v for k,v in raw.items() if k!='sha256'})
    return raw


def sensitivity(surface='0.1',structural='0',**kwargs):
    s=paired_summary_fixture(surface,structural,**kwargs)
    return u.summarize_sensitivity(s,u.DependenceCheck('fixture_stipulated',s.included_blocks,fixture=True))


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.replay=u.make_replay(BLOCKS)
    def test_fixed_shape_seed_and_order(self):
        r=self.replay
        self.assertEqual(r['seed'],20260917);self.assertEqual(r['replicates'],2000)
        self.assertEqual(r['block_ids'],BLOCKS);self.assertEqual(r['index_base'],0)
        self.assertTrue(all(len(x)==6 and all(type(i)is int and 0<=i<6 for i in x) for x in r['indices']))
    def test_recorded_rng_identity(self):
        r=self.replay['rng'];self.assertEqual(r['algorithm'],'MT19937')
        self.assertEqual(r['api'],'random.Random.randrange');self.assertEqual(r['state_version'],3)
        self.assertTrue(r['python_version']);self.assertTrue(r['implementation'])
    def test_independent_rejection_sampling_reference(self):
        expected=json.loads((ROOT/'tests/fixtures/resampling_oracles.json').read_text())['rng_reference']['cases']
        for p in (2,6):
            r=u.make_replay(BLOCKS[:p]);rng=random.Random(20260917);rows=[]
            for _ in range(2000):
                row=[]
                for _ in range(p):
                    x=rng.getrandbits(p.bit_length())
                    while x>=p:x=rng.getrandbits(p.bit_length())
                    row.append(x)
                rows.append(row)
            self.assertEqual(mutable(r['indices']),rows)
            self.assertEqual(r['indices_sha256'],expected[str(p)]['indices_sha256'])
            self.assertEqual(rows[:5],expected[str(p)]['first_rows'])
    def test_global_rng_is_unchanged(self):
        before=random.getstate();u.make_replay(BLOCKS);self.assertEqual(random.getstate(),before)
    def test_repeat_generation_identical(self):
        self.assertEqual(self.replay,u.make_replay(BLOCKS))
    def test_read_only_manifest_and_caller_input(self):
        raw=mutable(self.replay);before=copy.deepcopy(raw);r=u.validate_replay(raw,BLOCKS)
        self.assertEqual(raw,before)
        with self.assertRaises(TypeError):r['seed']=0
        with self.assertRaises(TypeError):r['indices'][0][0]=1
    def test_known_replay_never_calls_rng(self):
        with patch.object(u.random,'Random',side_effect=AssertionError('no RNG during replay')):
            self.assertEqual(u.validate_replay(self.replay,BLOCKS),self.replay)
    def test_future_runtime_consumes_pinned_indices(self):
        old=mutable(self.replay);old['rng']['python_version']='3.12.1';reseal(old)
        self.assertEqual(u.validate_replay(old,BLOCKS,expected_sha256=old['sha256'])['indices'],self.replay['indices'])
    def test_wrong_external_manifest_pin_rejected(self):
        with self.assertRaises(InputError):u.validate_replay(self.replay,BLOCKS,expected_sha256='0'*64)
    def test_modified_rng_metadata_cannot_retain_old_identity(self):
        old=mutable(self.replay);old['rng']['python_version']='3.12.1'
        with self.assertRaises(InputError):u.validate_replay(old,BLOCKS)
    def test_unknown_version_algorithm_and_state_rejected(self):
        for field,value in [('algorithm','unregistered'),('api','eval'),('state_version',True),('state_version',4),('python_version',''),('implementation','unknown')]:
            r=mutable(self.replay);r['rng'][field]=value;reseal(r)
            with self.subTest(field=field),self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
    def test_constants_cannot_change_even_with_recomputed_hash(self):
        for field,value in [('schema_version','0.2'),('method','row_bootstrap'),('seed',20260918),('seed',True),('replicates',1999),('index_base',True),('quantile','nearest'),('statistic','row_mean'),('probabilities',['0.05','0.95'])]:
            r=mutable(self.replay);r[field]=value;reseal(r)
            with self.subTest(field=field),self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
    def test_missing_extra_and_executable_keys_rejected(self):
        for field in self.replay:
            r=mutable(self.replay);r.pop(field)
            with self.subTest(field=field),self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
        r=mutable(self.replay);r['object_hook']='run'
        with self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
    def test_truncated_or_extended_replicates_fail(self):
        for count in (0,1999,2001):
            r=mutable(self.replay);r['indices']=(r['indices']*2)[:count];reseal(r)
            with self.subTest(count=count),self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
    def test_bad_row_widths_or_type_fail(self):
        for row in ([],[0]*5,[0]*7,None,{}):
            r=mutable(self.replay);r['indices'][0]=row;reseal(r)
            with self.subTest(row=row),self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
    def test_index_bool_float_negative_out_of_bounds_fail(self):
        for val in (True,False,1.0,-1,6,'1',None,{},[]):
            r=mutable(self.replay);r['indices'][0][0]=val;reseal(r)
            with self.subTest(value=val),self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
    def test_changed_index_or_array_hash_fails(self):
        for field in ('indices','indices_sha256','sha256'):
            r=mutable(self.replay)
            if field=='indices':r[field][0][0]=(r[field][0][0]+1)%6
            else:r[field]='0'*64
            with self.assertRaises(InputError):u.validate_replay(r,BLOCKS)
    def test_block_identity_order_and_subset_cannot_rebind(self):
        for ids in (BLOCKS[::-1],BLOCKS[:5],('P01',)*6,('X01',)+BLOCKS[1:]):
            with self.subTest(ids=ids),self.assertRaises(InputError):u.validate_replay(self.replay,ids)
    def test_invalid_block_inventories(self):
        for ids in ((),[],None,'P01',(True,'P02'),BLOCKS+('P07',),('x\n','b')):
            with self.subTest(ids=ids),self.assertRaises(InputError):u.make_replay(ids)
    def test_single_block_has_no_replay(self):
        with self.assertRaisesRegex(InputError,'fewer_than_two_blocks'):u.make_replay(('P01',))


class ArithmeticTests(unittest.TestCase):
    def test_mf18_source_toy(self):
        f=json.loads((ROOT/'tests/fixtures/resampling_oracles.json').read_text())['toy']
        ns=[number('d','unit',Fraction(x)) for x in f['values']]
        self.assertEqual(u.replicate_means(ns,f['draws']),tuple(Fraction(x) for x in f['means']))
    def test_vf_full_quantile_oracle(self):
        values=tuple(Fraction(j,1999) for j in range(2000))
        self.assertEqual(u.percentile(values,Fraction(1,40)),Fraction(1,40))
        self.assertEqual(u.percentile(values,Fraction(39,40)),Fraction(39,40))
        self.assertEqual(Fraction(1999,40),Fraction('49.975'))
    def test_integer_rank_exact_member(self):
        self.assertEqual(u.percentile((Fraction(-2),Fraction(1),Fraction(5)),Fraction(1,2)),1)
        self.assertEqual(u.percentile((Fraction(9),),Fraction(39,40)),9)
    def test_quantile_sorts_values_not_block_order(self):
        xs=tuple(Fraction(j,1999) for j in range(1999,-1,-1))
        self.assertEqual(u.percentile(xs,Fraction(1,40)),Fraction(1,40))
    def test_toy_is_not_accepted_as_full_replay(self):
        r=mutable(u.make_replay(BLOCKS[:2]));r['indices']=[[0,0],[0,1],[1,1]];reseal(r)
        with self.assertRaises(InputError):u.validate_replay(r,BLOCKS[:2])
    def test_mean_is_equal_block_not_output_count(self):
        xs=[number('d','u',Fraction(1,10)),number('d','u',Fraction(3,10))]
        self.assertEqual(u.replicate_means(xs,[(0,1)]),(Fraction(1,5),))
    def test_all_p1_components_use_same_rows(self):
        r=sensitivity(['0.1','0.3','-0.1','0.2','0.4','0'],['0','0.1','0','-0.1','0.2','0'])
        self.assertEqual(r.status,'available')
        for a,b,c in zip(*(r.replicate_means[n] for n in ('surface_gain','structural_gain','p1_proxy_gain_contrast'))):self.assertEqual(a-b,c)
        self.assertEqual(len({x['replay_sha256'] for x in r.intervals.values()}),1)
    def test_degenerate_range_keeps_scope(self):
        r=sensitivity()
        x=r.intervals['surface_gain'];self.assertEqual(x['lower'].exact_ratio,(1,10));self.assertEqual(x['upper'].exact_ratio,(1,10))
        self.assertTrue(x['degenerate']);self.assertEqual(r.interval_scope,'prompt_resampling_sensitivity')
        self.assertFalse(r.independent_validation_performed);self.assertIn('no_label_schema_or_total_generation_uncertainty_estimated',r.caveats)
    def test_exact_nonzero_is_not_tolerance_clamped(self):
        tiny=Fraction(1,10**100);r=sensitivity(str(tiny.numerator/tiny.denominator))
        self.assertGreater(u.scalar(r.intervals['surface_gain']['lower']),0)
    def test_underflow_is_withheld_not_zero_effect(self):
        r=sensitivity('1e-400');self.assertEqual(r.status,'unavailable');self.assertFalse(r.intervals)
    def test_invalid_value_types_and_nonfinite_fail(self):
        for value in (True,None,float('inf'),float('nan'),'0.1'):
            n=number('x','u',Fraction(1,10));n=replace(n,value=value,exact_ratio=None)
            with self.assertRaises(InputError):u.scalar(n)
    def test_exact_ratio_cannot_disagree_with_value(self):
        n=replace(number('x','u',Fraction(1,10)),value=-0.1)
        with self.assertRaises(InputError):u.scalar(n)
    def test_unavailable_means_never_create_replicates(self):
        s=paired_summary_fixture('0.1','0');bad=dict(s.means);bad['surface_gain']=number('surface_gain','u',status='unavailable')
        r=u.summarize_sensitivity(replace(s,means=freeze(bad)),u.DependenceCheck('fixture_stipulated',BLOCKS))
        self.assertEqual(r.status,'unavailable');self.assertFalse(r.replicate_means)
    def test_incompatible_units_and_estimands_fail(self):
        vals=[number('d','u',Fraction(1,10)),number('other','u',Fraction(3,10))]
        with self.assertRaises(InputError):u.replicate_means(vals,[(0,1)])
    def test_bad_toy_indices_and_values_fail(self):
        vals=[number('d','u',1),number('d','u',3)]
        for rows in ([],[(True,1)],[(0,2)],[(0,)],[(0,1,1)]):
            with self.assertRaises(InputError):u.replicate_means(vals,rows)
    def test_bad_quantiles_never_drop_values(self):
        for xs,q in (([0,float('nan')],Fraction(1,40)),([False,1],Fraction(1,40)),([0,1],0.025),([0,1],Fraction(2)),([],Fraction(1,40))):
            with self.assertRaises(InputError):u.percentile(xs,q)
    def test_resource_limit_retains_original_mean_and_no_replicate_subset(self):
        s=paired_summary_fixture('0.1','0');dep=u.DependenceCheck('fixture_stipulated',BLOCKS)
        r=u.summarize_sensitivity(s,dep,limit=3)
        self.assertEqual(r.status,'unavailable');self.assertFalse(r.intervals);self.assertFalse(r.replicate_means)
        self.assertEqual(r.source_summary.means['surface_gain'].exact_ratio,(1,10))
    def test_stale_summary_mean_rejected(self):
        s=paired_summary_fixture('0.1','0');m=dict(s.means);m['surface_gain']=number('surface_gain',s.means['surface_gain'].unit,Fraction(1,5))
        r=u.summarize_sensitivity(replace(s,means=freeze(m)),u.DependenceCheck('fixture_stipulated',BLOCKS))
        self.assertIn('stale_summary_mean',r.reasons)
    def test_changed_linked_contrast_is_not_silently_recomputed(self):
        s=paired_summary_fixture('0.1','0');rows={b:dict(v) for b,v in s.block_values.items()}
        rows['P01']['p1_proxy_gain_contrast']=number('p1_proxy_gain_contrast',s.means['surface_gain'].unit,Fraction(1,5))
        r=u.summarize_sensitivity(replace(s,block_values=freeze(rows)),u.DependenceCheck('fixture_stipulated',BLOCKS))
        self.assertIn('p1_linked_contrast_mismatch',r.reasons)
    def test_missing_component_cannot_use_a_different_block_set(self):
        s=paired_summary_fixture('0.1','0');rows={b:dict(v) for b,v in s.block_values.items()};del rows['P02']['surface_gain']
        r=u.summarize_sensitivity(replace(s,block_values=freeze(rows)),u.DependenceCheck('fixture_stipulated',BLOCKS))
        self.assertIn('linked_component_set_mismatch',r.reasons)
    def test_single_block_retains_description_no_interval(self):
        r=sensitivity('0.1','0',blocks=('P01',),subset=True)
        self.assertEqual(r.status,'unavailable');self.assertIn('fewer_than_two_blocks',r.reasons)
        self.assertEqual(r.source_summary.means['surface_gain'].exact_ratio,(1,10))
    def test_two_block_explicit_subset_has_own_replay(self):
        r=sensitivity(['0.1','0.3'],'0',blocks=('P01','P03'),subset=True)
        self.assertEqual(r.status,'available');self.assertEqual(r.replay['block_ids'],('P01','P03'))
        self.assertFalse(r.source_summary.full_target_complete)
    def test_implicit_subset_cannot_claim_full_interval(self):
        r=sensitivity(['0.1','0.3'],'0',blocks=('P01','P03'))
        self.assertEqual(r.status,'unavailable');self.assertIn('incomplete_full_target_no_silent_subset',r.reasons)
    def test_quality_restriction_does_not_delete_blocks(self):
        r=sensitivity(gated=False)
        self.assertEqual(r.status,'available');self.assertEqual(r.source_summary.included_blocks,BLOCKS)
        self.assertFalse(r.source_summary.eligible_before_resampling)
    def test_unknown_or_foreign_dependence_withholds_interval(self):
        s=paired_summary_fixture('0.1','0')
        for dep in (u.DependenceCheck('unresolved',BLOCKS),u.DependenceCheck('record_supported',BLOCKS[::-1])):
            r=u.summarize_sensitivity(s,dep);self.assertEqual(r.status,'unavailable');self.assertFalse(r.intervals)
    def test_correction_same_blocks_can_reuse_indices_but_changes_statistics(self):
        s=paired_summary_fixture('0.1','0');r=u.summarize_sensitivity(s,u.DependenceCheck('fixture_stipulated',BLOCKS))
        t=paired_summary_fixture('0.2','0');corrected=u.summarize_sensitivity(t,u.DependenceCheck('fixture_stipulated',BLOCKS),replay=r.replay)
        self.assertEqual(r.replay,corrected.replay);self.assertNotEqual(r.operand_sha256,corrected.operand_sha256)
        self.assertEqual(r.intervals['surface_gain']['lower'].exact_ratio,(1,10))
        self.assertEqual(corrected.intervals['surface_gain']['lower'].exact_ratio,(1,5))
    def test_large_exact_ratio_hash_does_not_require_decimal_expansion(self):
        s=paired_summary_fixture(Fraction(1,2)+Fraction(1,2**15000),'0')
        r=u.summarize_sensitivity(s,u.DependenceCheck('fixture_stipulated',BLOCKS),limit=20000)
        self.assertEqual(r.status,'available')
        self.assertEqual(u.scalar(r.intervals['surface_gain']['mean'],limit=20000),Fraction(1,2)+Fraction(1,2**15000))
        self.assertIsNotNone(r.operand_sha256)
    def test_source_pins_are_actual_frozen_bytes(self):
        data=json.loads((ROOT/'tests/fixtures/resampling_oracles.json').read_text())
        for name,digest in data['source_pins'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)


class StudyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.root=Path(cls.tmp.name)
        p,o,s,m=populated_comparison_fixture(cls.root,blocks=BLOCKS)
        add_fixture_dependence(o,s,m)
        cls.p=p;cls.obs=o;cls.support=s;cls.man=m
        cls.bundle=load_bundle(rewrite_evidence_bundle(cls.root,o,s,m))
        cls.pops=build_populations(cls.bundle);review=review_comparison(cls.bundle)
        cls.ds=diagnose_cells(cls.bundle,cls.pops.cells,method_from_record(review.configuration['text_method']),limits=limits_from_record(review.configuration['limits']))
        cls.comp=compare_study(cls.bundle,cls.pops,cls.ds)
        cls.out=u.resample_study(cls.bundle,cls.comp)
    def test_actual_text_to_shared_six_block_replay(self):
        self.assertTrue(all(r.status=='available' for r in self.out.results),[r.reasons for r in self.out.results])
        self.assertEqual(len(self.out.replays),1);self.assertEqual(len(self.out.results),6)
        for r in self.out.results:self.assertEqual(r.source_summary.included_blocks,BLOCKS)
    def test_original_populations_and_dependencies_unchanged(self):
        self.assertEqual(self.comp, self.out.comparisons)
        self.assertEqual(sum(c.inventory.selected_count.value for c in self.pops.cells),360)
        self.assertTrue(all(len(row.dependencies['call_groups'])==2 for row in self.comp.blocks))
    def test_unknown_actual_assessment_keeps_descriptive_means(self):
        cfg=mutable(self.comp.review.configuration);cfg['resampling']['dependence_assessment_ref']=tagged(state='unknown')
        review=replace(self.comp.review,configuration=freeze(cfg))
        comp=replace(self.comp,review=review)
        # Stale explicit configuration is also rejected, rather than trusted.
        out=u.resample_study(self.bundle,comp)
        self.assertTrue(all(x.status=='unavailable' for x in out.results))
        self.assertEqual(out.results[0].source_summary.means['surface_gain'].exact_ratio,(8,19))
    def test_no_io_network_or_global_random_during_components(self):
        with patch('builtins.open',side_effect=AssertionError('I/O')),patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):
            result=u.resample_study(self.bundle,self.comp)
        self.assertTrue(result.results)
    def test_conflicting_shared_group_overrides_declared_independence(self):
        rows=list(self.comp.blocks);row=rows[0];second=next(i for i,b in enumerate(rows) if b.block_id=='P02' and b.question==row.question and b.view==row.view)
        dep=dict(rows[second].dependencies);dep['call_groups']=row.dependencies['call_groups']
        rows[second]=replace(rows[second],dependencies=freeze(dep))
        comp=replace(self.comp,blocks=tuple(rows))
        result=u.resample_study(self.bundle,comp)
        self.assertIn('observed_cross_block_shared_generation',result.results[0].dependence.reasons)
    def test_imported_replay_uses_snapshot_and_ignores_later_disk_changes(self):
        with TemporaryDirectory() as t:
            root=Path(t);o=copy.deepcopy(self.obs);s=copy.deepcopy(self.support);m=copy.deepcopy(self.man)
            import shutil
            for p in self.root.glob('*.txt'):shutil.copy2(p,root/p.name)
            data=u._canonical({'schema_version':'0.1','replays':self.out.replays});(root/'replay.json').write_bytes(data)
            a=artifact_record('replay','replay.json');a['expected_sha256']=tagged(hashlib.sha256(data).hexdigest());o.append(a)
            m['analysis_config']['extensions']['comparison']['resampling']['replay_ref']=tagged(record_ref('artifact','replay'))
            bundle=load_bundle(rewrite_evidence_bundle(root,o,s,m));review=review_comparison(bundle)
            comp=compare_study(bundle,self.pops,self.ds)
            (root/'replay.json').write_text('do not read')
            result=u.resample_study(bundle,comp)
            self.assertTrue(all(r.status=='available' for r in result.results),[r.reasons for r in result.results])
            self.assertEqual(result.replays,self.out.replays)
    def test_nonfixture_context_does_not_promote_mock_assumptions(self):
        comp=replace(self.comp,material_role='confirmatory')
        result=u.resample_study(self.bundle,comp)
        self.assertTrue(all(r.status=='unavailable' for r in result.results))
        self.assertIn('mock_dependence_cannot_validate_empirical_scope',result.results[0].dependence.reasons)
    def test_missing_replay_is_not_regenerated(self):
        cfg=mutable(self.comp.review.configuration);cfg['resampling']['replay_ref']=tagged(record_ref('artifact','absent'))
        review=replace(self.comp.review,configuration=freeze(cfg));comp=replace(self.comp,review=review)
        with patch.object(u,'make_replay',side_effect=AssertionError('must not replace absent replay')):
            result=u.resample_study(self.bundle,comp)
        self.assertTrue(all(r.reasons==('replay_artifact_unavailable',) for r in result.results))
    def test_no_comparison_is_not_requested(self):
        comp=replace(self.comp,requested=False)
        self.assertEqual(u.resample_study(self.bundle,comp).results,())
    def test_changed_bundle_cannot_reuse_prior_comparison_even_if_config_matches(self):
        with TemporaryDirectory() as t:
            root=Path(t);o=copy.deepcopy(self.obs);s=copy.deepcopy(self.support);m=copy.deepcopy(self.man)
            import shutil
            for old in self.root.glob('*.txt'):shutil.copy2(old,root/old.name)
            next(x for x in s if x['record_id']=='e-P01-A-a1')['payload']['state']='withdrawn'
            bundle=load_bundle(rewrite_evidence_bundle(root,o,s,m))
            self.assertEqual(configuration_hash(review_comparison(bundle).configuration),self.comp.configuration_sha256)
            out=u.resample_study(bundle,self.comp)
            self.assertTrue(all(x.status=='unavailable' for x in out.results))
            self.assertTrue(any('comparison_snapshot_mismatch' in x.reasons for x in out.results))
    def test_actual_prediction_pipeline_keeps_both_p5_primaries(self):
        from structdet_bench.predictions import evaluate_predictions
        out=evaluate_predictions(self.out)
        self.assertEqual(out.p1_primary.outcome,'supporting')
        self.assertEqual([x.outcome for x in out.p5_comparators],['supporting','supporting'])
        self.assertEqual(out.p5_full.outcome,'supporting')
        self.assertEqual(out.p1_primary.permitted_claim_scope,'fixture_only')
    def test_no_text_preserves_count_based_p5_only(self):
        from structdet_bench.predictions import evaluate_predictions
        comp=compare_study(self.bundle,self.pops,())
        out=evaluate_predictions(u.resample_study(self.bundle,comp))
        self.assertEqual(out.p1_primary.outcome,'not_evaluated')
        self.assertEqual(out.p5_full.outcome,'supporting')
    def test_unknown_context_and_posthoc_claim_do_not_change_old_results(self):
        from structdet_bench.predictions import evaluate_predictions
        before=evaluate_predictions(self.out)
        comp=replace(self.comp,material_role='confirmatory')
        after=evaluate_predictions(u.resample_study(self.bundle,comp))
        self.assertEqual(after.p1_primary.outcome,'not_evaluated')
        self.assertEqual(before.p1_primary.outcome,'supporting')
        self.assertEqual(self.out.results[0].source_summary.means['surface_gain'].exact_ratio,(8,19))
    def test_wrong_api_type_is_controlled(self):
        with self.assertRaises(InputError):u.resample_study({},self.comp)


def configuration_hash(config):
    from structdet_bench.comparison_records import configuration_fingerprint
    return configuration_fingerprint(config)
