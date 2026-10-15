# Hồ sơ C3/S11 — đã chọn hướng demo giới hạn, chưa được publish

**Quyết định mới 15/10/2026:** Người dùng chọn “Demo giáo dục giới hạn, ghi rõ chưa được chuyên gia duyệt (khuyến nghị).” Xem [decision record](c3-policy-decision.json) có scope/version/hashes và [bảng review](publication-review-checklist.md). Lựa chọn chốt hướng policy; chưa phê duyệt nguồn, bản dịch hoặc quyền dùng. Các phương án và trạng thái “chưa duyệt” bên dưới là hồ sơ tại lúc trình lựa chọn, trước câu trả lời này.

## Bản cụ thể để review

Card `pex:disease_kb/tomato/healthy.json`, condition `TOM_HEALTHY`, draft version `phase2-healthy-v1`. Healthy chỉ là nhãn lớp lá, không chứng minh toàn cây khỏe hoặc đất/nước/phân phù hợp.

EN bất biến: “Water at the base of the plant to keep foliage dry.”

VI AI draft: **Tưới vào gốc cây để giữ lá khô.** Glossary: `base of the plant → gốc cây`; `foliage → lá`; `healthy (leaf class) → lá khỏe (nhãn lớp lá)`; `tomato → cà chua`, tên khoa học `Solanum lycopersicum`. Mọi mục chưa review ngôn ngữ/chuyên môn độc lập.

Bài học draft: quan sát lá xanh phù hợp giống và không thấy đốm/tổn thương; hiểu giới hạn ảnh lá; đọc nguyên tắc tưới tại gốc theo nguồn UMN. Không có lịch tưới, lượng nước hoặc thuốc.

Hai câu tự kiểm tra draft:

1. “Mô tả nào khớp dấu hiệu lá tham khảo trong thẻ EN?” Key `b`: màu xanh phù hợp giống và không thấy đốm hoặc tổn thương. Giải thích giữ giới hạn toàn cây; nguồn là hai pointer triệu chứng card và tài liệu phạm vi project.
2. “Nguyên tắc nào được claim và nguồn UMN hỗ trợ để giữ lá khô?” Key `a`: tưới vào gốc cây. Giải thích không suy lịch/lượng tưới; nguồn là claim và UMN Watering/Diseases.

Các choices/key/giải thích đầy đủ tại `content/phase2-healthy-v1/review-inputs.json`. Tests chỉ kiểm tính nối nguồn/key/hash/refusal, chưa đo học tập hay xác nhận lựa chọn nông học.

## Hai phương án cần quyết định của người có thẩm quyền

| Phương án | Điều kiện trước allowed bundle | Trạng thái hiện tại |
| --- | --- | --- |
| Demo giáo dục `source_checked` có nhãn giới hạn | C3 phê duyệt mode/version/scope cho đúng một claim và lesson, xác định actor review nguồn và nghĩa VI thật, chốt rights/context/nhãn giới hạn; S11 thiết kế chuyển đổi gate có regression riêng | Chưa duyệt. Validator hiện tại vẫn yêu cầu expert approval; không có cờ bypass hoặc tự sửa gate trong S10 |
| Giữ yêu cầu expert approval hiện tại | Có reviewer chuyên môn xác định, review nghĩa VI riêng, approved scope/actor/role/date/hash/version và rights/context rõ cho claim/lesson này | Chưa có reviewer; guidance tiếp tục blocked |

Hướng được chọn hiện tại là demo `source_checked` giới hạn. Thành viên nhóm/peer có thể review nguồn và nghĩa VI, ghi vai trò thật; không cần gán chuyên môn nông học cho họ. Một AI hoặc synthetic fixture không thay các lượt review này. Không hỏi lại lựa chọn mode đã được người dùng chốt.

## Trạng thái bàn giao

- Source check: AI đối chiếu nguyên tắc trên primary UMN, ngày 15/10/2026; không independent approval.
- VI/glossary/lesson: AI-authored draft; translation/domain reviewer null, review pending.
- Rights: redistribution và per-claim third-party scope pending theo ledger.
- Guidance: `display_allowed=false`, mọi lookup 10 lớp guidance rỗng.
- S11 chưa có `publish_knowledge`, allowed bundle hoặc positive real lookup; S06 còn bị chặn bởi C3 cùng các prerequisites khác. Không đổi ticket store/done state.

Bước S11 còn lại: review chính xác text/terms/questions cùng hashes hiện tại, ghi reviewers thật và chốt quyền dùng/đóng gói; sau đó triển khai publisher/gate riêng theo policy/version đã chọn và kiểm một card thật được phép. Không sửa validator niêm phong hoặc tái dùng threshold fixture 0,7 như production policy. Hiện chưa có approval thật nên S11 và Phase 2 vẫn chưa hoàn tất.
