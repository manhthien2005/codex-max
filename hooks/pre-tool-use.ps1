# pre-tool-use.ps1 - Thin Windows compatibility shim for PreToolUse.
param()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

# Active PreToolUse checks live in hooks/pre_tool_use.py.
# For this event, empty stdout is the safest success path.
exit 0
