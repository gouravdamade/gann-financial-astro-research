from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .constants import (
    BAV_BENEFIC_HOUSES,
    CONTRIBUTORS,
    EXPECTED_BAV_TOTALS,
    EXPECTED_SAV_TOTAL,
    PLANETS,
    SIGN_NAMES,
)


def normalize_sign(value: Any) -> int:
    if isinstance(value, str):
        text = value.strip().upper()
        if text in SIGN_NAMES:
            return SIGN_NAMES.index(text) + 1
        try:
            value = int(text)
        except ValueError as exc:
            raise ValueError(f"Unknown zodiac sign: {value!r}") from exc
    sign = int(value)
    if sign < 1 or sign > 12:
        raise ValueError(f"Sign index must be 1..12, got {value!r}")
    return sign


def sign_name(value: Any) -> str:
    return SIGN_NAMES[normalize_sign(value) - 1]


def sign_from_longitude(longitude: Any) -> int:
    lon = float(longitude) % 360.0
    return int(lon // 30.0) + 1


def _validated_positions(sign_positions: Mapping[str, Any]) -> dict[str, int]:
    normalized = {str(key).strip().upper(): normalize_sign(value) for key, value in sign_positions.items()}
    missing = [body for body in CONTRIBUTORS if body not in normalized]
    extra = sorted(set(normalized) - set(CONTRIBUTORS))
    if missing or extra:
        raise ValueError(f"Expected exactly {CONTRIBUTORS}; missing={missing}, extra={extra}")
    return {body: normalized[body] for body in CONTRIBUTORS}


def compute_bav(sign_positions: Mapping[str, Any]) -> dict[str, tuple[int, ...]]:
    """Compute seven unreduced BAV rows from planetary and Lagna signs."""
    positions = _validated_positions(sign_positions)
    rows: dict[str, tuple[int, ...]] = {}
    for target in PLANETS:
        counts = [0] * 12
        for contributor in CONTRIBUTORS:
            origin = positions[contributor]
            for house in BAV_BENEFIC_HOUSES[target][contributor]:
                destination = ((origin - 1) + (house - 1)) % 12
                counts[destination] += 1
        rows[target] = tuple(counts)
    return rows


def compute_sav(bav: Mapping[str, Sequence[int]]) -> tuple[int, ...]:
    missing = [planet for planet in PLANETS if planet not in bav]
    extra = sorted(set(bav) - set(PLANETS))
    if missing or extra:
        raise ValueError(f"SAV expects exactly seven BAV rows; missing={missing}, extra={extra}")
    rows = []
    for planet in PLANETS:
        row = tuple(int(value) for value in bav[planet])
        if len(row) != 12:
            raise ValueError(f"{planet} BAV row must contain 12 signs")
        if any(value < 0 or value > 8 for value in row):
            raise ValueError(f"{planet} BAV values must be 0..8")
        rows.append(row)
    return tuple(sum(row[index] for row in rows) for index in range(12))


def validate_chart(bav: Mapping[str, Sequence[int]], sav: Sequence[int] | None = None) -> dict[str, Any]:
    calculated_sav = compute_sav(bav)
    supplied_sav = tuple(int(value) for value in sav) if sav is not None else calculated_sav
    row_totals = {planet: sum(int(value) for value in bav[planet]) for planet in PLANETS}
    row_total_checks = {planet: row_totals[planet] == EXPECTED_BAV_TOTALS[planet] for planet in PLANETS}
    checks = {
        "row_totals": row_total_checks,
        "sav_matches_rows": supplied_sav == calculated_sav,
        "sav_total": sum(supplied_sav) == EXPECTED_SAV_TOTAL,
        "bav_values_in_range": all(0 <= int(value) <= 8 for planet in PLANETS for value in bav[planet]),
        "sav_values_in_range": all(0 <= int(value) <= 56 for value in supplied_sav),
    }
    return {
        "passed": all(row_total_checks.values()) and all(
            bool(checks[name]) for name in ("sav_matches_rows", "sav_total", "bav_values_in_range", "sav_values_in_range")
        ),
        "checks": checks,
        "row_totals": row_totals,
        "sav_total": sum(supplied_sav),
    }


def transit_evidence(
    natal_bav: Mapping[str, Sequence[int]],
    natal_sav: Sequence[int],
    transit_signs: Mapping[str, Any],
) -> dict[str, Any]:
    signs = {str(key).strip().upper(): normalize_sign(value) for key, value in transit_signs.items()}
    missing = [planet for planet in PLANETS if planet not in signs]
    extra = sorted(set(signs) - set(PLANETS))
    if missing or extra:
        raise ValueError(f"Transit evidence expects seven classical planets; missing={missing}, extra={extra}")
    sav = tuple(int(value) for value in natal_sav)
    if len(sav) != 12:
        raise ValueError("Natal SAV must contain 12 values")

    evidence: dict[str, Any] = {}
    sav_values = []
    own_bav_values: dict[str, int] = {}
    for planet in PLANETS:
        sign = signs[planet]
        own_bav = int(natal_bav[planet][sign - 1])
        sav_value = int(sav[sign - 1])
        own_bav_values[planet] = own_bav
        sav_values.append(sav_value)
        prefix = planet.lower()
        evidence[f"transit_{prefix}_sign"] = sign
        evidence[f"transit_{prefix}_sign_name"] = sign_name(sign)
        evidence[f"transit_{prefix}_own_bav"] = own_bav
        evidence[f"transit_{prefix}_sav"] = sav_value

    seven_planet_sav_total = sum(sav_values)
    js_sum = own_bav_values["JUPITER"] + own_bav_values["SATURN"]
    evidence.update(
        {
            "seven_planet_sav_total": seven_planet_sav_total,
            "sav_distance_from_196": seven_planet_sav_total - 196,
            "jupiter_saturn_own_bav_sum": js_sum,
            "js_distance_from_8": js_sum - 8,
        }
    )
    return evidence
