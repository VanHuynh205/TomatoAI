---
id: EPA
canonical_id: EP-A
type: epic
title: "Governance và dữ liệu có căn cứ"
parent: initiative-tomato-desktop
covers: ["CAP-1", "CAP-9"]
after: []
risk: high
status: in-progress
---

# Governance và dữ liệu có căn cứ

## Description

Có decision/license/data/group/split artifacts cho benchmark được phép dùng. Epic này sở hữu phần CAP và acceptance được phân công trong companion hiện hành; đầu ra phải bàn giao được cho consumer, không đóng bằng số ticket đã làm.

## Outcome

Có decision/license/data/group/split artifacts cho benchmark được phép dùng.

## Requirements

- CAP-1: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-9: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.

## Done when

1. S01 ledger ghi quyết định/rubric/quyền từng asset và gate chưa đóng
2. registry/provenance/counts khớp run không rerun cleaning vô cớ
3. grouping/duplicates có bằng chứng hoặc quarantine
4. approved class/split manifest qua T15 trước model, không random phần unresolved.

## Boundaries

Data governance/pipeline, không train hoặc duyệt guidance. Mở đầu là S01 baseline tooling/decision; runtime đã setup được tái dùng. S02 tiếp nhận inventory; S03/S04 tạo benchmark theo quyền phiên tương lai.

## References

- parent — [initiative](../initiative-tomato-desktop.md).
- spec — [SPEC-tomato-desktop](../spec-tomato-desktop/spec-tomato-desktop.md), các CAP được giao và tất cả companions.
- acceptance — [requirements-traceability](../spec-tomato-desktop/requirements-traceability.md), FR/NFR/story/test và các AC gốc adopted.
- readiness — [data-readiness](../spec-tomato-desktop/data-readiness.md), gating và evidence, không phải approval chuyên môn.
- constraint — `planning/tomato-desktop/architecture.md`, `security-testing.md`, `delivery-plan.md`, `experiments.md`, đường từ project root; xem links adopted trong spec.

## Notes

- Decision: 14/10/2026 — người dùng duyệt proposal revision 2; entries và thứ tự trong tickets.toml là tập planning đã chốt, chưa có implementation/status done.
- Tracer / sequencing / handoff: Không epic provider; user decisions/rights/rubric được S01 xử lý. S01 làm tracer governance từ một record đã có grouping và một record thiếu grouping trong manifest hiện có, qua source/hash/license/decision ledger tới eligibility/refusal report; không tạo split hoặc tự sửa nhãn. S02–S04 mở rộng inventory/group/split sau các gate khoa học, không dựng app scaffold trong Prompt 3.
- Unknown: C0…C5/AD theo companion và unknown/known_uncertainty riêng của entry; có câu trả lời thật mới bỏ gate, planning approval không giải quyết những câu hỏi này.
- Decision: 15/10/2026 — người dùng xác nhận nhóm ba người làm mỗi tối, bảo vệ khoảng hai tháng nữa, chưa ngày/giờ cụ thể; laptop hạn chế, chưa chuyên gia cà chua. Thay giả định cũ một người; các lane vẫn chỉ biểu diễn dependency, không mặc định nhiều GPU hoặc execution phase sau. Phase 0/EPA.S01 được cho phép thực hiện; xem `docs/development/decisions.md` và `artifacts/S01/` từ root.
- Decision: 14/10/2026 — không thêm Refactor sweep riêng; cleanup trong story bị ảnh hưởng, không giảm AC. Closure tích hợp/clean-machine S18 và evidence S19 giữ nguyên.
- Decision: mở governance/tooling thay product platform epic; S05/S06/S18 sở hữu experiment/desktop/release baseline theo initiative Notes.
- Runtime compatibility: canonical epic EP-A dùng store ID EPA; runtime chỉ nhận chữ/số. Đây là biểu diễn máy của cùng epic, không đổi scope/membership/story ID.
