"""
Learner-State Model & Error Taxonomy Classifier.
Implements StudyForge Readiness-First Engine & Learning Twin Diagnostics.
Classifies quiz errors into:
- Conceptual Gap
- Process/Calculation Mistake
- Terminology Confusion
- Careless Error

Triggers '30-Minute Rescue Missions' with targeted analogies when conceptual gaps occur.
"""

from typing import Dict, Any, List


class LearnerStateEngine:
    def __init__(self):
        # Initial user state state tracking
        self.state = {
            "user_id": "student_sih_2026",
            "overall_readiness": 72,
            "topics": {
                "bst_definition": {"readiness": 88, "confidence": "High", "mistakes": []},
                "bst_insertion": {"readiness": 78, "confidence": "Medium", "mistakes": []},
                "bst_deletion": {"readiness": 54, "confidence": "Low", "mistakes": ["Conceptual Gap"]},
                "bst_complexity": {"readiness": 68, "confidence": "Medium", "mistakes": []}
            }
        }

    def get_readiness_heatmap(self) -> Dict[str, Any]:
        """Returns topic mastery readiness levels and error breakdown for teacher heatmap."""
        return {
            "overall_readiness": self.state["overall_readiness"],
            "topic_heatmap": [
                {"topic": "BST Concept & Properties", "mastery": 88, "error_type": "None", "status": "Mastered"},
                {"topic": "BST Insertion Algorithm", "mastery": 78, "error_type": "Careless Error", "status": "Good"},
                {"topic": "BST Deletion (Two Children)", "mastery": 42, "error_type": "Conceptual Gap", "status": "Critical Gap"},
                {"topic": "Time & Space Complexity", "mastery": 68, "error_type": "Terminology Confusion", "status": "Needs Review"}
            ],
            "class_error_distribution": {
                "Conceptual Gap": 45,
                "Process Mistake": 25,
                "Terminology Confusion": 20,
                "Careless Error": 10
            }
        }

    def evaluate_quiz_answer(self, question_id: str, selected_option: int, topic_id: str = "bst_deletion") -> Dict[str, Any]:
        """
        Diagnoses quiz submission against Error Taxonomy and triggers Rescue Mission if conceptual gap exists.
        """
        # Question key mapping for demo
        correct_option = 0  # Option 0 is correct

        if selected_option == correct_option:
            # Correct answer update
            self.state["overall_readiness"] = min(self.state["overall_readiness"] + 5, 100)
            return {
                "status": "correct",
                "is_correct": True,
                "feedback": "🎉 **Correct!** Excellent understanding of BST in-order successor substitution.",
                "updated_readiness": self.state["overall_readiness"],
                "rescue_mission": None
            }

        # Incorrect answer classification mapping
        taxonomy_mapping = {
            1: {
                "type": "conceptual_gap",
                "title": "Conceptual Gap: In-Order Successor Substitution",
                "desc": "You confused node deletion with simple leaf removal.",
                "analogy": "💡 **30-Minute Rescue Mission Analogy**: Imagine replacing a school principal. You can't leave the position vacant or promote a random first-grader! You substitute the principal with the vice-principal (the in-order successor—the next qualified person in rank) to maintain school order!"
            },
            2: {
                "type": "process_mistake",
                "title": "Process / Calculation Mistake",
                "desc": "You identified the correct successor but skipped updating the parent pointer.",
                "analogy": "💡 **Process Tip**: Always perform pointer updates in 3 sequential steps: (1) Copy successor value, (2) Update child pointer, (3) Delete successor node."
            },
            3: {
                "type": "terminology_confusion",
                "title": "Terminology Confusion",
                "desc": "Confused In-Order Successor with Pre-Order Traversal.",
                "analogy": "💡 **Terminology Tip**: In-Order means 'Left -> Root -> Right' (gives sorted order). Pre-Order means 'Root -> Left -> Right'."
            }
        }

        error_info = taxonomy_mapping.get(selected_option, taxonomy_mapping[1])
        
        # Update topic state
        if topic_id in self.state["topics"]:
            self.state["topics"][topic_id]["readiness"] = max(self.state["topics"][topic_id]["readiness"] - 8, 20)
            self.state["topics"][topic_id]["mistakes"].append(error_info["title"])

        return {
            "status": "diagnosed",
            "is_correct": False,
            "error_category": error_info["type"],
            "error_title": error_info["title"],
            "explanation": error_info["desc"],
            "rescue_mission_triggered": error_info["type"] == "conceptual_gap",
            "rescue_mission": {
                "title": "🚨 30-Minute Rescue Mission Triggered",
                "analogy": error_info["analogy"],
                "action_plan": "Review foundational Binary Tree traversal rules before re-attempting the deletion quiz."
            }
        }


learner_engine = LearnerStateEngine()
