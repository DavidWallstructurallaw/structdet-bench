"""Independent Step 3 inventory and passive receipt checks.

Every example is stipulated software test material. No candidate source is
executed and no observation or reviewer identity is empirical evidence.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from contextlib import contextmanager
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from structdet_bench import study_records as sr
from structdet_bench import study_validation as sv
from structdet_bench.contracts import InputError
from structdet_bench.local_io import ReadLimits


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/phase4'
SUITE_SHA256 = '4b8dce8c2523bc953286bf853a0e17764e8fbaa6c71cc024b4e60d39feb17c11'
FAMILIES = ('SORT-ADJ','SORT-INS','SORT-SEL','SORT-MERGE','SORT-PIVOT','SORT-HEAP','SORT-COUNT','SORT-RADIX')
PROPERTIES = ('fresh_plain_list','plain_integers','length_preserved','nondecreasing','multiplicity_preserved','input_unchanged')
SEGMENT_COUNTS = {'V-SMALL':781,'V-SHAPE':18,'V-KEY':8192,'V-STAGE':4}
WITNESSES = ([7,1,6,2,5,3,4,0],[3,1,3,0,2,0,2,1],[256,1,4095,255,16,0,257,4094],[0,1,2,3,7,6,5,4])


def k(value=None, state='known'):
    return {'state':state,'value':value} if state=='known' else {'state':state,'reason':'Stipulated fixture uncertainty.'}


def expected_rows():
    """Base-five enumeration and literal constructions from HERO §§4.4/5.3."""
    rows=[]
    alphabet=(0,1,255,256,4095)
    for width in range(5):
        for ordinal in range(5**width):
            number=ordinal
            values=[0]*width
            for index in range(width-1,-1,-1):
                values[index]=alphabet[number % 5]
                number//=5
            rows.append({'test_id':f'V-SMALL-{len(rows)+1:04d}','segment':'V-SMALL','input':values})
    ordinal=0
    for width in (8,64,256):
        patterns=[list(range(width)),list(range(width-1,-1,-1)),[4095*(i%2) for i in range(width)],[256]*width,[(19+73*i)%4096 for i in range(width)],([255,256,4095,0,257,1,4094,16]*(width//8))]
        for values in patterns:
            ordinal+=1
            rows.append({'test_id':f'V-SHAPE-{ordinal:02d}','segment':'V-SHAPE','input':values})
    for number in range(4096):
        rows.extend([{'test_id':f'V-KEY-{2*number+1:04d}','segment':'V-KEY','input':[number]}, {'test_id':f'V-KEY-{2*number+2:04d}','segment':'V-KEY','input':[4095-number,number]}])
    for ordinal,values in enumerate(WITNESSES,1):
        rows.append({'test_id':f'V-STAGE-{ordinal:02d}','segment':'V-STAGE','input':values[:]})
    return rows


def canonical(value):
    return (json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')


def fixture(variant='complete'):
    return json.loads((FIXTURES/f'sorting_validation_{variant}.json').read_bytes())


def record(data,kind):
    return next(row for row in data['records'] if row['record_type']==kind)


def observation_fixture(variant='partial'):
    name='sorting_validation_'+('' if variant=='complete' else variant+'_')+'observations.json'
    return json.loads((FIXTURES/name).read_bytes())


@contextmanager
def stage(variant='partial', *, data=None, log=None):
    """Acquire independent fixture bytes from a temporary finite inventory."""
    with TemporaryDirectory() as temporary:
        root=Path(temporary)
        source=fixture(variant) if data is None else copy.deepcopy(data)
        for packet in source['packet_inventory']:
            location=packet['location']
            if location['state']=='known' and location['value']['kind']=='local':
                name=location['value']['path']
                original=FIXTURES/name
                if original.is_file() and '/' not in name and '\\' not in name:
                    shutil.copyfile(original,root/name)
        if log is not None:
            packet=next(p for p in source['packet_inventory'] if p['packet_id']=='observations')
            body=(json.dumps(log,sort_keys=True,ensure_ascii=True,indent=2)+'\n').encode('ascii')
            (root/packet['location']['value']['path']).write_bytes(body)
            packet['sha256']=k(hashlib.sha256(body).hexdigest())
            packet['size_bytes']=k(len(body))
        path=root/'study.json'
        path.write_bytes((json.dumps(source,sort_keys=True,ensure_ascii=True,indent=2)+'\n').encode('ascii'))
        yield root,path,source


class InventoryTests(unittest.TestCase):
    def test_all_8995_rows_match_independent_base_five_enumeration(self):
        self.assertEqual(sv.sorting_inputs(),expected_rows())

    def test_independent_canonical_hash_and_byte_count_are_fixed(self):
        body=canonical(expected_rows())
        self.assertEqual(len(body),555455)
        self.assertEqual(hashlib.sha256(body).hexdigest(),SUITE_SHA256)
        self.assertEqual((FIXTURES/'sorting_validation_inputs.json').read_bytes(),body)
        self.assertEqual((ROOT/'examples/phase4/reference_spec/sorting_inputs.json').read_bytes(),body)

    def test_segment_counts_and_exact_boundary_identities(self):
        rows=sv.sorting_inputs()
        self.assertEqual({key:sum(r['segment']==key for r in rows) for key in SEGMENT_COUNTS},SEGMENT_COUNTS)
        for index,test_id,values in ((0,'V-SMALL-0001',[]),(1,'V-SMALL-0002',[0]),(780,'V-SMALL-0781',[4095]*4),(781,'V-SHAPE-01',list(range(8))),(798,'V-SHAPE-18',[255,256,4095,0,257,1,4094,16]*32),(799,'V-KEY-0001',[0]),(8990,'V-KEY-8192',[0,4095]),(8991,'V-STAGE-01',WITNESSES[0]),(8994,'V-STAGE-04',WITNESSES[3])):
            with self.subTest(index=index):
                self.assertEqual((rows[index]['test_id'],rows[index]['input']),(test_id,values))

    def test_equal_inputs_remain_distinct_purpose_identities(self):
        rows=sv.sorting_inputs()
        repeated=[row['test_id'] for row in rows if row['input']==[0]]
        self.assertEqual(repeated,['V-SMALL-0002','V-KEY-0001'])
        self.assertEqual(len({r['test_id'] for r in rows}),8995)
        self.assertLess(len({tuple(r['input']) for r in rows}),8995)

    def test_every_input_is_a_fresh_plain_list_of_bounded_plain_integers(self):
        rows=sv.sorting_inputs()
        self.assertEqual(len({id(row['input']) for row in rows}),8995)
        self.assertTrue(all(type(row['input']) is list and len(row['input'])<=256 and all(type(value) is int and 0<=value<=4095 for value in row['input']) for row in rows))

    def test_independent_calls_do_not_share_mutable_input_state(self):
        first=sv.sorting_inputs()
        first[1]['input'].append(77)
        first[0]['test_id']='changed'
        self.assertEqual(sv.sorting_inputs(),expected_rows())

    def test_manifest_contains_exact_legacy_keys_and_hash(self):
        manifest=sv.sorting_manifest()
        self.assertEqual(set(manifest),{'version','tests','sha256'})
        self.assertEqual(manifest['version'],'0.1')
        self.assertEqual(manifest['sha256'],SUITE_SHA256)
        self.assertEqual(manifest['tests'],expected_rows())
        result=sv.validate_sorting_manifest(manifest)
        self.assertFalse(result.has_errors,result.diagnostics)
        self.assertEqual(result.test_count,8995)

    def test_missing_duplicate_and_reordered_rows_are_rejected(self):
        rows=expected_rows()
        for mutated in (rows[:-1],rows+[copy.deepcopy(rows[-1])],[rows[1],rows[0]]+rows[2:]):
            with self.subTest(count=len(mutated)):
                value={'version':'0.1','tests':mutated,'sha256':hashlib.sha256(canonical(mutated)).hexdigest()}
                self.assertTrue(sv.validate_sorting_manifest(value).has_errors)

    def test_modified_ids_segments_inputs_and_boolean_integer_substitution_fail(self):
        for field,value in (('test_id','V-SMALL-9999'),('segment','V-KEY'),('input',[True]),('input',[0.0]),('input',[4096]),('input',[-1])):
            manifest={'version':'0.1','tests':expected_rows(),'sha256':SUITE_SHA256}
            manifest['tests'][1][field]=value
            with self.subTest(field=field,value=value):
                self.assertTrue(sv.validate_sorting_manifest(manifest).has_errors)

    def test_tampered_suite_digest_and_unknown_versions_fields_fail(self):
        for key,value in (('sha256','0'*64),('version','9.9'),('unexpected',True)):
            manifest={'version':'0.1','tests':expected_rows(),'sha256':SUITE_SHA256}
            manifest[key]=value
            with self.subTest(key=key):
                self.assertTrue(sv.validate_sorting_manifest(manifest).has_errors)

    def test_manifest_strict_bytes_duplicate_keys_and_trailing_data_fail(self):
        for body in (b'{"version":"0.1","version":"0.1"}',b'{} {}',b'{"n":NaN}',b'\xff'):
            with self.subTest(body=body):
                self.assertTrue(sv.validate_sorting_manifest(body).has_errors)

    def test_direct_manifest_mapping_obeys_lowered_line_limit(self):
        manifest={'version':'0.1','tests':expected_rows(),'sha256':SUITE_SHA256}
        self.assertTrue(sv.validate_sorting_manifest(manifest,limits=ReadLimits(max_line_bytes=1)).has_errors)


class ReferenceSpecificationTests(unittest.TestCase):
    def test_delivered_reference_specification_files_have_the_checked_contents(self):
        specs=sv.reference_specifications()
        delivered={name:json.loads((ROOT/'examples/phase4/reference_spec'/name).read_bytes()) for name in ('core_catalog.json','descriptor_reviews.json','witnesses.json','preservation_quotas.json','readiness_gaps.json')}
        self.assertEqual(delivered,specs)
        self.assertFalse(sv.inspect_reference_specifications(delivered).has_errors)

    def test_exact_32_core_roles_cover_all_families_and_eight_boundaries(self):
        catalog=sv.reference_specifications()['core_catalog.json']
        expected=['CORE-'+family[5:]+'-'+variant for family in FAMILIES for variant in ('A','B','D')]+[f'CORE-X{i:02d}' for i in range(1,9)]
        self.assertEqual([row['role_id'] for row in catalog['roles']],expected)
        self.assertEqual((catalog['catalog_id'],catalog['catalog_version']),('sorting_core_32','0.1'))
        self.assertEqual(catalog['required_initial_item_reviews'],64)

    def test_missing_material_and_unperformed_reviews_never_become_accepted_labels(self):
        catalog=sv.reference_specifications()['core_catalog.json']
        self.assertEqual((catalog['actual_artifact_count'],catalog['actual_human_review_count']),(0,0))
        for row in catalog['roles']:
            with self.subTest(role=row['role_id']):
                self.assertEqual(row['role_status'],'missing')
                self.assertEqual(row['evidence_refs'],[])
                for field in ('artifact_ref','accepted_assignment','accepted_validity'):
                    self.assertEqual(row[field]['state'],'unknown')
                    self.assertNotIn('value',row[field])

    def test_positive_variants_require_two_shapes_and_defects_require_counterexamples(self):
        roles=sv.reference_specifications()['core_catalog.json']['roles']
        positives=[r for r in roles if r['role_kind']=='positive_variant']
        defects=[r for r in roles if r['role_id'].endswith('-D')]
        self.assertEqual((len(positives),len(defects)),(16,8))
        for row in positives:
            self.assertIn('two_nontrivial_witness_shapes',row['requirements'])
            self.assertIn('complete_validity_evidence',row['requirements'])
        for row in defects:
            self.assertTrue(any('counterexample' in value for value in row['requirements']))
            self.assertTrue(any('constitutive' in value for value in row['requirements']))

    def test_eight_descriptors_preserve_full_constitutive_text_from_frozen_hero(self):
        descriptors=sv.reference_specifications()['descriptor_reviews.json']['descriptors']
        self.assertEqual([row['class_id'] for row in descriptors],list(FAMILIES))
        authority={}
        for line in (ROOT/'HERO_BENCHMARK_SPEC.md').read_text().splitlines():
            if line.startswith('| `SORT-') and ' / ' in line:
                cells=[c.strip() for c in line.strip('|').split('|')]
                class_id=cells[0].split('`')[1]
                authority[class_id]=cells[1:4]
        self.assertEqual(set(authority),set(FAMILIES))
        for row in descriptors:
            with self.subTest(family=row['class_id']):
                self.assertEqual(row['constitutive_rule'],authority[row['class_id']][0])
                self.assertEqual(row['permitted_variation'],authority[row['class_id']][1])
                self.assertEqual(row['discriminating_evidence'],authority[row['class_id']][2])

    def test_all_28_unordered_pairs_and_four_mandatory_distinctions_remain_missing(self):
        pairs=sv.reference_specifications()['descriptor_reviews.json']['descriptor_pairs']
        expected=[(left,right) for index,left in enumerate(FAMILIES) for right in FAMILIES[index+1:]]
        self.assertEqual([(r['left_class_id'],r['right_class_id']) for r in pairs],expected)
        mandatory={(r['left_class_id'],r['right_class_id']) for r in pairs if r['mandatory_distinction']}
        self.assertEqual(mandatory,{('SORT-ADJ','SORT-INS'),('SORT-SEL','SORT-HEAP'),('SORT-MERGE','SORT-PIVOT'),('SORT-COUNT','SORT-RADIX')})
        self.assertTrue(all(row['review_status']=='missing' and row['evidence_refs']==[] for row in pairs))

    def test_w01_through_w04_keep_exact_inputs_and_no_executed_witness_claim(self):
        witnesses=sv.reference_specifications()['witnesses.json']['witnesses']
        self.assertEqual([(r['witness_id'],r['input']) for r in witnesses],[(f'W-{i:02d}',values) for i,values in enumerate(WITNESSES,1)])
        self.assertTrue(all(row['observation_status']=='not_performed' and row['evidence_refs']==[] for row in witnesses))

    def test_preservation_quotas_keep_two_positive_variants_one_defect_and_history(self):
        quotas=sv.reference_specifications()['preservation_quotas.json']['quotas']
        self.assertEqual([row['class_id'] for row in quotas],list(FAMILIES))
        for row in quotas:
            suffix=row['class_id'][5:]
            with self.subTest(family=suffix):
                self.assertEqual((row['positive_variant_minimum'],row['reviewed_defect_or_boundary_minimum']),(2,1))
                self.assertEqual(row['required_positive_roles'],[f'CORE-{suffix}-A',f'CORE-{suffix}-B'])
                self.assertTrue(row['protect_version_history'])
                self.assertEqual(row['retention_status'],'missing')
                if suffix in ('COUNT','RADIX'):
                    self.assertEqual(row['protected_witness_ids'],['W-03'])
                    self.assertIn('CORE-X04',row['protected_boundary_role_ids'])

    def test_readiness_reports_actual_core_and_environment_gaps(self):
        gaps=sv.reference_specifications()['readiness_gaps.json']
        self.assertEqual((gaps['missing_core_role_count'],gaps['actual_initial_item_reviews']),(32,0))
        for field in ('core_construction','human_review','external_validation'):
            self.assertEqual(gaps[field],'not_started')
        self.assertFalse(gaps['candidate_execution_performed'])
        self.assertFalse(gaps['empirical_validation_performed'])
        requirements={row['requirement_id'] for row in gaps['gaps']}
        self.assertTrue({'actual_core_material','independent_human_initial_reviews','oracle_implementation_review','containment_review','all_eight_families_accommodated','execution_authorization','full_external_validation_logs'}<=requirements)

    def test_reference_spec_inspection_rejects_deleted_roles_forged_evidence_and_quotas(self):
        original=sv.reference_specifications()
        self.assertFalse(sv.inspect_reference_specifications(original).has_errors)
        for change in ('role','pair','witness','quota','status'):
            data=copy.deepcopy(original)
            if change=='role': data['core_catalog.json']['roles'].pop()
            elif change=='pair': data['descriptor_reviews.json']['descriptor_pairs'].pop()
            elif change=='witness': data['witnesses.json']['witnesses'][2]['input'][0]=257
            elif change=='quota': data['preservation_quotas.json']['quotas'][0]['positive_variant_minimum']=1
            else: data['core_catalog.json']['roles'][0]['role_status']='validated'
            with self.subTest(change=change): self.assertTrue(sv.inspect_reference_specifications(data).has_errors)

    def test_direct_reference_specification_obeys_lowered_physical_line_limit(self):
        result=sv.inspect_reference_specifications(sv.reference_specifications(),limits=ReadLimits(max_line_bytes=1))
        self.assertTrue(result.has_errors)


class ValidationPacketTests(unittest.TestCase):
    def check(self,log):
        return sv.parse_validation_packet_bytes(canonical(log))

    def test_stipulated_partial_packet_is_well_formed(self):
        result=self.check(observation_fixture())
        self.assertFalse(result.has_errors,result.diagnostics)

    def test_packet_unknown_missing_and_wrong_version_fields_fail(self):
        original=observation_fixture()
        cases=[]
        for key in original:
            changed=copy.deepcopy(original)
            del changed[key]
            cases.append(changed)
        extra=copy.deepcopy(original); extra['outputs']=['would execute']; cases.append(extra)
        wrong=copy.deepcopy(original); wrong['validation_packet_version']='1'; cases.append(wrong)
        for index,changed in enumerate(cases):
            with self.subTest(index=index): self.assertTrue(self.check(changed).has_errors)

    def test_duplicate_json_keys_and_nonfinite_numbers_are_rejected(self):
        for body in (b'{"packet_id":"a","packet_id":"a"}',b'{"x":{"a":1,"a":2}}',b'{"x":Infinity}',b'{"x":NaN}',b'{}\n{}'):
            with self.subTest(body=body):
                self.assertTrue(sv.parse_validation_packet_bytes(body).has_errors)

    def test_property_checks_require_six_explicit_knowledge_booleans(self):
        for prop in PROPERTIES:
            log=observation_fixture()
            del log['observations'][0]['property_checks'][prop]
            with self.subTest(prop=prop): self.assertTrue(self.check(log).has_errors)
        for value in (True,1,0,'true',{'state':'known','value':1}):
            log=observation_fixture(); log['observations'][0]['property_checks']['fresh_plain_list']=value
            with self.subTest(value=value): self.assertTrue(self.check(log).has_errors)

    def test_unknown_and_unavailable_checks_remain_representable(self):
        for state in ('unknown','unavailable','not_applicable'):
            log=observation_fixture()
            log['observations'][0]['property_checks']['fresh_plain_list']=k(state=state)
            with self.subTest(state=state): self.assertFalse(self.check(log).has_errors)

    def test_false_property_is_representable_without_becoming_a_counterexample(self):
        log=observation_fixture(); log['observations'][0]['property_checks']['fresh_plain_list']=k(False)
        self.assertFalse(self.check(log).has_errors)

    def test_violation_requires_true_observation_and_closed_evidence_shape(self):
        original=observation_fixture('counterexample')
        for field,value in (('observed_violation',False),('observed_violation',1),('property','magic'),('evidence_refs','opaque')):
            log=copy.deepcopy(original); log['observations'][0]['violation']['value'][field]=value
            with self.subTest(field=field,value=value): self.assertTrue(self.check(log).has_errors)

    def test_runtime_status_is_closed_and_does_not_accept_pass_alias(self):
        for state in ('pass','success',False,0,None):
            log=observation_fixture(); log['observations'][0]['runtime_status']=state
            with self.subTest(state=state): self.assertTrue(self.check(log).has_errors)

    def test_packet_nested_extra_fields_do_not_allow_output_or_code_execution(self):
        log=observation_fixture()
        log['observations'][0]['candidate_source']='raise AssertionError("must remain inert")'
        self.assertTrue(self.check(log).has_errors)

    def test_packet_byte_limits_and_depth_are_bounded(self):
        for body,limits in ((canonical(observation_fixture()),ReadLimits(max_file_bytes=8)),(b'['*65+b'0'+b']'*65,None),(b'{"x":'+b'1'*1025+b'}',None)):
            with self.subTest(length=len(body)):
                self.assertTrue(sv.parse_validation_packet_bytes(body,limits=limits).has_errors)

    def test_custom_limits_cannot_expand_the_frozen_reader_ceiling(self):
        for field,value in (('max_file_bytes',16777217),('max_bundle_bytes',67108865),('max_line_bytes',1048577),('max_records',100001),('max_depth',65),('max_number_chars',1025)):
            with self.subTest(field=field):
                self.assertTrue(sv.parse_validation_packet_bytes(canonical(observation_fixture()),limits=ReadLimits(**{field:value})).has_errors)


class ReceiptAssessmentTests(unittest.TestCase):
    def assess(self,variant='partial',*,data=None,log=None):
        with stage(variant,data=data,log=log) as (_,path,_):
            loaded=sr.load_study(path)
            return sv.inspect_validation_receipt(loaded,'validation')

    def assert_not_valid(self,result):
        self.assertNotEqual(result.validity_status,'valid',result.diagnostics)

    def test_complete_fixture_matches_hand_authored_expected_assessment(self):
        result=self.assess('complete')
        expected=json.loads((FIXTURES/'sorting_validation_expected.json').read_bytes())['variants']['complete']
        for key,value in expected.items():
            with self.subTest(key=key): self.assertEqual(getattr(result,key),value)
        self.assertFalse(result.has_errors,result.diagnostics)

    def test_partial_fixture_retains_original_8995_denominator(self):
        result=self.assess()
        self.assertEqual((result.validity_status,result.observed_count,result.expected_count),('undetermined',1,8995))
        self.assertEqual(len(result.missing_ids),8994)
        self.assertEqual(result.missing_ids[0],'V-SMALL-0002')
        self.assertEqual(result.missing_ids[-1],'V-STAGE-04')

    def test_decisive_counterexample_can_be_invalid_before_complete_coverage(self):
        result=self.assess('counterexample')
        self.assertEqual(result.validity_status,'invalid',result.diagnostics)
        self.assertEqual((result.coverage_status,result.observed_count),('partial',1))
        self.assertEqual(result.mechanism_status,'unresolved')

    def test_harness_failure_is_undetermined_not_scoped_invalidity(self):
        result=self.assess('harness_failure')
        self.assertEqual(result.validity_status,'undetermined',result.diagnostics)
        self.assertEqual(result.expected_count,8995)

    def test_timeout_memory_containment_and_oracle_error_alone_are_limited(self):
        for state in ('timeout','memory_limit','containment_failure','oracle_error','harness_error'):
            data=fixture('partial'); log=observation_fixture()
            log['observations'][0]['runtime_status']=state
            record(data,'validation_receipt')['termination']='resource_exhausted' if state in ('timeout','memory_limit') else 'unknown'
            with self.subTest(state=state):
                result=self.assess(data=data,log=log)
                self.assertEqual(result.validity_status,'undetermined',result.diagnostics)

    def test_packet_study_revision_claim_and_receipt_associations_are_exact(self):
        for field,value in (('study_id','other-study'),('study_version','other-version'),('artifact_sha256','0'*64),('suite_sha256','1'*64),('environment_configuration_sha256','8'*64),('environment_image_sha256','7'*64),('environment_id','other-environment'),('oracle_id','other-oracle'),('oracle_source_sha256','9'*64)):
            log=observation_fixture(); log[field]=value
            with self.subTest(field=field): self.assertTrue(self.assess(log=log).has_errors)
        for field in ('receipt_ref','artifact_ref'):
            log=observation_fixture(); log[field]['record_id']='different-record'
            with self.subTest(field=field): self.assertTrue(self.assess(log=log).has_errors)
        log=observation_fixture(); log['scope']['claim_id']='other-claim'
        self.assertTrue(self.assess(log=log).has_errors)

    def test_declared_image_environment_and_oracle_identity_cannot_change_behind_log(self):
        for section,field,value in (('environment','image_sha256','6'*64),('environment','environment_id','other-environment'),('oracle','oracle_id','other-oracle')):
            data=fixture('partial'); record(data,'validation_receipt')[section][field]=k(value)
            with self.subTest(section=section,field=field): self.assertTrue(self.assess(data=data).has_errors)

    def test_declared_artifact_and_suite_hash_tampering_fails(self):
        for field in ('artifact','suite'):
            data=fixture('partial'); receipt=record(data,'validation_receipt')
            if field=='artifact': receipt['artifact_sha256']='0'*64
            else: receipt['suite']['manifest_sha256']='0'*64
            with self.subTest(field=field): self.assertTrue(self.assess(data=data).has_errors)

    def test_observation_id_must_match_declared_coverage_identity(self):
        log=observation_fixture(); log['observations'][0]['test_id']='V-SMALL-0002'
        self.assertTrue(self.assess(log=log).has_errors)

    def test_duplicate_observation_identity_cannot_inflate_coverage(self):
        log=observation_fixture(); log['observations'].append(copy.deepcopy(log['observations'][0]))
        result=self.assess(log=log)
        self.assertTrue(result.has_errors)
        self.assert_not_valid(result)

    def test_duplicate_declared_coverage_is_malformed(self):
        data=fixture('partial'); receipt=record(data,'validation_receipt')
        receipt['coverage']['segments'][0]['observed_ids']*=2
        self.assertTrue(self.assess(data=data).has_errors)

    def test_multiple_bounded_packets_keep_one_ordered_coverage_union(self):
        with stage() as (root,path,data):
            second=observation_fixture()
            second['packet_id']='observations-2'
            second['observations'][0]['test_id']='V-SMALL-0002'
            body=(json.dumps(second,sort_keys=True,indent=2)+'\n').encode('ascii')
            name='second-log.json'; (root/name).write_bytes(body)
            entry=copy.deepcopy(next(p for p in data['packet_inventory'] if p['packet_id']=='observations'))
            entry.update(packet_id='observations-2',location=k({'kind':'local','path':name}),sha256=k(hashlib.sha256(body).hexdigest()),size_bytes=k(len(body)))
            data['packet_inventory'].append(entry)
            segment=record(data,'validation_receipt')['coverage']['segments'][0]
            segment['observed_ids']=['V-SMALL-0001','V-SMALL-0002']
            segment['full_log_packets']=['observations','observations-2']
            path.write_text(json.dumps(data,indent=2)+'\n')
            result=sv.inspect_validation_receipt(sr.load_study(path),'validation')
            self.assertFalse(result.has_errors,result.diagnostics)
            self.assertEqual((result.observed_count,len(result.missing_ids)),(2,8993))
            segment['full_log_packets'].reverse()
            path.write_text(json.dumps(data,indent=2)+'\n')
            self.assertTrue(sv.inspect_validation_receipt(sr.load_study(path),'validation').has_errors)

    def test_observation_row_order_is_preserved_instead_of_sorted_on_import(self):
        data=fixture('partial'); log=observation_fixture()
        second=copy.deepcopy(log['observations'][0]); second['test_id']='V-SMALL-0002'
        log['observations']=[second,log['observations'][0]]
        record(data,'validation_receipt')['coverage']['segments'][0]['observed_ids']=['V-SMALL-0002','V-SMALL-0001']
        self.assertTrue(self.assess(data=data,log=log).has_errors)

    def test_counterexample_requires_same_loaded_input_and_observation_packets(self):
        for field,value in (('input_packet_id','payload'),('observation_packet_id','payload'),('test_id','V-SMALL-0002'),('violation','nondecreasing')):
            data=fixture('counterexample'); record(data,'validation_receipt')['counterexamples'][0][field]=value
            with self.subTest(field=field):
                result=self.assess('counterexample',data=data)
                self.assertNotEqual(result.validity_status,'invalid',result.diagnostics)

    def test_counterexample_cannot_borrow_review_for_another_artifact_with_same_bytes(self):
        data=fixture('counterexample'); log=observation_fixture('counterexample')
        other_artifact=copy.deepcopy(record(data,'artifact'))
        other_artifact['record_id']='other-artifact'
        other_review=copy.deepcopy(record(data,'human_review'))
        other_review['record_id']='other-artifact-review'
        other_review['artifact_ref']={'record_type':'artifact','record_id':'other-artifact','record_version':'0.1'}
        data['records'].extend([other_artifact,other_review])
        log['observations'][0]['violation']['value']['evidence_refs']=[{'record_type':'human_review','record_id':'other-artifact-review','record_version':'0.1'}]
        with stage('counterexample',data=data,log=log) as (_,path,_):
            loaded=sr.load_study(path)
            self.assertFalse(loaded.has_errors,loaded.diagnostics)
            result=sv.inspect_validation_receipt(loaded,'validation')
            self.assertTrue(result.has_errors)
            self.assertEqual(result.validity_status,'undetermined')
            self.assertIn('validation_counterexample_unsubstantiated',{d.code for d in result.diagnostics})

    def test_false_property_without_explicit_violation_is_not_decisive_invalidity(self):
        log=observation_fixture(); log['observations'][0]['property_checks']['fresh_plain_list']=k(False)
        self.assertEqual(self.assess(log=log).validity_status,'undetermined')

    def test_complete_correct_outputs_cannot_certify_mechanism_membership(self):
        result=self.assess('complete')
        self.assertEqual(result.validity_status,'valid',result.diagnostics)
        self.assertEqual(result.mechanism_status,'unresolved')
        self.assertFalse(result.substantive_validation_performed)
        self.assertEqual((result.evidence_policy,result.material_role),('fixture_only','fixture'))

    def test_named_algorithm_and_generic_trusted_text_cannot_replace_full_log(self):
        data=fixture('complete'); receipt=record(data,'validation_receipt')
        receipt['trusted_observations']=[{'test_id':'V-SMALL-0001','outcome':'pass','observation':'SORT-RADIX returned correct sorted outputs on all inputs.','evidence_packet_id':k('payload')}]
        for segment in receipt['coverage']['segments']: segment['full_log_packets']=[]
        result=self.assess('complete',data=data)
        self.assert_not_valid(result)
        self.assertEqual(result.mechanism_status,'unresolved')

    def test_trusted_summary_contradiction_cannot_be_ignored_by_complete_pass(self):
        for outcome in ('violation','harness_failure'):
            data=fixture('complete')
            record(data,'validation_receipt')['trusted_observations']=[{'test_id':'V-SMALL-0001','outcome':outcome,'observation':'Conflicting stipulated supplied summary must remain visible.','evidence_packet_id':k('observations')}]
            with self.subTest(outcome=outcome): self.assert_not_valid(self.assess('complete',data=data))

    def test_trusted_summary_wrong_identity_cannot_be_ignored(self):
        data=fixture('complete')
        record(data,'validation_receipt')['trusted_observations']=[{'test_id':'V-SMALL-9999','outcome':'pass','observation':'Stipulated summary names an untested identity.','evidence_packet_id':k('observations')}]
        self.assertTrue(self.assess('complete',data=data).has_errors)

    def test_stricter_inspection_budget_includes_original_envelope_and_all_acquisition(self):
        with stage('complete') as (_,path,_):
            loaded=sr.load_study(path)
            self.assertFalse(loaded.has_errors,loaded.diagnostics)
            result=sv.inspect_validation_receipt(loaded,'validation',limits=ReadLimits(max_bundle_bytes=loaded.total_read_bytes-1))
            self.assertTrue(result.has_errors)
            self.assert_not_valid(result)

    def test_mechanism_observation_remains_separate_from_functional_judgment(self):
        data=fixture('partial')
        record(data,'validation_receipt')['mechanism_observations']=[{'witness_id':'W-03','relation':'Stipulated proper-digit refinement observation, not actual evidence.','evidence_packet_id':k('payload')}]
        result=self.assess(data=data)
        self.assertEqual((result.validity_status,result.mechanism_status),('undetermined','unresolved'))

    def test_missing_local_full_log_cannot_inherit_declared_verified_provenance(self):
        with stage('complete') as (root,path,data):
            packet=next(p for p in data['packet_inventory'] if p['packet_id']=='observations')
            (root/packet['location']['value']['path']).unlink()
            loaded=sr.load_study(path)
            self.assertFalse(loaded.acquisition_complete)
            result=sv.inspect_validation_receipt(loaded,'validation')
            self.assert_not_valid(result)

    def test_missing_source_snapshot_cannot_accept_a_declared_valid_receipt(self):
        with stage('complete') as (root,path,_):
            (root/'study_payload.txt').unlink()
            self.assert_not_valid(sv.inspect_validation_receipt(sr.load_study(path),'validation'))

    def test_missing_or_modified_input_manifest_cannot_supply_valid_coverage(self):
        with stage('complete') as (root,path,_):
            (root/'sorting_validation_inputs.json').write_bytes(b'[]\n')
            result=sv.inspect_validation_receipt(sr.load_study(path),'validation')
            self.assertTrue(result.has_errors)
            self.assert_not_valid(result)

    def test_snapshot_bytes_are_used_after_path_content_changes(self):
        with stage('counterexample') as (root,path,data):
            loaded=sr.load_study(path)
            packet=next(p for p in data['packet_inventory'] if p['packet_id']=='observations')
            (root/packet['location']['value']['path']).write_bytes(b'{}\n')
            result=sv.inspect_validation_receipt(loaded,'validation')
            self.assertEqual(result.validity_status,'invalid',result.diagnostics)

    def test_external_attachment_is_not_fetched_or_promoted(self):
        data=fixture('partial')
        packet=next(p for p in data['packet_inventory'] if p['packet_id']=='observations')
        packet['location']=k({'kind':'external','locator':'https://example.invalid/never-fetch'})
        packet['verification']='verified_external_receipt'
        packet['verification_ref']=k({'record_type':'human_review','record_id':'review-draft','record_version':'0.1'})
        with patch('socket.socket',side_effect=AssertionError('No network permitted')):
            result=self.assess(data=data)
        self.assert_not_valid(result)

    def test_failed_containment_or_missing_family_cannot_qualify_complete_pass(self):
        for mutation in ('containment','family','review'):
            log=observation_fixture('complete')
            if mutation=='containment': log['environment_check']['containment_status']='failed'
            elif mutation=='family': log['environment_check']['accommodated_class_ids']=list(FAMILIES[:-1])
            else: log['environment_check']['oracle_review_ref']['record_id']='absent'
            with self.subTest(mutation=mutation): self.assert_not_valid(self.assess('complete',log=log))

    def test_unknown_oracle_and_draft_human_review_leave_complete_outputs_unqualified(self):
        for mutation in ('oracle','review','independence'):
            data=fixture('complete')
            if mutation=='oracle': record(data,'validation_receipt')['oracle']['source_sha256']=k(state='unknown')
            elif mutation=='review':
                record(data,'human_review')['submission_stage']='draft'
                record(data,'human_review')['submitted_at']=k(state='unknown')
            else: record(data,'human_review')['independence']['declared_independent']=k(False)
            with self.subTest(mutation=mutation): self.assert_not_valid(self.assess('complete',data=data))

    def test_any_unknown_functional_property_withholds_complete_validity(self):
        log=observation_fixture('complete')
        for index,prop in enumerate(PROPERTIES):
            log['observations'][index]['property_checks'][prop]=k(state='unknown')
        self.assert_not_valid(self.assess('complete',log=log))

    def test_nonexistent_receipt_returns_controlled_diagnostic(self):
        with stage() as (_,path,_):
            result=sv.inspect_validation_receipt(sr.load_study(path),'does-not-exist')
            self.assertTrue(result.has_errors)


class MaterializationTests(unittest.TestCase):
    def test_fresh_materialization_contains_only_two_exact_deterministic_files(self):
        with TemporaryDirectory() as temporary:
            dest=Path(temporary)/'inputs'
            sv.materialize_sorting_inputs(dest)
            self.assertEqual({p.name for p in dest.iterdir()},{'sorting_inputs.json','sorting_manifest.json'})
            body=(dest/'sorting_inputs.json').read_bytes()
            self.assertEqual(body,canonical(expected_rows()))
            manifest=json.loads((dest/'sorting_manifest.json').read_bytes())
            self.assertEqual(manifest,{'version':'0.1','suite_id':'sorting_functional_suite','suite_version':'0.1','test_count':8995,'segment_counts':SEGMENT_COUNTS,'inputs_path':'sorting_inputs.json','sha256':SUITE_SHA256})

    def test_repeated_materializations_are_byte_identical(self):
        with TemporaryDirectory() as temporary:
            paths=[Path(temporary)/name for name in ('first','second')]
            for path in paths: sv.materialize_sorting_inputs(path)
            self.assertEqual({p.name:p.read_bytes() for p in paths[0].iterdir()},{p.name:p.read_bytes() for p in paths[1].iterdir()})

    def test_existing_destination_directory_is_not_overwritten(self):
        with TemporaryDirectory() as temporary:
            dest=Path(temporary)/'existing'; dest.mkdir()
            sentinel=dest/'preserved.txt'; sentinel.write_bytes(b'keep exact\n')
            with self.assertRaises(InputError): sv.materialize_sorting_inputs(dest)
            self.assertEqual({p.name:p.read_bytes() for p in dest.iterdir()},{'preserved.txt':b'keep exact\n'})

    def test_existing_destination_file_is_not_overwritten(self):
        with TemporaryDirectory() as temporary:
            dest=Path(temporary)/'existing'; dest.write_bytes(b'keep\n')
            with self.assertRaises(InputError): sv.materialize_sorting_inputs(dest)
            self.assertEqual(dest.read_bytes(),b'keep\n')

    def test_symlink_destination_and_ancestor_are_rejected(self):
        with TemporaryDirectory() as temporary:
            root=Path(temporary); target=root/'real'; target.mkdir()
            link=root/'link'; link.symlink_to(target,target_is_directory=True)
            for dest in (link,link/'nested'):
                with self.subTest(dest=str(dest)):
                    with self.assertRaises(InputError): sv.materialize_sorting_inputs(dest)
            self.assertEqual(list(target.iterdir()),[])

    def test_generation_neither_loads_candidate_source_nor_uses_network(self):
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            candidate=root/'candidate.py'; candidate.write_text('raise AssertionError("must never run")\n')
            with patch('socket.socket',side_effect=AssertionError('No network')),patch('subprocess.Popen',side_effect=AssertionError('No candidate process')):
                sv.materialize_sorting_inputs(root/'inputs')
            self.assertEqual(candidate.read_text(),'raise AssertionError("must never run")\n')
            self.assertEqual({p.name for p in root.iterdir()},{'inputs','candidate.py'})


if __name__=='__main__':
    unittest.main()
