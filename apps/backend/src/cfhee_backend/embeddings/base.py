from __future__ import annotations

from typing import Protocol


class EmbeddingProviderError(RuntimeError):
    """Raised when the configured embedding provider cannot serve embeddings."""


class EmbeddingService(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""

    def describe(self) -> dict[str, str]:
        """Return a small runtime summary for diagnostics and ops surfaces."""
