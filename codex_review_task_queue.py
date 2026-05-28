from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aspect_annotation_store import (
    DEFAULT_DB_PATH,
    connect,
    enqueue_codex_review_task,
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
    parser.add_argument(
        "--ingest-dream-queue",
        action="store_true",
        help="Import queued Dream Review contradiction rows into codex_review_tasks.",
    )
    parser.add_argument(
        "--dream-queue-path",
        type=Path,
        default=Path("jyotish_agent") / "dream_review_queue.jsonl",
        help="Path to dream_review_queue.jsonl for --ingest-dream-queue.",
    )
    return parser.parse_args()


def load_note_text(args: argparse.Namespace) -> str:
    if args.note_file:
        return args.note_file.read_text(encoding="utf-8", errors="replace").strip()
    return str(args.note_text or "").strip()


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def dream_task_already_imported(conn: Any, report_path: str) -> bool:
    if not report_path:
        return False
    marker = Path(report_path).name or report_path
    row = conn.execute(
        """
        SELECT task_id
        FROM codex_review_tasks
        WHERE task_type = 'dream_review_correction'
          AND payload_json LIKE ?
        LIMIT 1
        """,
        (f"%{marker}%",),
    ).fetchone()
    return row is not None


def ingest_dream_queue(conn: Any, path: Path) -> dict[str, Any]:
    imported: list[int] = []
    skipped: list[dict[str, Any]] = []
    for row in iter_jsonl(path):
        status = str(row.get("status") or "")
        report_path = str(row.get("report_path") or "")
        if status != "queued_for_codex":
            skipped.append({"report_path": report_path, "reason": f"status={status or 'missing'}"})
            continue
        if dream_task_already_imported(conn, report_path):
            skipped.append({"report_path": report_path, "reason": "already_imported"})
            continue
        case_id = int(row.get("case_id") or 0)
        task_id = enqueue_codex_review_task(
            conn,
            task_type="dream_review_correction",
            case_id=case_id or None,
            family_key=str(row.get("family") or ""),
            priority="high",
            source="dream_review_jsonl",
            trigger_reason=str(row.get("message") or "Dream Review queued a contradiction for Codex review."),
            payload={
                "case_id": case_id,
                "family_key": str(row.get("family") or ""),
                "dream_review_result": row,
                "source_queue_path": str(path),
                "policy": "dream_review_contradictions_codex_owned",
                "instruction": (
                    "Inspect the queued Dream Review contradiction, local draft/verifier evidence, Auto Suggest evidence, "
                    "completed review and current official ML note. If deterministic evidence is clear, replace the official "
                    "ML note through --write-official-note; otherwise mark the task failed/skipped with the blocker."
                ),
            },
        )
        imported.append(task_id)
    conn.commit()
    return {"imported_task_ids": imported, "skipped": skipped, "source": str(path)}


def main() -> None:
    args = parse_args()
    initialize_database(args.db)
    with connect(args.db) as conn:
        if args.ingest_dream_queue:
            dream_path = args.dream_queue_path
            if not dream_path.is_absolute():
                dream_path = Path(__file__).resolve().parent / dream_path
            print(json.dumps(ingest_dream_queue(conn, dream_path), ensure_ascii=False, indent=2, default=str))
            return

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
