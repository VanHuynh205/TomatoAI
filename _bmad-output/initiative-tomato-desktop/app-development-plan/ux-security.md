# Cách hoạt động, chức năng, tài khoản và bảo mật

Ngày 14/10/2026. Brief UX mức planning theo Impeccable `shape`/Operate và thiết kế mặc định an toàn theo `sharp-edges`. Đọc cùng [kế hoạch phase](app-development-plan.md), [contracts](engineering-contracts.md), [PRODUCT](../../../PRODUCT.md) và [readiness hiện hành](../spec-tomato-desktop/data-readiness.md). Chưa có comp, DESIGN.md, token mỹ thuật khóa hoặc app để đánh giá.

## Công việc và người dùng

Người có ảnh lá cà chua muốn biết ảnh có đủ điều kiện phân tích không, trạng thái gợi ý thuộc nhóm nào, giới hạn của kết quả và nội dung có nguồn được phép đọc. Hành động chính là chọn một ảnh rồi phân tích. Bài học, nguồn và thông tin phiên bản hỗ trợ hiểu đúng; không tạo dashboard nhiều biểu đồ hoặc form tài khoản trước tác vụ này.

Chứng minh thành công bằng một ảnh thật → checkpoint sinh viên → một card VI được phép → nguồn offline → câu tự kiểm tra; đồng thời invalid/cancel/unknown/knowledge-blocked không sinh lời khuyên nhãn bệnh. Auto-tests không chứng minh nhãn ảnh hoặc nội dung nông học đã đúng.

## Luồng sử dụng chính

1. Mở app: kiểm release manifest/schema/hashes/model/KB compatibility; mở trực tiếp màn “Phân tích ảnh”. Không tài khoản, splash kéo dài hoặc download khi khởi động. Bundle lỗi có thông báo và cách kiểm gói; không tạo prediction thay thế.
2. Trạng thái chưa chọn: nêu phạm vi ảnh lá cà chua, JPEG/PNG và ví dụ cách chụp bằng nội dung local. Nút “Chọn ảnh” và phím tắt dự kiến Ctrl+O. Không dùng ảnh mẫu để giả kết quả người dùng.
3. Chọn ảnh: native file picker, preview đúng hướng, tên file nếu cần chỉ trong UI phiên hiện tại. Hủy picker giữ trạng thái trước, zero new inference. Chọn file mới làm vô hiệu request/kết quả cũ.
4. Phân tích: nút “Phân tích” chỉ bật khi input hợp lệ và không có job. UI hiển thị giai đoạn thực, có “Hủy”; không phần trăm tiến độ tự bịa. Decode/preprocess/infer nằm ngoài GUI thread.
5. Nhận kết quả: chỉ render request và image_identity hiện hành. Hiện tên VI/raw scientific name, loại trạng thái bệnh/tác nhân/khỏe, giới hạn và model/data/policy version. Điểm model nếu hiển thị phải giải thích, không gọi là xác suất chẩn đoán đúng.
6. Tra tri thức: exact code tới đúng card; review/version/context/license đủ mới hiển thị claim. Prediction accepted nhưng guidance blocked vẫn phải hiện “Chưa có hướng dẫn đã kiểm tra cho trạng thái này”. Không mượn card gần tên.
7. Xem nguồn: title/tác giả/revision/locator/license/change notice và excerpt/summary có quyền đóng gói. Xem offline được; URL chỉ là tham chiếu, không tự fetch hoặc mở browser. Mở link bên ngoài nếu bổ sung phải là thao tác rõ, cần Internet và không là phụ thuộc core.
8. Học: đọc dấu hiệu, tác nhân và phòng/chăm sóc có điều kiện; hai câu tự kiểm tra với giải thích và nguồn. Điểm quiz khác điểm model. Không dùng prediction làm ground truth đáp án.
9. Chọn ảnh khác/chạy lại: tạo request mới, không lưu phiên mặc định. Đóng app hủy/cleanup đúng worker, không xóa ảnh gốc hoặc process khác.

## Danh mục tính năng và phạm vi

| Tính năng | Bắt buộc / tùy chọn | Công việc cụ thể | Owner |
| --- | --- | --- | --- |
| Boot và thông tin gói | Bắt buộc | Validate bundle, tên/version/schema, missing/corrupt recovery; no silent fallback | S06/S14/S18 |
| Chọn/preview/đổi ảnh | Bắt buộc | File picker, JPEG/PNG, uppercase suffix, grayscale/RGBA policy, EXIF orientation, path có dấu | S06/S13/S14 |
| Kiểm format và giới hạn | Bắt buộc | Magic+decode, byte/pixel/edges, single-frame policy, bomb/resource guard, typed error | S06/S14 |
| Chạy/hủy/thử lại | Bắt buộc | Một job, disable lặp, request identity, cancel/restart, timeout, worker crash recovery | S06/S14 |
| Kết quả/không kết luận | Bắt buộc | Accepted/uncertain/out_of_scope/invalid/error/cancelled; nonaccepted không advice theo lớp | S06/S09/S13 |
| Giới hạn và provenance | Bắt buộc | Version và scope; không severity/yield/giống/chẩn đoán xác nhận | S13/S19 |
| Hướng dẫn có nguồn | Bắt buộc trong scope được phép | Symptoms/care/prevention/cautions đủ review; thiếu phải nêu và chặn | S10/S11/S10b/S11b |
| Ngữ cảnh | Nội dung chung bắt buộc; form cá nhân hóa hoãn | Context absent=`unknown`; chỉ field có rule/source đã duyệt mới được hỏi/tiêu thụ | S11/S11b/S13 |
| Kho học và quiz | Bắt buộc | Danh sách theo card đã cho phép, LO1–LO3, hai quiz/card, feedback/source và trạng thái thiếu nội dung | S12/S13 |
| Tìm theo tên VI/EN trong kho | Tiện ích nhỏ nếu không tăng scope | Lọc danh sách reviewed content trong RAM; tìm kiếm không thay identity mapping và không hiện pending card | S12/S13 |
| Nguồn và phiên bản | Bắt buộc | Vùng mở rộng bằng bàn phím, attribution, EN reference; sources offline | S13/S18 |
| Trợ giúp/hướng dẫn lần đầu | Bắt buộc ở mức ngắn | Chụp ảnh rõ, phạm vi, ý nghĩa không kết luận, cách xử lý lỗi và privacy | S13/S18 |
| Tuỳ chọn hiển thị | Mức tối thiểu | Chữ theo OS/DPI, thông tin version; không cho UI sửa threshold/review/model path | S13 |
| Log hỗ trợ | Bắt buộc | Error code, app/model/KB version, request ID/time; giới hạn kích thước và retention cần khóa | S14/S18 |
| Tài khoản/đăng nhập | Đã chọn không có | Không registration/password/reset/email/token/RBAC server, dùng boundary Windows user | S01/S13/S18 |
| Hồ sơ local | Tùy chọn sau core | Tên hiển thị/cài đặt riêng nếu cần; không là authentication, không metadata vai trò reviewer | S20 mở rộng cần duyệt |
| Lịch sử local | Tùy chọn, mặc định tắt | Opt-in, xem/xóa/export metadata, không ảnh/path/EXIF mặc định | S20 |
| Camera, batch, cloud sync, update online | Ngoài kế hoạch core | Chỉ lập ticket sau change scope riêng | Không có story core |

## Màn hình và cấu trúc tương tác

Đề xuất IA dựa trên UX đã adopted; **chưa khóa mỹ thuật**. Surface mode Operate, nền tảng Qt native, không scene 3D. Màn chính có vùng chọn ảnh/preview và vùng kết quả; thông báo/giới hạn trước prose dài. Hướng dẫn/bài học dùng tab hoặc section rõ; “Nguồn và phiên bản”, “Trợ giúp”, “Cài đặt” không chiếm hành động chính. Window hẹp xếp một cột theo ảnh → trạng thái → guidance → học; không ép chữ nhỏ.

Native controls, system font hỗ trợ VI, focus nổi rõ và status có text/icon. Style/token/color/transition cụ thể phải được duyệt ở S06/S13 trước UI code theo Impeccable; không dùng brief này như visual approval. Một vòng QA gộp các window sizes/DPI/states, sửa cùng batch, tối đa một vòng xác nhận. Không có mobile viewport trong acceptance app Windows.

| State | Nội dung và hành động | Assertion |
| --- | --- | --- |
| Empty | “Chọn ảnh lá cà chua để bắt đầu”; hướng dẫn phạm vi | Chưa prediction/guidance; phân tích disabled |
| Selected | Preview hiện hành, chọn ảnh khác, phân tích | Identity byte hiện hành, không dùng preview cũ cho job mới |
| Loading/running | Giai đoạn thật, Hủy | Active ≤1, queued=0; UI event loop vẫn đáp ứng |
| Invalid | “Không đọc được ảnh này. Hãy chọn ảnh JPEG hoặc PNG khác.” | Forward count=0, không healthy fallback |
| Too large | Nêu limit đã khóa và cách dùng bản ảnh nhỏ hơn | Không ghi đè/crop/resize file gốc |
| Cancelled | “Đã hủy”, chọn/chạy lại | Zero render từ job đã hủy |
| Accepted healthy | “Chưa thấy dấu hiệu thuộc các lớp bệnh/tác nhân được hỗ trợ” | Không bảo đảm toàn cây khỏe; chỉ basic-care hợp lệ |
| Accepted disease/pest | Tên trạng thái và giới hạn, guidance theo gate riêng | Không tự kết luận severity hoặc thuốc |
| Uncertain/out_of_scope | “Chưa đủ căn cứ để kết luận”, chụp/chọn lại, nội dung chung được phép | `guidance.claims=[]` cho lời khuyên theo lớp |
| Knowledge blocked | “Chưa có hướng dẫn đã kiểm tra cho trạng thái này” | Không lấy bệnh gần tên, không giấu việc review pending |
| Bundle/worker error | Mã lỗi dễ hiểu, Retry/Thông tin gói | Không network repair hoặc giả kết quả |

Ctrl+O/Tab/Shift+Tab/Enter/Escape là đề xuất shortcut cần kiểm xung đột Qt/Windows. Escape hủy job active, không đóng app bất ngờ. Accessible names và announcements tiếng Việt; status không chỉ qua màu. Kiểm DPI 100/150/200%, 1280×720/1920×1080 và text VI dài; tương phản tham chiếu chữ thường ≥4,5:1, chữ lớn/control/focus ≥3:1 theo loại. Motion ngắn phục vụ đổi state, không chặn kết quả, có giảm motion.

## Tài khoản, quyền và dữ liệu người dùng

Người dùng chốt **không đăng nhập**. App chạy quyền thường, state per-Windows-user bằng QStandardPaths. Không cần user table/password hash/JWT/OAuth/session timeout hoặc backend auth. Người cùng Windows account có thể truy cập state; profile local không cung cấp cách ly bảo mật. Không tuyên bố mã hóa vì không lưu ảnh, hoặc chống người có quyền admin chỉ bằng file ACL.

Sinh viên/biên tập viên/reviewer nông học là vai trò ngoài app trong pipeline review. Ghi actor/role/date/scope thật vào artifact, kiểm release bundle trước phân phối. Người dùng runtime không có nút đổi `safe_for_advice`/`expert_approved`/threshold để mở khóa. Chữ ký/code signing cần đánh giá C5; không tự cấp reviewer role bằng UI.

S20 nếu duyệt: history/profile đặt per-user, default off; cài đặt hiển thị ít nhạy cảm có thể lưu riêng. History ghi metadata tối thiểu, consent/retention/giới hạn record rõ; không lưu ảnh/full path/EXIF. Export do người dùng chủ động, cảnh báo nội dung cụ thể, giữ source/input. Nếu thêm tên profile thì chỉ tên hiển thị, không thu email/phone/địa chỉ. Xóa profile/history xác nhận phạm vi rồi xóa state tương ứng, không recursive-delete thư mục tự chọn hoặc source.

## Boundary bảo mật và mặc định an toàn

Đây là phân tích thiết kế, không finding exploit đã chạy hoặc audit code. Theo `sharp-edges`, kiểm cả người chỉnh config ác ý, implementer copy ví dụ nhanh và implementer hiểu sai type. Các testcase dưới đây là bằng chứng cần có khi module xuất hiện.

| Boundary / lỗi dễ dùng sai | Quy tắc thiết kế | Kiểm chứng cụ thể | Owner/test |
| --- | --- | --- | --- |
| Ảnh file không tin cậy | Chặn format/bytes/pixels trước decode lớn; worker bounded, giữ bomb warnings | Text giả JPG, truncated, huge-dimension header; forward=0, UI còn phản hồi | S14/T02,T03 |
| File đổi sau preview | Identity gắn đúng byte infer; input snapshot bounded trong worker | Sửa/thay file giữa chọn/run không ghép preview cũ và result mới | S06/S14/T01,T10 |
| Config 0/-1/null/boolean/NaN | Validate type và positive finite limits; thiếu key không tắt guard | `timeout=0`, `max_pixels=-1`, threshold NaN, index=True → reject config/result | S14/T03,T04,T06 |
| Nạp model | First-party allowlist/tensor state dict, explicit CPU/weights_only trên bản vá pin; không import tùy ý | Wrong hash/shape, unsupported architecture, safe hostile fixture không được execute | S14/T04,T12 |
| Policy content | Mode/scope/actor/EN–VI hashes rõ; config không có bypass-review | Thiếu nguồn/reviewer/hash, chemical/context unknown, stale VI → zero claims | S11/S11b/S14/T07–T09 |
| GUI–IPC–worker | Một active, không queue, schema/identity được validate | 20 lần click, late result, repeated cancel, malformed message/crash → no stale render | S06/S14/T10 |
| Filesystem/state | State root canonical per-user, atomic write, parameterized SQLite nếu có | Read-only/full disk/path có dấu; xóa chỉ selected IDs, raw/input hash không đổi | S14/S20/T18 |
| Log/private input | Không ảnh/base64/EXIF/full path; bound file count/size/retention | Scan logs và state off: zero ảnh/history, chỉ error/version/opaque ID | S14/S18/T18 |
| Resource/service/network | CPU-first, no remote fetch/font/telemetry/update; cleanup owned process | Network observation Windows sạch, thiếu cache/weights, cancel timeout; không download | S18/T11–T13 |
| Supply chain | Pin deps/hash, inventory và notices; kiểm advisory trước khóa/build | Release lock+manifest khớp gói; chưa đủ rights thì không distribute | S01/S18/T12,T13,T20 |

Không dùng `eval`, pickle/full-module load không tin cậy, dynamic import từ model manifest, SQL string concatenation hoặc subprocess command từ input người dùng. Không nhận archive/KB/model import tự do, nên không dựng archive parser chỉ để thêm tính năng. Cần import tương lai thì lập threat/test plan riêng trước.

Hash và isolated worker giảm một số rủi ro, không là sandbox tuyệt đối. `weights_only=True` vẫn phải đi cùng trusted source và bản vá; không đủ ngăn mọi DoS/corruption. Kiểm source và advisory của PyTorch tại [security policy](https://github.com/pytorch/pytorch/security/policy) và [serialization notes](https://docs.pytorch.org/docs/stable/notes/serialization).

## Gate nội dung và chặn readiness

Hiện 17 card/172 claim chưa mở guidance thật; policy demo `source_checked` xung đột gate validator và còn pending C3. S11 phải ghi quyết định mode/version/allowed claim/actor/nguồn/VI, tạo bundle mới; không sửa seal/flag nguồn để đủ milestone. Chemical/dose/lịch phun/cách ly chưa đủ căn cứ không được hiển thị. Chưa có expert thì không ghi expert-approved. Nếu C3 yêu cầu chuyên gia mà chưa có người, S06 positive một-card milestone vẫn blocked; chỉ có refusal fixtures không nghiệm thu thay được.

Mosaic ToMV/TMV pending; Target/mosaic thiếu grouping. Không mở benchmark/train full 10 lớp bằng singleton/random split. WUR/Dryad/Mendeley ngoài MVP; không nối vào khuyến nghị tưới/phân. Field/OOD và learning/care chỉ claim kết quả khi có ground truth/reviewer/người tham gia thật.
