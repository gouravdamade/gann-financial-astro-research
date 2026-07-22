from __future__ import annotations

from typing import Any


def _sequence(profile: dict[str, Any]) -> tuple[str, ...]:
    sequence = tuple(str(item).upper() for item in profile.get("sign_sequence", []))
    if len(sequence) != 12 or len(set(sequence)) != 12:
        raise ValueError("lordship profile requires twelve unique zodiac signs")
    return sequence


def sign_for_house(ascendant_sign: str, house: int, profile: dict[str, Any]) -> str:
    if not 1 <= int(house) <= 12:
        raise ValueError("house must be within [1, 12]")
    sequence = _sequence(profile)
    ascendant = str(ascendant_sign).upper()
    try:
        start = sequence.index(ascendant)
    except ValueError as exc:
        raise ValueError(f"unsupported ascendant sign: {ascendant_sign}") from exc
    return sequence[(start + int(house) - 1) % 12]


def houses_owned_by(
    planet: str, ascendant_sign: str, profile: dict[str, Any]
) -> tuple[int, ...]:
    rulers = {
        str(sign).upper(): str(ruler).upper()
        for sign, ruler in profile.get("sign_rulers", {}).items()
    }
    body = str(planet).upper()
    owned = [
        house
        for house in range(1, 13)
        if rulers.get(sign_for_house(ascendant_sign, house, profile)) == body
    ]
    return tuple(owned)


def group_flags(
    owned_houses: tuple[int, ...], profile: dict[str, Any]
) -> tuple[str, ...]:
    groups = {
        str(name).upper(): {int(item) for item in houses}
        for name, houses in profile.get("house_groups", {}).items()
    }
    owned = set(owned_houses)
    flags = [f"{name}_LORD" for name, houses in groups.items() if owned & houses]
    maraka = groups.get("MARAKA", set())
    if owned & maraka:
        flags.append("MARAKA_CANDIDATE")
    return tuple(sorted(set(flags)))
