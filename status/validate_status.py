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
            _sha256(item.get("installerSha256"), f"release {item['releaseId']} installer")
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
            raise ValueError(f"capability {item['capabilityId']} has an incomplete state matrix")
        if set(states.values()) - STATE_VALUES:
            raise ValueError(f"capability {item['capabilityId']} uses an unknown state value")
        if states["promotedStable"] == "yes" and states["packagedCandidate"] != "yes":
            raise ValueError(f"capability {item['capabilityId']} is stable but not packaged")
        if item.get("executionAllowed") is not False:
            raise ValueError(f"capability {item['capabilityId']} enables execution")


def validate_trials(document: dict[str, Any]) -> None:
    _utc_timestamp(document.get("asOfUtc"), "research trial status asOfUtc")
    _execution_locked(document, "research trial status")
    trials = list(document.get("trials") or [])
    _unique(trials, "trialId", "research trial status")
    for item in trials:
        if item.get("cohortMutable") is not False:
            raise ValueError(f"trial {item['trialId']} must fail closed against cohort mutation")
        financially_validated = item.get("financiallyValidated")
        if not isinstance(financially_validated, bool):
            raise ValueError(f"trial {item['trialId']} needs a boolean financiallyValidated")
        if financially_validated and (
            item.get("status") != "passed_financial_validation" or not item.get("frozen")
        ):
            raise ValueError(
                f"trial {item['trialId']} cannot claim financial validation without a frozen passed gate"
            )
        if item.get("executionAllowed") is not False:
            raise ValueError(f"trial {item['trialId']} enables execution")
        if item.get("status") == "frozen_collecting" and not item.get("frozen"):
            raise ValueError(f"trial {item['trialId']} collects without a frozen identity")


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
        raise ValueError("mobile acceptance plan cannot promote before evidence is complete")
    tests = list(document.get("tests") or [])
    _unique(tests, "testId", "mobile acceptance plan")
    expected = [f"MOB-{number:02d}" for number in range(1, 9)]
    if [item["testId"] for item in tests] != expected:
        raise ValueError("mobile acceptance plan must contain MOB-01 through MOB-08 in order")
    for side in ("desktopCandidate", "mobileCandidate"):
        _sha256(document.get(side, {}).get("artifactSha256"), f"{side} artifact")


def validate_sbc_phase_p0_audit(
    document: dict[str, Any], project_root: Path
) -> None:
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
                raise ValueError(f"SBC phase P0 tracked source is missing: {repository_path}")
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
        raise ValueError("SBC phase P0 audit must retain corrections P0-R1 through P0-R8")
    if any(not str(item.get("requiredBefore") or "") for item in corrections):
        raise ValueError("SBC phase P0 corrections must name their dependent milestone")

    adopted = list(document.get("adoptedCorrections") or [])
    if len(adopted) != len(set(adopted)) or any(not str(item) for item in adopted):
        raise ValueError("SBC phase P0 adopted corrections must be unique and non-empty")

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
        raise ValueError("SBC multidimensional P2 audit cannot claim financial validation")
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
        raise ValueError(
            "SBC multidimensional P2 verification evidence is incomplete"
        )


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
            raise ValueError(
                f"SBC linked audit P3 guardrail {field} must remain false"
            )
    if guardrails.get("directionalContribution") != 0:
        raise ValueError("SBC linked audit P3 directional contribution must remain zero")

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
        raise ValueError("SBC atomic P1 capability is not registered as source-implemented")
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
        capability_by_id["sbc_linked_audit_views_v1"]["states"][
            "implementedInSource"
        ]
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
    return {
        "contract": "GANN_PROJECT_STATUS_VALIDATION_V1",
        "valid": True,
        "documentCount": len(documents) + len(audits),
        "auditCount": len(audits),
        "executionAllowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate canonical Gann Astro status documents.")
    parser.add_argument("--root", type=Path, default=STATUS_ROOT)
    args = parser.parse_args()
    print(json.dumps(validate_all(args.root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
