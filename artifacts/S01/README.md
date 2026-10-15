# Báo cáo thực hiện Phase 0 / EPA.S01

Ngày 15/10/2026, Asia/Bangkok. Chỉ thực hiện Phase 0 được người dùng cho phép. Đây là evidence cho kế hoạch BMAD chính thức, không phải báo cáo huấn luyện hoặc nghiệm thu app.

## Quyết định và đầu ra

- [Decision ledger](../../docs/development/decisions.md): nhóm ba người làm mỗi tối; bảo vệ khoảng hai tháng, chưa ngày/rubric/giờ cụ thể. Không đăng nhập; hồ sơ/lịch sử local tùy chọn, history mặc định tắt.
- [Rights ledger](../../docs/development/assets-rights.json): sáu dataset, 17 thẻ tri thức riêng, hai pretrained weights ứng viên, font hệ thống, code dự án từng software dependency và ba mục runtime CPython/MSVC/Windows ICU. Tổng hiện tại 51 mục; không bao gồm phê duyệt license cho mọi component vendored của gói release tương lai. Có nguồn/hash hoặc ghi rõ thiếu; không tự duyệt quyền hoặc chuyên môn.
- [Compatibility](../../docs/development/compatibility.json), [lock](../../requirements-app.lock): môi trường riêng `.venv-phase0`, không nâng runtime cleaning. EfficientNet-B0 là baseline kỹ thuật cùng ResNet50; chưa chọn winner.
- [Tracer hai record thật](governance-trace.json): hash raw/processed khớp manifest và rights pointer; record có/thiếu bằng chứng nhóm khác nhau. Cả hai vẫn `training_eligible=false` vì chưa approved split/rights/review.

## Kiểm tra đã thực hiện

| Kiểm tra | Kết quả / bằng chứng |
| --- | --- |
| TDD diagnostic | Red quan sát trước khi có implementation: [red-check.txt](red-check.txt). GREEN cuối: 2/2 source và frozen regression pass, xem [native-test.log](native-test.log). Frozen RED thực tế và hai nguyên nhân được giữ trong log |
| Data regression, sáu module | CPython bundled 3.12.14: 82 tests, OK, trong đó 10 production checks skipped; [data-regressions.log](data-regressions.log) |
| UC-IPM collector regression | uv default CPython 3.14.7: 31 tests, OK; [collector-regressions.log](collector-regressions.log) |
| Aggregate discovery probes | Chưa pass: uv default thiếu `pdfplumber`; bundled runtime thiếu `jsonschema`. Giữ hai log `existing-data-tests*.log`. Sau đó chạy đủ bảy module bằng hai runtime phù hợp, không sửa dependency cleaning |
| Governance tracer | Exit 0; hai ảnh thật và căn cứ nhóm được hash; không ghi raw hoặc tạo split |
| Bảo toàn | [preservation-after.json](preservation-after.json): 34 file registry, bảy store và integration khớp checkpoint trước. Không đại diện full raw rehash |
| Native Qt / CPU forward / frozen spawn | PASS trên máy Windows 11 hiện tại: source/frozen đều Qt windows exposed/timer true, worker exit 0/PID riêng, hai CPU outputs finite [1,10]; [compatibility](../../docs/development/compatibility.json), [frozen JSON](frozen-smoke.json), [build log](build.log) |

Tổng data regression: **103 pass, 10 skip**, không có lỗi trong hai lần chạy tách runtime cuối cùng. Mười production checks chưa cấu hình `PLANTVILLAGE_REPORT`/report tương ứng; không tính là pass hoặc fresh full corpus verification. Synthetic fixture tests tạo dữ liệu trong thư mục tạm, không chạy cleaning lại raw thật.

## Điều kiện chưa đóng

| Mục | Người xử lý / điều kiện quay lại |
| --- | --- |
| C0 rubric, ngày bảo vệ, giờ/người/tuần | Nhóm hỏi giảng viên và xác nhận khi trường công bố; chưa tự tính tổng giờ |
| C1 compute và budget | Nhóm chốt máy phòng lab/cloud được phép, hạn mức và người sở hữu trước S05. Chưa dùng GPU train hoặc gửi dữ liệu lên cloud |
| C2 grouping/duplicates/split | Người thực hiện S02–S04 và reviewer dữ liệu; chỉ chuyển sang train sau approved class/split manifest |
| C3 chuyên môn, VI, guidance | Nhóm tìm reviewer phù hợp hoặc xin quyết định phạm vi khác ở S11. Hiện chưa có chuyên gia; không tự thay expert approval bằng source_checked |
| Pretrained weights | Người thực hiện S05 kiểm provenance/hash byte/quyền/recipe trước dùng; Phase 0 chỉ đọc enum metadata, không tải weights |
| C5 phát hành | Người thực hiện S18 hoàn thiện quyền từng asset, notices và Windows sạch/offline; bản chạy trên máy phát triển chưa đủ |

Không đo accuracy/F1, khả năng nhận diện ngoài miền, hiệu quả chăm sóc/học tập, latency/RSS acceptance hoặc CUDA training. Không có product E2E: skill e2e hiện hỗ trợ browser/mobile, chưa có config/URL hoặc Qt Windows engine; native diagnostic kiểm đúng phần Phase 0.

## Chạy lại

Các lệnh môi trường và diagnostic nằm trong [decisions](../../docs/development/decisions.md). Log cài và build giữ nguyên trong thư mục này. `requirements-app.lock` kèm hash; native/frozen JSON và software inventory ghi actual versions. Build diagnostic giữ ở `artifacts/S01/dist`, không là gói phát hành. [Native runtime inventory](native-runtime-inventory.json) ghi hash/source/version của 113 binary; Windows ICU không được bundle. [Governance verification](governance-verification.json) kiểm 17 cặp raw/source-copy và 162 file license cài thực tế. Các số này không thay cho expert review hoặc license clearance.

Hai lỗi đóng gói đã được tái hiện và sửa: ICU từ Poppler trên PATH gây QtCore thiếu procedure; hook contrib cũ thiếu hai extension `_C_stable`/`image_stable` của torchvision 0.29. Build helper giới hạn PATH cho tiến trình con và thêm đúng hidden imports, không vá vendor. Còn warning optional TensorBoard, tên extension cũ và tham chiếu Linux không dùng; xem build log. Không dùng warning suppression làm bằng chứng pass.

S01 có đủ năm đầu việc Phase 0 với các blocker ngoài phiên được ghi rõ; runtime BMAD đã ghi `built` sau kiểm chứng và [review độc lập cuối](final-review.md), không tự ghi `done`. Review không có Critical/Important; hai Minor tài liệu được ghi hoãn trong review và ledger. Lệnh tái tạo cần đúng CPython 3.12.14; đoạn Stack cũ của PRODUCT.md chưa đồng bộ, decisions/compatibility là baseline hiện hành. Các phase sau chưa được thực hiện.
