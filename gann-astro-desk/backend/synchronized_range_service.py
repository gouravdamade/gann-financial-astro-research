from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from chakra_lab_service import build_chakra_lab_atomic_range
from chart_conditioned_polarity_service import (
    build_chart_conditioned_polarity_range,
)


SYNCHRONIZED_RANGE_CONTRACT = "SYNCHRONIZED_INDEPENDENT_RANGE_V1"
SYNCHRONIZED_RANGE_SCHEMA_VERSION = 1
REQUEST_KEYS = {
    "rangeStartUtc",
    "rangeEndUtc",
    "aspectRanges",
    "sbcRange",
}
ASPECT_RANGE_KEYS = {
    "sideIdentity",
    "instrumentIdentity",
    "chartId",
    "chartHypothesisId",
    "events",
}
SBC_RANGE_KEYS = {"instrumentIdentity", "boundaries"}
FX_SIDE_IDENTITIES = {"USD", "JPY"}


def _reject_unknown(payload: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label} field(s): {', '.join(unknown)}")


def _required(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} is required")
    return text


def _utc(value: Any, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(_required(value, label).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _require_matching_range(
    value_start: Any,
    value_end: Any,
    *,
    expected_start: datetime,
    expected_end: datetime,
    label: str,
) -> None:
    if _utc(value_start, f"{label}.rangeStart") != expected_start:
        raise ValueError(f"{label} did not preserve the shared visible range start")
    if _utc(value_end, f"{label}.rangeEnd") != expected_end:
        raise ValueError(f"{label} did not preserve the shared visible range end")


def _side_range(
    payload: Mapping[str, Any],
    *,
    range_start: datetime,
    range_end: datetime,
) -> tuple[str, dict[str, Any]]:
    _reject_unknown(payload, ASPECT_RANGE_KEYS, "aspect range")
    side = _required(payload.get("sideIdentity"), "aspect range.sideIdentity").upper()
    if side not in FX_SIDE_IDENTITIES:
        raise ValueError("aspect range.sideIdentity must be USD or JPY")
    expected_instrument = f"FX_CURRENCY:{side}"
    if _required(payload.get("instrumentIdentity"), "aspect range.instrumentIdentity") != expected_instrument:
        raise ValueError(
            f"aspect range {side} must use primary identity {expected_instrument}"
        )
    result = build_chart_conditioned_polarity_range(
        {
            "instrumentIdentity": expected_instrument,
            "chartId": _required(payload.get("chartId"), "aspect range.chartId"),
            "chartHypothesisId": _required(
                payload.get("chartHypothesisId"),
                "aspect range.chartHypothesisId",
            ),
            "rangeStartUtc": _iso(range_start),
            "rangeEndUtc": _iso(range_end),
            "events": payload.get("events"),
        }
    )
    _require_matching_range(
        result["rangeStartUtc"],
        result["rangeEndUtc"],
        expected_start=range_start,
        expected_end=range_end,
        label=f"aspect range {side}",
    )
    return side, result


def build_synchronized_independent_range(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build independently compiled fields over one exact visible time range."""
    if not isinstance(payload, Mapping):
        raise ValueError("synchronized range request must be an object")
    _reject_unknown(payload, REQUEST_KEYS, "synchronized range request")
    range_start = _utc(payload.get("rangeStartUtc"), "rangeStartUtc")
    range_end = _utc(payload.get("rangeEndUtc"), "rangeEndUtc")
    if range_end <= range_start:
        raise ValueError("rangeEndUtc must be after rangeStartUtc")

    raw_aspect_ranges = payload.get("aspectRanges")
    if not isinstance(raw_aspect_ranges, list):
        raise ValueError("aspectRanges must be an array")
    compiled_sides = [
        _side_range(
            item,
            range_start=range_start,
            range_end=range_end,
        )
        for item in raw_aspect_ranges
        if isinstance(item, Mapping)
    ]
    if len(compiled_sides) != len(raw_aspect_ranges):
        raise ValueError("each aspect range must be an object")
    side_ids = {side for side, _ in compiled_sides}
    if side_ids != FX_SIDE_IDENTITIES or len(compiled_sides) != len(FX_SIDE_IDENTITIES):
        raise ValueError("aspectRanges must contain exactly one USD and one JPY range")

    raw_sbc = payload.get("sbcRange")
    if not isinstance(raw_sbc, Mapping):
        raise ValueError("sbcRange must be an object")
    _reject_unknown(raw_sbc, SBC_RANGE_KEYS, "sbc range")
    sbc_range = build_chakra_lab_atomic_range(
        {
            "instrumentIdentity": _required(
                raw_sbc.get("instrumentIdentity"),
                "sbcRange.instrumentIdentity",
            ),
            "terminalEnd": _iso(range_end),
            "boundaries": raw_sbc.get("boundaries"),
        }
    )
    _require_matching_range(
        sbc_range["range_start_utc"],
        sbc_range["range_end_utc"],
        expected_start=range_start,
        expected_end=range_end,
        label="SBC range",
    )

    ordered_sides = {
        side: value for side, value in sorted(compiled_sides, key=lambda item: item[0])
    }
    return {
        "contract": SYNCHRONIZED_RANGE_CONTRACT,
        "schemaVersion": SYNCHRONIZED_RANGE_SCHEMA_VERSION,
        "rangeStartUtc": _iso(range_start),
        "rangeEndUtc": _iso(range_end),
        "synchronizationStatus": "SYNCHRONIZED",
        "aspectFields": ordered_sides,
        "sbcField": sbc_range,
        "guardrails": {
            "readOnly": True,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
            "financiallyValidated": False,
            "fieldsFused": False,
            "actsAsSbcConfirmation": False,
            "marketDirectionInferred": False,
        },
    }
