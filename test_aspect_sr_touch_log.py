import pandas as pd

from build_aspect_sr_touch_log import filter_events_within_price_source, map_event_windows_to_price_indices


def test_event_window_mapping_never_borrows_an_outside_candle() -> None:
    price_index = pd.DatetimeIndex(
        [
            "2025-01-03T20:00:00Z",
            "2025-01-06T00:00:00Z",
            "2025-01-06T01:00:00Z",
        ]
    )
    starts = pd.Series(pd.to_datetime(["2025-01-04T00:00:00Z", "2025-01-05T23:30:00Z"]))
    ends = pd.Series(pd.to_datetime(["2025-01-05T00:00:00Z", "2025-01-06T00:30:00Z"]))

    idx_start, idx_end, valid = map_event_windows_to_price_indices(price_index, starts, ends)

    assert not bool(valid[0])
    assert bool(valid[1])
    assert idx_start[1] == 1
    assert idx_end[1] == 1


def test_event_start_between_bars_remains_eligible_for_contained_mapping() -> None:
    price_index = pd.date_range("2025-09-24T00:30:00+05:30", periods=12, freq="h")
    events = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2025-09-24T02:01:33+05:30", "2025-09-23T23:00:00+05:30"]
            ),
            "event_end": pd.to_datetime(
                ["2025-09-24T08:39:19+05:30", "2025-09-24T02:00:00+05:30"]
            ),
        }
    )

    eligible = filter_events_within_price_source(events, price_index)
    idx_start, idx_end, valid = map_event_windows_to_price_indices(
        price_index,
        eligible["timestamp"],
        eligible["event_end"],
    )

    assert len(eligible) == 1
    assert bool(valid[0])
    assert price_index[idx_start[0]] == pd.Timestamp("2025-09-24T02:30:00+05:30")
    assert price_index[idx_end[0]] == pd.Timestamp("2025-09-24T08:30:00+05:30")
