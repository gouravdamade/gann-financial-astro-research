from __future__ import annotations

import copy
import json

import pytest

from sbc.vedha import (
    DignityState,
    MotionClass,
    PlanetNature,
    VedhaActor,
    VedhaDirection,
    VedhaGuidanceEngine,
    VedhaMotionRequiredError,
    VedhaProfileBlockedError,
    load_vedha_profile,
    validate_vedha_profile,
)


PROFILE_ID = "phaladeepika_editor_vedha_guidance_v1"


def _keys(engine: VedhaGuidanceEngine, source: str, direction: str) -> tuple[str, ...]:
    return tuple(
        target.target_key for target in engine.targets_for_direction(source, direction)
    )


def _known_source_ids() -> tuple[str, ...]:
    profile = load_vedha_profile(PROFILE_ID)
    return tuple(item.source_id for item in profile.citations)


def test_three_page_worked_examples_compile_from_board_geometry() -> None:
    engine = VedhaGuidanceEngine(PROFILE_ID)

    assert _keys(engine, "KRITTIKA", "LEFT") == (
        "NAME_INITIAL:A",
        "RASHI:VRISHABHA",
        "TITHI_GROUP:NANDA",
        "TITHI_GROUP:BHADRA",
        "RASHI:TULA",
        "NAME_INITIAL:TA",
        "NAKSHATRA:VISHAKHA",
    )
    assert _keys(engine, "KRITTIKA", "FRONT") == ("NAKSHATRA:SHRAVANA",)
    assert _keys(engine, "KRITTIKA", "RIGHT") == ("NAKSHATRA:BHARANI",)

    assert set(_keys(engine, "ROHINI", "LEFT")) == {
        "NAME_INITIAL:VA",
        "RASHI:MITHUNA",
        "VOWEL:AU",
        "RASHI:KANYA",
        "NAME_INITIAL:RA",
        "NAKSHATRA:SWATI",
    }
    assert set(_keys(engine, "ROHINI", "RIGHT")) == {
        "VOWEL:U",
        "NAKSHATRA:ASHWINI",
    }
    assert _keys(engine, "ROHINI", "FRONT") == ("NAKSHATRA:ABHIJIT",)

    assert set(_keys(engine, "MRIGASHIRA", "LEFT")) == {
        "NAME_INITIAL:KA",
        "RASHI:KARKA",
        "RASHI:SIMHA",
        "NAME_INITIAL:PA",
        "NAKSHATRA:CHITRA",
    }
    assert set(_keys(engine, "MRIGASHIRA", "RIGHT")) == {
        "NAME_INITIAL:A",
        "NAME_INITIAL:LA",
        "NAKSHATRA:REVATI",
    }
    assert _keys(engine, "MRIGASHIRA", "FRONT") == ("NAKSHATRA:UTTARA_ASHADHA",)


def test_every_outer_nakshatra_has_three_deterministic_nine_target_union() -> None:
    engine = VedhaGuidanceEngine(PROFILE_ID)
    source_nakshatras = {
        entry.value
        for cell in engine.grid.cells
        for entry in cell.entries
        if entry.layer == "NAKSHATRA"
    }
    assert len(source_nakshatras) == 28
    for source in source_nakshatras:
        left = engine.targets_for_direction(source, VedhaDirection.LEFT)
        front = engine.targets_for_direction(source, VedhaDirection.FRONT)
        right = engine.targets_for_direction(source, VedhaDirection.RIGHT)
        assert len(front) == 1
        assert front[0].layer == "NAKSHATRA"
        assert len(left) + len(front) + len(right) == 9
        assert all(target.source_nakshatra == source for target in left + front + right)


def test_motion_rules_are_explicit_and_uncertified_speed_inference_fails_closed() -> (
    None
):
    engine = VedhaGuidanceEngine(PROFILE_ID)

    sun = engine.resolve_actor(VedhaActor("SUN", "KRITTIKA"))
    moon = engine.resolve_actor(VedhaActor("MOON", "KRITTIKA", moon_is_waning=False))
    rahu = engine.resolve_actor(VedhaActor("RAHU", "KRITTIKA"))
    mars = engine.resolve_actor(
        VedhaActor("MARS", "KRITTIKA", MotionClass.DIRECT_SWIFT)
    )
    jupiter = engine.resolve_actor(VedhaActor("JUPITER", "KRITTIKA", MotionClass.MEAN))
    saturn = engine.resolve_actor(
        VedhaActor("SATURN", "KRITTIKA", MotionClass.RETROGRADE)
    )

    assert sun.direction == moon.direction == mars.direction == VedhaDirection.LEFT
    assert rahu.direction == saturn.direction == VedhaDirection.RIGHT
    assert jupiter.direction == VedhaDirection.FRONT
    assert rahu.effective_multiplier == saturn.effective_multiplier == 2.0

    with pytest.raises(VedhaMotionRequiredError, match="automatic direct-speed"):
        engine.resolve_actor(VedhaActor("JUPITER", "KRITTIKA"))
    with pytest.raises(ValueError, match="outside the certified Vedha profile"):
        engine.resolve_actor(VedhaActor("NEPTUNE", "KRITTIKA", MotionClass.MEAN))


def test_guidance_ledger_keeps_favorable_adverse_and_net_units_visible() -> None:
    engine = VedhaGuidanceEngine(PROFILE_ID)
    report = engine.evaluate(
        (
            VedhaActor("JUPITER", "KRITTIKA", MotionClass.MEAN),
            VedhaActor("SATURN", "KRITTIKA", MotionClass.RETROGRADE),
        ),
        {
            "NAKSHATRA": {"SHRAVANA", "BHARANI"},
        },
    )

    assert report.matched_target_count == 2
    assert report.scored_match_count == 2
    assert report.unresolved_match_count == 0
    assert report.favorable_guidance_units == 1.0
    assert report.adverse_guidance_units == -2.0
    assert report.net_guidance_units == -1.0
    assert report.normalized_guidance_score == pytest.approx(-1.0 / 3.0)
    assert report.guidance_band == "ADVERSE_EVIDENCE_DOMINANT"
    assert report.scoring_coverage_ratio == 1.0
    assert all(item.status == "SCORED" for item in report.contributions)


def test_conditional_nature_and_modifier_precedence_are_not_guessed() -> None:
    engine = VedhaGuidanceEngine(PROFILE_ID)

    mercury = engine.evaluate(
        (VedhaActor("MERCURY", "KRITTIKA", MotionClass.MEAN),),
        {"NAKSHATRA": "SHRAVANA"},
    )
    assert mercury.matched_target_count == 1
    assert mercury.scored_match_count == 0
    assert mercury.unresolved_match_count == 1
    assert mercury.contributions[0].status == "UNRESOLVED_PLANET_NATURE"
    assert mercury.normalized_guidance_score == 0.0

    stacked = engine.evaluate(
        (
            VedhaActor(
                "SATURN",
                "KRITTIKA",
                MotionClass.RETROGRADE,
                dignity=DignityState.EXALTED,
            ),
        ),
        {"NAKSHATRA": "BHARANI"},
    )
    assert stacked.contributions[0].status == ("UNRESOLVED_MULTIPLIER_PRECEDENCE")
    assert stacked.contributions[0].signed_guidance_units is None


def test_dignity_and_context_overrides_are_auditable_not_hidden_weights() -> None:
    engine = VedhaGuidanceEngine(PROFILE_ID)
    report = engine.evaluate(
        (
            VedhaActor(
                "VENUS",
                "KRITTIKA",
                MotionClass.DIRECT_SWIFT,
                dignity=DignityState.EXALTED,
            ),
            VedhaActor(
                "MARS",
                "KRITTIKA",
                MotionClass.MEAN,
                dignity=DignityState.DEBILITATED,
            ),
            VedhaActor(
                "MERCURY",
                "KRITTIKA",
                MotionClass.MEAN,
                mercury_association_nature=PlanetNature.BENEFIC,
            ),
        ),
        {
            "RASHI": "TULA",
            "NAKSHATRA": "SHRAVANA",
        },
    )

    signed = sorted(
        item.signed_guidance_units
        for item in report.contributions
        if item.signed_guidance_units is not None
    )
    assert signed == [-0.5, 1.0, 3.0]
    assert report.net_guidance_units == 3.5
    assert report.guidance_band == "FAVORABLE_EVIDENCE_DOMINANT"


def test_target_context_rejects_uncertified_or_unknown_values() -> None:
    engine = VedhaGuidanceEngine(PROFILE_ID)
    actor = VedhaActor("JUPITER", "KRITTIKA", MotionClass.MEAN)
    with pytest.raises(ValueError, match="unsupported Vedha target layer"):
        engine.evaluate((actor,), {"WEEKDAY": "MONDAY"})
    with pytest.raises(ValueError, match="unknown NAKSHATRA"):
        engine.evaluate((actor,), {"NAKSHATRA": "NOT_A_STAR"})


def test_report_is_reproducible_guidance_only_and_contains_no_trade_opinion() -> None:
    first_engine = VedhaGuidanceEngine(PROFILE_ID)
    second_engine = VedhaGuidanceEngine(PROFILE_ID)
    actor = VedhaActor("JUPITER", "KRITTIKA", MotionClass.MEAN)
    first = first_engine.evaluate((actor,), {"NAKSHATRA": "SHRAVANA"})
    second = second_engine.evaluate((actor,), {"NAKSHATRA": "SHRAVANA"})

    assert first.vedha_profile_hash == second.vedha_profile_hash
    assert first.grid_profile_hash == second.grid_profile_hash
    assert first.guidance_only is True
    assert first.financial_validation_status == "NOT_VALIDATED"
    assert len(first.citations) == 3
    assert "TRADES" in first.blocked_capabilities
    encoded = json.dumps(first.to_dict(), sort_keys=True).lower()
    for forbidden in (
        "bullish",
        "bearish",
        "buy_signal",
        "sell_signal",
        "entry_price",
        "profit_pips",
        "order_send",
    ):
        assert forbidden not in encoded


def test_profile_validator_rejects_source_rule_and_safety_drift() -> None:
    profile = load_vedha_profile(PROFILE_ID)
    known = _known_source_ids()

    raw = copy.deepcopy(profile.raw)
    raw["unexpected"] = True
    with pytest.raises(ValueError, match="Unknown Vedha profile fields"):
        validate_vedha_profile(raw, known)

    raw = copy.deepcopy(profile.raw)
    raw["direction_geometry"]["LEFT"] = "GUESS"
    with pytest.raises(ValueError, match="unsupported or silently changed"):
        validate_vedha_profile(raw, known)

    raw = copy.deepcopy(profile.raw)
    raw["guidance_model"]["financial_validation_status"] = "VALIDATED"
    with pytest.raises(ValueError, match="NOT_VALIDATED"):
        validate_vedha_profile(raw, known)

    raw = copy.deepcopy(profile.raw)
    raw["worked_examples"][0]["expected_targets"].remove("RASHI:VRISHABHA")
    changed = validate_vedha_profile(raw, known)
    with pytest.raises(VedhaProfileBlockedError, match="worked-example mismatch"):
        VedhaGuidanceEngine(changed)
