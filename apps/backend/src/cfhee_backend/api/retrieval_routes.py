from fastapi import APIRouter, HTTPException

from cfhee_backend.embeddings.base import EmbeddingProviderError
from cfhee_backend.retrieval import RetrievalQueryRequest, RetrievalQueryResponse, query_retrieval

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/query", response_model=RetrievalQueryResponse)
def query_retrieval_endpoint(payload: RetrievalQueryRequest) -> RetrievalQueryResponse:
    try:
        return query_retrieval(payload)
    except EmbeddingProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
