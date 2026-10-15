"""Independent local checkpoint checks, actual QA evidence, and additive registry entry.

Run folders are sealed and never edited. Verification/handoff live beside runs.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import collect_ucipm as uc


def verify(project, run_id, register=False):
    project = project.resolve()
    if not re.fullmatch(r"ucipm-[a-z0-9-]+", run_id):
        raise ValueError("Unsafe run ID")
    config = uc.load(Path(__file__).with_name("ucipm-config.json"))
    root = uc.local(project, config["dataset_root"])
    raw, processed, report = [root / name / "uc-ipm-tomato" / run_id for name in ("raw", "processed", "reports")]
    parent = report.parent
    checkpoint, summary = uc.load(report / "checkpoint.json"), uc.load(report / "summary.json")
    rows = uc.load(report / "source-processed-manifest.json")
    if uc.load(report / "artifact-seal.json") != uc.seal(raw, processed, report):
        raise ValueError("Run seal invalid")
    if len(rows) != 21 or len({r["source_id"] for r in rows}) != 21 or {r["original_url"] for r in rows} != set(config["allowlist"]):
        raise ValueError("21-item identity/allowlist mismatch")
    counts = {"acquisition": dict(Counter(r["acquisition"] for r in rows)),
              "processing": dict(Counter(r["processing"] for r in rows))}
    if counts != summary["counts"]:
        raise ValueError("Counts mismatch")
    for row in rows:
        if row.get("snapshot_file"):
            if uc.digest(raw / row["snapshot_file"]) != row["snapshot_sha256"]:
                raise ValueError("Snapshot provenance mismatch")
        elif row["snapshot_sha256"] is not None:
            raise ValueError("Hash without bytes")
        if any(row["review"][key] is not False for key in ("display_allowed", "safe_for_advice", "ready_for_training")):
            raise ValueError("Review gate changed")
    before = uc.load(report / "preservation-before.json")
    if uc.protected(project, root) != before:
        raise ValueError("Original sources/reports/planning changed")
    with uc.local(project, config["coverage"]).open(encoding="utf-8-sig", newline="") as stream:
        coverage = list(csv.DictReader(stream))
    mapping = uc.load(processed / "mapping-sidecar.json")
    for old, new in zip(coverage, mapping):
        if any(old[k] != new[k] for k in old if k != "display_allowed"):
            raise ValueError("Coverage metadata changed")
    if len(mapping) != 10:
        raise ValueError("10-class coverage mismatch")
    samples = uc.load(processed / "claim-evidence-sidecar.json")
    ledger = {r["claim_id"]: r for r in uc.load(uc.local(project, config["integration"]) / "claim-ledger.json")}
    if len(samples) != 12:
        raise ValueError("12-claim sample mismatch")
    for claim in samples:
        original = ledger[claim["claim_id"]]
        if any(claim[k] != original[k] for k in ("text_en", "card_id", "canonical_condition_id")):
            raise ValueError("Claim identity/text changed")
        if claim["original_source_sha256"] != original["source_sha256"]:
            raise ValueError("PlantExpert origin hash changed")
    results = []
    commands = [("unit-tests", [sys.executable, "-m", "unittest", "discover", "-s", "scripts/data", "-p", "test_collect_ucipm.py", "-v"]),
                ("integration-tests", [sys.executable, "-m", "unittest", "discover", "-s", "scripts/data", "-p", "test_review_integration.py", "-v"]),
                ("lint", [sys.executable, "-m", "ruff", "check", "scripts/data/collect_ucipm.py", "scripts/data/test_collect_ucipm.py", "scripts/data/verify_ucipm.py"]),
                ("compile", [sys.executable, "-m", "py_compile", "scripts/data/collect_ucipm.py", "scripts/data/test_collect_ucipm.py", "scripts/data/verify_ucipm.py"])]
    for label, command in commands:
        path = parent / (run_id + "-" + label + ".txt")
        if path.exists():
            raise ValueError("Verification output exists; preserve it, do not overwrite")
        result = subprocess.run(command, cwd=project, capture_output=True, text=True)
        path.write_text(result.stdout + result.stderr, encoding="utf-8")
        results.append({"name": label, "command": command, "exit_code": result.returncode,
                        "log": path.relative_to(root).as_posix(), "sha256": uc.digest(path)})
        if result.returncode:
            raise ValueError("QA failed: " + label + "; see " + str(path))
    # Re-run the full offline derivation from existing snapshots into temporary folders.
    receipt = project / "scripts/data/ucipm-preflight-20261014.json"
    replay = uc.run(Path(__file__).with_name("ucipm-config.json"), project, run_id,
                    blocked_preflight=receipt, transform_only=True)
    registry_path = root / "dataset-registry.json"
    original_registry = uc.load(report / "registry-before.json")
    registry = uc.load(registry_path)
    for name, entry in original_registry["datasets"].items():
        if registry["datasets"].get(name) != entry:
            raise ValueError("Old registry entry changed: " + name)
    e2e_log = project / "tmp/ucipm-e2e.txt"
    if "CONFIG_NOT_FOUND" not in e2e_log.read_text(encoding="utf-8"):
        raise ValueError("Expected E2E blocker evidence missing")
    archived_e2e_log = parent / (run_id + "-e2e.txt")
    if archived_e2e_log.exists():
        raise ValueError("E2E evidence already exists; refusing overwrite")
    archived_e2e_log.write_bytes(e2e_log.read_bytes())
    verification = {"verified_at": uc.now(), "passed": True, "run_id": run_id,
                    "corpus_status": summary["status"], "counts": counts, "checks": results,
                    "protected_files_stat_checked": len(before),
                    "protected_files_sha256_checked": sum("sha256" in r for r in before),
                    "media_rehashed": False, "raw_snapshot_count": sum(bool(r.get("snapshot_file")) for r in rows),
                    "offline_transform_replay": replay, "mapping_rows": 10, "claim_sample": 12,
                    "full_172_claim_review": False,
                    "e2e": {"command": "npx --no-install e2e run --output ../tmp/ucipm-e2e",
                            "exit_code": 2, "error": "CONFIG_NOT_FOUND", "tests_executed": 0,
                            "frontend_url": None, "reason": "No e2e.config.ts/mts; Python data CLI changes only",
                            "log": archived_e2e_log.relative_to(root).as_posix(),
                            "sha256": uc.digest(archived_e2e_log)},
                    "registry_old_entries_unchanged": True, "registry_updated": register}
    verification_path = parent / (run_id + "-verification.json")
    if verification_path.exists():
        raise ValueError("Verification already exists; refusing overwrite")
    uc.write_json(verification_path, verification)
    if register:
        if "UC-IPM-Tomato" in registry["datasets"]:
            raise ValueError("Existing UC entry requires a separately versioned append, not replacement")
        registry["datasets"]["UC-IPM-Tomato"] = {
            "source_root": "raw/uc-ipm-tomato", "current_run": run_id,
            "status": "research_only; acquisition_blocked",
            "technical_status": "0 cleaned documents; 21 not applicable because preflight stopped",
            "processed": processed.relative_to(root).as_posix(), "report": report.relative_to(root).as_posix() + "/README.md",
            "checkpoint": (report / "checkpoint.json").relative_to(root).as_posix(),
            "validation": verification_path.relative_to(root).as_posix(),
            "research_only": True, "exclude_from_release": True, "mvp_dependency": False,
            "training_ready": False, "safe_for_advice": False, "display_allowed": False,
            "domain_review": "pending", "translation_review": "not_translated", "reviewer": None,
            "counts": counts, "blockers": [checkpoint["blocker"], "Resource rights and current robots not cleared; no corpus bytes acquired"],
            "next_action": "Resolve legitimate access/rights and current robots in a separate bounded run; no bypass, translation, advice or training"
        }
        if any(registry[k] != original_registry[k] for k in original_registry if k != "datasets"):
            raise ValueError("Registry top-level metadata changed")
        # Atomic file replacement; original bytes are preserved in the run's registry-before.json.
        temporary = registry_path.with_suffix(".ucipm.tmp")
        uc.write_json(temporary, registry)
        os.replace(temporary, registry_path)
        actual = uc.load(registry_path)
        if any(actual["datasets"][k] != v for k, v in original_registry["datasets"].items()):
            raise ValueError("Registry preservation check failed")
    return verification


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run", required=True)
    parser.add_argument("--register", action="store_true")
    args = parser.parse_args()
    result = verify(args.project, args.run, args.register)
    print(json.dumps({k: result[k] for k in ("passed", "counts", "protected_files_stat_checked",
                                           "protected_files_sha256_checked", "registry_updated")}, indent=2))
