"""
repo-index.py — Generic semantic indexer for any repo into Qdrant.

Usage:
    python repo-index.py [--repo <path>] [--collection <name>] [--subdir <subdir>]
                         [--watch] [--exts .dart,.py,.ts] [--batch <n>]

All options can also be set via environment variables:
    SEMANTIC_REPO_PATH      Path to the repo root (required if not --repo)
    SEMANTIC_SOURCE_SUBDIR  Subdirectory to index within the repo (default: lib)
    COLLECTION_NAME         Qdrant collection name (default: semantic-<repo-name>)
    SEMANTIC_INDEX_BATCH_SIZE
    SEMANTIC_CHUNK_LINES
    SEMANTIC_CHUNK_OVERLAP
    SEMANTIC_FILE_EXTS      Comma-separated extensions (default: .dart)

WATCH MODE (--watch):
    Monitors the repo for file changes and incrementally updates Qdrant.
    Requires: pip install watchdog
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Bootstrap: add semantic/ to sys.path so we can import the adapter helpers
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

import semantic_qdrant_http as semantic  # noqa: E402  (local import after path setup)
from mcp_server_qdrant.settings import METADATA_PATH  # noqa: E402
from qdrant_client import models  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("repo-index")

# ---------------------------------------------------------------------------
# CLI / env config
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Index a repo into Qdrant for semantic search.")
    p.add_argument("--repo", default=os.environ.get("SEMANTIC_REPO_PATH", ""),
                   help="Absolute path to the repo root.")
    p.add_argument("--subdir", default=os.environ.get("SEMANTIC_SOURCE_SUBDIR", ""),
                   help="Subdirectory inside the repo to index (e.g. lib, src). Empty = whole repo.")
    p.add_argument("--collection", default=os.environ.get("COLLECTION_NAME", ""),
                   help="Qdrant collection name. Defaults to semantic-<repo-name>.")
    p.add_argument("--batch", type=int,
                   default=int(os.environ.get("SEMANTIC_INDEX_BATCH_SIZE", "16")),
                   help="Embedding batch size (default: 16).")
    p.add_argument("--chunk-lines", type=int,
                   default=int(os.environ.get("SEMANTIC_CHUNK_LINES", "40")),
                   help="Lines per chunk (default: 40).")
    p.add_argument("--chunk-overlap", type=int,
                   default=int(os.environ.get("SEMANTIC_CHUNK_OVERLAP", "10")),
                   help="Overlapping lines between chunks (default: 10).")
    p.add_argument("--exts", default=os.environ.get("SEMANTIC_FILE_EXTS", ".dart"),
                   help="Comma-separated file extensions to index (default: .dart).")
    p.add_argument("--watch", action="store_true",
                   help="Watch for file changes and re-index incrementally.")
    return p.parse_args()


ARGS = _parse_args()

REPO_PATH = Path(ARGS.repo) if ARGS.repo else None
SOURCE_SUBDIR = ARGS.subdir
COLLECTION_NAME = ARGS.collection
BATCH_SIZE = ARGS.batch
CHUNK_LINES = ARGS.chunk_lines
CHUNK_OVERLAP = ARGS.chunk_overlap
INCLUDE_EXTENSIONS = {ext.strip() for ext in ARGS.exts.split(",") if ext.strip()}
WATCH_MODE = ARGS.watch

SKIP_DIR_NAMES = {
    ".git", ".dart_tool", ".idea", ".vscode",
    "build", "dist", "out", "coverage",
    "node_modules", "android", "ios", "linux", "macos", "windows", "web",
    "__pycache__", ".mypy_cache", ".pytest_cache",
}

DOC_FILE_NAMES = {
    "readme.md", "changelog.md", "contributing.md",
    "final_summary.md", "deploy_quick_start.md", "agents.md", "claude.md",
}

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class ChunkRecord:
    chunk_id: str
    content: str
    metadata: dict[str, object]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def detect_language(path: Path) -> str:
    suffix = path.suffix.lower()
    mapping = {".dart": "dart", ".py": "python", ".ts": "typescript",
               ".js": "javascript", ".go": "go", ".rs": "rust",
               ".yaml": "yaml", ".yml": "yaml", ".json": "json", ".md": "markdown"}
    return mapping.get(suffix, suffix.lstrip(".") or "text")


def detect_kind(path: Path) -> str:
    if path.suffix.lower() == ".md" or path.name.lower() in DOC_FILE_NAMES:
        return "doc"
    if path.suffix.lower() in {".yaml", ".yml", ".json"}:
        return "config"
    return "code"


def should_skip_dir(path: Path) -> bool:
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def iter_candidate_files(repo_path: Path, subdir: str) -> Iterable[Path]:
    source_root = repo_path / subdir if subdir else repo_path
    for path in source_root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_dir(path.relative_to(repo_path)):
            continue
        if path.suffix.lower() not in INCLUDE_EXTENSIONS:
            continue
        yield path


def build_chunk_id(relative_path: str, chunk_index: int, content: str) -> str:
    digest = hashlib.sha256(f"{relative_path}:{chunk_index}:{content}".encode()).hexdigest()
    return str(uuid.uuid5(uuid.NAMESPACE_URL, digest))


def chunk_file(path: Path, repo_path: Path) -> list[ChunkRecord]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    lines = text.splitlines()
    if not lines:
        return []

    relative_path = path.relative_to(repo_path).as_posix()
    language = detect_language(path)
    kind = detect_kind(path)
    repo_name = repo_path.name
    indexed_at = datetime.now(timezone.utc).isoformat()

    chunks: list[ChunkRecord] = []
    start = 0
    chunk_index = 0
    step = max(1, CHUNK_LINES - CHUNK_OVERLAP)

    while start < len(lines):
        end = min(len(lines), start + CHUNK_LINES)
        content = "\n".join(lines[start:end]).strip()
        if content:
            metadata: dict[str, object] = {
                "repo": repo_name,
                "repo_path": str(repo_path).replace("\\", "/"),
                "path": relative_path,
                "language": language,
                "kind": kind,
                "chunk_index": chunk_index,
                "start_line": start + 1,
                "end_line": end,
                "indexed_at": indexed_at,
                "source": "repo-index-auto",
                # Cross-file relationship hints stored in metadata
                # so Codex can open the real file and inspect neighbors.
                # Populated by build_import_hints() below.
                "imports": [],
            }
            chunks.append(ChunkRecord(
                chunk_id=build_chunk_id(relative_path, chunk_index, content),
                content=content,
                metadata=metadata,
            ))
        if end >= len(lines):
            break
        start += step
        chunk_index += 1

    # Enrich first chunk with import hints for cross-file tracing
    if chunks:
        chunks[0].metadata["imports"] = build_import_hints(text, language)

    return chunks


def build_import_hints(source: str, language: str) -> list[str]:
    """
    Extract imported file references from source so Codex can trace
    cross-file relationships after receiving a search shortlist.

    Returns a list of import strings (not resolved paths — the agent
    opens the real file and inspects them with view_file / grep_search).
    """
    import re
    hints: list[str] = []

    if language == "dart":
        # import 'package:...'; or import '../foo.dart';
        for m in re.findall(r"import\s+['\"]([^'\"]+)['\"]", source):
            hints.append(m)
    elif language in {"python"}:
        for m in re.findall(r"^\s*(?:from|import)\s+([\w.]+)", source, re.MULTILINE):
            hints.append(m)
    elif language in {"typescript", "javascript"}:
        for m in re.findall(r"from\s+['\"]([^'\"]+)['\"]", source):
            hints.append(m)
    elif language == "go":
        for m in re.findall(r"\"([^\"]+)\"", source):
            if "/" in m:
                hints.append(m)

    return hints[:20]  # cap to avoid giant payloads


# ---------------------------------------------------------------------------
# Qdrant operations
# ---------------------------------------------------------------------------

async def ensure_collection(collection_name: str) -> None:
    await semantic.ensure_embedding_ready()
    if await semantic.client.collection_exists(collection_name):
        return
    vname = semantic.embedding_provider.get_vector_name()
    vsize = semantic.embedding_provider.get_vector_size()
    await semantic.client.create_collection(
        collection_name=collection_name,
        vectors_config={vname: models.VectorParams(size=vsize, distance=models.Distance.COSINE)},
    )
    log.info("Created collection: %s", collection_name)


async def upsert_chunks(chunks: list[ChunkRecord], collection_name: str) -> None:
    if not chunks:
        return
    embeddings = await semantic.embedding_provider.embed_documents([c.content for c in chunks])
    vname = semantic.embedding_provider.get_vector_name()
    points = [
        models.PointStruct(
            id=c.chunk_id,
            vector={vname: emb},
            payload={"document": c.content, METADATA_PATH: c.metadata},
        )
        for c, emb in zip(chunks, embeddings, strict=True)
    ]
    await semantic.client.upsert(collection_name=collection_name, points=points)


async def delete_file_chunks(relative_path: str, collection_name: str) -> None:
    """Remove all chunks belonging to a specific file (used on file delete/modify)."""
    await semantic.client.delete(
        collection_name=collection_name,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key=f"{METADATA_PATH}.path",
                        match=models.MatchValue(value=relative_path),
                    )
                ]
            )
        ),
    )


# ---------------------------------------------------------------------------
# Full index
# ---------------------------------------------------------------------------

async def full_index(repo_path: Path, collection_name: str) -> None:
    await ensure_collection(collection_name)
    files = list(iter_candidate_files(repo_path, SOURCE_SUBDIR))
    all_chunks: list[ChunkRecord] = []
    for f in files:
        all_chunks.extend(chunk_file(f, repo_path))

    total = len(all_chunks)
    for start in range(0, total, BATCH_SIZE):
        batch = all_chunks[start : start + BATCH_SIZE]
        await upsert_chunks(batch, collection_name)
        log.info("Upserted %d/%d chunks", min(start + BATCH_SIZE, total), total)

    count = await semantic.client.count(collection_name=collection_name, exact=True)
    log.info(
        "Index complete — repo=%s  files=%d  chunks=%d  qdrant_points=%d",
        repo_path, len(files), total, count.count,
    )


# ---------------------------------------------------------------------------
# Watch mode (incremental)
# ---------------------------------------------------------------------------

async def _reindex_file(path: Path, repo_path: Path, collection_name: str) -> None:
    relative = path.relative_to(repo_path).as_posix()
    await delete_file_chunks(relative, collection_name)
    if path.exists():
        chunks = chunk_file(path, repo_path)
        await upsert_chunks(chunks, collection_name)
        log.info("Re-indexed %s  (%d chunks)", relative, len(chunks))
    else:
        log.info("Removed chunks for deleted file: %s", relative)


def _start_watch(repo_path: Path, collection_name: str) -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        log.error("watchdog not installed. Run: pip install watchdog")
        sys.exit(1)

    loop = asyncio.new_event_loop()

    class _Handler(FileSystemEventHandler):
        def _handle(self, src_path: str) -> None:
            path = Path(src_path)
            if path.suffix.lower() not in INCLUDE_EXTENSIONS:
                return
            if should_skip_dir(path.relative_to(repo_path)):
                return
            asyncio.run_coroutine_threadsafe(
                _reindex_file(path, repo_path, collection_name), loop
            )

        def on_modified(self, event):
            if not event.is_directory:
                self._handle(event.src_path)

        def on_created(self, event):
            if not event.is_directory:
                self._handle(event.src_path)

        def on_deleted(self, event):
            if not event.is_directory:
                self._handle(event.src_path)

    source_root = str(repo_path / SOURCE_SUBDIR if SOURCE_SUBDIR else repo_path)
    observer = Observer()
    observer.schedule(_Handler(), source_root, recursive=True)
    observer.start()
    log.info("Watching %s for changes (Ctrl-C to stop)...", source_root)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        observer.stop()
        loop.close()
    observer.join()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    if not REPO_PATH or not REPO_PATH.exists():
        log.error(
            "Repo path not set or does not exist. "
            "Pass --repo <path> or set SEMANTIC_REPO_PATH."
        )
        sys.exit(1)

    collection = COLLECTION_NAME or f"semantic-{REPO_PATH.name}"

    log.info("Repo:       %s", REPO_PATH)
    log.info("Subdir:     %s", SOURCE_SUBDIR or "(whole repo)")
    log.info("Collection: %s", collection)
    log.info("Extensions: %s", ", ".join(sorted(INCLUDE_EXTENSIONS)))

    await full_index(REPO_PATH, collection)

    if WATCH_MODE:
        _start_watch(REPO_PATH, collection)


if __name__ == "__main__":
    asyncio.run(main())
