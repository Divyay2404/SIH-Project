import io
import unittest
from fastapi.testclient import TestClient

import fitz
from app.main import app
from app.rag.vector_store import vector_store


class TestProductionDeployment(unittest.TestCase):
    """Verifies that FastAPI production deployment requirements are satisfied."""

    def setUp(self):
        self.client = TestClient(app)

    def _create_sample_pdf(self, pages_text: list) -> bytes:
        doc = fitz.open()
        for text in pages_text:
            page = doc.new_page(width=612, height=792)
            page.insert_text((50, 72), text, fontsize=11)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_production_health_endpoint_available(self):
        """Production backend exposes GET /api/health with online status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("version", data)

    def test_root_health_endpoint_available(self):
        """Production backend exposes GET /health with online status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")

    def test_cors_preflight_for_vercel_production_and_preview(self):
        """CORS middleware allows requests from Vercel production and preview domains."""
        origins_to_test = [
            "https://sih-project.vercel.app",
            "https://sih-project-git-feature-preview.vercel.app",
            "http://localhost:5173"
        ]
        for origin in origins_to_test:
            headers = {
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
            res = self.client.options("/api/ingest", headers=headers)
            self.assertIn(res.status_code, [200, 204])
            self.assertEqual(res.headers.get("access-control-allow-origin"), origin)

    def test_production_ingestion_selectable_pdf(self):
        """Production backend exposes POST /api/ingest and parses selectable PDF."""
        pdf_content = self._create_sample_pdf([
            "Cloud Computing Architecture\nVirtualization enables multi-tenancy and elasticity on distributed hardware."
        ])
        files = {"file": ("cloud_computing.pdf", io.BytesIO(pdf_content), "application/pdf")}
        response = self.client.post("/api/ingest", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["status"], "success")
        self.assertTrue(data["indexing_confirmed"])
        self.assertTrue(data["document_id"].startswith("doc_"))
        self.assertGreater(data["chunks_extracted"], 0)
        self.assertEqual(data["pages_processed"], 1)

    def test_production_complete_lifecycle_with_returned_document_id(self):
        """Returned document_id is correctly used by subsequent document operations."""
        pdf_content = self._create_sample_pdf([
            "Compiler Design: Lexical Analysis\nThe lexer scans source code and converts sequences of characters into tokens."
        ])
        files = {"file": ("Compiler_Design_Unit_1.pdf", io.BytesIO(pdf_content), "application/pdf")}
        ingest_res = self.client.post("/api/ingest", files=files)
        self.assertEqual(ingest_res.status_code, 200)
        doc_id = ingest_res.json()["document_id"]

        # 1. Retrieve document metadata via GET /api/document/{id}
        doc_res = self.client.get(f"/api/document/{doc_id}")
        self.assertEqual(doc_res.status_code, 200)
        doc_data = doc_res.json()
        self.assertEqual(doc_data["document_id"], doc_id)
        self.assertTrue(doc_data["indexing_confirmed"])
        self.assertIn("Compiler Design", doc_data["title"])

        # 2. Query document via POST /api/query
        rag_res = self.client.post(
            "/api/query",
            json={
                "question": "What is the primary role of lexical analysis in compiler design?",
                "marks": 5,
                "document_id": doc_id
            }
        )
        self.assertEqual(rag_res.status_code, 200)
        rag_data = rag_res.json()
        self.assertEqual(rag_data["status"], "success")
        self.assertFalse(rag_data["abstain"])
        self.assertIn("lexer", rag_data["answer"].lower())

        # 3. Export PPTX via GET /api/export/ppt
        ppt_res = self.client.get(f"/api/export/ppt?document_id={doc_id}")
        self.assertEqual(ppt_res.status_code, 200)
        self.assertGreater(len(ppt_res.content), 0)

        # 4. Export Handout PDF via GET /api/export/pdf
        pdf_res = self.client.get(f"/api/export/pdf?document_id={doc_id}")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertTrue(pdf_res.content.startswith(b"%PDF-"))

    def test_production_error_handling_non_existent_route(self):
        """Missing or non-existent endpoint returns standard HTTP 404 without crashing."""
        response = self.client.post("/api/non_existent_endpoint_xyz")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
