---
title: 'Review nội dung và scope thẻ đầu tiên'
type: feature
ticket: S11
created: '2026-10-15'
status: blocked
technical_slice: verified_refusal_only
blocked_reason: 'Human source/VI/rights evidence absent; positive publisher and genuine allowed card still required'
baseline_revision: 'NO_VCS'
route: full
route_source: auto
risk: high
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** S11 lacks its preparation publication boundary. C3 limited educational demo direction is selected, but the user explicitly confirms no human source/VI review has happened. Rights remain pending. The official story requires a genuine allowed card, which cannot be fabricated.

**Approach:** Implement and verify the currently reachable refusal half of `publish_knowledge(draft: CardDraft, approvals: Path) -> KnowledgeBundle`, with bounded input, provenance and explicit blockers. Prepare an exact pending review packet. Keep S11 and Phase 2 incomplete; after technical verification review earlier phase evidence and record an actionable recovery order.

## Boundaries & Constraints

**Always:** Preserve S10 code/content/C3 decision and all sealed inputs, raw/processed/registry/rights/ticket bytes. Reuse curation replay and canonical hashing. Outputs contain status, reasons/blockers and empty claims/sources/lesson IDs when blocked. Record actual AI author role. Snapshot any existing document before editing. Missing human reviews are external evidence, not missing permission to implement this refusal boundary.

**Never:** Invent actors/approvals/rights, mark expert approval, change the old lookup, implement an untested allowed path, use a synthetic approved card as acceptance, train/download, build UI, add dependencies, or mark this story built/done. This delivery is explicitly partial S11, not an allowed KnowledgeBundle for S06.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Real pending dossier | Exact S10 draft and C3 decision, null reviewers | `needs_check`, claims/sources/lesson_ids empty; separate source/VI/rights/publication blockers | Structured refusal, CLI exit 2 |
| Invalid approvals | Missing file, duplicate keys, NaN, oversized, wrong schema or null policy | No allowed content or writes | Typed refusal without traceback |
| Provenance drift | Changed EN/VI/glossary/lesson, stale draft/scope/policy hash | Empty claims, specific integrity/policy reason | Refuse before use |
| Unsafe content | Chemical kind, contextual claim, wrong condition/claim/card | Empty claims | Explicit refusal even if other gates also block |
| Approval injection | Approved metadata with no actor, AI/self reviewer, forged policy or skip flag | No approval and empty claims | Deny; no string/config enables publication |
| Immutability | Public API/CLI including invalid cases | Draft and all protected input bytes unchanged | Read-only CLI; stdout only |

</frozen-after-approval>

## Code Map

- `scripts/knowledge/curate.py`: `CardDraft`, `curate_card`, `fingerprint`, `read_json`, `ROOT`, `CARD_ID`, `CLAIM_ID`; reuse, do not modify. Reconstruct the exact trusted S10 draft from fixed versioned editorial input and compare full canonical fingerprint, preventing mutation of nested lookup/lesson metadata. Revalidate consumed pinned files with curation replay.
- `content/phase2-healthy-v1/review-inputs.json` and sibling `phase2-healthy-v1-bundle/card-draft.json`: genuine pending tracer, exactly one watering claim. Both remain unchanged.
- `artifacts/phase2/c3-policy-decision.json`: exact selected scope and hashes; publication/display false, source/translation/rights pending. Pin its actual bytes; do not accept arbitrary policy supplied in an approvals file or permit external paths via it.
- `docs/development/assets-rights.json`: inventory only; no distribution clearance. No legal approval inferred from demo selection.
- `scripts/data/review_integration.py`: sealed preparation validator/lookup; remain byte-identical. No runtime module extraction in this story.
- Official `app-development-plan.md` S11, `engineering-contracts.md`, `planning/tomato-desktop/knowledge-localization-edtech.md`: blocked claims empty; separate source and language reviews, no AI self-approval. Native runtime gate and genuine positive lookup remain future blocked work.

## Tasks & Acceptance

**Execution:**
- [x] `artifacts/phase2/s11/approvals.pending.json` — exact schema/version, pinned C3 path/hash, full draft hash and three separate pending source/translation/rights review records. Null actors, actual status, no placeholder approvals. Document schema and blocking limitations.
- [x] `scripts/knowledge/publish.py` — preparation-only dataclass response and read-only `publish_knowledge`; reason codes for matrix cases, reuse bounded JSON and curation. CLI uses the genuine draft reconstructed via `curate_card`, prints refusal JSON and exits 2; errors never write to an input. No output-path option or allowed implementation until real approvals and positive evidence exist.
- [x] `tests/knowledge/test_publication.py` — RED missing handler then matrix regressions. Assert specific reasons, not merely always-empty output. Actor-invalid tests may mutate negative metadata, never make or call a synthetic card approved. No patched validator/fingerprint oracle.
- [x] `artifacts/phase2/s11/` — RED/GREEN logs, actual CLI refusal, reproduction and preservation evidence, handback README and changed-files manifest. Do not modify earlier artifacts or official docs; parent updates current planning after review.

**Acceptance Criteria:**
- Given the real current dossier, when the API/CLI runs, then all independent missing evidence is identifiable and no content becomes allowed.
- Given any matrix mutation, when validation runs, then the matching refusal reason is tested and all published content stays empty.
- Given the protected baseline, when implementation and tests finish, then every protected byte hash matches; S10 tests and old lookup suite remain green.
- Given no genuine human review, when reporting delivery, then S11 remains incomplete and the unimplemented positive publisher/lookup is stated explicitly.

## Implementation Notes

The user explicitly requested continued S11 execution and subsequent readiness review, after already authorizing Phase 2 and selecting limited demo. This authorizes the concrete technical work above without another plan-permission loop; it does not approve content or rights. One implementation writer owns only the four task scopes above; others share the workspace and remain read-only, do not revert their edits. No Git repository; baseline is `NO_VCS`. Parent captured `artifacts/phase2/s11/preservation-before.json` before changes (122 protected files). Missing domain/issue docs remain absent. No UI flow/config exists; inspect installed e2e capability and report limitation, do not build a browser substitute.

## Plan Change Log

## Review Triage Log

Quick reviewer `/root/s11_final_review` returned no actionable findings after reading the staged diff and surrounding code. Reviewer independently ran 19 knowledge tests, 22 lookup tests and verified 122 protected hashes. No patch, loopback or deferred code finding. This review covers the explicit partial refusal scope; it does not approve content or complete S11.

## Verification

- `.venv-phase0/Scripts/python.exe -m unittest discover -s tests/knowledge -p 'test_*.py' -v`
- `.venv-phase0/Scripts/python.exe -m unittest discover -s scripts/data -p test_review_integration.py -v`
- Actual read-only publication CLI; expected exit 2 with empty content and named missing reviews.
- SHA256 compare against S11 preservation baseline; report exact scope, no full raw rescan claim.

## Execution Results

All four technical tasks above delivered. Parent independently passed 19 knowledge, 22 old lookup, 31 benchmark and 2 Phase 0 diagnostic tests (74 total); genuine CLI exit 2 with exact five blockers and empty content; draft replay matches, 122 protected files unchanged. E2E attempt exited 2 `CONFIG_NOT_FOUND`, zero tests/report; no Qt product/config/URL exists. No configured lint/type checker. See `artifacts/phase2/s11/parent-verification.json`, logs and `document-verification.json`.

Earlier phase readiness review and remedies: `artifacts/phase2/s11/prior-phases-review.md`. Current PRODUCT/decisions/contracts/phase plan/traceability/checklist corrected with snapshots; IDs/graph/test mappings and ticket stores preserved. 82 local links resolved and 24 requirement rows preserved at the initial document check.

Status remains blocked, not built/done: the user confirms no human review. Genuine source/VI/lesson/quiz and rights review, a versioned publication decision, positive publisher and genuine allowed card/lookup remain required. No code or testing substitutes for this evidence. No Git repository, commit or push.
