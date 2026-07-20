from __future__ import annotations

from typing import Any


CONTRACT = "GANN_ASTRO_COMPANION_CAPABILITIES_V1"


def build_companion_capabilities() -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "apiVersion": 1,
        "hostRole": "windows_research_host",
        "transport": {
            "gatewayRequired": True,
            "directPythonExposureAllowed": False,
            "tlsRequired": True,
            "devicePairingRequired": True,
        },
        "features": {
            "chartRead": True,
            "reviewWrite": True,
            "aiDrafts": True,
            "codexBridge": True,
            "offlineCache": True,
            "orderPlacement": False,
        },
        "computeTopology": {
            "android": [
                "chart_rendering",
                "touch_drawings",
                "parameter_input",
                "offline_cache",
            ],
            "windows": [
                "mt5",
                "swiss_ephemeris",
                "astro_doctrine",
                "historical_replay",
                "local_llm",
                "market_synthesis",
                "codex_bridge",
                "research_storage",
            ],
            "authoritativeEvidence": "windows",
        },
        "guardrails": {
            "executionAllowed": False,
            "timestampSafeEvidenceRequired": True,
            "retrospectiveLabelsAllowedInLiveInference": False,
            "llmDraftsAreEvidence": False,
        },
    }
