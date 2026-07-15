from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from generation import GenerationJobManager, normalize_generation_parameters  # noqa: E402
from price_sources import SNAPSHOT_CONTRACT, file_sha256  # noqa: E402
from repository import AstroRepository, DataPaths  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REAL_GENERATION_TIMEOUT_SECONDS = 90


class GenerationJobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary_root = Path(cls.temporary.name)
        database = temporary_root / "annotations.sqlite"
        source = sqlite3.connect(PROJECT_ROOT / "gann_aspect_annotations_raman_v2.sqlite")
        destination = sqlite3.connect(database)
        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()
        connection = sqlite3.connect(database)
        try:
            connection.execute("DELETE FROM app_generation_jobs")
            connection.execute("DELETE FROM app_data_artifacts")
            connection.commit()
        finally:
            connection.close()
        cls.paths = DataPaths(
            project_root=PROJECT_ROOT,
            source_events=PROJECT_ROOT / "astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet",
            touch_log=PROJECT_ROOT / "aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv",
            price_data=PROJECT_ROOT / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
            price_data_m30=PROJECT_ROOT / "usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet",
            annotation_db=database,
            snapshots_dir=temporary_root / "snapshots",
            artifacts_dir=temporary_root / "artifacts",
            market_snapshots_dir=temporary_root / "market_snapshots",
            price_sources_dir=temporary_root / "price_sources",
        )
        cls.repository = AstroRepository(cls.paths)
        snapshot_id = "USDJPY_H1_20250307T000000Z_generation_fixture"
        snapshot_dir = cls.paths.market_snapshots_dir / "USDJPY" / "H1"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        source_price = pd.read_parquet(cls.paths.price_data)
        source_price = source_price.loc["2025-02-27":"2025-03-06"].copy()
        snapshot_path = snapshot_dir / f"{snapshot_id}.parquet"
        snapshot_manifest = snapshot_dir / f"{snapshot_id}.manifest.json"
        source_price.to_parquet(snapshot_path)
        source_index = source_price.index.tz_convert("UTC")
        snapshot_as_of = source_index.max() + pd.Timedelta(hours=1)
        snapshot_manifest.write_text(
            json.dumps(
                {
                    "snapshotId": snapshot_id,
                    "contract": SNAPSHOT_CONTRACT,
                    "symbol": "USDJPY",
                    "timeframe": "H1",
                    "capturedAtUtc": snapshot_as_of.isoformat(),
                    "requestedStartUtc": source_index.min().isoformat(),
                    "requestedEndUtc": snapshot_as_of.isoformat(),
                    "asOfUtc": snapshot_as_of.isoformat(),
                    "barCount": len(source_price),
                    "firstBarOpenUtc": source_index.min().isoformat(),
                    "lastBarOpenUtc": source_index.max().isoformat(),
                    "lastBarCloseUtc": snapshot_as_of.isoformat(),
                    "incompleteBarsExcluded": 0,
                    "noLookahead": True,
                    "immutable": True,
                    "parquetPath": str(snapshot_path),
                    "parquetSha256": file_sha256(snapshot_path),
                    "manifestPath": str(snapshot_manifest),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        cls.promoted_source = cls.repository.promote_history_snapshot(snapshot_id, "Generation fixture")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def small_parameters(self) -> dict:
        return {
            **self.repository.parameter_schema()["defaults"],
            "start": "2025-03-01T00:00:00+05:30",
            "end": "2025-03-01T23:59:00+05:30",
            "transitBodies": ["AVG(ALL)"],
            "natalBodies": ["VENUS"],
            "aspects": ["conjunction_orb"],
        }

    def test_normalization_preserves_directional_entities_and_sr_inputs(self) -> None:
        normalized = normalize_generation_parameters(self.repository, self.small_parameters())
        self.assertEqual(normalized["sourceTimeframe"], "H1")
        self.assertEqual(normalized["transitBodies"], ["AVG(ALL)"])
        self.assertEqual(normalized["natalBodies"], ["VENUS"])
        self.assertEqual(normalized["aspects"], ["conjunction_orb"])
        self.assertEqual(normalized["harmonics"], [0.12, 0.18])

    def test_queued_job_can_be_cancelled_durably(self) -> None:
        manager = GenerationJobManager(self.repository, autostart=False)
        job = manager.create_job({"parameters": self.small_parameters()})
        cancelled = manager.cancel_job(job["jobId"])
        manager.stop()
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertTrue(cancelled["cancelRequested"])

    def test_frozen_worker_runs_in_process_without_spawning_itself(self) -> None:
        manager = GenerationJobManager(self.repository, autostart=False)
        log_path = self.paths.artifacts_dir / "frozen_worker_environment.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        previous_arguments = list(sys.argv)
        try:
            with (
                mock.patch.object(sys, "frozen", True, create=True),
                mock.patch("runtime_support.run_worker_mode", return_value=True) as worker,
                mock.patch("generation.subprocess.Popen") as popen,
            ):
                manager._run_command(
                    "test-job",
                    [
                        "GannAstroBackend.exe",
                        "--gann-worker",
                        "generator.py",
                        "--example",
                    ],
                    log_path,
                )
        finally:
            manager.stop()

        worker.assert_called_once_with(
            ["--gann-worker", "generator.py", "--example"]
        )
        popen.assert_not_called()
        self.assertEqual(sys.argv, previous_arguments)
        self.assertIn(
            "Packaged generator completed in the background worker thread.",
            log_path.read_text(encoding="utf-8"),
        )

    def test_small_real_frozen_job_runs_both_generators_in_process(self) -> None:
        manager = GenerationJobManager(self.repository)
        try:
            with (
                mock.patch.object(sys, "frozen", True, create=True),
                mock.patch("generation.subprocess.Popen") as popen,
            ):
                job = manager.create_job(
                    {
                        "label": "Frozen in-process regression smoke",
                        "parameters": self.small_parameters(),
                    }
                )
                deadline = time.monotonic() + REAL_GENERATION_TIMEOUT_SECONDS
                while time.monotonic() < deadline:
                    job = manager.get_job(job["jobId"])
                    if job["status"] not in {"queued", "running", "cancelling"}:
                        break
                    time.sleep(0.25)
        finally:
            manager.stop()

        self.assertEqual(job["status"], "completed", job.get("error") or job.get("logTail"))
        popen.assert_not_called()
        log_text = Path(job["logPath"]).read_text(encoding="utf-8")
        self.assertEqual(
            log_text.count("Packaged generator completed in the background worker thread."),
            2,
        )

    def test_promoted_snapshot_drives_generation_and_active_chart_prices(self) -> None:
        manager = GenerationJobManager(self.repository)
        parameters = {
            **self.small_parameters(),
            "priceSourceId": self.promoted_source["priceSourceId"],
        }
        job = manager.create_job(
            {"label": "Promoted source smoke", "parameters": parameters, "autoActivate": True}
        )
        deadline = time.monotonic() + REAL_GENERATION_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            job = manager.get_job(job["jobId"])
            if job["status"] not in {"queued", "running", "cancelling"}:
                break
            time.sleep(0.25)
        manager.stop()

        self.assertEqual(job["status"], "completed", job.get("error") or job.get("logTail"))
        artifact = next(
            item for item in self.repository.list_data_artifacts() if item["artifactId"] == job["artifactId"]
        )
        self.assertEqual(artifact["parameters"]["priceSourceId"], self.promoted_source["priceSourceId"])
        self.assertEqual(Path(artifact["pricePath"]), Path(self.promoted_source["pricePath"]))
        self.assertEqual(self.repository.active_artifact["artifactId"], job["artifactId"])
        self.assertEqual(
            self.repository.price.index.min(),
            pd.Timestamp(self.promoted_source["dateStart"]),
        )
        schema = self.repository.parameter_schema()
        self.assertEqual(schema["defaults"]["priceSourceId"], self.promoted_source["priceSourceId"])
        self.assertEqual(schema["defaults"]["start"], parameters["start"])
        self.assertNotIn("M30", schema["options"]["timeframes"])
        self.repository.activate_artifact("baseline")

    def test_small_real_job_registers_and_activates_analyzable_artifact(self) -> None:
        manager = GenerationJobManager(self.repository)
        job = manager.create_job(
            {"label": "Regression smoke", "parameters": self.small_parameters(), "autoActivate": True}
        )
        deadline = time.monotonic() + REAL_GENERATION_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            job = manager.get_job(job["jobId"])
            if job["status"] not in {"queued", "running", "cancelling"}:
                break
            time.sleep(0.25)
        manager.stop()
        self.assertEqual(job["status"], "completed", job.get("error") or job.get("logTail"))
        self.assertEqual(self.repository.active_artifact["artifactId"], job["artifactId"])
        family = self.repository.family_payload("TN::AVG(ALL)->VENUS::conjunction_orb")
        detail = self.repository.event_detail(family["selectedEventId"])
        self.assertEqual(family["summary"]["total"], 1)
        self.assertGreaterEqual(len(detail["astroEvidence"]), 2)
        self.assertEqual(detail["chart"]["artifact"]["artifactId"], job["artifactId"])
        reopened = AstroRepository(self.paths)
        self.assertEqual(reopened.active_artifact["artifactId"], job["artifactId"])
        restored = reopened.activate_artifact("baseline")
        self.assertEqual(restored["artifactId"], "baseline")
        self.assertEqual(restored["eventCount"], 1268)


if __name__ == "__main__":
    unittest.main()
