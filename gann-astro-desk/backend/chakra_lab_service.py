from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sbc.chakra_lab import (  # noqa: E402
    ChakraLabActorSelection,
    ChakraLabEngine,
    ChakraLabRequest,
)
from sbc.models import GeoLocation  # noqa: E402
from sbc.vedha import DignityState, MotionClass, PlanetNature  # noqa: E402


DEFAULT_BODIES = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
    "RAHU",
    "KETU",
)
REQUEST_KEYS = {
    "at",
    "timezone",
    "latitude",
    "longitude",
    "altitudeM",
    "bodies",
    "actors",
    "foundationProfileId",
    "gridProfileId",
    "vedhaProfileId",
    "vowels",
    "nameInitials",
}
ACTOR_KEYS = {
    "body",
    "motionClass",
    "nature",
    "dignity",
    "mercuryAssociationNature",
}


def _reject_unknown(payload: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label} fields: {', '.join(unknown)}")


def _required_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} is required")
    return text


def _offset_datetime(value: Any) -> datetime:
    text = _required_text(value, "at").replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("at must include a UTC offset")
    return parsed


def _string_tuple(
    value: Any, label: str, default: tuple[str, ...] = ()
) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    normalized = tuple(str(item).strip().upper() for item in value)
    if any(not item for item in normalized):
        raise ValueError(f"{label} must contain non-empty values")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} must not contain duplicates")
    return normalized


def _optional_enum(enum_type: type[Any], value: Any, label: str) -> Any:
    text = str(value or "").strip().upper()
    if not text:
        return None
    try:
        return enum_type(text)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ValueError(f"{label} must be one of: {allowed}") from exc


def _actor(value: Any) -> ChakraLabActorSelection:
    if not isinstance(value, dict):
        raise ValueError("each actor must be an object")
    _reject_unknown(value, ACTOR_KEYS, "actor")
    dignity = _optional_enum(
        DignityState, value.get("dignity") or "ORDINARY", "dignity"
    )
    return ChakraLabActorSelection(
        body=_required_text(value.get("body"), "actor.body").upper(),
        motion_class=_optional_enum(
            MotionClass, value.get("motionClass"), "motionClass"
        ),
        nature=_optional_enum(PlanetNature, value.get("nature"), "nature"),
        dignity=dignity,
        mercury_association_nature=_optional_enum(
            PlanetNature,
            value.get("mercuryAssociationNature"),
            "mercuryAssociationNature",
        ),
    )


def build_chakra_lab_snapshot(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab request must be an object")
    _reject_unknown(payload, REQUEST_KEYS, "Chakra Lab request")
    actors_raw = payload.get("actors") or []
    if not isinstance(actors_raw, list):
        raise ValueError("actors must be an array")
    request = ChakraLabRequest(
        at=_offset_datetime(payload.get("at")),
        location=GeoLocation(
            latitude=float(payload.get("latitude", 28.6139)),
            longitude=float(payload.get("longitude", 77.2090)),
            timezone=str(payload.get("timezone") or "Asia/Kolkata"),
            altitude_m=float(payload.get("altitudeM", 0.0)),
        ),
        bodies=_string_tuple(payload.get("bodies"), "bodies", DEFAULT_BODIES),
        actors=tuple(_actor(item) for item in actors_raw),
        foundation_profile_id=str(
            payload.get("foundationProfileId") or "sbc_raman_foundation_v1"
        ),
        grid_profile_id=str(
            payload.get("gridProfileId") or "sbc_81_rotation_normalized_partial_v1"
        ),
        vedha_profile_id=str(
            payload.get("vedhaProfileId") or "phaladeepika_editor_vedha_guidance_v1"
        ),
        vowels=_string_tuple(payload.get("vowels"), "vowels"),
        name_initials=_string_tuple(payload.get("nameInitials"), "nameInitials"),
    )
    return ChakraLabEngine().snapshot(request).to_dict()
