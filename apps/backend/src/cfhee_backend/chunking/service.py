from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(slots=True)
class ChunkDraft:
    chunk_index: int
    text: str
    char_count: int


def chunk_document(raw_text: str, max_chars: int = 1200, source_type: str | None = None) -> list[ChunkDraft]:
    if source_type is not None and source_type.casefold() == "code_snippet":
        return _chunk_code_snippet(raw_text)

    blocks = [block.strip() for block in raw_text.split("\n\n")]
    paragraphs = [block for block in blocks if block]

    if not paragraphs:
        return []

    paragraph_units: list[str] = []
    for paragraph in paragraphs:
        paragraph_units.extend(_expand_paragraph(paragraph, max_chars=max_chars))

    chunks: list[ChunkDraft] = []
    current_parts: list[str] = []
    current_length = 0

    for paragraph in paragraph_units:
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


def _expand_paragraph(paragraph: str, max_chars: int) -> list[str]:
    if len(paragraph) <= max_chars:
        return [paragraph]

    sentences = _split_sentences(paragraph)
    if len(sentences) <= 1:
        return _split_hard(paragraph, max_chars=max_chars)

    sentence_chunks = _pack_units(sentences, max_chars=max_chars, separator=" ")
    if any(len(chunk) > max_chars for chunk in sentence_chunks):
        hard_chunks: list[str] = []
        for sentence_chunk in sentence_chunks:
            if len(sentence_chunk) <= max_chars:
                hard_chunks.append(sentence_chunk)
                continue
            hard_chunks.extend(_split_hard(sentence_chunk, max_chars=max_chars))
        return hard_chunks

    return sentence_chunks


def _split_sentences(paragraph: str) -> list[str]:
    matches = re.findall(r".+?(?:[.!?](?=\s|$)|$)", paragraph, flags=re.DOTALL)
    return [match.strip() for match in matches if match.strip()]


def _pack_units(units: list[str], max_chars: int, separator: str) -> list[str]:
    chunks: list[str] = []
    current_parts: list[str] = []
    current_length = 0

    for unit in units:
        separator_length = len(separator) if current_parts else 0
        next_length = current_length + separator_length + len(unit)

        if current_parts and next_length > max_chars:
            chunks.append(separator.join(current_parts))
            current_parts = [unit]
            current_length = len(unit)
            continue

        current_parts.append(unit)
        current_length = next_length

    if current_parts:
        chunks.append(separator.join(current_parts))

    return chunks


def _split_hard(text: str, max_chars: int) -> list[str]:
    return [text[index : index + max_chars].strip() for index in range(0, len(text), max_chars) if text[index : index + max_chars].strip()]


def _chunk_code_snippet(raw_text: str, lines_per_chunk: int = 40, overlap_lines: int = 10) -> list[ChunkDraft]:
    lines = raw_text.splitlines()
    if not lines:
        return []

    step = lines_per_chunk - overlap_lines
    chunks: list[ChunkDraft] = []

    for start in range(0, len(lines), step):
        window = lines[start : start + lines_per_chunk]
        if not window:
            break

        text = "\n".join(window)
        chunks.append(
            ChunkDraft(
                chunk_index=len(chunks),
                text=text,
                char_count=len(text),
            )
        )

        if start + lines_per_chunk >= len(lines):
            break

    return chunks
