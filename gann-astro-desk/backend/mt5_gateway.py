from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from mt5_clock import (
    TIME_NORMALIZATION_CONTRACT,
    default_clock_probe_path,
    deploy_clock_probe,
    read_clock_probe,
    time_normalization_evidence,
)


TIMEFRAME_SECONDS = {
    "M30": 30 * 60,
    "H1": 60 * 60,
    "H4": 4 * 60 * 60,
    "D1": 24 * 60 * 60,
    "W1": 7 * 24 * 60 * 60,
}
NORMALIZED_SNAPSHOT_CONTRACT = "MT5_TIMESTAMP_NORMALIZED_CLOSED_BARS_V2"


class Mt5Gateway:
    def __init__(self, symbol: str = "USDJPY", autoconnect: bool = True) -> None:
        self.symbol = symbol
        self.autoconnect = autoconnect
        self._lock = threading.RLock()
        self._terminal_lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._mt5: Any = None
        self._status: dict[str, Any] = {
            "state": "starting" if autoconnect else "disabled",
            "symbol": symbol,
            "connected": False,
            "terminalAllowsTrading": False,
            "accountAllowsTrading": False,
            "accountExpertTradingAllowed": False,
            "appExecutionAllowed": False,
            "tradeAllowed": False,
            "lastError": "",
            "executionMode": "read_only_market_data",
            "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    def start(self) -> None:
        if not self.autoconnect or self._thread is not None:
            return
        self._thread = threading.Thread(target=self._heartbeat_loop, name="mt5-heartbeat", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        if self._mt5 is not None:
            try:
                self._mt5.shutdown()
            except Exception:
                pass

    def status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._status)

    def _set_status(self, **values: Any) -> None:
        with self._lock:
            self._status.update(values)
            self._status["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _load_mt5(self) -> Any:
        if self._mt5 is None:
            import MetaTrader5 as mt5

            self._mt5 = mt5
        return self._mt5

    def _normalization_evidence_locked(
        self,
        mt5: Any,
        symbol: str,
        observed_at: datetime,
        clock_probe: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        status = self.status()
        probe_path = default_clock_probe_path(status.get("terminalCommonDataPath"))
        probe = dict(clock_probe) if clock_probe is not None else read_clock_probe(probe_path)
        validation_symbol = str(probe.get("symbol") or "").upper().strip()
        if not validation_symbol:
            raise RuntimeError("MT5 clock probe does not identify its validation symbol")
        if not mt5.symbol_select(validation_symbol, True):
            raise RuntimeError(f"MT5 clock validation symbol is unavailable: {validation_symbol}")
        tick = mt5.symbol_info_tick(validation_symbol)
        if tick is None:
            raise RuntimeError("MT5 did not expose a timestamped validation-symbol tick")
        current_h1 = mt5.copy_rates_from_pos(validation_symbol, mt5.TIMEFRAME_H1, 0, 1)
        if current_h1 is None or len(current_h1) != 1:
            raise RuntimeError("MT5 did not expose the validation-symbol H1 timestamp")
        evidence = time_normalization_evidence(
            observed_at,
            int(tick.time),
            int(current_h1[-1]["time"]),
            probe,
            expected_symbol=validation_symbol,
            expected_server=str(status.get("server") or "") or None,
            expected_terminal_build=int(status.get("terminalBuild") or 0) or None,
        )
        if not evidence["valid"]:
            issue = "; ".join(evidence["validationIssues"])
            raise RuntimeError(f"MT5 server-time normalization failed: {issue}")
        evidence["validationSymbol"] = validation_symbol
        evidence["requestedSymbol"] = symbol.upper().strip()
        evidence["crossSymbolOffsetApplication"] = validation_symbol != symbol.upper().strip()
        return evidence

    def connect(self) -> bool:
        with self._terminal_lock:
            try:
                mt5 = self._load_mt5()
                terminal_path = os.environ.get("GANN_ASTRO_MT5_TERMINAL", "").strip()
                timeout_ms = int(os.environ.get("GANN_ASTRO_MT5_TIMEOUT_MS", "10000"))
                initialized = mt5.initialize(terminal_path, timeout=timeout_ms) if terminal_path else mt5.initialize(timeout=timeout_ms)
                if not initialized:
                    self._set_status(
                        state="reconnecting",
                        connected=False,
                        tradeAllowed=False,
                        lastError=str(mt5.last_error()),
                    )
                    return False
                mt5.symbol_select(self.symbol, True)
                return self._refresh()
            except Exception as exc:
                self._set_status(
                    state="reconnecting",
                    connected=False,
                    tradeAllowed=False,
                    lastError=str(exc),
                )
                return False

    def _refresh(self) -> bool:
        with self._terminal_lock:
            mt5 = self._load_mt5()
            terminal = mt5.terminal_info()
            account = mt5.account_info()
            tick = mt5.symbol_info_tick(self.symbol)
            connected = bool(terminal and getattr(terminal, "connected", False) and account)
            if not connected:
                self._set_status(
                    state="reconnecting",
                    connected=False,
                    tradeAllowed=False,
                    lastError=str(mt5.last_error()),
                )
                return False
            raw_tick_epoch = int(tick.time) if tick else None
            raw_tick_time = (
                datetime.fromtimestamp(raw_tick_epoch, tz=timezone.utc).isoformat()
                if raw_tick_epoch is not None
                else None
            )
            common_data_path = str(getattr(terminal, "commondata_path", "") or "")
            terminal_data_path = str(getattr(terminal, "data_path", "") or "")
            try:
                deployment = deploy_clock_probe(
                    os.environ.get("GANN_ASTRO_MT5_CLOCK_PROBE_BUNDLE"),
                    terminal_data_path,
                )
            except OSError as exc:
                deployment = {
                    "contract": "GANN_MT5_CLOCK_PROBE_DEPLOYMENT_V1",
                    "available": True,
                    "deployed": False,
                    "changed": False,
                    "message": str(exc),
                    "appExecutionAllowed": False,
                }
            self._set_status(
                state="connected",
                connected=True,
                terminalAllowsTrading=bool(getattr(terminal, "trade_allowed", False)),
                accountAllowsTrading=bool(getattr(account, "trade_allowed", False)),
                accountExpertTradingAllowed=bool(getattr(account, "trade_expert", False)),
                appExecutionAllowed=False,
                tradeAllowed=False,
                accountLogin=int(account.login),
                server=str(account.server),
                company=str(account.company),
                terminalBuild=int(getattr(terminal, "build", 0)),
                terminalPath=str(getattr(terminal, "path", "") or ""),
                terminalDataPath=terminal_data_path,
                terminalCommonDataPath=common_data_path,
                clockProbePath=str(default_clock_probe_path(common_data_path)),
                clockProbeDeployment=deployment,
                bid=float(tick.bid) if tick else None,
                ask=float(tick.ask) if tick else None,
                rawLastTickServerEpochSeconds=raw_tick_epoch,
                rawLastTickMilliseconds=int(getattr(tick, "time_msc", 0)) if tick else None,
                rawLastTickServerTime=raw_tick_time,
                lastTickUtc=None,
                lastError="",
                executionMode="read_only_market_data",
            )
            return True

    def bars(self, symbol: str, timeframe: str, count: int = 500) -> list[dict[str, Any]]:
        normalized_symbol = symbol.upper().strip()
        normalized_timeframe = timeframe.upper().strip()
        if not normalized_symbol or len(normalized_symbol) > 32 or not all(
            character.isalnum() or character in {".", "_", "-"} for character in normalized_symbol
        ):
            raise ValueError("invalid MT5 symbol")
        count = max(20, min(int(count), 5000))
        with self._terminal_lock:
            mt5 = self._load_mt5()
            if not self.status().get("connected") and not self.connect():
                raise RuntimeError(self.status().get("lastError") or "MT5 is not connected")
            timeframe_value = {
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
            }.get(normalized_timeframe)
            if timeframe_value is None:
                raise ValueError(f"unsupported MT5 timeframe: {timeframe}")
            if not mt5.symbol_select(normalized_symbol, True):
                raise RuntimeError(f"MT5 symbol is unavailable: {normalized_symbol}")
            rates = mt5.copy_rates_from_pos(normalized_symbol, timeframe_value, 0, count)
            if rates is None or len(rates) == 0:
                raise RuntimeError(str(mt5.last_error()))
            return [
                {
                    "time": int(row["time"]),
                    "open": round(float(row["open"]), 8),
                    "high": round(float(row["high"]), 8),
                    "low": round(float(row["low"]), 8),
                    "close": round(float(row["close"]), 8),
                    "volume": int(row["tick_volume"]),
                }
                for row in rates
            ]

    def save_history_snapshot(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
        output_root: Path,
        *,
        captured_at: datetime | None = None,
        clock_probe: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_symbol = symbol.upper().strip()
        normalized_timeframe = timeframe.upper().strip()
        if not normalized_symbol or len(normalized_symbol) > 32 or not all(
            character.isalnum() or character in {".", "_", "-"} for character in normalized_symbol
        ):
            raise ValueError("invalid MT5 symbol")
        if normalized_timeframe not in TIMEFRAME_SECONDS:
            raise ValueError(f"unsupported MT5 timeframe: {timeframe}")
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("snapshot start and end must include a UTC offset")

        requested_start = start.astimezone(timezone.utc)
        requested_end = end.astimezone(timezone.utc)
        captured = (captured_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if requested_end <= requested_start:
            raise ValueError("snapshot end must be later than start")
        if requested_start >= captured:
            raise ValueError("snapshot start must be earlier than capture time")
        if requested_end - requested_start > timedelta(days=366 * 20):
            raise ValueError("an MT5 history snapshot is limited to twenty years")
        effective_end = min(requested_end, captured)

        with self._terminal_lock:
            mt5 = self._load_mt5()
            if not self.status().get("connected") and not self.connect():
                raise RuntimeError(self.status().get("lastError") or "MT5 is not connected")
            timeframe_value = {
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
            }[normalized_timeframe]
            if not mt5.symbol_select(normalized_symbol, True):
                raise RuntimeError(f"MT5 symbol is unavailable: {normalized_symbol}")
            normalization = self._normalization_evidence_locked(
                mt5,
                normalized_symbol,
                captured,
                clock_probe,
            )
            server_offset = timedelta(seconds=int(normalization["serverOffsetSeconds"]))
            query_start = requested_start + server_offset
            query_end = effective_end + server_offset
            rates = mt5.copy_rates_range(
                normalized_symbol,
                timeframe_value,
                query_start,
                query_end,
            )
            if rates is None or len(rates) == 0:
                raise RuntimeError(str(mt5.last_error()))

        frame = pd.DataFrame(rates)
        frame["raw_time"] = pd.to_numeric(frame["time"], errors="raise").astype("int64")
        frame["time"] = pd.to_datetime(
            frame["raw_time"] - int(normalization["serverOffsetSeconds"]),
            unit="s",
            utc=True,
        )
        if frame["time"].duplicated().any() or not frame["time"].is_monotonic_increasing:
            raise RuntimeError("Normalized MT5 snapshot timestamps are not unique and increasing")
        frame = frame[
            (frame["time"] >= pd.Timestamp(requested_start))
            & (frame["time"] <= pd.Timestamp(effective_end))
        ].copy()
        frame["bar_close_time"] = frame["time"] + pd.to_timedelta(
            TIMEFRAME_SECONDS[normalized_timeframe], unit="s"
        )
        complete = frame["bar_close_time"] <= pd.Timestamp(effective_end)
        excluded_incomplete = int((~complete).sum())
        frame = frame.loc[complete].copy()
        if frame.empty:
            raise RuntimeError("MT5 returned no fully closed bars in the requested snapshot range")

        for column in ("tick_volume", "spread", "real_volume"):
            if column not in frame:
                frame[column] = 0
        frame = frame.set_index("time")[
            [
                "open",
                "high",
                "low",
                "close",
                "tick_volume",
                "spread",
                "real_volume",
                "raw_time",
            ]
        ].sort_index()
        frame.index.name = "time"

        snapshot_id = (
            f"{normalized_symbol}_{normalized_timeframe}_"
            f"{captured.strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
        )
        target_dir = Path(output_root).expanduser().resolve() / normalized_symbol / normalized_timeframe
        target_dir.mkdir(parents=True, exist_ok=True)
        parquet_path = target_dir / f"{snapshot_id}.parquet"
        partial_path = target_dir / f".{snapshot_id}.partial.parquet"
        frame.to_parquet(partial_path)
        partial_path.replace(parquet_path)

        digest = hashlib.sha256()
        with parquet_path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        status = self.status()
        last_bar_open = frame.index.max().to_pydatetime()
        last_bar_close = last_bar_open + timedelta(seconds=TIMEFRAME_SECONDS[normalized_timeframe])
        manifest = {
            "snapshotId": snapshot_id,
            "contract": NORMALIZED_SNAPSHOT_CONTRACT,
            "symbol": normalized_symbol,
            "timeframe": normalized_timeframe,
            "source": "MetaTrader5.copy_rates_range",
            "capturedAtUtc": captured.isoformat(timespec="seconds"),
            "requestedStartUtc": requested_start.isoformat(timespec="seconds"),
            "requestedEndUtc": requested_end.isoformat(timespec="seconds"),
            "queryStartServerEncoded": query_start.isoformat(timespec="seconds"),
            "queryEndServerEncoded": query_end.isoformat(timespec="seconds"),
            "asOfUtc": effective_end.isoformat(timespec="seconds"),
            "futureRequestClamped": requested_end > captured,
            "barCount": int(len(frame)),
            "firstBarOpenUtc": frame.index.min().isoformat(),
            "lastBarOpenUtc": frame.index.max().isoformat(),
            "lastBarCloseUtc": last_bar_close.isoformat(timespec="seconds"),
            "rawFirstBarOpenServerEpochSeconds": int(frame["raw_time"].iloc[0]),
            "rawLastBarOpenServerEpochSeconds": int(frame["raw_time"].iloc[-1]),
            "incompleteBarsExcluded": excluded_incomplete,
            "noLookahead": True,
            "immutable": True,
            "timeNormalizationContract": TIME_NORMALIZATION_CONTRACT,
            "timeNormalization": normalization,
            "appExecutionAllowed": False,
            "parquetPath": str(parquet_path),
            "parquetSha256": digest.hexdigest().upper(),
            "accountLogin": status.get("accountLogin"),
            "server": status.get("server"),
            "company": status.get("company"),
            "terminalBuild": status.get("terminalBuild"),
        }
        manifest_path = target_dir / f"{snapshot_id}.manifest.json"
        manifest_partial = target_dir / f".{snapshot_id}.manifest.partial.json"
        manifest["manifestPath"] = str(manifest_path)
        manifest_partial.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        manifest_partial.replace(manifest_path)
        return manifest

    @staticmethod
    def list_history_snapshots(output_root: Path, limit: int = 100) -> list[dict[str, Any]]:
        root = Path(output_root).expanduser().resolve()
        if not root.is_dir():
            return []
        snapshots: list[dict[str, Any]] = []
        for path in root.glob("*/*/*.manifest.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["manifestPath"] = str(path)
                snapshots.append(payload)
            except (OSError, ValueError, TypeError):
                continue
        snapshots.sort(key=lambda item: str(item.get("capturedAtUtc") or ""), reverse=True)
        return snapshots[: max(1, min(int(limit), 500))]

    def _heartbeat_loop(self) -> None:
        delay = 1.0
        while not self._stop.is_set():
            connected = False
            try:
                if self._mt5 is not None:
                    connected = self._refresh()
                if not connected:
                    connected = self.connect()
            except Exception as exc:
                self._set_status(state="reconnecting", connected=False, lastError=str(exc))
            delay = 2.0 if connected else min(delay * 1.6, 20.0)
            self._stop.wait(delay)
