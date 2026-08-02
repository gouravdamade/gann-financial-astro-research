from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
