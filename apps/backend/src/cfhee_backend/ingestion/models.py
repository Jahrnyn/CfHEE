from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from cfhee_backend.scope_registry.models import normalize_scope_value


class DocumentCreate(BaseModel):
    workspace: str
    domain: str
    project: str | None = None
    client: str | None = None
    module: str | None = None
    source_type: str
    title: str
    raw_text: str
    language: str | None = None
    source_ref: str | None = None
    metadata: dict[str, Any] | None = None

    @field_validator(
        "workspace",
        "domain",
        "project",
        "client",
        "module",
        "source_type",
        "title",
        "language",
        "source_ref",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return normalize_scope_value(value)

    @field_validator("raw_text", mode="before")
    @classmethod
    def validate_raw_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("raw_text must be a string")

        if not value.strip():
            raise ValueError("raw_text must not be empty")

        return value

    @model_validator(mode="after")
    def validate_scope_hierarchy(self) -> "DocumentCreate":
        if self.client and not self.project:
            raise ValueError("client requires project")

        if self.module and not self.client:
            raise ValueError("module requires client")

        return self


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace: str
    domain: str
    project: str | None
    client: str | None
    module: str | None
    title: str
    source_type: str
    language: str | None
    source_ref: str | None
    metadata: dict[str, Any] | None
    raw_text_preview: str
    created_at: datetime


class ChunkSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    chunk_index: int
    text: str
    char_count: int
    workspace: str
    domain: str
    project: str | None
    client: str | None
    module: str | None
    created_at: datetime


class DocumentDeleteResult(BaseModel):
    document_id: int
    deleted_chunk_count: int
    status: str
