# 🎓 StudyForge OS: AI-Powered Adaptive Learning & Research Platform

---

## 🌟 Executive Overview
This repository contains the complete codebase for **StudyForge OS**, an AI-powered adaptive learning platform that integrates structure-aware RAG document intelligence, marks-aware answer scaling, and active diagnostic assessment.

It converts static, unstructured curriculum materials (textbooks, scanned notes, course syllabi) into interactive, grounded learning instruments for students and automated preparation tools for educators.

---

## 🚀 Key Features

1. **Structure-Aware Ingestion & PDF Highlight Offsets**
   - Extracts page-level coordinates (bounding boxes `[x0, y0, x1, y1]`) alongside text chunks using PyMuPDF.
   - Includes automatic localized OCR fallback for scanned or non-selectable textbook pages with coordinate preservation.
   - Integrates a responsive split-screen PDF viewer with real-time orange bounding-box highlight overlays when citations are clicked.

2. **Marks-Aware Answer Scaling (2, 5, 10 Marks)**
   - **2-Mark Schema (Definition Scale)**: Precise definition + core example.
   - **5-Mark Schema (Concept Scale)**: Structured paragraph, 3-4 bulleted core principles, and code/process examples.
   - **10-Mark Schema (Comprehensive Scale)**: Full academic structure with abstract definitions, algorithms, step-by-step proofs, structural block diagrams, and evaluation conclusions.

3. **Strict Grounding & Abstention Gate**
   - Zero-hallucination evidence gate.
   - Rejects off-topic queries with: *"The requested query is not supported by verified textbook evidence"* when retrieval similarity falls below threshold.

4. **Learning Twin & Error Taxonomy Diagnostics**
   - Classifies quiz mistakes into **Conceptual Gap**, **Process/Calculation Mistake**, **Terminology Confusion**, or **Careless Error**.
   - Conceptual gaps trigger an immediate **30-Minute Rescue Mission** with real-world analogies before re-testing.

5. **Unified Facilitator Decks & Handout Generators**
   - **Editable PowerPoint Generator**: Generates clean `.pptx` slides with speaker notes using `python-pptx`.
   - **Printable Study Guide Compiler**: Generates double-column study guides & handouts using `ReportLab`.

---

## 🛠️ Quick Start Guide

### 1. Launch Everything (Windows)
Run `start_all.bat` or execute:
```cmd
start_all.bat
```

### 2. Manual Startup

**Backend:**
```cmd
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation: `http://localhost:8000/docs`

**Frontend:**
```cmd
cd frontend
npm run dev
```
Access the application UI at: `http://localhost:5173`

### 3. Optional OCR Setup (For Scanned PDFs)
To run localized OCR fallback on scanned/image-only PDFs, ensure Tesseract OCR is installed on the host:
- **Windows**: Install via [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) or `winget install UB-Mannheim.TesseractOCR`.
- **Linux**: `sudo apt install tesseract-ocr tesseract-ocr-eng`
- **macOS**: `brew install tesseract tesseract-lang`

*Note: Digital PDFs with selectable text layers parse natively via PyMuPDF without Tesseract.*