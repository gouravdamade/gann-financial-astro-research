from __future__ import annotations

import argparse
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
    validate_release(documents["release_status.json"])
    validate_capabilities(documents["capability_status.json"])
    validate_trials(documents["research_trials.json"])
    validate_sources(documents["source_certification.json"])
    validate_mobile_plan(documents["mobile_acceptance_plan.json"])
    validate_cross_document_links(documents, root)
    return {
        "contract": "GANN_PROJECT_STATUS_VALIDATION_V1",
        "valid": True,
        "documentCount": len(documents),
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
