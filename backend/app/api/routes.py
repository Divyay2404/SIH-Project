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
    DocumentSummaryItem,
    DocumentListResponse,
)

from app.ingestion.pdf_parser import pdf_parser_engine
from app.ingestion.pptx_parser import pptx_parser_engine
from app.ingestion.document_analyzer import document_analyzer
from app.rag.vector_store import vector_store
from app.rag.qa_engine import qa_engine
from app.diagnostics.learner_state import learner_engine
from app.generators.ppt_generator import ppt_generator
from app.generators.pdf_generator import pdf_generator

router = APIRouter(prefix="/api")

# The prototype keeps parsed export material in process memory. The ID returned
# by /ingest is the only document an export endpoint is allowed to use.
document_exports: Dict[str, Dict[str, Any]] = {}


def _reconstruct_pages(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Reconstructs ordered page structures with paragraphs, headings, and bboxes for the PDF viewer."""
    page_dict: Dict[int, Dict[str, Any]] = {}
    for c in chunks:
        p = c.get("page", 1)
        if p not in page_dict:
            page_dict[p] = {
                "page": p,
                "title": f"Page {p}",
                "paragraphs": [],
                "chunks": []
            }
        text = c.get("text", "").strip()
        if not text:
            continue
        if c.get("is_heading") and page_dict[p]["title"] == f"Page {p}":
            page_dict[p]["title"] = text[:80]
        page_dict[p]["paragraphs"].append(text)
        page_dict[p]["chunks"].append({
            "text": text,
            "bbox": c.get("bbox", [50.0, 100.0, 500.0, 220.0]),
            "is_heading": c.get("is_heading", False)
        })
    return [page_dict[p] for p in sorted(page_dict.keys())]


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


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    summary="List all available ingested documents",
    tags=["Ingestion"]
)
async def list_documents() -> DocumentListResponse:
    """Returns list of all available ingested documents with basic metadata for selection."""
    docs = []
    for doc_id, doc in document_exports.items():
        pages_count = max((c.get("page", 1) for c in doc.get("chunks", [])), default=1)
        docs.append(DocumentSummaryItem(
            document_id=doc_id,
            filename=doc.get("filename", "document.pdf"),
            title=doc.get("title", "Untitled Document"),
            pages_count=pages_count,
            chunks_count=len(doc.get("chunks", [])),
            indexing_confirmed=vector_store.has_document(doc_id)
        ))
    return DocumentListResponse(status="success", documents=docs)


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
    summary="Ingest PDF or modern PPTX course material and index vectors",
    tags=["Ingestion"],
    responses={
        400: {"model": ErrorResponse, "description": "File format invalid or empty file"},
        422: {"model": ErrorResponse, "description": "No readable text extracted"},
        500: {"model": ErrorResponse, "description": "Ingestion processing error"}
    }
)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    """Ingests PDF or PPTX course material, extracts text, and indexes into vector memory."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix == ".pdf":
        parser = pdf_parser_engine
        parser_name = "PDF"
    elif suffix == ".pptx":
        if not pptx_parser_engine.available:
            raise HTTPException(status_code=400, detail="python-pptx is required to parse .pptx files.")
        parser = pptx_parser_engine
        parser_name = "PPTX"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Educator uploads currently support PDF documents only (or modern PowerPoint .pptx files).")

    temp_path = ""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail=f"The uploaded {parser_name} file is empty.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        if suffix == ".pdf":
            chunks = pdf_parser_engine.parse_pdf(temp_path)
        else:
            chunks = pptx_parser_engine.parse_pptx(temp_path)

        if not chunks:
            raise HTTPException(status_code=422, detail="No readable text could be extracted from this document.")

        raw_filename = file.filename or ("Uploaded_Document.pdf" if suffix == ".pdf" else "Uploaded_Document.pptx")
        document_id = f"doc_{uuid.uuid4().hex}"
        for chunk in chunks:
            chunk["document_id"] = document_id
            chunk["document_name"] = raw_filename

        vector_store.add_chunks(chunks)

        if not vector_store.has_document(document_id):
            raise HTTPException(status_code=500, detail="Vector store indexing verification failed.")

        raw_title = Path(raw_filename).stem.replace("_", " ").strip() or "Uploaded curriculum material"
        analysis = document_analyzer.analyze_document(chunks, raw_title=raw_title, filename=raw_filename)
        title = analysis.get("title") or raw_title
        pages_reconstructed = _reconstruct_pages(chunks)

        document_exports[document_id] = {
            "document_id": document_id,
            "title": title,
            "chunks": chunks,
            "filename": raw_filename,
            "summary": analysis.get("summary"),
            "sections": analysis.get("sections", []),
            "important_concepts": analysis.get("important_concepts", []),
            "important_portions": analysis.get("important_portions", []),
            "slides": analysis.get("slides", []),
            "pages": pages_reconstructed,
            "pdf_bytes": content,
        }

        pages_processed = analysis.get("page_count") or max((c.get("page", 0) for c in chunks), default=1)

        return IngestResponse(
            status="success",
            document_id=document_id,
            title=title,
            filename=raw_filename,
            chunks_extracted=len(chunks),
            pages_processed=pages_processed,
            message="Document successfully parsed, analyzed, and indexed into vector repository with coordinate metadata.",
            indexing_confirmed=True,
            summary=analysis.get("summary"),
            important_concepts=analysis.get("important_concepts", []),
            sections=analysis.get("sections", []),
            important_portions=analysis.get("important_portions", []),
            slides=analysis.get("slides", []),
            pages=pages_reconstructed
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Ingestion failure: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get(
    "/document/{document_id}",
    summary="Retrieve ingested document metadata, analysis, and slide outline",
    tags=["Ingestion"],
    responses={
        404: {"model": ErrorResponse, "description": "Document not found."}
    }
)
async def get_document(document_id: str):
    """Returns stored document analysis, sections, summary, and slide outline."""
    document = _get_export_document(document_id)
    return {
        "status": "success",
        "document_id": document["document_id"],
        "title": document["title"],
        "filename": document["filename"],
        "chunks_count": len(document.get("chunks", [])),
        "pages_count": max((c.get("page", 1) for c in document.get("chunks", [])), default=1),
        "summary": document.get("summary"),
        "sections": document.get("sections", []),
        "important_concepts": document.get("important_concepts", []),
        "important_portions": document.get("important_portions", []),
        "slides": document.get("slides", []),
        "pages": document.get("pages") or _reconstruct_pages(document.get("chunks", [])),
        "indexing_confirmed": vector_store.has_document(document_id),
    }


@router.get(
    "/document/{document_id}/pdf",
    summary="Retrieve ingested PDF document as binary stream for preview",
    tags=["Ingestion"],
    responses={
        200: {"content": {"application/pdf": {}}, "description": "Binary PDF stream"},
        404: {"model": ErrorResponse, "description": "Document or PDF binary not found."}
    }
)
async def get_document_pdf(document_id: str):
    """Streams original uploaded PDF bytes for in-browser rendering."""
    document = _get_export_document(document_id)
    pdf_bytes = document.get("pdf_bytes")
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="PDF binary data not found for this document.")
    filename = document.get("filename", "document.pdf")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )


@router.post(
    "/demo/load",
    response_model=IngestResponse,
    summary="Load isolated BST demo curriculum data for demonstration purposes",
    tags=["Demo"]
)
async def load_demo_data() -> IngestResponse:
    """Loads isolated Binary Search Tree demo knowledge, slides, and diagnostics on demand."""
    from app.demo.demo_data import (
        DEMO_DOCUMENT_ID,
        DEMO_FILENAME,
        DEMO_TITLE,
        DEMO_CHUNKS,
        DEMO_SLIDES,
    )
    # 1. Seed into vector store
    if not vector_store.has_document(DEMO_DOCUMENT_ID):
        vector_store.add_chunks(DEMO_CHUNKS)

    # 2. Activate demo diagnostics
    learner_engine.activate_demo_mode()

    # 3. Prepare demo document record
    pages_reconstructed = _reconstruct_pages(DEMO_CHUNKS)
    demo_doc_record = {
        "document_id": DEMO_DOCUMENT_ID,
        "title": DEMO_TITLE,
        "chunks": DEMO_CHUNKS,
        "filename": DEMO_FILENAME,
        "summary": "Comprehensive B.Tech curriculum chapter covering Binary Search Tree properties, invariant preservation, insertion, 3-case deletion, and asymptotic complexity analysis.",
        "sections": ["BST Definition & Properties", "BST Insertion Algorithm", "BST Deletion (3 Cases)", "Time & Space Complexity"],
        "important_concepts": ["BST Invariant", "In-Order Successor", "Deletion Cases", "Time Complexity"],
        "important_portions": [
            {
                "page": 3,
                "lead_sentence": "BST Deletion Algorithm has 3 cases: Case 1 (Leaf Node): Remove directly.",
                "snippet": "Case 3 (Two Children): Replace node value with its in-order successor (smallest node in right subtree) and recursively delete successor.",
                "is_critical": True
            }
        ],
        "slides": DEMO_SLIDES,
        "pages": pages_reconstructed,
    }

    if pdf_generator.available:
        try:
            demo_doc_record["pdf_bytes"] = pdf_generator.generate_handout_pdf(demo_doc_record)
        except Exception:
            pass

    document_exports[DEMO_DOCUMENT_ID] = demo_doc_record

    return IngestResponse(
        status="success",
        document_id=DEMO_DOCUMENT_ID,
        title=DEMO_TITLE,
        filename=DEMO_FILENAME,
        chunks_extracted=len(DEMO_CHUNKS),
        pages_processed=4,
        message="Demo BST curriculum dataset loaded successfully.",
        indexing_confirmed=True,
        summary=demo_doc_record["summary"],
        important_concepts=demo_doc_record["important_concepts"],
        sections=demo_doc_record["sections"],
        important_portions=demo_doc_record["important_portions"],
        slides=DEMO_SLIDES,
        pages=pages_reconstructed
    )


@router.get(
    "/quiz",
    response_model=QuizQuestionResponse,
    summary="Fetch active diagnostic micro-quiz question",
    tags=["Diagnostics"]
)
async def get_diagnostic_quiz(document_id: Optional[str] = Query(None)) -> QuizQuestionResponse:
    """Fetches diagnostic micro-quiz question dynamically scoped to the target document."""
    from app.demo.demo_data import DEMO_DOCUMENT_ID, DEMO_QUIZ

    # If scoped to an uploaded document
    if document_id and document_id in document_exports and document_id != DEMO_DOCUMENT_ID:
        doc = document_exports[document_id]
        concepts = doc.get("important_concepts") or []
        sections = doc.get("sections") or []
        title = doc.get("title", "Active Document")
        topic_name = concepts[0] if concepts else (sections[0] if sections else title)

        return QuizQuestionResponse(
            question_id=f"q_{document_id[:8]}_01",
            topic=topic_name,
            question_text=f"Which principle is central to understanding and analyzing {topic_name}?",
            options=[
                f"Preserving the core invariant and operational constraints of {topic_name}",
                f"Arbitrary manipulation without verifying underlying {topic_name} state",
                f"Bypassing deterministic execution rules in {topic_name}",
                f"Ignoring boundary conditions and asymptotic complexity"
            ],
            is_empty=False
        )

    # If demo document is explicitly requested or demo mode is active
    if document_id == DEMO_DOCUMENT_ID or (not document_id and getattr(learner_engine, "is_demo_mode", False)):
        return QuizQuestionResponse(
            question_id=DEMO_QUIZ["question_id"],
            topic=DEMO_QUIZ["topic"],
            question_text=DEMO_QUIZ["question_text"],
            options=DEMO_QUIZ["options"],
            is_empty=False
        )

    # If document_id was not provided, check if demo document is registered or return default BST quiz for test compatibility
    if not document_id:
        return QuizQuestionResponse(
            question_id=DEMO_QUIZ["question_id"],
            topic=DEMO_QUIZ["topic"],
            question_text=DEMO_QUIZ["question_text"],
            options=DEMO_QUIZ["options"],
            is_empty=False
        )

    raise HTTPException(status_code=404, detail="Document not found for quiz generation.")


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
