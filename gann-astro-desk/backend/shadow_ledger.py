from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

import numpy as np
import pandas as pd

from decision_engine import LIVE_INFERENCE
from mt5_gateway import TIMEFRAME_SECONDS
from shadow_trial import (
    TRIAL_CONTRACT,
    trial_descriptor,
    trial_summary,
)


LEDGER_CONTRACT = "GANN_APPEND_ONLY_SHADOW_LEDGER_V1"
DECISION_CONTRACT = "GANN_PROSPECTIVE_SHADOW_DECISION_V1"
OUTCOME_CONTRACT = "GANN_PROSPECTIVE_72H_OUTCOME_V1"
OUTCOME_HORIZON_HOURS = 72
CAPTURE_GRACE_MINUTES = 15
GENESIS_HASH = "0" * 64
SUPPORTED_TIMEFRAMES = frozenset({"M30", "H1", "H4", "D1"})


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _json_safe(value),
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _fingerprint(value: Any) -> str:
    return _sha256(_canonical_json(value))


def _utc_timestamp(value: Any, label: str) -> pd.Timestamp:
    try:
        parsed = pd.Timestamp(value)
    except Exception as exc:
        raise ValueError(f"{label} is not a valid timestamp") from exc
    if pd.isna(parsed) or parsed.tzinfo is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.tz_convert("UTC")


def _utc_now() -> pd.Timestamp:
    return pd.Timestamp(datetime.now(timezone.utc))


def _timeframe_delta(timeframe: str) -> pd.Timedelta:
    normalized = str(timeframe or "").strip().upper()
    if normalized not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"unsupported shadow timeframe: {timeframe}")
    return pd.Timedelta(seconds=TIMEFRAME_SECONDS[normalized])


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


def _binomial_two_sided_p(hits: int, total: int) -> float | None:
    if total <= 0:
        return None
    center = total / 2
    if hits >= center:
        tail = sum(math.comb(total, k) for k in range(hits, total + 1)) / (2**total)
    else:
        tail = sum(math.comb(total, k) for k in range(0, hits + 1)) / (2**total)
    return min(1.0, 2 * tail)


def _wilson_interval(
    hits: int, total: int, z: float = 1.959963984540054
) -> tuple[float | None, float | None]:
    if total <= 0:
        return None, None
    proportion = hits / total
    denominator = 1 + (z * z / total)
    center = (proportion + (z * z / (2 * total))) / denominator
    margin = (
        z
        * math.sqrt(
            (proportion * (1 - proportion) / total) + (z * z / (4 * total * total))
        )
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def bars_to_price_frame(bars: list[dict[str, Any]]) -> pd.DataFrame:
    if not bars:
        raise ValueError("MT5 returned no bars")
    frame = pd.DataFrame(bars).copy()
    required = {"time", "open", "high", "low", "close"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"MT5 bars are missing columns: {missing}")
    frame["time"] = pd.to_datetime(frame["time"], unit="s", utc=True)
    frame = frame.drop_duplicates("time", keep="last").set_index("time").sort_index()
    return frame


def last_closed_anchor(
    price: pd.DataFrame,
    timeframe: str,
    observed_at: Any,
) -> tuple[pd.Timestamp, float]:
    now = _utc_timestamp(observed_at, "observed_at")
    delta = _timeframe_delta(timeframe)
    if not isinstance(price.index, pd.DatetimeIndex) or price.index.tz is None:
        raise ValueError("price evidence must have timezone-aware timestamps")
    normalized = price.copy().sort_index()
    normalized.index = normalized.index.tz_convert("UTC")
    closed = normalized.loc[normalized.index + delta <= now]
    if closed.empty:
        raise ValueError("MT5 has no fully closed bar for shadow capture")
    open_time = closed.index[-1]
    close_price = float(closed.iloc[-1]["close"])
    if not np.isfinite(close_price):
        raise ValueError("last closed MT5 price is invalid")
    return open_time + delta, close_price


def first_closed_outcome_bar(
    price: pd.DataFrame,
    timeframe: str,
    due_at: Any,
    observed_at: Any,
) -> tuple[pd.Timestamp, float] | None:
    due = _utc_timestamp(due_at, "due_at")
    now = _utc_timestamp(observed_at, "observed_at")
    delta = _timeframe_delta(timeframe)
    normalized = price.copy().sort_index()
    if (
        not isinstance(normalized.index, pd.DatetimeIndex)
        or normalized.index.tz is None
    ):
        raise ValueError("price evidence must have timezone-aware timestamps")
    normalized.index = normalized.index.tz_convert("UTC")
    close_times = normalized.index + delta
    eligible = normalized.loc[(close_times >= due) & (close_times <= now)]
    if eligible.empty:
        return None
    open_time = eligible.index[0]
    close_price = float(eligible.iloc[0]["close"])
    if not np.isfinite(close_price):
        raise ValueError("outcome MT5 price is invalid")
    return open_time + delta, close_price


class ShadowLedgerStore:
    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path).expanduser().resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS app_shadow_ledger_entries (
                    ledger_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT NOT NULL UNIQUE,
                    entry_type TEXT NOT NULL CHECK(entry_type IN ('decision', 'outcome')),
                    shadow_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    family_key TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    effective_at_utc TEXT NOT NULL,
                    recorded_at_utc TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    previous_entry_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_shadow_entry_type_subject
                    ON app_shadow_ledger_entries(entry_type, shadow_id);
                CREATE INDEX IF NOT EXISTS idx_shadow_entry_recorded
                    ON app_shadow_ledger_entries(recorded_at_utc, ledger_sequence);
                CREATE TABLE IF NOT EXISTS app_shadow_trial_manifest (
                    singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
                    trial_id TEXT NOT NULL UNIQUE,
                    contract TEXT NOT NULL,
                    identity_json TEXT NOT NULL,
                    identity_sha256 TEXT NOT NULL,
                    established_at_utc TEXT NOT NULL,
                    seed_shadow_id TEXT NOT NULL,
                    source TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS trg_shadow_ledger_no_update
                BEFORE UPDATE ON app_shadow_ledger_entries
                BEGIN
                    SELECT RAISE(ABORT, 'shadow ledger is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS trg_shadow_ledger_no_delete
                BEFORE DELETE ON app_shadow_ledger_entries
                BEGIN
                    SELECT RAISE(ABORT, 'shadow ledger is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS trg_shadow_trial_manifest_no_update
                BEFORE UPDATE ON app_shadow_trial_manifest
                BEGIN
                    SELECT RAISE(ABORT, 'shadow trial manifest is immutable');
                END;
                CREATE TRIGGER IF NOT EXISTS trg_shadow_trial_manifest_no_delete
                BEFORE DELETE ON app_shadow_trial_manifest
                BEGIN
                    SELECT RAISE(ABORT, 'shadow trial manifest is immutable');
                END;
                """
            )
            now = _utc_now().isoformat()
            connection.execute(
                """
                INSERT INTO schema_meta(key, value, updated_at_utc)
                VALUES('shadow_ledger_schema_version', '2', ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at_utc=excluded.updated_at_utc
                WHERE schema_meta.value <> excluded.value
                """,
                (now,),
            )
            connection.commit()
        self._backfill_trial_manifest()

    @staticmethod
    def _manifest_record(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        encoded = str(row["identity_json"])
        identity_sha = _sha256(encoded)
        if identity_sha != str(row["identity_sha256"]):
            raise ValueError("shadow trial manifest identity hash does not match")
        descriptor = json.loads(encoded)
        if descriptor.get("contract") != TRIAL_CONTRACT:
            raise ValueError("shadow trial manifest contract does not match")
        if descriptor.get("trialId") != str(row["trial_id"]):
            raise ValueError("shadow trial manifest ID does not match")
        return {
            **descriptor,
            "manifestIdentitySha256": identity_sha,
            "establishedAtUtc": str(row["established_at_utc"]),
            "seedShadowId": str(row["seed_shadow_id"]),
            "manifestSource": str(row["source"]),
        }

    @staticmethod
    def _insert_trial_manifest(
        connection: sqlite3.Connection,
        descriptor: Mapping[str, Any],
        *,
        established_at: pd.Timestamp,
        seed_shadow_id: str,
        source: str,
    ) -> None:
        encoded = _canonical_json(descriptor)
        connection.execute(
            """
            INSERT INTO app_shadow_trial_manifest(
                singleton_id, trial_id, contract, identity_json, identity_sha256,
                established_at_utc, seed_shadow_id, source
            ) VALUES(1, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                descriptor["trialId"],
                TRIAL_CONTRACT,
                encoded,
                _sha256(encoded),
                established_at.isoformat(),
                seed_shadow_id,
                source,
            ),
        )

    def _backfill_trial_manifest(self) -> None:
        with self._lock, self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                manifest = connection.execute(
                    "SELECT * FROM app_shadow_trial_manifest WHERE singleton_id = 1"
                ).fetchone()
                if manifest is not None:
                    self._manifest_record(manifest)
                    connection.commit()
                    return
                rows = connection.execute(
                    """
                    SELECT payload_json FROM app_shadow_ledger_entries
                    WHERE entry_type = 'decision' ORDER BY ledger_sequence
                    """
                ).fetchall()
                if not rows:
                    connection.commit()
                    return
                decisions = [json.loads(str(row["payload_json"])) for row in rows]
                descriptors = [
                    trial_descriptor(
                        item,
                        ledger_contract=LEDGER_CONTRACT,
                        outcome_contract=OUTCOME_CONTRACT,
                    )
                    for item in decisions
                ]
                trial_ids = {str(item["trialId"]) for item in descriptors}
                if len(trial_ids) != 1:
                    raise ValueError(
                        "existing shadow decisions contain mixed policy cohorts; "
                        "an immutable trial manifest cannot be established"
                    )
                first = decisions[0]
                self._insert_trial_manifest(
                    connection,
                    descriptors[0],
                    established_at=_utc_now(),
                    seed_shadow_id=str(first["shadowId"]),
                    source="existing_decision_backfill_v1",
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def trial_manifest(self) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM app_shadow_trial_manifest WHERE singleton_id = 1"
            ).fetchone()
        return self._manifest_record(row)

    @staticmethod
    def _verify_rows(rows: list[sqlite3.Row]) -> None:
        previous_hash = GENESIS_HASH
        previous_recorded: pd.Timestamp | None = None
        for expected_sequence, row in enumerate(rows, start=1):
            item = dict(row)
            if int(item["ledger_sequence"]) != expected_sequence:
                raise ValueError("shadow ledger sequence is not contiguous")
            if str(item["previous_entry_hash"]) != previous_hash:
                raise ValueError("shadow ledger previous-hash link is broken")
            payload_sha = _sha256(str(item["payload_json"]))
            if payload_sha != str(item["payload_sha256"]):
                raise ValueError("shadow ledger payload hash does not match")
            expected_hash = _fingerprint(_entry_hash_payload(item))
            if expected_hash != str(item["entry_hash"]):
                raise ValueError("shadow ledger entry hash does not match")
            recorded = _utc_timestamp(item["recorded_at_utc"], "recorded_at_utc")
            if previous_recorded is not None and recorded < previous_recorded:
                raise ValueError("shadow ledger clock moved backwards")
            previous_recorded = recorded
            previous_hash = str(item["entry_hash"])

    def verify_chain(self) -> dict[str, Any]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM app_shadow_ledger_entries ORDER BY ledger_sequence"
            ).fetchall()
        try:
            self._verify_rows(rows)
        except ValueError as exc:
            return {"valid": False, "entryCount": len(rows), "error": str(exc)}
        return {
            "valid": True,
            "entryCount": len(rows),
            "headHash": str(rows[-1]["entry_hash"]) if rows else GENESIS_HASH,
            "error": "",
        }

    def _append(
        self,
        *,
        entry_type: str,
        shadow_id: str,
        event_id: str,
        family_key: str,
        symbol: str,
        timeframe: str,
        effective_at: pd.Timestamp,
        recorded_at: pd.Timestamp,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        encoded = _canonical_json(payload)
        payload_sha = _sha256(encoded)
        with self._lock, self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                rows = connection.execute(
                    "SELECT * FROM app_shadow_ledger_entries ORDER BY ledger_sequence"
                ).fetchall()
                self._verify_rows(rows)
                if entry_type == "decision":
                    candidate_trial = trial_descriptor(
                        payload,
                        ledger_contract=LEDGER_CONTRACT,
                        outcome_contract=OUTCOME_CONTRACT,
                    )
                    manifest_row = connection.execute(
                        "SELECT * FROM app_shadow_trial_manifest WHERE singleton_id = 1"
                    ).fetchone()
                    if manifest_row is None:
                        self._insert_trial_manifest(
                            connection,
                            candidate_trial,
                            established_at=recorded_at,
                            seed_shadow_id=shadow_id,
                            source="first_decision_capture_v1",
                        )
                        manifest_row = connection.execute(
                            "SELECT * FROM app_shadow_trial_manifest WHERE singleton_id = 1"
                        ).fetchone()
                    manifest = self._manifest_record(manifest_row)
                    if manifest is None:
                        raise RuntimeError("shadow trial manifest was not established")
                    if manifest["trialId"] != candidate_trial["trialId"]:
                        raise ValueError(
                            "frozen prospective trial refuses a mixed policy cohort; "
                            f"expected {manifest['trialId']}, "
                            f"received {candidate_trial['trialId']}"
                        )
                existing = connection.execute(
                    """
                    SELECT * FROM app_shadow_ledger_entries
                    WHERE entry_type = ? AND shadow_id = ?
                    """,
                    (entry_type, shadow_id),
                ).fetchone()
                if existing is not None:
                    connection.commit()
                    return self._entry_record(existing), False
                sequence = len(rows) + 1
                previous_hash = str(rows[-1]["entry_hash"]) if rows else GENESIS_HASH
                if rows:
                    previous_recorded = _utc_timestamp(
                        rows[-1]["recorded_at_utc"], "previous recorded_at_utc"
                    )
                    if recorded_at < previous_recorded:
                        raise ValueError(
                            "refusing append after a backwards clock movement"
                        )
                entry_id = _fingerprint(
                    {
                        "contract": LEDGER_CONTRACT,
                        "entryType": entry_type,
                        "shadowId": shadow_id,
                        "payloadSha256": payload_sha,
                    }
                )
                row = {
                    "ledger_sequence": sequence,
                    "entry_id": entry_id,
                    "entry_type": entry_type,
                    "shadow_id": shadow_id,
                    "event_id": event_id,
                    "family_key": family_key,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "effective_at_utc": effective_at.isoformat(),
                    "recorded_at_utc": recorded_at.isoformat(),
                    "payload_sha256": payload_sha,
                    "previous_entry_hash": previous_hash,
                }
                entry_hash = _fingerprint(_entry_hash_payload(row))
                connection.execute(
                    """
                    INSERT INTO app_shadow_ledger_entries(
                        ledger_sequence, entry_id, entry_type, shadow_id, event_id,
                        family_key, symbol, timeframe, effective_at_utc, recorded_at_utc,
                        payload_json, payload_sha256, previous_entry_hash, entry_hash
                    ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sequence,
                        entry_id,
                        entry_type,
                        shadow_id,
                        event_id,
                        family_key,
                        symbol,
                        timeframe,
                        effective_at.isoformat(),
                        recorded_at.isoformat(),
                        encoded,
                        payload_sha,
                        previous_hash,
                        entry_hash,
                    ),
                )
                inserted = connection.execute(
                    "SELECT * FROM app_shadow_ledger_entries WHERE ledger_sequence = ?",
                    (sequence,),
                ).fetchone()
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        if inserted is None:
            raise RuntimeError("shadow ledger append did not return its inserted row")
        return self._entry_record(inserted), True

    @staticmethod
    def _entry_record(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        return {
            "sequence": int(item["ledger_sequence"]),
            "entryId": str(item["entry_id"]),
            "entryType": str(item["entry_type"]),
            "shadowId": str(item["shadow_id"]),
            "eventId": str(item["event_id"]),
            "familyKey": str(item["family_key"]),
            "symbol": str(item["symbol"]),
            "timeframe": str(item["timeframe"]),
            "effectiveAtUtc": str(item["effective_at_utc"]),
            "recordedAtUtc": str(item["recorded_at_utc"]),
            "payload": json.loads(str(item["payload_json"])),
            "payloadSha256": str(item["payload_sha256"]),
            "previousEntryHash": str(item["previous_entry_hash"]),
            "entryHash": str(item["entry_hash"]),
        }

    def append_decision(
        self,
        *,
        packet: dict[str, Any],
        capture_key: dict[str, Any],
        timeframe: str,
        anchor_time: Any,
        anchor_price: float,
        captured_at: Any,
        max_signal_age_seconds: int,
        artifact_evidence: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        captured = _utc_timestamp(captured_at, "captured_at")
        decision_time = _utc_timestamp(
            packet.get("times", {}).get("decisionTime"), "decisionTime"
        )
        signal_time = _utc_timestamp(
            packet.get("times", {}).get("signalTime"), "signalTime"
        )
        source_max = _utc_timestamp(
            packet.get("times", {}).get("sourceDataMaxTime"), "sourceDataMaxTime"
        )
        anchor = _utc_timestamp(anchor_time, "anchor_time")
        if packet.get("mode") != LIVE_INFERENCE:
            raise ValueError("shadow ledger accepts live_inference packets only")
        guardrails = packet.get("guardrails") or {}
        if (
            guardrails.get("timestampSafe") is not True
            or guardrails.get("noLookahead") is not True
        ):
            raise ValueError("shadow decision packet is not timestamp safe")
        if (
            guardrails.get("executionAllowed") is not False
            or packet.get("outcome") is not None
        ):
            raise ValueError(
                "shadow decision packet contains execution or outcome data"
            )
        if source_max > decision_time or decision_time > captured + pd.Timedelta(
            seconds=30
        ):
            raise ValueError("shadow decision chronology is invalid")
        if captured - decision_time > pd.Timedelta(minutes=5):
            raise ValueError("shadow packet was not captured at server decision time")
        signal_age = decision_time - signal_time
        if signal_age < pd.Timedelta(0) or signal_age > pd.Timedelta(
            seconds=max_signal_age_seconds
        ):
            raise ValueError("shadow signal is stale or not yet available")
        if anchor != source_max:
            raise ValueError("shadow anchor must equal the last closed evidence time")
        anchor_value = float(anchor_price)
        if not np.isfinite(anchor_value):
            raise ValueError("shadow anchor price is invalid")
        if bool(artifact_evidence.get("builtIn")):
            raise ValueError(
                "built-in retrospective artifacts cannot enter the prospective ledger"
            )
        label_due = anchor + pd.Timedelta(hours=OUTCOME_HORIZON_HOURS)
        shadow_id = _fingerprint(
            {
                "contract": DECISION_CONTRACT,
                "captureKey": capture_key,
                "engineVersion": packet.get("engineVersion"),
                "policyVersion": packet.get("policyVersion"),
            }
        )
        payload = {
            "contract": DECISION_CONTRACT,
            "ledgerContract": LEDGER_CONTRACT,
            "shadowId": shadow_id,
            "captureKey": capture_key,
            "capturedAtUtc": captured.isoformat(),
            "anchorBarCloseTimeUtc": anchor.isoformat(),
            "anchorClose": anchor_value,
            "labelDueTimeUtc": label_due.isoformat(),
            "horizonHours": OUTCOME_HORIZON_HOURS,
            "signalAgeSeconds": float(signal_age.total_seconds()),
            "artifactEvidence": artifact_evidence,
            "packet": packet,
            "executionAllowed": False,
        }
        payload["trialIdentity"] = trial_descriptor(
            payload,
            ledger_contract=LEDGER_CONTRACT,
            outcome_contract=OUTCOME_CONTRACT,
        )
        return self._append(
            entry_type="decision",
            shadow_id=shadow_id,
            event_id=str(packet.get("eventId") or ""),
            family_key=str(packet.get("familyKey") or ""),
            symbol=str(packet.get("symbol") or "USDJPY").upper(),
            timeframe=str(timeframe).upper(),
            effective_at=decision_time,
            recorded_at=captured,
            payload=payload,
        )

    def append_outcome(
        self,
        *,
        decision_payload: dict[str, Any],
        observed_time: Any,
        observed_price: float,
        settled_at: Any,
    ) -> tuple[dict[str, Any], bool]:
        if decision_payload.get("contract") != DECISION_CONTRACT:
            raise ValueError("outcome does not reference a shadow decision contract")
        shadow_id = str(decision_payload.get("shadowId") or "")
        packet = decision_payload.get("packet") or {}
        due = _utc_timestamp(decision_payload.get("labelDueTimeUtc"), "labelDueTimeUtc")
        observed = _utc_timestamp(observed_time, "observed_time")
        settled = _utc_timestamp(settled_at, "settled_at")
        if observed < due or settled < observed:
            raise ValueError(
                "shadow outcome was observed before its closed 72-hour horizon"
            )
        anchor_price = float(decision_payload.get("anchorClose"))
        target_price = float(observed_price)
        if (
            not np.isfinite(anchor_price)
            or not np.isfinite(target_price)
            or anchor_price == 0
        ):
            raise ValueError("shadow outcome prices are invalid")
        raw_return = ((target_price / anchor_price) - 1) * 100
        observed_direction = (
            "UP" if raw_return > 0 else "DOWN" if raw_return < 0 else "FLAT"
        )
        predicted = str((packet.get("decision") or {}).get("direction") or "abstain")
        predicted_direction = {"bullish": "UP", "bearish": "DOWN"}.get(predicted)
        hit = (
            bool(predicted_direction == observed_direction)
            if predicted_direction
            else None
        )
        signed_return = (
            raw_return
            if predicted == "bullish"
            else -raw_return
            if predicted == "bearish"
            else None
        )
        payload = {
            "contract": OUTCOME_CONTRACT,
            "ledgerContract": LEDGER_CONTRACT,
            "shadowId": shadow_id,
            "decisionPacketId": packet.get("packetId"),
            "labelDueTimeUtc": due.isoformat(),
            "observedBarCloseTimeUtc": observed.isoformat(),
            "settledAtUtc": settled.isoformat(),
            "settlementDelaySeconds": float((observed - due).total_seconds()),
            "anchorClose": anchor_price,
            "observedClose": target_price,
            "rawReturnPct": raw_return,
            "observedDirection": observed_direction,
            "predictedDirection": predicted_direction,
            "hit": hit,
            "signedReturnPct": signed_return,
            "costModel": "none_directional_shadow_only",
            "executionOccurred": False,
        }
        return self._append(
            entry_type="outcome",
            shadow_id=shadow_id,
            event_id=str(packet.get("eventId") or ""),
            family_key=str(packet.get("familyKey") or ""),
            symbol=str(packet.get("symbol") or "USDJPY").upper(),
            timeframe=str(
                decision_payload.get("captureKey", {}).get("timeframe") or "H1"
            ).upper(),
            effective_at=observed,
            recorded_at=settled,
            payload=payload,
        )

    def _payload_sets(self) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM app_shadow_ledger_entries ORDER BY ledger_sequence"
            ).fetchall()
        decisions: list[dict[str, Any]] = []
        outcomes: dict[str, dict[str, Any]] = {}
        for row in rows:
            payload = json.loads(str(row["payload_json"]))
            if row["entry_type"] == "decision":
                decisions.append(payload)
            else:
                outcomes[str(row["shadow_id"])] = payload
        return decisions, outcomes

    def pending_decisions(self, observed_at: Any) -> list[dict[str, Any]]:
        now = _utc_timestamp(observed_at, "observed_at")
        decisions, outcomes = self._payload_sets()
        return [
            decision
            for decision in decisions
            if str(decision["shadowId"]) not in outcomes
            and _utc_timestamp(decision["labelDueTimeUtc"], "labelDueTimeUtc") <= now
        ]

    def records(self, limit: int = 100) -> list[dict[str, Any]]:
        decisions, outcomes = self._payload_sets()
        records: list[dict[str, Any]] = []
        for decision in reversed(decisions):
            packet = decision.get("packet") or {}
            outcome = outcomes.get(str(decision.get("shadowId") or ""))
            records.append(
                {
                    "shadowId": decision.get("shadowId"),
                    "eventId": packet.get("eventId"),
                    "familyKey": packet.get("familyKey"),
                    "symbol": packet.get("symbol"),
                    "timeframe": decision.get("captureKey", {}).get("timeframe"),
                    "action": packet.get("decision", {}).get("action"),
                    "direction": packet.get("decision", {}).get("direction"),
                    "capturedAtUtc": decision.get("capturedAtUtc"),
                    "decisionTimeUtc": packet.get("times", {}).get("decisionTime"),
                    "anchorTimeUtc": decision.get("anchorBarCloseTimeUtc"),
                    "anchorClose": decision.get("anchorClose"),
                    "labelDueTimeUtc": decision.get("labelDueTimeUtc"),
                    "status": "settled" if outcome else "pending_72h",
                    "observedDirection": outcome.get("observedDirection")
                    if outcome
                    else None,
                    "rawReturnPct": outcome.get("rawReturnPct") if outcome else None,
                    "signedReturnPct": outcome.get("signedReturnPct")
                    if outcome
                    else None,
                    "hit": outcome.get("hit") if outcome else None,
                    "packetId": packet.get("packetId"),
                    "executionOccurred": False,
                }
            )
        return records[: max(1, min(int(limit), 500))]

    def summary(self, observed_at: Any | None = None) -> dict[str, Any]:
        decisions, outcomes = self._payload_sets()
        now = (
            _utc_timestamp(observed_at, "summary observed_at")
            if observed_at is not None
            else _utc_now()
        )
        trial = trial_summary(
            decisions,
            outcomes,
            now,
            ledger_contract=LEDGER_CONTRACT,
            outcome_contract=OUTCOME_CONTRACT,
            manifest=self.trial_manifest(),
        )
        gate_configuration = trial["gateConfiguration"]
        settled = [item for item in decisions if str(item["shadowId"]) in outcomes]
        clusters: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for decision in settled:
            packet = decision.get("packet") or {}
            key = (
                str(packet.get("symbol") or ""),
                str(decision.get("captureKey", {}).get("timeframe") or ""),
                str(decision.get("anchorBarCloseTimeUtc") or ""),
            )
            clusters.setdefault(key, []).append(decision)
        watch_clusters: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for items in clusters.values():
            directions = {
                str(item.get("packet", {}).get("decision", {}).get("direction") or "")
                for item in items
                if str(
                    item.get("packet", {}).get("decision", {}).get("direction") or ""
                )
                in {"bullish", "bearish"}
            }
            if len(directions) != 1:
                continue
            representative = items[0]
            watch_clusters.append(
                (representative, outcomes[str(representative["shadowId"])])
            )
        hits = sum(1 for _, outcome in watch_clusters if outcome.get("hit") is True)
        watch_count = len(watch_clusters)
        total_clusters = len(clusters)
        signed_returns = [
            float(outcome["signedReturnPct"])
            for _, outcome in watch_clusters
            if outcome.get("signedReturnPct") is not None
        ]
        months = {
            str(item.get("packet", {}).get("times", {}).get("decisionTime") or "")[:7]
            for item, _ in watch_clusters
        }
        lower, upper = _wilson_interval(hits, watch_count)
        p_value = _binomial_two_sided_p(hits, watch_count)
        coverage = (watch_count / total_clusters) if total_clusters else None
        mean_signed = float(np.mean(signed_returns)) if signed_returns else None
        criteria = {
            "minimum100WatchClusters": watch_count
            >= int(gate_configuration["minimumWatchClusters"]),
            "coverageAtLeast10Pct": coverage is not None
            and coverage >= float(gate_configuration["minimumCoverage"]),
            "wilsonLowerAbove50Pct": lower is not None
            and lower > float(gate_configuration["wilsonLowerMustExceed"]),
            "twoSidedPBelow005": p_value is not None
            and p_value < float(gate_configuration["twoSidedPBelow"]),
            "positiveMeanSignedReturn": mean_signed is not None
            and mean_signed
            > float(gate_configuration["meanSignedReturnMustExceedPct"]),
            "minimumFourCalendarMonths": len(months - {""})
            >= int(gate_configuration["minimumCalendarMonths"]),
        }
        enough_sample = (
            criteria["minimum100WatchClusters"]
            and criteria["minimumFourCalendarMonths"]
        )
        gate_status = (
            "blocked_mixed_policy_cohorts"
            if not trial["integrityValid"]
            else "collecting_prospective_shadow_evidence"
            if not enough_sample
            else "passed_prospective_statistical_gate"
            if all(criteria.values())
            else "failed_prospective_statistical_gate"
        )
        trial["progress"] = {
            "watchClusters": {
                "current": watch_count,
                "target": int(gate_configuration["minimumWatchClusters"]),
            },
            "calendarMonths": {
                "current": len(months - {""}),
                "target": int(gate_configuration["minimumCalendarMonths"]),
            },
            "coverage": {
                "current": coverage,
                "minimum": float(gate_configuration["minimumCoverage"]),
            },
        }
        return {
            "contract": LEDGER_CONTRACT,
            "gateStatus": gate_status,
            "decisionCount": len(decisions),
            "watchDecisionCount": sum(
                1
                for item in decisions
                if item.get("packet", {}).get("status") == "watch"
            ),
            "abstainDecisionCount": sum(
                1
                for item in decisions
                if item.get("packet", {}).get("status") == "abstain"
            ),
            "settledDecisionCount": len(settled),
            "pendingOutcomeCount": len(decisions) - len(settled),
            "settledClusterCount": total_clusters,
            "watchClusterCount": watch_count,
            "directionalHits": hits,
            "hitRate": (hits / watch_count) if watch_count else None,
            "coverage": coverage,
            "wilson95Lower": lower,
            "wilson95Upper": upper,
            "twoSidedBinomialP": p_value,
            "meanSigned72hReturnPct": mean_signed,
            "calendarMonthCount": len(months - {""}),
            "criteria": criteria,
            "executionAllowed": False,
            "chain": self.verify_chain(),
            "trial": trial,
        }


class ShadowLedgerSupervisor:
    def __init__(
        self,
        repository: Any,
        gateway: Any,
        *,
        autostart: bool = True,
        poll_seconds: float = 30.0,
    ) -> None:
        self.repository = repository
        self.gateway = gateway
        self.store = ShadowLedgerStore(repository.paths.annotation_db)
        self.poll_seconds = max(5.0, float(poll_seconds))
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._scan_lock = threading.RLock()
        self._thread: threading.Thread | None = None
        self._status_lock = threading.RLock()
        self._status: dict[str, Any] = {
            "state": "starting" if autostart else "paused",
            "lastScanAtUtc": None,
            "lastCaptureCount": 0,
            "lastSettlementCount": 0,
            "lastError": "",
            "readiness": {"ready": False, "code": "not_scanned"},
        }
        if autostart:
            self.start()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._worker_loop,
            name="prospective-shadow-ledger",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def status(self) -> dict[str, Any]:
        with self._status_lock:
            return dict(self._status)

    def _set_status(self, **values: Any) -> None:
        with self._status_lock:
            self._status.update(values)

    @staticmethod
    def _artifact_readiness(
        snapshot: dict[str, Any], now: pd.Timestamp
    ) -> dict[str, Any]:
        artifact = snapshot.get("artifact") or {}
        timeframe = str(snapshot.get("timeframe") or "").upper()
        if timeframe not in SUPPORTED_TIMEFRAMES:
            return {
                "ready": False,
                "code": "unsupported_timeframe",
                "timeframe": timeframe,
            }
        if bool(artifact.get("builtIn")):
            return {
                "ready": False,
                "code": "retrospective_baseline_blocked",
                "artifactId": artifact.get("artifactId"),
                "timeframe": timeframe,
            }
        parameters = artifact.get("parameters") or {}
        raw_source_as_of = parameters.get(
            "priceSourceLastBarCloseUtc"
        ) or parameters.get("priceSourceAsOfUtc")
        raw_created = artifact.get("createdAtUtc")
        if not raw_source_as_of or not raw_created:
            return {
                "ready": False,
                "code": "artifact_provenance_incomplete",
                "timeframe": timeframe,
            }
        source_as_of = _utc_timestamp(raw_source_as_of, "price source last closed bar")
        created_at = _utc_timestamp(raw_created, "artifact createdAtUtc")
        if source_as_of > now + pd.Timedelta(
            seconds=30
        ) or created_at > now + pd.Timedelta(seconds=30):
            return {
                "ready": False,
                "code": "artifact_timestamp_in_future",
                "timeframe": timeframe,
            }
        max_age = _timeframe_delta(timeframe) + pd.Timedelta(
            minutes=CAPTURE_GRACE_MINUTES
        )
        if now - source_as_of > max_age:
            return {
                "ready": False,
                "code": "artifact_price_snapshot_stale",
                "timeframe": timeframe,
                "sourceAsOfUtc": source_as_of.isoformat(),
                "maximumAgeSeconds": int(max_age.total_seconds()),
            }
        return {
            "ready": True,
            "code": "fresh_corrected_artifact",
            "timeframe": timeframe,
            "artifactId": artifact.get("artifactId"),
            "sourceAsOfUtc": source_as_of.isoformat(),
            "createdAtUtc": created_at.isoformat(),
            "maximumAgeSeconds": int(max_age.total_seconds()),
        }

    @staticmethod
    def _artifact_evidence(artifact: dict[str, Any]) -> dict[str, Any]:
        parameters = artifact.get("parameters") or {}
        return {
            "artifactId": artifact.get("artifactId"),
            "artifactLabel": artifact.get("label"),
            "builtIn": bool(artifact.get("builtIn")),
            "createdAtUtc": artifact.get("createdAtUtc"),
            "astronomyContract": artifact.get("astronomyContract"),
            "priceSourceId": parameters.get("priceSourceId"),
            "priceSourceSha256": parameters.get("priceSourceSha256"),
            "priceSourceAsOfUtc": parameters.get("priceSourceAsOfUtc"),
            "priceSourceLastBarCloseUtc": parameters.get("priceSourceLastBarCloseUtc"),
            "priceSourceContract": parameters.get("priceSourceContract"),
        }

    def _capture_fresh(
        self, now: pd.Timestamp
    ) -> tuple[int, dict[str, Any], list[str]]:
        snapshot = self.repository.shadow_candidate_snapshot()
        readiness = self._artifact_readiness(snapshot, now)
        if not readiness["ready"]:
            return 0, readiness, []
        artifact = snapshot["artifact"]
        timeframe = str(snapshot["timeframe"]).upper()
        delta = _timeframe_delta(timeframe)
        max_age = delta + pd.Timedelta(minutes=CAPTURE_GRACE_MINUTES)
        source_as_of = _utc_timestamp(readiness["sourceAsOfUtc"], "sourceAsOfUtc")
        candidates: list[dict[str, Any]] = []
        for touch in snapshot.get("touches") or []:
            touch_time = _utc_timestamp(touch.get("touchTime"), "touchTime")
            signal_time = touch_time + delta
            if (
                signal_time <= now
                and now - signal_time <= max_age
                and source_as_of >= signal_time
            ):
                candidates.append({**touch, "signalTime": signal_time})
        if not candidates:
            return 0, {**readiness, "code": "waiting_for_just_closed_touch"}, []
        bars = self.gateway.bars(
            str(artifact.get("symbol") or "USDJPY"),
            timeframe,
            count=500,
        )
        price = bars_to_price_frame(bars)
        anchor_time, anchor_price = last_closed_anchor(price, timeframe, now)
        captured_count = 0
        errors: list[str] = []
        for candidate in candidates:
            try:
                packet = self.repository.live_decision_packet(
                    str(candidate["eventId"]),
                    now,
                    price_override=price,
                )
                _, created = self.store.append_decision(
                    packet=packet,
                    capture_key={
                        "artifactId": artifact.get("artifactId"),
                        "eventId": candidate["eventId"],
                        "touchId": candidate["touchId"],
                        "signalTimeUtc": candidate["signalTime"].isoformat(),
                        "timeframe": timeframe,
                    },
                    timeframe=timeframe,
                    anchor_time=anchor_time,
                    anchor_price=anchor_price,
                    captured_at=now,
                    max_signal_age_seconds=int(max_age.total_seconds()),
                    artifact_evidence=self._artifact_evidence(artifact),
                )
                captured_count += int(created)
            except Exception as exc:
                errors.append(f"{candidate.get('eventId')}: {exc}")
        return captured_count, readiness, errors

    def _settle_due(self, now: pd.Timestamp) -> tuple[int, list[str]]:
        pending = self.store.pending_decisions(now)
        if not pending:
            return 0, []
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for decision in pending:
            packet = decision.get("packet") or {}
            key = (
                str(packet.get("symbol") or "USDJPY").upper(),
                str(decision.get("captureKey", {}).get("timeframe") or "H1").upper(),
            )
            grouped.setdefault(key, []).append(decision)
        settled_count = 0
        errors: list[str] = []
        for (symbol, timeframe), decisions in grouped.items():
            try:
                price = bars_to_price_frame(
                    self.gateway.bars(symbol, timeframe, count=5000)
                )
            except Exception as exc:
                errors.append(f"{symbol}/{timeframe}: {exc}")
                continue
            for decision in decisions:
                try:
                    observed = first_closed_outcome_bar(
                        price,
                        timeframe,
                        decision["labelDueTimeUtc"],
                        now,
                    )
                    if observed is None:
                        continue
                    _, created = self.store.append_outcome(
                        decision_payload=decision,
                        observed_time=observed[0],
                        observed_price=observed[1],
                        settled_at=now,
                    )
                    settled_count += int(created)
                except Exception as exc:
                    errors.append(f"{decision.get('shadowId')}: {exc}")
        return settled_count, errors

    def scan_once(self, observed_at: Any | None = None) -> dict[str, Any]:
        now = (
            _utc_timestamp(observed_at, "observed_at")
            if observed_at is not None
            else _utc_now()
        )
        with self._scan_lock:
            captured = 0
            settled = 0
            readiness: dict[str, Any] = {"ready": False, "code": "scan_failed"}
            errors: list[str] = []
            try:
                captured, readiness, capture_errors = self._capture_fresh(now)
                settled, settle_errors = self._settle_due(now)
                errors.extend(capture_errors)
                errors.extend(settle_errors)
                state = "collecting" if readiness.get("ready") else "waiting"
            except Exception as exc:
                errors.append(str(exc))
                state = "error"
            self._set_status(
                state=state,
                lastScanAtUtc=now.isoformat(),
                lastCaptureCount=captured,
                lastSettlementCount=settled,
                lastError="; ".join(errors[:8]),
                readiness=readiness,
            )
        return self.snapshot(observed_at=now)

    def snapshot(
        self, limit: int = 100, observed_at: Any | None = None
    ) -> dict[str, Any]:
        return {
            "summary": self.store.summary(observed_at),
            "records": self.store.records(limit),
            "supervisor": self.status(),
        }

    def _worker_loop(self) -> None:
        while not self._stop.is_set():
            self.scan_once()
            self._wake.wait(self.poll_seconds)
            self._wake.clear()
