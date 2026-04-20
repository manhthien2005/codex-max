# Cấu trúc dự án

Tài liệu này mô tả bố cục WSL-first thực tế của workspace Codex.

---

## Top level

```text
.
├── AGENTS.md
├── config.toml
├── hooks.json
├── README.md
├── README.vi.md
├── .agents/
├── agents/
├── docs/
├── hooks/
├── mcp/              ← gitignored, runtime cục bộ
├── mcp_template/     ← template launcher/source MCP để publish
├── rules/
├── scripts/
├── skills/
└── vendor_imports/
```

## Các file runtime cốt lõi

| Đường dẫn | Vai trò |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | Contract vận hành |
| [`config.toml`](../config.toml) | Cấu hình Codex WSL-first |
| [`hooks.json`](../hooks.json) | Hook registration |
| [`scripts/wsl-setup.sh`](../scripts/wsl-setup.sh) | Bootstrap và migrate WSL |
| [`scripts/launch-codex-rtk.sh`](../scripts/launch-codex-rtk.sh) | Launcher chuẩn trong WSL |
| [`scripts/launch-codex-rtk.ps1`](../scripts/launch-codex-rtk.ps1) | Bridge từ Windows host vào WSL |

## Các bề mặt skill

### Thư viện source được tuyển chọn

`skills/` vẫn là source of truth cho:

- nội dung skill đã tuyển chọn,
- `CATALOG.md`,
- `manifest.yaml`,
- maintainer-only workflows,
- `.system` support skills nội bộ.

### Bề mặt runtime để discover

`.agents/skills/` là bề mặt skill trong repo mà Codex nên discover khi chạy.

Nó được tạo bởi [`scripts/sync-runtime-skills.sh`](../scripts/sync-runtime-skills.sh) dưới dạng mirror dùng symlink từ curated library.

Bề mặt cấp user nằm tại:

```text
$HOME/.agents/skills -> ~/.codex/.agents/skills
```

## Hooks

`hooks/` giờ nhắm WSL/Linux làm runtime chính.

Các file chính:

```text
hooks/
├── codex_hook_adapter.py
├── hook-probe.py
├── post_tool_use.py
├── pre_tool_use.py
├── rtk-shell-init.sh
├── session-start.sh
├── stop.py
├── user-prompt-submit.sh
└── user_prompt_submit.py
```

Hành vi chính:

- `SessionStart` tạo diary sentinel và chạy planning catch-up nếu có
- `UserPromptSubmit` giờ phát JSON `hookSpecificOutput.additionalContext` qua `user_prompt_submit.py`; shell script chỉ còn là helper legacy/manual
- `PreToolUse` và `PostToolUse` chỉ áp dụng cho Bash
- `Stop` vẫn là diary gate

## Các bề mặt MCP

### Nguồn publish

`mcp_template/` là source of truth được track trên git cho launcher cục bộ và adapter code.

### Runtime cục bộ

`mcp/` là machine-local và gitignored. Nó chứa:

- Linux virtual environment,
- launcher được copy từ `mcp_template/`,
- cache cục bộ và Python entrypoint.

Bootstrap bằng:

```bash
bash ~/.codex/scripts/bootstrap-mcp-wsl.sh
```

## Rules

`rules/default.rules` là bề mặt rule WSL đang active.

Allowlist Windows cũ đã được archive tại:

```text
rules/archive/windows-default.rules
```

## Runtime state cục bộ

Các vùng sau vẫn cố ý không track:

- `mcp/`
- cache và model download
- sessions và SQLite files
- `.tmp/`
- auth và machine-local state

Xem [docs/INSTALLATION.vi.md](INSTALLATION.vi.md) để biết setup và verify.
