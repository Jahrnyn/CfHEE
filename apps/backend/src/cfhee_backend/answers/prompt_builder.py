from __future__ import annotations

from dataclasses import dataclass

from cfhee_backend.answers.base import GroundedAnswerInput
from cfhee_backend.answers.language import detect_answer_language
from cfhee_backend.retrieval.models import RetrievedChunkMatch


PROMPT_VERSION = "grounded-answer-v1"


@dataclass(slots=True)
class GroundedAnswerPrompt:
    version: str
    text: str


def build_grounded_answer_prompt(answer_input: GroundedAnswerInput) -> GroundedAnswerPrompt:
    answer_language = detect_answer_language(answer_input.query_text)
    sections = [
        _instruction_block(answer_language.response_instruction, answer_language.no_evidence_message),
        _query_block(answer_input),
        _scope_block(answer_input),
        _context_block(answer_input.citations),
        _response_contract_block(answer_language.no_evidence_message),
    ]
    return GroundedAnswerPrompt(
        version=PROMPT_VERSION,
        text="\n\n".join(section for section in sections if section.strip()),
    )


def _instruction_block(response_instruction: str, no_evidence_message: str) -> str:
    return "\n".join(
        [
            "You are a conservative grounded-answer assistant.",
            "Answer only from the retrieved context below.",
            "Use only the provided scope and chunk context.",
            response_instruction,
            "Keep the answer short, direct, and factual.",
            "Do not speculate or fill gaps from prior knowledge.",
            f"If the evidence is not enough, answer exactly: {no_evidence_message}",
            "Do not repeat raw chunk text unless it is necessary.",
            "Do not mention sources that are not included in the provided context.",
        ]
    )


def _query_block(answer_input: GroundedAnswerInput) -> str:
    return "\n".join(
        [
            "## Query",
            answer_input.query_text,
        ]
    )


def _scope_block(answer_input: GroundedAnswerInput) -> str:
    scope = answer_input.active_scope
    return "\n".join(
        [
            "## Active Scope",
            f"workspace={scope.workspace}",
            f"domain={scope.domain}",
            f"project={scope.project or '-'}",
            f"client={scope.client or '-'}",
            f"module={scope.module or '-'}",
            f"context_limit={answer_input.context_limit}",
            f"retrieval_top_k={answer_input.retrieval_top_k}",
        ]
    )


def _context_block(citations: list[RetrievedChunkMatch]) -> str:
    citation_blocks = [_format_citation_block(citation) for citation in citations]
    return "\n\n".join(["## Retrieved Context", *citation_blocks])


def _format_citation_block(citation: RetrievedChunkMatch) -> str:
    return "\n".join(
        [
            f"[Citation {citation.rank}]",
            f"document_id={citation.document_id}",
            f"chunk_id={citation.chunk_id}",
            f"chunk_index={citation.chunk_index}",
            f"title={citation.document.title}",
            f"source_type={citation.document.source_type}",
            f"source_ref={citation.document.source_ref or '-'}",
            f"scope={_format_scope_path(citation)}",
            "text:",
            citation.text.strip(),
        ]
    )


def _format_scope_path(citation: RetrievedChunkMatch) -> str:
    scope_parts = [citation.scope.workspace, citation.scope.domain]
    if citation.scope.project:
        scope_parts.append(citation.scope.project)
    if citation.scope.client:
        scope_parts.append(citation.scope.client)
    if citation.scope.module:
        scope_parts.append(citation.scope.module)
    return " / ".join(scope_parts)


def _response_contract_block(no_evidence_message: str) -> str:
    return "\n".join(
        [
            "## Response Rules",
            "- Answer in 1 to 3 short sentences.",
            "- Base every claim on the retrieved context.",
            "- Prefer synthesis over quotation.",
            f"- If the context does not support the answer, return exactly: {no_evidence_message}",
        ]
    )
