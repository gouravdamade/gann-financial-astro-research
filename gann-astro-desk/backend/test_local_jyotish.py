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
            {
                "source_id": "CHAKRA_DOCTRINE_AUDIT",
                "chunk_id": "CHAKRA-AUDIT-0001",
                "title": "Sudarshana recension audit",
                "text": "Sudarshana Chakra chapter numbering varies by later BPHS recension and must not be silently imported into the 1899 witness.",
            },
            {
                "source_id": "GANN_TUNNEL_1927",
                "chunk_id": "GANN-TUNNEL-0001",
                "title": "The Tunnel Thru the Air",
                "text": "The novel says a secret is veiled, but no particular planetary-line trading algorithm is thereby proven.",
            },
            {
                "source_id": "FINANCIAL_ASTRO_FORUM_HYPOTHESES",
                "chunk_id": "FORUM-HYPOTHESIS-0001",
                "title": "Planetary price line forum hypotheses",
                "text": "Forum planetary price line and radix claims are unverified hypotheses for prospective testing only.",
            },
            {
                "source_id": "AGARWAL_FINANCIAL_CHAPTER20_HYPOTHESIS_20260722",
                "chunk_id": "AGARWAL-FINANCIAL-0001",
                "title": "Astrological Norms for Financial Gain in Share Market",
                "text": "A modern practitioner proposes bullish and bearish share-market combinations for prospective testing only.",
            },
            {
                "source_id": "TRAILOKYA_DIPIKA_VYAS_1972_ENGLISH_STAGE1_20260723",
                "chunk_id": "TRAILOKYA-STAGE1-0001",
                "title": "Trailokya Dipika Stage 1 English Research Translation",
                "text": "PDF page 21 says Sun Moon Rahu and Ketu cast all three Vedha directions. This is an incomplete page-provenanced workspace research rendering.",
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

    def test_source_layers_keep_provenance_and_hypotheses_out_of_doctrine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalJyotishService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
            )
            provenance = service.retrieve(
                "Which Sudarshana BPHS recension is present?",
                layer="source_provenance",
            )
            hypotheses = service.retrieve(
                "Does the Gann Tunnel prove planetary price lines?",
                layer="hypothesis_reference",
            )
            doctrine = service.retrieve(
                "Does the Gann Tunnel prove planetary price lines?",
                layer="classical_doctrine",
            )
            self.assertEqual(provenance[0]["chunkId"], "CHAKRA-AUDIT-0001")
            self.assertTrue(any(
                item["chunkId"] == "GANN-TUNNEL-0001" for item in hypotheses
            ))
            self.assertFalse(any(item["chunkId"].startswith("GANN-") for item in doctrine))

            agarwal = service.retrieve(
                "Which Agarwal share market combinations are hypotheses?",
                layer="hypothesis_reference",
            )
            self.assertTrue(any(
                item["chunkId"] == "AGARWAL-FINANCIAL-0001" for item in agarwal
            ))

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
            self.assertFalse(any(item["layer"] == "hypothesis_reference" for item in result["citations"]))
            self.assertFalse(any(
                item["layer"] == "translated_source_reference"
                for item in result["citations"]
            ))

    def test_gann_hypothesis_is_opt_in_and_overclaim_requires_review(self) -> None:
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
                return {
                    "response": (
                        "The novel is proven classical doctrine for planetary price lines "
                        "[GANN-TUNNEL-0001]."
                    )
                }

            with patch.object(service, "_request_json", side_effect=fake_request):
                result = service.analyze(
                    "event-1",
                    "Does Gann's Tunnel Thru the Air prove planetary price lines?",
                )
            self.assertTrue(any(
                item["layer"] == "hypothesis_reference" for item in result["citations"]
            ))
            self.assertEqual(result["verifier"]["status"], "review_required")
            self.assertTrue(any(
                "hypothesis-reference" in issue for issue in result["verifier"]["issues"]
            ))

    def test_trailokya_translation_is_explicit_opt_in_and_overclaim_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = LocalJyotishService(
                FakeRepository(root),
                corpus_path=self.write_corpus(root),
                preferred_model="gemma4:12b",
            )

            ordinary = service.retrieve(
                "Explain Saturn square Moon and Shadbala.",
                layer="translated_source_reference",
            )
            self.assertTrue(any(
                item["chunkId"] == "TRAILOKYA-STAGE1-0001" for item in ordinary
            ))

            def fake_request(path: str, **_kwargs):
                if path == "/api/tags":
                    return {"models": [{"name": "gemma4:12b"}]}
                return {
                    "response": (
                        "This is a certified complete translation and proven ground truth "
                        "[TRAILOKYA-STAGE1-0001]."
                    )
                }

            with patch.object(service, "_request_json", side_effect=fake_request):
                result = service.analyze(
                    "event-1",
                    "What does Trailokya Dipika say about three-direction Vedha?",
                )
            self.assertTrue(any(
                item["layer"] == "translated_source_reference"
                for item in result["citations"]
            ))
            self.assertEqual(result["verifier"]["status"], "review_required")
            self.assertTrue(any(
                "translated research reference" in issue
                for issue in result["verifier"]["issues"]
            ))

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
