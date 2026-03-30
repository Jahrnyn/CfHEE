from __future__ import annotations

import json
import os
from urllib import error, request

from cfhee_backend.embeddings.base import EmbeddingProviderError, EmbeddingService


DEFAULT_OLLAMA_EMBEDDING_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_EMBEDDING_MODEL = "bge-m3"


class OllamaEmbeddingService(EmbeddingService):
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.base_url = (
            base_url
            or os.getenv("EMBEDDING_OLLAMA_BASE_URL")
            or os.getenv("OLLAMA_BASE_URL")
            or DEFAULT_OLLAMA_EMBEDDING_BASE_URL
        ).rstrip("/")
        self.model = (
            model
            or os.getenv("EMBEDDING_MODEL")
            or DEFAULT_OLLAMA_EMBEDDING_MODEL
        )
        self.timeout_seconds = timeout_seconds or int(os.getenv("EMBEDDING_OLLAMA_TIMEOUT_SECONDS", "60"))

    def describe(self) -> dict[str, str]:
        return {
            "provider": "ollama",
            "base_url": self.base_url,
            "model": self.model,
        }

    def is_available(self) -> tuple[bool, str | None]:
        try:
            response = self._request_json("GET", "/api/tags")
        except EmbeddingProviderError as exc:
            return False, str(exc)

        models = response.get("models", [])
        if not any(model.get("name") == self.model for model in models if isinstance(model, dict)):
            return False, f"Ollama embedding model '{self.model}' was not found locally."

        return True, None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self._request_json(
            "POST",
            "/api/embed",
            {
                "model": self.model,
                "input": texts,
                "truncate": True,
            },
        )
        embeddings = response.get("embeddings")
        if not isinstance(embeddings, list):
            raise EmbeddingProviderError("Ollama embedding response did not include an 'embeddings' array.")

        normalized_embeddings: list[list[float]] = []
        for embedding in embeddings:
            if not isinstance(embedding, list) or not all(isinstance(value, (int, float)) for value in embedding):
                raise EmbeddingProviderError("Ollama embedding response included an invalid embedding vector.")
            normalized_embeddings.append([float(value) for value in embedding])

        if len(normalized_embeddings) != len(texts):
            raise EmbeddingProviderError(
                f"Ollama returned {len(normalized_embeddings)} embeddings for {len(texts)} input text(s)."
            )

        return normalized_embeddings

    def _request_json(self, method: str, path: str, payload: dict[str, object] | None = None) -> dict[str, object]:
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace").strip()
            if response_body:
                raise EmbeddingProviderError(
                    f"Ollama embedding request failed with HTTP {exc.code}: {response_body}"
                ) from exc
            raise EmbeddingProviderError(f"Ollama embedding request failed with HTTP {exc.code}.") from exc
        except error.URLError as exc:
            raise EmbeddingProviderError(f"Ollama is not reachable at {self.base_url}.") from exc
        except json.JSONDecodeError as exc:
            raise EmbeddingProviderError("Ollama returned invalid JSON for embeddings.") from exc
