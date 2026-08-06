from __future__ import annotations

import unittest
from unittest.mock import patch

from chart_conditioned_transit_event_service import (
    build_chart_conditioned_transit_event_range,
)


class ChartConditionedTransitEventServiceTests(unittest.TestCase):
    def _request(self) -> dict:
        return {
            "sideIdentity": "USD",
            "rangeStartUtc": "2025-04-01T00:00:00Z",
            "rangeEndUtc": "2025-05-01T00:00:00Z",
            "aspectProfileId": "ASPECT_STRENGTH_V0",
        }

    def test_service_forwards_only_the_allowed_backend_contract(self) -> None:
        expected = {"contract": "CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1", "events": []}
        with patch(
            "chart_conditioned_transit_event_service.compile_chart_conditioned_transit_event_range",
            return_value=expected,
        ) as compiler:
            result = build_chart_conditioned_transit_event_range(self._request())

        self.assertIs(result, expected)
        compiler.assert_called_once_with(
            side_identity="USD",
            range_start_utc="2025-04-01T00:00:00Z",
            range_end_utc="2025-05-01T00:00:00Z",
            aspect_profile_id="ASPECT_STRENGTH_V0",
        )

    def test_frontend_chart_and_event_identity_injection_fails_closed(self) -> None:
        for key, value in (
            ("chartId", "FRONTEND-INVENTED-CHART"),
            ("chartHypothesisId", "FRONTEND-INVENTED-HYPOTHESIS"),
            ("events", []),
            ("transitBody", "MARS"),
        ):
            with self.subTest(key=key):
                request = self._request()
                request[key] = value
                with self.assertRaisesRegex(ValueError, "Unknown chart-conditioned event range"):
                    build_chart_conditioned_transit_event_range(request)


if __name__ == "__main__":
    unittest.main()
