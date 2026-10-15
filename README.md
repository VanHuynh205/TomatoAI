# TomatoAI

**Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua.**

Đồ án hướng tới ứng dụng desktop Windows bằng tiếng Việt, chạy offline sau cài đặt. Người dùng chọn ảnh lá cà chua để nhận gợi ý bệnh/trạng thái được hỗ trợ, đối chiếu giới hạn và đọc nội dung chăm sóc, bài học có nguồn. EfficientNet-B0 và ResNet50 là hai kiến trúc dự kiến so sánh; CNN phân loại ảnh, không tự sinh lời khuyên.

Repository lưu dataset, hồ sơ BMAD chính thức, mã xử lý dữ liệu/tri thức, kiểm thử và bằng chứng các phase gần đây. Hiện chưa có ứng dụng sản phẩm, mô hình sinh viên đã huấn luyện hoặc kết quả accuracy/F1. Một ảnh lá không thay xét nghiệm hoặc xác nhận tình trạng toàn cây.

## Bắt đầu đọc

1. [GIAI-THICH-DU-AN-TOMATOAI.md](docs/GIAI-THICH-DU-AN-TOMATOAI.md): giải thích bài toán, trải nghiệm dự kiến, nguồn dữ liệu và giới hạn. Tài liệu ghi mốc **14/10/2026**; các phát biểu tiến độ cũ cần đối chiếu checkpoint bên dưới.
2. [Kế hoạch phát triển chính thức Phase 0–9](_bmad-output/initiative-tomato-desktop/app-development-plan/app-development-plan.md): thứ tự công việc, phụ thuộc, điều kiện nghiệm thu và checkpoint thực hiện. Bản kế hoạch `adp-20261014-v1` là lộ trình chính.
3. [Đặc tả chính thức](_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/spec-tomato-desktop.md), [engineering contracts](_bmad-output/initiative-tomato-desktop/app-development-plan/engineering-contracts.md) và [UX/bảo mật](_bmad-output/initiative-tomato-desktop/app-development-plan/ux-security.md): yêu cầu và ranh giới triển khai.
4. [Initiative BMAD](_bmad-output/initiative-tomato-desktop/initiative-tomato-desktop.md) và [truy vết yêu cầu](_bmad-output/initiative-tomato-desktop/spec-tomato-desktop/requirements-traceability.md): 6 epic, 22 story và liên kết tới kiểm thử/bằng chứng.

Các hồ sơ trong [planning/tomato-desktop](planning/tomato-desktop/README.md) giữ bối cảnh và lịch sử trước tiếp nhận. Khi trạng thái khác nhau, đọc checkpoint mới nhất trong kế hoạch chính thức và báo cáo phase.

## Tiến trình hiện tại

Tổng hợp ngày **16/10/2026**, theo bằng chứng gần nhất ngày **15/10/2026**. Đây là tóm tắt hồ sơ đã có; việc đưa repository lên GitHub không phải lượt chạy lại kiểm thử sản phẩm.

| Giai đoạn | Đã có | Việc còn lại |
| --- | --- | --- |
| Chuẩn bị và planning | Đặc tả, 6 epic/22 story, kế hoạch Phase 0–9; làm sạch kỹ thuật và provenance cho các nguồn dữ liệu. | Readiness khoa học và quyền sử dụng có các điều kiện riêng. |
| [Phase 0 / S01](artifacts/S01/README.md) | Decision/rights ledger, lock môi trường, diagnostic Qt/CPU và build PyInstaller đã kiểm trên máy phát triển. | Chưa phải app sản phẩm hoặc nghiệm thu Windows sạch/offline; còn quyết định compute/quyền. |
| [Phase 1 / S02–S04](artifacts/phase1/README.md) | Inventory, provenance, điều tra grouping và pipeline benchmark có regression tests. | C2 chưa mở: grouping đầy đủ 10 lớp, identity mosaic, review nhãn/quyền và split được duyệt. Chưa có benchmark được phép train. |
| [Phase 2 / S10–S11](artifacts/phase2/README.md) | Draft một thẻ healthy EN–VI, glossary, lesson và hai quiz; S11 có API/CLI kiểm tra hồ sơ và từ chối khi thiếu điều kiện. | [S11 chưa hoàn tất](artifacts/phase2/s11/README.md): thiếu review nguồn, nghĩa VI, quyền dùng và positive publisher. Chưa có thẻ `allowed`; guidance thật vẫn rỗng. |
| Phase 3–9 | Đã có kế hoạch pilot/train, app native, so sánh mô hình, kiểm định và đóng gói. | Chưa triển khai; tiếp tục theo phụ thuộc và quyền đã chốt. |

Hồ sơ Phase 1 ghi **144/144 test pass** ở các lệnh/môi trường được mô tả trong báo cáo. Checkpoint S11 ghi parent chạy **74 test pass** trong phạm vi kiểm tra. Đây là kết quả kiểm kỹ thuật đã lưu, không phải độ chính xác mô hình hay nghiệm thu sản phẩm. E2E UI chưa chạy: chưa có app/URL/cấu hình runner phù hợp; xem từng báo cáo để biết giới hạn.

## Dữ liệu và cấu trúc

| Đường dẫn | Nội dung |
| --- | --- |
| [data/TomatoAI/data](data/TomatoAI/data/) | Dữ liệu raw, processed, registry, metadata và báo cáo; giữ nguồn gốc và phiên bản. |
| [_bmad-output](_bmad-output/initiative-tomato-desktop/) | Đầu ra planning chính thức: initiative, spec, epic/story, ticket và kế hoạch phase. |
| [scripts](scripts/) và [tests](tests/) | Cleaning, kiểm provenance/benchmark, chuẩn bị tri thức, publication refusal và regression tests. |
| [content](content/) | Input và bundle nháp Phase 2; chưa được phép dùng làm guidance runtime. |
| [artifacts](artifacts/) | Báo cáo, manifest, log kiểm thử và bằng chứng Phase 0–2. |
| [docs/development](docs/development/) | Quyết định kỹ thuật, compatibility và ledger quyền sử dụng. |

PlantVillage có **18.160 ảnh nguồn cà chua, 10 nhãn**; phần dẫn xuất giữ **18.146 ảnh** sau loại bản sao trùng byte. PlantExpertVQA-tomato có **17 thẻ tiếng Anh**, chưa phải bộ huấn luyện tư vấn có nhãn outcome. WUR, Dryad và Mendeley phục vụ nghiên cứu bổ sung, ngoài MVP. UC-IPM bị HTTP 403 trong đợt thu thập; chưa có tài liệu mới được thu và làm sạch.

**Quyền dữ liệu:** từng nguồn giữ giấy phép, tác giả và provenance riêng trong dataset/report. Xem [dataset registry](data/TomatoAI/data/dataset-registry.json) và [assets-rights.json](docs/development/assets-rights.json). Ledger vẫn ghi một số quyền theo từng asset, huấn luyện và tái phân phối là `pending`; repository công khai không thay các trạng thái đó hoặc cấp giấy phép mới. Không suy dữ liệu đã training-ready hay nội dung đã được chuyên gia duyệt từ việc có file trong repository.

## Lấy dữ liệu và chạy kiểm tra

Cần Git và Git LFS. Manifest WUR lớn được lưu bằng LFS; các dataset còn lại giữ file trực tiếp trong Git.

```powershell
git clone https://github.com/VanHuynh205/TomatoAI.git
cd TomatoAI
git lfs pull
```

Đây chưa phải ứng dụng có thể mở để nhận diện ảnh. Baseline Phase 0 là **CPython 3.12.14, PySide6 Widgets, PyTorch/torchvision, PyInstaller**; phiên bản cụ thể nằm trong [compatibility.json](docs/development/compatibility.json) và [requirements-app.lock](requirements-app.lock). Tạo môi trường mới khi chưa có:

```powershell
uv venv --python 3.12.14 --no-project .venv-phase0
uv pip sync --python .venv-phase0/Scripts/python.exe requirements-app.lock --require-hashes --default-index https://pypi.org/simple
```

Ví dụ kiểm phần benchmark và tri thức bằng môi trường phù hợp:

```powershell
.venv-phase0/Scripts/python.exe -m unittest discover -s tests/data -p test_benchmark.py -v
.venv-phase0/Scripts/python.exe -m unittest discover -s tests/knowledge -p 'test_*.py' -v
.venv-phase0/Scripts/python.exe -m unittest discover -s scripts/data -p test_review_integration.py -v
.venv-phase0/Scripts/python.exe scripts/knowledge/publish.py
```

CLI publication hiện phải trả **exit 2** cùng các lý do từ chối, không tạo nội dung được phép. Các lệnh khác, dependency cleaning riêng và điều kiện môi trường được ghi trong báo cáo phase. Một số evidence giữ đường dẫn tuyệt đối của máy gốc; cần đối chiếu đường dẫn khi tái lập trên máy khác. Không ghi đè raw, bundle hoặc artifact đã seal để chạy thử.

Repository loại trừ `AGENTS.md`, skill, cấu hình/session/cache agent, virtualenv, `node_modules`, bản backup setup và binary/wheel có thể tạo lại. Các bản HTML phụ trợ trong `cultivation_metadata/` cũng không đưa lên vì có thể nhúng token dịch vụ bên thứ ba; dữ liệu bảng, metadata JSON và báo cáo vẫn có. Các hồ sơ lịch sử có thể còn tham chiếu HTML này hoặc binary chỉ giữ trên máy gốc. Đầu ra BMAD chính thức và bằng chứng phát triển vẫn được giữ.
