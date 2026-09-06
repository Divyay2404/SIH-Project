"""Tests for curriculum ingestion across PDF and PowerPoint inputs."""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.ingestion.document_parser import CurriculumDocumentParser, UnsupportedDocumentError


class TestCurriculumDocumentParser(unittest.TestCase):
    def test_extracts_text_and_table_content_from_pptx_slides(self):
        text_shape = MagicMock(has_text_frame=True, has_table=False, shape_type=1, text="CPU Scheduling")
        table_cell = MagicMock(text="Ready queue")
        table_shape = MagicMock(has_text_frame=False, has_table=True, shape_type=1)
        table_shape.table.rows = [MagicMock(cells=[table_cell])]
        slide = MagicMock(shapes=[text_shape, table_shape])
        presentation = MagicMock(slides=[slide])

        with patch("app.ingestion.document_parser.PPTX_AVAILABLE", True), patch(
            "app.ingestion.document_parser.Presentation", return_value=presentation
        ):
            chunks = CurriculumDocumentParser().parse("operating_systems.pptx")

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["page"], 1)
        self.assertEqual(chunks[0]["block_type"], "slide")
        self.assertIn("CPU Scheduling", chunks[0]["text"])
        self.assertIn("Ready queue", chunks[0]["text"])

    def test_rejects_unknown_file_types_with_a_clear_message(self):
        with self.assertRaises(UnsupportedDocumentError):
            CurriculumDocumentParser().parse("notes.docx")

    def test_extracts_embedded_text_from_legacy_ppt_without_converter(self):
        with tempfile.NamedTemporaryFile(suffix=".ppt", delete=False) as stream:
            stream.write("Legacy PowerPoint Text".encode("utf-16-le"))
            legacy_path = stream.name
        with patch("app.ingestion.document_parser.shutil.which", return_value=None):
            chunks = CurriculumDocumentParser().parse(legacy_path)
        Path(legacy_path).unlink()
        self.assertIn("Legacy PowerPoint Text", chunks[0]["text"])


if __name__ == "__main__":
    unittest.main()
