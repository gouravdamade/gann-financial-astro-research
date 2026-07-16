from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .enums import (
    AbhijitPolicy,
    Ayanamsha,
    Center,
    EphemerisFallbackPolicy,
    NodeType,
    VaraBoundary,
    ZodiacMode,
)


def to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {item.name: to_primitive(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, dict):
        return {str(key): to_primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_primitive(item) for item in value]
    return value


@dataclass(frozen=True)
class GeoLocation:
    latitude: float
    longitude: float
    timezone: str
    altitude_m: float = 0.0

    def __post_init__(self) -> None:
        if not -90.0 <= float(self.latitude) <= 90.0:
            raise ValueError("latitude must be within [-90, 90]")
        if not -180.0 <= float(self.longitude) <= 180.0:
            raise ValueError("longitude must be within [-180, 180]")
        if not str(self.timezone).strip():
            raise ValueError("timezone is required")


@dataclass(frozen=True)
class AstroSettings:
    zodiac: ZodiacMode = ZodiacMode.SIDEREAL
    ayanamsha: Ayanamsha = Ayanamsha.RAMAN
    center: Center = Center.GEOCENTRIC
    node: NodeType = NodeType.TRUE_NODE
    fallback_policy: EphemerisFallbackPolicy = EphemerisFallbackPolicy.ALLOW_RECORDED


@dataclass(frozen=True)
class AbhijitInterval:
    start_deg: float
    end_deg: float
    source_rule_id: str
    start_inclusive: bool = True
    end_inclusive: bool = False

    def __post_init__(self) -> None:
        if not str(self.source_rule_id).strip():
            raise ValueError("Abhijit interval requires a source_rule_id")


@dataclass(frozen=True)
class PanchangaSettings:
    timezone: str = "Asia/Kolkata"
    vara_boundary: VaraBoundary = VaraBoundary.CIVIL_MIDNIGHT
    abhijit_policy: AbhijitPolicy = AbhijitPolicy.IGNORE_FOR_PLANET_PLACEMENT
    abhijit_interval: AbhijitInterval | None = None
    sunrise_algorithm: str = "SWISSEPH_STANDARD_APPARENT_UPPER_LIMB_V1"


@dataclass(frozen=True)
class EphemerisEvidence:
    provider: str
    library_version: str
    configured_path: str
    calculation_mode: str
    requested_flags: int
    returned_flags: int
    data_file: str | None
    data_file_sha256: str | None
    data_file_start_jd: float | None
    data_file_end_jd: float | None
    data_file_denum: int | None


@dataclass(frozen=True)
class PlanetPosition:
    body: str
    timestamp_utc: datetime
    longitude_deg: float
    latitude_deg: float
    distance_au: float
    longitude_speed_deg_per_day: float
    zodiac: ZodiacMode
    ayanamsha: Ayanamsha | None
    center: Center
    node: NodeType
    evidence: EphemerisEvidence
    derived_from: str | None = None


@dataclass(frozen=True)
class NakshatraMembership:
    name: str
    index_1: int | None
    pada: int | None
    fraction: float | None
    membership_kind: str
    source_rule_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class VaraState:
    weekday: str
    weekday_lord: str
    effective_local_date: str
    boundary_mode: VaraBoundary
    boundary_at_utc: datetime
    timezone: str
    algorithm: str
    status: str


@dataclass(frozen=True)
class PanchangaState:
    phase_angle_deg: float
    tithi_index: int
    tithi_name: str
    tithi_group: str
    paksha: str
    moon_phase: str
    karana_index: int
    karana_name: str
    yoga_angle_deg: float
    yoga_index: int
    yoga_name: str
    moon_nakshatra: NakshatraMembership
    sun_nakshatra: NakshatraMembership
    vara: VaraState
    rule_ids: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class SbcSnapshotRequest:
    at_utc: datetime
    profile_id: str
    bodies: tuple[str, ...]
    location: GeoLocation


@dataclass(frozen=True)
class SbcSnapshot:
    schema_version: str
    snapshot_id: str
    as_of_utc: datetime
    profile_id: str
    profile_hash: str
    astronomy_contract: str
    astro_settings: AstroSettings
    panchanga_settings: PanchangaSettings
    positions: tuple[PlanetPosition, ...]
    memberships: dict[str, tuple[NakshatraMembership, ...]]
    panchanga: PanchangaState
    source_ids: tuple[str, ...]
    research_locks: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)
