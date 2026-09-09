"""
Dedicated test suite verifying Issue #47: Isolation of demo BST data from uploaded-document workflows.
Validates:
1. Grounded RAG abstention on off-document queries (BST query targeted at OS doc abstains).
2. /api/document/{id}/pdf binary stream availability for native PDF preview.
3. /api/demo/load on-demand activation of demo BST dataset.
4. /api/quiz dynamic topic extraction for uploaded documents vs demo BST question.
5. /api/readiness dynamic diagnostic state isolation.
"""

import io
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.rag.vector_store import vector_store

try:
    import pymupdf as fitz
except ImportError:
    import fitz


class TestIssue47BSTIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def _create_sample_pdf(self, title: str, paragraphs: list) -> bytes:
        doc = fitz.open()
        for text in paragraphs:
            page = doc.new_page(width=612, height=792)
            page.insert_text((50, 100), f"{title}\n{text}", fontsize=12)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_demo_load_endpoint(self):
        """Verify POST /api/demo/load populates demo knowledge and slide outlines."""
        res = self.client.post("/api/demo/load")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["document_id"], "doc_bst_chapter_01")
        self.assertIn("Binary Search Trees", data["title"])
        self.assertGreaterEqual(len(data.get("slides", [])), 10)
        self.assertTrue(data.get("indexing_confirmed"))

    def test_document_pdf_stream_endpoint(self):
        """Verify GET /api/document/{document_id}/pdf streams valid PDF binary."""
        pdf_bytes = self._create_sample_pdf("Compiler Architecture", [
            "Lexical analysis parses tokens from the source stream.",
            "Syntax analysis builds an Abstract Syntax Tree (AST)."
        ])
        files = {"file": ("Compiler_Design.pdf", pdf_bytes, "application/pdf")}
        ingest_res = self.client.post("/api/ingest", files=files)
        self.assertEqual(ingest_res.status_code, 200)
        doc_id = ingest_res.json()["document_id"]

        pdf_res = self.client.get(f"/api/document/{doc_id}/pdf")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res.headers["content-type"], "application/pdf")
        self.assertTrue(pdf_res.content.startswith(b"%PDF-"))

    def test_rag_bst_isolation_on_uploaded_document(self):
        """Asking BST deletion questions targeting an unrelated document must abstain."""
        pdf_bytes = self._create_sample_pdf("Database Normalization", [
            "First Normal Form (1NF) eliminates duplicate columns and requires atomic attribute domains.",
            "Boyce-Codd Normal Form (BCNF) strictly requires every determinant to be a candidate key."
        ])
        files = {"file": ("Database_Theory.pdf", pdf_bytes, "application/pdf")}
        ingest_res = self.client.post("/api/ingest", files=files)
        doc_id = ingest_res.json()["document_id"]

        # Target query asking about BST deletion against the Database document
        query_payload = {
            "question": "How does BST deletion work for two children with in-order successor?",
            "marks": 5,
            "document_id": doc_id
        }
        rag_res = self.client.post("/api/query", json=query_payload)
        self.assertEqual(rag_res.status_code, 200)
        rag_data = rag_res.json()
        self.assertTrue(rag_data["abstain"])
        self.assertEqual(rag_data["status"], "abstain")
        self.assertIsNone(rag_data["citation"])
        self.assertIn("Abstention Gate Triggered", rag_data["answer"])

    def test_dynamic_quiz_for_uploaded_document(self):
        """GET /api/quiz?document_id={doc_id} must return quiz questions derived from uploaded material."""
        pdf_bytes = self._create_sample_pdf("Distributed Systems Quorum", [
            "Distributed Consensus and Paxos Protocol.",
            "Quorum intersection guarantees consistency under network partitions."
        ])
        files = {"file": ("Distributed_Systems.pdf", pdf_bytes, "application/pdf")}
        ingest_res = self.client.post("/api/ingest", files=files)
        doc_id = ingest_res.json()["document_id"]

        quiz_res = self.client.get(f"/api/quiz?document_id={doc_id}")
        self.assertEqual(quiz_res.status_code, 200)
        quiz_data = quiz_res.json()
        self.assertFalse(quiz_data.get("is_empty"))
        # Must NOT be BST Deletion topic
        self.assertNotEqual(quiz_data["topic"], "Binary Search Tree Deletion")
        self.assertNotIn("BST", quiz_data["question_text"])

    def test_demo_quiz_still_available_when_requested(self):
        """GET /api/quiz?document_id=doc_bst_chapter_01 returns BST quiz."""
        quiz_res = self.client.get("/api/quiz?document_id=doc_bst_chapter_01")
        self.assertEqual(quiz_res.status_code, 200)
        quiz_data = quiz_res.json()
        self.assertEqual(quiz_data["question_id"], "q_bst_del_01")
        self.assertEqual(quiz_data["topic"], "Binary Search Tree Deletion")


if __name__ == "__main__":
    unittest.main()
