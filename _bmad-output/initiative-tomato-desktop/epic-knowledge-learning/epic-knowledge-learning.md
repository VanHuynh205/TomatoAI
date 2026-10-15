---
id: EPD
canonical_id: EP-D
type: epic
title: "Tri thức Việt hóa và nội dung học có nguồn"
parent: initiative-tomato-desktop
covers: ["CAP-4", "CAP-5", "CAP-6"]
after: []
risk: high
---

# Tri thức Việt hóa và nội dung học có nguồn

## Description

Knowledge/localization/lesson bundle có scope duyệt rõ, dùng được bởi lookup contract. Epic này sở hữu phần CAP và acceptance được phân công trong companion hiện hành; đầu ra phải bàn giao được cho consumer, không đóng bằng số ticket đã làm.

## Outcome

Knowledge/localization/lesson bundle có scope duyệt rõ, dùng được bởi lookup contract.

## Requirements

- CAP-4: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-5: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-6: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.

## Done when

1. 10 lớp có exact mapping hoặc blocked reason, mosaic không ép accepted
2. milestone một card EN–VI/claim/source review được phép theo C3, lookup golden test kiểm
3. toàn scope card/lesson hiển thị có actor/role/revision/conditions, thuốc chưa đủ bị suppress
4. LO1–LO3, hai quiz/card và feedback/source qua T14.

## Boundaries

Knowledge/localization/education artifacts, không classifier/ảnh hoặc human learning study. Card không thuộc classifier ở kho riêng; không cần duyệt cả 17 cho milestone.

## References

- parent — [initiative](../initiative-tomato-desktop.md).
- spec — [SPEC-tomato-desktop](../spec-tomato-desktop/spec-tomato-desktop.md), các CAP được giao và tất cả companions.
- acceptance — [requirements-traceability](../spec-tomato-desktop/requirements-traceability.md), FR/NFR/story/test và các AC gốc adopted.
- readiness — [data-readiness](../spec-tomato-desktop/data-readiness.md), gating và evidence, không phải approval chuyên môn.
- constraint — `planning/tomato-desktop/architecture.md`, `security-testing.md`, `delivery-plan.md`, `experiments.md`, đường từ project root; xem links adopted trong spec.

## Notes

- Decision: 14/10/2026 — người dùng duyệt proposal revision 2; entries và thứ tự trong tickets.toml là tập planning đã chốt, chưa có implementation/status done.
- Tracer / sequencing / handoff: EP-A.S01 quyền/policy decision, EP-A.S02 nguồn/ID/provenance. S10 tracer kỹ thuật một card gồm EN–VI draft, nguồn/review metadata, draft lesson/hai quiz và lookup refusal chạy bằng validator đã có; S11 review/policy/meaning cho card và lesson đầu, tạo milestone được phép thật cho S06. S10b/S11b mở rộng phần còn lại và 24 link; S12 hoàn thiện/kiểm lessons trên scope được phép. Không đợi S10b/S11b để chạy S06, không lấy fixture synthetic thay positive card thật.
- Unknown: C0…C5/AD theo companion và unknown/known_uncertainty riêng của entry; có câu trả lời thật mới bỏ gate, planning approval không giải quyết những câu hỏi này.
- Assumption: một người làm mỗi tối; các lane không collision chỉ biểu diễn dependency, không mặc định chạy song song hoặc nhiều GPU.
- Decision: 14/10/2026 — không thêm Refactor sweep riêng; cleanup trong story bị ảnh hưởng, không giảm AC. Closure tích hợp/clean-machine S18 và evidence S19 giữ nguyên.
- Decision: S10/S11 chỉ thẻ đầu hoàn chỉnh; S10b/S11b giữ mapping/VI/claim review còn lại. S17 sang EP-F; không lấy synthetic fixture làm card thật được phép.
- Runtime compatibility: canonical epic EP-D dùng store ID EPD; runtime chỉ nhận chữ/số. Đây là biểu diễn máy của cùng epic, không đổi scope/membership/story ID.
