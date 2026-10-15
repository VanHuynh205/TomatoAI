---
id: SPEC-tomato-desktop
companions:
  - data-readiness.md
  - requirements-traceability.md
  - ../app-development-plan/app-development-plan.md
  - ../app-development-plan/engineering-contracts.md
  - ../app-development-plan/ux-security.md
  - ../../../planning/tomato-desktop/product-brief.md
  - ../../../planning/tomato-desktop/data-audit.md
  - ../../../planning/tomato-desktop/research.md
  - ../../../planning/tomato-desktop/prd.md
  - ../../../planning/tomato-desktop/ux-desktop.md
  - ../../../planning/tomato-desktop/architecture.md
  - ../../../planning/tomato-desktop/experiments.md
  - ../../../planning/tomato-desktop/knowledge-localization-edtech.md
  - ../../../planning/tomato-desktop/security-testing.md
  - ../../../planning/tomato-desktop/delivery-plan.md
sources:
  - ../../../planning/tomato-desktop/planning-spec.md
---

# Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua

Contract BMAD được dẫn xuất từ quyết định ghi bằng `memlog.py` và các nguồn tham chiếu ngày 14/10/2026. Spec và proposal ticket revision 2 đã được người dùng duyệt; kế hoạch chính thức gồm sáu epic/22 entry, giữ 20 ID story gốc và thêm S10b/S11b. Approval này không đồng nghĩa được phép triển khai hoặc dữ liệu đã sẵn sàng. Các companion phải được đọc cùng kernel.

Cập nhật planning `adp-20261014-v1` dẫn xuất từ direction/decisions mới trong memlog: [kế hoạch phát triển app](../app-development-plan/app-development-plan.md) chia Phase 0–9, giữ nguyên CAP/FR/NFR/AD/story và graph ticket. Người dùng chốt dùng trực tiếp không đăng nhập, hồ sơ/history local tùy chọn, lập kế hoạch theo Python/PySide6/PyTorch và khóa phiên bản/compatibility ở Phase 0. Đây là chi tiết công việc tương lai và định hướng stack cho planning, không phê duyệt targets/B0/policy C3 hoặc khởi động code/train.

## Why

Người Việt cần hỗ trợ quan sát trạng thái lá cà chua và học chăm sóc có nguồn bằng desktop offline. Sinh viên cần chứng minh quy trình dữ liệu, transfer learning hai CNN, so sánh công bằng và tích hợp tri thức có kiểm duyệt. “Thẩm định” là hỗ trợ kiểm tra ảnh/đối chiếu dấu hiệu và giới hạn; không xác nhận tác nhân bằng xét nghiệm hoặc nhận diện giống cây.

## Capabilities

- **CAP-1**
  - **intent:** Chuẩn bị benchmark ảnh có provenance, grouping và split hợp lệ.
  - **success:** T15 chứng minh giao group/component giữa các tập bằng rỗng; mọi inclusion/exclusion và vấn đề chưa giải quyết có căn cứ.
- **CAP-2**
  - **intent:** Sinh viên huấn luyện và so sánh EfficientNet với ResNet50.
  - **success:** Hai kiến trúc có head/fine-tune, config/log/checkpoint trên cùng split và ngân sách; chọn cấu hình/model bằng validation trước test.
- **CAP-3**
  - **intent:** Nhận diện ảnh lá local với giới hạn và trạng thái không kết luận.
  - **success:** T01–T06/T10 kiểm đúng ảnh/request/status; ảnh invalid, kết quả không được chấp nhận hoặc đã hủy không tạo hướng dẫn bệnh.
- **CAP-4**
  - **intent:** Tra cứu hướng dẫn phù hợp từ mã trạng thái chuẩn.
  - **success:** T07–T09 kiểm mapping chính xác hoặc chặn có lý do; chỉ claim đúng nguồn/context/version/review scope được hiển thị, không ghép top-k.
- **CAP-5**
  - **intent:** Hiển thị tiếng Việt dẫn xuất được rà soát, giữ nguồn tiếng Anh và ID.
  - **success:** Bản EN–VI, glossary và ledger truy vết source/hash/revision/actor/role; raw và processed đã chốt không bị sửa.
- **CAP-6**
  - **intent:** Hỗ trợ học dấu hiệu, nguyên nhân và phòng/chăm sóc.
  - **success:** Lesson/quiz có LO1–LO3, đáp án và feedback theo nguồn; hiệu quả học chỉ được báo khi có đánh giá người học thật.
- **CAP-7**
  - **intent:** Chạy desktop Windows offline ổn định và dùng được bằng bàn phím.
  - **success:** T10–T13/T18/T19 kiểm giới hạn worker, hủy, máy sạch, không tải/upload, tiếng Việt và DPI.
- **CAP-8**
  - **intent:** Đánh giá ảnh nội miền/ngoài miền, hướng dẫn và học tập riêng.
  - **success:** Báo metric/support/provenance thực đo hoặc báo thiếu bằng chứng; lookup test không thay đánh giá model/chuyên môn.
- **CAP-9**
  - **intent:** Bảo vệ đồ án bằng artifact truy vết được.
  - **success:** FR/NFR có story/test/evidence; báo cáo, license ledger, data/model card và demo nhất quán với kết quả và giới hạn.

## Constraints

- Cà chua; phạm vi classifier hiện có 10 nhãn, chưa có benchmark 10 lớp được duyệt. Healthy là trạng thái lá; nhện là tác nhân gây hại.
- Windows desktop, tiếng Việt, offline sau cài; không website, AI API hoặc translation API. Hai kiến trúc cố định EfficientNet/ResNet50; không tự chọn thêm model.
- Dùng trực tiếp không đăng nhập theo xác nhận người dùng; hồ sơ và lịch sử local tùy chọn, mặc định history tắt. Profile không là tài khoản bảo mật; không thêm online accounts hoặc sync.
- CNN chỉ phân loại ảnh. Tri thức tra cứu theo mã chuẩn và review policy riêng; không tự sinh chăm sóc, suy mức độ bệnh/giai đoạn/giống/năng suất/lây lan.
- Giữ raw, processed đã chốt, biên bản và ID CAP/FR/NFR/AD/S/T. Class manifest hiện chỉ là đề xuất; checkpoint tương lai phải lưu và xác minh thứ tự/version/hash. S10/S11 là scope thẻ đầu; S10b/S11b giữ phần còn lại, S15 thuộc EP-E và S17 thuộc EP-F theo slicing đã duyệt.
- Split theo cùng lá/trùng/biến thể trước augmentation; fit train, chọn validation, khóa winner/threshold trước test. Ảnh chưa đủ group evidence không được split ngẫu nhiên.
- Readiness và số liệu hiện hành tại [data-readiness](data-readiness.md) thay khảo sát sơ bộ; không nâng `cleaned_technical` thành training/advice-ready.
- Người dùng xác nhận ngày 15/10/2026: nhóm ba người làm mỗi tối, bảo vệ khoảng hai tháng nữa, chưa ngày cụ thể; laptop sinh viên hạn chế. Máy phiên này có Ryzen 5 5625U/RAM khoảng 16 GB/RTX 3050 VRAM 4 GB; chưa xác nhận compute train chung. Cloud/Colab chỉ là phương án cần chốt quyền/budget.
- Quyền hiện hành ngày 15/10/2026: thực hiện Phase 0/EPA.S01, gồm hồ sơ quyết định/quyền và môi trường/spike tương thích riêng. Không train, tải pretrained weights/dataset mới, dịch hàng loạt hoặc xây app sản phẩm. Phase sau cần quyền tương ứng; xem [quyết định Phase 0](../../../docs/development/decisions.md).

## Non-goals

- Tối ưu năng suất/nước/phân bón/chi phí, dùng WUR/Dryad/Mendeley suy lịch tưới/liều bón, IoT hoặc dự báo canh tác.
- Nhận diện giống cây, xét nghiệm/chẩn đoán xác nhận, severity, phân đoạn, năng suất hoặc tình hình dịch bệnh diện rộng.
- LLM/chatbot/vector database, tư vấn supervised chưa có dữ liệu phù hợp, ensemble/SVM mặc định, nhiều cây trồng, 3D, runtime cloud và train trong app.
- Thuốc/liều/lịch phun/thời gian cách ly thiếu căn cứ phù hợp Việt Nam. Lịch sử S20 tùy chọn, không chặn core.

## Success signal

Lát cắt S06 dùng một ảnh, checkpoint do sinh viên huấn luyện và một bản ghi tri thức được phép theo policy đã duyệt, chạy offline và xử lý invalid/cancel/knowledge blocked. Hoàn thành đồ án khi hai model có benchmark/selection/test minh bạch, bundle qua Windows sạch và hướng dẫn/học tập có bằng chứng riêng; phần chưa kiểm chứng phải ghi rõ và chặn acceptance liên quan.

## Assumptions

- Giả định cũ một sinh viên/112 giờ được thay bằng xác nhận nhóm ba người; số giờ/người/tuần và rubric/deadline vẫn chưa có. Không nhân ngân sách cũ lên ba để giả estimate đã duyệt.
- Python/PySide6/PyTorch giữ theo quyết định người dùng; Phase 0 kiểm CPU/build baseline và chọn B0 làm variant kỹ thuật. Pretrained rights/hash, CUDA/train compute, targets/budget vẫn cần khóa trước S05. Một winner triển khai giữ theo AD-2 và selection validation.

## Open Questions

- C0/C1: rubric và cách diễn giải “thẩm định”; duyệt biến thể/weights/versions/compatibility/limits/metric targets/budget trong hướng stack đã chọn trước story phụ thuộc.
- C2: grouping Target Spot/mosaic, near-duplicate và nhãn ảnh; phục hồi có bằng chứng hay thay phạm vi benchmark bằng quyết định rõ ràng?
- C3: người dùng xác nhận chưa có chuyên gia cà chua. Draft educational demo `source_checked` chưa được duyệt; card thật hiện `safe_for_advice=false`. Giữ chặn guidance; không tự đổi policy hoặc gắn expert approval. S11 phải giải quyết policy/reviewer/claim cụ thể.
- C4/C5: external/OOD ground truth, reviewer, người học thử, máy Windows sạch và quyền phân phối từng asset chưa đủ. Chặn đúng acceptance; nghiên cứu canh tác/UC IPM không là phụ thuộc MVP.
