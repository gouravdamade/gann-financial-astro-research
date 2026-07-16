from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .enums import (
    AbhijitPolicy,
    Ayanamsha,
    Center,
    EphemerisFallbackPolicy,
    NodeType,
    VaraBoundary,
    ZodiacMode,
)
from .models import AbhijitInterval, AstroSettings, PanchangaSettings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = PROJECT_ROOT / "configs" / "sbc"
PROFILE_ROOT = CONFIG_ROOT / "profiles"
SOURCE_REGISTER_PATH = CONFIG_ROOT / "sources.yaml"

PROFILE_KEYS = {
    "schema_version",
    "profile_id",
    "status",
    "authority",
    "phase",
    "astronomy",
    "panchanga",
    "features",
    "source_ids",
    "notes",
}
ASTRONOMY_KEYS = {"zodiac", "ayanamsha", "center", "node", "fallback_policy"}
PANCHANGA_KEYS = {
    "timezone",
    "vara_boundary",
    "abhijit_policy",
    "abhijit_interval",
    "sunrise_algorithm",
}
ABHIJIT_INTERVAL_KEYS = {
    "start_deg",
    "end_deg",
    "source_rule_id",
    "start_inclusive",
    "end_inclusive",
}
FEATURE_KEYS = {"positions", "panchanga", "grid", "vedha", "latta", "scoring", "trades"}
SOURCE_REGISTER_KEYS = {"schema_version", "register_id", "sources"}
SOURCE_KEYS = {
    "source_id",
    "title",
    "authority",
    "content_layer",
    "status",
    "rights_status",
    "sha256",
    "registry_ref",
    "source_url",
    "notes",
}


@dataclass(frozen=True)
class CompiledProfile:
    profile_id: str
    profile_hash: str
    status: str
    authority: str
    phase: int
    astro_settings: AstroSettings
    panchanga_settings: PanchangaSettings
    features: dict[str, bool]
    source_ids: tuple[str, ...]
    raw: dict[str, Any]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return loaded


def _reject_unknown(mapping: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label} fields: {', '.join(unknown)}")


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def validate_source_register(register: dict[str, Any]) -> dict[str, Any]:
    _reject_unknown(register, SOURCE_REGISTER_KEYS, "source register")
    if int(register.get("schema_version", 0)) != 1:
        raise ValueError("source register schema_version must be 1")
    if not str(register.get("register_id", "")).strip():
        raise ValueError("source register_id is required")
    sources = register.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source register requires at least one source")
    seen: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("every source must be a mapping")
        _reject_unknown(source, SOURCE_KEYS, "source")
        source_id = str(source.get("source_id", "")).strip()
        if not source_id or source_id in seen:
            raise ValueError(f"source_id is missing or duplicated: {source_id!r}")
        seen.add(source_id)
        for required in ("title", "authority", "content_layer", "status", "rights_status"):
            if not str(source.get(required, "")).strip():
                raise ValueError(f"{source_id} requires {required}")
        digest = source.get("sha256")
        if digest is not None and (len(str(digest)) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in str(digest))):
            raise ValueError(f"{source_id} has an invalid SHA-256")
    return register


def load_source_register(path: Path | None = None) -> dict[str, Any]:
    return validate_source_register(_load_yaml(path or SOURCE_REGISTER_PATH))


def validate_profile(raw: dict[str, Any], source_register: dict[str, Any] | None = None) -> CompiledProfile:
    _reject_unknown(raw, PROFILE_KEYS, "profile")
    if int(raw.get("schema_version", 0)) != 1:
        raise ValueError("profile schema_version must be 1")
    profile_id = str(raw.get("profile_id", "")).strip()
    if not profile_id:
        raise ValueError("profile_id is required")
    phase = int(raw.get("phase", 0))
    if phase != 1:
        raise ValueError("this compiler accepts Phase 1 foundation profiles only")

    astronomy = raw.get("astronomy")
    panchanga = raw.get("panchanga")
    features = raw.get("features")
    if not isinstance(astronomy, dict) or not isinstance(panchanga, dict) or not isinstance(features, dict):
        raise ValueError("astronomy, panchanga, and features must be mappings")
    _reject_unknown(astronomy, ASTRONOMY_KEYS, "astronomy")
    _reject_unknown(panchanga, PANCHANGA_KEYS, "panchanga")
    _reject_unknown(features, FEATURE_KEYS, "feature")

    feature_flags = {key: bool(features.get(key, False)) for key in FEATURE_KEYS}
    if not feature_flags["positions"] or not feature_flags["panchanga"]:
        raise ValueError("Phase 1 requires positions and panchanga")
    for forbidden in ("grid", "vedha", "latta", "scoring", "trades"):
        if feature_flags[forbidden]:
            raise ValueError(f"Phase 1 profile cannot enable {forbidden}")

    interval_raw = panchanga.get("abhijit_interval")
    interval = None
    if interval_raw is not None:
        if not isinstance(interval_raw, dict):
            raise ValueError("abhijit_interval must be null or a mapping")
        _reject_unknown(interval_raw, ABHIJIT_INTERVAL_KEYS, "Abhijit interval")
        interval = AbhijitInterval(
            start_deg=float(interval_raw["start_deg"]),
            end_deg=float(interval_raw["end_deg"]),
            source_rule_id=str(interval_raw["source_rule_id"]),
            start_inclusive=bool(interval_raw.get("start_inclusive", True)),
            end_inclusive=bool(interval_raw.get("end_inclusive", False)),
        )

    abhijit_policy = AbhijitPolicy(str(panchanga["abhijit_policy"]))
    if abhijit_policy is not AbhijitPolicy.IGNORE_FOR_PLANET_PLACEMENT and interval is None:
        raise ValueError("selected Abhijit policy requires a source-cited interval")

    source_ids = tuple(str(item) for item in raw.get("source_ids", []))
    register = source_register or load_source_register()
    known_source_ids = {str(item["source_id"]) for item in register["sources"]}
    unresolved = sorted(set(source_ids) - known_source_ids)
    if unresolved:
        raise ValueError(f"profile has unresolved source IDs: {', '.join(unresolved)}")

    return CompiledProfile(
        profile_id=profile_id,
        profile_hash=_canonical_hash(raw),
        status=str(raw.get("status", "")),
        authority=str(raw.get("authority", "")),
        phase=phase,
        astro_settings=AstroSettings(
            zodiac=ZodiacMode(str(astronomy["zodiac"])),
            ayanamsha=Ayanamsha(str(astronomy["ayanamsha"])),
            center=Center(str(astronomy["center"])),
            node=NodeType(str(astronomy["node"])),
            fallback_policy=EphemerisFallbackPolicy(str(astronomy["fallback_policy"])),
        ),
        panchanga_settings=PanchangaSettings(
            timezone=str(panchanga["timezone"]),
            vara_boundary=VaraBoundary(str(panchanga["vara_boundary"])),
            abhijit_policy=abhijit_policy,
            abhijit_interval=interval,
            sunrise_algorithm=str(panchanga["sunrise_algorithm"]),
        ),
        features=feature_flags,
        source_ids=source_ids,
        raw=raw,
    )


def load_profile(profile_id: str, profile_root: Path | None = None) -> CompiledProfile:
    root = profile_root or PROFILE_ROOT
    path = root / f"{profile_id}.yaml"
    raw = _load_yaml(path)
    if str(raw.get("profile_id", "")) != profile_id:
        raise ValueError(f"profile filename/id mismatch: {path}")
    return validate_profile(raw)
