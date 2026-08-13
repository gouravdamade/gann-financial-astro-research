"""Read-only BPHS 1899 calendar timing range compiler.

This service deliberately separates a held historical source profile from the
engineering astronomy used to calculate calendar boundaries.  It has no price,
polarity, SBC, score, catalogue, ML, or execution dependency.
"""

from __future__ import annotations

from functools import cache
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from threading import RLock
from typing import Any, Callable, Mapping
from zoneinfo import ZoneInfo

import swisseph as swe

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from financial_astro_ephemeris import configure_ephemeris

from panchanga_doctrine import karana_context, nakshatra_pada, tithi_context, yoga_context


BPHS_CLASSICAL_CALENDAR_CONTRACT = "BPHS_CLASSICAL_CALENDAR_RANGE_V1"
BPHS_CLASSICAL_CALENDAR_PROFILE_ID = "BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1"
BPHS_SOURCE_ID = "BPHS_1899_GOVIND_SHARMA_SHASTRI"
BPHS_SOURCE_SHA256 = "BB556804D8D546ACC39C43A22CECDBE2C29E3A7BA157E60EEC810C478EB645A4"
ENGINEERING_CALCULATION_PROFILE_ID = "SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1"
CHAPTER_14_CATEGORY_CONTEXT_LOCATOR = (
    "BPHS_1899_GOVIND_SHARMA_SHASTRI Chapter 14 / Packet 1W (chapter-level calendar-category context only; "
    "no individual category name or boundary table was page-transcribed for this engineering implementation)."
)
TARA_FULL_CHAPTER_AUDIT_LOCATOR = (
    "BPHS_1899_GOVIND_SHARMA_SHASTRI Chapter 14 full held-witness audit, printed pp. 196-258 / PDF images 679-741; "
    "Chapter 15 starts at printed p. 259 / PDF image 742."
)
REQUEST_KEYS = {
    "rangeStartUtc",
    "rangeEndUtc",
    "timezone",
    "latitude",
    "longitude",
    "profileId",
    "taraReference",
}
CATEGORY_ORDER = ("muhurta", "tithi", "nakshatra", "yoga", "karana", "weekday", "tara")
_SAMPLE_STEP = timedelta(hours=6)
_REFINEMENT_RESOLUTION = timedelta(seconds=1)
MAX_INTERACTIVE_RESEARCH_WINDOW = timedelta(days=14)
_MUHURTA_FIXTURE_RELATIVE = Path("research_labs") / "bphs_1899_classical_timing" / "bphs_1899_packet_1w_muhurta_fixture.json"
_EPHEMERIS_LOCK = RLock()


def _julian_ut(value: datetime) -> float:
    utc = value.astimezone(timezone.utc)
    hour = utc.hour + (utc.minute / 60.0) + (utc.second / 3600.0) + (utc.microsecond / 3_600_000_000.0)
    return float(swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL))


def _datetime_from_jd_ut(julian_day: float) -> datetime:
    year, month, day, hour = swe.revjul(julian_day, swe.GREG_CAL)
    whole_seconds = round(float(hour) * 3600.0)
    return datetime(int(year), int(month), int(day), tzinfo=timezone.utc) + timedelta(seconds=whole_seconds)


@cache
def _muhurta_fixture_path(resource_root: Path | None = None) -> Path:
    """Resolve source data in both source-tree and collected-sidecar runtimes."""
    root = resource_root or Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
    return root / _MUHURTA_FIXTURE_RELATIVE


def _muhurta_fixture() -> dict[str, Any]:
    """Load the small, source-closed Packet 1W table without broad doctrine lookup."""
    fixture = json.loads(_muhurta_fixture_path().read_text(encoding="utf-8"))
    source = fixture.get("source", {})
    if source.get("sourceId") != BPHS_SOURCE_ID or source.get("fileSha256") != BPHS_SOURCE_SHA256:
        raise RuntimeError("BPHS Packet 1W Muhurta fixture does not match the held witness")
    for key in ("daytime", "nighttime"):
        rows = fixture.get(key)
        if not isinstance(rows, list) or [row.get("index") for row in rows] != list(range(1, 16)):
            raise RuntimeError(f"BPHS Packet 1W Muhurta fixture has an invalid {key} order")
    if fixture.get("transcription", {}).get("diffStatus") != "AGREED":
        raise RuntimeError("BPHS Packet 1W Muhurta transcription passes disagree")
    return fixture


def _muhurta_name(period: str, index: int) -> str:
    rows = _muhurta_fixture()["daytime" if period == "DAY" else "nighttime"]
    return str(rows[index - 1]["name"])


def _muhurta_source_locator() -> str:
    return str(_muhurta_fixture()["source"]["tableLocator"])


def _parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_profile() -> dict[str, Any]:
    fixture = _muhurta_fixture()
    return {
        "profileId": BPHS_CLASSICAL_CALENDAR_PROFILE_ID,
        "sourceId": BPHS_SOURCE_ID,
        "edition": "1899 Purva/Uttara witness",
        "fileSha256": BPHS_SOURCE_SHA256,
        "scope": "Chapter 14 / Packet 1W; Muhurta table printed p. 197 (PDF image 680)",
        "evidenceStatus": "PARTIAL_SOURCE_PROFILE",
        "classicalCompletenessClaim": False,
        "sourceGaps": [
            "BPHS_1899_PACKET_1W_OTHER_CALENDAR_CATEGORY_TABLES_NOT_TRANSCRIBED",
            "BPHS_1899_WEEKDAY_BOUNDARY_NOT_CLOSED",
            "BPHS_1899_TARA_NINEFOLD_SEQUENCE_NOT_LOCATED_IN_HELD_CHAPTER_14_FULL_RANGE",
            "BPHS_1899_TARA_MAPPING_OPERATOR_NOT_CLOSED",
            "BPHS_1899_TARA_REFERENCE_IDENTITY_NOT_CONFIGURED",
        ],
        "sourceFixtures": [{
            "fixtureId": fixture["fixtureId"],
            "transcriptionStatus": fixture["transcription"]["status"],
            "locator": fixture["source"]["tableLocator"],
        }],
        "interpretation": "The Packet 1W Muhurta name/order table is source-transcribed. Sunrise/sunset segmentation and all other calculated categories remain engineering-labelled. No market meaning, suitability, polarity, or score is supplied.",
    }


def _category(
    value: str,
    *,
    availability: str,
    detail: str,
    source_locator: str,
    calculation: str,
    dependency: str | None = None,
) -> dict[str, Any]:
    return {
        "value": value,
        "availability": availability,
        "detail": detail,
        "sourceLocator": source_locator,
        "calculationProfile": calculation,
        "dependency": dependency,
    }


class _CalendarCalculator:
    def __init__(self, *, timezone_name: str, latitude: float, longitude: float) -> None:
        self.zone = ZoneInfo(timezone_name)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self._solar_cache: dict[object, tuple[datetime, datetime]] = {}

    def configure_session(self) -> None:
        """Configure one locked Swiss Ephemeris session for a complete range."""
        configure_ephemeris(None)
        swe.set_sid_mode(swe.SIDM_RAMAN)

    def _sun_moon(self, at_utc: datetime) -> tuple[float, float]:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        sun, _ = swe.calc_ut(_julian_ut(at_utc), swe.SUN, flags)
        moon, _ = swe.calc_ut(_julian_ut(at_utc), swe.MOON, flags)
        return float(sun[0]) % 360.0, float(moon[0]) % 360.0

    def _sunrise_sunset(self, local_date: object) -> tuple[datetime, datetime]:
        cached = self._solar_cache.get(local_date)
        if cached is not None:
            return cached
        local_midnight = datetime.combine(local_date, datetime.min.time(), tzinfo=self.zone)
        coordinates = (self.longitude, self.latitude, 0.0)
        rise_result, rise_times = swe.rise_trans(
            _julian_ut(local_midnight.astimezone(timezone.utc)), swe.SUN, swe.CALC_RISE,
            coordinates, 0.0, 0.0, swe.FLG_SWIEPH,
        )
        set_result, set_times = swe.rise_trans(
            _julian_ut(local_midnight.astimezone(timezone.utc)), swe.SUN, swe.CALC_SET,
            coordinates, 0.0, 0.0, swe.FLG_SWIEPH,
        )
        if int(rise_result) != 0 or int(set_result) != 0:
            raise RuntimeError(f"sunrise/sunset unavailable for {local_date}")
        sunrise = _datetime_from_jd_ut(float(rise_times[0]))
        sunset = _datetime_from_jd_ut(float(set_times[0]))
        if sunset <= sunrise:
            raise RuntimeError(f"sunset must follow sunrise for {local_date}")
        self._solar_cache[local_date] = (sunrise, sunset)
        return sunrise, sunset

    def _muhurta(self, at_utc: datetime) -> dict[str, Any]:
        local = at_utc.astimezone(self.zone)
        today = local.date()
        sunrise, sunset = self._sunrise_sunset(today)
        if sunrise <= at_utc < sunset:
            start, end, period = sunrise, sunset, "DAY"
        elif at_utc < sunrise:
            previous_sunset = self._sunrise_sunset(today - timedelta(days=1))[1]
            start, end, period = previous_sunset, sunrise, "NIGHT"
        else:
            next_sunrise = self._sunrise_sunset(today + timedelta(days=1))[0]
            start, end, period = sunset, next_sunrise, "NIGHT"
        fraction = max(0.0, min(0.999999, (at_utc - start).total_seconds() / (end - start).total_seconds()))
        index = min(15, int(fraction * 15) + 1)
        source_name = _muhurta_name(period, index)
        return _category(
            f"{period} MUHURTA {index:02d} - {source_name}",
            availability="SOURCE_TRANSCRIBED_ENGINEERING_BOUNDARY",
            detail=(
                f"{period.title()} Muhurta {index} of 15 is named {source_name} in the held Packet 1W table. "
                "Its live start/end are sunrise/sunset-derived engineering boundaries, not a claimed BPHS calculation formula."
            ),
            source_locator=_muhurta_source_locator(),
            calculation=ENGINEERING_CALCULATION_PROFILE_ID,
            dependency="ENGINEERING_SUNRISE_SUNSET_BOUNDARY_NOT_CLASSICAL_FORMULA",
        )

    def state_at(self, at_utc: datetime, tara_reference: Mapping[str, Any] | None) -> dict[str, dict[str, Any]]:
        sun, moon = self._sun_moon(at_utc)
        tithi = tithi_context(sun, moon)
        karana = karana_context(tithi["phase_angle_deg"])
        yoga = yoga_context(sun, moon)
        nakshatra = nakshatra_pada(moon)
        local = at_utc.astimezone(self.zone)
        tara_detail = (
            "The full held Chapter 14 audit did not locate a complete ninefold Tara sequence or a timestamp-evaluable mapping/operator, "
            "and no explicit Tara reference identity contract is configured."
        )
        if tara_reference:
            tara_detail = (
                "A Tara reference was supplied, but the full held Chapter 14 audit does not close the ninefold Tara mapping/operator; "
                "the supplied reference is therefore not evaluated."
            )
        return {
            "muhurta": self._muhurta(at_utc),
            "tithi": _category(
                f"{tithi['paksha']} {tithi['tithi_index']:02d} {tithi['tithi_name']}",
                availability="ENGINEERING_CALCULATED",
                detail=(
                    f"Engineering calculation: sidereal Sun-Moon phase {tithi['phase_angle_deg']:.4f} degrees. "
                    "The source is cited only for chapter-level calendar-category context; this displayed name and boundary were not individually page-transcribed."
                ),
                source_locator=CHAPTER_14_CATEGORY_CONTEXT_LOCATOR,
                calculation=ENGINEERING_CALCULATION_PROFILE_ID,
            ),
            "nakshatra": _category(
                f"{nakshatra['index']:02d} {nakshatra['name']} pada {nakshatra['pada']}",
                availability="ENGINEERING_CALCULATED",
                detail=(
                    "Engineering calculation: Moon sidereal nakshatra and pada. "
                    "The source is cited only for chapter-level calendar-category context; this displayed name and boundary were not individually page-transcribed."
                ),
                source_locator=CHAPTER_14_CATEGORY_CONTEXT_LOCATOR,
                calculation=ENGINEERING_CALCULATION_PROFILE_ID,
            ),
            "yoga": _category(
                f"{yoga['yoga_index']:02d} {yoga['yoga_name']}",
                availability="ENGINEERING_CALCULATED",
                detail=(
                    f"Engineering calculation: sidereal Sun+Moon yoga angle {yoga['yoga_angle_deg']:.4f} degrees. "
                    "The source is cited only for chapter-level calendar-category context; this displayed name and boundary were not individually page-transcribed."
                ),
                source_locator=CHAPTER_14_CATEGORY_CONTEXT_LOCATOR,
                calculation=ENGINEERING_CALCULATION_PROFILE_ID,
            ),
            "karana": _category(
                f"{karana['karana_index']:02d} {karana['karana_name']}",
                availability="ENGINEERING_CALCULATED",
                detail=(
                    "Engineering calculation: half-tithi calendar category. "
                    "The source is cited only for chapter-level calendar-category context; this displayed name and boundary were not individually page-transcribed."
                ),
                source_locator=CHAPTER_14_CATEGORY_CONTEXT_LOCATOR,
                calculation=ENGINEERING_CALCULATION_PROFILE_ID,
            ),
            "weekday": _category(
                f"Civil weekday: {local.strftime('%A')}",
                availability="PARTIAL_SOURCE",
                detail=(
                    f"Local civil-midnight weekday in {self.zone.key}. The audited Packet 1W witness does not close "
                    "a classical weekday/vāra ownership boundary, so this is engineering display data rather than literal BPHS doctrine."
                ),
                source_locator="No weekday/vāra boundary statement located in the audited BPHS_1899 Packet 1W evidence.",
                calculation="LOCAL_CIVIL_MIDNIGHT_WEEKDAY_V1",
                dependency="BPHS_1899_WEEKDAY_BOUNDARY_NOT_CLOSED",
            ),
            "tara": _category(
                "DEPENDENCY_NOT_READY",
                availability="DEPENDENCY_NOT_READY",
                detail=tara_detail,
                source_locator=TARA_FULL_CHAPTER_AUDIT_LOCATOR,
                calculation="NOT_EVALUATED",
                dependency=(
                    "BPHS_1899_TARA_NINEFOLD_SEQUENCE_NOT_LOCATED_IN_HELD_CHAPTER_14_FULL_RANGE; "
                    "BPHS_1899_TARA_MAPPING_OPERATOR_NOT_CLOSED; "
                    "BPHS_1899_TARA_REFERENCE_IDENTITY_NOT_CONFIGURED"
                ),
            ),
        }

    def _muhurta_boundaries(self, start: datetime, end: datetime) -> set[datetime]:
        boundaries: set[datetime] = set()
        cursor = start.astimezone(self.zone).date() - timedelta(days=1)
        final = end.astimezone(self.zone).date() + timedelta(days=1)
        while cursor <= final:
            sunrise, sunset = self._sunrise_sunset(cursor)
            next_sunrise = self._sunrise_sunset(cursor + timedelta(days=1))[0]
            for period_start, period_end in ((sunrise, sunset), (sunset, next_sunrise)):
                width = (period_end - period_start) / 15
                for index in range(16):
                    candidate = period_start + (width * index)
                    if start < candidate < end:
                        boundaries.add(candidate)
            cursor += timedelta(days=1)
        return boundaries


def _signature(state: Mapping[str, dict[str, Any]], category: str) -> tuple[str, str]:
    item = state[category]
    return str(item["value"]), str(item["availability"])


def _refine_change(
    calculator: _CalendarCalculator,
    category: str,
    left: datetime,
    right: datetime,
    left_signature: tuple[str, str],
    tara_reference: Mapping[str, Any] | None,
) -> datetime:
    while right - left > _REFINEMENT_RESOLUTION:
        midpoint = left + ((right - left) / 2)
        current = _signature(calculator.state_at(midpoint, tara_reference), category)
        if current == left_signature:
            left = midpoint
        else:
            right = midpoint
    return right.replace(microsecond=0)


def _calendar_boundaries(
    calculator: _CalendarCalculator,
    start: datetime,
    end: datetime,
    tara_reference: Mapping[str, Any] | None,
) -> list[datetime]:
    boundaries: set[datetime] = {start, end}
    cursor = start
    previous = calculator.state_at(cursor, tara_reference)
    while cursor < end:
        next_cursor = min(cursor + _SAMPLE_STEP, end)
        current = calculator.state_at(next_cursor, tara_reference)
        for category in ("tithi", "nakshatra", "yoga", "karana"):
            if _signature(previous, category) != _signature(current, category):
                boundaries.add(_refine_change(calculator, category, cursor, next_cursor, _signature(previous, category), tara_reference))
        cursor, previous = next_cursor, current

    local_cursor = start.astimezone(calculator.zone).date()
    local_end = end.astimezone(calculator.zone).date() + timedelta(days=1)
    while local_cursor <= local_end:
        midnight = datetime.combine(local_cursor, datetime.min.time(), tzinfo=calculator.zone).astimezone(timezone.utc)
        if start < midnight < end:
            boundaries.add(midnight)
        local_cursor += timedelta(days=1)
    boundaries.update(calculator._muhurta_boundaries(start, end))
    return sorted(boundaries)


def _merge_adjacent(intervals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for interval in intervals:
        if merged and merged[-1]["categories"] == interval["categories"] and merged[-1]["endUtc"] == interval["startUtc"]:
            merged[-1]["endUtc"] = interval["endUtc"]
            continue
        merged.append(interval)
    for index, interval in enumerate(merged, start=1):
        interval["intervalId"] = f"BPHS_CAL_{index:05d}"
    return merged


def build_bphs_classical_calendar_range(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ValueError("BPHS classical calendar request must be an object")
    unknown = sorted(set(payload) - REQUEST_KEYS)
    if unknown:
        raise ValueError("Unknown BPHS classical calendar request field(s): " + ", ".join(unknown))
    if str(payload.get("profileId") or "") != BPHS_CLASSICAL_CALENDAR_PROFILE_ID:
        raise ValueError(f"profileId must be {BPHS_CLASSICAL_CALENDAR_PROFILE_ID}")
    start = _parse_utc(payload.get("rangeStartUtc"), "rangeStartUtc")
    end = _parse_utc(payload.get("rangeEndUtc"), "rangeEndUtc")
    if end <= start:
        raise ValueError("rangeEndUtc must be later than rangeStartUtc")
    if end - start > MAX_INTERACTIVE_RESEARCH_WINDOW:
        raise ValueError(
            "BPHS_INTERACTIVE_RESEARCH_WINDOW_EXCEEDS_14_DAYS: "
            "use the shared Fields research-window paging controls"
        )
    timezone_name = str(payload.get("timezone") or "").strip()
    try:
        ZoneInfo(timezone_name)
    except Exception as exc:
        raise ValueError("timezone must be a valid IANA timezone") from exc
    try:
        latitude = float(payload.get("latitude"))
        longitude = float(payload.get("longitude"))
    except (TypeError, ValueError) as exc:
        raise ValueError("latitude and longitude must be numeric") from exc
    tara_reference = payload.get("taraReference")
    if tara_reference is not None and not isinstance(tara_reference, Mapping):
        raise ValueError("taraReference must be an object when supplied")

    calculator = _CalendarCalculator(timezone_name=timezone_name, latitude=latitude, longitude=longitude)
    # Swiss Ephemeris sidereal configuration is process-global.  One locked
    # session avoids interleaving settings and keeps a broad visible range fast.
    with _EPHEMERIS_LOCK:
        calculator.configure_session()
        boundaries = _calendar_boundaries(calculator, start, end, tara_reference)
        intervals = _merge_adjacent([
            {
                "intervalId": "",
                "startUtc": _iso(left),
                "endUtc": _iso(right),
                "categories": calculator.state_at(left, tara_reference),
            }
            for left, right in zip(boundaries, boundaries[1:])
            if right > left
        ])
    return {
        "contract": BPHS_CLASSICAL_CALENDAR_CONTRACT,
        "schemaVersion": 1,
        "rangeStartUtc": _iso(start),
        "rangeEndUtc": _iso(end),
        "timezone": timezone_name,
        "location": {"latitude": latitude, "longitude": longitude},
        "categoryOrder": list(CATEGORY_ORDER),
        "sourceProfile": _source_profile(),
        "engineeringCalculationProfile": ENGINEERING_CALCULATION_PROFILE_ID,
        "intervals": intervals,
        "guardrails": {
            "readOnly": True,
            "marketDataRead": False,
            "priceOutcomeRead": False,
            "polarityCatalogueRead": False,
            "pairRelativeFieldPath": False,
            "founderReviewDecisionPath": False,
            "sbcPath": False,
            "autoSuggestPath": False,
            "mlPath": False,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
            "scoreAggregationUsed": False,
            "marketDirectionInferred": False,
        },
    }


__all__ = [
    "BPHS_CLASSICAL_CALENDAR_CONTRACT",
    "BPHS_CLASSICAL_CALENDAR_PROFILE_ID",
    "build_bphs_classical_calendar_range",
]
