from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd


REFRESH_CONTRACT = "GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1"
ACTIVE_GENERATION_STATUSES = {"queued", "running", "cancelling"}
SOURCE_TIMEFRAMES = {"M30": pd.Timedelta(minutes=30), "H1": pd.Timedelta(hours=1)}


def _utc_timestamp(value: Any, label: str) -> pd.Timestamp:
    timestamp = pd.Timestamp(value if value is not None else datetime.now(timezone.utc))
    if timestamp.tzinfo is None:
        raise ValueError(f"{label} must include a UTC offset")
    return timestamp.tz_convert("UTC")


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ProspectiveArtifactRefreshSupervisor:
    """Refreshes the corrected research artifact after newly closed MT5 bars.

    This is an operational pipeline, not a trading engine. It cannot place orders and it
    never backdates a capture. A refresh is eligible only while the latest closed market bar
    is still fresh enough for the prospective shadow ledger.
    """

    def __init__(
        self,
        repository: Any,
        gateway: Any,
        generation_manager: Any,
        shadow_ledger: Any,
        *,
        autostart: bool = True,
        poll_seconds: float = 20.0,
        lookback_days: int = 14,
        close_grace_seconds: int = 90,
    ) -> None:
        self.repository = repository
        self.gateway = gateway
        self.generation_manager = generation_manager
        self.shadow_ledger = shadow_ledger
        self.poll_seconds = max(5.0, float(poll_seconds))
        self.lookback_days = max(3, min(int(lookback_days), 90))
        self.close_grace_seconds = max(15, min(int(close_grace_seconds), 600))
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._run_lock = threading.RLock()
        self._status_lock = threading.RLock()
        self._thread: threading.Thread | None = None
        self._force_requested = False
        self._status: dict[str, Any] = {
            "contract": REFRESH_CONTRACT,
            "enabled": bool(autostart),
            "state": "starting" if autostart else "paused",
            "message": "Preparing the prospective refresh supervisor." if autostart else "Automatic refresh is paused.",
            "lastCheckedAtUtc": None,
            "latestClosedBarUtc": None,
            "activeRun": None,
            "lastError": "",
            "executionAllowed": False,
        }
        self._initialize_schema()
        self._recover_interrupted_runs()
        self._repair_completed_run_parameters()
        if autostart:
            self.start()

    def _initialize_schema(self) -> None:
        with self.repository.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_prospective_refresh_runs (
                    run_id TEXT PRIMARY KEY,
                    contract TEXT NOT NULL,
                    source_bar_open_utc TEXT NOT NULL,
                    source_bar_close_utc TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    message TEXT NOT NULL DEFAULT '',
                    source_snapshot_id TEXT,
                    price_source_id TEXT,
                    generation_job_id TEXT,
                    artifact_id TEXT,
                    parameters_json TEXT NOT NULL DEFAULT '{}',
                    error TEXT NOT NULL DEFAULT '',
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL,
                    finished_at_utc TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_app_prospective_refresh_runs_created
                    ON app_prospective_refresh_runs(created_at_utc DESC);
                """
            )
            connection.execute(
                """
                INSERT INTO schema_meta(key, value, updated_at_utc)
                VALUES('prospective_refresh_schema_version', '1', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at_utc=excluded.updated_at_utc
                WHERE schema_meta.value <> excluded.value
                """,
                (_utc_now_text(),),
            )
            connection.commit()

    def _recover_interrupted_runs(self) -> None:
        now = _utc_now_text()
        with self.repository.connect() as connection:
            connection.execute(
                """
                UPDATE app_prospective_refresh_runs
                SET status = 'failed', stage = 'interrupted',
                    message = 'Backend restarted before snapshot promotion completed.',
                    error = 'Interrupted before a durable generation job was queued.',
                    updated_at_utc = ?, finished_at_utc = ?
                WHERE status = 'running' AND generation_job_id IS NULL
                """,
                (now, now),
            )
            connection.commit()

    def _repair_completed_run_parameters(self) -> int:
        """Backfill audit rows only when their verified artifact proves the lineage."""
        artifacts = {
            str(item.get("artifactId")): item
            for item in self.repository.list_data_artifacts()
            if item.get("artifactId") and isinstance(item.get("parameters"), dict)
        }
        with self.repository.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM app_prospective_refresh_runs
                WHERE status = 'completed' AND artifact_id IS NOT NULL
                """
            ).fetchall()
        repaired = 0
        for row in rows:
            run = self._run_record(row)
            artifact = artifacts.get(str(run.get("artifactId") or ""))
            if artifact is None:
                continue
            parameters = artifact["parameters"]
            refresh = parameters.get("prospectiveRefresh")
            if not isinstance(refresh, dict) or refresh.get("contract") != REFRESH_CONTRACT:
                continue
            try:
                same_close = _utc_timestamp(
                    refresh.get("sourceBarCloseUtc"),
                    "artifact source bar close",
                ) == _utc_timestamp(run["sourceBarCloseUtc"], "run source bar close")
            except (TypeError, ValueError):
                continue
            same_source = (
                not run.get("priceSourceId")
                or str(parameters.get("priceSourceId") or "") == str(run["priceSourceId"])
            )
            if refresh.get("runId") != run["runId"] or not same_close or not same_source:
                continue
            if run.get("parameters") == parameters:
                continue
            self._update_run(
                run["runId"],
                parameters_json=json.dumps(
                    parameters,
                    ensure_ascii=True,
                    sort_keys=True,
                    default=str,
                ),
            )
            repaired += 1
        return repaired

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._worker_loop,
            name="prospective-artifact-refresh",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def request_refresh(self) -> dict[str, Any]:
        self._force_requested = True
        self._wake.set()
        return self.status()

    def _set_status(self, **values: Any) -> None:
        with self._status_lock:
            self._status.update(values)

    @staticmethod
    def _run_record(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        try:
            parameters = json.loads(str(item.get("parameters_json") or "{}"))
        except json.JSONDecodeError:
            parameters = {}
        return {
            "runId": str(item["run_id"]),
            "contract": str(item["contract"]),
            "sourceBarOpenUtc": str(item["source_bar_open_utc"]),
            "sourceBarCloseUtc": str(item["source_bar_close_utc"]),
            "status": str(item["status"]),
            "stage": str(item["stage"]),
            "message": str(item["message"]),
            "sourceSnapshotId": item.get("source_snapshot_id"),
            "priceSourceId": item.get("price_source_id"),
            "generationJobId": item.get("generation_job_id"),
            "artifactId": item.get("artifact_id"),
            "parameters": parameters if isinstance(parameters, dict) else {},
            "error": str(item.get("error") or ""),
            "createdAtUtc": str(item["created_at_utc"]),
            "updatedAtUtc": str(item["updated_at_utc"]),
            "finishedAtUtc": item.get("finished_at_utc"),
        }

    def recent_runs(self, limit: int = 8) -> list[dict[str, Any]]:
        with self.repository.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM app_prospective_refresh_runs
                ORDER BY source_bar_close_utc DESC LIMIT ?
                """,
                (max(1, min(int(limit), 50)),),
            ).fetchall()
        return [self._run_record(row) for row in rows]

    def _run_for_close(self, source_bar_close: pd.Timestamp) -> dict[str, Any] | None:
        with self.repository.connect() as connection:
            row = connection.execute(
                "SELECT * FROM app_prospective_refresh_runs WHERE source_bar_close_utc = ?",
                (source_bar_close.isoformat(),),
            ).fetchone()
        return self._run_record(row) if row else None

    def _insert_run(
        self,
        source_bar_open: pd.Timestamp,
        source_bar_close: pd.Timestamp,
    ) -> dict[str, Any]:
        run_id = uuid.uuid4().hex
        now = _utc_now_text()
        with self.repository.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_prospective_refresh_runs(
                    run_id, contract, source_bar_open_utc, source_bar_close_utc,
                    status, stage, message, created_at_utc, updated_at_utc
                ) VALUES(?, ?, ?, ?, 'running', 'capturing',
                    'Capturing immutable closed MT5 bars.', ?, ?)
                """,
                (
                    run_id,
                    REFRESH_CONTRACT,
                    source_bar_open.isoformat(),
                    source_bar_close.isoformat(),
                    now,
                    now,
                ),
            )
            connection.commit()
        return self._run_for_close(source_bar_close) or {}

    def _update_run(self, run_id: str, **values: Any) -> None:
        allowed = {
            "status",
            "stage",
            "message",
            "source_snapshot_id",
            "price_source_id",
            "generation_job_id",
            "artifact_id",
            "parameters_json",
            "error",
            "finished_at_utc",
        }
        updates = {key: value for key, value in values.items() if key in allowed}
        updates["updated_at_utc"] = _utc_now_text()
        assignments = ", ".join(f"{key} = ?" for key in updates)
        with self.repository.connect() as connection:
            connection.execute(
                f"UPDATE app_prospective_refresh_runs SET {assignments} WHERE run_id = ?",
                (*updates.values(), run_id),
            )
            connection.commit()

    def _latest_closed_bar(
        self,
        symbol: str,
        timeframe: str,
        now: pd.Timestamp,
    ) -> tuple[pd.Timestamp, pd.Timestamp, float]:
        delta = SOURCE_TIMEFRAMES[timeframe]
        bars = self.gateway.bars(symbol, timeframe, count=30)
        candidates: list[tuple[pd.Timestamp, pd.Timestamp, float]] = []
        for bar in bars:
            opened = pd.Timestamp(int(bar["time"]), unit="s", tz="UTC")
            closed = opened + delta
            if closed <= now:
                candidates.append((opened, closed, float(bar["close"])))
        if not candidates:
            raise RuntimeError("MT5 has not returned a fully closed source bar")
        return max(candidates, key=lambda item: item[0])

    def _active_last_bar_close(self, timeframe: str) -> pd.Timestamp | None:
        artifact = self.repository.active_artifact
        if bool(artifact.get("builtIn")):
            return None
        parameters = artifact.get("parameters") or {}
        raw = parameters.get("priceSourceLastBarCloseUtc")
        if raw:
            return _utc_timestamp(raw, "active price source last bar close")
        frame = self.repository.price_by_timeframe.get(timeframe)
        if frame is None or frame.empty:
            return None
        return pd.Timestamp(frame.index.max()).tz_convert("UTC") + SOURCE_TIMEFRAMES[timeframe]

    def _generation_is_busy(self) -> bool:
        return any(
            str(job.get("status")) in ACTIVE_GENERATION_STATUSES
            for job in self.generation_manager.list_jobs(20)
        )

    def _reconcile_run(self, run: dict[str, Any]) -> bool:
        job_id = str(run.get("generationJobId") or "")
        if not job_id:
            return False
        try:
            job = self.generation_manager.get_job(job_id)
        except Exception as exc:
            self._set_status(state="error", message="Refresh job cannot be read.", lastError=str(exc))
            return True
        status = str(job.get("status") or "")
        if status in ACTIVE_GENERATION_STATUSES:
            self._update_run(
                run["runId"],
                status="running",
                stage="generating",
                message=f"Corrected artifact {job.get('progress', 0):.0f}%: {job.get('message') or status}",
            )
            self._set_status(
                state="generating",
                message=str(job.get("message") or "Generating corrected artifact."),
                activeRun=self._run_for_close(_utc_timestamp(run["sourceBarCloseUtc"], "source bar close")),
                lastError="",
            )
            return True
        if status == "completed":
            finished = _utc_now_text()
            artifact_id = str(job.get("artifactId") or "")
            artifact_parameters: dict[str, Any] | None = None
            if artifact_id:
                artifact = next(
                    (
                        item
                        for item in self.repository.list_data_artifacts()
                        if str(item.get("artifactId")) == artifact_id
                    ),
                    None,
                )
                if artifact and isinstance(artifact.get("parameters"), dict):
                    artifact_parameters = artifact["parameters"]
            self._update_run(
                run["runId"],
                status="completed",
                stage="completed",
                message="Fresh corrected artifact activated; shadow ledger scan requested.",
                artifact_id=artifact_id,
                **(
                    {
                        "parameters_json": json.dumps(
                            artifact_parameters,
                            ensure_ascii=True,
                            sort_keys=True,
                            default=str,
                        )
                    }
                    if artifact_parameters is not None
                    else {}
                ),
                error="",
                finished_at_utc=finished,
            )
            try:
                self.shadow_ledger.scan_once()
            except Exception as exc:
                self._set_status(lastError=f"Artifact completed, but shadow scan failed: {exc}")
            completed = self._run_for_close(_utc_timestamp(run["sourceBarCloseUtc"], "source bar close"))
            self._set_status(
                state="up_to_date",
                message="Latest closed MT5 bar has a verified corrected artifact.",
                activeRun=completed,
                lastError="",
            )
            return True
        if status in {"failed", "cancelled"}:
            error = str(job.get("error") or job.get("message") or "Generation did not complete")
            finished = _utc_now_text()
            self._update_run(
                run["runId"],
                status="failed",
                stage="generation_failed",
                message="Corrected artifact generation failed.",
                error=error[-6000:],
                finished_at_utc=finished,
            )
            self._set_status(state="error", message="Corrected artifact generation failed.", lastError=error)
            return True
        return False

    def _refresh_parameters(
        self,
        price_source: dict[str, Any],
        source_bar_open: pd.Timestamp,
        source_bar_close: pd.Timestamp,
        run_id: str,
    ) -> dict[str, Any]:
        artifact = self.repository.active_artifact
        active = artifact.get("parameters") if isinstance(artifact.get("parameters"), dict) else {}
        parameters = dict(active or {})
        start = source_bar_open - pd.Timedelta(days=self.lookback_days)
        previous_start = parameters.get("start")
        if previous_start:
            parsed_start = pd.Timestamp(previous_start)
            if parsed_start.tzinfo is None:
                parsed_start = parsed_start.tz_localize("Asia/Kolkata")
            parsed_start = parsed_start.tz_convert("UTC")
            if parsed_start > start and parsed_start < source_bar_open:
                start = parsed_start
        parameters.update(
            {
                "symbol": str(artifact.get("symbol") or self.gateway.symbol or "USDJPY").upper(),
                "dataSource": "research",
                "mode": "TN",
                "timeframe": str(parameters.get("timeframe") or "H1").upper(),
                "priceSourceId": price_source["priceSourceId"],
                "priceSourceContract": price_source["contract"],
                "priceSourceSha256": price_source["priceSha256"],
                "priceSourceAsOfUtc": price_source["asOfUtc"],
                "priceSourceLastBarCloseUtc": source_bar_close.isoformat(),
                "start": start.tz_convert("Asia/Kolkata").isoformat(),
                "end": source_bar_open.tz_convert("Asia/Kolkata").isoformat(),
                "prospectiveRefresh": {
                    "contract": REFRESH_CONTRACT,
                    "runId": run_id,
                    "sourceBarOpenUtc": source_bar_open.isoformat(),
                    "sourceBarCloseUtc": source_bar_close.isoformat(),
                    "executionAllowed": False,
                },
            }
        )
        return parameters

    def run_once(self, observed_at: Any | None = None) -> dict[str, Any]:
        now = _utc_timestamp(observed_at, "observed_at") if observed_at is not None else _utc_timestamp(None, "now")
        with self._run_lock:
            self._set_status(lastCheckedAtUtc=now.isoformat())
            active_runs = [
                run for run in self.recent_runs(20)
                if run["status"] == "running" and run.get("generationJobId")
            ]
            if active_runs and self._reconcile_run(active_runs[0]):
                return self.status()

            artifact = self.repository.active_artifact
            source_timeframe = str(artifact.get("sourceTimeframe") or "H1").upper()
            if source_timeframe not in SOURCE_TIMEFRAMES:
                self._set_status(
                    state="waiting",
                    message=f"Source timeframe {source_timeframe} is not eligible for automatic refresh.",
                    lastError="",
                )
                return self.status()
            symbol = str(artifact.get("symbol") or self.gateway.symbol or "USDJPY").upper()
            try:
                source_open, source_close, _ = self._latest_closed_bar(symbol, source_timeframe, now)
            except Exception as exc:
                self._set_status(state="waiting", message="Waiting for closed MT5 bars.", lastError=str(exc))
                return self.status()
            self._set_status(latestClosedBarUtc=source_close.isoformat())
            delta = SOURCE_TIMEFRAMES[source_timeframe]
            age = now - source_close
            maximum_age = delta + pd.Timedelta(minutes=15)
            if age > maximum_age:
                self._set_status(
                    state="market_stale",
                    message="Latest closed MT5 bar is stale; market may be closed. No artifact was fabricated.",
                    activeRun=None,
                    lastError="",
                )
                return self.status()
            if age < pd.Timedelta(seconds=self.close_grace_seconds):
                self._set_status(
                    state="waiting_for_close",
                    message="Waiting briefly for MT5 to finalize the newly closed bar.",
                    activeRun=None,
                    lastError="",
                )
                return self.status()

            existing = self._run_for_close(source_close)
            if existing:
                if existing.get("generationJobId"):
                    self._reconcile_run(existing)
                elif existing["status"] == "failed":
                    self._set_status(
                        state="error",
                        message="This closed bar already has a failed refresh attempt; inspect the run before retrying.",
                        activeRun=existing,
                        lastError=existing.get("error") or "refresh failed",
                    )
                else:
                    self._set_status(
                        state="up_to_date",
                        message="Latest closed MT5 bar was already processed.",
                        activeRun=existing,
                        lastError="",
                    )
                return self.status()

            active_last_close = self._active_last_bar_close(source_timeframe)
            if active_last_close is not None and active_last_close >= source_close:
                self._set_status(
                    state="up_to_date",
                    message="Active corrected artifact already includes the latest closed MT5 bar.",
                    activeRun=None,
                    lastError="",
                )
                return self.status()
            if self._generation_is_busy():
                self._set_status(
                    state="waiting_for_generator",
                    message="A user or refresh generation job is already running.",
                    activeRun=None,
                    lastError="",
                )
                return self.status()

            run = self._insert_run(source_open, source_close)
            run_id = run["runId"]
            try:
                snapshot = self.gateway.save_history_snapshot(
                    symbol,
                    source_timeframe,
                    (source_open - pd.Timedelta(days=self.lookback_days)).to_pydatetime(),
                    now.to_pydatetime(),
                    self.repository.paths.market_snapshots_dir,
                    captured_at=now.to_pydatetime(),
                )
                self._update_run(
                    run_id,
                    stage="promoting",
                    message="Immutable snapshot captured; verifying promoted price source.",
                    source_snapshot_id=snapshot["snapshotId"],
                )
                price_source = self.repository.promote_history_snapshot(
                    snapshot["snapshotId"],
                    f"Prospective {symbol} {source_timeframe} through {source_close.isoformat()}",
                )
                parameters = self._refresh_parameters(
                    price_source,
                    source_open,
                    source_close,
                    run_id,
                )
                self._update_run(
                    run_id,
                    stage="queueing",
                    message="Price source verified; queueing corrected Raman artifact.",
                    price_source_id=price_source["priceSourceId"],
                    parameters_json=json.dumps(parameters, ensure_ascii=True, sort_keys=True, default=str),
                )
                job = self.generation_manager.create_job(
                    {
                        "label": f"Prospective {symbol} through {source_close.isoformat()}",
                        "parameters": parameters,
                        "autoActivate": True,
                    }
                )
                self._update_run(
                    run_id,
                    status="running",
                    stage="generating",
                    message="Corrected artifact generation queued.",
                    generation_job_id=job["jobId"],
                )
                current = self._run_for_close(source_close)
                self._set_status(
                    state="generating",
                    message="Corrected Raman artifact is generating in the background.",
                    activeRun=current,
                    lastError="",
                )
            except Exception as exc:
                finished = _utc_now_text()
                self._update_run(
                    run_id,
                    status="failed",
                    stage="failed",
                    message="Prospective refresh failed before activation.",
                    error=str(exc)[-6000:],
                    finished_at_utc=finished,
                )
                self._set_status(
                    state="error",
                    message="Prospective refresh failed before activation.",
                    activeRun=self._run_for_close(source_close),
                    lastError=str(exc),
                )
            return self.status()

    def status(self) -> dict[str, Any]:
        with self._status_lock:
            state = dict(self._status)
        state["recentRuns"] = self.recent_runs(8)
        return state

    def _worker_loop(self) -> None:
        while not self._stop.is_set():
            self._force_requested = False
            try:
                self.run_once()
            except Exception as exc:
                self._set_status(state="error", message="Refresh supervisor failed.", lastError=str(exc))
            self._wake.wait(self.poll_seconds)
            self._wake.clear()
