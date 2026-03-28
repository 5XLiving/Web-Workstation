from __future__ import annotations

from io import BytesIO
import unittest

from workstation_core import create_app


class WorkStationCoreAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_health_route(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["service"], "WorkStation Core")

    def test_admin_ping_route(self) -> None:
        response = self.client.get("/admin/ping")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["admin"])
        self.assertEqual(payload["totalScopes"], 0)

    def test_ai_image_route_shape(self) -> None:
        response = self.client.post(
            "/api/ai-image",
            json={
                "prompt": "reading lamp",
                "style": "product render",
                "aspect": "1:1",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("imageUrl", payload)
        self.assertIn("note", payload)
        self.assertTrue(payload["imageUrl"].startswith("data:image/svg+xml"))

    def test_mesh_lifecycle_and_scope_count(self) -> None:
        create_response = self.client.post(
            "/api/mesh/first",
            data={
                "species": "chair",
                "workspace": "client-room-a",
                "image": (BytesIO(b"fake-image"), "chair.png"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(create_response.status_code, 200)
        created = create_response.get_json()
        self.assertIn("meshId", created)
        self.assertIn("glbUrl", created)
        self.assertEqual(created["scope"]["workspace"], "client-room-a")

        refine_response = self.client.post(
            "/api/mesh/refine",
            json={
                "meshId": created["meshId"],
                "params": {"smooth": 0.9, "decimate": 0.2, "thickness": 0.6},
            },
        )
        self.assertEqual(refine_response.status_code, 200)
        refined = refine_response.get_json()
        self.assertEqual(refined["meshId"], created["meshId"])
        self.assertEqual(refined["params"]["smooth"], 0.9)

        admin_response = self.client.get("/admin/ping")
        admin_payload = admin_response.get_json()
        self.assertEqual(admin_payload["totalScopes"], 1)
        self.assertEqual(admin_payload["totalMeshes"], 1)

    def test_generate_model_route_shape(self) -> None:
        response = self.client.post(
            "/generate-model",
            data={
                "modelType": "toy",
                "workspace": "preview-lane",
                "image": (BytesIO(b"preview-image"), "toy.png"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("previewImage", payload)
        self.assertIn("note", payload)


if __name__ == "__main__":
    unittest.main()