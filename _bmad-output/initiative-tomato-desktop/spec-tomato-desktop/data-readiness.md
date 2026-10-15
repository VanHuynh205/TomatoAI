# Evidence, readiness và cập nhật acceptance

Ngày 14/10/2026; phiên bản planning import `pi-20261014-v1`. Companion do `bmad-spec` dẫn xuất từ memlog và nguồn hiện có. Đây là baseline planning, không phải thao tác làm sạch/dịch/train mới.

## Thứ tự nguồn và bảo toàn lịch sử

Tên/phạm vi người dùng đã chốt được giữ nguyên. Registry chọn run, báo cáo/manifest/review queue của run xác định dữ liệu; review tích hợp `ir-20261014-v1` xác định linking/claim blockers. Khảo sát 13/10 và các dòng “chưa cleaned/chưa nhập/Setup only” trong companion là lịch sử, được thay về trạng thái bởi tài liệu này và quyền Prompt 3. AC chi tiết không xung đột vẫn giữ hiệu lực. Không sửa nguồn để che mâu thuẫn.

- [Registry](../../../data/TomatoAI/data/dataset-registry.json).
- [Review tích hợp](../../../data/TomatoAI/data/reports/integration/ir-20261014-v1/README.md), [mapping](../../../data/TomatoAI/data/reports/integration/ir-20261014-v1/mapping.md), [352 mục queue](../../../data/TomatoAI/data/reports/integration/ir-20261014-v1/review-queue.json).
- [PV report](../../../data/TomatoAI/data/reports/plantvillage/README.md), [PV queue](../../../data/TomatoAI/data/reports/plantvillage/pv-d9e4c21eec8e9172/review-queue.json).
- [KB report](../../../data/TomatoAI/data/reports/plantexpert-tomato/README.md), [110 mục queue nguồn](../../../data/TomatoAI/data/reports/plantexpert-tomato/pex-b3da04d66a031756/review-queue.json).
- [WUR](../../../data/TomatoAI/data/reports/wur/README.md), [Dryad](../../../data/TomatoAI/data/reports/dryad/README.md), [Mendeley](../../../data/TomatoAI/data/reports/mendeley/README.md), [UC IPM checkpoint](../../../data/TomatoAI/data/reports/uc-ipm-tomato/ucipm-20261014-acq-v1/README.md).

## Baseline tiếp nhận

| Dataset/run registry | Số liệu theo run/registry hiện hành | Readiness và vai trò |
| --- | --- | --- |
| PlantVillage `pv-d9e4c21eec8e9172` | 18.160 ảnh nguồn/10 lớp; 18.146 retained, 14 duplicate-byte excluded, 0 invalid; 11.411 technical split candidates, 6.735 retained review | Sạch kỹ thuật; chưa split/train-ready, nhãn chưa chuyên môn xác minh |
| PlantExpertVQA `pex-b3da04d66a031756` | 17 EN cards/17 retained; 10 draft links/10 thuật ngữ VI draft; 47 lookalike links có 24 unresolved | 17 domain/VI pending, 0 safe-for-advice; không là supervised QA/outcome training dataset |
| WUR `wur-7439c4f996527052` | 43 bảng/622.899 record; queue 134 | Research only; đơn vị/thời gian/độc lập/thích hợp nông học chưa đủ; không chặn MVP |
| Dryad `dryad-8b0f7c218098bfdf` | 8 bảng/508 record dẫn xuất từ 253 dòng vật lý; 108 formula cells; queue 79 | Research only; không là 508 thí nghiệm độc lập; không chặn MVP |
| Mendeley `mendeley-61d459ec1f46cef3` | 3.000 CSV +393 JSON =3.393; queue 103; chưa join | Research only; config “optimal” không là outcome đã chứng minh; không chặn MVP |
| UC-IPM `ucipm-20261014-acq-v1` | Permissions preflight HTTP 403; 21 mục không thử tải; 0 tài liệu cleaned | Nghiên cứu bị chặn; không có corpus mới hoặc review 172 claim mới; không chặn MVP, không bypass |

Các số là kết quả run đã có được đọc/đối chiếu trong phiên import; **không gọi là kết quả chạy cleaning hoặc kiểm đếm lại toàn corpus trong phiên này**. Đã kiểm lại 25 file thuộc artifact seal review: 0 mismatch. Snapshot/hash input và kiểm tra bảo toàn được lưu tại `../planning-import-20261014-v1/`. Raw/processed đã được các run và review đối chiếu trước đó; phiên planning không rehash toàn bộ raw. Baseline không chứng minh raw chưa từng thay đổi trước khi lập baseline.

## Trạng thái ảnh và liên kết

| Lớp | Source | Technical split candidates | Retained review | Excluded | Mapping identity |
| --- | ---: | ---: | ---: | ---: | --- |
| Bacterial spot | 2.127 | 2.127 | 0 | 0 | Source checked |
| Early blight | 1.000 | 999 | 1 | 0 | Source checked; không alias Target Spot |
| Late blight | 1.909 | 920 | 981 | 8 | Source checked; oomycete, không gọi nấm thật |
| Leaf Mold | 952 | 952 | 0 | 0 | Source checked |
| Septoria leaf spot | 1.771 | 1.000 | 771 | 0 | Source checked |
| Spider mites | 1.676 | 1.676 | 0 | 0 | Source checked; tác nhân gây hại |
| Target Spot | 1.404 | 0 | 1.404 | 0 | Source checked; grouping pending |
| Tomato Yellow Leaf Curl Virus | 5.357 | 2.738 | 2.619 | 0 | Source checked; không đồng nhất generic leaf curl |
| Tomato mosaic virus | 373 | 0 | 373 | 0 | Pending ToMV/TMV; grouping pending |
| Healthy | 1.591 | 999 | 586 | 6 | Source checked; không điều trị bệnh |

9 source-checked identity links, 1 pending, 0 missing card. Đây là Codex đối chiếu danh tính, **không xác nhận nhãn từng ảnh hoặc chuyên gia duyệt**. 6.749 record nguồn thiếu grouping, gồm 14 excluded; không đánh đồng với 6.735 retained review. Class manifest lexical 10 lớp chỉ là đề xuất, chưa có `class_to_idx` checkpoint được chốt.

## Tri thức, tiếng Việt và quyền hiển thị

172 management claims còn giữ EN: 26 source-checked candidate principles, 34 hỗ trợ một phần/context pending, 107 chưa xác minh, 5 specific-risk hold. **0 claim thật được mở hiển thị**. 16 card chứa chemical arrays; chemical ngoài array cũng cần kiểm. 56 alias occurrences: 4 accepted theo danh tính (hai synonym leaf mold), 6 blocked, 46 pending. Không giải alias bằng fuzzy matching.

S10/S11 làm thẻ đầu; S10b/S11b xử lý phần scope MVP còn lại phù hợp; 7 card không có lớp classifier vẫn ở kho với phạm vi riêng, không ép thành nhãn model. 17 card đều chưa domain/VI approved, nhưng không bắt buộc duyệt cả 17 để hoàn thành milestone một card. Không dịch toàn bộ ở Prompt 3. Ưu tiên EN–VI dẫn xuất lưu source/hash/claim pointer/glossary/revision, actor/role/date và trạng thái **ngôn ngữ tách chuyên môn**. Kiểm phủ định, đơn vị, điều kiện, tác nhân và không thêm thuốc/liều/cách ly.

Draft cho phép demo giáo dục low-risk `source_checked`; validator thật đang chặn `safe_for_advice=false`. **Đây là quyết định C3 pending**, không tự thay policy hoặc bật flag. S11 phải trình policy/version và từng claim trước khi tạo bundle demo. Không chuyên gia thì không ghi `expert_approved`; public/high-risk vẫn bị chặn. Bản dịch hoàn chỉnh không mở guidance nếu chuyên môn/policy chưa đủ.

License dataset, tài liệu cấu thành, weights, code và bundle cần ledger riêng S01. Metadata CC BY của kho không tự áp dụng cho mọi nguồn trích bên trong. UC IPM acquisition không tạo quyền tái phân phối hay nội dung tiếng Việt đã rà soát.

## Checklist và blocker theo story

| Gate | Đã có | Còn thiếu / acceptance bị chặn | Story/test |
| --- | --- | --- | --- |
| Runtime | BMAD 6.13.0-next, đúng output/initiative; spec và ticket proposal được người dùng duyệt | Store có 6 epic/22 entry sau nhập; xem kết quả actual status/next trong planning import. Chưa bắt đầu story | S01/T20 |
| Scope | Tên/Windows/offline/VI/two CNN/no optimization đã chốt | Rubric, giờ/team/deadline; B0/stack/targets còn đề xuất | S01; C0/C1; AD-1…AD-8 |
| Provenance | Cleaning + sealed review + registry hiện hành | Nhãn chuyên môn, asset rights; không chạy lại cleaning vô cớ | S01/S02; T15/T18/T20 |
| Split | 11.411 ứng viên kỹ thuật | Target/mosaic zero grouping, near-candidates; full 10-class benchmark chưa đủ | S03/S04; C2; T15 |
| Model | Hai kiến trúc và kế hoạch đã có | Không checkpoint/train/metrics; cần split và quyền chuẩn bị weights | S05/S07/S08/S09/S15; T04–T06/T11/T16 |
| Linking | 9 identity links/1 pending; validator có historical 22 tests qua | Mosaic; class-order approval; mapping không bằng image-label verification | S10/S10b; T04/T07/T08 |
| Guidance/VI | 17 EN card/claim ledger/10 VI glossary draft | 0 card display allowed; C3 policy, domain/translation review, nguồn/license | S10/S11/S10b/S11b; T07–T09 |
| Slice | Hợp đồng lookup có fixture | C1/C2/C3, checkpoint sinh viên và một card được phép; chưa UI | S06; T01/T04/T05/T07/T10 |
| Field/OOD/learning | Kế hoạch và giới hạn | Ground truth ngoài miền, negatives/reviewer/participants chưa có | S16/S17; T06/T14/T17/T20 |
| Release | Kiến trúc/risk/test plan | Máy sạch, offline/resource evidence, notices và release scope | S14/S18; T10–T13/T18/T19 |

**Kết luận hiện tại:** có evidence để lập kế hoạch và hợp đồng chặn đúng; chưa sẵn sàng huấn luyện, chưa sẵn sàng hiển thị hướng dẫn, chưa đủ khẳng định model hoặc chăm sóc hiệu quả. WUR/Dryad/Mendeley/UC-IPM không là blocker MVP.


## Readiness planning sau checkpoint

Decision 14/10/2026: người dùng duyệt spec và ticket set revision 2 (6 epic/22 story), gồm split thẻ đầu, membership S15/S17, ngoại lệ opening governance và không thêm Refactor sweep riêng. Store chỉ ghi planned, không mark done hoặc tạo build plan. S01 là entry governance có thể được tiếp tục sau Prompt 3 theo quyền phiên sau; S20 vẫn chưa được duyệt triển khai. Metadata official_planning_imported chỉ đánh dấu nhập planning, không thay training_ready hoặc safe_for_advice. Các baseline source hashes và current_run không được đổi theo planning approval.
