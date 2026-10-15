# Biên bản Prompt 1 — Setup BMAD

Ngày **13/10/2026**, Asia/Bangkok. **Đã setup runtime; chưa tiếp nhận planning draft thành kế hoạch chính thức.** Chỉ thực hiện Prompt 1 trong [hướng dẫn gốc](../../huong-dan-bmad-clean-tomatoai.md).

## Bản local và flow thực dùng

- Project root: `C:/Users/admin/Downloads/DACN_CayCaChua`, kiểm tra từ working directory; trước setup chưa có `_bmad/`, không có Git repository tại root.
- Skill chính: [bmad/SKILL.md](C:/Users/admin/.agents/skills/bmad/SKILL.md), đã đọc `references/setup.md` và `references/initiative.md` của chính bản local. Không gọi workflow planning/build/dev.
- Record local: `bmod-core-tools`, `bmod-method`, `bmod-toolsmith` đều **6.13.0-next**, scope global. Status trước setup: `bmad_exists=false`, scripts thiếu, không missing module record/duplicate/unmet requirement; `next="bmad setup"`.
- `uv 0.12.15` đã có tại `C:/Users/admin/.local/bin/uv.exe`. Interpreter kiểm tra bằng `uv run --no-project python`: **CPython 3.13.15**, `C:/Users/admin/AppData/Roaming/uv/python/cpython-3.13-windows-x86_64-none/python.exe`. Script resolver sử dụng stdlib/TOML. Không chạy lệnh cài thêm package, không cài GPU stack/dependency sản phẩm.
- `--list-config-questions` trả `[]`; setup trả `answers={}`, không có câu trả lời module cần hỏi hoặc file answers tạm.
- Không chạy `npx skills update`, `npx bmad-method install`, migration, đổi branch hoặc cài chồng module. Đối chiếu SHA256 các file skill/module local không có thay đổi; không suy phiên bản local từ upstream. Script status có kiểm tra nguồn module như cơ chế của bản cài, không cập nhật skill.

Các lệnh thực tế dùng trong flow chính (PowerShell, chạy từ project root):

```powershell
uv --version
uv run --no-cache 'C:\Users\admin\.agents\skills\bmad\scripts\setup.py' --project-root 'C:\Users\admin\Downloads\DACN_CayCaChua' --skill 'C:\Users\admin\.agents\skills\bmad' --root 'C:\Users\admin\Downloads\DACN_CayCaChua\.agents\skills' --root 'C:\Users\admin\.agents\skills' --root 'C:\Users\admin\.codex\skills' --status
uv run --no-cache 'C:\Users\admin\.agents\skills\bmad\scripts\setup.py' --project-root 'C:\Users\admin\Downloads\DACN_CayCaChua' --skill 'C:\Users\admin\.agents\skills\bmad' --root 'C:\Users\admin\Downloads\DACN_CayCaChua\.agents\skills' --root 'C:\Users\admin\.agents\skills' --root 'C:\Users\admin\.codex\skills' --list-config-questions
uv run --no-cache 'C:\Users\admin\.agents\skills\bmad\scripts\setup.py' --project-root 'C:\Users\admin\Downloads\DACN_CayCaChua' --skill 'C:\Users\admin\.agents\skills\bmad' --root 'C:\Users\admin\Downloads\DACN_CayCaChua\.agents\skills' --root 'C:\Users\admin\.agents\skills' --root 'C:\Users\admin\.codex\skills'
uv run '_bmad\scripts\resolve_config.py' --project-root 'C:\Users\admin\Downloads\DACN_CayCaChua' --key core.output_folder --key core.active_initiative
```

Sau setup và tạo initiative, chạy lại lệnh `--status` trên; tất cả exit code bằng 0. Kết quả setup: `status="created"`, shared/module scripts và config được tạo, `current=true`, `next=null`. Không tạo `_bmad` thủ công thay flow setup.

## File/config và output

| Vị trí | Thay đổi / trạng thái |
| --- | --- |
| `_bmad/config.toml` | Setup chính thức tạo; `[core] project_name="DACN_CayCaChua"`, `output_folder="{project-root}/_bmad-output"`. Project_name giữ mã thư mục, tên đề tài ở initiative và draft. |
| `_bmad/scripts/`, `_bmad/core-tools/scripts/`, `_bmad/method/scripts/`, `_bmad/toolsmith/scripts/` | Runtime được setup sao chép từ payload local; không sửa source runtime. |
| `_bmad/custom/.gitignore` | Setup chính thức tạo để bảo vệ config cá nhân; không tự sửa quy tắc ignore. |
| `_bmad/custom/config.user.toml` | Tạo theo hướng dẫn initiative: `[core] active_initiative="initiative-tomato-desktop"`. Chưa có file trước đó nên không ghi đè config cũ. |
| `_bmad-output/initiative-tomato-desktop/initiative-tomato-desktop.md` | Initiative mới được phép dùng slug tomato-desktop; chỉ frontmatter `type: initiative`, title tên đã chốt, `parent: none`. Chưa có epic/story/store breakdown. |
| `planning/tomato-desktop/` | Cập nhật 12 draft, thêm biên bản này. Draft giữ nguyên vị trí, không copy vào output để giả lập tài liệu chính thức. |

Resolver trả chính xác `core.output_folder="{project-root}/_bmad-output"`, `core.active_initiative="initiative-tomato-desktop"`. Thay `{project-root}` theo quy ước local: output tuyệt đối **`C:/Users/admin/Downloads/DACN_CayCaChua/_bmad-output`**; initiative ở **`_bmad-output/initiative-tomato-desktop/`**. Không có initiative phù hợp trước đó; đã tạo stub theo hướng dẫn được đọc, không dựng ticket store giả.

## Quyết định tên/phạm vi và bảo toàn lịch sử

**Người dùng chốt:** “Ứng dụng thẩm định và nhận diện dịch bệnh cho giống cây cà chua”. Nhận diện bệnh/trạng thái lá và hướng dẫn trồng/chăm sóc phù hợp; desktop Windows, offline, tiếng Việt; EfficientNet và ResNet50. Không thêm bài toán tối ưu canh tác, website hoặc AI API/dịch API.

Quyết định này thay thế tên lịch sử “Xây dựng ứng dụng máy tính nhận diện dịch bệnh và đưa ra phương pháp trồng tối ưu” và đề xuất tên trung gian trong brief cũ. WUR/Dryad/Mendeley vẫn giữ nguyên như tài nguyên nghiên cứu bổ sung, chưa là yêu cầu hoặc phụ thuộc MVP. Không dùng các bảng canh tác để gán nhãn tối ưu hay thêm mô hình/story trong lượt này.

Trước sửa đã sao lưu đầy đủ 12 draft, AGENTS.md và hướng dẫn gốc tại [checkpoint 20261013-234847](../setup-backups/20261013-234847/). Các biên bản khảo sát/tiếp nhận giữ nội dung lịch sử; README phân biệt tình trạng trước setup với hiện tại. Phần data-audit/research chỉ thêm thông báo scope, không biến khảo sát sơ bộ thành kết quả làm sạch mới.

Đã đối chiếu tập ID trên từng file draft trước/sau: **12/12 file giữ nguyên tập ID**, bao gồm FR01–FR14, NFR01–NFR10, S01–S20, T01–T20, CAP-1…CAP-9, AD-1…AD-8 và checkpoint hiện có. Không đổi các ID sang ID ticket store chưa tồn tại; không đánh dấu S01 hoặc test sản phẩm đã hoàn thành.

## Xác minh đã chạy

| Kiểm tra | Kết quả thật | Bằng chứng / giới hạn |
| --- | --- | --- |
| `bmad status` qua setup.py `--status` | `bmad_exists=true`, `current=true`, shared/module scripts `current`, không problems/unmet requirements/duplicates/missing module records, `next=null` | [bmad-status-after.json](../setup-backups/20261013-234847/evidence/bmad-status-after.json) |
| Config resolver | Đúng output và active initiative, exit 0 | [resolved-config.json](../setup-backups/20261013-234847/evidence/resolved-config.json) |
| Customization resolver cho 7 skill planning | Brief/recon/PRD/UX/architecture/spec/ticket đều exit 0; prepend/append đều rỗng | [activation-resolver-checks.json](../setup-backups/20261013-234847/evidence/activation-resolver-checks.json); lưu JSON riêng từng skill. Chỉ smoke check resolver, không gọi main workflow hoặc tạo run. |
| Đường script activation | resolve_config.py, resolve_customization.py, memlog.py, read_store.py và tickets.py tồn tại | [script-paths.json](../setup-backups/20261013-234847/evidence/script-paths.json) |
| Ticket store resolver chỉ đọc | `read_store.py --project-root ... -k tickets` exit 0, store mặc định `repo` | Đọc cấu hình store của bản cài, không khởi tạo tickets.toml, không chạy pull/create/planning. |
| Output chưa tiếp nhận draft | Chỉ có initiative Markdown với frontmatter; không có PRD/spec/run/memlog/tickets.toml | Inventory trong [preservation-checks.json](../setup-backups/20261013-234847/evidence/preservation-checks.json) |
| Bảo toàn raw | 18.362 file trước/sau; 0 khác biệt path/byte size/mtime UTC | Không hash lại toàn bộ raw; đây là kiểm tra metadata bảo toàn trong phạm vi setup, không chứng minh decode/nhãn/cleaning hoặc integrity toàn bộ byte. Không có thao tác ghi raw. |
| Biên bản/manifest tiếp nhận canh tác | SHA256 13 file metadata giữ nguyên | preservation-checks.json; dữ liệu/biên bản nguồn không sửa. |
| Skill local không nâng cấp | SHA256 86 file source trong bmad và 3 module record/payload giữ nguyên | So cả tập đường dẫn và hash; bỏ cache __pycache__/pyc khỏi source inventory. |
| ID draft và file chỉ dẫn | 12/12 tập ID giữ nguyên; hướng dẫn gốc và AGENTS.md giữ SHA256 | preservation-checks.json |

Không chạy SAST, E2E sản phẩm, build, làm sạch, chuẩn hóa/ghép/split dữ liệu, dịch dataset hoặc huấn luyện; chưa có metric mô hình hoặc kết quả nghiệm thu sản phẩm trong biên bản này.

## Blocker và dừng phiên

**Không còn blocker runtime cho Setup.** `docs/agents/domain.md`, `issue-tracker.md`, `triage-labels.md` chưa có; không tạo/publish `.scratch` issue hoặc triage nên không ảnh hưởng setup hiện tại. Chưa có rubric, chưa giải grouping/duplicate hoặc kiểm duyệt tri thức; đây là công việc/readiness còn thiếu cho các giai đoạn sau, không phải setup thất bại.

**Chưa tiếp nhận draft thành kế hoạch chính thức theo yêu cầu người dùng.** Bước tiếp theo là Prompt 2 cho từng dataset được chỉ định, đề xuất PlantVillage trước; chỉ bắt đầu khi có yêu cầu phiên tiếp theo. Có cleaning report/review queue/registry rồi mới dùng Prompt 3 cập nhật và tiếp nhận hồ sơ bằng workflow thật. Dừng tại đây, không làm sạch dữ liệu, viết ứng dụng hoặc train.
