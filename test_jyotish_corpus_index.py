import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from jyotish_agent.build_corpus_index import (
    build_index,
    chunk_text,
    retrieve,
    rule_notes_text,
    touch_log_text,
)


class CorpusChunkingTests(unittest.TestCase):
    def test_page_markers_are_repeated_when_a_page_needs_multiple_chunks(self) -> None:
        marker = "\n".join(
            [
                "[[SOURCE: TEST_BOOK]]",
                "[[PDF_PAGE: 0042]]",
                "[[PRINT_PAGE: 0031]]",
                "[[CHAPTER: timing]]",
            ]
        )
        chunks = chunk_text(f"{marker}\n{'word ' * 180}", "TEST_BOOK", "Test Book", max_chars=400)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all("[[PDF_PAGE: 0042]]" in chunk["text"] for chunk in chunks))
        self.assertTrue(all(chunk["source_id"] == "TEST_BOOK" for chunk in chunks))

    def test_page_marked_paragraph_does_not_merge_with_neighboring_text(self) -> None:
        text = "ordinary introduction\n\n[[SOURCE: TEST_BOOK]]\n[[PDF_PAGE: 0001]]\npage body"
        chunks = chunk_text(text, "TEST_BOOK", "Test Book", max_chars=2200)

        self.assertEqual(len(chunks), 2)
        self.assertNotIn("[[PDF_PAGE:", chunks[0]["text"])
        self.assertIn("[[PDF_PAGE: 0001]]", chunks[1]["text"])

    def test_retrieve_can_reserve_slots_by_source_group(self) -> None:
        chunks = [
            {"source_id": "CURRENT_RULE_NOTES", "title": "Notes", "chunk_id": "notes-1", "text": "planet strength"},
            {"source_id": "BRIHAT_JATAKA", "title": "Classic", "chunk_id": "classic-1", "text": "planet strength"},
        ]
        with TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.joblib"
            build_index(chunks, index_path)

            evidence = retrieve("planet strength", index_path, source_ids={"CURRENT_RULE_NOTES"})
            doctrine = retrieve("planet strength", index_path, exclude_source_ids={"CURRENT_RULE_NOTES"})

        self.assertEqual([item["source_id"] for item in evidence], ["CURRENT_RULE_NOTES"])
        self.assertEqual([item["source_id"] for item in doctrine], ["BRIHAT_JATAKA"])

    def test_rule_notes_quarantine_legacy_astronomy_contracts(self) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "notes.sqlite"
            with closing(sqlite3.connect(db_path)) as conn:
                conn.executescript(
                    """
                    CREATE TABLE aspect_cases (
                        case_id INTEGER PRIMARY KEY, pair_key TEXT, aspect TEXT, context_json TEXT
                    );
                    CREATE TABLE rule_notes (
                        note_id INTEGER PRIMARY KEY, case_id INTEGER, note_type TEXT,
                        note_text TEXT, created_at_utc TEXT
                    );
                    """
                )
                conn.execute(
                    "INSERT INTO aspect_cases VALUES (1, 'AVG(ALL)|MOON', 'square', '{}')"
                )
                conn.execute(
                    "INSERT INTO aspect_cases VALUES (2, 'MOON|SUN', 'trine', ?)",
                    ('{"astronomy_contract_version":"RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_V1"}',),
                )
                conn.execute("INSERT INTO rule_notes VALUES (1, 1, 'official_ml_note', 'legacy claim', '2026')")
                conn.execute("INSERT INTO rule_notes VALUES (2, 2, 'official_ml_note', 'supported claim', '2026')")
                conn.commit()

            text = rule_notes_text(db_path)

        self.assertNotIn("legacy claim", text)
        self.assertIn("supported claim", text)
        self.assertIn("Quarantined legacy/unversioned notes: 1", text)

    def test_touch_log_quarantines_unversioned_representative_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "touch.csv"
            pd.DataFrame([{"event_id": "legacy", "pair_key": "AVG(ALL)|MOON"}]).to_csv(path, index=False)

            text = touch_log_text(path)

        self.assertIn("legacy touch log has no astronomy contract version", text)
        self.assertNotIn("legacy AVG(ALL)|MOON", text)


if __name__ == "__main__":
    unittest.main()
