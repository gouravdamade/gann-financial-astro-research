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
    parser.add_argument(
        "--process-pending",
        action="store_true",
        help="Process deterministic Codex review-agent tasks immediately.",
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


def _fmt_pips(value: Any) -> str:
    try:
        return f"{float(value):+.1f}"
    except Exception:
        return "unknown"


def _jget(data: dict[str, Any], *path: str, default: Any = None) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


def _marker_note_excerpt(marker_note: dict[str, Any]) -> str:
    text = str(marker_note.get("note_text") or "").strip()
    if not text:
        return ""
    lines = [line for line in text.splitlines() if line.strip()]
    keep = []
    for line in lines:
        if line.startswith(("astro_hints=", "rule_vs_default=", "auto_reason=", "sr_geometry=", "break_confirmation=", "gann_fan_exit_status=", "multi_aspect_gate=")):
            keep.append(line)
    return "\n".join(keep[:8])


def compose_official_note_from_review(task: dict[str, Any]) -> str:
    payload = task.get("payload") or {}
    review = payload.get("completed_review_payload") or {}
    auto = review.get("auto_suggestion") or {}
    trade = review.get("trade_profit") or {}
    marker_note = review.get("current_marker_ml_note") or {}
    case_id = int(task.get("case_id") or review.get("case_id") or payload.get("case_id"))
    family = str(task.get("family_key") or review.get("family_key") or payload.get("family_key") or "")
    outcome = str(review.get("outcome_label") or trade.get("outcomeLabel") or "unknown")
    signed_pips = _fmt_pips(trade.get("signedPips"))
    start_rule = str(auto.get("start_rule") or "")
    end_rule = str(auto.get("end_rule") or "")
    sr_label = _jget(auto, "sr_geometry", "label", default="SR geometry unavailable")
    break_label = _jget(auto, "break_confirmation", "label", default="break confirmation unavailable")
    reason = str(auto.get("reason") or "")
    extras = _marker_note_excerpt(marker_note)
    return (
        f"scope=case_id/local; type=official_ml_note; status=codex_review_agent_official; "
        f"case_id={case_id}; family={family}; outcome={outcome}; signed_pips={signed_pips};\n\n"
        f"Official Codex review-agent note: this recurrence is recorded as {outcome} with {signed_pips} signed pips. "
        f"Auto Suggest used `{start_rule or 'unknown_start_rule'}` -> `{end_rule or 'unknown_end_rule'}`. "
        f"{reason}\n\n"
        f"Deterministic geometry: {sr_label}. Break/hold test: {break_label}. "
        "Treat local LLM prose as draft only; train from this official note plus the stored Auto Suggest JSON.\n\n"
        f"Entry: {review.get('trade_start_ist') or _jget(review, 'trade_start', 'x', default='unknown')} @ {trade.get('entry', 'unknown')}\n"
        f"Exit: {review.get('trade_end_ist') or _jget(review, 'trade_end', 'x', default='unknown')} @ {trade.get('exit', 'unknown')}\n"
        + (f"\nKey extracted marker evidence:\n{extras}\n" if extras else "")
    )


def compose_dream_correction_note(task: dict[str, Any]) -> str:
    payload = task.get("payload") or {}
    dream_payload = payload.get("dream_review_payload") or {}
    dream_result = payload.get("dream_review_result") or {}
    report = dream_payload.get("verifier_report") if isinstance(dream_payload.get("verifier_report"), dict) else {}
    evidence = report.get("evidence") if isinstance(report.get("evidence"), dict) else {}
    auto = dream_payload.get("auto_suggestion") or {}
    trade = evidence.get("trade_result") or dream_payload.get("trade_result") or {}
    case_id = int(task.get("case_id") or dream_payload.get("case_id") or payload.get("case_id"))
    family = str(task.get("family_key") or dream_payload.get("family") or payload.get("family_key") or "")
    issues = dream_result.get("issues") or report.get("issues") or []
    issue_text = "; ".join(f"{item.get('title')}: {item.get('detail')}" for item in issues if isinstance(item, dict))
    outcome = str(evidence.get("outcome") or trade.get("outcomeLabel") or "unknown")
    signed_pips = _fmt_pips(trade.get("signedPips"))
    sr_label = str(evidence.get("sr_label") or _jget(auto, "sr_geometry", "label", default="SR geometry unavailable"))
    default_sr_label = _jget(auto, "default_marker_flow_sr_geometry", "label", default="")
    break_label = str(evidence.get("break_label") or _jget(auto, "break_confirmation", "label", default="break confirmation unavailable"))
    reason = str(auto.get("reason") or evidence.get("auto_reason") or "")
    return (
        f"scope=case_id/local; type=official_ml_note; status=codex_verified_dream_review_resolved; "
        f"case_id={case_id}; family={family}; outcome={outcome}; signed_pips={signed_pips};\n\n"
        "Dream Review correction: queued draft contradictions were resolved in favor of deterministic evidence, "
        "not local LLM wording. The contradictory draft language must not be used for ML training.\n\n"
        f"Resolved issues: {issue_text or 'queued Dream Review contradiction'}\n\n"
        f"Correct deterministic reading: outcome is `{outcome}`, trade result is {signed_pips} pips, active SR geometry is `{sr_label}`, "
        f"and break status is `{break_label}`. {reason}\n\n"
        + (f"Important nuance: marker-flow/reference geometry also records `{default_sr_label}`. That is a separate reference marker context, "
           "not the final active exit geometry, so future verifier/draft text must name which SR reference it means.\n\n" if default_sr_label else "")
        + "Training instruction: store this as a correction example. When Draft ML Reason mixes old family/RAG notes with current Auto Suggest evidence, "
        "the deterministic Auto Suggest/trade-result fields win. BPHS-like orb strength for AVG(ALL) synthetic square remains a low-confidence proxy, "
        "not doctrinal proof.\n"
    )


def replay_change_is_material(item: dict[str, Any]) -> bool:
    try:
        if abs(float(item.get("pips_delta") or 0.0)) >= 0.1:
            return True
    except Exception:
        pass
    return str(item.get("stored_start_rule") or "") != str(item.get("replayed_start_rule") or "") or str(item.get("stored_end_rule") or "") != str(item.get("replayed_end_rule") or "")


def process_task(conn: Any, row: Any) -> dict[str, Any]:
    task = row_to_dict(row)
    task_id = int(task["task_id"])
    task_type = str(task.get("task_type") or "")
    if task_type == "official_ml_note":
        note = compose_official_note_from_review(task)
        note_id = replace_rule_note_type(conn, case_id=int(task["case_id"]), note_type="official_ml_note", note_text=note)
        update_codex_review_task(conn, task_id, status="done", result={"action": "official_note_written", "note_id": note_id})
        return {"task_id": task_id, "status": "done", "action": "official_note_written", "note_id": note_id}
    if task_type == "dream_review_correction":
        note = compose_dream_correction_note(task)
        note_id = replace_rule_note_type(conn, case_id=int(task["case_id"]), note_type="official_ml_note", note_text=note)
        update_codex_review_task(conn, task_id, status="done", result={"action": "dream_review_correction_applied", "note_id": note_id})
        return {"task_id": task_id, "status": "done", "action": "dream_review_correction_applied", "note_id": note_id}
    if task_type == "rule_replay_review":
        payload = task.get("payload") or {}
        affected = payload.get("affected_cases") or []
        material = [item for item in affected if isinstance(item, dict) and replay_change_is_material(item)]
        if not material:
            update_codex_review_task(
                conn,
                task_id,
                status="skipped",
                result={"action": "no_material_replay_change", "reason": "Only rule-version metadata changed; pips/rule path unchanged."},
            )
            return {"task_id": task_id, "status": "skipped", "action": "no_material_replay_change"}
        update_codex_review_task(
            conn,
            task_id,
            status="failed",
            result={"action": "material_replay_change_needs_codex", "affected_cases": material},
        )
        return {"task_id": task_id, "status": "failed", "action": "material_replay_change_needs_codex", "affected_count": len(material)}
    update_codex_review_task(conn, task_id, status="skipped", result={"action": "unsupported_task_type", "task_type": task_type})
    return {"task_id": task_id, "status": "skipped", "action": "unsupported_task_type", "task_type": task_type}


def process_pending_tasks(db_path: Path = DEFAULT_DB_PATH, limit: int = 20) -> dict[str, Any]:
    initialize_database(db_path)
    processed: list[dict[str, Any]] = []
    with connect(db_path) as conn:
        for row in list_codex_review_tasks(conn, status="pending", limit=limit):
            processed.append(process_task(conn, row))
        conn.commit()
    return {"processed": processed, "processed_count": len(processed)}


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

        if args.process_pending:
            print(json.dumps(process_pending_tasks(args.db, limit=args.limit), ensure_ascii=False, indent=2, default=str))
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
