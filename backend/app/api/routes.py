"""
FastAPI REST Router for SIH 2026 Prototype Gateway.
Connects UI to PyMuPDF parsing, RAG qa_engine, diagnostic learner_state,
and PPT/PDF generator modules.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Response, UploadFile, File, Query

from app.schemas.api_schemas import (
    HealthCheckResponse,
    RootHealthResponse,
    IngestResponse,
    CitationMetadata,
    RAGQueryRequest,
    RAGQueryResponse,
    QuizQuestionResponse,
    QuizSubmissionRequest,
    RescueMissionDetails,
    DiagnosticResponse,
    TopicHeatmapItem,
    ReadinessResponse,
    ErrorResponse,
)

from app.ingestion.pdf_parser import pdf_parser_engine
from app.rag.vector_store import vector_store
from app.rag.qa_engine import qa_engine
from app.diagnostics.learner_state import learner_engine
from app.generators.ppt_generator import ppt_generator
from app.generators.pdf_generator import pdf_generator

router = APIRouter(prefix="/api")

# The prototype keeps parsed export material in process memory. The ID returned
# by /ingest is the only document an export endpoint is allowed to use.
document_exports: Dict[str, Dict[str, Any]] = {}


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="API Gateway Health Check",
    tags=["Health"]
)
async def health_check() -> HealthCheckResponse:
    """Returns gateway service health status, engine identifier, and version."""
    return HealthCheckResponse(
        status="online",
        system="StudyCopilot & StudyForge Engine",
        version="1.0.0"
    )


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    summary="Execute grounded marks-aware RAG query",
    tags=["RAG"],
    responses={
        500: {"model": ErrorResponse, "description": "RAG engine execution error"}
    }
)
async def process_rag_query(request: RAGQueryRequest) -> RAGQueryResponse:
    """Executes grounded, evidence-gated RAG query with marks-aware output (2, 5, 10 marks)."""
    try:
        result = qa_engine.answer_question(
            question=request.question,
            marks=request.marks,
            document_id=request.document_id
        )
        return RAGQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest PDF textbook chapter and index vectors",
    tags=["Ingestion"],
    responses={
        400: {"model": ErrorResponse, "description": "File format invalid or empty file"},
        422: {"model": ErrorResponse, "description": "No readable text extracted"},
        500: {"model": ErrorResponse, "description": "Ingestion processing error"}
    }
)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    """Ingests PDF textbook chapter, extracts text & coordinates, and indexes into vector memory."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Educator uploads currently support PDF documents only.")

    temp_path = ""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="The uploaded PDF file is empty.")

        # PyMuPDF needs a file path, so persist only this request's uploaded bytes
        # to a temporary PDF and remove it immediately after extraction.
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        chunks = pdf_parser_engine.parse_pdf(temp_path)
        if not chunks:
            raise HTTPException(status_code=422, detail="No readable text could be extracted from this document.")

        raw_filename = file.filename or "Uploaded_Document.pdf"
        document_id = f"doc_{uuid.uuid4().hex}"
        for chunk in chunks:
            chunk["document_id"] = document_id
            chunk["document_name"] = raw_filename
        vector_store.add_chunks(chunks)
        title = Path(raw_filename).stem.replace("_", " ").strip() or "Uploaded curriculum material"
        document_exports[document_id] = {
            "document_id": document_id,
            "title": title,
            "chunks": chunks,
            "filename": raw_filename,
        }
        return IngestResponse(
            status="success",
            document_id=document_id,
            title=title,
            filename=raw_filename,
            chunks_extracted=len(chunks),
            pages_processed=max((c.get("page", 0) for c in chunks), default=1),
            message="Document successfully parsed and indexed into vector repository with coordinate metadata."
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Ingestion failure: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get(
    "/quiz",
    response_model=QuizQuestionResponse,
    summary="Fetch active diagnostic micro-quiz question",
    tags=["Diagnostics"]
)
async def get_diagnostic_quiz() -> QuizQuestionResponse:
    """Fetches active diagnostic micro-quiz question."""
    return QuizQuestionResponse(
        question_id="q_bst_del_01",
        topic="Binary Search Tree Deletion",
        question_text="When deleting a BST node with two children, which node is substituted in its place to maintain the BST invariant?",
        options=[
            "In-Order Successor (Smallest key in right subtree)",
            "Pre-Order Traversal Root Node",
            "Right-most Leaf Node in Left Subtree",
            "Any random child node"
        ]
    )


@router.post(
    "/diagnose",
    response_model=DiagnosticResponse,
    summary="Diagnose student mistake against error taxonomy",
    tags=["Diagnostics"]
)
async def submit_quiz_answer(request: QuizSubmissionRequest) -> DiagnosticResponse:
    """Diagnoses student mistake against Error Taxonomy and triggers Rescue Mission if needed."""
    result = learner_engine.evaluate_quiz_answer(
        question_id=request.question_id,
        selected_option=request.selected_option,
        topic_id=request.topic_id
    )
    return DiagnosticResponse(**result)


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    summary="Retrieve student readiness heatmap and error breakdown",
    tags=["Diagnostics"]
)
async def get_readiness_analytics() -> ReadinessResponse:
    """Returns student readiness heatmap & class error distribution data."""
    data = learner_engine.get_readiness_heatmap()
    return ReadinessResponse(**data)


def _get_export_document(document_id: str) -> Dict[str, Any]:
    document = document_exports.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found. Upload a PDF before exporting.")
    return document


@router.get(
    "/export/ppt",
    summary="Export editable PowerPoint presentation deck (.pptx)",
    tags=["Exports"],
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": {}
            },
            "description": "Generated PowerPoint presentation deck file."
        },
        404: {"model": ErrorResponse, "description": "Document not found."},
        500: {"model": ErrorResponse, "description": "PPT Export failure."}
    }
)
async def export_ppt(
    document_id: str = Query(..., description="Document ID generated during /api/ingest")
):
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


@router.get(
    "/export/pdf",
    summary="Export printable ReportLab study guide handout (.pdf)",
    tags=["Exports"],
    responses={
        200: {
            "content": {
                "application/pdf": {}
            },
            "description": "Generated ReportLab study guide handout PDF."
        },
        404: {"model": ErrorResponse, "description": "Document not found."},
        500: {"model": ErrorResponse, "description": "PDF Export failure."}
    }
)
async def export_pdf(
    document_id: str = Query(..., description="Document ID generated during /api/ingest")
):
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
