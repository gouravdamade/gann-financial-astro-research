from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))
if str(INSTRUMENT_SBC_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUMENT_SBC_ROOT))

from chart_conditioned_aspects.polarity_catalogue import (
    TargetAwarePolarityCatalogue,
    TargetAwarePolarityEntry,
)
from chart_conditioned_aspects.polarity_evidence import (
    TargetAwarePolarityEvidencePacket,
    TargetAwarePolarityEvidencePacketRegistry,
)
from chart_conditioned_aspects.models import stable_hash

from fx_side_pilot_service import build_fx_side_pilot_status


def _packet(side: str, polarity: str) -> TargetAwarePolarityEvidencePacket:
    payload = {
        "packetId": f"{side}-{polarity}-PILOT",
        "instrumentId": f"FX_CURRENCY:{side}",
        "sideIdentity": side,
        "chartId": f"{side}-REVIEWED-CHART",
        "chartHypothesisId": f"{side}-FOUNDATION-001",
        "transitBody": "MARS",
        "natalTarget": "SUN",
        "aspectType": "square",
        "reviewedPolarity": polarity,
        "evidenceStatus": "REVIEWED_RESEARCH_ONLY",
        "chartAcceptanceStatus": "ACCEPTED_RESEARCH",
        "astronomyContract": "RAMAN_SIDEREAL_SWISSEPH_V1",
        "profileHash": "profile-hash",
        "reviewedBy": "founder-review",
        "reviewedAtUtc": "2026-08-02T12:00:00+00:00",
        "sourceRefs": ["RESEARCH:side-chart-review"],
    }
    return TargetAwarePolarityEvidencePacket.from_mapping(
        {**payload, "packetHash": stable_hash(payload)}
    )


def _entry(packet: TargetAwarePolarityEvidencePacket) -> TargetAwarePolarityEntry:
    return TargetAwarePolarityEntry(
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


class FxSidePilotServiceTests(unittest.TestCase):
    def test_production_pilot_status_is_explicitly_pending(self) -> None:
        report = build_fx_side_pilot_status({})

        self.assertEqual(report["status"], "PILOT_EVIDENCE_PENDING")
        self.assertEqual(report["eligibleSides"], [])
        self.assertTrue(report["sides"]["USD"]["unknownGapsRetained"])
        self.assertEqual(report["sides"]["USD"]["missingRequiredStates"], ["SUPPORTIVE", "ADVERSE"])
        self.assertFalse(report["guardrails"]["executionAllowed"])
        self.assertFalse(report["guardrails"]["createsCatalogueEntry"])

    def test_one_side_requires_both_categorical_states_before_it_is_eligible(self) -> None:
        supportive = _packet("USD", "SUPPORTIVE")
        adverse = _packet("USD", "ADVERSE")
        registry = TargetAwarePolarityEvidencePacketRegistry(
            registry_id="TEST-REGISTRY",
            registry_status="RESEARCH_REVIEWED",
            packets=(supportive, adverse),
            registry_hash="registry-hash",
        )
        catalogue = TargetAwarePolarityCatalogue(
            catalogue_id="TEST-CATALOGUE",
            catalogue_status="RESEARCH_REVIEWED",
            entries=(_entry(supportive), _entry(adverse)),
            catalogue_hash="catalogue-hash",
        )

        report = build_fx_side_pilot_status({}, catalogue=catalogue, registry=registry)

        self.assertEqual(report["status"], "PILOT_EVIDENCE_PRESENT_RESEARCH_ONLY")
        self.assertEqual(report["eligibleSides"], ["USD"])
        self.assertEqual(report["sides"]["USD"]["missingRequiredStates"], [])
        self.assertTrue(report["sides"]["USD"]["pilotEvidenceComplete"])
        self.assertFalse(report["sides"]["JPY"]["pilotEvidenceComplete"])

    def test_pilot_status_rejects_unrecognized_request_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown FX side pilot status"):
            build_fx_side_pilot_status({"approve": True})
