**Ngôn ngữ:** [English](README.md) | [Tiếng Việt](README.vi.md)

<div align="center">

# AI Agent Workspace — Cấu Hình Codex Chuẩn Production

<img src="https://github.com/user-attachments/assets/0fcfb1a2-5f0b-4450-95d0-d55c9da57d09" alt="Project Logo" width="160" />

> Hệ thống workflow cho agent, ngữ cảnh bền vững, skill được tuyển chọn, hook tự động hóa, và kỷ luật vận hành multi-repo dành cho môi trường Codex nâng cao.

<br/>

**Workspace AI agent theo định hướng production cho Codex và các môi trường agent liên quan**

Repository này đóng gói một môi trường làm việc có kỷ luật cho phát triển phần mềm có AI hỗ trợ: agent tái sử dụng được, quy tắc vận hành chặt chẽ, planning bền vững, tự động hóa theo session, tích hợp memory cục bộ, và các convention hỗ trợ cho toàn bộ workspace.

<br/>

![Version](https://img.shields.io/badge/version-local-blue)
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

## Project Structure

Workspace này được tổ chức quanh một số lớp lõi chính:

- [`AGENTS.md`](AGENTS.md), [`config.toml`](config.toml), và [`hooks.json`](hooks.json) định nghĩa contract vận hành và hành vi runtime
- [`agents/`](agents) lưu các định nghĩa role subagent có thể tái sử dụng
- [`hooks/`](hooks) chứa các script tự động hóa theo vòng đời session
- [`skills/`](skills) cung cấp workflow tái sử dụng và tri thức vận hành đã được tuyển chọn
- [`rules/`](rules) lưu rule material bổ sung cho workspace
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

### TL;DR — bốn việc cần làm sau khi clone

```powershell
# 1. Clone đúng vào đường dẫn Codex tự nhận diện
git clone https://github.com/ThienPhanNoLife/codex-workspace.git C:\Users\$env:USERNAME\.codex

# 2. Thay toàn bộ đường dẫn cứng của username gốc
Select-String -Path "C:\Users\$env:USERNAME\.codex\config.toml" -Pattern "MrThien"
# Sửa config.toml — thay mọi chỗ "MrThien" bằng tên người dùng Windows của bạn

# 3. Tạo .tmp/ và setup MCP launcher cục bộ (không được Git track)
New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\.codex\.tmp" -Force

# 4. Cài gitnexus toàn cục
npm install -g gitnexus
```

Hướng dẫn đầy đủ bao gồm chi tiết từng bước:
- điều kiện tiên quyết (Node.js ≥ 18, Python ≥ 3.10, Git Bash),
- thay đường dẫn trong `config.toml`,
- setup MCP launcher trong `.tmp/` (qdrant, mempalace, semantic search),
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
