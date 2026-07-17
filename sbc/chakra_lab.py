from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .grid import CERTIFIED_LAYER_VALUES, CompiledGrid, compile_grid
from .models import GeoLocation, SbcSnapshot, SbcSnapshotRequest, to_primitive
from .snapshot import SbcFoundationEngine
from .vedha import (
    DignityState,
    MotionClass,
    PlanetNature,
    VedhaActor,
    VedhaGuidanceEngine,
    VedhaGuidanceReport,
)


CHAKRA_LAB_CONTRACT = "SBC_CHAKRA_LAB_SNAPSHOT_V1"
CHAKRA_LAB_SCHEMA_VERSION = 1
CURRENT_MOMENT_CONTEXT_CONTRACT = "SBC_CURRENT_MOMENT_CONTEXT_V1"
DEFAULT_FOUNDATION_PROFILE_ID = "sbc_raman_foundation_v1"
DEFAULT_GRID_PROFILE_ID = "sbc_81_rotation_normalized_partial_v1"
DEFAULT_VEDHA_PROFILE_ID = "phaladeepika_editor_vedha_guidance_v1"

ZODIAC_RASHIS_12 = (
    "MESHA",
    "VRISHABHA",
    "MITHUNA",
    "KARKA",
    "SIMHA",
    "KANYA",
    "TULA",
    "VRISCHIKA",
    "DHANUS",
    "MAKARA",
    "KUMBHA",
    "MEENA",
)
VEDHA_FIXED_BODIES = frozenset({"SUN", "MOON", "RAHU", "KETU"})
VEDHA_VARIABLE_BODIES = frozenset({"MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"})


@dataclass(frozen=True)
class ChakraLabActorSelection:
    body: str
    motion_class: MotionClass | str | None = None
    nature: PlanetNature | str | None = None
    dignity: DignityState | str = DignityState.ORDINARY
    mercury_association_nature: PlanetNature | str | None = None


@dataclass(frozen=True)
class ChakraLabRequest:
    at: datetime
    location: GeoLocation
    bodies: tuple[str, ...]
    actors: tuple[ChakraLabActorSelection, ...] = ()
    foundation_profile_id: str = DEFAULT_FOUNDATION_PROFILE_ID
    grid_profile_id: str = DEFAULT_GRID_PROFILE_ID
    vedha_profile_id: str = DEFAULT_VEDHA_PROFILE_ID
    vowels: tuple[str, ...] = ()
    name_initials: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChakraLabLayerContext:
    layer: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class ChakraLabPositionContext:
    body: str
    longitude_deg: float
    longitude_speed_deg_per_day: float
    rashi: str
    nakshatras: tuple[str, ...]


@dataclass(frozen=True)
class ChakraLabActorReadiness:
    body: str
    requested: bool
    status: str
    source_nakshatra: str
    motion_class: str | None
    reason: str


@dataclass(frozen=True)
class ChakraLabGuardrails:
    read_only: bool = True
    timestamp_safe: bool = True
    no_lookahead: bool = True
    execution_allowed: bool = False
    market_data_included: bool = False
    financially_validated: bool = False
    guidance_only: bool = True


@dataclass(frozen=True)
class ChakraLabSnapshot:
    contract: str
    schema_version: int
    snapshot_id: str
    requested_at_local: datetime
    as_of_utc: datetime
    evidence_cutoff_utc: datetime
    timezone: str
    location: GeoLocation
    foundation_snapshot: SbcSnapshot
    grid: CompiledGrid
    context_contract: str
    target_context: tuple[ChakraLabLayerContext, ...]
    position_context: tuple[ChakraLabPositionContext, ...]
    actor_readiness: tuple[ChakraLabActorReadiness, ...]
    guidance: VedhaGuidanceReport | None
    source_ids: tuple[str, ...]
    guardrails: ChakraLabGuardrails

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def rashi_from_longitude(longitude_deg: float) -> str:
    normalized = float(longitude_deg) % 360.0
    return ZODIAC_RASHIS_12[int(normalized // 30.0)]


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _normalized_values(values: tuple[str, ...], layer: str) -> tuple[str, ...]:
    normalized = tuple(dict.fromkeys(str(value).strip().upper() for value in values))
    if any(not value for value in normalized):
        raise ValueError(f"{layer} values must be non-empty")
    unknown = set(normalized) - CERTIFIED_LAYER_VALUES[layer]
    if unknown:
        raise ValueError(f"unknown {layer} values: {sorted(unknown)}")
    return normalized


def _machine_token(value: str) -> str:
    return "_".join(str(value).strip().upper().replace("-", " ").split())


def _actor_selections(
    selections: tuple[ChakraLabActorSelection, ...],
) -> dict[str, ChakraLabActorSelection]:
    normalized: dict[str, ChakraLabActorSelection] = {}
    for selection in selections:
        body = str(selection.body).strip().upper()
        if not body:
            raise ValueError("Chakra Lab actor body is required")
        if body in normalized:
            raise ValueError(f"duplicate Chakra Lab actor selection: {body}")
        normalized[body] = selection
    return normalized


def _current_context(
    foundation: SbcSnapshot,
    request: ChakraLabRequest,
) -> tuple[
    tuple[ChakraLabLayerContext, ...],
    tuple[ChakraLabPositionContext, ...],
]:
    nakshatras: list[str] = []
    rashis: list[str] = []
    positions: list[ChakraLabPositionContext] = []
    for position in foundation.positions:
        memberships = tuple(
            _machine_token(membership.name)
            for membership in foundation.memberships[position.body]
            if _machine_token(membership.name) in CERTIFIED_LAYER_VALUES["NAKSHATRA"]
        )
        if not memberships:
            raise ValueError(
                f"{position.body} has no certified SBC nakshatra membership"
            )
        rashi = rashi_from_longitude(position.longitude_deg)
        nakshatras.extend(memberships)
        rashis.append(rashi)
        positions.append(
            ChakraLabPositionContext(
                body=position.body,
                longitude_deg=position.longitude_deg,
                longitude_speed_deg_per_day=position.longitude_speed_deg_per_day,
                rashi=rashi,
                nakshatras=memberships,
            )
        )

    values: list[ChakraLabLayerContext] = [
        ChakraLabLayerContext("NAKSHATRA", tuple(dict.fromkeys(nakshatras))),
        ChakraLabLayerContext("RASHI", tuple(dict.fromkeys(rashis))),
        ChakraLabLayerContext("TITHI_GROUP", (foundation.panchanga.tithi_group,)),
    ]
    vowels = _normalized_values(request.vowels, "VOWEL")
    initials = _normalized_values(request.name_initials, "NAME_INITIAL")
    if vowels:
        values.append(ChakraLabLayerContext("VOWEL", vowels))
    if initials:
        values.append(ChakraLabLayerContext("NAME_INITIAL", initials))
    return tuple(values), tuple(positions)


def _moon_is_waning(foundation: SbcSnapshot) -> bool:
    return foundation.panchanga.moon_phase in {
        "WANING",
        "NEW_MOON_TITHI",
    }


def _resolve_actors(
    foundation: SbcSnapshot,
    selections: dict[str, ChakraLabActorSelection],
) -> tuple[tuple[VedhaActor, ...], tuple[ChakraLabActorReadiness, ...]]:
    available = {position.body for position in foundation.positions}
    unknown = sorted(set(selections) - available)
    if unknown:
        raise ValueError(
            "Chakra Lab actors must be present in the requested bodies: "
            + ", ".join(unknown)
        )

    actors: list[VedhaActor] = []
    readiness: list[ChakraLabActorReadiness] = []
    for position in foundation.positions:
        body = position.body
        selection = selections.get(body)
        source = _machine_token(foundation.memberships[body][0].name)
        if selection is None:
            readiness.append(
                ChakraLabActorReadiness(
                    body=body,
                    requested=False,
                    status="NOT_SELECTED",
                    source_nakshatra=source,
                    motion_class=None,
                    reason="body contributes to moment context but was not selected as a Vedha actor",
                )
            )
            continue
        if body not in VEDHA_FIXED_BODIES | VEDHA_VARIABLE_BODIES:
            readiness.append(
                ChakraLabActorReadiness(
                    body=body,
                    requested=True,
                    status="OUTSIDE_CERTIFIED_VEDHA_PROFILE",
                    source_nakshatra=source,
                    motion_class=None,
                    reason="body has no source-certified direction rule in this profile",
                )
            )
            continue
        supplied_motion = (
            str(selection.motion_class).strip().upper()
            if selection.motion_class is not None
            else None
        )
        if body in VEDHA_VARIABLE_BODIES and supplied_motion is None:
            readiness.append(
                ChakraLabActorReadiness(
                    body=body,
                    requested=True,
                    status="MOTION_REQUIRED",
                    source_nakshatra=source,
                    motion_class=None,
                    reason="DIRECT_SWIFT, MEAN, or RETROGRADE must be supplied explicitly",
                )
            )
            continue
        actor = VedhaActor(
            body=body,
            source_nakshatra=source,
            motion_class=selection.motion_class,
            nature=selection.nature,
            dignity=selection.dignity,
            moon_is_waning=_moon_is_waning(foundation) if body == "MOON" else None,
            mercury_association_nature=selection.mercury_association_nature,
        )
        actors.append(actor)
        readiness.append(
            ChakraLabActorReadiness(
                body=body,
                requested=True,
                status="READY",
                source_nakshatra=source,
                motion_class=supplied_motion,
                reason=(
                    "fixed source-profile direction"
                    if body in VEDHA_FIXED_BODIES
                    else "explicit caller-supplied motion class"
                ),
            )
        )
    return tuple(actors), tuple(readiness)


class ChakraLabEngine:
    def __init__(
        self,
        *,
        foundation_engine: SbcFoundationEngine | None = None,
        profile_root: Path | None = None,
    ) -> None:
        self.foundation_engine = foundation_engine or SbcFoundationEngine(
            profile_root=profile_root
        )

    def snapshot(self, request: ChakraLabRequest) -> ChakraLabSnapshot:
        if request.at.tzinfo is None or request.at.utcoffset() is None:
            raise ValueError("Chakra Lab timestamps must include a UTC offset")
        foundation = self.foundation_engine.snapshot(
            SbcSnapshotRequest(
                at_utc=request.at,
                profile_id=request.foundation_profile_id,
                bodies=request.bodies,
                location=request.location,
            )
        )
        grid = compile_grid(request.grid_profile_id)
        vedha_engine = VedhaGuidanceEngine(request.vedha_profile_id)
        if vedha_engine.grid.grid_profile_id != grid.grid_profile_id:
            raise ValueError(
                "selected Vedha and grid profiles do not share the same grid profile"
            )
        target_context, position_context = _current_context(foundation, request)
        actors, readiness = _resolve_actors(
            foundation, _actor_selections(request.actors)
        )
        context_mapping = {item.layer: item.values for item in target_context}
        guidance = vedha_engine.evaluate(actors, context_mapping) if actors else None
        as_of_utc = foundation.as_of_utc.astimezone(timezone.utc)
        requested_at_local = as_of_utc.astimezone(ZoneInfo(request.location.timezone))
        source_ids = tuple(
            dict.fromkeys(
                (
                    *foundation.source_ids,
                    *grid.source_ids,
                    *(item.source_id for item in vedha_engine.profile.citations),
                )
            )
        )
        guardrails = ChakraLabGuardrails()
        identity = {
            "contract": CHAKRA_LAB_CONTRACT,
            "schema_version": CHAKRA_LAB_SCHEMA_VERSION,
            "requested_at_local": requested_at_local.isoformat(),
            "as_of_utc": as_of_utc.isoformat(),
            "evidence_cutoff_utc": as_of_utc.isoformat(),
            "timezone": request.location.timezone,
            "location": to_primitive(request.location),
            "foundation_snapshot_id": foundation.snapshot_id,
            "grid_profile_id": grid.grid_profile_id,
            "grid_profile_hash": grid.profile_hash,
            "target_context": to_primitive(target_context),
            "actor_readiness": to_primitive(readiness),
            "guidance": to_primitive(guidance),
            "source_ids": source_ids,
            "guardrails": to_primitive(guardrails),
        }
        return ChakraLabSnapshot(
            contract=CHAKRA_LAB_CONTRACT,
            schema_version=CHAKRA_LAB_SCHEMA_VERSION,
            snapshot_id=_canonical_hash(identity),
            requested_at_local=requested_at_local,
            as_of_utc=as_of_utc,
            evidence_cutoff_utc=as_of_utc,
            timezone=request.location.timezone,
            location=request.location,
            foundation_snapshot=foundation,
            grid=grid,
            context_contract=CURRENT_MOMENT_CONTEXT_CONTRACT,
            target_context=target_context,
            position_context=position_context,
            actor_readiness=readiness,
            guidance=guidance,
            source_ids=source_ids,
            guardrails=guardrails,
        )
