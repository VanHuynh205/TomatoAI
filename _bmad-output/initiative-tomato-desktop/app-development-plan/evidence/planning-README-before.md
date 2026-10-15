# Hồ sơ planning đồ án cà chua desktop

## Trạng thái hiện hành — kế hoạch BMAD đã tiếp nhận

Đối chiếu ngày **14/10/2026** xác nhận báo cáo làm sạch PlantVillage, PlantExpertVQA-tomato, WUR, Dryad và Mendeley đã được đưa vào [kế hoạch BMAD chính thức](../../_bmad-output/initiative-tomato-desktop/initiative-tomato-desktop.md), phiên bản `pi-20261014-v1`. [Data readiness](../../_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/data-readiness.md) tham chiếu đúng các run hiện hành trong registry, review tích hợp `ir-20261014-v1` và checkpoint UC-IPM bị chặn HTTP 403, không có tài liệu cleaned mới. Xem [biên bản tiếp nhận chính thức](../../_bmad-output/initiative-tomato-desktop/planning-import-20261014-v1/README.md).

Runtime xác nhận **6 epic/22 story planned**, chỉ `EPA.S01` ready_to_start; 21 story còn bị chặn bởi phụ thuộc hoặc câu hỏi chưa giải quyết. PlantVillage được truy vết qua S02–S04; tri thức/mapping/tiếng Việt qua S10/S11/S10b/S11b. WUR/Dryad/Mendeley và UC-IPM giữ research-only ngoài MVP. Đã kiểm 24 liên kết trong initiative/spec/readiness/traceability, 42 artifact planning và 25 file sealed review: không thiếu liên kết hoặc lệch hash. [Bằng chứng đối chiếu và bản sao README trước sửa](../../tmp/bmad-dataset-reconciliation-20261014-233427/verification.json).

Việc tiếp nhận planning không nâng dữ liệu thành training-ready hoặc mở quyền hiển thị hướng dẫn. Grouping/split, license, policy và duyệt chuyên môn/tiếng Việt vẫn là các gate đang chặn. **Các đoạn bên dưới là hồ sơ lịch sử draft/setup/review trước tiếp nhận**; những câu “chưa tiếp nhận”, “chờ báo cáo cleaning” hoặc “bắt đầu PlantVillage” không mô tả trạng thái hiện hành. Giữ nguyên chúng để bảo toàn lịch sử, ID và tiêu chí nghiệm thu nguồn.

## Hồ sơ lịch sử trước tiếp nhận

**Checkpoint review trước tiếp nhận — 14/10/2026, ir-20261014-v1:** [báo cáo và bộ bằng chứng](../../data/TomatoAI/data/reports/integration/ir-20261014-v1/README.md). Registry đã chỉ định run cleaning kỹ thuật của cả năm dataset; các câu “bắt đầu PlantVillage” bên dưới thuộc checkpoint lịch sử 13/10, không yêu cầu làm sạch lại. Review nhận diện danh tính 9/10 cặp nhãn–card ở mức đối chiếu nguồn, 1 pending ToMV/TMV, 0 thiếu card. Cả 17 card vẫn chờ duyệt chuyên môn và tiếng Việt; 26/172 management claim có căn cứ nguyên tắc, nhưng 0 claim thật được mở hiển thị. Có 22 test hợp đồng lookup qua; chưa có model hoặc phép đo khả năng nhận diện. Grouping/split, manifest lớp, license và phê duyệt hướng dẫn còn chặn readiness. WUR/Dryad/Mendeley giữ ngoài MVP. Draft/ID/lịch sử giữ nguyên; chưa tiếp nhận planning chính thức hoặc khởi động triển khai. Bản README trước bổ sung và kiểm tra bảo toàn ID nằm trong bộ review.

Ngày khảo sát: **13/10/2026**, múi giờ Asia/Bangkok. Trạng thái: **bản nháp planning độc lập để duyệt và nhập vào BMAD; chưa phải đầu ra workflow BMAD đã kích hoạt**.

Tên đã chốt bởi người dùng: **“Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”**.

**Quyết định phạm vi thay thế, 13/10/2026:** nhận diện bệnh/trạng thái lá cà chua và hướng dẫn trồng/chăm sóc phù hợp; desktop Windows, tiếng Việt, offline; giữ EfficientNet và ResNet50, không website/AI API/dịch API. Không thêm bài toán tối ưu năng suất/nước/phân bón/chi phí. WUR, Dryad và Mendeley là tài nguyên nghiên cứu bổ sung, chưa là yêu cầu MVP. Trong draft, “thẩm định” được diễn giải ở mức kiểm tra đầu vào và đối chiếu dấu hiệu/giới hạn theo tri thức có nguồn; diễn giải này cần đối chiếu rubric, không bổ sung chức năng xét nghiệm hay kiểm định chuyên môn từ một ảnh. Các tên cũ trong biên bản lịch sử không còn là tên đang dùng.

**Setup hiện tại:** runtime local `6.13.0-next` đã tạo bằng flow `bmad setup`; output `_bmad-output`, active initiative `initiative-tomato-desktop`. Hồ sơ này vẫn là draft độc lập; chưa tạo PRD/spec/ticket hoặc memlog chính thức, chờ kết quả làm sạch từng dataset. Xem [biên bản setup](setup-report.md), bao gồm đường dẫn bản sao trước sửa và bằng chứng kiểm chứng.

## Đọc và duyệt

| Tài liệu | Nội dung chuẩn, không sao chép sang tài liệu khác |
| --- | --- |
| [product-brief.md](product-brief.md) | Bài toán, người dùng, MVP, ngoài phạm vi và tên đề tài đã chốt |
| [data-audit.md](data-audit.md) | Kiểm kê local, grouping, schema, mapping nhãn–tri thức và lỗ hổng |
| [research.md](research.md) | Nguồn chính thức đã đọc, phạm vi bằng chứng, giấy phép |
| [prd.md](prd.md) | FR/NFR, tiêu chí nghiệm thu và truy vết story/test |
| [ux-desktop.md](ux-desktop.md) | Luồng, bố cục đề xuất, trạng thái, bàn phím và học tập |
| [architecture.md](architecture.md) | Quyết định AD, module, contract, version và đóng gói |
| [experiments.md](experiments.md) | Chuẩn bị/split, EfficientNet/ResNet50, chọn mô hình và đánh giá |
| [knowledge-localization-edtech.md](knowledge-localization-edtech.md) | Dịch–duyệt, tra cứu, nội dung học và đánh giá tư vấn |
| [security-testing.md](security-testing.md) | Ma trận rủi ro và catalog test dự kiến |
| [delivery-plan.md](delivery-plan.md) | Quy trình, epic/story, phụ thuộc, readiness, báo cáo/demo |
| [planning-spec.md](planning-spec.md) | Contract gọn CAP-1…CAP-9 và danh sách companion để BMAD tiếp nhận |

**Quy ước bằng chứng:** “đã khảo sát” = đã đọc/đếm trong lượt này; “đề xuất” = phương án cần duyệt; “chưa kiểm chứng” = chưa có phép đo/kiểm duyệt cần thiết; “công việc sẽ làm” = backlog, không phải kết quả. Ô kết quả thực nghiệm để trống. Số từ tài liệu nguồn không phải số được kiểm kê local.

## Biên bản BMAD lịch sử — trước setup

Phần này giữ kết quả của lượt planning ban đầu; các phát biểu thiếu runtime/bị chặn activation mô tả thời điểm đó, đã được thay thế bởi setup trong [setup-report](setup-report.md). Các workflow planning vẫn chưa được chạy để tiếp nhận draft.

- Đã đọc `AGENTS.md`, skill người dùng chỉ định tại `C:/Users/admin/.agents/skills/bmad/SKILL.md`, `references/help.md`, help các module và activation của các skill planning bên dưới.
- Discovery chạy script có sẵn `knowledge.py --content`, qua Python đã cài, trên `.agents/skills`, `C:/Users/admin/.agents/skills`, `C:/Users/admin/.codex/skills`. Dùng Python trực tiếp thay `uv run` để tránh provision interpreter ngoài phạm vi; không viết script hoặc cài gói. Discovery không báo `problems`.
- Các record `bmod-core-tools`, `bmod-method`, `bmod-toolsmith` khai báo **6.13.0-next**. Đây là version record local, không phải xác nhận bản mới nhất upstream. Không nâng cấp.
- Trong `.agents/skills` của project không có các thư mục skill BMAD; skill BMAD được host cung cấp từ thư mục người dùng. `bmad` có; không thấy skill riêng tên `bmad-help` trong discovery. Dùng tên thực tế `bmad`.
- Không có `_bmad/` tại project hoặc các thư mục cha đã kiểm tra tới ổ C; không có `_bmad/config.toml`, `resolve_config.py`, `resolve_customization.py`, `memlog.py`. Vì vậy chưa có `core.output_folder` hoặc `active_initiative` để resolve.
- Activation của [bmad-spec](C:/Users/admin/.agents/skills/bmad-spec/SKILL.md) yêu cầu: **“Script not found: BMad is not set up here.”** Skill không cho bắt đầu main workflow trước activation hoàn tất. Các skill brief/PRD/architecture/ticket có cùng dependency. Không tạo memlog giả, không giả vờ chạy workflow, không tạo `tickets.toml` hoặc ticket store giả.
- Đã thử đọc `docs/agents/domain.md`: không tồn tại. `docs/agents/issue-tracker.md`, `triage-labels.md` cũng không tồn tại. Chưa đọc/publish issue hoặc triage; story trong tài liệu là backlog đề xuất, chưa là issue của store.
- `frontend/` tồn tại nhưng không có `frontend/package.json`; không dùng sự tồn tại thư mục để khẳng định có ứng dụng. Yêu cầu người dùng “chưa có code sản phẩm” là phạm vi của lượt này; không audit source hoặc khởi động server.

| Mục đích | Tên thực tế đã xác minh | Tài liệu chuẩn khi workflow chạy | Tình trạng lượt này |
| --- | --- | --- | --- |
| Định hướng | `bmad` | Discovery/help và đề xuất bước tiếp theo | Đã sử dụng help/discovery |
| Chốt bài toán | `bmad-product-brief` | `brief-<slug>/brief-<slug>.md` | Đã kiểm tra activation; bị chặn runtime |
| Nghiên cứu | `bmad-deep-recon` | `research-<topic>/brief.md`, `research-<topic>.md` | Bị chặn runtime; nghiên cứu độc lập có nguồn |
| Yêu cầu | `bmad-prd` | `prd-<slug>/prd-<slug>.md` | Bị chặn runtime |
| UX | `bmad-ux` | `DESIGN.md`, `EXPERIENCE.md` trong run UX | Bị chặn runtime; chỉ tài liệu UX đề xuất |
| Kiến trúc | `bmad-architecture` | Architecture spine với ID `AD-n` | Bị chặn runtime |
| Contract | `bmad-spec` | Folder spec, kernel, companions và memlog qua script | Bị chặn runtime; `planning-spec.md` là đầu vào |
| Chia việc | `bmad-ticket` | Initiative/epic, `tickets.toml`, leaf khi pull | Bị chặn runtime; chỉ bảng story đề xuất |

Chọn **BMAD planning** làm workflow chính dự kiến; không gọi build/dev, không áp dụng workflow implementation khác. Impeccable chỉ bổ trợ UX ở mức planning: nhánh B, `shape` và `operate`; context chạy thành công một lần qua launcher local, báo chưa có PRODUCT.md/visual authority. Không ghi direction contract hay tuyên bố UX đã được duyệt. Impeccable local v4.3.1 có thông báo upstream v4.5.2; không cập nhật trong phiên.

## Quyết định và checkpoint

**Đã chốt bởi người dùng:** cà chua; desktop ưu tiên Windows; offline sau cài; tiếng Việt; EfficientNet và ResNet50; sinh viên tự chuẩn bị dữ liệu, transfer learning và đánh giá; không website/AI API/dịch API. Hai tháng làm mỗi tối. Máy được khai báo: Ryzen 5 5625U, RAM 16 GB, RTX 3050 VRAM 4 GB; có thể dùng Colab cho training. Chưa có rubric, chưa có người hỗ trợ chuyên môn/ảnh thực tế.

**Đề xuất cần duyệt:** EfficientNet-B0; PyTorch/torchvision; Python + PySide6 Widgets; so sánh rồi triển khai một mô hình; giữ kho EN và bản VI dẫn xuất có review. Tên và phạm vi đã được người dùng chốt như trên; rubric giảng viên vẫn chưa có. Không mặc định stack/biến thể/metric hoặc nội dung tri thức đã được chấp thuận.

Checkpoint C0: tên/phạm vi đã chốt bởi người dùng, còn đối chiếu rubric giảng viên. C1: biến thể, stack, ngân sách, metric mục tiêu. C2: giấy phép và split/grouping đủ căn cứ. C3: nguồn/kiểm duyệt tri thức. C4: khóa lựa chọn bằng validation trước test. C5: clean-machine/offline và giới hạn bảo vệ. Các checkpoint chưa duyệt chỉ chặn công việc phụ thuộc, không chặn đọc hồ sơ này.

**Bước tiếp theo ở phiên sau:** thực hiện Prompt 2 cho từng dataset khi được yêu cầu, bắt đầu PlantVillage; lưu báo cáo/review queue/registry. Sau đó mới thực hiện Prompt 3 để cập nhật và tiếp nhận draft vào planning BMAD chính thức, giữ ID yêu cầu/story/test. Setup không đồng nghĩa đã duyệt toàn bộ draft hoặc cho phép code/train. Không cần tải lại dataset.

## Kiểm tra đã thực hiện

**Bổ sung sau lượt planning, 13/10/2026:** người dùng đã cho phép tải các dataset canh tác cà chua. Đã tiếp nhận ba bộ Dryad/Mendeley/WUR vào vùng raw riêng, kiểm tra digest và kiểm kê chỉ đọc. Xem [biên bản tiếp nhận và giới hạn dữ liệu](../../data/TomatoAI/data/cultivation_metadata/README.md). Các phát biểu “không tải” bên dưới mô tả lượt planning ban đầu; không phải trạng thái hiện tại của vùng dữ liệu. Việc tải chưa thay đổi MVP/PRD, chưa duyệt bài toán tối ưu hay cho phép training/code.

Đếm file/lớp, đọc metadata/schema 17 JSON, đối sánh sơ bộ grouping và liên kết ID, giải mã 11 mẫu ảnh, xem hai mẫu ảnh, đọc nguồn chính thức, kiểm tra nội bộ tài liệu/ID/link. Không huấn luyện, không đo inference, không dịch hàng loạt, không sửa raw, không tải weights, không chạy SAST/pentest/E2E sản phẩm. Chi tiết bằng chứng ở data-audit; test tương lai ở security-testing.

Kết quả kiểm tra tài liệu cuối lượt: **12 file Markdown**, không có file triển khai trong folder planning; **0 link local/skill bị thiếu**, **0 lỗi số cột bảng Markdown**. PRD có 24 hàng yêu cầu (14 FR + 10 NFR); backlog có 20 hàng story (S20 tùy chọn); catalog có 20 hàng test dự kiến; có 9 CAP và 8 AD. Tổng count đối chiếu: 18.160 ảnh = 11.411 khớp grouping sơ bộ + 6.749 chưa khớp; 2.854 nhóm đã khớp, không phải tổng lá của toàn dataset. Tổng giờ core kiểm lại là 95, dự phòng 17 theo giả định 112 giờ.

Đây là kiểm tra tính nhất quán hồ sơ và khảo sát read-only, **không phải kết quả chạy T01–T20 hoặc xác nhận chất lượng mô hình/phần mềm/tư vấn**. Workflow BMAD downstream, public review chuyên môn, external labeled evaluation và implementation authorization vẫn chưa đủ điều kiện như readiness checklist.
