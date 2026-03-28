# WorkStation Core

Minimal Flask backend skeleton for product-facing WorkStation actions and future Dev Room admin control.

## Why Flask here

This workspace already uses Flask and flask-cors in the active backend environment, so WorkStation Core can run without adding a second backend stack.

## What this skeleton includes

- Client-facing product routes:
  - `/api/ai-image`
  - `/api/mesh/first`
  - `/api/mesh/refine`
  - `/generate-model`
- Admin/internal route:
  - `/admin/ping`
- Service health route:
  - `/health`
- In-memory scope isolation keyed by company, project, workspace, and product
- Safe mock responses that match the current 3D model maker frontend contract

## Scope isolation

Scope can be supplied by request body, form fields, query string, or headers:

- `company`
- `project`
- `workspace`
- `product`

Header equivalents:

- `X-WS-Company`
- `X-WS-Project`
- `X-WS-Workspace`
- `X-WS-Product`

If omitted, defaults are used. Stored mesh state is bucketed by scope so products and workspaces can stay isolated as this backend expands.

## Local run

From the workspace root:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m workstation_core
```

Default address:

- `http://127.0.0.1:5000`

Optional environment overrides:

```powershell
$env:WORKSTATION_CORE_PORT="5050"
$env:WORKSTATION_CORE_DEBUG="false"
python -m workstation_core
```

## Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m unittest workstation_core.tests.test_app
```