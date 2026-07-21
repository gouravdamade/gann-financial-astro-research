from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from candlestick_analysis import (
    CANDLESTICK_EVIDENCE_CONTRACT,
    build_candlestick_bar_records,
    build_candlestick_evidence,
)


BASE = datetime(2026, 1, 5, tzinfo=timezone.utc)


def candle(offset: int, open_: float, high: float, low: float, close: float) -> dict[str, float | int]:
    return {
        "time": int((BASE + timedelta(hours=offset)).timestamp()),
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": 100,
    }


def detail(annotation_time: datetime | None = None) -> dict:
    annotations = []
    if annotation_time is not None:
        annotations.append(
            {
                "annotationId": "annotation-1",
                "anchorTimeUtc": annotation_time.isoformat(),
            }
        )
    return {
        "event": {
            "eventId": "event-1",
            "startIso": (BASE + timedelta(hours=2)).isoformat(),
            "endIso": (BASE + timedelta(hours=4)).isoformat(),
        },
        "chart": {
            "symbol": "USDJPY",
            "timeframe": "H1",
            "candles": [
                candle(0, 100.0, 100.8, 99.8, 100.5),
                candle(1, 100.5, 100.7, 99.8, 100.0),
                candle(2, 100.0, 100.2, 99.0, 99.2),
                candle(3, 99.0, 100.6, 98.8, 100.4),
                candle(4, 100.4, 100.7, 100.1, 100.2),
                candle(5, 100.2, 101.0, 100.0, 100.9),
            ],
        },
        "annotations": annotations,
    }


class CandlestickEvidenceTests(unittest.TestCase):
    def test_focus_bar_uses_only_closed_bars_and_detects_transparent_geometry(self) -> None:
        evidence = build_candlestick_evidence(detail())
        names = {item["name"] for item in evidence["focusBar"]["patterns"]}
        self.assertEqual(evidence["contract"], CANDLESTICK_EVIDENCE_CONTRACT)
        self.assertEqual(evidence["focusBar"]["closeTime"], (BASE + timedelta(hours=4)).isoformat())
        self.assertIn("bullish_body_engulfing", names)
        self.assertEqual(evidence["eventWindow"]["barCount"], 2)
        self.assertTrue(evidence["guardrails"]["closedBarsOnlyAtCutoff"])
        self.assertFalse(evidence["guardrails"]["consumedByLiveInference"])

    def test_annotation_cutoff_excludes_the_still_open_selected_bar(self) -> None:
        cutoff = BASE + timedelta(hours=3)
        evidence = build_candlestick_evidence(detail(cutoff), "annotation-1")
        self.assertEqual(evidence["analysisCutoff"], cutoff.isoformat())
        self.assertEqual(evidence["focusBar"]["startTime"], (BASE + timedelta(hours=2)).isoformat())
        self.assertEqual(evidence["closedBarCountAtCutoff"], 3)

    def test_future_bars_are_separate_and_explicitly_hindsight(self) -> None:
        evidence = build_candlestick_evidence(detail())
        self.assertTrue(evidence["hindsight"]["available"])
        self.assertIn("Retrospective only", evidence["hindsight"]["label"])
        self.assertEqual(evidence["hindsight"]["barCount"], 2)
        self.assertTrue(evidence["guardrails"]["hindsightSeparated"])

    def test_invalid_ohlc_is_rejected(self) -> None:
        payload = detail()
        payload["chart"]["candles"] = [candle(0, 100.0, 99.0, 98.0, 100.5)]
        with self.assertRaisesRegex(ValueError, "No valid OHLC"):
            build_candlestick_evidence(payload)

    def test_bar_records_are_transparent_ohlc_features(self) -> None:
        records = build_candlestick_bar_records(
            detail()["chart"]["candles"],
            symbol="USDJPY",
            timeframe="H1",
        )
        self.assertEqual(len(records), 6)
        self.assertEqual(records[0]["startTime"], BASE.isoformat())
        self.assertEqual(records[0]["closeTime"], (BASE + timedelta(hours=1)).isoformat())
        self.assertEqual(records[0]["direction"], "bullish")
        self.assertIn("patterns", records[3])
        self.assertGreater(records[3]["rangePips"], 0)


if __name__ == "__main__":
    unittest.main()
