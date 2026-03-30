from __future__ import annotations

import os
import re
from pathlib import Path

import chromadb

from cfhee_backend.embeddings import get_embedding_runtime_summary
from cfhee_backend.vector_store.base import VectorChunkRecord, VectorQuery, VectorQueryMatch


DEFAULT_COLLECTION_NAME = "document_chunks"


def get_chroma_persist_directory() -> str:
    return os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        str(Path(__file__).resolve().parents[3] / "data" / "chroma"),
    )


def get_chroma_collection_name() -> str:
    configured_name = os.getenv("CHROMA_COLLECTION_NAME")
    if configured_name and configured_name.strip():
        return configured_name.strip()

    embedding_summary = get_embedding_runtime_summary()
    provider = _slugify_collection_part(embedding_summary["provider"])
    model = _slugify_collection_part(embedding_summary.get("model"))
    dimensions = _slugify_collection_part(embedding_summary.get("dimensions"))

    suffix_parts = [part for part in (provider, model, dimensions) if part]
    if not suffix_parts:
        return DEFAULT_COLLECTION_NAME

    return f"{DEFAULT_COLLECTION_NAME}__{'__'.join(suffix_parts)}"


class ChromaVectorStore:
    def __init__(self, persist_directory: str | None = None) -> None:
        path = persist_directory or get_chroma_persist_directory()
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(name=get_chroma_collection_name())

    def index_chunks(self, chunks: list[VectorChunkRecord]) -> None:
        if not chunks:
            return

        self._collection.upsert(
            ids=[str(chunk.chunk_id) for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=[chunk.embedding for chunk in chunks],
            metadatas=[
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "workspace": chunk.workspace,
                    "domain": chunk.domain,
                    "project": chunk.project or "",
                    "client": chunk.client or "",
                    "module": chunk.module or "",
                    "source_type": chunk.source_type,
                    "language": chunk.language or "",
                }
                for chunk in chunks
            ],
        )

    def delete_chunks(self, chunk_ids: list[int]) -> None:
        if not chunk_ids:
            return

        self._collection.delete(ids=[str(chunk_id) for chunk_id in chunk_ids])

    def query_chunks(self, query: VectorQuery) -> list[VectorQueryMatch]:
        response = self._collection.query(
            query_embeddings=[query.embedding],
            n_results=query.top_k,
            where=self._build_where(query),
            include=["documents", "metadatas", "distances"],
        )

        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]
        ids = response.get("ids", [[]])[0]

        matches: list[VectorQueryMatch] = []
        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            if metadata is None:
                continue

            matches.append(
                VectorQueryMatch(
                    chunk_id=int(metadata.get("chunk_id", chunk_id)),
                    document_id=int(metadata["document_id"]),
                    chunk_index=int(metadata["chunk_index"]),
                    text=document,
                    distance=float(distance) if distance is not None else None,
                )
            )

        return matches

    def _build_where(self, query: VectorQuery) -> dict[str, object]:
        clauses: list[dict[str, object]] = [
            {"workspace": {"$eq": query.workspace}},
            {"domain": {"$eq": query.domain}},
        ]

        if query.project:
            clauses.append({"project": {"$eq": query.project}})

        if query.client:
            clauses.append({"client": {"$eq": query.client}})

        if query.module:
            clauses.append({"module": {"$eq": query.module}})

        if len(clauses) == 1:
            return clauses[0]

        return {"$and": clauses}


def _slugify_collection_part(value: str | None) -> str:
    if value is None:
        return ""

    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized[:48]
