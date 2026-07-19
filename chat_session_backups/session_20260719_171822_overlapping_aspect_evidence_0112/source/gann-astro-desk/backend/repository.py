from __future__ import annotations

import base64
import json
import os
import re
import sqlite3
import sys
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar
from urllib.parse import unquote

import numpy as np
import pandas as pd

from aspect_timeframe import (
    SUPPORTED_CHART_TIMEFRAMES,
    effective_aspect_min_duration_minutes,
    normalize_aspect_duration_mode,
)
from chart_layouts import ensure_chart_layout_schema
from price_sources import (
    PROMOTED_PRICE_CONTRACT,
    file_sha256,
    load_promoted_price_source,
    promote_snapshot,
)

SHARED_PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).expanduser().resolve()
if str(SHARED_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(SHARED_PROJECT_ROOT))

# The shared engine is outside backend/ in source and at the bundle root when frozen.
from decision_engine import ENGINE, LIVE_FEATURE_ALLOWLIST, currency_pair_evidence  # noqa: E402


IST = "Asia/Kolkata"
UTC = "UTC"
ASTRO_CONTRACT = "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2"
ASPECT_COLORS = {
    "conjunction_orb": "#f28c68",
    "square": "#e0ad45",
    "trine": "#36b8a0",
    "opposition_orb": "#dc6f91",
}
SUPPORTED_ASTRO_ENTITIES = (
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "RAHU",
    "KETU",
    "AVG(ALL)",
)
SUPPORTED_ASPECTS = ("conjunction_orb", "square", "trine", "opposition_orb")
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

TOUCH_BASE_COLUMNS = (
    "event_id",
    "touch_id",
    "touch_time_local",
    "touch_line_price_1",
    "touch_line_price_2",
    "touch_planet_1",
    "touch_planet_2",
)
TOUCH_CONTEXT_COLUMNS = tuple(field[0] for field in IMPORTANT_ASTRO_FIELDS) + (
    "event_best_time_local",
    "event_strict_shadbala_status",
    "event_strict_drik_status",
    "event_strict_shadbala_decision_notes",
    "touch_planets",
)
REQUIRED_EVENT_COLUMNS = {
    "event_id",
    "timestamp",
    "event_end",
    "peak_time",
    "aspect",
    "pair_key",
    "event_family_key",
    "event_transit_body",
    "event_natal_body",
    "duration_minutes",
    "event_peak_orb_deg",
    "event_orb_limit_deg",
    "astronomy_contract_version",
    "source_event_generator",
}

RepositoryMethod = TypeVar("RepositoryMethod", bound=Callable[..., Any])


def synchronized_dataset(method: RepositoryMethod) -> RepositoryMethod:
    @wraps(method)
    def wrapped(self: "AstroRepository", *args: Any, **kwargs: Any) -> Any:
        with self._data_lock:
            return method(self, *args, **kwargs)

    return wrapped  # type: ignore[return-value]


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        try:
            return bool(super().__exit__(exc_type, exc_value, traceback))
        finally:
            self.close()

DEFAULT_CHART_PARAMETERS: dict[str, Any] = {
    "symbol": "USDJPY",
    "dataSource": "research",
    "timeframe": "H1",
    "priceSourceId": "baseline",
    "start": "2025-05-25T00:00:00+05:30",
    "end": "2025-05-31T23:59:59+05:30",
    "mode": "TN",
    "transitBodies": [],
    "natalBodies": [],
    "aspects": ["conjunction_orb", "square", "trine", "opposition_orb"],
    "excludedFamilyKeys": [],
    "onlyTouched": False,
    "aspectDurationMode": "auto",
    "minDurationMinutes": 0.0,
    "maxDurationMinutes": None,
    "liveBarCount": 500,
    "harmonics": [0.12, 0.18],
    "nValues": [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8],
    "degrees": [360, 180, 90, 45],
    "epsilon": 0.30,
    "priceZone": 0.16,
    "reference": {
        "label": "Tokyo IPO hypothesis",
        "date": "1889-02-11",
        "time": "00:00:00",
        "utcOffset": "+09:00",
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
}

CHART_TIMEFRAME_DURATION = {
    "M30": pd.Timedelta(minutes=30),
    "H1": pd.Timedelta(hours=1),
    "H4": pd.Timedelta(hours=4),
    "D1": pd.Timedelta(days=1),
    "W1": pd.Timedelta(days=7),
}


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
    price_data_m30: Path
    annotation_db: Path
    snapshots_dir: Path
    artifacts_dir: Path
    market_snapshots_dir: Path
    price_sources_dir: Path

    @classmethod
    def default(cls) -> "DataPaths":
        root = Path(
            os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
        ).expanduser().resolve()

        def configured_path(name: str, fallback: Path) -> Path:
            return Path(os.environ.get(name) or fallback).expanduser().resolve()

        return cls(
            project_root=root,
            source_events=configured_path(
                "GANN_ASTRO_SOURCE_EVENTS",
                root / "astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet",
            ),
            touch_log=configured_path(
                "GANN_ASTRO_TOUCH_LOG",
                root / "aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv",
            ),
            price_data=configured_path(
                "GANN_ASTRO_PRICE_H1",
                root / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
            ),
            price_data_m30=configured_path(
                "GANN_ASTRO_PRICE_M30",
                root / "usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet",
            ),
            annotation_db=configured_path(
                "GANN_ASTRO_ANNOTATION_DB",
                root / "gann_aspect_annotations_raman_v2.sqlite",
            ),
            snapshots_dir=configured_path(
                "GANN_ASTRO_SNAPSHOTS_DIR",
                Path(r"D:\GannFinancialAstro\app_snapshots"),
            ),
            artifacts_dir=configured_path(
                "GANN_ASTRO_ARTIFACTS_DIR",
                Path(r"D:\GannFinancialAstro\app_artifacts"),
            ),
            market_snapshots_dir=configured_path(
                "GANN_ASTRO_MARKET_SNAPSHOTS_DIR",
                Path(r"D:\GannFinancialAstro\app_data\market_snapshots"),
            ),
            price_sources_dir=configured_path(
                "GANN_ASTRO_PRICE_SOURCES_DIR",
                Path(r"D:\GannFinancialAstro\app_data\price_sources"),
            ),
        )


class AstroRepository:
    def __init__(self, paths: DataPaths | None = None) -> None:
        self.paths = paths or DataPaths.default()
        self._data_lock = threading.RLock()
        self._baseline_metadata: dict[str, Any] | None = None
        self._baseline_reference_events = self._load_event_frame(self.paths.source_events)
        self._baseline_price_by_timeframe = {
            "H1": self._load_price_frame(self.paths.price_data),
            "M30": self._load_price_frame(self.paths.price_data_m30),
        }
        self.price_by_timeframe = dict(self._baseline_price_by_timeframe)
        self.price = self.price_by_timeframe["H1"]
        self._resampled_price: dict[str, pd.DataFrame] = {}
        self._baseline_price_source_cache: dict[str, Any] | None = None
        self._initialize_annotations()
        active = self._active_artifact_row()
        try:
            if active:
                self._install_dataset(
                    Path(str(active["events_path"])),
                    Path(str(active["touch_log_path"])),
                    self._artifact_record(active),
                )
            else:
                baseline = self._baseline_artifact()
                baseline["isActive"] = True
                self._install_dataset(self.paths.source_events, self.paths.touch_log, baseline)
        except Exception:
            if not active:
                raise
            with self.connect() as connection:
                connection.execute("UPDATE app_data_artifacts SET is_active = 0")
                connection.commit()
            baseline = self._baseline_artifact()
            baseline["isActive"] = True
            self._install_dataset(self.paths.source_events, self.paths.touch_log, baseline)
        self._reload_case_maps()

    @staticmethod
    def _load_event_frame(path: Path) -> pd.DataFrame:
        frame = pd.read_parquet(path).copy()
        missing = sorted(REQUIRED_EVENT_COLUMNS - set(frame.columns))
        if missing:
            raise ValueError(f"Event artifact is missing required columns: {missing}")
        for column in ("timestamp", "event_end", "peak_time"):
            frame[column] = pd.to_datetime(frame[column])
        contracts = set(frame["astronomy_contract_version"].dropna().astype(str))
        if contracts != {ASTRO_CONTRACT}:
            raise ValueError(f"Unsupported astronomy contract(s): {sorted(contracts)}")
        return frame.sort_values(["timestamp", "event_family_key", "event_id"]).reset_index(drop=True)

    @staticmethod
    def _load_touch_frame(path: Path) -> pd.DataFrame:
        header = pd.read_csv(path, nrows=0)
        missing = sorted(set(TOUCH_BASE_COLUMNS) - set(header.columns))
        if missing:
            raise ValueError(f"Touch artifact is missing required columns: {missing}")
        requested_columns = dict.fromkeys(
            (*TOUCH_BASE_COLUMNS, *TOUCH_CONTEXT_COLUMNS, *sorted(LIVE_FEATURE_ALLOWLIST))
        )
        usecols = [column for column in requested_columns if column in header.columns]
        frame = pd.read_csv(path, usecols=usecols)
        frame["touch_time_local"] = pd.to_datetime(frame["touch_time_local"])
        return frame

    def _install_dataset(self, events_path: Path, touch_path: Path, artifact: dict[str, Any]) -> None:
        events = self._load_event_frame(events_path)
        touches = self._load_touch_frame(touch_path)
        touch_by_event = {str(row["event_id"]): row for _, row in touches.iterrows()}
        family_counts = events.groupby("event_family_key")["event_id"].count().astype(int).to_dict()
        occurrence_index_by_event: dict[str, int] = {}
        for _, family in events.groupby("event_family_key", sort=False):
            for active_occurrence_index, event_id in enumerate(
                family["event_id"].astype(str),
                start=1,
            ):
                occurrence_index_by_event[event_id] = active_occurrence_index
        if (
            str(artifact.get("symbol") or "").upper() == "USDJPY"
            and str(artifact.get("mode") or "").upper() == "TN"
        ):
            known_events = pd.concat(
                [self._baseline_reference_events, events],
                ignore_index=True,
            )
            known_events = known_events.drop_duplicates(
                subset=["event_family_key", "timestamp", "event_end"],
                keep="last",
            )
        else:
            known_events = events.copy()
        known_events = known_events.sort_values(
            ["timestamp", "event_family_key", "event_id"]
        ).reset_index(drop=True)
        known_family_counts = (
            known_events.groupby("event_family_key")["event_id"]
            .count()
            .astype(int)
            .to_dict()
        )
        known_occurrence_index_by_event: dict[str, int] = {}
        for _, family in known_events.groupby("event_family_key", sort=False):
            for occurrence_index, event_id in enumerate(
                family["event_id"].astype(str),
                start=1,
            ):
                known_occurrence_index_by_event[event_id] = occurrence_index
        installed_artifact = dict(artifact)
        installed_artifact["eventCount"] = int(len(events))
        installed_artifact["touchCount"] = int(len(touches))
        installed_artifact["dateStart"] = pd.Timestamp(events["timestamp"].min()).isoformat()
        installed_artifact["dateEnd"] = pd.Timestamp(events["event_end"].max()).isoformat()
        if artifact.get("builtIn"):
            price_frames = dict(self._baseline_price_by_timeframe)
        else:
            source_timeframe = str(artifact.get("sourceTimeframe") or "H1").upper()
            price_frame = self._load_price_frame(Path(str(artifact.get("pricePath") or "")))
            if source_timeframe == "M30":
                price_frames = {
                    "M30": price_frame,
                    "H1": self._resample_ohlc(price_frame, "1h"),
                }
            elif source_timeframe == "H1":
                price_frames = {"H1": price_frame}
            else:
                raise ValueError(f"Unsupported artifact source timeframe: {source_timeframe}")
        with self._data_lock:
            self.events = events
            self.touches = touches
            self.touch_by_event = touch_by_event
            self.family_counts = family_counts
            self.occurrence_index_by_event = occurrence_index_by_event
            self.known_family_counts = known_family_counts
            self.known_occurrence_index_by_event = known_occurrence_index_by_event
            self.active_artifact = installed_artifact
            self.price_by_timeframe = price_frames
            self.price = price_frames.get("H1", next(iter(price_frames.values())))
            self._resampled_price.clear()

    def _baseline_artifact(self) -> dict[str, Any]:
        return {
            "artifactId": "baseline",
            "label": "Corrected USDJPY baseline",
            "symbol": "USDJPY",
            "mode": "TN",
            "sourceTimeframe": "H1",
            "eventsPath": str(self.paths.source_events),
            "touchLogPath": str(self.paths.touch_log),
            "pricePath": str(self.paths.price_data),
            "parameters": DEFAULT_CHART_PARAMETERS,
            "astronomyContract": ASTRO_CONTRACT,
            "eventCount": None,
            "touchCount": None,
            "dateStart": None,
            "dateEnd": None,
            "isActive": False,
            "createdAtUtc": None,
            "builtIn": True,
        }

    @staticmethod
    def _load_price_frame(path: Path) -> pd.DataFrame:
        frame = pd.read_parquet(path).copy().sort_index()
        if frame.index.tz is None:
            frame.index = frame.index.tz_localize(UTC)
        else:
            frame.index = frame.index.tz_convert(UTC)
        return frame

    @staticmethod
    def _resample_ohlc(
        source: pd.DataFrame,
        rule: str,
        *,
        label: str | None = None,
        closed: str | None = None,
    ) -> pd.DataFrame:
        aggregations: dict[str, str] = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
        }
        for column in ("tick_volume", "real_volume"):
            if column in source.columns:
                aggregations[column] = "sum"
        if "spread" in source.columns:
            aggregations["spread"] = "max"
        return (
            source.resample(rule, label=label, closed=closed)
            .agg(aggregations)
            .dropna(subset=["open", "close"])
        )

    def _price_for_timeframe(self, timeframe: str) -> pd.DataFrame:
        normalized = timeframe.upper()
        if normalized in self.price_by_timeframe:
            return self.price_by_timeframe[normalized]
        if normalized not in {"H4", "D1", "W1"}:
            raise ValueError(f"Unsupported historical timeframe: {timeframe}")
        if normalized not in self._resampled_price:
            source = self.price_by_timeframe.get("H1")
            if source is None:
                raise ValueError(f"Active artifact cannot provide {timeframe} candles")
            if normalized == "W1":
                self._resampled_price[normalized] = self._resample_ohlc(
                    source,
                    "W-MON",
                    label="left",
                    closed="left",
                )
            else:
                rule = "4h" if normalized == "H4" else "1D"
                self._resampled_price[normalized] = self._resample_ohlc(source, rule)
        return self._resampled_price[normalized]

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.paths.annotation_db,
            timeout=30,
            factory=ClosingConnection,
        )
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
                CREATE TABLE IF NOT EXISTS app_parameter_profiles (
                    profile_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    is_default INTEGER NOT NULL DEFAULT 0,
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS app_price_sources (
                    price_source_id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    source_timeframe TEXT NOT NULL CHECK(source_timeframe IN ('M30', 'H1')),
                    price_path TEXT NOT NULL,
                    manifest_path TEXT NOT NULL,
                    source_snapshot_id TEXT NOT NULL,
                    price_sha256 TEXT NOT NULL,
                    contract TEXT NOT NULL,
                    bar_count INTEGER NOT NULL,
                    date_start TEXT NOT NULL,
                    date_end TEXT NOT NULL,
                    as_of_utc TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_app_price_sources_created
                    ON app_price_sources(created_at_utc DESC);
                CREATE TABLE IF NOT EXISTS app_data_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    mode TEXT NOT NULL CHECK(mode IN ('TN', 'TT')),
                    source_timeframe TEXT NOT NULL,
                    events_path TEXT NOT NULL,
                    touch_log_path TEXT NOT NULL,
                    price_path TEXT NOT NULL,
                    events_manifest_path TEXT NOT NULL,
                    artifact_manifest_path TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    astronomy_contract TEXT NOT NULL,
                    event_count INTEGER NOT NULL,
                    touch_count INTEGER NOT NULL,
                    date_start TEXT NOT NULL,
                    date_end TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    created_at_utc TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_app_data_artifacts_active
                    ON app_data_artifacts(is_active) WHERE is_active = 1;
                CREATE INDEX IF NOT EXISTS idx_app_data_artifacts_created
                    ON app_data_artifacts(created_at_utc DESC);
                CREATE TABLE IF NOT EXISTS app_generation_jobs (
                    job_id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN (
                        'queued', 'running', 'cancelling', 'cancelled', 'completed', 'failed'
                    )),
                    stage TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    message TEXT NOT NULL DEFAULT '',
                    parameters_json TEXT NOT NULL,
                    auto_activate INTEGER NOT NULL DEFAULT 1,
                    cancel_requested INTEGER NOT NULL DEFAULT 0,
                    artifact_id TEXT,
                    events_path TEXT NOT NULL DEFAULT '',
                    touch_log_path TEXT NOT NULL DEFAULT '',
                    log_path TEXT NOT NULL DEFAULT '',
                    error TEXT NOT NULL DEFAULT '',
                    created_at_utc TEXT NOT NULL,
                    started_at_utc TEXT,
                    finished_at_utc TEXT,
                    updated_at_utc TEXT NOT NULL,
                    FOREIGN KEY(artifact_id) REFERENCES app_data_artifacts(artifact_id)
                );
                CREATE INDEX IF NOT EXISTS idx_app_generation_jobs_status
                    ON app_generation_jobs(status, created_at_utc);
                """
            )
            connection.execute(
                """
                INSERT INTO schema_meta(key, value, updated_at_utc)
                VALUES('chart_annotation_schema_version', '5', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at_utc=excluded.updated_at_utc
                WHERE schema_meta.value <> excluded.value
                """,
                (utc_now(),),
            )
            connection.commit()
        ensure_chart_layout_schema(self)

    @staticmethod
    def _artifact_record(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        try:
            parameters = json.loads(str(item.get("parameters_json") or "{}"))
        except json.JSONDecodeError:
            parameters = {}
        return {
            "artifactId": str(item["artifact_id"]),
            "label": str(item["label"]),
            "symbol": str(item["symbol"]),
            "mode": str(item["mode"]),
            "sourceTimeframe": str(item["source_timeframe"]),
            "eventsPath": str(item["events_path"]),
            "touchLogPath": str(item["touch_log_path"]),
            "pricePath": str(item["price_path"]),
            "eventsManifestPath": str(item["events_manifest_path"]),
            "artifactManifestPath": str(item["artifact_manifest_path"]),
            "parameters": parameters if isinstance(parameters, dict) else {},
            "astronomyContract": str(item["astronomy_contract"]),
            "eventCount": int(item["event_count"]),
            "touchCount": int(item["touch_count"]),
            "dateStart": str(item["date_start"]),
            "dateEnd": str(item["date_end"]),
            "isActive": bool(item["is_active"]),
            "createdAtUtc": str(item["created_at_utc"]),
            "builtIn": False,
        }

    def _active_artifact_row(self) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute(
                "SELECT * FROM app_data_artifacts WHERE is_active = 1 LIMIT 1"
            ).fetchone()

    def list_data_artifacts(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM app_data_artifacts ORDER BY created_at_utc DESC, artifact_id"
            ).fetchall()
        artifacts = [self._artifact_record(row) for row in rows]
        baseline = self._baseline_artifact()
        if self._baseline_metadata is None:
            baseline_events = self._load_event_frame(self.paths.source_events)
            self._baseline_metadata = {
                "eventCount": int(len(baseline_events)),
                "touchCount": int(len(self._load_touch_frame(self.paths.touch_log))),
                "dateStart": pd.Timestamp(baseline_events["timestamp"].min()).isoformat(),
                "dateEnd": pd.Timestamp(baseline_events["event_end"].max()).isoformat(),
            }
        baseline.update(self._baseline_metadata)
        baseline["isActive"] = not any(item["isActive"] for item in artifacts)
        return [baseline, *artifacts]

    @staticmethod
    def _price_source_record(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        return {
            "priceSourceId": str(item["price_source_id"]),
            "label": str(item["label"]),
            "symbol": str(item["symbol"]),
            "sourceTimeframe": str(item["source_timeframe"]),
            "pricePath": str(item["price_path"]),
            "manifestPath": str(item["manifest_path"]),
            "sourceSnapshotId": str(item["source_snapshot_id"]),
            "priceSha256": str(item["price_sha256"]),
            "contract": str(item["contract"]),
            "barCount": int(item["bar_count"]),
            "dateStart": str(item["date_start"]),
            "dateEnd": str(item["date_end"]),
            "asOfUtc": str(item["as_of_utc"]),
            "createdAtUtc": str(item["created_at_utc"]),
            "builtIn": False,
            "verified": True,
        }

    def _baseline_price_source(self) -> dict[str, Any]:
        if self._baseline_price_source_cache is None:
            h1 = self._baseline_price_by_timeframe["H1"]
            m30 = self._baseline_price_by_timeframe["M30"]
            self._baseline_price_source_cache = {
                "priceSourceId": "baseline",
                "label": "Bundled corrected baseline",
                "symbol": "USDJPY",
                "sourceTimeframe": "AUTO",
                "pricePath": "",
                "manifestPath": "",
                "sourceSnapshotId": None,
                "priceSha256": "",
                "contract": "BUNDLED_CORRECTED_PRICE_BASELINE_V1",
                "barCount": int(len(h1)),
                "dateStart": min(h1.index.min(), m30.index.min()).isoformat(),
                "dateEnd": max(h1.index.max(), m30.index.max()).isoformat(),
                "asOfUtc": max(h1.index.max(), m30.index.max()).isoformat(),
                "createdAtUtc": None,
                "builtIn": True,
                "verified": True,
            }
        return dict(self._baseline_price_source_cache)

    def list_price_sources(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM app_price_sources ORDER BY created_at_utc DESC, price_source_id"
            ).fetchall()
        records: list[dict[str, Any]] = [self._baseline_price_source()]
        for row in rows:
            record = self._price_source_record(row)
            try:
                manifest, _ = load_promoted_price_source(
                    self.paths.price_sources_dir, record["priceSourceId"]
                )
                if manifest["priceSha256"] != record["priceSha256"]:
                    raise ValueError("registered SHA-256 differs from promoted manifest")
            except Exception as exc:
                record["verified"] = False
                record["validationError"] = str(exc)
            records.append(record)
        return records

    def register_price_source(self, payload: dict[str, Any]) -> dict[str, Any]:
        source_id = str(payload.get("priceSourceId") or "").strip()
        if not source_id or payload.get("contract") != PROMOTED_PRICE_CONTRACT:
            raise ValueError("verified promoted price source payload is required")
        manifest, _ = load_promoted_price_source(self.paths.price_sources_dir, source_id)
        for key in (
            "sourceSnapshotId",
            "symbol",
            "sourceTimeframe",
            "priceSha256",
            "barCount",
            "dateStart",
            "dateEnd",
            "asOfUtc",
        ):
            if str(payload.get(key)) != str(manifest.get(key)):
                raise ValueError(f"promoted price source {key} does not match its manifest")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_price_sources(
                    price_source_id, label, symbol, source_timeframe, price_path,
                    manifest_path, source_snapshot_id, price_sha256, contract,
                    bar_count, date_start, date_end, as_of_utc, created_at_utc
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(price_source_id) DO UPDATE SET
                    label=excluded.label,
                    price_path=excluded.price_path,
                    manifest_path=excluded.manifest_path,
                    price_sha256=excluded.price_sha256
                """,
                (
                    source_id,
                    str(manifest.get("label") or "Promoted MT5 snapshot")[:120],
                    str(manifest["symbol"]).upper(),
                    str(manifest["sourceTimeframe"]).upper(),
                    str(manifest["pricePath"]),
                    str(manifest["manifestPath"]),
                    str(manifest["sourceSnapshotId"]),
                    str(manifest["priceSha256"]),
                    str(manifest["contract"]),
                    int(manifest["barCount"]),
                    str(manifest["dateStart"]),
                    str(manifest["dateEnd"]),
                    str(manifest["asOfUtc"]),
                    str(manifest["createdAtUtc"]),
                ),
            )
            connection.commit()
        return next(item for item in self.list_price_sources() if item["priceSourceId"] == source_id)

    def promote_history_snapshot(self, snapshot_id: str, label: str | None = None) -> dict[str, Any]:
        promoted = promote_snapshot(
            self.paths.market_snapshots_dir,
            self.paths.price_sources_dir,
            snapshot_id,
            label,
        )
        return self.register_price_source(promoted)

    def resolve_price_source(
        self,
        price_source_id: str | None,
        source_timeframe: str,
    ) -> tuple[dict[str, Any], pd.DataFrame]:
        normalized_id = str(price_source_id or "baseline").strip()
        normalized_timeframe = str(source_timeframe or "H1").upper()
        if normalized_timeframe not in {"M30", "H1"}:
            raise ValueError(f"Unsupported generation source timeframe: {source_timeframe}")
        if normalized_id == "baseline":
            path = self.paths.price_data_m30 if normalized_timeframe == "M30" else self.paths.price_data
            frame = self._baseline_price_by_timeframe[normalized_timeframe]
            return {
                **self._baseline_price_source(),
                "sourceTimeframe": normalized_timeframe,
                "pricePath": str(path),
                "priceSha256": file_sha256(path),
                "barCount": int(len(frame)),
                "dateStart": frame.index.min().isoformat(),
                "dateEnd": frame.index.max().isoformat(),
                "asOfUtc": frame.index.max().isoformat(),
            }, frame
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM app_price_sources WHERE price_source_id = ?", (normalized_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown price source: {normalized_id}")
        record = self._price_source_record(row)
        if record["sourceTimeframe"] != normalized_timeframe:
            raise ValueError(
                f"Price source {normalized_id} is {record['sourceTimeframe']}, not {normalized_timeframe}"
            )
        manifest, frame = load_promoted_price_source(self.paths.price_sources_dir, normalized_id)
        if manifest["priceSha256"] != record["priceSha256"]:
            raise ValueError("registered price source SHA-256 no longer matches its manifest")
        return record, frame

    def register_data_artifact(self, payload: dict[str, Any]) -> dict[str, Any]:
        artifact_id = str(payload.get("artifactId") or "").strip()
        if not artifact_id:
            raise ValueError("artifactId is required")
        root = self.paths.artifacts_dir.resolve()
        path_keys = (
            "eventsPath",
            "touchLogPath",
            "pricePath",
            "eventsManifestPath",
            "artifactManifestPath",
        )
        resolved_paths: dict[str, Path] = {}
        for key in path_keys:
            path = Path(str(payload.get(key) or "")).resolve()
            if key == "pricePath":
                baseline_paths = {
                    self.paths.price_data.resolve(),
                    self.paths.price_data_m30.resolve(),
                }
                approved = path in baseline_paths or path.is_relative_to(
                    self.paths.price_sources_dir.resolve()
                )
                if not approved:
                    raise ValueError("pricePath must be a baseline or verified promoted price source")
            elif not path.is_relative_to(root):
                raise ValueError(f"{key} must stay inside the app artifact directory")
            if not path.exists():
                raise ValueError(f"{key} does not exist: {path}")
            resolved_paths[key] = path
        parameters = payload.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError("artifact parameters are required")
        now = utc_now()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_data_artifacts(
                    artifact_id, label, symbol, mode, source_timeframe,
                    events_path, touch_log_path, price_path, events_manifest_path,
                    artifact_manifest_path, parameters_json, astronomy_contract,
                    event_count, touch_count, date_start, date_end, is_active, created_at_utc
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    artifact_id,
                    str(payload.get("label") or "Generated TN source")[:120],
                    str(payload.get("symbol") or "USDJPY").upper(),
                    str(payload.get("mode") or "TN").upper(),
                    str(payload.get("sourceTimeframe") or "H1").upper(),
                    str(resolved_paths["eventsPath"]),
                    str(resolved_paths["touchLogPath"]),
                    str(resolved_paths["pricePath"]),
                    str(resolved_paths["eventsManifestPath"]),
                    str(resolved_paths["artifactManifestPath"]),
                    json.dumps(parameters, ensure_ascii=True, sort_keys=True, default=str),
                    str(payload.get("astronomyContract") or ASTRO_CONTRACT),
                    int(payload.get("eventCount") or 0),
                    int(payload.get("touchCount") or 0),
                    str(payload.get("dateStart") or ""),
                    str(payload.get("dateEnd") or ""),
                    now,
                ),
            )
            connection.commit()
        return next(item for item in self.list_data_artifacts() if item["artifactId"] == artifact_id)

    def activate_artifact(self, artifact_id: str) -> dict[str, Any]:
        normalized = str(artifact_id or "").strip()
        with self._data_lock:
            if normalized == "baseline":
                artifact = self._baseline_artifact()
                self._install_dataset(self.paths.source_events, self.paths.touch_log, artifact)
                with self.connect() as connection:
                    connection.execute("UPDATE app_data_artifacts SET is_active = 0")
                    connection.commit()
                active = {**self.active_artifact, "isActive": True}
                self.active_artifact = active
                return active
            with self.connect() as connection:
                row = connection.execute(
                    "SELECT * FROM app_data_artifacts WHERE artifact_id = ?", (normalized,)
                ).fetchone()
            if row is None:
                raise KeyError(f"Unknown data artifact: {normalized}")
            artifact = self._artifact_record(row)
            root = self.paths.artifacts_dir.resolve()
            events_path = Path(artifact["eventsPath"]).resolve()
            touch_path = Path(artifact["touchLogPath"]).resolve()
            if not events_path.is_relative_to(root) or not touch_path.is_relative_to(root):
                raise ValueError("Registered artifact paths leave the app artifact directory")
            price_path = Path(artifact["pricePath"]).resolve()
            artifact_manifest_path = Path(artifact["artifactManifestPath"]).resolve()
            try:
                artifact_manifest = json.loads(artifact_manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError("Artifact manifest is unreadable") from exc
            expected_price_sha = str(artifact_manifest.get("price_source_sha256") or "").upper()
            if not expected_price_sha or file_sha256(price_path) != expected_price_sha:
                raise ValueError("Artifact price source SHA-256 verification failed")
            self._install_dataset(
                events_path,
                touch_path,
                artifact,
            )
            with self.connect() as connection:
                connection.execute("UPDATE app_data_artifacts SET is_active = 0")
                connection.execute(
                    "UPDATE app_data_artifacts SET is_active = 1 WHERE artifact_id = ?", (normalized,)
                )
                connection.commit()
            active = {**self.active_artifact, "isActive": True}
            self.active_artifact = active
            return active

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

    @synchronized_dataset
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
            "activeArtifact": self.active_artifact,
        }

    @synchronized_dataset
    def parameter_schema(self) -> dict[str, Any]:
        ranges = {}
        available_timeframes: list[str] = []
        for timeframe in SUPPORTED_CHART_TIMEFRAMES:
            try:
                frame = self._price_for_timeframe(timeframe)
            except ValueError:
                continue
            available_timeframes.append(timeframe)
            ranges[timeframe] = {
                "start": frame.index.min().isoformat(),
                "end": frame.index.max().isoformat(),
            }
        transit_bodies = list(SUPPORTED_ASTRO_ENTITIES)
        natal_bodies = list(SUPPORTED_ASTRO_ENTITIES)
        aspects = list(SUPPORTED_ASPECTS)
        active_parameters = self.active_artifact.get("parameters")
        defaults = {
            **DEFAULT_CHART_PARAMETERS,
            **(active_parameters if isinstance(active_parameters, dict) else {}),
        }
        defaults["reference"] = {
            **DEFAULT_CHART_PARAMETERS["reference"],
            **(
                active_parameters.get("reference", {})
                if isinstance(active_parameters, dict)
                and isinstance(active_parameters.get("reference"), dict)
                else {}
            ),
        }
        if defaults.get("timeframe") not in available_timeframes:
            defaults["timeframe"] = available_timeframes[0]
        return {
            "defaults": defaults,
            "options": {
                "symbols": ["USDJPY"],
                "timeframes": available_timeframes,
                "modes": [
                    {"id": "TN", "label": "Transit to natal", "available": True},
                    {"id": "TT", "label": "Transit to transit", "available": False},
                ],
                "transitBodies": transit_bodies,
                "natalBodies": natal_bodies,
                "aspects": aspects,
                "familyKeys": sorted(self.family_counts),
                "priceSources": self.list_price_sources(),
            },
            "dataRanges": ranges,
            "generation": {
                "correctedTn": "generator_ready",
                "correctedTt": "not_implemented",
                "customSrConfig": "builder_accepts_profile_config",
                "profileJobQueue": "ready",
                "astronomyContract": ASTRO_CONTRACT,
                "activeArtifactId": self.active_artifact["artifactId"],
            },
        }

    def list_parameter_profiles(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM app_parameter_profiles ORDER BY is_default DESC, updated_at_utc DESC, name"
            ).fetchall()
        profiles = []
        for row in rows:
            item = dict(row)
            try:
                parameters = json.loads(str(item["parameters_json"]))
            except json.JSONDecodeError:
                parameters = {}
            profiles.append(
                {
                    "profileId": str(item["profile_id"]),
                    "name": str(item["name"]),
                    "parameters": parameters if isinstance(parameters, dict) else {},
                    "isDefault": bool(item["is_default"]),
                    "createdAtUtc": str(item["created_at_utc"]),
                    "updatedAtUtc": str(item["updated_at_utc"]),
                }
            )
        return profiles

    def save_parameter_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        name = str(payload.get("name") or "").strip()[:80]
        parameters = payload.get("parameters")
        if not name or not isinstance(parameters, dict):
            raise ValueError("profile name and parameters are required")
        encoded = json.dumps(parameters, ensure_ascii=True, sort_keys=True, default=str)
        if len(encoded) > 100_000:
            raise ValueError("parameter profile exceeds 100 KB")
        profile_id = str(payload.get("profileId") or uuid.uuid4())
        is_default = bool(payload.get("isDefault", False))
        now = utc_now()
        with self.connect() as connection:
            if is_default:
                connection.execute("UPDATE app_parameter_profiles SET is_default = 0")
            connection.execute(
                """
                INSERT INTO app_parameter_profiles(
                    profile_id, name, parameters_json, is_default, created_at_utc, updated_at_utc
                ) VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(profile_id) DO UPDATE SET
                    name=excluded.name,
                    parameters_json=excluded.parameters_json,
                    is_default=excluded.is_default,
                    updated_at_utc=excluded.updated_at_utc
                """,
                (profile_id, name, encoded, int(is_default), now, now),
            )
            connection.commit()
        return next(item for item in self.list_parameter_profiles() if item["profileId"] == profile_id)

    def delete_parameter_profile(self, profile_id: str) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM app_parameter_profiles WHERE profile_id = ?", (profile_id,))
            connection.commit()
            return cursor.rowcount > 0

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
        if occurrence_index is None:
            occurrence_index = self.occurrence_index_by_event.get(event_id)
        case = self.case_by_event.get(event_id)
        context = self._case_context(case)
        case_id = int(case["case_id"]) if case else None
        review = self.review_by_case.get(case_id) if case_id is not None else None
        progress = self.progress_by_event.get(event_id)
        reviewed = bool(review) or bool(progress and progress.get("status") == "reviewed")
        outcome = str(context.get("ret_after_72h_dir") or "").upper() or None
        known_occurrence_index = self.known_occurrence_index_by_event.get(event_id)
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
            "knownPriorCount": max(0, int(known_occurrence_index or 1) - 1),
            "knownOccurrenceCount": int(
                self.known_family_counts.get(str(row["event_family_key"]), 1)
            ),
            "outcome": outcome,
            "returnPct": json_value(pd.to_numeric(context.get("ret_after_72h_pct"), errors="coerce")),
            "reviewed": reviewed,
            "reviewStatus": review.get("review_status") if review else (progress.get("status") if progress else "pending"),
            "reviewSource": "legacy_completed_review" if review else ("app_progress" if progress else "none"),
            "signedPips": json_value(review.get("signed_pips")) if review else None,
            "astronomyContract": str(row["astronomy_contract_version"]),
            "sourceGenerator": str(row["source_event_generator"]),
        }

    @staticmethod
    def _family_summary(occurrences: list[dict[str, Any]]) -> dict[str, Any]:
        reviewed = sum(1 for item in occurrences if item["reviewed"])
        bullish = sum(1 for item in occurrences if item["outcome"] == "UP")
        bearish = sum(1 for item in occurrences if item["outcome"] == "DOWN")
        returns = [
            float(item["returnPct"])
            for item in occurrences
            if item["returnPct"] is not None
        ]
        return {
            "total": len(occurrences),
            "reviewed": reviewed,
            "pending": len(occurrences) - reviewed,
            "bullish": bullish,
            "bearish": bearish,
            "unknown": len(occurrences) - bullish - bearish,
            "averageReturnPct": round(float(np.mean(returns)), 4) if returns else None,
        }

    def _family_occurrences(self, family_key: str) -> list[dict[str, Any]]:
        rows = self.events.loc[
            self.events["event_family_key"].astype(str) == str(family_key)
        ].sort_values("timestamp")
        return [
            self._event_record(row, occurrence_index=index)
            for index, (_, row) in enumerate(rows.iterrows(), start=1)
        ]

    def _assign_lanes(self, events: list[dict[str, Any]], lane_count: int = 7) -> None:
        lane_ends = [0] * lane_count
        for event in sorted(events, key=lambda item: (item["start"], item["end"])):
            lane = next((idx for idx, end in enumerate(lane_ends) if event["start"] > end), None)
            if lane is None:
                lane = min(range(lane_count), key=lambda idx: lane_ends[idx])
            event["lane"] = lane
            lane_ends[lane] = max(lane_ends[lane], int(event["end"]))

    @synchronized_dataset
    def chart_payload(
        self,
        start: str | None = None,
        end: str | None = None,
        symbol: str = "USDJPY",
        timeframe: str = "H1",
        transit_bodies: tuple[str, ...] | None = None,
        natal_bodies: tuple[str, ...] | None = None,
        aspects: tuple[str, ...] | None = None,
        excluded_family_keys: tuple[str, ...] | None = None,
        only_touched: bool = False,
        aspect_duration_mode: str = "auto",
        min_duration_minutes: float = 0.0,
        max_duration_minutes: float | None = None,
        replay_cutoff: str | None = None,
    ) -> dict[str, Any]:
        symbol = symbol.upper().strip()
        timeframe = timeframe.upper().strip()
        artifact_symbol = str(self.active_artifact.get("symbol") or "USDJPY").upper().strip()
        if symbol != artifact_symbol:
            raise ValueError(
                f"The active corrected artifact is for {artifact_symbol}, not {symbol}"
            )
        price_source = self._price_for_timeframe(timeframe)
        duration_mode = normalize_aspect_duration_mode(aspect_duration_mode)
        effective_min_duration = effective_aspect_min_duration_minutes(
            timeframe,
            duration_mode,
            min_duration_minutes,
        )
        start_local = parse_local_timestamp(start, "2025-05-25T00:00:00+05:30")
        end_local = parse_local_timestamp(end, "2025-05-31T23:59:59+05:30")
        if end_local <= start_local:
            raise ValueError("end must be later than start")
        start_utc = start_local.tz_convert(UTC)
        end_utc = end_local.tz_convert(UTC)
        source_price = price_source.loc[
            (price_source.index >= start_utc) & (price_source.index <= end_utc)
        ]
        if len(source_price) > 50_000:
            raise ValueError("Chart request exceeds 50,000 candles; narrow the date range or use a larger timeframe")
        timeframe_duration = CHART_TIMEFRAME_DURATION.get(timeframe)
        if timeframe_duration is None:
            raise ValueError(f"Unsupported replay timeframe: {timeframe}")
        replay_active = replay_cutoff is not None
        replay_metadata: dict[str, Any] | None = None
        price = source_price
        replay_cutoff_utc: pd.Timestamp | None = None
        if replay_active:
            if source_price.empty:
                raise ValueError("Bar Replay requires at least one candle in the requested range")
            replay_cutoff_utc = pd.Timestamp(replay_cutoff)
            if replay_cutoff_utc.tzinfo is None:
                raise ValueError("replayCutoff must include a UTC offset")
            replay_cutoff_utc = replay_cutoff_utc.tz_convert(UTC)
            close_times = source_price.index + timeframe_duration
            revealed_mask = close_times <= replay_cutoff_utc
            price = source_price.loc[revealed_mask]
            if price.empty:
                first_close = close_times[0].isoformat()
                raise ValueError(
                    f"replayCutoff precedes the first closed candle; use {first_close} or later"
                )
            revealed_count = int(revealed_mask.sum())
            previous_cutoff = (
                close_times[revealed_count - 2].isoformat()
                if revealed_count > 1
                else None
            )
            next_cutoff = (
                close_times[revealed_count].isoformat()
                if revealed_count < len(close_times)
                else None
            )
            replay_metadata = {
                "contract": "GANN_TIMESTAMP_SAFE_BAR_REPLAY_V1",
                "active": True,
                "cutoffUtc": replay_cutoff_utc.isoformat(),
                "evidenceCutoff": replay_cutoff_utc.isoformat(),
                "sourceDataMaxTime": close_times[revealed_count - 1].isoformat(),
                "firstCutoffUtc": close_times[0].isoformat(),
                "previousCutoffUtc": previous_cutoff,
                "nextCutoffUtc": next_cutoff,
                "position": revealed_count,
                "totalBars": int(len(close_times)),
                "excludedFutureCandles": int(len(close_times) - revealed_count),
                "timestampSafe": True,
                "noLookahead": True,
            }
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
        visible_end_local = (
            min(end_local, replay_cutoff_utc.tz_convert(IST))
            if replay_cutoff_utc is not None
            else end_local
        )
        overlapping = self.events.loc[
            (self.events["timestamp"] <= visible_end_local)
            & (self.events["event_end"] >= start_local)
        ]
        if transit_bodies:
            overlapping = overlapping.loc[overlapping["event_transit_body"].astype(str).isin(transit_bodies)]
        if natal_bodies:
            overlapping = overlapping.loc[overlapping["event_natal_body"].astype(str).isin(natal_bodies)]
        if aspects:
            overlapping = overlapping.loc[overlapping["aspect"].astype(str).isin(aspects)]
        if excluded_family_keys:
            overlapping = overlapping.loc[~overlapping["event_family_key"].astype(str).isin(excluded_family_keys)]
        if only_touched:
            overlapping = overlapping.loc[overlapping["event_id"].astype(str).isin(self.touch_by_event)]
        overlapping = overlapping.loc[
            pd.to_numeric(overlapping["duration_minutes"], errors="coerce")
            >= effective_min_duration
        ]
        if max_duration_minutes is not None:
            overlapping = overlapping.loc[
                pd.to_numeric(overlapping["duration_minutes"], errors="coerce") <= max_duration_minutes
            ]
        event_records = [self._event_record(row) for _, row in overlapping.iterrows()]
        if replay_cutoff_utc is not None:
            historical_counts = (
                self.events.loc[self.events["timestamp"] <= visible_end_local]
                .groupby("event_family_key")["event_id"]
                .count()
                .astype(int)
                .to_dict()
            )
            cutoff_epoch = int(replay_cutoff_utc.timestamp())
            for event in event_records:
                event["end"] = min(int(event["end"]), cutoff_epoch)
                event["endIso"] = pd.Timestamp(event["end"], unit="s", tz=UTC).isoformat()
                event["peak"] = min(int(event["peak"]), cutoff_epoch)
                event["peakIso"] = pd.Timestamp(event["peak"], unit="s", tz=UTC).isoformat()
                event["durationMinutes"] = round(
                    max(0.0, (event["end"] - int(event["start"])) / 60.0),
                    2,
                )
                event["occurrenceCount"] = int(
                    historical_counts.get(event["familyKey"], 1)
                )
                event["outcome"] = None
                event["returnPct"] = None
                event["reviewed"] = False
                event["reviewStatus"] = "unavailable_during_replay"
                event["reviewSource"] = "none"
                event["signedPips"] = None
        self._assign_lanes(event_records)
        sr_lines: list[dict[str, Any]] = []
        seen_prices: set[tuple[str, float]] = set()
        for event in event_records:
            touch = self.touch_by_event.get(event["eventId"])
            if touch is None:
                continue
            touch_time = pd.Timestamp(touch["touch_time_local"])
            if touch_time.tzinfo is None:
                touch_time = touch_time.tz_localize(IST)
            touch_known_at = touch_time.tz_convert(UTC) + timeframe_duration
            if replay_cutoff_utc is not None and touch_known_at > replay_cutoff_utc:
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
            "dataSource": "corrected_historical",
            "parametersApplied": {
                "transitBodies": list(transit_bodies or ()),
                "natalBodies": list(natal_bodies or ()),
                "aspects": list(aspects or ()),
                "excludedFamilyKeys": list(excluded_family_keys or ()),
                "onlyTouched": only_touched,
                "aspectDurationMode": duration_mode,
                "requestedMinDurationMinutes": min_duration_minutes,
                "effectiveMinDurationMinutes": effective_min_duration,
                "minimumAspectBars": 1 if duration_mode == "auto" else None,
                "minDurationMinutes": effective_min_duration,
                "maxDurationMinutes": max_duration_minutes,
            },
            "artifact": self.active_artifact,
            "generatedAt": utc_now(),
            "replay": replay_metadata,
        }

    @synchronized_dataset
    def family_payload(self, family_key: str, selected_event_id: str | None = None) -> dict[str, Any]:
        key = unquote(family_key)
        occurrences = self._family_occurrences(key)
        if not occurrences:
            raise KeyError(f"Unknown family: {key}")
        selected = next((item for item in occurrences if item["eventId"] == selected_event_id), occurrences[0])
        return {
            "familyKey": key,
            "pairKey": selected["pairKey"],
            "aspect": selected["aspect"],
            "transitBody": selected["transitBody"],
            "natalBody": selected["natalBody"],
            "occurrences": occurrences,
            "selectedEventId": selected["eventId"],
            "summary": self._family_summary(occurrences),
            "astronomyContract": ASTRO_CONTRACT,
            "artifact": self.active_artifact,
        }

    @synchronized_dataset
    def event_detail(self, event_id: str) -> dict[str, Any]:
        rows = self.events.loc[self.events["event_id"] == event_id]
        if rows.empty:
            raise KeyError(f"Unknown event: {event_id}")
        row = rows.iloc[0]
        family_occurrences = self._family_occurrences(str(row["event_family_key"]))
        record = next(
            item for item in family_occurrences if item["eventId"] == event_id
        )
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
        pair_evidence = None
        if touch is not None:
            pair_scores = currency_pair_evidence(touch)
            symbol_letters = re.sub(
                r"[^A-Z]",
                "",
                str(self.active_artifact.get("symbol") or "").upper(),
            )
            base_currency = symbol_letters[:3] if len(symbol_letters) >= 6 else "BASE"
            quote_currency = symbol_letters[3:6] if len(symbol_letters) >= 6 else "QUOTE"
            pair_evidence = {
                "contract": "GANN_FX_PAIR_EVIDENCE_V1",
                "status": (
                    "provisional_research_only"
                    if str(pair_scores.get("fx_hypothesis_direction") or "UNKNOWN")
                    != "UNKNOWN"
                    else "insufficient_pair_evidence"
                ),
                "base": {
                    "label": base_currency,
                    "referenceLabel": str(
                        pair_scores.get("fx_base_reference_label") or base_currency
                    ),
                    "netScore": pair_scores.get("fx_base_net_score"),
                    "doctrineNetScore": pair_scores.get("fx_doctrine_base_net_score"),
                    "scoredHitCount": pair_scores.get("fx_base_scored_hit_count"),
                    "dominantHit": pair_scores.get("fx_dominant_base_hit"),
                    "doctrineDominantHit": pair_scores.get(
                        "fx_doctrine_dominant_base_hit"
                    ),
                    "doctrineDominantDignity": pair_scores.get(
                        "fx_doctrine_dominant_base_dignity"
                    ),
                    "doctrineDignityVirupaAvg": pair_scores.get(
                        "fx_doctrine_base_dignity_virupa_avg"
                    ),
                },
                "quote": {
                    "label": quote_currency,
                    "referenceLabel": str(
                        pair_scores.get("fx_quote_reference_label") or quote_currency
                    ),
                    "netScore": pair_scores.get("fx_quote_net_score"),
                    "doctrineNetScore": pair_scores.get("fx_doctrine_quote_net_score"),
                    "scoredHitCount": pair_scores.get("fx_quote_scored_hit_count"),
                    "dominantHit": pair_scores.get("fx_dominant_quote_hit"),
                    "doctrineDominantHit": pair_scores.get(
                        "fx_doctrine_dominant_quote_hit"
                    ),
                    "doctrineDominantDignity": pair_scores.get(
                        "fx_doctrine_dominant_quote_dignity"
                    ),
                    "doctrineDignityVirupaAvg": pair_scores.get(
                        "fx_doctrine_quote_dignity_virupa_avg"
                    ),
                },
                "pair": {
                    "netScore": pair_scores.get("fx_pair_net_score"),
                    "conflictRatio": pair_scores.get("fx_pair_conflict_ratio"),
                    "direction": pair_scores.get("fx_hypothesis_direction"),
                    "doctrineNetScore": pair_scores.get(
                        "fx_doctrine_pair_net_score"
                    ),
                    "doctrineConflictRatio": pair_scores.get(
                        "fx_doctrine_pair_conflict_ratio"
                    ),
                    "doctrineDirection": pair_scores.get(
                        "fx_doctrine_hypothesis_direction"
                    ),
                },
                "notes": pair_scores.get("fx_scoring_notes"),
            }
            touch_context = {
                key: json_value(touch.get(key))
                for key in TOUCH_CONTEXT_COLUMNS
                if key in touch.index and not pd.isna(touch.get(key))
            }
            context = {**context, **touch_context}
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
            "familySummary": self._family_summary(family_occurrences),
            "currencyPairEvidence": pair_evidence,
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
                    "touch_time_local",
                }
            },
            "annotations": self.list_annotations(event_id=event_id),
        }

    @synchronized_dataset
    def shadow_candidate_snapshot(self) -> dict[str, Any]:
        timeframe = str(self.active_artifact.get("sourceTimeframe") or "H1").upper()
        touches = [
            {
                "eventId": str(row["event_id"]),
                "touchId": str(row["touch_id"]),
                "touchTime": pd.Timestamp(row["touch_time_local"]).isoformat(),
            }
            for _, row in self.touches.iterrows()
        ]
        return {
            "artifact": json.loads(json.dumps(self.active_artifact, default=str)),
            "timeframe": timeframe,
            "touches": touches,
        }

    @synchronized_dataset
    def live_decision_packet(
        self,
        event_id: str,
        decision_time: Any,
        *,
        price_override: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        rows = self.events.loc[self.events["event_id"].astype(str) == str(event_id)]
        if rows.empty:
            raise KeyError(f"Unknown event: {event_id}")
        event = rows.iloc[0].copy()
        case = self.case_by_event.get(str(event_id))
        if case is not None:
            event["case_id"] = int(case["case_id"])
        timeframe = str(self.active_artifact.get("sourceTimeframe") or "H1").upper()
        price = price_override.copy() if price_override is not None else self._price_for_timeframe(timeframe)
        touch = self.touch_by_event.get(str(event_id))
        return ENGINE.live_inference_packet(
            event=event,
            touch=touch,
            price=price,
            decision_time=decision_time,
            timeframe=timeframe,
            artifact=self.active_artifact,
        )

    @synchronized_dataset
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

    @synchronized_dataset
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
