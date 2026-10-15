# Phase 0 — Quyết định, quyền sử dụng và nền tảng

Ngày 15/10/2026, Asia/Bangkok. Phạm vi: **EPA.S01**, theo [kế hoạch chính thức](../../_bmad-output/initiative-tomato-desktop/app-development-plan/app-development-plan.md). Người dùng cho phép thực hiện Phase 0; không mở rộng sang benchmark, dịch hàng loạt, train hoặc xây app sản phẩm.

## Xác nhận và trách nhiệm

| Mục | Quyết định / bằng chứng | Trạng thái và người xử lý |
| --- | --- | --- |
| C0: nhóm và thời gian | Người dùng xác nhận nhóm **3 người**, làm mỗi tối; bảo vệ khoảng **hai tháng nữa**, chưa có ngày cụ thể | Đã xác nhận định tính; nhóm bổ sung giờ/người/tuần, rubric và deadline khi trường công bố |
| Phạm vi “thẩm định” | Hỗ trợ quan sát ảnh, đối chiếu tri thức và nêu giới hạn; không xét nghiệm hoặc xác nhận tác nhân từ ảnh | Giữ spec; rubric của giảng viên còn thiếu |
| Tài khoản | Dùng trực tiếp, không đăng nhập; hồ sơ/lịch sử local tùy chọn, history mặc định tắt | Đã chốt; không tạo server/password/RBAC |
| Công nghệ | Python/PySide6 Widgets/PyTorch/torchvision; PyInstaller onedir | Hướng đã được người dùng chọn; phiên bản kiểm thực tế trong compatibility.json |
| C1: compute | Laptop sinh viên không đủ mạnh theo người dùng. Máy phiên này có Ryzen 5 5625U, khoảng 16 GB RAM, RTX 3050 Laptop 4 GB | CPU chỉ làm smoke/runtime; pilot train thuộc S05. Chưa xác nhận quyền dùng máy GPU/cloud hoặc ngân sách trả phí |
| C2: dữ liệu | Grouping Target Spot/mosaic và near duplicates chưa đủ; split 10 lớp chưa được duyệt | Chặn S04/full training; S01 không sửa dữ liệu để mở gate |
| C3: chuyên môn | Người dùng xác nhận chưa có người đủ chuyên môn về cà chua | Tiếp tục gate hiện hành: chưa đủ review/VI/quyền/context thì zero guidance. Không tự duyệt educational-demo source_checked; S11 cần quyết định riêng |
| C4: hiệu quả ngoài miền/học tập | Chưa có ground truth độc lập hoặc người tham gia được xác nhận | S16/S17 ghi evidence thật hoặc thiếu chứng cứ; không hứa accuracy/learning gain |
| C5: phát hành | Rights từng asset, notices, người review và máy Windows sạch chưa đủ | Chặn phát hành; ledger là hồ sơ kiểm kê, không là giấy phép tự cấp |

Không dùng lại giả định cũ “một sinh viên/112 giờ” làm ngân sách nhóm. Hai tháng là cửa sổ tương đối, không tự suy ngày bảo vệ chính xác. Chưa phân người A/B/C hoặc giả tên reviewer. Nhóm phân công theo ba luồng dữ liệu/model, app native, tri thức/QA khi xác nhận giờ và người sở hữu; dependency BMAD vẫn quyết định thứ tự.

## Quyết định kỹ thuật ở Phase 0

1. Dùng **CPython 3.12.14 Windows x64** đã có, môi trường riêng `.venv-phase0`; không sửa Python/package cleaning. `requirements-app.in` lưu top-level; `requirements-app.lock` khóa dependency và hash. Đây là baseline CPU/build đã kiểm, không phải CUDA training lock.
2. Kiểm `torch 2.14.1+cpu` với `torchvision 0.29.1+cpu` bằng wheel CPU chính thức và dependency metadata; kiểm thực tế quan trọng hơn bảng README có thể chậm cập nhật. Cài package phục vụ Phase 0, không tải pretrained weights/dataset mới.
3. Dùng **PySide6-Essentials 6.12.0** và shiboken cùng phiên bản; package này cung cấp module `PySide6.QtCore/QtWidgets/QtTest` cần dùng. Không cài Addons/WebEngine vì chưa có nhu cầu; ghi đúng distribution trong báo cáo, không giả đã cài meta-package `PySide6`.
4. Chọn **EfficientNet-B0** làm variant baseline cho EfficientNet và giữ **ResNet50**. B0 giảm chi phí so với variant lớn trong ngân sách laptop hạn chế; không phải kết quả chọn winner. Smoke chỉ dùng `weights=None`, head 10 đầu ra và tensor tổng hợp; không tạo checkpoint hoặc kết quả đồ án.
5. Ứng viên transfer learning: `EfficientNet_B0_Weights.IMAGENET1K_V1` và `ResNet50_Weights.IMAGENET1K_V2`; recipe đã đọc từ enum đã pin: B0 resize 256/crop 224 BICUBIC; ResNet50 V2 resize 232/crop 224 BILINEAR, cùng ImageNet mean/std và antialias. Xem `artifacts/S01/weights-metadata.json`; không ép resize/crop giống nhau. Chưa tải weights, chưa kiểm hash byte hoặc quyền pretrained assets; S05 phải hoàn tất trước dùng. CUDA/train environment và pretrained provenance vẫn pending.
6. Dùng CPU ở app đích; train head/fine-tune sau approved split bằng compute được nhóm chốt. Cân nhắc máy phòng lab hoặc notebook cloud theo quyền/budget; không đăng ký dịch vụ, gửi dataset lên cloud hoặc chi tiền trong Phase 0.
7. Giữ target/limit kế hoạch ở mức **đề xuất chưa nghiệm thu**: 20 MiB, 24 MP, cạnh dài 12.000 px, cạnh ngắn 64 px; 2 threads; hủy grace 2 s, job 15 s và cold load riêng; warm p95 ≤3 s, RSS ≤2 GB, bundle ≤1,5 GB. S05 đo pilot, nhóm/giảng viên chốt trước acceptance; forward smoke không xác nhận performance.

## Hồ sơ quyền sử dụng

[assets-rights.json](assets-rights.json) tách dataset, từng card, pretrained weights và software dependencies. Mỗi entry ghi nguồn/revision/hash hoặc nơi lưu hash, khai báo license, scope cho phép trong phiên, trạng thái phân phối và việc còn thiếu. Metadata license của repository không chứng minh quyền mọi nội dung trích bên trong; không tự đặt `safe_for_advice` hoặc `expert_approved`.

Nguồn đã đối chiếu: [Qt for Python licenses](https://doc.qt.io/qtforpython-6/licenses.html), [PyInstaller license](https://pyinstaller.org/en/stable/license.html), [Torchvision models](https://docs.pytorch.org/vision/stable/models.html). Gói Qt/third-party cần notices theo thành phần thực dùng; quyền code khác quyền pretrained weights. Chưa phát hành gói nên chưa tuyên bố license compliance hoàn chỉnh.

## Kiểm chứng và cách chạy lại

```powershell
uv venv --python 3.12 --no-project .venv-phase0
uv pip sync --python .venv-phase0/Scripts/python.exe requirements-app.lock --require-hashes --default-index https://pypi.org/simple
.venv-phase0/Scripts/python.exe scripts/checks/build_phase0.py
.venv-phase0/Scripts/python.exe -m unittest discover -s scripts/checks -p test_phase0_smoke.py -v
.venv-phase0/Scripts/python.exe scripts/checks/phase0_smoke.py
.venv-phase0/Scripts/python.exe scripts/checks/phase0_trace.py
```

Build helper giới hạn PATH của tiến trình build vào Python đang dùng và Windows, dùng `--clean` để không tái dùng graph nhiễm DLL ngoài. Không sửa PATH hệ thống. Build diagnostic tại project root:

```powershell
.venv-phase0/Scripts/python.exe scripts/checks/build_phase0.py
artifacts/S01/dist/phase0_smoke/phase0_smoke.exe
```

Bản build đầu thất bại nạp QtCore vì PyInstaller lấy `icuuc.dll` từ Codex Poppler trên PATH, thiếu các symbol ICU không suffix mà Qt yêu cầu. Có regression test RED trong `frozen-red-test.log`; bằng chứng export/source trong `icu-root-cause.json` và `dll-diagnosis.json`. Lỗi này được xử lý ở đường build, không vá Qt hoặc đổi model. Sau khi sửa ICU, regression còn phát hiện hook contrib hiện cài tìm `torchvision._C`/`torchvision.image`, trong khi torchvision 0.29.1 đã đổi sang `_C_stable`/`image_stable`. Build helper thêm đúng hai hidden import này; không bỏ đăng ký operator hoặc vá vendor. Đây là điều kiện compatibility cần giữ ở S06/S18, không phải bằng chứng generic build không cần cấu hình.

Phiên này phải dùng fallback CDN theo HTTP range vì full transfer bị chậm/retry; cả hai wheel Qt/NumPy được kiểm SHA256 đầy đủ theo PyPI và lock trước cài. Xem `local-wheel-verification.json`, `install-first-attempt.log`, `install-offline-attempt.log`, `install-local-wheels.log` và `install.log` trong artifacts. Không đổi DNS hệ thống. Lệnh sync mặc định vẫn dùng nguồn chuẩn; fallback chỉ phục vụ vận chuyển cùng wheel, không đổi phiên bản hoặc nới hash.

Chỉ chạy `uv venv` khi chưa có môi trường; không thay môi trường đang tồn tại của người khác. Log, actual versions, source/hash tracer, frozen spawn và bảo toàn nằm tại [artifacts/S01](../../artifacts/S01/). Tracer chọn hai record thật của manifest hiện hành: một grouped technical candidate và một missing-group; kiểm hash byte raw/processed và căn cứ nhóm. Technical candidate khác **training eligibility**: cả hai còn bị chặn bởi approved split/quyền/label review. Không tạo split, nhãn mới hoặc approval giả để làm hai kết quả train khác nhau.

Qt window là cửa sổ chẩn đoán tự đóng, không phải UI sản phẩm hoặc visual approval. Windows sạch/offline, resource/security/privacy/UX acceptance của app còn thuộc S06/S14/S18. Skill e2e hiện chỉ mô tả browser/iOS/Android, không có config/URL app hoặc engine Qt Windows phù hợp; không dùng browser test để tuyên bố app native đã qua E2E.

## Điều kiện bàn giao

S01 hoàn thành hồ sơ governance khi các quyết định hoặc blocker có nguồn thật và các kiểm kỹ thuật có kết quả thật. Trạng thái build/review của S01 không đóng C2/C3/C5 hoặc cho phép tự chạy S05. Người dùng duyệt `done` theo BMAD; phiên này không tự mark done hoặc thực hiện phase sau.
