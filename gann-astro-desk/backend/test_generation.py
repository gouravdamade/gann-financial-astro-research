from __future__ import annotations

import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from generation import GenerationJobManager, normalize_generation_parameters
from repository import AstroRepository, DataPaths


PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
        )
        cls.repository = AstroRepository(cls.paths)

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

    def test_small_real_job_registers_and_activates_analyzable_artifact(self) -> None:
        manager = GenerationJobManager(self.repository)
        job = manager.create_job(
            {"label": "Regression smoke", "parameters": self.small_parameters(), "autoActivate": True}
        )
        deadline = time.monotonic() + 30
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
