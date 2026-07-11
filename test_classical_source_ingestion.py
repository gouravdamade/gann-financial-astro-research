import tempfile
import unittest
from pathlib import Path

from jyotish_agent.ingest_classical_sources import render_source, section_for, topics_for


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<DjVuXML><BODY>
  <OBJECT><HIDDENTEXT><PAGECOLUMN><REGION><PARAGRAPH><LINE>
    <WORD>Chapter</WORD><WORD>One</WORD><WORD>Dasa</WORD>
  </LINE></PARAGRAPH></REGION></PAGECOLUMN></HIDDENTEXT></OBJECT>
  <OBJECT><HIDDENTEXT><PAGECOLUMN><REGION><PARAGRAPH><LINE>
    <WORD>Appendix</WORD><WORD>longitude</WORD>
  </LINE></PARAGRAPH></REGION></PAGECOLUMN></HIDDENTEXT></OBJECT>
</BODY></DjVuXML>
"""


class ClassicalSourceIngestionTests(unittest.TestCase):
    def test_section_and_topic_classification(self) -> None:
        ranges = [{"start": 1, "end": 1, "type": "root"}, {"start": 2, "end": 2, "type": "appendix"}]
        self.assertEqual(section_for(2, ranges), "appendix")
        self.assertEqual(topics_for("A Dasa result", {"dasha": ["dasa"], "wealth": ["wealth"]}), ["dasha"])

    def test_render_source_preserves_pdf_page_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            xml_path = root / "source.xml"
            output_path = root / "source.txt"
            xml_path.write_text(SAMPLE_XML, encoding="utf-8")
            config = {
                "title": "Test Source",
                "author": "Test Author",
                "translator": "Test Translator",
                "edition": "Test Edition",
                "authority": "root_translation_with_notes",
                "ocr_xml_path": str(xml_path),
                "output_path": str(output_path),
                "expected_pages": 2,
                "section_ranges": [
                    {"start": 1, "end": 1, "type": "root"},
                    {"start": 2, "end": 2, "type": "appendix"},
                ],
                "topics": {"dasha": ["dasa"], "longitude": ["longitude"]},
            }

            result = render_source("TEST_SOURCE", config, minimum_chars=1)
            text = output_path.read_text(encoding="utf-8")

            self.assertEqual(result["retained_pages"], 2)
            self.assertIn("[[PDF_PAGE: 0001]]", text)
            self.assertIn("[[PDF_PAGE: 0002]]", text)
            self.assertIn("[[CONTENT_LAYER: appendix]]", text)
            self.assertIn("[[TRANSLATOR: Test Translator]]", text)
            self.assertIn("[[TOPICS: dasha]]", text)


if __name__ == "__main__":
    unittest.main()
