from __future__ import annotations

import unittest

from repository import ASTRO_CONTRACT, AstroRepository


class AstroRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = AstroRepository()

    def test_chart_payload_uses_versioned_directional_events(self) -> None:
        payload = self.repository.chart_payload("2025-05-26", "2025-05-30")
        self.assertEqual(payload["astronomyContract"], ASTRO_CONTRACT)
        self.assertTrue(payload["candles"])
        self.assertTrue(payload["aspects"])
        self.assertTrue(payload["srLines"])
        self.assertTrue(all(item["familyKey"].startswith("TN::") for item in payload["aspects"]))

    def test_health_reports_corrected_touch_source(self) -> None:
        health = self.repository.health()
        self.assertEqual(health["touchCount"], 754)

    def test_parameter_schema_exposes_supported_and_pending_modes(self) -> None:
        schema = self.repository.parameter_schema()
        self.assertIn("M30", schema["options"]["timeframes"])
        self.assertEqual(schema["generation"]["correctedTn"], "generator_ready")
        self.assertEqual(schema["generation"]["correctedTt"], "not_implemented")
        self.assertEqual(schema["generation"]["profileJobQueue"], "ready")
        self.assertEqual(schema["generation"]["activeArtifactId"], self.repository.active_artifact["artifactId"])

    def test_chart_filters_and_m30_source_are_applied(self) -> None:
        payload = self.repository.chart_payload(
            "2025-05-26",
            "2025-05-30",
            timeframe="M30",
            transit_bodies=("MOON",),
            aspects=("square",),
            only_touched=True,
        )
        self.assertTrue(payload["candles"])
        self.assertTrue(payload["aspects"])
        self.assertTrue(all(item["transitBody"] == "MOON" for item in payload["aspects"]))
        self.assertTrue(all(item["aspect"] == "square" for item in payload["aspects"]))
        self.assertTrue(all(item["eventId"] in self.repository.touch_by_event for item in payload["aspects"]))

    def test_family_payload_preserves_transit_natal_direction(self) -> None:
        payload = self.repository.family_payload("TN::MOON->MERCURY::square")
        self.assertEqual(payload["transitBody"], "MOON")
        self.assertEqual(payload["natalBody"], "MERCURY")
        self.assertGreaterEqual(payload["summary"]["total"], 1)

    def test_codex_context_is_analysis_only(self) -> None:
        event_id = self.repository.family_payload("TN::MOON->MERCURY::square")["occurrences"][0]["eventId"]
        context = self.repository.codex_context(event_id)
        self.assertTrue(context["guardrails"]["analysisOnly"])
        self.assertFalse(context["guardrails"]["mt5OrderPlacementAllowed"])
        self.assertEqual(context["guardrails"]["astronomyContract"], ASTRO_CONTRACT)


if __name__ == "__main__":
    unittest.main()
