"""Read-only raw audit -> versioned tomato copies, manifests and review queues.

No model, split, augmentation, resize, crop, relabel or network operation.
Pillow decodes one image at a time. Near hash samples original pixels, and is
only an unvalidated candidate heuristic, never a deduplication decision.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import unicodedata
import warnings
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import PIL
from PIL import Image


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(row[k], ensure_ascii=False) if isinstance(row.get(k), (list, dict)) else row.get(k, "") for k in fields})


def key(name):
    return unicodedata.normalize("NFC", Path(name).stem).strip().casefold()


def leaf(value):
    text = str(value).strip() if value is not None else ""
    if not text or text.casefold() in {"nan", "none", "null", "inf", "infinity"}:
        return None
    try:
        number = Decimal(text)
        if number.is_finite():
            return format(number.normalize(), "f")
    except (InvalidOperation, ValueError):
        # Group identifiers are opaque IDs, not measured quantities. The source
        # also has prefixed IDs (e.g. OCT_563.0); zero is not missing.
        return text
    return None


def snapshot(root):
    result = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in {".git", ".cache", "__pycache__"} for part in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Source symlink requires review: {rel}")
        if path.is_file():
            result.append({"source_file": rel.as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return result


def metadata(root):
    maps = []
    issues = []
    for name in ("leaf-map.json", "leaf_grouping/leaf-map.json"):
        with (root / name).open(encoding="utf-8-sig") as f:
            original = json.load(f)
        if not isinstance(original, dict):
            raise ValueError(f"Invalid map object: {name}")
        normalized = defaultdict(set)
        for source_key, entries in original.items():
            if not isinstance(entries, list) or not isinstance(source_key, str):
                issues.append({"source_file": name, "source_record": str(source_key), "reason": "invalid_map_schema"})
                continue
            for entry in entries:
                if not isinstance(entry, str) or ":::" not in entry:
                    issues.append({"source_file": name, "source_record": source_key, "reason": "invalid_map_value"})
                    continue
                label, leaf_raw = entry.rsplit(":::", 1)
                leaf_id = leaf(leaf_raw)
                if leaf_id is None:
                    issues.append({"source_file": name, "source_record": source_key, "reason": "invalid_leaf_id"})
                    continue
                # JSON keys already have the extension removed; do NOT Path.stem them.
                normalized[unicodedata.normalize("NFC", source_key).strip().casefold()].add((label, leaf_id))
        maps.append(normalized)
    csv_index = defaultdict(list)
    csv_rows = []
    for path in sorted((root / "leaf_grouping/filtered_leafmaps").glob("Tomato*.csv")):
        rel = path.relative_to(root).as_posix()
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ["File Name", "Leaf #"]:
                issues.append({"source_file": rel, "source_record": "header", "reason": "unexpected_csv_header"})
                continue
            for row_number, row in enumerate(reader, 2):
                leaf_id = leaf(row.get("Leaf #"))
                name = row.get("File Name")
                if None in row or not name or leaf_id is None:
                    issues.append({"source_file": rel, "source_record": str(row_number), "reason": "invalid_csv_row"})
                    continue
                record = {"label_original": path.stem, "name": name, "lookup_key": key(name), "leaf_id": leaf_id, "source_file": rel, "source_record": str(row_number)}
                csv_rows.append(record)
                csv_index[(path.stem, key(name))].append(record)
    return maps, csv_index, csv_rows, issues


def resolve_group(label, filename, variant, maps, csv_index):
    source_name = filename.split("___", 1)[-1]
    lookup = key(source_name)
    method = "casefold_nfc_stem_lookup"
    # Only the documented segmented suffix, never a filename fallback leaf.
    if variant == "segmented" and lookup.endswith("_final_masked"):
        lookup = lookup.removesuffix("_final_masked")
        method = "documented_segmented_suffix_lookup"
    claims = [{n for c, n in m.get(lookup, set()) if c == label} for m in maps]
    refs = csv_index.get((label, lookup), [])
    csv_claims = {r["leaf_id"] for r in refs}
    all_claims = set().union(*claims, csv_claims)
    evidence = [{"source_file": n, "source_record": lookup} for n, c in zip(("leaf-map.json", "leaf_grouping/leaf-map.json"), claims) if c]
    evidence += [{"source_file": r["source_file"], "source_record": r["source_record"]} for r in refs]
    if len(all_claims) == 1 and claims[0] == claims[1] == csv_claims:
        return label + ":::" + next(iter(all_claims)), method, lookup, evidence, []
    if all_claims:
        return "", "unresolved", lookup, evidence, ["group_metadata_conflict_or_incomplete"]
    return "", "unresolved", lookup, evidence, ["leaf_group_missing"]


def inspect_image(path):
    result = {"decode_ok": False, "image_format": "", "width": "", "height": "", "mode": "", "channels": "", "exif_keys": [], "pixel_sha256": "", "near_hash": "", "decode_error": ""}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                result["image_format"] = image.format
                image.verify()
            with Image.open(path) as image:
                image.load()
                result.update(width=image.width, height=image.height, mode=image.mode, channels=len(image.getbands()), exif_keys=sorted(image.getexif().keys()))
                h = hashlib.sha256(f"{image.mode}:{image.width}:{image.height}:".encode())
                h.update(image.tobytes())
                result["pixel_sha256"] = h.hexdigest()
                # 9x8 coordinate samples of decoded original pixels; no resize.
                rgb = image.convert("RGB")
                bits = 0
                for y in range(8):
                    yy = round(y * (image.height - 1) / 7)
                    values = []
                    for x in range(9):
                        red, green, blue = rgb.getpixel((round(x * (image.width - 1) / 8), yy))
                        values.append(299 * red + 587 * green + 114 * blue)
                    for a, b in zip(values, values[1:]):
                        bits = (bits << 1) | int(a > b)
                result["near_hash"] = f"{bits:016x}"
                result["decode_ok"] = True
    except Exception as error:
        result["decode_error"] = type(error).__name__ + ": " + str(error)
    return result


class Components:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def join(self, a, b):
        self.parent[self.find(b)] = self.find(a)


def near_candidates(rows, components, radius, limit):
    # r+1 non-overlapping blocks: any <=r bit changes leave one block exact.
    buckets = defaultdict(list)
    hashes = {}
    parts = radius + 1
    boundaries = [64 * i // parts for i in range(parts + 1)]
    pairs = []
    scanned = 0
    truncated = False
    for i, row in enumerate(rows):
        if not row["decode_ok"]:
            continue
        number = int(row["near_hash"], 16)
        candidates = set()
        for part in range(parts):
            start, end = boundaries[part:part + 2]
            candidates.update(buckets[(part, (number >> start) & ((1 << (end - start)) - 1))])
        for j in sorted(candidates):
            if rows[j]["pixel_sha256"] == row["pixel_sha256"]:
                continue
            if components.find(i) == components.find(j):
                continue  # Already inseparable by evidenced leaf/exact/variant.
            distance = (number ^ hashes[j]).bit_count()
            if distance <= radius:
                if len(pairs) >= limit:
                    truncated = True
                    break
                pairs.append({"record_a": rows[j]["record_id"], "record_b": row["record_id"], "distance": distance, "component_a": rows[j]["split_component_id"], "component_b": row["split_component_id"], "status": "needs_review", "action": "compare_originals; do_not_delete_or_join_from_hash_alone"})
        if truncated:
            break
        hashes[i] = number
        for part in range(parts):
            start, end = boundaries[part:part + 2]
            buckets[(part, (number >> start) & ((1 << (end - start)) - 1))].append(i)
        scanned += 1
    return pairs, scanned, truncated


def verify_artifacts(processed, report):
    artifacts = json.loads((report / "output-artifacts.json").read_text(encoding="utf-8"))
    actual = {(scope, p.relative_to(root).as_posix()) for scope, root in (("processed", processed), ("report", report)) for p in root.rglob("*") if p.is_file() and p.name != "output-artifacts.json"}
    if actual != {(r["scope"], r["path"]) for r in artifacts}:
        raise ValueError("Existing output file set changed; refusing overwrite")
    for row in artifacts:
        path = (processed if row["scope"] == "processed" else report) / row["path"]
        if sha256(path) != row["sha256"]:
            raise ValueError(f"Existing output hash mismatch: {row['path']}")


def run(config_path, project_root, run_tag=""):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    roots = []
    for name in ("source_root", "processed_root", "report_root"):
        path = (project_root / config[name]).resolve()
        if not path.is_relative_to(project_root) or path == project_root:
            raise ValueError(f"Path outside project: {name}")
        roots.append(path)
    source, processed_base, report_base = roots
    for a, b in ((source, processed_base), (source, report_base), (processed_base, report_base)):
        if a.is_relative_to(b) or b.is_relative_to(a):
            raise ValueError("Source, processed and report roots must be disjoint")
    if not re.fullmatch(r"[a-zA-Z0-9_-]*", run_tag):
        raise ValueError("Unsafe run tag")
    radius, limit = config["near_hash_radius"], config["near_pair_limit"]
    if not isinstance(radius, int) or not 0 <= radius <= 8 or not isinstance(limit, int) or limit < 1:
        raise ValueError("Invalid near candidate budget")
    print("Hashing source files before audit...", flush=True)
    before = snapshot(source)
    pipeline_hash = sha256(Path(__file__))
    fingerprint = hashlib.sha256(json.dumps([before, config, pipeline_hash, PIL.__version__, sys.version], sort_keys=True).encode()).hexdigest()
    run_id = "pv-" + fingerprint[:16] + ("-" + run_tag if run_tag else "")
    processed, report = processed_base / run_id, report_base / run_id
    if processed.exists() or report.exists():
        if not (report / "summary.json").exists():
            raise ValueError("Incomplete checkpoint exists; use a new --run-tag, do not overwrite")
        verify_artifacts(processed, report)
        summary = json.loads((report / "summary.json").read_text(encoding="utf-8"))
        if summary["raw_integrity"] != "all_sha256_equal":
            raise ValueError("Prior run incomplete; use a new --run-tag")
        if snapshot(source) != before:
            raise ValueError("Source changed during reuse verification")
        print(json.dumps({"status": "reused_verified", "run_id": run_id, "report": str(report), "processed": str(processed)}))
        return summary
    report.mkdir(parents=True, exist_ok=False)
    processed.mkdir(parents=True, exist_ok=False)
    save_csv(report / "raw-before.csv", before, ["source_file", "bytes", "sha256"])
    save_json(report / "config.json", config)
    save_json(report / "checkpoint.json", {"run_id": run_id, "status": "in_progress", "scope": "PlantVillage only", "pipeline_sha256": pipeline_hash})
    maps, csv_index, csv_rows, issues = metadata(source)
    source_inventory = {r["source_file"]: r for r in before}
    rows, aliases = [], []
    variants = sorted(p.name for p in (source / "raw").iterdir() if p.is_dir())
    for variant in variants:
        for folder in sorted((source / "raw" / variant).iterdir()):
            if not folder.is_dir() or not folder.name.startswith("Tomato"):
                continue
            for path in sorted(folder.rglob("*")):
                if not path.is_file():
                    continue
                rel = path.relative_to(source).as_posix()
                record_id = "pv:" + rel
                group, method, lookup, evidence, flags = resolve_group(folder.name, path.name, variant, maps, csv_index)
                if folder.name not in config["labels"]:
                    flags.append("label_not_in_mapping")
                image = inspect_image(path)
                if not image["decode_ok"]:
                    flags.append("image_decode_error")
                elif image["image_format"] not in {"JPEG", "PNG"}:
                    flags.append("unsupported_image_format")
                elif path.suffix.casefold() not in ({".jpg", ".jpeg"} if image["image_format"] == "JPEG" else {".png"}):
                    flags.append("extension_format_mismatch")
                if image["decode_ok"] and (image["mode"] != "RGB" or image["width"] != 256 or image["height"] != 256):
                    flags.append("mode_or_dimensions_need_review")
                row = {"schema_version": config["schema_version"], "record_id": record_id, "source_file": rel, "source_record": path.name, "source_uuid": path.name.split("___", 1)[0] if "___" in path.name else "", "label_original": folder.name, "status_code": config["labels"].get(folder.name, ""), "variant": variant, **source_inventory[rel], **image, "lookup_key": lookup, "leaf_group_id": group, "group_method": method, "group_evidence": evidence, "flags": flags, "duplicate_of": "", "split_component_id": "", "processed_file": "", "record_status": "", "ready_for_training": False}
                rows.append(row)
                if folder.name == "Tomato___Target_Spot" and lookup.startswith("com.g_tgs_fl ") and not group:
                    candidate_key = lookup.replace("com.g_tgs_fl ", "com.g_fl ", 1)
                    candidate_refs = csv_index.get((folder.name, candidate_key), [])
                    aliases.append({"record_id": record_id, "lookup_key": lookup, "candidate_key": candidate_key, "candidate_leaf_groups": sorted({folder.name + ":::" + r["leaf_id"] for r in candidate_refs}), "source_rows": candidate_refs, "status": "needs_review", "applied": False, "reason": "systematic_prefix_difference; numeric_match_is_not_proof_of_leaf_identity"})
                if len(rows) % 2000 == 0:
                    print(f"Decoded {len(rows)} tomato records...", flush=True)
    components = Components(len(rows))
    edges = []
    seen = defaultdict(dict)
    for i, row in enumerate(rows):
        identifiers = [("leaf", row["leaf_group_id"]), ("sha256", row["sha256"])]
        if row["decode_ok"]:
            identifiers.append(("pixels", row["pixel_sha256"]))
        if re.fullmatch(r"[0-9a-fA-F-]{36}", row["source_uuid"]):
            identifiers.append(("source_uuid", row["source_uuid"].casefold()))
        for kind, value in identifiers:
            if not value:
                continue
            if value in seen[kind]:
                j = seen[kind][value]
                components.join(i, j)
                edges.append({"record_a": rows[j]["record_id"], "record_b": row["record_id"], "evidence_type": kind, "evidence_value": value})
            else:
                seen[kind][value] = i
    members = defaultdict(list)
    for i in range(len(rows)):
        members[components.find(i)].append(i)
    for indices in members.values():
        identity = min(rows[i]["record_id"] for i in indices)
        component_id = "component:" + hashlib.sha256(identity.encode()).hexdigest()[:20]
        labels = {rows[i]["label_original"] for i in indices}
        for i in indices:
            rows[i]["split_component_id"] = component_id
            if len(labels) > 1:
                rows[i]["flags"].append("cross_label_exact_or_variant_conflict")
    duplicate_groups = []
    for kind, column in (("byte_exact", "sha256"), ("decoded_pixel_exact", "pixel_sha256")):
        groups = defaultdict(list)
        for i, row in enumerate(rows):
            if row[column]:
                groups[row[column]].append(i)
        for digest, indices in groups.items():
            if len(indices) < 2:
                continue
            same_label = len({rows[i]["label_original"] for i in indices}) == 1
            canonical = min(indices, key=lambda i: (not bool(rows[i]["leaf_group_id"]), rows[i]["source_file"]))
            for i in indices:
                duplicate_groups.append({"kind": kind, "digest": digest, "record_id": rows[i]["record_id"], "canonical_record": rows[canonical]["record_id"], "same_label": same_label})
                if kind == "byte_exact" and same_label and i != canonical:
                    rows[i]["duplicate_of"] = rows[canonical]["record_id"]
    print("Finding near-duplicate candidates (review only)...", flush=True)
    pairs, near_scanned, near_truncated = near_candidates(rows, components, radius, limit)
    near_components = {p[k] for p in pairs for k in ("component_a", "component_b")}
    blocked_components = {r["split_component_id"] for r in rows if r["flags"]}
    for row in rows:
        if row["split_component_id"] in near_components:
            row["flags"].append("cross_component_near_candidate")
        if near_truncated:
            row["flags"].append("near_scan_budget_reached")
        if row["split_component_id"] in blocked_components and not row["flags"]:
            row["flags"].append("component_contains_pending_record")
        if not row["decode_ok"] or "unsupported_image_format" in row["flags"]:
            row["record_status"] = "excluded_invalid"
        elif row["duplicate_of"] and "cross_label_exact_or_variant_conflict" not in row["flags"]:
            row["record_status"] = "excluded_exact_duplicate"
        elif row["flags"]:
            row["record_status"] = "needs_review"
        else:
            row["record_status"] = "ready_for_split"
        if not row["record_status"].startswith("excluded"):
            dest = processed / "images" / row["source_file"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / row["source_file"], dest)
            if sha256(dest) != row["sha256"]:
                raise ValueError("Derived copy is not byte-identical")
            row["processed_file"] = dest.relative_to(processed).as_posix()
    used_csv = {(ref["source_file"], ref["source_record"]) for row in rows for ref in row["group_evidence"] if ref["source_file"].endswith(".csv")}
    orphans = [r for r in csv_rows if (r["source_file"], r["source_record"]) not in used_csv]
    review = [{"record_id": r["record_id"], "source_file": r["source_file"], "record_status": r["record_status"], "reasons": r["flags"], "action": "inspect_source_and_metadata; label_or_leaf_decision_needs_evidence"} for r in rows if r["flags"]]
    fields = list(rows[0]) if rows else ["record_id", "source_file", "record_status"]
    save_csv(processed / "manifest.csv", rows, fields)
    with (processed / "manifest.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    save_json(processed / "label-mapping.json", {"schema_version": config["schema_version"], "labels": config["labels"], "domain_review": "pending; source_labels_unchanged", "class_order_for_model": "not_defined_by_cleaning"})
    save_csv(processed / "group-manifest.csv", rows, ["record_id", "source_file", "label_original", "variant", "source_uuid", "leaf_group_id", "group_method", "group_evidence", "split_component_id", "record_status"])
    save_csv(processed / "benchmark-candidates.csv", [r for r in rows if r["record_status"] == "ready_for_split"], ["record_id", "source_file", "processed_file", "label_original", "status_code", "leaf_group_id", "split_component_id", "sha256"])
    save_json(report / "review-queue.json", review)
    save_json(report / "alias-candidates.json", aliases)
    save_csv(report / "metadata-issues.csv", issues, ["source_file", "source_record", "reason"])
    save_csv(report / "orphan-metadata.csv", orphans, ["label_original", "name", "lookup_key", "leaf_id", "source_file", "source_record"])
    save_csv(report / "duplicate-groups.csv", duplicate_groups, ["kind", "digest", "record_id", "canonical_record", "same_label"])
    save_csv(report / "group-edges.csv", edges, ["record_a", "record_b", "evidence_type", "evidence_value"])
    save_csv(report / "near-candidates.csv", pairs, ["record_a", "record_b", "distance", "component_a", "component_b", "status", "action"])
    print("Rehashing every source file after audit...", flush=True)
    after = snapshot(source)
    save_csv(report / "raw-after.csv", after, ["source_file", "bytes", "sha256"])
    integrity = before == after
    try:
        git_head = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_head = "unavailable"
    per_class = {}
    for label in sorted({r["label_original"] for r in rows}):
        subset = [r for r in rows if r["label_original"] == label]
        per_class[label] = {"source_records": len(subset), "decode_ok": sum(r["decode_ok"] for r in subset), "group_resolved": sum(bool(r["leaf_group_id"]) for r in subset), "distinct_evidenced_leaf_groups": len({r["leaf_group_id"] for r in subset if r["leaf_group_id"]}), **dict(Counter(r["record_status"] for r in subset))}
    summary = {"schema_version": config["schema_version"], "run_id": run_id, "created_utc": datetime.now(timezone.utc).isoformat(), "dataset": "PlantVillage-tomato", "dataset_status": "cleaned_technical; needs_review; not_training_ready", "source_url": config["source_url"], "license_declared": config["license_declared"], "git_head": git_head, "pipeline_sha256": pipeline_hash, "fingerprint": fingerprint, "environment": {"python": sys.version, "executable": sys.executable, "Pillow": PIL.__version__, "platform": platform.platform()}, "source_file_count": len(before), "source_bytes": sum(r["bytes"] for r in before), "raw_integrity": "all_sha256_equal" if integrity else "FAILED", "variants_present": variants, "source_records": len(rows), "decode_ok": sum(r["decode_ok"] for r in rows), "image_formats": dict(Counter(r["image_format"] for r in rows)), "dimensions_modes": dict(Counter(f"{r['width']}x{r['height']}:{r['mode']}" for r in rows)), "record_status_counts": dict(Counter(r["record_status"] for r in rows)), "retained_copies": sum(bool(r["processed_file"]) for r in rows), "flags_overlapping": dict(Counter(flag for r in rows for flag in set(r["flags"]))), "per_class": per_class, "grouping": {"maps_semantically_equal": dict(maps[0]) == dict(maps[1]), "csv_rows": len(csv_rows), "metadata_issues": len(issues), "orphan_csv_rows": len(orphans), "resolved_records": sum(bool(r["leaf_group_id"]) for r in rows), "alias_candidates_not_applied": len(aliases), "split_component_count": len(members)}, "near_candidates": {"method": "64-bit comparisons on 9x8 samples of original coordinates; unvalidated", "radius": radius, "pairs": len(pairs), "scanned_valid_records": near_scanned, "truncated": near_truncated, "within_evidenced_component_skipped": True}, "training_ready": False, "split_created": False, "domain_review": "not_performed", "invocation": sys.argv}
    save_json(report / "summary.json", summary)
    save_json(report / "checkpoint.json", {"run_id": run_id, "status": "complete" if integrity else "raw_integrity_failed", "next_action": "review_grouping_and_near_candidates; no_training", "pipeline_sha256": pipeline_hash})
    artifacts = []
    for scope, root in (("processed", processed), ("report", report)):
        for path in sorted(root.rglob("*")):
            if path.is_file():
                artifacts.append({"scope": scope, "path": path.relative_to(root).as_posix(), "sha256": sha256(path)})
    save_json(report / "output-artifacts.json", artifacts)
    if not integrity:
        raise ValueError("Raw bytes changed: outputs not accepted")
    print(json.dumps({"status": "complete", "run_id": run_id, "report": str(report), "processed": str(processed), "counts": summary["record_status_counts"]}))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--run-tag", default="")
    args = parser.parse_args()
    run(args.config.resolve(), args.project_root.resolve(), args.run_tag)
