from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SOURCES_PATH = ROOT / "configs" / "sbc" / "sources.yaml"
MAP_PATH = ROOT / "configs" / "sbc" / "agarwal_2000_composite_page_map.yaml"
READINESS_PATH = ROOT / "configs" / "sbc" / "agarwal_2000_a1_readiness.yaml"


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
            "superseded_acquisition_request_page_level_transcription_still_gated",
        )
        self.assertIn("AGARWAL_MYSTICS_INCOMPLETE_SCAN_20260722", source_ids)
        self.assertIn("AGARWAL_MYSTICS_SAGAR_FIRST_EDITION_2000_HARDCOPY", source_ids)

    def test_composite_map_covers_every_page_without_derivative_fallback(self) -> None:
        source_map = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8"))
        covered: list[int] = []
        blocked_ranges: set[str] = set()
        for item in source_map["page_ranges"]:
            start, end = _page_span(item["printed_page_range"])
            covered.extend(range(start, end + 1))
            self.assertNotIn("CHISTABO", item["controlling_source_id"])
            if item["transcription_status"] == "BLOCKED_PRIVATE_CAPTURE_NOT_MATERIALIZED":
                blocked_ranges.add(item["printed_page_range"])

        self.assertEqual(covered, list(range(1, 195)))
        self.assertEqual(blocked_ranges, {"46-47", "54-55", "62-63", "133", "144", "145-146"})

    def test_readiness_fails_closed_without_private_capture_bytes(self) -> None:
        readiness = yaml.safe_load(READINESS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(readiness["private_capture_gate"], "BLOCKED_PRIVATE_CAPTURE_FILES_NOT_FOUND")
        self.assertFalse(readiness["readiness"]["AGARWAL_GEOMETRY_READY"]["value"])
        self.assertFalse(readiness["readiness"]["AGARWAL_STRENGTH_READY"]["value"])
        self.assertFalse(readiness["readiness"]["AGARWAL_VEDHA_OPERATOR_READY"]["value"])
        self.assertFalse(readiness["readiness"]["AGARWAL_A2_READY"]["value"])
        self.assertEqual(
            readiness["contracts"]["AGARWAL_SBC_2000_SOURCE_V1"]["status"],
            "NOT_CREATED_SOURCE_EXTRACTION_BLOCKED",
        )


if __name__ == "__main__":
    unittest.main()
