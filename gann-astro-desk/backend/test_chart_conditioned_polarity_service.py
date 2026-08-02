from __future__ import annotations

import unittest

from chart_conditioned_polarity_service import build_chart_conditioned_polarity_lookup


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
