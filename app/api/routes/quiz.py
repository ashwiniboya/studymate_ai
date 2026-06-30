"""Quiz API routes."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import CreateQuizRequest, QuizQuestionResponse, QuizResponse, QuizSubmitRequest, StatusResponse
from app.database.crud import get_quiz, get_quizzes, track_progress
from app.database.session import get_db
from app.services.agent_service import AgentService

router = APIRouter(prefix="/quiz", tags=["quiz"])
agent_service = AgentService()


@router.post("/generate", response_model=StatusResponse)
def generate_quiz(request: CreateQuizRequest):
    """Generate a quiz from a document using the Quiz Agent."""
    result = agent_service.create_quiz(
        request.document_id, request.num_questions, request.difficulty
    )
    return StatusResponse(
        status=result["status"],
        message=result.get("message", ""),
        data={k: v for k, v in result.items() if k not in ("status", "message")},
    )


@router.get("/", response_model=list[QuizResponse])
def list_quizzes(document_id: int | None = None, db: Session = Depends(get_db)):
    """List all quizzes."""
    quizzes = get_quizzes(db, document_id)
    result = []
    for q in quizzes:
        questions = [
            QuizQuestionResponse(
                id=qq.id,
                question=qq.question,
                options=json.loads(qq.options),
                correct_answer=qq.correct_answer,
                explanation=qq.explanation,
            )
            for qq in q.questions
        ]
        result.append(
            QuizResponse(
                id=q.id,
                document_id=q.document_id,
                title=q.title,
                questions=questions,
                created_at=q.created_at,
            )
        )
    return result


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    """Get a quiz with all questions."""
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = [
        QuizQuestionResponse(
            id=qq.id,
            question=qq.question,
            options=json.loads(qq.options),
            correct_answer=qq.correct_answer,
            explanation=qq.explanation,
        )
        for qq in quiz.questions
    ]
    return QuizResponse(
        id=quiz.id,
        document_id=quiz.document_id,
        title=quiz.title,
        questions=questions,
        created_at=quiz.created_at,
    )


@router.post("/{quiz_id}/submit", response_model=StatusResponse)
def submit_quiz(quiz_id: int, request: QuizSubmitRequest, db: Session = Depends(get_db)):
    """Submit quiz answers and get score."""
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    correct = 0
    total = len(quiz.questions)
    results = []

    for qq in quiz.questions:
        user_answer = request.answers.get(str(qq.id), "")
        is_correct = user_answer.strip().lower() == qq.correct_answer.strip().lower()
        if is_correct:
            correct += 1
        results.append(
            {
                "question_id": qq.id,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": qq.correct_answer,
                "explanation": qq.explanation,
            }
        )

    score = round((correct / total) * 100, 1) if total > 0 else 0
    track_progress(
        db,
        document_id=quiz.document_id,
        activity_type="quiz_completed",
        score=score,
        details=f"Quiz '{quiz.title}': {correct}/{total} correct",
    )

    return StatusResponse(
        status="success",
        message=f"Score: {correct}/{total} ({score}%)",
        data={"score": score, "correct": correct, "total": total, "results": results},
    )
