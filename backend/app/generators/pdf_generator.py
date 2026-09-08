import io
import re
from typing import Any, Dict, List, Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
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

    # 1. Header & Always-Visible Metadata Block
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