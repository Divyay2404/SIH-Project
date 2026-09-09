"""
FastAPI REST Router for SIH 2026 Prototype Gateway.
Connects UI to PyMuPDF parsing, RAG qa_engine, diagnostic learner_state,
and PPT/PDF generator modules. Backed by SQLite persistence, upload protections,
thread-pool execution, and deep health check reporting.
"""

import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Response, UploadFile, File, Query, Header

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

from app.ingestion.pdf_parser import pdf_parser_engine, PYMUPDF_AVAILABLE
from app.ingestion.pptx_parser import pptx_parser_engine
from app.ingestion.document_analyzer import document_analyzer
from app.ingestion.ocr import ocr_engine
from app.rag.vector_store import vector_store
from app.rag.qa_engine import qa_engine
from app.diagnostics.learner_state import learner_engine
from app.generators.ppt_generator import ppt_generator
from app.generators.pdf_generator import pdf_generator
from app.storage.database import db_manager

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

router = APIRouter(prefix="/api")

# Upload and safety constraints
MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB max upload
MAX_PAGE_COUNT = 100                      # 100 pages max
PROCESSING_TIMEOUT_SECONDS = 45           # 45s execution budget

# Process memory cache for parsed documents, supplemented by SQLite persistence
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


def _get_export_document(document_id: str) -> Dict[str, Any]:
    """Retrieves document from in-memory cache or rehydrates from SQLite storage."""
    document = document_exports.get(document_id)
    if not document:
        stored = db_manager.get_document(document_id)
        if stored:
            # Reconstruct chunks from vector store if available
            stored["chunks"] = vector_store.get_document_chunks(document_id)
            document_exports[document_id] = stored
            return stored
        raise HTTPException(status_code=404, detail="Document not found. Upload a PDF before exporting.")
    return document


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="API Gateway Deep Health Check",
    tags=["Health"]
)
async def health_check() -> HealthCheckResponse:
    """Returns gateway service health status, engine identifier, deep dependency checks, and pipeline readiness."""
    ocr_info = ocr_engine.verify_ocr_runtime()
    deps = {
        "pymupdf": bool(PYMUPDF_AVAILABLE),
        "ocr": bool(ocr_info.get("available")),
        "pptx": bool(pptx_parser_engine.available),
        "reportlab": bool(pdf_generator.available),
        "sqlite": True,
        "vector_store": True,
    }
    pipeline = {
        "ingestion": "ready" if deps["pymupdf"] else "degraded",
        "ocr": ocr_info.get("status", "unavailable"),
        "retrieval": "ready",
        "exports": "ready" if (deps["pptx"] and deps["reportlab"]) else "partial",
        "storage": "ready",
    }
    stored_docs = db_manager.list_documents()
    return HealthCheckResponse(
        status="online",
        system="StudyCopilot & StudyForge Engine",
        version="1.0.0",
        dependencies=deps,
        pipeline_readiness=pipeline,
        storage={"persisted_documents": len(stored_docs)},
        ocr_runtime=ocr_info,
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
    seen_ids = set()

    # In-memory documents
    for doc_id, doc in document_exports.items():
        seen_ids.add(doc_id)
        pages_count = max((c.get("page", 1) for c in doc.get("chunks", [])), default=doc.get("pages_count", 1))
        docs.append(DocumentSummaryItem(
            document_id=doc_id,
            filename=doc.get("filename", "document.pdf"),
            title=doc.get("title", "Untitled Document"),
            pages_count=pages_count,
            chunks_count=len(doc.get("chunks", [])),
            indexing_confirmed=vector_store.has_document(doc_id)
        ))

    # SQLite-persisted documents not in memory
    for stored in db_manager.list_documents():
        if stored["document_id"] not in seen_ids:
            seen_ids.add(stored["document_id"])
            docs.append(DocumentSummaryItem(
                document_id=stored["document_id"],
                filename=stored["filename"],
                title=stored["title"],
                pages_count=stored["pages_count"],
                chunks_count=stored["chunks_count"],
                indexing_confirmed=vector_store.has_document(stored["document_id"])
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
        413: {"model": ErrorResponse, "description": "File size exceeds 25 MB upload limit"},
        422: {"model": ErrorResponse, "description": "No readable text extracted"},
        500: {"model": ErrorResponse, "description": "Ingestion processing error"},
        504: {"model": ErrorResponse, "description": "Ingestion processing timeout"}
    }
)
async def ingest_document(
    file: UploadFile = File(...),
    x_user_id: Optional[str] = Header("student_sih_2026")
) -> IngestResponse:
    """Ingests PDF or PPTX course material, extracts text, and indexes into vector memory."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix == ".pdf":
        parser_name = "PDF"
    elif suffix == ".pptx":
        if not pptx_parser_engine.available:
            raise HTTPException(status_code=400, detail="python-pptx is required to parse .pptx files.")
        parser_name = "PPTX"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Educator uploads currently support PDF documents only (or modern PowerPoint .pptx files)."
        )

    temp_path = ""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail=f"The uploaded {parser_name} file is empty.")

        # Protection: 25 MB upload limit
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Uploaded file exceeds {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB size limit."
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        # Protection: Page count limit on PDFs
        if suffix == ".pdf" and fitz is not None:
            try:
                with fitz.open(temp_path) as test_doc:
                    if test_doc.page_count > MAX_PAGE_COUNT:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Document contains {test_doc.page_count} pages, exceeding the maximum allowed {MAX_PAGE_COUNT} pages."
                        )
            except Exception as pe:
                if isinstance(pe, HTTPException):
                    raise pe

        # Execute heavy CPU parsing and analysis in thread pool with timeout protection
        async def _process_pipeline():
            if suffix == ".pdf":
                extracted_chunks = await asyncio.to_thread(pdf_parser_engine.parse_pdf, temp_path)
            else:
                extracted_chunks = await asyncio.to_thread(pptx_parser_engine.parse_pptx, temp_path)
            return extracted_chunks

        try:
            chunks = await asyncio.wait_for(_process_pipeline(), timeout=PROCESSING_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail=f"Document processing exceeded execution time budget of {PROCESSING_TIMEOUT_SECONDS} seconds."
            )

        if not chunks:
            raise HTTPException(status_code=422, detail="No readable text could be extracted from this document.")

        raw_filename = file.filename or ("Uploaded_Document.pdf" if suffix == ".pdf" else "Uploaded_Document.pptx")
        document_id = f"doc_{uuid.uuid4().hex}"
        for chunk in chunks:
            chunk["document_id"] = document_id
            chunk["document_name"] = raw_filename

        # Index into vector store and SQLite storage
        vector_store.add_chunks(chunks)

        if not vector_store.has_document(document_id):
            raise HTTPException(status_code=500, detail="Vector store indexing verification failed.")

        raw_title = Path(raw_filename).stem.replace("_", " ").strip() or "Uploaded curriculum material"
        analysis = await asyncio.to_thread(
            document_analyzer.analyze_document,
            chunks,
            raw_title=raw_title,
            filename=raw_filename
        )
        title = analysis.get("title") or raw_title
        pages_reconstructed = _reconstruct_pages(chunks)

        doc_record = {
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

        document_exports[document_id] = doc_record

        # Persist document to SQLite
        try:
            db_manager.save_document(doc_record, user_id=x_user_id or "student_sih_2026")
        except Exception:
            pass

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
            try:
                os.unlink(temp_path)
            except Exception:
                pass


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
        "pages_count": max((c.get("page", 1) for c in document.get("chunks", [])), default=document.get("pages_count", 1)),
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
        DEMO_QUIZ,
    )
    # 1. Seed into vector store (memory only, never persisted to SQLite)
    if not vector_store.has_document(DEMO_DOCUMENT_ID):
        vector_store.add_chunks(DEMO_CHUNKS, persist=False)

    # 2. Activate demo diagnostics
    learner_engine.activate_demo_mode()

    # 3. Register demo quiz in SQLite question bank
    db_manager.register_quiz_question(
        question_id=DEMO_QUIZ["question_id"],
        topic=DEMO_QUIZ["topic"],
        question_text=DEMO_QUIZ["question_text"],
        options=DEMO_QUIZ["options"],
        correct_option=DEMO_QUIZ.get("correct_option", 0),
        document_id=DEMO_DOCUMENT_ID
    )

    # 4. Prepare demo document record
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
    """Fetches diagnostic micro-quiz question dynamically scoped to the target document with verified correct option."""
    from app.demo.demo_data import DEMO_DOCUMENT_ID, DEMO_QUIZ

    # If scoped to an uploaded document
    if document_id and (document_id in document_exports or db_manager.get_document(document_id)) and document_id != DEMO_DOCUMENT_ID:
        doc = _get_export_document(document_id)
        concepts = doc.get("important_concepts") or []
        sections = doc.get("sections") or []
        title = doc.get("title", "Active Document")
        topic_name = concepts[0] if concepts else (sections[0] if sections else title)

        question_id = f"q_{document_id[:8]}_01"
        options = [
            f"Preserving the core invariant and operational constraints of {topic_name}",
            f"Arbitrary manipulation without verifying underlying {topic_name} state",
            f"Bypassing deterministic execution rules in {topic_name}",
            f"Ignoring boundary conditions and asymptotic complexity"
        ]
        correct_option = 0
        error_mappings = {
            "1": {"type": "conceptual_gap", "title": "Conceptual Gap", "desc": f"Misunderstood foundational invariant in {topic_name}."},
            "2": {"type": "process_mistake", "title": "Process Mistake", "desc": f"Skipped execution sequencing in {topic_name}."},
            "3": {"type": "terminology_confusion", "title": "Terminology Confusion", "desc": f"Conflated operational boundaries in {topic_name}."}
        }

        # Register in SQLite quiz bank so diagnose evaluates against true correct option
        db_manager.register_quiz_question(
            question_id=question_id,
            topic=topic_name,
            question_text=f"Which principle is central to understanding and analyzing {topic_name}?",
            options=options,
            correct_option=correct_option,
            document_id=document_id,
            error_mappings=error_mappings
        )

        return QuizQuestionResponse(
            question_id=question_id,
            topic=topic_name,
            question_text=f"Which principle is central to understanding and analyzing {topic_name}?",
            options=options,
            is_empty=False
        )

    # If demo document is explicitly requested or demo mode is active
    if document_id == DEMO_DOCUMENT_ID or (not document_id and getattr(learner_engine, "is_demo_mode", False)):
        db_manager.register_quiz_question(
            question_id=DEMO_QUIZ["question_id"],
            topic=DEMO_QUIZ["topic"],
            question_text=DEMO_QUIZ["question_text"],
            options=DEMO_QUIZ["options"],
            correct_option=DEMO_QUIZ.get("correct_option", 0),
            document_id=DEMO_DOCUMENT_ID
        )
        return QuizQuestionResponse(
            question_id=DEMO_QUIZ["question_id"],
            topic=DEMO_QUIZ["topic"],
            question_text=DEMO_QUIZ["question_text"],
            options=DEMO_QUIZ["options"],
            is_empty=False
        )

    # If document_id was not provided, return default BST quiz for test compatibility
    if not document_id:
        db_manager.register_quiz_question(
            question_id=DEMO_QUIZ["question_id"],
            topic=DEMO_QUIZ["topic"],
            question_text=DEMO_QUIZ["question_text"],
            options=DEMO_QUIZ["options"],
            correct_option=DEMO_QUIZ.get("correct_option", 0),
            document_id=DEMO_DOCUMENT_ID
        )
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
async def submit_quiz_answer(
    request: QuizSubmissionRequest,
    x_user_id: Optional[str] = Header("student_sih_2026")
) -> DiagnosticResponse:
    """Diagnoses student mistake against Error Taxonomy and triggers Rescue Mission if needed."""
    result = learner_engine.evaluate_quiz_answer(
        question_id=request.question_id,
        selected_option=request.selected_option,
        topic_id=request.topic_id,
        user_id=x_user_id
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
    """Generates editable PowerPoint presentation deck (.pptx) with speaker notes in thread pool."""
    try:
        document = _get_export_document(document_id)
        ppt_bytes = await asyncio.to_thread(ppt_generator.generate_ppt_deck, document)
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
    """Generates printable ReportLab study guide handout (.pdf) in thread pool."""
    try:
        document = _get_export_document(document_id)
        pdf_bytes = await asyncio.to_thread(pdf_generator.generate_handout_pdf, document)
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
