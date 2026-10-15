# Bảo mật, độ ổn định và kiểm thử — chỉ mức kế hoạch

**Cập nhật Setup 13/10/2026:** tên đã chốt “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”; phạm vi nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50. Không tối ưu canh tác; WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung. Runtime đã setup; tài liệu vẫn là draft chưa tiếp nhận chính thức, xem [README](README.md) và [setup-report](setup-report.md).

Ngày 13/10/2026. Chưa có code sản phẩm để audit; **không chạy SAST, Semgrep, pentest hoặc E2E ứng dụng**. Đây là threat/design/test plan, không báo cáo audit code. Khảo sát dữ liệu chỉ đọc đã thực hiện được ghi riêng trong data-audit.

## Tài sản, đầu vào và boundary

Tài sản: ảnh gốc của người dùng, raw nghiên cứu, checkpoint/labels/preprocessing, KB EN/VI/source/review, configs/history nếu có, khả năng đáp ứng CPU/RAM, kết quả và provenance. Ảnh file local vẫn là input không tin cậy; model/KB từ ngoài hoặc bundle bị hỏng là boundary quan trọng dù offline. Không có service mạng, WAF, Fail2Ban hoặc chống DDoS trong kiến trúc này.

Boundaries: filesystem ảnh → decoder worker; bundle model/KB → loaders; GUI → worker IPC; application → user config/history. Không nhận archive/model/user KB tùy ý trong MVP. Giáo dục/care đúng và sai số phân loại không được giải quyết chỉ bằng hardening phần mềm.

## Ma trận rủi ro

| Rủi ro | Điều kiện áp dụng | Biện pháp thiết kế | Module/story liên quan | Test dự kiến | Rủi ro còn lại |
| --- | --- | --- | --- | --- | --- |
| File hỏng/đuôi giả/decoder exception | Người dùng chọn ảnh local | Magic+decode, allow JPEG/PNG, lỗi typed, worker boundary, patch decoder | Inference/UI S06,S14 | T02 | Lỗi native decoder chưa biết; không có sandbox tuyệt đối |
| Decompression bomb/ảnh cực lớn | Bytes nhỏ nhưng pixel rất lớn, dimensions bất thường | 20 MiB, 24 MP, cạnh dài 12.000, cạnh ngắn 64 đề xuất; pixel check trước full decode; không disable bomb warnings | Inference S14 | T03 | Threshold có thể chặn ảnh hợp lệ; cần benchmark |
| Multi-frame/EXIF/mode khác RGB | Animated PNG/mode/rotation/metadata | MVP một frame rõ policy, orientation xử lý bản tạm, RGB normalize, không ghi EXIF vào log | Inference S06,S14 | T01,T02,T18 | Decoder/library behavior thay version |
| Nhấn chạy liên tục gây treo | Job đang load/infer | 1 worker/1 active/0 queued; disable chạy; bounded IPC; resource budget | UI/Inference S06,S14 | T10,T11 | CPU/thermal phụ thuộc máy; OS chưa kiểm |
| Hủy không dừng native op, stale result | Người dùng hủy/đổi ảnh, worker chậm | request identity; cancel giữa stages; grace 2 s/timeout 15 s đề xuất; terminate/restart worker của app | UI/Inference S14 | T10 | Termination cần cleanup; timeout cold load phải thử |
| Checkpoint thực thi code không tin cậy | Tải/nạp model khác nguồn | First-party allowlisted architecture, tensor state dict, restricted weights_only phù hợp version; không full pickle/dynamic import | Inference/Package S01,S14,S18 | T12 | weights_only không chặn mọi DoS/memory corruption; hash không tự xác thực nguồn |
| Model/hash/schema/class order sai | Bundle hỏng/ghép version nhầm | SHA-256 manifest, shape/class/transform compatibility, fail closed; không repair bằng tải online | Inference S06,S14,S18 | T04,T12 | Kẻ thay cả manifest+binary vượt hash local; signing chưa chốt |
| Dependency/asset supply chain | Chuẩn bị môi trường hoặc package | Nguồn chính thức, pin version/hash, ledger/license notices; không remote code; quyền thường | Training/Package S01,S18 | T12,T13 | CVE và distribution rights cần kiểm ở phiên triển khai |
| Ghi file sai/chồng raw/traversal | Config/history, import/export nếu thêm | Raw read-only, paths resolve vào designated dirs; không import archive MVP; atomic write, không quyền admin | Data/Persistence S02,S14,S20 | T18 | Người dùng sửa filesystem bên ngoài app; backup phụ thuộc họ |
| Zip slip/archive bomb | Chỉ nếu future import archive được duyệt | Mặc định không có import; sau này kiểm canonical path/entries/size trước extract | Package/Persistence nhánh future | T18 mở rộng nếu scope đổi | Không claim đã test archive khi không hỗ trợ |
| Log/history lộ ảnh/path/EXIF | Logs hoặc history bật | Log mã lỗi/version/request id, không ảnh/base64/EXIF/path đầy đủ; opt-in, clear, permissions OS | UI/Persistence S14,S20 | T18 | Tài khoản/máy bị xâm nhập ngoài scope; local không đồng nghĩa bí mật tuyệt đối |
| Hết đĩa/worker crash/model thiếu | Máy clean, state dir lỗi | Error có recovery, giữ ảnh gốc, không partial result; limited tmp cleanup, validation bundle boot | Package/UI S14,S18 | T12,T18 | Antivirus/quyền filesystem tùy máy |
| App phụ thuộc tải online | Framework cache/weights/font/telemetry | Ship mọi asset cần; loader không fetch; không remote font/API/update; inspect network clean-machine | Package S18 | T13 | Third-party có hành vi mới cần kiểm theo version |
| Split leakage/nhóm sai | Cùng lá/trùng/biến thể qua tập | Group+duplicate component manifest, unresolved quarantine, split trước augment, fit train | Data/Experiments S03,S04 | T15 | Near-duplicate missed hoặc nguồn grouping sai vẫn cần review |
| Chọn winner/threshold bằng test | Mở test trong tuning | Khóa selection record/threshold/checkpoint C4, test cuối immutable, incident log | Experiments S09,S15 | T16 | Sai discipline người nghiên cứu không giải bằng phần mềm alone |
| Softmax cao nhưng ảnh OOD | Non-leaf/non-tomato/unseen condition/domain shift | Quality gates+validation policy, negatives độc lập, coverage/false accept; UI giới hạn, uncertain không advice theo nhãn | Inference/UX S09,S16 | T06,T17 | OOD không phát hiện hoàn hảo; hiện thiếu negatives/ground truth |
| Tri thức ghép sai/ID dangling | 24 link raw không khớp, alias bệnh giống tên | Canonical code mapping; alias review; không nearest keyword; validate bundle và suppress chưa rõ | Knowledge S10,S11 | T07,T08 | Taxonomy/source lỗi cần người chuyên môn |
| Dịch mất phủ định/đơn vị/điều kiện | Bản VI dẫn xuất | EN–VI aligned, glossary, claim source, reviewer/role/status/version; không dịch runtime | Localization S10,S11 | T09 | Chưa có reviewer nông nghiệp; ngôn ngữ đúng chưa đủ nội dung đúng |
| Hướng dẫn thuốc/rủi ro canh tác sai địa phương | Raw chemical hoặc thiếu điều kiện | Không thuốc/liều/cách ly thiếu nguồn phù hợp; suppress risky claims; source_checked demo label; expert scope gate | Knowledge/UX S11,S13 | T08,T09 | Nguồn khác vùng và người dùng hiểu quá mức; chưa chứng minh hiệu quả vườn |
| Kết quả bị hiểu là mức độ/năng suất/chẩn đoán xác nhận | Leaf classification/guidance | Nêu đúng lớp/phạm vi, không severity/yield/spread outputs; học giới hạn | UX/Report S12,S13,S19 | T14,T20 | Người dùng vẫn có thể bỏ qua giới hạn |

## Catalog kiểm thử dự kiến và expected assertions

Mỗi ID dưới đây có testcase triển khai sau; kết quả hiện tại đều **chưa chạy**. Các numeric limits phải được duyệt C1 rồi fixture kiểm đúng boundary, không tự nới để pass. Tests chất lượng khoa học/human review có tiêu chí minh bạch, không giả dùng unit test thay chuyên môn.

| Test | Fixture/thao tác | Expected assertion cụ thể | Yêu cầu liên quan |
| --- | --- | --- | --- |
| T01 | JPEG/PNG hợp lệ, uppercase extension, grayscale/RGBA được hỗ trợ, path có dấu; file picker cancel | Preview đúng ảnh/request identity, tensor RGB đúng shape 1×3×224×224; cancel có 0 inference job | FR01,FR02,NFR04 |
| T02 | File text giả JPG, JPEG truncated, unsupported/multi-frame theo policy | `invalid`, mã lỗi format/decode/frame; forward call count=0; không status_code healthy | FR02,NFR06 |
| T03 | Boundary bytes/pixel/dimension được khóa và fixture bomb | Trong limit hợp lệ; vượt bất kỳ limit → typed `invalid`; không full decode/tensor allocation vượt budget; UI còn đáp ứng | FR02,NFR06 |
| T04 | Golden class order/manifest, đổi order/schema/hash/10→9 labels | Mapping từng index đúng; bundle sai bị lỗi trước inference; không silent fallback | FR03,FR11,NFR09 |
| T05 | Cùng golden input/checkpoint qua eval pipeline và app worker | Preprocess và logits parity trong tolerance khóa (đề xuất atol/rtol 1e-5 CPU FP32 cùng version); accepted label đúng oracle; không severity/yield field | FR03,FR06,NFR05 |
| T06 | Policy fixture known-high/low score/margin, negative holdout có nhãn, unsupported ảnh | Rule fixture quyết định đúng status/reason; non-accepted có status_code null cho advice và 0 class-specific guidance; empirical OOD báo counts thật, không đòi 100% reject phi thực tế | FR04,NFR10 |
| T07 | 10 code, unknown code, bản record thiếu/not reviewed, wrong knowledge version | 10 lookup đúng knowledge_id/VI version; unknown/missing → knowledge_unavailable; không lấy bệnh gần tên; nguồn hiện offline | FR05,FR06,NFR08 |
| T08 | Context unknown/conflicting, hai top-k khác chỉ dẫn, chemical suppressed | Chỉ claim đúng conditions/approved_scope được render; không ghép top-k; 0 unsupported chemical/dose/PHI claims hiển thị | FR05,FR07,NFR08 |
| T09 | Golden EN–VI review checklist và metadata, glossary/schema/link validation | 100% claim hiển thị có source+actor+role+status+version; glossary/negation/unit issues trọng yếu không còn; raw hashes không đổi | FR08,NFR08 |
| T10 | Bấm chạy 20 lần, cancel/đổi ảnh trong inference, worker trả chậm, đóng app | Active ≤1, pending=0; request đã hủy/ảnh cũ có 0 render; worker được cleanup/restart đúng policy; không đụng process ngoài app | FR01,FR10,NFR06 |
| T11 | Model/package trên CPU reference, 10 warm-up+100 run, cold start và watchdog | Báo p50/p95/RSS/threads/load/job time; so mục tiêu đã duyệt; UI heartbeat đáp ứng, watchdog trả lỗi/hủy thay vì treo vô hạn | FR10,NFR02,NFR03 |
| T12 | Model state sai shape/hash, unsupported architecture/full-pickle fixture, model thiếu, worker crash | Loader từ chối artifact không allowlist/không tương thích; không execute payload; UI error có retry; không tải mạng hoặc gán nhãn thay thế | FR11,NFR06 |
| T13 | Windows sạch, user thường, offline, không Python/CUDA/cache; network observation | Launch→ảnh→guidance→lesson thành công; không remote download/upload/DNS do app; 0 dataset raw trong bundle; notices có; ghi bằng chứng test | NFR01,NFR02,FR14 |
| T14 | Lesson/quiz 10 thẻ được phép, từng lựa chọn đúng/sai và feedback | Đáp án đúng theo reviewed key, feedback có giải thích/source; LO1–LO3 được bao phủ; điểm quiz không lấy model confidence | FR09 |
| T15 | Split manifest/components/exclusion ledger/augmentation audit | Giao train/val/test group và duplicate-component = ∅; 10 code nhất quán; unresolved không bị split random; statistics fit chỉ train | FR12,NFR05 |
| T16 | Run registry, selection record trước final test, output metrics | Cùng split hash/budget hai model; config/policy/winner chốt trước test; đủ per-class support/confusion/macro-F1 và time; không chọn seed tốt nhất hậu test | FR12,FR14,NFR05 |
| T17 | External/challenge manifest, label provenance; pilot learning/usability | Không overlap nguồn/group với train/val; metric chỉ mẫu có ground truth; nhóm thiếu ghi N/A; pre/post/task counts tách ML; nếu không có mẫu ghi chưa đánh giá | FR14,NFR10 |
| T18 | Log review, read-only dirs/full disk, history on/off/delete nếu S20; package paths | Raw/input hash không đổi; log không ảnh/EXIF/full path; history off=0 records/images; delete chỉ state app được chọn; error không mất input | FR13,NFR07 |
| T19 | Tab/ShiftTab/Enter/Escape, 1280×720/1920×1080, DPI100/150/200%, chữ VI dài | Mọi thao tác chính dùng bàn phím, focus nhìn rõ; labels/sources không bị cắt; contrast đạt policy; status không chỉ qua màu | NFR04 |
| T20 | Report/model card/demo claims đối chiếu evidence | Ô chưa đo không được ghi số; winner/test/limitations khớp logs; không tuyên bố tối ưu canh tác, expert approval hoặc field validity thiếu bằng chứng | FR06,FR14,NFR10 |

## Cấp kiểm thử và kế hoạch công cụ

Unit: mapping/schema/state policy/paths/quiz; integration: preprocessing parity/model+knowledge contract/cancel identity; ML audit: split/selection/reproducibility/metrics; desktop E2E: file picker→prediction→source→lesson→cancel/error; clean-machine: bundle/offline/privacy. Human evaluation: nội dung nguồn/chuyên môn, usability và LO pre/post, độc lập auto-tests.

AGENTS yêu cầu sau code fixes dùng skill `.agents/skills/e2e/SKILL.md` và runner/config thật. **Khi triển khai** phải đọc skill/config trước kiểm affected flows; project hiện chưa có frontend URL hoặc `e2e.config.ts` được xác minh cho desktop. Không dựng server web để lách bài toán desktop. Nếu runner chỉ điều khiển browser, báo incompatibility cụ thể, duyệt native desktop harness phù hợp Qt/Windows và vẫn chạy unit/integration/ML checks; không gọi browser test là đã kiểm native app. Chưa chọn/cài tool desktop automation trong lượt planning.

Không cần AI-driven steps để kiểm desktop path nếu native automation hỗ trợ exact assertions. Nếu dùng AI-driven runner trong tương lai, kiểm credential presence không hiển thị secret và không coi nhận định AI là oracle metric/nhãn bệnh. Report/trace sẽ lưu theo feature/test config đã duyệt, ví dụ `artifacts/qa/<release>/`, **thư mục chưa tạo**. Nếu blocker services/credentials/tooling xuất hiện, ghi test bị chặn, không passed giả.

## Packaging acceptance gate

S18 khóa release manifest/asset inventory/notices; thử user không admin, machine không dev tools, offline cold launch, paths VI, model missing/error/cancel, chạy lại sau restart, memory/size/time, antivirus behavior và uninstall an toàn. Public distribution chỉ sau license/review scope rõ. Artifact demo học thuật cũng phải có attribution và không làm mất dữ liệu. Không tuyên bố offline bằng việc tắt Wi-Fi một lần nếu chưa kiểm mọi required asset/network paths.
