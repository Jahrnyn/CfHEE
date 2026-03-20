from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cfhee_backend.retrieval.models import RetrievalScope, RetrievedChunkMatch


@dataclass(slots=True)
class GroundedAnswerInput:
    query_text: str
    active_scope: RetrievalScope
    citations: list[RetrievedChunkMatch]


@dataclass(slots=True)
class GroundedAnswerResult:
    provider: str
    answer_text: str | None
    message: str | None = None


class GroundedAnswerProvider(Protocol):
    provider_name: str

    def is_available(self) -> tuple[bool, str | None]:
        """Return whether the provider is locally usable right now."""

    def generate_answer(self, answer_input: GroundedAnswerInput) -> GroundedAnswerResult:
        """Return a grounded answer built only from retrieved citations."""
