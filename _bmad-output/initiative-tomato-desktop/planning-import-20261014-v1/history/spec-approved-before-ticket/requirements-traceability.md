# Truy vết yêu cầu, story, test và phần việc còn lại

Ngày 14/10/2026. Giữ 9 CAP, 14 FR, 10 NFR, 8 AD, S01–S20 và T01–T20 của nguồn. Bảng là kế hoạch tiếp nhận có cập nhật evidence, **chưa là ticket store hoặc xác nhận test sản phẩm đã qua**. AC chi tiết tại companion PRD/delivery/security vẫn phải đọc.

## FR/NFR tới story và test

| Yêu cầu | Stories giữ ID | Tests giữ ID | Evidence/trạng thái hiện tại |
| --- | --- | --- | --- |
| FR01 | S06,S13 | T01,T10 | Chưa app; luồng/cancel dự kiến |
| FR02 | S06,S14 | T02,T03 | Chưa validator ảnh sản phẩm |
| FR03 | S05,S06,S07,S08 | T04,T05 | Class manifest đề xuất; chưa checkpoint |
| FR04 | S09,S13,S16 | T06,T17 | Threshold fixture 0,7 chỉ thử lookup; chưa detector OOD/calibration |
| FR05 | S10,S11,S13 | T07,T08 | 9 mapping identity source checked/1 pending; 10 thật bị chặn |
| FR06 | S06,S13,S19 | T05,T07,T20 | Giới hạn CNN/leaf-only trong spec; chưa model/app |
| FR07 | S11,S13 | T08 | Claim review/context/policy còn pending |
| FR08 | S10,S11 | T09 | EN bất biến; glossary draft, 0 VI approved |
| FR09 | S12,S17 | T14,T17 | LO/quiz kế hoạch; chưa lesson được phép/người học |
| FR10 | S06,S14 | T10,T11 | Worker/limits/cancel chưa triển khai |
| FR11 | S06,S14,S18 | T04,T12 | Lookup hash/version guard đã thử một phần; chưa loader model/app |
| FR12 | S03,S04,S05,S07,S08,S09,S15 | T15,T16 | Cleaning có evidence; chưa split/train/selection |
| FR13 | S20 | T18 | Optional; chờ core và duyệt riêng, không chặn S19 |
| FR14 | S01,S02,S15,S16,S17,S18,S19 | T16,T17,T20 | Report/review đã có; metric/demo/release chưa có |
| NFR01 | S18 | T13 | Chưa gói desktop/clean-machine evidence |
| NFR02 | S05,S15,S18 | T11,T13 | Phần cứng khai báo; chưa pilot/CPU benchmark |
| NFR03 | S09,S15,S18 | T11,T16 | Targets latency/RSS/size chỉ đề xuất C1 |
| NFR04 | S13 | T19 | UX reference; chưa UI/DPI/bàn phím test |
| NFR05 | S02,S03,S04,S05,S07,S08,S09,S15 | T15,T16 | Run/hash nguồn đã có; còn group/split/run model |
| NFR06 | S14,S18 | T02,T03,T10,T12 | Threat plan; chưa hardening sản phẩm |
| NFR07 | S02,S14,S20 | T18 | Run có integrity evidence; chưa product log/history |
| NFR08 | S01,S10,S11,S12 | T07,T08,T09 | Policy/licensing/claim/VI chưa đủ; không expert giả |
| NFR09 | S06,S14 | T04,T05 | Hợp đồng thiết kế; chưa parity training/inference |
| NFR10 | S16,S19 | T17,T20 | Field validity chưa đánh giá; mọi thiếu phải báo thật |

## Cập nhật stories theo dữ liệu, không khởi động thực thi

Các đầu ra và AC đầy đủ nằm ở [delivery-plan](../../../planning/tomato-desktop/delivery-plan.md). Bảng dưới bổ sung phần còn lại, dependency và tiêu chí chống nghiệm thu giả. Ước lượng gốc giữ nguyên, là nhân công giả định; công đã cleaning không bị yêu cầu làm lại.

| ID / epic / CAP | Phần việc sẽ làm và đầu ra | Dependency thật | Acceptance cập nhật / evidence |
| --- | --- | --- | --- |
| S01 / EP-A / CAP-9 | Decision/rubric/asset-license ledger; tiếp nhận BMAD qua checkpoint | Spec/user decisions C0/C1 | Ghi quyết định thật, license từng asset, scope sử dụng/phân phối; không coi setup thay AC; T20 |
| S02 / EP-A / CAP-1 | Tiếp nhận data card/provenance hiện có và delta evidence | S01 | Registry chỉ đúng run; tái dùng manifests/queues/hash, không rerun toàn cleaning; label verification riêng; T15/T18 |
| S03 / EP-A / CAP-1 | Giải grouping/near/alias trong bản dẫn xuất hoặc quarantine | S02 | 6.749 source missing/6.735 retained review phân biệt; Target 1.404/mosaic 373 không singleton đoán; unresolved không vào approved split; T15 |
| S04 / EP-A / CAP-1 | Versioned class/group/split manifest và supports | S03,C2 | Giao group/component=∅, khóa class order; full 10 lớp thiếu group thì blocked; subset pilot cần duyệt và không gọi full benchmark; T15 |
| S05 / EP-B / CAP-2 | Pilot/head checkpoints hai model, logs và compute budget | S04,S01/C1; quyền chuẩn bị weights/train phiên sau | B0 vẫn đề xuất; pin môi trường phù hợp, đo VRAM/batch thật; không dùng Python cleaning version thay compatibility; T04/T05/T16 |
| S06 / EP-C / CAP-3,CAP-4,CAP-7 | Một ảnh/checkpoint sinh viên/một record VI được phép chạy xuyên suốt | S04,S05; milestone một card S10/S11; AD-1/UX được duyệt | Không đợi toàn UI/17 cards; hiện 0 card được phép nên bị chặn; invalid/cancel/stale/blocked knowledge có kiểm chứng; T01/T04/T05/T07/T10 |
| S07 / EP-B / CAP-2 | EfficientNet-B0 head rồi fine-tune configs/logs | S05,C1 | Same split/budget; train-only fit, val selection; test chưa mở; T16 |
| S08 / EP-B / CAP-2 | ResNet50 head rồi fine-tune configs/logs | S05,C1 | Same split/budget; V1.5/weights recipe log thật, không thêm CNN; T16 |
| S09 / EP-B / CAP-2,CAP-3 | Selection/calibration/rejection record khóa | S07,S08; negative validation cho claim OOD nếu có | Winner/config/threshold chọn validation; thiếu negatives không claim detector OOD đáng tin; T06/T16 |
| S10 / EP-D / CAP-4,CAP-5 | Mapping/glossary/EN–VI/alias ledger dẫn xuất, milestone một card | S01,S02 | 10 lớp đều có exact mapping hoặc blocked reason; mosaic pending không ép accepted; 24 links có resolution/suppression bằng chứng; không cần toàn kho mới bàn giao card đầu; T07/T09 |
| S11 / EP-D / CAP-4,CAP-5 | Review ledger/policy/versioned allowed bundle, milestone một card | S10 milestone,C3 | 172 claim ledger giữ nguyên; chọn scope cần review, không đồng loạt bật safe_for_advice; source_checked≠expert; VI≠domain approved; chemical/risky blocked; T08/T09 |
| S12 / EP-D / CAP-6 | Lessons/quiz/explained keys/LO blueprint | S10/S11 card được phép | Mỗi card hiển thị có hai câu tự kiểm tra và nguồn; không CNN sinh quiz; T14 |
| S13 / EP-E / CAP-3,CAP-4,CAP-6 | UI đầy đủ states/keyboard/DPI trong scope | S06; S11/S12 milestone; UX/AD-1 | Uncertain/missing KB/pending review không mượn card gần tên; giới hạn/nguồn nhìn thấy; T07/T10/T14/T19 |
| S14 / EP-E / CAP-7 | Worker/input/model hardening và tests | S06; AD-4/AD-8/limits duyệt | 1 active/0 queued, stale render=0; safe loader fail closed, privacy/raw preservation; T02/T03/T10/T12/T18 |
| S15 / EP-B / CAP-2,CAP-8 | Final test/per-class metrics/CPU resources/model card | S09/C4,S14 | Test sau lock; không chọn winner bằng test; count/rejection mẫu số thật; T11/T16 |
| S16 / EP-F / CAP-8 | External/challenge evidence hoặc missing-evidence report | S09/C4; nguồn/quyền/nhãn độc lập | Không download phiên này; không ground truth thì chưa đo/qualitative, không bịa accuracy; T06/T17 |
| S17 / EP-D / CAP-4,CAP-6,CAP-8 | Care/usability/learning evidence hoặc missing-evidence log | S11,S12,S13; người tham gia nếu có | Có người/role thật mới claim user/expert study; tách khỏi F1 ảnh; T07–T09/T14/T17 |
| S18 / EP-E / CAP-7,CAP-9 | Offline package/notices/release manifest/clean-machine evidence | S09,S11,S13,S14,S15; quyền/review scope đủ | Không đóng gói raw/17 pending cards như tư vấn approved; máy sạch offline/user thường; T12/T13/T18/T19 |
| S19 / EP-F / CAP-9 | Báo cáo/slide/demo/evidence index/rehearsal | S15,S18; S16/S17 evidence hoặc blocker reports | T20 kiểm traceability/giới hạn; S16/S17 thiếu phải hiện công khai, không gán done nghiên cứu; không chờ S20 |
| S20 / EP-E / CAP-7 | History opt-in/delete/export, nếu duyệt | S18 core pass; quyền riêng và còn budget | Default off, không upload/raw deletion; optional parked, chưa approved; T18 |

Readiness của S01 là **đề xuất bắt đầu bằng quyết định/ledger**, không tuyên bố đã xong. S02 có nhiều evidence sẵn để tiếp nhận. S03/C2 là blocker khoa học trước S04/S05. S10 có thể biên tập độc lập grouping; S11/C3 chặn milestone guidance. S06 là lát cắt triển khai đầu tiên sau các gate, không là công việc được phép trong Prompt 3.

## Giới hạn kiểm chứng và trình tự

22 unit tests trong review `ir-20261014-v1` đã chạy ở phiên review: chứng minh lookup/hash/version/refusal trên fixture; fixture approved là tổng hợp. Chúng chỉ đóng góp một phần T04/T06/T07/T08/T09, không hoàn thành các test IDs này hoặc T05/parity/checkpoint/desktop/OOD/chuyên môn.

Trình tự đề xuất giữ sáu epic của nguồn: EP-A governance/data; EP-D knowledge mở sau S01/S02; EP-B pilot sau S04; EP-C S06 sau S05 và card milestone; EP-E UI/hardening/package; EP-F external/report. Đây là dependency graph có mốc qua lại, không đặt cả EP-B done làm prerequisite cho EP-C hoặc EP-E; S15 trong EP-B cần S14 trong EP-E. Khi `bmad-ticket` ghi store phải pin `after` tới story provider, tránh whole-epic cycle. Các việc có thể tiến song song về phụ thuộc không ngầm có nhiều người.

Không thêm story/refactor/test-suite ID tự động. `bmad-ticket` cần trình đề xuất closing sweep/E2E phù hợp cho epic >3 stories; dùng S14/S18/S19 để xác định coverage hiện có trước khi đề nghị scope mới. Quyết định thêm hoặc từ chối phải được người dùng ghi nhận, không invent consent.
