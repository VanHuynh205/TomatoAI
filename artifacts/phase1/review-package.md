# Phase 1 final read-only review package

No Git repository exists. Review the current newly created implementation/test files and focused BMAD/evidence additions; preservation-before/after proves old cleaning sources/reports/registry/ticket stores unchanged. Do not mutate files, run cleaners, download data, spawn reviewers or change model approvals. You may run tests that only use temporary fixtures.

## Requirements and scope

- Primary plan: `_bmad-output/initiative-tomato-desktop/app-development-plan/app-development-plan.md`, Phase 1 / EPA.S02–S04 only.
- Spec: `_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/spec-tomato-desktop.md`; companion `data-readiness.md`; `app-development-plan/engineering-contracts.md` and `ux-security.md`.
- Implementation: `scripts/data/prepare_benchmark.py`; tests `tests/data/test_benchmark.py`.
- Evidence runner `artifacts/phase1/verify_evidence.py`; policies `group-decisions.json` and `split-policy.pending.json`.
- Real outputs `artifacts/data-card.json`, `group-resolution.json`, `metadata-investigation.json`, `split-manifest.json`; summary `artifacts/phase1/README.md`.
- Rulings and task status: `artifacts/phase1/progress.md`; weigh every `Ruling:` line.
- Official board plan files for S02/S03 are in-progress pending this review; S04 blocked. Existing seven tickets.toml untouched. No story marked done.

## What was implemented and verified

S02 selected-run/hash/provenance/count/rights intake with six distinct dataset roles and five cleaning raw baselines (18,362 files). S03 exact metadata replay, conservative leaf/duplicate components, alias quarantine, whole-component pending-near quarantine; 11,411 candidates / 6,735 retained quarantine / 14 exact exclusions. Actual C2 remains blocked. S04 deterministic group-aware algorithm with explicit local approval policy and fixture-only positive tests; real output stays blocked/zero assignments. User authorizes best technical choices in absence of expert, not fabricated label/leaf approval. Pending seed42/70:15:15/order/code choices do not approve data.

140 final targeted tests passed: 27 benchmark, 82 existing data including ten actual production checks, 31 UC-IPM. Default uv aggregate also attempted and fails WUR import without pdfplumber; correct bundled runtime covers WUR. No native/browser UI changed or appropriate E2E engine/config.

## Plan Review Focus (verbatim)

1. File bị thay sau preview hoặc kết quả đến sau cancel: đúng image identity, zero stale render; S06/S14, T01/T10.
2. Cold load và worker spawn trong gói Windows: không mở app/process vô hạn, không áp timeout warm sai; S06/S18, T10–T13.
3. Input/config null/bool/NaN/zero hoặc malformed manifest: fail closed, không healthy fallback/bypass review; S14, T02–T04/T06/T12.
4. Ảnh accepted nhưng card/VI/claim chưa duyệt hoặc đổi nguồn: guidance trống có lý do, không substitute gần tên; S11/S11b/S13, T07–T09.
5. Full disk/read-only/path tiếng Việt/DPI cao: lỗi hữu ích, không mất input, không cắt hướng dẫn hoặc phá privacy; S13/S14/S18/S20, T18/T19.

Within Phase 1, deliberately inspect malformed config types, trust boundaries, path/output clobbering, stale evidence/approval, record eligibility, component leakage and honest status reporting. Later GUI/model/claim behavior is not implemented; list any behavior set aside under Declined to judge, with reason.

## Review response

Follow `superpowers:requesting-code-review/code-reviewer.md`: specific file:line, Critical/Important/Minor, actual user effect and proposed remedy. The spec is a vision document; reasonable expectations also count. List every Declined to judge item. Give a clear verdict on this technical Phase 1 slice, not a claim that full Phase 1 is complete. Do not dispatch any subagents.
