#!/usr/bin/env bash
# run-semantic-qdrant-stdio.sh — WSL/Linux launcher for the semantic adapter (stdio)
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6333}"
export COLLECTION_PREFIX="${COLLECTION_PREFIX:-semantic-}"
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-qwen3-embedding:0.6b}"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
export QDRANT_SEARCH_LIMIT="${QDRANT_SEARCH_LIMIT:-8}"
export SEMANTIC_QDRANT_TRANSPORT="stdio"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"

exec "$SCRIPT_DIR/../qdrant/bin/python" "$SCRIPT_DIR/semantic_qdrant_http.py"
