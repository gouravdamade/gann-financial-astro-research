from __future__ import annotations

import base64
import json
import os
import sqlite3
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
    "start": "2025-05-25T00:00:00+05:30",
    "end": "2025-05-31T23:59:59+05:30",
    "mode": "TN",
    "transitBodies": [],
    "natalBodies": [],
    "aspects": ["conjunction_orb", "square", "trine", "opposition_orb"],
    "excludedFamilyKeys": [],
    "onlyTouched": False,
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
        )


class AstroRepository:
    def __init__(self, paths: DataPaths | None = None) -> None:
        self.paths = paths or DataPaths.default()
        self._data_lock = threading.RLock()
        self._baseline_metadata: dict[str, Any] | None = None
        self.price_by_timeframe = {
            "H1": self._load_price_frame(self.paths.price_data),
            "M30": self._load_price_frame(self.paths.price_data_m30),
        }
        self.price = self.price_by_timeframe["H1"]
        self._resampled_price: dict[str, pd.DataFrame] = {}
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
        usecols = [
            column
            for column in (*TOUCH_BASE_COLUMNS, *TOUCH_CONTEXT_COLUMNS)
            if column in header.columns
        ]
        frame = pd.read_csv(path, usecols=usecols)
        frame["touch_time_local"] = pd.to_datetime(frame["touch_time_local"])
        return frame

    def _install_dataset(self, events_path: Path, touch_path: Path, artifact: dict[str, Any]) -> None:
        events = self._load_event_frame(events_path)
        touches = self._load_touch_frame(touch_path)
        touch_by_event = {str(row["event_id"]): row for _, row in touches.iterrows()}
        family_counts = events.groupby("event_family_key")["event_id"].count().astype(int).to_dict()
        installed_artifact = dict(artifact)
        installed_artifact["eventCount"] = int(len(events))
        installed_artifact["touchCount"] = int(len(touches))
        installed_artifact["dateStart"] = pd.Timestamp(events["timestamp"].min()).isoformat()
        installed_artifact["dateEnd"] = pd.Timestamp(events["event_end"].max()).isoformat()
        with self._data_lock:
            self.events = events
            self.touches = touches
            self.touch_by_event = touch_by_event
            self.family_counts = family_counts
            self.active_artifact = installed_artifact

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

    def _price_for_timeframe(self, timeframe: str) -> pd.DataFrame:
        normalized = timeframe.upper()
        if normalized in self.price_by_timeframe:
            return self.price_by_timeframe[normalized]
        if normalized not in {"H4", "D1"}:
            raise ValueError(f"Unsupported historical timeframe: {timeframe}")
        if normalized not in self._resampled_price:
            rule = "4h" if normalized == "H4" else "1D"
            source = self.price_by_timeframe["H1"]
            aggregations: dict[str, str] = {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
            }
            if "tick_volume" in source.columns:
                aggregations["tick_volume"] = "sum"
            self._resampled_price[normalized] = source.resample(rule).agg(aggregations).dropna(subset=["open", "close"])
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
                VALUES('chart_annotation_schema_version', '4', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at_utc=excluded.updated_at_utc
                WHERE schema_meta.value <> excluded.value
                """,
                (utc_now(),),
            )
            connection.commit()

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
            if key != "pricePath" and not path.is_relative_to(root):
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
        for timeframe in ("M30", "H1", "H4", "D1"):
            frame = self._price_for_timeframe(timeframe)
            ranges[timeframe] = {
                "start": frame.index.min().isoformat(),
                "end": frame.index.max().isoformat(),
            }
        transit_bodies = list(SUPPORTED_ASTRO_ENTITIES)
        natal_bodies = list(SUPPORTED_ASTRO_ENTITIES)
        aspects = list(SUPPORTED_ASPECTS)
        return {
            "defaults": DEFAULT_CHART_PARAMETERS,
            "options": {
                "symbols": ["USDJPY"],
                "timeframes": ["M30", "H1", "H4", "D1"],
                "modes": [
                    {"id": "TN", "label": "Transit to natal", "available": True},
                    {"id": "TT", "label": "Transit to transit", "available": False},
                ],
                "transitBodies": transit_bodies,
                "natalBodies": natal_bodies,
                "aspects": aspects,
                "familyKeys": sorted(self.family_counts),
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
        min_duration_minutes: float = 0.0,
        max_duration_minutes: float | None = None,
    ) -> dict[str, Any]:
        symbol = symbol.upper().strip()
        timeframe = timeframe.upper().strip()
        if symbol != "USDJPY":
            raise ValueError("The corrected historical source currently supports USDJPY only")
        price_source = self._price_for_timeframe(timeframe)
        start_local = parse_local_timestamp(start, "2025-05-25T00:00:00+05:30")
        end_local = parse_local_timestamp(end, "2025-05-31T23:59:59+05:30")
        if end_local <= start_local:
            raise ValueError("end must be later than start")
        start_utc = start_local.tz_convert(UTC)
        end_utc = end_local.tz_convert(UTC)
        price = price_source.loc[(price_source.index >= start_utc) & (price_source.index <= end_utc)]
        if len(price) > 50_000:
            raise ValueError("Chart request exceeds 50,000 candles; narrow the date range or use a larger timeframe")
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
        overlapping = overlapping.loc[pd.to_numeric(overlapping["duration_minutes"], errors="coerce") >= min_duration_minutes]
        if max_duration_minutes is not None:
            overlapping = overlapping.loc[
                pd.to_numeric(overlapping["duration_minutes"], errors="coerce") <= max_duration_minutes
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
            "dataSource": "corrected_historical",
            "parametersApplied": {
                "transitBodies": list(transit_bodies or ()),
                "natalBodies": list(natal_bodies or ()),
                "aspects": list(aspects or ()),
                "excludedFamilyKeys": list(excluded_family_keys or ()),
                "onlyTouched": only_touched,
                "minDurationMinutes": min_duration_minutes,
                "maxDurationMinutes": max_duration_minutes,
            },
            "artifact": self.active_artifact,
            "generatedAt": utc_now(),
        }

    @synchronized_dataset
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
            "artifact": self.active_artifact,
        }

    @synchronized_dataset
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
