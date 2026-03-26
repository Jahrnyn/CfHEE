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
