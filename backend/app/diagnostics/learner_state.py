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
        self.is_demo_mode = False
        # Fresh user state starts with zero fabricated data
        self.state = {
            "user_id": "student_sih_2026",
            "overall_readiness": 0,
            "topics": {},
            "submissions": []
        }

    def activate_demo_mode(self):
        """Activates demo diagnostics state."""
        self.is_demo_mode = True

    def deactivate_demo_mode(self):
        """Deactivates demo mode back to clean user state."""
        self.is_demo_mode = False

    def get_readiness_heatmap(self) -> Dict[str, Any]:
        """Returns topic mastery readiness levels and error breakdown for teacher heatmap."""
        if self.is_demo_mode:
            from app.demo.demo_data import BST_DEMO_HEATMAP
            return BST_DEMO_HEATMAP

        if not self.state["topics"]:
            return {
                "overall_readiness": 0,
                "topic_heatmap": [],
                "class_error_distribution": {},
                "is_empty": True,
                "message": "No diagnostic data available yet."
            }

        # Calculate actual dynamic heatmap from recorded student submissions
        heatmap_items = []
        error_counts = {
            "Conceptual Gap": 0,
            "Process Mistake": 0,
            "Terminology Confusion": 0,
            "Careless Error": 0
        }

        for topic_name, t_data in self.state["topics"].items():
            readiness = t_data.get("readiness", 50)
            status = "Mastered" if readiness >= 85 else ("Good Progress" if readiness >= 70 else ("Needs Review" if readiness >= 50 else "Critical Gap"))
            mistakes = t_data.get("mistakes", [])
            primary_error = mistakes[-1] if mistakes else "None"

            for m in mistakes:
                if m in error_counts:
                    error_counts[m] += 1

            heatmap_items.append({
                "topic": topic_name,
                "mastery": readiness,
                "error_type": primary_error,
                "status": status
            })

        total_errors = sum(error_counts.values()) or 1
        distribution = {k: round((v / total_errors) * 100) for k, v in error_counts.items()}

        return {
            "overall_readiness": self.state["overall_readiness"],
            "topic_heatmap": heatmap_items,
            "class_error_distribution": distribution,
            "is_empty": False
        }

    def evaluate_quiz_answer(self, question_id: str, selected_option: int, topic_id: str = "general") -> Dict[str, Any]:
        """
        Diagnoses quiz submission against Error Taxonomy and triggers Rescue Mission if conceptual gap exists.
        """
        clean_topic = topic_id.replace("_", " ").title()
        correct_option = 0  # Option 0 is correct by convention in micro-assessments

        # Initialize topic in state if not present
        if topic_id not in self.state["topics"]:
            self.state["topics"][topic_id] = {
                "readiness": 50,
                "confidence": "Medium",
                "mistakes": []
            }

        if selected_option == correct_option:
            self.state["topics"][topic_id]["readiness"] = min(self.state["topics"][topic_id]["readiness"] + 15, 100)
            # Recompute overall readiness across topics
            readiness_vals = [t["readiness"] for t in self.state["topics"].values()]
            self.state["overall_readiness"] = round(sum(readiness_vals) / len(readiness_vals))

            return {
                "status": "correct",
                "is_correct": True,
                "feedback": f"🎉 **Correct!** Excellent understanding of foundational principles in **{clean_topic}**.",
                "updated_readiness": self.state["overall_readiness"],
                "rescue_mission": None
            }

        taxonomy_mapping = {
            1: {
                "type": "conceptual_gap",
                "title": "Conceptual Gap",
                "desc": f"Misunderstood foundational invariant or rule in {clean_topic}.",
                "analogy": f"💡 **30-Minute Rescue Mission Analogy**: In {clean_topic}, fundamental constraints must be satisfied first before executing mutations, just like confirming a foundation is solid before building."
            },
            2: {
                "type": "process_mistake",
                "title": "Process Mistake",
                "desc": f"Correct concept identified, but skipped step-by-step procedural sequencing in {clean_topic}.",
                "analogy": f"💡 **Process Tip**: In {clean_topic}, ensure operations follow deterministic sequential ordering."
            },
            3: {
                "type": "terminology_confusion",
                "title": "Terminology Confusion",
                "desc": f"Conflated technical terminology or operational definitions in {clean_topic}.",
                "analogy": f"💡 **Terminology Tip**: Review the precise mathematical definitions for {clean_topic} to avoid notation confusion."
            },
            4: {
                "type": "careless_error",
                "title": "Careless Error",
                "desc": "A simple slip such as misclicking or selecting an unverified option.",
                "analogy": "💡 **Careless Tip**: Double-check your selection against core boundary conditions."
            }
        }

        error_info = taxonomy_mapping.get(selected_option, taxonomy_mapping[1])
        error_title = error_info["title"]

        self.state["topics"][topic_id]["readiness"] = max(self.state["topics"][topic_id]["readiness"] - 10, 15)
        self.state["topics"][topic_id]["mistakes"].append(error_title)

        readiness_vals = [t["readiness"] for t in self.state["topics"].values()]
        self.state["overall_readiness"] = round(sum(readiness_vals) / len(readiness_vals))

        return {
            "status": "diagnosed",
            "is_correct": False,
            "error_category": error_info["type"],
            "error_title": f"{error_title}: {clean_topic}",
            "explanation": error_info["desc"],
            "rescue_mission_triggered": error_info["type"] == "conceptual_gap",
            "rescue_mission": {
                "title": f"🚨 30-Minute Rescue Mission: {clean_topic}",
                "analogy": error_info["analogy"],
                "action_plan": f"Review foundational rules for {clean_topic} before re-attempting assessment."
            }
        }


learner_engine = LearnerStateEngine()
