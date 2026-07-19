from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from market_synthesis import MARKET_SYNTHESIS_PACKET_CONTRACT, MarketSynthesisService


class Repository:
    def event_detail(self, event_id: str) -> dict:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        candles = []
        for index in range(36):
            close = 145 + index * 0.01
            candles.append({
                "time": int((start + timedelta(hours=index)).timestamp()),
                "open": close - 0.005,
                "high": close + 0.01,
                "low": close - 0.01,
                "close": close,
                "volume": 1,
            })
        return {
            "event": {
                "eventId": event_id,
                "caseId": 1,
                "familyKey": "MERCURY|MOON::trine",
                "pairKey": "MERCURY|MOON",
                "aspect": "trine",
                "aspectLabel": "Trine",
                "transitBody": "MERCURY",
                "natalBody": "MOON",
                "startIso": (start + timedelta(hours=20)).isoformat(),
                "endIso": (start + timedelta(hours=24)).isoformat(),
                "peakIso": (start + timedelta(hours=22)).isoformat(),
                "durationMinutes": 240,
                "peakOrbDeg": 0.2,
                "orbLimitDeg": 1.0,
                "returnPct": 9.9,
            },
            "chart": {"symbol": "USDJPY", "timeframe": "H1", "candles": candles},
            "astroEvidence": [
                {"key": "shadbala", "label": "Shadbala", "value": 321, "unit": "virupa", "certification": "provisional"},
                {"key": "ret_after_72h_pct", "label": "Future return", "value": 9.9, "unit": "pct", "certification": "observed"},
            ],
            "currencyPairEvidence": {"status": "provisional"},
            "evidenceCertifications": [],
            "annotations": [],
        }


class MarketSynthesisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = MarketSynthesisService(Repository())

    def test_packet_keeps_specialists_separate_and_excludes_labels(self) -> None:
        packet = self.service.packet("event-1")
        self.assertEqual(packet["contract"], MARKET_SYNTHESIS_PACKET_CONTRACT)
        self.assertIsNotNone(packet["astrology"])
        self.assertIsNotNone(packet["candlesticks"])
        self.assertIsNotNone(packet["rsi"])
        keys = [item["key"] for item in packet["astrology"]["astroEvidence"]]
        self.assertEqual(keys, ["shadbala"])
        self.assertNotIn("hindsight", packet["candlesticks"])
        self.assertTrue(packet["guardrails"]["retrospectiveOutcomeExcluded"])

    def test_packet_supports_explicit_specialist_selection(self) -> None:
        packet = self.service.packet(
            "event-1",
            include_astrology=True,
            include_candles=False,
            include_rsi=False,
        )
        self.assertIsNone(packet["candlesticks"])
        self.assertIsNone(packet["rsi"])
        with self.assertRaises(ValueError):
            self.service.packet(
                "event-1",
                include_astrology=False,
                include_candles=False,
                include_rsi=False,
            )

    def test_verifier_blocks_execution_language_and_excluded_inputs(self) -> None:
        packet = self.service.packet(
            "event-1",
            include_astrology=True,
            include_candles=False,
            include_rsi=False,
        )
        verifier = self.service._verify(
            "Direction hypothesis: bullish. Buy now because RSI is 30.",
            packet,
        )
        self.assertEqual(verifier["status"], "review_required")
        self.assertGreaterEqual(len(verifier["issues"]), 2)


if __name__ == "__main__":
    unittest.main()
