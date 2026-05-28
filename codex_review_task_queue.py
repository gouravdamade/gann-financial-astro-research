from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aspect_annotation_store import (
    DEFAULT_DB_PATH,
    connect,
    initialize_database,
    list_codex_review_tasks,
    replace_rule_note_type,
    update_codex_review_task,
)


def row_to_dict(row: Any) -> dict[str, Any]:
    out = dict(row)
    for key in ("payload_json", "result_json"):
        raw = out.get(key) or ""
        if raw:
            try:
                out[key.replace("_json", "")] = json.loads(raw)
            except Exception:
                out[key.replace("_json", "")] = {"raw": raw}
        else:
            out[key.replace("_json", "")] = {}
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Codex-owned review task queue helper. The browser/server may enqueue tasks, "
            "but official ML notes should be written only by Codex through this helper."
        )
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--list-pending", action="store_true", help="Print pending tasks as JSON.")
    parser.add_argument("--show-task", type=int, help="Print one task as JSON.")
    parser.add_argument("--status", default="pending", help="Status filter for --list-pending.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--write-official-note", type=int, metavar="TASK_ID", help="Write Codex-approved official note for a task.")
    parser.add_argument("--note-file", type=Path, help="Markdown/text file containing the Codex-approved note.")
    parser.add_argument("--note-text", help="Codex-approved note text.")
    parser.add_argument("--note-type", default="official_ml_note")
    parser.add_argument("--mark-task", type=int, metavar="TASK_ID", help="Mark a task without writing a note.")
    parser.add_argument("--mark-status", default="done", choices=("pending", "in_progress", "done", "failed", "skipped"))
    parser.add_argument("--result-json", default="{}", help="Small JSON result summary for --mark-task.")
    return parser.parse_args()


def load_note_text(args: argparse.Namespace) -> str:
    if args.note_file:
        return args.note_file.read_text(encoding="utf-8", errors="replace").strip()
    return str(args.note_text or "").strip()


def main() -> None:
    args = parse_args()
    initialize_database(args.db)
    with connect(args.db) as conn:
        if args.list_pending:
            tasks = [row_to_dict(row) for row in list_codex_review_tasks(conn, status=args.status, limit=args.limit)]
            print(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2, default=str))
            return

        if args.show_task:
            row = conn.execute("SELECT * FROM codex_review_tasks WHERE task_id = ?", (int(args.show_task),)).fetchone()
            if row is None:
                raise SystemExit(f"No codex_review_tasks row found for task_id={args.show_task}")
            print(json.dumps(row_to_dict(row), ensure_ascii=False, indent=2, default=str))
            return

        if args.write_official_note:
            row = conn.execute("SELECT * FROM codex_review_tasks WHERE task_id = ?", (int(args.write_official_note),)).fetchone()
            if row is None:
                raise SystemExit(f"No codex_review_tasks row found for task_id={args.write_official_note}")
            task = row_to_dict(row)
            case_id = task.get("case_id")
            if case_id is None:
                payload = task.get("payload") or {}
                case_id = payload.get("case_id")
            if case_id is None:
                raise SystemExit("Task has no case_id; cannot write official ML note.")
            note_text = load_note_text(args)
            if not note_text:
                raise SystemExit("--write-official-note requires --note-file or --note-text.")
            note_id = replace_rule_note_type(
                conn,
                case_id=int(case_id),
                note_type=str(args.note_type or "official_ml_note"),
                note_text=note_text,
            )
            update_codex_review_task(
                conn,
                int(args.write_official_note),
                status="done",
                result={"note_id": note_id, "case_id": int(case_id), "note_type": args.note_type},
            )
            conn.commit()
            print(json.dumps({"ok": True, "task_id": args.write_official_note, "note_id": note_id}, indent=2))
            return

        if args.mark_task:
            try:
                result = json.loads(args.result_json or "{}")
            except Exception as exc:
                raise SystemExit(f"--result-json is not valid JSON: {exc}") from exc
            update_codex_review_task(conn, int(args.mark_task), status=args.mark_status, result=result)
            conn.commit()
            print(json.dumps({"ok": True, "task_id": args.mark_task, "status": args.mark_status}, indent=2))
            return

    raise SystemExit("Choose --list-pending, --show-task, --write-official-note, or --mark-task.")


if __name__ == "__main__":
    main()
