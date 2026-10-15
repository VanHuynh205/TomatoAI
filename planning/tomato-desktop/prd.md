# PRD — bản nháp planning, chưa duyệt

Ngày 13/10/2026. Đầu vào cho `bmad-prd`, chưa phải artifact workflow. Bài toán/phạm vi chuẩn ở [product-brief](product-brief.md); dữ liệu và taxonomy chuẩn ở [data-audit](data-audit.md). Chưa có rubric giảng viên.

**Tên đã chốt:** “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”. Draft đã cập nhật phạm vi nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50; không tối ưu canh tác. Runtime đã setup; PRD chính thức chờ kết quả làm sạch. Giữ FR01–FR14 và NFR01–NFR10.

## Người dùng và hành trình

Người dùng có ảnh lá trên Windows, chọn ảnh, đọc trạng thái và giới hạn, quan sát dấu hiệu tham khảo, xem hướng dẫn có nguồn rồi học/tự kiểm tra. Khi ảnh không hợp lệ hoặc hệ thống không kết luận, người dùng biết cách chụp/chọn lại và có thể đọc tài liệu chăm sóc chung. Sinh viên/giảng viên kiểm tra provenance model/split/tri thức và demo offline. Không có vai trò đăng nhập, dịch vụ mạng hoặc quản trị từ xa trong MVP.

## Yêu cầu chức năng và truy vết

AC là **test dự kiến**, chưa chạy. ID ổn định; chi tiết test T-n ở [security-testing](security-testing.md), story S-n ở [delivery-plan](delivery-plan.md).

| ID | Yêu cầu | Acceptance criteria kiểm chứng được | Story | Test |
| --- | --- | --- | --- | --- |
| FR01 | Chọn một ảnh local, preview, đổi/hủy | JPEG/PNG hợp lệ có preview; cancel không bắt đầu inference; đổi ảnh làm kết quả cũ mất hiệu lực | S06, S13 | T01, T10 |
| FR02 | Kiểm tra ảnh trước inference | Từ chối file hỏng/không phải ảnh/quá giới hạn bằng mã lỗi xác định; không đổi thành healthy; ảnh mờ được nhắc theo ngưỡng đã thử | S06, S14 | T02, T03 |
| FR03 | Nhận diện 10 trạng thái có manifest | Output index ánh xạ đúng 10 code, dùng checkpoint sinh viên huấn luyện và preprocessing đã khóa; hiện model/data version | S05, S06, S07, S08 | T04, T05 |
| FR04 | Có trạng thái không kết luận | Khi rule từ chối kích hoạt, status=`uncertain` hoặc `out_of_scope`, không hiện phác đồ cho nhãn; không tuyên bố phát hiện mọi OOD | S09, S13 | T06 |
| FR05 | Tra đúng một bản ghi VI có nguồn | 10 code đều có mapping duy nhất; thiếu/không duyệt thì status=`knowledge_unavailable`; nguồn/version nhìn được offline | S10, S11, S13 | T07, T08 |
| FR06 | Tách phân loại, tra cứu và giới hạn | CNN không sinh hướng dẫn; không hiển thị mức độ, năng suất, lây lan hoặc sức khỏe toàn cây từ ảnh | S06, S13, S19 | T05, T07, T20 |
| FR07 | Chăm sóc theo ngữ cảnh chỉ khi có căn cứ | MVP có hướng dẫn chung; dữ liệu người dùng không nhập thì context=`unknown`; rule chưa có nguồn không sinh nội dung; không trộn top-k | S11, S13 | T08 |
| FR08 | Việt hóa bằng bản dẫn xuất | Raw EN/ảnh/ID giữ nguyên; bản VI có source, glossary/version, reviewer/role/status; không có tác vụ dịch khi dùng app | S10, S11 | T09 |
| FR09 | Học ngắn và tự kiểm tra | Mỗi thẻ MVP có mục tiêu quan sát được, hai câu hỏi/đáp án/giải thích; điểm học tách khỏi confidence ảnh | S12, S17 | T14 |
| FR10 | Suy luận không làm treo giao diện | Một job active, không hàng đợi vô hạn; nút hủy hoạt động; kết quả job cũ không ghi đè ảnh mới | S06, S14 | T10, T11 |
| FR11 | Kiểm tra tính tương thích artifact | Check model/hash, schema, 10 code, preprocessing/KB version trước dùng; sai contract thì lỗi có cách khắc phục, không fallback nhãn im lặng | S06, S14, S18 | T04, T12 |
| FR12 | Hai mô hình được thực nghiệm công bằng | Cùng manifest/group split và ngân sách được log; chọn config/threshold/winner bằng validation; test khóa đến đánh giá cuối | S03–S09, S15 | T15, T16 |
| FR13 | Lịch sử tùy chọn, ngoài MVP bắt buộc | Mặc định không lưu ảnh/history; nếu thêm sau, opt-in, xem/xóa local, không mất file ảnh gốc | S20 (tùy chọn) | T18 |
| FR14 | Evidence cho báo cáo/bảo vệ | Có manifests/config/log/checkpoint/model card/data card, bảng metric trống trước đo, failure cases, demo script và giới hạn | S15–S19 | T16, T17, T20 |

## Yêu cầu phi chức năng

| ID | Yêu cầu/đề xuất định lượng cần duyệt | Cách nghiệm thu dự kiến | Story / test |
| --- | --- | --- | --- |
| NFR01 | Windows desktop offline sau cài; không AI API/dịch API; không gửi ảnh ra mạng | Máy sạch offline, không Python/GPU runtime cài trước; quan sát network và các đường dùng ảnh/KB/học | S18 / T13 |
| NFR02 | Máy mục tiêu tối thiểu chưa chốt; dùng máy khai báo và CPU inference làm reference | Ghi Windows build, CPU/RAM/GPU thực tế, power mode, device, batch=1; GPU tùy chọn không là dependency runtime | S05, S15, S18 / T11, T13 |
| NFR03 | Đề xuất warm end-to-end p95 ≤3 giây, peak app RSS ≤2 GB, gói ≤1,5 GB | 100 lần sau 10 warm-up; cold start đo riêng; ghi preprocessing/model/lookup/render và phần cứng | S15, S18 / T11 |
| NFR04 | UI tiếng Việt, bàn phím, DPI, tương phản và phóng chữ | Tab/focus order và accessible names; 1280×720, 1920×1080, DPI 100/150/200%; không chỉ dùng màu để diễn nghĩa | S13 / T19 |
| NFR05 | Tái lập/traceability | Seed, group manifest/hash, dependency versions, hardware, weights enum/hash, config, checkpoint và chọn winner được lưu | S02–S09, S15 / T15, T16 |
| NFR06 | Least privilege, tài nguyên có hạn, lỗi hữu ích | Không admin; image limits; 1 worker; watchdog/hủy; paths local; model load allowlist | S14, S18 / T02, T03, T10, T12 |
| NFR07 | Bảo toàn dữ liệu và riêng tư | Không ghi raw, không lưu EXIF/ảnh/path đầy đủ vào log mặc định; lỗi persistence không mất ảnh gốc | S14, S20 / T18 |
| NFR08 | Tri thức có provenance, review có phạm vi | 100% bản ghi hiển thị có source/version/role/trạng thái; chemical chưa đủ căn cứ bị suppress; không gọi source_checked là expert-approved | S10–S12 / T07–T09 |
| NFR09 | Maintainability vừa đủ | Tách training/inference/knowledge/UI, config đường dẫn; một implementation preprocessing dùng cho eval/app; không server/ORM/vector DB không cần | S06, S14 / T04, T05 |
| NFR10 | Không suy hiệu quả thực tế từ test PlantVillage | Model card tách internal vs external; external chưa có nhãn thì ghi không đo được, không báo như passed | S16, S19 / T17, T20 |

Các mục tiêu hiệu năng/metric chỉ là **đề xuất C1**. Không đạt thì phân tích, giảm phạm vi hoặc tối ưu có thực nghiệm; không sửa mục tiêu hồi tố để che thất bại. Không có yêu cầu accuracy ảnh đồng nghĩa tư vấn đúng.

## Nghiệm thu ML, tri thức và học tập riêng

ML: macro-F1 là tiêu chí chính, precision/recall/F1/support từng lớp, confusion matrix, accuracy bổ trợ; training wall-time, CPU latency/RAM. Mục tiêu thử nghiệm trong experiments, không bảo đảm. Lớp thiếu support hoặc group thiếu phải hiện trong bảng.

Tri thức: mapping đúng 10/10, zero dangling link trong kho phát hành, 100% claim hiển thị có nguồn kiểm được và review scope; không trộn điều kiện mâu thuẫn. Chưa có người chuyên môn: chỉ demo nội dung giáo dục rủi ro thấp đã đối chiếu nguồn, gắn nhãn review bởi sinh viên; không nghiệm thu “tư vấn nông nghiệp đã xác nhận”.

EdTech: người học nhận biết dấu hiệu, giải thích một nguyên nhân và chọn hành động phòng ngừa có căn cứ; đo completion và câu trả lời pre/post tách khỏi accuracy model. Pilot nhỏ chỉ báo mô tả và giới hạn, không tuyên bố hiệu quả giáo dục tổng quát.

## Phân tích rủi ro ở mức yêu cầu

Ảnh/model/KB và lịch sử là các tài sản/đầu vào cần bảo vệ. Ưu tiên kiểm tra file, giới hạn worker, nạp state dict nguồn tin cậy và không ghi dữ liệu không cần. Sai số mô hình và lời khuyên không phù hợp là hai loại rủi ro độc lập với bảo mật phần mềm. Ma trận thiết kế–story–test đầy đủ ở security-testing; chưa có code để audit/SAST/pentest.

## Điều kiện đổi scope

Tối ưu canh tác được loại khỏi phạm vi đã chốt; WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung, không tạo yêu cầu MVP hoặc target tối ưu. Ensemble, SVM, tư vấn supervised, thuốc/liều, nhiều cây hoặc history chỉ được xem xét khi có nhu cầu và ngân sách được duyệt, cập nhật CAP/FR/story/test trước code. Không tự thêm để đủ ML/DL/AgriTech/EdTech. Không chấp nhận test-set tuning. Nếu vẫn không có external ground truth hoặc reviewer chuyên môn, giữ giới hạn đó trong báo cáo và demo.
