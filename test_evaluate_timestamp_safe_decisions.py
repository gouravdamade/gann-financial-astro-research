from __future__ import annotations

from unittest.mock import patch

import pandas as pd

from evaluate_timestamp_safe_decisions import (
    build_packet_frame,
    chronological_fold_windows,
    cluster_decisions,
    purged_embargo_training_rows,
    touch_close_decision_time,
)


SCORES = {
    "fx_hypothesis_direction": "BEARISH",
    "fx_pair_net_score": -0.4,
    "fx_pair_conflict_ratio": 0.0,
    "fx_doctrine_hypothesis_direction": "BEARISH",
    "fx_doctrine_pair_net_score": -0.3,
    "fx_doctrine_pair_conflict_ratio": 0.0,
    "fx_base_scored_hit_count": 1,
    "fx_quote_scored_hit_count": 1,
}


def test_touch_close_is_the_decision_time_not_event_end() -> None:
    decision = touch_close_decision_time("2025-01-01T10:00:00+05:30", "H1")
    assert decision == pd.Timestamp("2025-01-01T05:30:00Z")


def test_purge_uses_label_availability_then_adds_embargo() -> None:
    history = pd.DataFrame(
        {
            "label_available_time_utc": pd.to_datetime(
                ["2025-01-01T00:00:00Z", "2025-01-03T00:00:00Z", "2025-01-04T00:00:00Z"],
                utc=True,
            )
        }
    )
    train, cutoff, purged = purged_embargo_training_rows(
        history,
        pd.Timestamp("2025-01-05T00:00:00Z"),
        pd.Timedelta(hours=48),
    )
    assert cutoff == pd.Timestamp("2025-01-03T00:00:00Z")
    assert train["label_available_time_utc"].tolist() == [
        pd.Timestamp("2025-01-01T00:00:00Z"),
        pd.Timestamp("2025-01-03T00:00:00Z"),
    ]
    assert purged == 1


def test_fold_windows_never_split_equal_decision_timestamps() -> None:
    times = pd.to_datetime(
        [
            "2025-01-01T00:00:00Z",
            "2025-01-01T00:00:00Z",
            "2025-01-02T00:00:00Z",
            "2025-01-03T00:00:00Z",
            "2025-01-04T00:00:00Z",
            "2025-01-05T00:00:00Z",
        ],
        utc=True,
    )
    frame = pd.DataFrame({"decision_time_utc": times})
    windows = chronological_fold_windows(frame, folds=2, initial_train_frac=0.4)
    assert windows == [
        (pd.Timestamp("2025-01-03T00:00:00Z"), pd.Timestamp("2025-01-04T00:00:00Z")),
        (pd.Timestamp("2025-01-05T00:00:00Z"), pd.Timestamp("2025-01-05T00:00:00Z")),
    ]


def test_cluster_counts_simultaneous_event_watches_once() -> None:
    time = pd.Timestamp("2025-01-01T01:00:00Z")
    frame = pd.DataFrame(
        [
            {
                "decision_time_utc": time,
                "label_available_time_utc": time + pd.Timedelta(hours=72),
                "packet_status": "watch",
                "predicted_direction": "bearish",
                "observed_direction": "DOWN",
                "observed_return_pct": -1.0,
            },
            {
                "decision_time_utc": time,
                "label_available_time_utc": time + pd.Timedelta(hours=72),
                "packet_status": "watch",
                "predicted_direction": "bearish",
                "observed_direction": "DOWN",
                "observed_return_pct": -1.0,
            },
        ]
    )
    clusters = cluster_decisions(frame, "UP")
    assert len(clusters) == 1
    assert clusters.iloc[0]["event_count"] == 2
    assert bool(clusters.iloc[0]["hit"])
    assert clusters.iloc[0]["signed_return_pct"] == 1.0


def evaluation_fixtures(return_pct: float, direction: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    events = pd.DataFrame(
        [
            {
                "event_id": "event-1",
                "event_family_key": "TN::MERCURY->MARS::trine",
                "timestamp": pd.Timestamp("2025-01-01T09:00:00Z"),
                "event_end": pd.Timestamp("2025-01-01T13:00:00Z"),
                "astronomy_contract_version": "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2",
            }
        ]
    )
    touches = pd.DataFrame(
        [
            {
                "event_id": "event-1",
                "pair_key": "MARS|MERCURY",
                "aspect": "trine",
                "touch_time_local": pd.Timestamp("2025-01-01T10:00:00Z"),
                "after72_time_local": pd.Timestamp("2025-01-04T10:00:00Z"),
                "close_after72": 149.0,
                "ret_after_72h_pct": return_pct,
                "ret_after_72h_dir": direction,
                "tn_hits_json": "[]",
                "base_tn_hits_json": "[]",
                "base_reference_label": "USD",
                "quote_reference_label": "JPY",
            }
        ]
    )
    price = pd.DataFrame(
        {
            "open": [150.0, 150.1, 150.2],
            "high": [150.2, 150.3, 150.4],
            "low": [149.8, 149.9, 150.0],
            "close": [150.1, 150.2, 150.3],
        },
        index=pd.date_range("2025-01-01T09:00:00Z", periods=3, freq="h"),
    )
    return events, touches, price


def test_future_label_changes_do_not_change_evaluation_packet() -> None:
    first = evaluation_fixtures(-1.0, "DOWN")
    second = evaluation_fixtures(1.0, "UP")
    with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
        first_frame, first_packets, first_quarantine = build_packet_frame(*first, timeframe="H1")
        second_frame, second_packets, second_quarantine = build_packet_frame(*second, timeframe="H1")
    assert not first_quarantine
    assert not second_quarantine
    assert first_packets[0]["packetId"] == second_packets[0]["packetId"]
    assert first_packets[0]["outcome"] is None
    assert first_frame.iloc[0]["observed_direction"] == "DOWN"
    assert second_frame.iloc[0]["observed_direction"] == "UP"
    assert first_frame.iloc[0]["packet_status"] == "watch"


def test_label_available_by_decision_is_quarantined() -> None:
    events, touches, price = evaluation_fixtures(-1.0, "DOWN")
    touches.loc[0, "after72_time_local"] = pd.Timestamp("2025-01-01T10:30:00Z")
    with patch("decision_engine.score_currency_pair_for_row", return_value=SCORES):
        frame, packets, quarantine = build_packet_frame(events, touches, price, timeframe="H1")
    assert frame.empty
    assert not packets
    assert "already available" in quarantine[0]["reason"]
