from pathlib import Path
from unittest.mock import patch

from reviewer_rule_replay import replay_completed_review_impacts


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
