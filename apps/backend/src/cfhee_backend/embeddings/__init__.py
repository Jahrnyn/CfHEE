from __future__ import annotations

import os

from cfhee_backend.embeddings.base import EmbeddingProviderError, EmbeddingService
from cfhee_backend.embeddings.hash_embedding import HashEmbeddingService
from cfhee_backend.embeddings.ollama_embedding import OllamaEmbeddingService

_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = _create_embedding_service()
    return _embedding_service


def reset_embedding_service() -> None:
    global _embedding_service
    _embedding_service = None


def get_embedding_provider_name() -> str:
    return os.getenv("EMBEDDING_PROVIDER", "ollama").strip().lower() or "ollama"


def get_embedding_runtime_summary() -> dict[str, str]:
    summary = {"provider_selection": get_embedding_provider_name()}
    summary.update(get_embedding_service().describe())
    return summary


def _create_embedding_service() -> EmbeddingService:
    provider = get_embedding_provider_name()

    if provider == "ollama":
        return OllamaEmbeddingService()

    if provider == "hash":
        return HashEmbeddingService()

    raise EmbeddingProviderError(
        f"Unknown EMBEDDING_PROVIDER '{provider}'. Supported values are 'ollama' and 'hash'."
    )
