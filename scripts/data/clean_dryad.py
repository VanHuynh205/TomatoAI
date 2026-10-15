"""Offline sparse XLSX derivation; no formula execution, raw edits or treatment inference."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import posixpath
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

from clean_plantexpert import digest, snapshot, verify_artifacts, write_csv, write_json

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def emit(stream, record):
    stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


def xml(data):
    # OOXML parts do not need DTD/entities. Reject before ElementTree parsing.
    if b"\x00" in data or b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("DTD/entity declarations are not allowed")
    return ET.fromstring(data)


def decimal_token(value):
    if not isinstance(value, str) or not NUMBER.fullmatch(value):
        raise ValueError("invalid numeric lexeme: " + repr(value))
    number = Decimal(value)
    if not number.is_finite():
        raise ValueError("non-finite number")
    return value  # JSON decimal text preserves original precision, scale and zero.


def coordinate(value):
    found = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]*)", value)
    if not found:
        raise ValueError("invalid cell coordinate: " + value)
    column, row = found.groups()
    index = 0
    for character in column:
        index = index * 26 + ord(character) - 64
    if index > 16384 or int(row) > 1048576:
        raise ValueError("cell outside Excel limits")
    return index, int(row)


def string_text(element):
    # Include direct text and rich text runs, excluding phonetic annotations.
    return "".join(t.text or "" for t in element.findall(NS+"t") + element.findall(NS+"r/"+NS+"t"))


def workbook(path, config):
    sheets, warnings = {}, []
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if len(infos) > config["maximum_parts"] or sum(i.file_size for i in infos) > config["maximum_zip_bytes"]:
            raise ValueError("XLSX package limit exceeded")
        names = [i.filename for i in infos]
        if len(set(names)) != len(names):
            raise ValueError("duplicate package member")
        for item in infos:
            name = PurePosixPath(item.filename)
            if name.is_absolute() or ".." in name.parts or "\\" in item.filename or item.flag_bits & 1:
                raise ValueError("unsafe/encrypted package member")
            if item.file_size > config["maximum_part_bytes"]:
                raise ValueError("XLSX part limit exceeded")
            if "vbaproject" in item.filename.casefold():
                raise ValueError("macro payload requires quarantine")
        # Audit every relationship; never fetch external links.
        for name in names:
            if name.endswith(".rels"):
                for link in xml(archive.read(name)):
                    if link.get("TargetMode") == "External":
                        warnings.append({"reason":"external_relationship_not_followed", "part":name, "target":link.get("Target")})
        strings = []
        if "xl/sharedStrings.xml" in names:
            strings = [string_text(si) for si in xml(archive.read("xl/sharedStrings.xml"))]
        relations = {r.get("Id"):r.get("Target") for r in xml(archive.read("xl/_rels/workbook.xml.rels")) if r.get("TargetMode") != "External"}
        book = xml(archive.read("xl/workbook.xml"))
        calc = book.find(NS+"calcPr")
        for sheet in book.findall(NS+"sheets/"+NS+"sheet"):
            name = sheet.get("name")
            if name in sheets:
                raise ValueError("duplicate worksheet name")
            target = relations[sheet.get(RID)]
            part = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/"+target)
            if not part.startswith("xl/") or part not in names:
                raise ValueError("worksheet target outside package")
            root = xml(archive.read(part))
            cells, bases = {}, {}
            for element in root.findall(NS+"sheetData/"+NS+"row/"+NS+"c"):
                ref = element.get("r")
                coordinate(ref)
                if ref in cells or len(cells) >= config["maximum_cells"]:
                    raise ValueError("duplicate cell/cell limit")
                value_element, formula_element = element.find(NS+"v"), element.find(NS+"f")
                raw_v = None if value_element is None else value_element.text
                cell_type = element.get("t", "n")
                kind, value = "missing", None
                if cell_type == "s" and raw_v is not None:
                    index = int(raw_v)
                    if index < 0 or index >= len(strings): raise ValueError("shared string index invalid")
                    kind, value = "text", strings[index]
                elif cell_type == "inlineStr":
                    inline = element.find(NS+"is")
                    kind, value = ("text", string_text(inline)) if inline is not None else ("missing", None)
                elif raw_v is not None:
                    kind, value = {"n":"numeric", "b":"boolean", "e":"error", "str":"text", "d":"date"}.get(cell_type, "unknown"), raw_v
                    if kind == "numeric": decimal_token(value)
                formula = None
                if formula_element is not None:
                    formula = {"raw_expression":formula_element.text, "attributes":dict(formula_element.attrib), "shared_base":None}
                    if formula_element.get("t") == "shared" and formula_element.text:
                        group = formula_element.get("si")
                        if group in bases: raise ValueError("duplicate shared formula base")
                        bases[group] = {"coordinate":ref, "expression":formula_element.text, "range":formula_element.get("ref")}
                cells[ref] = {"coordinate":ref, "xml_attributes":dict(element.attrib), "raw_v":raw_v,
                              "raw_kind":kind, "raw_value":value, "formula":formula,
                              "raw_cell_xml":ET.tostring(element, encoding="unicode")}
            for cell in cells.values():
                formula = cell["formula"]
                if formula and formula["attributes"].get("t") == "shared":
                    group = formula["attributes"].get("si")
                    if group not in bases: raise ValueError("shared formula base missing")
                    formula["shared_base"] = bases[group]
            dimension = root.find(NS+"dimension")
            merges = [m.get("ref") for m in root.findall(NS+"mergeCells/"+NS+"mergeCell")]
            sheets[name] = {"cells":cells, "dimension_declared":dimension.get("ref") if dimension is not None else None,
                            "merged_ranges":merges, "part":part}
    return sheets, {"file":path.name, "parts":len(infos), "uncompressed_bytes":sum(i.file_size for i in infos),
                    "calculation_properties":dict(calc.attrib) if calc is not None else {}, "warnings":warnings}


def nonempty(cell):
    return cell["formula"] is not None or cell["raw_value"] is not None


def normalize(cell, field_type):
    result = {k:cell[k] for k in ("coordinate", "raw_kind", "raw_value", "formula")}
    result.update({"value":None, "kind":"missing", "operations":[]})
    if cell["formula"] is not None:
        result.update(kind="formula", cached_kind=cell["raw_kind"], cached_value=cell["raw_value"])
        result["operations"] = ["separate_formula_and_unverified_cache_no_evaluation"]
        return result
    if cell["raw_value"] is None: return result
    value = cell["raw_value"]
    if field_type == "opaque_id":
        if cell["raw_kind"] != "text": raise ValueError("ID must be original text")
        result.update(kind="opaque_id", value=value)
    elif field_type == "calendar_date":
        # Source contains textual ISO dates, not Excel serials; do not infer epoch/timezone.
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value): raise ValueError("non-ISO date")
        result.update(kind="calendar_date", value=date.fromisoformat(value).isoformat())
        result["operations"] = ["validate_ISO_calendar_date_no_timezone"]
    elif field_type == "irrigation_status":
        if value.casefold() not in ("yes", "no"): raise ValueError("unknown irrigation status")
        result.update(kind="boolean", value=value.casefold() == "yes")
        result["operations"] = ["explicit_Yes_No_boolean_mapping"]
    else:
        if cell["raw_kind"] not in ("numeric", "text"): raise ValueError("invalid numeric cell kind")
        result.update(kind="decimal_text", value=decimal_token(value))
        if cell["raw_kind"] == "text": result["operations"] = ["parse_numeric_text_preserve_lexeme"]
    return result


def header(sheet, ref):
    column, row = coordinate(ref)
    anchor = ref
    for merged in sheet["merged_ranges"]:
        start, end = merged.split(":") if ":" in merged else (merged,merged)
        left, top = coordinate(start); right, bottom = coordinate(end)
        if left <= column <= right and top <= row <= bottom:
            anchor = start
            break
    cell = sheet["cells"].get(anchor)
    return {"source_cell":ref, "merged_anchor":anchor, "value":cell["raw_value"] if cell else None}


def table(spec, sheet, source_hash, processed):
    for ref, expected in spec["header_guards"].items():
        if header(sheet,ref)["value"] != expected: raise ValueError("header mismatch: "+spec["id"]+" "+ref)
    dictionary = []
    for column in spec["columns"]:
        levels = [header(sheet, column+str(r)) for r in spec["header_rows"]]
        kind = spec["key_type"] if column == spec["key"] else "irrigation_status" if column == spec.get("status_column") else "numeric"
        units = [u for level in levels for u in re.findall(r"\(([^()]*)\)", level["value"] or "")]
        dictionary.append({"table":spec["id"], "source_file":spec["file"], "sheet":spec["sheet"], "field":column,
                           "header_levels":levels, "expected_kind":kind, "unit_status":"source_header_retained_semantics_needs_review",
                           "unit_tokens_from_header":units, "unit_conversion":False,
                           "type_note":"formulas keep cache separately; missing is null; numeric values are decimal strings"})
    records, manifest, queue = [], [], []
    counts, operations, ids, values, ranges = Counter(), Counter(), defaultdict(list), defaultdict(list), {}
    previous_date = None
    for row in range(spec["first_row"],spec["last_row"]+1):
        record_id = "dryad:"+spec["id"]+":"+str(row)
        fields, flags = {}, ["treatment_replicate_group_mapping_unverified"]
        for entry in dictionary:
            ref = entry["field"]+str(row)
            cell = sheet["cells"].get(ref, {"coordinate":ref,"raw_kind":"missing","raw_value":None,"formula":None})
            try:
                fields[entry["field"]] = normalize(cell, entry["expected_kind"])
            except ValueError as error:
                fields[entry["field"]] = {**cell, "kind":"invalid_retained", "value":None, "operations":[]}
                flags.append("invalid_cell_retained:"+ref)
                queue.append({"reason":"invalid_cell_retained", "record_id":record_id, "coordinate":ref, "error":str(error)})
            item = fields[entry["field"]]
            counts[item["kind"]] += 1; operations.update(item["operations"])
            if item["kind"] == "formula":
                flags.append("formula_cache_unverified")
                if item["cached_value"] is None: flags.append("formula_cache_missing")
            elif item["kind"] == "missing": flags.append("missing_retained:"+ref)
            if item["kind"] == "decimal_text":
                number = Decimal(item["value"])
                if number == 0: counts["zero_numeric_preserved"] += 1
                extent = ranges.setdefault(entry["field"], [number,number])
                extent[0] = min(extent[0],number); extent[1] = max(extent[1],number)
        key = fields[spec["key"]]["value"]
        ids[key].append(row)
        if spec["key_type"] == "calendar_date" and key:
            if previous_date and key <= previous_date: flags.append("date_not_strictly_increasing")
            previous_date = key
        fingerprint = json.dumps({k:[v["raw_kind"],v["raw_value"]] for k,v in fields.items() if k != spec["key"]},sort_keys=True)
        values[fingerprint].append(row)
        records.append({"schema_version":"1.0", "record_id":record_id, "source_file":spec["file"],
                        "source_sha256":source_hash, "source_sheet":spec["sheet"], "source_row":row,
                        "original_key":key, "treatment_id":None, "replicate_id":None, "experimental_group":None,
                        "status":"needs_review;research_only", "training_ready":False, "fields":fields,
                        "flags":sorted(set(flags))})
        manifest.append({"record_id":record_id, "source_file":spec["file"], "source_sha256":source_hash,
                         "source_sheet":spec["sheet"], "source_row":row, "source_key":key,
                         "processed_file":"tables/"+spec["id"]+".jsonl", "processed_record":len(records),
                         "status":"needs_review;research_only", "transformations":dict(Counter(op for v in fields.values() for op in v["operations"]))})
    for key, rows in ids.items():
        if len(rows)>1: queue.append({"reason":"duplicate_original_key_retained", "table":spec["id"],"key":key,"rows":rows})
    for rows in values.values():
        if len(rows)>1: queue.append({"reason":"repeated_measurement_vector_retained", "table":spec["id"],"rows":rows,"action":"verify context; repetition is not automatically an error"})
    for reason in ("treatment_replicate_group_mapping_unverified", "unit_semantics_unverified"):
        queue.append({"reason":reason,"table":spec["id"],"source_rows":[spec["first_row"],spec["last_row"]], "affected_records":len(records), "action":"review source metadata/article; no guessed mapping or conversion"})
    with (processed/"tables"/(spec["id"]+".jsonl")).open("w",encoding="utf-8") as stream:
        for record in records: emit(stream,record)
    summary = {"table":spec["id"],"source_file":spec["file"],"sheet":spec["sheet"],"source_rows":[spec["first_row"],spec["last_row"]],
               "retained_records":len(records),"needs_review_records":len(records),"excluded_records":0,"quarantined_records":0,
               "field_counts":dict(counts),"operations":dict(operations),"numeric_ranges_audit_only":{k:list(map(str,v)) for k,v in ranges.items()},
               "flags_overlapping":dict(Counter(f for r in records for f in r["flags"]))}
    return summary, records, manifest, queue, dictionary


def run(config_path, project):
    project = project.resolve(); config = json.loads(config_path.read_text(encoding="utf-8"))
    source = (project/config["source_root"]).resolve()
    parents = [(project/config[k]).resolve() for k in ("processed_parent","report_parent")]
    if not source.is_dir() or not source.is_relative_to(project): raise ValueError("source must exist inside project")
    for parent in parents:
        if not parent.is_relative_to(project) or parent == project or "raw" in parent.relative_to(project).parts or parent == source or parent.is_relative_to(source) or source.is_relative_to(parent):
            raise ValueError("output overlaps source or escapes project")
    if parents[0] == parents[1] or parents[0].is_relative_to(parents[1]) or parents[1].is_relative_to(parents[0]):
        raise ValueError("output roots must be disjoint")
    before = snapshot(source)
    inputs = [{"path":p,"sha256":digest(project/p)} for p in [config["intake_manifest"]]+config["reference_inputs"]]
    intake = json.loads((project/config["intake_manifest"]).read_text(encoding="utf-8-sig"))
    expected = [{"source_file":PurePosixPath(r["relative_path"].replace("\\","/")).relative_to(source.name).as_posix(),
                 "bytes":r["bytes"],"sha256":r["sha256"]} for r in intake["files"] if r["dataset"] == source.name]
    if sorted(expected,key=lambda r:r["source_file"]) != before: raise ValueError("source differs from intake manifest")
    actual = {r["source_file"] for r in before}
    if actual != {s["file"] for s in config["tables"]} | {"README.md"}: raise ValueError("unexpected/missing source files")
    hashes = {r["source_file"]:r["sha256"] for r in before}
    payload = {"source":before,"references":inputs,"config_sha256":digest(config_path),"python":platform.python_version(),
               "code_sha256":digest(Path(__file__)),"helper_sha256":digest(Path(__file__).with_name("clean_plantexpert.py"))}
    run_id = "dryad-"+hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16]
    processed, report = [p/run_id for p in parents]
    if processed.exists() or report.exists():
        if not (report/"output-artifacts.json").exists(): raise ValueError("partial run retained; review checkpoint, do not overwrite")
        verify_artifacts(processed,report)
        print(json.dumps({"status":"idempotent_existing_verified","run_id":run_id}))
        return json.loads((report/"summary.json").read_text(encoding="utf-8"))
    processed.mkdir(parents=True); report.mkdir(parents=True); (processed/"tables").mkdir()
    write_json(report/"checkpoint.json", {"status":"started","run_id":run_id,"training_ready":False})
    try:
        write_csv(report/"raw-before.csv",before,["source_file","bytes","sha256"])
        write_json(report/"fingerprint-inputs.json",payload)
        books, package_meta = {}, []
        for name in sorted({s["file"] for s in config["tables"]}):
            books[name], meta = workbook(source/name,config); package_meta.append(meta)
            if set(books[name]) != {s["sheet"] for s in config["tables"] if s["file"] == name}:
                raise ValueError("unconfigured worksheet; review required")
        tables, records_all, manifest, queue, dictionary = [], [], [], [], []
        used = defaultdict(set)
        for spec in config["tables"]:
            sheet = books[spec["file"]][spec["sheet"]]
            results = table(spec,sheet,hashes[spec["file"]],processed)
            summary, records, mapping, pending, fields = results
            tables.append(summary); records_all.extend(records); manifest.extend(mapping); queue.extend(pending); dictionary.extend(fields)
            used[(spec["file"],spec["sheet"])].update(c+str(r) for c in spec["columns"] for r in spec["header_rows"]+list(range(spec["first_row"],spec["last_row"]+1)))
        inventory, unmapped = [], []
        with (processed/"cell-ledger.jsonl").open("w",encoding="utf-8") as ledger:
            for name, sheets in books.items():
                for sheet_name, sheet in sheets.items():
                    content = [c for c in sheet["cells"].values() if nonempty(c)]
                    for ref,cell in sheet["cells"].items():
                        emit(ledger,{"source_file":name,"source_sha256":hashes[name],"source_sheet":sheet_name,**cell})
                        if nonempty(cell) and ref not in used[(name,sheet_name)]:
                            unmapped.append({"source_file":name,"source_sheet":sheet_name,**cell})
                    extent = [coordinate(c["coordinate"]) for c in content]
                    inventory.append({"file":name,"sheet":sheet_name,"dimension_declared":sheet["dimension_declared"],
                        "serialized_cells":len(sheet["cells"]),"nonempty_cells":len(content),
                        "formatting_blank_cells":len(sheet["cells"])-len(content),
                        "content_max_column":max(c for c,r in extent),"content_max_row":max(r for c,r in extent),
                        "merged_ranges":sheet["merged_ranges"],"formula_cells":sum(c["formula"] is not None for c in content),
                        "formula_cache_missing":sum(c["formula"] is not None and c["raw_value"] is None for c in content),
                        "blank_omission_proof":"every serialized cell inspected; all nonempty outside tables retained in unmapped-cells.json; no full-grid allocation"})
        for item in unmapped:
            queue.append({"reason":"unmapped_nonempty_cell_retained","source_file":item["source_file"],"sheet":item["source_sheet"],"coordinate":item["coordinate"],"raw_value":item["raw_value"],"action":"retain in ledger; do not trim whitespace away"})
        for meta in package_meta: queue.extend(meta["warnings"])
        queue.extend([
            {"reason":"formula_caches_not_recalculated_or_verified_current","affected_cells":sum(s["formula_cells"] for s in inventory),"action":"verify against documented computations separately; no execution in this pipeline"},
            {"reason":"quality_unit_conflicts","details":"README solids °Brix; average headers %. Article methods VC mg/100g and sugar mg/g; several sheet headers %. No unit conversion.","action":"verify per-field scale and units from author/source"},
            {"reason":"nutrient_proportion_scale_unverified","details":"Proportion headers % include fractional-looking values. Keep exact numbers; no multiplication/division by 100.","action":"confirm original scale"},
            {"reason":"irrigation_meter_timing_unverified","details":"Daily volume and meter reading may refer to different sampling times; no enforced same-row difference.","action":"verify measurement timing before consistency correction"},
            {"reason":"cross_table_join_and_independence_unverified","details":"Exact Code collisions are candidates only; T1-1, T1-1-1 and four irrigation blocks do not establish a treatment crosswalk.","action":"obtain verified table/plant/replicate mapping; no join or random row split"},
            {"reason":"fruit_mass_is_not_seasonal_yield","details":"Fresh fruit weight(g) is sample-level; no supported seasonal yield conversion.","action":"retain original meaning; no optimization targets"}
        ])
        keys = defaultdict(list)
        for r in records_all:
            if r["record_id"].split(":")[1].startswith("irrigation"): continue
            keys[r["original_key"]].append({"table":r["record_id"].split(":")[1],"row":r["source_row"]})
        collisions = [{"original_key":k,"occurrences":v,"mapping_status":"candidate_only_no_join"} for k,v in keys.items() if len(v)>1]
        write_json(report/"cross-table-key-candidates.json",collisions)
        write_json(report/"unmapped-cells.json",unmapped)
        write_json(report/"worksheet-inventory.json",inventory)
        write_json(report/"package-inventory.json",package_meta)
        write_json(report/"tables.json",tables); write_json(report/"data-dictionary.json",dictionary)
        write_json(report/"review-queue.json",queue)
        write_json(report/"transformation-log.json",[{"table":t["table"],"cell_operations":t["operations"],"headers":"source levels with merged anchors; column-letter field keys; raw cell ledger retained"} for t in tables])
        write_csv(processed/"manifest.csv",manifest,list(manifest[0]))
        write_json(processed/"manifest.json",manifest)
        after = snapshot(source)
        write_csv(report/"raw-after.csv",after,["source_file","bytes","sha256"])
        equal = before == after and all(digest(project/i["path"]) == i["sha256"] for i in inputs)
        physical = len({(r["source_file"],r["source_sheet"],r["source_row"]) for r in records_all})
        summary = {"dataset":"Dryad","run_id":run_id,"created_utc":datetime.now(timezone.utc).isoformat(),
            "status":"cleaned_technical;needs_review;research_only","training_ready":False,"mvp_dependency":False,
            "doi":config["doi"],"license_declared":config["license_declared"],"source_files":len(before),
            "source_bytes":sum(r["bytes"] for r in before),"workbooks":len(books),"worksheets":len(inventory),"derived_tables":len(tables),
            "source_physical_rows":physical,"retained_table_records":len(records_all),"needs_review_records":len(records_all),
            "excluded_records":0,"quarantined_records":0,"serialized_cells":sum(i["serialized_cells"] for i in inventory),
            "nonempty_cells":sum(i["nonempty_cells"] for i in inventory),"formatting_blank_cells":sum(i["formatting_blank_cells"] for i in inventory),
            "formula_cells":sum(i["formula_cells"] for i in inventory),"formula_cache_missing":sum(i["formula_cache_missing"] for i in inventory),
            "missing_table_cells":sum(t["field_counts"].get("missing",0) for t in tables),
            "invalid_table_cells":sum(t["field_counts"].get("invalid_retained",0) for t in tables),
            "numeric_zero_cells_preserved":sum(t["field_counts"].get("zero_numeric_preserved",0) for t in tables),
            "review_items":len(queue),"review_reasons":dict(Counter(q["reason"] for q in queue)),
            "cross_table_key_candidates":len(collisions),"unmapped_nonempty_cells":len(unmapped),
            "raw_integrity":"all_sha256_equal_to_intake_and_before" if equal else "FAILED","reference_inputs_unchanged":equal,
            "environment":{"python":sys.version,"executable":sys.executable,"platform":platform.platform(),"dependencies":"stdlib only; existing helper"},
            "invocation":sys.argv,"no_formula_execution_join_split_imputation_scaling_training":True}
        write_json(report/"summary.json",summary)
        write_json(report/"checkpoint.json",{"status":"technical_complete_review_pending","run_id":run_id,"training_ready":False,"research_only":True,
            "blockers":["treatment/replicate/block crosswalk","per-field units and proportion scale","formula cache freshness","meter measurement timing","cross-table independence; agronomic review"],
            "next_action":"review queue with source evidence; Mendeley only in separately authorized session; no official planning import"})
        if not equal: raise ValueError("source/reference integrity failed")
        artifacts = [{"scope":scope,"path":p.relative_to(root).as_posix(),"sha256":digest(p)} for scope,root in (("processed",processed),("report",report)) for p in sorted(root.rglob("*")) if p.is_file()]
        write_json(report/"output-artifacts.json",artifacts)
        print(json.dumps({"status":"complete",**summary},ensure_ascii=False))
        return summary
    except Exception as error:
        write_json(report/"checkpoint.json",{"status":"partial_failed_retained","run_id":run_id,"error":str(error),"training_ready":False})
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--project-root",type=Path,default=Path.cwd())
    args = parser.parse_args()
    run(args.config.resolve(),args.project_root)
