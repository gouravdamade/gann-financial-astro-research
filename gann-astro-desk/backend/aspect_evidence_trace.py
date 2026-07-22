from __future__ import annotations

"""Timestamp-safe, research-only evidence traces for individual aspect windows.

The trace is intentionally an observation record, not a prediction engine.  It
keeps three distinct evidence domains apart:

* ``start`` and ``window`` records contain only information available at their
  own timestamps;
* ``end`` is still an in-window timestamp, not a result label; and
* ``outcome`` is explicitly retrospective and never appears on a live record.

This makes the same trace useful for manual review, later ML feature export,
and audit of any future decision policy without leaking a known result into the
historical state seen by the analyst.
"""

import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import swisseph as swe


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from candlestick_analysis import build_candlestick_bar_records  # noqa: E402
from financial_astro_ephemeris import (  # noqa: E402
    configure_ephemeris,
    fetch_planetary_longitude,
    sidereal_house_cusps,
)
from rsi_analysis import wilder_rsi_values  # noqa: E402
from sbc.chakra_lab import (  # noqa: E402
    ChakraLabActorSelection,
    ChakraLabEngine,
    ChakraLabRequest,
)
from sbc.models import GeoLocation, to_primitive  # noqa: E402
from strict_shadbala_doctrine import event_strict_shadbala_context  # noqa: E402


ASPECT_EVIDENCE_TRACE_CONTRACT = "GANN_ASPECT_EVIDENCE_TRACE_V1"
ASPECT_EVIDENCE_TRACE_VERSION = "timestamp_safe_sbc_strength_trace_v1"
SBC_DISPLAY_TIMEZONE = "Asia/Kolkata"
SBC_BODIES = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
    "RAHU",
    "KETU",
)
STRICT_SHADBALA_BODIES = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
)
STRICT_SWISSEPH_IDS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MARS": swe.MARS,
    "MERCURY": swe.MERCURY,
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
}
PIP_FACTOR_BY_SYMBOL = {"USDJPY": 100.0}
TIMEFRAME_DURATION = {
    "M30": pd.Timedelta(minutes=30),
    "H1": pd.Timedelta(hours=1),
    "H4": pd.Timedelta(hours=4),
    "D1": pd.Timedelta(days=1),
    "W1": pd.Timedelta(days=7),
}


def _utc(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        raise ValueError("Aspect evidence trace timestamps must include a UTC offset")
    return timestamp.tz_convert("UTC")


def _finite(value: Any, digits: int = 5) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number, digits) if math.isfinite(number) else None


def _json_number(value: Any, digits: int = 5) -> float | None:
    return _finite(value, digits)


def _timeframe_duration(timeframe: str) -> pd.Timedelta:
    duration = TIMEFRAME_DURATION.get(str(timeframe or "").upper())
    if duration is None:
        raise ValueError(f"Unsupported aspect evidence trace timeframe: {timeframe}")
    return duration


def _normalized_price(price: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close"}
    missing = sorted(required - set(price.columns))
    if missing:
        raise ValueError(f"Price frame is missing required columns: {', '.join(missing)}")
    frame = price.copy().sort_index()
    index = pd.DatetimeIndex(frame.index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    else:
        index = index.tz_convert("UTC")
    frame.index = index
    return frame.loc[~frame.index.duplicated(keep="last")].sort_index()


def _bar_candidates(total: int, max_records: int) -> tuple[list[int], bool]:
    if total <= max_records:
        return list(range(total)), False
    # Always retain the first and last completed bar.  The explicit sampling
    # metadata below prevents a sparse trace from looking like a full replay.
    selected = np.linspace(0, total - 1, num=max_records, dtype=int).tolist()
    return list(dict.fromkeys(int(item) for item in selected)), True


def _latest_closed_position(
    close_times: pd.DatetimeIndex,
    as_of: pd.Timestamp,
) -> int | None:
    positions = np.flatnonzero(close_times <= as_of)
    return int(positions[-1]) if len(positions) else None


def _rsi_zone(value: float | None) -> str:
    if value is None:
        return "unavailable"
    if value >= 70.0:
        return "at_or_above_70"
    if value <= 30.0:
        return "at_or_below_30"
    return "above_midline" if value >= 50.0 else "below_midline"


def _strict_observables(timestamp: pd.Timestamp) -> dict[str, dict[str, float]]:
    """Read per-planet observables without inferring an unrecorded doctrine."""

    result: dict[str, dict[str, float]] = {
        "speeds": {},
        "latitudes": {},
        "declinations": {},
    }
    try:
        configure_ephemeris()
        utc = _utc(timestamp)
        hour = (
            utc.hour
            + utc.minute / 60.0
            + utc.second / 3600.0
            + utc.microsecond / 3_600_000_000.0
        )
        julian_day = swe.julday(utc.year, utc.month, utc.day, hour)
        sidereal_flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        equatorial_flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL | swe.FLG_SPEED
        for body, planet_id in STRICT_SWISSEPH_IDS.items():
            try:
                ecliptic, _ = swe.calc_ut(julian_day, planet_id, sidereal_flags)
                equatorial, _ = swe.calc_ut(julian_day, planet_id, equatorial_flags)
            except Exception:
                continue
            result["speeds"][body] = float(ecliptic[3])
            result["latitudes"][body] = float(ecliptic[1])
            result["declinations"][body] = float(equatorial[1])
    except Exception:
        return result
    return result


def _aspect_strength_context(
    *,
    event: Mapping[str, Any],
    at: pd.Timestamp,
    longitudes_by_body: Mapping[str, pd.Series],
    reference: Mapping[str, Any],
    artifact_mode: str,
    external_gate: Mapping[str, Any],
) -> dict[str, Any]:
    longitudes: dict[str, float] = {}
    for body, series in longitudes_by_body.items():
        try:
            value = float(series.loc[at])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value):
            longitudes[body] = value % 360.0
    if not longitudes:
        return {
            "status": "unavailable",
            "reason": "Swiss Ephemeris longitudes were unavailable at this timestamp.",
        }

    active_body = str(event.get("event_transit_body") or "").strip().upper()
    secondary_body = ""
    if str(artifact_mode).upper() == "TT":
        secondary_body = str(event.get("event_natal_body") or "").strip().upper()
    if not active_body:
        return {
            "status": "not_applicable",
            "reason": "The event has no transit body for strict-strength evaluation.",
        }

    latitude = float(reference.get("latitude") or 0.0)
    longitude = float(reference.get("longitude") or 0.0)
    try:
        houses = sidereal_house_cusps(at, latitude, longitude)
        observables = _strict_observables(at)
        context = event_strict_shadbala_context(
            active_body,
            secondary_body,
            longitudes,
            houses.get(1),
            houses,
            at,
            longitude,
            observables["speeds"],
            observables["latitudes"],
            observables["declinations"],
            latitude,
        )
    except Exception as exc:
        return {
            "status": "unavailable",
            "body": active_body,
            "reason": f"Strict strength calculation failed: {exc}",
        }

    total = _json_number(context.get("event_strict_shadbala_implemented_total_virupa_avg"), 3)
    return {
        "status": "computed_provisional" if total is not None else "not_applicable",
        "body": active_body,
        "scopePolicy": context.get("event_strict_shadbala_scope_policy"),
        "implementedTotalVirupa": total,
        "strengthVsMinimum": _json_number(
            context.get("event_strict_shadbala_implemented_total_ratio_avg"), 4
        ),
        "drikVirupa": _json_number(context.get("event_strict_drik_bala_virupa_avg"), 3),
        "drikBeneficVirupa": _json_number(
            context.get("event_strict_drik_benefic_virupa_avg"), 3
        ),
        "drikMaleficVirupa": _json_number(
            context.get("event_strict_drik_malefic_virupa_avg"), 3
        ),
        "saptavargajaVirupa": _json_number(
            context.get("event_strict_saptavargaja_bala_virupa_avg"), 3
        ),
        "ojayugmaVirupa": _json_number(
            context.get("event_strict_ojayugma_bala_virupa_avg"), 3
        ),
        "kaala9Virupa": _json_number(
            context.get("event_strict_kaala_9_bala_virupa_avg"), 3
        ),
        "chestaVirupa": _json_number(
            context.get("event_strict_chesta_bala_virupa_avg"), 3
        ),
        "calculatorStatus": context.get("event_strict_shadbala_status"),
        "drikStatus": context.get("event_strict_drik_status"),
        "missingComponents": str(
            context.get("event_strict_shadbala_missing_components") or ""
        ).split("|") if context.get("event_strict_shadbala_missing_components") else [],
        "certification": {
            "status": str(external_gate.get("status") or "unavailable"),
            "certified": bool(external_gate.get("certified") is True),
            "contract": str(
                external_gate.get("contract")
                or "GANN_ASTRO_EXTERNAL_CERTIFICATION_GATE_V1"
            ),
        },
    }


def _sbc_snapshot_summary(
    engine: ChakraLabEngine,
    *,
    at: pd.Timestamp,
    reference: Mapping[str, Any],
) -> dict[str, Any]:
    """Produce the compact part of an SBC snapshot useful in a timeline."""

    latitude = float(reference.get("latitude") or 0.0)
    longitude = float(reference.get("longitude") or 0.0)
    request = ChakraLabRequest(
        at=_utc(at).to_pydatetime(),
        location=GeoLocation(
            latitude=latitude,
            longitude=longitude,
            timezone=SBC_DISPLAY_TIMEZONE,
            altitude_m=0.0,
        ),
        bodies=SBC_BODIES,
        # Fixed-source actors can be evaluated deterministically.  Variable
        # planets are deliberately selected without a motion class so the
        # existing SBC engine reports MOTION_REQUIRED rather than guessing.
        actors=tuple(ChakraLabActorSelection(body=body) for body in SBC_BODIES),
        foundation_profile_id="sbc_raman_foundation_v1",
        grid_profile_id="sbc_81_rotation_normalized_partial_v1",
        vedha_profile_id="phaladeepika_editor_vedha_guidance_v1",
    )
    snapshot = engine.snapshot(request)
    panchanga = snapshot.foundation_snapshot.panchanga
    readiness = [to_primitive(item) for item in snapshot.actor_readiness]
    guidance = snapshot.guidance
    return {
        "snapshotId": snapshot.snapshot_id,
        "asOfUtc": snapshot.as_of_utc.isoformat(),
        "panchanga": {
            "tithi": panchanga.tithi_name,
            "tithiGroup": panchanga.tithi_group,
            "paksha": panchanga.paksha,
            "yoga": panchanga.yoga_name,
            "karana": panchanga.karana_name,
            "weekday": panchanga.vara.weekday,
            "weekdayLord": panchanga.vara.weekday_lord,
        },
        "positions": [
            {
                "body": item.body,
                "longitudeDeg": _json_number(item.longitude_deg, 4),
                "speedDegPerDay": _json_number(item.longitude_speed_deg_per_day, 5),
                "rashi": item.rashi,
                "nakshatras": list(item.nakshatras),
            }
            for item in snapshot.position_context
        ],
        "actorReadiness": readiness,
        "guidance": None
        if guidance is None
        else {
            "guidanceOnly": bool(guidance.guidance_only),
            "financialValidationStatus": guidance.financial_validation_status,
            "favorableUnits": _json_number(guidance.favorable_guidance_units, 3),
            "adverseUnits": _json_number(guidance.adverse_guidance_units, 3),
            "netUnits": _json_number(guidance.net_guidance_units, 3),
            "normalizedScore": _json_number(guidance.normalized_guidance_score, 4),
            "band": guidance.guidance_band,
            "scoredMatchCount": int(guidance.scored_match_count),
            "unresolvedMatchCount": int(guidance.unresolved_match_count),
            "coverageRatio": _json_number(guidance.scoring_coverage_ratio, 4),
        },
        "policy": {
            "displayTimezone": SBC_DISPLAY_TIMEZONE,
            "locationSource": "active_artifact_reference",
            "variableMotion": "not_inferred; variable actors remain MOTION_REQUIRED",
            "instrumentKeys": "not_included_without_explicit_human_mapping",
        },
        "guardrails": {
            "readOnly": True,
            "timestampSafe": True,
            "noLookahead": True,
            "executionAllowed": False,
            "financiallyValidated": False,
            "guidanceOnly": True,
        },
    }


def _overlap_summary(
    events: pd.DataFrame,
    *,
    at: pd.Timestamp,
    selected_event_id: str,
) -> dict[str, Any]:
    local_at = _utc(at).tz_convert(SBC_DISPLAY_TIMEZONE)
    active = events.loc[
        (events["timestamp"] <= local_at) & (events["event_end"] >= local_at)
    ]
    labels: list[dict[str, str]] = []
    for _, row in active.head(10).iterrows():
        event_id = str(row["event_id"])
        labels.append(
            {
                "eventId": event_id,
                "familyKey": str(row["event_family_key"]),
                "aspect": str(row["aspect"]),
                "role": "selected" if event_id == selected_event_id else "overlap",
            }
        )
    return {
        "activeCount": int(len(active)),
        "otherActiveCount": max(0, int(len(active)) - 1),
        "events": labels,
        "truncated": len(active) > len(labels),
        "contract": "astronomy_geometry_visible_at_timestamp",
    }


def _sr_snapshot(
    touch: Mapping[str, Any] | None,
    *,
    as_of: pd.Timestamp,
    timeframe_duration: pd.Timedelta,
    close: float | None,
    pip_factor: float,
) -> dict[str, Any]:
    if touch is None:
        return {
            "status": "no_registered_touch",
            "knownAtUtc": None,
            "lines": [],
        }
    raw_touch_time = touch.get("touch_time_local")
    try:
        touch_time = _utc(raw_touch_time)
    except (TypeError, ValueError):
        return {
            "status": "invalid_registered_touch_time",
            "knownAtUtc": None,
            "lines": [],
        }
    known_at = touch_time + timeframe_duration
    if _utc(as_of) < known_at:
        return {
            "status": "not_observed_yet",
            "knownAtUtc": known_at.isoformat(),
            "lines": [],
        }
    lines: list[dict[str, Any]] = []
    for index in (1, 2):
        price = _finite(touch.get(f"touch_line_price_{index}"), 5)
        if price is None:
            continue
        raw_planet = touch.get(f"touch_planet_{index}")
        planet = "SR" if raw_planet is None or pd.isna(raw_planet) else str(raw_planet)
        lines.append(
            {
                "planet": planet,
                "price": price,
                "distancePipsFromClose": (
                    _finite((float(close) - price) * pip_factor, 2)
                    if close is not None
                    else None
                ),
            }
        )
    return {
        "status": "registered_touch_available",
        "knownAtUtc": known_at.isoformat(),
        "touchTimeUtc": touch_time.isoformat(),
        "lines": lines,
        "source": "registered touch log; unavailable before its candle closed",
    }


def _market_snapshot(
    *,
    position: int | None,
    frame: pd.DataFrame,
    close_times: pd.DatetimeIndex,
    candle_by_close: Mapping[pd.Timestamp, Mapping[str, Any]],
    rsi_values: list[float | None],
    touch: Mapping[str, Any] | None,
    as_of: pd.Timestamp,
    timeframe_duration: pd.Timedelta,
    pip_factor: float,
) -> dict[str, Any]:
    if position is None:
        return {
            "available": False,
            "reason": "No fully closed market candle was available at this timestamp.",
        }
    row = frame.iloc[position]
    close_time = close_times[position]
    candle = candle_by_close.get(close_time, {})
    close = _finite(row["close"], 5)
    rsi = _finite(rsi_values[position], 3) if position < len(rsi_values) else None
    return {
        "available": True,
        "barOpenTimeUtc": frame.index[position].isoformat(),
        "barCloseTimeUtc": close_time.isoformat(),
        "open": _finite(row["open"], 5),
        "high": _finite(row["high"], 5),
        "low": _finite(row["low"], 5),
        "close": close,
        "rsi14": {
            "value": rsi,
            "zone": _rsi_zone(rsi),
            "method": "wilder_smoothed_close_v1",
            "closedBarOnly": True,
        },
        "candle": {
            "direction": candle.get("direction"),
            "rangePips": candle.get("rangePips"),
            "bodyPips": candle.get("bodyPips"),
            "bodyFraction": candle.get("bodyFraction"),
            "upperWickFraction": candle.get("upperWickFraction"),
            "lowerWickFraction": candle.get("lowerWickFraction"),
            "closeLocation": candle.get("closeLocation"),
            "atr14Pips": candle.get("atr14Pips"),
            "preTrend": candle.get("preTrend"),
            "patterns": candle.get("patterns") or [],
        },
        "sr": _sr_snapshot(
            touch,
            as_of=as_of,
            timeframe_duration=timeframe_duration,
            close=close,
            pip_factor=pip_factor,
        ),
    }


def _trace_record(
    *,
    kind: str,
    at: pd.Timestamp,
    event_start: pd.Timestamp,
    event_end: pd.Timestamp,
    position: int | None,
    frame: pd.DataFrame,
    close_times: pd.DatetimeIndex,
    candle_by_close: Mapping[pd.Timestamp, Mapping[str, Any]],
    rsi_values: list[float | None],
    touch: Mapping[str, Any] | None,
    timeframe_duration: pd.Timedelta,
    pip_factor: float,
    events: pd.DataFrame,
    event: Mapping[str, Any],
    longitudes_by_body: Mapping[str, pd.Series],
    reference: Mapping[str, Any],
    artifact_mode: str,
    external_gate: Mapping[str, Any],
    chakra_engine: ChakraLabEngine,
) -> dict[str, Any]:
    if _utc(at) < event_start:
        event_state = "before_window"
    elif _utc(at) > event_end:
        event_state = "after_window"
    elif _utc(at) == event_start:
        event_state = "window_start"
    elif _utc(at) == event_end:
        event_state = "window_end"
    else:
        event_state = "inside_window"
    return {
        "kind": kind,
        "asOfUtc": _utc(at).isoformat(),
        "asOfIst": _utc(at).tz_convert(SBC_DISPLAY_TIMEZONE).isoformat(),
        "eventState": event_state,
        "market": _market_snapshot(
            position=position,
            frame=frame,
            close_times=close_times,
            candle_by_close=candle_by_close,
            rsi_values=rsi_values,
            touch=touch,
            as_of=at,
            timeframe_duration=timeframe_duration,
            pip_factor=pip_factor,
        ),
        "overlaps": _overlap_summary(
            events,
            at=at,
            selected_event_id=str(event.get("event_id") or ""),
        ),
        "sbc": _sbc_snapshot_summary(chakra_engine, at=at, reference=reference),
        "strength": _aspect_strength_context(
            event=event,
            at=at,
            longitudes_by_body=longitudes_by_body,
            reference=reference,
            artifact_mode=artifact_mode,
            external_gate=external_gate,
        ),
        "guardrails": {
            "timestampSafe": True,
            "noLookahead": True,
            "outcomeExcluded": True,
            "executionAllowed": False,
            "consumedByLiveInference": False,
        },
    }


def _outcome_record(
    *,
    touch: Mapping[str, Any] | None,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    if touch is None:
        return {
            "available": False,
            "reason": "No registered touch/outcome is available for this event.",
            "retrospectiveOnly": True,
        }
    raw_touch_time = touch.get("touch_time_local")
    try:
        touch_time = _utc(raw_touch_time)
    except (TypeError, ValueError):
        touch_time = None
    raw_after = touch.get("after72_time_local")
    try:
        label_available = _utc(raw_after) if raw_after is not None and not pd.isna(raw_after) else None
    except (TypeError, ValueError):
        label_available = None
    direction = str(context.get("ret_after_72h_dir") or touch.get("ret_after_72h_dir") or "").upper()
    return {
        "available": bool(direction),
        "retrospectiveOnly": True,
        "touchTimeUtc": touch_time.isoformat() if touch_time is not None else None,
        "labelAvailableAtUtc": label_available.isoformat() if label_available is not None else None,
        "direction": direction or None,
        "returnPct": _json_number(
            context.get("ret_after_72h_pct", touch.get("ret_after_72h_pct")), 5
        ),
        "reason": "Observed outcome is isolated from start/window records and live inference.",
    }


def build_aspect_evidence_trace(
    *,
    event: Mapping[str, Any],
    events: pd.DataFrame,
    price: pd.DataFrame,
    symbol: str,
    timeframe: str,
    reference: Mapping[str, Any],
    artifact_mode: str,
    touch: Mapping[str, Any] | None,
    context: Mapping[str, Any],
    external_gate: Mapping[str, Any],
    max_window_records: int = 120,
) -> dict[str, Any]:
    """Return a deterministic trace for one event without mutating repository state."""

    if not 1 <= int(max_window_records) <= 240:
        raise ValueError("max_window_records must be between 1 and 240")
    event_start = _utc(event.get("timestamp"))
    event_end = _utc(event.get("event_end"))
    if event_end <= event_start:
        raise ValueError("Event end must be later than event start")
    duration = _timeframe_duration(timeframe)
    full_price = _normalized_price(price)
    history_start = event_start - duration * 80
    frame = full_price.loc[(full_price.index >= history_start) & (full_price.index < event_end)].copy()
    if frame.empty:
        raise ValueError("No price candles are available through the event end")
    close_times = pd.DatetimeIndex(frame.index + duration)
    window_positions = [
        index
        for index, close_time in enumerate(close_times)
        if close_time > event_start and close_time <= event_end
    ]
    selected_window_positions, sampled = _bar_candidates(
        len(window_positions), int(max_window_records)
    )
    selected_window_positions = [window_positions[item] for item in selected_window_positions]

    crest_position = (
        max(window_positions, key=lambda index: float(frame.iloc[index]["high"]))
        if window_positions
        else None
    )
    trough_position = (
        min(window_positions, key=lambda index: float(frame.iloc[index]["low"]))
        if window_positions
        else None
    )

    pip_factor = PIP_FACTOR_BY_SYMBOL.get(str(symbol).upper(), 1.0)
    candle_inputs = [
        {
            "time": int(timestamp.timestamp()),
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": int(row.tick_volume) if "tick_volume" in row else 0,
        }
        for timestamp, row in frame.iterrows()
    ]
    candle_records = build_candlestick_bar_records(
        candle_inputs,
        symbol=str(symbol).upper(),
        timeframe=str(timeframe).upper(),
    )
    candle_by_close = {
        _utc(record["closeTime"]): record for record in candle_records
    }
    rsi_values = wilder_rsi_values(frame["close"].astype(float).tolist(), period=14)

    trace_times = [event_start]
    trace_times.extend(close_times[position] for position in selected_window_positions)
    trace_times.extend(
        close_times[position]
        for position in (crest_position, trough_position)
        if position is not None
    )
    trace_times.append(event_end)
    unique_times = pd.DatetimeIndex(trace_times).unique().sort_values()
    longitudes_by_body = {
        body: fetch_planetary_longitude(
            body,
            unique_times,
            astrology_method="sidereal",
            coordinate_system="geo",
        )
        for body in STRICT_SHADBALA_BODIES
    }
    chakra_engine = ChakraLabEngine()

    start_position = _latest_closed_position(close_times, event_start)
    end_position = _latest_closed_position(close_times, event_end)
    start = _trace_record(
        kind="start",
        at=event_start,
        event_start=event_start,
        event_end=event_end,
        position=start_position,
        frame=frame,
        close_times=close_times,
        candle_by_close=candle_by_close,
        rsi_values=rsi_values,
        touch=touch,
        timeframe_duration=duration,
        pip_factor=pip_factor,
        events=events,
        event=event,
        longitudes_by_body=longitudes_by_body,
        reference=reference,
        artifact_mode=artifact_mode,
        external_gate=external_gate,
        chakra_engine=chakra_engine,
    )
    window = [
        _trace_record(
            kind="window_bar",
            at=close_times[position],
            event_start=event_start,
            event_end=event_end,
            position=position,
            frame=frame,
            close_times=close_times,
            candle_by_close=candle_by_close,
            rsi_values=rsi_values,
            touch=touch,
            timeframe_duration=duration,
            pip_factor=pip_factor,
            events=events,
            event=event,
            longitudes_by_body=longitudes_by_body,
            reference=reference,
            artifact_mode=artifact_mode,
            external_gate=external_gate,
            chakra_engine=chakra_engine,
        )
        for position in selected_window_positions
    ]
    end = _trace_record(
        kind="end",
        at=event_end,
        event_start=event_start,
        event_end=event_end,
        position=end_position,
        frame=frame,
        close_times=close_times,
        candle_by_close=candle_by_close,
        rsi_values=rsi_values,
        touch=touch,
        timeframe_duration=duration,
        pip_factor=pip_factor,
        events=events,
        event=event,
        longitudes_by_body=longitudes_by_body,
        reference=reference,
        artifact_mode=artifact_mode,
        external_gate=external_gate,
        chakra_engine=chakra_engine,
    )
    reaction_checkpoints: dict[str, Any] = {
        "available": crest_position is not None and trough_position is not None,
        "retrospectiveOnly": True,
        "selectionKnownAtUtc": event_end.isoformat(),
        "selectionPolicy": (
            "after_window_close_highest_high_and_lowest_low_among_completed_window_bars"
        ),
        "usableAtStart": False,
        "usableDuringWindow": False,
        "consumedByLiveInference": False,
        "consumedByShadowLedger": False,
        "crest": None,
        "trough": None,
    }
    if crest_position is not None and trough_position is not None:
        checkpoints: dict[str, int] = {
            "crest": crest_position,
            "trough": trough_position,
        }
        for name, position in checkpoints.items():
            checkpoint = _trace_record(
                kind=f"window_{name}",
                at=close_times[position],
                event_start=event_start,
                event_end=event_end,
                position=position,
                frame=frame,
                close_times=close_times,
                candle_by_close=candle_by_close,
                rsi_values=rsi_values,
                touch=touch,
                timeframe_duration=duration,
                pip_factor=pip_factor,
                events=events,
                event=event,
                longitudes_by_body=longitudes_by_body,
                reference=reference,
                artifact_mode=artifact_mode,
                external_gate=external_gate,
                chakra_engine=chakra_engine,
            )
            checkpoint["guardrails"] = {
                **checkpoint["guardrails"],
                "selectedRetrospectively": True,
                "selectionKnownAtUtc": event_end.isoformat(),
                "usableAtStart": False,
                "usableDuringWindow": False,
                "consumedByLiveInference": False,
                "consumedByShadowLedger": False,
            }
            reaction_checkpoints[name] = checkpoint
    return {
        "contract": ASPECT_EVIDENCE_TRACE_CONTRACT,
        "version": ASPECT_EVIDENCE_TRACE_VERSION,
        "eventId": str(event.get("event_id") or ""),
        "familyKey": str(event.get("event_family_key") or ""),
        "symbol": str(symbol).upper(),
        "timeframe": str(timeframe).upper(),
        "times": {
            "eventStartUtc": event_start.isoformat(),
            "eventEndUtc": event_end.isoformat(),
            "displayTimezone": SBC_DISPLAY_TIMEZONE,
        },
        "profile": {
            "referenceLabel": str(reference.get("label") or "Active artifact reference"),
            "latitude": _json_number(reference.get("latitude"), 4),
            "longitude": _json_number(reference.get("longitude"), 4),
            "referenceTimezone": str(reference.get("utcOffset") or ""),
            "locationPolicy": "active artifact reference; displayed in IST",
        },
        "start": start,
        "window": {
            "totalCompletedBars": len(window_positions),
            "includedBarCount": len(window),
            "sampled": sampled,
            "samplingPolicy": (
                "all_completed_bars" if not sampled else "evenly_spaced_closed_bar_sample"
            ),
            "records": window,
        },
        "end": end,
        "reactionCheckpoints": reaction_checkpoints,
        "outcome": _outcome_record(touch=touch, context=context),
        "precalculationStatus": {
            "sbc": "computed_per_timestamp_guidance_only",
            "panchanga": "computed_per_timestamp",
            "strictShadbalaDrik": "computed_per_timestamp_provisional",
            "rsi": "computed_from_closed_bars_only",
            "candlestick": "computed_from_closed_bar_ohlc_only",
            "overlappingAspects": "geometry_visible_at_timestamp",
            "sr": "registered_touch_only_no_pre_touch_leakage",
            "gann": "not_included_manual_chart_drawing_state_is_not_a_backend_fact",
        },
        "guardrails": {
            "researchOnly": True,
            "timestampSafe": True,
            "noLookahead": True,
            "outcomeSeparated": True,
            "consumedByLiveInference": False,
            "consumedByShadowLedger": False,
            "executionAllowed": False,
        },
    }
