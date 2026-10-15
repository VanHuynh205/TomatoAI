"""Compare only the 122 parent-recorded protected files, never rescan all raw data."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
before = json.loads((HERE / "preservation-before.json").read_text(encoding="utf-8"))
entries = []
for old in before["files"]:
    path = ROOT / old["path"]
    current = {"path": old["path"], "bytes": path.stat().st_size,
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    current["matches"] = all(current[key] == old[key] for key in ("bytes", "sha256"))
    entries.append(current)
result = {"scope": before["scope"], "checked_count": len(entries),
          "changed_count": sum(not entry["matches"] for entry in entries), "files": entries}
(HERE / "preservation-after.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: result[key] for key in ("scope", "checked_count", "changed_count")}))
raise SystemExit(1 if result["changed_count"] else 0)
