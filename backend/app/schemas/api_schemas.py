"""
Pydantic Schemas for Request & Response Validation.
SIH 2026 StudyCopilot & StudyForge API Gateway.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DictAccessibleBaseModel(BaseModel):
    """Base model that provides dict-like subscripting for backward compatibility with direct function calls."""
    def __getitem__(self, item: str):
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)

    def get(self, item: str, default=None):
        return getattr(self, item, default)

    def __contains__(self, item: str):
        return hasattr(self, item)


# ==========================================
# Health Check Schemas
# ==========================================

class HealthCheckResponse(DictAccessibleBaseModel):
    status: str = Field(..., description="Service status", examples=["online"])
    system: str = Field(..., description="System identifier", examples=["StudyCopilot & StudyForge Engine"])
    version: str = Field(..., description="API Version", examples=["1.0.0"])


class RootHealthResponse(DictAccessibleBaseModel):
    message: str = Field(..., description="Welcome message", examples=["Welcome to SIH 2026 StudyCopilot & StudyForge Core Gateway API"])
    docs_url: str = Field(..., description="OpenAPI documentation URL", examples=["/docs"])
    health_check: str = Field(..., description="Health check endpoint URL", examples=["/api/health"])


# ==========================================
# Ingestion Schemas
# ==========================================

class IngestResponse(DictAccessibleBaseModel):
    status: str = Field(..., description="Ingestion status", examples=["success"])
    document_id: str = Field(..., description="Unique generated document identifier", examples=["doc_abc12345"])
    title: str = Field(..., description="Derived document title", examples=["Operating Systems Scheduling"])
    filename: str = Field(..., description="Original filename", examples=["lecture_notes.pdf"])
    chunks_extracted: int = Field(..., description="Number of text chunks extracted", examples=[12])
    pages_processed: int = Field(..., description="Total pages processed", examples=[3])
    message: str = Field(..., description="Status description message", examples=["Document successfully parsed and indexed into vector repository with coordinate metadata."])
    indexing_confirmed: bool = Field(default=True, description="Whether chunks are confirmed indexed in Vector DB", examples=[True])
    summary: Optional[str] = Field(default=None, description="Document-specific executive summary")
    important_concepts: Optional[List[str]] = Field(default_factory=list, description="Extracted key concepts and topics")
    sections: Optional[List[str]] = Field(default_factory=list, description="Extracted section headings")
    important_portions: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Important excerpts and page references")
    slides: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Structured 10-slide outline for presentation")
    pages: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Reconstructed structured pages with coordinates for PDF viewer")


class DocumentSummaryItem(DictAccessibleBaseModel):
    document_id: str = Field(..., description="Unique generated document identifier", examples=["doc_abc12345"])
    filename: str = Field(..., description="Original filename", examples=["lecture_notes.pdf"])
    title: str = Field(..., description="Derived or extracted document title", examples=["Operating Systems"])
    pages_count: int = Field(..., description="Total pages in document", examples=[4])
    chunks_count: int = Field(..., description="Number of indexed chunks", examples=[12])
    indexing_confirmed: bool = Field(default=True, description="Whether document is verified indexed in Vector DB", examples=[True])


class DocumentListResponse(DictAccessibleBaseModel):
    status: str = Field(default="success", description="Response status", examples=["success"])
    documents: List[DocumentSummaryItem] = Field(default_factory=list, description="List of available ingested documents")


# ==========================================
# RAG Query Schemas
# ==========================================

class CitationMetadata(DictAccessibleBaseModel):
    document_name: str = Field(..., description="Source textbook document name", examples=["sample_bst_chapter.pdf"])
    page_number: int = Field(..., description="Source page number", examples=[1])
    snippet: str = Field(..., description="Grounded contextual snippet text", examples=["When deleting a BST node with two children..."])
    bounding_box: Optional[List[float]] = Field(
        default=None,
        description="Normalized or pixel bounding box coordinates [x0, y0, x1, y1]",
        examples=[[50.0, 100.0, 500.0, 150.0]]
    )


class RAGQueryRequest(DictAccessibleBaseModel):
    question: str = Field(
        ...,
        description="The student's study query or exam prompt",
        min_length=1,
        examples=["Explain Binary Search Tree deletion algorithm"]
    )
    marks: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Exam marks rubric level: 2 (definition scale), 5 (concept scale), or 10 (algorithm & proof scale)",
        examples=[5]
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Target document scope identifier",
        examples=["doc_abc12345"]
    )


class RAGQueryResponse(DictAccessibleBaseModel):
    status: str = Field(..., description="Response status: 'success' or 'abstain'", examples=["success"])
    question: str = Field(..., description="Original query asked", examples=["Explain BST deletion algorithm"])
    marks: int = Field(..., description="Applied marks rubric scaling", examples=[5])
    answer: str = Field(..., description="Marks-aware generated or retrieved explanation", examples=["**5-MARK ANSWER (Concept Scale)**..."])
    confidence_score: float = Field(..., description="Grounded cosine similarity / confidence score", examples=[0.85])
    abstain: bool = Field(..., description="Whether the evidence-or-abstain gate was triggered", examples=[False])
    citation: Optional[CitationMetadata] = Field(
        default=None,
        description="Textbook grounding citation metadata with bounding box coordinates"
    )


# ==========================================
# Diagnostic Quiz Schemas
# ==========================================

class QuizQuestionResponse(DictAccessibleBaseModel):
    question_id: str = Field(..., description="Unique question identifier", examples=["q_bst_del_01"])
    topic: str = Field(..., description="Topic curriculum area", examples=["Binary Search Tree Deletion"])
    question_text: str = Field(..., description="Question prompt text", examples=["When deleting a BST node with two children, which node is substituted in its place to maintain the BST invariant?"])
    options: List[str] = Field(..., description="Multiple choice options list", examples=[["In-Order Successor", "Pre-Order Traversal Root Node", "Right-most Leaf Node in Left Subtree", "Any random child node"]])


class QuizSubmissionRequest(DictAccessibleBaseModel):
    question_id: str = Field(
        default="q_bst_del_01",
        description="ID of question being answered",
        examples=["q_bst_del_01"]
    )
    selected_option: int = Field(
        ...,
        ge=0,
        description="Zero-indexed option chosen by student",
        examples=[1]
    )
    correct_option: Optional[int] = Field(
        default=None,
        description="Optional expected correct index for client-server cross validation",
        examples=[0]
    )
    topic_id: str = Field(
        default="bst_deletion",
        description="Taxonomy topic identifier",
        examples=["bst_deletion"]
    )


class RescueMissionDetails(DictAccessibleBaseModel):
    title: str = Field(..., description="Rescue Mission headline", examples=["🚨 30-Minute Rescue Mission Triggered"])
    analogy: str = Field(..., description="Targeted real-world conceptual analogy", examples=["💡 30-Minute Rescue Mission Analogy: Imagine replacing a school principal..."])
    action_plan: Optional[str] = Field(
        default=None,
        description="Recommended student remediation steps",
        examples=["Review foundational Binary Tree traversal rules before re-attempting the deletion quiz."]
    )
    prerequisite_retest_question: Optional[str] = Field(
        default=None,
        description="Follow-up check question",
        examples=["Which node replaces a deleted node with two children?"]
    )


class DiagnosticResponse(DictAccessibleBaseModel):
    status: str = Field(..., description="Diagnostic result status ('correct' or 'diagnosed')", examples=["diagnosed"])
    is_correct: bool = Field(..., description="Whether option selected was correct", examples=[False])
    feedback: Optional[str] = Field(default=None, description="Immediate formative feedback", examples=["🎉 Correct! Excellent understanding of BST in-order successor substitution."])
    updated_readiness: Optional[int] = Field(default=None, description="Updated readiness score (0-100)", examples=[77])
    error_category: Optional[str] = Field(
        default=None,
        description="Error taxonomy classification: conceptual_gap, process_mistake, terminology_confusion, careless_error",
        examples=["conceptual_gap"]
    )
    error_title: Optional[str] = Field(default=None, description="Readable error title", examples=["Conceptual Gap: In-Order Successor Substitution"])
    explanation: Optional[str] = Field(default=None, description="Diagnostic analysis of mistake", examples=["You confused node deletion with simple leaf removal."])
    rescue_mission_triggered: Optional[bool] = Field(default=None, description="Whether a 30-Minute Rescue Mission was triggered", examples=[True])
    rescue_mission: Optional[RescueMissionDetails] = Field(default=None, description="Rescue mission content and analogy if triggered")


# ==========================================
# Readiness & Heatmap Schemas
# ==========================================

class TopicHeatmapItem(DictAccessibleBaseModel):
    topic: str = Field(..., description="Topic name", examples=["BST Deletion (Two Children)"])
    mastery: int = Field(..., description="Mastery percentage (0-100)", examples=[42])
    error_type: str = Field(..., description="Dominant error pattern", examples=["Conceptual Gap"])
    status: str = Field(..., description="Mastery status level", examples=["Critical Gap"])


class ReadinessResponse(DictAccessibleBaseModel):
    overall_readiness: int = Field(..., description="Aggregated class readiness score", examples=[72])
    topic_heatmap: List[TopicHeatmapItem] = Field(..., description="Breakdown of topic masteries")
    class_error_distribution: Dict[str, int] = Field(
        ...,
        description="Error distribution across error taxonomy types",
        examples=[{"Conceptual Gap": 45, "Process Mistake": 25, "Terminology Confusion": 20, "Careless Error": 10}]
    )


# ==========================================
# Error Response Schema
# ==========================================

class ErrorResponse(DictAccessibleBaseModel):
    detail: str = Field(..., description="Error message detail", examples=["Document not found. Upload a PDF before exporting."])

