from fastapi import APIRouter, HTTPException

from cfhee_backend.api.v1.models import (
    RetrievalDiagnosticsV1,
    RetrievalQueryRequestV1,
    RetrievalQueryResponseV1,
    RetrievalResultV1,
    ScopeRef,
)
from cfhee_backend.embeddings.base import EmbeddingProviderError
from cfhee_backend.retrieval.models import RetrievalQueryRequest
from cfhee_backend.retrieval.service import _safe_insert_query_log, execute_retrieval

router = APIRouter(tags=["api-v1-retrieval"])


@router.post(
    "/retrieval/query",
    response_model=RetrievalQueryResponseV1,
    response_model_exclude_none=True,
    tags=["retrieval"],
)
def query_retrieval_v1(payload: RetrievalQueryRequestV1) -> RetrievalQueryResponseV1:
    internal_payload = RetrievalQueryRequest(
        query_text=payload.query,
        workspace=payload.scope.workspace,
        domain=payload.scope.domain,
        project=payload.scope.project,
        client=payload.scope.client,
        module=payload.scope.module,
        top_k=payload.top_k,
    )
    try:
        execution = execute_retrieval(internal_payload)
    except EmbeddingProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    _safe_insert_query_log(payload=internal_payload, execution=execution)

    results = [
        RetrievalResultV1(
            document_id=result.document_id,
            chunk_id=result.chunk_id,
            chunk_index=result.chunk_index,
            title=result.document.title,
            source_type=result.document.source_type,
            similarity_score=result.similarity_score,
            distance=result.distance,
            text=result.text if payload.include_chunks else None,
        )
        for result in execution.response.results
    ]
    diagnostics = None
    if payload.include_diagnostics:
        diagnostics = RetrievalDiagnosticsV1(
            candidate_count=execution.candidate_count,
            top_k_limit_hit=execution.top_k_limit_hit,
            reranking_applied=execution.reranking_applied,
            original_ranked_chunk_ids=execution.original_ranked_chunk_ids,
            reranked_chunk_ids=execution.reranked_chunk_ids,
        )

    return RetrievalQueryResponseV1(
        status="no_results" if execution.response.empty else "ok",
        query=execution.response.query_text,
        active_scope=ScopeRef.model_validate(execution.response.active_scope.model_dump()),
        results=results,
        result_count=execution.response.returned_results,
        diagnostics=diagnostics,
    )
