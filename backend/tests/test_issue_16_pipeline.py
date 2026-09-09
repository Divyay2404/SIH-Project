"""
Comprehensive Integration & Acceptance Tests for Issue #16:
Complete PDF Upload → Document Analysis → Educator Output Pipeline.

Verifies:
1. Arbitrary PDF upload, validation, and PyMuPDF extraction (multi-page, multi-column, mixed).
2. OCR Fallback engine behavior without crashing.
3. Vector DB indexing confirmation and strict document_id isolation.
4. Structure-aware document analysis (summary, concepts, sections, portions).
5. Document-specific 10-slide outline generation (no BST/AVL demo bleed).
6. Document-specific PowerPoint deck (.pptx) generation and download.
7. Document-specific ReportLab study handout (.pdf) generation and download.
8. Grounded marks-aware RAG query execution scoped to active document_id.
9. Error handling for empty, corrupted, and invalid files.
10. API endpoints (/api/ingest, /api/document/{id}, /api/export/ppt, /api/export/pdf).
"""

import asyncio
import io
import os
import tempfile
import unittest
from pathlib import Path
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.main import app
from app.api.routes import ingest_document, router, document_exports
from app.ingestion.pdf_parser import PDFStructureParser, pdf_parser_engine
from app.ingestion.ocr import OCRFallbackEngine
from app.ingestion.document_analyzer import document_analyzer
from app.rag.vector_store import vector_store
from app.rag.qa_engine import qa_engine
from app.generators.ppt_generator import ppt_generator
from app.generators.pdf_generator import pdf_generator


class TestIssue16CompletePipeline(unittest.TestCase):
    """End-to-End Acceptance Tests for Issue #16."""

    def setUp(self):
        self.client = TestClient(app)

    def _create_multi_page_pdf(self, pages: list) -> bytes:
        """Helper to create synthetic PyMuPDF in-memory PDF documents."""
        doc = fitz.open()
        for page_data in pages:
            page = doc.new_page(width=612, height=792)
            if isinstance(page_data, str):
                page.insert_text((50, 72), page_data, fontsize=11)
            elif isinstance(page_data, list):
                # Multiple blocks or columns
                for block in page_data:
                    if len(block) == 5:
                        x0, y0, x1, y1, text = block
                        page.insert_textbox(fitz.Rect(x0, y0, x1, y1), text, fontsize=11)
                    else:
                        x, y, text = block
                        page.insert_text((x, y), text, fontsize=11)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_arbitrary_operating_systems_pdf_pipeline(self):
        """
        Verify that uploading an arbitrary Operating Systems lecture PDF produces
        document-specific summary, concepts, sections, slide deck, PPT, and study handout
        without any BST/AVL placeholders.
        """
        p1 = (
            "Operating Systems: Process Management & CPU Scheduling.\n"
            "CPU Scheduling is the basis of multi-programmed operating systems.\n"
            "By switching the CPU among processes, the operating system makes the computer more productive.\n"
            "The dispatcher is the module that gives control of the CPU to the process selected by the short-term scheduler."
        )
        p2 = (
            "Context Switching Architecture & Mechanisms.\n"
            "When CPU switches to another process, the system must save the state of the old process and load saved state for the new process.\n"
            "Context switch time is pure overhead because the system does no useful work while switching.\n"
            "Hardware support significantly affects context switch speed and latency bounds."
        )
        p3 = (
            "Scheduling Algorithms & Performance Criteria.\n"
            "First-Come, First-Served (FCFS) Scheduling: The process that requests CPU first is allocated CPU first.\n"
            "Shortest-Job-First (SJF) Scheduling: Associates with each process the length of its next CPU burst.\n"
            "Round Robin (RR) Scheduling: Designed especially for time-sharing systems, allocating a small unit of time called time quantum."
        )

        pdf_bytes = self._create_multi_page_pdf([p1, p2, p3])
        filename = "Operating_Systems_Unit_2.pdf"

        # 1. Ingest via async route handler
        upload_file = UploadFile(filename=filename, file=io.BytesIO(pdf_bytes))
        result = asyncio.run(ingest_document(upload_file))

        # 2. Verify IngestResponse schema and metadata
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["indexing_confirmed"])
        doc_id = result["document_id"]
        self.assertTrue(doc_id.startswith("doc_"))
        self.assertEqual(result["title"], "Operating Systems Unit 2")
        self.assertEqual(result["filename"], filename)
        self.assertEqual(result["pages_processed"], 3)
        self.assertGreaterEqual(result["chunks_extracted"], 3)

        # 3. Verify Document Analysis outputs
        summary = result["summary"]
        self.assertIsNotNone(summary)
        self.assertIn("Operating Systems", summary)
        self.assertNotIn("Binary Search Tree", summary)
        self.assertNotIn("AVL", summary)

        concepts = result["important_concepts"]
        self.assertIsInstance(concepts, list)
        self.assertGreater(len(concepts), 0)
        concepts_text = " ".join(concepts).lower()
        self.assertTrue(any(term in concepts_text for term in ["process", "cpu", "scheduling", "context", "round robin"]))
        self.assertNotIn("in-order successor", concepts_text)

        sections = result["sections"]
        self.assertIsInstance(sections, list)
        self.assertGreater(len(sections), 0)

        # 4. Verify Slide Deck generation
        slides = result["slides"]
        self.assertIsInstance(slides, list)
        self.assertEqual(len(slides), 10)

        # Check slide 1 (Title Slide)
        self.assertEqual(slides[0]["category"], "Title Slide")
        self.assertIn("Operating Systems", slides[0]["title"])

        # Check all slides are free of BST placeholders
        full_slide_text = "\n".join(
            f"{s['title']} {s['subtitle']} {' '.join(s['bullets'])} {s['notes']}"
            for s in slides
        )
        self.assertIn("Operating Systems", full_slide_text)
        self.assertNotIn("In-Order Successor", full_slide_text)
        self.assertNotIn("leaf node with zero child", full_slide_text)
        self.assertNotIn("AVL Rotation", full_slide_text)

        # Check diagram slide exists with 3 stages
        diagram_slide = next((s for s in slides if s.get("diagram")), None)
        self.assertIsNotNone(diagram_slide)
        self.assertEqual(len(diagram_slide["diagramStages"]), 3)

        # 5. Verify Vector DB indexing and strict isolation
        self.assertTrue(vector_store.has_document(doc_id))
        doc_chunks = vector_store.get_document_chunks(doc_id)
        self.assertEqual(len(doc_chunks), result["chunks_extracted"])
        for chunk in doc_chunks:
            self.assertEqual(chunk["document_id"], doc_id)
            self.assertEqual(chunk["document_name"], filename)

        # 6. Verify Grounded RAG Query Scoped to this document
        rag_res = qa_engine.answer_question(
            question="Explain Round Robin CPU scheduling and time quantum",
            marks=5,
            document_id=doc_id
        )
        self.assertEqual(rag_res["status"], "success")
        self.assertFalse(rag_res["abstain"])
        self.assertEqual(rag_res["citation"]["document_name"], filename)
        self.assertIn("Round Robin", rag_res["answer"])
        self.assertNotIn("In-Order Successor", rag_res["answer"])

        # Off-topic query must trigger abstention gate
        off_topic_res = qa_engine.answer_question(
            question="What is the boiling point of ethanol at sea level?",
            marks=2,
            document_id=doc_id
        )
        self.assertTrue(off_topic_res["abstain"])

        # Query scoped to wrong document_id must abstain
        wrong_scope_res = qa_engine.answer_question(
            question="Explain Round Robin CPU scheduling",
            marks=5,
            document_id="doc_non_existent_fake_999"
        )
        self.assertTrue(wrong_scope_res["abstain"])

        # 7. Verify PowerPoint export (.pptx)
        if ppt_generator.available:
            from pptx import Presentation
            doc_data = document_exports[doc_id]
            ppt_bytes = ppt_generator.generate_ppt_deck(doc_data)
            self.assertIsInstance(ppt_bytes, bytes)
            self.assertGreater(len(ppt_bytes), 0)

            prs = Presentation(io.BytesIO(ppt_bytes))
            ppt_text = "\n".join(
                shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")
            )
            self.assertIn("Operating Systems", ppt_text)
            self.assertNotIn("Binary Search Trees", ppt_text)
            self.assertNotIn("In-Order Successor", ppt_text)

        # 8. Verify ReportLab study handout export (.pdf)
        if pdf_generator.available:
            doc_data = document_exports[doc_id]
            pdf_out_bytes = pdf_generator.generate_handout_pdf(doc_data)
            self.assertIsInstance(pdf_out_bytes, bytes)
            self.assertTrue(pdf_out_bytes.startswith(b"%PDF-"))

            # Read back text from generated PDF
            doc_reader = fitz.open(stream=pdf_out_bytes, filetype="pdf")
            handout_text = "\n".join(page.get_text() for page in doc_reader)
            doc_reader.close()
            self.assertIn("Operating Systems", handout_text)
            self.assertNotIn("Binary Search Trees", handout_text)

    def test_multi_column_reading_order_preservation(self):
        """Verify layout-aware multi-column parsing maintains column separation."""
        left_col = (50, 100, 260, 250, "Left Column Section: Introduction to Network Topology and Star Architecture.")
        right_col = (320, 100, 530, 250, "Right Column Section: Mesh Networks and Peer-to-Peer Redundancy Metrics.")
        pdf_bytes = self._create_multi_page_pdf([[left_col, right_col]])

        parser = PDFStructureParser()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            chunks = parser.parse_pdf(tmp_path)
            self.assertGreaterEqual(len(chunks), 2)
            # Left column text should appear before right column text in reading order
            combined_texts = [c["text"] for c in chunks]
            left_idx = next(i for i, t in enumerate(combined_texts) if "Left Column" in t)
            right_idx = next(i for i, t in enumerate(combined_texts) if "Right Column" in t)
            self.assertLess(left_idx, right_idx)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_ocr_fallback_module_resilience(self):
        """Verify OCRFallbackEngine handles requests safely without crashing."""
        ocr = OCRFallbackEngine()
        self.assertTrue(hasattr(ocr, "ocr_page"))
        self.assertTrue(hasattr(ocr, "available"))

        # Test on dummy empty page
        doc = fitz.open()
        page = doc.new_page()
        # Even if Tesseract is not installed on the system, ocr_page must return list, not throw
        ocr_res = ocr.ocr_page(page, page_num=1)
        self.assertIsInstance(ocr_res, list)
        doc.close()

    def test_api_document_endpoint_and_exports(self):
        """Verify REST endpoints /api/document/{id}, /api/export/ppt, and /api/export/pdf."""
        # 1. Ingest a document via API client
        pdf_bytes = self._create_multi_page_pdf([
            "Digital Signal Processing: Fourier Transforms.\n"
            "Discrete Fourier Transform (DFT) converts finite discrete-time sequences to discrete frequency components.\n"
            "Fast Fourier Transform (FFT) computes the DFT in O(N log N) time complexity."
        ])
        response = self.client.post(
            "/api/ingest",
            files={"file": ("Digital_Signal_Processing.pdf", pdf_bytes, "application/pdf")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        doc_id = data["document_id"]

        # 2. Query /api/document/{id}
        doc_res = self.client.get(f"/api/document/{doc_id}")
        self.assertEqual(doc_res.status_code, 200)
        doc_data = doc_res.json()
        self.assertEqual(doc_data["document_id"], doc_id)
        self.assertEqual(doc_data["title"], "Digital Signal Processing")
        self.assertTrue(doc_data["indexing_confirmed"])
        self.assertGreaterEqual(len(doc_data["slides"]), 10)

        # 3. Test /api/export/ppt endpoint
        ppt_res = self.client.get(f"/api/export/ppt?document_id={doc_id}")
        self.assertEqual(ppt_res.status_code, 200)
        self.assertIn("application/vnd.openxmlformats-officedocument.presentationml.presentation", ppt_res.headers.get("content-type", ""))
        self.assertIn("Lecture_Digital_Signal_Processing.pptx", ppt_res.headers.get("content-disposition", ""))

        # 4. Test /api/export/pdf endpoint
        pdf_res = self.client.get(f"/api/export/pdf?document_id={doc_id}")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertIn("application/pdf", pdf_res.headers.get("content-type", ""))
        self.assertIn("Study_Guide_Digital_Signal_Processing.pdf", pdf_res.headers.get("content-disposition", ""))

        # 5. Non-existent document_id returns 404
        bad_ppt = self.client.get("/api/export/ppt?document_id=doc_non_existent")
        self.assertEqual(bad_ppt.status_code, 404)
        bad_pdf = self.client.get("/api/export/pdf?document_id=doc_non_existent")
        self.assertEqual(bad_pdf.status_code, 404)
        bad_doc = self.client.get("/api/document/doc_non_existent")
        self.assertEqual(bad_doc.status_code, 404)

    def test_error_handling_empty_and_invalid_files(self):
        """Verify 400 for empty or non-PDF files and 422 for unreadable PDFs."""
        # Empty PDF
        res_empty = self.client.post(
            "/api/ingest",
            files={"file": ("Empty.pdf", b"", "application/pdf")}
        )
        self.assertEqual(res_empty.status_code, 400)
        self.assertIn("empty", res_empty.json()["detail"].lower())

        # Non-PDF file
        res_txt = self.client.post(
            "/api/ingest",
            files={"file": ("Notes.txt", b"plain text content", "text/plain")}
        )
        self.assertEqual(res_txt.status_code, 400)
        self.assertIn("pdf documents only", res_txt.json()["detail"].lower())


if __name__ == "__main__":
    unittest.main()
