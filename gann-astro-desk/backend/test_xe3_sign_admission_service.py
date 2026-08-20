from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from xe3_sign_admission_service import (
    Xe3SignAdmissionIntegrityError,
    _review_projection,
    build_xe3_preregistration_status,
    build_xe3_signed_ledger,
    build_xe3_transform_comparison,
    build_xe3_workbench,
    freeze_xe3_preregistration,
    save_xe3_review_revision,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKET_DIRECTORY = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects" / "founder_review"
PREREGISTRATION_CONTRACT = PROJECT_ROOT / "research_labs" / "experimental_evidence" / "fixtures" / "xe3_preregistration_contract_v1.json"


def reviewed_rows(rows: list[dict], *, decision: str = "NEUTRAL") -> list[dict]:
    submitted = copy.deepcopy(rows)
    for row in submitted:
        row["review"] = {
            "decision": decision,
            "evidenceClassification": "FOUNDER_RESEARCH_HYPOTHESIS",
            "reasoning": "Founder-entered outcome-blind research rationale.",
            "rejectionReason": "",
            "reviewer": "Founder",
            "reviewTimestampUtc": None,
            "sourceReferences": [],
            "outcomeBlindAttestation": True,
            "priceDataRead": False,
        }
    return submitted


class Xe3SignAdmissionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.storage_root = Path(self.temporary_directory.name) / "xe3_store"
        self.usd_packet = PACKET_DIRECTORY / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
        self.usd_packet_hash_before = hashlib.sha256(self.usd_packet.read_bytes()).hexdigest().upper()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def workbench(self) -> dict:
        return build_xe3_workbench(PROJECT_ROOT, storage_root=self.storage_root)

    @staticmethod
    def side(workbench: dict, identity: str) -> dict:
        return next(item for item in workbench["sides"] if item["sideIdentity"] == identity)

    def save(self, side: dict, rows: list[dict]) -> dict:
        return save_xe3_review_revision(
            PROJECT_ROOT,
            {
                "side": side["sideIdentity"],
                "baseRevisionHash": side["latestReviewRevisionHash"],
                "reviewer": "Founder",
                "outcomeBlindAttestation": True,
                "rows": rows,
            },
            storage_root=self.storage_root,
        )

    def test_blank_packets_are_verified_and_price_paths_are_absent(self) -> None:
        workbench = self.workbench()
        self.assertEqual(workbench["datasetStatus"], "TOUCHED_DEV")
        self.assertEqual(len(workbench["sides"]), 2)
        self.assertTrue(all(len(side["rows"]) == 12 for side in workbench["sides"]))
        self.assertTrue(all(row["identityStatus"] == "SINGLE_PASS_VERIFIED" for side in workbench["sides"] for row in side["rows"]))
        self.assertTrue(all(row["review"]["decision"] is None for side in workbench["sides"] for row in side["rows"]))
        self.assertFalse(workbench["guardrails"]["priceDataRead"])
        self.assertFalse(workbench["guardrails"]["priceOutcomeRead"])
        self.assertFalse(workbench["guardrails"]["liveMt5Read"])
        self.assertFalse(workbench["guardrails"]["sbcRead"])
        self.assertFalse(workbench["guardrails"]["executionAllowed"])
        self.assertEqual(self.usd_packet_hash_before, hashlib.sha256(self.usd_packet.read_bytes()).hexdigest().upper())

    def test_concurrent_startup_reads_serialize_the_shared_ledger_index(self) -> None:
        # The packaged panel loads the workbench, ledger, transform preview and
        # preregistration together. These reads must remain independently safe
        # when they refresh the same append-only index on Windows.
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(
                executor.map(
                    lambda builder: builder(PROJECT_ROOT, storage_root=self.storage_root),
                    (
                        build_xe3_workbench,
                        build_xe3_signed_ledger,
                        build_xe3_preregistration_status,
                        build_xe3_signed_ledger,
                    ),
                )
            )
        self.assertEqual(len(results[0]["sides"]), 2)
        self.assertEqual(len(results[1]["entries"]), 0)
        self.assertEqual(results[2]["status"], "NOT_FROZEN")
        self.assertEqual(results[3]["ledgerHash"], results[1]["ledgerHash"])
        self.assertFalse((self.storage_root / "index.tmp").exists())

    def test_identity_mutation_and_price_claimed_sign_fail_closed(self) -> None:
        usd = self.side(self.workbench(), "USD")
        mutated = copy.deepcopy(usd["rows"])
        mutated[0]["eventIdentity"]["exactUtc"] = "2025-04-02T00:00:00Z"
        with self.assertRaises(Xe3SignAdmissionIntegrityError):
            self.save(usd, mutated)

        untrusted = copy.deepcopy(usd["rows"])
        untrusted[0]["review"] = {
            "decision": "SUPPORTIVE",
            "evidenceClassification": "FOUNDER_RESEARCH_HYPOTHESIS",
            "reasoning": "Founder-entered research rationale.",
            "reviewer": "Founder",
            "reviewTimestampUtc": None,
            "sourceReferences": [],
            "outcomeBlindAttestation": True,
            "priceDataRead": True,
            "rejectionReason": "",
        }
        with self.assertRaises(Xe3SignAdmissionIntegrityError):
            self.save(usd, untrusted)

    def test_append_only_revision_and_scalar_projection_are_explicit(self) -> None:
        usd = self.side(self.workbench(), "USD")
        result = self.save(usd, reviewed_rows(usd["rows"], decision="SUPPORTIVE"))
        revision_path = self.storage_root / "revisions" / "USD" / f"{result['reviewRevisionHash']}.json"
        self.assertTrue(revision_path.exists())
        self.assertEqual(result["completion"]["status"], "REVIEW_COMPLETE")
        ledger = build_xe3_signed_ledger(PROJECT_ROOT, storage_root=self.storage_root)
        self.assertEqual(len(ledger["entries"]), 12)
        self.assertTrue(all(entry["scalarProjection"]["value"] == 1.0 for entry in ledger["entries"]))
        self.assertEqual(_review_projection({"decision": "NEUTRAL"})["value"], 0.0)
        self.assertIsNone(_review_projection({"decision": "MIXED"})["value"])
        self.assertIsNone(_review_projection({"decision": "UNKNOWN_MORE_EVIDENCE_REQUIRED"})["value"])
        self.assertIsNone(_review_projection({"decision": "REJECT_EVENT_IDENTITY"})["value"])
        self.assertEqual(self.usd_packet_hash_before, hashlib.sha256(self.usd_packet.read_bytes()).hexdigest().upper())

    def test_preregistration_requires_terminal_review_of_both_sides(self) -> None:
        initial = build_xe3_preregistration_status(PROJECT_ROOT, storage_root=self.storage_root)
        self.assertEqual(initial["status"], "NOT_FROZEN")
        self.assertFalse(initial["freezeReady"])
        with self.assertRaises(Xe3SignAdmissionIntegrityError):
            freeze_xe3_preregistration(
                PROJECT_ROOT,
                {"ledgerHash": initial["ledgerHash"], "sourceCommit": "a" * 40, "outcomeBlindAttestation": True},
                storage_root=self.storage_root,
            )

        current = self.workbench()
        self.save(self.side(current, "USD"), reviewed_rows(self.side(current, "USD")["rows"]))
        current = self.workbench()
        self.save(self.side(current, "JPY"), reviewed_rows(self.side(current, "JPY")["rows"]))
        ready = build_xe3_preregistration_status(PROJECT_ROOT, storage_root=self.storage_root)
        self.assertTrue(ready["freezeReady"])
        frozen = freeze_xe3_preregistration(
            PROJECT_ROOT,
            {"ledgerHash": ready["ledgerHash"], "sourceCommit": "a" * 40, "outcomeBlindAttestation": True},
            storage_root=self.storage_root,
        )
        self.assertEqual(frozen["status"], "FROZEN")
        self.assertEqual(frozen["outcomeContractStatus"], "NOT_YET_FOUNDER_APPROVED")
        self.assertEqual(frozen["frozenRecord"]["sourceCommit"], "a" * 40)
        self.assertFalse(frozen["guardrails"]["executionAllowed"])

    def test_preregistration_rejects_non_package_bound_commit_identifier(self) -> None:
        current = self.workbench()
        self.save(self.side(current, "USD"), reviewed_rows(self.side(current, "USD")["rows"]))
        current = self.workbench()
        self.save(self.side(current, "JPY"), reviewed_rows(self.side(current, "JPY")["rows"]))
        ready = build_xe3_preregistration_status(PROJECT_ROOT, storage_root=self.storage_root)
        with self.assertRaises(Xe3SignAdmissionIntegrityError):
            freeze_xe3_preregistration(
                PROJECT_ROOT,
                {"ledgerHash": ready["ledgerHash"], "sourceCommit": "not-a-commit", "outcomeBlindAttestation": True},
                storage_root=self.storage_root,
            )

    def test_frozen_xe2_transforms_remain_outcome_blocked(self) -> None:
        comparison = build_xe3_transform_comparison(PROJECT_ROOT, storage_root=self.storage_root)
        self.assertEqual(len(comparison["comparisons"]), 5)
        self.assertTrue(all(item["outcomeEvaluationStatus"] == "BLOCKED" for item in comparison["comparisons"]))
        self.assertTrue(all(item["signedStateVector"]["state"] == "NO_PROJECTABLE_REAL_SIGNED_EVIDENCE" for item in comparison["comparisons"]))
        self.assertFalse(comparison["guardrails"]["priceOutcomeRead"])
        self.assertFalse(comparison["guardrails"]["fieldsRead"])
        self.assertFalse(comparison["guardrails"]["sbcRead"])

    def test_preregistration_contract_freezes_existing_xe2_parameters_without_outcomes(self) -> None:
        contract = json.loads(PREREGISTRATION_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["contract"], "XE3_PREREGISTERED_CAUSAL_MODIFIER_TRIAL_V1")
        self.assertEqual(contract["initialStatus"], "NOT_FROZEN")
        self.assertFalse(contract["initialFreezeReady"])
        self.assertEqual(contract["frozenXe2Profile"]["m1"], {"beta": 0.8, "mMin": 0.5, "mMax": 1.5})
        self.assertEqual(contract["frozenXe2Profile"]["m3"], {"gamma": 0.5})
        self.assertEqual(contract["projection"]["NEUTRAL"], 0.0)
        self.assertIsNone(contract["projection"]["UNKNOWN_MORE_EVIDENCE_REQUIRED"])
        self.assertFalse(contract["guardrails"]["priceOutcomeRead"])
        self.assertFalse(contract["guardrails"]["executionAllowed"])


if __name__ == "__main__":
    unittest.main()
