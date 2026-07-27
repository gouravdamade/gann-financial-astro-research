from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from planetary_lines import (
    PLANETARY_LINE_CONTRACT,
    build_planetary_line_overlay,
)


def deterministic_longitude(
    planet: str,
    dates: object,
    astrology_method: str = "tropical",
    coordinate_system: str = "geo",
) -> pd.Series:
    index = pd.DatetimeIndex(dates)
    values = [30.0 + position * 30.0 for position in range(len(index))]
    return pd.Series(values, index=index, dtype=float)


class PlanetaryLineOverlayTests(unittest.TestCase):
    def request(self) -> dict:
        return {
            "symbol": "USDJPY",
            "timeframe": "H1",
            "timestamps": [1_700_000_000, 1_700_003_600],
            "groups": [
                {
                    "planet": "MARS",
                    "enabled": True,
                    "color": "#ef8354",
                    "mode": "both",
                    "nValues": [2],
                    "fValues": [0.5],
                    "degrees": [180],
                }
            ],
        }

    @patch("planetary_lines.fetch_planetary_longitude", deterministic_longitude)
    def test_direct_and_mirror_lines_use_canonical_formula(self) -> None:
        overlay = build_planetary_line_overlay(self.request())

        self.assertEqual(overlay["contract"], PLANETARY_LINE_CONTRACT)
        self.assertEqual(overlay["lineCount"], 2)
        direct = next(line for line in overlay["lines"] if line["mode"] == "direct")
        mirror = next(line for line in overlay["lines"] if line["mode"] == "mirror")
        self.assertEqual([point["value"] for point in direct["points"]], [195.0, 210.0])
        self.assertEqual([point["value"] for point in mirror["points"]], [345.0, 330.0])
        self.assertTrue(overlay["guardrails"]["researchOnly"])
        self.assertFalse(overlay["guardrails"]["consumedByLiveInference"])
        self.assertFalse(overlay["guardrails"]["executionAllowed"])
        self.assertIsNone(overlay["collectiveField"])

    @patch("planetary_lines.fetch_planetary_longitude", deterministic_longitude)
    def test_avg_all_adds_context_only_collective_geometry(self) -> None:
        request = self.request()
        request["groups"] = [
            {
                "planet": "AVG(ALL)",
                "enabled": True,
                "color": "#f2e96b",
                "mode": "direct",
                "nValues": [2],
                "fValues": [0.5],
                "degrees": [180],
            }
        ]
        overlay = build_planetary_line_overlay(request)
        collective = overlay["collectiveField"]

        self.assertIsNotNone(collective)
        self.assertEqual(collective["latest"]["state"], "CONCENTRATED")
        self.assertEqual(collective["latest"]["coherenceR1"], 1.0)
        self.assertTrue(collective["legacyCompatibility"]["legacyLineValuesPreserved"])
        self.assertEqual(collective["evidence"]["role"], "CONTEXT_ONLY")
        self.assertEqual(
            collective["motion"]["contract"],
            "GANN_PLANETARY_COLLECTIVE_MOTION_V1",
        )
        self.assertEqual(
            collective["eventSummary"]["eventPolicy"]["profileId"],
            "AVG_ALL_SAMPLED_EVENTS_V1",
        )
        self.assertEqual(
            collective["causalClusterPolicy"]["directionalContribution"],
            0.0,
        )
        self.assertFalse(collective["guardrails"]["consumedByAutoSuggest"])
        self.assertFalse(collective["guardrails"]["consumedByShadowLedger"])
        self.assertFalse(collective["guardrails"]["executionAllowed"])

    @patch("planetary_lines.fetch_planetary_longitude", deterministic_longitude)
    def test_disabled_planets_do_not_trigger_calculation(self) -> None:
        request = self.request()
        request["groups"][0]["enabled"] = False
        overlay = build_planetary_line_overlay(request)
        self.assertEqual(overlay["lineCount"], 0)
        self.assertEqual(overlay["pointCount"], 0)

    def test_oversized_cartesian_product_fails_closed(self) -> None:
        request = self.request()
        request["groups"][0].update(
            {
                "mode": "direct",
                "nValues": list(range(1, 13)),
                "fValues": list(range(1, 13)),
                "degrees": [180],
            }
        )
        with self.assertRaisesRegex(ValueError, "Requested 144 lines"):
            build_planetary_line_overlay(request)

    def test_unknown_request_fields_fail_closed(self) -> None:
        request = self.request()
        request["executionAllowed"] = True
        with self.assertRaisesRegex(ValueError, "Unknown planetary line request"):
            build_planetary_line_overlay(request)


if __name__ == "__main__":
    unittest.main()
