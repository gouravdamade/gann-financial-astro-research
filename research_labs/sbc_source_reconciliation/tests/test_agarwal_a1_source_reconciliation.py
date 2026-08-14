from __future__ import annotations

import unittest
from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[3]
SOURCES_PATH = ROOT / "configs" / "sbc" / "sources.yaml"
MAP_PATH = ROOT / "configs" / "sbc" / "agarwal_2000_composite_page_map.yaml"
READINESS_PATH = ROOT / "configs" / "sbc" / "agarwal_2000_a1_readiness.yaml"
STRENGTH_PATH = ROOT / "configs" / "sbc" / "evidence_packets" / "agarwal_2000_strength_two_pass_v1.yaml"
GEOMETRY_PATH = ROOT / "configs" / "sbc" / "evidence_packets" / "agarwal_2000_geometry_and_operator_partial_v1.yaml"
FINANCIAL_PATH = ROOT / "configs" / "sbc" / "evidence_packets" / "agarwal_financial_sbc_v1_hypothesis_ledger.yaml"


def _page_span(value: str) -> tuple[int, int]:
    if "-" in value:
        start, end = value.split("-", 1)
        return int(start), int(end)
    page = int(value)
    return page, page


class AgarwalA1SourceReconciliationTests(unittest.TestCase):
    def test_current_source_register_preserves_history_and_records_hardcopy(self) -> None:
        source_ids = {
            item["source_id"]: item
            for item in yaml.safe_load(SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
        }

        self.assertIn("AGARWAL_2000_SBC_PENDING", source_ids)
        self.assertEqual(
            source_ids["AGARWAL_2000_SBC_PENDING"]["status"],
            "superseded_acquisition_request_page_level_extraction_partially_completed",
        )
        self.assertIn("AGARWAL_MYSTICS_INCOMPLETE_SCAN_20260722", source_ids)
        self.assertIn("AGARWAL_MYSTICS_SAGAR_FIRST_EDITION_2000_HARDCOPY", source_ids)

    def test_composite_map_covers_every_page_without_derivative_fallback(self) -> None:
        source_map = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8"))
        covered: list[int] = []
        for item in source_map["page_ranges"]:
            start, end = _page_span(item["printed_page_range"])
            covered.extend(range(start, end + 1))
            self.assertNotIn("CHISTABO", item["controlling_source_id"])

        self.assertEqual(covered, list(range(1, 195)))
        self.assertEqual(source_map["private_capture_materialization_state"], "ALL_6_CAPTURE_FILES_HASH_VERIFIED_20260814")

    def test_readiness_keeps_operator_and_a2_fail_closed(self) -> None:
        readiness = yaml.safe_load(READINESS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(readiness["private_capture_gate"], "ALL_6_CAPTURE_FILES_HASH_VERIFIED_20260814")
        self.assertFalse(readiness["readiness"]["AGARWAL_GEOMETRY_READY"]["value"])
        self.assertTrue(readiness["readiness"]["AGARWAL_STRENGTH_READY"]["value"])
        self.assertFalse(readiness["readiness"]["AGARWAL_VEDHA_OPERATOR_READY"]["value"])
        self.assertFalse(readiness["readiness"]["AGARWAL_A2_READY"]["value"])
        self.assertEqual(
            readiness["contracts"]["AGARWAL_SBC_2000_SOURCE_V1"]["status"],
            "NOT_CREATED_MINIMUM_OPERATOR_DEPENDENCIES_NOT_CLOSED",
        )
        self.assertEqual(readiness["contracts"]["A2_SCOPE_FULL_VEDHA_INSPECTOR"]["status"], "NOT_AUTHORIZED")
        self.assertEqual(readiness["contracts"]["A2_SCOPE_GEOMETRY_STRENGTH_INSPECTOR"]["status"], "NOT_AUTHORIZED")

    def test_admitted_numeric_entries_have_two_pass_evidence(self) -> None:
        packet = yaml.safe_load(STRENGTH_PATH.read_text(encoding="utf-8"))
        self.assertTrue(packet["entries"])
        for entry in packet["entries"]:
            self.assertTrue(entry["transcription_pass_A"])
            self.assertTrue(entry["transcription_pass_B"])
            self.assertEqual(entry["diff_status"], "AGREED")
            self.assertIn(entry["source_status"], {"SOURCE_CLOSED", "PARTIAL"})

    def test_geometry_preserves_unknown_fold_and_operator_is_not_executable(self) -> None:
        packet = yaml.safe_load(GEOMETRY_PATH.read_text(encoding="utf-8"))
        self.assertIn("UNKNOWN_CENTER_FOLD", str(packet["author_figure"]["unresolved_properties"]))
        self.assertEqual(
            packet["author_figure"]["a1r2_capture_search"]["result"],
            "NO_NEW_AUTHENTICATED_FLAT_OR_CENTRE_FOLD_CAPTURE_FOUND",
        )
        self.assertEqual(packet["author_figure"]["admitted_machine_cell_mapping"]["count"], 0)
        self.assertEqual(packet["author_figure"]["admitted_machine_cell_mapping"]["status"], "NOT_CREATED")
        self.assertEqual(packet["contract_status"]["AGARWAL_SBC_2000_SOURCE_V1"], "NOT_CREATED_MINIMUM_OPERATOR_DEPENDENCIES_NOT_CLOSED")

    def test_p144_allocations_are_preserved_without_inferred_cell_reconstruction(self) -> None:
        packet = yaml.safe_load(GEOMETRY_PATH.read_text(encoding="utf-8"))
        allocations = packet["geometry"]["source_closed_allocations"]
        self.assertEqual(packet["geometry"]["diff_status"], "AGREED")
        self.assertEqual(allocations["stars"], ["2-8", "10-16", "18-24", "26-32"])
        self.assertEqual(allocations["signs"], ["58-60", "62-64", "66-68", "70-72"])
        self.assertEqual(packet["author_figure"]["admitted_machine_cell_mapping"]["count"], 0)

    def test_operator_matrix_closes_source_facts_but_fails_closed_for_execution(self) -> None:
        packet = yaml.safe_load(GEOMETRY_PATH.read_text(encoding="utf-8"))
        matrix = packet["vedha_dependency_matrix"]
        self.assertEqual(matrix["subject_reference_inputs"]["status"], "SOURCE_CLOSED_FACT_LIST_ONLY")
        self.assertEqual(matrix["transiting_object_input"]["status"], "SOURCE_CLOSED_FACT_LIST_ONLY")
        self.assertEqual(matrix["direction_ray"]["status"], "SOURCE_CLOSED_STAR_TABLE_ONLY")
        self.assertEqual(matrix["motion_class"]["status"], "PARTIAL")
        self.assertEqual(matrix["target_cell_resolution"]["status"], "PARTIAL")
        self.assertEqual(matrix["worked_example_reproducibility"]["status"], "NOT_REPRODUCIBLE")
        self.assertEqual(packet["contract_status"]["AGARWAL_SBC_2000_SOURCE_V1"], "NOT_CREATED_MINIMUM_OPERATOR_DEPENDENCIES_NOT_CLOSED")

    def test_private_source_bytes_are_not_git_tracked(self) -> None:
        tracked = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files"], text=True, encoding="utf-8"
        ).splitlines()
        self.assertFalse(any(path.lower().startswith("sources/private/") for path in tracked))

    def test_financial_ledger_is_hypothesis_only_and_locked(self) -> None:
        ledger = yaml.safe_load(FINANCIAL_PATH.read_text(encoding="utf-8"))
        self.assertEqual(ledger["classification"], "FINANCIAL_HYPOTHESIS")
        self.assertIn("execution", ledger["prohibited_uses"])
        self.assertIn("Fields_polarity", ledger["prohibited_uses"])
        self.assertTrue(all(item["source_status"] == "FINANCIAL_HYPOTHESIS" for item in ledger["claims"]))


if __name__ == "__main__":
    unittest.main()
