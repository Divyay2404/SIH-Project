"""
Comprehensive test suite for Student Portal arbitrary PDF upload,
strict document-scoped RAG retrieval, marks-aware scaling, and cross-document isolation.
"""

import asyncio
import io
import unittest
from fastapi import UploadFile, HTTPException

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.api.routes import ingest_document, process_rag_query, list_documents, get_document
from app.schemas.api_schemas import RAGQueryRequest
from app.rag.vector_store import vector_store
from app.rag.qa_engine import qa_engine


class TestStudentAnyPdfRAG(unittest.TestCase):
    """Verifies complete upload -> active document -> document-scoped RAG -> citation workflow."""

    def _create_pdf_bytes(self, pages: list) -> bytes:
        doc = fitz.open()
        for text in pages:
            page = doc.new_page(width=612, height=792)
            if text:
                page.insert_text((50, 100), text, fontsize=12)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_complete_two_pdf_upload_and_scoped_rag_workflow(self):
        # 1. Prepare PDF A: Operating Systems Virtual Memory
        doc_a_text_p1 = (
            "Chapter 9: Virtual Memory and Paging Architecture.\n"
            "Virtual memory decouples the logical address space from physical memory.\n"
            "Demand paging brings pages into physical memory only when accessed by the CPU."
        )
        doc_a_text_p2 = (
            "Page Replacement Algorithms:\n"
            "LRU (Least Recently Used) replaces the page that has not been used for the longest period of time.\n"
            "FIFO replaces the oldest page in memory, but can suffer from Belady's Anomaly."
        )
        pdf_a_bytes = self._create_pdf_bytes([doc_a_text_p1, doc_a_text_p2])
        filename_a = "OS_Virtual_Memory.pdf"

        upload_a = UploadFile(filename=filename_a, file=io.BytesIO(pdf_a_bytes))
        result_a = asyncio.run(ingest_document(upload_a))

        self.assertEqual(result_a["status"], "success")
        self.assertTrue(result_a["indexing_confirmed"])
        doc_id_a = result_a["document_id"]
        self.assertTrue(doc_id_a.startswith("doc_"))
        self.assertIn("pages", result_a)
        self.assertEqual(len(result_a["pages"]), 2)

        # 2. Prepare PDF B: Engineering Thermodynamics
        doc_b_text_p1 = (
            "Module 4: Second Law of Thermodynamics and Heat Engines.\n"
            "A heat engine converts thermal energy into mechanical work operating between high and low reservoirs.\n"
            "The Carnot engine provides the theoretical upper limit on efficiency: eta = 1 - (TL / TH)."
        )
        doc_b_text_p2 = (
            "Entropy and Reversibility:\n"
            "Clausius statement: heat cannot spontaneously flow from colder to hotter body without external work.\n"
            "For all irreversible processes, total entropy of an isolated system always increases: dS >= 0."
        )
        pdf_b_bytes = self._create_pdf_bytes([doc_b_text_p1, doc_b_text_p2])
        filename_b = "Engineering_Thermodynamics.pdf"

        upload_b = UploadFile(filename=filename_b, file=io.BytesIO(pdf_b_bytes))
        result_b = asyncio.run(ingest_document(upload_b))

        self.assertEqual(result_b["status"], "success")
        self.assertTrue(result_b["indexing_confirmed"])
        doc_id_b = result_b["document_id"]
        self.assertTrue(doc_id_b.startswith("doc_"))
        self.assertNotEqual(doc_id_a, doc_id_b)

        # 3. Test Query on PDF A (Active Document = A)
        req_a = RAGQueryRequest(
            question="Explain LRU page replacement algorithm in virtual memory",
            marks=5,
            document_id=doc_id_a
        )
        res_a = asyncio.run(process_rag_query(req_a))

        self.assertEqual(res_a.status, "success")
        self.assertFalse(res_a.abstain)
        self.assertIn("5-MARK ANSWER", res_a.answer)
        self.assertIn("LRU", res_a.answer)
        self.assertIsNotNone(res_a.citation)
        self.assertEqual(res_a.citation.document_name, filename_a)
        self.assertEqual(res_a.citation.page_number, 2)
        self.assertIsNotNone(res_a.citation.bounding_box)

        # 4. Test Query on PDF B (Active Document = B)
        req_b = RAGQueryRequest(
            question="What is the theoretical efficiency of a Carnot heat engine?",
            marks=5,
            document_id=doc_id_b
        )
        res_b = asyncio.run(process_rag_query(req_b))

        self.assertEqual(res_b.status, "success")
        self.assertFalse(res_b.abstain)
        self.assertIn("5-MARK ANSWER", res_b.answer)
        self.assertIn("Carnot", res_b.answer)
        self.assertIsNotNone(res_b.citation)
        self.assertEqual(res_b.citation.document_name, filename_b)
        self.assertEqual(res_b.citation.page_number, 1)

        # 5. Cross-Document Isolation Test:
        # Ask question whose answer is ONLY in PDF B, but target document_id is A!
        req_cross = RAGQueryRequest(
            question="What is the Carnot engine theoretical efficiency?",
            marks=5,
            document_id=doc_id_a
        )
        res_cross = asyncio.run(process_rag_query(req_cross))

        # Must abstain! Must NOT leak content from document B!
        self.assertTrue(res_cross.abstain)
        self.assertIn("Abstention Gate Triggered", res_cross.answer)
        self.assertIsNone(res_cross.citation)

        # 6. Marks-Aware Scaling Test on Arbitrary Document:
        # Same question on Document A across 2, 5, and 10 marks
        query_2m = asyncio.run(process_rag_query(RAGQueryRequest(
            question="Explain LRU page replacement algorithm in virtual memory",
            marks=2,
            document_id=doc_id_a
        )))
        query_5m = asyncio.run(process_rag_query(RAGQueryRequest(
            question="Explain LRU page replacement algorithm in virtual memory",
            marks=5,
            document_id=doc_id_a
        )))
        query_10m = asyncio.run(process_rag_query(RAGQueryRequest(
            question="Explain LRU page replacement algorithm in virtual memory",
            marks=10,
            document_id=doc_id_a
        )))

        self.assertIn("2-MARK ANSWER", query_2m.answer)
        self.assertIn("5-MARK ANSWER", query_5m.answer)
        self.assertIn("10-MARK ANSWER", query_10m.answer)

        # Depth progression: 2 marks < 5 marks < 10 marks
        len_2m = len(query_2m.answer)
        len_5m = len(query_5m.answer)
        len_10m = len(query_10m.answer)
        self.assertLess(len_2m, len_5m)
        self.assertLess(len_5m, len_10m)

        # 7. Off-topic Abstention Test on Active Document:
        query_off_topic = asyncio.run(process_rag_query(RAGQueryRequest(
            question="How do I bake a chocolate cake with sprinkles?",
            marks=5,
            document_id=doc_id_a
        )))
        self.assertTrue(query_off_topic.abstain)
        self.assertIn("Abstention Gate Triggered", query_off_topic.answer)

        # 8. Document Listing Endpoint (/api/documents)
        doc_list_res = asyncio.run(list_documents())
        self.assertEqual(doc_list_res.status, "success")
        listed_ids = [d.document_id for d in doc_list_res.documents]
        self.assertIn(doc_id_a, listed_ids)
        self.assertIn(doc_id_b, listed_ids)

        # 9. Document Retrieval Endpoint (/api/document/{doc_id})
        doc_meta = asyncio.run(get_document(doc_id_a))
        self.assertEqual(doc_meta["document_id"], doc_id_a)
        self.assertEqual(doc_meta["filename"], filename_a)
        self.assertEqual(doc_meta["pages_count"], 2)
        self.assertIn("pages", doc_meta)
        self.assertEqual(len(doc_meta["pages"]), 2)

    def test_empty_and_invalid_pdf_uploads(self):
        # Empty file returns 400
        empty_upload = UploadFile(filename="empty.pdf", file=io.BytesIO(b""))
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(ingest_document(empty_upload))
        self.assertEqual(ctx.exception.status_code, 400)

        # Non-pdf file returns 400
        txt_upload = UploadFile(filename="notes.txt", file=io.BytesIO(b"hello world"))
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(ingest_document(txt_upload))
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
