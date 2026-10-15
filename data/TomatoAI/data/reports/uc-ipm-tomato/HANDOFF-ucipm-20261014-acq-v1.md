# Bàn giao thu thập và cleaning kỹ thuật UC IPM Tomato

Ngày: 2026-10-14, Asia/Bangkok. Run: `ucipm-20261014-acq-v1`. Dataset root thực tế: `data/TomatoAI/data`.

## Kết quả và giới hạn

**Đợt thu thập bị chặn ở preflight permissions HTTP 403. Chưa có corpus HTML và chưa có tài liệu cleaned_technical.** Đây không phải báo cáo thu thập thành công. Yêu cầu dừng sau 403 được thực hiện; không gửi request corpus, không đổi danh tính, đăng nhập, dùng proxy hoặc đường thay thế để né chặn.

Đã đối chiếu đúng 21 URL giữa kế hoạch mục 6, config và inventory. Không mở 95 liên kết chưa khảo sát; không tải ảnh, PDF, video hoặc tài nguyên phụ. Các kiểm tra điều khoản bằng web reader là preflight riêng, không tính trong 21 tài liệu. Web reader không cung cấp HTTP status cho trang đọc được thì để null, không suy thành 200. Các policy được mở theo nhóm; không chứng minh cadence của web reader. Collector corpus chưa được khởi chạy; collector Python kiểm tra một request mỗi lượt và chờ ít nhất 5 giây sau khi hoàn tất.

| Thu thập corpus | Số item |
| --- | ---: |
| downloaded | 0 |
| reused | 0 |
| metadata_only | 0 |
| blocked | 0 |
| not_attempted_batch_stopped | 21 |
| Tổng | 21 |

| Xử lý corpus | Số item |
| --- | ---: |
| cleaned_technical | 0 |
| processing_pending | 0 |
| failed | 0 |
| not_applicable | 21 |
| Tổng | 21 |

`blocked=0` trong bảng corpus không có nghĩa preflight thành công: tài nguyên bị HTTP 403 là trang quyền ngoài corpus. Cả 21 item chưa thử, chỉ có metadata khảo sát kế thừa; không phân loại chúng thành downloaded hoặc metadata_only của lượt live. Các flag chồng nhau không được cộng vào số item.

Robots hiện tại chưa được kiểm lại vì batch đã dừng; bằng chứng robots ngày 2026-10-14 của báo cáo khảo sát được dẫn rõ là prior evidence, không dùng thay authorization hiện tại. Parser mới được kiểm với fixture, chưa được xác minh trên HTML thật của 21 trang.

## Quyền, provenance và sidecar

[Legal Notices của IPM](https://ipm.ucanr.edu/GENERAL/copyright.html) có banner archived và căn cứ bản văn bản cá nhân/giáo dục có điều kiện giữ credit/copyright. [UC ANR Copyright](https://ucanr.edu/copyright) có notice giáo dục và tham chiếu CC BY-NC-ND; chưa xác minh phạm vi từng HTML. [Permissions](https://ucanr.edu/dept/anr-publishing/permissions) trả HTTP 403. [CC legal code](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en) phân biệt thay đổi định dạng kỹ thuật, bản thích nghi cá nhân và việc chia sẻ; chỉ áp dụng với tài nguyên thực sự được cấp phép.

Ledger giữ năm mục đích riêng: lưu nghiên cứu, xử lý kỹ thuật, biên soạn/chuyển ngữ, phân phối app/repo/demo và media/ML. Trạng thái từng item hiện pending; không gán CC0 hay license chung cho domain. Config mặc định không tự cho phép tải/processing. Khi có căn cứ từng tài nguyên, `rights_by_item` cần `conditional_allowed` và `evidence_url` riêng cho mục đích; quyền lưu không suy thành quyền xử lý, dịch hoặc phát hành. Không gửi email/form xin phép.

Snapshot SHA-256, accessed_at và final URL của corpus chưa tải đều null. Không tạo hash từ URL hay từ response rỗng. Raw run không có HTML. Processed run chỉ có mapping/evidence sidecar dẫn xuất từ khảo sát cũ: 10 condition/nhãn ảnh giữ nguyên, 12 claim giữ EN và hash nguồn PlantExpert. Không thêm evidence source-check mới khi thiếu snapshot. Bốn nguồn đúng bệnh, hai nhóm tác nhân, Healthy và ba thiếu nguồn đặc hiệu được giữ phân biệt; không gọi 7/10 là mapping đã duyệt. Metadata đối chiếu gần tên vẫn được giữ, nhưng không biến thành evidence snapshot.

Giữ nguyên conflict TMV/ToMV, aphid vector, bleach, misting, crop rotation và điều kiện cấp vùng. Spider mite không đổi thành russet mite; Gray Mold không thay Leaf Mold; Early Blight không thay Target Spot. Không review toàn bộ 172 claim. Mọi domain review pending, translation not_translated, reviewer null, display/advice/training false. `research_only` và `exclude_from_release=true`; không đóng gói các nhánh UC vào app/repo/demo hoặc artifact phân phối.

## Kiểm chứng và bảo toàn

- **31/31 test collector/parser/run** qua: allowlist/robots/redirect, decoded-byte cap, lỗi/attachment/error HTML, retry/backoff, 304/cache, 429 checkpoint/dừng, heading/list/table/span/header/footnote, phủ định/điều kiện/đơn vị, encoding và quyền theo mục đích, schema/gate, provenance, IDs, sidecar và idempotency.
- **22/22 test integration hiện có** qua. Tổng 53 test. Các fixture permission/approval là SYNTHETIC, không phải chứng cứ cấp quyền thật.
- Ruff và `py_compile` qua cho ba script mới. Không có cấu hình type checker riêng cho pipeline này; không tuyên bố đã chạy mypy/pyright.
- Chạy lại transform offline: tạo lại derivative vào thư mục tạm, đối chiếu hash với artifact sealed, không network và không mutate raw. Lượt thật có 0 snapshot nên replay chỉ xác minh sidecar; test fixture có snapshot kiểm đầy đủ đường parser/hash trước-sau.
- Bảo toàn **55.097 file** qua danh sách/size/mtime; **278 file** có SHA-256 trong phạm vi control/report/planning và PlantExpert raw. Không rehash toàn bộ ảnh. So sánh trước/sau và kiểm lại lúc bàn giao khớp.
- `npx --no-install e2e run` được thử bằng runner đã cài ở frontend: exit 2, `CONFIG_NOT_FOUND`, 0 test thực chạy, không có e2e.config.ts/mts hoặc URL frontend trong config. Không dựng UI/server hay tạo cấu hình sản phẩm cho pipeline dữ liệu này.
- Registry thêm một entry `UC-IPM-Tomato` với trạng thái acquisition_blocked/research_only; toàn bộ năm entry cũ và metadata cấp registry giữ nguyên. UC không thành dependency MVP.

## File và lệnh Windows

Script: `scripts/data/collect_ucipm.py`, `scripts/data/test_collect_ucipm.py`, `scripts/data/verify_ucipm.py`; config/schema/receipt nằm cùng thư mục. Tái sử dụng `digest`, `pairs_unique`, `write_json` của helper PlantExpert; dùng stdlib và requests/beautifulsoup4/jsonschema đã cài. Không cài dependency mới hoặc gọi model/API AI. Workflow chính: **Ponytail full** cho reuse-first/guard/test; **e2e** cho kiểm tra runner/config và ghi blocker. Không chạy BMAD, UI/Impeccable, training hoặc dịch.

Từ project root:

```powershell
python scripts/data/collect_ucipm.py --run ucipm-20261014-acq-v1 --blocked-preflight scripts/data/ucipm-preflight-20261014.json
python scripts/data/collect_ucipm.py --run ucipm-20261014-acq-v1 --blocked-preflight scripts/data/ucipm-preflight-20261014.json --transform-only
python -m unittest discover -s scripts/data -p test_collect_ucipm.py -v
python -m unittest discover -s scripts/data -p test_review_integration.py -v
python -m ruff check scripts/data/collect_ucipm.py scripts/data/test_collect_ucipm.py scripts/data/verify_ucipm.py
```

Verifier/registry đã chạy một lần: `python scripts/data/verify_ucipm.py --run ucipm-20261014-acq-v1 --register`. Verifier không ghi đè báo cáo QA đã tồn tại. Collector cùng input/config/parser kiểm seal rồi reuse, không nhân đôi record; thay input/parser phải tạo run mới.

- [README run](ucipm-20261014-acq-v1/README.md)
- [Manifest đủ 21 item](ucipm-20261014-acq-v1/source-processed-manifest.json)
- [Checkpoint](ucipm-20261014-acq-v1/checkpoint.json)
- [Schema](ucipm-20261014-acq-v1/schema.json), [data dictionary](ucipm-20261014-acq-v1/data-dictionary.json), [transformation log](ucipm-20261014-acq-v1/transformation-log.json)
- [Review queue](ucipm-20261014-acq-v1/review-queue.json), [attribution/rights ledger](ucipm-20261014-acq-v1/attribution-rights-ledger.json), [preflight](ucipm-20261014-acq-v1/preflight.json)
- [Verification](ucipm-20261014-acq-v1-verification.json), [31 test](ucipm-20261014-acq-v1-unit-tests.txt), [22 test](ucipm-20261014-acq-v1-integration-tests.txt), [E2E blocker](ucipm-20261014-acq-v1-e2e.txt)
- [Mapping sidecar](../../processed/uc-ipm-tomato/ucipm-20261014-acq-v1/mapping-sidecar.json), [12 claim sidecar](../../processed/uc-ipm-tomato/ucipm-20261014-acq-v1/claim-evidence-sidecar.json)

## Bước tiếp theo

Giải quyết truy cập permissions bằng tuyến được chấp thuận và xác minh quyền từng tài nguyên; không né HTTP 403. Trong một run phiên bản mới, kiểm robots/terms hiện tại trước collector, ghi notice từng item và chỉ tải/xử lý khi đủ căn cứ tương ứng. Sau khi có snapshot hợp lệ mới kiểm parser trên layout thật. Dừng tại đây; chưa Việt hóa, mở guidance, train, làm sản phẩm hoặc tiếp nhận kế hoạch chính thức BMAD.
