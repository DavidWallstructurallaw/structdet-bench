"""Step 5 conformance: independent arithmetic and previously accepted populations.

All test material is stipulated. Numeric oracles use a separate log-count
identity and exact fractions; passing these checks supplies no empirical theory
result, human adjudication, model measurement, or executed sorting program.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import ast
import copy
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
from itertools import product
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from structdet_bench import metrics
from structdet_bench.contracts import ExactNumber, InputError, ThresholdToken
from structdet_bench.local_io import load_bundle, parse_json_bytes
from structdet_bench.metrics import CORE_NAMES, cell_metrics, count_metrics, population_metrics, prefix_metric
from structdet_bench.populations import build_populations, prefix
from tests.helpers import ROOT, population_bundle, rewrite_evidence_bundle, support_record, record_ref, tagged

S,T,H,C,E1,E2=CORE_NAMES
A,B,D='SORT-ADJ','SORT-INS','SORT-MERGE'
ORACLES=ROOT/'tests/fixtures/arithmetic_oracles.json'
HERO=[
 'SORT-MERGE','SORT-PIVOT','SORT-MERGE','SORT-HEAP','SORT-COUNT',
 'SORT-MERGE','SORT-PIVOT','SORT-MERGE','SORT-HEAP','SORT-RADIX',
 'SORT-MERGE','SORT-PIVOT','SORT-MERGE','SORT-PIVOT','SORT-COUNT',
 'SORT-MERGE','SORT-PIVOT','SORT-MERGE','SORT-PIVOT','SORT-HEAP']


def values(d):
    return {k:(v.result_status,v.value) for k,v in d.results.items()}


class Checks(unittest.TestCase):
    def close(self,actual,expected):
        self.assertIsNotNone(actual)
        self.assertTrue(math.isfinite(actual))
        self.assertLessEqual(abs(actual-float(expected)),1e-12+1e-10*abs(float(expected)))


class Arithmetic(Checks):
    def test_source_oracles(self):
        for case in json.loads(ORACLES.read_text())['cases']:
            with self.subTest(case=case['fixture_id']):
                out=count_metrics(case['counts'],case['population_size'])
                self.assertEqual(out.population_size,case['population_size'])
                for name,wanted in case['expected'].items():
                    r=out.results[name]
                    if wanted is None:
                        self.assertEqual(r.result_status,'undefined');self.assertIsNone(r.value)
                    else:
                        self.assertEqual(r.result_status,'available')
                        if name==S:
                            self.assertIs(type(r.value),int);self.assertEqual(r.value,wanted)
                        elif isinstance(wanted,list):
                            self.assertEqual(r.exact_ratio,tuple(wanted));self.close(r.value,Fraction(*wanted))
                        else:self.close(r.value,Decimal(wanted))

    def test_oracle_identity_and_role(self):
        data=json.loads(ORACLES.read_text())
        self.assertEqual(data['data_role'],'fixture');self.assertEqual(len(data['cases']),11)
        self.assertIn('Step 6',data['hero_scope'])
        for f,h in data['source_pins'].items():self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h)

    def test_higher_precision_independent_check(self):
        for case in json.loads(ORACLES.read_text())['cases']:
            n=case['population_size']
            if not n:continue
            with localcontext() as ctx:
                ctx.prec=100;dn=Decimal(n)
                h=(dn*dn.ln()-sum(Decimal(c)*Decimal(c).ln() for c in case['counts'].values() if c))/dn
                self.assertLess(abs(h-Decimal(case['expected'][H])),Decimal('1e-76'))
                self.assertLess(abs(h.exp()-Decimal(case['expected'][E1])),Decimal('1e-75'))

    def test_effective_counts_differ(self):
        r=count_metrics({'A':3,'B':1},4).results
        self.close(r[H].value,math.log(4)-.75*math.log(3))
        self.close(r[E1].value,4/3**.75);self.assertEqual(r[E2].exact_ratio,(8,5))
        self.assertGreater(r[E1].value,r[E2].value);self.assertNotIn('N_eff',r)

    def test_one_class(self):
        for n in (1,4,50000):
            r=count_metrics({'A':n,'Z':0},n).results
            self.assertEqual([r[k].value for k in (S,H,C,E1,E2)],[1,0,1,1,1])
            self.assertEqual(math.copysign(1,r[H].value),1)
            self.assertTrue(all(r[k].result_status=='available' for k in (S,H,C,E1,E2)))

    def test_zero_registry_entries(self):
        one=count_metrics({'A':3,'B':1},4);two=count_metrics({'A':3,'B':1,'C':0,'D':0},4)
        self.assertEqual(values(one),values(two));self.assertEqual(two.exact_frequencies['C'],(0,4))

    def test_sci_with_replacement(self):
        r=count_metrics({'A':3,'B':1},4).results
        self.assertEqual(r[C].exact_ratio,(5,8));self.assertNotEqual(r[C].value,.5)
        self.assertNotIn('structural_pair_non_equivalence',r)

    def test_unrounded_derivation(self):
        r=count_metrics({'A':8,'B':6,'C':3,'D':2,'E':1},20).results
        self.assertEqual(r[E1].value,math.exp(r[H].value));self.assertEqual(r[E2].value,1/r[C].value)
        self.assertNotEqual(r[E1].value,math.exp(round(r[H].value,3)))
        self.assertNotEqual(r[E2].value,1/round(r[C].value,2))

    def test_units_and_scope(self):
        r=count_metrics({'A':3,'B':1},4,min_empirical_frequency='0.25')
        self.assertEqual(set(r.results),set(CORE_NAMES));self.assertEqual(r.results[H].unit,'nats')
        self.assertEqual(r.results[C].unit,'dimensionless')
        for x in r.results.values():
            self.assertEqual(x.metric_definition_version,'MET-0.2')
            self.assertEqual(x.uncertainty_status,'not_estimated');self.assertIsNone(x.uncertainty_method)
        self.assertFalse(r.independent_validation_performed)


class Thresholds(Checks):
    def test_source_thresholds(self):
        for case in json.loads(ORACLES.read_text())['threshold_cases']:
            r=count_metrics(case['counts'],sum(case['counts'].values()),min_empirical_frequency=case['threshold'])
            self.assertEqual(r.results[T].value,case['expected']);self.assertEqual(r.threshold.token,case['threshold'])

    def test_beyond_float_boundary(self):
        for token,wanted in [('0.25',2),('0.25000000000000000000000000000000001',1),('0.24999999999999999999999999999999999',2)]:
            self.assertEqual(count_metrics({'A':3,'B':1},4,min_empirical_frequency=token).results[T].value,wanted)

    def test_no_renormalization(self):
        r=count_metrics({'A':3,'B':1},4,min_empirical_frequency='0.8')
        self.assertEqual(r.results[T].value,0);self.assertEqual(r.results[T].result_status,'available')
        self.assertEqual(r.population_size,4);self.assertEqual(r.exact_frequencies['A'],(3,4));self.assertEqual(r.results[C].value,.625)

    def test_other_metrics_unchanged(self):
        base=count_metrics({'A':3,'B':1},4)
        for token in ('0.25','0.8',None,'bad'):
            out=count_metrics({'A':3,'B':1},4,min_empirical_frequency=token)
            for key in CORE_NAMES:
                if key!=T:self.assertEqual(base.results[key],out.results[key])

    def test_omitted_vs_null(self):
        omitted=count_metrics({'A':1},1);null=count_metrics({'A':1},1,min_empirical_frequency=None)
        self.assertFalse(omitted.threshold.requested);self.assertTrue(null.threshold.requested)
        self.assertEqual(omitted.results[T].result_status,'not_requested');self.assertEqual(null.results[T].result_status,'unavailable')
        self.assertIsNone(null.results[T].value)

    def test_empty_requested(self):
        r=count_metrics({'A':0},0,min_empirical_frequency='0.1')
        self.assertEqual(r.results[S].value,0);self.assertEqual(r.results[T].result_status,'undefined');self.assertIsNone(r.results[T].value)

    def test_invalid_values(self):
        for token in (True,False,0,-1,2,.25,None,{},[],'','0','NaN','Infinity','1/4',' 0.25','.25','1.1',Fraction(1,4),Decimal('.25')):
            with self.subTest(token=token):
                r=count_metrics({'A':3,'B':1},4,min_empirical_frequency=token)
                self.assertEqual(r.results[T].result_status,'unavailable');self.assertIsNone(r.results[T].value)
                self.assertEqual(r.results[S].value,2);self.assertIn('invalid_threshold',r.input_diagnostics)

    def test_invalid_empty(self):
        r=count_metrics({},0,min_empirical_frequency='0')
        self.assertEqual(r.results[T].result_status,'unavailable');self.assertEqual(r.results[H].result_status,'undefined')

    def test_lexemes_and_origins(self):
        for token,origin in [('0.10','decimal_string'),(ExactNumber('1.0E-1'),'json_number'),(ThresholdToken('0.100','json_number'),'json_number')]:
            r=count_metrics({'A':1,'B':9},10,min_empirical_frequency=token)
            self.assertEqual(r.results[T].value,2);self.assertEqual(r.threshold.representation,origin);self.assertEqual(r.threshold.exact_ratio,(1,10))
        raw=parse_json_bytes(b'{"threshold":0.10}')
        self.assertEqual(count_metrics({'A':1},1,min_empirical_frequency=raw['threshold']).threshold.token,'0.10')

    def test_revalidate_token_object(self):
        for token in (ThresholdToken('0','decimal_string'),ThresholdToken('0.2','invalid'),ThresholdToken('0.2',[]),ThresholdToken(None,'decimal_string')):
            self.assertEqual(count_metrics({'A':1},1,min_empirical_frequency=token).results[T].result_status,'unavailable')

    def test_zero_never_passes(self):
        self.assertEqual(count_metrics({'A':1,'B':0},1,min_empirical_frequency='1e-100').results[T].value,1)

    def test_large_negative_exponent(self):
        r=count_metrics({'A':1,'B':4,'C':0},5,min_empirical_frequency='1e-1000000000')
        self.assertEqual(r.results[T].value,2);self.assertEqual(r.threshold.coefficient,1)
        self.assertEqual(r.threshold.denominator_power10,1000000000);self.assertIsNone(r.threshold.exact_ratio)
        self.assertEqual(r.threshold.status,'available')

    def test_large_integer_equality(self):
        n=10**80
        self.assertEqual(count_metrics({'A':1,'B':n-1},n,min_empirical_frequency='1e-80').results[T].value,2)
        self.assertEqual(count_metrics({'A':1,'B':n-1},n,min_empirical_frequency='1.000000000000000001e-80').results[T].value,1)

    def test_one_threshold_spellings(self):
        for t in (1,'1.0000','10e-1','0.1e1'):
            self.assertEqual(count_metrics({'A':1},1,min_empirical_frequency=t).results[T].value,1)
            self.assertEqual(count_metrics({'A':1,'B':1},2,min_empirical_frequency=t).results[T].value,0)

    def test_token_limit(self):
        r=count_metrics({'A':1},1,min_empirical_frequency='0.'+'0'*1100+'1')
        self.assertEqual(r.results[T].result_status,'unavailable');self.assertEqual(r.results[C].value,1)


class Numerical(Checks):
    def test_invalid_counts(self):
        for table in ({'A':True},{'A':-1},{'A':.5},{'A':Fraction(1,1)},{'A':'1'},{'':1},{'secret\n':1},[],None):
            r=count_metrics(table,1)
            self.assertEqual(r.results[S].result_status,'unavailable');self.assertIsNone(r.results[S].value)
            self.assertIn('invalid_count_table',r.input_diagnostics)

    def test_exact_total(self):
        for n in (None,True,1.0,'1',-1):self.assertEqual(count_metrics({'A':1},n).results[S].result_status,'unavailable')
        r=count_metrics({'A':2},1);self.assertIn('count_conservation_failed',r.input_diagnostics);self.assertEqual(r.population_size,1)

    def test_resource_limits(self):
        r=count_metrics({'A':1<<4096},1<<4096);self.assertIn('arithmetic_resource_limit',r.input_diagnostics)
        self.assertIsNone(r.results[S].value)
        with patch.object(metrics,'MAX_CLASS_ENTRIES',1):r=count_metrics({'A':1,'B':1},2)
        self.assertIn('arithmetic_resource_limit',r.input_diagnostics)

    def test_underflow_preserves_exact_support(self):
        n=1<<4095;r=count_metrics({'A':1,'B':n-1},n,min_empirical_frequency='1e-1000000')
        self.assertEqual(r.results[S].value,2);self.assertEqual(r.results[T].value,2)
        for name in CORE_NAMES[2:]:
            self.assertEqual(r.results[name].result_status,'unavailable');self.assertIn('numerical_check_failed',r.results[name].reasons)

    def test_renaming_and_order(self):
        a=count_metrics({'A':11,'B':3,'C':1,'D':0},15,min_empirical_frequency='0.2')
        b=count_metrics({'zero':0,'z':1,'q':11,'r':3},15,min_empirical_frequency='0.2')
        self.assertEqual(values(a),values(b));self.assertEqual(a.exact_frequencies['A'],b.exact_frequencies['q'])

    def test_uniform_scaling(self):
        a=count_metrics({'A':3,'B':1},4,min_empirical_frequency='0.25');b=count_metrics({'A':300,'B':100},400,min_empirical_frequency='0.25')
        self.assertEqual(values(a),values(b));self.assertNotEqual(a.population_size,b.population_size)

    def test_624_small_tables(self):
        checked=0
        for counts in product(range(5),repeat=4):
            n=sum(counts)
            if not n:continue
            checked+=1;r=count_metrics(dict(zip('ABCD',counts)),n).results;s=sum(c>0 for c in counts)
            self.close(r[H].value,math.log(n)-sum(c*math.log(c) for c in counts if c)/n)
            self.assertEqual(Fraction(*r[C].exact_ratio),Fraction(sum(c*c for c in counts),n*n))
            self.assertGreaterEqual(r[H].value,0);self.assertLessEqual(r[H].value,math.log(s)+1e-12)
            self.assertLessEqual(1,r[E2].value);self.assertLessEqual(r[E2].value,r[E1].value+1e-10)
            self.assertLessEqual(r[E1].value,s+1e-10);self.assertLessEqual(s,n)
        self.assertEqual(checked,624)

    def test_tiny_boundary_record(self):
        r=metrics._bounded(H,-5e-13,0.0,math.log(2));self.assertEqual(r.value,0)
        self.assertEqual(r.corrections[0].original_value,-5e-13)
        self.assertEqual(r.corrections[0].reason,'within_tolerance_range_boundary')
        r=metrics._bounded(E1,3+1e-11,1,3);self.assertEqual(r.value,3);self.assertTrue(r.corrections)

    def test_signed_zero(self):
        r=metrics._bounded(H,-0.0,0.0,0.0);self.assertEqual(math.copysign(1,r.value),1)
        self.assertEqual(r.corrections[0].reason,'signed_negative_zero')
        self.assertEqual(math.copysign(1,r.corrections[0].original_value),-1)

    def test_material_errors(self):
        for v in (-1e-5,2.,float('nan'),float('inf'),-float('inf')):
            r=metrics._bounded(C,v,.5,1);self.assertEqual(r.result_status,'unavailable');self.assertIsNone(r.value);self.assertEqual(r.corrections,())

    def test_tolerance_sum(self):
        b=2.;a=1e-12+1e-10*b
        self.assertEqual(metrics._bounded(E1,b+a*.99,1,b).result_status,'available')
        self.assertEqual(metrics._bounded(E1,b+a*1.01,1,b).result_status,'unavailable')

    def test_exp_failure_scoped(self):
        with patch.object(metrics.math,'exp',return_value=float('inf')):r=count_metrics({'A':3,'B':1},4,min_empirical_frequency='0.25').results
        self.assertEqual(r[E1].result_status,'unavailable')
        for name in (S,T,H,C,E2):self.assertEqual(r[name].result_status,'available')

    def test_log_failure_scoped(self):
        with patch.object(metrics.math,'log',return_value=float('nan')):r=count_metrics({'A':3,'B':1},4).results
        self.assertEqual(r[H].result_status,'unavailable');self.assertEqual(r[E1].result_status,'unavailable')
        self.assertEqual(r[C].result_status,'available');self.assertEqual(r[S].value,2)

    def test_normalization_failure(self):
        with patch.object(metrics.math,'fsum',return_value=2.):r=count_metrics({'A':3,'B':1},4).results
        self.assertEqual(r[S].value,2)
        for name in CORE_NAMES[2:]:self.assertEqual(r[name].result_status,'unavailable')

    def test_effective_order_failure(self):
        with patch.object(metrics.math,'exp',return_value=1.1):r=count_metrics({'A':3,'B':1},4).results
        self.assertEqual(r[E1].result_status,'unavailable');self.assertEqual(r[E2].result_status,'unavailable');self.assertEqual(r[C].value,.625)

    def test_immutable_results(self):
        table={'A':3,'B':1};r=count_metrics(table,4);table['B']=9;self.assertEqual(r.class_counts['B'],1)
        with self.assertRaises(TypeError):r.results[S]='replace'

    def test_no_deferred_estimators(self):
        for name in ('gini_simpson_diversity','structural_half_life','external_recovery_rate','latent_support','expressible_support','bootstrap','compare','render_report','generate','execute','overall_score'):
            self.assertFalse(hasattr(metrics,name))
        self.assertEqual(len(CORE_NAMES),6)


class CellFixture(Checks):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
    def build(self,labels,validity=None,groups=()):
        self.path,self.obs,self.support,self.man=population_bundle(self.root,labels,validity=validity,group_sizes=groups)
        return self.get()
    def get(self):
        return build_populations(load_bundle(rewrite_evidence_bundle(self.root,self.obs,self.support,self.man))).cells[0]
    def row(self,kind,rid):return next(r for r in self.obs if r['record_type']==kind and r['record_id']==rid)


class Populations(CellFixture):
    def test_mf07_views_and_ratios(self):
        self.build([A,A,B,B,None,D],['valid','valid','invalid','undetermined','valid','valid'])
        self.row('assignment','a6')['assignment_review_status']='provisional';cell=self.get();r=cell_metrics(cell,min_empirical_frequency='0.30')
        a,v=r.distributions.values();self.assertEqual((a.population_size,v.population_size),(4,2))
        self.assertEqual((a.results[S].value,v.results[S].value),(2,1));self.assertEqual((a.results[T].value,v.results[T].value),(2,1))
        self.assertEqual((a.results[C].value,v.results[C].value),(.5,1));self.assertIs(r.source_cell,cell)
        expected={'classification_coverage':(4,6),'valid_fraction_selected':(4,6),'decisive_validity_coverage':(5,6),'classified_valid_coverage':(2,4),'classified_valid_fraction':(2,4)}
        for k,pair in expected.items():self.assertEqual((cell.ratios[k].numerator,cell.ratios[k].denominator),pair)

    def test_all_invalid(self):
        r=cell_metrics(self.build([A]*4,['invalid']*4),min_empirical_frequency='0.25');a,v=r.distributions.values()
        self.assertEqual(a.results[C].value,1);self.assertEqual(a.results[H].value,0);self.assertEqual(v.results[S].value,0)
        self.assertEqual(v.results[H].result_status,'undefined');self.assertEqual(v.results[T].result_status,'undefined')

    def test_unclassified(self):
        cell=self.build([None]*4);r=cell_metrics(cell).distributions['classified_all'].results
        self.assertEqual(r[S].value,0);self.assertIn('empty_classified_population',r[S].qualifiers)
        self.assertIsNone(r[H].value);self.assertEqual(cell.inventory.selected_count.value,4)

    def test_empty_selection(self):
        c=self.build([]);r=cell_metrics(c)
        self.assertEqual(c.inventory.selected_count.value,0);self.assertEqual(r.distributions['classified_all'].results[S].value,0)
        self.assertIn('empty_selected_inventory',r.distributions['classified_all'].results[S].qualifiers)
        self.assertTrue(all(x.status=='undefined' for x in c.ratios.values()))

    def test_frame_failure(self):
        self.build([A,A]);del self.man['frames'][0]['task_context'];c=self.get();r=cell_metrics(c,min_empirical_frequency='0.1')
        self.assertEqual(c.inventory.realization_count.value,2)
        for d in r.distributions.values():
            self.assertIsNone(d.population_size);self.assertTrue(all(m.result_status=='unavailable' for m in d.results.values()))

    def test_local_evidence_failure(self):
        self.build([A,A,B,B]);next(r for r in self.support if r['record_id']=='e-a4')['payload']['state']='withdrawn'
        c=self.get();r=cell_metrics(c).distributions['classified_all']
        self.assertEqual(r.population_size,3);self.assertEqual(r.results[C].exact_ratio,(5,9))
        self.assertEqual(c.inventory.selected_count.value,4);self.assertEqual(c.ratios['valid_fraction_selected'].value,1)

    def test_independence_only_withdrawal(self):
        c=self.build([A,A,B]);base=cell_metrics(c)
        self.support.append(support_record('correction','claim-change',effect='independence',target_refs=[record_ref('frame','frame1')],action='withdraw',stage='applied',reason=tagged('Mock withdrawal'),evidence_refs=[record_ref('evidence','e-a1')],reviewer_refs=[record_ref('role','reviewer')]))
        r=cell_metrics(self.get());self.assertEqual(values(base.distributions['classified_all']),values(r.distributions['classified_all']))
        self.assertFalse(r.independent_validation_performed)

    def test_unknown_checkpoint(self):
        self.build([A,A,B]);self.man['cells'][0]['checkpoint_identifier']=tagged(state='unknown');r=cell_metrics(self.get())
        self.assertEqual(r.distributions['classified_all'].results[C].exact_ratio,(5,9))
        self.assertEqual(r.source_cell.inventory.identity['checkpoint_identifier']['state'],'unknown')

    def test_malformed_threshold_is_component_specific(self):
        r=cell_metrics(self.build([A,A,B]),min_empirical_frequency='invalid');d=r.distributions['classified_all']
        self.assertEqual(d.results[T].result_status,'unavailable');self.assertEqual(d.results[C].value,5/9)
        self.assertEqual(r.source_cell.inventory.selected_count.value,3)

    def test_ambiguous_ids(self):
        self.build([A,A]);self.obs.append(copy.deepcopy(self.row('realization','s1')))
        r=cell_metrics(self.get()).distributions['classified_all'];self.assertEqual(r.results[S].result_status,'unavailable');self.assertIsNone(r.results[H].value)

    def test_population_duplicate_ids(self):
        p=self.build([A,A]).populations['classified_all'];r=population_metrics(replace(p,sample_ids=('s1','s1')))
        self.assertIn('population_identity_conflict',r.input_diagnostics);self.assertIsNone(r.results[S].value)

    def test_population_conservation(self):
        p=self.build([A,A]).populations['classified_all'];r=population_metrics(replace(p,class_counts={A:1}))
        self.assertIn('count_conservation_failed',r.input_diagnostics)

    def test_passive_arithmetic(self):
        c=self.build([A,A,B])
        with patch('builtins.open',side_effect=AssertionError('I/O')),patch('socket.socket',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):
            r=cell_metrics(c,ks=(1,3))
        self.assertEqual(r.distributions['classified_all'].results[S].value,2)

    def test_bad_component_types(self):
        for op in (lambda:population_metrics({}),lambda:prefix_metric({}),lambda:cell_metrics({}),lambda:cell_metrics(self.build([A]),prefix_mode=[])):
            with self.assertRaises(InputError):op()

    def test_no_hero_program_or_report_created(self):
        fixture_root = ROOT / 'examples/hero_hf00'
        before_files = {p.relative_to(fixture_root).as_posix(): p.read_bytes()
                        for p in fixture_root.rglob('*') if p.is_file()}
        r=cell_metrics(self.build(HERO,groups=(5,5,5,5)),ks=(5,10,20),prefix_mode='hero')
        self.assertEqual(r.distributions['classified_all'].results[C].exact_ratio,(57,200));self.assertFalse(r.independent_validation_performed)
        after_files = {p.relative_to(fixture_root).as_posix(): p.read_bytes()
                       for p in fixture_root.rglob('*') if p.is_file()}
        self.assertEqual(before_files, after_files)
        self.assertFalse(hasattr(r,'source_text_diagnostic'))


class Prefixes(CellFixture):
    def test_mf10(self):
        c=self.build([A,A,B,None,D,B],['valid','valid','invalid','valid','valid','valid'],groups=(3,3));r=cell_metrics(c,ks=(2,4,6,7))
        self.assertEqual([x.result.value for x in r.prefixes],[1,1,2,1,3,3,None,None])
        self.assertEqual([x.source_prefix.counted_samples for x in r.prefixes],[2,2,3,2,5,4,None,None])
        self.assertEqual(r.prefixes[3].source_prefix.selected_sample_ids,('s1','s2','s3','s4'));self.assertEqual(r.prefixes[3].source_prefix.counted_sample_ids,('s1','s2'))

    def test_storage_order_invariant(self):
        c=self.build([A,A,B,None,D,B],['valid','valid','invalid','valid','valid','valid']);old=cell_metrics(c,ks=(2,4,6))
        self.obs.reverse();self.support.reverse();new=cell_metrics(self.get(),ks=(2,4,6))
        self.assertEqual([x.result for x in old.prefixes],[x.result for x in new.prefixes])
        for name in old.distributions:self.assertEqual(values(old.distributions[name]),values(new.distributions[name]))

    def test_real_order_change(self):
        old=cell_metrics(self.build([A,A,B]),ks=(2,));self.man['analysis_config']['selection'][0]['sample_order']=tagged(['s3','s1','s2'])
        for i,s in enumerate(('s3','s1','s2'),1):self.row('realization',s)['sample_order']=tagged(i)
        new=cell_metrics(self.get(),ks=(2,));self.assertEqual((old.prefixes[0].result.value,new.prefixes[0].result.value),(1,2))
        self.assertEqual(values(old.distributions['classified_all']),values(new.distributions['classified_all']))

    def test_missing_order(self):
        self.build([A,A,B]);self.man['analysis_config']['selection'][0]['sample_order']=tagged(state='unknown')
        for r in self.obs:
            if r['record_type']=='realization':r['sample_order']=tagged(state='unknown')
        out=cell_metrics(self.get(),ks=(2,));self.assertEqual(out.distributions['classified_all'].results[S].value,2)
        self.assertEqual(out.prefixes[0].result.result_status,'unavailable');self.assertIn('missing_sample_order',out.prefixes[0].result.reasons)

    def test_zero_vs_missing_prefix(self):
        r=cell_metrics(self.build([None]*3),ks=(3,4));self.assertEqual(r.prefixes[0].result.value,0)
        self.assertEqual(r.prefixes[0].result.result_status,'available');self.assertIn('empty_classified_prefix',r.prefixes[0].result.qualifiers)
        self.assertEqual(r.prefixes[2].result.result_status,'unavailable')

    def test_partial_group(self):
        r=cell_metrics(self.build([A,A,B,D],groups=(4,)),ks=(2,)).prefixes[0]
        self.assertEqual(r.source_prefix.partial_group_ids,('G1',));self.assertIsNone(r.source_prefix.independent_draw_count)
        self.assertEqual(r.result.unit,'classes_among_k_realization_prefix')

    def test_k_states(self):
        c=self.build([A,A]);self.assertEqual(prefix_metric(prefix(c,None)).result.result_status,'not_requested')
        for ks in ([0],[True],[2,1],[1,1],None):
            with self.assertRaises(InputError):cell_metrics(c,ks=ks)
        self.assertEqual(cell_metrics(c).prefixes,())

    def test_monotone_accumulation(self):
        out=cell_metrics(self.build([A,None,B,D,A],groups=(5,)),ks=(1,2,3,4,5))
        for offset in (0,1):
            vals=[x.result.value for x in out.prefixes[offset::2]];self.assertEqual(vals,sorted(vals))

    def test_prefix_conservation(self):
        p=prefix(self.build([A,A,B]),3);r=prefix_metric(replace(p,distinct_count=99))
        self.assertEqual(r.result.result_status,'unavailable');self.assertIn('prefix_conservation_failed',r.result.reasons)

    def test_hero_count_projection(self):
        r=cell_metrics(self.build(HERO,groups=(5,5,5,5)),min_empirical_frequency='0.10',ks=(5,10,20),prefix_mode='hero')
        self.assertEqual([x.result.value for x in r.prefixes],[4,4,5,5,5,5])
        for d in r.distributions.values():self.assertEqual(d.results[T].value,4);self.assertEqual(d.results[E2].exact_ratio,(200,57))

    def test_hero_invalid_projection(self):
        v=['valid']*20;v[9]='invalid';r=cell_metrics(self.build(HERO,v,groups=(5,5,5,5)),ks=(5,10,20),prefix_mode='hero')
        self.assertEqual([x.result.value for x in r.prefixes],[4,4,5,4,5,4]);a,v=r.distributions.values()
        self.assertEqual((a.population_size,v.population_size),(20,19));self.assertEqual(v.results[C].exact_ratio,(113,361))

    def test_hero_missing_intended_slot(self):
        self.build(HERO,groups=(5,5,5,5));self.obs[:]=[r for r in self.obs if not(r['record_type']=='realization' and r['record_id']=='s10')]
        sel=self.man['analysis_config']['selection'][0]
        for f in ('sample_order','selected_sample_ids'):sel[f]=tagged([s for s in sel[f]['value'] if s!='s10'])
        c=self.get();r=cell_metrics(c,ks=(5,10,20),prefix_mode='hero')
        self.assertEqual(r.distributions['classified_all'].results[C].exact_ratio,(113,361));self.assertEqual(r.prefixes[0].result.value,4)
        self.assertEqual(r.prefixes[2].result.result_status,'unavailable');self.assertEqual(r.prefixes[4].result.result_status,'unavailable')
        self.assertEqual(cell_metrics(c,ks=(10,)).prefixes[0].result.result_status,'available')

    def test_revision_preserves_old_result(self):
        old=cell_metrics(self.build([A,A,B,B]));next(r for r in self.support if r['record_id']=='e-a4')['payload']['state']='withdrawn'
        pending=cell_metrics(self.get());new=copy.deepcopy(self.row('assignment','a4'))
        new.update(record_id='a4-revised',assignment_id='a4-revised',assignment_version='0.2',structural_class_id=A,supersedes_assignment_id=tagged('a4'))
        new['evidence_refs']=[record_ref('evidence','e-a4-revised')]
        e=copy.deepcopy(next(r for r in self.support if r['record_id']=='e-a4'));e['record_id']='e-a4-revised'
        e['payload'].update(state='active',assertion=tagged(A),target_ref=record_ref('assignment','a4-revised'))
        self.obs.append(new);self.support.append(e)
        next(p for p in self.man['analysis_config']['assignment_pins'] if p['sample_id']=='s4').update(assignment_id='a4-revised',assignment_version='0.2')
        revised=cell_metrics(self.get());self.assertEqual(self.row('assignment','a4')['structural_class_id'],B)
        self.assertEqual([x.distributions['classified_all'].results[C].exact_ratio for x in (old,pending,revised)],[(1,2),(5,9),(5,8)])
        for x in (old,pending,revised):self.assertEqual(x.source_cell.inventory.selected_count.value,4)
        self.assertEqual(old.distributions['classified_all'].class_counts[B],2)


