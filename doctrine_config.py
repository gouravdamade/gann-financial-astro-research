from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


DOCTRINE_CONFIG_PATH = Path(__file__).resolve().with_name("doctrine_config.yaml")

SHADBALA_MINIMUM_TOTAL_VIRUPA: dict[str, float] = {
    "SUN": 300.0,
    "MOON": 360.0,
    "MARS": 300.0,
    "MERCURY": 420.0,
    "JUPITER": 390.0,
    "VENUS": 330.0,
    "SATURN": 300.0,
}
AVG_ALL_CLASSICAL = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")

DEFAULT_DOCTRINE_CONFIG: dict[str, Any] = {
    "config_id": "doctrine_v1_20260521",
    "status": "foundation",
    "time_standard": {
        "internal_time": "UTC/JD_UT",
        "display_time": "Asia/Kolkata",
    },
    "astronomy": {
        "zodiac": "sidereal",
        "ayanamsa": "Raman",
        "ayanamsa_swiss_ephemeris_id": "SIDM_RAMAN",
        "node_type": "true_node",
        "coordinate_system": "geocentric",
        "ephemeris_provider": "swiss_ephemeris",
        "house_system": "existing_reference_engine",
    },
    "graha_set": {
        "classical": ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"],
        "nodes": ["RAHU", "KETU"],
        "experimental_outer": ["URANUS", "NEPTUNE", "PLUTO"],
        "avg_all_policy": "experimental_context_feature",
    },
    "drishti": {
        "method": "bphs_like_longitudinal",
        "status": "proxy_pending_strict_drik_bala",
        "current_strength_field": "event_bphs_like_orb_strength",
        "current_virupa_field": "event_bphs_like_orb_virupa",
    },
    "shadbala": {
        "method": "proxy_pending_full_shadbala",
        "current_fields": ["shadbala_tag", "shadbala_avg"],
        "minimum_total_virupa": SHADBALA_MINIMUM_TOTAL_VIRUPA,
        "minimum_total_source": "SHADBALA_JAYA lines 743-745",
    },
    "rule_layer": {
        "status": "heuristic_doctrine_v1",
        "ml_scope": "calibrate_weights_thresholds_and_interactions_only",
        "llm_scope": "explanation_with_citations_only",
        "rule_citation_status": "pending",
    },
    "experimental_layers": [
        "financial_astrology_orb_windows",
        "support_resistance_planetary_lines",
        "gann_research_context",
        "usdjpy_base_minus_quote_score",
        "repeatation_manual_marker_review",
    ],
    "source_ids": ["STRICT_VEDIC_LLM", "SHADBALA_JAYA"],
}

AYANAMSA_SWISSEPH_IDS: dict[str, str] = {
    "fagan": "SIDM_FAGAN_BRADLEY",
    "fagan_bradley": "SIDM_FAGAN_BRADLEY",
    "lahiri": "SIDM_LAHIRI",
    "chitrapaksha": "SIDM_LAHIRI",
    "raman": "SIDM_RAMAN",
}


def load_doctrine_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DOCTRINE_CONFIG_PATH
    if cfg_path.exists():
        try:
            import yaml  # type: ignore

            loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                return loaded
        except Exception:
            pass
    return DEFAULT_DOCTRINE_CONFIG.copy()


def doctrine_ayanamsa_name(config: dict[str, Any] | None = None) -> str:
    cfg = config or load_doctrine_config()
    astronomy = cfg.get("astronomy", {}) if isinstance(cfg.get("astronomy"), dict) else {}
    name = str(astronomy.get("ayanamsa", "Raman")).strip()
    return name or "Raman"


def doctrine_ayanamsa_swe_id(config: dict[str, Any] | None = None) -> str:
    cfg = config or load_doctrine_config()
    astronomy = cfg.get("astronomy", {}) if isinstance(cfg.get("astronomy"), dict) else {}
    explicit = str(astronomy.get("ayanamsa_swiss_ephemeris_id", "")).strip()
    if explicit:
        return explicit
    key = doctrine_ayanamsa_name(cfg).strip().lower().replace("-", "_").replace(" ", "_")
    return AYANAMSA_SWISSEPH_IDS.get(key, "SIDM_RAMAN")


def configure_swiss_ephemeris_sidereal(swe_module: Any, config: dict[str, Any] | None = None) -> str:
    """Apply the doctrine-locked sidereal mode to a Swiss Ephemeris module."""
    swe_id = doctrine_ayanamsa_swe_id(config)
    mode = getattr(swe_module, swe_id, None)
    if mode is None:
        raise ValueError(f"Swiss Ephemeris ayanamsa constant not available: {swe_id}")
    swe_module.set_sid_mode(mode)
    return doctrine_ayanamsa_name(config)


def doctrine_metadata_columns(config: dict[str, Any] | None = None) -> dict[str, str]:
    cfg = config or load_doctrine_config()
    astronomy = cfg.get("astronomy", {}) if isinstance(cfg.get("astronomy"), dict) else {}
    drishti = cfg.get("drishti", {}) if isinstance(cfg.get("drishti"), dict) else {}
    shadbala = cfg.get("shadbala", {}) if isinstance(cfg.get("shadbala"), dict) else {}
    rule_layer = cfg.get("rule_layer", {}) if isinstance(cfg.get("rule_layer"), dict) else {}
    experimental_layers = cfg.get("experimental_layers", [])
    source_ids = cfg.get("source_ids", [])
    return {
        "doctrine_config_id": str(cfg.get("config_id", "")),
        "doctrine_config_status": str(cfg.get("status", "")),
        "doctrine_zodiac": str(astronomy.get("zodiac", "")),
        "doctrine_ayanamsa": str(astronomy.get("ayanamsa", "")),
        "doctrine_ayanamsa_swiss_ephemeris_id": str(astronomy.get("ayanamsa_swiss_ephemeris_id", "")),
        "doctrine_node_type": str(astronomy.get("node_type", "")),
        "doctrine_coordinate_system": str(astronomy.get("coordinate_system", "")),
        "doctrine_ephemeris_provider": str(astronomy.get("ephemeris_provider", "")),
        "doctrine_house_system": str(astronomy.get("house_system", "")),
        "doctrine_drishti_method": str(drishti.get("method", "")),
        "doctrine_drishti_status": str(drishti.get("status", "")),
        "doctrine_shadbala_method": str(shadbala.get("method", "")),
        "doctrine_rule_layer_status": str(rule_layer.get("status", "")),
        "doctrine_rule_citation_status": str(rule_layer.get("rule_citation_status", "")),
        "doctrine_ml_scope": str(rule_layer.get("ml_scope", "")),
        "doctrine_llm_scope": str(rule_layer.get("llm_scope", "")),
        "doctrine_source_ids": "|".join(str(item) for item in source_ids),
        "experimental_layer_flags": "|".join(str(item) for item in experimental_layers),
    }


def append_doctrine_metadata(frame: Any, config: dict[str, Any] | None = None) -> Any:
    additions: dict[str, Any] = {col: value for col, value in doctrine_metadata_columns(config).items()}
    if "event_bphs_strength" in frame.columns and "event_bphs_like_orb_strength" not in frame.columns:
        additions["event_bphs_like_orb_strength"] = frame["event_bphs_strength"]
    if "event_bphs_virupa" in frame.columns and "event_bphs_like_orb_virupa" not in frame.columns:
        additions["event_bphs_like_orb_virupa"] = frame["event_bphs_virupa"]
    if "event_bphs_strength" in frame.columns:
        additions["event_strength_doctrine_status"] = "bphs_like_orb_proxy_not_full_drik_bala"
    if "shadbala_tag" in frame.columns or "shadbala_avg" in frame.columns:
        additions["shadbala_doctrine_status"] = "source_or_proxy_pending_full_six_bala_calculation"
    if {"b1", "b2", "shadbala_avg"}.issubset(set(frame.columns)):
        minimum_avg = frame.apply(_row_minimum_shadbala_avg, axis=1)
        additions["event_shadbala_minimum_total_virupa_avg"] = minimum_avg
        try:
            shadbala_avg = frame["shadbala_avg"].astype(float)
            comparable = shadbala_avg > 100.0
            additions["event_shadbala_avg_minus_minimum_virupa"] = (
                shadbala_avg - pd.Series(minimum_avg, index=frame.index).astype(float)
            ).where(comparable, "")
            additions["event_shadbala_avg_scale_status"] = comparable.map(
                {True: "total_virupa_comparable", False: "not_total_virupa_or_unknown"}
            )
        except Exception:
            additions["event_shadbala_avg_minus_minimum_virupa"] = ""
            additions["event_shadbala_avg_scale_status"] = "not_total_virupa_or_unknown"
        additions["event_shadbala_minimum_source"] = "SHADBALA_JAYA_lines_743_745"
    additions = {key: value for key, value in additions.items() if key not in frame.columns}
    if not additions:
        return frame
    return pd.concat([frame, pd.DataFrame(additions, index=frame.index)], axis=1)


def _minimum_shadbala_for_body(value: Any) -> float | None:
    body = str(value or "").strip().upper()
    if body in {"AVG(ALL)", "AVG_ALL", "ALL"}:
        values = [SHADBALA_MINIMUM_TOTAL_VIRUPA[item] for item in AVG_ALL_CLASSICAL]
        return sum(values) / len(values)
    return SHADBALA_MINIMUM_TOTAL_VIRUPA.get(body)


def _row_minimum_shadbala_avg(row: Any) -> float | str:
    values = []
    for key in ("b1", "b2"):
        minimum = _minimum_shadbala_for_body(row.get(key))
        if minimum is not None:
            values.append(float(minimum))
    if not values:
        return ""
    return sum(values) / len(values)
