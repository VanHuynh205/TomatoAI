# PlantExpertVQA-tomato — làm sạch kỹ thuật và checkpoint

Ngày **14/10/2026**, Asia/Bangkok. Đề tài: **Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua**. Chỉ thực hiện Prompt 2 cho kho tri thức cà chua; không viết ứng dụng, train, tải dữ liệu/weights, gọi API AI, dịch dataset hoặc nhập planning chính thức. Audit/planning cũ và kết quả PlantVillage giữ nguyên.

**Trạng thái `cleaned_technical` + `needs_review`: 17/17 thẻ parse và đạt contract kỹ thuật local, 17 thẻ vẫn chờ domain/translation review.** `safe_for_advice=false` và `ready_for_training=false` cho mọi record. Không có tập QA có answer/outcome hoặc ảnh VQA trong bản tải này; `qa_seeds` là template/thông tin tham chiếu. Không coi mô tả mức độ bệnh trong KB là nhãn severity cho ảnh PlantVillage.

## Artifact, skill và môi trường thực dùng

Run hiện hành **`pex-b3da04d66a031756`**. Fingerprint dùng toàn bộ source snapshot, config, hai input tham chiếu, SHA256 script và Python version; output được seal bằng hash.

| Artifact | Nội dung |
| --- | --- |
| [Pipeline](../../../../../scripts/data/clean_plantexpert.py), [config](../../../../../scripts/data/plantexpert-config.json), [test](../../../../../scripts/data/test_clean_plantexpert.py) | CLI Python và unittest; đường dẫn dữ liệu tương đối qua config |
| [Processed run](../../processed/plantexpert-tomato/pex-b3da04d66a031756/) | 17 JSON envelope EN, 17 source copy nguyên byte; không ghép ảnh/tri thức thành dataset train |
| [Manifest JSONL](../../processed/plantexpert-tomato/pex-b3da04d66a031756/manifest.jsonl), [CSV](../../processed/plantexpert-tomato/pex-b3da04d66a031756/manifest.csv) | 21 field/record, source pointer/hash và transformation log |
| [Mapping nhãn–tri thức](../../processed/plantexpert-tomato/pex-b3da04d66a031756/label-knowledge-mapping.json), [glossary VI draft](../../processed/plantexpert-tomato/pex-b3da04d66a031756/glossary-vi-draft.json) | 10 nhãn ảnh/ID đã có; tên Việt lấy từ draft hiện hữu, chưa duyệt |
| [Summary](pex-b3da04d66a031756/summary.json), [checkpoint](pex-b3da04d66a031756/checkpoint.json) | Counts mới, môi trường, provenance, trạng thái và bước tiếp tục |
| [Raw trước](pex-b3da04d66a031756/raw-before.csv), [raw sau](pex-b3da04d66a031756/raw-after.csv), [reference inputs](pex-b3da04d66a031756/reference-inputs.json) | SHA256 nguồn và input tham chiếu; gồm cache/intake metadata |
| [Source schema](pex-b3da04d66a031756/source-schema.json), [field inventory](pex-b3da04d66a031756/field-inventory.csv) | Contract kỹ thuật local; kiểu/missingness/zero tại từng JSON pointer |
| [Review queue](pex-b3da04d66a031756/review-queue.json), [quarantine](pex-b3da04d66a031756/quarantine.json) | 110 mục review trên 17 thẻ; quarantine kỹ thuật hiện rỗng |
| [Lookalike links](pex-b3da04d66a031756/reference-links.json), [confounder links](pex-b3da04d66a031756/confounder-links.json) | Link exact và ứng viên chưa áp dụng; không viết lại ID nguồn |
| [Duplicate groups](pex-b3da04d66a031756/duplicate-groups.json), [shared text](pex-b3da04d66a031756/repeated-text.json), [alias collisions](pex-b3da04d66a031756/alias-collisions.json) | Kiểm tra trùng và tên; nội dung dùng chung được giữ |
| [Output hashes](pex-b3da04d66a031756/output-artifacts.json), [registry](../../dataset-registry.json) | Hash artifact bất biến; trạng thái các dataset khác giữ nguyên |
| [Registry trước](registry-before-20261014.json) | Bản sao nguyên byte trước cập nhật, dùng đối chiếu/rollback |

Skill thực dùng:

- **Migration** (`C:/Users/admin/.agents/skills/migration/SKILL.md`): xác định writer hiện tại chỉ là pipeline, chưa có reader ứng dụng; tạo format dẫn xuất có phiên bản, giữ nguồn/các ID hiện hữu; idempotency, checkpoint và rollback qua registry. Không có bước contract/xóa raw.
- **Ponytail full** (`.dsh/skills/ponytail/SKILL.md`): dùng stdlib và runtime đã có, tái sử dụng conventions versioned manifest/queue/hash cùng mapping PlantVillage. Không refactor pipeline ảnh đã seal hoặc thêm framework chỉ để chia vài hàm I/O; script KB độc lập không import Pillow.

Discovery catalog/router và skill local không tìm thấy skill chuyên audit JSON PlantExpert, Python preprocessing hay kiểm duyệt nông học. Pipeline/unittest minh bạch là fallback. Đã đọc e2e để kiểm tra điều kiện AGENTS; không chạy workflow UI: không có e2e.config/frontend URL/API sản phẩm cho pipeline này. Không tạo UI/config, không gọi model để test. `docs/agents/domain.md` không tồn tại; dùng tài liệu planning và source thực tế, không dựng domain doc giả. BMAD runtime từ phiên setup không bị đổi; không gọi build/dev hay tạo memlog/ticket.

Môi trường thực chạy: **Python 3.12.14**, Windows 11 build 26200, executable `C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Pipeline/test chỉ dùng **stdlib**, không cài dependency. Chỉ parse từng thẻ và giữ cấu trúc nhỏ trong RAM; không nạp ảnh hoặc cả corpus QA vào context.

## Nguồn và kiểm chứng bất biến

Nguồn local `data/TomatoAI/data/raw/plantexpert`; card directory `disease_kb/tomato`. Có **18 file payload không thuộc cache = 17 JSON + README, 151.858 byte**. Scope bảo toàn đầy đủ gồm cả `.cache/huggingface`, metadata tiếp nhận và cache tree: **39 file, 3.298.343 byte**. Không giải nén archive hoặc thực thi nội dung nguồn.

Snapshot path/size/SHA256 trước–sau **khớp toàn bộ 39 file**; mỗi source copy trong processed cũng khớp byte nguồn. Hai input tham chiếu (mapping PlantVillage và audit draft) có hash giữ nguyên. Cache metadata của 18 payload cùng ghi revision `e21eacc1eff9e1db38966d78d0e8af2f22706313`; đây là quan sát cache local, không chứng nhận remote hoặc toàn repository tại revision đó.

README local khai báo **CC BY 4.0**, nguồn được chỉ định là [PlantExpertVQA tomato](https://huggingface.co/datasets/SyedNazmusSakib/PlantExpertVQA/tree/main/disease_kb/tomato). Phiên này không fetch/đối chiếu remote, không xác nhận điều kiện phân phối từng thành phần. Giữ nguồn/license/notice và ghi biến đổi trước phân phối; quyền phân phối vẫn là checkpoint riêng. Các số QA/ảnh toàn corpus trong README không phải số local hay kết quả đồ án.

## Trước/sau và flags

| Hạng mục | Trước | Sau / xử lý |
| --- | ---: | --- |
| Thẻ nguồn cà chua | 17 | 17 record manifest, 17 source copy, 17 normalized envelope |
| Parse JSON UTF-8/UTF-8 BOM | Chưa kiểm chứng trong phiên | 17/17 hợp lệ; 0 lỗi encoding/duplicate-key/JSON constant |
| Contract schema kỹ thuật local | Chưa kiểm chứng trong phiên | 17/17 đạt, 0 thiếu field bắt buộc/sai kiểu/ID syntax/crop/timestamp |
| Excluded / quarantine kỹ thuật | 0 | **0 / 0**; không tự loại thẻ khi thiếu nguồn chuyên môn |
| Needs review theo record, disjoint | Chưa chạy | **17**; 17 + 0 quarantine + 0 excluded = 17 |
| Thay đổi Unicode giá trị | Chưa chạy | **0** trên nguồn thực; NFC đã kiểm bằng fixture khác |
| Trùng toàn file hoặc canonical JSON | Chưa chạy | **0 nhóm**; không xác nhận mọi trùng ngữ nghĩa đã được tìm hết |
| Chuỗi dùng chung | Chưa chạy | **17 nhóm** cùng field quản lý/template, giữ nguyên; không coi là thẻ trùng |
| Alias collision literal | Chưa chạy | **0**, phép so khớp token literal không chứng minh không có alias mơ hồ |
| Lookalike references | 47 | **23 exact / 24 unresolved**, mọi ID nguồn giữ nguyên |
| Confounder entries | 56 | **52 filename-slug candidate / 4 cần review**, không tự apply |
| Mapping/VI labels | Draft có từ planning | 10 explicit draft schema matches + 10 glossary term; chưa domain/translation approve |

Field inventory có **2.677 node**, gồm **55 empty array**, **31 empty string**, **2 null**, cùng **11 numeric zero được giữ nguyên**. Empty/null ở khoa học của trạng thái khỏe, taxonomy chưa đầy đủ, triệu chứng cơ quan không áp dụng... không mặc định là lỗi. Không impute/scaling/fit, không đổi 0 thành missing. Missing field bắt buộc khác với empty value hợp lệ theo contract.

Flags **chồng nhau**, không cộng thành số thẻ: domain review 17; nguồn theo claim chưa xác minh 17; translation pending 17; chemical applicability 16; unresolved references trên 12 thẻ/24 links; type vocabulary difference 9; issue_type unknown 2; checkpoint nội dung 4; confounder review trên 2 thẻ/4 entries. Queue **110 item** là số vấn đề/điểm duyệt, không phải 110 record dữ liệu.

## Schema, đơn vị và provenance

Thẻ thực có **15 field top-level**. Audit lịch sử ghi 16 nhưng liệt kê chính 15 tên; giữ biên bản cũ, dùng source-schema và kết quả mới làm căn cứ phiên này. Contract tự khai báo phục vụ audit local, không giả là JSON Schema chính thức của tác giả.

| Nhóm field nguồn | Kiểu và ý nghĩa / đơn vị |
| --- | --- |
| schema_version, disease_id, issue_type | String; giữ nguyên ID/category nguồn, không canonicalize taxonomy |
| aliases, crop, condition | List string và object; scientific_name có thể null; chưa coi aliases là resolver được duyệt |
| transmission, symptoms | Object chứa list string; empty list được giữ; chia lá/thân/quả/rễ/toàn cây |
| environmental_risk | risk_factors list; temp_c_day/night là khoảng theo tên field °C; relative_humidity_pct theo tên field %; leaf_wetness_hours_threshold theo tên field giờ. Giữ số/range, không tự bổ sung điều kiện áp dụng |
| severity_rubric | unit string và mô tả mild/moderate/severe/notes. Có `percent_leaf_area` và `qualitative`; không chuyển văn bản thành target severity của ảnh |
| lookalikes | List object: condition_name, condition_id, key_differences; mỗi link có source pointer và trạng thái exact/unresolved |
| management | cultural/biological/chemical list string, notes string; EN nguyên nghĩa, chưa xác nhận thuốc/liều/pháp lý/hiệu quả địa phương |
| qa_seeds | 6 list string: verification/attribute/diagnosis/counterfactual/severity templates và confounders. Không phải cặp supervised input–answer |
| data_requirements | min_resolution_px integer pixel, min_roi_fraction số tỷ lệ, lighting/occlusion notes string; điều kiện hướng dẫn thu ảnh trong KB, không áp làm bộ lọc ảnh PlantVillage |
| provenance | created/reviewed_by và timestamp ISO có timezone; sources list string. Tên vai trò chưa chứng minh người review hoặc claim đúng |

Manifest **21 field**:

| Field | Contract dẫn xuất |
| --- | --- |
| schema_version, record_id | Version `1.0`; ID `pex:<relative source_file>` ổn định theo path; không thay disease_id hay gán nhãn bệnh mới |
| source_file, source_record, source_sha256, source_bytes | Path tương đối source root; JSON pointer `/`; SHA256 file gốc và byte count |
| disease_id_original, issue_type_original | String gốc hoặc null nếu parse lỗi, không tự sửa namespace |
| parse_ok, schema_ok, technical_errors | Bool riêng parse/schema; lỗi có JSON pointer và lý do |
| flags, record_status | List flag chồng; needs_review hoặc quarantined_technical, không gán training-ready |
| raw_copy, processed_file, normalized_sha256 | Relative path bản copy nguồn/envelope; null nếu không tạo envelope; hash dẫn xuất |
| transformations | List source_pointer/operation/before/after; chỉ NFC string value, không đổi key, bỏ text, đổi số hay dịch EN |
| domain_review, translation_review | pending / not_translated; review glossary riêng là draft needs_review |
| safe_for_advice, ready_for_training | **False** cho mọi record trong lượt này |

Envelope có schema_version/record_id/content_language/source/content_en/normalizations/flags/review; `content_en` giữ cả field ngoài contract nếu có. CSV encode list/object bằng JSON, JSONL giữ kiểu số/bool/null. UTF-8 xuất có Unicode, ID/file nguồn không bị đổi tên.

Transformation log thực chạy: full raw hash → strict parse → type/required/identity/timestamp audit → inventory → NFC string values → reference/duplicate checks → envelope + draft mapping/glossary → review queue → source copy/output manifests → full rehash → artifact seal. Không thay đổi EN nào trong 17 thẻ thật vì đã ở NFC. Tests có chứng minh NFC không đổi source keys, số, phủ định và raw bytes.

## Checkpoint cần review

| Điểm chưa giải quyết | Bằng chứng đã đọc | Cách tiếp tục |
| --- | --- | --- |
| 24 lookalike IDs chưa khớp | Mọi link có thẻ/pointer/ID gốc; 24 candidate theo suffix filename có sẵn | Xác minh từng identity/namespace với nguồn cụ thể; ghi quyết định alias, reviewer và phiên bản trước tạo dẫn xuất mới. Không áp suffix như ground truth |
| 4 confounder entries | leaf_curl_virus có 3 **câu hỏi**, không phải slug; mosaic có `herbicide_damage` chưa có card local | Giữ strings; duyệt schema/ý nghĩa, không đổi câu hỏi thành ID, không bịa thẻ hoặc gán ảnh vào lớp mới |
| Late blight | disease_id/issue_type `disease_fungal`; pathogen.type `disease_oomycete` | Giữ cả hai; duyệt taxonomy bằng nguồn, không đổi ID raw. [Research draft R14](../../../../../planning/tomato-desktop/research.md) có nguồn đối chiếu trước, chưa là approval |
| ToMV/TMV, early/target aliases, leaf-curl/yellow-curl | Source aliases/card riêng và checkpoint pointer trong config | Không đồng nhất tác nhân hoặc merge thẻ; review theo source, nhãn ảnh và phạm vi display |
| 9 type vocabulary differences | `fungus`/`virus`/`insect`/`physiological`... so với issue_type | Một số có thể là synonym hợp lệ; flag không phải kết luận 9 lỗi taxonomy. Hai issue_type `unknown` giữ unknown |
| Nguồn/reviewer | 17 thẻ chỉ có tên nhóm tài liệu, **không URL theo claim**; reviewer là vai trò, early có `N/A` | Bổ sung citation cụ thể, điều kiện áp dụng và bằng chứng review. README nói expert review không chứng minh từng card đã được chuyên gia Việt Nam duyệt |
| 16 thẻ có chemical advice | 42 string chemical; healthy chemical=[] hợp lệ | Giữ EN, không thêm thuốc/liều/thời gian cách ly; chờ review nguồn và điều kiện Việt Nam trước cho phép hiển thị tư vấn |
| VI/glossary | 10 term kế thừa mapping draft, reviewer=null | Duyệt tên khoa học/thuật ngữ/loại bệnh–hại–khỏe trước dịch ở phiên được phép; không gọi bản draft đã duyệt |
| Độ đầy đủ chăm sóc/trồng | Cultural advice chủ yếu gắn trạng thái, có giai đoạn/môi trường trong text | Chưa là giáo trình trồng đầy đủ, quy tắc cá nhân hóa hoặc dữ liệu tối ưu canh tác. Không ghép top-k thành phác đồ chung |

Mẫu EN đã đọc, chỉ minh họa cấu trúc: healthy `/symptoms/leaves/0` “Uniformly green color, consistent with the cultivar.”; early `/aliases/1` “target spot of tomato”. Các câu chưa được gọi hướng dẫn VI đã duyệt. Đánh giá mâu thuẫn chỉ bao gồm liên kết, vocabulary, alias checkpoint và range screening nêu trên; chưa xác minh khoa học mọi câu, đối chiếu thuốc hoặc semantic contradiction toàn kho.

MVP nên dùng lookup từ mã trạng thái tới thẻ được kiểm duyệt trong giai đoạn sau; dữ liệu này chưa đủ bằng chứng để train một bộ tư vấn supervised. Các QA templates/severity text không bổ sung nhãn ảnh, không cho CNN suy năng suất/độ lây lan.

## Lệnh và kiểm chứng đã chạy

Từ project root:

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'scripts/data/clean_plantexpert.py' --config 'scripts/data/plantexpert-config.json' --project-root 'C:\Users\admin\Downloads\DACN_CayCaChua'
$env:PLANTEXPERT_REPORT = 'C:\Users\admin\Downloads\DACN_CayCaChua\data\TomatoAI\data\reports\plantexpert-tomato\pex-b3da04d66a031756'
$env:PLANTEXPERT_PROJECT_ROOT = 'C:\Users\admin\Downloads\DACN_CayCaChua'
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'scripts/data/test_clean_plantexpert.py'
```

**14/14 test đạt, 0 skip, exit code 0** trong lần cuối: 9 CLI fixture tests và 5 kiểm tra output thật. Bao phủ EN/source provenance, zero/null/empty hợp lệ, NFC không đổi raw/key, malformed/duplicate JSON keys/NaN/overflow/encoding quarantine, missing/wrong type/crop, unresolved alias/taxonomy không tự sửa, duplicate IDs/trùng thẻ giữ review, mapping/VI gate, output boundary/byte limit/incomplete checkpoint, rerun/tamper refusal. Output thật được kiểm bằng SHA256 từng nguồn và source copy, content_en so với raw NFC, count/schema/IDs/links/10 nhãn, flags/approval gate và output/input hashes. Fixture tạm không thuộc dữ liệu train.

Bằng chứng: [cleaning-run.txt](cleaning-run.txt), [verification-tests.txt](verification-tests.txt), [idempotency-rerun.txt](idempotency-rerun.txt). Rerun exit code 0, trả `reused_verified`; kiểm artifact set/hash, không tạo record/run mới hoặc ghi đè kết quả seal. Fixture idempotency còn kiểm mtime toàn artifact không đổi và tamper bị từ chối. Test preflight trước khi có output đã skip 5 production checks; kết quả cuối nêu trên chạy đủ 14, không dùng preflight làm bằng chứng production.

Chưa chạy browser e2e vì không có ứng dụng/config phù hợp; không dựng frontend để phục vụ pipeline. Không dùng AI-driven test/model API. Không có lint/type-check tool riêng đã cấu hình cho pipeline; CLI và unittest đã thực thi Python. Không chạy SAST/pentest hay metric train.

Retry: cùng source/config/code/version dùng lại artifact đã verify. Thay input/code tạo fingerprint mới. Checkpoint chưa seal phải được đọc để tìm lỗi; CLI từ chối overwrite và cho phép `--run-tag <slug>` cho lần thử mới. Không có delete/overwrite flag. Partial failure giữ artifact/checkpoint, không được registry đánh dấu current thành công.

Rollback: registry đã backup trước cập nhật. Nếu quyết định không dùng run này, khôi phục entry PlantExpert từ bản backup hoặc trỏ current tới run được duyệt trước đó; không khôi phục cả registry nếu dataset khác có cập nhật mới. Giữ nguyên run/evidence để truy vết; nguồn chưa từng bị sửa. Chưa có app reader nên không cần chuyển đổi writer sản phẩm hoặc contract migration.

## Handoff

Đã hoàn thành phần làm sạch kỹ thuật; domain, translation, reference alias và quyền phân phối vẫn pending. Checkpoint và 110 review item có source pointer/next action; các phần này chặn sử dụng tri thức như tư vấn đã duyệt, không được bỏ qua bằng trạng thái JSON hợp lệ. Không nhập PRD/spec/ticket chính thức trong phiên này.

Dataset tiếp theo theo thứ tự Prompt 2: **WUR**, chỉ xử lý ở phiên người dùng yêu cầu riêng. WUR/Dryad/Mendeley vẫn research_only, ngoài phụ thuộc MVP; giữ các blocker PlantVillage và PlantExpert khi chuyển sang Prompt 3 sau này. Phiên này dừng tại bàn giao PlantExpertVQA-tomato.
