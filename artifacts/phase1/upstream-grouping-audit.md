# Đối chiếu grouping với nguồn chính thức

Kiểm tra ngày 15/10/2026, bổ sung sau final review kỹ thuật. Chỉ đọc metadata/source công khai; không tải ảnh, weights, sửa raw hoặc selected run. Evidence HTTP, thời điểm, URLs, bytes và SHA-256 ở [fetch-evidence](upstream-metadata/fetch-evidence.json); kết quả so sánh ở [comparison](upstream-metadata/comparison.json).

## Nguồn và kết quả trực tiếp

- GitHub `spMohanty/PlantVillage-Dataset`, HEAD tại thời điểm kiểm: `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`, trùng revision đã chọn. [Leaf map](https://github.com/spMohanty/PlantVillage-Dataset/blob/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a/leaf_grouping/leaf-map.json) và [Target Spot CSV](https://github.com/spMohanty/PlantVillage-Dataset/blob/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a/leaf_grouping/filtered_leafmaps/Tomato___Target_Spot.csv) đều byte-identical với raw hiện có; không tìm thấy bản sửa mới ở revision này.
- [Danh mục CSV chính thức](https://github.com/spMohanty/PlantVillage-Dataset/tree/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a/leaf_grouping/filtered_leafmaps) có chín CSV cà chua, không có CSV mosaic. Đây là kết luận trong danh mục đã kiểm, không phải khẳng định không thể tồn tại annotation khác.
- Hugging Face `mohanty/PlantVillage`, revision `9e97599868962bd0079b8db4b7f1efa9185fa1e7`: [leaf map](https://huggingface.co/datasets/mohanty/PlantVillage/blob/9e97599868962bd0079b8db4b7f1efa9185fa1e7/leaf_grouping/leaf-map.json) cũng byte-identical với raw hiện có. Đổi kênh truy cập không bổ sung grouping.

## Vì sao không nhập leaf_id từ loader

[Loader chính thức](https://github.com/spMohanty/PlantVillage-Dataset/blob/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a/plant_village.py#L171) tra leaf map, nhưng khi không có key hoặc không chọn được class thì tạo `fallback_` từ image identifier. Vì vậy, một chuỗi leaf_id không chứng minh physical leaf identity. [Dataset card](https://huggingface.co/datasets/mohanty/PlantVillage) mô tả split có grouping; mã loader cho thấy phải kiểm nguồn từng ID trước khi dùng.

Suy luận kỹ thuật: nhập toàn bộ leaf_id của bản Hub có thể biến ảnh chưa có annotation thành nhóm dựa trên tên. Điều đó không đáp ứng C2 của dự án. Không áp fallback, không coi lời mô tả trên dataset card là bằng chứng đầy đủ cho hai lớp đang thiếu.

## Tác động đến Phase 1

Không có delta grouping đủ căn cứ trong các nguồn đã kiểm. S02/S03 vẫn built; S04 vẫn blocked, zero assignments. Technical support của Target Spot và mosaic vẫn bằng zero theo [completion audit](completion-audit.json). Chưa có approval nhãn/class/rights mới.

Để mở full10 cần bằng chứng/annotation leaf identity có thể truy nguyên, xử lý review còn treo và approval C2/quyền theo scope. Nếu đổi thành pilot subset thì cần quyết định scope riêng; không gọi pilot là nghiệm thu full10. Không có tiến trình hay external job đang chạy để chờ. Phần kỹ thuật hiện tại không thể tự tạo bằng chứng scientific approval hoặc annotation còn thiếu.
