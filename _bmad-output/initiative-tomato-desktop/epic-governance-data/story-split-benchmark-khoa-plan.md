---
title: "split benchmark khóa"
ticket: S04
status: blocked
blocked_at: "2026-10-15"
blocked_reason: "C2: full10 grouping and label/class approval pending; training rights pending. Technical split harness verified; zero real assignments."
---

# S04 — Harness có kiểm chứng, benchmark thật chưa được duyệt

Ngày 15/10/2026, người dùng không có reviewer/seed/ratios và giao best-effort. Đã chọn seed 42, targets train/validation/test 70/15/15 trong `artifacts/phase1/split-policy.pending.json`; giữ explicit proposed class order và TOM_* mapping hiện có. Approval fields vẫn false, không tự ký thay chuyên gia hoặc đổi scope thành pilot.

`create_split` có grouped deterministic balancing, min three independent components/class, explicit IDs/order/codes, review/policy hash, rights and approval gates, supports/exclusions và train-only preprocessing boundary. Tests synthetic chứng minh giao groups/components bằng rỗng, order/hash ổn định, stale/missing approvals hoặc unresolved fail closed. Không preprocess hay train ảnh thật.

Actual `artifacts/split-manifest.json` có status blocked, zero assignments và empty class manifest. Full10 còn thiếu grouping/label/class approval; rights ledger training_approved vẫn false. Scope pilot chỉ sau quyết định riêng, không được gọi full benchmark. [Báo cáo Phase 1](../../../artifacts/phase1/README.md) và [ledger](../../../artifacts/phase1/progress.md) lưu kiểm thử, evidence và giới hạn. S04 chưa built/done; Phase 1 chưa qua C2.

Bổ sung 15/10: đã kiểm pinned metadata GitHub/Hugging Face; leaf maps/Target CSV không có delta so với raw. Loader upstream dùng fallback theo tên khi thiếu nhóm, nên không dùng fallback để mở C2. [Source audit](../../../artifacts/phase1/upstream-grouping-audit.md) có URLs/revision/hashes và kết luận phạm vi kiểm. Cần annotation/bằng chứng mới hoặc quyết định scope riêng; không còn tiến trình kỹ thuật đang chạy để chờ.
