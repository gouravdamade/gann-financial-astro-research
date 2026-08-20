from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Xe3ApiRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.storage_directory = tempfile.TemporaryDirectory()
        os.environ["GANN_ASTRO_PROJECT_ROOT"] = str(PROJECT_ROOT)
        os.environ["GANN_ASTRO_API_TOKEN"] = "server-test-token-20260820"
        os.environ["GANN_ASTRO_XE3_SIGN_ADMISSION_DIR"] = cls.storage_directory.name
        os.environ["GANN_ASTRO_MT5_AUTOCONNECT"] = "0"
        os.environ["GANN_ASTRO_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_CANDLE_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_REFRESH_AUTOSTART"] = "0"
        from server import app

        cls.app = app
        cls.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.storage_directory.cleanup()

    def setUp(self) -> None:
        self.client = self.app.test_client()
        self.headers = {"X-Gann-Astro-Token": "server-test-token-20260820"}

    def test_xe3_workbench_is_json_and_contains_all_verified_rows(self) -> None:
        response = self.client.get("/api/experiments/xe3/workbench", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        payload = response.get_json()
        self.assertEqual(payload["ok"], True)
        sides = {side["sideIdentity"]: side for side in payload["workbench"]["sides"]}
        self.assertEqual(len(sides["USD"]["rows"]), 12)
        self.assertEqual(len(sides["JPY"]["rows"]), 12)
        self.assertTrue(
            all(
                row["identityStatus"] == "SINGLE_PASS_VERIFIED"
                for side in sides.values()
                for row in side["rows"]
            )
        )

    def test_missing_api_route_never_uses_the_spa_fallback(self) -> None:
        response = self.client.get("/api/experiments/xe3/missing", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", response.get_data(as_text=True).lower())
        self.assertIn("API route not found", response.get_json()["error"])

    def test_api_internal_failure_is_structured_json(self) -> None:
        with mock.patch(
            "server.build_xe3_signed_ledger",
            side_effect=PermissionError("simulated index lock"),
        ):
            response = self.client.get("/api/experiments/xe3/signed-ledger", headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", response.get_data(as_text=True).lower())
        self.assertIn("PermissionError", response.get_json()["error"])

    def test_existing_xe2_route_remains_json(self) -> None:
        response = self.client.get("/api/experiments/xe2/profile", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertEqual(response.get_json()["ok"], True)


if __name__ == "__main__":
    unittest.main()
