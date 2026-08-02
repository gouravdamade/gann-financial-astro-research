"""Execution-locked chart-conditioned planetary aspect research foundation."""

from .chart_registry import ChartRegistry
from .evaluation import (
    compile_structural_prior,
    evaluate_runtime_event,
    explain_prior,
    explain_runtime,
    resolve_activation_paths,
)
from .fx_composer import compose_fx_pair_score
from .models import (
    ActivationPath,
    AspectPriorRecord,
    DynamicContribution,
    ExplanationEntry,
    FinancialDomainRecord,
    GeoLocation,
    GraphEdge,
    GraphNode,
    NatalAspectGraph,
    NatalChartSnapshot,
    NatalCondition,
    OrganizationChartHypothesis,
    PlanetFunctionalRole,
    RuntimeEvaluation,
    SourceRef,
    TransitNatalEvent,
    canonical_json,
    stable_hash,
)
from .profiles import ResearchProfiles, load_research_profiles
from .polarity_catalogue import (
    TargetAwarePolarityCatalogue,
    TargetAwarePolarityEntry,
    lookup_target_aware_polarity,
)
from .polarity_evidence import (
    TargetAwarePolarityEvidencePacket,
    TargetAwarePolarityEvidencePacketRegistry,
)
from .polarity_series import compile_categorical_visible_range
from .transits import adapt_explicit_tn_event

__all__ = [
    "ActivationPath",
    "AspectPriorRecord",
    "ChartRegistry",
    "adapt_explicit_tn_event",
    "compile_structural_prior",
    "compose_fx_pair_score",
    "DynamicContribution",
    "ExplanationEntry",
    "FinancialDomainRecord",
    "GeoLocation",
    "GraphEdge",
    "GraphNode",
    "NatalAspectGraph",
    "NatalChartSnapshot",
    "NatalCondition",
    "OrganizationChartHypothesis",
    "PlanetFunctionalRole",
    "TargetAwarePolarityCatalogue",
    "TargetAwarePolarityEntry",
    "TargetAwarePolarityEvidencePacket",
    "TargetAwarePolarityEvidencePacketRegistry",
    "ResearchProfiles",
    "evaluate_runtime_event",
    "explain_prior",
    "explain_runtime",
    "resolve_activation_paths",
    "RuntimeEvaluation",
    "SourceRef",
    "TransitNatalEvent",
    "canonical_json",
    "load_research_profiles",
    "lookup_target_aware_polarity",
    "compile_categorical_visible_range",
    "stable_hash",
]
