from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from build_corpus_index import INDEX_PATH, build_chunks, build_index, retrieve, write_jsonl, CHUNKS_PATH, MANIFEST


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
DB_PATH = PROJECT_ROOT / "gann_aspect_annotations.sqlite"
OUT_DIR = ROOT / "case_explanations"

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
        "trades": trades,
        "ignores": ignores,
    }


def compact_case_summary(packet: dict[str, Any]) -> str:
    case = packet["case"]
    context = packet["context"]
    lines = [
        f"case_id={case['case_id']} family={case['pair_key']}::{case['aspect']}",
        f"window={case['window_start_ist']} -> {case['window_end_ist']} timeframe={case.get('timeframe')}",
    ]
    for key in IMPORTANT_CONTEXT_KEYS:
        value = context.get(key)
        if value not in (None, ""):
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
    model = os.getenv("OLLAMA_MODEL", "llama3.1")
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
- Separate doctrine/source hints from observed case-family evidence.
- Say when a citation is only a local note or when doctrine citation is missing.
- Output practical ML features/rules to test, not trading advice.

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


def deterministic_analysis(packet: dict[str, Any]) -> str:
    case = packet["case"]
    ctx = packet["context"]
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
    if "JUPITER" in touch_planets.upper() or "JUPITER" in notes.upper():
        reasons.append("Touched SR involves Jupiter; in this workspace note logic that is treated as a benefic/supportive floor unless price closes through it decisively.")
    if moon_relation or moon_dignity:
        reasons.append(f"Moon condition is not visibly damaged in the simple fields: relation={moon_relation}, dignity={moon_dignity}.")

    feature_list = [
        "sr_geometry_role and distance in pips",
        "support_break_threshold_pips and break_line",
        "break/retest/continuation status",
        "touched SR planet and benefic/malefic nature",
        "Shadbala total and ratio bucket",
        "Drik Bala signed pressure plus benefic/malefic split",
        "Chesta/motion strength bucket",
        "aspect exactness/orb bucket",
        "active nearby regime count",
        "rule_vs_default_pips_delta",
    ]

    return "\n".join(
        [
            "## Deterministic Plain-English Analysis",
            "",
            f"- Case `{case['case_id']}` is `{case['pair_key']}::{case['aspect']}` from `{case['window_start_ist']}` to `{case['window_end_ist']}`.",
            f"- The stored 72h outcome direction is `{ret_dir}` with return `{ret_pct}`.",
            f"- Nearby active regime count is `{regime_count}`, so attribution remains important.",
            "- Probable reason this can be bearish without cleanly breaking support:",
            *[f"  - {reason}" for reason in reasons],
            "- ML features to log/test:",
            *[f"  - {item}" for item in feature_list],
            "- Rule status suggestion: keep `bearish_bias_support_barrier` provisional until all family repeatations are reviewed and rule-vs-default tracking shows improvement.",
        ]
    )


def extractive_answer(packet: dict[str, Any], case_summary: str, retrieved: list[dict[str, Any]], question: str) -> str:
    lines = [
        "# Local Jyotish Agent Draft",
        "",
        "LLM runtime was not available, so this is an extractive RAG draft from deterministic evidence and local notes.",
        "",
        "## Question",
        question,
        "",
        deterministic_analysis(packet),
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
    retrieved = retrieve(case_summary + "\n" + question, top_k=8)
    prompt = build_prompt(case_summary, retrieved, question)
    llm_text = ollama_generate(prompt) if use_llm else None
    text = llm_text or extractive_answer(packet, case_summary, retrieved, question)
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
