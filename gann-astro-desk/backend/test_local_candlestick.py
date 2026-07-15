from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from local_candlestick import LOCAL_CANDLESTICK_CONTRACT, LocalCandlestickService


BASE = datetime(2026, 1, 5, tzinfo=timezone.utc)


class FakeRepository:
    def __init__(self, root: Path) -> None:
        self.paths = SimpleNamespace(project_root=root)

    def event_detail(self, event_id: str) -> dict:
        candles = []
        values = [
            (100.0, 100.8, 99.8, 100.5),
            (100.5, 100.7, 99.8, 100.0),
            (100.0, 100.2, 99.0, 99.2),
            (99.0, 100.6, 98.8, 100.4),
            (100.4, 100.7, 100.1, 100.2),
        ]
        for index, (open_, high, low, close) in enumerate(values):
            candles.append(
                {
                    "time": int((BASE + timedelta(hours=index)).timestamp()),
                    "open": open_,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": 100,
                }
            )
        return {
            "event": {
                "eventId": event_id,
                "startIso": (BASE + timedelta(hours=2)).isoformat(),
                "endIso": (BASE + timedelta(hours=4)).isoformat(),
            },
            "chart": {"symbol": "USDJPY", "timeframe": "H1", "candles": candles},
            "annotations": [],
        }


class LocalCandlestickTests(unittest.TestCase):
    def write_corpus(self, root: Path) -> Path:
        path = root / "corpus.jsonl"
        rows = [
            {
                "source_id": "TALIB_PATTERN_REFERENCE",
                "chunk_id": "TALIB_PATTERN_REFERENCE-0001",
                "title": "Transparent candlestick geometry",
                "text": "Geometry and preceding trend must be recorded separately for engulfing and wick patterns.",
            },
            {
                "source_id": "CANDLESTICK_EMPIRICAL_EVIDENCE",
                "chunk_id": "CANDLESTICK_EMPIRICAL_EVIDENCE-0001",
                "title": "Mixed empirical evidence",
                "text": "Profitability depends on market, trend definition, holding strategy, and transaction costs.",
            },
            {
                "source_id": "CANDLESTICK_METHOD_AUDIT",
                "chunk_id": "CANDLESTICK_METHOD_AUDIT-0001",
                "title": "Source and method audit",
                "text": "The transparent detector does not claim TA-Lib parity and is analysis only.",
            },
        ]
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        return path

    def test_evidence_is_available_without_an_llm_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalCandlestickService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
            )
            with patch.object(service, "_request_json", side_effect=OSError("offline")):
                health = service.health()
                evidence = service.evidence("event-1")
            self.assertFalse(health["ready"])
            self.assertTrue(health["corpusReady"])
            self.assertEqual(evidence["eventId"], "event-1")
            self.assertFalse(evidence["guardrails"]["executionAllowed"])

    def test_retrieval_keeps_method_empirical_and_provenance_layers_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalCandlestickService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
            )
            method = service.retrieve("engulfing geometry trend", layer="method_reference")
            evidence = service.retrieve("holding strategy costs", layer="empirical_evidence")
            provenance = service.retrieve("TA-Lib parity", layer="source_provenance")
            self.assertEqual(method[0]["chunkId"], "TALIB_PATTERN_REFERENCE-0001")
            self.assertEqual(evidence[0]["chunkId"], "CANDLESTICK_EMPIRICAL_EVIDENCE-0001")
            self.assertEqual(provenance[0]["chunkId"], "CANDLESTICK_METHOD_AUDIT-0001")

    def test_analyze_returns_separate_guarded_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalCandlestickService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
                preferred_model="qwen2.5:3b",
            )

            def fake_request(path: str, **_kwargs):
                if path == "/api/tags":
                    return {"models": [{"name": "qwen2.5:3b"}]}
                return {
                    "response": (
                        "Observed OHLC: the focus bar has bullish body-engulfing geometry. "
                        "Pattern context is conditional [TALIB_PATTERN_REFERENCE-0001]. "
                        "Published evidence is mixed [CANDLESTICK_EMPIRICAL_EVIDENCE-0001]."
                    )
                }

            with patch.object(service, "_request_json", side_effect=fake_request):
                result = service.analyze("event-1", "Explain the focus-bar geometry.")
            self.assertEqual(result["contract"], LOCAL_CANDLESTICK_CONTRACT)
            self.assertEqual(result["verifier"]["status"], "pass")
            self.assertFalse(result["guardrails"]["consumedByLiveInference"])
            self.assertFalse(result["guardrails"]["consumedByShadowLedger"])
            self.assertFalse(result["guardrails"]["executionAllowed"])

    def test_verifier_rejects_execution_overclaim_and_false_talib_parity(self) -> None:
        evidence = {
            "focusBar": {"patterns": []},
        }
        sources = [
            {
                "chunkId": "TALIB_PATTERN_REFERENCE-0001",
                "sourceId": "TALIB_PATTERN_REFERENCE",
                "title": "Method",
                "layer": "method_reference",
                "score": 1.0,
            }
        ]
        verifier = LocalCandlestickService._verify_draft(
            "TA-Lib confirmed parity. The current bar is a hammer, so buy now [TALIB_PATTERN_REFERENCE-0001].",
            evidence,
            sources,
        )
        self.assertEqual(verifier["status"], "review_required")
        self.assertGreaterEqual(len(verifier["issues"]), 3)

    def test_missing_model_citations_get_a_visible_deterministic_footer(self) -> None:
        sources = [
            {
                "chunkId": "TALIB_PATTERN_REFERENCE-0001",
                "sourceId": "TALIB_PATTERN_REFERENCE",
                "title": "Method",
                "layer": "method_reference",
                "score": 1.0,
            },
            {
                "chunkId": "CANDLESTICK_EMPIRICAL_EVIDENCE-0001",
                "sourceId": "CANDLESTICK_EMPIRICAL_EVIDENCE",
                "title": "Evidence",
                "layer": "empirical_evidence",
                "score": 1.0,
            },
        ]
        text, repairs = LocalCandlestickService._ensure_source_footer(
            "Named patterns are not universally predictive.",
            sources,
        )
        verifier = LocalCandlestickService._verify_draft(
            text,
            {"focusBar": {"patterns": []}},
            sources,
        )
        self.assertTrue(repairs)
        self.assertIn("[TALIB_PATTERN_REFERENCE-0001]", text)
        self.assertIn("[CANDLESTICK_EMPIRICAL_EVIDENCE-0001]", text)
        self.assertEqual(verifier["status"], "pass")

    def test_verifier_requires_both_method_and_empirical_citation_layers(self) -> None:
        sources = [
            {
                "chunkId": "TALIB_PATTERN_REFERENCE-0001",
                "sourceId": "TALIB_PATTERN_REFERENCE",
                "title": "Method",
                "layer": "method_reference",
                "score": 1.0,
            },
            {
                "chunkId": "CANDLESTICK_EMPIRICAL_EVIDENCE-0001",
                "sourceId": "CANDLESTICK_EMPIRICAL_EVIDENCE",
                "title": "Evidence",
                "layer": "empirical_evidence",
                "score": 1.0,
            },
        ]
        verifier = LocalCandlestickService._verify_draft(
            "The geometry is conditional [TALIB_PATTERN_REFERENCE-0001].",
            {"focusBar": {"patterns": []}},
            sources,
        )
        self.assertEqual(verifier["status"], "review_required")
        self.assertIn(
            "Draft did not cite a retrieved empirical-evidence passage.",
            verifier["issues"],
        )


if __name__ == "__main__":
    unittest.main()
