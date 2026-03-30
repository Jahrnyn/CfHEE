from fastapi import APIRouter

from cfhee_backend.api.v1.models import ScopeTreeResponseV1, ScopeValuesResponseV1
from cfhee_backend.scope_registry.models import ScopeValuesQuery
from cfhee_backend.scope_registry.service import get_scope_tree, list_scope_values

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


@router.get("/scopes/tree", response_model=ScopeTreeResponseV1, tags=["scope-values"])
def get_scope_tree_v1() -> ScopeTreeResponseV1:
    # Visibility helper only: exposes stored hierarchy without scope inference or planning.
    response = get_scope_tree()
    return ScopeTreeResponseV1.model_validate(response.model_dump())
