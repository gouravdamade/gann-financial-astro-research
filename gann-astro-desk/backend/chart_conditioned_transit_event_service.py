"""Backend boundary for the canonical chart-conditioned TN event compiler."""

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

from chart_conditioned_aspects.transits.chart_conditioned_event_compiler import (  # noqa: E402
    APPROVED_ASPECT_PROFILE_ID,
    CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT,
    compile_chart_conditioned_transit_event_range,
)


EVENT_RANGE_REQUEST_KEYS = {
    "sideIdentity",
    "rangeStartUtc",
    "rangeEndUtc",
    "aspectProfileId",
}


def build_chart_conditioned_transit_event_range(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Compile server-owned TN astronomy events for one accepted FX side.

    The contract intentionally accepts no frontend chart IDs or event bodies.
    This prevents a client from substituting an identity or sending a fabricated
    event to the polarity range path.
    """
    if not isinstance(payload, Mapping):
        raise ValueError("chart-conditioned event range request must be an object")
    unknown = sorted(set(payload) - EVENT_RANGE_REQUEST_KEYS)
    if unknown:
        raise ValueError(
            "Unknown chart-conditioned event range request field(s): "
            + ", ".join(unknown)
        )
    return compile_chart_conditioned_transit_event_range(
        side_identity=str(payload.get("sideIdentity") or ""),
        range_start_utc=str(payload.get("rangeStartUtc") or ""),
        range_end_utc=str(payload.get("rangeEndUtc") or ""),
        aspect_profile_id=str(payload.get("aspectProfileId") or APPROVED_ASPECT_PROFILE_ID),
    )


__all__ = [
    "APPROVED_ASPECT_PROFILE_ID",
    "CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT",
    "build_chart_conditioned_transit_event_range",
]
