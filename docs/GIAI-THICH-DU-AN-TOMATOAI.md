# Giải thích dự án TomatoAI

**Đề tài: “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”**

Bản giải thích này tổng hợp hồ sơ hiện hành ngày **14/10/2026**. Dự án đã có kế hoạch chính thức được duyệt và kết quả chuẩn bị dữ liệu. Chưa có ứng dụng desktop chạy, mô hình đã huấn luyện hay kết quả đo độ chính xác. Những trải nghiệm dưới đây mô tả sản phẩm dự kiến.

## 1. Dự án giải quyết vấn đề gì?

Người trồng cà chua thấy lá xuất hiện đốm hoặc đổi màu thường muốn biết nên quan sát thêm điều gì và chăm sóc ra sao. TomatoAI hướng tới người Việt trồng hoặc học chăm sóc cà chua, có ảnh trên máy Windows. Nhu cầu trong hồ sơ chưa được xác nhận qua khảo sát người dùng thật.

Ứng dụng dự kiến gợi ý bệnh/trạng thái được hỗ trợ, kèm dấu hiệu, giới hạn và nội dung chăm sóc có nguồn. Tiếng Việt và khả năng chạy offline sau cài đặt giúp người dùng đọc kết quả trên máy, không gửi ảnh đến dịch vụ AI bên ngoài.

“Thẩm định” được hiểu là hỗ trợ kiểm tra ảnh và đối chiếu dấu hiệu. Một ảnh lá không xác nhận bệnh toàn cây hay tác nhân bằng xét nghiệm. Ứng dụng không nhận diện giống, mức độ bệnh hoặc năng suất. Hiệu quả hỗ trợ quan sát và học còn phải kiểm chứng.

## 2. Người dùng sẽ sử dụng ứng dụng như thế nào?

Ví dụ dự kiến: người dùng chọn ảnh lá cà chua có đốm và xem ảnh để xác nhận lựa chọn. Ứng dụng kiểm tra khả năng đọc và giới hạn xử lý trước khi phân tích. File hỏng được yêu cầu chọn lại, không thành kết quả “lá khỏe”.

Nếu đáp ứng quy tắc chấp nhận đã được kiểm thử, kết quả sẽ hiện tên tiếng Việt, ghi rõ đây là gợi ý từ ảnh. Người dùng đọc dấu hiệu, hướng dẫn và nguồn; nội dung chỉ xuất hiện khi bản ghi tương ứng được phép sử dụng.

Nếu chưa đủ căn cứ, ứng dụng thông báo “Chưa đủ căn cứ để kết luận”, cho chọn ảnh khác hoặc đọc bài học chung đã kiểm tra. Hướng dẫn chưa duyệt phải được báo rõ. Người dùng có thể hủy hoặc đổi ảnh; kết quả cũ không được ghi đè ảnh mới.

Bài học ngắn và hai câu tự kiểm tra dự kiến giúp hiểu dấu hiệu, nguyên nhân và phòng ngừa. Toàn bộ luồng này **chưa được triển khai**.

## 3. Dự án đã được định hình ra sao?

Ý tưởng ban đầu là “Xây dựng ứng dụng máy tính nhận diện dịch bệnh và đưa ra phương pháp trồng tối ưu”. Ảnh lá và thẻ kiến thức chưa đủ chứng minh tối ưu: cần mục tiêu đo được, dữ liệu can thiệp và đánh giá trong điều kiện canh tác cụ thể.

Sau một đề xuất tên nhấn mạnh nhận diện và học chăm sóc, ngày 13/10/2026 người dùng chốt tên hiện tại. Phạm vi gồm desktop Windows, tiếng Việt, offline; EfficientNet và ResNet50; nhận diện lá và hướng dẫn phù hợp. Không website, dịch vụ AI bên ngoài qua API hoặc mô hình tối ưu canh tác.

BMAD tổ chức bài toán, yêu cầu và công việc phát triển. Dự án đi từ hồ sơ nháp đến cài bộ công cụ, chuẩn bị dữ liệu, rà liên kết rồi tiếp nhận chính thức. Ngày 14/10/2026, người dùng duyệt spec — bản đặc tả thống nhất — và **6 nhóm việc, 22 công việc**, tất cả chưa bắt đầu.

Tài liệu cũ giữ chữ “bản nháp” hoặc “chưa tiếp nhận”. Registry — bảng quản lý phiên bản dữ liệu — và biên bản mới xác định trạng thái hiện hành. Hồ sơ bài toán, yêu cầu, trải nghiệm người dùng và kiến trúc được tham chiếu vào kế hoạch; không phải mọi quy trình đã chạy lại hay mọi lựa chọn đã chốt.

## 4. Ứng dụng dự kiến hoạt động ra sao?

Ứng dụng gồm bộ nhận diện đọc ảnh và kho kiến thức. Mã trạng thái từ bộ nhận diện dùng để tìm đúng bản ghi được duyệt; mô hình ảnh không tự viết lời khuyên.

EfficientNet cân đối độ lớn mô hình với chi phí xử lý; ResNet50 dùng đường nối giúp mô hình sâu học ổn định. Cả hai học từ ảnh. Kế hoạch tận dụng nền tảng đã học đặc điểm ảnh, rồi huấn luyện phần phù hợp với cà chua: cách này gọi là học chuyển giao.

Hai mô hình sẽ so sánh trên cùng dữ liệu. Hồ sơ đề xuất triển khai một mô hình sau đánh giá chất lượng, tốc độ và bộ nhớ; chưa chọn mô hình thắng. EfficientNet-B0, PyTorch, Python/PySide6 và cách đóng gói vẫn cần xác nhận.

Dữ liệu có 10 nhãn: bệnh, nhện gây hại và lá khỏe. “Lá khỏe” chỉ nghĩa chưa thấy dấu hiệu thuộc nhóm hỗ trợ. Tiếng Việt được biên tập trước, giữ nguồn tiếng Anh, không dịch khi dùng app. Huấn luyện diễn ra ngoài ứng dụng; Colab là lựa chọn tính toán, không làm sản phẩm phụ thuộc Internet.

## 5. Dữ liệu đến từ đâu và dùng để làm gì?

Ảnh dùng học nhận diện, kiến thức dùng giải thích, bảng canh tác dùng nghiên cứu bổ sung. Không ghép thành tập huấn luyện chung chỉ vì đều liên quan cà chua.

| Nguồn | Đã có và dùng cho việc gì? | Giới hạn hiện tại |
| --- | --- | --- |
| PlantVillage | 18.160 ảnh cà chua, 10 nhãn; nguồn chính dự kiến cho huấn luyện và đánh giá nhận diện. | Chưa có bộ chia dữ liệu được duyệt; còn thiếu căn cứ nhóm ảnh và xác minh nhãn độc lập. |
| PlantExpertVQA, phần cà chua | 17 thẻ, tức bản ghi kiến thức tiếng Anh về trạng thái, dấu hiệu và chăm sóc. | Bản local không có bộ hỏi–đáp với đáp án/kết quả để huấn luyện tư vấn; cả 17 thẻ cần duyệt. |
| UC IPM | Nguồn tham khảo về quản lý dịch hại đã được khảo sát và dùng đối chiếu một số nội dung. | Đợt thu thập mới bị chặn; chưa có kho HTML tải về, chưa có bản Việt hóa được phép phát hành. |
| WUR | Dữ liệu nhà kính, đã tải và chuẩn hóa 43 bảng với 622.899 bản ghi. | Nhiều dòng đo lặp; thời gian, đơn vị và ý nghĩa thí nghiệm còn cần rà soát. |
| Dryad | Dữ liệu thí nghiệm nước–dinh dưỡng, đã tải; chuẩn hóa thành 8 bảng, 508 bản ghi. | 508 bản ghi không phải 508 thí nghiệm độc lập; mã nghiệm thức và đơn vị chưa được xác minh đầy đủ. |
| Mendeley | Dữ liệu tưới đã tải: 3.000 bản ghi CSV và 393 bản ghi JSON, xử lý riêng. | Chưa có khóa nối hai phần; trường mang tên “optimal” không chứng minh chế độ tưới tối ưu. |

WUR, Dryad, Mendeley và UC IPM ngoài phụ thuộc bắt buộc của bản sản phẩm tối thiểu. Vướng mắc nghiên cứu ở đây không chặn phần nhận diện và kho hướng dẫn.

## 6. Những công việc đã làm và kết quả

Đã có hồ sơ bài toán, yêu cầu, trải nghiệm, kiến trúc, thí nghiệm, bản địa hóa, bảo mật và kiểm thử. Báo cáo dữ liệu giữ nguồn, biến đổi, phần chờ rà soát và bằng chứng bảo toàn; dữ liệu gốc không bị xóa để loại bản sao trùng.

| Đã làm | Đang vướng | Mới lên kế hoạch |
| --- | --- | --- |
| Setup BMAD; tiếp nhận đặc tả và kế hoạch chính thức; nối yêu cầu với công việc và kiểm thử. | Tiêu chí giảng viên, công cụ, ngân sách thời gian và quyền sử dụng còn cần chốt. | Triển khai 22 công việc; chưa công việc nào được ghi là đã bắt đầu. |
| Làm sạch kỹ thuật PlantVillage; giữ 18.146 bản sao, loại 14 bản sao trùng byte khỏi phần dẫn xuất. | 11.411 ảnh là ứng viên chia tập ở mức kỹ thuật; 6.735 ảnh giữ lại cần rà soát. | Chốt nhóm ảnh, thứ tự nhãn và bộ huấn luyện–kiểm tra. |
| Chuẩn hóa 17 thẻ tiếng Anh; có 10 thuật ngữ tiếng Việt dự thảo. | Chưa thẻ nào được duyệt chuyên môn và tiếng Việt. | Biên tập, duyệt một thẻ thật trước, rồi mở rộng phần cần dùng. |
| Rà liên kết: 9/10 cặp nhãn–thẻ đối chiếu được danh tính, không thiếu thẻ. | Cặp virus khảm còn mâu thuẫn; 24 liên kết tới tình trạng dễ nhầm chưa giải quyết. | Khóa ánh xạ và nội dung được phép hiển thị. |
| Chuẩn hóa kỹ thuật ba bộ canh tác; lưu mốc bàn giao UC IPM. | Trang kiểm tra quyền UC IPM trả HTTP 403; 21 mục chưa thử tải, 0 tài liệu được làm sạch. | Xử lý truy cập/quyền hợp lệ nếu tiếp tục nghiên cứu; không né chặn. |

Đã rà **172 câu hướng dẫn**: 26 có căn cứ nguyên tắc, 34 hỗ trợ một phần nhưng thiếu ngữ cảnh, 107 chưa xác minh, 5 có rủi ro cụ thể. **Chưa câu nào được mở hiển thị.** Đối chiếu tài liệu chuyên môn không có nghĩa chuyên gia riêng của dự án đã duyệt.

Báo cáo ghi kiểm thử công cụ xử lý dữ liệu đạt: PlantVillage 16, PlantExpert 14, WUR 10, Dryad 12, Mendeley 8; tra cứu 22; công cụ UC IPM 31. Chúng kiểm xử lý, truy vết và nhánh chặn; không chứng minh nhận diện đúng hay tải UC IPM thành công. Lượt này không chạy lại.

## 7. Kế hoạch phát triển tiếp theo

**Hoàn thiện quyết định và dữ liệu.** Bước đầu chốt tiêu chí đồ án, quyền tài nguyên, công cụ và phạm vi nội dung. Sau đó dùng bằng chứng làm sạch hiện có để giải quyết nhóm ảnh, trùng/gần trùng và chốt bộ đánh giá; không làm sạch lại vô cớ.

**Chuẩn bị mô hình và một thẻ thật.** Huấn luyện thử cần dữ liệu, quyền và cấu hình được duyệt. Nhánh kiến thức chuẩn bị theo phụ thuộc: biên tập tiếng Việt, rà nguồn, duyệt một thẻ cùng nội dung học. Không cần đợi cả 17 thẻ để tích hợp bước đầu.

**Làm luồng sử dụng đầu tiên.** Dữ liệu được duyệt, mô hình sinh viên huấn luyện và thẻ tiếng Việt được phép là điều kiện nối ảnh–nhận diện–hướng dẫn trong desktop. Phải kiểm thành công, ảnh lỗi, hủy và thiếu kiến thức; dữ liệu thử giả không thay thẻ thật.

**So sánh và hoàn thiện.** Chọn cấu hình bằng validation — tập dùng điều chỉnh và lựa chọn — trước khi mở tập kiểm tra cuối. Hoàn thiện giao diện, bài học, xử lý lỗi và giới hạn tài nguyên theo phụ thuộc; sau đó đo chất lượng cuối, đóng gói và kiểm Windows sạch, offline.

**Bàn giao bằng chứng.** Đánh giá ảnh vườn, hướng dẫn và học tập riêng khi có người, nguồn và nhãn phù hợp; thiếu thì ghi chưa đánh giá. Lịch sử sử dụng tùy chọn cần duyệt riêng, không chặn phần cốt lõi.

Hồ sơ dự kiến hai tháng, làm mỗi tối. Một sinh viên, hai giờ mỗi tối trong tám tuần tương đương 112 giờ là giả định. Chưa chốt ngày hoàn thành; nhóm ảnh, kiểm duyệt, máy và nguồn lực ảnh hưởng lịch.

## 8. Chất lượng sẽ được kiểm tra thế nào?

Ảnh cùng lá hoặc trùng phải ở cùng tập. Nếu xuất hiện cả khi học lẫn kiểm tra, mô hình có thể đạt điểm cao vì gặp ảnh tương tự. Chưa đủ căn cứ nhóm cho 10 lớp, đặc biệt Target Spot và virus khảm; không chia ngẫu nhiên phần chưa rõ.

Hai mô hình dùng cùng bộ dữ liệu và ngân sách minh bạch. Đánh giá macro-F1 — chỉ số tổng hợp coi trọng từng lớp — cùng bệnh dễ nhầm, tốc độ và bộ nhớ. Chưa có số đo hay mức chính xác cam kết. Điểm PlantVillage chưa chứng minh hiệu quả ngoài vườn.

Kho kiến thức kiểm riêng: đúng trạng thái, nguồn, điều kiện; không ghép bệnh gần tên. Bản dịch giữ phủ định, đơn vị và giới hạn. Ngôn ngữ đúng không thay duyệt chuyên môn; thuốc, liều, lịch phun hoặc cách ly thiếu căn cứ vẫn bị chặn.

Khi không chắc chắn, hệ thống từ chối kết luận. Điểm cao vẫn có thể sai; ảnh ngoài phạm vi cần kiểm riêng. Bảo mật dự kiến giới hạn file/tài nguyên, giữ ảnh gốc, kiểm phiên bản và không gửi ảnh ra mạng. Lịch sử mặc định không lưu nếu được triển khai. Kiểm desktop, bàn phím và gói offline chưa chạy.

## 9. Những điểm còn cần quyết định

Cần chốt tiêu chí giảng viên, diễn giải “thẩm định”, biến thể EfficientNet, công cụ, mục tiêu và ngân sách thử nghiệm. Dữ liệu cần phục hồi nhóm ảnh hoặc điều chỉnh bộ đánh giá có căn cứ; giải quyết mâu thuẫn hai virus ToMV và TMV.

Chưa có chuyên gia được xác nhận, ảnh vườn có nhãn độc lập hay người đánh giá học tập. Demo giáo dục chỉ đối chiếu nguồn là đề xuất cũ còn chờ chính sách; hiện vẫn chặn hướng dẫn thật. Bản dịch hoặc nguồn tham khảo chưa đủ để mở nội dung.

Cần rà quyền từng ảnh, tài liệu, mô hình và thành phần ứng dụng; quyền cả bộ không tự bao phủ mọi trích dẫn. UC IPM cần truy cập/quyền hợp lệ. Phạm vi demo, số giờ/người, máy kiểm offline và ngày bảo vệ chưa được xác nhận đầy đủ.

## 10. Tài liệu làm căn cứ

Gốc project đã xác nhận: `C:\Users\admin\Downloads\DACN_CayCaChua`. Cấu hình chọn `_bmad-output`, initiative `initiative-tomato-desktop`; dữ liệu ở `data/TomatoAI/data/`.

- [Đặc tả hiện hành](../_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/spec-tomato-desktop.md), [readiness dữ liệu](../_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/data-readiness.md) và [truy vết yêu cầu](../_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/requirements-traceability.md).
- [Biên bản tiếp nhận kế hoạch chính thức](../_bmad-output/initiative-tomato-desktop/planning-import-20261014-v1/README.md) và [initiative đang hoạt động](../_bmad-output/initiative-tomato-desktop/initiative-tomato-desktop.md).
- [Brief hiện tại](../planning/tomato-desktop/product-brief.md), [brief lịch sử](../planning/setup-backups/20261013-234847/tomato-desktop/product-brief.md) và [biên bản setup, đổi tên/phạm vi](../planning/tomato-desktop/setup-report.md).
- [Yêu cầu sản phẩm](../planning/tomato-desktop/prd.md), [UX desktop](../planning/tomato-desktop/ux-desktop.md) và [kiến trúc đề xuất](../planning/tomato-desktop/architecture.md).
- [Kế hoạch thí nghiệm](../planning/tomato-desktop/experiments.md), [tri thức và Việt hóa](../planning/tomato-desktop/knowledge-localization-edtech.md), [bảo mật/kiểm thử](../planning/tomato-desktop/security-testing.md) và [ước lượng lịch sử](../planning/tomato-desktop/delivery-plan.md).
- [Dataset registry](../data/TomatoAI/data/dataset-registry.json), [cleaning PlantVillage](../data/TomatoAI/data/reports/plantvillage/README.md) và [cleaning PlantExpert](../data/TomatoAI/data/reports/plantexpert-tomato/README.md).
- [Review tích hợp và liên kết](../data/TomatoAI/data/reports/integration/ir-20261014-v1/README.md).
- [Tiếp nhận dữ liệu canh tác](../data/TomatoAI/data/cultivation_metadata/README.md), các báo cáo [WUR](../data/TomatoAI/data/reports/wur/README.md), [Dryad](../data/TomatoAI/data/reports/dryad/README.md) và [Mendeley](../data/TomatoAI/data/reports/mendeley/README.md).
- [Bàn giao UC IPM: thu thập bị chặn và giới hạn kiểm chứng](../data/TomatoAI/data/reports/uc-ipm-tomato/HANDOFF-ucipm-20261014-acq-v1.md).

