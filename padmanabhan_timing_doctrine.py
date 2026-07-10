from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd


PADMANABHAN_TIMING_RULE_ID = "PADMANABHAN_TIMING_QUAL_QUANT_V1_SOURCE_BOUNDED"
PADMANABHAN_TIMING_STATUS = (
    "experimental_source_bounded_article_page_14_plus_phaladeepika_26;"
    "article_continuation_and_weight_tables_not_recovered;walk_forward_validation_required"
)
PADMANABHAN_TIMING_SOURCE = (
    "R.A.Padmanabhan_Timing_of_Events_A_Qualitative_and_Quantitative_Study_"
    "Astrological_Magazine_vol74_1985_page14_partial;Phaladeepika_ch26"
)
SCIENTIFIC_VALIDATION_STATUS = "traditional_astrology_hypothesis_not_scientifically_validated"

CLASSICAL_TRANSIT_PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
NODE_PLANETS = ("RAHU", "KETU")
VIMSHOTTARI_ORDER = ("KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU", "JUPITER", "SATURN", "MERCURY")
VIMSHOTTARI_YEARS = {
    "KETU": 7.0,
    "VENUS": 20.0,
    "SUN": 6.0,
    "MOON": 10.0,
    "MARS": 7.0,
    "RAHU": 18.0,
    "JUPITER": 16.0,
    "SATURN": 19.0,
    "MERCURY": 17.0,
}
VIMSHOTTARI_CYCLE_YEARS = 120.0
TROPICAL_YEAR_DAYS = 365.2425
NAKSHATRA_SPAN_DEG = 360.0 / 27.0

# Phaladeepika 26.2, counted by whole sign from natal Moon.
GOCHARA_FAVOURABLE_HOUSES = {
    "SUN": {3, 6, 10, 11},
    "MOON": {1, 3, 6, 7, 10, 11},
    "MARS": {3, 6, 11},
    "MERCURY": {2, 4, 6, 8, 10, 11},
    "JUPITER": {2, 5, 7, 9, 11},
    "VENUS": {1, 2, 3, 4, 5, 8, 9, 11, 12},
    "SATURN": {3, 6, 11},
}

# Phaladeepika 26.3-8: favourable house -> obstruction house.
GOCHARA_VEDHA_HOUSES = {
    "SUN": {11: 5, 3: 9, 10: 4, 6: 12},
    "MOON": {7: 2, 1: 5, 6: 12, 11: 8, 10: 4, 3: 9},
    "MARS": {3: 12, 11: 5, 6: 9},
    "MERCURY": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
    "JUPITER": {2: 12, 11: 8, 9: 10, 5: 4, 7: 3},
    "VENUS": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 12: 6, 11: 3},
    "SATURN": {3: 12, 11: 5, 6: 9},
}

# The source explicitly exempts father/son and Moon/Mercury from mutual Vedha.
VEDHA_EXEMPT_BLOCKERS = {
    "SUN": {"SATURN"},
    "SATURN": {"SUN"},
    "MOON": {"MERCURY"},
    "MERCURY": {"MOON"},
}

# Phaladeepika 26.33-34, cited on the photographed first article page.
# These are retained as exceptional warning placements, not treated as the
# complement of favourable houses. Mercury house 4 conflicts with 26.2 and is
# deliberately neutral-scored until Padmanabhan's missing table is recovered.
GOCHARA_EXCEPTIONAL_ADVERSE_HOUSES = {
    "SUN": {1, 5, 8, 12},
    "MOON": {8},
    "MARS": {1, 7, 8, 12},
    "MERCURY": {4},
    "JUPITER": {1, 3, 8, 12},
    "VENUS": {6},
    "SATURN": {1, 8, 12},
    "RAHU": {9},
}


def normalize_planet(value: Any) -> str:
    return str(value or "").strip().upper()


def normalize_longitude(value: Any) -> float | None:
    try:
        result = float(value) % 360.0
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def whole_sign_house_from(reference_lon: Any, transit_lon: Any) -> int | None:
    reference = normalize_longitude(reference_lon)
    transit = normalize_longitude(transit_lon)
    if reference is None or transit is None:
        return None
    reference_sign = int(reference // 30.0)
    transit_sign = int(transit // 30.0)
    return ((transit_sign - reference_sign) % 12) + 1


def _timestamp(value: Any) -> pd.Timestamp | None:
    try:
        result = pd.Timestamp(value)
    except Exception:
        return None
    return None if pd.isna(result) else result


def _add_days(value: pd.Timestamp, days: float) -> pd.Timestamp:
    return value + pd.to_timedelta(float(days), unit="D")


def vimshottari_dasha_context(natal_moon_lon: Any, birth_time: Any, event_time: Any) -> dict[str, Any]:
    moon_lon = normalize_longitude(natal_moon_lon)
    birth = _timestamp(birth_time)
    event = _timestamp(event_time)
    if moon_lon is None or birth is None or event is None:
        return {
            "status": "missing_natal_moon_or_timestamp",
            "mahadasha_lord": "",
            "antardasha_lord": "",
        }
    if event.tzinfo is not None and birth.tzinfo is None:
        birth = birth.tz_localize(event.tzinfo)
    elif event.tzinfo is None and birth.tzinfo is not None:
        event = event.tz_localize(birth.tzinfo)
    elif event.tzinfo is not None and birth.tzinfo is not None:
        event = event.tz_convert(birth.tzinfo)

    nakshatra_index = int(moon_lon // NAKSHATRA_SPAN_DEG)
    natal_lord = VIMSHOTTARI_ORDER[nakshatra_index % len(VIMSHOTTARI_ORDER)]
    elapsed_fraction = (moon_lon % NAKSHATRA_SPAN_DEG) / NAKSHATRA_SPAN_DEG
    natal_lord_years = VIMSHOTTARI_YEARS[natal_lord]
    maha_start = _add_days(birth, -elapsed_fraction * natal_lord_years * TROPICAL_YEAR_DAYS)
    cycle_days = VIMSHOTTARI_CYCLE_YEARS * TROPICAL_YEAR_DAYS
    elapsed_days = (event - maha_start).total_seconds() / 86400.0
    cycle_number = int(np.floor(elapsed_days / cycle_days)) if elapsed_days >= 0 else int(np.floor(elapsed_days / cycle_days))
    cycle_start = _add_days(maha_start, cycle_number * cycle_days)
    offset_days = (event - cycle_start).total_seconds() / 86400.0
    if offset_days < 0:
        cycle_number -= 1
        cycle_start = _add_days(cycle_start, -cycle_days)
        offset_days += cycle_days

    start_index = VIMSHOTTARI_ORDER.index(natal_lord)
    rotated = VIMSHOTTARI_ORDER[start_index:] + VIMSHOTTARI_ORDER[:start_index]
    maha_lord = rotated[-1]
    maha_period_start = cycle_start
    maha_period_end = _add_days(cycle_start, cycle_days)
    consumed = 0.0
    for lord in rotated:
        duration = VIMSHOTTARI_YEARS[lord] * TROPICAL_YEAR_DAYS
        if offset_days < consumed + duration or lord == rotated[-1]:
            maha_lord = lord
            maha_period_start = _add_days(cycle_start, consumed)
            maha_period_end = _add_days(maha_period_start, duration)
            break
        consumed += duration

    maha_elapsed_days = max(0.0, (event - maha_period_start).total_seconds() / 86400.0)
    maha_years = VIMSHOTTARI_YEARS[maha_lord]
    sub_start_index = VIMSHOTTARI_ORDER.index(maha_lord)
    sub_rotated = VIMSHOTTARI_ORDER[sub_start_index:] + VIMSHOTTARI_ORDER[:sub_start_index]
    antar_lord = sub_rotated[-1]
    antar_period_start = maha_period_start
    antar_period_end = maha_period_end
    antar_consumed = 0.0
    for lord in sub_rotated:
        duration = maha_years * VIMSHOTTARI_YEARS[lord] / VIMSHOTTARI_CYCLE_YEARS * TROPICAL_YEAR_DAYS
        if maha_elapsed_days < antar_consumed + duration or lord == sub_rotated[-1]:
            antar_lord = lord
            antar_period_start = _add_days(maha_period_start, antar_consumed)
            antar_period_end = _add_days(antar_period_start, duration)
            break
        antar_consumed += duration

    return {
        "status": "deterministic_vimshottari_365_2425_day_year",
        "natal_moon_lon": moon_lon,
        "natal_nakshatra_index": nakshatra_index,
        "birth_mahadasha_lord": natal_lord,
        "birth_mahadasha_elapsed_fraction": float(elapsed_fraction),
        "cycle_number": cycle_number,
        "mahadasha_lord": maha_lord,
        "mahadasha_start": maha_period_start.isoformat(),
        "mahadasha_end": maha_period_end.isoformat(),
        "antardasha_lord": antar_lord,
        "antardasha_start": antar_period_start.isoformat(),
        "antardasha_end": antar_period_end.isoformat(),
    }


def evaluate_gochara(natal_moon_lon: Any, transit_longitudes: dict[str, Any]) -> dict[str, Any]:
    moon_lon = normalize_longitude(natal_moon_lon)
    houses = {
        normalize_planet(planet): whole_sign_house_from(moon_lon, lon)
        for planet, lon in transit_longitudes.items()
        if normalize_longitude(lon) is not None
    }
    details: list[dict[str, Any]] = []
    score = 0.0
    favourable_count = 0
    blocked_count = 0
    adverse_count = 0
    neutral_count = 0
    source_conflict_count = 0
    for planet in CLASSICAL_TRANSIT_PLANETS:
        house = houses.get(planet)
        if house is None:
            continue
        favourable = house in GOCHARA_FAVOURABLE_HOUSES.get(planet, set())
        exceptional_adverse = house in GOCHARA_EXCEPTIONAL_ADVERSE_HOUSES.get(planet, set())
        vedha_house = GOCHARA_VEDHA_HOUSES.get(planet, {}).get(house) if favourable else None
        exempt = VEDHA_EXEMPT_BLOCKERS.get(planet, set())
        blockers = sorted(
            other
            for other in CLASSICAL_TRANSIT_PLANETS
            if other != planet and other not in exempt and vedha_house is not None and houses.get(other) == vedha_house
        )
        if favourable and exceptional_adverse:
            status = "source_conflict_favourable_and_exceptional_adverse"
            signed = 0.0
            source_conflict_count += 1
        elif favourable and blockers:
            status = "favourable_blocked_by_vedha"
            signed = 0.0
            blocked_count += 1
        elif favourable:
            status = "favourable_unblocked"
            signed = 1.0
            favourable_count += 1
        elif exceptional_adverse:
            status = "exceptional_adverse"
            signed = -1.0
            adverse_count += 1
        else:
            status = "neutral_not_listed"
            signed = 0.0
            neutral_count += 1
        score += signed
        details.append(
            {
                "planet": planet,
                "house_from_natal_moon": house,
                "favourable": bool(favourable),
                "exceptional_adverse": bool(exceptional_adverse),
                "vedha_house": vedha_house,
                "vedha_blockers": blockers,
                "status": status,
                "score": signed,
            }
        )
    node_houses = {planet: houses.get(planet) for planet in NODE_PLANETS if houses.get(planet) is not None}
    node_exceptional_adverse = {
        planet: bool(house in GOCHARA_EXCEPTIONAL_ADVERSE_HOUSES.get(planet, set()))
        for planet, house in node_houses.items()
    }
    return {
        "score_a": float(score),
        "favourable_unblocked_count": favourable_count,
        "favourable_blocked_count": blocked_count,
        "exceptional_adverse_count": adverse_count,
        "neutral_count": neutral_count,
        "source_conflict_count": source_conflict_count,
        "details": details,
        "node_houses": node_houses,
        "node_exceptional_adverse": node_exceptional_adverse,
        "node_scoring_status": "raw_house_only_nodes_excluded_from_vedha_score_due_source_uncertainty",
        "method_status": "plus1_unblocked_favourable_minus1_exceptional_adverse_zero_neutral_or_blocked_provisional",
    }


def _is_waxing(natal_longitudes: dict[str, Any]) -> bool | None:
    sun = normalize_longitude(natal_longitudes.get("SUN"))
    moon = normalize_longitude(natal_longitudes.get("MOON"))
    if sun is None or moon is None:
        return None
    phase = (moon - sun) % 360.0
    return 0.0 < phase < 180.0


def natural_quality(planet: Any, natal_longitudes: dict[str, Any]) -> tuple[float, str]:
    body = normalize_planet(planet)
    if body in {"JUPITER", "VENUS"}:
        return 1.0, "natural_benefic"
    if body in {"SUN", "MARS", "SATURN", "RAHU", "KETU"}:
        return -1.0, "natural_malefic"
    if body == "MOON":
        waxing = _is_waxing(natal_longitudes)
        if waxing is None:
            return 0.0, "moon_phase_missing"
        return (1.0, "waxing_moon_benefic") if waxing else (-1.0, "waning_moon_malefic")
    if body == "MERCURY":
        return 1.0, "mercury_natural_benefic_workspace_policy_article_association_rule_not_recovered"
    return 0.0, "natural_quality_unknown"


def disposition_for_planet(
    planet: Any,
    natal_longitudes: dict[str, Any],
    natal_shadbala_totals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = normalize_planet(planet)
    natural_score, natural_status = natural_quality(body, natal_longitudes)
    try:
        shadbala_total = float((natal_shadbala_totals or {}).get(body, np.nan))
    except (TypeError, ValueError):
        shadbala_total = np.nan
    if np.isfinite(shadbala_total):
        shadbala_score = 1.0 if shadbala_total >= 360.0 else -1.0
        shadbala_status = "at_or_above_six_rupa" if shadbala_score > 0 else "below_six_rupa"
    else:
        shadbala_score = 0.0
        shadbala_status = "missing_strict_shadbala_total"
    # The photographed page names these factors but its continuation/Table 2
    # was not recovered. They stay zero rather than receiving invented rules.
    temporal_score = 0.0
    yogakaraka_score = 0.0
    total = natural_score + temporal_score + shadbala_score + yogakaraka_score
    return {
        "planet": body,
        "natural_quality_score": natural_score,
        "natural_quality_status": natural_status,
        "temporal_quality_score": temporal_score,
        "temporal_quality_status": "not_scored_article_table_missing",
        "shadbala_six_rupa_score": shadbala_score,
        "shadbala_total_virupa": shadbala_total,
        "shadbala_six_rupa_status": shadbala_status,
        "yogakaraka_score": yogakaraka_score,
        "yogakaraka_status": "not_scored_named_yoga_rules_not_recovered",
        "disposition_total": float(total),
    }


def reference_timing_context(
    *,
    reference_label: str,
    reference_time: Any,
    natal_longitudes: dict[str, Any],
    transit_longitudes: dict[str, Any],
    event_time: Any,
    natal_shadbala_totals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    natal_moon_lon = natal_longitudes.get("MOON")
    gochara = evaluate_gochara(natal_moon_lon, transit_longitudes)
    dasha = vimshottari_dasha_context(natal_moon_lon, reference_time, event_time)
    maha = disposition_for_planet(dasha.get("mahadasha_lord"), natal_longitudes, natal_shadbala_totals)
    antar = disposition_for_planet(dasha.get("antardasha_lord"), natal_longitudes, natal_shadbala_totals)
    dasha_score = float(maha.get("disposition_total", 0.0)) + float(antar.get("disposition_total", 0.0))
    prosperity_index = float(gochara["score_a"]) + dasha_score
    return {
        "reference_label": str(reference_label),
        "reference_time": str(reference_time),
        "event_time": str(event_time),
        "natal_moon_lon": normalize_longitude(natal_moon_lon),
        "gochara_score_a": float(gochara["score_a"]),
        "dasha_bhukti_score_b": dasha_score,
        "prosperity_index_i": prosperity_index,
        "gochara": gochara,
        "dasha": dasha,
        "mahadasha_disposition": maha,
        "antardasha_disposition": antar,
        "dasha_weighting_status": "mahadasha_plus_antardasha_equal_additive_provisional_article_weight_table_missing",
    }


def pair_timing_context(base: dict[str, Any], quote: dict[str, Any]) -> dict[str, Any]:
    base_a = float(base.get("gochara_score_a", 0.0))
    quote_a = float(quote.get("gochara_score_a", 0.0))
    base_b = float(base.get("dasha_bhukti_score_b", 0.0))
    quote_b = float(quote.get("dasha_bhukti_score_b", 0.0))
    base_i = float(base.get("prosperity_index_i", base_a + base_b))
    quote_i = float(quote.get("prosperity_index_i", quote_a + quote_b))
    pair_i = base_i - quote_i
    if pair_i > 0:
        direction = "BULLISH_BASE_VS_QUOTE"
    elif pair_i < 0:
        direction = "BEARISH_BASE_VS_QUOTE"
    else:
        direction = "NEUTRAL_OR_CONFLICT"
    return {
        "base_label": str(base.get("reference_label", "BASE")),
        "quote_label": str(quote.get("reference_label", "QUOTE")),
        "base_gochara_score_a": base_a,
        "quote_gochara_score_a": quote_a,
        "pair_gochara_delta_a": base_a - quote_a,
        "base_dasha_bhukti_score_b": base_b,
        "quote_dasha_bhukti_score_b": quote_b,
        "pair_dasha_bhukti_delta_b": base_b - quote_b,
        "base_prosperity_index_i": base_i,
        "quote_prosperity_index_i": quote_i,
        "pair_prosperity_index_i": pair_i,
        "pair_direction": direction,
        "pair_formula": "I_basequote=(A_base+B_base)-(A_quote+B_quote)",
    }


def flatten_reference_timing(prefix: str, context: dict[str, Any]) -> dict[str, Any]:
    dasha = context.get("dasha", {})
    gochara = context.get("gochara", {})
    maha = context.get("mahadasha_disposition", {})
    antar = context.get("antardasha_disposition", {})
    return {
        f"{prefix}_reference_label": context.get("reference_label", ""),
        f"{prefix}_natal_moon_lon": context.get("natal_moon_lon", np.nan),
        f"{prefix}_gochara_score_a": context.get("gochara_score_a", np.nan),
        f"{prefix}_dasha_bhukti_score_b": context.get("dasha_bhukti_score_b", np.nan),
        f"{prefix}_prosperity_index_i": context.get("prosperity_index_i", np.nan),
        f"{prefix}_mahadasha_lord": dasha.get("mahadasha_lord", ""),
        f"{prefix}_antardasha_lord": dasha.get("antardasha_lord", ""),
        f"{prefix}_mahadasha_disposition": maha.get("disposition_total", np.nan),
        f"{prefix}_antardasha_disposition": antar.get("disposition_total", np.nan),
        f"{prefix}_gochara_favourable_count": gochara.get("favourable_unblocked_count", 0),
        f"{prefix}_gochara_blocked_count": gochara.get("favourable_blocked_count", 0),
        f"{prefix}_gochara_adverse_count": gochara.get("exceptional_adverse_count", 0),
        f"{prefix}_gochara_source_conflict_count": gochara.get("source_conflict_count", 0),
        f"{prefix}_gochara_details_json": json.dumps(gochara.get("details", []), ensure_ascii=True),
        f"{prefix}_dasha_details_json": json.dumps(dasha, ensure_ascii=True),
        f"{prefix}_disposition_details_json": json.dumps(
            {"mahadasha": maha, "antardasha": antar}, ensure_ascii=True
        ),
        f"{prefix}_node_houses_json": json.dumps(gochara.get("node_houses", {}), ensure_ascii=True),
        f"{prefix}_node_exceptional_adverse_json": json.dumps(
            gochara.get("node_exceptional_adverse", {}), ensure_ascii=True
        ),
        f"{prefix}_dasha_weighting_status": context.get("dasha_weighting_status", ""),
    }


def flatten_pair_timing(prefix: str, context: dict[str, Any]) -> dict[str, Any]:
    return {f"{prefix}_{key}": value for key, value in context.items()}


def doctrine_metadata() -> dict[str, Any]:
    return {
        "event_padmanabhan_timing_rule_id": PADMANABHAN_TIMING_RULE_ID,
        "event_padmanabhan_timing_status": PADMANABHAN_TIMING_STATUS,
        "event_padmanabhan_timing_source": PADMANABHAN_TIMING_SOURCE,
        "event_padmanabhan_scientific_validation_status": SCIENTIFIC_VALIDATION_STATUS,
        "event_padmanabhan_article_complete_flag": 0,
        "event_padmanabhan_trade_signal_enabled": 0,
        "event_padmanabhan_missing_components": (
            "article_continuation|table_2_exact_weights|temporal_quality_rules|"
            "named_yogakaraka_rules|external_dasha_shadbala_crosscheck|walk_forward_validation"
        ),
    }
