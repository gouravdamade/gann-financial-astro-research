from __future__ import annotations

import unittest
from unittest.mock import patch

from multi_oscillator_activity_service import build_multi_oscillator_activity_range


def _event(event_id: str, side: str, start: str, exact: str, end: str, body: str = "MARS", aspect: str = "SQUARE") -> dict:
    return {
        "eventId": event_id,
        "eventHash": f"hash-{event_id}",
        "sideIdentity": side,
        "instrumentIdentity": f"FX_CURRENCY:{side}",
        "chartId": f"{side.lower()}-chart",
        "chartHypothesisId": f"{side.lower()}-hypothesis",
        "transitBody": body,
        "natalTarget": "SUN",
        "aspectType": aspect,
        "applyingStartUtc": start,
        "exactUtc": exact,
        "separatingEndUtc": end,
        "polarity": None,
        "magnitude": None,
    }


def _event_range(side: str, events: list[dict], unknown_reasons: list[str] | None = None) -> dict:
    return {
        "contract": "CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1",
        "chartId": f"{side.lower()}-chart",
        "chartHypothesisId": f"{side.lower()}-hypothesis",
        "generatorHash": "event-universe-hash",
        "astronomyContract": "RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1",
        "historicalCivilTimeConversionPolicy": "ACCEPTED_HISTORICAL_CIVIL_TIME_V1",
        "ephemerisProvider": "Swiss Ephemeris",
        "ephemerisVersion": "test",
        "ayanamsha": "Raman",
        "nodePolicy": "TRUE_NODE",
        "generatorVersion": "test-generator",
        "events": events,
        "rejectedEvents": [],
        "unknownReasons": unknown_reasons or [],
    }


class MultiOscillatorActivityServiceTests(unittest.TestCase):
    def _request(self) -> dict:
        return {
            "rangeStartUtc": "2025-04-01T00:00:00Z",
            "rangeEndUtc": "2025-04-01T05:00:00Z",
            "sideIdentities": ["USD", "JPY"],
            "aspectProfileId": "ASPECT_STRENGTH_V0",
        }

    def test_segments_union_of_exact_half_open_event_boundaries(self) -> None:
        usd_events = [
            _event("usd-1", "USD", "2025-04-01T01:00:00Z", "2025-04-01T01:30:00Z", "2025-04-01T03:00:00Z"),
            _event("usd-2", "USD", "2025-04-01T02:00:00Z", "2025-04-01T02:30:00Z", "2025-04-01T04:00:00Z", body="VENUS", aspect="TRINE"),
        ]
        with patch(
            "multi_oscillator_activity_service.build_chart_conditioned_transit_event_range",
            side_effect=lambda payload: _event_range(
                payload["sideIdentity"],
                usd_events if payload["sideIdentity"] == "USD" else [],
            ),
        ):
            result = build_multi_oscillator_activity_range(self._request())

        usd = result["fields"]["USD"]
        self.assertEqual(
            [(item["startUtc"], item["endUtc"], item["rawActiveEventCount"], item["contributingEventIds"]) for item in usd["activityIntervals"]],
            [
                ("2025-04-01T00:00:00.000Z", "2025-04-01T01:00:00.000Z", 0, []),
                ("2025-04-01T01:00:00.000Z", "2025-04-01T02:00:00.000Z", 1, ["usd-1"]),
                ("2025-04-01T02:00:00.000Z", "2025-04-01T03:00:00.000Z", 2, ["usd-1", "usd-2"]),
                ("2025-04-01T03:00:00.000Z", "2025-04-01T04:00:00.000Z", 1, ["usd-2"]),
                ("2025-04-01T04:00:00.000Z", "2025-04-01T05:00:00.000Z", 0, []),
            ],
        )
        self.assertEqual(usd["coverage"], "KNOWN")
        self.assertEqual(result["guardrails"]["executionAllowed"], False)
        self.assertEqual(result["guardrails"]["pairDifferenceComputed"], False)
        self.assertEqual(usd["events"][0]["polarity"], None)
        self.assertEqual(usd["events"][0]["magnitude"], None)

    def test_successful_empty_compilation_is_known_zero_not_unknown(self) -> None:
        with patch(
            "multi_oscillator_activity_service.build_chart_conditioned_transit_event_range",
            side_effect=lambda payload: _event_range(payload["sideIdentity"], []),
        ):
            result = build_multi_oscillator_activity_range(self._request())

        for side in ("USD", "JPY"):
            self.assertEqual(result["fields"][side]["coverage"], "KNOWN")
            self.assertEqual(result["fields"][side]["activityIntervals"][0]["rawActiveEventCount"], 0)
            self.assertIsNone(result["fields"][side]["unknownReason"])

    def test_compiler_unknown_state_propagates_without_becoming_zero(self) -> None:
        with patch(
            "multi_oscillator_activity_service.build_chart_conditioned_transit_event_range",
            side_effect=lambda payload: _event_range(payload["sideIdentity"], [], ["EPHEMERIS_UNAVAILABLE"]),
        ):
            result = build_multi_oscillator_activity_range(self._request())

        self.assertEqual(result["fields"]["USD"]["coverage"], "UNKNOWN")
        self.assertEqual(result["fields"]["USD"]["activityIntervals"][0]["coverage"], "UNKNOWN")
        self.assertEqual(result["fields"]["USD"]["activityIntervals"][0]["rawActiveEventCount"], 0)
        self.assertEqual(result["fields"]["USD"]["unknownReason"], "EPHEMERIS_UNAVAILABLE")

    def test_client_cannot_inject_event_universe_or_pair_field(self) -> None:
        for key, value in (("bodyUniverse", ["PLUTO"]), ("events", []), ("pairRelative", True)):
            with self.subTest(key=key):
                request = self._request()
                request[key] = value
                with self.assertRaisesRegex(ValueError, "Unknown multi-oscillator activity"):
                    build_multi_oscillator_activity_range(request)

    def test_only_approved_aspect_profile_is_allowed(self) -> None:
        request = self._request()
        request["aspectProfileId"] = "INVENTED_PROFILE"
        with self.assertRaisesRegex(ValueError, "unsupported event universe profile"):
            build_multi_oscillator_activity_range(request)

    def test_signed_or_magnitude_compiler_output_fails_closed(self) -> None:
        signed = _event(
            "usd-signed",
            "USD",
            "2025-04-01T01:00:00Z",
            "2025-04-01T01:30:00Z",
            "2025-04-01T03:00:00Z",
        )
        signed["polarity"] = "SUPPORTIVE"
        with patch(
            "multi_oscillator_activity_service.build_chart_conditioned_transit_event_range",
            side_effect=lambda payload: _event_range(payload["sideIdentity"], [signed]),
        ):
            with self.assertRaisesRegex(ValueError, "signed or magnitude"):
                build_multi_oscillator_activity_range(self._request())


if __name__ == "__main__":
    unittest.main()
