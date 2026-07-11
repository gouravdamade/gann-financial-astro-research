import unittest

from jyotish_agent.build_corpus_index import chunk_text


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


if __name__ == "__main__":
    unittest.main()
