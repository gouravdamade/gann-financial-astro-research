from __future__ import annotations

PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
CONTRIBUTORS = PLANETS + ("LAGNA",)
SIGN_NAMES = (
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
)

EXPECTED_BAV_TOTALS = {
    "SUN": 48,
    "MOON": 49,
    "MARS": 39,
    "MERCURY": 54,
    "JUPITER": 56,
    "VENUS": 52,
    "SATURN": 39,
}
EXPECTED_SAV_TOTAL = 337

# Unreduced benefic places counted inclusively from each contributor's sign.
# This is the B. V. Raman-style table used by the published certification fixture.
BAV_BENEFIC_HOUSES: dict[str, dict[str, tuple[int, ...]]] = {
    "SUN": {
        "SUN": (1, 2, 4, 7, 8, 9, 10, 11),
        "MOON": (3, 6, 10, 11),
        "MARS": (1, 2, 4, 7, 8, 9, 10, 11),
        "MERCURY": (3, 5, 6, 9, 10, 11, 12),
        "JUPITER": (5, 6, 9, 11),
        "VENUS": (6, 7, 12),
        "SATURN": (1, 2, 4, 7, 8, 9, 10, 11),
        "LAGNA": (3, 4, 6, 10, 11, 12),
    },
    "MOON": {
        "SUN": (3, 6, 7, 8, 10, 11),
        "MOON": (1, 3, 6, 7, 10, 11),
        "MARS": (2, 3, 5, 6, 9, 10, 11),
        "MERCURY": (1, 3, 4, 5, 7, 8, 10, 11),
        "JUPITER": (1, 4, 7, 8, 10, 11, 12),
        "VENUS": (3, 4, 5, 7, 9, 10, 11),
        "SATURN": (3, 5, 6, 11),
        "LAGNA": (3, 6, 10, 11),
    },
    "MARS": {
        "SUN": (3, 5, 6, 10, 11),
        "MOON": (3, 6, 11),
        "MARS": (1, 2, 4, 7, 8, 10, 11),
        "MERCURY": (3, 5, 6, 11),
        "JUPITER": (6, 10, 11, 12),
        "VENUS": (6, 8, 11, 12),
        "SATURN": (1, 4, 7, 8, 9, 10, 11),
        "LAGNA": (1, 3, 6, 10, 11),
    },
    "MERCURY": {
        "SUN": (5, 6, 9, 11, 12),
        "MOON": (2, 4, 6, 8, 10, 11),
        "MARS": (1, 2, 4, 7, 8, 9, 10, 11),
        "MERCURY": (1, 3, 5, 6, 9, 10, 11, 12),
        "JUPITER": (6, 8, 11, 12),
        "VENUS": (1, 2, 3, 4, 5, 8, 9, 11),
        "SATURN": (1, 2, 4, 7, 8, 9, 10, 11),
        "LAGNA": (1, 2, 4, 6, 8, 10, 11),
    },
    "JUPITER": {
        "SUN": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "MOON": (2, 5, 7, 9, 11),
        "MARS": (1, 2, 4, 7, 8, 10, 11),
        "MERCURY": (1, 2, 4, 5, 6, 9, 10, 11),
        "JUPITER": (1, 2, 3, 4, 7, 8, 10, 11),
        "VENUS": (2, 5, 6, 9, 10, 11),
        "SATURN": (3, 5, 6, 12),
        "LAGNA": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "VENUS": {
        "SUN": (8, 11, 12),
        "MOON": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "MARS": (3, 5, 6, 9, 11, 12),
        "MERCURY": (3, 5, 6, 9, 11),
        "JUPITER": (5, 8, 9, 10, 11),
        "VENUS": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "SATURN": (3, 4, 5, 8, 9, 10, 11),
        "LAGNA": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "SATURN": {
        "SUN": (1, 2, 4, 7, 8, 10, 11),
        "MOON": (3, 6, 11),
        "MARS": (3, 5, 6, 10, 11, 12),
        "MERCURY": (6, 8, 9, 10, 11, 12),
        "JUPITER": (5, 6, 11, 12),
        "VENUS": (6, 11, 12),
        "SATURN": (3, 5, 6, 11),
        "LAGNA": (1, 3, 4, 6, 10, 11),
    },
}
