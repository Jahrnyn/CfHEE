from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel

from cfhee_backend.persistence.query_logs import QueryLogRow, list_query_logs

router = APIRouter(prefix="/query-logs", tags=["query-logs"])


class QueryLogResponse(BaseModel):
    id: int
    created_at: datetime
    query_text: str
    workspace: str
    domain: str
    project: str | None
    client: str | None
    module: str | None
    top_k: int | None
    result_count: int
    empty_result: bool
    retrieved_chunk_ids: list[int]
    retrieved_document_ids: list[int]
    selected_context_chunk_ids: list[int] | None
    dropped_context_chunk_ids: list[int] | None
    answer_text: str | None
    has_evidence: bool | None
    context_used_count: int | None
    answer_length: int | None
    grounded_flag: str | None
    provider_used: str
    fallback_used: bool


@router.get("", response_model=list[QueryLogResponse])
def list_query_logs_endpoint(limit: int = Query(default=20, ge=1, le=100)) -> list[QueryLogResponse]:
    rows = list_query_logs(limit=limit)
    return [QueryLogResponse.model_validate(_row_to_dict(row)) for row in rows]


def _row_to_dict(row: QueryLogRow) -> dict[str, object]:
    return {
        "id": row.id,
        "created_at": row.created_at,
        "query_text": row.query_text,
        "workspace": row.workspace,
        "domain": row.domain,
        "project": row.project,
        "client": row.client,
        "module": row.module,
        "top_k": row.top_k,
        "result_count": row.result_count,
        "empty_result": row.empty_result,
        "retrieved_chunk_ids": row.retrieved_chunk_ids,
        "retrieved_document_ids": row.retrieved_document_ids,
        "selected_context_chunk_ids": row.selected_context_chunk_ids,
        "dropped_context_chunk_ids": row.dropped_context_chunk_ids,
        "answer_text": row.answer_text,
        "has_evidence": row.has_evidence,
        "context_used_count": row.context_used_count,
        "answer_length": row.answer_length,
        "grounded_flag": row.grounded_flag,
        "provider_used": row.provider_used,
        "fallback_used": row.fallback_used,
    }
