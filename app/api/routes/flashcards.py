"""Flashcards API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import CreateFlashcardsRequest, FlashcardResponse, FlashcardReviewRequest, StatusResponse
from app.database.crud import get_flashcards, update_flashcard_review
from app.database.session import get_db
from app.services.agent_service import AgentService

router = APIRouter(prefix="/flashcards", tags=["flashcards"])
agent_service = AgentService()


@router.post("/generate", response_model=StatusResponse)
def generate_flashcards(request: CreateFlashcardsRequest):
    """Generate flashcards from a document using the Flashcard Agent."""
    result = agent_service.create_flashcards(request.document_id, request.num_cards)
    return StatusResponse(
        status=result["status"],
        message=result.get("message", ""),
        data={k: v for k, v in result.items() if k not in ("status", "message")},
    )


@router.get("/", response_model=list[FlashcardResponse])
def list_flashcards(document_id: int | None = None, db: Session = Depends(get_db)):
    """List all flashcards."""
    return get_flashcards(db, document_id)


@router.post("/{flashcard_id}/review", response_model=StatusResponse)
def review_flashcard(
    flashcard_id: int,
    request: FlashcardReviewRequest,
    db: Session = Depends(get_db),
):
    """Record a flashcard review result."""
    fc = update_flashcard_review(db, flashcard_id, request.correct)
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    from app.database.crud import track_progress

    track_progress(
        db,
        document_id=fc.document_id,
        activity_type="flashcard_reviewed",
        score=100.0 if request.correct else 0.0,
        details=f"Flashcard reviewed: {'correct' if request.correct else 'incorrect'}",
    )

    return StatusResponse(
        status="success",
        message="Review recorded",
        data={"times_reviewed": fc.times_reviewed, "times_correct": fc.times_correct},
    )
