from __future__ import annotations

import unittest

from chakra_lab_service import build_chakra_lab_audit, build_chakra_lab_snapshot


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

    def test_explicit_boundaries_compile_linked_read_only_audit(self) -> None:
        request = {
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
        audit = build_chakra_lab_audit(
            {
                "instrumentIdentity": "FX:USDJPY",
                "terminalEnd": "2026-07-17T15:00:00+05:30",
                "boundaries": [
                    {
                        "reason": "review start",
                        "request": {
                            **request,
                            "at": "2026-07-17T12:00:00+05:30",
                        },
                    },
                    {
                        "reason": "review midpoint",
                        "request": {
                            **request,
                            "at": "2026-07-17T13:00:00+05:30",
                        },
                    },
                ],
            }
        )

        self.assertEqual(audit["contract"], "SBC_LINKED_AUDIT_VIEW_V1")
        self.assertEqual(audit["instrument_identity"], "FX:USDJPY")
        self.assertEqual(len(audit["intervals"]), 2)
        self.assertEqual(audit["intervals"][0]["duration_seconds"], 3600)
        self.assertEqual(audit["intervals"][1]["duration_seconds"], 7200)
        self.assertFalse(audit["guardrails"]["phase_included"])
        self.assertFalse(audit["guardrails"]["execution_allowed"])
        self.assertTrue(
            all(item["reconciled"] for item in audit["reconciliations"])
        )

    def test_audit_preserves_missing_guidance_as_unknown(self) -> None:
        audit = build_chakra_lab_audit(
            {
                "instrumentIdentity": "FX:USDJPY",
                "terminalEnd": "2026-07-17T13:00:00+05:30",
                "boundaries": [
                    {
                        "reason": "no actors selected",
                        "request": {
                            "at": "2026-07-17T12:00:00+05:30",
                            "actors": [],
                        },
                    },
                ],
            }
        )

        unknown = {
            item["gate_id"]: item["state"] for item in audit["validation_gates"]
        }
        self.assertEqual(unknown["UNKNOWN_EVIDENCE"], "UNKNOWN")
        self.assertTrue(
            any(
                item["unknown_reason"]
                == "Explicit missing evidence: VEDHA_GUIDANCE_NOT_AVAILABLE"
                for item in audit["ray_rows"]
            )
        )

    def test_audit_rejects_naive_terminal_and_duplicate_boundaries(self) -> None:
        boundary = {
            "reason": "duplicate",
            "request": {
                "at": "2026-07-17T12:00:00+05:30",
                "actors": [{"body": "SUN"}],
            },
        }
        with self.assertRaisesRegex(ValueError, "terminalEnd must include"):
            build_chakra_lab_audit(
                {
                    "instrumentIdentity": "FX:USDJPY",
                    "terminalEnd": "2026-07-17T13:00:00",
                    "boundaries": [boundary],
                }
            )
        with self.assertRaisesRegex(ValueError, "timestamps must be unique"):
            build_chakra_lab_audit(
                {
                    "instrumentIdentity": "FX:USDJPY",
                    "terminalEnd": "2026-07-17T13:00:00+05:30",
                    "boundaries": [boundary, boundary],
                }
            )


if __name__ == "__main__":
    unittest.main()
