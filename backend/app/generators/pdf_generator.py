import io
import re
from typing import Any, Dict, List, Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    canvas = None


if REPORTLAB_AVAILABLE and canvas is not None:
    class NumberedCanvas(canvas.Canvas):
        """Canvas for adding running headers and footers with accurate page counts."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pages = []

        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self.pages)
            for page in self.pages:
                self.__dict__.update(page)
                self.draw_header_footer(num_pages)
                super().showPage()
            super().save()

        def draw_header_footer(self, total_pages):
            page_width, page_height = A4
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#4A5568"))

            # Running Header (positioned clearly above top frame boundary)
            self.drawString(36, page_height - 35, "B.TECH REVISION HANDOUT | ACADEMIC STUDY GUIDE")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(36, page_height - 40, page_width - 36, page_height - 40)

            # Running Footer (positioned clearly below bottom frame boundary)
            self.line(36, 45, page_width - 36, 45)
            self.setFont("Helvetica", 8)
            self.drawString(36, 32, "Confidential - For Academic Use Only")
            self.drawRightString(page_width - 36, 32, f"Page {self._pageNumber} of {total_pages}")
            self.restoreState()
else:
    class NumberedCanvas:  # type: ignore[no-redef]
        """Fallback dummy canvas when ReportLab is unavailable."""
        pass


class StudyHandoutGenerator:
    """
    Generates printable ReportLab study guide handouts (.pdf)
    derived dynamically from uploaded curriculum materials in a true 2-column layout.
    """

    def __init__(self):
        self.available = REPORTLAB_AVAILABLE

    @staticmethod
    def _safe_text(value: Any) -> str:
        text = str(value) if value is not None else ""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    @staticmethod
    def _extract_subtopic_and_body(chunk_text: Any) -> tuple[str, str]:
        """Return a clean sub-topic title and paragraph body.

        A raw chunk may begin with a numbered or bullet style marker, for example
        "1. Process Scheduling" or "• Process Scheduling". The marker should not
        become a standalone heading, so this helper removes the marker from the
        topic label and keeps the written explanation in the paragraph body.
        """
        raw_text = str(chunk_text or "")
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        if not lines:
            return "Topic", ""

        # If the first line is just a numeric or bullet marker, attach the next
        # non-empty line as the actual topic title.
        if re.fullmatch(r"^\d+[\.)]$|^[-•]$", lines[0]):
            if len(lines) > 1:
                topic = lines[1]
                body_lines = lines[2:]
            else:
                return "Topic", ""
        else:
            topic = lines[0]
            body_lines = lines[1:]

        # Remove numeric/bullet markers embedded in the first topic line, such
        # as "1. Process Scheduling" or "2) Context Switching".
        topic = re.sub(r"^\s*\d+[\.\)]\s*", "", topic)
        topic = re.sub(r"^\s*[-•]\s*", "", topic)

        # Check if line begins with "Section N:"
        sec_match = re.match(r"^\s*(Section\s+\d+)\s*:\s*(.*)$", topic, flags=re.IGNORECASE)
        if sec_match:
            topic = sec_match.group(1)
            rest = sec_match.group(2).strip()
            if rest:
                body_lines.insert(0, rest)
        else:
            topic = re.sub(r"^\s*Topic\s*[:\-]\s*", "", topic, flags=re.IGNORECASE)

        # Trim remaining empty lines and join explanation paragraphs.
        body_lines = [line for line in body_lines if line.strip()]
        body = " ".join(body_lines) if body_lines else ""
        return topic, body

    def _generate_practice_questions(self, title: str, concepts: list, headings: list) -> Dict[int, List[str]]:
        """Generates marks-aligned 2, 5, and 10 mark practice questions."""
        safe_title = self._safe_text(title)
        c = [self._safe_text(x) for x in concepts[:5]] if concepts else [safe_title]
        h = [self._safe_text(x) for x in headings[:5]] if headings else [safe_title]

        q2 = [
            f"Define the fundamental principles and operational boundaries of {safe_title}.",
            f"State the primary characteristics and operational properties of {c[0]}.",
        ]
        if len(c) > 1:
            q2.append(f"List any two real-world engineering applications of {c[1]}.")

        q5 = [
            f"Explain the core mechanism, architecture, and step-by-step procedures of {safe_title} with a suitable diagram.",
            f"Describe the operational invariants and role of {h[0]} in the context of {safe_title}.",
        ]
        if len(h) > 1:
            q5.append(f"Compare and contrast {h[0]} with {h[1]}, highlighting operational trade-offs.")

        q10 = [
            f"Provide an in-depth analytical evaluation, mathematical bounds, and edge-case failure analysis for {safe_title}.",
            f"Design a complete system implementation demonstrating {safe_title}. Detail the algorithm, asymptotic complexity, and boundary error mitigations.",
        ]

        return {2: q2, 5: q5, 10: q10}

    def generate_handout_pdf(self, document: Dict[str, Any]) -> bytes:
        """
        Builds a true double-column printable study guide handout from the uploaded document.
        Returns PDF bytes for HTTP response streaming.
        """
        if not self.available:
            raise RuntimeError("ReportLab is required to generate PDF files.")

        title = document.get("title", "Study Guide")
        chunks: List[Dict[str, Any]] = document.get("chunks", [])
        if (
            not chunks
            and not document.get("definitions")
            and not document.get("important_concepts")
            and not document.get("questions")
        ):
            raise ValueError("The selected document has no extracted content to export.")

        page_width, page_height = A4
        margin = 36
        gutter = 14

        printable_width = page_width - (2 * margin)
        column_width = (printable_width - gutter) / 2

        frame_top = page_height - 55
        frame_bottom = 55
        frame_height = frame_top - frame_bottom

        left_frame = Frame(
            margin, frame_bottom, column_width, frame_height,
            id="col1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
        )
        right_frame = Frame(
            margin + column_width + gutter, frame_bottom, column_width, frame_height,
            id="col2", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
        )

        buffer = io.BytesIO()
        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=55,
            bottomMargin=55,
        )
        two_column_template = PageTemplate(id="two_column", frames=[left_frame, right_frame])
        doc.addPageTemplates([two_column_template])

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1A202C"),
            spaceAfter=3,
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#4A5568"),
            spaceAfter=3,
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.white,
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True,
        )
        item_heading = ParagraphStyle(
            "ItemHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True,
        )
        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor("#2D3748"),
            spaceAfter=3,
        )
        summary_style = ParagraphStyle(
            "SummaryBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor("#334155"),
            spaceAfter=4,
        )
        q_header_style = ParagraphStyle(
            "QHeader",
            parent=body_style,
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#9C4221"),
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True,
        )

        def create_section_header(title_text):
            t_table = Table([[Paragraph(title_text, section_heading)]], colWidths=[column_width])
            t_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2B6CB0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ])
            )
            return t_table

        safe_title = self._safe_text(title)
        story = []

        # 1. Title & Academic Header
        story.append(Paragraph(f"B.Tech Study Guide: {safe_title}", title_style))

        # Course Metadata
        filename = document.get("filename", "")
        code_hint = "N/A"
        if filename:
            code_match = re.search(r"([A-Z]{2,5}[\-_]?\d{3,5})", filename)
            if code_match:
                code_hint = code_match.group(1)
        code_val = document.get("code") or code_hint
        module_val = document.get("module") or safe_title
        page_count = document.get("page_count") or max((c.get("page", 1) for c in chunks), default=1)
        section_count = len(chunks)

        subtitle_text = f"<b>Course Code:</b> {code_val} &nbsp;|&nbsp; <b>Module:</b> {module_val}"
        story.append(Paragraph(subtitle_text, subtitle_style))

        meta_text = (
            f"<b>Target Audience:</b> B.Tech CSE &nbsp;|&nbsp; <b>Author:</b> Study Co-Pilot &nbsp;|&nbsp; "
            f"<b>Sections:</b> {section_count} &nbsp;|&nbsp; <b>Pages:</b> {page_count}"
        )
        story.append(Paragraph(meta_text, subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2B6CB0"), spaceAfter=5))

        # 2. Executive Curriculum Summary
        summary = document.get("summary")
        if summary:
            story.append(create_section_header("Executive Curriculum Summary"))
            story.append(Spacer(1, 3))
            clean_summary = self._safe_text(summary).replace("\n", "<br/>")
            story.append(Paragraph(clean_summary, summary_style))
            story.append(Spacer(1, 4))

        # 3. Content Sections (render as clean sub-topic headings with paragraph explanations)
        if chunks:
            story.append(create_section_header("Curriculum Content Sections"))
            story.append(Spacer(1, 3))
            for chunk in chunks:
                sub_topic, body_text = self._extract_subtopic_and_body(chunk.get("text", ""))
                if not sub_topic:
                    continue

                safe_topic = self._safe_text(sub_topic)
                safe_body = self._safe_text(body_text).replace("\n", "<br/>") if body_text else ""

                story.append(Paragraph(f"<b>Sub-topic: {safe_topic}</b>", item_heading))
                if safe_body:
                    story.append(Paragraph(safe_body, body_style))
                else:
                    story.append(Paragraph("", body_style))
                story.append(Spacer(1, 2))
            story.append(Spacer(1, 4))

        # 4. Key Definitions & Concepts
        definitions = document.get("definitions")
        concepts = document.get("important_concepts")
        key_items = definitions or concepts
        if key_items:
            story.append(create_section_header("Key Definitions &amp; Concepts"))
            story.append(Spacer(1, 3))
            if isinstance(key_items, list):
                for item in key_items:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        term, defn = item
                        story.append(Paragraph(f"• <b>{self._safe_text(term)}:</b> {self._safe_text(defn)}", body_style))
                    else:
                        story.append(Paragraph(f"• <b>{self._safe_text(item)}</b>", body_style))
            story.append(Spacer(1, 4))

        # 5. Important Portions (if available)
        portions = document.get("important_portions", [])
        if portions:
            story.append(create_section_header("Important Portions &amp; Exam Focus"))
            story.append(Spacer(1, 3))
            for p in portions:
                page_ref = f" [Page {p.get('page', '?')}]" if p.get("page") else ""
                lead = self._safe_text(p.get("lead_sentence", ""))
                crit_tag = " ★ CRITICAL" if p.get("is_critical") else ""
                story.append(Paragraph(f"<b>►{page_ref}{crit_tag}</b> {lead}", item_heading))
                snippet = self._safe_text(p.get("snippet", ""))
                if snippet and snippet != lead:
                    story.append(Paragraph(snippet, body_style))
                story.append(Spacer(1, 2))
            story.append(Spacer(1, 4))

        # 6. Practice Questions (2, 5, 10 Marks)
        story.append(create_section_header("Marks-Aligned Practice Questions"))
        story.append(Spacer(1, 3))

        custom_questions = document.get("questions")
        if isinstance(custom_questions, dict) and any(custom_questions.values()):
            questions_dict = custom_questions
        else:
            headings = document.get("sections") or [c.get("text", "")[:40] for c in chunks[:5]]
            conc_list = concepts if isinstance(concepts, list) else []
            questions_dict = self._generate_practice_questions(title, conc_list, headings)

        for marks in [2, 5, 10]:
            q_list = questions_dict.get(marks, [])
            if q_list:
                story.append(Paragraph(f"<b>[{marks} Marks Section]</b>", q_header_style))
                for idx, q_text in enumerate(q_list, 1):
                    story.append(Paragraph(f"{idx}. {self._safe_text(q_text)}", body_style))
                story.append(Spacer(1, 3))

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()


def build_study_guide_pdf(course_data: dict, output_filepath: Optional[str] = None) -> str:
    """
    Compiles a double-column B.Tech study guide PDF using ReportLab.
    Wrapper around StudyHandoutGenerator.generate_handout_pdf for file-based outputs.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab is required to generate PDF files.")

    if not output_filepath:
        title_raw = course_data.get("title", "study_guide")
        safe_title = re.sub(r"[^a-zA-Z0-9]", "_", title_raw).lower()
        safe_title = re.sub(r"_+", "_", safe_title).strip("_")
        output_filepath = f"{safe_title}.pdf"

    pdf_bytes = pdf_generator.generate_handout_pdf(course_data)
    with open(output_filepath, "wb") as f:
        f.write(pdf_bytes)
    return output_filepath


# Singleton instance exported for REST router and test compatibility
pdf_generator = StudyHandoutGenerator()