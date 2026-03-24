from __future__ import annotations

from dataclasses import dataclass

from cfhee_backend.retrieval.models import RetrievedChunkMatch


DEFAULT_ANSWER_CONTEXT_LIMIT = 4


@dataclass(slots=True)
class DroppedContextChunk:
    chunk_id: int
    reason: str


@dataclass(slots=True)
class AnswerContext:
    chunks: list[RetrievedChunkMatch]
    selected_chunk_ids: list[int]
    dropped_chunks: list[DroppedContextChunk]
    context_limit: int


def build_answer_context(
    retrieved_chunks: list[RetrievedChunkMatch],
    retrieval_top_k: int,
    answer_context_limit: int = DEFAULT_ANSWER_CONTEXT_LIMIT,
) -> AnswerContext:
    ordered_chunks = sorted(
        retrieved_chunks,
        key=lambda chunk: (
            chunk.distance is None,
            chunk.distance if chunk.distance is not None else float("inf"),
            chunk.document_id,
            chunk.chunk_index,
            chunk.chunk_id,
        ),
    )
    limit = min(retrieval_top_k, answer_context_limit)

    selected_chunks: list[RetrievedChunkMatch] = []
    selected_keys: set[tuple[int, int]] = set()
    selected_texts: set[str] = set()
    dropped_chunks: list[DroppedContextChunk] = []

    for chunk in ordered_chunks:
        metadata_key = (chunk.document_id, chunk.chunk_index)
        normalized_text = _normalize_text(chunk.text)

        if metadata_key in selected_keys:
            dropped_chunks.append(DroppedContextChunk(chunk_id=chunk.chunk_id, reason="duplicate-metadata"))
            continue

        if normalized_text in selected_texts:
            dropped_chunks.append(DroppedContextChunk(chunk_id=chunk.chunk_id, reason="duplicate-text"))
            continue

        if len(selected_chunks) >= limit:
            dropped_chunks.append(DroppedContextChunk(chunk_id=chunk.chunk_id, reason="context-limit"))
            continue

        selected_chunks.append(chunk)
        selected_keys.add(metadata_key)
        selected_texts.add(normalized_text)

    return AnswerContext(
        chunks=selected_chunks,
        selected_chunk_ids=[chunk.chunk_id for chunk in selected_chunks],
        dropped_chunks=dropped_chunks,
        context_limit=limit,
    )


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())
