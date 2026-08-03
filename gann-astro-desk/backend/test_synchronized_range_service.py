from __future__ import annotations

import unittest
from unittest.mock import patch

from synchronized_range_service import build_synchronized_independent_range


class SynchronizedRangeServiceTests(unittest.TestCase):
    @staticmethod
    def _request() -> dict:
        return {
            "rangeStartUtc": "2026-07-17T06:30:00Z",
            "rangeEndUtc": "2026-07-17T08:30:00Z",
            "aspectRanges": [
                {
                    "sideIdentity": "USD",
                    "instrumentIdentity": "FX_CURRENCY:USD",
                    "chartId": "USD-TEST",
                    "chartHypothesisId": "USD-HYPOTHESIS-001",
                    "events": [],
                },
                {
                    "sideIdentity": "JPY",
                    "instrumentIdentity": "FX_CURRENCY:JPY",
                    "chartId": "JPY-TEST",
                    "chartHypothesisId": "JPY-HYPOTHESIS-001",
                    "events": [],
                },
            ],
            "sbcRange": {
                "instrumentIdentity": "FX:USDJPY",
                "boundaries": [
                    {
                        "reason": "visible range start",
                        "request": {
                            "at": "2026-07-17T12:00:00+05:30",
                            "actors": [{"body": "SUN"}],
                        },
                    },
                ],
            },
        }

    def test_fields_share_the_exact_range_without_fusion(self) -> None:
        result = build_synchronized_independent_range(self._request())

        self.assertEqual(result["contract"], "SYNCHRONIZED_INDEPENDENT_RANGE_V1")
        self.assertEqual(result["synchronizationStatus"], "SYNCHRONIZED")
        self.assertEqual(set(result["aspectFields"]), {"USD", "JPY"})
        self.assertEqual(
            result["aspectFields"]["USD"]["rangeStartUtc"],
            result["rangeStartUtc"],
        )
        self.assertEqual(
            result["aspectFields"]["JPY"]["rangeEndUtc"],
            result["rangeEndUtc"],
        )
        self.assertEqual(
            result["sbcField"]["range_start_utc"].replace("+00:00", "Z"),
            result["rangeStartUtc"],
        )
        self.assertFalse(result["guardrails"]["fieldsFused"])
        self.assertFalse(result["guardrails"]["marketDirectionInferred"])

    def test_sbc_range_start_must_match_the_shared_selection(self) -> None:
        request = self._request()
        request["sbcRange"]["boundaries"][0]["request"]["at"] = (
            "2026-07-17T12:15:00+05:30"
        )

        with self.assertRaisesRegex(ValueError, "shared visible range start"):
            build_synchronized_independent_range(request)

    def test_trailokya_geometry_profile_keeps_side_fields_available_without_scored_sbc(self) -> None:
        request = self._request()
        request["sbcRange"]["boundaries"][0]["request"]["vedhaProfileId"] = (
            "SBC_TRAILOKYA_1972_V1"
        )

        with patch(
            "synchronized_range_service.build_chakra_lab_atomic_range",
            side_effect=AssertionError("ordinary atomic range must not be constructed"),
        ), patch(
            "sbc.chakra_lab.VedhaGuidanceEngine",
            side_effect=AssertionError("scored Vedha engine must not be constructed"),
        ):
            result = build_synchronized_independent_range(request)

        self.assertEqual(set(result["aspectFields"]), {"USD", "JPY"})
        self.assertEqual(result["aspectFields"]["USD"]["rangeStartUtc"], result["rangeStartUtc"])
        self.assertEqual(result["aspectFields"]["JPY"]["rangeEndUtc"], result["rangeEndUtc"])
        self.assertEqual(
            result["sbcField"]["state"],
            "GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED",
        )
        self.assertEqual(result["sbcField"]["intervals"], [])
        self.assertFalse(result["sbcField"]["guardrails"]["score_aggregation_used"])
        self.assertNotIn("phaladeepika", str(result["sbcField"]).lower())
        self.assertNotIn("trailokya_dipika_1972_vedha_guidance_v1", str(result["sbcField"]).lower())


if __name__ == "__main__":
    unittest.main()
