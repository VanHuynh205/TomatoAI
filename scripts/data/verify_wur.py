"""Independent full-record comparison of WUR raw, normalized tables and provenance."""
import argparse
import csv
import json
import unicodedata
from collections import Counter
from decimal import Decimal
from itertools import zip_longest
from pathlib import Path

from clean_plantexpert import digest, snapshot, verify_artifacts, write_json


def verify(project, config_path, run_id):
    config = json.loads(config_path.read_text(encoding='utf-8'))
    source = project/config['source_root']
    processed = project/config['processed_parent']/run_id
    report = project/config['report_parent']/run_id
    verify_artifacts(processed, report)
    with (report/'raw-before.csv').open(encoding='utf-8',newline='') as stream:
        before = list(csv.DictReader(stream))
    for item in before: item['bytes']=int(item['bytes'])
    assert before == snapshot(source), 'raw before/current mismatch'
    intake=json.loads((project/config['intake_manifest']).read_text(encoding='utf-8-sig'))
    intake_rows=[r for r in intake['files'] if r['dataset']==source.name]
    assert len(before)==len(intake_rows)==46
    summary=json.loads((report/'summary.json').read_text(encoding='utf-8'))
    evidence=json.loads((report/'pdf-evidence.json').read_text(encoding='utf-8'))
    page14=next(r for r in evidence if r['source_file']=='source_files/ReadMe.pdf' and r['page']==14)['text']
    assert 'Weight' in page14 and 'DMC_fruit' in page14
    totals=Counter(); per_kind=Counter(); observed_flags=Counter()
    with (processed/'manifest.csv').open(encoding='utf-8',newline='') as manifest_stream:
        manifest=csv.DictReader(manifest_stream)
        files=sorted((source/'source_files').rglob('*.csv'))
        assert len(files)==43
        for path in files:
            relative=path.relative_to(source/'source_files')
            with path.open(encoding='utf-8-sig',newline='') as original, (processed/'tables'/relative).open(encoding='utf-8',newline='') as derived:
                raw_reader=csv.reader(original); out_reader=csv.reader(derived)
                h=next(raw_reader); out_h=next(out_reader)
                expected_h=[unicodedata.normalize('NFC',v).strip() for v in h]
                if relative.as_posix()=='Reference/TomQuality.csv':
                    assert len(h)==7 and h[-1].strip()=='Weight\tDMC_fruit'
                    expected_h=expected_h[:6]+['Weight','DMC_fruit']
                if relative.as_posix()=='IUACAAS/Resources.csv':
                    assert len(h)==12 and h[7:]==['']*5
                    expected_h=expected_h[:7]
                expected_h[0]='time_excel_serial'
                assert out_h==['record_id','source_record']+expected_h
                n=0
                for n,(raw,out) in enumerate(zip_longest(raw_reader,out_reader),1):
                    assert raw is not None and out is not None, 'lost/extra record'
                    if relative.as_posix()=='IUACAAS/Resources.csv':
                        assert len(raw)==12 and all(not v.strip() for v in raw[7:])
                        totals['omitted_proven_empty_cells']+=5
                        raw=raw[:7]
                    expected=[]
                    for token in raw:
                        token=unicodedata.normalize('NFC',token).strip()
                        if token.casefold() in ('','nan'):
                            expected.append('');totals['missing_cells']+=1
                        else:
                            value=Decimal(token);assert value.is_finite()
                            if value==0:totals['zero_cells']+=1
                            expected.append(token)
                    expected_id=f'wur:{path.parent.name}:{path.stem}:{n:06d}'
                    assert out==[expected_id,str(n)]+expected, f'cell/provenance mismatch {relative}:{n}'
                    row=next(manifest)
                    assert row['record_id']==expected_id and row['source_record']==str(n)
                    assert int(row['source_line_end'])==raw_reader.line_num
                    assert row['source_file']==path.relative_to(source).as_posix()
                    assert row['source_sha256']==digest_cached(path)
                    assert row['processed_file']=='tables/'+relative.as_posix()
                    assert row['processed_record']==str(n)
                    assert row['status']=='needs_review;research_only'
                    observed_flags.update(json.loads(row['flags']))
                    totals['records']+=1
                per_kind[path.stem]+=n
                assert (processed/'quarantine'/(relative.as_posix()+'.jsonl')).stat().st_size==0
        assert next(manifest,None) is None, 'extra manifest row'
    assert totals['records']==summary['source_records']==summary['retained_normalized_records']==622899
    assert summary['excluded_records']==summary['quarantined_records']==0
    assert summary['needs_review_retained_records']==622899
    assert totals['missing_cells']==summary['missing_cells']
    assert totals['zero_cells']==summary['zero_cells_preserved']
    assert dict(observed_flags)==summary['flags_overlapping']
    assert not summary['training_ready'] and not summary['mvp_dependency']
    assert summary['time_policy']==config['time_policy']
    inputs=json.loads((report/'fingerprint-inputs.json').read_text(encoding='utf-8'))
    for item in inputs['inputs']:assert digest(project/item['path'])==item['sha256']
    result={'run_id':run_id,'status':'passed','tables_checked':43,'raw_files_sha256_checked':46,
            'records_and_all_cells_compared':totals['records'],'totals':dict(totals),'per_kind':dict(per_kind),
            'source_and_output_hashes_valid':True,'no_canonical_epoch_or_timezone_assigned':True}
    write_json(report.parent/('validation-'+run_id+'.json'),result)
    print(json.dumps(result))


_hashes={}
def digest_cached(path):
    if path not in _hashes:_hashes[path]=digest(path)
    return _hashes[path]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path.cwd())
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    verify(args.project_root.resolve(),args.config.resolve(),args.run_id)
