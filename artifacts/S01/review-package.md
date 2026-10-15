# Phase 0 / EPA.S01 — Final review package

Review is read-only. This directory has no Git repository. Review the listed current files, the before/after preservation evidence and runtime logs. Do not manufacture a Git diff, execute later phases or spawn more reviewers.

## Authority and scope

- Plan: `_bmad-output/initiative-tomato-desktop/app-development-plan/app-development-plan.md`, Phase 0 only.
- Spec: `_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/spec-tomato-desktop.md` and its data-readiness/requirements companions.
- Rulings: `artifacts/S01/progress.md`, every `Ruling:` line.
- User authorized Phase 0 execution, no-login desktop, optional local history default off, Python/PySide6/PyTorch. Team: three people working evenings; defense roughly two months away; exact rubric/date/hours/compute budget unknown; weak laptops and no tomato-domain expert.
- Governance deliverables may explicitly leave external decisions blocked. S01 does not approve a scientific benchmark, training, content guidance or redistribution.

## Changed implementation and evidence

- `scripts/checks/phase0_smoke.py`, `test_phase0_smoke.py`, `phase0_trace.py`, `scripts/checks/build_phase0.py`: diagnostics only, not the product app.
- `requirements-app.in`, `requirements-app.lock`: isolated Windows CPython 3.12 CPU environment; no cleaning environment upgrades.
- `docs/development/decisions.md`, `assets-rights.json`, `compatibility.json`.
- `artifacts/S01/README.md`, `software-inventory.json`, `weights-metadata.json`, smoke/build/test logs, governance-trace and preservation evidence.
- Official plan/spec, `PRODUCT.md`, EPA epic and S01 story checkpoint; append-only spec memlog. No other story execution or changed ticket membership.

Check exact commands/results and incomplete checks. Check artifact links, factual status, rights/provenance, protected input hashes, worker cleanup, bounded execution, actual native Qt and frozen spawn. A synthetic CPU tensor and random model initialization prove compatibility only. Neither accuracy nor pretrained weights were evaluated.

## Plan Review Focus (verbatim)

1. File bị thay sau preview hoặc kết quả đến sau cancel: đúng image identity, zero stale render; S06/S14, T01/T10.
2. Cold load và worker spawn trong gói Windows: không mở app/process vô hạn, không áp timeout warm sai; S06/S18, T10–T13.
3. Input/config null/bool/NaN/zero hoặc malformed manifest: fail closed, không healthy fallback/bypass review; S14, T02–T04/T06/T12.
4. Ảnh accepted nhưng card/VI/claim chưa duyệt hoặc đổi nguồn: guidance trống có lý do, không substitute gần tên; S11/S11b/S13, T07–T09.
5. Full disk/read-only/path tiếng Việt/DPI cao: lỗi hữu ích, không mất input, không cắt hướng dẫn hoặc phá privacy; S13/S14/S18/S20, T18/T19.

Assess these deliberately: only the Phase 0 frozen/native diagnostic portion of item 2 is implemented. The remaining product cases must remain explicitly unclaimed and assigned to their future stories.

Return findings with severity, file/line, concrete effect and suggested fix. Also list strengths, evidence limits, anything declined to judge, and readiness for S01 `built` review (not `done` or release). Do not flag absent future-phase product implementation as missing Phase 0 scope.
