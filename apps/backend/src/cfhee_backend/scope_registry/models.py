from __future__ import annotations

from pydantic import BaseModel, field_validator


def normalize_scope_value(value: str | None) -> str | None:
    if value is None:
        return None

    collapsed = " ".join(value.split())
    return collapsed or None


class ScopeValuesQuery(BaseModel):
    workspace: str | None = None
    domain: str | None = None
    project: str | None = None
    client: str | None = None

    @field_validator("workspace", "domain", "project", "client", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return normalize_scope_value(value)


class ScopeValuesResponse(BaseModel):
    workspaces: list[str]
    domains: list[str]
    projects: list[str]
    clients: list[str]
    modules: list[str]
