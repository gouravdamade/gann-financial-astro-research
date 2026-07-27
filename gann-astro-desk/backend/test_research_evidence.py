from __future__ import annotations

import unittest

from research_evidence import (
    RESEARCH_EVIDENCE_CONTRACT,
    build_context_only_evidence_packet,
    build_research_evidence_packet,
)


class ResearchEvidenceContractTests(unittest.TestCase):
    def test_context_packet_cannot_create_a_market_signal(self) -> None:
        packet = build_context_only_evidence_packet(
            source_family="collective_geometry",
            source_profile_id="profile-v1",
            calculation_version="calculation-v1",
            observed_at_unix=1_700_000_000,
            reason="No validated market mapping.",
            descriptors=[
                {
                    "key": "coherence_r1",
                    "value": 0.72,
                    "unit": "ratio",
                }
            ],
        )

        self.assertEqual(packet["contract"], RESEARCH_EVIDENCE_CONTRACT)
        self.assertEqual(packet["role"], "CONTEXT_ONLY")
        self.assertEqual(
            {item["status"] for item in packet["channels"].values()},
            {"NOT_APPLICABLE"},
        )
        self.assertEqual(packet["empiricalCoefficient"], 0.0)
        self.assertFalse(packet["guardrails"]["consumedByLiveInference"])
        self.assertFalse(packet["guardrails"]["executionAllowed"])

    def test_packet_requires_all_four_named_channels(self) -> None:
        with self.assertRaisesRegex(ValueError, "direction, activation, conflict"):
            build_research_evidence_packet(
                source_family="test",
                source_profile_id="profile-v1",
                calculation_version="calculation-v1",
                observed_at_unix=1_700_000_000,
                role="CONTEXT_ONLY",
                channels={
                    "direction": {
                        "status": "NOT_APPLICABLE",
                        "reason": "not mapped",
                    }
                },
            )


if __name__ == "__main__":
    unittest.main()
