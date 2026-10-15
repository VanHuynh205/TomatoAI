# S11 — Bảng review thẻ demo đầu tiên

Ngày 15/10/2026. Người dùng đã chọn demo giáo dục giới hạn, có nhãn **“Demo giáo dục giới hạn — nội dung chưa được chuyên gia duyệt.”** Đây là bảng thực hiện review còn thiếu, chưa phải biên bản duyệt. Không có tên reviewer hoặc ngày duyệt nào được điền thay người thật.

## Bản cần review

- [Editorial input](../../content/phase2-healthy-v1/review-inputs.json): EN–VI, glossary, lesson, đầy đủ choices/key/feedback.
- [Draft sinh từ input](../../content/phase2-healthy-v1-bundle/card-draft.json): claim/source/mapping và hashes.
- [Decision record](c3-policy-decision.json): scope đúng version, card/claim/translation/glossary/lesson hashes. Không review một bản rồi áp cho bản khác.
- [Source audit](source-audit.md): đối chiếu AI đã làm; không thay review độc lập.

Card `pex:disease_kb/tomato/healthy.json`, condition `TOM_HEALTHY`, version `phase2-healthy-v1`. Claim duy nhất `ir-claim:healthy:cultural:2`, pointer `/content_en/management/cultural/2`.

EN: “Water at the base of the plant to keep foliage dry.”

VI: “Tưới vào gốc cây để giữ lá khô.”

## Việc còn thiếu và bằng chứng cần ghi

| Lượt kiểm | Việc thực hiện | Biên bản cần có | Hiện tại |
| --- | --- | --- | --- |
| Nguồn và context | Thành viên nhóm/peer đọc mục Watering và Diseases của [UMN Extension](https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/growing-tomatoes), đối chiếu claim; xác nhận không thêm lịch/lượng tưới hoặc suy điều kiện Việt Nam từ số liệu Minnesota | Actor, vai trò thật, ngày, URL/mục, kết luận và giới hạn; hash/version claim đã kiểm | Pending; mới có AI source check |
| Nghĩa VI | Người thật đối chiếu câu EN–VI và glossary, giữ mục đích giữ lá khô; healthy chỉ là lớp lá, không bảo đảm toàn cây khỏe | Actor, vai trò, ngày; kết luận riêng với review nguồn; hashes VI/glossary | Pending; bản dịch do AI soạn |
| Lesson/quiz | Kiểm ba phần bài học và hai câu. Câu quan sát key `b` trỏ dấu hiệu lá; câu tưới key `a` trỏ claim/UMN. Kiểm mọi distractor và giải thích không thêm khuyến cáo | Actor, ngày, lesson hash, hai question IDs/keys; sửa hoặc chấp nhận từng phần | Pending; mới kiểm logic và nối nguồn |
| Quyền dùng/đóng gói | Ghi căn cứ và phạm vi dùng cho card dẫn xuất, bản dịch, nguồn tham khảo và trích dẫn; phân biệt demo với public redistribution | Actor, ngày, asset/claim IDs, căn cứ/phạm vi được phép và điểm còn thiếu | Pending trong rights ledger; lựa chọn demo không tự cấp quyền |
| S11 kỹ thuật | Khi có hồ sơ thật: `publish_knowledge`, policy/version mới; tests missing actor, stale EN/VI, chemical/context/policy null và positive card thật | Command/log, sources/role/scope hiển thị, refusal rỗng, bundle hash/version | Chưa triển khai; không sửa gate niêm phong |

Có thể phân công trong nhóm ba người; không tự đặt tên hoặc vai trò chuyên gia. AI tác giả bản nháp không được tự ký các lượt human review. Nếu nội dung đổi, tăng version dẫn xuất và review lại hashes bị ảnh hưởng; không ghi đè raw hoặc artifact đã niêm phong.

## Tiêu chí mở milestone

S11 chỉ đạt khi có hồ sơ review thật cho đúng nội dung, quyền sử dụng rõ theo scope demo, publisher đã kiểm và một positive lookup thật. Thẻ hiển thị phải mang nhãn giới hạn, source/version/role/scope; không có thuốc/liều/PHI hoặc suy lượng nước/phân từ ảnh. Hiện `display_allowed=false`, 10/10 lớp lookup rỗng. Không có card allowed để bàn giao S06.

Tài liệu này không xác nhận hiệu quả nông học, hiệu quả học tập hoặc quyền public release. Thiếu chuyên gia không còn là blocker riêng cho mode demo đã chọn; thiếu human source/VI review và căn cứ quyền vẫn là blocker hiện tại.
