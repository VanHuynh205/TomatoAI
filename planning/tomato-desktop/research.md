# Nghiên cứu nguồn chính thức và giới hạn bằng chứng

**Cập nhật Setup 13/10/2026:** tên đã chốt “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”; phạm vi nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50. Không tối ưu canh tác; WUR/Dryad/Mendeley chỉ là tài nguyên nghiên cứu bổ sung. Runtime đã setup; tài liệu vẫn là draft chưa tiếp nhận chính thức, xem [README](README.md) và [setup-report](setup-report.md). Kết quả khảo sát dưới đây giữ nguyên theo thời điểm ban đầu; setup không làm mới số liệu hoặc làm sạch dữ liệu.

Truy cập ngày **13/10/2026**. Nghiên cứu độc lập làm đầu vào `bmad-deep-recon`; chưa chạy workflow recon vì thiếu runtime. Chỉ đọc tài liệu/metadata, không tải weights/dataset. Link là nguồn cho claim, không chứng minh đã áp dụng API hoặc chạy thí nghiệm.

## Các quyết định có bằng chứng

| ID | Claim/bằng chứng đã đọc | Hệ quả đề xuất | Điều chưa kiểm chứng |
| --- | --- | --- | --- |
| R01 | [PlantVillage repository](https://github.com/spMohanty/PlantVillage-Dataset) mô tả ảnh color/grayscale/segmented và leaf grouping | Giữ group qua các biến thể, ưu tiên RGB local | Local chỉ có color, grouping chưa phủ hoàn toàn |
| R02 | [PlantVillage card](https://huggingface.co/datasets/mohanty/PlantVillage) ghi CC BY-SA 3.0 và trường leaf_id trong card | Lưu revision/attribution, rà nghĩa vụ dữ liệu dẫn xuất | Không suy giấy phép checkpoint từ giấy phép dataset |
| R03 | Mohanty, Hughes & Salathé (2016), [Using Deep Learning for Image-Based Plant Disease Detection](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2016.01419/full) nghiên cứu nhận diện trong dữ liệu ảnh có kiểm soát và đánh giá ảnh điều kiện khác | Đánh giá miền ngoài vườn tách khỏi benchmark | Không chuyển metric bài báo thành metric đồ án |
| R04 | Tan & Le (2019), [EfficientNet](https://proceedings.mlr.press/v97/tan19a.html) mô tả cân bằng depth/width/resolution | B0 là điểm xuất phát nhẹ cho 4 GB VRAM | B0 tốt nhất trên dữ liệu này chưa được chứng minh |
| R05 | He và cộng sự (2015), [Deep Residual Learning](https://arxiv.org/abs/1512.03385) dùng residual learning | Giữ ResNet50 làm kiến trúc so sánh đã chốt | Không chọn winner bằng uy tín kiến trúc |
| R06 | [torchvision EfficientNet-B0](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.efficientnet_b0.html): weights IMAGENET1K_V1; transform của weights, khoảng 5,29 triệu tham số bản ImageNet | Pin enum cụ thể, không dùng alias DEFAULT | Số tham số head 10 lớp và RAM/latency phải đo lại |
| R07 | [torchvision ResNet50](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html): V1/V2 có recipe khác; torchvision dùng ResNet V1.5; khoảng 25,56 triệu tham số bản ImageNet | Ghi rõ implementation và weights V1 cho so sánh ban đầu | V2 chỉ thêm nếu còn ngân sách và ghi yếu tố recipe |
| R08 | [Models and pre-trained weights](https://docs.pytorch.org/vision/stable/models.html) cảnh báo weights có điều kiện riêng; preprocessing phụ thuộc version | Không đồng nhất giấy phép thư viện và weights; không khởi tạo tải online trong app | Điều kiện quyền dùng/phân phối weights chưa được đóng |
| R09 | [PyTorch serialization](https://github.com/pytorch/pytorch/blob/main/docs/source/notes/serialization.md) mô tả weights_only hạn chế unpickling; không bảo đảm chống mọi DoS/memory corruption | State dict first-party, allowlist model, hash, schema/resource validation | Không coi weights_only là sandbox tuyệt đối |
| R10 | [Qt for Python](https://doc.qt.io/qtforpython-6/index.html) là Python binding chính thức cho Qt; [licenses](https://doc.qt.io/qtforpython-6/licenses.html) có LGPL/commercial và thành phần bên thứ ba | Đề xuất PySide6 Widgets cho desktop native, kiểm giấy phép các module thật sự dùng | Chưa thử gói binary hoặc chốt nghĩa vụ phân phối |
| R11 | [Tkinter](https://docs.python.org/3/library/tkinter.html) là giao diện Python cho Tcl/Tk | Là phương án đơn giản hơn nếu Qt/license/packaging không phù hợp | Chưa làm benchmark UX/packaging hai stack |
| R12 | [PyInstaller usage](https://pyinstaller.org/en/stable/usage.html), [license](https://pyinstaller.org/en/stable/license.html) mô tả bundle và ngoại lệ phân phối | Bắt đầu onedir trên Windows, kiểm máy sạch | Kích thước, antivirus false positive, DLL/plugin chưa đo |
| R13 | [Pillow Image](https://pillow.readthedocs.io/en/stable/reference/Image.html) mô tả cảnh báo decompression bomb | Giới hạn bytes/pixel, xử lý warning/error thay vì tắt bảo vệ | Ngưỡng app là đề xuất, chưa benchmark |
| R14 | [UMN late blight](https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/disease-management/late-blight) phân biệt Phytophthora là water mold | Taxonomy dẫn xuất không gọi late blight đơn giản là nấm thật | Hướng dẫn địa phương Việt Nam còn thiếu |
| R15 | [UMN tomato leaf spots](https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/yard-and-garden-problems/tomato-leaf-spot-diseases) trình bày triệu chứng/phòng ngừa các bệnh đốm lá | Đối chiếu claim theo trạng thái, ưu tiên vệ sinh/tưới phù hợp | Không tự áp dụng thuốc/khuyến cáo vùng Minnesota tại VN |
| R16 | [UC IPM spider mites](https://ipm.ucanr.edu/home-and-landscape/spider-mites/) phân biệt nhện và triệu chứng chấm li ti | Nhện là tác nhân gây hại; cần chỉ dẫn quan sát mặt dưới lá | Không xác nhận nhện thực trên ảnh mẫu chỉ từ tên lớp |
| R17 | [Colab FAQ](https://research.google.com/colaboratory/faq.html) nói tài nguyên/GPU/limits thay đổi và không được bảo đảm | Colab chỉ là training compute tùy chọn, lưu checkpoint/provenance và có kế hoạch máy local | Không dự toán dựa trên một GPU/VRAM/session chắc chắn được cấp |
| R18 | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) có attribution/share-alike với nội dung thích nghi; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) có attribution và chỉ rõ thay đổi | Ledger phân biệt ảnh/tri thức dẫn xuất, giữ notices/nguồn và license tương ứng | Không suy tự động nghĩa vụ checkpoint; phải đọc legal text và điều kiện asset cụ thể trước phân phối |

Publication date: R03 2016, R04 2019, R05 2015; các trang tài liệu kỹ thuật không cố gán ngày công bố, ghi access date. Version hiển thị của trang stable thay đổi theo thời gian; **không** dùng để tự pin phiên bản tương lai. Khi được phép chuẩn bị môi trường, kiểm tương thích Python/PyTorch/torchvision/CUDA với Windows và máy thật rồi lưu lock/version.

## Nguồn local và nguồn chưa xác minh

PlantExpert README local, 17 JSON và cache metadata đã đọc; nguồn người dùng chỉ định là [PlantExpertVQA tomato](https://huggingface.co/datasets/SyedNazmusSakib/PlantExpertVQA/tree/main/disease_kb/tomato). Web tool không mở được trang tree/card/raw trong lượt này. Vì vậy schema/count/provenance/CC BY 4.0 trong hồ sơ là **quan sát file local và lời khai card**, chưa xác thực remote hiện tại. Không suy ra có parquet QA đã tải.

Giấy phép thư viện PyTorch có các điều kiện BSD-style trong [LICENSE chính thức](https://github.com/pytorch/pytorch/blob/main/LICENSE); torchvision có BSD 3-Clause tại [LICENSE](https://github.com/pytorch/vision/blob/main/LICENSE). Đây không là giấy phép mặc định cho ImageNet, ảnh thực tế hay mọi trọng số. Story S01 phải hoàn thiện ledger gồm asset, tác giả, URL/revision, quyền dùng/biến đổi/phân phối, attribution/notice và trạng thái xác minh. Nếu điều kiện chưa rõ, chặn phân phối artifact liên quan và tìm nguồn/permission phù hợp trong phiên được phép; không suy đoán “nghiên cứu nên luôn được”.

## Nghiên cứu cần tiếp tục

1. Grouping: chứng minh alias tên, kiểm phần chưa khớp và CSV khác count; kiểm trùng/gần trùng.
2. Compute: pilot B0/ResNet50 cùng 224 px trên 4 GB; đo batch, epoch time và thermal/throttle. Colab không có GPU/VRAM bảo đảm.
3. Tri thức: đối chiếu từng claim, bổ sung URL/trang/source cụ thể; tìm người đủ chuyên môn hoặc giảm mức tuyên bố của sản phẩm demo.
4. Lệch miền: nguồn ảnh độc lập có provenance và quyền sử dụng, nhãn xác minh; không tải thêm trong lượt này. Nếu không có, giữ blocker external validity.
5. Dịch local: chỉ chọn model dịch sau kiểm tra license, chất lượng EN–VI nông nghiệp và RAM; không thêm dependency/model chỉ để ghi tên lĩnh vực.
