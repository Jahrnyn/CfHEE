from fastapi import APIRouter

from cfhee_backend.api.v1.models import DocumentCreateRequestV1, DocumentCreateResponseV1, ScopeRef
from cfhee_backend.ingestion.models import DocumentCreate
from cfhee_backend.ingestion.service import create_document, list_document_chunks

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
    )
    document = create_document(internal_payload)
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
