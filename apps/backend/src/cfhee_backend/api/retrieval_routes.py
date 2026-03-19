from fastapi import APIRouter

from cfhee_backend.retrieval import RetrievalQueryRequest, RetrievalQueryResponse, query_retrieval

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/query", response_model=RetrievalQueryResponse)
def query_retrieval_endpoint(payload: RetrievalQueryRequest) -> RetrievalQueryResponse:
    return query_retrieval(payload)
