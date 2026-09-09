"""Read-only, outcome-blind Founder Review freeze verifier.

This module is deliberately separate from the Founder Review export writer.
It reads an explicitly supplied immutable resource root and durable review
root, verifies the complete 24-row review and revision chains, and publishes a
new freeze bundle to an explicitly supplied output directory.  It never
writes to the review store or to repository resources.

The command is intended for a future real freeze only after the founder has
completed all 24 rows and central review authorizes the run.  Tests use only
synthetic resource and review stores.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

import founder_review_workbench as fr


FREEZE_SCHEMA_VERSION = "FOUNDER_POLARITY_REVIEW_FREEZE_V1"
FREEZE_TOOL_VERSION = "founder_review_freeze_v1_20260909"
FREEZE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SOURCE_IMPLEMENTATION_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
EVENT_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)

REQUIRED_EVENT_FIELDS = (
    "eventId",
    "eventHash",
    "sideIdentity",
    "exactUtc",
    "applyingStartUtc",
    "separatingEndUtc",
    "chartId",
    "chartHypothesisId",
    "instrumentIdentity",
    "transitBody",
    "natalTarget",
    "aspectType",
)

FREEZE_DECISIONS = tuple(fr.DECISIONS)
FREEZE_EVIDENCE_CLASSES = tuple(fr.EVIDENCE_CLASSIFICATIONS)
REQUIRED_REVIEW_GUARDRAILS_FALSE = (
    "automaticOrderPlacement",
    "catalogueEntryCreated",
    "executionAllowed",
    "llmRead",
    "marketDirectionInferred",
    "magnitudeConfigured",
    "modeOneAdmission",
    "polarityAssigned",
    "priceDataRead",
    "sbcRead",
    "waveRendered",
)
FORBIDDEN_EVENT_KEYS = {"price", "close", "return", "returns", "pnl", "outcome", "score", "magnitude"}


class FounderReviewFreezeError(ValueError):
    """Raised when a read-only freeze precondition fails closed."""


class FreezeOutputExistsError(FounderReviewFreezeError):
    """Raised when the requested append-only freeze destination exists."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except FileNotFoundError as exc:
        raise FounderReviewFreezeError(f"Required freeze input is missing: {path}") from exc


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FounderReviewFreezeError(f"Required {label} is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FounderReviewFreezeError(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(value, dict):
        raise FounderReviewFreezeError(f"{label} must be a JSON object: {path}")
    return value


def _write_fsync(path: Path, value: bytes) -> None:
    with path.open("wb") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _timestamp_key(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FounderReviewFreezeError(f"{label} must be non-blank text")
    return value.strip()


def _required_bool(document: Mapping[str, Any], names: tuple[str, ...], label: str) -> bool:
    for name in names:
        if name in document:
            value = document[name]
            if type(value) is not bool:
                raise FounderReviewFreezeError(f"Candidate manifest {name} must be Boolean")
            return value
    raise FounderReviewFreezeError(f"Candidate manifest {label} is missing")


def _read_candidate_manifest(path: Path) -> dict[str, str]:
    manifest = _read_json(path, "candidate release manifest")
    candidate_version = _require_text(manifest.get("candidateVersion"), "Candidate manifest candidateVersion")
    if "version" in manifest and manifest["version"] != candidate_version:
        raise FounderReviewFreezeError("Candidate manifest version and candidateVersion disagree")

    source_commit: Any = None
    for key in (
        "implementationSourceCommit",
        "sourceGitCommit",
        "source_git_commit",
        "sourceCommit",
    ):
        if key in manifest:
            source_commit = manifest[key]
            break
    source_commit = _require_text(source_commit, "Candidate manifest source implementation commit").lower()
    if not SOURCE_IMPLEMENTATION_COMMIT_PATTERN.fullmatch(source_commit):
        raise FounderReviewFreezeError("Candidate manifest source implementation commit must be a 40-character SHA-1")

    if _required_bool(manifest, ("sourceGitDirty", "source_git_dirty"), "sourceGitDirty") is not False:
        raise FounderReviewFreezeError("Candidate release manifest must declare sourceGitDirty=false")
    if _required_bool(manifest, ("executionAllowed",), "executionAllowed") is not False:
        raise FounderReviewFreezeError("Candidate release manifest must declare executionAllowed=false")

    return {
        "candidateVersion": candidate_version,
        "candidateReleaseManifestSha256": _sha256_file(path),
        "sourceImplementationCommit": source_commit,
    }


def _revision_file_paths(revision_dir: Path) -> dict[str, Path]:
    return {
        "packet": revision_dir / "reviewed_packet.json",
        "manifest": revision_dir / "manifest.json",
        "completeness": revision_dir / "completeness.json",
        "status": revision_dir / "status.json",
        "markdown": revision_dir / "reviewed.md",
    }


def _verify_revision(
    side_data: dict[str, Any],
    revision_dir: Path,
) -> dict[str, Any]:
    if revision_dir.is_symlink() or not revision_dir.is_dir():
        raise FounderReviewFreezeError(f"{side_data['sideIdentity']} revision directory is invalid: {revision_dir}")
    paths = _revision_file_paths(revision_dir)
    if revision_dir.resolve().parent != side_data["_revisions"].resolve():
        raise FounderReviewFreezeError(f"{side_data['sideIdentity']} revision directory escapes the review store")
    for path in paths.values():
        if not path.is_file():
            raise FounderReviewFreezeError(f"{side_data['sideIdentity']} revision is incomplete: {revision_dir}")

    packet = _read_json(paths["packet"], "reviewed packet")
    manifest = _read_json(paths["manifest"], "revision manifest")
    completeness = _read_json(paths["completeness"], "revision completeness report")
    status = _read_json(paths["status"], "revision status record")
    side = side_data["sideIdentity"]
    if packet.get("contract") != fr.REVIEWED_PACKET_CONTRACT or packet.get("schemaVersion") != fr.REVIEWED_PACKET_SCHEMA_VERSION:
        raise FounderReviewFreezeError(f"{side} reviewed packet contract/schema is invalid")
    if packet.get("sideIdentity") != side or packet.get("revisionId") != revision_dir.name:
        raise FounderReviewFreezeError(f"{side} reviewed packet revision identity is invalid")
    packet_bindings = (
        ("blankPacketSha256", side_data["blankPacketSha256"]),
        ("sourceBlankPacketSha256", side_data["blankPacketSha256"]),
        ("identityIntegrityManifestSha256", side_data["identityIntegrityManifestSha256"]),
        ("identityAuditContract", side_data["identityAuditContract"]),
        ("identityAuditVersion", side_data["identityAuditVersion"]),
        ("identityAuditSha256", side_data["identityAuditSha256"]),
        ("ephemerisVersion", side_data["ephemerisVersion"]),
        ("ephemerisVersionSourcePacketSha256", side_data["blankPacketSha256"]),
        ("instrumentIdentity", side_data["instrumentIdentity"]),
        ("chartId", side_data["chartId"]),
        ("chartHypothesisId", side_data["chartHypothesisId"]),
    )
    for field, expected in packet_bindings:
        if packet.get(field) != expected:
            raise FounderReviewFreezeError(f"{side} reviewed packet binding is invalid: {field}")
    if not isinstance(packet.get("revisionHash"), str) or not isinstance(packet.get("reviewedPacketHash"), str):
        raise FounderReviewFreezeError(f"{side} reviewed packet hashes are missing")
    try:
        fr._verify_packet_hash(packet)
        fr._verify_revision_hash(packet)
        rows = fr._validate_stored_rows(side_data, packet.get("rows"))
    except fr.FounderReviewIntegrityError as exc:
        raise FounderReviewFreezeError(str(exc)) from exc

    manifest_bindings = (
        ("contract", fr.REVISION_MANIFEST_CONTRACT),
        ("schemaVersion", fr.REVIEWED_PACKET_SCHEMA_VERSION),
        ("reviewStoreContract", fr.REVIEW_STORE_CONTRACT),
        ("revisionId", revision_dir.name),
        ("revisionHash", packet["revisionHash"]),
        ("previousRevisionHash", packet.get("previousRevisionHash")),
        ("reviewedPacketHash", packet["reviewedPacketHash"]),
        ("blankPacketFile", side_data["blankPacketFile"]),
        ("blankPacketSha256", side_data["blankPacketSha256"]),
        ("identityIntegrityManifestFile", side_data["identityIntegrityManifestFile"]),
        ("identityIntegrityManifestSha256", side_data["identityIntegrityManifestSha256"]),
        ("identityAuditContract", side_data["identityAuditContract"]),
        ("identityAuditVersion", side_data["identityAuditVersion"]),
        ("identityAuditSha256", side_data["identityAuditSha256"]),
    )
    for field, expected in manifest_bindings:
        if manifest.get(field) != expected:
            raise FounderReviewFreezeError(f"{side} revision manifest binding is invalid: {field}")
    packet_guardrails = packet.get("guardrails")
    if not isinstance(packet_guardrails, dict) or any(
        packet_guardrails.get(key) is not False for key in REQUIRED_REVIEW_GUARDRAILS_FALSE
    ):
        raise FounderReviewFreezeError(f"{side} reviewed packet guardrails are not fail-closed")
    if manifest.get("reviewedPacketSha256") != fr._sha256_file(paths["packet"]):
        raise FounderReviewFreezeError(f"{side} revision manifest packet file hash is invalid")
    if completeness.get("contract") != "FOUNDER_REVIEW_COMPLETENESS_REPORT_V1" or completeness.get("reviewStoreContract") != fr.REVIEW_STORE_CONTRACT or completeness.get("sideIdentity") != side:
        raise FounderReviewFreezeError(f"{side} completeness report contract is invalid")
    if completeness.get("revisionId") != revision_dir.name or completeness.get("revisionHash") != packet["revisionHash"]:
        raise FounderReviewFreezeError(f"{side} completeness report does not bind the revision")
    if status.get("contract") != "FOUNDER_REVIEW_PACKET_STATUS_V1" or status.get("reviewStoreContract") != fr.REVIEW_STORE_CONTRACT or status.get("sideIdentity") != side:
        raise FounderReviewFreezeError(f"{side} status record contract is invalid")
    if status.get("revisionId") != revision_dir.name or status.get("revisionHash") != packet["revisionHash"]:
        raise FounderReviewFreezeError(f"{side} status record does not bind the revision")
    expected_counts = fr._completeness(rows)
    if packet.get("completeness") != expected_counts:
        raise FounderReviewFreezeError(f"{side} stored completeness counts are invalid")
    if completeness.get("counts") != expected_counts or status.get("counts") != expected_counts:
        raise FounderReviewFreezeError(f"{side} revision side reports do not bind completeness")
    if not _is_utc_timestamp(packet.get("serverCreatedAtUtc")):
        raise FounderReviewFreezeError(f"{side} revision server timestamp is invalid")

    return {
        "revisionId": revision_dir.name,
        "revisionHash": packet["revisionHash"],
        "previousRevisionHash": packet.get("previousRevisionHash"),
        "packet": packet,
        "manifest": manifest,
        "rows": rows,
        "revisionDir": revision_dir,
    }


def _verify_revision_chain(
    side_data: dict[str, Any],
    review_root: Path,
) -> dict[str, Any]:
    side = side_data["sideIdentity"]
    revisions_root = review_root / "revisions" / side
    side_data["_revisions"] = revisions_root
    current_path = review_root / "current" / f"{side}.json"
    pointer = _read_json(current_path, f"{side} current revision pointer")
    if pointer.get("contract") != fr.CURRENT_POINTER_CONTRACT or pointer.get("sideIdentity") != side:
        raise FounderReviewFreezeError(f"{side} current revision pointer is invalid")
    revision_id = pointer.get("revisionId")
    revision_hash = pointer.get("revisionHash")
    if not isinstance(revision_id, str) or not isinstance(revision_hash, str):
        raise FounderReviewFreezeError(f"{side} current revision pointer lacks revision identity")
    revision_dir = revisions_root / revision_id
    if revision_dir.resolve().parent != revisions_root.resolve():
        raise FounderReviewFreezeError(f"{side} current revision pointer escapes the review store")
    if not revisions_root.is_dir():
        raise FounderReviewFreezeError(f"{side} revision chain is missing")

    records_by_hash: dict[str, dict[str, Any]] = {}
    records_by_id: dict[str, dict[str, Any]] = {}
    children = list(revisions_root.iterdir())
    if not children:
        raise FounderReviewFreezeError(f"{side} revision chain is empty")
    for child in children:
        if child.name.startswith("."):
            raise FounderReviewFreezeError(f"{side} revision chain contains an unpublished staging directory")
        record = _verify_revision(side_data, child)
        if record["revisionId"] in records_by_id or record["revisionHash"] in records_by_hash:
            raise FounderReviewFreezeError(f"{side} revision chain contains a duplicate identity")
        records_by_id[record["revisionId"]] = record
        records_by_hash[record["revisionHash"]] = record

    current = records_by_id.get(revision_id)
    if current is None or current["revisionHash"] != revision_hash:
        raise FounderReviewFreezeError(f"{side} current pointer does not resolve to its authoritative revision")
    if pointer.get("previousRevisionHash") != current["previousRevisionHash"]:
        raise FounderReviewFreezeError(f"{side} current pointer parent binding is invalid")
    if pointer.get("reviewedPacketHash") != current["packet"].get("reviewedPacketHash"):
        raise FounderReviewFreezeError(f"{side} current pointer packet binding is invalid")

    chain: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursor = current
    while True:
        if cursor["revisionHash"] in seen:
            raise FounderReviewFreezeError(f"{side} revision chain contains a cycle")
        seen.add(cursor["revisionHash"])
        chain.append(cursor)
        parent_hash = cursor["previousRevisionHash"]
        if parent_hash is None:
            break
        if not isinstance(parent_hash, str) or parent_hash not in records_by_hash:
            raise FounderReviewFreezeError(f"{side} revision chain has a missing parent revision")
        cursor = records_by_hash[parent_hash]

    return {"pointer": pointer, "current": current, "chain": chain}


def _verify_current_rows(side_data: dict[str, Any], current: dict[str, Any]) -> list[dict[str, Any]]:
    side = side_data["sideIdentity"]
    rows = current["rows"]
    if len(rows) != 12:
        raise FounderReviewFreezeError(f"{side} must contain exactly 12 current review rows")
    if any(row.get("eligible") is not True or row.get("identityStatus") != fr.REVIEWABLE_IDENTITY_STATUS for row in rows):
        raise FounderReviewFreezeError(f"{side} contains an ineligible or non-SINGLE_PASS_VERIFIED current row")

    for row in rows:
        event = row.get("eventIdentity")
        if not isinstance(event, dict):
            raise FounderReviewFreezeError(f"{side} contains a row without immutable event identity")
        for field in REQUIRED_EVENT_FIELDS:
            if not isinstance(event.get(field), str) or not event[field].strip():
                raise FounderReviewFreezeError(f"{side} event {event.get('eventId', '<unknown>')} lacks exact {field}")
        if FORBIDDEN_EVENT_KEYS.intersection(key.lower() for key in event):
            raise FounderReviewFreezeError(f"{side} event {event['eventId']} contains forbidden market/outcome content")
        if event["sideIdentity"] != side or not EVENT_HASH_PATTERN.fullmatch(event["eventHash"]):
            raise FounderReviewFreezeError(f"{side} event identity binding is invalid: {event.get('eventId')}")
        for field in ("exactUtc", "applyingStartUtc", "separatingEndUtc"):
            if not _is_utc_timestamp(event[field]):
                raise FounderReviewFreezeError(f"{side} event {event['eventId']} has invalid {field}")
        checks = row.get("identityChecks")
        required_checks = (
            "eventIdMatchesAudit",
            "eventHashMatchesAudit",
            "blankPacketHashMatchesManifest",
            "listedAsVerified",
            "auditChecksPass",
            "identityAuditContractMatches",
            "identityAuditVersionMatches",
            "identityAuditHashMatches",
            "identityManifestBindsAudit",
            "eventCompilerMetadataPresent",
        )
        if not isinstance(checks, dict) or any(type(checks.get(key)) is not bool or checks[key] is not True for key in required_checks):
            raise FounderReviewFreezeError(f"{side} event {event['eventId']} identity checks are not all true")
        review = row.get("founderReview")
        if not isinstance(review, dict) or review.get("reviewedPolarity") is None:
            raise FounderReviewFreezeError(f"{side} event {event['eventId']} has no explicit founder decision")
        try:
            fr._normalize_review_input(review, event["eventId"])
            fr._validate_review_types(review, event["eventId"])
        except fr.FounderReviewIntegrityError as exc:
            raise FounderReviewFreezeError(str(exc)) from exc
        for field in ("firstReviewedAtUtc", "lastModifiedAtUtc", "reviewTimestampUtc"):
            if not _is_utc_timestamp(review.get(field)):
                raise FounderReviewFreezeError(f"{side} event {event['eventId']} lacks server review chronology: {field}")

    return rows


def _normalize_freeze_row(row: dict[str, Any]) -> dict[str, Any]:
    review = row["founderReview"]
    return {
        "sideIdentity": row["eventIdentity"]["sideIdentity"],
        "identityStatus": row["identityStatus"],
        "identityChecks": copy.deepcopy(row["identityChecks"]),
        "eventIdentity": copy.deepcopy(row["eventIdentity"]),
        "founderReview": {
            key: copy.deepcopy(review.get(key))
            for key in (
                "evidenceClassification",
                "founderReasoning",
                "firstReviewedAtUtc",
                "lastModifiedAtUtc",
                "rejectionReason",
                "reviewTimestampUtc",
                "reviewedPolarity",
                "reviewer",
                "sourceReferences",
            )
        },
    }


def _review_counts(rows: list[dict[str, Any]]) -> tuple[dict[str, int], dict[str, int]]:
    decisions = {decision: 0 for decision in FREEZE_DECISIONS}
    evidence = {classification: 0 for classification in FREEZE_EVIDENCE_CLASSES}
    evidence["REJECTED_NO_CLASSIFICATION"] = 0
    for row in rows:
        review = row["founderReview"]
        decision = review["reviewedPolarity"]
        decisions[decision] += 1
        classification = review.get("evidenceClassification")
        if classification is None:
            evidence["REJECTED_NO_CLASSIFICATION"] += 1
        else:
            evidence[classification] += 1
    return decisions, evidence


def _side_hash_payload(
    side: str,
    side_data: dict[str, Any],
    revision: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "sideIdentity": side,
        "blankPacketSha256": side_data["blankPacketSha256"],
        "identityIntegrityManifestSha256": side_data["identityIntegrityManifestSha256"],
        "identityAuditSha256": side_data["identityAuditSha256"],
        "authoritativeRevisionId": revision["revisionId"],
        "authoritativeRevisionHash": revision["revisionHash"],
        "rows": copy.deepcopy(rows),
    }


def _render_markdown(document: Mapping[str, Any]) -> str:
    def cell(value: Any) -> str:
        return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Founder Polarity Review Freeze",
        "",
        "This immutable bundle records founder-entered, outcome-blind review state only.",
        "It is pending central review and does not authorize outcome analysis, catalogue admission, signed waves, or execution.",
        "",
        f"- Schema: `{document['schemaVersion']}`",
        f"- Freeze ID: `{document['freezeId']}`",
        f"- Server created: `{document['serverCreatedAtUtc']}`",
        f"- Founder: `{document['founder']}`",
        f"- Candidate: `{document['candidateVersion']}`",
        f"- Candidate release-manifest SHA-256: `{document['candidateReleaseManifestSha256']}`",
        f"- Source implementation commit: `{document['sourceImplementationCommit']}`",
        f"- First reviewed: `{document['firstReviewedAtUtc']}`",
        f"- Last modified: `{document['lastReviewedAtUtc']}`",
        "",
        "## State",
        "",
    ]
    for key, value in document["state"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Frozen hashes",
            "",
            f"- USD: `{document['freezeHashes']['usdFrozenReviewHash']}`",
            f"- JPY: `{document['freezeHashes']['jpyFrozenReviewHash']}`",
            f"- Combined: `{document['freezeHashes']['combinedFounderReviewFreezeHash']}`",
            "",
            "## Attestation",
            "",
            f"- Type: `{document['attestation']['type']}`",
            f"- Founder: `{document['attestation']['founder']}`",
            f"- System proven: `{document['attestation']['systemProven']}`",
            f"- Text: {cell(document['attestation']['text'])}",
            "",
            "## Review rows",
            "",
            "| Side | Event ID | Event hash | Identity | Decision | Evidence | First reviewed | Last modified | Reason / rejection | Source references |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in document["reviewRows"]:
        event = row["eventIdentity"]
        review = row["founderReview"]
        refs = "; ".join(
            f"{ref.get('sourceId', '')} {ref.get('edition', '')} {ref.get('locator', '')}: {ref.get('connection', '')}"
            for ref in review.get("sourceReferences", [])
        )
        reason = review.get("founderReasoning") or review.get("rejectionReason") or ""
        lines.append(
            "| "
            + " | ".join(
                cell(value)
                for value in (
                    row["sideIdentity"],
                    event.get("eventId"),
                    event.get("eventHash"),
                    row["identityStatus"],
                    review.get("reviewedPolarity"),
                    review.get("evidenceClassification"),
                    review.get("firstReviewedAtUtc"),
                    review.get("lastModifiedAtUtc"),
                    reason,
                    refs,
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "All product and execution guardrails are fail-closed. The freeze is a record, not an admission or analysis step.",
            "",
        ]
    )
    for key, value in document["guardrails"].items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"


def _build_freeze_document(
    *,
    founder_name: str,
    candidate: dict[str, str],
    freeze_id: str,
    server_created_at_utc: str,
    side_records: dict[str, dict[str, Any]],
    review_rows: list[dict[str, Any]],
    attestation_text: str,
) -> dict[str, Any]:
    decision_counts, evidence_counts = _review_counts(review_rows)
    first_reviewed = min(
        (row["founderReview"]["firstReviewedAtUtc"] for row in review_rows),
        key=_timestamp_key,
    )
    last_modified = max(
        (row["founderReview"]["lastModifiedAtUtc"] for row in review_rows),
        key=_timestamp_key,
    )

    source_packets = {
        side: {
            "blankPacketSha256": record["sideData"]["blankPacketSha256"],
            "identityIntegrityManifestSha256": record["sideData"]["identityIntegrityManifestSha256"],
            "identityAuditSha256": record["sideData"]["identityAuditSha256"],
        }
        for side, record in side_records.items()
    }
    authoritative_revisions = {
        side: {
            "revisionId": record["current"]["revisionId"],
            "revisionHash": record["current"]["revisionHash"],
            "previousRevisionHash": record["current"]["previousRevisionHash"],
            "chainLength": len(record["chain"]),
        }
        for side, record in side_records.items()
    }
    state = {
        "FOUNDER_POLARITY_REVIEW": "FROZEN_PENDING_CENTRAL_REVIEW",
        "OUTCOME_ANALYSIS": "NOT_STARTED",
        "ANALYSIS_PROTOCOL": "NOT_PREREGISTERED",
        "PRODUCTION_POLARITY_ADMISSION": "NOT_STARTED",
        "SIGNED_USD_WAVE": "NOT_AUTHORIZED",
        "SIGNED_JPY_WAVE": "NOT_AUTHORIZED",
        "SIGNED_USDJPY_RESULTANT": "NOT_AUTHORIZED",
        "MAGNITUDE": "NOT_CONFIGURED",
        "executionAllowed": False,
    }
    guardrails = {
        "reviewStoreReadOnly": True,
        "blankPacketsReadOnly": True,
        "priceDataRead": False,
        "priceOutcomeRead": False,
        "sbcRead": False,
        "catalogueAdmission": False,
        "evidenceAdmission": False,
        "modeOneAdmission": False,
        "modeTwoAdmission": False,
        "autoSuggest": False,
        "llm": False,
        "ml": False,
        "marketDirectionInferred": False,
        "signedWaveRendered": False,
        "numericNormalization": False,
        "magnitudeConfigured": False,
        "executionAllowed": False,
    }
    attestation_for_hash = {
        "type": "HUMAN_OUTCOME_BLIND_ATTESTATION",
        "founder": founder_name,
        "text": attestation_text,
        "systemProven": False,
    }

    side_hashes = {
        side: _sha256_bytes(
            _canonical_bytes(
                _side_hash_payload(
                    side,
                    record["sideData"],
                    record["current"],
                    [row for row in review_rows if row["sideIdentity"] == side],
                )
            )
        )
        for side, record in side_records.items()
    }
    hash_body = {
        "schemaVersion": FREEZE_SCHEMA_VERSION,
        "founder": founder_name,
        "candidateVersion": candidate["candidateVersion"],
        "candidateReleaseManifestSha256": candidate["candidateReleaseManifestSha256"],
        "sourceImplementationCommit": candidate["sourceImplementationCommit"],
        "sourcePackets": source_packets,
        "authoritativeRevisions": authoritative_revisions,
        "reviewRows": review_rows,
        "firstReviewedAtUtc": first_reviewed,
        "lastReviewedAtUtc": last_modified,
        "attestation": attestation_for_hash,
        "decisionCategoryCounts": decision_counts,
        "evidenceCategoryCounts": evidence_counts,
        "state": state,
        "guardrails": guardrails,
        "sideFrozenReviewHashes": side_hashes,
    }
    combined_hash = _sha256_bytes(_canonical_bytes(hash_body))

    document = {
        **hash_body,
        "toolVersion": FREEZE_TOOL_VERSION,
        "freezeId": freeze_id,
        "serverCreatedAtUtc": server_created_at_utc,
        "attestation": {
            **attestation_for_hash,
            "serverCreatedAtUtc": server_created_at_utc,
        },
        "freezeHashes": {
            "usdFrozenReviewHash": side_hashes["USD"],
            "jpyFrozenReviewHash": side_hashes["JPY"],
            "combinedFounderReviewFreezeHash": combined_hash,
        },
        "executionAllowed": False,
    }
    return document


def _publish_bundle(
    *,
    document: dict[str, Any],
    output_dir: Path,
    publish_hook: Callable[[], None] | None = None,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    freeze_id = document["freezeId"]
    final_dir = output_dir / freeze_id
    if final_dir.exists():
        raise FreezeOutputExistsError(f"Freeze destination already exists: {final_dir}")

    staged_dir = Path(tempfile.mkdtemp(prefix=f".{freeze_id}.", dir=str(output_dir)))
    json_name = "FOUNDER_POLARITY_REVIEW_FREEZE_V1.json"
    markdown_name = "FOUNDER_POLARITY_REVIEW_FREEZE_V1.md"
    sums_name = "SHA256SUMS.txt"
    try:
        json_bytes = _json_bytes(document)
        markdown_bytes = _render_markdown(document).encode("utf-8")
        sums = (
            f"{_sha256_bytes(json_bytes)}  {json_name}\n"
            f"{_sha256_bytes(markdown_bytes)}  {markdown_name}\n"
            f"{document['freezeHashes']['combinedFounderReviewFreezeHash']}  combined-founder-review-freeze\n"
        ).encode("ascii")
        _write_fsync(staged_dir / json_name, json_bytes)
        _write_fsync(staged_dir / markdown_name, markdown_bytes)
        _write_fsync(staged_dir / sums_name, sums)
        if publish_hook is not None:
            publish_hook()
        if final_dir.exists():
            raise FreezeOutputExistsError(f"Freeze destination appeared during publication: {final_dir}")
        # The staged directory is complete before this single publication step.
        os.rename(staged_dir, final_dir)
        staged_dir = Path()
    except Exception:
        if staged_dir and staged_dir.exists():
            shutil.rmtree(staged_dir, ignore_errors=True)
        raise

    return {
        "freeze": document,
        "bundlePath": str(final_dir),
        "files": {
            "json": str(final_dir / json_name),
            "markdown": str(final_dir / markdown_name),
            "sha256sums": str(final_dir / sums_name),
        },
        "fileSha256": {
            "json": _sha256_file(final_dir / json_name),
            "markdown": _sha256_file(final_dir / markdown_name),
            "sha256sums": _sha256_file(final_dir / sums_name),
        },
    }


def freeze_founder_review(
    *,
    resource_root: Path,
    review_root: Path,
    output_dir: Path,
    founder_name: str,
    candidate_release_manifest: Path,
    attestation_text: str,
    expected_audit_sha256: str = fr.IDENTITY_AUDIT_EXPECTED_SHA256,
    freeze_id: str | None = None,
    server_created_at_utc: str | None = None,
    publish_hook: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Verify and atomically publish one freeze without writing review input."""

    founder_name = _require_text(founder_name, "Founder name")
    attestation_text = _require_text(attestation_text, "Outcome-blind attestation")
    resource_root = Path(resource_root).resolve()
    review_root = Path(review_root).resolve()
    output_dir = Path(output_dir).resolve()
    candidate_release_manifest = Path(candidate_release_manifest).resolve()
    if freeze_id is None:
        freeze_id = f"freeze-{uuid.uuid4().hex}"
    if not FREEZE_ID_PATTERN.fullmatch(freeze_id):
        raise FounderReviewFreezeError("Freeze ID contains unsupported characters")
    created = server_created_at_utc or _now_utc()
    if not _is_utc_timestamp(created):
        raise FounderReviewFreezeError("server_created_at_utc must be explicit UTC ISO text")

    try:
        candidate = _read_candidate_manifest(candidate_release_manifest)
        side_records: dict[str, dict[str, Any]] = {}
        all_rows: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, str]] = set()
        seen_event_hashes: set[str] = set()
        for side in fr.SIDES:
            side_data = fr._validate_side_inputs(
                resource_root,
                side,
                expected_audit_sha256=expected_audit_sha256,
                durable_root=review_root,
            )
            if len(side_data["rows"]) != 12 or any(row.get("eligible") is not True for row in side_data["rows"]):
                raise FounderReviewFreezeError(f"{side} immutable identity universe is not exactly 12 eligible rows")
            chain = _verify_revision_chain(side_data, review_root)
            current_rows = _verify_current_rows(side_data, chain["current"])
            normalized_rows = [_normalize_freeze_row(row) for row in current_rows]
            for row in normalized_rows:
                event = row["eventIdentity"]
                key = (side, event["eventId"])
                if key in seen_keys or event["eventHash"] in seen_event_hashes:
                    raise FounderReviewFreezeError(f"Duplicate canonical event identity in freeze input: {side}/{event['eventId']}")
                seen_keys.add(key)
                seen_event_hashes.add(event["eventHash"])
            side_records[side] = {
                "sideData": side_data,
                "current": chain["current"],
                "chain": chain["chain"],
                "rows": normalized_rows,
            }
            all_rows.extend(normalized_rows)

        if len(side_records["USD"]["rows"]) != 12 or len(side_records["JPY"]["rows"]) != 12 or len(all_rows) != 24:
            raise FounderReviewFreezeError("Freeze requires exactly 12 USD and 12 JPY rows")
        document = _build_freeze_document(
            founder_name=founder_name,
            candidate=candidate,
            freeze_id=freeze_id,
            server_created_at_utc=created,
            side_records=side_records,
            review_rows=all_rows,
            attestation_text=attestation_text,
        )
        return _publish_bundle(document=document, output_dir=output_dir, publish_hook=publish_hook)
    except FounderReviewFreezeError:
        raise
    except fr.FounderReviewIntegrityError as exc:
        raise FounderReviewFreezeError(str(exc)) from exc
    except (OSError, TypeError, ValueError) as exc:
        raise FounderReviewFreezeError(str(exc)) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify and atomically freeze a completed Founder Review store.")
    parser.add_argument("--resource-root", required=True, type=Path, help="Immutable repository/resource root containing the canonical packets.")
    parser.add_argument("--review-root", required=True, type=Path, help="Explicit durable Founder Review root; read-only.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Parent directory for append-only freeze bundles.")
    parser.add_argument("--founder-name", required=True, help="Founder name recorded in the freeze.")
    parser.add_argument("--candidate-release-manifest", required=True, type=Path, help="Exact candidate release manifest to bind.")
    parser.add_argument("--attestation-file", required=True, type=Path, help="UTF-8 file containing the founder's outcome-blind attestation.")
    parser.add_argument("--freeze-id", help="Optional explicit append-only freeze ID; generated when omitted.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        attestation_text = args.attestation_file.read_text(encoding="utf-8")
        result = freeze_founder_review(
            resource_root=args.resource_root,
            review_root=args.review_root,
            output_dir=args.output_dir,
            founder_name=args.founder_name,
            candidate_release_manifest=args.candidate_release_manifest,
            attestation_text=attestation_text,
            freeze_id=args.freeze_id,
        )
    except FounderReviewFreezeError as exc:
        print(f"FOUNDER_REVIEW_FREEZE_FAILED: {exc}")
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
