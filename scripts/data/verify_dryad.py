"""Independent read-only production checks using openpyxl; never calculate or save XLSX."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

import openpyxl
from openpyxl.formula.translate import Translator

from clean_plantexpert import digest, snapshot, verify_artifacts, write_json


def require(condition, message):
    if not condition: raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_lines(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def verify(project, config_path, run_id):
    config = read_json(config_path)
    source = project/config["source_root"]
    processed, report = [project/config[k]/run_id for k in ("processed_parent","report_parent")]
    verify_artifacts(processed,report)
    before = snapshot(source)
    payload = read_json(report/"fingerprint-inputs.json")
    require(before == payload["source"],"source hash/size mismatch")
    require(all(digest(project/r["path"]) == r["sha256"] for r in payload["references"]),"reference hash mismatch")
    ledger_list = read_lines(processed/"cell-ledger.jsonl")
    ledger = {(c["source_file"],c["source_sheet"],c["coordinate"]):c for c in ledger_list}
    require(len(ledger) == len(ledger_list),"duplicate provenance cell")
    formula_count = content_count = 0
    for name in sorted({s["file"] for s in config["tables"]}):
        formulas = openpyxl.load_workbook(source/name,data_only=False,read_only=False,keep_links=False)
        cached = openpyxl.load_workbook(source/name,data_only=True,read_only=False,keep_links=False)
        for sheet in formulas:
            # ponytail: inspect sparse serialized cells; normal mode supports merges without allocating declared grid.
            original_content = {c.coordinate:c for c in sheet._cells.values() if c.value is not None}
            cells = {k[2]:v for k,v in ledger.items() if k[:2] == (name,sheet.title)}
            retained_content = {ref:c for ref,c in cells.items() if c["formula"] is not None or c["raw_value"] is not None}
            require(set(original_content) == set(retained_content),"content cell set differs: "+name+":"+sheet.title)
            for ref, item in retained_content.items():
                original = original_content[ref]
                require(item["source_sha256"] == digest(source/name),"cell source hash mismatch")
                formula = item["formula"]
                if formula:
                    formula_count += 1
                    if formula["attributes"].get("t") == "shared":
                        base = formula["shared_base"]
                        expression = Translator("="+base["expression"],origin=base["coordinate"]).translate_formula(ref)
                    else: expression = "="+(formula["raw_expression"] or "")
                    require(original.value == expression,"formula expression mismatch: "+ref)
                    value = cached[sheet.title][ref].value
                else: value = original.value
                if item["raw_kind"] == "numeric":
                    require(value is not None and float(item["raw_value"]) == float(value),"numeric/cache mismatch: "+ref)
                else:
                    require(item["raw_value"] == value,"text/cache mismatch: "+ref)
            content_count += len(original_content)
        formulas.close(); cached.close()
    dictionary = read_json(report/"data-dictionary.json")
    manifest = read_json(processed/"manifest.json")
    manifest_by_id = {m["record_id"]:m for m in manifest}
    require(len(manifest_by_id) == len(manifest),"duplicate manifest ID")
    with (processed/"manifest.csv").open(encoding="utf-8",newline="") as stream:
        csv_manifest = list(csv.DictReader(stream))
    require([r["record_id"] for r in csv_manifest] == [r["record_id"] for r in manifest],"CSV/JSON manifest order mismatch")
    records_all, normalized_formula_count, missing_count, zero_count = [], 0, 0, 0
    for spec in config["tables"]:
        records = read_lines(processed/"tables"/(spec["id"]+".jsonl"))
        expected_rows = list(range(spec["first_row"],spec["last_row"]+1))
        require([r["source_row"] for r in records] == expected_rows,"row coverage mismatch")
        fields_dict = [d for d in dictionary if d["table"] == spec["id"]]
        require([d["field"] for d in fields_dict] == spec["columns"],"dictionary fields mismatch")
        for entry in fields_dict:
            for level in entry["header_levels"]:
                original = ledger.get((spec["file"],spec["sheet"],level["merged_anchor"]))
                require(level["value"] == (original["raw_value"] if original else None),"header provenance mismatch")
        for index,record in enumerate(records,1):
            require(record["schema_version"] == "1.0" and set(record["fields"]) == set(spec["columns"]),"record schema mismatch")
            require(record["source_file"] == spec["file"] and record["source_sheet"] == spec["sheet"],"source table mismatch")
            require(record["status"] == "needs_review;research_only" and record["training_ready"] is False,"readiness changed")
            require(all(record[k] is None for k in ("treatment_id","replicate_id","experimental_group")),"guessed experimental mapping")
            mapping = manifest_by_id[record["record_id"]]
            require(mapping["source_row"] == record["source_row"] and mapping["processed_record"] == index,"manifest row mismatch")
            require(mapping["source_sheet"] == record["source_sheet"] and mapping["source_sha256"] == digest(source/spec["file"]),"manifest source mismatch")
            require(mapping["processed_file"] == "tables/"+spec["id"]+".jsonl","manifest output mismatch")
            require(mapping["source_key"] == record["original_key"],"manifest key mismatch")
            for column,item in record["fields"].items():
                original = ledger.get((spec["file"],spec["sheet"],column+str(record["source_row"])))
                require(original is not None,"expected source cell absent")
                require(item["coordinate"] == original["coordinate"],"field coordinate mismatch")
                require(item["raw_kind"] == original["raw_kind"] and item["raw_value"] == original["raw_value"] and item["formula"] == original["formula"],"field source content mismatch")
                if item["kind"] == "formula":
                    normalized_formula_count += 1
                    require(item["value"] is None and item["cached_value"] == original["raw_value"],"formula conflated with measured value")
                elif item["kind"] == "decimal_text":
                    require(item["value"] == original["raw_value"],"numeric lexeme changed")
                    zero_count += Decimal(item["value"]) == 0
                elif item["kind"] == "boolean": require(item["value"] == (original["raw_value"].casefold() == "yes"),"status mapping mismatch")
                elif item["kind"] in ("opaque_id","calendar_date"): require(item["value"] == original["raw_value"],"ID/date altered")
                elif item["kind"] == "missing": missing_count += 1
                else: raise ValueError("invalid/unexpected normalized kind")
            records_all.append(record)
    require(len({r["record_id"] for r in records_all}) == len(records_all),"duplicate record IDs")
    summary = read_json(report/"summary.json")
    physical = len({(r["source_file"],r["source_sheet"],r["source_row"]) for r in records_all})
    require(len(records_all) == len(manifest) == summary["retained_table_records"] == 508,"record reconciliation")
    require(physical == summary["source_physical_rows"] == 253,"physical source row reconciliation")
    require(formula_count == normalized_formula_count == summary["formula_cells"] == 108,"formula reconciliation")
    require(content_count == summary["nonempty_cells"] == 3119,"content reconciliation")
    require(len(ledger_list) == summary["serialized_cells"] == 36223,"serialized cell reconciliation")
    require(missing_count == summary["missing_table_cells"] == 0,"missing reconciliation")
    require(zero_count == summary["numeric_zero_cells_preserved"] == 254,"zero reconciliation")
    for spec in config["tables"]:
        if spec["key_type"] == "calendar_date":
            dates = [r["original_key"] for r in records_all if r["record_id"].startswith("dryad:"+spec["id"]+":")]
            require(len(set(dates)) == 85 and dates == sorted(dates),"irrigation date duplication/order")
            require(dates[0] == "2024-04-01" and dates[-1] == "2024-06-24","irrigation date range")
    require(snapshot(source) == before,"verifier changed source")
    require(all(digest(project/r["path"]) == r["sha256"] for r in payload["references"]),"verifier changed references")
    verify_artifacts(processed,report)
    return {"status":"passed", "run_id":run_id,"openpyxl":openpyxl.__version__,"raw_files_verified":len(before),
            "reference_files_verified":len(payload["references"]),"independent_nonempty_cells_verified":content_count,
            "serialized_ledger_cells":len(ledger_list),"formula_and_cache_cells_verified":formula_count,
            "records_verified":len(records_all),"physical_source_rows":physical,"raw_unchanged":True,
            "no_formula_evaluation_or_workbook_save":True,"source_semantics_approved":False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root",type=Path,default=Path.cwd())
    parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--run-id",required=True)
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    result = verify(args.project_root.resolve(),args.config.resolve(),args.run_id)
    if args.output: write_json(args.output,result)
    print(json.dumps(result,ensure_ascii=False))
