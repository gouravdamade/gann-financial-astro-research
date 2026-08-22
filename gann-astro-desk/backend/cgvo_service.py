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
from threading import RLock
from typing import Any, Mapping
import unicodedata
from zoneinfo import ZoneInfo

import swisseph as swe
import yaml

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
KURMA_G1_GAZETTEER_FIXTURE = CGVO_ROOT / "kurma_historical_geography_g1_v1.json"
GEOGRAPHY_SOURCE_LAYERS_FIXTURE = CGVO_ROOT / "cgvo_geography_source_layers_g1_v1.json"
GEOGRAPHY_G2_POLICY_FIXTURE = CGVO_ROOT / "cgvo_historical_geography_geometry_policy_g2_v1.json"
KURMA_G2_FOOTPRINTS_FIXTURE = CGVO_ROOT / "kurma_research_footprints_g2_v1.json"
CGVO_G2_R1_SITE_EVIDENCE_FIXTURE = CGVO_ROOT / "cgvo_g2_r1_historical_site_coordinate_evidence_v1.json"
CGVO_G2_READINESS_FIXTURE = CGVO_ROOT / "cgvo_g2_readiness_matrix_v1.json"
VARAHAMIHIRA_FIXTURE = CGVO_ROOT / "varahamihira_eclipse_source_profile_v1.json"
TRAILOKYA_FIXTURE = CGVO_ROOT / "trailokya_geography_argha_context_v1.json"
VARAHAMIHIRA_FRAME_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_ASTRONOMICAL_FRAME_V1.yaml"
VARAHAMIHIRA_LUNAR_MONTH_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_LUNAR_MONTH_PROFILE_V1.yaml"
VARAHAMIHIRA_ASPECT_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_ECLIPSE_ASPECT_PROFILE_V1.yaml"
VARAHAMIHIRA_FIRMAMENT_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_FIRMAMENT_GEOMETRY_V1.yaml"
CGVO_S1_READINESS_FIXTURE = CGVO_ROOT / "CGVO_S1_READINESS_MATRIX_V1.yaml"
VARAHAMIHIRA_ABSOLUTE_FRAME_AUDIT_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_ABSOLUTE_FRAME_AUDIT_V2.yaml"
PANCHASIDDHANTIKA_FIXED_STAR_LEDGER_FIXTURE = CGVO_ROOT / "PANCHASIDDHANTIKA_FIXED_STAR_SOURCE_LEDGER_V1.yaml"
VARAHAMIHIRA_SOLAR_PHASE_MAPPING_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_SOLAR_ECLIPSE_PHASE_MAPPING_V1.yaml"
VARAHAMIHIRA_LUNAR_PHASE_MAPPING_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_LUNAR_ECLIPSE_PHASE_MAPPING_V1.yaml"
VARAHAMIHIRA_FIRMAMENT_ADJUDICATION_FIXTURE = CGVO_ROOT / "VARAHAMIHIRA_FIRMAMENT_SOURCE_ADJUDICATION_V2.yaml"
CGVO_S1B_READINESS_FIXTURE = CGVO_ROOT / "CGVO_S1B_R1_READINESS_MATRIX.yaml"
VARAHAMIHIRA_CHITRA_FRAME_ID = "VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1"
SOURCE_UNKNOWN_REASONS = [
    "VARAHAMIHIRA_ABSOLUTE_FRAME_RECONSTRUCTION_NOT_DEFAULT",
    "VARAHAMIHIRA_FIRMAMENT_CLASSIFIER_NOT_SOURCE_CLOSED",
    "VARAHAMIHIRA_LUNAR_MONTH_INTERCALATION_PROFILE_NOT_CLOSED",
    "VARAHAMIHIRA_MORPHOLOGY_MAPPING_UNRESOLVED",
    "VARAHAMIHIRA_COLOUR_OBSERVATION_REQUIRED",
    "TRAILOKYA_ECLIPSE_VISIBILITY_SOURCE_SILENT",
]
MAX_SEARCH_DAYS = 3700
SEARCH_LIMIT = 24
_JD_UNIX_EPOCH = 2440587.5
_EPHEMERIS_LOCK = RLock()

_RASI_NAMES = (
    "MESHA", "VRISHABHA", "MITHUNA", "KARKATAKA", "SIMHA", "KANYA",
    "TULA", "VRISCHIKA", "DHANUS", "MAKARA", "KUMBHA", "MEENA",
)
_NAKSHATRA_NAMES = (
    "ASHWINI", "BHARANI", "KRITTIKA", "ROHINI", "MRIGASHIRSHA", "ARDRA",
    "PUNARVASU", "PUSHYA", "ASHLESHA", "MAGHA", "PURVA_PHALGUNI",
    "UTTARA_PHALGUNI", "HASTA", "CHITRA", "SWATI", "VISHAKHA", "ANURADHA",
    "JYESHTHA", "MULA", "PURVA_ASHADHA", "UTTARA_ASHADHA", "SHRAVANA",
    "DHANISHTHA", "SHATABHISHA", "PURVA_BHADRAPADA", "UTTARA_BHADRAPADA", "REVATI",
)
_PLANET_IDS = {
    "MERCURY": swe.MERCURY,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
    "SUN": swe.SUN,
    "MOON": swe.MOON,
}
_LUNAR_MONTH_BY_FULL_MOON_NAKSHATRA = {
    "CHITRA": "CHAITRA", "VISHAKHA": "VAISHAKHA", "JYESHTHA": "JYESHTHA",
    "PURVA_ASHADHA": "ASHADHA", "UTTARA_ASHADHA": "ASHADHA", "SHRAVANA": "SHRAVANA",
    "PURVA_BHADRAPADA": "BHADRAPADA", "UTTARA_BHADRAPADA": "BHADRAPADA",
    "ASHWINI": "ASHVINA", "KRITTIKA": "KARTIKA", "MRIGASHIRSHA": "MARGASHIRSHA",
    "PUSHYA": "PAUSHA", "MAGHA": "MAGHA", "PURVA_PHALGUNI": "PHALGUNA", "UTTARA_PHALGUNI": "PHALGUNA",
}


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


def _load_yaml(project_root: Path, relative_path: Path) -> dict[str, Any]:
    path = project_root / relative_path
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"CGVO source fixture is missing: {relative_path.as_posix()}") from exc
    except yaml.YAMLError as exc:
        raise RuntimeError(f"CGVO source fixture is invalid YAML: {relative_path.as_posix()}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"CGVO source fixture must be a YAML object: {relative_path.as_posix()}")
    return payload


def _s1a_fixtures(project_root: Path) -> dict[str, dict[str, Any]]:
    return {
        "frame": _load_yaml(project_root, VARAHAMIHIRA_FRAME_FIXTURE),
        "lunarMonth": _load_yaml(project_root, VARAHAMIHIRA_LUNAR_MONTH_FIXTURE),
        "aspect": _load_yaml(project_root, VARAHAMIHIRA_ASPECT_FIXTURE),
        "firmament": _load_yaml(project_root, VARAHAMIHIRA_FIRMAMENT_FIXTURE),
        "readiness": _load_yaml(project_root, CGVO_S1_READINESS_FIXTURE),
    }


def _s1b_fixtures(project_root: Path) -> dict[str, dict[str, Any]]:
    return {
        "absoluteFrameAudit": _load_yaml(project_root, VARAHAMIHIRA_ABSOLUTE_FRAME_AUDIT_FIXTURE),
        "panchasiddhantikaFixedStarLedger": _load_yaml(project_root, PANCHASIDDHANTIKA_FIXED_STAR_LEDGER_FIXTURE),
        "solarPhaseMapping": _load_yaml(project_root, VARAHAMIHIRA_SOLAR_PHASE_MAPPING_FIXTURE),
        "lunarPhaseMapping": _load_yaml(project_root, VARAHAMIHIRA_LUNAR_PHASE_MAPPING_FIXTURE),
        "firmamentAdjudication": _load_yaml(project_root, VARAHAMIHIRA_FIRMAMENT_ADJUDICATION_FIXTURE),
        "readiness": _load_yaml(project_root, CGVO_S1B_READINESS_FIXTURE),
    }


def _frame_profile_id(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("absoluteFrameProfileId")
    if value in (None, ""):
        return None
    if not isinstance(value, str) or value != VARAHAMIHIRA_CHITRA_FRAME_ID:
        raise CgvoRequestError(
            "absoluteFrameProfileId must be omitted or " + VARAHAMIHIRA_CHITRA_FRAME_ID
        )
    return value


def _tropical_longitude(at_utc: datetime, body: str) -> float:
    body_id = _PLANET_IDS[body]
    values, _ = swe.calc_ut(_jd(at_utc), body_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return float(values[0]) % 360.0


def _chitra_180_offset(at_utc: datetime) -> float:
    values, _, _ = swe.fixstar2_ut("Spica", _jd(at_utc), swe.FLG_SWIEPH)
    return (float(values[0]) - 180.0) % 360.0


_CHITRA_AUDIT_FLAGS = {
    "CHITRA_180_APPARENT_TRUE_EQUINOX": swe.FLG_SWIEPH,
    "CHITRA_180_APPARENT_MEAN_EQUINOX": swe.FLG_SWIEPH | swe.FLG_NONUT,
    "CHITRA_180_TRUE_GEOMETRIC_TRUE_EQUINOX": swe.FLG_SWIEPH | swe.FLG_TRUEPOS,
    "CHITRA_180_TRUE_NOABERR_NODEFL": swe.FLG_SWIEPH | swe.FLG_TRUEPOS | swe.FLG_NOABERR | swe.FLG_NOGDEFL,
    "CHITRA_180_TRUE_NOABERR_NODEFL_MEAN_EQUINOX": swe.FLG_SWIEPH | swe.FLG_TRUEPOS | swe.FLG_NOABERR | swe.FLG_NOGDEFL | swe.FLG_NONUT,
}


def _chitra_audit_offset(at_utc: datetime, audit_profile_id: str) -> tuple[float, float, int]:
    """Return Spica's modern coordinate, offset, and Swiss returned flags for audit only."""
    try:
        flags = _CHITRA_AUDIT_FLAGS[audit_profile_id]
    except KeyError as exc:
        raise RuntimeError(f"Unsupported Chitra audit profile: {audit_profile_id}") from exc
    with _EPHEMERIS_LOCK:
        configure_ephemeris(None)
        values, _, returned_flags = swe.fixstar2_ut("Spica", _jd(at_utc), flags)
    longitude = float(values[0]) % 360.0
    return longitude, (longitude - 180.0) % 360.0, int(returned_flags)


def _rasi_nakshatra(at_utc: datetime, body: str, frame_profile_id: str | None) -> dict[str, Any]:
    if frame_profile_id is None:
        return {
            "availability": "ABSOLUTE_FRAME_NOT_SELECTED",
            "profileId": None,
            "rasi": None,
            "nakshatra": None,
            "pada": None,
            "siderealLongitudeDeg": None,
            "candidateOffsetDeg": None,
        }
    tropical = _tropical_longitude(at_utc, body)
    offset = _chitra_180_offset(at_utc)
    sidereal = (tropical - offset) % 360.0
    nakshatra_index = min(26, int(sidereal / (360.0 / 27.0)))
    pada = min(4, int((sidereal % (360.0 / 27.0)) / (360.0 / 108.0)) + 1)
    return {
        "availability": "SOURCE_RECONSTRUCTION_CANDIDATE_CALCULATED",
        "profileId": frame_profile_id,
        "rasi": _RASI_NAMES[int(sidereal // 30.0)],
        "rasiIndex": int(sidereal // 30.0) + 1,
        "nakshatra": _NAKSHATRA_NAMES[nakshatra_index],
        "nakshatraIndex": nakshatra_index + 1,
        "pada": pada,
        "siderealLongitudeDeg": _finite(sidereal, 6),
        "tropicalLongitudeDeg": _finite(tropical, 6),
        "candidateOffsetDeg": _finite(offset, 6),
        "anchor": "SPICA_CHITRA_AT_180_DEGREES",
    }


def _phase_angle(at_utc: datetime) -> float:
    return (_tropical_longitude(at_utc, "MOON") - _tropical_longitude(at_utc, "SUN")) % 360.0


def _full_moons_around(at_utc: datetime) -> list[datetime]:
    """Find physical full-moon crossings without importing a calendar convention."""
    start = at_utc - timedelta(days=38)
    end = at_utc + timedelta(days=38)
    step = timedelta(hours=3)
    points: list[datetime] = []
    left = start
    left_phase = _phase_angle(left)
    while left < end:
        right = min(left + step, end)
        right_phase = _phase_angle(right)
        if left_phase < 180.0 <= right_phase:
            lo, hi = left, right
            for _ in range(32):
                mid = lo + ((hi - lo) / 2)
                if _phase_angle(mid) < 180.0:
                    lo = mid
                else:
                    hi = mid
            points.append(hi.replace(microsecond=0))
        left, left_phase = right, right_phase
    return points


def _new_moons_around(at_utc: datetime) -> list[datetime]:
    """Find physical conjunction boundaries for a conservative calendar guard."""
    start = at_utc - timedelta(days=50)
    end = at_utc + timedelta(days=50)
    step = timedelta(hours=3)
    points: list[datetime] = []
    left = start
    left_phase = _phase_angle(left)
    while left < end:
        right = min(left + step, end)
        right_phase = _phase_angle(right)
        if left_phase > right_phase:
            lo, hi = left, right
            for _ in range(32):
                mid = lo + ((hi - lo) / 2)
                if _phase_angle(mid) > 180.0:
                    lo = mid
                else:
                    hi = mid
            points.append(hi.replace(microsecond=0))
        left, left_phase = right, right_phase
    return points


def _solar_rasi_ingresses(
    start_utc: datetime,
    end_utc: datetime,
    frame_profile_id: str,
) -> list[dict[str, Any]]:
    """Find actual selected-frame solar rasi boundaries inside one synodic interval."""
    step = timedelta(hours=6)
    events: list[dict[str, Any]] = []
    left = start_utc
    left_rasi = _rasi_nakshatra(left, "SUN", frame_profile_id)
    while left < end_utc:
        right = min(left + step, end_utc)
        right_rasi = _rasi_nakshatra(right, "SUN", frame_profile_id)
        if left_rasi["rasiIndex"] != right_rasi["rasiIndex"]:
            lo, hi = left, right
            prior_index = int(left_rasi["rasiIndex"])
            for _ in range(40):
                mid = lo + ((hi - lo) / 2)
                if int(_rasi_nakshatra(mid, "SUN", frame_profile_id)["rasiIndex"]) == prior_index:
                    lo = mid
                else:
                    hi = mid
            ingress = _rasi_nakshatra(hi, "SUN", frame_profile_id)
            if int(ingress["rasiIndex"]) == prior_index:
                raise RuntimeError("SANKRANTI_BOUNDARY_NOT_RESOLVED")
            events.append({
                "atUtc": _iso(hi.replace(microsecond=0)),
                "fromRasi": left_rasi["rasi"],
                "toRasi": ingress["rasi"],
                "frameProfileId": frame_profile_id,
            })
        left, left_rasi = right, right_rasi
    return events


def _purnimanta_intercalation_guard(
    at_utc: datetime,
    previous_full: datetime,
    next_full: datetime,
    frame_profile_id: str,
) -> dict[str, Any]:
    new_moons = _new_moons_around(at_utc)
    intervals = [
        (start, end)
        for start, end in zip(new_moons, new_moons[1:])
        if end > previous_full and start < next_full
    ]
    if not intervals:
        return {
            "status": "AMBIGUOUS_OR_INTERCALARY",
            "reason": "NEW_MOON_BOUNDARIES_NOT_RESOLVED",
            "synodicIntervals": [],
        }
    records: list[dict[str, Any]] = []
    try:
        for start, end in intervals:
            ingresses = _solar_rasi_ingresses(start, end, frame_profile_id)
            records.append({
                "startNewMoonUtc": _iso(start),
                "endNewMoonUtc": _iso(end),
                "sankrantiCount": len(ingresses),
                "ingressEvents": ingresses,
            })
    except Exception:
        return {
            "status": "AMBIGUOUS_OR_INTERCALARY",
            "reason": "SANKRANTI_BOUNDARY_NOT_RESOLVED",
            "synodicIntervals": records,
        }
    if any(record["sankrantiCount"] != 1 for record in records):
        return {
            "status": "AMBIGUOUS_OR_INTERCALARY",
            "reason": "ADHIKA_OR_KSHAYA_GUARD_TRIGGERED",
            "synodicIntervals": records,
        }
    return {
        "status": "CLEAR_ORDINARY",
        "reason": None,
        "synodicIntervals": records,
    }


def _lunar_month_unknown(
    fixture: Mapping[str, Any],
    reason: str,
    **details: Any,
) -> dict[str, Any]:
    return {
        "baseSystem": "PURNIMANTA",
        "evidenceStatus": fixture["sourceStatus"],
        "result": "UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED",
        "unknownReason": reason,
        **details,
    }


def _lunar_month_adapter(
    at_utc: datetime,
    locality: Mapping[str, Any] | None,
    frame_profile_id: str | None,
    fixture: Mapping[str, Any],
) -> dict[str, Any]:
    if locality is None:
        return _lunar_month_unknown(
            fixture,
            "LOCALITY_REQUIRED_FOR_SOURCE_DAY_PROVENANCE",
            intercalationGuard={"status": "NOT_EVALUATED", "synodicIntervals": []},
        )
    if frame_profile_id is None:
        return _lunar_month_unknown(
            fixture,
            "ABSOLUTE_FRAME_PROFILE_NOT_SELECTED",
            intercalationGuard={"status": "NOT_EVALUATED", "synodicIntervals": []},
        )
    full_moons = _full_moons_around(at_utc)
    before = [moment for moment in full_moons if moment <= at_utc]
    after = [moment for moment in full_moons if moment >= at_utc]
    if not before or not after:
        return _lunar_month_unknown(fixture, "FULL_MOON_BOUNDARY_NOT_RESOLVED")
    previous_full, next_full = before[-1], after[0]
    if next_full - previous_full < timedelta(hours=12):
        next_candidates = [moment for moment in full_moons if moment > previous_full + timedelta(days=20)]
        if not next_candidates:
            return _lunar_month_unknown(fixture, "NEXT_FULL_MOON_NOT_RESOLVED")
        next_full = next_candidates[0]
    guard = _purnimanta_intercalation_guard(at_utc, previous_full, next_full, frame_profile_id)
    if guard["status"] != "CLEAR_ORDINARY":
        return _lunar_month_unknown(
            fixture,
            str(guard["reason"]),
            previousFullMoonUtc=_iso(previous_full),
            nextFullMoonUtc=_iso(next_full),
            intercalationGuard=guard,
        )
    month_star = _rasi_nakshatra(next_full, "MOON", frame_profile_id)
    month_name = _LUNAR_MONTH_BY_FULL_MOON_NAKSHATRA.get(str(month_star["nakshatra"]))
    if month_name is None:
        return _lunar_month_unknown(
            fixture,
            "MONTH_NAME_NOT_MAPPED",
            intercalationGuard=guard,
        )
    local = at_utc.astimezone(ZoneInfo(str(locality["timezone"])))
    return {
        "baseSystem": "PURNIMANTA", "evidenceStatus": fixture["sourceStatus"],
        "result": month_name, "monthAnchorNakshatra": month_star["nakshatra"],
        "previousFullMoonUtc": _iso(previous_full), "nextFullMoonUtc": _iso(next_full),
        "sourceDayLocal": local.date().isoformat(), "timezone": locality["timezone"],
        "localityId": locality["localityId"], "calculationStatus": "ORDINARY_UNAMBIGUOUS_PURNIMANTA_CASE",
        "intercalationGuard": guard,
    }


def _source_phase_activation(phase_fixture: Mapping[str, Any] | None) -> dict[str, Any]:
    if phase_fixture is None:
        return {
            "requiredBySource": "COMMENCEMENT_OR_CONCLUSION",
            "status": "UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED",
            "commencement": None,
            "conclusion": None,
            "effectActivated": None,
            "jupiterMitigationActivated": None,
        }
    phase = phase_fixture["phaseActivation"]
    return {
        "requiredBySource": "COMMENCEMENT_OR_CONCLUSION",
        "status": phase["status"],
        "commencement": phase["commencement"],
        "conclusion": phase["conclusion"],
        "effectActivated": phase["effectActivated"],
        "jupiterMitigationActivated": phase["jupiterMitigationActivated"],
        "mappingContract": phase_fixture["contract"],
        "modernCandidateLabels": phase_fixture["modernCandidateLabels"],
    }


def _eclipse_aspect_adapter(
    at_utc: datetime,
    event_type: str,
    frame_profile_id: str | None,
    fixture: Mapping[str, Any],
    phase_fixture: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if frame_profile_id is None:
        return {
            "geometryStatus": fixture["sourceStatus"], "frameStatus": "ABSOLUTE_FRAME_NOT_SELECTED",
            "auditGeometryAtMaximum": {
                "timeSwissUt": _iso(at_utc), "records": [], "role": "GEOMETRY_SNAPSHOT_ONLY",
            },
            "sourcePhaseActivation": _source_phase_activation(phase_fixture),
            "effectMagnitudeMultiplier": None, "jupiterMitigationCoefficient": None,
        }
    eclipsed_body = "SUN" if event_type == "SOLAR" else "MOON"
    target = _rasi_nakshatra(at_utc, eclipsed_body, frame_profile_id)
    fractions = {int(key): float(value) for key, value in fixture["ordinarySignFractions"].items()}
    special = {str(key): {int(item) for item in values} for key, values in fixture["specialFullAspects"].items()}
    records: list[dict[str, Any]] = []
    for planet in ("MERCURY", "MARS", "JUPITER", "VENUS", "SATURN"):
        source = _rasi_nakshatra(at_utc, planet, frame_profile_id)
        distance = ((int(target["rasiIndex"]) - int(source["rasiIndex"])) % 12) + 1
        fraction = 1.0 if distance in special.get(planet, set()) else fractions.get(distance, 0.0)
        records.append({
            "planet": planet, "eclipsedLuminary": eclipsed_body,
            "aspectingRasi": source["rasi"], "eclipsedRasi": target["rasi"],
            "signDistance": distance, "fraction": fraction, "aspectExists": fraction > 0.0,
            "sourceEffectToken": fixture["effectTokens"].get(planet) if fraction > 0.0 else None,
            "calculation": "SIGN_RELATIVE_JYOTISHA_COUNTING", "sourceStatus": fixture["sourceStatus"],
        })
    return {
        "geometryStatus": fixture["sourceStatus"], "frameStatus": "SOURCE_RECONSTRUCTION_CANDIDATE_CALCULATED",
        "eclipsedLuminary": eclipsed_body,
        "auditGeometryAtMaximum": {
            "timeSwissUt": _iso(at_utc), "records": records, "role": "GEOMETRY_SNAPSHOT_ONLY",
        },
        "sourcePhaseActivation": _source_phase_activation(phase_fixture),
        "effectMagnitudeMultiplier": None, "jupiterMitigationCoefficient": None,
    }


def _firmament_adapter(
    at_utc: datetime, event_type: str, locality: Mapping[str, Any] | None, fixture: Mapping[str, Any], modern: Mapping[str, Any] | None
) -> dict[str, Any]:
    body_key = "sun" if event_type == "SOLAR" else "moon"
    coordinates = (modern or {}).get(f"{body_key}AltitudeAzimuth")
    if locality is None or not isinstance(coordinates, Mapping):
        raw_geometry: dict[str, Any] = {"availability": "LOCALITY_OR_HORIZONTAL_COORDINATES_NOT_AVAILABLE"}
    else:
        raw_geometry = {
            "availability": "RAW_MODERN_GEOMETRY_AVAILABLE", "apparentAltitudeDeg": coordinates.get("altitudeApparentDeg"),
            "normalizedAzimuthDeg": coordinates.get("azimuthDeg"), "rawSwissAzimuthDeg": coordinates.get("sourceAzimuthDeg"),
            "rightAscensionDeg": coordinates.get("rightAscensionDeg"),
            "localHourAngleDeg": coordinates.get("localHourAngleDeg"), "riseSetState": (modern or {}).get("visibility"),
            "meridianRelation": coordinates.get("meridianRelation"),
            "calculation": "LOCALITY_SCOPED_TOPOCENTRIC_OBSERVER_STATE",
        }
    return {
        "status": fixture["sourceStatus"], "rawGeometry": raw_geometry,
        "classicalSection": "UNKNOWN", "sourceCertifiedClassifier": False,
        "nonVotingComparisonCandidates": fixture["nonVotingComparisonCandidates"],
    }


def _attach_s1a_source_adapters(project_root: Path, event: dict[str, Any], payload: Mapping[str, Any]) -> None:
    fixtures = _s1a_fixtures(project_root)
    s1b = _s1b_fixtures(project_root)
    frame_profile_id = _frame_profile_id(payload)
    identity = event["astronomyEventIdentity"]
    at_utc = _parse_utc(identity["globalMaxSwissUt"], "globalMaxSwissUt")
    event_type = str(identity["eventType"])
    locality = event.get("locality") if isinstance(event.get("locality"), Mapping) else None
    modern = event.get("modernAstronomy") if isinstance(event.get("modernAstronomy"), Mapping) else None
    luminary = "SUN" if event_type == "SOLAR" else "MOON"
    event["sourceAdapters"] = {
        "varahamihiraFrame": {
            "partitionStatus": fixtures["frame"]["sourceAuthority"],
            "absoluteFrameStatus": "NULL" if frame_profile_id is None else "SOURCE_RECONSTRUCTION_CANDIDATE",
            "selectedProfileId": frame_profile_id,
            "luminary": _rasi_nakshatra(at_utc, luminary, frame_profile_id),
            "partition": fixtures["frame"]["partition"],
            "precessionalDistinction": fixtures["frame"]["precessionalDistinction"],
        },
        "varahamihiraLunarMonth": _lunar_month_adapter(at_utc, locality, frame_profile_id, fixtures["lunarMonth"]),
        "varahamihiraAspect": _eclipse_aspect_adapter(
            at_utc,
            event_type,
            frame_profile_id,
            fixtures["aspect"],
            s1b["solarPhaseMapping"] if event_type == "SOLAR" else s1b["lunarPhaseMapping"],
        ),
        "varahamihiraFirmament": _firmament_adapter(at_utc, event_type, locality, fixtures["firmament"], modern),
    }
    event["sourceUnknowns"] = list(dict.fromkeys(event["sourceUnknowns"] + [
        "VARAHAMIHIRA_ABSOLUTE_FRAME_NOT_SELECTED" if frame_profile_id is None else "VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_CANDIDATE",
        "VARAHAMIHIRA_FIRMAMENT_CLASSIFIER_NOT_SOURCE_CLOSED",
    ]))


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


def _topocentric_body_states(event_max: datetime, locality: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Calculate all locality-dependent Swiss values in one process-global critical section."""
    longitude = float(locality["longitude"])
    latitude = float(locality["latitude"])
    elevation = float(locality["elevationM"])
    coordinates = (longitude, latitude, elevation)
    # Swiss Ephemeris returns azalt() azimuths from South toward West.  Keep
    # the raw value for audit, and expose the normalized compass convention
    # used by the UI: 0 North, 90 East, 180 South, 270 West.
    with _EPHEMERIS_LOCK:
        configure_ephemeris(None)
        swe.set_topo(longitude, latitude, elevation)
        event_jd = _jd(event_max)
        flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL | swe.FLG_TOPOCTR
        local_sidereal = (float(swe.sidtime(event_jd)) * 15.0 + longitude) % 360.0
        result: dict[str, dict[str, Any]] = {}
        for body, body_id in (("SUN", swe.SUN), ("MOON", swe.MOON)):
            values, _ = swe.calc_ut(event_jd, body_id, flags)
            source_azimuth, true_altitude, apparent_altitude = swe.azalt(event_jd, swe.EQU2HOR, coordinates, 0.0, 15.0, values)
            right_ascension = float(values[0])
            hour_angle = ((local_sidereal - right_ascension + 180.0) % 360.0) - 180.0
            normalized_azimuth = (float(source_azimuth) + 180.0) % 360.0
            result[body.lower()] = {
                "altitudeTrueDeg": _finite(true_altitude),
                "altitudeApparentDeg": _finite(apparent_altitude),
                "azimuthDeg": _finite(normalized_azimuth),
                "sourceAzimuthDeg": _finite(source_azimuth),
                "azimuthConvention": "NORTH_CLOCKWISE_0N_90E_180S_270W",
                "sourceAzimuthConvention": "SWISSEPH_SOUTH_CLOCKWISE_TO_WEST",
                "rightAscensionDeg": _finite(right_ascension, 6),
                "localHourAngleDeg": _finite(hour_angle, 6),
                "meridianRelation": "ON_MERIDIAN" if abs(hour_angle) < 0.25 else (
                    "EAST_OF_MERIDIAN" if hour_angle < 0 else "WEST_OF_MERIDIAN"
                ),
                "topocentric": True,
            }
    return result


def _observer_position(project_root: Path, event_type: str, event_max: datetime, locality: Mapping[str, Any]) -> dict[str, Any]:
    del project_root
    result = _topocentric_body_states(event_max, locality)
    result["calculation"] = "TOPOCENTRIC_HORIZONTAL_COORDINATES_AT_LOCAL_MAX"
    result["eventType"] = event_type
    return result


def _visibility_summary(
    event_type: str,
    flags: int,
    times: tuple[float, ...] | None,
    contacts: Mapping[str, str | None],
) -> dict[str, Any]:
    visible = bool(flags & swe.ECL_VISIBLE)
    maximum_visible = bool(flags & swe.ECL_MAX_VISIBLE)
    if not visible:
        status = "NOT_VISIBLE"
    elif maximum_visible:
        status = "VISIBLE"
    else:
        status = "RISE_SET_CLIPPED"

    if event_type == "SOLAR":
        phase_start_key, phase_end_key = "C1", "C4"
        rise_label, set_label = "sunrise", "sunset"
        rise_index, set_index = 5, 6
    else:
        phase_start_key, phase_end_key = "P1", "P4"
        rise_label, set_label = "moonrise", "moonset"
        rise_index, set_index = 8, 9

    rise = _from_jd(times[rise_index]) if times is not None else None
    set_time = _from_jd(times[set_index]) if times is not None else None

    phase_start = _parse_utc(contacts[phase_start_key], phase_start_key) if contacts.get(phase_start_key) else None
    phase_end = _parse_utc(contacts[phase_end_key], phase_end_key) if contacts.get(phase_end_key) else None
    visible_start = rise if rise and (phase_start is None or rise > phase_start) else phase_start
    visible_end = set_time if set_time and (phase_end is None or set_time < phase_end) else phase_end
    clipping: list[str] = []
    if rise is not None:
        clipping.append(rise_label.upper())
    if set_time is not None:
        clipping.append(set_label.upper())
    if status == "RISE_SET_CLIPPED" and not clipping:
        clipping.append("MAXIMUM_NOT_VISIBLE")
    return {
        "status": status,
        "maximumVisibility": "VISIBLE" if maximum_visible else "NOT_VISIBLE_AT_MAXIMUM",
        "visibleWindowStartUtc": _iso(visible_start),
        "visibleWindowEndUtc": _iso(visible_end),
        "clipBoundaries": clipping,
        "horizonEvents": {
            "riseUtc": _iso(rise),
            "setUtc": _iso(set_time),
        },
        "swissVisibilityFlags": int(flags),
    }


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
        visibility_details = _visibility_summary(event_type, int(next_flags), times if local_max is not None else None, contact_map)
        local_attrs = attrs if local_max is not None else swe.sol_eclipse_how(event_max_jd, coordinates, flags)[1]
        observer = _observer_position(project_root, event_type, local_max or global_max, locality)
        return {
            "localEclipseType": _local_type(int(next_flags), event_type, local_max if visibility_details["status"] != "NOT_VISIBLE" else None),
            "visibility": visibility_details["status"],
            "visibilityDetails": visibility_details,
            "contacts": contact_map,
            "localMaxUtc": _iso(local_max),
            "sunriseDuring": _iso(_from_jd(times[5])) if local_max is not None else None,
            "sunsetDuring": _iso(_from_jd(times[6])) if local_max is not None else None,
            "magnitude": _finite(local_attrs[0]),
            "obscuration": _finite(local_attrs[2]),
            "apparentDiameterRatio": _finite(local_attrs[1]),
            "sunAltitudeAzimuth": observer["sun"],
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
        attrs = (None,) * 20
    visibility_details = _visibility_summary(event_type, int(next_flags), times if local_max is not None else None, contact_map)
    observer = _observer_position(project_root, event_type, local_max or global_max, locality)
    _, magnitude_attrs = swe.lun_eclipse_how(_jd(local_max or global_max), coordinates, flags)
    return {
        "localEclipseType": _local_type(int(next_flags), event_type, local_max if visibility_details["status"] != "NOT_VISIBLE" else None),
        "visibility": visibility_details["status"],
        "visibilityDetails": visibility_details,
        "contacts": contact_map,
        "localMaxUtc": _iso(local_max),
        "moonAltitudeAzimuth": observer["moon"],
        "sunAltitudeAzimuth": observer["sun"],
        "umbralMagnitude": _finite(magnitude_attrs[0]),
        "penumbralMagnitude": _finite(magnitude_attrs[1]),
        "magnitudeReference": "SWISSEPH_LUNAR_ECLIPSE_HOW_AT_EVENT_MAX_SWISSEPH_UT",
        "distanceFromOppositionDeg": _finite(magnitude_attrs[7]),
        "moonriseDuring": _iso(_from_jd(times[8])) if local_max is not None else None,
        "moonsetDuring": _iso(_from_jd(times[9])) if local_max is not None else None,
        "rawAttributes": [_finite(value) for value in magnitude_attrs],
    }


def _event_identity(event_type: str, global_max: datetime, global_type: str) -> dict[str, Any]:
    swiss_ut = _iso(global_max)
    identity = {"eventType": event_type, "globalMaxSwissUt": swiss_ut, "globalType": global_type}
    return {
        "causalEventId": f"CGVO-{event_type}-{_hash(identity)[:20]}",
        "eventIdentity": {
            **identity,
            # Backward-compatible display alias.  It is never used to derive
            # the causal hash; the identity hash uses globalMaxSwissUt above.
            "globalMaxUtc": swiss_ut,
            "globalMaxUtcDisplay": swiss_ut,
            "identityTimeScale": "SWISSEPH_UT",
            "displayTimeScale": "UTC",
            "displayTimezone": "UTC",
        },
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
            "globalMaxSwissUt": _iso(global_max),
            "globalMaxUtc": _iso(global_max),
            "globalMaxUtcDisplay": _iso(global_max),
            "globalContacts": global_contacts,
            "globalContactsSwissUt": global_contacts,
            "globalContactsUtcDisplay": global_contacts,
            "astronomyContract": MODERN_ASTRONOMY_CONTRACT,
            "ephemeris": "Swiss Ephemeris",
            "ephemerisVersion": str(getattr(swe, "version", "unknown")),
            "timeScale": "SWISSEPH_UT",
            "displayTimeScale": "UTC",
            "displayTimezone": "UTC",
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
            {
                "kind": "TIME",
                "identityTimeScale": "SWISSEPH_UT",
                "displayTimeScale": "UTC",
                "displayTimezone": "UTC",
                "timezoneRole": "DISPLAY_ONLY",
            },
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


def _s1a_source_status(project_root: Path) -> dict[str, Any]:
    fixtures = _s1a_fixtures(project_root)
    return {
        "varahamihiraFrame": {
            "partitionStatus": fixtures["frame"]["sourceAuthority"],
            "absoluteFrameStatus": "SOURCE_RECONSTRUCTION_CANDIDATE | NULL",
            "availableAbsoluteFrameProfiles": [VARAHAMIHIRA_CHITRA_FRAME_ID],
            "defaultAuthorized": False,
        },
        "varahamihiraLunarMonth": {
            "baseSystem": fixtures["lunarMonth"]["baseSystem"],
            "evidenceStatus": fixtures["lunarMonth"]["sourceStatus"],
            "result": "MONTH | UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED",
        },
        "varahamihiraAspect": {
            "geometryStatus": fixtures["aspect"]["sourceStatus"],
            "maximumGeometryRole": fixtures["aspect"]["maximumGeometryRole"],
            "sourcePhaseActivationStatus": fixtures["aspect"]["sourcePhaseActivationStatus"],
            "effectMagnitudeMultiplier": None,
            "jupiterMitigationCoefficient": None,
        },
        "varahamihiraFirmament": {
            "status": fixtures["firmament"]["sourceStatus"],
            "classicalSection": "UNKNOWN",
            "sourceCertifiedClassifier": False,
        },
    }


def build_cgvo_s1b_source_audit(project_root: Path) -> dict[str, Any]:
    """Compile an inspectable, non-selectable modern-coordinate audit ledger."""
    fixtures = _s1b_fixtures(project_root)
    absolute = fixtures["absoluteFrameAudit"]
    epochs: list[dict[str, Any]] = []
    candidate_profiles = absolute["candidateProfiles"]
    for value in absolute["epochsUtc"]:
        at_utc = _parse_utc(value, "epochsUtc")
        profile_records: list[dict[str, Any]] = []
        for candidate in candidate_profiles:
            profile_id = candidate["profileId"]
            record: dict[str, Any] = {
                "profileId": profile_id,
                "sourceConfidence": candidate["sourceConfidence"],
                "reconstructionConfidence": candidate["reconstructionConfidence"],
                "calculationStatus": "SOURCE_TABLE_NOT_TRANSFORMED" if profile_id not in _CHITRA_AUDIT_FLAGS else "MODERN_AUDIT_CALCULATED",
                "requestedFlags": _CHITRA_AUDIT_FLAGS.get(profile_id),
                "returnedFlags": None,
                "spicaTropicalLongitudeDeg": None,
                "derivedZeroMeshaDeg": None,
                "sourceTablePolarLongitudeDeg": candidate.get("sourceTableValue", {}).get("polarLongitudeDeg"),
                "rawHistoricalChitraMaghaDifferenceArcMinutes": None,
            }
            if profile_id in _CHITRA_AUDIT_FLAGS:
                longitude, offset, returned_flags = _chitra_audit_offset(at_utc, profile_id)
                record["spicaTropicalLongitudeDeg"] = _finite(longitude, 8)
                record["derivedZeroMeshaDeg"] = _finite(offset, 8)
                record["returnedFlags"] = returned_flags
            profile_records.append(record)
        epochs.append({"atUtc": _iso(at_utc), "profiles": profile_records, "role": "MODERN_FRAME_AUDIT_ONLY"})
    return {
        "contract": absolute["contract"],
        "currentActiveCandidate": absolute["currentActiveCandidate"],
        "candidates": candidate_profiles,
        "epochs": epochs,
        "maghaComparison": {
            "status": "SOURCE_TABLE_ACQUIRED_MODERN_TRANSFORMATION_UNRESOLVED",
            "sourceLedgerId": fixtures["panchasiddhantikaFixedStarLedger"]["contract"],
            "maghaPolarLongitudeDeg": 126.0,
            "chitraMinusMaghaPolarLongitudeArcMinutes": 3290,
            "reason": "SOURCE_TABLE_HAS_NO_CLOSED_TRANSFORMATION_TO_CURRENT_ECLIPTIC_COORDINATES",
            "crossAnchorAverageAllowed": False,
        },
        "guardrails": absolute["guardrails"],
    }


def _s1b_source_status(project_root: Path) -> dict[str, Any]:
    fixtures = _s1b_fixtures(project_root)
    absolute = fixtures["absoluteFrameAudit"]
    return {
        "absoluteFrameAudit": {
            "contract": absolute["contract"],
            "currentActiveCandidate": absolute["currentActiveCandidate"]["profileId"],
            "availableAuditProfiles": [candidate["profileId"] for candidate in absolute["candidateProfiles"]],
            "auditProfilesRuntimeSelectable": False,
            "maghaComparisonStatus": "SOURCE_TABLE_ACQUIRED_MODERN_TRANSFORMATION_UNRESOLVED",
            "crossAnchorAverageAllowed": False,
        },
        "solarPhaseMapping": {
            "contract": fixtures["solarPhaseMapping"]["contract"],
            "status": fixtures["solarPhaseMapping"]["phaseActivation"]["status"],
            "modernCandidateLabels": fixtures["solarPhaseMapping"]["modernCandidateLabels"],
        },
        "lunarPhaseMapping": {
            "contract": fixtures["lunarPhaseMapping"]["contract"],
            "status": fixtures["lunarPhaseMapping"]["phaseActivation"]["status"],
            "modernCandidateLabels": fixtures["lunarPhaseMapping"]["modernCandidateLabels"],
        },
        "firmamentAdjudication": {
            "contract": fixtures["firmamentAdjudication"]["contract"],
            "status": fixtures["firmamentAdjudication"]["adjudication"]["status"],
            "classicalSection": fixtures["firmamentAdjudication"]["adjudication"]["classicalSection"],
            "sourceCertifiedClassifier": fixtures["firmamentAdjudication"]["adjudication"]["sourceCertifiedClassifier"],
        },
        "readiness": fixtures["readiness"],
    }


def build_cgvo_status(project_root: Path) -> dict[str, Any]:
    return {
        "contract": CGVO_CONTRACT,
        "schemaVersion": 6,
        "milestone": "CGVO-G2-R1",
        "milestones": {
            "current": "CGVO-G2-R1",
            "astronomy": "CGVO-S1B-R1",
            "geography": "CGVO-G2-R1",
        },
        "status": "READY_FOR_CENTRAL_REVIEW_WITH_SOURCE_GAPS",
        "availableProfiles": ["MODERN_ASTRONOMY_VISIBILITY_V1", VARAHAMIHIRA_PROFILE_ID, TRAILOKYA_PROFILE_ID, VARAHAMIHIRA_CHITRA_FRAME_ID],
        "availableEventTypes": ["SOLAR", "LUNAR"],
        "guardrails": _guardrails(),
        "sourceProfiles": {
            "varahamihira": "SOURCE_ARCHITECTURE_AVAILABLE_READ_ONLY",
            "trailokya": _source_profile(project_root, TRAILOKYA_FIXTURE)["sourceStatus"],
        },
        "sourceAdapters": _s1a_source_status(project_root),
        "s1bSourceAudit": _s1b_source_status(project_root),
    }


def build_cgvo_source_profiles(project_root: Path) -> dict[str, Any]:
    varahamihira = _source_profile(project_root, VARAHAMIHIRA_FIXTURE)
    trailokya = _source_profile(project_root, TRAILOKYA_FIXTURE)
    return {
        "contract": "CGVO_SOURCE_PROFILE_BUNDLE_V1",
        "profiles": [varahamihira, trailokya],
        "sourceAdapters": _s1a_source_status(project_root),
        "guardrails": _guardrails(),
        "crossSourceComposition": "NOT_AUTHORIZED",
    }


def build_cgvo_kurma_seed(project_root: Path) -> dict[str, Any]:
    return _load_json(project_root, KURMA_FIXTURE)


def _region_key(value: str) -> str:
    """Make a deterministic lookup key without changing the source literal."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return "".join(character for character in normalized.upper() if character.isalnum())


def _validate_gazetteer_overlay(overlay: Mapping[str, Any]) -> None:
    allowed_entity_types = set(overlay.get("allowedCandidateEntityTypes", []))
    allowed_statuses = set(overlay.get("allowedMappingStatuses", []))
    candidates = overlay.get("candidateOverlays")
    if not isinstance(candidates, dict) or not allowed_entity_types or not allowed_statuses:
        raise RuntimeError("CGVO G1 gazetteer overlay has no controlled candidate contract")
    for key, record in candidates.items():
        if not isinstance(key, str) or not isinstance(record, dict):
            raise RuntimeError("CGVO G1 gazetteer overlay has an invalid candidate record")
        if record.get("candidateEntityType") not in allowed_entity_types:
            raise RuntimeError(f"CGVO G1 gazetteer candidate {key} has an invalid candidate entity type")
        if record.get("mappingStatus") not in allowed_statuses:
            raise RuntimeError(f"CGVO G1 gazetteer candidate {key} has an invalid mapping status")
        mappings = record.get("candidateMappings", [])
        if record["mappingStatus"] in {"HIGH_CONFIDENCE_CANDIDATE", "MEDIUM_CONFIDENCE_CANDIDATE", "LOW_CONFIDENCE_CANDIDATE", "CONTESTED_CANDIDATES"} and not mappings:
            raise RuntimeError(f"CGVO G1 gazetteer candidate {key} lacks mapping evidence")
        if record["mappingStatus"] == "CONTESTED_CANDIDATES" and len(mappings) < 2:
            raise RuntimeError(f"CGVO G1 gazetteer candidate {key} must preserve competing candidates")
        for mapping in mappings:
            if not mapping.get("temporalApplicability") or not mapping.get("evidenceItems"):
                raise RuntimeError(f"CGVO G1 gazetteer candidate {key} lacks temporal or evidence provenance")
            if mapping.get("geometryStatus") == "EVIDENCE_BACKED":
                raise RuntimeError("CGVO G1 does not authorize downstream geometry")
            if mapping.get("geometryType") == "POLYGON" or mapping.get("geometry") is not None:
                raise RuntimeError("CGVO G1 does not store active modern polygons")


def build_cgvo_historical_gazetteer(project_root: Path) -> dict[str, Any]:
    """Compile Chapter XIV raw names into read-only evidence records.

    The input seed remains the sole raw-name source.  G1 overlays only attach
    reviewed candidate evidence and never create an automatic modern region.
    """
    seed = build_cgvo_kurma_seed(project_root)
    overlay = _load_json(project_root, KURMA_G1_GAZETTEER_FIXTURE)
    layers = _load_json(project_root, GEOGRAPHY_SOURCE_LAYERS_FIXTURE)
    _validate_gazetteer_overlay(overlay)
    candidate_overlays = overlay["candidateOverlays"]
    default_forbidden = list(overlay["defaultForbiddenUses"])
    records: list[dict[str, Any]] = []
    direction_counts: dict[str, int] = {}
    for group in seed.get("groups", []):
        direction = str(group["direction"])
        direction_counts[direction] = 0
        for ordinal, literal in enumerate(group.get("historicalNames", []), start=1):
            key = _region_key(str(literal))
            candidate = candidate_overlays.get(key, {})
            mapping_status = candidate.get("mappingStatus", "SOURCE_NAME_ONLY")
            direction_counts[direction] += 1
            records.append({
                "regionId": f"VARAHA_XIV_{direction}_{key}_{ordinal:02d}",
                "sourceProfileId": overlay["sourceProfileId"],
                "sourceWork": overlay["sourceWork"],
                "sourceLocator": f"Brihat Samhita {group['sourceVerses']}",
                "sourceNameOriginal": None,
                "sourceNameTransliteration": literal,
                "sourceLiteralStatus": "ROOT_SOURCE_NAME",
                "normalizedName": key,
                "variantSpellings": candidate.get("variantSpellings", []),
                "sourceDirectionGroup": direction,
                "nakshatraTriad": group["nakshatras"],
                "sourceContext": "KURMAVIBHAGA_DIRECTIONAL_NAME_LIST",
                "geometry": None,
                "rawSourceCategory": "UNKNOWN",
                "rawSourceCategoryStatus": "NOT_CLASSIFIED_FROM_ROOT_SOURCE",
                "candidateEntityType": candidate.get("candidateEntityType", "UNKNOWN"),
                "candidateEntityTypeStatus": "RESEARCH_OVERLAY" if candidate else "NOT_ASSIGNED",
                "mappingStatus": mapping_status,
                "candidateMappings": candidate.get("candidateMappings", []),
                "unresolvedFlags": ["NOT_MODERN_GEOMETRY_AUTHORIZED", "MARKET_USE_PROHIBITED"],
                "prohibitedUses": default_forbidden,
            })
    summary = {
        "totalSourceNames": len(records),
        "sourceNameOnly": sum(record["mappingStatus"] == "SOURCE_NAME_ONLY" for record in records),
        "mappedHighConfidence": sum(record["mappingStatus"] == "HIGH_CONFIDENCE_CANDIDATE" for record in records),
        "mappedMediumConfidence": sum(record["mappingStatus"] == "MEDIUM_CONFIDENCE_CANDIDATE" for record in records),
        "contested": sum(record["mappingStatus"] == "CONTESTED_CANDIDATES" for record in records),
        "approximateRegionOnly": sum(record["mappingStatus"] == "APPROXIMATE_REGION_ONLY" for record in records),
        "unmapped": sum(record["mappingStatus"] == "UNMAPPED" for record in records),
        "byDirection": direction_counts,
    }
    return {
        "contract": overlay["contract"],
        "schemaVersion": overlay["schemaVersion"],
        "milestone": overlay["milestone"],
        "startingMaster": overlay["startingMaster"],
        "sourceProfiles": layers["sourceProfiles"],
        "records": records,
        "summary": summary,
        "guardrails": layers["guardrails"],
        "aggregationPolicy": layers["aggregationPolicy"],
    }


def _validate_g2_research_footprints(
    policy: Mapping[str, Any],
    ledger: Mapping[str, Any],
    gazetteer: Mapping[str, Any],
    site_evidence: Mapping[str, Any],
) -> None:
    if ledger.get("sourceGazetteerBaseline") != "CGVO-G1-R1":
        raise RuntimeError("CGVO G2 footprint ledger must declare the accepted G1-R1 baseline")
    if policy.get("geometryRole") != "RESEARCH_GEOMETRY_ONLY" or ledger.get("geometryRole") != "RESEARCH_GEOMETRY_ONLY":
        raise RuntimeError("CGVO G2 research geometry must remain research-only")
    locked_paths = (
        "downstreamIntersectionAuthorized", "eclipseVisibilityMatching", "priceDataRead", "priceOutcomeRead",
        "marketDirectionInferred", "scoreAggregationUsed", "fieldsPath", "sbcPath", "autoSuggestPath",
        "mlPath", "mt5Path", "marketUseAllowed", "executionAllowed",
    )
    if any(policy["guardrails"].get(key) for key in locked_paths):
        raise RuntimeError("CGVO G2 geometry policy has an active downstream guardrail")
    if any(ledger["guardrails"].get(key) for key in locked_paths):
        raise RuntimeError("CGVO G2 footprint ledger has an active downstream guardrail")

    base_records = list(gazetteer["records"])
    mapping_index: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for record in base_records:
        if record.get("geometry") is not None:
            raise RuntimeError("CGVO G1 base records must remain geometry-null")
        for candidate in record["candidateMappings"]:
            if candidate.get("geometry") is not None:
                raise RuntimeError("CGVO G1 candidate overlays must remain geometry-null")
            candidate_id = candidate.get("candidateId")
            if candidate_id in mapping_index:
                raise RuntimeError(f"CGVO G1 candidate ID is not unique: {candidate_id}")
            mapping_index[candidate_id] = (record, candidate)

    if site_evidence.get("sourceGazetteerBaseline") != "CGVO-G1-R1":
        raise RuntimeError("CGVO G2-R1 site evidence must declare the accepted G1-R1 baseline")
    if site_evidence.get("geometryRole") != "RESEARCH_GEOMETRY_ONLY":
        raise RuntimeError("CGVO G2-R1 site evidence must remain research-only")
    if any(site_evidence.get("guardrails", {}).get(key) for key in locked_paths):
        raise RuntimeError("CGVO G2-R1 site evidence has an active downstream guardrail")

    target_site_names = {"MATHURAKA_MATHURA", "RAJAGRIHA_RAJGIR", "PATALIPUTRA", "TAKSASILA_TAXILA", "PUSKALAVATI_CHARSADDA"}
    site_evidence_index: dict[str, Mapping[str, Any]] = {}
    for evidence in site_evidence.get("siteEvidence", []):
        evidence_id = evidence.get("siteEvidenceId")
        if not isinstance(evidence_id, str) or evidence_id in site_evidence_index:
            raise RuntimeError("CGVO G2-R1 site evidence IDs must be unique")
        site_evidence_index[evidence_id] = evidence
        if evidence.get("siteKey") not in target_site_names:
            raise RuntimeError("CGVO G2-R1 site evidence is outside the authorized target list")
        if not isinstance(evidence.get("historicalIdentityEvidence"), list) or not evidence["historicalIdentityEvidence"]:
            raise RuntimeError(f"CGVO G2-R1 site evidence lacks historical identity evidence: {evidence_id}")
        if not isinstance(evidence.get("coordinateEvidence"), list) or not evidence["coordinateEvidence"]:
            raise RuntimeError(f"CGVO G2-R1 site evidence lacks coordinate evidence: {evidence_id}")
        if not evidence.get("uncertainty") or not evidence.get("temporalApplicability") or not evidence.get("limitations"):
            raise RuntimeError(f"CGVO G2-R1 site evidence lacks uncertainty, temporal validity, or limitations: {evidence_id}")
        if evidence.get("researchAnchorEligible"):
            coordinate = evidence.get("normalizedCoordinate")
            if not isinstance(coordinate, Mapping):
                raise RuntimeError(f"CGVO G2-R1 eligible site lacks normalized coordinate: {evidence_id}")
            _validate_g2_point_coordinate(coordinate, evidence_id)
        elif evidence.get("normalizedCoordinate") is not None and evidence.get("coordinateStatus") == "COORDINATE_SOURCE_CLOSED":
            raise RuntimeError(f"CGVO G2-R1 closed coordinate must be anchor-eligible: {evidence_id}")

    seen_footprint_ids: set[str] = set()
    seen_candidate_ids: set[str] = set()
    allowed_statuses = set(policy["geometryStatuses"])
    allowed_primitives = set(policy["geometryPrimitives"])
    for footprint in ledger.get("footprints", []):
        footprint_id = footprint.get("footprintId")
        candidate_id = footprint.get("linkedGazetteerCandidateId")
        if not isinstance(footprint_id, str) or footprint_id in seen_footprint_ids:
            raise RuntimeError("CGVO G2 footprint IDs must be unique")
        if not isinstance(candidate_id, str) or candidate_id in seen_candidate_ids:
            raise RuntimeError("CGVO G2 candidate mappings must not receive duplicate footprints")
        seen_footprint_ids.add(footprint_id)
        seen_candidate_ids.add(candidate_id)
        if candidate_id not in mapping_index:
            raise RuntimeError(f"CGVO G2 footprint references unknown G1 candidate: {candidate_id}")
        record, _candidate = mapping_index[candidate_id]
        if record["mappingStatus"] == "SOURCE_NAME_ONLY":
            raise RuntimeError("CGVO G2 SOURCE_NAME_ONLY records cannot receive footprints")
        if footprint.get("normalizedName") != record["normalizedName"]:
            raise RuntimeError(f"CGVO G2 footprint normalized name mismatch: {footprint_id}")
        if footprint.get("geometryStatus") not in allowed_statuses:
            raise RuntimeError(f"CGVO G2 footprint has invalid geometry status: {footprint_id}")
        if footprint.get("geometryPrimitive") not in allowed_primitives:
            raise RuntimeError(f"CGVO G2 footprint has invalid geometry primitive: {footprint_id}")
        if not footprint.get("uncertainty") or not footprint.get("temporalApplicability") or not footprint.get("limitations"):
            raise RuntimeError(f"CGVO G2 footprint lacks uncertainty, temporal validity, or limitations: {footprint_id}")
        geometry_data = footprint.get("geometryData")
        geometry_status = footprint["geometryStatus"]
        geometry_primitive = footprint["geometryPrimitive"]
        if geometry_status == "GEOMETRY_PENDING_EVIDENCE":
            if geometry_primitive != "NONE" or geometry_data is not None:
                raise RuntimeError(f"CGVO G2 pending footprint must not contain geometry data: {footprint_id}")
        elif geometry_status == "RESEARCH_ANCHOR_POINT":
            if geometry_primitive != "POINT_ANCHOR":
                raise RuntimeError(f"CGVO G2 point anchor must use POINT_ANCHOR: {footprint_id}")
            _validate_g2_point_anchor(footprint, site_evidence_index)
        elif geometry_status == "RESEARCH_MULTI_ANCHOR":
            if geometry_primitive != "MULTI_POINT_ANCHORS":
                raise RuntimeError(f"CGVO G2 multi-anchor must use MULTI_POINT_ANCHORS: {footprint_id}")
            _validate_g2_multi_point_anchors(footprint, site_evidence_index)
        if footprint["geometryStatus"] == "CONTESTED_RESEARCH_GEOMETRIES":
            if not footprint.get("contestedGroupId") or not isinstance(geometry_data, dict) or not geometry_data.get("separateAlternative"):
                raise RuntimeError(f"CGVO G2 contested footprint must remain an explicit separate alternative: {footprint_id}")
            if geometry_data.get("mergedGeometry") is not None:
                raise RuntimeError(f"CGVO G2 contested footprint may not merge alternatives: {footprint_id}")
        if footprint["normalizedName"] == "SINDHU":
            if footprint["geometryPrimitive"] != "RIVER_SYSTEM_CONTEXT" or not isinstance(geometry_data, dict):
                raise RuntimeError("CGVO G2 Sindhu must remain a river-system context")
            if geometry_data.get("landPolygon") is not None or geometry_data.get("adjacentLandExtent") is not None:
                raise RuntimeError("CGVO G2 Sindhu may not imply an adjacent land polygon")
        if geometry_primitive == "NONE" and geometry_data is not None:
            raise RuntimeError(f"CGVO G2 NONE primitive may not carry geometry data: {footprint_id}")


def _validate_g2_point_coordinate(coordinate: Mapping[str, Any], evidence_id: str) -> None:
    required = {
        "latitude", "longitude", "coordinateReferenceSystem", "axisOrder", "sourceCoordinateRaw",
        "coordinatePrecision", "coordinateSourceId", "coordinateSourceLocator", "coordinateSourceType",
        "coordinateInterpretation", "normalizationMethod",
    }
    missing = sorted(key for key in required if coordinate.get(key) in (None, "", []))
    if missing:
        raise RuntimeError(f"CGVO G2-R1 coordinate is missing required evidence fields ({', '.join(missing)}): {evidence_id}")
    latitude = coordinate.get("latitude")
    longitude = coordinate.get("longitude")
    if not isinstance(latitude, (int, float)) or isinstance(latitude, bool) or not math.isfinite(latitude) or not -90 <= latitude <= 90:
        raise RuntimeError(f"CGVO G2-R1 coordinate latitude must be finite and within -90..90: {evidence_id}")
    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool) or not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise RuntimeError(f"CGVO G2-R1 coordinate longitude must be finite and within -180..180: {evidence_id}")
    if coordinate.get("coordinateReferenceSystem") != "WGS84" or coordinate.get("axisOrder") != "LATITUDE_LONGITUDE":
        raise RuntimeError(f"CGVO G2-R1 active coordinate must explicitly declare WGS84 latitude/longitude: {evidence_id}")
    if coordinate.get("normalizationMethod") not in {"DMS_TO_DECIMAL_DEGREES", "SOURCE_DECIMAL_DEGREES_VERBATIM"}:
        raise RuntimeError(f"CGVO G2-R1 coordinate must declare a supported normalization method: {evidence_id}")
    if coordinate.get("coordinatePrecision") == "UNSPECIFIED":
        raise RuntimeError(f"CGVO G2-R1 coordinate precision may not be unspecified: {evidence_id}")


def _validate_g2_point_anchor(footprint: Mapping[str, Any], site_evidence_index: Mapping[str, Mapping[str, Any]]) -> None:
    geometry = footprint.get("geometryData")
    if not isinstance(geometry, Mapping):
        raise RuntimeError(f"CGVO G2 point anchor requires geometry data: {footprint.get('footprintId')}")
    forbidden = {"anchors", "centroid", "midpoint", "polygon", "boundingBox", "envelope", "mergedGeometry"}
    if forbidden.intersection(geometry):
        raise RuntimeError(f"CGVO G2 point anchor may not contain multi-point or regional geometry: {footprint.get('footprintId')}")
    if geometry.get("anchorRole") not in {"HISTORICAL_SITE_REFERENCE_ONLY", "ASSOCIATED_HISTORICAL_SITE_REFERENCE"}:
        raise RuntimeError(f"CGVO G2 point anchor must declare a limited historical site role: {footprint.get('footprintId')}")
    if geometry.get("regionRepresentationAllowed") is not False:
        raise RuntimeError(f"CGVO G2 point anchor may not represent a historical region: {footprint.get('footprintId')}")
    site_evidence_id = geometry.get("siteEvidenceId")
    evidence = site_evidence_index.get(site_evidence_id)
    if evidence is None or not evidence.get("researchAnchorEligible"):
        raise RuntimeError(f"CGVO G2 point anchor needs an eligible site evidence record: {footprint.get('footprintId')}")
    _validate_g2_point_coordinate(geometry, str(site_evidence_id))
    if footprint.get("candidateCoverageStatus") not in {"FULL_SITE_IDENTITY_ONLY", "PARTIAL_HISTORICAL_CONTEXT"}:
        raise RuntimeError(f"CGVO G2 point anchor must state candidate coverage honestly: {footprint.get('footprintId')}")
    if not footprint.get("siteIdentityEvidence") or not footprint.get("coordinateEvidence"):
        raise RuntimeError(f"CGVO G2 point anchor requires separate identity and coordinate evidence: {footprint.get('footprintId')}")


def _validate_g2_multi_point_anchors(footprint: Mapping[str, Any], site_evidence_index: Mapping[str, Mapping[str, Any]]) -> None:
    geometry = footprint.get("geometryData")
    if not isinstance(geometry, Mapping) or not isinstance(geometry.get("anchors"), list) or len(geometry["anchors"]) < 2:
        raise RuntimeError(f"CGVO G2 multi-anchor requires at least two independently evidenced anchors: {footprint.get('footprintId')}")
    if any(key in geometry for key in ("centroid", "midpoint", "polygon", "boundingBox", "envelope", "mergedGeometry")):
        raise RuntimeError(f"CGVO G2 multi-anchor may not contain merged regional geometry: {footprint.get('footprintId')}")
    for anchor in geometry["anchors"]:
        _validate_g2_point_anchor({
            "footprintId": footprint.get("footprintId"),
            "geometryData": anchor,
            "candidateCoverageStatus": "PARTIAL_HISTORICAL_CONTEXT",
            "siteIdentityEvidence": anchor.get("siteIdentityEvidence"),
            "coordinateEvidence": anchor.get("coordinateEvidence"),
        }, site_evidence_index)
    if footprint.get("candidateCoverageStatus") != "MULTI_CENTRE_CONTEXT":
        raise RuntimeError(f"CGVO G2 multi-anchor must state multi-centre context: {footprint.get('footprintId')}")


def build_cgvo_historical_research_footprints(project_root: Path) -> dict[str, Any]:
    """Compile G2's separate, non-downstream historical-footprint ledger."""
    policy = _load_json(project_root, GEOGRAPHY_G2_POLICY_FIXTURE)
    ledger = _load_json(project_root, KURMA_G2_FOOTPRINTS_FIXTURE)
    site_evidence = _load_json(project_root, CGVO_G2_R1_SITE_EVIDENCE_FIXTURE)
    readiness = _load_json(project_root, CGVO_G2_READINESS_FIXTURE)
    gazetteer = build_cgvo_historical_gazetteer(project_root)
    _validate_g2_research_footprints(policy, ledger, gazetteer, site_evidence)

    base_by_candidate: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for record in gazetteer["records"]:
        for candidate in record["candidateMappings"]:
            base_by_candidate[candidate["candidateId"]] = (record, candidate)

    footprints: list[dict[str, Any]] = []
    for fixture in ledger["footprints"]:
        record, candidate = base_by_candidate[fixture["linkedGazetteerCandidateId"]]
        source_occurrences = [
            source["regionId"] for source in gazetteer["records"]
            if source["normalizedName"] == fixture["normalizedName"]
        ]
        footprints.append({
            **fixture,
            "geometryRole": policy["geometryRole"],
            "sourceOccurrenceIds": source_occurrences,
            "sourceMappingStatus": record["mappingStatus"],
            "candidateEntityType": record["candidateEntityType"],
            "evidenceItems": candidate["evidenceItems"],
            "downstreamIntersectionAuthorized": False,
            "marketUseAllowed": False,
            "executionAllowed": False,
        })

    status_counts: dict[str, int] = {}
    primitive_counts: dict[str, int] = {}
    for footprint in footprints:
        status_counts[footprint["geometryStatus"]] = status_counts.get(footprint["geometryStatus"], 0) + 1
        primitive_counts[footprint["geometryPrimitive"]] = primitive_counts.get(footprint["geometryPrimitive"], 0) + 1
    return {
        "contract": ledger["contract"],
        "schemaVersion": ledger["schemaVersion"],
        "milestone": ledger["milestone"],
        "sourceGazetteerBaseline": ledger["sourceGazetteerBaseline"],
        "geometryRole": policy["geometryRole"],
        "policy": policy,
        "siteEvidence": site_evidence,
        "readiness": readiness,
        "footprints": footprints,
        "summary": {
            "footprintCount": len(footprints),
            "reviewedCandidateTermCount": len({footprint["normalizedName"] for footprint in footprints}),
            "coordinateBearingFootprintCount": sum(
                footprint["geometryPrimitive"] in {"POINT_ANCHOR", "MULTI_POINT_ANCHORS"}
                for footprint in footprints
            ),
            "byGeometryStatus": status_counts,
            "byGeometryPrimitive": primitive_counts,
        },
        "guardrails": {
            **policy["guardrails"],
            "researchGeometryOnly": True,
        },
    }


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
    identity_value = payload.get("globalMaxSwissUt") or payload.get("globalMaxUtc")
    identity_field = "globalMaxSwissUt" if payload.get("globalMaxSwissUt") else "globalMaxUtc"
    global_max = _parse_utc(identity_value, identity_field)
    locality = _validate_locality(payload)
    # Reconstruct both the flags and the event time from Swiss Ephemeris.  A
    # frontend-supplied global flag is never trusted as an event identity.
    flags, times = _next_global_event(event_type, global_max - timedelta(minutes=1))
    resolved_max = _from_jd(times[0])
    if resolved_max is None or abs((resolved_max - global_max).total_seconds()) > 3600:
        raise CgvoRequestError("globalMaxUtc does not resolve to the requested eclipse identity")
    event = _build_event(project_root, event_type, int(flags), times, locality)
    if event["astronomyEventIdentity"]["globalMaxUtc"] != _iso(global_max):
        raise CgvoRequestError("globalMaxUtc does not match the immutable Swiss Ephemeris event identity")
    requested_causal_id = str(payload.get("causalEventId") or "").strip()
    if requested_causal_id and requested_causal_id != event["causalEventId"]:
        raise CgvoRequestError("causalEventId does not match the reconstructed Swiss Ephemeris event")
    with _EPHEMERIS_LOCK:
        _attach_s1a_source_adapters(project_root, event, payload)
    return {
        "contract": "CGVO_LOCAL_CIRCUMSTANCES_V1",
        "event": event,
        "sourceProfiles": build_cgvo_source_profiles(project_root)["profiles"],
        "kurma": build_cgvo_kurma_seed(project_root),
        "guardrails": _guardrails(),
    }


def build_cgvo_workbench(project_root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    event_type = str(payload.get("eventType") or "SOLAR").upper()
    if payload.get("globalMaxSwissUt") or payload.get("globalMaxUtc"):
        local_payload = dict(payload)
        local_payload["eventType"] = event_type
        local = build_cgvo_local_circumstances(project_root, local_payload)
        event = local["event"]
    else:
        start = _parse_utc(payload.get("startUtc") or "2027-01-01T00:00:00Z", "startUtc")
        end = _parse_utc(payload.get("endUtc") or "2028-01-01T00:00:00Z", "endUtc")
        search = build_cgvo_event_search(project_root, {"startUtc": _iso(start), "endUtc": _iso(end), "eventType": event_type, "limit": 12})
        event = search["events"][0] if search["events"] else None
        requested_causal_id = str(payload.get("causalEventId") or "").strip()
        if requested_causal_id and (event is None or requested_causal_id != event["causalEventId"]):
            raise CgvoRequestError("causalEventId does not match the reconstructed Swiss Ephemeris event")
        if event is not None:
            with _EPHEMERIS_LOCK:
                _attach_s1a_source_adapters(project_root, event, payload)
    return {
        "contract": CGVO_CONTRACT,
        "schemaVersion": 2,
        "event": event,
        "sourceProfiles": build_cgvo_source_profiles(project_root)["profiles"],
        "sourceAdapters": _s1a_source_status(project_root),
        "kurma": build_cgvo_kurma_seed(project_root),
        "guardrails": _guardrails(),
    }
