"""Synthetic-only tests for the MO-R4 Founder Review freeze utility."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import founder_review_freeze as freeze
import founder_review_workbench as fr
import test_founder_review_workbench as workbench_tests


class SyntheticFounderReviewFreezeTests(unittest.TestCase):
    """No test in this class reads the repository's real durable review root."""

    def setUp(self) -> None:
        self.fixture = workbench_tests.SyntheticFounderReviewFixture()
        self.fixture.setUp()
        self.candidate_manifest = self.fixture.temp_dir / "candidate-release.manifest.json"
        self.fixture._write_json(
            self.candidate_manifest,
            {
                "candidateVersion": "synthetic-founder-review-candidate",
                "version": "synthetic-founder-review-candidate",
                "implementationSourceCommit": "a" * 40,
                "sourceGitDirty": False,
                "executionAllowed": False,
            },
        )
        self.output_dir = self.fixture.temp_dir / "freeze-output"

    def tearDown(self) -> None:
        self.fixture.tearDown()

    def _write_review_rows(
        self,
        *,
        decision: str = "UNKNOWN_MORE_EVIDENCE_REQUIRED",
        classification: str | None = "FOUNDER_RESEARCH_HYPOTHESIS",
        skip: tuple[str, int] | None = None,
    ) -> None:
        workbench = self.fixture._build()
        for side in fr.SIDES:
            side_data = self.fixture._side(side, workbench)
            rows = [
                self.fixture._reviewed_row(
                    side_data,
                    index=index,
                    decision=decision,
                    classification=classification,
                    reasoning="Synthetic founder-only attestation reasoning",
                    references=(
                        [self.fixture._source_reference(f"{side}-{index}")]
                        if classification == "SOURCE_BACKED_CLASSICAL_CANDIDATE"
                        else None
                    ),
                )
                for index in range(12)
                if skip != (side, index)
            ]
            self.fixture._export(side, rows)

    def _prepare_complete(self, *, decision: str = "UNKNOWN_MORE_EVIDENCE_REQUIRED") -> None:
        self._write_review_rows(decision=decision)

    def _freeze(self, **overrides: object) -> dict:
        arguments: dict[str, object] = {
            "resource_root": self.fixture.resources,
            "review_root": self.fixture.review_root,
            "output_dir": self.output_dir,
            "founder_name": "Synthetic Founder",
            "candidate_release_manifest": self.candidate_manifest,
            "attestation_text": "[SYNTHETIC TEST ONLY] No outcome, price, return, PnL, or post-event data was used.",
            "expected_audit_sha256": self.fixture.audit_hash,
            "freeze_id": "synthetic-freeze-001",
            "server_created_at_utc": "2026-09-09T12:00:00Z",
        }
        arguments.update(overrides)
        return freeze.freeze_founder_review(**arguments)

    def _mutate_current_packet(self, side: str, mutator) -> None:
        pointer_path = self.fixture.review_root / "current" / f"{side}.json"
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        packet_path = self.fixture.review_root / pointer["revisionDirectory"] / "reviewed_packet.json"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        mutator(packet)
        self.fixture._write_json(packet_path, packet)

    def _assert_freeze_rejects(self) -> None:
        with self.assertRaises(freeze.FounderReviewFreezeError):
            self._freeze()

    def test_complete_24_row_freeze_succeeds(self) -> None:
        self._prepare_complete()
        result = self._freeze()
        document = result["freeze"]
        self.assertEqual(len(document["reviewRows"]), 24)
        self.assertEqual(sum(row["sideIdentity"] == "USD" for row in document["reviewRows"]), 12)
        self.assertEqual(sum(row["sideIdentity"] == "JPY" for row in document["reviewRows"]), 12)
        self.assertEqual(document["decisionCategoryCounts"]["UNKNOWN_MORE_EVIDENCE_REQUIRED"], 24)
        self.assertEqual(document["evidenceCategoryCounts"]["FOUNDER_RESEARCH_HYPOTHESIS"], 24)
        self.assertEqual(document["state"]["FOUNDER_POLARITY_REVIEW"], "FROZEN_PENDING_CENTRAL_REVIEW")
        self.assertFalse(document["executionAllowed"])
        self.assertTrue(Path(result["files"]["json"]).is_file())
        self.assertTrue(Path(result["files"]["markdown"]).is_file())
        self.assertTrue(Path(result["files"]["sha256sums"]).is_file())

    def test_missing_row_fails(self) -> None:
        self._write_review_rows(skip=("USD", 11))
        self._assert_freeze_rejects()

    def test_duplicate_row_fails(self) -> None:
        self._prepare_complete()

        def duplicate(packet: dict) -> None:
            packet["rows"][1]["eventIdentity"] = copy.deepcopy(packet["rows"][0]["eventIdentity"])

        self._mutate_current_packet("USD", duplicate)
        self._assert_freeze_rejects()

    def test_foreign_identity_fails(self) -> None:
        self._prepare_complete()

        def foreign(packet: dict) -> None:
            packet["rows"][0]["eventIdentity"]["eventId"] = "FOREIGN-EVENT"

        self._mutate_current_packet("USD", foreign)
        self._assert_freeze_rejects()

    def test_modified_event_hash_fails(self) -> None:
        self._prepare_complete()

        def modified(packet: dict) -> None:
            packet["rows"][0]["eventIdentity"]["eventHash"] = "b" * 64

        self._mutate_current_packet("USD", modified)
        self._assert_freeze_rejects()

    def test_modified_blank_packet_binding_fails(self) -> None:
        self._prepare_complete()

        def modified(packet: dict) -> None:
            packet["blankPacketSha256"] = "bad-blank-packet-binding"

        self._mutate_current_packet("USD", modified)
        self._assert_freeze_rejects()

    def test_modified_identity_manifest_binding_fails(self) -> None:
        self._prepare_complete()

        def modified(packet: dict) -> None:
            packet["identityIntegrityManifestSha256"] = "bad-identity-manifest-binding"

        self._mutate_current_packet("USD", modified)
        self._assert_freeze_rejects()

    def test_broken_revision_parent_chain_fails(self) -> None:
        self._prepare_complete()

        def broken(packet: dict) -> None:
            packet["previousRevisionHash"] = "c" * 64

        self._mutate_current_packet("USD", broken)
        self._assert_freeze_rejects()

    def test_incomplete_decision_fails(self) -> None:
        self._write_review_rows(skip=("JPY", 0))
        self._assert_freeze_rejects()

    def test_invalid_decision_enum_fails(self) -> None:
        self._prepare_complete()

        def invalid(packet: dict) -> None:
            packet["rows"][0]["founderReview"]["reviewedPolarity"] = "BUY"

        self._mutate_current_packet("USD", invalid)
        self._assert_freeze_rejects()

    def test_supportive_without_reasoning_fails(self) -> None:
        self._prepare_complete()

        def missing_reason(packet: dict) -> None:
            review = packet["rows"][0]["founderReview"]
            review["reviewedPolarity"] = "SUPPORTIVE"
            review["founderReasoning"] = ""

        self._mutate_current_packet("USD", missing_reason)
        self._assert_freeze_rejects()

    def test_adverse_without_reasoning_fails(self) -> None:
        self._prepare_complete()

        def missing_reason(packet: dict) -> None:
            review = packet["rows"][0]["founderReview"]
            review["reviewedPolarity"] = "ADVERSE"
            review["founderReasoning"] = ""

        self._mutate_current_packet("USD", missing_reason)
        self._assert_freeze_rejects()

    def test_non_rejected_without_evidence_class_fails(self) -> None:
        self._prepare_complete()

        def missing_class(packet: dict) -> None:
            packet["rows"][0]["founderReview"]["evidenceClassification"] = None

        self._mutate_current_packet("USD", missing_class)
        self._assert_freeze_rejects()

    def test_source_backed_missing_locator_fails(self) -> None:
        self._write_review_rows(classification="SOURCE_BACKED_CLASSICAL_CANDIDATE")

        def missing_locator(packet: dict) -> None:
            review = packet["rows"][0]["founderReview"]
            review["evidenceClassification"] = "SOURCE_BACKED_CLASSICAL_CANDIDATE"
            review["sourceReferences"] = [{"sourceId": "SYNTH_SOURCE", "edition": "Synthetic edition"}]

        self._mutate_current_packet("USD", missing_locator)
        self._assert_freeze_rejects()

    def test_reject_without_reason_fails(self) -> None:
        self._prepare_complete()

        def missing_rejection_reason(packet: dict) -> None:
            review = packet["rows"][0]["founderReview"]
            review["reviewedPolarity"] = "REJECT_EVENT_IDENTITY"
            review["evidenceClassification"] = None
            review["founderReasoning"] = ""
            review["rejectionReason"] = ""

        self._mutate_current_packet("USD", missing_rejection_reason)
        self._assert_freeze_rejects()

    def test_unknown_is_genuine_without_numeric_value(self) -> None:
        self._prepare_complete()
        document = self._freeze()["freeze"]
        self.assertEqual(document["decisionCategoryCounts"]["UNKNOWN_MORE_EVIDENCE_REQUIRED"], 24)
        self.assertNotIn("score", json.dumps(document).lower())
        self.assertNotIn("numericValue", json.dumps(document))

    def test_mixed_is_genuine_without_numeric_value(self) -> None:
        self._prepare_complete(decision="MIXED")
        document = self._freeze()["freeze"]
        self.assertEqual(document["decisionCategoryCounts"]["MIXED"], 24)
        self.assertFalse(document["guardrails"]["numericNormalization"])
        self.assertNotIn("signedValue", json.dumps(document))

    def test_zero_supportive_adverse_is_valid(self) -> None:
        self._prepare_complete(decision="NEUTRAL")
        document = self._freeze()["freeze"]
        self.assertEqual(document["decisionCategoryCounts"]["SUPPORTIVE"], 0)
        self.assertEqual(document["decisionCategoryCounts"]["ADVERSE"], 0)
        self.assertEqual(document["decisionCategoryCounts"]["NEUTRAL"], 24)

    def test_missing_human_attestation_fails(self) -> None:
        self._prepare_complete()
        with self.assertRaises(freeze.FounderReviewFreezeError):
            self._freeze(attestation_text="")

    def test_existing_output_path_fails_closed(self) -> None:
        self._prepare_complete()
        self._freeze()
        with self.assertRaises(freeze.FreezeOutputExistsError):
            self._freeze()

    def test_interrupted_publication_leaves_no_bundle(self) -> None:
        self._prepare_complete()

        def interrupt() -> None:
            raise RuntimeError("synthetic publication interruption")

        with self.assertRaises(RuntimeError):
            self._freeze(publish_hook=interrupt)
        self.assertFalse(self.output_dir.exists() and any(self.output_dir.iterdir()))

    def test_review_store_bytes_unchanged(self) -> None:
        self._prepare_complete()
        before = {
            str(path.relative_to(self.fixture.review_root)): path.read_bytes()
            for path in self.fixture.review_root.rglob("*")
            if path.is_file()
        }
        self._freeze()
        after = {
            str(path.relative_to(self.fixture.review_root)): path.read_bytes()
            for path in self.fixture.review_root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_no_catalogue_write_or_admission_field(self) -> None:
        self._prepare_complete()
        result = self._freeze()
        document = result["freeze"]
        self.assertFalse(document["guardrails"]["catalogueAdmission"])
        self.assertFalse(document["guardrails"]["modeOneAdmission"])
        self.assertFalse(document["guardrails"]["modeTwoAdmission"])

    def test_no_evidence_registry_write_or_admission_field(self) -> None:
        self._prepare_complete()
        document = self._freeze()["freeze"]
        self.assertFalse(document["guardrails"]["evidenceAdmission"])
        self.assertEqual(document["state"]["PRODUCTION_POLARITY_ADMISSION"], "NOT_STARTED")

    def test_no_price_or_outcome_access_and_no_market_content(self) -> None:
        self._prepare_complete()
        document = self._freeze()["freeze"]
        self.assertFalse(document["guardrails"]["priceDataRead"])
        self.assertFalse(document["guardrails"]["priceOutcomeRead"])
        self.assertFalse(document["guardrails"]["marketDirectionInferred"])
        self.assertEqual(document["state"]["OUTCOME_ANALYSIS"], "NOT_STARTED")
        for row in document["reviewRows"]:
            self.assertNotIn("price", {key.lower() for key in row["eventIdentity"]})
            self.assertNotIn("pnl", {key.lower() for key in row["eventIdentity"]})
            self.assertNotIn("outcome", {key.lower() for key in row["eventIdentity"]})

    def test_execution_allowed_false(self) -> None:
        self._prepare_complete()
        document = self._freeze()["freeze"]
        self.assertFalse(document["executionAllowed"])
        self.assertFalse(document["guardrails"]["executionAllowed"])
        self.assertEqual(document["state"]["SIGNED_USD_WAVE"], "NOT_AUTHORIZED")
        self.assertEqual(document["state"]["SIGNED_JPY_WAVE"], "NOT_AUTHORIZED")
        self.assertEqual(document["state"]["SIGNED_USDJPY_RESULTANT"], "NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()
