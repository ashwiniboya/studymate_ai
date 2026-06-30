"""Chat API routes."""

from fastapi import APIRouter

from app.api.schemas import ChatRequest, ChatResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/chat", tags=["chat"])
agent_service = AgentService()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Ask questions about uploaded study materials."""
    result = agent_service.chat(request.message, request.document_id)
    return ChatResponse(
        response=result.get("response", "Sorry, I could not process your request."),
        context_used=result.get("context_used", False),
    )
