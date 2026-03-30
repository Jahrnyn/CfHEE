from __future__ import annotations

import hashlib
import math
import re

from cfhee_backend.embeddings.base import EmbeddingService


TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


class HashEmbeddingService(EmbeddingService):
    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def describe(self) -> dict[str, str]:
        return {
            "provider": "hash",
            "dimensions": str(self.dimensions),
        }

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions

        for token in TOKEN_PATTERN.findall(text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]
