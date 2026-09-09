"""
Automated RAG & Diagnostic Unit Tests for SIH Prototype.
Verifies marks-aware prompt scaling, strict document_id scoping,
evidence-or-abstain security gating, and dynamic context grounding.
"""

import unittest
from app.rag.qa_engine import qa_engine
from app.rag.vector_store import vector_store
from app.diagnostics.learner_state import learner_engine
from app.generators.ppt_generator import ppt_generator
from app.generators.pdf_generator import pdf_generator


EXPORT_DOCUMENT = {
    "title": "Operating Systems Scheduling",
    "chunks": [
        {"page": 1, "text": "Process Scheduling\nThe scheduler selects a ready process for CPU execution."},
    ],
}


class TestSIHBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        vector_store.load_demo_knowledge()

    def test_marks_aware_scaling_2_marks(self):
        result = qa_engine.answer_question("Explain BST deletion algorithm", marks=2)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["marks"], 2)
        self.assertIn("2-MARK ANSWER", result["answer"])
        self.assertIsNotNone(result["citation"])

    def test_marks_aware_scaling_5_marks(self):
        result = qa_engine.answer_question("Explain BST insertion algorithm", marks=5)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["marks"], 5)
        self.assertIn("5-MARK ANSWER", result["answer"])
        self.assertIn("Overview", result["answer"])
        self.assertIsNotNone(result["citation"])

    def test_marks_aware_scaling_10_marks(self):
        result = qa_engine.answer_question("Explain BST deletion algorithm", marks=10)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["marks"], 10)
        self.assertIn("10-MARK ANSWER", result["answer"])
        self.assertIn("Abstract & Academic Definition", result["answer"])

    def test_evidence_or_abstain_gate(self):
        # Query that lacks textbook evidence
        result = qa_engine.answer_question("How do I bake a chocolate cake?", marks=2)
        self.assertTrue(result["abstain"])
        self.assertEqual(result["status"], "abstain")
        self.assertIn("Abstention Gate Triggered", result["answer"])
        self.assertIsNone(result["citation"])

    def test_vector_store_strict_document_filtering(self):
        # Searching with valid default document_id
        matches = vector_store.search("BST deletion", document_id="doc_bst_chapter_01")
        self.assertGreater(len(matches), 0)
        for m in matches:
            self.assertEqual(m["document_id"], "doc_bst_chapter_01")

        # Searching with non-existent document_id must return empty list
        empty_matches = vector_store.search("BST deletion", document_id="doc_non_existent_999")
        self.assertEqual(len(empty_matches), 0)

    def test_document_scoping_in_qa_engine(self):
        # Query with valid document_id succeeds
        valid_res = qa_engine.answer_question(
            "Explain BST deletion algorithm",
            marks=5,
            document_id="doc_bst_chapter_01"
        )
        self.assertEqual(valid_res["status"], "success")
        self.assertFalse(valid_res["abstain"])
        self.assertEqual(valid_res["citation"]["document_name"], "Binary_Search_Trees_Chapter.pdf")
        self.assertEqual(valid_res["citation"]["page_number"], 3)

        # Query with invalid document_id triggers Evidence Abstention Gate
        invalid_res = qa_engine.answer_question(
            "Explain BST deletion algorithm",
            marks=5,
            document_id="doc_wrong_scope_123"
        )
        self.assertEqual(invalid_res["status"], "abstain")
        self.assertTrue(invalid_res["abstain"])
        self.assertIsNone(invalid_res["citation"])
        self.assertIn("Abstention Gate Triggered", invalid_res["answer"])

    def test_grounded_answer_from_arbitrary_uploaded_document(self):
        # Verify qa_engine dynamically generates answers from newly ingested document chunks
        # without hardcoding to BST topics
        custom_doc_id = "doc_os_scheduling_test"
        custom_chunks = [
            {
                "page": 1,
                "text": "Round Robin CPU Scheduling allocates a fixed time quantum of 10ms to every ready process sequentially.",
                "bbox": [20.0, 40.0, 400.0, 150.0],
                "document_id": custom_doc_id,
                "document_name": "OS_Operating_Systems.pdf"
            }
        ]
        vector_store.add_chunks(custom_chunks)

        res = qa_engine.answer_question(
            "Explain Round Robin CPU scheduling time quantum",
            marks=2,
            document_id=custom_doc_id
        )
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["abstain"])
        self.assertEqual(res["citation"]["document_name"], "OS_Operating_Systems.pdf")
        self.assertIn("Round Robin", res["answer"])
        self.assertNotIn("BST Deletion removes", res["answer"])

    def test_diagnostic_error_taxonomy(self):
        # Incorrect option select (1 = conceptual gap)
        diagnosis = learner_engine.evaluate_quiz_answer("q_bst_del_01", selected_option=1)
        self.assertFalse(diagnosis["is_correct"])
        self.assertEqual(diagnosis["error_category"], "conceptual_gap")
        self.assertTrue(diagnosis["rescue_mission_triggered"])
        self.assertIn("30-Minute Rescue Mission", diagnosis["rescue_mission"]["title"])

    def test_ppt_export_generator(self):
        if not ppt_generator.available:
            self.skipTest("python-pptx is not installed")
        ppt_bytes = ppt_generator.generate_ppt_deck(EXPORT_DOCUMENT)
        self.assertGreater(len(ppt_bytes), 0)

    def test_pdf_handout_generator(self):
        if not pdf_generator.available:
            self.skipTest("ReportLab is not installed")
        pdf_bytes = pdf_generator.generate_handout_pdf(EXPORT_DOCUMENT)
        self.assertGreater(len(pdf_bytes), 0)


if __name__ == "__main__":
    unittest.main()
