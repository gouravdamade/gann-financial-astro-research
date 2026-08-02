from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))
if str(INSTRUMENT_SBC_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUMENT_SBC_ROOT))

from chart_conditioned_aspects.polarity_catalogue import (  # noqa: E402
    TargetAwarePolarityCatalogue,
    lookup_target_aware_polarity,
)


REQUEST_KEYS = {
    "instrumentIdentity",
    "chartId",
    "transitBody",
    "natalTarget",
    "aspectType",
}


def build_chart_conditioned_polarity_lookup(payload: Mapping[str, Any]) -> dict[str, Any]:
    unknown = sorted(set(payload) - REQUEST_KEYS)
    if unknown:
        raise ValueError(
            "Unknown chart-conditioned polarity request field(s): " + ", ".join(unknown)
        )
    instrument_identity = str(payload.get("instrumentIdentity") or "").strip()
    if not instrument_identity:
        raise ValueError("instrumentIdentity is required")
    return lookup_target_aware_polarity(
        TargetAwarePolarityCatalogue.load(),
        instrument_id=instrument_identity,
        chart_id=_optional(payload.get("chartId")),
        transit_body=_optional(payload.get("transitBody")),
        natal_target=_optional(payload.get("natalTarget")),
        aspect_type=_optional(payload.get("aspectType")),
    )


def _optional(value: Any) -> str | None:
    token = str(value or "").strip()
    return token or None
