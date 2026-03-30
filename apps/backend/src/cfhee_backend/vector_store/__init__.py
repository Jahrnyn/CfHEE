from __future__ import annotations

from cfhee_backend.vector_store.chroma_adapter import ChromaVectorStore

_vector_store: ChromaVectorStore | None = None


def get_vector_store() -> ChromaVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore()
    return _vector_store


def reset_vector_store() -> None:
    global _vector_store
    _vector_store = None
