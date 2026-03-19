from __future__ import annotations

from typing import Any

from cfhee_backend.chunking.service import chunk_document
from cfhee_backend.embeddings import get_embedding_service
from cfhee_backend.ingestion.models import ChunkSummary, DocumentCreate, DocumentSummary
from cfhee_backend.persistence.database import get_connection
from cfhee_backend.vector_store import get_vector_store
from cfhee_backend.vector_store.base import VectorChunkRecord


def create_document(payload: DocumentCreate) -> DocumentSummary:
    chunk_rows: list[dict[str, Any]] = []

    with get_connection() as connection:
        with connection.cursor() as cursor:
            workspace_id = _upsert_scope(
                cursor,
                table_name="workspaces",
                name=payload.workspace,
                conflict_target="name",
            )
            domain_id = _upsert_scope(
                cursor,
                table_name="domains",
                name=payload.domain,
                parent_column="workspace_id",
                parent_id=workspace_id,
                conflict_target="workspace_id, name",
            )

            project_id = None
            if payload.project:
                project_id = _upsert_scope(
                    cursor,
                    table_name="projects",
                    name=payload.project,
                    parent_column="domain_id",
                    parent_id=domain_id,
                    conflict_target="domain_id, name",
                )

            client_id = None
            if payload.client and project_id is not None:
                client_id = _upsert_scope(
                    cursor,
                    table_name="clients",
                    name=payload.client,
                    parent_column="project_id",
                    parent_id=project_id,
                    conflict_target="project_id, name",
                )

            module_id = None
            if payload.module and client_id is not None:
                module_id = _upsert_scope(
                    cursor,
                    table_name="modules",
                    name=payload.module,
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

            _index_chunks(chunk_rows=chunk_rows, payload=payload)
        connection.commit()

    return get_document(document_id)


def list_documents() -> list[DocumentSummary]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"{_document_select()} ORDER BY d.created_at DESC, d.id DESC")
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


def _index_chunks(chunk_rows: list[dict[str, Any]], payload: DocumentCreate) -> None:
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
                workspace=payload.workspace,
                domain=payload.domain,
                project=payload.project,
                client=payload.client,
                module=payload.module,
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
