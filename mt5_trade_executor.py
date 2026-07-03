from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


try:
    import MetaTrader5 as mt5
except Exception as exc:  # pragma: no cover - depends on local terminal package.
    mt5 = None
    MT5_IMPORT_ERROR = exc
else:
    MT5_IMPORT_ERROR = None


ACTION_CHOICES = ("status", "buy", "sell", "close")
FILLING_MODES = {
    "FOK": "ORDER_FILLING_FOK",
    "IOC": "ORDER_FILLING_IOC",
    "RETURN": "ORDER_FILLING_RETURN",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Safe MetaTrader 5 execution bridge for USDJPY research. "
            "Default mode is dry-run; live order_send requires --live --confirm LIVE."
        )
    )
    parser.add_argument("--action", choices=ACTION_CHOICES, default="status")
    parser.add_argument("--status", action="store_true", help="Shortcut for --action status.")
    parser.add_argument("--symbol", default="USDJPY")
    parser.add_argument("--volume", type=float, default=0.01)
    parser.add_argument("--sl-pips", type=float, default=0.0)
    parser.add_argument("--tp-pips", type=float, default=0.0)
    parser.add_argument("--deviation", type=int, default=20)
    parser.add_argument("--magic", type=int, default=27052026)
    parser.add_argument("--comment", default="gann_astro_research")
    parser.add_argument("--ticket", type=int, help="Position ticket for --action close.")
    parser.add_argument("--json-plan", type=Path, help="Optional JSON trade plan with action/symbol/volume/sl_pips/tp_pips.")
    parser.add_argument("--terminal-path", help="Optional terminal64.exe path if multiple MT5 terminals are installed.")
    parser.add_argument("--login", type=int, help="Optional MT5 account number. Prefer demo first.")
    parser.add_argument("--server", help="Optional MT5 trade server name exactly as shown in the terminal.")
    parser.add_argument("--password-env", default="MT5_PASSWORD", help="Environment variable containing the MT5 password.")
    parser.add_argument("--timeout", type=int, default=60000, help="MT5 initialize timeout in milliseconds.")
    parser.add_argument("--portable", action="store_true", help="Use MT5 portable mode when launching the terminal path.")
    parser.add_argument("--type-filling", choices=tuple(FILLING_MODES), default="RETURN")
    parser.add_argument("--live", action="store_true", help="Actually send order_send. Omit for dry-run.")
    parser.add_argument("--confirm", default="", help="Must be exactly LIVE together with --live.")
    return parser.parse_args()


def load_plan(args: argparse.Namespace) -> argparse.Namespace:
    if not args.json_plan:
        return args
    data = json.loads(args.json_plan.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("--json-plan must contain a JSON object")
    aliases = {
        "sl_pips": "sl_pips",
        "tp_pips": "tp_pips",
        "type_filling": "type_filling",
    }
    for key in ("action", "symbol", "volume", "sl_pips", "tp_pips", "deviation", "magic", "comment", "ticket", "type_filling"):
        json_key = key
        attr = aliases.get(key, key.replace("-", "_"))
        if json_key in data and data[json_key] is not None:
            setattr(args, attr, data[json_key])
    return args


def fail(message: str, code: int = 2) -> None:
    print(json.dumps({"ok": False, "error": message}, indent=2))
    raise SystemExit(code)


def initialize(args: argparse.Namespace) -> None:
    if mt5 is None:
        fail(f"MetaTrader5 import failed: {MT5_IMPORT_ERROR}")
    kwargs: dict[str, Any] = {"timeout": int(args.timeout), "portable": bool(args.portable)}
    if args.login:
        password = os.environ.get(str(args.password_env or "MT5_PASSWORD"), "")
        if not password:
            fail(f"--login requires password in environment variable {args.password_env!r}; refusing to read credentials from code.")
        kwargs.update({"login": int(args.login), "password": password})
        if args.server:
            kwargs["server"] = str(args.server)
    if args.terminal_path:
        ok = mt5.initialize(str(args.terminal_path), **kwargs)
    elif args.login:
        ok = mt5.initialize(**kwargs)
    else:
        ok = mt5.initialize()
    if not ok:
        fail(f"mt5.initialize failed: {mt5.last_error()}")


def shutdown() -> None:
    if mt5 is not None:
        mt5.shutdown()


def as_dict(obj: Any) -> dict[str, Any]:
    if obj is None:
        return {}
    if hasattr(obj, "_asdict"):
        return dict(obj._asdict())
    if isinstance(obj, dict):
        return dict(obj)
    return {key: getattr(obj, key) for key in dir(obj) if not key.startswith("_") and not callable(getattr(obj, key))}


def pip_size(symbol_info: Any) -> float:
    point = float(symbol_info.point)
    digits = int(symbol_info.digits)
    return point * 10 if digits in (3, 5) else point


def select_symbol(symbol: str) -> Any:
    info = mt5.symbol_info(symbol)
    if info is None:
        fail(f"Symbol not found in MT5: {symbol}")
    if not info.visible and not mt5.symbol_select(symbol, True):
        fail(f"Could not select symbol in Market Watch: {symbol}")
    return mt5.symbol_info(symbol)


def account_status(symbol: str) -> dict[str, Any]:
    account = mt5.account_info()
    terminal = mt5.terminal_info()
    info = select_symbol(symbol)
    tick = mt5.symbol_info_tick(symbol)
    positions = mt5.positions_get(symbol=symbol) or []
    return {
        "ok": True,
        "mode": "status",
        "account": as_dict(account),
        "terminal": as_dict(terminal),
        "symbol": as_dict(info),
        "tick": as_dict(tick),
        "positions": [as_dict(pos) for pos in positions],
        "pip_size": pip_size(info),
        "live_ready_checks": [
            "Use demo first.",
            "Enable AutoTrading in the MT5 terminal.",
            "Confirm broker symbol name, minimum lot, stop level, and spread.",
            "Use --live --confirm LIVE only after dry-run request is correct.",
        ],
    }


def filling_mode(args: argparse.Namespace) -> int:
    return int(getattr(mt5, FILLING_MODES[str(args.type_filling).upper()]))


def build_market_request(args: argparse.Namespace) -> dict[str, Any]:
    info = select_symbol(str(args.symbol))
    tick = mt5.symbol_info_tick(str(args.symbol))
    if tick is None:
        fail(f"No tick available for {args.symbol}")
    action = str(args.action).lower()
    order_type = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL
    price = float(tick.ask if action == "buy" else tick.bid)
    pip = pip_size(info)
    sl = 0.0
    tp = 0.0
    if float(args.sl_pips or 0) > 0:
        sl = price - float(args.sl_pips) * pip if action == "buy" else price + float(args.sl_pips) * pip
    if float(args.tp_pips or 0) > 0:
        tp = price + float(args.tp_pips) * pip if action == "buy" else price - float(args.tp_pips) * pip
    digits = int(info.digits)
    return {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": str(args.symbol),
        "volume": float(args.volume),
        "type": order_type,
        "price": round(price, digits),
        "sl": round(sl, digits) if sl else 0.0,
        "tp": round(tp, digits) if tp else 0.0,
        "deviation": int(args.deviation),
        "magic": int(args.magic),
        "comment": str(args.comment)[:31],
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode(args),
    }


def build_close_request(args: argparse.Namespace) -> dict[str, Any]:
    positions = mt5.positions_get(symbol=str(args.symbol)) or []
    if args.ticket:
        positions = [pos for pos in positions if int(pos.ticket) == int(args.ticket)]
    if not positions:
        fail(f"No open position found to close for {args.symbol}" + (f" ticket={args.ticket}" if args.ticket else ""))
    pos = positions[0]
    info = select_symbol(str(pos.symbol))
    tick = mt5.symbol_info_tick(str(pos.symbol))
    close_type = mt5.ORDER_TYPE_SELL if int(pos.type) == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = float(tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask)
    return {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": str(pos.symbol),
        "volume": float(pos.volume),
        "type": close_type,
        "position": int(pos.ticket),
        "price": round(price, int(info.digits)),
        "deviation": int(args.deviation),
        "magic": int(args.magic),
        "comment": str(args.comment)[:31],
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode(args),
    }


def dry_run_or_send(args: argparse.Namespace, request: dict[str, Any]) -> dict[str, Any]:
    if not args.live:
        check = mt5.order_check(request)
        return {
            "ok": True,
            "mode": "dry_run",
            "request": request,
            "order_check": as_dict(check),
            "message": "No order was sent. Add --live --confirm LIVE only after this request is correct.",
        }
    if str(args.confirm) != "LIVE":
        fail("Refusing live trade: pass --confirm LIVE together with --live.")
    result = mt5.order_send(request)
    return {"ok": bool(result and result.retcode == mt5.TRADE_RETCODE_DONE), "mode": "live", "request": request, "result": as_dict(result)}


def main() -> None:
    args = load_plan(parse_args())
    if args.status:
        args.action = "status"
    initialize(args)
    try:
        if args.action == "status":
            result = account_status(str(args.symbol))
        elif args.action in {"buy", "sell"}:
            result = dry_run_or_send(args, build_market_request(args))
        elif args.action == "close":
            result = dry_run_or_send(args, build_close_request(args))
        else:
            fail(f"Unsupported action: {args.action}")
        print(json.dumps(result, indent=2, default=str))
    finally:
        shutdown()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        shutdown()
        sys.exit(130)
