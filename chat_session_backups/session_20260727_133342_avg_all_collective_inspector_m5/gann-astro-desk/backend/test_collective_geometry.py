from __future__ import annotations

import unittest

import numpy as np

from collective_geometry import (
    AVG_ALL_MEMBERS,
    COLLECTIVE_FIELD_CONTRACT,
    LEGACY_AVG_ALL_PROFILE_ID,
    calculate_collective_field,
    legacy_circular_mean,
)


def member_matrix(values: list[float]) -> dict[str, np.ndarray]:
    return {
        member: np.asarray([values[position]], dtype=np.float64)
        for position, member in enumerate(AVG_ALL_MEMBERS)
    }


class CollectiveGeometryTests(unittest.TestCase):
    def test_aligned_planets_are_concentrated_and_reliable(self) -> None:
        members = {
            member: np.asarray([30.0, 60.0], dtype=np.float64)
            for member in AVG_ALL_MEMBERS
        }
        result = calculate_collective_field(
            members,
            [1_700_000_000, 1_700_003_600],
        )

        self.assertEqual(result["contract"], COLLECTIVE_FIELD_CONTRACT)
        self.assertEqual(result["profile"]["profileId"], LEGACY_AVG_ALL_PROFILE_ID)
        self.assertEqual(result["samples"][0]["meanLongitudeDeg"], 30.0)
        self.assertEqual(result["samples"][0]["coherenceR1"], 1.0)
        self.assertEqual(result["samples"][0]["polarisationR2"], 1.0)
        self.assertEqual(result["samples"][0]["state"], "CONCENTRATED")
        self.assertTrue(result["samples"][0]["longitudeReliable"])
        self.assertEqual(result["samples"][0]["segmentId"], 1)
        self.assertEqual(result["samples"][0]["unwrappedLongitudeDeg"], 30.0)
        self.assertEqual(result["samples"][0]["velocityDegPerDay"], 720.0)
        self.assertIsNone(result["samples"][0]["accelerationDegPerDay2"])
        self.assertEqual(result["summary"]["reliabilityCounts"], {"RELIABLE": 2})
        self.assertEqual(
            result["motion"]["contract"],
            "GANN_PLANETARY_COLLECTIVE_MOTION_V1",
        )
        self.assertEqual(len(result["samples"][0]["memberAudit"]), 10)
        self.assertEqual(
            result["influence"]["contract"],
            "GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1",
        )
        self.assertFalse(
            result["influence"]["guardrails"]["countsAsIndependentVote"]
        )
        self.assertFalse(
            result["influence"]["guardrails"]["consumedByAutoSuggest"]
        )
        self.assertEqual(
            result["eventSummary"]["eventPolicy"]["timingClassification"],
            "SAMPLED_RESEARCH_ESTIMATE",
        )
        self.assertEqual(result["evidence"]["role"], "CONTEXT_ONLY")
        self.assertFalse(
            result["evidence"]["guardrails"]["consumedByShadowLedger"]
        )
        self.assertEqual(result["guardrails"]["directionalContribution"], 0.0)
        self.assertFalse(result["guardrails"]["castsSbcVedha"])
        self.assertFalse(result["guardrails"]["consumedByAutoSuggest"])
        self.assertFalse(result["guardrails"]["consumedByShadowLedger"])
        self.assertFalse(result["guardrails"]["consumedByOfficialMlNotes"])
        self.assertFalse(result["guardrails"]["executionAllowed"])

    def test_opposed_groups_are_bipolar_without_a_reliable_mean(self) -> None:
        result = calculate_collective_field(
            member_matrix([0.0] * 5 + [180.0] * 5),
            [1_700_000_000],
        )
        sample = result["samples"][0]

        self.assertLess(sample["coherenceR1"], 1e-8)
        self.assertAlmostEqual(sample["polarisationR2"], 1.0)
        self.assertEqual(sample["state"], "BIPOLAR")
        self.assertEqual(sample["reliability"], "UNSTABLE")
        self.assertFalse(sample["longitudeReliable"])
        self.assertIsNone(sample["segmentId"])
        self.assertIsNone(sample["unwrappedLongitudeDeg"])
        self.assertIsNone(sample["velocityDegPerDay"])
        self.assertTrue(
            all(
                member["longitudeLeverageDeg"] is None
                and member["coherenceLeverage"] is None
                for member in sample["memberAudit"]
            )
        )

    def test_low_first_harmonic_and_strong_second_harmonic_is_bipolar(self) -> None:
        values = [0.0] * 6 + [180.0] * 4
        result = calculate_collective_field(
            member_matrix(values),
            [1_700_000_000],
        )
        sample = result["samples"][0]

        self.assertAlmostEqual(sample["coherenceR1"], 0.2)
        self.assertAlmostEqual(sample["polarisationR2"], 1.0)
        self.assertEqual(sample["state"], "PARTIALLY_COHERENT")

    def test_legacy_mean_remains_identical_to_original_vector_formula(self) -> None:
        values = [
            np.asarray([350.0, 10.0]),
            np.asarray([10.0, 30.0]),
        ]
        actual = legacy_circular_mean(values)
        radians = np.deg2rad(np.vstack(values))
        expected = (
            np.degrees(
                np.arctan2(
                    np.sin(radians).sum(axis=0),
                    np.cos(radians).sum(axis=0),
                )
            )
            % 360.0
        )
        np.testing.assert_array_equal(actual, expected)

    def test_profile_hash_is_deterministic(self) -> None:
        members = {
            member: np.asarray([float(position * 7)], dtype=np.float64)
            for position, member in enumerate(AVG_ALL_MEMBERS)
        }
        first = calculate_collective_field(members, [1_700_000_000])
        second = calculate_collective_field(members, [1_700_000_000])
        self.assertEqual(
            first["profile"]["memberSetHash"],
            second["profile"]["memberSetHash"],
        )


if __name__ == "__main__":
    unittest.main()
