"""
Chroma / Hybrid Vector Store Manager with Bounding Box Coordinate Metadata.
Stores chunk text alongside page numbers and bounding box coordinates [x0, y0, x1, y1].
"""

import math
from typing import List, Dict, Any


class VectorStoreManager:
    def __init__(self):
        self.documents = []
        self._initialize_default_knowledge()

    def _initialize_default_knowledge(self):
        """Seed initial grounded knowledge base from B.Tech Binary Search Tree syllabus."""
        self.documents = [
            {
                "id": "chunk_01",
                "page": 1,
                "text": "A Binary Search Tree (BST) is a binary tree where for every node X, all keys in the left subtree of X are less than key(X), and all keys in the right subtree of X are greater than key(X).",
                "bbox": [50.0, 100.0, 500.0, 220.0],
                "keywords": ["bst", "binary search tree", "definition", "property", "left subtree", "right subtree"]
            },
            {
                "id": "chunk_02",
                "page": 2,
                "text": "BST Insertion Algorithm: To insert a key K into a BST, compare K with the root. If root is null, create a node. If K < root.key, recurse left. If K > root.key, recurse right.",
                "bbox": [60.0, 150.0, 520.0, 300.0],
                "keywords": ["insertion", "insert", "algorithm", "recurse", "root"]
            },
            {
                "id": "chunk_03",
                "page": 3,
                "text": "BST Deletion Algorithm has 3 cases: Case 1 (Leaf Node): Remove directly. Case 2 (Single Child): Link parent to child. Case 3 (Two Children): Replace node value with its in-order successor (smallest node in right subtree) and recursively delete successor.",
                "bbox": [80.0, 200.0, 540.0, 380.0],
                "keywords": ["deletion", "delete", "remove", "in-order successor", "two children", "leaf node", "cases"]
            },
            {
                "id": "chunk_04",
                "page": 4,
                "text": "Time Complexity Analysis of BST Operations: Search, Insertion, and Deletion take O(h) time where h is tree height. Best/Average case (Balanced BST) is O(log N). Worst case (Skewed BST) is O(N).",
                "bbox": [70.0, 120.0, 510.0, 280.0],
                "keywords": ["complexity", "time complexity", "o(log n)", "o(n)", "worst case", "average case", "height"]
            }
        ]

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Add newly ingested PDF chunks into vector memory."""
        for idx, chunk in enumerate(chunks):
            chunk["id"] = f"ingested_chunk_{len(self.documents) + idx + 1}"
            chunk["keywords"] = [w.lower() for w in chunk["text"].split() if len(w) > 3]
            self.documents.append(chunk)

    def search_similar(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Calculates similarity score between user query and knowledge base chunks.
        Returns top-k matching chunks with similarity score and bounding box metadata.
        """
        query_words = set(query.lower().split())
        scored_chunks = []

        for doc in self.documents:
            text = doc["text"].lower()
            keywords = set(doc.get("keywords", []))
            
            # Simple term overlap similarity proxy
            matches = sum(1 for w in query_words if w in text or w in keywords)
            score = round(matches / max(len(query_words), 1), 2)
            
            # Boost score for direct keyword hits
            if any(kw in query.lower() for kw in ["bst", "deletion", "insertion", "complexity", "definition"]):
                if any(kw in text for kw in ["bst", "deletion", "insertion", "complexity", "definition"]):
                    score += 0.45

            score = min(score, 0.98)
            scored_chunks.append({**doc, "score": score})

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]


vector_store = VectorStoreManager()
