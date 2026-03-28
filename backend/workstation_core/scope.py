from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from flask import Request


def _first_non_empty(*values: object) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = lowered.strip("-")
    return lowered or "default"


@dataclass(frozen=True)
class ScopeContext:
    company: str
    project: str
    workspace: str
    product: str

    @property
    def scope_key(self) -> str:
        return "::".join(
            [
                _slugify(self.company),
                _slugify(self.project),
                _slugify(self.workspace),
                _slugify(self.product),
            ]
        )

    @property
    def scope_token(self) -> str:
        digest = hashlib.sha1(self.scope_key.encode("utf-8")).hexdigest()
        return digest[:12]

    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "project": self.project,
            "workspace": self.workspace,
            "product": self.product,
            "scopeKey": self.scope_key,
        }


def resolve_scope(request: Request, config: dict) -> ScopeContext:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {}

    form_data = request.form.to_dict(flat=True)
    query_data = request.args.to_dict(flat=True)

    company = _first_non_empty(
        payload.get("company"),
        payload.get("companyName"),
        form_data.get("company"),
        query_data.get("company"),
        request.headers.get("X-WS-Company"),
        config.get("DEFAULT_COMPANY"),
    )
    project = _first_non_empty(
        payload.get("project"),
        payload.get("projectName"),
        form_data.get("project"),
        query_data.get("project"),
        request.headers.get("X-WS-Project"),
        config.get("DEFAULT_PROJECT"),
    )
    workspace = _first_non_empty(
        payload.get("workspace"),
        payload.get("workspaceId"),
        form_data.get("workspace"),
        query_data.get("workspace"),
        request.headers.get("X-WS-Workspace"),
        config.get("DEFAULT_WORKSPACE"),
    )
    product = _first_non_empty(
        payload.get("product"),
        payload.get("productName"),
        form_data.get("product"),
        query_data.get("product"),
        request.headers.get("X-WS-Product"),
        config.get("DEFAULT_PRODUCT"),
    )

    return ScopeContext(
        company=company,
        project=project,
        workspace=workspace,
        product=product,
    )