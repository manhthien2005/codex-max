#!/usr/bin/env bash
# run-qdrant-mcp.sh — WSL/Linux launcher for mcp-server-qdrant
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6333}"
export COLLECTION_NAME="${COLLECTION_NAME:-qdrant-memory}"
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2}"
export FASTMCP_LOG_LEVEL="${FASTMCP_LOG_LEVEL:-INFO}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
export HF_HUB_DISABLE_TELEMETRY=1
export FASTEMBED_CACHE_PATH="${FASTEMBED_CACHE_PATH:-$SCRIPT_DIR/fastembed-cache}"

mkdir -p "$FASTEMBED_CACHE_PATH"
exec "$SCRIPT_DIR/bin/mcp-server-qdrant" "$@"
