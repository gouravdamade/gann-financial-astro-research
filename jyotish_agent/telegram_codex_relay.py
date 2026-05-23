from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from telegram_notify import DEFAULT_RUNNER, load_runner


ROOT = Path(__file__).resolve().parent
DEFAULT_STATE = ROOT / "telegram_codex_relay_state.json"
DEFAULT_INBOX = ROOT / "codex_telegram_inbox.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Telegram -> Codex relay inbox. This does not call OpenAI or a local LLM; "
            "it saves user messages for the active Codex workspace/session to read."
        )
    )
    parser.add_argument("--token", default=os.getenv("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--chat-id", default=os.getenv("TELEGRAM_CHAT_ID"))
    parser.add_argument("--legacy-bot-file", default=r"C:\Users\ADMIN\Desktop\WD GANN\telegram_bot.py")
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--inbox-file", type=Path, default=DEFAULT_INBOX)
    parser.add_argument("--poll-timeout-sec", type=int, default=25)
    parser.add_argument("--sleep-sec", type=float, default=1.0)
    parser.add_argument("--announce-start", action="store_true")
    parser.add_argument("--once", action="store_true", help="Poll once and exit, useful for smoke tests.")
    return parser.parse_args()


class TelegramClient:
    def __init__(self, token: str):
        self.base = f"https://api.telegram.org/bot{token}"

    def _request(self, method: str, payload: dict[str, Any], timeout: float = 40.0) -> dict[str, Any]:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            url=f"{self.base}/{method}",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            parsed = json.loads(resp.read().decode("utf-8", errors="replace"))
        if not parsed.get("ok", False):
            raise RuntimeError(f"Telegram API error: {parsed}")
        return parsed

    def send_message(self, chat_id: str, text: str) -> None:
        chunk_size = 3500
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] or [""]
        for chunk in chunks:
            self._request("sendMessage", {"chat_id": chat_id, "text": chunk})

    def get_updates(self, offset: int, timeout_sec: int) -> list[dict[str, Any]]:
        data = self._request(
            "getUpdates",
            {
                "offset": offset,
                "timeout": timeout_sec,
                "allowed_updates": json.dumps(["message"]),
            },
            timeout=max(40.0, timeout_sec + 15.0),
        )
        return list(data.get("result", []))


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"offset": 0, "saved_count": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {"offset": 0, "saved_count": 0}


def save_state(path: Path, state: dict[str, Any]) -> None:
    state = dict(state)
    state["updated_at"] = now_iso()
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def consume_backlog(tg: TelegramClient, state: dict[str, Any], state_file: Path) -> None:
    if int(state.get("offset") or 0) > 0:
        return
    updates = tg.get_updates(0, 0)
    if updates:
        state["offset"] = int(updates[-1]["update_id"]) + 1
    state["backlog_consumed_at"] = now_iso()
    save_state(state_file, state)


def append_inbox(path: Path, update: dict[str, Any], text: str, priority: str) -> dict[str, Any]:
    msg = update.get("message") or {}
    chat = msg.get("chat") or {}
    sender = msg.get("from") or {}
    rec = {
        "relay_id": f"tg_{update.get('update_id')}_{msg.get('message_id')}",
        "saved_at_utc": now_iso(),
        "status": "pending_for_codex",
        "priority": priority,
        "source": "telegram",
        "chat_id": str(chat.get("id", "")),
        "message_id": msg.get("message_id"),
        "telegram_date": msg.get("date"),
        "from_user_id": str(sender.get("id", "")),
        "from_username": str(sender.get("username", "")),
        "text": text,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    return rec


def tail_inbox(path: Path, limit: int = 5) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def help_text(inbox_file: Path) -> str:
    return (
        "Codex relay commands:\n"
        "/codex <message> - send message/query to Codex inbox\n"
        "/urgent <message> - mark high priority for Codex\n"
        "/status - relay status and inbox path\n"
        "/last - show latest saved relay messages\n"
        "/ping - health check\n"
        "/help - show this help\n\n"
        "Plain text is also saved for Codex.\n"
        "Important: this bot cannot inject text into the live Codex app by itself; "
        "it creates a local inbox that Codex reads while this workspace is active.\n"
        f"Inbox: {inbox_file}"
    )


def extract_relay_text(raw: str) -> tuple[str, str, str]:
    lower = raw.lower()
    if lower.startswith("/urgent "):
        return raw[8:].strip(), "high", "urgent"
    if lower.startswith("/codex "):
        return raw[7:].strip(), "normal", "codex"
    return raw.strip(), "normal", "plain"


def main() -> None:
    args = parse_args()
    token = (args.token or "").strip()
    chat_id = str(args.chat_id or "").strip()
    if not token or not chat_id:
        runner = load_runner(args.runner)
        legacy_token, legacy_chat = runner.load_legacy_telegram_config(args.legacy_bot_file)
        token = token or (legacy_token or "").strip()
        chat_id = chat_id or str(legacy_chat or "").strip()
    if not token or not chat_id:
        raise SystemExit("Telegram token/chat id missing.")

    tg = TelegramClient(token)
    state = load_state(args.state_file)
    consume_backlog(tg, state, args.state_file)
    if args.announce_start:
        tg.send_message(chat_id, "Codex Telegram relay started. Use /help.")

    while True:
        updates = tg.get_updates(int(state.get("offset") or 0), args.poll_timeout_sec)
        for update in updates:
            state["offset"] = int(update["update_id"]) + 1
            msg = update.get("message") or {}
            incoming_chat_id = str((msg.get("chat") or {}).get("id", ""))
            if incoming_chat_id != chat_id:
                continue
            raw = str(msg.get("text") or "").strip()
            if not raw:
                continue
            lower = raw.lower()
            if lower in ("/help", "help", "/start"):
                tg.send_message(chat_id, help_text(args.inbox_file))
            elif lower in ("/ping", "ping"):
                tg.send_message(chat_id, f"PONG {now_iso()}")
            elif lower in ("/status", "status"):
                count = int(state.get("saved_count") or 0)
                tg.send_message(
                    chat_id,
                    "Codex relay status:\n"
                    f"- saved messages this state: {count}\n"
                    f"- inbox: {args.inbox_file}\n"
                    "- mode: Telegram -> local Codex inbox, no LLM answer.",
                )
            elif lower in ("/last", "last"):
                rows = tail_inbox(args.inbox_file, limit=5)
                if not rows:
                    tg.send_message(chat_id, "No relay messages saved yet.")
                else:
                    formatted = []
                    for row in rows:
                        formatted.append(f"{row.get('relay_id')} [{row.get('priority')}]: {row.get('text')}")
                    tg.send_message(chat_id, "Latest relay messages:\n" + "\n".join(formatted))
            else:
                text, priority, mode = extract_relay_text(raw)
                if not text:
                    tg.send_message(chat_id, "Empty message. Use /codex <message>.")
                else:
                    rec = append_inbox(args.inbox_file, update, text, priority)
                    state["saved_count"] = int(state.get("saved_count") or 0) + 1
                    ack = "Queued for Codex"
                    if mode == "urgent":
                        ack = "Queued for Codex as HIGH priority"
                    tg.send_message(chat_id, f"{ack}: {rec['relay_id']}")
        save_state(args.state_file, state)
        if args.once:
            break
        time.sleep(args.sleep_sec)


if __name__ == "__main__":
    main()
