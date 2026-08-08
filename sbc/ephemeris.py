from __future__ import annotations

import hashlib
import threading
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import swisseph as swe

from financial_astro_ephemeris import configure_ephemeris

from .enums import Ayanamsha, Center, EphemerisFallbackPolicy, NodeType, SUPPORTED_BODIES, ZodiacMode
from .models import AstroSettings, EphemerisEvidence, GeoLocation, PlanetPosition


_EPHEMERIS_LOCK = threading.RLock()

_BODY_IDS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
    "URANUS": swe.URANUS,
    "NEPTUNE": swe.NEPTUNE,
    "PLUTO": swe.PLUTO,
}

_AYANAMSHA_IDS = {
    Ayanamsha.RAMAN: swe.SIDM_RAMAN,
    Ayanamsha.LAHIRI: swe.SIDM_LAHIRI,
}


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("SBC timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _julian_ut(value: datetime) -> float:
    at_utc = _aware_utc(value)
    _, jd_ut = swe.utc_to_jd(
        at_utc.year,
        at_utc.month,
        at_utc.day,
        at_utc.hour,
        at_utc.minute,
        at_utc.second + at_utc.microsecond / 1_000_000.0,
        swe.GREG_CAL,
    )
    return float(jd_ut)


def _datetime_from_jd_ut(jd_ut: float) -> datetime:
    year, month, day, hour, minute, second = swe.jdut1_to_utc(float(jd_ut), swe.GREG_CAL)
    whole_second = int(second)
    microsecond = int(round((float(second) - whole_second) * 1_000_000.0))
    if microsecond >= 1_000_000:
        whole_second += 1
        microsecond -= 1_000_000
    return datetime(year, month, day, hour, minute, whole_second, microsecond, tzinfo=timezone.utc)


@lru_cache(maxsize=16)
def _sha256_file(path_text: str) -> str:
    digest = hashlib.sha256()
    with Path(path_text).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _calculation_mode(returned_flags: int) -> str:
    if returned_flags & swe.FLG_SWIEPH:
        return "SWISSEPH"
    if returned_flags & swe.FLG_MOSEPH:
        return "MOSHIER_FALLBACK"
    if returned_flags & swe.FLG_JPLEPH:
        return "JPL"
    return "UNKNOWN"


def _library_version() -> str:
    value = getattr(swe, "__version__", None) or getattr(swe, "version", None)
    return str(value or "unknown")


class SwissEphemerisProvider:
    """Audit-friendly Swiss Ephemeris adapter for SBC research facts.

    Swiss Ephemeris mode and topocentric location are process-global. A lock is
    therefore required so concurrent profile calculations cannot leak settings.
    """

    provider_id = "PYSWISSEPH_AUDITED_V1"

    def __init__(self, ephemeris_path: Path | None = None) -> None:
        self.ephemeris_path = ephemeris_path
        self.configured_path = ""

    def _configure(self, settings: AstroSettings, location: GeoLocation) -> None:
        self.configured_path = configure_ephemeris(self.ephemeris_path)
        if settings.zodiac is ZodiacMode.SIDEREAL:
            swe.set_sid_mode(_AYANAMSHA_IDS[settings.ayanamsha])
        if settings.center is Center.TOPOCENTRIC:
            swe.set_topo(float(location.longitude), float(location.latitude), float(location.altitude_m))

    @staticmethod
    def _node_id(settings: AstroSettings) -> int:
        return swe.TRUE_NODE if settings.node is NodeType.TRUE_NODE else swe.MEAN_NODE

    @staticmethod
    def _flags(settings: AstroSettings) -> int:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        if settings.zodiac is ZodiacMode.SIDEREAL:
            flags |= swe.FLG_SIDEREAL
        if settings.center is Center.TOPOCENTRIC:
            flags |= swe.FLG_TOPOCTR
        return flags

    def _evidence(self, body: str, requested_flags: int, returned_flags: int) -> EphemerisEvidence:
        file_number = 1 if body == "MOON" else 0
        data_file: str | None = None
        digest: str | None = None
        start_jd: float | None = None
        end_jd: float | None = None
        denum: int | None = None
        try:
            path_text, start_jd_raw, end_jd_raw, denum_raw = swe.get_current_file_data(file_number)
            candidate = Path(str(path_text)) if path_text else None
            if candidate is not None and candidate.is_file():
                data_file = str(candidate.resolve())
                digest = _sha256_file(data_file)
                start_jd = float(start_jd_raw)
                end_jd = float(end_jd_raw)
                denum = int(denum_raw)
        except (OSError, TypeError, ValueError):
            pass
        return EphemerisEvidence(
            provider=self.provider_id,
            library_version=_library_version(),
            configured_path=self.configured_path,
            calculation_mode=_calculation_mode(returned_flags),
            requested_flags=int(requested_flags),
            returned_flags=int(returned_flags),
            data_file=data_file,
            data_file_sha256=digest,
            data_file_start_jd=start_jd,
            data_file_end_jd=end_jd,
            data_file_denum=denum,
        )

    def _position(
        self,
        body: str,
        at_utc: datetime,
        settings: AstroSettings,
        requested_flags: int,
    ) -> PlanetPosition:
        body_id = self._node_id(settings) if body == "RAHU" else _BODY_IDS[body]
        values, returned_flags = swe.calc_ut(_julian_ut(at_utc), body_id, requested_flags)
        mode = _calculation_mode(int(returned_flags))
        if settings.fallback_policy is EphemerisFallbackPolicy.ERROR_IF_NOT_SWISSEPH and mode != "SWISSEPH":
            raise RuntimeError(f"{body} calculation used {mode}; profile requires Swiss Ephemeris data files")
        return PlanetPosition(
            body=body,
            timestamp_utc=at_utc,
            longitude_deg=float(values[0]) % 360.0,
            latitude_deg=float(values[1]),
            distance_au=float(values[2]),
            longitude_speed_deg_per_day=float(values[3]),
            zodiac=settings.zodiac,
            ayanamsha=settings.ayanamsha if settings.zodiac is ZodiacMode.SIDEREAL else None,
            center=settings.center,
            node=settings.node,
            evidence=self._evidence(body, requested_flags, int(returned_flags)),
        )

    @staticmethod
    def _ketu_from_rahu(rahu: PlanetPosition) -> PlanetPosition:
        return PlanetPosition(
            body="KETU",
            timestamp_utc=rahu.timestamp_utc,
            longitude_deg=(rahu.longitude_deg + 180.0) % 360.0,
            latitude_deg=-rahu.latitude_deg,
            distance_au=rahu.distance_au,
            longitude_speed_deg_per_day=rahu.longitude_speed_deg_per_day,
            zodiac=rahu.zodiac,
            ayanamsha=rahu.ayanamsha,
            center=rahu.center,
            node=rahu.node,
            evidence=rahu.evidence,
            derived_from="RAHU_PLUS_180_DEG",
        )

    def positions(
        self,
        at_utc: datetime,
        bodies: tuple[str, ...],
        settings: AstroSettings,
        location: GeoLocation,
    ) -> tuple[PlanetPosition, ...]:
        timestamp = _aware_utc(at_utc)
        normalized = tuple(str(body).strip().upper() for body in bodies)
        if not normalized:
            raise ValueError("at least one body is required")
        if len(set(normalized)) != len(normalized):
            raise ValueError("body list contains duplicates")
        unknown = sorted(set(normalized) - set(SUPPORTED_BODIES))
        if unknown:
            raise ValueError(f"unsupported bodies: {', '.join(unknown)}")

        with _EPHEMERIS_LOCK:
            self._configure(settings, location)
            requested_flags = self._flags(settings)
            rahu: PlanetPosition | None = None
            calculated: dict[str, PlanetPosition] = {}
            for body in normalized:
                if body == "KETU":
                    if rahu is None:
                        rahu = self._position("RAHU", timestamp, settings, requested_flags)
                    calculated[body] = self._ketu_from_rahu(rahu)
                    continue
                calculated[body] = self._position(body, timestamp, settings, requested_flags)
                if body == "RAHU":
                    rahu = calculated[body]
            return tuple(calculated[body] for body in normalized)

    def sunrise_for_local_date(
        self,
        local_date: date,
        location: GeoLocation,
        settings: AstroSettings,
    ) -> datetime:
        zone = ZoneInfo(location.timezone)
        local_midnight = datetime.combine(local_date, time.min, tzinfo=zone)
        with _EPHEMERIS_LOCK:
            self._configure(settings, location)
            result, times = swe.rise_trans(
                _julian_ut(local_midnight.astimezone(timezone.utc)),
                swe.SUN,
                swe.CALC_RISE,
                (float(location.longitude), float(location.latitude), float(location.altitude_m)),
                0.0,
                0.0,
                swe.FLG_SWIEPH,
            )
        if int(result) != 0:
            raise RuntimeError(f"sunrise unavailable for {local_date.isoformat()} at {location}: code {result}")
        return _datetime_from_jd_ut(float(times[0]))

    def sunset_for_local_date(
        self,
        local_date: date,
        location: GeoLocation,
        settings: AstroSettings,
    ) -> datetime:
        """Return the local civil date's sunset for read-only calendar timing.

        This is an astronomy utility only.  Source profiles decide whether a
        product is permitted to attach any classical interpretation to it.
        """
        zone = ZoneInfo(location.timezone)
        local_midnight = datetime.combine(local_date, time.min, tzinfo=zone)
        with _EPHEMERIS_LOCK:
            self._configure(settings, location)
            result, times = swe.rise_trans(
                _julian_ut(local_midnight.astimezone(timezone.utc)),
                swe.SUN,
                swe.CALC_SET,
                (float(location.longitude), float(location.latitude), float(location.altitude_m)),
                0.0,
                0.0,
                swe.FLG_SWIEPH,
            )
        if int(result) != 0:
            raise RuntimeError(f"sunset unavailable for {local_date.isoformat()} at {location}: code {result}")
        return _datetime_from_jd_ut(float(times[0]))

    def sunrise_at_or_before(
        self,
        at_utc: datetime,
        location: GeoLocation,
        settings: AstroSettings,
    ) -> datetime:
        timestamp = _aware_utc(at_utc)
        zone = ZoneInfo(location.timezone)
        local_date = timestamp.astimezone(zone).date()
        sunrise = self.sunrise_for_local_date(local_date, location, settings)
        if timestamp < sunrise:
            sunrise = self.sunrise_for_local_date(local_date - timedelta(days=1), location, settings)
        return sunrise
