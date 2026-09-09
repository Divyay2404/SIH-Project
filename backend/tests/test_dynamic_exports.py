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

    def test_deep_document_analysis_for_full_slide_deck_and_ppt(self):
        """Verifies that multi-topic documents produce 10 deeply analyzed slides spanning the whole document."""
        from app.ingestion.document_analyzer import document_analyzer

        chunks = [
            {
                "page": 1,
                "text": "Distributed Consensus and State Replication.\nConsensus is the fundamental basis of fault-tolerant distributed computing.\nA distributed system achieves consensus when all non-faulty nodes agree on a single data value."
            },
            {
                "page": 2,
                "text": "Paxos Protocol Mechanics & Invariants.\nThe proposer dispatches prepare requests with monotonically increasing ballot numbers.\nAcceptors promise not to accept proposals with lower ballot numbers to preserve safety invariants."
            },
            {
                "page": 3,
                "text": "Raft Leader Election and Log Replication.\nIn Raft, a leader is elected through randomized election timeouts to prevent split votes.\nThe leader manages log entries and dispatches AppendEntries RPCs to follower replicas."
            },
            {
                "page": 4,
                "text": "Production Cluster Implementations & Deployments.\nModern cloud systems utilize distributed consensus in ZooKeeper, etcd, and Consul coordination engines.\nHardware network partitions require quorum intersection across independent failure domains."
            },
            {
                "page": 5,
                "text": "Critical Analysis & Latency Bottlenecks.\nRound-trip latency across geographically distributed regions creates a performance bottleneck.\nTrade-offs between strong consistency and availability are bounded by the CAP theorem under network partitions.\nAll state machine replication routines must strictly enforce monotonic sequence criteria."
            }
        ]

        title = "Distributed Consensus Protocols"
        analysis = document_analyzer.analyze_document(chunks, raw_title=title, filename="Distributed_Consensus.pdf")

        slides = analysis["slides"]
        self.assertEqual(len(slides), 10)

        # 1. Slide 1 (Title)
        self.assertEqual(slides[0]["category"], "Title Slide")
        self.assertIn("Distributed Consensus", slides[0]["title"])

        # 2. Slide 2 (Curriculum Overview)
        self.assertEqual(slides[1]["category"], "Curriculum Overview")
        self.assertTrue(any("Consensus is the fundamental basis" in b for b in slides[1]["bullets"]))

        # 3. Slide 3 (Theoretical Foundations)
        self.assertEqual(slides[2]["category"], "Theoretical Foundations")
        self.assertTrue(any("consensus when all non-faulty nodes agree" in b for b in slides[2]["bullets"]))

        # 4. Slide 4 & 5 (Mechanics & System Dynamics)
        s4_text = " ".join(slides[3]["bullets"])
        s5_text = " ".join(slides[4]["bullets"])
        self.assertTrue("proposer" in s4_text.lower() or "ballot" in s4_text.lower() or "raft" in s4_text.lower())
        self.assertTrue("leader" in s5_text.lower() or "appendentries" in s5_text.lower() or "raft" in s5_text.lower() or "acceptor" in s5_text.lower())

        # 5. Slide 6 (Diagram)
        self.assertTrue(slides[5]["diagram"])
        self.assertEqual(len(slides[5]["diagramStages"]), 3)
        self.assertIn("1. BACKGROUND", slides[5]["diagramStages"][0]["stage"])
        self.assertIn("2. MECHANISM", slides[5]["diagramStages"][1]["stage"])
        self.assertIn("3. IMPACT", slides[5]["diagramStages"][2]["stage"])

        # 6. Slide 7 (Real-World Applications)
        s7_text = " ".join(slides[6]["bullets"])
        self.assertTrue("zookeeper" in s7_text.lower() or "etcd" in s7_text.lower() or "cloud systems" in s7_text.lower() or "consul" in s7_text.lower())

        # 7. Slide 8 (Critical Analysis & Bottlenecks)
        s8_text = " ".join(slides[7]["bullets"])
        self.assertTrue("bottleneck" in s8_text.lower() or "latency" in s8_text.lower() or "trade-offs" in s8_text.lower() or "cap theorem" in s8_text.lower())

        # 8. Slide 9 (Assessment Standards)
        s9_text = " ".join(slides[8]["bullets"])
        self.assertIn("2 Marks", s9_text)
        self.assertIn("5 Marks", s9_text)
        self.assertIn("10 Marks", s9_text)
        self.assertTrue("monotonic sequence criteria" in s9_text.lower() or "boundary" in s9_text.lower() or "rubric" in s9_text.lower())

        # 9. Slide 10 (Summary)
        self.assertEqual(slides[9]["category"], "Summary & Takeaways")

        # 10. Verify speaker notes are populated for all 10 slides
        for idx, slide in enumerate(slides):
            self.assertIn("notes", slide, f"Slide {idx + 1} missing speaker notes")
            self.assertGreater(len(slide["notes"]), 50, f"Slide {idx + 1} notes too short")

        # 11. Verify PPT generation from analysis
        if ppt_generator.available:
            from pptx import Presentation
            ppt_bytes = ppt_generator.generate_ppt_deck({
                "title": title,
                "chunks": chunks,
                "slides": slides
            })
            prs = Presentation(io.BytesIO(ppt_bytes))
            self.assertEqual(len(prs.slides), 10)
            all_slide_text = "\n".join(shape.text for s in prs.slides for shape in s.shapes if hasattr(shape, "text"))
            self.assertIn("Distributed Consensus", all_slide_text)
            self.assertNotIn("Binary Search Trees", all_slide_text)


if __name__ == "__main__":
    unittest.main()
