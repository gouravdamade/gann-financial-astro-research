from __future__ import annotations

import unittest
from pathlib import Path
import subprocess
import hashlib

import yaml


ROOT = Path(__file__).resolve().parents[3]
SOURCES_PATH = ROOT / "configs" / "sbc" / "sources.yaml"
MAP_PATH = ROOT / "configs" / "sbc" / "agarwal_2000_composite_page_map.yaml"
READINESS_PATH = ROOT / "configs" / "sbc" / "agarwal_2000_a1_readiness.yaml"
STRENGTH_PATH = ROOT / "configs" / "sbc" / "evidence_packets" / "agarwal_2000_strength_two_pass_v1.yaml"
GEOMETRY_PATH = ROOT / "configs" / "sbc" / "evidence_packets" / "agarwal_2000_geometry_and_operator_partial_v1.yaml"
PAGE145_GEOMETRY_PATH = ROOT / "configs" / "sbc" / "evidence_packets" / "agarwal_2000_page145_geometry_two_pass_v1.yaml"
FINANCIAL_PATH = ROOT / "configs" / "sbc" / "evidence_packets" / "agarwal_financial_sbc_v1_hypothesis_ledger.yaml"
PRIVATE_PAGE145_DIR = Path("D:/GannFinancialAstro/sources/private/agarwal_hardcopy_20260813/page145_photographs_20260815")


def _flatten_rows(rows: list[list[dict]]) -> list[dict]:
    return [cell for row in rows for cell in row]


def _expand_ranges(values: list[str | int]) -> set[int]:
    result: set[int] = set()
    for value in values:
        if isinstance(value, int):
            result.add(value)
            continue
        start, separator, end = value.partition("-")
        if separator:
            result.update(range(int(start), int(end) + 1))
        else:
            result.add(int(start))
    return result


def _core_geometry_is_ready(packet: dict) -> bool:
    pass_a = packet["transcription"]["pass_A"]["core_rows"]
    pass_b = packet["transcription"]["pass_B"]["core_rows"]
    statuses = _flatten_rows(packet["mechanical_diff"]["coordinate_status_rows"])
    return (
        len(pass_a) == len(pass_b) == 9
        and all(len(row) == 9 for row in pass_a + pass_b)
        and _flatten_rows(pass_a) == _flatten_rows(pass_b)
        and len(statuses) == 81
        and all(status == "AGREED" for status in statuses)
    )


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

    def test_readiness_authorizes_only_bounded_geometry_strength_scope(self) -> None:
        readiness = yaml.safe_load(READINESS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(readiness["private_capture_gate"], "ALL_6_CAPTURE_FILES_HASH_VERIFIED_20260814")
        self.assertEqual(readiness["milestone"], "PFR-V2B-R6-SBC-A2R1")
        self.assertTrue(readiness["readiness"]["AGARWAL_GEOMETRY_READY"]["value"])
        self.assertTrue(readiness["readiness"]["AGARWAL_STRENGTH_READY"]["value"])
        self.assertFalse(readiness["readiness"]["AGARWAL_VEDHA_OPERATOR_READY"]["value"])
        self.assertTrue(readiness["readiness"]["AGARWAL_A2_READY"]["value"])
        self.assertEqual(
            readiness["contracts"]["AGARWAL_SBC_2000_SOURCE_V1"]["status"],
            "NOT_CREATED_MINIMUM_OPERATOR_DEPENDENCIES_NOT_CLOSED",
        )
        self.assertEqual(readiness["contracts"]["A2_SCOPE_FULL_VEDHA_INSPECTOR"]["status"], "NOT_AUTHORIZED")
        self.assertEqual(
            readiness["contracts"]["A2_SCOPE_GEOMETRY_STRENGTH_INSPECTOR"]["status"],
            "FOUNDER_ACCEPTED",
        )

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
        self.assertEqual(packet["author_figure"]["a1r3_supersession"]["status"], "SUPERSEDED_BY_CLEAR_PAGE145_PHOTOGRAPHS")
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

    def test_page145_photographs_are_private_and_checksum_verified(self) -> None:
        packet = yaml.safe_load(PAGE145_GEOMETRY_PATH.read_text(encoding="utf-8"))
        expected = {
            item["filename"]: item["sha256"]
            for item in packet["page_evidence"]["photographs"]
        }
        self.assertEqual(len(expected), 4)
        self.assertEqual(expected["1000413731.jpg"], "CF0F72F82558B9C634B13EC9936BD2322900BCC9636945C1B0CB144310A3FA3F")
        self.assertEqual(expected["1000413730.jpg"], "BE4F77485AE29A7184D2629C4ADC6B26C31F47FFD4854DF02E4BA23DD86ECC3F")
        for filename, expected_sha in expected.items():
            artifact = PRIVATE_PAGE145_DIR / filename
            self.assertTrue(artifact.is_file())
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest().upper(), expected_sha)
        tracked = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files"], text=True, encoding="utf-8"
        ).splitlines()
        self.assertFalse(any(filename in path for filename in expected for path in tracked))

    def test_page145_passes_are_distinct_complete_and_two_pass_agreed(self) -> None:
        packet = yaml.safe_load(PAGE145_GEOMETRY_PATH.read_text(encoding="utf-8"))
        pass_a = packet["transcription"]["pass_A"]
        pass_b = packet["transcription"]["pass_B"]
        self.assertEqual(pass_a["witness"], "1000413731.jpg")
        self.assertEqual(pass_b["witness"], "1000413730.jpg")
        self.assertNotEqual(pass_a["witness"], pass_b["witness"])
        self.assertEqual(len(_flatten_rows(pass_a["core_rows"])), 81)
        self.assertEqual(len(_flatten_rows(pass_b["core_rows"])), 81)
        self.assertTrue(_core_geometry_is_ready(packet))
        self.assertEqual(packet["final_machine_cell_map"]["coordinate_count"], 81)
        self.assertEqual(packet["final_machine_cell_map"]["admission_status"], "SOURCE_CLOSED_TWO_PASS_AGREED")

    def test_page145_orientation_and_machine_layers_are_source_closed(self) -> None:
        packet = yaml.safe_load(PAGE145_GEOMETRY_PATH.read_text(encoding="utf-8"))
        orientation = packet["page_evidence"]["author_orientation"]
        self.assertEqual(orientation, {"east": "top", "west": "bottom", "north": "left", "south": "right"})
        cells = _flatten_rows(packet["transcription"]["pass_A"]["core_rows"])
        self.assertEqual({cell["varga_number"] for cell in cells}, set(range(1, 82)))
        self.assertEqual({cell["layer"] for cell in cells}, {"star", "sign", "vowel", "consonant", "weekday_tithi_group"})
        self.assertEqual(next(cell for cell in cells if cell["varga_number"] == 23)["literal"], "ABHIJIT")

    def test_page145_p144_reconciliation_is_mechanical_and_exact(self) -> None:
        packet = yaml.safe_load(PAGE145_GEOMETRY_PATH.read_text(encoding="utf-8"))
        cells = _flatten_rows(packet["transcription"]["pass_A"]["core_rows"])
        expected = packet["p144_reconciliation"]["expected"]
        by_layer = {
            "stars": {cell["varga_number"] for cell in cells if cell["layer"] == "star"},
            "signs": {cell["varga_number"] for cell in cells if cell["layer"] == "sign"},
            "vowels": {cell["varga_number"] for cell in cells if cell["layer"] == "vowel"},
            "consonants": {cell["varga_number"] for cell in cells if cell["layer"] == "consonant"},
            "lunar_tithis": {cell["varga_number"] for cell in cells if cell["layer"] == "weekday_tithi_group"},
            "weekdays": {cell["varga_number"] for cell in cells if cell["layer"] == "weekday_tithi_group"},
        }
        for layer, actual in by_layer.items():
            self.assertEqual(actual, _expand_ranges(expected[layer]))
        self.assertEqual(packet["p144_reconciliation"]["status"], "MATCH")

    def test_page145_artificial_unresolved_coordinate_fails_geometry_readiness(self) -> None:
        packet = yaml.safe_load(PAGE145_GEOMETRY_PATH.read_text(encoding="utf-8"))
        packet["mechanical_diff"]["coordinate_status_rows"][4][4] = "UNREADABLE_BOTH"
        self.assertFalse(_core_geometry_is_ready(packet))

    def test_page145_geometry_closure_does_not_create_a_vedha_operator(self) -> None:
        packet = yaml.safe_load(PAGE145_GEOMETRY_PATH.read_text(encoding="utf-8"))
        readiness = yaml.safe_load(READINESS_PATH.read_text(encoding="utf-8"))
        self.assertTrue(packet["readiness_result"]["AGARWAL_GEOMETRY_READY"])
        self.assertFalse(readiness["readiness"]["AGARWAL_VEDHA_OPERATOR_READY"]["value"])
        self.assertEqual(readiness["contracts"]["AGARWAL_SBC_2000_SOURCE_V1"]["status"], "NOT_CREATED_MINIMUM_OPERATOR_DEPENDENCIES_NOT_CLOSED")
        self.assertIn("polarity", packet["prohibited_uses"])
        self.assertIn("execution", packet["prohibited_uses"])


if __name__ == "__main__":
    unittest.main()
