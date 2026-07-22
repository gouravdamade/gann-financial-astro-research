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
)


class StatusValidationTests(unittest.TestCase):
    def test_canonical_documents_validate(self) -> None:
        result = validate_all()
        self.assertTrue(result["valid"])
        self.assertFalse(result["executionAllowed"])
        self.assertEqual(result["documentCount"], 5)

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


if __name__ == "__main__":
    unittest.main()
