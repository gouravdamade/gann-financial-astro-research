from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote


AUDIT_CONTRACT = "GANN_FROZEN_SHADOW_TRIAL_READ_ONLY_AUDIT_V1"
TRIAL_CONTRACT = "GANN_FROZEN_PROSPECTIVE_SHADOW_TRIAL_V1"
LEDGER_CONTRACT = "GANN_APPEND_ONLY_SHADOW_LEDGER_V1"
DECISION_CONTRACT = "GANN_PROSPECTIVE_SHADOW_DECISION_V1"
OUTCOME_CONTRACT = "GANN_PROSPECTIVE_72H_OUTCOME_V1"
GENESIS_HASH = "0" * 64
DEFAULT_DATABASE = Path(
    r"D:\GannFinancialAstro\app_data\gann_aspect_annotations_raman_v2.sqlite"
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _fingerprint(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _aware_timestamp(value: Any, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} is not a valid ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _entry_hash_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract": LEDGER_CONTRACT,
        "sequence": int(row["ledger_sequence"]),
        "entryId": str(row["entry_id"]),
        "entryType": str(row["entry_type"]),
        "shadowId": str(row["shadow_id"]),
        "eventId": str(row["event_id"]),
        "familyKey": str(row["family_key"]),
        "symbol": str(row["symbol"]),
        "timeframe": str(row["timeframe"]),
        "effectiveAtUtc": str(row["effective_at_utc"]),
        "recordedAtUtc": str(row["recorded_at_utc"]),
        "payloadSha256": str(row["payload_sha256"]),
        "previousEntryHash": str(row["previous_entry_hash"]),
    }


def _trial_descriptor(
    decision: Mapping[str, Any], gate_configuration: Mapping[str, Any]
) -> dict[str, Any]:
    packet = decision.get("packet") or {}
    artifact = decision.get("artifactEvidence") or {}
    capture = decision.get("captureKey") or {}
    identity = {
        "contract": TRIAL_CONTRACT,
        "ledgerContract": LEDGER_CONTRACT,
        "decisionContract": decision.get("contract"),
        "packetContract": packet.get("contract"),
        "engineVersion": packet.get("engineVersion"),
        "policyVersion": packet.get("policyVersion"),
        "astronomyContract": artifact.get("astronomyContract"),
        "symbol": str(packet.get("symbol") or "").upper(),
        "timeframe": str(capture.get("timeframe") or "").upper(),
        "outcomeContract": OUTCOME_CONTRACT,
        "horizonHours": decision.get("horizonHours"),
        "gateConfiguration": dict(gate_configuration),
    }
    missing = [
        key for key, value in identity.items() if value is None or value == ""
    ]
    if missing:
        raise ValueError("trial identity is incomplete: " + ", ".join(missing))
    return {
        **identity,
        "gateConfigurationSha256": _fingerprint(dict(gate_configuration)),
        "trialId": _fingerprint(identity),
    }


def _read_only_uri(path: Path) -> str:
    normalized = path.resolve().as_posix()
    return f"file:{quote(normalized, safe=':/')}?mode=ro"


def audit_database(
    database_path: Path,
    *,
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    database = database_path.expanduser().resolve()
    if not database.is_file():
        raise ValueError(f"shadow database does not exist: {database}")
    before_sha = _sha256_file(database)
    before_size = database.stat().st_size
    now = (observed_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    connection = sqlite3.connect(_read_only_uri(database), uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only=ON")
        query_only = int(connection.execute("PRAGMA query_only").fetchone()[0]) == 1
        data_version_before = int(
            connection.execute("PRAGMA data_version").fetchone()[0]
        )
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        required_tables = {
            "app_shadow_ledger_entries",
            "app_shadow_trial_manifest",
        }
        missing_tables = sorted(required_tables - tables)
        if missing_tables:
            raise ValueError("missing shadow tables: " + ", ".join(missing_tables))
        triggers = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        required_triggers = {
            "trg_shadow_ledger_no_update",
            "trg_shadow_ledger_no_delete",
            "trg_shadow_trial_manifest_no_update",
            "trg_shadow_trial_manifest_no_delete",
        }
        manifest_row = connection.execute(
            "SELECT * FROM app_shadow_trial_manifest WHERE singleton_id=1"
        ).fetchone()
        if manifest_row is None:
            raise ValueError("frozen shadow trial manifest is missing")
        manifest = dict(manifest_row)
        identity_json = str(manifest["identity_json"])
        identity_sha = _sha256_text(identity_json)
        if identity_sha != str(manifest["identity_sha256"]):
            raise ValueError("manifest identity SHA-256 does not match")
        descriptor = json.loads(identity_json)
        if descriptor.get("contract") != TRIAL_CONTRACT:
            raise ValueError("manifest trial contract does not match")
        if descriptor.get("trialId") != manifest.get("trial_id"):
            raise ValueError("manifest trial ID does not match")
        if descriptor.get("gateConfigurationSha256") != _fingerprint(
            descriptor.get("gateConfiguration") or {}
        ):
            raise ValueError("manifest gate configuration SHA-256 does not match")
        rows = [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM app_shadow_ledger_entries ORDER BY ledger_sequence"
            )
        ]
        data_version_after = int(
            connection.execute("PRAGMA data_version").fetchone()[0]
        )
    finally:
        connection.close()

    previous_hash = GENESIS_HASH
    previous_recorded: datetime | None = None
    decisions: list[dict[str, Any]] = []
    outcomes: dict[str, dict[str, Any]] = {}
    cohort_ids: set[str] = set()
    for expected_sequence, row in enumerate(rows, start=1):
        if int(row["ledger_sequence"]) != expected_sequence:
            raise ValueError("shadow ledger sequence is not contiguous")
        if str(row["previous_entry_hash"]) != previous_hash:
            raise ValueError("shadow ledger previous-hash link is broken")
        payload_json = str(row["payload_json"])
        if _sha256_text(payload_json) != str(row["payload_sha256"]):
            raise ValueError("shadow ledger payload hash does not match")
        if _fingerprint(_entry_hash_payload(row)) != str(row["entry_hash"]):
            raise ValueError("shadow ledger entry hash does not match")
        recorded = _aware_timestamp(row["recorded_at_utc"], "recorded_at_utc")
        if previous_recorded is not None and recorded < previous_recorded:
            raise ValueError("shadow ledger clock moved backwards")
        previous_recorded = recorded
        previous_hash = str(row["entry_hash"])
        payload = json.loads(payload_json)
        if str(row["entry_type"]) == "decision":
            if payload.get("contract") != DECISION_CONTRACT:
                raise ValueError("decision contract does not match")
            if payload.get("executionAllowed") is not False:
                raise ValueError("shadow decision enables execution")
            trial = _trial_descriptor(payload, descriptor["gateConfiguration"])
            cohort_ids.add(str(trial["trialId"]))
            decisions.append(payload)
        elif str(row["entry_type"]) == "outcome":
            if payload.get("contract") != OUTCOME_CONTRACT:
                raise ValueError("outcome contract does not match")
            outcomes[str(payload.get("shadowId") or "")] = payload
        else:
            raise ValueError("unknown shadow ledger entry type")

    if cohort_ids != {str(descriptor["trialId"])}:
        raise ValueError("ledger decisions do not belong to one frozen manifest cohort")
    abstain_count = sum(
        1 for item in decisions if (item.get("packet") or {}).get("status") == "abstain"
    )
    watch_count = sum(
        1 for item in decisions if (item.get("packet") or {}).get("status") == "watch"
    )
    pending = [
        item for item in decisions if str(item.get("shadowId") or "") not in outcomes
    ]
    due = sum(
        1
        for item in pending
        if _aware_timestamp(item["labelDueTimeUtc"], "labelDueTimeUtc") <= now
    )
    after_sha = _sha256_file(database)
    after_size = database.stat().st_size
    unchanged = (
        before_sha == after_sha
        and before_size == after_size
        and data_version_before == data_version_after
    )
    if not unchanged:
        raise ValueError("database changed during read-only audit; retry without concurrent writes")
    return {
        "contract": AUDIT_CONTRACT,
        "auditedAtUtc": now.isoformat().replace("+00:00", "Z"),
        "status": "pass_frozen_cohort_collecting",
        "database": {
            "path": str(database),
            "sha256Before": before_sha,
            "sha256After": after_sha,
            "bytes": before_size,
            "openedReadOnly": query_only,
            "sqliteDataVersionBefore": data_version_before,
            "sqliteDataVersionAfter": data_version_after,
            "unchangedDuringAudit": unchanged,
        },
        "immutability": {
            "requiredTriggersPresent": sorted(required_triggers & triggers),
            "missingTriggers": sorted(required_triggers - triggers),
            "triggerGatePassed": required_triggers <= triggers,
        },
        "manifest": {
            "contract": descriptor["contract"],
            "trialId": descriptor["trialId"],
            "manifestIdentitySha256": identity_sha,
            "gateConfigurationSha256": descriptor["gateConfigurationSha256"],
            "engineVersion": descriptor["engineVersion"],
            "policyVersion": descriptor["policyVersion"],
            "astronomyContract": descriptor["astronomyContract"],
            "symbol": descriptor["symbol"],
            "timeframe": descriptor["timeframe"],
            "horizonHours": descriptor["horizonHours"],
            "cohortMutable": False,
        },
        "ledger": {
            "chainValid": True,
            "entryCount": len(rows),
            "headHash": previous_hash,
            "cohortCount": len(cohort_ids),
            "decisionCount": len(decisions),
            "abstainDecisionCount": abstain_count,
            "watchDecisionCount": watch_count,
            "settledDecisionCount": len(outcomes),
            "pendingOutcomeCount": len(pending),
            "dueOutcomeCountAtAudit": due,
        },
        "financiallyValidated": False,
        "executionAllowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the frozen prospective shadow database without writing to it."
    )
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_database(args.database)
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
