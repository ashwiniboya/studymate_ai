"""Quiz Agent - generates multiple-choice quizzes."""

import json

from google.adk.agents.llm_agent import Agent

from app.agents.utils import generate_content, parse_json_response, retrieve_context
from app.config import settings
from app.mcp.tools.generate_quiz import generate_quiz


def create_quiz(document_id: int, num_questions: int = 5, difficulty: str = "medium") -> dict:
    """Generate a multiple-choice quiz from document content.

    Args:
        document_id: ID of the source document.
        num_questions: Number of questions to generate (3-20).
        difficulty: Difficulty level: easy, medium, or hard.

    Returns:
        Dictionary with quiz details and status.
    """
    num_questions = max(3, min(20, num_questions))
    context = retrieve_context("important concepts facts details", document_id=document_id, top_k=10)
    if not context:
        return {"status": "error", "message": "No content found for this document"}

    prompt = f"""Create a {difficulty} difficulty multiple-choice quiz with exactly {num_questions} questions.

STUDY MATERIAL:
{context[:10000]}

Return ONLY a JSON array of questions. Each question object must have:
- "question": the question text
- "options": array of exactly 4 answer choices
- "correct_answer": the exact text of the correct option
- "explanation": brief explanation of why the answer is correct

Example format:
[
  {{
    "question": "What is...?",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "B",
    "explanation": "Because..."
  }}
]"""

    response = generate_content(
        prompt,
        system_instruction="You are an expert quiz creator. Generate accurate, educational multiple-choice questions. Return only valid JSON.",
        temperature=0.6,
    )

    try:
        questions = parse_json_response(response)
        if not isinstance(questions, list):
            return {"status": "error", "message": "Failed to parse quiz questions"}
    except (json.JSONDecodeError, ValueError) as e:
        return {"status": "error", "message": f"Failed to parse quiz: {e}"}

    title = f"Quiz ({difficulty.title()}, {num_questions} questions)"
    return generate_quiz(
        document_id=document_id,
        title=title,
        questions_json=json.dumps(questions),
    )


quiz_agent = Agent(
    model=settings.model_name,
    name="quiz_agent",
    description="Generates multiple-choice quizzes from study materials.",
    instruction="""You are the Quiz Agent for StudyMate AI.
Your role is to create educational multiple-choice quizzes from uploaded documents.
Use the create_quiz tool to generate quizzes with configurable difficulty
and number of questions. Ensure questions test understanding, not just memorization.""",
    tools=[create_quiz],
)

root_agent = quiz_agent
