"""Versioned offline CSV/JSON derivation; preserve source, numbers and unverified semantics."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from clean_dryad import decimal_token
from clean_plantexpert import digest, pairs_unique, snapshot, verify_artifacts, write_csv, write_json


class NumberLexeme(str):
    """Marker for an exact source JSON numeric token, distinct from JSON strings."""


def emit(stream, record):
    stream.write(json.dumps(record,ensure_ascii=False,allow_nan=False)+"\n")


def parse_array(text, limit):
    def invalid(value): raise ValueError("non-standard JSON constant: "+value)
    decoder = json.JSONDecoder(parse_float=NumberLexeme,parse_int=NumberLexeme,
                               parse_constant=invalid,object_pairs_hook=pairs_unique)
    whitespace = re.compile(r"[ \t\r\n]*")
    skip = lambda index: whitespace.match(text,index).end()
    index = skip(0)
    if index >= len(text) or text[index] != "[": raise ValueError("JSON root must be array")
    index = skip(index+1); rows = []
    if index < len(text) and text[index] == "]":
        index += 1
    else:
        while True:
            if len(rows) >= limit: raise ValueError("JSON record limit")
            start = index
            value,index = decoder.raw_decode(text,index)
            rows.append((value,text[start:index],start,index))
            index = skip(index)
            if index >= len(text): raise ValueError("unterminated JSON array")
            if text[index] == "]": index += 1; break
            if text[index] != ",": raise ValueError("invalid JSON array separator")
            index = skip(index+1)
    if skip(index) != len(text): raise ValueError("trailing JSON content")
    return rows


def field(value, kind, missing):
    raw_kind = "number" if isinstance(value,NumberLexeme) else "null" if value is None else "string" if isinstance(value,str) else type(value).__name__
    result = {"raw_kind":raw_kind,"raw_value":value,"kind":"missing","value":None,"operations":[]}
    if value is None: return result
    token = unicodedata.normalize("NFC",value).strip() if isinstance(value,str) else value
    if isinstance(token,str) and not isinstance(value,NumberLexeme) and token.casefold() in missing:
        return result
    if kind == "number":
        result.update(kind="decimal_text",value=decimal_token(token))
        if raw_kind == "string": result["operations"].append("parse_numeric_text_preserve_precision")
        else: result["operations"].append("JSON_number_to_exact_decimal_text")
    elif kind == "timestamp":
        if raw_kind != "string" or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}",token):
            raise ValueError("invalid source wall-clock timestamp")
        result.update(kind="naive_datetime",value=datetime.strptime(token,"%Y-%m-%d %H:%M:%S").isoformat())
        result["operations"].append("ISO_naive_datetime_no_timezone")
    else:
        if raw_kind != "string": raise ValueError("category must be string")
        result.update(kind="category",value=token)
    if isinstance(value,str) and not isinstance(value,NumberLexeme) and token != value:
        result["operations"].append("NFC_trim_derived_value_only")
    return result


def read_source(path, config, kind):
    if path.stat().st_size > config["maximum_source_bytes"]: raise ValueError("source byte limit")
    if kind == "csv":
        rows = []
        with path.open(encoding="utf-8-sig",newline="") as stream:
            reader = csv.reader(stream,strict=True)
            headers = next(reader)
            if headers != config["csv_headers_expected"]: raise ValueError("CSV header mismatch")
            normalized = [unicodedata.normalize("NFC",h).strip() for h in headers]
            if not all(normalized) or len(set(normalized)) != len(normalized): raise ValueError("CSV header collision")
            previous = reader.line_num
            for values in reader:
                if len(rows) >= config["maximum_records"]: raise ValueError("CSV record limit")
                rows.append({"value":values,"source_line_start":previous+1,"source_line_end":reader.line_num})
                previous = reader.line_num
        return headers,normalized,rows
    text = path.read_text(encoding="utf-8-sig")
    rows = [{"value":value,"raw_json_record":raw,"source_character_start":start,"source_character_end":end}
            for value,raw,start,end in parse_array(text,config["maximum_records"])]
    return config["json_keys_expected"],config["json_keys_expected"],rows


def hypotheses(records, kind, config):
    # Diagnostic identities only: no labels, thresholds or corrections are learned/applied.
    candidates = [("ET_equals_ET0_times_Kc",
                   ["Evapotranspiration","Reference evapotranspiration","Crop Coefficient"] if kind == "csv" else ["evapotranspirationValue","reference_eto","cropCoffiecient"],
                   lambda x:x[0]-x[1]*x[2])]
    if kind == "json":
        candidates += [("needed_equals_ET_minus_moisture",["irrigation_needed_value","evapotranspirationValue","moisturePercentage"],lambda x:x[0]-(x[1]-x[2])),
                       ("needed_equals_clamped_ET_minus_moisture",["irrigation_needed_value","evapotranspirationValue","moisturePercentage"],lambda x:x[0]-max(Decimal(0),x[1]-x[2])),
                       ("motor_equals_positive_needed",["motorValue","irrigation_needed_value"],lambda x:x[0]-int(x[1]>0))]
    result = []
    tolerance = Decimal(config["numeric_hypothesis_tolerance"][kind])
    for name,keys,equation in candidates:
        matched, mismatched, skipped, residual = [],[],[],Decimal(0)
        for r in records:
            if r["status"].startswith("quarantined") or any(r["fields"].get(k,{}).get("kind") != "decimal_text" for k in keys):
                skipped.append(r["source_record"]); continue
            error = abs(equation([Decimal(r["fields"][k]["value"]) for k in keys]))
            residual = max(residual,error)
            (matched if error<=tolerance else mismatched).append(r["source_record"])
        result.append({"table":kind,"hypothesis":name,"fields":keys,"tolerance_absolute_fixed_before_audit":str(tolerance),
                       "matches":len(matched),"nonmatches":len(mismatched),"skipped":len(skipped),"max_absolute_residual":str(residual),
                       "matched_source_records":matched,"nonmatching_source_records":mismatched,
                       "status":"diagnostic_candidate_only_not_confirmed_source_formula","no_values_or_labels_changed":True})
    return result


def process(path,kind,config,processed,report):
    headers,names,rows = read_source(path,config,kind)
    source_hash = digest(path); records,manifest,queue,dictionary = [],[],[],[]
    counters, operations, missing, zeros, output_counts, ranges = Counter(),Counter(),Counter(),Counter(),Counter(),{}
    duplicates,values = defaultdict(list),defaultdict(set)
    timestamps = defaultdict(list); decreases = []; previous_time = None
    for index,(original,name) in enumerate(zip(headers,names)):
        unit = re.findall(r"\[([^\[\]]+)\]",original) if kind == "csv" else []
        dictionary.append({"table":kind,"field":name,"source_field":original,"source_index_1based":index+1 if kind=="csv" else None,
            "source_pointer_template":"/record_index/"+original if kind=="json" else None,
            "expected_kind":"timestamp" if original==config["timestamp_key"] and kind=="json" else "category" if original==config["csv_category_column"] and kind=="csv" else "number",
            "unit_explicit_header":unit,"unit_status":"explicit_header_scale_still_unverified" if unit else "unverified",
            "unit_from_name_candidate":original if kind=="json" and any(s in original.casefold() for s in ("percentage","liter","voltage","minute","kbps")) else None,
            "source_evidence":"CSV header; dataset description in mendeley-source-v3.html","unit_conversion":False,
            "role_status":"unverified_configuration_not_optimal_label" if "optimal" in original.casefold() else "unverified_actuator_or_computed_target" if original in ("motorValue","irrigation_needed_value") else "unverified_observation_or_configuration",
            "header_operations":["NFC_trim_header_only"] if name!=original else []})
    for index,row in enumerate(rows,1):
        fields,errors,flags = {},[],["research_only_semantics_and_independence_unverified"]
        value = row["value"]
        if kind=="csv" and len(value)!=len(headers): errors.append("CSV field count mismatch")
        if kind=="json" and (not isinstance(value,dict) or set(value)!=set(headers)): errors.append("JSON record key schema mismatch")
        if not errors:
            for column,entry in enumerate(dictionary):
                original = value[column] if kind=="csv" else value[entry["source_field"]]
                try: fields[entry["field"]] = field(original,entry["expected_kind"],config["missing_tokens"])
                except (ValueError,TypeError) as error:
                    errors.append(entry["field"]+": "+str(error)); continue
                item = fields[entry["field"]]; counters[item["kind"]]+=1; operations.update(item["operations"])
                values[entry["field"]].add((item["kind"],item["value"]))
                if item["kind"]=="missing": missing[entry["field"]]+=1; flags.append("missing_retained:"+entry["field"])
                elif item["kind"]=="decimal_text":
                    number = Decimal(item["value"])
                    if number==0: zeros[entry["field"]]+=1
                    extent=ranges.setdefault(entry["field"],[number,number]); extent[0]=min(extent[0],number);extent[1]=max(extent[1],number)
        provenance = {k:v for k,v in row.items() if k!="value"}
        if kind=="csv": provenance["raw_fields"]=value
        record = {"schema_version":"1.0","record_id":f"mendeley:{kind}:{index}","source_file":path.name,"source_sha256":source_hash,
                  "source_record":index,"source_pointer":"/"+str(index-1) if kind=="json" else None,
                  **provenance,"fields":fields,"errors":errors,"flags":flags,
                  "status":"quarantined_technical;research_only" if errors else "needs_review;research_only",
                  "training_ready":False,"experimental_group":None,"verified_cross_dataset_key":None}
        records.append(record)
        if errors: queue.append({"reason":"record_schema_or_type_quarantined","table":kind,"source_record":index,"errors":errors,"action":"retain source and quarantined envelope; resolve from evidence"})
        else:
            # Exact lexical values, ignoring JSON member order/formatting, are candidates only.
            signature=json.dumps({k:[v["raw_kind"],v["raw_value"]] for k,v in fields.items()},sort_keys=True,ensure_ascii=False)
            duplicates[signature].append(index)
            if kind=="json":
                timestamp=fields[config["timestamp_key"]]["value"]
                if timestamp is not None:
                    timestamps[timestamp].append(index)
                    if previous_time is not None and timestamp<previous_time: decreases.append(index)
                    previous_time=timestamp
            if kind=="csv" and fields["pH"]["kind"]=="decimal_text" and not 0<=Decimal(fields["pH"]["value"])<=14:
                flags.append("pH_outside_conventional_range_needs_review")
        output_counts[bool(errors)] += 1
        manifest.append({"record_id":record["record_id"],"source_file":path.name,"source_sha256":source_hash,"source_record":index,
                         "source_pointer":record["source_pointer"],"source_line_start":row.get("source_line_start"),"source_line_end":row.get("source_line_end"),
                         "processed_file":"quarantine/"+kind+".jsonl" if errors else "tables/"+kind+".jsonl",
                         "processed_record":output_counts[bool(errors)],
                         "status":record["status"],"transformations":dict(Counter(op for v in fields.values() for op in v["operations"]))})
    dupgroups=[{"table":kind,"source_records":positions,"basis":"exact_field_lexemes_no_row_id","approved_duplicate":False,"action":"retain all; verify acquisition context"} for positions in duplicates.values() if len(positions)>1]
    timegroups=[{"table":kind,"timestamp_naive":t,"source_records":positions,"approved_experimental_group":False,"action":"no collapse or random split; sensor/device identity unknown"} for t,positions in timestamps.items() if len(positions)>1]
    queue.extend({"reason":"exact_value_duplicates_retained",**r} for r in dupgroups)
    queue.extend({"reason":"duplicate_timestamp_retained",**r} for r in timegroups)
    queue += [{"reason":"units_and_sensor_calibration_unverified","table":kind,"source_records":"all","action":"verify units, preprocessing and calibration from author; no scaling"},
              {"reason":"experimental_independence_unverified","table":kind,"source_records":"all","action":"obtain device/plant/session IDs; retain order; no guessed grouping/split"}]
    if missing: queue.append({"reason":"missing_retained_not_imputed","table":kind,"per_field":dict(missing)})
    if decreases: queue.append({"reason":"timestamp_order_decrease_retained","table":kind,"source_records":decreases})
    with (processed/"tables"/(kind+".jsonl")).open("w",encoding="utf-8") as stream, (processed/"quarantine"/(kind+".jsonl")).open("w",encoding="utf-8") as bad:
        for r in records: emit(bad if r["errors"] else stream,r)
    if kind=="csv":
        with (processed/"tables/csv-normalized.csv").open("w",encoding="utf-8",newline="") as stream:
            writer=csv.writer(stream);writer.writerow(names)
            for r in records:
                if not r["errors"]: writer.writerow([r["fields"][name]["value"] if r["fields"][name]["value"] is not None else "" for name in names])
    diagnostic=hypotheses(records,kind,config)
    constants=[{"field":k,"distinct_normalized_values":len(v),"value":next(iter(v))[1],"role_unverified":True} for k,v in values.items() if len(v)==1]
    categories={name:dict(Counter(r["fields"].get(name,{}).get("value") for r in records if not r["errors"])) for name in names if name==config["csv_category_column"] and kind=="csv"}
    summary={"table":kind,"source_file":path.name,"source_sha256":source_hash,"source_records":len(rows),
        "retained_records":sum(not r["errors"] for r in records),"quarantined_records":sum(bool(r["errors"]) for r in records),"excluded_records":0,
        "needs_review_retained_records":sum(not r["errors"] for r in records),"source_headers":headers,"normalized_fields":names,
        "field_kind_counts":dict(counters),"missing_per_field":dict(missing),"zeros_per_field":dict(zeros),
        "numeric_ranges_audit_only":{k:list(map(str,v)) for k,v in ranges.items()},"category_counts":categories,
        "duplicate_value_groups":len(dupgroups),"duplicate_value_records":sum(len(g["source_records"]) for g in dupgroups),
        "duplicate_value_surplus":sum(len(g["source_records"])-1 for g in dupgroups),
        "unique_timestamps":len(timestamps),"duplicate_timestamp_groups":len(timegroups),"duplicate_timestamp_records":sum(len(g["source_records"]) for g in timegroups),
        "timestamp_decreases":len(decreases),"timestamp_min_max_naive":[min(timestamps),max(timestamps)] if timestamps else None,
        "constant_fields":constants,"cell_operations":dict(operations),"flags_overlapping":dict(Counter(f for r in records for f in r["flags"]))}
    return summary,manifest,queue,dictionary,diagnostic,dupgroups,timegroups


def run(config_path,project):
    project=project.resolve(); config=json.loads(config_path.read_text(encoding="utf-8"))
    source=(project/config["source_root"]).resolve()
    parents=[(project/config[k]).resolve() for k in ("processed_parent","report_parent")]
    if not source.is_dir() or not source.is_relative_to(project): raise ValueError("source must exist inside project")
    for parent in parents:
        if not parent.is_relative_to(project) or parent==project or "raw" in parent.relative_to(project).parts or parent.is_relative_to(source) or source.is_relative_to(parent):
            raise ValueError("output overlaps raw or escapes project")
    if parents[0]==parents[1] or parents[0].is_relative_to(parents[1]) or parents[1].is_relative_to(parents[0]): raise ValueError("output roots must be disjoint")
    before=snapshot(source)
    inputs=[{"path":p,"sha256":digest(project/p)} for p in [config["intake_manifest"]]+config["reference_inputs"]]
    intake=json.loads((project/config["intake_manifest"]).read_text(encoding="utf-8-sig"))
    expected=[{"source_file":Path(r["relative_path"]).relative_to(source.name).as_posix(),"bytes":r["bytes"],"sha256":r["sha256"]} for r in intake["files"] if r["dataset"]==source.name]
    if sorted(expected,key=lambda r:r["source_file"])!=before: raise ValueError("source differs from immutable intake")
    if {r["source_file"] for r in before}!={config["csv_file"],config["json_file"]}: raise ValueError("unexpected/missing source files")
    code={name:digest(Path(__file__).with_name(name)) for name in (Path(__file__).name,"clean_plantexpert.py","clean_dryad.py")}
    payload={"sources":before,"references":inputs,"code_sha256":code,"config_sha256":digest(config_path),"python":platform.python_version()}
    run_id="mendeley-"+hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16]
    processed,report=[p/run_id for p in parents]
    if processed.exists() or report.exists():
        if not (report/"output-artifacts.json").exists(): raise ValueError("partial run retained; do not overwrite checkpoint")
        verify_artifacts(processed,report)
        print(json.dumps({"status":"idempotent_existing_verified","run_id":run_id}))
        return json.loads((report/"summary.json").read_text(encoding="utf-8"))
    processed.mkdir(parents=True);report.mkdir(parents=True)
    for name in ("tables","quarantine"): (processed/name).mkdir()
    write_json(report/"checkpoint.json",{"status":"started","run_id":run_id,"training_ready":False})
    try:
        write_json(report/"fingerprint-inputs.json",payload);write_csv(report/"raw-before.csv",before,["source_file","bytes","sha256"])
        tables,manifest,queue,dictionary,diagnostic,duplicates,times,blocked=[],[],[],[],[],[],[],[]
        for kind,key in (("csv","csv_file"),("json","json_file")):
            try:
                values=process(source/config[key],kind,config,processed,report)
                for accumulator,items in zip((tables,manifest,queue,dictionary,diagnostic,duplicates,times),values):
                    if isinstance(items,dict): accumulator.append(items)
                    else: accumulator.extend(items)
            except (ValueError,UnicodeError,csv.Error,json.JSONDecodeError) as error:
                issue={"table":kind,"source_file":config[key],"source_sha256":digest(source/config[key]),"reason":"file_parse_or_schema_blocked","error":str(error),"source_records":"unknown_if_parse_failed","action":"retain raw and checkpoint; continue independent table"}
                blocked.append(issue);queue.append(issue)
                write_json(processed/"quarantine"/(kind+"-file.json"),issue)
        queue.extend([
            {"reason":"CSV_JSON_join_not_verified","details":"Different row counts; CSV has no record ID/timestamp and source says preprocessing. No row-index or approximate-value join authorized.","action":"obtain verified join keys and transformation lineage"},
            {"reason":"computed_target_leakage_risk","details":"Diagnostic identities and actuator-state relationships do not prove an experimentally optimal action.","action":"verify generating code, field units and independent outcomes before supervised use"},
            {"reason":"optimal_fields_not_ground_truth","details":"Configuration fields named optimal/min/max may be constants, not measured optimization labels.","action":"source/documented agronomic review; no advice or target promotion"},
            {"reason":"naive_timezone_and_sensor_identity_unverified","details":config["timestamp_policy"],"action":"obtain source timezone/device/session metadata; do not infer from coordinates"}])
        for name,value in (("tables.json",tables),("data-dictionary.json",dictionary),("review-queue.json",queue),("numeric-hypotheses.json",diagnostic),("duplicate-candidates.json",duplicates),("timestamp-candidates.json",times),
                           ("transformation-log.json",[{"table":t["table"],"operations":t["cell_operations"],"source_headers":t["source_headers"],"derived_headers":t["normalized_fields"]} for t in tables])):
            write_json(report/name,value)
        write_json(processed/"manifest.json",manifest)
        if manifest: write_csv(processed/"manifest.csv",manifest,list(manifest[0]))
        after=snapshot(source);write_csv(report/"raw-after.csv",after,["source_file","bytes","sha256"])
        equal=before==after and all(digest(project/i["path"])==i["sha256"] for i in inputs)
        totals={k:sum(t[k] for t in tables) for k in ("source_records","retained_records","quarantined_records","excluded_records","needs_review_retained_records")}
        summary={"dataset":"Mendeley","run_id":run_id,"created_utc":datetime.now(timezone.utc).isoformat(),
            "status":"technical_partial;needs_review;research_only" if blocked else "cleaned_technical;needs_review;research_only",
            "training_ready":False,"mvp_dependency":False,"doi":config["doi"],"license_declared":config["license_declared"],
            "source_files":len(before),"source_bytes":sum(r["bytes"] for r in before),"tables_completed":len(tables),"blocked_files":blocked,**totals,
            "raw_integrity":"all_sha256_equal_to_intake_and_before" if equal else "FAILED","reference_inputs_unchanged":equal,
            "missing_cells":sum(sum(t["missing_per_field"].values()) for t in tables),"zero_cells_preserved":sum(sum(t["zeros_per_field"].values()) for t in tables),
            "review_items":len(queue),"review_reason_counts":dict(Counter(q["reason"] for q in queue)),
            "environment":{"python":sys.version,"platform":platform.platform(),"executable":sys.executable,"dependencies":"stdlib; existing project helpers"},
            "invocation":sys.argv,"no_join_split_imputation_scaling_training_or_optimal_labels":True}
        write_json(report/"summary.json",summary)
        write_json(report/"checkpoint.json",{"status":"technical_partial_review_pending" if blocked else "technical_complete_review_pending","run_id":run_id,"training_ready":False,"research_only":True,
            "blocked_files":blocked,"blockers":["units/calibration and CSV preprocessing lineage","source formula/actuator semantics and outcome validation","timezone/device/session independence","cross-format join key absent","no domain approval of optimal/configuration claims"],
            "next_action":"review evidence; all five requested datasets now have checkpoints; Prompt 3 only if separately authorized"})
        if not equal or totals["source_records"]!=totals["retained_records"]+totals["quarantined_records"]: raise ValueError("integrity/count reconciliation failed")
        artifacts=[{"scope":scope,"path":p.relative_to(root).as_posix(),"sha256":digest(p)} for scope,root in (("processed",processed),("report",report)) for p in sorted(root.rglob("*")) if p.is_file()]
        write_json(report/"output-artifacts.json",artifacts)
        print(json.dumps(summary,ensure_ascii=False));return summary
    except Exception as error:
        write_json(report/"checkpoint.json",{"status":"partial_failed_retained","run_id":run_id,"error":str(error),"training_ready":False});raise


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,required=True);parser.add_argument("--project-root",type=Path,default=Path.cwd())
    args=parser.parse_args();run(args.config.resolve(),args.project_root)
