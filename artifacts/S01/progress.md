# SDD ledger — plan: _bmad-output/initiative-tomato-desktop/app-development-plan/app-development-plan.md

Scope: Phase 0 / EPA.S01 only, authorized by the user on 2026-10-15 (Asia/Bangkok).

- Primary workflow: superpowers:executing-plans, inline execution; Ponytail full for the smallest runnable compatibility spike. BMAD ticket operations only record the existing story.
- Ruling: This workspace has no Git repository. Use `artifacts/S01/preservation-before.json`, evidence files and hashes instead of Git-based workspace/task/commit scripts. Do not initialize Git or claim a commit. Cost if wrong: no Git rollback/history; preserve these checkpoints.
- Ruling: Phase 0 is governance plus a diagnostic spike, not product implementation. Run real compatibility/traceability checks; TDD applies to the spike's observable output, not prose. Cost if wrong: spike evidence cannot prove the future app works.
- Pre-flight: S01 produces decisions, rights and compatibility for S05/S06/S18. Those consumers must still enforce grouping/split, pretrained-weight rights, content approval, compute and release gates; a successful import is insufficient.
- Confirmed by user: team of three working evenings; defense date unknown, roughly two months away; student laptops are weak; no tomato-domain expert is available. Exact hours, rubric, paid compute budget and reviewer remain unknown.
- Existing `docs/agents/domain.md` and `docs/agents/issue-tracker.md` are missing. Use the adopted spec and existing BMAD store; do not invent a second issue tracker.
- Task S01: in progress. Protected registry, seven ticket stores and sealed integration files snapshotted before changes.

- Ruling: S01 compares technical grouping eligibility, not final training permission. Both real records remain training-ineligible because approved split, rights and label review are missing. Cost if wrong: treating a grouped record as train-ready would bypass scientific gates.
- Existing suite probe with uv default Python 3.14.7: 104 tests, one import error (`test_clean_wur`: pdfplumber absent), 10 production checks skipped because production report was not specified. Do not alter cleaning code or claim this suite passed.
- Diagnostic red check observed: one failing test because phase0_smoke.py was absent; minimal implementation then added.

- Existing data verification resolved without installing into cleaning runtimes: bundled CPython 3.12 ran six modules, 82 tests OK (10 production checks skipped); uv default ran UC-IPM module, 31 tests OK. Earlier aggregate probes failed on missing pdfplumber/jsonschema and remain logged; do not call them passes.
- Preservation check: all 34 protected registry/ticket-store/integration files match before hashes. Scope is not a full corpus raw rehash.

- Transport diagnosis: the original official PyPI CDN route delivered only 619152/1048576 bytes in 20s and the uv sync retried NumPy/Qt. Stopped only the owned uv process. Download the same official wheels through another CDN address with unchanged host/TLS, verify published SHA256 and existing lock, then sync from local wheel files. Do not change system DNS or dependency versions. Original log retained as install-first-attempt.log.

- Dependency preparation complete: 21 packages in isolated CPython 3.12.14. Official Qt/NumPy wheels downloaded in bounded ranges after stalled full transfers; full SHA256 verified before hashed local install. Full lock sync then succeeded offline; uv pip check reports all packages compatible. No system DNS or cleaning environment changed.
- Diagnostic GREEN: native unittest 1/1 passed in 16.307s; standalone JSON records native Windows Qt exposure/timer, distinct spawned worker exit 0, finite [1,10] CPU outputs for both models. Pretrained weights not loaded, no training.
- Rights inventory: 48 entries total, including 21 installed software distributions and 17 separate knowledge cards. Both candidate weight enum recipes read without downloads; byte hashes/rights still pending.

- Frozen regression RED observed: 2 tests, source passes and frozen fails importing QtCore (WinError procedure missing). Analysis-00.toc points icuuc.dll to bundled Codex Poppler, not Windows ICU. The collected file lacks ucnv_open and exposes ICU78-suffixed symbols; Windows ICU exports the required unversioned symbols. Rebuild helper now constrains only its child PATH to the active Python and Windows directories; no host PATH change, dependency downgrade or vendor patch. Original failure/build evidence retained.

- ICU fix verified: clean build TOC has no Poppler/ICU78 and execution progresses past QtCore. Frozen regression then exposed torchvision 0.29.1 dynamic extension rename: installed _C_stable.pyd/image_stable.pyd versus installed hook hiddenimports=[torchvision._C]. TORCHVISION_WARN_WHEN_EXTENSION_LOADING_FAILS=1 confirms missing _C_stable in the bundle (frozen-extension-diagnosis.log). Source still passes; add exact installed stable extension names to diagnostic build, no patched vendor or operator bypass.

- Continuation audit: the interrupted turn made concrete progress (source checks, dependency/rights evidence, frozen failure); resumed from current failed executable, not a restart.
- Task S01 technical work complete: clean build exit 0; source/frozen regression 2/2 GREEN in 22.975s. Standalone frozen run exit 0 with native Qt, distinct worker and both finite CPU outputs; no foreign Poppler ICU and both stable torchvision extensions present. No train/pretrained download.
- Native runtime inventory records 113 binary hashes/origins/versions; rights ledger now 51 entries including CPython, MSVC and Windows ICU. Governance check verified 17 raw/source-copy card pairs and 162 installed license-file hashes. No release clearance claimed.

- Final review: one fresh-context read-only reviewer, gpt-6-astra; zero Critical/Important. Independent hash checks agree with current evidence; review did not rerun tests/build/GUI. See final-review.md. Executor re-graded both documentation findings as Minor by their actual effect; no fix pass or second review.
- Final: minor (deferred): decisions.md recreation command selects Python 3.12 rather than exact 3.12.14; use the verified 3.12.14 patch for reproduction until the command is synchronized.
- Final: minor (deferred): PRODUCT.md Stack still describes B0/package versions as undecided; decisions.md/compatibility.json hold the verified current baseline; synchronize product context in the next documentation pass.
- Final: Ruling: File replacement after preview, cancel and stale render remain unverified product behavior — this deliverable is a diagnostic with no product image flow; S06/S14 must implement and verify it — cost if wrong: stale or cancelled results could be shown if diagnostic evidence is mistaken for app acceptance.
- Final: Ruling: App cold-load and warm timeout policy remains unverified — S01 proves bounded diagnostic worker spawn only; S06/S18 own app policy — cost if wrong: startup hangs or incorrect timeout acceptance could be overlooked.
- Final: Ruling: Null/bool/NaN/malformed manifest fail-closed behavior remains unverified — the tracer reads selected existing manifests; S14 must validate product inputs — cost if wrong: malformed inputs could bypass future product checks.
- Final: Ruling: Guidance/card/VI approval and mapping after source changes remain gated — S01 inventories provenance without showing or approving guidance; S11/S11b/S13 own review — cost if wrong: unsafe or mismatched advice could be presented.
- Final: Ruling: Full disk/read-only/Vietnamese paths/DPI/privacy acceptance remains open — no product persistence or full UI was built; S13/S14/S18/S20 own these flows — cost if wrong: data loss, broken access or privacy failures could be missed.
- Final: Ruling: Accuracy, pretrained parity, CUDA and care/learning effectiveness remain unclaimed — no pretrained weights or training were run; later scientific work must supply evidence — cost if wrong: unsupported performance or care claims could be trusted.
- Final: Ruling: Redistribution clearance, complete notices and clean-machine/offline acceptance remain open — dev-machine execution is not release approval; C5/S18 must close these gates — cost if wrong: an unlawful or nonportable release could be shipped.
- Final: Ruling: Diagnostic window aesthetics/usability are not product design acceptance — the auto-closing window only proves native Qt exposure/event loop — cost if wrong: unusable product UI could be accepted without design verification.
- Task S01: complete for all five Phase 0 deliverables; native/frozen final suite 2/2 PASS, data regressions 103 pass/10 skip, all 34 protected hashes unchanged. BMAD runtime marked EPA.S01 built, not done; later phases remain planned. No Git commit or artifact cleanup claimed; preserve the evidence.
