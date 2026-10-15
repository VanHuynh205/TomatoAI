"""Read-only intake, evidenced grouping and gated derivative benchmark preparation.

Cleaning runs and raw data are inputs, never output directories. No model or
network operation belongs here. A technical candidate is not training approval.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path

from clean_plantexpert import digest, strict_parse, verify_artifacts, write_json


CONFIGS = {"PlantVillage": "plantvillage", "PlantExpertVQA-tomato": "plantexpert",
           "WUR": "wur", "Dryad": "dryad", "Mendeley": "mendeley"}
ROLES = {"PlantVillage": "image_benchmark_candidate", "PlantExpertVQA-tomato": "knowledge_review_only",
         "WUR": "research_only", "Dryad": "research_only", "Mendeley": "research_only",
         "UC-IPM-Tomato": "acquisition_blocked"}


@dataclass
class InventoryReport:
    registry: str
    registry_sha256: str = ""
    rights_ledger: str = ""
    rights_sha256: str = ""
    datasets: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    raw_writes: int = 0


@dataclass
class GroupReview:
    inventory_sha256: str
    records: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    counts: dict = field(default_factory=dict)
    evidence: dict = field(default_factory=dict)
    training_approved: bool = False
    split_created: bool = False


@dataclass
class SplitPolicy:
    version: str = ""
    seed: int | None = None
    ratios: dict = field(default_factory=dict)
    ordered_labels: list = field(default_factory=list)
    ordered_codes: list = field(default_factory=list)
    scope: str = ""
    benchmark_approved: bool = False
    approved_by: str = ""
    approved_at: str = ""
    labels_reviewed: bool = False
    group_review_sha256: str = ""
    approved_record_ids: list = field(default_factory=list)


@dataclass
class SplitManifest:
    status: str = "blocked"
    errors: list = field(default_factory=list)
    class_manifest: dict = field(default_factory=dict)
    assignments: list = field(default_factory=list)
    exclusions: list = field(default_factory=list)
    supports: dict = field(default_factory=dict)
    preprocessing: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)
    sha256: str = ""


def load(path):
    if not path.is_file():
        raise ValueError(f"missing artifact: {path.as_posix()}")
    return strict_parse(path, 256 * 1024 * 1024)


def below(root, relative):
    """Reject path escape and symlink/junction resolution outside the input root."""
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError(f"invalid relative path: {relative!r}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError(f"path outside input root: {relative}")
    return path


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


def raw_baseline(source, baseline, ignored=()):
    expected = {}
    for row in csv_rows(baseline):
        name = row["source_file"]
        if name in expected:
            raise ValueError(f"duplicate raw provenance: {baseline}: {name}")
        path = below(source, name)
        if not path.is_file() or path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"]:
            raise ValueError(f"raw baseline mismatch: {path}")
        expected[name] = row
    actual = set()
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in ignored for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"raw symlink requires review: {path}")
        if path.is_file():
            actual.add(relative.as_posix())
    if actual != set(expected):
        raise ValueError(f"raw file set mismatch: {source}")
    return expected


def manifest_observations(processed, baseline):
    statuses, ids = Counter(), set()
    checked_outputs = set()
    retained = 0
    for number, row in enumerate(csv_rows(processed / "manifest.csv"), 2):
        record_id = row.get("record_id")
        if not record_id or record_id in ids:
            raise ValueError(f"missing/duplicate record ID: manifest.csv:{number}")
        ids.add(record_id)
        source = row.get("source_file")
        source_hash = row.get("source_sha256", row.get("sha256"))
        if not source_hash or source not in baseline or source_hash != baseline[source]["sha256"]:
            raise ValueError(f"missing/mismatched source hash: manifest.csv:{number}: {source}")
        status = row.get("record_status", row.get("status", ""))
        if not status:
            raise ValueError(f"missing disposition: manifest.csv:{number}")
        statuses[status] += 1
        if row.get("processed_file"):
            if row["processed_file"] not in checked_outputs:
                if not below(processed, row["processed_file"]).is_file():
                    raise ValueError(f"missing processed record: {row['processed_file']}")
                checked_outputs.add(row["processed_file"])
            retained += 1
    return {"manifest_records": len(ids), "retained": retained,
            "excluded": sum(v for k, v in statuses.items() if k.startswith("excluded")),
            "quarantined": sum(v for k, v in statuses.items() if k.startswith("quarantined")),
            "needs_review": sum(v for k, v in statuses.items() if "needs_review" in k),
            "record_status_counts": dict(statuses)}


def build_inventory(registry_path: Path) -> InventoryReport:
    registry_path = registry_path.resolve()
    root = registry_path.parent
    project = root.parents[2]
    rights_path = project / "docs/development/assets-rights.json"
    result = InventoryReport(str(registry_path), rights_ledger=str(rights_path))
    try:
        registry = load(registry_path)
        result.registry_sha256 = digest(registry_path)
        rights = load(rights_path)
        result.rights_sha256 = digest(rights_path)
        assets = {a["id"]: a for a in rights["assets"]}
        if len(assets) != len(rights["assets"]):
            raise ValueError("duplicate rights asset ID")
        entries = registry["datasets"]
        if not isinstance(entries, dict) or not entries:
            raise ValueError("registry datasets must be a nonempty object")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result.errors.append(f"{registry_path} / {rights_path}: {exc}")
        return result
    for name, entry in entries.items():
        try:
            if name not in ROLES:
                raise ValueError(f"dataset role not declared: {name}")
            run = entry["current_run"]
            if not isinstance(run, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", run):
                raise ValueError("invalid current_run")
            checkpoint_path = below(root, entry["checkpoint"])
            checkpoint = load(checkpoint_path)
            report = checkpoint_path.parent
            processed = below(root, entry["processed"])
            if report.name != run or processed.name != run:
                raise ValueError(f"current_run path mismatch: {run}")
            summary_path = report / "summary.json"
            summary = load(summary_path)
            if summary.get("run_id", summary.get("run")) != run or (name != "UC-IPM-Tomato" and checkpoint.get("run_id") != run):
                raise ValueError(f"run_id mismatch: {summary_path}")
            asset = assets["dataset:" + name]
            if asset["selected_run"] != run:
                raise ValueError("rights selected_run mismatch")
            output = {"dataset": name, "selected_run": run, "role": ROLES[name],
                      "inclusion_reason": "provenance intake only; role does not confer train or advice permission",
                      "processed": str(processed), "report": str(report),
                      "summary_sha256": digest(summary_path), "registry_counts": entry["counts"],
                      "rights_asset": asset["id"], "rights": asset, "training_eligible": False,
                      "blockers": entry.get("blockers", [])}
            if name == "UC-IPM-Tomato":
                if summary.get("status") != "blocked" or summary.get("processed_documents") != 0:
                    raise ValueError("UC-IPM acquisition state changed; explicit intake review required")
                for item in load(report / "artifact-seal.json"):
                    if item["scope"] not in {"processed", "report"}:
                        raise ValueError("invalid seal scope")
                    folder = processed if item["scope"] == "processed" else report
                    if digest(below(folder, item["file"])) != item["sha256"]:
                        raise ValueError("UC-IPM artifact hash mismatch")
                output["observed"] = {"processed_documents": 0, "acquisition_items": len(checkpoint["rows"])}
                if summary["counts"] != entry["counts"]:
                    raise ValueError("UC-IPM registry count mismatch")
                output["raw_verification"] = "no acquired corpus; no collection attempted"
            else:
                config_path = report / "config.json"
                if not config_path.exists():
                    config_path = project / f"scripts/data/{CONFIGS[name]}-config.json"
                    if digest(config_path) != load(report / "fingerprint-inputs.json")["config_sha256"]:
                        raise ValueError(f"config hash mismatch: {config_path}")
                config = load(config_path)
                source = below(project, config["source_root"])
                registry_source = below(root, entry["source_root"])
                # PlantExpert baseline includes cache/intake metadata above its
                # tomato card folder, exactly as the existing cleaning config.
                if source != registry_source and not (name == "PlantExpertVQA-tomato" and registry_source == source / "disease_kb/tomato"):
                    raise ValueError("source root differs from registry scope")
                for item in load(report / "output-artifacts.json"):
                    if item["scope"] not in {"processed", "report"}:
                        raise ValueError("invalid artifact scope")
                    below(processed if item["scope"] == "processed" else report, item["path"])
                verify_artifacts(processed, report)
                reference_count = 0
                for ref_name in ("reference-inputs.json", "fingerprint-inputs.json"):
                    ref_path = report / ref_name
                    if not ref_path.exists():
                        continue
                    ref_data = load(ref_path)
                    if ref_name == "reference-inputs.json":
                        refs = list(ref_data.values()) if isinstance(ref_data, dict) else ref_data
                    else:
                        refs = ref_data.get("references", ref_data.get("inputs", []))
                    for ref in refs:
                        ref_file = below(project, ref.get("path", ref.get("source_file")))
                        if digest(ref_file) != ref["sha256"]:
                            raise ValueError(f"reference hash mismatch: {ref_file}")
                        reference_count += 1
                ignored = (".git", ".cache", "__pycache__") if name == "PlantVillage" else ()
                baseline = raw_baseline(source, report / "raw-before.csv", ignored)
                observed = manifest_observations(processed, baseline)
                count_key = {"PlantVillage": "source_images", "PlantExpertVQA-tomato": "source_cards",
                             "Dryad": "retained_table_records"}.get(name, "source_records")
                if observed["manifest_records"] != entry["counts"][count_key]:
                    raise ValueError(f"registry manifest count mismatch: {count_key}")
                summary_count = {"PlantExpertVQA-tomato": "source_card_records", "Dryad": "retained_table_records"}.get(name, "source_records")
                if observed["manifest_records"] != summary[summary_count]:
                    raise ValueError("summary manifest count mismatch")
                if "record_status_counts" in summary and observed["record_status_counts"] != summary["record_status_counts"]:
                    raise ValueError("summary disposition count mismatch")
                for k in ("retained_copies", "retained_normalized_cards", "retained_normalized_records", "retained_table_records", "retained_records"):
                    if k in entry["counts"] and observed["retained"] != entry["counts"][k]:
                        raise ValueError(f"retained count mismatch: {k}")
                for k, v in (("excluded_records", "excluded"), ("quarantined_records", "quarantined"),
                             ("needs_review_retained", "needs_review"), ("needs_review_retained_records", "needs_review")):
                    if k in entry["counts"] and entry["counts"][k] != observed[v]:
                        raise ValueError(f"disposition count mismatch: {k}")
                output.update(observed=observed, raw_source=str(source), raw_files_hash_checked=len(baseline),
                              raw_baseline_sha256=digest(report / "raw-before.csv"),
                              reference_files_hash_checked=reference_count, raw_scope_exclusions=list(ignored),
                              manifest_sha256=digest(processed / "manifest.csv"),
                              raw_verification="fresh hashes of every file named in cleaning raw-before baseline; not historical integrity before baseline",
                              review_items=len(load(report / "review-queue.json")))
                if name == "PlantVillage":
                    output["manifest_jsonl_sha256"] = digest(processed / "manifest.jsonl")
                    output["group_inputs"] = {n: digest(report / n) for n in
                                              ("near-candidates.csv", "alias-candidates.json", "group-edges.csv")}
            result.datasets.append(output)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            result.errors.append(f"{name}: {exc}")
    return result


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def investigate_metadata(inventory: InventoryReport) -> dict:
    """Replay exact source lookups; mirrored maps do not independently prove labels."""
    from clean_plantvillage import metadata, resolve_group

    result = {"errors": [], "metadata_disagreements": [], "aliases_applied": False,
              "exact_grouped_records": 0, "missing_group_records": 0}
    try:
        if inventory.errors:
            raise ValueError("inventory errors must be resolved first")
        entry, = [e for e in inventory.datasets if e["dataset"] == "PlantVillage"]
        raw = Path(entry["raw_source"])
        manifest = Path(entry["processed"]) / "manifest.jsonl"
        if digest(manifest) != entry["manifest_jsonl_sha256"]:
            raise ValueError("stale inventory manifest hash")
        maps, index, csv_records, issues = metadata(raw)
        source_files = [raw / "leaf-map.json", raw / "leaf_grouping/leaf-map.json"]
        source_files += sorted((raw / "leaf_grouping/filtered_leafmaps").glob("Tomato*.csv"))
        result.update(selected_run=entry["selected_run"], manifest_sha256=digest(manifest),
                      metadata_files={p.relative_to(raw).as_posix(): digest(p) for p in source_files},
                      mirrored_json_maps_equal=maps[0] == maps[1], metadata_issues=issues,
                      metadata_csv_records=len(csv_records),
                      limits=["JSON maps are derived mirrors of CSV, not independent annotations",
                              "exact filename lookup verifies metadata linkage, not disease labels",
                              "numeric alias candidates do not prove leaf identity"])
        used_keys, missing = set(), Counter()
        with manifest.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                label = row["label_original"]
                group, _, key, _, _ = resolve_group(label, Path(row["source_file"]).name,
                                                    row.get("variant", "color"), maps, index)
                used_keys.add((label, key))
                if group != row.get("leaf_group_id", ""):
                    result["metadata_disagreements"].append(row["record_id"])
                result["exact_grouped_records" if group else "missing_group_records"] += 1
                if not group:
                    missing[label] += 1
        result["missing_by_class"] = dict(missing)
        result["orphan_csv_records"] = sum((r["label_original"], r["lookup_key"]) not in used_keys for r in csv_records)
        if issues or result["metadata_disagreements"]:
            raise ValueError("source grouping metadata conflicts with selected manifest; review required")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result["errors"].append(str(exc))
    return result


def resolve_groups(inventory: InventoryReport, decisions: Path) -> GroupReview:
    result = GroupReview(fingerprint(asdict(inventory)))
    try:
        if inventory.errors:
            raise ValueError("inventory errors must be resolved first")
        if digest(Path(inventory.registry)) != inventory.registry_sha256 or digest(Path(inventory.rights_ledger)) != inventory.rights_sha256:
            raise ValueError("stale inventory registry/rights hash")
        entry, = [e for e in inventory.datasets if e["dataset"] == "PlantVillage"]
        processed, report = Path(entry["processed"]), Path(entry["report"])
        manifest = processed / "manifest.jsonl"
        if digest(manifest) != entry["manifest_jsonl_sha256"]:
            raise ValueError("stale inventory manifest hash")
        for name, sha in entry["group_inputs"].items():
            if digest(below(report, name)) != sha:
                raise ValueError(f"stale grouping input hash: {name}")
        decision = load(decisions)
        # No evidence-backed manual override has been supplied in this project.
        # Reject rather than silently interpreting a speculative new schema.
        if decision.get("group_assignments") or decision.get("near_reviews"):
            raise ValueError("manual grouping/near override requires a separately reviewed evidence contract")
        with manifest.open(encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream if line.strip()]
        by_id = {r["record_id"]: r for r in rows}
        if not rows or len(by_id) != len(rows):
            raise ValueError("empty/duplicate manifest record ID")
        parent = {i: i for i in by_id}

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def join(a, b):
            a, b = find(a), find(b)
            if a != b:
                parent[max(a, b)] = min(a, b)

        seen = {}
        for row in rows:
            for kind in ("leaf_group_id", "sha256", "pixel_sha256", "split_component_id"):
                value = row.get(kind)
                if value:
                    token = (kind, value)
                    if token in seen:
                        join(row["record_id"], seen[token])
                    else:
                        seen[token] = row["record_id"]
        members = defaultdict(list)
        for row in rows:
            members[find(row["record_id"])].append(row)
        aliases = {r["record_id"]: r for r in load(report / "alias-candidates.json")}
        if not set(aliases).issubset(by_id):
            raise ValueError("alias references unknown record")
        near = list(csv_rows(report / "near-candidates.csv"))
        pending_components = set()
        for pair in near:
            if pair["record_a"] not in by_id or pair["record_b"] not in by_id:
                raise ValueError("near candidate references unknown record")
            pending_components.update((find(pair["record_a"]), find(pair["record_b"])))
        component_reasons = {}
        for component, values in members.items():
            reasons = []
            for row in values:
                flags = row.get("flags")
                if not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags):
                    raise ValueError("invalid source review flags; explicit review required")
                reasons.extend("source_flag:" + flag for flag in flags)
                if row["record_status"] not in {"ready_for_split", "excluded_exact_duplicate"}:
                    reasons.append("source_status_requires_review:" + row["record_status"])
                if not row.get("processed_file") and row["record_status"] != "excluded_exact_duplicate":
                    reasons.append("source_processed_copy_missing")
            if any(not r.get("leaf_group_id") or not r.get("group_evidence") for r in values):
                reasons.append("group_evidence_missing_in_component")
            if len({r["label_original"] for r in values}) != 1:
                reasons.append("component_label_conflict")
            if component in pending_components:
                reasons.append("near_duplicate_review_pending")
            component_reasons[component] = sorted(set(reasons))
        for row in rows:
            component = find(row["record_id"])
            reasons = list(component_reasons[component])
            if row["record_id"] in aliases:
                reasons.append("alias_candidate_not_identity_evidence")
            duplicate = row.get("duplicate_of")
            if duplicate:
                canonical = by_id.get(duplicate)
                if canonical is None or canonical["label_original"] != row["label_original"] or not any(
                        row.get(k) and row[k] == canonical.get(k) for k in ("sha256", "pixel_sha256")):
                    raise ValueError(f"unverified duplicate disposition: {row['record_id']}")
            if row["record_status"].startswith("excluded"):
                if row["record_status"] != "excluded_exact_duplicate" or not duplicate:
                    raise ValueError("unsupported excluded disposition requires review")
                disposition = "excluded_exact_duplicate"
            else:
                disposition = "quarantined" if reasons else "technical_candidate"
            result.records.append({"record_id": row["record_id"], "source_file": row["source_file"],
                                   "source_sha256": row["sha256"], "pixel_sha256": row.get("pixel_sha256"),
                                   "processed_file": row["processed_file"], "label_original": row["label_original"],
                                   "leaf_group_id": row.get("leaf_group_id", ""), "group_evidence": row.get("group_evidence", []),
                                   "source_record_status": row["record_status"], "source_flags": row["flags"],
                                   "component_id": "component:" + fingerprint(sorted(r["record_id"] for r in members[component]))[:24],
                                   "disposition": disposition, "reasons": reasons, "duplicate_of": duplicate or "",
                                   "training_eligible": False})
        result.counts = {"source_records": len(rows), "dispositions": dict(Counter(r["disposition"] for r in result.records)),
                         "components": len(members), "near_pairs_pending": len(near), "alias_candidates_unapplied": len(aliases),
                         "source_missing_group": sum(not r.get("leaf_group_id") for r in rows),
                         "per_class": {label: dict(Counter(r["disposition"] for r in result.records if r["label_original"] == label))
                                       for label in sorted({r["label_original"] for r in rows})}}
        result.evidence = {"selected_run": entry["selected_run"], "manifest_sha256": entry["manifest_jsonl_sha256"],
                           "group_inputs": entry["group_inputs"], "decisions_sha256": digest(decisions),
                           "rights": entry["rights"], "limits": ["no independent image-label review", "no leaf ID inferred from filename or numeric alias", "near candidates quarantine whole components; heuristic is not proof"]}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result.records = []
        result.errors.append(str(exc))
    return result


def create_split(review: GroupReview, policy: SplitPolicy) -> SplitManifest:
    """Only a supplied, review-bound approval can produce assignments.

    Approval fields are an auditable local record, not authentication of the
    person's expertise. Synthetic approvals exercise the algorithm in tests;
    they never approve actual project data.
    """
    result = SplitManifest()
    try:
        if review.errors:
            raise ValueError("group review has errors")
        if policy.benchmark_approved is not True or policy.labels_reviewed is not True or not all(
                isinstance(x, str) and x.strip() for x in (policy.version, policy.approved_by, policy.approved_at)):
            raise ValueError("C2 benchmark/label/class order approval missing")
        if policy.group_review_sha256 != fingerprint(asdict(review)):
            raise ValueError("stale group review hash in split approval")
        if review.evidence.get("rights", {}).get("training_approved") is not True:
            raise ValueError("dataset training rights not approved")
        if type(policy.seed) is not int or policy.seed < 0:
            raise ValueError("seed must be an explicit nonnegative integer, not bool")
        splits = ("train", "validation", "test")
        if not isinstance(policy.ratios, dict) or set(policy.ratios) != set(splits) or any(
                type(x) not in (float, int) or not math.isfinite(x) or x <= 0 or x >= 1 for x in policy.ratios.values()) or not math.isclose(
                    sum(policy.ratios.values()), 1.0, abs_tol=1e-9):
            raise ValueError("split ratios must be positive finite numbers summing to one")
        labels = policy.ordered_labels
        if not isinstance(labels, list) or not labels or any(not isinstance(x, str) or not x for x in labels) or len(set(labels)) != len(labels):
            raise ValueError("approved class order is empty or duplicated")
        if policy.scope not in {"full10", "approved_pilot", "fixture-only"}:
            raise ValueError("explicit approved benchmark scope required")
        if policy.scope == "full10" and len(labels) != 10:
            raise ValueError("full10 scope requires ten approved labels")
        if policy.scope == "fixture-only" and review.evidence.get("selected_run") != "fixture-only":
            raise ValueError("fixture scope cannot approve actual project data")
        codes = policy.ordered_codes
        if not isinstance(codes, list) or (policy.scope != "fixture-only" and (
                len(codes) != len(labels) or any(not isinstance(x, str) or not x.strip() for x in codes)
                or len(set(codes)) != len(codes))):
            raise ValueError("approved ordered status codes required")
        rows = {r["record_id"]: r for r in review.records}
        approved = policy.approved_record_ids
        if not isinstance(approved, list) or not approved or len(set(approved)) != len(approved) or not set(approved).issubset(rows):
            raise ValueError("explicit unique approved record IDs required")
        selected = [rows[i] for i in approved]
        if any(r["disposition"] != "technical_candidate" or not r.get("leaf_group_id") for r in selected):
            raise ValueError("quarantined/excluded/unresolved records cannot be approved for split")
        components = defaultdict(list)
        for row in review.records:
            components[row["component_id"]].append(row)
        chosen = defaultdict(list)
        for row in selected:
            chosen[row["component_id"]].append(row)
        for component, values in chosen.items():
            if any(r["disposition"] == "quarantined" for r in components[component]) or len({r["label_original"] for r in components[component]}) != 1:
                raise ValueError("component contains unresolved or conflicting records")
            if values[0]["label_original"] not in labels:
                raise ValueError("record label absent from approved class order")
        if set(labels) != {r["label_original"] for r in selected}:
            raise ValueError("missing class support in approved records")
        assignments = []
        supports = {s: {label: 0 for label in labels} for s in splits}
        for label in labels:
            groups = [(c, v) for c, v in chosen.items() if v[0]["label_original"] == label]
            if len(groups) < 3:
                raise ValueError(f"insufficient independent component support for three splits: {label}")
            groups.sort(key=lambda item: (-len(item[1]), fingerprint([policy.seed, item[0]])))
            total = sum(len(v) for _, v in groups)
            for index, (component, values) in enumerate(groups):
                # Reserve one independent group per split before filling the
                # remaining per-class deficits. Ratios are targets, not promises
                # that indivisible groups can meet exactly.
                split = splits[index] if index < 3 else max(splits, key=lambda s: policy.ratios[s] * total - supports[s][label])
                supports[split][label] += len(values)
                for row in sorted(values, key=lambda r: r["record_id"]):
                    assignments.append({"record_id": row["record_id"], "component_id": component,
                                        "leaf_group_id": row["leaf_group_id"], "label_original": label,
                                        "class_index": labels.index(label), "source_sha256": row.get("source_sha256", row.get("sha256")),
                                        "split": split})
        result.status = "approved_derivative"
        result.assignments = sorted(assignments, key=lambda r: r["record_id"])
        result.supports = supports
        result.exclusions = [{"record_id": r["record_id"], "disposition": r["disposition"], "reason": "outside explicit approved record set"}
                             for r in review.records if r["record_id"] not in set(approved)]
        result.class_manifest = {"schema_version": "1.0", "version": policy.version, "scope": policy.scope,
                                 "ordered_labels": labels, "ordered_codes": codes,
                                 "class_to_idx": {label: i for i, label in enumerate(labels)}}
        result.class_manifest["sha256"] = fingerprint(result.class_manifest)
        result.preprocessing = {"augmentation_on": "train_only", "fit_statistics_on": "train_only",
                                "eval_transforms": "separate per approved weights recipe in S05; not applied in Phase 1",
                                "data_transformed": False}
        result.provenance = {"group_review_sha256": policy.group_review_sha256, "policy": asdict(policy),
                             "test_usage": "locked; never used for tuning or selection", "raw_writes": 0}
        result.sha256 = fingerprint(asdict(result))
    except (ValueError, KeyError, TypeError) as exc:
        return SplitManifest(errors=[str(exc)])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("data/TomatoAI/data/dataset-registry.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/data-card.json"))
    parser.add_argument("--group-decisions", type=Path)
    parser.add_argument("--split-policy", type=Path)
    args = parser.parse_args()
    if args.split_policy and not args.group_decisions:
        parser.error("--split-policy requires --group-decisions")
    output = args.output.resolve()
    # Only project artifacts are writable. Raw, sealed runs and source code
    # cannot become an accidental CLI output path.
    artifacts = args.registry.resolve().parent.parents[2] / "artifacts"
    outputs = [output]
    if args.group_decisions:
        outputs += [(output.parent / name).resolve() for name in ("metadata-investigation.json", "group-resolution.json")]
        if args.split_policy:
            outputs.append((output.parent / "split-manifest.json").resolve())
    if any(not path.is_relative_to(artifacts.resolve()) or path == artifacts.resolve() for path in outputs):
        parser.error("every output must be a file below project artifacts")
    inputs = {args.registry.resolve(), (artifacts.parent / "docs/development/assets-rights.json").resolve()}
    inputs.update(path.resolve() for path in (args.group_decisions, args.split_policy) if path)
    if len(set(outputs)) != len(outputs) or inputs.intersection(outputs):
        parser.error("output collides with an input or fixed sidecar")
    result = build_inventory(args.registry)
    protected = [Path(entry[key]).resolve() for entry in result.datasets
                 for key in ("raw_source", "processed", "report") if key in entry]
    if any(path.is_relative_to(folder) for path in outputs for folder in protected):
        parser.error("output collides with a source or sealed run")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, asdict(result))
    print(json.dumps({"datasets": len(result.datasets), "errors": result.errors, "raw_writes": result.raw_writes}))
    if result.errors:
        return 1
    if args.group_decisions:
        audit = investigate_metadata(result)
        write_json(output.parent / "metadata-investigation.json", audit)
        if audit["errors"]:
            print(json.dumps({"metadata_errors": audit["errors"]}))
            return 1
        review = resolve_groups(result, args.group_decisions)
        write_json(output.parent / "group-resolution.json", asdict(review))
        print(json.dumps({"group_counts": review.counts, "errors": review.errors}))
        if review.errors:
            return 1
        if args.split_policy:
            split = create_split(review, SplitPolicy(**load(args.split_policy)))
            write_json(output.parent / "split-manifest.json", asdict(split))
            print(json.dumps({"split_status": split.status, "errors": split.errors}))
            return 2 if split.status == "blocked" else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
