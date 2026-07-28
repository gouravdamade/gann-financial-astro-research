from __future__ import annotations

import copy
import unittest

from chakra_lab_service import (
    build_chakra_lab_audit,
    build_chakra_lab_audit_package,
    build_chakra_lab_snapshot,
    verify_chakra_lab_audit_package,
)


class ChakraLabServiceTests(unittest.TestCase):
    @staticmethod
    def _browser_json_numbers(value):
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, dict):
            return {
                key: ChakraLabServiceTests._browser_json_numbers(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [
                ChakraLabServiceTests._browser_json_numbers(item)
                for item in value
            ]
        return value

    @staticmethod
    def _two_interval_audit_request() -> dict:
        shared = {
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
        return {
            "instrumentIdentity": "FX:USDJPY",
            "terminalEnd": "2026-07-17T15:00:00+05:30",
            "boundaries": [
                {
                    "reason": "review start",
                    "request": {
                        **shared,
                        "at": "2026-07-17T12:00:00+05:30",
                    },
                },
                {
                    "reason": "review midpoint",
                    "request": {
                        **shared,
                        "at": "2026-07-17T13:00:00+05:30",
                    },
                },
            ],
        }

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
        audit = build_chakra_lab_audit(self._two_interval_audit_request())

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

    def test_audit_package_recomputes_exports_and_replays(self) -> None:
        audit_request = self._two_interval_audit_request()
        audit = build_chakra_lab_audit(audit_request)
        package_request = {
            "auditRequest": audit_request,
            "baselineIntervalId": audit["intervals"][0]["interval_id"],
            "comparisonIntervalIds": [audit["intervals"][1]["interval_id"]],
            "bookmarks": [
                {
                    "targetType": "INTERVAL",
                    "targetId": audit["intervals"][1]["interval_id"],
                    "label": "Manual contrast",
                    "note": "Research observation only.",
                    "createdAt": "2026-07-17T16:00:00+05:30",
                }
            ],
            "sealedAt": "2026-07-17T16:30:00+05:30",
        }
        result = build_chakra_lab_audit_package(package_request)
        package = result["package"]

        self.assertEqual(
            package["contract"],
            "SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1",
        )
        self.assertEqual(package["source_audit_id"], audit["audit_view_id"])
        self.assertEqual(len(package["comparisons"]), 1)
        self.assertEqual(
            package["bookmarks"][0]["annotation_role"],
            "MANUAL_RESEARCH_ANNOTATION_ONLY",
        )
        self.assertFalse(package["guardrails"]["execution_allowed"])
        self.assertIn("Reproducible SBC Audit Package", result["htmlReport"])

        verification = verify_chakra_lab_audit_package({"package": package})
        self.assertEqual(verification["state"], "PASS")
        self.assertTrue(verification["replay_audit_match"])
        self.assertTrue(verification["replay_package_match"])

    def test_audit_package_survives_browser_numeric_json_round_trip(self) -> None:
        audit_request = self._two_interval_audit_request()
        audit = build_chakra_lab_audit(audit_request)
        result = build_chakra_lab_audit_package(
            {
                "auditRequest": audit_request,
                "baselineIntervalId": audit["intervals"][0]["interval_id"],
                "comparisonIntervalIds": [audit["intervals"][1]["interval_id"]],
                "bookmarks": [],
                "sealedAt": "2026-07-17T16:30:00+05:30",
            }
        )
        transported = self._browser_json_numbers(copy.deepcopy(result["package"]))

        verification = verify_chakra_lab_audit_package({"package": transported})

        self.assertEqual(verification["state"], "PASS")
        self.assertTrue(verification["replay_package_match"])

    def test_audit_package_tampering_returns_failed_verification(self) -> None:
        audit_request = self._two_interval_audit_request()
        audit = build_chakra_lab_audit(audit_request)
        result = build_chakra_lab_audit_package(
            {
                "auditRequest": audit_request,
                "baselineIntervalId": audit["intervals"][0]["interval_id"],
                "comparisonIntervalIds": [audit["intervals"][1]["interval_id"]],
                "bookmarks": [],
                "sealedAt": "2026-07-17T16:30:00+05:30",
            }
        )
        result["package"]["instrument_identity"] = "FX:EURUSD"

        verification = verify_chakra_lab_audit_package(
            {"package": result["package"]}
        )
        self.assertEqual(verification["state"], "FAIL")
        self.assertIn("hash", verification["errors"][0])

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
