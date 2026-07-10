from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from .constants import PLANETS, SIGN_NAMES
from .core import normalize_sign


SIGN_LORDS = {
    1: "MARS",
    2: "VENUS",
    3: "MERCURY",
    4: "MOON",
    5: "SUN",
    6: "MERCURY",
    7: "VENUS",
    8: "MARS",
    9: "JUPITER",
    10: "SATURN",
    11: "SATURN",
    12: "JUPITER",
}

ASPECT_HOUSES = {
    "SUN": (7,),
    "MOON": (7,),
    "MARS": (4, 7, 8),
    "MERCURY": (7,),
    "JUPITER": (5, 7, 9),
    "VENUS": (7,),
    "SATURN": (3, 7, 10),
}

NATURAL_SAMDHARMI = {
    frozenset(("VENUS", "SATURN")),
    frozenset(("MARS", "SUN")),
    frozenset(("MARS", "MOON")),
}
FOUR_TEN_MALEFIC_RECIPIENTS = {"SUN", "MARS", "SATURN"}

SIGN_MULTIPLIERS = {
    "SUN": (1.4, 0.5, 1.0, 1.2, 1.4, 1.0, 0.4, 1.2, 1.2, 0.4, 0.5, 1.2),
    "MOON": (1.0, 1.4, 1.2, 1.2, 1.2, 1.2, 1.0, 0.8, 1.0, 1.0, 1.0, 1.0),
    "MARS": (1.4, 1.0, 0.5, 1.0, 1.2, 0.5, 1.0, 1.2, 1.2, 1.2, 1.0, 1.2),
    "MERCURY": (1.0, 1.2, 1.2, 0.5, 1.2, 1.6, 1.2, 1.0, 1.0, 1.0, 1.0, 0.8),
    "JUPITER": (1.2, 0.5, 0.5, 1.4, 1.2, 0.5, 0.5, 1.2, 1.4, 0.8, 1.0, 1.2),
    "VENUS": (1.0, 1.2, 1.2, 0.5, 0.5, 1.0, 1.4, 1.0, 1.0, 1.2, 1.2, 1.2),
    "SATURN": (0.4, 1.2, 1.2, 0.5, 0.5, 1.2, 1.4, 0.5, 1.0, 1.2, 1.4, 1.0),
}


def house_from_sign(sign: int, lagna_sign: int) -> int:
    return ((normalize_sign(sign) - normalize_sign(lagna_sign)) % 12) + 1


def sign_from_house(house: int, lagna_sign: int) -> int:
    return ((normalize_sign(lagna_sign) - 1 + int(house) - 1) % 12) + 1


def relative_house(origin: int, destination: int) -> int:
    return ((int(destination) - int(origin)) % 12) + 1


def event_houses(house_b: int) -> dict[str, int]:
    b = int(house_b)
    if b < 1 or b > 12:
        raise ValueError("House B must be in 1..12")
    a = ((b - 1 + 7) % 12) + 1
    return {
        "A": a,
        "B": b,
        "C": ((a - 1 + 9) % 12) + 1,
        "D": ((a - 1 + 2) % 12) + 1,
        "E": ((a - 1 + 10) % 12) + 1,
    }


def inverse_aspect_points(bindus: int) -> int:
    value = int(bindus)
    if value < 0 or value > 8:
        raise ValueError("Bindus must be in 0..8")
    if value < 4:
        return 8 - value
    if value == 4:
        return 0
    return -value


def aspected_houses(planet: str, occupied_house: int) -> tuple[int, ...]:
    body = str(planet).upper()
    return tuple(((int(occupied_house) - 1 + sight - 1) % 12) + 1 for sight in ASPECT_HOUSES[body])


def _validated_bav(bav: Mapping[str, Sequence[int]]) -> dict[str, tuple[int, ...]]:
    rows = {str(key).upper(): tuple(int(value) for value in values) for key, values in bav.items()}
    if set(rows) != set(PLANETS):
        raise ValueError("KAS worksheet requires seven classical BAV rows")
    if any(len(rows[planet]) != 12 for planet in PLANETS):
        raise ValueError("Every BAV row must contain 12 values")
    return rows


def _planet_context(
    bav: Mapping[str, Sequence[int]],
    sign_positions: Mapping[str, Any],
    lagna_sign: Any,
) -> tuple[dict[str, tuple[int, ...]], dict[str, int], dict[str, int], dict[str, int]]:
    rows = _validated_bav(bav)
    signs = {str(key).upper(): normalize_sign(value) for key, value in sign_positions.items() if str(key).upper() in PLANETS}
    if set(signs) != set(PLANETS):
        raise ValueError("KAS worksheet requires signs for all seven classical planets")
    lagna = normalize_sign(lagna_sign)
    houses = {planet: house_from_sign(signs[planet], lagna) for planet in PLANETS}
    natal_bindus = {planet: rows[planet][signs[planet] - 1] for planet in PLANETS}
    return rows, signs, houses, natal_bindus


def _samdharmi_relations(
    houses: Mapping[str, int],
    natal_bindus: Mapping[str, int],
    nakshatras: Mapping[str, int] | None,
    navamsa_signs: Mapping[str, int] | None,
) -> list[dict[str, Any]]:
    nak = {str(key).upper(): int(value) for key, value in (nakshatras or {}).items()}
    nav = {str(key).upper(): normalize_sign(value) for key, value in (navamsa_signs or {}).items()}
    relations: list[dict[str, Any]] = []
    for index, left in enumerate(PLANETS):
        for right in PLANETS[index + 1 :]:
            reasons = []
            pair = frozenset((left, right))
            if pair in NATURAL_SAMDHARMI and relative_house(houses[left], houses[right]) != 7:
                reasons.append("natural_pair")
            if houses[left] == houses[right]:
                reasons.append("same_rasi")
            if left in nak and right in nak and nak[left] == nak[right]:
                reasons.append("same_nakshatra")
            if left in nav and right in nav and nav[left] == nav[right]:
                reasons.append("same_navamsa")
            relation = relative_house(houses[left], houses[right])
            reverse = relative_house(houses[right], houses[left])
            if {relation, reverse} == {4, 10}:
                stronger = left if natal_bindus[left] > natal_bindus[right] else right
                weaker = right if stronger == left else left
                if natal_bindus[stronger] > 4 and natal_bindus[weaker] < 4:
                    reasons.append(f"four_ten:{stronger}_supports_{weaker}")
            if reasons:
                relations.append({"planets": [left, right], "reasons": reasons})
    return relations


def corrected_event_worksheet(
    bav: Mapping[str, Sequence[int]],
    sign_positions: Mapping[str, Any],
    lagna_sign: Any,
    house_b: int,
    *,
    nakshatras: Mapping[str, int] | None = None,
    navamsa_signs: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Build the corrected Lesson 7 worksheet with every adjustment exposed.

    This implements only rules that can be represented consistently from the supplied
    lessons and the corrected Lesson 7 commentary. Event-specific delay and karaka
    judgments remain separate evidence rather than hidden worksheet adjustments.
    """
    rows, signs, houses, natal_bindus = _planet_context(bav, sign_positions, lagna_sign)
    labels = event_houses(house_b)
    abc = {labels[name] for name in ("A", "B", "C")}
    de = {labels[name] for name in ("D", "E")}

    row2 = {
        name: {planet: rows[planet][sign_from_house(house, lagna_sign) - 1] for planet in PLANETS}
        for name, house in labels.items()
        if name in {"A", "B", "C"}
    }
    row3 = {planet: sum(row2[name][planet] for name in ("A", "B", "C")) for planet in PLANETS}

    transfers: list[dict[str, Any]] = []
    row5 = {planet: 0 for planet in PLANETS}
    planets_by_house: dict[int, list[str]] = defaultdict(list)
    for planet, house in houses.items():
        planets_by_house[house].append(planet)
    for donor in PLANETS:
        if natal_bindus[donor] <= 4:
            continue
        recipient_house = ((houses[donor] - 1 + 9) % 12) + 1
        candidates = [
            planet
            for planet in planets_by_house.get(recipient_house, [])
            if natal_bindus[planet] < 4 and planet in FOUR_TEN_MALEFIC_RECIPIENTS
        ]
        if not candidates:
            continue
        minimum = min(natal_bindus[planet] for planet in candidates)
        recipients = [planet for planet in candidates if natal_bindus[planet] == minimum]
        for recipient in recipients:
            row5[recipient] += row3[donor]
            transfers.append(
                {
                    "donor": donor,
                    "recipient": recipient,
                    "points": row3[donor],
                    "reason": "corrected_four_ten_all_minimum_ties",
                }
            )
    row6 = {planet: row3[planet] + row5[planet] for planet in PLANETS}

    de_lords = {SIGN_LORDS[sign_from_house(house, lagna_sign)] for house in de}
    de_occupants = {
        planet for planet, house in houses.items() if house in de and natal_bindus[planet] > 4
    }
    de_bonus_planets = de_lords | de_occupants
    row8 = {planet: 5 if planet in de_bonus_planets else 0 for planet in PLANETS}
    row9 = {planet: row6[planet] + row8[planet] for planet in PLANETS}

    house_aspects: list[dict[str, Any]] = []
    row12 = {planet: 0 for planet in PLANETS}
    obstructed = set()
    for planet in PLANETS:
        targets = sorted(abc.intersection(aspected_houses(planet, houses[planet])))
        if not targets:
            continue
        obstructed.add(planet)
        own_house_targets = [
            target
            for target in targets
            if SIGN_LORDS[sign_from_house(target, lagna_sign)] == planet
        ]
        adjustment = 0 if own_house_targets else inverse_aspect_points(natal_bindus[planet])
        row12[planet] = adjustment
        house_aspects.append(
            {
                "planet": planet,
                "targets": targets,
                "natal_bindus": natal_bindus[planet],
                "adjustment": adjustment,
                "own_house_exemption": bool(own_house_targets),
            }
        )
    row13 = {planet: row9[planet] + row12[planet] for planet in PLANETS}

    planet_aspects: list[dict[str, Any]] = []
    row16 = {planet: 0 for planet in PLANETS}
    for aspector in PLANETS:
        target_houses = set(aspected_houses(aspector, houses[aspector]))
        adjustment = inverse_aspect_points(natal_bindus[aspector])
        if adjustment == 0:
            continue
        for target in PLANETS:
            if target == aspector or houses[target] not in target_houses:
                continue
            exempt = target in de_lords
            applied = 0 if exempt else adjustment
            row16[target] += applied
            planet_aspects.append(
                {
                    "aspector": aspector,
                    "target": target,
                    "natal_bindus": natal_bindus[aspector],
                    "adjustment": applied,
                    "de_lord_exemption": exempt,
                }
            )
    row17 = {planet: row13[planet] + row16[planet] for planet in PLANETS}
    ranking = sorted(PLANETS, key=lambda planet: (-row17[planet], PLANETS.index(planet)))
    samdharmi = _samdharmi_relations(houses, natal_bindus, nakshatras, navamsa_signs)
    strong = {planet for planet in PLANETS if row17[planet] > 12}
    direct_candidates = sorted(
        {planet for planet in strong if planet not in obstructed or planet in de_lords},
        key=lambda planet: ranking.index(planet),
    )
    sixth_from_b = ((labels["B"] - 1 + 5) % 12) + 1
    twelfth_from_b = ((labels["B"] - 2) % 12) + 1
    sixth_lord = SIGN_LORDS[sign_from_house(sixth_from_b, lagna_sign)]
    twelfth_lord = SIGN_LORDS[sign_from_house(twelfth_from_b, lagna_sign)]
    transfer_from_restricted_lord = {
        item["recipient"]
        for item in transfers
        if item["donor"] in {sixth_lord, twelfth_lord}
    }
    substitute_candidates = set()
    for relation in samdharmi:
        left, right = relation["planets"]
        for principal, substitute in ((left, right), (right, left)):
            substitute_score_ok = row17[substitute] >= 12
            principal_score_ok = row17[principal] >= 12
            sixth_lord_block = (
                substitute == sixth_lord and substitute not in {"SUN", "MOON"} and labels["B"] not in {1, 9}
            )
            blocked = (
                sixth_lord_block
                or substitute == twelfth_lord
                or relative_house(labels["B"], houses[substitute]) == 12
                or substitute in transfer_from_restricted_lord
            )
            if principal in obstructed and principal_score_ok and substitute_score_ok and not blocked:
                substitute_candidates.add(substitute)

    multiplied = {
        planet: round(row17[planet] * SIGN_MULTIPLIERS[planet][signs[planet] - 1], 6)
        for planet in PLANETS
    }

    return {
        "status": "corrected_kas_experimental",
        "trade_signal_enabled": False,
        "house_b": int(house_b),
        "event_houses": labels,
        "planet_signs": signs,
        "planet_houses": houses,
        "natal_bindus": natal_bindus,
        "row2_abc_bindus": row2,
        "row3_basic_strength": row3,
        "row5_four_ten_transfer": row5,
        "row6_after_transfer": row6,
        "four_ten_audit": transfers,
        "de_lords": sorted(de_lords),
        "de_qualified_occupants": sorted(de_occupants),
        "row8_de_bonus": row8,
        "row9_primary_strength": row9,
        "row12_house_aspects": row12,
        "house_aspect_audit": house_aspects,
        "row13_after_house_aspects": row13,
        "row16_planet_aspects": row16,
        "planet_aspect_audit": planet_aspects,
        "row17_final_strength": row17,
        "ranking": ranking,
        "strong_over_12": [planet for planet in ranking if planet in strong],
        "exactly_12_neutral": [planet for planet in ranking if row17[planet] == 12],
        "obstructed_by_aspecting_abc": [planet for planet in ranking if planet in obstructed],
        "direct_timing_candidates": direct_candidates,
        "samdharmi_relations": samdharmi,
        "samdharmi_substitute_candidates": sorted(
            substitute_candidates, key=lambda planet: ranking.index(planet)
        ),
        "samdharmi_restrictions": {
            "sixth_from_b_house": sixth_from_b,
            "sixth_lord": sixth_lord,
            "twelfth_from_b_house": twelfth_from_b,
            "twelfth_lord": twelfth_lord,
            "transfer_from_restricted_lord": sorted(transfer_from_restricted_lord),
        },
        "lesson26_multiplied_result_strength": multiplied,
        "lesson26_ranking": sorted(PLANETS, key=lambda planet: (-multiplied[planet], PLANETS.index(planet))),
        "lesson26_timing_use": "disabled_by_source_not_a_timing_method",
        "unresolved_components": [
            "event-specific natural/functional karaka selection",
            "event-specific delay-sector judgment",
            "source-exact improved Krushna ayanamsa ephemeris",
        ],
        "doctrine": {
            "source": "Krushna KAS Lessons 3, 5, 7, 8 and corrected Lesson 7 commentary",
            "strong_threshold": "strictly_more_than_12",
            "exact_four_aspect": "neutral",
            "four_ten_ties": "all_minimum_tied_recipients",
            "four_ten_recipient_policy": "natural_malefics_only_per_published_lesson7_fixture",
            "own_house_aspect": "exempt",
            "de_lord_planet_aspect": "exempt",
        },
    }
