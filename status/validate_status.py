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


def _sha256(value: Any, label: str) -> None:
    if not re.fullmatch(r"[0-9A-F]{64}", str(value or "")):
        raise ValueError(f"{label} must be an uppercase SHA-256 digest")


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
    validate_cross_document_links(documents, root)
    capability_ids = {
        item["capabilityId"]
        for item in documents["capability_status.json"]["capabilities"]
    }
    required_capabilities = {
        "multidimensional_sbc_atomic_intervals_v1",
        "phase_interference_research_engine_v1",
    }
    if not required_capabilities <= capability_ids:
        raise ValueError("SBC phase P0 capability status entries are missing")
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
