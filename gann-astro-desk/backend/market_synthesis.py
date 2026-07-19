from __future__ import annotations

import json
import os
import re
import time
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from candlestick_analysis import build_candlestick_evidence
from rsi_analysis import build_rsi_evidence


MARKET_SYNTHESIS_CONTRACT = "GANN_LOCAL_MARKET_SYNTHESIS_DRAFT_V1"
MARKET_SYNTHESIS_PACKET_CONTRACT = "GANN_MARKET_SYNTHESIS_PACKET_V1"
FORBIDDEN_ASTRO_KEY_PARTS = (
    "return",
    "outcome",
    "signed_pips",
    "raw_pips",
    "mfe",
    "mae",
    "excursion",
    "ret_after",
    "observed",
)


def _safe_astro_evidence(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    output: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "")
        if not key or any(part in key.lower() for part in FORBIDDEN_ASTRO_KEY_PARTS):
            continue
        output.append(
            {
                "key": key,
                "label": str(item.get("label") or key),
                "value": item.get("value"),
                "unit": item.get("unit"),
                "certification": item.get("certification"),
            }
        )
    return output


class MarketSynthesisService:
    """Research-only coordinator over isolated deterministic specialist packets."""

    def __init__(
        self,
        repository: Any,
        *,
        endpoint: str | None = None,
        preferred_model: str | None = None,
        diagnostics: Any | None = None,
    ) -> None:
        self.repository = repository
        self.endpoint = str(
            endpoint
            or os.environ.get("GANN_ASTRO_OLLAMA_URL")
            or "http://127.0.0.1:11434"
        ).rstrip("/")
        self.preferred_model = str(
            preferred_model
            or os.environ.get("GANN_ASTRO_MARKET_LLM_MODEL")
            or os.environ.get("GANN_ASTRO_LOCAL_LLM_MODEL")
            or "qwen2.5:3b"
        ).strip()
        self.diagnostics = diagnostics

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
            "contract": MARKET_SYNTHESIS_CONTRACT,
            "ready": bool(selected),
            "runtimeReady": bool(models),
            "model": selected or self.preferred_model,
            "availableModels": models,
            "error": error,
            "analysisOnly": True,
            "executionAllowed": False,
        }

    def packet(
        self,
        event_id: str,
        annotation_id: str | None = None,
        *,
        period: int = 14,
        levels: list[Any] | None = None,
        include_astrology: bool = True,
        include_candles: bool = True,
        include_rsi: bool = True,
    ) -> dict[str, Any]:
        normalized_event = str(event_id or "").strip()
        if not normalized_event:
            raise ValueError("eventId is required")
        if not any((include_astrology, include_candles, include_rsi)):
            raise ValueError("At least one specialist input must be included")
        detail = self.repository.event_detail(normalized_event)
        event = detail.get("event") if isinstance(detail.get("event"), dict) else {}
        candle = build_candlestick_evidence(detail, annotation_id) if include_candles else None
        rsi = build_rsi_evidence(
            detail,
            annotation_id,
            period=period,
            levels=levels,
        ) if include_rsi else None
        candle_input = None
        if candle is not None:
            candle_input = {
                key: value
                for key, value in candle.items()
                if key != "hindsight"
            }
        astrology_input = None
        if include_astrology:
            astrology_input = {
                "event": {
                    key: event.get(key)
                    for key in (
                        "eventId",
                        "caseId",
                        "familyKey",
                        "pairKey",
                        "aspect",
                        "aspectLabel",
                        "transitBody",
                        "natalBody",
                        "startIso",
                        "endIso",
                        "peakIso",
                        "durationMinutes",
                        "peakOrbDeg",
                        "orbLimitDeg",
                        "astronomyContract",
                        "sourceGenerator",
                    )
                },
                "astroEvidence": _safe_astro_evidence(detail.get("astroEvidence")),
                "currencyPairEvidence": detail.get("currencyPairEvidence"),
                "evidenceCertifications": detail.get("evidenceCertifications"),
            }
        cutoffs = [
            str(item.get("analysisCutoff") or "")
            for item in (candle_input, rsi)
            if isinstance(item, dict) and item.get("analysisCutoff")
        ]
        if len(set(cutoffs)) > 1:
            raise ValueError("Specialist packets disagree on the analysis cutoff")
        return {
            "contract": MARKET_SYNTHESIS_PACKET_CONTRACT,
            "eventId": normalized_event,
            "symbol": str((detail.get("chart") or {}).get("symbol") or ""),
            "timeframe": str((detail.get("chart") or {}).get("timeframe") or ""),
            "analysisCutoff": cutoffs[0] if cutoffs else str(event.get("endIso") or ""),
            "includedInputs": {
                "astrology": include_astrology,
                "candlesticks": include_candles,
                "rsi": include_rsi,
            },
            "astrology": astrology_input,
            "candlesticks": candle_input,
            "rsi": rsi,
            "guardrails": {
                "analysisOnly": True,
                "specialistPacketsRemainIsolated": True,
                "retrospectiveOutcomeExcluded": True,
                "candlestickHindsightExcluded": True,
                "closedBarsOnlyAtCutoff": True,
                "consumedByLiveInference": False,
                "consumedByShadowLedger": False,
                "automaticOrderPlacement": False,
                "executionAllowed": False,
            },
        }

    @staticmethod
    def _prompt(question: str, packet: dict[str, Any]) -> str:
        return "\n".join(
            [
                "You are the research-only market synthesis coordinator inside Gann Astro Desk.",
                "The deterministic packet is ground truth. Never invent a price, time, RSI value, candle pattern, astrological value, or certification.",
                "Astrology, candlestick geometry, and RSI remain separate specialist inputs. Compare them; do not pretend they are one doctrine.",
                "Use only inputs whose includedInputs flag is true. The packet excludes observed outcome and candlestick hindsight.",
                "RSI 30/50/70 or custom levels are observations, not guaranteed reversal levels.",
                "A candlestick name is geometry, not a universal trade signal. Uncertified astrology must be identified as provisional.",
                "Return a provisional Direction hypothesis: bullish, bearish, or abstain. Abstain when inputs conflict or evidence is too weak.",
                "Entry conditions may describe what would need to happen on a future closed bar, but never tell the user to place or execute an order.",
                "Never claim certainty, profitability, or live eligibility. This draft cannot change policy or place trades.",
                "Use concise sections: Direction hypothesis, Entry conditions, Supporting evidence, Conflicts, Invalidation, Uncertainty.",
                "Refer to deterministic fields by their exact names in backticks when giving a numerical reason.",
                "Do not cite external books or doctrine; the isolated Local Jyotish specialist owns doctrine interpretation.",
                "",
                f"Question: {question}",
                "",
                "Deterministic specialist packet:",
                json.dumps(packet, indent=2, ensure_ascii=True, default=str)[:48000],
            ]
        )

    @staticmethod
    def _verify(text: str, packet: dict[str, Any]) -> dict[str, Any]:
        issues: list[str] = []
        if not re.search(r"direction hypothesis", text, re.I):
            issues.append("Draft omitted the required Direction hypothesis section.")
        if not re.search(r"\b(bullish|bearish|abstain)\b", text, re.I):
            issues.append("Draft did not state bullish, bearish, or abstain.")
        if re.search(r"\b(place|execute|open|send)\s+(an?\s+)?(trade|order|position)\b|\b(buy|sell)\s+(now|immediately|USDJPY)\b", text, re.I):
            issues.append("Draft contains execution-like language.")
        if re.search(r"\b(guaranteed|certainly|will definitely|proven profitable|cannot lose)\b", text, re.I):
            issues.append("Draft overstates certainty or profitability.")
        included = packet.get("includedInputs") if isinstance(packet.get("includedInputs"), dict) else {}
        if not included.get("rsi") and re.search(r"\bRSI\b|relative strength index", text, re.I):
            issues.append("Draft discusses RSI even though RSI input was excluded.")
        if not included.get("candlesticks") and re.search(r"\b(candle|candlestick|wick|OHLC)\b", text, re.I):
            issues.append("Draft discusses candlesticks even though candle input was excluded.")
        if not included.get("astrology") and re.search(r"\b(planet|aspect|shadbala|jyotish|astrolog)\w*\b", text, re.I):
            issues.append("Draft discusses astrology even though astrology input was excluded.")
        return {"status": "pass" if not issues else "review_required", "issues": issues}

    def analyze(
        self,
        event_id: str,
        question: str,
        annotation_id: str | None = None,
        *,
        period: int = 14,
        levels: list[Any] | None = None,
        include_astrology: bool = True,
        include_candles: bool = True,
        include_rsi: bool = True,
    ) -> dict[str, Any]:
        normalized_question = str(question or "").strip()
        if not normalized_question:
            raise ValueError("question is required")
        if len(normalized_question) > 3000:
            raise ValueError("question exceeds 3000 characters")
        packet = self.packet(
            event_id,
            annotation_id,
            period=period,
            levels=levels,
            include_astrology=include_astrology,
            include_candles=include_candles,
            include_rsi=include_rsi,
        )
        health = self.health()
        if not health["runtimeReady"]:
            raise RuntimeError(health.get("error") or "Ollama runtime is unavailable")
        models = list(dict.fromkeys([health["model"], *health["availableModels"]]))
        result: dict[str, Any] | None = None
        selected_model = ""
        errors: list[str] = []
        started_at = time.perf_counter()
        for model in models:
            try:
                result = self._request_json(
                    "/api/generate",
                    payload={
                        "model": model,
                        "prompt": self._prompt(normalized_question, packet),
                        "stream": False,
                        "options": {
                            "temperature": 0.05,
                            "seed": 73,
                            "num_predict": 750,
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
            raise RuntimeError("Local models failed: " + "; ".join(errors))
        text = str(result.get("response") or "").strip()
        if not text:
            raise RuntimeError("Local market synthesis model returned an empty draft")
        if self.diagnostics is not None:
            self.diagnostics.record(
                "local_market_synthesis_generation",
                (time.perf_counter() - started_at) * 1000,
                details={"model": selected_model},
            )
        return {
            "contract": MARKET_SYNTHESIS_CONTRACT,
            "draftId": uuid.uuid4().hex,
            "eventId": str(event_id),
            "model": selected_model,
            "text": text,
            "packet": packet,
            "verifier": self._verify(text, packet),
            "guardrails": {
                "analysisOnly": True,
                "deterministicEvidenceIsGroundTruth": True,
                "rawDraftIsOfficial": False,
                "consumedByLiveInference": False,
                "consumedByShadowLedger": False,
                "automaticOrderPlacement": False,
                "executionAllowed": False,
            },
            "disclaimer": "Untrusted market synthesis draft. It cannot place an order or override validation gates.",
        }
