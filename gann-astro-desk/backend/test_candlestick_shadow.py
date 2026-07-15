from __future__ import annotations

# ruff: noqa: E402 - the repository root must precede cross-project test imports.

import copy
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from candlestick_agent.usdjpy_walk_forward import (
    DEFAULT_CONTRACT_PATH,
    build_decision_dataset,
    load_contract,
)
from candlestick_shadow import (
    CandlestickShadowStore,
    CandlestickShadowSupervisor,
    bars_to_frame,
    build_outcome_payload,
    evaluate_model,
    feature_snapshot,
    load_frozen_model,
    market_clock_evidence,
)

MODEL_PATH = PROJECT_ROOT / "candlestick_agent" / "usdjpy_shadow_model_v1.json"


def synthetic_price(rows: int = 72) -> pd.DataFrame:
    index = pd.date_range("2026-07-01T00:00:00Z", periods=rows, freq="h")
    step = np.sin(np.arange(rows) / 2.7) * 0.026 + np.cos(np.arange(rows) / 9.0) * 0.012
    close = 145.0 + np.cumsum(step)
    open_ = np.concatenate(([145.0], close[:-1]))
    high = np.maximum(open_, close) + 0.022 + (np.arange(rows) % 3) * 0.003
    low = np.minimum(open_, close) - 0.021 - (np.arange(rows) % 4) * 0.002
    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": np.arange(rows) + 100,
            "spread": np.full(rows, 10.0),
            "real_volume": np.zeros(rows),
        },
        index=index,
    )


def mt5_bars(frame: pd.DataFrame) -> list[dict]:
    return [
        {
            "time": int(timestamp.timestamp()),
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": int(row.tick_volume),
        }
        for timestamp, row in frame.iterrows()
    ]


class FakeGateway:
    def bars(self, _symbol: str, _timeframe: str, _count: int) -> list[dict]:
        raise AssertionError("Tests pass timestamped bars directly")


class CandlestickShadowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = load_frozen_model(MODEL_PATH)
        self.frame = synthetic_price()
        self.bars = mt5_bars(self.frame)
        self.decision_index = 35
        self.observed = self.frame.index[self.decision_index] + pd.Timedelta(hours=1, minutes=5)

    def supervisor(self, database_path: Path) -> CandlestickShadowSupervisor:
        return CandlestickShadowSupervisor(
            FakeGateway(),
            model_path=MODEL_PATH,
            database_path=database_path,
            autostart=False,
        )

    def test_live_feature_snapshot_matches_retrospective_geometry(self) -> None:
        contract = load_contract(DEFAULT_CONTRACT_PATH)
        retrospective = build_decision_dataset(self.frame, contract)
        expected = retrospective.loc[
            retrospective["source_row_number"] == self.decision_index
        ].iloc[0]
        live = feature_snapshot(bars_to_frame(self.bars), self.artifact, self.observed)
        for name, value in live["features"].items():
            self.assertAlmostEqual(value, float(expected[name]), places=12, msg=name)
        self.assertEqual(
            live["featureAvailableAtUtc"], expected["feature_available_time"].isoformat()
        )

    def test_future_bars_cannot_change_a_timestamped_decision(self) -> None:
        baseline = feature_snapshot(bars_to_frame(self.bars), self.artifact, self.observed)
        changed = self.frame.copy()
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("close")] += 50.0
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("high")] += 50.0
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("low")] += 50.0
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("open")] += 50.0
        replay = feature_snapshot(bars_to_frame(mt5_bars(changed)), self.artifact, self.observed)
        self.assertEqual(baseline["features"], replay["features"])
        self.assertEqual(baseline["inputBarsSha256"], replay["inputBarsSha256"])

    def test_transparent_probability_math_matches_independent_formula(self) -> None:
        snapshot = feature_snapshot(bars_to_frame(self.bars), self.artifact, self.observed)
        model = self.artifact["primaryModel"]
        result = evaluate_model(model, snapshot["features"])
        values = np.asarray([snapshot["features"][name] for name in model["features"]])
        scaled = (values - np.asarray(model["scalerMean"])) / np.asarray(model["scalerScale"])
        logit = float(np.dot(scaled, np.asarray(model["coefficients"])) + model["intercept"])
        expected = 1.0 / (1.0 + np.exp(-logit))
        self.assertAlmostEqual(result["probabilityUp"], expected, places=15)

    def test_timely_scan_is_idempotent_across_restart(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "shadow.sqlite"
            first = self.supervisor(database)
            captured = first.scan_once(
                observed_at=self.observed, bars=self.bars, market_time_utc=self.observed
            )
            self.assertEqual(captured["summary"], {"decisions": 1, "outcomes": 0, "pending": 1})
            self.assertEqual(captured["lastScan"]["state"], "captured")
            first.stop()
            restarted = self.supervisor(database)
            current = restarted.scan_once(
                observed_at=self.observed + pd.Timedelta(minutes=4),
                bars=self.bars,
                market_time_utc=self.observed + pd.Timedelta(minutes=4),
            )
            self.assertEqual(current["summary"], captured["summary"])
            self.assertEqual(current["lastScan"]["state"], "current")
            self.assertTrue(current["integrity"]["ok"])
            restarted.stop()

    def test_late_bar_is_skipped_and_never_backfilled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "late.sqlite")
            late = self.frame.index[self.decision_index] + pd.Timedelta(hours=1, minutes=16)
            status = supervisor.scan_once(
                observed_at=late, bars=self.bars, market_time_utc=late
            )
            self.assertEqual(status["summary"]["decisions"], 0)
            self.assertEqual(status["lastScan"]["state"], "skipped")
            self.assertIn("never backfilled", status["lastScan"]["message"])
            supervisor.stop()

    def test_six_actual_market_bars_settle_with_frozen_costs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "settle.sqlite")
            supervisor.scan_once(
                observed_at=self.observed, bars=self.bars, market_time_utc=self.observed
            )
            settled_at = self.frame.index[self.decision_index + 6] + pd.Timedelta(
                hours=1, minutes=5
            )
            status = supervisor.scan_once(
                observed_at=settled_at, bars=self.bars, market_time_utc=settled_at
            )
            self.assertEqual(status["summary"], {"decisions": 2, "outcomes": 1, "pending": 1})
            outcome = next(
                item["payload"] for item in status["records"] if item["entryType"] == "outcome"
            )
            self.assertEqual(outcome["heldBars"], 6)
            self.assertAlmostEqual(
                outcome["entryPrice"], float(self.frame.iloc[self.decision_index + 1]["open"])
            )
            self.assertAlmostEqual(
                outcome["exitPrice"], float(self.frame.iloc[self.decision_index + 6]["close"])
            )
            self.assertEqual(outcome["totalCostPips"], 1.4)
            self.assertFalse(outcome["guardrails"]["executionOccurred"])
            supervisor.stop()

    def test_outcome_waits_for_six_bars_not_six_wall_clock_hours(self) -> None:
        snapshot = feature_snapshot(bars_to_frame(self.bars), self.artifact, self.observed)
        from candlestick_shadow import build_decision_payload

        decision = build_decision_payload(
            snapshot,
            self.artifact,
            self.observed,
            market_clock_evidence(self.observed, self.observed),
        )
        sparse = self.frame.iloc[: self.decision_index + 4].copy()
        result = build_outcome_payload(
            decision,
            sparse,
            self.artifact,
            self.frame.index[self.decision_index] + pd.Timedelta(days=3),
        )
        self.assertIsNone(result)

    def test_ledger_and_manifest_are_immutable_and_trial_locked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "immutable.sqlite"
            supervisor = self.supervisor(database)
            status = supervisor.scan_once(
                observed_at=self.observed, bars=self.bars, market_time_utc=self.observed
            )
            self.assertTrue(status["integrity"]["ok"])
            connection = sqlite3.connect(database)
            try:
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "UPDATE candlestick_shadow_entries SET payload_json = '{}' WHERE ledger_sequence = 1"
                    )
                connection.rollback()
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute("DELETE FROM candlestick_shadow_manifest")
                connection.rollback()
            finally:
                connection.close()
            drifted = copy.deepcopy(self.artifact)
            drifted["costs"]["fallbackSpreadPips"] = 2.0
            with self.assertRaisesRegex(ValueError, "another frozen trial"):
                CandlestickShadowStore(database, drifted)
            supervisor.stop()

    def test_tampered_model_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "tampered.json"
            payload = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
            payload["primaryModel"]["coefficients"][0] += 0.01
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                load_frozen_model(path)

    def test_every_persisted_decision_keeps_execution_and_consumers_off(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "guardrails.sqlite")
            status = supervisor.scan_once(
                observed_at=self.observed, bars=self.bars, market_time_utc=self.observed
            )
            decision = status["records"][0]["payload"]
            self.assertEqual(decision["primary"]["action"], "abstain")
            self.assertFalse(decision["guardrails"]["executionAllowed"])
            self.assertFalse(decision["guardrails"]["consumedByAstrologyRules"])
            self.assertFalse(decision["guardrails"]["consumedByAutoSuggest"])
            self.assertFalse(decision["guardrails"]["consumedByOfficialMlNotes"])
            self.assertFalse(decision["guardrails"]["consumedByCoordinator"])
            self.assertTrue(decision["guardrails"]["mt5ReadOnly"])
            supervisor.stop()

    def test_market_clock_skew_fails_closed_without_an_append(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "clock.sqlite")
            market_time = self.observed + pd.Timedelta(minutes=6)
            status = supervisor.scan_once(
                observed_at=self.observed,
                bars=self.bars,
                market_time_utc=market_time,
            )
            self.assertEqual(status["summary"]["decisions"], 0)
            self.assertEqual(status["lastScan"]["state"], "skipped")
            self.assertIn("clock skew", status["lastScan"]["message"])
            self.assertFalse(status["lastScan"]["marketClock"]["valid"])
            supervisor.stop()


if __name__ == "__main__":
    unittest.main()
