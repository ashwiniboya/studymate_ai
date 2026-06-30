"""Notes API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import GenerateNotesRequest, NoteResponse, StatusResponse
from app.database.crud import get_note, get_notes
from app.database.session import get_db
from app.services.agent_service import AgentService

router = APIRouter(prefix="/notes", tags=["notes"])
agent_service = AgentService()


@router.post("/generate", response_model=StatusResponse)
def generate_study_notes(request: GenerateNotesRequest):
    """Generate study notes from a document using the Notes Agent."""
    result = agent_service.generate_notes(request.document_id, request.focus_area)
    return StatusResponse(
        status=result["status"],
        message=result.get("message", ""),
        data={k: v for k, v in result.items() if k not in ("status", "message")},
    )


@router.get("/", response_model=list[NoteResponse])
def list_notes(document_id: int | None = None, db: Session = Depends(get_db)):
    """List all notes, optionally filtered by document."""
    return get_notes(db, document_id)


@router.get("/{note_id}", response_model=NoteResponse)
def get_note_by_id(note_id: int, db: Session = Depends(get_db)):
    """Get a specific note by ID."""
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
