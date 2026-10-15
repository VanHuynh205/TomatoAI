# PlantVillage — báo cáo làm sạch và checkpoint

Ngày **14/10/2026**, Asia/Bangkok. Đề tài: **Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua**. Chỉ thực hiện Prompt 2 cho PlantVillage; không viết ứng dụng, train, tải dữ liệu, gọi AI API hoặc tiếp nhận draft thành planning chính thức. Các số dưới đây là kết quả pipeline đã chạy trên local, thay cho số khảo sát sơ bộ khi đánh giá readiness; biên bản khảo sát cũ không bị sửa.

**Trạng thái: `cleaned_technical` và `needs_review`.** Có subset **11.411 ảnh / 2.854 component có grouping, ứng viên `ready_for_split` ở mức kỹ thuật**; chưa tạo split, chưa đánh dấu `ready_for_training_subset`, chưa được duyệt benchmark đủ 10 lớp. Không suy đúng nhãn bệnh hoặc chất lượng ngoài vườn từ decode/hash/grouping.

## Artifact hiện hành và môi trường

Run hiện hành: **`pv-d9e4c21eec8e9172`**, fingerprint gắn source hashes + config + SHA256 pipeline + Python/Pillow version. Run trước `pv-018f15e5f3a9b2a1` giữ nguyên, được thay thế vì parser chỉ nhận leaf ID số đã gắn cờ sai các ID prefix của cây khác. Bản sửa giữ ID nhóm dạng chuỗi/số 0 hợp lệ; counts ảnh cà chua không đổi, regression test bổ sung. Không dùng checkpoint cũ làm nguồn metadata issue hiện hành.

| Artifact | Nội dung |
| --- | --- |
| [Pipeline](../../../../../scripts/data/clean_plantvillage.py), [config](../../../../../scripts/data/plantvillage-config.json) | CLI Python, đường dẫn tương đối/config; không hardcode đường dẫn máy trong logic |
| [Test](../../../../../scripts/data/test_clean_plantvillage.py) | CLI/manifest/output tests, fixture tổng hợp chỉ trong thư mục tạm |
| [Bản dẫn xuất](../../processed/plantvillage/pv-d9e4c21eec8e9172/) | 18.146 ảnh sao chép nguyên byte; manifest CSV/JSONL, mapping, group manifest, benchmark-candidates |
| [Summary](pv-d9e4c21eec8e9172/summary.json), [checkpoint](pv-d9e4c21eec8e9172/checkpoint.json) | Counts, môi trường, trạng thái, next action và provenance của run |
| [Raw trước](pv-d9e4c21eec8e9172/raw-before.csv), [raw sau](pv-d9e4c21eec8e9172/raw-after.csv) | Tập path/size/SHA256 toàn bộ file trong source scope, bao gồm archive/metadata |
| [Review queue](pv-d9e4c21eec8e9172/review-queue.json), [alias candidates](pv-d9e4c21eec8e9172/alias-candidates.json) | Bản ghi chưa đủ grouping/ứng viên near; alias Target Spot không tự áp dụng |
| [Exact duplicate groups](pv-d9e4c21eec8e9172/duplicate-groups.csv), [near candidates](pv-d9e4c21eec8e9172/near-candidates.csv) | Exact byte/pixel tách biệt; near chỉ là ứng viên chưa được xác nhận |
| [Group edges](pv-d9e4c21eec8e9172/group-edges.csv), [orphan metadata](pv-d9e4c21eec8e9172/orphan-metadata.csv) | Căn cứ component và các dòng CSV chưa nối được tới ảnh local |
| [Metadata source evidence](metadata-source-evidence.json) | Đối chiếu 9 CSV gốc, CSV filtered và 2 workbook; không tính lại công thức |
| [Output hashes](pv-d9e4c21eec8e9172/output-artifacts.json) | SHA256 của ảnh dẫn xuất và các artifact trong run; kiểm lại khi rerun |
| [Registry](../../dataset-registry.json) | Trạng thái tổng các dataset, không sửa trạng thái bộ chưa làm sạch |

Nguồn local: `data/TomatoAI/data/raw/plantvillage`. Repo nguồn được khai báo tại [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset), local HEAD `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`. README_HF local khai báo **CC BY-SA 3.0**, CITATION.cff ghi bài Mohanty/Hughes/Salathé 2016. Đây là ghi nhận khai báo nguồn local, không xác nhận quyền phân phối từng asset/checkpoint; chưa fetch/clone/đối chiếu remote trong phiên. HEAD không tự chứng minh working tree giống commit; hash snapshot mới là căn cứ byte của nguồn thực dùng.

Python bundled có sẵn **3.12.14**, Pillow **12.3.0**, Windows 11 build 26200; không cài thêm package. Pipeline và test dùng stdlib + Pillow; đọc workbook bổ sung dùng openpyxl **3.1.5** có sẵn (phiên bản ghi trong metadata-source-evidence). Không dùng môi trường `.venv` TomatoAI vì chưa có Pillow. Mỗi lần chỉ giải mã một ảnh; không nạp toàn bộ tensor ảnh vào RAM.

Skill thực áp dụng: **Ponytail, mức full**, đọc `.dsh/skills/ponytail/SKILL.md`: tái sử dụng runtime có sẵn, stdlib CSV/JSON/hash/copy/unittest, không framework hoặc lớp triển khai thừa. Discovery không thấy skill chuyên audit ảnh/preprocessing PlantVillage. Đã đọc `tdd`/`e2e` để đối chiếu phạm vi, không tuyên bố đã chạy hai workflow đó. Primary workflow là CLI data pipeline với kiểm chứng đầu ra, không BMAD build/dev. Không tạo memlog/ticket giả; runtime BMAD đã setup từ phiên trước, chưa dùng để nhập kế hoạch.

## Số lượng trước/sau

Phạm vi hash nguồn loại trừ `.git`, `.cache`, `__pycache__` (tooling/cache); **18.270 file, 298.942.097 byte** trước/sau, tất cả path/size/SHA256 khớp. Bao gồm 18.160 ảnh cà chua và 110 file metadata/tài liệu/archive/khác; không di chuyển, đổi tên, sửa hoặc xóa nguồn. Không giải nén archive trong cleaning này, nhưng byte archive nằm trong kiểm chứng hash.

| Hạng mục disjoint trên 18.160 ảnh nguồn | Số lượng | Xử lý / trạng thái |
| --- | ---: | --- |
| Giữ và `ready_for_split` kỹ thuật | 11.411 | Có leaf grouping đối chiếu CSV + hai map, không flag đang chặn component |
| Giữ và `needs_review` | 6.735 | Chưa đủ bằng chứng nhóm; một số còn near candidate |
| `excluded_exact_duplicate` | 14 | Trùng byte cùng nhãn; không tạo bản copy dư, giữ record và duplicate_of; raw vẫn nguyên |
| `excluded_invalid` | 0 | Không tìm thấy lỗi giải mã/format trong lần kiểm tra đầy đủ này |
| **Tổng record / tổng copy dẫn xuất** | **18.160 / 18.146** | **11.411 + 6.735 + 14 = 18.160** |

18.160/18.160 file giải mã được: tất cả JPEG, 256×256, RGB/3 kênh; không EXIF key trong lần đọc bằng Pillow. File `.jpeg` đặc biệt hợp lệ, không loại vì đuôi khác `.JPG`. Không có file ảnh 0 byte hoặc mismatch format/đuôi được phát hiện. Không có lớp cây khác trong vùng ảnh local hiện có; pipeline chỉ chọn thư mục Tomato, không xóa cây khác nếu xuất hiện ở raw.

| Nhãn gốc rút gọn | Trước | Ready for split kỹ thuật | Giữ cần review | Loại copy trùng |
| --- | ---: | ---: | ---: | ---: |
| Bacterial spot | 2.127 | 2.127 | 0 | 0 |
| Early blight | 1.000 | 999 | 1 | 0 |
| Late blight | 1.909 | 920 | 981 | 8 |
| Leaf mold | 952 | 952 | 0 | 0 |
| Septoria | 1.771 | 1.000 | 771 | 0 |
| Spider mites | 1.676 | 1.676 | 0 | 0 |
| Target spot | 1.404 | 0 | 1.404 | 0 |
| Yellow leaf curl virus | 5.357 | 2.738 | 2.619 | 0 |
| Mosaic virus | 373 | 0 | 373 | 0 |
| Healthy | 1.591 | 999 | 586 | 6 |
| **Tổng** | **18.160** | **11.411** | **6.735** | **14** |

Các flag **có thể chồng nhau**, không cộng với các trạng thái disjoint: `leaf_group_missing` trên **6.749 record nguồn**, gồm 14 record đã loại copy trùng; `cross_component_near_candidate` trên **12 record**, đều thuộc Late blight và đã thiếu grouping. Review queue có 6.749 record có flag, gồm cả 14 excluded; không đồng nghĩa có 6.749 copy cần review.

## Grouping, trùng và phần chưa xác minh

- Hai JSON map cùng nội dung đã đối chiếu. 9 CSV filtered cà chua có **12.820 dòng** hợp lệ; metadata schema issues hiện hành **0**. Numeric ID chuẩn hóa biểu diễn `1.0` → `1` trong dẫn xuất, giữ namespace class và provenance tới raw. ID có prefix/số 0 không bị coi là missing chỉ vì không phải số dương.
- **11.411 ảnh** có nhóm khớp cả hai JSON và CSV; **2.854 leaf group** đã chứng minh bằng metadata, không phải tổng lá thật của dataset. Ngoài subset này không tạo singleton leaf ID từ UUID/tên ảnh. Tổng **9.589 split component** gồm cả ảnh chưa có leaf group; component kỹ thuật không phải xác nhận nhóm lá sinh học.
- **14 nhóm trùng byte**, mỗi nhóm 2 ảnh cùng nhãn; decoded-pixel hash cũng cho đúng 14 nhóm đó. Không tìm thấy xung đột nhãn trong các exact duplicate/source-variant component hiện có. Canonical chọn theo có group trước rồi đường dẫn thứ tự từ điển; excluded record trỏ đúng `duplicate_of`, không xóa dữ liệu nguồn. Không dùng near hash để loại ảnh.
- Near heuristic so sánh 64 bit từ luma tại 9×8 tọa độ trên pixel gốc; **không resize/crop/làm nét hoặc xuất ảnh biến đổi**. Khoảng Hamming ≤4 là cấu hình screening chưa kiểm chứng, không phải ngưỡng duplicate đã được chuyên gia duyệt. Quét 18.160 ảnh, không chạm cap 200.000 pair; **10 pair / 12 ảnh** qua component khác cần review. Các pair cùng component đã có căn cứ được bỏ khỏi near queue vì đã bị ràng buộc cùng tập. Phương pháp lấy mẫu này có thể bỏ sót crop/rotation/near duplicate khác; không tuyên bố đã tìm mọi ảnh gần trùng.
- Local chỉ có biến thể `color`. Không tải/tạo grayscale hoặc segmented. Logic component/test có xét UUID nguồn giữa biến thể nếu đã tồn tại và exact hashes; UUID không được dùng làm leaf ID. Test fixture grayscale không phải dataset dẫn xuất/train.
- CSV gốc và cached values của **2 workbook × 9 sheet** đều khớp CSV filtered. Đã đọc **25.564 ô công thức** ở hai workbook dưới dạng chuỗi và cached value, không thực thi/tính lại; không missing cached leaf value trong đối chiếu. openpyxl báo unsupported extension khi đọc workbook đầu; chỉ đọc, không save nên không loại extension khỏi raw. SHA256 workbook sau chạy vẫn khớp trước.
- Có **1.409 dòng CSV chưa nối** qua exact lookup: Target 1.404, Bacterial 1, Early 1, Healthy 1, Yellow curl 2. Đây là metadata orphan theo phép nối hiện hành, không xóa hoặc kết luận ảnh nguồn mất/hỏng. Target có **1.404 alias candidate / 351 nhóm ứng viên** nhưng chưa applied.

| Queue / checkpoint | Bằng chứng đã có | Quyết định còn thiếu / cách tiếp tục |
| --- | --- | --- |
| Target Spot — 1.404 ảnh | Ảnh `Com.G_TgS_FL`, CSV/map/workbook `Com.G_FL`; alias candidates có từng source row | Cần xác nhận liên kết filename/nhóm bằng nguồn tác giả hoặc review có căn cứ. Numeric one-to-one chưa được coi là chứng minh leaf identity; không auto-replace. |
| Early blight — 1 ảnh | Raw `RS_Erly.B 6341.JPG`; CSV filtered và CSV gốc dòng 10 có tên thêm `(Kelsee Baranowski's conflicted copy 2015-10-06)`, leaf value `2.0` | Ứng viên alias đặc biệt đã ghi metadata-source-evidence, chưa tự gán nhóm 2. Cần quyết định review và ghi lý do/bằng chứng trước áp dụng dẫn xuất mới. |
| Healthy/Late/Septoria/Yellow curl còn thiếu group | Prefix GH_HL/GHLB/JR/Keller/UF.GRC... không có exact metadata tương ứng | Giữ pending; không suy leaf ID từ chữ Leaf/số trong tên ảnh. Phục hồi nguồn/annotation có bằng chứng hoặc loại khỏi benchmark có kiểm soát ở phiên được duyệt. |
| Mosaic — 373 ảnh | Không có CSV/sheet nhóm cho lớp này trong bộ metadata đã đọc | Chưa có benchmark 10 lớp được kiểm soát grouping. Cần nguồn/group evidence hoặc quyết định phạm vi benchmark, không tự giả định từng ảnh độc lập. |
| Near — 10 pair | Pixel hash khác, Hamming candidate và đường dẫn gốc đầy đủ | So sánh original, ghi same/different/uncertain và căn cứ; chỉ sau review mới cập nhật grouping/quarantine. Không xóa theo radius. |
| Đúng nhãn và license | Nhãn thư mục/README local giữ nguyên | Nhãn bệnh chưa được chuyên gia xác nhận; phân biệt healthy và spider mites (tác nhân gây hại) với bệnh. Tên sheet `Target Spot Bacteria` không tự là taxonomy tác nhân đã duyệt. Quyền phân phối cần review riêng. |

## Schema và transformation log

Manifest CSV/JSONL **30 field**, một record trên mỗi file ảnh nguồn, không mất record khi exclude. CSV biểu diễn list/object bằng JSON, unavailable scalar là chuỗi rỗng; JSONL giữ type số/bool/list. `benchmark-candidates.csv` là danh sách kỹ thuật, không phải split hoặc training manifest được duyệt.

| Field | Type / đơn vị / nghĩa |
| --- | --- |
| schema_version, record_id | String; schema `1.0`, ID `pv:<relative source_file>` ổn định theo file, không phải leaf ground truth |
| source_file, source_record, source_uuid | Path tương đối từ source root; filename gốc; prefix UUID nếu có, không tự là nhóm lá |
| label_original, status_code, variant | Nhãn thư mục nguyên bản; mã đề xuất từ planning giữ nguyên; color/grayscale/segmented thực có |
| bytes, sha256 | Số byte nguồn và SHA256 toàn file; không lấy hash decoded thay hash nguồn |
| decode_ok, decode_error, image_format | Bool và error string; format do decoder nhận, không dựa riêng extension |
| width, height, mode, channels | Pixel/int hoặc rỗng khi lỗi; mode và số kênh; không đơn vị vật lý lá |
| exif_keys | List mã EXIF key, không giữ nội dung EXIF trong manifest |
| pixel_sha256, near_hash | Hash pixel gồm mode/kích thước và pixel bytes; 64-bit sample signature chỉ screening |
| lookup_key, group_method | NFC/casefold/stem ở lớp dẫn xuất; method lookup hoặc unresolved; raw filename không đổi |
| leaf_group_id, group_evidence | Class namespace + ID chỉ khi metadata đồng thuận; list source_file + JSON key hoặc số dòng CSV bắt đầu từ 1 |
| split_component_id | Ràng buộc không tách qua split theo leaf/exact/UUID variant; không thay leaf ID còn thiếu |
| flags, record_status | List flag có thể chồng; enum ready_for_split / needs_review / excluded_exact_duplicate / excluded_invalid |
| duplicate_of, processed_file | Canonical record nguồn khi loại copy trùng; relative path trong versioned processed run hoặc rỗng |
| ready_for_training | Bool, **false cho mọi record trong lượt này** |

Các bước đã thực hiện: snapshot/hash → parse metadata → chọn chỉ Tomato → decode/inspect → exact hashes → component edges → near screening → xác định trạng thái → copy nguyên byte non-excluded → manifests/queues → full raw rehash → seal output hashes. Chỉ khóa canonical ở **trùng byte cùng nhãn**; decoded-pixel identical chỉ tạo constraint/evidence, không tự xóa ảnh có file bytes khác.

Không resize/crop/augmentation, cân bằng lớp, impute, scale, fit statistics/classifier, split train/val/test hoặc tính threshold từ test. Không ghép PlantExpert/CSV canh tác vào dataset ảnh. Mọi mapping tên Việt/tri thức vẫn thuộc bước review khác, không được gọi đã kiểm duyệt ở đây.

## Lệnh, test và rerun

Chạy từ project root bằng Python bundled có sẵn:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'scripts\data\clean_plantvillage.py' --config 'scripts\data\plantvillage-config.json' --project-root 'C:\Users\admin\Downloads\DACN_CayCaChua'
$env:PLANTVILLAGE_REPORT = 'C:\Users\admin\Downloads\DACN_CayCaChua\data\TomatoAI\data\reports\plantvillage\pv-d9e4c21eec8e9172'
$env:PLANTVILLAGE_PROJECT_ROOT = 'C:\Users\admin\Downloads\DACN_CayCaChua'
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'scripts\data\test_clean_plantvillage.py'
```

**Kết quả đã chạy: 16/16 test đạt, 0 skip, exit code 0**; rerun cũng exit code 0 và trả `reused_verified` cho run hiện hành. Bằng chứng tại [verification-tests-final.txt](verification-tests-final.txt), [idempotency-final.txt](idempotency-final.txt); log chạy bản sửa tại [cleaning-run-v2.txt](cleaning-run-v2.txt). Test gồm 11 tình huống tổng hợp qua CLI và 5 kiểm tra trên output thật: schema/count/provenance, full raw before/after hashes, mọi derived copy nguyên byte, component/benchmark exclusion, queue có endpoint thật. Không coi fixture synthetic là dữ liệu thực nghiệm.

Rerun cùng nguồn/config/code/environment trả `reused_verified`, kiểm tập artifact và SHA256, không tạo copy mới hoặc ghi đè report đã seal. Sửa code/config/source sẽ có fingerprint/run folder mới. Checkpoint chưa hoàn tất không bị ghi đè; CLI từ chối và cho phép `--run-tag <slug>` ở lần thử mới. Không có cờ overwrite/clean/delete.

Đã đọc skill e2e theo AGENTS: không có `e2e.config.ts/mts` hoặc frontend URL cho pipeline, chưa có ứng dụng thuộc phạm vi; **không chạy npx e2e hoặc tạo frontend/config UI**. Kiểm chứng user flow CLI bằng unittest nêu trên. Không dùng AI-driven runner/API; không SAST/pentest/training metric.

## Handoff

Đã lưu checkpoint cho phần chưa giải quyết, không tự duyệt alias/nhãn hoặc thay scope 10 lớp. Cần review grouping và các pair trước khi chốt benchmark/split, đồng thời kiểm tra domain/license riêng; “parse sạch” không đồng nghĩa đủ để train hay tư vấn.

Dataset nên xử lý tiếp theo: **PlantExpertVQA-tomato** bằng Prompt 2 riêng khi người dùng yêu cầu. Sau báo cáo cleaning và registry đủ bằng chứng mới dùng Prompt 3 để cập nhật/tích hợp kế hoạch chính thức. Phiên này dừng sau bàn giao PlantVillage.
