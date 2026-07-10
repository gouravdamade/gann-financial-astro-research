from __future__ import annotations

from padmanabhan_timing_doctrine import (
    doctrine_metadata,
    disposition_for_planet,
    evaluate_gochara,
    pair_timing_context,
    vimshottari_dasha_context,
    whole_sign_house_from,
)


def assert_close(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if abs(float(actual) - float(expected)) > tolerance:
        raise AssertionError(f"{actual!r} != {expected!r}")


def test_whole_sign_house_counting() -> None:
    assert whole_sign_house_from(15.0, 20.0) == 1
    assert whole_sign_house_from(350.0, 5.0) == 2
    assert whole_sign_house_from(95.0, 5.0) == 10


def test_sun_vedha_and_saturn_exception() -> None:
    blocked = evaluate_gochara(
        0.0,
        {"SUN": 60.0, "JUPITER": 240.0, "SATURN": 240.0},
    )
    sun = next(item for item in blocked["details"] if item["planet"] == "SUN")
    assert sun["house_from_natal_moon"] == 3
    assert sun["vedha_house"] == 9
    assert sun["vedha_blockers"] == ["JUPITER"]
    assert sun["status"] == "favourable_blocked_by_vedha"

    exempt_only = evaluate_gochara(0.0, {"SUN": 60.0, "SATURN": 240.0})
    sun_exempt = next(item for item in exempt_only["details"] if item["planet"] == "SUN")
    assert sun_exempt["vedha_blockers"] == []
    assert sun_exempt["status"] == "favourable_unblocked"


def test_mercury_house_four_source_conflict_is_not_forced() -> None:
    out = evaluate_gochara(0.0, {"MERCURY": 90.0})
    mercury = next(item for item in out["details"] if item["planet"] == "MERCURY")
    assert mercury["status"] == "source_conflict_favourable_and_exceptional_adverse"
    assert_close(mercury["score"], 0.0)
    assert out["source_conflict_count"] == 1


def test_vimshottari_boundaries_from_ashwini_start() -> None:
    birth = "2000-01-01T00:00:00+00:00"
    at_birth = vimshottari_dasha_context(0.0, birth, birth)
    assert at_birth["birth_mahadasha_lord"] == "KETU"
    assert at_birth["mahadasha_lord"] == "KETU"
    assert at_birth["antardasha_lord"] == "KETU"

    after_eight_years = vimshottari_dasha_context(0.0, birth, "2008-01-01T00:00:00+00:00")
    assert after_eight_years["mahadasha_lord"] == "VENUS"


def test_six_rupa_gate_is_separate_from_planet_minimum() -> None:
    natal = {"SUN": 10.0, "MOON": 100.0, "JUPITER": 120.0}
    strong = disposition_for_planet("JUPITER", natal, {"JUPITER": 360.0})
    weak = disposition_for_planet("JUPITER", natal, {"JUPITER": 359.9})
    assert_close(strong["shadbala_six_rupa_score"], 1.0)
    assert_close(weak["shadbala_six_rupa_score"], -1.0)
    assert strong["temporal_quality_status"] == "not_scored_article_table_missing"


def test_pair_index_is_base_minus_quote() -> None:
    out = pair_timing_context(
        {"reference_label": "USD", "gochara_score_a": 2.0, "dasha_bhukti_score_b": 1.0, "prosperity_index_i": 3.0},
        {"reference_label": "JPY", "gochara_score_a": -1.0, "dasha_bhukti_score_b": 0.0, "prosperity_index_i": -1.0},
    )
    assert_close(out["pair_gochara_delta_a"], 3.0)
    assert_close(out["pair_prosperity_index_i"], 4.0)
    assert out["pair_direction"] == "BULLISH_BASE_VS_QUOTE"


def test_source_and_signal_safety_flags() -> None:
    metadata = doctrine_metadata()
    assert metadata["event_padmanabhan_article_complete_flag"] == 0
    assert metadata["event_padmanabhan_trade_signal_enabled"] == 0
    assert "table_2_exact_weights" in metadata["event_padmanabhan_missing_components"]


def run_all() -> None:
    test_whole_sign_house_counting()
    test_sun_vedha_and_saturn_exception()
    test_mercury_house_four_source_conflict_is_not_forced()
    test_vimshottari_boundaries_from_ashwini_start()
    test_six_rupa_gate_is_separate_from_planet_minimum()
    test_pair_index_is_base_minus_quote()
    test_source_and_signal_safety_flags()


if __name__ == "__main__":
    run_all()
    print("Padmanabhan timing doctrine tests passed")
