---
id: SPEC-tomato-desktop
companions:
  - data-readiness.md
  - requirements-traceability.md
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
- CNN chỉ phân loại ảnh. Tri thức tra cứu theo mã chuẩn và review policy riêng; không tự sinh chăm sóc, suy mức độ bệnh/giai đoạn/giống/năng suất/lây lan.
- Giữ raw, processed đã chốt, biên bản và ID CAP/FR/NFR/AD/S/T. Class manifest hiện chỉ là đề xuất; checkpoint tương lai phải lưu và xác minh thứ tự/version/hash. S10/S11 là scope thẻ đầu; S10b/S11b giữ phần còn lại, S15 thuộc EP-E và S17 thuộc EP-F theo slicing đã duyệt.
- Split theo cùng lá/trùng/biến thể trước augmentation; fit train, chọn validation, khóa winner/threshold trước test. Ảnh chưa đủ group evidence không được split ngẫu nhiên.
- Readiness và số liệu hiện hành tại [data-readiness](data-readiness.md) thay khảo sát sơ bộ; không nâng `cleaned_technical` thành training/advice-ready.
- Hai tháng, làm mỗi tối; máy người dùng khai báo Ryzen 5 5625U/RAM 16 GB/RTX 3050 VRAM 4 GB; Colab chỉ là compute training tùy chọn.
- Quyền lượt này chỉ Prompt 3 planning. Không code sản phẩm, tải thêm, dịch hàng loạt hoặc train; mọi story là công việc tương lai, cần quyền giai đoạn tương ứng.

## Non-goals

- Tối ưu năng suất/nước/phân bón/chi phí, dùng WUR/Dryad/Mendeley suy lịch tưới/liều bón, IoT hoặc dự báo canh tác.
- Nhận diện giống cây, xét nghiệm/chẩn đoán xác nhận, severity, phân đoạn, năng suất hoặc tình hình dịch bệnh diện rộng.
- LLM/chatbot/vector database, tư vấn supervised chưa có dữ liệu phù hợp, ensemble/SVM mặc định, nhiều cây trồng, 3D, runtime cloud và train trong app.
- Thuốc/liều/lịch phun/thời gian cách ly thiếu căn cứ phù hợp Việt Nam. Lịch sử S20 tùy chọn, không chặn core.

## Success signal

Lát cắt S06 dùng một ảnh, checkpoint do sinh viên huấn luyện và một bản ghi tri thức được phép theo policy đã duyệt, chạy offline và xử lý invalid/cancel/knowledge blocked. Hoàn thành đồ án khi hai model có benchmark/selection/test minh bạch, bundle qua Windows sạch và hướng dẫn/học tập có bằng chứng riêng; phần chưa kiểm chứng phải ghi rõ và chặn acceptance liên quan.

## Assumptions

- Một sinh viên, hai giờ mỗi tối, tám tuần: 112 giờ nhân công, 95 giờ core +17 giờ dự phòng; chưa xác nhận team/số giờ/ngày bảo vệ.
- B0, PyTorch/torchvision, PySide6 Widgets, PyInstaller onedir và một winner triển khai là đề xuất AD-1/AD-2; chưa khóa version, framework compatibility hoặc ngân sách.

## Open Questions

- C0/C1: rubric và cách diễn giải “thẩm định”; duyệt biến thể/stack/limits/metric targets/budget trước story phụ thuộc.
- C2: grouping Target Spot/mosaic, near-duplicate và nhãn ảnh; phục hồi có bằng chứng hay thay phạm vi benchmark bằng quyết định rõ ràng?
- C3: draft cho phép educational demo `source_checked`; card thật hiện `safe_for_advice=false`. Có duyệt policy demo riêng và claim cụ thể hay phải có chuyên gia trước mọi guidance? Hiện giữ chặn.
- C4/C5: external/OOD ground truth, reviewer, người học thử, máy Windows sạch và quyền phân phối từng asset chưa đủ. Chặn đúng acceptance; nghiên cứu canh tác/UC IPM không là phụ thuộc MVP.
