from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import pandas as pd

from repository import (
    ASTRO_CONTRACT,
    DEFAULT_CHART_PARAMETERS,
    SUPPORTED_ASPECTS,
    SUPPORTED_ASTRO_ENTITIES as SUPPORTED_ENTITIES,
    AstroRepository,
    utc_now,
)
ACTIVE_JOB_STATUSES = {"queued", "running", "cancelling"}


class JobCancelled(RuntimeError):
    pass


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _timestamp(value: Any, name: str) -> pd.Timestamp:
    try:
        parsed = pd.Timestamp(value)
    except Exception as exc:
        raise ValueError(f"{name} is not a valid timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.tz_localize("Asia/Kolkata")
    return parsed.tz_convert("Asia/Kolkata")


def _string_list(value: Any, allowed: tuple[str, ...], name: str) -> list[str]:
    if not value:
        return list(allowed)
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be a list")
    normalized = list(dict.fromkeys(str(item).upper().strip() for item in value if str(item).strip()))
    unknown = sorted(set(normalized) - set(allowed))
    if unknown:
        raise ValueError(f"Unsupported {name}: {unknown}")
    if not normalized:
        raise ValueError(f"At least one {name} value is required")
    return normalized


def _number_list(
    value: Any,
    default: list[float],
    name: str,
    maximum_items: int,
) -> list[float]:
    raw = value if isinstance(value, (list, tuple)) else default
    try:
        normalized = list(dict.fromkeys(float(item) for item in raw))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} contains a non-numeric value") from exc
    if not normalized or len(normalized) > maximum_items or any(item <= 0 for item in normalized):
        raise ValueError(f"{name} must contain 1-{maximum_items} positive values")
    return normalized


def normalize_generation_parameters(repository: AstroRepository, value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("parameters are required")
    merged = {**DEFAULT_CHART_PARAMETERS, **value}
    merged["reference"] = {**DEFAULT_CHART_PARAMETERS["reference"], **(value.get("reference") or {})}
    symbol = str(merged.get("symbol") or "").upper().strip()
    if symbol != "USDJPY":
        raise ValueError("Corrected background generation currently supports USDJPY only")
    if str(merged.get("mode") or "").upper() != "TN":
        raise ValueError("The corrected transit-to-transit generator is not implemented")
    if str(merged.get("dataSource") or "research").lower() != "research":
        raise ValueError("Generate corrected sources from Research mode, not the live-bar view")
    timeframe = str(merged.get("timeframe") or "H1").upper()
    if timeframe not in {"M30", "H1", "H4", "D1"}:
        raise ValueError(f"Unsupported generation timeframe: {timeframe}")

    start = _timestamp(merged.get("start"), "start")
    end = _timestamp(merged.get("end"), "end")
    if end <= start:
        raise ValueError("end must be later than start")
    if end - start > pd.Timedelta(days=366 * 5):
        raise ValueError("A generation job is limited to five years; split larger research ranges")
    source_timeframe = "M30" if timeframe == "M30" else "H1"
    source = repository.price_by_timeframe[source_timeframe]
    start_utc = start.tz_convert("UTC")
    end_utc = end.tz_convert("UTC")
    if start_utc < source.index.min() or end_utc > source.index.max():
        raise ValueError(
            "Requested generation range is outside the versioned price source: "
            f"{source.index.min().isoformat()} to {source.index.max().isoformat()}"
        )

    transit_bodies = _string_list(merged.get("transitBodies"), SUPPORTED_ENTITIES, "transit bodies")
    natal_bodies = _string_list(merged.get("natalBodies"), SUPPORTED_ENTITIES, "natal bodies")
    aspects = [
        item.lower()
        for item in _string_list(merged.get("aspects"), tuple(item.upper() for item in SUPPORTED_ASPECTS), "aspects")
    ]
    harmonics = _number_list(merged.get("harmonics"), [0.12, 0.18], "harmonics", 40)
    n_values = _number_list(merged.get("nValues"), [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8], "n values", 40)
    degree_values = _number_list(merged.get("degrees"), [360, 180, 90, 45], "degrees", 20)
    degrees = list(dict.fromkeys(int(item) for item in degree_values))
    if any(item <= 0 or item > 360 for item in degrees):
        raise ValueError("degrees must be integers in the range 1-360")
    if len(harmonics) * len(n_values) * len(degrees) > 400:
        raise ValueError("harmonic x n x degree combinations exceed the safe limit of 400")
    epsilon = float(merged.get("epsilon", 0.30))
    price_zone = float(merged.get("priceZone", 0.16))
    if not 0 < epsilon <= 10 or not 0 < price_zone <= 10:
        raise ValueError("epsilon and price zone must be greater than 0 and no more than 10")

    reference = merged["reference"]
    date = str(reference.get("date") or "").strip()
    time_text = str(reference.get("time") or "").strip()
    offset = str(reference.get("utcOffset") or "").strip()
    _timestamp(f"{date}T{time_text}{offset}", "reference date/time")
    latitude = float(reference.get("latitude"))
    longitude = float(reference.get("longitude"))
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("reference latitude/longitude are outside valid bounds")

    normalized = {
        **merged,
        "symbol": symbol,
        "dataSource": "research",
        "timeframe": timeframe,
        "sourceTimeframe": source_timeframe,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "mode": "TN",
        "transitBodies": transit_bodies,
        "natalBodies": natal_bodies,
        "aspects": aspects,
        "harmonics": harmonics,
        "nValues": n_values,
        "degrees": degrees,
        "epsilon": epsilon,
        "priceZone": price_zone,
        "reference": {
            "label": str(reference.get("label") or "Custom reference")[:160],
            "date": date,
            "time": time_text,
            "utcOffset": offset,
            "latitude": latitude,
            "longitude": longitude,
        },
    }
    return normalized


class GenerationJobManager:
    def __init__(self, repository: AstroRepository, autostart: bool = True) -> None:
        self.repository = repository
        self.project_root = repository.paths.project_root
        self.artifacts_root = repository.paths.artifacts_dir
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._process_lock = threading.RLock()
        self._current_process: subprocess.Popen[Any] | None = None
        self._thread: threading.Thread | None = None
        self._recover_interrupted_jobs()
        if autostart:
            self.start()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._worker_loop, name="astro-generation-worker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        with self._process_lock:
            process = self._current_process
        if process and process.poll() is None:
            process.terminate()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def _recover_interrupted_jobs(self) -> None:
        now = utc_now()
        with self.repository.connect() as connection:
            connection.execute(
                """
                UPDATE app_generation_jobs
                SET status = 'failed', stage = 'interrupted', progress = 0,
                    message = 'Backend restarted before this job completed.',
                    error = 'Interrupted by backend restart.', finished_at_utc = ?, updated_at_utc = ?
                WHERE status IN ('running', 'cancelling')
                """,
                (now, now),
            )
            connection.commit()

    @staticmethod
    def _job_record(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        try:
            parameters = json.loads(str(item.get("parameters_json") or "{}"))
        except json.JSONDecodeError:
            parameters = {}
        return {
            "jobId": str(item["job_id"]),
            "label": str(item["label"]),
            "status": str(item["status"]),
            "stage": str(item["stage"]),
            "progress": float(item["progress"]),
            "message": str(item["message"]),
            "parameters": parameters if isinstance(parameters, dict) else {},
            "autoActivate": bool(item["auto_activate"]),
            "cancelRequested": bool(item["cancel_requested"]),
            "artifactId": item["artifact_id"],
            "eventsPath": str(item["events_path"]),
            "touchLogPath": str(item["touch_log_path"]),
            "logPath": str(item["log_path"]),
            "error": str(item["error"]),
            "createdAtUtc": str(item["created_at_utc"]),
            "startedAtUtc": item["started_at_utc"],
            "finishedAtUtc": item["finished_at_utc"],
            "updatedAtUtc": str(item["updated_at_utc"]),
        }

    def list_jobs(self, limit: int = 30) -> list[dict[str, Any]]:
        with self.repository.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM app_generation_jobs ORDER BY created_at_utc DESC LIMIT ?",
                (max(1, min(int(limit), 100)),),
            ).fetchall()
        return [self._job_record(row) for row in rows]

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self.repository.connect() as connection:
            row = connection.execute(
                "SELECT * FROM app_generation_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown generation job: {job_id}")
        record = self._job_record(row)
        log_path = Path(record["logPath"]) if record["logPath"] else None
        record["logTail"] = self._tail(log_path) if log_path else ""
        return record

    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        parameters = normalize_generation_parameters(self.repository, payload.get("parameters"))
        label = str(payload.get("label") or "").strip()[:120]
        if not label:
            start = pd.Timestamp(parameters["start"]).strftime("%Y-%m-%d")
            end = pd.Timestamp(parameters["end"]).strftime("%Y-%m-%d")
            label = f"USDJPY TN {start} to {end}"
        job_id = uuid.uuid4().hex
        now = utc_now()
        with self.repository.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_generation_jobs(
                    job_id, label, status, stage, progress, message, parameters_json,
                    auto_activate, created_at_utc, updated_at_utc
                ) VALUES(?, ?, 'queued', 'queued', 0, 'Waiting for the background worker.', ?, ?, ?, ?)
                """,
                (
                    job_id,
                    label,
                    json.dumps(parameters, ensure_ascii=True, sort_keys=True, default=str),
                    int(bool(payload.get("autoActivate", True))),
                    now,
                    now,
                ),
            )
            connection.commit()
        self._wake.set()
        return self.get_job(job_id)

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        now = utc_now()
        with self.repository.connect() as connection:
            row = connection.execute(
                "SELECT status FROM app_generation_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown generation job: {job_id}")
            status = str(row["status"])
            if status == "queued":
                connection.execute(
                    """
                    UPDATE app_generation_jobs
                    SET status = 'cancelled', stage = 'cancelled', cancel_requested = 1,
                        message = 'Cancelled before generation started.', progress = 0,
                        finished_at_utc = ?, updated_at_utc = ?
                    WHERE job_id = ?
                    """,
                    (now, now, job_id),
                )
            elif status in {"running", "cancelling"}:
                connection.execute(
                    """
                    UPDATE app_generation_jobs
                    SET status = 'cancelling', cancel_requested = 1,
                        message = 'Stopping the active generator.', updated_at_utc = ?
                    WHERE job_id = ?
                    """,
                    (now, job_id),
                )
            connection.commit()
        self._wake.set()
        return self.get_job(job_id)

    def _claim_next_job(self) -> dict[str, Any] | None:
        with self.repository.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT * FROM app_generation_jobs
                WHERE status = 'queued' AND cancel_requested = 0
                ORDER BY created_at_utc, job_id LIMIT 1
                """
            ).fetchone()
            if row is None:
                connection.commit()
                return None
            now = utc_now()
            connection.execute(
                """
                UPDATE app_generation_jobs
                SET status = 'running', stage = 'preparing', progress = 2,
                    message = 'Preparing isolated artifact paths.', started_at_utc = ?, updated_at_utc = ?
                WHERE job_id = ? AND status = 'queued'
                """,
                (now, now, row["job_id"]),
            )
            connection.commit()
        return self.get_job(str(row["job_id"]))

    def _worker_loop(self) -> None:
        while not self._stop.is_set():
            job = self._claim_next_job()
            if job is None:
                self._wake.wait(timeout=1.0)
                self._wake.clear()
                continue
            self._run_job(job)

    def _update_job(self, job_id: str, **values: Any) -> None:
        allowed = {
            "status",
            "stage",
            "progress",
            "message",
            "artifact_id",
            "events_path",
            "touch_log_path",
            "log_path",
            "error",
            "finished_at_utc",
        }
        updates = {key: value for key, value in values.items() if key in allowed}
        updates["updated_at_utc"] = utc_now()
        assignments = ", ".join(f"{key} = ?" for key in updates)
        with self.repository.connect() as connection:
            connection.execute(
                f"UPDATE app_generation_jobs SET {assignments} WHERE job_id = ?",
                (*updates.values(), job_id),
            )
            connection.commit()

    def _cancel_requested(self, job_id: str) -> bool:
        with self.repository.connect() as connection:
            row = connection.execute(
                "SELECT cancel_requested FROM app_generation_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        return bool(row and row["cancel_requested"])

    def _run_command(self, job_id: str, command: list[str], log_path: Path) -> None:
        with log_path.open("a", encoding="utf-8", errors="replace") as log:
            log.write(f"\n$ {subprocess.list2cmdline(command)}\n")
            log.flush()
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            process = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creationflags,
            )
            with self._process_lock:
                self._current_process = process
            try:
                while process.poll() is None:
                    if self._stop.is_set() or self._cancel_requested(job_id):
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        raise JobCancelled("Generation cancelled by the user.")
                    time.sleep(0.25)
                if process.returncode:
                    raise RuntimeError(
                        f"Generator exited with code {process.returncode}.\n{self._tail(log_path)}"
                    )
            finally:
                with self._process_lock:
                    self._current_process = None

    def _worker_command(self, script_name: str, arguments: list[str]) -> list[str]:
        if getattr(sys, "frozen", False):
            return [sys.executable, "--gann-worker", script_name, *arguments]
        return [sys.executable, str(self.project_root / script_name), *arguments]

    @staticmethod
    def _tail(path: Path | None, maximum: int = 6000) -> str:
        if path is None or not path.exists():
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[-maximum:]

    def _run_job(self, job: dict[str, Any]) -> None:
        job_id = job["jobId"]
        parameters = job["parameters"]
        artifact_id = f"tn_{job_id}"
        artifact_dir = self.artifacts_root / artifact_id
        events_path = artifact_dir / "events.parquet"
        touch_path = artifact_dir / "touches.csv"
        touch_partial = artifact_dir / "touches.partial.csv"
        log_path = artifact_dir / "generation.log"
        sr_config_path = artifact_dir / "sr_config.json"
        artifact_manifest_path = artifact_dir / "artifact.manifest.json"
        events_manifest_path = events_path.with_suffix(".manifest.json")
        source_timeframe = parameters["sourceTimeframe"]
        price_path = (
            self.repository.paths.price_data_m30
            if source_timeframe == "M30"
            else self.repository.paths.price_data
        )
        interval = "30m" if source_timeframe == "M30" else "1h"
        sr_config = {
            "harmonics": parameters["harmonics"],
            "n_values": parameters["nValues"],
            "degrees": parameters["degrees"],
            "epsilon": parameters["epsilon"],
            "price_zone": parameters["priceZone"],
            "moon_factor": 1.8,
            "band_pct": 0.01,
        }
        start_date = pd.Timestamp(parameters["start"]).strftime("%Y-%m-%d")
        end_date = pd.Timestamp(parameters["end"]).strftime("%Y-%m-%d")
        reference = parameters["reference"]
        try:
            artifact_dir.mkdir(parents=True, exist_ok=False)
            sr_config_path.write_text(
                json.dumps(sr_config, indent=2, sort_keys=True, ensure_ascii=True), encoding="utf-8"
            )
            self._update_job(
                job_id,
                events_path=str(events_path),
                touch_log_path=str(touch_path),
                log_path=str(log_path),
            )
            self._update_job(
                job_id,
                stage="events",
                progress=10,
                message="Generating corrected Raman transit-to-natal aspect windows.",
            )
            event_command = self._worker_command("build_corrected_natal_event_source.py", [
                "--ticker",
                parameters["symbol"],
                "--interval",
                interval,
                "--price-parquet",
                str(price_path),
                "--start-date",
                start_date,
                "--end-date",
                end_date,
                "--transit-entities",
                ",".join(parameters["transitBodies"]),
                "--natal-entities",
                ",".join(parameters["natalBodies"]),
                "--selected-aspects",
                ",".join(parameters["aspects"]),
                "--reference-date",
                reference["date"],
                "--reference-time",
                reference["time"],
                "--reference-utc-offset",
                reference["utcOffset"],
                "--reference-label",
                reference["label"],
                "--reference-lat",
                str(reference["latitude"]),
                "--reference-lon",
                str(reference["longitude"]),
                "--min-window-minutes",
                str(max(30.0, float(parameters.get("minDurationMinutes") or 0))),
                "--sr-config-file",
                str(sr_config_path),
                "--output",
                str(events_path),
                "--overwrite",
            ])
            self._run_command(job_id, event_command, log_path)
            events = self.repository._load_event_frame(events_path)

            self._update_job(
                job_id,
                stage="sr_touches",
                progress=55,
                message=f"Generated {len(events)} events; calculating deterministic SR touches.",
            )
            max_days = float(parameters.get("maxDurationMinutes") or 0) / 1440.0
            touch_command = self._worker_command("build_aspect_sr_touch_log.py", [
                "--events",
                str(events_path),
                "--price",
                str(price_path),
                "--output",
                str(touch_partial),
                "--interval",
                interval,
                "--aspect-mode",
                "orb",
                "--include-natal",
                "--ipo-date",
                reference["date"],
                "--ipo-time",
                reference["time"],
                "--reference-tz",
                reference["utcOffset"],
                "--reference-lat",
                str(reference["latitude"]),
                "--reference-lon",
                str(reference["longitude"]),
                "--quote-reference-label",
                parameters["symbol"][-3:],
                "--max-event-days",
                str(max_days),
                "--allow-empty",
            ])
            self._run_command(job_id, touch_command, log_path)
            touch_partial.replace(touch_path)
            touches = self.repository._load_touch_frame(touch_path)

            self._update_job(
                job_id,
                stage="registering",
                progress=92,
                message="Validating manifests and registering the completed artifact.",
            )
            manifest = {
                "artifact_id": artifact_id,
                "label": job["label"],
                "created_at_utc": utc_now(),
                "astronomy_contract": ASTRO_CONTRACT,
                "event_count": int(len(events)),
                "touch_count": int(len(touches)),
                "event_start": pd.Timestamp(events["timestamp"].min()).isoformat(),
                "event_end": pd.Timestamp(events["event_end"].max()).isoformat(),
                "events_sha256": file_sha256(events_path),
                "touches_sha256": file_sha256(touch_path),
                "price_source_sha256": file_sha256(price_path),
                "parameters": parameters,
                "outcome_labels_included": False,
            }
            temporary_manifest = artifact_manifest_path.with_suffix(".json.tmp")
            temporary_manifest.write_text(
                json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True), encoding="utf-8"
            )
            temporary_manifest.replace(artifact_manifest_path)
            artifact = self.repository.register_data_artifact(
                {
                    "artifactId": artifact_id,
                    "label": job["label"],
                    "symbol": parameters["symbol"],
                    "mode": "TN",
                    "sourceTimeframe": source_timeframe,
                    "eventsPath": str(events_path),
                    "touchLogPath": str(touch_path),
                    "pricePath": str(price_path),
                    "eventsManifestPath": str(events_manifest_path),
                    "artifactManifestPath": str(artifact_manifest_path),
                    "parameters": parameters,
                    "astronomyContract": ASTRO_CONTRACT,
                    "eventCount": len(events),
                    "touchCount": len(touches),
                    "dateStart": manifest["event_start"],
                    "dateEnd": manifest["event_end"],
                }
            )
            if job["autoActivate"]:
                artifact = self.repository.activate_artifact(artifact_id)
            finished = utc_now()
            self._update_job(
                job_id,
                status="completed",
                stage="completed",
                progress=100,
                message=(
                    f"Ready: {len(events)} events, {len(touches)} SR touches"
                    + ("; dataset activated." if artifact["isActive"] else ".")
                ),
                artifact_id=artifact_id,
                finished_at_utc=finished,
            )
        except JobCancelled as exc:
            self._update_job(
                job_id,
                status="cancelled",
                stage="cancelled",
                message=str(exc),
                error="",
                finished_at_utc=utc_now(),
            )
        except Exception as exc:
            self._update_job(
                job_id,
                status="failed",
                stage="failed",
                message="Generation failed. Open the job log for the exact generator output.",
                error=str(exc)[-6000:],
                finished_at_utc=utc_now(),
            )
