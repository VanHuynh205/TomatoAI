# Final review — Phase 1 technical slice

Fresh read-only reviewer: `/root/phase1_final_review`, `gpt-6-astra`, high reasoning. Review requested by executing-plans; no implementation subagents or second review. Reviewer independently ran 27 pre-fix benchmark tests; other test/raw claims were read from evidence. No Git repository exists; package and preserved baseline define scope.

## Findings and executor re-grade

No Critical or Minor findings. Three Important findings accepted in one fix pass:

1. `resolve_groups` ignored source review flags/statuses and could promote a pending record. Regression `test_source_review_flags_and_unknown_status_block_whole_component` failed before the fix for image-quality flag, near scan-budget flag, unknown status and missing processed copy. Fix preserves original flags/status, propagates each review blocker across the entire component and quarantines it. No manual override added.
2. CLI could overwrite an input policy before rejecting invalid argument combinations. Regressions `test_cli_rejects_missing_dependency_without_any_output` and `test_cli_rejects_input_and_fixed_sidecar_collisions_before_writing` failed before the fix. Fix validates dependency flags, resolved output/input paths, fixed sidecar collisions and protected input trees before writing any output.
3. `ordered_codes` string/dict could pass sequence validation and create an invalid class manifest. `test_ordered_codes_require_list_of_unique_nonempty_strings` failed for both string and dict. Fix requires a list before element/uniqueness checks; null/empty/duplicate/nonstring values fail closed, valid explicit list preserves order.

RED evidence: `final-review-red.log` (31 tests; 11 failing subcases). Each finding then passed its focused run: `review-status-green.log`, `review-cli-green.log`, `review-codes-green.log`. Whole benchmark suite after all fixes: `benchmark-final.log`, 31/31 pass. Full affected regression and real pipeline evidence are linked from README. Fixes do not approve real labels, rights or a split.

## Declined to judge and executor rulings

Every declined behavior is retained as a dated `Final: Ruling:` in `progress.md`:

- Preview/cancel/stale render: not implemented in Phase 1; remains S06/S14.
- Cold load/worker spawn/Windows packaging: remains S06/S18.
- Guidance/VI/claim/context gate: remains the knowledge branch; no allowed claims produced here.
- DPI/accessibility/privacy UI/full-disk/read-only runtime/native E2E: no corresponding app surface exists yet; CLI proof does not cover it.
- Scientific label/leaf/ToMV–TMV correctness or legal efficacy: technical review does not grant specialist authority.
- Real benchmark quality/full10 balance/preprocessing/model: no approved real split or training exists.
- Whole 140-test pre-review total and raw rehash: reviewer only independently ran 27; executor runs and preserves real commands/logs, without calling that independent replication.

Technical findings addressed by tests in one pass; no re-review requested. S02/S03 may move to `built` after final evidence checks. S04/full Phase 1 remain incomplete behind C2 and rights. There are no deferred minor findings from this review.
