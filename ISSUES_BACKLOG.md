# 📋 SIH 2026 Team Task & GitHub Issues Backlog
### Team: Tech_Warriors | Project: StudyCopilot & StudyForge Integration

This backlog provides 12 ready-to-copy GitHub issues formatted for immediate assignment across our **6-Member SIH Team Roles**. Each issue specifies the primary file target, requirement checklist, and technical acceptance criteria.

---

## 👥 Team Role Assignment Matrix

| Role | Role Title | Primary Scope | Assigned Backlog Issues |
|---|---|---|---|
| **Role 0 (You)** | RAG & Integration Lead | Core RAG pipeline, marks-aware prompts, evidence-or-abstain gate | #1, #2 |
| **Teammate 1** | Document Intelligence | PyMuPDF parsing, bounding box coordinates, layout cleaning | #3, #4 |
| **Teammate 2** | Lead Backend Architect | FastAPI REST routing, SQLite learner state, async endpoints | #5, #6 |
| **Teammate 3** | Student Portal Dev | React split-screen chat console, PDF highlight overlay | #7, #8 |
| **Teammate 4** | Educator Console Dev | Teacher presentation hub, class weakness heatmap | #9, #10 |
| **Teammate 5** | Output & QA Engineer | `python-pptx` deck builder, `ReportLab` handouts, stress tests | #11, #12 |

---

## 📌 Ready-to-Copy GitHub Issues

### 🔹 Issue #1: Implement Marks-Aware LangChain/LLM Prompt Router
- **Labels**: `role:rag-lead`, `backend`, `high-priority`
- **Target File**: `backend/app/rag/qa_engine.py`
- **Description**:  
  Build the prompt template matrix in `qa_engine.py` that formats output based on marks requested (2, 5, or 10 marks).
- **Acceptance Criteria**:
  - [ ] **2-Mark**: 1-2 sentence definition + 1 concise example (<50 words).
  - [ ] **5-Mark**: Paragraph definition, 3-4 bullet points, code/process example.
  - [ ] **10-Mark**: Abstract definition, advantages, detailed algorithm, step-by-step math proof/diagram text, evaluative conclusion.
  - [ ] Returns response with citation metadata (page number and bounding box coordinates).

---

### 🔹 Issue #2: Build Evidence-or-Abstain Gate for Hallucination Prevention
- **Labels**: `role:rag-lead`, `security`, `rag`
- **Target File**: `backend/app/rag/qa_engine.py`
- **Description**:  
  Implement a strict evidence verification gate that calculates similarity score between top retrieved chunks and user question.
- **Acceptance Criteria**:
  - [ ] If top cosine similarity < 0.72 or context lacks direct evidence, return abstain object.
  - [ ] Abstain text must strictly match: `"The requested query is not supported by verified textbook evidence."`
  - [ ] Include unit test simulating off-topic questions (e.g., cooking/pop-culture).

---

### 🔹 Issue #3: PyMuPDF Layout Coordinate & Bounding Box Extractor
- **Labels**: `role:doc-intel`, `ingestion`, `pdf`
- **Target File**: `backend/app/ingestion/pdf_parser.py`
- **Description**:  
  Extract page text along with character string offsets and pixel bounding boxes `[x0, y0, x1, y1]` during PDF ingestion.
- **Acceptance Criteria**:
  - [ ] Extract structured text per page with bounding box array for each paragraph/chunk.
  - [ ] Clean multi-column layout artifacts and preserve section headings.
  - [ ] Return JSON payload containing page text, page index, and normalized coordinates `[x0, y0, x1, y1]`.

---

### 🔹 Issue #4: OCR Fallback Engine for Scanned Textbooks
- **Labels**: `role:doc-intel`, `ocr`, `ingestion`
- **Target File**: `backend/app/ingestion/pdf_parser.py`
- **Description**:  
  Add automatic detection for non-selectable digital PDFs or low-resolution scans to invoke localized OCR parsing.
- **Acceptance Criteria**:
  - [ ] Check if page contains selectable text layer; if missing, trigger OCR pipeline.
  - [ ] Extract recognized text blocks with estimated bounding boxes.
  - [ ] Gracefully handle table/grid structures without raising server exceptions.

---

### 🔹 Issue #5: FastAPI REST Gateway Setup & CORS Config
- **Labels**: `role:backend`, `fastapi`, `api`
- **Target File**: `backend/app/main.py`, `backend/app/api/routes.py`
- **Description**:  
  Set up FastAPI boilerplate with CORS middleware, asynchronous router mounting, and health check endpoints.
- **Acceptance Criteria**:
  - [ ] FastAPI instance initialized with middleware allowing `http://localhost:5173`.
  - [ ] Define endpoints for `/api/ingest`, `/api/query`, `/api/quiz`, `/api/diagnose`, `/api/export/ppt`, `/api/export/pdf`.
  - [ ] Provide Pydantic schemas for request and response validation.

---

### 🔹 Issue #6: Learner State Storage & Error Taxonomy Classifier
- **Labels**: `role:backend`, `diagnostics`, `database`
- **Target File**: `backend/app/diagnostics/learner_state.py`
- **Description**:  
  Program the Learner-State model (`topic_id` → `readiness_score` → `confidence_level` → `recent_mistakes`) and rule-based Error Taxonomy classifier.
- **Acceptance Criteria**:
  - [ ] Classify quiz errors into: `conceptual_gap`, `process_mistake`, `terminology_confusion`, `careless_error`.
  - [ ] Automatically trigger a **30-Minute Rescue Mission** with targeted real-world analogy when `conceptual_gap` occurs.
  - [ ] Maintain updated topic readiness scores (0-100%).

---

### 🔹 Issue #7: React Split-Screen Student Workspace Component
- **Labels**: `role:student-ui`, `frontend`, `react`
- **Target File**: `frontend/src/components/student/StudentPortal.jsx`
- **Description**:  
  Build responsive split-screen student view featuring interactive chat panel on the left and PDF viewer on the right.
- **Acceptance Criteria**:
  - [ ] Resizable/toggleable split layout.
  - [ ] Chat panel with message history, citation badges, and Marks Selector (2, 5, 10 marks).
  - [ ] Clicking a citation badge scrolls PDF viewer to exact page and triggers coordinate highlight.

---

### 🔹 Issue #8: Real-Time Canvas/SVG Bounding Box PDF Highlight Overlay
- **Labels**: `role:student-ui`, `frontend`, `canvas`
- **Target File**: `frontend/src/components/student/PdfViewer.jsx`
- **Description**:  
  Draw a vibrant orange highlight bounding box overlay over the original PDF page based on citation coordinates.
- **Acceptance Criteria**:
  - [ ] Render PDF page image/canvas cleanly.
  - [ ] Dynamically scale normalized `[x0, y0, x1, y1]` coordinates to match current viewer zoom level.
  - [ ] Display animated pulse highlight effect when user clicks a citation reference link.

---

### 🔹 Issue #9: Educator Slide Generator Interface & Control Hub
- **Labels**: `role:educator-ui`, `frontend`, `react`
- **Target File**: `frontend/src/components/educator/EducatorConsole.jsx`
- **Description**:  
  Build teacher console with textbook upload zone, slide outline editor, and one-click export buttons.
- **Acceptance Criteria**:
  - [ ] Drag-and-drop syllabus/textbook document uploader.
  - [ ] Live preview of extracted slide topics and speaker notes.
  - [ ] Direct download triggers for `.pptx` and `.pdf` files.

---

### 🔹 Issue #10: Class Weakness Heatmap & Concept Mastery Widget
- **Labels**: `role:educator-ui`, `frontend`, `analytics`
- **Target File**: `frontend/src/components/educator/WeaknessHeatmap.jsx`
- **Description**:  
  Visualize class-wide conceptual gaps and misconception patterns using a color-coded heatmap grid.
- **Acceptance Criteria**:
  - [ ] Grid displaying topic readiness (Red = High Error Rate, Green = Mastered).
  - [ ] Hover tooltips showing top error categories (e.g., Conceptual Gap in BST Deletion).
  - [ ] Filter by mistake taxonomy type.

---

### 🔹 Issue #11: python-pptx Automated Presentation Builder
- **Labels**: `role:qa-export`, `python-pptx`, `export`
- **Target File**: `backend/app/generators/ppt_generator.py`
- **Description**:  
  Write python script using `python-pptx` to compile extracted textbook outlines into structured slides with speaker notes.
- **Acceptance Criteria**:
  - [ ] Generate 5-10 slide deck containing Title Slide, Overview, Concept Breakdown, Code/Diagram slide, and Summary.
  - [ ] Include detailed teacher speaker notes in slide metadata.
  - [ ] Save output as editable `.pptx` binary stream for HTTP download response.

---

### 🔹 Issue #12: ReportLab Printable Double-Column Handout Exporter
- **Labels**: `role:qa-export`, `reportlab`, `export`
- **Target File**: `backend/app/generators/pdf_generator.py`
- **Description**:  
  Build ReportLab PDF compiler to produce print-ready 2-column B.Tech study guides and revision sheets.
- **Acceptance Criteria**:
  - [ ] Formatted double-column academic layout with header, course metadata, key definitions, and practice questions (2/5/10 marks).
  - [ ] Generates clean printable PDF without text clipping or overlapping elements.
  - [ ] Stress-tested against multi-page outputs.
