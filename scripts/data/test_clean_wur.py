"""Regression and integration checks for immutable WUR derivation."""
import csv
import io
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import clean_wur as pipeline
from clean_plantexpert import digest, snapshot, write_json


class WurChecks(unittest.TestCase):
    def test_actual_reference_header_repair_requires_evidence_and_eight_values(self):
        header = ['%time', '\tFlavour', ' \tTSS', '\tAcid', '\t%Juice', '\tBite', '\tWeight\tDMC_fruit']
        names, changes = pipeline.headers(header, [['43880','74','7.9','15','58','187','7.77','nan']], 'Reference/TomQuality.csv', True)
        self.assertEqual(names, ['time_excel_serial','Flavour','TSS','Acid','%Juice','Bite','Weight','DMC_fruit'])
        self.assertEqual(changes[0]['after'], ['Weight','DMC_fruit'])
        for evidence, row in ((False,['0']*8), (True,['0']*7)):
            with self.assertRaisesRegex(ValueError,'evidence'):
                pipeline.headers(header,[row],'Reference/TomQuality.csv',evidence)

    def test_empty_trailing_columns_require_all_row_proof(self):
        header = ['%Time ','Heat_cons','ElecHigh','ElecLow','CO2_cons','Irr','Drain']+['']*5
        names,_ = pipeline.headers(header,[['43815']+['0']*6+['']*5],'IUACAAS/Resources.csv',True)
        self.assertEqual(len(names),7)
        with self.assertRaisesRegex(ValueError,'all-row evidence'):
            pipeline.headers(header,[['43815']+['0']*6+['']*4+['1']],'IUACAAS/Resources.csv',True)

    def test_colliding_or_unknown_headers_rejected(self):
        for header in (['%time','x',' x '], ['date','x'], ['%time','record_id']):
            with self.assertRaises(ValueError):
                pipeline.headers(header,[['0']*len(header)],'Weather/Weather.csv',True)

    def test_missing_and_zero_stay_distinct_no_numeric_rounding(self):
        self.assertEqual(pipeline.number(' NaN ',['','nan']),('',None,'missing'))
        self.assertEqual(pipeline.number(' 0 ',['','nan']),('0',Decimal(0),'numeric'))
        self.assertEqual(pipeline.number('0.0000000000000000001234', ['','nan'])[0],'0.0000000000000000001234')
        for value in ['inf','NaN','1_000','=1+2','1,2','１２']:
            with self.assertRaises(ValueError): pipeline.number(value,[])

    def test_temporal_flags_do_not_correct_or_sort(self):
        self.assertEqual(pipeline.time_flags(Decimal(4),Decimal(5),{Decimal(4):1},Decimal(1),Decimal(1)),
                         ['duplicate_timestamp_retained','time_order_decrease_retained','interval_differs_from_documented_cadence'])
        self.assertEqual(pipeline.time_flags(Decimal('43815.00347'),Decimal('43815'),{},Decimal(1)/288,Decimal(1)),[])
        self.assertEqual(pipeline.time_flags(None,None,{},None,Decimal(1)),['timestamp_missing'])

    def fixture(self, root):
        source = root/'raw/wur_fixture'
        (source/'source_files/Weather').mkdir(parents=True)
        (source/'source_files/Weather/Weather.csv').write_text('%time,Rain\n43815, 0 \n43815.00347,NaN\n43815.00694,bad\n43815.01042,1\n',encoding='utf-8')
        (source/'source_files/ReadMe.pdf').write_bytes(b'fixture-document-not-real-PDF')
        (source/'source_files/Economics.pdf').write_bytes(b'fixture-document-not-real-PDF')
        write_json(root/'intake.json',{'files':[{'dataset':source.name,'relative_path':source.name+'/'+r['source_file'],'bytes':r['bytes'],'sha256':r['sha256']} for r in snapshot(source)]})
        config = {'source_root':'raw/wur_fixture','processed_parent':'processed','report_parent':'reports',
                  'intake_manifest':'intake.json','reference_inputs':[], 'teams':[], 'table_kinds':[],
                  'maximum_csv_bytes':10000,'maximum_csv_rows':100,'missing_tokens':['','nan'],
                  'expected_interval_days':{'Weather':str(Decimal(1)/288)},'frequency_tolerance_seconds':'1',
                  'time_policy':'serial only', 'source_url':'fixture','doi':'fixture','license_declared':'fixture'}
        write_json(root/'config.json',config)
        return source, root/'config.json'

    @staticmethod
    def fake_pdf(source, report, config):
        write_json(report/'pdf-evidence.json',{'fixture_only':True})
        return {},False

    def test_cli_flow_count_provenance_quarantine_raw_and_idempotency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source,config = self.fixture(root); before = snapshot(source)
            with patch.object(pipeline,'pdf_evidence',side_effect=self.fake_pdf):
                result = pipeline.run(config,root)
                self.assertEqual((result['source_records'],result['retained_normalized_records'],result['quarantined_records'],result['excluded_records']),(4,3,1,0))
                run = result['run_id']; p=root/'processed'/run; r=root/'reports'/run
                with (p/'manifest.csv').open(newline='',encoding='utf-8') as f: manifest=list(csv.DictReader(f))
                self.assertEqual([m['source_record'] for m in manifest],['1','2','3','4'])
                self.assertTrue(all(m['source_sha256']==digest(source/'source_files/Weather/Weather.csv') for m in manifest))
                with (p/'tables/Weather/Weather.csv').open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
                self.assertEqual([row['source_record'] for row in rows],['1','2','4'])
                self.assertEqual([row['Rain'] for row in rows],['0','','1'])
                q=json.loads((p/'quarantine/Weather/Weather.csv.jsonl').read_text())
                self.assertEqual(q['original_cells'],['43815.00694','bad'])
                self.assertEqual(q['source_record'],3)
                artifacts=snapshot(p)+snapshot(r)
                second=pipeline.run(config,root)
                self.assertEqual(second,result)
                self.assertEqual(artifacts,snapshot(p)+snapshot(r))
                self.assertEqual(before,snapshot(source))
                self.assertFalse(result['training_ready'])

    def test_output_tampering_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); _,config=self.fixture(root)
            with patch.object(pipeline,'pdf_evidence',side_effect=self.fake_pdf):
                result=pipeline.run(config,root)
                target=root/'processed'/result['run_id']/'tables/Weather/Weather.csv'
                target.write_text('modified',encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'hash changed'):pipeline.run(config,root)
                self.assertEqual(target.read_text(),'modified')

    def test_intake_hash_mismatch_blocks_before_derivation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source,config=self.fixture(root)
            (source/'source_files/Weather/Weather.csv').write_text('tampered',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'intake manifest'):pipeline.run(config,root)
            self.assertFalse((root/'processed').exists())

    def test_partial_failure_checkpoint_retained_and_retry_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); _,config=self.fixture(root)
            with patch.object(pipeline,'pdf_evidence',side_effect=ValueError('PDF parse failure')):
                with self.assertRaisesRegex(ValueError,'PDF parse failure'):pipeline.run(config,root)
            checkpoint=next((root/'reports').rglob('checkpoint.json'))
            self.assertEqual(json.loads(checkpoint.read_text())['status'],'partial_failed_retained')
            with self.assertRaisesRegex(ValueError,'partial run retained'):pipeline.run(config,root)

    def test_output_cannot_overlap_raw(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); _,config=self.fixture(root)
            value=json.loads(config.read_text());value['processed_parent']='raw/wur_fixture/new'
            write_json(config,value)
            with self.assertRaisesRegex(ValueError,'overlaps source'):pipeline.run(config,root)


if __name__ == '__main__':
    unittest.main()
