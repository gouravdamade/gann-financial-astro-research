from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROFILE_ROOT, CompiledProfile, load_profile
from .enums import SUPPORTED_BODIES
from .ephemeris import SwissEphemerisProvider
from .models import SbcSnapshot, SbcSnapshotRequest, to_primitive
from .nakshatra import sbc_memberships
from .panchanga import build_panchanga


SNAPSHOT_SCHEMA_VERSION = "1.0.0"
RESEARCH_LOCKS = {
    "grid": False,
    "vedha": False,
    "latta": False,
    "scoring": False,
    "trades": False,
    "market_data": False,
    "auto_suggest": False,
    "mt5_execution": False,
}


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _normalize_bodies(bodies: tuple[str, ...]) -> tuple[str, ...]:
    normalized = [str(body).strip().upper() for body in bodies]
    if not normalized:
        raise ValueError("SBC snapshot requires at least one requested body")
    for required in ("SUN", "MOON"):
        if required not in normalized:
            normalized.append(required)
    if len(set(normalized)) != len(normalized):
        raise ValueError("SBC snapshot body list contains duplicates")
    unknown = sorted(set(normalized) - set(SUPPORTED_BODIES))
    if unknown:
        raise ValueError(f"unsupported bodies: {', '.join(unknown)}")
    return tuple(normalized)


def _scientific_identity(
    request: SbcSnapshotRequest,
    profile: CompiledProfile,
    positions: tuple[Any, ...],
    memberships: dict[str, tuple[Any, ...]],
    panchanga: Any,
) -> dict[str, Any]:
    position_facts = [
        {
            "body": item.body,
            "longitude_deg": item.longitude_deg,
            "latitude_deg": item.latitude_deg,
            "distance_au": item.distance_au,
            "longitude_speed_deg_per_day": item.longitude_speed_deg_per_day,
            "derived_from": item.derived_from,
            "ephemeris_sha256": item.evidence.data_file_sha256,
            "calculation_mode": item.evidence.calculation_mode,
        }
        for item in positions
    ]
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "as_of_utc": request.at_utc.astimezone(timezone.utc).isoformat(),
        "profile_id": profile.profile_id,
        "profile_hash": profile.profile_hash,
        "location": to_primitive(request.location),
        "positions": position_facts,
        "memberships": to_primitive(memberships),
        "panchanga": to_primitive(panchanga),
        "research_locks": RESEARCH_LOCKS,
    }


class SbcFoundationEngine:
    def __init__(
        self,
        profile_root: Path | None = None,
        ephemeris_provider: SwissEphemerisProvider | None = None,
    ) -> None:
        self.profile_root = profile_root or PROFILE_ROOT
        self.ephemeris_provider = ephemeris_provider or SwissEphemerisProvider()

    def snapshot(self, request: SbcSnapshotRequest) -> SbcSnapshot:
        if request.at_utc.tzinfo is None or request.at_utc.utcoffset() is None:
            raise ValueError("SBC snapshot timestamps must be timezone-aware")
        profile = load_profile(request.profile_id, self.profile_root)
        if request.location.timezone != profile.panchanga_settings.timezone:
            raise ValueError(
                "location timezone must match profile Panchanga timezone; "
                f"got {request.location.timezone!r} and {profile.panchanga_settings.timezone!r}"
            )
        bodies = _normalize_bodies(request.bodies)
        positions = self.ephemeris_provider.positions(
            request.at_utc,
            bodies,
            profile.astro_settings,
            request.location,
        )
        by_body = {item.body: item for item in positions}
        memberships = {
            item.body: sbc_memberships(
                item.longitude_deg,
                profile.panchanga_settings.abhijit_policy,
                profile.panchanga_settings.abhijit_interval,
            )
            for item in positions
        }
        panchanga = build_panchanga(
            request.at_utc,
            by_body["SUN"].longitude_deg,
            by_body["MOON"].longitude_deg,
            profile.panchanga_settings,
            profile.astro_settings,
            request.location,
            self.ephemeris_provider,
        )
        identity = _scientific_identity(request, profile, positions, memberships, panchanga)
        astronomy_contract = (
            f"SBC_{profile.astro_settings.ayanamsha.value}_"
            f"{profile.astro_settings.node.value}_SWISSEPH_FOUNDATION_V1"
        )
        return SbcSnapshot(
            schema_version=SNAPSHOT_SCHEMA_VERSION,
            snapshot_id=_canonical_hash(identity),
            as_of_utc=request.at_utc.astimezone(timezone.utc),
            profile_id=profile.profile_id,
            profile_hash=profile.profile_hash,
            astronomy_contract=astronomy_contract,
            astro_settings=profile.astro_settings,
            panchanga_settings=profile.panchanga_settings,
            positions=positions,
            memberships=memberships,
            panchanga=panchanga,
            source_ids=profile.source_ids,
            research_locks=dict(RESEARCH_LOCKS),
        )
