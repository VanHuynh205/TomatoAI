# Rà readiness Phase 0–2 và thứ tự tháo gỡ

Ngày 15/10/2026. Phạm vi: các bước đã thực hiện S01–S04/S10 và phần kỹ thuật S11; không phải audit toàn bộ codebase. Người dùng xác nhận chưa có lượt kiểm nguồn/VI của người thật. S11 chưa thể hoàn thành trước khi có đầu vào đó, nên báo cáo này rà các phần trước sau khi kiểm xong nhánh từ chối S11, không chờ hoặc giả biên bản duyệt.

## Kết quả kiểm thực chạy

Parent chạy lại bằng `.venv-phase0/Scripts/python.exe` (CPython 3.12.14):

| Phạm vi | Kết quả | Log mới |
| --- | --- | --- |
| Phase 0 source + executable Qt chẩn đoán | 2/2 pass; window/event loop, worker spawn, hai CPU forward `[1,10]`, không weights/train | [parent-phase0.log](parent-phase0.log) |
| Benchmark pipeline | 31/31 pass; grouping/refusal/split synthetic và bảo vệ CLI | [parent-phase1.log](parent-phase1.log) |
| Knowledge preparation | 19/19 pass: 8 S10, 11 S11 | [parent-knowledge.log](parent-knowledge.log) |
| Lookup niêm phong hiện có | 22/22 pass; fixture positive lịch sử không là approval thật | [parent-lookup.log](parent-lookup.log) |
| Artifact thật | Draft tái tạo giống saved JSON, CLI exit 2 đúng năm blocker, nội dung rỗng; 122/122 file baseline không đổi hash | [parent-preservation.log](parent-preservation.log) |

Tổng **74 test pass trong lượt này**. Không cộng lại 144 test cleaning lịch sử thành kết quả mới. Không rehash toàn raw hoặc sửa pipeline cleaning. E2E runner thực chạy nhưng dừng `CONFIG_NOT_FOUND`, zero test, không report: [log](e2e-attempt.log). Chưa có config/URL/flow app Qt sản phẩm; CLI tests và diagnostic window không thay native E2E. Chưa chạy lint/type checker vì không có cấu hình task. Không train, download weights hoặc mở test set.

## Việc chưa xong và hướng xử lý

| Ưu tiên | Evidence hiện có / chỗ thiếu | Hướng xử lý tốt nhất hiện tại | Điều kiện đóng / người xử lý đề xuất |
| --- | --- | --- | --- |
| 1 — S11 / C3 | Hướng limited demo đã chọn; source, EN–VI/glossary/lesson/quiz và rights đều chưa được người thật kiểm. Cổng chỉ từ chối, chưa có positive publisher | Dùng [checklist hiện có](../publication-review-checklist.md). Thành viên/peer đọc nguồn và kiểm bản dịch theo hai lượt riêng, ghi vai trò thật; không cần giả chuyên gia cho scope demo này. Giữ đúng một claim phi hóa học | Người review ghi actor/role/date, URL/section, nhận xét từng phần và hashes/version; quyền dùng có căn cứ/phạm vi thật. AI không tự ký |
| 1 — S04 / C2 | [Audit Phase 1](../../phase1/completion-audit.json): 8 lớp có ít nhất ba technical components; Target Spot 1.404 ảnh và mosaic 373 ảnh đều 0 eligible component; labels đều chưa verified. Không có approved assignments | Không random split hoặc tự gán leaf ID. Ưu tiên trình nhóm/giảng viên **đề xuất pilot 8 lớp riêng** để tránh chờ vô hạn. Giữ full10 là mục tiêu còn thiếu; chưa tự áp dụng đề xuất | Quyết định scope thật; review nguồn nhãn/class order, seed/ratios/rule và hash grouping; rights train rõ. Nếu duyệt pilot: manifest/output head đúng 8, report exclusions và giới hạn; tuyệt đối không báo metric full10 |
| 1 — S05 / C1 | Laptop hạn chế; CPU smoke đã pass, chưa có GPU/time budget/quyền pretrained assets và training environment | Nhóm chốt máy phòng lab/GPU được phép dùng, quota/thời lượng và giới hạn chi phí trước pilot. Đầu tiên đo một pilot có giới hạn cho hai kiến trúc sau S04 | Có người phụ trách compute, quyền dùng máy/dữ liệu, nguồn/hash/rights weights, lock train tương thích và budget/run config. Không tự đăng ký cloud, upload dataset hoặc chi tiền |
| 2 — S03 data review | Grouping nguồn là bằng chứng kỹ thuật, chưa là xác minh bệnh/lá độc lập; 10 near-pair còn chờ kiểm. Upstream audit trước chưa tìm được grouping đầy đủ | Review từng pair bằng ảnh/metadata thật, ghi quyết định và lý do; quarantine unresolved. Chỉ điều tra upstream tiếp khi có revision/metadata mới | Quyết định có người/role/date/evidence, grouping derivative mới; complete components không cross split. Không đổi raw hoặc ép alias mosaic ToMV/TMV |
| 2 — S01 / C0 | Nhóm ba người, mỗi tối, khoảng hai tháng; chưa deadline/rubric/giờ/người/tuần chính xác | Bổ sung khi trường/nhóm xác nhận; chia trách nhiệm dữ liệu/model, app, tri thức/QA. Ưu tiên core, giữ S20 history/profile ngoài đường găng | Nhóm xác nhận lịch và người sở hữu thật. Không suy thành deadline hoặc ngân sách giờ đã cam kết |
| Theo milestone — C4/C5 | Chưa ground truth ngoài miền, người học, máy Windows sạch và notices/quyền release đầy đủ | S16/S17 ghi evidence hoặc missing-evidence report; S18 kiểm gói offline với notices theo asset thật. Không dùng F1 ảnh làm learning/care efficacy | Người tham gia/role thật và protocol phù hợp; kiểm clean Windows/offline; phạm vi phát hành được chốt. Không gọi demo là khuyến cáo nông học đã xác nhận |

Tám lớp có grouping kỹ thuật là Bacterial spot, Early blight, Late blight, Leaf Mold, Septoria, Spider mite, Yellow curl và healthy. Đây chỉ là căn cứ **đề xuất** pilot; chưa phải scope đã được duyệt hoặc nhãn đã được xác nhận. Seed 42, targets 70/15/15 hiện cũng chỉ nằm trong `split-policy.pending.json`. Đổi seed không giải grouping thiếu.

## Cách hoàn tất S11 sau lượt review thật

1. Lưu biên bản review có nguồn, phạm vi và phiên bản thật; không sửa `approvals.pending.json` thành bằng chứng được duyệt. Packet hiện tại chỉ là schema phục vụ từ chối, không chứng thực danh tính.
2. Lesson v1 còn câu “chưa có review độc lập” và “chưa được phép hiển thị”. Khi kết luận review thay đổi nội dung, tạo derivative version mới, hashes mới và rà lại phần bị ảnh hưởng. Giữ draft/input/C3 v1 để truy vết; không chỉ bật một boolean.
3. Ghi quyết định publication mới gắn đúng content/rights/review version; giới hạn một claim, nguồn, nhãn demo và leaf-only. Hướng C3 đã chọn không phải quyền đóng gói hoặc public release.
4. Triển khai positive publisher và kiểm card thật; không xuất nguyên `CardDraft.lookup_bundle` chứa 17 card/172 claim. Negative matrix phải giữ xanh; metadata tự khai không được tự mở gate.
5. Kiểm positive lookup thật theo contract C3; sau đó mới bàn giao allowed artifact cho S06 khi S04/S05 cũng đủ. Runtime thuần được xử lý ở S06, không import cleaning/preparation vào executable.

## Sửa ngay trong lượt rà này

- `PRODUCT.md` đã phản ánh B0 và compatibility CPU thực có; cập nhật C3 direction selected nhưng S11 còn blocked.
- `docs/development/decisions.md` dùng `uv venv --python 3.12.14` để tái tạo đúng patch; giữ điều kiện chỉ tạo khi environment chưa tồn tại.
- Companion contracts sửa trạng thái B0 cũ và phân biệt response refusal preparation với runtime KnowledgeBundle dự kiến.
- Kế hoạch phase, traceability và checklist bổ sung checkpoint S11 một phần cùng đường dẫn bằng chứng/recovery. Không đổi graph, ID, ticket store, raw, rights hoặc approval.

Các bản trước sửa lưu ở [baseline-docs](baseline-docs/manifest.json). Lỗi kiểm/code cũ trong Phase 0/1 đã có regression và lượt này vẫn pass; không mở refactor mới khi không có bằng chứng lỗi. Blocker còn lại cần quyết định hoặc evidence ngoài code, không thể đóng bằng tăng số test. Hành động gần nhất là lượt kiểm nguồn/VI thật trong nhóm; đồng thời chuẩn bị quyết định pilot/compute trước khi yêu cầu Phase 3.
