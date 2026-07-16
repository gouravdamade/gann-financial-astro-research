from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from sbc.config import CONFIG_ROOT, load_profile, load_source_register, validate_profile
from sbc.enums import Ayanamsha


def test_source_register_and_schema_documents_load() -> None:
    register = load_source_register()
    source_ids = {item["source_id"] for item in register["sources"]}
    assert "SBC_IMPLEMENTATION_GUIDE_20260717" in source_ids
    assert "PHALADEEPIKA_1937_SUBRAHMANYA_SASTRI" in source_ids
    for path in sorted((CONFIG_ROOT / "schemas").glob("*.json")):
        assert json.loads(path.read_text(encoding="utf-8"))["$schema"].endswith("2020-12/schema")


def test_primary_and_comparison_profiles_are_explicit() -> None:
    primary = load_profile("sbc_raman_foundation_v1")
    comparison = load_profile("sbc_lahiri_comparison_v1")
    assert primary.astro_settings.ayanamsha is Ayanamsha.RAMAN
    assert primary.status == "active_research_foundation"
    assert comparison.astro_settings.ayanamsha is Ayanamsha.LAHIRI
    assert comparison.status == "comparison_only"
    assert primary.profile_hash == load_profile("sbc_raman_foundation_v1").profile_hash
    assert all(not primary.features[name] for name in ("grid", "vedha", "latta", "scoring", "trades"))


def test_profile_compiler_rejects_interpretive_features_and_unknown_fields() -> None:
    raw = copy.deepcopy(load_profile("sbc_raman_foundation_v1").raw)
    raw["features"]["grid"] = True
    with pytest.raises(ValueError, match="cannot enable grid"):
        validate_profile(raw)

    raw = copy.deepcopy(load_profile("sbc_raman_foundation_v1").raw)
    raw["astronomy"]["silent_magic"] = True
    with pytest.raises(ValueError, match="Unknown astronomy fields"):
        validate_profile(raw)


def test_profile_compiler_rejects_unresolved_sources() -> None:
    raw = copy.deepcopy(load_profile("sbc_raman_foundation_v1").raw)
    raw["source_ids"].append("UNRESOLVED_BOOK")
    with pytest.raises(ValueError, match="unresolved source IDs"):
        validate_profile(raw)


def test_private_corpus_paths_are_gitignored() -> None:
    text = (Path(__file__).resolve().parent / ".gitignore").read_text(encoding="utf-8")
    assert "sbc/corpus/private/" in text
    assert "sbc/generated/" in text
