"""Versioned, offline tomato KB normalization; raw, claims and IDs stay intact.

Only NFC string values and an explicit envelope are derived. Reference aliases,
taxonomy, EN advice and VI drafts are never approved or rewritten here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


TEXT = "string"
NUMBER = "number"
STRINGS = [TEXT]
SCHEMA = {
    "schema_version": TEXT, "disease_id": TEXT, "aliases": STRINGS,
    "crop": {k: TEXT for k in ("common_name", "scientific_name", "family")},
    "condition": {"common_name": TEXT, "scientific_name": "nullable_string", "alt_names": STRINGS,
                  "pathogen": {"type": TEXT, "taxonomy": {k: TEXT for k in ("kingdom", "phylum", "class", "order", "family", "genus", "species")}}},
    "issue_type": TEXT,
    "transmission": {k: STRINGS for k in ("vectors", "dispersal", "overwintering")},
    "environmental_risk": {"risk_factors": STRINGS, "temp_c_day": [NUMBER], "temp_c_night": [NUMBER],
                           "relative_humidity_pct": [NUMBER], "leaf_wetness_hours_threshold": NUMBER},
    "severity_rubric": {k: TEXT for k in ("unit", "mild", "moderate", "severe", "notes")},
    "symptoms": {k: STRINGS for k in ("leaves", "stems", "fruit", "roots", "whole_plant", "signs_microscopic_or_visible")},
    "lookalikes": [{"condition_name": TEXT, "condition_id": TEXT, "key_differences": STRINGS}],
    "management": {"cultural": STRINGS, "biological": STRINGS, "chemical": STRINGS, "notes": TEXT},
    "qa_seeds": {k: STRINGS for k in ("verification_templates", "attribute_templates", "diagnosis_templates", "counterfactual_templates", "severity_templates", "confounders")},
    "data_requirements": {"min_resolution_px": "integer", "min_roi_fraction": NUMBER, "lighting_notes": TEXT, "occlusion_notes": TEXT},
    "provenance": {"created_by": TEXT, "reviewed_by": TEXT, "created_at": TEXT, "updated_at": TEXT, "sources": STRINGS},
}
FIELDS = ["schema_version", "record_id", "source_file", "source_record", "source_sha256", "source_bytes",
          "disease_id_original", "issue_type_original", "parse_ok", "schema_ok", "technical_errors", "flags",
          "record_status", "raw_copy", "processed_file", "normalized_sha256", "transformations",
          "domain_review", "translation_review", "safe_for_advice", "ready_for_training"]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(row[k], ensure_ascii=False) if isinstance(row.get(k), (dict, list)) else row.get(k, "") for k in fields})


def snapshot(root):
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Source symlink requires review: {path}")
        if path.is_file():
            rows.append({"source_file": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    return rows


def pointer(parent, key):
    return parent + "/" + str(key).replace("~", "~0").replace("/", "~1")


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_parse(path, limit):
    if path.stat().st_size > limit:
        raise ValueError("JSON exceeds configured byte limit; retained for review")
    def invalid_constant(value):
        raise ValueError(f"Non-standard JSON constant: {value}")
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("JSON number exceeds finite float range: " + value)
        return number
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs_unique, parse_constant=invalid_constant, parse_float=finite_float)


def normalize(value, changes, location=""):
    if isinstance(value, dict):
        # Source keys remain exact: never silently collapse Unicode-equivalent keys.
        return {key: normalize(item, changes, pointer(location, key)) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item, changes, pointer(location, index)) for index, item in enumerate(value)]
    if isinstance(value, str):
        converted = unicodedata.normalize("NFC", value)
        if converted != value:
            changes.append({"source_pointer": location, "operation": "NFC_string_value", "before": value, "after": converted})
        return converted
    return value


def validate(value, schema, errors, location=""):
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            errors.append({"pointer": location or "/", "reason": "expected object"})
            return
        for key, rule in schema.items():
            if key not in value:
                errors.append({"pointer": pointer(location, key), "reason": "required field absent"})
            else:
                validate(value[key], rule, errors, pointer(location, key))
    elif isinstance(schema, list):
        if not isinstance(value, list):
            errors.append({"pointer": location, "reason": "expected array"})
        else:
            for index, item in enumerate(value):
                validate(item, schema[0], errors, pointer(location, index))
    else:
        good = ((schema == TEXT and isinstance(value, str)) or
                (schema == "nullable_string" and (value is None or isinstance(value, str))) or
                (schema == NUMBER and type(value) in (int, float)) or
                (schema == "integer" and type(value) is int))
        if not good:
            errors.append({"pointer": location, "reason": "expected " + schema, "observed": type(value).__name__})


def inventory(value, fields, record, location=""):
    empty = "null" if value is None else "empty_string" if value == "" else "empty_array" if value == [] else "empty_object" if value == {} else ""
    zero = type(value) in (int, float) and value == 0
    fields.append({"record_id": record, "source_pointer": location or "/", "type": type(value).__name__, "empty_kind": empty, "numeric_zero": zero})
    if isinstance(value, dict):
        for key, item in value.items():
            inventory(item, fields, record, pointer(location, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            inventory(item, fields, record, pointer(location, index))


def token(value):
    return unicodedata.normalize("NFC", value).replace("_", " ").strip().casefold()


def verify_artifacts(processed, report):
    expected = json.loads((report / "output-artifacts.json").read_text(encoding="utf-8"))
    actual = {(scope, path.relative_to(root).as_posix()) for scope, root in (("processed", processed), ("report", report)) for path in root.rglob("*") if path.is_file() and path != report / "output-artifacts.json"}
    if actual != {(item["scope"], item["path"]) for item in expected}:
        raise ValueError("Existing artifact set changed; refusing overwrite")
    for item in expected:
        root = processed if item["scope"] == "processed" else report
        if digest(root / item["path"]) != item["sha256"]:
            raise ValueError("Existing artifact hash changed; refusing overwrite: " + item["path"])


def run(config_path, project, run_tag=""):
    project = project.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    roots = []
    for key in ("source_root", "processed_root", "report_root"):
        relative = Path(config[key])
        root = (project / relative).resolve()
        if relative.is_absolute() or not root.is_relative_to(project) or root == project:
            raise ValueError("Paths must stay below project root")
        roots.append(root)
    source, processed_parent, report_parent = roots
    for i, a in enumerate(roots):
        for b in roots[i + 1:]:
            if a.is_relative_to(b) or b.is_relative_to(a):
                raise ValueError("Source and output roots must be disjoint")
    if any("raw" in root.relative_to(project).parts for root in roots[1:]):
        raise ValueError("Output cannot be inside raw data")
    if run_tag and not re.fullmatch(r"[a-z0-9-]{1,32}", run_tag):
        raise ValueError("Unsafe run tag")
    cards = (source / config["card_directory"]).resolve()
    if not cards.is_relative_to(source) or not cards.is_dir():
        raise ValueError("Tomato card directory missing or outside source")
    inputs = {}
    for key in ("image_label_mapping", "mapping_basis"):
        path = (project / config[key]).resolve()
        if not path.is_relative_to(project):
            raise ValueError("Reference input outside project")
        inputs[key] = {"path": config[key], "sha256": digest(path)}
    before = snapshot(source)
    if not before:
        raise ValueError("No local source files")
    script_hash = digest(Path(__file__))
    fingerprint = hashlib.sha256(json.dumps([before, config, inputs, script_hash, sys.version], sort_keys=True).encode()).hexdigest()
    run_id = "pex-" + fingerprint[:16] + ("-" + run_tag if run_tag else "")
    processed, report = processed_parent / run_id, report_parent / run_id
    if processed.exists() or report.exists():
        if not (report / "output-artifacts.json").is_file():
            raise ValueError("Incomplete checkpoint exists; inspect it and use a new --run-tag, never overwrite")
        verify_artifacts(processed, report)
        if before != snapshot(source):
            raise ValueError("Raw changed during verification")
        print(json.dumps({"status": "reused_verified", "run_id": run_id, "report": str(report)}))
        return json.loads((report / "summary.json").read_text(encoding="utf-8"))
    processed.mkdir(parents=True)
    report.mkdir(parents=True)
    write_json(report / "checkpoint.json", {"status": "in_progress", "run_id": run_id, "next_action": "inspect partial artifacts after failure; no overwrite"})
    write_csv(report / "raw-before.csv", before, ["source_file", "bytes", "sha256"])
    write_json(report / "config.json", config)
    write_json(report / "reference-inputs.json", inputs)
    image_labels = json.loads((project / config["image_label_mapping"]).read_text(encoding="utf-8"))["labels"]
    manifest, content, fields, queue = [], {}, [], []
    def flag(row, code, location, evidence, action="review source and record decision; do not auto-rewrite"):
        if code not in row["flags"]:
            row["flags"].append(code)
        queue.append({"queue_id": "pex-review:" + str(len(queue) + 1), "record_id": row["record_id"], "source_file": row["source_file"], "source_pointer": location, "reason": code, "evidence": evidence, "next_action": action, "review_status": "pending", "reviewer": None})
    for path in sorted(cards.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source).as_posix()
        copy = processed / "source-copies" / rel
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, copy)
        row = {"schema_version": config["schema_version"], "record_id": "pex:" + rel, "source_file": rel, "source_record": "/",
               "source_sha256": digest(path), "source_bytes": path.stat().st_size, "disease_id_original": None, "issue_type_original": None,
               "parse_ok": False, "schema_ok": False, "technical_errors": [], "flags": [], "record_status": "quarantined_technical",
               "raw_copy": copy.relative_to(processed).as_posix(), "processed_file": None, "normalized_sha256": None, "transformations": [],
               "domain_review": "pending", "translation_review": "not_translated", "safe_for_advice": False, "ready_for_training": False}
        manifest.append(row)
        try:
            if path.suffix.casefold() != ".json":
                raise ValueError("Unsupported card file format; source copy retained")
            original = strict_parse(path, config["max_json_bytes"])
        except (ValueError, UnicodeError, RecursionError) as error:
            row["technical_errors"].append({"pointer": "/", "reason": str(error)})
            flag(row, "parse_error", "/", str(error))
            continue
        row["parse_ok"] = True
        validate(original, SCHEMA, row["technical_errors"])
        normalized = normalize(original, row["transformations"])
        inventory(original, fields, row["record_id"])
        if isinstance(original, dict):
            row["disease_id_original"] = original.get("disease_id")
            row["issue_type_original"] = original.get("issue_type")
        if not row["technical_errors"]:
            for name in ("schema_version", "disease_id", "issue_type"):
                if not original[name].strip():
                    row["technical_errors"].append({"pointer": "/" + name, "reason": "empty identity field"})
            if original["crop"]["common_name"].casefold() != "tomato":
                row["technical_errors"].append({"pointer": "/crop/common_name", "reason": "crop is not tomato"})
            if not re.fullmatch(r"tomato\.[a-z0-9_]+\.[a-z0-9_]+", original["disease_id"]):
                row["technical_errors"].append({"pointer": "/disease_id", "reason": "unexpected ID syntax; source retained"})
            for name in ("created_at", "updated_at"):
                try:
                    if datetime.fromisoformat(original["provenance"][name].replace("Z", "+00:00")).tzinfo is None:
                        raise ValueError("timezone absent")
                except ValueError as error:
                    row["technical_errors"].append({"pointer": "/provenance/" + name, "reason": "unparseable timestamp: " + str(error)})
        row["schema_ok"] = not row["technical_errors"]
        if not row["schema_ok"]:
            flag(row, "schema_error", "/", row["technical_errors"])
            continue
        row["record_status"] = "needs_review"
        content[row["record_id"]] = normalized
        flag(row, "domain_review_unverified", "/provenance/reviewed_by", original["provenance"]["reviewed_by"])
        flag(row, "claim_sources_unverified", "/provenance/sources", original["provenance"]["sources"], "attach specific claim-to-source URL/page and applicability evidence")
        flag(row, "translation_pending", "/", "EN retained; VI labels are draft only", "review glossary before separately authorized translation")
        for location, values in (("/symptoms/leaves", original["symptoms"]["leaves"]), ("/management/cultural", original["management"]["cultural"]), ("/provenance/sources", original["provenance"]["sources"])):
            if not values or not any(v.strip() for v in values):
                flag(row, "core_content_empty_review", location, values, "check applicability; do not impute missing advice or citations")
        if original["schema_version"] != "1.0.0":
            flag(row, "source_schema_version_review", "/schema_version", original["schema_version"])
        if original["management"]["chemical"]:
            flag(row, "chemical_local_review_required", "/management/chemical", "source advice preserved; no Vietnam product, dose or withholding validation")
        pathogen = original["condition"]["pathogen"]["type"]
        if original["issue_type"] != pathogen:
            flag(row, "type_vocabulary_difference", "/condition/pathogen/type", {"issue_type": original["issue_type"], "pathogen_type": pathogen}, "distinguish vocabulary synonym from taxonomy inconsistency; preserve raw")
        if original["issue_type"] == "unknown":
            flag(row, "issue_type_unknown", "/issue_type", "unknown remains unknown")
        for checkpoint in config.get("domain_checkpoints", []):
            if path.name == checkpoint["card"]:
                flag(row, "domain_checkpoint", checkpoint["pointer"], checkpoint["reason"])
        risk = original["environmental_risk"]
        for name in ("temp_c_day", "temp_c_night", "relative_humidity_pct"):
            values = risk[name]
            if len(values) not in (0, 2) or (len(values) == 2 and values[0] > values[1]) or (name == "relative_humidity_pct" and any(v < 0 or v > 100 for v in values)):
                flag(row, "numeric_range_review", "/environmental_risk/" + name, values)
        req = original["data_requirements"]
        if req["min_resolution_px"] <= 0 or not 0 <= req["min_roi_fraction"] <= 1 or risk["leaf_wetness_hours_threshold"] < 0:
            flag(row, "numeric_range_review", "/data_requirements", req)
    by_id, by_name = defaultdict(list), defaultdict(list)
    for row in manifest:
        if row["schema_ok"]:
            by_id[row["disease_id_original"]].append(row)
            by_name[token(Path(row["source_file"]).stem)].append(row)
    for ident, rows in by_id.items():
        if len(rows) > 1:
            for row in rows:
                flag(row, "duplicate_disease_id", "/disease_id", {"id": ident, "records": [r["record_id"] for r in rows]})
    links, confounder_links = [], []
    for row in manifest:
        if not row["schema_ok"]:
            continue
        card = content[row["record_id"]]
        for index, link in enumerate(card["lookalikes"]):
            ident = link["condition_id"]
            exact = by_id.get(ident, [])
            candidates = by_name.get(token(ident.split(".")[-1]), [])
            status = "exact_reference" if len(exact) == 1 else "ambiguous_reference" if exact else "unresolved_reference"
            entry = {"record_id": row["record_id"], "source_file": row["source_file"], "source_pointer": f"/lookalikes/{index}/condition_id", "target_id_original": ident, "status": status,
                     "resolved_record_id": exact[0]["record_id"] if len(exact) == 1 else None, "candidate_record_ids": [r["record_id"] for r in candidates], "candidates_applied": False}
            links.append(entry)
            if status != "exact_reference":
                flag(row, status, entry["source_pointer"], entry)
        for index, slug in enumerate(card["qa_seeds"]["confounders"]):
            candidates = by_name.get(token(slug), [])
            entry = {"record_id": row["record_id"], "source_file": row["source_file"], "source_pointer": f"/qa_seeds/confounders/{index}", "slug_original": slug,
                     "candidate_record_ids": [r["record_id"] for r in candidates], "status": "exact_filename_slug_candidate" if len(candidates) == 1 else "unresolved_or_ambiguous_slug", "candidates_applied": False}
            confounder_links.append(entry)
            if len(candidates) != 1:
                flag(row, "confounder_slug_review", entry["source_pointer"], entry)
    mappings, glossary = [], []
    by_file = {r["source_file"]: r for r in manifest}
    for item in config["labels"]:
        row = by_file.get((Path(config["card_directory"]) / item["card"]).as_posix())
        matches = image_labels.get(item["label_original"]) == item["status_code"]
        ok = bool(row and row["schema_ok"] and matches and len(by_id[row["disease_id_original"]]) == 1)
        entry = {**item, "record_id": row["record_id"] if row else None, "disease_id_original": row["disease_id_original"] if row else None,
                 "link_status": "explicit_draft_schema_match" if ok else "mapping_needs_review", "mapping_basis": config["mapping_basis"],
                 "domain_review": "pending", "translation_review": "draft_needs_review", "approved_for_advice": False}
        mappings.append(entry)
        if row and not ok:
            flag(row, "mapping_needs_review", "/disease_id", entry)
        glossary.append({"term_id": "glossary:" + item["status_code"], "status_code": item["status_code"], "term_en": content.get(row["record_id"], {}).get("condition", {}).get("common_name") if row else None,
                         "term_vi_draft": item["name_vi_draft"], "scientific_name_original": content.get(row["record_id"], {}).get("condition", {}).get("scientific_name") if row else None,
                         "source_file": row["source_file"] if row else None, "source_pointer": "/condition", "draft_basis": config["mapping_basis"], "version": "1.0-draft", "reviewer": None, "review_status": "needs_review"})
    duplicate_groups = []
    for kind, selector in (("byte_identical", lambda r: r["source_sha256"]), ("canonical_json_identical", lambda r: hashlib.sha256(json.dumps(content.get(r["record_id"]), sort_keys=True, ensure_ascii=False).encode()).hexdigest() if r["schema_ok"] else None)):
        groups = defaultdict(list)
        for row in manifest:
            if (value := selector(row)) is not None:
                groups[value].append(row)
        for value, rows in groups.items():
            if len(rows) > 1:
                duplicate_groups.append({"kind": kind, "hash": value, "records": [r["record_id"] for r in rows], "action": "retained_all; review"})
                for row in rows:
                    flag(row, "duplicate_card_candidate", "/", duplicate_groups[-1])
    repeated = defaultdict(list)
    aliases = defaultdict(list)
    for row in manifest:
        if not row["schema_ok"]:
            continue
        card = content[row["record_id"]]
        for section in ("management", "qa_seeds"):
            for field, values in card[section].items():
                if isinstance(values, list):
                    for index, value in enumerate(values):
                        repeated[(section, field, token(value))].append({"record_id": row["record_id"], "source_pointer": f"/{section}/{field}/{index}", "text_en": value})
        for index, value in enumerate(card["aliases"]):
            aliases[token(value)].append({"record_id": row["record_id"], "source_pointer": f"/aliases/{index}", "text_en": value})
        aliases[token(card["condition"]["common_name"])].append({"record_id": row["record_id"], "source_pointer": "/condition/common_name", "text_en": card["condition"]["common_name"]})
    repeated_rows = [{"section": k[0], "field": k[1], "occurrences": v, "action": "retained; shared text is not duplicate disease card"} for k, v in repeated.items() if len(v) > 1]
    alias_collisions = [{"alias_key": k, "occurrences": v, "action": "no alias resolver approved"} for k, v in aliases.items() if len({e["record_id"] for e in v}) > 1]
    for collision in alias_collisions:
        for occurrence in collision["occurrences"]:
            flag(next(r for r in manifest if r["record_id"] == occurrence["record_id"]), "alias_collision", occurrence["source_pointer"], collision)
    for row in manifest:
        if not row["schema_ok"]:
            continue
        normalized = processed / "cards" / Path(row["source_file"]).relative_to(config["card_directory"])
        normalized.parent.mkdir(parents=True, exist_ok=True)
        write_json(normalized, {"schema_version": config["schema_version"], "record_id": row["record_id"], "content_language": "en",
                               "source": {"file": row["source_file"], "pointer": "/", "sha256": row["source_sha256"], "disease_id_original": row["disease_id_original"]},
                               "content_en": content[row["record_id"]], "normalizations": row["transformations"], "flags": row["flags"],
                               "review": {"domain": "pending", "translation": "not_translated", "safe_for_advice": False, "ready_for_training": False}})
        row["processed_file"] = normalized.relative_to(processed).as_posix()
        row["normalized_sha256"] = digest(normalized)
    write_csv(processed / "manifest.csv", manifest, FIELDS)
    with (processed / "manifest.jsonl").open("w", encoding="utf-8") as stream:
        for row in manifest:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    for name, value in (("label-knowledge-mapping.json", mappings), ("glossary-vi-draft.json", glossary)):
        write_json(processed / name, value)
    for name, value in (("review-queue.json", queue), ("reference-links.json", links), ("confounder-links.json", confounder_links), ("duplicate-groups.json", duplicate_groups), ("repeated-text.json", repeated_rows), ("alias-collisions.json", alias_collisions), ("source-schema.json", SCHEMA)):
        write_json(report / name, value)
    write_csv(report / "field-inventory.csv", fields, ["record_id", "source_pointer", "type", "empty_kind", "numeric_zero"])
    write_json(report / "quarantine.json", [{"record_id": r["record_id"], "source_file": r["source_file"], "raw_copy": r["raw_copy"], "errors": r["technical_errors"]} for r in manifest if not r["schema_ok"]])
    after = snapshot(source)
    write_csv(report / "raw-after.csv", after, ["source_file", "bytes", "sha256"])
    inputs_equal = all(digest(project / item["path"]) == item["sha256"] for item in inputs.values())
    integrity = before == after and inputs_equal and all(digest(processed / r["raw_copy"]) == r["source_sha256"] for r in manifest)
    revisions = Counter(path.read_text(encoding="utf-8").splitlines()[0] for path in source.rglob("*.metadata"))
    summary = {"schema_version": config["schema_version"], "run_id": run_id, "created_utc": datetime.now(timezone.utc).isoformat(), "dataset": "PlantExpertVQA-tomato",
               "status": "cleaned_technical; needs_review; not_training_ready", "fingerprint": fingerprint, "pipeline_sha256": script_hash,
               "environment": {"python": sys.version, "executable": sys.executable, "platform": platform.platform(), "dependencies": "stdlib only"},
               "source_url": config["source_url"], "license_declared": config["license_declared"], "cache_revision_observations": dict(revisions),
               "source_file_count_including_cache": len(before), "source_bytes_including_cache": sum(r["bytes"] for r in before), "source_card_records": len(manifest),
               "parse_ok": sum(r["parse_ok"] for r in manifest), "schema_ok": sum(r["schema_ok"] for r in manifest), "retained_source_copies": len(manifest),
               "retained_normalized_records": sum(bool(r["processed_file"]) for r in manifest), "excluded_records": 0,
               "record_status_counts": dict(Counter(r["record_status"] for r in manifest)), "flags_overlapping": dict(Counter(f for r in manifest for f in r["flags"])),
               "reference_link_counts": dict(Counter(link["status"] for link in links)), "reference_link_total": len(links), "duplicate_groups": len(duplicate_groups),
               "confounder_link_counts": dict(Counter(link["status"] for link in confounder_links)),
               "alias_collisions": len(alias_collisions), "shared_text_groups_retained": len(repeated_rows), "unicode_value_changes": sum(len(r["transformations"]) for r in manifest),
               "field_occurrences": len(fields), "empty_occurrences": dict(Counter(f["empty_kind"] for f in fields if f["empty_kind"])), "numeric_zero_occurrences_preserved": sum(f["numeric_zero"] for f in fields),
               "label_mapping_counts": dict(Counter(m["link_status"] for m in mappings)), "glossary_draft_terms": len(glossary), "review_items": len(queue),
               "raw_integrity": "all_sha256_equal" if integrity else "FAILED", "reference_inputs_unchanged": inputs_equal,
               "training_ready": False, "safe_for_advice": False, "translation_performed": False, "domain_review_performed": False, "qa_pairs_available": False, "invocation": sys.argv}
    write_json(report / "summary.json", summary)
    write_json(report / "checkpoint.json", {"run_id": run_id, "status": "technical_complete_review_pending" if integrity else "raw_integrity_failed", "next_action": "review references, taxonomy, claim sources and VI glossary; no training or official planning import", "blocked": ["domain/claim validation", "reference aliases not approved", "Vietnam chemical applicability", "translation review"], "training_ready": False})
    if not integrity:
        raise ValueError("Source or reference bytes changed; artifacts not accepted")
    artifacts = [{"scope": scope, "path": path.relative_to(root).as_posix(), "sha256": digest(path)} for scope, root in (("processed", processed), ("report", report)) for path in sorted(root.rglob("*")) if path.is_file()]
    write_json(report / "output-artifacts.json", artifacts)
    print(json.dumps({"status": "complete", "run_id": run_id, "report": str(report), "processed": str(processed), "counts": summary["record_status_counts"]}))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--run-tag", default="")
    args = parser.parse_args()
    run(args.config.resolve(), args.project_root.resolve(), args.run_tag)
