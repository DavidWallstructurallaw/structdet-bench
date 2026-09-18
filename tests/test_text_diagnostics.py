"""Step 3 exact text oracles and passive accepted-population diagnostics.

All examples are stipulated. No actual model, annotation or program execution.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from collections import Counter
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import text_diagnostics as td
from structdet_bench.contracts import InputError, freeze
from structdet_bench.local_io import load_bundle
from structdet_bench.populations import build_populations
from structdet_bench.metrics import cell_metrics
from tests import phase2_helpers as helper
from tests.helpers import ROOT, tagged, artifact_record, record_ref, rewrite_evidence_bundle

METHOD = td.TextMethod('fixture-original-region-v1')
ORACLE = ROOT/'tests/fixtures/text_oracles.json'


def token(data, **kwargs):
    return td.tokenize_text(data.encode('utf-8') if isinstance(data, str) else data, METHOD, **kwargs)


def text_fixture(root: Path, texts, labels=None, *, validity=None, group_sizes=()):
    """Stipulated component texts. Missing bytes never become an empty file.

    No candidate program is run. Every actual occurrence keeps its own sample
    identity and deterministic class, even when byte snapshots repeat.
    """
    from tests.helpers import population_bundle, artifact_record, tagged, record_ref, rewrite_evidence_bundle
    texts = list(texts)
    labels = list(labels) if labels is not None else ["SORT-ADJ"] * len(texts)
    path, observations, support, manifest = population_bundle(root, labels, validity=validity, group_sizes=group_sizes)
    by_id = {r["record_id"]: r for r in observations}
    for number, content in enumerate(texts, 1):
        sample = by_id[f"s{number}"]
        sample["extraction_rule_version"] = tagged("fixture-original-region-v1")
        if content is None:
            sample["output_ref"] = tagged(state="unavailable", reason="Stipulated missing text")
            continue
        data = content.encode("utf-8") if isinstance(content, str) else content
        identity, filename = f"text{number}", f"text{number}.txt"
        (root / filename).write_bytes(data)
        artifact = artifact_record(identity, filename)
        artifact["expected_sha256"] = tagged(hashlib.sha256(data).hexdigest())
        observations.append(artifact)
        sample["output_ref"] = tagged(record_ref("artifact", identity))
        sample["output_content_hash"] = tagged(hashlib.sha256(data).hexdigest())
    return rewrite_evidence_bundle(root, observations, support, manifest), observations, support, manifest


class TokenizerTests(unittest.TestCase):
    def test_all_literal_token_and_trigram_oracles(self):
        for case in json.loads(ORACLE.read_text())['token_cases']:
            with self.subTest(case=case['id']):
                t=token(case['text'])
                self.assertEqual(t.units,tuple(case['units']))
                self.assertEqual(t.trigrams,frozenset(tuple(tuple(u) for u in g) for g in case['trigrams']))
                self.assertEqual(t.lexical_unit_count,len(case['units']))
                self.assertEqual(t.normalized_sha256,hashlib.sha256(case['normalized'].encode()).hexdigest())
                self.assertEqual(t.status,'eligible' if case['units'] else 'ineligible')
    def test_oracle_source_pins_match_frozen_documents(self):
        for path,sha in json.loads(ORACLE.read_text())['source_pins'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha)
    def test_white_space_table_and_encoding_digest(self):
        case=json.loads(ORACLE.read_text())
        self.assertEqual(td.WHITE_SPACE_RANGES,tuple(map(tuple,case['white_space_ranges'])))
        self.assertEqual(sum(b-a+1 for a,b in td.WHITE_SPACE_RANGES),25)
        self.assertEqual(td.WHITE_SPACE_SHA256,case['white_space_sha256'])
        self.assertEqual(td.CATEGORY_VERSION,'15.1.0')
    def test_all_25_white_space_codepoints_split_units(self):
        for lo,hi in td.WHITE_SPACE_RANGES:
            for codepoint in range(lo,hi+1):
                with self.subTest(codepoint=codepoint):
                    self.assertEqual(token('a'+chr(codepoint)+'b').units,('a','b'))
    def test_host_isspace_extra_controls_are_retained(self):
        for cp in range(28,32):
            self.assertTrue(chr(cp).isspace())
            self.assertEqual(token('a'+chr(cp)+'b').units,('a',chr(cp),'b'))
    def test_empty_and_whitespace_are_distinct(self):
        self.assertEqual(token('').reasons,('empty_emitted_text',))
        self.assertEqual(token(' \r\n\t').reasons,('whitespace_only_text',))
    def test_one_unit_has_exact_boundary_trigram(self):
        self.assertEqual(token('x').trigrams,frozenset({(('boundary','begin'),('text','x'),('boundary','end'))}))
    def test_boundary_spelling_never_collides(self):
        t=token('begin end boundary BEGIN END')
        lexical={u for g in t.trigrams for u in g if u[0]=='text'}
        self.assertNotIn(td.BEGIN,lexical);self.assertNotIn(td.END,lexical)
        self.assertIn(('text','begin'),lexical)
    def test_original_and_normalized_hashes_differ_only_where_expected(self):
        a=token('a\r\nb\rc');b=token('a\nb\nc')
        self.assertNotEqual(a.original_sha256,b.original_sha256)
        self.assertEqual(a.normalized_sha256,b.normalized_sha256)
        self.assertEqual(a.trigram_sha256,b.trigram_sha256)
    def test_case_and_comments_are_not_removed(self):
        self.assertNotEqual(token('a b c').trigrams,token('A b c').trigrams)
        self.assertIn('#',token('a b c #comment').units)
        self.assertIn('comment',token('a b c #comment').units)
    def test_combining_marks_do_not_join_word_runs(self):
        self.assertEqual(token('e\u0301_2').units,('e','\u0301','_2'))
        self.assertNotEqual(token('e\u0301').trigram_sha256,token('é').trigram_sha256)
    def test_numbers_identifiers_and_punctuation(self):
        self.assertEqual(token('_x12² 1.2 !=').units,('_x12²','1','.','2','!','='))
    def test_repeated_trigrams_are_sets_not_bags(self):
        a=token('a a a a');b=token('a a a a a a')
        self.assertEqual(a.trigrams,b.trigrams);self.assertEqual(len(a.trigrams),3)
        self.assertNotEqual(a.lexical_unit_count,b.lexical_unit_count)
    def test_utf8_failure_is_not_empty_or_replacement_text(self):
        for data in (b'\xff',b'\xed\xa0\x80',b'\xe2\x82'):
            t=token(data);self.assertEqual(t.status,'ineligible')
            self.assertEqual(t.reasons,('invalid_utf8',));self.assertIsNone(t.normalized_sha256)
    def test_feff_and_zero_width_characters_not_stripped(self):
        self.assertEqual(token('\ufeffa\u200b').units,('\ufeff','a','\u200b'))
    def test_registered_category_version_mismatch_withheld(self):
        t=td.tokenize_text(b'a',replace(METHOD,unicode_category_version='16.0.0'))
        self.assertEqual(t.status,'unavailable');self.assertIn('unicode_category_version_mismatch',t.reasons)
    def test_host_category_version_mismatch_withheld(self):
        with patch.object(td.unicodedata,'unidata_version','0.0.0'):
            t=token('a')
        self.assertIn('host_unicode_category_version_mismatch',t.reasons);self.assertEqual(t.units,())
    def test_white_space_version_and_digest_mismatch_withheld(self):
        for fields,reason in [({'white_space_version':'0.0.0'},'white_space_version_mismatch'),
                              ({'white_space_sha256':'0'*64},'white_space_identity_mismatch')]:
            t=td.tokenize_text(b'a',replace(METHOD,**fields));self.assertIn(reason,t.reasons)
    def test_encoding_and_proxy_are_not_guessed(self):
        for fields,reason in [({'encoding':'latin-1'},'unsupported_text_encoding'),
                              ({'proxy_version':'different'},'unsupported_proxy_version')]:
            self.assertIn(reason,td.tokenize_text(b'a',replace(METHOD,**fields)).reasons)
    def test_method_record_round_trip_and_unknown_fields(self):
        r={k:v if k in ('encoding','proxy_version') else tagged(v) for k,v in METHOD.identity.items()}
        self.assertEqual(td.method_from_record(r),METHOD)
        r['unicode_category_version']=tagged(state='unknown')
        with self.assertRaises(InputError):td.method_from_record(r)
        r['execute']='no'
        with self.assertRaises(InputError):td.method_from_record(r)
    def test_component_types_are_explicit(self):
        for data in ('a',None,bytearray(b'a'),False):
            with self.assertRaises(InputError):td.tokenize_text(data,METHOD)
        with self.assertRaises(InputError):td.tokenize_text(b'a',{})
        with self.assertRaises(InputError):td.TextMethod('')
        with self.assertRaises(InputError):td.TextMethod('x',white_space_version=False)
    def test_token_limit_is_inclusive_and_never_returns_truncation(self):
        limit=td.DiagnosticLimits(max_lexical_units=3)
        self.assertEqual(token('a b c',limits=limit).status,'eligible')
        t=token('a b c d',limits=limit)
        self.assertTrue(t.resource_failure);self.assertEqual(t.status,'unavailable')
        self.assertEqual(t.units,());self.assertIsNone(t.lexical_unit_count)
        self.assertGreater(t.observed_lexical_units,3)
    def test_single_large_identifier_remains_one_unit(self):
        self.assertEqual(token('a'*20000,limits=td.DiagnosticLimits(max_lexical_units=1)).lexical_unit_count,1)
    def test_invalid_limits_do_not_become_defaults(self):
        for value in (False,0,-1,1.2,'1',None,2**31):
            with self.assertRaises(InputError):td.DiagnosticLimits(max_pairs=value)
        for value in (False,{},1):
            with self.assertRaises(InputError):token('a',limits=value)
        with self.assertRaises(InputError):td.limits_from_record({})
    def test_sensitive_tokens_not_in_default_repr(self):
        t=token('PRIVATE_TOKEN # secret')
        self.assertNotIn('PRIVATE_TOKEN',repr(t));self.assertNotIn('secret',repr(t))
        self.assertIn('surface_lexical_unit',repr(t))


class TextFixture(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
    def build(self,texts,labels=None,**kw):
        self.p,self.obs,self.sup,self.man=text_fixture(self.root,texts,labels,**kw)
        return self.context()
    def context(self):
        self.p=rewrite_evidence_bundle(self.root,self.obs,self.sup,self.man)
        b=load_bundle(self.p);c=build_populations(b).cells[0]
        return b,c
    def diag(self,b,c,view='classified_all',**kw):
        return td.diagnose_population(b,c,view,METHOD,**kw)
    def row(self,kind,rid):return next(x for x in self.obs if x['record_type']==kind and x['record_id']==rid)


class PairTests(TextFixture):
    def test_literal_pair_oracles_and_weighted_mean(self):
        for case in json.loads(ORACLE.read_text())['pair_cases']:
            with TemporaryDirectory() as temp:
                p,*_=text_fixture(Path(temp),case['texts'],case['labels'])
                b=load_bundle(p);d=self.diag(b,build_populations(b).cells[0])
                for name,key in ((td.SURFACE,'surface'),(td.WITHIN,'within'),(td.STRUCTURAL,'structural')):
                    self.assertEqual(d.results[name].exact_ratio,tuple(case[key]))
                if case['id']=='MF-11':
                    self.assertEqual((d.pairs[0].intersection_size,d.pairs[0].union_size),(1,5))
                else:self.assertNotEqual(d.results[td.WITHIN].exact_ratio,tuple(case['equal_class_average']))
    def test_mf12_finite_pair_correction_uses_same_subset(self):
        b,c=self.build(['a b c','a b d','a x c','q r s'],['SORT-ADJ']*3+['SORT-INS'])
        d=self.diag(b,c);self.assertEqual(d.pair_count,6)
        self.assertEqual(d.results[td.STRUCTURAL].exact_ratio,(1,2));self.assertEqual(d.text_sci_ratio,(5,8))
        self.assertEqual(Fraction(*d.results[td.STRUCTURAL].exact_ratio),Fraction(4,3)*(1-Fraction(*d.text_sci_ratio)))
        self.assertNotEqual(Fraction(1,2),1-Fraction(*d.text_sci_ratio))
    def test_mf13_all_singletons_has_undefined_within(self):
        b,c=self.build(['a b c','a b d'],['SORT-ADJ','SORT-INS']);d=self.diag(b,c)
        self.assertEqual(d.results[td.WITHIN].result_status,'undefined')
        self.assertEqual(d.results[td.STRUCTURAL].exact_ratio,(1,1))
        self.assertTrue(all(x.mean.result_status=='undefined' for x in d.class_diagnostics))
    def test_mf13_one_text_has_three_undefined_pair_means(self):
        b,c=self.build(['a b c']);d=self.diag(b,c)
        self.assertEqual(d.pair_count,0)
        self.assertTrue(all(x.result_status=='undefined' for x in d.results.values()))
    def test_mf14_keeps_original_n_and_matched_pair_ids(self):
        b,c=self.build(['a b c','a b d',None,None],['SORT-ADJ','SORT-INS','SORT-INS','SORT-INS'])
        d=self.diag(b,c);self.assertEqual((d.population_size,d.eligible_count,d.pair_count),(4,2,1))
        self.assertEqual(d.proxy_text_coverage.value,Fraction(1,2))
        self.assertEqual(d.results[td.STRUCTURAL].exact_ratio,(1,1))
        self.assertEqual(d.results[td.SURFACE].exact_ratio,(4,5))
        self.assertEqual(c.populations['classified_all'].count,4)
        self.assertEqual(d.eligible_sample_ids,('s1','s2'))
    def test_known_empty_population_retains_undefined_coverage(self):
        b,c=self.build([]);d=self.diag(b,c)
        self.assertEqual(d.population_size,0);self.assertEqual(d.eligible_count,0)
        self.assertEqual(d.proxy_text_coverage.status,'undefined');self.assertEqual(d.status,'available')
    def test_all_missing_is_not_empty_population(self):
        b,c=self.build([None,None]);d=self.diag(b,c)
        self.assertEqual(d.population_size,2);self.assertEqual(d.eligible_count,0)
        self.assertEqual(d.proxy_text_coverage.value,0)
        self.assertTrue(all(x.result_status=='undefined' for x in d.results.values()))
    def test_class_with_missing_text_is_not_hidden(self):
        b,c=self.build(['a b c',None,None],['SORT-ADJ','SORT-INS','SORT-INS']);d=self.diag(b,c)
        classes={x.class_id:x for x in d.class_diagnostics}
        self.assertEqual(classes['SORT-INS'].population_count,2)
        self.assertEqual(classes['SORT-INS'].eligible_sample_ids,());self.assertIsNone(classes['SORT-INS'].mean.value)
    def test_all_and_valid_views_keep_separate_denominators(self):
        b,c=self.build(['a b c','a b d','q r s'],['SORT-ADJ','SORT-ADJ','SORT-INS'],validity=['valid','invalid','valid'])
        a=self.diag(b,c);v=self.diag(b,c,'classified_valid')
        self.assertEqual((a.population_size,v.population_size),(3,2));self.assertEqual((a.pair_count,v.pair_count),(3,1))
        self.assertEqual(a.results[td.STRUCTURAL].exact_ratio,(2,3));self.assertEqual(v.results[td.STRUCTURAL].exact_ratio,(1,1))
    def test_unresolved_and_provisional_labels_never_tokenized(self):
        b,c=self.build(['a b c','q r s','q r t'],['SORT-ADJ',None,'SORT-INS'])
        self.row('assignment','a3')['assignment_review_status']='provisional';b,c=self.context();d=self.diag(b,c)
        self.assertEqual(d.population_sample_ids,('s1',));self.assertEqual(len(d.samples),1)
    def test_duplicate_content_preserves_observation_multiplicity(self):
        b,c=self.build(['a b c']*4,group_sizes=(4,));d=self.diag(b,c)
        self.assertEqual(d.pair_count,6);self.assertEqual(len(d.pairs),6)
        self.assertEqual(d.results[td.SURFACE].exact_ratio,(0,1))
        self.assertEqual(d.dependency_counts['same_call'],6);self.assertIsNone(d.independent_draw_count)
        self.assertEqual(d.work['unique_snapshot_tokenizations'],1)
    def test_distinct_calls_are_not_independent_draw_claim(self):
        b,c=self.build(['a b c','a b d'],group_sizes=(1,1));d=self.diag(b,c)
        self.assertEqual(d.dependency_counts['distinct_recorded_calls'],1);self.assertIsNone(d.independent_draw_count)
    def test_unknown_group_is_explicit(self):
        b,c=self.build(['a b c','a b d']);d=self.diag(b,c)
        self.assertEqual(d.dependency_counts['unknown_call_relation'],1)
        self.assertIsNone(d.pairs[0].same_call)
    def test_input_storage_order_does_not_change_diagnostics(self):
        b,c=self.build(['a b c','a b d','q r s'],['SORT-ADJ','SORT-ADJ','SORT-INS']);before=self.diag(b,c)
        self.obs.reverse();self.sup.reverse();b,c=self.context();after=self.diag(b,c)
        self.assertEqual(before.results,after.results);self.assertEqual(before.pairs,after.pairs)
        self.assertEqual(before.samples,after.samples)
    def test_class_renaming_preserves_distance_and_Q(self):
        b,c=self.build(['a b c','a b d','q r s'],['SORT-ADJ','SORT-ADJ','SORT-INS']);before=self.diag(b,c)
        for r in self.obs:
            if r['record_type']=='assignment':r['structural_class_id']={'SORT-ADJ':'SORT-MERGE','SORT-INS':'SORT-PIVOT'}[r['structural_class_id']]
        for r in self.sup:
            if r['record_id'].startswith('e-a'):r['payload']['assertion']=tagged({'SORT-ADJ':'SORT-MERGE','SORT-INS':'SORT-PIVOT'}[r['payload']['assertion']['value']])
        b,c=self.context();after=self.diag(b,c)
        self.assertEqual(before.results,after.results)
    def test_small_pair_tables_match_independent_direct_enumeration(self):
        texts=['a b c','a b d','q r s'];grams=[{('BEGIN','a','b'),('a','b','c'),('b','c','END')},
            {('BEGIN','a','b'),('a','b','d'),('b','d','END')},{('BEGIN','q','r'),('q','r','s'),('r','s','END')}]
        for labels in product(('SORT-ADJ','SORT-INS'),repeat=3):
            b,c=self.build(texts,labels);d=self.diag(b,c)
            ds=[Fraction(len(grams[i]|grams[j])-len(grams[i]&grams[j]),len(grams[i]|grams[j])) for i,j in combinations(range(3),2)]
            self.assertEqual(d.results[td.SURFACE].exact_ratio,(sum(ds)/3).as_integer_ratio())
            q=Fraction(sum(labels[i]!=labels[j] for i,j in combinations(range(3),2)),3)
            self.assertEqual(d.results[td.STRUCTURAL].exact_ratio,q.as_integer_ratio())
    def test_invalid_population_identity_and_count_are_not_empty_results(self):
        b,c=self.build(['a b c','a b d']);p=c.populations['classified_all']
        for broken in (replace(p,sample_ids=('s1','s1')),replace(p,class_counts={'SORT-ADJ':9})):
            modified=replace(c,populations=freeze({**c.populations,'classified_all':broken}))
            d=self.diag(b,modified);self.assertEqual(d.status,'unavailable')
            self.assertTrue(all(x.result_status=='unavailable' for x in d.results.values()))
    def test_frame_failure_does_not_manufacture_zero_pairs(self):
        self.build(['a b c']);del self.man['frames'][0]['task_context'];b,c=self.context();d=self.diag(b,c)
        self.assertIsNone(d.eligible_count);self.assertIsNone(d.pair_count)
        self.assertEqual(d.results[td.SURFACE].result_status,'unavailable')
    def test_revised_label_changes_pairs_not_original_samples(self):
        b,c=self.build(['a b c','a b d','q r s']);a=self.diag(b,c)
        self.row('assignment','a3')['structural_class_id']='SORT-INS'
        next(r for r in self.sup if r['record_id']=='e-a3')['payload']['assertion']=tagged('SORT-INS')
        b,c=self.context();bresult=self.diag(b,c)
        self.assertEqual(a.population_sample_ids,bresult.population_sample_ids)
        self.assertEqual(a.results[td.SURFACE],bresult.results[td.SURFACE])
        self.assertNotEqual(a.results[td.STRUCTURAL],bresult.results[td.STRUCTURAL])
        self.assertEqual(a.results[td.STRUCTURAL].exact_ratio,(0,1))


class SnapshotTests(TextFixture):
    def test_snapshot_content_not_live_file(self):
        b,c=self.build(['a b c','a b d']);old=self.diag(b,c)
        (self.root/'text1.txt').write_text('other data')
        self.assertEqual(old.results,self.diag(b,c).results)
    def test_original_hash_normalized_hash_and_trigram_identity_retained(self):
        b,c=self.build(['a\r\nb\rc','a\nb\nc']);d=self.diag(b,c);a,b=d.samples
        self.assertNotEqual(a.original_sha256,b.original_sha256)
        self.assertEqual(a.normalized_sha256,b.normalized_sha256);self.assertEqual(a.trigram_sha256,b.trigram_sha256)
        self.assertEqual(a.artifact_ref,('artifact','text1','0.1'))
    def test_empty_whitespace_inaccessible_decode_failures_stay_separate(self):
        b,c=self.build([b'',b' \t',None,b'\xff']);d=self.diag(b,c)
        self.assertEqual([s.reasons for s in d.samples],[('empty_emitted_text',),('whitespace_only_text',),('output_ref_unavailable',),('invalid_utf8',)])
        self.assertEqual(d.population_size,4);self.assertEqual(d.proxy_text_coverage.value,0)
    def test_extraction_version_unknown_or_mismatched_is_excluded(self):
        self.build(['a b c','a b d'])
        self.row('realization','s1')['extraction_rule_version']=tagged(state='unknown')
        self.row('realization','s2')['extraction_rule_version']=tagged('other')
        b,c=self.context();d=self.diag(b,c)
        self.assertEqual(d.population_size,2);self.assertEqual(d.eligible_count,0)
        self.assertTrue(all('extraction_version_mismatch_or_unknown' in s.reasons for s in d.samples))
    def test_declared_byte_span_verified_without_extracting_or_repair(self):
        self.build(['a b c','a b d'])
        raw=b'HEADER\r\n```python\r\na b c\r\n```'
        (self.root/'raw.txt').write_bytes(raw);self.obs.append(artifact_record('raw1','raw.txt'))
        s=self.row('realization','s1');start=raw.index(b'a b c')
        s['raw_response_ref']=tagged(record_ref('artifact','raw1'))
        s['extensions']={'extraction_span':{'byte_start':start,'byte_end':start+5}}
        b,c=self.context();d=self.diag(b,c)
        self.assertEqual(d.samples[0].span_status,'bytes_match');self.assertEqual(d.samples[0].original_bytes,5)
    def test_unverified_declared_region_does_not_pick_new_fence(self):
        self.build(['a b c','a b d'])
        self.row('realization','s1')['extensions']={'extraction_span':{'byte_start':0,'byte_end':5}}
        b,c=self.context();d=self.diag(b,c)
        self.assertEqual(d.population_size,2);self.assertEqual(d.eligible_count,1)
        self.assertIn('declared_extraction_span_unverified',d.samples[0].reasons)
    def test_truncated_identified_text_remains_truncated_and_eligible(self):
        self.build(['a b c','a b d']);self.row('realization','s1')['completion_status']='truncated'
        b,c=self.context();d=self.diag(b,c)
        self.assertEqual(d.samples[0].completion_status,'truncated');self.assertEqual(d.samples[0].status,'eligible')
    def test_no_fence_search_on_registered_body(self):
        body='```python\na b c\n```\n```python\nx y z\n```'
        b,c=self.build([body]);d=self.diag(b,c)
        self.assertEqual(d.samples[0].original_sha256,hashlib.sha256(body.encode()).hexdigest())
        self.assertEqual(d.samples[0].lexical_unit_count,20)
    def test_missing_output_does_not_fall_back_to_raw(self):
        self.build([None,'a b d']);self.obs.append(artifact_record('raw','raw.txt'));(self.root/'raw.txt').write_bytes(b'a b c')
        self.row('realization','s1')['raw_response_ref']=tagged(record_ref('artifact','raw'))
        b,c=self.context();d=self.diag(b,c);self.assertEqual(d.eligible_count,1)
        self.assertIn('output_ref_unavailable',d.samples[0].reasons)
    def test_same_source_text_under_different_ids_is_not_deduplicated(self):
        b,c=self.build(['a b c','a b c']);d=self.diag(b,c)
        self.assertEqual(d.eligible_sample_ids,('s1','s2'));self.assertEqual(d.pair_count,1)
        self.assertEqual(d.results[td.SURFACE].value,0)
    def test_held_snapshot_tampering_is_not_rehashed_into_acceptance(self):
        b,c=self.build(['a b c','a b d']);snaps=dict(b.snapshots)
        snap=snaps['text1.txt'];snaps['text1.txt']=replace(snap,content=b'other')
        d=self.diag(replace(b,snapshots=freeze(snaps)),c)
        self.assertIn('snapshot_identity_conflict',d.samples[0].reasons);self.assertEqual(d.eligible_count,1)
    def test_text_absence_does_not_modify_M_arithmetic(self):
        b,c=self.build(['a b c',None]);before=cell_metrics(c)
        self.diag(b,c);after=cell_metrics(c)
        self.assertEqual(before,after);self.assertEqual(c.populations['classified_all'].count,2)


class ResourceTests(TextFixture):
    def test_pair_limit_preflight_is_inclusive(self):
        b,c=self.build(['a b c']*3)
        self.assertEqual(self.diag(b,c,limits=td.DiagnosticLimits(max_pairs=3)).results[td.SURFACE].value,0)
        d=self.diag(b,c,limits=td.DiagnosticLimits(max_pairs=2))
        self.assertEqual(d.pair_count,3);self.assertEqual(d.work['enumerated_pairs'],0)
        self.assertTrue(all(x.result_status=='unavailable' for x in d.results.values()))
        self.assertEqual(d.proxy_text_coverage.value,1)
    def test_long_text_failure_never_drops_expensive_sample(self):
        b,c=self.build(['a b c','a b c d','a b d'])
        d=self.diag(b,c,limits=td.DiagnosticLimits(max_lexical_units=3))
        self.assertEqual(d.population_size,3);self.assertIsNone(d.eligible_count)
        self.assertEqual(d.proxy_text_coverage.status,'unavailable');self.assertIsNone(d.pair_count)
        self.assertTrue(d.samples[1].resource_failure)
        self.assertTrue(all(x.result_status=='unavailable' for x in d.results.values()))
    def test_visit_limit_preflight_keeps_original_membership(self):
        b,c=self.build(['a b c','a b d']);d=self.diag(b,c,limits=td.DiagnosticLimits(max_trigram_visits=5))
        self.assertEqual(d.eligible_count,2);self.assertEqual(d.work['required_trigram_visits'],6)
        self.assertEqual(d.work['visits_this_diagnostic'],0)
        self.assertEqual(d.results[td.SURFACE].result_status,'unavailable')
        self.assertEqual(d.results[td.STRUCTURAL].exact_ratio,(0,1))
    def test_cumulative_budget_is_shared_between_views(self):
        b,c=self.build(['a b c','a b d']);limit=td.DiagnosticLimits(max_trigram_visits=6);work=td.WorkBudget(6)
        first=self.diag(b,c,limits=limit,work=work);second=self.diag(b,c,'classified_valid',limits=limit,work=work)
        self.assertEqual(first.results[td.SURFACE].exact_ratio,(4,5));self.assertEqual(work.visits,6)
        self.assertEqual(second.results[td.SURFACE].result_status,'unavailable')
        self.assertEqual(second.work['visits_before'],6)
    def test_different_budget_limit_cannot_sneak_past_configuration(self):
        b,c=self.build(['a b c'])
        with self.assertRaises(InputError):self.diag(b,c,work=td.WorkBudget(1))
        for value in (-1,False,'1'):
            with self.assertRaises(InputError):td.WorkBudget(6,value)
    def test_exact_fraction_limit_does_not_fall_back_to_float(self):
        b,c=self.build(['a b c','a b d']);d=self.diag(b,c,limits=td.DiagnosticLimits(max_exact_bits=2))
        self.assertEqual(d.results[td.SURFACE].result_status,'unavailable')
        self.assertIn('max_exact_bits_exceeded',d.results[td.SURFACE].reasons)
        self.assertIsNone(d.results[td.SURFACE].value);self.assertEqual(d.pairs,())
    def test_work_counter_records_actual_partial_attempt(self):
        b,c=self.build(['a b c','a b d']);d=self.diag(b,c,limits=td.DiagnosticLimits(max_exact_bits=2))
        self.assertEqual(d.work['visits_this_diagnostic'],6);self.assertFalse(d.work['pair_table_complete'])
    def test_repeated_snapshot_does_not_change_pair_budget(self):
        b,c=self.build(['a b c']*5);d=self.diag(b,c)
        self.assertEqual(d.pair_count,10);self.assertEqual(d.work['required_trigram_visits'],60)
        self.assertEqual(d.work['unique_snapshot_tokenizations'],1)
    def test_limits_record_round_trip(self):
        limit=td.DiagnosticLimits(max_pairs=999)
        self.assertEqual(td.limits_from_record(asdict(limit)),limit)
        with self.assertRaises(InputError):td.limits_from_record({**asdict(limit),'approximate':True})
    def test_method_failure_is_not_ordinary_text_attrition(self):
        b,c=self.build(['a b c','a b d'])
        d=td.diagnose_population(b,c,'classified_all',replace(METHOD,white_space_sha256='0'*64))
        self.assertEqual(d.population_size,2);self.assertIsNone(d.eligible_count)
        self.assertEqual(d.proxy_text_coverage.status,'unavailable')
    def test_bad_public_components_fail_explicitly(self):
        b,c=self.build(['a b c'])
        for params in [(None,c,'classified_all',METHOD),(b,None,'classified_all',METHOD),(b,c,'all',METHOD),(b,c,'classified_all',{})]:
            with self.assertRaises(InputError):td.diagnose_population(*params)
    def test_no_new_contrasts_or_intervals_or_label_inference(self):
        for name in ('bootstrap','compare','predict','classify','render_report','execute','generate'):
            self.assertFalse(hasattr(td,name))
        b,c=self.build(['a b c','a b d']);d=self.diag(b,c)
        self.assertFalse(d.independent_validation_performed)
        self.assertTrue(all(x.uncertainty_status=='not_estimated' for x in d.results.values()))


class BatchAndContextTests(TextFixture):
    def test_batch_shares_limits_and_does_not_pool_populations(self):
        b,c=self.build(['a b c','a b d'])
        results=td.diagnose_cells(b,(c,),METHOD,limits=td.DiagnosticLimits(max_trigram_visits=6))
        self.assertEqual([r.analysis_population for r in results],['classified_all','classified_valid'])
        self.assertEqual(results[0].results[td.SURFACE].exact_ratio,(4,5))
        self.assertEqual(results[1].results[td.SURFACE].result_status,'unavailable')
        self.assertEqual([r.population_size for r in results],[2,2])
    def test_batch_rejects_duplicate_cells_and_views(self):
        b,c=self.build(['a b c'])
        for cells,views in [((c,c),('classified_all',)),((c,),('classified_all','classified_all')),((c,),()),((c,),([],))]:
            with self.assertRaises(InputError):td.diagnose_cells(b,cells,METHOD,views=views)
    def test_stale_accepted_assignment_is_not_used_for_new_bundle(self):
        b,c=self.build(['a b c','a b d'])
        self.row('assignment','a1')['structural_class_id']='SORT-INS'
        newer,_=self.context();d=self.diag(newer,c)
        self.assertEqual(d.status,'unavailable');self.assertIn('accepted_assignment_context_mismatch',d.reasons)
    def test_stale_output_association_is_not_silently_replaced(self):
        b,c=self.build(['a b c','a b d'])
        self.row('realization','s1')['output_ref']=tagged(record_ref('artifact','text2'))
        newer,_=self.context();d=self.diag(newer,c)
        self.assertIn('accepted_association_context_mismatch',d.samples[0].reasons)
        self.assertEqual(d.eligible_count,1)
    def test_all_current_step3_methods_have_real_bindings(self):
        import ast
        matrix=helper.read_matrix()
        declared=matrix['stage_bindings']['3']['test_bindings']
        methods=[]
        for module in ('test_text_diagnostics','test_phase2_security'):
            for cls in ast.parse((ROOT/'tests'/(module+'.py')).read_text()).body:
                if isinstance(cls,ast.ClassDef) and (module=='test_text_diagnostics' or cls.name=='TextBoundaryTests'):
                    methods.extend(f'tests.{module}.{cls.name}.{m.name}' for m in cls.body if isinstance(m,ast.FunctionDef) and m.name.startswith('test_'))
        self.assertEqual(set(declared),set(methods));self.assertEqual(len(declared),len(methods))
        self.assertEqual(matrix['delivery']['step'],3)
        self.assertEqual(len(matrix['vt_obligations']),26)
    def test_prior_stage_records_preserved_without_new_phase1_claim(self):
        matrix=helper.read_matrix()
        self.assertEqual([r['step'] for r in matrix['delivery']['history']],[1,2])
        self.assertEqual(len(matrix['predecessor']['test_ids']),503)
        self.assertEqual(matrix['evidence_status'],'not_supplied')
        self.assertEqual(matrix['deferred_status'],'deferred')
