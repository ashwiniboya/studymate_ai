"""Progress API routes."""

from fastapi import APIRouter, Depends

from app.api.schemas import CreatePlanRequest, ProgressRecordResponse, StatusResponse
from app.database.crud import get_progress
from app.database.session import get_db
from app.services.agent_service import AgentService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/progress", tags=["progress"])
agent_service = AgentService()


@router.get("/summary", response_model=StatusResponse)
def get_progress_summary(document_id: int | None = None):
    """Get learning progress summary with AI analysis."""
    result = agent_service.get_progress(document_id)
    return StatusResponse(
        status=result["status"],
        message="Progress retrieved",
        data={k: v for k, v in result.items() if k != "status"},
    )


@router.get("/records", response_model=list[ProgressRecordResponse])
def list_progress_records(document_id: int | None = None, db: Session = Depends(get_db)):
    """List all progress records."""
    return get_progress(db, document_id)


@router.post("/plan", response_model=StatusResponse)
def create_study_plan(request: CreatePlanRequest):
    """Create a study plan using the Planner Agent."""
    result = agent_service.create_plan(request.document_id, request.goals)
    return StatusResponse(
        status=result["status"],
        message=result.get("message", ""),
        data={k: v for k, v in result.items() if k not in ("status", "message")},
    )
