# 👥 Team Roles & API Contract Specifications
### Team Tech_Warriors | SIH 2026 Prototype Development

This document defines the 6 team member role responsibilities, shared code contracts, and integration boundaries based on **Section 5 of the SIH Winner's Playbook**.

---

## 1. Team Role Allocation

```
                        ┌───────────────────────────────────────────────┐
                        │        You (RAG & Integration Lead)           │
                        │ Architecture Contracts, RAG, Prompts, Gating │
                        └───────────────────────┬───────────────────────┘
                                                │
       ┌────────────────────────┬───────────────┴───────────────┬────────────────────────┐
       ▼                        ▼                               ▼                        ▼
 ┌───────────┐            ┌───────────┐                   ┌───────────┐            ┌───────────┐
 │Teammate 1 │            │Teammate 2 │                   │Teammate 3 │            │Teammate 4 │
 │ Doc Intel │            │  Backend  │                   │ Student UI│            │Educator UI│
 └─────┬─────┘            └─────┬─────┘                   └─────┬─────┘            └─────┬─────┘
       │                        │                               │                        │
       └────────────────────────┴───────────────┬───────────────┴────────────────────────┘
                                                ▼
                                         ┌───────────┐
                                         │Teammate 5 │
                                         │  QA & PPT │
                                         └───────────┘
```

### Role 0: RAG & Integration Lead (You)
- **Primary Deliverables**: Prompt templates for 2, 5, 10 marks, Chroma vector DB schema, evidence-or-abstain gate, end-to-end RAG workflow.
- **Code Scope**: `backend/app/rag/qa_engine.py`, `backend/app/rag/vector_store.py`.

### Role 1: Document Intelligence Specialist (Teammate 1)
- **Primary Deliverables**: PyMuPDF coordinate & bounding box extractor, text layout cleaner, OCR fallback.
- **Code Scope**: `backend/app/ingestion/pdf_parser.py`.

### Role 2: Lead Systems Backend Architect (Teammate 2)
- **Primary Deliverables**: FastAPI async routes, SQLite learner state DB schema, error taxonomy classifier.
- **Code Scope**: `backend/app/main.py`, `backend/app/api/routes.py`, `backend/app/diagnostics/learner_state.py`.

### Role 3: Student Portal Developer (Teammate 3)
- **Primary Deliverables**: React split-screen chat interface, marks selector UI, dynamic SVG/Canvas PDF bounding box highlight renderer.
- **Code Scope**: `frontend/src/components/student/*`.

### Role 4: Educator Console Developer (Teammate 4)
- **Primary Deliverables**: Teacher upload panel, PPT generator controller UI, class weakness heatmap widgets.
- **Code Scope**: `frontend/src/components/educator/*`.

### Role 5: Output & QA Engineer (Teammate 5)
- **Primary Deliverables**: `python-pptx` presentation builder, `ReportLab` study handout PDF exporter, stress testing scripts.
- **Code Scope**: `backend/app/generators/*`, `backend/tests/*`.

---

## 2. Shared API Data Contracts

### A. RAG Query Contract (`POST /api/query`)
**Request Body:**
```json
{
  "question": "Explain Binary Search Tree deletion algorithm",
  "marks": 10,
  "document_id": "doc_bst_chapter_01"
}
```

**Response Body (Grounded Success):**
```json
{
  "status": "success",
  "question": "Explain Binary Search Tree deletion algorithm",
  "marks": 10,
  "answer": "### Definition\nBinary Search Tree (BST) deletion involves removing a node...",
  "confidence_score": 0.94,
  "abstain": false,
  "citation": {
    "document_name": "sample_bst_chapter.pdf",
    "page_number": 3,
    "snippet": "When deleting a node with two children, replace it with its in-order successor...",
    "bounding_box": [100, 240, 520, 380]
  }
}
```

**Response Body (Abstain Triggered):**
```json
{
  "status": "abstain",
  "question": "How to bake a chocolate cake?",
  "marks": 2,
  "answer": "The requested query is not supported by verified textbook evidence.",
  "confidence_score": 0.12,
  "abstain": true,
  "citation": null
}
```

### B. Diagnostic Quiz Submission (`POST /api/diagnose`)
**Request Body:**
```json
{
  "question_id": "q_bst_del_01",
  "selected_option": 2,
  "correct_option": 0,
  "topic_id": "bst_deletion"
}
```

**Response Body:**
```json
{
  "status": "diagnosed",
  "error_category": "conceptual_gap",
  "error_title": "Conceptual Gap: In-Order Successor Substitution",
  "explanation": "You confused node deletion with simple leaf removal.",
  "rescue_mission_triggered": true,
  "rescue_mission": {
    "title": "30-Minute Rescue Mission: BST Node Swapping Analogy",
    "analogy": "Think of deleting a node with two children like replacing a manager in a company hierarchy: you replace them with the next lowest employee who is still qualified (the in-order successor).",
    "prerequisite_retest_question": "Which node replaces a deleted node with two children?"
  }
}
```
