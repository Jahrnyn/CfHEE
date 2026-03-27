from __future__ import annotations

from dataclasses import dataclass

from cfhee_backend.retrieval.models import RetrievedChunkMatch


DEFAULT_CONTEXT_CHUNK_LIMIT = 4


@dataclass(slots=True)
class DroppedContextChunk:
    chunk_id: int
    reason: str


@dataclass(slots=True)
class BuiltContext:
    chunks: list[RetrievedChunkMatch]
    selected_chunk_ids: list[int]
    dropped_chunks: list[DroppedContextChunk]
    context_limit: int


def build_context(
    retrieved_chunks: list[RetrievedChunkMatch],
    retrieval_top_k: int,
    context_chunk_limit: int = DEFAULT_CONTEXT_CHUNK_LIMIT,
) -> BuiltContext:
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
    limit = min(retrieval_top_k, context_chunk_limit)

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

    return BuiltContext(
        chunks=selected_chunks,
        selected_chunk_ids=[chunk.chunk_id for chunk in selected_chunks],
        dropped_chunks=dropped_chunks,
        context_limit=limit,
    )


def format_context_text(chunks: list[RetrievedChunkMatch]) -> str:
    return "\n\n".join(_format_chunk_block(index + 1, chunk) for index, chunk in enumerate(chunks))


def _format_chunk_block(position: int, chunk: RetrievedChunkMatch) -> str:
    return "\n".join(
        [
            f"[Chunk {position}]",
            f"document_id={chunk.document_id}",
            f"chunk_id={chunk.chunk_id}",
            f"chunk_index={chunk.chunk_index}",
            f"title={chunk.document.title}",
            f"source_type={chunk.document.source_type}",
            f"source_ref={chunk.document.source_ref or '-'}",
            f"scope={_format_scope_path(chunk)}",
            "text:",
            chunk.text.strip(),
        ]
    )


def _format_scope_path(chunk: RetrievedChunkMatch) -> str:
    scope_parts = [chunk.scope.workspace, chunk.scope.domain]
    if chunk.scope.project:
        scope_parts.append(chunk.scope.project)
    if chunk.scope.client:
        scope_parts.append(chunk.scope.client)
    if chunk.scope.module:
        scope_parts.append(chunk.scope.module)
    return " / ".join(scope_parts)


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())
