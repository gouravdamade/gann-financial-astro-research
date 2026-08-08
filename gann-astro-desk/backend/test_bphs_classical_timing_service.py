from __future__ import annotations

import unittest

from bphs_classical_timing_service import (
    BPHS_CLASSICAL_CALENDAR_PROFILE_ID,
    build_bphs_classical_calendar_range,
)


class BphsClassicalTimingServiceTests(unittest.TestCase):
    def request(self) -> dict:
        return {
            "rangeStartUtc": "2025-04-01T00:00:00Z",
            "rangeEndUtc": "2025-04-02T00:00:00Z",
            "timezone": "Asia/Kolkata",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "profileId": BPHS_CLASSICAL_CALENDAR_PROFILE_ID,
        }

    def test_returns_sorted_clipped_half_open_calendar_intervals(self) -> None:
        result = build_bphs_classical_calendar_range(self.request())

        self.assertEqual(result["contract"], "BPHS_CLASSICAL_CALENDAR_RANGE_V1")
        self.assertEqual(result["intervals"][0]["startUtc"], self.request()["rangeStartUtc"])
        self.assertEqual(result["intervals"][-1]["endUtc"], self.request()["rangeEndUtc"])
        for left, right in zip(result["intervals"], result["intervals"][1:]):
            self.assertEqual(left["endUtc"], right["startUtc"])
            self.assertLess(left["startUtc"], left["endUtc"])

    def test_all_required_categories_and_explicit_tara_dependency_are_present(self) -> None:
        result = build_bphs_classical_calendar_range(self.request())
        state = result["intervals"][0]["categories"]

        self.assertEqual(set(state), {"muhurta", "tithi", "nakshatra", "yoga", "karana", "weekday", "tara"})
        self.assertEqual(state["tara"]["value"], "DEPENDENCY_NOT_READY")
        self.assertEqual(state["tara"]["availability"], "DEPENDENCY_NOT_READY")
        self.assertIn("MUHURTA_NAME_ORDER", state["muhurta"]["dependency"])

    def test_is_deterministic_and_has_no_market_or_direction_path(self) -> None:
        first = build_bphs_classical_calendar_range(self.request())
        second = build_bphs_classical_calendar_range(self.request())

        self.assertEqual(first["intervals"], second["intervals"])
        guardrails = first["guardrails"]
        self.assertFalse(guardrails["marketDataRead"])
        self.assertFalse(guardrails["priceOutcomeRead"])
        self.assertFalse(guardrails["polarityCatalogueRead"])
        self.assertFalse(guardrails["pairRelativeFieldPath"])
        self.assertFalse(guardrails["founderReviewDecisionPath"])
        self.assertFalse(guardrails["sbcPath"])
        self.assertFalse(guardrails["autoSuggestPath"])
        self.assertFalse(guardrails["mlPath"])
        self.assertFalse(guardrails["executionAllowed"])
        self.assertFalse(guardrails["marketDirectionInferred"])

    def test_rejects_frontend_market_and_profile_injection(self) -> None:
        for key, value in (("symbol", "USDJPY"), ("price", 151.0), ("events", []), ("profileId", "other")):
            with self.subTest(key=key):
                payload = self.request()
                payload[key] = value
                with self.assertRaises(ValueError):
                    build_bphs_classical_calendar_range(payload)


if __name__ == "__main__":
    unittest.main()
