from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class MultiOscillatorActivityApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["GANN_ASTRO_API_TOKEN"] = "multi-oscillator-test-token"
        os.environ["GANN_ASTRO_MT5_AUTOCONNECT"] = "0"
        os.environ["GANN_ASTRO_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_CANDLE_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_REFRESH_AUTOSTART"] = "0"
        from server import app

        cls.app = app
        cls.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)

    def setUp(self) -> None:
        self.client = self.app.test_client()
        self.headers = {"X-Gann-Astro-Token": "multi-oscillator-test-token"}

    def test_activity_route_returns_json_contract(self) -> None:
        response_body = {
            "contract": "MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1",
            "evidenceMode": "EXPLORATORY_UNSIGNED",
            "fields": {"USD": {}, "JPY": {}},
            "guardrails": {"executionAllowed": False},
        }
        with patch("server.build_multi_oscillator_activity_range", return_value=response_body):
            response = self.client.post(
                "/api/multi-oscillator/activity-range",
                json={
                    "rangeStartUtc": "2025-04-01T00:00:00Z",
                    "rangeEndUtc": "2025-05-01T00:00:00Z",
                    "sideIdentities": ["USD", "JPY"],
                    "aspectProfileId": "ASPECT_STRENGTH_V0",
                },
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertEqual(response.get_json()["activity"]["contract"], "MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1")
        self.assertNotIn("<!doctype", response.get_data(as_text=True).lower())

    def test_activity_route_returns_structured_json_error(self) -> None:
        with patch("server.build_multi_oscillator_activity_range", side_effect=ValueError("unknown event universe field")):
            response = self.client.post(
                "/api/multi-oscillator/activity-range",
                json={"events": []},
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertEqual(response.get_json()["ok"], False)
        self.assertIn("unknown event universe", response.get_json()["error"])
        self.assertNotIn("<!doctype", response.get_data(as_text=True).lower())


if __name__ == "__main__":
    unittest.main()
