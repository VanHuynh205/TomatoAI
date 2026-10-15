"""Trace two real PlantVillage records; never approve training or alter data."""

import hashlib
import json
from pathlib import Path


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    base = root / "data/TomatoAI/data"
    registry = json.loads((base / "dataset-registry.json").read_text(encoding="utf-8"))
    dataset = registry["datasets"]["PlantVillage"]
    processed = base / dataset["processed"]
    manifest = processed / "manifest.jsonl"
    chosen = {}
    with manifest.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row["record_status"] == "ready_for_split" and row["leaf_group_id"]:
                chosen.setdefault("grouped", row)
            if row["record_status"] == "needs_review" and not row["leaf_group_id"]:
                chosen.setdefault("missing_group", row)
            if len(chosen) == 2:
                break
    assert set(chosen) == {"grouped", "missing_group"}
    records = []
    for kind, row in chosen.items():
        raw = base / dataset["source_root"] / row["source_file"]
        copy = processed / row["processed_file"]
        raw.resolve().relative_to((base / dataset["source_root"]).resolve())
        copy.resolve().relative_to(processed.resolve())
        assert sha256(raw) == sha256(copy) == row["sha256"], row["record_id"]
        evidence = []
        for item in row["group_evidence"]:
            path = base / dataset["source_root"] / item["source_file"]
            path.resolve().relative_to((base / dataset["source_root"]).resolve())
            evidence.append({**item, "artifact_sha256": sha256(path)})
        candidate = bool(row["leaf_group_id"] and evidence
                         and row["split_component_id"]
                         and row["record_status"] == "ready_for_split")
        assert candidate is (kind == "grouped")
        assert row["ready_for_training"] is False
        records.append({
            "kind": kind, "record_id": row["record_id"], "run": dataset["current_run"],
            "source_file": raw.relative_to(root).as_posix(),
            "processed_file": copy.relative_to(root).as_posix(),
            "sha256": row["sha256"], "raw_and_processed_hash_match": True,
            "leaf_group_id": row["leaf_group_id"], "group_evidence": evidence,
            "split_component_id": row["split_component_id"],
            "technical_grouping_candidate": candidate, "training_eligible": False,
            "rights_asset_id": "dataset:PlantVillage",
            "refusal_reasons": ["approved split absent", "asset use/redistribution not cleared",
                                "image-label expert verification pending"]
                               + ([] if candidate else ["missing grouping evidence"]),
        })
    report = {"scope": "two real records only; not a full raw rehash or benchmark approval",
              "manifest": manifest.relative_to(root).as_posix(),
              "manifest_sha256": sha256(manifest), "records": records,
              "rights_ledger": "docs/development/assets-rights.json",
              "raw_writes": 0, "split_created": False}
    ledger = json.loads((root / report["rights_ledger"]).read_text(encoding="utf-8"))
    assert any(asset["id"] == "dataset:PlantVillage" and
               asset["redistribution_status"] == "pending" for asset in ledger["assets"])
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
