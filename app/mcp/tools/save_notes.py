"""Save Notes tool - persists study notes to the database."""

import app.database.session as db_session
from app.database.crud import save_note


def save_notes(document_id: int, title: str, content: str) -> dict:
    """Save study notes for a document.

    Args:
        document_id: ID of the source document.
        title: Title of the notes.
        content: Full notes content in markdown format.

    Returns:
        Dictionary with status and saved note ID.
    """
    if not content or not content.strip():
        return {"status": "error", "message": "Notes content cannot be empty"}
    if not title or not title.strip():
        return {"status": "error", "message": "Notes title cannot be empty"}

    db = db_session.SessionLocal()
    try:
        note = save_note(db, document_id=document_id, title=title.strip(), content=content.strip())
        return {
            "status": "success",
            "note_id": note.id,
            "title": note.title,
            "message": f"Notes saved successfully (ID: {note.id})",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save notes: {e}"}
    finally:
        db.close()
