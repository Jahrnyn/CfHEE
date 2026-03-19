from __future__ import annotations

import os
from pathlib import Path

import chromadb

from cfhee_backend.vector_store.base import VectorChunkRecord, VectorQuery, VectorQueryMatch


DEFAULT_COLLECTION_NAME = "document_chunks"


class ChromaVectorStore:
    def __init__(self, persist_directory: str | None = None) -> None:
        path = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            str(Path(__file__).resolve().parents[3] / "data" / "chroma"),
        )
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(name=DEFAULT_COLLECTION_NAME)

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

    def query_chunks(self, query: VectorQuery) -> list[VectorQueryMatch]:
        response = self._collection.query(
            query_embeddings=[query.embedding],
            n_results=query.limit,
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
