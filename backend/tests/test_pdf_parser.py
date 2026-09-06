"""
Unit Tests for PDFStructureParser & OCR Fallback Engine.
Tests cover:
1. Normal selectable PDF (uses PyMuPDF, OCR not invoked).
2. Scanned/image-only PDF (triggers localized OCR).
3. Mixed PDF (page-level selective OCR).
4. Bounding box coordinates format and validation.
5. Page number preservation across normal and OCR pages.
6. Table/grid and multi-column layout resilience.
7. OCR failure error-isolation and graceful continuation.
8. Safe execution when Tesseract/tessdata is missing.
"""

import math
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

try:
    import pymupdf as fitz  # type: ignore[import-not-found, import-untyped]
except ImportError:
    import fitz  # type: ignore[import-not-found, import-untyped]
from app.ingestion.pdf_parser import OCRFallbackEngine, PDFStructureParser


class TestPDFParserAndOCRFallback(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_sample_pdf(self, pages_content: list) -> str:
        """
        Helper to create temporary PDF files.
        pages_content is a list of strings (or None for blank/scanned pages).
        """
        doc = fitz.open()
        for text in pages_content:
            page = doc.new_page(width=612, height=792)  # Standard Letter
            if text:
                page.insert_text((50, 100), text, fontsize=12)
        pdf_path = os.path.join(self.temp_dir.name, "test_doc.pdf")
        doc.save(pdf_path)
        doc.close()
        return pdf_path

    def test_selectable_pdf_normal_extraction(self):
        """Test that selectable PDFs extract normally and do NOT trigger OCR."""
        sample_text_1 = (
            "Chapter 1: Binary Search Trees.\n"
            "A Binary Search Tree is an essential data structure used in computer science.\n"
            "Every left descendant has a smaller key and every right descendant has a larger key."
        )
        sample_text_2 = (
            "Time Complexity Analysis of Search, Insertion, and Deletion in a BST.\n"
            "In a balanced tree, operations take O(log N) time. In a skewed tree, operations take O(N)."
        )
        pdf_path = self._create_sample_pdf([sample_text_1, sample_text_2])

        mock_ocr = MagicMock(spec=OCRFallbackEngine)
        parser = PDFStructureParser(ocr_engine=mock_ocr)

        chunks = parser.parse_pdf(pdf_path)

        # Assert chunks extracted for both pages
        self.assertGreaterEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertEqual(chunk["block_type"], "text")
            self.assertIn(chunk["page"], [1, 2])
            self.assertEqual(len(chunk["bbox"]), 4)

        # Ensure OCR was NOT invoked because pages had sufficient selectable text
        mock_ocr.ocr_page.assert_not_called()

    def test_scanned_pdf_triggers_ocr(self):
        """Test that scanned/image-only PDF (no selectable text) triggers localized OCR."""
        # 1 page with no selectable text
        pdf_path = self._create_sample_pdf([None])

        mock_ocr = MagicMock(spec=OCRFallbackEngine)
        mock_ocr.ocr_page.return_value = [
            {
                "page": 1,
                "text": "Binary search is an efficient searching algorithm with O(log n) complexity.",
                "bbox": [72.0, 110.0, 520.0, 185.0],
                "block_type": "ocr"
            }
        ]

        parser = PDFStructureParser(ocr_engine=mock_ocr)
        chunks = parser.parse_pdf(pdf_path)

        # OCR should have been invoked for page 1
        mock_ocr.ocr_page.assert_called_once()
        call_args, call_kwargs = mock_ocr.ocr_page.call_args
        self.assertEqual(call_kwargs.get("page_num"), 1)

        # Verify extracted OCR chunk
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["block_type"], "ocr")
        self.assertEqual(chunks[0]["page"], 1)
        self.assertIn("Binary search", chunks[0]["text"])
        self.assertEqual(chunks[0]["bbox"], [72.0, 110.0, 520.0, 185.0])

    def test_mixed_pdf_extraction(self):
        """
        Test mixed PDF:
        - Page 1: Selectable text (normal extraction)
        - Page 2: Scanned image (OCR fallback)
        - Page 3: Selectable text (normal extraction)
        """
        p1_text = (
            "Introduction to Operating Systems and Process Scheduling.\n"
            "Operating systems manage hardware resources and coordinate application execution."
        )
        p2_text = None  # Scanned page (missing text layer)
        p3_text = (
            "Memory Management and Virtual Memory Paging.\n"
            "Paging allows physical address space of a process to be non-contiguous."
        )
        pdf_path = self._create_sample_pdf([p1_text, p2_text, p3_text])

        mock_ocr = MagicMock(spec=OCRFallbackEngine)
        mock_ocr.ocr_page.return_value = [
            {
                "page": 2,
                "text": "Scanned Diagram: CPU Scheduler Queue and Context Switching mechanism.",
                "bbox": [50.0, 120.0, 550.0, 300.0],
                "block_type": "ocr"
            }
        ]

        parser = PDFStructureParser(ocr_engine=mock_ocr)
        chunks = parser.parse_pdf(pdf_path)

        # OCR should ONLY have been called once for page 2
        mock_ocr.ocr_page.assert_called_once()
        self.assertEqual(mock_ocr.ocr_page.call_args[1]["page_num"], 2)

        # Page 1: normal text
        p1_chunks = [c for c in chunks if c["page"] == 1]
        self.assertTrue(all(c["block_type"] == "text" for c in p1_chunks))

        # Page 2: OCR text
        p2_chunks = [c for c in chunks if c["page"] == 2]
        self.assertEqual(len(p2_chunks), 1)
        self.assertEqual(p2_chunks[0]["block_type"], "ocr")
        self.assertIn("Scanned Diagram", p2_chunks[0]["text"])

        # Page 3: normal text
        p3_chunks = [c for c in chunks if c["page"] == 3]
        self.assertTrue(all(c["block_type"] == "text" for c in p3_chunks))

    def test_ocr_bounding_box_format(self):
        """Test OCR bounding box coordinates are numeric, rounded, and conform to [x0, y0, x1, y1]."""
        mock_page = MagicMock()
        mock_textpage = MagicMock()
        mock_page.get_textpage_ocr.return_value = mock_textpage
        mock_page.get_text.return_value = [
            (54.2345, 120.8976, 500.1234, 180.4567, "First OCR block text\n", 0, 0),
            (60.1, 200.2, 450.3, 280.4, "Second OCR block text\n", 1, 0),
        ]

        engine = OCRFallbackEngine()
        ocr_blocks = engine.ocr_page(mock_page, page_num=4)

        self.assertEqual(len(ocr_blocks), 2)
        for block in ocr_blocks:
            self.assertEqual(block["page"], 4)
            self.assertEqual(block["block_type"], "ocr")
            bbox = block["bbox"]
            self.assertEqual(len(bbox), 4)
            # Ensure all coordinates are floats rounded to 2 decimal places
            self.assertTrue(all(isinstance(c, float) for c in bbox))
            x0, y0, x1, y1 = bbox
            self.assertLess(x0, x1)
            self.assertLess(y0, y1)

        self.assertEqual(ocr_blocks[0]["bbox"], [54.23, 120.9, 500.12, 180.46])

    def test_page_numbers_preserved(self):
        """Test that 1-indexed page numbers are preserved across normal and OCR blocks."""
        pdf_path = self._create_sample_pdf([
            "Selectable Page One content with enough words to satisfy threshold.",
            None,  # Scanned Page Two
            None,  # Scanned Page Three
            "Selectable Page Four content with enough words to satisfy threshold."
        ])

        def mock_ocr_side_effect(page, page_num):
            return [{
                "page": page_num,
                "text": f"OCR Content for Page {page_num}",
                "bbox": [10.0, 20.0, 100.0, 200.0],
                "block_type": "ocr"
            }]

        mock_ocr = MagicMock(spec=OCRFallbackEngine)
        mock_ocr.ocr_page.side_effect = mock_ocr_side_effect

        parser = PDFStructureParser(ocr_engine=mock_ocr)
        chunks = parser.parse_pdf(pdf_path)

        pages_found = sorted(list(set(c["page"] for c in chunks)))
        self.assertEqual(pages_found, [1, 2, 3, 4])

    def test_table_grid_page_handling(self):
        """Test OCR block parsing handles table grids, multi-column blocks, and irregular coordinates safely."""
        mock_page = MagicMock()
        mock_textpage = MagicMock()
        mock_page.get_textpage_ocr.return_value = mock_textpage

        # Simulate table cells and multi-column grid with irregular and edge-case blocks
        mock_page.get_text.return_value = [
            (50.0, 100.0, 150.0, 120.0, "Header Col 1\n", 0, 0),
            (160.0, 100.0, 260.0, 120.0, "Header Col 2\n", 1, 0),
            (270.0, 100.0, 370.0, 120.0, "Header Col 3\n", 2, 0),
            # Multi-line cell text
            (50.0, 130.0, 150.0, 160.0, "Data Row 1\nValue A\n", 3, 0),
            # Empty / whitespace block
            (160.0, 130.0, 260.0, 160.0, "   \n\t  ", 4, 0),
            # Irregular / invalid NaN coordinate that shouldn't crash parser
            (float("nan"), 130.0, 370.0, 160.0, "Invalid NaN Block\n", 5, 0),
            # Valid cell
            (270.0, 130.0, 370.0, 160.0, "Valid Cell Value\n", 6, 0),
        ]

        engine = OCRFallbackEngine()
        ocr_blocks = engine.ocr_page(mock_page, page_num=7)

        # Should parse safely without throwing any exceptions
        self.assertIsInstance(ocr_blocks, list)
        self.assertEqual(len(ocr_blocks), 5)  # 3 headers + 1 multi-line cell + 1 valid cell
        texts = [b["text"] for b in ocr_blocks]
        self.assertIn("Header Col 1", texts)
        self.assertIn("Data Row 1\nValue A", texts)
        self.assertIn("Valid Cell Value", texts)

    def test_ocr_failure_resilience(self):
        """Test that an unhandled OCR error on one page does not crash processing for remaining pages."""
        pdf_path = self._create_sample_pdf([
            None,  # Page 1: Scanned, OCR succeeds
            None,  # Page 2: Scanned, OCR fails with RuntimeError
            None,  # Page 3: Scanned, OCR succeeds
        ])

        def mock_ocr_side_effect(page, page_num):
            if page_num == 2:
                raise RuntimeError("OCR engine crashed: Out of memory or corrupted tessdata")
            return [{
                "page": page_num,
                "text": f"Successfully recognized OCR content on page {page_num}",
                "bbox": [50.0, 50.0, 400.0, 150.0],
                "block_type": "ocr"
            }]

        mock_ocr = MagicMock(spec=OCRFallbackEngine)
        mock_ocr.ocr_page.side_effect = mock_ocr_side_effect

        parser = PDFStructureParser(ocr_engine=mock_ocr)
        # Should not raise exception
        chunks = parser.parse_pdf(pdf_path)

        # Pages 1 and 3 should be successfully extracted
        pages_processed = [c["page"] for c in chunks]
        self.assertIn(1, pages_processed)
        self.assertNotIn(2, pages_processed)
        self.assertIn(3, pages_processed)

    def test_ocr_fallback_engine_missing_tesseract_graceful(self):
        """Test OCRFallbackEngine safely handles missing Tesseract without unhandled exception."""
        mock_page = MagicMock()
        mock_page.get_textpage_ocr.side_effect = RuntimeError("No tessdata specified and Tesseract is not installed")

        engine = OCRFallbackEngine()
        result = engine.ocr_page(mock_page, page_num=1)

        # Must return empty list safely without crashing
        self.assertEqual(result, [])

    def test_text_sufficiency_detection(self):
        """Test selectable-text sufficiency detection heuristics."""
        parser = PDFStructureParser(min_char_threshold=50, min_word_threshold=8)

        # Empty / whitespace text
        self.assertFalse(parser.is_page_text_sufficient(""))
        self.assertFalse(parser.is_page_text_sufficient("   \n\t  "))

        # Too short (scanned watermark / single digit page number)
        self.assertFalse(parser.is_page_text_sufficient("Page 1"))
        self.assertFalse(parser.is_page_text_sufficient("Scan001 2026-09-05"))

        # Sufficient paragraph
        good_text = (
            "A Binary Search Tree is a hierarchical data structure with ordered nodes "
            "where each node contains a key and optional associated value."
        )
        self.assertTrue(parser.is_page_text_sufficient(good_text))


if __name__ == "__main__":
    unittest.main()
