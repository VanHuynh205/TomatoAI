# Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua

<!-- impeccable:product-schema 1 -->

## Platform

Windows desktop native, offline sau cài. Giá trị này giữ đúng nền tảng đã chốt; không dùng giá trị `web` của template Impeccable để đổi phạm vi sản phẩm.

## Stack

Người dùng xác nhận ngày 14/10/2026: lập kế hoạch theo Python + PySide6 Widgets + PyTorch/torchvision, đóng gói PyInstaller. Kiểm tương thích và chốt phiên bản ở Phase 0. EfficientNet và ResNet50 được giữ; B0, phiên bản package, nguồn weights và ngân sách vẫn cần quyết định có bằng chứng.

## Users

Checkpoint Phase 0 ngày 15/10/2026: nhóm ba người làm mỗi tối, bảo vệ khoảng hai tháng nữa, chưa ngày/giờ cụ thể. Laptop hạn chế và chưa có chuyên gia cà chua. [Quyết định hiện hành](docs/development/decisions.md) thay giả định một người trong planning cũ; không mở gate tri thức hoặc train.

Theo spec BMAD: người dùng tiếng Việt có ảnh lá cà chua trên Windows muốn quan sát trạng thái và học chăm sóc có căn cứ. Sinh viên/giảng viên kiểm tra dữ liệu, thực nghiệm và demo offline. Chưa xác minh nghiên cứu người dùng hoặc hiệu quả ngoài vườn.

## Product Purpose

Chọn một ảnh local, kiểm đầu vào, phân loại các trạng thái được hỗ trợ, đọc giới hạn và tra đúng nội dung có nguồn/phiên bản/phạm vi kiểm duyệt. Học qua bài ngắn và câu hỏi có giải thích. “Thẩm định” không phải xét nghiệm hoặc xác nhận tác nhân từ một ảnh.

## Operating Context

Mở app và dùng trực tiếp, **không đăng nhập**, theo xác nhận người dùng ngày 14/10/2026. Không server hoặc đồng bộ online. Hồ sơ và lịch sử local là tùy chọn; chưa được yêu cầu triển khai, lịch sử mặc định tắt. Danh tính reviewer trong hồ sơ tri thức là provenance, không phải vai trò tài khoản trong app.

## Capabilities and Constraints

- Spec chuẩn: [_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/spec-tomato-desktop.md](_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/spec-tomato-desktop.md), CAP-1…CAP-9; giữ FR/NFR/AD/S/T hiện có.
- Hai CNN dùng để thực nghiệm; app đóng gói winner được chọn bằng validation. CNN không sinh hướng dẫn hoặc quiz.
- Chạy CPU ở máy đích, tiếng Việt, bàn phím và Windows DPI; không phụ thuộc AI API/dịch API hoặc tải tài nguyên khi chạy.
- Một ảnh/job, một worker active, không hàng đợi; hủy/đổi ảnh không được hiện kết quả cũ.
- Healthy là trạng thái ảnh lá; không bảo đảm toàn cây khỏe. Không suy giống, mức độ bệnh, năng suất hoặc lịch tưới/phân.
- Không tối ưu canh tác, website, mobile, 3D, chatbot hoặc quản trị từ xa.
- Tri thức chuyên môn và tiếng Việt duyệt riêng; nội dung thiếu căn cứ bị chặn. Policy demo C3 còn mở, không giả phê duyệt.

## Evidence on Hand

[Data readiness](_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/data-readiness.md) ghi năm run cleaning và review tích hợp. PlantVillage còn rủi ro grouping/split; 17 card và 172 claim chưa được mở guidance thật. WUR/Dryad/Mendeley là research-only; UC-IPM thu thập bị chặn 403. Chưa có model sinh viên, app native, metric sản phẩm hoặc thử người dùng. Không dùng fixture synthetic thay bằng chứng thật.

## Product Principles

1. Người dùng thấy trạng thái và cách xử lý trước văn bản dài.
2. Phân loại ảnh, nguồn chăm sóc và đánh giá học tập có bằng chứng riêng.
3. Thiếu review/version/nguồn thì chặn, không thay bằng thẻ gần tên.
4. Ảnh gốc và raw bất biến; app không thu thập dữ liệu ngoài nhu cầu.
5. Hoàn thành lát cắt một ảnh–một thẻ thật trước khi mở rộng giao diện.

## Accessibility & Inclusion

Tiếng Việt và dấu đầy đủ; native file picker, accessible names, focus thấy được, không chỉ dùng màu. Kiểm 1280×720/1920×1080, DPI 100/150/200%, cửa sổ hẹp và chữ dài. Chuyển động chỉ phản hồi tác vụ; visual direction chưa chốt, cần duyệt trước sửa UI.
