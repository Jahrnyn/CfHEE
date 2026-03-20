from __future__ import annotations

from pydantic import BaseModel

from cfhee_backend.retrieval.models import RetrievalQueryRequest, RetrievalScope, RetrievedChunkMatch


class AnswerQueryRequest(RetrievalQueryRequest):
    pass


class AnswerQueryResponse(BaseModel):
    query_text: str
    active_scope: RetrievalScope
    grounded: bool
    answer_text: str | None
    message: str | None
    provider: str
    provider_error: str | None
    retrieval_empty: bool
    citations: list[RetrievedChunkMatch]
