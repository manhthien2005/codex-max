# post-tool-use.ps1 — Thin Windows compatibility shim for PostToolUse.
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

# Active PostToolUse reminders live in hooks/post_tool_use.py.
exit 0
