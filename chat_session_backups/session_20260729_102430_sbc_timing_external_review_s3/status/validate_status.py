from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


STATUS_ROOT = Path(__file__).resolve().parent
STATE_VALUES = {"yes", "no", "not_applicable"}
EXPECTED_CONTRACTS = {
    "release_status.json": "GANN_RELEASE_STATUS_V1",
    "capability_status.json": "GANN_CAPABILITY_STATUS_V1",
    "research_trials.json": "GANN_RESEARCH_TRIAL_STATUS_V1",
    "source_certification.json": "GANN_SOURCE_CERTIFICATION_STATUS_V1",
    "mobile_acceptance_plan.json": "GANN_MOBILE_PHYSICAL_ACCEPTANCE_V1",
    "timing_phase_profile_registry.json": "SBC_TIMING_PROFILE_REGISTRY_V1",
}
CANONICAL_AUDITS = {
    "audits/sbc_phase_p0_gap_audit_20260728.json": "GANN_SBC_PHASE_P0_GAP_AUDIT_V1",
    "audits/sbc_atomic_intervals_p1_20260728.json": "GANN_SBC_ATOMIC_INTERVALS_P1_AUDIT_V1",
    "audits/sbc_multidimensional_ledger_p2_20260728.json": (
        "GANN_SBC_MULTIDIMENSIONAL_LEDGER_P2_AUDIT_V1"
    ),
    "audits/sbc_linked_audit_views_p3_20260728.json": (
        "GANN_SBC_LINKED_AUDIT_VIEWS_P3_AUDIT_V1"
    ),
    "audits/sbc_reproducible_audit_packages_p4_20260728.json": (
        "GANN_SBC_REPRODUCIBLE_AUDIT_PACKAGES_P4_AUDIT_V1"
    ),
    "audits/sbc_signed_audit_catalogs_p5_20260728.json": (
        "GANN_SBC_SIGNED_AUDIT_CATALOGS_P5_AUDIT_V1"
    ),
    "audits/sbc_fixed_zero_pi_phasor_f3_20260729.json": (
        "GANN_SBC_FIXED_ZERO_PI_PHASOR_F3_AUDIT_V1"
    ),
    "audits/sbc_timing_profile_admission_t0_20260729.json": (
        "GANN_SBC_TIMING_PROFILE_ADMISSION_T0_AUDIT_V1"
    ),
    "audits/sbc_timing_profile_source_packet_s1_20260729.json": (
        "GANN_SBC_TIMING_PROFILE_SOURCE_PACKET_S1_AUDIT_V1"
    ),
    "audits/sbc_timing_profile_source_verification_s2_20260729.json": (
        "GANN_SBC_TIMING_PROFILE_SOURCE_VERIFICATION_S2_AUDIT_V1"
    ),
    "audits/sbc_timing_profile_external_review_s3_20260729.json": (
        "GANN_SBC_TIMING_PROFILE_EXTERNAL_REVIEW_S3_AUDIT_V1"
    ),
}
P0_CORRECTION_IDS = {f"P0-R{number}" for number in range(1, 9)}
P0_INVENTORY_STATES = {"implemented_reuse", "partial_reuse", "absent", "blocked"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain one JSON object")
    return value


def _utc_timestamp(value: Any, label: str) -> None:
    normalized = str(value or "")
    if not normalized.endswith("Z"):
        raise ValueError(f"{label} must be an explicit UTC timestamp ending in Z")
    datetime.fromisoformat(normalized.replace("Z", "+00:00"))


def _unique(items: list[dict[str, Any]], key: str, label: str) -> None:
    values = [str(item.get(key) or "") for item in items]
    if any(not value for value in values):
        raise ValueError(f"{label} contains an empty {key}")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} contains duplicate {key} values")


def _execution_locked(document: dict[str, Any], label: str) -> None:
    if document.get("executionAllowed") is not False:
        raise ValueError(f"{label} must keep executionAllowed=false")


def _sha256(value: Any, label: str) -> str:
    normalized = str(value or "")
    if not re.fullmatch(r"[0-9A-F]{64}", normalized):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")
    return normalized


def _required_text(value: Any, label: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{label} is required")
    return normalized


def _canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest().upper()


def validate_release(document: dict[str, Any]) -> None:
    _utc_timestamp(document.get("asOfUtc"), "release status asOfUtc")
    _execution_locked(document, "release status")
    releases = list(document.get("releases") or [])
    _unique(releases, "releaseId", "release status")
    by_id = {item["releaseId"]: item for item in releases}
    selected = document.get("selectedAcceptancePair") or {}
    for key in ("desktopReleaseId", "mobileReleaseId"):
        if selected.get(key) not in by_id:
            raise ValueError(f"selected acceptance {key} is not a known release")
    for item in releases:
        _sha256(item.get("artifactSha256"), f"release {item['releaseId']} artifact")
        if item.get("installerSha256") is not None:
            _sha256(
                item.get("installerSha256"), f"release {item['releaseId']} installer"
            )
        if item.get("executionAllowed") is not False:
            raise ValueError(f"release {item['releaseId']} enables execution")
        if item.get("promotedStable") and (
            not item.get("physicallyTested") or item.get("sourceGitDirty")
        ):
            raise ValueError(
                f"release {item['releaseId']} cannot be stable without physical tests and clean source"
            )
    blockers = list(document.get("promotionBlockers") or [])
    if document.get("promotionAllowed") and blockers:
        raise ValueError("release promotion cannot be allowed while blockers remain")


def validate_capabilities(document: dict[str, Any]) -> None:
    _utc_timestamp(document.get("asOfUtc"), "capability status asOfUtc")
    _execution_locked(document, "capability status")
    capabilities = list(document.get("capabilities") or [])
    _unique(capabilities, "capabilityId", "capability status")
    required = {
        "implementedInSource",
        "packagedCandidate",
        "physicallyTested",
        "promotedStable",
        "sourceCertified",
        "financiallyValidated",
    }
    for item in capabilities:
        states = item.get("states") or {}
        if set(states) != required:
            raise ValueError(
                f"capability {item['capabilityId']} has an incomplete state matrix"
            )
        if set(states.values()) - STATE_VALUES:
            raise ValueError(
                f"capability {item['capabilityId']} uses an unknown state value"
            )
        if states["promotedStable"] == "yes" and states["packagedCandidate"] != "yes":
            raise ValueError(
                f"capability {item['capabilityId']} is stable but not packaged"
            )
        if item.get("executionAllowed") is not False:
            raise ValueError(f"capability {item['capabilityId']} enables execution")


def validate_trials(document: dict[str, Any]) -> None:
    _utc_timestamp(document.get("asOfUtc"), "research trial status asOfUtc")
    _execution_locked(document, "research trial status")
    trials = list(document.get("trials") or [])
    _unique(trials, "trialId", "research trial status")
    for item in trials:
        if item.get("cohortMutable") is not False:
            raise ValueError(
                f"trial {item['trialId']} must fail closed against cohort mutation"
            )
        financially_validated = item.get("financiallyValidated")
        if not isinstance(financially_validated, bool):
            raise ValueError(
                f"trial {item['trialId']} needs a boolean financiallyValidated"
            )
        if financially_validated and (
            item.get("status") != "passed_financial_validation"
            or not item.get("frozen")
        ):
            raise ValueError(
                f"trial {item['trialId']} cannot claim financial validation without a frozen passed gate"
            )
        if item.get("executionAllowed") is not False:
            raise ValueError(f"trial {item['trialId']} enables execution")
        if item.get("status") == "frozen_collecting" and not item.get("frozen"):
            raise ValueError(
                f"trial {item['trialId']} collects without a frozen identity"
            )


def validate_timing_profile_registry(document: dict[str, Any]) -> None:
    if document.get("schemaVersion") != 1:
        raise ValueError("timing profile registry schemaVersion must be 1")
    _execution_locked(document, "timing profile registry")
    profiles = document.get("profiles")
    if not isinstance(profiles, list):
        raise ValueError("timing profile registry profiles must be an array")
    allowed = {
        "profileHash",
        "profileId",
        "profileVersion",
        "frozen",
        "sourceCertified",
        "sourceAuditRefs",
        "prospectiveTrialId",
    }
    hashes: set[str] = set()
    for index, item in enumerate(profiles):
        if not isinstance(item, dict) or set(item) != allowed:
            raise ValueError(
                f"timing profile registry entry {index} has an incomplete schema"
            )
        profile_hash = _sha256(
            item.get("profileHash"),
            f"timing profile registry entry {index} profileHash",
        )
        if profile_hash in hashes:
            raise ValueError("timing profile registry contains duplicate hashes")
        hashes.add(profile_hash)
        _required_text(
            item.get("profileId"),
            f"timing profile registry entry {index} profileId",
        )
        _required_text(
            item.get("profileVersion"),
            f"timing profile registry entry {index} profileVersion",
        )
        if item.get("frozen") is not True:
            raise ValueError("registered timing profiles must be frozen")
        if item.get("sourceCertified") is not True:
            raise ValueError("registered timing profiles must be source-certified")
        refs = item.get("sourceAuditRefs")
        if not isinstance(refs, list) or not refs:
            raise ValueError(
                "registered timing profiles need source-certification audit refs"
            )
        for ref in refs:
            _required_text(ref, "timing profile source audit ref")
        if item.get("prospectiveTrialId") is not None:
            _required_text(
                item.get("prospectiveTrialId"),
                "timing profile prospectiveTrialId",
            )


def validate_sources(document: dict[str, Any]) -> None:
    _utc_timestamp(document.get("asOfUtc"), "source status asOfUtc")
    _execution_locked(document, "source certification status")
    items = list(document.get("certifications") or [])
    _unique(items, "certificationId", "source certification status")
    for item in items:
        certified = item.get("sourceCertified")
        if not isinstance(certified, bool):
            raise ValueError(
                f"source {item['certificationId']} needs a boolean sourceCertified"
            )
        status = str(item.get("status") or "")
        if certified and (
            not item.get("evidenceRefs")
            or any(token in status for token in ("blocked", "failed", "pending"))
            or not any(token in status for token in ("passed", "certified"))
        ):
            raise ValueError(
                f"source {item['certificationId']} is marked certified without a completed gate"
            )


def validate_mobile_plan(document: dict[str, Any]) -> None:
    _utc_timestamp(document.get("createdAtUtc"), "mobile plan createdAtUtc")
    _execution_locked(document, "mobile acceptance plan")
    if document.get("promotionAllowed") is not False:
        raise ValueError(
            "mobile acceptance plan cannot promote before evidence is complete"
        )
    tests = list(document.get("tests") or [])
    _unique(tests, "testId", "mobile acceptance plan")
    expected = [f"MOB-{number:02d}" for number in range(1, 9)]
    if [item["testId"] for item in tests] != expected:
        raise ValueError(
            "mobile acceptance plan must contain MOB-01 through MOB-08 in order"
        )
    for side in ("desktopCandidate", "mobileCandidate"):
        _sha256(document.get(side, {}).get("artifactSha256"), f"{side} artifact")


def validate_sbc_phase_p0_audit(document: dict[str, Any], project_root: Path) -> None:
    _utc_timestamp(document.get("auditedAtUtc"), "SBC phase P0 audit auditedAtUtc")
    _execution_locked(document, "SBC phase P0 audit")
    if document.get("phase") != "P0_GAP_AUDIT":
        raise ValueError("SBC phase P0 audit has an unexpected phase")
    if document.get("implementationChanged") is not False:
        raise ValueError("SBC phase P0 audit must not claim an implementation change")
    if document.get("promotionAllowed") is not False:
        raise ValueError("SBC phase P0 audit cannot allow promotion")

    sources = list(document.get("sourceDocuments") or [])
    _unique(sources, "sourceId", "SBC phase P0 source documents")
    for source in sources:
        _sha256(source.get("sha256"), f"SBC phase P0 source {source['sourceId']}")
        if source.get("doctrineAuthority") is not False:
            raise ValueError(
                f"SBC phase P0 source {source['sourceId']} must not claim doctrine authority"
            )
        repository_path = source.get("repositoryPath")
        if repository_path:
            path = (project_root / str(repository_path)).resolve()
            if not path.is_file():
                raise ValueError(
                    f"SBC phase P0 tracked source is missing: {repository_path}"
                )
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest().upper()
            if actual_hash != source["sha256"]:
                raise ValueError(
                    f"SBC phase P0 tracked source hash differs: {repository_path}"
                )

    inventory = list(document.get("currentInventory") or [])
    _unique(inventory, "capabilityId", "SBC phase P0 inventory")
    for item in inventory:
        if item.get("state") not in P0_INVENTORY_STATES:
            raise ValueError(
                f"SBC phase P0 inventory {item['capabilityId']} has an unknown state"
            )
        evidence_path = item.get("evidencePath")
        if evidence_path and not (project_root / str(evidence_path)).exists():
            raise ValueError(
                f"SBC phase P0 inventory evidence is missing: {evidence_path}"
            )

    corrections = list(document.get("residualContractCorrections") or [])
    _unique(corrections, "correctionId", "SBC phase P0 residual corrections")
    correction_ids = {item["correctionId"] for item in corrections}
    if correction_ids != P0_CORRECTION_IDS:
        raise ValueError(
            "SBC phase P0 audit must retain corrections P0-R1 through P0-R8"
        )
    if any(not str(item.get("requiredBefore") or "") for item in corrections):
        raise ValueError("SBC phase P0 corrections must name their dependent milestone")

    adopted = list(document.get("adoptedCorrections") or [])
    if len(adopted) != len(set(adopted)) or any(not str(item) for item in adopted):
        raise ValueError(
            "SBC phase P0 adopted corrections must be unique and non-empty"
        )

    boundary = document.get("p1Boundary") or {}
    if boundary.get("capabilityId") != "sbc_atomic_state_intervals_v1":
        raise ValueError("SBC phase P0 audit has an unexpected P1 capability")
    if boundary.get("phaseEngineIncluded") is not False:
        raise ValueError("SBC phase P1 must exclude the phase engine")
    if boundary.get("completed") is not False:
        raise ValueError("SBC phase P1 cannot be complete during P0")
    for field in ("entryCriteria", "exitCriteria"):
        values = list(boundary.get(field) or [])
        if not values or len(values) != len(set(values)):
            raise ValueError(f"SBC phase P1 {field} must be unique and non-empty")

    guardrails = document.get("guardrails") or {}
    if guardrails.get("researchOnly") is not True:
        raise ValueError("SBC phase P0 audit must remain research-only")
    if guardrails.get("sourceProfiledExperimentalOnly") is not True:
        raise ValueError("SBC phase P0 audit must remain source-profiled experimental")
    false_locks = {
        "countsAsIndependentVote",
        "consumedByLiveInference",
        "consumedByAutoSuggest",
        "consumedByShadowLedger",
        "consumedByOfficialMlNotes",
        "prospectiveTrialRegistered",
        "windowsPackageChanged",
        "androidPackageChanged",
        "runtimeBehaviorChanged",
        "executionAllowed",
    }
    for field in false_locks:
        if guardrails.get(field) is not False:
            raise ValueError(f"SBC phase P0 guardrail {field} must remain false")
    if guardrails.get("directionalContribution") != 0:
        raise ValueError("SBC phase P0 directional contribution must remain zero")


def validate_sbc_atomic_intervals_p1_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(document.get("auditedAtUtc"), "SBC atomic P1 audit auditedAtUtc")
    _execution_locked(document, "SBC atomic P1 audit")
    if document.get("capabilityId") != "multidimensional_sbc_atomic_intervals_v1":
        raise ValueError("SBC atomic P1 audit has an unexpected capability")
    if document.get("status") != "implemented_in_source_research_only":
        raise ValueError("SBC atomic P1 audit has an unexpected status")
    if document.get("packagedCandidate") is not False:
        raise ValueError("SBC atomic P1 audit cannot claim a packaged candidate")
    if document.get("financiallyValidated") is not False:
        raise ValueError("SBC atomic P1 audit cannot claim financial validation")
    if document.get("promotionAllowed") is not False:
        raise ValueError("SBC atomic P1 audit cannot allow promotion")

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "seriesContract": "SBC_ATOMIC_INTERVAL_SERIES_V1",
        "boundaryPolicy": "EXPLICIT_BOUNDARY_STATES_V1",
        "contributionContract": "SBC_ATOMIC_CONTRIBUTION_V1",
        "sourceLineageContract": "SBC_ATOMIC_SOURCE_LINEAGE_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(f"SBC atomic P1 {field} differs from {expected}")
    for field in ("modulePath", "testPath", "acceptancePath", "milestonePath"):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(f"SBC atomic P1 evidence is missing: {path}")
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC atomic P1 module canonical text",
    )
    actual_hash = _canonical_text_sha256(module_path)
    if actual_hash != expected_hash:
        raise ValueError("SBC atomic P1 module hash differs from the audit")

    semantics = document.get("intervalSemantics") or {}
    expected_semantics = {
        "intervalForm": "[startUtc,endUtc)",
        "inputOrder": "canonical_chronological_sort",
        "duplicateBoundaryTimestamps": "rejected",
        "nonPositiveDuration": "rejected",
        "profileMixing": "rejected",
        "evidenceCutoffRule": "cutoff_not_later_than_interval_start",
        "boundaryDiscoveryIncluded": False,
    }
    if semantics != expected_semantics:
        raise ValueError("SBC atomic P1 interval semantics drifted")

    accounting = document.get("accounting") or {}
    if accounting.get("grossActivationUnits") != "sum_absolute_scored_contributions":
        raise ValueError("SBC atomic P1 gross activation semantics drifted")
    if accounting.get("unknownMagnitudeWhenUnknown") is not None:
        raise ValueError("SBC atomic P1 unknown magnitude must remain null")
    if accounting.get("unknownMagnitudeWhenKnown") != 0:
        raise ValueError("SBC atomic P1 known-empty unknown magnitude must remain zero")
    unknown_sources = set(accounting.get("unknownCountIncludes") or [])
    if unknown_sources != {"unresolved_contributions", "explicit_missing_evidence"}:
        raise ValueError("SBC atomic P1 unknown-count sources drifted")

    lineage = document.get("lineage") or {}
    required_true_lineage = {
        "sourceAndEvaluationIdentitySeparated",
        "canonicalSha256",
        "profileHashesPreserved",
        "targetWitnessMetadataPreserved",
        "citationSourceIdsPreserved",
    }
    for field in required_true_lineage:
        if lineage.get(field) is not True:
            raise ValueError(f"SBC atomic P1 lineage lock {field} must remain true")
    if lineage.get("causalClusterVotingImplemented") is not False:
        raise ValueError("SBC atomic P1 cannot claim causal-cluster voting")

    guardrails = document.get("guardrails") or {}
    for field in (
        "researchOnly",
        "timestampSafe",
        "noLookahead",
        "sourceProfiledExperimental",
    ):
        if guardrails.get(field) is not True:
            raise ValueError(f"SBC atomic P1 guardrail {field} must remain true")
    false_locks = {
        "countsAsIndependentVote",
        "phaseOutputIncluded",
        "confidenceOutputIncluded",
        "marketDirectionIncluded",
        "consumedByAutoSuggest",
        "consumedByLiveInference",
        "consumedByOfficialMlNotes",
        "consumedByShadowLedger",
        "tradeOutputIncluded",
        "executionAllowed",
    }
    for field in false_locks:
        if guardrails.get(field) is not False:
            raise ValueError(f"SBC atomic P1 guardrail {field} must remain false")
    if guardrails.get("directionalContribution") != 0:
        raise ValueError("SBC atomic P1 directional contribution must remain zero")

    verification = document.get("verification") or {}
    expected_verification = {
        "newAtomicIntervalTests": "11_passed",
        "focusedSbcChakraFxTests": "93_passed",
        "statusValidation": "8_passed",
        "repositoryPythonTests": "405_passed",
        "pythonRuff": "passed",
    }
    if verification != expected_verification:
        raise ValueError("SBC atomic P1 verification evidence is incomplete")


def validate_sbc_multidimensional_ledger_p2_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC multidimensional P2 audit auditedAtUtc",
    )
    _execution_locked(document, "SBC multidimensional P2 audit")
    if document.get("capabilityId") != "multidimensional_sbc_ledger_v1":
        raise ValueError("SBC multidimensional P2 audit has an unexpected capability")
    if document.get("status") != "implemented_in_source_research_only":
        raise ValueError("SBC multidimensional P2 audit has an unexpected status")
    if document.get("packagedCandidate") is not False:
        raise ValueError("SBC multidimensional P2 audit cannot claim packaging")
    if document.get("financiallyValidated") is not False:
        raise ValueError(
            "SBC multidimensional P2 audit cannot claim financial validation"
        )
    if document.get("promotionAllowed") is not False:
        raise ValueError("SBC multidimensional P2 audit cannot allow promotion")

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "seriesContract": "SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1",
        "causalClusterContract": "SBC_CAUSAL_CLUSTER_V1",
        "dimensionCellContract": "SBC_LEDGER_DIMENSION_CELL_V1",
        "missingEvidenceLineageContract": "SBC_MISSING_EVIDENCE_LINEAGE_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(f"SBC multidimensional P2 {field} differs from {expected}")
    for field in (
        "modulePath",
        "testPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(f"SBC multidimensional P2 evidence is missing: {path}")
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC multidimensional P2 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError("SBC multidimensional P2 module hash differs from the audit")

    expected_roles = [
        "PRIMARY_EVIDENCE",
        "DERIVED_AXIS",
        "VISUALIZATION_ONLY",
        "NON_VOTING_CONTEXT",
    ]
    if implementation.get("derivationRoles") != expected_roles:
        raise ValueError("SBC multidimensional P2 derivation roles drifted")
    expected_axes = [
        "TOTAL",
        "ACTOR",
        "TARGET_LAYER",
        "NATURE",
        "VEDHA_DIRECTION",
        "SOURCE_LINEAGE",
    ]
    if implementation.get("ledgerAxes") != expected_axes:
        raise ValueError("SBC multidimensional P2 ledger axes drifted")

    deduplication = document.get("deduplication") or {}
    expected_deduplication = {
        "unit": "one_source_lineage_per_atomic_interval",
        "exactRepeat": "deduplicated",
        "conflictingEvaluations": "rejected",
        "missingEvidenceRepeat": "deduplicated",
        "evaluatedMagnitudeInClusterIdentity": False,
        "contributionIdPreservedSeparately": True,
    }
    if deduplication != expected_deduplication:
        raise ValueError("SBC multidimensional P2 deduplication contract drifted")

    reconciliation = document.get("reconciliation") or {}
    expected_reconciliation = {
        "scalarP1LedgerReproduced": True,
        "everyClusterExactlyOncePerAxis": True,
        "unavailableDimensionKey": "UNAVAILABLE",
        "fields": [
            "favorable_guidance_units",
            "adverse_guidance_units",
            "net_guidance_units",
            "gross_activation_units",
            "scored_contribution_count",
            "unknown_contribution_count",
            "missing_evidence_count",
            "total_evidence_count",
        ],
    }
    if reconciliation != expected_reconciliation:
        raise ValueError("SBC multidimensional P2 reconciliation contract drifted")

    guardrails = document.get("guardrails") or {}
    for field in (
        "researchOnly",
        "timestampSafe",
        "noLookahead",
        "sourceProfiledExperimental",
    ):
        if guardrails.get(field) is not True:
            raise ValueError(
                f"SBC multidimensional P2 guardrail {field} must remain true"
            )
    false_locks = {
        "countsAsIndependentVote",
        "fxSubtractionIncluded",
        "phaseOutputIncluded",
        "confidenceOutputIncluded",
        "marketDirectionIncluded",
        "consumedByAutoSuggest",
        "consumedByLiveInference",
        "consumedByOfficialMlNotes",
        "consumedByShadowLedger",
        "tradeOutputIncluded",
        "executionAllowed",
    }
    for field in false_locks:
        if guardrails.get(field) is not False:
            raise ValueError(
                f"SBC multidimensional P2 guardrail {field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC multidimensional P2 directional contribution must remain zero"
        )

    expected_verification = {
        "newMultidimensionalLedgerTests": "10_passed",
        "focusedSbcChakraFxTests": "103_passed",
        "statusValidation": "11_passed",
        "repositoryPythonTests": "418_passed",
        "pythonRuff": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError("SBC multidimensional P2 verification evidence is incomplete")


def validate_sbc_linked_audit_views_p3_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC linked audit P3 auditedAtUtc",
    )
    _execution_locked(document, "SBC linked audit P3")
    if document.get("capabilityId") != "sbc_linked_audit_views_v1":
        raise ValueError("SBC linked audit P3 has an unexpected capability")
    if document.get("status") != "implemented_in_source_research_only":
        raise ValueError("SBC linked audit P3 has an unexpected status")
    if document.get("packagedCandidate") is not False:
        raise ValueError("SBC linked audit P3 cannot claim packaging")
    if document.get("financiallyValidated") is not False:
        raise ValueError("SBC linked audit P3 cannot claim financial validation")
    if document.get("promotionAllowed") is not False:
        raise ValueError("SBC linked audit P3 cannot allow promotion")

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "linkedAuditContract": "SBC_LINKED_AUDIT_VIEW_V1",
        "schemaVersion": 1,
        "policy": "LINKED_READ_ONLY_PROGRESSIVE_DISCLOSURE_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(f"SBC linked audit P3 {field} differs from {expected}")
    for field in (
        "modulePath",
        "testPath",
        "servicePath",
        "serviceTestPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(f"SBC linked audit P3 evidence is missing: {path}")
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC linked audit P3 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError("SBC linked audit P3 module hash differs from the audit")

    expected_states = ["PASS", "FAIL", "UNKNOWN"]
    if implementation.get("validationStates") != expected_states:
        raise ValueError("SBC linked audit P3 validation states drifted")
    expected_views = [
        "TIMELINE",
        "LEDGER",
        "RAY_AUDIT",
        "SOURCE_LINEAGE",
        "RECONCILIATION",
        "VALIDATION",
    ]
    if implementation.get("viewIds") != expected_views:
        raise ValueError("SBC linked audit P3 view IDs drifted")

    expected_projection = {
        "inputContract": "SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1",
        "inputSchemaVersion": 1,
        "recomputesEvidenceWeights": False,
        "preservesIntervalIds": True,
        "preservesCellIds": True,
        "preservesClusterIds": True,
        "preservesSourceLineage": True,
        "crossLinksValidated": True,
        "unreconciledInputRejected": True,
        "unknownEvidenceVisible": True,
        "unknownMagnitudeMayRemainNull": True,
        "deterministicAuditHash": True,
    }
    if (document.get("projection") or {}) != expected_projection:
        raise ValueError("SBC linked audit P3 projection contract drifted")

    expected_gates = [
        "TIMESTAMP_SAFETY",
        "AXIS_RECONCILIATION",
        "UNKNOWN_EVIDENCE",
        "FINANCIAL_VALIDATION",
        "PHASE_PROFILE",
        "EXECUTION_LOCK",
    ]
    if document.get("validationGates") != expected_gates:
        raise ValueError("SBC linked audit P3 validation gates drifted")

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "browserSuppliesComputedEvidence": False,
        "backendRecomputesChakraP1P2P3": True,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError("SBC linked audit P3 transport contract drifted")

    guardrails = document.get("guardrails") or {}
    for field in (
        "researchOnly",
        "readOnly",
        "timestampSafe",
        "noLookahead",
        "sourceProfiledExperimental",
    ):
        if guardrails.get(field) is not True:
            raise ValueError(f"SBC linked audit P3 guardrail {field} must remain true")
    false_locks = {
        "countsAsIndependentVote",
        "fxSubtractionIncluded",
        "phaseOutputIncluded",
        "confidenceOutputIncluded",
        "marketDirectionIncluded",
        "consumedByAutoSuggest",
        "consumedByLiveInference",
        "consumedByOfficialMlNotes",
        "consumedByShadowLedger",
        "tradeOutputIncluded",
        "executionAllowed",
    }
    for field in false_locks:
        if guardrails.get(field) is not False:
            raise ValueError(f"SBC linked audit P3 guardrail {field} must remain false")
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC linked audit P3 directional contribution must remain zero"
        )

    expected_verification = {
        "newLinkedAuditTests": "6_passed",
        "chakraServiceTests": "6_passed",
        "focusedFrontendTests": "9_passed",
        "statusValidation": "14_passed",
        "repositoryPythonTests": "430_passed",
        "pythonRuff": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustCheck": "passed",
        "browserVisualAcceptance": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError("SBC linked audit P3 verification evidence is incomplete")


def validate_sbc_reproducible_audit_packages_p4_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC reproducible audit P4 auditedAtUtc",
    )
    _execution_locked(document, "SBC reproducible audit P4")
    if document.get("capabilityId") != "sbc_reproducible_audit_packages_v1":
        raise ValueError("SBC reproducible audit P4 has an unexpected capability")
    if document.get("status") != "implemented_in_source_research_only":
        raise ValueError("SBC reproducible audit P4 has an unexpected status")
    if document.get("packagedCandidate") is not False:
        raise ValueError("SBC reproducible audit P4 cannot claim packaging")
    if document.get("financiallyValidated") is not False:
        raise ValueError("SBC reproducible audit P4 cannot claim financial validation")
    if document.get("promotionAllowed") is not False:
        raise ValueError("SBC reproducible audit P4 cannot allow promotion")

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "packageContract": "SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1",
        "verificationContract": "SBC_AUDIT_PACKAGE_VERIFICATION_V1",
        "schemaVersion": 1,
        "policy": "READ_ONLY_COMPARISON_EXPORT_REPLAY_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(
                f"SBC reproducible audit P4 {field} differs from {expected}"
            )
    for field in (
        "modulePath",
        "testPath",
        "servicePath",
        "serviceTestPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(f"SBC reproducible audit P4 evidence is missing: {path}")
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC reproducible audit P4 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError("SBC reproducible audit P4 module hash differs from the audit")
    if implementation.get("validationStates") != ["PASS", "FAIL", "UNKNOWN"]:
        raise ValueError("SBC reproducible audit P4 validation states drifted")

    expected_projection = {
        "inputContract": "SBC_LINKED_AUDIT_VIEW_V1",
        "inputSchemaVersion": 1,
        "singleCanonicalSourceAudit": True,
        "baselineRequired": True,
        "multipleComparisonsAllowed": True,
        "comparisonOrder": "stable_source_interval_order",
        "deltaConvention": "comparison_minus_baseline",
        "descriptiveOnly": True,
        "preservesIntervalIds": True,
        "preservesCellIds": True,
        "preservesClusterIds": True,
        "preservesSourceLineage": True,
        "manualBookmarksOnly": True,
        "jsonExport": True,
        "escapedHtmlExport": True,
        "portableNumericCanonicalization": True,
        "fullReplayChain": "CHAKRA_TO_P1_TO_P2_TO_P3_TO_P4",
    }
    if (document.get("projection") or {}) != expected_projection:
        raise ValueError("SBC reproducible audit P4 projection contract drifted")

    expected_gates = [
        "SOURCE_AUDIT_LOCKS",
        "COMPARISON_LINKS",
        "REPLAY_RECIPE",
        "MANUAL_BOOKMARKS",
        "UNKNOWN_EVIDENCE",
        "FINANCIAL_INTERPRETATION",
        "EXECUTION_LOCK",
    ]
    if document.get("validationGates") != expected_gates:
        raise ValueError("SBC reproducible audit P4 validation gates drifted")

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "browserSuppliesComputedEvidence": False,
        "backendRecomputesChakraP1P2P3P4": True,
        "replayRequiredForVerification": True,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError("SBC reproducible audit P4 transport contract drifted")

    guardrails = document.get("guardrails") or {}
    for field in (
        "researchOnly",
        "readOnly",
        "timestampSafe",
        "noLookahead",
        "sourceProfiledExperimental",
        "descriptiveComparisonOnly",
        "manualAnnotationsOnly",
        "replayRequiredForVerification",
    ):
        if guardrails.get(field) is not True:
            raise ValueError(
                f"SBC reproducible audit P4 guardrail {field} must remain true"
            )
    for field in (
        "financiallyValidated",
        "countsAsIndependentVote",
        "fxSubtractionIncluded",
        "phaseOutputIncluded",
        "confidenceOutputIncluded",
        "marketDirectionIncluded",
        "consumedByAutoSuggest",
        "consumedByLiveInference",
        "consumedByOfficialMlNotes",
        "consumedByShadowLedger",
        "tradeOutputIncluded",
        "executionAllowed",
    ):
        if guardrails.get(field) is not False:
            raise ValueError(
                f"SBC reproducible audit P4 guardrail {field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC reproducible audit P4 directional contribution must remain zero"
        )

    expected_verification = {
        "newAuditPackageTests": "6_passed",
        "chakraServiceTests": "9_passed",
        "chakraAuditWorkspaceTests": "4_passed",
        "frontendTests": "95_passed",
        "statusValidation": "17_passed",
        "repositoryPythonTests": "442_passed",
        "pythonRuff": "passed",
        "frontendLint": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustCheck": "passed",
        "browserVisualAcceptance": "passed",
        "browserReplayVerification": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError(
            "SBC reproducible audit P4 verification evidence is incomplete"
        )


def validate_sbc_signed_audit_catalogs_p5_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC signed audit catalog P5 auditedAtUtc",
    )
    _execution_locked(document, "SBC signed audit catalog P5")
    if document.get("capabilityId") != "sbc_signed_audit_catalogs_v1":
        raise ValueError("SBC signed audit catalog P5 has an unexpected capability")
    if document.get("status") != "implemented_in_source_research_only":
        raise ValueError("SBC signed audit catalog P5 has an unexpected status")
    for field in (
        "packagedCandidate",
        "externallyAttestedIdentity",
        "financiallyValidated",
        "promotionAllowed",
    ):
        if document.get(field) is not False:
            raise ValueError(f"SBC signed audit catalog P5 {field} must remain false")

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "catalogContract": "SBC_AUDIT_PACKAGE_CATALOG_V1",
        "signatureContract": "SBC_AUDIT_CATALOG_SIGNATURE_V1",
        "bundleContract": "SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1",
        "verificationContract": "SBC_AUDIT_CATALOG_VERIFICATION_V1",
        "schemaVersion": 1,
        "catalogPolicy": "SEALED_PACKAGE_CATALOG_NO_CROSS_AUDIT_INFERENCE_V1",
        "bundlePolicy": "SIGNED_PORTABLE_RESEARCH_EXCHANGE_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
        "signatureAlgorithm": "ED25519",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(
                f"SBC signed audit catalog P5 {field} differs from {expected}"
            )
    for field in (
        "modulePath",
        "testPath",
        "standaloneVerifierPath",
        "servicePath",
        "serviceTestPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(f"SBC signed audit catalog P5 evidence is missing: {path}")
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC signed audit catalog P5 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError(
            "SBC signed audit catalog P5 module hash differs from the audit"
        )

    expected_catalog = {
        "minimumPackages": 1,
        "uniquePackageIdsRequired": True,
        "completeP4ReplayRequired": True,
        "stableOrder": "package_id",
        "embedsCanonicalP4Bytes": True,
        "portablePackageIdentity": True,
        "portableEntryIdentity": True,
        "portableCatalogIdentity": True,
        "crossPackageComputation": False,
    }
    if (document.get("catalog") or {}) != expected_catalog:
        raise ValueError("SBC signed audit catalog P5 catalog contract drifted")

    expected_verification_levels = {
        "integrityOnly": {
            "signatureAndStructure": True,
            "embeddedP4SemanticReplay": False,
            "semanticReplayState": "NOT_PERFORMED",
        },
        "fullReplay": {
            "signatureAndStructure": True,
            "embeddedP4SemanticReplay": True,
            "requiredPassState": "PASS",
        },
        "standaloneVerifierImportsApplicationSbc": False,
        "standaloneSemanticReplayState": "NOT_PERFORMED",
    }
    if (document.get("verificationLevels") or {}) != expected_verification_levels:
        raise ValueError("SBC signed audit catalog P5 verification levels drifted")

    expected_key_management = {
        "platform": "Windows",
        "privateKeyProtection": "DPAPI_CURRENT_USER",
        "privateKeyOutsideGit": True,
        "defaultDirectory": ("D:\\GannFinancialAstro\\app_data\\sbc_audit_catalog"),
        "privateKeyExported": False,
        "publicKeyExported": True,
        "externallyAttestedIdentity": False,
    }
    if (document.get("keyManagement") or {}) != expected_key_management:
        raise ValueError("SBC signed audit catalog P5 key management drifted")

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "browserSuppliesPrivateKey": False,
        "backendRecomputesChakraP1P2P3P4": True,
        "readOnlyRuntimeRequired": True,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError("SBC signed audit catalog P5 transport contract drifted")

    guardrails = document.get("guardrails") or {}
    for field in (
        "researchOnly",
        "readOnly",
        "timestampSafe",
        "noLookahead",
        "sourceProfiledExperimental",
        "catalogOnly",
        "embeddedP4ReplayRequired",
        "noCrossPackageArithmetic",
        "noCrossPackageVoting",
        "noMarketDirection",
        "noConfidenceOutput",
        "signaturesProveIntegrityOnly",
    ):
        if guardrails.get(field) is not True:
            raise ValueError(
                f"SBC signed audit catalog P5 guardrail {field} must remain true"
            )
    for field in (
        "financiallyValidated",
        "countsAsIndependentVote",
        "executionAllowed",
    ):
        if guardrails.get(field) is not False:
            raise ValueError(
                f"SBC signed audit catalog P5 guardrail {field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC signed audit catalog P5 directional contribution must remain zero"
        )
    expected_blocked = [
        "CROSS_AUDIT_ARITHMETIC",
        "CROSS_PACKAGE_VOTING",
        "FX_SUBTRACTION",
        "PHASE_OUTPUT",
        "CONFIDENCE_OUTPUT",
        "MARKET_DIRECTION",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VALIDATION_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    ]
    if guardrails.get("blockedCapabilities") != expected_blocked:
        raise ValueError("SBC signed audit catalog P5 blockedCapabilities drifted")

    expected_verification = {
        "newAuditCatalogTests": "6_passed",
        "chakraServiceTests": "10_passed",
        "chakraAuditWorkspaceTests": "4_passed",
        "frontendTests": "96_passed",
        "statusValidation": "25_passed",
        "repositoryPythonTests": "452_passed",
        "pythonRuff": "changed_scope_passed",
        "repositoryWidePythonRuff": "blocked_by_19_out_of_scope_findings",
        "frontendLint": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustCheck": "passed",
        "standaloneVerifier": "passed",
        "dpapiKeyRoundTrip": "passed",
        "packagingDependencyPreflight": "passed",
        "browserVisualAcceptance": "passed",
        "browserIntegrityOnlyVerification": "semantic_replay_not_performed",
        "browserFullReplayVerification": "semantic_replay_passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError(
            "SBC signed audit catalog P5 verification evidence is incomplete"
        )


def validate_sbc_fixed_zero_pi_phasor_f3_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC fixed zero/pi phasor F3 auditedAtUtc",
    )
    _execution_locked(document, "SBC fixed zero/pi phasor F3")
    if document.get("capabilityId") != "fixed_zero_pi_scalar_phasor_visualization_v1":
        raise ValueError("SBC fixed zero/pi phasor F3 has an unexpected capability")
    if document.get("status") != "implemented_in_source_research_only":
        raise ValueError("SBC fixed zero/pi phasor F3 has an unexpected status")
    for field in (
        "packagedCandidate",
        "financiallyValidated",
        "promotionAllowed",
    ):
        if document.get(field) is not False:
            raise ValueError(f"SBC fixed zero/pi phasor F3 {field} must remain false")

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "inputContract": "SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1",
        "projectionContract": "SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1",
        "schemaVersion": 1,
        "projectionPolicy": "FIXED_ZERO_PI_SCALAR_PARITY_VISUALIZATION_ONLY_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(
                f"SBC fixed zero/pi phasor F3 {field} differs from {expected}"
            )
    for field in (
        "modulePath",
        "testPath",
        "servicePath",
        "serviceTestPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(f"SBC fixed zero/pi phasor F3 evidence is missing: {path}")
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC fixed zero/pi phasor F3 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError(
            "SBC fixed zero/pi phasor F3 module hash differs from the audit"
        )

    expected_projection = {
        "nonNegativeFixedAngle": "ZERO",
        "nonNegativeFixedAngleRadians": 0.0,
        "negativeFixedAngle": "PI",
        "negativeFixedAngleRadians": 3.141592653589793,
        "magnitude": "abs(signed_guidance_units)",
        "realComponent": "signed_guidance_units",
        "imaginaryComponent": 0.0,
        "unknownProjectionStatus": "UNKNOWN_NOT_PLOTTED",
        "unknownMagnitude": None,
        "knownScoredCoherence": (
            "abs(vector_real_sum_units)/vector_magnitude_sum_units"
        ),
        "sourceUnitReinterpretation": False,
    }
    if (document.get("projection") or {}) != expected_projection:
        raise ValueError("SBC fixed zero/pi phasor F3 projection domain drifted")

    expected_parity = {
        "realSumMatchesP2Net": True,
        "magnitudeSumMatchesP2Gross": True,
        "imaginarySumZero": True,
        "countsMatchP2": True,
        "unknownsPreserved": True,
        "compilerFailsClosedOnMismatch": True,
        "sourceLedgerRemainsCanonicalEvidence": True,
    }
    if (document.get("parity") or {}) != expected_parity:
        raise ValueError("SBC fixed zero/pi phasor F3 parity contract drifted")

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "backendRecomputesChakraP1P2F3": True,
        "browserSuppliesDerivedLedger": False,
        "readOnlyRuntimeRequired": True,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError("SBC fixed zero/pi phasor F3 transport contract drifted")

    guardrails = document.get("guardrails") or {}
    for field in (
        "researchOnly",
        "readOnly",
        "timestampSafe",
        "noLookahead",
        "sourceProfiledExperimental",
        "scalarEquivalentOnly",
        "fixedZeroPiOnly",
        "visualizationOnly",
    ):
        if guardrails.get(field) is not True:
            raise ValueError(
                f"SBC fixed zero/pi phasor F3 guardrail {field} must remain true"
            )
    for field in (
        "physicalWaveClaimed",
        "timingPhaseIncluded",
        "timingSectorProfileIncluded",
        "fxSubtractionIncluded",
        "confidenceIncluded",
        "financiallyValidated",
        "countsAsIndependentVote",
        "executionAllowed",
    ):
        if guardrails.get(field) is not False:
            raise ValueError(
                f"SBC fixed zero/pi phasor F3 guardrail {field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC fixed zero/pi phasor F3 directional contribution must remain zero"
        )
    expected_blocked = [
        "PHYSICAL_WAVE_INTERPRETATION",
        "TIMING_PHASE_OUTPUT",
        "TIMING_SECTOR_DIRECTION",
        "FX_SUBTRACTION",
        "CONFIDENCE_OUTPUT",
        "MARKET_DIRECTION",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VALIDATION_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    ]
    if guardrails.get("blockedCapabilities") != expected_blocked:
        raise ValueError("SBC fixed zero/pi phasor F3 blockedCapabilities drifted")

    expected_verification = {
        "newFixedPhasorTests": "6_passed",
        "chakraServiceTests": "11_passed",
        "chakraAuditWorkspaceTests": "4_passed",
        "frontendTests": "96_passed",
        "statusValidation": "23_passed",
        "repositoryPythonTests": "462_passed",
        "pythonRuff": "changed_scope_passed",
        "repositoryWidePythonRuff": "blocked_by_19_out_of_scope_findings",
        "frontendLint": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustCheck": "passed",
        "browserVisualAcceptance": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError(
            "SBC fixed zero/pi phasor F3 verification evidence is incomplete"
        )


def validate_sbc_timing_profile_admission_t0_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC timing profile admission T0 auditedAtUtc",
    )
    _execution_locked(document, "SBC timing profile admission T0")
    if document.get("capabilityId") != "timing_profile_admission_gate_v1":
        raise ValueError("SBC timing profile admission T0 has an unexpected capability")
    if document.get("status") != "implemented_in_source_profile_absent":
        raise ValueError("SBC timing profile admission T0 has an unexpected status")
    for field in (
        "packagedCandidate",
        "profileRegistered",
        "directionalEngineImplemented",
        "financiallyValidated",
        "promotionAllowed",
    ):
        if document.get(field) is not False:
            raise ValueError(
                f"SBC timing profile admission T0 {field} must remain false"
            )

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "candidateContract": "SBC_DIRECTIONAL_TIMING_PROFILE_V1",
        "admissionContract": "SBC_TIMING_PROFILE_ADMISSION_REPORT_V1",
        "registryContract": "SBC_TIMING_PROFILE_REGISTRY_V1",
        "schemaVersion": 1,
        "admissionPolicy": "FAIL_CLOSED_SOURCE_REGISTRY_ADMISSION_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(
                f"SBC timing profile admission T0 {field} differs from {expected}"
            )
    for field in (
        "modulePath",
        "testPath",
        "registryPath",
        "servicePath",
        "serviceTestPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(
                f"SBC timing profile admission T0 evidence is missing: {path}"
            )
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC timing profile admission T0 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError(
            "SBC timing profile admission T0 module hash differs from the audit"
        )

    registry_path = project_root / implementation["registryPath"]
    registry = _load(registry_path)
    if registry.get("contract") != implementation["registryContract"]:
        raise ValueError("SBC timing profile admission T0 registry contract drifted")
    validate_timing_profile_registry(registry)

    expected_admission = {
        "applicationSuppliesCandidate": False,
        "candidateValidatedInMemoryOnly": True,
        "candidatePersisted": False,
        "canonicalCandidateSha256": True,
        "structuralValidityIsAdmission": False,
        "serverRegistryRequired": True,
        "clientCanWriteRegistry": False,
        "typedGateStates": ["PASS", "FAIL", "UNKNOWN"],
        "noCandidateState": "NO_PROFILE_LOADED",
        "unregisteredCompleteState": "STRUCTURALLY_COMPLETE_UNREGISTERED",
        "repositoryProfileCount": len(registry["profiles"]),
    }
    if (document.get("admission") or {}) != expected_admission:
        raise ValueError("SBC timing profile admission T0 admission contract drifted")
    if registry["profiles"]:
        raise ValueError(
            "SBC timing profile admission T0 repository registry must remain empty"
        )

    expected_domains = [
        "HASH_PINNED_SOURCE_EVIDENCE",
        "FINITE_PHASE_SPAN",
        "GAP_FREE_HALF_OPEN_SECTORS",
        "SAFE_UNSAFE_DIRECTION_ROLES",
        "BOUNDARY_MARGIN_AND_INCLUSIVITY",
        "ASYMMETRY_POLICY",
        "REPEATED_EXACT_EVENT_POLICY",
        "RETROGRADE_LOOP_POLICY",
        "STATION_POLICY_BY_BODY",
        "MISSING_BOUNDARY_POLICY",
        "UNSUPPORTED_STATE_POLICY",
        "ACTIVITY_COHERENCE_UNSAFE_SHARE_COVERAGE_THRESHOLDS",
        "ONE_CONFIDENCE_EQUATION",
        "RESEARCH_AND_EXECUTION_LOCKS",
    ]
    if document.get("requiredDomains") != expected_domains:
        raise ValueError("SBC timing profile admission T0 required domains drifted")

    expected_separation = {
        "profileStructuralCompletenessSeparate": True,
        "sourceRegistryAdmissionSeparate": True,
        "directionalEngineImplementationSeparate": True,
        "prospectiveFinancialValidationSeparate": True,
        "executionPermissionSeparate": True,
        "directionalEngineImplemented": False,
        "directionalOutputAvailable": False,
        "financialUseAllowed": False,
    }
    if (document.get("separation") or {}) != expected_separation:
        raise ValueError("SBC timing profile admission T0 separation contract drifted")

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "serverOwnsRegistry": True,
        "readOnlyRuntimeRequired": True,
        "candidateUploadPersists": False,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError("SBC timing profile admission T0 transport contract drifted")

    guardrails = document.get("guardrails") or {}
    for field in ("researchOnly", "readOnly"):
        if guardrails.get(field) is not True:
            raise ValueError(
                f"SBC timing profile admission T0 guardrail {field} must remain true"
            )
    for field in (
        "profileValuesSuppliedByApplication",
        "timingPhaseCalculated",
        "directionalPhaseCalculated",
        "confidenceCalculated",
        "countsAsIndependentVote",
        "autoSuggestIncluded",
        "liveInferenceIncluded",
        "officialMlNotesIncluded",
        "shadowVoteIncluded",
        "tradeOutputIncluded",
        "financiallyValidated",
        "executionAllowed",
    ):
        if guardrails.get(field) is not False:
            raise ValueError(
                f"SBC timing profile admission T0 guardrail {field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC timing profile admission T0 directional contribution must remain zero"
        )
    expected_blocked = [
        "DIRECTIONAL_TIMING_PHASE",
        "TIMING_CONFIDENCE",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    ]
    if guardrails.get("blockedCapabilities") != expected_blocked:
        raise ValueError(
            "SBC timing profile admission T0 blockedCapabilities drifted"
        )

    expected_verification = {
        "newTimingProfileAdmissionTests": "8_passed",
        "chakraServiceTests": "13_passed",
        "chakraAuditWorkspaceTests": "5_passed",
        "frontendTests": "97_passed",
        "statusValidation": "28_passed",
        "repositoryPythonTests": "477_passed",
        "pythonRuff": "changed_scope_passed",
        "repositoryWidePythonRuff": "blocked_by_19_out_of_scope_findings",
        "frontendLint": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustCheck": "passed",
        "browserVisualAcceptance": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError(
            "SBC timing profile admission T0 verification evidence is incomplete"
        )


def validate_sbc_timing_profile_source_packet_s1_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC timing profile source packet S1 auditedAtUtc",
    )
    _execution_locked(document, "SBC timing profile source packet S1")
    if (
        document.get("capabilityId")
        != "timing_profile_source_packet_readiness_v1"
    ):
        raise ValueError(
            "SBC timing profile source packet S1 has an unexpected capability"
        )
    if document.get("status") != "implemented_in_source_no_packet":
        raise ValueError(
            "SBC timing profile source packet S1 has an unexpected status"
        )
    for field in (
        "packagedCandidate",
        "packagedPacket",
        "externalReviewCompleted",
        "sourceCertified",
        "profileRegistered",
        "directionalEngineImplemented",
        "financiallyValidated",
        "promotionAllowed",
    ):
        if document.get(field) is not False:
            raise ValueError(
                f"SBC timing profile source packet S1 {field} must remain false"
            )

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "candidateContract": "SBC_DIRECTIONAL_TIMING_PROFILE_V1",
        "packetContract": "SBC_TIMING_PROFILE_SOURCE_PACKET_V1",
        "readinessContract": "SBC_TIMING_PROFILE_SOURCE_READINESS_REPORT_V1",
        "schemaVersion": 1,
        "readinessPolicy": "CLAIM_HASH_AND_INDEPENDENT_LINEAGE_READINESS_V1",
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(
                "SBC timing profile source packet S1 "
                f"{field} differs from {expected}"
            )
    for field in (
        "modulePath",
        "testPath",
        "profileGatePath",
        "registryPath",
        "servicePath",
        "serviceTestPath",
        "nativePath",
        "apiPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(
                "SBC timing profile source packet S1 evidence is missing: "
                f"{path}"
            )
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC timing profile source packet S1 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError(
            "SBC timing profile source packet S1 module hash differs from the audit"
        )

    registry = _load(project_root / implementation["registryPath"])
    validate_timing_profile_registry(registry)
    if registry["profiles"]:
        raise ValueError(
            "SBC timing profile source packet S1 registry must remain empty"
        )

    expected_readiness = {
        "applicationSuppliesCandidate": False,
        "applicationSuppliesPacket": False,
        "evaluatedInMemoryOnly": True,
        "candidatePersisted": False,
        "packetPersisted": False,
        "exactCandidateProfileHashRequired": True,
        "exactCandidateSubtreeHashRequired": True,
        "candidateSourceEvidenceHashLinkRequired": True,
        "pageCitationsRequired": True,
        "excerptSha256Required": True,
        "sourceBytesVerifiedByApplication": False,
        "doctrinePrimaryClaimRequired": True,
        "doctrineIndependentWitnessRequired": True,
        "minimumDoctrineLineages": 2,
        "researchSpecificationRequired": True,
        "unresolvedConflictAllowed": False,
        "externalReviewerRequired": True,
        "externalReviewerIndependence": "EXTERNAL_TO_PROFILE_AUTHOR",
        "typedGateStates": ["PASS", "FAIL", "UNKNOWN"],
        "noPacketState": "NO_PACKET_LOADED",
        "passingState": "READY_FOR_EXTERNAL_REVIEW",
        "passingStateMeans": "READY_FOR_EXTERNAL_REVIEW_ONLY",
    }
    if (document.get("packetReadiness") or {}) != expected_readiness:
        raise ValueError(
            "SBC timing profile source packet S1 readiness contract drifted"
        )

    expected_domains = {
        "doctrine": [
            "/phaseSpan",
            "/sectors",
            "/boundaryPolicy",
            "/asymmetryPolicy",
            "/repeatedExactEventPolicy",
            "/retrogradeLoopPolicy",
            "/stationPolicy",
            "/missingBoundaryPolicy",
            "/unsupportedStatePolicy",
        ],
        "researchProtocol": [
            "/eligibilityPolicy",
            "/confidencePolicy",
        ],
    }
    if (document.get("requiredClaimDomains") or {}) != expected_domains:
        raise ValueError(
            "SBC timing profile source packet S1 claim domains drifted"
        )

    expected_separation = {
        "candidateStructuralCompletenessSeparate": True,
        "packetReadinessSeparate": True,
        "sourceByteVerificationSeparate": True,
        "externalReviewSeparate": True,
        "sourceCertificationSeparate": True,
        "profileRegistryAdmissionSeparate": True,
        "directionalEngineImplementationSeparate": True,
        "prospectiveFinancialValidationSeparate": True,
        "executionPermissionSeparate": True,
        "externalReviewCompleted": False,
        "sourceCertified": False,
        "profileRegistered": False,
        "directionalEngineImplemented": False,
        "directionalOutputAvailable": False,
        "financialUseAllowed": False,
    }
    if (document.get("separation") or {}) != expected_separation:
        raise ValueError(
            "SBC timing profile source packet S1 separation contract drifted"
        )

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "readOnlyRuntimeRequired": True,
        "candidateUploadPersists": False,
        "packetUploadPersists": False,
        "clientCanWriteRegistry": False,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError(
            "SBC timing profile source packet S1 transport contract drifted"
        )

    guardrails = document.get("guardrails") or {}
    for field in ("researchOnly", "readOnly"):
        if guardrails.get(field) is not True:
            raise ValueError(
                "SBC timing profile source packet S1 guardrail "
                f"{field} must remain true"
            )
    for field in (
        "sourceBytesVerifiedByApplication",
        "externalReviewCompleted",
        "sourceCertified",
        "profileRegistrationAllowed",
        "timingPhaseCalculated",
        "directionalPhaseCalculated",
        "confidenceCalculated",
        "countsAsIndependentVote",
        "autoSuggestIncluded",
        "liveInferenceIncluded",
        "officialMlNotesIncluded",
        "shadowVoteIncluded",
        "tradeOutputIncluded",
        "financiallyValidated",
        "executionAllowed",
    ):
        if guardrails.get(field) is not False:
            raise ValueError(
                "SBC timing profile source packet S1 guardrail "
                f"{field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC timing profile source packet S1 directional contribution "
            "must remain zero"
        )
    expected_blocked = [
        "SOURCE_CERTIFICATION",
        "TIMING_PROFILE_REGISTRATION",
        "DIRECTIONAL_TIMING_PHASE",
        "TIMING_CONFIDENCE",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    ]
    if guardrails.get("blockedCapabilities") != expected_blocked:
        raise ValueError(
            "SBC timing profile source packet S1 blockedCapabilities drifted"
        )

    expected_verification = {
        "newTimingProfileSourcePacketTests": "9_passed",
        "chakraServiceTests": "15_passed",
        "chakraAuditWorkspaceTests": "6_passed",
        "frontendTests": "98_passed",
        "statusValidation": "32_passed",
        "repositoryPythonTests": "492_passed",
        "pythonRuff": "changed_scope_passed",
        "repositoryWidePythonRuff": "blocked_by_19_out_of_scope_findings",
        "frontendLint": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustCheck": "passed",
        "browserVisualAcceptance": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError(
            "SBC timing profile source packet S1 verification evidence is incomplete"
        )


def validate_sbc_timing_profile_source_verification_s2_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    _utc_timestamp(
        document.get("auditedAtUtc"),
        "SBC timing profile source verification S2 auditedAtUtc",
    )
    _execution_locked(document, "SBC timing profile source verification S2")
    if document.get("capabilityId") != "timing_profile_source_verification_v1":
        raise ValueError(
            "SBC timing profile source verification S2 has an unexpected capability"
        )
    if document.get("status") != "implemented_in_source_no_verified_bundle":
        raise ValueError(
            "SBC timing profile source verification S2 has an unexpected status"
        )
    for field in (
        "packagedCandidate",
        "packagedPacket",
        "packagedReviewBundle",
        "externalReviewCompleted",
        "sourceCertified",
        "profileRegistered",
        "directionalEngineImplemented",
        "financiallyValidated",
        "promotionAllowed",
    ):
        if document.get(field) is not False:
            raise ValueError(
                "SBC timing profile source verification S2 "
                f"{field} must remain false"
            )

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "reportContract": (
            "SBC_TIMING_PROFILE_SOURCE_BYTE_VERIFICATION_REPORT_V1"
        ),
        "bundleContract": "SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1",
        "attestationContract": (
            "SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1"
        ),
        "schemaVersion": 1,
        "verificationPolicy": (
            "EXACT_SOURCE_BYTES_AND_UTF8_EXCERPT_PAYLOADS_V1"
        ),
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(
                "SBC timing profile source verification S2 "
                f"{field} differs from {expected}"
            )
    for field in (
        "modulePath",
        "testPath",
        "sourcePacketGatePath",
        "registryPath",
        "servicePath",
        "serviceTestPath",
        "serverPath",
        "nativePath",
        "apiPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(
                "SBC timing profile source verification S2 evidence is missing: "
                f"{path}"
            )
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        "SBC timing profile source verification S2 module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError(
            "SBC timing profile source verification S2 module hash "
            "differs from the audit"
        )

    registry = _load(project_root / implementation["registryPath"])
    validate_timing_profile_registry(registry)
    if registry["profiles"]:
        raise ValueError(
            "SBC timing profile source verification S2 registry must remain empty"
        )

    expected_verification_policy = {
        "s1ReadinessRequired": True,
        "repositorySuppliesCandidate": False,
        "repositorySuppliesPacket": False,
        "repositorySuppliesSourceBytes": False,
        "repositorySuppliesExcerptPayloads": False,
        "runtimePayloadsInMemoryOnly": True,
        "sourcePayloadsPersisted": False,
        "excerptPayloadsPersisted": False,
        "exactIdentifierSetsRequired": True,
        "sourceHashMethod": "SHA256_EXACT_SUPPLIED_BYTES",
        "excerptHashMethod": "SHA256_EXACT_UTF8_NO_NORMALIZATION",
        "sourceMaxBytes": 64 * 1024 * 1024,
        "sourceCombinedMaxBytes": 192 * 1024 * 1024,
        "excerptMaxUtf8Bytes": 256 * 1024,
        "excerptCombinedMaxUtf8Bytes": 8 * 1024 * 1024,
        "typedGateStates": ["PASS", "FAIL", "UNKNOWN"],
        "noPayloadState": "NO_VERIFICATION_PAYLOAD",
        "failureState": "SOURCE_VERIFICATION_FAILED",
        "passingState": "READY_FOR_INDEPENDENT_REVIEW",
        "passingStateMeans": "READY_FOR_INDEPENDENT_REVIEW_ONLY",
    }
    if (document.get("sourceVerification") or {}) != expected_verification_policy:
        raise ValueError(
            "SBC timing profile source verification S2 verification policy drifted"
        )

    expected_bundle = {
        "contract": "SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1",
        "attestationContract": (
            "SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1"
        ),
        "schemaVersion": 1,
        "hashMethod": (
            "CANONICAL_JSON_SHA256_WITH_ATTESTATION_BUNDLE_HASH_BLANK"
        ),
        "hashFunction": "independent_review_bundle_hash",
        "includesCandidate": True,
        "includesSourcePacket": True,
        "includesVerificationRows": True,
        "includesReviewInstructions": True,
        "includesPendingAttestationTemplate": True,
        "includesSourceBytes": False,
        "includesExcerptText": False,
        "attestationDecision": "PENDING",
        "attestationRegistryWriteAllowed": False,
        "reviewerIndependence": "EXTERNAL_TO_PROFILE_AUTHOR",
        "pagePresenceChecked": False,
        "doctrineCorrectnessChecked": False,
        "externalReviewCompleted": False,
        "sourceCertified": False,
        "profileRegistrationAllowed": False,
    }
    if (document.get("reviewBundle") or {}) != expected_bundle:
        raise ValueError(
            "SBC timing profile source verification S2 review bundle drifted"
        )

    expected_separation = {
        "candidateStructuralCompletenessSeparate": True,
        "packetReadinessSeparate": True,
        "sourceByteVerificationSeparate": True,
        "pageCitationVerificationSeparate": True,
        "doctrineCorrectnessReviewSeparate": True,
        "externalReviewSeparate": True,
        "sourceCertificationSeparate": True,
        "profileRegistryAdmissionSeparate": True,
        "directionalEngineImplementationSeparate": True,
        "prospectiveFinancialValidationSeparate": True,
        "executionPermissionSeparate": True,
        "pagePresenceChecked": False,
        "doctrineCorrectnessChecked": False,
        "externalReviewCompleted": False,
        "sourceCertified": False,
        "profileRegistered": False,
        "directionalEngineImplemented": False,
        "directionalOutputAvailable": False,
        "financialUseAllowed": False,
    }
    if (document.get("separation") or {}) != expected_separation:
        raise ValueError(
            "SBC timing profile source verification S2 separation contract drifted"
        )

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "route": "/api/chakra-lab/timing-profile/source-packet/verify-bytes",
        "nativeCommand": "chakra_lab_timing_source_verification",
        "readOnlyRuntimeRequired": True,
        "clientSuppliesBase64Only": True,
        "arbitraryClientPathsAccepted": False,
        "payloadPersistenceAllowed": False,
        "clientCanWriteRegistry": False,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError(
            "SBC timing profile source verification S2 transport contract drifted"
        )

    guardrails = document.get("guardrails") or {}
    for field in ("researchOnly", "readOnly"):
        if guardrails.get(field) is not True:
            raise ValueError(
                "SBC timing profile source verification S2 guardrail "
                f"{field} must remain true"
            )
    for field in (
        "sourceBytesIncludedInBundle",
        "excerptTextIncludedInBundle",
        "pagePresenceChecked",
        "doctrineCorrectnessChecked",
        "externalReviewCompleted",
        "sourceCertified",
        "profileRegistrationAllowed",
        "registryWriteAllowed",
        "timingPhaseCalculated",
        "directionalPhaseCalculated",
        "confidenceCalculated",
        "countsAsIndependentVote",
        "autoSuggestIncluded",
        "liveInferenceIncluded",
        "officialMlNotesIncluded",
        "shadowVoteIncluded",
        "tradeOutputIncluded",
        "financiallyValidated",
        "executionAllowed",
    ):
        if guardrails.get(field) is not False:
            raise ValueError(
                "SBC timing profile source verification S2 guardrail "
                f"{field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(
            "SBC timing profile source verification S2 directional contribution "
            "must remain zero"
        )
    expected_blocked = [
        "PAGE_CITATION_VERIFICATION",
        "DOCTRINE_CORRECTNESS_REVIEW",
        "SOURCE_CERTIFICATION",
        "TIMING_PROFILE_REGISTRATION",
        "DIRECTIONAL_TIMING_PHASE",
        "TIMING_CONFIDENCE",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    ]
    if guardrails.get("blockedCapabilities") != expected_blocked:
        raise ValueError(
            "SBC timing profile source verification S2 blockedCapabilities drifted"
        )

    expected_verification = {
        "newTimingProfileSourceVerificationTests": "9_passed",
        "chakraServiceTests": "18_passed",
        "chakraAuditWorkspaceTests": "7_passed",
        "frontendTests": "99_passed",
        "statusValidation": "36_passed",
        "repositoryPythonTests": "508_passed",
        "pythonRuff": "changed_scope_passed",
        "repositoryWidePythonRuff": "blocked_by_19_out_of_scope_findings",
        "frontendLint": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustFormat": "changed_scope_passed",
        "repositoryWideRustFormat": (
            "blocked_by_1_out_of_scope_formatting_diff"
        ),
        "nativeRustCheck": "passed",
        "backendEndpointAcceptance": "passed",
        "browserVisualAcceptance": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError(
            "SBC timing profile source verification S2 verification "
            "evidence is incomplete"
        )


def validate_sbc_timing_profile_external_review_s3_audit(
    document: dict[str, Any], project_root: Path
) -> None:
    label = "SBC timing profile external review S3"
    _utc_timestamp(document.get("auditedAtUtc"), f"{label} auditedAtUtc")
    _execution_locked(document, label)
    if (
        document.get("capabilityId")
        != "timing_profile_external_review_verification_v1"
    ):
        raise ValueError(f"{label} has an unexpected capability")
    if document.get("status") != "implemented_in_source_no_completed_attestation":
        raise ValueError(f"{label} has an unexpected status")
    for field in (
        "packagedReviewBundle",
        "packagedCompletedAttestation",
        "reviewerAuthenticated",
        "externalReviewIndependentlyProven",
        "sourceCertified",
        "profileRegistered",
        "directionalEngineImplemented",
        "financiallyValidated",
        "promotionAllowed",
    ):
        if document.get(field) is not False:
            raise ValueError(f"{label} {field} must remain false")

    implementation = document.get("implementation") or {}
    expected_contracts = {
        "reportContract": "SBC_TIMING_PROFILE_EXTERNAL_REVIEW_REPORT_V1",
        "bundleContract": "SBC_TIMING_PROFILE_INDEPENDENT_REVIEW_BUNDLE_V1",
        "attestationContract": (
            "SBC_TIMING_PROFILE_EXTERNAL_REVIEW_ATTESTATION_V1"
        ),
        "proposalContract": (
            "SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_PROPOSAL_V1"
        ),
        "schemaVersion": 1,
        "reviewPolicy": (
            "INTERNAL_COHERENCE_AND_EXACT_DECISION_COVERAGE_V1"
        ),
        "classification": "SOURCE_PROFILED_EXPERIMENTAL",
    }
    for field, expected in expected_contracts.items():
        if implementation.get(field) != expected:
            raise ValueError(f"{label} {field} differs from {expected}")
    for field in (
        "modulePath",
        "testPath",
        "sourceVerificationPath",
        "registryPath",
        "servicePath",
        "serviceTestPath",
        "serverPath",
        "nativePath",
        "apiPath",
        "uiPath",
        "uiTestPath",
        "acceptancePath",
        "milestonePath",
        "adrPath",
    ):
        path = project_root / _required_text(implementation.get(field), field)
        if not path.is_file():
            raise ValueError(f"{label} evidence is missing: {path}")
    module_path = project_root / implementation["modulePath"]
    expected_hash = _sha256(
        implementation.get("moduleCanonicalTextSha256"),
        f"{label} module canonical text",
    )
    if _canonical_text_sha256(module_path) != expected_hash:
        raise ValueError(f"{label} module hash differs from the audit")

    registry = _load(project_root / implementation["registryPath"])
    validate_timing_profile_registry(registry)
    if registry["profiles"]:
        raise ValueError(f"{label} registry must remain empty")

    expected_review = {
        "repositorySuppliesReviewBundle": False,
        "repositorySuppliesCompletedAttestation": False,
        "runtimePayloadsInMemoryOnly": True,
        "payloadsPersisted": False,
        "bundleDigestReproduced": True,
        "embeddedS1ReplayRequired": True,
        "embeddedS2RowsReconciled": True,
        "exactSourceDecisionCoverageRequired": True,
        "exactClaimDecisionCoverageRequired": True,
        "exactConflictDecisionCoverageRequired": True,
        "duplicateDecisionIdsRejected": True,
        "extraDecisionIdsRejected": True,
        "pendingDecisionsRejected": True,
        "decisionNotesRequired": True,
        "approvedRequiresAllPass": True,
        "rejectedRequiresAtLeastOneFail": True,
        "noAttestationState": "NO_ATTESTATION",
        "invalidState": "ATTESTATION_INVALID",
        "rejectedState": "REVIEW_REJECTED",
        "passingState": "READY_FOR_HUMAN_CERTIFICATION_DECISION",
        "passingStateMeans": "INTERNALLY_COHERENT_RECORD_ONLY",
    }
    if (document.get("externalReview") or {}) != expected_review:
        raise ValueError(f"{label} review contract drifted")

    expected_human_control = {
        "reviewerIdentityAuthenticated": False,
        "reviewerIndependenceAuthenticated": False,
        "externalReviewIndependentlyProven": False,
        "manualReviewerAuthenticationRequired": True,
        "manualCertificationDecisionRequired": True,
        "applicationMayEmitProposal": True,
        "applicationMayCertifySource": False,
        "applicationMayRegisterProfile": False,
        "applicationMayWriteRegistry": False,
        "proposalIsCertificate": False,
        "proposalIsRegistryAdmission": False,
    }
    if (document.get("humanControl") or {}) != expected_human_control:
        raise ValueError(f"{label} human-control contract drifted")

    expected_proposal = {
        "contract": "SBC_TIMING_PROFILE_SOURCE_CERTIFICATION_PROPOSAL_V1",
        "schemaVersion": 1,
        "hashMethod": "CANONICAL_JSON_SHA256_WITH_PROPOSAL_SHA256_BLANK",
        "emittedOnlyAfterApprovedCompleteAttestation": True,
        "includesSourceBytes": False,
        "includesExcerptText": False,
        "reviewerIdentityAuthenticated": False,
        "externalReviewIndependentlyProven": False,
        "sourceCertified": False,
        "profileRegistered": False,
        "registryWriteAllowed": False,
        "executionAllowed": False,
    }
    if (document.get("certificationProposal") or {}) != expected_proposal:
        raise ValueError(f"{label} certification proposal drifted")

    expected_separation = {
        "bundleIntegritySeparate": True,
        "reviewRecordCoherenceSeparate": True,
        "reviewerAuthenticationSeparate": True,
        "reviewerIndependenceAuthenticationSeparate": True,
        "sourceCertificationSeparate": True,
        "profileRegistryAdmissionSeparate": True,
        "directionalEngineImplementationSeparate": True,
        "prospectiveFinancialValidationSeparate": True,
        "executionPermissionSeparate": True,
        "reviewerIdentityAuthenticated": False,
        "externalReviewIndependentlyProven": False,
        "sourceCertified": False,
        "profileRegistered": False,
        "directionalEngineImplemented": False,
        "directionalOutputAvailable": False,
        "financialUseAllowed": False,
    }
    if (document.get("separation") or {}) != expected_separation:
        raise ValueError(f"{label} separation contract drifted")

    expected_transport = {
        "browserDevelopment": "private_http_post",
        "nativeDesktop": "tauri_ipc_private_sidecar",
        "route": "/api/chakra-lab/timing-profile/external-review/verify",
        "nativeCommand": "chakra_lab_timing_external_review",
        "readOnlyRuntimeRequired": True,
        "clientSuppliesJsonObjectsOnly": True,
        "arbitraryClientPathsAccepted": False,
        "payloadPersistenceAllowed": False,
        "clientCanWriteRegistry": False,
    }
    if (document.get("transport") or {}) != expected_transport:
        raise ValueError(f"{label} transport contract drifted")

    guardrails = document.get("guardrails") or {}
    for field in ("researchOnly", "readOnly"):
        if guardrails.get(field) is not True:
            raise ValueError(f"{label} guardrail {field} must remain true")
    for field in (
        "payloadsPersisted",
        "reviewerIdentityAuthenticated",
        "reviewerIndependenceAuthenticated",
        "externalReviewIndependentlyProven",
        "sourceCertified",
        "profileRegistered",
        "registryWriteAllowed",
        "timingPhaseCalculated",
        "directionalPhaseCalculated",
        "confidenceCalculated",
        "countsAsIndependentVote",
        "autoSuggestIncluded",
        "liveInferenceIncluded",
        "officialMlNotesIncluded",
        "shadowVoteIncluded",
        "tradeOutputIncluded",
        "financiallyValidated",
        "executionAllowed",
    ):
        if guardrails.get(field) is not False:
            raise ValueError(f"{label} guardrail {field} must remain false")
    if guardrails.get("directionalContribution") != 0:
        raise ValueError(f"{label} directional contribution must remain zero")
    expected_blocked = [
        "REVIEWER_IDENTITY_AUTHENTICATION",
        "REVIEWER_INDEPENDENCE_AUTHENTICATION",
        "SOURCE_CERTIFICATION",
        "TIMING_PROFILE_REGISTRATION",
        "DIRECTIONAL_TIMING_PHASE",
        "TIMING_CONFIDENCE",
        "AUTO_SUGGEST",
        "LIVE_INFERENCE",
        "OFFICIAL_ML_NOTES",
        "SHADOW_VOTE",
        "TRADE_OUTPUT",
        "MT5_EXECUTION",
    ]
    if guardrails.get("blockedCapabilities") != expected_blocked:
        raise ValueError(f"{label} blockedCapabilities drifted")

    expected_verification = {
        "newTimingProfileExternalReviewTests": "10_passed",
        "chakraServiceTests": "20_passed",
        "chakraAuditWorkspaceTests": "8_passed",
        "frontendTests": "100_passed",
        "statusValidation": "40_passed",
        "repositoryPythonTests": "524_passed",
        "pythonRuff": "changed_scope_passed",
        "repositoryWidePythonRuff": "blocked_by_19_out_of_scope_findings",
        "frontendLint": "passed",
        "frontendProductionBuild": "passed",
        "nativeRustFormat": "changed_scope_passed",
        "repositoryWideRustFormat": (
            "blocked_by_1_out_of_scope_formatting_diff"
        ),
        "nativeRustCheck": "passed",
        "backendEndpointAcceptance": "passed",
        "browserVisualAcceptance": "passed",
    }
    if (document.get("verification") or {}) != expected_verification:
        raise ValueError(f"{label} verification evidence is incomplete")


def validate_cross_document_links(
    documents: dict[str, dict[str, Any]], root: Path
) -> None:
    release = documents["release_status.json"]
    plan = documents["mobile_acceptance_plan.json"]
    selected = release["selectedAcceptancePair"]
    if selected["planId"] != plan["planId"]:
        raise ValueError("release status and mobile acceptance plan IDs differ")
    releases = {item["releaseId"]: item for item in release["releases"]}
    for side, release_key in (
        ("desktopCandidate", "desktopReleaseId"),
        ("mobileCandidate", "mobileReleaseId"),
    ):
        candidate = plan[side]
        selected_release = releases[selected[release_key]]
        for field in (
            "releaseId",
            "version",
            "artifactPath",
            "artifactSha256",
            "sourceGitCommit",
            "sourceGitDirty",
        ):
            if candidate.get(field) != selected_release.get(field):
                raise ValueError(f"{side} {field} differs from selected release")

    trials = documents["research_trials.json"]
    for trial in trials["trials"]:
        audit_ref = trial.get("latestAuditRef")
        if not audit_ref:
            continue
        audit_path = (root.parent / str(audit_ref)).resolve()
        audit = _load(audit_path)
        if audit.get("executionAllowed") is not False:
            raise ValueError(f"trial audit {audit_ref} enables execution")
        if (audit.get("manifest") or {}).get("trialId") != trial["trialId"]:
            raise ValueError(f"trial audit {audit_ref} belongs to another cohort")


def validate_all(root: Path = STATUS_ROOT) -> dict[str, Any]:
    documents: dict[str, dict[str, Any]] = {}
    for filename, contract in EXPECTED_CONTRACTS.items():
        document = _load(root / filename)
        if document.get("contract") != contract:
            raise ValueError(f"{filename} contract does not match {contract}")
        documents[filename] = document
    audits: dict[str, dict[str, Any]] = {}
    for filename, contract in CANONICAL_AUDITS.items():
        document = _load(root / filename)
        if document.get("contract") != contract:
            raise ValueError(f"{filename} contract does not match {contract}")
        audits[filename] = document
    validate_release(documents["release_status.json"])
    validate_capabilities(documents["capability_status.json"])
    validate_trials(documents["research_trials.json"])
    validate_sources(documents["source_certification.json"])
    validate_mobile_plan(documents["mobile_acceptance_plan.json"])
    validate_sbc_phase_p0_audit(
        audits["audits/sbc_phase_p0_gap_audit_20260728.json"], root.parent
    )
    validate_sbc_atomic_intervals_p1_audit(
        audits["audits/sbc_atomic_intervals_p1_20260728.json"], root.parent
    )
    validate_sbc_multidimensional_ledger_p2_audit(
        audits["audits/sbc_multidimensional_ledger_p2_20260728.json"],
        root.parent,
    )
    validate_sbc_linked_audit_views_p3_audit(
        audits["audits/sbc_linked_audit_views_p3_20260728.json"],
        root.parent,
    )
    validate_sbc_reproducible_audit_packages_p4_audit(
        audits["audits/sbc_reproducible_audit_packages_p4_20260728.json"],
        root.parent,
    )
    validate_sbc_signed_audit_catalogs_p5_audit(
        audits["audits/sbc_signed_audit_catalogs_p5_20260728.json"],
        root.parent,
    )
    validate_sbc_fixed_zero_pi_phasor_f3_audit(
        audits["audits/sbc_fixed_zero_pi_phasor_f3_20260729.json"],
        root.parent,
    )
    validate_timing_profile_registry(
        documents["timing_phase_profile_registry.json"]
    )
    validate_sbc_timing_profile_admission_t0_audit(
        audits["audits/sbc_timing_profile_admission_t0_20260729.json"],
        root.parent,
    )
    validate_sbc_timing_profile_source_packet_s1_audit(
        audits["audits/sbc_timing_profile_source_packet_s1_20260729.json"],
        root.parent,
    )
    validate_sbc_timing_profile_source_verification_s2_audit(
        audits[
            "audits/sbc_timing_profile_source_verification_s2_20260729.json"
        ],
        root.parent,
    )
    validate_sbc_timing_profile_external_review_s3_audit(
        audits[
            "audits/sbc_timing_profile_external_review_s3_20260729.json"
        ],
        root.parent,
    )
    validate_cross_document_links(documents, root)
    capability_ids = {
        item["capabilityId"]
        for item in documents["capability_status.json"]["capabilities"]
    }
    required_capabilities = {
        "multidimensional_sbc_atomic_intervals_v1",
        "multidimensional_sbc_ledger_v1",
        "sbc_linked_audit_views_v1",
        "sbc_reproducible_audit_packages_v1",
        "sbc_signed_audit_catalogs_v1",
        "fixed_zero_pi_scalar_phasor_visualization_v1",
        "timing_profile_admission_gate_v1",
        "timing_profile_source_packet_readiness_v1",
        "timing_profile_source_verification_v1",
        "timing_profile_external_review_verification_v1",
        "phase_interference_research_engine_v1",
    }
    if not required_capabilities <= capability_ids:
        raise ValueError("SBC phase P0 capability status entries are missing")
    capability_by_id = {
        item["capabilityId"]: item
        for item in documents["capability_status.json"]["capabilities"]
    }
    if (
        capability_by_id["multidimensional_sbc_atomic_intervals_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC atomic P1 capability is not registered as source-implemented"
        )
    if (
        capability_by_id["multidimensional_sbc_ledger_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC multidimensional P2 capability is not registered as source-implemented"
        )
    if (
        capability_by_id["sbc_linked_audit_views_v1"]["states"]["implementedInSource"]
        != "yes"
    ):
        raise ValueError(
            "SBC linked audit P3 capability is not registered as source-implemented"
        )
    if (
        capability_by_id["sbc_reproducible_audit_packages_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC reproducible audit P4 capability is not registered as source-implemented"
        )
    if (
        capability_by_id["sbc_signed_audit_catalogs_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC signed audit catalog P5 capability is not registered as source-implemented"
        )
    if (
        capability_by_id["fixed_zero_pi_scalar_phasor_visualization_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC fixed zero/pi phasor F3 capability is not registered as "
            "source-implemented"
        )
    if (
        capability_by_id["timing_profile_admission_gate_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC timing profile admission T0 capability is not registered as "
            "source-implemented"
        )
    if (
        capability_by_id["timing_profile_source_packet_readiness_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC timing profile source packet S1 capability is not registered as "
            "source-implemented"
        )
    if (
        capability_by_id["timing_profile_source_verification_v1"]["states"][
            "implementedInSource"
        ]
        != "yes"
    ):
        raise ValueError(
            "SBC timing profile source verification S2 capability is not "
            "registered as source-implemented"
        )
    if (
        capability_by_id["timing_profile_external_review_verification_v1"][
            "states"
        ]["implementedInSource"]
        != "yes"
    ):
        raise ValueError(
            "SBC timing profile external review S3 capability is not "
            "registered as source-implemented"
        )
    return {
        "contract": "GANN_PROJECT_STATUS_VALIDATION_V1",
        "valid": True,
        "documentCount": len(documents) + len(audits),
        "auditCount": len(audits),
        "executionAllowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate canonical Gann Astro status documents."
    )
    parser.add_argument("--root", type=Path, default=STATUS_ROOT)
    args = parser.parse_args()
    print(json.dumps(validate_all(args.root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
