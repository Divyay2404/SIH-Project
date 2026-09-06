"""
Automated RAG & Diagnostic Unit Tests for SIH Prototype.
"""

import unittest
from app.rag.qa_engine import qa_engine
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

    def test_marks_aware_scaling_2_marks(self):
        result = qa_engine.answer_question("Explain BST deletion algorithm", marks=2)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["marks"], 2)
        self.assertIn("2-MARK ANSWER", result["answer"])
        self.assertIsNotNone(result["citation"])

    def test_marks_aware_scaling_10_marks(self):
        result = qa_engine.answer_question("Explain BST deletion algorithm", marks=10)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["marks"], 10)
        self.assertIn("10-MARK ANSWER", result["answer"])

    def test_evidence_or_abstain_gate(self):
        # Query that lacks textbook evidence
        result = qa_engine.answer_question("How do I bake a chocolate cake?", marks=2)
        self.assertTrue(result["abstain"])
        self.assertEqual(result["status"], "abstain")
        self.assertIn("Abstention Gate Triggered", result["answer"])

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
