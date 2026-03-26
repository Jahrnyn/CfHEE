from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator


class RetrievalQueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query_text: str | None = None
    workspace: str | None = None
    domain: str | None = None
    project: str | None = None
    client: str | None = None
    module: str | None = None
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        validation_alias=AliasChoices("top_k", "limit"),
        serialization_alias="top_k",
    )

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
        if not self.query_text:
            raise ValueError("query_text is required")

        if not self.workspace or not self.domain:
            raise ValueError("workspace and domain are required; global retrieval is disabled")

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
    original_rank: int | None = None
    chunk_id: int
    document_id: int
    chunk_index: int
    text: str
    char_count: int
    similarity_score: float | None
    distance: float | None
    vector_score: float | None = None
    lexical_score: float | None = None
    final_score: float | None = None
    created_at: datetime
    document: RetrievedDocumentSummary
    scope: RetrievalScope


class RetrievalQueryResponse(BaseModel):
    query_text: str
    active_scope: RetrievalScope
    top_k: int
    returned_results: int
    empty: bool
    results: list[RetrievedChunkMatch]
