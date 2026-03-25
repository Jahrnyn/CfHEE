from __future__ import annotations

import json
import os
import logging
from urllib import error, request

from cfhee_backend.answers.base import GroundedAnswerInput, GroundedAnswerProvider, GroundedAnswerResult
from cfhee_backend.answers.prompt_builder import build_grounded_answer_prompt


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:7b"
logger = logging.getLogger("uvicorn.error")


class OllamaGroundedAnswerProvider(GroundedAnswerProvider):
    provider_name = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        self.timeout_seconds = timeout_seconds or int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))

    def is_available(self) -> tuple[bool, str | None]:
        try:
            response = self._request_json("GET", "/api/tags")
        except RuntimeError as exc:
            return False, str(exc)

        models = response.get("models", [])
        if not any(model.get("name") == self.model for model in models if isinstance(model, dict)):
            return False, f"Ollama model '{self.model}' was not found locally."

        return True, None

    def generate_answer(self, answer_input: GroundedAnswerInput) -> GroundedAnswerResult:
        prompt = build_grounded_answer_prompt(answer_input)
        logger.info("Generating grounded answer with provider=%s prompt_version=%s", self.provider_name, prompt.version)
        response = self._request_json(
            "POST",
            "/api/generate",
            {
                "model": self.model,
                "prompt": prompt.text,
                "stream": False,
                "options": {
                    "temperature": 0,
                },
            },
        )
        answer_text = str(response.get("response", "")).strip()

        if not answer_text:
            return GroundedAnswerResult(
                provider=self.provider_name,
                answer_text=None,
                message="Ollama returned an empty answer.",
            )

        return GroundedAnswerResult(
            provider=self.provider_name,
            answer_text=self._truncate(answer_text, 420),
        )

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
        except error.URLError as exc:
            raise RuntimeError(f"Ollama is not reachable at {self.base_url}.") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned invalid JSON.") from exc

    def _truncate(self, value: str, limit: int) -> str:
        if len(value) <= limit:
            return value

        return value[: limit - 3].rstrip() + "..."
