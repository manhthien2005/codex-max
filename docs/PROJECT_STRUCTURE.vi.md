# Cấu trúc dự án

Tài liệu này mô tả cấu trúc làm việc thực tế của workspace Codex chi tiết hơn so với [`README.md`](../README.md).

Nó tập trung vào:
- các file source và cấu hình quan trọng,
- các file chính nằm trong các thư mục quan trọng,
- vai trò của từng vùng trong workspace,
- phần nào là source vận hành, phần nào chỉ là local artifact.

---

## Bố cục top-level

```text
.
├── AGENTS.md
├── config.toml
├── hooks.json
├── README.md
├── README.vi.md
├── agents/
├── docs/
├── hooks/
├── mcp/           ← gitignored, chỉ tồn tại cục bộ
├── rules/
├── skills/
└── vendor_imports/
```

Workspace còn chứa nhiều thư mục vận hành cục bộ như cache, session, temp clone, và SQLite state. Các mục đó đã được loại trừ bởi [`.gitignore`](../.gitignore) và không thuộc clean publishable surface.

---

## Các file lõi ở root

### [`AGENTS.md`](../AGENTS.md)
Hợp đồng vận hành chính của workspace.

Nó định nghĩa:
- protocol khởi động task,
- active repo detection,
- quy tắc an toàn multi-repo,
- strategy nạp skill,
- quy tắc sử dụng MCP,
- format báo cáo.

### [`config.toml`](../config.toml)
File cấu hình runtime Codex chính.

Vai trò chính:
- model và reasoning defaults,
- approval và sandbox policy,
- khai báo MCP server,
- trusted project paths,
- binding cho multi-agent role.

### [`hooks.json`](../hooks.json)
File đăng ký hook cho lifecycle automation.

Các event chính:
- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `Stop`

### [`README.md`](../README.md)
Trang giới thiệu tiếng Anh của repository.

### [`README.vi.md`](../README.vi.md)
Trang giới thiệu tiếng Việt của repository.

---

## Các thư mục chính

## [`agents/`](../agents)
Chứa định nghĩa các subagent role có thể tái sử dụng.

Các file chính hiện tại:

```text
agents/
├── docs-researcher.toml
├── explorer.toml
└── reviewer.toml
```

### Tóm tắt vai trò
- [`agents/explorer.toml`](../agents/explorer.toml): role read-only để thu thập bằng chứng
- [`agents/reviewer.toml`](../agents/reviewer.toml): role review cho correctness, security và regression checks
- [`agents/docs-researcher.toml`](../agents/docs-researcher.toml): role xác minh tài liệu và API

---

## [`hooks/`](../hooks)
Thư mục triển khai logic thực tế cho lifecycle hooks của workspace.

Các file chính hiện tại:

```text
hooks/
├── codex_hook_adapter.py
├── post_tool_use.py
├── post-tool-use.ps1
├── post-tool-use.sh
├── pre_tool_use.py
├── pre-tool-use.ps1
├── pre-tool-use.sh
├── session-start.ps1
├── session-start.sh
├── stop.ps1
├── stop.py
├── user-prompt-submit.ps1
└── user-prompt-submit.sh
```

### Nhóm chức năng
- khởi động session: [`hooks/session-start.sh`](../hooks/session-start.sh), [`hooks/session-start.ps1`](../hooks/session-start.ps1)
- inject context khi submit prompt: [`hooks/user-prompt-submit.sh`](../hooks/user-prompt-submit.sh), [`hooks/user-prompt-submit.ps1`](../hooks/user-prompt-submit.ps1)
- kiểm tra trước khi dùng tool: [`hooks/pre_tool_use.py`](../hooks/pre_tool_use.py), [`hooks/pre-tool-use.sh`](../hooks/pre-tool-use.sh), [`hooks/pre-tool-use.ps1`](../hooks/pre-tool-use.ps1)
- review sau khi dùng tool: [`hooks/post_tool_use.py`](../hooks/post_tool_use.py), [`hooks/post-tool-use.sh`](../hooks/post-tool-use.sh), [`hooks/post-tool-use.ps1`](../hooks/post-tool-use.ps1)
- stop/finalization: [`hooks/stop.py`](../hooks/stop.py), [`hooks/stop.ps1`](../hooks/stop.ps1)
- adapter hỗ trợ: [`hooks/codex_hook_adapter.py`](../hooks/codex_hook_adapter.py)

---

## [`rules/`](../rules)
Khu vực chứa rule asset của workspace.

File chính hiện tại:

```text
rules/
└── default.rules
```

### Vai trò
- lưu rule material mặc định mang tính policy cho workspace.

---

## [`skills/`](../skills)
Bề mặt skill được tuyển chọn để tái sử dụng workflow.

Các mục chính đang thấy gồm:

```text
skills/
├── README.md
├── workflow_bundles_readme.md
├── concise-planning/
├── lint-and-validate/
├── planning-with-files/
├── systematic-debugging/
├── task-intelligence/
├── verification-before-completion/
└── .system/
```

### Các nhóm skill quan trọng
- [`skills/concise-planning/`](../skills/concise-planning): hỗ trợ planning gọn
- [`skills/lint-and-validate/`](../skills/lint-and-validate): kỷ luật validation bắt buộc sau thay đổi
- [`skills/planning-with-files/`](../skills/planning-with-files): planning workflow dựa trên markdown bền vững
- [`skills/systematic-debugging/`](../skills/systematic-debugging): pattern debugging theo root-cause-first
- [`skills/task-intelligence/`](../skills/task-intelligence): phân tích task và định khung thực thi
- [`skills/verification-before-completion/`](../skills/verification-before-completion): completion gate yêu cầu bằng chứng

### Subtree hỗ trợ
- [`skills/.system/`](../skills/.system): skill hỗ trợ nội bộ/hệ thống

---

## [`vendor_imports/`](../vendor_imports)
Vùng chứa material import từ nguồn vendor.

Khu vực này nên được xem là imported support content hơn là vùng source chỉnh tay ưu tiên đầu tiên.

---

## `mcp/` (gitignored)
Thư mục binary và launcher script cho các MCP server cục bộ. Thư mục này **bị loại khỏi Git** vì chứa Python virtual environment (~305 MB) và đường dẫn tuyệt đối gắn với máy cụ thể.

```text
mcp/
├── mempalace/
│   └── run-mempalace-mcp.cmd
├── qdrant/
│   ├── run-qdrant-mcp.cmd
│   └── Scripts/           ← Python venv (~305 MB)
└── semantic/
    ├── run-semantic-qdrant-stdio.cmd
    └── semantic_qdrant_http.py
```

Xem [`docs/INSTALLATION.vi.md`](INSTALLATION.vi.md) phần 5 để biết hướng dẫn setup.

---

## Các vùng vận hành cục bộ

Các thư mục và file sau quan trọng cho runtime nhưng không thuộc clean publishable source layer:

- temp clone và planning scratch
- archived sessions và backup
- cache và binary tạm
- sandbox traces
- session history
- SQLite và state files
- credential/auth artifact cục bộ theo máy

Các mục này đã được exclude có chủ đích trong [`.gitignore`](../.gitignore).

---

## Thứ tự nên đọc

Nếu là người mới vào workspace, nên đọc theo thứ tự sau:

1. [`AGENTS.md`](../AGENTS.md)
2. [`config.toml`](../config.toml)
3. [`hooks.json`](../hooks.json)
4. [`agents/`](../agents)
5. [`skills/`](../skills)
6. [`README.md`](../README.md) hoặc [`README.vi.md`](../README.vi.md)

Thứ tự này giúp có cả policy context lẫn implementation context mà không bị lẫn với runtime noise đã ignore.