from __future__ import annotations

from collections.abc import Iterable
from datetime import timezone
from typing import Any

import pandas as pd

from .config import profile as get_profile
from .core import compute_bav, compute_sav, transit_evidence, validate_chart
from .ephemeris import natal_context, transit_signs


def natal_tables(config: dict[str, Any], profile_id: str) -> dict[str, Any]:
    context = natal_context(profile_id, get_profile(config, profile_id))
    bav = compute_bav(context["signs"])
    sav = compute_sav(bav)
    validation = validate_chart(bav, sav)
    return {
        "profile": context,
        "bav": {planet: list(row) for planet, row in bav.items()},
        "sav": list(sav),
        "validation": validation,
        "doctrine": {
            "zodiac": config["doctrine"]["zodiac"],
            "ayanamsa": config["doctrine"]["ayanamsa"],
            "ayanamsa_status": config["doctrine"]["ayanamsa_status"],
            "bav_rule_set": config["doctrine"]["bav_rule_set"],
            "reductions": config["doctrine"]["reductions"],
        },
    }


def _utc_timestamp(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def build_daily_evidence(
    config: dict[str, Any],
    profile_ids: Iterable[str],
    start: Any,
    end: Any,
) -> pd.DataFrame:
    profiles = [str(item).strip() for item in profile_ids if str(item).strip()]
    if not profiles:
        raise ValueError("At least one reference profile is required")
    start_ts = _utc_timestamp(start).normalize()
    end_ts = _utc_timestamp(end).normalize()
    if end_ts <= start_ts:
        raise ValueError("End must be after start")
    dates = pd.date_range(start_ts, end_ts, freq="1D", inclusive="left")
    tables = {profile_id: natal_tables(config, profile_id) for profile_id in profiles}
    rows: list[dict[str, Any]] = []

    for ts in dates:
        signs = transit_signs(ts.to_pydatetime().astimezone(timezone.utc))
        for profile_id in profiles:
            table = tables[profile_id]
            values = transit_evidence(table["bav"], table["sav"], signs)
            rows.append(
                {
                    "timestamp_utc": ts,
                    "profile_id": profile_id,
                    "profile_status": table["profile"]["status"],
                    "doctrine_zodiac": table["doctrine"]["zodiac"],
                    "doctrine_ayanamsa": table["doctrine"]["ayanamsa"],
                    "doctrine_ayanamsa_status": table["doctrine"]["ayanamsa_status"],
                    "bav_rule_set": table["doctrine"]["bav_rule_set"],
                    "reductions": table["doctrine"]["reductions"],
                    "trade_signal_enabled": 0,
                    **values,
                }
            )
    return pd.DataFrame(rows).sort_values(["timestamp_utc", "profile_id"]).reset_index(drop=True)
