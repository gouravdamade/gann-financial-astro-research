from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


DASHA_SEQUENCE = ("KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU", "JUPITER", "SATURN", "MERCURY")
DASHA_YEARS = {
    "KETU": 7,
    "VENUS": 20,
    "SUN": 6,
    "MOON": 10,
    "MARS": 7,
    "RAHU": 18,
    "JUPITER": 16,
    "SATURN": 19,
    "MERCURY": 17,
}
NAKSHATRA_SPAN = 360.0 / 27.0
YEAR_DAYS = 365.2425


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def nakshatra_index(longitude: float) -> int:
    return int((float(longitude) % 360.0) // NAKSHATRA_SPAN)


def nakshatra_lord(longitude: float) -> str:
    return DASHA_SEQUENCE[nakshatra_index(longitude) % 9]


def _add_year_fraction(value: datetime, years: float) -> datetime:
    return value + timedelta(days=float(years) * YEAR_DAYS)


def mahadasha_periods(birth: datetime, moon_longitude: float, cycles: int = 2) -> list[dict[str, Any]]:
    born = _utc(birth)
    index = nakshatra_index(moon_longitude)
    lord_index = index % 9
    fraction_elapsed = ((float(moon_longitude) % NAKSHATRA_SPAN) / NAKSHATRA_SPAN)
    first_lord = DASHA_SEQUENCE[lord_index]
    start = _add_year_fraction(born, -fraction_elapsed * DASHA_YEARS[first_lord])
    periods = []
    cursor = start
    for offset in range(9 * int(cycles)):
        lord = DASHA_SEQUENCE[(lord_index + offset) % 9]
        end = _add_year_fraction(cursor, DASHA_YEARS[lord])
        periods.append({"lord": lord, "start": cursor, "end": end})
        cursor = end
    return periods


def antardasha_periods(mahadasha: dict[str, Any]) -> list[dict[str, Any]]:
    md_lord = str(mahadasha["lord"]).upper()
    start = _utc(mahadasha["start"])
    end = _utc(mahadasha["end"])
    total_seconds = (end - start).total_seconds()
    first_index = DASHA_SEQUENCE.index(md_lord)
    periods = []
    cursor = start
    for offset in range(9):
        lord = DASHA_SEQUENCE[(first_index + offset) % 9]
        duration = total_seconds * DASHA_YEARS[lord] / 120.0
        item_end = end if offset == 8 else cursor + timedelta(seconds=duration)
        sector_seconds = (item_end - cursor).total_seconds() / 3.0
        sectors = []
        for sector in range(3):
            sector_start = cursor + timedelta(seconds=sector * sector_seconds)
            sector_end = item_end if sector == 2 else cursor + timedelta(seconds=(sector + 1) * sector_seconds)
            sectors.append(
                {
                    "sector": sector + 1,
                    "label": ("no_delay", "moderate_delay", "full_delay")[sector],
                    "start": sector_start,
                    "end": sector_end,
                }
            )
        periods.append(
            {
                "mahadasha_lord": md_lord,
                "lord": lord,
                "start": cursor,
                "end": item_end,
                "sectors": sectors,
            }
        )
        cursor = item_end
    return periods


def dasha_at(birth: datetime, moon_longitude: float, when: datetime) -> dict[str, Any]:
    moment = _utc(when)
    for md in mahadasha_periods(birth, moon_longitude, cycles=3):
        if md["start"] <= moment < md["end"]:
            for ad in antardasha_periods(md):
                if ad["start"] <= moment < ad["end"]:
                    sector = next(item for item in ad["sectors"] if item["start"] <= moment < item["end"])
                    return {"mahadasha": md, "antardasha": ad, "sector": sector}
    raise ValueError(f"Date {moment.isoformat()} falls outside generated Vimshottari cycles")

