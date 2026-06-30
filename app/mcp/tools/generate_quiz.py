"""Generate Quiz tool - creates and stores quiz questions."""

import json

import app.database.session as db_session
from app.database.crud import create_quiz


def generate_quiz(
    document_id: int,
    title: str,
    questions_json: str,
) -> dict:
    """Generate and store a quiz from structured question data.

    Args:
        document_id: ID of the source document.
        title: Quiz title.
        questions_json: JSON string of questions, each with:
            question, options (list), correct_answer, explanation (optional).

    Returns:
        Dictionary with status and quiz ID.
    """
    try:
        questions = json.loads(questions_json)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {e}"}

    if not isinstance(questions, list) or len(questions) == 0:
        return {"status": "error", "message": "Questions must be a non-empty list"}

    for i, q in enumerate(questions):
        required = ["question", "options", "correct_answer"]
        missing = [f for f in required if f not in q]
        if missing:
            return {"status": "error", "message": f"Question {i + 1} missing fields: {missing}"}

    db = db_session.SessionLocal()
    try:
        quiz = create_quiz(db, document_id=document_id, title=title, questions=questions)
        return {
            "status": "success",
            "quiz_id": quiz.id,
            "title": quiz.title,
            "question_count": len(questions),
            "message": f"Quiz created with {len(questions)} questions (ID: {quiz.id})",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to create quiz: {e}"}
    finally:
        db.close()
