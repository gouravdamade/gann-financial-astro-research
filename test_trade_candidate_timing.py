from argparse import Namespace

import pandas as pd

from build_trade_candidates_from_touches import (
    build_candidates,
    entry_from_policy,
    signal_direction,
)


def test_direction_mapping_does_not_need_observed_zone_kind() -> None:
    assert signal_direction("BULLISH") == "LONG"
    assert signal_direction("BEARISH") == "SHORT"
    assert signal_direction("CONFLICT") == "NONE"


def test_next_bar_entry_is_after_signal_and_uses_open() -> None:
    index = pd.date_range("2025-01-01", periods=3, freq="1h", tz="UTC")
    price = pd.DataFrame(
        {"open": [100.0, 101.0, 102.0], "high": [101.0, 102.0, 103.0], "low": [99.0, 100.0, 101.0], "close": [100.5, 101.5, 102.5]},
        index=index,
    )

    entry = entry_from_policy(price, index[0], 100.5, "next_bar_open")

    assert entry["entry_time_utc"] == index[1]
    assert entry["entry_price"] == 101.0
    assert entry["entry_timestamp_safe"] == 1


def test_candidate_direction_comes_from_hypothesis_not_future_outcome() -> None:
    index = pd.date_range("2025-01-01", periods=5, freq="1h", tz="UTC")
    price = pd.DataFrame(
        {"open": [100.0] * 5, "high": [100.2] * 5, "low": [99.8] * 5, "close": [100.0] * 5},
        index=index,
    )
    touches = pd.DataFrame(
        [
            {
                "touch_time_local": index[0],
                "close_touch": 100.0,
                "ret_after_72h_dir": "UP",
                "ret_after_72h_pct": 1.0,
                "fx_hypothesis_direction": "BEARISH",
            }
        ]
    )
    args = Namespace(
        direction_source="none",
        entry_policy="next_bar_open",
        hold_hours=2,
        tp_pct=0.3,
        sl_pct=0.2,
        flat_pct=0.05,
    )

    result = build_candidates(touches, price, args)

    assert result.loc[0, "signal_direction"] == "NONE"
    assert result.loc[0, "observed_72h_direction"] == "UP"
