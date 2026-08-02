from __future__ import annotations

import json

import pytest

from chart_conditioned_aspects.polarity_catalogue import (
    TargetAwarePolarityCatalogue,
    TargetAwarePolarityEntry,
    lookup_target_aware_polarity,
)


def test_production_catalogue_is_explicitly_missing_for_usdjpy() -> None:
    catalogue = TargetAwarePolarityCatalogue.load()

    result = lookup_target_aware_polarity(catalogue, instrument_id="FX:USDJPY")

    assert result["lookupState"] == "POLARITY_CATALOGUE_MISSING"
    assert result["entry"] is None
    assert result["magnitudeState"] == "MAGNITUDE_NOT_CONFIGURED"
    assert result["guardrails"]["executionAllowed"] is False
    assert result["guardrails"]["actsAsSbcConfirmation"] is False


def test_incomplete_event_context_fails_closed() -> None:
    result = lookup_target_aware_polarity(
        TargetAwarePolarityCatalogue.load(),
        instrument_id="USDJPY",
        chart_id="USDJPY-TEST",
        transit_body="MARS",
    )

    assert result["lookupState"] == "TARGET_CONTEXT_INCOMPLETE"
    assert result["entry"] is None


def test_explicit_catalogue_entry_is_categorical_without_magnitude(tmp_path) -> None:
    entry = TargetAwarePolarityEntry(
        entry_id="USDJPY-TEST-MARS-SUN-SQUARE",
        instrument_id="USDJPY",
        chart_id="USDJPY-TEST",
        transit_body="MARS",
        natal_target="SUN",
        aspect_type="square",
        precomputed_polarity="ADVERSE",
        evidence_status="REVIEWED_RESEARCH_ONLY",
        profile_hash="profile-hash",
        evidence_packet_hash="evidence-hash",
    )
    path = tmp_path / "catalogue.json"
    path.write_text(json.dumps({
        "contract": "CHART_CONDITIONED_POLARITY_CATALOGUE_V1",
        "schema_version": 1,
        "catalogue_id": "TEST-CATALOGUE",
        "catalogue_status": "RESEARCH_ENTRY_PRESENT",
        "entries": [entry.to_public()],
        "guardrails": {
            "read_only": True,
            "execution_allowed": False,
            "automatic_order_placement": False,
            "magnitude_configured": False,
            "financially_validated": False,
        },
    }), encoding="utf-8")

    result = lookup_target_aware_polarity(
        TargetAwarePolarityCatalogue.load(path),
        instrument_id="FX:USDJPY",
        chart_id="USDJPY-TEST",
        transit_body="MARS",
        natal_target="SUN",
        aspect_type="SQUARE",
    )

    assert result["lookupState"] == "READY"
    assert result["entry"]["precomputedPolarity"] == "ADVERSE"
    assert result["stateContract"] == "CATEGORICAL_POLARITY_STATE"
    assert result["magnitudeState"] == "MAGNITUDE_NOT_CONFIGURED"


def test_catalogue_rejects_any_execution_unlock(tmp_path) -> None:
    path = tmp_path / "unsafe.json"
    path.write_text(json.dumps({
        "contract": "CHART_CONDITIONED_POLARITY_CATALOGUE_V1",
        "schema_version": 1,
        "catalogue_id": "UNSAFE",
        "catalogue_status": "UNSAFE",
        "entries": [],
        "guardrails": {
            "execution_allowed": True,
            "automatic_order_placement": False,
            "magnitude_configured": False,
        },
    }), encoding="utf-8")

    with pytest.raises(ValueError, match="execution_allowed=false"):
        TargetAwarePolarityCatalogue.load(path)
