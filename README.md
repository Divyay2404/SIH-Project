# 🎓 StudyCopilot & StudyForge: Unified Hybrid Adaptive Learning OS
### Smart India Hackathon (SIH) 2026 Prototype Submission | Team Tech_Warriors
**Problem Statement**: AI-Powered Adaptive Learning & Content Generation Platform  
**Theme**: Smart Education | **Category**: Software | **PS ID**: SIH-2026-EDU-001  

---

## 🌟 Executive Overview
This repository contains the production-ready prototype for the **Unified Hybrid Adaptive Learning OS**, synthesizing the document intelligence of **StudyCopilot** with the readiness-first diagnostic mission engine of **StudyForge**.

Built specifically for the SIH 2026 evaluation round, this solution addresses the core educational challenge: converting static, unstructured curriculum materials (textbooks, scanned notes, B.Tech syllabi) into interactive, grounded learning instruments for students and automated preparation tools for educators.

---

## 🚀 Key Technical Differentiators & Features

1. **Structure-Aware Ingestion & PDF Highlight Offsets**
   - Extracts page-level coordinates (bounding boxes `[x0, y0, x1, y1]`) alongside text chunks using PyMuPDF.
   - Integrates a responsive split-screen PDF viewer in React with real-time orange bounding-box highlight overlays when citations are clicked.

2. **Marks-Aware Answer Scaling (2, 5, 10 Marks)**
   - **2-Mark Schema (Definition Scale)**: Precise 1-2 sentence definition + 1 core example (<50 words).
   - **5-Mark Schema (Concept Scale)**: Structured paragraph, 3-4 bulleted core principles, and code/process examples.
   - **10-Mark Schema (Comprehensive Scale)**: Full academic structure with abstract definitions, algorithms, step-by-step proofs, structural block diagrams, and evaluation conclusions.

3. **Strict Grounding & Abstention Gate**
   - Zero-hallucination evidence gate.
   - Rejects off-topic queries with: *"The requested query is not supported by verified textbook evidence"* when retrieval similarity falls below threshold.

4. **Synthesized Learning Twin & Error Taxonomy**
   - Learner State Tracker (`topic_id` → `readiness_score` → `confidence_level` → `recent_mistakes`).
   - Classifies quiz mistakes into **Conceptual Gap**, **Process/Calculation Mistake**, **Terminology Confusion**, or **Careless Error**.
   - Conceptual gaps trigger an immediate **30-Minute Rescue Mission** with real-world analogies before re-testing.

5. **Unified Facilitator Decks & Handout Generators**
   - **Editable PowerPoint Generator**: Generates clean `.pptx` slides with speaker notes using `python-pptx`.
   - **Printable Study Guide Compiler**: Generates double-column B.Tech study guides & handouts using `ReportLab`.

---

## 📁 Repository Layout

```
SIH-Project/
├── README.md                 # Prototype documentation & script
├── ISSUES_BACKLOG.md         # 12 GitHub issues for team delegation
├── TEAM_ROLES.md             # 6-member team roles & API contracts
├── start_all.bat             # One-click launcher for FastAPI + Vite UI
├── backend/
│   ├── requirements.txt      # Python dependencies
│   ├── run_backend.bat       # FastAPI launcher
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── api/routes.py     # REST endpoints (/ingest, /query, /quiz, /export/ppt, /export/pdf)
│   │   ├── ingestion/        # PyMuPDF coordinate-aware text parser
│   │   ├── rag/              # Vector store & marks-aware prompt engine
│   │   ├── diagnostics/      # Learner state model & Error Taxonomy
│   │   └── generators/       # python-pptx & ReportLab compilers
│   ├── data/                 # Sample B.Tech textbook chapter (Binary Search Trees)
│   └── tests/                # Automated RAG & generator tests
└── frontend/
    ├── package.json          # Vite React app dependencies
    ├── run_frontend.bat      # Vite app launcher
    └── src/
        ├── index.css         # Modern glassmorphism UI design system
        ├── App.jsx           # Master navigation & view switcher
        └── components/
            ├── student/      # Split-screen PDF viewer, chat, diagnostic quiz
            └── educator/     # Presentation builder, handout exporter, weakness heatmap
```

---

## 🛠️ Quick Start Guide

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Node.js 18+ and npm

### 1. Launch Everything with One Click (Windows)
Double-click `start_all.bat` or run in terminal:
```cmd
start_all.bat
```

### 2. Manual Startup

**Backend:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation will be active at: `http://localhost:8000/docs`

**Frontend:**
```cmd
cd frontend
npm install
npm run dev
```
Access the application UI at: `http://localhost:5173`

---

## 🎬 Winning 4-Minute Jury Demo Script

| Time | Action | Demonstration Point |
|---|---|---|
| **0:00 - 0:30** | Select sample B.Tech PDF (*Binary Search Trees*) in Educator/Student Portal | Show structure-aware ingestion with coordinate indexing. |
| **0:30 - 1:30** | Ask *"Explain BST deletion algorithm"*. Switch between **2 Marks** and **10 Marks**. | Demonstrate marks-aware prompt scaling & academic formatting. |
| **1:30 - 2:15** | Click the evidence citation badge next to generated answer. | **The 'Wow' Moment**: Split-screen PDF viewer highlights exact page bounding box overlay in real-time. |
| **2:15 - 3:00** | Click **"Take Diagnostic Quiz"**, pick an incorrect answer. | Show Error Taxonomy diagnosis & **30-Minute Rescue Mission** with conceptual analogy. |
| **3:00 - 3:45** | Switch to **Educator Console**, click **"Generate Presentation Deck (.pptx)"** and **"Export Handout (.pdf)"**. | Show single-source-of-truth export for teachers (`python-pptx` & `ReportLab`). |
| **3:45 - 4:00** | Ask off-topic query *"How do I bake a cake?"*. | Demonstrate strict **Evidence-or-Abstain Gate** preventing hallucination. |

---

## 👥 Teammate Issue Tracking & Collaboration
Refer to [`ISSUES_BACKLOG.md`](file:///c:/Users/Dell/OneDrive/Desktop/hackathon/SIH/SIH%20Project/SIH-Project/ISSUES_BACKLOG.md) for 12 ready-to-copy GitHub issues mapped directly to our 6 team roles:
1. **You (RAG & Integration Lead)**
2. **Teammate 1 (Document Intelligence)**
3. **Teammate 2 (Lead Backend & Architect)**
4. **Teammate 3 (Student Portal Dev)**
5. **Teammate 4 (Educator Console Dev)**
6. **Teammate 5 (Output & QA Engineer)**