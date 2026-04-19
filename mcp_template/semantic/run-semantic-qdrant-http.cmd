@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: run-semantic-qdrant-http.cmd — Launches semantic adapter in HTTP/SSE mode
:: Use this for manual testing or when you need the HTTP endpoint directly.
:: For Codex integration, use run-semantic-qdrant-stdio.cmd instead.
::
:: SETUP: same as run-semantic-qdrant-stdio.cmd
:: ─────────────────────────────────────────────────────────────────────────────
setlocal

set "QDRANT_URL=http://127.0.0.1:6333"
set "COLLECTION_PREFIX=semantic-"
set "EMBEDDING_MODEL=qwen3-embedding:0.6b"
set "OLLAMA_URL=http://127.0.0.1:11434"
set "QDRANT_SEARCH_LIMIT=8"
set "SEMANTIC_QDRANT_HOST=127.0.0.1"
set "SEMANTIC_QDRANT_PORT=8010"
set "SEMANTIC_QDRANT_MCP_PATH=/mcp"
set "PYTHONIOENCODING=utf-8"

"%~dp0..\qdrant\Scripts\python.exe" "%~dp0semantic_qdrant_http.py"

endlocal
