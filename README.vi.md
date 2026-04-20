**Ngôn ngữ:** [English](README.md) | [Tiếng Việt](README.vi.md)

<div align="center">

# AI Agent Workspace — Cấu hình Codex WSL-First

<img src="https://github.com/user-attachments/assets/0fcfb1a2-5f0b-4450-95d0-d55c9da57d09" alt="Project Logo" width="300" />

> Workspace Codex có workflow tuyển chọn, planning bền vững, MCP cục bộ, và runtime WSL có thể tái lập cho công việc multi-repo.

[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](https://github.com/manhthien2005/codex-max/releases/tag/v1.0.0)
![Platform](https://img.shields.io/badge/platform-WSL2%20Ubuntu-0F4C81)
![Runtime](https://img.shields.io/badge/runtime-Windows%20host%20bridge%20%E2%86%92%20WSL-1F2937)
![Mode](https://img.shields.io/badge/focus-Codex%20Workspace-111827)

</div>

---

## Tổng quan

Repository này là một Codex workspace, không phải project template chung chung. Nó kết hợp:

- contract vận hành trong [`AGENTS.md`](AGENTS.md),
- cấu hình Codex WSL-native trong [`config.toml`](config.toml),
- hook automation qua [`hooks.json`](hooks.json) và [`hooks/`](hooks),
- skill đã tuyển chọn trong [`skills/`](skills) với bề mặt runtime được expose qua [`.agents/skills`](.agents/skills),
- launcher MCP và Python venv cục bộ trong `~/.codex/mcp/`, được publish từ [`mcp_template/`](mcp_template),
- semantic search, GitNexus, và MemPalace cục bộ khi các dịch vụ nền sẵn sàng.

Home runtime chuẩn là `~/.codex` bên trong WSL. Script PowerShell chỉ còn là bridge mỏng để nhảy vào runtime đó.

## Mô hình runtime

### Các path chuẩn

- Codex home chuẩn: `~/.codex`
- Runtime skills trong repo: `./.agents/skills`
- Runtime skills cấp user: `$HOME/.agents/skills`
- Nguồn MCP publish lên git: `./mcp_template`
- MCP runtime cục bộ theo máy: `~/.codex/mcp`

### Các lớp intelligence

| Lớp | Vai trò | Điều kiện |
|---|---|---|
| MemPalace | Memory bền vững cho dự án | Python venv cục bộ tại `~/.codex/mcp/mempalace` |
| Semantic search | Tìm code theo ý nghĩa | Qdrant + Ollama + semantic adapter |
| GitNexus | Code graph và impact lookup | Node/npm trong WSL |
| Context7 | Docs library/framework hiện tại | MCP remote |
| Exa | Web search | MCP remote |

Workspace giờ dùng mô hình **lazy-degrade**. Nếu task không cần MemPalace hay semantic search, việc các lớp đó đang down không còn là blocker.

## Luồng xử lý request

1. Codex đọc [`AGENTS.md`](AGENTS.md).
2. Hook từ [`hooks.json`](hooks.json) chạy qua `~/.codex/hooks/` khi được bật.
3. Agent xác định active repo, related repos, write scope, và git scope.
4. Phase PLAN đi qua `task-router-lite`.
5. Phase BUILD chọn skill hẹp nhất từ runtime skill surface.
6. Chỉ probe MCP/intelligence layer khi task thực sự cần.

## Bố cục repository

- [`AGENTS.md`](AGENTS.md), [`config.toml`](config.toml), [`hooks.json`](hooks.json): contract runtime
- [`agents/`](agents): role subagent tái sử dụng
- [`hooks/`](hooks): hook implementation cho WSL
- [`skills/`](skills): thư viện source được tuyển chọn, catalog, và maintainer surface
- [`.agents/`](.agents): bề mặt runtime để Codex discover skill
- [`mcp_template/`](mcp_template): template launcher/source WSL để publish
- `mcp/`: ignored, chỉ dành cho launcher, venv, cache cục bộ

Tài liệu cấu trúc chi tiết:

- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- [docs/PROJECT_STRUCTURE.vi.md](docs/PROJECT_STRUCTURE.vi.md)

## Bắt đầu nhanh

### 1. Đưa runtime chuẩn về WSL

Clone hoặc migrate repo này sao cho runtime home chuẩn là:

```bash
/home/<your-user>/.codex
```

Nếu working copy vẫn đang ở `/mnt/c/...`, hãy chạy bootstrap WSL một lần. Script đó sẽ copy workspace vào `~/.codex` và cấu hình mọi thứ từ đó.

### 2. Chạy bootstrap

Nếu clone đã ở `~/.codex`, chạy:

```bash
bash ~/.codex/scripts/wsl-setup.sh
```

Nếu đang migrate một lần từ clone trên Windows filesystem, ví dụ:

```bash
bash /mnt/c/Users/<your-user>/.codex/scripts/wsl-setup.sh
```

Bootstrap sẽ:

- migrate repo sang `~/.codex`,
- cài hoặc kích hoạt `nvm`, Node, Codex CLI, và RTK trong WSL,
- sync runtime skill surface sang `.agents/skills` và `$HOME/.agents/skills`,
- bootstrap `~/.codex/mcp` từ `mcp_template/`,
- bỏ qua Node MCP reinstall nếu các binary cục bộ cần thiết đã tồn tại,
- chạy verify config và runtime.

### 3. Chạy Codex

Trong WSL:

```bash
bash ~/.codex/scripts/launch-codex-rtk.sh
```

Từ Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\<your-user>\.codex\scripts\launch-codex-rtk.ps1
```

Script PowerShell đó chỉ handoff vào `~/.codex/scripts/launch-codex-rtk.sh` trong WSL.

## Cài đặt

Hướng dẫn cài đặt và verify đầy đủ ở đây:

- [docs/INSTALLATION.md](docs/INSTALLATION.md)
- [docs/INSTALLATION.vi.md](docs/INSTALLATION.vi.md)

## Ghi chú

- `mcp/` luôn là local-only và gitignored.
- Muốn publish thay đổi launcher hoặc MCP source thì sửa [`mcp_template/`](mcp_template), không sửa `mcp/`.
- `skills/` vẫn là thư viện source được tuyển chọn. `.agents/skills` là runtime mirror để Codex discover.
- MCP `github` có thể để trạng thái configured nhưng chưa có token; verify sẽ báo `auth_missing` cho tới khi export `GITHUB_TOKEN`.
