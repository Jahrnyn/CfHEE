from pydantic import BaseModel


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


class ScopeValuesResponseV1(BaseModel):
    workspaces: list[str]
    domains: list[str]
    projects: list[str]
    clients: list[str]
    modules: list[str]


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


class RetrievalQueryRequestV1(BaseModel):
    query: str
    scope: ScopeRef
    top_k: int = 5
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
