# Quy trình đồ án, backlog và readiness

Ngày 13/10/2026. **Các giai đoạn/story dưới đây là công việc sẽ làm**, không đã thực hiện, trừ setup runtime được ghi riêng trong setup-report. Backlog đề xuất, chưa là ticket BMAD/store/issue. `docs/agents/issue-tracker.md` không tồn tại nên không publish `.scratch` issue; runtime đã setup nhưng chưa tiếp nhận draft thành tickets chính thức.

**Tên đã chốt:** “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”. Phạm vi hiện hành tại [README](README.md): nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp, desktop Windows/offline/tiếng Việt, EfficientNet và ResNet50; không tối ưu canh tác. WUR/Dryad/Mendeley là tài nguyên nghiên cứu bổ sung. Giữ S01–S20, T01–T20, FR/NFR/CAP/AD; setup không hoàn thành thay các AC của S01.

## Giả định ước lượng và nguồn lực

Người dùng xác nhận hai tháng và làm mỗi tối; chưa xác nhận số thành viên hoặc số giờ mỗi tối. Đề xuất baseline **một sinh viên × 2 giờ × 7 tối × 8 tuần = 112 giờ nhân công**, gồm 95 giờ story core và 17 giờ dự phòng. GPU compute dự kiến cap riêng 24 giờ, chưa đo và không cộng như giờ nhân công. Training kéo dài ngoài lúc theo dõi chỉ sau được phép; session/cooling/checkpoint cần kiểm. Nếu chỉ 1 giờ/tối, budget còn 56 giờ: cần giảm phạm vi tùy chọn/iterations hoặc tăng nguồn lực, không cắt chống leakage/hai mô hình/offline evidence.

Ngày bắt đầu/deadline chính thức chưa chốt; “hai tháng” không tự có nghĩa đúng 8 tuần. Bảng tuần là lịch tương đối để duyệt; giữ phần còn lại của khoảng hai tháng cho dự phòng/bảo vệ. Thiếu chuyên gia, ảnh thực tế và grouping mosaic có thể làm các mốc không đạt dù có đủ thời gian code.

## Bảng quy trình

Tên skill là **tên đã xác minh trong bản cài**, phục vụ planning; runtime/resolver đã khả dụng nhưng chưa chạy workflow downstream tiếp nhận draft, chờ báo cáo làm sạch và Prompt 3. Không có workflow `bmad-train` tự chế; huấn luyện/kiểm thử/đóng gói là việc tương lai được spec/ticket lập kế hoạch, chưa gọi build/dev.

| Giai đoạn | Mục tiêu | Skill/workflow BMAD thực tế | Đầu vào | Công việc sẽ làm | Đầu ra | Tiêu chí nghiệm thu | Phụ thuộc/rủi ro | Ước lượng có giả định |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0. Tooling/định hướng | Khả dụng runtime, output duy nhất | `bmad` setup/status và initiative theo bản local | Skills local, Prompt 1 | Đã setup/resolve; tiếp nhận draft sẽ làm sau báo cáo cleaning ở Prompt 3 | Runtime/config và initiative stub; chưa có roadmap chính thức | Status current=true; resolver trả đúng output/initiative; không tạo run/memlog giả | Setup xong; draft chưa nhập chính thức | Setup đã thực hiện; chưa cộng vào giờ story core |
| 1. Khảo sát | Biết dữ liệu thật/thiếu gì | `bmad-deep-recon` | Raw/metadata, data-audit, nguồn | Hoàn thiện provenance/license, corruption/duplicate/group coverage | Data card, inclusion/alias ledger | Counts/provenance/raw integrity kiểm được | Grouping 6.749 chưa khớp lookup; mosaic chưa có group | Tuần1–2; S01–S03, 14h |
| 2. Chốt bài toán | Phạm vi/tên và rubric rõ | `bmad-product-brief`, `bmad-prd`, `bmad-spec` | Brief, scope/name đã chốt, báo cáo cleaning | Đối chiếu rubric, duyệt target/hardware/limits và tiếp nhận draft đúng scope đã chốt | Brief/PRD/spec có quyết định | C0/C1, không có bài toán tối ưu canh tác | Giảng viên chưa có rubric | Tuần1; nằm trong S01/đồng thuận, tránh tính giờ hai lần |
| 3. Chuẩn bị/split | Benchmark không leakage | `bmad-spec`, `bmad-ticket` lập việc data | Group/duplicate evidence | Resolve/quarantine, grouped split, train-only statistics | Manifests/hash/exclusions | T15; supports/group đủ 10 lớp hoặc blocker minh bạch | Alias sai/thiếu groups có thể chặn benchmark | Tuần2; S04 4h sau S03 |
| 4. Pilot/lát cắt đầu | Kiểm tích hợp sớm | `bmad-architecture`, `bmad-ux`, `bmad-ticket` | Spec/contracts, một KB nguồn, train manifest | Pilot/head checkpoint rồi ảnh→worker→code→KB→UI minimal | Demo lát cắt và contract tests | T01/T04/T05/T07/T10; không phải hiệu quả model cuối | Không đợi UI hoàn chỉnh; một thẻ đủ milestone | Tuần2–3; S05/S06 12h + một phần S10/S11 |
| 5. Hai mô hình | So sánh có đóng góp DL | `bmad-spec`, `bmad-ticket` lập experiments | Split/pilot/config/budget | Head/fine-tune B0/ResNet50, logs, seeds, selection validation | Checkpoints/registry/selection record | T16; same split/budget, chưa dùng test | 4GB VRAM/Colab session/thermal | Tuần3–5; S07–S09 14h + compute chưa đo |
| 6. Tri thức/VI | Hướng dẫn có nguồn và scope review | `bmad-deep-recon`, `bmad-prd`, `bmad-ticket` | 10 thẻ EN, mapping, sources | Dịch nháp dẫn xuất, glossary, review/source claims, resolve links | KB VI/EN/version/review ledger | T07–T09; không fake expert approval | Reviewer chuyên môn thiếu; chemical bị suppress | Tuần1–5 song song nghiên cứu; S10/S11 12h |
| 7. Học tập/desktop | UX và LO có ý nghĩa | `bmad-ux`, `bmad-ticket` | KB/UX/LO/contracts | Lessons/quiz, các states, keyboard/DPI | UI native và content | T14/T19, content phù hợp scope | Chưa có người dùng thử/visual direction duyệt | Tuần4–6; S12/S13 10h |
| 8. Tích hợp/hardening | Gói hoạt động với artifact version | `bmad-architecture`, `bmad-ticket` | Winner/policy/KB/UI | Worker limits/cancel/errors/load-safe, resource/network privacy | Candidate integration | T02/T03/T10/T12/T18 | Artifact mismatch/native decoder | Tuần5–6; S14 6h |
| 9. Đánh giá cuối | Bằng chứng tách ML/care/learning | `bmad-prd`, `bmad-ticket` kế hoạch nghiệm thu | C4 locked, test/external/pilot | Test cuối cả hai, CPU, challenge nếu có ground truth; care/LO separately | Metrics/cards/qa evidence | T11/T16/T17; no test tuning; thiếu ghi rõ | External labels/expert/participants thiếu | Tuần6–7; S15–S17 10h |
| 10. Offline packaging | Chạy Windows sạch | `bmad-architecture`, `bmad-ticket` | Release assets/notices/test plan | Bundle CPU, test offline clean user, paths/errors/license | Gói demo và release manifest | T13/T18; không raw dataset/network fetch | License weights/Qt, DLL/antivirus, máy sạch | Tuần7; S18 6h |
| 11. Báo cáo/demo | Bảo vệ đúng bằng chứng | `bmad-spec`, `bmad-ticket` quản lý deliverable | Cards/logs/results/limitations | Viết báo cáo/slide/demo, rehearsal, kiểm traceability | Báo cáo, demo script, artifact index | T20; mọi claim có evidence | Rubric chưa có; không hứa số đẹp | Tuần8; S19 7h; dự phòng 17h toàn kỳ |

Tổng giờ story core bên dưới là nguồn ước lượng chuẩn; bảng giai đoạn gom story và có công việc song song, không cộng lại từng ô như các việc tách biệt. Lượt hiện tại chỉ giao tài liệu planning, không thực hiện các giai đoạn code/train.

## Epics và phụ thuộc

| Epic | Kết quả | Stories | CAP | Phụ thuộc |
| --- | --- | --- | --- | --- |
| EP-A | Governance và dữ liệu có căn cứ | S01–S04 | CAP-1,CAP-9 | C0, giấy phép/grouping |
| EP-B | Transfer learning và lựa chọn model | S05,S07–S09,S15 | CAP-2,CAP-8 | EP-A, C1/C2 |
| EP-C | Lát cắt desktop xuyên suốt | S06 | CAP-3,CAP-4,CAP-7 | S04,S05 và milestone một thẻ S10/S11 |
| EP-D | Tri thức VI và học tập | S10–S12,S17 | CAP-4,CAP-5,CAP-6,CAP-8 | Mapping/sources; review scope C3 |
| EP-E | UI đầy đủ, hardening, package | S13,S14,S18,S20 tùy chọn | CAP-3,CAP-7 | S06, S09, S10/S11; không chờ EP-B xong để bắt đầu minimal UI |
| EP-F | External evidence và bảo vệ | S16,S19 | CAP-8,CAP-9 | Test/model/content evidence, C4/C5 |

S10/S11 có milestone **một thẻ low-risk source_checked** được định nghĩa trong AC; S06 chỉ phụ thuộc milestone này, không đợi xong toàn kho. Milestone không phải ticket lẻ giả. Có thể chuẩn bị nội dung song song ML trong kế hoạch, nhưng mỗi giờ nhân công chỉ tính một lần; không ngầm có nhiều người.

## Stories đề xuất có acceptance criteria

Tất cả state là **đề xuất/chưa bắt đầu**. ID giữ để trace; khi BMAD ticket tạo store thật phải mapping ID/`covers` CAP, không ngầm coi tên S-n là ID store đã tồn tại. C0…C5 và test IDs là references, không outputs đã có.

| ID / mục tiêu | Yêu cầu và CAP | Dependency | Đầu ra sẽ có | Acceptance criteria và test | Nhân công giả định |
| --- | --- | --- | --- | --- | --- |
| **S01 — chốt scope và quyền dùng** | FR14,NFR01,NFR08,NFR10; CAP-9 | C0/C1, runtime đã setup, báo cáo cleaning trước tiếp nhận chính thức | Decision/rubric ledger, asset-license ledger, BMAD output thống nhất | Ghi đúng tên/phạm vi đã chốt, B0/stack/budget decisions; mỗi asset có source/revision/license/use/distribute/status; chưa rõ quyền phân phối là blocker, không “approved” giả; T20 | 3h, ngoài thời gian chờ giảng viên |
| **S02 — inventory/provenance đầy đủ** | FR12,FR14,NFR05,NFR07; CAP-1 | S01 | Data card, raw hash/decode inventory/exclusion list dẫn xuất | Count mỗi lớp/format khớp filesystem; decode errors/zero bytes/EXIF/mode ghi thật; raw không đổi; mẫu nghi nhãn chờ review; T15,T18 | 3h + read/hash wall-time |
| **S03 — giải grouping và trùng** | FR12,NFR05; CAP-1 | S02 | Group/alias/duplicate-component ledger | Mọi ảnh được dùng có group evidence; Target prefix đối chiếu và review, mosaic không auto-singleton; cross-label duplicates được quyết định; unresolved quarantine và báo class supports; T15 | 8h; có thể vượt nếu phục hồi thủ công |
| **S04 — split benchmark khóa** | FR12,NFR05; CAP-1 | S03,C2 | Train/val/test manifests/hashes, supports, config | Group/component intersections=∅, ratio thực tế ghi; split trước augmentation; class order stable; chưa đủ nhóm 10 lớp thì story bị chặn, không random fix; T15 | 4h |
| **S05 — pilot/head checkpoint** | FR03,FR12,NFR02,NFR05; CAP-2 | S04,C1, quyền chuẩn bị weights | Pilot compute/logs, head-only B0 và ResNet50 checkpoints | Training head do sinh viên thực hiện, BN/freeze/config/version/seed rõ; batch/VRAM/epoch time đo thật và chọn budget; checkpoint debug dùng cho slice có label “chưa đánh giá cuối”; T04,T05,T16 | 4h + GPU time |
| **S06 — lát cắt đầu một ảnh–một thẻ** | FR01–FR06,FR10,FR11,NFR09; CAP-3,CAP-4,CAP-7 | S04,S05; milestone 1 thẻ S10/S11; AD-1/UX duyệt | UI native tối thiểu, worker/preprocess/lookup contracts, evidence | Một ảnh hợp lệ → checkpoint sinh viên → đúng code/VI/source; một invalid và cancel không tạo kết quả/advice; không network/training trong app; exact fixture expectations, score chưa calibration gắn giới hạn; T01,T04,T05,T07,T10 | 8h |
| **S07 — fine-tune EfficientNet-B0** | FR03,FR12,NFR05; CAP-2 | S05 | B0 config A/B logs/checkpoints/trainable-layer record | Cùng split, head rồi fine-tune; chọn B0 config bằng val theo grid/budget, BN/augmentation/statistics train-only; test chưa mở; T16 | 5h + GPU time |
| **S08 — fine-tune ResNet50** | FR03,FR12,NFR05; CAP-2 | S05 | ResNet50 config A/B logs/checkpoints/trainable-layer record | Cùng điều kiện S07, record torchvision V1.5/weights enum; candidate count và effective batch minh bạch; không thêm CNN khác; T16 | 5h + GPU time |
| **S09 — chọn winner/policy bằng validation** | FR04,FR12,NFR03,NFR05; CAP-2,CAP-3 | S07,S08, negative validation nếu có | Repeat logs, selection/calibration/rejection record C4 | Ghi val macro-F1/recall/resources mỗi model, seed variation, winner rationale và locked hashes trước test; thiếu negative data thì không claim OOD detector tin cậy; T06,T16 | 4h + compute repeats |
| **S10 — VI/glossary/mapping dẫn xuất** | FR05,FR08,NFR08; CAP-4,CAP-5 | S01,S02 mapping; không đợi model final | Kho EN/VI draft, glossary, claim/source/alias ledger | Milestone đầu: một thẻ EN–VI low-risk có source alignment cho S11/S06; sau đó 10/10 code có record unique; raw giữ; không dịch runtime/API; 24 raw links có resolution/suppression reason; T07,T09 | 6h |
| **S11 — review nội dung và scope** | FR05,FR07,FR08,NFR08; CAP-4,CAP-5 | Milestone/outputs S10,C3 | Review ledger/version/bundle policy | Milestone đầu: một thẻ source_checked, actor/role/date/scope thật, không chemical thiếu nguồn; 10 thẻ theo review checklist; không expert thì demo label và chặn public/high-risk scope; unknown context không suy từ ảnh; T08,T09 | 6h; không gồm chờ reviewer |
| **S12 — lesson/quiz LO1–LO3** | FR09; CAP-6 | S10,S11 thẻ được phép | Lessons, 2 câu/thẻ, answer/explanation/source, assessment blueprint | Mỗi thẻ hiển thị có LO/symptoms/cause/prevention/limits; correct/wrong answers phản hồi đúng source; quiz score riêng ML; T14 | 4h |
| **S13 — UI states/keyboard/DPI** | FR01,FR04–FR07,FR09,FR10,NFR04; CAP-3,CAP-4,CAP-6 | S06,UX/AD-1 duyệt; knowledge/lesson milestones | UI đầy đủ trong phạm vi MVP, text/status mapping | Empty/loading/error/cancel/accepted/uncertain/unknown/knowledge_missing đủ; single-column khi hẹp, tiếng Việt không clipping ở DPI; bàn phím hoàn thành flow; T07,T10,T14,T19 | 6h |
| **S14 — hardening worker/input/model** | FR02,FR10,FR11,NFR06,NFR07,NFR09; CAP-7 | S06,AD-4/AD-8/limits duyệt | Resource/load-safe/cancellation/error policies và tests | 1 active/0 queued, stale render=0; magic/bytes/pixels limits exact; artifact lỗi fail closed; không ảnh/EXIF/path đầy đủ log; worker crash/retry bảo toàn ảnh; T02,T03,T10,T12,T18 | 6h |
| **S15 — final test và CPU benchmark** | FR12,FR14,NFR02,NFR03,NFR05; CAP-2,CAP-8 | S09/C4,S14 | Test metrics/per-class confusion, CPU profile, model card | Test mở sau lock, winner không đổi theo test; cả hai báo metrics thật/support, reject coverage/mẫu số rõ; 100 runs/10 warm-up cold riêng; missing repeats/targets failed báo thật; T11,T16 | 4h + eval wall-time |
| **S16 — external/challenge evidence** | FR04,FR14,NFR10; CAP-8 | S09,C4, nguồn/quyền/nhãn độc lập | External/challenge manifest hoặc blocker report | Có ground truth: không overlap source/group, metrics/support/false accept/reject đúng; thiếu: ghi qualitative only hoặc chưa đánh giá, không tự gán nhãn chắc/accuracy bịa; T06,T17 | 3h chỉ quản lý/đánh giá, không gồm tìm chuyên gia/thu đủ dữ liệu |
| **S17 — care/usability/learning evaluation** | FR05,FR09,FR14,NFR08; CAP-4,CAP-6,CAP-8 | S11,S12,S13; người tham gia nếu có | Mapping/source review và task/pre/post pilot hoặc missing-evidence log | Care đánh giá độc lập ML; actors/role thật; n/task/LO outcomes mô tả; không người/chuyên gia thì không claim user study/expert validation; T07–T09,T14,T17 | 3h, không gồm thời gian chờ người |
| **S18 — bundle Windows offline** | FR11,FR14,NFR01–NFR03,NFR06,NFR07; CAP-7,CAP-9 | S09,S11,S13–S15; license/review release scope đủ | Onedir/package manifest/notices/clean-machine evidence | Máy không Python/CUDA/cache/user thường chạy core offline; 0 raw dataset/network fetch/upload; missing artifact error/cancel/pathVI hoạt động; size/RSS/startup/license ghi; T12,T13,T18,T19 | 6h; chưa gồm signing/installer phức tạp |
| **S19 — báo cáo và bảo vệ** | FR06,FR14,NFR10; CAP-9 | S15–S18 (kể cả blocker report S16/S17) | Báo cáo, slide/demo script, artifact index | FR/NFR→story→test→evidence đủ; internal/external/care/EdTech tách; tên đã duyệt; số chưa đo để trống, giới hạn grouping/review/OOD minh bạch; rehearsal offline; T20 | 7h |
| **S20 — history local, tùy chọn hoãn** | FR13,NFR07; CAP-7 | Core S18 pass, user duyệt và còn budget | Opt-in local history/preferences, delete/export policy | Off=0 record/ảnh; bật có versions; xóa chỉ state đã chọn, không raw/input; không upload; T18 | 4–6h ngoài 95h core |

Nếu S03/S04 không chứng minh được nhóm cho mosaic hoặc full 10 lớp, **dừng benchmark đầy đủ** và duyệt phương án phục hồi/nguồn/scope trước S05–S09. Có thể nghiên cứu/biên tập/thiết kế độc lập, không báo 10-class benchmark đã sẵn sàng. Nếu chỉ làm pilot subset để kiểm stack, label “pilot subset”, không dùng làm kết quả so sánh đầy đủ hoặc fake success S04.

## Lịch tương đối tám tuần

| Tuần | Trọng tâm | Gate/đầu ra mong đợi | Rủi ro cần xử lý |
| --- | --- | --- | --- |
| 1 | S01/S02, bắt đầu S03, thẻ đầu S10 | Scope/ledger/tooling và evidence inventory | Rubric, cleaning và tiếp nhận draft còn thiếu |
| 2 | S03/S04, S05 pilot nếu group đủ; S11 thẻ đầu | C2 split hoặc blocker rõ; compute pilot | Mosaic/alias không phục hồi kịp |
| 3 | S06 lát cắt, S07/S08 bắt đầu | Một ảnh chạy xuyên suốt, contracts có tests | Không chờ UI đầy đủ |
| 4 | S07/S08, hoàn thiện S10/S11 và S12 | Two-model candidates, KB/lesson scope review | VRAM/time/source review |
| 5 | S09, S13/S14 | C4 validation winner/policy lock, UI states | Negative/OOD thiếu |
| 6 | S14/S15, S16/S17 khi có input | Final metrics và báo rõ evidence thiếu | Không chỉnh test để đủ metric |
| 7 | S18 packaging/clean-machine | Offline evidence C5, đóng feature | License/DLL/antivirus |
| 8 | S19 báo cáo/demo, xử lý lỗi trong reserve | Claim/evidence nhất quán, rehearsal | Không thêm history/ensemble sát bảo vệ |

## Đóng góp giao nhau có thể chứng minh

| ML/DL/Applied AI/AgriTech/EdTech | Đóng góp thực chất | Artifact | Cách chứng minh |
| --- | --- | --- | --- |
| ML | Thiết kế benchmark/split, chọn cấu hình, phân tích phân lớp và sai số | Manifests, experiments registry, per-class metrics | T15/T16; train/val/test discipline, không leakage |
| DL (thuộc ML) | Transfer learning head/fine-tune hai CNN, so chi phí/chất lượng | Configs/trainable layers/logs/checkpoints/ablation | T16, giải thích residual vs scaling và đóng góp fine-tune |
| Applied AI | Chuyển checkpoint thành inference/offline có contract/từ chối/knowledge | App/model bundle, parity/worker tests | T05/T06/T10/T13 demo trên máy sạch |
| AgriTech | Chuẩn hóa trạng thái cà chua, nguồn chăm sóc/điều kiện, taxonomy bệnh/nhện | Data/KB card, mapping/claim review ledger | T07–T09/T17; thiếu field/expert evidence nói rõ; không claim yield optimization |
| EdTech | Mục tiêu quan sát được, bài học/quiz có giải thích, formative evaluation | LO blueprint/lessons/answer keys/pilot | T14/T17, pre/post/task results nếu có; không gắn nhãn chỉ vì có đoạn văn |

Một pipeline đóng góp đồng thời nhiều lĩnh vực: ML cung cấp phương pháp, DL là model class, Applied AI là vận hành sản phẩm, AgriTech là bài toán/tri thức chuyên ngành, EdTech là mục tiêu và đánh giá học. Không phải năm mô hình hoặc năm tính năng không liên quan. Không yêu cầu novelty kiến trúc chưa có; đóng góp đồ án nằm ở pipeline/evidence/tích hợp/ngữ cảnh/learning có thể kiểm chứng.

## Readiness và checkpoint để duyệt

| Hạng mục | Trạng thái hiện tại | Việc cần trước phụ thuộc |
| --- | --- | --- |
| Scope cà chua/desktop/offline/VI/hai CNN | Đã chốt người dùng | Giữ trong spec |
| Thời hạn hai tháng/mỗi tối và máy | Đã khai báo, chưa benchmark | Xác nhận số giờ/người/ngày bảo vệ; pilot |
| Tên/phạm vi và rubric | Người dùng chốt tên mới và loại tối ưu canh tác; rubric chưa có | **C0:** lưu quyết định đã chốt, đối chiếu rubric giảng viên; không tự mở rộng phạm vi |
| EfficientNet variant/framework/stack | B0/PyTorch/PySide6 là đề xuất | **C1:** duyệt biến thể/stack/limits/metric/budget trước chuẩn bị dependency/weights |
| BMAD runtime/output | Setup local 6.13.0-next đã xong; output _bmad-output, initiative-tomato-desktop | Chờ báo cáo cleaning và Prompt 3 để nhập docs; chưa tạo PRD/spec/ticket chính thức, không upgrade |
| Raw local/count/schema | Đã khảo sát; corruption/trùng toàn bộ chưa kiểm | S02/S03 trong phiên được phép |
| Group split 10 lớp | **Blocker:** 6.749 chưa khớp sơ bộ; mosaic 0 match | **C2:** grouping/duplicate resolution hoặc scope/nguồn được duyệt; không random split |
| License datasets/weights/package | Local declarations/some docs đã đọc, ledger chưa đóng | S01; chưa rõ quyền distribute thì chặn package liên quan |
| Tri thức/VI | 10/10 chủ đề có thẻ; 24 raw links dangling; VI chưa làm | S10/S11, claim sources/corrections/glossary |
| Review chuyên môn | **Blocker cho expert approval/high-risk/public scope:** chưa có reviewer | **C3:** tìm người hoặc chỉ educational demo source_checked, không fake approval |
| External labeled dataset | **Blocker cho field validity:** hiện chưa có | S16 thu/nguồn hợp lệ được phép hoặc qualitative/không đo; giới hạn bảo vệ |
| Participants EdTech/UX | Chưa xác nhận | S17 pilot nếu có; không có thì chưa đo learning benefit |
| Model winner/threshold/metrics | Chưa có model hoặc kết quả | **C4:** lock validation selection trước final test |
| UI direction/bundle/QA native runner | Chỉ proposal, chưa implement/test | Duyệt UX, đọc e2e/config và chọn harness native phù hợp; **C5:** clean-machine evidence |
| Planning traceability | FR01–FR14/NFR01–NFR10/CAP1–9/S01–S20/T01–T20 đã đề xuất | Người dùng/giảng viên duyệt, BMAD tiếp nhận; không coi approval đã có |

Hồ sơ đủ làm cơ sở **review và lập kế hoạch triển khai**, nhưng chưa đủ để tự bắt đầu code/training hoặc tuyên bố BMAD planning đã chạy hoàn tất. Điểm chưa rõ có owner/action: sinh viên lấy rubric/nguồn/người review, người dùng duyệt C0/C1/C3, người triển khai giải grouping/tooling/QA theo S03/S04/S18. Không cần dừng công việc tài liệu độc lập để chờ những quyết định này.

## Đề cương báo cáo và demo bảo vệ

1. Bài toán, người dùng, tên/phạm vi đã chốt: nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp; ý nghĩa và giới hạn của “thẩm định”.
2. Cơ sở ML/DL, EfficientNet/ResNet50, transfer learning, domain shift và tri thức tra cứu.
3. Dataset/provenance/license, counts/imbalance/grouping/conflicts/exclusions, split/augmentation chống leakage.
4. Thiết kế thực nghiệm/grid/budget/seeds, hardware/versions, head→fine-tune, metric/selection protocol.
5. Kết quả **sau khi đo**: macro/per-class/confusion, seeds/CI nếu có, train/latency/RAM, rejected/OOD/internal vs external.
6. Knowledge/VI/review scope, thuật ngữ/nguồn, chất lượng guidance độc lập, EdTech LO/pilot và giới hạn người tham gia.
7. Kiến trúc/contracts/security/reliability, packaging/offline/clean-machine evidence.
8. Thảo luận lỗi/giới hạn/ethics of claims, đóng góp thực chất và hướng phát triển có dữ liệu cần bổ sung.
9. Kết luận theo mục tiêu đã duyệt, phụ lục manifests/configs/cards/QA traces/attribution.

Demo đề xuất 7–10 phút tùy rubric: máy offline cold launch → chọn ảnh demo có expected label/source fixture → ảnh không hợp lệ → uncertain/cancel → nguồn/VI review status → bài học/quiz → version bundle → bảng hai-model/selection và một failure case. Ảnh demo phải là fixture/public hoặc test đã dùng cuối với provenance, không dùng một ảnh đẹp làm bằng chứng accuracy toàn bộ. Nếu ảnh inference thực không khớp expected, trình bày failure thật, không sửa kết quả thủ công. Chuẩn bị package và video dự phòng sau khi được phép, không dựng video demo giả trong lượt này.

Câu hỏi bảo vệ cần chuẩn bị: tại sao B0, ResNet50 implementation/weights nào, khác nhau architecture và recipe; vì sao nhóm lá trước split; cách tránh augmentation/test leakage; macro-F1 so accuracy; tại sao winner bằng val; softmax/OOD có giới hạn gì; CNN có sinh lời khuyên không; nguồn/VI/review scope; offline kiểm thế nào; “thẩm định” hỗ trợ quan sát đến đâu; bằng chứng EdTech thực là gì; phần sinh viên tự làm và phần pretrained/library kế thừa.

## Phiên tiếp tục

Đọc README và setup-report; runtime đã khả dụng. Phiên sau chỉ thực hiện Prompt 2 cho dataset được chỉ định khi người dùng yêu cầu; lưu cleaning report/review queue/registry. Sau đó Prompt 3 mới cập nhật và tiếp nhận hồ sơ vào output/initiative, tạo memlog/spec/tickets bằng workflow thật, giữ ID. **Lượt hiện tại dừng sau Setup; không làm sạch dữ liệu, code ứng dụng, dịch dataset hoặc train.**
