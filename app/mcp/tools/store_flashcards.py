"""Store Flashcards tool - persists flashcards to the database."""

import json

import app.database.session as db_session
from app.database.crud import store_flashcards


def store_flashcards_tool(document_id: int, cards_json: str) -> dict:
    """Store flashcards for a document.

    Args:
        document_id: ID of the source document.
        cards_json: JSON string of flashcards, each with front, back, and optional difficulty.

    Returns:
        Dictionary with status and count of stored cards.
    """
    try:
        cards = json.loads(cards_json)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {e}"}

    if not isinstance(cards, list) or len(cards) == 0:
        return {"status": "error", "message": "Cards must be a non-empty list"}

    for i, card in enumerate(cards):
        if "front" not in card or "back" not in card:
            return {"status": "error", "message": f"Card {i + 1} missing front or back"}

    db = db_session.SessionLocal()
    try:
        created = store_flashcards(db, document_id=document_id, cards=cards)
        return {
            "status": "success",
            "count": len(created),
            "flashcard_ids": [fc.id for fc in created],
            "message": f"Stored {len(created)} flashcards",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to store flashcards: {e}"}
    finally:
        db.close()
