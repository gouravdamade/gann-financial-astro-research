"""Integrity-bound, durable Founder Review records.

The blank packets, their identity manifests, and the identity audit are
immutable resource inputs. Founder-entered state is a separate application
data store with append-only revisions and an atomically published current
pointer. This module never reads price, outcomes, SBC, LLM output, or the
polarity catalogue.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator


TOOL_VERSION = "founder_review_workbench_v2_20260909"
WORKBENCH_CONTRACT = "FOUNDER_REVIEW_WORKBENCH_V1"
REVIEWED_PACKET_CONTRACT = "FOUNDER_REVIEWED_POLARITY_PACKET_V1"
REVIEWED_PACKET_SCHEMA_VERSION = 2
REVIEW_STORE_CONTRACT = "FOUNDER_REVIEW_DURABLE_STORE_V1"
CURRENT_POINTER_CONTRACT = "FOUNDER_REVIEW_CURRENT_POINTER_V1"
REVISION_MANIFEST_CONTRACT = "FOUNDER_REVIEW_REVISION_MANIFEST_V1"

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
EPHEMERIS_VERSION_PROVENANCE = "PACKET_COMPILER_METADATA"
EPHEMERIS_VERSION_SOURCE_FIELD = "eventCompiler.ephemerisVersion"

# These are the contracts of the already accepted identity audit. The
# artifact digest is over the normalized LF bytes used by _sha256_file().
IDENTITY_AUDIT_ARTIFACT_CONTRACT = "PFR_V2B_R5_F2A_R1_EVENT_IDENTITY_INTEGRITY_AUDIT_V1"
IDENTITY_AUDIT_CONTRACT = "CHART_CONDITIONED_TRANSIT_EVENT_IDENTITY_AUDIT_V1"
IDENTITY_AUDIT_VERSION = "chart_conditioned_event_identity_audit_v1_20260806"
IDENTITY_AUDIT_EXPECTED_SHA256 = "A869651BA374F5090AEE175877047BC5A945EEC91A6CC3DC419922FDE79F5F82"
MANDATORY_IDENTITY_CHECKS = (
    "acceptedChartIdentityMatches",
    "configuredOrbBoundariesVerified",
    "eventHashReproduces",
    "eventIdMatchesHash",
    "recordedExactMatchesIndependentCandidate",
    "recordedExactOrbIsPassMinimum",
    "residualReachesIntendedExactAngle",
    "strictTimeOrdering",
)


class FounderReviewIntegrityError(ValueError):
    """Raised when immutable inputs or a submitted review fail closed."""


class FounderReviewRevisionConflictError(FounderReviewIntegrityError):
    """Raised when a client submits against an obsolete current revision."""

    def __init__(
        self,
        side: str,
        expected_revision_hash: str | None,
        current_revision_hash: str | None,
        current_revision_id: str | None,
    ) -> None:
        self.side = side
        self.expected_revision_hash = expected_revision_hash
        self.current_revision_hash = current_revision_hash
        self.current_revision_id = current_revision_id
        super().__init__(
            f"Founder review revision conflict for {side}: expected "
            f"{expected_revision_hash or 'no revision'}, current "
            f"{current_revision_hash or 'no revision'}"
        )


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
    """Hash JSON independently of a Windows CRLF checkout conversion."""

    return _sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FounderReviewIntegrityError(
            f"Required founder-review file is missing: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise FounderReviewIntegrityError(
            f"Invalid JSON in founder-review file: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise FounderReviewIntegrityError(
            f"Founder-review JSON must be an object: {path}"
        )
    return value


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    try:
        with temporary.open("wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_write_bytes(path, _json_bytes(value))


def _packet_dir(project_root: Path) -> Path:
    return project_root / "research_labs" / "chart_conditioned_aspects" / "founder_review"


def _status_dir(project_root: Path) -> Path:
    # Kept as a named helper for callers that used the old immutable path
    # layout. New status reports are written below the durable store.
    return project_root / "status" / "founder_review"


def review_store_root(
    project_root: Path | None = None,
    explicit_root: Path | None = None,
) -> Path:
    """Resolve mutable review state separately from immutable resources."""

    if explicit_root is not None:
        return Path(explicit_root).expanduser().resolve()
    configured = str(os.environ.get("GANN_ASTRO_FOUNDER_REVIEW_ROOT") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    data_root = str(os.environ.get("GANN_ASTRO_DESKTOP_DATA") or "").strip()
    if data_root:
        return (Path(data_root).expanduser().resolve() / "founder_review").resolve()
    if Path("D:/").exists():
        return Path(r"D:\GannFinancialAstro\app_data\founder_review")
    local = Path(os.environ.get("LOCALAPPDATA") or Path.home())
    return (local / "GannAstroDesk" / "founder_review").resolve()


def _side_paths(
    project_root: Path,
    side: str,
    durable_root: Path | None = None,
) -> dict[str, Path]:
    if side not in SIDES:
        raise FounderReviewIntegrityError(f"Unsupported founder-review side: {side}")
    stem = f"{side}_APRIL_2025"
    packet_stem = f"{stem}_BLANK_POLARITY_REVIEW_V1"
    packet_dir = _packet_dir(project_root)
    store = review_store_root(project_root, durable_root)
    return {
        "blank": packet_dir / f"{packet_stem}.json",
        "integrity_manifest": packet_dir / f"{packet_stem}.identity_integrity.manifest.json",
        "audit": project_root
        / "status"
        / "audits"
        / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json",
        "store": store,
        "current": store / "current" / f"{side}.json",
        "revisions": store / "revisions" / side,
    }


_LOCKS: dict[str, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()


@contextmanager
def _store_lock(root: Path, side: str) -> Iterator[None]:
    """Serialize writers in-process and across sidecar processes."""

    key = f"{root.resolve()}::{side}"
    with _LOCKS_GUARD:
        lock = _LOCKS.setdefault(key, threading.RLock())
    lock.acquire()
    lock_path = root / "locks" / f"{side}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    try:
        handle.seek(0)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()
            lock.release()


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _next_server_timestamp(previous: str | None) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if isinstance(previous, str):
        try:
            prior = datetime.fromisoformat(previous.replace("Z", "+00:00"))
        except ValueError as exc:
            raise FounderReviewIntegrityError(
                "Current revision has an invalid server timestamp"
            ) from exc
        if now <= prior:
            now = prior + timedelta(seconds=1)
    return now.isoformat().replace("+00:00", "Z")


def _blank_review() -> dict[str, Any]:
    return {
        "evidenceClassification": None,
        "founderReasoning": "",
        "firstReviewedAtUtc": None,
        "lastModifiedAtUtc": None,
        "rejectionReason": "",
        "reviewTimestampUtc": None,
        "reviewedPolarity": None,
        "reviewer": "",
        "sourceReferences": [],
    }


def _identity_fields(event: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(event)


def _audit_records(audit: dict[str, Any], side: str) -> dict[str, dict[str, Any]]:
    reports = audit.get("sideReports")
    report = reports.get(side) if isinstance(reports, dict) else None
    if not isinstance(report, dict):
        raise FounderReviewIntegrityError(f"Identity audit has no side report for {side}")
    records = report.get("eventRecords")
    if not isinstance(records, list):
        raise FounderReviewIntegrityError(f"Identity audit has no event records for {side}")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("eventId"), str):
            raise FounderReviewIntegrityError(
                f"Identity audit contains an invalid {side} event record"
            )
        if record["eventId"] in result:
            raise FounderReviewIntegrityError(
                f"Duplicate identity-audit event ID for {side}: {record['eventId']}"
            )
        result[record["eventId"]] = record
    return result


def _validate_event_compiler(
    packet: dict[str, Any], side: str
) -> tuple[dict[str, Any], str]:
    event_compiler = packet.get("eventCompiler")
    if not isinstance(event_compiler, dict):
        raise FounderReviewIntegrityError(f"{side} blank packet eventCompiler metadata is missing")
    version = event_compiler.get("ephemerisVersion")
    if not isinstance(version, str) or not version.strip():
        raise FounderReviewIntegrityError(
            f"{side} blank packet eventCompiler.ephemerisVersion is missing or blank"
        )
    provider = event_compiler.get("ephemerisProvider")
    if not isinstance(provider, str) or not provider.strip():
        raise FounderReviewIntegrityError(
            f"{side} blank packet eventCompiler.ephemerisProvider is missing or blank"
        )
    return copy.deepcopy(event_compiler), version


def _checks_pass(checks: Any) -> bool:
    """Require the exact mandatory boolean check contract, fail closed."""

    if type(checks) is not dict:
        return False
    if set(checks) != set(MANDATORY_IDENTITY_CHECKS):
        return False
    for key in MANDATORY_IDENTITY_CHECKS:
        if type(checks.get(key)) is not bool or checks[key] is not True:
            return False
    return True


def _validate_side_inputs(
    project_root: Path,
    side: str,
    expected_audit_sha256: str = IDENTITY_AUDIT_EXPECTED_SHA256,
    durable_root: Path | None = None,
) -> dict[str, Any]:
    paths = _side_paths(project_root, side, durable_root)
    packet = _read_json(paths["blank"])
    manifest = _read_json(paths["integrity_manifest"])
    audit = _read_json(paths["audit"])
    actual_packet_hash = _sha256_file(paths["blank"])
    actual_manifest_hash = _sha256_file(paths["integrity_manifest"])
    actual_audit_hash = _sha256_file(paths["audit"])

    if actual_audit_hash != expected_audit_sha256:
        raise FounderReviewIntegrityError(
            f"{side} identity audit hash mismatch: expected {expected_audit_sha256}, got {actual_audit_hash}"
        )
    if audit.get("contract") != IDENTITY_AUDIT_ARTIFACT_CONTRACT:
        raise FounderReviewIntegrityError("Identity audit artifact contract is not recognized")
    if audit.get("auditVersion") != IDENTITY_AUDIT_VERSION:
        raise FounderReviewIntegrityError("Identity audit artifact version is not recognized")
    if manifest.get("contract") != "FOUNDER_BLANK_POLARITY_REVIEW_V1_IDENTITY_VERIFICATION_MANIFEST_V1":
        raise FounderReviewIntegrityError(f"{side} identity manifest contract is not recognized")
    if manifest.get("sideIdentity") != side:
        raise FounderReviewIntegrityError(f"{side} identity manifest side binding is invalid")
    if type(manifest.get("allRowsSinglePassVerified")) is not bool or not manifest["allRowsSinglePassVerified"]:
        raise FounderReviewIntegrityError(f"{side} identity manifest is not fully verified")
    if manifest.get("identityAuditContract") != IDENTITY_AUDIT_CONTRACT:
        raise FounderReviewIntegrityError(f"{side} identity manifest audit contract binding is invalid")
    if manifest.get("identityAuditVersion") != IDENTITY_AUDIT_VERSION:
        raise FounderReviewIntegrityError(f"{side} identity manifest audit version binding is invalid")
    if manifest.get("packetSha256") != actual_packet_hash:
        raise FounderReviewIntegrityError(
            f"{side} blank packet hash mismatch: expected {manifest.get('packetSha256')}, got {actual_packet_hash}"
        )
    if manifest.get("originalGenerationManifestOutputSha256") != actual_packet_hash:
        raise FounderReviewIntegrityError(f"{side} original generation hash does not match the blank packet")
    if packet.get("instrumentIdentity") != f"FX_CURRENCY:{side}":
        raise FounderReviewIntegrityError(f"{side} blank packet instrument identity mismatch")

    reports = audit.get("sideReports")
    audit_report = reports.get(side) if isinstance(reports, dict) else None
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
        raise FounderReviewIntegrityError(
            f"{side} blank packet chart identity does not match the accepted audit chart"
        )

    records = _audit_records(audit, side)
    verified_event_ids = manifest.get("verifiedEventIds")
    if not isinstance(verified_event_ids, list) or not all(
        isinstance(value, str) for value in verified_event_ids
    ):
        raise FounderReviewIntegrityError(f"{side} identity manifest has no valid verified event list")
    if len(set(verified_event_ids)) != len(verified_event_ids):
        raise FounderReviewIntegrityError(f"{side} identity manifest has duplicate verified event IDs")
    verified_set = set(verified_event_ids)
    rows = packet.get("rows")
    if not isinstance(rows, list):
        raise FounderReviewIntegrityError(f"{side} blank packet rows are missing")

    event_compiler, ephemeris_version = _validate_event_compiler(packet, side)
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
        packet_identity = {
            "sideIdentity": side,
            "instrumentIdentity": packet.get("instrumentIdentity"),
            "chartId": packet.get("chartId"),
            "chartHypothesisId": packet.get("chartHypothesisId"),
        }
        if any(event.get(key) != value for key, value in packet_identity.items()):
            raise FounderReviewIntegrityError(
                f"{side} event {event_id} provenance does not match its blank packet identity"
            )
        for field, message, compiler_field in (
            ("eventContract", "event contract conflicts", "contract"),
            ("astronomyContract", "astronomy contract conflicts", "astronomyContract"),
            ("generatorVersion", "generator provenance conflicts", "generatorVersion"),
        ):
            if event.get(field) != event_compiler.get(compiler_field):
                raise FounderReviewIntegrityError(
                    f"{side} event {event_id} {message} with packet eventCompiler metadata"
                )

        audit_record = records.get(event_id)
        status_value = audit_record.get("status") if isinstance(audit_record, dict) else None
        status = status_value if isinstance(status_value, str) else "UNVERIFIED"
        identity_match = isinstance(audit_record, dict) and all(
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
        hash_match = isinstance(audit_record, dict) and audit_record.get("eventHash") == event.get("eventHash")
        checks = audit_record.get("checks") if isinstance(audit_record, dict) else None
        audit_checks_pass = _checks_pass(checks)
        nested_audit = audit_record.get("audit") if isinstance(audit_record, dict) else None
        nested_contract = isinstance(nested_audit, dict) and nested_audit.get("contract") == IDENTITY_AUDIT_CONTRACT
        nested_version = isinstance(nested_audit, dict) and nested_audit.get("auditVersion") == IDENTITY_AUDIT_VERSION
        eligible = bool(
            event_id in verified_set
            and isinstance(audit_record, dict)
            and status == REVIEWABLE_IDENTITY_STATUS
            and hash_match
            and identity_match
            and audit_checks_pass
            and nested_contract
            and nested_version
        )
        normalized_rows.append(
            {
                "eligible": eligible,
                "identityStatus": status,
                "identityChecks": {
                    "eventIdMatchesAudit": bool(identity_match),
                    "eventHashMatchesAudit": bool(hash_match),
                    "blankPacketHashMatchesManifest": actual_packet_hash == manifest.get("packetSha256"),
                    "integrityManifestHash": actual_manifest_hash,
                    "listedAsVerified": event_id in verified_set,
                    "auditChecksPass": audit_checks_pass,
                    "identityAuditContractMatches": bool(nested_contract),
                    "identityAuditVersionMatches": bool(nested_version),
                    "identityAuditHashMatches": actual_audit_hash == expected_audit_sha256,
                    "identityManifestBindsAudit": (
                        manifest.get("identityAuditContract") == IDENTITY_AUDIT_CONTRACT
                        and manifest.get("identityAuditVersion") == IDENTITY_AUDIT_VERSION
                    ),
                    "eventCompilerMetadataPresent": True,
                    "eventCompilerProvenance": EPHEMERIS_VERSION_PROVENANCE,
                },
                "eventIdentity": _identity_fields(event),
                "motionPhaseAtExact": copy.deepcopy(
                    nested_audit.get("motionPhaseAtExact") if isinstance(nested_audit, dict) else None
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
        "identityAuditContract": IDENTITY_AUDIT_CONTRACT,
        "identityAuditVersion": IDENTITY_AUDIT_VERSION,
        "identityAuditSha256": actual_audit_hash,
        "eventCompiler": event_compiler,
        "ephemerisVersion": ephemeris_version,
        "ephemerisVersionProvenance": EPHEMERIS_VERSION_PROVENANCE,
        "ephemerisVersionSourcePacketSha256": actual_packet_hash,
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
        "sourceBlankPacketSha256": side_data["blankPacketSha256"],
        "eventCompiler": copy.deepcopy(side_data["eventCompiler"]),
        "ephemerisVersion": side_data["ephemerisVersion"],
        "ephemerisVersionProvenance": EPHEMERIS_VERSION_PROVENANCE,
        "ephemerisVersionSourcePacketSha256": side_data["blankPacketSha256"],
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
        "identityAuditContract": side_data["identityAuditContract"],
        "identityAuditVersion": side_data["identityAuditVersion"],
        "identityAuditSha256": side_data["identityAuditSha256"],
        "instrumentIdentity": side_data["instrumentIdentity"],
        "packetVersion": REVIEWED_PACKET_SCHEMA_VERSION,
        "reviewToolVersion": TOOL_VERSION,
        "schemaVersion": REVIEWED_PACKET_SCHEMA_VERSION,
        "rows": [],
        "sideIdentity": side_data["sideIdentity"],
        "revisionId": None,
        "serverCreatedAtUtc": None,
        "previousRevisionHash": None,
        "revisionHash": None,
        "reviewedPacketHash": None,
    }


def _completeness(rows: list[dict[str, Any]]) -> dict[str, int]:
    eligible_rows = [row for row in rows if row.get("eligible")]
    reviews = [row.get("founderReview", {}) for row in eligible_rows]
    decided = [review for review in reviews if review.get("reviewedPolarity")]
    unknown = [
        review
        for review in decided
        if review.get("reviewedPolarity") == "UNKNOWN_MORE_EVIDENCE_REQUIRED"
    ]
    rejected = [
        review
        for review in decided
        if review.get("reviewedPolarity") == "REJECT_EVENT_IDENTITY"
    ]
    classical = [
        review
        for review in decided
        if review.get("evidenceClassification") == "SOURCE_BACKED_CLASSICAL_CANDIDATE"
    ]
    hypotheses = [
        review
        for review in decided
        if review.get("evidenceClassification") == "FOUNDER_RESEARCH_HYPOTHESIS"
    ]
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


def _is_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _validate_source_references(review: dict[str, Any]) -> None:
    references = review.get("sourceReferences")
    if not isinstance(references, list) or not references:
        raise FounderReviewIntegrityError(
            "SOURCE_BACKED_CLASSICAL_CANDIDATE requires an exact source reference"
        )
    for reference in references:
        if not isinstance(reference, dict):
            raise FounderReviewIntegrityError("Every source reference must be an object")
        for key in ("sourceId", "edition", "locator", "connection"):
            if type(reference.get(key)) is not str or not reference[key].strip():
                raise FounderReviewIntegrityError(
                    f"SOURCE_BACKED_CLASSICAL_CANDIDATE source references require {key}"
                )


def _review_content(review: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(review.get(key))
        for key in (
            "evidenceClassification",
            "founderReasoning",
            "rejectionReason",
            "reviewedPolarity",
            "reviewer",
            "sourceReferences",
        )
    }


def _validate_review_types(review: dict[str, Any], event_id: str) -> None:
    for key in ("founderReasoning", "rejectionReason", "reviewer"):
        if key in review and type(review[key]) is not str:
            raise FounderReviewIntegrityError(f"Founder review field {key} must be a string: {event_id}")
    for key in ("reviewTimestampUtc", "firstReviewedAtUtc", "lastModifiedAtUtc"):
        if key in review and review[key] is not None and not _is_utc_timestamp(review[key]):
            raise FounderReviewIntegrityError(f"Founder review field {key} must be explicit UTC ISO: {event_id}")
    references = review.get("sourceReferences", [])
    if type(references) is not list:
        raise FounderReviewIntegrityError(f"Founder review sourceReferences must be a list: {event_id}")
    for reference in references:
        if not isinstance(reference, dict):
            raise FounderReviewIntegrityError(f"Founder review source reference must be an object: {event_id}")
        for key in ("sourceId", "edition", "locator", "connection"):
            if key in reference and type(reference[key]) is not str:
                raise FounderReviewIntegrityError(f"Founder review source reference {key} must be a string: {event_id}")


def _normalize_review_input(review: Any, event_id: str) -> dict[str, Any]:
    if not isinstance(review, dict):
        raise FounderReviewIntegrityError(f"Founder review fields are missing: {event_id}")
    _validate_review_types(review, event_id)
    decision = review.get("reviewedPolarity")
    if decision is not None and decision not in DECISIONS:
        raise FounderReviewIntegrityError(f"Unsupported founder decision for {event_id}: {decision}")
    classification = review.get("evidenceClassification")
    if classification is not None and classification not in EVIDENCE_CLASSIFICATIONS:
        raise FounderReviewIntegrityError(f"Unsupported evidence classification for {event_id}: {classification}")
    reasoning = review.get("founderReasoning", "")
    rejection_reason = review.get("rejectionReason", "")
    reviewer = review.get("reviewer", "")
    references = review.get("sourceReferences", [])
    if decision is None:
        if classification is not None or reasoning.strip() or rejection_reason.strip() or reviewer.strip() or references:
            raise FounderReviewIntegrityError(f"Blank founder decision contains review fields: {event_id}")
        return _blank_review()
    if decision == "REJECT_EVENT_IDENTITY":
        if classification is not None:
            raise FounderReviewIntegrityError(f"Rejected identity cannot claim an evidence classification: {event_id}")
        if not rejection_reason.strip():
            raise FounderReviewIntegrityError(f"Rejected identity requires a founder rejection reason: {event_id}")
        if not reviewer.strip():
            raise FounderReviewIntegrityError(f"Every decided row requires a reviewer: {event_id}")
        if references:
            raise FounderReviewIntegrityError(f"Rejected identity cannot claim source references: {event_id}")
        return {
            **_blank_review(),
            "rejectionReason": rejection_reason.strip(),
            "reviewedPolarity": decision,
            "reviewer": reviewer.strip(),
            "founderReasoning": reasoning.strip(),
        }
    if classification not in EVIDENCE_CLASSIFICATIONS:
        raise FounderReviewIntegrityError(
            f"Every non-rejected decision requires an evidence classification: {event_id}"
        )
    if not reviewer.strip():
        raise FounderReviewIntegrityError(f"Every decided row requires a reviewer: {event_id}")
    normalized_reasoning = reasoning.strip()
    if decision in {"SUPPORTIVE", "ADVERSE"} and not normalized_reasoning:
        raise FounderReviewIntegrityError(f"{decision} requires non-empty founder reasoning: {event_id}")
    if classification == "SOURCE_BACKED_CLASSICAL_CANDIDATE":
        _validate_source_references(review)
    else:
        # References are optional for the calibrated research class, but any
        # supplied records still have to be strictly typed and complete.
        for reference in references:
            for key in ("sourceId", "edition", "locator", "connection"):
                if type(reference.get(key)) is not str:
                    raise FounderReviewIntegrityError(f"Founder research source reference {key} is invalid: {event_id}")
    return {
        **_blank_review(),
        "evidenceClassification": classification,
        "founderReasoning": normalized_reasoning,
        "reviewedPolarity": decision,
        "reviewer": reviewer.strip(),
        "sourceReferences": copy.deepcopy(references),
    }


def _validate_stored_rows(side_data: dict[str, Any], rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise FounderReviewIntegrityError(f"{side_data['sideIdentity']} reviewed packet rows are missing")
    expected = {row["eventIdentity"]["eventId"]: row for row in side_data["rows"]}
    if len(rows) != len(expected):
        raise FounderReviewIntegrityError(f"{side_data['sideIdentity']} reviewed packet row count is invalid")
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for stored in rows:
        if not isinstance(stored, dict) or not isinstance(stored.get("eventIdentity"), dict):
            raise FounderReviewIntegrityError("Reviewed packet contains an invalid row")
        event_id = stored["eventIdentity"].get("eventId")
        if not isinstance(event_id, str) or event_id in seen or event_id not in expected:
            raise FounderReviewIntegrityError("Reviewed packet contains an unknown or duplicate event identity")
        seen.add(event_id)
        expected_row = expected[event_id]
        if stored["eventIdentity"] != expected_row["eventIdentity"]:
            raise FounderReviewIntegrityError(f"Reviewed packet attempted to mutate event identity: {event_id}")
        supplied = stored.get("founderReview")
        review = _normalize_review_input(supplied, event_id)
        if not isinstance(supplied, dict):
            raise FounderReviewIntegrityError(f"Reviewed packet founder fields are invalid: {event_id}")
        for key in ("firstReviewedAtUtc", "lastModifiedAtUtc", "reviewTimestampUtc"):
            review[key] = supplied.get(key)
        if review["reviewedPolarity"] is None and any(
            review[key] is not None for key in ("firstReviewedAtUtc", "lastModifiedAtUtc", "reviewTimestampUtc")
        ):
            raise FounderReviewIntegrityError(f"Blank reviewed row contains review chronology: {event_id}")
        if review["reviewedPolarity"] is not None and (
            not _is_utc_timestamp(review["firstReviewedAtUtc"])
            or not _is_utc_timestamp(review["lastModifiedAtUtc"])
            or not _is_utc_timestamp(review["reviewTimestampUtc"])
        ):
            raise FounderReviewIntegrityError(f"Decided reviewed row lacks server chronology: {event_id}")
        output.append(
            {
                "eligible": expected_row["eligible"],
                "identityChecks": copy.deepcopy(expected_row["identityChecks"]),
                "identityStatus": expected_row["identityStatus"],
                "motionPhaseAtExact": copy.deepcopy(expected_row.get("motionPhaseAtExact")),
                "eventIdentity": _identity_fields(expected_row["eventIdentity"]),
                "founderReview": review,
            }
        )
    return output


def _validate_submitted_rows(
    side_data: dict[str, Any],
    submitted: Any,
    existing_rows: list[dict[str, Any]] | None = None,
    server_now: str | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(submitted, list):
        raise FounderReviewIntegrityError("Founder review rows must be a list")
    expected = {row["eventIdentity"]["eventId"]: row for row in side_data["rows"]}
    prior_rows = existing_rows or side_data["rows"]
    prior_by_id = {row["eventIdentity"]["eventId"]: row for row in prior_rows}
    seen: set[str] = set()
    submitted_by_id: dict[str, dict[str, Any]] = {}
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
        submitted_by_id[event_id] = candidate

    effective_now = server_now or _now_utc()
    normalized: list[dict[str, Any]] = []
    for event_id, expected_row in expected.items():
        prior = prior_by_id.get(event_id, expected_row)
        prior_review = prior.get("founderReview", _blank_review())
        candidate = submitted_by_id.get(event_id)
        if candidate is None:
            normalized.append(copy.deepcopy(prior))
            continue
        review = _normalize_review_input(candidate.get("founderReview"), event_id)
        prior_content = _review_content(prior_review)
        if review["reviewedPolarity"] is not None:
            if _review_content(review) == prior_content and prior_review.get("lastModifiedAtUtc"):
                review["firstReviewedAtUtc"] = prior_review.get("firstReviewedAtUtc")
                review["lastModifiedAtUtc"] = prior_review.get("lastModifiedAtUtc")
                review["reviewTimestampUtc"] = prior_review.get("reviewTimestampUtc")
            else:
                review["firstReviewedAtUtc"] = (
                    prior_review.get("firstReviewedAtUtc")
                    if prior_review.get("reviewedPolarity") is not None
                    else effective_now
                )
                review["lastModifiedAtUtc"] = effective_now
                review["reviewTimestampUtc"] = effective_now
        normalized.append(
            {
                "eligible": expected_row["eligible"],
                "identityChecks": copy.deepcopy(expected_row["identityChecks"]),
                "identityStatus": expected_row["identityStatus"],
                "motionPhaseAtExact": copy.deepcopy(expected_row.get("motionPhaseAtExact")),
                "eventIdentity": _identity_fields(expected_row["eventIdentity"]),
                "founderReview": review,
            }
        )
    return normalized


def _build_packet(
    side_data: dict[str, Any],
    rows: list[dict[str, Any]],
    revision_id: str | None = None,
    server_created_at_utc: str | None = None,
    previous_revision_hash: str | None = None,
) -> dict[str, Any]:
    packet = _reviewed_base(side_data)
    packet["rows"] = copy.deepcopy(rows)
    packet["revisionId"] = revision_id
    packet["serverCreatedAtUtc"] = server_created_at_utc
    packet["previousRevisionHash"] = previous_revision_hash
    packet["founderCompletionStatus"] = _status_for(rows)
    packet["completeness"] = _completeness(rows)
    body = copy.deepcopy(packet)
    body["reviewedPacketHash"] = None
    body["revisionHash"] = None
    packet["reviewedPacketHash"] = _sha256_bytes(_canonical_bytes(body))
    if revision_id is not None:
        revision_body = copy.deepcopy(packet)
        revision_body["revisionHash"] = None
        packet["revisionHash"] = _sha256_bytes(_canonical_bytes(revision_body))
    return packet


def _verify_packet_hash(packet: dict[str, Any]) -> None:
    recorded = packet.get("reviewedPacketHash")
    if not isinstance(recorded, str):
        raise FounderReviewIntegrityError("Reviewed packet hash is missing")
    body = copy.deepcopy(packet)
    body["reviewedPacketHash"] = None
    # The packet digest is the content digest before the revision envelope is
    # assigned.  Keep it independent from the parent-linked revision digest.
    body["revisionHash"] = None
    if recorded != _sha256_bytes(_canonical_bytes(body)):
        raise FounderReviewIntegrityError("Reviewed packet hash is invalid")


def _verify_revision_hash(packet: dict[str, Any]) -> None:
    recorded = packet.get("revisionHash")
    if not isinstance(recorded, str):
        raise FounderReviewIntegrityError("Reviewed packet revision hash is missing")
    body = copy.deepcopy(packet)
    body["revisionHash"] = None
    if recorded != _sha256_bytes(_canonical_bytes(body)):
        raise FounderReviewIntegrityError("Reviewed packet revision hash is invalid")


def _markdown_render(side: str, side_data: dict[str, Any], packet: dict[str, Any]) -> str:
    lines = [
        f"# {side} Founder Review Packet",
        "",
        "This is a non-authoritative founder-review record. It contains astronomy identity and founder-entered fields only.",
        "It does not admit a catalogue entry, infer a market direction, create a wave, or enable execution.",
        "",
        f"- Revision ID: `{packet.get('revisionId') or ''}`",
        f"- Server created: `{packet.get('serverCreatedAtUtc') or ''}`",
        f"- Previous revision hash: `{packet.get('previousRevisionHash') or ''}`",
        f"- Revision hash: `{packet.get('revisionHash') or ''}`",
        f"- Completion: `{packet['founderCompletionStatus']}`",
        f"- Blank packet SHA-256: `{side_data['blankPacketSha256']}`",
        f"- Identity manifest SHA-256: `{side_data['identityIntegrityManifestSha256']}`",
        f"- Identity audit SHA-256: `{side_data['identityAuditSha256']}`",
        f"- Ephemeris version: `{packet['ephemerisVersion']}` (bound from `{EPHEMERIS_VERSION_SOURCE_FIELD}`; `{packet['ephemerisVersionProvenance']}`)",
        f"- Reviewed packet hash: `{packet['reviewedPacketHash']}`",
        "",
        "| # | Event | Identity | Decision | Evidence class | Reviewer | First reviewed | Last modified | Reasoning / rejection | Source references |",
        "|---:|---|---|---|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(packet["rows"], 1):
        event = row["eventIdentity"]
        review = row["founderReview"]
        references = "; ".join(
            f"{item.get('sourceId', '')} {item.get('edition', '')} {item.get('locator', '')}: {item.get('connection', '')}"
            for item in review.get("sourceReferences", [])
        )
        reason = review.get("founderReasoning", "") or review.get("rejectionReason", "")
        lines.append(
            "| {index} | {transit} to {natal} / {aspect} | {status} | {decision} | {classification} | {reviewer} | {first} | {last} | {reason} | {references} |".format(
                index=index,
                transit=event.get("transitBody", ""),
                natal=event.get("natalTarget", ""),
                aspect=event.get("aspectType", ""),
                status=row.get("identityStatus", ""),
                decision=review.get("reviewedPolarity") or "",
                classification=review.get("evidenceClassification") or "",
                reviewer=review.get("reviewer", ""),
                first=review.get("firstReviewedAtUtc") or "",
                last=review.get("lastModifiedAtUtc") or "",
                reason=reason.replace("|", "\\|"),
                references=references.replace("|", "\\|"),
            )
        )
    return "\n".join(lines) + "\n"


def _load_current_revision(
    side_data: dict[str, Any],
    durable_root: Path,
) -> dict[str, Any] | None:
    side = side_data["sideIdentity"]
    paths = _side_paths(Path("."), side, durable_root)
    pointer_path = paths["current"]
    if not pointer_path.exists():
        return None
    pointer = _read_json(pointer_path)
    if pointer.get("contract") != CURRENT_POINTER_CONTRACT or pointer.get("sideIdentity") != side:
        raise FounderReviewIntegrityError(f"{side} current review pointer is invalid")
    revision_id = pointer.get("revisionId")
    revision_hash = pointer.get("revisionHash")
    if type(revision_id) is not str or type(revision_hash) is not str:
        raise FounderReviewIntegrityError(f"{side} current review pointer lacks revision identity")
    revision_dir = paths["revisions"] / revision_id
    if revision_dir.resolve().parent != paths["revisions"].resolve():
        raise FounderReviewIntegrityError(f"{side} current review pointer escapes the durable store")
    packet_path = revision_dir / "reviewed_packet.json"
    manifest_path = revision_dir / "manifest.json"
    completeness_path = revision_dir / "completeness.json"
    status_path = revision_dir / "status.json"
    markdown_path = revision_dir / "reviewed.md"
    for path in (packet_path, manifest_path, completeness_path, status_path, markdown_path):
        if not path.is_file():
            raise FounderReviewIntegrityError(f"{side} current review revision is incomplete")
    packet = _read_json(packet_path)
    if packet.get("contract") != REVIEWED_PACKET_CONTRACT or packet.get("schemaVersion") != REVIEWED_PACKET_SCHEMA_VERSION:
        raise FounderReviewIntegrityError(f"{side} reviewed packet schema is invalid")
    if packet.get("sideIdentity") != side:
        raise FounderReviewIntegrityError(f"{side} reviewed packet side identity changed")
    if packet.get("revisionId") != revision_id or packet.get("revisionHash") != revision_hash:
        raise FounderReviewIntegrityError(f"{side} current review pointer does not bind the revision")
    for field, expected in (
        ("blankPacketSha256", side_data["blankPacketSha256"]),
        ("sourceBlankPacketSha256", side_data["blankPacketSha256"]),
        ("identityIntegrityManifestSha256", side_data["identityIntegrityManifestSha256"]),
        ("identityAuditContract", side_data["identityAuditContract"]),
        ("identityAuditVersion", side_data["identityAuditVersion"]),
        ("identityAuditSha256", side_data["identityAuditSha256"]),
        ("ephemerisVersion", side_data["ephemerisVersion"]),
        ("ephemerisVersionSourcePacketSha256", side_data["blankPacketSha256"]),
    ):
        if packet.get(field) != expected:
            raise FounderReviewIntegrityError(f"{side} reviewed packet binding changed: {field}")
    _verify_packet_hash(packet)
    _verify_revision_hash(packet)
    rows = _validate_stored_rows(side_data, packet.get("rows"))
    manifest = _read_json(manifest_path)
    if manifest.get("contract") != REVISION_MANIFEST_CONTRACT:
        raise FounderReviewIntegrityError(f"{side} review revision manifest contract is invalid")
    if manifest.get("revisionId") != revision_id or manifest.get("revisionHash") != revision_hash:
        raise FounderReviewIntegrityError(f"{side} review revision manifest does not bind the revision")
    if manifest.get("reviewedPacketHash") != packet.get("reviewedPacketHash"):
        raise FounderReviewIntegrityError(f"{side} review revision manifest packet hash is invalid")
    if manifest.get("reviewedPacketSha256") != _sha256_file(packet_path):
        raise FounderReviewIntegrityError(f"{side} review revision manifest file hash is invalid")
    if manifest.get("blankPacketSha256") != side_data["blankPacketSha256"]:
        raise FounderReviewIntegrityError(f"{side} review revision blank packet binding changed")
    if manifest.get("identityIntegrityManifestSha256") != side_data["identityIntegrityManifestSha256"]:
        raise FounderReviewIntegrityError(f"{side} review revision identity manifest binding changed")
    if manifest.get("identityAuditSha256") != side_data["identityAuditSha256"]:
        raise FounderReviewIntegrityError(f"{side} review revision identity audit binding changed")
    return {
        "pointer": pointer,
        "packet": packet,
        "rows": rows,
        "revisionId": revision_id,
        "revisionHash": revision_hash,
        "revisionDirectory": revision_dir,
        "packetPath": packet_path,
        "manifestPath": manifest_path,
        "completenessPath": completeness_path,
        "statusPath": status_path,
        "markdownPath": markdown_path,
    }


def _persist_revision(
    side_data: dict[str, Any],
    rows: list[dict[str, Any]],
    durable_root: Path,
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    side = side_data["sideIdentity"]
    paths = _side_paths(Path("."), side, durable_root)
    paths["revisions"].mkdir(parents=True, exist_ok=True)
    revision_id = f"rev-{uuid.uuid4().hex}"
    previous_hash = previous["revisionHash"] if previous else None
    created = _next_server_timestamp(previous["packet"].get("serverCreatedAtUtc") if previous else None)
    packet = _build_packet(
        side_data,
        rows,
        revision_id=revision_id,
        server_created_at_utc=created,
        previous_revision_hash=previous_hash,
    )
    temporary_dir = Path(tempfile.mkdtemp(prefix=".revision-", dir=str(paths["revisions"])))
    final_dir = paths["revisions"] / revision_id
    try:
        packet_path = temporary_dir / "reviewed_packet.json"
        manifest_path = temporary_dir / "manifest.json"
        completeness_path = temporary_dir / "completeness.json"
        status_path = temporary_dir / "status.json"
        markdown_path = temporary_dir / "reviewed.md"
        _write_json(packet_path, packet)
        manifest = {
            "contract": REVISION_MANIFEST_CONTRACT,
            "schemaVersion": REVIEWED_PACKET_SCHEMA_VERSION,
            "reviewStoreContract": REVIEW_STORE_CONTRACT,
            "sideIdentity": side,
            "revisionId": revision_id,
            "serverCreatedAtUtc": created,
            "previousRevisionHash": previous_hash,
            "revisionHash": packet["revisionHash"],
            "reviewedPacketFile": "reviewed_packet.json",
            "reviewedPacketHash": packet["reviewedPacketHash"],
            "reviewedPacketSha256": _sha256_file(packet_path),
            "blankPacketFile": side_data["blankPacketFile"],
            "blankPacketSha256": side_data["blankPacketSha256"],
            "identityIntegrityManifestFile": side_data["identityIntegrityManifestFile"],
            "identityIntegrityManifestSha256": side_data["identityIntegrityManifestSha256"],
            "identityAuditContract": side_data["identityAuditContract"],
            "identityAuditVersion": side_data["identityAuditVersion"],
            "identityAuditSha256": side_data["identityAuditSha256"],
            "founderCompletionStatus": packet["founderCompletionStatus"],
            "completeness": packet["completeness"],
            "guardrails": packet["guardrails"],
        }
        _write_json(manifest_path, manifest)
        _write_json(
            completeness_path,
            {
                "contract": "FOUNDER_REVIEW_COMPLETENESS_REPORT_V1",
                "reviewStoreContract": REVIEW_STORE_CONTRACT,
                "sideIdentity": side,
                "revisionId": revision_id,
                "revisionHash": packet["revisionHash"],
                "reviewedPacketHash": packet["reviewedPacketHash"],
                "founderCompletionStatus": packet["founderCompletionStatus"],
                "counts": packet["completeness"],
            },
        )
        _write_json(
            status_path,
            {
                "contract": "FOUNDER_REVIEW_PACKET_STATUS_V1",
                "reviewStoreContract": REVIEW_STORE_CONTRACT,
                "sideIdentity": side,
                "revisionId": revision_id,
                "revisionHash": packet["revisionHash"],
                "reviewedPacketHash": packet["reviewedPacketHash"],
                "founderCompletionStatus": packet["founderCompletionStatus"],
                "counts": packet["completeness"],
                "admission": "NOT_CONNECTED_TO_CATALOGUE",
                "guardrails": packet["guardrails"],
            },
        )
        markdown_path.write_text(_markdown_render(side, side_data, packet), encoding="utf-8")
        os.replace(temporary_dir, final_dir)
        store_relative = f"revisions/{side}/{revision_id}"
        pointer = {
            "contract": CURRENT_POINTER_CONTRACT,
            "schemaVersion": REVIEWED_PACKET_SCHEMA_VERSION,
            "reviewStoreContract": REVIEW_STORE_CONTRACT,
            "sideIdentity": side,
            "revisionId": revision_id,
            "serverCreatedAtUtc": created,
            "previousRevisionHash": previous_hash,
            "revisionHash": packet["revisionHash"],
            "reviewedPacketHash": packet["reviewedPacketHash"],
            "revisionDirectory": store_relative,
        }
        # The pointer is the sole publication step. A failed write leaves the
        # prior pointer authoritative; the complete orphan revision is
        # harmless and can be reconciled later.
        _atomic_write_json(paths["current"], pointer)
    except Exception:
        if temporary_dir.exists():
            import shutil

            shutil.rmtree(temporary_dir, ignore_errors=True)
        raise

    revision_dir = final_dir
    return {
        "reviewedPacketFile": f"{store_relative}/reviewed_packet.json",
        "reviewedPacketSha256": _sha256_file(revision_dir / "reviewed_packet.json"),
        "reviewedPacketHash": packet["reviewedPacketHash"],
        "reviewedManifestFile": f"{store_relative}/manifest.json",
        "reviewedManifestSha256": _sha256_file(revision_dir / "manifest.json"),
        "completenessFile": f"{store_relative}/completeness.json",
        "statusFile": f"{store_relative}/status.json",
        "markdownFile": f"{store_relative}/reviewed.md",
        "ephemerisVersion": packet["ephemerisVersion"],
        "ephemerisVersionProvenance": packet["ephemerisVersionProvenance"],
        "founderCompletionStatus": packet["founderCompletionStatus"],
        "counts": packet["completeness"],
        "revisionId": revision_id,
        "serverCreatedAtUtc": created,
        "previousRevisionHash": previous_hash,
        "revisionHash": packet["revisionHash"],
        "reviewStoreContract": REVIEW_STORE_CONTRACT,
    }


def build_founder_review_workbench(
    project_root: Path,
    requested_side: str | None = None,
    review_root: Path | None = None,
    expected_audit_sha256: str = IDENTITY_AUDIT_EXPECTED_SHA256,
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    durable_root = review_store_root(project_root, review_root)
    sides = (requested_side,) if requested_side else SIDES
    side_payloads: list[dict[str, Any]] = []
    for side in sides:
        side_data = _validate_side_inputs(
            project_root,
            side,
            expected_audit_sha256=expected_audit_sha256,
            durable_root=durable_root,
        )
        current = _load_current_revision(side_data, durable_root)
        rows = current["rows"] if current else side_data["rows"]
        counts = _completeness(rows)
        side_payloads.append(
            {
                **side_data,
                "rows": rows,
                "founderCompletionStatus": _status_for(rows),
                "completeness": counts,
                "reviewedPacketHash": current["packet"].get("reviewedPacketHash") if current else None,
                "currentRevisionId": current["revisionId"] if current else None,
                "currentRevisionHash": current["revisionHash"] if current else None,
                "previousRevisionHash": current["packet"].get("previousRevisionHash") if current else None,
                "reviewStoreContract": REVIEW_STORE_CONTRACT,
            }
        )
    return {
        "contract": WORKBENCH_CONTRACT,
        "schemaVersion": REVIEWED_PACKET_SCHEMA_VERSION,
        "toolVersion": TOOL_VERSION,
        "reviewStoreContract": REVIEW_STORE_CONTRACT,
        "sides": side_payloads,
        "allowedFounderPolarityDecisions": list(DECISIONS),
        "allowedEvidenceClassifications": list(EVIDENCE_CLASSIFICATIONS),
        "reviewStatuses": list(REVIEW_STATUSES),
        "guardrails": {
            "blankPacketsReadOnly": True,
            "durableReviewStore": True,
            "priceDataRead": False,
            "sbcRead": False,
            "llmRead": False,
            "catalogueAdmission": False,
            "directionalWaveRendered": False,
            "executionAllowed": False,
        },
    }


def export_founder_review_packet(
    project_root: Path,
    payload: dict[str, Any],
    review_root: Path | None = None,
    expected_audit_sha256: str = IDENTITY_AUDIT_EXPECTED_SHA256,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise FounderReviewIntegrityError("Founder review export payload must be an object")
    side = payload.get("side")
    if type(side) is not str or side not in SIDES:
        raise FounderReviewIntegrityError(f"Unsupported founder-review side: {side}")
    base_revision_hash = payload.get("baseRevisionHash")
    if base_revision_hash is not None and type(base_revision_hash) is not str:
        raise FounderReviewIntegrityError("baseRevisionHash must be a string or null")
    project_root = Path(project_root).resolve()
    durable_root = review_store_root(project_root, review_root)
    with _store_lock(durable_root, side):
        side_data = _validate_side_inputs(
            project_root,
            side,
            expected_audit_sha256=expected_audit_sha256,
            durable_root=durable_root,
        )
        current = _load_current_revision(side_data, durable_root)
        current_hash = current["revisionHash"] if current else None
        if base_revision_hash != current_hash:
            raise FounderReviewRevisionConflictError(
                side,
                base_revision_hash,
                current_hash,
                current["revisionId"] if current else None,
            )
        existing_rows = current["rows"] if current else None
        server_now = _next_server_timestamp(
            current["packet"].get("serverCreatedAtUtc") if current else None
        )
        rows = _validate_submitted_rows(
            side_data,
            payload.get("rows"),
            existing_rows=existing_rows,
            server_now=server_now,
        )
        return _persist_revision(side_data, rows, durable_root, current)
