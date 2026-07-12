from __future__ import annotations

import unittest
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from mt5_gateway import Mt5Gateway


class FakeMt5:
    TIMEFRAME_M30 = 30
    TIMEFRAME_H1 = 60
    TIMEFRAME_H4 = 240
    TIMEFRAME_D1 = 1440

    def symbol_select(self, _symbol: str, _enabled: bool) -> bool:
        return True

    def copy_rates_from_pos(self, _symbol: str, _timeframe: int, _position: int, count: int):
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
        base = int(datetime(2026, 7, 12, 10, tzinfo=timezone.utc).timestamp())
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
        capture = datetime(2026, 7, 12, 12, 30, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            snapshot = gateway.save_history_snapshot(
                "USDJPY",
                "H1",
                datetime(2026, 7, 12, 9, tzinfo=timezone.utc),
                datetime(2026, 7, 12, 13, tzinfo=timezone.utc),
                Path(directory),
                captured_at=capture,
            )
            stored = pd.read_parquet(snapshot["parquetPath"])
            listed = gateway.list_history_snapshots(Path(directory))

        self.assertEqual(snapshot["contract"], "MT5_TIMESTAMPED_CLOSED_BARS_V1")
        self.assertTrue(snapshot["futureRequestClamped"])
        self.assertTrue(snapshot["noLookahead"])
        self.assertEqual(snapshot["barCount"], 2)
        self.assertEqual(snapshot["incompleteBarsExcluded"], 1)
        self.assertEqual(len(stored), 2)
        self.assertEqual(listed[0]["snapshotId"], snapshot["snapshotId"])


if __name__ == "__main__":
    unittest.main()
