from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
