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


class VectorStore(Protocol):
    def index_chunks(self, chunks: list[VectorChunkRecord]) -> None:
        """Persist chunk vectors and metadata into the active vector index."""
