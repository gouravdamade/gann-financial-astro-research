from __future__ import annotations

import re
import sys
import threading
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from collective_geometry import (
    AVG_ALL_MEMBERS,
    calculate_collective_field,
    legacy_circular_mean,
)

SHARED_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(SHARED_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(SHARED_PROJECT_ROOT))

from financial_astro_ephemeris import fetch_planetary_longitude  # noqa: E402


PLANETARY_LINE_CONTRACT = "GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1"
SUPPORTED_PLANETS = (
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "RAHU",
    "KETU",
    "URANUS",
    "NEPTUNE",
    "PLUTO",
    "AVG(ALL)",
)
AVG_ALL_PLANETS = AVG_ALL_MEMBERS
MAX_TIMESTAMPS = 1_200
MAX_LINES = 96
MAX_POINTS = 100_000
MAX_VALUES_PER_PARAMETER = 12
_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
_EPHEMERIS_LOCK = threading.RLock()


def _finite_values(
    value: Any,
    label: str,
    *,
    minimum: float,
    maximum: float,
) -> tuple[float, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    if len(value) > MAX_VALUES_PER_PARAMETER:
        raise ValueError(
            f"{label} supports at most {MAX_VALUES_PER_PARAMETER} values"
        )
    values: list[float] = []
    for item in value:
        number = float(item)
        if not np.isfinite(number) or not minimum <= number <= maximum:
            raise ValueError(
                f"{label} values must be finite and between {minimum:g} and {maximum:g}"
            )
        if number not in values:
            values.append(number)
    return tuple(values)


def _timestamps(value: Any) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("timestamps must be a non-empty list of Unix seconds")
    timestamps = tuple(sorted({int(item) for item in value}))
    if len(timestamps) > MAX_TIMESTAMPS:
        raise ValueError(f"timestamps supports at most {MAX_TIMESTAMPS} samples")
    if any(item <= 0 for item in timestamps):
        raise ValueError("timestamps must contain positive Unix seconds")
    return timestamps


def _circular_average(member_values: list[np.ndarray]) -> np.ndarray:
    return legacy_circular_mean(member_values)


def _number_label(value: float) -> str:
    return f"{value:.8g}"


def build_planetary_line_overlay(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Planetary line request must be an object")
    unknown = set(payload) - {"symbol", "timeframe", "timestamps", "groups"}
    if unknown:
        raise ValueError(
            f"Unknown planetary line request field(s): {', '.join(sorted(unknown))}"
        )

    timestamps = _timestamps(payload.get("timestamps"))
    raw_groups = payload.get("groups")
    if not isinstance(raw_groups, list):
        raise ValueError("groups must be a list")
    if len(raw_groups) > len(SUPPORTED_PLANETS):
        raise ValueError(f"groups supports at most {len(SUPPORTED_PLANETS)} planets")

    groups: list[dict[str, Any]] = []
    seen_planets: set[str] = set()
    line_count = 0
    for raw_group in raw_groups:
        if not isinstance(raw_group, dict):
            raise ValueError("Each planetary line group must be an object")
        planet = str(raw_group.get("planet") or "").strip().upper()
        if planet not in SUPPORTED_PLANETS:
            raise ValueError(f"Unsupported planetary line planet: {planet or '(blank)'}")
        if planet in seen_planets:
            raise ValueError(f"Duplicate planetary line group: {planet}")
        seen_planets.add(planet)
        if not bool(raw_group.get("enabled", False)):
            continue

        mode = str(raw_group.get("mode") or "direct").strip().lower()
        if mode not in {"direct", "mirror", "both"}:
            raise ValueError(f"Unsupported mode for {planet}: {mode}")
        color = str(raw_group.get("color") or "#58a6c6").strip()
        if not _COLOR_PATTERN.fullmatch(color):
            raise ValueError(f"{planet} color must use #RRGGBB")
        n_values = _finite_values(
            raw_group.get("nValues"), f"{planet} nValues", minimum=0.000001, maximum=100_000
        )
        f_values = _finite_values(
            raw_group.get("fValues"), f"{planet} fValues", minimum=0.000001, maximum=1_000
        )
        degrees = _finite_values(
            raw_group.get("degrees"), f"{planet} degrees", minimum=0.000001, maximum=360
        )
        directions = ("direct", "mirror") if mode == "both" else (mode,)
        group_lines = len(n_values) * len(f_values) * len(degrees) * len(directions)
        line_count += group_lines
        groups.append(
            {
                "planet": planet,
                "color": color.lower(),
                "directions": directions,
                "nValues": n_values,
                "fValues": f_values,
                "degrees": degrees,
                "lineCount": group_lines,
            }
        )

    if line_count > MAX_LINES:
        raise ValueError(
            f"Requested {line_count} lines; the live overlay limit is {MAX_LINES}"
        )
    point_count = line_count * len(timestamps)
    if point_count > MAX_POINTS:
        raise ValueError(
            f"Requested {point_count} plotted points; the live overlay limit is {MAX_POINTS}"
        )

    required_planets: list[str] = []
    for group in groups:
        members = AVG_ALL_PLANETS if group["planet"] == "AVG(ALL)" else (group["planet"],)
        for member in members:
            if member not in required_planets:
                required_planets.append(member)

    index = pd.DatetimeIndex(pd.to_datetime(timestamps, unit="s", utc=True))
    longitudes: dict[str, np.ndarray] = {}
    if required_planets:
        with _EPHEMERIS_LOCK:
            for planet in required_planets:
                values = fetch_planetary_longitude(
                    planet,
                    index,
                    astrology_method="sidereal",
                    coordinate_system="geo",
                )
                longitudes[planet] = values.reindex(index).to_numpy(dtype=np.float64)

    lines: list[dict[str, Any]] = []
    collective_field = (
        calculate_collective_field(longitudes, timestamps)
        if "AVG(ALL)" in seen_planets
        and any(group["planet"] == "AVG(ALL)" for group in groups)
        else None
    )
    for group in groups:
        planet = group["planet"]
        longitude = (
            _circular_average([longitudes[member] for member in AVG_ALL_PLANETS])
            if planet == "AVG(ALL)"
            else longitudes[planet]
        )
        for n_value, f_value, degree, direction in product(
            group["nValues"],
            group["fValues"],
            group["degrees"],
            group["directions"],
        ):
            source_longitude = 360.0 - longitude if direction == "mirror" else longitude
            values = f_value * n_value * degree + f_value * source_longitude
            suffix = (
                f"{planet}:{direction}:n={_number_label(n_value)}:"
                f"f={_number_label(f_value)}:d={_number_label(degree)}"
            )
            lines.append(
                {
                    "id": suffix,
                    "planet": planet,
                    "mode": direction,
                    "n": n_value,
                    "f": f_value,
                    "degree": degree,
                    "color": group["color"],
                    "label": (
                        f"{planet} {direction} | n {_number_label(n_value)} | "
                        f"f {_number_label(f_value)} | d {_number_label(degree)}"
                    ),
                    "points": [
                        {"time": timestamp, "value": round(float(value), 8)}
                        for timestamp, value in zip(timestamps, values, strict=True)
                    ],
                }
            )

    return {
        "contract": PLANETARY_LINE_CONTRACT,
        "symbol": str(payload.get("symbol") or "").strip().upper(),
        "timeframe": str(payload.get("timeframe") or "").strip().upper(),
        "astronomyContract": "RAMAN_SIDEREAL_SWISSEPH_EXACT_BAR_TIMESTAMPS_V1",
        "formula": {
            "direct": "f * n * degree + f * longitude",
            "mirror": "f * n * degree + f * (360 - longitude)",
            "avgAll": "circular mean of Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto",
        },
        "timestampCount": len(timestamps),
        "lineCount": len(lines),
        "pointCount": len(timestamps) * len(lines),
        "limits": {
            "maxTimestamps": MAX_TIMESTAMPS,
            "maxLines": MAX_LINES,
            "maxPoints": MAX_POINTS,
        },
        "collectiveField": collective_field,
        "lines": lines,
        "guardrails": {
            "researchOnly": True,
            "curveFitExploration": True,
            "exactBarTimestamps": True,
            "consumedByLiveInference": False,
            "consumedByAutoSuggest": False,
            "consumedByShadowLedger": False,
            "executionAllowed": False,
        },
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
