from fastapi import APIRouter

from cfhee_backend.api.document_routes import router as document_router
from cfhee_backend.api.retrieval_routes import router as retrieval_router

router = APIRouter()
router.include_router(document_router)
router.include_router(retrieval_router)


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
