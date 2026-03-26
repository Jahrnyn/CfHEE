from __future__ import annotations

from dataclasses import dataclass
import re

from cfhee_backend.retrieval.models import RetrievedChunkMatch


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_\-]{1,}")
IDENTIFIER_PATTERN = re.compile(r"\b[A-Z]{2,}[A-Z0-9_]*-\d+\b")
STOPWORDS = {
    "a",
    "an",
    "and",
    "az",
    "a",
    "the",
    "this",
    "that",
    "with",
    "from",
    "into",
    "your",
    "what",
    "which",
    "when",
    "where",
    "melyik",
    "mi",
    "mit",
    "hogyan",
    "hol",
    "mikor",
    "miert",
    "vagy",
    "es",
}


@dataclass(slots=True)
class RescoredChunk:
    match: RetrievedChunkMatch
    lexical_score: float
    final_score: float


def rescore_retrieved_chunks(query_text: str, matches: list[RetrievedChunkMatch], top_k: int) -> list[RetrievedChunkMatch]:
    if len(matches) <= 1:
        return _attach_scores(matches)

    query_tokens = _query_tokens(query_text)
    identifiers = _exact_identifiers(query_text)
    rescored: list[RescoredChunk] = []

    for match in matches:
        vector_score = match.vector_score or 0.0
        lexical_score = _lexical_score(match, query_tokens, identifiers)
        rescored.append(
            RescoredChunk(
                match=match,
                lexical_score=lexical_score,
                final_score=vector_score + lexical_score,
            )
        )

    ordered = sorted(
        rescored,
        key=lambda item: (
            -item.final_score,
            item.match.distance is None,
            item.match.distance if item.match.distance is not None else float("inf"),
            item.match.document_id,
            item.match.chunk_index,
            item.match.chunk_id,
        ),
    )

    reranked: list[RetrievedChunkMatch] = []
    for rank, item in enumerate(ordered[:top_k], start=1):
        reranked.append(
            item.match.model_copy(
                update={
                    "rank": rank,
                    "lexical_score": round(item.lexical_score, 4),
                    "final_score": round(item.final_score, 4),
                }
            )
        )

    return reranked


def _attach_scores(matches: list[RetrievedChunkMatch]) -> list[RetrievedChunkMatch]:
    reranked: list[RetrievedChunkMatch] = []
    for rank, match in enumerate(matches, start=1):
        reranked.append(
            match.model_copy(
                update={
                    "rank": rank,
                    "lexical_score": 0.0,
                    "final_score": round(match.vector_score or 0.0, 4),
                }
            )
        )
    return reranked


def _lexical_score(
    match: RetrievedChunkMatch,
    query_tokens: list[str],
    identifiers: list[str],
) -> float:
    title_text = (match.document.title or "").lower()
    chunk_text = match.text.lower()
    score = 0.0

    for identifier in identifiers:
        lowered_identifier = identifier.lower()
        if lowered_identifier in title_text:
            score += 0.35
        if lowered_identifier in chunk_text:
            score += 0.3

    for token in query_tokens:
        if token in STOPWORDS:
            continue

        title_hit = _contains_whole_term(title_text, token)
        chunk_hit = _contains_whole_term(chunk_text, token)
        if title_hit:
            score += 0.12
        if chunk_hit:
            score += 0.05

    return min(score, 0.7)


def _query_tokens(query_text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(query_text) if len(token) >= 3]


def _exact_identifiers(query_text: str) -> list[str]:
    identifiers = IDENTIFIER_PATTERN.findall(query_text.upper())
    return list(dict.fromkeys(identifiers))


def _contains_whole_term(text: str, term: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", text) is not None
