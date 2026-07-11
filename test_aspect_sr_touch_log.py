import pandas as pd

from build_aspect_sr_touch_log import map_event_windows_to_price_indices


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
