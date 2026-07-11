from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

import requests

from build_corpus_index import INDEX_PATH, build_chunks, build_index, retrieve, write_jsonl, CHUNKS_PATH, MANIFEST


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
DB_PATH = PROJECT_ROOT / "gann_aspect_annotations.sqlite"
OUT_DIR = ROOT / "case_explanations"
DREAM_CORRECTIONS_PATH = ROOT / "dream_review_corrections.jsonl"

IMPORTANT_CONTEXT_KEYS = [
    "event_strict_shadbala_implemented_total_virupa_avg",
    "event_strict_shadbala_implemented_total_ratio_avg",
    "event_strict_drik_bala_virupa_avg",
    "event_strict_drik_benefic_virupa_avg",
    "event_strict_drik_malefic_virupa_avg",
    "event_strict_chesta_bala_virupa_avg",
    "event_orb_deg",
    "event_bphs_like_orb_strength",
    "aspect_regime_active_count",
    "event_b2_sign",
    "event_b2_sign_relation",
    "event_b2_sthana_dignity_label",
    "event_b2_strict_whole_sign_house",
    "event_tithi_name",
    "event_paksha",
    "event_weekday",
    "event_weekday_lord",
    "event_moon_nakshatra",
    "event_moon_pada",
    "event_yoga_name",
    "event_karana_name",
    "touch_planets",
    "touch_line_price_1",
    "touch_line_price_2",
    "ret_after_72h_pct",
    "ret_after_72h_dir",
    "event_strict_shadbala_decision_notes",
]


def ensure_index() -> None:
    if INDEX_PATH.exists():
        return
    chunks = build_chunks(MANIFEST)
    if not chunks:
        raise SystemExit("No Jyotish corpus chunks available. Run build_corpus_index.py after adding sources.")
    write_jsonl(CHUNKS_PATH, chunks)
    build_index(chunks, INDEX_PATH)


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any]:
    return dict(row) if row is not None else {}


def parse_json_field(value: Any, fallback: Any) -> Any:
    if value in (None, ""):
        return fallback
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value))
    except Exception:
        return fallback


def load_dream_corrections(case_id: int, family_key: str, limit: int = 8) -> list[dict[str, Any]]:
    if not DREAM_CORRECTIONS_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in DREAM_CORRECTIONS_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        summary = row.get("payload_summary") if isinstance(row.get("payload_summary"), dict) else {}
        row_case = int(row.get("case_id") or summary.get("case_id") or 0)
        row_family = str(row.get("family") or summary.get("family") or "")
        if row_case == int(case_id) or row_family == family_key:
            rows.append(row)
    return rows[-limit:]


def load_case(case_id: int, db_path: Path) -> dict[str, Any]:
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        case = row_to_dict(conn.execute("SELECT * FROM aspect_cases WHERE case_id = ?", (case_id,)).fetchone())
        if not case:
            raise SystemExit(f"case_id={case_id} not found in {db_path}")
        exact_notes = [row_to_dict(r) for r in conn.execute("SELECT * FROM rule_notes WHERE case_id = ? ORDER BY created_at_utc, note_id", (case_id,))]
        trades = [row_to_dict(r) for r in conn.execute("SELECT * FROM trade_annotations WHERE case_id = ? ORDER BY created_at_utc, annotation_id", (case_id,))]
        ignores = [row_to_dict(r) for r in conn.execute("SELECT * FROM ignore_regions WHERE case_id = ? ORDER BY created_at_utc, ignore_id", (case_id,))]
        family_notes = [
            row_to_dict(r)
            for r in conn.execute(
                """
                SELECT n.*, c.pair_key, c.aspect
                FROM rule_notes n
                JOIN aspect_cases c ON c.case_id = n.case_id
                WHERE c.pair_key = ? AND c.aspect = ?
                ORDER BY n.created_at_utc, n.note_id
                """,
                (case["pair_key"], case["aspect"]),
            )
        ]
        family_key = f"{case['pair_key']}::{case['aspect']}"
        try:
            rule_lessons = [
                row_to_dict(r)
                for r in conn.execute(
                    """
                    SELECT *
                    FROM rule_lessons
                    WHERE case_id = ? OR family_key = ?
                    ORDER BY updated_at_utc DESC, lesson_id DESC
                    LIMIT 24
                    """,
                    (case_id, family_key),
                )
            ]
        except sqlite3.OperationalError:
            rule_lessons = []
    context = {}
    try:
        context = json.loads(case.get("context_json") or "{}")
    except json.JSONDecodeError:
        context = {}
    return {
        "case": case,
        "context": context,
        "exact_notes": exact_notes,
        "family_notes": family_notes,
        "rule_lessons": rule_lessons,
        "dream_corrections": load_dream_corrections(case_id, f"{case['pair_key']}::{case['aspect']}"),
        "trades": trades,
        "ignores": ignores,
    }


def compact_case_summary(packet: dict[str, Any]) -> str:
    case = packet["case"]
    context = packet["context"]
    synthetic_avg_square = "AVG(ALL)" in str(case.get("pair_key", "")).upper() or str(case.get("aspect", "")).lower() == "square"
    lines = [
        f"case_id={case['case_id']} family={case['pair_key']}::{case['aspect']}",
        f"window={case['window_start_ist']} -> {case['window_end_ist']} timeframe={case.get('timeframe')}",
    ]
    for key in IMPORTANT_CONTEXT_KEYS:
        value = context.get(key)
        if value not in (None, ""):
            if key == "event_bphs_like_orb_strength" and synthetic_avg_square:
                lines.append(
                    "event_bphs_like_orb_strength=not_applicable_for_synthetic_AVG_ALL_square "
                    f"(raw={value}; do not treat raw 0.0 as a doctrinal BPHS zero)"
                )
                continue
            lines.append(f"{key}={value}")
    if packet["exact_notes"]:
        lines.append("Exact-case notes:")
        for note in packet["exact_notes"]:
            lines.append(f"- note_id={note['note_id']} type={note['note_type']} {note['note_text'][:900]}")
    family_ml = [n for n in packet["family_notes"] if "ml" in str(n.get("note_type", "")).lower() or "ml_" in str(n.get("note_text", "")).lower()]
    if family_ml:
        lines.append("Family ML notes:")
        for note in family_ml[:4]:
            lines.append(f"- note_id={note['note_id']} case_id={note['case_id']} type={note['note_type']} {note['note_text'][:900]}")
    if packet.get("rule_lessons"):
        lines.append("Rule conflict lessons / training memory:")
        for lesson in packet["rule_lessons"][:8]:
            hints = parse_json_field(lesson.get("astro_hints_json"), [])
            hint_text = "; ".join(str(item) for item in hints[:6]) if isinstance(hints, list) else str(hints)[:500]
            lines.append(
                "- "
                f"lesson_id={lesson.get('lesson_id')} case_id={lesson.get('case_id')} "
                f"conflict={lesson.get('conflict_type')} winner={lesson.get('winner_rule')} "
                f"status={lesson.get('status')} text={str(lesson.get('lesson_text') or '')[:900]} "
                f"astro_hints={hint_text}"
            )
    if packet.get("dream_corrections"):
        lines.append("Dream Review corrections / verifier memory:")
        for correction in packet["dream_corrections"][-6:]:
            applied = correction.get("applied") if isinstance(correction.get("applied"), list) else []
            issues = correction.get("issues") if isinstance(correction.get("issues"), list) else []
            lines.append(
                "- "
                f"created_at={correction.get('created_at')} status={correction.get('status')} "
                f"message={str(correction.get('message') or '')[:500]} "
                f"applied={json.dumps(applied[:3], ensure_ascii=False, default=str)[:600]} "
                f"issues={json.dumps(issues[:3], ensure_ascii=False, default=str)[:600]}"
            )
    if packet["trades"]:
        lines.append("Saved trades:")
        for trade in packet["trades"]:
            lines.append(f"- {trade}")
    if packet["ignores"]:
        lines.append("Ignore regions:")
        for ignore in packet["ignores"]:
            lines.append(f"- {ignore}")
    return "\n".join(lines)


def ollama_generate(prompt: str) -> str | None:
    endpoint = os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/generate")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    try:
        resp = requests.post(endpoint, json={"model": model, "prompt": prompt, "stream": False}, timeout=120)
        if resp.status_code >= 400:
            return None
        data = resp.json()
        return str(data.get("response") or "").strip() or None
    except requests.RequestException:
        return None


def build_prompt(case_summary: str, retrieved: list[dict[str, Any]], question: str) -> str:
    sources = []
    for item in retrieved:
        sources.append(
            f"[{item['chunk_id']} | {item['title']} | score={item['score']:.3f}]\n{item['text'][:1600]}"
        )
    return f"""You are a strict Jyotish research assistant for a USDJPY Gann/financial astrology workspace.

Rules:
- Do not invent ephemeris, Shadbala, trades, or marker positions.
- Use the deterministic case evidence as ground truth.
- Treat "Rule conflict lessons / training memory" and "Dream Review corrections / verifier memory" as high-priority local memory.
- If Dream Review corrected an older note, follow the correction and say the older wording is stale.
- Separate doctrine/source hints from observed case-family evidence.
- Say when a citation is only a local note or when doctrine citation is missing.
- Output practical ML features/rules to test, not trading advice.
- Keep the answer about the exact case in the evidence. Do not drift to generic planets or unrelated aspects.
- If the evidence does not mention a planet/aspect, do not mention it.
- Use the exact numeric fields from the evidence when available.

Question:
{question}

Case evidence:
{case_summary}

Retrieved local sources:
{chr(10).join(sources)}

Draft a concise explanation with:
1. What happened.
2. Probable why.
3. Which features ML should log.
4. Rule candidate/status.
5. Missing citations or uncertainty.
"""


def llm_drift_warning(case_id: int, case_summary: str, llm_text: str | None) -> str | None:
    if not llm_text:
        return "Local LLM did not return text."
    checks = [
        f"case_id={case_id}" in case_summary and str(case_id) in llm_text,
        "MOON" not in case_summary.upper() or "moon" in llm_text.lower(),
        "JUPITER" not in case_summary.upper() or "jupiter" in llm_text.lower(),
    ]
    banned_generic = ("sun, mercury, venus", "nepture", "economic indicators")
    direction_conflict = (
        ("ret_after_72h_dir=DOWN" in case_summary or "direction=bearish" in case_summary.lower())
        and "bullish bias" in llm_text.lower()
    )
    if direction_conflict or not all(checks) or any(item in llm_text.lower() for item in banned_generic):
        return (
            "Local LLM commentary may have drifted from the evidence. "
            "Use the deterministic analysis below as ground truth and treat the LLM section as untrusted draft text."
        )
    return None


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def bucket_strength(value: float | None, low: float, high: float) -> str:
    if value is None:
        return "unknown"
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "middle"


def extract_auto_suggest(question: str) -> dict[str, Any]:
    marker = "Auto Suggest summary:"
    idx = question.find(marker)
    if idx < 0:
        return {}
    raw = question[idx + len(marker):].lstrip()
    decoder = json.JSONDecoder()
    try:
        parsed, _ = decoder.raw_decode(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def extract_trade_result(question: str) -> str:
    match = re.search(r"Current manual/auto trade result:\s*(.+)", question)
    return match.group(1).strip() if match else ""


def fmt_pips(value: Any) -> str:
    num = as_float(value)
    if num is None:
        return "unknown"
    return f"{num:+.1f} pips"


def deterministic_analysis(packet: dict[str, Any], question: str = "") -> str:
    case = packet["case"]
    ctx = packet["context"]
    auto = extract_auto_suggest(question)
    trade_result = extract_trade_result(question)
    shad = as_float(ctx.get("event_strict_shadbala_implemented_total_virupa_avg"))
    ratio = as_float(ctx.get("event_strict_shadbala_implemented_total_ratio_avg"))
    drik = as_float(ctx.get("event_strict_drik_bala_virupa_avg"))
    benefic = as_float(ctx.get("event_strict_drik_benefic_virupa_avg"))
    malefic = as_float(ctx.get("event_strict_drik_malefic_virupa_avg"))
    chesta = as_float(ctx.get("event_strict_chesta_bala_virupa_avg"))
    orb = as_float(ctx.get("event_orb_deg"))
    regime_count = ctx.get("aspect_regime_active_count", "unknown")
    touch_planets = str(ctx.get("touch_planets") or "").strip()
    ret_dir = str(ctx.get("ret_after_72h_dir") or "unknown").strip()
    ret_pct = ctx.get("ret_after_72h_pct", "unknown")
    moon_relation = ctx.get("event_b2_sign_relation", "unknown")
    moon_dignity = ctx.get("event_b2_sthana_dignity_label", "unknown")
    notes = "\n".join(str(n.get("note_text", "")) for n in packet["exact_notes"] + packet["family_notes"])
    break_info = auto.get("break_confirmation") if isinstance(auto.get("break_confirmation"), dict) else {}
    sr_geom = auto.get("sr_geometry") if isinstance(auto.get("sr_geometry"), dict) else {}
    barrier_geom = auto.get("barrier_sr_geometry") if isinstance(auto.get("barrier_sr_geometry"), dict) else {}
    attribution = auto.get("attribution_boundary") if isinstance(auto.get("attribution_boundary"), dict) else {}
    tracking = auto.get("outcome_tracking") if isinstance(auto.get("outcome_tracking"), dict) else {}

    setup_lines = []
    if auto:
        setup_lines.append(f"Auto Suggest confidence is `{auto.get('confidence', 'unknown')}`.")
        if auto.get("applied_family_rule"):
            setup_lines.append(f"Applied family rule: `{auto.get('applied_family_rule')}`.")
        if sr_geom:
            setup_lines.append(
                f"Final SR geometry: {sr_geom.get('label', 'unknown')} "
                f"({fmt_pips(sr_geom.get('distance_pips'))} from entry; epsilon {fmt_pips(sr_geom.get('epsilon_pips')).replace('+', '')})."
            )
        if barrier_geom and barrier_geom != sr_geom:
            setup_lines.append(
                f"First barrier checked: {barrier_geom.get('label', 'unknown')} "
                f"({fmt_pips(barrier_geom.get('distance_pips'))} from entry)."
            )
        if break_info:
            setup_lines.append(
                f"Break confirmation: {break_info.get('label', break_info.get('status', 'unknown'))}; "
                f"threshold {fmt_pips(break_info.get('threshold_pips')).replace('+', '')}; "
                f"break line {break_info.get('break_line', 'unknown')}."
            )
        if attribution:
            setup_lines.append(
                "Attribution boundary: exit at the next hardcoded marker/event "
                f"`{attribution.get('markerLabel', attribution.get('traceName', 'unknown'))}` "
                f"near `{attribution.get('x', 'unknown')}` @ `{attribution.get('y', 'unknown')}`."
            )
        if tracking:
            setup_lines.append(
                f"Rule tracking: rule {fmt_pips(tracking.get('rule_signed_pips'))} vs default "
                f"{fmt_pips(tracking.get('default_signed_pips'))}; delta {fmt_pips(tracking.get('delta_signed_pips'))}."
            )
    if trade_result:
        setup_lines.append(f"Current marker result from drawer: {trade_result}.")

    reasons = []
    if shad is not None:
        ratio_text = f"{ratio:.3f}" if ratio is not None else "unknown"
        reasons.append(
            f"Total implemented Shadbala is {shad:.2f} ({bucket_strength(shad, 240, 480)}); ratio vs minimum is "
            f"{ratio_text}."
        )
    if drik is not None:
        tilt = "supportive/mild" if drik >= 0 else "stressful"
        benefic_text = f"{benefic:.2f}" if benefic is not None else "unknown"
        malefic_text = f"{malefic:.2f}" if malefic is not None else "unknown"
        reasons.append(
            f"Drik/aspect pressure is {drik:.2f}, a {tilt} reading rather than a heavy bearish crush. "
            f"Benefic={benefic_text}, malefic={malefic_text}."
        )
    if chesta is not None:
        reasons.append(f"Chesta/motion strength is {chesta:.2f} ({bucket_strength(chesta, 5, 35)}), so unusual motion force is not the main driver.")
    if orb is not None:
        reasons.append(f"Aspect distance from exact is {orb:.2f} degrees ({bucket_strength(orb, 45, 75)} in current feature buckets), so this is not a very tight exact-aspect hit.")
    if "AVG(ALL)" in str(case.get("pair_key", "")).upper() or str(case.get("aspect", "")).lower() == "square":
        reasons.append(
            "BPHS-like orb strength is not treated as a clean doctrine field here because AVG(ALL) is synthetic "
            "and square is not a direct classical BPHS graha-drishti measure; use event_orb_deg and observed family behavior instead."
        )
    if "JUPITER" in touch_planets.upper() or "JUPITER" in notes.upper():
        reasons.append("Touched SR involves Jupiter; in this workspace note logic that is treated as a benefic/supportive floor unless price closes through it decisively.")
    if moon_relation or moon_dignity:
        reasons.append(f"Moon condition is not visibly damaged in the simple fields: relation={moon_relation}, dignity={moon_dignity}.")

    feature_list = [
        "sr_geometry_role and distance in pips",
        "sr_geometry_epsilon_pips / at-SR band",
        "support_break_threshold_pips and break_line",
        "break/retest/continuation status",
        "attribution_boundary marker/time/aspect",
        "touched SR planet and benefic/malefic nature",
        "Shadbala total and ratio bucket",
        "Drik Bala signed pressure plus benefic/malefic split",
        "Chesta/motion strength bucket",
        "aspect exactness/orb bucket",
        "active nearby regime count",
        "rule_vs_default_pips_delta",
    ]
    if break_info.get("status") == "confirmed":
        behavior_label = "Probable reason this bearish family rule can continue after support breaks, while still stopping at the next attribution boundary:"
    elif str(sr_geom.get("position", "")).startswith("below"):
        behavior_label = "Probable reason this can be bearish into support, but should not assume a clean support break without confirmation:"
    else:
        behavior_label = "Probable astro/trading reasons to test:"

    lines = [
            "## Deterministic Plain-English Analysis",
            "",
            f"- Case `{case['case_id']}` is `{case['pair_key']}::{case['aspect']}` from `{case['window_start_ist']}` to `{case['window_end_ist']}`.",
            f"- The stored 72h outcome direction is `{ret_dir}` with return `{ret_pct}`.",
            f"- Nearby active regime count is `{regime_count}`, so attribution remains important.",
        ]
    if setup_lines:
        lines.extend(["- Current UI / rule evidence:", *[f"  - {item}" for item in setup_lines]])
    lines.extend(
        [
            f"- {behavior_label}",
            *[f"  - {reason}" for reason in reasons],
            "- ML features to log/test:",
            *[f"  - {item}" for item in feature_list],
            "- Rule status suggestion: keep `bearish_bias_support_barrier` provisional until all family repeatations are reviewed and rule-vs-default tracking shows improvement.",
        ]
    )
    return "\n".join(lines)


def extractive_answer(packet: dict[str, Any], case_summary: str, retrieved: list[dict[str, Any]], question: str) -> str:
    lines = [
        "# Local Jyotish Agent Draft",
        "",
        "LLM runtime was not available, so this is an extractive RAG draft from deterministic evidence and local notes.",
        "",
        "## Question",
        question,
        "",
        deterministic_analysis(packet, question),
        "",
        "## Deterministic Case Evidence",
        "```text",
        case_summary[:5000],
        "```",
        "",
        "## Retrieved Sources",
    ]
    for item in retrieved:
        lines.extend(
            [
                f"### {item['chunk_id']} | {item['title']} | score={item['score']:.3f}",
                item["text"][:1400],
                "",
            ]
        )
    lines.extend(
        [
            "## Draft Interpretation",
            "- Treat this as a cited assistant draft, not final ML truth.",
            "- Compare the exact-case notes with the family ML notes before accepting any rule.",
            "- Promote a rule only after repeatation review and rule-vs-default tracking improve out-of-sample behavior.",
        ]
    )
    return "\n".join(lines)


def explain(case_id: int, question: str, db_path: Path, out_dir: Path, use_llm: bool) -> Path:
    ensure_index()
    packet = load_case(case_id, db_path)
    case_summary = compact_case_summary(packet)
    retrieval_query = case_summary + "\n" + question
    structured_sources = {"CURRENT_RULE_NOTES", "TOUCH_LOG"}
    retrieved = [
        *retrieve(retrieval_query, top_k=4, source_ids=structured_sources),
        *retrieve(retrieval_query, top_k=4, exclude_source_ids=structured_sources),
    ]
    prompt = build_prompt(case_summary, retrieved, question)
    llm_text = ollama_generate(prompt) if use_llm else None
    if llm_text:
        warning = llm_drift_warning(case_id, case_summary, llm_text)
        text_parts = [
            "# Local Jyotish Agent Draft",
            "",
            "## Question",
            question,
            "",
            deterministic_analysis(packet, question),
            "",
            "## Local LLM Commentary",
        ]
        if warning:
            text_parts.extend(
                [
                    "",
                    f"**Omitted:** {warning}",
                    "",
                    "The local model produced commentary that failed the evidence checks, so this draft keeps only deterministic analysis and retrieved local notes.",
                    "",
                ]
            )
        else:
            text_parts.extend(["", llm_text, ""])
        text_parts.extend(
            [
                "",
                "## Deterministic Case Evidence",
                "```text",
                case_summary[:5000],
                "```",
                "",
                "## Retrieved Sources",
            ]
        )
        for item in retrieved:
            text_parts.extend(
                [
                    f"### {item['chunk_id']} | {item['title']} | score={item['score']:.3f}",
                    item["text"][:1400],
                    "",
                ]
            )
        text = "\n".join(text_parts)
    else:
        text = extractive_answer(packet, case_summary, retrieved, question)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"case_{case_id}_jyotish_explanation.md"
    out_path.write_text(text, encoding="utf-8")
    (out_dir / f"case_{case_id}_evidence_packet.json").write_text(
        json.dumps(packet, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (out_dir / f"case_{case_id}_retrieved_chunks.json").write_text(
        json.dumps(retrieved, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Draft a local Jyotish/RAG explanation for a reviewed case_id.")
    parser.add_argument("--case-id", type=int, required=True)
    parser.add_argument("--question", default="Explain this case behavior and propose ML features/rules to test.")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--no-llm", action="store_true", help="Skip Ollama even if it is running.")
    args = parser.parse_args()
    out = explain(args.case_id, args.question, args.db, args.out_dir, use_llm=not args.no_llm)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
