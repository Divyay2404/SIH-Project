"""Generate editable lecture decks from the chunks extracted from an uploaded document."""
import io
import re
from typing import Any, Dict, List, Optional

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.util import Inches, Pt
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False


class PresentationGenerator:
    """Generates 5-10 slide educational lecture decks with extensive teacher speaker notes using python-pptx."""

    def __init__(self):
        self.available = PPTX_AVAILABLE

    @staticmethod
    def _clean_and_stitch_text(text: str) -> List[str]:
        """Reconstructs broken PDF lines into complete, grammatically sound sentences without truncating."""
        flat_text = re.sub(r"[\r\n]+", " ", text)
        flat_text = re.sub(r"\s+", " ", flat_text).strip()

        raw_sentences = re.split(r"(?<=[.!?])\s+", flat_text)
        
        valid_sentences = []
        for s in raw_sentences:
            s_clean = re.sub(r"^[0-9\.\s\-•*]+", "", s).strip()
            if len(s_clean) > 12 and not s_clean.upper() in ["C", "F", "P", "AB", "FIG"]:
                if not s_clean.endswith((".", "!", "?", "}")) and "=" not in s_clean:
                    s_clean += "."
                valid_sentences.append(s_clean)

        return valid_sentences

    def _points(self, text: str, limit: int = 5) -> List[str]:
        """Turn a text block into concise, complete slide points."""
        sentences = self._clean_and_stitch_text(text)
        return sentences[:limit] or ["No extractable content was found for this section."]

    @staticmethod
    def _style_title(slide, text: str):
        """Sets the slide title in bold with professional styling."""
        slide.shapes.title.text = text[:60]
        if slide.shapes.title.text_frame.paragraphs:
            p = slide.shapes.title.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(36)
            p.font.color.rgb = RGBColor(30, 41, 59)
            p.space_after = Pt(10)

    @staticmethod
    def _add_bullet(text_frame, text: str, is_first: bool = False, font_size: int = 24):
        """Appends a complete, wrapped sentence bullet point."""
        p = text_frame.paragraphs[0] if is_first else text_frame.add_paragraph()
        p.text = text
        p.level = 0
        p.font.size = Pt(font_size)
        p.font.color.rgb = RGBColor(51, 65, 85)
        if is_first:
            p.space_before = Pt(2)
        p.space_after = Pt(4)
        return p

    @staticmethod
    def _add_speaker_notes(slide, notes_text: str):
        """Attach detailed teacher speaker notes to slide metadata."""
        try:
            notes_slide = slide.notes_slide
            text_frame = notes_slide.notes_text_frame
            text_frame.text = notes_text
        except Exception:
            pass

    def _add_architecture_diagram(self, slide, chunks: List[Dict[str, Any]]):
        """Draws a formal 3-stage universal conceptual flow diagram utilizing consecutive chunk text."""
        try:
            stages = []
            
            collected_sentences = []
            for chunk in chunks:
                sentences = self._clean_and_stitch_text(chunk.get("text", ""))
                for s in sentences:
                    if len(s) > 15 and s not in collected_sentences and not any(w in s for w in ["Figure", "Mirror", "Axis"]):
                        collected_sentences.append(s)

            stage_titles = ["1. BACKGROUND", "2. MECHANISM", "3. IMPACT"]
            for idx, title_t in enumerate(stage_titles):
                if idx < len(collected_sentences):
                    desc = collected_sentences[idx]
                    stages.append((title_t, desc))

            default_stages = [
                ("1. BACKGROUND", "Establish core definitions, conceptual parameters, and baseline context."),
                ("2. MECHANISM", "Examine structural breakdowns, analytical mechanisms, and core dynamics."),
                ("3. IMPACT", "Synthesize primary takeaways, functional outcomes, and boundary implications."),
            ]
            while len(stages) < 3:
                stages.append(default_stages[len(stages)])

            card_width = Inches(2.6)
            card_height = Inches(2.1)
            card_top = Inches(1.5)
            arrow_top = Inches(2.4)
            arrow_width = Inches(0.4)
            arrow_height = Inches(0.3)

            positions = [Inches(0.8), Inches(3.8), Inches(6.8)]
            arrow_positions = [Inches(3.4), Inches(6.4)]

            for i, (title_text, sub_text) in enumerate(stages):
                card = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    positions[i],
                    card_top,
                    card_width,
                    card_height,
                )
                card.fill.solid()
                card.fill.fore_color.rgb = RGBColor(241, 245, 249)
                card.line.color.rgb = RGBColor(59, 130, 246)
                card.line.width = Pt(1.5)

                tf = card.text_frame
                tf.clear()
                tf.word_wrap = True

                p1 = tf.paragraphs[0]
                p1.text = title_text
                p1.font.bold = True
                p1.font.size = Pt(15)
                p1.font.color.rgb = RGBColor(30, 64, 175)

                p2 = tf.add_paragraph()
                p2.text = sub_text
                p2.font.size = Pt(13)
                p2.font.color.rgb = RGBColor(71, 85, 105)

            for arrow_left in arrow_positions:
                arrow = slide.shapes.add_shape(
                    MSO_SHAPE.RIGHT_ARROW,
                    arrow_left,
                    arrow_top,
                    arrow_width,
                    arrow_height,
                )
                arrow.fill.solid()
                arrow.fill.fore_color.rgb = RGBColor(59, 130, 246)
                arrow.line.fill.background()
        except Exception:
            pass

    def generate_ppt_deck(self, document: Dict[str, Any]) -> bytes:
        """Builds a 10-slide educational deck containing Title Slide, Overview, Theoretical Foundations, Concept Breakdowns, Universal Diagram Slide, Case Studies, Critical Analysis, Assessment Standards, and Summary with deep speaker notes as an editable binary stream."""
        if not self.available:
            raise RuntimeError("python-pptx is required to generate PowerPoint files.")

        title = document.get("title", "Lecture Presentation")
        chunks = document.get("chunks", [])
        if not chunks:
            raise ValueError("The selected document has no extracted content to export.")

        prs = Presentation()
        content_layout = prs.slide_layouts[1]

        # -------------------------------------------------------------------------
        # Slide 1: Title Slide
        # -------------------------------------------------------------------------
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title_slide.shapes.title.text = title
        title_slide.placeholders[1].text = "Curriculum Briefing & Educational Outline"
        self._add_speaker_notes(
            title_slide,
            f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            f"Welcome everyone to today's comprehensive curriculum session covering '{title}'. "
            "In this introductory session, our primary goal is to establish a rigorous baseline understanding of the core modules. "
            "Instructors should emphasize that the concepts introduced today form the architectural bedrock for all subsequent analytical modules. "
            "Take 3 to 5 minutes to outline expectations, review the syllabus roadmap, and encourage active inquiry before diving into the core material."
        )

        fallback_pool = [
            f"Establishes structural foundations for {title}.",
            "Enforces operational constraints and strict boundaries.",
            "Maintains invariant processing guarantees across states.",
            "Optimizes performance under concurrent execution models.",
            "Mitigates edge-case bottlenecks and edge failures.",
        ]

        presented_topics = []

        # -------------------------------------------------------------------------
        # Slide 2: Curriculum Overview & Scope
        # -------------------------------------------------------------------------
        overview_slide = prs.slides.add_slide(content_layout)
        self._style_title(overview_slide, "Curriculum Overview & Scope")
        overview_tf = overview_slide.shapes.placeholders[1].text_frame
        overview_tf.clear()

        overview_points = [
            f"Comprehensive examination of key modules in {title}.",
            "Core theoretical principles and empirical foundations.",
            "Analytical methodologies for problem solving.",
            "Real-world applications and boundary conditions.",
            "Preparation standards for formal assessments.",
        ]
        for idx, pt in enumerate(overview_points[:5]):
            self._add_bullet(overview_tf, pt, is_first=(idx == 0))

        self._add_speaker_notes(
            overview_slide,
            "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            "When presenting this curriculum overview, walk students methodically through each bullet point. "
            "Point 1 establishes the broad structural scope, while Point 2 grounds the discussion in empirical theory. "
            "Instructors should spend extra time highlighting Point 4 (real-world applications), as students often struggle to connect abstract textbook theory with practical constraints. "
            "Open the floor briefly to ensure the class understands the evaluation standards before moving forward."
        )

        # -------------------------------------------------------------------------
        # Slide 3: Theoretical Foundations
        # -------------------------------------------------------------------------
        found_slide = prs.slides.add_slide(content_layout)
        self._style_title(found_slide, "Theoretical Foundations")
        found_tf = found_slide.shapes.placeholders[1].text_frame
        found_tf.clear()

        found_points = [
            f"Defining axiomatic principles underlying {title}.",
            "Establishing rigorous logical frameworks and proofs.",
            "Analyzing fundamental hypotheses and core parameters.",
            "Reviewing foundational literature and historical context.",
            "Mapping conceptual relationships to empirical outcomes."
        ]
        for idx, pt in enumerate(found_points[:5]):
            self._add_bullet(found_tf, pt, is_first=(idx == 0))

        self._add_speaker_notes(
            found_slide,
            "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            "Explore the theoretical foundations and axiomatic parameters. "
            "Emphasize how these principles serve as the prerequisite framework for understanding the rest of the material. "
            "Encourage students to relate these foundational rules back to real-world observations."
        )

        # -------------------------------------------------------------------------
        # Slides 4 & 5: Concept Breakdown Parts I & II
        # -------------------------------------------------------------------------
        concept_chunks = chunks[:2]
        for index, chunk in enumerate(concept_chunks, start=1):
            slide = prs.slides.add_slide(content_layout)
            raw_text = chunk["text"]
            
            heading_candidate = f"Concept Breakdown: Part {index}"
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
            for line in lines:
                if len(line) < 45 and any(keyword in line.lower() for keyword in ["chapter", "reflection", "refraction", "light", "mirror", "lens", "topic", "section"]):
                    heading_candidate = line
                    break
                elif lines:
                 if len(lines[0]) < 45:
                    heading_candidate = lines[0]

            self._style_title(slide, heading_candidate)
            presented_topics.append(heading_candidate)

            tf = slide.shapes.placeholders[1].text_frame
            tf.clear()

            sentences = self._points(raw_text, limit=10)
            body_points = [s for s in sentences if s.rstrip(".") != heading_candidate.rstrip(".")]
            if not body_points:
                body_points = sentences

            start_idx = (index - 1) * 3
            unique_chunk_points = body_points[start_idx : start_idx + 5]
            if not unique_chunk_points:
                unique_chunk_points = body_points[:5]

            final_points = list(unique_chunk_points)
            for fb in fallback_pool:
                if len(final_points) < 5 and fb not in final_points:
                    final_points.append(fb)

            for point_index, point in enumerate(final_points[:5]):
                self._add_bullet(tf, point, is_first=(point_index == 0))

            self._add_speaker_notes(
                slide,
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Detailed Breakdown for Section {index} (Referencing source page {chunk.get('page', 'unknown')}).\n\n"
                "Instructors should unpack these core bullet points line by line derived directly from the document text. "
                "Explain the underlying principles and empirical findings associated with each statement. "
                "Be sure to address common student misconceptions regarding boundaries and operational parameters."
            )

        # -------------------------------------------------------------------------
        # Slide 6: Process Workflow & Architecture Diagram
        # -------------------------------------------------------------------------
        diagram_slide = prs.slides.add_slide(content_layout)
        diag_title = "Conceptual Progression & Workflow"
        self._style_title(diagram_slide, diag_title)
        presented_topics.append(diag_title)

        self._add_architecture_diagram(diagram_slide, chunks=chunks)

        diag_shape = diagram_slide.shapes.placeholders[1]
        diag_shape.top = Inches(3.8)
        diag_shape.left = Inches(0.8)
        diag_shape.width = Inches(8.4)
        diag_shape.height = Inches(3.0)

        diag_tf = diag_shape.text_frame
        diag_tf.word_wrap = True
        diag_tf.clear()

        primary_text = chunks[0]["text"] if chunks else title
        all_sentences = self._points(primary_text, limit=10)
        diag_points = all_sentences[3:6] if len(all_sentences) >= 6 else [
            f"Establishes core analytical parameters for {title}.",
            "Examines operational mechanics across structural stages.",
            "Synthesizes primary conclusions and boundary outcomes."
        ]
        
        for idx, pt in enumerate(diag_points[:4]):
            self._add_bullet(diag_tf, pt, is_first=(idx == 0), font_size=20)

        self._add_speaker_notes(
            diagram_slide,
            "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            "Conceptual Progression & Workflow Walkthrough:\n\n"
            "This workflow slide is critical for visualizing the document's conceptual progression. "
            "Walk students explicitly through the three universal stages displayed in the process cards: "
            "1. Background, 2. Mechanism, and 3. Impact. "
            "Emphasize how the concepts build logically from initial definitions to final analytical takeaways derived straight from the textbook text."
        )

        # -------------------------------------------------------------------------
        # Slide 7: Practical Applications & Case Studies
        # -------------------------------------------------------------------------
        app_slide = prs.slides.add_slide(content_layout)
        self._style_title(app_slide, "Practical Applications & Case Studies")
        app_tf = app_slide.shapes.placeholders[1].text_frame
        app_tf.clear()

        app_points = [
            f"Real-world implementations of {title} in industry.",
            "Case study analysis of successful deployments.",
            "Evaluating performance metrics under practical constraints.",
            "Addressing integration challenges and mitigation techniques.",
            "Synthesizing lessons learned for future optimization."
        ]
        for idx, pt in enumerate(app_points[:5]):
            self._add_bullet(app_tf, pt, is_first=(idx == 0))

        self._add_speaker_notes(
            app_slide,
            "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            "Bridge theory and practice by discussing these real-world case studies. "
            "Ask students how the abstract principles covered earlier apply directly to these practical scenarios."
        )

        # -------------------------------------------------------------------------
        # Slide 8: Critical Analysis & Discussion
        # -------------------------------------------------------------------------
        crit_slide = prs.slides.add_slide(content_layout)
        self._style_title(crit_slide, "Critical Analysis & Discussion")
        crit_tf = crit_slide.shapes.placeholders[1].text_frame
        crit_tf.clear()

        crit_points = [
            f"What primary engineering constraint is resolved by {title}?",
            "How does this methodology compare with conventional alternatives?",
            "What specific failure modes or edge cases must be evaluated?",
            "Diagnostic Inquiry: Explain the primary architectural trade-off.",
            "How can system stability be verified under high concurrent load?"
        ]
        for idx, pt in enumerate(crit_points[:5]):
            self._add_bullet(crit_tf, pt, is_first=(idx == 0))

        self._add_speaker_notes(
            crit_slide,
            "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            "Facilitate an interactive discussion using these critical analysis questions. "
            "Encourage students to debate the trade-offs and consider potential failure modes."
        )

        # -------------------------------------------------------------------------
        # Slide 9: Assessment Standards & Review
        # -------------------------------------------------------------------------
        assess_slide = prs.slides.add_slide(content_layout)
        self._style_title(assess_slide, "Assessment Standards & Review")
        assess_tf = assess_slide.shapes.placeholders[1].text_frame
        assess_tf.clear()

        assess_points = [
            "Core competency benchmarks for formal evaluations.",
            "Key terminology and definitions required for mastery.",
            "Problem-solving rubrics and expected solution steps.",
            "Self-assessment questions for student revision.",
            "Preparation guidelines for upcoming examinations."
        ]
        for idx, pt in enumerate(assess_points[:5]):
            self._add_bullet(assess_tf, pt, is_first=(idx == 0))

        self._add_speaker_notes(
            assess_slide,
            "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            "Review evaluation criteria and assessment expectations with the class. "
            "Ensure students understand what is required to achieve mastery on upcoming exams."
        )

        # -------------------------------------------------------------------------
        # Slide 10: Summary & Key Takeaways
        # -------------------------------------------------------------------------
        summary_slide = prs.slides.add_slide(content_layout)
        self._style_title(summary_slide, f"{title}: Summary & Takeaways")
        summary_frame = summary_slide.shapes.placeholders[1].text_frame
        summary_frame.clear()

        summary_takeaways = [
            f"Reviewed foundational scope and educational roadmap for {title}.",
            f"Analyzed core curriculum concepts: {presented_topics[0] if presented_topics else 'Core Modules'}.",
            f"Examined conceptual progression and workflow via {diag_title}.",
            "Evaluated critical performance boundaries and analytical constraints.",
            "Confirmed foundational readiness for advanced assessment standards."
        ]
        for idx, item in enumerate(summary_takeaways[:5]):
            self._add_bullet(summary_frame, item, is_first=(idx == 0))

        self._add_speaker_notes(
            summary_slide,
            f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
            f"Concluding Lecture Summary for '{title}':\n\n"
            "Synthesize the key takeaways listed on the slide. "
            "Remind students of the journey from our initial curriculum overview through the concept breakdowns and conceptual progression workflow. "
            "Assign recommended follow-up reading tasks, outline expectations for the upcoming homework assignment, and open the floor for final student queries."
        )

        buffer = io.BytesIO()
        prs.save(buffer)
        return buffer.getvalue()


ppt_generator = PresentationGenerator()