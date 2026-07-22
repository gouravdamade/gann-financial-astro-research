from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from sbc.grid import CERTIFIED_LAYER_VALUES

from .models import InstrumentIdentity, TargetMapping
from .scoring import resolve_time_valid_targets


CONNECTOR_CONTRACT = "SBC_IMMUTABLE_SNAPSHOT_TARGET_CONNECTOR_V1"
SNAPSHOT_CONTRACT = "SBC_CHAKRA_LAB_SNAPSHOT_V1"
LAYER_TARGET_TYPES = {
    "NAME_INITIAL": "akshara",
    "NAKSHATRA": "nakshatra",
    "RASHI": "rashi",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _aware_utc(value: Any, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} is not a valid ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _machine_token(value: Any) -> str:
    return "_".join(str(value).strip().upper().replace("-", " ").split())


def _snapshot_dict(snapshot: Any) -> dict[str, Any]:
    if isinstance(snapshot, Mapping):
        value = dict(snapshot)
    elif callable(getattr(snapshot, "to_dict", None)):
        value = snapshot.to_dict()
    else:
        raise ValueError("snapshot must be a ChakraLabSnapshot or serialized mapping")
    return json.loads(_canonical_json(value))


def _snapshot_targets(snapshot: Mapping[str, Any]) -> tuple["SnapshotTarget", ...]:
    targets: list[SnapshotTarget] = []
    for context in snapshot.get("target_context") or []:
        layer = str(context.get("layer") or "").strip().upper()
        target_type = LAYER_TARGET_TYPES.get(layer)
        if target_type is None:
            continue
        for raw_value in context.get("values") or []:
            value = _machine_token(raw_value)
            if value:
                if value not in CERTIFIED_LAYER_VALUES[layer]:
                    raise ValueError(
                        f"snapshot contains uncertified {layer} value: {value}"
                    )
                targets.append(
                    SnapshotTarget(
                        layer=layer,
                        target_type=target_type,
                        target_value=value,
                    )
                )
    unique = {
        (item.layer, item.target_type, item.target_value): item for item in targets
    }
    return tuple(unique[key] for key in sorted(unique))


def _source_ids(mapping: TargetMapping, snapshot: Mapping[str, Any]) -> tuple[str, ...]:
    values = [str(item) for item in snapshot.get("source_ids") or [] if str(item)]
    values.extend(
        citation.source_id for citation in mapping.provenance if citation.source_id
    )
    return tuple(dict.fromkeys(values))


@dataclass(frozen=True)
class SnapshotTarget:
    layer: str
    target_type: str
    target_value: str


@dataclass(frozen=True)
class UnscoredIdentityMatch:
    match_id: str
    instrument_id: str
    snapshot_id: str
    timestamp_utc: datetime
    layer: str
    target_type: str
    target_value: str
    mapping_method: str
    mapping_confidence: float
    mapping_review_status: str
    source_ids: tuple[str, ...]
    status: str = "matched_unscored"
    signed_value: None = None
    scoring_allowed: bool = False
    contribution_emission_allowed: bool = False
    execution_allowed: bool = False


@dataclass(frozen=True)
class SnapshotConnectorResult:
    contract: str
    connector_version: int
    connector_run_id: str
    source_snapshot_sha256: str
    snapshot_id: str
    snapshot_as_of_utc: datetime
    evidence_cutoff_utc: datetime
    instrument_id: str
    identity_gate_status: str
    accepted_target_count: int
    snapshot_target_count: int
    matches: tuple[UnscoredIdentityMatch, ...]
    blockers: tuple[str, ...]
    scoring_allowed: bool = False
    contribution_emission_allowed: bool = False
    financially_validated: bool = False
    auto_suggest_allowed: bool = False
    ml_training_allowed: bool = False
    mt5_input_allowed: bool = False
    execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["snapshot_as_of_utc"] = self.snapshot_as_of_utc.isoformat()
        value["evidence_cutoff_utc"] = self.evidence_cutoff_utc.isoformat()
        for index, match in enumerate(self.matches):
            value["matches"][index]["timestamp_utc"] = match.timestamp_utc.isoformat()
        return value


def connect_snapshot_to_identity(
    snapshot: Any,
    identity: InstrumentIdentity,
) -> SnapshotConnectorResult:
    value = _snapshot_dict(snapshot)
    if value.get("contract") != SNAPSHOT_CONTRACT:
        raise ValueError(f"snapshot contract must be {SNAPSHOT_CONTRACT}")
    snapshot_id = str(value.get("snapshot_id") or "").strip().upper()
    if not re.fullmatch(r"[0-9A-F]{64}", snapshot_id):
        raise ValueError("snapshot_id must be a 64-character uppercase SHA-256")
    as_of = _aware_utc(value.get("as_of_utc"), "snapshot as_of_utc")
    cutoff = _aware_utc(value.get("evidence_cutoff_utc"), "evidence_cutoff_utc")
    if cutoff > as_of:
        raise ValueError("snapshot evidence cutoff cannot be later than its as-of time")
    guardrails = value.get("guardrails") or {}
    required_guardrails = {
        "read_only": True,
        "timestamp_safe": True,
        "no_lookahead": True,
        "execution_allowed": False,
        "financially_validated": False,
        "guidance_only": True,
    }
    wrong = [
        name
        for name, expected in required_guardrails.items()
        if guardrails.get(name) is not expected
    ]
    if wrong:
        raise ValueError("snapshot guardrails are unsafe or incomplete: " + ", ".join(wrong))

    source_snapshot_sha = _fingerprint(value)
    snapshot_targets = _snapshot_targets(value)
    accepted_targets = resolve_time_valid_targets(identity, as_of)
    matches: list[UnscoredIdentityMatch] = []
    for mapping in accepted_targets:
        target_value = _machine_token(mapping.target_value)
        for target in snapshot_targets:
            if (
                target.target_type != mapping.target_type
                or target.target_value != target_value
            ):
                continue
            match_identity = {
                "contract": CONNECTOR_CONTRACT,
                "snapshotId": snapshot_id,
                "instrumentId": identity.instrument_id,
                "timestampUtc": as_of.isoformat(),
                "layer": target.layer,
                "targetType": target.target_type,
                "targetValue": target.target_value,
                "mappingMethod": mapping.mapping_method,
                "mappingConfidence": mapping.confidence,
                "sourceIds": _source_ids(mapping, value),
            }
            matches.append(
                UnscoredIdentityMatch(
                    match_id=_fingerprint(match_identity),
                    instrument_id=identity.instrument_id,
                    snapshot_id=snapshot_id,
                    timestamp_utc=as_of,
                    layer=target.layer,
                    target_type=target.target_type,
                    target_value=target.target_value,
                    mapping_method=mapping.mapping_method,
                    mapping_confidence=mapping.confidence,
                    mapping_review_status=mapping.review_status,
                    source_ids=_source_ids(mapping, value),
                )
            )

    deduplicated = {item.match_id: item for item in matches}
    ordered_matches = tuple(deduplicated[key] for key in sorted(deduplicated))
    blockers = [
        "No source-certified snapshot contribution profile was supplied; signed polarity and numeric magnitude remain unknown.",
        "Financial validation is not registered; matches cannot enter Auto Suggest, ML training, MT5, or execution.",
    ]
    if not accepted_targets:
        identity_status = "blocked_no_time_valid_human_accepted_targets"
        blockers.insert(
            0,
            "The identity has no time-valid human-accepted akshara, nakshatra, or rashi mapping.",
        )
    elif not ordered_matches:
        identity_status = "accepted_identity_no_snapshot_match"
    else:
        identity_status = "accepted_identity_exact_snapshot_match_unscored"
    run_identity = {
        "contract": CONNECTOR_CONTRACT,
        "sourceSnapshotSha256": source_snapshot_sha,
        "snapshotId": snapshot_id,
        "instrumentId": identity.instrument_id,
        "acceptedTargets": [
            {
                "type": item.target_type,
                "value": _machine_token(item.target_value),
                "method": item.mapping_method,
                "confidence": item.confidence,
            }
            for item in accepted_targets
        ],
        "matchIds": [item.match_id for item in ordered_matches],
    }
    return SnapshotConnectorResult(
        contract=CONNECTOR_CONTRACT,
        connector_version=1,
        connector_run_id=_fingerprint(run_identity),
        source_snapshot_sha256=source_snapshot_sha,
        snapshot_id=snapshot_id,
        snapshot_as_of_utc=as_of,
        evidence_cutoff_utc=cutoff,
        instrument_id=identity.instrument_id,
        identity_gate_status=identity_status,
        accepted_target_count=len(accepted_targets),
        snapshot_target_count=len(snapshot_targets),
        matches=ordered_matches,
        blockers=tuple(blockers),
    )
