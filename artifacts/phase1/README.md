# Phase 1 — Dữ liệu có provenance và benchmark bị chặn đúng

Ngày kiểm chứng: 15/10/2026. Phạm vi EPA.S02–S04 theo kế hoạch app chính thức. Không train, tải dataset/weights hoặc triển khai Phase 2.

## Kết quả

S02/S03 đã `built`, chưa tự `done`: có inventory thật, điều tra metadata gốc và derivative quarantine có lý do. S04 đã có thuật toán và regression tests, nhưng **chưa có benchmark được duyệt**. Phase 1 chưa hoàn tất toàn bộ gate C2.

- [Data card](../data-card.json): chọn đúng sáu `registry.current_run`, xác minh artifact seals, 18.362 file raw trong năm baseline và từng record provenance. WUR/Dryad/Mendeley giữ research-only; PlantExpert là knowledge-review-only; UC-IPM vẫn blocked, zero acquired documents.
- [Group resolution](../group-resolution.json): 18.160 source records, 11.411 technical candidates, 6.735 quarantined retained, 14 excluded exact duplicates; 9.589 components. Không record nào được cấp quyền train.
- [Metadata replay](../metadata-investigation.json): cả hai JSON và CSV khớp manifest nhưng là các bản dẫn xuất của cùng nguồn. 6.749 source thiếu grouping khác 6.735 retained review. Có 1.409 CSV records không khớp source ảnh hiện có.
- [Workbook gốc](original-metadata-workbook.json): giữ hash container/member, đọc trong bộ nhớ, không giải nén hoặc chạy công thức. Workbook có 1.404 tên `Com.G_FL`, zero `TgS`, không sheet mosaic. Nhãn sheet “Target Spot Bacteria” là nguyên văn nguồn, không được nhận làm taxonomy chuẩn.
- [Split bị chặn](../split-manifest.json): không assignments/class manifest thật. [Pending policy](split-policy.pending.json) chứa seed 42, targets 70/15/15 và class order đề xuất hiện có; approvals vẫn false. Đây là lựa chọn kỹ thuật theo chỉ đạo best-effort của người dùng, không phải kết quả phân chia.

Target Spot có 1.404 alias candidates theo phần số của tên ảnh; phần số trùng không chứng minh cùng lá. Mosaic có 373 ảnh không grouping và identity ToMV/TMV chưa duyệt. Cả hai giữ nguyên nhãn nguồn, không tạo singleton hoặc fuzzy mapping. Mười near pairs là gợi ý heuristic chưa được xác nhận; hai component của mỗi pair được quarantine. Nhãn bệnh ảnh chưa được chuyên gia xác minh; hash không thay thế review nhãn.

[Completion audit](completion-audit.json) có số component theo từng lớp: tám lớp có ít nhất ba technical components; Target Spot và mosaic có zero technical support. Vì thế seed/ratios tự chúng không giải được full10 benchmark. Đây không phải quyết định tự đổi thành pilot tám lớp.

[Đối chiếu upstream ngày 15/10](upstream-grouping-audit.md): GitHub HEAD vẫn trùng revision đã chọn; leaf maps của cả GitHub/Hugging Face và Target CSV không có delta. Loader chính thức sinh `fallback_` khi thiếu metadata, nên không nhập các ID đó làm bằng chứng nhóm. Gate C2 vẫn chưa mở sau kiểm tra nguồn công khai.

## Gate còn thiếu

1. Bằng chứng grouping đủ cho full 10 lớp hoặc quyết định riêng về pilot subset được duyệt. Không tự giảm thành tám lớp.
2. Review nhãn, identity mosaic, class/code order và approval C2 gắn hash với đúng review hiện hành.
3. Quyền dùng dữ liệu để train trong rights ledger vẫn pending. Phân phối/pretrained/tri thức có các gate riêng.

Seed và ratios đã có dự thảo kỹ thuật, không cần chờ chuyên gia để chọn số. Chỉ được khóa sau khi kiểm support thực và duyệt scope; tỷ lệ theo group là target, không bảo đảm tỷ lệ ảnh chính xác. Không có accuracy, checkpoint hoặc hiệu quả lời khuyên được công bố.

## Kiểm chứng

- Benchmark tests: **31/31 pass**, gồm deterministic split, giao group/components rỗng, class order, hỗ trợ từng lớp, thiếu review/rights, stale hashes, path traversal, raw mutation, source review flags, code-list type và CLI chống ghi đè input/sidecar. Positive split chỉ dùng fixture synthetic.
- Sau fix pass: existing cleaning/integration suite **82/82 pass**, gồm mười production checks PV/PlantExpert được bật bằng report/project-root environment variables. UC-IPM **31/31 pass** qua uv. Cùng benchmark tests, có **144/144 pass**, zero skip. Xem [cleaning final](cleaning-after-review.log), [UC-IPM final](ucipm-after-review.log), [benchmark final](benchmark-final.log). Lượt production đầu thiếu biến `PLANTVILLAGE_PROJECT_ROOT` đã được sửa cấu hình lệnh, không sửa assertions.
- Pipeline thật: [run record](pipeline-run.json), [log](pipeline-final.log). Exit code `2` có nghĩa gate C2 blocked; không phải pass cho approved split.
- [Preservation](preservation-after.json): 216 file registry, bảy ticket stores, existing reports và cleaning source không đổi. [Raw after-check](raw-after.json) rehash lại 18.362 file sau pipeline, đủ năm baseline; loại `.git`, `.cache`, `__pycache__` trong PV như cleaner. Không suy ra tính đúng trước thời điểm baseline.
- [Default discovery](data-default-environment.log): 104 tests, một lỗi import WUR do `pdfplumber` chưa có trong Python uv mặc định, mười production tests skip. WUR được chạy riêng bằng bundled runtime có dependency. Không cài dependency để che lỗi. Không có cấu hình lint/type-check dự án cho pipeline này.
- Không chạy `npx e2e run`: không có `e2e.config.ts`, frontend URL hay Qt Windows engine phù hợp trong skill hiện cài. Không UI nào thay đổi trong Phase 1. CLI integration và unit/regression là bằng chứng đã chạy, không phải native UI E2E.
- Fresh read-only review bằng `gpt-6-astra` phát hiện ba Important, đã sửa trong một pass có RED→GREEN; không Critical/Minor, không review vòng hai. [Review và phạm vi chưa đánh giá](final-review.md), [các quyết định và rủi ro](progress.md). Reviewer tự chạy 27 pre-fix tests; không gọi toàn bộ evidence là independent replication.

## Chạy lại

Tại project root, tái dùng môi trường Phase 0 hiện có:

```powershell
.venv-phase0/Scripts/python.exe -m unittest discover -s tests/data -p test_benchmark.py -v
.venv-phase0/Scripts/python.exe artifacts/phase1/verify_evidence.py
```

`verify_evidence.py` tạo lại pipeline evidence, workbook audit và preservation; yêu cầu raw/runs/baselines hiện hành còn đúng. Output chỉ ghi dưới `artifacts/`. Đổi file pending policy không tự tạo approval hoặc quyền train. Các đường dẫn tuyệt đối trong báo cáo là evidence nội bộ máy phát triển, không dùng làm app log người dùng.

Thay đổi nguồn chính: `scripts/data/prepare_benchmark.py`, `tests/data/test_benchmark.py`. Không thêm dependency, không sửa cleaner hay dữ liệu đã seal. Trạng thái BMAD `built` chỉ là đã xây và kiểm phần kỹ thuật; người dùng quyết định `done`.
