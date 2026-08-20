"""Classical Geography & Visibility Observatory (CGVO) read-only service.

The modern astronomy layer in this module is factual Swiss Ephemeris output.
The Varahamihira and Trailokya layers are source-ledger records with explicit
unknowns.  No layer produces a market direction, score, or execution input.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping
from zoneinfo import ZoneInfo

import swisseph as swe

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from financial_astro_ephemeris import configure_ephemeris


CGVO_CONTRACT = "CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1"
CGVO_EVENT_CONTRACT = "CGVO_CAUSAL_ECLIPSE_EVENT_V1"
MODERN_ASTRONOMY_CONTRACT = "MODERN_ASTRONOMY_VISIBILITY_V1"
VARAHAMIHIRA_PROFILE_ID = "VARAHAMIHIRA_BS_ECLIPSE_V1"
TRAILOKYA_PROFILE_ID = "TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1"
CGVO_ROOT = Path("configs") / "research" / "cgvo"
KURMA_FIXTURE = CGVO_ROOT / "kurma_gazetteer_seed_v1.json"
VARAHAMIHIRA_FIXTURE = CGVO_ROOT / "varahamihira_eclipse_source_profile_v1.json"
TRAILOKYA_FIXTURE = CGVO_ROOT / "trailokya_geography_argha_context_v1.json"
SOURCE_UNKNOWN_REASONS = [
    "VARAHAMIHIRA_RASI_MAPPING_UNRESOLVED",
    "VARAHAMIHIRA_NAKSHATRA_FRAME_UNRESOLVED",
    "VARAHAMIHIRA_LUNAR_MONTH_UNRESOLVED",
    "VARAHAMIHIRA_FIRMAMENT_INTERPRETATION_UNRESOLVED",
    "VARAHAMIHIRA_MORPHOLOGY_MAPPING_UNRESOLVED",
    "VARAHAMIHIRA_COLOUR_OBSERVATION_REQUIRED",
    "TRAILOKYA_ECLIPSE_VISIBILITY_SOURCE_SILENT",
]
MAX_SEARCH_DAYS = 3700
SEARCH_LIMIT = 24
_JD_UNIX_EPOCH = 2440587.5


class CgvoRequestError(ValueError):
    """An invalid read-only CGVO request."""


def _parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CgvoRequestError(f"{field} must be an ISO-8601 UTC timestamp")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CgvoRequestError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None:
        raise CgvoRequestError(f"{field} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _jd(value: datetime) -> float:
    utc = value.astimezone(timezone.utc)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600 + utc.microsecond / 3_600_000_000
    return float(swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL))


def _from_jd(value: float | int | None) -> datetime | None:
    if value is None or float(value) == 0:
        return None
    year, month, day, hour = swe.revjul(float(value), swe.GREG_CAL)
    seconds = round(float(hour) * 3600)
    return datetime(int(year), int(month), int(day), tzinfo=timezone.utc) + timedelta(seconds=seconds)


def _iso(value: datetime | None) -> str | None:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if value else None


def _finite(value: Any, digits: int = 8) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return round(parsed, digits) if math.isfinite(parsed) else None


def _hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _load_json(project_root: Path, relative_path: Path) -> dict[str, Any]:
    path = project_root / relative_path
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"CGVO source fixture is missing: {relative_path.as_posix()}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"CGVO source fixture is invalid JSON: {relative_path.as_posix()}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"CGVO source fixture must be a JSON object: {relative_path.as_posix()}")
    return payload


def _guardrails() -> dict[str, bool]:
    return {
        "readOnly": True,
        "experimental": True,
        "priceDataRead": False,
        "priceOutcomeRead": False,
        "fieldsPath": False,
        "sbcPath": False,
        "autoSuggestPath": False,
        "mlPath": False,
        "mt5Path": False,
        "executionAllowed": False,
        "automaticOrderPlacement": False,
        "marketDirectionInferred": False,
        "scoreAggregationUsed": False,
        "crossSourceComposition": False,
    }


def _validate_locality(payload: Mapping[str, Any]) -> dict[str, Any]:
    try:
        latitude = float(payload.get("latitude"))
        longitude = float(payload.get("longitude"))
    except (TypeError, ValueError) as exc:
        raise CgvoRequestError("latitude and longitude are required numeric values") from exc
    if not -90 <= latitude <= 90:
        raise CgvoRequestError("latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise CgvoRequestError("longitude must be between -180 and 180")
    try:
        elevation = float(payload.get("elevationM", 0.0))
    except (TypeError, ValueError) as exc:
        raise CgvoRequestError("elevationM must be numeric") from exc
    if not math.isfinite(elevation):
        raise CgvoRequestError("elevationM must be finite")
    timezone_name = str(payload.get("timezone") or "UTC")
    try:
        ZoneInfo(timezone_name)
    except Exception as exc:
        raise CgvoRequestError(f"unknown IANA timezone: {timezone_name}") from exc
    locality_id = str(payload.get("localityId") or "AD_HOC_LOCALITY").strip()
    return {
        "localityId": locality_id,
        "label": str(payload.get("label") or locality_id),
        "latitude": round(latitude, 8),
        "longitude": round(longitude, 8),
        "elevationM": round(elevation, 3),
        "timezone": timezone_name,
        "elevationProvenance": "EXPLICIT_REQUEST_VALUE" if "elevationM" in payload else "ENGINEERING_DEFAULT_ZERO_METRES",
    }


def _global_type(flags: int, event_type: str) -> str:
    if event_type == "SOLAR":
        if flags & swe.ECL_ANNULAR_TOTAL:
            return "HYBRID"
        if flags & swe.ECL_TOTAL:
            return "TOTAL"
        if flags & swe.ECL_ANNULAR:
            return "ANNULAR"
        if flags & swe.ECL_PARTIAL:
            return "PARTIAL"
        return "UNKNOWN_GLOBAL_TYPE"
    if flags & swe.ECL_TOTAL:
        return "TOTAL"
    if flags & swe.ECL_PARTIAL:
        return "PARTIAL"
    if flags & swe.ECL_PENUMBRAL:
        return "PENUMBRAL"
    return "UNKNOWN_GLOBAL_TYPE"


def _local_type(flags: int, event_type: str, local_max: datetime | None) -> str:
    if local_max is None:
        return "NOT_GEOMETRICALLY_VISIBLE"
    if event_type == "LUNAR" and flags & swe.ECL_PENUMBRAL:
        return "PENUMBRAL"
    if flags & swe.ECL_TOTAL:
        return "TOTAL"
    if flags & swe.ECL_ANNULAR:
        return "ANNULAR"
    if flags & swe.ECL_PARTIAL:
        return "PARTIAL"
    return "LOCAL_CIRCUMSTANCE_AVAILABLE"


def _solar_global_contacts(times: tuple[float, ...]) -> dict[str, str | None]:
    return {name: _iso(_from_jd(times[index])) for name, index in (("C1", 2), ("C2", 4), ("MAX", 0), ("C3", 5), ("C4", 3))}


def _solar_local_contacts(times: tuple[float, ...]) -> dict[str, str | None]:
    return {name: _iso(_from_jd(times[index])) for name, index in (("C1", 1), ("C2", 2), ("MAX", 0), ("C3", 3), ("C4", 4))}


def _lunar_contacts(times: tuple[float, ...]) -> dict[str, str | None]:
    return {name: _iso(_from_jd(times[index])) for name, index in (("P1", 6), ("U1", 2), ("U2", 4), ("MAX", 0), ("U3", 5), ("U4", 3), ("P4", 7))}


def _observer_position(project_root: Path, event_type: str, event_max: datetime, locality: Mapping[str, Any]) -> dict[str, Any]:
    del project_root
    coordinates = (float(locality["longitude"]), float(locality["latitude"]), float(locality["elevationM"]))
    flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    result: dict[str, Any] = {}
    for body, body_id in (("SUN", swe.SUN), ("MOON", swe.MOON)):
        values, _ = swe.calc_ut(_jd(event_max), body_id, flags)
        azimuth, true_altitude, apparent_altitude = swe.azalt(_jd(event_max), swe.EQU2HOR, coordinates, 0.0, 15.0, values)
        result[body.lower()] = {
            "altitudeTrueDeg": _finite(true_altitude),
            "altitudeApparentDeg": _finite(apparent_altitude),
            "azimuthDeg": _finite(azimuth),
        }
    result["calculation"] = "TOPOCENTRIC_HORIZONTAL_COORDINATES_AT_LOCAL_MAX"
    result["eventType"] = event_type
    return result


def _local_circumstances(project_root: Path, event_type: str, global_max: datetime, locality: Mapping[str, Any]) -> dict[str, Any]:
    configure_ephemeris(None)
    coordinates = (float(locality["longitude"]), float(locality["latitude"]), float(locality["elevationM"]))
    flags = swe.FLG_SWIEPH
    event_max_jd = _jd(global_max)
    if event_type == "SOLAR":
        next_flags, times, attrs = swe.sol_eclipse_when_loc(event_max_jd - 1.0, coordinates, flags)
        contact_map = _solar_local_contacts(times)
        local_max = _from_jd(times[0])
        if local_max is None or abs((local_max - global_max).total_seconds()) > 172800:
            next_flags = 0
            contact_map = {name: None for name in ("C1", "C2", "MAX", "C3", "C4")}
            local_max = None
            attrs = (None,) * 20
        local_attrs = attrs if local_max is not None else swe.sol_eclipse_how(event_max_jd, coordinates, flags)[1]
        observer = _observer_position(project_root, event_type, local_max or global_max, locality)
        return {
            "localEclipseType": _local_type(int(next_flags), event_type, local_max),
            "visibility": "VISIBLE" if local_max is not None else "NOT_VISIBLE",
            "contacts": contact_map,
            "localMaxUtc": _iso(local_max),
            "sunriseDuring": _iso(_from_jd(times[5])) if local_max is not None else None,
            "sunsetDuring": _iso(_from_jd(times[6])) if local_max is not None else None,
            "magnitude": _finite(local_attrs[0]),
            "obscuration": _finite(local_attrs[2]),
            "apparentDiameterRatio": _finite(local_attrs[1]),
            "sunAltitudeAzimuth": {"azimuthDeg": _finite(local_attrs[4]), "altitudeTrueDeg": _finite(local_attrs[5]), "altitudeApparentDeg": _finite(local_attrs[6])},
            "moonAltitudeAzimuth": observer["moon"],
            "apparentMoonSunDiameterRatio": _finite(local_attrs[1]),
            "coreShadowDiameterKm": _finite(local_attrs[3]) if local_max is not None else None,
            "saros": {"series": _finite(local_attrs[9], 0), "member": _finite(local_attrs[10], 0)} if local_max is not None else None,
            "rawAttributes": [_finite(value) for value in attrs],
        }
    next_flags, times, attrs = swe.lun_eclipse_when_loc(event_max_jd - 1.0, coordinates, flags)
    contact_map = _lunar_contacts(times)
    local_max = _from_jd(times[0])
    if local_max is None or abs((local_max - global_max).total_seconds()) > 172800:
        next_flags = 0
        contact_map = {name: None for name in ("P1", "U1", "U2", "MAX", "U3", "U4", "P4")}
        local_max = None
    return {
        "localEclipseType": _local_type(int(next_flags), event_type, local_max),
        "visibility": "VISIBLE" if local_max is not None else "NOT_VISIBLE",
        "contacts": contact_map,
        "localMaxUtc": _iso(local_max),
        "moonAltitudeAzimuth": _observer_position(project_root, event_type, local_max or global_max, locality)["moon"],
        "sunAltitudeAzimuth": _observer_position(project_root, event_type, local_max or global_max, locality)["sun"],
        "umbralMagnitude": _finite(attrs[0]) if attrs and local_max is not None else None,
        "penumbralMagnitude": _finite(attrs[1]) if attrs and local_max is not None else None,
        "distanceFromOppositionDeg": _finite(attrs[7]) if attrs and local_max is not None else None,
        "moonriseDuring": _iso(_from_jd(times[8])) if local_max is not None else None,
        "moonsetDuring": _iso(_from_jd(times[9])) if local_max is not None else None,
        "rawAttributes": [_finite(value) for value in attrs],
    }


def _event_identity(event_type: str, global_max: datetime, global_type: str) -> dict[str, Any]:
    identity = {"eventType": event_type, "globalMaxUtc": _iso(global_max), "globalType": global_type}
    return {
        "causalEventId": f"CGVO-{event_type}-{_hash(identity)[:20]}",
        "eventIdentity": identity,
    }


def _build_event(project_root: Path, event_type: str, flags: int, times: tuple[float, ...], locality: Mapping[str, Any] | None = None) -> dict[str, Any]:
    global_max = _from_jd(times[0])
    if global_max is None:
        raise RuntimeError("Swiss Ephemeris returned an eclipse without a global maximum")
    global_type = _global_type(int(flags), event_type)
    identity = _event_identity(event_type, global_max, global_type)
    if event_type == "SOLAR":
        global_contacts = _solar_global_contacts(times)
    else:
        global_contacts = _lunar_contacts(times)
    event = {
        **identity,
        "astronomyEventIdentity": {
            "eventType": event_type,
            "globalType": global_type,
            "globalMaxUtc": _iso(global_max),
            "globalContacts": global_contacts,
            "astronomyContract": MODERN_ASTRONOMY_CONTRACT,
            "ephemeris": "Swiss Ephemeris",
            "ephemerisVersion": str(getattr(swe, "version", "unknown")),
            "timeScale": "UT1_PRIMARY_SWISSEPH_UT",
            "deltaTModel": "SWISS_EPHEMERIS_INTERNAL",
        },
        "locality": None,
        "modernAstronomy": None,
        "observationalContext": {"saros": None, "sarosStatus": "MODERN_CONTEXT_ONLY_NOT_EXPOSED"},
        "varahamihiraClaims": [],
        "trailokyaClaims": [],
        "historicalRegionCandidates": [],
        "sourceUnknowns": list(SOURCE_UNKNOWN_REASONS),
        "provenance": [
            {"kind": "MODERN_ASTRONOMY", "contract": MODERN_ASTRONOMY_CONTRACT, "status": "FACTUAL_ENGINE_OUTPUT"},
            {"kind": "TIME", "primaryTimeScale": "UT1", "timezoneRole": "DISPLAY_ONLY"},
        ],
        "guardrails": _guardrails(),
    }
    if locality is not None:
        local = _local_circumstances(project_root, event_type, global_max, locality)
        event["locality"] = dict(locality)
        event["modernAstronomy"] = {"globalType": global_type, **local}
    return event


def _next_global_event(event_type: str, after: datetime) -> tuple[int, tuple[float, ...]]:
    configure_ephemeris(None)
    if event_type == "SOLAR":
        return swe.sol_eclipse_when_glob(_jd(after), swe.FLG_SWIEPH)
    return swe.lun_eclipse_when(_jd(after), swe.FLG_SWIEPH)


def _source_profile(project_root: Path, path: Path) -> dict[str, Any]:
    return _load_json(project_root, path)


def build_cgvo_status(project_root: Path) -> dict[str, Any]:
    return {
        "contract": CGVO_CONTRACT,
        "schemaVersion": 1,
        "milestone": "PFR-V2B-CGVO-P1",
        "status": "RESEARCH_INSPECTOR_READY_FOR_FOUNDER_REVIEW",
        "availableProfiles": ["MODERN_ASTRONOMY_VISIBILITY_V1", VARAHAMIHIRA_PROFILE_ID, TRAILOKYA_PROFILE_ID],
        "availableEventTypes": ["SOLAR", "LUNAR"],
        "guardrails": _guardrails(),
        "sourceProfiles": {
            "varahamihira": _source_profile(project_root, VARAHAMIHIRA_FIXTURE)["sourceStatus"],
            "trailokya": _source_profile(project_root, TRAILOKYA_FIXTURE)["sourceStatus"],
        },
    }


def build_cgvo_source_profiles(project_root: Path) -> dict[str, Any]:
    varahamihira = _source_profile(project_root, VARAHAMIHIRA_FIXTURE)
    trailokya = _source_profile(project_root, TRAILOKYA_FIXTURE)
    return {
        "contract": "CGVO_SOURCE_PROFILE_BUNDLE_V1",
        "profiles": [varahamihira, trailokya],
        "guardrails": _guardrails(),
        "crossSourceComposition": "NOT_AUTHORIZED",
    }


def build_cgvo_kurma_seed(project_root: Path) -> dict[str, Any]:
    return _load_json(project_root, KURMA_FIXTURE)


def build_cgvo_event_search(project_root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    start = _parse_utc(payload.get("startUtc"), "startUtc")
    end = _parse_utc(payload.get("endUtc"), "endUtc")
    if end <= start:
        raise CgvoRequestError("endUtc must be after startUtc")
    if end - start > timedelta(days=MAX_SEARCH_DAYS):
        raise CgvoRequestError(f"CGVO search range cannot exceed {MAX_SEARCH_DAYS} days")
    event_type = str(payload.get("eventType") or "SOLAR").upper()
    if event_type not in {"SOLAR", "LUNAR"}:
        raise CgvoRequestError("eventType must be SOLAR or LUNAR")
    try:
        limit = max(1, min(SEARCH_LIMIT, int(payload.get("limit") or 12)))
    except (TypeError, ValueError) as exc:
        raise CgvoRequestError("limit must be an integer") from exc
    events: list[dict[str, Any]] = []
    cursor = start - timedelta(hours=1)
    for _ in range(limit + 12):
        flags, times = _next_global_event(event_type, cursor)
        event_max = _from_jd(times[0])
        if event_max is None or event_max <= cursor:
            raise RuntimeError("Swiss Ephemeris did not advance the CGVO event search")
        if event_max >= end:
            break
        if event_max >= start:
            events.append(_build_event(project_root, event_type, int(flags), times))
            if len(events) >= limit:
                break
        cursor = event_max + timedelta(seconds=1)
    return {
        "contract": "CGVO_ECLIPSE_SEARCH_RANGE_V1",
        "range": {"startUtc": _iso(start), "endUtc": _iso(end)},
        "eventType": event_type,
        "events": events,
        "count": len(events),
        "selection": "CHRONOLOGICAL_GLOBAL_MAXIMUM_WITHIN_REQUESTED_RANGE",
        "guardrails": _guardrails(),
    }


def build_cgvo_local_circumstances(project_root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    event_type = str(payload.get("eventType") or "").upper()
    if event_type not in {"SOLAR", "LUNAR"}:
        raise CgvoRequestError("eventType must be SOLAR or LUNAR")
    global_max = _parse_utc(payload.get("globalMaxUtc"), "globalMaxUtc")
    locality = _validate_locality(payload)
    flags = int(payload.get("globalFlags") or 0)
    if not flags:
        # The identity is still caller-independent: global facts are resolved
        # from the timestamp rather than trusting a frontend-created flag.
        flags, times = _next_global_event(event_type, global_max - timedelta(minutes=1))
        resolved_max = _from_jd(times[0])
        if resolved_max is None or abs((resolved_max - global_max).total_seconds()) > 3600:
            raise CgvoRequestError("globalMaxUtc does not resolve to the requested eclipse identity")
    else:
        _, times = _next_global_event(event_type, global_max - timedelta(minutes=1))
    event = _build_event(project_root, event_type, int(flags), times, locality)
    if event["astronomyEventIdentity"]["globalMaxUtc"] != _iso(global_max):
        raise CgvoRequestError("globalMaxUtc does not match the immutable Swiss Ephemeris event identity")
    return {
        "contract": "CGVO_LOCAL_CIRCUMSTANCES_V1",
        "event": event,
        "sourceProfiles": build_cgvo_source_profiles(project_root)["profiles"],
        "kurma": build_cgvo_kurma_seed(project_root),
        "guardrails": _guardrails(),
    }


def build_cgvo_workbench(project_root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    event_type = str(payload.get("eventType") or "SOLAR").upper()
    if payload.get("globalMaxUtc"):
        local_payload = dict(payload)
        local_payload["eventType"] = event_type
        local = build_cgvo_local_circumstances(project_root, local_payload)
        event = local["event"]
    else:
        start = _parse_utc(payload.get("startUtc") or "2027-01-01T00:00:00Z", "startUtc")
        end = _parse_utc(payload.get("endUtc") or "2028-01-01T00:00:00Z", "endUtc")
        search = build_cgvo_event_search(project_root, {"startUtc": _iso(start), "endUtc": _iso(end), "eventType": event_type, "limit": 12})
        event = search["events"][0] if search["events"] else None
    return {
        "contract": CGVO_CONTRACT,
        "schemaVersion": 1,
        "event": event,
        "sourceProfiles": build_cgvo_source_profiles(project_root)["profiles"],
        "kurma": build_cgvo_kurma_seed(project_root),
        "guardrails": _guardrails(),
    }
