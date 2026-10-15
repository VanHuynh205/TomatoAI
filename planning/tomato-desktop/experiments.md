# Kế hoạch thực nghiệm EfficientNet và ResNet50

**Cập nhật Setup 13/10/2026:** tên đã chốt “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”; phạm vi nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50. Không tối ưu canh tác; WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung. Runtime đã setup; tài liệu vẫn là draft chưa tiếp nhận chính thức, xem [README](README.md) và [setup-report](setup-report.md).

Ngày 13/10/2026. **Tất cả cấu hình, lịch huấn luyện, ngưỡng và mục tiêu là đề xuất; chưa train hoặc đo metric.** Dữ liệu thực tế ở data-audit; phần cứng do người dùng khai báo, chưa kiểm device/CUDA runtime.

## Câu hỏi nghiên cứu

RQ1: Transfer learning EfficientNet-B0 và ResNet50 khác nhau thế nào về macro-F1/recall từng lớp trên cùng benchmark nhóm lá? RQ2: Fine-tune cải thiện gì so với chỉ train head trong cùng kiến trúc? RQ3: Trade-off chất lượng–CPU latency–RAM nào phù hợp desktop offline? RQ4: Kết quả suy giảm thế nào trên ảnh độc lập ngoài miền và cơ chế từ chối có hạn chế gì?

Hai CNN là **DL thuộc ML**. Không cần một mô hình truyền thống để có đóng góp ML. Nếu rubric yêu cầu baseline riêng: đề xuất backbone đóng băng + đặc trưng → scaler fit train → SVM (classifier truyền thống) cùng split; đây là hệ hybrid DL feature + ML classifier, không baseline thuần không-DL. Chi phí feature extraction/tuning/kernel/RAM và ngân sách phải được duyệt. Không triển khai SVM/ensemble trong MVP mặc định.

## Hai cấu hình nền đề xuất cần duyệt C1

| Hạng mục | EfficientNet | ResNet50 |
| --- | --- | --- |
| Biến thể | **EfficientNet-B0**; B1/B2 chỉ nếu pilot/nhu cầu chứng minh và duyệt | **ResNet50**, torchvision implementation V1.5 |
| Framework | PyTorch + torchvision, pin bộ version tương thích Python/CUDA/Windows sau pilot | Cùng framework/version |
| Pretrained | `EfficientNet_B0_Weights.IMAGENET1K_V1` | `ResNet50_Weights.IMAGENET1K_V1` cho baseline ban đầu |
| Nguồn | Official torchvision weights registry/docs R06 | Official torchvision weights registry/docs R07 |
| Quyền sử dụng | License thư viện BSD không tự áp dụng cho weights/ImageNet; ledger chưa đóng | Cùng checkpoint quyền dùng/phân phối |
| Head | Thay output ImageNet bằng 10 mã chuẩn, ghi class order | Tương tự 10 lớp |
| Transform eval tham chiếu V1 | Resize cạnh ngắn 256, bicubic, center crop 224; RGB/float/normalize theo weights | Resize cạnh ngắn 256, bilinear, center crop 224; normalize theo weights |
| Train transform dự kiến | Crop 224/flip/rotate nhẹ theo nhãn, không xóa dấu hiệu; thống kê chỉ train | Cùng family augmentation và ngân sách; interpolation riêng tương thích weights |

Thông số transform lấy từ [B0 docs](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.efficientnet_b0.html) và [ResNet50 docs](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html); lưu recipe thực tế khi pin version. Không dùng `DEFAULT` để tránh alias thay đổi. ResNet50 V2 là tùy chọn đổi recipe/pretraining, không mặc định gọi khác biệt V1–V2 là tác động kiến trúc thuần.

B0 được đề xuất vì input 224 và chi phí tương đối nhẹ; không bảo đảm vừa batch cụ thể trên RTX 3050 4 GB. Pilot đề xuất batch vật lý 8; nếu OOM thử 4 rồi 2, gradient accumulation giữ effective batch 16 cho cả hai nếu phù hợp. AMP chỉ nếu kiểm numeric stability và device hỗ trợ. Không bắt B0 phải dùng batch vật lý của ResNet nếu lãng phí, nhưng log effective batch/steps và device. Colab là compute training có thể thay đổi GPU; không trộn run mà không ghi hardware/session/runtime. CPU app vẫn phải đo trên máy mục tiêu.

## Chuẩn bị dữ liệu và split trước augmentation

1. Khóa provenance/version raw; inventory + decoding/hash toàn bộ được thực hiện trong **phiên triển khai được phép**. Giữ raw; corruption/nhãn nghi vấn vào exclusion ledger dẫn xuất với lý do và review.
2. Đối chiếu map/CSV/alias. Group key namespace class/source/leaf; UUID đầu filename không mặc nhiên là leaf_id. Không merge group khác lớp chỉ vì cùng số `1.0`.
3. Exact hash và near-duplicate là bằng chứng bổ sung. Gom ảnh cùng lá, bản trùng/gần trùng, color/grayscale/segmented (nếu bổ sung sau) thành connected components. Cross-label duplicate là conflict cần review, không tự sửa nhãn hoặc đặt hai tập khác nhau.
4. 6.749 ảnh chưa khớp bằng lookup sơ bộ cần alias/group recovery; hiện chưa có manifest an toàn cho full 18.160 ảnh. Không split ngẫu nhiên phần này. Nếu không phục hồi: benchmark trên subset có grouping chứng minh; loại các ảnh chưa rõ, báo class support/coverage và xem lại khả năng 10 lớp. Mosaic hiện 0 match → blocker cho benchmark 10 lớp có grouping, không được che bằng split ngẫu nhiên. Có thể cần evidence/manual grouping mới hoặc scope dataset bổ sung đã duyệt.
5. Đề xuất grouped stratified **70/15/15 train/validation/test** theo component, seed cố định, tỷ lệ xấp xỉ vì group không chia. Báo số ảnh và group từng lớp/tập thực tế. Nếu chọn official 80/20, cần kiểm manifest nguồn và chia train thành train/val theo group; không tự giả định card đảm bảo bản local. Hai cách là lựa chọn cần chốt, không trộn kết quả.
6. Khóa test manifest/hash và hạn chế đọc test output cho tới C4. Augmentation chỉ train sau split. Resize/normalization constants của pretrained là fixed recipe, không fit từ test. Mọi scaler/statistics/class weights/sampler/feature classifier fit **train**; policy/config chọn **validation**.
7. Nếu tune calibration/rejection: tách group trong validation thành phần selection và calibration hoặc grouped cross-validation trong train nếu support nhỏ; chốt trước run. Tập âm/OOD dùng để tune policy khác hoàn toàn tập OOD cuối. Không bỏ ảnh khó sau khi nhìn test.

T15 phải chứng minh giao các tập group/duplicate component bằng rỗng, đúng class order, ảnh training augmented không xuất hiện như test gốc. Grouping thiếu là blocker khoa học, không chỉ là việc housekeeping.

## Transfer learning hai giai đoạn riêng mỗi kiến trúc

**B0:** train classification head với backbone đóng băng; model mode/BatchNorm phải được kiểm soát, không để running statistics của backbone đổi ngoài chủ ý. Sau đó fine-tune block cuối được chọn; nếu validation ổn và còn budget, mở rộng một phần backbone với LR thấp hơn head. Ghi chính xác block/parameters trainable và mode BN.

**ResNet50:** train head với backbone đóng băng và BN policy xác định; fine-tune `layer4` là ứng viên ban đầu, không gọi đây là lịch tối ưu. Có thể thử thêm `layer3` sau evidence, trong ngân sách. Ghi loss/trainability/BN như B0.

Đề xuất khởi điểm: head 3–5 epoch, fine-tune tối đa 20 epoch, early stopping patience 4 theo validation macro-F1, tổng hard cap 30 epoch/run. Hai candidate LR backbone khoảng 1e-5 và 3e-5, head cao hơn (ví dụ 1e-3 lúc head, 1e-4 lúc fine-tune), AdamW là ứng viên; weight decay/scheduler/class weighting ghi config, không khẳng định tối ưu. Chốt candidate grid trước run, không mở tìm kiếm không giới hạn. Không vừa thay optimizer, augmentation, loss và unfreeze trong một ablation không giải thích.

Mất cân bằng lớp: xem train supports, so loss chuẩn và một phương án weighting/sampling nếu cần; mọi weights từ train. Không resample val/test. Head-only là baseline DL bắt buộc trong kế hoạch vì đo được đóng góp fine-tune, không thay bằng metric pretrained ImageNet.

## Ngân sách và bảng thí nghiệm dự kiến

Đề xuất tối đa **3 cấu hình/kiến trúc** (head-only, fine-tune A, fine-tune B), seed đầu 42; cấu hình chọn bằng validation chạy thêm seed 17 và 2026 cho **mỗi** kiến trúc. Tổng tối đa 10 run, hard cap 30 epoch/run và budget compute tạm 24 GPU-giờ, **chưa biết thực tế cần bao nhiêu**. Sau pilot điều chỉnh cap trong C1, ghi lý do trước dùng test. Nhân công và GPU wall-time khác nhau. Nếu thiếu thời gian, giảm candidates đối xứng cả hai, giữ hai kiến trúc và test integrity; báo thiếu repeats nếu không chạy.

| ID | Model / cấu hình dự kiến | Seed | Val macro-F1 | Final test macro-F1 | Accuracy | Recall từng lớp | Train time | CPU p50/p95 | Peak RSS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | B0 head-only | 42 | | | | | | | |
| E02 | ResNet50 head-only | 42 | | | | | | | |
| E03 | B0 fine-tune A | 42 | | | | | | | |
| E04 | B0 fine-tune B | 42 | | | | | | | |
| E05 | ResNet50 fine-tune A | 42 | | | | | | | |
| E06 | ResNet50 fine-tune B | 42 | | | | | | | |
| E07 | B0 config đã chọn, repeat | 17, 2026 | | | | | | | |
| E08 | ResNet50 config đã chọn, repeat | 17, 2026 | | | | | | | |
| E09 | Hai model trên ảnh ngoài miền độc lập | Theo manifest | | | | | | | |
| E10 | Calibration/rejection policy đã khóa | Theo policy | | | | | | | |

Ô trống nghĩa **chưa đo**. E09/E10 là evaluation/policy, không thêm CNN; báo n/count/nguồn riêng. Lưu một hàng thực cho từng seed/run, không lấy một hàng gộp làm kết quả seed tốt nhất.

## Chọn model trước test

Đề xuất mục tiêu nội miền cần duyệt: validation macro-F1 ≥0,90, recall từng lớp ≥0,80, CPU warm p95 ≤3 s và peak RSS ≤2 GB. Không hứa đạt; test báo kết quả thật và mức đáp ứng mục tiêu, không tune lại để đủ.

Chọn config từng kiến trúc bằng validation macro-F1, kiểm recall worst class, stability qua seeds và chi phí. Chọn **một** model triển khai trước khi mở test. Nếu chênh macro-F1 nhỏ hơn 0,01 và uncertainty/seed variation không cho thấy khác biệt vững, ưu tiên model đạt recall/resource budget với latency/RAM thấp hơn. Quy tắc 0,01 là đề xuất, không p-value. Nếu cả hai không đạt, báo kết quả/phân tích và xin điều chỉnh scope hoặc thêm run train/val; không đổi winner bằng test. Ensemble chỉ thử khi được duyệt, giữ budget/latency/offline và chứng minh lợi ích validation.

Khóa checkpoint, preprocessing, label order, confidence policy và selection rationale C4. Sau khóa, test cuối có thể báo cả hai model để so sánh khoa học, nhưng model triển khai vẫn được chọn trước đó. Nếu lỗi pipeline nghiêm trọng làm test không hợp lệ, ghi incident, không gọi sửa và chạy lại là “chưa từng thấy test”; cân nhắc test độc lập mới được duyệt.

## Đánh giá và phân tích

- Classification: macro-F1; precision/recall/F1/support mỗi lớp; confusion matrix với ordered labels; accuracy bổ trợ; cả predicted class lẫn rejection behavior phải báo riêng. Rejected ảnh không được biến mất khỏi mẫu số để tăng accuracy. Báo coverage, accepted risk/error và số reject; confusion matrix extended có cột unknown nếu policy bật.
- Stability: seed results và mean/std; confidence interval bootstrap **theo group**, không theo từng ảnh cùng lá. Không suy significance chỉ từ accuracy khác nhỏ. Báo thiếu support/CI rộng.
- Performance: training elapsed/GPU hours/peak VRAM; app CPU batch1, 10 warm-ups +100 đo, cold load riêng; p50/p95 và peak RSS; ghi power/threads/Windows/device. Không dùng latency GPU Colab làm latency desktop.
- Failure analysis: từng cặp nhầm, lớp nhỏ mosaic, healthy giả, nhện với đốm lá, thay background/lighting/blur. Không vẽ vùng tổn thương hoặc mức độ mà không model/annotation hỗ trợ.

## Ảnh độc lập, OOD và từ chối

**Chưa có bộ ảnh vườn có nhãn độc lập hoặc người xác minh.** Kế hoạch S16: nếu có quyền/nguồn, thu/bổ sung tập từ cây/buổi/vườn/source khác; grouped theo cây/buổi/người chụp, có provenance/consent/license và nhãn review. Đề xuất khoảng 10–20 ảnh mỗi lớp nếu khả thi, không là yêu cầu đủ chứng minh generalization. Không thu đủ lớp thì báo lớp vắng và chỉ metric cho support thật. Không lấy ảnh PlantVillage khác biến thể làm external test.

Nếu chỉ có ảnh web chưa xác minh nhãn, dùng **qualitative challenge set**, không báo accuracy bệnh của nó. Nếu không có nguồn ảnh/nhãn, ghi external metric “chưa đánh giá” và giới hạn bảo vệ; không suy điểm nội miền ra vườn. Thu/tải thêm chỉ sau được phép ở phiên sau.

Policy dự kiến tách validation chất lượng ảnh (blur/exposure/size), confidence/margin/calibration và bộ challenge non-leaf/non-tomato/unseen conditions. Softmax cao vẫn có thể sai/OOD; threshold không tạo open-set detector hoàn hảo. Tập negative tune/test tách nguồn và group; báo false accept OOD, false reject known, coverage và selective error. Threshold phải chọn validation có ground truth; nếu thiếu negative validation, chỉ tuyên bố rule chất lượng/uncertain đã thử, **không** tuyên bố phát hiện non-tomato/OOD tin cậy. UI luôn nêu phạm vi, cho chụp lại và không có hướng dẫn nhãn khi non-accepted.

## Hồ sơ tái lập phải tạo sau

Mỗi run: dataset revision/exclusion/hash, split/group manifest/hash và seed, config/grid/budget, code revision, Python/torch/vision/CUDA/cuDNN/driver versions, device/VRAM, seeds Python/NumPy/torch/data workers, deterministic settings và hạn chế tái lập khác thiết bị, transform/augmentation/loss/optimizer/scheduler, parameters trainable/BN mode, class supports, checkpoint hash, logs train/val, selection rationale. Final model card kèm test/OOD/rejection/performance và intended use/limits. Không ghi API key/Colab token vào notebook/log/config.
