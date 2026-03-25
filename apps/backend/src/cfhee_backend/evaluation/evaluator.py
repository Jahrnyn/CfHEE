from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EvaluationResult:
    has_evidence: bool
    context_used_count: int
    answer_length: int
    grounded_flag: str


def evaluate_answer_trace(
    answer_text: str | None,
    selected_context_chunk_ids: list[int] | None,
    result_count: int,
) -> EvaluationResult:
    selected_chunk_ids = selected_context_chunk_ids or []
    has_evidence = result_count > 0 and bool(selected_chunk_ids)
    context_used_count = len(selected_chunk_ids)
    answer_length = len(answer_text) if answer_text is not None else 0

    if result_count == 0:
        grounded_flag = "no-evidence"
    elif has_evidence:
        grounded_flag = "likely"
    else:
        grounded_flag = "unknown"

    return EvaluationResult(
        has_evidence=has_evidence,
        context_used_count=context_used_count,
        answer_length=answer_length,
        grounded_flag=grounded_flag,
    )
