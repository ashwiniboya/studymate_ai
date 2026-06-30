"""Agent orchestration service."""

from app.agents.flashcard.agent import create_flashcards
from app.agents.notes.agent import generate_notes
from app.agents.planner.agent import create_study_plan
from app.agents.progress.agent import get_learning_progress, record_activity
from app.agents.quiz.agent import create_quiz
from app.agents.utils import generate_content, retrieve_context


class AgentService:
    """Orchestrates ADK agent tool functions for the API layer."""

    def create_plan(self, document_id: int, goals: str = "") -> dict:
        return create_study_plan(document_id, goals)

    def generate_notes(self, document_id: int, focus_area: str = "") -> dict:
        return generate_notes(document_id, focus_area)

    def create_quiz(self, document_id: int, num_questions: int = 5, difficulty: str = "medium") -> dict:
        return create_quiz(document_id, num_questions, difficulty)

    def create_flashcards(self, document_id: int, num_cards: int = 10) -> dict:
        return create_flashcards(document_id, num_cards)

    def get_progress(self, document_id: int | None = None) -> dict:
        return get_learning_progress(document_id)

    def record_activity(self, document_id: int, activity_type: str, score: float = 0.0, details: str = "") -> dict:
        return record_activity(document_id, activity_type, score, details)

    def chat(self, message: str, document_id: int | None = None) -> dict:
        """Answer questions about uploaded documents using RAG."""
        context = retrieve_context(message, document_id=document_id, top_k=6)
        if not context:
            return {
                "status": "success",
                "response": "I don't have any study materials to reference yet. Please upload a document first.",
            }

        prompt = f"""Answer the student's question based on the study material below.
If the answer is not in the material, say so clearly and provide general guidance.

STUDY MATERIAL:
{context}

STUDENT QUESTION: {message}

Provide a clear, educational answer. Use examples when helpful."""

        response = generate_content(
            prompt,
            system_instruction="You are StudyMate AI, a helpful study assistant. Answer questions clearly and educationally based on the provided material.",
            temperature=0.5,
        )

        if document_id:
            record_activity(document_id, "chat_session", details=f"Q: {message[:100]}")

        return {"status": "success", "response": response, "context_used": True}
