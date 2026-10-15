"""Independent full source-to-derived verification with csv/json/Decimal, read only."""
import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from clean_plantexpert import digest, snapshot, verify_artifacts, write_json


def require(condition,message):
    if not condition: raise ValueError(message)


def read_json(path): return json.loads(path.read_text(encoding="utf-8"))


def lines(path):
    with path.open(encoding="utf-8") as stream: return [json.loads(line) for line in stream]


def verify(project,config_path,run_id):
    config=read_json(config_path);source=project/config["source_root"]
    processed,report=[project/config[k]/run_id for k in ("processed_parent","report_parent")]
    verify_artifacts(processed,report)
    before=snapshot(source);payload=read_json(report/"fingerprint-inputs.json")
    require(before==payload["sources"],"raw hash/size mismatch")
    require(all(digest(project/r["path"])==r["sha256"] for r in payload["references"]),"reference changed")
    summary=read_json(report/"summary.json"); tables={t["table"]:t for t in read_json(report/"tables.json")}
    records_all=[];fields_checked=0; zeros=0
    with (source/config["csv_file"]).open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.reader(stream,strict=True);headers=next(reader);csv_source=list(reader)
    json_text=(source/config["json_file"]).read_text(encoding="utf-8-sig")
    json_source=json.loads(json_text,parse_float=Decimal,parse_int=Decimal)
    dictionary=read_json(report/"data-dictionary.json")
    require(len(dictionary)==51,"dictionary coverage 14+37")
    for kind,original in (("csv",csv_source),("json",json_source)):
        records=lines(processed/"tables"/(kind+".jsonl"))
        require(len(records)==len(original)==tables[kind]["source_records"],"source count mismatch")
        require(len(lines(processed/"quarantine"/(kind+".jsonl")))==0,"unexpected real-source quarantine")
        source_file=config[kind+"_file"];source_hash=digest(source/source_file)
        for index,(raw,r) in enumerate(zip(original,records),1):
            require(r["source_record"]==index and r["record_id"]==f"mendeley:{kind}:{index}","record provenance/ID mismatch")
            require(r["source_file"]==source_file and r["source_sha256"]==source_hash,"source file/hash mismatch")
            require(r["training_ready"] is False and r["status"]=="needs_review;research_only","readiness changed")
            require(r["experimental_group"] is None and r["verified_cross_dataset_key"] is None,"guessed group/join")
            require(not r["errors"],"unexpected record error")
            if kind=="csv":
                require(r["raw_fields"]==raw,"CSV raw values altered")
                require(r["source_line_start"]==r["source_line_end"]==index+1,"CSV source line mismatch")
                expected={h.strip():v for h,v in zip(headers,raw)}
                require(set(r["fields"])==set(expected),"CSV field schema")
                for name,value in expected.items():
                    item=r["fields"][name]
                    require(item["raw_kind"]=="string" and item["raw_value"]==value,"CSV raw field mismatch")
                    require(item["value"]==value.strip(),"CSV normalized value altered")
                    if name==config["csv_category_column"]: require(item["kind"]=="category","CSV category type")
                    else:
                        require(item["kind"]=="decimal_text" and Decimal(item["value"])==Decimal(value),"CSV numeric precision mismatch")
                        zeros+=Decimal(value)==0
            else:
                require(r["source_pointer"]=="/"+str(index-1),"JSON source pointer")
                require(json_text[r["source_character_start"]:r["source_character_end"]]==r["raw_json_record"],"JSON literal source slice altered")
                require(json.loads(r["raw_json_record"],parse_float=Decimal,parse_int=Decimal)==raw,"JSON source record mismatch")
                require(set(r["fields"])==set(raw),"JSON field schema")
                for name,value in raw.items():
                    item=r["fields"][name]
                    if name==config["timestamp_key"]:
                        require(item["raw_kind"]=="string" and item["raw_value"]==value,"JSON raw time mismatch")
                        require(item["kind"]=="naive_datetime" and item["value"]==datetime.strptime(value,"%Y-%m-%d %H:%M:%S").isoformat(),"JSON time normalized/zone mismatch")
                    else:
                        require(item["raw_kind"]=="number" and item["kind"]=="decimal_text","JSON number became string source/missing")
                        require(Decimal(item["raw_value"])==value and Decimal(item["value"])==value,"JSON numeric precision mismatch")
                        require(item["raw_value"]==item["value"],"JSON numeric lexeme changed")
                        zeros+=value==0
            fields_checked+=len(r["fields"]);records_all.append(r)
        require(tables[kind]["quarantined_records"]==0 and tables[kind]["excluded_records"]==0,"table retention status")
    with (processed/"tables/csv-normalized.csv").open(encoding="utf-8",newline="") as stream:
        table=list(csv.reader(stream))
    require(table[0]==[h.strip() for h in headers] and table[1:]==csv_source,"derived CSV header/value coverage")
    manifest=read_json(processed/"manifest.json")
    require(len(manifest)==len(records_all)==3393,"manifest reconciliation")
    require(len({r["record_id"] for r in manifest})==3393,"duplicate manifest IDs")
    by_id={r["record_id"]:r for r in records_all}
    with (processed/"manifest.csv").open(encoding="utf-8",newline="") as stream: csv_manifest=list(csv.DictReader(stream))
    require([r["record_id"] for r in csv_manifest]==[r["record_id"] for r in manifest],"manifest CSV/JSON order")
    for item in manifest:
        r=by_id[item["record_id"]]
        require(item["source_file"]==r["source_file"] and item["source_sha256"]==r["source_sha256"] and item["source_record"]==r["source_record"],"manifest source reference")
        require(item["source_pointer"]==r["source_pointer"] and item["status"]==r["status"],"manifest pointer/status")
        kind=item["record_id"].split(":")[1]
        require(item["processed_file"]=="tables/"+kind+".jsonl" and item["processed_record"]==item["source_record"],"manifest output row")
    json_times=Counter(r["dateTimeAdded"] for r in json_source)
    require(len(json_times)==30 and sum(v>1 for v in json_times.values())==23,"independent timestamp audit")
    require(sum(v for v in json_times.values() if v>1)==386,"duplicate timestamp record reconciliation")
    csv_dups=Counter(tuple(r) for r in csv_source)
    json_dups=Counter(json.dumps(r,sort_keys=True,default=str) for r in json_source)
    require(sum(v-1 for v in csv_dups.values())==tables["csv"]["duplicate_value_surplus"]==28,"CSV duplicate reconciliation")
    require(sum(v-1 for v in json_dups.values())==tables["json"]["duplicate_value_surplus"]==92,"JSON duplicate reconciliation")
    require(summary["retained_records"]==summary["source_records"]==3393 and summary["quarantined_records"]==summary["excluded_records"]==0,"summary counts")
    require(fields_checked==56541 and zeros==summary["zero_cells_preserved"]==1535,"field/zero reconciliation")
    diagnostics=read_json(report/"numeric-hypotheses.json")
    require([(d["matches"],d["nonmatches"],d["skipped"]) for d in diagnostics]==[(236,2764,0),(393,0,0),(14,379,0),(227,166,0),(393,0,0)],"diagnostic baseline changed")
    # Independent source checks of the strongest identities; not proof of generating policy/outcome.
    tolerance=Decimal(config["numeric_hypothesis_tolerance"]["json"])
    require(all(abs(r["evapotranspirationValue"]-r["reference_eto"]*r["cropCoffiecient"])<=tolerance for r in json_source),"JSON ET identity source check")
    require(all(r["motorValue"]==int(r["irrigation_needed_value"]>0) for r in json_source),"motor/needed source check")
    require(snapshot(source)==before and all(digest(project/r["path"])==r["sha256"] for r in payload["references"]),"verifier changed raw/reference")
    verify_artifacts(processed,report)
    return {"status":"passed","run_id":run_id,"source_files_verified":len(before),"reference_files_verified":len(payload["references"]),
            "records_verified":len(records_all),"field_values_verified":fields_checked,"numeric_zeros_preserved":zeros,
            "raw_unchanged":True,"no_join_or_guessed_group":True,"training_ready":False,"semantics_or_optimality_approved":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,required=True);parser.add_argument("--run-id",required=True)
    parser.add_argument("--project-root",type=Path,default=Path.cwd());parser.add_argument("--output",type=Path)
    args=parser.parse_args();result=verify(args.project_root.resolve(),args.config.resolve(),args.run_id)
    if args.output: write_json(args.output,result)
    print(json.dumps(result,ensure_ascii=False))
