from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

import numpy as np
import pandas as pd

from candlestick_analysis import METHODOLOGY_VERSION, _records
from mt5_clock import (
    default_clock_probe_path,
    normalization_probe_identity,
    normalize_bars,
    read_clock_probe,
    time_normalization_evidence,
)


LEDGER_CONTRACT = "GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3"
DECISION_CONTRACT = "GANN_CANDLESTICK_PROSPECTIVE_DECISION_V3"
OUTCOME_CONTRACT = "GANN_CANDLESTICK_PROSPECTIVE_6BAR_OUTCOME_V3"
TRIAL_CONTRACT = "GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3"
ARTIFACT_CONTRACT = "GANN_CANDLESTICK_FROZEN_MODEL_ARTIFACT_V1"
MODEL_CONTRACT = "GANN_CANDLESTICK_TRANSPARENT_LOGISTIC_MODEL_V1"
GENESIS_HASH = "0" * 64
BAR_DELTA = pd.Timedelta(hours=1)


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


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _fingerprint(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


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


def _model_identity(model: Mapping[str, Any]) -> dict[str, Any]:
    identity = dict(model)
    identity.pop("modelId", None)
    identity.pop("trainingProbabilityRange", None)
    return identity


def load_frozen_model(path: Path | str) -> dict[str, Any]:
    model_path = Path(path).expanduser().resolve()
    artifact = json.loads(model_path.read_text(encoding="utf-8"))
    if artifact.get("contract") != ARTIFACT_CONTRACT:
        raise ValueError("Unsupported candlestick shadow model artifact")
    if artifact.get("status") != "prospective_shadow_research_only":
        raise ValueError("Candlestick model lost its research-only status")
    if artifact.get("symbol") != "USDJPY" or artifact.get("timeframe") != "H1":
        raise ValueError("Version 1 supports only USDJPY H1")
    if artifact.get("geometryMethodologyVersion") != METHODOLOGY_VERSION:
        raise ValueError("Candlestick geometry methodology drifted")
    decision = artifact.get("decision") or {}
    if int(decision.get("minimumHistoryBars", 0)) < 21:
        raise ValueError("Candlestick model requires at least 21 history bars")
    if int(decision.get("holdingBars", 0)) != 6:
        raise ValueError("Version 1 freezes the outcome at six held H1 bars")
    if int(decision.get("captureGraceMinutes", 0)) != 15:
        raise ValueError("Version 1 freezes capture grace at 15 minutes")
    if decision.get("lateDecisionBackfillAllowed") is not False:
        raise ValueError("Late decision backfill must remain disabled")
    guardrails = artifact.get("guardrails") or {}
    required_false = (
        "consumedByAstrologyRules",
        "consumedByAutoSuggest",
        "consumedByOfficialMlNotes",
        "consumedByCoordinator",
        "executionAllowed",
    )
    if any(guardrails.get(key) is not False for key in required_false):
        raise ValueError("Candlestick shadow guardrails drifted")
    if guardrails.get("mt5ReadOnly") is not True:
        raise ValueError("MT5 must remain read-only")
    if (artifact.get("retrospectiveGate") or {}).get("status") != "failed":
        raise ValueError("The failed retrospective primary gate must remain visible")
    if (artifact.get("retrospectiveGate") or {}).get("promotionAuthorized") is not False:
        raise ValueError("Retrospective promotion must remain unauthorized")
    primary = artifact.get("primaryModel") or {}
    diagnostics = artifact.get("diagnosticModels") or []
    if primary.get("name") != "named_pattern_logistic_v1" or len(diagnostics) != 1:
        raise ValueError("Frozen model roster drifted")
    for model in [primary, *diagnostics]:
        if model.get("contract") != MODEL_CONTRACT:
            raise ValueError("Unsupported transparent logistic model")
        features = list(model.get("features") or [])
        sizes = {
            len(features),
            len(model.get("scalerMean") or []),
            len(model.get("scalerScale") or []),
            len(model.get("coefficients") or []),
        }
        if len(sizes) != 1 or not features:
            raise ValueError("Frozen model vector lengths do not match")
        if any(float(value) <= 0.0 for value in model["scalerScale"]):
            raise ValueError("Frozen model contains a non-positive scale")
        if model.get("classes") != [0, 1]:
            raise ValueError("Frozen model classes drifted")
        if _fingerprint(_model_identity(model)) != str(model.get("modelId") or ""):
            raise ValueError(f"Frozen model identity mismatch: {model.get('name')}")
    identity = dict(artifact)
    identity.pop("artifactId", None)
    identity.pop("frozenAtUtc", None)
    if _fingerprint(identity) != str(artifact.get("artifactId") or ""):
        raise ValueError("Candlestick artifact identity mismatch")
    artifact["artifactSha256"] = _sha256_file(model_path)
    artifact["artifactPath"] = str(model_path)
    return artifact


def bars_to_frame(bars: list[dict[str, Any]]) -> pd.DataFrame:
    if not bars:
        raise ValueError("MT5 returned no bars")
    frame = pd.DataFrame(bars).copy()
    required = {"time", "open", "high", "low", "close"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"MT5 bars are missing columns: {missing}")
    frame["time"] = pd.to_datetime(frame["time"], unit="s", utc=True)
    frame = frame.drop_duplicates("time", keep="last").set_index("time").sort_index()
    numeric = frame.loc[:, ["open", "high", "low", "close"]].apply(
        pd.to_numeric, errors="coerce"
    )
    if frame.empty or frame.index.has_duplicates or not np.isfinite(numeric).all().all():
        raise ValueError("MT5 bars contain invalid timestamps or OHLC values")
    if (numeric["high"] < numeric[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("MT5 bars contain an invalid high")
    if (numeric["low"] > numeric[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("MT5 bars contain an invalid low")
    return frame


def _geometry_records(frame: pd.DataFrame, pip_size: float) -> list[dict[str, Any]]:
    geometry = pd.DataFrame(
        {
            "time": frame.index,
            "open": frame["open"].to_numpy(dtype=float),
            "high": frame["high"].to_numpy(dtype=float),
            "low": frame["low"].to_numpy(dtype=float),
            "close": frame["close"].to_numpy(dtype=float),
        }
    )
    return _records(geometry, 3600, 1.0 / pip_size)


def feature_snapshot(
    frame: pd.DataFrame,
    artifact: Mapping[str, Any],
    observed_at: Any,
) -> dict[str, Any]:
    now = _utc_timestamp(observed_at, "observed_at")
    decision = artifact["decision"]
    minimum_history = int(decision["minimumHistoryBars"])
    grace = pd.Timedelta(minutes=int(decision["captureGraceMinutes"]))
    pip_size = float(decision["pipSize"])
    normalized = frame.copy().sort_index()
    if not isinstance(normalized.index, pd.DatetimeIndex) or normalized.index.tz is None:
        raise ValueError("MT5 evidence must have timezone-aware timestamps")
    normalized.index = normalized.index.tz_convert("UTC")
    closed = normalized.loc[normalized.index + BAR_DELTA <= now].copy()
    if len(closed) < minimum_history + 1:
        raise ValueError("MT5 has insufficient fully closed H1 history")
    decision_open = closed.index[-1]
    feature_available = decision_open + BAR_DELTA
    lag = now - feature_available
    if lag < pd.Timedelta(0):
        raise ValueError("Latest candidate H1 bar is not closed")
    if lag > grace:
        raise ValueError(
            f"Latest closed H1 bar is {lag.total_seconds() / 60:.1f} minutes old; "
            "late decisions are never backfilled"
        )
    training_cutoff = _utc_timestamp(
        artifact["training"]["lastLabelAvailableAtUtc"], "training cutoff"
    )
    if feature_available <= training_cutoff:
        raise ValueError("Candidate is not prospective relative to the frozen training labels")
    history = closed.iloc[-(minimum_history + 1) :].copy()
    records = _geometry_records(history, pip_size)
    record = records[-1]
    source = history.iloc[-1]
    previous = history.iloc[-2]
    candle_range = max(float(source["high"] - source["low"]), 1e-12)
    signed_body = float(source["close"] - source["open"])
    atr_pips = float(record.get("atr14Pips") or 0.0)
    atr_price = atr_pips * pip_size
    patterns = list(record.get("patterns") or [])
    pattern_map = {str(item.get("name") or ""): item for item in patterns}
    raw_decision_bar_open = int(
        source.get("raw_time", int(decision_open.timestamp()))
    )
    features: dict[str, float] = {
        "body_signed_fraction": signed_body / candle_range,
        "upper_wick_fraction": float(record["upperWickFraction"]),
        "lower_wick_fraction": float(record["lowerWickFraction"]),
        "close_location": float(record["closeLocation"]),
        "range_atr_ratio": float(record["rangePips"]) / max(atr_pips, 1e-12),
        "pretrend_signed_strength_atr": float(record["preTrendStrengthAtr"]),
        "gap_from_prior_close_atr": (
            float(source["open"]) - float(previous["close"])
        )
        / max(atr_price, 1e-12),
    }
    for name in (
        "doji",
        "spinning_top",
        "marubozu_like",
        "long_bullish_body",
        "long_bearish_body",
        "long_lower_wick",
        "long_upper_wick",
        "bullish_body_engulfing",
        "bearish_body_engulfing",
        "inside_bar",
        "outside_bar",
    ):
        features[f"pattern_{name}"] = float(name in pattern_map)
    input_rows = [
        {
            "time": timestamp.isoformat(),
            "rawServerEpochSeconds": int(
                row.get("raw_time", int(timestamp.timestamp()))
            ),
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
        }
        for timestamp, row in history.iterrows()
    ]
    return {
        "decisionBarOpenUtc": decision_open.isoformat(),
        "featureAvailableAtUtc": feature_available.isoformat(),
        "rawDecisionBarOpenServerEpochSeconds": raw_decision_bar_open,
        "rawFeatureAvailableServerEpochSeconds": raw_decision_bar_open + 3600,
        "captureLagSeconds": int(lag.total_seconds()),
        "ohlc": input_rows[-1],
        "features": features,
        "patterns": patterns,
        "preTrend": str(record.get("preTrend") or ""),
        "atr14Pips": atr_pips,
        "inputBars": len(input_rows),
        "inputBarsSha256": _fingerprint(input_rows),
    }


def evaluate_model(model: Mapping[str, Any], features: Mapping[str, float]) -> dict[str, Any]:
    names = list(model["features"])
    values = np.asarray([float(features[name]) for name in names], dtype=float)
    means = np.asarray(model["scalerMean"], dtype=float)
    scales = np.asarray(model["scalerScale"], dtype=float)
    coefficients = np.asarray(model["coefficients"], dtype=float)
    logit = float(np.dot((values - means) / scales, coefficients) + float(model["intercept"]))
    probability = 1.0 / (1.0 + math.exp(-max(-700.0, min(700.0, logit))))
    short_threshold = float(model["shortProbability"])
    long_threshold = float(model["longProbability"])
    action = "long" if probability >= long_threshold else "short" if probability <= short_threshold else "abstain"
    return {
        "name": str(model["name"]),
        "modelId": str(model["modelId"]),
        "probabilityUp": probability,
        "action": action,
        "shortProbability": short_threshold,
        "longProbability": long_threshold,
    }


def build_decision_payload(
    snapshot: Mapping[str, Any],
    artifact: Mapping[str, Any],
    observed_at: Any,
    time_normalization: Mapping[str, Any],
) -> dict[str, Any]:
    now = _utc_timestamp(observed_at, "observed_at")
    primary = evaluate_model(artifact["primaryModel"], snapshot["features"])
    diagnostics = [
        {**evaluate_model(model, snapshot["features"]), "diagnosticOnly": True}
        for model in artifact["diagnosticModels"]
    ]
    decision_id = _fingerprint(
        {
            "contract": DECISION_CONTRACT,
            "artifactId": artifact["artifactId"],
            "symbol": artifact["symbol"],
            "timeframe": artifact["timeframe"],
            "decisionBarOpenUtc": snapshot["decisionBarOpenUtc"],
        }
    )
    return {
        "contract": DECISION_CONTRACT,
        "decisionId": decision_id,
        "recordedAtUtc": now.isoformat(),
        "symbol": artifact["symbol"],
        "timeframe": artifact["timeframe"],
        "artifactId": artifact["artifactId"],
        "artifactSha256": artifact["artifactSha256"],
        "primary": primary,
        "diagnostics": diagnostics,
        "decisionBarOpenUtc": snapshot["decisionBarOpenUtc"],
        "featureAvailableAtUtc": snapshot["featureAvailableAtUtc"],
        "rawDecisionBarOpenServerEpochSeconds": snapshot[
            "rawDecisionBarOpenServerEpochSeconds"
        ],
        "rawFeatureAvailableServerEpochSeconds": snapshot[
            "rawFeatureAvailableServerEpochSeconds"
        ],
        "captureLagSeconds": snapshot["captureLagSeconds"],
        "ohlc": snapshot["ohlc"],
        "features": snapshot["features"],
        "patterns": snapshot["patterns"],
        "preTrend": snapshot["preTrend"],
        "atr14Pips": snapshot["atr14Pips"],
        "inputBars": snapshot["inputBars"],
        "inputBarsSha256": snapshot["inputBarsSha256"],
        "timeNormalization": dict(time_normalization),
        "holdingBars": int(artifact["decision"]["holdingBars"]),
        "entryPolicy": "next_bar_open",
        "exitPolicy": "sixth_held_bar_close",
        "guardrails": {
            "prospectiveOnly": True,
            "lateBackfillAllowed": False,
            "diagnosticModelCanTrade": False,
            "consumedByAstrologyRules": False,
            "consumedByAutoSuggest": False,
            "consumedByOfficialMlNotes": False,
            "consumedByCoordinator": False,
            "executionAllowed": False,
            "mt5ReadOnly": True,
        },
    }


def build_outcome_payload(
    decision_payload: Mapping[str, Any],
    frame: pd.DataFrame,
    artifact: Mapping[str, Any],
    observed_at: Any,
    time_normalization: Mapping[str, Any],
) -> dict[str, Any] | None:
    now = _utc_timestamp(observed_at, "observed_at")
    feature_time = _utc_timestamp(
        decision_payload["featureAvailableAtUtc"], "feature available time"
    )
    normalized = frame.copy().sort_index()
    normalized.index = normalized.index.tz_convert("UTC")
    held = normalized.loc[
        (normalized.index >= feature_time) & (normalized.index + BAR_DELTA <= now)
    ]
    holding_bars = int(artifact["decision"]["holdingBars"])
    if len(held) < holding_bars:
        return None
    selected = held.iloc[:holding_bars]
    entry_time = selected.index[0]
    exit_open_time = selected.index[-1]
    exit_time = exit_open_time + BAR_DELTA
    entry_price = float(selected.iloc[0]["open"])
    exit_price = float(selected.iloc[-1]["close"])
    raw_entry_time = int(
        selected.iloc[0].get("raw_time", int(entry_time.timestamp()))
    )
    raw_exit_open_time = int(
        selected.iloc[-1].get("raw_time", int(exit_open_time.timestamp()))
    )
    pip_size = float(artifact["decision"]["pipSize"])
    gross_long = (exit_price - entry_price) / pip_size
    spread = float(artifact["costs"]["fallbackSpreadPips"])
    slippage = 2.0 * float(artifact["costs"]["slippagePipsPerSide"])
    total_cost = spread + slippage

    def candidate_result(candidate: Mapping[str, Any]) -> dict[str, Any]:
        action = str(candidate["action"])
        signed_gross = gross_long if action == "long" else -gross_long if action == "short" else None
        return {
            "name": candidate["name"],
            "modelId": candidate["modelId"],
            "action": action,
            "signedGrossPips": signed_gross,
            "netPips": signed_gross - total_cost if signed_gross is not None else None,
            "tradeOccurred": action != "abstain",
            "executionOccurred": False,
        }

    return {
        "contract": OUTCOME_CONTRACT,
        "decisionId": decision_payload["decisionId"],
        "recordedAtUtc": now.isoformat(),
        "entryTimeUtc": entry_time.isoformat(),
        "exitTimeUtc": exit_time.isoformat(),
        "rawEntryBarOpenServerEpochSeconds": raw_entry_time,
        "rawExitBarOpenServerEpochSeconds": raw_exit_open_time,
        "rawExitAvailableServerEpochSeconds": raw_exit_open_time + 3600,
        "entryPrice": entry_price,
        "exitPrice": exit_price,
        "heldBars": holding_bars,
        "grossLongPips": gross_long,
        "targetUp": bool(gross_long > 0.0),
        "spreadPips": spread,
        "slippagePips": slippage,
        "totalCostPips": total_cost,
        "spreadSource": "frozen_fixed_fallback",
        "timeNormalization": dict(time_normalization),
        "decisionTimeNormalizationSha256": _fingerprint(
            decision_payload["timeNormalization"]
        ),
        "primary": candidate_result(decision_payload["primary"]),
        "diagnostics": [candidate_result(item) for item in decision_payload["diagnostics"]],
        "guardrails": {
            "retrospectiveBackfill": False,
            "sixActualSubsequentBars": True,
            "executionOccurred": False,
            "executionAllowed": False,
        },
    }


def _entry_hash_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract": LEDGER_CONTRACT,
        "sequence": int(row["ledger_sequence"]),
        "entryId": str(row["entry_id"]),
        "entryType": str(row["entry_type"]),
        "decisionId": str(row["decision_id"]),
        "effectiveAtUtc": str(row["effective_at_utc"]),
        "recordedAtUtc": str(row["recorded_at_utc"]),
        "payloadSha256": str(row["payload_sha256"]),
        "previousEntryHash": str(row["previous_entry_hash"]),
    }


class CandlestickShadowStore:
    def __init__(self, database_path: Path | str, artifact: Mapping[str, Any]) -> None:
        self.database_path = Path(database_path).expanduser().resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifact = dict(artifact)
        self._lock = threading.RLock()
        self.initialize()
        self.ensure_manifest()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS candlestick_shadow_manifest (
                    singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
                    trial_id TEXT NOT NULL UNIQUE,
                    contract TEXT NOT NULL,
                    identity_json TEXT NOT NULL,
                    identity_sha256 TEXT NOT NULL,
                    established_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS candlestick_shadow_entries (
                    ledger_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT NOT NULL UNIQUE,
                    entry_type TEXT NOT NULL CHECK(entry_type IN ('decision', 'outcome')),
                    decision_id TEXT NOT NULL,
                    effective_at_utc TEXT NOT NULL,
                    recorded_at_utc TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    previous_entry_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_candle_shadow_subject
                    ON candlestick_shadow_entries(entry_type, decision_id);
                CREATE TRIGGER IF NOT EXISTS trg_candle_shadow_no_update
                BEFORE UPDATE ON candlestick_shadow_entries
                BEGIN
                    SELECT RAISE(ABORT, 'candlestick shadow ledger is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS trg_candle_shadow_no_delete
                BEFORE DELETE ON candlestick_shadow_entries
                BEGIN
                    SELECT RAISE(ABORT, 'candlestick shadow ledger is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS trg_candle_shadow_manifest_no_update
                BEFORE UPDATE ON candlestick_shadow_manifest
                BEGIN
                    SELECT RAISE(ABORT, 'candlestick shadow manifest is immutable');
                END;
                CREATE TRIGGER IF NOT EXISTS trg_candle_shadow_manifest_no_delete
                BEFORE DELETE ON candlestick_shadow_manifest
                BEGIN
                    SELECT RAISE(ABORT, 'candlestick shadow manifest is immutable');
                END;
                """
            )
            connection.commit()

    def manifest_identity(self) -> dict[str, Any]:
        return {
            "contract": TRIAL_CONTRACT,
            "artifactId": self.artifact["artifactId"],
            "artifactSha256": self.artifact["artifactSha256"],
            "primaryModelId": self.artifact["primaryModel"]["modelId"],
            "diagnosticModelIds": [
                item["modelId"] for item in self.artifact["diagnosticModels"]
            ],
            "symbol": self.artifact["symbol"],
            "timeframe": self.artifact["timeframe"],
            "decision": self.artifact["decision"],
            "costs": self.artifact["costs"],
            "retrospectiveGate": self.artifact["retrospectiveGate"],
            "guardrails": self.artifact["guardrails"],
            "timeNormalization": normalization_probe_identity(),
        }

    def ensure_manifest(self) -> None:
        identity = self.manifest_identity()
        identity_json = _canonical_json(identity)
        identity_sha = _sha256_text(identity_json)
        trial_id = _fingerprint({"contract": TRIAL_CONTRACT, "identitySha256": identity_sha})
        with self._lock, self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM candlestick_shadow_manifest WHERE singleton_id = 1"
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO candlestick_shadow_manifest(
                        singleton_id, trial_id, contract, identity_json,
                        identity_sha256, established_at_utc
                    ) VALUES(1, ?, ?, ?, ?, ?)
                    """,
                    (
                        trial_id,
                        TRIAL_CONTRACT,
                        identity_json,
                        identity_sha,
                        _utc_now().isoformat(),
                    ),
                )
                connection.commit()
                return
            if (
                row["contract"] != TRIAL_CONTRACT
                or row["identity_sha256"] != identity_sha
                or row["identity_json"] != identity_json
                or row["trial_id"] != trial_id
            ):
                raise ValueError("Existing candlestick shadow database belongs to another frozen trial")

    def append(
        self,
        entry_type: str,
        decision_id: str,
        effective_at: Any,
        recorded_at: Any,
        payload: Mapping[str, Any],
    ) -> bool:
        effective = _utc_timestamp(effective_at, "effective_at")
        recorded = _utc_timestamp(recorded_at, "recorded_at")
        if recorded < effective:
            raise ValueError("A shadow entry cannot be recorded before it becomes effective")
        payload_json = _canonical_json(payload)
        payload_sha = _sha256_text(payload_json)
        entry_id = _fingerprint(
            {
                "contract": LEDGER_CONTRACT,
                "entryType": entry_type,
                "decisionId": decision_id,
                "payloadSha256": payload_sha,
            }
        )
        with self._lock, self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT payload_sha256 FROM candlestick_shadow_entries WHERE entry_type = ? AND decision_id = ?",
                (entry_type, decision_id),
            ).fetchone()
            if existing is not None:
                if existing["payload_sha256"] != payload_sha:
                    raise ValueError("An immutable candlestick shadow subject changed payload")
                connection.rollback()
                return False
            previous = connection.execute(
                "SELECT ledger_sequence, entry_hash FROM candlestick_shadow_entries ORDER BY ledger_sequence DESC LIMIT 1"
            ).fetchone()
            previous_hash = previous["entry_hash"] if previous else GENESIS_HASH
            sequence = int(previous["ledger_sequence"]) + 1 if previous else 1
            row = {
                "ledger_sequence": sequence,
                "entry_id": entry_id,
                "entry_type": entry_type,
                "decision_id": decision_id,
                "effective_at_utc": effective.isoformat(),
                "recorded_at_utc": recorded.isoformat(),
                "payload_sha256": payload_sha,
                "previous_entry_hash": previous_hash,
            }
            entry_hash = _fingerprint(_entry_hash_payload(row))
            connection.execute(
                """
                INSERT INTO candlestick_shadow_entries(
                    ledger_sequence, entry_id, entry_type, decision_id, effective_at_utc,
                    recorded_at_utc, payload_json, payload_sha256,
                    previous_entry_hash, entry_hash
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sequence,
                    entry_id,
                    entry_type,
                    decision_id,
                    effective.isoformat(),
                    recorded.isoformat(),
                    payload_json,
                    payload_sha,
                    previous_hash,
                    entry_hash,
                ),
            )
            connection.commit()
        return True

    def pending_decisions(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT decision.payload_json
                FROM candlestick_shadow_entries decision
                LEFT JOIN candlestick_shadow_entries outcome
                    ON outcome.entry_type = 'outcome'
                   AND outcome.decision_id = decision.decision_id
                WHERE decision.entry_type = 'decision' AND outcome.ledger_sequence IS NULL
                ORDER BY decision.ledger_sequence
                """
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def has_decision(self, decision_id: str) -> bool:
        with self.connect() as connection:
            return (
                connection.execute(
                    "SELECT 1 FROM candlestick_shadow_entries WHERE entry_type = 'decision' AND decision_id = ?",
                    (decision_id,),
                ).fetchone()
                is not None
            )

    def verify_chain(self) -> dict[str, Any]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM candlestick_shadow_entries ORDER BY ledger_sequence"
            ).fetchall()
        previous = GENESIS_HASH
        for expected_sequence, row in enumerate(rows, start=1):
            values = dict(row)
            if int(values["ledger_sequence"]) != expected_sequence:
                raise ValueError("Candlestick shadow ledger sequence is not contiguous")
            if values["previous_entry_hash"] != previous:
                raise ValueError("Candlestick shadow previous hash mismatch")
            if _sha256_text(values["payload_json"]) != values["payload_sha256"]:
                raise ValueError("Candlestick shadow payload hash mismatch")
            if _fingerprint(_entry_hash_payload(values)) != values["entry_hash"]:
                raise ValueError("Candlestick shadow entry hash mismatch")
            previous = values["entry_hash"]
        return {"ok": True, "entries": len(rows), "headHash": previous}

    def snapshot(self, limit: int = 100) -> dict[str, Any]:
        integrity = self.verify_chain()
        with self.connect() as connection:
            manifest = dict(
                connection.execute(
                    "SELECT * FROM candlestick_shadow_manifest WHERE singleton_id = 1"
                ).fetchone()
            )
            totals = connection.execute(
                """
                SELECT
                    SUM(CASE WHEN entry_type = 'decision' THEN 1 ELSE 0 END) decisions,
                    SUM(CASE WHEN entry_type = 'outcome' THEN 1 ELSE 0 END) outcomes
                FROM candlestick_shadow_entries
                """
            ).fetchone()
            rows = connection.execute(
                "SELECT * FROM candlestick_shadow_entries ORDER BY ledger_sequence DESC LIMIT ?",
                (max(1, min(int(limit), 500)),),
            ).fetchall()
        decisions = int(totals["decisions"] or 0)
        outcomes = int(totals["outcomes"] or 0)
        records = []
        for row in rows:
            values = dict(row)
            records.append(
                {
                    "sequence": int(values["ledger_sequence"]),
                    "entryId": values["entry_id"],
                    "entryType": values["entry_type"],
                    "decisionId": values["decision_id"],
                    "effectiveAtUtc": values["effective_at_utc"],
                    "recordedAtUtc": values["recorded_at_utc"],
                    "payloadSha256": values["payload_sha256"],
                    "entryHash": values["entry_hash"],
                    "payload": json.loads(values["payload_json"]),
                }
            )
        return {
            "contract": LEDGER_CONTRACT,
            "trial": {
                "trialId": manifest["trial_id"],
                "contract": manifest["contract"],
                "identitySha256": manifest["identity_sha256"],
                "establishedAtUtc": manifest["established_at_utc"],
            },
            "model": {
                "artifactId": self.artifact["artifactId"],
                "artifactSha256": self.artifact["artifactSha256"],
                "primaryModelId": self.artifact["primaryModel"]["modelId"],
                "retrospectiveGate": self.artifact["retrospectiveGate"],
            },
            "summary": {
                "decisions": decisions,
                "outcomes": outcomes,
                "pending": max(0, decisions - outcomes),
            },
            "integrity": integrity,
            "records": records,
            "guardrails": self.artifact["guardrails"],
        }


class CandlestickShadowSupervisor:
    def __init__(
        self,
        gateway: Any,
        *,
        model_path: Path | str,
        database_path: Path | str,
        clock_probe_path: Path | str | None = None,
        autostart: bool = True,
        poll_seconds: float = 20.0,
    ) -> None:
        self.gateway = gateway
        self.artifact = load_frozen_model(model_path)
        self.store = CandlestickShadowStore(database_path, self.artifact)
        self.clock_probe_path = (
            Path(clock_probe_path).expanduser().resolve()
            if clock_probe_path is not None
            else None
        )
        self.poll_seconds = max(2.0, float(poll_seconds))
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_scan: dict[str, Any] = {
            "state": "not_scanned",
            "observedAtUtc": None,
            "decisionAppended": False,
            "outcomesAppended": 0,
            "message": "Waiting for the first read-only MT5 scan.",
            "timeNormalization": None,
        }
        if autostart:
            self.start()

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._loop, name="candlestick-shadow", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.scan_once()
            except Exception as exc:
                with self._lock:
                    self._last_scan = {
                        "state": "error",
                        "observedAtUtc": _utc_now().isoformat(),
                        "decisionAppended": False,
                        "outcomesAppended": 0,
                        "message": str(exc),
                    }
            self._stop.wait(self.poll_seconds)

    def scan_once(
        self,
        *,
        observed_at: Any | None = None,
        bars: list[dict[str, Any]] | None = None,
        clock_probe: Mapping[str, Any] | None = None,
        raw_market_tick_epoch_seconds: int | None = None,
    ) -> dict[str, Any]:
        now = _utc_timestamp(observed_at or _utc_now(), "observed_at")
        evidence = bars if bars is not None else self.gateway.bars("USDJPY", "H1", 5000)
        status = (
            self.gateway.status()
            if callable(getattr(self.gateway, "status", None))
            else {}
        )
        raw_tick = raw_market_tick_epoch_seconds
        if raw_tick is None:
            raw_tick = status.get("rawLastTickServerEpochSeconds")
        if raw_tick is None:
            with self._lock:
                self._last_scan = {
                    "state": "skipped",
                    "observedAtUtc": now.isoformat(),
                    "decisionAppended": False,
                    "outcomesAppended": 0,
                    "message": "MT5 did not expose a raw timestamped market tick; no entry was appended.",
                    "timeNormalization": None,
                }
            return self.status()
        try:
            raw_h1 = max(int(row["time"]) for row in evidence)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("MT5 H1 evidence does not expose raw server timestamps") from exc
        probe_path = self.clock_probe_path or default_clock_probe_path(
            status.get("terminalCommonDataPath")
        )
        try:
            probe = dict(clock_probe) if clock_probe is not None else read_clock_probe(probe_path)
        except (OSError, ValueError) as exc:
            with self._lock:
                self._last_scan = {
                    "state": "skipped",
                    "observedAtUtc": now.isoformat(),
                    "decisionAppended": False,
                    "outcomesAppended": 0,
                    "message": f"{exc}. No entry was appended.",
                    "timeNormalization": None,
                    "clockProbePath": str(probe_path),
                }
            return self.status()
        normalization = time_normalization_evidence(
            now.to_pydatetime(),
            int(raw_tick),
            raw_h1,
            probe,
            expected_symbol=str(self.artifact["symbol"]),
            expected_server=str(status.get("server") or "") or None,
            expected_terminal_build=int(status.get("terminalBuild") or 0) or None,
        )
        if not normalization["valid"]:
            issue = "; ".join(normalization["validationIssues"])
            with self._lock:
                self._last_scan = {
                    "state": "skipped",
                    "observedAtUtc": now.isoformat(),
                    "decisionAppended": False,
                    "outcomesAppended": 0,
                    "message": f"MT5 server-time normalization failed: {issue}. No entry was appended.",
                    "timeNormalization": normalization,
                    "clockProbePath": str(probe_path),
                }
            return self.status()
        frame = bars_to_frame(normalize_bars(evidence, normalization))
        outcomes = 0
        for decision_payload in self.store.pending_decisions():
            outcome = build_outcome_payload(
                decision_payload,
                frame,
                self.artifact,
                now,
                normalization,
            )
            if outcome is None:
                continue
            if self.store.append(
                "outcome",
                str(decision_payload["decisionId"]),
                outcome["exitTimeUtc"],
                outcome["recordedAtUtc"],
                outcome,
            ):
                outcomes += 1
        decision_appended = False
        message = "No new decision was eligible."
        state = "idle"
        try:
            snapshot = feature_snapshot(frame, self.artifact, now)
            decision_payload = build_decision_payload(
                snapshot, self.artifact, now, normalization
            )
            if self.store.has_decision(decision_payload["decisionId"]):
                state = "current"
                message = "The latest timely closed-bar decision already exists."
            else:
                decision_appended = self.store.append(
                    "decision",
                    decision_payload["decisionId"],
                    decision_payload["featureAvailableAtUtc"],
                    decision_payload["recordedAtUtc"],
                    decision_payload,
                )
                state = "captured"
                message = "Appended the latest timely closed-bar decision."
        except ValueError as exc:
            message = str(exc)
            state = "skipped"
        with self._lock:
            self._last_scan = {
                "state": state,
                "observedAtUtc": now.isoformat(),
                "decisionAppended": decision_appended,
                "outcomesAppended": outcomes,
                "message": message,
                "timeNormalization": normalization,
                "clockProbePath": str(probe_path),
            }
        return self.status()

    def status(self, limit: int = 100) -> dict[str, Any]:
        snapshot = self.store.snapshot(limit=limit)
        with self._lock:
            snapshot["lastScan"] = dict(self._last_scan)
        snapshot["databasePath"] = str(self.store.database_path)
        return snapshot


def default_model_path(project_root: Path) -> Path:
    configured = str(os.environ.get("GANN_ASTRO_CANDLE_SHADOW_MODEL") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    packaged = project_root / "candlestick" / "usdjpy_shadow_model_v1.json"
    source = project_root / "candlestick_agent" / "usdjpy_shadow_model_v1.json"
    return packaged if packaged.is_file() else source
