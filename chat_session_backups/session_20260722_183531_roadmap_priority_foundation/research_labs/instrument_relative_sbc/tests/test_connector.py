from __future__ import annotations

from datetime import date

import pytest

from instrument_relative_sbc import (
    AksharaMapping,
    InstrumentIdentity,
    SourceCitation,
    connect_snapshot_to_identity,
)


SOURCE = SourceCitation(
    source_id="HUMAN_IDENTITY_RECORD",
    title="Human accepted identity record",
    source_tier="experimental_note",
    locator="record USD-1",
)


def snapshot(*, execution_allowed: bool = False, as_of: str = "2026-07-22T10:00:00+00:00"):
    return {
        "contract": "SBC_CHAKRA_LAB_SNAPSHOT_V1",
        "snapshot_id": "A" * 64,
        "as_of_utc": as_of,
        "evidence_cutoff_utc": as_of,
        "target_context": [
            {"layer": "NAME_INITIAL", "values": ["YA"]},
            {"layer": "NAKSHATRA", "values": ["MRIGASHIRA"]},
            {"layer": "RASHI", "values": ["MITHUNA"]},
            {"layer": "VOWEL", "values": ["U"]},
        ],
        "source_ids": ["SBC_SOURCE"],
        "guardrails": {
            "read_only": True,
            "timestamp_safe": True,
            "no_lookahead": True,
            "execution_allowed": execution_allowed,
            "market_data_included": False,
            "financially_validated": False,
            "guidance_only": True,
        },
    }


def identity(review_status: str = "accepted", valid_from: date = date(2020, 1, 1)):
    return InstrumentIdentity(
        instrument_id="currency:USD",
        symbol="USD",
        asset_class="currency",
        legal_name="United States dollar",
        akshara_candidates=(
            AksharaMapping(
                raw_name="USD",
                spoken_form="you ess dee",
                candidate_akshara="YA",
                mapping_method="manual",
                language="English",
                confidence=1.0,
                review_status=review_status,  # type: ignore[arg-type]
                valid_from=valid_from,
                reviewer="human",
                provenance=(SOURCE,),
            ),
        ),
        provenance=(SOURCE,),
    )


def test_exact_accepted_match_is_unscored_and_execution_locked() -> None:
    result = connect_snapshot_to_identity(snapshot(), identity())
    assert result.identity_gate_status == "accepted_identity_exact_snapshot_match_unscored"
    assert result.accepted_target_count == 1
    assert len(result.matches) == 1
    match = result.matches[0]
    assert match.target_value == "YA"
    assert match.mapping_review_status == "accepted"
    assert match.signed_value is None
    assert match.scoring_allowed is False
    assert result.contribution_emission_allowed is False
    assert result.auto_suggest_allowed is False
    assert result.ml_training_allowed is False
    assert result.mt5_input_allowed is False
    assert result.execution_allowed is False


def test_unreviewed_or_future_mapping_remains_blocked() -> None:
    unreviewed = connect_snapshot_to_identity(snapshot(), identity("unreviewed"))
    assert unreviewed.identity_gate_status == "blocked_no_time_valid_human_accepted_targets"
    assert unreviewed.matches == ()

    future = connect_snapshot_to_identity(
        snapshot(), identity("accepted", valid_from=date(2027, 1, 1))
    )
    assert future.identity_gate_status == "blocked_no_time_valid_human_accepted_targets"
    assert future.matches == ()


def test_connector_rejects_unsafe_or_naive_snapshot() -> None:
    with pytest.raises(ValueError, match="guardrails"):
        connect_snapshot_to_identity(snapshot(execution_allowed=True), identity())
    with pytest.raises(ValueError, match="UTC offset"):
        connect_snapshot_to_identity(
            snapshot(as_of="2026-07-22T10:00:00"), identity()
        )


def test_vowel_is_not_silently_treated_as_identity_akshara() -> None:
    value = snapshot()
    value["target_context"] = [{"layer": "VOWEL", "values": ["A"]}]
    result = connect_snapshot_to_identity(value, identity())
    assert result.identity_gate_status == "accepted_identity_no_snapshot_match"
    assert result.matches == ()


def test_serialized_snapshot_cannot_inject_an_uncertified_board_value() -> None:
    value = snapshot()
    value["target_context"] = [{"layer": "NAME_INITIAL", "values": ["YU"]}]
    with pytest.raises(ValueError, match="uncertified NAME_INITIAL"):
        connect_snapshot_to_identity(value, identity())
