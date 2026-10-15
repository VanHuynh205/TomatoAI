---
id: EPC
canonical_id: EP-C
type: epic
title: "Lát cắt desktop xuyên suốt"
parent: initiative-tomato-desktop
covers: ["CAP-3", "CAP-4", "CAP-7"]
after: []
risk: high
---

# Lát cắt desktop xuyên suốt

## Description

Một ảnh local nối checkpoint sinh viên với đúng card VI được phép, có giới hạn và failure states. Epic này sở hữu phần CAP và acceptance được phân công trong companion hiện hành; đầu ra phải bàn giao được cho consumer, không đóng bằng số ticket đã làm.

## Outcome

Một ảnh local nối checkpoint sinh viên với đúng card VI được phép, có giới hạn và failure states.

## Requirements

- CAP-3: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-4: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-7: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.

## Done when

1. T01/T04/T05 kiểm identity/classes/transform parity với head checkpoint sinh viên, manifest/hash/preprocessing tương thích và nhãn “chưa đánh giá cuối”
2. positive lookup một card VI thật được C3/policy/version cho phép, đồng thời case blocked không giả approved
3. invalid/cancel/stale không render advice, worker bounded qua T10
4. minimal desktop path chạy local không training/network.

## Boundaries

Minimal UI/orchestration/inference/lookup contract cho một ảnh và một card; không đợi UI full hoặc toàn kho. S06 sở hữu runtime shared contracts, golden fixtures và native QA harness cho S13/S14/S18; chọn công cụ thực sự tương thích Qt/Windows, không dựng web URL/config giả hoặc gọi browser test là native E2E.

## References

- parent — [initiative](../initiative-tomato-desktop.md).
- spec — [SPEC-tomato-desktop](../spec-tomato-desktop/spec-tomato-desktop.md), các CAP được giao và tất cả companions.
- acceptance — [requirements-traceability](../spec-tomato-desktop/requirements-traceability.md), FR/NFR/story/test và các AC gốc adopted.
- readiness — [data-readiness](../spec-tomato-desktop/data-readiness.md), gating và evidence, không phải approval chuyên môn.
- constraint — `planning/tomato-desktop/architecture.md`, `security-testing.md`, `delivery-plan.md`, `experiments.md`, đường từ project root; xem links adopted trong spec.

## Notes

- Decision: 14/10/2026 — người dùng duyệt proposal revision 2; entries và thứ tự trong tickets.toml là tập planning đã chốt, chưa có implementation/status done.
- Tracer / sequencing / handoff: EP-A.S04, EP-B.S05, milestone EP-D.S11 sau S10; AD-1/UX và C3 được duyệt. Không chờ whole EP-B/EP-D done.
- Unknown: C0…C5/AD theo companion và unknown/known_uncertainty riêng của entry; có câu trả lời thật mới bỏ gate, planning approval không giải quyết những câu hỏi này.
- Assumption: một người làm mỗi tối; các lane không collision chỉ biểu diễn dependency, không mặc định chạy song song hoặc nhiều GPU.

- Runtime compatibility: canonical epic EP-C dùng store ID EPC; runtime chỉ nhận chữ/số. Đây là biểu diễn máy của cùng epic, không đổi scope/membership/story ID.
