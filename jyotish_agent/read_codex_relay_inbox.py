from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_INBOX = ROOT / "codex_telegram_inbox.jsonl"
DEFAULT_SEEN = ROOT / "codex_telegram_inbox_seen.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read pending Telegram -> Codex relay messages.")
    parser.add_argument("--inbox-file", type=Path, default=DEFAULT_INBOX)
    parser.add_argument("--seen-file", type=Path, default=DEFAULT_SEEN)
    parser.add_argument("--mark-seen", action="store_true")
    parser.add_argument("--all", action="store_true", help="Show all messages, not only unseen.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def load_rows(path: Path) -> list[dict[str, Any]]:
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
    return rows


def main() -> None:
    args = parse_args()
    rows = load_rows(args.inbox_file)
    seen = load_json(args.seen_file)
    seen_ids = set(seen.get("seen_ids") or [])
    pending = rows if args.all else [row for row in rows if row.get("relay_id") not in seen_ids]

    if not pending:
        print("No pending Telegram relay messages.")
        return

    for row in pending:
        print("=" * 80)
        print(f"relay_id: {row.get('relay_id')}")
        print(f"saved_at_utc: {row.get('saved_at_utc')}")
        print(f"priority: {row.get('priority')}")
        print(f"status: {row.get('status')}")
        print("text:")
        print(row.get("text", ""))

    if args.mark_seen:
        updated = sorted(seen_ids | {str(row.get("relay_id")) for row in pending if row.get("relay_id")})
        args.seen_file.write_text(json.dumps({"seen_ids": updated}, indent=2), encoding="utf-8")
        print("=" * 80)
        print(f"Marked {len(pending)} message(s) seen in {args.seen_file}")


if __name__ == "__main__":
    main()
