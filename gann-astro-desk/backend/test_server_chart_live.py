from __future__ import annotations

import os
import unittest
from unittest.mock import Mock, patch


class LiveChartHistoryProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["GANN_ASTRO_API_TOKEN"] = "live-chart-test-token-20261001"
        os.environ["GANN_ASTRO_MT5_AUTOCONNECT"] = "0"
        os.environ["GANN_ASTRO_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_CANDLE_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_REFRESH_AUTOSTART"] = "0"
        import server

        cls.server = server
        cls.app = server.app
        cls.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)

    def setUp(self) -> None:
        self.client = self.app.test_client()
        self.headers = {"X-Gann-Astro-Token": "live-chart-test-token-20261001"}

    @staticmethod
    def live_bars(count: int, *, close_offset: float = 0.0) -> list[dict[str, object]]:
        return [
            {
                "time": 1_800_000_000 + index * 86_400,
                "open": 150.0 + close_offset,
                "high": 151.0 + close_offset,
                "low": 149.0 + close_offset,
                "close": 150.5 + close_offset,
                "volume": 100 + index,
            }
            for index in range(count)
        ]

    def get_live(self, *, symbol: str = "USDJPY", timeframe: str = "D1", count: int = 12):
        return self.client.get(
            "/api/chart",
            query_string={
                "source": "live",
                "symbol": symbol,
                "timeframe": timeframe,
                "liveBarCount": str(count),
            },
            headers=self.headers,
        )

    def test_usdjpy_uses_one_bounded_mt5_fetch_for_both_visible_and_rsi_history(self) -> None:
        all_bars = self.live_bars(120)
        overlay = {
            "symbol": "USDJPY",
            "timeframe": "D1",
            "candles": [{"time": 1, "close": 9_000.0}],
            "indicatorHistory": {"candles": [{"time": 2, "close": 8_000.0}]},
        }
        gateway = Mock()
        gateway.bars.return_value = all_bars
        with patch.object(self.server, "gateway", gateway), patch.object(
            self.server.repository, "chart_payload", return_value=overlay
        ) as chart_payload:
            response = self.get_live()

        self.assertEqual(response.status_code, 200)
        chart = response.get_json()["chart"]
        gateway.bars.assert_called_once_with(symbol="USDJPY", timeframe="D1", count=1012)
        chart_payload.assert_called_once()
        self.assertEqual(chart["dataSource"], "mt5_live")
        self.assertEqual(chart["candles"], all_bars[-12:])
        self.assertEqual(chart["indicatorHistory"]["candles"], all_bars[:-12])
        self.assertLess(
            chart["indicatorHistory"]["candles"][-1]["time"],
            chart["candles"][0]["time"],
        )
        self.assertEqual(
            {item["time"] for item in chart["candles"]}
            & {item["time"] for item in chart["indicatorHistory"]["candles"]},
            set(),
        )
        self.assertTrue(all(item["close"] < 1_000 for item in chart["candles"]))
        self.assertTrue(all(item["close"] < 1_000 for item in chart["indicatorHistory"]["candles"]))
        self.assertEqual(chart["candles"][-1]["time"], all_bars[-1]["time"])

    def test_live_history_is_bounded_to_1000_preceding_bars(self) -> None:
        all_bars = self.live_bars(1_500)
        gateway = Mock()
        gateway.bars.return_value = all_bars
        with patch.object(self.server, "gateway", gateway), patch.object(
            self.server.repository, "chart_payload", return_value={}
        ):
            chart = self.get_live().get_json()["chart"]

        self.assertEqual(len(chart["candles"]), 12)
        self.assertEqual(len(chart["indicatorHistory"]["candles"]), 1_000)
        self.assertEqual(chart["indicatorHistory"]["candles"], all_bars[-1_012:-12])
        self.assertEqual(gateway.bars.call_args.kwargs["count"], 1_012)

    def test_limited_history_keeps_latest_visible_bars_first(self) -> None:
        all_bars = self.live_bars(20)
        gateway = Mock()
        gateway.bars.return_value = all_bars
        with patch.object(self.server, "gateway", gateway), patch.object(
            self.server.repository, "chart_payload", return_value={}
        ):
            chart = self.get_live().get_json()["chart"]

        self.assertEqual(chart["candles"], all_bars[-12:])
        self.assertEqual(chart["indicatorHistory"]["candles"], all_bars[:8])
        self.assertEqual(chart["candles"][-1], all_bars[-1])

    def test_insufficient_history_returns_all_bars_as_visible_without_fabrication(self) -> None:
        all_bars = self.live_bars(10)
        gateway = Mock()
        gateway.bars.return_value = all_bars
        with patch.object(self.server, "gateway", gateway), patch.object(
            self.server.repository, "chart_payload", return_value={}
        ):
            chart = self.get_live().get_json()["chart"]

        self.assertEqual(chart["candles"], all_bars)
        self.assertEqual(chart["indicatorHistory"]["candles"], [])

    def test_non_usdjpy_live_chart_keeps_mt5_history_and_skips_research_overlay(self) -> None:
        all_bars = self.live_bars(30, close_offset=0.25)
        gateway = Mock()
        gateway.bars.return_value = all_bars
        with patch.object(self.server, "gateway", gateway), patch.object(
            self.server.repository, "chart_payload"
        ) as chart_payload:
            response = self.get_live(symbol="EURUSD", timeframe="H4")

        self.assertEqual(response.status_code, 200)
        chart = response.get_json()["chart"]
        gateway.bars.assert_called_once_with(symbol="EURUSD", timeframe="H4", count=1012)
        chart_payload.assert_not_called()
        self.assertEqual(chart["dataSource"], "mt5_live")
        self.assertEqual(chart["candles"], all_bars[-12:])
        self.assertEqual(chart["indicatorHistory"]["candles"], all_bars[:-12])

    def test_live_timeframes_preserve_same_source_boundary(self) -> None:
        for timeframe in ("H1", "H4", "D1", "W1"):
            all_bars = self.live_bars(25)
            gateway = Mock()
            gateway.bars.return_value = all_bars
            with patch.object(self.server, "gateway", gateway), patch.object(
                self.server.repository, "chart_payload", return_value={}
            ):
                response = self.get_live(timeframe=timeframe)

            self.assertEqual(response.status_code, 200)
            chart = response.get_json()["chart"]
            self.assertEqual(chart["dataSource"], "mt5_live")
            self.assertEqual(chart["candles"], all_bars[-12:])
            self.assertEqual(chart["indicatorHistory"]["candles"], all_bars[:-12])
            self.assertEqual(gateway.bars.call_args.kwargs["timeframe"], timeframe)


if __name__ == "__main__":
    unittest.main()
