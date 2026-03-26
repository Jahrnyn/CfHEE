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
