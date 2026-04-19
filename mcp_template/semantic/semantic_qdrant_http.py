from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote
from urllib.request import Request, urlopen

from fastmcp import FastMCP
from qdrant_client import AsyncQdrantClient, models

from mcp_server_qdrant.embeddings.base import EmbeddingProvider
from mcp_server_qdrant.qdrant import QdrantConnector


QDRANT_URL = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "qwen3-embedding:0.6b")
SEARCH_LIMIT = int(os.environ.get("QDRANT_SEARCH_LIMIT", "8"))
HOST = os.environ.get("SEMANTIC_QDRANT_HOST", "127.0.0.1")
PORT = int(os.environ.get("SEMANTIC_QDRANT_PORT", "8010"))
MCP_PATH = os.environ.get("SEMANTIC_QDRANT_MCP_PATH", "/mcp")

# Multi-collection support — three modes (priority order):
#  1. SEARCH_COLLECTIONS env var (comma-separated) — explicit override
#  2. COLLECTION_NAME env var — legacy single-collection mode
#  3. Auto-discover — query Qdrant for all collections matching COLLECTION_PREFIX
#     (default prefix: "semantic-"). Works automatically across any project.
COLLECTION_PREFIX = os.environ.get("COLLECTION_PREFIX", "semantic-")
_SEARCH_COLLECTIONS_ENV = os.environ.get("SEARCH_COLLECTIONS", "")
_LEGACY_COLLECTION = os.environ.get("COLLECTION_NAME", "")

# Resolved at startup via _resolve_search_collections(); placeholder until then.
SEARCH_COLLECTIONS: list[str] = []


def _parse_explicit_collections() -> list[str] | None:
    """Return explicit collection list from env, or None if auto-discover should be used."""
    if _SEARCH_COLLECTIONS_ENV:
        return [c.strip() for c in _SEARCH_COLLECTIONS_ENV.split(",") if c.strip()]
    if _LEGACY_COLLECTION:
        return [_LEGACY_COLLECTION]
    return None


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._vector_size: int | None = None

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        return await self._embed(documents)

    async def embed_query(self, query: str) -> list[float]:
        # Qwen3-embedding instruction prefix for code-search task
        prefixed = (
            "Instruct: Given a code search query, retrieve relevant source code\n"
            f"Query: {query}"
        )
        embeddings = await self._embed([prefixed])
        return embeddings[0]

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        payload = json.dumps({"model": self.model_name, "input": texts}).encode("utf-8")

        def send_request() -> dict[str, Any]:
            request = Request(
                url=f"{OLLAMA_URL}/api/embed",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))

        response_payload = await asyncio.to_thread(send_request)
        embeddings = response_payload.get("embeddings")
        if not embeddings:
            raise ValueError(f"Ollama returned no embeddings for model '{self.model_name}'")
        if self._vector_size is None:
            self._vector_size = len(embeddings[0])
        return embeddings

    def get_vector_name(self) -> str:
        safe_name = self.model_name.replace(":", "-").replace("/", "-").lower()
        return f"ollama-{safe_name}"

    def get_vector_size(self) -> int:
        if self._vector_size is None:
            raise RuntimeError("Vector size is unknown. Call initialize_vector_size() first.")
        return self._vector_size

    async def initialize_vector_size(self) -> int:
        if self._vector_size is None:
            await self.embed_query("vector size probe")
        return self.get_vector_size()


client = AsyncQdrantClient(location=QDRANT_URL, api_key=os.environ.get("QDRANT_API_KEY"))
embedding_provider = OllamaEmbeddingProvider(EMBEDDING_MODEL)

# Build one connector per collection — keyed by collection name
_connectors: dict[str, QdrantConnector] = {}
_collections_resolved = False


async def _resolve_search_collections() -> None:
    """Populate SEARCH_COLLECTIONS on first call.

    Priority:
      1. Explicit env var (SEARCH_COLLECTIONS / COLLECTION_NAME)
      2. Auto-discover: all Qdrant collections whose name starts with COLLECTION_PREFIX
    """
    global SEARCH_COLLECTIONS, _collections_resolved
    if _collections_resolved:
        return
    explicit = _parse_explicit_collections()
    if explicit:
        SEARCH_COLLECTIONS = explicit
    else:
        all_cols = await client.get_collections()
        SEARCH_COLLECTIONS = [
            c.name for c in all_cols.collections
            if c.name.startswith(COLLECTION_PREFIX)
        ]
    _collections_resolved = True


def get_connector(collection_name: str) -> QdrantConnector:
    if collection_name not in _connectors:
        _connectors[collection_name] = QdrantConnector(
            qdrant_url=QDRANT_URL,
            qdrant_api_key=os.environ.get("QDRANT_API_KEY"),
            collection_name=collection_name,
            embedding_provider=embedding_provider,
            qdrant_local_path=os.environ.get("QDRANT_LOCAL_PATH"),
            field_indexes={},
        )
    return _connectors[collection_name]


mcp = FastMCP(
    name="semantic-qdrant-http",
    instructions=(
        "Multi-repo semantic search. Collections are auto-discovered from Qdrant "
        f"(prefix='{COLLECTION_PREFIX}') or set via SEARCH_COLLECTIONS env var. "
        "Use semantic://search/{query} to search all active repos at once. "
        "Use semantic://search-repo/{repo}/{query} to search a specific repo. "
        "Use semantic://health to check readiness and see which collections are active. "
        "Use semantic://collection/{name} to inspect a specific collection."
    ),
)


@dataclass
class SearchResult:
    content: str
    metadata: dict[str, Any] | None
    collection: str
    score: float = 0.0


async def ensure_embedding_ready() -> int:
    await _resolve_search_collections()
    return await embedding_provider.initialize_vector_size()


def build_kind_filter(kinds: list[str] | None) -> models.Filter | None:
    if not kinds:
        return None
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.kind",
                match=models.MatchAny(any=kinds),
            )
        ]
    )


async def search_one_collection(
    collection_name: str,
    query: str,
    *,
    kinds: list[str] | None = None,
    limit: int,
) -> list[SearchResult]:
    """Search a single collection. Returns [] if collection doesn't exist."""
    try:
        connector = get_connector(collection_name)
        entries = await connector.search(
            query,
            collection_name=collection_name,
            limit=limit,
            query_filter=build_kind_filter(kinds),
        )
        return [
            SearchResult(
                content=entry.content,
                metadata=entry.metadata,
                collection=collection_name,
            )
            for entry in entries
        ]
    except Exception:
        return []


async def run_search(
    query: str,
    *,
    collections: list[str] | None = None,
    kinds: list[str] | None = None,
    per_collection_limit: int | None = None,
) -> dict[str, Any]:
    """Fan-out search across multiple collections, merge and return top results."""
    decoded_query = unquote(query).strip()
    await ensure_embedding_ready()

    target_collections = collections if collections else SEARCH_COLLECTIONS
    # Per-collection limit: fetch enough so merged top-N is useful
    per_limit = per_collection_limit or max(SEARCH_LIMIT, SEARCH_LIMIT // max(len(target_collections), 1) + 3)

    tasks = [
        search_one_collection(col, decoded_query, kinds=kinds, limit=per_limit)
        for col in target_collections
    ]
    results_per_collection = await asyncio.gather(*tasks)

    # Merge all results — already ordered by score within each collection
    merged: list[SearchResult] = []
    for col_results in results_per_collection:
        merged.extend(col_results)

    # Trim to global SEARCH_LIMIT
    final = merged[:SEARCH_LIMIT]

    return {
        "query": decoded_query,
        "searched_collections": target_collections,
        "embedding_model": EMBEDDING_MODEL,
        "kinds": kinds,
        "limit": SEARCH_LIMIT,
        "result_count": len(final),
        "results": [asdict(item) for item in final],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Resources ────────────────────────────────────────────────────────────────

@mcp.resource("semantic://health", name="semantic_health", mime_type="application/json")
async def semantic_health() -> str:
    await ensure_embedding_ready()
    all_collections = await client.get_collections()
    available_names = [item.name for item in all_collections.collections]

    collection_details = []
    for col in SEARCH_COLLECTIONS:
        exists = col in available_names
        points: int | None = None
        if exists:
            try:
                count_result = await client.count(collection_name=col, exact=True)
                points = int(count_result.count)
            except Exception:
                points = -1
        collection_details.append({"collection": col, "exists": exists, "points_count": points})

    payload = {
        "status": "ok",
        "transport": "streamable-http",
        "qdrant_url": QDRANT_URL,
        "ollama_url": OLLAMA_URL,
        "embedding_model": EMBEDDING_MODEL,
        "search_collections": SEARCH_COLLECTIONS,
        "collection_details": collection_details,
        "available_collections": available_names,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


@mcp.resource(
    "semantic://collection/{name}",
    name="semantic_collection_info",
    mime_type="application/json",
)
async def semantic_collection_info(name: str) -> str:
    decoded_name = unquote(name).strip()
    all_collections = await client.get_collections()
    available_names = [item.name for item in all_collections.collections]
    exists = decoded_name in available_names
    payload: dict[str, Any] = {
        "collection": decoded_name,
        "exists": exists,
        "available_collections": available_names,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if exists:
        count_result = await client.count(collection_name=decoded_name, exact=True)
        payload["points_count"] = int(count_result.count)
    return json.dumps(payload, ensure_ascii=False, indent=2)


@mcp.resource(
    "semantic://search/{query}",
    name="semantic_search",
    description=(
        "Run semantic search across ALL workspace repos "
        f"({', '.join(SEARCH_COLLECTIONS)}) and return merged results."
    ),
    mime_type="application/json",
)
async def semantic_search(query: str) -> str:
    return json.dumps(await run_search(query), ensure_ascii=False, indent=2)


@mcp.resource(
    "semantic://search-code/{query}",
    name="semantic_search_code",
    description="Search code and config chunks only, across ALL workspace repos.",
    mime_type="application/json",
)
async def semantic_search_code(query: str) -> str:
    return json.dumps(await run_search(query, kinds=["code", "config"]), ensure_ascii=False, indent=2)


@mcp.resource(
    "semantic://search-repo/{repo}/{query}",
    name="semantic_search_repo",
    description=(
        "Search within a specific repo collection. "
        "repo must be one of: health-system, iot-simulator, healthguard, healthguard-model-api."
    ),
    mime_type="application/json",
)
async def semantic_search_repo(repo: str, query: str) -> str:
    # Map short aliases to full collection names
    _alias_map = {
        "health-system": "semantic-health-system",
        "health_system": "semantic-health-system",
        "iot-simulator": "semantic-iot-simulator",
        "iot_simulator": "semantic-iot-simulator",
        "healthguard": "semantic-healthguard",
        "healthguard-model-api": "semantic-healthguard-model-api",
        "model-api": "semantic-healthguard-model-api",
    }
    decoded_repo = unquote(repo).strip().lower()
    collection = _alias_map.get(decoded_repo, f"semantic-{decoded_repo}")
    result = await run_search(query, collections=[collection])
    result["repo_alias"] = decoded_repo
    return json.dumps(result, ensure_ascii=False, indent=2)


def main() -> None:
    transport = os.environ.get("SEMANTIC_QDRANT_TRANSPORT", "streamable-http")
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http", host=HOST, port=PORT, path=MCP_PATH)


if __name__ == "__main__":
    main()
