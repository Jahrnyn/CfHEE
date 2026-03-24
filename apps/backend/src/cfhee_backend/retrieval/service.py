from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from cfhee_backend.embeddings import get_embedding_service
from cfhee_backend.persistence.database import get_connection
from cfhee_backend.persistence.query_logs import QueryLogCreate, insert_query_log
from cfhee_backend.retrieval.models import (
    RetrievalQueryRequest,
    RetrievalQueryResponse,
    RetrievalScope,
    RetrievedChunkMatch,
    RetrievedDocumentSummary,
)
from cfhee_backend.vector_store import get_vector_store
from cfhee_backend.vector_store.base import VectorQuery

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RetrievalExecution:
    response: RetrievalQueryResponse
    chunk_ids: list[int]
    document_ids: list[int]


def query_retrieval(payload: RetrievalQueryRequest) -> RetrievalQueryResponse:
    execution = execute_retrieval(payload)
    _safe_insert_query_log(payload=payload, execution=execution)
    return execution.response


def execute_retrieval(payload: RetrievalQueryRequest) -> RetrievalExecution:
    active_scope = RetrievalScope(
        workspace=payload.workspace,
        domain=payload.domain,
        project=payload.project,
        client=payload.client,
        module=payload.module,
    )
    logger.info(
        "Retrieval query text=%r scope=%s top_k=%s",
        payload.query_text,
        active_scope.model_dump(),
        payload.top_k,
    )

    embedding_service = get_embedding_service()
    query_embedding = embedding_service.embed_texts([payload.query_text])[0]
    vector_store = get_vector_store()
    vector_matches = vector_store.query_chunks(
        VectorQuery(
            text=payload.query_text,
            embedding=query_embedding,
            workspace=payload.workspace,
            domain=payload.domain,
            project=payload.project,
            client=payload.client,
            module=payload.module,
            top_k=payload.top_k,
        )
    )
    vector_matches = sorted(
        vector_matches,
        key=lambda match: (
            match.distance is None,
            match.distance if match.distance is not None else float("inf"),
            match.document_id,
            match.chunk_index,
            match.chunk_id,
        ),
    )

    rows_by_chunk_id = _load_chunk_rows([match.chunk_id for match in vector_matches])
    results: list[RetrievedChunkMatch] = []

    for index, match in enumerate(vector_matches, start=1):
        row = rows_by_chunk_id.get(match.chunk_id)
        if row is None:
            continue

        results.append(
            RetrievedChunkMatch(
                rank=len(results) + 1,
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                text=row["text"],
                char_count=row["char_count"],
                similarity_score=_calculate_similarity_score(match.distance),
                distance=match.distance,
                created_at=row["chunk_created_at"],
                document=RetrievedDocumentSummary(
                    id=row["document_id"],
                    title=row["title"],
                    source_type=row["source_type"],
                    language=row["language"],
                    source_ref=row["source_ref"],
                    created_at=row["document_created_at"],
                ),
                scope=RetrievalScope(
                    workspace=row["workspace"],
                    domain=row["domain"],
                    project=row["project"],
                    client=row["client"],
                    module=row["module"],
                ),
            )
        )

    logger.info(
        "Retrieval returned %s result(s) scope=%s",
        len(results),
        active_scope.model_dump(),
    )

    response = RetrievalQueryResponse(
        query_text=payload.query_text,
        active_scope=active_scope,
        top_k=payload.top_k,
        returned_results=len(results),
        empty=len(results) == 0,
        results=results,
    )
    return RetrievalExecution(
        response=response,
        chunk_ids=[result.chunk_id for result in results],
        document_ids=_unique_document_ids(results),
    )


def _load_chunk_rows(chunk_ids: list[int]) -> dict[int, dict[str, Any]]:
    if not chunk_ids:
        return {}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  ch.id AS chunk_id,
                  ch.document_id,
                  ch.chunk_index,
                  ch.text,
                  ch.char_count,
                  ch.created_at AS chunk_created_at,
                  d.title,
                  d.source_type,
                  d.language,
                  d.source_ref,
                  d.created_at AS document_created_at,
                  w.name AS workspace,
                  dm.name AS domain,
                  p.name AS project,
                  c.name AS client,
                  m.name AS module
                FROM chunks ch
                JOIN documents d ON d.id = ch.document_id
                JOIN workspaces w ON w.id = ch.workspace_id
                JOIN domains dm ON dm.id = ch.domain_id
                LEFT JOIN projects p ON p.id = ch.project_id
                LEFT JOIN clients c ON c.id = ch.client_id
                LEFT JOIN modules m ON m.id = ch.module_id
                WHERE ch.id = ANY(%(chunk_ids)s)
                """,
                {"chunk_ids": chunk_ids},
            )
            rows = cursor.fetchall()

    return {row["chunk_id"]: row for row in rows}


def _calculate_similarity_score(distance: float | None) -> float | None:
    if distance is None:
        return None

    if distance < 0:
        return 1.0

    return 1.0 / (1.0 + distance)


def _safe_insert_query_log(payload: RetrievalQueryRequest, execution: RetrievalExecution) -> None:
    try:
        insert_query_log(
            QueryLogCreate(
                query_text=payload.query_text,
                workspace=payload.workspace,
                domain=payload.domain,
                project=payload.project,
                client=payload.client,
                module=payload.module,
                top_k=payload.top_k,
                result_count=execution.response.returned_results,
                empty_result=execution.response.empty,
                retrieved_chunk_ids=execution.chunk_ids,
                retrieved_document_ids=execution.document_ids,
                answer_text=None,
                provider_used="retrieval-only",
                fallback_used=False,
            )
        )
    except Exception as exc:
        logger.warning("Query log insert failed for retrieval query %r: %s", payload.query_text, exc)


def _unique_document_ids(results: list[RetrievedChunkMatch]) -> list[int]:
    seen: set[int] = set()
    ordered_ids: list[int] = []

    for result in results:
        if result.document_id in seen:
            continue

        seen.add(result.document_id)
        ordered_ids.append(result.document_id)

    return ordered_ids
