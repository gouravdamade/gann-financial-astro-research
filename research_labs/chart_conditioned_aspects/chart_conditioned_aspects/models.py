from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from typing import Any, Literal, Mapping


EvidenceClass = Literal[
    "CLASSICAL_TEXT",
    "COMMENTARIAL",
    "MODERN_FINANCIAL_EXTENSION",
    "EMPIRICAL_MARKET_EVIDENCE",
    "WORKSPACE_SPECIFICATION",
]
TimeAccuracy = Literal[
    "EXACT_TIME",
    "DOCUMENTED_EXCHANGE_OPEN",
    "DATE_ONLY_STABLE_MOON",
    "DATE_ONLY_UNSTABLE_MOON",
    "UNKNOWN",
]
DirectionalPrior = Literal["SUPPORTIVE", "ADVERSE", "MIXED", "INDETERMINATE"]
ActivationPrior = Literal["WEAK", "MODERATE", "STRONG", "EXCEPTIONAL", "UNKNOWN"]
VolatilityPrior = Literal["LOW", "ELEVATED", "HIGH", "UNKNOWN"]
FunctionalClass = Literal["SUPPORTIVE", "ADVERSE", "MIXED", "INDETERMINATE", "UNKNOWN"]


HOUSE_CAPABLE_ACCURACY = {"EXACT_TIME", "DOCUMENTED_EXCHANGE_OPEN"}


def _required(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _aware(value: datetime | None, field_name: str, *, optional: bool = False) -> None:
    if value is None:
        if optional:
            return
        raise ValueError(f"{field_name} is required")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _confidence(value: float, field_name: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{field_name} must be within [0, 1]")
    return number


def _canonical(value: Any) -> Any:
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        _canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest().upper()


def _normalized_pairs(
    values: Mapping[str, Any] | tuple[tuple[str, Any], ...],
    *,
    uppercase_keys: bool = True,
) -> tuple[tuple[str, Any], ...]:
    items = values.items() if isinstance(values, Mapping) else values
    normalized: dict[str, Any] = {}
    for raw_key, item in items:
        key = _required(str(raw_key), "mapping key")
        key = key.upper() if uppercase_keys else key
        if key in normalized:
            raise ValueError(f"duplicate mapping key: {key}")
        normalized[key] = item
    return tuple(sorted(normalized.items()))


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    locator: str
    evidence_class: EvidenceClass
    status: str
    confidence: float
    note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _required(self.source_id, "source_id"))
        object.__setattr__(self, "locator", _required(self.locator, "source locator"))
        object.__setattr__(self, "status", _required(self.status, "source status"))
        _confidence(self.confidence, "source confidence")


@dataclass(frozen=True)
class GeoLocation:
    name: str
    latitude: float | None
    longitude: float | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required(self.name, "location name"))
        if self.latitude is not None and not -90.0 <= float(self.latitude) <= 90.0:
            raise ValueError("latitude must be within [-90, 90]")
        if self.longitude is not None and not -180.0 <= float(self.longitude) <= 180.0:
            raise ValueError("longitude must be within [-180, 180]")


@dataclass(frozen=True)
class OrganizationChartHypothesis:
    chart_id: str
    instrument_id: str
    entity_id: str
    chart_type: str
    timestamp_utc: datetime | None
    location: GeoLocation
    sources: tuple[SourceRef, ...]
    time_accuracy: TimeAccuracy
    ayanamsa: str
    house_model: str
    astronomy_contract: str
    effective_from: date
    effective_to: date | None = None
    status: Literal["CANDIDATE", "ACCEPTED_RESEARCH", "REJECTED"] = "CANDIDATE"
    accepted_by: str | None = None
    accepted_at: datetime | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "chart_id",
            "instrument_id",
            "entity_id",
            "chart_type",
            "ayanamsa",
            "house_model",
            "astronomy_contract",
        ):
            object.__setattr__(
                self, field_name, _required(getattr(self, field_name), field_name)
            )
        _aware(self.timestamp_utc, "chart timestamp", optional=True)
        if self.time_accuracy in HOUSE_CAPABLE_ACCURACY:
            _aware(self.timestamp_utc, "house-capable chart timestamp")
            if self.location.latitude is None or self.location.longitude is None:
                raise ValueError("house-capable charts require latitude and longitude")
        if self.effective_to is not None and self.effective_to < self.effective_from:
            raise ValueError("effective_to cannot precede effective_from")
        if not self.sources:
            raise ValueError("chart hypothesis requires source provenance")
        if self.status == "ACCEPTED_RESEARCH":
            if not str(self.accepted_by or "").strip() or self.accepted_at is None:
                raise ValueError(
                    "accepted research charts require reviewer and acceptance time"
                )
            _aware(self.accepted_at, "chart acceptance time")

    @property
    def allows_houses(self) -> bool:
        return self.time_accuracy in HOUSE_CAPABLE_ACCURACY

    @property
    def chart_hash(self) -> str:
        return stable_hash(self)

    def effective_at(self, at: datetime) -> bool:
        current = at.date()
        return self.effective_from <= current and (
            self.effective_to is None or current <= self.effective_to
        )


@dataclass(frozen=True)
class NatalChartSnapshot:
    chart_id: str
    captured_at_utc: datetime
    planet_longitudes: tuple[tuple[str, float], ...]
    house_placements: tuple[tuple[str, int], ...] = ()
    retrograde_flags: tuple[tuple[str, bool], ...] = ()
    ascendant_sign: str | None = None
    astronomy_contract: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "chart_id", _required(self.chart_id, "chart_id"))
        object.__setattr__(
            self,
            "astronomy_contract",
            _required(self.astronomy_contract, "astronomy_contract"),
        )
        _aware(self.captured_at_utc, "snapshot timestamp")
        normalized_longitudes = tuple(
            (planet, float(longitude) % 360.0)
            for planet, longitude in _normalized_pairs(self.planet_longitudes)
        )
        normalized_houses = tuple(
            (planet, int(house))
            for planet, house in _normalized_pairs(self.house_placements)
        )
        if any(not 1 <= house <= 12 for _, house in normalized_houses):
            raise ValueError("house placements must be within [1, 12]")
        normalized_retrograde = tuple(
            (planet, bool(flag))
            for planet, flag in _normalized_pairs(self.retrograde_flags)
        )
        object.__setattr__(self, "planet_longitudes", normalized_longitudes)
        object.__setattr__(self, "house_placements", normalized_houses)
        object.__setattr__(self, "retrograde_flags", normalized_retrograde)
        if self.ascendant_sign is not None:
            object.__setattr__(
                self,
                "ascendant_sign",
                _required(self.ascendant_sign, "ascendant_sign").upper(),
            )

    @classmethod
    def from_mappings(
        cls,
        *,
        chart_id: str,
        captured_at_utc: datetime,
        planet_longitudes: Mapping[str, float],
        house_placements: Mapping[str, int] | None = None,
        retrograde_flags: Mapping[str, bool] | None = None,
        ascendant_sign: str | None,
        astronomy_contract: str,
    ) -> "NatalChartSnapshot":
        return cls(
            chart_id=chart_id,
            captured_at_utc=captured_at_utc,
            planet_longitudes=tuple(planet_longitudes.items()),
            house_placements=tuple((house_placements or {}).items()),
            retrograde_flags=tuple((retrograde_flags or {}).items()),
            ascendant_sign=ascendant_sign,
            astronomy_contract=astronomy_contract,
        )

    def longitude_for(self, planet: str) -> float | None:
        return dict(self.planet_longitudes).get(str(planet).upper())

    def house_for(self, planet: str) -> int | None:
        return dict(self.house_placements).get(str(planet).upper())

    def retrograde_for(self, planet: str) -> bool | None:
        return dict(self.retrograde_flags).get(str(planet).upper())

    @property
    def snapshot_hash(self) -> str:
        return stable_hash(self)


@dataclass(frozen=True)
class PlanetFunctionalRole:
    chart_id: str
    planet: str
    natural_nature: str
    owned_houses: tuple[int, ...]
    functional_class: FunctionalClass
    flags: tuple[str, ...]
    conflicts: tuple[str, ...]
    source_profile: str
    doctrine_status: str
    confidence: float
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "chart_id",
            "planet",
            "natural_nature",
            "source_profile",
            "doctrine_status",
        ):
            object.__setattr__(
                self, field_name, _required(getattr(self, field_name), field_name)
            )
        object.__setattr__(self, "planet", self.planet.upper())
        object.__setattr__(
            self,
            "owned_houses",
            tuple(sorted(set(int(item) for item in self.owned_houses))),
        )
        object.__setattr__(self, "flags", tuple(sorted(set(self.flags))))
        object.__setattr__(self, "conflicts", tuple(sorted(set(self.conflicts))))
        _confidence(self.confidence, "functional-role confidence")


@dataclass(frozen=True)
class NatalCondition:
    chart_id: str
    planet: str
    longitude: float
    sign: str
    house: int | None
    dignity: str
    retrograde: bool | None
    profile_id: str
    doctrine_status: str
    unknowns: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "longitude", float(self.longitude) % 360.0)
        if self.house is not None and not 1 <= int(self.house) <= 12:
            raise ValueError("natal condition house must be within [1, 12]")


@dataclass(frozen=True)
class FinancialDomainRecord:
    chart_id: str
    planet: str
    domain: str
    source_house: int
    mapping_profile: str
    evidence_class: EvidenceClass
    status: str
    explanation: str


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: Literal["PLANET", "HOUSE", "ANGLE", "YOGA"]
    label: str
    attributes: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_id", _required(self.node_id, "node_id"))
        object.__setattr__(self, "label", _required(self.label, "node label"))
        object.__setattr__(
            self, "attributes", _normalized_pairs(self.attributes, uppercase_keys=False)
        )


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    edge_type: Literal[
        "CONJUNCTION",
        "CONFIGURED_DRISHTI",
        "DISPOSITOR",
        "LORD_OF",
        "OCCUPIES_HOUSE",
        "YOGA_RELATION",
    ]
    status: str
    orb_deg: float | None = None
    evidence_refs: tuple[str, ...] = ()
    attributes: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", _required(self.source, "edge source"))
        object.__setattr__(self, "target", _required(self.target, "edge target"))
        if self.source == self.target:
            raise ValueError("self-referential graph edges are not allowed")
        if self.orb_deg is not None and float(self.orb_deg) < 0.0:
            raise ValueError("edge orb cannot be negative")
        object.__setattr__(
            self, "attributes", _normalized_pairs(self.attributes, uppercase_keys=False)
        )


@dataclass(frozen=True)
class NatalAspectGraph:
    natal_context_id: str
    chart_id: str
    chart_hash: str
    snapshot_hash: str
    doctrine_profile_id: str
    graph_profile_id: str
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    financial_domains: tuple[FinancialDomainRecord, ...]
    doctrine_status: str
    graph_hash: str
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        if self.execution_allowed:
            raise ValueError("natal research graph cannot authorize execution")
        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("graph node IDs must be unique")
        known = set(node_ids)
        for edge in self.edges:
            if edge.source not in known or edge.target not in known:
                raise ValueError("graph edge references an unknown node")


@dataclass(frozen=True)
class ActivationPath:
    target_node: str
    depth: int
    path: tuple[str, ...]
    edge_types: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.depth < 0:
            raise ValueError("activation depth cannot be negative")
        if self.depth != len(self.edge_types):
            raise ValueError("activation depth must equal edge count")


@dataclass(frozen=True)
class ExplanationEntry:
    entry_id: str
    category: str
    directional_effect: DirectionalPrior
    activation_effect: ActivationPrior
    volatility_effect: VolatilityPrior
    reason: str
    confidence: float
    evidence_refs: tuple[str, ...]
    uncertainty: str = ""

    def __post_init__(self) -> None:
        for field_name in ("entry_id", "category", "reason"):
            object.__setattr__(
                self, field_name, _required(getattr(self, field_name), field_name)
            )
        _confidence(self.confidence, "explanation confidence")


@dataclass(frozen=True)
class AspectPriorRecord:
    prior_id: str
    chart_id: str
    transit_body: str
    natal_target_type: Literal["PLANET", "ANGLE"]
    natal_target: str
    aspect_type: str
    natal_context_id: str
    directional_prior: DirectionalPrior
    activation_prior: ActivationPrior
    volatility_prior: VolatilityPrior
    explanation_ledger: tuple[ExplanationEntry, ...]
    unknowns: tuple[str, ...]
    doctrine_status: str
    profile_hash: str
    prior_hash: str
    execution_allowed: bool = False
    automatic_order_placement: bool = False

    def __post_init__(self) -> None:
        if self.execution_allowed or self.automatic_order_placement:
            raise ValueError("aspect-prior research records cannot authorize trading")


@dataclass(frozen=True)
class TransitNatalEvent:
    event_id: str
    event_contract: str
    chart_id: str
    event_timestamp_utc: datetime
    evidence_available_at_utc: datetime
    transit_body: str
    natal_target: str
    aspect_type: str
    exact_angle_deg: float
    observed_separation_deg: float
    orb_deg: float
    applying: bool | None
    duration_seconds: float | None
    source_payload_hash: str

    def __post_init__(self) -> None:
        _aware(self.event_timestamp_utc, "event timestamp")
        _aware(self.evidence_available_at_utc, "evidence availability timestamp")
        if self.evidence_available_at_utc > self.event_timestamp_utc:
            raise ValueError(
                "event geometry cannot become available after the event timestamp"
            )
        if float(self.orb_deg) < 0.0:
            raise ValueError("event orb cannot be negative")
        if self.duration_seconds is not None and float(self.duration_seconds) < 0.0:
            raise ValueError("event duration cannot be negative")


@dataclass(frozen=True)
class DynamicContribution:
    contribution_id: str
    available_at_utc: datetime
    category: str
    directional_effect: DirectionalPrior
    activation_effect: ActivationPrior
    volatility_effect: VolatilityPrior
    reason: str
    evidence_refs: tuple[str, ...]
    confidence: float

    def __post_init__(self) -> None:
        _aware(self.available_at_utc, "dynamic contribution availability")
        _confidence(self.confidence, "dynamic contribution confidence")


@dataclass(frozen=True)
class RuntimeEvaluation:
    event_id: str
    as_of_utc: datetime
    event_contract: str
    chart_id: str
    prior_id: str
    natal_context_id: str
    directional_result: DirectionalPrior
    activation_result: ActivationPrior
    volatility_result: VolatilityPrior
    activation_paths: tuple[ActivationPath, ...]
    dynamic_contributions: tuple[DynamicContribution, ...]
    conflict_flags: tuple[str, ...]
    unknowns: tuple[str, ...]
    timestamp_safe: bool
    evaluation_hash: str
    execution_allowed: bool = False
    automatic_order_placement: bool = False

    def __post_init__(self) -> None:
        _aware(self.as_of_utc, "evaluation as-of timestamp")
        if not self.timestamp_safe:
            raise ValueError("runtime evaluation must be timestamp-safe")
        if self.execution_allowed or self.automatic_order_placement:
            raise ValueError("runtime research evaluation cannot authorize trading")
