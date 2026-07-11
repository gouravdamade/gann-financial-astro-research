import pandas as pd

from evaluate_transitsign_walk_forward import is_feature_column, purged_training_rows


def test_horizon_embargo_is_not_algebraically_cancelled() -> None:
    history = pd.DataFrame(
        {
            "close_time_utc": pd.to_datetime(
                ["2025-01-01T00:00:00Z", "2025-01-03T00:00:00Z", "2025-01-04T00:00:00Z"],
                utc=True,
            )
        }
    )
    test_start = pd.Timestamp("2025-01-05T00:00:00Z")
    train, cutoff = purged_training_rows(history, test_start, pd.Timedelta(hours=72))
    assert cutoff == pd.Timestamp("2025-01-02T00:00:00Z")
    assert train["close_time_utc"].tolist() == [pd.Timestamp("2025-01-01T00:00:00Z")]


def test_same_bar_prices_are_excluded_until_timing_contract_is_explicit() -> None:
    for column in ("open_touch", "high_touch", "low_touch", "close_touch", "entry_price"):
        assert not is_feature_column(column)
