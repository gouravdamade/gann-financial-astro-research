from __future__ import annotations

import json

from chart_conditioned_aspects.models import stable_hash
from chart_conditioned_aspects.polarity_catalogue import (
    TargetAwarePolarityCatalogue,
    TargetAwarePolarityEntry,
)
from chart_conditioned_aspects.polarity_evidence import (
    TargetAwarePolarityEvidencePacket,
    TargetAwarePolarityEvidencePacketRegistry,
)
from chart_conditioned_aspects.polarity_series import compile_categorical_visible_range


def reviewed_packet(packet_id: str, transit: str, target: str, polarity: str) -> TargetAwarePolarityEvidencePacket:
    payload = {
        "packetId": packet_id,
        "instrumentId": "FX_CURRENCY:USD",
        "sideIdentity": "USD",
        "chartId": "USD-SIDE-TEST",
        "chartHypothesisId": "USD-SIDE-HYPOTHESIS-001",
        "transitBody": transit,
        "natalTarget": target,
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
    return TargetAwarePolarityEvidencePacket.from_mapping({**payload, "packetHash": stable_hash(payload)})


def catalogue_with_two_states(tmp_path) -> TargetAwarePolarityCatalogue:
    supportive = reviewed_packet("USD-PACKET-SUPPORTIVE", "MARS", "SUN", "SUPPORTIVE")
    adverse = reviewed_packet("USD-PACKET-ADVERSE", "VENUS", "MOON", "ADVERSE")
    entries = [
        TargetAwarePolarityEntry(
            entry_id=f"ENTRY-{packet.packet_id}",
            instrument_id=packet.instrument_id,
            side_identity=packet.side_identity,
            chart_id=packet.chart_id,
            chart_hypothesis_id=packet.chart_hypothesis_id,
            transit_body=packet.transit_body,
            natal_target=packet.natal_target,
            aspect_type=packet.aspect_type,
            precomputed_polarity=packet.reviewed_polarity,
            evidence_status=packet.evidence_status,
            profile_hash=packet.profile_hash,
            evidence_packet_id=packet.packet_id,
            evidence_packet_hash=packet.packet_hash,
        )
        for packet in (supportive, adverse)
    ]
    source = tmp_path / "catalogue.json"
    source.write_text(json.dumps({
        "contract": "CHART_CONDITIONED_POLARITY_CATALOGUE_V1",
        "schema_version": 1,
        "catalogue_id": "USD-SIDE-TEST-CATALOGUE",
        "catalogue_status": "RESEARCH_ENTRY_PRESENT",
        "entries": [entry.to_public() for entry in entries],
        "guardrails": {"read_only": True, "execution_allowed": False, "automatic_order_placement": False, "magnitude_configured": False, "financially_validated": False},
    }), encoding="utf-8")
    return TargetAwarePolarityCatalogue.load(
        source,
        evidence_registry=TargetAwarePolarityEvidencePacketRegistry(
            registry_id="USD-SIDE-TEST-REGISTRY", registry_status="REVIEWED_PACKET_PRESENT",
            packets=(supportive, adverse), registry_hash="test-registry-hash",
        ),
    )


def test_visible_range_preserves_unknown_gaps_and_marks_mixed_overlap(tmp_path) -> None:
    result = compile_categorical_visible_range(
        catalogue_with_two_states(tmp_path),
        instrument_id="FX_CURRENCY:USD",
        chart_id="USD-SIDE-TEST",
        chart_hypothesis_id="USD-SIDE-HYPOTHESIS-001",
        range_start_utc="2026-08-02T00:00:00Z",
        range_end_utc="2026-08-02T01:00:00Z",
        events=[
            {"eventId": "supportive", "startUtc": "2026-08-02T00:10:00Z", "endUtc": "2026-08-02T00:40:00Z", "transitBody": "MARS", "natalTarget": "SUN", "aspectType": "square"},
            {"eventId": "adverse", "startUtc": "2026-08-02T00:20:00Z", "endUtc": "2026-08-02T00:30:00Z", "transitBody": "VENUS", "natalTarget": "MOON", "aspectType": "square"},
            {"eventId": "unreviewed", "startUtc": "2026-08-02T00:30:00Z", "endUtc": "2026-08-02T00:50:00Z", "transitBody": "JUPITER", "natalTarget": "SATURN", "aspectType": "square"},
        ],
    )

    assert result["contract"] == "CHART_CONDITIONED_CATEGORICAL_RANGE_V1"
    assert result["magnitudeState"] == "MAGNITUDE_NOT_CONFIGURED"
    assert result["guardrails"]["executionAllowed"] is False
    assert [item["polarityState"] for item in result["intervals"]] == ["UNKNOWN", "SUPPORTIVE", "MIXED", "UNKNOWN", "UNKNOWN", "UNKNOWN"]
    assert result["intervals"][2]["supportiveActive"] is True
    assert result["intervals"][2]["adverseActive"] is True
    assert result["intervals"][3]["unknownEventIds"] == ["unreviewed"]


def test_visible_range_rejects_a_pair_as_primary_input(tmp_path) -> None:
    try:
        compile_categorical_visible_range(
            catalogue_with_two_states(tmp_path),
            instrument_id="FX_PAIR:USDJPY",
            chart_id="USD-SIDE-TEST",
            chart_hypothesis_id="USD-SIDE-HYPOTHESIS-001",
            range_start_utc="2026-08-02T00:00:00Z",
            range_end_utc="2026-08-02T01:00:00Z",
            events=[],
        )
    except ValueError as exc:
        assert "FX_CURRENCY" in str(exc)
    else:
        raise AssertionError("pair identity must not compile as a primary side range")
