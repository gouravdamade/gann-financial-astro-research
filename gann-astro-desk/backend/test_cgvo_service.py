from __future__ import annotations

from pathlib import Path
import unittest

from cgvo_service import (
    CgvoRequestError,
    build_cgvo_event_search,
    build_cgvo_local_circumstances,
    build_cgvo_source_profiles,
    build_cgvo_status,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CgvoServiceTests(unittest.TestCase):
    def solar_search(self) -> dict:
        return build_cgvo_event_search(PROJECT_ROOT, {
            "startUtc": "2027-01-01T00:00:00Z",
            "endUtc": "2028-01-01T00:00:00Z",
            "eventType": "SOLAR",
            "limit": 24,
        })

    def test_global_search_is_deterministic_and_has_the_2027_demo_event(self) -> None:
        first = self.solar_search()
        second = self.solar_search()
        self.assertEqual(first, second)
        self.assertEqual(first["count"], 2)
        demo = next(item for item in first["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        self.assertEqual(demo["astronomyEventIdentity"]["globalType"], "TOTAL")
        self.assertTrue(demo["causalEventId"].startswith("CGVO-SOLAR-"))
        self.assertEqual(demo["guardrails"]["executionAllowed"], False)

    def test_locality_changes_local_facts_but_not_global_identity(self) -> None:
        event = next(item for item in self.solar_search()["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        common = {
            "eventType": "SOLAR",
            "globalMaxUtc": event["astronomyEventIdentity"]["globalMaxUtc"],
        }
        uj = build_cgvo_local_circumstances(PROJECT_ROOT, {
            **common, "localityId": "UJJAIN", "label": "Ujjain", "latitude": 23.1765,
            "longitude": 75.7885, "elevationM": 0, "timezone": "Asia/Kolkata",
        })["event"]
        ny = build_cgvo_local_circumstances(PROJECT_ROOT, {
            **common, "localityId": "NEW_YORK", "label": "New York", "latitude": 40.7128,
            "longitude": -74.006, "elevationM": 10, "timezone": "America/New_York",
        })["event"]
        self.assertEqual(uj["causalEventId"], ny["causalEventId"])
        self.assertEqual(uj["astronomyEventIdentity"], ny["astronomyEventIdentity"])
        self.assertEqual(uj["modernAstronomy"]["localEclipseType"], "PARTIAL")
        self.assertEqual(uj["modernAstronomy"]["visibility"], "VISIBLE")
        self.assertEqual(ny["modernAstronomy"]["visibility"], "NOT_VISIBLE")
        self.assertEqual(ny["modernAstronomy"]["localEclipseType"], "NOT_GEOMETRICALLY_VISIBLE")

    def test_unknown_and_source_profiles_are_explicit(self) -> None:
        status = build_cgvo_status(PROJECT_ROOT)
        self.assertEqual(status["sourceProfiles"]["varahamihira"], "WORKING_WITNESS_METADATA_PENDING")
        self.assertEqual(status["sourceProfiles"]["trailokya"], "SOURCE_SILENT_FOR_ECLIPSE_VISIBILITY_IN_HELD_WITNESS")
        profiles = build_cgvo_source_profiles(PROJECT_ROOT)["profiles"]
        trailokya = next(item for item in profiles if item["profileId"].startswith("TRAILOKYA"))
        self.assertIn("ECLIPSE VISIBILITY DOCTRINE: SOURCE SILENT IN HELD WITNESS", trailokya["banner"])
        self.assertFalse(build_cgvo_source_profiles(PROJECT_ROOT)["guardrails"]["crossSourceComposition"])
        event = self.solar_search()["events"][0]
        self.assertIn("VARAHAMIHIRA_RASI_MAPPING_UNRESOLVED", event["sourceUnknowns"])
        self.assertIn("TRAILOKYA_ECLIPSE_VISIBILITY_SOURCE_SILENT", event["sourceUnknowns"])

    def test_invalid_locality_fails_closed(self) -> None:
        with self.assertRaisesRegex(CgvoRequestError, "latitude"):
            build_cgvo_local_circumstances(PROJECT_ROOT, {
                "eventType": "SOLAR", "globalMaxUtc": "2027-08-02T10:06:41Z",
                "latitude": 91, "longitude": 0, "timezone": "UTC",
            })

    def test_lunar_search_uses_lunar_contract(self) -> None:
        result = build_cgvo_event_search(PROJECT_ROOT, {
            "startUtc": "2025-01-01T00:00:00Z",
            "endUtc": "2026-01-01T00:00:00Z",
            "eventType": "LUNAR",
            "limit": 24,
        })
        self.assertGreaterEqual(result["count"], 1)
        self.assertTrue(all(item["astronomyEventIdentity"]["eventType"] == "LUNAR" for item in result["events"]))
        self.assertTrue(all("P1" in item["astronomyEventIdentity"]["globalContacts"] for item in result["events"]))


if __name__ == "__main__":
    unittest.main()
