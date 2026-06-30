"""Track Progress tool - records learning activity."""

import app.database.session as db_session
from app.database.crud import track_progress


def track_progress_tool(
    document_id: int,
    activity_type: str,
    score: float = 0.0,
    details: str = "",
) -> dict:
    """Track a learning activity for progress monitoring.

    Args:
        document_id: ID of the related document.
        activity_type: Type of activity (notes_generated, quiz_completed, flashcard_reviewed, etc.).
        score: Optional score (0-100) for the activity.
        details: Optional details about the activity.

    Returns:
        Dictionary with status and progress record ID.
    """
    valid_types = {
        "notes_generated",
        "quiz_completed",
        "flashcard_reviewed",
        "document_uploaded",
        "chat_session",
        "study_plan_created",
    }
    if activity_type not in valid_types:
        return {
            "status": "error",
            "message": f"Invalid activity type. Must be one of: {', '.join(sorted(valid_types))}",
        }

    db = db_session.SessionLocal()
    try:
        record = track_progress(
            db,
            document_id=document_id,
            activity_type=activity_type,
            score=min(max(score, 0.0), 100.0),
            details=details,
        )
        return {
            "status": "success",
            "progress_id": record.id,
            "activity_type": record.activity_type,
            "score": record.score,
            "message": f"Progress tracked: {activity_type}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to track progress: {e}"}
    finally:
        db.close()
