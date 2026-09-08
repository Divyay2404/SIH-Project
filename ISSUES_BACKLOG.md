# 📋 SIH 2026 Team Task & GitHub Issues Backlog
### Team: Tech_Warriors | Project: StudyCopilot & StudyForge Integration

This backlog provides 14 ready-to-copy GitHub issues formatted for immediate assignment across our **6-Member SIH Team Roles**. Each issue specifies the primary file target, requirement checklist, and technical acceptance criteria.

---

## 🛡️ Git Merge Conflict Prevention Guidelines
To prevent **Git merge conflicts** when multiple team members add, update, or resolve backlog issues:
1. **Append-Only Policy**: Always append new issue definitions at the **bottom** of this file under the `Ready-to-Copy GitHub Issues` section.
2. **Sequential & Unique Issue Identifiers**: Every issue MUST use a distinct sequential identifier (`Issue #1`, `Issue #2`, ..., `Issue #13`, `Issue #14`). Never re-use or re-number existing issue numbers.
3. **Isolated Structural Boundaries**: Wrap each issue entry inside self-contained Markdown headers (`### 🔹 Issue #N: ...`) bounded by explicit horizontal rules (`---`). Do not edit preceding issue blocks.
4. **Non-Overlapping Target File Scopes**: Clearly define primary target file boundaries to avoid conflicting edits across team role branches.

---

## 👥 Team Role Assignment Matrix

| Role | Role Title | Primary Scope | Assigned Backlog Issues |
|---|---|---|---|
| **Divyay** | RAG & Integration Lead | Core RAG pipeline, marks-aware prompts, evidence-or-abstain gate | #1, #2, #14 |
| **Yatharth** | Document Intelligence | PyMuPDF parsing, bounding box coordinates, layout cleaning | #3, #4 |
| **Priya** | Lead Backend Architect | FastAPI REST routing, SQLite learner state, async endpoints | #5, #6 |
| **Deepanshu** | Student Portal Dev | React split-screen chat console, PDF highlight overlay | #7, #8 |
| **Ayush** | Educator Console Dev | Teacher presentation hub, class weakness heatmap | #9, #10 |
| **Dev** | Output & QA Engineer | `python-pptx` deck builder, `ReportLab` handouts, stress tests | #11, #12, #13 |

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
  - [x] Extract structured text per page with bounding box array for each paragraph/chunk.
  - [x] Clean multi-column layout artifacts and preserve section headings.
  - [x] Return JSON payload containing page text, page index, and normalized coordinates `[x0, y0, x1, y1]`.

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
  - [x] Resizable/toggleable split layout.
  - [x] Chat panel with message history, citation badges, and Marks Selector (2, 5, 10 marks).
  - [x] Clicking a citation badge scrolls PDF viewer to exact page and triggers coordinate highlight.

---

### 🔹 Issue #8: Real-Time Canvas/SVG Bounding Box PDF Highlight Overlay
- **Labels**: `role:student-ui`, `frontend`, `canvas`
- **Target File**: `frontend/src/components/student/PdfViewer.jsx`
- **Description**:  
  Draw a vibrant orange highlight bounding box overlay over the original PDF page based on citation coordinates.
- **Acceptance Criteria**:
  - [x] Render PDF page image/canvas cleanly.
  - [x] Dynamically scale normalized `[x0, y0, x1, y1]` coordinates to match current viewer zoom level.
  - [x] Display animated pulse highlight effect when user clicks a citation reference link.

---

### 🔹 Issue #9: Educator Slide Generator Interface & Control Hub
- **Labels**: `role:educator-ui`, `frontend`, `react`
- **Target File**: `frontend/src/components/educator/EducatorConsole.jsx`
- **Description**:  
  Build teacher console with textbook upload zone, slide outline editor, and one-click export buttons.
- **Acceptance Criteria**:
  - [x] Drag-and-drop syllabus/textbook document uploader.
  - [x] Live preview of extracted slide topics and speaker notes.
  - [x] Direct download triggers for `.pptx` and `.pdf` files.

---

### 🔹 Issue #10: Class Weakness Heatmap & Concept Mastery Widget
- **Labels**: `role:educator-ui`, `frontend`, `analytics`
- **Target File**: `frontend/src/components/educator/WeaknessHeatmap.jsx`
- **Description**:  
  Visualize class-wide conceptual gaps and misconception patterns using a color-coded heatmap grid.
- **Acceptance Criteria**:
  - [x] Grid displaying topic readiness (Red = High Error Rate, Green = Mastered).
  - [x] Hover tooltips showing top error categories (e.g., Conceptual Gap in BST Deletion).
  - [x] Filter by mistake taxonomy type.

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

---

### 🔹 Issue #13: Fix Educator Console Upload & Presentation/Handout Content Relevance
- **Labels**: `bug`, `role:qa-export`, `role:educator-ui`, `backend`, `high-priority`
- **Target File**: `backend/app/api/routes.py`, `backend/app/generators/ppt_generator.py`, `backend/app/generators/pdf_generator.py`, `frontend/src/components/educator/EducatorConsole.jsx`
- **Description**:  
  When an educator uploads any file (e.g. Operating Systems, Chemistry) in Educator Console and triggers "Generate Lecture Deck" or "Export Study Handout", the downloaded PowerPoint and PDF handouts return static hardcoded placeholder content (Binary Search Trees) rather than content extracted from or relevant to the uploaded document.
- **Acceptance Criteria**:
  - [ ] Refactor `/api/ingest` in `backend/app/api/routes.py` to stream uploaded file content to `pdf_parser_engine` for real text/outline extraction instead of static fallback data.
  - [ ] Update `ppt_generator.py` and `pdf_generator.py` to generate presentation slides and PDF study guides dynamically from extracted document outlines and summaries.
  - [ ] Connect `EducatorConsole.jsx` to bind and send active `document_id` / dynamic topic payload during export API calls.
  - [ ] Ensure exported files (.pptx and .pdf) accurately reflect the title, key concepts, bullet points, and speaker notes of the uploaded document.

---

### 🔹 Issue #14: Fix Student Portal RAG Query Answer Relevance & Context Scope
- **Labels**: `bug`, `role:rag-lead`, `role:student-ui`, `backend`, `high-priority`
- **Target File**: `backend/app/api/routes.py`, `backend/app/rag/qa_engine.py`, `backend/app/rag/vector_store.py`, `frontend/src/components/student/StudentPortal.jsx`
- **Description**:  
  In the Student Portal split-screen chat interface, when a student submits a question regarding their uploaded document, the generated response is not relevant to the query or active document. The backend returns off-topic answers or fallback definitions instead of querying the vector database for matching textbook evidence.
- **Acceptance Criteria**:
  - [x] Enforce strict `document_id` scoping in `vector_store.search(query, document_id)` to query embeddings of the active uploaded document.
  - [x] Update `StudentPortal.jsx` to send the active `document_id` alongside `question` and `marks` in `/api/query` requests.
  - [x] Refactor `qa_engine.py` prompt templates to ground answer generation in retrieved top-k document chunks for 2, 5, and 10 marks responses.
  - [x] If top retrieved chunk similarity is below threshold or context is missing, return the verified evidence abstain message.

---


### 🔹 Issue #15: Fix Generic PDF Upload Pipeline & Production API Connectivity

- **Labels**: `bug`, `role:backend`, `role:student-ui`, `role:educator-ui`, `backend`, `frontend`, `high-priority`
- **Target File**: `backend/app/api/routes.py`, `backend/app/generators/pdf_generator.py`, `frontend/src/components/educator/EducatorConsole.jsx`, `frontend/src/config/api.js`, `frontend/vite.config.js`, `vercel.json`
- **Description**:\
  In the Educator Console, uploading lecture notes or course-material PDFs fails because the frontend expects a JSON response from `/api/ingest`, while the deployed Vercel frontend currently has no reachable production FastAPI backend. Non-JSON gateway responses such as `404 "The page could not be found"` cause a JSON parsing error. The local FastAPI backend also fails to start due to a missing `pdf_generator` export. The upload pipeline must be fixed generically so any valid lecture-notes PDF can be processed and indexed without filename-specific logic.
- **Acceptance Criteria**:
  - [ ] Restore `pdf_generator` compatibility in `backend/app/generators/pdf_generator.py` so FastAPI starts successfully without import errors.
  - [ ] Ensure `/api/ingest` accepts arbitrary valid lecture-notes/course-material PDFs and returns a consistent JSON success response.
  - [ ] Reject empty, invalid, or unreadable PDFs with clear JSON error responses instead of server crashes.
  - [ ] Update `EducatorConsole.jsx` to safely handle JSON and non-JSON responses and prevent `Unexpected token` parsing errors.
  - [ ] Preserve uploaded file size correctly in the upload status UI.
  - [ ] Centralize frontend API routing through `VITE_API_BASE_URL` for local and production environments.
  - [ ] Ensure local `/api/*` requests are correctly proxied to the FastAPI backend.
  - [ ] Prepare production API connectivity so the Vercel frontend can communicate with the deployed FastAPI backend.
  - [ ] Preserve existing OCR fallback, bounding-box extraction, RAG indexing, PPT generation, and handout generation functionality.
  - [ ] Verify selectable, scanned, mixed, multi-page, table, and multi-column PDFs are handled safely.
  - [ ] Add/update automated tests for backend startup, PDF ingestion, error responses, arbitrary filenames, and frontend upload error handling.
  - [ ] All existing and new backend tests pass successfully.
 
  ---

### 🔹 Issue #16: Complete PDF Upload → Document Analysis → Educator Output Pipeline

- **Labels**: `feature`, `role:backend`, `role:educator-ui`, `ingestion`, `rag`, `high-priority`
- **Target File**: `backend/app/api/routes.py`, `backend/app/ingestion/pdf_parser.py`, `backend/app/ingestion/ocr.py`, `backend/app/rag/vector_store.py`, `backend/app/rag/qa_engine.py`, `backend/app/generators/ppt_generator.py`, `backend/app/generators/pdf_generator.py`, `frontend/src/components/educator/EducatorConsole.jsx`, `frontend/src/config/api.js`
- **Description**:\
  Complete the Educator Console PDF workflow so that any uploaded lecture notes, textbook, or course-material PDF is validated, processed using PyMuPDF/OCR, structurally analyzed, indexed in the Vector DB, and used to generate document-specific summaries, important concepts, slide outlines, PPTs, and study handouts. The Educator Console must display the actual uploaded document's content and accurately report processing, backend, and indexing status without relying on hardcoded/demo content.
- **Acceptance Criteria**:
  - [ ] Accept arbitrary lecture notes, textbooks, study material, and course PDFs without filename-specific or subject-specific logic.
  - [ ] Validate uploaded PDFs and gracefully handle empty, invalid, corrupted, and unreadable files.
  - [ ] Return a unique `document_id` and display clear upload/processing status.
  - [ ] Use the existing PyMuPDF parser to extract page text, structured paragraphs/chunks, headings, page indexes, character offsets, bounding boxes, and layout information.
  - [ ] Preserve meaningful multi-column reading order and clean common PDF extraction artifacts.
  - [ ] Use the existing OCR fallback for scanned and mixed selectable/scanned PDFs.
  - [ ] Preserve OCR text blocks and bounding boxes and handle OCR failures without crashing ingestion.
  - [ ] Index extracted chunks in the existing Vector DB using the correct `document_id`.
  - [ ] Prevent chunks from different documents from being mixed.
  - [ ] Confirm Vector DB indexing only after it actually succeeds.
  - [ ] Preserve existing embeddings, retrieval, citations, confidence scores, source highlighting, and bounding-box highlighting.
  - [ ] Make the uploaded document queryable through the existing RAG pipeline using the correct `document_id`.
  - [ ] Generate a document-specific title/name, page count, chunk count, sections/headings, important concepts/topics, important portions, and summary.
  - [ ] Ensure all document analysis is based on the actual uploaded PDF.
  - [ ] Generate a document-specific slide outline with meaningful slide titles, bullet points, important topics, sections, and speaker/teaching notes where supported.
  - [ ] Ensure the existing Slide Outline Editor displays content from the uploaded document.
  - [ ] Generate a document-specific PPT using the existing PPT generator and verify that it is valid and downloadable.
  - [ ] Generate a document-specific study handout using the existing PDF/handout generator and verify that it is valid and downloadable.
  - [ ] Update the Educator Console to display document name/title, processing/indexing status, page count, chunk count, summary, concepts, sections, slide outline, PPT export, and study handout export.
  - [ ] Display processing states: Uploading → Processing PDF → Extracting Text → Analyzing Structure → Indexing in Vector DB → Generating Learning Content → Ready.
  - [ ] Clearly distinguish Backend Connected from Backend Unavailable.
  - [ ] Do not display "Indexed in Vector DB" unless indexing actually succeeds.
  - [ ] Do not silently treat backend failures as successful ingestion.
  - [ ] Handle HTTP 404, 500, 502, 503, 504, network timeout, malformed API responses, and missing `document_id` with clear human-readable errors.
  - [ ] Handle OCR, Vector DB, embedding, parsing, PPT generation, and handout generation failures gracefully.
  - [ ] Prevent frontend JSON parsing errors such as `Unexpected token`.
  - [ ] Identify and remove/replace hardcoded document-specific demo content where actual uploaded-document data is available.
  - [ ] Do not display unrelated ML/BST/AVL or other demo content as if it came from the uploaded PDF.
  - [ ] Clearly label any remaining fallback/demo data.
  - [ ] Do not generate fake student performance statistics from PDF uploads.
  - [ ] Ensure the Weakness Heatmap uses actual student diagnostic/error data and shows an appropriate empty state when no diagnostic data exists.
  - [ ] Preserve existing error taxonomy and mastery/readiness analytics.
  - [ ] Use the existing `VITE_API_BASE_URL` configuration for backend connectivity.
  - [ ] Do not hardcode localhost or production URLs.
  - [ ] Preserve local development support.
  - [ ] Use the returned `document_id` for all subsequent document-specific operations.
  - [ ] Test selectable-text, scanned, mixed, multi-page, multi-column, table, and different-subject PDFs.
  - [ ] Verify filename/title, page/chunk counts, headings, concepts, summary, slide outline, PPT, and handout all correspond to the uploaded PDF.
  - [ ] Verify RAG retrieval uses the correct document and does not retrieve unrelated document content.
  - [ ] Verify backend failures are clearly reported and no false indexing success is shown.
  - [ ] Add/update automated tests for PDF ingestion, OCR fallback, document indexing, document-specific analysis, RAG, API failures, PPT generation, and handout generation.
  - [ ] Run all existing and new backend tests, relevant frontend tests/build, and lint/type checks if configured.
  - [ ] Preserve all existing OCR, RAG, analytics, PPT, handout, and ingestion functionality.

   ---

 
