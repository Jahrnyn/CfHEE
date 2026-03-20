from __future__ import annotations

import logging

from cfhee_backend.answers import get_answer_provider
from cfhee_backend.answers.base import GroundedAnswerInput
from cfhee_backend.answers.models import AnswerQueryRequest, AnswerQueryResponse
from cfhee_backend.retrieval import query_retrieval

logger = logging.getLogger(__name__)


def query_answer(payload: AnswerQueryRequest) -> AnswerQueryResponse:
    retrieval_response = query_retrieval(payload)
    requested_provider, provider, fallback_used, fallback_message = get_answer_provider()

    if retrieval_response.empty:
        return AnswerQueryResponse(
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
        return AnswerQueryResponse(
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

    grounded = provider_result.answer_text is not None
    response_message = provider_result.message
    if fallback_message:
        response_message = f"{fallback_message} {response_message}".strip() if response_message else fallback_message

    return AnswerQueryResponse(
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
