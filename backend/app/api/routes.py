"""
FastAPI REST Router for SIH 2026 Prototype Gateway.
Connects UI to PyMuPDF parsing, RAG qa_engine, diagnostic learner_state,
and PPT/PDF generator modules.
"""

import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from app.ingestion.document_parser import UnsupportedDocumentError, document_parser
from app.rag.vector_store import vector_store
from app.rag.qa_engine import qa_engine
from app.diagnostics.learner_state import learner_engine
from app.generators.ppt_generator import ppt_generator
from app.generators.pdf_generator import pdf_generator

router = APIRouter(prefix="/api")

# The prototype keeps parsed export material in process memory.  The ID returned
# by /ingest is the only document an export endpoint is allowed to use.
document_exports: Dict[str, Dict[str, Any]] = {}


class RAGQueryRequest(BaseModel):
    question: str = Field(..., example="Explain Binary Search Tree deletion algorithm")
    marks: int = Field(default=5, example=5)
    document_id: Optional[str] = "doc_bst_chapter_01"


class QuizSubmissionRequest(BaseModel):
    question_id: str = Field(default="q_bst_del_01")
    selected_option: int = Field(..., example=1)
    topic_id: str = Field(default="bst_deletion")


@router.get("/health")
def health_check():
    return {"status": "online", "system": "StudyCopilot & StudyForge Engine", "version": "1.0.0"}


@router.post("/query")
def process_rag_query(request: RAGQueryRequest):
    """Executes grounded, evidence-gated RAG query with marks-aware output (2, 5, 10 marks)."""
    try:
        result = qa_engine.answer_question(question=request.question, marks=request.marks)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Ingests PDF textbook chapter, extracts text & coordinates, and indexes into vector memory."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in document_parser.SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Supported uploads are PDF, PPTX, and PPT files.")

    temp_path = ""
    try:
        # Parsers need a file path, so persist only this request's uploaded bytes
        # to a temporary file and remove it immediately after extraction.
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            temp_file.write(await file.read())

        chunks = document_parser.parse(temp_path)
        if not chunks:
            raise HTTPException(status_code=422, detail="No readable text could be extracted from this document.")

        document_id = f"doc_{uuid.uuid4().hex}"
        for chunk in chunks:
            chunk["document_id"] = document_id
        vector_store.add_chunks(chunks)
        title = Path(file.filename).stem.replace("_", " ").strip() or "Uploaded curriculum material"
        document_exports[document_id] = {
            "document_id": document_id,
            "title": title,
            "chunks": chunks,
            "filename": file.filename,
        }
        return {
            "status": "success",
            "document_id": document_id,
            "title": title,
            "filename": file.filename,
            "chunks_extracted": len(chunks),
            "pages_processed": max(c.get("page", 0) for c in chunks),
            "message": "Document successfully parsed and indexed into vector repository with coordinate metadata."
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        status_code = 422 if isinstance(e, UnsupportedDocumentError) else 500
        raise HTTPException(status_code=status_code, detail=f"Ingestion failure: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get("/quiz")
def get_diagnostic_quiz():
    """Fetches active diagnostic micro-quiz question."""
    return {
        "question_id": "q_bst_del_01",
        "topic": "Binary Search Tree Deletion",
        "question_text": "When deleting a BST node with two children, which node is substituted in its place to maintain the BST invariant?",
        "options": [
            "In-Order Successor (Smallest key in right subtree)",
            "Pre-Order Traversal Root Node",
            "Right-most Leaf Node in Left Subtree",
            "Any random child node"
        ]
    }


@router.post("/diagnose")
def submit_quiz_answer(request: QuizSubmissionRequest):
    """Diagnoses student mistake against Error Taxonomy and triggers Rescue Mission if needed."""
    result = learner_engine.evaluate_quiz_answer(
        question_id=request.question_id,
        selected_option=request.selected_option,
        topic_id=request.topic_id
    )
    return result


@router.get("/readiness")
def get_readiness_analytics():
    """Returns student readiness heatmap & class error distribution data."""
    return learner_engine.get_readiness_heatmap()


def _get_export_document(document_id: str) -> Dict[str, Any]:
    document = document_exports.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found. Upload a PDF or PowerPoint file before exporting.")
    return document


@router.get("/export/ppt")
def export_ppt(document_id: str):
    """Generates editable PowerPoint presentation deck (.pptx) with speaker notes."""
    try:
        document = _get_export_document(document_id)
        ppt_bytes = ppt_generator.generate_ppt_deck(document)
        filename_stem = document["title"].replace(" ", "_")
        return Response(
            content=ppt_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="Lecture_{filename_stem}.pptx"'}
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"PPT Export error: {str(e)}")


@router.get("/export/pdf")
def export_pdf(document_id: str):
    """Generates printable ReportLab study guide handout (.pdf)."""
    try:
        document = _get_export_document(document_id)
        pdf_bytes = pdf_generator.generate_handout_pdf(document)
        filename_stem = document["title"].replace(" ", "_")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="Study_Guide_{filename_stem}.pdf"'}
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"PDF Export error: {str(e)}")
