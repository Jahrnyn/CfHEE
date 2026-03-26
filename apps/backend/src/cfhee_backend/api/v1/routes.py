from fastapi import APIRouter

from cfhee_backend.api.v1.models import ApiV1CapabilitiesResponse, ApiV1HealthResponse, CapabilitiesFlags

router = APIRouter(prefix="/api/v1", tags=["api-v1"])


@router.get("/health", response_model=ApiV1HealthResponse, tags=["system"])
async def health_check_v1() -> ApiV1HealthResponse:
    return ApiV1HealthResponse(
        status="ok",
        service="cfhee",
        api_version="v1",
    )


@router.get("/capabilities", response_model=ApiV1CapabilitiesResponse, tags=["system"])
async def capabilities_v1() -> ApiV1CapabilitiesResponse:
    return ApiV1CapabilitiesResponse(
        status="ok",
        service="cfhee",
        api_version="v1",
        capabilities=CapabilitiesFlags(
            document_ingest=True,
            document_inspection=True,
            scoped_retrieval=True,
            grounded_answer=True,
            query_logs=True,
            scope_values=True,
        ),
    )
