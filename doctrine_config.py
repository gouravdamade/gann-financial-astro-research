from __future__ import annotations

import copy
import warnings
from pathlib import Path
from typing import Any

import pandas as pd


DOCTRINE_CONFIG_PATH = Path(__file__).resolve().with_name("doctrine_config.yaml")

SHADBALA_MINIMUM_TOTAL_VIRUPA: dict[str, float] = {
    "SUN": 390.0,
    "MOON": 360.0,
    "MARS": 300.0,
    "MERCURY": 420.0,
    "JUPITER": 390.0,
    "VENUS": 330.0,
    "SATURN": 300.0,
}
AVG_ALL_CLASSICAL = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")

DEFAULT_DOCTRINE_CONFIG: dict[str, Any] = {
    "config_id": "doctrine_v6_20260727_visible_kaala_reconciliation",
    "status": "provisional_audited",
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
        "house_system": "porphyry_sripati_like_for_bala_provisional",
    },
    "graha_set": {
        "classical": ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"],
        "nodes": ["RAHU", "KETU"],
        "experimental_outer": ["URANUS", "NEPTUNE", "PLUTO"],
        "avg_all_policy": "experimental_context_feature",
    },
    "drishti": {
        "method": "bphs_like_longitudinal",
        "status": "event_orb_proxy_not_drik_bala",
        "current_strength_field": "event_bphs_like_orb_strength",
        "current_virupa_field": "event_bphs_like_orb_virupa",
    },
    "shadbala": {
        "method": "strict_shadbala_v9_dynamic_paksha_jhora_witness_provisional",
        "status": "provisional_independent_jhora_witness_failed_reconciliation_in_progress",
        "current_fields": ["shadbala_tag", "shadbala_avg"],
        "implemented_components": [
            "naisargika_bala",
            "uchcha_bala",
            "saptavargaja_bala",
            "ojayugma_bala",
            "kendradi_bala",
            "drekkana_bala",
            "dig_bala",
            "strict_drik_bala",
            "nathonnatha_bala",
            "paksha_bala",
            "tribhaga_bala",
            "abda_bala",
            "masa_bala",
            "vara_bala",
            "hora_bala",
            "ayana_bala",
            "yuddha_bala",
            "chesta_bala",
        ],
        "doctrine_decisions": {
            "rahu_ketu_shadbala_policy": "excluded_proxy_nodes_not_classical_shadbala_members",
            "avg_all_policy": "seven_classical_planet_component_mean",
            "saptavargaja_policy": "BPHS_source_weights_and_D1_degree_moolatrikona_with_named_PyJHora_comparator_profile",
            "tribhaga_policy": "Jupiter_permanent_60_virupa_plus_segment_lord_60_virupa",
            "kaala_abda_masa_policy": "BPHS_Ahargana_anchor_1860_sunrise_boundary_and_astronomical_rise_set",
            "paksha_policy": "dynamic_Moon_phase_and_Mercury_malefic_association_JHora_visible_witness_35_of_35",
            "chesta_policy": "sun_moon_display_only_excluded_from_total_others_mean_true_seegrocha_model",
            "luminary_chesta_total_policy": "display_carryover_excluded_to_prevent_ayana_paksha_double_count",
            "chesta_motion_policy": "eight_motion_state_speed_buckets_are_diagnostic_not_base_Chesta",
            "comparator_policy": "locked_jhora_witness_plus_pyjhora_secondary_and_named_reconciliation_profiles",
            "pyjhora_epoch_chesta_policy": "named_diagnostic_only_never_production",
            "yuddha_policy": "detect_within_1deg_candidates_and_fail_closed_pending_disc_diameter_certification",
        },
        "minimum_total_virupa": SHADBALA_MINIMUM_TOTAL_VIRUPA,
        "minimum_total_source": "BPHS Santhanam chapter 27 Shadbala minimum totals",
    },
    "drik_bala": {
        "method": "parashara_sripati_six_formula_signed",
        "status": "strict_formula_foundation",
        "rule_id": "PARASHARA_SRIPATI_DRIK_BALA_SIX_FORMULA_V1",
    },
    "panchanga": {
        "method": "deterministic_sidereal_sun_moon",
        "status": "formula_foundation_pending_traditional_validation",
        "current_fields": [
            "event_tithi_name",
            "event_paksha",
            "event_weekday_lord",
            "event_moon_nakshatra",
            "event_moon_pada",
            "event_yoga_name",
            "event_karana_name",
        ],
        "rule_id": "PANCHANGA_SIDEREAL_SUN_MOON_V1",
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
        "instrument_relative_sbc_fx_v1_execution_locked",
        "chart_conditioned_aspect_polarity_v0_execution_locked",
    ],
    "chart_conditioned_aspects": {
        "status": "experimental_isolated",
        "contract": "GANN_CHART_CONDITIONED_ASPECT_POLARITY_V0",
        "specification": "CHART_CONDITIONED_ASPECT_POLARITY_REVISED_V2_20260722",
        "implementation_root": "research_labs/chart_conditioned_aspects",
        "primary_event_stream": "explicit_transit_to_natal_only",
        "static_context": "immutable_natal_aspect_graph",
        "output_contract": ["direction", "activation", "volatility"],
        "unknown_policy": "preserve_unknown_never_impute_direction",
        "fx_pair_method": "delegate_to_instrument_relative_base_minus_quote",
        "blocked_source_profiles": [
            "TRAILOKYA_DIPIKA_1972",
            "AGARWAL_FINANCIAL_COMPLETE_EDITION",
        ],
        "execution_allowed": False,
        "promotion_allowed": False,
    },
    "source_ids": ["STRICT_VEDIC_LLM", "SHADBALA_JAYA", "BPHS", "PHALADEEPIKA", "SANJAY_RATH_CRUX_1998"],
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
        except ImportError:
            warnings.warn(
                f"PyYAML is unavailable; using the embedded doctrine fallback instead of {cfg_path}",
                RuntimeWarning,
                stacklevel=2,
            )
            return copy.deepcopy(DEFAULT_DOCTRINE_CONFIG)
        try:
            loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise RuntimeError(f"Doctrine config exists but could not be parsed: {cfg_path}") from exc
        if not isinstance(loaded, dict):
            raise RuntimeError(f"Doctrine config must contain a mapping: {cfg_path}")
        return loaded
    return copy.deepcopy(DEFAULT_DOCTRINE_CONFIG)


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
    drik_bala = cfg.get("drik_bala", {}) if isinstance(cfg.get("drik_bala"), dict) else {}
    panchanga = cfg.get("panchanga", {}) if isinstance(cfg.get("panchanga"), dict) else {}
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
        "doctrine_shadbala_status": str(shadbala.get("status", "")),
        "doctrine_shadbala_implemented_components": "|".join(
            str(item) for item in shadbala.get("implemented_components", [])
        ),
        "doctrine_strict_drik_bala_method": str(drik_bala.get("method", "")),
        "doctrine_strict_drik_bala_status": str(drik_bala.get("status", "")),
        "doctrine_strict_drik_bala_rule_id": str(drik_bala.get("rule_id", "")),
        "doctrine_panchanga_method": str(panchanga.get("method", "")),
        "doctrine_panchanga_status": str(panchanga.get("status", "")),
        "doctrine_panchanga_rule_id": str(panchanga.get("rule_id", "")),
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
        additions["shadbala_doctrine_status"] = str(
            (config or load_doctrine_config()).get("shadbala", {}).get(
                "status",
                "provisional_source_aligned_components_pending_external_validation",
            )
        )
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
