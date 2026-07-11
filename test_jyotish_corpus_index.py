import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jyotish_agent.build_corpus_index import build_index, chunk_text, retrieve


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


if __name__ == "__main__":
    unittest.main()
