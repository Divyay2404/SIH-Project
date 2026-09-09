"""
Chroma / Hybrid Vector Store Manager with Bounding Box Coordinate Metadata.
Stores chunk text alongside page numbers, document IDs, and bounding box coordinates [x0, y0, x1, y1].
"""

import math
import re
from typing import List, Dict, Any, Optional

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
        self.documents = []
        self._initialize_default_knowledge()

    def _initialize_default_knowledge(self):
        """Seed initial grounded knowledge base from B.Tech Binary Search Tree syllabus."""
        self.documents = [
            {
                "id": "chunk_01",
                "document_id": "doc_bst_chapter_01",
                "document_name": "Binary_Search_Trees_Chapter.pdf",
                "page": 1,
                "text": "A Binary Search Tree (BST) is a binary tree where for every node X, all keys in the left subtree of X are less than key(X), and all keys in the right subtree of X are greater than key(X).",
                "bbox": [50.0, 100.0, 500.0, 220.0],
                "keywords": ["bst", "binary search tree", "definition", "property", "left subtree", "right subtree"]
            },
            {
                "id": "chunk_02",
                "document_id": "doc_bst_chapter_01",
                "document_name": "Binary_Search_Trees_Chapter.pdf",
                "page": 2,
                "text": "BST Insertion Algorithm: To insert a key K into a BST, compare K with the root. If root is null, create a node. If K < root.key, recurse left. If K > root.key, recurse right.",
                "bbox": [60.0, 150.0, 520.0, 300.0],
                "keywords": ["insertion", "insert", "algorithm", "recurse", "root"]
            },
            {
                "id": "chunk_03",
                "document_id": "doc_bst_chapter_01",
                "document_name": "Binary_Search_Trees_Chapter.pdf",
                "page": 3,
                "text": "BST Deletion Algorithm has 3 cases: Case 1 (Leaf Node): Remove directly. Case 2 (Single Child): Link parent to child. Case 3 (Two Children): Replace node value with its in-order successor (smallest node in right subtree) and recursively delete successor.",
                "bbox": [80.0, 200.0, 540.0, 380.0],
                "keywords": ["deletion", "delete", "remove", "in-order successor", "two children", "leaf node", "cases"]
            },
            {
                "id": "chunk_04",
                "document_id": "doc_bst_chapter_01",
                "document_name": "Binary_Search_Trees_Chapter.pdf",
                "page": 4,
                "text": "Time Complexity Analysis of BST Operations: Search, Insertion, and Deletion take O(h) time where h is tree height. Best/Average case (Balanced BST) is O(log N). Worst case (Skewed BST) is O(N).",
                "bbox": [70.0, 120.0, 510.0, 280.0],
                "keywords": ["complexity", "time complexity", "o(log n)", "o(n)", "worst case", "average case", "height"]
            }
        ]

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Add newly ingested PDF chunks into vector memory."""
        for idx, chunk in enumerate(chunks):
            chunk["id"] = chunk.get("id") or f"ingested_chunk_{len(self.documents) + idx + 1}"
            chunk["keywords"] = [w.lower() for w in chunk["text"].split() if len(w) > 3]
            self.documents.append(chunk)

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
        Enforces strict document_id filtering and calculates similarity scores
        between user query and knowledge base chunks scoped to the target document.

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

        scored_chunks = []
        for doc in candidate_docs:
            text = doc.get("text", "").lower()
            doc_words = set(re.findall(r'\b[a-zA-Z0-9_-]+\b', text))
            keywords = set(k.lower() for k in doc.get("keywords", []))

            # Word-level overlap similarity calculation
            matches = sum(1 for w in search_tokens if w in doc_words or w in keywords)
            if matches == 0:
                scored_chunks.append({**doc, "score": 0.0})
                continue

            score = matches / len(search_tokens)

            # Boost score for domain terms (len > 3) that matched
            significant_terms = [w for w in search_tokens if len(w) > 3]
            if significant_terms:
                term_hits = sum(1 for w in significant_terms if w in doc_words or w in keywords)
                if term_hits > 0:
                    score += min(0.35 * (term_hits / len(significant_terms)), 0.45)

            score = min(round(score, 2), 0.98)
            scored_chunks.append({**doc, "score": score})

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def search_similar(self, query: str, top_k: int = 2, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Backward-compatible proxy forwarding to search with document scoping."""
        return self.search(query=query, document_id=document_id, top_k=top_k)


vector_store = VectorStoreManager()
