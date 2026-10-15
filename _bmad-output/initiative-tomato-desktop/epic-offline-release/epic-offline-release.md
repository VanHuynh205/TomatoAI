---
id: EPE
canonical_id: EP-E
type: epic
title: "Desktop hoàn thiện, đánh giá cuối và phát hành offline"
parent: initiative-tomato-desktop
covers: ["CAP-2", "CAP-3", "CAP-4", "CAP-6", "CAP-7", "CAP-8", "CAP-9"]
after: []
risk: high
---

# Desktop hoàn thiện, đánh giá cuối và phát hành offline

## Description

Release candidate Windows có final metrics, giới hạn tài nguyên, policy và clean-machine evidence. Epic này sở hữu phần CAP và acceptance được phân công trong companion hiện hành; đầu ra phải bàn giao được cho consumer, không đóng bằng số ticket đã làm.

## Outcome

Release candidate Windows có final metrics, giới hạn tài nguyên, policy và clean-machine evidence.

## Requirements

- CAP-2: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-3: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-4: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-6: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-7: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-8: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-9: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.

## Done when

1. Full states/VI/source/lesson/keyboard/DPI T19
2. worker/input/model guard T02/T03/T10/T12/T18
3. S15 final test sau S09 lock, CPU metrics thật không đổi winner
4. S18 bundle qua máy sạch offline/notices/license/review scope
5. S20 chỉ khi được duyệt, default off/không upload, không chặn core.

## Boundaries

Native UI, worker/load-safe, final benchmark và package. Tách UI files S13 khỏi worker S14; S14 chờ UI hoàn chỉnh S13 để kiểm failure/cancel flows. S15 từ EP-B chuyển về đây vì cần runtime S14. Lịch sử không phải core release prerequisite.

## References

- parent — [initiative](../initiative-tomato-desktop.md).
- spec — [SPEC-tomato-desktop](../spec-tomato-desktop/spec-tomato-desktop.md), các CAP được giao và tất cả companions.
- acceptance — [requirements-traceability](../spec-tomato-desktop/requirements-traceability.md), FR/NFR/story/test và các AC gốc adopted.
- readiness — [data-readiness](../spec-tomato-desktop/data-readiness.md), gating và evidence, không phải approval chuyên môn.
- constraint — `planning/tomato-desktop/architecture.md`, `security-testing.md`, `delivery-plan.md`, `experiments.md`, đường từ project root; xem links adopted trong spec.

## Notes

- Decision: 14/10/2026 — người dùng duyệt proposal revision 2; entries và thứ tự trong tickets.toml là tập planning đã chốt, chưa có implementation/status done.
- Tracer / sequencing / handoff: EP-C.S06 shared contracts; EP-B.S09 winner/policy lock; EP-D.S12 lesson sau S11. S13 mở rộng tracer của S06; S18 là kiểm thử tích hợp/clean-machine kết thúc core.
- Unknown: C0…C5/AD theo companion và unknown/known_uncertainty riêng của entry; có câu trả lời thật mới bỏ gate, planning approval không giải quyết những câu hỏi này.
- Assumption: một người làm mỗi tối; các lane không collision chỉ biểu diễn dependency, không mặc định chạy song song hoặc nhiều GPU.
- Decision: 14/10/2026 — không thêm Refactor sweep riêng; cleanup trong story bị ảnh hưởng, không giảm AC. Closure tích hợp/clean-machine S18 và evidence S19 giữ nguyên.
- Decision: S15 nhận final benchmark tại EP-E sau S09/S14; S20 chưa được duyệt triển khai và không chặn core/report.
- Runtime compatibility: canonical epic EP-E dùng store ID EPE; runtime chỉ nhận chữ/số. Đây là biểu diễn máy của cùng epic, không đổi scope/membership/story ID.
