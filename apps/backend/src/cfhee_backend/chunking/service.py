from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChunkDraft:
    chunk_index: int
    text: str
    char_count: int


def chunk_document(raw_text: str, max_chars: int = 1200) -> list[ChunkDraft]:
    blocks = [block.strip() for block in raw_text.split("\n\n")]
    paragraphs = [block for block in blocks if block]

    if not paragraphs:
        return []

    chunks: list[ChunkDraft] = []
    current_parts: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        separator_length = 2 if current_parts else 0
        next_length = current_length + separator_length + len(paragraph)

        if current_parts and next_length > max_chars:
            chunks.append(_build_chunk(len(chunks), current_parts))
            current_parts = [paragraph]
            current_length = len(paragraph)
            continue

        current_parts.append(paragraph)
        current_length = next_length

    if current_parts:
        chunks.append(_build_chunk(len(chunks), current_parts))

    return chunks


def _build_chunk(chunk_index: int, parts: list[str]) -> ChunkDraft:
    text = "\n\n".join(parts)
    return ChunkDraft(chunk_index=chunk_index, text=text, char_count=len(text))
