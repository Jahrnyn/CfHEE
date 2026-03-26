from fastapi import APIRouter

from cfhee_backend.api.v1.models import ScopeValuesResponseV1
from cfhee_backend.scope_registry.models import ScopeValuesQuery
from cfhee_backend.scope_registry.service import list_scope_values

router = APIRouter(tags=["api-v1-scopes"])


@router.get("/scopes/values", response_model=ScopeValuesResponseV1, tags=["scope-values"])
def list_scope_values_v1(
    workspace: str | None = None,
    domain: str | None = None,
    project: str | None = None,
    client: str | None = None,
) -> ScopeValuesResponseV1:
    response = list_scope_values(
        ScopeValuesQuery(
            workspace=workspace,
            domain=domain,
            project=project,
            client=client,
        )
    )
    return ScopeValuesResponseV1.model_validate(response.model_dump())
