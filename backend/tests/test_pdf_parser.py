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


class TestPyMuPDFLayoutCoordinateExtractor(unittest.TestCase):
    """
    Exhaustive tests for Issue #3: PyMuPDF Layout Coordinate & Bounding Box Extractor.
    Validates:
    1. Single-column PDF.
    2. Two-column PDF reading order (no column interleaving).
    3. Section heading preservation and is_heading inference.
    4. Multiple paragraphs and exact character offset mapping.
    5. Bounding-box normalization [x0, y0, x1, y1] clamped to [0, 1].
    6. Empty/textless page handling.
    7. Multi-page document structure.
    8. Unusual whitespace and hyphenation cleanup.
    9. JSON-serializable public API output.
    10. parse_pdf backward compatibility with legacy callers.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.parser = PDFStructureParser(enable_ocr=False)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _save_pdf(self, doc, filename="test.pdf") -> str:
        pdf_path = os.path.join(self.temp_dir.name, filename)
        doc.save(pdf_path)
        doc.close()
        return pdf_path

    def test_single_column_pdf(self):
        """Test single-column PDF extracts clean structured chunks in reading order."""
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((50, 80), "Introduction to Data Structures", fontsize=16)
        page.insert_text((50, 130), "Paragraph 1: Linear data structures include arrays and linked lists.", fontsize=11)
        page.insert_text((50, 180), "Paragraph 2: Non-linear data structures include trees and graphs.", fontsize=11)
        pdf_path = self._save_pdf(doc, "single_col.pdf")

        result = self.parser.parse_document(pdf_path)

        self.assertEqual(result["page_count"], 1)
        self.assertEqual(len(result["pages"]), 1)
        page_data = result["pages"][0]
        self.assertEqual(page_data["page_index"], 0)
        self.assertGreaterEqual(len(page_data["chunks"]), 3)

        # Verify reading order
        texts = [c["text"] for c in page_data["chunks"]]
        self.assertIn("Introduction to Data Structures", texts[0])
        self.assertIn("Paragraph 1", texts[1])
        self.assertIn("Paragraph 2", texts[2])

    def test_two_column_pdf_reading_order(self):
        """
        Test two-column PDF processes column 1 top-to-bottom, THEN column 2 top-to-bottom.
        Verifies that vertical y-coordinate interleaving does NOT corrupt column reading order.
        """
        doc = fitz.open()
        page = doc.new_page(width=600, height=800)

        # Full-width paper title
        page.insert_text((50, 50), "Two-Column Academic Paper Title", fontsize=18)

        # Column 1 (left column)
        page.insert_text((50, 120), "Col1-P1: Left column initial hypothesis and problem definition.", fontsize=10)
        page.insert_text((50, 220), "Col1-P2: Left column detailed methodology and experiments.", fontsize=10)

        # Column 2 (right column) - y coordinates interleave with Column 1
        page.insert_text((320, 130), "Col2-P1: Right column related works and comparative baseline.", fontsize=10)
        page.insert_text((320, 230), "Col2-P2: Right column conclusion and evaluation metrics.", fontsize=10)

        pdf_path = self._save_pdf(doc, "two_col.pdf")
        result = self.parser.parse_document(pdf_path)

        chunks = result["pages"][0]["chunks"]
        texts = [c["text"] for c in chunks]

        # Verify title is first
        self.assertIn("Two-Column Academic Paper Title", texts[0])

        # Find indices of column paragraphs
        idx_c1_p1 = next(i for i, t in enumerate(texts) if "Col1-P1" in t)
        idx_c1_p2 = next(i for i, t in enumerate(texts) if "Col1-P2" in t)
        idx_c2_p1 = next(i for i, t in enumerate(texts) if "Col2-P1" in t)
        idx_c2_p2 = next(i for i, t in enumerate(texts) if "Col2-P2" in t)

        # Crucial test: Column 1 paragraphs MUST both precede Column 2 paragraphs
        self.assertLess(idx_c1_p1, idx_c1_p2, "Col1-P1 must precede Col1-P2")
        self.assertLess(idx_c1_p2, idx_c2_p1, "Col1-P2 must precede Col2-P1 (No column interleaving!)")
        self.assertLess(idx_c2_p1, idx_c2_p2, "Col2-P1 must precede Col2-P2")

    def test_section_heading_detection(self):
        """Test headings are detected via font size/weight and marked with is_heading=True."""
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)

        # Large heading
        page.insert_text((50, 80), "Chapter 4: Binary Search Trees", fontsize=18)
        # Normal body
        page.insert_text((50, 130), "A BST satisfies the strict invariant that left keys are smaller than root.", fontsize=11)
        # Section heading
        page.insert_text((50, 180), "Section 4.2: Insertion Mechanics", fontsize=15)
        # Normal body
        page.insert_text((50, 220), "Insertion traverses recursively until reaching a leaf null position.", fontsize=11)

        pdf_path = self._save_pdf(doc, "headings.pdf")
        result = self.parser.parse_document(pdf_path)

        chunks = result["pages"][0]["chunks"]
        heading_chunks = [c for c in chunks if c["is_heading"]]
        body_chunks = [c for c in chunks if not c["is_heading"]]

        self.assertGreaterEqual(len(heading_chunks), 2)
        heading_texts = [c["text"] for c in heading_chunks]
        self.assertTrue(any("Chapter 4" in t for t in heading_texts))
        self.assertTrue(any("Section 4.2" in t for t in heading_texts))

        # Ensure body paragraphs are not marked as headings
        body_texts = [c["text"] for c in body_chunks]
        self.assertTrue(any("BST satisfies" in t for t in body_texts))
        self.assertTrue(any("Insertion traverses" in t for t in body_texts))

    def test_multiple_paragraphs_and_character_offsets(self):
        """
        Test that character offsets are deterministic:
        page_text[chunk['char_start']:chunk['char_end']] == chunk['text']
        for every single chunk returned.
        """
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((50, 70), "Title of the Article", fontsize=16)
        page.insert_text((50, 110), "First paragraph discusses basic principles and foundation.", fontsize=11)
        page.insert_text((50, 150), "Second paragraph elaborates on algorithm runtime characteristics.", fontsize=11)
        page.insert_text((50, 190), "Third paragraph summarizes findings and provides benchmark analysis.", fontsize=11)

        pdf_path = self._save_pdf(doc, "offsets.pdf")
        result = self.parser.parse_document(pdf_path)

        page_data = result["pages"][0]
        page_text = page_data["text"]

        for idx, chunk in enumerate(page_data["chunks"]):
            c_start = chunk["char_start"]
            c_end = chunk["char_end"]
            c_text = chunk["text"]

            # Exact slice match verification
            extracted_slice = page_text[c_start:c_end]
            self.assertEqual(
                extracted_slice,
                c_text,
                f"Chunk {idx} offset slice '{extracted_slice}' does not match chunk text '{c_text}'"
            )

    def test_bounding_box_normalization(self):
        """
        Test bounding box normalization constraints:
        0 <= x0 <= x1 <= 1
        0 <= y0 <= y1 <= 1
        Coordinates must be floats rounded consistently.
        """
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((100, 150), "Test normalized coordinates across page bounds.", fontsize=12)
        pdf_path = self._save_pdf(doc, "bbox.pdf")

        result = self.parser.parse_document(pdf_path)
        chunks = result["pages"][0]["chunks"]

        self.assertGreaterEqual(len(chunks), 1)
        for chunk in chunks:
            bbox = chunk["bbox"]
            self.assertEqual(len(bbox), 4)
            x0, y0, x1, y1 = bbox

            # Check bounding box normalization constraints
            self.assertGreaterEqual(x0, 0.0)
            self.assertLessEqual(x0, 1.0)
            self.assertGreaterEqual(y0, 0.0)
            self.assertLessEqual(y0, 1.0)
            self.assertGreaterEqual(x1, 0.0)
            self.assertLessEqual(x1, 1.0)
            self.assertGreaterEqual(y1, 0.0)
            self.assertLessEqual(y1, 1.0)

            # Ordering constraints
            self.assertLessEqual(x0, x1)
            self.assertLessEqual(y0, y1)

            # Native bbox should also be preserved
            self.assertIn("native_bbox", chunk)
            self.assertEqual(len(chunk["native_bbox"]), 4)

    def test_empty_and_textless_page_handling(self):
        """Test empty or image-only pages are handled safely without exceptions."""
        doc = fitz.open()
        # Page 0 has content
        p1 = doc.new_page(width=612, height=792)
        p1.insert_text((50, 100), "Selectable text on first page.", fontsize=12)
        # Page 1 is completely empty
        doc.new_page(width=612, height=792)
        # Page 2 has only spaces
        p3 = doc.new_page(width=612, height=792)
        p3.insert_text((50, 100), "     \n\t  ", fontsize=12)

        pdf_path = self._save_pdf(doc, "empty_pages.pdf")
        result = self.parser.parse_document(pdf_path)

        self.assertEqual(result["page_count"], 3)
        self.assertEqual(len(result["pages"]), 3)
        self.assertGreaterEqual(len(result["pages"][0]["chunks"]), 1)
        # Empty pages must produce empty chunks list without crashing
        self.assertEqual(len(result["pages"][1]["chunks"]), 0)
        self.assertEqual(result["pages"][1]["text"], "")

    def test_multiple_pages(self):
        """Test multi-page document structure, page_count, and page_index sequencing."""
        doc = fitz.open()
        for i in range(4):
            p = doc.new_page(width=612, height=792)
            p.insert_text((50, 100), f"Content on Page {i + 1} of four.", fontsize=12)

        pdf_path = self._save_pdf(doc, "multi_page.pdf")
        result = self.parser.parse_document(pdf_path)

        self.assertEqual(result["page_count"], 4)
        self.assertEqual(len(result["pages"]), 4)
        for i, page_data in enumerate(result["pages"]):
            self.assertEqual(page_data["page_index"], i)
            self.assertIn(f"Page {i + 1}", page_data["text"])

    def test_unusual_whitespace_and_hyphenation_cleanup(self):
        """Test cleanup of non-breaking spaces, excess tabs, and split hyphenated words."""
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        # Text with hyphenated line break and non-breaking spaces
        dirty_text = "The quick brown fox jumps over the algo-\nrithm with \u00a0 non-breaking spaces."
        page.insert_text((50, 100), dirty_text, fontsize=12)

        pdf_path = self._save_pdf(doc, "cleanup.pdf")
        result = self.parser.parse_document(pdf_path)

        page_data = result["pages"][0]
        chunks = page_data["chunks"]
        self.assertGreaterEqual(len(chunks), 1)

        combined_text = " ".join(c["text"] for c in chunks)
        # Hyphenated break "algo-\nrithm" should be joined to "algorithm"
        self.assertIn("algorithm", combined_text)
        # Non-breaking space should be normalized
        self.assertNotIn("\u00a0", combined_text)

        # Character offsets must still hold exactly for the cleaned text
        for chunk in chunks:
            self.assertEqual(
                page_data["text"][chunk["char_start"]:chunk["char_end"]],
                chunk["text"]
            )

    def test_json_compatible_output(self):
        """Test public parser output is 100% JSON-serializable."""
        import json

        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((50, 100), "JSON Compatibility Test Heading", fontsize=16)
        page.insert_text((50, 140), "Standard body paragraph for serialization testing.", fontsize=11)

        pdf_path = self._save_pdf(doc, "json_test.pdf")
        result = self.parser.parse_document(pdf_path)

        # Must serialize cleanly without TypeError
        serialized = json.dumps(result, indent=2)
        self.assertIsInstance(serialized, str)

        parsed_back = json.loads(serialized)
        self.assertEqual(parsed_back["page_count"], 1)
        self.assertIn("pages", parsed_back)
        self.assertIn("chunks", parsed_back["pages"][0])
        first_chunk = parsed_back["pages"][0]["chunks"][0]
        self.assertIn("text", first_chunk)
        self.assertIn("char_start", first_chunk)
        self.assertIn("char_end", first_chunk)
        self.assertIn("bbox", first_chunk)
        self.assertIn("is_heading", first_chunk)

    def test_parse_pdf_backward_compatibility(self):
        """
        Test parse_pdf returns flattened chunks for legacy callers,
        while supporting as_document=True for structured callers.
        """
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((50, 100), "Legacy Backward Compatibility Test", fontsize=14)

        pdf_path = self._save_pdf(doc, "compat.pdf")

        # 1. Legacy call: returns list of dicts
        legacy_chunks = self.parser.parse_pdf(pdf_path)
        self.assertIsInstance(legacy_chunks, list)
        self.assertGreaterEqual(len(legacy_chunks), 1)
        self.assertEqual(legacy_chunks[0]["page"], 1)
        self.assertIn("bbox", legacy_chunks[0])
        self.assertIn("char_start", legacy_chunks[0])
        self.assertIn("char_end", legacy_chunks[0])
        self.assertIn("is_heading", legacy_chunks[0])

        # 2. Structured call: returns dict with page_count and pages
        doc_result = self.parser.parse_pdf(pdf_path, as_document=True)
        self.assertIsInstance(doc_result, dict)
        self.assertEqual(doc_result["page_count"], 1)
        self.assertIn("pages", doc_result)


if __name__ == "__main__":
    unittest.main()

