from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel

from cfhee_backend.embeddings import get_embedding_runtime_summary
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


class EmbeddingSummary(BaseModel):
    provider_selection: str
    active_provider: str
    model: str | None = None
    base_url: str | None = None
    dimensions: str | None = None


class ConfigSummary(BaseModel):
    frontend_api_base_url: str | None
    backend_cors_origins: list[str]
    postgres_target: PostgresTargetSummary
    chroma_persist_directory: str
    embedding: EmbeddingSummary
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


class BackupSummary(BaseModel):
    expected_backup_root: str
    backup_root_visible_to_runtime: bool
    backup_root_exists: bool
    discovered_backup_count: int
    latest_backup_name: str | None = None
    latest_backup_created_at_utc: str | None = None
    latest_backup_has_manifest: bool | None = None


class OpsSummaryResponse(BaseModel):
    status: str
    runtime_info: RuntimeInfoSummary
    config_summary: ConfigSummary
    storage_visibility: StorageVisibilitySummary
    backup_summary: BackupSummary
    notes: list[str]


def build_ops_summary() -> OpsSummaryResponse:
    chroma_persist_directory = get_chroma_persist_directory()
    database_url = get_database_url()
    runtime_mode = _detect_runtime_mode(database_url=database_url, chroma_persist_directory=chroma_persist_directory)
    embedding_runtime_summary = get_embedding_runtime_summary()

    return OpsSummaryResponse(
        status="ok",
        runtime_info=RuntimeInfoSummary(
            service="cfhee",
            public_api_version="v1",
            runtime_mode=runtime_mode,
            answer_provider_mode=_get_answer_provider_mode(),
            ollama=OllamaSummary(
                optional=_is_ollama_optional(),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
            ),
        ),
        config_summary=ConfigSummary(
            frontend_api_base_url=os.getenv("CFHEE_API_BASE_URL"),
            backend_cors_origins=_get_allowed_origins_summary(),
            postgres_target=_summarize_database_target(database_url),
            chroma_persist_directory=chroma_persist_directory,
            embedding=EmbeddingSummary(
                provider_selection=embedding_runtime_summary["provider_selection"],
                active_provider=embedding_runtime_summary["provider"],
                model=embedding_runtime_summary.get("model"),
                base_url=embedding_runtime_summary.get("base_url"),
                dimensions=embedding_runtime_summary.get("dimensions"),
            ),
            runtime_lifecycle_control="external",
        ),
        storage_visibility=StorageVisibilitySummary(
            chroma_persist_directory=_summarize_path(Path(chroma_persist_directory)),
            runtime_data_postgres=_summarize_path(_get_repo_root() / "runtime-data" / "postgres"),
            runtime_data_chroma=_summarize_path(_get_repo_root() / "runtime-data" / "chroma"),
        ),
        backup_summary=_summarize_backups(_get_repo_root() / "backups"),
        notes=[
            "This surface is read-only and reports conservative app-visible runtime facts only.",
            "Runtime start, stop, rebuild, and other host lifecycle operations remain external.",
            "Backup visibility here is read-only only. Backup creation and restore remain external helper-driven operations.",
            "Final destructive restore cutover remains external while the stopped-runtime restore model is in place.",
        ],
    )


def _get_answer_provider_mode() -> str:
    return os.getenv("ANSWER_PROVIDER", "auto").strip().lower() or "auto"


def _is_ollama_optional() -> bool:
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama").strip().lower() or "ollama"
    answer_provider = _get_answer_provider_mode()
    return embedding_provider == "hash" and answer_provider not in {"ollama"}


def _get_allowed_origins_summary() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOW_ORIGINS")
    if not configured_origins:
        return [
            "http://localhost:4200",
            "http://127.0.0.1:4200",
            "http://localhost:4210",
            "http://127.0.0.1:4210",
        ]

    origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
    return origins or [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:4210",
        "http://127.0.0.1:4210",
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
    resolved = Path(__file__).resolve()
    parents = list(resolved.parents)

    if len(parents) > 5:
        return parents[5]

    for parent in parents:
        if parent.name == "src":
            return parent.parent

    return parents[-1] if parents else Path.cwd()


def _summarize_path(path: Path) -> PathVisibilitySummary:
    exists = path.exists()
    is_directory = path.is_dir()

    return PathVisibilitySummary(
        path=str(path),
        visible_to_runtime=exists,
        exists=exists,
        writable=os.access(path, os.W_OK) if exists and is_directory else None,
    )


def _summarize_backups(backup_root: Path) -> BackupSummary:
    root_exists = backup_root.exists() and backup_root.is_dir()
    backup_entries = _discover_backups(backup_root) if root_exists else []
    latest_backup = backup_entries[-1] if backup_entries else None

    latest_backup_name = latest_backup.name if latest_backup else None
    latest_backup_has_manifest = None
    latest_backup_created_at_utc = None

    if latest_backup and latest_backup.is_dir():
        manifest_path = latest_backup / "manifest.json"
        latest_backup_has_manifest = manifest_path.exists()
        latest_backup_created_at_utc = _read_backup_manifest_timestamp(manifest_path) if manifest_path.exists() else None

    return BackupSummary(
        expected_backup_root=str(backup_root),
        backup_root_visible_to_runtime=root_exists,
        backup_root_exists=root_exists,
        discovered_backup_count=len(backup_entries),
        latest_backup_name=latest_backup_name,
        latest_backup_created_at_utc=latest_backup_created_at_utc,
        latest_backup_has_manifest=latest_backup_has_manifest,
    )


def _discover_backups(backup_root: Path) -> list[Path]:
    backups: list[Path] = []
    for child in backup_root.iterdir():
        if child.name.startswith("cfhee-backup-") and child.is_dir():
            backups.append(child)

    return sorted(backups, key=lambda path: path.name)


def _read_backup_manifest_timestamp(manifest_path: Path) -> str | None:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    created_at_utc = manifest.get("created_at_utc")
    return created_at_utc if isinstance(created_at_utc, str) and created_at_utc.strip() else None
