# Hướng dẫn cài đặt

Workspace này được hỗ trợ theo mô hình **WSL2-first**.

Trạng thái mục tiêu là:

- Codex home chuẩn ở `~/.codex`,
- runtime skills trong repo ở `./.agents/skills`,
- runtime skills cấp user ở `$HOME/.agents/skills`,
- launcher MCP và Python venv cục bộ ở `~/.codex/mcp`,
- Windows chỉ còn là bridge mỏng để launch vào WSL.

---

## 1. Yêu cầu

| Yêu cầu | Ghi chú |
|---|---|
| **WSL2 Ubuntu** | Runtime chính được hỗ trợ |
| **Git** | Clone và cập nhật |
| **Python 3.10+** | Hooks, bootstrap, MCP venv cục bộ |
| **curl** | Các script bootstrap |
| **Node.js LTS qua nvm** | Memory, Playwright, Sequential Thinking, GitNexus |
| **Codex CLI** | Cài bên trong WSL |
| **Docker** | Backend Qdrant |
| **Ollama** | Backend embedding cho semantic search |

> [!IMPORTANT]
> Không còn nhắm tới runtime native Windows. Hãy dùng WSL làm runtime thật, còn PowerShell chỉ để handoff vào WSL.

---

## 2. Source và Canonical Home

Bạn có thể bắt đầu từ một clone ở `/mnt/c/...`, nhưng home runtime chuẩn cuối cùng phải là:

```bash
~/.codex
```

Nếu đang có working copy trên Windows filesystem, script bootstrap sẽ backup `~/.codex` hiện tại rồi copy workspace sang đó.

---

## 3. Bootstrap runtime WSL

Chạy một lần trong WSL:

Nếu workspace đã ở `~/.codex`:

```bash
bash ~/.codex/scripts/wsl-setup.sh
```

Nếu đang migrate từ clone trên Windows filesystem, ví dụ:

```bash
bash /mnt/c/Users/<your-user>/.codex/scripts/wsl-setup.sh
```

Script sẽ:

1. cập nhật `~/.bash_profile` và `~/.bashrc` với block bootstrap của Codex
2. copy workspace sang `~/.codex`
3. cài hoặc kích hoạt `nvm` và Node.js LTS
4. cài `@openai/codex` trong môi trường npm của WSL
5. cài RTK nếu có thể
6. sync runtime skills vào `~/.codex/.agents/skills` và `$HOME/.agents/skills`
7. bootstrap `~/.codex/mcp` từ `mcp_template/`
8. bỏ qua Node MCP reinstall nếu local launcher binary đã có sẵn
9. chạy verify config và runtime

---

## 4. Runtime Skills

Repository có hai bề mặt skill tách biệt:

| Đường dẫn | Vai trò |
|---|---|
| `skills/` | Thư viện source, catalog, manifest, maintainer material |
| `.agents/skills/` | Bề mặt runtime để Codex discover trong repo |
| `$HOME/.agents/skills` | Bề mặt runtime cấp user |

Sau khi chỉnh curated library, làm mới runtime mirror bằng:

```bash
bash ~/.codex/scripts/sync-runtime-skills.sh
```

---

## 5. Bootstrap MCP cục bộ

`mcp/` là local-only và gitignored. Không được commit.

Nguồn publish chuẩn là [`mcp_template/`](../mcp_template). Bootstrap runtime cục bộ bằng:

```bash
bash ~/.codex/scripts/bootstrap-mcp-wsl.sh
```

Script này sẽ:

- tạo `~/.codex/mcp/qdrant`, `~/.codex/mcp/semantic`, và `~/.codex/mcp/mempalace`,
- copy launcher WSL và Python source đã publish từ `mcp_template/`,
- tạo Linux virtual environment dùng `bin/`,
- cài dependency cho Qdrant MCP,
- cài MemPalace vào venv riêng, ưu tiên local clone ở `.tmp/mempalace` nếu có.
- bỏ qua nhánh Node MCP reinstall nếu `~/.codex/mcp/npm/node_modules/.bin/*` đã sẵn.

### Bố cục launcher MCP

| Server | Launch path |
|---|---|
| `memory` | `~/.codex/scripts/run-with-nvm.sh npx -y @modelcontextprotocol/server-memory` |
| `playwright` | `~/.codex/scripts/run-with-nvm.sh npx -y @playwright/mcp@latest --extension` |
| `sequential-thinking` | `~/.codex/scripts/run-with-nvm.sh npx -y @modelcontextprotocol/server-sequential-thinking` |
| `gitnexus` | `~/.codex/scripts/run-with-nvm.sh npx -y gitnexus@latest mcp` |
| `qdrant` | `~/.codex/mcp/qdrant/run-qdrant-mcp.sh` |
| `semantic_qdrant_http` | `~/.codex/mcp/semantic/run-semantic-qdrant-stdio.sh` |
| `mempalace` | `~/.codex/mcp/mempalace/run-mempalace-mcp.sh` |

---

## 6. Backend cho semantic search

`semantic_qdrant_http` cần cả Qdrant và Ollama.

Các endpoint tối thiểu:

- Qdrant: `http://127.0.0.1:6333/healthz`
- Ollama: `http://127.0.0.1:11434/api/tags`

Bạn có thể chạy chúng theo cách mình muốn, miễn là các endpoint localhost trên hoạt động đúng.

Ví dụ chạy Qdrant bằng Docker:

```bash
docker run -d --name codex-qdrant -p 6333:6333 -p 6334:6334 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

Ví dụ chạy Ollama:

```bash
ollama serve
ollama pull qwen3-embedding:0.6b
```

> [!NOTE]
> Workspace không còn chặn các task không liên quan khi Qdrant hay Ollama đang down. Semantic search chỉ được check khi thực sự cần.

---

## 7. Verify

### Static checks

```bash
python3 ~/.codex/scripts/config-lint.py
sh -n ~/.codex/hooks/session-start.sh ~/.codex/hooks/user-prompt-submit.sh ~/.codex/scripts/*.sh ~/.codex/mcp_template/*/*.sh
python3 -m py_compile ~/.codex/hooks/*.py ~/.codex/scripts/*.py
python3 -m unittest discover -s ~/.codex/tests -p 'test_*.py'
```

### Verify runtime

```bash
python3 ~/.codex/scripts/verify-wsl-runtime.py
codex features list
codex mcp list
```

Kỳ vọng:

- `config-lint.py` pass, không còn path Windows-native hoặc `persistent_instructions`
- `codex_hooks` đang bật
- runtime skills tồn tại ở `$HOME/.agents/skills`
- toàn bộ local MCP launcher trỏ về `~/.codex`
- `github` có thể báo `auth_missing` cho tới khi export `GITHUB_TOKEN`

---

## 8. GITHUB_TOKEN cho GitHub MCP

Để bật `github` MCP trong WSL, lưu token vào file loader mà bootstrap shell của WSL sẽ đọc:

```bash
read -rsp "GitHub token: " GITHUB_TOKEN && echo
mkdir -p ~/.config/codex/env
printf '%s' "$GITHUB_TOKEN" > ~/.config/codex/env/github_token
chmod 600 ~/.config/codex/env/github_token
unset GITHUB_TOKEN
source ~/.bashrc
```

Kiểm tra nhanh:

```bash
test -n "${GITHUB_TOKEN:-}" && echo GITHUB_TOKEN_set
codex mcp list
```

Dòng `github` sẽ không còn báo `auth_missing`.

> [!NOTE]
> `UserPromptSubmit` giờ chạy qua `~/.codex/hooks/user_prompt_submit.py` và phát JSON `hookSpecificOutput.additionalContext`. Nếu anh tùy biến phần inject prompt, nhớ giữ file này đồng bộ với `hooks.json`.

---

## 9. Chạy Codex

Trong WSL:

```bash
bash ~/.codex/scripts/launch-codex-rtk.sh
```

Từ Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\<your-user>\.codex\scripts\launch-codex-rtk.ps1
```

Script PowerShell đó không chạy Codex native trên Windows. Nó chỉ gọi `wsl.exe ... ~/.codex/scripts/launch-codex-rtk.sh`.
