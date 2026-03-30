from __future__ import annotations

from typing import Any

from cfhee_backend.chunking.service import chunk_document
from cfhee_backend.embeddings import get_embedding_service
from cfhee_backend.ingestion.models import ChunkSummary, DocumentCreate, DocumentDeleteResult, DocumentSummary
from cfhee_backend.persistence.database import get_connection
from cfhee_backend.scope_registry.service import resolve_scope_name
from cfhee_backend.vector_store import get_vector_store
from cfhee_backend.vector_store.base import VectorChunkRecord


class DocumentNotFoundError(ValueError):
    """Raised when a document lifecycle operation targets a missing document."""


def create_document(payload: DocumentCreate) -> DocumentSummary:
    chunk_rows: list[dict[str, Any]] = []
    canonical_scope = {
        "workspace": payload.workspace,
        "domain": payload.domain,
        "project": payload.project,
        "client": payload.client,
        "module": payload.module,
    }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            canonical_scope["workspace"] = resolve_scope_name(
                cursor=cursor,
                table_name="workspaces",
                name=payload.workspace,
            )
            workspace_id = _upsert_scope(
                cursor,
                table_name="workspaces",
                name=canonical_scope["workspace"],
                conflict_target="name",
            )
            canonical_scope["domain"] = resolve_scope_name(
                cursor=cursor,
                table_name="domains",
                name=payload.domain,
                parent_column="workspace_id",
                parent_id=workspace_id,
            )
            domain_id = _upsert_scope(
                cursor,
                table_name="domains",
                name=canonical_scope["domain"],
                parent_column="workspace_id",
                parent_id=workspace_id,
                conflict_target="workspace_id, name",
            )

            project_id = None
            if payload.project:
                canonical_scope["project"] = resolve_scope_name(
                    cursor=cursor,
                    table_name="projects",
                    name=payload.project,
                    parent_column="domain_id",
                    parent_id=domain_id,
                )
                project_id = _upsert_scope(
                    cursor,
                    table_name="projects",
                    name=canonical_scope["project"],
                    parent_column="domain_id",
                    parent_id=domain_id,
                    conflict_target="domain_id, name",
                )

            client_id = None
            if payload.client and project_id is not None:
                canonical_scope["client"] = resolve_scope_name(
                    cursor=cursor,
                    table_name="clients",
                    name=payload.client,
                    parent_column="project_id",
                    parent_id=project_id,
                )
                client_id = _upsert_scope(
                    cursor,
                    table_name="clients",
                    name=canonical_scope["client"],
                    parent_column="project_id",
                    parent_id=project_id,
                    conflict_target="project_id, name",
                )

            module_id = None
            if payload.module and client_id is not None:
                canonical_scope["module"] = resolve_scope_name(
                    cursor=cursor,
                    table_name="modules",
                    name=payload.module,
                    parent_column="client_id",
                    parent_id=client_id,
                )
                module_id = _upsert_scope(
                    cursor,
                    table_name="modules",
                    name=canonical_scope["module"],
                    parent_column="client_id",
                    parent_id=client_id,
                    conflict_target="client_id, name",
                )

            cursor.execute(
                """
                INSERT INTO documents (
                  workspace_id,
                  domain_id,
                  project_id,
                  client_id,
                  module_id,
                  title,
                  source_type,
                  language,
                  source_ref,
                  raw_text
                )
                VALUES (
                  %(workspace_id)s,
                  %(domain_id)s,
                  %(project_id)s,
                  %(client_id)s,
                  %(module_id)s,
                  %(title)s,
                  %(source_type)s,
                  %(language)s,
                  %(source_ref)s,
                  %(raw_text)s
                )
                RETURNING id
                """,
                {
                    "workspace_id": workspace_id,
                    "domain_id": domain_id,
                    "project_id": project_id,
                    "client_id": client_id,
                    "module_id": module_id,
                    "title": payload.title,
                    "source_type": payload.source_type,
                    "language": payload.language,
                    "source_ref": payload.source_ref,
                    "raw_text": payload.raw_text,
                },
            )
            document_id = cursor.fetchone()["id"]

            chunk_rows = _insert_chunks(
                cursor=cursor,
                document_id=document_id,
                workspace_id=workspace_id,
                domain_id=domain_id,
                project_id=project_id,
                client_id=client_id,
                module_id=module_id,
                raw_text=payload.raw_text,
            )

            _index_chunks(chunk_rows=chunk_rows, payload=payload, canonical_scope=canonical_scope)
        connection.commit()

    return get_document(document_id)


def list_documents() -> list[DocumentSummary]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"{_document_select()} ORDER BY d.created_at DESC, d.id DESC")
            rows = cursor.fetchall()

    return [DocumentSummary.model_validate(row) for row in rows]


def list_documents_filtered(
    workspace: str,
    domain: str,
    project: str | None = None,
    client: str | None = None,
    module: str | None = None,
    source_type: str | None = None,
    title_contains: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[DocumentSummary]:
    where_clauses = [
        "w.name = %(workspace)s",
        "dm.name = %(domain)s",
    ]
    params: dict[str, Any] = {
        "workspace": workspace,
        "domain": domain,
        "limit": limit,
        "offset": offset,
    }

    if project is not None:
        where_clauses.append("p.name = %(project)s")
        params["project"] = project

    if client is not None:
        where_clauses.append("c.name = %(client)s")
        params["client"] = client

    if module is not None:
        where_clauses.append("m.name = %(module)s")
        params["module"] = module

    if source_type is not None:
        where_clauses.append("d.source_type = %(source_type)s")
        params["source_type"] = source_type

    if title_contains is not None:
        where_clauses.append("d.title ILIKE %(title_contains)s")
        params["title_contains"] = f"%{title_contains}%"

    where_sql = " AND ".join(where_clauses)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                {_document_select()}
                WHERE {where_sql}
                ORDER BY d.created_at DESC, d.id DESC
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                params,
            )
            rows = cursor.fetchall()

    return [DocumentSummary.model_validate(row) for row in rows]


def get_document(document_id: int) -> DocumentSummary:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"{_document_select()} WHERE d.id = %(document_id)s",
                {"document_id": document_id},
            )
            row = cursor.fetchone()

    return DocumentSummary.model_validate(row)


def list_document_chunks(document_id: int) -> list[ChunkSummary]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"{_chunk_select()} WHERE ch.document_id = %(document_id)s ORDER BY ch.chunk_index ASC",
                {"document_id": document_id},
            )
            rows = cursor.fetchall()

    return [ChunkSummary.model_validate(row) for row in rows]


def delete_document(document_id: int) -> DocumentDeleteResult:
    vector_store = get_vector_store()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM documents
                WHERE id = %(document_id)s
                """,
                {"document_id": document_id},
            )
            document_row = cursor.fetchone()

            if document_row is None:
                raise DocumentNotFoundError(f"document {document_id} was not found")

            cursor.execute(
                """
                SELECT id
                FROM chunks
                WHERE document_id = %(document_id)s
                ORDER BY id ASC
                """,
                {"document_id": document_id},
            )
            chunk_rows = cursor.fetchall()
            chunk_ids = [int(row["id"]) for row in chunk_rows]

            # Capture the stored chunk ids first so vector cleanup follows the same explicit mapping.
            vector_store.delete_chunks(chunk_ids)

            cursor.execute(
                """
                DELETE FROM documents
                WHERE id = %(document_id)s
                RETURNING id
                """,
                {"document_id": document_id},
            )
            deleted_row = cursor.fetchone()

        connection.commit()

    if deleted_row is None:
        raise DocumentNotFoundError(f"document {document_id} was not found")

    return DocumentDeleteResult(
        status="ok",
        document_id=int(deleted_row["id"]),
        deleted_chunk_count=len(chunk_ids),
    )


def get_document_chunk_count(document_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) AS chunk_count
                FROM chunks
                WHERE document_id = %(document_id)s
                """,
                {"document_id": document_id},
            )
            row = cursor.fetchone()

    return int(row["chunk_count"])


def _upsert_scope(
    cursor: Any,
    table_name: str,
    name: str,
    conflict_target: str,
    parent_column: str | None = None,
    parent_id: int | None = None,
) -> int:
    if parent_column is None:
        cursor.execute(
            f"""
            INSERT INTO {table_name} (name)
            VALUES (%(name)s)
            ON CONFLICT ({conflict_target}) DO UPDATE
            SET name = EXCLUDED.name
            RETURNING id
            """,
            {"name": name},
        )
    else:
        cursor.execute(
            f"""
            INSERT INTO {table_name} ({parent_column}, name)
            VALUES (%(parent_id)s, %(name)s)
            ON CONFLICT ({conflict_target}) DO UPDATE
            SET name = EXCLUDED.name
            RETURNING id
            """,
            {"parent_id": parent_id, "name": name},
        )

    return cursor.fetchone()["id"]


def _insert_chunks(
    cursor: Any,
    document_id: int,
    workspace_id: int,
    domain_id: int,
    project_id: int | None,
    client_id: int | None,
    module_id: int | None,
    raw_text: str,
) -> list[dict[str, Any]]:
    inserted_chunks: list[dict[str, Any]] = []

    for chunk in chunk_document(raw_text):
        cursor.execute(
            """
            INSERT INTO chunks (
              document_id,
              workspace_id,
              domain_id,
              project_id,
              client_id,
              module_id,
              chunk_index,
              text,
              char_count
            )
            VALUES (
              %(document_id)s,
              %(workspace_id)s,
              %(domain_id)s,
              %(project_id)s,
              %(client_id)s,
              %(module_id)s,
              %(chunk_index)s,
              %(text)s,
              %(char_count)s
            )
            RETURNING id, document_id, chunk_index, text, char_count
            """,
            {
                "document_id": document_id,
                "workspace_id": workspace_id,
                "domain_id": domain_id,
                "project_id": project_id,
                "client_id": client_id,
                "module_id": module_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "char_count": chunk.char_count,
            },
        )
        inserted_chunks.append(cursor.fetchone())

    return inserted_chunks


def _index_chunks(
    chunk_rows: list[dict[str, Any]],
    payload: DocumentCreate,
    canonical_scope: dict[str, str | None],
) -> None:
    if not chunk_rows:
        return

    embedding_service = get_embedding_service()
    vector_store = get_vector_store()
    embeddings = embedding_service.embed_texts([chunk["text"] for chunk in chunk_rows])

    vector_store.index_chunks(
        [
            VectorChunkRecord(
                chunk_id=chunk["id"],
                document_id=chunk["document_id"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                embedding=embedding,
                workspace=canonical_scope["workspace"] or payload.workspace,
                domain=canonical_scope["domain"] or payload.domain,
                project=canonical_scope["project"],
                client=canonical_scope["client"],
                module=canonical_scope["module"],
                source_type=payload.source_type,
                language=payload.language,
            )
            for chunk, embedding in zip(chunk_rows, embeddings, strict=True)
        ]
    )


def _document_select() -> str:
    return """
        SELECT
          d.id,
          w.name AS workspace,
          dm.name AS domain,
          p.name AS project,
          c.name AS client,
          m.name AS module,
          d.title,
          d.source_type,
          d.language,
          d.source_ref,
          LEFT(d.raw_text, 280) AS raw_text_preview,
          d.created_at
        FROM documents d
        JOIN workspaces w ON w.id = d.workspace_id
        JOIN domains dm ON dm.id = d.domain_id
        LEFT JOIN projects p ON p.id = d.project_id
        LEFT JOIN clients c ON c.id = d.client_id
        LEFT JOIN modules m ON m.id = d.module_id
    """


def _chunk_select() -> str:
    return """
        SELECT
          ch.id,
          ch.document_id,
          ch.chunk_index,
          ch.text,
          ch.char_count,
          w.name AS workspace,
          dm.name AS domain,
          p.name AS project,
          c.name AS client,
          m.name AS module,
          ch.created_at
        FROM chunks ch
        JOIN workspaces w ON w.id = ch.workspace_id
        JOIN domains dm ON dm.id = ch.domain_id
        LEFT JOIN projects p ON p.id = ch.project_id
        LEFT JOIN clients c ON c.id = ch.client_id
        LEFT JOIN modules m ON m.id = ch.module_id
    """
