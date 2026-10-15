# Kiểm định proposal ticket trước checkpoint

Ngày 14/10/2026; proposal revision 2. Phạm vi chỉ tài liệu planning, không kiểm định mô hình, lời khuyên chuyên môn hoặc phần mềm đã chạy. Các finding/trạng thái dưới đây ghi tại thời điểm trước duyệt; kết quả sau duyệt nằm ở phần cuối.

## Phương pháp

Theo `bmad-ticket/references/validate.md`, người lập proposal tự kiểm Dependencies trước, rồi sáu agent độc lập kiểm Ticket/Set/Dependencies theo epic; một agent độc lập kiểm Tree/Dependencies. Custom checks của bản local rỗng. Các reviewer chỉ đọc, không sửa dữ liệu hoặc chạy workflow triển khai. Chưa có `tickets.toml`, nên board hiện tại vẫn có 0 ticket; không coi graph tự kiểm là validation của store đã nhập.

## Finding và xử lý

| Phạm vi | Finding | Xử lý trong revision 2 | Trạng thái |
| --- | --- | --- | --- |
| EP-A | S01 chưa có tracer, S01–S03 thiếu uncertainty riêng | Tracer record grouped/ungrouped qua provenance/rights tới eligibility/refusal; ghi uncertainty từng entry | Reviewer đã xác nhận giải quyết |
| EP-B | S05 kiểm full T05 có thể chờ S06 theo vòng; selection S09 thiếu owner CPU profile trước lock | S05 kiểm eval-side, S06 kiểm app parity; S09 đo validation/fixture trước lock, S15 kiểm cuối | Reviewer đã xác nhận giải quyết |
| EP-B | Handoff harness/config và references experiments chưa trực tiếp | S05 sở hữu harness; S07/S08 dùng config/run riêng, thêm references | Reviewer đã xác nhận giải quyết |
| EP-C/EP-D | Runtime không có semantics hoàn thành một phần S10/S11 để mở S06 | S10/S11 là scope thẻ đầu; đề xuất S10b/S11b giữ scope còn lại; S06 pin S11 thật | Hai reviewer đã xác nhận draft kỹ thuật; split vẫn chờ người dùng |
| EP-C/EP-D | Positive path và tracer education/handoff chưa rõ | Một card EN–VI/lesson/quiz draft nối lookup refusal ở S10; S11 review scope thật; S06 cần card thật được phép và checkpoint sinh viên | Reviewer đã xác nhận giải quyết; hiện chưa có card/checkpoint đó |
| EP-E | S15 thiếu uncertainty; QA native chưa có owner | Ghi C4/CPU/targets/authorization; S06 sở hữu native QA harness/contracts | Reviewer đã xác nhận giải quyết |
| EP-F | S16/S17 thiếu uncertainty; missing-evidence report có thể bị hiểu là nghiệm thu efficacy | Ghi nguồn/quyền/ground truth/reviewer/consent; Done when phân biệt báo cáo giới hạn và efficacy | Đã cập nhật; bản nguồn review không chứng minh hiệu quả ngoài miền/học tập |
| Tree | Opening epic governance chưa nêu ngoại lệ platform-baseline | Notes đề xuất EP-A mở governance; S05/S06/S18 sở hữu nền tảng thực nghiệm/desktop/release | Ngoại lệ chờ người dùng, không giả Decision đã duyệt |
| Tree | Descriptions S13/S14/S15/S18/S19 thiếu handoff máy đọc | Nêu provider/output và downstream consumer trong JSON | Đã cập nhật, không đổi graph/ID |
| Set/Tree | Membership S15/S17, split S10/S11, không thêm Refactor sweep, S20 optional | Tập hợp trong `decisions_pending` và proposal cho một checkpoint | Chờ người dùng |

## Bằng chứng và giới hạn

- `draft-dependency-check.json`: 6 epic, 22 entry, 20 ID gốc được giữ, 0 missing prerequisite/cycle/reference/coverage/order problem trong các kiểm tra đã chạy. Không phải chứng minh mọi dependency tương lai đã đầy đủ.
- `continuation-integrity.json`: 42 input snapshots không đổi; 25 file theo integration seal không mismatch. Không rehash toàn corpus raw hoặc kết luận raw chưa từng thay đổi trước baseline.
- Spec đã được người dùng duyệt với lời trả lời “Duyệt spec, tiếp tục planning ticket”. Quyền chỉ planning; B0/stack/C3/targets/data readiness vẫn pending.
- 22 lookup tests là kết quả lịch sử phiên review dữ liệu, không chạy lại trong phiên planning này. Chưa chạy model, native UI, clean-machine hoặc user/expert study.

Tại thời điểm trước duyệt, proposal đủ để trình lựa chọn ticket; chưa đủ để ghi tập ticket chính thức khi thiếu checkpoint theo skill.

## Sau checkpoint và ghi store

Người dùng đã trả lời “Duyệt proposal, ghi kế hoạch chính thức”. Các ask về membership, split, sweep và ngoại lệ platform đã được ghi Decision ở initiative/epic. Không coi đây là duyệt B0/stack/C3/targets, dữ liệu hoặc quyền implementation/train.

Actual `tickets.py status`: 22/22 planned, sáu epic; không problems, drift, unpinned_after, undeclared_after hoặc order_conflict. Actual `next`: chỉ EPA.S01 ready_to_start, 21 entry blocked bởi prerequisites/unknown. Đây là readiness của board, không phải quyền bắt đầu sản phẩm.

Runtime ban đầu từ chối epic ID có dấu `-`. Đã ghi alias canonical EP-A…EP-F sang runtime EPA…EPF trong `ticket-runtime-compatibility.json`, giữ nguyên 22 story IDs, thứ tự, scope và graph; không sửa vendor. Sau chuẩn hóa, status/next chạy thành công. Không claim rằng proposal graph check trước đó đã kiểm được quy tắc ID của TOML runtime.

Registry `official_planning_imported=true` chỉ là marker tiếp nhận planning; subtree datasets, current_run, counts, training_ready và safe_for_advice giữ nguyên. Input integrity cuối và hash bộ tài liệu được lưu riêng. Không có Git metadata nên chưa commit/publish; hồ sơ được ghi local, không giả publish tracker.
