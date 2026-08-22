from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

import swisseph as swe
import cgvo_service

from cgvo_service import (
    CgvoRequestError,
    build_cgvo_event_search,
    build_cgvo_historical_gazetteer,
    build_cgvo_historical_research_footprints,
    build_cgvo_kurma_seed,
    build_cgvo_local_circumstances,
    build_cgvo_source_profiles,
    build_cgvo_status,
    build_cgvo_workbench,
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
        self.assertEqual(status["sourceProfiles"]["varahamihira"], "SOURCE_ARCHITECTURE_AVAILABLE_READ_ONLY")
        self.assertEqual(status["sourceProfiles"]["trailokya"], "SOURCE_SILENT_FOR_ECLIPSE_VISIBILITY_IN_HELD_WITNESS")
        self.assertEqual(status["sourceAdapters"]["varahamihiraFrame"]["partitionStatus"], "CLOSED_ROOT_SOURCE")
        self.assertFalse(status["sourceAdapters"]["varahamihiraFrame"]["defaultAuthorized"])
        profiles = build_cgvo_source_profiles(PROJECT_ROOT)["profiles"]
        trailokya = next(item for item in profiles if item["profileId"].startswith("TRAILOKYA"))
        self.assertIn("ECLIPSE VISIBILITY DOCTRINE: SOURCE SILENT IN HELD WITNESS", trailokya["banner"])
        self.assertFalse(build_cgvo_source_profiles(PROJECT_ROOT)["guardrails"]["crossSourceComposition"])
        event = self.solar_search()["events"][0]
        self.assertIn("VARAHAMIHIRA_ABSOLUTE_FRAME_RECONSTRUCTION_NOT_DEFAULT", event["sourceUnknowns"])
        self.assertIn("TRAILOKYA_ECLIPSE_VISIBILITY_SOURCE_SILENT", event["sourceUnknowns"])

    def test_s1a_requires_explicit_absolute_frame_and_never_defaults_to_raman_or_tropical(self) -> None:
        event = next(item for item in self.solar_search()["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        common = {
            "eventType": "SOLAR", "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "causalEventId": event["causalEventId"], "localityId": "UJJAIN", "label": "Ujjain",
            "latitude": 23.1765, "longitude": 75.7885, "elevationM": 0, "timezone": "Asia/Kolkata",
        }
        unselected = build_cgvo_workbench(PROJECT_ROOT, common)["event"]["sourceAdapters"]
        self.assertEqual(unselected["varahamihiraFrame"]["absoluteFrameStatus"], "NULL")
        self.assertIsNone(unselected["varahamihiraFrame"]["luminary"]["rasi"])
        self.assertEqual(unselected["varahamihiraAspect"]["auditGeometryAtMaximum"]["records"], [])
        selected = build_cgvo_workbench(PROJECT_ROOT, {
            **common, "absoluteFrameProfileId": "VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1",
        })["event"]["sourceAdapters"]
        self.assertEqual(selected["varahamihiraFrame"]["selectedProfileId"], "VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1")
        self.assertEqual(selected["varahamihiraFrame"]["luminary"]["availability"], "SOURCE_RECONSTRUCTION_CANDIDATE_CALCULATED")
        self.assertEqual(len(selected["varahamihiraAspect"]["auditGeometryAtMaximum"]["records"]), 5)
        with self.assertRaisesRegex(CgvoRequestError, "absoluteFrameProfileId"):
            build_cgvo_workbench(PROJECT_ROOT, {**common, "absoluteFrameProfileId": "RAMAN"})

    def test_s1a_lunar_month_and_aspect_geometry_stay_categorical_and_fail_closed(self) -> None:
        fixture = cgvo_service._s1a_fixtures(PROJECT_ROOT)["lunarMonth"]
        locality = {"localityId": "UJJAIN", "timezone": "Asia/Kolkata"}
        ordinary = cgvo_service._lunar_month_adapter(
            cgvo_service._parse_utc("2025-04-15T00:00:00Z", "timestamp"),
            locality,
            cgvo_service.VARAHAMIHIRA_CHITRA_FRAME_ID,
            fixture,
        )
        self.assertEqual(ordinary["baseSystem"], "PURNIMANTA")
        self.assertEqual(ordinary["result"], "VAISHAKHA")
        intercalary = cgvo_service._lunar_month_adapter(
            cgvo_service._parse_utc("2023-07-29T00:00:00Z", "timestamp"),
            locality,
            cgvo_service.VARAHAMIHIRA_CHITRA_FRAME_ID,
            fixture,
        )
        self.assertEqual(intercalary["result"], "UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED")
        self.assertEqual(intercalary["unknownReason"], "ADHIKA_OR_KSHAYA_GUARD_TRIGGERED")
        self.assertEqual(intercalary["intercalationGuard"]["status"], "AMBIGUOUS_OR_INTERCALARY")
        self.assertTrue(any(item["sankrantiCount"] != 1 for item in intercalary["intercalationGuard"]["synodicIntervals"]))
        aspect = cgvo_service._eclipse_aspect_adapter(
            cgvo_service._parse_utc("2027-08-02T10:06:41Z", "timestamp"), "SOLAR",
            cgvo_service.VARAHAMIHIRA_CHITRA_FRAME_ID,
            cgvo_service._s1a_fixtures(PROJECT_ROOT)["aspect"],
        )
        self.assertIsNone(aspect["effectMagnitudeMultiplier"])
        self.assertIsNone(aspect["jupiterMitigationCoefficient"])
        self.assertEqual(aspect["auditGeometryAtMaximum"]["role"], "GEOMETRY_SNAPSHOT_ONLY")
        self.assertTrue(all(record["fraction"] in {0.0, 0.25, 0.5, 0.75, 1.0} for record in aspect["auditGeometryAtMaximum"]["records"]))
        self.assertEqual(aspect["sourcePhaseActivation"]["status"], "UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED")
        self.assertIsNone(aspect["sourcePhaseActivation"]["effectActivated"])
        self.assertIsNone(aspect["sourcePhaseActivation"]["jupiterMitigationActivated"])
        self.assertFalse(build_cgvo_status(PROJECT_ROOT)["guardrails"]["executionAllowed"])

    def test_s1a_r1_lunar_guard_fails_closed_when_ingresses_cannot_be_resolved(self) -> None:
        fixture = cgvo_service._s1a_fixtures(PROJECT_ROOT)["lunarMonth"]
        locality = {"localityId": "UJJAIN", "timezone": "Asia/Kolkata"}
        with patch.object(cgvo_service, "_solar_rasi_ingresses", side_effect=RuntimeError("fixture failure")):
            result = cgvo_service._lunar_month_adapter(
                cgvo_service._parse_utc("2025-04-15T00:00:00Z", "timestamp"),
                locality,
                cgvo_service.VARAHAMIHIRA_CHITRA_FRAME_ID,
                fixture,
            )
        self.assertEqual(result["result"], "UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED")
        self.assertEqual(result["unknownReason"], "SANKRANTI_BOUNDARY_NOT_RESOLVED")

    def test_s1a_r1_lunar_guard_rejects_zero_or_two_ingresses(self) -> None:
        fixture = cgvo_service._s1a_fixtures(PROJECT_ROOT)["lunarMonth"]
        locality = {"localityId": "UJJAIN", "timezone": "Asia/Kolkata"}
        for ingresses in ([], [{"atUtc": "2025-04-14T00:00:00Z"}, {"atUtc": "2025-04-15T00:00:00Z"}]):
            with self.subTest(ingress_count=len(ingresses)), patch.object(cgvo_service, "_solar_rasi_ingresses", return_value=ingresses):
                result = cgvo_service._lunar_month_adapter(
                    cgvo_service._parse_utc("2025-04-15T00:00:00Z", "timestamp"),
                    locality,
                    cgvo_service.VARAHAMIHIRA_CHITRA_FRAME_ID,
                    fixture,
                )
            self.assertEqual(result["result"], "UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED")
            self.assertEqual(result["unknownReason"], "ADHIKA_OR_KSHAYA_GUARD_TRIGGERED")

    def test_s1a_r1_topocentric_geometry_is_locality_safe_under_concurrency(self) -> None:
        event = next(item for item in self.solar_search()["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        common = {
            "eventType": "SOLAR", "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "causalEventId": event["causalEventId"],
        }
        localities = {
            "UJJAIN": {"localityId": "UJJAIN", "label": "Ujjain", "latitude": 23.1765, "longitude": 75.7885, "elevationM": 0, "timezone": "Asia/Kolkata"},
            "NEW_YORK": {"localityId": "NEW_YORK", "label": "New York", "latitude": 40.7128, "longitude": -74.006, "elevationM": 10, "timezone": "America/New_York"},
        }
        def calculate(locality: dict) -> tuple[dict, dict]:
            result = build_cgvo_workbench(PROJECT_ROOT, {**common, **locality})["event"]
            return result["modernAstronomy"]["sunAltitudeAzimuth"], result["sourceAdapters"]["varahamihiraFirmament"]["rawGeometry"]
        baseline = {name: calculate(locality) for name, locality in localities.items()}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(calculate, localities[name]) for name in ("UJJAIN", "NEW_YORK") * 8]
            results = [future.result() for future in futures]
        for index, result in enumerate(results):
            self.assertEqual(result, baseline["UJJAIN" if index % 2 == 0 else "NEW_YORK"])
        self.assertNotEqual(baseline["UJJAIN"], baseline["NEW_YORK"])

    def test_s1a_firmament_remains_raw_geometry_not_a_certified_classifier(self) -> None:
        event = next(item for item in self.solar_search()["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        result = build_cgvo_workbench(PROJECT_ROOT, {
            "eventType": "SOLAR", "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "causalEventId": event["causalEventId"], "localityId": "UJJAIN", "label": "Ujjain",
            "latitude": 23.1765, "longitude": 75.7885, "elevationM": 0, "timezone": "Asia/Kolkata",
        })["event"]["sourceAdapters"]["varahamihiraFirmament"]
        self.assertEqual(result["status"], "COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED")
        self.assertEqual(result["classicalSection"], "UNKNOWN")
        self.assertFalse(result["sourceCertifiedClassifier"])
        self.assertIn("localHourAngleDeg", result["rawGeometry"])

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

    def test_g1_gazetteer_preserves_all_nine_source_triads_as_read_only_records(self) -> None:
        gazetteer = build_cgvo_historical_gazetteer(PROJECT_ROOT)
        expected_triads = {
            "CENTER": ["Krittika", "Rohini", "Mrigashirsha"],
            "EAST": ["Ardra", "Punarvasu", "Pushya"],
            "SOUTHEAST": ["Ashlesha", "Magha", "Purva Phalguni"],
            "SOUTH": ["Uttara Phalguni", "Hasta", "Chitra"],
            "SOUTHWEST": ["Swati", "Vishakha", "Anuradha"],
            "WEST": ["Jyeshtha", "Mula", "Purva Ashadha"],
            "NORTHWEST": ["Uttara Ashadha", "Shravana", "Dhanishtha"],
            "NORTH": ["Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada"],
            "NORTHEAST": ["Revati", "Ashwini", "Bharani"],
        }
        self.assertEqual(gazetteer["summary"]["totalSourceNames"], 308)
        self.assertEqual(gazetteer["schemaVersion"], 2)
        self.assertEqual(gazetteer["startingMaster"], "34659956d1de1ed44e307d0788938e67ac23f7bf")
        self.assertEqual(gazetteer["summary"]["byDirection"], {
            "CENTER": 32, "EAST": 33, "SOUTHEAST": 28, "SOUTH": 65,
            "SOUTHWEST": 29, "WEST": 19, "NORTHWEST": 15, "NORTH": 52,
            "NORTHEAST": 35,
        })
        self.assertEqual(set(gazetteer["summary"]["byDirection"]), set(expected_triads))
        self.assertFalse(gazetteer["guardrails"]["automaticRegionUnion"])
        self.assertFalse(gazetteer["guardrails"]["automaticRegionIntersection"])
        self.assertFalse(gazetteer["guardrails"]["executionAllowed"])
        for direction, triad in expected_triads.items():
            first = next(record for record in gazetteer["records"] if record["sourceDirectionGroup"] == direction)
            self.assertEqual(first["nakshatraTriad"], triad)

    def test_g1_gazetteer_candidate_records_require_evidence_and_remain_non_geometric(self) -> None:
        gazetteer = build_cgvo_historical_gazetteer(PROJECT_ROOT)
        records = gazetteer["records"]
        magadha = next(record for record in records if record["normalizedName"] == "MAGADHA")
        gandhara = next(record for record in records if record["normalizedName"] == "GANDHARA")
        kamboja = next(record for record in records if record["normalizedName"] == "KAMBOJA")
        mathuraka = next(record for record in records if record["normalizedName"] == "MATHURAKA")
        self.assertEqual(magadha["mappingStatus"], "HIGH_CONFIDENCE_CANDIDATE")
        self.assertEqual(gandhara["mappingStatus"], "HIGH_CONFIDENCE_CANDIDATE")
        self.assertEqual(kamboja["mappingStatus"], "CONTESTED_CANDIDATES")
        self.assertGreaterEqual(len(kamboja["candidateMappings"]), 2)
        self.assertEqual(kamboja["sourceNameTransliteration"], "Kāmboja")
        self.assertEqual(magadha["rawSourceCategory"], "UNKNOWN")
        self.assertEqual(magadha["rawSourceCategoryStatus"], "NOT_CLASSIFIED_FROM_ROOT_SOURCE")
        self.assertEqual(magadha["candidateEntityType"], "HISTORICAL_REGION")
        self.assertEqual(magadha["candidateEntityTypeStatus"], "RESEARCH_OVERLAY")
        self.assertEqual(mathuraka["sourceNameTransliteration"], "Māthuraka")
        self.assertEqual(mathuraka["sourceLiteralStatus"], "ROOT_SOURCE_NAME")
        self.assertEqual(mathuraka["rawSourceCategory"], "UNKNOWN")
        self.assertEqual(mathuraka["candidateEntityType"], "PEOPLE_OR_URBAN_ASSOCIATION")
        self.assertTrue(any(item["evidenceId"] == "G1_MATHURAKA_CH14_TRANSLATION_01" for item in mathuraka["candidateMappings"][0]["evidenceItems"]))
        self.assertTrue(any(item["evidenceId"] == "G1_MATHURAKA_LEXICAL_01" for item in mathuraka["candidateMappings"][0]["evidenceItems"]))
        self.assertTrue(all("Surasena centred" not in item["supports"] for item in mathuraka["candidateMappings"][0]["evidenceItems"]))
        self.assertEqual({
            "SOURCE_NAME_ONLY": gazetteer["summary"]["sourceNameOnly"],
            "HIGH_CONFIDENCE_CANDIDATE": gazetteer["summary"]["mappedHighConfidence"],
            "MEDIUM_CONFIDENCE_CANDIDATE": gazetteer["summary"]["mappedMediumConfidence"],
            "APPROXIMATE_REGION_ONLY": gazetteer["summary"]["approximateRegionOnly"],
            "CONTESTED_CANDIDATES": gazetteer["summary"]["contested"],
            "UNMAPPED": gazetteer["summary"]["unmapped"],
        }, {
            "SOURCE_NAME_ONLY": 297,
            "HIGH_CONFIDENCE_CANDIDATE": 6,
            "MEDIUM_CONFIDENCE_CANDIDATE": 3,
            "APPROXIMATE_REGION_ONLY": 1,
            "CONTESTED_CANDIDATES": 1,
            "UNMAPPED": 0,
        })
        mapped_names = [record["normalizedName"] for record in records if record["candidateMappings"]]
        self.assertEqual(len(mapped_names), 11)
        self.assertEqual(len(set(mapped_names)), 11)
        for record in records:
            self.assertTrue(record["sourceLocator"])
            self.assertNotIn("XIV.14.", record["sourceLocator"])
            self.assertNotIn("14.14.", record["sourceLocator"])
            self.assertEqual(record["rawSourceCategory"], "UNKNOWN")
            self.assertEqual(record["rawSourceCategoryStatus"], "NOT_CLASSIFIED_FROM_ROOT_SOURCE")
            self.assertIn(record["candidateEntityTypeStatus"], {"RESEARCH_OVERLAY", "NOT_ASSIGNED"})
            self.assertTrue(record["sourceDirectionGroup"])
            self.assertIn(record["mappingStatus"], {
                "SOURCE_NAME_ONLY", "HIGH_CONFIDENCE_CANDIDATE", "MEDIUM_CONFIDENCE_CANDIDATE",
                "CONTESTED_CANDIDATES", "APPROXIMATE_REGION_ONLY",
            })
            self.assertIn("MARKET_PROXY_SELECTION", record["prohibitedUses"])
            for mapping in record["candidateMappings"]:
                self.assertTrue(mapping["evidenceItems"])
                self.assertTrue(mapping["temporalApplicability"])
                self.assertNotEqual(mapping["geometryType"], "POLYGON")
                self.assertNotEqual(mapping["geometryStatus"], "EVIDENCE_BACKED")
                self.assertIsNone(mapping["geometry"])

    def test_g1_repeated_source_names_remain_distinct_contextual_occurrences(self) -> None:
        gazetteer = build_cgvo_historical_gazetteer(PROJECT_ROOT)
        mandavyas = [record for record in gazetteer["records"] if record["normalizedName"] == "MANDAVYA"]
        self.assertEqual(len(mandavyas), 3)
        self.assertEqual({record["sourceDirectionGroup"] for record in mandavyas}, {"CENTER", "NORTHWEST", "NORTH"})
        self.assertEqual(len({record["regionId"] for record in mandavyas}), 3)
        self.assertEqual(len({record["sourceLocator"] for record in mandavyas}), 3)
        center_mathuraka = next(record for record in gazetteer["records"] if record["regionId"] == "VARAHA_XIV_CENTER_MATHURAKA_14")
        self.assertEqual(center_mathuraka["sourceLocator"], "Brihat Samhita 14.2-14.4")

    def test_g1_keeps_geography_claim_layers_separate(self) -> None:
        gazetteer = build_cgvo_historical_gazetteer(PROJECT_ROOT)
        profiles = {profile["profileId"] for profile in gazetteer["sourceProfiles"]}
        self.assertEqual(profiles, {
            "VARAHAMIHIRA_KURMAVIBHAGA_XIV",
            "VARAHAMIHIRA_ECLIPSE_RASI_V",
            "VARAHAMIHIRA_NAKSHATRA_DEPENDENCIES_XV",
            "TRAILOKYA_GEOGRAPHY_PLACEHOLDER_G1",
        })
        self.assertFalse(gazetteer["aggregationPolicy"]["automaticUnion"])
        self.assertFalse(gazetteer["aggregationPolicy"]["automaticIntersection"])
        self.assertFalse(gazetteer["guardrails"]["priceDataRead"])
        self.assertFalse(gazetteer["guardrails"]["fieldsPath"])
        self.assertFalse(gazetteer["guardrails"]["sbcPath"])
        self.assertFalse(gazetteer["guardrails"]["autoSuggestPath"])
        self.assertFalse(gazetteer["guardrails"]["mlPath"])
        self.assertFalse(gazetteer["guardrails"]["mt5Path"])

    def test_g2_research_footprints_are_separate_from_g1_and_remain_downstream_locked(self) -> None:
        gazetteer = build_cgvo_historical_gazetteer(PROJECT_ROOT)
        footprints = build_cgvo_historical_research_footprints(PROJECT_ROOT)
        self.assertEqual(gazetteer["summary"]["totalSourceNames"], 308)
        self.assertTrue(all("geometry" in record and record["geometry"] is None for record in gazetteer["records"]))
        self.assertTrue(all(mapping["geometry"] is None for record in gazetteer["records"] for mapping in record["candidateMappings"]))
        self.assertEqual(footprints["contract"], "CGVO_HISTORICAL_GEOGRAPHY_RESEARCH_FOOTPRINTS_V1")
        self.assertEqual(footprints["milestone"], "CGVO-G2")
        self.assertEqual(footprints["sourceGazetteerBaseline"], "CGVO-G1-R1")
        self.assertEqual(footprints["geometryRole"], "RESEARCH_GEOMETRY_ONLY")
        self.assertEqual(footprints["summary"]["footprintCount"], 12)
        self.assertEqual(footprints["summary"]["reviewedCandidateTermCount"], 11)
        self.assertEqual(footprints["summary"]["coordinateBearingFootprintCount"], 0)
        self.assertEqual(footprints["summary"]["byGeometryStatus"], {
            "GEOMETRY_PENDING_EVIDENCE": 9,
            "CONTESTED_RESEARCH_GEOMETRIES": 2,
            "RESEARCH_CORRIDOR_OR_RIVER_SYSTEM": 1,
        })
        for key in ("automaticRegionUnion", "automaticRegionIntersection", "downstreamIntersectionAuthorized", "marketUseAllowed", "executionAllowed"):
            self.assertFalse(footprints["guardrails"][key])
        self.assertTrue(footprints["guardrails"]["researchGeometryOnly"])
        for footprint in footprints["footprints"]:
            self.assertEqual(footprint["geometryRole"], "RESEARCH_GEOMETRY_ONLY")
            self.assertFalse(footprint["downstreamIntersectionAuthorized"])
            self.assertFalse(footprint["marketUseAllowed"])
            self.assertFalse(footprint["executionAllowed"])
            self.assertTrue(footprint["sourceOccurrenceIds"])
            self.assertTrue(footprint["evidenceItems"])
            self.assertTrue(footprint["uncertainty"])
            self.assertTrue(footprint["temporalApplicability"])
            self.assertTrue(footprint["limitations"])
        self.assertNotIn("CINA", {footprint["normalizedName"] for footprint in footprints["footprints"]})
        self.assertNotIn("YAVANA", {footprint["normalizedName"] for footprint in footprints["footprints"]})
        mathuraka = next(item for item in footprints["footprints"] if item["normalizedName"] == "MATHURAKA")
        self.assertEqual(mathuraka["candidateEntityType"], "PEOPLE_OR_URBAN_ASSOCIATION")
        self.assertEqual(mathuraka["geometryStatus"], "GEOMETRY_PENDING_EVIDENCE")
        sindhu = next(item for item in footprints["footprints"] if item["normalizedName"] == "SINDHU")
        self.assertEqual(sindhu["geometryPrimitive"], "RIVER_SYSTEM_CONTEXT")
        self.assertIsNone(sindhu["geometryData"]["landPolygon"])
        self.assertIsNone(sindhu["geometryData"]["adjacentLandExtent"])
        kamboja = [item for item in footprints["footprints"] if item["normalizedName"] == "KAMBOJA"]
        self.assertEqual(len(kamboja), 2)
        self.assertEqual({item["contestedGroupId"] for item in kamboja}, {"G2_KAMBOJA_UNMERGED_ALTERNATIVES"})
        self.assertTrue(all(item["geometryData"]["separateAlternative"] for item in kamboja))
        self.assertTrue(all(item["geometryData"]["mergedGeometry"] is None for item in kamboja))

    def test_g2_validator_fails_closed_for_missing_footprint_evidence_or_merged_contested_geometry(self) -> None:
        policy = cgvo_service._load_json(PROJECT_ROOT, cgvo_service.GEOGRAPHY_G2_POLICY_FIXTURE)
        ledger = cgvo_service._load_json(PROJECT_ROOT, cgvo_service.KURMA_G2_FOOTPRINTS_FIXTURE)
        gazetteer = build_cgvo_historical_gazetteer(PROJECT_ROOT)
        missing_uncertainty = deepcopy(ledger)
        missing_uncertainty["footprints"][0]["uncertainty"] = {}
        with self.assertRaisesRegex(RuntimeError, "lacks uncertainty"):
            cgvo_service._validate_g2_research_footprints(policy, missing_uncertainty, gazetteer)
        merged_kamboja = deepcopy(ledger)
        merged_kamboja["footprints"][5]["geometryData"]["mergedGeometry"] = {"forbidden": True}
        with self.assertRaisesRegex(RuntimeError, "may not merge alternatives"):
            cgvo_service._validate_g2_research_footprints(policy, merged_kamboja, gazetteer)


if __name__ == "__main__":
    unittest.main()
