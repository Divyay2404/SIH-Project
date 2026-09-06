"""Generate printable study handouts from the chunks extracted from an uploaded document."""

import io
from typing import Any, Dict, List

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class StudyHandoutGenerator:
    def __init__(self):
        self.available = REPORTLAB_AVAILABLE

    @staticmethod
    def _safe_text(value: str) -> str:
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def generate_handout_pdf(self, document: Dict[str, Any]) -> bytes:
        """Build a two-column handout whose content is derived from one document."""
        if not self.available:
            raise RuntimeError("ReportLab is required to generate PDF files.")

        title = document["title"]
        chunks: List[Dict[str, Any]] = document.get("chunks", [])
        if not chunks:
            raise ValueError("The selected document has no extracted content to export.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("DocumentTitle", parent=styles["Heading1"], fontSize=20, leading=24, textColor=colors.HexColor("#1e293b"), spaceAfter=6)
        heading_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], fontSize=12, leading=15, textColor=colors.HexColor("#2563eb"), spaceBefore=6, spaceAfter=4)
        body_style = ParagraphStyle("DocumentBody", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.HexColor("#0f172a"), spaceAfter=6)

        story = [
            Paragraph(f"Study Guide: {self._safe_text(title)}", title_style),
            Paragraph("Generated from the uploaded curriculum material", styles["Normal"]),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10),
        ]
        columns = [[], []]
        for index, chunk in enumerate(chunks):
            destination = columns[index % 2]
            source_text = self._safe_text(chunk["text"]).replace("\n", "<br/>")
            destination.extend([
                Paragraph(f"{index + 1}. Source section (page {chunk.get('page', 'n/a')})", heading_style),
                Paragraph(source_text, body_style),
            ])
        story.append(Table([[columns[0], columns[1]]], colWidths=[270, 270], style=TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBEFORE", (1, 0), (1, 0), 0.5, colors.HexColor("#cbd5e1")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Practice questions", heading_style))
        story.append(Paragraph(f"<b>2 marks:</b> Define one central idea from {self._safe_text(title)}.", body_style))
        story.append(Paragraph(f"<b>5 marks:</b> Explain a process or relationship described in {self._safe_text(title)}.", body_style))
        story.append(Paragraph(f"<b>10 marks:</b> Analyse the major concepts in {self._safe_text(title)} using evidence from the source material.", body_style))
        doc.build(story)
        return buffer.getvalue()


pdf_generator = StudyHandoutGenerator()
