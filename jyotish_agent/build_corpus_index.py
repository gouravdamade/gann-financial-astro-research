from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Iterable

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
MANIFEST = ROOT / "corpus_manifest.csv"
CHUNKS_PATH = ROOT / "corpus_chunks.jsonl"
INDEX_PATH = ROOT / "index" / "tfidf_index.joblib"
PDF_EXTRACTS = PROJECT_ROOT / "pdf_alignment_extracts"
DB_PATH = PROJECT_ROOT / "gann_aspect_annotations.sqlite"
TOUCH_LOG = PROJECT_ROOT / "aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv"

LOCAL_TEXT_SOURCES = {
    "STRICT_VEDIC_LLM": PDF_EXTRACTS / "Building a Strict Vedic Astrology Prediction Engine with a Local LLM Layer.txt",
    "SHADBALA_JAYA": PDF_EXTRACTS / "jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.txt",
    "GANN_TUNNEL_1927": Path(
        r"D:\GannFinancialAstro\sources\gann\GANN_TUNNEL_1927_PROJECT_GUTENBERG.txt"
    ),
    "AGARWAL_FINANCIAL_CHAPTER20_HYPOTHESIS_20260722": Path(
        r"D:\GannFinancialAstro\sources\private\derived\AGARWAL_FINANCIAL_CHAPTER20_PDF_PAGES_177_191_5644DFC4.txt"
    ),
}

SUPPORTED_ASTRONOMY_CONTRACT_PREFIX = "RAMAN_SWISSEPH_SINGLE_SIDEREAL_"


def supported_astronomy_contract(value: object) -> bool:
    return str(value or "").startswith(SUPPORTED_ASTRONOMY_CONTRACT_PREFIX)


def case_astronomy_contract(context_json: object) -> str:
    try:
        context = json.loads(str(context_json or "{}"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return ""
    return str(
        context.get("event_source_astronomy_contract")
        or context.get("astronomy_contract_version")
        or ""
    )


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, source_id: str, title: str, max_chars: int = 2200) -> list[dict[str, str]]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", clean_text(text)) if p.strip()]
    chunks: list[dict[str, str]] = []
    current: list[str] = []
    current_len = 0

    def append_chunk(value: str) -> None:
        chunks.append(
            {
                "source_id": source_id,
                "title": title,
                "chunk_id": f"{source_id}-{len(chunks) + 1:04d}",
                "text": value,
            }
        )

    def flush_current() -> None:
        nonlocal current, current_len
        if current:
            append_chunk("\n\n".join(current))
            current = []
            current_len = 0

    for para in paragraphs:
        marker_lines = [line for line in para.splitlines() if line.startswith("[[") and line.endswith("]]")]
        if any(line.startswith("[[PDF_PAGE:") for line in marker_lines):
            flush_current()
            marker_prefix = "\n".join(marker_lines)
            body = "\n".join(
                line for line in para.splitlines() if not (line.startswith("[[") and line.endswith("]]"))
            ).strip()
            if not body:
                append_chunk(marker_prefix)
                continue
            body_limit = max(256, max_chars - len(marker_prefix) - 1)
            for start in range(0, len(body), body_limit):
                append_chunk(f"{marker_prefix}\n{body[start : start + body_limit]}")
            continue
        if current and current_len + len(para) + 2 > max_chars:
            flush_current()
        if len(para) > max_chars:
            for start in range(0, len(para), max_chars):
                append_chunk(para[start : start + max_chars])
            continue
        current.append(para)
        current_len += len(para) + 2
    flush_current()
    return chunks


def rule_notes_text(db_path: Path) -> str:
    with closing(sqlite3.connect(str(db_path))) as conn:
        conn.row_factory = sqlite3.Row
        case_columns = {str(row[1]) for row in conn.execute("PRAGMA table_info(aspect_cases)")}
        family_expr = (
            "c.family_key"
            if "family_key" in case_columns
            else "'LEGACY::' || UPPER(c.pair_key) || '::' || LOWER(c.aspect)"
        )
        rows = conn.execute(
            f"""
            SELECT n.note_id, n.case_id, {family_expr} AS family_key, c.pair_key, c.aspect, c.context_json,
                   n.note_type, n.note_text, n.created_at_utc
            FROM rule_notes n
            JOIN aspect_cases c ON c.case_id = n.case_id
            ORDER BY n.created_at_utc, n.note_id
            """
        ).fetchall()
    parts = []
    skipped = 0
    for row in rows:
        contract = case_astronomy_contract(row["context_json"])
        if not supported_astronomy_contract(contract):
            skipped += 1
            continue
        parts.append(
            "\n".join(
                [
                    f"note_id={row['note_id']} case_id={row['case_id']} family={row['family_key']}",
                    f"note_type={row['note_type']} created_at_utc={row['created_at_utc']}",
                    f"astronomy_contract={contract}",
                    str(row["note_text"] or ""),
                ]
            )
        )
    header = (
        "Only notes tied to the supported single-sidereal Raman astronomy contract are indexed. "
        f"Quarantined legacy/unversioned notes: {skipped}."
    )
    return "\n\n".join([header, "\n\n---\n\n".join(parts)]).strip()


def touch_log_text(path: Path) -> str:
    df = pd.read_csv(path, low_memory=False)
    columns = list(df.columns)
    feature_groups = {
        "identity": [c for c in columns if c in {"touch_id", "event_id", "event_family_key", "pair_key", "b1", "b2", "aspect"}],
        "timing": [c for c in columns if "time" in c.lower() or c in {"event_duration_minutes", "event_weekday", "event_tithi_name", "event_yoga_name", "event_karana_name", "event_moon_nakshatra"}],
        "strength": [c for c in columns if "shadbala" in c.lower() or "drik" in c.lower() or "chesta" in c.lower() or "kaala" in c.lower()],
        "sr_touch": [c for c in columns if c.startswith("touch_") or c.startswith("sr_")],
        "outcome": [c for c in columns if "ret_after" in c.lower() or "dir" in c.lower()],
    }
    lines = ["USDJPY touch log schema summary for local Jyotish agent."]
    for group, cols in feature_groups.items():
        lines.append(f"{group}: " + ", ".join(cols[:80]))
    contract_column = next(
        (name for name in ("event_source_astronomy_contract", "astronomy_contract_version") if name in df.columns),
        None,
    )
    if contract_column is None:
        lines.append(
            "Representative rows are quarantined: this legacy touch log has no astronomy contract version."
        )
        return "\n\n".join(lines)

    supported = df[contract_column].map(supported_astronomy_contract)
    quarantined = int((~supported).sum())
    df = df.loc[supported].head(80).copy()
    lines.append(
        f"Representative rows use the supported astronomy contract; quarantined rows: {quarantined}."
    )
    if df.empty:
        lines.append("No supported rows are available for retrieval.")
        return "\n\n".join(lines)
    lines.append("Representative rows:")
    keep_cols = []
    for cols in feature_groups.values():
        keep_cols.extend(cols[:8])
    keep_cols = list(dict.fromkeys([c for c in keep_cols if c in df.columns]))
    lines.append(df[keep_cols].head(12).to_string(index=False))
    return "\n\n".join(lines)


def source_text(row: dict[str, str]) -> tuple[str, str] | None:
    source_id = row.get("source_id", "")
    title = row.get("title", source_id)
    if source_id in LOCAL_TEXT_SOURCES and LOCAL_TEXT_SOURCES[source_id].exists():
        return title, LOCAL_TEXT_SOURCES[source_id].read_text(encoding="utf-8", errors="ignore")
    if source_id == "CURRENT_RULE_NOTES" and DB_PATH.exists():
        return title, rule_notes_text(DB_PATH)
    if source_id == "TOUCH_LOG" and TOUCH_LOG.exists():
        return title, touch_log_text(TOUCH_LOG)
    local_path = ROOT / "corpus_text" / f"{source_id}.txt"
    if local_path.exists():
        return title, local_path.read_text(encoding="utf-8", errors="ignore")
    return None


def build_chunks(manifest_path: Path) -> list[dict[str, str]]:
    rows = read_manifest(manifest_path)
    chunks: list[dict[str, str]] = []
    skipped: list[str] = []
    for row in rows:
        loaded = source_text(row)
        if not loaded:
            skipped.append(row.get("source_id", "UNKNOWN"))
            continue
        title, text = loaded
        chunks.extend(chunk_text(text, row.get("source_id", "UNKNOWN"), title))
    if skipped:
        print("Skipped sources without local text:", ", ".join(skipped))
    return chunks


def write_jsonl(path: Path, rows: Iterable[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_index(chunks: list[dict[str, str]], index_path: Path) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    texts = [f"{c['title']}\n{c['text']}" for c in chunks]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=50000)
    matrix = vectorizer.fit_transform(texts)
    joblib.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}, index_path)


def retrieve(
    query: str,
    index_path: Path = INDEX_PATH,
    top_k: int = 6,
    source_ids: set[str] | None = None,
    exclude_source_ids: set[str] | None = None,
) -> list[dict[str, str | float]]:
    data = joblib.load(index_path)
    vectorizer = data["vectorizer"]
    matrix = data["matrix"]
    chunks = data["chunks"]
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    eligible = [
        idx
        for idx, chunk in enumerate(chunks)
        if (source_ids is None or chunk["source_id"] in source_ids)
        and (exclude_source_ids is None or chunk["source_id"] not in exclude_source_ids)
    ]
    order = sorted(eligible, key=lambda idx: float(scores[idx]), reverse=True)[:top_k]
    out = []
    for idx in order:
        chunk = dict(chunks[int(idx)])
        chunk["score"] = float(scores[int(idx)])
        out.append(chunk)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local TF-IDF RAG index for the Jyotish agent.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--chunks", type=Path, default=CHUNKS_PATH)
    parser.add_argument("--index", type=Path, default=INDEX_PATH)
    parser.add_argument("--query", default="", help="Optional smoke-test query after building.")
    args = parser.parse_args()

    chunks = build_chunks(args.manifest)
    if not chunks:
        raise SystemExit("No chunks available. Add local text or approve corpus sources first.")
    write_jsonl(args.chunks, chunks)
    build_index(chunks, args.index)
    print(f"Wrote chunks: {args.chunks} ({len(chunks)} chunks)")
    print(f"Wrote index: {args.index}")
    if args.query:
        for item in retrieve(args.query, args.index):
            print(f"{item['score']:.3f} {item['chunk_id']} {item['title']}")


if __name__ == "__main__":
    main()
