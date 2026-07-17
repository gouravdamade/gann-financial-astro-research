from pathlib import Path
from unittest.mock import patch

import pytest

from reviewer_rule_replay import (
    auto_suggest_case,
    replay_completed_review_impacts,
)


GOLDEN_PACK = Path(
    r"D:\GannFinancialAstro\doc"
    r"\repeatation_review_case_8_avg_all_moon_square_20260711_022803"
)


def replay_projection(value: dict) -> dict:
    auto = value.get("auto_suggestion") or {}
    return {
        "outcome_label": value.get("outcome_label"),
        "entry_price": value.get("entry_price"),
        "exit_price": value.get("exit_price"),
        "signed_pips": value.get("signed_pips"),
        "raw_pips": value.get("raw_pips"),
        "start_rule": value.get("start_rule"),
        "end_rule": value.get("end_rule"),
        "start_source": (value.get("trade_start") or {}).get("source"),
        "start_x": (value.get("trade_start") or {}).get("x"),
        "end_source": (value.get("trade_end") or {}).get("source"),
        "end_x": (value.get("trade_end") or {}).get("x"),
        "family_rule": auto.get("applied_family_rule"),
        "break_status": (auto.get("break_confirmation") or {}).get("status"),
        "gann_status": auto.get("gann_fan_exit_rule_status"),
    }


GOLDEN_PROJECTIONS = {
    8: {
        "outcome_label": "bearish",
        "entry_price": 147.745,
        "exit_price": 147.512,
        "signed_pips": 23.3,
        "raw_pips": -23.3,
        "start_rule": "family_rule_case_window_entry_open_price",
        "end_rule": "confirmed_break_next_shaded_zone_boundary",
        "start_source": "auto_case_window_entry",
        "start_x": "2025-03-07 19:30:00+05:30",
        "end_source": "auto_zone_boundary",
        "end_x": "2025-03-07T23:30:00+05:30",
        "family_rule": "bearish_bias_support_barrier",
        "break_status": "confirmed",
        "gann_status": "blocked_no_multi_aspect_overlap",
    },
    43: {
        "outcome_label": "bearish",
        "entry_price": 146.158,
        "exit_price": 146.021,
        "signed_pips": 13.7,
        "raw_pips": -13.7,
        "start_rule": "family_rule_case_window_entry_open_price",
        "end_rule": "confirmed_break_next_shaded_zone_boundary",
        "start_source": "auto_case_window_entry",
        "start_x": "2025-04-04 02:30:00+05:30",
        "end_source": "auto_zone_boundary",
        "end_x": "2025-04-04T05:30:00+05:30",
        "family_rule": "bearish_bias_support_barrier",
        "break_status": "confirmed",
        "gann_status": "blocked_no_multi_aspect_overlap",
    },
    103: {
        "outcome_label": "bearish",
        "entry_price": 145.792,
        "exit_price": 145.21480079913766,
        "signed_pips": 57.7,
        "raw_pips": -57.7,
        "start_rule": "family_rule_case_window_entry_open_price",
        "end_rule": "global_first_sr_touch_target",
        "start_source": "auto_case_window_entry",
        "start_x": "2025-05-15 22:30:00+05:30",
        "end_source": "auto_sr_line_touch",
        "end_x": "2025-05-16T09:00:00+05:30",
        "family_rule": "bearish_bias_support_barrier",
        "break_status": "confirmed",
        "gann_status": "blocked_no_multi_aspect_overlap",
    },
    127: {
        "outcome_label": "bearish",
        "entry_price": 144.965,
        "exit_price": 144.925,
        "signed_pips": 4.0,
        "raw_pips": -4.0,
        "start_rule": "first_case_window_sr_line_touch",
        "end_rule": "gann_second_from_bottom_touch_multi_aspect",
        "start_source": None,
        "start_x": "2025-05-28T22:00:00+05:30",
        "end_source": "auto_gann_fan_second_from_bottom_touch",
        "end_x": "2025-05-28T23:00:00+05:30",
        "family_rule": None,
        "break_status": "confirmed",
        "gann_status": "provisional_review_required",
    },
    185: {
        "outcome_label": "bullish",
        "entry_price": 144.786,
        "exit_price": 144.791,
        "signed_pips": 0.5,
        "raw_pips": 0.5,
        "start_rule": "first_case_window_sr_line_touch",
        "end_rule": "gann_second_from_bottom_touch_multi_aspect",
        "start_source": None,
        "start_x": "2025-06-25T07:30:00+05:30",
        "end_source": "auto_gann_fan_second_from_bottom_touch",
        "end_x": "2025-06-25T08:00:00+05:30",
        "family_rule": None,
        "break_status": "confirmed",
        "gann_status": "provisional_review_required",
    },
}


@pytest.mark.skipif(not GOLDEN_PACK.exists(), reason="local review pack is unavailable")
@pytest.mark.parametrize("case_id", sorted(GOLDEN_PROJECTIONS))
def test_decomposed_auto_suggest_matches_golden_cases(case_id: int) -> None:
    replay = auto_suggest_case(GOLDEN_PACK, case_id)
    assert replay_projection(replay) == GOLDEN_PROJECTIONS[case_id]


def test_historical_replay_preserves_ignored_reviews() -> None:
    rows = [
        {
            "case_id": 185,
            "review_status": "ignored",
            "signed_pips": None,
            "start_rule": "",
            "end_rule": "",
        }
    ]
    with patch("reviewer_rule_replay.auto_suggest_case") as auto_suggest:
        result = replay_completed_review_impacts(Path("unused"), rows)
    auto_suggest.assert_not_called()
    assert result["reviewed_count"] == 1
    assert result["skipped_ignored_count"] == 1
    assert result["affected_count"] == 0


def test_historical_replay_still_checks_completed_trade_reviews() -> None:
    rows = [
        {
            "case_id": 8,
            "review_status": "completed",
            "signed_pips": 10.0,
            "start_rule": "old_start",
            "end_rule": "old_end",
        }
    ]
    replay = {
        "signed_pips": 12.0,
        "start_rule": "new_start",
        "end_rule": "new_end",
    }
    with patch("reviewer_rule_replay.auto_suggest_case", return_value=replay):
        result = replay_completed_review_impacts(Path("unused"), rows)
    assert result["skipped_ignored_count"] == 0
    assert result["affected_count"] == 1
    assert result["affected_or_needs_replay"][0]["pips_delta"] == 2.0
