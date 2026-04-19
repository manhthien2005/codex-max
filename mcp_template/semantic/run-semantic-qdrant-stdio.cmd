@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: run-semantic-qdrant-stdio.cmd — Launches semantic adapter in stdio mode
:: This is the transport Codex uses (MCP stdio protocol).
::
:: SETUP:
::   1. Create a venv inside mcp/qdrant/ (shared venv for both qdrant + semantic):
::        python -m venv C:\Users\<YOUR_USERNAME>\.codex\mcp\qdrant
::   2. Install dependencies into that venv:
::        C:\Users\<YOUR_USERNAME>\.codex\mcp\qdrant\Scripts\pip install ^
::            fastmcp qdrant-client mcp-server-qdrant
::   3. Copy semantic_qdrant_http.py into mcp/semantic/
::   4. Place this file at: mcp/semantic/run-semantic-qdrant-stdio.cmd
::
:: Uses %~dp0 for relative resolution — no hardcoded user paths.
:: The venv lives at ../qdrant/ (shared with the upstream qdrant MCP server).
:: ─────────────────────────────────────────────────────────────────────────────
setlocal

set "QDRANT_URL=http://127.0.0.1:6333"
set "COLLECTION_PREFIX=semantic-"
set "EMBEDDING_MODEL=qwen3-embedding:0.6b"
set "OLLAMA_URL=http://127.0.0.1:11434"
set "QDRANT_SEARCH_LIMIT=8"
set "SEMANTIC_QDRANT_TRANSPORT=stdio"
set "PYTHONIOENCODING=utf-8"

"%~dp0..\qdrant\Scripts\python.exe" "%~dp0semantic_qdrant_http.py"

endlocal
