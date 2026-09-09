"""
ReportLab Printable Double-Column Handout Exporter.
Compiles professional double-column B.Tech study guides, revision handouts,
and marks-aligned practice questions dynamically from uploaded course materials.
"""

import io
import re
from typing import Any, Dict, List, Optional

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate, SimpleDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


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
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Running Header
        self.drawString(36, 805, "B.TECH REVISION HANDOUT | ACADEMIC STUDY GUIDE")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(36, 798, 559, 798)

        # Running Footer
        self.line(36, 45, 559, 45)
        self.setFont("Helvetica", 8)
        self.drawString(36, 32, "Confidential - For Academic Use Only")
        self.drawRightString(559, 32, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


class StudyHandoutGenerator:
    """
    Generates printable ReportLab study guide handouts (.pdf)
    derived dynamically from uploaded curriculum materials.
    """
    def __init__(self):
        self.available = REPORTLAB_AVAILABLE

    @staticmethod
    def _safe_text(value: Any) -> str:
        text = str(value) if value is not None else ""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def generate_handout_pdf(self, document: Dict[str, Any]) -> bytes:
        """
        Builds a double-column printable study guide handout from the uploaded document.
        Returns PDF bytes for HTTP response streaming.
        """
        if not self.available:
            raise RuntimeError("ReportLab is required to generate PDF files.")

        title = document.get("title", "Study Guide")
        chunks: List[Dict[str, Any]] = document.get("chunks", [])
        if not chunks and not document.get("definitions") and not document.get("questions"):
            raise ValueError("The selected document has no extracted content to export.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocumentTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocumentSubTitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#475569"),
            spaceAfter=8,
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#2563eb"),
            spaceBefore=6,
            spaceAfter=3,
        )
        body_style = ParagraphStyle(
            "DocumentBody",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )
        summary_style = ParagraphStyle(
            "SummaryBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        )

        safe_title = self._safe_text(title)
        story = [
            Paragraph(f"B.Tech Study Guide: {safe_title}", title_style),
            Paragraph(f"Verified Academic Knowledge Base | Generated for {safe_title}", subtitle_style),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=8),
        ]

        # Executive Summary if present
        summary = document.get("summary")
        if summary:
            story.append(Paragraph("<b>Executive Curriculum Summary</b>", heading_style))
            clean_summary = self._safe_text(summary).replace("\n", "<br/>")
            story.append(Paragraph(clean_summary, summary_style))
            story.append(Spacer(1, 4))

        # Double-column layout for chunk sections using a multi-row grid
        # Each row contains at most 2 chunks, allowing ReportLab to split between rows across pages seamlessly
        if chunks:
            table_data = []
            for i in range(0, len(chunks), 2):
                row_cells = []
                for j in range(2):
                    if i + j < len(chunks):
                        chunk = chunks[i + j]
                        page_info = f" (Page {chunk.get('page')})" if chunk.get("page") else ""
                        raw_text = self._safe_text(chunk.get("text", "")).strip()
                        clean_text = raw_text.replace("\n", "<br/>")
                        cell_flowables = [
                            Paragraph(f"<b>Section {i + j + 1}{page_info}</b>", heading_style),
                            Paragraph(clean_text, body_style),
                            Spacer(1, 4),
                        ]
                        row_cells.append(cell_flowables)
                    else:
                        row_cells.append("")
                table_data.append(row_cells)

            if table_data:
                story.append(Table(
                    table_data,
                    colWidths=[265, 265],
                    style=TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LINEBEFORE", (1, 0), (1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ])
                ))
                story.append(Spacer(1, 8))

        # Important Concepts / Definitions if present
        concepts = document.get("important_concepts") or document.get("definitions")
        if concepts:
            story.append(Paragraph("Key Terminology & Concepts", heading_style))
            if isinstance(concepts, list):
                for item in concepts:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        term, defn = item
                        story.append(Paragraph(f"• <b>{self._safe_text(term)}:</b> {self._safe_text(defn)}", body_style))
                    else:
                        story.append(Paragraph(f"• <b>{self._safe_text(item)}</b>", body_style))
            story.append(Spacer(1, 6))

        # Practice questions section
        story.append(Paragraph("Marks-Aligned Practice Questions", heading_style))
        story.append(Paragraph(f"<b>2 Marks:</b> Define the fundamental principles and operational boundaries of {safe_title}.", body_style))
        story.append(Paragraph(f"<b>5 Marks:</b> Explain the core mechanism, architecture, and step-by-step procedures of {safe_title}.", body_style))
        story.append(Paragraph(f"<b>10 Marks:</b> Provide an in-depth analytical evaluation, mathematical bounds, and edge-case analysis for {safe_title}.", body_style))

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()


def build_study_guide_pdf(course_data: dict, output_filepath: Optional[str] = None) -> str:
    """
    Compiles a double-column B.Tech study guide PDF using ReportLab.
    Always shows metadata headings, fixed author as 'Study Co-Pilot', and target audience as 'B.Tech CSE'.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab is required to generate PDF files.")

    if not output_filepath:
        title_raw = course_data.get('title', 'study_guide')
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title_raw).lower()
        safe_title = re.sub(r'_+', '_', safe_title).strip('_')
        output_filepath = f"{safe_title}.pdf"

    page_width, page_height = A4
    margin = 36
    gutter = 18

    printable_width = page_width - (2 * margin)
    column_width = (printable_width - gutter) / 2

    frame_top = page_height - 55
    frame_bottom = 55
    frame_height = frame_top - frame_bottom

    left_frame = Frame(margin, frame_bottom, column_width, frame_height, id='col1', topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
    right_frame = Frame(margin + column_width + gutter, frame_bottom, column_width, frame_height, id='col2', topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)

    doc = BaseDocTemplate(output_filepath, pagesize=A4)
    two_column_template = PageTemplate(id='two_column', frames=[left_frame, right_frame])
    doc.addPageTemplates([two_column_template])

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=colors.HexColor('#1A202C'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=4
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.white,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=11.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4
    )
    q_header_style = ParagraphStyle(
        'QHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#9C4221'),
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    story = []

    title_val = course_data.get('title', 'Study Guide')
    story.append(Paragraph(title_val, title_style))

    code_val = course_data.get('code', 'N/A')
    module_val = course_data.get('module', 'General')
    subtitle_text = f"<b>Course Code:</b> {code_val} | <b>Module:</b> {module_val}"
    story.append(Paragraph(subtitle_text, subtitle_style))

    meta_text = "<b>Target Audience:</b> B.Tech CSE &nbsp;&nbsp;|&nbsp;&nbsp; <b>Author:</b> Study Co-Pilot"
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 6))

    def create_section_header(title_text):
        t_table = Table([[Paragraph(title_text, section_heading)]], colWidths=[column_width])
        t_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#2B6CB0')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        return t_table

    definitions = course_data.get('definitions')
    if definitions:
        story.append(create_section_header("Key Definitions"))
        story.append(Spacer(1, 4))
        for term, definition in definitions:
            story.append(Paragraph(f"• <b>{term}:</b> {definition}", body_style))
        story.append(Spacer(1, 6))

    questions = course_data.get('questions')
    if questions:
        story.append(create_section_header("Practice Questions"))
        story.append(Spacer(1, 4))
        for marks in [2, 5, 10]:
            if marks in questions and questions[marks]:
                story.append(Paragraph(f"<b>[{marks} Marks Section]</b>", q_header_style))
                for idx, q_text in enumerate(questions[marks], 1):
                    story.append(Paragraph(f"{idx}. {q_text}", body_style))
                story.append(Spacer(1, 4))

    doc.build(story, canvasmaker=NumberedCanvas)
    return output_filepath


# Singleton instance exported for REST router and test compatibility
pdf_generator = StudyHandoutGenerator()