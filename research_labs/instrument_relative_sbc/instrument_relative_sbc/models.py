from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal


SourceTier = Literal[
    "classical_text",
    "commentary",
    "modern_book",
    "academic",
    "market_reference",
    "experimental_note",
]
RuleStatus = Literal["verified", "provisional", "disputed", "disabled"]
ReviewStatus = Literal["unreviewed", "accepted", "rejected", "requires_review"]
DirectionHypothesis = Literal[
    "base_outperformance",
    "quote_outperformance",
    "no_edge",
    "unknown",
]


def _required(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _confidence(value: float, field_name: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{field_name} must be within [0, 1]")
    return number


@dataclass(frozen=True)
class SourceCitation:
    source_id: str
    title: str
    source_tier: SourceTier
    author_or_editor: str | None = None
    edition: str | None = None
    publication_year: int | None = None
    locator: str | None = None
    url: str | None = None
    access_date: date | None = None
    excerpt_hash: str | None = None
    rights_note: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _required(self.source_id, "source_id"))
        object.__setattr__(self, "title", _required(self.title, "title"))


@dataclass(frozen=True)
class NameInterval:
    raw_name: str
    spoken_form: str | None
    valid_from: date
    valid_to: date | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_name", _required(self.raw_name, "raw_name"))
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("name interval valid_to cannot precede valid_from")

    def valid_at(self, at: datetime) -> bool:
        current = at.date()
        return self.valid_from <= current and (
            self.valid_to is None or current <= self.valid_to
        )


@dataclass(frozen=True)
class TargetMapping:
    target_type: Literal[
        "akshara",
        "nakshatra",
        "rashi",
        "tithi",
        "vara",
        "chart_point",
        "sector",
        "country",
    ]
    target_value: str
    mapping_method: str
    confidence: float
    review_status: ReviewStatus
    valid_from: date
    valid_to: date | None = None
    provenance: tuple[SourceCitation, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "target_value",
            _required(self.target_value, "target_value"),
        )
        object.__setattr__(
            self,
            "mapping_method",
            _required(self.mapping_method, "mapping_method"),
        )
        _confidence(self.confidence, "mapping confidence")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("mapping valid_to cannot precede valid_from")

    def valid_at(self, at: datetime) -> bool:
        current = at.date()
        return self.valid_from <= current and (
            self.valid_to is None or current <= self.valid_to
        )


@dataclass(frozen=True)
class AksharaMapping:
    raw_name: str
    spoken_form: str
    candidate_akshara: str
    mapping_method: Literal["manual", "dictionary", "transliteration", "llm_suggestion"]
    language: str
    confidence: float
    review_status: ReviewStatus
    valid_from: date
    valid_to: date | None = None
    reviewer: str | None = None
    provenance: tuple[SourceCitation, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("raw_name", "spoken_form", "candidate_akshara", "language"):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name),
            )
        _confidence(self.confidence, "akshara confidence")
        if (
            self.mapping_method == "llm_suggestion"
            and self.review_status == "accepted"
            and not str(self.reviewer or "").strip()
        ):
            raise ValueError("accepted LLM akshara suggestions require a human reviewer")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("akshara valid_to cannot precede valid_from")

    def valid_at(self, at: datetime) -> bool:
        current = at.date()
        return self.valid_from <= current and (
            self.valid_to is None or current <= self.valid_to
        )


@dataclass(frozen=True)
class EntityChartHypothesis:
    hypothesis_id: str
    hypothesis_type: Literal[
        "legal_incorporation",
        "business_commencement",
        "ipo_open",
        "first_trade",
        "major_reorganisation",
        "country_foundation",
        "central_bank_foundation",
        "currency_launch",
    ]
    timestamp_utc: datetime
    timezone_source: str
    latitude: float
    longitude: float
    uncertainty_note: str
    valid_from: date
    valid_to: date | None = None
    provenance: tuple[SourceCitation, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "hypothesis_id",
            _required(self.hypothesis_id, "hypothesis_id"),
        )
        if self.timestamp_utc.tzinfo is None:
            raise ValueError("entity chart timestamp must be timezone-aware")
        if not -90.0 <= float(self.latitude) <= 90.0:
            raise ValueError("latitude must be within [-90, 90]")
        if not -180.0 <= float(self.longitude) <= 180.0:
            raise ValueError("longitude must be within [-180, 180]")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("chart hypothesis valid_to cannot precede valid_from")

    def valid_at(self, at: datetime) -> bool:
        current = at.date()
        return self.valid_from <= current and (
            self.valid_to is None or current <= self.valid_to
        )


@dataclass(frozen=True)
class EconomicExposure:
    exposure_type: Literal[
        "producer",
        "consumer",
        "exporter",
        "importer",
        "lender",
        "borrower",
        "safe_haven",
        "rate_sensitive",
        "commodity_input",
        "commodity_output",
    ]
    domain_id: str
    direction: float
    confidence: float
    valid_from: date
    valid_to: date | None
    source: SourceCitation

    def __post_init__(self) -> None:
        object.__setattr__(self, "domain_id", _required(self.domain_id, "domain_id"))
        _confidence(self.confidence, "exposure confidence")
        if not -1.0 <= float(self.direction) <= 1.0:
            raise ValueError("exposure direction must be within [-1, 1]")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("exposure valid_to cannot precede valid_from")


@dataclass(frozen=True)
class InstrumentIdentity:
    instrument_id: str
    symbol: str
    asset_class: Literal[
        "equity",
        "index",
        "commodity",
        "currency",
        "fx_pair",
        "crypto",
    ]
    legal_name: str
    spoken_name: str | None = None
    name_history: tuple[NameInterval, ...] = ()
    akshara_candidates: tuple[AksharaMapping, ...] = ()
    rashi_candidates: tuple[TargetMapping, ...] = ()
    nakshatra_candidates: tuple[TargetMapping, ...] = ()
    entity_chart_hypotheses: tuple[EntityChartHypothesis, ...] = ()
    country_codes: tuple[str, ...] = ()
    sector_codes: tuple[str, ...] = ()
    economic_exposures: tuple[EconomicExposure, ...] = ()
    benchmark_ids: tuple[str, ...] = ()
    provenance: tuple[SourceCitation, ...] = ()
    base_currency: str | None = None
    quote_currency: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("instrument_id", "symbol", "legal_name"):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name),
            )
        if self.asset_class == "fx_pair":
            if not self.base_currency or not self.quote_currency:
                raise ValueError("FX identity requires explicit base and quote currencies")
            object.__setattr__(self, "base_currency", self.base_currency.upper())
            object.__setattr__(self, "quote_currency", self.quote_currency.upper())
            if self.base_currency == self.quote_currency:
                raise ValueError("FX base and quote currencies must differ")


@dataclass(frozen=True)
class AstroEvent:
    event_id: str
    event_family: Literal[
        "sbc_vedha",
        "sbc_latta",
        "angular_aspect",
        "transit",
        "mundane",
    ]
    timestamp_utc: datetime
    source_body: str
    target_body_or_cell: str | None
    geometry: dict[str, Any]
    motion_state: dict[str, Any]
    strength_features: dict[str, Any]
    rule_profile_id: str
    provenance: tuple[SourceCitation, ...]

    def __post_init__(self) -> None:
        for field_name in ("event_id", "source_body", "rule_profile_id"):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name),
            )
        if self.timestamp_utc.tzinfo is None:
            raise ValueError("event timestamp must be timezone-aware")
        if not self.provenance:
            raise ValueError("event provenance is required")


@dataclass(frozen=True)
class RuleRecord:
    rule_id: str
    rule_family: str
    profile_id: str
    status: RuleStatus
    source_citations: tuple[SourceCitation, ...]
    normalized_condition: dict[str, Any]
    normalized_effect: dict[str, Any]
    confidence: float
    translation_notes: str | None = None
    interpretation_notes: str | None = None
    reviewer: str | None = None
    verified_at: datetime | None = None

    def __post_init__(self) -> None:
        for field_name in ("rule_id", "rule_family", "profile_id"):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name),
            )
        _confidence(self.confidence, "rule confidence")
        if not self.source_citations:
            raise ValueError("rule source citations are required")
        if self.status == "verified":
            if not self.reviewer or self.verified_at is None:
                raise ValueError("verified rules require reviewer and verified_at")
            if any(not citation.locator for citation in self.source_citations):
                raise ValueError("verified rule citations require source locators")


@dataclass(frozen=True)
class InfluenceContribution:
    contribution_id: str
    instrument_id: str
    timestamp_utc: datetime
    event_id: str
    target_type: str
    target_value: str
    rule_id: str
    rule_profile_id: str
    semantic_effect: str
    raw_polarity: int | Literal["mixed", "unknown"]
    intensity: float
    relevance: float
    mapping_confidence: float
    source_confidence: float
    signed_value: float | None
    explanation: str
    provenance: tuple[SourceCitation, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "contribution_id",
            "instrument_id",
            "event_id",
            "target_type",
            "target_value",
            "rule_id",
            "rule_profile_id",
            "semantic_effect",
            "explanation",
        ):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name),
            )
        if self.timestamp_utc.tzinfo is None:
            raise ValueError("contribution timestamp must be timezone-aware")
        for value, name in (
            (self.intensity, "intensity"),
            (self.relevance, "relevance"),
            (self.mapping_confidence, "mapping confidence"),
            (self.source_confidence, "source confidence"),
        ):
            _confidence(value, name)
        if self.raw_polarity not in {-1, 0, 1, "mixed", "unknown"}:
            raise ValueError("raw polarity is invalid")
        if self.raw_polarity in {"mixed", "unknown"} and self.signed_value is not None:
            raise ValueError("mixed/unknown polarity cannot silently become a number")
        if isinstance(self.raw_polarity, int):
            expected = (
                float(self.raw_polarity)
                * self.intensity
                * self.relevance
                * self.mapping_confidence
                * self.source_confidence
            )
            if self.signed_value is None or abs(self.signed_value - expected) > 1e-12:
                raise ValueError("signed contribution does not match declared factors")
        if not self.provenance:
            raise ValueError("contribution provenance is required")


@dataclass(frozen=True)
class UncertaintySummary:
    reasons: tuple[str, ...] = ()
    source_uncertainty: float = 0.0
    identity_uncertainty: float = 0.0
    chart_uncertainty: float = 0.0
    statistical_uncertainty: float = 1.0

    def __post_init__(self) -> None:
        for value, name in (
            (self.source_uncertainty, "source uncertainty"),
            (self.identity_uncertainty, "identity uncertainty"),
            (self.chart_uncertainty, "chart uncertainty"),
            (self.statistical_uncertainty, "statistical uncertainty"),
        ):
            _confidence(value, name)


@dataclass(frozen=True)
class CurrencyScore:
    currency: str
    timestamp_utc: datetime
    profile_id: str
    sbc_identity_score: float | None
    currency_event_scores: dict[str, float | None]
    central_bank_scores: dict[str, float | None]
    country_scores: dict[str, float | None]
    mundane_domain_score: float | None
    combined_score: float | None
    component_weights: dict[str, float]
    contributions: tuple[InfluenceContribution, ...]
    uncertainty: UncertaintySummary
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "currency", _required(self.currency, "currency").upper())
        object.__setattr__(self, "profile_id", _required(self.profile_id, "profile_id"))
        if self.timestamp_utc.tzinfo is None:
            raise ValueError("currency score timestamp must be timezone-aware")
        if self.execution_allowed:
            raise ValueError("experimental currency score cannot authorize execution")


@dataclass(frozen=True)
class FxPairScore:
    pair: str
    base_currency: str
    quote_currency: str
    timestamp_utc: datetime
    base_score: CurrencyScore
    quote_score: CurrencyScore
    differential: float | None
    signed_common_mode: float | None
    joint_activation: float | None
    direction_hypothesis: DirectionHypothesis
    confidence_band: str
    invariant_checks: dict[str, bool]
    explanation: tuple[str, ...]
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        if self.execution_allowed:
            raise ValueError("experimental FX score cannot authorize execution")


@dataclass(frozen=True)
class HypothesisRegistration:
    hypothesis_id: str
    created_at: datetime
    feature_profile_ids: tuple[str, ...]
    mapping_snapshot_hash: str
    training_period: tuple[date, date]
    validation_period: tuple[date, date]
    final_holdout_period: tuple[date, date]
    primary_metric: str
    success_threshold: float
    allowed_transformations: tuple[str, ...]
    frozen: bool
    result_status: Literal["registered", "failed", "passed", "retired"] = "registered"

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError("hypothesis creation timestamp must be timezone-aware")
        if not self.frozen:
            raise ValueError("research hypotheses must be frozen before evaluation")
