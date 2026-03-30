from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class VectorChunkRecord:
    chunk_id: int
    document_id: int
    chunk_index: int
    text: str
    embedding: list[float]
    workspace: str
    domain: str
    project: str | None
    client: str | None
    module: str | None
    source_type: str
    language: str | None


@dataclass(slots=True)
class VectorQuery:
    text: str
    embedding: list[float]
    workspace: str
    domain: str
    project: str | None = None
    client: str | None = None
    module: str | None = None
    top_k: int = 5


@dataclass(slots=True)
class VectorQueryMatch:
    chunk_id: int
    document_id: int
    chunk_index: int
    text: str
    distance: float | None


class VectorStore(Protocol):
    def index_chunks(self, chunks: list[VectorChunkRecord]) -> None:
        """Persist chunk vectors and metadata into the active vector index."""

    def delete_chunks(self, chunk_ids: list[int]) -> None:
        """Remove chunk vectors from the active vector index by stored chunk id."""

    def query_chunks(self, query: VectorQuery) -> list[VectorQueryMatch]:
        """Return scoped chunk matches for a query embedding."""
