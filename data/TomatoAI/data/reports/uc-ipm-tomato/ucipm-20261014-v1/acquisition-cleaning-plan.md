# UC IPM Tomato: quyền sử dụng và đề xuất thu thập/làm sạch

Ngày truy cập: **2026-10-14, Asia/Bangkok (UTC+07:00)**. Phiên bản nghiên cứu: `ucipm-20261014-v1`. Phạm vi hiện tại là đọc nguồn chính thức, lưu metadata và phân tích; chưa tải ảnh/PDF để tạo corpus, chưa đổi raw/processed/registry/policy hoặc ứng dụng. Đây là kế hoạch đề xuất, không phải xác nhận bộ dữ liệu đã có quyền phân phối hay sẵn sàng huấn luyện.

## 1. Nguồn và tình trạng kiểm chứng

| Mã | URL yêu cầu / URL cuối | Tình trạng đọc; ngày trên nguồn |
| --- | --- | --- |
| T | [Tomato index](https://ipm.ucanr.edu/agriculture/tomato/) → cùng URL | HTTP trực tiếp 200; trang hiện hành, footer ©1996–2026; không thấy ngày cập nhật nội dung index. |
| A | [UC IPM Legal Notices](https://ipm.ucanr.edu/GENERAL/copyright.html) → cùng URL | HTTP trực tiếp 200; **banner archived**, bản quyền nội dung ©1995–2019, footer 2019; không phải bản chính sách mới ghi ngày 2026. |
| B0 | [Đích liên kết copyright từ Tomato](https://ucanr.edu/?copyright=) → cùng URL trong web reader | Web reader trả trang chủ, không có điều khoản chi tiết. HTTP trực tiếp lần đầu 200, lần sau 403. Chỉ dùng để xác định đường tới B. |
| B | [UC ANR Copyright](https://ucanr.edu/copyright) → cùng URL | Web reader đọc được trang chính thức; HTTP trực tiếp 403. Nội dung notice ghi 2024, footer 2026; không có ngày sửa chính sách. |
| C | [Permissions URL được liên kết](https://ucanr.edu/site/anr-publishing/permissions) → [URL cuối](https://ucanr.edu/dept/anr-publishing/permissions) | Web reader ghi redirect và đọc được; HTTP trực tiếp cả hai URL 403. Không thấy ngày sửa nội dung. |
| D | [CC BY-NC-ND 4.0 deed](https://creativecommons.org/licenses/by-nc-nd/4.0/) → cùng URL | HTTP trực tiếp 200; header Last-Modified `2026-10-01 17:09:54 GMT`; đây là thời điểm phục vụ tài nguyên, không phải ngày UC cấp quyền. |
| E | [CC BY-NC-ND 4.0 legal code](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en) → cùng URL | Đọc toàn văn bằng web reader; phiên bản giấy phép 4.0. |
| R | [robots.txt](https://ipm.ucanr.edu/robots.txt) → cùng URL | HTTP trực tiếp 200; Last-Modified `2024-12-18 17:54:40 GMT`; kiểm tra lại trong phiên 2026-10-14. |
| M | [About UC IPM pest information](https://ipm.ucanr.edu/PMG/aboutpmg.html) → cùng URL | HTTP trực tiếp 200; **banner archived**, footer 2016; không thấy ngày sửa nội dung. |

Web reader không trả HTTP status cho B/C/E; không suy diễn status 200 từ việc đọc được. Header Date được ghi nhận trong khoảng `2026-10-14 10:46–10:48 UTC` đối với các lần HTTP trực tiếp. Các lỗi 403 được giữ là giới hạn kiểm chứng; không tìm cách vượt chặn. T và M nằm trong tổng 26 trang nội dung/metadata của báo cáo, không đếm lại vào bảy URL quyền/robots. B0 là điểm định tuyến bản quyền, không dùng nội dung trang chủ làm bằng chứng chuyên môn.

## 2. Các điều khoản có bằng chứng

**A — chính sách IPM lưu trữ, TEXT/PHOTOGRAPHS/FIGURES:** cho tải văn bản/PDF cá nhân hoặc sao chép giáo dục, giữ credit/copyright. Ngoài phạm vi ấy cần đồng ý trước bằng văn bản; phân phối thương mại bị cấm. Ảnh đưa vào software/media hoặc ấn phẩm cần chấp thuận. Slide phi quảng bá có ngoại lệ; website trường/cơ quan tối đa 20 ảnh kèm điều kiện credit, notice, liên kết, thông báo. Figures có ngoại lệ quyền bên thứ ba và chỉ dẫn liên hệ xin quyền. Những ngoại lệ này không tự cấp quyền ML. [Nguồn A](https://ipm.ucanr.edu/GENERAL/copyright.html).

**B — Use of Materials hiện tại của UC ANR:** cho sao chép giáo dục, yêu cầu notice Regents và CC BY-NC-ND 4.0. Ảnh dùng quảng bá/ấn phẩm khác cần quyền thêm; thương mại bị cấm. Trang không nói riêng dataset cà chua hay ML. [Nguồn B](https://ucanr.edu/copyright).

**C — Requesting use of UC ANR materials:** ấn phẩm tải miễn phí được sao chép/phân phối theo CC BY-NC-ND. Cấp phép phải do permissions officer hoặc đại diện được ủy quyền, không phải tác giả. [Nguồn C](https://ucanr.edu/dept/anr-publishing/permissions).

**E — §1(a), §2(a)(1), §2(a)(4), §3, §4:** dịch có thể là Adapted Material; CC này cho tạo/sao chép bản thích nghi phi thương mại nhưng không Share. Thay đổi kỹ thuật định dạng cần thiết không tự tạo bản thích nghi. Chia sẻ phải giữ attribution, notice, disclaimer, URL/license; cơ sở dữ liệu còn có điều kiện riêng. Chỉ áp dụng với vật liệu được cấp giấy phép, không mọi thứ trên một domain. [Legal code E](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en). [Deed D](https://creativecommons.org/licenses/by-nc-nd/4.0/) chỉ là bản tóm tắt, không thay văn bản giấy phép.

**Điểm chưa chắc chắn:** T hiện vẫn trỏ A đã archived; B/C là chính sách chung mới hơn. Chưa có chứng cứ riêng rằng toàn bộ HTML Tomato, mọi PDF, ảnh/figure/table bên thứ ba đều được cấp CC BY-NC-ND. Không chọn chính sách thuận lợi hơn rồi gắn nhãn `cleared` cho toàn nguồn. Cần đối chiếu notice từng tài nguyên và xác nhận phạm vi khi muốn dùng sản phẩm dẫn xuất.

## 3. Năm trường hợp sử dụng riêng

Các trạng thái **được nêu rõ / cần xác minh / không phù hợp theo điều khoản** áp dụng cho mục đích và tài nguyên cụ thể. Việc dự án tạm không thu thập ảnh không có nghĩa mọi cách train/test đều bị điều khoản cấm. Đây là đánh giá bằng chứng đã đọc, không phải nhãn UC cung cấp.

| Trường hợp | Trạng thái và bằng chứng | Quyết định đề xuất cho TomatoAI |
| --- | --- | --- |
| 1. Đọc web; tải để nghiên cứu cá nhân | **Được nêu rõ, có điều kiện** theo A/TEXT, đối với bản văn bản/PDF cá nhân; giới hạn archived nêu trên. | Có thể tham khảo thủ công và lưu metadata/trích dẫn. Không suy diễn thành crawler toàn site hay quyền tải mọi media. Nếu lưu bản cá nhân, giữ nguồn và notice, tách khỏi artifact sẽ chia sẻ. |
| 2. Lưu văn bản/PDF cho đồ án học thuật | **Được nêu rõ, có điều kiện** cho bản gốc phục vụ giáo dục theo A/TEXT, B/Use of Materials, C; **cần xác minh** từng tài nguyên chưa rõ phạm vi. | Chỉ lưu bản có mục đích/quyền tương ứng. “Đồ án” không cấp quyền mặc định đưa corpus vào Git hoặc app. Bản học tập và bản phát hành có cổng kiểm tra riêng. |
| 3. Trích xuất, biên soạn lại, dịch tiếng Việt | **Cần xác minh** corpus/chuyển ngữ TomatoAI; **không phù hợp theo điều khoản** nếu chia sẻ bản dịch chỉ dựa CC ND (E §1/§2). | Bản thích nghi cá nhân phi thương mại chỉ được cân nhắc nếu tài liệu thực sự cấp CC. Cần đánh giá quyền riêng cho biên soạn; ghi chú độc lập không đồng nghĩa quyền tái tạo có hệ thống nội dung được bảo hộ. |
| 4. Phân phối offline trong app/repo/demo | **Cần xác minh** chính gói đề xuất; **được nêu rõ, có điều kiện** với bản nguyên trạng thực sự cấp CC, phi thương mại (C/E). | Demo công khai vẫn có thể là Share. Chỉ chia sẻ report metadata/liên kết ở giai đoạn này; không tuyên bố mọi bản offline bị cấm. Chưa có quyền cho bộ tiếng Việt dẫn xuất. |
| 5. Photos, figures, tables; ảnh huấn luyện/kiểm thử | **Cần xác minh** riêng cho ML và chủ quyền từng item; **không phù hợp theo điều khoản** A nếu đưa ảnh vào software/media không thuộc ngoại lệ mà thiếu chấp thuận. Tables cần xét tài liệu chứa/quyền bên thứ ba. | Chưa tải ảnh, crop, screenshot bảng/figure hay tạo nhãn. Ngoại lệ slide/website cơ quan không mở rộng thành dataset ML. Caption, credit và khả năng xem công khai không thay giấy phép. |

Không kết luận huấn luyện/kiểm thử ảnh bị cấm trong mọi hoàn cảnh: nguồn đã đọc chưa cấp phép rõ cho mục tiêu này. Tuyến dataset ảnh hiện tại thiếu cả quyền và bằng chứng schema/nhãn/split. Trích dẫn và photographer credit không thay cấp quyền sử dụng.

## 4. Robots và giới hạn truy cập

Các directive thực tế có liên quan trực tiếp, trích nguyên dạng tối thiểu từ R:

```text
User-agent: *
Allow: /PDF/PUBS
Allow: /PDF/QTSP
Disallow: /PDF
Disallow: /PMG/TEST
Disallow: /ADMIN
```

R còn chặn các tuyến nội bộ, tạm, tài nguyên giao diện, feedback, tools, page-view và một số model/weather. Không thấy directive chặn `/agriculture/tomato/`. Các dòng bắt đầu `#` là comment; ghi chú giờ quét buổi tối/cuối tuần không phải directive cấp phép. Không thấy Crawl-delay hoặc Sitemap trong bản đã đọc. [Nguồn R](https://ipm.ucanr.edu/robots.txt).

Đề xuất: trước đợt thu thập tương lai, đọc lại robots, kiểm tra đúng URL cuối và host, ưu tiên đường cụ thể dài hơn khi xử lý Allow/Disallow; không quét đường cấm. Robots không phải giấy phép bản quyền; đường không bị chặn không chứng minh được phép chuyển ngữ, phân phối hay ML. Không thử vượt 403/429, đổi danh tính bot hoặc tìm đường phụ để lấy nội dung bị chặn.

## 5. Chất lượng chuyên môn và giới hạn địa phương

M mô tả PMG do chủ yếu nhà khoa học UC viết, phản biện bởi chuyên gia trước xuất bản; cập nhật hằng năm khi cần và rà soát sâu ít nhất mỗi năm năm. `reviewed` và `updated` có ý nghĩa khác nhau. Đây là mô tả quy trình trên trang **archived**, chưa chứng minh mọi trang hiện hành mới được phản biện gần đây. Khuyến cáo dựa bối cảnh California; nhãn thuốc thay đổi và người dùng phải tuân nhãn/quy định địa phương. [Nguồn M](https://ipm.ucanr.edu/PMG/aboutpmg.html).

Đề xuất khi biên soạn dữ liệu: giữ ngày `updated`/`reviewed` nguyên trạng và riêng với `accessed_at`; ghi địa bàn California. Không chuyển đăng ký thuốc, liều dùng hay thời gian cách ly của California thành hướng dẫn áp dụng Việt Nam. Những nội dung ấy cần đối chiếu nguồn Việt Nam phù hợp trước khi cân nhắc chức năng khuyến nghị.

## 6. Allowlist cụ thể — đề xuất HTML, chưa tải

Đợt đầu tối đa **21 URL HTML dưới đây**, đều đã đọc. Đây là danh sách ứng viên cho nghiên cứu văn bản; chưa phải xác nhận mọi mục có quyền dịch/phân phối. `decision` trong inventory dùng đúng cùng tập URL. Mục lục phục vụ provenance; Authors phục vụ attribution; không tạo claim bệnh từ hai trang ấy.

| STT | URL cuối dùng cho allowlist | Vai trò |
| --- | --- | --- |
| 1 | [Introduction](https://ipm.ucanr.edu/agriculture/tomato/introduction/) | growth_stage_framework |
| 2 | [Preplanting](https://ipm.ucanr.edu/agriculture/tomato/preplanting/) | growth_stage_care |
| 3 | [Planting to Prebloom](https://ipm.ucanr.edu/agriculture/tomato/planting-to-prebloom/) | growth_stage_care |
| 4 | [Bloom to Early Fruit Set](https://ipm.ucanr.edu/agriculture/tomato/bloom-to-early-fruit-set/) | growth_stage_care |
| 5 | [Late Fruit Set](https://ipm.ucanr.edu/agriculture/tomato/late-fruit-set/) | growth_stage_care |
| 6 | [First Red Fruit](https://ipm.ucanr.edu/agriculture/tomato/first-red-fruit/) | growth_stage_care |
| 7 | [Harvest and Postharvest](https://ipm.ucanr.edu/agriculture/tomato/harvest-and-postharvest/) | growth_stage_care |
| 8 | [Variety Selection](https://ipm.ucanr.edu/agriculture/tomato/variety-selection/) | conditional_general_care |
| 9 | [Fertilization](https://ipm.ucanr.edu/agriculture/tomato/fertilization/) | conditional_general_care |
| 10 | [Irrigation of Processing Tomatoes](https://ipm.ucanr.edu/agriculture/tomato/irrigation-of-processing-tomatoes/) | conditional_general_care |
| 11 | [Crop Rotation](https://ipm.ucanr.edu/agriculture/tomato/crop-rotation/) | conditional_general_care |
| 12 | [Whiteflies](https://ipm.ucanr.edu/agriculture/tomato/whiteflies/) | vector_context |
| 13 | [Bacterial Spot](https://ipm.ucanr.edu/agriculture/tomato/bacterial-spot/) | specific_disease |
| 14 | [Early Blight](https://ipm.ucanr.edu/agriculture/tomato/early-blight/) | specific_disease |
| 15 | [Late Blight](https://ipm.ucanr.edu/agriculture/tomato/late-blight/) | specific_disease |
| 16 | [Tobacco Mosaic](https://ipm.ucanr.edu/agriculture/tomato/tobacco-mosaic/) | broad_virus_group |
| 17 | [Tomato Yellow Leaf Curl](https://ipm.ucanr.edu/agriculture/tomato/tomato-yellow-leaf-curl/) | specific_disease |
| 18 | [Authors and Credits](https://ipm.ucanr.edu/agriculture/tomato/authors-and-credits/) | publication_authorship |
| 19 | [Tomato](https://ipm.ucanr.edu/agriculture/tomato/) | index |
| 20 | [Cultural Tips for Growing Tomato](https://ipm.ucanr.edu/home-and-landscape/tomato/cultural-tips/index.html) | general_garden_care |
| 21 | [Spider Mites](https://ipm.ucanr.edu/home-and-landscape/spider-mites/) | broad_pest_group |

Không có ảnh, PDF hoặc link đệ quy trong đợt này. Gray Mold/Russet Mite chỉ metadata loại nhầm mapping; Home index/About chỉ nghiên cứu phương pháp. 95 link mục lục chưa mở không thuộc allowlist. Các URL quyền/robots ở mục 1 chỉ dùng preflight, không là nội dung corpus. URL original/canonical/final nằm trong inventory; canonical là chuẩn hóa để dedup, không khẳng định đã kiểm HTML rel=canonical.

### Điều kiện trước và giới hạn vận hành

1. Người dùng chọn mục đích/phạm vi bước sau. Với từng item, ghi quyền riêng cho personal research, academic original copy, extraction/adaptation, translation, redistribution, image ML. Xem notice từng tài nguyên; chưa rõ quyền chỉ giữ metadata. Không tự chuyển `unknown` thành `allowed`; không gán CC0 hoặc CC chung cho domain. Đợt nghiên cứu cá nhân không đồng nghĩa quyền phát hành.
2. Kiểm lại robots/điều khoản trước đợt mới; áp đúng host và path, phân biệt hoa/thường. `/PDF` không suy thành mọi `/pdf`; đợt này không lấy PDF. Redirect tối đa 3 hop trong host/phạm vi được chấp thuận; đích mới ngoài allowlist vào review queue. Không lấy tài nguyên qua đường phụ để né chặn.
3. User-agent đề xuất: `TomatoAI-AcademicSourceSurvey/1.0 (local academic research; bounded text collection)`. Nếu có địa chỉ liên hệ chính thức được người dùng cung cấp, thêm đúng địa chỉ; không bịa danh tính/liên hệ. **Một request tại một thời điểm**, chờ **5 giây sau khi hoàn tất** trước request kế; không tải tài nguyên phụ của HTML.
4. Timeout **30 giây/request**; tối đa **2 MiB bytes HTML/item**, **50 MiB/đợt**, tối đa 21 tài nguyên payload. Kiểm Content-Type, giới hạn streaming/decompressed body, từ chối attachment/media hoặc response quá lớn; không lưu page lỗi làm snapshot thành công. Các số này là đề xuất của dự án, không phải UC quy định.
5. Tối đa **2 lần thử lại sau lần đầu**, chỉ cho timeout/lỗi kết nối tạm hoặc 5xx; backoff **10 rồi 30 giây**, thêm jitter nhỏ. Với 429/Retry-After, dừng batch và tôn trọng thời gian HTTP-date/seconds; nếu chờ vượt budget thì lưu checkpoint và kết thúc, không tranh thủ gửi URL khác. 403/CAPTCHA/robots deny: dừng, ghi blocker, không retry để vượt chặn. Không đổi proxy/user-agent giả, đăng nhập hay tạo tài khoản.
6. Dùng cache ETag/Last-Modified khi có. 304 chỉ hợp lệ khi đã có bytes cache trước đó và hash tương ứng; không tạo nội dung/hash từ response rỗng. Lần tải mới ghi UTC timestamp có timezone, final URL, status, Content-Type/charset, bytes, ETag/Last-Modified; header ngày khác `content_updated`.
7. Chỉ sau khi đợt sau được chọn và có quyền tương ứng, dùng nhánh mới trong root thực: `data/TomatoAI/data/raw/uc-ipm-tomato/<run>/` cho snapshot bất biến và `data/TomatoAI/data/processed/uc-ipm-tomato/<run>/` cho dẫn xuất. Không ghi vào các run đã chốt; hiện chưa tạo hai thư mục ấy. Inventory hiện tại chỉ metadata, `snapshot_sha256=null` vì chưa lưu bytes corpus.
8. Nếu muốn dịch/phát hành hoặc lấy ảnh train/test, chuẩn bị câu hỏi quyền cụ thể: URL, loại tài nguyên, phần trích/chỉnh/dịch, mục đích học thuật, app/repo/demo và mức công khai. Xin xác nhận qua đầu mối C trong lượt được ủy quyền riêng. Hiện chưa gửi email/form.

## 7. Schema tối thiểu và tương thích dữ liệu hiện có

Đối chiếu thực tế: card chuẩn hóa hiện có envelope `schema_version=1.0`, `record_id`, `content_language`, `source.file/pointer/sha256/disease_id_original`, `content_en`, `normalizations`, `flags`, `review.domain/translation/safe_for_advice/ready_for_training`. Ledger có `claim_id/card_id/canonical_condition_id/pointer/text_en/kind/source_sha256/card_sha256/source_check/evidence/required_context/domain_review/translation_review/display_allowed` và hash/reviewer bản dịch.

Đề xuất **sidecar provenance/evidence theo nguồn**, không sửa envelope card PEX hoặc origin `source.sha256` của PlantExpert. Nguồn UC mới giữ ID riêng; claim hiện có tham chiếu UC trong evidence dẫn xuất phiên bản mới ở lượt sau. Report schema hiện tại là schema khảo sát, không coi đã trở thành schema ingestion được đăng ký.

| Nhóm | Trường tối thiểu và quy tắc |
| --- | --- |
| Source identity | `source_id`, `publication_id`, `document_part`, `representation`, `original_url`, `canonical_url`, `final_url`, `title`. ID ổn định gợi ý `ucipm:3470:tomato:early-blight`; không lấy số thứ tự TOC làm ID corpus dài hạn. |
| Truy vết cấu trúc | `section_title`, `section_path`, `anchor` nếu có trên HTML; `source.file/pointer/sha256` trỏ snapshot thực. Không bịa anchor hoặc PDF page chưa đọc. |
| Attribution | `authors`, `authors_scope`, `authors_url`, `contributors`, `copyright_notice`, `credits`, `attribution_text`, `license_url`. Roster cả ấn phẩm không thành tác giả/reviewer từng claim. |
| Ngày/version | `accessed_at` UTC/timezone; `updated_original`, `reviewed_original`, `parsed_date`, `date_precision`, `date_parse_status`; `snapshot_id`, `version`, `sha256`, `etag`, `last_modified`. Chuỗi mơ hồ để nguyên, parsed null; hash chỉ có sau bytes thực. |
| Mapping | `canonical_condition_id` lấy đúng mapping hiện hữu, `label_original`, `agent_original`, `agent_normalized_candidate`, `identity_relation`, `mapping_evidence`, `mapping_review`. Tách đúng bệnh / bao quát nhóm / nguyên tắc / chưa đủ căn cứ / chưa tìm thấy; không sửa nhãn ảnh hoặc thêm lớp. |
| Claim và provenance | Giữ `claim_id`, `card_id`, `pointer`, `text_en` nguyên bản đối với claim PEX; UC evidence có `source_id/snapshot_sha256/section/locator` và đoạn ngắn EN nếu được phép. `claim_sha256` bám EN; ghi `kind` và kết quả hỗ trợ/thiếu/mâu thuẫn theo claim, không gán uy tín nguồn thành accepted. |
| Điều kiện áp dụng | `required_context`: geography, climate/weather, production_system, processing/fresh_market, garden/field/greenhouse, cultivar, soil, growth_stage, irrigation, pest_incidence, host/vector. Trường không biết null; cần nhập thực địa hoặc duyệt riêng, không đoán từ nhãn lá. |
| Quyền theo mục đích | `rights_source_url`, `rights_checked_at`, `rights_status_by_use`, `rights_scope`, `restrictions`, `permission_evidence`. Giữ archived/current và quyền bên thứ ba; boolean chung không đủ. |
| Ba review độc lập | `source_check` + evidence/reason; `domain_review/domain_reviewer`; `translation_review/translation_reviewer` và hash phiên bản. Duyệt nguồn không bằng duyệt chuyên môn/bản dịch; chưa có reviewer để null. |
| Hiển thị/rủi ro | `risk_flags`, `display_allowed=false`, `safe_for_advice=false` cho bản dự thảo hiện tại. `chemical`, numeric dose, disinfection recipe, destructive action, context_conflict tách khỏi tập dự kiến demo; giữ nguyên bằng chứng nguồn. |
| Việt hóa | `text_vi=null` cho tới bước dịch được chọn và có quyền; `translation_version`, `glossary_version`, `translation_source_sha256/translation_claim_sha256/translation_sha256`, lịch sử sửa và quyết định reviewer. Không gọi API dịch/AI. |

Không tạo schema/pipeline mới trong sản phẩm ở lượt này. Sidecar tương lai chỉ bổ sung evidence, không thay nguồn PEX thành UC bằng cách ghi đè hash/card ID. Bằng chứng cũ và mới cùng tồn tại; conflict không mất đi khi source-check mới.

## 8. Cleaning đề xuất và review queue

1. **Giữ snapshot nguyên bản** nếu được phép thu thập. Dẫn xuất normalized có lineage/version/hash riêng; không sửa raw hoặc credit để làm parser dễ hơn. BOM/charset lấy từ response và kiểm UTF-8; lỗi decode vào queue, không dùng replacement character rồi coi thành công.
2. **Tách chrome khỏi content:** menu, footer lặp, scripts, tracker/iframe, form/feedback, nút điều hướng. Copyright/credits/disclaimer/footer citation được tách metadata trước khi bỏ phần giao diện. Không kích hoạt JavaScript, tracker hay tự fetch ảnh qua HTML.
3. **Bảo toàn cấu trúc và nghĩa:** headings/path, list/order, emphasis có nghĩa, tên khoa học, negation, modal như if possible/might, điều kiện và đơn vị. Không tự đổi độ/acre/lb, ngày California, crop names, tỷ lệ hoặc lịch can thiệp sang Việt Nam. Không sửa typo/đơn vị mâu thuẫn bằng suy đoán; ghi queue.
4. **Bảng:** giữ row/cell, header nhiều cấp, row/col span và footnote liên quan. Phân biệt dấu gạch, missing, label-dependent rate và số 0. Amount/REI/PHI/mode-of-action/comment không được thành câu rời mất nhãn. Giữ table raw + representation dẫn xuất khi có quyền; tránh flatten làm lẫn sản phẩm/liều/chú thích.
5. **Phân loại hướng dẫn:** observation, symptom/agent, preventive/cultural, biological, chemical và nội dung định lượng/rủi ro. Organic không tự thành nonchemical. Nội dung hóa học giữ trong evidence corpus nhưng không vào tập dự kiến hiển thị. Câu trộn vệ sinh + bleach vẫn giữ cả câu held; muốn tách thành claim mới phải version hóa và review riêng, không xóa vế rủi ro rồi tự nâng claim cũ.
6. **Không đếm nguồn hai lần:** một publication/edition/part có thể có HTML và PDF; redirect/fragment/representation không thành bằng chứng độc lập. Publication 3470 có nhiều part, không collapse mọi trang bệnh thành cùng record. Dùng final/canonical đã kiểm, snapshot checksum và lineage; giống title hoặc cùng publication không đủ để gộp hai bệnh. Cùng source đã có trong ledger được coi tái kiểm, không thêm phiếu độc lập.
7. **Queue rõ lý do:** broken link/403/429, unknown redirect/rights, encoding/parser failure, thiếu section/agent, bảng mất cell/footnote, ngày mơ hồ, tác nhân/host sai, context conflict, version mới khác. Ghi ID, URL, section/pointer, lỗi, version, status, reviewer=null và next action; không tự impute phần thiếu hoặc đổi status để đạt kiểm tra.
8. **Version/update:** snapshot mới không ghi đè cũ; diff theo section/claim, đánh dấu evidence/bản dịch phụ thuộc version cũ cần tái kiểm. HTTP Last-Modified chỉ tín hiệu phục vụ; không thay ngày nội dung hoặc ngày peer review.
9. **Kiểm bản trích:** đối chiếu mẫu HTML/normalized ở những trang đã chọn, nhất là bảng và câu có điều kiện. Kiểm unique IDs, URLs, số trang allowlist, provenance/hash, condition ID và claim EN, quyền từng mục đích, charset, dấu phủ định/đơn vị/footnote và trường null. Chỉ gọi `cleaned_technical` khi kiểm kỹ thuật pass; không gọi training-ready hoặc advice-ready.

## 9. Việt hóa và demo tham khảo khi chưa có chuyên gia riêng

Bước sau có quyền chuyển ngữ mới dịch từng claim được chọn **thủ công/offline**, bám EN và version. Dùng `glossary-vi-draft.json` hiện có làm ứng viên, không coi thuật ngữ đã duyệt. Giữ TMV/ToMV riêng, oomycete riêng fungal, spider mite riêng russet, leaf mold riêng gray mold; tránh dịch mọi blight thành cùng tên. Người kiểm EN–VI đối chiếu negation, điều kiện, uncertainty, đơn vị và thuật ngữ với source; không tự khai người kiểm ngôn ngữ là chuyên gia nông học. Không dịch hàng loạt hoặc dùng API.

**Tiêu chí đề xuất cho artifact demo giáo dục riêng:**

- Quyền lưu/biên soạn/chuyển ngữ/phân phối đúng mục đích đã xác định theo item, attribution và version truy vết được.
- Identity/claim có nguồn và section cụ thể, context áp dụng đầy đủ; missing/broad/pending không biến thành chẩn đoán chắc chắn. Mâu thuẫn chưa giải quyết thì không đưa claim ấy vào demo.
- Chỉ nội dung quan sát/nguyên tắc ít rủi ro đã đối chiếu; chưa gồm thuốc/liều/bleach, treatment threshold, tưới/phân tự tính, lịch điều trị, nhổ cây theo CNN hoặc tối ưu năng suất. Phi hóa học vẫn phải đánh giá ngữ cảnh/rủi ro.
- Bản VI được kiểm độc lập với source-check; hiển thị nguồn/ngày/phạm vi và nhãn rõ “tham khảo học tập; chưa được chuyên gia riêng của dự án duyệt”. Không dùng logo peer review để tạo cảm giác ứng dụng được chuyên gia duyệt.
- `project_expert_review=pending`, reviewer=null vẫn đúng. Artifact demo tham khảo là đề xuất cho lượt riêng có quyết định rõ; **không sửa policy/safe_for_advice/display gate hiện tại**, không mở guidance thật bằng report này.

Tra cứu tĩnh theo canonical condition ID đáp ứng mục tiêu offline; không cần RAG/vector database/mô hình sinh. Kiến thức website không thành nhãn ảnh, severity ground truth hoặc chứng cứ EfficientNet/ResNet50 nhận diện đúng.

## 10. Phần chưa kiểm chứng và điểm dừng

95 URL mục lục chưa đọc; PDF/media chưa tải; ba bệnh còn thiếu trang tomato phù hợp sau khảo sát giới hạn. Lượt riêng có thể khảo sát tiếp nguồn extension chính thức cho ba bệnh, ưu tiên đối chiếu tài liệu đã có, không tự tạo phần thiếu.

Quyền từng HTML/PDF/media, bản dịch/phân phối demo và ML còn cần xác minh. California/fresh-market/processing/garden/greenhouse, tác nhân cũ và ngày cập nhật mơ hồ cần review; chưa kiểm quy định thuốc Việt Nam. Không dùng điều khoản archived để khẳng định quyền hiện hành mọi mục đích.

Hiện đã dừng ở metadata, đánh giá và kế hoạch. Chưa tạo corpus raw/normalized, chưa tải ảnh/PDF, chưa dịch, chưa merge registry, chưa train và chưa chạy BMAD. Kiểm tra báo cáo dùng `survey.py verify`; không chạy test sản phẩm/E2E vì không đổi sản phẩm. Kết quả và giới hạn kiểm chứng được ghi ở `verification.json` và README.
