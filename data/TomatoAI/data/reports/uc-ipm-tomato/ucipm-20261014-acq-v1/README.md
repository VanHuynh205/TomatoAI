# UC IPM bounded research run ucipm-20261014-acq-v1

Status: **blocked**. Corpus: 21 selected HTML items. Counts: `{"acquisition": {"not_attempted_batch_stopped": 21}, "processing": {"not_applicable": 21}}`.

Blocker: `{"http_status": 403, "url": "https://ucanr.edu/dept/anr-publishing/permissions", "reason": "HTTP 403 Forbidden during permissions preflight; stop collection; do not bypass"}`. No corpus request after preflight stop.

Snapshot bytes remain immutable and exclude media. This run has no distribution, translation, advice or training approval. All original datasets, integration mapping/ledger/class order, survey and policies are preserved. See preservation-before/after.json: file list/size/mtime plus scoped control and PlantExpert hashes; images are not rehashed.

Mapping sidecar keeps 4 exact disease pages, 2 broad groups, Healthy care and 3 gaps distinct. TMV/ToMV not synonyms; spider mite not russet mite; Gray Mold does not replace Leaf Mold; Early Blight does not replace Target Spot. Claim sidecar retains only 12 previously surveyed examples and conflicts; no fresh source-check without a snapshot, no full review of 172 claims.

## Windows commands (project root)

```powershell
python scripts/data/collect_ucipm.py --run ucipm-20261014-acq-v1 --blocked-preflight scripts/data/ucipm-preflight-20261014.json
python scripts/data/collect_ucipm.py --run ucipm-20261014-acq-v1 --blocked-preflight scripts/data/ucipm-preflight-20261014.json --transform-only
python -m unittest discover -s scripts/data -p test_collect_ucipm.py -v
```

Same sealed input/parser reuses artifacts without network. Changed input/parser requires a new run. A future live run uses --live with a new run ID and checks current robots/terms first; it never bypasses 403/CAPTCHA/429. Per-item rights_by_item decisions need evidence_url and conditional_allowed for research_copy; technical_processing has a separate gate. Empty rights decisions retain metadata, never imply a blanket CC license.

Dependencies: existing requests, beautifulsoup4 and jsonschema; standard unittest. No install, model/API translation or product dependency. Parser live layout remains unverified when corpus snapshots are absent. UI e2e is not a Python CLI test; e2e.config.ts/mts absent, no UI flow changed.
