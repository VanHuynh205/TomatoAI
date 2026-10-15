---
title: 'VI/glossary/mapping dẫn xuất cho thẻ đầu tiên'
type: feature
ticket: S10
created: '2026-10-15'
status: built
baseline_revision: 'NO_VCS'
route: full
route_source: auto
risk: high
review: 'quick'
review_source: 'pinned'
lenses_ran: [quick]
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Phase 2 has no traceable Vietnamese card draft connecting the cleaned EN knowledge to a lesson and two quiz questions. Guidance remains blocked by C3.

**Approach:** Build the S10 tracer for the existing healthy leaf card and one source-checked nonchemical watering claim. Reuse the sealed integration validator and refusal lookup. Prepare a concrete S11 decision dossier without approving policy or advice. The user explicitly requested execution of Phase 2 under the official plan on 2026-10-15; this supplies execution authorization for S10, not missing C3 review.

## Boundaries & Constraints

**Always:** Preserve raw, processed cards, registry, existing reports, EN text and IDs. Derive a new version under `content/`. Bind source/card/claim/translation/glossary/lesson hashes and actual author role/date. Translation is an AI-authored draft, not independent or agronomic approval. Keep domain/translation review pending and `display_allowed=false`. Healthy denotes a leaf class only. Record unresolved rights and C3 explicitly.

**Never:** Translate 17 cards, train/download models, build UI, change split/class order, add dependencies, certify experts, relax the existing lookup gate, or publish allowed guidance. Source checking is not advice approval. Do not infer numeric irrigation or fertilizer schedules.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Real tracer | Healthy card and selected watering claim with draft VI | Versioned draft, terms, one lesson, exactly two sourced quiz keys; existing lookup returns empty guidance | Explicit pending review |
| Stale inputs | Raw/card/integration/claim/glossary hash mismatch | No output bundle | ValueError with cause |
| Invalid selection | Unknown/duplicate claim, wrong condition/pointer or noncandidate claim | No output bundle | Reject exact mismatch |
| Invalid editorial input | Empty VI/actor/role, bad lesson references/key, duplicate JSON keys | No output bundle | Reject before writing |
| Approval injection | Draft input claims approved status or unsafe context | No approval produced | Reject or preserve refusal |
| Output collision | Existing version or source/ancestor output path | Original bytes remain unchanged | Refuse output |

</frozen-after-approval>

## Code Map

- `scripts/data/review_integration.py`: reuse `load`, `fingerprint`, `validate_bundle`, `lookup` in this preparation tool only; leave sealed module bytes intact. Runtime extraction belongs to S06.
- `data/TomatoAI/data/processed/plantexpert-tomato/pex-b3da04d66a031756/cards/healthy.json`: immutable card ID `pex:disease_kb/tomato/healthy.json`, source SHA256 `89a50caefe302b04ac61b3ccfd35f43054335be3ad5bf63eb8a9cd0025cddb83`.
- `data/TomatoAI/data/reports/integration/ir-20261014-v1/lookup-bundle.json`: immutable mapping, class order, claims and evidence. Select only `ir-claim:healthy:cultural:2`, pointer `/content_en/management/cultural/2`.
- `docs/development/assets-rights.json`: healthy card redistribution and independent review remain pending.
- `planning/tomato-desktop/knowledge-localization-edtech.md`: draft EN–VI, separate source/language/domain review, partial learning evidence only.
- `_bmad-output/initiative-tomato-desktop/app-development-plan/engineering-contracts.md`: owns `CardDraft` interface; no runtime imports of cleaners.

## Tasks & Acceptance

**Execution:**
- [x] `content/phase2-healthy-v1/review-inputs.json` — author one watering translation, versioned glossary, source-check notes, lesson and two quiz drafts with source references; record AI role and pending approvals.
- [x] `scripts/knowledge/curate.py` — implement `curate_card(card_id: str, review_inputs: Path) -> CardDraft` and bounded read-only CLI; reuse integrity and lookup contracts, validate provenance and editorial references, refuse output overwrite.
- [x] `tests/knowledge/test_curation.py` — first show missing handler failure, then verify real tracer, stale hashes, invalid selection/editorial inputs, output preservation, approval refusal and lesson keys. Keep historical lookup suite.
- [x] `artifacts/phase2/` — record commands, real CLI output, preservation hashes, source audit, S11 policy proposal and completion limits.
- [ ] Official plan and traceability — record S10 build evidence and S11 pending C3; leave ticket stores and done states unchanged.

**Acceptance Criteria:**
- Given the real healthy EN card, when curation runs, then the selected claim has exact unchanged EN/ID/pointer and hash-bound VI, glossary and lesson provenance.
- Given missing independent reviews, when the derived bundle goes through existing lookup, then `guidance == []` for every real class, including healthy.
- Given the lesson, when references and keys are checked, then exactly two draft questions have valid unique choices, an existing correct key, explanation and traceable sources. No learning-effectiveness claim follows.
- Given immutable input baselines, when implementation and checks finish, then relevant raw/processed/integration bytes and old validator remain unchanged.

## Implementation Notes

User authorization covers this execution; no repeated plan approval requested. C3 policy and reviewers remain unresolved and cannot be supplied by a technical test. No Git repository exists, so no baseline commit or commit operation is available. Missing `docs/agents/domain.md` and `issue-tracker.md` were checked; use official spec/contracts instead, create no local issues.

Execution ownership: the implementation agent owns all tasks in this plan. Other agents share this workspace and remain read-only during implementation; do not revert their existing work. The parent will independently verify results after handback. Keep the agent available for review fixes. Fresh primary-source check on 2026-10-15 by Codex and a read-only investigator found the UMN Growing tomatoes page (existing evidence URL) supports watering at plant base in Diseases and avoiding wet foliage in Watering. Record this as AI source checking, not independent human/domain/translation approval. Do not archive the full copyrighted page or reproduce numeric Minnesota schedules; use concise original support notes and source metadata.

## Plan Change Log

## Review Triage Log

2026-10-15 — Quick reviewer returned no findings. Parent independently reran 8 curation and 22 lookup tests, reproduced the generated draft and all 10 refusals, and rehashed all 117 preserved files without mismatch. No findings deferred. S10 build only; S11 and Phase 2 remain incomplete. NO_VCS: no commit.

## Verification

- `.venv-phase0/Scripts/python.exe -m unittest discover -s tests/knowledge -p test_curation.py -v`
- `.venv-phase0/Scripts/python.exe -m unittest discover -s scripts/data -p test_review_integration.py -v`
- Real CLI curation and all-ten-class refusal checks; before/after hashes for consumed raw, processed, registry, integration seal and validator.
- Inspect installed e2e capability/config. This phase is a JSON/CLI preparation pipeline; there is no frontend URL or Qt app flow to drive. Report that limitation instead of creating a browser substitute.
