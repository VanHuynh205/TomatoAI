"""Offline WUR derivation. Raw immutable; separate tables; no date/treatment inference."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pdfplumber
import pypdf
from clean_plantexpert import digest, snapshot, verify_artifacts, write_csv, write_json

META = ["record_id", "source_record"]
MANIFEST = ["record_id", "source_file", "source_record", "source_line_end", "source_sha256",
            "processed_file", "processed_record", "status", "flags", "transformations"]
QUALITY = ["%time", "Flavour", "TSS", "Acid", "%Juice", "Bite", "Weight", "DMC_fruit"]


def number(text, missing):
    token = unicodedata.normalize("NFC", text).strip()
    if token.casefold() in missing:
        return "", None, "missing"
    # Decimal accepts underscores and Unicode digits; these are not source CSV numeric syntax.
    if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", token):
        raise ValueError("invalid numeric token: " + repr(text))
    try:
        value = Decimal(token)
    except InvalidOperation as error:
        raise ValueError("invalid Decimal") from error
    if not value.is_finite():
        raise ValueError("non-finite numeric token")
    return token, value, "numeric"


def headers(original, rows, relative, evidence_ok):
    result = [unicodedata.normalize("NFC", h).strip() for h in original]
    changes = []
    if relative == "Reference/TomQuality.csv" and result == QUALITY[:6] + ["Weight\tDMC_fruit"]:
        if not evidence_ok or not rows or any(len(r) != 8 for r in rows):
            raise ValueError("merged header repair lacks PDF/row-width evidence")
        result = QUALITY.copy()
        changes.append({"operation": "split_merged_header_only", "header_index_1based": 7,
                        "before": original[-1], "after": ["Weight", "DMC_fruit"], "pdf_page": 14})
    if relative == "IUACAAS/Resources.csv" and len(result) == 12 and result[7:] == [""] * 5:
        if not rows or any(len(r) != 12 or any(c.strip() for c in r[7:]) for r in rows):
            raise ValueError("trailing empty-column removal lacks all-row evidence")
        changes.append({"operation": "omit_five_proven_empty_trailing_columns", "source_indices": [8,9,10,11,12],
                        "rows_checked": len(rows), "nonempty_cells": 0, "recoverable_from_raw": True})
        result = result[:7]
    for i, h in enumerate(result):
        if i == 0 and h.casefold() == "%time":
            result[i] = "time_excel_serial"
        if not result[i] or result[i] in META:
            raise ValueError("empty/reserved header")
    if len(set(result)) != len(result):
        raise ValueError("normalized header collision")
    if not result or result[0] != "time_excel_serial":
        raise ValueError("unrecognized timestamp header")
    for i, h in enumerate(result):
        if i < len(original) and h != original[i] and not (relative == "Reference/TomQuality.csv" and i >= 6):
            changes.append({"operation": "NFC_trim_header_and_explicit_time_key", "source_index": i+1,
                            "before": original[i], "after": h})
    return result, changes


def pdf_evidence(source, report, config):
    extracted, units = [], {}
    for name in ("ReadMe.pdf", "Economics.pdf"):
        path = source / "source_files" / name
        for i, page in enumerate(pypdf.PdfReader(path).pages):
            extracted.append({"source_file": "source_files/"+name, "source_sha256": digest(path),
                              "page": i+1, "text": page.extract_text()})
    with pdfplumber.open(source / "source_files/ReadMe.pdf") as document:
        for kind, pages in config["source_pages"].items():
            units[kind] = []
            for page_number in pages:
                for table in document.pages[page_number-1].extract_tables():
                    for row in table:
                        if len(row) < 5 or not row[0] or row[0].startswith("Column"):
                            continue
                        units[kind].append({"source_heading": row[0], "description_raw": row[1],
                                            "unit_raw": row[2], "interval_raw": row[3],
                                            "dataset_raw": row[4], "source_page": page_number,
                                            "remaining_cells_raw": row[5:]})
    quality = {r["source_heading"]: r["unit_raw"] for r in units["TomQuality"]}
    peer_headers_ok = True
    for team in config["teams"]:
        if team == "Reference": continue
        with (source / "source_files" / team / "TomQuality.csv").open(encoding="utf-8-sig", newline="") as stream:
            peer_headers_ok &= [h.strip() for h in next(csv.reader(stream))] == QUALITY
    valid = (digest(source / "source_files/ReadMe.pdf") == config["readme_sha256"]
             and quality.get("Weight") == "g" and quality.get("DMC_fruit") == "%" and peer_headers_ok)
    write_json(report / "pdf-evidence.json", extracted)
    write_json(report / "source-unit-dictionary.json", units)
    return units, valid


def time_flags(current, previous, seen, interval, tolerance):
    flags = []
    if current is None:
        return ["timestamp_missing"]
    if current in seen:
        flags.append("duplicate_timestamp_retained")
    if previous is not None:
        delta = current-previous
        if delta < 0:
            flags.append("time_order_decrease_retained")
        if interval is not None and abs(delta-interval)*86400 > tolerance:
            flags.append("interval_differs_from_documented_cadence")
    return flags


def process_table(path, source, processed, report, config, units, evidence_ok, manifest_writer):
    relative = path.relative_to(source / "source_files").as_posix()
    team, kind = path.parent.name, path.stem
    source_file = path.relative_to(source).as_posix()
    source_hash = digest(path)
    if path.stat().st_size > config["maximum_csv_bytes"]:
        raise ValueError("CSV byte limit exceeded")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        original = next(reader)
        # ponytail: one source table in RAM, capped at 100 MB / 1M rows; use streaming if larger tables arrive.
        rows, lines = [], []
        for row in reader:
            if len(rows) >= config["maximum_csv_rows"]:
                raise ValueError("CSV row limit exceeded")
            rows.append(row); lines.append(reader.line_num)
    queue, changes, dictionary = [], [], []
    def review(reason, details, records=None):
        queue.append({"source_file": source_file, "reason": reason, "details": details,
                      "source_records": records, "action": "retain; resolve from source evidence before reuse"})
    try:
        names, changes = headers(original, rows, relative, evidence_ok)
    except ValueError as error:
        names = None
        review("schema_quarantined", str(error), "all")
    if names:
        for index, name in enumerate(names):
            matches = [r for r in units.get(kind, []) if r["source_heading"].strip().casefold() == name.casefold()]
            if name == "time_excel_serial":
                matches = [r for r in units.get(kind, []) if r["source_heading"].strip().casefold() == "time"]
            dictionary.append({"source_file": source_file, "column_index": index+1,
                               "source_header": original[index] if index < len(original) else None,
                               "normalized_header": name, "type": "nullable_decimal_text",
                               "source_dictionary_matches": matches, "unit_status": "documented_no_conversion" if len(matches)==1 else "needs_review",
                               "note": "Excel epoch/timezone unverified; serial retained" if index == 0 else ""})
            if index and len(matches) != 1:
                review("unit_or_alias_unresolved", {"column": name, "matching_dictionary_entries": len(matches)})
    output = processed / "tables" / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    quarantine = processed / "quarantine" / (relative + ".jsonl")
    quarantine.parent.mkdir(parents=True, exist_ok=True)
    widths = Counter(map(len, rows)); missing_counts = Counter(); missing_tokens = Counter()
    flag_counts = Counter(); transformations = Counter(); zero_counts = Counter(); ranges = {}
    previous = None; times = {}; fingerprints = {}; deltas = Counter(); retained = bad = 0
    interval = config["expected_interval_days"].get(kind)
    interval = Decimal(interval) if interval else None
    tolerance = Decimal(config["frequency_tolerance_seconds"])
    climate_path = source / "source_files" / team / "GreenhouseClimate.csv"
    time_span = None
    if climate_path.exists():
        with climate_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream); next(reader)
            serials = [Decimal(row[0].strip()) for row in reader]
        time_span = [min(serials), max(serials)]
    with output.open("w", encoding="utf-8", newline="") as stream, quarantine.open("w", encoding="utf-8") as q:
        writer = csv.writer(stream)
        if names: writer.writerow(META + names)
        for n, (raw, line) in enumerate(zip(rows, lines), 1):
            ident = f"wur:{team}:{kind}:{n:06d}"
            flags, normalized, values, operations = [], [], [], []
            error = None
            if not names:
                error = "schema_quarantined"
            elif len(raw) != (12 if relative == "IUACAAS/Resources.csv" and len(original)==12 else len(names)):
                error = "row_width_mismatch"
            else:
                try:
                    for index, cell in enumerate(raw[:len(names)]):
                        token, value, state = number(cell, config["missing_tokens"])
                        normalized.append(token); values.append(value)
                        if token != cell:
                            operations.append("missing_to_empty" if state=="missing" else "NFC_trim_numeric_lexeme")
                except ValueError as exc:
                    error = str(exc)
            if error:
                operations = []  # No cell transform is applied to quarantined rows.
                bad += 1; flags.append("quarantined_technical")
                q.write(json.dumps({"record_id": ident, "source_file": source_file, "source_record": n,
                                    "source_line_end": line, "source_sha256": source_hash,
                                    "original_cells": raw, "reason": error}, ensure_ascii=False) + "\n")
                review("quarantined_technical", error, [n])
            else:
                for index, (cell, value) in enumerate(zip(raw, values)):
                    if value is None:
                        missing_counts[names[index]] += 1
                        missing_tokens[cell] += 1
                    if value == 0: zero_counts[names[index]] += 1
                    if value is not None:
                        lo, hi = ranges.get(names[index], (value, value))
                        ranges[names[index]] = (min(lo,value), max(hi,value))
                current = values[0]
                flags.extend(time_flags(current, previous, times, interval, tolerance))
                if current is not None:
                    if previous is not None: deltas[str(current-previous)] += 1
                    if time_span and not time_span[0] <= current <= time_span[1]:
                        flags.append("timestamp_outside_own_climate_span_retained")
                    times.setdefault(current, n); previous = current
                key = hashlib.sha256(json.dumps(normalized, separators=(",", ":")).encode()).hexdigest()
                if key in fingerprints:
                    flags.append("exact_normalized_row_duplicate_retained")
                fingerprints.setdefault(key, n)
                retained += 1
                writer.writerow([ident, n] + normalized)
                if flags: review("record_temporal_or_duplicate_flag", flags, [n])
            transformations.update(operations); flag_counts.update(flags)
            manifest_writer.writerow({"record_id": ident, "source_file": source_file, "source_record": n,
                                      "source_line_end": line, "source_sha256": source_hash,
                                      "processed_file": (output if not error else quarantine).relative_to(processed).as_posix(),
                                      "processed_record": retained if not error else bad,
                                      "status": "needs_review;research_only" if not error else "quarantined_technical;research_only",
                                      "flags": json.dumps(flags), "transformations": json.dumps(dict(Counter(operations)))})
    if names:
        missing_total = sum(missing_counts.values())
        if missing_total: review("missing_values_retained", {"cells": missing_total, "per_column": dict(missing_counts)})
    review("epoch_timezone_and_experiment_scope_unverified", {"time_policy": config["time_policy"],
           "team": team, "group_basis": "source directory; not randomized replicate/treatment label", "independence": "not established"}, "all")
    summary = {"source_file": source_file, "source_sha256": source_hash, "team_directory_original": team,
               "table_kind": kind, "encoding": "utf-8-sig strict", "delimiter": ",", "original_headers": original,
               "normalized_headers": names, "original_width_counts": dict(widths), "source_header_fields": len(original),
               "normalized_data_fields": len(names) if names else 0, "source_records": len(rows),
               "retained_normalized_records": retained, "quarantined_records": bad, "excluded_records": 0,
               "needs_review_retained_records": retained, "missing_cells": dict(missing_counts),
               "missing_lexeme_counts": dict(missing_tokens), "zero_cells_preserved": dict(zero_counts),
               "numeric_ranges_audit_only": {k: [str(x) for x in v] for k,v in ranges.items()},
               "timestamp_min_max_serial": [str(min(times)),str(max(times))] if times else None,
               "delta_days_histogram": dict(deltas), "flags_overlapping": dict(flag_counts),
               "cell_transformations": dict(transformations), "header_transformations": changes,
               "processed_file": output.relative_to(processed).as_posix(), "processed_sha256": digest(output),
               "quarantine_file": quarantine.relative_to(processed).as_posix(), "quarantine_sha256": digest(quarantine)}
    return summary, queue, dictionary


def run(config_path, project):
    project = project.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source = (project / config["source_root"]).resolve()
    parents = [(project / config[k]).resolve() for k in ("processed_parent", "report_parent")]
    if not source.is_relative_to(project) or not source.is_dir():
        raise ValueError("source must exist inside project")
    for parent in parents:
        if not parent.is_relative_to(project) or parent == source or parent.is_relative_to(source) or source.is_relative_to(parent):
            raise ValueError("output overlaps source or escapes project")
    if parents[0] == parents[1] or parents[0].is_relative_to(parents[1]) or parents[1].is_relative_to(parents[0]):
        raise ValueError("processed and report roots must be disjoint")
    before = snapshot(source)
    refs = [config["intake_manifest"]] + config["reference_inputs"]
    inputs = [{"path": p, "sha256": digest(project/p)} for p in refs]
    intake = json.loads((project/config["intake_manifest"]).read_text(encoding="utf-8-sig"))
    entries = [r for r in intake["files"] if r["dataset"] == source.name]
    expected = [{"source_file": str(Path(r["relative_path"]).relative_to(source.name)).replace("\\", "/"),
                 "bytes": r["bytes"], "sha256": r["sha256"]} for r in entries]
    if sorted(expected,key=lambda x:x["source_file"]) != before:
        raise ValueError("source does not match immutable intake manifest")
    code = {Path(__file__).name: digest(Path(__file__)), "clean_plantexpert.py": digest(Path(__file__).with_name("clean_plantexpert.py"))}
    payload = {"sources": before, "inputs": inputs, "code": code, "config_sha256": digest(config_path),
               "python": platform.python_version(), "pypdf": pypdf.__version__, "pdfplumber": pdfplumber.__version__}
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    run_id = "wur-" + fingerprint[:16]
    processed, report = [p/run_id for p in parents]
    if processed.exists() or report.exists():
        if not (report/"output-artifacts.json").exists():
            raise ValueError("partial run retained; review checkpoint, do not overwrite")
        verify_artifacts(processed, report)
        print(json.dumps({"status": "idempotent_existing_verified", "run_id": run_id}))
        return json.loads((report/"summary.json").read_text(encoding="utf-8"))
    processed.mkdir(parents=True); report.mkdir(parents=True)
    write_json(report/"checkpoint.json", {"status": "started", "run_id": run_id, "training_ready": False})
    try:
        write_csv(report/"raw-before.csv", before, ["source_file", "bytes", "sha256"])
        write_json(report/"fingerprint-inputs.json", payload)
        units, evidence_ok = pdf_evidence(source, report, config)
        wanted = {"Weather/Weather.csv"} | {f"{t}/{k}.csv" for t in config["teams"] for k in config["table_kinds"]}
        actual = {p.relative_to(source/"source_files").as_posix() for p in (source/"source_files").rglob("*.csv")}
        if actual != wanted: raise ValueError("unexpected/missing source tables; manual review required")
        tables, queue, dictionary = [], [], []
        with (processed/"manifest.csv").open("w",encoding="utf-8",newline="") as stream:
            writer = csv.DictWriter(stream,fieldnames=MANIFEST); writer.writeheader()
            for relative in sorted(actual):
                table, pending, fields = process_table(source/"source_files"/relative, source, processed, report, config, units, evidence_ok, writer)
                tables.append(table); queue.extend(pending); dictionary.extend(fields)
        write_json(report/"tables.json", tables)
        schemas = {}
        duplicate_files = []
        for table in tables:
            schemas.setdefault(table["table_kind"], []).append({"source_file": table["source_file"], "headers": table["normalized_headers"]})
        for kind, variants in schemas.items():
            if len({json.dumps(v["headers"]) for v in variants}) > 1:
                queue.append({"reason": "cross_team_schema_mismatch", "table_kind": kind, "variants": variants, "action": "retain separate; no forced schema join"})
        file_groups = {}
        for item in before: file_groups.setdefault(item["sha256"], []).append(item["source_file"])
        for sha, paths in file_groups.items():
            if len(paths) > 1:
                duplicate_files.append({"sha256": sha, "source_files": paths, "action": "retained; repeated measurements not automatically invalid"})
                queue.append({"reason": "byte_identical_source_files_retained", "source_files": paths, "action": "confirm compartment/source ownership"})
        write_json(report/"duplicate-files.json", duplicate_files)
        write_json(report/"cross-team-schemas.json", schemas)
        write_json(report/"review-queue.json", queue)
        write_json(report/"data-dictionary.json", dictionary)
        write_json(report/"transformation-log.json", [{"source_file": t["source_file"], "header_operations": t["header_transformations"], "cell_operations": t["cell_transformations"]} for t in tables])
        after = snapshot(source)
        write_csv(report/"raw-after.csv", after, ["source_file", "bytes", "sha256"])
        equal = before == after and all(digest(project/r["path"]) == r["sha256"] for r in inputs)
        totals = {k: sum(t[k] for t in tables) for k in ("source_records", "retained_normalized_records", "quarantined_records", "excluded_records", "needs_review_retained_records")}
        summary = {"dataset": "WUR", "run_id": run_id, "created_utc": datetime.now(timezone.utc).isoformat(),
                   "status": "cleaned_technical;needs_review;research_only", "training_ready": False, "mvp_dependency": False,
                   "source_url": config["source_url"], "doi": config["doi"], "license_declared": config["license_declared"],
                   "source_files": len(before), "source_bytes": sum(r["bytes"] for r in before), "tables": len(tables),
                   **totals, "raw_integrity": "all_sha256_equal_to_intake_and_before" if equal else "FAILED",
                   "reference_inputs_unchanged": equal, "missing_cells": sum(sum(t["missing_cells"].values()) for t in tables),
                   "zero_cells_preserved": sum(sum(t["zero_cells_preserved"].values()) for t in tables),
                   "review_items": len(queue), "review_reason_counts": dict(Counter(q["reason"] for q in queue)),
                   "flags_overlapping": dict(sum((Counter(t["flags_overlapping"]) for t in tables),Counter())),
                   "environment": {"python": sys.version, "executable": sys.executable, "platform": platform.platform(), "pypdf": pypdf.__version__, "pdfplumber": pdfplumber.__version__},
                   "time_policy": config["time_policy"], "invocation": sys.argv,
                   "no_split_join_interpolation_imputation_scaling_training": True}
        write_json(report/"summary.json", summary)
        write_json(report/"checkpoint.json", {"status": "technical_complete_review_pending", "run_id": run_id,
                   "blocked": ["Excel epoch/timezone", "timestamp 43510 in Reference/Production", "unit aliases and source dictionary extraction", "missingness/cadence and agronomic plausibility", "experiment independence and future question/split if authorized"],
                   "training_ready": False, "research_only": True, "next_action": "manual evidence review; no MVP expansion; next dataset Dryad in separately requested session"})
        if not equal or totals["source_records"] != totals["retained_normalized_records"] + totals["quarantined_records"]:
            raise ValueError("integrity/count reconciliation failed")
        artifacts = [{"scope": scope, "path": p.relative_to(root).as_posix(), "sha256": digest(p)} for scope,root in (("processed",processed),("report",report)) for p in sorted(root.rglob("*")) if p.is_file()]
        write_json(report/"output-artifacts.json", artifacts)
        print(json.dumps({"status": "complete", "run_id": run_id, **totals}))
        return summary
    except Exception as error:
        write_json(report/"checkpoint.json", {"status": "partial_failed_retained", "run_id": run_id, "error": str(error), "training_ready": False})
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    run(args.config.resolve(), args.project_root)
