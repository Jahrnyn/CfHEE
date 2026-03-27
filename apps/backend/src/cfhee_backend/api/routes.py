from fastapi import APIRouter

from cfhee_backend.api.answer_routes import router as answer_router
from cfhee_backend.api.document_routes import router as document_router
from cfhee_backend.api.ops_routes import router as ops_router
from cfhee_backend.api.query_log_routes import router as query_log_router
from cfhee_backend.api.retrieval_routes import router as retrieval_router
from cfhee_backend.api.scope_routes import router as scope_router
from cfhee_backend.api.v1.routes import router as api_v1_router

router = APIRouter()
router.include_router(answer_router)
router.include_router(document_router)
router.include_router(ops_router)
router.include_router(query_log_router)
router.include_router(retrieval_router)
router.include_router(scope_router)
router.include_router(api_v1_router)


@router.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/", tags=["system"])
async def root() -> dict[str, object]:
    return {
        "name": "Copilot for Hostile Enterprise Environment API",
        "status": "running",
        "docs_url": "/docs",
    }
