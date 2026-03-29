from pathlib import Path
from typing import Any, Dict, List, Optional

class XYZSpatialService:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        # In a real implementation, you would load or initialize data here

    def create_plan(self, payload: Dict[str, Any], actor: str = "api_user") -> Dict[str, Any]:
        # Stub: Accepts a plan creation request and returns a mock plan
        return {
            "ok": True,
            "planId": "mock-plan-001",
            "createdBy": actor,
            "payload": payload,
            "message": "Plan created (mock)"
        }

    def create_generation_package(self, payload: Dict[str, Any], actor: str = "api_user") -> Dict[str, Any]:
        # Stub: Accepts a generation package request and returns a mock package
        return {
            "ok": True,
            "packageId": "mock-package-001",
            "createdBy": actor,
            "payload": payload,
            "message": "Generation package created (mock)"
        }

    def list_plans(self, limit: int = 100, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        # Stub: Returns a list of mock plans
        return {
            "ok": True,
            "plans": [
                {"planId": "mock-plan-001", "workspaceId": workspace_id, "summary": "Mock plan"}
            ][:limit]
        }

    def get_plan(self, plan_id: str) -> Dict[str, Any]:
        # Stub: Returns a mock plan
        return {
            "ok": True,
            "planId": plan_id,
            "summary": "Mock plan details"
        }

    def list_previews(self, limit: int = 100, workspace_id: Optional[str] = None, plan_id: Optional[str] = None) -> Dict[str, Any]:
        # Stub: Returns a list of mock previews
        return {
            "ok": True,
            "previews": [
                {"previewId": "mock-preview-001", "planId": plan_id, "workspaceId": workspace_id, "summary": "Mock preview"}
            ][:limit]
        }

    def get_preview(self, preview_id: str) -> Dict[str, Any]:
        # Stub: Returns a mock preview
        return {
            "ok": True,
            "previewId": preview_id,
            "summary": "Mock preview details"
        }

    def list_jobs(self, limit: int = 100, workspace_id: Optional[str] = None, plan_id: Optional[str] = None) -> Dict[str, Any]:
        # Stub: Returns a list of mock jobs
        return {
            "ok": True,
            "jobs": [
                {"jobId": "mock-job-001", "planId": plan_id, "workspaceId": workspace_id, "summary": "Mock job"}
            ][:limit]
        }

    def get_job(self, job_id: str) -> Dict[str, Any]:
        # Stub: Returns a mock job
        return {
            "ok": True,
            "jobId": job_id,
            "summary": "Mock job details"
        }

    def history(self, limit: int = 100, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        # Stub: Returns a mock history
        return {
            "ok": True,
            "history": [
                {"eventId": "mock-event-001", "workspaceId": workspace_id, "summary": "Mock event"}
            ][:limit]
        }
