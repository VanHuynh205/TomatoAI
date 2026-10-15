"""Read-only integrity/lookup review. No cleaning, model or translation calls."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from os.path import relpath

from clean_plantexpert import digest, pairs_unique, snapshot, verify_artifacts, write_json
from clean_plantvillage import snapshot as pv_snapshot


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_unique)


def fingerprint(value):
    import hashlib
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_review(project, output):
    """Derive review artifacts from explicit, manually researched decisions.

    No advice approval, relabeling, fuzzy matching or translation occurs here.
    A fresh output version is required if inputs or decisions change.
    """
    if (output / "artifact-seal.json").exists():
        raise ValueError("sealed_review_use_new_version")
    decisions = load(output / "decisions.json")
    root = project / "data/TomatoAI/data"
    registry = load(root / "dataset-registry.json")
    entry = registry["datasets"]["PlantExpertVQA-tomato"]
    processed = root / entry["processed"]
    cards = [load(p) for p in sorted((processed / "cards").glob("*.json"))]
    originals = load(processed / "label-knowledge-mapping.json")
    by_id = {c["record_id"]: c for c in cards}
    pv = root / registry["datasets"]["PlantVillage"]["processed"]
    with (pv / "manifest.csv").open(encoding="utf-8", newline="") as stream:
        labels = sorted({r["label_original"] for r in csv.DictReader(stream)})
    if set(labels) != {m["label_original"] for m in originals}:
        raise ValueError("Current classes differ from existing explicit draft mapping")
    evidence = {k: dict(v, source_id=k, accessed=decisions["accessed"], checked_by=decisions["actor"])
                for k, v in decisions["sources"].items()}
    def refs(stem):
        return [evidence[k] for k in decisions["identity_sources"].get(stem, [])]
    matrix = []
    for item in originals:
        card = by_id[item["record_id"]]
        stem = Path(item["card"]).stem
        matrix.append({"label_original": item["label_original"], "dataset": "PlantVillage",
                       "label_source_url": evidence["pv"]["url"],
                       "label_review": "source_label_preserved; independent_image_review_pending",
                       "canonical_condition_id": item["status_code"],
                       "name_en": card["content_en"]["condition"]["common_name"],
                       "name_vi_draft": item["name_vi_draft"],
                       "agent_from_card": card["content_en"]["condition"]["scientific_name"],
                       "agent_category_derived": "oomycete" if stem == "late_blight" else card["content_en"]["issue_type"],
                       "card_id": card["record_id"], "card_path": (processed / "cards" / item["card"]).relative_to(project).as_posix(),
                       "card_file_sha256": digest(processed / "cards" / item["card"]),
                       "card_sha256": fingerprint(card), "source_sha256": card["source"]["sha256"],
                       "disease_id_original": card["content_en"]["disease_id"],
                       "relation": "candidate_pending" if stem == "mosaic_virus" else "exact_source_checked",
                       "identity_evidence": refs(stem),
                       "reason": "ToMV scientific name conflicts with TMV aliases; no automatic merge." if stem == "mosaic_virus" else "Explicit source label/card concept corroborated by cited crop/pathogen source; not image-label or expert approval.",
                       "domain_review": "pending", "translation_review": "not_translated; disease_name_draft_only",
                       "display_allowed": False, "display_condition": "identity resolved + expert-approved claim + reviewed VI + hash-bound sources + applicable context; chemicals remain blocked"})
    manifest = {"version": "tomato-classes-proposed-v1", "status": "proposed_not_training_checkpoint",
                "ordering_basis": "lexicographically sorted current PlantVillage labels; requires approval before training",
                "dataset_run": registry["datasets"]["PlantVillage"]["current_run"],
                "ordered_labels": labels, "condition_by_label": {m["label_original"]: m["canonical_condition_id"] for m in matrix}}
    manifest["sha256"] = fingerprint(manifest)
    condition_by_card = {m["card_id"]: m["canonical_condition_id"] for m in matrix}
    claims, aliases, summaries = [], [], []
    # These decisions are exact, evidence-based entries, not string heuristics.
    accepted_aliases = {("leaf_mold", "Fulvia fulva"): "mold", ("leaf_mold", "Cladosporium fulvum"): "mold"}
    blocked_aliases = {("early_blight", "target spot of tomato"): "early/target distinct pathogens",
                       ("mosaic_virus", "Tobacco Mosaic Virus on tomato"): "TMV and ToMV distinct viruses",
                       ("mosaic_virus", "Tobacco mosaic virus (TMV)"): "TMV and ToMV distinct viruses",
                       ("cercospora_leaf_spot", "Gray leaf spot"): "Stemphylium usage prevents automatic Cercospora equivalence",
                       ("healthy", "no disease"): "leaf class cannot certify whole-plant absence of disease"}
    for card in cards:
        stem = Path(card["source"]["file"]).stem
        content = card["content_en"]
        for field in ("aliases", "condition/alt_names"):
            values = content["aliases"] if field == "aliases" else content["condition"]["alt_names"]
            for index, alias in enumerate(values):
                key = (stem, alias)
                status = "accepted_identity_alias" if key in accepted_aliases else "blocked" if key in blocked_aliases else "pending"
                aliases.append({"card_id": card["record_id"], "alias_original": alias,
                                "pointer": f"/content_en/{field}/{index}", "status": status,
                                "evidence": [evidence[accepted_aliases[key]]] if key in accepted_aliases else refs(stem),
                                "reason": "historical pathogen synonym, no cross-condition merge" if key in accepted_aliases else blocked_aliases.get(key, "no explicit alias acceptance in this review; retain source unchanged"),
                                "expert_approved": False})
        card_claims = []
        for section, values in content["management"].items():
            values = [values] if isinstance(values, str) else values
            for index, text_en in enumerate(values):
                pointer = f"/content_en/management/{section}" + ("" if section == "notes" else f"/{index}")
                key = f"{stem}/{section}/{index}"
                checked = index in decisions["source_checked_claims"].get(stem, {}).get(section, [])
                partial = index in decisions["partial_claims"].get(stem, {}).get(section, [])
                hold = decisions["special_holds"].get(key)
                kind = "basic_care" if stem == "healthy" else "nonchemical_cultural" if section == "cultural" else "biological_needs_context" if section == "biological" else "chemical_or_mixed"
                if hold and ("Copper" in hold or "bleach" in hold):
                    kind = "chemical_or_mixed"
                status = "held_specific_risk" if hold else "source_checked_candidate" if checked else "partial_support_context_pending" if partial else "unverified"
                claim = {"claim_id": f"ir-claim:{stem}:{section}:{index}", "card_id": card["record_id"],
                         "canonical_condition_id": condition_by_card.get(card["record_id"]), "pointer": pointer,
                         "text_en": text_en, "text_vi": None, "kind": kind,
                         "source_sha256": card["source"]["sha256"], "card_sha256": fingerprint(card),
                         "source_check": status, "evidence": refs(stem) if checked or partial or hold else [],
                         "reason": hold or ("Authority supports principle; expert/context and VI review still pending." if checked else "Partial/absent specific support; do not infer application, duration, efficacy or local legality."),
                         "required_context": {} if checked else {"applicability": "unverified"},
                         "domain_review": "pending", "domain_reviewer": None,
                         "translation_review": "not_translated", "translation_reviewer": None,
                         "translation_source_sha256": None, "translation_claim_sha256": None,
                         "translation_sha256": None, "display_allowed": False}
                claims.append(claim)
                card_claims.append(claim)
        summaries.append({"card_id": card["record_id"], "file": stem + ".json", "issue_type_original": content["issue_type"],
                          "classifier_link": "candidate" if stem == "mosaic_virus" else "exact_source_checked" if card["record_id"] in condition_by_card else "knowledge_only_no_image_class",
                          "claims": len(card_claims), "source_checks": dict(Counter(c["source_check"] for c in card_claims)),
                          "domain_review": "pending", "translation_review": "not_translated", "safe_for_advice": False})
    bundle = {"version": decisions["version"], "class_manifest": manifest, "mapping": matrix, "cards": cards, "claims": claims,
              "fixture": False, "approval_policy": "Conservative proposed release contract; no override of sealed card review flags."}
    validate_bundle(bundle)
    queue_path = root / Path(entry["checkpoint"]).parent / "review-queue.json"
    queue = load(queue_path)
    inherited_count = len(queue)
    for claim in claims:
        queue.append({"queue_id": claim["claim_id"] + ":review", "record_id": claim["card_id"], "source_pointer": claim["pointer"],
                      "reason": claim["source_check"], "next_action": "verify applicability and domain approval, then translate/review VI; chemical claims stay hidden", "review_status": "pending", "reviewer": None})
    for number, finding in enumerate(load(output / "findings.json"), 1):
        queue.append(dict(finding, queue_id=f"ir-review:{number}", review_status="pending", reviewer=None))
    for number, alias in enumerate(aliases, 1):
        if alias["status"] != "accepted_identity_alias":
            queue.append({"queue_id": f"ir-alias:{number}", "record_id": alias["card_id"], "source_pointer": alias["pointer"],
                          "reason": alias["reason"], "alias_status": alias["status"], "review_status": "pending", "reviewer": None})
    write_json(output / "evidence.json", evidence)
    write_json(output / "mapping.json", matrix)
    write_csv(output / "mapping.csv", [{k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in m.items()} for m in matrix])
    write_json(output / "class-manifest.proposed.json", manifest)
    write_json(output / "aliases.json", aliases)
    reference_path = root / Path(entry["checkpoint"]).parent / "reference-links.json"
    write_json(output / "reference-link-review.json", {"source_path": reference_path.relative_to(project).as_posix(),
                "source_sha256": digest(reference_path), "links": [dict(r, identity_review="pending", accepted_for_lookup=False,
                reason="Exact ID resolution is technical only; unresolved aliases are not accepted by suffix/fuzzy matching.") for r in load(reference_path)]})
    write_json(output / "claim-ledger.json", claims)
    write_json(output / "card-review-summary.json", summaries)
    write_json(output / "lookup-bundle.json", bundle)
    write_json(output / "review-queue.json", {"version": decisions["version"], "inherited_queue_path": queue_path.relative_to(project).as_posix(),
                                             "inherited_sha256": digest(queue_path), "inherited_items_unchanged": inherited_count, "items": queue})
    write_json(output / "provenance.json", {"version": decisions["version"], "registry_sha256": digest(root / "dataset-registry.json"),
                                          "decisions_sha256": digest(output / "decisions.json"), "mapping_input_sha256": digest(processed / "label-knowledge-mapping.json"),
                                          "class_source_sha256": digest(pv / "manifest.csv"), "card_files": [{"path": p.relative_to(project).as_posix(), "sha256": digest(p)} for p in sorted((processed / "cards").glob("*.json"))],
                                          "change_log": ["New derivative review only; no source mapping/card/class index changed.", "9 identity links source-checked, 1 ToMV/TMV candidate held; no expert or translation approval granted."]})
    table = ["# Ma trận nhãn–kiến thức", "", "Source-checked là đối chiếu danh tính, không phải phê duyệt nhãn ảnh/chuyên môn. Tất cả tên Việt là dự thảo; 0 hướng dẫn được phép hiển thị.", "",
             "| Nhãn PlantVillage | ID chuẩn | Tên EN / VI dự thảo | Tác nhân từ card | Card | Quan hệ | Nguồn danh tính |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for m in matrix:
        refs_md = ", ".join(f"[{e['source_id']}]({e['url']})" for e in m["identity_evidence"])
        card_link = relpath(project / m["card_path"], output).replace("\\", "/")
        table.append(f"| {m['label_original']} | {m['canonical_condition_id']} | {m['name_en']} / {m['name_vi_draft']} | {m['agent_from_card']} | [{Path(m['card_path']).name}]({card_link}) | {m['relation']} | {refs_md} |")
    table += ["", "Trạng thái, đường dẫn, SHA-256, disease ID gốc và điều kiện hiển thị đầy đủ: mapping.json / mapping.csv. 7 card không có lớp ảnh vẫn được giữ độc lập trong kho tri thức."]
    (output / "mapping.md").write_text("\n".join(table) + "\n", encoding="utf-8")


def audit(project, output):
    """Compare current bytes to cleaning-run baselines, without recreating outputs."""
    root = project / "data/TomatoAI/data"
    registry = load(root / "dataset-registry.json")
    results = []
    for name, entry in registry["datasets"].items():
        processed = root / entry["processed"]
        report = root / Path(entry["checkpoint"]).parent
        config_path = report / "config.json"
        if not config_path.exists():
            config_path = project / f"scripts/data/{name.lower()}-config.json"
            if digest(config_path) != load(report / "fingerprint-inputs.json")["config_sha256"]:
                raise ValueError(f"Config mismatch: {name}")
        config = load(config_path)
        source = project / config["source_root"]
        with (report / "raw-before.csv").open(encoding="utf-8", newline="") as stream:
            before = list(csv.DictReader(stream))
        now = pv_snapshot(source) if name == "PlantVillage" else snapshot(source)
        expected = {r["source_file"]: (int(r["bytes"]), r["sha256"]) for r in before}
        actual = {r["source_file"]: (r["bytes"], r["sha256"]) for r in now}
        if actual != expected:
            raise ValueError(f"Raw baseline mismatch: {name}")
        verify_artifacts(processed, report)
        summary = load(report / "summary.json")
        if summary["run_id"] != entry["current_run"]:
            raise ValueError(f"Registry run mismatch: {name}")
        references = report / "reference-inputs.json"
        reference_count = 0
        if references.exists():
            values = load(references)
            values = list(values.values()) if isinstance(values, dict) else values
            for item in values:
                path = item.get("path", item.get("source_file"))
                if path is None or digest(project / path) != item["sha256"]:
                    raise ValueError(f"Reference mismatch: {name}: {path}")
                reference_count += 1
        recorded_inputs = report / "fingerprint-inputs.json"
        if recorded_inputs.exists():
            recorded = load(recorded_inputs)
            for item in recorded.get("inputs", recorded.get("references", [])):
                if digest(project / item["path"]) != item["sha256"]:
                    raise ValueError(f"Reference mismatch: {name}: {item['path']}")
                reference_count += 1
        observed = {}
        manifest = processed / "manifest.csv"
        if manifest.exists():
            with manifest.open(encoding="utf-8", newline="") as stream:
                statuses, classes = Counter(), {}
                for row in csv.DictReader(stream):
                    statuses[row.get("record_status", row.get("status", "not_recorded"))] += 1
                    if name == "PlantVillage":
                        classes.setdefault(row["label_original"], Counter())[row["record_status"]] += 1
            observed["manifest_records"] = sum(statuses.values())
            observed["record_status_counts"] = dict(statuses)
            if classes:
                observed["per_class"] = {k: dict(v) for k, v in sorted(classes.items())}
        observed["table_records"] = {}
        for table in sorted((processed / "tables").rglob("*.csv")):
            with table.open(encoding="utf-8-sig", newline="") as stream:
                observed["table_records"][table.relative_to(processed).as_posix()] = sum(1 for _ in csv.DictReader(stream))
        # Count normalized research records directly, not by copying registry totals.
        tables = sorted(processed.rglob("*.jsonl"))
        observed["jsonl_records"] = {p.relative_to(processed).as_posix(): sum(1 for _ in p.open(encoding="utf-8")) for p in tables}
        results.append({"dataset": name, "run_id": entry["current_run"],
                        "source_root": str(source.relative_to(project)).replace("\\", "/"),
                        "raw_files_checked": len(now), "raw_baseline": str((report / "raw-before.csv").relative_to(project)).replace("\\", "/"),
                        "raw_equal": True, "baseline_exclusions": [".git", ".cache", "__pycache__"] if name == "PlantVillage" else [],
                        "sealed_artifacts_checked": len(load(report / "output-artifacts.json")),
                        "sealed_equal": True, "reference_files_checked": reference_count,
                        "summary_sha256": digest(report / "summary.json"), "summary": summary,
                        "observed": observed})
    write_json(output, {"review_version": "ir-20261014-v1", "registry_sha256": digest(root / "dataset-registry.json"),
                        "datasets": results, "limit": "Equality to cleaning baselines only; no proof of integrity before those baselines."})


def validate_bundle(bundle):
    """Reject malformed/stale contracts before interpreting any class index."""
    manifest = bundle["class_manifest"]
    if manifest["sha256"] != fingerprint({k: v for k, v in manifest.items() if k != "sha256"}):
        raise ValueError("class_manifest_hash")
    labels = manifest["ordered_labels"]
    if not labels or len(set(labels)) != len(labels):
        raise ValueError("duplicate_class_label")
    maps = bundle["mapping"]
    if Counter(m["label_original"] for m in maps) != Counter(labels):
        raise ValueError("mapping_coverage_or_duplicate")
    cards = bundle["cards"]
    if len({c["record_id"] for c in cards}) != len(cards):
        raise ValueError("duplicate_card_id")
    by_id = {c["record_id"]: c for c in cards}
    for m in maps:
        card = by_id.get(m["card_id"])
        if card is None:
            raise ValueError("missing_card")
        if m["card_sha256"] != fingerprint(card):
            raise ValueError("card_hash")
        if m["source_sha256"] != card["source"]["sha256"]:
            raise ValueError("source_hash")
        if m["disease_id_original"] != card["content_en"]["disease_id"]:
            raise ValueError("condition_card_mismatch")
        if m["canonical_condition_id"] != manifest["condition_by_label"][m["label_original"]]:
            raise ValueError("condition_manifest_mismatch")
        if m["canonical_condition_id"] == "TOM_HEALTHY" and card["content_en"]["issue_type"] != "healthy":
            raise ValueError("healthy_card_mismatch")
    if len({c["claim_id"] for c in bundle["claims"]}) != len(bundle["claims"]):
        raise ValueError("duplicate_claim_id")
    for c in bundle["claims"]:
        card = by_id.get(c["card_id"])
        if card is None:
            raise ValueError("claim_missing_card")
        value = card
        for part in c["pointer"].strip("/").split("/"):
            value = value[int(part)] if isinstance(value, list) else value[part]
        if value != c["text_en"]:
            raise ValueError("claim_text_source_mismatch")
    return by_id


def lookup(bundle, prediction, *, confidence_threshold):
    """Fixture threshold only; no claim of calibration or OOD detection.

    The caller supplies externally determined scope/quality status. Actual project
    cards remain blocked. Only explicitly approved, hash-bound VI claims can pass.
    """
    def blocked(reason, condition=None):
        return {"status": "needs_check", "reason": reason, "canonical_condition_id": condition, "guidance": []}
    try:
        by_id = validate_bundle(bundle)
        manifest = bundle["class_manifest"]
        if prediction.get("manifest_version") != manifest["version"] or prediction.get("manifest_sha256") != manifest["sha256"]:
            return blocked("manifest_mismatch")
        if prediction.get("mapping_version") != bundle["version"]:
            return blocked("mapping_version_mismatch")
        index = prediction.get("class_index")
        if type(index) is not int or not 0 <= index < len(manifest["ordered_labels"]):
            return blocked("invalid_class_index")
        label = manifest["ordered_labels"][index]
        if prediction.get("label_original", label) != label:
            return blocked("unknown_or_inconsistent_label")
        score = prediction.get("confidence")
        if (type(score) not in (int, float) or not 0 <= score <= 1 or not math.isfinite(score)
                or type(confidence_threshold) not in (int, float) or not 0 <= confidence_threshold <= 1
                or not math.isfinite(confidence_threshold)):
            return blocked("invalid_confidence")
        if prediction.get("scope") != "in_scope" or prediction.get("quality") != "accepted" or score < confidence_threshold:
            return blocked("quality_scope_or_confidence")
        m = next(m for m in bundle["mapping"] if m["label_original"] == label)
        condition = m["canonical_condition_id"]
        if m["relation"] != "exact_source_checked":
            return blocked("mapping_not_verified", condition)
        card = by_id[m["card_id"]]
        if card["review"]["safe_for_advice"] is not True or card["review"]["domain"] != "expert_approved":
            return blocked("card_not_approved", condition)
        claims = [c for c in bundle["claims"] if c["card_id"] == card["record_id"]]
        approved = []
        for c in claims:
            if (c["source_sha256"] != card["source"]["sha256"] or c["card_sha256"] != m["card_sha256"]
                    or c["domain_review"] != "expert_approved" or not c.get("domain_reviewer")
                    or c["translation_review"] != "approved" or not c.get("translation_reviewer")
                    or c.get("translation_source_sha256") != c["source_sha256"]
                    or c.get("translation_claim_sha256") != fingerprint(c["text_en"])
                    or not c.get("text_vi") or c.get("translation_sha256") != fingerprint(c["text_vi"])
                    or c["display_allowed"] is not True or not c.get("evidence")
                    or c["kind"] not in ("basic_care", "nonchemical_cultural")
                    or c.get("required_context", {})):
                continue
            if condition == "TOM_HEALTHY" and c["kind"] != "basic_care":
                continue
            # Scope is condition-bound; no top-k merging and no context guessing.
            if c["canonical_condition_id"] != condition:
                continue
            if any(not e.get("url", "").startswith("https://") or not e.get("section") or not e.get("accessed") for e in c["evidence"]):
                continue
            approved.append({"claim_id": c["claim_id"], "text_vi": c["text_vi"], "evidence": c["evidence"],
                             "source_sha256": c["source_sha256"], "card_sha256": c["card_sha256"], "version": bundle["version"]})
        if not approved:
            return blocked("no_approved_vi_claims", condition)
        return {"status": "guidance_allowed", "canonical_condition_id": condition, "guidance": approved}
    except (AttributeError, KeyError, IndexError, TypeError, ValueError, StopIteration):
        return blocked("invalid_bundle")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--audit-output", type=Path)
    parser.add_argument("--build-output", type=Path)
    args = parser.parse_args()
    if args.audit_output:
        audit(args.project_root.resolve(), args.audit_output)
    if args.build_output:
        build_review(args.project_root.resolve(), args.build_output)
    if not args.audit_output and not args.build_output:
        parser.error("choose --audit-output or --build-output")
