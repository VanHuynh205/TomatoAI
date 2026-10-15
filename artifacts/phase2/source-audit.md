# Đối chiếu nguồn cho một claim — AI check

Ngày kiểm: 15/10/2026. Actor: Codex (GPT-6), AI assistant; không reviewer độc lập, không chuyên gia phê duyệt.

Nguồn: [University of Minnesota Extension — Growing tomatoes](https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/growing-tomatoes). Parent và investigator đã đọc nguồn primary trong phiên thực thi; metadata được giữ trong `review-inputs.json/source_checks`, không lưu toàn trang có copyright.

- `Diseases`: hỗ trợ tưới ở gốc để hạn chế làm ướt phần lá.
- `Watering`: hỗ trợ tránh tưới làm ướt lá. Đủ căn cứ đối chiếu nguyên tắc của claim duy nhất đã chọn; không xác nhận mọi management claim của healthy.
- Phạm vi nguồn: làm vườn tại Minnesota. Không nhập các lịch/tần suất/lượng nước hoặc khuyến nghị dinh dưỡng theo địa phương vào artifact này. Không suy thuốc, hiệu quả, chẩn đoán hoặc lịch tưới ở Việt Nam.

Claim nguồn bất biến: `ir-claim:healthy:cultural:2`; card `pex:disease_kb/tomato/healthy.json`; pointer `/content_en/management/cultural/2`; raw SHA-256 `89a50caefe302b04ac61b3ccfd35f43054335be3ad5bf63eb8a9cd0025cddb83`. EN không sửa; VI được viết bởi AI bằng đối chiếu trên, không gọi dịch API.

Observation trong bài học là nội dung draft dựa trên hai pointer triệu chứng của card. Giới hạn healthy là lớp lá dựa trên mục “Hướng dẫn có ngữ cảnh và giới hạn” của `planning/tomato-desktop/knowledge-localization-edtech.md`, được hash-pin riêng. Không gán tuyên bố về classifier cho UMN hoặc nguyên văn raw card.

Rights ledger hiện ghi parent repository khai báo CC BY 4.0 nhưng quyền embedded claims/third-party excerpts và redistribution chưa được cleared. Bản này chỉ chuẩn bị draft theo quyền thực thi S10 của người dùng; không thay ledger, không public release.

Source-checked không phải domain approval; dịch có SHA-256 không phải reviewed meaning. Domain/translation review và C3 đều pending. Không có positive real guidance fixture hoặc claim expert_approved.
