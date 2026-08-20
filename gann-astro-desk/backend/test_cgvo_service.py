from __future__ import annotations

from pathlib import Path
import unittest

import swisseph as swe
import cgvo_service

from cgvo_service import (
    CgvoRequestError,
    build_cgvo_event_search,
    build_cgvo_kurma_seed,
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
            "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "causalEventId": event["causalEventId"],
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
        self.assertIsNone(ny["modernAstronomy"]["visibilityDetails"]["horizonEvents"]["riseUtc"])
        self.assertIsNone(ny["modernAstronomy"]["visibilityDetails"]["horizonEvents"]["setUtc"])

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

    def test_horizontal_coordinates_are_topocentric_and_azimuth_is_explicitly_normalized(self) -> None:
        event = next(item for item in self.solar_search()["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        payload = {
            "eventType": "SOLAR",
            "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "causalEventId": event["causalEventId"],
            "localityId": "UJJAIN", "label": "Ujjain", "latitude": 23.1765,
            "longitude": 75.7885, "elevationM": 0, "timezone": "Asia/Kolkata",
        }
        modern = build_cgvo_local_circumstances(PROJECT_ROOT, payload)["event"]["modernAstronomy"]
        for coordinates in (modern["sunAltitudeAzimuth"], modern["moonAltitudeAzimuth"]):
            self.assertTrue(coordinates["topocentric"])
            self.assertEqual(coordinates["azimuthConvention"], "NORTH_CLOCKWISE_0N_90E_180S_270W")
            self.assertEqual(coordinates["sourceAzimuthConvention"], "SWISSEPH_SOUTH_CLOCKWISE_TO_WEST")
            self.assertAlmostEqual(coordinates["azimuthDeg"], (coordinates["sourceAzimuthDeg"] + 180.0) % 360.0, places=7)

    def test_rise_set_clipped_visibility_is_not_collapsed_to_not_visible(self) -> None:
        result = build_cgvo_event_search(PROJECT_ROOT, {
            "startUtc": "2019-12-01T00:00:00Z", "endUtc": "2020-12-01T00:00:00Z",
            "eventType": "LUNAR", "limit": 24,
        })
        event = next(item for item in result["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2020-01-10"))
        modern = build_cgvo_local_circumstances(PROJECT_ROOT, {
            "eventType": "LUNAR", "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "causalEventId": event["causalEventId"], "localityId": "ANTARCTIC_TEST",
            "label": "Antarctic test locality", "latitude": -60, "longitude": 10,
            "elevationM": 0, "timezone": "UTC",
        })["event"]["modernAstronomy"]
        self.assertEqual(modern["visibility"], "RISE_SET_CLIPPED")
        self.assertEqual(modern["visibilityDetails"]["maximumVisibility"], "NOT_VISIBLE_AT_MAXIMUM")
        self.assertTrue(modern["visibilityDetails"]["clipBoundaries"])
        self.assertTrue(modern["visibilityDetails"]["visibleWindowStartUtc"] or modern["visibilityDetails"]["visibleWindowEndUtc"])

    def test_lunar_umbral_and_penumbral_magnitudes_use_swiss_lunar_eclipse_how(self) -> None:
        result = build_cgvo_event_search(PROJECT_ROOT, {
            "startUtc": "2025-01-01T00:00:00Z", "endUtc": "2026-01-01T00:00:00Z",
            "eventType": "LUNAR", "limit": 24,
        })
        event = next(item for item in result["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2025-09-07"))
        locality = {"longitude": 75.7885, "latitude": 23.1765, "elevationM": 0}
        output = build_cgvo_local_circumstances(PROJECT_ROOT, {
            "eventType": "LUNAR", "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "causalEventId": event["causalEventId"], "localityId": "UJJAIN", "label": "Ujjain",
            **locality, "timezone": "Asia/Kolkata",
        })["event"]
        modern = output["modernAstronomy"]
        how_time = modern["localMaxUtc"] or event["astronomyEventIdentity"]["globalMaxSwissUt"]
        expected = swe.lun_eclipse_how(cgvo_service._jd(cgvo_service._parse_utc(how_time, "how_time")), (locality["longitude"], locality["latitude"], locality["elevationM"]), swe.FLG_SWIEPH)[1]
        self.assertEqual(modern["magnitudeReference"], "SWISSEPH_LUNAR_ECLIPSE_HOW_AT_EVENT_MAX_SWISSEPH_UT")
        self.assertAlmostEqual(modern["umbralMagnitude"], expected[0], places=7)
        self.assertAlmostEqual(modern["penumbralMagnitude"], expected[1], places=7)

    def test_causal_event_id_must_match_reconstructed_event(self) -> None:
        event = next(item for item in self.solar_search()["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        with self.assertRaisesRegex(CgvoRequestError, "causalEventId"):
            build_cgvo_local_circumstances(PROJECT_ROOT, {
                "eventType": "SOLAR", "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
                "causalEventId": "CGVO-SOLAR-NOT-THE-EVENT", "localityId": "UJJAIN", "label": "Ujjain",
                "latitude": 23.1765, "longitude": 75.7885, "elevationM": 0, "timezone": "Asia/Kolkata",
            })

    def test_kurma_seed_keeps_raw_chapter_xiv_names_without_modern_mapping(self) -> None:
        seed = build_cgvo_kurma_seed(PROJECT_ROOT)
        self.assertEqual(seed["status"], "RAW_CHAPTER_XIV_NAMES_MODERN_MAPPING_NOT_BUILT")
        self.assertFalse(seed["historicalSource"]["modernGeographicInference"])
        self.assertEqual(len(seed["groups"]), 9)
        self.assertTrue(all(group["historicalNames"] for group in seed["groups"]))
        self.assertTrue(all(group["mappingStatus"] == "UNKNOWN" for group in seed["groups"]))


if __name__ == "__main__":
    unittest.main()
