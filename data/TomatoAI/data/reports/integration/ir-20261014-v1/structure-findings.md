# Lens structure — giữ đủ sáu khuyến nghị

Tài liệu đầu vào: README 1.634 từ, tri thức 1.457 từ, kiến trúc 1.571 từ; tổng 4.662 từ theo reviewer. Đây là số đo tài liệu, không phải metric chất lượng dữ liệu. Không đặt mục tiêu rút ngắn. Không chạy prose vì không yêu cầu copy-edit.

| Pass | Original Text | Revised Text | Changes / quyết định lượt này |
| --- | --- | --- | --- |
| structure | knowledge-localization-edtech.md:28, Trạng thái review và phạm vi phát hành, 200 từ | MOVE trước workflow dịch–kiểm duyệt | Điều kiện hiển thị là tiền đề; giữ C3/S11, source_checked/expert_approved. Hoãn sửa cấu trúc; báo cáo review nêu gate trước. |
| structure | README.md:29, lịch sử BMAD, 569 từ | MOVE sau quyết định hiện hành | Không xóa lịch sử. Lượt này chỉ thêm checkpoint mới phía trên; hoãn chuyển mục. |
| structure | README.md:63, “bắt đầu PlantVillage”; mục 265 từ | QUESTION: xác định checkpoint 13/10, liên kết kết quả hiện hành | Đã bổ sung checkpoint hiện hành, giữ nguyên văn lịch sử; không rerun cleaning. |
| structure | architecture.md:7–29, so sánh stack và AD-1…AD-8, 499 từ | MOVE AD vào mục riêng | Hoãn editorial; bảo toàn toàn bộ ID và quyết định. |
| structure | architecture.md:63, contract 316 từ | PRESERVE | Bảng invariant/version phục vụ kiểm thử, giữ nguyên. |
| structure | knowledge-localization-edtech.md:45, đánh giá tư vấn 205 từ | PRESERVE | Giữ giới hạn: metadata tests không chứng minh đúng chuyên môn. |

Các phát hiện lặp giữa adversarial và edge-case vẫn giữ riêng trong lens-findings.json. findings.json là triage bổ sung theo yêu cầu người dùng, không thay thế đầu ra từng lens. Các bản diễn đạt trong JSON đã rút gọn nhưng giữ đủ trigger, guard và consequence; đường dẫn card được resolve theo registry/run ghi trong review-input.md.
