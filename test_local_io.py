"""Strict parser, bounded byte snapshots and scoped bundle diagnostics."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from structdet_bench.contracts import ExactNumber, InputError
from structdet_bench.local_io import LocalReader, ReadLimits, load_bundle, parse_json_bytes, relative_parts
from structdet_bench.records import parse_manifest
from tests.helpers import artifact_record, minimal_manifest, record_ref, sample_record, tagged, write_input_bundle

class StrictJSONTests(unittest.TestCase):
    def test_duplicate_keys_and_escaped_aliases_fail(self):
        for raw in (b'{"x":1,"x":2}',b'{"x":{"a":1,"a":2}}',b'{"a":1,"\\u0061":2}'):
            with self.subTest(raw=raw),self.assertRaises(InputError) as ctx: parse_json_bytes(raw)
            self.assertEqual(ctx.exception.code,"duplicate_json_key")

    def test_nonfinite_constants_fail(self):
        for token in (b'NaN',b'Infinity',b'-Infinity'):
            with self.assertRaises(InputError) as ctx: parse_json_bytes(b'{"n":'+token+b'}')
            self.assertEqual(ctx.exception.code,"nonfinite_number")

    def test_large_finite_exponent_is_not_float_infinity(self):
        got=parse_json_bytes(b'{"n":1e309}')
        self.assertIsInstance(got['n'],ExactNumber)
        self.assertEqual(got['n'].token,'1e309')
        self.assertTrue(got['n'].decimal.is_finite())

    def test_utf8_bom_surrogates_and_bad_syntax_fail(self):
        for raw,code in ((b'\xff','invalid_utf8'),(b'\xef\xbb\xbf{}','utf8_bom_not_supported'),
                         (b'{"x":"\\ud800"}','unpaired_unicode_surrogate'),(b'{"x":1,}','invalid_json'),
                         (b'','invalid_json'),(b'{} {}','invalid_json')):
            with self.subTest(code=code),self.assertRaises(InputError) as ctx: parse_json_bytes(raw)
            self.assertEqual(ctx.exception.code,code)
        self.assertEqual(parse_json_bytes(b'{"x":"\\ud83d\\ude00"}')['x'],'😀')

    def test_depth_bound_respects_strings(self):
        self.assertEqual(parse_json_bytes(b'{"x":"[[[\\\"[[["}',ReadLimits(max_depth=1))['x'],'[[["[[[')
        parse_json_bytes(b'[[0]]',ReadLimits(max_depth=2))
        with self.assertRaises(InputError) as ctx: parse_json_bytes(b'[[[0]]]',ReadLimits(max_depth=2))
        self.assertEqual(ctx.exception.code,'json_depth_exceeded')

    def test_number_length_and_file_limits(self):
        for raw in (b'12345',b'1.2345'):
            with self.assertRaises(InputError) as ctx: parse_json_bytes(raw,ReadLimits(max_number_chars=4))
            self.assertEqual(ctx.exception.code,'number_token_too_long')
        with self.assertRaises(InputError) as ctx: parse_json_bytes(b'{"a": 1}',ReadLimits(max_file_bytes=3))
        self.assertEqual(ctx.exception.code,'file_size_exceeded')

    def test_invalid_overrides_never_weaken_limits(self):
        for kw in ({'max_depth':True},{'max_file_bytes':0},{'max_records':-1},{'max_depth':129},{'max_number_chars':4097}):
            with self.assertRaises(InputError): ReadLimits(**kw)

    def test_bad_manifest_field_types_have_controlled_errors(self):
        for key in minimal_manifest():
            for value in (None,False,[],{}):
                raw=minimal_manifest();raw[key]=value
                try: parse_manifest(raw)
                except InputError: pass
                except Exception as exc: self.fail(f'Uncontrolled {type(exc).__name__} for {key}')

class SnapshotTests(unittest.TestCase):
    def test_snapshot_and_repeated_path_read(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);data=b'\xef\xbb\xbfpassive bytes\r\n';(root/'body.bin').write_bytes(data)
            with LocalReader(root,ReadLimits()) as reader:
                one=reader.read('body.bin');two=reader.read('body.bin')
                self.assertIs(one,two)
                self.assertEqual(one.content,data)
                self.assertEqual(one.sha256,hashlib.sha256(data).hexdigest())
                self.assertEqual(reader.total,len(data))
            with self.assertRaises(InputError): reader.read('body.bin')

    def test_snapshot_stays_stable_after_path_replacement(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'a').write_bytes(b'original')
            with LocalReader(root,ReadLimits()) as reader:
                old=reader.read('a');(root/'a').write_bytes(b'replacement')
                self.assertEqual(old.content,b'original')
                self.assertEqual(reader.read('a').content,b'original')
            with LocalReader(root,ReadLimits()) as reader: self.assertEqual(reader.read('a').content,b'replacement')

    def test_file_and_total_byte_limits(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'a').write_bytes(b'1234');(root/'b').write_bytes(b'5678')
            with LocalReader(root,ReadLimits(max_file_bytes=3)) as reader:
                with self.assertRaises(InputError) as ctx: reader.read('a')
                self.assertEqual(ctx.exception.code,'file_size_exceeded')
            with LocalReader(root,ReadLimits(max_bundle_bytes=7)) as reader:
                reader.read('a')
                with self.assertRaises(InputError) as ctx: reader.read('b')
                self.assertEqual(ctx.exception.code,'bundle_size_exceeded')
                self.assertNotIn('b',reader.snapshots)

    def test_change_during_read_is_detected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);target=root/'a';target.write_bytes(b'abc');original_read=os.read;changed=False
            def mutate(fd,count):
                nonlocal changed
                result=original_read(fd,count)
                if not changed: changed=True;target.write_bytes(b'abcdef')
                return result
            with LocalReader(root,ReadLimits()) as reader,patch('os.read',side_effect=mutate):
                with self.assertRaises(InputError) as ctx: reader.read('a')
                self.assertEqual(ctx.exception.code,'file_changed_during_read')

    def test_path_grammar_rejects_remote_and_expansion(self):
        for path in ('../x','/etc/passwd','a/../../x','./x','a//b',r'..\x','https://example.test/x','file:///x',
                     's3://x','C:/x','//host/share','$HOME/x','~/x','a\x00b','a\nb'):
            with self.subTest(path=path),self.assertRaises(InputError): relative_parts(path)
        self.assertEqual(relative_parts('subdir/local-文稿.txt'),('subdir','local-文稿.txt'))

    def test_internal_external_and_root_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as t,tempfile.TemporaryDirectory() as other:
            root=Path(t);(root/'regular').write_text('data');(Path(other)/'outside').write_text('private')
            (root/'internal-link').symlink_to(root/'regular');(root/'outside-link').symlink_to(Path(other)/'outside')
            (root/'dir-link').symlink_to(other,target_is_directory=True)
            with LocalReader(root,ReadLimits()) as reader:
                for path in ('internal-link','outside-link','dir-link/outside'):
                    with self.assertRaises(InputError): reader.read(path)
            root_link=Path(other)/'root-link';root_link.symlink_to(root,target_is_directory=True)
            with self.assertRaises(InputError): LocalReader(root_link,ReadLimits())

    def test_directory_and_fifo_are_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'directory').mkdir();os.mkfifo(root/'pipe')
            with LocalReader(root,ReadLimits()) as reader:
                for path in ('directory','pipe'):
                    with self.assertRaises(InputError) as ctx: reader.read(path)
                    self.assertEqual(ctx.exception.code,'not_regular_file')

    def test_unsupported_platform_has_no_unsafe_fallback(self):
        with tempfile.TemporaryDirectory() as t,patch('os.supports_dir_fd',set()):
            with self.assertRaises(InputError) as ctx: LocalReader(Path(t),ReadLimits())
            self.assertEqual(ctx.exception.code,'safe_local_open_unavailable')

class BundleTests(unittest.TestCase):
    def test_empty_and_malformed_records_remain_distinct(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path=write_input_bundle(root);empty=load_bundle(path)
            self.assertFalse(empty.has_errors,empty.diagnostics);self.assertEqual(len(empty.records),3)
            (root/'records.jsonl').write_bytes(b'{broken\n');bad=load_bundle(path)
            self.assertTrue(bad.has_errors);self.assertFalse(bad.acquisition_complete)
            self.assertEqual(len(bad.records),4);self.assertIsNone(bad.records[-1].record)
            self.assertEqual(bad.snapshots['records.jsonl'].content,b'{broken\n')

    def test_malformed_line_does_not_erase_next_record(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path=write_input_bundle(root)
            (root/'records.jsonl').write_bytes(b'not-json\n'+json.dumps(sample_record()).encode()+b'\n')
            got=load_bundle(path)
            self.assertEqual(len(got.records),5);self.assertIsNone(got.records[-2].record)
            self.assertEqual(got.records[-1].record.record_id,'s1');self.assertFalse(got.acquisition_complete)

    def test_hash_mismatch_is_scoped_and_keeps_expected_hash(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);art=artifact_record();art['expected_sha256']=tagged('0'*64)
            path=write_input_bundle(root,[art,sample_record()]);(root/'body.txt').write_bytes(b'original output')
            got=load_bundle(path)
            self.assertEqual(got.artifacts[0].status,'hash_mismatch')
            self.assertEqual(got.artifacts[0].expected_sha256,'0'*64)
            self.assertEqual(got.artifacts[0].actual_sha256,hashlib.sha256(b'original output').hexdigest())
            self.assertTrue(got.records[-1].shape_valid)
            self.assertTrue(any(d.code=='content_hash_mismatch' and d.scope=='artifact' for d in got.diagnostics))

    def test_record_file_hash_mismatch_preserves_inventory(self):
        with tempfile.TemporaryDirectory() as t:
            raw=minimal_manifest();raw['record_files'][0]['expected_sha256']=tagged('0'*64)
            got=load_bundle(write_input_bundle(Path(t),[sample_record()],raw))
            self.assertEqual(got.records[-1].record.record_id,'s1')
            self.assertTrue(any(d.code=='content_hash_mismatch' and d.scope=='file' for d in got.diagnostics))

    def test_sample_hash_uses_analyzed_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);sample=sample_record();sample['output_ref']=tagged(record_ref('artifact','artifact1'))
            sample['output_content_hash']=tagged('0'*64);path=write_input_bundle(root,[artifact_record(),sample])
            (root/'body.txt').write_bytes(b'passive');got=load_bundle(path)
            self.assertIn('sample_content_hash_mismatch',[d.code for d in got.diagnostics])

    def test_external_and_unavailable_artifacts_are_inert(self):
        with tempfile.TemporaryDirectory() as t:
            external=artifact_record('external');external['content_ref']=tagged({'kind':'external','locator':'https://example.test/private?token=SECRET'})
            private=artifact_record('private');private['content_ref']=tagged(state='unavailable',reason='Access restricted.')
            got=load_bundle(write_input_bundle(Path(t),[external,private]))
            self.assertEqual([a.status for a in got.artifacts],['external_not_fetched','unavailable'])
            self.assertEqual(set(got.snapshots),{'bundle.json','records.jsonl'})
            self.assertNotIn('SECRET',repr(got));self.assertFalse(got.has_errors)

    def test_line_limit_does_not_turn_suffix_into_next_row(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path=write_input_bundle(root);(root/'records.jsonl').write_bytes(b'x'*3000+b'\n{}\n')
            got=load_bundle(path,limits=ReadLimits(max_line_bytes=32))
            self.assertEqual(len(got.records),5);self.assertEqual(got.records[-2].line,1);self.assertEqual(got.records[-1].line,2)
            self.assertIn('jsonl_line_size_exceeded',[d.code for d in got.diagnostics])

    def test_record_limit_is_not_silent_sampling(self):
        with tempfile.TemporaryDirectory() as t:
            path=write_input_bundle(Path(t),[sample_record('s1'),sample_record('s2')])
            got=load_bundle(path,limits=ReadLimits(max_records=4))
            self.assertFalse(got.acquisition_complete);self.assertIn('record_count_exceeded',[d.code for d in got.diagnostics])
            self.assertIn(b'"s2"',got.snapshots['records.jsonl'].content)

    def test_read_order_does_not_become_scientific_order(self):
        with tempfile.TemporaryDirectory() as t:
            one,two=sample_record('z'),sample_record('a');one['sample_order']=tagged(state='unknown');two['sample_order']=tagged(state='unknown')
            got=load_bundle(write_input_bundle(Path(t),[one,two]))
            samples=[e.record for e in got.records if e.record and e.record.record_type=='realization']
            self.assertEqual([s.record_id for s in samples],['z','a'])
            self.assertTrue(all(s.data['sample_order']['state']=='unknown' for s in samples))

    def test_only_declared_files_are_read(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path=write_input_bundle(root);(root/'never-read.jsonl').write_bytes(b'broken private bytes')
            got=load_bundle(path)
            self.assertNotIn('never-read.jsonl',got.snapshots);self.assertFalse(got.has_errors)

    def test_source_pin_mismatch_does_not_trigger_retrieval(self):
        with tempfile.TemporaryDirectory() as t:
            raw=minimal_manifest();raw['source_pins']=[{'source_id':'EC','sha256':'0'*64}]
            got=load_bundle(write_input_bundle(Path(t),manifest=raw))
            self.assertIn('source_pin_mismatch',[d.code for d in got.diagnostics]);self.assertEqual(len(got.snapshots),2)

    def test_bad_required_version_never_becomes_empty_success(self):
        with tempfile.TemporaryDirectory() as t:
            raw=minimal_manifest();raw['input_schema_version']='9.0'
            got=load_bundle(write_input_bundle(Path(t),manifest=raw))
            self.assertIsNone(got.manifest);self.assertTrue(got.has_errors);self.assertFalse(got.acquisition_complete)
            self.assertIn('bundle.json',got.snapshots)

    def test_wrong_file_role_preserves_raw_record(self):
        with tempfile.TemporaryDirectory() as t:
            raw={**record_ref('evidence','e1'),'payload':{'text':'fixture'}}
            got=load_bundle(write_input_bundle(Path(t),[raw]))
            self.assertIsNone(got.records[-1].record);self.assertEqual(got.records[-1].raw['record_id'],'e1')
            self.assertIn('record_file_role_mismatch',[d.code for d in got.diagnostics])
