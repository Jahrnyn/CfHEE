from fastapi import APIRouter

from cfhee_backend.ingestion.models import ChunkSummary, DocumentCreate, DocumentSummary
from cfhee_backend.ingestion.service import create_document, list_document_chunks, list_documents

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentSummary)
def create_document_endpoint(payload: DocumentCreate) -> DocumentSummary:
    return create_document(payload)


@router.get("", response_model=list[DocumentSummary])
def list_documents_endpoint() -> list[DocumentSummary]:
    return list_documents()


@router.get("/{document_id}/chunks", response_model=list[ChunkSummary])
def list_document_chunks_endpoint(document_id: int) -> list[ChunkSummary]:
    return list_document_chunks(document_id)
