---
title: "chốt scope và quyền dùng"
ticket: S01
status: built
---

# S01 — Phase 0

Phạm vi được người dùng cho phép ngày 15/10/2026: thực hiện Phase 0 theo kế hoạch chính thức. Không thực hiện các phase sau hoặc huấn luyện.

## Đầu ra và bằng chứng

- [Quyết định và blocker](../../../docs/development/decisions.md): nhóm 3 người làm mỗi tối, bảo vệ khoảng hai tháng; chưa ngày/rubric/giờ cụ thể. Không login; history/profile tùy chọn. Compute và chuyên gia còn thiếu.
- [Rights ledger](../../../docs/development/assets-rights.json): sáu dataset, từng thẻ tri thức, hai weights ứng viên và software; không tự cấp quyền hoặc ký expert review.
- [Compatibility](../../../docs/development/compatibility.json) và [log kiểm chứng](../../../artifacts/S01/): CPU forward hai kiến trúc, Qt native/event loop/spawn và executable kiểm riêng; chỉ ghi pass khi có kết quả thật.
- [Tracer](../../../artifacts/S01/governance-trace.json): hai record thật, hash raw/processed và căn cứ nhóm; grouping khác nhau, cả hai vẫn chưa được train.
- [Checkpoint bảo toàn](../../../artifacts/S01/preservation-after.json): registry, bảy ticket store và integration artifacts giữ nguyên; không suy thành full raw rehash.

## Giới hạn bàn giao

S01 không đóng C2/C3/C5. Chưa approved split, rights pretrained, training compute hoặc expert review. Không có accuracy, care effectiveness, latency acceptance hay clean-machine release proof. Bản chẩn đoán không là app sản phẩm. T20 kiểm claim/evidence ở phạm vi S01, các acceptance còn lại ở story tương ứng.

Trạng thái `built` chỉ áp dụng khi evidence Phase 0 đã kiểm đủ; người dùng/orchestrator quyết định `done`. Không tự chạy S02/S05.
