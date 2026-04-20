# pre-tool-use.ps1 - Quiet Windows compatibility shim for PreToolUse.
param()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

# Active PreToolUse checks live in hooks/pre_tool_use.py; do not dump plan context here.
Write-Output '{"decision": "allow"}'
exit 0
