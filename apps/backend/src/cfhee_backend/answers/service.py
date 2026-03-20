from __future__ import annotations

import logging

from cfhee_backend.answers import get_answer_provider
from cfhee_backend.answers.base import GroundedAnswerInput
from cfhee_backend.answers.models import AnswerQueryRequest, AnswerQueryResponse
from cfhee_backend.retrieval import query_retrieval

logger = logging.getLogger(__name__)


def query_answer(payload: AnswerQueryRequest) -> AnswerQueryResponse:
    retrieval_response = query_retrieval(payload)

    if retrieval_response.empty:
        return AnswerQueryResponse(
            query_text=payload.query_text,
            active_scope=retrieval_response.active_scope,
            grounded=False,
            answer_text=None,
            message="Not enough evidence in retrieved context.",
            provider="deterministic-local",
            provider_error=None,
            retrieval_empty=True,
            citations=[],
        )

    provider = get_answer_provider()
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
            provider=provider_name,
            provider_error=str(exc),
            retrieval_empty=False,
            citations=retrieval_response.results,
        )

    grounded = provider_result.answer_text is not None
    return AnswerQueryResponse(
        query_text=payload.query_text,
        active_scope=retrieval_response.active_scope,
        grounded=grounded,
        answer_text=provider_result.answer_text,
        message=provider_result.message,
        provider=provider_result.provider,
        provider_error=None,
        retrieval_empty=False,
        citations=retrieval_response.results,
    )
