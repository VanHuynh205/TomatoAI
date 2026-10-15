# Đánh giá UC IPM Tomato cho TomatoAI

Phiên bản: **ucipm-20261014-v1**. Khảo sát ngày **2026-10-14**, múi giờ Asia/Bangkok. Phạm vi: khảo sát nguồn chính thức, đối chiếu metadata/claim và đề xuất bước sau. Đây không phải corpus đã thu thập, bản dịch, nhãn ảnh được thẩm định hoặc xác nhận chuyên gia đã duyệt ứng dụng.

## 1. Kết luận theo mục đích

| Mục đích | Kết luận | Căn cứ và điều kiện |
| --- | --- | --- |
| Nguồn bằng chứng cho kho kiến thức | **Phù hợp có điều kiện** | PMG có tác nhân, triệu chứng, quản lý và nguồn tác giả. Bổ sung đối chiếu theo từng claim, giữ địa bàn/hệ canh tác; không nâng trạng thái chỉ vì tên tổ chức. |
| Kho hướng dẫn tiếng Việt chạy offline | **Phù hợp có điều kiện** | Có thể tổ chức lookup theo condition ID. Cần xác minh quyền đối với tài nguyên và bản dịch/phân phối; đối chiếu ngữ cảnh Việt Nam, kiểm bản dịch và duyệt nội dung riêng. Hiện chưa đủ điều kiện đóng gói hướng dẫn thật. |
| Dữ liệu ảnh train/test | **Chưa đủ căn cứ** | Website hướng dẫn với ảnh minh họa, không cung cấp dataset ảnh tomato có schema, nhãn, split và quyền ML rõ ràng trong khảo sát này. Caption/credit không là ground truth. |

Nguồn là **website hướng dẫn IPM**, gồm HTML, liên kết ấn phẩm/PDF, ảnh minh họa và bảng quản lý. Không gọi toàn bộ website là dataset huấn luyện chuẩn hóa. [Tomato PMG](https://ipm.ucanr.edu/agriculture/tomato/), [Authors and Credits](https://ipm.ucanr.edu/agriculture/tomato/authors-and-credits/).

## 2. Hiện trạng dự án được đối chiếu

Dataset root thực tế là `data/TomatoAI/data`, trong workspace `C:/Users/admin/Downloads/DACN_CayCaChua`. Thư mục ngoài `data/TomatoAI` chứa cấu trúc hiện hữu; không tạo thêm một dataset root lồng mới.

- [Registry hiện hành](../../../dataset-registry.json): PlantVillage run `pv-d9e4c21eec8e9172`, manifest 18.160 record thuộc 10 nhãn; 18.146 bản ảnh giữ lại, 14 record trùng bytes loại khỏi bản giữ. Coverage dùng **toàn manifest**, không nhầm record nguồn với số ảnh retained.
- [Integration hiện hành](../../integration/ir-20261014-v1/README.md): 9/10 mapping `exact_source_checked`, ToMV/TMV `candidate_pending`. Đây là đối chiếu khái niệm nguồn/card, không chứng minh nhãn từng ảnh. `class-manifest.proposed.json` vẫn là đề xuất; chưa có checkpoint classifier/class order chính thức được duyệt.
- PlantExpertVQA-tomato run `pex-b3da04d66a031756`: 17 card parse/schema hợp lệ, 172 management claim. Ledger ghi 26 `source_checked_candidate`, 34 `partial_support_context_pending`, 107 `unverified`, 5 `held_specific_risk`; tất cả vẫn chưa được mở hiển thị.
- `domain_review=pending`, bản dịch chưa duyệt, `safe_for_advice=false`, `training_ready=false` vẫn giữ nguyên. Không ghi lại registry, policy, mapping, claim ledger hay bundle lookup.
- Đọc [kế hoạch bản địa hóa/giáo dục](../../../../../../planning/tomato-desktop/knowledge-localization-edtech.md) để giữ ranh giới demo tham khảo và hướng dẫn đã duyệt. Không nhập hay chạy workflow triển khai BMAD. WUR/Dryad/Mendeley không được dùng để mở rộng sang tối ưu năng suất.

`docs/agents/domain.md` được AGENTS.md dẫn tới nhưng không tồn tại trong checkout tại thời điểm khảo sát. Đã dùng registry, integration và tài liệu planning hiện có; không tự tạo tài liệu domain thay thế.

## 3. Phạm vi đọc và giới hạn bằng chứng

Đọc **26 URL nội dung/metadata duy nhất**: **25 trang đọc sâu** và **1 trang caption/credit ảnh**. Trong 25 có hai mục lục và trang About PMG; không phải 25 bài bệnh. Đọc thêm **7 URL quyền/robots** riêng: tổng **33 URL duy nhất thực đọc**. URL permissions redirect được đếm một tài nguyên cuối; trang About không được đếm lại vào quyền.

Mục lục Tomato có **115 liên kết** trong vùng nội dung: 8 Year-Round, 6 General Management, 24 Invertebrates, 34 Plant Diseases, 1 Nematodes, 6 Weeds, 26 Supplemental, 2 Tools, 5 Resources, 1 Emerging Pests, 2 Publication Information. Nhóm Plant Diseases gồm cả trang tổng quan fungicide, không suy thành 34 bệnh. Đã đọc sâu **20 liên kết mục lục**; **95 liên kết chưa mở**. Inventory có **128 URL duy nhất**, gồm mục lục, link phát hiện và các nguồn bổ sung/quyền.

Giữ dưới giới hạn 30 trang sâu. Thực hiện bảy truy vấn chính thức giới hạn domain/tomato, ghi trong `search_log`. Search snippet chỉ để phát hiện; kết luận dựa mục lục và nội dung gốc đã mở. Không crawl đệ quy. Không tải bộ ảnh/PDF, không lưu toàn văn website; một request HTTP mục lục chỉ dùng trích metadata liên kết rồi bỏ HTML khỏi bộ nhớ.

Danh mục đầy đủ, trạng thái truy cập và quyết định chọn nằm trong [source-inventory.json](source-inventory.json). Các URL `not_opened` chưa được chứng minh truy cập được hoặc có nội dung phù hợp. Web reader không cung cấp HTTP status thì ghi null, không tự gán 200.

## 4. Phủ lớp ảnh và các nhầm lẫn cần giữ

[coverage-matrix.csv](coverage-matrix.csv) có **10 dòng**, giữ nguyên từng `label_original`, canonical ID và số record từ manifest. Mức hỗ trợ: **4 đúng bệnh**, **2 trang bao quát nhóm tác nhân**, **1 chăm sóc Healthy**, **3 chưa tìm thấy trang đặc hiệu**. Vì vậy **7/10 có hỗ trợ theo mức khác nhau**, không phải 7 mapping chính xác được duyệt.

**Đúng bệnh:** Bacterial Spot, Early Blight, Late Blight, Tomato Yellow Leaf Curl. Bacterial Spot dùng tên trên UC `Xanthomonas campestris pv. vesicatoria`; card dùng complex Xanthomonas. Khớp bệnh không xác nhận mọi loài/strain tương đương. Late Blight là `Phytophthora infestans`; giữ phân biệt oomycete với nhãn phân loại fungal cũ trong card, không sửa raw. Nội dung triệu chứng chỉ là tài liệu tham khảo, không xác nhận mô hình phân biệt được bệnh qua ảnh. [Bacterial Spot](https://ipm.ucanr.edu/agriculture/tomato/bacterial-spot/), [Early Blight](https://ipm.ucanr.edu/agriculture/tomato/early-blight/), [Late Blight](https://ipm.ucanr.edu/agriculture/tomato/late-blight/), [TYLCV](https://ipm.ucanr.edu/agriculture/tomato/tomato-yellow-leaf-curl/).

**Bao quát nhóm:** Tobacco Mosaic ghi cả Tobacco mosaic virus và Tomato mosaic virus. Điều này không chứng minh TMV = ToMV hoặc ảnh `Tomato___Tomato_mosaic_virus` đúng virus. Trang nêu lây cơ học và loại insect/nematode/fungal vectors cho nhóm tobamovirus; giữ mapping pending. Spider Mites bao quát Tetranychus với tên thường twospotted; scientific name `Tetranychus urticae` của lớp hiện có không được xác minh chỉ bằng caption. [Tobacco Mosaic](https://ipm.ucanr.edu/agriculture/tomato/tobacco-mosaic/), [Spider Mites](https://ipm.ucanr.edu/home-and-landscape/spider-mites/).

**Healthy:** nối nguyên tắc chăm sóc vườn, đất thoát nước và quan sát nhu cầu nước. Lá nhìn khỏe không chứng minh toàn cây/đất/phân/nước đều phù hợp; không nối sang bài điều trị bệnh. [Cultural Tips](https://ipm.ucanr.edu/home-and-landscape/tomato/cultural-tips/index.html).

**Thiếu:** Leaf Mold (`Passalora fulva`), Septoria leaf spot (`Septoria lycopersici`), Target Spot (`Corynespora cassiicola`) không thấy trong hai danh mục đã đọc; chưa tìm thấy trang tomato phù hợp sau tìm kiếm giới hạn. Chưa xác nhận toàn UC IPM không có. Giữ bằng chứng UMN, UMD, UF/IFAS trong ledger; những nguồn cũ ấy không được mở lại trong lượt này. Hit “leaf mold” vật liệu cải tạo đất và Septoria của cây khác không dùng làm nguồn bệnh cà chua.

Gray Mold là `Botrytis cinerea`, không thay Leaf Mold. Tomato Russet Mite là `Aculops lycopersici`, không thay two-spotted spider mite. Early Blight không thay Target Spot. Hai trang gần tên được giữ **metadata so sánh**, loại khỏi allowlist nhập kiến thức theo nhãn. Không thêm lớp classifier từ website. [Gray Mold](https://ipm.ucanr.edu/agriculture/tomato/gray-mold/), [Tomato Russet Mite](https://ipm.ucanr.edu/agriculture/tomato/tomato-russet-mite/).

## 5. Nội dung nên chọn và giới hạn áp dụng

Ưu tiên triệu chứng/tác nhân có cảnh báo nhầm lẫn; nguyên tắc cây giống sạch, vệ sinh, quản lý volunteer/weed hosts, theo dõi sâu bệnh và bảo tồn thiên địch có điều kiện. Không coi mọi “organic” là phi hóa học: copper, oil, soap và các bảng treatment vẫn cần cờ rủi ro.

Khung Year-Round được UC xác định cho **California processing tomatoes**. Chỉ đề xuất nguyên tắc quan sát theo giai đoạn; lịch, ngưỡng treatment, thị trường và môi trường cụ thể không tự chuyển sang Việt Nam. [Introduction](https://ipm.ucanr.edu/agriculture/tomato/introduction/).

| Giai đoạn đã đọc | Nội dung có thể khảo sát để biên soạn sau |
| --- | --- |
| [Preplanting](https://ipm.ucanr.edu/agriculture/tomato/preplanting/) | Lịch sử ruộng, đất, chọn giống và vấn đề trước trồng. |
| [Planting to Prebloom](https://ipm.ucanr.edu/agriculture/tomato/planting-to-prebloom/) | Kiểm cây giống, theo dõi sớm và ghi nhận vấn đề. |
| [Bloom to Early Fruit Set](https://ipm.ucanr.edu/agriculture/tomato/bloom-to-early-fruit-set/) | Quan sát, vệ sinh và ghi chép trong giai đoạn hoa/đậu quả. |
| [Late Fruit Set](https://ipm.ucanr.edu/agriculture/tomato/late-fruit-set/) | Theo dõi biểu hiện trên lá/quả, giữ điều kiện crop stage. |
| [First Red Fruit](https://ipm.ucanr.edu/agriculture/tomato/first-red-fruit/) | Quan sát gần thu hoạch; không chuyển PHI thành lịch thuốc của ứng dụng. |
| [Harvest and Postharvest](https://ipm.ucanr.edu/agriculture/tomato/harvest-and-postharvest/) | Ghi nhận tổn hại/lịch sử vụ và vệ sinh cho vụ sau. |

[Fertilization](https://ipm.ucanr.edu/agriculture/tomato/fertilization/) dựa đất/tissue test và giai đoạn. [Irrigation of Processing Tomatoes](https://ipm.ucanr.edu/agriculture/tomato/irrigation-of-processing-tomatoes/) phụ thuộc đất, salinity, water table và ET; deficit/cutoff để điều chỉnh chất lượng/năng suất ngoài mục tiêu. [Crop Rotation](https://ipm.ucanr.edu/agriculture/tomato/crop-rotation/) giữ nonhost và thời lượng theo pest. [Variety Selection](https://ipm.ucanr.edu/agriculture/tomato/variety-selection/) có dữ liệu thị trường 2012; không lấy danh sách đó làm giống nên trồng hiện tại ở Việt Nam. Không tính liều nước/phân/thuốc từ nhãn bệnh.

[Whiteflies](https://ipm.ucanr.edu/agriculture/tomato/whiteflies/) bổ sung vector TYLCV và giới hạn mulch phản quang chỉ hiệu quả đầu vụ. Không biến kiểm soát vector thành chữa virus hoặc lịch can thiệp khi chỉ có ảnh lá.

## 6. Mẫu claim: 12/172, giữ trạng thái hiện hành

Phần `claim_sample` trong inventory là **bản đánh giá duy nhất ở cấp claim**: ID gốc, EN nguyên văn, pointer, bằng chứng cũ, section/URL UC, nhận xét khác biệt và điều kiện. Mẫu gồm **4 source_checked, 5 partial, 3 held**; không suy thành đã review tất cả 172 claim. Toàn bộ 26 claim có căn cứ ban đầu và 34 partial vẫn giữ nguyên trạng thái ngoài mẫu.

Các phát hiện ảnh hưởng quyết định:

- “Certified” trong claim Bacterial Spot vượt mức UC nêu pathogen-free/disease-free khi có thể. Nguồn UF/IFAS cũ và UC cùng hỗ trợ nguyên tắc, không tự xác nhận chứng nhận cây giống. Bảng Crop Rotation UC ghi **1 or more** cho bacterial spot; claim PlantExpert **3–4 năm** vẫn partial. Khác thời lượng không đủ để tự chọn bên đúng trong mọi đất/vùng.
- Các claim drip/khô lá có thêm căn cứ nguyên tắc từ Late Blight và garden care. Trang Early Blight mô tả free moisture nhưng không trực tiếp chứng minh toàn bộ công thức dùng drip của claim. Healthy “balanced fertilizer” vẫn cần soil test/ngữ cảnh; không thành hướng dẫn từ lớp Healthy.
- UC không cung cấp thêm bằng chứng bệnh đặc hiệu cho Leaf Mold, Septoria hoặc Target Spot trong phạm vi khảo sát. Điều kiện greenhouse/morning của claim Leaf Mold và số giờ leaf wetness của Target Spot không được giải quyết bằng trang chăm sóc chung.
- Claim aphid/insecticide cho mosaic mâu thuẫn nhóm tobamovirus không insect vector trên UC. Claim sanitation có bleach 10% chỉ được hỗ trợ vệ sinh chung, chưa xác minh công thức/thời gian tiếp xúc. Cả hai giữ held.
- Spider Mites Quick Tips thực sự có spray/mist **mặt dưới lá**; Cultural Control có rửa nước trong vườn/cây nhỏ. Không đồng nhất với tưới overhead tăng ẩm chung cho cà chua. Xung đột nguy cơ ướt lá với tomato care/Late Blight vẫn chưa giải quyết; giữ held.
- TYLCV host-free period là biện pháp **cấp vùng**, có thể hữu ích tùy agroecosystem/vùng thiếu mùa đông thực sự. Claim bỏ các điều kiện ấy vẫn partial. UC là nguồn đã có trong ledger cho TYLCV/spider mites; đọc lại không tạo thêm một nguồn độc lập để “bỏ phiếu”.

Không viết đè PlantExpert hoặc nguồn cũ. `domain_review=pending`, `translation_review=not_translated`, `display_allowed=false` cho mọi mẫu; bằng chứng source-check và duyệt chuyên môn là hai bước khác nhau.

## 7. Metadata, khả năng trích xuất và quyền

Tomato PMG là UC ANR Publication **3470**, citation “Revised continuously”; có authors theo nhóm, acknowledgments và nhiều trang hiện logo **UC Peer Reviewed**. Spider Mites là Publication **7405**, tác giả L.D. Godfrey. About PMG mô tả quy trình phản biện nhưng trang archived; không xác nhận từng trang mới được review gần đây, càng không thay duyệt riêng cho ứng dụng. [Authors](https://ipm.ucanr.edu/agriculture/tomato/authors-and-credits/), [About PMG](https://ipm.ucanr.edu/PMG/aboutpmg.html).

Giữ chuỗi updated nguyên bản như `12/13`, `09/16`, không đoán định dạng; parsed date null. Footer ©2026 và ngày HTTP không phải ngày cập nhật nội dung. Ngày từng trang chưa ghi nhận cũng để null, không tuyên bố trang không có ngày. Whiteflies có chú thích quy định California hiệu lực 2024 dù dòng updated `12/13`; bản snapshot sau này phải truy vết section/version thay vì tin một ngày cho toàn trang.

HTML có menu/footer/iframe Google Tag Manager, heading/list, liên kết caption và bảng với header nhiều dòng, cell nối tiếp, REI/PHI, đơn vị và chú thích. Trích xuất text khả thi nhưng parser cần bảo toàn liên kết giữa cell/footnote và điều kiện. Các PDF chưa tải/parse; không tuyên bố đã kiểm toàn bộ PDF. [Bacterial Spot, bảng và chú thích](https://ipm.ucanr.edu/agriculture/tomato/bacterial-spot/).

Ảnh kiểm ở mức trang caption/credit: [two-spotted adult](https://ipm.ucanr.edu/PMG/T/I-AC-TSPP-AD.022.html), Jack Kelly Clark, UC IPM; chưa lấy bytes ảnh. Không biết phân bố số ảnh/label, split, hash trùng hoặc quyền ML chỉ từ một ví dụ.

[acquisition-cleaning-plan.md](acquisition-cleaning-plan.md) ghi đầy đủ **năm trường hợp quyền**, điều khoản/section, redirect, archived và lỗi HTTP. Điểm quyết định: link Use Permissions từ Tomato trỏ chính sách IPM **archived**, trong khi UC ANR có notice/permissions hiện tại dẫn CC BY-NC-ND. Phạm vi cấp quyền từng HTML/PDF/media chưa được giải quyết. CC ND không tự cho chia sẻ bản dịch; không gán CC0 hoặc CC cho mọi tài nguyên công khai. [IPM Legal Notices](https://ipm.ucanr.edu/GENERAL/copyright.html), [UC ANR Copyright](https://ucanr.edu/copyright), [Permissions](https://ucanr.edu/dept/anr-publishing/permissions), [CC legal code](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en).

HTTP trực tiếp các trang UC ANR copyright/permissions có 403; web reader đọc được nội dung chính thức. Giữ cả bằng chứng và giới hạn, không vượt chặn hoặc tự gửi email. [robots.txt](https://ipm.ucanr.edu/robots.txt) không chặn tuyến agriculture tomato trong bản đọc; robots không thay giấy phép. Văn bản vẫn có thể dùng nghiên cứu có điều kiện dù quyền ảnh chưa rõ.

## 8. Kế hoạch bước sau và kiểm chứng báo cáo

Kế hoạch kèm **21 URL HTML cụ thể** đã đọc, ưu tiên văn bản theo nhãn và chăm sóc, không đệ quy/PDF/media. Có timeout, giới hạn dung lượng, backoff/Retry-After, cổng quyền theo mục đích, schema tương thích envelope/ledger hiện có, dedup publication/representation, cleaning giữ điều kiện và review queue. Việt hóa đề xuất có version, glossary và kiểm độc lập EN–VI; chưa dịch. Lookup condition ID đủ, không đề xuất RAG/vector database/mô hình sinh.

Skill thực dùng: **research** (`.agents/skills/research/SKILL.md`) làm workflow chính, nghiên cứu quyền được giao một background agent độc lập; **Ponytail full** (`.dsh/skills/ponytail/SKILL.md`) cho script kiểm báo cáo bằng Python stdlib; **superpowers:using-superpowers** cho discovery/routing, không khởi động workflow triển khai. Không dùng browser-harness/Playwright vì web reader và HTTP metadata đủ.

Kiểm tra bằng:

```powershell
C:\Python314\python.exe data/TomatoAI/data/reports/uc-ipm-tomato/ucipm-20261014-v1/survey.py verify
```

Kết quả thực chạy lưu trong [verification.json](verification.json): parse JSON/CSV, unique ID/URL, 10 nhãn/ID/count đúng manifest, 12 EN/pointer/status đúng ledger, tham chiếu UC có inventory, allowlist chỉ trang đã đọc, Markdown local links tồn tại, UTF-8, và so sánh baseline các đầu vào được bảo vệ. Raw/processed kiểm file list/size/mtime; SHA-256 dùng cho control/review/planning, không tuyên bố rehash toàn bộ media. Không kiểm lại HTTP của 95 link chưa mở, không chạy test sản phẩm/pipeline/E2E vì không sửa sản phẩm.

Điểm dừng: báo cáo và đề xuất hoàn tất khi verifier pass. Chưa tải nguồn vào raw, chưa cleaning, chưa merge registry, chưa train, chưa mở hướng dẫn hoặc chạy BMAD. Bước thu thập tiếp theo cần phạm vi người dùng chọn và quyền tương ứng.
