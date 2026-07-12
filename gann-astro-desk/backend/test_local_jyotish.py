from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from local_jyotish import LOCAL_JYOTISH_CONTRACT, LocalJyotishService


class FakeRepository:
    def __init__(self, root: Path) -> None:
        self.paths = SimpleNamespace(project_root=root)

    def codex_context(self, event_id: str, annotation_id: str | None = None):
        return {
            "event": {
                "eventId": event_id,
                "familyKey": "TN::SATURN->MOON::square",
                "transitBody": "SATURN",
                "natalBody": "MOON",
                "aspectLabel": "Square",
            },
            "selectedAnnotation": {"annotationId": annotation_id} if annotation_id else None,
            "annotations": [],
            "astroEvidence": [
                {"key": "strict_shadbala", "label": "Shadbala", "value": 382.5},
            ],
            "deterministicContext": {"event_b2_sign_relation": "enemy"},
            "guardrails": {"analysisOnly": True, "mt5OrderPlacementAllowed": False},
        }


class LocalJyotishTests(unittest.TestCase):
    def write_corpus(self, root: Path) -> Path:
        path = root / "corpus.jsonl"
        rows = [
            {
                "source_id": "BPHS",
                "chunk_id": "BPHS-0123",
                "title": "Shadbala and planetary strength",
                "text": "Shadbala measures sixfold planetary strength and must be judged with dignity.",
            },
            {
                "source_id": "PHALA",
                "chunk_id": "PHALA-0042",
                "title": "Saturn and the Moon",
                "text": "Saturn and Moon conditions require house, dignity, and aspect context.",
            },
        ]
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        return path

    def test_retrieval_prefers_matching_doctrine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalJyotishService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
            )
            results = service.retrieve("How should strict Shadbala strength be judged?", limit=2)
            self.assertEqual(results[0]["chunkId"], "BPHS-0123")

    def test_analyze_returns_guarded_untrusted_draft_with_citations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalJyotishService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
                preferred_model="gemma4:12b",
            )

            def fake_request(path: str, **_kwargs):
                if path == "/api/tags":
                    return {"models": [{"name": "gemma4:12b"}]}
                return {"response": "Observed evidence is deterministic. Doctrine hint [BPHS-0123]."}

            with patch.object(service, "_request_json", side_effect=fake_request):
                result = service.analyze(
                    "event-1",
                    "Explain Saturn square Moon and Shadbala.",
                    "annotation-1",
                )
            self.assertEqual(result["contract"], LOCAL_JYOTISH_CONTRACT)
            self.assertEqual(result["model"], "gemma4:12b")
            self.assertFalse(result["guardrails"]["rawDraftIsOfficial"])
            self.assertFalse(result["guardrails"]["consumedByLiveInference"])
            self.assertFalse(result["guardrails"]["consumedByShadowLedger"])
            self.assertFalse(result["guardrails"]["executionAllowed"])
            self.assertTrue(any(item["chunkId"] == "BPHS-0123" for item in result["citations"]))

    def test_health_is_offline_when_runtime_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalJyotishService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
            )
            with patch.object(service, "_request_json", side_effect=OSError("offline")):
                health = service.health()
            self.assertFalse(health["ready"])
            self.assertFalse(health["runtimeReady"])
            self.assertTrue(health["corpusReady"])
            self.assertFalse(health["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
