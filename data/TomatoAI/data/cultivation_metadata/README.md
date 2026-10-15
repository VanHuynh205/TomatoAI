# Dữ liệu bổ sung cho nghiên cứu canh tác cà chua

Ngày tiếp nhận: **13/10/2026**. Người dùng đã cho phép tải dataset trong yêu cầu tiếp theo. Phạm vi thực hiện: tải file công khai, giữ nguyên nguồn, kiểm tra tính toàn vẹn, giải nén an toàn và kiểm kê chỉ đọc. Chưa làm sạch/ghép bảng, tạo nhãn tối ưu, dịch, huấn luyện hay viết script triển khai. Hồ sơ này là biên bản tiếp nhận dữ liệu độc lập, không phải kết quả workflow BMAD.

## File và nguồn đã tải

Thư mục raw: [cultivation](../raw/cultivation/). Không thay đổi PlantVillage hoặc PlantExpertVQA hiện có.

| Bộ dữ liệu | Nguồn/phiên bản | File đã có local | Giấy phép nguồn | Kiểm tra |
| --- | --- | --- | --- | --- |
| Dryad: thí nghiệm tưới, đạm và phân hữu cơ | [DOI 10.5061/dryad.wm37pvn33](https://datadryad.org/dataset/doi:10.5061/dryad.wm37pvn33); công bố 09/06/2026; API versionNumber 5, version ID 446657 | [dryad_water_nitrogen_2024_v5](../raw/cultivation/dryad_water_nitrogen_2024_v5/): 4 XLSX + README, tổng 159.125 byte | CC0 1.0 | Cả 5 file khớp kích thước và SHA-256 do Dryad công bố |
| Mendeley: Dataset on irrigation for Tomato | [DOI 10.17632/33cngpcrmx.3](https://data.mendeley.com/datasets/33cngpcrmx/3); version 3, công bố 01/07/2026 | [mendeley_irrigation_33cngpcrmx_v3](../raw/cultivation/mendeley_irrigation_33cngpcrmx_v3/): CSV + JSON, tổng 821.018 byte | CC BY 4.0 | Cả 2 file khớp kích thước và SHA-256 do Mendeley công bố |
| WUR: Autonomous Greenhouse Challenge, Second Edition (2019) | [Kho 4TU, version 2](https://data.4tu.nl/articles/dataset/Autonomous_Greenhouse_Challenge_Second_Edition_2019_/12764777/2); DOI 10.4121/uuid:88d22c60-21b3-4ea8-90db-20249a5be2a7; ID kho hiện tại 8b35675d-7549-49cc-a8c3-dedec8d3f23e | [wur_greenhouse_2019_v2](../raw/cultivation/wur_greenhouse_2019_v2/): archive 7z 8.418.715 byte và bản giải nén nguyên trạng 43 CSV + 2 PDF | CC0 1.0 theo metadata 4TU | Archive khớp MD5 nguồn; tar đọc/giải nén thành công; SHA-256 local cho từng file |

**Tổng: 53 file raw**, bao gồm archive WUR và 45 file giải nén; tổng **113.081.483 byte**, khoảng 107,8 MiB. Tổng payload tải trực tiếp từ mạng là 9.398.858 byte, phần còn lại là bản giải nén. Không tính metadata vào các tổng này.

Dryad: API trả `versionStatus=submitted` đồng thời dataset có publicationDate và trang công khai cung cấp đúng năm file. Đã lưu phản hồi thực tế, không đổi thành trạng thái published trong metadata. Các hash khớp danh sách file công khai đã tải.

## Bằng chứng và khả năng tái kiểm tra

- [download-manifest.csv](download-manifest.csv), [download-manifest.json](download-manifest.json): đường dẫn tương đối, byte, SHA-256 local, URL file nguồn, giấy phép, digest nguồn, trạng thái đối chiếu và archive cha.
- [content-inventory.json](content-inventory.json): số dòng/header CSV; dimensions worksheet và năm dòng đầu XLSX. Dimensions Excel có thể chứa vùng trống được định dạng, không phải số mẫu ML.
- Dryad: [dataset](dryad-dataset.json), [version](dryad-version.json), [files](dryad-files.json), [trang nguồn](dryad-source.html).
- Mendeley: [danh sách file v3](mendeley-files-v3.json), [trang nguồn](mendeley-source-v3.html).
- WUR: [RO-Crate v2](wur-ro-crate-v2.json), [trang nguồn](wur-source-v2.html); ReadMe.pdf và Economics.pdf nằm trong source_files.
- `manifest_created_at_utc` là thời điểm tạo manifest, không phải timestamp chính xác cho mỗi lần tải. SHA-256 local giúp nhận biết sửa đổi sau này; chỉ Dryad/Mendeley có SHA-256 nguồn để đối chiếu. WUR công bố MD5 archive, chưa có đối chiếu SHA-256 độc lập từ tác giả.

Dryad API download yêu cầu token; liên kết tải công khai trả trang xác minh khi gọi từ shell. Đã dùng thao tác tải thông thường trong trình duyệt, kiểm tra hash rồi copy vào project. Phản hồi HTML thất bại lưu riêng ở `dryad-download-validation-response.html`, không tính là dữ liệu Excel. Không thu thập credential hay viết scraper.

## Đã khảo sát nội dung local

### Mendeley

- `tomato irrigation dataset.csv`: **3.000 dòng dữ liệu, 14 cột**, không có dòng sai số trường; không thấy token rỗng/NaN/NA/null trong lần đếm cú pháp này. Không phải xác nhận giá trị đúng hoặc không trùng.
- Header gồm nhiệt độ, độ ẩm, độ ẩm đất, ET0/ET, crop coefficient/giai đoạn, N/P/K, bức xạ, gió, ngày sau trồng và pH. **Không có cột năng suất, chi phí hoặc hành động tưới thực đo trong CSV này.**
- `tomato_water_sensor_data.json`: **393 bản ghi**. Đã đọc mẫu có `dateTimeAdded`, `moisturePercentage`, `waterVolume_liter`, `motorValue`, `irrigation_needed_value`, `reference_eto`, `cropCoffiecient` và các field cấu hình/cảm biến khác.
- Cần xác minh đơn vị ET, độ ẩm đất raw, nguồn công thức, thời điểm đo, ý nghĩa motor/action và tính độc lập các bản ghi. Không mặc định `irrigation_needed_value` là nhãn tối ưu được xác thực; không mặc định các field chứa chữ optimal là kết quả thí nghiệm. CSV và JSON chưa chứng minh có khóa nối một-một.

### WUR

Có sáu nhóm AICU, Automatoes, Digilog, IUACAAS, Reference, TheAutomators và một nhóm Weather. Mỗi nhóm nhà kính có bảy bảng; tổng **43 CSV, 622.899 dòng dữ liệu** theo đếm cú pháp, không phải 622.899 thí nghiệm độc lập.

| Bảng | Số file | Tổng dòng dữ liệu |
| --- | --- | --- |
| GreenhouseClimate | 6 | 286.854 |
| GrodanSens | 6 | 286.854 |
| CropParameters | 6 | 138 |
| LabAnalysis | 6 | 60 |
| Production | 6 | 140 |
| Resources | 6 | 996 |
| TomQuality | 6 | 48 |
| Weather | 1 | 47.809 |

Đã đọc header/mẫu và PDF nguồn. `Production` có `ProdA/ProdB`; PDF giải thích kg/m² tại kỳ thu hoạch. `Resources` có tiêu thụ nhiệt, điện, CO2, tưới và drain; `GreenhouseClimate` có nhiệt độ, ẩm, CO2, irrigation và setpoint. Timestamp ở dạng số Excel, tần suất khác nhau. Có NaN ở dữ liệu nguồn.

**Lỗi cấu trúc đã thấy:** `Reference/TomQuality.csv` có header 7 trường nhưng cả 8 dòng dữ liệu có 8 trường; `Weight` và `DMC_fruit` bị dính ở header. Chưa sửa raw; cần sửa có tài liệu ở bản dẫn xuất sau khi đối chiếu ReadMe.

PDF Economics có cơ chế tính điểm lợi nhuận và giá giả định của cuộc thi; dataset chưa chứa sẵn kết quả kinh tế tính hoàn chỉnh. Tác giả nêu nhiều chi phí thương mại không được tính. Không dùng giá cuộc thi làm lợi nhuận thực tế ở Việt Nam. Bộ này cung cấp bằng chứng nghiên cứu nhà kính cà chua bi, chưa xác nhận hiệu quả khuyến nghị ngoài miền thí nghiệm.

### Dryad

Cả bốn workbook đã mở bằng openpyxl chỉ đọc, không tính hoặc thực thi công thức. Có header nhiều tầng, công thức Excel và ô trống/định dạng rộng. Ví dụ worksheet quality khai báo `max_column=16367`; đó không phải 16.367 đặc trưng canh tác.

- Quality: mẫu có chất rắn hòa tan, vitamin C, acid, đường, công thức trung bình; **12 dòng mã** dạng `T1-1`…`T4-3`.
- Photosynthetic: **60 dòng mã**, các field thoát hơi nước, quang hợp, CO2 nội bào, khí khổng.
- Leaf/stem: **36 dòng mã**; fruit: **60 dòng mã**; khối lượng và tỷ lệ/hàm lượng N/P/K. Khối lượng mẫu quả chưa đồng nghĩa năng suất toàn vụ trên diện tích.
- Irrigation: sheet 87 hàng khai báo (gồm header), bốn khối dữ liệu tưới; cần xác minh cách bốn khối liên hệ với 12 tổ hợp xử lý.

Các mã local nhóm theo T1–T4 và các cấp số phía sau. Phải đối chiếu thiết kế nghiệm thức trong metadata/bài báo trước khi gán nước–đạm–phân hữu cơ; không tự equate `T1-1` với treatment `T1` của bảng mô tả. Chưa chứng minh mọi kết quả yield trong bài báo có bản raw tương ứng trong các file tải.

## Đề xuất sử dụng và công việc còn lại

1. Chốt một mục tiêu đo được: ví dụ năng suất/nước trong điều kiện nhà kính hoặc so sánh nghiệm thức nước–phân. Những file đã tải là nguồn nghiên cứu, chưa là bộ train/test đã chuẩn hóa.
2. WUR có biến tài nguyên, thu hoạch và hướng dẫn kinh tế rõ nhất cho khảo sát quan hệ đầu vào–kết quả. Cần xử lý timestamp, đơn vị, missingness, gom cửa sổ thời gian, dữ liệu trễ và ràng buộc theo khoang/crop cycle. Số bản ghi lớn không khắc phục số môi trường độc lập ít.
3. Dryad phù hợp nghiên cứu so sánh nghiệm thức sau khi xác minh mapping và kết quả diện tích/toàn vụ. Số nghiệm thức nhỏ; chưa đủ căn cứ để huấn luyện mô hình tổng quát nhiều biến.
4. Mendeley phù hợp khảo sát cảm biến/tưới; cần xác minh nhãn và công thức trước khi đề xuất supervised learning. Không dùng target tính từ input như bằng chứng mô hình học quyết định tối ưu thực nghiệm.
5. Không ghép ba bộ thành một bảng train chung trước khi có semantic schema, đơn vị, crop/context, nguồn và định nghĩa outcome thống nhất. Chia theo thời gian/khoang/nghiệm thức, tránh random split các dòng phụ thuộc. Không chọn mô hình/ngưỡng bằng test.
6. Phần nhận diện ảnh EfficientNet/ResNet50 vẫn độc lập với dữ liệu canh tác dạng bảng. Việc tải các bộ này không đồng nghĩa đã duyệt thêm mô hình hoặc mở rộng MVP; không suy lượng phân/nước từ nhãn bệnh ảnh.
7. Chưa kiểm tra sâu duplicate, sensor calibration, sai số đo, nhân quả, tính phù hợp tại Việt Nam hoặc hiệu quả ngoài thực tế; chưa có metric tối ưu, năng suất hay tiết kiệm được đo bởi dự án.

Khi dùng CC BY 4.0 phải ghi công tác giả, DOI/phiên bản, giấy phép và thay đổi; với CC0 vẫn giữ citation cho liêm chính học thuật. Không sửa bản nguồn; mọi dữ liệu chuẩn hóa sau này lưu ở vùng dẫn xuất kèm manifest, mapping và phiên bản.
