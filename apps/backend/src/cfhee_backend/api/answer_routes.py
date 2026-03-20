from fastapi import APIRouter

from cfhee_backend.answers.models import AnswerQueryRequest, AnswerQueryResponse
from cfhee_backend.answers.service import query_answer

router = APIRouter(prefix="/answer", tags=["answer"])


@router.post("/query", response_model=AnswerQueryResponse)
def query_answer_endpoint(payload: AnswerQueryRequest) -> AnswerQueryResponse:
    return query_answer(payload)
