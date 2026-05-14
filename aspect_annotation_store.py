from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_DB_PATH = Path(__file__).resolve().with_name("gann_aspect_annotations.sqlite")
DEFAULT_REVIEW_EXPORT_DIR = Path(r"C:\Users\ADMIN\Desktop\doc")
VALID_OUTCOME_LABELS = ("bullish", "bearish", "sideways", "unclear")
IST = "Asia/Kolkata"
USDJPY_PIP_SIZE = 0.01
DEFAULT_M30_PRICE_PATH = Path(__file__).resolve().with_name("usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet")
DEFAULT_H1_PRICE_PATH = Path(__file__).resolve().with_name("usd_jpy_h1_mt5_metaquotes_demo_full.parquet")
DEFAULT_PRICE_PATHS = {
    "m30": DEFAULT_M30_PRICE_PATH,
    "h1": DEFAULT_H1_PRICE_PATH,
}
DEFAULT_TOUCH_LOG = Path(__file__).resolve().with_name(
    "aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_usdjpy_basequote_all_durations_transitsign.csv"
)
CASE_CONTEXT_COLUMNS = (
    "touch_id",
    "event_id",
    "pair_key",
    "b1",
    "b2",
    "aspect",
    "aspect_system",
    "aspect_label",
    "event_time_local",
    "event_window_start_local",
    "event_window_end_local",
    "event_duration_minutes",
    "aspect_regime_id",
    "aspect_regime_active_count",
    "aspect_regime_signature",
    "event_pair_sep_deg",
    "event_orb_deg",
    "event_orb_limit_deg",
    "event_orb_strength",
    "event_bphs_strength",
    "event_bphs_virupa",
    "event_best_time_local",
    "ret_after_72h_pct",
    "ret_after_72h_dir",
    "shadbala_tag",
    "shadbala_avg",
    "moon_nakshatra",
    "reference_time_ist",
    "base_reference_time_ist",
    "tn_primary_transit_planet",
    "tn_primary_natal_planet",
    "tn_primary_aspect",
    "tn_primary_orb_deg",
    "tn_primary_bphs_strength",
    "tn_primary_bphs_virupa",
    "tn_primary_natal_sign",
    "tn_primary_transit_sign",
    "base_tn_primary_transit_planet",
    "base_tn_primary_natal_planet",
    "base_tn_primary_aspect",
    "base_tn_primary_orb_deg",
    "base_tn_primary_bphs_strength",
    "base_tn_primary_bphs_virupa",
    "base_tn_primary_natal_sign",
    "base_tn_primary_transit_sign",
)


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aspect_cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_event_id TEXT,
    pair_key TEXT NOT NULL,
    aspect TEXT NOT NULL,
    aspect_label TEXT,
    window_start_ist TEXT NOT NULL,
    window_end_ist TEXT NOT NULL,
    timeframe TEXT,
    source_csv TEXT,
    context_json TEXT,
    created_at_utc TEXT NOT NULL,
    UNIQUE(source_event_id, pair_key, aspect, window_start_ist, window_end_ist)
);

CREATE INDEX IF NOT EXISTS idx_aspect_cases_pair_aspect
ON aspect_cases(pair_key, aspect, window_start_ist);

CREATE TABLE IF NOT EXISTS trade_annotations (
    annotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES aspect_cases(case_id) ON DELETE CASCADE,
    trade_start_ist TEXT NOT NULL,
    trade_end_ist TEXT NOT NULL,
    outcome_label TEXT NOT NULL CHECK(outcome_label IN ('bullish', 'bearish', 'sideways', 'unclear')),
    entry_price REAL,
    exit_price REAL,
    pips REAL,
    mfe_pips REAL,
    mae_pips REAL,
    why_text TEXT,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trade_annotations_case
ON trade_annotations(case_id, trade_start_ist);

CREATE TABLE IF NOT EXISTS ignore_regions (
    ignore_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES aspect_cases(case_id) ON DELETE CASCADE,
    region_start_ist TEXT NOT NULL,
    region_end_ist TEXT NOT NULL,
    why_text TEXT,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ignore_regions_case
ON ignore_regions(case_id, region_start_ist);

CREATE TABLE IF NOT EXISTS rule_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES aspect_cases(case_id) ON DELETE CASCADE,
    annotation_id INTEGER REFERENCES trade_annotations(annotation_id) ON DELETE CASCADE,
    note_type TEXT NOT NULL DEFAULT 'general',
    note_text TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rule_notes_case
ON rule_notes(case_id, created_at_utc);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.execute(
            """
            INSERT INTO schema_meta(key, value, updated_at_utc)
            VALUES('schema_version', '1', ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at_utc = excluded.updated_at_utc
            """,
            (utc_now(),),
        )


def upsert_aspect_case(conn: sqlite3.Connection, case_data: dict[str, Any]) -> int:
    now = utc_now()
    conn.execute(
        """
        INSERT OR IGNORE INTO aspect_cases(
            source_event_id,
            pair_key,
            aspect,
            aspect_label,
            window_start_ist,
            window_end_ist,
            timeframe,
            source_csv,
            context_json,
            created_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_data.get("source_event_id"),
            case_data["pair_key"],
            case_data["aspect"],
            case_data.get("aspect_label"),
            case_data["window_start_ist"],
            case_data["window_end_ist"],
            case_data.get("timeframe"),
            case_data.get("source_csv"),
            case_data.get("context_json"),
            now,
        ),
    )
    row = conn.execute(
        """
        SELECT case_id
        FROM aspect_cases
        WHERE IFNULL(source_event_id, '') = IFNULL(?, '')
          AND pair_key = ?
          AND aspect = ?
          AND window_start_ist = ?
          AND window_end_ist = ?
        """,
        (
            case_data.get("source_event_id"),
            case_data["pair_key"],
            case_data["aspect"],
            case_data["window_start_ist"],
            case_data["window_end_ist"],
        ),
    ).fetchone()
    if row is None:
        raise RuntimeError("Failed to read inserted aspect case.")
    return int(row["case_id"])


def case_exists(conn: sqlite3.Connection, case_data: dict[str, Any]) -> bool:
    row = conn.execute(
        """
        SELECT 1
        FROM aspect_cases
        WHERE IFNULL(source_event_id, '') = IFNULL(?, '')
          AND pair_key = ?
          AND aspect = ?
          AND window_start_ist = ?
          AND window_end_ist = ?
        LIMIT 1
        """,
        (
            case_data.get("source_event_id"),
            case_data["pair_key"],
            case_data["aspect"],
            case_data["window_start_ist"],
            case_data["window_end_ist"],
        ),
    ).fetchone()
    return row is not None


def row_to_context_json(row: dict[str, str]) -> str:
    context = {key: row.get(key, "") for key in CASE_CONTEXT_COLUMNS if key in row}
    return json.dumps(context, ensure_ascii=True, sort_keys=True)


def timeframe_bucket(row: dict[str, str]) -> str:
    try:
        duration = float(row.get("event_duration_minutes") or "")
    except ValueError:
        return ""
    if duration <= 24.0 * 60.0:
        return "m30_h1"
    return "daily"


def load_price_frame(path: Path) -> pd.DataFrame:
    price = pd.read_parquet(path).sort_index()
    if price.index.tz is None:
        price.index = price.index.tz_localize("UTC")
    price = price.tz_convert(IST)
    price.columns = [str(col).lower() for col in price.columns]
    required = {"open", "high", "low", "close"}
    missing = required.difference(price.columns)
    if missing:
        raise ValueError(f"Price file missing columns: {', '.join(sorted(missing))}")
    return price


def parse_ist_timestamp(value: str) -> pd.Timestamp:
    ts = pd.to_datetime(value, errors="raise")
    if ts.tzinfo is None:
        ts = ts.tz_localize(IST)
    else:
        ts = ts.tz_convert(IST)
    return pd.Timestamp(ts)


def nearest_bar(price: pd.DataFrame, ts: pd.Timestamp) -> pd.Series:
    if price.empty:
        raise ValueError("Price frame is empty.")
    pos = price.index.get_indexer([ts], method="nearest")[0]
    if pos < 0:
        raise ValueError(f"No nearest price bar found for {ts}.")
    return price.iloc[int(pos)]


def calculate_trade_prices(
    price: pd.DataFrame,
    trade_start_ist: str,
    trade_end_ist: str,
    outcome_label: str,
) -> dict[str, float]:
    start_ts = parse_ist_timestamp(trade_start_ist)
    end_ts = parse_ist_timestamp(trade_end_ist)
    if end_ts < start_ts:
        raise ValueError("trade_end must be after trade_start.")
    start_bar = nearest_bar(price, start_ts)
    end_bar = nearest_bar(price, end_ts)
    entry_price = float(start_bar["close"])
    exit_price = float(end_bar["close"])
    window = price.loc[(price.index >= start_ts) & (price.index <= end_ts)]
    if window.empty:
        window = pd.DataFrame([start_bar, end_bar])
    high = float(window["high"].max())
    low = float(window["low"].min())
    direction = 0
    if outcome_label == "bullish":
        direction = 1
    elif outcome_label == "bearish":
        direction = -1
    if direction == 1:
        pips = (exit_price - entry_price) / USDJPY_PIP_SIZE
        mfe = (high - entry_price) / USDJPY_PIP_SIZE
        mae = (low - entry_price) / USDJPY_PIP_SIZE
    elif direction == -1:
        pips = (entry_price - exit_price) / USDJPY_PIP_SIZE
        mfe = (entry_price - low) / USDJPY_PIP_SIZE
        mae = (entry_price - high) / USDJPY_PIP_SIZE
    else:
        pips = (exit_price - entry_price) / USDJPY_PIP_SIZE
        mfe = (high - entry_price) / USDJPY_PIP_SIZE
        mae = (low - entry_price) / USDJPY_PIP_SIZE
    return {
        "entry_price": round(entry_price, 5),
        "exit_price": round(exit_price, 5),
        "pips": round(float(pips), 2),
        "mfe_pips": round(float(mfe), 2),
        "mae_pips": round(float(mae), 2),
    }


def validate_trade_inside_case(case: sqlite3.Row, trade_start_ist: str, trade_end_ist: str) -> None:
    case_start = parse_ist_timestamp(str(case["window_start_ist"]))
    case_end = parse_ist_timestamp(str(case["window_end_ist"]))
    trade_start = parse_ist_timestamp(trade_start_ist)
    trade_end = parse_ist_timestamp(trade_end_ist)
    if trade_end < trade_start:
        raise ValueError("trade_end must be after trade_start.")
    if trade_start < case_start or trade_end > case_end:
        raise ValueError(
            "Trade markers must be inside the selected aspect window: "
            f"{case_start} -> {case_end}. "
            f"Received {trade_start} -> {trade_end}."
        )


def validate_region_inside_case(case: sqlite3.Row, region_start_ist: str, region_end_ist: str) -> None:
    case_start = parse_ist_timestamp(str(case["window_start_ist"]))
    case_end = parse_ist_timestamp(str(case["window_end_ist"]))
    region_start = parse_ist_timestamp(region_start_ist)
    region_end = parse_ist_timestamp(region_end_ist)
    if region_end < region_start:
        raise ValueError("region_end must be after region_start.")
    if region_start < case_start or region_end > case_end:
        raise ValueError(
            "Ignore region must be inside the selected aspect window: "
            f"{case_start} -> {case_end}. "
            f"Received {region_start} -> {region_end}."
        )


def case_data_from_touch_log_row(row: dict[str, str], source_csv: Path) -> dict[str, Any] | None:
    pair_key = str(row.get("pair_key") or "").strip()
    aspect = str(row.get("aspect") or "").strip()
    start = str(row.get("event_window_start_local") or "").strip()
    end = str(row.get("event_window_end_local") or "").strip()
    if not pair_key or not aspect or not start or not end:
        return None
    return {
        "source_event_id": str(row.get("event_id") or "").strip() or None,
        "pair_key": pair_key,
        "aspect": aspect,
        "aspect_label": str(row.get("aspect_label") or "").strip() or f"{pair_key} {aspect}",
        "window_start_ist": start,
        "window_end_ist": end,
        "timeframe": timeframe_bucket(row),
        "source_csv": str(source_csv),
        "context_json": row_to_context_json(row),
    }


def import_aspect_cases_from_csv(db_path: Path, source_csv: Path) -> tuple[int, int, int]:
    initialize_database(db_path)
    source_csv = source_csv.resolve()
    attempted = 0
    inserted = 0
    skipped = 0
    seen: set[tuple[str, str, str, str, str]] = set()
    with source_csv.open("r", encoding="utf-8-sig", newline="") as fh, connect(db_path) as conn:
        reader = csv.DictReader(fh)
        for row in reader:
            case_data = case_data_from_touch_log_row(row, source_csv)
            if case_data is None:
                skipped += 1
                continue
            key = (
                str(case_data.get("source_event_id") or ""),
                case_data["pair_key"],
                case_data["aspect"],
                case_data["window_start_ist"],
                case_data["window_end_ist"],
            )
            if key in seen:
                skipped += 1
                continue
            seen.add(key)
            attempted += 1
            existed = case_exists(conn, case_data)
            upsert_aspect_case(conn, case_data)
            if existed:
                skipped += 1
            else:
                inserted += 1
    return attempted, inserted, skipped


def list_aspects(conn: sqlite3.Connection, limit: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT pair_key, aspect, COALESCE(aspect_label, pair_key || ' ' || aspect) AS aspect_label, COUNT(*) AS case_count
        FROM aspect_cases
        GROUP BY pair_key, aspect
        ORDER BY case_count DESC, pair_key, aspect
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def list_cases(conn: sqlite3.Connection, pair_key: str, aspect: str, limit: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT case_id, source_event_id, pair_key, aspect, aspect_label, window_start_ist, window_end_ist, timeframe
        FROM aspect_cases
        WHERE pair_key = ?
          AND aspect = ?
        ORDER BY window_start_ist
        LIMIT ?
        """,
        (pair_key, aspect, limit),
    ).fetchall()


def review_aspect_cases(conn: sqlite3.Connection, pair_key: str, aspect: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            c.case_id,
            c.source_event_id,
            c.pair_key,
            c.aspect,
            c.aspect_label,
            c.window_start_ist,
            c.window_end_ist,
            c.timeframe,
            COUNT(a.annotation_id) AS annotation_count
        FROM aspect_cases c
        LEFT JOIN trade_annotations a ON a.case_id = c.case_id
        WHERE c.pair_key = ?
          AND c.aspect = ?
        GROUP BY
            c.case_id,
            c.source_event_id,
            c.pair_key,
            c.aspect,
            c.aspect_label,
            c.window_start_ist,
            c.window_end_ist,
            c.timeframe
        ORDER BY c.window_start_ist
        """,
        (pair_key, aspect),
    ).fetchall()


def review_status(rows: list[sqlite3.Row]) -> dict[str, Any]:
    total = len(rows)
    annotated = sum(1 for row in rows if int(row["annotation_count"]) > 0)
    next_unreviewed = next((row for row in rows if int(row["annotation_count"]) == 0), None)
    return {
        "total": total,
        "annotated": annotated,
        "unreviewed": total - annotated,
        "next_unreviewed": next_unreviewed,
    }


def suggested_price_timeframe(case: sqlite3.Row) -> str:
    timeframe = str(case["timeframe"] or "").lower()
    if timeframe == "daily":
        return "h1"
    return "m30"


def command_quote(value: Any) -> str:
    return '"' + str(value).replace('"', '\\"') + '"'


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def print_review_case(case: sqlite3.Row, prefix: str = "Next unreviewed") -> None:
    label = str(case["aspect_label"] or "").strip()
    if label and str(case["pair_key"]) not in label:
        label = f"{case['pair_key']} {label}"
    elif not label:
        label = f"{case['pair_key']} {case['aspect']}"
    print(f"{prefix}:")
    print(f"- case_id: {case['case_id']}")
    print(f"- event_id: {case['source_event_id']}")
    print(f"- aspect: {case['pair_key']} | {case['aspect']}")
    print(f"- label: {label}")
    print(f"- window: {case['window_start_ist']} -> {case['window_end_ist']}")
    print(f"- timeframe bucket: {case['timeframe']}")
    print(f"- existing annotations: {case['annotation_count']}")


def print_annotation_command_template(case: sqlite3.Row, price_timeframe: str) -> None:
    print("")
    print("Copy/edit this after you choose trade start/end and label:")
    print(
        "python .\\aspect_annotation_store.py --add-trade-annotation "
        f"--case-id {case['case_id']} "
        f"--trade-start {command_quote(case['window_start_ist'])} "
        f"--trade-end {command_quote(case['window_end_ist'])} "
        "--outcome-label bullish "
        f"--price-timeframe {price_timeframe} "
        "--why \"type reason here\""
    )
    print("")
    print("Change --outcome-label to one of: bullish, bearish, sideways, unclear.")


def annotation_command_template(case: sqlite3.Row, price_timeframe: str) -> str:
    return (
        "python .\\aspect_annotation_store.py --add-trade-annotation "
        f"--case-id {case['case_id']} "
        f"--trade-start {command_quote(case['window_start_ist'])} "
        f"--trade-end {command_quote(case['window_end_ist'])} "
        "--outcome-label bullish "
        f"--price-timeframe {price_timeframe} "
        "--why \"type reason here\""
    )


def ignore_region_command_template(case: sqlite3.Row) -> str:
    return (
        "python .\\aspect_annotation_store.py --mark-ignore-region "
        f"--case-id {case['case_id']} "
        f"--region-start {command_quote(case['window_start_ist'])} "
        f"--region-end {command_quote(case['window_end_ist'])} "
        "--why \"type reason here\""
    )


def rule_note_command_template(case: sqlite3.Row) -> str:
    return (
        "python .\\aspect_annotation_store.py --add-rule-note "
        f"--case-id {case['case_id']} "
        "--note-type general "
        "--note \"type note here\""
    )


def default_review_export_path(case_id: int) -> Path:
    return DEFAULT_REVIEW_EXPORT_DIR / f"aspect_review_case_{case_id}.json"


def get_aspect_case(conn: sqlite3.Connection, case_id: int) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT case_id, source_event_id, pair_key, aspect, aspect_label, window_start_ist, window_end_ist, timeframe
        FROM aspect_cases
        WHERE case_id = ?
        """,
        (case_id,),
    ).fetchone()


def add_trade_annotation(
    conn: sqlite3.Connection,
    case_id: int,
    trade_start_ist: str,
    trade_end_ist: str,
    outcome_label: str,
    why_text: str = "",
    entry_price: float | None = None,
    exit_price: float | None = None,
    pips: float | None = None,
    mfe_pips: float | None = None,
    mae_pips: float | None = None,
) -> int:
    outcome_label = outcome_label.strip().lower()
    if outcome_label not in VALID_OUTCOME_LABELS:
        raise ValueError(f"outcome_label must be one of: {', '.join(VALID_OUTCOME_LABELS)}")
    now = utc_now()
    cur = conn.execute(
        """
        INSERT INTO trade_annotations(
            case_id,
            trade_start_ist,
            trade_end_ist,
            outcome_label,
            entry_price,
            exit_price,
            pips,
            mfe_pips,
            mae_pips,
            why_text,
            created_at_utc,
            updated_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_id,
            trade_start_ist,
            trade_end_ist,
            outcome_label,
            entry_price,
            exit_price,
            pips,
            mfe_pips,
            mae_pips,
            why_text,
            now,
            now,
        ),
    )
    return int(cur.lastrowid)


def list_trade_annotations(conn: sqlite3.Connection, case_id: int | None, limit: int) -> list[sqlite3.Row]:
    if case_id is None:
        return conn.execute(
            """
            SELECT
                a.annotation_id,
                a.case_id,
                c.pair_key,
                c.aspect,
                c.aspect_label,
                a.trade_start_ist,
                a.trade_end_ist,
                a.outcome_label,
                a.entry_price,
                a.exit_price,
                a.pips,
                a.why_text,
                a.created_at_utc
            FROM trade_annotations a
            JOIN aspect_cases c ON c.case_id = a.case_id
            ORDER BY a.created_at_utc DESC, a.annotation_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return conn.execute(
        """
        SELECT
            a.annotation_id,
            a.case_id,
            c.pair_key,
            c.aspect,
            c.aspect_label,
            a.trade_start_ist,
            a.trade_end_ist,
            a.outcome_label,
            a.entry_price,
            a.exit_price,
            a.pips,
            a.why_text,
            a.created_at_utc
        FROM trade_annotations a
        JOIN aspect_cases c ON c.case_id = a.case_id
        WHERE a.case_id = ?
        ORDER BY a.trade_start_ist, a.annotation_id
        LIMIT ?
        """,
        (case_id, limit),
    ).fetchall()


def print_annotation(row: sqlite3.Row) -> None:
    prices = []
    if row["entry_price"] is not None:
        prices.append(f"entry={row['entry_price']}")
    if row["exit_price"] is not None:
        prices.append(f"exit={row['exit_price']}")
    if row["pips"] is not None:
        prices.append(f"pips={row['pips']}")
    price_text = " ".join(prices) if prices else "prices=n/a"
    why = str(row["why_text"] or "").strip()
    if len(why) > 120:
        why = why[:117] + "..."
    print(
        f"- annotation_id={row['annotation_id']} case_id={row['case_id']} "
        f"{row['pair_key']} | {row['aspect']} | {row['outcome_label']} | "
        f"{row['trade_start_ist']} -> {row['trade_end_ist']} | {price_text}"
    )
    if why:
        print(f"  why: {why}")


def list_ignore_regions(conn: sqlite3.Connection, case_id: int | None, limit: int) -> list[sqlite3.Row]:
    if case_id is None:
        return conn.execute(
            """
            SELECT
                i.ignore_id,
                i.case_id,
                c.pair_key,
                c.aspect,
                i.region_start_ist,
                i.region_end_ist,
                i.why_text,
                i.created_at_utc
            FROM ignore_regions i
            JOIN aspect_cases c ON c.case_id = i.case_id
            ORDER BY i.created_at_utc DESC, i.ignore_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return conn.execute(
        """
        SELECT
            i.ignore_id,
            i.case_id,
            c.pair_key,
            c.aspect,
            i.region_start_ist,
            i.region_end_ist,
            i.why_text,
            i.created_at_utc
        FROM ignore_regions i
        JOIN aspect_cases c ON c.case_id = i.case_id
        WHERE i.case_id = ?
        ORDER BY i.region_start_ist, i.ignore_id
        LIMIT ?
        """,
        (case_id, limit),
    ).fetchall()


def print_ignore_region(row: sqlite3.Row) -> None:
    why = str(row["why_text"] or "").strip()
    if len(why) > 120:
        why = why[:117] + "..."
    print(
        f"- ignore_id={row['ignore_id']} case_id={row['case_id']} "
        f"{row['pair_key']} | {row['aspect']} | "
        f"{row['region_start_ist']} -> {row['region_end_ist']}"
    )
    if why:
        print(f"  why: {why}")


def add_ignore_region(
    conn: sqlite3.Connection,
    case_id: int,
    region_start_ist: str,
    region_end_ist: str,
    why_text: str,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO ignore_regions(case_id, region_start_ist, region_end_ist, why_text, created_at_utc)
        VALUES (?, ?, ?, ?, ?)
        """,
        (case_id, region_start_ist, region_end_ist, why_text, utc_now()),
    )
    return int(cur.lastrowid)


def add_rule_note(
    conn: sqlite3.Connection,
    case_id: int,
    note_text: str,
    note_type: str = "general",
    annotation_id: int | None = None,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO rule_notes(case_id, annotation_id, note_type, note_text, created_at_utc)
        VALUES (?, ?, ?, ?, ?)
        """,
        (case_id, annotation_id, note_type, note_text, utc_now()),
    )
    return int(cur.lastrowid)


def list_rule_notes(conn: sqlite3.Connection, case_id: int | None, limit: int) -> list[sqlite3.Row]:
    if case_id is None:
        return conn.execute(
            """
            SELECT
                n.note_id,
                n.case_id,
                n.annotation_id,
                c.pair_key,
                c.aspect,
                n.note_type,
                n.note_text,
                n.created_at_utc
            FROM rule_notes n
            JOIN aspect_cases c ON c.case_id = n.case_id
            ORDER BY n.created_at_utc DESC, n.note_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return conn.execute(
        """
        SELECT
            n.note_id,
            n.case_id,
            n.annotation_id,
            c.pair_key,
            c.aspect,
            n.note_type,
            n.note_text,
            n.created_at_utc
        FROM rule_notes n
        JOIN aspect_cases c ON c.case_id = n.case_id
        WHERE n.case_id = ?
        ORDER BY n.created_at_utc, n.note_id
        LIMIT ?
        """,
        (case_id, limit),
    ).fetchall()


def print_rule_note(row: sqlite3.Row) -> None:
    note = str(row["note_text"] or "").strip()
    if len(note) > 140:
        note = note[:137] + "..."
    annotation_part = f" annotation_id={row['annotation_id']}" if row["annotation_id"] is not None else ""
    print(
        f"- note_id={row['note_id']} case_id={row['case_id']}{annotation_part} "
        f"{row['pair_key']} | {row['aspect']} | type={row['note_type']}"
    )
    print(f"  note: {note}")


def export_review_case_snapshot(db_path: Path, case_id: int, output_path: Path | None = None) -> Path:
    initialize_database(db_path)
    with connect(db_path) as conn:
        case = get_aspect_case(conn, case_id)
        if case is None:
            raise ValueError(f"No aspect case found for case_id={case_id}.")
        same_aspect_rows = review_aspect_cases(conn, str(case["pair_key"]), str(case["aspect"]))
        status = review_status(same_aspect_rows)
        trade_rows = list_trade_annotations(conn, case_id, limit=1000)
        ignore_rows = list_ignore_regions(conn, case_id, limit=1000)
        note_rows = list_rule_notes(conn, case_id, limit=1000)

    same_aspect_cases = [row_to_dict(row) for row in same_aspect_rows]
    case_index = next(
        (idx for idx, row in enumerate(same_aspect_cases, start=1) if int(row["case_id"]) == int(case_id)),
        None,
    )
    price_timeframe = suggested_price_timeframe(case)
    payload = {
        "exported_at_utc": utc_now(),
        "case": row_to_dict(case),
        "same_aspect": {
            "pair_key": case["pair_key"],
            "aspect": case["aspect"],
            "case_index": case_index,
            "total_cases": status["total"],
            "annotated_cases": status["annotated"],
            "unreviewed_cases": status["unreviewed"],
            "cases": same_aspect_cases,
        },
        "saved": {
            "trade_annotations": [row_to_dict(row) for row in trade_rows],
            "ignore_regions": [row_to_dict(row) for row in ignore_rows],
            "rule_notes": [row_to_dict(row) for row in note_rows],
        },
        "suggestions": {
            "price_timeframe": price_timeframe,
            "outcome_labels": list(VALID_OUTCOME_LABELS),
            "add_trade_annotation_command": annotation_command_template(case, price_timeframe),
            "mark_ignore_region_command": ignore_region_command_template(case),
            "add_rule_note_command": rule_note_command_template(case),
        },
    }
    output_path = output_path or default_review_export_path(case_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return output_path


def run_smoke_test(db_path: Path) -> None:
    initialize_database(db_path)
    with connect(db_path) as conn:
        case_id = upsert_aspect_case(
            conn,
            {
                "source_event_id": "SMOKE_TEST_EVENT",
                "pair_key": "MARS|JUPITER",
                "aspect": "opposition",
                "aspect_label": "MARS|JUPITER opposition",
                "window_start_ist": "2026-01-01T09:00:00+05:30",
                "window_end_ist": "2026-01-01T18:00:00+05:30",
                "timeframe": "m30",
                "source_csv": "smoke_test.csv",
            },
        )
        annotation_id = add_trade_annotation(
            conn,
            case_id=case_id,
            trade_start_ist="2026-01-01T10:00:00+05:30",
            trade_end_ist="2026-01-01T12:30:00+05:30",
            outcome_label="bullish",
            entry_price=145.10,
            exit_price=145.42,
            pips=32.0,
            mfe_pips=40.0,
            mae_pips=-8.0,
            why_text="Smoke test: sample bullish annotation.",
        )
        ignore_id = add_ignore_region(
            conn,
            case_id=case_id,
            region_start_ist="2026-01-01T09:30:00+05:30",
            region_end_ist="2026-01-01T10:00:00+05:30",
            why_text="Smoke test: ignore first SR line because it is too close.",
        )
        note_id = add_rule_note(
            conn,
            case_id=case_id,
            annotation_id=annotation_id,
            note_type="sr_ignore_reason",
            note_text="Smoke test rule note.",
        )
        row = conn.execute(
            """
            SELECT c.pair_key, c.aspect, a.outcome_label, a.pips
            FROM aspect_cases c
            JOIN trade_annotations a ON a.case_id = c.case_id
            WHERE a.annotation_id = ?
            """,
            (annotation_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError("Smoke test failed to read sample annotation.")
        conn.execute("DELETE FROM rule_notes WHERE note_id = ?", (note_id,))
        conn.execute("DELETE FROM ignore_regions WHERE ignore_id = ?", (ignore_id,))
        conn.execute("DELETE FROM trade_annotations WHERE annotation_id = ?", (annotation_id,))
        conn.execute("DELETE FROM aspect_cases WHERE case_id = ?", (case_id,))
        print(
            "Smoke test passed: "
            f"{row['pair_key']} {row['aspect']} -> {row['outcome_label']} ({row['pips']} pips)"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize and test the Gann aspect annotation SQLite store.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite database path.")
    parser.add_argument("--init-db", action="store_true", help="Create or update the annotation database schema.")
    parser.add_argument("--smoke-test", action="store_true", help="Insert/read/delete one sample annotation.")
    parser.add_argument(
        "--import-cases-from-csv",
        type=Path,
        help="Import aspect cases from a touch-log CSV. Defaults are kept in the local SQLite DB.",
    )
    parser.add_argument("--list-aspects", action="store_true", help="Show imported pair_key + aspect groups.")
    parser.add_argument("--list-cases", action="store_true", help="Show imported cases for --pair-key and --aspect.")
    parser.add_argument("--review-aspect", action="store_true", help="Show review progress and next unreviewed case.")
    parser.add_argument("--add-trade-annotation", action="store_true", help="Save one manual trade annotation.")
    parser.add_argument("--list-annotations", action="store_true", help="Show saved trade annotations.")
    parser.add_argument("--mark-ignore-region", action="store_true", help="Save an ignored time region inside a case.")
    parser.add_argument("--list-ignore-regions", action="store_true", help="Show saved ignored time regions.")
    parser.add_argument("--add-rule-note", action="store_true", help="Save a free-form rule note for a case.")
    parser.add_argument("--list-rule-notes", action="store_true", help="Show saved rule notes.")
    parser.add_argument("--export-review-case", action="store_true", help="Write one case review snapshot JSON.")
    parser.add_argument("--case-id", type=int, help="Aspect case id for annotation commands.")
    parser.add_argument("--annotation-id", type=int, help="Optional trade annotation id for a rule note.")
    parser.add_argument("--trade-start", help="Trade start timestamp in IST, copied from the chart/candle.")
    parser.add_argument("--trade-end", help="Trade end timestamp in IST, copied from the chart/candle.")
    parser.add_argument("--region-start", help="Ignored region start timestamp in IST.")
    parser.add_argument("--region-end", help="Ignored region end timestamp in IST.")
    parser.add_argument("--outcome-label", choices=VALID_OUTCOME_LABELS, help="bullish, bearish, sideways, or unclear.")
    parser.add_argument("--entry-price", type=float, help="Optional manual entry price.")
    parser.add_argument("--exit-price", type=float, help="Optional manual exit price.")
    parser.add_argument("--pips", type=float, help="Optional manual pips result.")
    parser.add_argument("--mfe-pips", type=float, help="Optional maximum favorable excursion in pips.")
    parser.add_argument("--mae-pips", type=float, help="Optional maximum adverse excursion in pips.")
    parser.add_argument(
        "--price-timeframe",
        choices=tuple(DEFAULT_PRICE_PATHS),
        help="Use a default price file to auto-calculate entry/exit/pips, currently m30 or h1.",
    )
    parser.add_argument("--price-file", type=Path, help="Optional custom price parquet for auto-calculation.")
    parser.add_argument("--why", default="", help="Free-form reason/rule note for the annotation.")
    parser.add_argument("--note-type", default="general", help="Rule note type, for example sr_ignore_reason.")
    parser.add_argument("--note", default="", help="Free-form note text for --add-rule-note.")
    parser.add_argument("--output-json", type=Path, help="Output path for --export-review-case.")
    parser.add_argument("--pair-key", help="Pair key for --list-cases, for example MARS|JUPITER.")
    parser.add_argument("--aspect", help="Aspect for --list-cases, for example opposition.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum rows to show for list commands.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not any(
        (
            args.init_db,
            args.smoke_test,
            args.import_cases_from_csv,
            args.list_aspects,
            args.list_cases,
            args.review_aspect,
            args.add_trade_annotation,
            args.list_annotations,
            args.mark_ignore_region,
            args.list_ignore_regions,
            args.add_rule_note,
            args.list_rule_notes,
            args.export_review_case,
        )
    ):
        raise SystemExit(
            "Use --init-db, --smoke-test, --import-cases-from-csv, --list-aspects, --list-cases, --review-aspect, "
            "--add-trade-annotation, --list-annotations, --mark-ignore-region, --list-ignore-regions, "
            "--add-rule-note, --list-rule-notes, or --export-review-case."
        )
    if args.init_db:
        initialize_database(args.db)
        print(f"Initialized annotation database: {args.db}")
    if args.import_cases_from_csv:
        attempted, inserted, skipped = import_aspect_cases_from_csv(args.db, args.import_cases_from_csv)
        print(f"Imported aspect cases from: {args.import_cases_from_csv}")
        print(f"Attempted unique cases: {attempted}")
        print(f"Inserted new cases: {inserted}")
        print(f"Skipped existing/invalid/duplicate rows: {skipped}")
    if args.smoke_test:
        run_smoke_test(args.db)
    if args.add_trade_annotation:
        missing = [
            name
            for name, value in (
                ("--case-id", args.case_id),
                ("--trade-start", args.trade_start),
                ("--trade-end", args.trade_end),
                ("--outcome-label", args.outcome_label),
            )
            if value in (None, "")
        ]
        if missing:
            raise SystemExit("--add-trade-annotation requires " + ", ".join(missing))
        initialize_database(args.db)
        with connect(args.db) as conn:
            case = get_aspect_case(conn, int(args.case_id))
            if case is None:
                raise SystemExit(f"No aspect case found for case_id={args.case_id}.")
            try:
                validate_trade_inside_case(case, str(args.trade_start), str(args.trade_end))
            except ValueError as exc:
                raise SystemExit(str(exc)) from exc
            entry_price = args.entry_price
            exit_price = args.exit_price
            pips = args.pips
            mfe_pips = args.mfe_pips
            mae_pips = args.mae_pips
            auto_prices = None
            if args.price_timeframe or args.price_file:
                price_path = args.price_file or DEFAULT_PRICE_PATHS[str(args.price_timeframe)]
                try:
                    price = load_price_frame(price_path)
                    auto_prices = calculate_trade_prices(
                        price,
                        trade_start_ist=str(args.trade_start),
                        trade_end_ist=str(args.trade_end),
                        outcome_label=str(args.outcome_label),
                    )
                except (ValueError, FileNotFoundError) as exc:
                    raise SystemExit(str(exc)) from exc
                entry_price = entry_price if entry_price is not None else auto_prices["entry_price"]
                exit_price = exit_price if exit_price is not None else auto_prices["exit_price"]
                pips = pips if pips is not None else auto_prices["pips"]
                mfe_pips = mfe_pips if mfe_pips is not None else auto_prices["mfe_pips"]
                mae_pips = mae_pips if mae_pips is not None else auto_prices["mae_pips"]
            annotation_id = add_trade_annotation(
                conn,
                case_id=int(args.case_id),
                trade_start_ist=str(args.trade_start),
                trade_end_ist=str(args.trade_end),
                outcome_label=str(args.outcome_label),
                why_text=str(args.why or ""),
                entry_price=entry_price,
                exit_price=exit_price,
                pips=pips,
                mfe_pips=mfe_pips,
                mae_pips=mae_pips,
            )
        print(f"Saved annotation_id={annotation_id} for case_id={args.case_id}.")
        print(
            f"Case: {case['pair_key']} | {case['aspect']} | "
            f"{case['window_start_ist']} -> {case['window_end_ist']}"
        )
        if auto_prices is not None:
            print(
                "Auto-calculated from price file: "
                f"entry={entry_price} exit={exit_price} pips={pips} "
                f"mfe={mfe_pips} mae={mae_pips}"
            )
    if args.mark_ignore_region:
        missing = [
            name
            for name, value in (
                ("--case-id", args.case_id),
                ("--region-start", args.region_start),
                ("--region-end", args.region_end),
                ("--why", args.why),
            )
            if value in (None, "")
        ]
        if missing:
            raise SystemExit("--mark-ignore-region requires " + ", ".join(missing))
        initialize_database(args.db)
        with connect(args.db) as conn:
            case = get_aspect_case(conn, int(args.case_id))
            if case is None:
                raise SystemExit(f"No aspect case found for case_id={args.case_id}.")
            try:
                validate_region_inside_case(case, str(args.region_start), str(args.region_end))
            except ValueError as exc:
                raise SystemExit(str(exc)) from exc
            ignore_id = add_ignore_region(
                conn,
                case_id=int(args.case_id),
                region_start_ist=str(args.region_start),
                region_end_ist=str(args.region_end),
                why_text=str(args.why),
            )
        print(f"Saved ignore_id={ignore_id} for case_id={args.case_id}.")
        print(
            f"Case: {case['pair_key']} | {case['aspect']} | "
            f"{case['window_start_ist']} -> {case['window_end_ist']}"
        )
    if args.add_rule_note:
        missing = [
            name
            for name, value in (
                ("--case-id", args.case_id),
                ("--note", args.note),
            )
            if value in (None, "")
        ]
        if missing:
            raise SystemExit("--add-rule-note requires " + ", ".join(missing))
        initialize_database(args.db)
        with connect(args.db) as conn:
            case = get_aspect_case(conn, int(args.case_id))
            if case is None:
                raise SystemExit(f"No aspect case found for case_id={args.case_id}.")
            if args.annotation_id is not None:
                annotation = conn.execute(
                    """
                    SELECT 1
                    FROM trade_annotations
                    WHERE annotation_id = ?
                      AND case_id = ?
                    """,
                    (int(args.annotation_id), int(args.case_id)),
                ).fetchone()
                if annotation is None:
                    raise SystemExit(
                        f"No annotation_id={args.annotation_id} found for case_id={args.case_id}."
                    )
            note_id = add_rule_note(
                conn,
                case_id=int(args.case_id),
                annotation_id=args.annotation_id,
                note_type=str(args.note_type or "general"),
                note_text=str(args.note),
            )
        print(f"Saved note_id={note_id} for case_id={args.case_id}.")
    if args.list_aspects:
        initialize_database(args.db)
        with connect(args.db) as conn:
            rows = list_aspects(conn, max(1, args.limit))
        if not rows:
            print("No aspect cases imported yet.")
        else:
            print("Imported aspect groups:")
            for row in rows:
                print(f"- {row['pair_key']} | {row['aspect']} | cases={row['case_count']}")
    if args.list_cases:
        if not args.pair_key or not args.aspect:
            raise SystemExit("--list-cases requires --pair-key and --aspect.")
        initialize_database(args.db)
        with connect(args.db) as conn:
            rows = list_cases(conn, args.pair_key, args.aspect, max(1, args.limit))
        if not rows:
            print(f"No cases found for pair_key={args.pair_key} aspect={args.aspect}.")
        else:
            print(f"Cases for {args.pair_key} | {args.aspect}:")
            for row in rows:
                print(
                    f"- case_id={row['case_id']} event_id={row['source_event_id']} "
                    f"{row['window_start_ist']} -> {row['window_end_ist']} timeframe={row['timeframe']}"
                )
    if args.review_aspect:
        if not args.pair_key or not args.aspect:
            raise SystemExit("--review-aspect requires --pair-key and --aspect.")
        initialize_database(args.db)
        with connect(args.db) as conn:
            rows = review_aspect_cases(conn, args.pair_key, args.aspect)
        if not rows:
            print(f"No cases found for pair_key={args.pair_key} aspect={args.aspect}.")
        else:
            status = review_status(rows)
            print(f"Review queue: {args.pair_key} | {args.aspect}")
            print(f"Total cases: {status['total']}")
            print(f"Annotated cases: {status['annotated']}")
            print(f"Unreviewed cases: {status['unreviewed']}")
            print("")
            next_case = status["next_unreviewed"]
            if next_case is None:
                print("All cases currently have at least one annotation.")
                print_review_case(rows[-1], prefix="Last case")
            else:
                print_review_case(next_case)
                print_annotation_command_template(next_case, suggested_price_timeframe(next_case))
    if args.list_annotations:
        initialize_database(args.db)
        with connect(args.db) as conn:
            rows = list_trade_annotations(conn, args.case_id, max(1, args.limit))
        if not rows:
            if args.case_id is None:
                print("No trade annotations saved yet.")
            else:
                print(f"No trade annotations saved for case_id={args.case_id}.")
        else:
            print("Saved trade annotations:")
            for row in rows:
                print_annotation(row)
    if args.list_ignore_regions:
        initialize_database(args.db)
        with connect(args.db) as conn:
            rows = list_ignore_regions(conn, args.case_id, max(1, args.limit))
        if not rows:
            if args.case_id is None:
                print("No ignore regions saved yet.")
            else:
                print(f"No ignore regions saved for case_id={args.case_id}.")
        else:
            print("Saved ignore regions:")
            for row in rows:
                print_ignore_region(row)
    if args.list_rule_notes:
        initialize_database(args.db)
        with connect(args.db) as conn:
            rows = list_rule_notes(conn, args.case_id, max(1, args.limit))
        if not rows:
            if args.case_id is None:
                print("No rule notes saved yet.")
            else:
                print(f"No rule notes saved for case_id={args.case_id}.")
        else:
            print("Saved rule notes:")
            for row in rows:
                print_rule_note(row)
    if args.export_review_case:
        if args.case_id is None:
            raise SystemExit("--export-review-case requires --case-id.")
        try:
            output_path = export_review_case_snapshot(args.db, int(args.case_id), args.output_json)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(f"Exported review snapshot: {output_path}")


if __name__ == "__main__":
    main()
