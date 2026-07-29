from __future__ import annotations

import copy

from sbc.timing_profile_admission import (
    FAIL,
    PASS,
    STRUCTURALLY_COMPLETE_UNREGISTERED,
    UNKNOWN,
    SbcTimingProfileAdmissionGate,
)


def _registry(profiles: list[dict] | None = None) -> dict:
    return {
        "contract": "SBC_TIMING_PROFILE_REGISTRY_V1",
        "schemaVersion": 1,
        "profiles": profiles or [],
        "executionAllowed": False,
    }


def _candidate() -> dict:
    deterministic_policy = {
        "policyId": "explicit_rule_v1",
        "deterministicRule": "Resolve the named state from frozen profile inputs.",
        "fallbackState": "UNKNOWN",
    }
    return {
        "contract": "SBC_DIRECTIONAL_TIMING_PROFILE_V1",
        "schemaVersion": 1,
        "profileId": "candidate_timing_profile_v1",
        "profileVersion": "1.0.0",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
        "frozen": True,
        "sourceEvidence": [
            {
                "sourceId": "timing-source-1",
                "citation": "Candidate source, page 1",
                "sha256": "A" * 64,
                "role": "DOCTRINE",
            }
        ],
        "phaseSpan": {
            "unit": "DEGREES",
            "start": 0.0,
            "end": 360.0,
            "wraps": True,
        },
        "sectors": [
            {
                "sectorId": "sector-positive",
                "start": 0.0,
                "end": 90.0,
                "startInclusive": True,
                "endInclusive": False,
                "directionEligibility": "SAFE",
                "directionRole": "POSITIVE",
            },
            {
                "sectorId": "sector-unsafe-a",
                "start": 90.0,
                "end": 180.0,
                "startInclusive": True,
                "endInclusive": False,
                "directionEligibility": "UNSAFE",
                "directionRole": "NONE",
            },
            {
                "sectorId": "sector-negative",
                "start": 180.0,
                "end": 270.0,
                "startInclusive": True,
                "endInclusive": False,
                "directionEligibility": "SAFE",
                "directionRole": "NEGATIVE",
            },
            {
                "sectorId": "sector-unsafe-b",
                "start": 270.0,
                "end": 360.0,
                "startInclusive": True,
                "endInclusive": False,
                "directionEligibility": "UNSAFE",
                "directionRole": "NONE",
            },
        ],
        "boundaryPolicy": {
            "policyId": "boundary_margin_v1",
            "margin": 1.0,
            "unit": "DEGREES",
            "insideMarginState": "UNSAFE",
            "exactBoundaryState": "UNKNOWN",
        },
        "asymmetryPolicy": copy.deepcopy(deterministic_policy),
        "repeatedExactEventPolicy": copy.deepcopy(deterministic_policy),
        "retrogradeLoopPolicy": copy.deepcopy(deterministic_policy),
        "stationPolicy": {
            "policyId": "station_thresholds_v1",
            "deterministicRule": "Compare absolute speed with the body threshold.",
            "speedThresholdsByBody": {
                "MERCURY": 0.05,
                "JUPITER": 0.01,
                "SATURN": 0.005,
            },
            "fallbackState": "UNKNOWN",
        },
        "missingBoundaryPolicy": {
            "policyId": "missing_boundary_unknown_v1",
            "deterministicRule": "A missing boundary produces UNKNOWN.",
            "fallbackState": "UNKNOWN",
        },
        "unsupportedStatePolicy": {
            "policyId": "unsupported_unknown_v1",
            "deterministicRule": "Enumerated unsupported states produce UNKNOWN.",
            "enumeratedStates": [
                "MISSING_EPHEMERIS",
                "UNRESOLVED_LOOP",
                "UNCERTIFIED_SOURCE",
            ],
            "fallbackState": "UNKNOWN",
        },
        "eligibilityPolicy": {
            "activityFloor": 1.0,
            "coherenceFloor": 0.25,
            "maximumUnsafeActivationShare": 0.20,
            "minimumCoverage": 0.80,
        },
        "confidencePolicy": {
            "equation": "NORMALIZED_WEIGHTED_GEOMETRIC_MEAN_V1",
            "terms": [
                {
                    "termId": "coverage",
                    "weight": 1.0,
                    "sourceLineagePolicy": "DEDUPLICATE_IDENTICAL_SOURCE_LINEAGE",
                }
            ],
            "mandatoryGates": [
                "SOURCE_CERTIFIED",
                "SAFE_SECTOR",
                "MINIMUM_COVERAGE",
            ],
            "minimumCoverage": 0.80,
        },
        "guardrails": {
            "researchOnly": True,
            "readOnly": True,
            "noAutoSuggest": True,
            "noLiveInference": True,
            "noOfficialMlNotes": True,
            "noShadowVote": True,
            "noTradeOutput": True,
            "executionAllowed": False,
        },
    }


def _gate(report, gate_id: str):
    return next(item for item in report.validation_gates if item.gate_id == gate_id)


def test_no_profile_preserves_unknown_readiness_and_execution_lock() -> None:
    report = SbcTimingProfileAdmissionGate(_registry()).evaluate(None)

    assert report.profile_status == "NO_PROFILE_LOADED"
    assert _gate(report, "profile_core").state == UNKNOWN
    assert _gate(report, "server_registry_integrity").state == PASS
    assert report.structural_complete is False
    assert report.directional_output_available is False
    assert report.financial_use_allowed is False
    assert report.guardrails["execution_allowed"] is False


def test_complete_candidate_is_structurally_valid_but_unregistered() -> None:
    report = SbcTimingProfileAdmissionGate(_registry()).evaluate(_candidate())

    assert report.profile_status == STRUCTURALLY_COMPLETE_UNREGISTERED
    assert report.structural_complete is True
    assert _gate(report, "sector_partition").state == PASS
    assert _gate(report, "station_policy").state == PASS
    assert _gate(report, "frozen_source_certified_registration").state == UNKNOWN
    assert report.isolated_research_profile_admitted is False


def test_matching_source_certified_registry_entry_admits_profile_only() -> None:
    candidate = _candidate()
    first = SbcTimingProfileAdmissionGate(_registry()).evaluate(candidate)
    registered = {
        "profileHash": first.candidate_profile_hash,
        "profileId": candidate["profileId"],
        "profileVersion": candidate["profileVersion"],
        "frozen": True,
        "sourceCertified": True,
        "sourceAuditRefs": ["status/audits/future-source-audit.json"],
        "prospectiveTrialId": None,
    }
    report = SbcTimingProfileAdmissionGate(_registry([registered])).evaluate(
        candidate
    )

    assert report.source_registry_admitted is True
    assert report.isolated_research_profile_admitted is True
    assert _gate(report, "frozen_source_certified_registration").state == PASS
    assert report.directional_engine_implemented is False
    assert report.directional_output_available is False
    assert report.financial_use_allowed is False


def test_sector_gap_fails_profile_without_fabricating_direction() -> None:
    candidate = _candidate()
    candidate["sectors"][1]["start"] = 91.0

    report = SbcTimingProfileAdmissionGate(_registry()).evaluate(candidate)

    assert report.structural_complete is False
    assert _gate(report, "sector_partition").state == FAIL
    assert "gap-free partition" in _gate(
        report,
        "sector_partition",
    ).detail
    assert report.directional_output_available is False


def test_unsafe_sector_cannot_carry_direction_role() -> None:
    candidate = _candidate()
    candidate["sectors"][1]["directionRole"] = "POSITIVE"

    report = SbcTimingProfileAdmissionGate(_registry()).evaluate(candidate)

    assert _gate(report, "sector_partition").state == FAIL
    assert "UNSAFE sectors require directionRole NONE" in _gate(
        report,
        "sector_partition",
    ).detail


def test_station_thresholds_and_execution_lock_are_mandatory() -> None:
    candidate = _candidate()
    candidate["stationPolicy"]["speedThresholdsByBody"] = {}
    candidate["guardrails"]["executionAllowed"] = True

    report = SbcTimingProfileAdmissionGate(_registry()).evaluate(candidate)

    assert _gate(report, "station_policy").state == FAIL
    assert _gate(report, "profile_guardrails").state == FAIL
    assert report.isolated_research_profile_admitted is False
    assert report.guardrails["execution_allowed"] is False


def test_registry_that_allows_execution_fails_closed() -> None:
    registry = _registry()
    registry["executionAllowed"] = True

    report = SbcTimingProfileAdmissionGate(registry).evaluate(_candidate())

    assert _gate(report, "server_registry_integrity").state == FAIL
    assert report.source_registry_admitted is False
    assert report.financial_use_allowed is False


def test_prospective_pass_does_not_turn_t0_into_financial_output() -> None:
    candidate = _candidate()
    first = SbcTimingProfileAdmissionGate(_registry()).evaluate(candidate)
    trial_id = "future-timing-trial"
    registered = {
        "profileHash": first.candidate_profile_hash,
        "profileId": candidate["profileId"],
        "profileVersion": candidate["profileVersion"],
        "frozen": True,
        "sourceCertified": True,
        "sourceAuditRefs": ["status/audits/future-source-audit.json"],
        "prospectiveTrialId": trial_id,
    }
    trials = {
        "executionAllowed": False,
        "trials": [
            {
                "trialId": trial_id,
                "financiallyValidated": True,
                "executionAllowed": False,
            }
        ],
    }
    report = SbcTimingProfileAdmissionGate(
        _registry([registered]),
        trials,
    ).evaluate(candidate)

    assert _gate(report, "prospective_financial_validation").state == PASS
    assert report.prospective_financial_validation_passed is True
    assert report.financial_use_allowed is False
    assert report.directional_output_available is False
