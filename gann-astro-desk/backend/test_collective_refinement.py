from __future__ import annotations

import math
import unittest

from collective_motion import (
    apply_reliability_safe_motion,
    detect_sampled_collective_events,
)
from collective_refinement import (
    COLLECTIVE_REFINEMENT_CONTRACT,
    MAX_REFINEMENT_CANDIDATES,
    refine_collective_events,
)


START = 1_700_000_000
HOUR = 3_600


def sampled_events() -> tuple[list[dict], dict]:
    samples, _ = apply_reliability_safe_motion(
        [
            {
                "time": START,
                "meanLongitudeDeg": 29.0,
                "coherenceR1": 0.5,
                "state": "PARTIALLY_COHERENT",
                "longitudeReliable": True,
            },
            {
                "time": START + HOUR,
                "meanLongitudeDeg": 33.0,
                "coherenceR1": 0.7,
                "state": "CONCENTRATED",
                "longitudeReliable": True,
            },
        ]
    )
    return detect_sampled_collective_events(
        samples,
        profile_id="TEST_PROFILE",
        low_coherence_floor=0.2,
        concentrated_floor=0.65,
    )


def aligned_members(longitude: float) -> tuple[float, ...]:
    return (longitude,) * 10


class CollectiveRefinementTests(unittest.TestCase):
    def test_reliably_bracketed_ingress_is_refined_within_tolerance(
        self,
    ) -> None:
        events, summary = sampled_events()

        def evaluator(timestamp: float) -> tuple[float, ...]:
            fraction = (timestamp - START) / HOUR
            return aligned_members(29.0 + 4.0 * fraction)

        refined, refined_summary = refine_collective_events(
            events,
            summary,
            longitude_evaluator=evaluator,
            unstable_resultant_floor=1e-8,
        )
        ingress = next(
            event
            for event in refined
            if event["eventType"] == "MEAN_RASHI_INGRESS"
        )

        self.assertTrue(ingress["timing"]["exact"])
        self.assertTrue(ingress["guardrails"]["exactEventTime"])
        self.assertEqual(
            ingress["refinement"]["contract"],
            COLLECTIVE_REFINEMENT_CONTRACT,
        )
        self.assertEqual(
            ingress["refinement"]["status"],
            "REFINED_BRACKETED_ROOT",
        )
        self.assertLessEqual(
            abs(ingress["refinedTimeUnix"] - (START + HOUR / 4)),
            1.0,
        )
        self.assertLessEqual(
            abs(ingress["refinement"]["residualDeg"]),
            ingress["refinement"]["residualToleranceDeg"],
        )
        self.assertEqual(refined_summary["refinement"]["attemptedCount"], 1)
        self.assertEqual(refined_summary["refinement"]["refinedCount"], 1)
        self.assertEqual(refined_summary["refinement"]["fallbackCount"], 0)
        self.assertLessEqual(
            refined_summary["refinement"]["evaluatedTimestampCount"],
            16,
        )

    def test_unpreserved_ephemeris_bracket_keeps_sampled_fallback(self) -> None:
        events, summary = sampled_events()

        refined, refined_summary = refine_collective_events(
            events,
            summary,
            longitude_evaluator=lambda _timestamp: aligned_members(40.0),
            unstable_resultant_floor=1e-8,
        )
        ingress = next(
            event
            for event in refined
            if event["eventType"] == "MEAN_RASHI_INGRESS"
        )

        self.assertFalse(ingress["timing"]["exact"])
        self.assertFalse(ingress["guardrails"]["exactEventTime"])
        self.assertIsNone(ingress["refinedTimeUnix"])
        self.assertEqual(
            ingress["refinement"]["status"],
            "SAMPLED_FALLBACK",
        )
        self.assertIn(
            "do not preserve",
            ingress["refinement"]["reason"],
        )
        self.assertEqual(refined_summary["refinement"]["fallbackCount"], 1)

    def test_unreliable_midpoint_aborts_root_instead_of_bridging(self) -> None:
        events, summary = sampled_events()

        def evaluator(timestamp: float) -> tuple[float, ...]:
            if math.isclose(timestamp, START + HOUR / 2):
                return (0.0,) * 5 + (180.0,) * 5
            fraction = (timestamp - START) / HOUR
            return aligned_members(29.0 + 4.0 * fraction)

        refined, _ = refine_collective_events(
            events,
            summary,
            longitude_evaluator=evaluator,
            unstable_resultant_floor=1e-8,
        )
        ingress = next(
            event
            for event in refined
            if event["eventType"] == "MEAN_RASHI_INGRESS"
        )

        self.assertEqual(
            ingress["refinement"]["status"],
            "SAMPLED_FALLBACK",
        )
        self.assertIn(
            "unreliable",
            ingress["refinement"]["reason"],
        )

    def test_heuristic_events_remain_sampled_and_non_executable(self) -> None:
        events, summary = sampled_events()
        refined, refined_summary = refine_collective_events(
            events,
            summary,
            longitude_evaluator=lambda timestamp: aligned_members(
                29.0 + 4.0 * ((timestamp - START) / HOUR)
            ),
            unstable_resultant_floor=1e-8,
        )

        heuristic_events = [
            event
            for event in refined
            if event["eventType"] != "MEAN_RASHI_INGRESS"
        ]
        self.assertTrue(heuristic_events)
        for event in heuristic_events:
            self.assertFalse(event["timing"]["exact"])
            self.assertIsNone(event["refinedTimeUnix"])
            self.assertIsNone(event["refinement"])
            self.assertFalse(event["guardrails"]["executionAllowed"])
        guardrails = refined_summary["refinement"]["guardrails"]
        self.assertTrue(guardrails["heuristicThresholdEventsRemainSampled"])
        self.assertFalse(guardrails["consumedByLiveInference"])
        self.assertFalse(guardrails["consumedByAutoSuggest"])
        self.assertFalse(guardrails["executionAllowed"])

    def test_candidate_limit_preserves_excess_events_as_sampled(self) -> None:
        events, summary = sampled_events()
        ingress = next(
            event
            for event in events
            if event["eventType"] == "MEAN_RASHI_INGRESS"
        )
        candidates = [
            {
                **ingress,
                "eventId": f"ingress-{index}",
                "details": {
                    **ingress["details"],
                    "boundaryWrappedDeg": None,
                },
            }
            for index in range(MAX_REFINEMENT_CANDIDATES + 1)
        ]

        refined, refined_summary = refine_collective_events(
            candidates,
            summary,
            longitude_evaluator=lambda _timestamp: aligned_members(30.0),
            unstable_resultant_floor=1e-8,
        )

        self.assertEqual(len(refined), MAX_REFINEMENT_CANDIDATES + 1)
        self.assertEqual(
            refined_summary["refinement"]["attemptedCount"],
            MAX_REFINEMENT_CANDIDATES,
        )
        self.assertEqual(
            refined_summary["refinement"]["skippedBudgetCount"],
            1,
        )
        self.assertEqual(
            refined_summary["refinement"]["fallbackCount"],
            MAX_REFINEMENT_CANDIDATES + 1,
        )
        self.assertIn(
            "budget was exhausted",
            next(
                event
                for event in refined
                if event["eventId"] == f"ingress-{MAX_REFINEMENT_CANDIDATES}"
            )["refinement"]["reason"],
        )

    def test_invalid_boundary_keeps_sampled_event_without_ephemeris_work(
        self,
    ) -> None:
        events, summary = sampled_events()
        ingress = next(
            event
            for event in events
            if event["eventType"] == "MEAN_RASHI_INGRESS"
        )
        invalid_ingress = {
            **ingress,
            "details": {
                **ingress["details"],
                "boundaryWrappedDeg": None,
            },
        }
        evaluation_count = 0

        def evaluator(_timestamp: float) -> tuple[float, ...]:
            nonlocal evaluation_count
            evaluation_count += 1
            return aligned_members(30.0)

        refined, _ = refine_collective_events(
            [invalid_ingress],
            summary,
            longitude_evaluator=evaluator,
            unstable_resultant_floor=1e-8,
        )

        self.assertEqual(
            refined[0]["refinement"]["status"],
            "SAMPLED_FALLBACK",
        )
        self.assertIn("boundary longitude", refined[0]["refinement"]["reason"])
        self.assertEqual(evaluation_count, 0)


if __name__ == "__main__":
    unittest.main()
