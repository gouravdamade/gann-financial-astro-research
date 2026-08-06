"""Integrity-bound founder review packets for the R5 F2A pilot.

This module deliberately stops at founder review.  It reads the canonical
blank packets and the independent identity audit, but it never reads price,
SBC, LLM output, or the polarity catalogue.  A reviewed packet is only a
record of a founder-entered decision; it is not an admission or a forecast.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_VERSION = "founder_review_workbench_v1_20260806"
WORKBENCH_CONTRACT = "FOUNDER_REVIEW_WORKBENCH_V1"
REVIEWED_PACKET_CONTRACT = "FOUNDER_REVIEWED_POLARITY_PACKET_V1"
REVIEWED_MANIFEST_CONTRACT = "FOUNDER_REVIEWED_POLARITY_PACKET_MANIFEST_V1"

SIDES = ("USD", "JPY")
DECISIONS = (
    "SUPPORTIVE",
    "ADVERSE",
    "MIXED",
    "NEUTRAL",
    "UNKNOWN_MORE_EVIDENCE_REQUIRED",
    "REJECT_EVENT_IDENTITY",
)
EVIDENCE_CLASSIFICATIONS = (
    "FOUNDER_RESEARCH_HYPOTHESIS",
    "SOURCE_BACKED_CLASSICAL_CANDIDATE",
)
REVIEW_STATUSES = (
    "REVIEW_NOT_STARTED",
    "REVIEW_IN_PROGRESS",
    "REVIEW_COMPLETE",
    "REVIEW_COMPLETE_WITH_UNKNOWNS",
)
REVIEWABLE_IDENTITY_STATUS = "SINGLE_PASS_VERIFIED"


class FounderReviewIntegrityError(ValueError):
    """Raised when a packet or submitted review fails closed integrity checks."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FounderReviewIntegrityError(f"Required founder-review file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FounderReviewIntegrityError(f"Invalid JSON in founder-review file: {path}") from exc
    if not isinstance(value, dict):
        raise FounderReviewIntegrityError(f"Founder-review JSON must be an object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _packet_dir(project_root: Path) -> Path:
    return project_root / "research_labs" / "chart_conditioned_aspects" / "founder_review"


def _status_dir(project_root: Path) -> Path:
    return project_root / "status" / "founder_review"


def _side_paths(project_root: Path, side: str) -> dict[str, Path]:
    if side not in SIDES:
        raise FounderReviewIntegrityError(f"Unsupported founder-review side: {side}")
    stem = f"{side}_APRIL_2025"
    packet_stem = f"{stem}_BLANK_POLARITY_REVIEW_V1"
    reviewed_stem = f"{stem}_FOUNDER_REVIEWED_POLARITY_V1"
    packet_dir = _packet_dir(project_root)
    return {
        "blank": packet_dir / f"{packet_stem}.json",
        "integrity_manifest": packet_dir / f"{packet_stem}.identity_integrity.manifest.json",
        "audit": project_root / "status" / "audits" / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json",
        "reviewed": packet_dir / f"{reviewed_stem}.json",
        "reviewed_manifest": packet_dir / f"{reviewed_stem}.manifest.json",
        "reviewed_markdown": packet_dir / f"{reviewed_stem}.md",
        "completeness": packet_dir / f"{reviewed_stem}.completeness.json",
        "status": _status_dir(project_root) / f"{reviewed_stem}.status.json",
    }


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _blank_review() -> dict[str, Any]:
    return {
        "evidenceClassification": None,
        "founderReasoning": "",
        "rejectionReason": "",
        "reviewTimestampUtc": None,
        "reviewedPolarity": None,
        "reviewer": "",
        "sourceReferences": [],
    }


def _identity_fields(event: dict[str, Any]) -> dict[str, Any]:
    """Return the complete immutable event identity, without review fields."""

    return copy.deepcopy(event)


def _audit_records(audit: dict[str, Any], side: str) -> dict[str, dict[str, Any]]:
    report = audit.get("sideReports", {}).get(side)
    if not isinstance(report, dict):
        raise FounderReviewIntegrityError(f"Identity audit has no side report for {side}")
    records = report.get("eventRecords")
    if not isinstance(records, list):
        raise FounderReviewIntegrityError(f"Identity audit has no event records for {side}")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("eventId"), str):
            raise FounderReviewIntegrityError(f"Identity audit contains an invalid {side} event record")
        if record["eventId"] in result:
            raise FounderReviewIntegrityError(f"Duplicate identity-audit event ID for {side}: {record['eventId']}")
        result[record["eventId"]] = record
    return result


def _validate_side_inputs(project_root: Path, side: str) -> dict[str, Any]:
    paths = _side_paths(project_root, side)
    packet = _read_json(paths["blank"])
    manifest = _read_json(paths["integrity_manifest"])
    audit = _read_json(paths["audit"])
    actual_packet_hash = _sha256_file(paths["blank"])
    actual_manifest_hash = _sha256_file(paths["integrity_manifest"])
    expected_packet_hash = manifest.get("packetSha256")
    if actual_packet_hash != expected_packet_hash:
        raise FounderReviewIntegrityError(
            f"{side} blank packet hash mismatch: expected {expected_packet_hash}, got {actual_packet_hash}"
        )
    if manifest.get("originalGenerationManifestOutputSha256") != actual_packet_hash:
        raise FounderReviewIntegrityError(f"{side} original generation hash does not match the blank packet")
    if manifest.get("contract") != "FOUNDER_BLANK_POLARITY_REVIEW_V1_IDENTITY_VERIFICATION_MANIFEST_V1":
        raise FounderReviewIntegrityError(f"{side} identity manifest contract is not recognized")
    if manifest.get("sideIdentity") != side or not manifest.get("allRowsSinglePassVerified"):
        raise FounderReviewIntegrityError(f"{side} identity manifest is not fully verified")
    if packet.get("instrumentIdentity") != f"FX_CURRENCY:{side}":
        raise FounderReviewIntegrityError(f"{side} blank packet instrument identity mismatch")
    audit_report = audit.get("sideReports", {}).get(side)
    if not isinstance(audit_report, dict):
        raise FounderReviewIntegrityError(f"{side} accepted chart audit report is missing")
    accepted_chart = audit_report.get("acceptedChart")
    if not isinstance(accepted_chart, dict):
        raise FounderReviewIntegrityError(f"{side} accepted chart identity is missing from the audit")
    expected_chart = {
        "instrumentIdentity": packet.get("instrumentIdentity"),
        "chartId": packet.get("chartId"),
        "chartHypothesisId": packet.get("chartHypothesisId"),
    }
    if any(accepted_chart.get(key) != value for key, value in expected_chart.items()):
        raise FounderReviewIntegrityError(f"{side} blank packet chart identity does not match the accepted audit chart")

    records = _audit_records(audit, side)
    verified_event_ids = manifest.get("verifiedEventIds")
    if not isinstance(verified_event_ids, list):
        raise FounderReviewIntegrityError(f"{side} identity manifest has no verified event list")
    verified_set = set(verified_event_ids)
    rows = packet.get("rows")
    if not isinstance(rows, list):
        raise FounderReviewIntegrityError(f"{side} blank packet rows are missing")
    seen: set[str] = set()
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("eventIdentity"), dict):
            raise FounderReviewIntegrityError(f"{side} blank packet contains an invalid row")
        event = row["eventIdentity"]
        event_id = event.get("eventId")
        if not isinstance(event_id, str) or event_id in seen:
            raise FounderReviewIntegrityError(f"{side} blank packet has a missing or duplicate event ID")
        seen.add(event_id)
        audit_record = records.get(event_id)
        status = audit_record.get("status") if audit_record else "UNVERIFIED"
        checks = audit_record.get("checks", {}) if audit_record else {}
        identity_match = bool(audit_record) and all(
            event.get(key) == audit_record.get(key)
            for key in (
                "eventId",
                "eventHash",
                "transitBody",
                "natalTarget",
                "aspectType",
                "applyingStartUtc",
                "exactUtc",
                "separatingEndUtc",
            )
        )
        eligible = bool(
            event_id in verified_set
            and audit_record
            and status == REVIEWABLE_IDENTITY_STATUS
            and audit_record.get("eventHash") == event.get("eventHash")
            and identity_match
            and all(value is True for value in checks.values())
        )
        normalized_rows.append(
            {
                "eligible": eligible,
                "identityStatus": status,
                "identityChecks": {
                    "eventIdMatchesAudit": identity_match,
                    "eventHashMatchesAudit": bool(audit_record) and audit_record.get("eventHash") == event.get("eventHash"),
                    "blankPacketHashMatchesManifest": actual_packet_hash == expected_packet_hash,
                    "integrityManifestHash": actual_manifest_hash,
                    "listedAsVerified": event_id in verified_set,
                    "auditChecksPass": all(value is True for value in checks.values()),
                },
                "eventIdentity": _identity_fields(event),
                "motionPhaseAtExact": copy.deepcopy(
                    audit_record.get("audit", {}).get("motionPhaseAtExact")
                    if audit_record
                    else None
                ),
                "founderReview": _blank_review(),
            }
        )
    return {
        "sideIdentity": side,
        "instrumentIdentity": packet["instrumentIdentity"],
        "chartId": packet["chartId"],
        "chartHypothesisId": packet["chartHypothesisId"],
        "blankPacketId": f"{packet.get('contract')}:{side}",
        "blankPacketFile": paths["blank"].name,
        "blankPacketSha256": actual_packet_hash,
        "identityIntegrityManifestId": f"{manifest.get('contract')}:{side}",
        "identityIntegrityManifestFile": paths["integrity_manifest"].name,
        "identityIntegrityManifestSha256": actual_manifest_hash,
        "rows": normalized_rows,
        "sourcePacketStatus": packet.get("packetStatus"),
        "guardrails": {
            "priceDataRead": False,
            "sbcRead": False,
            "llmRead": False,
            "catalogueAdmission": False,
            "polarityAssigned": False,
            "executionAllowed": False,
            "directionalWaveRendered": False,
        },
    }


def _reviewed_base(side_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "allowedEvidenceClassifications": list(EVIDENCE_CLASSIFICATIONS),
        "allowedFounderPolarityDecisions": list(DECISIONS),
        "blankPacketId": side_data["blankPacketId"],
        "blankPacketFile": side_data["blankPacketFile"],
        "blankPacketSha256": side_data["blankPacketSha256"],
        "chartHypothesisId": side_data["chartHypothesisId"],
        "chartId": side_data["chartId"],
        "contract": REVIEWED_PACKET_CONTRACT,
        "evidenceClassificationPolicy": {
            "FOUNDER_RESEARCH_HYPOTHESIS": "CALIBRATED_RESEARCH_ONLY_NON_CLASSICAL_FINANCIALLY_UNVALIDATED",
            "SOURCE_BACKED_CLASSICAL_CANDIDATE": "PENDING_R4_MODE_2_TO_MODE_1_PROMOTION_GATE",
        },
        "founderCompletionStatus": "REVIEW_NOT_STARTED",
        "guardrails": {
            "automaticOrderPlacement": False,
            "catalogueEntryCreated": False,
            "executionAllowed": False,
            "llmRead": False,
            "marketDirectionInferred": False,
            "magnitudeConfigured": False,
            "modeOneAdmission": False,
            "polarityAssigned": False,
            "priceDataRead": False,
            "sbcRead": False,
            "waveRendered": False,
        },
        "identityIntegrityManifestFile": side_data["identityIntegrityManifestFile"],
        "identityIntegrityManifestId": side_data["identityIntegrityManifestId"],
        "identityIntegrityManifestSha256": side_data["identityIntegrityManifestSha256"],
        "instrumentIdentity": side_data["instrumentIdentity"],
        "packetVersion": 1,
        "reviewToolVersion": TOOL_VERSION,
        "rows": [],
        "sideIdentity": side_data["sideIdentity"],
        "reviewedPacketHash": None,
    }


def _completeness(rows: list[dict[str, Any]]) -> dict[str, int]:
    eligible_rows = [row for row in rows if row.get("eligible")]
    reviews = [row.get("founderReview", {}) for row in eligible_rows]
    decided = [review for review in reviews if review.get("reviewedPolarity")]
    unknown = [review for review in decided if review.get("reviewedPolarity") == "UNKNOWN_MORE_EVIDENCE_REQUIRED"]
    rejected = [review for review in decided if review.get("reviewedPolarity") == "REJECT_EVENT_IDENTITY"]
    classical = [review for review in decided if review.get("evidenceClassification") == "SOURCE_BACKED_CLASSICAL_CANDIDATE"]
    hypotheses = [review for review in decided if review.get("evidenceClassification") == "FOUNDER_RESEARCH_HYPOTHESIS"]
    return {
        "eligibleRows": len(eligible_rows),
        "decidedRows": len(decided),
        "unknownRows": len(unknown),
        "rejectedRows": len(rejected),
        "incompleteRows": len(eligible_rows) - len(decided),
        "classicalCandidates": len(classical),
        "founderResearchHypotheses": len(hypotheses),
        "nonReviewableRows": len(rows) - len(eligible_rows),
    }


def _status_for(rows: list[dict[str, Any]]) -> str:
    counts = _completeness(rows)
    if counts["decidedRows"] == 0:
        return "REVIEW_NOT_STARTED"
    if counts["incompleteRows"] > 0:
        return "REVIEW_IN_PROGRESS"
    if counts["unknownRows"] > 0:
        return "REVIEW_COMPLETE_WITH_UNKNOWNS"
    return "REVIEW_COMPLETE"


def _reviewed_rows(side_data: dict[str, Any], submitted: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    by_id = {row["eventIdentity"]["eventId"]: row for row in (submitted or [])}
    rows: list[dict[str, Any]] = []
    for row in side_data["rows"]:
        event_id = row["eventIdentity"]["eventId"]
        source = by_id.get(event_id, row)
        rows.append(
            {
                "eligible": row["eligible"],
                "identityChecks": row["identityChecks"],
                "identityStatus": row["identityStatus"],
                "motionPhaseAtExact": copy.deepcopy(row.get("motionPhaseAtExact")),
                "eventIdentity": _identity_fields(row["eventIdentity"]),
                "founderReview": copy.deepcopy(source.get("founderReview", _blank_review())),
            }
        )
    return rows


def _validate_source_references(review: dict[str, Any]) -> None:
    references = review.get("sourceReferences")
    if not isinstance(references, list) or not references:
        raise FounderReviewIntegrityError("SOURCE_BACKED_CLASSICAL_CANDIDATE requires an exact source reference")
    for reference in references:
        if not isinstance(reference, dict):
            raise FounderReviewIntegrityError("Every source reference must be an object")
        for key in ("sourceId", "edition", "locator", "connection"):
            if not isinstance(reference.get(key), str) or not reference[key].strip():
                raise FounderReviewIntegrityError(
                    f"SOURCE_BACKED_CLASSICAL_CANDIDATE source references require {key}"
                )


def _validate_submitted_rows(side_data: dict[str, Any], submitted: Any) -> list[dict[str, Any]]:
    if not isinstance(submitted, list):
        raise FounderReviewIntegrityError("Founder review rows must be a list")
    expected = {row["eventIdentity"]["eventId"]: row for row in side_data["rows"]}
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for candidate in submitted:
        if not isinstance(candidate, dict):
            raise FounderReviewIntegrityError("Founder review row must be an object")
        event = candidate.get("eventIdentity")
        if not isinstance(event, dict) or not isinstance(event.get("eventId"), str):
            raise FounderReviewIntegrityError("Founder review row is missing its immutable event identity")
        event_id = event["eventId"]
        if event_id in seen or event_id not in expected:
            raise FounderReviewIntegrityError(f"Unknown or duplicate founder-review event ID: {event_id}")
        seen.add(event_id)
        expected_event = expected[event_id]["eventIdentity"]
        if event != expected_event:
            raise FounderReviewIntegrityError(f"Founder review attempted to mutate event identity: {event_id}")
        if not expected[event_id]["eligible"]:
            raise FounderReviewIntegrityError(f"Founder review row is not eligible: {event_id}")
        review = candidate.get("founderReview")
        if not isinstance(review, dict):
            raise FounderReviewIntegrityError(f"Founder review fields are missing: {event_id}")
        decision = review.get("reviewedPolarity")
        if decision is not None and decision not in DECISIONS:
            raise FounderReviewIntegrityError(f"Unsupported founder decision for {event_id}: {decision}")
        classification = review.get("evidenceClassification")
        if decision is None:
            if classification is not None:
                raise FounderReviewIntegrityError(f"Evidence classification cannot be entered before a decision: {event_id}")
            normalized_review = _blank_review()
        elif decision == "REJECT_EVENT_IDENTITY":
            if classification is not None:
                raise FounderReviewIntegrityError(f"Rejected identity cannot claim an evidence classification: {event_id}")
            if not str(review.get("rejectionReason") or "").strip():
                raise FounderReviewIntegrityError(f"Rejected identity requires a founder rejection reason: {event_id}")
            reviewer = str(review.get("reviewer") or "").strip()
            if not reviewer:
                raise FounderReviewIntegrityError(f"Every decided row requires a reviewer: {event_id}")
            normalized_review = {
                **_blank_review(),
                "rejectionReason": str(review.get("rejectionReason")).strip(),
                "reviewedPolarity": decision,
                "reviewer": reviewer,
                "founderReasoning": str(review.get("founderReasoning") or "").strip(),
            }
        else:
            if classification not in EVIDENCE_CLASSIFICATIONS:
                raise FounderReviewIntegrityError(f"Every non-rejected decision requires an evidence classification: {event_id}")
            reviewer = str(review.get("reviewer") or "").strip()
            if not reviewer:
                raise FounderReviewIntegrityError(f"Every decided row requires a reviewer: {event_id}")
            normalized_review = {
                **_blank_review(),
                "evidenceClassification": classification,
                "founderReasoning": str(review.get("founderReasoning") or "").strip(),
                "reviewedPolarity": decision,
                "reviewer": reviewer,
            }
            if classification == "SOURCE_BACKED_CLASSICAL_CANDIDATE":
                _validate_source_references(review)
                normalized_review["sourceReferences"] = copy.deepcopy(review["sourceReferences"])
        timestamp = review.get("reviewTimestampUtc")
        if decision is not None:
            if timestamp is None:
                normalized_review["reviewTimestampUtc"] = _now_utc()
            elif not isinstance(timestamp, str) or not timestamp.endswith("Z"):
                raise FounderReviewIntegrityError(f"Review timestamp must be an explicit UTC ISO string: {event_id}")
            else:
                normalized_review["reviewTimestampUtc"] = timestamp
        normalized.append(
            {
                "eligible": True,
                "identityChecks": copy.deepcopy(expected[event_id]["identityChecks"]),
                "identityStatus": expected[event_id]["identityStatus"],
                "motionPhaseAtExact": copy.deepcopy(expected[event_id].get("motionPhaseAtExact")),
                "eventIdentity": _identity_fields(expected_event),
                "founderReview": normalized_review,
            }
        )
    # Omitted rows are allowed for partial-review submissions and remain blank.
    for event_id, expected_row in expected.items():
        if event_id not in seen:
            normalized.append(
                {
                    "eligible": expected_row["eligible"],
                    "identityChecks": copy.deepcopy(expected_row["identityChecks"]),
                    "identityStatus": expected_row["identityStatus"],
                    "eventIdentity": _identity_fields(expected_row["eventIdentity"]),
                    "founderReview": _blank_review(),
                }
            )
    normalized_by_id = {row["eventIdentity"]["eventId"]: row for row in normalized}
    return [normalized_by_id[event_id] for event_id in expected]


def _build_packet(side_data: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    packet = _reviewed_base(side_data)
    packet["rows"] = rows
    packet["founderCompletionStatus"] = _status_for(rows)
    packet["completeness"] = _completeness(rows)
    body = copy.deepcopy(packet)
    body["reviewedPacketHash"] = None
    packet["reviewedPacketHash"] = _sha256_bytes(_canonical_bytes(body))
    return packet


def _write_review_artifacts(project_root: Path, side: str, side_data: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    paths = _side_paths(project_root, side)
    _write_json(paths["reviewed"], packet)
    reviewed_file_hash = _sha256_file(paths["reviewed"])
    manifest = {
        "contract": REVIEWED_MANIFEST_CONTRACT,
        "sideIdentity": side,
        "reviewToolVersion": TOOL_VERSION,
        "reviewedPacketFile": paths["reviewed"].name,
        "reviewedPacketHash": packet["reviewedPacketHash"],
        "reviewedPacketSha256": reviewed_file_hash,
        "blankPacketFile": side_data["blankPacketFile"],
        "blankPacketSha256": side_data["blankPacketSha256"],
        "identityIntegrityManifestFile": side_data["identityIntegrityManifestFile"],
        "identityIntegrityManifestSha256": side_data["identityIntegrityManifestSha256"],
        "founderCompletionStatus": packet["founderCompletionStatus"],
        "completeness": packet["completeness"],
        "guardrails": packet["guardrails"],
    }
    _write_json(paths["reviewed_manifest"], manifest)
    _write_json(paths["completeness"], {
        "contract": "FOUNDER_REVIEW_COMPLETENESS_REPORT_V1",
        "sideIdentity": side,
        "reviewedPacketFile": paths["reviewed"].name,
        "reviewedPacketHash": packet["reviewedPacketHash"],
        "founderCompletionStatus": packet["founderCompletionStatus"],
        "counts": packet["completeness"],
    })
    _write_json(paths["status"], {
        "contract": "FOUNDER_REVIEW_PACKET_STATUS_V1",
        "sideIdentity": side,
        "reviewedPacketFile": paths["reviewed"].name,
        "reviewedPacketManifestFile": paths["reviewed_manifest"].name,
        "reviewedPacketHash": packet["reviewedPacketHash"],
        "founderCompletionStatus": packet["founderCompletionStatus"],
        "counts": packet["completeness"],
        "admission": "NOT_CONNECTED_TO_CATALOGUE",
        "guardrails": packet["guardrails"],
    })
    markdown = _markdown_render(side, side_data, packet)
    paths["reviewed_markdown"].write_text(markdown, encoding="utf-8")
    return {
        "reviewedPacketFile": paths["reviewed"].name,
        "reviewedPacketSha256": reviewed_file_hash,
        "reviewedPacketHash": packet["reviewedPacketHash"],
        "reviewedManifestFile": paths["reviewed_manifest"].name,
        "reviewedManifestSha256": _sha256_file(paths["reviewed_manifest"]),
        "completenessFile": paths["completeness"].name,
        "statusFile": str(paths["status"].relative_to(project_root)),
        "markdownFile": paths["reviewed_markdown"].name,
        "founderCompletionStatus": packet["founderCompletionStatus"],
        "counts": packet["completeness"],
    }


def _markdown_render(side: str, side_data: dict[str, Any], packet: dict[str, Any]) -> str:
    lines = [
        f"# {side} Founder Review Packet",
        "",
        "This is a non-authoritative founder-review record. It contains astronomy identity and founder-entered fields only.",
        "It does not admit a catalogue entry, infer a market direction, create a wave, or enable execution.",
        "",
        f"- Completion: `{packet['founderCompletionStatus']}`",
        f"- Blank packet SHA-256: `{side_data['blankPacketSha256']}`",
        f"- Identity manifest SHA-256: `{side_data['identityIntegrityManifestSha256']}`",
        f"- Reviewed packet hash: `{packet['reviewedPacketHash']}`",
        "",
        "| # | Transit | Natal | Aspect | Applying start (UTC / IST) | Exact (UTC / IST) | Separating end (UTC / IST) | Identity | Founder decision | Evidence class |",
        "|---:|---|---|---|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(packet["rows"], 1):
        event = row["eventIdentity"]
        review = row["founderReview"]
        lines.append(
            "| {index} | {transit} | {natal} | {aspect} | {start} / {start_ist} | {exact} / {exact_ist} | {end} / {end_ist} | {status} | {decision} | {classification} |".format(
                index=index,
                transit=event.get("transitBody", ""),
                natal=event.get("natalTarget", ""),
                aspect=event.get("aspectType", ""),
                start=event.get("applyingStartUtc", ""),
                start_ist=_ist_label(event.get("applyingStartUtc")),
                exact=event.get("exactUtc", ""),
                exact_ist=_ist_label(event.get("exactUtc")),
                end=event.get("separatingEndUtc", ""),
                end_ist=_ist_label(event.get("separatingEndUtc")),
                status=row.get("identityStatus", ""),
                decision=review.get("reviewedPolarity") or "",
                classification=review.get("evidenceClassification") or "",
            )
        )
    return "\n".join(lines) + "\n"


def _ist_label(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        from datetime import timedelta
        return (parsed + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S IST")
    except ValueError:
        return ""


def _load_existing_review(project_root: Path, side: str, side_data: dict[str, Any]) -> list[dict[str, Any]] | None:
    paths = _side_paths(project_root, side)
    if not paths["reviewed"].exists():
        return None
    packet = _read_json(paths["reviewed"])
    if packet.get("contract") != REVIEWED_PACKET_CONTRACT:
        raise FounderReviewIntegrityError(f"{side} reviewed packet contract is invalid")
    if packet.get("blankPacketSha256") != side_data["blankPacketSha256"]:
        raise FounderReviewIntegrityError(f"{side} reviewed packet points at a different blank packet")
    body = copy.deepcopy(packet)
    recorded_hash = body.pop("reviewedPacketHash", None)
    if recorded_hash != _sha256_bytes(_canonical_bytes({**body, "reviewedPacketHash": None})):
        raise FounderReviewIntegrityError(f"{side} reviewed packet hash is invalid")
    if paths["reviewed_manifest"].exists():
        manifest = _read_json(paths["reviewed_manifest"])
        if manifest.get("reviewedPacketSha256") != _sha256_file(paths["reviewed"]):
            raise FounderReviewIntegrityError(f"{side} reviewed packet manifest hash is invalid")
        if manifest.get("identityIntegrityManifestSha256") != side_data["identityIntegrityManifestSha256"]:
            raise FounderReviewIntegrityError(f"{side} reviewed packet identity manifest reference changed")
    rows = packet.get("rows")
    if not isinstance(rows, list):
        raise FounderReviewIntegrityError(f"{side} reviewed packet rows are missing")
    return _validate_submitted_rows(side_data, rows)


def build_founder_review_workbench(project_root: Path, requested_side: str | None = None) -> dict[str, Any]:
    sides = (requested_side,) if requested_side else SIDES
    side_payloads: list[dict[str, Any]] = []
    for side in sides:
        side_data = _validate_side_inputs(project_root, side)
        existing_rows = _load_existing_review(project_root, side, side_data)
        rows = existing_rows if existing_rows is not None else side_data["rows"]
        packet = _build_packet(side_data, rows)
        if existing_rows is None:
            _write_review_artifacts(project_root, side, side_data, packet)
        side_payloads.append(
            {
                **side_data,
                "rows": rows,
                "founderCompletionStatus": packet["founderCompletionStatus"],
                "completeness": packet["completeness"],
                "reviewedPacketHash": packet["reviewedPacketHash"],
            }
        )
    return {
        "contract": WORKBENCH_CONTRACT,
        "schemaVersion": 1,
        "toolVersion": TOOL_VERSION,
        "sides": side_payloads,
        "allowedFounderPolarityDecisions": list(DECISIONS),
        "allowedEvidenceClassifications": list(EVIDENCE_CLASSIFICATIONS),
        "reviewStatuses": list(REVIEW_STATUSES),
        "guardrails": {
            "blankPacketsReadOnly": True,
            "priceDataRead": False,
            "sbcRead": False,
            "llmRead": False,
            "catalogueAdmission": False,
            "directionalWaveRendered": False,
            "executionAllowed": False,
        },
    }


def export_founder_review_packet(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    side = payload.get("side")
    side_data = _validate_side_inputs(project_root, side)
    rows = _validate_submitted_rows(side_data, payload.get("rows"))
    packet = _build_packet(side_data, rows)
    return _write_review_artifacts(project_root, side, side_data, packet)
