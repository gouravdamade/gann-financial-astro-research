"""XE3 outcome-blind chart-conditioned sign admission.

This module is intentionally isolated from price, MT5, Fields, SBC, LLM, Auto
Suggest, and execution code.  It turns only packet-verified founder decisions
into append-only research revisions, a signed-evidence ledger, and a later
preregistration candidate.  It never infers a sign from astronomy.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from founder_review_workbench import (
    DECISIONS,
    EVIDENCE_CLASSIFICATIONS,
    REVIEWABLE_IDENTITY_STATUS,
    SIDES,
    FounderReviewIntegrityError,
    _completeness,
    _status_for,
    _validate_side_inputs,
)
from xe2_scoped_evidence_service import (
    PROFILE_ID as XE2_PROFILE_ID,
    TRANSFORMS as XE2_TRANSFORMS,
    _fixture as load_xe2_fixture,
    _profile as load_xe2_profile,
    apply_xe2_causal_transform,
)


WORKBENCH_CONTRACT = "XE3_OUTCOME_BLIND_SIGN_ADMISSION_WORKBENCH_V1"
ADMISSION_CONTRACT = "OUTCOME_BLIND_CHART_CONDITIONED_SIGN_ADMISSION_V1"
REVISION_CONTRACT = "XE3_OUTCOME_BLIND_REVIEW_REVISION_V1"
LEDGER_CONTRACT = "XE3_SIGNED_EVIDENCE_LEDGER_V1"
PROJECTION_CONTRACT = "XE3_SIGN_SCALAR_PROJECTION_V1"
PREREGISTRATION_CONTRACT = "XE3_PREREGISTERED_CAUSAL_MODIFIER_TRIAL_V1"
PROFILE_ID = "XE3_OUTCOME_BLIND_CHART_CONDITIONED_SIGN_ADMISSION_V1"
TOOL_VERSION = "xe3_outcome_blind_sign_admission_v1"
DATASET_STATUS = "TOUCHED_DEV"

GUARDRAILS = {
    "experimental": True,
    "classicalDoctrine": False,
    "priceDataRead": False,
    "priceOutcomeRead": False,
    "liveMt5Read": False,
    "fieldsRead": False,
    "sbcRead": False,
    "autoSuggestRead": False,
    "llmPolarityInference": False,
    "marketDirectionInferred": False,
    "modeOnePromotion": False,
    "executionAllowed": False,
    "automaticOrderPlacement": False,
    "financiallyValidated": False,
}


class Xe3SignAdmissionIntegrityError(ValueError):
    """Raised when XE3 evidence cannot be proven outcome-blind and immutable."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest().upper()


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise Xe3SignAdmissionIntegrityError(f"Required XE3 record is missing: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise Xe3SignAdmissionIntegrityError(f"Invalid XE3 JSON record: {path.name}") from exc
    if not isinstance(value, dict):
        raise Xe3SignAdmissionIntegrityError(f"XE3 JSON record must be an object: {path.name}")
    return value


def _write_json_once(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError as exc:
        raise Xe3SignAdmissionIntegrityError(f"XE3 immutable record already exists: {path.name}") from exc


def _write_index(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _store_root(project_root: Path, storage_root: Path | None = None) -> Path:
    if storage_root is not None:
        return Path(storage_root).expanduser().resolve()
    configured = os.environ.get("GANN_ASTRO_XE3_SIGN_ADMISSION_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(r"D:\GannFinancialAstro\app_data\xe3_outcome_blind_sign_admission")


def _index_path(store_root: Path) -> Path:
    return store_root / "index.json"


def _load_index(store_root: Path) -> dict[str, Any]:
    path = _index_path(store_root)
    if not path.exists():
        return {"contract": "XE3_SIGN_ADMISSION_STORE_INDEX_V1", "latestRevisionBySide": {}, "latestLedgerHash": None, "latestPrerecordHash": None}
    value = _read_json(path)
    if value.get("contract") != "XE3_SIGN_ADMISSION_STORE_INDEX_V1":
        raise Xe3SignAdmissionIntegrityError("XE3 admission store index contract is not recognized")
    return value


def _revision_path(store_root: Path, side: str, revision_hash: str) -> Path:
    return store_root / "revisions" / side / f"{revision_hash}.json"


def _ledger_path(store_root: Path, ledger_hash: str) -> Path:
    return store_root / "ledgers" / f"{ledger_hash}.json"


def _freeze_path(store_root: Path, preregistration_hash: str) -> Path:
    return store_root / "preregistrations" / f"{preregistration_hash}.json"


def _blank_review() -> dict[str, Any]:
    return {
        "decision": None,
        "evidenceClassification": None,
        "reasoning": "",
        "rejectionReason": "",
        "reviewer": "",
        "reviewTimestampUtc": None,
        "sourceReferences": [],
        "outcomeBlindAttestation": False,
        "priceDataRead": False,
    }


def _base_rows(project_root: Path, side: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        side_data = _validate_side_inputs(project_root, side)
    except FounderReviewIntegrityError as exc:
        raise Xe3SignAdmissionIntegrityError(str(exc)) from exc
    rows: list[dict[str, Any]] = []
    for source_row in side_data["rows"]:
        if not source_row.get("eligible") or source_row.get("identityStatus") != REVIEWABLE_IDENTITY_STATUS:
            raise Xe3SignAdmissionIntegrityError(f"{side} packet contains a non-reviewable event")
        rows.append(
            {
                "eventIdentity": copy.deepcopy(source_row["eventIdentity"]),
                "identityStatus": source_row["identityStatus"],
                "motionPhaseAtExact": copy.deepcopy(source_row.get("motionPhaseAtExact")),
                "review": _blank_review(),
            }
        )
    return side_data, rows


def _validate_revision(project_root: Path, side: str, revision: Mapping[str, Any]) -> dict[str, Any]:
    side_data, base_rows = _base_rows(project_root, side)
    if revision.get("contract") != REVISION_CONTRACT or revision.get("sideIdentity") != side:
        raise Xe3SignAdmissionIntegrityError(f"{side} XE3 review revision has an invalid contract or side")
    body = copy.deepcopy(dict(revision))
    recorded_hash = body.pop("reviewRevisionHash", None)
    body["reviewRevisionHash"] = None
    if not isinstance(recorded_hash, str) or recorded_hash != _sha256(body):
        raise Xe3SignAdmissionIntegrityError(f"{side} XE3 review revision hash is invalid")
    if revision.get("blankPacketSha256") != side_data["blankPacketSha256"]:
        raise Xe3SignAdmissionIntegrityError(f"{side} XE3 review revision references a different blank packet")
    if revision.get("identityIntegrityManifestSha256") != side_data["identityIntegrityManifestSha256"]:
        raise Xe3SignAdmissionIntegrityError(f"{side} XE3 review revision references a different identity manifest")
    rows = revision.get("rows")
    if not isinstance(rows, list) or len(rows) != len(base_rows):
        raise Xe3SignAdmissionIntegrityError(f"{side} XE3 review revision row set is incomplete")
    normalized = _normalize_rows(base_rows, rows, reviewer=None, outcome_blind_attestation=None, preserve_timestamps=True)
    return {**dict(revision), "rows": normalized}


def _latest_revision(project_root: Path, store_root: Path, side: str) -> dict[str, Any] | None:
    index = _load_index(store_root)
    latest = index.get("latestRevisionBySide", {}).get(side)
    if latest is None:
        return None
    if not isinstance(latest, str):
        raise Xe3SignAdmissionIntegrityError(f"{side} XE3 latest revision pointer is invalid")
    revision = _read_json(_revision_path(store_root, side, latest))
    return _validate_revision(project_root, side, revision)


def _require_string(value: Any, label: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise Xe3SignAdmissionIntegrityError(f"{label} is required")
    return result


def _normalize_source_references(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise Xe3SignAdmissionIntegrityError("SOURCE_BACKED_CLASSICAL_CANDIDATE requires at least one exact source reference")
    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise Xe3SignAdmissionIntegrityError("XE3 source references must be objects")
        result.append({key: _require_string(item.get(key), f"Source reference {key}") for key in ("sourceId", "edition", "locator", "connection")})
    return result


def _normalize_review(
    review: Any,
    *,
    reviewer: str | None,
    outcome_blind_attestation: bool | None,
    preserve_timestamps: bool,
) -> dict[str, Any]:
    if not isinstance(review, Mapping):
        raise Xe3SignAdmissionIntegrityError("XE3 review fields are missing")
    decision = review.get("decision")
    if decision is None:
        if any(review.get(key) not in (None, "", [], False) for key in ("evidenceClassification", "reasoning", "rejectionReason", "sourceReferences")):
            raise Xe3SignAdmissionIntegrityError("A blank XE3 review cannot contain classification, reasoning, or source references")
        return _blank_review()
    if decision not in DECISIONS:
        raise Xe3SignAdmissionIntegrityError(f"Unsupported XE3 founder decision: {decision}")
    selected_reviewer = _require_string(review.get("reviewer") or reviewer, "Reviewer")
    attested = bool(review.get("outcomeBlindAttestation")) if outcome_blind_attestation is None else bool(outcome_blind_attestation)
    if not attested:
        raise Xe3SignAdmissionIntegrityError("Outcome-blind attestation is required before saving a sign decision")
    if review.get("priceDataRead") not in (None, False):
        raise Xe3SignAdmissionIntegrityError("XE3 review rejects any price-data-read claim")
    normalized = {
        **_blank_review(),
        "decision": decision,
        "reviewer": selected_reviewer,
        "outcomeBlindAttestation": True,
        "priceDataRead": False,
    }
    supplied_timestamp = review.get("reviewTimestampUtc")
    if preserve_timestamps and isinstance(supplied_timestamp, str) and supplied_timestamp.endswith("Z"):
        normalized["reviewTimestampUtc"] = supplied_timestamp
    else:
        normalized["reviewTimestampUtc"] = _now_utc()
    if decision == "REJECT_EVENT_IDENTITY":
        normalized["rejectionReason"] = _require_string(review.get("rejectionReason"), "Founder rejection reason")
        normalized["reasoning"] = str(review.get("reasoning") or "").strip()
        return normalized

    classification = review.get("evidenceClassification")
    if classification not in EVIDENCE_CLASSIFICATIONS:
        raise Xe3SignAdmissionIntegrityError("Every non-rejected XE3 decision requires an evidence classification")
    normalized["evidenceClassification"] = classification
    normalized["reasoning"] = str(review.get("reasoning") or "").strip()
    if decision in ("SUPPORTIVE", "ADVERSE", "MIXED", "NEUTRAL") and not normalized["reasoning"]:
        raise Xe3SignAdmissionIntegrityError(f"{decision} requires founder reasoning")
    if classification == "SOURCE_BACKED_CLASSICAL_CANDIDATE":
        normalized["sourceReferences"] = _normalize_source_references(review.get("sourceReferences"))
    return normalized


def _normalize_rows(
    base_rows: list[dict[str, Any]],
    submitted: Any,
    *,
    reviewer: str | None,
    outcome_blind_attestation: bool | None,
    preserve_timestamps: bool,
) -> list[dict[str, Any]]:
    if not isinstance(submitted, list) or len(submitted) != len(base_rows):
        raise Xe3SignAdmissionIntegrityError("XE3 review submission must contain the complete approved packet row set")
    expected = {row["eventIdentity"]["eventId"]: row for row in base_rows}
    normalized_by_id: dict[str, dict[str, Any]] = {}
    for candidate in submitted:
        if not isinstance(candidate, Mapping) or not isinstance(candidate.get("eventIdentity"), Mapping):
            raise Xe3SignAdmissionIntegrityError("XE3 review row is missing immutable event identity")
        event = candidate["eventIdentity"]
        event_id = event.get("eventId")
        if not isinstance(event_id, str) or event_id not in expected or event_id in normalized_by_id:
            raise Xe3SignAdmissionIntegrityError("XE3 review contains an unknown or duplicate event")
        expected_row = expected[event_id]
        if dict(event) != expected_row["eventIdentity"]:
            raise Xe3SignAdmissionIntegrityError(f"XE3 review attempted to mutate event identity: {event_id}")
        normalized_by_id[event_id] = {
            "eventIdentity": copy.deepcopy(expected_row["eventIdentity"]),
            "identityStatus": expected_row["identityStatus"],
            "motionPhaseAtExact": copy.deepcopy(expected_row.get("motionPhaseAtExact")),
            "review": _normalize_review(
                candidate.get("review"),
                reviewer=reviewer,
                outcome_blind_attestation=outcome_blind_attestation,
                preserve_timestamps=preserve_timestamps,
            ),
        }
    return [normalized_by_id[row["eventIdentity"]["eventId"]] for row in base_rows]


def _completion(rows: list[dict[str, Any]]) -> dict[str, Any]:
    legacy_rows = [
        {
            "eligible": True,
            "founderReview": {"reviewedPolarity": row["review"]["decision"], "evidenceClassification": row["review"]["evidenceClassification"]},
        }
        for row in rows
    ]
    return {"status": _status_for(legacy_rows), "counts": _completeness(legacy_rows)}


def _review_projection(review: Mapping[str, Any]) -> dict[str, Any]:
    decision = review.get("decision")
    mapping = {
        "SUPPORTIVE": ("SIGNED_KNOWN", 1.0),
        "ADVERSE": ("SIGNED_KNOWN", -1.0),
        "NEUTRAL": ("EXPLICIT_NEUTRAL", 0.0),
        "MIXED": ("MIXED_NOT_PROJECTABLE", None),
        "UNKNOWN_MORE_EVIDENCE_REQUIRED": ("UNKNOWN_MORE_EVIDENCE_REQUIRED", None),
        "REJECT_EVENT_IDENTITY": ("REJECTED_EVENT_IDENTITY", None),
    }
    if decision is None:
        return {"mappingVersion": PROJECTION_CONTRACT, "status": "NO_REVIEW_DECISION", "value": None}
    status, value = mapping[decision]
    return {"mappingVersion": PROJECTION_CONTRACT, "status": status, "value": value}


def _causal_event_id(side: str, event_hash: str, xe2_by_hash: Mapping[str, Mapping[str, Any]]) -> str:
    matched = xe2_by_hash.get(event_hash)
    if matched:
        return str(matched["causalEventId"])
    return f"XE3_CAUSAL_{side}_{event_hash}"


def _xe2_event_by_hash(project_root: Path) -> dict[str, Mapping[str, Any]]:
    return {str(event["eventIdentity"]["eventHash"]): event for event in load_xe2_fixture(project_root)["events"]}


def _ledger_from_revisions(project_root: Path, store_root: Path) -> dict[str, Any]:
    xe2_by_hash = _xe2_event_by_hash(project_root)
    entries: list[dict[str, Any]] = []
    side_states: dict[str, Any] = {}
    seen: set[tuple[str, str]] = set()
    for side in SIDES:
        side_data, base_rows = _base_rows(project_root, side)
        revision = _latest_revision(project_root, store_root, side)
        rows = revision["rows"] if revision else base_rows
        completion = _completion(rows)
        side_states[side] = {
            "blankPacketSha256": side_data["blankPacketSha256"],
            "identityIntegrityManifestSha256": side_data["identityIntegrityManifestSha256"],
            "reviewRevisionHash": revision.get("reviewRevisionHash") if revision else None,
            "completion": completion,
        }
        for row in rows:
            review = row["review"]
            if review["decision"] is None:
                continue
            event = row["eventIdentity"]
            projection = _review_projection(review)
            causal_event_id = _causal_event_id(side, event["eventHash"], xe2_by_hash)
            key = (side, causal_event_id)
            if key in seen:
                raise Xe3SignAdmissionIntegrityError(f"Duplicate XE3 causal event identity: {side}/{causal_event_id}")
            seen.add(key)
            xe2_event = xe2_by_hash.get(event["eventHash"])
            modifier_binding = {
                "status": "BOUND_XE2_FROZEN_COHORT" if xe2_event else "NOT_IN_XE2_FROZEN_COHORT",
                "causalEventId": causal_event_id if xe2_event else None,
                "rawMoonSpeedDegPerDay": xe2_event["eventIdentity"].get("speedDegPerDay") if xe2_event else None,
                "motionPhaseAtExact": xe2_event["eventIdentity"].get("motionPhaseAtExact") if xe2_event else (row.get("motionPhaseAtExact") or {}).get("phase"),
            }
            entry = {
                "contract": ADMISSION_CONTRACT,
                "sourceReviewedPacketHash": revision.get("reviewRevisionHash") if revision else None,
                "eventHash": event["eventHash"],
                "eventId": event["eventId"],
                "causalEventId": causal_event_id,
                "sideIdentity": side,
                "chartId": event["chartId"],
                "chartHypothesisId": event["chartHypothesisId"],
                "exactUtc": event["exactUtc"],
                "identityStatus": row["identityStatus"],
                "review": copy.deepcopy(review),
                "scalarProjection": projection,
                "modifierBinding": modifier_binding,
                "contributionIncluded": projection["status"] in {"SIGNED_KNOWN", "EXPLICIT_NEUTRAL"},
            }
            entry["admissionHash"] = _sha256({key: value for key, value in entry.items() if key != "admissionHash"})
            entries.append(entry)
    entries.sort(key=lambda item: (item["exactUtc"], item["sideIdentity"], item["causalEventId"]))
    ledger = {
        "contract": LEDGER_CONTRACT,
        "profileId": PROFILE_ID,
        "datasetStatus": DATASET_STATUS,
        "outcomeContractStatus": "NOT_YET_FOUNDER_APPROVED",
        "sideStates": side_states,
        "entries": entries,
        "guardrails": copy.deepcopy(GUARDRAILS),
        "ledgerHash": None,
    }
    ledger["ledgerHash"] = _sha256(ledger)
    return ledger


def _persist_ledger(store_root: Path, ledger: dict[str, Any]) -> dict[str, Any]:
    path = _ledger_path(store_root, ledger["ledgerHash"])
    if not path.exists():
        _write_json_once(path, ledger)
    return ledger


def _latest_ledger(project_root: Path, store_root: Path) -> dict[str, Any]:
    ledger = _persist_ledger(store_root, _ledger_from_revisions(project_root, store_root))
    index = _load_index(store_root)
    index["latestLedgerHash"] = ledger["ledgerHash"]
    _write_index(_index_path(store_root), index)
    return ledger


def build_xe3_workbench(project_root: Path, *, storage_root: Path | None = None, requested_side: str | None = None) -> dict[str, Any]:
    store = _store_root(project_root, storage_root)
    selected_sides = (requested_side,) if requested_side else SIDES
    if any(side not in SIDES for side in selected_sides):
        raise Xe3SignAdmissionIntegrityError("XE3 side selector accepts only USD or JPY")
    payload_sides: list[dict[str, Any]] = []
    for side in selected_sides:
        side_data, base_rows = _base_rows(project_root, side)
        revision = _latest_revision(project_root, store, side)
        rows = revision["rows"] if revision else base_rows
        completion = _completion(rows)
        payload_sides.append(
            {
                "sideIdentity": side,
                "instrumentIdentity": side_data["instrumentIdentity"],
                "chartId": side_data["chartId"],
                "chartHypothesisId": side_data["chartHypothesisId"],
                "blankPacketFile": side_data["blankPacketFile"],
                "blankPacketSha256": side_data["blankPacketSha256"],
                "identityIntegrityManifestFile": side_data["identityIntegrityManifestFile"],
                "identityIntegrityManifestSha256": side_data["identityIntegrityManifestSha256"],
                "latestReviewRevisionHash": revision.get("reviewRevisionHash") if revision else None,
                "completion": completion,
                "rows": rows,
            }
        )
    ledger = _latest_ledger(project_root, store)
    return {
        "contract": WORKBENCH_CONTRACT,
        "profileId": PROFILE_ID,
        "toolVersion": TOOL_VERSION,
        "datasetStatus": DATASET_STATUS,
        "datasetLabel": "TOUCHED DEV - OUTCOME-BLIND SIGN REVIEW ONLY",
        "allowedDecisions": list(DECISIONS),
        "allowedEvidenceClassifications": list(EVIDENCE_CLASSIFICATIONS),
        "sides": payload_sides,
        "signedEvidenceStatus": _signed_evidence_status(ledger),
        "ledgerHash": ledger["ledgerHash"],
        "guardrails": copy.deepcopy(GUARDRAILS),
    }


def save_xe3_review_revision(project_root: Path, payload: Mapping[str, Any], *, storage_root: Path | None = None) -> dict[str, Any]:
    allowed = {"side", "baseRevisionHash", "reviewer", "outcomeBlindAttestation", "rows"}
    unexpected = sorted(set(payload) - allowed)
    if unexpected:
        raise Xe3SignAdmissionIntegrityError(f"XE3 review request contains unsupported fields: {', '.join(unexpected)}")
    side = payload.get("side")
    if side not in SIDES:
        raise Xe3SignAdmissionIntegrityError("XE3 review save requires USD or JPY side")
    store = _store_root(project_root, storage_root)
    side_data, base_rows = _base_rows(project_root, side)
    latest = _latest_revision(project_root, store, side)
    expected_parent = latest.get("reviewRevisionHash") if latest else None
    if payload.get("baseRevisionHash") != expected_parent:
        raise Xe3SignAdmissionIntegrityError("XE3 review changed elsewhere; refresh before saving")
    reviewer = _require_string(payload.get("reviewer"), "Reviewer")
    rows = _normalize_rows(
        base_rows,
        payload.get("rows"),
        reviewer=reviewer,
        outcome_blind_attestation=payload.get("outcomeBlindAttestation") is True,
        preserve_timestamps=False,
    )
    completion = _completion(rows)
    revision = {
        "contract": REVISION_CONTRACT,
        "profileId": PROFILE_ID,
        "toolVersion": TOOL_VERSION,
        "sideIdentity": side,
        "instrumentIdentity": side_data["instrumentIdentity"],
        "chartId": side_data["chartId"],
        "chartHypothesisId": side_data["chartHypothesisId"],
        "blankPacketFile": side_data["blankPacketFile"],
        "blankPacketSha256": side_data["blankPacketSha256"],
        "identityIntegrityManifestFile": side_data["identityIntegrityManifestFile"],
        "identityIntegrityManifestSha256": side_data["identityIntegrityManifestSha256"],
        "parentRevisionHash": expected_parent,
        "reviewer": reviewer,
        "createdAtUtc": _now_utc(),
        "completion": completion,
        "rows": rows,
        "guardrails": copy.deepcopy(GUARDRAILS),
        "reviewRevisionHash": None,
    }
    revision["reviewRevisionHash"] = _sha256(revision)
    _write_json_once(_revision_path(store, side, revision["reviewRevisionHash"]), revision)
    index = _load_index(store)
    latest_by_side = dict(index.get("latestRevisionBySide") or {})
    latest_by_side[side] = revision["reviewRevisionHash"]
    index["latestRevisionBySide"] = latest_by_side
    _write_index(_index_path(store), index)
    ledger = _latest_ledger(project_root, store)
    return {
        "sideIdentity": side,
        "reviewRevisionHash": revision["reviewRevisionHash"],
        "parentRevisionHash": expected_parent,
        "completion": completion,
        "ledgerHash": ledger["ledgerHash"],
        "signedEvidenceStatus": _signed_evidence_status(ledger),
        "executionAllowed": False,
    }


def _signed_evidence_status(ledger: Mapping[str, Any]) -> str:
    entries = ledger.get("entries", [])
    if not entries:
        return "NONE"
    if any(item.get("scalarProjection", {}).get("status") in {"SIGNED_KNOWN", "EXPLICIT_NEUTRAL"} for item in entries):
        return "PARTIAL"
    return "NON_PROJECTABLE_ONLY"


def build_xe3_signed_ledger(project_root: Path, *, storage_root: Path | None = None) -> dict[str, Any]:
    store = _store_root(project_root, storage_root)
    return _latest_ledger(project_root, store)


def _transform_preview(ledger: Mapping[str, Any], project_root: Path, transform_id: str) -> dict[str, Any]:
    profile = load_xe2_profile()
    transform = next((item for item in profile["transforms"] if item["transformId"] == transform_id), None)
    if transform is None:
        raise Xe3SignAdmissionIntegrityError("XE3 requested an unsupported frozen XE2 transform")
    contributions: list[dict[str, Any]] = []
    for entry in ledger["entries"]:
        projection = entry["scalarProjection"]
        binding = entry["modifierBinding"]
        if projection["status"] not in {"SIGNED_KNOWN", "EXPLICIT_NEUTRAL"}:
            applied = {"value": None, "zSpeed": None, "multiplierOrInteraction": None, "separateChannelValue": None, "contextGate": None, "reason": projection["status"]}
            status = "NOT_PROJECTABLE"
        elif binding["status"] != "BOUND_XE2_FROZEN_COHORT":
            applied = {"value": None, "zSpeed": None, "multiplierOrInteraction": None, "separateChannelValue": None, "contextGate": None, "reason": "MODIFIER_BINDING_NOT_IN_XE2_FROZEN_COHORT"}
            status = "NOT_IN_XE2_FROZEN_COHORT"
        else:
            fixture = load_xe2_fixture(project_root)
            normalization = fixture["normalization"]
            applied = apply_xe2_causal_transform(
                sign_value=projection["value"],
                raw_speed=binding["rawMoonSpeedDegPerDay"],
                motion_phase=binding["motionPhaseAtExact"],
                transform_id=transform_id,
                normalization=normalization,
            )
            status = "ACTIVE" if applied["value"] is not None else "UNKNOWN_TARGET_ONLY"
        contributions.append(
            {
                "causalEventId": entry["causalEventId"],
                "eventId": entry["eventId"],
                "sideIdentity": entry["sideIdentity"],
                "admissionHash": entry["admissionHash"],
                "scalarProjection": projection,
                "modifierBinding": binding,
                "status": status,
                **applied,
            }
        )
    active_values = [float(item["value"]) for item in contributions if item["status"] == "ACTIVE" and isinstance(item.get("value"), (int, float))]
    positive = sum(max(value, 0.0) for value in active_values)
    negative = sum(max(-value, 0.0) for value in active_values)
    activity = positive + negative
    return {
        "transformId": transform_id,
        "transform": transform,
        "profileId": XE2_PROFILE_ID,
        "profileHash": profile["profileHash"],
        "contributions": contributions,
        "signedStateVector": {
            "state": "REAL_SIGNED_EVIDENCE_OUTCOME_NOT_EVALUATED" if activity else "NO_PROJECTABLE_REAL_SIGNED_EVIDENCE",
            "positive": positive,
            "negative": negative,
            "signedRaw": positive - negative if activity else None,
            "signedNormalized": (positive - negative) / activity if activity else None,
            "activity": activity,
            "unknownCount": len([item for item in contributions if item["status"] != "ACTIVE"]),
        },
        "outcomeEvaluationStatus": "BLOCKED",
    }


def build_xe3_transform_comparison(project_root: Path, payload: Mapping[str, Any] | None = None, *, storage_root: Path | None = None) -> dict[str, Any]:
    request = dict(payload or {})
    if set(request) - {"transformId"}:
        raise Xe3SignAdmissionIntegrityError("XE3 transform requests accept only an existing transform identifier")
    ledger = build_xe3_signed_ledger(project_root, storage_root=storage_root)
    return {
        "contract": "XE3_REAL_SIGNED_EVIDENCE_XE2_TRANSFORM_PREVIEW_V1",
        "ledgerHash": ledger["ledgerHash"],
        "datasetStatus": DATASET_STATUS,
        "comparisons": [_transform_preview(ledger, project_root, transform_id) for transform_id in XE2_TRANSFORMS],
        "guardrails": copy.deepcopy(GUARDRAILS),
    }


def _freeze_ready(ledger: Mapping[str, Any]) -> bool:
    states = ledger.get("sideStates", {})
    return all(
        states.get(side, {}).get("completion", {}).get("status") in {"REVIEW_COMPLETE", "REVIEW_COMPLETE_WITH_UNKNOWNS"}
        for side in SIDES
    )


def build_xe3_preregistration_status(project_root: Path, *, storage_root: Path | None = None) -> dict[str, Any]:
    store = _store_root(project_root, storage_root)
    ledger = build_xe3_signed_ledger(project_root, storage_root=store)
    index = _load_index(store)
    frozen_hash = index.get("latestPrerecordHash")
    frozen = _read_json(_freeze_path(store, frozen_hash)) if isinstance(frozen_hash, str) else None
    return {
        "contract": PREREGISTRATION_CONTRACT,
        "status": "FROZEN" if frozen else "NOT_FROZEN",
        "freezeReady": _freeze_ready(ledger),
        "ledgerHash": ledger["ledgerHash"],
        "frozenRecord": frozen,
        "datasetStatus": DATASET_STATUS,
        "outcomeContractStatus": "NOT_YET_FOUNDER_APPROVED",
        "sourceCommitRequired": True,
        "guardrails": copy.deepcopy(GUARDRAILS),
    }


def freeze_xe3_preregistration(project_root: Path, payload: Mapping[str, Any], *, storage_root: Path | None = None) -> dict[str, Any]:
    if set(payload) - {"ledgerHash", "outcomeBlindAttestation", "sourceCommit"}:
        raise Xe3SignAdmissionIntegrityError("XE3 preregistration request contains unsupported fields")
    if payload.get("outcomeBlindAttestation") is not True:
        raise Xe3SignAdmissionIntegrityError("Outcome-blind attestation is required before freezing XE3")
    source_commit = str(payload.get("sourceCommit") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise Xe3SignAdmissionIntegrityError("XE3 preregistration requires the exact packaged 40-character source commit")
    store = _store_root(project_root, storage_root)
    status = build_xe3_preregistration_status(project_root, storage_root=store)
    if status["status"] == "FROZEN":
        return status
    if not status["freezeReady"] or payload.get("ledgerHash") != status["ledgerHash"]:
        raise Xe3SignAdmissionIntegrityError("XE3 preregistration is not ready; terminal reviewed USD and JPY packets are required")
    profile = load_xe2_profile()
    ledger = build_xe3_signed_ledger(project_root, storage_root=store)
    record = {
        "contract": PREREGISTRATION_CONTRACT,
        "profileId": PROFILE_ID,
        "sourceCommit": source_commit,
        "createdAtUtc": _now_utc(),
        "datasetGovernance": {
            "datasetStatus": DATASET_STATUS,
            "outcomeRead": False,
            "outcomeContractStatus": "NOT_YET_FOUNDER_APPROVED",
            "futureHoldoutPolicy": "PREREGISTERED_PROSPECTIVE_PENDING_V1",
        },
        "ledgerHash": ledger["ledgerHash"],
        "sideStates": ledger["sideStates"],
        "includedAdmissions": [
            {key: entry[key] for key in ("admissionHash", "eventHash", "causalEventId", "sideIdentity", "scalarProjection")}
            for entry in ledger["entries"]
        ],
        "xe2ProfileId": XE2_PROFILE_ID,
        "xe2ProfileHash": profile["profileHash"],
        "transforms": profile["transforms"],
        "causalDeduplicationPolicy": "ONE_ENTRY_PER_CAUSAL_EVENT_ID_AND_SIDE_V1",
        "globalModifierDefaultAllowed": False,
        "modifierStackingAllowed": False,
        "unknownMixedNeutralRejectedPolicy": {
            "unknown": "NOT_PROJECTABLE",
            "mixed": "NOT_PROJECTABLE",
            "neutral": "EXPLICIT_ZERO_ONLY",
            "rejected": "EXCLUDED_WITH_AUDIT_RECORD",
        },
        "guardrails": copy.deepcopy(GUARDRAILS),
        "preregistrationHash": None,
    }
    record["preregistrationHash"] = _sha256(record)
    _write_json_once(_freeze_path(store, record["preregistrationHash"]), record)
    index = _load_index(store)
    index["latestPrerecordHash"] = record["preregistrationHash"]
    _write_index(_index_path(store), index)
    return build_xe3_preregistration_status(project_root, storage_root=store)
