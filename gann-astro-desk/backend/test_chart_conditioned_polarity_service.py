from __future__ import annotations

import unittest
from unittest.mock import patch

from chart_conditioned_polarity_service import (
    build_chart_conditioned_polarity_lookup,
    build_chart_conditioned_polarity_range,
)


def _compiled_event_range(side: str = "USD") -> dict:
    return {
        "contract": "CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1",
        "sideIdentity": side,
        "instrumentIdentity": f"FX_CURRENCY:{side}",
        "chartId": f"{side}-CANONICAL-CHART",
        "chartHypothesisId": f"{side}-CANONICAL-HYPOTHESIS",
        "rangeStartUtc": "2026-08-02T00:00:00Z",
        "rangeEndUtc": "2026-08-02T01:00:00Z",
        "aspectProfileId": "ASPECT_STRENGTH_V0",
        "astronomyContract": "RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1",
        "ephemerisVersion": "test",
        "ayanamsha": "Raman",
        "nodePolicy": "TRUE_NODE_RAHU_KETU_OPPOSITION_V1",
        "generatorVersion": "test-generator",
        "generatorHash": "TEST-GENERATOR-HASH",
        "events": [
            {
                "eventId": "TN_REAL_ASTRONOMY_EVENT",
                "startUtc": "2026-08-02T00:10:00Z",
                "endUtc": "2026-08-02T00:40:00Z",
                "transitBody": "MARS",
                "natalTarget": "SUN",
                "aspectType": "square",
            }
        ],
        "rejectedEvents": [],
        "unknownReasons": [],
    }


class ChartConditionedPolarityServiceTests(unittest.TestCase):
    def test_currency_side_returns_explicit_missing_state(self) -> None:
        result = build_chart_conditioned_polarity_lookup({"instrumentIdentity": "FX_CURRENCY:USD"})

        self.assertEqual(result["lookupState"], "POLARITY_CATALOGUE_MISSING")
        self.assertIsNone(result["entry"])
        self.assertEqual(result["sideIdentity"], "USD")
        self.assertEqual(result["magnitudeState"], "MAGNITUDE_NOT_CONFIGURED")
        self.assertFalse(result["guardrails"]["executionAllowed"])
        self.assertFalse(result["guardrails"]["actsAsSbcConfirmation"])

    def test_unknown_fields_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown chart-conditioned polarity"):
            build_chart_conditioned_polarity_lookup({
                "instrumentIdentity": "FX_CURRENCY:USD",
                "score": 9,
            })

    def test_partial_event_context_is_reported_not_inferred(self) -> None:
        result = build_chart_conditioned_polarity_lookup({
            "instrumentIdentity": "FX_CURRENCY:USD",
            "chartId": "USD-TEST",
        })

        self.assertEqual(result["lookupState"], "TARGET_CONTEXT_INCOMPLETE")
        self.assertIsNone(result["entry"])

    def test_pair_is_rejected_as_primary_lookup(self) -> None:
        result = build_chart_conditioned_polarity_lookup({"instrumentIdentity": "FX_PAIR:USDJPY"})

        self.assertEqual(result["lookupState"], "PAIR_DERIVATION_ONLY")
        self.assertIsNone(result["entry"])

    def test_real_backend_event_boundaries_create_unknown_segments_before_review(self) -> None:
        with patch(
            "chart_conditioned_polarity_service.build_chart_conditioned_transit_event_range",
            return_value=_compiled_event_range(),
        ) as compiler:
            result = build_chart_conditioned_polarity_range({
                "sideIdentity": "USD",
                "rangeStartUtc": "2026-08-02T00:00:00Z",
                "rangeEndUtc": "2026-08-02T01:00:00Z",
                "aspectProfileId": "ASPECT_STRENGTH_V0",
            })

        compiler.assert_called_once()
        self.assertEqual(len(result["intervals"]), 3)
        active = result["intervals"][1]
        self.assertEqual(active["polarityState"], "UNKNOWN")
        self.assertEqual(active["unknownEventIds"], ["TN_REAL_ASTRONOMY_EVENT"])
        self.assertEqual(result["eventCompiler"]["eventCount"], 1)
        self.assertFalse(result["guardrails"]["executionAllowed"])

    def test_frontend_event_or_chart_identity_injection_is_rejected(self) -> None:
        for forbidden in ("events", "chartId", "chartHypothesisId", "instrumentIdentity"):
            with self.subTest(forbidden=forbidden):
                with self.assertRaisesRegex(ValueError, "Unknown chart-conditioned polarity range"):
                    build_chart_conditioned_polarity_range({
                        "sideIdentity": "USD",
                        "rangeStartUtc": "2026-08-02T00:00:00Z",
                        "rangeEndUtc": "2026-08-02T01:00:00Z",
                        forbidden: [] if forbidden == "events" else "INVENTED",
                    })


if __name__ == "__main__":
    unittest.main()
