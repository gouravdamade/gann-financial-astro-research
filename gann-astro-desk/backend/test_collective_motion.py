from __future__ import annotations

import unittest

from collective_motion import (
    COLLECTIVE_EVENT_CONTRACT,
    COLLECTIVE_MOTION_CONTRACT,
    apply_reliability_safe_motion,
    detect_sampled_collective_events,
    signed_circular_difference_degrees,
)


DAY = 86_400
START = 1_700_000_000


def sample(
    offset_seconds: int,
    longitude: float | None,
    *,
    reliable: bool = True,
    coherence: float = 0.5,
    state: str = "PARTIALLY_COHERENT",
) -> dict[str, object]:
    return {
        "time": START + offset_seconds,
        "meanLongitudeDeg": longitude,
        "coherenceR1": coherence,
        "state": state,
        "longitudeReliable": reliable,
    }


def events_for(
    samples: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    motion_samples, _ = apply_reliability_safe_motion(samples)
    return detect_sampled_collective_events(
        motion_samples,
        profile_id="TEST_PROFILE",
        low_coherence_floor=0.2,
        concentrated_floor=0.65,
    )


class CollectiveMotionTests(unittest.TestCase):
    def test_signed_circular_difference_uses_shortest_path(self) -> None:
        self.assertAlmostEqual(signed_circular_difference_degrees(1.0, 359.0), 2.0)
        self.assertAlmostEqual(
            signed_circular_difference_degrees(359.0, 1.0),
            -2.0,
        )

    def test_forward_wrap_is_unwrapped_without_a_false_reverse_jump(self) -> None:
        samples, summary = apply_reliability_safe_motion(
            [
                sample(0, 359.0),
                sample(DAY, 1.0),
                sample(2 * DAY, 4.0),
            ]
        )

        self.assertEqual(summary["contract"], COLLECTIVE_MOTION_CONTRACT)
        self.assertEqual(
            [row["unwrappedLongitudeDeg"] for row in samples],
            [359.0, 361.0, 364.0],
        )
        self.assertEqual(
            [row["velocityDegPerDay"] for row in samples],
            [2.0, 2.5, 3.0],
        )
        self.assertIsNone(samples[0]["accelerationDegPerDay2"])
        self.assertEqual(samples[1]["accelerationDegPerDay2"], 0.5)
        self.assertIsNone(samples[2]["accelerationDegPerDay2"])

    def test_motion_uses_elapsed_time_instead_of_sample_count(self) -> None:
        samples, _ = apply_reliability_safe_motion(
            [
                sample(0, 10.0),
                sample(DAY // 2, 11.0),
                sample(2 * DAY, 14.0),
            ]
        )

        self.assertEqual(
            [row["velocityDegPerDay"] for row in samples],
            [2.0, 2.0, 2.0],
        )
        self.assertEqual(samples[1]["accelerationDegPerDay2"], 0.0)

    def test_unreliable_sample_breaks_motion_and_ingress_segments(self) -> None:
        samples, motion = apply_reliability_safe_motion(
            [
                sample(0, 29.0),
                sample(DAY, None, reliable=False),
                sample(2 * DAY, 31.0),
            ]
        )
        events, _ = detect_sampled_collective_events(
            samples,
            profile_id="TEST_PROFILE",
            low_coherence_floor=0.2,
            concentrated_floor=0.65,
        )

        self.assertEqual([row["segmentId"] for row in samples], [1, None, 2])
        self.assertTrue(
            all(row["velocityDegPerDay"] is None for row in samples)
        )
        self.assertEqual(motion["segmentCount"], 2)
        self.assertFalse(motion["guardrails"]["bridgesUnreliableSamples"])
        self.assertNotIn(
            "MEAN_RASHI_INGRESS",
            {event["eventType"] for event in events},
        )

    def test_duplicate_or_reversed_timestamps_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            apply_reliability_safe_motion(
                [
                    sample(0, 10.0),
                    sample(0, 11.0),
                ]
            )


class CollectiveSampledEventTests(unittest.TestCase):
    def test_forward_and_backward_rashi_ingress_are_interpolated(self) -> None:
        forward, _ = events_for(
            [
                sample(0, 29.0),
                sample(DAY, 31.0),
            ]
        )
        backward, _ = events_for(
            [
                sample(0, 31.0),
                sample(DAY, 29.0),
            ]
        )

        forward_ingress = next(
            event for event in forward if event["eventType"] == "MEAN_RASHI_INGRESS"
        )
        backward_ingress = next(
            event
            for event in backward
            if event["eventType"] == "MEAN_RASHI_INGRESS"
        )
        self.assertEqual(forward_ingress["estimatedTimeUnix"], START + DAY // 2)
        self.assertEqual(
            forward_ingress["details"],
            {
                "direction": "FORWARD",
                "boundaryUnwrappedDeg": 30.0,
                "boundaryWrappedDeg": 30.0,
                "fromRashi": "ARIES",
                "toRashi": "TAURUS",
            },
        )
        self.assertEqual(
            backward_ingress["details"],
            {
                "direction": "BACKWARD",
                "boundaryUnwrappedDeg": 30.0,
                "boundaryWrappedDeg": 30.0,
                "fromRashi": "TAURUS",
                "toRashi": "ARIES",
            },
        )

    def test_backward_boundary_endpoint_emits_once_on_entry_to_lower_rashi(
        self,
    ) -> None:
        events, _ = events_for(
            [
                sample(0, 31.0),
                sample(DAY, 30.0),
                sample(2 * DAY, 29.0),
            ]
        )
        ingress_events = [
            event for event in events if event["eventType"] == "MEAN_RASHI_INGRESS"
        ]

        self.assertEqual(len(ingress_events), 1)
        self.assertEqual(ingress_events[0]["estimatedTimeUnix"], START + DAY)
        self.assertEqual(ingress_events[0]["details"]["fromRashi"], "TAURUS")
        self.assertEqual(ingress_events[0]["details"]["toRashi"], "ARIES")

    def test_threshold_and_state_events_share_one_causal_cluster(self) -> None:
        events, summary = events_for(
            [
                sample(
                    0,
                    20.0,
                    coherence=0.1,
                    state="DISPERSED",
                ),
                sample(
                    600,
                    20.5,
                    coherence=0.7,
                    state="CONCENTRATED",
                ),
            ]
        )

        self.assertEqual(summary["eventCount"], 3)
        self.assertEqual(
            summary["eventTypeCounts"],
            {
                "CLUSTER_STATE_TRANSITION": 1,
                "COHERENCE_THRESHOLD_CROSSING": 2,
            },
        )
        self.assertEqual(len({event["causalClusterId"] for event in events}), 1)
        threshold_events = [
            event
            for event in events
            if event["eventType"] == "COHERENCE_THRESHOLD_CROSSING"
        ]
        self.assertEqual(
            [event["estimatedTimeUnix"] for event in threshold_events],
            [START + 100, START + 550],
        )

    def test_events_are_deterministic_approximate_and_non_executable(self) -> None:
        source = [
            sample(0, 29.0, coherence=0.1, state="DISPERSED"),
            sample(DAY, 31.0, coherence=0.7, state="CONCENTRATED"),
        ]
        first, first_summary = events_for(source)
        second, second_summary = events_for(source)

        self.assertEqual(first, second)
        self.assertEqual(first_summary, second_summary)
        self.assertTrue(first)
        for event in first:
            self.assertEqual(event["contract"], COLLECTIVE_EVENT_CONTRACT)
            self.assertFalse(event["timing"]["exact"])
            self.assertFalse(event["guardrails"]["exactEventTime"])
            self.assertEqual(event["guardrails"]["directionalContribution"], 0.0)
            self.assertFalse(event["guardrails"]["castsSbcVedha"])
            self.assertFalse(event["guardrails"]["consumedByLiveInference"])
            self.assertFalse(event["guardrails"]["consumedByAutoSuggest"])
            self.assertFalse(event["guardrails"]["consumedByShadowLedger"])
            self.assertFalse(event["guardrails"]["consumedByOfficialMlNotes"])
            self.assertFalse(event["guardrails"]["executionAllowed"])
        self.assertEqual(
            first_summary["eventPolicy"]["timingClassification"],
            "SAMPLED_RESEARCH_ESTIMATE",
        )
        self.assertIn(
            "EXACT_EPHEMERIS_REFINED_INGRESS",
            first_summary["eventPolicy"]["doesNotDetectYet"],
        )


if __name__ == "__main__":
    unittest.main()
