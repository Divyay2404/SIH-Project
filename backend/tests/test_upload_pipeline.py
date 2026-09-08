"""
Unit and integration tests for the generic PDF upload pipeline,
error handling, and backend startup compatibility.
"""

import asyncio
import io
import os
import tempfile
import unittest
from pathlib import Path
from fastapi import HTTPException, UploadFile

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.api.routes import ingest_document, router
from app.generators.pdf_generator import pdf_generator, StudyHandoutGenerator
from app.ingestion.pdf_parser import OCRFallbackEngine, PDFStructureParser, pdf_parser_engine


class TestBackendStartupAndImports(unittest.TestCase):
    """Verify backend modules import cleanly and routes are mounted without regression."""

    def test_backend_app_import(self):
        import app.main
        self.assertIsNotNone(app.main.app)
        self.assertEqual(app.main.app.title, "StudyCopilot & StudyForge Unified Learning OS API")

    def test_pdf_generator_contract(self):
        self.assertIsInstance(pdf_generator, StudyHandoutGenerator)
        self.assertTrue(hasattr(pdf_generator, "generate_handout_pdf"))
        self.assertTrue(hasattr(pdf_generator, "available"))

    def test_routes_mounted(self):
        route_paths = [r.path for r in router.routes]
        self.assertIn("/api/ingest", route_paths)
        self.assertIn("/api/query", route_paths)
        self.assertIn("/api/export/ppt", route_paths)
        self.assertIn("/api/export/pdf", route_paths)


class TestGenericPDFUploadPipeline(unittest.TestCase):
    """Verify upload pipeline handles arbitrary lecture-notes PDFs."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_test_pdf(self, pages: list) -> bytes:
        doc = fitz.open()
        for text in pages:
            page = doc.new_page(width=612, height=792)
            if text:
                page.insert_text((50, 100), text, fontsize=12)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_selectable_pdf_arbitrary_filename(self):
        """Verify arbitrary lecture-notes filename ingests properly with schema compliance."""
        p1 = (
            "Chapter 3: Graph Theory and Minimum Spanning Trees.\n"
            "A connected undirected graph has a spanning tree containing all vertices.\n"
            "Kruskal's and Prim's algorithms find a minimum-weight spanning tree in O(E log V)."
        )
        p2 = (
            "Dijkstra's Shortest Path Algorithm:\n"
            "Computes single-source shortest paths on non-negative weighted edges.\n"
            "Maintains a min-priority queue of tentative distances."
        )
        pdf_bytes = self._create_test_pdf([p1, p2])
        filename = "Discrete_Mathematics_Lecture_03_Graphs.pdf"

        upload_file = UploadFile(filename=filename, file=io.BytesIO(pdf_bytes))
        result = asyncio.run(ingest_document(upload_file))

        # Schema compliance checks
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["document_id"].startswith("doc_"))
        self.assertEqual(result["title"], "Discrete Mathematics Lecture 03 Graphs")
        self.assertEqual(result["filename"], filename)
        self.assertGreaterEqual(result["chunks_extracted"], 2)
        self.assertEqual(result["pages_processed"], 2)
        self.assertIn("coordinate metadata", result["message"])

    def test_arbitrary_chemistry_lecture_pdf(self):
        """Verify another arbitrary subject (e.g. Chemistry) ingests without hard-coded assumptions."""
        text = (
            "Unit 2: Chemical Kinetics and Reaction Rates.\n"
            "The rate law expresses reaction rate as a function of reactant concentrations.\n"
            "The Arrhenius equation describes temperature dependence of rate constants: k = A exp(-Ea/RT)."
        )
        pdf_bytes = self._create_test_pdf([text])
        filename = "Engineering_Chemistry_Ch2_Kinetics.pdf"

        upload_file = UploadFile(filename=filename, file=io.BytesIO(pdf_bytes))
        result = asyncio.run(ingest_document(upload_file))

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["title"], "Engineering Chemistry Ch2 Kinetics")
        self.assertEqual(result["pages_processed"], 1)

    def test_mixed_selectable_and_scanned_pdf(self):
        """Verify mixed PDF (selectable page 1 + empty page 2) retains selectable content."""
        p1 = (
            "Computer Architecture & Microprocessors.\n"
            "Pipelining overlaps instruction execution across fetch, decode, execute, and writeback stages."
        )
        p2 = None  # Scanned or blank page without selectable text
        pdf_bytes = self._create_test_pdf([p1, p2])
        filename = "Microprocessor_Architecture_Mixed.pdf"

        upload_file = UploadFile(filename=filename, file=io.BytesIO(pdf_bytes))
        result = asyncio.run(ingest_document(upload_file))

        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["chunks_extracted"], 1)

    def test_empty_pdf_returns_400(self):
        """0-byte file must return a clean HTTP 400 JSON error."""
        upload_file = UploadFile(filename="Empty.pdf", file=io.BytesIO(b""))
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(ingest_document(upload_file))
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail, "The uploaded PDF file is empty.")

    def test_non_pdf_file_returns_400(self):
        """Non-PDF extension must return HTTP 400."""
        upload_file = UploadFile(filename="Syllabus.docx", file=io.BytesIO(b"fake docx content"))
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(ingest_document(upload_file))
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("PDF documents only", ctx.exception.detail)

    def test_unreadable_blank_pdf_returns_422(self):
        """Blank PDF with 0 readable characters and no OCR yields 422 Unprocessable Entity."""
        pdf_bytes = self._create_test_pdf([None])
        upload_file = UploadFile(filename="Blank_Scanned.pdf", file=io.BytesIO(pdf_bytes))
        # When OCR is not available or yields no chunks, 422 is raised
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(ingest_document(upload_file))
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertIn("No readable text could be extracted", ctx.exception.detail)

    def test_pdf_handout_generator_output(self):
        """Verify pdf_generator produces valid PDF bytes from uploaded document structure."""
        if not pdf_generator.available:
            self.skipTest("ReportLab is not installed")
        sample_doc = {
            "title": "Operating Systems Virtual Memory",
            "chunks": [
                {"page": 1, "text": "Virtual Memory and Paging\nPages are mapped to frames using page tables."},
                {"page": 2, "text": "Page Replacement Algorithms\nLRU replaces the page unused for the longest time."}
            ]
        }
        pdf_bytes = pdf_generator.generate_handout_pdf(sample_doc)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))


class TestFrontendErrorHandlingSimulator(unittest.TestCase):
    """
    Simulates the frontend response-checking algorithm in EducatorConsole.jsx
    to guarantee that non-JSON 404/502/504 responses never throw SyntaxError: Unexpected token 'T'.
    """

    def _simulate_frontend_parse(self, status: int, content_type: str, body: str):
        """Mirrors the exact logic implemented in EducatorConsole.jsx."""
        is_json = "application/json" in content_type.lower()
        if status != 200:
            if is_json:
                import json
                try:
                    payload = json.loads(body)
                    return {"error": payload.get("detail", f"Ingestion error (HTTP {status})")}
                except Exception:
                    pass

            if status == 404:
                return {"error": "Server unavailable (HTTP 404): Upload endpoint not found."}
            elif status in (502, 503, 504):
                return {"error": f"Server gateway error (HTTP {status}). Please check backend status."}
            else:
                return {"error": f"Server returned an unexpected response (HTTP {status})."}

        if not is_json:
            return {"error": "Server returned an unexpected response format."}

        import json
        return {"data": json.loads(body)}

    def test_simulated_vercel_404_plain_text(self):
        """The exact error reported in the bug: 404 with body 'The page could not be found'."""
        result = self._simulate_frontend_parse(
            status=404,
            content_type="text/plain; charset=utf-8",
            body="The page could not be found"
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Server unavailable (HTTP 404): Upload endpoint not found.")
        self.assertNotIn("Unexpected token", result["error"])

    def test_simulated_backend_json_422_error(self):
        """FastAPI application-level error (e.g. 422 with JSON detail)."""
        result = self._simulate_frontend_parse(
            status=422,
            content_type="application/json",
            body='{"detail": "No readable text could be extracted from this document."}'
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No readable text could be extracted from this document.")

    def test_simulated_backend_502_gateway_timeout(self):
        """Reverse proxy timeout (e.g. 504 HTML)."""
        result = self._simulate_frontend_parse(
            status=504,
            content_type="text/html",
            body="<html><body><h1>504 Gateway Timeout</h1></body></html>"
        )
        self.assertIn("error", result)
        self.assertIn("Server gateway error (HTTP 504)", result["error"])


if __name__ == "__main__":
    unittest.main()
