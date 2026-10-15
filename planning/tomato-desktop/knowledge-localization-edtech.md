# Tri thức, Việt hóa và EdTech — kế hoạch

**Cập nhật Setup 13/10/2026:** tên đã chốt “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”; phạm vi nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50. Không tối ưu canh tác; WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung. Runtime đã setup; tài liệu vẫn là draft chưa tiếp nhận chính thức, xem [README](README.md) và [setup-report](setup-report.md).

Ngày 13/10/2026. Không dịch dataset trong lượt này. Schema/mapping thực tế ở data-audit. Hai CNN phân loại; module knowledge tra cứu/quy tắc, không là mô hình sinh hướng dẫn. 17 thẻ và qa_seeds local chưa đủ bằng chứng cho huấn luyện tư vấn supervised có context–action–outcome; không mặc định LLM/chatbot/vector database.

## So sánh phương án tiếng Việt

| Phương án | Tài nguyên/độ trễ | Chất lượng và vận hành | Kết luận đề xuất |
| --- | --- | --- | --- |
| Dịch một lần bằng công cụ/model local rồi review | Compute lúc chuẩn bị; không thêm latency khi dùng app | Cần license model, glossary và review thuật ngữ/điều kiện; model dịch không thay chuyên môn | Có thể tạo bản nháp khi được phép, chưa chọn/tải model |
| Kho EN + VI dẫn xuất đã kiểm tra, app hiển thị VI | Lookup nhỏ/offline; không phải đóng gói translation weights | Dễ so sánh nguồn, version, sửa có kiểm soát; cần công biên tập | **MVP ưu tiên** |
| Dịch runtime bằng model local | RAM/CPU/bundle/latency thêm, cạnh tranh với inference | Câu có thể khác mỗi phiên; khó kiểm review đúng bản hiển thị, không cần cho kho 10 thẻ | Hoãn, chỉ xem xét nếu có nhu cầu và benchmark |

Kho song ngữ là cách lưu/hiển thị; dịch một lần là cách tạo bản nháp, có thể kết hợp. Với 10 thẻ MVP và hai tháng, đề xuất biên tập/dịch thủ công có đối chiếu hoặc model local một lần sau pilot; **không bắt buộc mua/tải model dịch**. Giữ raw ảnh, label/ID EN và JSON gốc; mọi correction/mapping/VI nằm ở artifact dẫn xuất.

## Workflow dịch–kiểm duyệt dự kiến

1. Khóa EN source path/revision/hash và chọn 10 thẻ tương ứng CNN, không dịch toàn bộ 17 thẻ hoặc VQA toàn nguồn.
2. Tách claim: symptoms để học quan sát, causal/risk, cultural care/prevention, lookalikes, cautions. Loại/cách ly chemical, severity suy từ ảnh và numeric conditions chưa nguồn.
3. Glossary EN → VI → scientific/raw name → nguồn → reviewer/status. Bắt đầu nhóm healthy, disease, pest/mites, leaf spot/blight/mold, yellow curl/mosaic; không coi các tên “đốm vòng/đốm bia” đã duyệt chỉ vì có trong mapping.
4. Dịch nháp, giữ câu nguồn gắn câu VI và context. Model dịch nếu dùng phải local, pin version/license/config và không cần trong app; không gọi dịch API.
5. Review ngôn ngữ: không mất phủ định, may/should/must, đơn vị, số/range, leaf vs plant, condition về khí hậu/giai đoạn/đất, tên tác nhân. Kiểm tra sự khác nhau ToMV/TMV, nấm/oomycete, nhện/côn trùng. Back-translation chỉ hỗ trợ, không thay review.
6. Review nguồn và chuyên môn riêng: từng claim có URL/trang/mục đủ tìm, scope địa lý/giai đoạn và ngày truy cập. Không chép khuyến cáo thuốc nước ngoài thành lời khuyên VN; không tự thêm thuốc/liều/thời gian cách ly. Bất nhất raw ghi correction note ở bản dẫn xuất, có rationale/source; raw giữ nguyên.
7. Gán review actor, role, date, source/translation/glossary versions, review_status và approved_scope; generate bundle chỉ từ policy cho phép. Không có actor chuyên môn thì không đánh dấu expert_approved.
8. Check mapping 10/10, resolved lookalikes (24 raw dangling links phải được sửa bằng alias kiểm duyệt hoặc loại với lý do), source completeness, condition consistency, UI length/diacritics và golden-record tests. Mọi thay đổi content tăng knowledge version và rerun relevant tests.

### Trạng thái review và phạm vi phát hành

| Status | Ai/kiểm tra gì | App được dùng thế nào |
| --- | --- | --- |
| draft | Bản dịch/claim chưa kiểm | Không hiển thị như hướng dẫn |
| source_checked | Sinh viên/peer kiểm bản EN–VI và nguồn cụ thể, ghi actor và role thật | Chỉ nội dung giáo dục/chăm sóc rủi ro thấp trong demo có nhãn “chưa review chuyên môn” |
| expert_approved | Người có chuyên môn được xác định review nội dung và điều kiện áp dụng | Có thể dùng theo approved_scope; không vượt scope |
| suppressed | Claim mâu thuẫn/không nguồn/thuốc chưa căn cứ | Không hiển thị, giữ lý do trong ledger |

Người dùng hiện chưa có chuyên gia hỗ trợ. **MVP bảo vệ có thể là educational demo với source_checked**, không gọi là bộ tư vấn nông nghiệp đã xác nhận. Public release/tư vấn can thiệp rủi ro cao bị chặn C3. Nếu giảng viên yêu cầu review chuyên môn cho mọi guidance, đó là blocker cần tìm reviewer hoặc đổi scope, không dùng AI tự duyệt thay người. S11 ghi nhận trạng thái thật, không bypass review để đủ số thẻ.

## Hướng dẫn có ngữ cảnh và giới hạn

MVP chưa cá nhân hóa; hiện nội dung chung có điều kiện. Nếu cá nhân hóa được duyệt, phải hỏi người dùng trực tiếp giai đoạn cây, giống nếu biết, chậu/đất/nhà kính/ngoài trời, tưới/thoát nước, dấu hiệu ngoài lá, thời gian xuất hiện và vùng/điều kiện môi trường. Được chọn “không biết”. Chỉ hỏi field có rule/nguồn dùng được; không thu địa chỉ chính xác khi không cần.

Rule: status_code + context được nhập → đúng claim phù hợp condition/source; thiếu context → nội dung chung an toàn hoặc yêu cầu bổ sung; conflict → không tự đưa phác đồ. Rule/data có version và test matrix. Không suy giai đoạn/nhiệt độ/độ ẩm/thiếu phân từ ảnh; không trộn late blight tránh ướt lá với nhện tăng ẩm thành một quy trình chung. Không lấy top-k để ghép hướng dẫn; uncertain chỉ học/chăm sóc chung. Healthy class không chứng minh đất/nước/phân đã tối ưu.

## Đánh giá tư vấn riêng

| Dimension | Bằng chứng/test dự kiến | Mục tiêu đề xuất |
| --- | --- | --- |
| Ánh xạ | Fixture 10 code, unknown, alias conflict | Đúng 10/10 mapping; không auto-nearest label |
| Nguồn | Claim→URL/trang/revision; hiển thị source offline | 100% claim hiển thị truy vết được |
| Đầy đủ | Checklist triệu chứng quan sát/chăm sóc/phòng ngừa/cautions/context | Đủ mục áp dụng của mỗi thẻ; mục thiếu phải nêu |
| Điều kiện | Case context known/unknown/conflicting, top-k, knowledge missing | Không claim vượt scope; không mix nhãn |
| Thuật ngữ/ý nghĩa | Review glossary, phủ định/đơn vị/conditions | Không còn lỗi trọng yếu đã nhận diện trước demo |
| Dễ hiểu | Người dùng giải thích lại bước chăm sóc và giới hạn | Pilot 3–5 người nếu có; báo số/tỷ lệ thật |
| An toàn nội dung | Review thuốc/liều/cách ly, biology, source conflict | Nội dung chưa căn cứ bị suppress; expert scope không giả |

Accuracy/F1 ảnh không là metric chất lượng tư vấn. Auto-tests xác minh mapping/metadata/hiển thị, không chứng minh agronomy đúng. Nếu reviewer thiếu, báo coverage review và giới hạn, không cho tự-checklist thành expert validation.

## EdTech có mục tiêu quan sát được

Mỗi thẻ được hiển thị có lesson ngắn 3–5 phút đề xuất, ba phần: **quan sát dấu hiệu**, **hiểu tác nhân/điều kiện**, **phòng và chăm sóc theo nguồn**. Hai câu tự kiểm tra: một câu phân biệt dấu hiệu, một câu chọn hành động phù hợp điều kiện; feedback giải thích theo nguồn, không chỉ “đúng/sai”. Content từ thẻ/nguồn đã review, không dùng CNN sinh quiz/đáp án.

LO1: sau bài học người dùng nêu được hai dấu hiệu tham khảo và một điều không suy được từ ảnh. LO2: phân biệt nhện gây hại với bệnh do vi sinh, hoặc healthy class với bảo đảm toàn cây khỏe. LO3: chọn được một hành động chăm sóc có điều kiện và giải thích nguồn/giới hạn.

Đề xuất đánh giá formative: pre/post 4–6 câu có blueprint LO, các câu tương đương không chỉ nhớ đáp án vừa đọc; ghi n, completion, số đúng theo LO, paired change và phản hồi hiểu nhầm. Pilot nhỏ 3–5 người nếu có consent và khả năng; không cần lưu tên, không báo thống kê suy luận mạnh hoặc causal learning gain từ nhóm nhỏ không control. Không có người học thật: chỉ kiểm lesson/quiz/feedback logic (T14), ghi chưa đo hiệu quả học tập. T17 và báo cáo tách kết quả usability/learning khỏi ML và tư vấn.
