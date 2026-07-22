"""Experimental instrument-relative SBC and forex scoring foundation."""

from .connector import (
    CONNECTOR_CONTRACT,
    SnapshotConnectorResult,
    SnapshotTarget,
    UnscoredIdentityMatch,
    connect_snapshot_to_identity,
)

from .models import (
    AksharaMapping,
    AstroEvent,
    CurrencyScore,
    EconomicExposure,
    EntityChartHypothesis,
    FxPairScore,
    HypothesisRegistration,
    InfluenceContribution,
    InstrumentIdentity,
    NameInterval,
    RuleRecord,
    SourceCitation,
    TargetMapping,
    UncertaintySummary,
)
from .profiles import ExperimentalProfile, load_experimental_profile
from .scoring import (
    aggregate_component_score,
    build_currency_score,
    derive_fx_pair_score,
    resolve_time_valid_targets,
    validate_currency_invariants,
    validate_rule_profile,
)

__all__ = [
    "CONNECTOR_CONTRACT",
    "AksharaMapping",
    "AstroEvent",
    "CurrencyScore",
    "EconomicExposure",
    "EntityChartHypothesis",
    "ExperimentalProfile",
    "FxPairScore",
    "HypothesisRegistration",
    "InfluenceContribution",
    "InstrumentIdentity",
    "NameInterval",
    "RuleRecord",
    "SourceCitation",
    "SnapshotConnectorResult",
    "SnapshotTarget",
    "TargetMapping",
    "UncertaintySummary",
    "UnscoredIdentityMatch",
    "aggregate_component_score",
    "build_currency_score",
    "connect_snapshot_to_identity",
    "derive_fx_pair_score",
    "load_experimental_profile",
    "resolve_time_valid_targets",
    "validate_currency_invariants",
    "validate_rule_profile",
]
