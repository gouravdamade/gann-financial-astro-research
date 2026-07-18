from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ExperimentalProfile:
    profile_id: str
    status: str
    no_edge_threshold: float
    component_weights: dict[str, float]
    require_explanations: bool
    require_source_locator_for_verified_rules: bool
    prohibit_unreviewed_akshara_as_ground_truth: bool
    pair_method: str
    execution_allowed: bool
    promotion_allowed: bool


def load_experimental_profile(path: str | Path) -> ExperimentalProfile:
    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    requirements = dict(raw.get("requirements") or {})
    pair = dict(raw.get("pair_model") or {})
    profile = ExperimentalProfile(
        profile_id=str(raw.get("profile_id") or "").strip(),
        status=str(raw.get("status") or "").strip(),
        no_edge_threshold=float(raw.get("no_edge_threshold")),
        component_weights={
            str(key): float(value)
            for key, value in dict(raw.get("component_weights") or {}).items()
        },
        require_explanations=bool(requirements.get("require_explanations")),
        require_source_locator_for_verified_rules=bool(
            requirements.get("require_source_locator_for_verified_rules")
        ),
        prohibit_unreviewed_akshara_as_ground_truth=bool(
            requirements.get("prohibit_unreviewed_akshara_as_ground_truth")
        ),
        pair_method=str(pair.get("method") or "").strip(),
        execution_allowed=bool(raw.get("execution_allowed")),
        promotion_allowed=bool(raw.get("promotion_allowed")),
    )
    if not profile.profile_id:
        raise ValueError("profile_id is required")
    if profile.status != "experimental":
        raise ValueError("instrument-relative profile must remain experimental")
    if profile.no_edge_threshold < 0:
        raise ValueError("no_edge_threshold must be non-negative")
    if profile.pair_method != "latent_currency_difference":
        raise ValueError("only latent_currency_difference is allowed")
    if profile.execution_allowed or profile.promotion_allowed:
        raise ValueError("experimental profile cannot enable execution or promotion")
    return profile
