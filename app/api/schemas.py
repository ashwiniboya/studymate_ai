"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: int
    filename: str
    title: str
    file_type: str
    content_preview: str
    chunk_count: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class NoteResponse(BaseModel):
    id: int
    document_id: int
    title: str
    content: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class FlashcardResponse(BaseModel):
    id: int
    document_id: int
    front: str
    back: str
    difficulty: str
    times_reviewed: int
    times_correct: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class QuizQuestionResponse(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_answer: str
    explanation: str

    model_config = {"from_attributes": True}


class QuizResponse(BaseModel):
    id: int
    document_id: int
    title: str
    questions: list[QuizQuestionResponse] = []
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProgressRecordResponse(BaseModel):
    id: int
    document_id: int
    activity_type: str
    score: float
    details: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    document_id: int | None = None


class ChatResponse(BaseModel):
    response: str
    context_used: bool = False


class GenerateNotesRequest(BaseModel):
    document_id: int
    focus_area: str = ""


class CreateQuizRequest(BaseModel):
    document_id: int
    num_questions: int = Field(default=5, ge=3, le=20)
    difficulty: str = "medium"


class CreateFlashcardsRequest(BaseModel):
    document_id: int
    num_cards: int = Field(default=10, ge=5, le=30)


class CreatePlanRequest(BaseModel):
    document_id: int
    goals: str = ""


class QuizSubmitRequest(BaseModel):
    answers: dict[str, str]


class FlashcardReviewRequest(BaseModel):
    correct: bool


class StatusResponse(BaseModel):
    status: str
    message: str = ""
    data: dict[str, Any] | None = None
