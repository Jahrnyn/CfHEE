from fastapi import APIRouter

from cfhee_backend.scope_registry.models import ScopeValuesQuery, ScopeValuesResponse
from cfhee_backend.scope_registry.service import list_scope_values

router = APIRouter(prefix="/scope-values", tags=["scope-values"])


@router.get("", response_model=ScopeValuesResponse)
def list_scope_values_endpoint(
    workspace: str | None = None,
    domain: str | None = None,
    project: str | None = None,
    client: str | None = None,
) -> ScopeValuesResponse:
    query = ScopeValuesQuery(
        workspace=workspace,
        domain=domain,
        project=project,
        client=client,
    )
    return list_scope_values(query)
