# Audit dữ liệu — khảo sát chỉ đọc

**Cập nhật Setup 13/10/2026:** tên đã chốt “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”; phạm vi nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50. Không tối ưu canh tác; WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung. Runtime đã setup; tài liệu vẫn là draft chưa tiếp nhận chính thức, xem [README](README.md) và [setup-report](setup-report.md). Kết quả khảo sát dưới đây giữ nguyên theo thời điểm ban đầu; setup không làm mới số liệu hoặc làm sạch dữ liệu.

Ngày 13/10/2026. Không sửa raw; không tạo split; không hash/giải mã toàn bộ ảnh. Phân biệt kiểm kê file với đánh giá đúng nhãn.

## Vị trí và cấu trúc đã khảo sát

Đường dẫn người dùng: `C:/Users/admin/Downloads/DACN_CayCaChua/data/TomatoAI` truy cập được. Dataset thực tế nằm sâu hơn tại `data/raw/` bên trong đường dẫn đó.

| Đường dẫn tương đối từ TomatoAI | Nội dung local |
| --- | --- |
| `data/raw/plantvillage/raw/color/Tomato___*/` | 10 thư mục lớp, 18.160 file ảnh |
| `data/raw/plantvillage/leaf-map.json` | Map tên nguồn → danh sách class:::leaf_id; 40.328 khóa |
| `data/raw/plantvillage/leaf_grouping/leaf-map.json` | Bản map thứ hai, cũng 40.328 khóa; chưa so toàn bộ giá trị/hash hai map |
| `data/raw/plantvillage/leaf_grouping/filtered_leafmaps/` | 9 CSV cà chua; thiếu CSV mosaic virus |
| `data/raw/plantvillage/leaf_grouping/leaf_maps/` | CSV tên nguồn, có dữ liệu cho nhiều cây |
| `data/raw/plantexpert/disease_kb/tomato/` | 17 JSON thẻ tri thức |
| `data/raw/plantexpert/README.md` | Dataset card local, không phải VQA parquet thực tế |

Chỉ có thư mục biến thể **color** local; không có grayscale/segmented trong `plantvillage/raw`. README upstream mô tả cả ba, không đồng nghĩa đã tải cả ba. Không thấy ảnh loài khác trong local color. Không nạp `.venv`, `.git` hoặc toàn bộ nội dung dataset vào context.

Kiểm kê file PlantVillage loại trừ `.git`/`.cache`: **18.270 file** = 18.159 `.JPG`, 1 `.jpeg`, 64 CSV, 36 XLSX, 2 JSON, 2 Markdown, 2 Python có sẵn trong dataset, 2 `.DS_Store`, 1 ZIP, 1 CFF. PlantExpert loại trừ cache: **18 file** = 17 JSON + README. Không thực thi script dataset, mở XLSX hoặc giải nén ZIP. Các file có sẵn không phải code triển khai được tạo trong lượt này.

## Lớp, mã chuẩn và ánh xạ đề xuất

Số ảnh được đếm thực tế bằng file enumeration; chưa chứng minh mỗi file là một ảnh độc lập/đúng nhãn. Tất cả 18.160 file ảnh không có file 0 byte. Tên VI và mã chuẩn bên dưới là **đề xuất cần kiểm duyệt thuật ngữ**; ID gốc không bị sửa. Thứ tự output model tương lai phải ghi rõ trong manifest, không lấy thứ tự thư mục làm hợp đồng ngầm.

| Nhãn PlantVillage gốc | Ảnh | Mã chuẩn đề xuất | Tên VI đề xuất / loại | Thẻ PlantExpert liên quan |
| --- | ---: | --- | --- | --- |
| `Tomato___Bacterial_spot` | 2.127 | `TOM_BACTERIAL_SPOT` | Đốm vi khuẩn / bệnh vi khuẩn | `bacterial_spot.json` → `tomato.disease_bacterial.bacterial_spot` |
| `Tomato___Early_blight` | 1.000 | `TOM_EARLY_BLIGHT` | Đốm vòng (early blight) / bệnh nấm | `early_blight.json` → `tomato.disease_fungal.early_blight` |
| `Tomato___Late_blight` | 1.909 | `TOM_LATE_BLIGHT` | Mốc sương (late blight) / bệnh do oomycete | `late_blight.json` → `tomato.disease_fungal.late_blight` (ID gốc bất nhất) |
| `Tomato___Leaf_Mold` | 952 | `TOM_LEAF_MOLD` | Mốc lá / bệnh nấm | `leaf_mold.json` → `tomato.disease_fungal.leaf_mold` |
| `Tomato___Septoria_leaf_spot` | 1.771 | `TOM_SEPTORIA` | Đốm lá Septoria / bệnh nấm | `septoria_leaf_spot.json` → `tomato.disease_fungal.septoria_leaf_spot` |
| `Tomato___Spider_mites Two-spotted_spider_mite` | 1.676 | `TOM_SPIDER_MITE` | Nhện hai chấm gây hại / tác nhân gây hại, không phải bệnh nhiễm | `spider_mites.json` → `tomato.pest_mite.spider_mites` |
| `Tomato___Target_Spot` | 1.404 | `TOM_TARGET_SPOT` | Đốm bia (target spot) / bệnh nấm | `target_spot.json` → `tomato.disease_fungal.target_spot` |
| `Tomato___Tomato_mosaic_virus` | 373 | `TOM_MOSAIC` | Khảm do virus / bệnh virus | `mosaic_virus.json` → `tomato.disease_viral.mosaic_virus` |
| `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | 5.357 | `TOM_YELLOW_CURL` | Vàng xoăn lá do virus / bệnh virus | `yellow_leaf_curl_virus.json` → `tomato.disease_viral.yellow_leaf_curl_virus` |
| `Tomato___healthy` | 1.591 | `TOM_HEALTHY` | Lá khỏe theo lớp dữ liệu / healthy | `healthy.json` → `tomato.healthy.healthy` |
| **Tổng** | **18.160** | | | |

Không có lớp ảnh nào thiếu thẻ tương ứng ở mức tên/chủ đề (10/10). Điều này **không** có nghĩa 10 thẻ đã đầy đủ, đúng chuyên môn hoặc sẵn sàng hiển thị. Lớp lớn nhất/nhỏ nhất chênh khoảng 14,36 lần; không báo accuracy đơn lẻ làm bằng chứng.

7 thẻ không có lớp ảnh local tương ứng: `cercospora_leaf_spot`, `flea_beetle_injury`, `fusarium_wilt`, `leaf_curl_virus`, `leaf_miner`, `pest_damage`, `yellowing_symptom`. Có thể làm nội dung tham khảo sau kiểm duyệt, không thêm vào output CNN hoặc nhận diện các trạng thái đó. `leaf_curl_virus` và `yellow_leaf_curl_virus` phải được phân biệt, không hợp nhất bằng keyword.

## Grouping đã kiểm tra sơ bộ

CSV có hai cột `File Name`, `Leaf #`, ví dụ healthy `RS_HL 0003.JPG` → `1.0`. Map có khóa dạng `com.g_fl 8310` → `Tomato___Target_Spot:::243.0`. Đây là nhóm lá, không phải số thứ tự ảnh. Namespace class/source phải được giữ; `1.0` của hai lớp không tự là cùng lá.

Phép khảo sát: tách basename sau `___`, chuyển chữ thường, lookup map ở root PlantVillage, lọc ID đúng class. Chưa áp dụng alias, không sửa tên. “Chưa khớp” bên dưới chỉ nghĩa phép lookup này thất bại, **không kết luận metadata không thể phục hồi**.

| Lớp rút gọn | Ảnh | Khớp duy nhất | Chưa khớp | Nhóm đã khớp | Dòng CSV filtered / nhóm CSV |
| --- | ---: | ---: | ---: | ---: | --- |
| Bacterial spot | 2.127 | 2.127 | 0 | 532 | 2.128 / 532 |
| Early blight | 1.000 | 999 | 1 | 250 | 1.000 / 250 |
| Healthy | 1.591 | 999 | 592 | 250 | 1.000 / 250 |
| Late blight | 1.909 | 920 | 989 | 230 | 920 / 230 |
| Leaf mold | 952 | 952 | 0 | 238 | 952 / 238 |
| Septoria | 1.771 | 1.000 | 771 | 250 | 1.000 / 250 |
| Spider mites | 1.676 | 1.676 | 0 | 419 | 1.676 / 419 |
| Target spot | 1.404 | 0 | 1.404 | 0 | 1.404 / 351 |
| Mosaic virus | 373 | 0 | 373 | 0 | Không có CSV filtered |
| Yellow curl | 5.357 | 2.738 | 2.619 | 685 | 2.740 / 685 |
| **Tổng** | **18.160** | **11.411** | **6.749** | **2.854** | Không coi tổng nhóm này là tổng lá thực |

Không có trường hợp nhiều ID cùng class trong các lookup đã khớp. Chưa khảo sát đầy đủ ambiguity khác class hoặc alias. Target Spot có ảnh `Com.G_TgS_FL ...` trong khi CSV/map dùng `Com.G_FL ...`; đây là ứng viên chuẩn hóa tên **cần chứng minh**, không áp dụng replace hàng loạt. Chênh dòng CSV–ảnh và các prefix healthy/late/septoria/YLCV cần đối chiếu. Mosaic chưa có grouping; không được giả sử mỗi ảnh là một lá.

**Công việc sẽ làm:** đối chiếu root map và leaf_grouping map, CSV/source, tên có prefix/suffix khác; lập bảng alias có provenance và kiểm duyệt; tính hash và near-duplicate; gom connected component theo cùng lá/biến thể/trùng rồi split. Trường hợp grouping không chứng minh được: phục hồi thủ công có bằng chứng hoặc loại khỏi benchmark kiểm soát và báo số loại/mất cân bằng. Không random split các ảnh chưa có group để đạt số lượng.

## Định dạng và mẫu đại diện

Giải mã bằng thư viện hệ thống một ảnh đầu tiên theo thứ tự tên của mỗi lớp và ảnh `.jpeg` đặc biệt: **11/11 mẫu giải mã được, đều 256×256**. Đây không phải kiểm tra toàn bộ ảnh. Đã xem trực quan hai mẫu healthy và spider mites: lá rời trên nền đơn giản; chưa xác minh độc lập cây/tác nhân của mẫu.

Ví dụ đường dẫn tương đối dưới `plantvillage/raw/color/`:

- `Tomato___healthy/000146ff-92a4-4db6-90ad-8fce2ae4fddd___GH_HL Leaf 259.1.JPG`.
- `Tomato___Spider_mites Two-spotted_spider_mite/002835d1-c18e-4471-aa6e-8d8c29585e9b___Com.G_SpM_FL 8584.JPG`.
- File khác đuôi trong Late blight: `d0badc95-d04c-457b-8db8-aa6e198f4bd6___GHLB Leaf 10 Day 6.jpeg`, 12.412 byte. Không có file khác cùng suffix trong thư mục theo phép kiểm tra tên. Đuôi khác **không chứng minh lỗi hoặc trùng**; cần provenance/hash/near-duplicate ở bước sau.

## PlantExpert: schema và nội dung thực tế

Cả 17 JSON parse được, có 16 field top-level: `schema_version`, `disease_id`, `aliases`, `crop`, `condition`, `issue_type`, `transmission`, `environmental_risk`, `severity_rubric`, `symptoms`, `lookalikes`, `management`, `qa_seeds`, `data_requirements`, `provenance`.

`crop` gồm common/scientific/family; `condition` gồm tên và taxonomy tác nhân; `symptoms` chia lá/thân/quả/rễ/toàn cây; `management` chia cultural/biological/chemical/notes; `qa_seeds` là mẫu câu hỏi, không phải tập tư vấn supervised có cặp đầu vào–đầu ra và outcome. `severity_rubric` là mô tả văn bản, không phải nhãn mức độ gắn vào 18.160 ảnh. Không có VQA CSV/parquet hoặc ảnh PlantExpert trong bản tải local đã khảo sát.

Mẫu EN đã đọc (trích ngắn, không là hướng dẫn đã duyệt): healthy, `symptoms.leaves[0]`: “Uniformly green color, consistent with the cultivar.”; late blight, `management.cultural[2]`: “Avoid overhead irrigation; use drip irrigation to keep foliage dry.”; spider mites, `symptoms.leaves[0]`: “Fine, pale yellow or white stippling (tiny dots) on the upper leaf surface.”

### Bất nhất/thiếu đã quan sát

- **24 liên kết `lookalikes.condition_id` không khớp chính xác** bất kỳ `disease_id` nào trong 17 thẻ. Ví dụ healthy dùng `tomato.fungal.early_blight` nhưng thẻ thật là `tomato.disease_fungal.early_blight`; spider mites tham chiếu `tomato.pest_damage.leaf_miner` nhưng ID thật là `tomato.pest_insect.leaf_miner`. Có chủ đề tương ứng không đồng nghĩa ID hợp lệ. Cần resolver alias kiểm duyệt, không bỏ link âm thầm.
- Late blight ID/issue_type ghi `disease_fungal`, pathogen.type ghi `disease_oomycete`; mapping dẫn xuất phân biệt oomycete, giữ raw để truy vết. Nguồn UMN hỗ trợ phân loại này, xem research.
- `flea_beetle_injury` và `pest_damage` có `issue_type=unknown`; không lấy trực tiếp làm taxonomy sản phẩm.
- `mosaic_virus` có alias cả ToMV và TMV; không coi đó là bằng chứng hai virus đồng nhất. Chỉ hiển thị tên lớp tổng quát và chờ review chuyên môn.
- `provenance.sources` phần lớn là tên nhóm tài liệu/compendium, thiếu URL/trang/trích dẫn theo claim. `created_by/reviewed_by` là mô tả vai trò; chưa xác minh danh tính/chất lượng review. Không gọi kho local “đã được chuyên gia Việt Nam duyệt”.
- `data_requirements.min_resolution_px` của healthy là 512, late blight/spider mites là 1024; mẫu ảnh PlantVillage là 256. Đây là hướng dẫn thu ảnh trong KB, không phải metadata ảnh local; cần không ép một yêu cầu KB thành tiêu chí loại toàn bộ ảnh training.
- Lời khuyên tưới của thẻ nhện và late blight có điều kiện khác nhau. Không ghép hai hướng dẫn thành một phác đồ từ top-k.

## Provenance và kiểm tra chưa làm

PlantVillage clone local HEAD `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`; chưa chứng minh raw sạch hoặc giống hoàn toàn commit. README_HF local khai báo CC BY-SA 3.0, khớp card upstream đã mở. PlantExpert README local khai báo CC BY 4.0; metadata cache README ghi revision `e21eacc1eff9e1db38966d78d0e8af2f22706313`, không phải checksum toàn bản tải. Trang PlantExpert online không mở được qua web tool trong lượt này; chưa đối chiếu remote từng file/giấy phép revision.

Chưa làm: hash toàn ảnh/KB, kiểm tra near-duplicate, corruption toàn ảnh, EXIF/mode toàn bộ, đúng nhãn bởi chuyên gia, mapping đầy đủ tên–lá, overlap giữa nguồn, nội dung ZIP/XLSX, kiểm tra giấy phép từng thành phần nguồn, ảnh vườn độc lập. Dataset card nói 54.306 ảnh toàn nguồn và 765.186 QA toàn PlantExpert; **không sử dụng các số này làm số dữ liệu local**. Chi tiết điều kiện pháp lý là checkpoint trước phân phối, không là xác nhận pháp lý.
