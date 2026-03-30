from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from cfhee_backend.scope_registry.models import normalize_scope_value


class CapabilitiesFlags(BaseModel):
    document_ingest: bool
    document_inspection: bool
    scoped_retrieval: bool
    grounded_answer: bool
    query_logs: bool
    scope_values: bool


class ApiV1HealthResponse(BaseModel):
    status: str
    service: str
    api_version: str


class ApiV1CapabilitiesResponse(ApiV1HealthResponse):
    capabilities: CapabilitiesFlags


class ScopeRef(BaseModel):
    workspace: str
    domain: str
    project: str | None = None
    client: str | None = None
    module: str | None = None

    @field_validator("workspace", "domain", "project", "client", "module", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return normalize_scope_value(value)

    @model_validator(mode="after")
    def validate_scope_hierarchy(self) -> "ScopeRef":
        if self.client and not self.project:
            raise ValueError("client requires project")

        if self.module and not self.client:
            raise ValueError("module requires client")

        return self


class ScopeValuesResponseV1(BaseModel):
    workspaces: list[str]
    domains: list[str]
    projects: list[str]
    clients: list[str]
    modules: list[str]


class ScopeTreeModuleNodeV1(BaseModel):
    name: str


class ScopeTreeClientNodeV1(BaseModel):
    name: str
    modules: list[ScopeTreeModuleNodeV1]


class ScopeTreeProjectNodeV1(BaseModel):
    name: str
    clients: list[ScopeTreeClientNodeV1]


class ScopeTreeDomainNodeV1(BaseModel):
    name: str
    projects: list[ScopeTreeProjectNodeV1]


class ScopeTreeWorkspaceNodeV1(BaseModel):
    name: str
    domains: list[ScopeTreeDomainNodeV1]


class ScopeTreeResponseV1(BaseModel):
    workspaces: list[ScopeTreeWorkspaceNodeV1]


class DocumentCreateRequestV1(BaseModel):
    source_type: str
    title: str
    raw_text: str
    language: str | None = None
    source_ref: str | None = None
    scope: ScopeRef
    metadata: dict[str, object] | None = None


class DocumentCreateResponseV1(BaseModel):
    document_id: int
    status: str
    scope: ScopeRef
    chunk_count: int
    indexed: bool


class DocumentDeleteResponseV1(BaseModel):
    status: str
    document_id: int
    deleted_chunk_count: int


class DocumentListItemV1(BaseModel):
    document_id: int
    title: str
    source_type: str
    language: str | None
    source_ref: str | None
    scope: ScopeRef
    raw_text_preview: str
    created_at: str


class PagingInfoV1(BaseModel):
    limit: int
    offset: int
    returned: int


class DocumentListResponseV1(BaseModel):
    items: list[DocumentListItemV1]
    paging: PagingInfoV1


class DocumentDetailResponseV1(BaseModel):
    document_id: int
    title: str
    source_type: str
    language: str | None
    source_ref: str | None
    scope: ScopeRef
    raw_text_preview: str
    chunk_count: int
    created_at: str


class ChunkItemV1(BaseModel):
    chunk_id: int
    chunk_index: int
    text: str
    char_count: int


class DocumentChunksResponseV1(BaseModel):
    document_id: int
    chunks: list[ChunkItemV1]


class RetrievalQueryRequestV1(BaseModel):
    query: str
    scope: ScopeRef
    top_k: int = Field(default=5, ge=1, le=20)
    include_chunks: bool = True
    include_diagnostics: bool = False


class RetrievalResultV1(BaseModel):
    document_id: int
    chunk_id: int
    chunk_index: int
    title: str
    source_type: str
    similarity_score: float | None
    distance: float | None
    text: str | None = None


class RetrievalDiagnosticsV1(BaseModel):
    candidate_count: int
    top_k_limit_hit: bool
    reranking_applied: bool
    original_ranked_chunk_ids: list[int]
    reranked_chunk_ids: list[int]


class RetrievalQueryResponseV1(BaseModel):
    status: str
    query: str
    active_scope: ScopeRef
    results: list[RetrievalResultV1]
    result_count: int
    diagnostics: RetrievalDiagnosticsV1 | None = None


class ContextBuildRequestV1(BaseModel):
    query: str
    scope: ScopeRef
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=4, ge=1, le=20)
    include_diagnostics: bool = False


class ContextChunkV1(BaseModel):
    document_id: int
    chunk_id: int
    chunk_index: int
    title: str
    source_type: str
    similarity_score: float | None
    distance: float | None
    text: str


class ContextStatsV1(BaseModel):
    char_count: int
    chunk_count: int


class ContextBuildResponseV1(BaseModel):
    status: str
    query: str
    active_scope: ScopeRef
    context_text: str
    selected_chunks: list[ContextChunkV1]
    selected_chunk_count: int
    dropped_chunk_ids: list[int]
    context_stats: ContextStatsV1
    diagnostics: RetrievalDiagnosticsV1 | None = None


class QueryLogListItemV1(BaseModel):
    query_log_id: int
    type: Literal["retrieval", "answer"]
    query: str
    created_at: str
    active_scope: ScopeRef
    result_count: int
    provider_used: str
    fallback_used: bool


class QueryLogPagingV1(BaseModel):
    limit: int
    returned: int


class QueryLogListResponseV1(BaseModel):
    items: list[QueryLogListItemV1]
    paging: QueryLogPagingV1
