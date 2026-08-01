from __future__ import annotations

import gc
import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from aspect_evidence_trace import ASPECT_EVIDENCE_TRACE_CONTRACT
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
        self.assertTrue(
            all(
                0 <= item["knownPriorCount"] < item["knownOccurrenceCount"]
                for item in payload["aspects"]
            )
        )

    def test_health_reports_corrected_touch_source(self) -> None:
        health = self.repository.health()
        self.assertEqual(health["touchCount"], 754)

    def test_parameter_schema_exposes_supported_and_pending_modes(self) -> None:
        schema = self.repository.parameter_schema()
        self.assertIn("M30", schema["options"]["timeframes"])
        self.assertIn("W1", schema["options"]["timeframes"])
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

    def test_timeframe_policy_filters_aspects_without_changing_event_windows(self) -> None:
        h1 = self.repository.chart_payload("2025-05-01", "2025-06-30", timeframe="H1")
        d1 = self.repository.chart_payload("2025-05-01", "2025-06-30", timeframe="D1")
        self.assertEqual(h1["parametersApplied"]["effectiveMinDurationMinutes"], 60.0)
        self.assertEqual(d1["parametersApplied"]["effectiveMinDurationMinutes"], 1440.0)
        self.assertTrue(all(item["durationMinutes"] >= 60 for item in h1["aspects"]))
        self.assertTrue(all(item["durationMinutes"] >= 1440 for item in d1["aspects"]))
        h1_by_id = {item["eventId"]: item for item in h1["aspects"]}
        for item in d1["aspects"]:
            self.assertEqual(item["start"], h1_by_id[item["eventId"]]["start"])
            self.assertEqual(item["end"], h1_by_id[item["eventId"]]["end"])

    def test_weekly_candles_are_monday_anchored_and_use_weekly_aspect_policy(self) -> None:
        payload = self.repository.chart_payload("2025-05-01", "2025-06-30", timeframe="W1")
        self.assertTrue(payload["candles"])
        self.assertEqual(payload["parametersApplied"]["effectiveMinDurationMinutes"], 10080.0)
        candle_days = {
            pd.to_datetime(item["time"], unit="s", utc=True).dayofweek
            for item in payload["candles"]
        }
        self.assertEqual(candle_days, {0})
        self.assertTrue(all(item["durationMinutes"] >= 10080 for item in payload["aspects"]))

    def test_bar_replay_is_cut_at_closed_bar_evidence_time(self) -> None:
        full = self.repository.chart_payload(
            "2025-05-26T00:00:00+05:30",
            "2025-05-30T23:59:59+05:30",
            timeframe="H1",
        )
        self.assertGreater(len(full["candles"]), 20)
        selected = full["candles"][19]
        cutoff = pd.Timestamp(selected["time"], unit="s", tz="UTC") + pd.Timedelta(hours=1)
        replay = self.repository.chart_payload(
            "2025-05-26T00:00:00+05:30",
            "2025-05-30T23:59:59+05:30",
            timeframe="H1",
            replay_cutoff=cutoff.isoformat(),
        )

        self.assertEqual(
            replay["replay"]["contract"],
            "GANN_TIMESTAMP_SAFE_BAR_REPLAY_V1",
        )
        self.assertEqual(replay["replay"]["position"], 20)
        self.assertEqual(len(replay["candles"]), 20)
        self.assertTrue(replay["replay"]["timestampSafe"])
        self.assertTrue(replay["replay"]["noLookahead"])
        self.assertLessEqual(
            max(item["time"] + 60 * 60 for item in replay["candles"]),
            int(cutoff.timestamp()),
        )
        self.assertTrue(
            all(item["start"] <= int(cutoff.timestamp()) for item in replay["aspects"])
        )
        self.assertTrue(
            all(item["end"] <= int(cutoff.timestamp()) for item in replay["aspects"])
        )
        self.assertTrue(
            all(item["peak"] <= int(cutoff.timestamp()) for item in replay["aspects"])
        )
        self.assertTrue(all(item["outcome"] is None for item in replay["aspects"]))
        self.assertTrue(all(item["returnPct"] is None for item in replay["aspects"]))
        self.assertTrue(all(not item["reviewed"] for item in replay["aspects"]))
        self.assertTrue(
            all(
                item.get("touchTime", 0) + 60 * 60 <= int(cutoff.timestamp())
                for item in replay["srLines"]
            )
        )

    def test_bar_replay_rejects_cutoff_before_first_close(self) -> None:
        with self.assertRaisesRegex(ValueError, "precedes the first closed candle"):
            self.repository.chart_payload(
                "2025-05-26T00:00:00+05:30",
                "2025-05-27T23:59:59+05:30",
                timeframe="H1",
                replay_cutoff="2025-05-25T18:45:00Z",
            )

    def test_family_payload_preserves_transit_natal_direction(self) -> None:
        payload = self.repository.family_payload("TN::MOON->MERCURY::square")
        self.assertEqual(payload["transitBody"], "MOON")
        self.assertEqual(payload["natalBody"], "MERCURY")
        self.assertGreaterEqual(payload["summary"]["total"], 1)

    def test_event_detail_includes_recurrence_and_both_currency_sides(self) -> None:
        event_id = str(self.repository.touches.iloc[0]["event_id"])
        detail = self.repository.event_detail(event_id)

        self.assertGreaterEqual(detail["event"]["occurrenceIndex"], 1)
        self.assertEqual(
            detail["event"]["occurrenceCount"],
            detail["familySummary"]["total"],
        )
        self.assertEqual(
            detail["familySummary"]["reviewed"]
            + detail["familySummary"]["pending"],
            detail["familySummary"]["total"],
        )
        pair = detail["currencyPairEvidence"]
        self.assertIsNotNone(pair)
        self.assertEqual(pair["contract"], "GANN_FX_PAIR_EVIDENCE_V2")
        self.assertEqual(pair["base"]["label"], "USD")
        self.assertEqual(pair["quote"]["label"], "JPY")
        self.assertEqual(pair["base"]["referenceLabel"], "USD")
        self.assertEqual(pair["quote"]["referenceLabel"], "JPY")
        self.assertGreaterEqual(detail["event"]["knownPriorCount"], 0)
        self.assertGreaterEqual(
            detail["event"]["knownOccurrenceCount"],
            detail["event"]["occurrenceCount"],
        )
        self.assertIn(
            pair["pair"]["doctrineDirection"],
            {"BULLISH", "BEARISH", "UNKNOWN"},
        )
        self.assertIn(
            pair["status"],
            {"provisional_research_only", "insufficient_pair_evidence", "blocked_mapping"},
        )
        self.assertIn(pair["base"]["state"], {"KNOWN", "UNKNOWN", "BLOCKED_MAPPING"})
        self.assertIn(pair["quote"]["state"], {"KNOWN", "UNKNOWN"})
        self.assertIn(pair["pair"]["state"], {"KNOWN", "UNKNOWN"})
        self.assertIn("commonActivationUnits", pair["pair"])
        certification = {item["key"]: item for item in detail["evidenceCertifications"]}
        self.assertEqual(certification["astronomy_geometry"]["status"], "versioned")
        self.assertIn(certification["shadbala_drik"]["status"], {"certified", "failed", "blocked"})
        self.assertEqual(certification["family_outcomes"]["status"], "retrospective")

    def test_aspect_evidence_trace_keeps_outcome_out_of_timestamp_safe_records(self) -> None:
        event_id = str(self.repository.touches.iloc[0]["event_id"])
        trace = self.repository.aspect_evidence_trace(event_id, max_window_records=12)

        self.assertEqual(trace["contract"], ASPECT_EVIDENCE_TRACE_CONTRACT)
        self.assertTrue(trace["guardrails"]["timestampSafe"])
        self.assertTrue(trace["guardrails"]["noLookahead"])
        self.assertTrue(trace["guardrails"]["outcomeSeparated"])
        self.assertFalse(trace["guardrails"]["executionAllowed"])
        self.assertEqual(trace["start"]["kind"], "start")
        self.assertEqual(trace["end"]["kind"], "end")
        self.assertTrue(trace["start"]["guardrails"]["outcomeExcluded"])
        self.assertTrue(trace["end"]["guardrails"]["outcomeExcluded"])
        self.assertTrue(trace["outcome"]["retrospectiveOnly"])
        self.assertIn("sbc", trace["precalculationStatus"])
        self.assertIn("strictShadbalaDrik", trace["precalculationStatus"])

        checkpoints = trace["reactionCheckpoints"]
        self.assertTrue(checkpoints["retrospectiveOnly"])
        self.assertFalse(checkpoints["usableAtStart"])
        self.assertFalse(checkpoints["usableDuringWindow"])
        self.assertFalse(checkpoints["consumedByLiveInference"])
        self.assertFalse(checkpoints["consumedByShadowLedger"])
        if checkpoints["available"]:
            self.assertIsNotNone(checkpoints["crest"])
            self.assertIsNotNone(checkpoints["trough"])
            for checkpoint in (checkpoints["crest"], checkpoints["trough"]):
                self.assertTrue(checkpoint["guardrails"]["selectedRetrospectively"])
                self.assertFalse(checkpoint["guardrails"]["usableAtStart"])
                self.assertFalse(checkpoint["guardrails"]["usableDuringWindow"])
                self.assertLessEqual(
                    pd.Timestamp(checkpoint["asOfUtc"]),
                    pd.Timestamp(trace["times"]["eventEndUtc"]),
                )

        records = [trace["start"], *trace["window"]["records"], trace["end"]]
        for record in records:
            self.assertTrue(record["guardrails"]["timestampSafe"])
            self.assertTrue(record["guardrails"]["noLookahead"])
            self.assertTrue(record["guardrails"]["outcomeExcluded"])
            self.assertFalse(record["guardrails"]["executionAllowed"])
            self.assertIn("panchanga", record["sbc"])
            self.assertIn("actorReadiness", record["sbc"])
            self.assertIn("implementedTotalVirupa", record["strength"])
            self.assertIn("certification", record["strength"])
            market = record["market"]
            if market["available"]:
                self.assertLessEqual(
                    pd.Timestamp(market["barCloseTimeUtc"]),
                    pd.Timestamp(record["asOfUtc"]),
                )
                self.assertTrue(market["rsi14"]["closedBarOnly"])

    def test_historical_family_summary_uses_only_prior_matured_outcomes(self) -> None:
        family_key = "TN::MOON->KETU::trine"
        rows = self.repository.events.loc[
            self.repository.events["event_family_key"] == family_key
        ].sort_values("timestamp")
        selected = rows.iloc[-1]
        detail = self.repository.event_detail(str(selected["event_id"]))
        summary = detail["historicalFamilySummary"]

        self.assertEqual(summary["contract"], "GANN_RETROSPECTIVE_FAMILY_EVIDENCE_V1")
        self.assertEqual(summary["scope"], "strictly_prior_matured_occurrences")
        self.assertEqual(
            pd.Timestamp(summary["asOf"]),
            pd.Timestamp(selected["timestamp"]).tz_convert("UTC"),
        )
        self.assertGreater(summary["priorOccurrenceCount"], 0)
        self.assertGreater(summary["labeledCount"], 0)
        self.assertLessEqual(summary["maturedTouchCount"], summary["priorOccurrenceCount"])
        self.assertAlmostEqual(
            summary["bullishRatePct"] + summary["bearishRatePct"],
            100.0,
        )
        self.assertGreater(summary["excursionSampleCount"], 0)
        self.assertGreaterEqual(summary["medianUpsideExcursionPct"], 0)
        self.assertLessEqual(summary["medianDownsideExcursionPct"], 0)
        self.assertTrue(summary["timestampSafeForSelectedEvent"])
        self.assertFalse(summary["liveInferenceConsumed"])

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
