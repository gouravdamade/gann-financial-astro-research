from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np
import pandas as pd

from astro_event_contract import directional_family_key, entity_members
from financial_astro_ephemeris import (
    IST,
    build_exact_longitude_map,
    configure_ephemeris,
    fetch_planetary_longitude,
    fetch_planetary_longitude_single,
)


ASTRONOMY_CONTRACT = "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2"
GENERATOR_VERSION = "native_tn_event_source_v1_20260711"
EVENT_PROGRESS_REPLACE_ATTEMPTS = 12
EVENT_PROGRESS_REPLACE_RETRY_SECONDS = 0.01
DEFAULT_ENTITIES = "Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu, AVG(all)"
ASPECT_SPECS = {
    "conjunction_orb": {"angle": 0.0, "orb": 1.5},
    "square": {"angle": 90.0, "orb": 1.0},
    "trine": {"angle": 120.0, "orb": 1.0},
    "opposition_orb": {"angle": 180.0, "orb": 1.5},
}
INTERVALS = {
    "30m": pd.Timedelta(minutes=30),
    "1h": pd.Timedelta(hours=1),
    "60m": pd.Timedelta(hours=1),
}


@dataclass(frozen=True)
class OrbWindow:
    start: pd.Timestamp
    end: pd.Timestamp
    peak: pd.Timestamp
    peak_index: int
    peak_orb_deg: float
    peak_separation_deg: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate corrected transit-to-natal aspect windows without JDML4 or market labels. "
            "The first version deliberately supports the Western orb family used by the current reviews."
        )
    )
    parser.add_argument("--ticker", default="USDJPY")
    parser.add_argument("--interval", default="1h", choices=tuple(INTERVALS))
    parser.add_argument(
        "--price-parquet",
        type=Path,
        default=Path(r"D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet"),
        help="Used only to define the available date range and timestamp cadence anchor.",
    )
    parser.add_argument("--start-date", default="2025-03-01")
    parser.add_argument("--end-date", default="2026-03-10")
    parser.add_argument("--transit-entities", default=DEFAULT_ENTITIES)
    parser.add_argument("--natal-entities", default=DEFAULT_ENTITIES)
    parser.add_argument(
        "--selected-aspects",
        default=",".join(ASPECT_SPECS),
        help="Comma-separated subset of conjunction_orb,square,trine,opposition_orb.",
    )
    parser.add_argument("--reference-date", default="1889-02-11")
    parser.add_argument("--reference-time", default="00:00")
    parser.add_argument(
        "--reference-utc-offset",
        default="+09:00",
        help="Fixed historical source-clock offset. +09:00 preserves the declared Tokyo contract.",
    )
    parser.add_argument("--reference-label", default="Tokyo IPO hypothesis 1889-02-11 00:00 +09:00")
    parser.add_argument("--reference-lat", type=float, default=35.6762)
    parser.add_argument("--reference-lon", type=float, default=139.6503)
    parser.add_argument("--min-window-minutes", type=float, default=30.0)
    parser.add_argument(
        "--sr-config-json",
        default="{}",
        help="JSON object embedded in every event for the downstream corrected SR touch builder.",
    )
    parser.add_argument(
        "--sr-config-file",
        type=Path,
        help="Optional UTF-8 JSON file; preferred over shell-escaped --sr-config-json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(r"D:\PycharmProjects\astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet"),
    )
    parser.add_argument(
        "--progress-file",
        type=Path,
        help=(
            "Optional JSON heartbeat written while event combinations are compiled. "
            "It contains only generator progress, never market outcomes."
        ),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def parse_entities(value: str) -> tuple[str, ...]:
    tokens = re.findall(r"AVG\([^)]*\)|[A-Za-z]+", str(value or ""), flags=re.IGNORECASE)
    normalized: list[str] = []
    for token in tokens:
        compact = re.sub(r"\s+", "", token).upper()
        if compact in {"AVG(ALL)", "AVG(ALL7)"}:
            compact = "AVG(ALL)"
        if compact and compact not in normalized:
            normalized.append(compact)
    if not normalized:
        raise ValueError("At least one celestial entity is required.")
    return tuple(normalized)


def parse_aspects(value: str) -> tuple[str, ...]:
    names = tuple(dict.fromkeys(item.strip().lower() for item in str(value or "").split(",") if item.strip()))
    unknown = sorted(set(names) - set(ASPECT_SPECS))
    if unknown:
        raise ValueError(f"Unsupported aspect(s) for the native TN generator: {unknown}")
    if not names:
        raise ValueError("At least one aspect is required.")
    return names


def parse_fixed_offset(value: str) -> timezone:
    match = re.fullmatch(r"([+-])(\d{2}):(\d{2})", str(value or "").strip())
    if not match:
        raise ValueError("reference-utc-offset must use +HH:MM or -HH:MM")
    sign = 1 if match.group(1) == "+" else -1
    minutes = sign * (int(match.group(2)) * 60 + int(match.group(3)))
    return timezone(timedelta(minutes=minutes))


def reference_timestamp(date_text: str, time_text: str, offset_text: str) -> pd.Timestamp:
    try:
        naive = datetime.fromisoformat(f"{str(date_text).strip()}T{str(time_text).strip()}")
    except ValueError as exc:
        raise ValueError("reference date/time must use YYYY-MM-DD and HH:MM[:SS]") from exc
    return pd.Timestamp(naive.replace(tzinfo=parse_fixed_offset(offset_text)))


def parse_sr_config_json(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(str(value or "{}"))
    except json.JSONDecodeError as exc:
        raise ValueError("sr-config-json must be a JSON object") from exc
    if not isinstance(parsed, dict):
        raise ValueError("sr-config-json must be a JSON object")

    def float_list(name: str, default: tuple[float, ...]) -> list[float]:
        raw = parsed.get(name, default)
        if not isinstance(raw, (list, tuple)):
            raise ValueError(f"SR {name} must be a list")
        values = list(dict.fromkeys(float(item) for item in raw))
        if not values or len(values) > 40 or any(not np.isfinite(item) or item <= 0 for item in values):
            raise ValueError(f"SR {name} must contain 1-40 positive finite values")
        return values

    harmonics = float_list("harmonics", (0.12, 0.18))
    n_values = float_list("n_values", (1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8))
    raw_degrees = parsed.get("degrees", (360, 180, 90, 45))
    if not isinstance(raw_degrees, (list, tuple)):
        raise ValueError("SR degrees must be a list")
    degrees = list(dict.fromkeys(int(float(item)) for item in raw_degrees))
    if not degrees or len(degrees) > 20 or any(item <= 0 or item > 360 for item in degrees):
        raise ValueError("SR degrees must contain 1-20 integers in the range 1-360")
    if len(harmonics) * len(n_values) * len(degrees) > 400:
        raise ValueError("SR harmonic x n x degree combinations exceed the safe limit of 400")
    epsilon = float(parsed.get("epsilon", 0.30))
    price_zone = float(parsed.get("price_zone", 0.16))
    moon_factor = float(parsed.get("moon_factor", 1.8))
    band_pct = float(parsed.get("band_pct", 0.01))
    if not 0 < epsilon <= 10 or not 0 < price_zone <= 10:
        raise ValueError("SR epsilon and price_zone must be greater than 0 and no more than 10")
    if not 0 < moon_factor <= 10 or not 0 < band_pct <= 1:
        raise ValueError("SR moon_factor and band_pct are outside safe bounds")
    return {
        "harmonics": harmonics,
        "n_values": n_values,
        "degrees": degrees,
        "epsilon": epsilon,
        "price_zone": price_zone,
        "moon_factor": moon_factor,
        "band_pct": band_pct,
    }


def write_progress(
    path: Path | None,
    *,
    phase: str,
    completed: int,
    total: int,
    transit_body: str | None = None,
    natal_body: str | None = None,
    aspect: str | None = None,
) -> None:
    """Publish generator-only progress without allowing a UI reader to stop the job."""

    if path is None:
        return
    payload = {
        "contract": "CORRECTED_TN_EVENT_PROGRESS_V1",
        "phase": str(phase),
        "completed": max(0, int(completed)),
        "total": max(0, int(total)),
        "transitBody": str(transit_body or ""),
        "natalBody": str(natal_body or ""),
        "aspect": str(aspect or ""),
        "updatedAtUtc": pd.Timestamp.now(tz="UTC").isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    try:
        temporary.write_text(serialized, encoding="utf-8")
        for attempt in range(EVENT_PROGRESS_REPLACE_ATTEMPTS):
            try:
                temporary.replace(path)
                return
            except PermissionError:
                # On Windows a short-lived reader can deny the delete-share access needed by
                # replace(). The job manager treats an unreadable in-progress snapshot as a
                # missed heartbeat, so retry the preferred atomic handoff before degrading.
                if attempt + 1 < EVENT_PROGRESS_REPLACE_ATTEMPTS:
                    time.sleep(EVENT_PROGRESS_REPLACE_RETRY_SECONDS)
    except OSError:
        pass

    # A heartbeat is advisory. If an external reader keeps the destination locked, use a
    # best-effort in-place write and let readers ignore a transient partial JSON document.
    # Generation must never fail merely because progress cannot be published.
    try:
        path.write_text(serialized, encoding="utf-8")
    except OSError:
        pass
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def circular_average_frame(frame: pd.DataFrame) -> pd.Series:
    radians = np.deg2rad(frame.astype(float))
    sin_mean = np.sin(radians).mean(axis=1, skipna=True)
    cos_mean = np.cos(radians).mean(axis=1, skipna=True)
    magnitude = np.hypot(sin_mean, cos_mean)
    values = np.mod(np.rad2deg(np.arctan2(sin_mean, cos_mean)), 360.0)
    return pd.Series(np.where(magnitude > 1e-12, values, np.nan), index=frame.index, dtype=float)


def entity_series_map(entities: Iterable[str], timestamps: pd.DatetimeIndex) -> tuple[dict[str, pd.Series], dict[str, pd.Series]]:
    entity_names = tuple(dict.fromkeys(str(entity).upper() for entity in entities))
    required_planets = tuple(
        dict.fromkeys(member for entity in entity_names for member in entity_members(entity))
    )
    planet_map = build_exact_longitude_map(
        required_planets,
        timestamps,
        fetch_fn=fetch_planetary_longitude,
        astrology_method="sidereal",
        coordinate_system="geo",
    )
    result: dict[str, pd.Series] = {}
    for entity in entity_names:
        members = entity_members(entity)
        if len(members) == 1:
            result[entity] = planet_map[members[0]].copy()
        else:
            result[entity] = circular_average_frame(
                pd.concat([planet_map[member].rename(member) for member in members], axis=1)
            )
    return result, planet_map


def natal_entity_map(entities: Iterable[str], timestamp: pd.Timestamp) -> tuple[dict[str, float], dict[str, float]]:
    entity_names = tuple(dict.fromkeys(str(entity).upper() for entity in entities))
    required_planets = tuple(
        dict.fromkeys(member for entity in entity_names for member in entity_members(entity))
    )
    planets: dict[str, float] = {}
    for planet in required_planets:
        value = fetch_planetary_longitude_single(planet, timestamp, "sidereal", "geo")
        if value is None or not np.isfinite(float(value)):
            raise RuntimeError(f"No corrected natal longitude for {planet} at {timestamp}")
        planets[planet] = float(value) % 360.0

    entities_out: dict[str, float] = {}
    for entity in entity_names:
        members = entity_members(entity)
        if len(members) == 1:
            entities_out[entity] = planets[members[0]]
            continue
        values = pd.DataFrame([[planets[member] for member in members]], columns=members)
        entities_out[entity] = float(circular_average_frame(values).iloc[0])
    return entities_out, planets


def separation_degrees(left: np.ndarray, right: float | np.ndarray) -> np.ndarray:
    difference = np.mod(np.abs(np.asarray(left, dtype=float) - np.asarray(right, dtype=float)), 360.0)
    return np.minimum(difference, 360.0 - difference)


def _interpolate_crossing(
    left_time: pd.Timestamp,
    right_time: pd.Timestamp,
    left_value: float,
    right_value: float,
) -> pd.Timestamp:
    denominator = float(right_value) - float(left_value)
    if not np.isfinite(denominator) or abs(denominator) < 1e-15:
        return right_time
    fraction = min(1.0, max(0.0, -float(left_value) / denominator))
    return left_time + (right_time - left_time) * fraction


def detect_orb_windows(
    longitudes: pd.Series,
    target_longitude: float,
    target_angle: float,
    orb_limit: float,
    min_window_minutes: float = 30.0,
) -> list[OrbWindow]:
    index = pd.DatetimeIndex(longitudes.index)
    separation = separation_degrees(longitudes.to_numpy(dtype=float), float(target_longitude))
    distance = np.abs(separation - float(target_angle))
    inside = np.isfinite(distance) & (distance <= float(orb_limit))
    hit_indices = np.flatnonzero(inside)
    if len(hit_indices) == 0:
        return []

    segments = np.split(hit_indices, np.flatnonzero(np.diff(hit_indices) != 1) + 1)
    boundary_value = float(orb_limit) - distance
    windows: list[OrbWindow] = []
    for segment in segments:
        first = int(segment[0])
        last = int(segment[-1])
        start = index[first]
        end = index[last]
        if first > 0 and np.isfinite(boundary_value[first - 1]):
            start = _interpolate_crossing(
                index[first - 1], index[first], boundary_value[first - 1], boundary_value[first]
            )
        if last + 1 < len(index) and np.isfinite(boundary_value[last + 1]):
            end = _interpolate_crossing(
                index[last], index[last + 1], boundary_value[last], boundary_value[last + 1]
            )
        peak_index = int(segment[np.argmin(distance[segment])])
        duration_minutes = (end - start).total_seconds() / 60.0
        if duration_minutes < float(min_window_minutes):
            continue
        windows.append(
            OrbWindow(
                start=start,
                end=end,
                peak=index[peak_index],
                peak_index=peak_index,
                peak_orb_deg=float(distance[peak_index]),
                peak_separation_deg=float(separation[peak_index]),
            )
        )
    return windows


def canonical_pair(left: str, right: str) -> str:
    return "|".join(sorted((str(left).upper(), str(right).upper())))


def stable_event_id(
    transit_body: str,
    natal_body: str,
    aspect: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> str:
    identity = "|".join(
        (
            ASTRONOMY_CONTRACT,
            "TN",
            str(transit_body).upper(),
            str(natal_body).upper(),
            str(aspect).lower(),
            start.isoformat(),
            end.isoformat(),
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def build_calendar_index(
    price_index: pd.DatetimeIndex,
    start_date: str,
    end_date: str,
    cadence: pd.Timedelta,
) -> pd.DatetimeIndex:
    index = pd.DatetimeIndex(price_index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    index = index.tz_convert(IST).sort_values()
    requested_start = pd.Timestamp(start_date).tz_localize(IST)
    requested_end = pd.Timestamp(end_date).tz_localize(IST) + pd.Timedelta(days=1) - cadence
    available_start = index.min()
    available_end = index.max()
    start = max(requested_start, available_start)
    end = min(requested_end, available_end)
    if start > end:
        raise ValueError(f"Requested range does not overlap price data: {start} -> {end}")

    anchor = available_start
    steps = int(np.ceil((start - anchor) / cadence))
    aligned_start = anchor + steps * cadence
    steps_end = int(np.floor((end - anchor) / cadence))
    aligned_end = anchor + steps_end * cadence
    return pd.date_range(aligned_start, aligned_end, freq=cadence)


def build_event_frame(
    timestamps: pd.DatetimeIndex,
    transit_entities: tuple[str, ...],
    natal_entities: tuple[str, ...],
    aspects: tuple[str, ...],
    natal_timestamp: pd.Timestamp,
    ticker: str,
    interval: str,
    reference_metadata: dict[str, Any],
    min_window_minutes: float,
    progress_callback: Callable[[str, int, int, str | None, str | None, str | None], None]
    | None = None,
) -> tuple[pd.DataFrame, dict[str, float]]:
    total_combinations = len(transit_entities) * len(natal_entities) * len(aspects)
    if progress_callback is not None:
        progress_callback("ephemeris", 0, total_combinations, None, None, None)
    transit_map, transit_planet_map = entity_series_map(transit_entities, timestamps)
    natal_map, natal_planets = natal_entity_map(natal_entities, natal_timestamp)
    natal_snapshot_json = json.dumps(natal_planets, sort_keys=True, separators=(",", ":"))
    rows: list[dict[str, Any]] = []
    completed_combinations = 0
    report_every = max(1, total_combinations // 100)

    for transit_body in transit_entities:
        transit_series = transit_map[transit_body]
        for natal_body in natal_entities:
            natal_longitude = natal_map[natal_body]
            for aspect in aspects:
                spec = ASPECT_SPECS[aspect]
                windows = detect_orb_windows(
                    transit_series,
                    natal_longitude,
                    target_angle=float(spec["angle"]),
                    orb_limit=float(spec["orb"]),
                    min_window_minutes=min_window_minutes,
                )
                for window in windows:
                    peak_snapshot = {
                        planet: float(series.iloc[window.peak_index]) % 360.0
                        for planet, series in transit_planet_map.items()
                    }
                    start = window.start.tz_convert(IST)
                    end = window.end.tz_convert(IST)
                    peak = window.peak.tz_convert(IST)
                    event_id = stable_event_id(transit_body, natal_body, aspect, start, end)
                    event_detail = {
                        "scope": "TN",
                        "transit_body": transit_body,
                        "natal_body": natal_body,
                        "aspect": aspect,
                        "target_angle_deg": float(spec["angle"]),
                        "orb_limit_deg": float(spec["orb"]),
                        "peak_orb_deg": window.peak_orb_deg,
                        "peak_separation_deg": window.peak_separation_deg,
                        "peak_time": peak.isoformat(),
                    }
                    rows.append(
                        {
                            "event_id": event_id,
                            "timestamp": start,
                            "event_end": end,
                            "peak_time": peak,
                            "ticker": str(ticker).upper(),
                            "interval": interval,
                            "aspect": aspect,
                            "b1": transit_body,
                            "b2": natal_body,
                            "pair_key": canonical_pair(transit_body, natal_body),
                            "is_natal": True,
                            "event_scope": "TN",
                            "event_transit_body": transit_body,
                            "event_natal_body": natal_body,
                            "event_family_key": directional_family_key("TN", transit_body, natal_body, aspect),
                            "event_role_resolution_status": "explicit_native_generator",
                            "event_role_best_orb_deg": window.peak_orb_deg,
                            "event_role_alternate_orb_deg": np.nan,
                            "duration_minutes": (end - start).total_seconds() / 60.0,
                            "closeness": max(0.0, 1.0 - window.peak_orb_deg / float(spec["orb"])),
                            "event_peak_orb_deg": window.peak_orb_deg,
                            "event_peak_separation_deg": window.peak_separation_deg,
                            "event_target_angle_deg": float(spec["angle"]),
                            "event_orb_limit_deg": float(spec["orb"]),
                            "aspect_signatures": f"TN:{transit_body}->{natal_body}:{aspect}",
                            "event_aspects_json": json.dumps([event_detail], sort_keys=True, separators=(",", ":")),
                            "planet_longitudes_json": json.dumps(peak_snapshot, sort_keys=True, separators=(",", ":")),
                            "natal_longitudes_json": natal_snapshot_json,
                            "astrology_method": "sidereal",
                            "coordinate_system": "geo",
                            "astronomy_contract_version": ASTRONOMY_CONTRACT,
                            "source_event_generator": GENERATOR_VERSION,
                            **reference_metadata,
                        }
                    )
                completed_combinations += 1
                if progress_callback is not None and (
                    completed_combinations % report_every == 0
                    or completed_combinations == total_combinations
                ):
                    progress_callback(
                        "aspect_windows",
                        completed_combinations,
                        total_combinations,
                        transit_body,
                        natal_body,
                        aspect,
                    )

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, natal_planets
    frame = frame.sort_values(
        ["timestamp", "event_transit_body", "event_natal_body", "aspect", "event_id"]
    ).reset_index(drop=True)
    starts = frame["timestamp"].astype("int64").to_numpy()
    ends = frame["event_end"].astype("int64").to_numpy()
    peaks = frame["peak_time"].astype("int64").to_numpy()
    frame["active_aspects_count"] = [int(np.sum((starts <= peak) & (ends >= peak))) for peak in peaks]
    return frame, natal_planets


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def atomic_write_parquet(frame: pd.DataFrame, path: Path, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists; pass --overwrite to replace it: {path}")
    temporary = path.with_name(f"{path.name}.tmp")
    frame.to_parquet(temporary, index=False)
    temporary.replace(path)


def main() -> None:
    args = parse_args()
    configure_ephemeris()
    transit_entities = parse_entities(args.transit_entities)
    natal_entities = parse_entities(args.natal_entities)
    aspects = parse_aspects(args.selected_aspects)
    sr_config_text = (
        args.sr_config_file.read_text(encoding="utf-8")
        if args.sr_config_file is not None
        else args.sr_config_json
    )
    sr_config = parse_sr_config_json(sr_config_text)
    cadence = INTERVALS[args.interval]
    if not args.price_parquet.exists():
        raise FileNotFoundError(args.price_parquet)
    price = pd.read_parquet(args.price_parquet, columns=[])
    timestamps = build_calendar_index(price.index, args.start_date, args.end_date, cadence)
    natal_timestamp = reference_timestamp(
        args.reference_date,
        args.reference_time,
        args.reference_utc_offset,
    )
    reference_metadata = {
        "reference_chart_label": args.reference_label,
        "reference_datetime_source": natal_timestamp.isoformat(),
        "reference_timezone_policy": f"fixed_offset_{args.reference_utc_offset}",
        "reference_lat": float(args.reference_lat),
        "reference_lon": float(args.reference_lon),
    }

    def report_progress(
        phase: str,
        completed: int,
        total: int,
        transit_body: str | None,
        natal_body: str | None,
        aspect: str | None,
    ) -> None:
        write_progress(
            args.progress_file,
            phase=phase,
            completed=completed,
            total=total,
            transit_body=transit_body,
            natal_body=natal_body,
            aspect=aspect,
        )
        if args.progress_file is not None:
            print(
                "EVENT_PROGRESS "
                f"phase={phase} completed={completed}/{total} "
                f"transit={transit_body or '-'} natal={natal_body or '-'} aspect={aspect or '-'}",
                flush=True,
            )

    frame, natal_planets = build_event_frame(
        timestamps=timestamps,
        transit_entities=transit_entities,
        natal_entities=natal_entities,
        aspects=aspects,
        natal_timestamp=natal_timestamp,
        ticker=args.ticker,
        interval=args.interval,
        reference_metadata=reference_metadata,
        min_window_minutes=args.min_window_minutes,
        progress_callback=report_progress,
    )
    if frame.empty:
        raise RuntimeError("No aspect windows were generated for the requested contract.")
    frame["sr_config_json"] = json.dumps(sr_config, sort_keys=True, separators=(",", ":"))
    atomic_write_parquet(frame, args.output, args.overwrite)

    manifest_path = args.output.with_suffix(".manifest.json")
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "astronomy_contract_version": ASTRONOMY_CONTRACT,
        "generated_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "output_path": str(args.output.resolve()),
        "output_sha256": sha256_file(args.output),
        "price_source_path": str(args.price_parquet.resolve()),
        "price_source_sha256": sha256_file(args.price_parquet),
        "timestamp_count": len(timestamps),
        "timestamp_start": timestamps.min().isoformat(),
        "timestamp_end": timestamps.max().isoformat(),
        "event_count": len(frame),
        "event_start": frame["timestamp"].min().isoformat(),
        "event_end": frame["event_end"].max().isoformat(),
        "transit_entities": list(transit_entities),
        "natal_entities": list(natal_entities),
        "aspects": list(aspects),
        "aspect_specs": ASPECT_SPECS,
        "reference": reference_metadata,
        "sr_config": sr_config,
        "natal_planet_longitudes": natal_planets,
        "outcome_labels_included": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {len(frame)} corrected TN events: {args.output}")
    print(f"Manifest: {manifest_path}")
    print(frame["aspect"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
