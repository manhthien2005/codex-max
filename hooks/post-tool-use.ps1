# post-tool-use.ps1 — Quiet Windows compatibility shim for PostToolUse.
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

# Progress reminders are handled by agent planning discipline, not hook output.
exit 0
