---
title: "giải grouping và trùng"
ticket: S03
status: built
---

# S03 — Grouping hoặc quarantine có căn cứ

Thực hiện ngày 15/10/2026. `resolve_groups` tạo `artifacts/group-resolution.json` từ selected-run hashes; union cùng leaf, byte/pixel duplicate và sealed components. Cross-label conflicts hoặc gần trùng chưa duyệt quarantine cả component. Mỗi ảnh có đúng một disposition; không sinh leaf ID từ tên ảnh.

18.160 source gồm 11.411 technical candidates, 6.735 retained quarantine, 14 excluded exact duplicate. Source missing-group là 6.749, không phải 6.735. Exact metadata replay khớp cả manifest, 1.404 alias Target Spot không được áp dụng, 373 mosaic chưa nhóm. Workbook gốc không chứa TgS prefix hoặc sheet mosaic; hai JSON là mirrored metadata, không phải hai annotation độc lập. Mười near pairs giữ pending, không heuristic merge/delete.

Các record chưa đủ bằng chứng không vào approved split. Full10 còn chặn C2/S04; nhãn bệnh/ToMV–TMV chưa có chuyên gia duyệt. [Báo cáo và evidence](../../../artifacts/phase1/README.md) ghi tests, hashes và giới hạn. Phạm vi S03 cho phép quarantine, không đồng nghĩa đã hoàn tất grouping benchmark. Không tự mark done.
