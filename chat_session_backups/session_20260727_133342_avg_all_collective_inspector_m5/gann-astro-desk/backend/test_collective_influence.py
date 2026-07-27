from __future__ import annotations

import math
import unittest

from collective_influence import (
    COLLECTIVE_INFLUENCE_CONTRACT,
    build_member_audit,
    summarize_member_influence,
)


MEMBERS = (
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "URANUS",
    "NEPTUNE",
    "PLUTO",
)
WEIGHTS = (0.1,) * 10


class CollectiveInfluenceTests(unittest.TestCase):
    def test_aligned_members_have_zero_leave_one_out_leverage(self) -> None:
        audit = build_member_audit(
            [30.0] * 10,
            members=MEMBERS,
            weights=WEIGHTS,
            mean_longitude_deg=30.0,
            coherence_r1=1.0,
            longitude_reliable=True,
            unstable_resultant_floor=1e-8,
        )

        self.assertEqual(len(audit), 10)
        self.assertTrue(
            all(row["angularDistanceFromMeanDeg"] == 0.0 for row in audit)
        )
        self.assertTrue(
            all(row["longitudeLeverageDeg"] == 0.0 for row in audit)
        )
        self.assertTrue(all(row["coherenceLeverage"] == 0.0 for row in audit))
        self.assertTrue(
            all(str(row["role"]).startswith("NEUTRAL_") for row in audit)
        )

    def test_outlying_fast_body_is_auditable_as_top_disperser(self) -> None:
        longitudes = [0.0] * 10
        longitudes[1] = 90.0
        cosine = sum(math.cos(math.radians(value)) for value in longitudes) / 10
        sine = sum(math.sin(math.radians(value)) for value in longitudes) / 10
        mean = math.degrees(math.atan2(sine, cosine)) % 360.0
        r1 = math.hypot(cosine, sine)
        audit = build_member_audit(
            longitudes,
            members=MEMBERS,
            weights=WEIGHTS,
            mean_longitude_deg=mean,
            coherence_r1=r1,
            longitude_reliable=True,
            unstable_resultant_floor=1e-8,
        )
        moon = next(row for row in audit if row["body"] == "MOON")

        self.assertEqual(moon["influenceRank"], 1)
        self.assertGreater(moon["longitudeLeverageDeg"], 6.0)
        self.assertLess(moon["coherenceLeverage"], 0.0)
        self.assertEqual(moon["role"], "DISPERSING_FAST_DRIVER")

    def test_unreliable_mean_never_invents_member_leverage(self) -> None:
        audit = build_member_audit(
            [0.0, float("nan")] + [30.0] * 8,
            members=MEMBERS,
            weights=WEIGHTS,
            mean_longitude_deg=None,
            coherence_r1=None,
            longitude_reliable=False,
            unstable_resultant_floor=1e-8,
        )

        self.assertTrue(
            all(row["longitudeLeverageDeg"] is None for row in audit)
        )
        self.assertTrue(all(row["coherenceLeverage"] is None for row in audit))
        self.assertTrue(all(row["influenceRank"] is None for row in audit))
        self.assertIsNone(audit[1]["longitudeDeg"])

    def test_summary_is_context_only_and_non_executable(self) -> None:
        audit = build_member_audit(
            [0.0] * 9 + [60.0],
            members=MEMBERS,
            weights=WEIGHTS,
            mean_longitude_deg=5.2087191029,
            coherence_r1=0.9539392014,
            longitude_reliable=True,
            unstable_resultant_floor=1e-8,
        )
        summary = summarize_member_influence([{"memberAudit": audit}])

        self.assertEqual(summary["contract"], COLLECTIVE_INFLUENCE_CONTRACT)
        self.assertIsNotNone(summary["latestTopLongitudeLeverage"])
        self.assertFalse(summary["guardrails"]["countsAsIndependentVote"])
        self.assertEqual(summary["guardrails"]["directionalContribution"], 0.0)
        self.assertFalse(summary["guardrails"]["consumedByLiveInference"])
        self.assertFalse(summary["guardrails"]["consumedByAutoSuggest"])
        self.assertFalse(summary["guardrails"]["consumedByShadowLedger"])
        self.assertFalse(summary["guardrails"]["consumedByOfficialMlNotes"])
        self.assertFalse(summary["guardrails"]["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
