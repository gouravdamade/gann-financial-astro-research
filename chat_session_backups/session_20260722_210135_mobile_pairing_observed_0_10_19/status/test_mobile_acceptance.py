from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from status.mobile_acceptance import (
    load_plan,
    load_result,
    new_result,
    record_test,
    save_result,
)


class MobileAcceptanceTests(unittest.TestCase):
    def test_pass_requires_hash_addressed_evidence(self) -> None:
        plan = load_plan()
        result = new_result(plan)
        with self.assertRaisesRegex(ValueError, "requires at least one evidence"):
            record_test(
                result,
                plan,
                test_id="MOB-01",
                status="passed",
                observer="tester",
                evidence_paths=[],
                notes="",
            )

    def test_result_is_bound_to_exact_plan_and_evidence_hash(self) -> None:
        plan = load_plan()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence.txt"
            evidence.write_text("physical evidence", encoding="utf-8")
            result = record_test(
                new_result(plan),
                plan,
                test_id="MOB-01",
                status="passed",
                observer="tester",
                evidence_paths=[evidence],
                notes="installed",
            )
            result_path = root / "result.json"
            save_result(result_path, result)
            loaded = load_result(result_path, plan)
        self.assertEqual(loaded["tests"]["MOB-01"]["status"], "passed")
        self.assertEqual(len(loaded["tests"]["MOB-01"]["evidence"][0]["sha256"]), 64)
        self.assertFalse(loaded["promotionAllowed"])


if __name__ == "__main__":
    unittest.main()
