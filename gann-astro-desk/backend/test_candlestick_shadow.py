from __future__ import annotations

# ruff: noqa: E402 - the repository root must precede cross-project test imports.

import copy
import hashlib
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
    CandlestickShadowUnavailable,
    bars_to_frame,
    build_decision_payload,
    build_outcome_payload,
    evaluate_model,
    feature_snapshot,
    load_frozen_model,
)
from mt5_clock import (
    CLOCK_PROBE_CONTRACT,
    TIME_NORMALIZATION_CONTRACT,
    normalize_bars,
    time_normalization_evidence,
)

MODEL_PATH = PROJECT_ROOT / "candlestick_agent" / "usdjpy_shadow_model_v1.json"
SERVER_OFFSET_SECONDS = 3 * 60 * 60


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


def server_encoded_bars(frame: pd.DataFrame) -> list[dict]:
    bars = mt5_bars(frame)
    for row in bars:
        row["time"] += SERVER_OFFSET_SECONDS
    return bars


def clock_probe(
    observed: pd.Timestamp,
    bars: list[dict],
    *,
    offset_seconds: int = SERVER_OFFSET_SECONDS,
    age_seconds: int = 0,
) -> dict:
    gmt = int(observed.timestamp()) - age_seconds
    raw_tick = int(observed.timestamp()) + offset_seconds
    return {
        "contract": CLOCK_PROBE_CONTRACT,
        "probeSequence": 42,
        "writtenAtGmtEpochSeconds": gmt,
        "timeCurrentEpochSeconds": raw_tick,
        "timeTradeServerEpochSeconds": gmt + offset_seconds,
        "timeGmtEpochSeconds": gmt,
        "timeLocalEpochSeconds": gmt + 19_800,
        "timeGmtOffsetSeconds": -19_800,
        "rawTickEpochSeconds": raw_tick,
        "rawTickMilliseconds": raw_tick * 1000,
        "rawH1BarOpenEpochSeconds": max(int(row["time"]) for row in bars),
        "terminalBuild": 6012,
        "terminalName": "MetaTrader 5",
        "terminalCompany": "MetaQuotes Ltd.",
        "terminalDataPath": "C:/MetaQuotes/Terminal/Test",
        "terminalCommonDataPath": "C:/MetaQuotes/Terminal/Common",
        "terminalConnected": True,
        "terminalAllowsTrading": True,
        "accountLogin": 123,
        "accountServer": "Test-Demo",
        "accountCompany": "MetaQuotes Ltd.",
        "accountAllowsTrading": True,
        "accountExpertTradingAllowed": True,
        "symbol": "USDJPY",
        "bid": 145.0,
        "ask": 145.01,
        "periodSeconds": 3600,
        "writeIntervalMilliseconds": 2000,
        "probePath": "C:/MetaQuotes/Terminal/Common/Files/gann_mt5_clock_probe_v1.csv",
        "probeFileSha256": "A" * 64,
    }


class FakeGateway:
    def bars(self, _symbol: str, _timeframe: str, _count: int) -> list[dict]:
        raise AssertionError("Tests pass timestamped bars directly")


class CandlestickShadowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = load_frozen_model(MODEL_PATH)
        self.frame = synthetic_price()
        self.utc_bars = mt5_bars(self.frame)
        self.bars = server_encoded_bars(self.frame)
        self.decision_index = 35
        self.observed = self.frame.index[self.decision_index] + pd.Timedelta(hours=1, minutes=5)

    def supervisor(self, database_path: Path) -> CandlestickShadowSupervisor:
        return CandlestickShadowSupervisor(
            FakeGateway(),
            model_path=MODEL_PATH,
            database_path=database_path,
            autostart=False,
        )

    def normalization(
        self,
        observed: pd.Timestamp | None = None,
        bars: list[dict] | None = None,
        **probe_values,
    ) -> dict:
        when = observed if observed is not None else self.observed
        source = bars if bars is not None else self.bars
        probe = clock_probe(when, source)
        probe.update(probe_values)
        return time_normalization_evidence(
            when.to_pydatetime(),
            int(when.timestamp()) + SERVER_OFFSET_SECONDS,
            max(int(row["time"]) for row in source),
            probe,
            expected_symbol="USDJPY",
        )

    def scan(
        self,
        supervisor: CandlestickShadowSupervisor,
        observed: pd.Timestamp | None = None,
        bars: list[dict] | None = None,
        probe: dict | None = None,
    ) -> dict:
        when = observed if observed is not None else self.observed
        source = bars if bars is not None else self.bars
        supplied_probe = probe if probe is not None else clock_probe(when, source)
        return supervisor.scan_once(
            observed_at=when,
            bars=source,
            clock_probe=supplied_probe,
            raw_market_tick_epoch_seconds=int(when.timestamp())
            + SERVER_OFFSET_SECONDS,
        )

    def normalized_frame(
        self,
        observed: pd.Timestamp | None = None,
        bars: list[dict] | None = None,
    ) -> pd.DataFrame:
        source = bars if bars is not None else self.bars
        return bars_to_frame(
            normalize_bars(source, self.normalization(observed, source))
        )

    def test_live_feature_snapshot_matches_retrospective_geometry(self) -> None:
        contract = load_contract(DEFAULT_CONTRACT_PATH)
        retrospective = build_decision_dataset(self.frame, contract)
        expected = retrospective.loc[
            retrospective["source_row_number"] == self.decision_index
        ].iloc[0]
        live = feature_snapshot(self.normalized_frame(), self.artifact, self.observed)
        for name, value in live["features"].items():
            self.assertAlmostEqual(value, float(expected[name]), places=12, msg=name)
        self.assertEqual(
            live["featureAvailableAtUtc"], expected["feature_available_time"].isoformat()
        )

    def test_future_bars_cannot_change_a_timestamped_decision(self) -> None:
        baseline = feature_snapshot(self.normalized_frame(), self.artifact, self.observed)
        changed = self.frame.copy()
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("close")] += 50.0
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("high")] += 50.0
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("low")] += 50.0
        changed.iloc[self.decision_index + 1 :, changed.columns.get_loc("open")] += 50.0
        changed_bars = server_encoded_bars(changed)
        replay = feature_snapshot(
            self.normalized_frame(bars=changed_bars), self.artifact, self.observed
        )
        self.assertEqual(baseline["features"], replay["features"])
        self.assertEqual(baseline["inputBarsSha256"], replay["inputBarsSha256"])

    def test_transparent_probability_math_matches_independent_formula(self) -> None:
        snapshot = feature_snapshot(self.normalized_frame(), self.artifact, self.observed)
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
            captured = self.scan(first)
            self.assertEqual(captured["summary"], {"decisions": 1, "outcomes": 0, "pending": 1})
            self.assertEqual(captured["lastScan"]["state"], "captured")
            first.stop()
            restarted = self.supervisor(database)
            current = self.scan(
                restarted, self.observed + pd.Timedelta(minutes=4)
            )
            self.assertEqual(current["summary"], captured["summary"])
            self.assertEqual(current["lastScan"]["state"], "current")
            self.assertTrue(current["integrity"]["ok"])
            restarted.stop()

    def test_late_bar_is_skipped_and_never_backfilled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "late.sqlite")
            late = self.frame.index[self.decision_index] + pd.Timedelta(hours=1, minutes=16)
            status = self.scan(supervisor, late)
            self.assertEqual(status["summary"]["decisions"], 0)
            self.assertEqual(status["lastScan"]["state"], "skipped")
            self.assertIn("never backfilled", status["lastScan"]["message"])
            supervisor.stop()

    def test_six_actual_market_bars_settle_with_frozen_costs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "settle.sqlite")
            self.scan(supervisor)
            settled_at = self.frame.index[self.decision_index + 6] + pd.Timedelta(
                hours=1, minutes=5
            )
            status = self.scan(supervisor, settled_at)
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
        frame = self.normalized_frame()
        snapshot = feature_snapshot(frame, self.artifact, self.observed)
        normalization = self.normalization()
        decision = build_decision_payload(
            snapshot,
            self.artifact,
            self.observed,
            normalization,
        )
        sparse = self.frame.iloc[: self.decision_index + 4].copy()
        result = build_outcome_payload(
            decision,
            sparse,
            self.artifact,
            self.frame.index[self.decision_index] + pd.Timedelta(days=3),
            normalization,
        )
        self.assertIsNone(result)

    def test_ledger_and_manifest_are_immutable_and_trial_locked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "immutable.sqlite"
            supervisor = self.supervisor(database)
            status = self.scan(supervisor)
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
            status = self.scan(supervisor)
            decision = status["records"][0]["payload"]
            self.assertEqual(decision["primary"]["action"], "abstain")
            self.assertFalse(decision["guardrails"]["executionAllowed"])
            self.assertFalse(decision["guardrails"]["consumedByAstrologyRules"])
            self.assertFalse(decision["guardrails"]["consumedByAutoSuggest"])
            self.assertFalse(decision["guardrails"]["consumedByOfficialMlNotes"])
            self.assertFalse(decision["guardrails"]["consumedByCoordinator"])
            self.assertTrue(decision["guardrails"]["mt5ReadOnly"])
            supervisor.stop()

    def test_measured_server_offset_is_normalized_with_raw_provenance(self) -> None:
        normalization = self.normalization()
        self.assertTrue(normalization["valid"])
        self.assertEqual(
            normalization["contract"], TIME_NORMALIZATION_CONTRACT
        )
        self.assertEqual(
            normalization["serverOffsetSeconds"], SERVER_OFFSET_SECONDS
        )
        normalized = normalize_bars(self.bars, normalization)
        self.assertEqual(normalized[0]["raw_time"], self.bars[0]["time"])
        self.assertEqual(normalized[0]["time"], self.utc_bars[0]["time"])

        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "normalized.sqlite")
            status = self.scan(supervisor)
            decision = status["records"][0]["payload"]
            self.assertEqual(
                decision["timeNormalization"]["contract"],
                TIME_NORMALIZATION_CONTRACT,
            )
            self.assertEqual(
                decision["rawDecisionBarOpenServerEpochSeconds"]
                - SERVER_OFFSET_SECONDS,
                int(pd.Timestamp(decision["decisionBarOpenUtc"]).timestamp()),
            )
            self.assertFalse(
                decision["timeNormalization"]["appExecutionAllowed"]
            )
            supervisor.stop()

    def test_stale_clock_probe_fails_closed_without_an_append(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "clock.sqlite")
            probe = clock_probe(self.observed, self.bars, age_seconds=31)
            status = self.scan(supervisor, probe=probe)
            self.assertEqual(status["summary"]["decisions"], 0)
            self.assertEqual(status["lastScan"]["state"], "skipped")
            self.assertIn("probe is stale", status["lastScan"]["message"])
            self.assertFalse(status["lastScan"]["timeNormalization"]["valid"])
            supervisor.stop()

    def test_offset_grid_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "offset.sqlite")
            probe = clock_probe(self.observed, self.bars)
            probe["timeTradeServerEpochSeconds"] = (
                probe["timeGmtEpochSeconds"] + 10_000
            )
            status = self.scan(supervisor, probe=probe)
            self.assertEqual(status["summary"]["decisions"], 0)
            self.assertIn("fifteen-minute grid", status["lastScan"]["message"])
            supervisor.stop()

    def test_python_and_probe_tick_disagreement_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            supervisor = self.supervisor(Path(temporary) / "tick.sqlite")
            probe = clock_probe(self.observed, self.bars)
            probe["rawTickEpochSeconds"] -= 10
            status = self.scan(supervisor, probe=probe)
            self.assertEqual(status["summary"]["decisions"], 0)
            self.assertIn("raw tick times disagree", status["lastScan"]["message"])
            supervisor.stop()

    def test_v2_evidence_file_is_never_opened_by_v3_trial(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            v2 = root / "candlestick_shadow_v2.sqlite"
            v2.write_bytes(b"immutable-v2-evidence")
            before = hashlib.sha256(v2.read_bytes()).hexdigest()
            supervisor = self.supervisor(root / "candlestick_shadow_v3.sqlite")
            status = self.scan(supervisor)
            after = hashlib.sha256(v2.read_bytes()).hexdigest()
            self.assertEqual(before, after)
            self.assertEqual(
                status["contract"],
                "GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3",
            )
            self.assertEqual(
                status["trial"]["contract"],
                "GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3",
            )
            supervisor.stop()

    def test_optional_specialist_is_startup_safe_without_a_private_model(self) -> None:
        unavailable = CandlestickShadowUnavailable("C:/missing/private-model.json")
        status = unavailable.status()

        self.assertEqual(status["availability"], "NOT_CONFIGURED")
        self.assertEqual(status["lastScan"]["state"], "skipped")
        self.assertFalse(status["guardrails"]["executionAllowed"])
        self.assertIn("optional", status["lastScan"]["message"].lower())
        self.assertEqual(unavailable.scan_once()["availability"], "NOT_CONFIGURED")


if __name__ == "__main__":
    unittest.main()
