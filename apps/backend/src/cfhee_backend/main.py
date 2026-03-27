import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cfhee_backend.api.routes import router as api_router
from cfhee_backend.persistence.database import initialize_database


DEFAULT_CORS_ALLOW_ORIGINS = (
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost:4210",
    "http://127.0.0.1:4210",
)


def get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOW_ORIGINS")
    if not configured_origins:
        return list(DEFAULT_CORS_ALLOW_ORIGINS)

    origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
    return origins or list(DEFAULT_CORS_ALLOW_ORIGINS)


def create_app() -> FastAPI:
    initialize_database()

    app = FastAPI(
        title="Copilot for Hostile Enterprise Environment API",
        version="0.1.0",
        description="Minimal backend for the first vertical slice.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
