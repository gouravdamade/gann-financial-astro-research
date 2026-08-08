from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import unittest

from bphs_classical_timing_service import (
    BPHS_CLASSICAL_CALENDAR_PROFILE_ID,
    _CalendarCalculator,
    _EPHEMERIS_LOCK,
    _muhurta_fixture,
    _muhurta_name,
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
        self.assertIn("TARA_NINEFOLD_SEQUENCE", state["tara"]["dependency"])
        self.assertIn("TARA_REFERENCE_IDENTITY", state["tara"]["dependency"])

    def test_source_closed_muhurta_order_preserves_literal_rows_and_repetitions(self) -> None:
        fixture = _muhurta_fixture()
        self.assertEqual(fixture["transcription"]["status"], "SOURCE_CLOSED_TWO_PASS_AGREED")
        self.assertEqual(fixture["transcription"]["diffStatus"], "AGREED")
        self.assertEqual([row["index"] for row in fixture["daytime"]], list(range(1, 16)))
        self.assertEqual([row["index"] for row in fixture["nighttime"]], list(range(1, 16)))
        self.assertEqual(_muhurta_name("DAY", 1), "Ardra")
        self.assertEqual(_muhurta_name("DAY", 15), "Vishvajit (Abhijit)")
        self.assertEqual(_muhurta_name("NIGHT", 4), "Uttara (source literal)")
        self.assertEqual(_muhurta_name("NIGHT", 6), "Rohini")
        self.assertEqual(_muhurta_name("NIGHT", 8), "Rohini")
        self.assertEqual(_muhurta_name("NIGHT", 10), "Hasta")
        self.assertEqual(_muhurta_name("NIGHT", 13), "Hasta")

    def test_sunrise_sunset_own_day_night_segments_with_source_names(self) -> None:
        calculator = _CalendarCalculator(timezone_name="Asia/Kolkata", latitude=18.5204, longitude=73.8567)
        with _EPHEMERIS_LOCK:
            calculator.configure_session()
            sunrise, sunset = calculator._sunrise_sunset(date(2025, 4, 1))
            day = calculator._muhurta(sunrise + timedelta(seconds=1))
            night = calculator._muhurta(sunset + timedelta(seconds=1))
        self.assertTrue(day["value"].startswith("DAY MUHURTA 01 - Ardra"))
        self.assertTrue(night["value"].startswith("NIGHT MUHURTA 01 - Uttarabhadrapada"))
        self.assertEqual(day["availability"], "SOURCE_TRANSCRIBED_ENGINEERING_BOUNDARY")
        self.assertIn("engineering boundaries", day["detail"])

    def test_weekday_is_explicit_civil_engineering_data_and_tara_stays_unavailable(self) -> None:
        result = build_bphs_classical_calendar_range(self.request())
        state = result["intervals"][0]["categories"]
        self.assertTrue(state["weekday"]["value"].startswith("Civil weekday:"))
        self.assertEqual(state["weekday"]["availability"], "PARTIAL_SOURCE")
        self.assertEqual(state["weekday"]["dependency"], "BPHS_1899_WEEKDAY_BOUNDARY_NOT_CLOSED")
        self.assertEqual(state["tara"]["value"], "DEPENDENCY_NOT_READY")
        self.assertIn("Packet 1W", state["tara"]["detail"])

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

    def test_service_has_no_sbc_market_or_execution_module_dependency(self) -> None:
        source = Path(__file__).with_name("bphs_classical_timing_service.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("from sbc", source)
        self.assertNotIn("import sbc", source)
        self.assertNotIn("metatrader", source)
        self.assertNotIn("order_send", source)


if __name__ == "__main__":
    unittest.main()
