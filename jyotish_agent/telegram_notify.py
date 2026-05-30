from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path


DEFAULT_RUNNER = Path(r"D:\Trading_Algo\New folder\telegram_job_runner.py")
DEFAULT_STATE = Path(r"D:\PycharmProjects\jyotish_agent\telegram_notify_state.json")


def load_runner(path: Path):
    spec = importlib.util.spec_from_file_location("telegram_job_runner_local", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import Telegram runner from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a short Codex/Jyotish-agent notification through the existing Telegram runner.")
    parser.add_argument("--message", default="")
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--legacy-bot-file", default=r"D:\Trading_Algo\WD GANN\telegram_bot.py")
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    runner = load_runner(args.runner)
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        legacy_token, legacy_chat = runner.load_legacy_telegram_config(args.legacy_bot_file)
        token = token or (legacy_token or "").strip()
        chat_id = chat_id or str(legacy_chat or "").strip()

    configured = bool(token and chat_id)
    if args.dry_run:
        print(f"telegram_configured={configured} runner_exists={args.runner.exists()} chat_id_present={bool(chat_id)} token_present={bool(token)}")
        return
    if not configured:
        raise SystemExit("Telegram token/chat id missing. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID or provide legacy bot file.")
    message = args.message.strip() or "Codex Jyotish agent checkpoint."
    client = runner.TelegramClient(token=token, chat_id=chat_id, state_file=args.state_file)
    client.send_message(message)
    print("Telegram message sent.")


if __name__ == "__main__":
    main()
