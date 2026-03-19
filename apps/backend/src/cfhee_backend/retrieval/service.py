from __future__ import annotations

from typing import Any

from cfhee_backend.embeddings import get_embedding_service
from cfhee_backend.persistence.database import get_connection
from cfhee_backend.retrieval.models import (
    RetrievalQueryRequest,
    RetrievalQueryResponse,
    RetrievalScope,
    RetrievedChunkMatch,
    RetrievedDocumentSummary,
)
from cfhee_backend.vector_store import get_vector_store
from cfhee_backend.vector_store.base import VectorQuery


def query_retrieval(payload: RetrievalQueryRequest) -> RetrievalQueryResponse:
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
            limit=payload.limit,
        )
    )

    rows_by_chunk_id = _load_chunk_rows([match.chunk_id for match in vector_matches])
    results: list[RetrievedChunkMatch] = []

    for index, match in enumerate(vector_matches, start=1):
        row = rows_by_chunk_id.get(match.chunk_id)
        if row is None:
            continue

        results.append(
            RetrievedChunkMatch(
                rank=index,
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                text=row["text"],
                char_count=row["char_count"],
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

    return RetrievalQueryResponse(
        query_text=payload.query_text,
        active_scope=RetrievalScope(
            workspace=payload.workspace,
            domain=payload.domain,
            project=payload.project,
            client=payload.client,
            module=payload.module,
        ),
        results=results,
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
