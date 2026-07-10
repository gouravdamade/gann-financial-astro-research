from __future__ import annotations

import json
from datetime import timezone
from typing import Any

import pandas as pd

from research_labs.ashtakavarga_validation.ashtakavarga_lab.config import load_config
from research_labs.ashtakavarga_validation.ashtakavarga_lab.core import transit_evidence
from research_labs.ashtakavarga_validation.ashtakavarga_lab.dasha import dasha_at, nakshatra_index, nakshatra_lord
from research_labs.ashtakavarga_validation.ashtakavarga_lab.ephemeris import (
    configure,
    sidereal_longitudes,
    transit_signs,
)
from research_labs.ashtakavarga_validation.ashtakavarga_lab.kas import SIGN_LORDS
from research_labs.ashtakavarga_validation.ashtakavarga_lab.kas_evidence import (
    antardasha_evidence,
    profile_kas_context,
)


def _utc_timestamp(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _ordinal(value: float, center: float, center_is_positive: bool = False) -> int:
    if value > center or (center_is_positive and value == center):
        return 1
    if value < center:
        return -1
    return 0


def _vote_summary(votes: list[str], denominator: int = 12) -> dict[str, Any]:
    bullish = votes.count("BULLISH")
    bearish = votes.count("BEARISH")
    neutral = votes.count("NEUTRAL")
    if bullish == bearish:
        suggestion = "MIXED" if bullish else "NEUTRAL"
    else:
        suggestion = "BULLISH" if bullish > bearish else "BEARISH"
    agreement = max(bullish, bearish) / max(1, int(denominator))
    return {
        "suggestion": suggestion,
        "bullish": bullish,
        "bearish": bearish,
        "neutral": neutral,
        "agreement_fraction": round(agreement, 6),
        "agreement_percent": round(agreement * 100.0, 1),
    }


class KrushnaKasAdvisoryEngine:
    """Read-only KAS vote adapter for review UI context.

    The adapter intentionally has no methods for orders, marker placement, ML notes,
    rule selection, or Auto Suggest. Its output carries explicit non-trading locks.
    """

    def __init__(self, base_profile: str = "usd_reference", quote_profile: str = "jpy_reference") -> None:
        self.config = load_config()
        configure(self.config)
        self.base_profile = str(base_profile)
        self.quote_profile = str(quote_profile)
        self.contexts = {
            profile_id: profile_kas_context(self.config, profile_id)
            for profile_id in (self.base_profile, self.quote_profile)
        }

    def _profile_house_rows(self, profile_id: str, moment: pd.Timestamp) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
        context = self.contexts[profile_id]
        dt = moment.to_pydatetime().astimezone(timezone.utc)
        transit_lons = sidereal_longitudes(dt)
        transits = transit_signs(dt)
        transit = transit_evidence(context["bav"], context["sav"], transits)
        dasha = dasha_at(context["birth"], context["profile"]["longitudes"]["MOON"], dt)
        ad_lord = dasha["antardasha"]["lord"]
        sun_sign = transits["SUN"]
        sun_nak = nakshatra_index(transit_lons["SUN"]) + 1
        sun_nak_lord = nakshatra_lord(transit_lons["SUN"])
        sav_disposition = _ordinal(transit["seven_planet_sav_total"], 196)
        js_disposition = _ordinal(transit["jupiter_saturn_own_bav_sum"], 8, center_is_positive=True)
        rows: dict[int, dict[str, Any]] = {}
        for house_b, worksheet in context["worksheets"].items():
            ad = antardasha_evidence(worksheet, ad_lord, context["node_proxies"])
            candidates = set(worksheet["direct_timing_candidates"]) | set(
                worksheet["samdharmi_substitute_candidates"]
            )
            sign_hits = sorted(
                planet for planet in candidates if context["profile"]["signs"][planet] == sun_sign
            )
            nak_hits = sorted(planet for planet in candidates if context["nakshatras"][planet] == sun_nak)
            sign_lord_hit = SIGN_LORDS[sun_sign] if SIGN_LORDS[sun_sign] in candidates else ""
            nak_lord_hit = sun_nak_lord if sun_nak_lord in candidates else ""
            sun_trigger = bool(sign_hits or nak_hits or sign_lord_hit or nak_lord_hit)
            rows[int(house_b)] = {
                "house_b": int(house_b),
                "antardasha_score": ad["antardasha_effective_score"],
                "antardasha_disposition": ad["antardasha_disposition"],
                "antardasha_eligible": ad["antardasha_eligible"],
                "sav_disposition": sav_disposition,
                "js_disposition": js_disposition,
                "full_context_score": ad["antardasha_disposition"] + sav_disposition + js_disposition,
                "sun_trigger": int(sun_trigger),
                "sun_trigger_planets": sorted(set(sign_hits + nak_hits + [sign_lord_hit, nak_lord_hit]) - {""}),
                "top_planet": worksheet["ranking"][0],
                "top_score": worksheet["row17_final_strength"][worksheet["ranking"][0]],
            }
        timing = {
            "mahadasha_lord": dasha["mahadasha"]["lord"],
            "antardasha_lord": ad_lord,
            "antardasha_sector": dasha["sector"]["sector"],
            "antardasha_sector_label": dasha["sector"]["label"],
            "seven_planet_sav_total": transit["seven_planet_sav_total"],
            "jupiter_saturn_own_bav_sum": transit["jupiter_saturn_own_bav_sum"],
        }
        return rows, timing

    def advisory_at(self, value: Any) -> dict[str, Any]:
        moment = _utc_timestamp(value)
        base_rows, base_timing = self._profile_house_rows(self.base_profile, moment)
        quote_rows, quote_timing = self._profile_house_rows(self.quote_profile, moment)
        house_votes = []
        votes = []
        sun_votes = []
        for house_b in range(1, 13):
            base = base_rows[house_b]
            quote = quote_rows[house_b]
            difference = int(base["full_context_score"] - quote["full_context_score"])
            direction = "BULLISH" if difference > 0 else ("BEARISH" if difference < 0 else "NEUTRAL")
            sun_timed = bool(base["sun_trigger"] or quote["sun_trigger"])
            votes.append(direction)
            if sun_timed:
                sun_votes.append(direction)
            house_votes.append(
                {
                    "house_b": house_b,
                    "direction": direction,
                    "pair_score": difference,
                    "usd_score": base["full_context_score"],
                    "jpy_score": quote["full_context_score"],
                    "sun_timed": int(sun_timed),
                    "usd_antardasha_score": base["antardasha_score"],
                    "jpy_antardasha_score": quote["antardasha_score"],
                }
            )
        all_votes = _vote_summary(votes)
        sun_summary = _vote_summary(sun_votes, denominator=len(sun_votes)) if sun_votes else {
            "suggestion": "NO_TRIGGER",
            "bullish": 0,
            "bearish": 0,
            "neutral": 0,
            "agreement_fraction": 0.0,
            "agreement_percent": 0.0,
        }
        return {
            "status": "experimental_suggestion_only",
            "methodology": "corrected_kas_raman_adaptation_all_12_house_vote_v1",
            "evaluation_time_utc": moment.isoformat(),
            "suggestion": all_votes["suggestion"],
            "bullish_house_count": all_votes["bullish"],
            "bearish_house_count": all_votes["bearish"],
            "neutral_house_count": all_votes["neutral"],
            "agreement_percent": all_votes["agreement_percent"],
            "sun_timed_suggestion": sun_summary["suggestion"],
            "sun_timed_house_count": len(sun_votes),
            "sun_timed_bullish_count": sun_summary["bullish"],
            "sun_timed_bearish_count": sun_summary["bearish"],
            "sun_timed_neutral_count": sun_summary["neutral"],
            "sun_timed_agreement_percent": sun_summary["agreement_percent"],
            "usd_timing": base_timing,
            "jpy_timing": quote_timing,
            "house_votes": house_votes,
            "house_votes_json": json.dumps(house_votes, separators=(",", ":")),
            "validation_status": "first_usdjpy_run_no_robust_edge",
            "warning": "Research suggestion only. It did not pass full multiple-testing/placebo/cost validation.",
            "evidence_only": 1,
            "trade_signal_enabled": 0,
            "trade_override_allowed": 0,
            "auto_suggest_input": 0,
            "ml_training_input": 0,
            "mt5_input": 0,
        }


def unavailable_advisory(error: Any) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "suggestion": "UNAVAILABLE",
        "warning": str(error),
        "evidence_only": 1,
        "trade_signal_enabled": 0,
        "trade_override_allowed": 0,
        "auto_suggest_input": 0,
        "ml_training_input": 0,
        "mt5_input": 0,
    }

