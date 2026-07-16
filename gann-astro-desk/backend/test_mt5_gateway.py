from __future__ import annotations

import unittest
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from mt5_clock import CLOCK_PROBE_CONTRACT, TIME_NORMALIZATION_CONTRACT
from mt5_gateway import NORMALIZED_SNAPSHOT_CONTRACT, Mt5Gateway
from price_sources import validate_snapshot


TEST_CAPTURE = datetime(2026, 7, 12, 12, 30, tzinfo=timezone.utc)
TEST_SERVER_OFFSET_SECONDS = 10_800


class FakeMt5:
    TIMEFRAME_M30 = 30
    TIMEFRAME_H1 = 60
    TIMEFRAME_H4 = 240
    TIMEFRAME_D1 = 1440
    TIMEFRAME_W1 = 10080

    def symbol_select(self, _symbol: str, _enabled: bool) -> bool:
        return True

    def terminal_info(self):
        return SimpleNamespace(
            connected=True,
            trade_allowed=True,
            build=6012,
            path="C:/Program Files/MetaTrader 5",
            data_path="C:/MetaQuotes/Terminal/Test",
            commondata_path="C:/MetaQuotes/Terminal/Common",
        )

    def account_info(self):
        return SimpleNamespace(
            login=123,
            server="Test-Demo",
            company="MetaQuotes Ltd.",
            trade_allowed=True,
            trade_expert=True,
        )

    def symbol_info_tick(self, _symbol: str):
        raw_tick = int(TEST_CAPTURE.timestamp()) + TEST_SERVER_OFFSET_SECONDS
        return SimpleNamespace(
            time=raw_tick,
            time_msc=raw_tick * 1000 + 500,
            bid=145.0,
            ask=145.01,
        )

    def copy_rates_from_pos(self, _symbol: str, _timeframe: int, _position: int, count: int):
        if count == 1:
            current_h1 = TEST_CAPTURE.replace(minute=0, second=0, microsecond=0)
            return [{"time": int(current_h1.timestamp()) + TEST_SERVER_OFFSET_SECONDS}]
        return [
            {
                "time": 1_700_000_000 + index * 3600,
                "open": 150.0,
                "high": 150.2,
                "low": 149.8,
                "close": 150.1,
                "tick_volume": 100,
            }
            for index in range(count)
        ]

    def copy_rates_range(self, _symbol: str, _timeframe: int, _start: datetime, _end: datetime):
        self.last_range = (_start, _end)
        base = int(datetime(2026, 7, 12, 10, tzinfo=timezone.utc).timestamp())
        base += TEST_SERVER_OFFSET_SECONDS
        return [
            {
                "time": base + index * 3600,
                "open": 150.0 + index * 0.1,
                "high": 150.2 + index * 0.1,
                "low": 149.8 + index * 0.1,
                "close": 150.1 + index * 0.1,
                "tick_volume": 100 + index,
                "spread": 2,
                "real_volume": 0,
            }
            for index in range(3)
        ]

    def last_error(self):
        return (0, "ok")


class Mt5GatewayTests(unittest.TestCase):
    @staticmethod
    def clock_probe(observed: datetime, *, age_seconds: int = 0) -> dict:
        gmt = int(observed.timestamp()) - age_seconds
        raw_tick = int(observed.timestamp()) + TEST_SERVER_OFFSET_SECONDS
        raw_h1 = int(observed.replace(minute=0, second=0, microsecond=0).timestamp())
        raw_h1 += TEST_SERVER_OFFSET_SECONDS
        return {
            "contract": CLOCK_PROBE_CONTRACT,
            "probeSequence": 42,
            "writtenAtGmtEpochSeconds": gmt,
            "timeCurrentEpochSeconds": raw_tick,
            "timeTradeServerEpochSeconds": gmt + TEST_SERVER_OFFSET_SECONDS,
            "timeGmtEpochSeconds": gmt,
            "timeLocalEpochSeconds": gmt + 19_800,
            "timeGmtOffsetSeconds": -19_800,
            "rawTickEpochSeconds": raw_tick,
            "rawTickMilliseconds": raw_tick * 1000,
            "rawH1BarOpenEpochSeconds": raw_h1,
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

    def test_read_only_bar_contract(self) -> None:
        gateway = Mt5Gateway(autoconnect=False)
        gateway._mt5 = FakeMt5()
        gateway._set_status(connected=True, state="connected", tradeAllowed=False)
        bars = gateway.bars("USDJPY", "H1", 20)
        self.assertEqual(len(bars), 20)
        self.assertEqual(bars[-1]["close"], 150.1)
        self.assertFalse(gateway.status()["tradeAllowed"])

    def test_invalid_symbol_is_rejected(self) -> None:
        gateway = Mt5Gateway(autoconnect=False)
        with self.assertRaises(ValueError):
            gateway.bars("USDJPY;DROP", "H1", 20)

    def test_terminal_permission_is_disclosed_while_app_execution_stays_locked(self) -> None:
        gateway = Mt5Gateway(autoconnect=False)
        gateway._mt5 = FakeMt5()
        self.assertTrue(gateway._refresh())
        status = gateway.status()
        self.assertTrue(status["terminalAllowsTrading"])
        self.assertTrue(status["accountAllowsTrading"])
        self.assertTrue(status["accountExpertTradingAllowed"])
        self.assertFalse(status["appExecutionAllowed"])
        self.assertFalse(status["tradeAllowed"])
        self.assertEqual(status["executionMode"], "read_only_market_data")
        expected_raw_tick = int(TEST_CAPTURE.timestamp()) + TEST_SERVER_OFFSET_SECONDS
        self.assertEqual(status["rawLastTickServerEpochSeconds"], expected_raw_tick)
        self.assertIsNone(status["lastTickUtc"])

    def test_history_snapshot_excludes_unclosed_bar_and_records_as_of_contract(self) -> None:
        gateway = Mt5Gateway(autoconnect=False)
        gateway._mt5 = FakeMt5()
        gateway._set_status(
            connected=True,
            state="connected",
            tradeAllowed=False,
            accountLogin=123,
            server="Test-Demo",
        )
        capture = TEST_CAPTURE
        with tempfile.TemporaryDirectory() as directory:
            snapshot = gateway.save_history_snapshot(
                "USDJPY",
                "H1",
                datetime(2026, 7, 12, 9, tzinfo=timezone.utc),
                datetime(2026, 7, 12, 13, tzinfo=timezone.utc),
                Path(directory),
                captured_at=capture,
                clock_probe=self.clock_probe(capture),
            )
            stored = pd.read_parquet(snapshot["parquetPath"])
            listed = gateway.list_history_snapshots(Path(directory))
            validated, validated_frame = validate_snapshot(
                Path(directory), snapshot["snapshotId"]
            )

        self.assertEqual(snapshot["contract"], NORMALIZED_SNAPSHOT_CONTRACT)
        self.assertEqual(snapshot["timeNormalizationContract"], TIME_NORMALIZATION_CONTRACT)
        self.assertTrue(snapshot["timeNormalization"]["valid"])
        self.assertEqual(snapshot["timeNormalization"]["serverOffsetSeconds"], 10_800)
        self.assertTrue(snapshot["futureRequestClamped"])
        self.assertTrue(snapshot["noLookahead"])
        self.assertEqual(snapshot["barCount"], 2)
        self.assertEqual(snapshot["incompleteBarsExcluded"], 1)
        self.assertEqual(len(stored), 2)
        self.assertIn("raw_time", stored.columns)
        normalized_epoch = stored.index.as_unit("ns").asi8 // 1_000_000_000
        self.assertTrue(
            (
                stored["raw_time"].to_numpy(dtype="int64")
                - TEST_SERVER_OFFSET_SECONDS
                == normalized_epoch
            ).all()
        )
        self.assertEqual(
            gateway._mt5.last_range[0],
            datetime(2026, 7, 12, 12, tzinfo=timezone.utc),
        )
        self.assertEqual(
            gateway._mt5.last_range[1],
            capture + timedelta(seconds=TEST_SERVER_OFFSET_SECONDS),
        )
        self.assertEqual(listed[0]["snapshotId"], snapshot["snapshotId"])
        self.assertEqual(validated["contract"], NORMALIZED_SNAPSHOT_CONTRACT)
        self.assertEqual(len(validated_frame), 2)

    def test_history_snapshot_uses_server_clock_probe_for_a_different_symbol(self) -> None:
        gateway = Mt5Gateway(autoconnect=False)
        gateway._mt5 = FakeMt5()
        gateway._set_status(
            connected=True,
            state="connected",
            tradeAllowed=False,
            accountLogin=123,
            server="Test-Demo",
        )
        with tempfile.TemporaryDirectory() as directory:
            snapshot = gateway.save_history_snapshot(
                "AAPL",
                "H1",
                datetime(2026, 7, 12, 9, tzinfo=timezone.utc),
                datetime(2026, 7, 12, 13, tzinfo=timezone.utc),
                Path(directory),
                captured_at=TEST_CAPTURE,
                clock_probe=self.clock_probe(TEST_CAPTURE),
            )

        normalization = snapshot["timeNormalization"]
        self.assertEqual(snapshot["symbol"], "AAPL")
        self.assertEqual(normalization["validationSymbol"], "USDJPY")
        self.assertEqual(normalization["requestedSymbol"], "AAPL")
        self.assertTrue(normalization["crossSymbolOffsetApplication"])
        self.assertEqual(normalization["serverOffsetSeconds"], TEST_SERVER_OFFSET_SECONDS)

    def test_history_snapshot_rejects_stale_clock_probe_without_writing(self) -> None:
        gateway = Mt5Gateway(autoconnect=False)
        gateway._mt5 = FakeMt5()
        gateway._set_status(
            connected=True,
            state="connected",
            tradeAllowed=False,
            accountLogin=123,
            server="Test-Demo",
            terminalBuild=6012,
        )
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "probe is stale"):
                gateway.save_history_snapshot(
                    "USDJPY",
                    "H1",
                    datetime(2026, 7, 12, 9, tzinfo=timezone.utc),
                    datetime(2026, 7, 12, 12, tzinfo=timezone.utc),
                    Path(directory),
                    captured_at=TEST_CAPTURE,
                    clock_probe=self.clock_probe(TEST_CAPTURE, age_seconds=31),
                )
            self.assertEqual(list(Path(directory).rglob("*.parquet")), [])


if __name__ == "__main__":
    unittest.main()
