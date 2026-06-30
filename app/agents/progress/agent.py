"""Progress Agent - tracks and analyzes learning progress."""

from google.adk.agents.llm_agent import Agent

import app.database.session as db_session
from app.agents.utils import generate_content
from app.config import settings
from app.database.crud import get_progress, get_progress_summary
from app.mcp.tools.track_progress import track_progress_tool


def get_learning_progress(document_id: int | None = None) -> dict:
    """Get learning progress summary and analysis.

    Args:
        document_id: Optional document ID to filter progress.

    Returns:
        Dictionary with progress data and AI analysis.
    """
    db = db_session.SessionLocal()
    try:
        summary = get_progress_summary(db)
        records = get_progress(db, document_id=document_id)

        recent = [
            {
                "activity": r.activity_type,
                "score": r.score,
                "details": r.details,
                "date": r.created_at.isoformat() if r.created_at else "",
            }
            for r in records[:10]
        ]

        analysis_prompt = f"""Analyze this student's learning progress and provide encouraging, actionable feedback.

PROGRESS SUMMARY:
- Documents: {summary['total_documents']}
- Notes created: {summary['total_notes']}
- Flashcards: {summary['total_flashcards']}
- Quizzes taken: {summary['total_quizzes']}
- Total activities: {summary['total_activities']}
- Average score: {summary['average_score']}%
- Activity breakdown: {summary['activity_breakdown']}

RECENT ACTIVITIES:
{recent}

Provide:
1. Overall progress assessment
2. Strengths identified
3. Areas for improvement
4. Recommended next steps"""

        analysis = generate_content(
            analysis_prompt,
            system_instruction="You are a supportive learning coach. Provide encouraging, specific feedback on student progress.",
            temperature=0.6,
        )

        return {
            "status": "success",
            "summary": summary,
            "recent_activities": recent,
            "analysis": analysis,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def record_activity(
    document_id: int,
    activity_type: str,
    score: float = 0.0,
    details: str = "",
) -> dict:
    """Record a learning activity for progress tracking.

    Args:
        document_id: ID of the related document.
        activity_type: Type of activity completed.
        score: Optional score (0-100).
        details: Optional activity details.

    Returns:
        Dictionary with tracking status.
    """
    return track_progress_tool(document_id, activity_type, score, details)


progress_agent = Agent(
    model=settings.model_name,
    name="progress_agent",
    description="Tracks and analyzes student learning progress.",
    instruction="""You are the Progress Agent for StudyMate AI.
Your role is to track learning activities and provide insightful progress analysis.
Use get_learning_progress to retrieve and analyze progress data.
Use record_activity to log new learning activities.
Provide encouraging, actionable feedback to help students improve.""",
    tools=[get_learning_progress, record_activity],
)

root_agent = progress_agent
