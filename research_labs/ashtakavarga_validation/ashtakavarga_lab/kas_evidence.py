from __future__ import annotations

from datetime import timezone
from typing import Any

import pandas as pd

from .config import profile as get_profile
from .core import compute_bav, compute_sav, sign_name, transit_evidence
from .dasha import dasha_at, nakshatra_index, nakshatra_lord
from .ephemeris import (
    natal_context,
    parse_local_datetime,
    sidereal_longitudes,
    sidereal_node_longitudes,
    transit_signs,
)
from .kas import SIGN_LORDS, corrected_event_worksheet


def navamsa_sign(longitude: float) -> int:
    lon = float(longitude) % 360.0
    rasi = int(lon // 30.0) + 1
    pada = int((lon % 30.0) // (30.0 / 9.0))
    if rasi in {1, 4, 7, 10}:
        start = rasi
    elif rasi in {2, 5, 8, 11}:
        start = ((rasi - 1 + 8) % 12) + 1
    else:
        start = ((rasi - 1 + 4) % 12) + 1
    return ((start - 1 + pada) % 12) + 1


def node_proxies(
    node_longitude: float,
    classical_longitudes: dict[str, float],
) -> dict[str, Any]:
    sign = int((float(node_longitude) % 360.0) // 30.0) + 1
    navamsa = navamsa_sign(node_longitude)
    proxies = {
        SIGN_LORDS[sign],
        nakshatra_lord(node_longitude),
        SIGN_LORDS[navamsa],
    }
    conjunctions = sorted(
        planet for planet, longitude in classical_longitudes.items() if navamsa_sign(longitude) == navamsa
    )
    proxies.update(conjunctions)
    return {
        "sign": sign,
        "sign_name": sign_name(sign),
        "nakshatra_index": nakshatra_index(node_longitude) + 1,
        "navamsa_sign": navamsa,
        "navamsa_conjunctions": conjunctions,
        "proxies": sorted(proxies),
    }


def profile_kas_context(config: dict[str, Any], profile_id: str) -> dict[str, Any]:
    configured = get_profile(config, profile_id)
    context = natal_context(profile_id, configured)
    bdate = parse_local_datetime(configured)
    nodes = sidereal_node_longitudes(bdate)
    bav = compute_bav(context["signs"])
    sav = compute_sav(bav)
    longitudes = context["longitudes"]
    nakshatras = {planet: nakshatra_index(lon) + 1 for planet, lon in longitudes.items()}
    navamsas = {planet: navamsa_sign(lon) for planet, lon in longitudes.items()}
    worksheets = {
        house: corrected_event_worksheet(
            bav,
            context["signs"],
            context["signs"]["LAGNA"],
            house,
            nakshatras=nakshatras,
            navamsa_signs=navamsas,
        )
        for house in range(1, 13)
    }
    return {
        "profile": context,
        "birth": bdate,
        "bav": bav,
        "sav": sav,
        "worksheets": worksheets,
        "nakshatras": nakshatras,
        "navamsas": navamsas,
        "node_longitudes": nodes,
        "node_proxies": {
            node: node_proxies(longitude, longitudes) for node, longitude in nodes.items()
        },
    }


def _ordinal(value: float, center: float, exact_center_positive: bool = False) -> int:
    if value > center or (exact_center_positive and value == center):
        return 1
    if value < center:
        return -1
    return 0


def antardasha_evidence(worksheet: dict[str, Any], ad_lord: str, proxies: dict[str, Any]) -> dict[str, Any]:
    scores = worksheet["row17_final_strength"]
    candidates = set(worksheet["direct_timing_candidates"]) | set(worksheet["samdharmi_substitute_candidates"])
    if ad_lord in scores:
        score = scores[ad_lord]
        eligible = ad_lord in candidates
        proxy_planets = []
    else:
        proxy_planets = list(proxies[ad_lord]["proxies"])
        proxy_scores = [scores[planet] for planet in proxy_planets]
        score = min(proxy_scores) if proxy_scores else None
        eligible = bool(proxy_scores) and all(value > 12 for value in proxy_scores)
    disposition = 1 if score is not None and score > 12 and eligible else (-1 if score is not None and score < 12 else 0)
    return {
        "antardasha_lord": ad_lord,
        "antardasha_effective_score": score,
        "antardasha_eligible": int(eligible),
        "antardasha_disposition": disposition,
        "antardasha_proxy_planets": "|".join(proxy_planets),
    }


def build_daily_kas_evidence(
    config: dict[str, Any],
    profile_ids: list[str],
    start: Any,
    end: Any,
) -> pd.DataFrame:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    start_ts = start_ts.tz_localize("UTC") if start_ts.tzinfo is None else start_ts.tz_convert("UTC")
    end_ts = end_ts.tz_localize("UTC") if end_ts.tzinfo is None else end_ts.tz_convert("UTC")
    dates = pd.date_range(start_ts.normalize(), end_ts.normalize(), freq="1D", inclusive="left")
    contexts = {profile_id: profile_kas_context(config, profile_id) for profile_id in profile_ids}
    rows: list[dict[str, Any]] = []
    for ts in dates:
        moment = ts.to_pydatetime().astimezone(timezone.utc)
        transits = transit_signs(moment)
        transit_lons = sidereal_longitudes(moment)
        sun_sign = transits["SUN"]
        sun_nakshatra = nakshatra_index(transit_lons["SUN"]) + 1
        for profile_id, context in contexts.items():
            transit = transit_evidence(context["bav"], context["sav"], transits)
            dasha = dasha_at(context["birth"], context["profile"]["longitudes"]["MOON"], moment)
            md_lord = dasha["mahadasha"]["lord"]
            ad_lord = dasha["antardasha"]["lord"]
            for house_b, worksheet in context["worksheets"].items():
                ad = antardasha_evidence(worksheet, ad_lord, context["node_proxies"])
                candidates = set(worksheet["direct_timing_candidates"]) | set(
                    worksheet["samdharmi_substitute_candidates"]
                )
                sign_hits = sorted(
                    planet for planet in candidates if context["profile"]["signs"][planet] == sun_sign
                )
                nakshatra_hits = sorted(
                    planet for planet in candidates if context["nakshatras"][planet] == sun_nakshatra
                )
                sun_sign_lord_hit = SIGN_LORDS[sun_sign] if SIGN_LORDS[sun_sign] in candidates else ""
                sun_nakshatra_lord = nakshatra_lord(transit_lons["SUN"])
                sun_nakshatra_lord_hit = sun_nakshatra_lord if sun_nakshatra_lord in candidates else ""
                sun_trigger = bool(sign_hits or nakshatra_hits or sun_sign_lord_hit or sun_nakshatra_lord_hit)
                sav_disposition = _ordinal(transit["seven_planet_sav_total"], 196)
                js_disposition = _ordinal(transit["jupiter_saturn_own_bav_sum"], 8, exact_center_positive=True)
                full_score = ad["antardasha_disposition"] + sav_disposition + js_disposition
                rows.append(
                    {
                        "timestamp_utc": ts,
                        "profile_id": profile_id,
                        "house_b": house_b,
                        "profile_status": context["profile"]["status"],
                        "methodology": "corrected_kas_raman_adaptation_v1",
                        "trade_signal_enabled": 0,
                        "mahadasha_lord": md_lord,
                        **ad,
                        "antardasha_sector": dasha["sector"]["sector"],
                        "antardasha_sector_label": dasha["sector"]["label"],
                        "sun_trigger": int(sun_trigger),
                        "sun_trigger_sign_planets": "|".join(sign_hits),
                        "sun_trigger_nakshatra_planets": "|".join(nakshatra_hits),
                        "sun_trigger_sign_lord": sun_sign_lord_hit,
                        "sun_trigger_nakshatra_lord": sun_nakshatra_lord_hit,
                        "sav_disposition": sav_disposition,
                        "js_disposition": js_disposition,
                        "kas_full_context_score": full_score,
                        "worksheet_top_planet": worksheet["ranking"][0],
                        "worksheet_top_score": worksheet["row17_final_strength"][worksheet["ranking"][0]],
                        "lesson26_top_planet": worksheet["lesson26_ranking"][0],
                        "lesson26_top_strength": worksheet["lesson26_multiplied_result_strength"][
                            worksheet["lesson26_ranking"][0]
                        ],
                        "worksheet_direct_candidates": "|".join(worksheet["direct_timing_candidates"]),
                        "worksheet_substitute_candidates": "|".join(
                            worksheet["samdharmi_substitute_candidates"]
                        ),
                        **transit,
                    }
                )
    return pd.DataFrame(rows).sort_values(["timestamp_utc", "profile_id", "house_b"]).reset_index(drop=True)
