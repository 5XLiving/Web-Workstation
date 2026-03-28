from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..scope import resolve_scope
from ..services.mock_products import (
    build_ai_image_response,
    build_first_mesh_response,
    build_generate_model_response,
    build_refined_mesh_response,
    file_to_data_url,
)

client_bp = Blueprint("workstation_core_client", __name__)


@client_bp.post("/api/ai-image")
def ai_image() -> tuple:
    payload = request.get_json(silent=True) or {}
    scope = resolve_scope(request, current_app.config)

    prompt = str(payload.get("prompt", "concept object")).strip() or "concept object"
    style = str(payload.get("style", "studio")).strip() or "studio"
    aspect = str(payload.get("aspect", "1:1")).strip() or "1:1"

    return jsonify(build_ai_image_response(scope, prompt, style, aspect)), 200


@client_bp.post("/api/mesh/first")
def mesh_first() -> tuple:
    scope = resolve_scope(request, current_app.config)
    store = current_app.extensions["workstation_core_store"]

    image_file = request.files.get("image")
    species = str(request.form.get("species", "custom item")).strip() or "custom item"
    source_image = file_to_data_url(image_file)

    response = build_first_mesh_response(scope, species, source_image)
    created = store.create_mesh(scope, response)
    return jsonify(created), 200


@client_bp.post("/api/mesh/refine")
def mesh_refine() -> tuple:
    payload = request.get_json(silent=True) or {}
    store = current_app.extensions["workstation_core_store"]

    mesh_id = str(payload.get("meshId", "")).strip()
    params = payload.get("params", {})
    if not isinstance(params, dict):
        params = {}

    if not mesh_id:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "meshId is required",
                    "note": "Provide a meshId returned by /api/mesh/first.",
                }
            ),
            400,
        )

    existing = store.get_mesh(mesh_id)
    if not existing:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Unknown meshId",
                    "note": "The requested mesh was not found in this WorkStation Core store.",
                }
            ),
            404,
        )

    refined = build_refined_mesh_response(existing, params)
    updated = store.update_mesh(mesh_id, refined)
    return jsonify(updated), 200


@client_bp.post("/generate-model")
def generate_model() -> tuple:
    scope = resolve_scope(request, current_app.config)

    image_file = request.files.get("image")
    model_type = str(request.form.get("modelType", "generic-model")).strip() or "generic-model"
    preview_image = file_to_data_url(image_file)

    return jsonify(build_generate_model_response(scope, model_type, preview_image)), 200