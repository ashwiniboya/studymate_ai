"""Health check routes."""

from fastapi import APIRouter

from app.config import settings
from app.rag.vector_store import get_vector_store

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Application health check endpoint."""
    try:
        store = get_vector_store()
        chunk_count = store.total_chunks
    except Exception:
        chunk_count = 0

    return {
        "status": "healthy",
        "app": "StudyMate AI",
        "version": "1.0.0",
        "model": settings.model_name,
        "vector_chunks": chunk_count,
    }
