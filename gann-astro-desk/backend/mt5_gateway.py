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
