from __future__ import annotations

import logging

from cfhee_backend.answers import get_answer_provider
from cfhee_backend.answers.base import GroundedAnswerInput
from cfhee_backend.answers.context_builder import build_answer_context
from cfhee_backend.answers.language import detect_answer_language
from cfhee_backend.answers.models import AnswerQueryRequest, AnswerQueryResponse
from cfhee_backend.evaluation import EvaluationResult, evaluate_answer_trace
from cfhee_backend.persistence.query_logs import (
    QueryLogCreate,
    insert_query_log,
    update_query_log_answer,
    update_query_log_evaluation,
)
from cfhee_backend.retrieval.service import execute_retrieval

logger = logging.getLogger(__name__)


def query_answer(payload: AnswerQueryRequest) -> AnswerQueryResponse:
    answer_language = detect_answer_language(payload.query_text)
    retrieval_execution = execute_retrieval(payload)
    retrieval_response = retrieval_execution.response
    query_log_id = _safe_insert_answer_query_log(payload, retrieval_execution)
    answer_context = build_answer_context(
        retrieved_chunks=retrieval_response.results,
        retrieval_top_k=payload.top_k,
    )
    logger.info(
        "Answer context selected=%s dropped=%s limit=%s scope=%s",
        answer_context.selected_chunk_ids,
        [{"chunk_id": item.chunk_id, "reason": item.reason} for item in answer_context.dropped_chunks],
        answer_context.context_limit,
        retrieval_response.active_scope.model_dump(),
    )
    requested_provider, provider, fallback_used, fallback_message = get_answer_provider()

    if retrieval_response.empty or not answer_context.chunks:
        response = AnswerQueryResponse(
            query_text=payload.query_text,
            active_scope=retrieval_response.active_scope,
            grounded=False,
            answer_text=None,
            message=answer_language.no_evidence_message,
            requested_provider=requested_provider,
            provider=getattr(provider, "provider_name", provider.__class__.__name__),
            fallback_used=fallback_used,
            provider_error=None,
            retrieval_empty=True,
            citations=[],
        )
        _safe_update_query_log_answer(
            query_log_id=query_log_id,
            answer_text=response.answer_text,
            provider_used=response.provider,
            fallback_used=response.fallback_used,
            selected_context_chunk_ids=answer_context.selected_chunk_ids,
            dropped_context_chunk_ids=[item.chunk_id for item in answer_context.dropped_chunks],
        )
        _safe_update_query_log_evaluation(
            query_log_id=query_log_id,
            evaluation=_build_evaluation_result(
                answer_text=response.answer_text,
                selected_context_chunk_ids=answer_context.selected_chunk_ids,
                result_count=retrieval_response.returned_results,
            ),
        )
        return response

    provider_name = getattr(provider, "provider_name", provider.__class__.__name__)
    try:
        provider_result = provider.generate_answer(
            GroundedAnswerInput(
                query_text=payload.query_text,
                active_scope=retrieval_response.active_scope,
                citations=answer_context.chunks,
                retrieval_top_k=payload.top_k,
                context_limit=answer_context.context_limit,
            )
        )
    except Exception as exc:
        logger.exception("Answer provider failed for scope=%s", retrieval_response.active_scope.model_dump())
        response = AnswerQueryResponse(
            query_text=payload.query_text,
            active_scope=retrieval_response.active_scope,
            grounded=False,
            answer_text=None,
            message=answer_language.provider_failure_message,
            requested_provider=requested_provider,
            provider=provider_name,
            fallback_used=fallback_used,
            provider_error=str(exc),
            retrieval_empty=False,
            citations=answer_context.chunks,
        )
        _safe_update_query_log_answer(
            query_log_id=query_log_id,
            answer_text=response.answer_text,
            provider_used=response.provider,
            fallback_used=response.fallback_used,
            selected_context_chunk_ids=answer_context.selected_chunk_ids,
            dropped_context_chunk_ids=[item.chunk_id for item in answer_context.dropped_chunks],
        )
        _safe_update_query_log_evaluation(
            query_log_id=query_log_id,
            evaluation=_build_evaluation_result(
                answer_text=response.answer_text,
                selected_context_chunk_ids=answer_context.selected_chunk_ids,
                result_count=retrieval_response.returned_results,
            ),
        )
        return response

    grounded = provider_result.answer_text is not None
    response_message = provider_result.message
    if fallback_message:
        response_message = f"{fallback_message} {response_message}".strip() if response_message else fallback_message

    response = AnswerQueryResponse(
        query_text=payload.query_text,
        active_scope=retrieval_response.active_scope,
        grounded=grounded,
        answer_text=provider_result.answer_text,
        message=response_message,
        requested_provider=requested_provider,
        provider=provider_result.provider,
        fallback_used=fallback_used,
        provider_error=None,
        retrieval_empty=False,
        citations=answer_context.chunks,
    )
    _safe_update_query_log_answer(
        query_log_id=query_log_id,
        answer_text=response.answer_text,
        provider_used=response.provider,
        fallback_used=response.fallback_used,
        selected_context_chunk_ids=answer_context.selected_chunk_ids,
        dropped_context_chunk_ids=[item.chunk_id for item in answer_context.dropped_chunks],
    )
    _safe_update_query_log_evaluation(
        query_log_id=query_log_id,
        evaluation=_build_evaluation_result(
            answer_text=response.answer_text,
            selected_context_chunk_ids=answer_context.selected_chunk_ids,
            result_count=retrieval_response.returned_results,
        ),
    )
    return response


def _safe_insert_answer_query_log(payload: AnswerQueryRequest, retrieval_execution) -> int | None:
    try:
        return insert_query_log(
            QueryLogCreate(
                query_text=payload.query_text,
                workspace=payload.workspace,
                domain=payload.domain,
                project=payload.project,
                client=payload.client,
                module=payload.module,
                top_k=payload.top_k,
                result_count=retrieval_execution.response.returned_results,
                empty_result=retrieval_execution.response.empty,
                retrieved_chunk_ids=retrieval_execution.chunk_ids,
                retrieved_document_ids=retrieval_execution.document_ids,
                selected_context_chunk_ids=None,
                dropped_context_chunk_ids=None,
                answer_text=None,
                has_evidence=None,
                context_used_count=None,
                answer_length=None,
                grounded_flag=None,
                candidate_count=retrieval_execution.candidate_count,
                top_k_limit_hit=retrieval_execution.top_k_limit_hit,
                returned_distance_values=retrieval_execution.returned_distance_values,
                returned_document_distribution=retrieval_execution.returned_document_distribution,
                provider_used="pending-answer",
                fallback_used=False,
            )
        )
    except Exception as exc:
        logger.warning("Query log insert failed for answer query %r: %s", payload.query_text, exc)
        return None


def _safe_update_query_log_answer(
    query_log_id: int | None,
    answer_text: str | None,
    provider_used: str,
    fallback_used: bool,
    selected_context_chunk_ids: list[int],
    dropped_context_chunk_ids: list[int],
) -> None:
    if query_log_id is None:
        return

    try:
        update_query_log_answer(
            query_log_id=query_log_id,
            answer_text=answer_text,
            provider_used=provider_used,
            fallback_used=fallback_used,
            selected_context_chunk_ids=selected_context_chunk_ids,
            dropped_context_chunk_ids=dropped_context_chunk_ids,
        )
    except Exception as exc:
        logger.warning("Query log update failed for query_log_id=%s: %s", query_log_id, exc)


def _build_evaluation_result(
    answer_text: str | None,
    selected_context_chunk_ids: list[int],
    result_count: int,
) -> EvaluationResult:
    return evaluate_answer_trace(
        answer_text=answer_text,
        selected_context_chunk_ids=selected_context_chunk_ids,
        result_count=result_count,
    )


def _safe_update_query_log_evaluation(
    query_log_id: int | None,
    evaluation: EvaluationResult,
) -> None:
    if query_log_id is None:
        return

    try:
        update_query_log_evaluation(
            query_log_id=query_log_id,
            has_evidence=evaluation.has_evidence,
            context_used_count=evaluation.context_used_count,
            answer_length=evaluation.answer_length,
            grounded_flag=evaluation.grounded_flag,
        )
    except Exception as exc:
        logger.warning("Query log evaluation update failed for query_log_id=%s: %s", query_log_id, exc)
