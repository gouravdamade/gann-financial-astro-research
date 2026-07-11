from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from typing import Any


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
            "tradeAllowed": False,
            "lastError": "",
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
            tick_time = datetime.fromtimestamp(int(tick.time), tz=timezone.utc).isoformat() if tick else None
            self._set_status(
                state="connected",
                connected=True,
                tradeAllowed=False,
                accountLogin=int(account.login),
                server=str(account.server),
                company=str(account.company),
                terminalBuild=int(getattr(terminal, "build", 0)),
                bid=float(tick.bid) if tick else None,
                ask=float(tick.ask) if tick else None,
                lastTickUtc=tick_time,
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
