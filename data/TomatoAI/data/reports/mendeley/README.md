# Báo cáo làm sạch kỹ thuật Mendeley

Ngày thực hiện: 2026-10-14, Asia/Bangkok. Run hiện hành: **mendeley-61d459ec1f46cef3**.

Đề tài: **Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua**. Phiên này chỉ thực hiện Prompt 2 cho Mendeley. Bộ canh tác này giữ trạng thái **research_only**, ngoài phụ thuộc MVP nhận diện trạng thái lá, hướng dẫn chăm sóc, Windows desktop offline tiếng Việt. Không tạo ứng dụng, huấn luyện, tải thêm dataset/weights, gọi API AI/dịch thuật hoặc mở rộng sang tối ưu canh tác.

## 1. Nguồn và bảo toàn

Nguồn bất biến: `../../raw/cultivation/mendeley_irrigation_33cngpcrmx_v3/`.

| File nguồn | Byte | Kiểu | Record thực đếm lại |
| --- | ---: | --- | ---: |
| tomato irrigation dataset.csv | 265.150 | UTF-8, CSV 14 cột | 3.000 |
| tomato_water_sensor_data.json | 555.868 | UTF-8, JSON array, 37 key/record | 393 |
| Tổng | 821.018 | Hai bảng riêng | 3.393 |

Không có archive/README trong thư mục raw của bộ này. Metadata tham chiếu nằm trong `../../cultivation_metadata/`. Hai file raw khớp byte/SHA-256 manifest tiếp nhận và digest file nguồn đã lưu. Hash trước/sau pipeline, verifier và bàn giao đều giữ nguyên. Không đổi tên, di chuyển hoặc ghi lại raw.

Nguồn: Rohit Kumar Kasera và Tapodhir Acharjee (2026), **Dataset on irrigation for Tomato**, Mendeley Data, version 3, [DOI 10.17632/33cngpcrmx.3](https://data.mendeley.com/datasets/33cngpcrmx/3). Metadata HTML tiếp nhận ghi datePublished **2026-07-01T18:23:54.298Z**, giấy phép **CC BY 4.0**. Phải giữ công tác giả, DOI/version, license và mô tả thay đổi khi phân phối dẫn xuất. File-level created dates trong metadata khác nhau; không coi chúng là ngày đo. Đây là đối chiếu hồ sơ nguồn local, không tuyên bố đã cập nhật toàn bộ metadata từ mạng trong phiên.

Mô tả nguồn nói dữ liệu đến từ cảm biến và nguồn khí tượng; CSV đã trải qua preprocessing/normalization, JSON là dữ liệu thu khi thử hệ tưới. Đây là mô tả của tác giả, không đủ để chứng minh lineage nối từng record CSV–JSON, độ chính xác cảm biến hoặc hiệu quả tưới tối ưu. Pipeline của dự án không gọi những API khí tượng được nhắc trong mô tả đó. Bằng chứng: `mendeley-source-v3.html`, `mendeley-files-v3.json` và README tiếp nhận, giữ nguyên.

## 2. Workflow, implementation và môi trường

Skill thực áp dụng:

- **migration**, bản local `C:/Users/admin/.agents/skills/migration/SKILL.md`: xác định hai reader CSV/JSON, giữ nguồn cũ, tạo phiên bản dẫn xuất riêng, kiểm chứng bảo toàn, retry idempotent và rollback qua registry backup. Không thực hiện contraction hoặc xóa raw.
- **Ponytail full**, bản project `.dsh/skills/ponytail/SKILL.md`: tái sử dụng hash/snapshot/CSV/JSON/artifact helpers, dùng stdlib, không thêm tầng/dependency ngoài nhu cầu.

Đã kiểm tra catalog/registry và các skill project theo phạm vi. Không chọn được skill chuyên dụng cho Mendeley/Python preprocessing; fallback là pipeline Python minh bạch. Skill Spreadsheets có trong catalog nhưng không dùng workflow authoring/recalculate workbook. Skill e2e đã kiểm tra; không có app/config/URL để chạy UI flow. Không gọi BMAD build/dev và không gắn tên workflow BMAD cho script dữ liệu tự viết. Chưa nhập planning draft thành PRD/spec/ticket chính thức.

File mới: `scripts/data/clean_mendeley.py`, `mendeley-config.json`, `test_clean_mendeley.py`, `verify_mendeley.py`. Helper được import từ `clean_plantexpert.py` và numeric lexeme validation từ `clean_dryad.py`; các script cũ không thay đổi. Fingerprint ghi cả hash helper. Config lưu header/key thực đã đọc, đường dẫn tương đối, giới hạn file/record, policy missing và timestamp. Không hardcode đường dẫn máy trong logic.

Môi trường thực chạy: **Python 3.12.14**, Windows 11 build 26200, runtime bundled. Pipeline/verifier dùng stdlib `csv`, `json`, `Decimal`, `datetime`, `unicodedata`, `hashlib`, `pathlib`; không cài dependency/GPU stack. Mỗi file tối đa 10 MB, tối đa 100.000 record theo config; JSON/record envelopes được giữ trong RAM cho bộ local nhỏ hiện có. Nếu nguồn lớn hơn giới hạn, cần pipeline streaming riêng được kiểm chứng; không nâng giới hạn để bỏ qua lỗi.

## 3. Kết quả trước/sau và reconciliation

| Bảng | Nguồn | Retained | Excluded | Quarantine kỹ thuật | Needs review retained |
| --- | ---: | ---: | ---: | ---: | ---: |
| CSV | 3.000 | 3.000 | 0 | 0 | 3.000 |
| JSON | 393 | 393 | 0 | 0 | 393 |
| Tổng | 3.393 | 3.393 | 0 | 0 | 3.393 |

Needs_review chồng lên retained, không cộng thêm thành số mẫu. Hai bảng không được nối/ghép; tổng 3.393 là số record từ hai nguồn, **không phải số thí nghiệm độc lập**.

- CSV: 39.000 field số và 3.000 category; JSON: 14.148 field số và 393 timestamp. Tổng **56.541 giá trị trường** được đối chiếu độc lập.
- Không có missing trong body theo policy/schema hiện tại; không có field-count/type/key-schema lỗi ở nguồn thật. Không suy diễn thành không có đo đạc bị thiếu ngoài file.
- **1.535 ô số 0** được giữ. JSON: waterFlow_rate 386, waterVolume_liter 386, irrigation_needed_value 379, motorValue 379, dataSpeedRate 5. Không biến 0 thành missing hoặc xóa vì actuator tắt.
- CSV có 12 nhóm giá trị lặp, 40 record liên quan, surplus 28. JSON có 60 nhóm, 152 record liên quan, surplus 92. Đây là duplicate candidate theo exact field lexemes/kind, không theo ID hàng; **giữ tất cả**. Không coi các nhóm lặp là lỗi thu thập đã xác nhận.
- JSON có **30 timestamp khác nhau**, 23 timestamp lặp bao phủ 386 record; không giảm thứ tự timestamp. Khoảng nguồn: **2023-07-27 17:50:10 đến 2023-08-02 19:43:48**, timezone chưa biết. 30 timestamp không xác nhận 30 cây/thiết bị/thí nghiệm.
- Có 16 field JSON hằng trong toàn bộ 393 record. Các field min/max/optimal, vị trí và cropCoffiecient có thể là cấu hình; không được nâng thành ground truth nông học.

103 mục review: 72 nhóm duplicate value, 23 nhóm duplicate timestamp, 2 mục đơn vị/calibration, 2 mục độc lập thí nghiệm và 4 vấn đề riêng về join/target/optimal/timezone. Các mục/flag có thể chồng trên cùng record; không cộng số nhóm thành số record lỗi.

## 4. Schema, dictionary và transformation log

Dẫn xuất gồm hai JSONL envelope riêng và một CSV chuẩn hóa phục vụ đọc bảng CSV. Không tạo bảng join.

Mỗi envelope có schema_version=1.0, record_id, source_file, source_sha256, source_record, source_pointer, fields, errors, flags, status, training_ready và hai key **experimental_group=null**, **verified_cross_dataset_key=null**. ID dựa trên định dạng + vị trí nguồn, không giả làm plant/treatment ID. JSON giữ pointer `/0`…`/392`; CSV giữ line start/end. JSON giữ nguyên text object nguồn qua `raw_json_record` và character span trong text UTF-8-sig đã decode; span là chỉ số ký tự, không phải byte offset. CSV giữ toàn bộ raw_fields.

| Biến đổi | Cách lưu | Giới hạn |
| --- | --- | --- |
| Header CSV | NFC/trim khoảng trắng ngoài; source header/mapping giữ trong dictionary | Chỉ header Temperature có khoảng trắng cuối; không sửa token `_ C` thành đơn vị được đoán |
| Số CSV | decimal_text và raw string | Không float-rounding, đổi đơn vị hoặc scale |
| Số JSON | Parse token số thành marker rồi decimal_text; raw_kind=number, raw lexeme giữ nguyên | Không nhầm numeric token với JSON string; giữ số 0 và precision |
| Category CSV | NFC/trim bản dẫn xuất; raw còn nguyên | Không gộp/sửa stage theo kiến thức tự suy |
| dateTimeAdded | Chuỗi ISO naive dùng `T`, raw vẫn giữ dấu cách | Không gán Z, UTC offset hoặc timezone từ tọa độ |
| Missing/lỗi | Missing null với raw token; lỗi nằm quarantine envelope/pointer | Không impute; nguồn thật có 0 missing/quarantine |

Dictionary đầy đủ **14+37 field** nằm trong `mendeley-61d459ec1f46cef3/data-dictionary.json`. Numeric range, category count, constant-field list, timestamp span và flag nằm trong tables.json; các range chỉ là audit dữ liệu, không phải khoảng khuyến nghị chăm sóc.

| Nhóm field | Bằng chứng đơn vị/ý nghĩa | Trạng thái |
| --- | --- | --- |
| CSV Humidity [%], Nitrogen/Phosphorus [mg/kg] | Header ghi trực tiếp; mô tả nguồn nói NPK sensor mg/kg | Unit header có nguồn; scale sau preprocessing vẫn cần xác minh |
| CSV Temperature [_ C] | Giữ nguyên header bất thường | Không tự sửa thành °C; review notation/scale |
| CSV Soil moisture, ET0/ET, Potassium, GHI, Wind Speed | Không có unit đầy đủ trong header | Chưa gán %, mm/ngày, W/m² hoặc m/s |
| CSV Days of planted | Nhãn có nội dung “days”, không có ngày trồng/record ID | Không đổi thành timestamp hoặc khóa join |
| JSON moisturePercentage, waterVolume_liter, Voltage/Minute/Kbps | Tên key là unit candidate | Chưa chứng minh calibration/định nghĩa, không chuyển đơn vị |
| JSON cropCoffiecient, hauntValue, driperBetweenDistance… | Giữ đúng chính tả key nguồn | Không tự đổi tên hoặc đồng nhất với biến CSV |
| JSON optimal/min/max, motorValue, irrigation_needed_value | Tên cấu hình/action/computed-value candidate | Chưa duyệt là target tối ưu, actual irrigation hoặc hướng dẫn sử dụng |

CSV có 4 category nguyên gốc: Initial Stage 167, Development Stage 129, Mid stage 2.501, Last stage 203. Không thay tên/viết hoa trong raw. Không tự biến stage thành nhãn bệnh, phân loại model hoặc mục tiêu tối ưu.

## 5. Audit công thức và nguy cơ leakage

`numeric-hypotheses.json` ghi diagnostic, tolerance cố định trong config, match/nonmatch record list và max residual. Đây là kiểm tra quan hệ số học của giá trị lưu, **không phải metric mô hình, policy đã xác nhận hoặc kết quả tối ưu**. Không tính target mới, sửa số đo hoặc thay nhãn theo các giả thuyết này.

| Giả thuyết audit | Bảng | Khớp | Không khớp | Tolerance tuyệt đối |
| --- | --- | ---: | ---: | --- |
| ET = ET0 × Kc | CSV | 236 | 2.764 | 1e-6 |
| evapotranspirationValue = reference_eto × cropCoffiecient | JSON | 393 | 0 | 1e-8 |
| irrigation_needed_value = ET − moisturePercentage | JSON | 14 | 379 | 1e-8 |
| irrigation_needed_value = max(0, ET − moisturePercentage) | JSON | 227 | 166 | 1e-8 |
| motorValue = indicator(irrigation_needed_value > 0) | JSON | 393 | 0 | 1e-8 |

Quan hệ ET JSON và motor–needed cho thấy nguy cơ mô hình chỉ học lại giá trị tính từ input/state. Nguồn sinh field, thuật toán/controller, đơn vị và time alignment chưa được xác minh. Giả thuyết clamp không giải thích toàn bộ record; không sửa 166 record cho khớp. ET CSV không khớp phần lớn giả thuyết; không kết luận tác giả sai hoặc sửa số theo JSON. Chưa xác nhận hai trường tên tương tự có cùng biến đổi/đơn vị.

motorValue=1 có 14 record, waterVolume_liter khác 0 có 7 record. Cần xác minh state/time window của log trước khi gọi volume là lượng tưới thực đo tương ứng. Không suy actuator bật đồng nghĩa cây cần mức nước tối ưu. Field optimalTomatoTemperature hằng 28 trong nguồn không trở thành khuyến nghị đã kiểm duyệt cho người dùng Việt Nam.

Không có CSV target năng suất, chi phí, hành động tưới thực đo được xác nhận. JSON không có independent optimality/outcome label đã được dự án thẩm định. Không chọn target/model, random split các dòng liên quan theo thời gian, fit preprocessing trên toàn nguồn hoặc train trong phiên này.

## 6. Review queue, checkpoint và điều kiện tiếp tục

Queue: `mendeley-61d459ec1f46cef3/review-queue.json`; checkpoint: `mendeley-61d459ec1f46cef3/checkpoint.json`. Trạng thái: **cleaned_technical ở cấp parse/provenance**, **needs_review**, **research_only**, training_ready=false, mvp_dependency=false.

| Phần chưa xác minh | Bằng chứng cần | Điều kiện duyệt |
| --- | --- | --- |
| CSV preprocessing và đơn vị/calibration | Dictionary, code xử lý, sensor protocol hoặc xác nhận tác giả | Field/scale/đơn vị có nguồn, không lấy tên key làm xác nhận |
| JSON công thức/controller và optimal/min/max | Code tạo field/quy tắc/nguồn nông học có provenance | Phân biệt observed, computed, config, actuator state và target |
| Dữ liệu lặp/timestamp/độc lập | Device/plant/session ID, log acquisition và timezone | Group/split có bằng chứng; duplicate có lý do xử lý, không xóa tự động |
| CSV–JSON join | Khóa nguồn hoặc lineage crosswalk có thể kiểm chứng | Không nối theo index, tên gần giống, pH/stage hay “days” |
| Tưới/volume và hiệu quả canh tác | Event alignment, hành động và outcome độc lập | Không gọi motor/needed là nhãn tối ưu khi chỉ khớp quan hệ số học |
| Áp dụng hướng dẫn nông nghiệp | Kiểm duyệt domain và điều kiện địa phương | Chỉ tái sử dụng khi được yêu cầu, không thêm tư vấn vào MVP bằng suy đoán |

Không thiếu quyền hoặc dữ liệu để hoàn thành nhánh kỹ thuật hiện tại; các quyết định ngữ nghĩa được giữ pending. Nguồn đủ parse không đồng nghĩa nguồn đáng tin để train hoặc đưa hướng dẫn chăm sóc. Các blocker nghiên cứu canh tác không chặn MVP nhận diện ảnh/kho tri thức nếu vẫn ngoài phụ thuộc MVP.

## 7. Kiểm chứng thực chạy

**8 test unittest PASS**: precision/token number-vs-string, missing-vs-zero/invalid numbers, JSON duplicate-key/nonstandard constant/array/limit, timestamp naive/NFC, preservation/duplicates/no join/idempotency/tamper refusal, schema-blocked file tiếp tục định dạng độc lập, row quarantine không mất nguồn, output raw guard/intake mismatch.

Verifier độc lập **PASS**: 3.393 record, 56.541 giá trị trường, toàn bộ CSV normalized/envelope và JSON raw slices/numeric Decimal/timestamp, manifest CSV/JSON, schema/dictionary coverage, duplicate/timestamp counts, 1.535 số 0, raw/metadata hash và artifact seal. Verifier đọc nguồn với parser CSV/JSON riêng, không dùng hàm normalization của pipeline để tạo expected values.

Chạy lại pipeline **PASS: idempotent_existing_verified**, không nhân đôi output hoặc ghi đè artifact. Tamper/refusal và schema-error tests chỉ dùng fixture tạm, không sửa dữ liệu thật. Số rows parsed/retained/quarantine được kiểm chứng, không lấy số khảo sát cũ thay kết quả chạy.

UI E2E chưa chạy: đã kiểm tra không có `e2e.config.ts`, `frontend/package.json` hoặc frontend URL. Không tạo app/server hoặc gọi model để chạy UI test ngoài quyền. Không chạy train, SAST/pentest hoặc tự nhận audit code sản phẩm.

Các lệnh thực chạy từ project; executable chính xác và exit code có trong checks JSON:

```powershell
python -B scripts/data/clean_mendeley.py --config scripts/data/mendeley-config.json --project-root .
python -B -m unittest discover -s scripts/data -p test_clean_mendeley.py -v
python -B scripts/data/verify_mendeley.py --config scripts/data/mendeley-config.json --run-id mendeley-61d459ec1f46cef3 --output data/TomatoAI/data/reports/mendeley/validation-mendeley-61d459ec1f46cef3.json
```

Lưu `tests-mendeley-61d459ec1f46cef3.log`, `verify-mendeley-61d459ec1f46cef3.log`, `idempotency-mendeley-61d459ec1f46cef3.log`, `checks-mendeley-61d459ec1f46cef3.json`, validation JSON. Tất cả ba exit code bằng 0. Python AST và kiểm tra bàn giao được ghi riêng.

## 8. Đầu ra, rollback và bước sau

`../../processed/mendeley/mendeley-61d459ec1f46cef3/` gồm tables/csv.jsonl, tables/csv-normalized.csv, tables/json.jsonl, manifest.csv/json và hai quarantine JSONL rỗng. Quarantine rỗng chỉ nói không gặp lỗi kỹ thuật theo schema hiện tại, không nghĩa đã duyệt ngữ nghĩa.

Báo cáo run gồm raw-before/raw-after, fingerprint inputs, tables, dictionary, transformation log, review queue, duplicate/timestamp candidates, numeric hypotheses, summary, checkpoint và output-artifacts seal. File raw/error được giữ nếu có; parser lỗi một định dạng sẽ lưu file-level review và tiếp tục bảng độc lập. Partial run không có seal thì không overwrite; dùng checkpoint và tạo version mới sau sửa config/code. Rollback registry từ backup có hash, không rollback bằng sửa raw.

Chỉ cập nhật entry **Mendeley** trong `../../dataset-registry.json`; giữ các entry/history khác và official_planning_imported=false. Registry backup/proof và `handoff-verification.json` lưu tại report parent.

Cả năm bộ theo chuỗi Prompt 2 đã có báo cáo/checkpoint. Bước tiếp theo là review các vấn đề còn mở; **Prompt 3 — Nhập kế hoạch chính thức chỉ khi có yêu cầu riêng**. Không tự chạy Prompt 3, ứng dụng hoặc train sau bàn giao này.
