# WUR — báo cáo làm sạch kỹ thuật

Tên đề tài: **Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua**.
Phạm vi phiên: **chỉ Prompt 2, dataset WUR**. WUR là tài nguyên nghiên cứu bổ sung, không là phụ thuộc MVP nhận diện lá/hướng dẫn chăm sóc. Không thêm bài toán tối ưu canh tác.

Run hiện tại: `wur-7439c4f996527052`, ngày 2026-10-14. Dẫn xuất: `../../processed/wur/wur-7439c4f996527052/`.
Trạng thái: **cleaned_technical + needs_review + research_only**. `training_ready=false`; không có tập train/validation/test.

## Nguồn, quyền và skill thực dùng

- Nguồn local bất biến: `../../raw/cultivation/wur_greenhouse_2019_v2/`, gồm archive 7z, CSV đã giải nén và hai PDF nguồn.
- Autonomous Greenhouse Challenge, Second Edition (2019), **4TU version 2**. DOI `10.4121/uuid:88d22c60-21b3-4ea8-90db-20249a5be2a7`. [Trang nguồn đã lưu ở thời điểm tiếp nhận](https://data.4tu.nl/articles/dataset/Autonomous_Greenhouse_Challenge_Second_Edition_2019_/12764777/2).
- Giấy phép **CC0-1.0 theo metadata tiếp nhận local**. Archive đã được đối chiếu MD5 công bố ở phiên tiếp nhận. Phiên này đối chiếu lại SHA-256 local cho tất cả 46 file với intake; không tải lại hay xác minh website mới. CSV giải nén có hash local, không gọi đó là SHA-256 độc lập do tác giả công bố.
- Đã đọc hướng dẫn Prompt 2, quy tắc project, registry skill và pipeline PlantVillage/PlantExpert đang có. Không sửa pipeline/kết quả của hai bộ đó.
- Workflow chính **migration**: mở rộng bằng dẫn xuất phiên bản, giữ raw, manifest, checkpoint; xác minh rồi cập nhật riêng entry WUR của registry; có đường rollback.
- **Ponytail full**: tái sử dụng `digest/snapshot/write_json/write_csv/verify_artifacts` từ pipeline PlantExpert; CSV, hash, Decimal và unittest dùng thư viện chuẩn. Không thêm dependency.
- **pdf:pdf**: đọc ReadMe/Economics bằng pypdf/pdfplumber, render trang 14 với Poppler, kiểm tra hình bảng để chứng minh header. Không thực thi mã, macro hoặc JavaScript trong tài liệu.
- Không tìm thấy workflow chuyên làm sạch WUR/Python trong catalog đã kiểm tra. Skill Spreadsheets được kiểm tra về độ phù hợp nhưng không áp dụng workflow tạo workbook; đầu ra là pipeline Python/CSV theo quyền người dùng. Skill `e2e` đã được đọc để kiểm tra khả năng: không có frontend, URL hoặc `e2e.config.ts` áp dụng. Không chạy browser E2E, không tạo ứng dụng/config E2E hay gọi AI.
- Không kích hoạt BMAD build/dev hoặc nhập draft thành kế hoạch chính thức. Registry giữ bối cảnh; đây là kết quả pipeline dữ liệu, không giả vờ là BMAD tự làm sạch.

## Kết quả trước/sau đã đo

| Phạm vi | Trước | Sau |
| --- | ---: | ---: |
| File nguồn trong phạm vi hash | 46 | 46; SHA-256 giữ nguyên |
| CSV dữ liệu | 43 | 43 bảng chuẩn hóa riêng |
| Bản ghi dữ liệu, không tính header | 622.899 | 622.899 retained |
| Bản ghi excluded | — | 0 |
| Bản ghi quarantine kỹ thuật | — | 0 |
| Bản ghi retained còn needs_review | — | 622.899 |
| Ô missing ở các cột dữ liệu được giữ | 1.413.536 | 1.413.536, biểu diễn CSV rỗng |
| Ô có số 0 ở các cột dữ liệu được giữ | 3.818.128 | 3.818.128 |
| Cột trống dư đã chứng minh | 5 ở IUACAAS/Resources | 0 trong dẫn xuất; 830 ô trống dư không mang dữ liệu |

46 file = 43 CSV + ReadMe.pdf + Economics.pdf + 1 archive 7z. Tổng **112.101.340 byte** nguồn, giữ nguyên. Các manifest tiếp nhận và metadata tham chiếu cũng giữ nguyên hash.

| Loại bảng | Số bảng | Dòng nguồn = dòng dẫn xuất | Số cột dữ liệu sau chuẩn hóa |
| --- | ---: | ---: | ---: |
| CropParameters | 6 | 138 | 6 |
| GreenhouseClimate | 6 | 286.854 | 50 |
| GrodanSens | 6 | 286.854 | 7 |
| LabAnalysis | 6 | 60 | 39 |
| Production | 6 | 140 | 9 |
| Resources | 6 | 996 | 7 |
| TomQuality | 6 | 48 | 8 |
| Weather | 1 | 47.809 | 11 |

Dẫn xuất thêm hai cột provenance `record_id`, `source_record`. Sáu nhánh được giữ nguyên tên thư mục: AICU, Automatoes, Digilog, IUACAAS, Reference, TheAutomators. Weather là bảng môi trường chung. Đây là group theo nguồn, **không phải nhãn treatment hoặc replicate được tự suy đoán**. ReadMe mô tả năm đội và một Reference; không nhân 622.899 dòng thành số thí nghiệm độc lập.

## Biến đổi có căn cứ

1. CSV parse strict `utf-8-sig`, dấu phẩy; kiểm tra độ rộng từng dòng. Không đổi thứ tự hoặc loại dòng dữ liệu.
2. Trim/NFC tên cột; đổi duy nhất khóa timestamp `%Time/%time` thành `time_excel_serial`. Giữ tên các biến khác, ánh xạ theo vị trí trong data dictionary. Cột trùng tên sau chuẩn hóa bị quarantine thay vì gộp.
3. Trim/NFC lexeme số; kiểm tra bằng Decimal, không ép float/làm tròn. `NaN/nan` và ô trống thành missing CSV rỗng. Token gốc có thể phục hồi từ file raw, hash và dòng nguồn; thống kê lexeme missing theo bảng được lưu. Không thay missing bằng 0.
4. **Reference/TomQuality**: header nguồn có **7 trường**, mọi dòng dữ liệu có **8 trường**. Header cuối `Weight\tDMC_fruit` tách thành hai tên cột. ReadMe trang 14 ghi riêng `Weight` (g) và `DMC_fruit` (%); năm CSV cùng loại của các đội khác có đúng tám header. Tám dòng Reference sau sửa đều khớp tám giá trị. Không tách ô dữ liệu, không dịch vị trí số liệu. Dữ liệu đầu tiên vẫn là Weight `7.77`, DMC missing; dòng thứ ba giữ `7.47`, `9.59`.
5. **IUACAAS/Resources**: header và tất cả **166 dòng** có 12 trường; năm trường cuối không tên, đều thực sự trống. Dẫn xuất bỏ đúng năm cột đó, giữ bảy cột có tên. Không mất dòng hay giá trị khác; raw phục hồi được toàn bộ cột trống.
6. Ghi dictionary từ bảng PDF: giữ nguyên heading, unit, interval và page của nguồn. Match chỉ exact/trim/casefold không nhập nhằng; **không tự áp alias gần giống**. Không đổi đơn vị.

Chi tiết: [transformation log](wur-7439c4f996527052/transformation-log.json), [data dictionary](wur-7439c4f996527052/data-dictionary.json), [dictionary nguồn PDF](wur-7439c4f996527052/source-unit-dictionary.json), [bằng chứng PDF từng trang](wur-7439c4f996527052/pdf-evidence.json).

## Timestamp, tần suất, missingness và trùng

- ReadMe xác nhận **Excel format**, nhưng chưa chứng minh epoch 1900/1904 hoặc timezone. Chỉ giữ Decimal serial; không xuất canonical ngày lịch, UTC hay gán múi giờ Việt Nam/Hà Lan. Các chỉ số thứ tự và chênh lệch dùng serial, không cần timezone.
- GreenhouseClimate/GrodanSens/Weather: mỗi bảng 47.809 dòng; serial **43815–43981**. Tần suất mô tả 5 phút; observed delta `0.00347/0.00348` ngày do độ chính xác nguồn. Dùng tolerance **1 giây** cho kiểm tra audit, ghi trong config; không resample/làm tròn thời gian. Không phát hiện chênh lệch vượt tolerance ở những bảng này.
- Resources: 166 dòng mỗi đội, chênh lệch **1 ngày**, phù hợp daily trong ReadMe.
- CropParameters: mỗi đội 23 dòng; **21 khoảng 7 ngày, 1 khoảng 8 ngày**.
- LabAnalysis: mỗi đội 10 dòng; **3 khoảng 14 ngày, 4 khoảng 15 ngày, 1 khoảng 13 ngày, 1 khoảng 12 ngày**. Mô tả nguồn bi-weekly; chưa tự coi sai hoặc dời timestamp.
- TomQuality: mỗi đội 8 dòng; **6 khoảng 14 ngày, 1 khoảng 16 ngày**. Bi-weekly từ tài liệu, lịch thực tế không hoàn toàn cố định.
- Production là dữ liệu ở ngày thu hoạch, **không ép một tần suất cố định**. AICU/Reference có 24 dòng, các đội còn lại 23.
- **Reference/Production, bản ghi 1, dòng CSV 2: serial `43510`** nằm ngoài span climate cùng nhóm `[43815,43981]`. Giữ nguyên `43510`; không đoán sửa thành ngày giống đội khác.
- **48 cờ cadence**, **1 cờ timestamp ngoài span**. Chúng là cờ audit cần diễn giải, không mặc nhiên là lỗi. Có 49 record mang cờ cụ thể; toàn bộ 622.899 record vẫn needs_review do epoch/phạm vi thí nghiệm và kiểm duyệt ý nghĩa chưa xong.
- Không phát hiện file nguồn trùng byte, dòng trùng sau chuẩn hóa hoặc timestamp trùng trong cùng bảng; không phát hiện giảm thứ tự serial. Không thực hiện semantic/near duplicate xuyên đội; giá trị đo lặp được giữ, không xem là lỗi.
- Missingness ở 30 bảng, tổng **1.413.536 ô**. Per-column/per-table, token gốc, zero count, min/max và histogram delta nằm trong [audit đầy đủ](wur-7439c4f996527052/tables.json). Không impute, scale, cân bằng, chọn ngưỡng học, nối bảng hay nội suy target.
- ReadMe trang 17 nói Grodan đã được tác giả chuyển 3 phút thành 5 phút và dữ liệu có đến May 26. Không thực hiện lại resampling; các missing phía sau giữ nguyên. Crop parameters có ghi giới hạn sau khi bấm ngọn; không tự loại dòng muộn hoặc filling.

Đơn vị quan trọng: ProdA/ProdB `kg/m²` tại ngày thu hoạch; các Weight_fruits_ClassA/B là `g` của mẫu theo mô tả nguồn; không gọi chúng là năng suất toàn vụ. Resources có MJ/m²/day, kWh/m²/day, kg/m²/day, L/m²/day. Economics là quy tắc giá/chi phí của thử thách; nguồn nói economic calculations chưa có trong dataset. Không tính profit hoặc suy ra lợi ích tại Việt Nam.

## Review queue và checkpoint

[Review queue](wur-7439c4f996527052/review-queue.json): **134 mục**; một mục có thể đại diện nhiều dòng/cột. Không cộng số mục thành số record lỗi.

| Lý do | Số mục | Cách tiếp tục |
| --- | ---: | --- |
| Cờ thời gian/cadence của record | 49 | Xác minh lịch thu/nhập nguồn; riêng `43510` cần tài liệu/tác giả, không tự sửa |
| Missing retained theo bảng | 30 | Xác minh outage/giai đoạn sinh trưởng và giới hạn cảm biến; chưa impute |
| Epoch/timezone và scope/group chưa đủ bằng chứng | 43 | Xác nhận hệ ngày Excel, lịch nguồn, đơn vị thí nghiệm; giữ serial nếu chưa có |
| Alias đơn vị chưa khớp | 12 | `water_sup_intervals_sp_min/vip_min` trong sáu bảng climate khác `water_sup_int_sp_min/vip_min` trong ReadMe; chưa áp alias |

Dictionary timestamp Weather không bắt được heading trống trong bảng PDF; climate có hai entry Time ở hai mục. Đã giữ nguyên extraction, không chọn một entry tùy ý. Những vấn đề này thuộc checkpoint timestamp/dictionary, cần xem PDF trước khi dùng ngày lịch. Extraction còn giữ các câu bị ngắt dòng hoặc nối trang; không coi toàn bộ dictionary máy trích là đã được kiểm duyệt.

Ngoài 134 mục kỹ thuật, **domain review chưa thực hiện**: giá trị/range, hiệu chuẩn sensor, nhãn Raw/Processed của tác giả, thực nghiệm độc lập, target/window và khả năng suy luận nhân quả. Không tuyên bố mọi outlier/đơn vị đã đúng chỉ vì parse thành công.

[Checkpoint](wur-7439c4f996527052/checkpoint.json) lưu phần chờ. Không có blocker làm sạch kỹ thuật đã đủ căn cứ. Các việc chưa xác minh chặn tái sử dụng nghiên cứu tương ứng; **không chặn MVP** vì WUR ngoài phụ thuộc MVP. Chưa có quyền train hoặc sửa raw; không tiếp tục qua checkpoint bằng suy đoán.

## Provenance, chạy lại và rollback

- [Manifest từng record](../../processed/wur/wur-7439c4f996527052/manifest.csv): stable ID `wur:<team>:<type>:<source_record>`, source file/row/line-end/SHA-256, processed file/record, status, flag, cell transformation count. `source_record` bắt đầu 1 sau header; physical `source_line_end` do CSV parser ghi.
- Hash [trước](wur-7439c4f996527052/raw-before.csv)/[sau](wur-7439c4f996527052/raw-after.csv) khớp cả 46 file và manifest tiếp nhận. [Fingerprint](wur-7439c4f996527052/fingerprint-inputs.json) khóa nguồn, input metadata, code/helper/config và phiên bản Python/PDF parser.
- [Output hashes](wur-7439c4f996527052/output-artifacts.json) kiểm tra toàn bộ tập file dẫn xuất/report của run. Chạy lại cùng fingerprint chỉ xác minh và dùng kết quả có sẵn. Output bị thêm/sửa hoặc partial run bị chặn ghi đè, có checkpoint lỗi.
- Registry được sao lưu có timestamp trước khi sửa; chỉ cập nhật entry WUR. Rollback: chọn lại entry WUR trong backup nếu cần; giữ nguyên mọi kết quả, không xóa raw hoặc khôi phục cả registry làm mất phiên khác. Các bản đầu ra đã duyệt không bị ghi đè.
- Bản dẫn xuất không chứa dataset ảnh/tri thức, không là bản ghép train chung. UI/model/training đều chưa thực hiện.

## Môi trường và lệnh tái lập

Python **3.12.14**, pypdf **6.10.0**, pdfplumber **0.11.9**, Windows 11 build 26200. Runtime bundled hiện có, không cài package/GPU stack. Poppler bundled chỉ render PDF nguồn. CSV dùng stdlib.

Chạy từ project root trong PowerShell:

```powershell
$pipelinePython = 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $pipelinePython -B -m unittest discover -s scripts/data -p test_clean_wur.py -v
& $pipelinePython -B scripts/data/clean_wur.py --config scripts/data/wur-config.json --project-root .
& $pipelinePython -B scripts/data/verify_wur.py --config scripts/data/wur-config.json --project-root . --run-id wur-7439c4f996527052
# Lần thứ hai chỉ xác minh idempotency, không tạo bản nhân đôi:
& $pipelinePython -B scripts/data/clean_wur.py --config scripts/data/wur-config.json --project-root .
```

File thực hiện: [pipeline](../../../../../scripts/data/clean_wur.py), [config](../../../../../scripts/data/wur-config.json), [test](../../../../../scripts/data/test_clean_wur.py), [verifier độc lập](../../../../../scripts/data/verify_wur.py). Config không hardcode đường dẫn dữ liệu máy; executable trong lệnh trên là runtime của máy được kiểm chứng.

## Kiểm chứng

- **10 unittest đạt**: hai lỗi header thực tế, bằng chứng repair, collision, Decimal/missing/0, temporal flags, provenance/quarantine/count, raw bảo toàn, idempotency, intake/output tampering, partial failure và output overlap.
- Production: pipeline hoàn thành **43 bảng, 622.899 retained, 0 excluded, 0 quarantine**, hash trước/sau/intake khớp.
- Chạy pipeline lần hai: **idempotent_existing_verified**, cùng run ID.
- Verifier độc lập đọc lại raw, từng giá trị và toàn bộ record manifest; kết quả lưu ở [validation](validation-wur-7439c4f996527052.json). Chỉ dùng kết quả `passed` đã chạy; test fixture không thay thế việc kiểm trên dữ liệu thật.
- Browser E2E không chạy: chưa có ứng dụng/config/URL trong project và không có user flow UI trong phạm vi dataset. Không chạy SAST/pentest hoặc tuyên bố audit code sản phẩm.

Bằng chứng bàn giao: [log 10 test](tests-wur-7439c4f996527052.txt), [kiểm chứng registry](registry-verification-wur-7439c4f996527052.json), [backup registry trước sửa](registry-before-20261014T141208.json). Registry hiện tại là `../../dataset-registry.json`; đã xác minh mọi entry dataset khác và metadata cấp root giữ nguyên. Project không có Git repository; dùng backup timestamp và fingerprint/hash thay cho checkpoint Git.

Bước kế tiếp theo thứ tự đã đề xuất: **Dryad**, chỉ trong phiên được yêu cầu riêng. Phiên WUR dừng tại báo cáo/checkpoint và registry; không làm sạch Dryad, code ứng dụng, dịch hàng loạt hoặc train.
