from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from rsi_analysis import RSI_EVIDENCE_CONTRACT, build_rsi_evidence, wilder_rsi_values


def detail(closes: list[float], *, event_start_index: int = 15, event_end_index: int = 20) -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    candles = [
        {
            "time": int((start + timedelta(hours=index)).timestamp()),
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": 1,
        }
        for index, close in enumerate(closes)
    ]
    return {
        "event": {
            "eventId": "event-rsi-1",
            "startIso": (start + timedelta(hours=event_start_index)).isoformat(),
            "endIso": (start + timedelta(hours=event_end_index)).isoformat(),
        },
        "chart": {"symbol": "USDJPY", "timeframe": "H1", "candles": candles},
        "annotations": [],
    }


class WilderRsiTests(unittest.TestCase):
    def test_monotonic_series_reaches_expected_limits(self) -> None:
        self.assertEqual(wilder_rsi_values(range(20), 14)[-1], 100.0)
        self.assertEqual(wilder_rsi_values(range(20, 0, -1), 14)[-1], 0.0)
        self.assertEqual(wilder_rsi_values([10.0] * 20, 14)[-1], 50.0)

    def test_requires_period_plus_one_closes(self) -> None:
        self.assertTrue(all(value is None for value in wilder_rsi_values(range(14), 14)))
        self.assertIsNotNone(wilder_rsi_values(range(15), 14)[-1])

    def test_rejects_unsupported_period(self) -> None:
        with self.assertRaises(ValueError):
            wilder_rsi_values([1, 2, 3], 1)


class RsiEvidenceTests(unittest.TestCase):
    def test_packet_is_closed_bar_timestamp_safe(self) -> None:
        evidence = build_rsi_evidence(detail([100 + index for index in range(30)]), period=14)
        self.assertEqual(evidence["contract"], RSI_EVIDENCE_CONTRACT)
        self.assertEqual(evidence["closedBarCountAtCutoff"], 20)
        self.assertEqual(evidence["focus"]["barCloseTime"], "2026-01-01T20:00:00+00:00")
        self.assertEqual(evidence["focus"]["value"], 100.0)
        self.assertTrue(evidence["guardrails"]["closedBarsOnlyAtCutoff"])
        self.assertFalse(evidence["guardrails"]["consumedByLiveInference"])

    def test_annotation_moves_cutoff_without_using_later_bars(self) -> None:
        payload = detail([100 + index for index in range(30)])
        payload["annotations"] = [{
            "annotationId": "annotation-1",
            "anchorTimeUtc": "2026-01-01T17:30:00+00:00",
        }]
        evidence = build_rsi_evidence(payload, "annotation-1", period=14)
        self.assertEqual(evidence["closedBarCountAtCutoff"], 17)
        self.assertEqual(evidence["focus"]["barCloseTime"], "2026-01-01T17:00:00+00:00")
        self.assertEqual(evidence["selectedAnnotationId"], "annotation-1")

    def test_custom_levels_are_validated_and_sorted(self) -> None:
        evidence = build_rsi_evidence(
            detail([100 + index for index in range(30)]),
            period=14,
            levels=[70, "50", -1, 30, 70, 101],
        )
        self.assertEqual(evidence["levels"], [30.0, 50.0, 70.0])


if __name__ == "__main__":
    unittest.main()
