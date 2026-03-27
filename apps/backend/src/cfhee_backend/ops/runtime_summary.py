from __future__ import annotations

import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel

from cfhee_backend.persistence.database import get_database_url
from cfhee_backend.vector_store.chroma_adapter import get_chroma_persist_directory


class OllamaSummary(BaseModel):
    optional: bool
    base_url: str
    model: str


class RuntimeInfoSummary(BaseModel):
    service: str
    public_api_version: str
    runtime_mode: Literal["portable-runtime-container", "source-local", "unknown"]
    answer_provider_mode: str
    ollama: OllamaSummary


class PostgresTargetSummary(BaseModel):
    scheme: str | None
    host: str | None
    port: int | None
    database: str | None


class ConfigSummary(BaseModel):
    frontend_api_base_url: str | None
    backend_cors_origins: list[str]
    postgres_target: PostgresTargetSummary
    chroma_persist_directory: str
    runtime_lifecycle_control: Literal["external"]


class PathVisibilitySummary(BaseModel):
    path: str
    visible_to_runtime: bool
    exists: bool
    writable: bool | None = None


class StorageVisibilitySummary(BaseModel):
    chroma_persist_directory: PathVisibilitySummary
    runtime_data_postgres: PathVisibilitySummary
    runtime_data_chroma: PathVisibilitySummary


class OpsSummaryResponse(BaseModel):
    status: str
    runtime_info: RuntimeInfoSummary
    config_summary: ConfigSummary
    storage_visibility: StorageVisibilitySummary
    notes: list[str]


def build_ops_summary() -> OpsSummaryResponse:
    chroma_persist_directory = get_chroma_persist_directory()
    database_url = get_database_url()
    runtime_mode = _detect_runtime_mode(database_url=database_url, chroma_persist_directory=chroma_persist_directory)

    return OpsSummaryResponse(
        status="ok",
        runtime_info=RuntimeInfoSummary(
            service="cfhee",
            public_api_version="v1",
            runtime_mode=runtime_mode,
            answer_provider_mode=_get_answer_provider_mode(),
            ollama=OllamaSummary(
                optional=True,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
            ),
        ),
        config_summary=ConfigSummary(
            frontend_api_base_url=os.getenv("CFHEE_API_BASE_URL"),
            backend_cors_origins=_get_allowed_origins_summary(),
            postgres_target=_summarize_database_target(database_url),
            chroma_persist_directory=chroma_persist_directory,
            runtime_lifecycle_control="external",
        ),
        storage_visibility=StorageVisibilitySummary(
            chroma_persist_directory=_summarize_path(Path(chroma_persist_directory)),
            runtime_data_postgres=_summarize_path(_get_repo_root() / "runtime-data" / "postgres"),
            runtime_data_chroma=_summarize_path(_get_repo_root() / "runtime-data" / "chroma"),
        ),
        notes=[
            "This surface is read-only and reports conservative app-visible runtime facts only.",
            "Runtime start, stop, rebuild, and other host lifecycle operations remain external.",
            "Final destructive restore cutover remains external while the stopped-runtime restore model is in place.",
        ],
    )


def _get_answer_provider_mode() -> str:
    return os.getenv("ANSWER_PROVIDER", "auto").strip().lower() or "auto"


def _get_allowed_origins_summary() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOW_ORIGINS")
    if not configured_origins:
        return [
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ]

    origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
    return origins or [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]


def _summarize_database_target(database_url: str) -> PostgresTargetSummary:
    parsed = urlparse(database_url)
    database = parsed.path.lstrip("/") or None

    return PostgresTargetSummary(
        scheme=parsed.scheme or None,
        host=parsed.hostname,
        port=parsed.port,
        database=database,
    )


def _detect_runtime_mode(database_url: str, chroma_persist_directory: str) -> Literal["portable-runtime-container", "source-local", "unknown"]:
    postgres_target = _summarize_database_target(database_url)
    chroma_path = Path(chroma_persist_directory)

    if postgres_target.host == "postgres" and chroma_path.as_posix() == "/app/data/chroma":
        return "portable-runtime-container"

    if postgres_target.host in {"localhost", "127.0.0.1"}:
        default_source_path = (_get_repo_root() / "apps" / "backend" / "data" / "chroma").resolve()
        if chroma_path.resolve() == default_source_path:
            return "source-local"

    return "unknown"


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _summarize_path(path: Path) -> PathVisibilitySummary:
    exists = path.exists()
    is_directory = path.is_dir()

    return PathVisibilitySummary(
        path=str(path),
        visible_to_runtime=exists,
        exists=exists,
        writable=os.access(path, os.W_OK) if exists and is_directory else None,
    )
