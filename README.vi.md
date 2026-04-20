**Ngôn ngữ:** [English](README.md) | [Tiếng Việt](README.vi.md)

<div align="center">

# AI Agent Workspace — Cấu Hình Codex Chuẩn Production

<img src="https://github.com/user-attachments/assets/0fcfb1a2-5f0b-4450-95d0-d55c9da57d09" alt="Project Logo" width="300" />

> Hệ thống workflow cho agent, ngữ cảnh bền vững, skill được tuyển chọn, hook tự động hóa, và kỷ luật vận hành multi-repo dành cho môi trường Codex nâng cao.

<br/>

**Workspace AI agent theo định hướng production cho Codex và các môi trường agent liên quan**

Repository này đóng gói một môi trường làm việc có kỷ luật cho phát triển phần mềm có AI hỗ trợ: agent tái sử dụng được, quy tắc vận hành chặt chẽ, planning bền vững, tự động hóa theo session, tích hợp memory cục bộ, và các convention hỗ trợ cho toàn bộ workspace.

<br/>

[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](https://github.com/manhthien2005/codex-max/releases/tag/v1.0.0)
![Platform](https://img.shields.io/badge/platform-Windows%2011-0078D4)
![Shell](https://img.shields.io/badge/shell-cmd%20%2B%20PowerShell-2C2D72)
![Mode](https://img.shields.io/badge/focus-Codex%20Workspace-111827)

</div>

---

## Introduction

Workspace này được thiết kế như một môi trường vận hành nghiêm túc cho phát triển phần mềm có agent hỗ trợ. Nó không nên được dùng như một thư mục scratch chung chung. Thay vào đó, nó đóng vai trò như một control plane tập trung cho Codex, nơi tập hợp role tái sử dụng được, workflow automation, skill loading, và sự tách biệt chặt chẽ giữa repository asset và machine-local runtime data.

---

## Overview

Repository này đóng vai trò như một lớp orchestration tập trung cho Codex trong công việc kỹ thuật hằng ngày. Nó kết hợp workflow được harden, code intelligence cục bộ, semantic search, memory bền vững, và cấu hình riêng cho từng dự án vào một workspace có thể lặp lại.

### Thành phần cốt lõi

- **Workflow hardening lấy cảm hứng từ ECC** — hệ thống rules, skills, hooks, và agent roles giúp planning, validation, review, và reporting nhất quán hơn qua từng task.
- **Codebase indexing bằng GitNexus** — hỗ trợ điều hướng cấu trúc code, tra cứu symbol, trace dependency, phân tích call graph, và hiểu impact trước khi sửa dự án thật.
- **Semantic search bằng Ollama + Qdrant** — embedding cục bộ và vector search giúp tìm code theo ý nghĩa/khái niệm mà không phụ thuộc vào external search infrastructure.
- **Session memory bằng MemPalace** — lưu giữ context dự án, quyết định kỹ thuật, và ghi chú quan trọng xuyên suốt nhiều session thay vì mất ngữ cảnh sau mỗi lần chạy.
- **Tùy biến theo từng project** — mỗi dự án có thể có rules, tools, MCP servers, và execution boundaries riêng để phù hợp với cách vận hành thực tế.

### Mục tiêu cốt lõi

- Duy trì một workspace Codex có thể chạy local và tái lập được
- Hỗ trợ làm việc multi-repo với boundary rõ ràng
- Kết hợp kỷ luật workflow với local code intelligence
- Giữ lại memory hữu ích của dự án qua nhiều session
- Tránh push cache, session trace, temp clone hoặc local state

---

## Cách hoạt động

### Vòng đời request

Mọi prompt từ người dùng đều đi qua một stack phân lớp trước khi tạo ra output:

```
User prompt
    │
    ├── [SessionStart hook] ──── tạo diary sentinel và nạp lại planning context khi có planning files
    │
    ├── [UserPromptSubmit hook] ─ inject planning context hiện hành từ task_plan.md vào prompt
    │
    ├── [AGENTS.md] ─────────── agent đọc operational contract:
    │       └── xác định active repo
    │       └── nạp thin PLAN router (`task-router-lite`)
    │       └── giữ `task-intelligence` chỉ như compatibility alias
    │       └── quyết định: chạy trực tiếp hay spawn subagent
    │
    ├── [Intelligence Layers] ── tra cứu trước khi viết code:
    │       └── MemPalace     → quyết định cũ, note kiến trúc
    │       └── Semantic search → code liên quan theo concept (Qdrant + Ollama)
    │       └── GitNexus      → symbol đích xác, call graph, blast radius
    │
    ├── [Skills / Agent roles] ─ Phase BUILD: nạp đúng skill hẹp nhất
    │
    ├── [PreToolUse hook] ───── kiểm tra Bash tool call theo active plan/runtime rules
    │
    ├── Code generation + edits
    │
    ├── [PostToolUse hook] ──── review Bash tool output so với plan
    │
    └── [Stop hook] ────────── chặn stop cho tới khi diary gate và active-plan gate được thoả mãn
```

### Các lớp Intelligence

| Lớp | Vai trò | Tình huống dùng |
|---|---|---|
| **MemPalace** | Memory bền vững qua nhiều session | Tra cứu quyết định cũ, context kiến trúc |
| **Qdrant Semantic** | Vector similarity search trên code | Tìm code liên quan theo ý định/concept |
| **GitNexus** | Structural code graph (symbol, deps) | Lookup chính xác, phân tích mồi ảnh hưởng |
| **Context7** | Tài liệu dự án/thư viện up-to-date | Đọc doc trước khi viết code phụ thuộc lib |
| **GitHub MCP** | Truy cập PR/issue | Review PR, đọc context issue |

### Bản đồ lưu trữ data

| Data | Vị trí | Ghi chú |
|---|---|---|
| Semantic vector index | Docker volume `qdrant_data` → `/qdrant/storage` | Re-index qua `mcp_template/semantic/repo-index.py` (hỗ trợ `--watch`) |
| MemPalace drawers | `~/.mempalace/palace/chroma.sqlite3` | Không bị mất khi reboot, ~ChromaDB |
| MemPalace knowledge graph | `~/.mempalace/palace/knowledge_graph.sqlite3` | Structured facts (chủ thể → vị ngữ → bổ ngữ) |
| GitNexus graph | `<repo>/.gitnexus/` trên từng repo | 60–70 MB mỗi repo, gitignored ở repo |
| GitNexus global registry | `~/.gitnexus/registry.json` | Chứa DS toàn bộ repo đã index |
| ChromaDB ONNX model | `~/.cache/chroma/onnx_models/` | 166 MB, tải một lần |
| Session hooks state | `./.sandbox/`, `./sessions/` | Chỉ chạy local, gitignored ở workspace |

---

## Project Structure

Workspace này được tổ chức quanh một số lớp lõi chính:

- [`AGENTS.md`](AGENTS.md), [`config.toml`](config.toml), và [`hooks.json`](hooks.json) định nghĩa contract vận hành và hành vi runtime
- [`agents/`](agents) lưu các định nghĩa role subagent có thể tái sử dụng
- [`hooks/`](hooks) chứa các script tự động hóa theo vòng đời session
- [`skills/`](skills) cung cấp workflow tái sử dụng và tri thức vận hành đã được tuyển chọn
- [`skills/CATALOG.md`](skills/CATALOG.md) và [`skills/manifest.yaml`](skills/manifest.yaml) theo dõi skill surface đã cài và trạng thái rollout dự kiến
- [`rules/`](rules) lưu rule material bổ sung cho workspace
- [`mcp_template/`](mcp_template) cung cấp launcher script mẫu và source semantic adapter để cài đặt `mcp/` trên máy mới
- các vùng local-only như cache, sessions, SQLite state, sandbox traces, và temp clones được giữ ngoài clean source surface

Nếu muốn xem chi tiết đầy đủ, gồm cả các file chính bên trong từng thư mục quan trọng, mặc định hãy mở bản tiếng Anh trước:

- Tài liệu chi tiết mặc định: [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)
- Bản tiếng Việt: [`docs/PROJECT_STRUCTURE.vi.md`](docs/PROJECT_STRUCTURE.vi.md)

---

## Quick Start

### 1. Mở đúng workspace root
Dùng chính thư mục này làm Codex workspace để runtime nhận diện được:

- [`AGENTS.md`](AGENTS.md)
- [`config.toml`](config.toml)
- [`hooks.json`](hooks.json)
- [`agents/`](agents)
- [`hooks/`](hooks)
- [`skills/`](skills)

### 2. Đọc operating contract
Đọc [`AGENTS.md`](AGENTS.md) trước. File này định nghĩa:

- active repo detection,
- write-scope discipline,
- Git-scope boundaries,
- flow nạp skills,
- kỳ vọng khi dùng MCP,
- format báo cáo.

### 3. Kiểm tra runtime configuration
Xem [`config.toml`](config.toml) để xác nhận:

- model mặc định,
- approval policy,
- sandbox setting,
- MCP server bindings,
- cấu hình multi-agent role.

### 4. Giữ workspace sạch
Kiểm tra [`.gitignore`](.gitignore) trước khi versioning workspace này. File này đã exclude các artifact máy cục bộ như cache, sessions, local databases, temp clones, và sandbox traces.

---

## How to Install

> Hướng dẫn đầy đủ: [`docs/INSTALLATION.vi.md`](docs/INSTALLATION.vi.md) · English: [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

### TL;DR — năm việc cần làm sau khi clone

```powershell
# 1. Clone đúng vào đường dẫn Codex tự nhận diện
git clone https://github.com/manhthien2005/codex-max.git C:\Users\$env:USERNAME\.codex

# 2. Thay toàn bộ đường dẫn cứng của username gốc
Select-String -Path "C:\Users\$env:USERNAME\.codex\config.toml" -Pattern "MrThien"
# Sửa config.toml — thay mọi chỗ "MrThien" bằng tên người dùng Windows của bạn

# 3. Bootstrap mcp/ từ template có sẵn (launcher + semantic adapter)
$src = "C:\Users\$env:USERNAME\.codex\mcp_template"
$dst = "C:\Users\$env:USERNAME\.codex\mcp"
New-Item -Force -ItemType Directory "$dst\qdrant", "$dst\semantic", "$dst\mempalace"
Copy-Item "$src\qdrant\*"    "$dst\qdrant\"
Copy-Item "$src\semantic\*"  "$dst\semantic\"
Copy-Item "$src\mempalace\*" "$dst\mempalace\"

# 4. Cài Python venv + dependencies cho qdrant/semantic MCP server
python -m venv "$dst\qdrant"
& "$dst\qdrant\Scripts\pip" install fastmcp qdrant-client mcp-server-qdrant

# 5. Cài gitnexus toàn cục và pull model Ollama
npm install -g gitnexus
ollama pull qwen3-embedding:0.6b
```

Hướng dẫn đầy đủ bao gồm chi tiết từng bước:
- điều kiện tiên quyết (Node.js ≥ 18, Python ≥ 3.10, PowerShell 5+, Docker Desktop, Ollama),
- thay đường dẫn trong `config.toml`,
- setup `mcp/` từ `mcp_template/` (qdrant, mempalace, semantic search),
- index repo với `repo-index.py` (one-shot hoặc `--watch` mode),
- kiểm tra hook scripts,
- checklist verify sau cài đặt bằng lệnh PowerShell có thể chạy ngay.

---

## Author

<div align="center">

<img src="https://avatars.githubusercontent.com/u/65497946?v=4" alt="Mr. Thien" width="96" style="border-radius: 50%;" />

## Mr. Thien

[![Facebook](https://img.shields.io/badge/Facebook-ThienPhanNoLife-1877F2?logo=facebook&logoColor=white)](https://www.facebook.com/ThienPhanNoLife/)

| Nền tảng | Liên kết |
|---|---|
| Facebook | [facebook.com/ThienPhanNoLife](https://www.facebook.com/ThienPhanNoLife/) |

**Lấy cảm hứng từ [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code), [GitNexus](https://github.com/0xPlaygrounds/gitnexus), và [MemPalace](https://github.com/MemPalace/mempalace).**

**Made with Mr. Thien**

</div>
