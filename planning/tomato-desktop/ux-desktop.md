# UX desktop tiếng Việt — đề xuất, chưa khóa visual direction

**Cập nhật Setup 13/10/2026:** tên đã chốt “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”; phạm vi nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50. Không tối ưu canh tác; WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung. Runtime đã setup; tài liệu vẫn là draft chưa tiếp nhận chính thức, xem [README](README.md) và [setup-report](setup-report.md).

Ngày 13/10/2026. Đầu vào cho `bmad-ux`; không phải DESIGN/EXPERIENCE đã finalize. Đã dùng Impeccable nhánh B, `shape` (job/flow/states) và `operate` (giao diện công cụ); context local chạy một lần, báo không có PRODUCT.md/visual authority. Không có comp, screenshot sản phẩm, prototype hoặc UI code trong lượt này. `craft-floor` chỉ cần ngay trước sửa UI, chưa áp dụng vì không sửa UI.

## Công việc và cấu trúc trải nghiệm

Màn hình nhận diện là **Operate**: giúp hoàn thành một ảnh. Hướng dẫn/bài học là **Read**: giúp hiểu dấu hiệu và điều kiện áp dụng. Người dùng Việt, desktop offline, chưa khảo sát tuổi/kỹ năng/DPI; ưu tiên native controls, bàn phím và chữ dễ đọc. Không 3D, không animation trang trí.

Navigation MVP: **Nhận diện**, **Học chăm sóc**, **Thông tin & nguồn**. Lịch sử chỉ thêm nếu S20 được duyệt. Không yêu cầu đăng nhập/nhập dữ liệu nhạy cảm.

1. Empty: “Chọn ảnh lá cà chua” kèm ba hướng dẫn chụp ngắn (lá rõ nét, ánh sáng đều, tránh che khuất); nút Chọn ảnh là thao tác chính.
2. Selected: preview, tên file rút gọn, Đổi ảnh/Xóa lựa chọn; giải thích phạm vi 10 trạng thái và giới hạn một ảnh.
3. Running: hiển thị bước đang chạy và nút Hủy, không % tiến độ giả. UI vẫn phản hồi bàn phím.
4. Result: tên trạng thái VI + nhóm healthy/bệnh/tác nhân gây hại; dòng “Kết quả gợi ý từ ảnh”; giới hạn hiển thị cạnh kết quả. Không dùng “chẩn đoán chắc chắn”.
5. Guidance: bản ghi có nguồn, triệu chứng để quan sát thêm, chăm sóc/phòng ngừa, điều kiện/cảnh báo, trạng thái review. Chỉ một nhãn được accepted; top-k nếu trình bày trong phần nghiên cứu không tạo phác đồ.
6. Learn: mục tiêu ngắn, nội dung 3 phần, hai câu tự kiểm tra + giải thích. Có thể truy cập bài học chung từ uncertain/unknown.

## Bố cục đề xuất, cần duyệt trước code

Màn hình rộng: khu chọn/preview ảnh bên trái; kết quả chính và hướng dẫn bên phải. Tên trạng thái và giới hạn xuất hiện trước văn bản dài; nguồn/versions trong vùng “Nguồn và phiên bản” mở rộng bằng bàn phím. Thu hẹp cửa sổ: một cột theo thứ tự ảnh → kết quả → hướng dẫn → học, không ép panel thành chữ quá nhỏ. Không thiết kế website/mobile trong scope; kiểm cửa sổ hẹp và Windows DPI thay cho mobile viewport.

Direction dự kiến là công cụ quan sát/học đáng tin: nền trung tính, một accent cho hành động chính, semantic status có text/icon. Typography đề xuất system Segoe UI hỗ trợ dấu VI, body khoảng 16 px tương đương theo DPI, heading 20–24 px, spacing theo nhịp 8/16/24; chưa là token khóa. Các chỉ số cần test clipping/contrast trước duyệt. Line length văn bản chăm sóc khoảng 65–75 ký tự, đoạn ngắn có điều kiện rõ. Giữ tên khoa học/EN trong phần mở rộng, không che nội dung VI.

Không nhận diện bằng màu duy nhất: healthy dùng nhãn “Lớp khỏe”; bệnh ghi “Bệnh”; nhện ghi “Tác nhân gây hại”; uncertain có nhãn “Chưa đủ căn cứ”. Không tô đỏ mọi trạng thái có điểm thấp thành bệnh nặng. Score nếu hiển thị: “điểm của mô hình, không phải xác suất chẩn đoán đúng”; không gọi softmax là độ chắc chắn đã hiệu chuẩn.

## Trạng thái và copy cần kiểm thử

| Trạng thái | Nội dung/hành động dự kiến | Invariant |
| --- | --- | --- |
| Empty | Chọn ảnh; hướng dẫn và phạm vi | Không hiện kết quả mẫu như đã phân tích |
| Invalid format/decode | “Không đọc được ảnh này. Hãy chọn ảnh JPEG hoặc PNG khác.” | Không chạy forward; không fallback healthy |
| Too large | Nêu bytes/pixel vượt giới hạn và cách dùng bản ảnh nhỏ hơn | Không tự ghi đè ảnh gốc |
| Blur/poor quality | Yêu cầu ảnh rõ hơn, chỉ báo sau policy đã thử | Không khẳng định blur detector hiểu cây |
| Loading model/running | Bước đang thực hiện, Hủy; disable chạy lặp | Không queue vô hạn hoặc % giả |
| Cancelled | “Đã hủy”; Chọn/Chạy lại | Job cũ không render sau hủy |
| Accepted healthy | “Chưa thấy dấu hiệu thuộc các lớp bệnh/tác nhân được hỗ trợ” | Không bảo đảm sức khỏe toàn cây |
| Accepted disease/pest | Tên lớp + gợi ý quan sát + nguồn/giới hạn | Không mức độ bệnh/thuốc tự suy |
| Uncertain/out_of_scope | “Chưa đủ căn cứ để kết luận”; Chọn ảnh khác/Bài học chung | Không hiện hướng dẫn theo một nhãn bệnh |
| Knowledge missing/not reviewed | “Chưa có hướng dẫn đã kiểm tra cho trạng thái này”; vẫn nêu giới hạn model | Không mượn thẻ gần tên khác |
| Model/version error | Không phân tích được; mã lỗi hỗ trợ, Retry/Thông tin gói | Không download weights/network repair tự động |
| Review source_checked demo | Nêu đã đối chiếu nguồn bởi sinh viên, chưa có review chuyên môn | Không gắn badge “chuyên gia duyệt” |

## Bàn phím, accessibility, giới hạn chuyển động

Ctrl+O chọn ảnh; Tab/Shift+Tab đi theo thứ tự chọn ảnh → inference/hủy → kết quả → nguồn → học; Enter kích hoạt control đang focus, Escape hủy job khi có, không đóng app làm mất trạng thái bất ngờ. Native file picker và accessible names tiếng Việt; focus visible, chuyển focus vào thông báo lỗi phù hợp, accessible announcement cho hoàn thành/hủy. Các shortcut là đề xuất, phải kiểm xung đột native.

Đề xuất tương phản WCAG AA làm reference: chữ thường ≥4,5:1, chữ lớn/control/focus ≥3:1 phù hợp từng loại; đo màu thật sau triển khai. Phóng chữ/DPI không cắt nhãn/nguồn, không horizontal scroll văn bản chính. Trạng thái nút đầy đủ default/hover/focus/pressed/disabled/running/error. Motion chỉ phản hồi state ngắn; tôn trọng cài đặt giảm chuyển động Windows, không delay kết quả vì hiệu ứng. Không tải font/icon từ mạng.

## Kiểm thử UX/học tập dự kiến

T01–T10 và T19 kiểm empty→selected→running→result/uncertain/error/cancel với bàn phím, ảnh/path có dấu, guidance dài. Pilot usability đề xuất 3–5 người tự nguyện: hoàn thành chọn ảnh/đọc giới hạn/tìm nguồn/học, ghi task success, thời gian và misunderstanding; số người thực tế phải báo đúng. Không có người thử thì chỉ tự kiểm bàn phím/layout, không gọi đó là nghiên cứu người dùng.

Trước code: duyệt product context/stack/flow và visual direction, ghi tài liệu UX BMAD chính thức sau setup. Nếu triển khai PySide6 được duyệt, dùng native Qt widgets thay ví dụ CSS/React trong skill; quy tắc giữ React hiện hữu không áp dụng như yêu cầu tạo website khi project chưa có app và người dùng đã chốt desktop. Mọi thay đổi stack khác cần duyệt.
