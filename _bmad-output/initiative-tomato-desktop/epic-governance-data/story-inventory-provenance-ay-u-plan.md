---
title: "inventory/provenance đầy đủ"
ticket: S02
status: built
---

# S02 — Inventory/provenance Phase 1

Thực hiện ngày 15/10/2026 trong phạm vi người dùng đã giao. Pipeline `scripts/data/prepare_benchmark.py` nhận đúng `registry.current_run`, không chọn theo mtime. Data card tại `artifacts/data-card.json` xác minh năm cleaning run và UC-IPM acquisition blocked riêng; không gộp research records thành training data.

18.362 file raw được fresh hash theo năm cleaning baseline; raw_writes=0. Có checks seal, reference/config hashes, source/record provenance, count conservation và missing provenance fail-closed. Không thay cleaner, registry, reports cũ hoặc raw. Scope exclusions PV giữ đúng baseline; hash không chứng minh nhãn bệnh đúng.

Evidence/commands/limits: [Phase 1 report](../../../artifacts/phase1/README.md), [pipeline](../../../artifacts/phase1/pipeline-run.json), [preservation](../../../artifacts/phase1/preservation-after.json), [tests](../../../artifacts/phase1/metadata-green.log). T15 là evidence intake/boundary; T18 là integrity/path guard trong scope dữ liệu, không phải UI/privacy acceptance đầy đủ. Final review phát hiện ba lỗi dùng chung pipeline; đã sửa có RED→GREEN, suite cuối 144/144 pass. Trạng thái built đã được ghi sau kiểm chứng; không tự done hoặc mở quyền train.
