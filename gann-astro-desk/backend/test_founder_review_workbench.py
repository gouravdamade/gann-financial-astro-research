from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from founder_review_workbench import (
    FounderReviewIntegrityError,
    build_founder_review_workbench,
    export_founder_review_packet,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKET_RELATIVE = Path("research_labs/chart_conditioned_aspects/founder_review")
AUDIT_RELATIVE = Path("status/audits/pfr_v2b_r5_f2a_r1_event_identity_integrity.json")


class FounderReviewWorkbenchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        destination = self.root / PACKET_RELATIVE
        destination.mkdir(parents=True)
        source = PROJECT_ROOT / PACKET_RELATIVE
        for side in ("USD", "JPY"):
            for path in source.glob(f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1*"):
                shutil.copy2(path, destination / path.name)
        audit_destination = self.root / AUDIT_RELATIVE
        audit_destination.parent.mkdir(parents=True)
        shutil.copy2(PROJECT_ROOT / AUDIT_RELATIVE, audit_destination)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def load(self) -> dict:
        return build_founder_review_workbench(self.root)

    def test_all_rows_are_eligible_and_start_blank(self) -> None:
        workbench = self.load()
        self.assertEqual(workbench["contract"], "FOUNDER_REVIEW_WORKBENCH_V1")
        self.assertEqual(len(workbench["sides"]), 2)
        for side in workbench["sides"]:
            self.assertEqual(len(side["rows"]), 12)
            self.assertTrue(all(row["eligible"] for row in side["rows"]))
            self.assertTrue(all(row["identityStatus"] == "SINGLE_PASS_VERIFIED" for row in side["rows"]))
            self.assertTrue(all(row["founderReview"]["reviewedPolarity"] is None for row in side["rows"]))
            self.assertEqual(side["founderCompletionStatus"], "REVIEW_NOT_STARTED")
        self.assertFalse(workbench["guardrails"]["priceDataRead"])
        self.assertFalse(workbench["guardrails"]["sbcRead"])
        self.assertFalse(workbench["guardrails"]["llmRead"])

    def test_canonical_blank_packet_hash_is_verified_and_preserved(self) -> None:
        packet = self.root / PACKET_RELATIVE / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
        before = hashlib.sha256(packet.read_bytes()).hexdigest().upper()
        self.load()
        row = self.load()["sides"][0]["rows"][0]
        export_founder_review_packet(self.root, {"side": "USD", "rows": [row]})
        after = hashlib.sha256(packet.read_bytes()).hexdigest().upper()
        self.assertEqual(before, after)

    def test_lf_and_crlf_checkouts_verify_as_the_same_immutable_packet(self) -> None:
        packet = self.root / PACKET_RELATIVE / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
        packet.write_bytes(packet.read_bytes().replace(b"\r\n", b"\n"))
        workbench = self.load()
        self.assertTrue(all(row["eligible"] for row in workbench["sides"][0]["rows"]))

    def test_packet_hash_mismatch_fails_closed(self) -> None:
        packet = self.root / PACKET_RELATIVE / "JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
        packet.write_text(packet.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaises(FounderReviewIntegrityError):
            build_founder_review_workbench(self.root, requested_side="JPY")

    def test_partial_founder_hypothesis_export_is_research_only(self) -> None:
        side = self.load()["sides"][0]
        row = side["rows"][0]
        row["founderReview"] = {
            **row["founderReview"],
            "reviewedPolarity": "SUPPORTIVE",
            "evidenceClassification": "FOUNDER_RESEARCH_HYPOTHESIS",
            "founderReasoning": "Founder-entered research observation.",
            "reviewer": "Founder",
            "reviewTimestampUtc": "2026-08-06T12:00:00Z",
        }
        result = export_founder_review_packet(self.root, {"side": "USD", "rows": [row]})
        self.assertEqual(result["founderCompletionStatus"], "REVIEW_IN_PROGRESS")
        self.assertEqual(result["counts"]["decidedRows"], 1)
        self.assertEqual(result["counts"]["incompleteRows"], 11)
        reviewed = json.loads((self.root / PACKET_RELATIVE / result["reviewedPacketFile"]).read_text(encoding="utf-8"))
        self.assertFalse(reviewed["guardrails"]["catalogueEntryCreated"])
        self.assertFalse(reviewed["guardrails"]["polarityAssigned"])
        self.assertFalse(reviewed["guardrails"]["priceDataRead"])
        self.assertEqual(reviewed["rows"][0]["founderReview"]["reviewedPolarity"], "SUPPORTIVE")
        self.assertEqual(reviewed["rows"][1]["founderReview"]["reviewedPolarity"], None)

    def test_source_backed_requires_complete_exact_reference(self) -> None:
        side = self.load()["sides"][0]
        row = side["rows"][0]
        row["founderReview"] = {
            **row["founderReview"],
            "reviewedPolarity": "ADVERSE",
            "evidenceClassification": "SOURCE_BACKED_CLASSICAL_CANDIDATE",
            "reviewer": "Founder",
            "reviewTimestampUtc": "2026-08-06T12:00:00Z",
            "sourceReferences": [{"sourceId": "S1", "edition": "Edition", "locator": "p. 10", "connection": "Exact event rule."}],
        }
        result = export_founder_review_packet(self.root, {"side": "USD", "rows": [row]})
        self.assertEqual(result["counts"]["classicalCandidates"], 1)

        row["founderReview"]["sourceReferences"][0]["locator"] = ""
        with self.assertRaises(FounderReviewIntegrityError):
            export_founder_review_packet(self.root, {"side": "USD", "rows": [row]})

    def test_unknown_and_rejected_remain_explicit(self) -> None:
        side = self.load()["sides"][1]
        unknown = side["rows"][0]
        unknown["founderReview"] = {
            **unknown["founderReview"],
            "reviewedPolarity": "UNKNOWN_MORE_EVIDENCE_REQUIRED",
            "evidenceClassification": "FOUNDER_RESEARCH_HYPOTHESIS",
            "reviewer": "Founder",
            "reviewTimestampUtc": "2026-08-06T12:00:00Z",
        }
        rejected = side["rows"][1]
        rejected["founderReview"] = {
            **rejected["founderReview"],
            "reviewedPolarity": "REJECT_EVENT_IDENTITY",
            "rejectionReason": "Founder rejects the identity for follow-up.",
            "reviewer": "Founder",
            "reviewTimestampUtc": "2026-08-06T12:00:00Z",
        }
        result = export_founder_review_packet(self.root, {"side": "JPY", "rows": [unknown, rejected]})
        self.assertEqual(result["founderCompletionStatus"], "REVIEW_IN_PROGRESS")
        self.assertEqual(result["counts"]["unknownRows"], 1)
        self.assertEqual(result["counts"]["rejectedRows"], 1)
        self.assertEqual(result["counts"]["classicalCandidates"], 0)

    def test_rejected_identity_requires_reviewer(self) -> None:
        side = self.load()["sides"][1]
        row = side["rows"][0]
        row["founderReview"] = {
            **row["founderReview"],
            "reviewedPolarity": "REJECT_EVENT_IDENTITY",
            "rejectionReason": "Founder rejects the identity for follow-up.",
            "reviewer": "",
        }
        with self.assertRaises(FounderReviewIntegrityError):
            export_founder_review_packet(self.root, {"side": "JPY", "rows": [row]})

    def test_identity_mutation_and_unverified_rows_fail_closed(self) -> None:
        side = self.load()["sides"][0]
        row = side["rows"][0]
        row["eventIdentity"]["exactUtc"] = "2025-04-01T00:00:00Z"
        with self.assertRaises(FounderReviewIntegrityError):
            export_founder_review_packet(self.root, {"side": "USD", "rows": [row]})


if __name__ == "__main__":
    unittest.main()
