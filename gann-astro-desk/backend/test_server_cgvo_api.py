from __future__ import annotations

import os
import unittest


class CgvoApiRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["GANN_ASTRO_API_TOKEN"] = "cgvo-test-token-20260821"
        os.environ["GANN_ASTRO_MT5_AUTOCONNECT"] = "0"
        os.environ["GANN_ASTRO_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_CANDLE_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_REFRESH_AUTOSTART"] = "0"
        from server import app
        cls.app = app
        cls.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)

    def setUp(self) -> None:
        self.client = self.app.test_client()
        self.headers = {"X-Gann-Astro-Token": "cgvo-test-token-20260821"}

    def test_cgvo_status_and_workbench_are_json_read_only(self) -> None:
        status = self.client.get("/api/experiments/cgvo/status", headers=self.headers)
        self.assertEqual(status.status_code, 200)
        self.assertTrue(status.content_type.startswith("application/json"))
        self.assertFalse(status.get_json()["status"]["guardrails"]["executionAllowed"])
        workbench = self.client.get(
            "/api/experiments/cgvo/workbench?eventType=SOLAR&globalMaxUtc=2027-08-02T10:06:41Z&localityId=UJJAIN&label=Ujjain&latitude=23.1765&longitude=75.7885&elevationM=0&timezone=Asia%2FKolkata",
            headers=self.headers,
        )
        self.assertEqual(workbench.status_code, 200)
        self.assertTrue(workbench.content_type.startswith("application/json"))
        payload = workbench.get_json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["workbench"]["event"]["modernAstronomy"]["localEclipseType"], "PARTIAL")
        self.assertFalse(payload["workbench"]["guardrails"]["marketDirectionInferred"])

    def test_invalid_locality_is_typed_json_error(self) -> None:
        response = self.client.get(
            "/api/experiments/cgvo/eclipse-search?eventType=SOLAR&startUtc=2027-01-01T00:00:00Z&endUtc=2028-01-01T00:00:00Z&limit=1",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        bad = self.client.get(
            "/api/experiments/cgvo/workbench?eventType=SOLAR&globalMaxUtc=2027-08-02T10:06:41Z&latitude=91&longitude=0&timezone=UTC",
            headers=self.headers,
        )
        self.assertEqual(bad.status_code, 400)
        self.assertTrue(bad.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", bad.get_data(as_text=True).lower())
        self.assertIn("latitude", bad.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
