from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from ..models import TransitNatalEvent, stable_hash
from ..profiles import ResearchProfiles
from .orb_profile import validate_profile_orb


FORBIDDEN_RESEARCH_KEYS = {
    "future_return",
    "future_returns",
    "future_price",
    "known_outcome",
    "label",
    "outcome",
    "p_l",
    "pnl",
    "profit",
    "profit_loss",
    "ret_after_24h_pct",
    "ret_after_72h_pct",
    "target",
    "trade_result",
}


def _parse_aware(value: Any, field_name: str) -> datetime:
    if isinstance(value, datetime):
        result = value
    else:
        text = str(value or "").strip()
        if not text:
            raise ValueError(f"{field_name} is required")
        result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return result


def _optional_bool(value: Any, field_name: str) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    raise ValueError(
        f"{field_name} must be a boolean, 0/1, or a recognized boolean string"
    )


def _reject_forbidden_fields(value: Any, *, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            key = str(raw_key).strip().lower().replace("-", "_").replace(" ", "_")
            if key in FORBIDDEN_RESEARCH_KEYS or key.startswith("future_"):
                raise ValueError(
                    f"retrospective/outcome field is forbidden at {path}.{raw_key}"
                )
            _reject_forbidden_fields(item, path=f"{path}.{raw_key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_forbidden_fields(item, path=f"{path}[{index}]")


def adapt_explicit_tn_event(
    payload: Mapping[str, Any],
    profiles: ResearchProfiles,
) -> TransitNatalEvent:
    """Convert an explicit TN payload without recovering roles from sorted pairs."""

    _reject_forbidden_fields(payload)
    scope = str(payload.get("event_scope") or "").strip().upper()
    if scope != "TN":
        raise ValueError(
            "chart-conditioned aspect evaluation accepts explicit TN events only"
        )
    transit_body = (
        str(payload.get("event_transit_body") or payload.get("transit_body") or "")
        .strip()
        .upper()
    )
    natal_target = (
        str(
            payload.get("event_natal_body")
            or payload.get("natal_body")
            or payload.get("natal_target")
            or ""
        )
        .strip()
        .upper()
    )
    if not transit_body or not natal_target:
        raise ValueError("TN event requires explicit transit and natal target roles")
    role_status = (
        str(payload.get("event_role_resolution_status") or "explicit").strip().lower()
    )
    if role_status != "explicit":
        raise ValueError(
            "inferred or ambiguous TN role orientation is not accepted by this lab"
        )

    aspect_type = (
        str(payload.get("aspect_type") or payload.get("aspect") or "").strip().lower()
    )
    if not aspect_type:
        raise ValueError("aspect_type is required")
    try:
        observed = float(payload["observed_separation_deg"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "observed_separation_deg is required and must be numeric"
        ) from exc
    exact, orb, _ = validate_profile_orb(
        aspect_type=aspect_type,
        observed_separation_deg=observed,
        profiles=profiles,
    )
    if (
        payload.get("orb_deg") is not None
        and abs(float(payload["orb_deg"]) - orb) > 1e-6
    ):
        raise ValueError(
            "supplied orb_deg disagrees with deterministic angular geometry"
        )

    event_timestamp = _parse_aware(
        payload.get("event_timestamp_utc") or payload.get("event_timestamp"),
        "event_timestamp_utc",
    )
    available_at = _parse_aware(
        payload.get("evidence_available_at_utc") or event_timestamp,
        "evidence_available_at_utc",
    )
    duration = payload.get("duration_seconds")
    source_payload = dict(payload)
    chart_id = str(payload.get("chart_id") or "").strip()
    if not chart_id:
        raise ValueError("chart_id is required")
    return TransitNatalEvent(
        event_id=str(payload.get("event_id") or stable_hash(source_payload)[:24]),
        event_contract=str(payload.get("event_contract") or "EXPLICIT_TN_EVENT_V1"),
        chart_id=chart_id,
        event_timestamp_utc=event_timestamp,
        evidence_available_at_utc=available_at,
        transit_body=transit_body,
        natal_target=natal_target,
        aspect_type=aspect_type,
        exact_angle_deg=exact,
        observed_separation_deg=observed,
        orb_deg=orb,
        applying=_optional_bool(payload.get("applying"), "applying"),
        duration_seconds=(None if duration is None else float(duration)),
        source_payload_hash=stable_hash(source_payload),
    )
