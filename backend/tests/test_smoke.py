"""Small contract tests that do not require real GIS/AI models."""

import unittest

from app import app


class ApiSmokeTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/api/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "running")

    def test_tool_contracts(self):
        endpoints = [
            "/api/water/extract",
            "/api/path/plan",
            "/api/detect/objects",
            "/api/gis/overlay",
        ]
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, json={"provider": "mock"})
                body = response.get_json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(body["status"], "success")
                self.assertIn("data", body)
                self.assertIn("meta", body)

    def test_workflow_runs_real_tool_chain(self):
        response = self.client.post(
            "/api/orchestrator/execute",
            json={"scenario": "flood_recon", "params": {"provider": "mock"}},
        )
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertIn("water_extract", body["data"]["results"])
        self.assertIn("path_plan", body["data"]["results"])
        self.assertIn("gis_overlay", body["data"]["results"])
        self.assertIn("stats", body["data"]["results"])


if __name__ == "__main__":
    unittest.main()
