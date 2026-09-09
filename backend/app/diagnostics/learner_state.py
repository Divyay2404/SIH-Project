"""
Learner-State Model & Error Taxonomy Classifier.
Implements StudyForge Readiness-First Engine & Learning Twin Diagnostics.
Backed by SQLite persistent storage for student topic readiness, error telemetry,
and registered quiz question verification.

Classifies quiz errors into:
- Conceptual Gap
- Process/Calculation Mistake
- Terminology Confusion
- Careless Error

Triggers '30-Minute Rescue Missions' with targeted analogies when conceptual gaps occur.
"""

from typing import Dict, Any, List, Optional
from app.storage.database import db_manager


class LearnerStateEngine:
    def __init__(self, user_id: str = "student_sih_2026"):
        self.user_id = user_id
        self.is_demo_mode = False
        # Fresh user state starts with zero fabricated data
        self.state = {
            "user_id": user_id,
            "overall_readiness": 0,
            "topics": {},
            "submissions": []
        }
        self._load_from_storage()

    def _load_from_storage(self):
        """Rehydrates learner state from SQLite storage on startup."""
        try:
            stored_topics = db_manager.get_learner_topics(self.user_id)
            for t in stored_topics:
                tid = t["topic_id"]
                self.state["topics"][tid] = {
                    "readiness": t["readiness"],
                    "confidence": t["confidence"],
                    "attempts": t["attempts"],
                    "correct_attempts": t["correct_attempts"],
                    "mistakes": [t["last_error"]] if t.get("last_error") else []
                }
            if self.state["topics"]:
                readiness_vals = [t["readiness"] for t in self.state["topics"].values()]
                self.state["overall_readiness"] = round(sum(readiness_vals) / len(readiness_vals))
        except Exception:
            pass

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

        # Reload latest state from SQLite
        self._load_from_storage()

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
        db_distribution = db_manager.get_class_error_distribution()

        for topic_id, t_data in self.state["topics"].items():
            topic_name = topic_id.replace("_", " ").title()
            readiness = t_data.get("readiness", 50)
            status = (
                "Mastered" if readiness >= 85
                else ("Good Progress" if readiness >= 70
                else ("Needs Review" if readiness >= 50 else "Critical Gap"))
            )
            mistakes = t_data.get("mistakes", [])
            primary_error = mistakes[-1] if mistakes else "None"

            attempts = t_data.get("attempts", 1)
            correct_attempts = t_data.get("correct_attempts", 1 if readiness >= 50 else 0)
            error_rate = max(0, round(((attempts - correct_attempts) / max(1, attempts)) * 100))

            heatmap_items.append({
                "topic": topic_name,
                "mastery": readiness,
                "error_type": primary_error,
                "status": status,
                "attempts": attempts,
                "error_rate": error_rate
            })

        if not db_distribution:
            # Aggregate fallback distribution from active topics
            error_counts = {
                "Conceptual Gap": 0,
                "Process Mistake": 0,
                "Terminology Confusion": 0,
                "Careless Error": 0
            }
            for t_data in self.state["topics"].values():
                for m in t_data.get("mistakes", []):
                    if m in error_counts:
                        error_counts[m] += 1
            tot = sum(error_counts.values()) or 1
            distribution = {k: round((v / tot) * 100) for k, v in error_counts.items()}
        else:
            distribution = db_distribution

        return {
            "overall_readiness": self.state["overall_readiness"],
            "topic_heatmap": heatmap_items,
            "class_error_distribution": distribution,
            "is_empty": False
        }

    def evaluate_quiz_answer(
        self,
        question_id: str,
        selected_option: int,
        topic_id: str = "general",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Diagnoses quiz submission against Error Taxonomy and triggers Rescue Mission if conceptual gap exists.
        Evaluates answer against true correct option registered in SQLite question bank.
        """
        active_user = user_id or self.user_id
        clean_topic = topic_id.replace("_", " ").title()

        # Look up registered question to verify true correct option
        q_record = db_manager.get_quiz_question(question_id)
        if q_record is not None:
            correct_option = q_record.get("correct_option", 0)
            custom_error_mappings = q_record.get("error_mappings", {})
        else:
            # Fallback for demo / uncatalogued questions: option 0
            correct_option = 0
            custom_error_mappings = {}

        # Initialize topic in state if not present
        if topic_id not in self.state["topics"]:
            self.state["topics"][topic_id] = {
                "readiness": 50,
                "confidence": "Medium",
                "attempts": 0,
                "correct_attempts": 0,
                "mistakes": []
            }

        is_correct = (selected_option == correct_option)

        if is_correct:
            self.state["topics"][topic_id]["attempts"] = self.state["topics"][topic_id].get("attempts", 0) + 1
            self.state["topics"][topic_id]["correct_attempts"] = self.state["topics"][topic_id].get("correct_attempts", 0) + 1
            self.state["topics"][topic_id]["readiness"] = min(self.state["topics"][topic_id]["readiness"] + 15, 100)

            # Persist to SQLite
            db_manager.record_quiz_submission(
                user_id=active_user,
                question_id=question_id,
                topic_id=topic_id,
                selected_option=selected_option,
                is_correct=True,
                error_category=None
            )

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

        # Check if question has custom error mapping for this option
        opt_key = str(selected_option)
        if opt_key in custom_error_mappings:
            error_info = custom_error_mappings[opt_key]
        else:
            # Map based on selected option index or default to conceptual_gap
            error_info = taxonomy_mapping.get(selected_option, taxonomy_mapping[1])

        error_title = error_info["title"]
        error_type = error_info["type"]

        self.state["topics"][topic_id]["attempts"] = self.state["topics"][topic_id].get("attempts", 0) + 1
        self.state["topics"][topic_id]["readiness"] = max(self.state["topics"][topic_id]["readiness"] - 10, 15)
        self.state["topics"][topic_id]["mistakes"].append(error_title)

        # Persist to SQLite
        db_manager.record_quiz_submission(
            user_id=active_user,
            question_id=question_id,
            topic_id=topic_id,
            selected_option=selected_option,
            is_correct=False,
            error_category=error_title
        )

        readiness_vals = [t["readiness"] for t in self.state["topics"].values()]
        self.state["overall_readiness"] = round(sum(readiness_vals) / len(readiness_vals))

        return {
            "status": "diagnosed",
            "is_correct": False,
            "error_category": error_type,
            "error_title": f"{error_title}: {clean_topic}",
            "explanation": error_info.get("desc", f"Identified {error_title} in {clean_topic}."),
            "rescue_mission_triggered": error_type == "conceptual_gap",
            "rescue_mission": {
                "title": f"🚨 30-Minute Rescue Mission: {clean_topic}",
                "analogy": error_info.get("analogy", f"💡 Review foundational rules and invariants for {clean_topic}."),
                "action_plan": f"Review foundational rules for {clean_topic} before re-attempting assessment."
            }
        }


learner_engine = LearnerStateEngine()
