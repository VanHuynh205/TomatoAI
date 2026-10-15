---
id: EPB
canonical_id: EP-B
type: epic
title: "Hai mô hình và lựa chọn bằng validation"
parent: initiative-tomato-desktop
covers: ["CAP-2", "CAP-3"]
after: []
risk: high
---

# Hai mô hình và lựa chọn bằng validation

## Description

Model candidates và winner/policy được khóa để tích hợp và final test. Epic này sở hữu phần CAP và acceptance được phân công trong companion hiện hành; đầu ra phải bàn giao được cho consumer, không đóng bằng số ticket đã làm.

## Outcome

Model candidates và winner/policy được khóa để tích hợp và final test.

## Requirements

- CAP-2: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.
- CAP-3: tham chiếu cùng ID trong kernel; phần epic sở hữu được xác định trong Done when và entries, không tạo local ID khác.

## Done when

1. Hai head checkpoints do sinh viên huấn luyện có manifest/config/log
2. head/fine-tune hai model cùng split/budget, train-only fit
3. validation winner/policy/transform/hash được khóa trước test
4. negatives thiếu được ghi, không claim OOD detector đã đúng.

## Boundaries

Pilot/training/validation model artifacts; final test được EP-E.S15 thực hiện sau runtime hardening. S05 sở hữu shared experiment harness/config convention và golden input/eval oracle, chỉ kiểm phần training-side T04/T05/T16; full app parity T05 thuộc S06. S07/S08 dùng config/run riêng, không sửa shared harness song song. S09 đo CPU/resource sơ bộ trên validation/fixture bằng eval harness trước lock, không đợi S15/final test; S15 đo end-to-end app cuối sau lock. Một GPU được lên lịch tuần tự, không ngầm chạy đồng thời.

## References

- parent — [initiative](../initiative-tomato-desktop.md).
- spec — [SPEC-tomato-desktop](../spec-tomato-desktop/spec-tomato-desktop.md), các CAP được giao và tất cả companions.
- acceptance — [requirements-traceability](../spec-tomato-desktop/requirements-traceability.md), FR/NFR/story/test và các AC gốc adopted.
- readiness — [data-readiness](../spec-tomato-desktop/data-readiness.md), gating và evidence, không phải approval chuyên môn.
- constraint — `planning/tomato-desktop/architecture.md`, `security-testing.md`, `delivery-plan.md`, `experiments.md`, đường từ project root; xem links adopted trong spec.

## Notes

- Decision: 14/10/2026 — người dùng duyệt proposal revision 2; entries và thứ tự trong tickets.toml là tập planning đã chốt, chưa có implementation/status done.
- Tracer / sequencing / handoff: EP-A.S04 approved benchmark/class order, S01/C1 và quyền chuẩn bị weights/train ở phiên sau. S05 pilot là tracer artifact consumable bởi S06.
- Unknown: C0…C5/AD theo companion và unknown/known_uncertainty riêng của entry; có câu trả lời thật mới bỏ gate, planning approval không giải quyết những câu hỏi này.
- Assumption: một người làm mỗi tối; các lane không collision chỉ biểu diễn dependency, không mặc định chạy song song hoặc nhiều GPU.
- Decision: 14/10/2026 — không thêm Refactor sweep riêng; cleanup trong story bị ảnh hưởng, không giảm AC. Closure tích hợp/clean-machine S18 và evidence S19 giữ nguyên.
- Runtime compatibility: canonical epic EP-B dùng store ID EPB; runtime chỉ nhận chữ/số. Đây là biểu diễn máy của cùng epic, không đổi scope/membership/story ID.
