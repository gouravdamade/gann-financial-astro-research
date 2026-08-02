from __future__ import annotations

import json

import pytest

from chart_conditioned_aspects.polarity_catalogue import (
    TargetAwarePolarityCatalogue,
    TargetAwarePolarityEntry,
    lookup_target_aware_polarity,
)
from chart_conditioned_aspects.polarity_evidence import (
    TargetAwarePolarityEvidencePacket,
    TargetAwarePolarityEvidencePacketRegistry,
)
from chart_conditioned_aspects.models import stable_hash


def reviewed_packet(side: str = "USD", polarity: str = "ADVERSE") -> TargetAwarePolarityEvidencePacket:
    payload = {
        "packetId": f"{side}-TEST-PACKET-001",
        "instrumentId": f"FX_CURRENCY:{side}",
        "sideIdentity": side,
        "chartId": f"{side}-TEST",
        "chartHypothesisId": f"{side}-HYPOTHESIS-001",
        "transitBody": "MARS",
        "natalTarget": "SUN",
        "aspectType": "square",
        "reviewedPolarity": polarity,
        "evidenceStatus": "REVIEWED_RESEARCH_ONLY",
        "chartAcceptanceStatus": "ACCEPTED_RESEARCH",
        "astronomyContract": "RAMAN_SIDEREAL_SWISSEPH_V1",
        "profileHash": "profile-hash",
        "reviewedBy": "test-reviewer",
        "reviewedAtUtc": "2026-08-02T12:00:00+00:00",
        "sourceRefs": ["TEST-SOURCE:fixture"],
    }
    return TargetAwarePolarityEvidencePacket.from_mapping({
        **payload,
        "packetHash": stable_hash(payload),
    })


def test_production_catalogue_is_explicitly_missing_for_usd_side() -> None:
    catalogue = TargetAwarePolarityCatalogue.load()

    result = lookup_target_aware_polarity(catalogue, instrument_id="FX_CURRENCY:USD")

    assert result["lookupState"] == "POLARITY_CATALOGUE_MISSING"
    assert result["entry"] is None
    assert result["sideIdentity"] == "USD"
    assert result["magnitudeState"] == "MAGNITUDE_NOT_CONFIGURED"
    assert result["guardrails"]["executionAllowed"] is False
    assert result["guardrails"]["actsAsSbcConfirmation"] is False


def test_incomplete_event_context_fails_closed() -> None:
    result = lookup_target_aware_polarity(
        TargetAwarePolarityCatalogue.load(),
        instrument_id="FX_CURRENCY:USD",
        chart_id="USD-TEST",
        transit_body="MARS",
    )

    assert result["lookupState"] == "TARGET_CONTEXT_INCOMPLETE"
    assert result["entry"] is None


def test_explicit_catalogue_entry_is_categorical_without_magnitude(tmp_path) -> None:
    packet = reviewed_packet()
    entry = TargetAwarePolarityEntry(
        entry_id="USD-TEST-MARS-SUN-SQUARE",
        instrument_id="FX_CURRENCY:USD",
        side_identity="USD",
        chart_id="USD-TEST",
        chart_hypothesis_id="USD-HYPOTHESIS-001",
        transit_body="MARS",
        natal_target="SUN",
        aspect_type="square",
        precomputed_polarity="ADVERSE",
        evidence_status="REVIEWED_RESEARCH_ONLY",
        profile_hash="profile-hash",
        evidence_packet_id=packet.packet_id,
        evidence_packet_hash=packet.packet_hash,
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
        TargetAwarePolarityCatalogue.load(
            path,
            evidence_registry=TargetAwarePolarityEvidencePacketRegistry(
                registry_id="TEST-REGISTRY",
                registry_status="REVIEWED_PACKET_PRESENT",
                packets=(packet,),
                registry_hash="registry-hash",
            ),
        ),
        instrument_id="FX_CURRENCY:USD",
        chart_id="USD-TEST",
        transit_body="MARS",
        natal_target="SUN",
        aspect_type="SQUARE",
    )

    assert result["lookupState"] == "READY"
    assert result["sideIdentity"] == "USD"
    assert result["entry"]["precomputedPolarity"] == "ADVERSE"
    assert result["stateContract"] == "CATEGORICAL_POLARITY_STATE"
    assert result["magnitudeState"] == "MAGNITUDE_NOT_CONFIGURED"


def test_catalogue_entry_cannot_reference_the_wrong_reviewed_packet(tmp_path) -> None:
    packet = reviewed_packet()
    entry = TargetAwarePolarityEntry(
        entry_id="USD-TEST-MARS-SUN-SQUARE",
        instrument_id="FX_CURRENCY:USD",
        side_identity="USD",
        chart_id="USD-TEST",
        chart_hypothesis_id="USD-HYPOTHESIS-001",
        transit_body="MARS",
        natal_target="SUN",
        aspect_type="square",
        precomputed_polarity="SUPPORTIVE",
        evidence_status="REVIEWED_RESEARCH_ONLY",
        profile_hash="profile-hash",
        evidence_packet_id=packet.packet_id,
        evidence_packet_hash=packet.packet_hash,
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

    with pytest.raises(ValueError, match="does not match reviewed evidence packet"):
        TargetAwarePolarityCatalogue.load(
            path,
            evidence_registry=TargetAwarePolarityEvidencePacketRegistry(
                registry_id="TEST-REGISTRY",
                registry_status="REVIEWED_PACKET_PRESENT",
                packets=(packet,),
                registry_hash="registry-hash",
            ),
        )


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


def test_pair_identity_is_derived_only_not_a_primary_catalogue_lookup() -> None:
    result = lookup_target_aware_polarity(
        TargetAwarePolarityCatalogue.load(),
        instrument_id="FX_PAIR:USDJPY",
    )

    assert result["lookupState"] == "PAIR_DERIVATION_ONLY"
    assert result["entry"] is None
    assert result["sideIdentity"] is None


def test_usd_and_jpy_chart_contexts_resolve_independently(tmp_path) -> None:
    usd_packet = reviewed_packet("USD", "ADVERSE")
    jpy_packet = reviewed_packet("JPY", "SUPPORTIVE")
    entries = [
        TargetAwarePolarityEntry(
            entry_id=f"{side}-TEST-MARS-SUN-SQUARE",
            instrument_id=f"FX_CURRENCY:{side}",
            side_identity=side,
            chart_id=f"{side}-TEST",
            chart_hypothesis_id=f"{side}-HYPOTHESIS-001",
            transit_body="MARS",
            natal_target="SUN",
            aspect_type="square",
            precomputed_polarity=polarity,  # type: ignore[arg-type]
            evidence_status="REVIEWED_RESEARCH_ONLY",
            profile_hash="profile-hash",
            evidence_packet_id=packet.packet_id,
            evidence_packet_hash=packet.packet_hash,
        )
        for side, polarity, packet in (("USD", "ADVERSE", usd_packet), ("JPY", "SUPPORTIVE", jpy_packet))
    ]
    path = tmp_path / "catalogue.json"
    path.write_text(json.dumps({
        "contract": "CHART_CONDITIONED_POLARITY_CATALOGUE_V1",
        "schema_version": 1,
        "catalogue_id": "TEST-CATALOGUE",
        "catalogue_status": "RESEARCH_ENTRY_PRESENT",
        "entries": [entry.to_public() for entry in entries],
        "guardrails": {"read_only": True, "execution_allowed": False, "automatic_order_placement": False, "magnitude_configured": False, "financially_validated": False},
    }), encoding="utf-8")
    catalogue = TargetAwarePolarityCatalogue.load(
        path,
        evidence_registry=TargetAwarePolarityEvidencePacketRegistry(
            registry_id="TEST-REGISTRY", registry_status="REVIEWED_PACKET_PRESENT",
            packets=(usd_packet, jpy_packet), registry_hash="registry-hash",
        ),
    )

    usd = lookup_target_aware_polarity(catalogue, instrument_id="FX_CURRENCY:USD", chart_id="USD-TEST", transit_body="MARS", natal_target="SUN", aspect_type="square")
    jpy = lookup_target_aware_polarity(catalogue, instrument_id="FX_CURRENCY:JPY", chart_id="JPY-TEST", transit_body="MARS", natal_target="SUN", aspect_type="square")

    assert usd["entry"]["precomputedPolarity"] == "ADVERSE"
    assert jpy["entry"]["precomputedPolarity"] == "SUPPORTIVE"
