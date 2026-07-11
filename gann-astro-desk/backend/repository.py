from __future__ import annotations

import base64
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import numpy as np
import pandas as pd


IST = "Asia/Kolkata"
UTC = "UTC"
ASTRO_CONTRACT = "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2"
ASPECT_COLORS = {
    "conjunction_orb": "#f28c68",
    "square": "#e0ad45",
    "trine": "#36b8a0",
    "opposition_orb": "#dc6f91",
}
IMPORTANT_ASTRO_FIELDS = (
    ("event_strict_shadbala_implemented_total_virupa_avg", "Planet strength", "virupa"),
    ("event_strict_shadbala_implemented_total_ratio_avg", "Strength versus minimum", "ratio"),
    ("event_strict_drik_bala_virupa_avg", "Aspect pressure", "virupa"),
    ("event_strict_drik_benefic_virupa_avg", "Supportive pressure", "virupa"),
    ("event_strict_drik_malefic_virupa_avg", "Stress pressure", "virupa"),
    ("event_strict_chesta_bala_virupa_avg", "Motion strength", "virupa"),
    ("event_orb_deg", "Distance from exact aspect", "degrees"),
    ("event_b1_sign", "Transit sign", "text"),
    ("event_b1_sign_relation", "Transit sign relationship", "text"),
    ("event_b1_sthana_dignity_label", "Transit dignity", "text"),
    ("event_b2_sign", "Natal sign", "text"),
    ("event_b2_sign_relation", "Natal sign relationship", "text"),
    ("event_b2_sthana_dignity_label", "Natal dignity", "text"),
    ("event_tithi_name", "Tithi", "text"),
    ("event_moon_nakshatra", "Moon nakshatra", "text"),
    ("event_yoga_name", "Yoga", "text"),
    ("event_karana_name", "Karana", "text"),
    ("aspect_regime_active_count", "Overlapping aspect count", "count"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def epoch_seconds(value: Any) -> int:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(IST)
    return int(timestamp.tz_convert(UTC).timestamp())


def parse_local_timestamp(value: str | None, fallback: str) -> pd.Timestamp:
    timestamp = pd.Timestamp(value or fallback)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(IST)
    return timestamp.tz_convert(IST)


@dataclass(frozen=True)
class DataPaths:
    project_root: Path
    source_events: Path
    touch_log: Path
    price_data: Path
    annotation_db: Path
    snapshots_dir: Path

    @classmethod
    def default(cls) -> "DataPaths":
        root = Path(__file__).resolve().parents[2]
        return cls(
            project_root=root,
            source_events=root / "astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet",
            touch_log=root / "aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv",
            price_data=root / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
            annotation_db=root / "gann_aspect_annotations_raman_v2.sqlite",
            snapshots_dir=Path(r"D:\GannFinancialAstro\app_snapshots"),
        )


class AstroRepository:
    def __init__(self, paths: DataPaths | None = None) -> None:
        self.paths = paths or DataPaths.default()
        self.events = pd.read_parquet(self.paths.source_events).copy()
        self.events["timestamp"] = pd.to_datetime(self.events["timestamp"])
        self.events["event_end"] = pd.to_datetime(self.events["event_end"])
        self.events["peak_time"] = pd.to_datetime(self.events["peak_time"])
        self.events = self.events.sort_values(["timestamp", "event_family_key", "event_id"]).reset_index(drop=True)
        touch_columns = [
            "event_id",
            "touch_id",
            "touch_time_local",
            "touch_line_price_1",
            "touch_line_price_2",
            "touch_planet_1",
            "touch_planet_2",
        ]
        self.touches = pd.read_csv(self.paths.touch_log, usecols=touch_columns)
        self.touches["touch_time_local"] = pd.to_datetime(self.touches["touch_time_local"])
        self.touch_by_event = {
            str(row["event_id"]): row
            for _, row in self.touches.iterrows()
        }
        self.price = pd.read_parquet(self.paths.price_data).copy().sort_index()
        if self.price.index.tz is None:
            self.price.index = self.price.index.tz_localize(UTC)
        else:
            self.price.index = self.price.index.tz_convert(UTC)
        self._initialize_annotations()
        self._reload_case_maps()
        self.family_counts = self.events.groupby("event_family_key")["event_id"].count().astype(int).to_dict()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.paths.annotation_db, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize_annotations(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS chart_annotations (
                    annotation_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    case_id INTEGER,
                    family_key TEXT NOT NULL,
                    annotation_type TEXT NOT NULL,
                    anchor_time_utc TEXT NOT NULL,
                    anchor_price REAL,
                    end_time_utc TEXT,
                    end_price REAL,
                    target_type TEXT NOT NULL DEFAULT 'chart_point',
                    target_id TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    color TEXT NOT NULL DEFAULT '#4bb7e5',
                    chart_state_json TEXT NOT NULL DEFAULT '{}',
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_chart_annotations_event
                    ON chart_annotations(event_id, updated_at_utc);
                CREATE INDEX IF NOT EXISTS idx_chart_annotations_family
                    ON chart_annotations(family_key, updated_at_utc);
                CREATE TABLE IF NOT EXISTS app_codex_threads (
                    scope_key TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS app_occurrence_progress (
                    event_id TEXT PRIMARY KEY,
                    case_id INTEGER,
                    family_key TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending', 'reviewed')),
                    updated_at_utc TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_app_occurrence_progress_family
                    ON app_occurrence_progress(family_key, status, updated_at_utc);
                """
            )
            connection.execute(
                """
                INSERT INTO schema_meta(key, value, updated_at_utc)
                VALUES('chart_annotation_schema_version', '2', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at_utc=excluded.updated_at_utc
                WHERE schema_meta.value <> excluded.value
                """,
                (utc_now(),),
            )
            connection.commit()

    def _reload_case_maps(self) -> None:
        with self.connect() as connection:
            cases = [dict(row) for row in connection.execute("SELECT * FROM aspect_cases ORDER BY case_id")]
            reviews = {
                int(row["case_id"]): dict(row)
                for row in connection.execute(
                    "SELECT * FROM completed_reviews ORDER BY updated_at_utc, review_id"
                )
            }
            progress = {
                str(row["event_id"]): dict(row)
                for row in connection.execute(
                    "SELECT * FROM app_occurrence_progress ORDER BY updated_at_utc, event_id"
                )
            }
        self.case_by_event = {str(row["source_event_id"]): row for row in cases}
        self.case_by_id = {int(row["case_id"]): row for row in cases}
        self.review_by_case = reviews
        self.progress_by_event = progress

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "astronomyContract": ASTRO_CONTRACT,
            "eventRows": int(len(self.events)),
            "familyCount": int(len(self.family_counts)),
            "caseCount": int(len(self.case_by_id)),
            "touchCount": int(len(self.touches)),
            "priceStart": self.price.index.min().isoformat(),
            "priceEnd": self.price.index.max().isoformat(),
            "annotationDb": str(self.paths.annotation_db),
        }

    def _case_context(self, case: dict[str, Any] | None) -> dict[str, Any]:
        if not case:
            return {}
        try:
            parsed = json.loads(str(case.get("context_json") or "{}"))
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _event_record(self, row: pd.Series, occurrence_index: int | None = None) -> dict[str, Any]:
        event_id = str(row["event_id"])
        case = self.case_by_event.get(event_id)
        context = self._case_context(case)
        case_id = int(case["case_id"]) if case else None
        review = self.review_by_case.get(case_id) if case_id is not None else None
        progress = self.progress_by_event.get(event_id)
        reviewed = bool(review) or bool(progress and progress.get("status") == "reviewed")
        outcome = str(context.get("ret_after_72h_dir") or "").upper() or None
        return {
            "eventId": event_id,
            "caseId": case_id,
            "familyKey": str(row["event_family_key"]),
            "pairKey": str(row["pair_key"]),
            "aspect": str(row["aspect"]),
            "aspectLabel": str(row.get("aspect", "")).replace("_orb", "").replace("_", " ").title(),
            "transitBody": str(row["event_transit_body"]),
            "natalBody": str(row["event_natal_body"]),
            "start": epoch_seconds(row["timestamp"]),
            "end": epoch_seconds(row["event_end"]),
            "peak": epoch_seconds(row["peak_time"]),
            "startIso": pd.Timestamp(row["timestamp"]).isoformat(),
            "endIso": pd.Timestamp(row["event_end"]).isoformat(),
            "peakIso": pd.Timestamp(row["peak_time"]).isoformat(),
            "durationMinutes": round(float(row["duration_minutes"]), 2),
            "peakOrbDeg": round(float(row["event_peak_orb_deg"]), 4),
            "orbLimitDeg": round(float(row["event_orb_limit_deg"]), 4),
            "color": ASPECT_COLORS.get(str(row["aspect"]), "#7894ad"),
            "occurrenceIndex": occurrence_index,
            "occurrenceCount": int(self.family_counts.get(str(row["event_family_key"]), 1)),
            "outcome": outcome,
            "returnPct": json_value(pd.to_numeric(context.get("ret_after_72h_pct"), errors="coerce")),
            "reviewed": reviewed,
            "reviewStatus": review.get("review_status") if review else (progress.get("status") if progress else "pending"),
            "reviewSource": "legacy_completed_review" if review else ("app_progress" if progress else "none"),
            "signedPips": json_value(review.get("signed_pips")) if review else None,
            "astronomyContract": str(row["astronomy_contract_version"]),
            "sourceGenerator": str(row["source_event_generator"]),
        }

    def _assign_lanes(self, events: list[dict[str, Any]], lane_count: int = 7) -> None:
        lane_ends = [0] * lane_count
        for event in sorted(events, key=lambda item: (item["start"], item["end"])):
            lane = next((idx for idx, end in enumerate(lane_ends) if event["start"] > end), None)
            if lane is None:
                lane = min(range(lane_count), key=lambda idx: lane_ends[idx])
            event["lane"] = lane
            lane_ends[lane] = max(lane_ends[lane], int(event["end"]))

    def chart_payload(
        self,
        start: str | None = None,
        end: str | None = None,
        symbol: str = "USDJPY",
        timeframe: str = "H1",
    ) -> dict[str, Any]:
        start_local = parse_local_timestamp(start, "2025-05-25T00:00:00+05:30")
        end_local = parse_local_timestamp(end, "2025-05-31T23:59:59+05:30")
        if end_local <= start_local:
            raise ValueError("end must be later than start")
        start_utc = start_local.tz_convert(UTC)
        end_utc = end_local.tz_convert(UTC)
        price = self.price.loc[(self.price.index >= start_utc) & (self.price.index <= end_utc)]
        candles = [
            {
                "time": int(index.timestamp()),
                "open": round(float(row.open), 5),
                "high": round(float(row.high), 5),
                "low": round(float(row.low), 5),
                "close": round(float(row.close), 5),
                "volume": int(row.tick_volume) if "tick_volume" in row else 0,
            }
            for index, row in price.iterrows()
        ]
        overlapping = self.events.loc[
            (self.events["timestamp"] <= end_local) & (self.events["event_end"] >= start_local)
        ]
        event_records = [self._event_record(row) for _, row in overlapping.iterrows()]
        self._assign_lanes(event_records)
        sr_lines: list[dict[str, Any]] = []
        seen_prices: set[tuple[str, float]] = set()
        for event in event_records:
            touch = self.touch_by_event.get(event["eventId"])
            if touch is None:
                continue
            for index in (1, 2):
                price_value = pd.to_numeric(touch.get(f"touch_line_price_{index}"), errors="coerce")
                planet_value = touch.get(f"touch_planet_{index}")
                planet = "SR" if pd.isna(planet_value) else str(planet_value)
                if pd.isna(price_value):
                    continue
                key = (planet, round(float(price_value), 4))
                if key in seen_prices:
                    continue
                seen_prices.add(key)
                sr_lines.append(
                    {
                        "id": f"{event['eventId']}:sr:{index}",
                        "price": round(float(price_value), 5),
                        "label": f"{planet} SR",
                        "planet": planet,
                        "color": "#54c4d8" if index == 1 else "#c687d8",
                        "eventId": event["eventId"],
                        "touchTime": epoch_seconds(touch["touch_time_local"]),
                    }
                )
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "start": start_local.isoformat(),
            "end": end_local.isoformat(),
            "candles": candles,
            "aspects": event_records,
            "srLines": sr_lines[:8],
            "astronomyContract": ASTRO_CONTRACT,
            "generatedAt": utc_now(),
        }

    def family_payload(self, family_key: str, selected_event_id: str | None = None) -> dict[str, Any]:
        key = unquote(family_key)
        rows = self.events.loc[self.events["event_family_key"] == key].sort_values("timestamp")
        if rows.empty:
            raise KeyError(f"Unknown family: {key}")
        occurrences = [
            self._event_record(row, occurrence_index=index)
            for index, (_, row) in enumerate(rows.iterrows(), start=1)
        ]
        reviewed = sum(1 for item in occurrences if item["reviewed"])
        bullish = sum(1 for item in occurrences if item["outcome"] == "UP")
        bearish = sum(1 for item in occurrences if item["outcome"] == "DOWN")
        returns = [float(item["returnPct"]) for item in occurrences if item["returnPct"] is not None]
        selected = next((item for item in occurrences if item["eventId"] == selected_event_id), occurrences[0])
        return {
            "familyKey": key,
            "pairKey": selected["pairKey"],
            "aspect": selected["aspect"],
            "transitBody": selected["transitBody"],
            "natalBody": selected["natalBody"],
            "occurrences": occurrences,
            "selectedEventId": selected["eventId"],
            "summary": {
                "total": len(occurrences),
                "reviewed": reviewed,
                "pending": len(occurrences) - reviewed,
                "bullish": bullish,
                "bearish": bearish,
                "unknown": len(occurrences) - bullish - bearish,
                "averageReturnPct": round(float(np.mean(returns)), 4) if returns else None,
            },
            "astronomyContract": ASTRO_CONTRACT,
        }

    def event_detail(self, event_id: str) -> dict[str, Any]:
        rows = self.events.loc[self.events["event_id"] == event_id]
        if rows.empty:
            raise KeyError(f"Unknown event: {event_id}")
        row = rows.iloc[0]
        record = self._event_record(row)
        case = self.case_by_event.get(event_id)
        context = self._case_context(case)
        evidence = []
        for key, label, unit in IMPORTANT_ASTRO_FIELDS:
            value = context.get(key)
            if value in (None, ""):
                continue
            numeric = pd.to_numeric(value, errors="coerce")
            evidence.append(
                {
                    "key": key,
                    "label": label,
                    "value": json_value(numeric) if not pd.isna(numeric) else str(value),
                    "unit": unit,
                    "certification": "provisional" if "strict_" in key else "observed",
                }
            )
        touch = self.touch_by_event.get(event_id)
        if touch is not None:
            for index in (1, 2):
                price_value = pd.to_numeric(touch.get(f"touch_line_price_{index}"), errors="coerce")
                planet_value = touch.get(f"touch_planet_{index}")
                if pd.isna(price_value):
                    continue
                planet = "SR" if pd.isna(planet_value) else str(planet_value)
                evidence.extend(
                    [
                        {
                            "key": f"touch_planet_{index}",
                            "label": f"Touched SR planet {index}",
                            "value": planet,
                            "unit": "text",
                            "certification": "observed",
                        },
                        {
                            "key": f"touch_line_price_{index}",
                            "label": f"Touched SR price {index}",
                            "value": round(float(price_value), 5),
                            "unit": "price",
                            "certification": "observed",
                        },
                    ]
                )
            context = {
                **context,
                "touch_id": str(touch["touch_id"]),
                "touch_time_local": pd.Timestamp(touch["touch_time_local"]).isoformat(),
            }
        start = pd.Timestamp(row["timestamp"]) - pd.Timedelta(hours=72)
        end = pd.Timestamp(row["event_end"]) + pd.Timedelta(hours=72)
        if end - start > pd.Timedelta(days=21):
            peak = pd.Timestamp(row["peak_time"])
            start = peak - pd.Timedelta(days=7)
            end = peak + pd.Timedelta(days=7)
        return {
            "event": record,
            "chart": self.chart_payload(start.isoformat(), end.isoformat()),
            "astroEvidence": evidence,
            "context": {
                key: json_value(value)
                for key, value in context.items()
                if key in {field[0] for field in IMPORTANT_ASTRO_FIELDS}
                or key
                in {
                    "event_best_time_local",
                    "event_strict_shadbala_status",
                    "event_strict_drik_status",
                    "event_strict_shadbala_decision_notes",
                    "ret_after_72h_dir",
                    "ret_after_72h_pct",
                    "touch_planets",
                }
            },
            "annotations": self.list_annotations(event_id=event_id),
        }

    def set_occurrence_progress(self, event_id: str, status: str) -> dict[str, Any]:
        normalized = status.strip().lower()
        if normalized not in {"pending", "reviewed"}:
            raise ValueError("status must be pending or reviewed")
        rows = self.events.loc[self.events["event_id"] == event_id]
        if rows.empty:
            raise KeyError(f"Unknown event: {event_id}")
        family_key = str(rows.iloc[0]["event_family_key"])
        case = self.case_by_event.get(event_id)
        case_id = int(case["case_id"]) if case else None
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_occurrence_progress(event_id, case_id, family_key, status, updated_at_utc)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(event_id) DO UPDATE SET
                    case_id=excluded.case_id,
                    family_key=excluded.family_key,
                    status=excluded.status,
                    updated_at_utc=excluded.updated_at_utc
                """,
                (event_id, case_id, family_key, normalized, utc_now()),
            )
            connection.commit()
        self._reload_case_maps()
        return self._event_record(rows.iloc[0])

    def list_annotations(
        self,
        event_id: str | None = None,
        family_key: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        if event_id:
            clauses.append("event_id = ?")
            values.append(event_id)
        if family_key:
            clauses.append("family_key = ?")
            values.append(family_key)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM chart_annotations {where} ORDER BY created_at_utc, annotation_id",
                values,
            ).fetchall()
        output = []
        for row in rows:
            item = dict(row)
            item["caseId"] = item.pop("case_id")
            item["eventId"] = item.pop("event_id")
            item["familyKey"] = item.pop("family_key")
            item["annotationId"] = item.pop("annotation_id")
            item["annotationType"] = item.pop("annotation_type")
            item["anchorTimeUtc"] = item.pop("anchor_time_utc")
            item["anchorPrice"] = item.pop("anchor_price")
            item["endTimeUtc"] = item.pop("end_time_utc")
            item["endPrice"] = item.pop("end_price")
            item["targetType"] = item.pop("target_type")
            item["targetId"] = item.pop("target_id")
            item["chartState"] = json.loads(item.pop("chart_state_json") or "{}")
            item["createdAtUtc"] = item.pop("created_at_utc")
            item["updatedAtUtc"] = item.pop("updated_at_utc")
            output.append(item)
        return output

    def save_annotation(self, payload: dict[str, Any]) -> dict[str, Any]:
        event_id = str(payload.get("eventId") or "").strip()
        family_key = str(payload.get("familyKey") or "").strip()
        anchor_time = str(payload.get("anchorTimeUtc") or "").strip()
        annotation_type = str(payload.get("annotationType") or "point").strip()
        if not event_id or not family_key or not anchor_time:
            raise ValueError("eventId, familyKey, and anchorTimeUtc are required")
        event_rows = self.events.loc[self.events["event_id"] == event_id]
        if event_rows.empty or str(event_rows.iloc[0]["event_family_key"]) != family_key:
            raise ValueError("annotation event/family identity does not match the source data")
        annotation_id = str(payload.get("annotationId") or uuid.uuid4())
        case = self.case_by_event.get(event_id)
        case_id = int(case["case_id"]) if case else None
        now = utc_now()
        note = str(payload.get("note") or "")[:4000]
        chart_state = payload.get("chartState") if isinstance(payload.get("chartState"), dict) else {}
        values = (
            annotation_id,
            event_id,
            case_id,
            family_key,
            annotation_type,
            anchor_time,
            payload.get("anchorPrice"),
            payload.get("endTimeUtc"),
            payload.get("endPrice"),
            str(payload.get("targetType") or "chart_point"),
            str(payload.get("targetId") or ""),
            note,
            str(payload.get("color") or "#4bb7e5"),
            json.dumps(chart_state, ensure_ascii=True, default=str),
            now,
            now,
        )
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO chart_annotations(
                    annotation_id, event_id, case_id, family_key, annotation_type,
                    anchor_time_utc, anchor_price, end_time_utc, end_price,
                    target_type, target_id, note, color, chart_state_json,
                    created_at_utc, updated_at_utc
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(annotation_id) DO UPDATE SET
                    annotation_type=excluded.annotation_type,
                    anchor_time_utc=excluded.anchor_time_utc,
                    anchor_price=excluded.anchor_price,
                    end_time_utc=excluded.end_time_utc,
                    end_price=excluded.end_price,
                    target_type=excluded.target_type,
                    target_id=excluded.target_id,
                    note=excluded.note,
                    color=excluded.color,
                    chart_state_json=excluded.chart_state_json,
                    updated_at_utc=excluded.updated_at_utc
                """,
                values,
            )
            connection.commit()
        return next(item for item in self.list_annotations(event_id=event_id) if item["annotationId"] == annotation_id)

    def delete_annotation(self, annotation_id: str) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM chart_annotations WHERE annotation_id = ?",
                (annotation_id,),
            )
            connection.commit()
            return cursor.rowcount > 0

    def save_snapshot(self, data_url: str) -> Path:
        prefix = "data:image/png;base64,"
        if not data_url.startswith(prefix):
            raise ValueError("snapshot must be a PNG data URL")
        raw = base64.b64decode(data_url[len(prefix) :], validate=True)
        if len(raw) > 10 * 1024 * 1024:
            raise ValueError("snapshot exceeds 10 MB")
        self.paths.snapshots_dir.mkdir(parents=True, exist_ok=True)
        path = self.paths.snapshots_dir / f"aspect_annotation_{uuid.uuid4().hex}.png"
        path.write_bytes(raw)
        return path

    def codex_context(self, event_id: str, annotation_id: str | None = None) -> dict[str, Any]:
        detail = self.event_detail(event_id)
        selected_annotation = None
        if annotation_id:
            selected_annotation = next(
                (item for item in detail["annotations"] if item["annotationId"] == annotation_id),
                None,
            )
        event = detail["event"]
        return {
            "contextVersion": "gann_astro_desk_codex_context_v1",
            "event": event,
            "selectedAnnotation": selected_annotation,
            "annotations": detail["annotations"],
            "astroEvidence": detail["astroEvidence"],
            "deterministicContext": detail["context"],
            "guardrails": {
                "analysisOnly": True,
                "mt5OrderPlacementAllowed": False,
                "rawLlmTextIsOfficial": False,
                "astronomyContract": ASTRO_CONTRACT,
            },
        }

    def get_codex_thread(self, scope_key: str) -> str | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT thread_id FROM app_codex_threads WHERE scope_key = ?",
                (scope_key,),
            ).fetchone()
        return str(row["thread_id"]) if row else None

    def save_codex_thread(self, scope_key: str, thread_id: str) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_codex_threads(scope_key, thread_id, updated_at_utc)
                VALUES(?, ?, ?)
                ON CONFLICT(scope_key) DO UPDATE SET
                    thread_id=excluded.thread_id,
                    updated_at_utc=excluded.updated_at_utc
                """,
                (scope_key, thread_id, utc_now()),
            )
            connection.commit()
