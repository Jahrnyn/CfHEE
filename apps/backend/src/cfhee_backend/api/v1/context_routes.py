from fastapi import APIRouter

from cfhee_backend.api.v1.models import (
    ContextBuildRequestV1,
    ContextBuildResponseV1,
    ContextChunkV1,
    ContextStatsV1,
    RetrievalDiagnosticsV1,
    ScopeRef,
)
from cfhee_backend.context_builder import build_context, format_context_text
from cfhee_backend.retrieval.models import RetrievalQueryRequest
from cfhee_backend.retrieval.service import execute_retrieval

router = APIRouter(tags=["api-v1-context"])


@router.post(
    "/context/build",
    response_model=ContextBuildResponseV1,
    response_model_exclude_none=True,
    tags=["context"],
)
def build_context_v1(payload: ContextBuildRequestV1) -> ContextBuildResponseV1:
    internal_payload = RetrievalQueryRequest(
        query_text=payload.query,
        workspace=payload.scope.workspace,
        domain=payload.scope.domain,
        project=payload.scope.project,
        client=payload.scope.client,
        module=payload.scope.module,
        top_k=payload.top_k,
    )
    execution = execute_retrieval(internal_payload)
    built_context = build_context(
        retrieved_chunks=execution.response.results,
        retrieval_top_k=payload.top_k,
        context_chunk_limit=payload.max_context_chunks,
    )
    context_text = format_context_text(built_context.chunks)

    diagnostics = None
    if payload.include_diagnostics:
        diagnostics = RetrievalDiagnosticsV1(
            candidate_count=execution.candidate_count,
            top_k_limit_hit=execution.top_k_limit_hit,
            reranking_applied=execution.reranking_applied,
            original_ranked_chunk_ids=execution.original_ranked_chunk_ids,
            reranked_chunk_ids=execution.reranked_chunk_ids,
        )

    return ContextBuildResponseV1(
        status="no_results" if execution.response.empty else "ok",
        query=execution.response.query_text,
        active_scope=ScopeRef.model_validate(execution.response.active_scope.model_dump()),
        context_text=context_text,
        selected_chunks=[
            ContextChunkV1(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                title=chunk.document.title,
                source_type=chunk.document.source_type,
                similarity_score=chunk.similarity_score,
                distance=chunk.distance,
                text=chunk.text,
            )
            for chunk in built_context.chunks
        ],
        selected_chunk_count=len(built_context.chunks),
        dropped_chunk_ids=[chunk.chunk_id for chunk in built_context.dropped_chunks],
        context_stats=ContextStatsV1(
            char_count=len(context_text),
            chunk_count=len(built_context.chunks),
        ),
        diagnostics=diagnostics,
    )
