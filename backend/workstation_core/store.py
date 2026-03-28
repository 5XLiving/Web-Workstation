from __future__ import annotations

from copy import deepcopy

from .scope import ScopeContext


class ScopeStore:
    def __init__(self) -> None:
        self._scopes: dict[str, dict] = {}
        self._mesh_index: dict[str, str] = {}

    def _ensure_scope(self, scope: ScopeContext) -> dict:
        return self._scopes.setdefault(
            scope.scope_key,
            {
                "scope": scope.to_dict(),
                "meshes": {},
            },
        )

    def create_mesh(self, scope: ScopeContext, payload: dict) -> dict:
        scope_bucket = self._ensure_scope(scope)
        mesh_number = len(scope_bucket["meshes"]) + 1
        mesh_id = f"{scope.scope_token}-mesh-{mesh_number:04d}"

        record = deepcopy(payload)
        record["meshId"] = mesh_id
        record["scope"] = deepcopy(scope_bucket["scope"])

        scope_bucket["meshes"][mesh_id] = record
        self._mesh_index[mesh_id] = scope.scope_key
        return deepcopy(record)

    def get_mesh(self, mesh_id: str) -> dict | None:
        scope_key = self._mesh_index.get(mesh_id)
        if not scope_key:
            return None
        scope_bucket = self._scopes.get(scope_key, {})
        record = scope_bucket.get("meshes", {}).get(mesh_id)
        return deepcopy(record) if record else None

    def update_mesh(self, mesh_id: str, payload: dict) -> dict | None:
        scope_key = self._mesh_index.get(mesh_id)
        if not scope_key:
            return None

        scope_bucket = self._scopes.get(scope_key, {})
        if mesh_id not in scope_bucket.get("meshes", {}):
            return None

        updated = deepcopy(payload)
        updated["meshId"] = mesh_id
        updated["scope"] = deepcopy(scope_bucket["scope"])
        scope_bucket["meshes"][mesh_id] = updated
        return deepcopy(updated)

    def summary(self) -> dict:
        total_meshes = sum(len(scope_bucket["meshes"]) for scope_bucket in self._scopes.values())
        return {
            "totalScopes": len(self._scopes),
            "totalMeshes": total_meshes,
        }