from __future__ import annotations

import gc
import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from repository import ASTRO_CONTRACT, AstroRepository, DataPaths


class AstroRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary_root = Path(cls.temporary.name)
        project_root = Path(__file__).resolve().parents[2]
        database = temporary_root / "annotations.sqlite"
        source = sqlite3.connect(project_root / "gann_aspect_annotations_raman_v2.sqlite")
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
            connection.execute("DELETE FROM app_price_sources")
            connection.commit()
        finally:
            connection.close()
        paths = DataPaths(
            project_root=project_root,
            source_events=project_root / "astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet",
            touch_log=project_root / "aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv",
            price_data=project_root / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
            price_data_m30=project_root / "usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet",
            annotation_db=database,
            snapshots_dir=temporary_root / "snapshots",
            artifacts_dir=temporary_root / "artifacts",
            market_snapshots_dir=temporary_root / "market_snapshots",
            price_sources_dir=temporary_root / "price_sources",
        )
        cls.repository = AstroRepository(paths)

    @classmethod
    def tearDownClass(cls) -> None:
        del cls.repository
        gc.collect()
        cls.temporary.cleanup()

    def test_chart_payload_uses_versioned_directional_events(self) -> None:
        payload = self.repository.chart_payload("2025-05-26", "2025-05-30")
        self.assertEqual(payload["astronomyContract"], ASTRO_CONTRACT)
        self.assertTrue(payload["candles"])
        self.assertTrue(payload["aspects"])
        self.assertTrue(payload["srLines"])
        self.assertTrue(all(item["familyKey"].startswith("TN::") for item in payload["aspects"]))

    def test_health_reports_corrected_touch_source(self) -> None:
        health = self.repository.health()
        self.assertEqual(health["touchCount"], 754)

    def test_parameter_schema_exposes_supported_and_pending_modes(self) -> None:
        schema = self.repository.parameter_schema()
        self.assertIn("M30", schema["options"]["timeframes"])
        self.assertEqual(schema["generation"]["correctedTn"], "generator_ready")
        self.assertEqual(schema["generation"]["correctedTt"], "not_implemented")
        self.assertEqual(schema["generation"]["profileJobQueue"], "ready")
        self.assertEqual(schema["generation"]["activeArtifactId"], self.repository.active_artifact["artifactId"])

    def test_chart_filters_and_m30_source_are_applied(self) -> None:
        payload = self.repository.chart_payload(
            "2025-05-26",
            "2025-05-30",
            timeframe="M30",
            transit_bodies=("MOON",),
            aspects=("square",),
            only_touched=True,
        )
        self.assertTrue(payload["candles"])
        self.assertTrue(payload["aspects"])
        self.assertTrue(all(item["transitBody"] == "MOON" for item in payload["aspects"]))
        self.assertTrue(all(item["aspect"] == "square" for item in payload["aspects"]))
        self.assertTrue(all(item["eventId"] in self.repository.touch_by_event for item in payload["aspects"]))

    def test_family_payload_preserves_transit_natal_direction(self) -> None:
        payload = self.repository.family_payload("TN::MOON->MERCURY::square")
        self.assertEqual(payload["transitBody"], "MOON")
        self.assertEqual(payload["natalBody"], "MERCURY")
        self.assertGreaterEqual(payload["summary"]["total"], 1)

    def test_codex_context_is_analysis_only(self) -> None:
        event_id = self.repository.family_payload("TN::MOON->MERCURY::square")["occurrences"][0]["eventId"]
        context = self.repository.codex_context(event_id)
        self.assertTrue(context["guardrails"]["analysisOnly"])
        self.assertFalse(context["guardrails"]["mt5OrderPlacementAllowed"])
        self.assertEqual(context["guardrails"]["astronomyContract"], ASTRO_CONTRACT)

    def test_live_decision_uses_allowlisted_touch_evidence_only(self) -> None:
        touch = self.repository.touches.iloc[0]
        event_id = str(touch["event_id"])
        cutoff = pd.Timestamp(touch["touch_time_local"]) + pd.Timedelta(hours=1)
        packet = self.repository.live_decision_packet(event_id, cutoff)

        self.assertEqual(packet["mode"], "live_inference")
        self.assertEqual(packet["status"], "watch")
        self.assertIn(packet["decision"]["action"], {"WATCH_LONG", "WATCH_SHORT"})
        self.assertTrue(packet["guardrails"]["timestampSafe"])
        self.assertTrue(packet["guardrails"]["noLookahead"])
        self.assertFalse(packet["guardrails"]["executionAllowed"])
        self.assertEqual(
            packet["policyLocks"]["historicalValidationStatus"],
            "failed_retrospective_statistical_gate_20260713",
        )
        self.assertIsNone(packet["outcome"])
        self.assertIsNone(packet["entry"]["price"])
        self.assertIsNone(packet["exit"]["price"])
        self.assertEqual(pd.Timestamp(packet["times"]["decisionTime"]), cutoff.tz_convert("UTC"))
        self.assertEqual(
            set(packet["featureAudit"]["consumedFields"]),
            {
                "aspect",
                "base_reference_label",
                "base_tn_hits_json",
                "pair_key",
                "quote_reference_label",
                "tn_hits_json",
            },
        )
        self.assertLessEqual(
            pd.Timestamp(packet["times"]["sourceDataMaxTime"]),
            pd.Timestamp(packet["times"]["decisionTime"]),
        )


if __name__ == "__main__":
    unittest.main()
