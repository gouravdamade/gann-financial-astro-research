from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from sbc.chakra_lab import (
    CHAKRA_LAB_CONTRACT,
    ChakraLabActorSelection,
    ChakraLabEngine,
    ChakraLabRequest,
    rashi_from_longitude,
)
from sbc.models import GeoLocation
from sbc.vedha import MotionClass


LOCATION = GeoLocation(
    latitude=28.6139,
    longitude=77.2090,
    timezone="Asia/Kolkata",
    altitude_m=216.0,
)
MOMENT = datetime(2026, 7, 17, 6, 30, tzinfo=timezone.utc)
BODIES = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
    "RAHU",
    "KETU",
)


def _request(
    actors: tuple[ChakraLabActorSelection, ...],
) -> ChakraLabRequest:
    return ChakraLabRequest(
        at=MOMENT,
        location=LOCATION,
        bodies=BODIES,
        actors=actors,
    )


def test_chakra_lab_snapshot_is_reproducible_and_timestamp_safe() -> None:
    engine = ChakraLabEngine()
    actors = (
        ChakraLabActorSelection("SUN"),
        ChakraLabActorSelection("MOON"),
        ChakraLabActorSelection("RAHU"),
        ChakraLabActorSelection("KETU"),
    )
    first = engine.snapshot(_request(actors))
    second = engine.snapshot(_request(actors))

    assert first.contract == CHAKRA_LAB_CONTRACT
    assert first.snapshot_id == second.snapshot_id
    assert first.as_of_utc == MOMENT
    assert first.evidence_cutoff_utc == MOMENT
    assert first.requested_at_local.isoformat() == "2026-07-17T12:00:00+05:30"
    assert (
        first.foundation_snapshot.snapshot_id == second.foundation_snapshot.snapshot_id
    )
    assert first.grid.grid_profile_id == "sbc_81_rotation_normalized_partial_v1"
    assert first.guidance is not None
    assert first.guardrails.read_only is True
    assert first.guardrails.timestamp_safe is True
    assert first.guardrails.no_lookahead is True
    assert first.guardrails.execution_allowed is False
    assert first.guardrails.market_data_included is False
    assert first.guardrails.financially_validated is False

    encoded = json.dumps(first.to_dict(), sort_keys=True).lower()
    for forbidden in (
        "entry_price",
        "exit_price",
        "profit_pips",
        "buy_signal",
        "sell_signal",
        "order_send",
    ):
        assert forbidden not in encoded


def test_variable_motion_is_visible_and_never_guessed() -> None:
    result = ChakraLabEngine().snapshot(
        _request(
            (
                ChakraLabActorSelection("SUN"),
                ChakraLabActorSelection("JUPITER"),
            )
        )
    )

    readiness = {item.body: item for item in result.actor_readiness}
    assert readiness["SUN"].status == "READY"
    assert readiness["JUPITER"].status == "MOTION_REQUIRED"
    assert result.guidance is not None
    assert {item.body for item in result.guidance.actor_resolutions} == {"SUN"}


def test_explicit_variable_motion_reaches_guidance_ledger() -> None:
    result = ChakraLabEngine().snapshot(
        _request(
            (
                ChakraLabActorSelection("JUPITER", motion_class=MotionClass.MEAN),
                ChakraLabActorSelection("SATURN", motion_class=MotionClass.RETROGRADE),
            )
        )
    )

    assert result.guidance is not None
    directions = {
        item.body: item.direction.value for item in result.guidance.actor_resolutions
    }
    assert directions == {"JUPITER": "FRONT", "SATURN": "RIGHT"}
    readiness = {item.body: item for item in result.actor_readiness}
    assert readiness["JUPITER"].motion_class == "MEAN"
    assert readiness["SATURN"].motion_class == "RETROGRADE"


def test_current_context_is_derived_from_the_same_snapshot() -> None:
    result = ChakraLabEngine().snapshot(_request((ChakraLabActorSelection("SUN"),)))
    layers = {item.layer: set(item.values) for item in result.target_context}

    assert layers["TITHI_GROUP"] == {result.foundation_snapshot.panchanga.tithi_group}
    assert len(result.position_context) == len(result.foundation_snapshot.positions)
    assert all(item.rashi in layers["RASHI"] for item in result.position_context)
    assert all(
        set(item.nakshatras) <= layers["NAKSHATRA"] for item in result.position_context
    )
    assert all(
        position.timestamp_utc == result.as_of_utc
        for position in result.foundation_snapshot.positions
    )


@pytest.mark.parametrize(
    ("longitude", "expected"),
    (
        (0.0, "MESHA"),
        (29.999999, "MESHA"),
        (30.0, "VRISHABHA"),
        (359.999999, "MEENA"),
        (360.0, "MESHA"),
        (-1.0, "MEENA"),
    ),
)
def test_rashi_mapping_has_explicit_boundaries(longitude: float, expected: str) -> None:
    assert rashi_from_longitude(longitude) == expected


def test_chakra_lab_rejects_naive_time_and_actor_outside_request() -> None:
    naive = ChakraLabRequest(
        at=datetime(2026, 7, 17, 12, 0),
        location=LOCATION,
        bodies=("SUN", "MOON"),
    )
    with pytest.raises(ValueError, match="UTC offset"):
        ChakraLabEngine().snapshot(naive)

    missing = ChakraLabRequest(
        at=MOMENT,
        location=LOCATION,
        bodies=("SUN", "MOON"),
        actors=(ChakraLabActorSelection("JUPITER", MotionClass.MEAN),),
    )
    with pytest.raises(ValueError, match="requested bodies"):
        ChakraLabEngine().snapshot(missing)
