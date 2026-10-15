# Product brief — bản nháp chờ duyệt

Ngày 13/10/2026. Tài liệu planning độc lập, đầu vào cho `bmad-product-brief`; runtime đã setup, workflow tiếp nhận draft chưa chạy, chờ kết quả làm sạch dữ liệu.

**Tên đã chốt:** “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”. Phạm vi hiện hành và quyết định thay thế tên cũ tại [README](README.md). Diễn giải “thẩm định” trong draft là hỗ trợ kiểm tra ảnh, đối chiếu dấu hiệu và giới hạn có nguồn, cần đối chiếu rubric; chưa có căn cứ xác nhận bệnh toàn cây hoặc tác nhân bằng xét nghiệm, và không suy ra giống cà chua từ ảnh lá.

## Bài toán và giá trị

Người Việt có ảnh lá cà chua cần biết ảnh gợi ý trạng thái gì, giới hạn của nhận diện, dấu hiệu cần quan sát thêm và cách chăm sóc/phòng ngừa có căn cứ. Sản phẩm phục vụ học và hỗ trợ quan sát; một ảnh không xác nhận tình trạng toàn cây hoặc chẩn đoán tác nhân bằng xét nghiệm.

Sinh viên thực hiện một quy trình Applied AI có thể bảo vệ: chuẩn hóa dữ liệu và nhóm lá, transfer learning hai CNN đã chọn, so sánh công bằng, phân tích lỗi và tích hợp một mô hình local với kho tri thức kiểm duyệt. Kho tri thức không phải đầu ra do CNN sinh ra.

Người dùng chính: người Việt trồng/học chăm sóc cà chua, dùng máy Windows có ảnh đã lưu. Người đánh giá: giảng viên cần bằng chứng đóng góp, tái lập và giới hạn. Chưa khảo sát người dùng thật; nhu cầu cụ thể/khả năng sử dụng là giả định từ brief, cần kiểm thử tác vụ sau này.

## MVP đề xuất

1. Chọn một ảnh local; kiểm tra định dạng, khả năng giải mã, kích thước và chất lượng theo quy tắc được kiểm chứng.
2. Inference một mô hình do sinh viên fine-tune; có thể từ chối/không kết luận. Hiển thị tên trạng thái tiếng Việt, dấu hiệu/giới hạn và version.
3. Mã trạng thái ánh xạ một bản ghi đã duyệt, có nguồn, vào hướng dẫn quan sát/chăm sóc/phòng ngừa. Trạng thái khỏe mạnh là “chưa thấy dấu hiệu thuộc lớp được hỗ trợ”, không bảo đảm cây hoàn toàn khỏe.
4. Bài học ngắn: dấu hiệu → nguyên nhân → phòng/chăm sóc; hai câu tự kiểm tra và giải thích. Không chatbot.
5. Đóng gói Windows offline; CPU inference là đường cơ sở dự kiến. Chỉ lưu lịch sử khi người dùng chủ động bật; lịch sử không cần cho lát cắt đầu tiên.

Ngoài phạm vi: bài toán tối ưu canh tác (năng suất/nước/phân bón/chi phí), website/server, AI API/dịch API, 3D, thêm kiến trúc CNN khác, phân đoạn/mức độ bệnh, đếm sâu, dự báo lây lan/năng suất, nhận diện giống cà chua, IoT/thời tiết tự động, kê thuốc/liều/cách ly, LLM/vector DB, ensemble mặc định, nhiều cây trồng, cập nhật model online và huấn luyện trong ứng dụng.

## Quyết định tên/phạm vi và lịch sử “phương pháp trồng tối ưu”

**Khảo sát lịch sử ban đầu:** local có ảnh lá phân lớp và thẻ mô tả bệnh/tác nhân/chăm sóc; thẻ healthy có thực hành phòng ngừa chung. Trong hai bộ PlantVillage/PlantExpertVQA khảo sát lúc đó không thấy bảng kết quả canh tác, đầu vào nước/phân hoặc hàm mục tiêu; chúng không đủ để chứng minh tối ưu canh tác. Sau đó đã tiếp nhận WUR/Dryad/Mendeley, xem [biên bản tiếp nhận](../../data/TomatoAI/data/cultivation_metadata/README.md); việc tiếp nhận không xác nhận dữ liệu đã sạch hoặc phù hợp triển khai tư vấn tại Việt Nam.

**Đã chốt thay thế bởi người dùng, 13/10/2026:** dùng tên nêu ở đầu tài liệu, nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp có nguồn. Đề xuất tên cũ được lưu trong bản sao trước sửa, không còn chờ duyệt. WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung, không là phụ thuộc MVP.

**Lý do loại khỏi phạm vi:** bài toán tối ưu cần mục tiêu/outcome, dữ liệu can thiệp, bối cảnh giống/giai đoạn/đất/khí hậu và đánh giá thực nghiệm riêng. Người dùng đã loại bài toán này; không thêm mô hình hoặc story tối ưu trong kế hoạch hiện hành.

## Khả thi và thành công

Phần cứng người dùng khai báo hỗ trợ đề xuất B0 ở 224 px; khả năng fit batch và thời gian train chưa đo. Thời gian hai tháng/mỗi tối; tạm giả định một sinh viên, hai giờ mỗi tối. Colab chỉ là compute training tùy chọn, phải ghi GPU/session/version và lưu checkpoint; không làm app phụ thuộc mạng.

Thành công được chứng minh bằng manifest split không rò rỉ có kiểm toán, hai mô hình có config/checkpoint/log, lựa chọn dựa validation, test cuối và phân tích từng lớp, demo offline trên máy sạch, mapping/hướng dẫn đúng và bài học được kiểm thử. Mục tiêu số ở PRD/experiments là **đề xuất**, không phải kết quả hay bảo đảm. Chưa có rubric; chưa có chuyên gia hoặc bộ ảnh vườn độc lập. Nếu thiếu, báo cáo phải ghi giới hạn và không tuyên bố hiệu quả ngoài vườn hoặc tư vấn đã được chuyên gia xác nhận.
