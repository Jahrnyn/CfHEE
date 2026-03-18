from fastapi import APIRouter

router = APIRouter()


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
