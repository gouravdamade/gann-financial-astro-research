from __future__ import annotations

import unittest

from chakra_lab_service import build_chakra_lab_snapshot


class ChakraLabServiceTests(unittest.TestCase):
    def test_valid_request_returns_locked_timestamp_safe_snapshot(self) -> None:
        snapshot = build_chakra_lab_snapshot(
            {
                "at": "2026-07-17T12:00:00+05:30",
                "timezone": "Asia/Kolkata",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "altitudeM": 216.0,
                "bodies": ["SUN", "MOON", "JUPITER"],
                "actors": [
                    {"body": "SUN"},
                    {"body": "MOON"},
                    {"body": "JUPITER", "motionClass": "MEAN"},
                ],
            }
        )

        self.assertEqual(snapshot["contract"], "SBC_CHAKRA_LAB_SNAPSHOT_V1")
        self.assertEqual(snapshot["as_of_utc"], "2026-07-17T06:30:00+00:00")
        self.assertEqual(
            snapshot["evidence_cutoff_utc"],
            snapshot["as_of_utc"],
        )
        self.assertTrue(snapshot["guardrails"]["read_only"])
        self.assertTrue(snapshot["guardrails"]["no_lookahead"])
        self.assertFalse(snapshot["guardrails"]["execution_allowed"])
        readiness = {
            item["body"]: item["status"] for item in snapshot["actor_readiness"]
        }
        self.assertEqual(readiness["JUPITER"], "READY")

    def test_missing_variable_motion_is_reported_not_inferred(self) -> None:
        snapshot = build_chakra_lab_snapshot(
            {
                "at": "2026-07-17T12:00:00+05:30",
                "actors": [{"body": "SUN"}, {"body": "SATURN"}],
            }
        )
        readiness = {
            item["body"]: item["status"] for item in snapshot["actor_readiness"]
        }
        self.assertEqual(readiness["SATURN"], "MOTION_REQUIRED")
        resolved = {item["body"] for item in snapshot["guidance"]["actor_resolutions"]}
        self.assertNotIn("SATURN", resolved)

    def test_naive_timestamp_and_unknown_fields_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "UTC offset"):
            build_chakra_lab_snapshot({"at": "2026-07-17T12:00:00"})
        with self.assertRaisesRegex(ValueError, "Unknown Chakra Lab request"):
            build_chakra_lab_snapshot(
                {
                    "at": "2026-07-17T12:00:00+05:30",
                    "marketPrice": 147.5,
                }
            )


if __name__ == "__main__":
    unittest.main()
