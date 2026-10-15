# Envelope và ticket tree revision 2 — đã được duyệt

**Checkpoint 14/10/2026: người dùng trả lời “Duyệt proposal, ghi kế hoạch chính thức”.** Nội dung trình duyệt bên dưới được lưu để bảo toàn lịch sử; các lựa chọn slicing, membership, sweep và platform đã trở thành Decision trong initiative/epic chính thức. C1/C2/C3/C4/C5, stack/B0/targets và S20 execution riêng vẫn pending. Store đã ghi sáu epic/22 entry, tất cả planned; xem `ticket-status-final.json` và `ticket-next-final.json`. Canonical EP-A…EP-F có runtime alias EPA…EPF vì `tickets.py` chỉ nhận chữ/số; story IDs không đổi.

Spec đã được người dùng duyệt ngày 14/10/2026; tiếp tục `bmad-ticket` chỉ để lập kế hoạch. Activation đã chạy resolver/config/store/customization; hooks/facts/on_complete rỗng. Repo store local; không Git metadata, không commit/publish remote. Đây là proposal, chưa là `tickets.toml` và chưa có task bắt đầu.

Nguồn bắt buộc: [spec](../spec-tomato-desktop/spec-tomato-desktop.md) và mọi companion, đặc biệt [AC/story delta](../spec-tomato-desktop/requirements-traceability.md), [readiness](../spec-tomato-desktop/data-readiness.md), [delivery-plan nguồn](../../../planning/tomato-desktop/delivery-plan.md). Danh sách máy đọc tại `ticket-proposal.json` giữ ID, output/verify/gates, không giả trạng thái done.

## Initiative envelope

**Title:** Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua.

**Description / Outcome:** Giúp người Việt quan sát trạng thái lá và học chăm sóc có nguồn bằng desktop offline; sinh viên chứng minh pipeline hai mô hình và giới hạn theo Success signal của SPEC-tomato-desktop.

**Covers:** CAP-1…CAP-9. FR01…FR14/NFR01…NFR10 giữ làm yêu cầu chi tiết; AD-1…AD-8 là đề xuất phải duyệt.

**Done when:**

1. Benchmark được duyệt có provenance/group/class/split manifest kiểm T15; unresolved không được dùng để nghiệm thu giả.
2. EfficientNet/ResNet50 có head/fine-tune/config/log/checkpoint; winner/policy chọn validation trước test và báo kết quả thực đo T16.
3. S06 có một ảnh/checkpoint sinh viên/một card VI được phép, kèm invalid/cancel/unknown/knowledge-blocked theo đúng policy.
4. Bundle Windows qua clean-machine/offline/resource/keyboard tests; claim hiển thị có nguồn, version và scope duyệt; license đủ phạm vi phân phối.
5. Báo cáo truy vết FR/NFR-story-test-evidence; image/care/learning tách biệt, field/expert/participants thiếu phải báo rõ T20.

**Boundaries:** desktop local/data/experiments/knowledge/localization/education/package/report. Không web, optimization, LLM/API, training trong app, dịch runtime mặc định hoặc model thứ ba. Touch points: raw/registry/run manifests do EP-A quản trị; runtime pretrained/library assets do S01 quyền dùng và S05/S18 chuẩn bị theo quyền tương lai; kho nghiên cứu WUR/Dryad/Mendeley/UC-IPM ngoài MVP. Tracer liên epic: EP-A.S04, EP-B.S05 và một card EP-D.S10/S11 cung cấp cho EP-C.S06; EP-E mở rộng/hardening/release.

**Notes:** Scope/title đã chốt. B0/stack/budget/C3/release chưa chốt. Không có full 10-class split, model, VI approved hoặc guidance allowed. Ước lượng nguồn một sinh viên/2h mỗi tối là giả định, không ghi `estimate` như người dùng đã duyệt. Ngoại lệ opening platform-baseline cần người dùng duyệt: EP-A mở governance/tooling dữ liệu vì benchmark và policy chưa đủ; scaffold/harness thực nghiệm do S05 sở hữu, scaffold/contracts/QA desktop do S06 sở hữu, packaging/release do S18 sở hữu. Không lập epic nền tảng riêng hoặc giả đã tạo scaffold trong Prompt 3.

## Sáu epic đề xuất theo thứ tự dependency

Giữ EP-A…EP-F nhưng thứ tự A,D,B,C,E,F. Không dùng whole-epic gate cho handoff cần một story/milestone. Source conflict cần duyệt: chuyển **S15 từ EP-B sang EP-E**, **S17 từ EP-D sang EP-F** để tránh chu trình EP-B↔EP-E và EP-D↔EP-E; giữ ID/ý định/yêu cầu/test/AC. Tách S10/S11 thành scope thẻ đầu tiên và phần còn lại **S10b/S11b** để runtime pin milestone bằng story thật; không đánh dấu toàn kho done để mở S06. Tổng 22 entries, vẫn giữ toàn bộ 20 ID cũ và AC phân bổ rõ. Các thay đổi là đề xuất, chưa phải quyết định người dùng.

### EP-A — Governance và dữ liệu có căn cứ

- **Covers:** CAP-1,CAP-9; **children:** S01,S02,S03,S04.
- **Outcome:** Có decision/license/data/group/split artifacts cho benchmark được phép dùng.
- **Done when:** (1) S01 ledger ghi quyết định/rubric/quyền từng asset và gate chưa đóng; (2) registry/provenance/counts khớp run không rerun cleaning vô cớ; (3) grouping/duplicates có bằng chứng hoặc quarantine; (4) approved class/split manifest qua T15 trước model, không random phần unresolved.
- **Boundary:** Data governance/pipeline, không train hoặc duyệt guidance. Mở đầu là S01 baseline tooling/decision; runtime đã setup được tái dùng. S02 tiếp nhận inventory; S03/S04 tạo benchmark theo quyền phiên tương lai.
- **Needs:** Không epic provider; user decisions/rights/rubric được S01 xử lý. S01 làm tracer governance từ một record đã có grouping và một record thiếu grouping trong manifest hiện có, qua source/hash/license/decision ledger tới eligibility/refusal report; không tạo split hoặc tự sửa nhãn. S02–S04 mở rộng inventory/group/split sau các gate khoa học, không dựng app scaffold trong Prompt 3.

### EP-D — Tri thức Việt hóa và nội dung học có nguồn

- **Covers:** CAP-4,CAP-5,CAP-6; **children:** S10,S11,S10b,S11b,S12.
- **Outcome:** Knowledge/localization/lesson bundle có scope duyệt rõ, dùng được bởi lookup contract.
- **Done when:** (1) 10 lớp có exact mapping hoặc blocked reason, mosaic không ép accepted; (2) milestone một card EN–VI/claim/source review được phép theo C3, lookup golden test kiểm; (3) toàn scope card/lesson hiển thị có actor/role/revision/conditions, thuốc chưa đủ bị suppress; (4) LO1–LO3, hai quiz/card và feedback/source qua T14.
- **Boundary:** Knowledge/localization/education artifacts, không classifier/ảnh hoặc human learning study. Card không thuộc classifier ở kho riêng; không cần duyệt cả 17 cho milestone.
- **Needs:** EP-A.S01 quyền/policy decision, EP-A.S02 nguồn/ID/provenance. S10 tracer kỹ thuật một card gồm EN–VI draft, nguồn/review metadata, draft lesson/hai quiz và lookup refusal chạy bằng validator đã có; S11 review/policy/meaning cho card và lesson đầu, tạo milestone được phép thật cho S06. S10b/S11b mở rộng phần còn lại và 24 link; S12 hoàn thiện/kiểm lessons trên scope được phép. Không đợi S10b/S11b để chạy S06, không lấy fixture synthetic thay positive card thật.

### EP-B — Hai mô hình và lựa chọn bằng validation

- **Covers:** CAP-2,CAP-3; **children:** S05,S07,S08,S09.
- **Outcome:** Model candidates và winner/policy được khóa để tích hợp và final test.
- **Done when:** (1) Hai head checkpoints do sinh viên huấn luyện có manifest/config/log; (2) head/fine-tune hai model cùng split/budget, train-only fit; (3) validation winner/policy/transform/hash được khóa trước test; (4) negatives thiếu được ghi, không claim OOD detector đã đúng.
- **Boundary:** Pilot/training/validation model artifacts; final test được EP-E.S15 thực hiện sau runtime hardening. S05 sở hữu shared experiment harness/config convention và golden input/eval oracle, chỉ kiểm phần training-side T04/T05/T16; full app parity T05 thuộc S06. S07/S08 dùng config/run riêng, không sửa shared harness song song. S09 đo CPU/resource sơ bộ trên validation/fixture bằng eval harness trước lock, không đợi S15/final test; S15 đo end-to-end app cuối sau lock. Một GPU được lên lịch tuần tự, không ngầm chạy đồng thời.
- **Needs:** EP-A.S04 approved benchmark/class order, S01/C1 và quyền chuẩn bị weights/train ở phiên sau. S05 pilot là tracer artifact consumable bởi S06.

### EP-C — Lát cắt desktop xuyên suốt

- **Covers:** CAP-3,CAP-4,CAP-7; **child:** S06.
- **Outcome:** Một ảnh local nối checkpoint sinh viên với đúng card VI được phép, có giới hạn và failure states.
- **Done when:** (1) T01/T04/T05 kiểm identity/classes/transform parity với head checkpoint sinh viên, manifest/hash/preprocessing tương thích và nhãn “chưa đánh giá cuối”; (2) positive lookup một card VI thật được C3/policy/version cho phép, đồng thời case blocked không giả approved; (3) invalid/cancel/stale không render advice, worker bounded qua T10; (4) minimal desktop path chạy local không training/network.
- **Boundary:** Minimal UI/orchestration/inference/lookup contract cho một ảnh và một card; không đợi UI full hoặc toàn kho. S06 sở hữu runtime shared contracts, golden fixtures và native QA harness cho S13/S14/S18; chọn công cụ thực sự tương thích Qt/Windows, không dựng web URL/config giả hoặc gọi browser test là native E2E.
- **Needs:** EP-A.S04, EP-B.S05, milestone EP-D.S11 sau S10; AD-1/UX và C3 được duyệt. Không chờ whole EP-B/EP-D done.

### EP-E — Desktop hoàn thiện, đánh giá cuối và phát hành offline

- **Covers:** CAP-2,CAP-3,CAP-4,CAP-6,CAP-7,CAP-8,CAP-9; **children:** S13,S14,S15,S18,S20 optional.
- **Outcome:** Release candidate Windows có final metrics, giới hạn tài nguyên, policy và clean-machine evidence.
- **Done when:** (1) Full states/VI/source/lesson/keyboard/DPI T19; (2) worker/input/model guard T02/T03/T10/T12/T18; (3) S15 final test sau S09 lock, CPU metrics thật không đổi winner; (4) S18 bundle qua máy sạch offline/notices/license/review scope; (5) S20 chỉ khi được duyệt, default off/không upload, không chặn core.
- **Boundary:** Native UI, worker/load-safe, final benchmark và package. Tách UI files S13 khỏi worker S14; S14 chờ UI hoàn chỉnh S13 để kiểm failure/cancel flows. S15 từ EP-B chuyển về đây vì cần runtime S14. Lịch sử không phải core release prerequisite.
- **Needs:** EP-C.S06 shared contracts; EP-B.S09 winner/policy lock; EP-D.S12 lesson sau S11. S13 mở rộng tracer của S06; S18 là kiểm thử tích hợp/clean-machine kết thúc core.

### EP-F — Evidence độc lập, đánh giá người dùng và bảo vệ

- **Covers:** CAP-4,CAP-6,CAP-8,CAP-9; **children:** S16,S17,S19.
- **Outcome:** Báo cáo/demo truy vết kết quả thật và thiếu bằng chứng ngoài miền/chuyên môn/học tập.
- **Done when:** (1) S16 external/challenge metric có ground truth/quyền/group độc lập hoặc missing-evidence report; (2) S17 care/learning/usability study có actor/participants thật hoặc báo chưa đánh giá, không expert/user-study giả; (3) T20 report/slide/demo thống nhất lock/metrics/limits/license; (4) rehearsal offline trên release core, không tuyên bố tối ưu canh tác. Missing-evidence report chỉ đóng đầu ra báo cáo, không chứng minh hoặc thông qua acceptance hiệu quả ngoài miền/chăm sóc/học tập.
- **Boundary:** Independent/human assessment và báo cáo; không tune winner bằng test. S17 chuyển từ EP-D vì cần UI S13. S16/S17 có thể ghi blocker report; điều này không chứng minh field/care/learning hiệu quả.
- **Needs:** EP-B.S09 locked policy; EP-D.S12 nguồn/lesson; EP-E.S13 UI, S15 metrics và S18 release. S16 dùng locked artifact/challenge path làm tracer assessment, không yêu cầu download hiện tại.

## Điểm cần chốt khi duyệt slicing

1. Giữ sáu epic và 20 ID cũ; thêm S10b/S11b để bảo toàn phần còn lại sau milestone card đầu, tổng 22 story. Chuyển membership S15/S17 như trên để graph không cycle.
2. Skill mặc định đề xuất closing **Refactor sweep** cho epic >3 entry (EP-A/EP-D/EP-B/EP-E). Đề xuất **không thêm ticket riêng** trong budget hai tháng; cleanup nằm trong AC/story bị ảnh hưởng, S18 có closing integration/clean-machine, S19 có evidence closure. Đây là đề nghị để người dùng quyết định, chưa ghi `Decision: declined`.
3. S20 giữ entry optional/blocked bởi duyệt riêng và budget; core/report không chờ S20. Không chạy unattended/build; không ngầm duyệt plan/done checkpoints cho execution.
4. EP-A mở governance thay cho epic platform sản phẩm riêng; S05/S06/S18 nhận trách nhiệm nền tảng theo Notes. Đây là ngoại lệ được đề xuất, chưa ghi thành quyết định đã duyệt.

Mọi thay đổi description/note/reference khác có thể được người dùng nêu trước ghi store. Các source conflicts C1/C2/C3 và thiếu reviewer/ảnh ngoài miền giữ nguyên; duyệt split planning không thông qua các gate này.
