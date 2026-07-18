from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


CLASSICAL_PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
DRIK_ENGINE_RULE_ID = "PARASHARA_DRIK_BALA_RECONCILIATION_V2"
DRIK_NORMALIZATION_RULE_ID = "DRIK_NET_DIVIDE_BY_FOUR_V1"
DRIK_NATURE_RULE_ID = "PVR_TITHI_SIGN_ASSOCIATION_NATURE_V1"
DRIK_SPECIAL_ASPECT_RULE_ID = "PYJHORA_4_8_7_ACTIVE_SPECIAL_ASPECT_RANGES_V1"
DRIK_ENGINE_STATUS = "tier_b_pyjhora_aligned_pending_independent_jhora_or_worked_example"
DRIK_NORMALIZATION_DIVISOR = 4.0

NATURAL_BENEFICS = {"JUPITER", "VENUS"}
NATURAL_MALEFICS = {"SUN", "MARS", "SATURN"}
SPECIAL_ASPECT_RANGES = {
    "SATURN": ((60.0, 90.0, 45.0), (270.0, 300.0, 45.0)),
    "MARS": ((90.0, 120.0, 15.0), (210.0, 240.0, 15.0)),
    "JUPITER": ((120.0, 150.0, 30.0), (240.0, 270.0, 30.0)),
}


@dataclass(frozen=True)
class PlanetNature:
    planet: str
    nature: str
    sign_index: int | None
    reason: str
    associated_benefics: tuple[str, ...] = ()
    associated_malefics: tuple[str, ...] = ()
    nearest_tie_breaker: str | None = None


@dataclass(frozen=True)
class DrikContribution:
    aspector: str
    target: str
    available: bool
    angle_deg: float | None
    base_virupa: float
    special_bonus_virupa: float
    gross_virupa: float
    nature: str
    nature_reason: str
    raw_signed_virupa: float
    normalized_signed_virupa: float


@dataclass(frozen=True)
class DrikResult:
    target: str
    available: bool
    drik_bala_virupa: float | None
    normalized_net_unrounded_virupa: float | None
    benefic_virupa: float | None
    malefic_virupa: float | None
    raw_net_virupa: float | None
    benefic_raw_virupa: float | None
    malefic_raw_virupa: float | None
    normalization_divisor: float
    rule_id: str
    normalization_rule_id: str
    nature_rule_id: str
    special_aspect_rule_id: str
    status: str
    aspector_natures: tuple[PlanetNature, ...]
    contributions: tuple[DrikContribution, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["aspector_natures"] = [asdict(item) for item in self.aspector_natures]
        payload["contributions"] = [asdict(item) for item in self.contributions]
        return payload


def normalize_planet(value: Any) -> str:
    return str(value or "").strip().upper().replace(" ", "_")


def normalize_longitude(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:
        return None
    return number % 360.0


def forward_angle(aspector_longitude: Any, target_longitude: Any) -> float | None:
    aspector = normalize_longitude(aspector_longitude)
    target = normalize_longitude(target_longitude)
    if aspector is None or target is None:
        return None
    return (target - aspector) % 360.0


def base_aspect_strength_virupa(angle: Any) -> float:
    try:
        value = float(angle) % 360.0
    except (TypeError, ValueError):
        return 0.0
    if 0.0 <= value < 30.0:
        return 0.0
    if 30.0 <= value < 60.0:
        return 0.5 * (value - 30.0)
    if 60.0 <= value < 90.0:
        return (value - 60.0) + 15.0
    if 90.0 <= value < 120.0:
        return 0.5 * (120.0 - value) + 30.0
    if 120.0 <= value < 150.0:
        return 150.0 - value
    if 150.0 <= value < 180.0:
        return 2.0 * (value - 150.0)
    if 180.0 <= value < 300.0:
        return 0.5 * (300.0 - value)
    return 0.0


def special_aspect_bonus_virupa(planet: Any, angle: Any) -> float:
    body = normalize_planet(planet)
    try:
        value = float(angle) % 360.0
    except (TypeError, ValueError):
        return 0.0
    for lower, upper, bonus in SPECIAL_ASPECT_RANGES.get(body, ()):
        if lower <= value < upper:
            return bonus
    return 0.0


def _sign_index(longitude: Any) -> int | None:
    value = normalize_longitude(longitude)
    return int(value // 30.0) if value is not None else None


def classify_planet_natures(
    longitudes: dict[str, float],
    *,
    sun_lon: Any = None,
    moon_lon: Any = None,
) -> dict[str, PlanetNature]:
    normalized = {
        normalize_planet(planet): value
        for planet, value in longitudes.items()
        if normalize_planet(planet) in CLASSICAL_PLANETS
    }
    if normalize_longitude(sun_lon) is not None:
        normalized["SUN"] = float(sun_lon) % 360.0
    if normalize_longitude(moon_lon) is not None:
        normalized["MOON"] = float(moon_lon) % 360.0

    natures: dict[str, PlanetNature] = {}
    for planet in CLASSICAL_PLANETS:
        sign_index = _sign_index(normalized.get(planet))
        if planet in NATURAL_BENEFICS:
            natures[planet] = PlanetNature(
                planet,
                "benefic",
                sign_index,
                "Jupiter and Venus are treated as natural benefics.",
            )
        elif planet in NATURAL_MALEFICS:
            natures[planet] = PlanetNature(
                planet,
                "malefic",
                sign_index,
                "Sun, Mars, and Saturn are treated as natural malefics.",
            )

    sun = normalize_longitude(normalized.get("SUN"))
    moon = normalize_longitude(normalized.get("MOON"))
    if sun is None or moon is None:
        moon_nature = "benefic"
        moon_reason = "Moon phase was unavailable; compatibility fallback treats Moon as benefic."
    else:
        elongation = (moon - sun) % 360.0
        moon_nature = "benefic" if elongation <= 180.0 else "malefic"
        phase_name = "waxing" if moon_nature == "benefic" else "waning"
        moon_reason = f"Moon is {phase_name}; Sun-to-Moon elongation is {elongation:.2f} degrees."
    natures["MOON"] = PlanetNature("MOON", moon_nature, _sign_index(moon), moon_reason)

    mercury_lon = normalize_longitude(normalized.get("MERCURY"))
    mercury_sign = _sign_index(mercury_lon)
    companions = [
        planet
        for planet in CLASSICAL_PLANETS
        if planet != "MERCURY"
        and mercury_sign is not None
        and _sign_index(normalized.get(planet)) == mercury_sign
    ]
    benefic_companions = tuple(
        planet for planet in companions if natures.get(planet) and natures[planet].nature == "benefic"
    )
    malefic_companions = tuple(
        planet for planet in companions if natures.get(planet) and natures[planet].nature == "malefic"
    )
    nearest: str | None = None
    if not companions or len(benefic_companions) > len(malefic_companions):
        mercury_nature = "benefic"
        if not companions:
            mercury_reason = "Mercury is alone in its sign, so it is treated as benefic."
        else:
            mercury_reason = "Mercury shares its sign with more benefics than malefics."
    elif len(malefic_companions) > len(benefic_companions):
        mercury_nature = "malefic"
        mercury_reason = "Mercury shares its sign with more malefics than benefics."
    else:
        if mercury_lon is not None and companions:
            nearest = min(
                companions,
                key=lambda planet: abs(float(normalized[planet]) - mercury_lon),
            )
        mercury_nature = (
            "benefic"
            if nearest is not None
            and natures.get(nearest)
            and natures[nearest].nature == "benefic"
            else "malefic"
        )
        mercury_reason = (
            f"Mercury has an equal benefic/malefic association count; nearest same-sign "
            f"planet {nearest or 'unavailable'} decides {mercury_nature}."
        )
    natures["MERCURY"] = PlanetNature(
        "MERCURY",
        mercury_nature,
        mercury_sign,
        mercury_reason,
        benefic_companions,
        malefic_companions,
        nearest,
    )
    return natures


def calculate_drik_bala(
    target: Any,
    longitudes: dict[str, float],
    *,
    sun_lon: Any = None,
    moon_lon: Any = None,
) -> DrikResult:
    target_body = normalize_planet(target)
    normalized = {
        normalize_planet(planet): longitude
        for planet, longitude in longitudes.items()
        if normalize_planet(planet) in CLASSICAL_PLANETS
    }
    target_lon = normalize_longitude(normalized.get(target_body))
    natures = classify_planet_natures(normalized, sun_lon=sun_lon, moon_lon=moon_lon)
    ordered_natures = tuple(natures[planet] for planet in CLASSICAL_PLANETS if planet in natures)
    if target_body not in CLASSICAL_PLANETS or target_lon is None:
        return DrikResult(
            target_body,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            DRIK_NORMALIZATION_DIVISOR,
            DRIK_ENGINE_RULE_ID,
            DRIK_NORMALIZATION_RULE_ID,
            DRIK_NATURE_RULE_ID,
            DRIK_SPECIAL_ASPECT_RULE_ID,
            DRIK_ENGINE_STATUS,
            ordered_natures,
            (),
        )

    benefic_raw = 0.0
    malefic_raw = 0.0
    contributions: list[DrikContribution] = []
    for aspector in CLASSICAL_PLANETS:
        if aspector == target_body:
            continue
        aspector_lon = normalize_longitude(normalized.get(aspector))
        nature = natures[aspector]
        angle = forward_angle(aspector_lon, target_lon)
        if angle is None:
            contributions.append(
                DrikContribution(
                    aspector,
                    target_body,
                    False,
                    None,
                    0.0,
                    0.0,
                    0.0,
                    nature.nature,
                    nature.reason,
                    0.0,
                    0.0,
                )
            )
            continue
        rounded_angle = round(angle, 2)
        base = round(base_aspect_strength_virupa(rounded_angle), 2)
        bonus = round(special_aspect_bonus_virupa(aspector, rounded_angle), 2)
        gross = round(base + bonus, 2)
        sign = 1.0 if nature.nature == "benefic" else -1.0
        raw_signed = round(gross * sign, 2)
        normalized_signed = round(raw_signed / DRIK_NORMALIZATION_DIVISOR, 6)
        if raw_signed >= 0.0:
            benefic_raw += raw_signed
        else:
            malefic_raw += raw_signed
        contributions.append(
            DrikContribution(
                aspector,
                target_body,
                True,
                rounded_angle,
                base,
                bonus,
                gross,
                nature.nature,
                nature.reason,
                raw_signed,
                normalized_signed,
            )
        )

    benefic_raw = round(benefic_raw, 2)
    malefic_raw = round(malefic_raw, 2)
    raw_net = round(benefic_raw + malefic_raw, 2)
    normalized_unrounded = raw_net / DRIK_NORMALIZATION_DIVISOR
    return DrikResult(
        target_body,
        True,
        round(normalized_unrounded, 2),
        normalized_unrounded,
        round(benefic_raw / DRIK_NORMALIZATION_DIVISOR, 6),
        round(malefic_raw / DRIK_NORMALIZATION_DIVISOR, 6),
        raw_net,
        benefic_raw,
        malefic_raw,
        DRIK_NORMALIZATION_DIVISOR,
        DRIK_ENGINE_RULE_ID,
        DRIK_NORMALIZATION_RULE_ID,
        DRIK_NATURE_RULE_ID,
        DRIK_SPECIAL_ASPECT_RULE_ID,
        DRIK_ENGINE_STATUS,
        ordered_natures,
        tuple(contributions),
    )
