from fastapi import APIRouter, HTTPException, Query

from cfhee_backend.api.v1.models import (
    ChunkItemV1,
    DocumentChunksResponseV1,
    DocumentCreateRequestV1,
    DocumentCreateResponseV1,
    DocumentDeleteResponseV1,
    DocumentDetailResponseV1,
    DocumentListItemV1,
    DocumentListResponseV1,
    PagingInfoV1,
    ScopeRef,
)
from cfhee_backend.embeddings.base import EmbeddingProviderError
from cfhee_backend.ingestion.models import DocumentCreate
from cfhee_backend.ingestion.service import (
    create_document,
    delete_document,
    get_document,
    get_document_chunk_count,
    list_document_chunks,
    list_documents_filtered,
    DocumentNotFoundError,
)

router = APIRouter(tags=["api-v1-documents"])


@router.post("/documents", response_model=DocumentCreateResponseV1, tags=["documents"])
def create_document_v1(payload: DocumentCreateRequestV1) -> DocumentCreateResponseV1:
    internal_payload = DocumentCreate(
        workspace=payload.scope.workspace,
        domain=payload.scope.domain,
        project=payload.scope.project,
        client=payload.scope.client,
        module=payload.scope.module,
        source_type=payload.source_type,
        title=payload.title,
        raw_text=payload.raw_text,
        language=payload.language,
        source_ref=payload.source_ref,
        metadata=payload.metadata,
    )
    try:
        document = create_document(internal_payload)
    except EmbeddingProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    chunk_count = len(list_document_chunks(document.id))

    return DocumentCreateResponseV1(
        document_id=document.id,
        status="stored",
        scope=ScopeRef(
            workspace=document.workspace,
            domain=document.domain,
            project=document.project,
            client=document.client,
            module=document.module,
        ),
        chunk_count=chunk_count,
        indexed=chunk_count > 0,
    )


@router.get("/documents", response_model=DocumentListResponseV1, tags=["documents"])
def list_documents_v1(
    workspace: str,
    domain: str,
    project: str | None = None,
    client: str | None = None,
    module: str | None = None,
    source_type: str | None = None,
    title_contains: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DocumentListResponseV1:
    scope = ScopeRef(
        workspace=workspace,
        domain=domain,
        project=project,
        client=client,
        module=module,
    )
    documents = list_documents_filtered(
        workspace=scope.workspace,
        domain=scope.domain,
        project=scope.project,
        client=scope.client,
        module=scope.module,
        source_type=source_type,
        title_contains=title_contains,
        limit=limit,
        offset=offset,
    )

    return DocumentListResponseV1(
        items=[
            DocumentListItemV1(
                document_id=document.id,
                title=document.title,
                source_type=document.source_type,
                language=document.language,
                source_ref=document.source_ref,
                metadata=document.metadata,
                scope=ScopeRef(
                    workspace=document.workspace,
                    domain=document.domain,
                    project=document.project,
                    client=document.client,
                    module=document.module,
                ),
                raw_text_preview=document.raw_text_preview,
                created_at=document.created_at.isoformat(),
            )
            for document in documents
        ],
        paging=PagingInfoV1(
            limit=limit,
            offset=offset,
            returned=len(documents),
        ),
    )


@router.get("/documents/{document_id}", response_model=DocumentDetailResponseV1, tags=["documents"])
def get_document_v1(document_id: int) -> DocumentDetailResponseV1:
    document = get_document(document_id)
    chunk_count = get_document_chunk_count(document_id)

    return DocumentDetailResponseV1(
        document_id=document.id,
        title=document.title,
        source_type=document.source_type,
        language=document.language,
        source_ref=document.source_ref,
        metadata=document.metadata,
        scope=ScopeRef(
            workspace=document.workspace,
            domain=document.domain,
            project=document.project,
            client=document.client,
            module=document.module,
        ),
        raw_text_preview=document.raw_text_preview,
        chunk_count=chunk_count,
        created_at=document.created_at.isoformat(),
    )


@router.get("/documents/{document_id}/chunks", response_model=DocumentChunksResponseV1, tags=["documents"])
def list_document_chunks_v1(document_id: int) -> DocumentChunksResponseV1:
    chunks = list_document_chunks(document_id)

    return DocumentChunksResponseV1(
        document_id=document_id,
        chunks=[
            ChunkItemV1(
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                char_count=chunk.char_count,
            )
            for chunk in chunks
        ],
    )


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponseV1, tags=["documents"])
def delete_document_v1(document_id: int) -> DocumentDeleteResponseV1:
    try:
        result = delete_document(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return DocumentDeleteResponseV1(
        status=result.status,
        document_id=result.document_id,
        deleted_chunk_count=result.deleted_chunk_count,
    )
