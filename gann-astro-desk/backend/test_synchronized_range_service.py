from __future__ import annotations

import unittest
from unittest.mock import patch

from synchronized_range_service import build_synchronized_independent_range


def _side_result(side: str, start: str, end: str) -> dict:
    return {
        "rangeStartUtc": start,
        "rangeEndUtc": end,
        "instrumentId": f"FX_CURRENCY:{side}",
        "chartId": f"{side}-CANONICAL-CHART",
        "chartHypothesisId": f"{side}-CANONICAL-HYPOTHESIS",
        "intervals": [{
            "intervalId": f"{side}_0001",
            "startUtc": start,
            "endUtc": end,
            "polarityState": "UNKNOWN",
            "supportiveActive": False,
            "adverseActive": False,
            "activeEventIds": [f"TN_{side}_REAL"],
            "unknownEventIds": [f"TN_{side}_REAL"],
            "reason": "Unreviewed real event.",
        }],
        "guardrails": {"executionAllowed": False},
    }


class SynchronizedRangeServiceTests(unittest.TestCase):
    @staticmethod
    def _request() -> dict:
        return {
            "rangeStartUtc": "2026-07-17T06:30:00Z",
            "rangeEndUtc": "2026-07-17T08:30:00Z",
            "sideIdentities": ["USD", "JPY"],
            "aspectProfileId": "ASPECT_STRENGTH_V0",
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

    @staticmethod
    def _compiler(payload: dict) -> dict:
        return _side_result(
            payload["sideIdentity"],
            payload["rangeStartUtc"],
            payload["rangeEndUtc"],
        )

    def test_fields_share_the_exact_range_without_fusion(self) -> None:
        with patch("synchronized_range_service.build_chart_conditioned_polarity_range", side_effect=self._compiler) as compiler:
            result = build_synchronized_independent_range(self._request())

        self.assertEqual(result["contract"], "SYNCHRONIZED_INDEPENDENT_RANGE_V1")
        self.assertEqual(result["schemaVersion"], 2)
        self.assertEqual(result["synchronizationStatus"], "SYNCHRONIZED")
        self.assertEqual(set(result["aspectFields"]), {"USD", "JPY"})
        self.assertEqual(result["aspectFields"]["USD"]["rangeStartUtc"], result["rangeStartUtc"])
        self.assertEqual(result["aspectFields"]["JPY"]["rangeEndUtc"], result["rangeEndUtc"])
        self.assertEqual(result["sbcField"]["range_start_utc"].replace("+00:00", "Z"), result["rangeStartUtc"])
        self.assertFalse(result["guardrails"]["fieldsFused"])
        self.assertFalse(result["guardrails"]["marketDirectionInferred"])
        self.assertEqual(
            [call.args[0]["sideIdentity"] for call in compiler.call_args_list],
            ["USD", "JPY"],
        )
        for call in compiler.call_args_list:
            self.assertNotIn("events", call.args[0])
            self.assertNotIn("chartId", call.args[0])

    def test_sbc_range_start_must_match_the_shared_selection(self) -> None:
        request = self._request()
        request["sbcRange"]["boundaries"][0]["request"]["at"] = "2026-07-17T12:15:00+05:30"

        with patch("synchronized_range_service.build_chart_conditioned_polarity_range", side_effect=self._compiler):
            with self.assertRaisesRegex(ValueError, "shared visible range start"):
                build_synchronized_independent_range(request)

    def test_trailokya_geometry_profile_keeps_side_fields_available_without_scored_sbc(self) -> None:
        request = self._request()
        request["sbcRange"]["boundaries"][0]["request"]["vedhaProfileId"] = "SBC_TRAILOKYA_1972_V1"

        with patch("synchronized_range_service.build_chart_conditioned_polarity_range", side_effect=self._compiler), patch(
            "synchronized_range_service.build_chakra_lab_atomic_range",
            side_effect=AssertionError("ordinary atomic range must not be constructed"),
        ), patch(
            "sbc.chakra_lab.VedhaGuidanceEngine",
            side_effect=AssertionError("scored Vedha engine must not be constructed"),
        ):
            result = build_synchronized_independent_range(request)

        self.assertEqual(set(result["aspectFields"]), {"USD", "JPY"})
        self.assertEqual(result["sbcField"]["state"], "GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED")
        self.assertEqual(result["sbcField"]["intervals"], [])
        self.assertFalse(result["sbcField"]["guardrails"]["score_aggregation_used"])
        self.assertNotIn("phaladeepika", str(result["sbcField"]).lower())

    def test_frontend_cannot_supply_chart_or_event_payloads(self) -> None:
        request = self._request()
        request["events"] = []
        with self.assertRaisesRegex(ValueError, "Unknown synchronized range request"):
            build_synchronized_independent_range(request)


if __name__ == "__main__":
    unittest.main()
