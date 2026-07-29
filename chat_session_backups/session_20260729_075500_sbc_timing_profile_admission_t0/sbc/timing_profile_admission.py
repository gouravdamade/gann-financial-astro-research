from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Callable

from .atomic_intervals import RESEARCH_CLASSIFICATION
from .models import to_primitive


TIMING_PROFILE_CONTRACT = "SBC_DIRECTIONAL_TIMING_PROFILE_V1"
TIMING_PROFILE_SCHEMA_VERSION = 1
TIMING_PROFILE_ADMISSION_CONTRACT = "SBC_TIMING_PROFILE_ADMISSION_REPORT_V1"
TIMING_PROFILE_ADMISSION_SCHEMA_VERSION = 1
TIMING_PROFILE_REGISTRY_CONTRACT = "SBC_TIMING_PROFILE_REGISTRY_V1"
TIMING_PROFILE_REGISTRY_SCHEMA_VERSION = 1
TIMING_PROFILE_ADMISSION_POLICY = "FAIL_CLOSED_SOURCE_REGISTRY_ADMISSION_V1"
CONFIDENCE_EQUATION = "NORMALIZED_WEIGHTED_GEOMETRIC_MEAN_V1"

PASS = "PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"

NO_PROFILE_LOADED = "NO_PROFILE_LOADED"
INVALID_PROFILE = "INVALID_PROFILE"
STRUCTURALLY_COMPLETE_UNREGISTERED = "STRUCTURALLY_COMPLETE_UNREGISTERED"
SOURCE_CERTIFIED_PROFILE_ADMITTED = "SOURCE_CERTIFIED_PROFILE_ADMITTED"

SAFE = "SAFE"
UNSAFE = "UNSAFE"
POSITIVE = "POSITIVE"
NEGATIVE = "NEGATIVE"
NONE = "NONE"

_PROFILE_KEYS = {
    "contract",
    "schemaVersion",
    "profileId",
    "profileVersion",
    "classification",
    "frozen",
    "sourceEvidence",
    "phaseSpan",
    "sectors",
    "boundaryPolicy",
    "asymmetryPolicy",
    "repeatedExactEventPolicy",
    "retrogradeLoopPolicy",
    "stationPolicy",
    "missingBoundaryPolicy",
    "unsupportedStatePolicy",
    "eligibilityPolicy",
    "confidencePolicy",
    "guardrails",
}
_SOURCE_KEYS = {"sourceId", "citation", "sha256", "role"}
_PHASE_SPAN_KEYS = {"unit", "start", "end", "wraps"}
_SECTOR_KEYS = {
    "sectorId",
    "start",
    "end",
    "startInclusive",
    "endInclusive",
    "directionEligibility",
    "directionRole",
}
_BOUNDARY_POLICY_KEYS = {
    "policyId",
    "margin",
    "unit",
    "insideMarginState",
    "exactBoundaryState",
}
_DETERMINISTIC_POLICY_KEYS = {
    "policyId",
    "deterministicRule",
    "fallbackState",
}
_STATION_POLICY_KEYS = {
    "policyId",
    "deterministicRule",
    "speedThresholdsByBody",
    "fallbackState",
}
_UNSUPPORTED_POLICY_KEYS = {
    "policyId",
    "deterministicRule",
    "enumeratedStates",
    "fallbackState",
}
_ELIGIBILITY_POLICY_KEYS = {
    "activityFloor",
    "coherenceFloor",
    "maximumUnsafeActivationShare",
    "minimumCoverage",
}
_CONFIDENCE_POLICY_KEYS = {
    "equation",
    "terms",
    "mandatoryGates",
    "minimumCoverage",
}
_CONFIDENCE_TERM_KEYS = {"termId", "weight", "sourceLineagePolicy"}
_GUARDRAIL_KEYS = {
    "researchOnly",
    "readOnly",
    "noAutoSuggest",
    "noLiveInference",
    "noOfficialMlNotes",
    "noShadowVote",
    "noTradeOutput",
    "executionAllowed",
}
_REGISTRY_KEYS = {"contract", "schemaVersion", "profiles", "executionAllowed"}
_REGISTRY_PROFILE_KEYS = {
    "profileHash",
    "profileId",
    "profileVersion",
    "frozen",
    "sourceCertified",
    "sourceAuditRefs",
    "prospectiveTrialId",
}


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _required_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _required_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty array")
    return value


def _exact_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    missing = sorted(allowed - set(value))
    unknown = sorted(set(value) - allowed)
    problems: list[str] = []
    if missing:
        problems.append(f"missing {', '.join(missing)}")
    if unknown:
        problems.append(f"unknown {', '.join(unknown)}")
    if problems:
        raise ValueError(f"{label}: {'; '.join(problems)}")


def _required_text(value: Any, label: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


def _required_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be boolean")
    return value


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be finite")
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite") from exc
    if not math.isfinite(normalized):
        raise ValueError(f"{label} must be finite")
    return 0.0 if normalized == 0.0 else normalized


def _ratio(value: Any, label: str) -> float:
    normalized = _finite(value, label)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{label} must be between 0 and 1")
    return normalized


def _sha256(value: Any, label: str) -> str:
    normalized = _required_text(value, label).upper()
    if len(normalized) != 64 or any(
        character not in "0123456789ABCDEF" for character in normalized
    ):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")
    return normalized


def _policy(
    profile: dict[str, Any],
    field_name: str,
    *,
    fallback_states: set[str] | None = None,
) -> None:
    payload = _required_dict(profile.get(field_name), field_name)
    _exact_keys(payload, _DETERMINISTIC_POLICY_KEYS, field_name)
    _required_text(payload.get("policyId"), f"{field_name}.policyId")
    _required_text(
        payload.get("deterministicRule"),
        f"{field_name}.deterministicRule",
    )
    fallback = _required_text(
        payload.get("fallbackState"),
        f"{field_name}.fallbackState",
    ).upper()
    allowed = fallback_states or {UNSAFE, UNKNOWN}
    if fallback not in allowed:
        raise ValueError(
            f"{field_name}.fallbackState must be one of {sorted(allowed)}"
        )


@dataclass(frozen=True)
class TimingProfileAdmissionGateResult:
    gate_id: str
    state: str
    mandatory: bool
    label: str
    detail: str
    missing_paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in {PASS, FAIL, UNKNOWN}:
            raise ValueError(f"unknown gate state: {self.state}")
        object.__setattr__(self, "gate_id", _required_text(self.gate_id, "gate_id"))
        object.__setattr__(self, "label", _required_text(self.label, "label"))
        object.__setattr__(self, "detail", _required_text(self.detail, "detail"))
        object.__setattr__(
            self,
            "missing_paths",
            tuple(_required_text(item, "missing_path") for item in self.missing_paths),
        )

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


@dataclass(frozen=True)
class TimingProfileAdmissionReport:
    profile_status: str
    profile_id: str | None
    profile_version: str | None
    candidate_profile_hash: str | None
    structural_complete: bool
    source_registry_admitted: bool
    isolated_research_profile_admitted: bool
    directional_engine_implemented: bool
    directional_output_available: bool
    prospective_financial_validation_passed: bool
    financial_use_allowed: bool
    validation_gates: tuple[TimingProfileAdmissionGateResult, ...]
    missing_requirements: tuple[str, ...]
    contract: str = TIMING_PROFILE_ADMISSION_CONTRACT
    schema_version: int = TIMING_PROFILE_ADMISSION_SCHEMA_VERSION
    admission_policy: str = TIMING_PROFILE_ADMISSION_POLICY
    classification: str = RESEARCH_CLASSIFICATION
    guardrails: dict[str, Any] = field(
        default_factory=lambda: {
            "research_only": True,
            "read_only": True,
            "candidate_persisted": False,
            "profile_values_supplied_by_application": False,
            "timing_phase_calculated": False,
            "directional_phase_calculated": False,
            "confidence_calculated": False,
            "counts_as_independent_vote": False,
            "directional_contribution": 0.0,
            "auto_suggest_included": False,
            "live_inference_included": False,
            "official_ml_notes_included": False,
            "shadow_vote_included": False,
            "trade_output_included": False,
            "financially_validated": False,
            "execution_allowed": False,
            "blocked_capabilities": [
                "DIRECTIONAL_TIMING_PHASE",
                "TIMING_CONFIDENCE",
                "AUTO_SUGGEST",
                "LIVE_INFERENCE",
                "OFFICIAL_ML_NOTES",
                "SHADOW_VOTE",
                "TRADE_OUTPUT",
                "MT5_EXECUTION",
            ],
        }
    )

    def __post_init__(self) -> None:
        if self.directional_engine_implemented:
            raise ValueError("T0 cannot claim a directional timing engine")
        if self.directional_output_available:
            raise ValueError("T0 cannot expose directional output")
        if self.financial_use_allowed:
            raise ValueError("T0 cannot allow financial use")
        if self.guardrails.get("execution_allowed") is not False:
            raise ValueError("T0 execution must remain locked")
        if float(self.guardrails.get("directional_contribution", 1.0)) != 0.0:
            raise ValueError("T0 cannot contribute market direction")

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


class SbcTimingProfileAdmissionGate:
    def __init__(
        self,
        registry: dict[str, Any],
        research_trials: dict[str, Any] | None = None,
    ) -> None:
        self._registry = registry
        self._research_trials = research_trials or {
            "executionAllowed": False,
            "trials": [],
        }

    @staticmethod
    def _gate(
        gate_id: str,
        label: str,
        validator: Callable[[], str],
        *,
        mandatory: bool = True,
        unknown_paths: tuple[str, ...] = (),
        profile_present: bool = True,
    ) -> TimingProfileAdmissionGateResult:
        if not profile_present:
            return TimingProfileAdmissionGateResult(
                gate_id=gate_id,
                state=UNKNOWN,
                mandatory=mandatory,
                label=label,
                detail="No candidate profile is loaded; this requirement is unknown.",
                missing_paths=unknown_paths,
            )
        try:
            detail = validator()
        except (TypeError, ValueError) as exc:
            return TimingProfileAdmissionGateResult(
                gate_id=gate_id,
                state=FAIL,
                mandatory=mandatory,
                label=label,
                detail=str(exc),
                missing_paths=unknown_paths,
            )
        return TimingProfileAdmissionGateResult(
            gate_id=gate_id,
            state=PASS,
            mandatory=mandatory,
            label=label,
            detail=detail,
        )

    @staticmethod
    def _validate_profile_core(profile: dict[str, Any]) -> str:
        _exact_keys(profile, _PROFILE_KEYS, "profile")
        if profile.get("contract") != TIMING_PROFILE_CONTRACT:
            raise ValueError(f"profile.contract must be {TIMING_PROFILE_CONTRACT}")
        if profile.get("schemaVersion") != TIMING_PROFILE_SCHEMA_VERSION:
            raise ValueError(
                f"profile.schemaVersion must be {TIMING_PROFILE_SCHEMA_VERSION}"
            )
        _required_text(profile.get("profileId"), "profile.profileId")
        _required_text(profile.get("profileVersion"), "profile.profileVersion")
        if profile.get("classification") != RESEARCH_CLASSIFICATION:
            raise ValueError(
                f"profile.classification must be {RESEARCH_CLASSIFICATION}"
            )
        if not _required_bool(profile.get("frozen"), "profile.frozen"):
            raise ValueError("profile.frozen must be true")
        return "Contract, schema, identity, classification, and frozen flag are explicit."

    @staticmethod
    def _validate_source_evidence(profile: dict[str, Any]) -> str:
        sources = _required_list(profile.get("sourceEvidence"), "sourceEvidence")
        source_ids: set[str] = set()
        for index, item in enumerate(sources):
            label = f"sourceEvidence[{index}]"
            payload = _required_dict(item, label)
            _exact_keys(payload, _SOURCE_KEYS, label)
            source_id = _required_text(payload.get("sourceId"), f"{label}.sourceId")
            if source_id in source_ids:
                raise ValueError(f"duplicate sourceEvidence sourceId: {source_id}")
            source_ids.add(source_id)
            _required_text(payload.get("citation"), f"{label}.citation")
            _sha256(payload.get("sha256"), f"{label}.sha256")
            _required_text(payload.get("role"), f"{label}.role")
        return f"{len(sources)} hash-pinned source reference(s) are declared."

    @staticmethod
    def _validate_phase_span(profile: dict[str, Any]) -> str:
        span = _required_dict(profile.get("phaseSpan"), "phaseSpan")
        _exact_keys(span, _PHASE_SPAN_KEYS, "phaseSpan")
        unit = _required_text(span.get("unit"), "phaseSpan.unit")
        start = _finite(span.get("start"), "phaseSpan.start")
        end = _finite(span.get("end"), "phaseSpan.end")
        if end <= start:
            raise ValueError("phaseSpan.end must be greater than phaseSpan.start")
        _required_bool(span.get("wraps"), "phaseSpan.wraps")
        return f"Phase span is explicit in {unit}: {start:g} to {end:g}."

    @staticmethod
    def _validated_sectors(profile: dict[str, Any]) -> list[dict[str, Any]]:
        span = _required_dict(profile.get("phaseSpan"), "phaseSpan")
        span_start = _finite(span.get("start"), "phaseSpan.start")
        span_end = _finite(span.get("end"), "phaseSpan.end")
        sectors = _required_list(profile.get("sectors"), "sectors")
        if len(sectors) < 2:
            raise ValueError("sectors must define at least two sectors")
        normalized: list[dict[str, Any]] = []
        sector_ids: set[str] = set()
        for index, item in enumerate(sectors):
            label = f"sectors[{index}]"
            sector = _required_dict(item, label)
            _exact_keys(sector, _SECTOR_KEYS, label)
            sector_id = _required_text(sector.get("sectorId"), f"{label}.sectorId")
            if sector_id in sector_ids:
                raise ValueError(f"duplicate sectorId: {sector_id}")
            sector_ids.add(sector_id)
            start = _finite(sector.get("start"), f"{label}.start")
            end = _finite(sector.get("end"), f"{label}.end")
            if end <= start:
                raise ValueError(f"{label}.end must be greater than start")
            if _required_bool(
                sector.get("startInclusive"),
                f"{label}.startInclusive",
            ) is not True:
                raise ValueError(f"{label}.startInclusive must be true")
            if _required_bool(
                sector.get("endInclusive"),
                f"{label}.endInclusive",
            ) is not False:
                raise ValueError(f"{label}.endInclusive must be false")
            eligibility = _required_text(
                sector.get("directionEligibility"),
                f"{label}.directionEligibility",
            ).upper()
            role = _required_text(
                sector.get("directionRole"),
                f"{label}.directionRole",
            ).upper()
            if eligibility not in {SAFE, UNSAFE}:
                raise ValueError(
                    f"{label}.directionEligibility must be SAFE or UNSAFE"
                )
            if role not in {POSITIVE, NEGATIVE, NONE}:
                raise ValueError(
                    f"{label}.directionRole must be POSITIVE, NEGATIVE, or NONE"
                )
            if eligibility == SAFE and role not in {POSITIVE, NEGATIVE}:
                raise ValueError(f"{label}: SAFE sectors require a direction role")
            if eligibility == UNSAFE and role != NONE:
                raise ValueError(f"{label}: UNSAFE sectors require directionRole NONE")
            normalized.append(
                {
                    "sectorId": sector_id,
                    "start": start,
                    "end": end,
                    "directionEligibility": eligibility,
                    "directionRole": role,
                }
            )
        normalized.sort(key=lambda item: (item["start"], item["end"]))
        if not math.isclose(
            normalized[0]["start"],
            span_start,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("sectors must begin exactly at phaseSpan.start")
        if not math.isclose(
            normalized[-1]["end"],
            span_end,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("sectors must end exactly at phaseSpan.end")
        for left, right in zip(normalized, normalized[1:]):
            if not math.isclose(
                left["end"],
                right["start"],
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "sectors must form an exact non-overlapping, gap-free partition"
                )
        return normalized

    @classmethod
    def _validate_sectors(cls, profile: dict[str, Any]) -> str:
        sectors = cls._validated_sectors(profile)
        safe_count = sum(
            item["directionEligibility"] == SAFE for item in sectors
        )
        unsafe_count = len(sectors) - safe_count
        return (
            f"{len(sectors)} half-open sectors exactly partition the span; "
            f"{safe_count} SAFE and {unsafe_count} UNSAFE."
        )

    @classmethod
    def _validate_boundary_policy(cls, profile: dict[str, Any]) -> str:
        payload = _required_dict(profile.get("boundaryPolicy"), "boundaryPolicy")
        _exact_keys(payload, _BOUNDARY_POLICY_KEYS, "boundaryPolicy")
        _required_text(payload.get("policyId"), "boundaryPolicy.policyId")
        margin = _finite(payload.get("margin"), "boundaryPolicy.margin")
        if margin < 0.0:
            raise ValueError("boundaryPolicy.margin cannot be negative")
        unit = _required_text(payload.get("unit"), "boundaryPolicy.unit")
        span = _required_dict(profile.get("phaseSpan"), "phaseSpan")
        if unit != _required_text(span.get("unit"), "phaseSpan.unit"):
            raise ValueError("boundaryPolicy.unit must match phaseSpan.unit")
        inside_state = _required_text(
            payload.get("insideMarginState"),
            "boundaryPolicy.insideMarginState",
        ).upper()
        exact_state = _required_text(
            payload.get("exactBoundaryState"),
            "boundaryPolicy.exactBoundaryState",
        ).upper()
        if inside_state not in {UNSAFE, UNKNOWN}:
            raise ValueError(
                "boundaryPolicy.insideMarginState must be UNSAFE or UNKNOWN"
            )
        if exact_state not in {UNSAFE, UNKNOWN}:
            raise ValueError(
                "boundaryPolicy.exactBoundaryState must be UNSAFE or UNKNOWN"
            )
        widths = [
            item["end"] - item["start"] for item in cls._validated_sectors(profile)
        ]
        if margin * 2.0 >= min(widths):
            raise ValueError(
                "boundaryPolicy.margin must leave a non-empty sector interior"
            )
        return (
            f"Boundary margin is {margin:g} {unit}; exact and margin states "
            "fail closed."
        )

    @staticmethod
    def _validate_station_policy(profile: dict[str, Any]) -> str:
        payload = _required_dict(profile.get("stationPolicy"), "stationPolicy")
        _exact_keys(payload, _STATION_POLICY_KEYS, "stationPolicy")
        _required_text(payload.get("policyId"), "stationPolicy.policyId")
        _required_text(
            payload.get("deterministicRule"),
            "stationPolicy.deterministicRule",
        )
        fallback = _required_text(
            payload.get("fallbackState"),
            "stationPolicy.fallbackState",
        ).upper()
        if fallback not in {UNSAFE, UNKNOWN}:
            raise ValueError(
                "stationPolicy.fallbackState must be UNSAFE or UNKNOWN"
            )
        thresholds = _required_dict(
            payload.get("speedThresholdsByBody"),
            "stationPolicy.speedThresholdsByBody",
        )
        if not thresholds:
            raise ValueError(
                "stationPolicy.speedThresholdsByBody cannot be empty"
            )
        for body, value in thresholds.items():
            _required_text(body, "stationPolicy body")
            if _finite(value, f"stationPolicy.speedThresholdsByBody.{body}") < 0.0:
                raise ValueError("station speed thresholds cannot be negative")
        return f"Station handling declares {len(thresholds)} body threshold(s)."

    @staticmethod
    def _validate_unsupported_state_policy(profile: dict[str, Any]) -> str:
        payload = _required_dict(
            profile.get("unsupportedStatePolicy"),
            "unsupportedStatePolicy",
        )
        _exact_keys(
            payload,
            _UNSUPPORTED_POLICY_KEYS,
            "unsupportedStatePolicy",
        )
        _required_text(
            payload.get("policyId"),
            "unsupportedStatePolicy.policyId",
        )
        _required_text(
            payload.get("deterministicRule"),
            "unsupportedStatePolicy.deterministicRule",
        )
        states = _required_list(
            payload.get("enumeratedStates"),
            "unsupportedStatePolicy.enumeratedStates",
        )
        normalized = [
            _required_text(item, "unsupportedStatePolicy state") for item in states
        ]
        if len(set(normalized)) != len(normalized):
            raise ValueError("unsupportedStatePolicy states must be unique")
        fallback = _required_text(
            payload.get("fallbackState"),
            "unsupportedStatePolicy.fallbackState",
        ).upper()
        if fallback not in {UNSAFE, UNKNOWN}:
            raise ValueError(
                "unsupportedStatePolicy.fallbackState must be UNSAFE or UNKNOWN"
            )
        return f"{len(normalized)} unsupported state(s) have an explicit fallback."

    @staticmethod
    def _validate_eligibility_policy(profile: dict[str, Any]) -> str:
        payload = _required_dict(
            profile.get("eligibilityPolicy"),
            "eligibilityPolicy",
        )
        _exact_keys(payload, _ELIGIBILITY_POLICY_KEYS, "eligibilityPolicy")
        if _finite(payload.get("activityFloor"), "eligibilityPolicy.activityFloor") < 0:
            raise ValueError("eligibilityPolicy.activityFloor cannot be negative")
        _ratio(
            payload.get("coherenceFloor"),
            "eligibilityPolicy.coherenceFloor",
        )
        _ratio(
            payload.get("maximumUnsafeActivationShare"),
            "eligibilityPolicy.maximumUnsafeActivationShare",
        )
        _ratio(
            payload.get("minimumCoverage"),
            "eligibilityPolicy.minimumCoverage",
        )
        return (
            "Activity, coherence, unsafe-share, and minimum-coverage thresholds "
            "are explicit."
        )

    @staticmethod
    def _validate_confidence_policy(profile: dict[str, Any]) -> str:
        payload = _required_dict(
            profile.get("confidencePolicy"),
            "confidencePolicy",
        )
        _exact_keys(payload, _CONFIDENCE_POLICY_KEYS, "confidencePolicy")
        if payload.get("equation") != CONFIDENCE_EQUATION:
            raise ValueError(
                f"confidencePolicy.equation must be {CONFIDENCE_EQUATION}"
            )
        terms = _required_list(payload.get("terms"), "confidencePolicy.terms")
        term_ids: set[str] = set()
        for index, item in enumerate(terms):
            label = f"confidencePolicy.terms[{index}]"
            term = _required_dict(item, label)
            _exact_keys(term, _CONFIDENCE_TERM_KEYS, label)
            term_id = _required_text(term.get("termId"), f"{label}.termId")
            if term_id in term_ids:
                raise ValueError(f"duplicate confidence termId: {term_id}")
            term_ids.add(term_id)
            if _finite(term.get("weight"), f"{label}.weight") <= 0.0:
                raise ValueError(f"{label}.weight must be positive")
            _required_text(
                term.get("sourceLineagePolicy"),
                f"{label}.sourceLineagePolicy",
            )
        gates = _required_list(
            payload.get("mandatoryGates"),
            "confidencePolicy.mandatoryGates",
        )
        gate_ids = [_required_text(item, "mandatory gate") for item in gates]
        if len(set(gate_ids)) != len(gate_ids):
            raise ValueError("confidencePolicy.mandatoryGates must be unique")
        _ratio(
            payload.get("minimumCoverage"),
            "confidencePolicy.minimumCoverage",
        )
        return (
            f"One frozen confidence equation declares {len(terms)} term(s) and "
            f"{len(gate_ids)} mandatory gate(s)."
        )

    @staticmethod
    def _validate_guardrails(profile: dict[str, Any]) -> str:
        payload = _required_dict(profile.get("guardrails"), "guardrails")
        _exact_keys(payload, _GUARDRAIL_KEYS, "guardrails")
        required_true = _GUARDRAIL_KEYS - {"executionAllowed"}
        for key in sorted(required_true):
            if _required_bool(payload.get(key), f"guardrails.{key}") is not True:
                raise ValueError(f"guardrails.{key} must be true")
        if _required_bool(
            payload.get("executionAllowed"),
            "guardrails.executionAllowed",
        ):
            raise ValueError("guardrails.executionAllowed must be false")
        return "Inference, ML-note, shadow-vote, trade, and execution locks are explicit."

    @staticmethod
    def _validate_registry(registry: dict[str, Any]) -> str:
        payload = _required_dict(registry, "registry")
        _exact_keys(payload, _REGISTRY_KEYS, "registry")
        if payload.get("contract") != TIMING_PROFILE_REGISTRY_CONTRACT:
            raise ValueError(
                f"registry.contract must be {TIMING_PROFILE_REGISTRY_CONTRACT}"
            )
        if payload.get("schemaVersion") != TIMING_PROFILE_REGISTRY_SCHEMA_VERSION:
            raise ValueError(
                "registry.schemaVersion must be "
                f"{TIMING_PROFILE_REGISTRY_SCHEMA_VERSION}"
            )
        if _required_bool(
            payload.get("executionAllowed"),
            "registry.executionAllowed",
        ):
            raise ValueError("registry.executionAllowed must be false")
        profiles = payload.get("profiles")
        if not isinstance(profiles, list):
            raise ValueError("registry.profiles must be an array")
        hashes: set[str] = set()
        for index, item in enumerate(profiles):
            label = f"registry.profiles[{index}]"
            entry = _required_dict(item, label)
            _exact_keys(entry, _REGISTRY_PROFILE_KEYS, label)
            profile_hash = _sha256(entry.get("profileHash"), f"{label}.profileHash")
            if profile_hash in hashes:
                raise ValueError(f"duplicate registered profile hash: {profile_hash}")
            hashes.add(profile_hash)
            _required_text(entry.get("profileId"), f"{label}.profileId")
            _required_text(entry.get("profileVersion"), f"{label}.profileVersion")
            _required_bool(entry.get("frozen"), f"{label}.frozen")
            _required_bool(
                entry.get("sourceCertified"),
                f"{label}.sourceCertified",
            )
            refs = entry.get("sourceAuditRefs")
            if not isinstance(refs, list):
                raise ValueError(f"{label}.sourceAuditRefs must be an array")
            for ref in refs:
                _required_text(ref, f"{label}.sourceAuditRef")
            trial_id = entry.get("prospectiveTrialId")
            if trial_id is not None:
                _required_text(trial_id, f"{label}.prospectiveTrialId")
        return f"Server-owned registry is valid with {len(profiles)} profile(s)."

    def _registered_profile(
        self,
        candidate_hash: str | None,
    ) -> dict[str, Any] | None:
        if candidate_hash is None:
            return None
        profiles = self._registry.get("profiles")
        if not isinstance(profiles, list):
            return None
        return next(
            (
                item
                for item in profiles
                if isinstance(item, dict)
                and str(item.get("profileHash") or "").upper() == candidate_hash
            ),
            None,
        )

    @staticmethod
    def _validate_registered_profile(
        profile: dict[str, Any],
        candidate_hash: str,
        entry: dict[str, Any] | None,
    ) -> str:
        if entry is None:
            raise LookupError(
                "Candidate hash is not present in the server-owned timing profile registry."
            )
        if entry.get("profileId") != profile.get("profileId"):
            raise ValueError("Registered profileId does not match the candidate")
        if entry.get("profileVersion") != profile.get("profileVersion"):
            raise ValueError("Registered profileVersion does not match the candidate")
        if str(entry.get("profileHash") or "").upper() != candidate_hash:
            raise ValueError("Registered profile hash does not match the candidate")
        if entry.get("frozen") is not True:
            raise ValueError("Registered profile is not frozen")
        if entry.get("sourceCertified") is not True:
            raise ValueError("Registered profile is not source-certified")
        refs = entry.get("sourceAuditRefs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("Registered profile lacks source-certification audit refs")
        return (
            "Candidate hash matches a frozen, source-certified server registry entry."
        )

    def _prospective_gate(
        self,
        entry: dict[str, Any] | None,
    ) -> TimingProfileAdmissionGateResult:
        trial_id = entry.get("prospectiveTrialId") if entry else None
        if not trial_id:
            return TimingProfileAdmissionGateResult(
                gate_id="prospective_financial_validation",
                state=UNKNOWN,
                mandatory=False,
                label="Prospective financial validation",
                detail=(
                    "No timing-profile prospective trial is registered. "
                    "Financial interpretation remains unavailable."
                ),
                missing_paths=("registry.profiles[].prospectiveTrialId",),
            )
        trials = self._research_trials.get("trials")
        if not isinstance(trials, list):
            return TimingProfileAdmissionGateResult(
                gate_id="prospective_financial_validation",
                state=FAIL,
                mandatory=False,
                label="Prospective financial validation",
                detail="Research trial registry is malformed.",
            )
        trial = next(
            (
                item
                for item in trials
                if isinstance(item, dict) and item.get("trialId") == trial_id
            ),
            None,
        )
        if trial is None:
            return TimingProfileAdmissionGateResult(
                gate_id="prospective_financial_validation",
                state=FAIL,
                mandatory=False,
                label="Prospective financial validation",
                detail="Registered timing-profile trial ID is absent from the trial registry.",
            )
        if (
            trial.get("financiallyValidated") is True
            and trial.get("executionAllowed") is False
        ):
            return TimingProfileAdmissionGateResult(
                gate_id="prospective_financial_validation",
                state=PASS,
                mandatory=False,
                label="Prospective financial validation",
                detail="The registered immutable trial reports financial validation.",
            )
        return TimingProfileAdmissionGateResult(
            gate_id="prospective_financial_validation",
            state=UNKNOWN,
            mandatory=False,
            label="Prospective financial validation",
            detail="The registered trial has not passed its financial validation gate.",
        )

    def evaluate(self, profile_payload: Any | None) -> TimingProfileAdmissionReport:
        profile_present = profile_payload is not None
        profile = profile_payload if isinstance(profile_payload, dict) else {}
        candidate_hash: str | None = None
        if profile_present and isinstance(profile_payload, dict):
            try:
                candidate_hash = _canonical_hash(profile_payload)
            except (TypeError, ValueError):
                candidate_hash = None

        gate_specs: tuple[
            tuple[str, str, Callable[[], str], tuple[str, ...]],
            ...,
        ] = (
            (
                "profile_core",
                "Frozen profile contract",
                lambda: self._validate_profile_core(profile),
                ("profile.contract", "profile.profileId", "profile.frozen"),
            ),
            (
                "source_evidence",
                "Hash-pinned source evidence",
                lambda: self._validate_source_evidence(profile),
                ("profile.sourceEvidence",),
            ),
            (
                "phase_span",
                "Complete phase span",
                lambda: self._validate_phase_span(profile),
                ("profile.phaseSpan",),
            ),
            (
                "sector_partition",
                "Gap-free safe and unsafe sectors",
                lambda: self._validate_sectors(profile),
                ("profile.sectors",),
            ),
            (
                "boundary_policy",
                "Boundary inclusivity and margin",
                lambda: self._validate_boundary_policy(profile),
                ("profile.boundaryPolicy",),
            ),
            (
                "asymmetry_policy",
                "Asymmetry handling",
                lambda: (
                    _policy(profile, "asymmetryPolicy")
                    or "Asymmetry policy and fail-closed fallback are explicit."
                ),
                ("profile.asymmetryPolicy",),
            ),
            (
                "repeated_exact_event_policy",
                "Repeated exact-event handling",
                lambda: (
                    _policy(profile, "repeatedExactEventPolicy")
                    or "Repeated exact-event handling is deterministic."
                ),
                ("profile.repeatedExactEventPolicy",),
            ),
            (
                "retrograde_loop_policy",
                "Retrograde-loop handling",
                lambda: (
                    _policy(profile, "retrogradeLoopPolicy")
                    or "Retrograde-loop handling is deterministic."
                ),
                ("profile.retrogradeLoopPolicy",),
            ),
            (
                "station_policy",
                "Station handling",
                lambda: self._validate_station_policy(profile),
                ("profile.stationPolicy",),
            ),
            (
                "missing_boundary_policy",
                "Missing-boundary handling",
                lambda: (
                    _policy(profile, "missingBoundaryPolicy", fallback_states={UNKNOWN})
                    or "Missing boundaries resolve to UNKNOWN."
                ),
                ("profile.missingBoundaryPolicy",),
            ),
            (
                "unsupported_state_policy",
                "Unsupported-state handling",
                lambda: self._validate_unsupported_state_policy(profile),
                ("profile.unsupportedStatePolicy",),
            ),
            (
                "eligibility_policy",
                "Directional eligibility thresholds",
                lambda: self._validate_eligibility_policy(profile),
                ("profile.eligibilityPolicy",),
            ),
            (
                "confidence_policy",
                "Single confidence equation",
                lambda: self._validate_confidence_policy(profile),
                ("profile.confidencePolicy",),
            ),
            (
                "profile_guardrails",
                "Research and execution locks",
                lambda: self._validate_guardrails(profile),
                ("profile.guardrails",),
            ),
        )
        gates = [
            self._gate(
                gate_id,
                label,
                validator,
                unknown_paths=missing_paths,
                profile_present=profile_present,
            )
            for gate_id, label, validator, missing_paths in gate_specs
        ]
        registry_gate = self._gate(
            "server_registry_integrity",
            "Server-owned profile registry",
            lambda: self._validate_registry(self._registry),
            profile_present=True,
        )
        gates.append(registry_gate)

        registry_entry = self._registered_profile(candidate_hash)
        if not profile_present:
            registration_gate = TimingProfileAdmissionGateResult(
                gate_id="frozen_source_certified_registration",
                state=UNKNOWN,
                mandatory=True,
                label="Frozen source-certified registration",
                detail="No candidate hash is available for registry lookup.",
                missing_paths=("candidate_profile_hash",),
            )
        elif candidate_hash is None:
            registration_gate = TimingProfileAdmissionGateResult(
                gate_id="frozen_source_certified_registration",
                state=FAIL,
                mandatory=True,
                label="Frozen source-certified registration",
                detail="Candidate profile cannot be canonically hashed.",
            )
        else:
            try:
                registration_detail = self._validate_registered_profile(
                    profile,
                    candidate_hash,
                    registry_entry,
                )
            except LookupError as exc:
                registration_gate = TimingProfileAdmissionGateResult(
                    gate_id="frozen_source_certified_registration",
                    state=UNKNOWN,
                    mandatory=True,
                    label="Frozen source-certified registration",
                    detail=str(exc),
                    missing_paths=("status/timing_phase_profile_registry.json",),
                )
            except (TypeError, ValueError) as exc:
                registration_gate = TimingProfileAdmissionGateResult(
                    gate_id="frozen_source_certified_registration",
                    state=FAIL,
                    mandatory=True,
                    label="Frozen source-certified registration",
                    detail=str(exc),
                )
            else:
                registration_gate = TimingProfileAdmissionGateResult(
                    gate_id="frozen_source_certified_registration",
                    state=PASS,
                    mandatory=True,
                    label="Frozen source-certified registration",
                    detail=registration_detail,
                )
        gates.append(registration_gate)
        prospective_gate = self._prospective_gate(registry_entry)
        gates.append(prospective_gate)
        gates.append(
            TimingProfileAdmissionGateResult(
                gate_id="directional_engine_presence",
                state=UNKNOWN,
                mandatory=False,
                label="Directional engine presence",
                detail=(
                    "No directional timing-phase engine is implemented. "
                    "T0 validates profile admission only."
                ),
                missing_paths=("directional_timing_phase_engine",),
            )
        )

        structural_gate_ids = {item[0] for item in gate_specs}
        structural_complete = all(
            gate.state == PASS
            for gate in gates
            if gate.gate_id in structural_gate_ids
        )
        source_registry_admitted = (
            registry_gate.state == PASS and registration_gate.state == PASS
        )
        isolated_research_profile_admitted = (
            structural_complete and source_registry_admitted
        )
        prospective_passed = prospective_gate.state == PASS

        if not profile_present:
            profile_status = NO_PROFILE_LOADED
        elif not structural_complete:
            profile_status = INVALID_PROFILE
        elif not source_registry_admitted:
            profile_status = STRUCTURALLY_COMPLETE_UNREGISTERED
        else:
            profile_status = SOURCE_CERTIFIED_PROFILE_ADMITTED

        missing_requirements = tuple(
            gate.label
            for gate in gates
            if gate.state != PASS
        )
        return TimingProfileAdmissionReport(
            profile_status=profile_status,
            profile_id=(
                _required_text(profile.get("profileId"), "profileId")
                if profile_present
                and structural_complete
                and isinstance(profile.get("profileId"), str)
                else None
            ),
            profile_version=(
                _required_text(profile.get("profileVersion"), "profileVersion")
                if profile_present
                and structural_complete
                and isinstance(profile.get("profileVersion"), str)
                else None
            ),
            candidate_profile_hash=candidate_hash,
            structural_complete=structural_complete,
            source_registry_admitted=source_registry_admitted,
            isolated_research_profile_admitted=isolated_research_profile_admitted,
            directional_engine_implemented=False,
            directional_output_available=False,
            prospective_financial_validation_passed=prospective_passed,
            financial_use_allowed=False,
            validation_gates=tuple(gates),
            missing_requirements=missing_requirements,
        )
