@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: run-mempalace-mcp.cmd — Launcher for MemPalace MCP server
::
:: SETUP:
::   pip install mempalace
::   (uses the global or venv Python — no local venv needed)
::
:: No hardcoded paths — %USERPROFILE% is resolved at runtime.
:: ─────────────────────────────────────────────────────────────────────────────
setlocal

set "PYTHONIOENCODING=utf-8"
set "MEMPALACE_PALACE_PATH=%USERPROFILE%\.mempalace\palace"

python -m mempalace.mcp_server --palace "%USERPROFILE%\.mempalace\palace"

endlocal
