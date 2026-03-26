from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from cfhee_backend.api.v1.models import QueryLogListItemV1, QueryLogListResponseV1, QueryLogPagingV1, ScopeRef
from cfhee_backend.persistence.query_logs import QueryLogRow, list_query_logs_filtered

router = APIRouter(tags=["api-v1-query-logs"])


@router.get("/query-logs", response_model=QueryLogListResponseV1, tags=["query-logs"])
def list_query_logs_v1(
    limit: int = Query(default=20, ge=1, le=100),
    type: Literal["retrieval", "answer"] | None = None,
    workspace: str | None = None,
    domain: str | None = None,
    project: str | None = None,
    client: str | None = None,
    module: str | None = None,
) -> QueryLogListResponseV1:
    scope = None
    if any(value is not None for value in (workspace, domain, project, client, module)):
        if not workspace or not domain:
            raise HTTPException(
                status_code=422,
                detail="workspace and domain must be provided together when scope filtering query logs",
            )
        scope = ScopeRef(
            workspace=workspace,
            domain=domain,
            project=project,
            client=client,
            module=module,
        )

    rows = list_query_logs_filtered(
        limit=limit,
        query_type=type,
        workspace=scope.workspace if scope is not None else None,
        domain=scope.domain if scope is not None else None,
        project=scope.project if scope is not None else None,
        client=scope.client if scope is not None else None,
        module=scope.module if scope is not None else None,
    )

    return QueryLogListResponseV1(
        items=[_to_query_log_list_item(row) for row in rows],
        paging=QueryLogPagingV1(limit=limit, returned=len(rows)),
    )


def _to_query_log_list_item(row: QueryLogRow) -> QueryLogListItemV1:
    return QueryLogListItemV1(
        query_log_id=row.id,
        type="retrieval" if row.provider_used == "retrieval-only" else "answer",
        query=row.query_text,
        created_at=row.created_at.isoformat(),
        active_scope=ScopeRef(
            workspace=row.workspace,
            domain=row.domain,
            project=row.project,
            client=row.client,
            module=row.module,
        ),
        result_count=row.result_count,
        provider_used=row.provider_used,
        fallback_used=row.fallback_used,
    )
