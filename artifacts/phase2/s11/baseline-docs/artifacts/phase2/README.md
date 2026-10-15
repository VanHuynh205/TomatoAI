# Phase 2 — tracer S10, chưa mở guidance

Ngày 15/10/2026. **S10 đã build và qua review Quick**, không có finding phải sửa hoặc hoãn. Parent chạy độc lập 8 test curation, 22 test lookup; tái tạo draft giống artifact và kiểm 117 file giữ nguyên hash. **Phase 2 chưa hoàn tất**: người dùng đã chọn hướng C3 demo giáo dục giới hạn, nhưng S11 còn chờ review nguồn, nghĩa VI và quyền dùng nội dung. Không đổi ticket store hay tự đánh dấu done.

- Editorial input: [review-inputs.json](../../content/phase2-healthy-v1/review-inputs.json).
- Bundle dẫn xuất: [card-draft.json](../../content/phase2-healthy-v1-bundle/card-draft.json). `lookup_bundle` là bản sao dẫn xuất dùng trực tiếp validator/lookup cũ; EN/cards/mapping/class order không đổi, chỉ claim đã chọn có VI draft. Artifact folder thêm hậu tố `-bundle` để tách input biên tập trong folder `<version>` và từ chối ghi đè bundle hiện hữu.
- [checks.json](checks.json), [CLI thật](cli-output.json), [test thiếu handler](tests-red.log), [curation tests](tests-curation.log), [22 regression lookup cũ](tests-integration.log), [preservation](preservation-after.json).
- [Preview tiếng Việt và hồ sơ C3/S11](s11-decision-dossier.md), [source audit](source-audit.md).
- [Quyết định C3 mới](c3-policy-decision.json), [bảng review để tiếp tục S11](publication-review-checklist.md), [kiểm chứng độc lập của parent](parent-verification.json).

Một management claim: `ir-claim:healthy:cultural:2`, nguyên văn EN “Water at the base of the plant to keep foliage dry.” Bản nháp VI: **Tưới vào gốc cây để giữ lá khô.** Tác giả là Codex, vai trò AI drafting/source checking, ngày 15/10/2026. Đây không phải người review độc lập hay chuyên gia nông học.

Một glossary draft bốn mục, một bài học ba phần và đúng hai câu hỏi có key/giải thích/nguồn. Câu quan sát trỏ vào `/content_en/symptoms/leaves/0` và `/content_en/symptoms/leaves/2`; giới hạn nhãn lá trỏ tài liệu localization của project; câu tưới trỏ claim/pointer riêng. Hash bind raw/card/integration/claim/VI/glossary/lesson/source-check/author provenance. SHA-256 chứng minh byte alignment trong baseline tin cậy, không chứng minh tác giả nguồn, chuyên môn hay nghĩa bản dịch đúng.

`curate_card` chỉ đọc và trả `CardDraft`; CLI mặc định chỉ validate. `--output content/<version>-bundle` mới ghi vào folder chưa tồn tại sau toàn bộ kiểm tra. Không có publisher, policy engine hoặc runtime package mới, không dịch API, không dependencies mới, không đổi sealed validator.

```powershell
.venv-phase0/Scripts/python.exe -m unittest discover -s tests/knowledge -p test_curation.py -v
.venv-phase0/Scripts/python.exe -m unittest discover -s scripts/data -p test_review_integration.py -v
.venv-phase0/Scripts/python.exe scripts/knowledge/curate.py --review-inputs content/phase2-healthy-v1/review-inputs.json
```

Lệnh tạo bundle đã chạy một lần, output lưu trong `cli-output.json`; chạy lại cùng `--output` phải bị từ chối. Bản draft S10 giữ nguyên snapshot `display_allowed=false`, domain/translation review pending, không reviewer và C3/redistribution pending. Quyết định hướng C3 mới được ghi riêng, không sửa lịch sử draft hoặc mở gate cũ. Lookup thật trả guidance rỗng cho cả 10 lớp. Không đo learning gain, usability, ML quality hoặc hiệu quả chăm sóc.

Đã đọc skill `.agents/skills/e2e/SKILL.md` cùng running reference và kiểm cấu hình/runner. Runner e2e 0.16.0 có sẵn tại `frontend/node_modules/e2e/`; launcher `.bin/e2e.cmd` tồn tại. Không có `e2e.config.ts`/`.mts`, frontend URL, app Qt hay UI flow của pipeline JSON/CLI này; E2E UI không chạy. Không dựng browser substitute, không gọi npx để tải runner. `docs/agents/domain.md` không tồn tại; dùng plan/contracts/localization chính thức.

Ruling: workspace không có Git; bằng chứng là manifest/hash/log, không dùng commit/worktree tooling. Mọi checklist/nhãn built chỉ phản ánh S10 preparation; không xác nhận thẻ đã được phép xuất bản. E2E UI chưa chạy; kiểm CLI và lookup đã chạy thật.

S11 chưa triển khai `publish_knowledge` hoặc bundle allowed vì chưa có hồ sơ duyệt đầu vào thật. Theo kế hoạch chính thức, milestone này cần một card thật được phép và positive lookup có evidence thật. Không dùng synthetic reviewer hoặc AI tự duyệt để thay đầu vào còn thiếu. Nhóm có thể phân công thành viên kiểm nguồn/nghĩa VI theo bảng review; demo giới hạn đã chọn không bắt buộc tìm chuyên gia nông học cho riêng phạm vi này. Quyền dùng/đóng gói và kiểm chứng publisher vẫn phải hoàn tất trước khi hiển thị trong app.
