"""Regression tests that prevent educator exports from reverting to BST placeholders."""

import io
import unittest

from app.generators.pdf_generator import pdf_generator
from app.generators.ppt_generator import ppt_generator


DOCUMENT = {
    "title": "Operating Systems Scheduling",
    "chunks": [
        {"page": 1, "text": "Process Scheduling\nThe scheduler selects a ready process for CPU execution."},
        {"page": 2, "text": "Context Switching\nThe operating system saves one process state before restoring another."},
    ],
}


class TestDynamicEducatorExports(unittest.TestCase):
    def test_presentation_uses_uploaded_document_content(self):
        if not ppt_generator.available:
            self.skipTest("python-pptx is not installed")
        from pptx import Presentation

        presentation = Presentation(io.BytesIO(ppt_generator.generate_ppt_deck(DOCUMENT)))
        text = "\n".join(shape.text for slide in presentation.slides for shape in slide.shapes if hasattr(shape, "text"))
        self.assertIn("Operating Systems Scheduling", text)
        self.assertIn("Process Scheduling", text)
        self.assertNotIn("Binary Search Trees", text)

    def test_handout_uses_uploaded_document_content(self):
        if not pdf_generator.available:
            self.skipTest("ReportLab is not installed")
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_generator.generate_handout_pdf(DOCUMENT)))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(stream=pdf_generator.generate_handout_pdf(DOCUMENT), filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()

        self.assertIn("Operating Systems Scheduling", text)
        self.assertIn("Context Switching", text)
        self.assertNotIn("Binary Search Trees", text)

    def test_handout_large_multipage_document_no_table_overflow(self):
        """Verifies that large documents with 60+ chunks split across pages cleanly without table overflow."""
        if not pdf_generator.available:
            self.skipTest("ReportLab is not installed")

        large_doc = {
            "title": "Advanced Distributed Systems",
            "summary": "Comprehensive overview of consensus algorithms, Byzantine fault tolerance, and Raft replication.",
            "chunks": [
                {
                    "page": (i // 4) + 1,
                    "text": f"Section {i + 1}: Detailed technical specification covering state machine replication, consensus bounds, network partitions, and quorum mechanics in distributed cluster {i + 1}."
                }
                for i in range(60)
            ],
            "important_concepts": ["Paxos", "Raft", "Byzantine Fault Tolerance", "Quorum", "Split-Brain"],
        }

        pdf_bytes = pdf_generator.generate_handout_pdf(large_doc)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

        import fitz
        reader = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreater(len(reader), 1)
        full_text = "\n".join(p.get_text() for p in reader)
        reader.close()

        self.assertIn("Advanced Distributed Systems", full_text)
        self.assertIn("Section 60", full_text)
        self.assertIn("Paxos", full_text)


if __name__ == "__main__":
    unittest.main()
