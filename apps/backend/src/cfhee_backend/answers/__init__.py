import os

from cfhee_backend.answers.base import GroundedAnswerInput, GroundedAnswerProvider, GroundedAnswerResult
from cfhee_backend.answers.deterministic_provider import DeterministicLocalAnswerProvider
from cfhee_backend.answers.ollama_provider import OllamaGroundedAnswerProvider

_deterministic_provider = DeterministicLocalAnswerProvider()


def get_ollama_provider() -> OllamaGroundedAnswerProvider:
    return OllamaGroundedAnswerProvider()

def get_answer_provider() -> tuple[str, GroundedAnswerProvider, bool, str | None]:
    requested_provider = os.getenv("ANSWER_PROVIDER", "auto").strip().lower() or "auto"

    if requested_provider == "deterministic":
        return requested_provider, _deterministic_provider, False, None

    if requested_provider not in {"auto", "ollama"}:
        return (
            requested_provider,
            _deterministic_provider,
            True,
            f"Unknown ANSWER_PROVIDER '{requested_provider}'. Falling back to deterministic provider.",
        )

    ollama_provider = get_ollama_provider()
    is_available, reason = ollama_provider.is_available()
    if is_available:
        return requested_provider, ollama_provider, False, None

    return (
        requested_provider,
        _deterministic_provider,
        True,
        reason or "Ollama is unavailable. Falling back to deterministic provider.",
    )


__all__ = [
    "GroundedAnswerInput",
    "GroundedAnswerProvider",
    "GroundedAnswerResult",
    "DeterministicLocalAnswerProvider",
    "OllamaGroundedAnswerProvider",
    "get_ollama_provider",
    "get_answer_provider",
]
