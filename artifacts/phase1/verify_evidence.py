"""Capture Phase 1 real-data verification without changing cleaning inputs."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import time
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/phase1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


started = time.monotonic()
command = [sys.executable, "scripts/data/prepare_benchmark.py", "--group-decisions",
           "artifacts/phase1/group-decisions.json", "--split-policy", "artifacts/phase1/split-policy.pending.json"]
with (OUT / "pipeline-final.log").open("w", encoding="utf-8") as log:
    run = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
save("pipeline-run.json", {"command": command, "exit_code": run.returncode,
                          "elapsed_seconds": round(time.monotonic() - started, 2),
                          "expected_exit_code": 2, "meaning": "C2 blocked; no approved real split"})
assert run.returncode == 2, "expected a blocked real split, inspect pipeline-final.log"
card = json.loads((ROOT / "artifacts/data-card.json").read_text(encoding="utf-8"))
groups = json.loads((ROOT / "artifacts/group-resolution.json").read_text(encoding="utf-8"))
split = json.loads((ROOT / "artifacts/split-manifest.json").read_text(encoding="utf-8"))
assert not card["errors"] and not groups["errors"]
assert card["raw_writes"] == 0 and not split["assignments"] and not split["class_manifest"]
assert len(groups["records"]) == 18160
assert groups["counts"]["dispositions"] == {"technical_candidate": 11411, "quarantined": 6735, "excluded_exact_duplicate": 14}

# Explicit after-check for the same five scopes, beyond the pipeline's intake check.
sys.path.insert(0, str(ROOT / "scripts/data"))
from prepare_benchmark import raw_baseline

after_counts = {}
for entry in card["datasets"]:
    if "raw_source" not in entry:
        continue
    baseline = Path(entry["report"]) / "raw-before.csv"
    assert sha(baseline) == entry["raw_baseline_sha256"]
    verified = raw_baseline(Path(entry["raw_source"]), baseline, tuple(entry["raw_scope_exclusions"]))
    after_counts[entry["dataset"]] = len(verified)
save("raw-after.json", {"scopes": after_counts, "files_checked": sum(after_counts.values()),
                        "equals_intake_count": sum(after_counts.values()) == sum(d.get("raw_files_hash_checked", 0) for d in card["datasets"]),
                        "hashes_match_same_cleaning_baselines": True,
                        "limits": "same file-set/bytes/SHA256 baseline scope; not label review or integrity before baseline"})

# Original workbook inspected in memory. No extraction, macro or formula execution.
raw = ROOT / "data/TomatoAI/data/raw/plantvillage"
archive = raw / "leaf_grouping/Google Leaf Counts.zip"
member = "Google Leaf Counts/Tomato Leaf Counts.xlsx"
with ZipFile(archive) as outer:
    assert outer.getinfo(member).file_size < 16 * 1024 * 1024
    workbook_bytes = outer.read(member)
with ZipFile(io.BytesIO(workbook_bytes)) as book:
    def xml(name):
        assert book.getinfo(name).file_size < 16 * 1024 * 1024
        payload = book.read(name)
        assert b"<!DOCTYPE" not in payload and b"<!ENTITY" not in payload
        return ET.fromstring(payload)

    strings = ["".join(n.itertext()) for n in xml("xl/sharedStrings.xml")]
    sheets = [node.attrib["name"] for node in xml("xl/workbook.xml").iter() if node.tag.endswith("}sheet")]
save("original-metadata-workbook.json", {
    "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
    "member": member, "member_sha256": hashlib.sha256(workbook_bytes).hexdigest(),
    "shared_string_count": len(strings), "sheet_names_verbatim": sheets,
    "prefix_counts": {prefix: sum(prefix.casefold() in s.casefold() for s in strings)
                      for prefix in ("Com.G_FL", "TgS", "mosaic", "TmV", "TomV")},
    "conclusions": ["No target-image TgS prefix or mosaic sheet found in this workbook",
                    "Source wording Target Spot Bacteria is not an accepted taxonomy decision",
                    "Numeric filename overlap does not establish leaf identity; aliases remain unapplied"],
    "formulas_executed": False, "files_extracted": 0})

before = json.loads((OUT / "preservation-before.json").read_text(encoding="utf-8"))
changed = [r["path"] for r in before["files"] if not (ROOT / r["path"]).is_file() or sha(ROOT / r["path"]) != r["sha256"]]
save("preservation-after.json", {"scope": before["scope"], "files_checked": len(before["files"]),
                                 "changed": changed, "passed": not changed,
                                 "raw_baselines_checked_by_pipeline": sum(d.get("raw_files_hash_checked", 0) for d in card["datasets"])})
assert not changed, changed
print(json.dumps({"datasets": len(card["datasets"]), "group_counts": groups["counts"]["dispositions"],
                  "split_status": split["status"], "preserved_files": len(before["files"]),
                  "elapsed_seconds": round(time.monotonic() - started, 2)}))
