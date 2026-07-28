from __future__ import annotations

import copy
import unittest

from status.validate_status import (
    EXPECTED_CONTRACTS,
    STATUS_ROOT,
    _load,
    validate_all,
    validate_capabilities,
    validate_cross_document_links,
    validate_release,
    validate_sbc_phase_p0_audit,
)


class StatusValidationTests(unittest.TestCase):
    def test_canonical_documents_validate(self) -> None:
        result = validate_all()
        self.assertTrue(result["valid"])
        self.assertFalse(result["executionAllowed"])
        self.assertEqual(result["documentCount"], 6)
        self.assertEqual(result["auditCount"], 1)

    def test_release_cannot_promote_with_blockers(self) -> None:
        document = _load(STATUS_ROOT / "release_status.json")
        document["promotionAllowed"] = True
        with self.assertRaisesRegex(ValueError, "blockers"):
            validate_release(document)

    def test_capability_cannot_enable_execution(self) -> None:
        document = copy.deepcopy(_load(STATUS_ROOT / "capability_status.json"))
        document["capabilities"][0]["executionAllowed"] = True
        with self.assertRaisesRegex(ValueError, "enables execution"):
            validate_capabilities(document)

    def test_selected_candidate_metadata_must_match_release(self) -> None:
        documents = {
            filename: copy.deepcopy(_load(STATUS_ROOT / filename))
            for filename in EXPECTED_CONTRACTS
        }
        documents["mobile_acceptance_plan.json"]["mobileCandidate"][
            "sourceGitDirty"
        ] = True
        with self.assertRaisesRegex(ValueError, "sourceGitDirty differs"):
            validate_cross_document_links(documents, STATUS_ROOT)

    def test_sbc_phase_p0_audit_cannot_enable_runtime_behavior(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_phase_p0_gap_audit_20260728.json")
        )
        document["guardrails"]["runtimeBehaviorChanged"] = True
        with self.assertRaisesRegex(ValueError, "runtimeBehaviorChanged"):
            validate_sbc_phase_p0_audit(document, STATUS_ROOT.parent)

    def test_sbc_phase_p0_audit_requires_all_residual_corrections(self) -> None:
        document = copy.deepcopy(
            _load(STATUS_ROOT / "audits/sbc_phase_p0_gap_audit_20260728.json")
        )
        document["residualContractCorrections"].pop()
        with self.assertRaisesRegex(ValueError, "P0-R1 through P0-R8"):
            validate_sbc_phase_p0_audit(document, STATUS_ROOT.parent)


if __name__ == "__main__":
    unittest.main()
