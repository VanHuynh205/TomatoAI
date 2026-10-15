# Review tích hợp dữ liệu — ir-20261014-v1

Đề tài: **Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua**. Ngày review: **14/10/2026**, Asia/Bangkok. Repository thực tế: `C:/Users/admin/Downloads/DACN_CayCaChua`; dữ liệu thực tế: `data/TomatoAI/data/`. Đây là review dữ liệu và hợp đồng tra cứu, không phải đánh giá mô hình hoặc phê duyệt chuyên môn.

**Kết luận: chưa đủ để phát hành hướng dẫn hoặc huấn luyện.** Có **9/10 liên kết nhãn–card đối chiếu được danh tính**, **1 pending ToMV/TMV**, **0 thiếu card**. “Xác minh mapping” trong báo cáo chỉ có nghĩa Codex đối chiếu khái niệm/tác nhân với nguồn được dẫn; chưa xác minh lại nhãn từng ảnh hoặc có chuyên gia ký duyệt. **17/17 card cần review chuyên môn và tiếng Việt; 0 card và 0 lời khuyên thật được mở hiển thị.** Hợp đồng kỹ thuật đã có 22 test qua, gồm nhánh cho phép bằng fixture tổng hợp trong RAM và nhánh chặn cả 10 lớp thật.

## 1. Phạm vi, workflow và bằng chứng

Workflow chính thực dùng: [bmad-review](C:/Users/admin/.agents/skills/bmad-review/SKILL.md). Đã resolve customization local và dùng ba lens độc lập **adversarial, edge-case, structure**. Skill yêu cầu reviewer song song, nên dùng ba subagent cho ba lens. Đầu vào cố định trong [review-input.md](review-input.md). Không chạy prose vì không yêu cầu copy-edit. Không chạy verification-gap lens của code review vì đầu vào lens là bộ tài liệu/hợp đồng thiết kế; code validator bổ sung được kiểm tra bằng unittest sau đó.

[lens-findings.json](lens-findings.json) giữ riêng **15 adversarial + 6 edge-case**; [structure-findings.md](structure-findings.md) giữ **6 khuyến nghị**. Phát hiện lặp vẫn giữ theo lens. [findings.json](findings.json) là 18 mục triage bổ sung theo yêu cầu người dùng, gồm mức ảnh hưởng, evidence và hành động; không thay thế đầu ra các lens.

Capability bổ trợ thực dùng: [bmad](C:/Users/admin/.agents/skills/bmad/SKILL.md), nhánh status; [Ponytail full](C:/Users/admin/Downloads/DACN_CayCaChua/.dsh/skills/ponytail/SKILL.md), tái sử dụng helper và stdlib cho validator. Không chọn được skill chuyên dụng Python/data-contract trong catalog đã khảo sát; phần này là Python minh bạch, không gắn tên skill giả. Đã đọc skill project `e2e` để kiểm tra khả năng QA: thiếu `e2e.config.ts`, `frontend/package.json`, app URL và ứng dụng hiện thực, nên **không chạy E2E sản phẩm**. Không có UI flow trong phạm vi được phép xây để thay thế các thiếu hụt này.

AGENTS.md và global router áp dụng: giữ raw, không gọi cleaned_technical là training-ready, ưu tiên helper có sẵn. Ba domain/issue/triage document được AGENTS dẫn tới không tồn tại; không tạo issue store thay thế. Repository hiện không có Git metadata; provenance dựa trên hash/file version, không bịa commit/branch.

BMAD status thực chạy, exit 0: **6.13.0-next**, shared scripts current, ba module core-tools/method/toolsmith, `problems=[]`, `current=true`. Bằng chứng [bmad-status.json](bmad-status.json). `_bmad/config.toml` đặt output `_bmad-output`; `_bmad/custom/config.user.toml` đặt initiative `initiative-tomato-desktop`. Registry vẫn `official_planning_imported=false`; không tiếp nhận draft, chạy build/dev hoặc tự nâng cấp. Review này lưu theo quy ước reports dữ liệu hiện có; không tạo bản PRD/architecture song song.

## 2. Kiểm kê hiện hành và tính toàn vẹn

Chọn run theo **dataset-registry.json**, không lấy thư mục đầu tiên hoặc run cũ. Đã hash lại nguồn và toàn bộ artifact có trong seal; đọc/count lại manifest. [integrity-before.json](integrity-before.json), [integrity-after.json](integrity-after.json), [verification.json](verification.json) lưu bằng chứng đối chiếu.

| Dataset | Run registry đang chọn | Thực đếm | Trạng thái / vai trò |
| --- | --- | --- | --- |
| PlantVillage | pv-d9e4c21eec8e9172 | 18.160 record ảnh, 10 lớp; 18.146 copy retained; 14 byte-duplicate excluded; 0 invalid | 11.411 ready_for_split kỹ thuật, 6.735 retained needs_review; chưa có split hoặc mô hình |
| PlantExpertVQA-tomato | pex-b3da04d66a031756 | 17 card/17 manifest record; 17 needs_review; 10 draft links | 17 EN card normalized, nguồn EN giữ nguyên; schema envelope 1.0/content 1.0.0; không phải supervised advisory dataset |
| WUR | wur-7439c4f996527052 | 622.899 manifest record và 622.899 dòng trong 43 CSV | Toàn bộ research_only/needs_review; không phụ thuộc MVP |
| Dryad | dryad-8b0f7c218098bfdf | 508 manifest record; 508 dòng trong 8 JSONL bảng | 253 lần xuất hiện dòng vật lý từ 5 sheet/4 workbook; không phải 508 thí nghiệm độc lập |
| Mendeley | mendeley-61d459ec1f46cef3 | 3.393 manifest record; JSONL riêng 3.000 CSV + 393 JSON | CSV-normalized 3.000 dòng là biểu diễn lại CSV, không cộng thành 6.393 mẫu |

Raw được đối chiếu: PlantVillage **18.270 file**, PlantExpert **39**, WUR **46**, Dryad **5**, Mendeley **2**. Artifact sealed đối chiếu tương ứng: **18.163 / 53 / 100 / 24 / 19**. Baseline PlantVillage có loại `.git`, `.cache`, `__pycache__`; không nhận xét tính bất biến của file ngoài baseline này. KB bao gồm metadata/cache trong scope 39 file theo baseline của pipeline. Tất cả file trong scope **khớp SHA-256/byte baseline**, trước và sau review; đây không chứng minh raw chưa từng thay đổi trước ngày baseline. Reference-inputs và fingerprint-inputs của từng run cũng được kiểm tra, không sửa các input/report nguồn.

| Lớp ảnh | Record nguồn | Ready_for_split kỹ thuật | Retained needs_review | Excluded |
| --- | ---: | ---: | ---: | ---: |
| Bacterial spot | 2.127 | 2.127 | 0 | 0 |
| Early blight | 1.000 | 999 | 1 | 0 |
| Late blight | 1.909 | 920 | 981 | 8 |
| Leaf Mold | 952 | 952 | 0 | 0 |
| Septoria leaf spot | 1.771 | 1.000 | 771 | 0 |
| Spider mites | 1.676 | 1.676 | 0 | 0 |
| Target Spot | 1.404 | 0 | 1.404 | 0 |
| Tomato Yellow Leaf Curl Virus | 5.357 | 2.738 | 2.619 | 0 |
| Tomato mosaic virus | 373 | 0 | 373 | 0 |
| Healthy | 1.591 | 999 | 586 | 6 |

Ảnh hiện có là color JPEG RGB 256×256 theo manifest/sealed audit đã kiểm tra; không decode lại toàn bộ hoặc chạy lại near-duplicate cleaning. **6.749 record nguồn thiếu grouping có bằng chứng**, gồm 14 record excluded; Target Spot và mosaic đều chưa có group xác minh. Domain/nhãn ảnh chưa review độc lập. Không dùng sự đầy đủ mapping để thông qua split, leakage hay benchmark.

Đã đọc nội dung toàn bộ 17 card tomato, gồm condition/taxonomy, transmission, risk/severity, management, lookalikes/confounders, provenance và QA seeds. Các câu hỏi, rubric mức độ bệnh và giá trị risk trong card **không trở thành nhãn ảnh hoặc feature được đo**. Chưa có training hay đo inference EfficientNet/ResNet50. Không suy độ bệnh, giống cây, giai đoạn, năng suất hoặc lây lan diện rộng từ nhãn.

## 3. Liên kết bệnh và alias

[mapping.md](mapping.md) là bảng cho người đọc; [mapping.json](mapping.json)/[mapping.csv](mapping.csv) có nguyên nhãn, ID chuẩn giữ từ draft cũ, tên EN/VI dự thảo, tác nhân gốc, category dẫn xuất, đường dẫn card, SHA-256 file/content/source, disease ID gốc, bằng chứng và điều kiện hiển thị. Chín cặp exact_source_checked gồm bacterial spot, early blight, late blight, leaf mold, Septoria, spider mites, target spot, TYLCV, healthy. Mosaic là candidate_pending. Không có many-card fusion hoặc suy hướng dẫn từ top-k.

- **Early blight–Target spot:** khái niệm/tác nhân khác nhau; block alias `target spot of tomato` của early card. Có thể giữ hai mapping chính riêng, không cần sửa nhãn ảnh để tăng coverage. [UMN Early blight](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/early-blight-in-tomato-and-potato), [UF/IFAS Target Spot](https://ask.ifas.ufl.edu/publication/PP351).
- **ToMV–TMV:** mosaic card ghi Tomato mosaic virus nhưng alias chứa Tobacco Mosaic Virus; mapping chưa chốt. Không biến hai virus thành synonym. [UMN Tomato viruses](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/tomato-viruses).
- **Leaf curl–TYLCV:** leaf_curl_virus card giữ độc lập ngoài classifier; không đồng nhất triệu chứng xoăn lá/complex với lớp TYLCV. [UC IPM TYLCV](https://ipm.ucanr.edu/agriculture/tomato/tomato-yellow-leaf-curl/).
- **Nấm–oomycete:** late card có category/ID fungal, pathogen type oomycete. Chỉ sửa cách phân loại ở metadata dẫn xuất; không đổi raw ID. [UMN Late blight](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/late-blight).
- **Bệnh–thiếu dinh dưỡng–thuốc:** yellowing_symptom là triệu chứng physiological; pest_damage chưa xác định tác nhân; herbicide_damage được tham chiếu nhưng không có card. Không có lớp PlantVillage tomato tương ứng để tạo classifier link. Triệu chứng giống nhau không xác định nguyên nhân. [UMN Tomato viruses](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/tomato-viruses).
- **Cercospora–gray leaf spot:** card alias này cần chặn vì tên gray leaf spot còn dùng cho Stemphylium; chưa đủ nguồn để chấp nhận synonym ở đây. [UConn Tomato Stemphylium](https://ipm.cahnr.uconn.edu/tomato-stemphylium/).

[aliases.json](aliases.json) ghi **56 lần xuất hiện alias** theo JSON pointer: **4 accepted occurrences của 2 synonym khoa học** Fulvia fulva/Cladosporium fulvum của Passalora fulva; **6 blocked**, **46 pending**. Accepted ở mức danh tính theo nguồn, không phải chuyên gia ký duyệt. Không auto-accept alias còn lại chỉ vì gần tên. [UMN Leaf mold](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/tomato-leaf-mold).

[reference-link-review.json](reference-link-review.json) giữ nguyên **47 lookalike reference**: 23 exact-ID kỹ thuật, 24 unresolved. Cả 47 chưa được mở làm advice lookup/lesson xác minh. 56 confounder reference ở báo cáo nguồn gồm 52 slug candidate và 4 chưa diễn giải (3 câu hỏi, 1 absent herbicide card); không áp dụng candidate vào mapping.

Không có class_to_idx đã chốt cho mô hình tomato hoặc checkpoint thật. Metadata label index của README_HF nguồn vẫn giữ nguyên; đó không phải thứ tự checkpoint 10 lớp của project. [class-manifest.proposed.json](class-manifest.proposed.json) là **đề xuất**, lấy thứ tự lexical 10 nhãn hiện có, giữ TOM_* ID, có version/hash/ordering basis. Cần duyệt trước training; không sửa thứ tự một checkpoint tương lai bằng cách đọc folder tại runtime.

## 4. Review chăm sóc: căn cứ không đồng nghĩa được hiển thị

[claim-ledger.json](claim-ledger.json) chứa **172 management claim**, gồm mọi phần tử cultural/biological/chemical và 17 notes. Mỗi claim giữ nguyên EN, JSON pointer, raw/card hash, nguồn, mức hỗ trợ, lý do, ngữ cảnh, trạng thái chuyên môn/dịch và display_allowed. Đếm: **26 source_checked_candidate**, **34 partial_support_context_pending**, **107 unverified**, **5 held_specific_risk**. Tất cả **172 domain pending, chưa dịch và display_allowed=false**. Không coi mọi biological là phi hóa học hoặc mọi cultural là an toàn.

| Card | Số claim | Đối chiếu được nguyên tắc | Hỗ trợ một phần / cần ngữ cảnh | Chưa có căn cứ riêng | Hold cụ thể |
| --- | ---: | ---: | ---: | ---: | ---: |
| bacterial_spot | 11 | 2 | 4 | 5 | 0 |
| cercospora_leaf_spot | 11 | 0 | 0 | 11 | 0 |
| early_blight | 11 | 4 | 3 | 4 | 0 |
| flea_beetle_injury | 9 | 0 | 0 | 9 | 0 |
| fusarium_wilt | 11 | 0 | 0 | 11 | 0 |
| healthy | 7 | 4 | 3 | 0 | 0 |
| late_blight | 9 | 2 | 3 | 3 | 1 |
| leaf_curl_virus | 10 | 0 | 0 | 10 | 0 |
| leaf_miner | 11 | 0 | 0 | 11 | 0 |
| leaf_mold | 11 | 3 | 3 | 5 | 0 |
| mosaic_virus | 11 | 2 | 4 | 2 | 3 |
| pest_damage | 11 | 0 | 0 | 11 | 0 |
| septoria_leaf_spot | 11 | 4 | 2 | 5 | 0 |
| spider_mites | 9 | 1 | 4 | 3 | 1 |
| target_spot | 11 | 2 | 4 | 5 | 0 |
| yellow_leaf_curl_virus | 10 | 2 | 4 | 4 | 0 |
| yellowing_symptom | 8 | 0 | 0 | 8 | 0 |

Ví dụ căn cứ: spacing/mulch/tưới gốc cho early blight; giảm ướt lá/luân canh có điều kiện cho late blight; airflow/drip/residue trong protected cultivation cho leaf mold; giảm splash/tưới gốc/vệ sinh cho Septoria; giảm water stress cho mites; chăm sóc cơ bản cho healthy. Không vì chưa được ký duyệt mà loại khỏi ledger những nguyên tắc phi hóa học đã có nguồn. Chúng là ứng viên ưu tiên để kiểm duyệt và Việt hóa. [UMN Early blight](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/early-blight-in-tomato-and-potato), [UMN Late blight](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/late-blight), [UMN Leaf mold](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/tomato-leaf-mold), [UMD Septoria](https://www.extension.umd.edu/resource/septoria-leaf-spot-tomatoes), [UC IPM mites](https://ipm.ucanr.edu/home-and-landscape/spider-mites/), [UMN Growing tomatoes](https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/growing-tomatoes).

Hold cụ thể: copper hydroxide nằm trong biological; bleach 10% trong cultural; cross-protection bằng mild virus; aphid advice chưa đúng ToMV; overhead/misting cho mites thiếu điều kiện và có xung đột. Những câu hỗn hợp này chặn cả câu, không tự tách rồi coi phần còn lại đã duyệt. Removal/rogue cho virus hoặc late blight cần xác minh hiện trạng; TYLCV host-free period là quản lý phối hợp theo vùng, không suy từ một ảnh. Target spot card nêu leaf-wetness 8 giờ trong khi nguồn Florida mô tả 16–44 giờ ở điều kiện nghiên cứu; **khác biệt cần giải thích, không tự tuyên bố ngưỡng nào phổ quát đúng/sai**. [UC IPM TYLCV](https://ipm.ucanr.edu/agriculture/tomato/tomato-yellow-leaf-curl/), [UF/IFAS Target Spot](https://ask.ifas.ufl.edu/publication/PP351).

16 card chứa chemical array. Chưa xác minh đăng ký/nhãn/điều kiện Việt Nam, nên **không mở hóa chất, liều, lịch phun, thời gian cách ly hoặc cam kết chữa khỏi**. “Codex đã đối chiếu nguồn” không điền reviewer chuyên gia. Không sửa `safe_for_advice=false` hoặc policy dự án để vượt gate. Draft policy có demo source_checked giới hạn; sealed card hiện vẫn false/pending. Validator lượt này dùng release gate bảo thủ. Nếu muốn demo giáo dục dùng nội dung source_checked, cần duyệt phạm vi/artifact demo riêng và VI trước, không tái diễn giải cờ hiện tại là đã cho phép.

## 5. Vai trò WUR, Dryad, Mendeley và license

| Bộ | Điều kiện, đơn vị và giới hạn thực tế | Quyết định |
| --- | --- | --- |
| WUR | Challenge 2019, nhà kính cherry tomato, 6 compartment/team + weather. Dictionary/PDF lưu đơn vị khí hậu, cân nặng g, DMC %, năng lượng và resources. Excel serial chưa chốt epoch/timezone; 12 water interval alias và 48 cadence flag còn pending, 1 production timestamp ngoài climate span. Không chuyển đơn vị hoặc hiểu zeros thành missing. | Research-only; không join nhãn bệnh để tính lịch tưới/phân. |
| Dryad | Nghiên cứu water–nitrogen; 4 workbook, bốn khối tưới/85 dòng ngày, quality/photosynthesis/leaf-stem/fruit. T/Code chưa xác minh với treatment/replicate. Đơn vị VC/sugar, nutrient proportion scale còn tranh chấp; 108 formula cache chưa chứng minh freshness. Khối lượng mẫu quả g không phải năng suất mùa. Không suy giống/địa điểm từ tên thư mục; cần đối chiếu bài gốc và nhóm thực nghiệm trước ứng dụng mới. | Research-only; không tính liều hay tối ưu từ lớp ảnh. |
| Mendeley | CSV đã preprocessing/normalization theo mô tả tác giả; JSON cảm biến thử hệ tưới. Đơn vị/calibration, timezone, thiết bị/session còn thiếu; CSV không có khóa nối JSON. 30 timestamp không phải 30 thí nghiệm. ET=ET0*Kc khớp số học JSON không chứng minh ET tối ưu; optimalTemperature/crop coefficient có thể là cấu hình. | Research-only; không join hoặc dùng optimal/config thành outcome. |

Các nhận xét trên dựa trên source metadata, dictionaries và báo cáo cleaning sealed hiện hành, không phải fresh agronomic validation. 134/79/103 queue item WUR/Dryad/Mendeley tiếp tục giữ riêng. Nhãn bệnh không quyết định đất, giống, mùa, chậu/nhà kính, kích thước cây, lịch đo hoặc lượng tưới. Không có lý do đưa ba bộ này vào contract classifier/knowledge MVP.

License: PlantVillage local README_HF khai báo **CC-BY-SA-3.0**; cần kiểm tra scope phân phối/chuỗi attribution và nghĩa vụ dẫn xuất. PlantExpert README khai báo **CC-BY-4.0**, đồng thời nêu constituent CC0/CC-BY/CC-BY-NC; không đủ để khẳng định mọi thành phần hoặc lời khuyên APS có cùng quyền phân phối. [PlantVillage repository](https://github.com/spMohanty/PlantVillage-Dataset), [PlantExpert dataset card](https://huggingface.co/datasets/SyedNazmusSakib/PlantExpertVQA/blob/main/README.md).

WUR và Dryad intake khai báo CC0; Mendeley khai báo CC-BY-4.0, tác giả Rohit Kumar Kasera/Tapodhir Acharjee, DOI/version giữ trong hồ sơ. Nguồn khuyến nông dùng làm evidence, không mặc nhiên được sao chép toàn bài hoặc đóng gói ảnh của trang vào app. Trước phát hành cần attribution ledger cho từng thành phần, title/author/version/URL/license/change notice; nhánh NC hoặc chưa rõ quyền phải pending. Hash chứng minh byte, không chứng minh bản quyền hay chuyên môn.

## 6. Hợp đồng thử nghiệm và giới hạn

Code bổ sung: `scripts/data/review_integration.py`, `scripts/data/test_review_integration.py`. Tái sử dụng `pairs_unique`, `digest`, `snapshot`, `verify_artifacts`, `write_json` từ cleaning helper; riêng PlantVillage dùng snapshot có exclusion khớp baseline. Không đổi helper, framework hoặc dependency. Môi trường validator thực chạy Python **3.14.5** theo verification.json; runtime cleaning cũ là 3.12.14, giữ provenance phiên cũ.

Đầu vào lookup: class_index + manifest_version/sha256 + mapping_version + optional nguyên nhãn + confidence + scope/quality **do caller cung cấp**. Sau kiểm tra bundle, index phải thuộc đúng manifest. Chỉ relation exact_source_checked mới tiếp tục. Card phải giữ `domain=expert_approved`, `safe_for_advice=true`; claim phải có domain actor, VI actor, approved statuses, nguồn cụ thể và hash bind EN/source/card/VI. Healthy chỉ basic_care; chemical/mixed, biological chưa có contract và claim cần context đều bị giữ lại. Không ghép top-k. Output `needs_check` có reason và guidance rỗng; nhánh cho phép trả claim ID, VI, evidence và hash/version.

Đây là **contract release đề xuất**; không tự sửa chính sách hay phê duyệt thật. Chỉ một bản curated trusted bundle được phép nạp trong app tương lai; trước nạp phải xác minh file hash/version từ manifest phát hành được tin cậy. Hash không xác thực danh tính reviewer; dữ liệu bị sửa và tự hash lại vẫn cần trust boundary/provenance review. Validator nhỏ không phải security audit hoặc full schema framework.

22 unittest đã chạy, exit 0, [tests.txt](tests.txt): tất cả 10 lớp thật; approved synthetic fixture; index sai/bool/float; đổi thứ tự/hash/version; card mất/duplicate; mapping/claim duplicate; unknown label; ambiguous; thiếu nguồn; domain và VI tách biệt; healthy không trị bệnh và không trỏ disease; low/invalid confidence, external OOD/blurred; top-k không mix; chemical/context giữ lại; stale source/card/VI; EN claim không khớp JSON pointer; reviewer/evidence thiếu; object không mutate và card thật khớp processed registry. **Fixture approved chỉ nằm trong RAM, actor và VI ghi SYNTHETIC, không là bằng chứng duyệt card thật.**

Fixture threshold **0,7** là giá trị test. `scope=in_scope`/`quality=accepted` không phải thuật toán phát hiện OOD/mờ đã hiện thực. Chưa có model/evaluation để xác nhận calibration, OOD, accuracy hoặc hiệu quả chăm sóc. Test lookup chứng minh gate/referential contract, không chứng minh model chọn đúng lớp. Không chạy app E2E, SAST, pentest, training hay inference benchmark.

Lệnh tái kiểm tra từ gốc repository (không cleaning):

```powershell
python -m unittest discover -s scripts/data -p test_review_integration.py -v
python scripts/data/review_integration.py --audit-output <new-review-checkpoint.json>
```

`--build-output` dùng decisions.json và findings.json để tạo lại derivative; chỉ chạy vào **version review mới**, không ghi đè bản đã seal để đổi quyết định. Kết quả actual lookup và hash trước/sau nằm trong verification.json. Chưa có model manifest/checkpoint, nên không gọi đây là kiểm thử load model thật.

## 7. Việt hóa, readiness và thứ tự xử lý

EN/source/ID luôn bất biến. MVP ưu tiên **kho song ngữ với VI đã duyệt**, không dịch tại runtime. Không dịch hàng loạt lượt này; 10 tên Việt chỉ kế thừa draft. Cấu trúc từng bản dịch: translation_id/version, condition_id, card_id, claim_id/pointer, source EN/raw/card/claim hashes, EN text reference, VI text/hash, glossary version, translator/role/date/tool nếu có, translation review actor/status/date, domain approval riêng, context và attribution. Source/claim đổi phải invalidation; bản dịch hoàn chỉnh không mở gate domain.

Review VI: thuật ngữ/tác nhân đúng, phân biệt fungal/oomycete/mites/virus/healthy; giữ phủ định, mức chắc chắn, điều kiện, đơn vị và phạm vi; không thêm liều/thuốc/lịch ngoài nguồn. Giữ EN scientific names và glossary bilingual, tránh một tên Việt trỏ hai canonical disease. Không dùng API dịch. Dịch local một lần hoặc dịch thủ công đều cần đối chiếu từng claim; lựa chọn công cụ chưa được chốt/cài.

| Thứ tự | Việc cần làm tiếp | Điều kiện mở / checkpoint | Truy vết draft hiện có |
| --- | --- | --- | --- |
| 1 | Giải quyết ToMV/TMV, alias Target/gray/leaf curl, category oomycete | Quyết định danh tính có nguồn và actor; tạo derivative version mới, giữ ID | C3; S10; T05/T07; CAP-3/CAP-4 |
| 2 | Rà license/attribution, provenance từng card/claim; xác minh label/grouping ảnh | C2/C3, không dùng schema pass thay duyệt; no full split/training-ready | S01–S04, S10; T15/T18/T20/T07 |
| 3 | Ưu tiên 26 ứng viên phi hóa học, trước healthy và bệnh có identity rõ; xử lý 34 partial | Chuyên môn/ngữ cảnh đủ căn cứ; bỏ qua chemistry cho MVP, không loại toàn bộ nonchemical | C3; S10/S11; T07/T08 |
| 4 | Việt hóa số claim đã chọn, duyệt glossary và VI độc lập | Actor, version, hash, phủ định/đơn vị/context đúng; không bulk translate khi chưa chọn nội dung | S10/S11; T07/T08/T09 |
| 5 | Duyệt manifest lớp và release/demo policy rõ | Không tạo checkpoint giả; public/demo có artifact và gate riêng | C2/C3; S04/S10; T04/T05/T07 |
| 6 | Cập nhật và tiếp nhận draft BMAD khi được yêu cầu riêng | Giữ FR/NFR/S/T/CAP/AD, lịch sử; đưa blockers vào kế hoạch chính thức | C0–C3; S01 |

Các ID trên là truy vết đề xuất tới draft cũ; test unit mới có tên hàm riêng, **không đánh dấu T01–T20 đã chạy/qua**. Nếu chưa có người chuyên môn, domain approval tiếp tục pending; có thể chuẩn bị bằng chứng và dịch draft, nhưng không giả expert hoặc lặng lẽ đổi policy để phát hành.

| Readiness | Kết luận hiện tại |
| --- | --- |
| Sạch kỹ thuật | Các run sealed/manifest khớp baseline trong scope; không đồng nghĩa nhãn/nội dung đúng |
| Nhãn ảnh xác minh | Chưa có review độc lập toàn bộ ảnh; grouping/near duplicate còn pending |
| Nối dữ liệu kỹ thuật | Có contract và tests; 9 identity source-checked, 1 held; class manifest còn đề xuất |
| Hiển thị guidance thật | **Chưa đủ**: 17 card/172 claim chưa domain/VI approval, license/context còn thiếu |
| Huấn luyện | **Chưa đủ**: chưa split/manifest chốt/grouping đầy đủ, chưa model hoặc metric |
| Planning chính thức | **Chưa tiếp nhận**; runtime ready không làm dự án ready |

[review-queue.json](review-queue.json) là derivative **352 item**: giữ nguyên 110 item cleaning, thêm 172 claim review + 18 triage + 52 alias pending/blocked. Không đóng queue gốc. [provenance.json](provenance.json), planning-before snapshot và artifact seal ghi input/code/output hashes, nhật ký và bảo toàn ID. Không có raw/processed đã chốt bị sửa; không có ứng dụng, training, dữ liệu/weights mới hoặc dịch dataset trong lượt này.
