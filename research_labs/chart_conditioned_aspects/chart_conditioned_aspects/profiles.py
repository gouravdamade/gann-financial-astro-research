from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import stable_hash


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = PACKAGE_ROOT / "profiles"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"profile root must be a mapping: {path}")
    return raw


def _locked(raw: dict[str, Any], label: str) -> None:
    if raw.get("execution_allowed") is not False:
        raise ValueError(f"{label} must keep execution_allowed=false")
    if raw.get("promotion_allowed") is not False:
        raise ValueError(f"{label} must keep promotion_allowed=false")


@dataclass(frozen=True)
class ResearchProfiles:
    lordship: dict[str, Any]
    domains: dict[str, Any]
    graph: dict[str, Any]
    aspects: dict[str, Any]
    manifest: dict[str, Any]
    profile_hash: str


def load_research_profiles(root: Path | None = None) -> ResearchProfiles:
    base = root or PROFILE_ROOT
    lordship = _load_yaml(base / "parashari_org_v0.yaml")
    domains = _load_yaml(base / "financial_domains_v0.yaml")
    graph = _load_yaml(base / "natal_graph_v0.yaml")
    aspects = _load_yaml(base / "aspect_strength_v0.yaml")
    manifest = _load_yaml(base / "source_manifest.yaml")
    for label, raw in (
        ("lordship profile", lordship),
        ("domain profile", domains),
        ("graph profile", graph),
        ("aspect profile", aspects),
        ("source manifest", manifest),
    ):
        _locked(raw, label)
    if graph.get("configured_drishti_enabled") is not False:
        raise ValueError(
            "Milestone 1 graph profile must keep configured drishti disabled"
        )
    if graph.get("yoga_edges_enabled") is not False:
        raise ValueError("Milestone 1 graph profile must keep yoga edges disabled")
    blocked = set(str(item) for item in manifest.get("blocked_source_profiles", []))
    required_blocks = {
        "TRAILOKYA_DIPIKA_ARGHYA_FINANCIAL_PROFILE",
        "AGARWAL_FINANCIAL_COMPLETE_EDITION",
    }
    if not required_blocks.issubset(blocked):
        raise ValueError(
            "uncertified financial source profiles must remain explicitly blocked"
        )
    payload = {
        "lordship": lordship,
        "domains": domains,
        "graph": graph,
        "aspects": aspects,
        "manifest": manifest,
    }
    return ResearchProfiles(
        lordship=lordship,
        domains=domains,
        graph=graph,
        aspects=aspects,
        manifest=manifest,
        profile_hash=stable_hash(payload),
    )
