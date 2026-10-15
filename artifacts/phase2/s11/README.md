# S11 — bằng chứng triển khai một phần

Ngày 15/10/2026. **S11 và Phase 2 chưa hoàn tất.** Chỉ có publisher chuẩn bị với nhánh từ chối; chưa có `allowed` KnowledgeBundle, publisher positive hay lookup runtime cho S06. Không có người thật review nguồn/VI/quyền; không suy approval từ hướng demo C3. AI thực hiện chuẩn bị và kiểm kỹ thuật, không là reviewer độc lập.

`scripts/knowledge/publish.py` tái tạo S10 qua `curate_card`, kiểm tất cả input pin và seal hiện hữu, so full canonical draft hash và saved draft với baseline C3. Policy luôn đọc từ path cố định và so SHA256 bytes pin trong code; path/flag trong packet không đổi trust boundary. Không sửa validator/lookup cũ, draft hoặc sealed input. API/CLI chỉ đọc, stdout JSON, exit 2, không có `--output`.

Packet `approvals.pending.json` là hồ sơ pending version `s11-approvals-pending-v1`, schema 1 (integer, không nhận bool). Các key chính xác: `schema_version`, `version`, `draft_sha256`, `policy`, `prepared_by`, `source_review`, `translation_review`, `rights_scope_review`. Policy gồm `path`, `sha256`; `prepared_by` ghi actor/role AI thực tế. Mỗi review có `status`, `actor`, `role`, `reviewed_sha256`; cả ba hiện `pending` và ba metadata còn lại null. Hash draft bao gồm EN/VI/glossary/lesson/quiz và metadata lồng. JSON tối đa 2 MiB, không key trùng hoặc NaN/Infinity. Mọi field thừa, kể cả skip flag, bị từ chối.

Đây không phải schema chứng thực approval. `approved`/`rejected` chỉ được phân tích để báo lý do âm; kể cả metadata trông hợp lệ cũng bị `review_approval_unverified`. Tên/role AI hoặc tự review bị `review_actor_not_independent`; thiếu actor/role bị `review_actor_missing`. Không status/config nào mở publication. Không chỉnh packet này để giả hoàn tất review; evidence thật và publisher positive cần công việc tiếp theo theo S11.

CLI dossier thật trả `needs_check`, `claims=[]`, `sources=[]`, `lesson_ids=[]` và đúng năm lý do:

- `source_review_pending`
- `translation_review_pending`
- `rights_scope_review_pending`
- `publication_not_authorized`
- `positive_publisher_unimplemented`

Test có assertion mã riêng cho schema/file/size, stale draft/policy pin, EN/VI/glossary/lesson/lookup metadata drift, chemical/context/card/claim/condition ngoài scope, actor âm, và bất biến input qua API/CLI. Không tạo hoặc dùng approved card tổng hợp cho acceptance S11; suite lookup lịch sử giữ nguyên, kể cả fixture lịch sử vốn có.

Kiểm đã chạy:

| Kiểm | Kết quả | Evidence |
| --- | --- | --- |
| RED publication | fail vì chưa có module `publish` | `red-publication.log` |
| Knowledge | 19/19 pass: S10 8 + S11 11 | `green-knowledge.log` |
| Lookup lịch sử | 22/22 pass | `green-old-lookup.log` |
| CLI thật | exit 2, stderr rỗng, nội dung rỗng và năm lý do trên | `cli-refusal.json`, `cli-refusal-run.json` |
| Preservation | so 122 file baseline; 0 đổi | `preservation-before.json`, `preservation-after.json` |
| E2E runner 0.16.0 | blocked exit 2 `CONFIG_NOT_FOUND`; 0 test chạy, không report | `e2e-attempt.log`, `inventory.json` |

Đã đọc skill e2e và running reference; không có `e2e.config.ts/.mts`, root/frontend `package.json`, URL frontend hoặc UI flow bị tác động. Lệnh thật từ `frontend`: `npx --no-install e2e run --output ../artifacts/phase2/s11/e2e`. Không dựng browser substitute cho CLI/native project. Không cần credential model cho unit/CLI deterministic; E2E dừng ở config, chưa kiểm credential. Không có cấu hình lint/type-check của task; unit/import execution là kiểm Python thực chạy.

Tái lập từ gốc repo bằng PowerShell:

```powershell
.venv-phase0/Scripts/python.exe -m unittest discover -s tests/knowledge -p 'test_*.py' -v
.venv-phase0/Scripts/python.exe -m unittest discover -s scripts/data -p test_review_integration.py -v
.venv-phase0/Scripts/python.exe scripts/knowledge/publish.py
# CLI trên phải exit 2: refusal là kết quả mong đợi.
.venv-phase0/Scripts/python.exe artifacts/phase2/s11/verify-preservation.py
```

Preservation chỉ là 122 file được parent ghi trước S11; không tuyên bố rescan toàn raw. SHA256 ràng buộc baseline local, không xác thực con người hoặc chống người thay cả code/manifest. JSON bounded dùng loader hiện có; API nhận object Python trong process, không phải endpoint công khai.

Bàn giao writer không đổi ticket store/done states hoặc tài liệu cũ. Parent sau đó chạy độc lập 74 test (19 knowledge, 22 lookup, 31 benchmark, 2 source/frozen diagnostic), CLI refusal, draft replay và 122 protected hashes; tất cả kiểm trong scope pass. [Review Quick](review-result.md) không có finding phải sửa hoặc hoãn. [Rà Phase 0–2](prior-phases-review.md) ghi việc chưa xong và hướng xử lý; parent đã sửa tài liệu hiện tại, với snapshot ở `baseline-docs/`. Xem `parent-verification.json`, `document-verification.json` và `delivery-manifest.json` cho bằng chứng cuối; `changed-files.json` là snapshot bàn giao riêng của writer trước thay đổi tài liệu.

Trước khi hoàn tất S11 cần review nguồn/context thật, review EN–VI/glossary/lesson/hai quiz riêng, evidence quyền dùng/đóng gói, rồi triển khai/test positive publisher và card thật được phép. Runtime lookup/native S06 vẫn bị chặn. Plan S11 ghi `blocked`, technical slice verified; không có allowed card hoặc publication approval.
