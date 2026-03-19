from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RetrievalQueryRequest(BaseModel):
    query_text: str
    workspace: str
    domain: str
    project: str | None = None
    client: str | None = None
    module: str | None = None
    limit: int = Field(default=5, ge=1, le=20)

    @field_validator(
        "query_text",
        "workspace",
        "domain",
        "project",
        "client",
        "module",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_scope_hierarchy(self) -> "RetrievalQueryRequest":
        if self.client and not self.project:
            raise ValueError("client requires project")

        if self.module and not self.client:
            raise ValueError("module requires client")

        return self


class RetrievalScope(BaseModel):
    workspace: str
    domain: str
    project: str | None
    client: str | None
    module: str | None


class RetrievedDocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source_type: str
    language: str | None
    source_ref: str | None
    created_at: datetime


class RetrievedChunkMatch(BaseModel):
    rank: int
    chunk_id: int
    document_id: int
    chunk_index: int
    text: str
    char_count: int
    distance: float | None
    created_at: datetime
    document: RetrievedDocumentSummary
    scope: RetrievalScope


class RetrievalQueryResponse(BaseModel):
    query_text: str
    active_scope: RetrievalScope
    results: list[RetrievedChunkMatch]
