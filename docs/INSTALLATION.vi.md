# Hướng dẫn cài đặt

Tài liệu này chứa quy trình cài đặt và setup chi tiết cho workspace Codex.

Nó được tách khỏi [`README.md`](../README.md) để trang giới thiệu chính gọn hơn.

---

## 1. Mục tiêu của việc setup

Mục tiêu của quy trình cài đặt là làm cho repository này hoạt động như một workspace Codex ổn định với:
- runtime configuration đúng,
- hook wiring hoạt động,
- role agent có thể tái sử dụng,
- skill được tuyển chọn,
- ranh giới rõ ràng giữa source file và local runtime data.

---

## 2. Điều kiện tiên quyết

Trước khi dùng workspace này, cần xác nhận các công cụ sau có sẵn trên máy:

| Yêu cầu | Ghi chú |
|---|---|
| **Windows 11** | Hệ điều hành chính được hỗ trợ |
| **Git** | Để clone và quản lý version |
| **Node.js ≥ 18** | Cần cho MCP servers (memory, playwright, sequential-thinking, gitnexus) |
| **Python ≥ 3.10** | Cần cho hook scripts (`pre_tool_use.py`, `post_tool_use.py`, `stop.py`) |
| **PowerShell 5+** | Có sẵn mặc định trên Windows 11 |
| **Git Bash hoặc WSL** | Cần thiết cho các hook script `.sh` trong `hooks.json` |
| **Codex CLI** | Đã cài và xác thực với API key |
| **Docker Desktop** | Bắt buộc để chạy Qdrant vector database (`mcp/semantic`) |
| **Ollama** | Bắt buộc cài tại máy để tạo semantic embeddings (cần pull `qwen3-embedding:0.6b`) |

> [!NOTE]
> Các hook trong `hooks.json` dùng `sh` (cú pháp Bash). Trên Windows, cần **Git Bash** (đi kèm với Git for Windows) hoặc **WSL**. Chỉ dùng `cmd.exe` sẽ không chạy được các hook này.

---

## 3. Clone repository

```powershell
# Thay <your-username> bằng tên người dùng Windows của bạn
git clone https://github.com/manhthien2005/codex-max.git C:\Users\<your-username>\.codex
```

> [!IMPORTANT]
> Workspace **phải** nằm tại `C:\Users\<your-username>\.codex` để Codex tự nhận diện.
> Codex sẽ tìm `AGENTS.md`, `config.toml`, và `hooks.json` tại đường dẫn này khi khởi động.

Kiểm tra sau khi clone:

```powershell
ls C:\Users\$env:USERNAME\.codex
```

Các mục phải có ở cấp root: `AGENTS.md`, `config.toml`, `hooks.json`, `agents/`, `hooks/`, `skills/`, `.gitignore`.

---

## 4. Điều chỉnh cấu hình cho máy của bạn

### 4.1 Thay toàn bộ đường dẫn cứng trong `config.toml`

Mở `config.toml` và tìm mọi chỗ có `MrThien`. Thay bằng tên người dùng Windows của bạn.

```powershell
# Xem trước tất cả đường dẫn cần thay
Select-String -Path "C:\Users\$env:USERNAME\.codex\config.toml" -Pattern "MrThien"
```

Các phần chứa đường dẫn tuyệt đối cần chỉnh:

```toml
# Launcher MCP server — mỗi dòng được đánh dấu ← EDIT trong config.toml:
[mcp_servers.gitnexus]
command = "node"
args = ['C:\Users\<YOUR_USERNAME>\AppData\Roaming\npm\node_modules\gitnexus\dist\cli\index.js', "mcp"] # ← EDIT

[mcp_servers.qdrant]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\qdrant\\run-qdrant-mcp.cmd" # ← EDIT

[mcp_servers.semantic_qdrant_http]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\semantic\\run-semantic-qdrant-stdio.cmd" # ← EDIT

[mcp_servers.mempalace]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\mempalace\\run-mempalace-mcp.cmd" # ← EDIT
```

### 4.2 Cập nhật trusted project paths

Trong `config.toml`, các mục `[projects.'...']` liệt kê các path mà Codex xem là tin cậy. Thay hoặc xóa các mục dành riêng cho máy gốc:

```toml
[projects.'D:\DoAn2\VSmartwatch']
trust_level = "trusted"
```

Thêm các project path của bạn vào theo nhu cầu.

---

## 5. Cài đặt MCP Launcher cục bộ (`mcp/`)

> [!WARNING]
> Thư mục `mcp/` bị **loại khỏi Git** (xem `.gitignore`). Nó **không được clone** — bạn phải tự setup trên mỗi máy.

Thư mục này chứa binary và launcher script cho các MCP server cục bộ:

| MCP Server | Đường dẫn launcher | Cách setup |
|---|---|---|
| `qdrant` | `mcp/qdrant/run-qdrant-mcp.cmd` | Python venv + `pip install mcp-server-qdrant` |
| `semantic_qdrant_http` | `mcp/semantic/run-semantic-qdrant-stdio.cmd` | Clone/build semantic adapter |
| `mempalace` | `mcp/mempalace/run-mempalace-mcp.cmd` | Cài MemPalace MCP server |

Tạo thư mục `mcp/`:

```powershell
New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\.codex\mcp" -Force
New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\.codex\mcp\qdrant" -Force
New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\.codex\mcp\semantic" -Force
New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\.codex\mcp\mempalace" -Force
```

Sau đó làm theo hướng dẫn cài đặt của từng công cụ để đặt file launcher `.cmd` đúng vị trí.

> [!NOTE]
> Các MCP server `memory`, `playwright`, `sequential-thinking`, `context7`, `github`, `exa` **không** cần setup `mcp/` — chúng dùng `npx` hoặc remote URL và tự cài khi dùng lần đầu.

### Cài `gitnexus` toàn cục

```powershell
npm install -g gitnexus
```

Kiểm tra:

```powershell
node "C:\Users\$env:USERNAME\AppData\Roaming\npm\node_modules\gitnexus\dist\cli\index.js" --version
```

---

## 6. Kiểm tra hook scripts

```powershell
ls "C:\Users\$env:USERNAME\.codex\hooks\"
```

Tất cả script được `hooks.json` tham chiếu phải tồn tại. Các file cần có:
- `session-start.sh` (và tùy chọn `.ps1`)
- `user-prompt-submit.sh`
- `pre_tool_use.py`
- `post_tool_use.py`
- `stop.py`

> [!IMPORTANT]
> Các hook trong `hooks.json` dùng `sh` để chạy file `.sh`. Cần **Git Bash** phải được cài và `sh` có trong `PATH`. Kiểm tra:
> ```powershell
> sh --version
> ```
> Nếu không tìm thấy `sh`, hãy cài [Git for Windows](https://gitforwindows.org/) và đảm bảo thư mục `bin/` của Git Bash nằm trong `PATH`.

---

## 7. Checklist verify sau khi cài đặt

Chạy các lệnh sau để xác nhận mọi thứ đúng:

```powershell
# 1. Kiểm tra các file bắt buộc tồn tại
$base = "C:\Users\$env:USERNAME\.codex"
@("AGENTS.md","config.toml","hooks.json",".gitignore") | ForEach-Object {
    $p = Join-Path $base $_
    if (Test-Path $p) { Write-Host "OK  $_" } else { Write-Host "MISSING  $_" }
}

# 2. Kiểm tra các thư mục bắt buộc tồn tại
@("agents","hooks","skills","rules","docs") | ForEach-Object {
    $p = Join-Path $base $_
    if (Test-Path $p) { Write-Host "OK  $_\" } else { Write-Host "MISSING  $_\" }
}

# 3. Xác nhận không còn đường dẫn cứng MrThien
Select-String -Path "$base\config.toml" -Pattern "MrThien"
# Kỳ vọng: không có output (zero matches)

# 4. Kiểm tra node
node --version

# 5. Kiểm tra python
python --version

# 6. Kiểm tra sh (Git Bash)
sh --version
```

---

## 8. Kỷ luật vận hành được khuyến nghị

Sau khi cài xong:
- luôn giữ `mcp/` và các thư mục runtime cục bộ ở trạng thái ignored — không được commit,
- không trộn reference clone vào source surface chính,
- ưu tiên cập nhật tài liệu có chủ đích thay vì note rời rạc,
- giữ thay đổi cấu hình ở mức tối thiểu và dễ review,
- cập nhật `[projects.'...']` trong `config.toml` cho mỗi project mới cần Codex tin cậy.

---

## 9. Tài liệu liên quan

- Tổng quan chính: [`README.md`](../README.md)
- Tổng quan tiếng Việt: [`README.vi.md`](../README.vi.md)
- Tài liệu cấu trúc tiếng Anh: [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)
- Tài liệu cấu trúc tiếng Việt: [`PROJECT_STRUCTURE.vi.md`](PROJECT_STRUCTURE.vi.md)