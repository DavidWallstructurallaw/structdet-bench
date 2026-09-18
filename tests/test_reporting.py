"""Shared report semantics, disclosure, deterministic rendering and redaction."""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
import html
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from structdet_bench.pipeline import analyze_bundle,V_FIELDS,D_FIELDS
from structdet_bench.reporting import (SECTION_TITLES, render_json,render_markdown,plain,protected,canonical_bytes)
from structdet_bench.contracts import InputError,INTEGRITY_CONDITIONS
from tests.helpers import materialize_hero,tagged,rewrite_evidence_bundle,ROOT
from tests.test_pipeline import section


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=TemporaryDirectory();cls.root=Path(cls.temp.name)
        cls.path,_=materialize_hero(cls.root/'input')
        cls.result=analyze_bundle(cls.path)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_required_section_order(self):
        r=plain(self.result.report)
        self.assertEqual([x['title'] for x in r['sections']],list(SECTION_TITLES))
        md=self.result.report_markdown.decode()
        self.assertEqual([md.index(f'## {i}. {x}') for i,x in enumerate(SECTION_TITLES,1)],sorted(md.index(f'## {i}. {x}') for i,x in enumerate(SECTION_TITLES,1)))
    def test_evidence_limitations_precede_numeric_results(self):
        md=self.result.report_markdown.decode()
        self.assertLess(md.index('fixture_only'),md.index('## 4.'))
        self.assertLess(md.index('Independent scientific validation'),md.index('## 4.'))
    def test_json_and_markdown_consume_identical_tree(self):
        loaded=json.loads(self.result.report_json)
        self.assertEqual(loaded,plain(self.result.report))
        self.assertEqual(render_markdown(loaded),self.result.report_markdown)
    def test_every_scalar_value_unit_status_and_reason_survives_markdown(self):
        r=json.loads(self.result.report_json);md=self.result.report_markdown.decode()
        for row in r['sections'][3]['content']['metrics']:
            for key in ('metric_name','value','unit','result_status','population_size','reasons','qualifiers'):
                value=json.dumps(row[key],ensure_ascii=True,separators=(',',':'))
                self.assertIn(html.escape(value,quote=True).replace('|','&#124;'),md)
    def test_json_keeps_unrounded_float(self):
        r=json.loads(self.result.report_json)
        h=next(x['value'] for x in r['sections'][3]['content']['metrics'] if x['metric_name']=='structural_entropy_nats')
        self.assertEqual(h,1.392321254757429)
        self.assertNotEqual(h,round(h,3))
    def test_all_v_and_d_results_are_null_with_explicit_status(self):
        r=self.result
        vals=section(r,6)['comparisons']+section(r,7)['diagnostics']+section(r,8)['deferred']
        self.assertEqual({v['metric_name'] for v in vals},set(V_FIELDS+D_FIELDS))
        for value in vals:
            self.assertIsNone(value['value']);self.assertTrue(value['reason'])
            self.assertIn(value['result_status'],['unavailable','deferred'])
    def test_no_empirical_support_or_score_fabricated(self):
        data=json.loads(self.result.report_json)
        self.assertFalse(data['sections'][0]['content']['scope']['phase1_complete'])
        self.assertNotIn('overall_score',data)
        self.assertIn('No P1/P5 support',section(self.result,6)['claim_boundary'])
    def test_five_conjunctive_conditions_visible(self):
        conditions=section(self.result,8)['five_conditions']
        self.assertEqual({c['condition'] for c in conditions},set(INTEGRITY_CONDITIONS))
        self.assertTrue(all(c['outcome']=='unresolved' for c in conditions))
    def test_all_ten_ec_disclosures_and_unknown_expiry_visible(self):
        d=section(self.result,8)['ec_reporting_disclosures'];self.assertEqual(len(d),10)
        self.assertEqual(d['current_until']['state'],'unknown')
        self.assertIn('not_established',d['live_field_evidence'])
    def test_source_lineage_pins_and_transform_references_retained(self):
        self.assertEqual(set(section(self.result,1)['source_pins']),{'SD','SI','EC'})
        rows=section(self.result,8)['support_records']
        self.assertTrue(rows)
        self.assertTrue(all('transformation_refs' in x and 'origin' in x and 'payload_sha256' in x for x in rows))
    def test_scoped_ids_retained_without_private_person_mappings(self):
        content=self.result.report_json.decode()
        self.assertIn('reviewer',content);self.assertNotIn('test-person-1',content)
        self.assertNotIn('Stipulated test qualification',content)
    def test_private_root_absent_from_all_outputs(self):
        for data in (self.result.report_json,self.result.report_markdown,self.result.manifest_json):
            self.assertNotIn(str(self.root).encode(),data)
    def test_control_characters_links_html_and_pipes_are_inert(self):
        r=plain(self.result.report)
        r['sections'][0]['content']['test_field']='<script>alert(1)</script>\n| [click](https://example.test) ` ``` \x1b'
        md=render_markdown(r).decode()
        self.assertNotIn('<script>',md);self.assertIn('&lt;script&gt;',md)
        self.assertIn('&#124;',md);self.assertNotIn('\x1b',md)
        self.assertIn('<code>',md)
        self.assertEqual(r['sections'][0]['content']['test_field'],'<script>alert(1)</script>\n| [click](https://example.test) ` ``` \x1b')
    def test_nonfinite_results_cannot_be_serialized(self):
        for number in (float('nan'),float('inf'),-float('inf')):
            r=plain(self.result.report);r['bad']=number
            with self.assertRaises(InputError):render_json(r)
    def test_missing_required_section_fails_serialization(self):
        r=plain(self.result.report);r['sections'].pop()
        with self.assertRaises(InputError):render_json(r)
    def test_zero_false_and_known_null_are_not_unknown(self):
        for value in [0,False,None]:
            k=protected(tagged(value));self.assertEqual(k['state'],'known');self.assertEqual(k['value'],value)
        self.assertEqual(protected(tagged(state='unknown'))['state'],'unknown')
    def test_unknown_unavailable_and_inapplicable_retain_distinction(self):
        for state in ['unknown','unavailable','not_applicable']:
            self.assertEqual(protected(tagged(state=state,reason='PRIVATE_REASON'))['state'],state)
            self.assertNotIn('PRIVATE_REASON',json.dumps(protected(tagged(state=state,reason='PRIVATE_REASON'))))
    def test_canonical_dictionary_order_invariance(self):
        self.assertEqual(canonical_bytes({'b':1,'a':2}),canonical_bytes({'a':2,'b':1}))
        self.assertEqual(plain(Fraction(3,4)),{'numerator':3,'denominator':4})
    def test_pinned_input_hashes_do_not_claim_program_hashes(self):
        refs=section(self.result,1)['input_refs']
        self.assertEqual(len(refs),3)
        self.assertTrue(all(x['sha256'] and x['locator_sha256'] for x in refs))
        associations=section(self.result,2)['output_associations']
        self.assertTrue(all(x['output_content_hash']['state']=='not_applicable' for x in associations))
    def test_zero_count_registry_classes_are_visible(self):
        d=section(self.result,4)['distributions'][0]['class_counts']
        self.assertEqual(len(d),8)
        self.assertEqual([d[x] for x in ('SORT-ADJ','SORT-INS','SORT-SEL')],[0,0,0])
    def test_held_evidence_prose_and_task_metadata_not_copied(self):
        with TemporaryDirectory() as t:
            p,_=materialize_hero(Path(t)/'input')
            m=json.loads(p.read_text());obs=[json.loads(x) for x in (p.parent/'records.jsonl').read_text().splitlines()]
            sup=[json.loads(x) for x in (p.parent/'evidence.jsonl').read_text().splitlines()]
            secret='TOP_SECRET_TOKEN /home/private/id <script>bad</script>'
            m['frames'][0]['task_context']=secret
            m['cells'][0]['model_identifier']=tagged(secret)
            sup[0]['payload']['entity_id']=tagged(secret)
            # Clear asserted file hashes for the intentionally changed test input.
            for f in m['record_files']:f['expected_sha256']=tagged(state='unknown')
            r=analyze_bundle(rewrite_evidence_bundle(p.parent,obs,sup,m))
            for data in (r.report_json,r.report_markdown,r.manifest_json):self.assertNotIn(secret.encode(),data)
    def test_reanalysis_and_v_dependents_remain_separate(self):
        with TemporaryDirectory() as t:
            p,_=materialize_hero(Path(t)/'input','HF-06');r=analyze_bundle(p)
            c=section(r,8)['corrections'][0]
            self.assertEqual(c['event_type'],'correction');self.assertEqual(c['v_dependents'],'not_implemented')
            self.assertTrue(c['m_fields_recomputed_from_pinned_input'])

class SourceAssociationDisclosureTests(unittest.TestCase):
    def test_actual_output_hash_is_preserved_while_body_is_withheld(self):
        import hashlib
        from tests.helpers import population_bundle,artifact_record,record_ref
        with TemporaryDirectory() as t:
            root=Path(t);p,o,s,m=population_bundle(root,['SORT-ADJ'])
            body=b'PASSIVE_TEST_BODY_NOT_A_SORTING_PROGRAM';sha=hashlib.sha256(body).hexdigest()
            (root/'body.txt').write_bytes(body);o.append(artifact_record())
            sample=next(r for r in o if r['record_type']=='realization')
            sample['output_ref']=tagged(record_ref('artifact','artifact1'));sample['output_content_hash']=tagged(sha)
            r=analyze_bundle(rewrite_evidence_bundle(root,o,s,m))
            a=section(r,2)['output_associations'][0]
            self.assertEqual(a['output_content_hash'],{'state':'known','value':sha})
            self.assertNotIn(body,r.report_json);self.assertEqual(r.exit_code,0)
