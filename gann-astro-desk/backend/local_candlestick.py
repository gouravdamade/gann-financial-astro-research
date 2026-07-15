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

from candlestick_analysis import build_candlestick_evidence


LOCAL_CANDLESTICK_CONTRACT = "GANN_LOCAL_CANDLE_RAG_DRAFT_V1"
TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]{1,}")
STOP_WORDS = {
    "about", "after", "also", "and", "are", "bar", "bars", "before", "candle",
    "candlestick", "chart", "could", "does", "event", "explain", "for", "from",
    "have", "into", "its", "more", "not", "our", "should", "that", "the", "their",
    "this", "through", "using", "was", "were", "what", "when", "which", "with", "would",
}

SOURCE_LAYERS = {
    "TALIB_PATTERN_REFERENCE": "method_reference",
    "CANDLESTICK_EMPIRICAL_EVIDENCE": "empirical_evidence",
    "CANDLESTICK_METHOD_AUDIT": "source_provenance",
}

PATTERN_TERMS = {
    "doji": "doji",
    "spinning top": "spinning_top",
    "marubozu": "marubozu_like",
    "hammer": "long_lower_wick",
    "hanging man": "long_lower_wick",
    "shooting star": "long_upper_wick",
    "inverted hammer": "long_upper_wick",
    "bullish engulfing": "bullish_body_engulfing",
    "bearish engulfing": "bearish_body_engulfing",
    "inside bar": "inside_bar",
    "outside bar": "outside_bar",
}


def _tokens(value: str) -> set[str]:
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(str(value or ""))
        if token.lower() not in STOP_WORDS
    }


def _source_layer(source_id: str) -> str:
    return SOURCE_LAYERS.get(str(source_id or "").upper(), "unclassified_reference")


class LocalCandlestickService:
    """Isolated deterministic OHLC evidence plus untrusted local-RAG commentary."""

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
        default_corpus = repository.paths.project_root / "candlestick_agent" / "corpus_chunks.jsonl"
        self.corpus_path = Path(
            corpus_path
            or os.environ.get("GANN_ASTRO_CANDLE_CORPUS")
            or default_corpus
        ).expanduser().resolve()
        self.endpoint = str(
            endpoint
            or os.environ.get("GANN_ASTRO_OLLAMA_URL")
            or "http://127.0.0.1:11434"
        ).rstrip("/")
        self.preferred_model = str(
            preferred_model
            or os.environ.get("GANN_ASTRO_CANDLE_LLM_MODEL")
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
                source_id = str(row.get("source_id") or "LOCAL")
                title = str(row.get("title") or source_id)
                token_set = _tokens(f"{title} {text}")
                if not token_set:
                    continue
                frequency.update(token_set)
                chunks.append(
                    {
                        "sourceId": source_id,
                        "chunkId": str(row.get("chunk_id") or f"LOCAL-{len(chunks) + 1:05d}"),
                        "title": title,
                        "layer": _source_layer(source_id),
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
        *,
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

    def _required_layer_sources(
        self,
        query: str,
        *,
        layer: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        matches = self.retrieve(query, limit=limit, layer=layer)
        if matches:
            return matches
        fallbacks = sorted(
            (item for item in self._load_corpus() if item["layer"] == layer),
            key=lambda item: item["chunkId"],
        )
        return [
            {
                "sourceId": item["sourceId"],
                "chunkId": item["chunkId"],
                "title": item["title"],
                "layer": item["layer"],
                "score": 0.0,
                "excerpt": item["text"][:2200],
            }
            for item in fallbacks[: max(1, min(int(limit), 10))]
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
            selected = next((item for item in models if item.startswith("gemma")), "")
        if not selected and models:
            selected = models[0]
        return {
            "contract": LOCAL_CANDLESTICK_CONTRACT,
            "ready": bool(selected and chunks),
            "runtimeReady": bool(models),
            "corpusReady": bool(chunks),
            "model": selected or self.preferred_model,
            "availableModels": models,
            "corpusChunks": len(chunks),
            "retrievalPolicy": "candlestick_method_empirical_provenance_v1",
            "layerCounts": dict(sorted(layer_counts.items())),
            "corpusPath": str(self.corpus_path),
            "error": error,
            "analysisOnly": True,
            "rawDraftIsOfficial": False,
            "executionAllowed": False,
        }

    def evidence(self, event_id: str, annotation_id: str | None = None) -> dict[str, Any]:
        normalized_event = str(event_id or "").strip()
        if not normalized_event:
            raise ValueError("eventId is required")
        return build_candlestick_evidence(
            self.repository.event_detail(normalized_event),
            str(annotation_id or "").strip() or None,
        )

    @staticmethod
    def _build_prompt(
        question: str,
        evidence: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> str:
        source_text = "\n\n".join(
            f"[{item['chunkId']} | {item['layer']} | {item['title']} | retrieval={item['score']}]\n{item['excerpt']}"
            for item in sources
        ) or "No local candlestick passage matched this question."
        return "\n".join(
            [
                "You are the isolated candlestick research specialist inside Gann Astro Desk.",
                "This is retrospective/manual analysis only. Never place, execute, or recommend an order.",
                "The deterministic OHLC packet is ground truth. Never invent a bar, price, time, trend, pattern, or outcome.",
                "The transparent detector is not TA-Lib and must never be described as TA-Lib parity.",
                "A named shape is not a universal signal. Keep geometry, prior trend, confirmation, and market context separate.",
                "Post-cutoff bars are hindsight and must be labeled retrospective whenever discussed.",
                "Empirical studies are mixed and market/timeframe/holding-cost dependent. Do not promise predictive value.",
                "Every method statement must cite an exact bracketed method-reference chunk id.",
                "The Empirical caveat section must cite an exact bracketed empirical-evidence chunk id.",
                "Do not invent or shorten citation ids; copy them exactly from the retrieved passage headers.",
                "Raw output is an untrusted draft even when its citations are valid.",
                "Return concise sections: Observed OHLC, Pattern geometry, Context hypothesis, Empirical caveat, Uncertainty.",
                "Do not discuss Jyotish; a future coordinator may compare specialist outputs without merging their evidence.",
                "",
                f"Question: {question}",
                "",
                "Deterministic candlestick evidence:",
                json.dumps(evidence, indent=2, ensure_ascii=True, default=str)[:30000],
                "",
                "Retrieved local candlestick passages:",
                source_text,
            ]
        )

    @staticmethod
    def _verify_draft(
        text: str,
        evidence: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        issues: list[str] = []
        cited_ids = set(re.findall(r"\[([A-Za-z0-9_.:-]+)\]", text))
        available_ids = {str(item["chunkId"]) for item in sources}
        unknown = sorted(cited_ids - available_ids)
        if unknown:
            issues.append("Draft cites unavailable chunk ids: " + ", ".join(unknown[:8]))
        if sources and not cited_ids:
            issues.append("Draft did not cite any retrieved passage id.")
        required_layers = {
            "method_reference": "method-reference",
            "empirical_evidence": "empirical-evidence",
        }
        for layer, label in required_layers.items():
            layer_ids = {
                str(item["chunkId"])
                for item in sources
                if str(item.get("layer") or "") == layer
            }
            if layer_ids and not cited_ids.intersection(layer_ids):
                issues.append(f"Draft did not cite a retrieved {label} passage.")
        if re.search(r"\b(place|execute|open|close)\s+(an?\s+)?(trade|order|position)\b|\b(buy|sell)\s+(now|USDJPY)\b", text, re.I):
            issues.append("Draft contains execution-like language; analysis must remain non-actionable.")
        overclaim_pattern = re.compile(
            r"\b(guaranteed|universally predictive|proven profitable|always predicts|never fails)\b",
            re.I,
        )
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
            if not overclaim_pattern.search(sentence):
                continue
            if re.search(
                r"\b(?:not|never|no evidence|cannot be|isn't|is not|aren't|are not)\b[^.\n]{0,35}\b(?:guaranteed|universally predictive|proven profitable|always predicts|never fails)\b",
                sentence,
                re.I,
            ):
                continue
            issues.append("Draft overstates candlestick predictive evidence.")
            break
        if re.search(r"\bTA[- ]?Lib\b.*\b(detected|confirmed|parity|identical|equivalent)\b", text, re.I):
            issues.append("Draft falsely claims TA-Lib detection or parity for the transparent geometry engine.")
        if re.search(r"\bwill\s+(rise|fall|rally|drop|reverse|continue)\b", text, re.I):
            issues.append("Draft presents a conditional pattern hypothesis as a certain future outcome.")
        observed_patterns = {
            str(pattern.get("name") or "")
            for section in (evidence.get("focusBar"),)
            if isinstance(section, dict)
            for pattern in section.get("patterns", [])
            if isinstance(pattern, dict)
        }
        normalized_text = text.lower().replace("-", " ")
        for phrase, detector_name in PATTERN_TERMS.items():
            current_claim = re.search(
                rf"\b(?:current|focus|latest|selected)\s+(?:bar|candle)?[^.\n]{{0,35}}\b{re.escape(phrase)}\b",
                normalized_text,
            )
            if current_claim and detector_name not in observed_patterns:
                issues.append(
                    f"Draft calls the focus bar {phrase}, but deterministic geometry did not detect {detector_name}."
                )
        return {
            "status": "pass" if not issues else "review_required",
            "issues": issues,
            "availableCitationIds": sorted(available_ids),
            "citedIds": sorted(cited_ids),
        }

    @staticmethod
    def _ensure_source_footer(
        text: str,
        sources: list[dict[str, Any]],
    ) -> tuple[str, list[str]]:
        if re.search(r"\[([A-Za-z0-9_.:-]+)\]", text):
            return text, []
        method = next((item for item in sources if item.get("layer") == "method_reference"), None)
        empirical = next((item for item in sources if item.get("layer") == "empirical_evidence"), None)
        lines = ["", "### Deterministic source boundary"]
        if method:
            lines.append(
                f"- Geometry labels and trend-context cautions use [{method['chunkId']}]."
            )
        if empirical:
            lines.append(
                f"- Published findings are mixed and require target-market validation [{empirical['chunkId']}]."
            )
        if len(lines) == 2:
            return text, []
        return (
            text.rstrip() + "\n" + "\n".join(lines),
            ["The model omitted source ids; code appended a deterministic citation footer."],
        )

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
        evidence = self.evidence(normalized_event, annotation_id)
        health = self.health()
        if not health["ready"]:
            detail = health.get("error") or "Ollama runtime or candlestick corpus is unavailable"
            raise RuntimeError(detail)
        pattern_names = [
            str(pattern.get("name") or "")
            for record in [evidence.get("focusBar"), *evidence.get("eventWindow", {}).get("patterns", [])]
            if isinstance(record, dict)
            for pattern in (
                record.get("patterns", [])
                if isinstance(record.get("patterns"), list)
                else [record]
            )
            if isinstance(pattern, dict)
        ]
        query = " ".join(
            [
                normalized_question,
                str(evidence.get("symbol") or ""),
                str(evidence.get("timeframe") or ""),
                " ".join(pattern_names),
                str((evidence.get("focusBar") or {}).get("preTrend") or ""),
            ]
        )
        retrieval_started_at = time.perf_counter()
        sources = [
            *self._required_layer_sources(query, limit=2, layer="source_provenance"),
            *self._required_layer_sources(query, limit=3, layer="method_reference"),
            *self._required_layer_sources(query, limit=3, layer="empirical_evidence"),
        ]
        if self.diagnostics is not None:
            self.diagnostics.record(
                "local_candlestick_retrieval",
                (time.perf_counter() - retrieval_started_at) * 1000,
                details={"sourceCount": len(sources)},
            )
        prompt = self._build_prompt(normalized_question, evidence, sources)
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
                            "temperature": 0.10,
                            "seed": 43,
                            "num_predict": 700,
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
                    "local_candlestick_generation",
                    (time.perf_counter() - generation_started_at) * 1000,
                    ok=False,
                    details={"attemptedModels": available},
                )
            raise RuntimeError("Local models failed: " + "; ".join(errors))
        if self.diagnostics is not None:
            self.diagnostics.record(
                "local_candlestick_generation",
                (time.perf_counter() - generation_started_at) * 1000,
                details={"model": selected_model},
            )
        raw_text = str(result.get("response") or "").strip()
        if not raw_text:
            raise RuntimeError("Local candlestick model returned an empty draft")
        text, repairs = self._ensure_source_footer(raw_text, sources)
        verifier = self._verify_draft(text, evidence, sources)
        verifier["repairs"] = repairs
        return {
            "contract": LOCAL_CANDLESTICK_CONTRACT,
            "draftId": uuid.uuid4().hex,
            "eventId": normalized_event,
            "model": selected_model,
            "text": text,
            "evidence": evidence,
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
            "disclaimer": "Untrusted candlestick RAG draft. A named pattern is not a trade signal.",
        }
