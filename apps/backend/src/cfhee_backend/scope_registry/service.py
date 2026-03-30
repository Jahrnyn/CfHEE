from __future__ import annotations

from typing import Any

from cfhee_backend.persistence.database import get_connection
from cfhee_backend.scope_registry.models import (
    ScopeTreeClientNode,
    ScopeTreeDomainNode,
    ScopeTreeModuleNode,
    ScopeTreeProjectNode,
    ScopeTreeResponse,
    ScopeTreeWorkspaceNode,
    ScopeValuesQuery,
    ScopeValuesResponse,
    normalize_scope_value,
)


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


def get_scope_tree() -> ScopeTreeResponse:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  w.id AS workspace_id,
                  w.name AS workspace_name,
                  d.id AS domain_id,
                  d.name AS domain_name,
                  p.id AS project_id,
                  p.name AS project_name,
                  c.id AS client_id,
                  c.name AS client_name,
                  m.id AS module_id,
                  m.name AS module_name
                FROM workspaces w
                LEFT JOIN domains d ON d.workspace_id = w.id
                LEFT JOIN projects p ON p.domain_id = d.id
                LEFT JOIN clients c ON c.project_id = p.id
                LEFT JOIN modules m ON m.client_id = c.id
                ORDER BY w.id ASC, d.id ASC, p.id ASC, c.id ASC, m.id ASC
                """
            )
            rows = cursor.fetchall()

    workspaces: list[ScopeTreeWorkspaceNode] = []
    workspace_nodes: dict[int, ScopeTreeWorkspaceNode] = {}
    domain_nodes: dict[int, ScopeTreeDomainNode] = {}
    project_nodes: dict[int, ScopeTreeProjectNode] = {}
    client_nodes: dict[int, ScopeTreeClientNode] = {}
    module_ids: set[int] = set()

    for row in rows:
        workspace_id = int(row["workspace_id"])
        workspace_node = workspace_nodes.get(workspace_id)
        if workspace_node is None:
            workspace_node = ScopeTreeWorkspaceNode(
                name=row["workspace_name"],
                domains=[],
            )
            workspace_nodes[workspace_id] = workspace_node
            workspaces.append(workspace_node)

        domain_id = row["domain_id"]
        if domain_id is None:
            continue

        domain_node = domain_nodes.get(int(domain_id))
        if domain_node is None:
            domain_node = ScopeTreeDomainNode(
                name=row["domain_name"],
                projects=[],
            )
            domain_nodes[int(domain_id)] = domain_node
            workspace_node.domains.append(domain_node)

        project_id = row["project_id"]
        if project_id is None:
            continue

        project_node = project_nodes.get(int(project_id))
        if project_node is None:
            project_node = ScopeTreeProjectNode(
                name=row["project_name"],
                clients=[],
            )
            project_nodes[int(project_id)] = project_node
            domain_node.projects.append(project_node)

        client_id = row["client_id"]
        if client_id is None:
            continue

        client_node = client_nodes.get(int(client_id))
        if client_node is None:
            client_node = ScopeTreeClientNode(
                name=row["client_name"],
                modules=[],
            )
            client_nodes[int(client_id)] = client_node
            project_node.clients.append(client_node)

        module_id = row["module_id"]
        if module_id is None or int(module_id) in module_ids:
            continue

        module_ids.add(int(module_id))
        client_node.modules.append(
            ScopeTreeModuleNode(
                name=row["module_name"],
            )
        )

    # Visibility helper only: this reflects stored scope hierarchy and does not infer missing scope.
    return ScopeTreeResponse(workspaces=workspaces)


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
            fr"""
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
            fr"""
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
            fr"""
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
            fr"""
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
