"""
SQLite Database Layer for StudyForge OS.
Provides persistent storage for:
- Document registry and metadata
- Learner state and topic mastery
- Quiz submissions and mistake telemetry
- Quiz questions bank with verified correct options
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default database path in the backend directory
DEFAULT_DB_PATH = os.getenv(
    "STUDYFORGE_DB_PATH",
    str(Path(__file__).resolve().parent.parent.parent / "studyforge.db")
)


class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes database schema if tables do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Documents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    user_id TEXT DEFAULT 'student_sih_2026',
                    filename TEXT NOT NULL,
                    title TEXT NOT NULL,
                    pages_count INTEGER DEFAULT 1,
                    chunks_count INTEGER DEFAULT 0,
                    summary TEXT,
                    sections TEXT,
                    important_concepts TEXT,
                    important_portions TEXT,
                    slides TEXT,
                    pages TEXT,
                    pdf_bytes BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Learner Topics Mastery Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learner_topics (
                    user_id TEXT NOT NULL,
                    topic_id TEXT NOT NULL,
                    readiness INTEGER DEFAULT 50,
                    confidence TEXT DEFAULT 'Medium',
                    attempts INTEGER DEFAULT 0,
                    correct_attempts INTEGER DEFAULT 0,
                    last_error TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, topic_id)
                )
            """)

            # Quiz Questions Bank
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_questions (
                    question_id TEXT PRIMARY KEY,
                    document_id TEXT,
                    topic TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    options TEXT NOT NULL,
                    correct_option INTEGER NOT NULL DEFAULT 0,
                    error_mappings TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Quiz Submissions History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    topic_id TEXT NOT NULL,
                    selected_option INTEGER NOT NULL,
                    is_correct INTEGER NOT NULL,
                    error_category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Vector Chunks Persistence Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    page INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    bbox TEXT NOT NULL,
                    keywords TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    # ==========================================
    # Document Persistence Methods
    # ==========================================

    def save_document(self, doc_data: Dict[str, Any], user_id: str = "student_sih_2026"):
        """Inserts or updates document record in SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents (
                    document_id, user_id, filename, title, pages_count, chunks_count,
                    summary, sections, important_concepts, important_portions,
                    slides, pages, pdf_bytes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_data["document_id"],
                user_id,
                doc_data.get("filename", "document.pdf"),
                doc_data.get("title", "Untitled Document"),
                doc_data.get("pages_count", 1),
                len(doc_data.get("chunks", [])),
                doc_data.get("summary", ""),
                json.dumps(doc_data.get("sections", [])),
                json.dumps(doc_data.get("important_concepts", [])),
                json.dumps(doc_data.get("important_portions", [])),
                json.dumps(doc_data.get("slides", [])),
                json.dumps(doc_data.get("pages", [])),
                doc_data.get("pdf_bytes"),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves document record by document_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "document_id": row["document_id"],
                "user_id": row["user_id"],
                "filename": row["filename"],
                "title": row["title"],
                "pages_count": row["pages_count"],
                "chunks_count": row["chunks_count"],
                "summary": row["summary"],
                "sections": json.loads(row["sections"] or "[]"),
                "important_concepts": json.loads(row["important_concepts"] or "[]"),
                "important_portions": json.loads(row["important_portions"] or "[]"),
                "slides": json.loads(row["slides"] or "[]"),
                "pages": json.loads(row["pages"] or "[]"),
                "pdf_bytes": row["pdf_bytes"],
            }

    def list_documents(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists stored documents optionally filtered by user_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            else:
                cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
            rows = cursor.fetchall()
            docs = []
            for row in rows:
                docs.append({
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "title": row["title"],
                    "pages_count": row["pages_count"],
                    "chunks_count": row["chunks_count"],
                    "summary": row["summary"],
                })
            return docs

    # ==========================================
    # Vector Chunk Persistence Methods
    # ==========================================

    def save_chunks(self, chunks: List[Dict[str, Any]]):
        """Persists extracted vector chunks into SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for chunk in chunks:
                cursor.execute("""
                    INSERT OR REPLACE INTO vector_chunks (
                        id, document_id, document_name, page, text, bbox, keywords
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.get("id"),
                    chunk.get("document_id"),
                    chunk.get("document_name", ""),
                    chunk.get("page", 1),
                    chunk.get("text", ""),
                    json.dumps(chunk.get("bbox", [0, 0, 0, 0])),
                    json.dumps(chunk.get("keywords", []))
                ))
            conn.commit()

    def get_all_chunks(self, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves stored chunks from SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if document_id:
                cursor.execute("SELECT * FROM vector_chunks WHERE document_id = ?", (document_id,))
            else:
                cursor.execute("SELECT * FROM vector_chunks")
            rows = cursor.fetchall()
            chunks = []
            for r in rows:
                chunks.append({
                    "id": r["id"],
                    "document_id": r["document_id"],
                    "document_name": r["document_name"],
                    "page": r["page"],
                    "text": r["text"],
                    "bbox": json.loads(r["bbox"] or "[0,0,0,0]"),
                    "keywords": json.loads(r["keywords"] or "[]")
                })
            return chunks

    # ==========================================
    # Quiz Questions Bank Methods
    # ==========================================

    def register_quiz_question(
        self,
        question_id: str,
        topic: str,
        question_text: str,
        options: List[str],
        correct_option: int,
        document_id: Optional[str] = None,
        error_mappings: Optional[Dict[str, Any]] = None
    ):
        """Stores a generated or demo quiz question with its true correct option."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO quiz_questions (
                    question_id, document_id, topic, question_text, options, correct_option, error_mappings
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                question_id,
                document_id,
                topic,
                question_text,
                json.dumps(options),
                correct_option,
                json.dumps(error_mappings or {})
            ))
            conn.commit()

    def get_quiz_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a quiz question from the question bank."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quiz_questions WHERE question_id = ?", (question_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "question_id": row["question_id"],
                "document_id": row["document_id"],
                "topic": row["topic"],
                "question_text": row["question_text"],
                "options": json.loads(row["options"] or "[]"),
                "correct_option": row["correct_option"],
                "error_mappings": json.loads(row["error_mappings"] or "{}")
            }

    # ==========================================
    # Learner State & Telemetry Methods
    # ==========================================

    def record_quiz_submission(
        self,
        user_id: str,
        question_id: str,
        topic_id: str,
        selected_option: int,
        is_correct: bool,
        error_category: Optional[str] = None
    ):
        """Records a learner quiz submission and updates topic mastery in SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Record submission
            cursor.execute("""
                INSERT INTO quiz_submissions (
                    user_id, question_id, topic_id, selected_option, is_correct, error_category
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                question_id,
                topic_id,
                selected_option,
                1 if is_correct else 0,
                error_category
            ))

            # Fetch existing topic mastery
            cursor.execute("""
                SELECT * FROM learner_topics WHERE user_id = ? AND topic_id = ?
            """, (user_id, topic_id))
            row = cursor.fetchone()

            if row:
                attempts = row["attempts"] + 1
                correct_attempts = row["correct_attempts"] + (1 if is_correct else 0)
                current_readiness = row["readiness"]
                if is_correct:
                    new_readiness = min(current_readiness + 15, 100)
                    last_err = row["last_error"]
                else:
                    new_readiness = max(current_readiness - 10, 15)
                    last_err = error_category or "Conceptual Gap"

                cursor.execute("""
                    UPDATE learner_topics
                    SET readiness = ?, attempts = ?, correct_attempts = ?, last_error = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND topic_id = ?
                """, (new_readiness, attempts, correct_attempts, last_err, user_id, topic_id))
            else:
                attempts = 1
                correct_attempts = 1 if is_correct else 0
                new_readiness = 65 if is_correct else 40
                last_err = None if is_correct else (error_category or "Conceptual Gap")
                cursor.execute("""
                    INSERT INTO learner_topics (
                        user_id, topic_id, readiness, attempts, correct_attempts, last_error
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, topic_id, new_readiness, attempts, correct_attempts, last_err))

            conn.commit()

    def get_learner_topics(self, user_id: str = "student_sih_2026") -> List[Dict[str, Any]]:
        """Retrieves all tracked topics for a learner."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM learner_topics WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_class_error_distribution(self) -> Dict[str, int]:
        """Calculates aggregated class error breakdown from actual learner submissions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT error_category, COUNT(*) as count
                FROM quiz_submissions
                WHERE is_correct = 0 AND error_category IS NOT NULL
                GROUP BY error_category
            """)
            rows = cursor.fetchall()
            total = sum(r["count"] for r in rows)
            if not total:
                return {}

            distribution = {}
            for r in rows:
                cat = r["error_category"]
                distribution[cat] = round((r["count"] / total) * 100)
            return distribution

    def clear_all(self):
        """Clears all data (useful for test resets)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents")
            cursor.execute("DELETE FROM learner_topics")
            cursor.execute("DELETE FROM quiz_questions")
            cursor.execute("DELETE FROM quiz_submissions")
            cursor.execute("DELETE FROM vector_chunks")
            conn.commit()


# Singleton database instance
db_manager = DatabaseManager()
