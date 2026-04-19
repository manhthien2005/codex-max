@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: run-qdrant-mcp.cmd — Launcher for mcp-server-qdrant (upstream MCP server)
::
:: SETUP:
::   1. Create a Python venv inside mcp/qdrant/:
::        python -m venv C:\Users\<YOUR_USERNAME>\.codex\mcp\qdrant
::   2. Install the server into that venv:
::        C:\Users\<YOUR_USERNAME>\.codex\mcp\qdrant\Scripts\pip install mcp-server-qdrant
::   3. Place this file at: mcp/qdrant/run-qdrant-mcp.cmd
::
:: No hardcoded paths — %~dp0 resolves to the directory of this script.
:: ─────────────────────────────────────────────────────────────────────────────
setlocal

set "QDRANT_URL=http://127.0.0.1:6333"
set "COLLECTION_NAME=qdrant-memory"
set "EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2"
set "FASTMCP_LOG_LEVEL=INFO"
set "PYTHONIOENCODING=utf-8"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "FASTEMBED_CACHE_PATH=%~dp0fastembed-cache"

if not exist "%FASTEMBED_CACHE_PATH%" mkdir "%FASTEMBED_CACHE_PATH%"

"%~dp0Scripts\mcp-server-qdrant.exe" %*

endlocal
