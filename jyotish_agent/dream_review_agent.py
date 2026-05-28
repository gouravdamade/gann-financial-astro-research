from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
DB_PATH = PROJECT_ROOT / "gann_aspect_annotations.sqlite"
REPORT_DIR = ROOT / "dream_review_reports"
QUEUE_PATH = ROOT / "dream_review_queue.jsonl"
CORRECTIONS_PATH = ROOT / "dream_review_corrections.jsonl"


SAFE_STALE_BREAK_PHRASES = (
    "reverted instead of breaking support",
    "reverted instead of breaking resistance",
    "instead of breaking support",
    "instead of breaking resistance",
    "did not break support",
    "did not break resistance",
    "failed to break support",
    "failed to break resistance",
    "no clean break",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def load_payload(path: Path | None) -> dict[str, Any]:
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(sys.stdin.read() or "{}")


def issue_titles(report: dict[str, Any]) -> set[str]:
    return {str(item.get("title") or "") for item in report.get("issues", []) if isinstance(item, dict)}


def issue_severities(report: dict[str, Any]) -> set[str]:
    return {str(item.get("severity") or "") for item in report.get("issues", []) if isinstance(item, dict)}


def contains_stale_break_phrase(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in SAFE_STALE_BREAK_PHRASES)


def corrected_break_note_text(case_id: int, family: str, evidence: dict[str, Any], old_text: str) -> str:
    outcome = evidence.get("outcome") or "unknown"
    sr_label = evidence.get("sr_label") or "SR geometry unavailable"
    break_label = evidence.get("break_label") or evidence.get("break_status") or "break status unavailable"
    global_exit = evidence.get("global_exit_boundary") or {}
    attribution = evidence.get("attribution_boundary") or {}
    exit_bits = []
    if isinstance(global_exit, dict) and global_exit:
        exit_bits.append(f"global_exit={global_exit.get('x', 'unknown')} @ {global_exit.get('y', 'unknown')}")
    if isinstance(attribution, dict) and attribution:
        exit_bits.append(f"attribution_boundary={attribution.get('x', 'unknown')} @ {attribution.get('y', 'unknown')}")
    exit_text = "; ".join(exit_bits) if exit_bits else "exit boundary from current Auto Suggest evidence"
    return (
        f"scope=case_id/local; type=ml_astro_reason; case_id={case_id}; family={family}; "
        "label=dream_corrected_confirmed_break_global_exit; "
        "status=dream_corrected_safe_stale_note; "
        "correction_reason=older note language conflicted with current deterministic verifier evidence.\n\n"
        f"Dream correction at {utc_now()}: current verifier evidence says outcome={outcome}, {sr_label}, "
        f"break_confirmation={break_label}, and {exit_text}. Therefore old wording that implied a failed/no support break "
        "must not be used for ML training for this recurrence.\n\n"
        "Corrected learning: treat this case as confirmed break behavior only when the deterministic break/retest/continuation "
        "rule says confirmed, then exit using global boundary discipline: first SR-line touch, next shaded zone, or next hardcoded "
        "marker, whichever appears first. Keep the usual astrology-strength caveat: Shadbala/Drik/Chesta/orb features are evidence "
        "weights, not standalone proof.\n\n"
        "Previous note snapshot for audit:\n"
        f"{old_text[:1800]}"
    )


def safe_apply_break_correction(case_id: int, family: str, evidence: dict[str, Any], db_path: Path) -> list[dict[str, Any]]:
    if evidence.get("break_status") != "confirmed":
        return []
    applied: list[dict[str, Any]] = []
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = list(
            conn.execute(
                """
                SELECT note_id, note_type, note_text
                FROM rule_notes
                WHERE case_id = ?
                  AND (lower(note_type) LIKE '%ml%' OR lower(note_text) LIKE '%ml%')
                ORDER BY note_id
                """,
                (case_id,),
            )
        )
        for row in rows:
            text = str(row["note_text"] or "")
            if "dream_corrected_safe_stale_note" in text:
                continue
            if not contains_stale_break_phrase(text):
                continue
            new_text = corrected_break_note_text(case_id, family, evidence, text)
            conn.execute("UPDATE rule_notes SET note_text = ? WHERE note_id = ?", (new_text, row["note_id"]))
            applied.append(
                {
                    "note_id": row["note_id"],
                    "action": "updated_rule_note",
                    "reason": "stale break/no-break wording contradicted confirmed break evidence",
                }
            )
        if applied:
            conn.commit()
    return applied


def classify_and_apply(payload: dict[str, Any], apply_safe: bool, db_path: Path) -> dict[str, Any]:
    case_id = int(payload.get("case_id") or 0)
    family = str(payload.get("family") or "")
    report = payload.get("verifier_report") if isinstance(payload.get("verifier_report"), dict) else {}
    evidence = report.get("evidence") if isinstance(report.get("evidence"), dict) else {}
    titles = issue_titles(report)
    severities = issue_severities(report)
    contradictions = [i for i in report.get("issues", []) if isinstance(i, dict) and i.get("severity") == "contradiction"]
    safe_candidates: list[dict[str, Any]] = []
    needs_review: list[dict[str, Any]] = []

    if "Break-confirmation conflict" in titles and evidence.get("break_status") == "confirmed":
        safe_candidates.append(
            {
                "type": "stale_break_note",
                "reason": "Verifier says current evidence confirms break but some draft/note text says no break.",
                "safe_to_apply": True,
            }
        )
    if "Direction conflict" in titles:
        needs_review.append(
            {
                "type": "direction_conflict",
                "reason": "Direction conflicts can be fixed only after checking whether the note or the selected outcome is wrong.",
            }
        )
    if "SR geometry conflict" in titles:
        needs_review.append(
            {
                "type": "sr_geometry_conflict",
                "reason": "SR above/below wording conflicts with chart geometry; review if Auto Suggest target is correct first.",
            }
        )
    if "Generic market claim" in titles:
        safe_candidates.append(
            {
                "type": "unsupported_generic_claim",
                "reason": "Generic macro/sentiment claims should be omitted unless explicitly cited.",
                "safe_to_apply": False,
            }
        )

    applied: list[dict[str, Any]] = []
    if apply_safe and case_id and any(item["type"] == "stale_break_note" for item in safe_candidates):
        applied.extend(safe_apply_break_correction(case_id, family, evidence, db_path))

    status = "clean"
    if contradictions and applied:
        status = "auto_corrected"
    elif contradictions:
        status = "queued_for_codex"
    elif "caution" in severities:
        status = "caution_only"
    elif report.get("verdict") == "verified":
        status = "verified"

    return {
        "ok": True,
        "created_at": utc_now(),
        "case_id": case_id,
        "family": family,
        "verdict_before": report.get("verdict"),
        "status": status,
        "safe_candidates": safe_candidates,
        "needs_review": needs_review,
        "applied": applied,
        "issues": report.get("issues", []),
        "checks": report.get("checks", []),
        "message": dream_message(status, safe_candidates, needs_review, applied),
    }


def dream_message(
    status: str,
    safe_candidates: list[dict[str, Any]],
    needs_review: list[dict[str, Any]],
    applied: list[dict[str, Any]],
) -> str:
    if status == "auto_corrected":
        return f"Dream review auto-corrected {len(applied)} stale note(s). Rebuild/reload to embed corrected notes."
    if status == "queued_for_codex":
        return "Dream review found contradiction(s) but did not auto-apply; queued for Codex review-agent correction."
    if status == "caution_only":
        return "Dream review found only caution-level issues; no correction needed."
    if status == "verified":
        return "Dream review found no contradictions."
    if safe_candidates or needs_review:
        return "Dream review produced candidates; inspect report before training."
    return "Dream review completed."


def write_report(result: dict[str, Any], payload: dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    case_id = int(payload.get("case_id") or 0)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"case_{case_id}_{stamp}_dream_review.md"
    lines = [
        "# Dream Review Report",
        "",
        f"- case_id: {case_id}",
        f"- family: {payload.get('family', '')}",
        f"- status: {result.get('status')}",
        f"- verdict before: {result.get('verdict_before')}",
        f"- created_at: {result.get('created_at')}",
        "",
        "## Message",
        result.get("message", ""),
        "",
        "## Applied Corrections",
    ]
    if result.get("applied"):
        for item in result["applied"]:
            lines.append(f"- note_id={item.get('note_id')}: {item.get('reason')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Issues"])
    for item in result.get("issues", []):
        lines.append(f"- {item.get('severity')}: {item.get('title')} - {item.get('detail')}")
    lines.extend(["", "## Checks"])
    for item in result.get("checks", []):
        lines.append(f"- {item}")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run(payload: dict[str, Any], apply_safe: bool, db_path: Path) -> dict[str, Any]:
    result = classify_and_apply(payload, apply_safe=apply_safe, db_path=db_path)
    report_path = write_report(result, payload)
    result["report_path"] = str(report_path)
    row = {"payload_summary": {k: payload.get(k) for k in ("case_id", "family")}, **result}
    if result["status"] in {"queued_for_codex", "auto_corrected"}:
        append_jsonl(QUEUE_PATH, row)
    if result.get("applied"):
        append_jsonl(CORRECTIONS_PATH, row)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Check local ML draft/verifier output and apply safe dream corrections.")
    parser.add_argument("--payload", type=Path, help="JSON payload path. Defaults to stdin.")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--apply-safe", action="store_true", help="Apply narrow deterministic corrections.")
    args = parser.parse_args()
    payload = load_payload(args.payload)
    print(json.dumps(run(payload, apply_safe=args.apply_safe, db_path=args.db), ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
