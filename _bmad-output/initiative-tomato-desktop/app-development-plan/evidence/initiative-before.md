---
type: initiative
title: "Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua"
parent: none
covers: [CAP-1, CAP-2, CAP-3, CAP-4, CAP-5, CAP-6, CAP-7, CAP-8, CAP-9]
after: []
risk: high
---

# Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua

## Description

Người Việt quan sát trạng thái lá cà chua và học chăm sóc có căn cứ bằng desktop Windows tiếng Việt hoạt động offline. Sinh viên chứng minh dữ liệu, transfer learning EfficientNet/ResNet50, lựa chọn công bằng và tích hợp tri thức có scope duyệt; [spec](spec-tomato-desktop/spec-tomato-desktop.md) là contract.

## Outcome

Đạt Success signal của SPEC-tomato-desktop bằng lát cắt S06 và release offline có bằng chứng nhận diện, chăm sóc, học tập riêng; báo rõ phần chưa được kiểm chứng.

## Requirements

Dùng CAP-1…CAP-9 trong [spec](spec-tomato-desktop/spec-tomato-desktop.md#capabilities); 24 FR/NFR và 22 story truy vết ở [companion](spec-tomato-desktop/requirements-traceability.md). Không tạo ID yêu cầu song song.

## Done when

1. Benchmark được duyệt có provenance/group/class/split manifest kiểm T15; unresolved không được dùng để nghiệm thu giả.
2. EfficientNet/ResNet50 có head/fine-tune/config/log/checkpoint; winner/policy chọn validation trước test và báo kết quả thực đo T16.
3. S06 có một ảnh/checkpoint sinh viên/một card VI được phép, kèm invalid/cancel/unknown/knowledge-blocked theo đúng policy.
4. Bundle Windows qua clean-machine/offline/resource/keyboard tests; claim hiển thị có nguồn, version và scope duyệt; license đủ phạm vi phân phối.
5. Báo cáo truy vết FR/NFR-story-test-evidence; image/care/learning tách biệt, field/expert/participants thiếu phải báo rõ T20.

## Boundaries

desktop local/data/experiments/knowledge/localization/education/package/report. Không web, optimization, LLM/API, training trong app, dịch runtime mặc định hoặc model thứ ba. Touch points: raw/registry/run manifests do EP-A quản trị; runtime pretrained/library assets do S01 quyền dùng và S05/S18 chuẩn bị theo quyền tương lai; kho nghiên cứu WUR/Dryad/Mendeley/UC-IPM ngoài MVP. Tracer liên epic: EP-A.S04, EP-B.S05 và một card EP-D.S10/S11 cung cấp cho EP-C.S06; EP-E mở rộng/hardening/release.

- Touch point: raw/processed/registry/run manifests và sealed review — tiêu thụ evidence, không sửa corpus đã chốt; owner EP-A.
- Touch point: thư viện/pretrained weights — quyền và nguồn S01, chuẩn bị theo quyền tương lai S05, phân phối notices S18; owner EP-B/EP-E theo trách nhiệm này.
- Touch point: WUR/Dryad/Mendeley/UC-IPM — research-only ngoài phụ thuộc MVP, không tạo module canh tác tối ưu.

## References

- spec — [kernel](spec-tomato-desktop/spec-tomato-desktop.md), Capabilities/Constraints/Non-goals/Success signal và tất cả companions.
- acceptance — [truy vết](spec-tomato-desktop/requirements-traceability.md), FR/NFR và story/test.
- readiness — [evidence và gates](spec-tomato-desktop/data-readiness.md).
- evidence of import — [planning import](planning-import-20261014-v1/README.md); [proposal được duyệt](planning-import-20261014-v1/ticket-proposal.md).

## Notes

- Decision: 14/10/2026 — người dùng duyệt spec và “Duyệt proposal, ghi kế hoạch chính thức”; sáu epic/22 entry được ghi, chỉ planning.
- Decision: giữ S01–S20; thêm S10b/S11b cho scope còn lại sau thẻ đầu S10/S11; S15 thuộc EP-E, S17 thuộc EP-F để bỏ vòng phụ thuộc cấp epic. Tài liệu nguồn lịch sử và AC không bị xóa.
- Decision: EP-A mở governance thay epic platform sản phẩm riêng vì benchmark/policy chưa đủ; S05 sở hữu environment/harness thực nghiệm, S06 desktop scaffold/contracts/native QA, S18 package/release. Không dựng scaffold trong Prompt 3.
- Decision: không thêm ticket Refactor sweep riêng trong A/D/B/E; cleanup nằm trong các story bị ảnh hưởng, S18 tích hợp/máy sạch và S19 evidence closure. Không giảm AC nguồn.
- Decision: S20 optional, duyệt riêng và budget; core/report không chờ S20. Không tự cho phép execution hoặc bỏ checkpoint tương lai.
- Assumption: một sinh viên/2 giờ mỗi tối/tám tuần từ planning nguồn, chưa được người dùng xác nhận; không ghi estimate vào ticket.
- Open question: B0/stack/version/budget/targets/rubric C0/C1, grouping C2, policy/reviewer C3, evaluation C4 và rights/máy sạch C5 vẫn pending; S01 quản lý ledger quyết định, story phụ thuộc có Unknown riêng.
- Source conflict: draft cho educational source_checked demo, real safe_for_advice=false; hiện tiếp tục chặn tới policy/claim version được phép, không tự phê duyệt chuyên môn.
- Source conflict: membership và milestone cũ ở delivery draft được thay bởi quyết định slicing trên; IDs/AC gốc tiếp tục được truy vết trong companion hiện hành.