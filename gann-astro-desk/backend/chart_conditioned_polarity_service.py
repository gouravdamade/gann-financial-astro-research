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
from chart_conditioned_aspects.polarity_series import compile_categorical_visible_range  # noqa: E402
from chart_conditioned_transit_event_service import (  # noqa: E402
    APPROVED_ASPECT_PROFILE_ID,
    build_chart_conditioned_transit_event_range,
)


REQUEST_KEYS = {
    "instrumentIdentity",
    "chartId",
    "chartHypothesisId",
    "transitBody",
    "natalTarget",
    "aspectType",
}
RANGE_REQUEST_KEYS = {
    "sideIdentity",
    "rangeStartUtc",
    "rangeEndUtc",
    "aspectProfileId",
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
        chart_hypothesis_id=_optional(payload.get("chartHypothesisId")),
        transit_body=_optional(payload.get("transitBody")),
        natal_target=_optional(payload.get("natalTarget")),
        aspect_type=_optional(payload.get("aspectType")),
    )


def _optional(value: Any) -> str | None:
    token = str(value or "").strip()
    return token or None


def build_chart_conditioned_polarity_range(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Compile unreviewed categorical intervals from backend-owned TN events.

    The empty catalogue intentionally keeps these intervals UNKNOWN.  Event
    geometry is real and segmented, but it never becomes a polarity shortcut.
    """
    unknown = sorted(set(payload) - RANGE_REQUEST_KEYS)
    if unknown:
        raise ValueError("Unknown chart-conditioned polarity range field(s): " + ", ".join(unknown))
    event_range = build_chart_conditioned_transit_event_range(
        {
            "sideIdentity": payload.get("sideIdentity"),
            "rangeStartUtc": payload.get("rangeStartUtc"),
            "rangeEndUtc": payload.get("rangeEndUtc"),
            "aspectProfileId": payload.get("aspectProfileId") or APPROVED_ASPECT_PROFILE_ID,
        }
    )
    result = compile_categorical_visible_range(
        TargetAwarePolarityCatalogue.load(),
        instrument_id=str(event_range["instrumentIdentity"]),
        chart_id=str(event_range["chartId"]),
        chart_hypothesis_id=str(event_range["chartHypothesisId"]),
        range_start_utc=str(payload.get("rangeStartUtc") or ""),
        range_end_utc=str(payload.get("rangeEndUtc") or ""),
        events=event_range["events"],
    )
    result["eventCompiler"] = {
        "contract": event_range["contract"],
        "generatorVersion": event_range["generatorVersion"],
        "generatorHash": event_range["generatorHash"],
        "aspectProfileId": event_range["aspectProfileId"],
        "eventCount": len(event_range["events"]),
        "rejectedEvents": event_range["rejectedEvents"],
        "unknownReasons": event_range["unknownReasons"],
        "astronomyContract": event_range["astronomyContract"],
        "ephemerisVersion": event_range["ephemerisVersion"],
        "ayanamsha": event_range["ayanamsha"],
        "nodePolicy": event_range["nodePolicy"],
    }
    return result
