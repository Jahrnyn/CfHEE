from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cfhee_backend.api.routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Copilot for Hostile Enterprise Environment API",
        version="0.1.0",
        description="Minimal backend for the first vertical slice.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
