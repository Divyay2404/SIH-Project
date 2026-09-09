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
            if len(s_clean) > 12 and not s_clean.upper() in ["C", "F", "P", "AB", "FIG", "PAGE", "TABLE"]:
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

    def _add_architecture_diagram(
        self,
        slide,
        chunks: List[Dict[str, Any]],
        stages_input: Optional[List[Dict[str, Any]]] = None
    ):
        """Draws a formal 3-stage universal conceptual flow diagram utilizing consecutive chunk text."""
        try:
            stages = []
            if stages_input:
                for st in stages_input:
                    title_t = st.get("stage", "STAGE")
                    if st.get("title"):
                        title_t = f"{title_t}: {st.get('title')}"
                    desc = st.get("description", "")
                    stages.append((title_t, desc))
            else:
                collected_sentences = []
                for chunk in chunks:
                    sentences = self._clean_and_stitch_text(chunk.get("text", ""))
                    for s in sentences:
                        if len(s) > 15 and s not in collected_sentences and not any(w in s for w in ["Figure", "Table", "Page"]):
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

            for i, (title_text, sub_text) in enumerate(stages[:3]):
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
                p1.text = title_text[:35]
                p1.font.bold = True
                p1.font.size = Pt(14)
                p1.font.color.rgb = RGBColor(30, 64, 175)

                p2 = tf.add_paragraph()
                p2.text = sub_text[:120]
                p2.font.size = Pt(12)
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
        """
        Builds a 10-slide educational deck containing Title Slide, Overview,
        Theoretical Foundations, Concept Breakdowns, Universal Diagram Slide,
        Real-World Applications, Critical Analysis, Assessment Standards, and Summary
        with deep speaker notes as an editable binary stream.
        """
        if not self.available:
            raise RuntimeError("python-pptx is required to generate PowerPoint files.")

        title = document.get("title", "Lecture Presentation")
        chunks = document.get("chunks", [])
        slides_data = document.get("slides")

        if not chunks and not slides_data:
            raise ValueError("The selected document has no extracted content to export.")

        if not slides_data:
            from app.ingestion.document_analyzer import document_analyzer
            analysis = document_analyzer.analyze_document(chunks, raw_title=title)
            slides_data = analysis.get("slides", [])

        prs = Presentation()
        title_layout = prs.slide_layouts[0]
        content_layout = prs.slide_layouts[1]

        for s_idx, slide_info in enumerate(slides_data):
            category = slide_info.get("category", "")
            is_title = (s_idx == 0) or (category == "Title Slide")

            if is_title:
                slide = prs.slides.add_slide(title_layout)
                slide.shapes.title.text = slide_info.get("title", title)
                if len(slide.placeholders) > 1:
                    slide.placeholders[1].text = slide_info.get("subtitle", "Curriculum Briefing & Educational Outline")
            else:
                slide = prs.slides.add_slide(content_layout)
                slide_title = slide_info.get("title", f"Curriculum Module {s_idx}")
                self._style_title(slide, slide_title)

                if slide_info.get("diagram"):
                    self._add_architecture_diagram(
                        slide,
                        chunks=chunks,
                        stages_input=slide_info.get("diagramStages")
                    )
                    diag_shape = slide.shapes.placeholders[1]
                    diag_shape.top = Inches(3.8)
                    diag_shape.left = Inches(0.8)
                    diag_shape.width = Inches(8.4)
                    diag_shape.height = Inches(3.0)

                    diag_tf = diag_shape.text_frame
                    diag_tf.word_wrap = True
                    diag_tf.clear()

                    bullets = slide_info.get("bullets", [])
                    for idx, pt in enumerate(bullets[:4]):
                        self._add_bullet(diag_tf, pt, is_first=(idx == 0), font_size=20)
                else:
                    tf = slide.shapes.placeholders[1].text_frame
                    tf.clear()
                    bullets = slide_info.get("bullets", [])
                    for idx, pt in enumerate(bullets[:5]):
                        self._add_bullet(tf, pt, is_first=(idx == 0))

            if slide_info.get("notes"):
                self._add_speaker_notes(slide, slide_info["notes"])

        buffer = io.BytesIO()
        prs.save(buffer)
        return buffer.getvalue()


ppt_generator = PresentationGenerator()