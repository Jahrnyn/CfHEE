from fastapi import APIRouter

from cfhee_backend.ops import OpsSummaryResponse, build_ops_summary


router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/summary", response_model=OpsSummaryResponse, response_model_exclude_none=True)
def get_ops_summary() -> OpsSummaryResponse:
    return build_ops_summary()
