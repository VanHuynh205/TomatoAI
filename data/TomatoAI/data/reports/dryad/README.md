# Báo cáo làm sạch kỹ thuật Dryad

Ngày thực hiện: 2026-10-14, Asia/Bangkok. Run hiện hành: **dryad-8b0f7c218098bfdf**.

Đề tài: **Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua**. Phiên này chỉ thực hiện Prompt 2 cho Dryad. Dữ liệu canh tác này là tài nguyên **research_only**, không phải phụ thuộc MVP nhận diện trạng thái lá và hướng dẫn chăm sóc. Không có code sản phẩm, huấn luyện hoặc mô hình tối ưu canh tác được tạo trong phiên.

## 1. Phạm vi, nguồn và cách thực hiện

Nguồn bất biến: `../../raw/cultivation/dryad_water_nitrogen_2024_v5/`. Có 4 XLSX và README, tổng **5 file, 159.125 byte**. Không có archive thuộc nguồn này. Mỗi file khớp byte và SHA-256 của `../../cultivation_metadata/download-manifest.json`, đồng thời khớp trước/sau pipeline và verifier. Không di chuyển, đổi tên, lưu lại workbook hoặc sửa README nguồn.

DOI dataset: [10.5061/dryad.wm37pvn33](https://doi.org/10.5061/dryad.wm37pvn33). Metadata tiếp nhận ghi version **5**, version ID **446657**, publicationDate **2026-06-09**, versionStatus **submitted**, giấy phép khai báo **CC0-1.0**. Giữ nguyên trạng thái API này; không suy diễn nó thành trạng thái xuất bản khác. Manifest tiếp nhận có digest SHA-256 công bố của từng file. Thông tin giấy phép/phiên bản là bằng chứng từ metadata đã nhận, không phải một đánh giá pháp lý mới.

Pipeline: `scripts/data/clean_dryad.py`; config: `scripts/data/dryad-config.json`; test: `scripts/data/test_clean_dryad.py`; verifier độc lập: `scripts/data/verify_dryad.py`. Đường dẫn được cấu hình tương đối theo project, không hardcode đường dẫn Windows vào logic. Các helper hash/snapshot/artifact seal được tái sử dụng từ `clean_plantexpert.py`, không sửa script của các phiên trước.

Workflow chính thực dùng: **migration** — mở rộng bằng bản dẫn xuất riêng, giữ reader/raw cũ, kiểm chứng bảo toàn, chạy lại idempotent, lưu checkpoint lỗi và không thực hiện contraction. **Ponytail full** — tái sử dụng helper, dùng thư viện chuẩn để đọc sparse OOXML, không thêm dependency. Skill **Spreadsheets** có trong catalog và đã được khảo sát; không dùng workflow tác giả workbook/recalculate của skill đó. Không có skill chuyên dụng làm sạch Dryad/Python preprocessing được chọn. Không gọi BMAD build/dev hay coi BMAD là bộ xử lý dữ liệu. Planning chính thức chưa được nhập.

Môi trường thực chạy: Python **3.12.14**, Windows 11 build 26200. Pipeline dùng stdlib `zipfile`, `xml.etree.ElementTree`, `Decimal`, `json`, `csv`; verifier dùng **openpyxl 3.1.5** đã có trong runtime bundled. Không cài dependency, không tải dataset/weights và không gọi API AI/dịch thuật.

## 2. Đối chiếu trước/sau

| Nguồn/sheet | Dòng dữ liệu vật lý | Bảng dẫn xuất | Record dẫn xuất giữ lại | Ô công thức |
| --- | ---: | --- | ---: | ---: |
| Quality / Sheet1, hàng 3–14 | 12 | quality | 12 | 48 |
| Photosynthetic / Sheet1, hàng 2–61 | 60 | photosynthetic | 60 | 0 |
| Weights / `Leaf and stem `, hàng 2–37 | 36 | leaf_stem | 36 | 0 |
| Weights / fruit, hàng 2–61 | 60 | fruit | 60 | 60 |
| Irrigation / `历史数据`, hàng 3–87 | 85 | irrigation_1 đến irrigation_4 | 340 | 0 |
| **Tổng** | **253** | **8 bảng, từ 5 sheet/4 workbook** | **508** | **108** |

253 là số lần xuất hiện dòng trong các bảng nguồn; **không phải 253 thí nghiệm độc lập**. 508 gồm bốn bản ghi khối tưới cho mỗi ngày nguồn. Trường ngày A được tham chiếu lại có chủ đích; không tạo ra 508 thí nghiệm. Manifest bảo toàn sheet/hàng/cột gốc để đối chiếu sự mở rộng này.

**Retained: 508; excluded: 0; quarantined technical: 0; needs_review: 508.** Needs_review là tập con trạng thái của retained, không cộng vào retained lần nữa. Không phát hiện ô body thiếu hoặc sai kiểu theo schema đã cấu hình trong run này. Điều này không chứng minh không có thiếu đo đạc bên ngoài bảng được cung cấp.

| Kiểm kê ô serialized | Số lượng | Cách xử lý |
| --- | ---: | --- |
| Tổng cell element trong OOXML | 36.223 | Lưu toàn bộ trong cell-ledger.jsonl |
| Ô có nội dung/công thức | 3.119 | Đối chiếu độc lập với openpyxl |
| Ô trống nhưng có serialization/định dạng | 33.104 | Không tạo feature; vẫn có provenance trong ledger |
| Công thức | 108 | Tách expression/attributes/shared base và cached value |
| Công thức thiếu cache | 0 | Cache hiện diện; độ cập nhật/chính xác chưa được duyệt |
| Ô số 0 trong bảng dẫn xuất | 254 | Giữ đúng lexeme, không coi là missing |
| Ô có nội dung ngoài schema bảng | 1 | `Leaf and stem `!S1 chứa đúng một dấu cách; giữ trong unmapped-cells.json và ledger |

Quality khai báo `A1:XEM28` (16.367 cột) nhưng nội dung chỉ A–W, hàng 1–14. Photosynthetic khai báo đến BW (75 cột), nội dung chỉ A–E. Leaf/stem có cột I phân cách, Q/R trống và S1 dấu cách. Không lấy `max_column` làm số đặc trưng; không gọi dấu cách là ô thực sự trống. Inventory đã duyệt mọi cell element serialized; nội dung ngoài cột/hàng chọn đều được giữ và xếp review. Không cấp phát lưới theo vùng khai báo rộng.

79 **mục review**, không phải 79 record: 8 mapping nghiệm thức/group; 8 đơn vị; 56 nhóm vector phép đo lặp giữ nguyên; 1 ô dấu cách ngoài schema; 6 vấn đề liên bảng/cache/đơn vị/thời điểm/ý nghĩa quả. Có **60 khóa Code trùng chính xác giữa các bảng**, chỉ lưu candidate, không join. Không có Code trùng trong cùng bảng, không có trùng ngày hoặc giảm thứ tự ngày ở bốn bảng tưới. Các nhóm vector lặp chủ yếu xuất hiện khi không tưới và đồng hồ giữ nguyên; sự lặp không tự động là dữ liệu lỗi. Flag có thể chồng nhau, xem tables.json và review-queue.json.

## 3. Schema và biến đổi có căn cứ

Mỗi JSONL record có schema_version, record_id, source_file, source_sha256, source_sheet, source_row, original_key, fields, flags, status và training_ready. `treatment_id`, `replicate_id`, `experimental_group` đều **null** vì mapping chưa đủ bằng chứng. `record_id` dựa trên bảng và hàng nguồn; không dựa trên Code để tránh gộp nhầm record trùng.

Field key dùng chữ cột Excel, duy nhất trong từng bảng. `data-dictionary.json` lưu label ở từng tầng, source_cell, merged_anchor, unit token nguyên gốc và trạng thái đơn vị. Ví dụ Quality H có nhóm từ A1:H1 và label H2; không nhân bản giá trị đo từ merged header. Leaf/stem giữ hai nhóm theo đúng cột nguồn B–H/J–P, không ép các header giống nhau thành một cột. Tên sheet có dấu cách cuối và Unicode được giữ nguyên.

| Loại trường | Dẫn xuất | Bằng chứng/giới hạn |
| --- | --- | --- |
| Code | opaque_id, chuỗi gốc | Không cắt `T1-1-1` thành treatment/replicate được duyệt |
| Ngày tưới | calendar_date, ISO `YYYY-MM-DD` | Nguồn là chuỗi, từ 2024-04-01 đến 2024-06-24; không gán timezone |
| Trạng thái tưới | boolean từ Yes/yes/No | Mapping literal minh bạch; raw_value còn nguyên |
| Số đo | decimal_text | Giữ chuỗi numeric OOXML/text, độ chính xác và số 0; không float-rounding |
| Công thức | kind=formula, value=null | Cached_kind/cached_value riêng; không dùng cache như số đo trực tiếp |
| Ô thiếu | kind=missing, value=null | Không thay thành 0; run thật không có body cell thiếu |

Ledger giữ raw cell XML, XML attributes, style index, raw_v, raw kind/value và shared formula base. Shared-formula follower có expression trống vẫn là **công thức**, không phải missing. Ví dụ fruit H4 lưu group/shared base H3, expression gốc follower null và cache riêng. Verifier chỉ dịch địa chỉ tham chiếu bằng Translator để đối chiếu text với openpyxl, **không tính công thức**.

Không tính lại trung bình/tỷ lệ, không scale %, đổi đơn vị, impute, xóa outlier, dịch dataset, tạo target, nối bảng hay split. Min/max trong tables.json là thống kê audit của giá trị gốc, không là khoảng nông học đã chấp thuận. Header % và giá trị dạng 0,02 được giữ; chưa nhân/chia 100.

## 4. Bằng chứng nghiên cứu và phần chưa xác minh

Metadata liên kết [bài báo chính thức PLOS](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0354927). Methods mô tả 12 nghiệm thức với ba lần lặp. Cách mã hóa bảng nguồn vẫn chưa có crosswalk được xác minh. Đường đọc riêng Table 2 qua công cụ web lỗi; không tuyên bố đã đọc/duyệt toàn bộ bảng đó. Không gán `T1-1` thành `T1`, hoặc khối tưới 1–4 thành nghiệm thức của bài báo.

Methods bài báo ghi VC mg/100g và đường hòa tan mg/g; một số header nguồn ghi %. README ghi chất rắn °Brix, header trung bình ghi %. Những khác biệt này được đưa vào review, không chuyển đơn vị dựa riêng vào bài báo. Nguồn: [PLOS, mục phương pháp](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0354927).

Đã đọc README nguồn và mẫu đại diện từng sheet; đã kiểm chứng toàn bộ cell nội dung, provenance và cache. Chưa có kiểm duyệt nông học, xác minh freshness cache, khóa liên bảng, thiết kế thí nghiệm độc lập hoặc tính hợp lệ của outlier. Khối lượng quả mẫu g **không được đặt tên thành năng suất toàn vụ**. Không trích kết luận “tối ưu” của nghiên cứu làm nhãn train hoặc hướng dẫn áp dụng cho người dùng Việt Nam.

## 5. Review/checkpoint và tiêu chí tiếp tục

Checkpoint: `dryad-8b0f7c218098bfdf/checkpoint.json`. Queue chi tiết: `dryad-8b0f7c218098bfdf/review-queue.json`. Tất cả record giữ trạng thái **cleaned_technical ở cấp pipeline; needs_review; research_only**, training_ready=false. “Cleaned_technical” chỉ xác nhận parse/provenance/biến đổi kỹ thuật trong schema hiện có, không xác nhận ngữ nghĩa hoặc sẵn sàng train.

| Vấn đề còn mở | Bằng chứng cần bổ sung/duyệt | Điều kiện chấp thuận |
| --- | --- | --- |
| Code/nghiệm thức/replicate/khối tưới | Bảng source hoặc xác nhận tác giả có crosswalk cụ thể | Mỗi mapping có nguồn, không suy từ hình thức Code; xác định đơn vị độc lập |
| Đơn vị Quality/photosynthesis và scale N/P/K | Tài liệu field-level, phương pháp và đối chiếu giá trị | Chốt đơn vị/scale từng cột trước bất kỳ chuyển đổi; phiên bản dẫn xuất mới nếu sửa |
| Cache 108 công thức | Bằng chứng tính toán được cho phép ở một lượt riêng | Không đánh đồng “cache khớp lưu trong XLSX” với “cache đúng/current” |
| Thời điểm daily volume/meter | Quy ước đo của từng khối/ngày | Không tự sửa chênh lệch đồng hồ; lưu event time nếu nguồn xác nhận |
| Vector lặp/khóa liên bảng | Danh sách row trong queue và ngữ cảnh lấy mẫu | Duyệt lặp hợp lệ/duplicate; không xóa chỉ vì cùng giá trị |
| Ô S1 dấu cách | Ledger và workbook gốc | Có thể duyệt không phải field; hiện đã giữ trong supplementary ledger |
| Ứng dụng nông học tương lai | Câu hỏi nghiên cứu, domain review và dữ liệu bối cảnh | Chỉ khi được yêu cầu riêng; không mở rộng MVP phiên này |

Không cần hỏi thêm để hoàn thành nhánh kỹ thuật. Các quyết định ngữ nghĩa bị chặn đã có checkpoint; không cần đoán để “hoàn tất”. Không random split các dòng theo ngày/cùng Code. Nếu sau này có quyền nghiên cứu dự đoán, phải chốt grouping và target, rồi fit mọi bước học tham số trên train.

## 6. Kiểm chứng thực chạy và tái lập

12 test unittest **PASS**: zero/precision/nonfinite, formula/cache/missing, date/status/opaque IDs, merged-header provenance, header mismatch, duplicate ID/vector không gộp, DTD/UTF-16/unsafe ZIP, giới hạn part/macro, shared follower/whitespace, output không được nằm trong raw, checkpoint partial không ghi đè, idempotency và từ chối output bị sửa.

Verifier openpyxl độc lập **PASS**: 3.119 ô nội dung; 108 công thức cùng cache; 508 record, 253 dòng vật lý; 36.223 ô ledger; dictionary/manifest/schema; 254 số 0; ngày tưới; 5 raw file và 5 reference file hash bất biến. So sánh numeric với openpyxl theo giá trị đọc tương ứng; precision đầy đủ được giữ từ XML lexeme trong ledger. Chưa đánh giá tính đúng nông học của giá trị/cache.

Chạy lại pipeline **PASS, idempotent_existing_verified**, không thêm run/table hay ghi đè artifact. Tamper refusal được kiểm tra trên fixture tạm, không sửa output thật. Không chạy UI E2E: project chưa có frontend/package.json, e2e.config.ts hoặc frontend URL; việc tạo app hoặc gọi AI cho UI test ngoài quyền của phiên. Không chạy train, SAST/pentest hay audit sản phẩm.

Lệnh đã chạy từ gốc project bằng Python bundled; trong ví dụ sau, `python` chỉ cùng executable ghi trong summary/checks:

```powershell
python -B scripts/data/clean_dryad.py --config scripts/data/dryad-config.json --project-root .
python -B -m unittest discover -s scripts/data -p test_clean_dryad.py -v
python -B scripts/data/verify_dryad.py --config scripts/data/dryad-config.json --run-id dryad-8b0f7c218098bfdf --output data/TomatoAI/data/reports/dryad/validation-dryad-8b0f7c218098bfdf.json
```

Log thực: `tests-dryad-8b0f7c218098bfdf.log`, `verify-dryad-8b0f7c218098bfdf.log`, `idempotency-dryad-8b0f7c218098bfdf.log`, `checks-dryad-8b0f7c218098bfdf.json`. Mỗi command/exit code được ghi; không coi ghi nhận kế hoạch là kết quả chạy.

Fingerprint gồm hash raw, reference, config, code/helper và Python version. Các artifact được seal bằng `output-artifacts.json`. Pipeline giữ checkpoint partial nếu lỗi, từ chối overwrite; sửa pipeline/config tạo run mới. Rollback: chọn lại run trước trong registry từ backup có hash; không thay raw. Không xóa run cũ.

Run ban đầu `dryad-07a66a01524acebb` có cùng số lượng và đã qua verifier; giữ nguyên làm lịch sử. Run hiện hành tăng guard XML/đường output raw, có 12 test và seal riêng. Không sửa báo cáo intake hoặc các kết quả PlantVillage/PlantExpertVQA/WUR.

## 7. Đầu ra và trạng thái tổng

Dẫn xuất: `../../processed/dryad/dryad-8b0f7c218098bfdf/` gồm 8 JSONL, manifest.csv/manifest.json và cell-ledger.jsonl. Báo cáo run gồm summary, bảng audit, inventory workbook/sheet, dictionary, transformation log, raw-before/raw-after, unmapped cells, cross-table candidates, review queue, fingerprint, checkpoint và artifact seal.

`../../dataset-registry.json` chỉ cập nhật entry Dryad, bảo toàn các entry khác và flag official_planning_imported=false. Backup registry trước sửa được lưu trong thư mục báo cáo; `registry-update-verification.json` chứng minh các entry khác giữ nguyên. Checkpoint/queue cho phép tiếp tục review nguồn ở phiên sau.

Dataset tiếp theo theo hướng dẫn: **Mendeley**, chỉ xử lý khi có yêu cầu phiên riêng. Dừng tại bàn giao Dryad; chưa nhập PRD/spec/ticket chính thức, làm app hoặc train.
