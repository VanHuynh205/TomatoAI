# Prompt 3 — tiếp nhận kế hoạch chính thức

Phiên bản `pi-20261014-v1`, ngày 14/10/2026. **Prompt 3 hoàn tất trong phạm vi planning.** Người dùng đã duyệt spec rồi trả lời “Duyệt proposal, ghi kế hoạch chính thức”. Không viết sản phẩm, tải dữ liệu/weights, dịch hàng loạt hoặc huấn luyện; không tự chuyển workflow sang build.

## Kế hoạch được ghi

- [Initiative](../initiative-tomato-desktop.md): tên/phạm vi đã chốt, Outcome/Done when, touch points, decisions và những gate chưa giải quyết.
- [Spec](../spec-tomato-desktop/spec-tomato-desktop.md): 9 CAP, 12 companions; 10 nguồn draft adopted giữ nguyên, 2 companion authored cập nhật bằng memlog và accepted decisions.
- [Requirements traceability](../spec-tomato-desktop/requirements-traceability.md) và [CSV](../spec-tomato-desktop/requirements-traceability.csv): 14 FR +10 NFR tới 22 story/T01–T20, AC và dependency. Giữ CAP/FR/NFR/AD/S/T cũ, thêm S10b/S11b theo duyệt.
- [Data readiness](../spec-tomato-desktop/data-readiness.md): dữ liệu/tri thức/translation/training/display tách trạng thái; approval planning không nâng readiness khoa học.
- [Ticket index](../tickets.toml): sáu epic theo thứ tự dependency; mỗi epic có envelope và tickets.toml, không có leaf/build plan/status done.

| Canonical epic | Runtime ID | Entries / trách nhiệm |
| --- | --- | --- |
| EP-A | EPA | S01–S04: quyết định/quyền/provenance/group/split |
| EP-D | EPD | S10,S11,S10b,S11b,S12: thẻ đầu thật, phần còn lại và lessons |
| EP-B | EPB | S05,S07,S08,S09: pilot, hai model, validation lock |
| EP-C | EPC | S06: ảnh/checkpoint sinh viên/card VI được phép, native desktop tracer |
| EP-E | EPE | S13,S14,S15,S18,S20: UI/hardening/final benchmark/offline; S20 riêng optional |
| EP-F | EPF | S16,S17,S19: external/care/learning evidence hoặc missing-evidence report, bảo vệ |

Runtime chỉ nhận chữ/số, nên có [ledger alias](ticket-runtime-compatibility.json) EP-A…EP-F sang EPA…EPF. Không đổi story ID hoặc semantics của graph. S15/S17 đổi membership trước lần nhập store đầu; S10b/S11b giữ AC phần còn lại, không giả partial-story done. Người dùng đã đồng ý không thêm Refactor sweep riêng và opening governance thay epic nền tảng sản phẩm riêng; S05/S06/S18 sở hữu experiment/desktop/release baseline. Cleanup và closure hiện có vẫn phải thực hiện.

## Runtime và workflow thực dùng

Project `C:/Users/admin/Downloads/DACN_CayCaChua`, data root `data/TomatoAI/data/`. BMAD `6.13.0-next`; output `_bmad-output`, active initiative `initiative-tomato-desktop`. Resolver/config giữ nguyên; hooks/facts/on_complete của spec/ticket rỗng. Store repo local; không Git metadata, nên chưa commit/publish hoặc tracker publication.

Skills thực dùng: `bmad` Help/status/config; `bmad-spec` extract/update/memlog/self-validation/user checkpoint; `bmad-ticket` activation/envelope/slicing/independent validation/record/status/next. Upstream brief/recon/PRD/UX/architecture chỉ xác minh bản cài và adopted tài liệu đủ sẵn; không giả các workflow đó đã chạy trong Prompt 3, không cài/nâng cấp bộ khác.

| Mục đích | Tên thực tế | Activation theo bản local | Đầu ra / trạng thái phiên này |
| --- | --- | --- | --- |
| Định tuyến/trạng thái | `bmad` | knowledge/help, resolver/output inventory; status qua setup script với `--status` | Runtime status và lựa chọn tuyến; đã dùng |
| Bài toán/phạm vi | `bmad-product-brief` | resolve_customization, prepend/facts/external_sources, config, intent, append | `brief-{slug}/brief-{slug}.md`; nguồn `product-brief.md` adopted, không chạy lại |
| Evidence/decision research | `bmad-deep-recon` | customization/prepend/append, config, chọn Draft/Process/Run | `research-{topic}/`; research/data/review hiện có adopted; không nghiên cứu/tải mới |
| FR/NFR/AC | `bmad-prd` | customization/config, mode/intent, bootstrap/extraction theo nhánh | `prd-{slug}/prd-{slug}.md`; PRD nguồn adopted, 24 ID được truy vết |
| UX desktop | `bmad-ux` | customization/prepend/facts/config, mode/intent, append | `ux-{slug}/DESIGN.md`, `EXPERIENCE.md`, kernel; nguồn UX adopted, direction vẫn đề xuất |
| Module/AD/contracts | `bmad-architecture` | customization/facts/config, chọn Coaching/Fast, append | Architecture spine theo workspace; AD-1…AD-8 adopted với trạng thái đề xuất, chưa bind stack |
| Contract thống nhất | `bmad-spec` | customization, facts/hooks, config, mode, append; memlog chuẩn | [Kernel chính thức trong workspace](../spec-tomato-desktop/spec-tomato-desktop.md); 9 CAP, 12 companions, đã được người dùng duyệt |
| Epic/story/dependency | `bmad-ticket` | config, read_store, customization/facts/hooks; slice/validate/board theo nhánh | Store repo mặc định; [status 0 tickets](ticket-status-before.json); spec và tập ticket đã duyệt; store 6 epic/22 planned, actual status/next sạch |

## Kiểm chứng thực chạy

- `resolve_config.py`: output/initiative đúng; `resolve_customization.py`: activation theo bản local, không có hooks cần chạy thêm.
- `memlog.py append`: ghi accepted user decisions và validation events, không tự tạo log/status giả. Kernel và authored companions được dẫn xuất theo accepted scope; nguồn adopted không sửa.
- [Independent ticket validation](ticket-validation.md), [bản máy đọc](ticket-validation.json): sáu reviewer theo epic và một reviewer Tree/Dependencies; fixes cơ học xử lý, các ask slicing đã được người dùng chấp nhận.
- [Actual status](ticket-status-final.json): **22/22 planned**, sáu epic, không problems/drift/unpinned_after/undeclared_after/order_conflict. [Actual next](ticket-next-final.json): **EPA.S01 ready_to_start**, **21 blocked** bởi dependencies/unknown. `ready_to_start` là trạng thái board, không quyền code/train trong Prompt 3.
- [Final verification](verification-final.json): cấu trúc/IDs/links/provenance/preservation và registry marker. [Baseline](inputs-before.json), [integrity trước tiếp tục](continuation-integrity.json), [registry trước](registry-before-official-import.json) và [spec đã duyệt trước ticket](history/spec-approved-before-ticket/) bảo toàn lịch sử.
- [Artifact hashes](artifact-hashes.json): bộ mới và store; hash chỉ là integrity evidence, không chữ ký phê duyệt chuyên môn.

Registry đã đổi **marker top-level `official_planning_imported=true`** và metadata import. Toàn subtree datasets, current_run, counts, training_ready/safe_for_advice và vai trò research-only giữ nguyên. Hai input thay đổi có chủ đích: initiative stub thành envelope và registry metadata. Draft, config và sealed integration không đổi; không rehash toàn corpus raw hoặc kết luận raw chưa từng thay đổi trước baseline.

22 lookup unit tests là kết quả lịch sử `ir-20261014-v1`, không chạy lại ở đây. Chưa chạy model, UI/native E2E, clean-machine hoặc expert/user study. Kiểm định ticket/store chỉ chứng minh cấu trúc kế hoạch và hợp đồng phụ thuộc, không chứng minh khả năng nhận diện hoặc chăm sóc.

## Blocker và bước tiếp theo

1. **S01/EPA.S01**, [epic governance](../epic-governance-data/epic-governance-data.md): điều tra/ghi quyết định rubric, quyền asset, B0/framework/stack/version/budget/targets và C3. Đây là story đầu tiên đề xuất cho phiên sau; không tự thực hiện trong Prompt 3. Một sinh viên/2h mỗi tối/112h vẫn là giả định nguồn, không estimate đã được người dùng duyệt.
2. **S03/S04 trước S05:** full 10-class grouping/near/label evidence và benchmark chưa đủ; Target/mosaic zero grouping, mosaic ToMV/TMV chưa xác minh. Không random unresolved hoặc tạo class_to_idx checkpoint giả.
3. **S10/S11 trước S06:** 17 card domain/VI pending, 0 guidance thật được phép. C3 policy, từng claim, reviewer/source/context/translation phải được xử lý; synthetic approved fixture không thay card thật. S10b/S11b mở rộng phần còn lại, không chặn tracer thẻ đầu.
4. **S06:** lát cắt desktop triển khai đầu tiên chỉ sau approved benchmark/head checkpoint sinh viên/allowed VI card và quyền giai đoạn sản phẩm. Không đợi toàn UI mới thử tích hợp.
5. **S16/S17/S18:** ảnh thực tế/ground truth, reviewer/người học, rights và Windows sạch chưa đủ. Báo missing evidence nếu thiếu; không coi đó là chứng minh efficacy. WUR/Dryad/Mendeley/UC-IPM ngoài MVP, không chặn core.

**Planning sẵn sàng chuyển sang quyết định/ledger và chuẩn bị triển khai có kiểm soát; chưa sẵn sàng huấn luyện hoặc hiển thị hướng dẫn.** Dừng sau bàn giao này.