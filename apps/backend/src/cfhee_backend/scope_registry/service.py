from __future__ import annotations

from typing import Any

from cfhee_backend.persistence.database import get_connection
from cfhee_backend.scope_registry.models import ScopeValuesQuery, ScopeValuesResponse, normalize_scope_value


def list_scope_values(query: ScopeValuesQuery) -> ScopeValuesResponse:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            workspace_values = _list_names(cursor=cursor, table_name="workspaces")
            workspace_id = _find_scope_id(cursor=cursor, table_name="workspaces", name=query.workspace)

            domain_values = _list_names(
                cursor=cursor,
                table_name="domains",
                parent_column="workspace_id",
                parent_id=workspace_id,
            )
            domain_id = _find_scope_id(
                cursor=cursor,
                table_name="domains",
                name=query.domain,
                parent_column="workspace_id",
                parent_id=workspace_id,
            )

            project_values = _list_names(
                cursor=cursor,
                table_name="projects",
                parent_column="domain_id",
                parent_id=domain_id,
            )
            project_id = _find_scope_id(
                cursor=cursor,
                table_name="projects",
                name=query.project,
                parent_column="domain_id",
                parent_id=domain_id,
            )

            client_values = _list_names(
                cursor=cursor,
                table_name="clients",
                parent_column="project_id",
                parent_id=project_id,
            )
            client_id = _find_scope_id(
                cursor=cursor,
                table_name="clients",
                name=query.client,
                parent_column="project_id",
                parent_id=project_id,
            )

            module_values = _list_names(
                cursor=cursor,
                table_name="modules",
                parent_column="client_id",
                parent_id=client_id,
            )

    return ScopeValuesResponse(
        workspaces=workspace_values,
        domains=domain_values,
        projects=project_values,
        clients=client_values,
        modules=module_values,
    )


def resolve_scope_name(
    cursor: Any,
    table_name: str,
    name: str | None,
    parent_column: str | None = None,
    parent_id: int | None = None,
) -> str | None:
    normalized_name = normalize_scope_value(name)
    if normalized_name is None:
        return None

    if parent_column is None:
        cursor.execute(
            f"""
            SELECT name
            FROM {table_name}
            WHERE LOWER(REGEXP_REPLACE(name, '\s+', ' ', 'g')) = LOWER(%(name)s)
            ORDER BY id ASC
            LIMIT 1
            """,
            {"name": normalized_name},
        )
    else:
        cursor.execute(
            f"""
            SELECT name
            FROM {table_name}
            WHERE {parent_column} = %(parent_id)s
              AND LOWER(REGEXP_REPLACE(name, '\s+', ' ', 'g')) = LOWER(%(name)s)
            ORDER BY id ASC
            LIMIT 1
            """,
            {"parent_id": parent_id, "name": normalized_name},
        )

    row = cursor.fetchone()
    if row is None:
        return normalized_name

    return row["name"]


def _find_scope_id(
    cursor: Any,
    table_name: str,
    name: str | None,
    parent_column: str | None = None,
    parent_id: int | None = None,
) -> int | None:
    normalized_name = normalize_scope_value(name)
    if normalized_name is None:
        return None

    if parent_column is None:
        cursor.execute(
            f"""
            SELECT id
            FROM {table_name}
            WHERE LOWER(REGEXP_REPLACE(name, '\s+', ' ', 'g')) = LOWER(%(name)s)
            ORDER BY id ASC
            LIMIT 1
            """,
            {"name": normalized_name},
        )
    else:
        if parent_id is None:
            return None

        cursor.execute(
            f"""
            SELECT id
            FROM {table_name}
            WHERE {parent_column} = %(parent_id)s
              AND LOWER(REGEXP_REPLACE(name, '\s+', ' ', 'g')) = LOWER(%(name)s)
            ORDER BY id ASC
            LIMIT 1
            """,
            {"parent_id": parent_id, "name": normalized_name},
        )

    row = cursor.fetchone()
    if row is None:
        return None

    return int(row["id"])


def _list_names(
    cursor: Any,
    table_name: str,
    parent_column: str | None = None,
    parent_id: int | None = None,
) -> list[str]:
    if parent_column is not None and parent_id is None:
        return []

    if parent_column is None:
        cursor.execute(f"SELECT name FROM {table_name} ORDER BY LOWER(name) ASC, name ASC")
    else:
        cursor.execute(
            f"""
            SELECT name
            FROM {table_name}
            WHERE {parent_column} = %(parent_id)s
            ORDER BY LOWER(name) ASC, name ASC
            """,
            {"parent_id": parent_id},
        )

    values: list[str] = []
    seen: set[str] = set()
    for row in cursor.fetchall():
        name = row["name"]
        normalized = normalize_scope_value(name)
        if normalized is None:
            continue

        key = normalized.lower()
        if key in seen:
            continue

        seen.add(key)
        values.append(name)

    return values
