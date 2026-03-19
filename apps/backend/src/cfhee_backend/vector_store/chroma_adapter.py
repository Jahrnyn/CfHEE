from __future__ import annotations

import os
from pathlib import Path

import chromadb

from cfhee_backend.vector_store.base import VectorChunkRecord


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
