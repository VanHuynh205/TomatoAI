# Planning contract — đầu vào cho bmad-spec

Ngày 13/10/2026. **Bản nháp độc lập, chưa phải kernel BMAD được sinh từ memlog.** Runtime đã setup; chưa tiếp nhận draft trước kết quả làm sạch dữ liệu. Không tạo memlog giả hoặc claim Spec Law đã được workflow self-validate. CAP IDs dưới đây giữ nguyên khi tiếp nhận sau.

**Tên đã chốt:** “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”. Quyết định phạm vi hiện hành tại [README](README.md); nhận diện bệnh/trạng thái lá, hướng dẫn trồng/chăm sóc phù hợp, không thêm tối ưu canh tác. Ba dataset canh tác là tài nguyên nghiên cứu bổ sung, không là yêu cầu MVP.

## Why

Người Việt cần hỗ trợ nhận biết trạng thái lá cà chua và học chăm sóc có nguồn bằng desktop offline. Sinh viên cần chứng minh quy trình dữ liệu, transfer learning và đánh giá hai CNN, không chỉ gọi pretrained inference.

## Capabilities

| ID | Intent | Success |
| --- | --- | --- |
| CAP-1 | Chuẩn bị benchmark có provenance, grouping và split hợp lệ | T15 chứng minh không group/component qua tập; unresolved có quyết định và ledger |
| CAP-2 | Huấn luyện/so sánh EfficientNet và ResNet50 | Hai kiến trúc có head/fine-tune/config/log/checkpoint cùng split/budget; selection record trước test |
| CAP-3 | Chọn ảnh và nhận diện local có giới hạn/từ chối | T01–T06/T10 chạy đúng request/status; non-accepted không guidance theo nhãn |
| CAP-4 | Tra cứu hướng dẫn theo mã chuẩn có nguồn | T07–T09 chứng minh mapping/review policy/context và version, không nhầm nhãn/ghép top-k |
| CAP-5 | Hiển thị VI dẫn xuất, bảo toàn raw EN/ảnh/ID | Bản song ngữ/glossary/review ledger; raw hash giữ nguyên |
| CAP-6 | Hỗ trợ học quan sát–nguyên nhân–phòng/chăm sóc | Lessons/quiz LO1–LO3, feedback đúng; đánh giá formative riêng nếu có người học |
| CAP-7 | Chạy desktop Windows offline ổn định | T10–T13/T18/T19: worker limits, clean-machine, no upload, keyboard/DPI |
| CAP-8 | Đánh giá nội miền/ngoài miền, tư vấn/học tập riêng | Metrics thật/support/provenance; thiếu ground truth/reviewer báo rõ, không metric bịa |
| CAP-9 | Bảo vệ đồ án bằng artifact truy vết được | Report/demo có FR/NFR→story→test→evidence, license/model/data cards và giới hạn |

## Constraints

Cà chua, 10 lớp local đã khảo sát sơ bộ, readiness cần báo cáo làm sạch; CNN chỉ phân loại, tri thức tra cứu có review. Desktop Windows, tiếng Việt, offline sau cài; không website/AI API/dịch API. Hai kiến trúc cố định EfficientNet/ResNet50; B0 và stack là đề xuất. Split trước augmentation theo cùng lá/trùng/biến thể; fit train, chọn bằng validation, test cuối. Raw không sửa. Lượt Setup chỉ cho phép runtime BMAD/dependency cần thiết và cập nhật draft; chưa cho phép làm sạch, code ứng dụng, tải weights hoặc train. Hai tháng mỗi tối, máy khai báo Ryzen5 5625U/RAM16GB/RTX3050VRAM4GB, Colab compute tùy chọn. Chưa có rubric, expert review hoặc field dataset.

## Non-goals

Tối ưu canh tác đã được người dùng loại khỏi phạm vi; nhận diện giống cà chua hoặc xác nhận tác nhân bằng xét nghiệm; mức độ bệnh/năng suất/lây lan; tư vấn supervised/LLM/chatbot/vector DB; thuốc/liều/cách ly thiếu nguồn; ensemble/baseline truyền thống mặc định; nhiều cây, 3D, cloud runtime, training trong app. History là tùy chọn, không chặn core.

## Success signal

Lát cắt một ảnh–một checkpoint sinh viên huấn luyện–một thẻ có nguồn hoạt động offline và có failure states; sau đó hai model có benchmark/selection/test minh bạch, bundle được thử Windows sạch và nội dung học có bằng chứng riêng. Nếu grouping 10 lớp/external labels/expert approval chưa đủ, báo giới hạn hoặc chặn acceptance liên quan thay vì bảo đảm chất lượng giả.

## Companions phải đọc

[data-audit](data-audit.md), [research](research.md), [prd](prd.md), [ux-desktop](ux-desktop.md), [architecture](architecture.md), [experiments](experiments.md), [knowledge-localization-edtech](knowledge-localization-edtech.md), [security-testing](security-testing.md), [delivery-plan](delivery-plan.md). Brief là nguồn bài toán, README là tình trạng tooling. Các companion chứa contract/criteria thật, không duplicate toàn bộ vào kernel.

Sau báo cáo làm sạch và khi được yêu cầu Prompt 3: `bmad-spec` tiếp nhận hồ sơ qua script memlog chuẩn, ghi nguồn/adopted companions, preserve CAP/FR/NFR/AD IDs; tự-validate coherence và preservation thật. `bmad-ticket` chia initiative/epic với `covers` CAP IDs sau đó. Không gọi `bmad-build` trong lượt Setup.
