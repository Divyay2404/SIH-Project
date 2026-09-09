"""
Demo Data Module for StudyForge OS.
Provides isolated Binary Search Tree (BST) sample curriculum content,
slides, diagnostic questions, and analytics for interactive demonstrations.
"""

DEMO_DOCUMENT_ID = "doc_bst_chapter_01"
DEMO_FILENAME = "Binary_Search_Trees_Chapter.pdf"
DEMO_TITLE = "Binary Search Trees &amp; Dynamic Dictionaries"

DEMO_CHUNKS = [
    {
        "id": "chunk_01",
        "document_id": DEMO_DOCUMENT_ID,
        "document_name": DEMO_FILENAME,
        "page": 1,
        "text": "A Binary Search Tree (BST) is a binary tree where for every node X, all keys in the left subtree of X are less than key(X), and all keys in the right subtree of X are greater than key(X).",
        "bbox": [50.0, 100.0, 500.0, 220.0],
        "keywords": ["bst", "binary search tree", "definition", "property", "left subtree", "right subtree"]
    },
    {
        "id": "chunk_02",
        "document_id": DEMO_DOCUMENT_ID,
        "document_name": DEMO_FILENAME,
        "page": 2,
        "text": "BST Insertion Algorithm: To insert a key K into a BST, compare K with the root. If root is null, create a node. If K < root.key, recurse left. If K > root.key, recurse right.",
        "bbox": [60.0, 150.0, 520.0, 300.0],
        "keywords": ["insertion", "insert", "algorithm", "recurse", "root"]
    },
    {
        "id": "chunk_03",
        "document_id": DEMO_DOCUMENT_ID,
        "document_name": DEMO_FILENAME,
        "page": 3,
        "text": "BST Deletion Algorithm has 3 cases: Case 1 (Leaf Node): Remove directly. Case 2 (Single Child): Link parent to child. Case 3 (Two Children): Replace node value with its in-order successor (smallest node in right subtree) and recursively delete successor.",
        "bbox": [80.0, 200.0, 540.0, 380.0],
        "keywords": ["deletion", "delete", "remove", "in-order successor", "two children", "leaf node", "cases"]
    },
    {
        "id": "chunk_04",
        "document_id": DEMO_DOCUMENT_ID,
        "document_name": DEMO_FILENAME,
        "page": 4,
        "text": "Time Complexity Analysis of BST Operations: Search, Insertion, and Deletion take O(h) time where h is tree height. Best/Average case (Balanced BST) is O(log N). Worst case (Skewed BST) is O(N).",
        "bbox": [70.0, 120.0, 510.0, 280.0],
        "keywords": ["complexity", "time complexity", "o(log n)", "o(n)", "worst case", "average case", "height"]
    }
]

DEMO_QUIZ = {
    "question_id": "q_bst_del_01",
    "topic": "Binary Search Tree Deletion",
    "question_text": "When deleting a BST node with two children, which node is substituted in its place to maintain the BST invariant?",
    "options": [
        "In-Order Successor (Smallest key in right subtree)",
        "Pre-Order Traversal Root Node",
        "Right-most Leaf Node in Left Subtree",
        "Any random child node"
    ],
    "correct_option": 0
}

DEMO_READINESS_DATA = {
    "overall_readiness": 72,
    "confidence_level": "Medium",
    "active_topics_count": 4,
    "topic_heatmap": [
        {"topic": "BST Invariant Property", "mastery": 88, "error_type": "None", "status": "Mastered"},
        {"topic": "BST Insertion Algorithm", "mastery": 75, "error_type": "Process Mistake", "status": "Proficient"},
        {"topic": "BST Deletion (Two Children)", "mastery": 42, "error_type": "Conceptual Gap", "status": "Critical Gap"},
        {"topic": "Time & Space Complexity", "mastery": 68, "error_type": "Terminology Confusion", "status": "Needs Review"}
    ],
    "class_error_distribution": {
        "Conceptual Gap": 45,
        "Process Mistake": 25,
        "Terminology Confusion": 20,
        "Careless Error": 10
    },
    "is_empty": False
}

BST_DEMO_HEATMAP = DEMO_READINESS_DATA

DEMO_SLIDES = [
    {
        "category": "Title Slide",
        "title": "Binary Search Trees (BST): Theoretical Principles & Algorithms",
        "bullets": [
            "Course: Data Structures & Algorithms (CS201)",
            "Module: Non-Linear Hierarchical Dynamic Data Structures",
            "Target Audience: B.Tech Computer Science & Engineering"
        ],
        "notes": "Welcome class. Today we cover Binary Search Trees, invariant preservation, and asymptotic efficiency bounds."
    },
    {
        "category": "Curriculum Overview",
        "title": "Curriculum Scope & Prerequisites",
        "bullets": [
            "Binary Tree pointer structures and dynamic memory allocation",
            "Search, Insertion, and In-place Deletion semantics",
            "Worst-case vs average-case recurrence relations"
        ],
        "notes": "Review pointer manipulation and recursive tree traversals before delving into deletion cases."
    },
    {
        "category": "Theoretical Foundations",
        "title": "The BST Ordering Invariant",
        "bullets": [
            "For every node X: Left_Subtree(X) < X < Right_Subtree(X)",
            "In-Order traversal strictly produces monotonically increasing keys",
            "Duplicate handling strategies (frequency counters vs left-bias)"
        ],
        "notes": "Explain why preserving the invariant at every mutation is critical for logarithmic query times."
    },
    {
        "category": "Algorithmic Mechanics",
        "title": "Insertion & Search Traversal",
        "bullets": [
            "Root comparison dictates branch descent: left when K < root.key, right when K > root.key",
            "Base condition: Allocation at null pointer terminating leaf position",
            "Deterministic path length bounded strictly by tree depth"
        ],
        "notes": "Walk through insertion step-by-step on the blackboard with numerical keys: 50, 30, 70, 20, 40."
    },
    {
        "category": "System Dynamics",
        "title": "BST Deletion: The Three Structural Cases",
        "bullets": [
            "Case 1: Target is a Leaf node -> Nullify parent pointer and deallocate",
            "Case 2: Target has Single Child -> Bypass node and link parent directly to child",
            "Case 3: Target has Two Children -> Replace with In-Order Successor and recurse"
        ],
        "notes": "Emphasize Case 3: Why in-order successor or predecessor must be used to prevent invariant destruction."
    },
    {
        "category": "Structural Architecture",
        "title": "In-Order Successor Substitution Pipeline",
        "bullets": [
            "Locate smallest node in the target's right subtree (leftmost leaf)",
            "Deep-copy successor payload into target node's memory cell",
            "Execute recursive case 1 or 2 deletion on the original successor node"
        ],
        "diagram": True,
        "diagramStages": [
            {"stage": "1. IDENTIFY", "desc": "Find In-Order Successor in right subtree"},
            {"stage": "2. COPY", "desc": "Overwrite target payload with successor key"},
            {"stage": "3. DELETE", "desc": "Reclaim original successor node leaf memory"}
        ],
        "notes": "Point out the 3-step diagram. Most student conceptual bugs happen when skipping step 2 or 3."
    },
    {
        "category": "Real-World Applications",
        "title": "Industrial Deployments of BST Derivatives",
        "bullets": [
            "Linux Kernel VMA Tracking (Red-Black self-balancing BSTs)",
            "Database Primary Indices & Range Scans (B+ Tree multi-way extensions)",
            "Compiler Symbol Tables for lexical scope resolution"
        ],
        "notes": "Connect theory to systems engineering: Linux CFS scheduler and Postgres indexes."
    },
    {
        "category": "Critical Analysis",
        "title": "Complexity Analysis & Degeneracy Bounds",
        "bullets": [
            "Balanced Tree: Height h = O(log N) -> Search/Insert/Delete O(log N)",
            "Degenerate / Skewed Tree: Height h = O(N) -> Operations degrade to O(N)",
            "Mitigation: AVL rotations and Red-Black color recoloring invariants"
        ],
        "notes": "Show how sorted input sequences cause catastrophic skew without self-balancing rotations."
    },
    {
        "category": "Assessment Standards",
        "title": "Academic Rubric & Exam Patterns",
        "bullets": [
            "2 Marks: State the BST ordering invariant and average-case lookup complexity",
            "5 Marks: Trace deletion of a two-child root node with pointer diagrams",
            "10 Marks: Prove logarithmic height bound and synthesize AVL rotation algorithms"
        ],
        "notes": "Direct students to practice past university exam questions following this exact mark structure."
    },
    {
        "category": "Summary & Takeaways",
        "title": "Core Takeaways & Revision Checklist",
        "bullets": [
            "BST invariant must hold for all subtrees, not merely immediate children",
            "In-order successor maintains sorted traversal order upon node removal",
            "Next Session: Balanced search structures and 2-3 Trees"
        ],
        "notes": "Review the summary and assign the diagnostic rescue quiz for homework."
    }
]
