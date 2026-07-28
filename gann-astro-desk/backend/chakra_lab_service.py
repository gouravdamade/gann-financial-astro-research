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
from sbc.atomic_intervals import (  # noqa: E402
    SbcAtomicIntervalCompiler,
    boundary_from_chakra_snapshot,
)
from sbc.audit_views import SbcLinkedAuditViewCompiler  # noqa: E402
from sbc.models import GeoLocation  # noqa: E402
from sbc.multidimensional_ledger import (  # noqa: E402
    SbcMultidimensionalLedgerCompiler,
)
from sbc.vedha import (  # noqa: E402
    GUIDANCE_MODEL_ID,
    DignityState,
    MotionClass,
    PlanetNature,
    load_vedha_profile,
)


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
AUDIT_REQUEST_KEYS = {
    "instrumentIdentity",
    "terminalEnd",
    "boundaries",
}
AUDIT_BOUNDARY_KEYS = {
    "reason",
    "request",
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


def _offset_datetime(value: Any, label: str = "at") -> datetime:
    text = _required_text(value, label).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
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


def _chakra_lab_request(payload: Any) -> ChakraLabRequest:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab request must be an object")
    _reject_unknown(payload, REQUEST_KEYS, "Chakra Lab request")
    actors_raw = payload.get("actors") or []
    if not isinstance(actors_raw, list):
        raise ValueError("actors must be an array")
    return ChakraLabRequest(
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


def build_chakra_lab_snapshot(payload: Any) -> dict[str, Any]:
    request = _chakra_lab_request(payload)
    return ChakraLabEngine().snapshot(request).to_dict()


def build_chakra_lab_audit(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab audit request must be an object")
    _reject_unknown(payload, AUDIT_REQUEST_KEYS, "Chakra Lab audit request")
    instrument_identity = _required_text(
        payload.get("instrumentIdentity"),
        "instrumentIdentity",
    )
    terminal_end = _offset_datetime(payload.get("terminalEnd"), "terminalEnd")
    boundaries_raw = payload.get("boundaries")
    if not isinstance(boundaries_raw, list) or not boundaries_raw:
        raise ValueError("boundaries must be a non-empty array")

    engine = ChakraLabEngine()
    boundaries = []
    for index, item in enumerate(boundaries_raw):
        if not isinstance(item, dict):
            raise ValueError(f"boundary {index + 1} must be an object")
        _reject_unknown(item, AUDIT_BOUNDARY_KEYS, f"boundary {index + 1}")
        reason = _required_text(item.get("reason"), f"boundary {index + 1}.reason")
        request = _chakra_lab_request(item.get("request"))
        snapshot = engine.snapshot(request)
        if snapshot.guidance is None:
            profile = load_vedha_profile(request.vedha_profile_id)
            boundary = boundary_from_chakra_snapshot(
                snapshot,
                boundary_reason=reason,
                unavailable_vedha_profile_id=profile.vedha_profile_id,
                unavailable_vedha_profile_hash=profile.profile_hash,
                unavailable_guidance_model_id=GUIDANCE_MODEL_ID,
            )
        else:
            boundary = boundary_from_chakra_snapshot(
                snapshot,
                boundary_reason=reason,
            )
        boundaries.append(boundary)

    atomic = SbcAtomicIntervalCompiler().compile(
        boundaries,
        terminal_end_utc=terminal_end,
    )
    ledger = SbcMultidimensionalLedgerCompiler().compile(
        atomic,
        instrument_identity=instrument_identity,
    )
    return SbcLinkedAuditViewCompiler().compile(ledger).to_dict()
