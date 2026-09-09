"""Outcome-blind contracts for machine-assisted astrology interpretation.

This module is intentionally a research architecture boundary.  It keeps
astronomy/source facts, astrology interpretation, experimental market bridges,
currency-side state, and explanation separate.  It does not load market data,
the durable Founder Review store, the polarity catalogue, or the unsigned
multi-oscillator runtime.

The synthetic interpreter is deliberately restricted to synthetic identities.
The real April 2025 helper reads only immutable blank-packet identity and audit
records and always reports an unsigned, no-market-bridge result.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

import founder_review_workbench as founder_review


INTERPRETATION_CONTRACT = "MACHINE_ASSISTED_ASTROLOGICAL_INTERPRETATION_V1"
INTERPRETATION_SCHEMA_VERSION = 1
HYPOTHESIS_REGISTRY_CONTRACT = "MACHINE_ASSISTED_EXPERIMENTAL_MARKET_HYPOTHESIS_REGISTRY_V1"
HYPOTHESIS_REGISTRY_SCHEMA_VERSION = 1
IDENTITY_ONLY_COVERAGE_CONTRACT = "MO_R4A_P0_REAL_24_IDENTITY_ONLY_COVERAGE_V1"
IDENTITY_ONLY_COVERAGE_SCHEMA_VERSION = 1
DEFAULT_HYPOTHESIS_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "configs"
    / "research"
    / "machine_interpretation"
    / "experimental_market_hypothesis_registry_v1.json"
)


class MachineInterpretationError(ValueError):
    """Raised when a machine-assisted interpretation would cross a contract boundary."""


class InterpretationMode(str, Enum):
    SOURCE_CERTIFIED = "SOURCE_CERTIFIED"
    EXPERIMENTAL_PROFILED = "EXPERIMENTAL_PROFILED"
    EXPLORATORY_UNSIGNED = "EXPLORATORY_UNSIGNED"


class AstrologyState(str, Enum):
    SUPPORTIVE_ASTRO_STATE = "SUPPORTIVE_ASTRO_STATE"
    ADVERSE_ASTRO_STATE = "ADVERSE_ASTRO_STATE"
    MIXED_ASTRO_STATE = "MIXED_ASTRO_STATE"
    NEUTRAL_ASTRO_STATE = "NEUTRAL_ASTRO_STATE"
    UNKNOWN_ASTRO_STATE = "UNKNOWN_ASTRO_STATE"


class MarketBridgeStatus(str, Enum):
    SOURCE_BACKED_MARKET_BRIDGE = "SOURCE_BACKED_MARKET_BRIDGE"
    EXPERIMENTAL_MARKET_HYPOTHESIS = "EXPERIMENTAL_MARKET_HYPOTHESIS"
    NO_AUTHORIZED_MARKET_BRIDGE = "NO_AUTHORIZED_MARKET_BRIDGE"


class CurrencyPressureState(str, Enum):
    SUPPORTIVE = "SUPPORTIVE"
    ADVERSE = "ADVERSE"
    MIXED = "MIXED"
    NEUTRAL = "NEUTRAL"
    UNKNOWN_MORE_EVIDENCE_REQUIRED = "UNKNOWN_MORE_EVIDENCE_REQUIRED"


class SourceEvidenceStatus(str, Enum):
    SOURCE_CLOSED = "SOURCE_CLOSED"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"


class HypothesisApprovalStatus(str, Enum):
    SYNTHETIC_TEST_ONLY = "SYNTHETIC_TEST_ONLY"
    AUTHORIZED_FOR_BLINDED_TEST = "AUTHORIZED_FOR_BLINDED_TEST"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"


def _required(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise MachineInterpretationError(f"{label} is required")
    return text


def _utc(value: Any, label: str) -> str:
    text = _required(value, label)
    if not text.endswith("Z"):
        raise MachineInterpretationError(f"{label} must be explicit UTC ISO text")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise MachineInterpretationError(f"{label} must be explicit UTC ISO text") from exc
    if parsed.tzinfo is None:
        raise MachineInterpretationError(f"{label} must be explicit UTC ISO text")
    return text


def _enum(value: Any, enum_type: type[Enum], label: str) -> Enum:
    try:
        return enum_type(value)
    except ValueError as exc:
        raise MachineInterpretationError(f"Unsupported {label}: {value!r}") from exc


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()
    except FileNotFoundError as exc:
        raise MachineInterpretationError(f"Required immutable identity input is missing: {path}") from exc


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MachineInterpretationError(f"Required {label} is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MachineInterpretationError(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(raw, dict):
        raise MachineInterpretationError(f"{label} must be a JSON object: {path}")
    return raw


@dataclass(frozen=True)
class SourceLocator:
    source_id: str
    edition: str
    locator: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _required(self.source_id, "Source locator source_id"))
        object.__setattr__(self, "edition", _required(self.edition, "Source locator edition"))
        object.__setattr__(self, "locator", _required(self.locator, "Source locator locator"))


@dataclass(frozen=True)
class SourceMeasurement:
    """A literal source measurement that is explicitly not an oscillator magnitude."""

    component_id: str
    literal_value: str
    locator: SourceLocator

    def __post_init__(self) -> None:
        object.__setattr__(self, "component_id", _required(self.component_id, "Source measurement component_id"))
        object.__setattr__(self, "literal_value", _required(self.literal_value, "Source measurement literal_value"))


@dataclass(frozen=True)
class SourceOperatorEvidence:
    """Source-bound operator output before any market/currency interpretation."""

    operator_contract_id: str
    source_status: SourceEvidenceStatus
    astrological_state: AstrologyState
    locators: tuple[SourceLocator, ...]
    rationale: str
    unresolved_dependencies: tuple[str, ...] = ()
    source_measurements: tuple[SourceMeasurement, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "operator_contract_id", _required(self.operator_contract_id, "operator_contract_id"))
        object.__setattr__(self, "source_status", _enum(self.source_status, SourceEvidenceStatus, "source_status"))
        object.__setattr__(self, "astrological_state", _enum(self.astrological_state, AstrologyState, "astrological_state"))
        object.__setattr__(self, "rationale", _required(self.rationale, "source operator rationale"))
        locators = tuple(self.locators)
        if not locators:
            raise MachineInterpretationError("Source operator evidence requires at least one exact source locator")
        if not all(isinstance(locator, SourceLocator) for locator in locators):
            raise MachineInterpretationError("Source operator locators must be SourceLocator instances")
        object.__setattr__(self, "locators", locators)
        dependencies = tuple(_required(item, "unresolved dependency") for item in self.unresolved_dependencies)
        object.__setattr__(self, "unresolved_dependencies", dependencies)
        measurements = tuple(self.source_measurements)
        if not all(isinstance(item, SourceMeasurement) for item in measurements):
            raise MachineInterpretationError("Source measurements must be SourceMeasurement instances")
        object.__setattr__(self, "source_measurements", measurements)
        if self.source_status is not SourceEvidenceStatus.SOURCE_CLOSED and self.astrological_state is not AstrologyState.UNKNOWN_ASTRO_STATE:
            raise MachineInterpretationError("Partial or unresolved source evidence must remain UNKNOWN_ASTRO_STATE")


@dataclass(frozen=True)
class ExperimentalMarketHypothesis:
    """Versioned modern bridge; never a source-certified financial conclusion."""

    hypothesis_id: str
    version: str
    author: str
    created_at_utc: str
    input_operator_contract_ids: tuple[str, ...]
    astrological_state_condition: AstrologyState
    target_side: str
    currency_pressure_state: CurrencyPressureState
    reasoning: str
    source_dependencies: tuple[str, ...]
    experimental_assumptions: tuple[str, ...]
    prohibited_generalizations: tuple[str, ...]
    validation_status: str
    outcome_data_seen_at_creation: bool
    approval_status: HypothesisApprovalStatus
    signed_unit_if_configured: None = None
    magnitude_configured: bool = False
    mode: InterpretationMode = InterpretationMode.EXPERIMENTAL_PROFILED
    hypothesis_hash: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "hypothesis_id", _required(self.hypothesis_id, "hypothesis_id"))
        object.__setattr__(self, "version", _required(self.version, "hypothesis version"))
        object.__setattr__(self, "author", _required(self.author, "hypothesis author"))
        object.__setattr__(self, "created_at_utc", _utc(self.created_at_utc, "hypothesis created_at_utc"))
        operator_ids = tuple(sorted({_required(item, "input operator contract id") for item in self.input_operator_contract_ids}))
        if not operator_ids:
            raise MachineInterpretationError("Experimental hypothesis requires exact input operator contract IDs")
        object.__setattr__(self, "input_operator_contract_ids", operator_ids)
        object.__setattr__(self, "astrological_state_condition", _enum(self.astrological_state_condition, AstrologyState, "astrological_state_condition"))
        if self.astrological_state_condition in {AstrologyState.UNKNOWN_ASTRO_STATE, AstrologyState.MIXED_ASTRO_STATE}:
            raise MachineInterpretationError("Experimental hypothesis cannot bridge an unknown or unresolved mixed astrology state")
        side = _required(self.target_side, "hypothesis target_side").upper()
        if side not in {"USD", "JPY"}:
            raise MachineInterpretationError("Experimental hypothesis target_side must be USD or JPY")
        object.__setattr__(self, "target_side", side)
        object.__setattr__(self, "currency_pressure_state", _enum(self.currency_pressure_state, CurrencyPressureState, "currency_pressure_state"))
        if self.currency_pressure_state is CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED:
            raise MachineInterpretationError("Experimental hypothesis must state a testable non-unknown currency pressure condition")
        object.__setattr__(self, "reasoning", _required(self.reasoning, "hypothesis reasoning"))
        for field_name in ("source_dependencies", "experimental_assumptions", "prohibited_generalizations"):
            values = tuple(_required(item, field_name) for item in getattr(self, field_name))
            if not values:
                raise MachineInterpretationError(f"Experimental hypothesis requires {field_name}")
            object.__setattr__(self, field_name, values)
        object.__setattr__(self, "validation_status", _required(self.validation_status, "hypothesis validation_status"))
        if self.validation_status != "NOT_FINANCIALLY_VALIDATED":
            raise MachineInterpretationError("Experimental hypothesis must remain NOT_FINANCIALLY_VALIDATED")
        if type(self.outcome_data_seen_at_creation) is not bool or self.outcome_data_seen_at_creation:
            raise MachineInterpretationError("Experimental hypothesis must declare outcome_data_seen_at_creation=false")
        object.__setattr__(self, "approval_status", _enum(self.approval_status, HypothesisApprovalStatus, "hypothesis approval_status"))
        if self.signed_unit_if_configured is not None or self.magnitude_configured:
            raise MachineInterpretationError("This architecture cannot configure signed units or magnitude")
        object.__setattr__(self, "mode", _enum(self.mode, InterpretationMode, "hypothesis mode"))
        if self.mode is not InterpretationMode.EXPERIMENTAL_PROFILED:
            raise MachineInterpretationError("Experimental market hypotheses must remain EXPERIMENTAL_PROFILED")
        computed = self.computed_hash
        if self.hypothesis_hash is None:
            object.__setattr__(self, "hypothesis_hash", computed)
        elif self.hypothesis_hash != computed:
            raise MachineInterpretationError("Experimental hypothesis hash does not match decision-bearing content")

    @property
    def computed_hash(self) -> str:
        return _canonical_hash(
            {
                "hypothesisId": self.hypothesis_id,
                "version": self.version,
                "author": self.author,
                "createdAtUtc": self.created_at_utc,
                "inputOperatorContractIds": list(self.input_operator_contract_ids),
                "astrologicalStateCondition": self.astrological_state_condition.value,
                "targetSide": self.target_side,
                "currencyPressureState": self.currency_pressure_state.value,
                "reasoning": self.reasoning,
                "sourceDependencies": list(self.source_dependencies),
                "experimentalAssumptions": list(self.experimental_assumptions),
                "prohibitedGeneralizations": list(self.prohibited_generalizations),
                "validationStatus": self.validation_status,
                "outcomeDataSeenAtCreation": self.outcome_data_seen_at_creation,
                "approvalStatus": self.approval_status.value,
                "signedUnitIfConfigured": self.signed_unit_if_configured,
                "magnitudeConfigured": self.magnitude_configured,
                "mode": self.mode.value,
            }
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "hypothesisId": self.hypothesis_id,
            "version": self.version,
            "author": self.author,
            "createdAtUtc": self.created_at_utc,
            "inputOperatorContractIds": list(self.input_operator_contract_ids),
            "astrologicalStateCondition": self.astrological_state_condition.value,
            "targetSide": self.target_side,
            "currencyPressureState": self.currency_pressure_state.value,
            "reasoning": self.reasoning,
            "sourceDependencies": list(self.source_dependencies),
            "experimentalAssumptions": list(self.experimental_assumptions),
            "prohibitedGeneralizations": list(self.prohibited_generalizations),
            "validationStatus": self.validation_status,
            "outcomeDataSeenAtCreation": self.outcome_data_seen_at_creation,
            "approvalStatus": self.approval_status.value,
            "signedUnitIfConfigured": None,
            "magnitudeConfigured": False,
            "mode": self.mode.value,
            "hypothesisHash": self.hypothesis_hash,
        }


@dataclass(frozen=True)
class ExperimentalHypothesisRegistry:
    registry_id: str
    registry_status: str
    entries: tuple[ExperimentalMarketHypothesis, ...]
    registry_hash: str

    @classmethod
    def load(cls, path: Path | None = None) -> "ExperimentalHypothesisRegistry":
        source = Path(path or DEFAULT_HYPOTHESIS_REGISTRY_PATH)
        raw = _read_json(source, "experimental market hypothesis registry")
        if raw.get("contract") != HYPOTHESIS_REGISTRY_CONTRACT:
            raise MachineInterpretationError("Unsupported experimental market hypothesis registry contract")
        if raw.get("schemaVersion") != HYPOTHESIS_REGISTRY_SCHEMA_VERSION:
            raise MachineInterpretationError("Unsupported experimental market hypothesis registry schema")
        guardrails = raw.get("guardrails")
        if not isinstance(guardrails, dict) or any(
            guardrails.get(key) is not False
            for key in (
                "priceDataRead",
                "outcomeDataRead",
                "catalogueAdmission",
                "evidenceAdmission",
                "signedWaveRendered",
                "executionAllowed",
            )
        ):
            raise MachineInterpretationError("Experimental market hypothesis registry guardrails are not fail-closed")
        entries_raw = raw.get("entries")
        if not isinstance(entries_raw, list):
            raise MachineInterpretationError("Experimental market hypothesis registry entries must be a list")
        entries = tuple(_hypothesis_from_mapping(item) for item in entries_raw)
        if len({entry.hypothesis_id for entry in entries}) != len(entries):
            raise MachineInterpretationError("Experimental market hypothesis registry contains duplicate IDs")
        if raw.get("registryStatus") == "EMPTY_NO_AUTHORIZED_MARKET_BRIDGES" and entries:
            raise MachineInterpretationError("Empty experimental market hypothesis registry cannot contain entries")
        return cls(
            registry_id=_required(raw.get("registryId"), "hypothesis registryId"),
            registry_status=_required(raw.get("registryStatus"), "hypothesis registryStatus"),
            entries=entries,
            registry_hash=_canonical_hash(raw),
        )


def _hypothesis_from_mapping(raw: Any) -> ExperimentalMarketHypothesis:
    if not isinstance(raw, dict):
        raise MachineInterpretationError("Experimental hypothesis entry must be an object")
    return ExperimentalMarketHypothesis(
        hypothesis_id=raw.get("hypothesisId"),
        version=raw.get("version"),
        author=raw.get("author"),
        created_at_utc=raw.get("createdAtUtc"),
        input_operator_contract_ids=tuple(raw.get("inputOperatorContractIds") or ()),
        astrological_state_condition=raw.get("astrologicalStateCondition"),
        target_side=raw.get("targetSide"),
        currency_pressure_state=raw.get("currencyPressureState"),
        reasoning=raw.get("reasoning"),
        source_dependencies=tuple(raw.get("sourceDependencies") or ()),
        experimental_assumptions=tuple(raw.get("experimentalAssumptions") or ()),
        prohibited_generalizations=tuple(raw.get("prohibitedGeneralizations") or ()),
        validation_status=raw.get("validationStatus"),
        outcome_data_seen_at_creation=raw.get("outcomeDataSeenAtCreation"),
        approval_status=raw.get("approvalStatus"),
        signed_unit_if_configured=raw.get("signedUnitIfConfigured"),
        magnitude_configured=raw.get("magnitudeConfigured", False),
        mode=raw.get("mode"),
        hypothesis_hash=raw.get("hypothesisHash"),
    )


@dataclass(frozen=True)
class AstrologyInterpretation:
    state: AstrologyState
    source_coverage: str
    operator_contract_ids: tuple[str, ...]
    unresolved_operator_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class MarketBridge:
    status: MarketBridgeStatus
    hypothesis_id: str | None
    hypothesis_hash: str | None
    validation_status: str | None
    reason: str


@dataclass(frozen=True)
class CurrencySideInterpretation:
    state: CurrencyPressureState
    signed_unit: None
    magnitude_state: str
    reason: str


@dataclass(frozen=True)
class PlainLanguageExplanation:
    headline: str
    why: str
    classical_evidence: str
    experimental_status: str
    unknowns: tuple[str, ...]
    financial_validation: str


@dataclass(frozen=True)
class InterpretationProvenance:
    """Processing scope and source/bridge lineage for one interpretation packet."""

    input_scope: str
    source_operator_contract_ids: tuple[str, ...]
    source_evidence_statuses: tuple[SourceEvidenceStatus, ...]
    hypothesis_registry_contract: str
    market_hypothesis_id: str | None
    market_hypothesis_hash: str | None
    review_store_read: bool
    price_or_outcome_read: bool
    execution_allowed: bool

    def __post_init__(self) -> None:
        if self.input_scope != "SYNTHETIC_TEST_ONLY":
            raise MachineInterpretationError("Current interpreter provenance must remain SYNTHETIC_TEST_ONLY")
        operator_ids = tuple(_required(value, "provenance source operator contract id") for value in self.source_operator_contract_ids)
        statuses = tuple(_enum(value, SourceEvidenceStatus, "provenance source evidence status") for value in self.source_evidence_statuses)
        if len(operator_ids) != len(statuses):
            raise MachineInterpretationError("Provenance source operator IDs and statuses must align")
        if self.hypothesis_registry_contract != HYPOTHESIS_REGISTRY_CONTRACT:
            raise MachineInterpretationError("Unsupported hypothesis registry provenance")
        if any(value is not False for value in (self.review_store_read, self.price_or_outcome_read, self.execution_allowed)):
            raise MachineInterpretationError("Interpretation provenance must remain outcome-blind and non-executable")
        object.__setattr__(self, "source_operator_contract_ids", operator_ids)
        object.__setattr__(self, "source_evidence_statuses", statuses)


@dataclass(frozen=True)
class MachineAssistedInterpretation:
    event_identity: dict[str, str]
    source_operator_evidence: tuple[SourceOperatorEvidence, ...]
    astrological_interpretation: AstrologyInterpretation
    market_bridge: MarketBridge
    currency_side_interpretation: CurrencySideInterpretation
    mode: InterpretationMode
    explanation: PlainLanguageExplanation
    provenance: InterpretationProvenance
    prohibited_claims: tuple[str, ...] = field(default_factory=tuple)
    execution_allowed: bool = False

    def to_mapping(self) -> dict[str, Any]:
        return {
            "contract": INTERPRETATION_CONTRACT,
            "schemaVersion": INTERPRETATION_SCHEMA_VERSION,
            "eventIdentity": copy.deepcopy(self.event_identity),
            "sourceOperatorStates": [
                {
                    "operatorContractId": item.operator_contract_id,
                    "sourceStatus": item.source_status.value,
                    "astrologicalState": item.astrological_state.value,
                    "locators": [asdict(locator) for locator in item.locators],
                    "rationale": item.rationale,
                    "unresolvedDependencies": list(item.unresolved_dependencies),
                    "sourceMeasurements": [
                        {
                            "componentId": measurement.component_id,
                            "literalValue": measurement.literal_value,
                            "locator": asdict(measurement.locator),
                        }
                        for measurement in item.source_measurements
                    ],
                }
                for item in self.source_operator_evidence
            ],
            "astrologicalInterpretation": {
                "state": self.astrological_interpretation.state.value,
                "sourceCoverage": self.astrological_interpretation.source_coverage,
                "operatorContractIds": list(self.astrological_interpretation.operator_contract_ids),
                "unresolvedOperatorIds": list(self.astrological_interpretation.unresolved_operator_ids),
                "reason": self.astrological_interpretation.reason,
            },
            "marketBridge": {
                "status": self.market_bridge.status.value,
                "hypothesisId": self.market_bridge.hypothesis_id,
                "hypothesisHash": self.market_bridge.hypothesis_hash,
                "validationStatus": self.market_bridge.validation_status,
                "reason": self.market_bridge.reason,
            },
            "currencySideInterpretation": {
                "state": self.currency_side_interpretation.state.value,
                "signedUnit": None,
                "magnitudeState": self.currency_side_interpretation.magnitude_state,
                "reason": self.currency_side_interpretation.reason,
            },
            "mode": self.mode.value,
            "explanation": {
                "headline": self.explanation.headline,
                "why": self.explanation.why,
                "classicalEvidence": self.explanation.classical_evidence,
                "experimentalStatus": self.explanation.experimental_status,
                "unknowns": list(self.explanation.unknowns),
                "financialValidation": self.explanation.financial_validation,
            },
            "provenance": {
                "inputScope": self.provenance.input_scope,
                "sourceOperatorContractIds": list(self.provenance.source_operator_contract_ids),
                "sourceEvidenceStatuses": [status.value for status in self.provenance.source_evidence_statuses],
                "hypothesisRegistryContract": self.provenance.hypothesis_registry_contract,
                "marketHypothesisId": self.provenance.market_hypothesis_id,
                "marketHypothesisHash": self.provenance.market_hypothesis_hash,
                "reviewStoreRead": False,
                "priceOrOutcomeRead": False,
                "executionAllowed": False,
            },
            "prohibitedClaims": list(self.prohibited_claims),
            "executionAllowed": False,
        }


_PROHIBITED_CLAIMS = (
    "NO_PRICE_OR_OUTCOME_READ",
    "NO_SOURCE_CERTIFIED_FINANCIAL_FORECAST",
    "NO_SIGNED_WAVE_RUNTIME",
    "NO_PAIR_RESULTANT_RUNTIME",
    "NO_MAGNITUDE_CONFIGURATION",
    "NO_CATALOGUE_OR_EVIDENCE_ADMISSION",
    "NO_AUTO_SUGGEST_OR_ML_INTERPRETATION",
    "NO_MT5_OR_EXECUTION",
)


def _resolve_astrological_state(
    source_operator_evidence: Sequence[SourceOperatorEvidence],
) -> AstrologyInterpretation:
    if not source_operator_evidence:
        return AstrologyInterpretation(
            state=AstrologyState.UNKNOWN_ASTRO_STATE,
            source_coverage="OPERATOR_NOT_YET_AVAILABLE",
            operator_contract_ids=(),
            unresolved_operator_ids=("NO_SOURCE_OPERATOR_EVIDENCE",),
            reason="No event-bound source operator evidence was supplied.",
        )

    operator_ids = tuple(item.operator_contract_id for item in source_operator_evidence)
    unresolved = [
        dependency
        for item in source_operator_evidence
        if item.source_status is not SourceEvidenceStatus.SOURCE_CLOSED
        for dependency in (item.unresolved_dependencies or (item.operator_contract_id,))
    ]
    if unresolved:
        return AstrologyInterpretation(
            state=AstrologyState.UNKNOWN_ASTRO_STATE,
            source_coverage="PARTIAL_SOURCE_OPERATOR_COVERAGE",
            operator_contract_ids=operator_ids,
            unresolved_operator_ids=tuple(sorted(set(unresolved))),
            reason="A required source operator remains partial or unresolved.",
        )

    states = {item.astrological_state for item in source_operator_evidence}
    if AstrologyState.UNKNOWN_ASTRO_STATE in states:
        return AstrologyInterpretation(
            state=AstrologyState.UNKNOWN_ASTRO_STATE,
            source_coverage="SOURCE_CLOSED_OPERATOR_OUTPUT_UNKNOWN",
            operator_contract_ids=operator_ids,
            unresolved_operator_ids=("SOURCE_OPERATOR_OUTPUT_UNKNOWN",),
            reason="Available source operators do not close an astrology interpretation state.",
        )
    if len(states) != 1:
        return AstrologyInterpretation(
            state=AstrologyState.MIXED_ASTRO_STATE,
            source_coverage="SOURCE_CLOSED_CONFLICTING_OPERATORS",
            operator_contract_ids=operator_ids,
            unresolved_operator_ids=("NO_APPROVED_ASTROLOGICAL_PRECEDENCE_CONTRACT",),
            reason="Applicable source operators conflict and no approved precedence rule exists.",
        )
    return AstrologyInterpretation(
        state=next(iter(states)),
        source_coverage="SOURCE_CLOSED_OPERATOR_COVERAGE",
        operator_contract_ids=operator_ids,
        unresolved_operator_ids=(),
        reason="Source-bound operator evidence closes one astrology interpretation state.",
    )


def _no_market_bridge(reason: str) -> MarketBridge:
    return MarketBridge(
        status=MarketBridgeStatus.NO_AUTHORIZED_MARKET_BRIDGE,
        hypothesis_id=None,
        hypothesis_hash=None,
        validation_status=None,
        reason=reason,
    )


def _resolve_market_bridge(
    *,
    side: str,
    mode: InterpretationMode,
    astrology: AstrologyInterpretation,
    hypothesis: ExperimentalMarketHypothesis | None,
) -> MarketBridge:
    if astrology.state in {AstrologyState.UNKNOWN_ASTRO_STATE, AstrologyState.MIXED_ASTRO_STATE} or astrology.unresolved_operator_ids:
        return _no_market_bridge("No market bridge may resolve an unknown or unprecedenced astrology interpretation.")
    if mode is InterpretationMode.SOURCE_CERTIFIED:
        return _no_market_bridge("Source-certified mode cannot use an experimental market bridge.")
    if mode is InterpretationMode.EXPLORATORY_UNSIGNED:
        return _no_market_bridge("Exploratory unsigned mode exposes source features without currency direction.")
    if hypothesis is None:
        return _no_market_bridge("No approved USD/JPY market bridge exists for this source-defined astrology state.")
    if hypothesis.approval_status is not HypothesisApprovalStatus.AUTHORIZED_FOR_BLINDED_TEST:
        return _no_market_bridge("The supplied experimental hypothesis is not authorized for a blinded test.")
    if hypothesis.target_side != side:
        return _no_market_bridge("The supplied experimental hypothesis targets another currency side.")
    if hypothesis.astrological_state_condition is not astrology.state:
        return _no_market_bridge("The supplied experimental hypothesis does not match the astrology interpretation state.")
    if tuple(hypothesis.input_operator_contract_ids) != tuple(sorted(astrology.operator_contract_ids)):
        return _no_market_bridge("The supplied experimental hypothesis does not bind the exact applicable source operator set.")
    return MarketBridge(
        status=MarketBridgeStatus.EXPERIMENTAL_MARKET_HYPOTHESIS,
        hypothesis_id=hypothesis.hypothesis_id,
        hypothesis_hash=hypothesis.hypothesis_hash,
        validation_status=hypothesis.validation_status,
        reason="A versioned experimental bridge is explicitly authorized for blinded testing.",
    )


def _plain_explanation(
    astrology: AstrologyInterpretation,
    bridge: MarketBridge,
    currency: CurrencySideInterpretation,
    mode: InterpretationMode,
) -> PlainLanguageExplanation:
    if astrology.state is AstrologyState.MIXED_ASTRO_STATE:
        headline = "Currency direction: unknown"
        why = "Mixed interpretation because two applicable operators conflict and no approved precedence rule exists."
    elif astrology.state is AstrologyState.UNKNOWN_ASTRO_STATE:
        headline = "Currency direction: unknown"
        why = "Direction unknown because a required astrology operator is not yet available or remains unresolved."
    elif bridge.status is MarketBridgeStatus.NO_AUTHORIZED_MARKET_BRIDGE:
        headline = "Currency direction: unknown"
        why = "Direction unknown because the astrology is source-supported but no approved USD/JPY market bridge exists."
    else:
        headline = f"Currency pressure: {currency.state.value.lower()}"
        why = (
            f"Experimental {currency.state.value.lower()} interpretation. Classical evidence supports the astrology condition; "
            "the currency mapping is experimental and not yet financially validated."
        )
    return PlainLanguageExplanation(
        headline=headline,
        why=why,
        classical_evidence=astrology.source_coverage,
        experimental_status=(
            "EXPERIMENTAL_MARKET_HYPOTHESIS_NOT_FINANCIALLY_VALIDATED"
            if bridge.status is MarketBridgeStatus.EXPERIMENTAL_MARKET_HYPOTHESIS
            else "NO_AUTHORIZED_MARKET_BRIDGE"
        ),
        unknowns=astrology.unresolved_operator_ids,
        financial_validation="NOT_FINANCIALLY_VALIDATED",
    )


def interpret_synthetic_event(
    event_identity: Mapping[str, Any],
    *,
    source_operator_evidence: Sequence[SourceOperatorEvidence],
    mode: InterpretationMode,
    experimental_market_hypothesis: ExperimentalMarketHypothesis | None = None,
) -> MachineAssistedInterpretation:
    """Interpret one synthetic event without price, outcome, or runtime side effects."""

    if not isinstance(event_identity, Mapping) or event_identity.get("synthetic") is not True:
        raise MachineInterpretationError("Synthetic interpreter accepts only explicit synthetic identities")
    event_id = _required(event_identity.get("eventId"), "synthetic eventId")
    if not event_id.startswith("SYNTHETIC_"):
        raise MachineInterpretationError("Synthetic interpreter eventId must begin SYNTHETIC_")
    side = _required(event_identity.get("sideIdentity"), "synthetic sideIdentity").upper()
    if side not in {"USD", "JPY"}:
        raise MachineInterpretationError("Synthetic interpreter sideIdentity must be USD or JPY")
    selected_mode = _enum(mode, InterpretationMode, "interpretation mode")
    evidence = tuple(source_operator_evidence)
    if not all(isinstance(item, SourceOperatorEvidence) for item in evidence):
        raise MachineInterpretationError("source_operator_evidence must contain SourceOperatorEvidence values")
    astrology = _resolve_astrological_state(evidence)
    bridge = _resolve_market_bridge(
        side=side,
        mode=selected_mode,
        astrology=astrology,
        hypothesis=experimental_market_hypothesis,
    )
    if bridge.status is MarketBridgeStatus.EXPERIMENTAL_MARKET_HYPOTHESIS:
        assert experimental_market_hypothesis is not None
        currency = CurrencySideInterpretation(
            state=experimental_market_hypothesis.currency_pressure_state,
            signed_unit=None,
            magnitude_state="MAGNITUDE_NOT_CONFIGURED",
            reason="Experimental bridge supplies a categorical test state only; no signed unit or magnitude is configured.",
        )
    else:
        currency = CurrencySideInterpretation(
            state=CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED,
            signed_unit=None,
            magnitude_state="MAGNITUDE_NOT_CONFIGURED",
            reason=bridge.reason,
        )
    explanation = _plain_explanation(astrology, bridge, currency, selected_mode)
    return MachineAssistedInterpretation(
        event_identity={"eventId": event_id, "sideIdentity": side, "synthetic": "true"},
        source_operator_evidence=evidence,
        astrological_interpretation=astrology,
        market_bridge=bridge,
        currency_side_interpretation=currency,
        mode=selected_mode,
        explanation=explanation,
        provenance=InterpretationProvenance(
            input_scope="SYNTHETIC_TEST_ONLY",
            source_operator_contract_ids=tuple(item.operator_contract_id for item in evidence),
            source_evidence_statuses=tuple(item.source_status for item in evidence),
            hypothesis_registry_contract=HYPOTHESIS_REGISTRY_CONTRACT,
            market_hypothesis_id=bridge.hypothesis_id,
            market_hypothesis_hash=bridge.hypothesis_hash,
            review_store_read=False,
            price_or_outcome_read=False,
            execution_allowed=False,
        ),
        prohibited_claims=_PROHIBITED_CLAIMS,
        execution_allowed=False,
    )


def _identity_only_paths(resource_root: Path, side: str) -> dict[str, Path]:
    if side not in founder_review.SIDES:
        raise MachineInterpretationError(f"Unsupported side: {side}")
    packet_root = resource_root / "research_labs" / "chart_conditioned_aspects" / "founder_review"
    prefix = f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1"
    return {
        "packet": packet_root / f"{prefix}.json",
        "manifest": packet_root / f"{prefix}.identity_integrity.manifest.json",
        "audit": resource_root / "status" / "audits" / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json",
    }


def _all_mandatory_audit_checks_pass(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == set(founder_review.MANDATORY_IDENTITY_CHECKS)
        and all(type(value.get(key)) is bool and value[key] is True for key in founder_review.MANDATORY_IDENTITY_CHECKS)
    )


def _identity_only_side_coverage(resource_root: Path, side: str) -> dict[str, Any]:
    paths = _identity_only_paths(resource_root, side)
    packet = _read_json(paths["packet"], f"{side} immutable blank packet")
    manifest = _read_json(paths["manifest"], f"{side} immutable identity manifest")
    audit = _read_json(paths["audit"], "immutable identity audit")
    packet_hash = _sha256_file(paths["packet"])
    manifest_hash = _sha256_file(paths["manifest"])
    audit_hash = _sha256_file(paths["audit"])
    if audit_hash != founder_review.IDENTITY_AUDIT_EXPECTED_SHA256:
        raise MachineInterpretationError(f"{side} immutable identity audit hash does not match the accepted audit")
    if packet.get("instrumentIdentity") != f"FX_CURRENCY:{side}" or manifest.get("sideIdentity") != side:
        raise MachineInterpretationError(f"{side} immutable identity packet/manifest side binding is invalid")
    if manifest.get("contract") != "FOUNDER_BLANK_POLARITY_REVIEW_V1_IDENTITY_VERIFICATION_MANIFEST_V1":
        raise MachineInterpretationError(f"{side} immutable identity manifest contract is unsupported")
    if (
        manifest.get("identityAuditContract") != "CHART_CONDITIONED_TRANSIT_EVENT_IDENTITY_AUDIT_V1"
        or manifest.get("identityAuditVersion") != audit.get("auditVersion")
        or audit.get("contract") != "PFR_V2B_R5_F2A_R1_EVENT_IDENTITY_INTEGRITY_AUDIT_V1"
    ):
        raise MachineInterpretationError(f"{side} immutable identity manifest/audit contract binding is invalid")
    expected_packet_file = f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
    if manifest.get("packetFile") != expected_packet_file:
        raise MachineInterpretationError(f"{side} immutable identity manifest packet filename binding is invalid")
    if manifest.get("packetSha256") != packet_hash or manifest.get("originalGenerationManifestOutputSha256") != packet_hash:
        raise MachineInterpretationError(f"{side} immutable blank packet hash binding is invalid")
    if manifest.get("allRowsSinglePassVerified") is not True:
        raise MachineInterpretationError(f"{side} immutable identity manifest is not fully verified")
    reports = audit.get("sideReports")
    audit_side = reports.get(side) if isinstance(reports, dict) else None
    if not isinstance(audit_side, dict) or audit_side.get("sideIdentity") != side:
        raise MachineInterpretationError(f"{side} immutable identity audit side binding is invalid")
    records = audit_side.get("eventRecords") if isinstance(audit_side, dict) else None
    if not isinstance(records, list):
        raise MachineInterpretationError(f"{side} immutable identity audit records are unavailable")
    audit_records = {item.get("eventId"): item for item in records if isinstance(item, dict) and isinstance(item.get("eventId"), str)}
    verified_ids = manifest.get("verifiedEventIds")
    if not isinstance(verified_ids, list) or len(verified_ids) != 12 or len(set(verified_ids)) != len(verified_ids):
        raise MachineInterpretationError(f"{side} immutable identity manifest verified event IDs are invalid")
    rows = packet.get("rows")
    if not isinstance(rows, list) or len(rows) != 12:
        raise MachineInterpretationError(f"{side} immutable identity packet must contain exactly 12 rows")

    events: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    required_identity_fields = (
        "eventId",
        "eventHash",
        "sideIdentity",
        "instrumentIdentity",
        "chartId",
        "chartHypothesisId",
        "transitBody",
        "natalTarget",
        "aspectType",
        "applyingStartUtc",
        "exactUtc",
        "separatingEndUtc",
        "astronomyContract",
    )
    for row in rows:
        if not isinstance(row, dict):
            raise MachineInterpretationError(f"{side} immutable identity packet row is invalid")
        # Intentionally inspect eventIdentity only. Founder review fields are not read.
        event = row.get("eventIdentity")
        if not isinstance(event, dict):
            raise MachineInterpretationError(f"{side} immutable identity packet has no event identity")
        identity = {field: event.get(field) for field in required_identity_fields}
        if any(not isinstance(value, str) or not value for value in identity.values()):
            raise MachineInterpretationError(f"{side} immutable event identity is incomplete")
        event_id = identity["eventId"]
        event_hash = identity["eventHash"]
        if identity["sideIdentity"] != side or identity["instrumentIdentity"] != f"FX_CURRENCY:{side}":
            raise MachineInterpretationError(f"{side} immutable event identity has an invalid side/instrument binding")
        try:
            applying = datetime.fromisoformat(identity["applyingStartUtc"].replace("Z", "+00:00"))
            exact = datetime.fromisoformat(identity["exactUtc"].replace("Z", "+00:00"))
            separating = datetime.fromisoformat(identity["separatingEndUtc"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise MachineInterpretationError(f"{side} immutable event identity has an invalid UTC interval") from exc
        if not applying < exact < separating:
            raise MachineInterpretationError(f"{side} immutable event identity does not preserve half-open interval ordering")
        if event_id in seen_ids or event_hash in seen_hashes:
            raise MachineInterpretationError(f"{side} immutable identity packet has duplicate event identity")
        seen_ids.add(event_id)
        seen_hashes.add(event_hash)
        audit_record = audit_records.get(event_id)
        audit_identity_fields = (
            "eventId",
            "eventHash",
            "sideIdentity",
            "transitBody",
            "natalTarget",
            "aspectType",
            "applyingStartUtc",
            "exactUtc",
            "separatingEndUtc",
        )
        if (
            event_id not in verified_ids
            or not isinstance(audit_record, dict)
            or audit_record.get("status") != founder_review.REVIEWABLE_IDENTITY_STATUS
            or any(audit_record.get(field) != identity[field] for field in audit_identity_fields)
            or not _all_mandatory_audit_checks_pass(audit_record.get("checks"))
        ):
            raise MachineInterpretationError(f"{side} immutable event identity is not SINGLE_PASS_VERIFIED")
        events.append(
            {
                "eventIdentity": identity,
                "identityStatus": founder_review.REVIEWABLE_IDENTITY_STATUS,
                "sourceOperatorCoverage": "OPERATOR_NOT_YET_AVAILABLE",
                "sourceOperatorContractIds": [],
                "unresolvedOperatorCount": 1,
                "unresolvedOperatorIds": ["NO_EVENT_BOUND_SOURCE_OPERATOR_CONTRACT"],
                "marketBridgeStatus": MarketBridgeStatus.NO_AUTHORIZED_MARKET_BRIDGE.value,
                "currentDirectionStatus": CurrencyPressureState.UNKNOWN_MORE_EVIDENCE_REQUIRED.value,
                "magnitudeState": "MAGNITUDE_NOT_CONFIGURED",
                "mode": InterpretationMode.EXPLORATORY_UNSIGNED.value,
                "explanation": "Direction unknown because no event-bound source operator and no approved USD/JPY market bridge are available.",
            }
        )
    if set(verified_ids) != seen_ids:
        raise MachineInterpretationError(f"{side} immutable identity manifest and packet event sets disagree")
    return {
        "sideIdentity": side,
        "blankPacketSha256": packet_hash,
        "identityIntegrityManifestSha256": manifest_hash,
        "identityAuditSha256": audit_hash,
        "eventCount": len(events),
        "events": events,
    }


def build_real_identity_only_coverage_report(resource_root: Path) -> dict[str, Any]:
    """Read only canonical blank-packet identities; never read a review store."""

    root = Path(resource_root).resolve()
    sides = [_identity_only_side_coverage(root, side) for side in founder_review.SIDES]
    if sum(side["eventCount"] for side in sides) != 24:
        raise MachineInterpretationError("Identity-only coverage requires exactly 24 verified events")
    body = {
        "contract": IDENTITY_ONLY_COVERAGE_CONTRACT,
        "schemaVersion": IDENTITY_ONLY_COVERAGE_SCHEMA_VERSION,
        "inputPolicy": "IMMUTABLE_BLANK_PACKET_IDENTITY_AND_AUDIT_ONLY",
        "reviewStoreRead": False,
        "founderDecisionRead": False,
        "priceOrOutcomeRead": False,
        "sides": sides,
        "summary": {
            "eventCount": 24,
            "usdEventCount": sides[0]["eventCount"],
            "jpyEventCount": sides[1]["eventCount"],
            "singlePassVerifiedCount": 24,
            "sourceOperatorAvailableCount": 0,
            "marketBridgeAvailableCount": 0,
            "currentDirectionUnknownCount": 24,
        },
        "guardrails": {
            "reviewStoreRead": False,
            "founderDecisionRead": False,
            "priceDataRead": False,
            "outcomeDataRead": False,
            "sbcRead": False,
            "catalogueAdmission": False,
            "evidenceAdmission": False,
            "signedWaveCreated": False,
            "pairResultantCreated": False,
            "executionAllowed": False,
        },
    }
    return {**body, "identityOnlyCoverageHash": _canonical_hash(body)}


def render_identity_only_coverage_markdown(report: Mapping[str, Any]) -> str:
    """Render a compact, outcome-free audit view of the canonical identities."""

    if report.get("contract") != IDENTITY_ONLY_COVERAGE_CONTRACT:
        raise MachineInterpretationError("Cannot render an unsupported identity-only coverage report")
    lines = [
        "# MO-R4A-P0 Real 24 Event Identity-Only Coverage",
        "",
        "This record was derived from immutable blank packets and identity audits only.",
        "It did not read Founder Review decisions, price, outcomes, SBC, or a review store.",
        "",
        f"- Coverage hash: `{report.get('identityOnlyCoverageHash')}`",
        f"- Events: `{report.get('summary', {}).get('eventCount')}`",
        "- Current direction for every event: `UNKNOWN_MORE_EVIDENCE_REQUIRED`",
        "",
        "| Side | Event ID | Event hash | Source operator coverage | Unresolved operators | Market bridge | Current direction |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for side in report.get("sides", []):
        for item in side.get("events", []):
            event = item["eventIdentity"]
            lines.append(
                "| "
                + " | ".join(
                    (
                        str(side["sideIdentity"]),
                        str(event["eventId"]),
                        str(event["eventHash"]),
                        str(item["sourceOperatorCoverage"]),
                        str(item["unresolvedOperatorCount"]),
                        str(item["marketBridgeStatus"]),
                        str(item["currentDirectionStatus"]),
                    )
                )
                + " |"
            )
    return "\n".join(lines) + "\n"
