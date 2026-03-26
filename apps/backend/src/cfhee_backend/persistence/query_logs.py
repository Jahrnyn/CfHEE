from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from psycopg.types.json import Jsonb

from cfhee_backend.persistence.database import get_connection


@dataclass(slots=True)
class QueryLogCreate:
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
    candidate_count: int | None
    top_k_limit_hit: bool | None
    returned_distance_values: list[float] | None
    returned_document_distribution: dict[str, int] | None
    original_ranked_chunk_ids: list[int] | None
    reranked_chunk_ids: list[int] | None
    reranking_applied: bool | None
    provider_used: str
    fallback_used: bool


@dataclass(slots=True)
class QueryLogRow:
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
    candidate_count: int | None
    top_k_limit_hit: bool | None
    returned_distance_values: list[float] | None
    returned_document_distribution: dict[str, int] | None
    original_ranked_chunk_ids: list[int] | None
    reranked_chunk_ids: list[int] | None
    reranking_applied: bool | None
    provider_used: str
    fallback_used: bool


def insert_query_log(entry: QueryLogCreate) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO query_logs (
                  query_text,
                  workspace,
                  domain,
                  project,
                  client,
                  module,
                  top_k,
                  result_count,
                  empty_result,
                  retrieved_chunk_ids,
                  retrieved_document_ids,
                  selected_context_chunk_ids,
                  dropped_context_chunk_ids,
                  answer_text,
                  has_evidence,
                  context_used_count,
                  answer_length,
                  grounded_flag,
                  candidate_count,
                  top_k_limit_hit,
                  returned_distance_values,
                  returned_document_distribution,
                  original_ranked_chunk_ids,
                  reranked_chunk_ids,
                  reranking_applied,
                  provider_used,
                  fallback_used
                )
                VALUES (
                  %(query_text)s,
                  %(workspace)s,
                  %(domain)s,
                  %(project)s,
                  %(client)s,
                  %(module)s,
                  %(top_k)s,
                  %(result_count)s,
                  %(empty_result)s,
                  %(retrieved_chunk_ids)s,
                  %(retrieved_document_ids)s,
                  %(selected_context_chunk_ids)s,
                  %(dropped_context_chunk_ids)s,
                  %(answer_text)s,
                  %(has_evidence)s,
                  %(context_used_count)s,
                  %(answer_length)s,
                  %(grounded_flag)s,
                  %(candidate_count)s,
                  %(top_k_limit_hit)s,
                  %(returned_distance_values)s,
                  %(returned_document_distribution)s,
                  %(original_ranked_chunk_ids)s,
                  %(reranked_chunk_ids)s,
                  %(reranking_applied)s,
                  %(provider_used)s,
                  %(fallback_used)s
                )
                RETURNING id
                """,
                {
                    "query_text": entry.query_text,
                    "workspace": entry.workspace,
                    "domain": entry.domain,
                    "project": entry.project,
                    "client": entry.client,
                    "module": entry.module,
                    "top_k": entry.top_k,
                    "result_count": entry.result_count,
                    "empty_result": entry.empty_result,
                    "retrieved_chunk_ids": Jsonb(entry.retrieved_chunk_ids),
                    "retrieved_document_ids": Jsonb(entry.retrieved_document_ids),
                    "selected_context_chunk_ids": Jsonb(entry.selected_context_chunk_ids)
                    if entry.selected_context_chunk_ids is not None
                    else None,
                    "dropped_context_chunk_ids": Jsonb(entry.dropped_context_chunk_ids)
                    if entry.dropped_context_chunk_ids is not None
                    else None,
                    "answer_text": entry.answer_text,
                    "has_evidence": entry.has_evidence,
                    "context_used_count": entry.context_used_count,
                    "answer_length": entry.answer_length,
                    "grounded_flag": entry.grounded_flag,
                    "candidate_count": entry.candidate_count,
                    "top_k_limit_hit": entry.top_k_limit_hit,
                    "returned_distance_values": Jsonb(entry.returned_distance_values)
                    if entry.returned_distance_values is not None
                    else None,
                    "returned_document_distribution": Jsonb(entry.returned_document_distribution)
                    if entry.returned_document_distribution is not None
                    else None,
                    "original_ranked_chunk_ids": Jsonb(entry.original_ranked_chunk_ids)
                    if entry.original_ranked_chunk_ids is not None
                    else None,
                    "reranked_chunk_ids": Jsonb(entry.reranked_chunk_ids)
                    if entry.reranked_chunk_ids is not None
                    else None,
                    "reranking_applied": entry.reranking_applied,
                    "provider_used": entry.provider_used,
                    "fallback_used": entry.fallback_used,
                },
            )
            row = cursor.fetchone()
        connection.commit()

    return int(row["id"])


def update_query_log_answer(
    query_log_id: int,
    answer_text: str | None,
    provider_used: str,
    fallback_used: bool,
    selected_context_chunk_ids: list[int] | None,
    dropped_context_chunk_ids: list[int] | None,
) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE query_logs
                SET
                  answer_text = %(answer_text)s,
                  provider_used = %(provider_used)s,
                  fallback_used = %(fallback_used)s,
                  selected_context_chunk_ids = %(selected_context_chunk_ids)s,
                  dropped_context_chunk_ids = %(dropped_context_chunk_ids)s
                WHERE id = %(query_log_id)s
                """,
                {
                    "query_log_id": query_log_id,
                    "answer_text": answer_text,
                    "provider_used": provider_used,
                    "fallback_used": fallback_used,
                    "selected_context_chunk_ids": Jsonb(selected_context_chunk_ids)
                    if selected_context_chunk_ids is not None
                    else None,
                    "dropped_context_chunk_ids": Jsonb(dropped_context_chunk_ids)
                    if dropped_context_chunk_ids is not None
                    else None,
                },
            )
        connection.commit()


def update_query_log_evaluation(
    query_log_id: int,
    has_evidence: bool,
    context_used_count: int,
    answer_length: int,
    grounded_flag: str,
) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE query_logs
                SET
                  has_evidence = %(has_evidence)s,
                  context_used_count = %(context_used_count)s,
                  answer_length = %(answer_length)s,
                  grounded_flag = %(grounded_flag)s
                WHERE id = %(query_log_id)s
                """,
                {
                    "query_log_id": query_log_id,
                    "has_evidence": has_evidence,
                    "context_used_count": context_used_count,
                    "answer_length": answer_length,
                    "grounded_flag": grounded_flag,
                },
            )
        connection.commit()


def list_query_logs(limit: int = 20) -> list[QueryLogRow]:
    return list_query_logs_filtered(limit=limit)


def list_query_logs_filtered(
    limit: int = 20,
    query_type: str | None = None,
    workspace: str | None = None,
    domain: str | None = None,
    project: str | None = None,
    client: str | None = None,
    module: str | None = None,
) -> list[QueryLogRow]:
    where_clauses: list[str] = []
    params: dict[str, object] = {"limit": limit}

    if query_type == "retrieval":
        where_clauses.append("provider_used = 'retrieval-only'")
    elif query_type == "answer":
        where_clauses.append("provider_used <> 'retrieval-only'")

    if workspace is not None:
        where_clauses.append("workspace = %(workspace)s")
        params["workspace"] = workspace

    if domain is not None:
        where_clauses.append("domain = %(domain)s")
        params["domain"] = domain

    if project is not None:
        where_clauses.append("project = %(project)s")
        params["project"] = project

    if client is not None:
        where_clauses.append("client = %(client)s")
        params["client"] = client

    if module is not None:
        where_clauses.append("module = %(module)s")
        params["module"] = module

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  id,
                  created_at,
                  query_text,
                  workspace,
                  domain,
                  project,
                  client,
                  module,
                  top_k,
                  result_count,
                  empty_result,
                  retrieved_chunk_ids,
                  retrieved_document_ids,
                  selected_context_chunk_ids,
                  dropped_context_chunk_ids,
                  answer_text,
                  has_evidence,
                  context_used_count,
                  answer_length,
                  grounded_flag,
                  candidate_count,
                  top_k_limit_hit,
                  returned_distance_values,
                  returned_document_distribution,
                  original_ranked_chunk_ids,
                  reranked_chunk_ids,
                  reranking_applied,
                  provider_used,
                  fallback_used
                FROM query_logs
                """
                + where_sql
                + """
                ORDER BY created_at DESC, id DESC
                LIMIT %(limit)s
                """,
                params,
            )
            rows = cursor.fetchall()

    return [
        QueryLogRow(
            id=row["id"],
            created_at=row["created_at"],
            query_text=row["query_text"],
            workspace=row["workspace"],
            domain=row["domain"],
            project=row["project"],
            client=row["client"],
            module=row["module"],
            top_k=row["top_k"],
            result_count=row["result_count"],
            empty_result=row["empty_result"],
            retrieved_chunk_ids=list(row["retrieved_chunk_ids"]),
            retrieved_document_ids=list(row["retrieved_document_ids"]),
            selected_context_chunk_ids=list(row["selected_context_chunk_ids"])
            if row["selected_context_chunk_ids"] is not None
            else None,
            dropped_context_chunk_ids=list(row["dropped_context_chunk_ids"])
            if row["dropped_context_chunk_ids"] is not None
            else None,
            answer_text=row["answer_text"],
            has_evidence=row["has_evidence"],
            context_used_count=row["context_used_count"],
            answer_length=row["answer_length"],
            grounded_flag=row["grounded_flag"],
            candidate_count=row["candidate_count"],
            top_k_limit_hit=row["top_k_limit_hit"],
            returned_distance_values=list(row["returned_distance_values"])
            if row["returned_distance_values"] is not None
            else None,
            returned_document_distribution=dict(row["returned_document_distribution"])
            if row["returned_document_distribution"] is not None
            else None,
            original_ranked_chunk_ids=list(row["original_ranked_chunk_ids"])
            if row["original_ranked_chunk_ids"] is not None
            else None,
            reranked_chunk_ids=list(row["reranked_chunk_ids"])
            if row["reranked_chunk_ids"] is not None
            else None,
            reranking_applied=row["reranking_applied"],
            provider_used=row["provider_used"],
            fallback_used=row["fallback_used"],
        )
        for row in rows
    ]
