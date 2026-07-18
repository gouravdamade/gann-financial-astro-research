from __future__ import annotations

from typing import Any

import numpy as np


SOURCE_ID = "SHADBALA_JAYA"
STHANA_SOURCE_LOCATOR = "SHADBALA_JAYA lines 1526-1600, 1730-1736"
MINIMUM_SOURCE_LOCATOR = "BPHS Santhanam chapter 27 Shadbala minimum totals"
CLASSICAL_PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")

SIGN_ALIASES = {
    "AR": "ARIES",
    "ARIES": "ARIES",
    "MESHA": "ARIES",
    "TA": "TAURUS",
    "TAURUS": "TAURUS",
    "VRISHABHA": "TAURUS",
    "GE": "GEMINI",
    "GEMINI": "GEMINI",
    "MITHUNA": "GEMINI",
    "CN": "CANCER",
    "CANCER": "CANCER",
    "KARKATA": "CANCER",
    "LE": "LEO",
    "LEO": "LEO",
    "SIMHA": "LEO",
    "VI": "VIRGO",
    "VIRGO": "VIRGO",
    "KANYA": "VIRGO",
    "LI": "LIBRA",
    "LIBRA": "LIBRA",
    "TULA": "LIBRA",
    "THULA": "LIBRA",
    "SC": "SCORPIO",
    "SCORPIO": "SCORPIO",
    "VRISHCHIKA": "SCORPIO",
    "SG": "SAGITTARIUS",
    "SAGITTARIUS": "SAGITTARIUS",
    "DHANUS": "SAGITTARIUS",
    "CP": "CAPRICORN",
    "CAPRICORN": "CAPRICORN",
    "MAKARA": "CAPRICORN",
    "AQ": "AQUARIUS",
    "AQUARIUS": "AQUARIUS",
    "KUMBHA": "AQUARIUS",
    "PI": "PISCES",
    "PISCES": "PISCES",
    "MEENA": "PISCES",
}
SIGN_LORDS = {
    "ARIES": "MARS",
    "TAURUS": "VENUS",
    "GEMINI": "MERCURY",
    "CANCER": "MOON",
    "LEO": "SUN",
    "VIRGO": "MERCURY",
    "LIBRA": "VENUS",
    "SCORPIO": "MARS",
    "SAGITTARIUS": "JUPITER",
    "CAPRICORN": "SATURN",
    "AQUARIUS": "SATURN",
    "PISCES": "JUPITER",
}
OWN_SIGNS = {
    "SUN": {"LEO"},
    "MOON": {"CANCER"},
    "MARS": {"ARIES", "SCORPIO"},
    "MERCURY": {"GEMINI", "VIRGO"},
    "JUPITER": {"SAGITTARIUS", "PISCES"},
    "VENUS": {"TAURUS", "LIBRA"},
    "SATURN": {"CAPRICORN", "AQUARIUS"},
}
EXALTATION_SIGNS = {
    "SUN": "ARIES",
    "MOON": "TAURUS",
    "MARS": "CAPRICORN",
    "MERCURY": "VIRGO",
    "JUPITER": "CANCER",
    "VENUS": "PISCES",
    "SATURN": "LIBRA",
}
DEBILITATION_SIGNS = {
    "SUN": "LIBRA",
    "MOON": "SCORPIO",
    "MARS": "CANCER",
    "MERCURY": "PISCES",
    "JUPITER": "CAPRICORN",
    "VENUS": "VIRGO",
    "SATURN": "ARIES",
}
MOOLATRIKONA_SIGNS = {
    "SUN": "LEO",
    "MOON": "TAURUS",
    "MARS": "ARIES",
    "MERCURY": "VIRGO",
    "JUPITER": "SAGITTARIUS",
    "VENUS": "LIBRA",
    "SATURN": "AQUARIUS",
}
NATURAL_RELATIONSHIPS = {
    "SUN": {"friend": {"MOON", "MARS", "JUPITER"}, "neutral": {"MERCURY"}, "enemy": {"VENUS", "SATURN"}},
    "MOON": {"friend": {"SUN", "MERCURY"}, "neutral": {"MARS", "JUPITER", "VENUS", "SATURN"}, "enemy": set()},
    "MARS": {"friend": {"SUN", "MOON", "JUPITER"}, "neutral": {"VENUS", "SATURN"}, "enemy": {"MERCURY"}},
    "MERCURY": {"friend": {"SUN", "VENUS"}, "neutral": {"MARS", "JUPITER", "SATURN"}, "enemy": {"MOON"}},
    "JUPITER": {"friend": {"SUN", "MOON", "MARS"}, "neutral": {"SATURN"}, "enemy": {"MERCURY", "VENUS"}},
    "VENUS": {"friend": {"MERCURY", "SATURN"}, "neutral": {"MARS", "JUPITER"}, "enemy": {"SUN", "MOON"}},
    "SATURN": {"friend": {"MERCURY", "VENUS"}, "neutral": {"JUPITER"}, "enemy": {"SUN", "MOON", "MARS"}},
}
STHANA_VIRUPA_BY_DIGNITY = {
    "exaltation": 60.0,
    "moolatrikona": 45.0,
    "own": 30.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 4.0,
    "debilitation": 0.0,
    "unknown": np.nan,
}
SHADBALA_MINIMUM_TOTAL_VIRUPA = {
    "SUN": 390.0,
    "MOON": 360.0,
    "MARS": 300.0,
    "MERCURY": 420.0,
    "JUPITER": 390.0,
    "VENUS": 330.0,
    "SATURN": 300.0,
}


def normalize_body(value: Any) -> str:
    return str(value or "").strip().upper()


def normalize_sign(value: Any) -> str:
    text = str(value or "").strip().upper().replace("-", " ").replace("_", " ")
    text = " ".join(text.split())
    return SIGN_ALIASES.get(text, text)


def minimum_shadbala_total_virupa(value: Any) -> float | None:
    body = normalize_body(value)
    if body in {"AVG(ALL)", "AVG_ALL", "ALL"}:
        values = [SHADBALA_MINIMUM_TOTAL_VIRUPA[item] for item in CLASSICAL_PLANETS]
        return float(sum(values) / len(values))
    return SHADBALA_MINIMUM_TOTAL_VIRUPA.get(body)


def dignity_for_planet_in_sign(planet: Any, sign: Any) -> dict[str, Any]:
    body = normalize_body(planet)
    sign_name = normalize_sign(sign)
    if body not in OWN_SIGNS or sign_name not in SIGN_LORDS:
        return {
            "dignity_label": "unknown",
            "dignity_virupa": np.nan,
            "sign_lord": SIGN_LORDS.get(sign_name, ""),
            "sign_relation": "unknown",
            "rule_id": "STHANA_SIGN_DIGNITY_UNSUPPORTED",
        }
    if sign_name == DEBILITATION_SIGNS.get(body):
        label = "debilitation"
        relation = "enemy"
    elif sign_name == EXALTATION_SIGNS.get(body):
        label = "exaltation"
        relation = "friend"
    elif sign_name == MOOLATRIKONA_SIGNS.get(body):
        label = "moolatrikona"
        relation = "own"
    elif sign_name in OWN_SIGNS.get(body, set()):
        label = "own"
        relation = "own"
    else:
        lord = SIGN_LORDS.get(sign_name, "")
        relationships = NATURAL_RELATIONSHIPS.get(body, {})
        if lord in relationships.get("friend", set()):
            label = "friend"
            relation = "friend"
        elif lord in relationships.get("enemy", set()):
            label = "enemy"
            relation = "enemy"
        else:
            label = "neutral"
            relation = "neutral"
    return {
        "dignity_label": label,
        "dignity_virupa": float(STHANA_VIRUPA_BY_DIGNITY[label]),
        "sign_lord": SIGN_LORDS.get(sign_name, ""),
        "sign_relation": relation,
        "rule_id": "STHANA_SIGN_DIGNITY_V1",
    }


def planet_sthana_context(prefix: str, planet: Any, sign: Any) -> dict[str, Any]:
    body = normalize_body(planet)
    dignity = dignity_for_planet_in_sign(body, sign)
    minimum = minimum_shadbala_total_virupa(body)
    return {
        f"{prefix}_sign": normalize_sign(sign),
        f"{prefix}_sign_lord": dignity["sign_lord"],
        f"{prefix}_sthana_dignity_label": dignity["dignity_label"],
        f"{prefix}_sthana_dignity_virupa": dignity["dignity_virupa"],
        f"{prefix}_sign_relation": dignity["sign_relation"],
        f"{prefix}_shadbala_minimum_total_virupa": minimum if minimum is not None else np.nan,
        f"{prefix}_sthana_rule_id": dignity["rule_id"],
    }


def event_pair_sthana_context(b1: Any, b1_sign: Any, b2: Any, b2_sign: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    out.update(planet_sthana_context("event_b1", b1, b1_sign))
    out.update(planet_sthana_context("event_b2", b2, b2_sign))
    sthana_values = [
        value
        for value in [out.get("event_b1_sthana_dignity_virupa"), out.get("event_b2_sthana_dignity_virupa")]
        if value is not None and np.isfinite(float(value))
    ]
    minimum_values = [
        value
        for value in [
            out.get("event_b1_shadbala_minimum_total_virupa"),
            out.get("event_b2_shadbala_minimum_total_virupa"),
        ]
        if value is not None and np.isfinite(float(value))
    ]
    out["event_sthana_dignity_virupa_avg"] = float(sum(sthana_values) / len(sthana_values)) if sthana_values else np.nan
    out["event_shadbala_minimum_total_virupa_avg"] = (
        float(sum(minimum_values) / len(minimum_values)) if minimum_values else np.nan
    )
    out["event_sthana_rule_ids"] = "STHANA_SIGN_DIGNITY_V1|SHADBALA_MIN_TOTAL_GATE"
    out["event_sthana_source_id"] = SOURCE_ID
    out["event_sthana_source_locator"] = STHANA_SOURCE_LOCATOR
    out["event_shadbala_minimum_source_locator"] = MINIMUM_SOURCE_LOCATOR
    out["event_doctrine_feature_status"] = "basic_sthana_and_minimum_shadbala_only_pending_full_six_bala"
    return out
