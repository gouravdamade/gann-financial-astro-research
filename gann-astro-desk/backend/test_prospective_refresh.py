from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pandas as pd

from prospective_refresh import ProspectiveArtifactRefreshSupervisor


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


class FakeRepository:
    def __init__(self, root: Path, *, active_last_close: str | None = None) -> None:
        self.db_path = root / "annotations.sqlite"
        with sqlite3.connect(self.db_path, factory=ClosingConnection) as connection:
            connection.execute(
                "CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT, updated_at_utc TEXT)"
            )
        self.paths = SimpleNamespace(
            annotation_db=self.db_path,
            market_snapshots_dir=root / "market_snapshots",
        )
        parameters: dict[str, Any] = {
            "start": "2026-07-01T00:00:00+05:30",
            "timeframe": "H1",
        }
        if active_last_close:
            parameters["priceSourceLastBarCloseUtc"] = active_last_close
        self.active_artifact = {
            "artifactId": "tn_old",
            "symbol": "USDJPY",
            "sourceTimeframe": "H1",
            "builtIn": False,
            "parameters": parameters,
        }
        index = pd.DatetimeIndex([pd.Timestamp("2026-07-13T08:00:00Z")])
        self.price_by_timeframe = {
            "H1": pd.DataFrame({"close": [145.0]}, index=index),
        }
        self.promotions: list[str] = []
        self.artifacts: list[dict[str, Any]] = []

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, factory=ClosingConnection)
        connection.row_factory = sqlite3.Row
        return connection

    def promote_history_snapshot(self, snapshot_id: str, label: str) -> dict[str, Any]:
        self.promotions.append(snapshot_id)
        return {
            "priceSourceId": f"mt5_{snapshot_id}",
            "sourceTimeframe": "H1",
            "symbol": "USDJPY",
            "contract": "PROMOTED_MT5_PRICE_SOURCE_V1",
            "priceSha256": "A" * 64,
            "asOfUtc": "2026-07-13T10:02:00+00:00",
        }

    def list_data_artifacts(self) -> list[dict[str, Any]]:
        return list(self.artifacts)


class FakeGateway:
    symbol = "USDJPY"

    def __init__(self) -> None:
        self.snapshot_calls = 0

    def bars(self, _symbol: str, _timeframe: str, count: int = 30) -> list[dict[str, Any]]:
        del count
        return [
            {"time": int(pd.Timestamp("2026-07-13T08:00:00Z").timestamp()), "close": 145.0},
            {"time": int(pd.Timestamp("2026-07-13T09:00:00Z").timestamp()), "close": 145.2},
            {"time": int(pd.Timestamp("2026-07-13T10:00:00Z").timestamp()), "close": 145.3},
        ]

    def save_history_snapshot(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        self.snapshot_calls += 1
        return {"snapshotId": "USDJPY_H1_fresh"}


class FakeGenerationManager:
    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, Any]] = {}
        self.created: list[dict[str, Any]] = []

    def list_jobs(self, _limit: int = 20) -> list[dict[str, Any]]:
        return list(self.jobs.values())

    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.created.append(payload)
        job = {
            "jobId": "job-1",
            "status": "queued",
            "progress": 0.0,
            "message": "queued",
            "artifactId": None,
            "error": "",
        }
        self.jobs[job["jobId"]] = job
        return job

    def get_job(self, job_id: str) -> dict[str, Any]:
        return dict(self.jobs[job_id])


class FakeShadowLedger:
    def __init__(self) -> None:
        self.scans = 0

    def scan_once(self) -> dict[str, Any]:
        self.scans += 1
        return {}


class ProspectiveRefreshTests(unittest.TestCase):
    def make_manager(
        self,
        root: Path,
        *,
        active_last_close: str | None = None,
    ) -> tuple[ProspectiveArtifactRefreshSupervisor, FakeRepository, FakeGateway, FakeGenerationManager, FakeShadowLedger]:
        repository = FakeRepository(root, active_last_close=active_last_close)
        gateway = FakeGateway()
        generation = FakeGenerationManager()
        shadow = FakeShadowLedger()
        manager = ProspectiveArtifactRefreshSupervisor(
            repository,
            gateway,
            generation,
            shadow,
            autostart=False,
            close_grace_seconds=90,
        )
        return manager, repository, gateway, generation, shadow

    def test_fresh_closed_bar_queues_one_idempotent_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manager, repository, gateway, generation, _shadow = self.make_manager(Path(temporary))
            status = manager.run_once("2026-07-13T10:02:00Z")
            self.assertEqual(status["state"], "generating")
            self.assertEqual(gateway.snapshot_calls, 1)
            self.assertEqual(repository.promotions, ["USDJPY_H1_fresh"])
            self.assertEqual(len(generation.created), 1)
            parameters = generation.created[0]["parameters"]
            self.assertEqual(parameters["priceSourceId"], "mt5_USDJPY_H1_fresh")
            self.assertEqual(parameters["priceSourceContract"], "PROMOTED_MT5_PRICE_SOURCE_V1")
            self.assertEqual(parameters["priceSourceSha256"], "A" * 64)
            self.assertEqual(parameters["priceSourceAsOfUtc"], "2026-07-13T10:02:00+00:00")
            self.assertEqual(parameters["priceSourceLastBarCloseUtc"], "2026-07-13T10:00:00+00:00")
            self.assertEqual(
                parameters["prospectiveRefresh"]["sourceBarCloseUtc"],
                "2026-07-13T10:00:00+00:00",
            )
            persisted = status["activeRun"]["parameters"]
            self.assertEqual(persisted["priceSourceLastBarCloseUtc"], "2026-07-13T10:00:00+00:00")
            manager.run_once("2026-07-13T10:03:00Z")
            self.assertEqual(gateway.snapshot_calls, 1)
            self.assertEqual(len(generation.created), 1)

    def test_completed_generation_wakes_shadow_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manager, repository, _gateway, generation, shadow = self.make_manager(Path(temporary))
            manager.run_once("2026-07-13T10:02:00Z")
            repository.artifacts.append(
                {
                    "artifactId": "tn_fresh",
                    "parameters": {
                        "priceSourceId": "mt5_USDJPY_H1_fresh",
                        "priceSourceLastBarCloseUtc": "2026-07-13T10:00:00+00:00",
                        "verifiedArtifactParameters": True,
                    },
                }
            )
            generation.jobs["job-1"].update(
                status="completed",
                progress=100.0,
                message="ready",
                artifactId="tn_fresh",
            )
            status = manager.run_once("2026-07-13T10:04:00Z")
            self.assertEqual(status["state"], "up_to_date")
            self.assertEqual(status["activeRun"]["artifactId"], "tn_fresh")
            self.assertTrue(status["activeRun"]["parameters"]["verifiedArtifactParameters"])
            self.assertEqual(shadow.scans, 1)

    def test_stale_market_bar_does_not_create_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manager, _repository, gateway, generation, _shadow = self.make_manager(Path(temporary))
            status = manager.run_once("2026-07-13T12:30:00Z")
            self.assertEqual(status["state"], "market_stale")
            self.assertEqual(gateway.snapshot_calls, 0)
            self.assertEqual(generation.created, [])

    def test_current_artifact_does_not_regenerate_same_closed_bar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manager, _repository, gateway, generation, _shadow = self.make_manager(
                Path(temporary),
                active_last_close="2026-07-13T10:00:00Z",
            )
            status = manager.run_once("2026-07-13T10:02:00Z")
            self.assertEqual(status["state"], "up_to_date")
            self.assertEqual(gateway.snapshot_calls, 0)
            self.assertEqual(generation.created, [])

    def test_startup_repairs_completed_audit_parameters_from_verified_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manager, repository, gateway, generation, shadow = self.make_manager(root)
            with repository.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO app_prospective_refresh_runs(
                        run_id, contract, source_bar_open_utc, source_bar_close_utc,
                        status, stage, source_snapshot_id, price_source_id, artifact_id,
                        parameters_json, created_at_utc, updated_at_utc
                    ) VALUES(?, ?, ?, ?, 'completed', 'completed', ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "run-repair",
                        "GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1",
                        "2026-07-13T09:00:00+00:00",
                        "2026-07-13T10:00:00+00:00",
                        "snapshot-repair",
                        "price-repair",
                        "tn_repair",
                        '{"priceSourceLastBarCloseUtc":"2026-07-13T09:00:00+00:00"}',
                        "2026-07-13T10:02:00+00:00",
                        "2026-07-13T10:03:00+00:00",
                    ),
                )
            repository.artifacts.append(
                {
                    "artifactId": "tn_repair",
                    "parameters": {
                        "priceSourceId": "price-repair",
                        "priceSourceLastBarCloseUtc": "2026-07-13T10:00:00+00:00",
                        "prospectiveRefresh": {
                            "contract": "GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1",
                            "runId": "run-repair",
                            "sourceBarCloseUtc": "2026-07-13T10:00:00+00:00",
                        },
                    },
                }
            )

            repaired = ProspectiveArtifactRefreshSupervisor(
                repository,
                gateway,
                generation,
                shadow,
                autostart=False,
            )
            run = repaired.recent_runs(1)[0]
            self.assertEqual(
                run["parameters"]["priceSourceLastBarCloseUtc"],
                "2026-07-13T10:00:00+00:00",
            )


if __name__ == "__main__":
    unittest.main()
