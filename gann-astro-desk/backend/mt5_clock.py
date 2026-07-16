from __future__ import annotations

import csv
import hashlib
import io
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


CLOCK_PROBE_CONTRACT = "GANN_MT5_CLOCK_PROBE_V1"
TIME_NORMALIZATION_CONTRACT = "GANN_MT5_SERVER_TIME_NORMALIZATION_V1"
PROBE_FILENAME = "gann_mt5_clock_probe_v1.csv"
PROBE_DEPLOYMENT_CONTRACT = "GANN_MT5_CLOCK_PROBE_DEPLOYMENT_V1"
OFFSET_GRID_SECONDS = 15 * 60
MAX_ABSOLUTE_OFFSET_SECONDS = 14 * 60 * 60
MAX_OFFSET_RESIDUAL_SECONDS = 5
MAX_PROBE_AGE_SECONDS = 30
MAX_FUTURE_PROBE_SECONDS = 5
MAX_NORMALIZED_TICK_SKEW_SECONDS = 5 * 60
MAX_TICK_SOURCE_DIFFERENCE_SECONDS = 5
MAX_H1_SOURCE_DIFFERENCE_SECONDS = 60 * 60


def _utc_datetime(value: Any, label: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip().replace("Z", "+00:00")
        if not text:
            raise ValueError(f"{label} is required")
        parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _epoch_iso(value: int | float) -> str:
    return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()


def _integer(row: Mapping[str, str], name: str) -> int:
    try:
        return int(str(row.get(name) or "").strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"MT5 clock probe field {name!r} is not an integer") from exc


def _number(row: Mapping[str, str], name: str) -> float:
    try:
        return float(str(row.get(name) or "").strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"MT5 clock probe field {name!r} is not numeric") from exc


def _boolean(row: Mapping[str, str], name: str) -> bool:
    value = str(row.get(name) or "").strip().lower()
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no"}:
        return False
    raise ValueError(f"MT5 clock probe field {name!r} is not boolean")


def default_clock_probe_path(common_data_path: Path | str | None = None) -> Path:
    configured = str(os.environ.get("GANN_ASTRO_MT5_CLOCK_PROBE") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    if common_data_path:
        root = Path(common_data_path).expanduser().resolve()
    else:
        appdata = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        root = appdata / "MetaQuotes" / "Terminal" / "Common"
    files_root = root if root.name.lower() == "files" else root / "Files"
    return (files_root / PROBE_FILENAME).resolve()


def deploy_clock_probe(
    bundle_root: Path | str | None,
    terminal_data_path: Path | str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "contract": PROBE_DEPLOYMENT_CONTRACT,
        "available": False,
        "deployed": False,
        "changed": False,
        "appExecutionAllowed": False,
    }
    if not bundle_root or not terminal_data_path:
        result["message"] = "Clock probe bundle or terminal data path is unavailable."
        return result
    source_root = Path(bundle_root).expanduser().resolve()
    target_root = (
        Path(terminal_data_path).expanduser().resolve()
        / "MQL5"
        / "Services"
        / "GannFinancialAstro"
    )
    sources = [source_root / "GannClockProbe.mq5", source_root / "GannClockProbe.ex5"]
    missing = [str(path) for path in sources if not path.is_file()]
    result.update(
        {
            "bundleRoot": str(source_root),
            "targetRoot": str(target_root),
            "missing": missing,
        }
    )
    if missing:
        result["message"] = "Packaged clock probe files are missing."
        return result
    result["available"] = True
    target_root.mkdir(parents=True, exist_ok=True)
    changed = False
    files: list[dict[str, Any]] = []
    for source in sources:
        target = target_root / source.name
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest().upper()
        target_hash = (
            hashlib.sha256(target.read_bytes()).hexdigest().upper()
            if target.is_file()
            else None
        )
        if target_hash != source_hash:
            shutil.copy2(source, target)
            target_hash = hashlib.sha256(target.read_bytes()).hexdigest().upper()
            changed = True
        if target_hash != source_hash:
            raise OSError(f"Clock probe deployment hash mismatch: {target}")
        files.append(
            {
                "name": source.name,
                "sourceSha256": source_hash,
                "targetSha256": target_hash,
                "targetPath": str(target),
            }
        )
    result.update(
        {
            "deployed": True,
            "changed": changed,
            "files": files,
            "message": (
                "Clock probe files were updated. Restart its service instance to load the new binary."
                if changed
                else "Clock probe files match the packaged read-only binary."
            ),
        }
    )
    return result


def _stable_probe_bytes(path: Path, attempts: int = 3) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(f"MT5 clock probe is missing: {path}")
    previous = path.read_bytes()
    for _ in range(max(1, attempts)):
        time.sleep(0.02)
        current = path.read_bytes()
        if current == previous and current:
            return current
        previous = current
    raise ValueError("MT5 clock probe changed while it was being read")


def read_clock_probe(path: Path | str) -> dict[str, Any]:
    probe_path = Path(path).expanduser().resolve()
    raw = _stable_probe_bytes(probe_path)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) != 1:
        raise ValueError("MT5 clock probe must contain exactly one evidence row")
    row = rows[0]
    if str(row.get("contract") or "").strip() != CLOCK_PROBE_CONTRACT:
        raise ValueError("Unsupported MT5 clock probe contract")
    return {
        "contract": CLOCK_PROBE_CONTRACT,
        "probeSequence": _integer(row, "probe_sequence"),
        "writtenAtGmtEpochSeconds": _integer(row, "written_at_gmt_epoch"),
        "timeCurrentEpochSeconds": _integer(row, "time_current_epoch"),
        "timeTradeServerEpochSeconds": _integer(row, "time_trade_server_epoch"),
        "timeGmtEpochSeconds": _integer(row, "time_gmt_epoch"),
        "timeLocalEpochSeconds": _integer(row, "time_local_epoch"),
        "timeGmtOffsetSeconds": _integer(row, "time_gmt_offset_seconds"),
        "rawTickEpochSeconds": _integer(row, "tick_time_epoch"),
        "rawTickMilliseconds": _integer(row, "tick_time_msc"),
        "rawH1BarOpenEpochSeconds": _integer(row, "h1_bar_time_epoch"),
        "terminalBuild": _integer(row, "terminal_build"),
        "terminalName": str(row.get("terminal_name") or "").strip(),
        "terminalCompany": str(row.get("terminal_company") or "").strip(),
        "terminalDataPath": str(row.get("terminal_data_path") or "").strip(),
        "terminalCommonDataPath": str(row.get("terminal_common_data_path") or "").strip(),
        "terminalConnected": _boolean(row, "terminal_connected"),
        "terminalAllowsTrading": _boolean(row, "terminal_trade_allowed"),
        "accountLogin": _integer(row, "account_login"),
        "accountServer": str(row.get("account_server") or "").strip(),
        "accountCompany": str(row.get("account_company") or "").strip(),
        "accountAllowsTrading": _boolean(row, "account_trade_allowed"),
        "accountExpertTradingAllowed": _boolean(row, "account_trade_expert"),
        "symbol": str(row.get("symbol") or "").strip().upper(),
        "bid": _number(row, "bid"),
        "ask": _number(row, "ask"),
        "periodSeconds": _integer(row, "period_seconds"),
        "writeIntervalMilliseconds": _integer(row, "write_interval_ms"),
        "probePath": str(probe_path),
        "probeFileSha256": hashlib.sha256(raw).hexdigest().upper(),
    }


def time_normalization_evidence(
    observed_at: Any,
    raw_market_tick_epoch_seconds: int | float,
    raw_h1_bar_open_epoch_seconds: int | float,
    probe: Mapping[str, Any],
    *,
    expected_symbol: str = "USDJPY",
    expected_server: str | None = None,
    expected_terminal_build: int | None = None,
) -> dict[str, Any]:
    observed = _utc_datetime(observed_at, "observed_at")
    observed_epoch = observed.timestamp()
    raw_tick = int(raw_market_tick_epoch_seconds)
    raw_h1 = int(raw_h1_bar_open_epoch_seconds)
    gmt = int(probe["timeGmtEpochSeconds"])
    local = int(probe["timeLocalEpochSeconds"])
    current = int(probe["timeCurrentEpochSeconds"])
    trade_server = int(probe["timeTradeServerEpochSeconds"])
    probe_tick = int(probe["rawTickEpochSeconds"])
    probe_h1 = int(probe["rawH1BarOpenEpochSeconds"])
    raw_offset = trade_server - gmt
    rounded_offset = int(round(raw_offset / OFFSET_GRID_SECONDS) * OFFSET_GRID_SECONDS)
    offset_residual = raw_offset - rounded_offset
    normalized_tick_epoch = raw_tick - rounded_offset
    normalized_h1_epoch = raw_h1 - rounded_offset
    probe_age = observed_epoch - gmt
    normalized_tick_skew = normalized_tick_epoch - observed_epoch
    reasons: list[str] = []

    if probe.get("contract") != CLOCK_PROBE_CONTRACT:
        reasons.append("probe contract mismatch")
    if not bool(probe.get("terminalConnected")):
        reasons.append("MT5 terminal is not connected")
    if str(probe.get("symbol") or "").upper() != expected_symbol.upper():
        reasons.append("probe symbol does not match the frozen trial")
    if expected_server and str(probe.get("accountServer") or "") != expected_server:
        reasons.append("probe account server does not match the Python gateway")
    if expected_terminal_build and int(probe.get("terminalBuild") or 0) != int(expected_terminal_build):
        reasons.append("probe terminal build does not match the Python gateway")
    if probe_age > MAX_PROBE_AGE_SECONDS:
        reasons.append(f"probe is stale by {probe_age:.1f} seconds")
    if probe_age < -MAX_FUTURE_PROBE_SECONDS:
        reasons.append(f"probe GMT is {-probe_age:.1f} seconds in the future")
    if abs(raw_offset) > MAX_ABSOLUTE_OFFSET_SECONDS:
        reasons.append("measured server offset exceeds fourteen hours")
    if abs(offset_residual) > MAX_OFFSET_RESIDUAL_SECONDS:
        reasons.append("measured server offset is not on a fifteen-minute grid")
    if abs((gmt - local) - int(probe["timeGmtOffsetSeconds"])) > 2:
        reasons.append("probe local/GMT offset is internally inconsistent")
    if abs(probe_tick - current) > MAX_NORMALIZED_TICK_SKEW_SECONDS:
        reasons.append("probe tick and TimeCurrent disagree")
    if abs(raw_tick - probe_tick) > MAX_TICK_SOURCE_DIFFERENCE_SECONDS:
        reasons.append("Python and MQL5 raw tick times disagree")
    if abs(raw_h1 - probe_h1) > MAX_H1_SOURCE_DIFFERENCE_SECONDS:
        reasons.append("Python and MQL5 current H1 bar times disagree")
    if abs(normalized_tick_skew) > MAX_NORMALIZED_TICK_SKEW_SECONDS:
        reasons.append("normalized market tick is not close to observed UTC")
    h1_grid_residual = min(normalized_h1_epoch % 3600, 3600 - normalized_h1_epoch % 3600)
    if h1_grid_residual > 2:
        reasons.append("normalized H1 bar is not aligned to the one-hour UTC grid")

    probe_evidence = dict(probe)
    probe_evidence.update(
        {
            "writtenAtGmtUtc": _epoch_iso(int(probe["writtenAtGmtEpochSeconds"])),
            "timeCurrentServerEncoded": _epoch_iso(current),
            "timeTradeServerEncoded": _epoch_iso(trade_server),
            "timeGmtUtc": _epoch_iso(gmt),
            "timeLocalEncoded": _epoch_iso(local),
            "rawTickServerEncoded": _epoch_iso(probe_tick),
            "rawH1BarOpenServerEncoded": _epoch_iso(probe_h1),
            "ageSeconds": probe_age,
        }
    )
    return {
        "contract": TIME_NORMALIZATION_CONTRACT,
        "observedAtUtc": observed.isoformat(),
        "valid": not reasons,
        "failureMode": "skip_without_append",
        "validationIssues": reasons,
        "serverOffsetSeconds": rounded_offset,
        "rawMeasuredOffsetSeconds": raw_offset,
        "offsetResidualSeconds": offset_residual,
        "offsetSource": "TimeTradeServer-TimeGMT",
        "offsetGridSeconds": OFFSET_GRID_SECONDS,
        "maximumAbsoluteOffsetSeconds": MAX_ABSOLUTE_OFFSET_SECONDS,
        "maximumProbeAgeSeconds": MAX_PROBE_AGE_SECONDS,
        "maximumNormalizedTickSkewSeconds": MAX_NORMALIZED_TICK_SKEW_SECONDS,
        "rawMarketTickEpochSeconds": raw_tick,
        "rawMarketTickServerEncoded": _epoch_iso(raw_tick),
        "normalizedMarketTickUtc": _epoch_iso(normalized_tick_epoch),
        "normalizedMarketTickSkewSeconds": normalized_tick_skew,
        "rawH1BarOpenEpochSeconds": raw_h1,
        "rawH1BarOpenServerEncoded": _epoch_iso(raw_h1),
        "normalizedH1BarOpenUtc": _epoch_iso(normalized_h1_epoch),
        "normalizedH1GridResidualSeconds": h1_grid_residual,
        "probe": probe_evidence,
        "appExecutionAllowed": False,
    }


def normalize_epoch_seconds(value: int | float, evidence: Mapping[str, Any]) -> int:
    if evidence.get("contract") != TIME_NORMALIZATION_CONTRACT or evidence.get("valid") is not True:
        raise ValueError("MT5 time normalization evidence is not valid")
    offset = int(evidence["serverOffsetSeconds"])
    return int(value) - offset


def normalize_bars(
    bars: list[dict[str, Any]], evidence: Mapping[str, Any]
) -> list[dict[str, Any]]:
    if not bars:
        raise ValueError("MT5 returned no bars")
    normalized: list[dict[str, Any]] = []
    previous: int | None = None
    for row in bars:
        raw_time = int(row["time"])
        timestamp = normalize_epoch_seconds(raw_time, evidence)
        if previous is not None and timestamp <= previous:
            raise ValueError("Normalized MT5 bars are not strictly increasing")
        previous = timestamp
        normalized.append(
            {
                **row,
                "raw_time": raw_time,
                "time": timestamp,
                "time_normalization_contract": TIME_NORMALIZATION_CONTRACT,
            }
        )
    return normalized


def normalization_probe_identity() -> dict[str, Any]:
    return {
        "contract": TIME_NORMALIZATION_CONTRACT,
        "probeContract": CLOCK_PROBE_CONTRACT,
        "probeFilename": PROBE_FILENAME,
        "offsetSource": "TimeTradeServer-TimeGMT",
        "offsetGridSeconds": OFFSET_GRID_SECONDS,
        "maximumAbsoluteOffsetSeconds": MAX_ABSOLUTE_OFFSET_SECONDS,
        "maximumProbeAgeSeconds": MAX_PROBE_AGE_SECONDS,
        "maximumNormalizedTickSkewSeconds": MAX_NORMALIZED_TICK_SKEW_SECONDS,
        "failureMode": "skip_without_append",
        "normalization": "raw_server_epoch_minus_measured_server_offset",
    }
