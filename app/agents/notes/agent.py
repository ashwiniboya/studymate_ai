"""Notes Agent - generates structured study notes."""

from google.adk.agents.llm_agent import Agent

from app.agents.utils import generate_content, retrieve_context
from app.config import settings
from app.mcp.tools.save_notes import save_notes


def generate_notes(document_id: int, focus_area: str = "") -> dict:
    """Generate structured study notes from a document.

    Args:
        document_id: ID of the source document.
        focus_area: Optional topic to focus notes on.

    Returns:
        Dictionary with generated notes and status.
    """
    query = focus_area if focus_area else "main concepts definitions key points summary"
    context = retrieve_context(query, document_id=document_id, top_k=8)
    if not context:
        return {"status": "error", "message": "No content found for this document"}

    prompt = f"""Create comprehensive study notes from this material.

STUDY MATERIAL:
{context[:10000]}

{f"FOCUS AREA: {focus_area}" if focus_area else ""}

Generate well-structured notes with:
- Main topic headings (##)
- Key concepts and definitions
- Important formulas or facts (if any)
- Summary bullet points
- Connections between concepts

Use clear markdown formatting."""

    notes_content = generate_content(
        prompt,
        system_instruction="You are an expert note-taker. Create clear, organized study notes that help students learn effectively.",
        temperature=0.4,
    )

    title = f"Study Notes{' - ' + focus_area if focus_area else ''}"
    result = save_notes(document_id=document_id, title=title, content=notes_content)

    if result["status"] == "success":
        from app.database.session import SessionLocal
        from app.database.crud import track_progress

        db = SessionLocal()
        try:
            track_progress(
                db,
                document_id=document_id,
                activity_type="notes_generated",
                details=f"Notes generated: {title}",
            )
        finally:
            db.close()

    return {**result, "content": notes_content}


notes_agent = Agent(
    model=settings.model_name,
    name="notes_agent",
    description="Generates structured study notes from uploaded documents.",
    instruction="""You are the Notes Agent for StudyMate AI.
Your role is to generate clear, well-organized study notes from uploaded documents.
Use the generate_notes tool to create comprehensive notes with headings,
key concepts, definitions, and summaries. You can focus on specific topics
when the student requests it.""",
    tools=[generate_notes],
)

root_agent = notes_agent
