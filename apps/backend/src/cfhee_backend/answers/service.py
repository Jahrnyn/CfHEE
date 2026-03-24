from __future__ import annotations

import logging

from cfhee_backend.answers import get_answer_provider
from cfhee_backend.answers.base import GroundedAnswerInput
from cfhee_backend.answers.models import AnswerQueryRequest, AnswerQueryResponse
from cfhee_backend.persistence.query_logs import QueryLogCreate, insert_query_log, update_query_log_answer
from cfhee_backend.retrieval.service import execute_retrieval

logger = logging.getLogger(__name__)


def query_answer(payload: AnswerQueryRequest) -> AnswerQueryResponse:
    retrieval_execution = execute_retrieval(payload)
    retrieval_response = retrieval_execution.response
    query_log_id = _safe_insert_answer_query_log(payload, retrieval_execution)
    requested_provider, provider, fallback_used, fallback_message = get_answer_provider()

    if retrieval_response.empty:
        response = AnswerQueryResponse(
            query_text=payload.query_text,
            active_scope=retrieval_response.active_scope,
            grounded=False,
            answer_text=None,
            message="Not enough evidence in retrieved context.",
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
        )
        return response

    provider_name = getattr(provider, "provider_name", provider.__class__.__name__)
    try:
        provider_result = provider.generate_answer(
            GroundedAnswerInput(
                query_text=payload.query_text,
                active_scope=retrieval_response.active_scope,
                citations=retrieval_response.results,
            )
        )
    except Exception as exc:
        logger.exception("Answer provider failed for scope=%s", retrieval_response.active_scope.model_dump())
        response = AnswerQueryResponse(
            query_text=payload.query_text,
            active_scope=retrieval_response.active_scope,
            grounded=False,
            answer_text=None,
            message="Answer provider failed to produce a grounded answer.",
            requested_provider=requested_provider,
            provider=provider_name,
            fallback_used=fallback_used,
            provider_error=str(exc),
            retrieval_empty=False,
            citations=retrieval_response.results,
        )
        _safe_update_query_log_answer(
            query_log_id=query_log_id,
            answer_text=response.answer_text,
            provider_used=response.provider,
            fallback_used=response.fallback_used,
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
        citations=retrieval_response.results,
    )
    _safe_update_query_log_answer(
        query_log_id=query_log_id,
        answer_text=response.answer_text,
        provider_used=response.provider,
        fallback_used=response.fallback_used,
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
                answer_text=None,
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
) -> None:
    if query_log_id is None:
        return

    try:
        update_query_log_answer(
            query_log_id=query_log_id,
            answer_text=answer_text,
            provider_used=provider_used,
            fallback_used=fallback_used,
        )
    except Exception as exc:
        logger.warning("Query log update failed for query_log_id=%s: %s", query_log_id, exc)
