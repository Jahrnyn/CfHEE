from __future__ import annotations

import re

from cfhee_backend.answers.base import GroundedAnswerInput, GroundedAnswerProvider, GroundedAnswerResult


SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+|\n+")
TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


class DeterministicLocalAnswerProvider(GroundedAnswerProvider):
    provider_name = "deterministic-local"

    def is_available(self) -> tuple[bool, str | None]:
        return True, None

    def generate_answer(self, answer_input: GroundedAnswerInput) -> GroundedAnswerResult:
        snippets = self._select_supporting_snippets(answer_input)
        if not snippets:
            return GroundedAnswerResult(
                provider=self.provider_name,
                answer_text=None,
                message="Not enough evidence in retrieved context to produce a grounded answer.",
            )

        answer_text = "Based on the retrieved context, " + " ".join(snippets)
        return GroundedAnswerResult(
            provider=self.provider_name,
            answer_text=self._truncate(answer_text, limit=360),
        )

    def _select_supporting_snippets(self, answer_input: GroundedAnswerInput) -> list[str]:
        query_tokens = set(self._tokenize(answer_input.query_text))
        candidates: list[tuple[int, int, str]] = []

        for citation in answer_input.citations[:3]:
            sentences = [segment.strip() for segment in SENTENCE_SPLIT_PATTERN.split(citation.text) if segment.strip()]
            if not sentences and citation.text.strip():
                sentences = [citation.text.strip()]

            for sentence_index, sentence in enumerate(sentences):
                score = self._score_sentence(sentence, query_tokens)
                candidates.append((score, -sentence_index, sentence))

        if not candidates:
            return []

        ordered = sorted(candidates, key=lambda item: (-item[0], item[1], item[2]))
        snippets: list[str] = []

        for _, _, sentence in ordered:
            normalized = self._truncate(sentence, limit=180)
            if normalized not in snippets:
                snippets.append(normalized)
            if len(snippets) == 2:
                break

        return snippets

    def _score_sentence(self, sentence: str, query_tokens: set[str]) -> int:
        sentence_tokens = set(self._tokenize(sentence))
        if not sentence_tokens:
            return 0

        overlap = len(sentence_tokens & query_tokens)
        return overlap if overlap > 0 else 1

    def _tokenize(self, value: str) -> list[str]:
        return [token.lower() for token in TOKEN_PATTERN.findall(value) if len(token) > 2]

    def _truncate(self, value: str, limit: int) -> str:
        if len(value) <= limit:
            return value

        return value[: limit - 3].rstrip() + "..."
