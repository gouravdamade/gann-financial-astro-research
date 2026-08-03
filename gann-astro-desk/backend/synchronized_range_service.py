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
TRAILOKYA_SOURCE_ONLY_PROFILE_ID = "SBC_TRAILOKYA_1972_V1"
TRAILOKYA_GEOMETRY_RANGE_CONTRACT = "SBC_TRAILOKYA_1972_GEOMETRY_ONLY_RANGE_V1"
TRAILOKYA_GEOMETRY_RANGE_STATE = "GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED"
TRAILOKYA_SOURCE_GAPS = (
    "SBC_TD1972_BASE_NATURAL_PLANET_CLASS_PENDING",
    "SBC_TD1972_ISOLATED_RESULT_FACTORS_PENDING",
    "SBC_TD1972_SWIFT_MEAN_THRESHOLD_SOURCE_MISSING",
    "SBC_TD1972_MODIFIER_STACKING_SOURCE_MISSING",
    "SBC_TD1972_MOON_MERCURY_CONDITIONS_PENDING",
    "SBC_ABSOLUTE_ORIENTATION_UNRESOLVED",
    "SBC_TD1972_GEOMETRY_RANGE_NOT_COMPILED",
)


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


def _trailokya_source_only_selected(raw_sbc: Mapping[str, Any]) -> bool:
    """Detect the explicit source-only request without constructing an SBC engine."""
    boundaries = raw_sbc.get("boundaries")
    if not isinstance(boundaries, list):
        return False
    return any(
        isinstance(boundary, Mapping)
        and isinstance(boundary.get("request"), Mapping)
        and boundary["request"].get("vedhaProfileId") == TRAILOKYA_SOURCE_ONLY_PROFILE_ID
        for boundary in boundaries
    )


def _trailokya_geometry_range_unavailable(
    raw_sbc: Mapping[str, Any],
    *,
    range_start: datetime,
    range_end: datetime,
) -> dict[str, Any]:
    """Fail closed until a score-free range compiler is separately admitted.

    This validates only the visible-range boundary and does not create a
    ChakraLabEngine, a ledger, or a VedhaGuidanceEngine.
    """
    boundaries = raw_sbc.get("boundaries")
    if not isinstance(boundaries, list) or not boundaries:
        raise ValueError("Trailokya geometry range requires at least one boundary")
    for index, boundary in enumerate(boundaries):
        if not isinstance(boundary, Mapping):
            raise ValueError(f"Trailokya geometry boundary {index + 1} must be an object")
        request = boundary.get("request")
        if not isinstance(request, Mapping):
            raise ValueError(f"Trailokya geometry boundary {index + 1}.request must be an object")
        if request.get("vedhaProfileId") != TRAILOKYA_SOURCE_ONLY_PROFILE_ID:
            raise ValueError("Trailokya geometry range cannot mix scored and source-only profiles")
        _require_matching_range(
            request.get("at"),
            _iso(range_end),
            expected_start=range_start,
            expected_end=range_end,
            label="Trailokya geometry boundary",
        )
    return {
        "contract": TRAILOKYA_GEOMETRY_RANGE_CONTRACT,
        "schema_version": 1,
        "state": TRAILOKYA_GEOMETRY_RANGE_STATE,
        "instrument_identity": _required(
            raw_sbc.get("instrumentIdentity"),
            "sbcRange.instrumentIdentity",
        ),
        "range_start_utc": _iso(range_start),
        "range_end_utc": _iso(range_end),
        "source_profile_id": TRAILOKYA_SOURCE_ONLY_PROFILE_ID,
        "field_role": "INDEPENDENT_SYNCHRONIZED_COMPARISON",
        "aspect_relationship": "NOT_AUTOMATIC_CONFIRMATION",
        "magnitude_state": "NOT_CONFIGURED",
        "classicalCompletenessClaim": False,
        "source_gaps": list(TRAILOKYA_SOURCE_GAPS),
        "intervals": [],
        "reason": (
            "The selected Trailokya profile is approved only for source-only "
            "geometry. A score-free visible-range compiler is not yet implemented; "
            "no scored profile or guidance engine was used."
        ),
        "guardrails": {
            "read_only": True,
            "execution_allowed": False,
            "automatic_order_placement": False,
            "financially_validated": False,
            "acts_as_aspect_confirmation": False,
            "score_aggregation_used": False,
            "market_direction_inferred": False,
        },
    }


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
    if _trailokya_source_only_selected(raw_sbc):
        sbc_range = _trailokya_geometry_range_unavailable(
            raw_sbc,
            range_start=range_start,
            range_end=range_end,
        )
    else:
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
