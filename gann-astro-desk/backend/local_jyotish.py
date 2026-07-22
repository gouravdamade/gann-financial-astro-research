from __future__ import annotations

import json
import math
import os
import re
import threading
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


LOCAL_JYOTISH_CONTRACT = "GANN_LOCAL_JYOTISH_RAG_DRAFT_V1"
TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]{1,}")
STOP_WORDS = {
    "about", "after", "also", "and", "are", "been", "before", "between", "case",
    "chart", "could", "does", "event", "explain", "for", "from", "have", "into", "its",
    "more", "not", "occurrence", "our", "should", "that", "the", "their", "this", "through",
    "using", "was", "were", "what", "when", "which", "with", "would", "you",
}

CLASSICAL_DOCTRINE_SOURCES = {
    "BPHS",
    "BRIHAT_JATAKA",
    "BRIHAT_SAMHITA",
    "PHALADEEPIKA",
    "SURYA_SIDDHANTA",
}
REFERENCE_COMMENTARY_SOURCES = {
    "SHADBALA_JAYA",
    "STRICT_VEDIC_LLM",
    "SANJAY_RATH_CRUX_1998",
}
SOURCE_PROVENANCE_SOURCES = {"CHAKRA_DOCTRINE_AUDIT"}
HYPOTHESIS_REFERENCE_SOURCES = {
    "AGARWAL_FINANCIAL_CHAPTER20_HYPOTHESIS_20260722",
    "GANN_TUNNEL_1927",
    "FINANCIAL_ASTRO_FORUM_HYPOTHESES",
}
HYPOTHESIS_QUERY_TERMS = {
    "agarwal",
    "bullish market",
    "bearish market",
    "financial astrology",
    "forex factory",
    "forum",
    "gann",
    "planetary line",
    "planetary price",
    "radix",
    "sarvatobhadra",
    "share market",
    "tunnel thru the air",
    "tunnel through the air",
}


def _tokens(value: str) -> set[str]:
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(str(value or ""))
        if token.lower() not in STOP_WORDS
    }


def _source_layer(source_id: str) -> str:
    normalized = str(source_id or "").upper()
    if normalized in {"CURRENT_RULE_NOTES", "TOUCH_LOG"} or normalized.startswith(
        ("CASE_", "DREAM_", "RULE_", "REVIEW_", "ML_")
    ):
        return "local_research"
    if normalized in CLASSICAL_DOCTRINE_SOURCES:
        return "classical_doctrine"
    if normalized in REFERENCE_COMMENTARY_SOURCES:
        return "reference_commentary"
    if normalized in SOURCE_PROVENANCE_SOURCES:
        return "source_provenance"
    if normalized in HYPOTHESIS_REFERENCE_SOURCES:
        return "hypothesis_reference"
    return "unclassified_reference"


def _query_requests_hypotheses(query: str) -> bool:
    normalized = " ".join(str(query or "").lower().split())
    return any(term in normalized for term in HYPOTHESIS_QUERY_TERMS)


class LocalJyotishService:
    """Local Ollama + classical-corpus RAG drafting service.

    Drafts are never persisted as official notes and are not consumed by live inference or
    the prospective ledger. Deterministic application context remains ground truth.
    """

    def __init__(
        self,
        repository: Any,
        *,
        corpus_path: Path | None = None,
        endpoint: str | None = None,
        preferred_model: str | None = None,
        diagnostics: Any | None = None,
    ) -> None:
        self.repository = repository
        self.diagnostics = diagnostics
        default_corpus = repository.paths.project_root / "jyotish_agent" / "corpus_chunks.jsonl"
        self.corpus_path = Path(
            corpus_path
            or os.environ.get("GANN_ASTRO_JYOTISH_CORPUS")
            or default_corpus
        ).expanduser().resolve()
        self.endpoint = str(
            endpoint
            or os.environ.get("GANN_ASTRO_OLLAMA_URL")
            or "http://127.0.0.1:11434"
        ).rstrip("/")
        self.preferred_model = str(
            preferred_model
            or os.environ.get("GANN_ASTRO_LOCAL_LLM_MODEL")
            or "qwen2.5:3b"
        ).strip()
        self._corpus_lock = threading.RLock()
        self._chunks: list[dict[str, Any]] | None = None
        self._document_frequency: Counter[str] = Counter()

    def _load_corpus(self) -> list[dict[str, Any]]:
        with self._corpus_lock:
            if self._chunks is not None:
                return self._chunks
            if not self.corpus_path.is_file():
                self._chunks = []
                return self._chunks
            chunks: list[dict[str, Any]] = []
            frequency: Counter[str] = Counter()
            for line in self.corpus_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                text = str(row.get("text") or "").strip()
                if not text:
                    continue
                title = str(row.get("title") or row.get("source_id") or "Local source")
                token_set = _tokens(f"{title} {text}")
                if not token_set:
                    continue
                frequency.update(token_set)
                chunks.append(
                    {
                        "sourceId": str(row.get("source_id") or "LOCAL"),
                        "chunkId": str(row.get("chunk_id") or f"LOCAL-{len(chunks) + 1:05d}"),
                        "title": title,
                        "layer": _source_layer(str(row.get("source_id") or "LOCAL")),
                        "text": text,
                        "tokens": token_set,
                        "titleTokens": _tokens(title),
                    }
                )
            self._chunks = chunks
            self._document_frequency = frequency
            return chunks

    def retrieve(
        self,
        query: str,
        limit: int = 6,
        layer: str | None = None,
    ) -> list[dict[str, Any]]:
        chunks = self._load_corpus()
        query_tokens = _tokens(query)
        if not chunks or not query_tokens:
            return []
        total = len(chunks)
        scored: list[tuple[float, dict[str, Any]]] = []
        for chunk in chunks:
            if layer and chunk["layer"] != layer:
                continue
            overlap = query_tokens & chunk["tokens"]
            if not overlap:
                continue
            score = sum(
                1.0 + math.log((total + 1) / (self._document_frequency[token] + 1))
                for token in overlap
            )
            score += 1.5 * len(query_tokens & chunk["titleTokens"])
            score /= math.sqrt(max(1, len(chunk["tokens"])))
            scored.append((score, chunk))
        scored.sort(key=lambda item: (-item[0], item[1]["chunkId"]))
        return [
            {
                "sourceId": chunk["sourceId"],
                "chunkId": chunk["chunkId"],
                "title": chunk["title"],
                "layer": chunk["layer"],
                "score": round(score, 6),
                "excerpt": chunk["text"][:2200],
            }
            for score, chunk in scored[: max(1, min(int(limit), 10))]
        ]

    def _request_json(
        self,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        timeout: float = 3.0,
    ) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload, ensure_ascii=True).encode("utf-8")
        request = Request(
            f"{self.endpoint}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST" if data is not None else "GET",
        )
        with urlopen(request, timeout=timeout) as response:
            decoded = json.loads(response.read().decode("utf-8"))
        if not isinstance(decoded, dict):
            raise ValueError("Ollama returned a non-object response")
        return decoded

    def health(self) -> dict[str, Any]:
        chunks = self._load_corpus()
        layer_counts = Counter(str(item["layer"]) for item in chunks)
        models: list[str] = []
        error = ""
        try:
            payload = self._request_json("/api/tags", timeout=2.0)
            models = [
                str(item.get("name") or item.get("model") or "")
                for item in payload.get("models", [])
                if isinstance(item, dict) and (item.get("name") or item.get("model"))
            ]
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            error = str(exc)
        selected = self.preferred_model if self.preferred_model in models else ""
        if not selected:
            selected = next((item for item in models if item.startswith("qwen2.5:")), "")
        if not selected:
            selected = next((item for item in models if item.startswith("gemma4:")), "")
        if not selected and models:
            selected = models[0]
        return {
            "contract": LOCAL_JYOTISH_CONTRACT,
            "ready": bool(selected and chunks),
            "runtimeReady": bool(models),
            "corpusReady": bool(chunks),
            "model": selected or self.preferred_model,
            "availableModels": models,
            "corpusChunks": len(chunks),
            "retrievalPolicy": "provenance_classical_commentary_hypothesis_opt_in_v3",
            "layerCounts": dict(sorted(layer_counts.items())),
            "corpusPath": str(self.corpus_path),
            "error": error,
            "analysisOnly": True,
            "rawDraftIsOfficial": False,
            "executionAllowed": False,
        }

    @staticmethod
    def _compact_context(context: dict[str, Any]) -> dict[str, Any]:
        deterministic = context.get("deterministicContext")
        if not isinstance(deterministic, dict):
            deterministic = {}
        useful_context = {
            key: value
            for key, value in deterministic.items()
            if value not in (None, "", [], {})
        }
        return {
            "event": context.get("event"),
            "selectedAnnotation": context.get("selectedAnnotation"),
            "annotations": context.get("annotations"),
            "astroEvidence": context.get("astroEvidence"),
            "deterministicContext": useful_context,
            "guardrails": context.get("guardrails"),
        }

    @staticmethod
    def _build_prompt(
        question: str,
        context: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> str:
        source_text = "\n\n".join(
            f"[{item['chunkId']} | {item['layer']} | {item['title']} | retrieval={item['score']}]\n{item['excerpt']}"
            for item in sources
        ) or "No local corpus passage matched this question."
        return "\n".join(
            [
                "You are the local Jyotish research assistant inside Gann Astro Desk.",
                "This is retrospective/manual research only. Never place or recommend an MT5 order.",
                "Treat deterministic application evidence as ground truth. Retrieved passages have different trust layers.",
                "Do not invent ephemeris, Shadbala values, aspects, prices, outcomes, citations, or marker positions.",
                "When a doctrine claim lacks a relevant passage, say that it is an uncited hypothesis.",
                "Cite corpus claims with the exact bracketed chunk id. Separate observation, deterministic calculation, doctrine, and uncertainty.",
                "Classical-doctrine passages, secondary commentary, source-provenance audits, hypothesis references, and local-research memory are different evidence layers.",
                "A source-provenance passage controls attribution and recension warnings; do not treat it as root doctrine.",
                "A hypothesis-reference passage is unverified research material. It may suggest a test, but it is never doctrine, proof, certification, ground truth, or permission to alter deterministic output.",
                "Never present a local note, forum claim, or literary Gann passage as classical authority.",
                "Raw output is an untrusted draft. It must not be promoted to an official ML note without deterministic verification and Codex/human review.",
                "Return concise sections: Observed, Deterministic evidence, Jyotish hypothesis, ML features to test, Uncertainty.",
                "",
                f"Question: {question}",
                "",
                "Deterministic application context:",
                json.dumps(context, indent=2, ensure_ascii=True, default=str)[:30000],
                "",
                "Retrieved local corpus passages:",
                source_text,
            ]
        )

    @staticmethod
    def _verify_draft(
        text: str,
        context: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        issues: list[str] = []
        cited_ids = set(re.findall(r"\[([A-Za-z0-9_.:-]+)\]", text))
        available_ids = {str(item["chunkId"]) for item in sources}
        unknown = sorted(cited_ids - available_ids)
        if unknown:
            issues.append("Draft cites unavailable chunk ids: " + ", ".join(unknown[:8]))
        if re.search(r"\b(place|execute)\s+(an?\s+)?(trade|order)\b|\b(buy|sell)\s+(now|USDJPY)\b", text, re.I):
            issues.append("Draft contains execution-like language; analysis must remain non-actionable.")
        deterministic = context.get("deterministicContext")
        deterministic_keys = " ".join((deterministic or {}).keys()).lower() if isinstance(deterministic, dict) else ""
        event = context.get("event") if isinstance(context.get("event"), dict) else {}
        family = str(event.get("familyKey") or "").upper()
        natal_body = str(event.get("natalBody") or "").upper()
        for mentioned in re.findall(r"AVG\(ALL\)\s*(?:\||-|TO|->)+\s*([A-Z]+)", text.upper()):
            if natal_body and mentioned != natal_body:
                issues.append(
                    f"Draft drifted to AVG(ALL) with {mentioned}; selected family is {family or natal_body}."
                )
                break
        if re.search(r"\b(support|resistance)\s+break\b", text, re.I) and not any(
            token in deterministic_keys for token in ("support", "resistance", "break_confirmation", "sr_geometry")
        ):
            issues.append("Draft introduces an SR-break claim absent from deterministic context.")
        if re.search(r"\b(certified|proven)\s+(jyotish|astrology|shadbala|drik)\b", text, re.I):
            issues.append("Draft overstates external astrology certification.")
        hypothesis_sources = [
            item for item in sources if item.get("layer") == "hypothesis_reference"
        ]
        if hypothesis_sources:
            hypothesis_ids = {str(item["chunkId"]) for item in hypothesis_sources}
            for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
                sentence_ids = set(re.findall(r"\[([A-Za-z0-9_.:-]+)\]", sentence))
                if not (sentence_ids & hypothesis_ids):
                    continue
                if re.search(
                    r"\b(classical(?:\s+doctrine)?|scriptural|authoritative|proven|certified|ground\s+truth)\b",
                    sentence,
                    re.I,
                ) and not re.search(
                    r"\b(not|never|unverified|unproven|hypothesis|fiction|literary)\b",
                    sentence,
                    re.I,
                ):
                    issues.append(
                        "Draft overstates a hypothesis-reference source as doctrine, proof, certification, or ground truth."
                    )
                    break
        if "shadbala" in text.lower() and "shadbala" not in deterministic_keys:
            issues.append("Draft discusses Shadbala although this occurrence exposes no deterministic Shadbala field.")
        if "drik bala" in text.lower() and "drik" not in deterministic_keys:
            issues.append("Draft discusses Drik Bala although this occurrence exposes no deterministic Drik field.")
        if not cited_ids and sources:
            issues.append("Draft did not cite any retrieved passage id.")
        return {
            "status": "pass" if not issues else "review_required",
            "issues": issues,
            "availableCitationIds": sorted(available_ids),
            "citedIds": sorted(cited_ids),
        }

    def analyze(
        self,
        event_id: str,
        question: str,
        annotation_id: str | None = None,
    ) -> dict[str, Any]:
        normalized_event = str(event_id or "").strip()
        normalized_question = str(question or "").strip()
        if not normalized_event:
            raise ValueError("eventId is required")
        if not normalized_question:
            raise ValueError("question is required")
        if len(normalized_question) > 3000:
            raise ValueError("question exceeds 3000 characters")
        health = self.health()
        if not health["ready"]:
            detail = health.get("error") or "Ollama runtime or classical corpus is unavailable"
            raise RuntimeError(detail)
        context = self._compact_context(
            self.repository.codex_context(normalized_event, annotation_id)
        )
        event = context.get("event") if isinstance(context.get("event"), dict) else {}
        evidence = context.get("astroEvidence") if isinstance(context.get("astroEvidence"), list) else []
        query_parts = [
            normalized_question,
            str(event.get("familyKey") or ""),
            str(event.get("transitBody") or ""),
            str(event.get("natalBody") or ""),
            str(event.get("aspectLabel") or event.get("aspect") or ""),
            " ".join(str(item.get("label") or item.get("key") or "") for item in evidence if isinstance(item, dict)),
        ]
        query = " ".join(query_parts)
        retrieval_started_at = time.perf_counter()
        provenance_sources = self.retrieve(query, limit=2, layer="source_provenance")
        doctrine_sources = self.retrieve(query, limit=3, layer="classical_doctrine")
        commentary_sources = self.retrieve(query, limit=2, layer="reference_commentary")
        hypothesis_sources = (
            self.retrieve(query, limit=2, layer="hypothesis_reference")
            if _query_requests_hypotheses(normalized_question)
            else []
        )
        local_candidates = self.retrieve(query, limit=10, layer="local_research")
        family_needles = {
            str(event.get("familyKey") or "").upper(),
            str(event.get("pairKey") or "").upper(),
        } - {""}
        local_sources = [
            item for item in local_candidates
            if any(needle in str(item.get("excerpt") or "").upper() for needle in family_needles)
        ][:2]
        sources = [
            *provenance_sources,
            *doctrine_sources,
            *commentary_sources,
            *hypothesis_sources,
            *local_sources,
        ]
        if self.diagnostics is not None:
            self.diagnostics.record(
                "local_jyotish_retrieval",
                (time.perf_counter() - retrieval_started_at) * 1000,
                details={"sourceCount": len(sources)},
            )
        prompt = self._build_prompt(normalized_question, context, sources)
        available = list(dict.fromkeys([health["model"], *health["availableModels"]]))
        result: dict[str, Any] | None = None
        selected_model = ""
        errors: list[str] = []
        generation_started_at = time.perf_counter()
        for model in available:
            try:
                result = self._request_json(
                    "/api/generate",
                    payload={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.15,
                            "seed": 42,
                            "num_predict": 800,
                            "num_ctx": 16384,
                        },
                    },
                    timeout=240.0,
                )
                selected_model = model
                break
            except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{model}: {exc}")
        if result is None:
            if self.diagnostics is not None:
                self.diagnostics.record(
                    "local_jyotish_generation",
                    (time.perf_counter() - generation_started_at) * 1000,
                    ok=False,
                    details={"attemptedModels": available},
                )
            raise RuntimeError("Local models failed: " + "; ".join(errors))
        if self.diagnostics is not None:
            self.diagnostics.record(
                "local_jyotish_generation",
                (time.perf_counter() - generation_started_at) * 1000,
                details={"model": selected_model},
            )
        text = str(result.get("response") or "").strip()
        if not text:
            raise RuntimeError("Local Jyotish model returned an empty draft")
        verifier = self._verify_draft(text, context, sources)
        return {
            "contract": LOCAL_JYOTISH_CONTRACT,
            "draftId": uuid.uuid4().hex,
            "eventId": normalized_event,
            "model": selected_model,
            "text": text,
            "citations": [
                {
                    "sourceId": item["sourceId"],
                    "chunkId": item["chunkId"],
                    "title": item["title"],
                    "layer": item["layer"],
                    "score": item["score"],
                }
                for item in sources
            ],
            "guardrails": {
                "analysisOnly": True,
                "deterministicEvidenceIsGroundTruth": True,
                "rawDraftIsOfficial": False,
                "consumedByLiveInference": False,
                "consumedByShadowLedger": False,
                "executionAllowed": False,
            },
            "verifier": verifier,
            "disclaimer": "Untrusted local RAG draft. Verify before creating any official research note.",
        }
