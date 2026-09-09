"""
Hybrid Semantic & Vector Store Manager with Bounding Box Coordinate Metadata.
Stores chunk text alongside page numbers, document IDs, and bounding box coordinates [x0, y0, x1, y1].
Backed by SQLite persistence and scikit-learn TF-IDF semantic embeddings.

Enforces strict document_id scoping to guarantee complete cross-document isolation.
Production retrieval initializes completely clean with zero implicit BST/demo data.
"""

import math
import re
from typing import List, Dict, Any, Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from app.storage.database import db_manager

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "isn't", "it", "its", "itself", "let's", "me", "more", "most", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "were",
    "weren't", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "won't", "would", "you", "your", "yours", "yourself", "yourselves",
    # Procedural and conversational query tokens
    "work", "works", "working", "explain", "explains", "describe", "describes",
    "define", "defines", "definition", "detail", "details", "give", "gives",
    "tell", "show", "shows", "step", "steps", "state", "states", "overview", "please"
}


class VectorStoreManager:
    def __init__(self):
        # Starts completely clean: no hardcoded BST chunks in production!
        self.documents: List[Dict[str, Any]] = []
        self._load_persisted_chunks()

    def _load_persisted_chunks(self):
        """Loads previously ingested chunks from SQLite persistence."""
        try:
            stored = db_manager.get_all_chunks()
            if stored:
                self.documents.extend(stored)
        except Exception:
            pass

    def load_demo_knowledge(self):
        """Explicitly seeds isolated BST demo curriculum data on demand."""
        from app.demo.demo_data import DEMO_CHUNKS, DEMO_DOCUMENT_ID
        if not self.has_document(DEMO_DOCUMENT_ID):
            self.add_chunks(DEMO_CHUNKS, persist=False)

    def clear(self):
        """Clears in-memory documents."""
        self.documents = []

    def add_chunks(self, chunks: List[Dict[str, Any]], persist: bool = True):
        """Add newly ingested chunks into vector memory and SQLite storage."""
        for idx, chunk in enumerate(chunks):
            chunk["id"] = chunk.get("id") or f"chunk_{chunk.get('document_id', 'doc')}_{idx + 1}"
            chunk["keywords"] = [w.lower() for w in chunk.get("text", "").split() if len(w) > 3]
            # Avoid duplicate chunks
            if not any(d.get("id") == chunk["id"] for d in self.documents):
                self.documents.append(chunk)

        if persist:
            try:
                db_manager.save_chunks(chunks)
            except Exception:
                pass

    def has_document(self, document_id: str) -> bool:
        """Confirms whether chunks associated with document_id exist in vector memory."""
        if not document_id:
            return False
        return any(doc.get("document_id") == document_id for doc in self.documents)

    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Returns all indexed chunks scoped to document_id."""
        if not document_id:
            return []
        return [doc for doc in self.documents if doc.get("document_id") == document_id]

    def search(self, query: str, document_id: Optional[str] = None, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Enforces strict document_id filtering and computes hybrid semantic similarity
        scores combining lexical overlap with TF-IDF vector embeddings.

        If document_id is provided, only chunks matching document_id are searched.
        If no chunks match document_id, an empty list is returned.
        """
        raw_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', query or "")]
        if not raw_tokens:
            return []

        # Separate domain content words from general stop words
        content_words = [w for w in raw_tokens if w not in STOP_WORDS and len(w) > 1]
        search_tokens = content_words if content_words else raw_tokens

        # Enforce strict document_id filtering if specified
        if document_id and document_id != "all":
            candidate_docs = [doc for doc in self.documents if doc.get("document_id") == document_id]
        else:
            candidate_docs = self.documents

        if not candidate_docs:
            return []

        # Step 1: Lexical keyword overlap scores
        lexical_scores = []
        for doc in candidate_docs:
            text = doc.get("text", "").lower()
            doc_words = set(re.findall(r'\b[a-zA-Z0-9_-]+\b', text))
            keywords = set(k.lower() for k in doc.get("keywords", []))

            matches = sum(1 for w in search_tokens if w in doc_words or w in keywords)
            if matches == 0:
                lexical_scores.append(0.0)
                continue

            score = matches / len(search_tokens)
            significant_terms = [w for w in search_tokens if len(w) > 3]
            if significant_terms:
                term_hits = sum(1 for w in significant_terms if w in doc_words or w in keywords)
                if term_hits > 0:
                    score += min(0.35 * (term_hits / len(significant_terms)), 0.45)

            lexical_scores.append(min(round(score, 4), 0.98))

        # Step 2: TF-IDF vector cosine similarity (if scikit-learn available)
        tfidf_scores = [0.0] * len(candidate_docs)
        if SKLEARN_AVAILABLE and len(candidate_docs) >= 1:
            try:
                corpus = [doc.get("text", "") for doc in candidate_docs]
                vectorizer = TfidfVectorizer(
                    ngram_range=(1, 2),
                    stop_words="english",
                    sublinear_tf=True
                )
                tfidf_matrix = vectorizer.fit_transform(corpus)
                query_vec = vectorizer.transform([query])
                sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
                tfidf_scores = [round(float(s), 4) for s in sims]
            except Exception:
                pass

        # Step 3: Hybrid Score Blending
        scored_chunks = []
        for idx, doc in enumerate(candidate_docs):
            lex = lexical_scores[idx]
            vec = tfidf_scores[idx]
            # Blend: if both present, 60% lexical + 40% vector
            if vec > 0:
                blended = round(0.6 * lex + 0.4 * vec, 2)
            else:
                blended = round(lex, 2)

            scored_chunks.append({**doc, "score": min(blended, 0.98)})

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def search_similar(self, query: str, top_k: int = 2, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Backward-compatible proxy forwarding to search with document scoping."""
        return self.search(query=query, document_id=document_id, top_k=top_k)


vector_store = VectorStoreManager()
