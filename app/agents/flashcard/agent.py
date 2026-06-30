"""Flashcard Agent - generates study flashcards."""

import json

from google.adk.agents.llm_agent import Agent

from app.agents.utils import generate_content, parse_json_response, retrieve_context
from app.config import settings
from app.mcp.tools.store_flashcards import store_flashcards_tool


def create_flashcards(document_id: int, num_cards: int = 10) -> dict:
    """Generate flashcards from document content.

    Args:
        document_id: ID of the source document.
        num_cards: Number of flashcards to generate (5-30).

    Returns:
        Dictionary with flashcard details and status.
    """
    num_cards = max(5, min(30, num_cards))
    context = retrieve_context("key terms definitions concepts facts", document_id=document_id, top_k=10)
    if not context:
        return {"status": "error", "message": "No content found for this document"}

    prompt = f"""Create exactly {num_cards} study flashcards from this material.

STUDY MATERIAL:
{context[:10000]}

Return ONLY a JSON array of flashcard objects. Each must have:
- "front": question or term (concise)
- "back": answer or definition (clear and complete)
- "difficulty": "easy", "medium", or "hard"

Example:
[
  {{"front": "What is photosynthesis?", "back": "The process by which plants convert light energy into chemical energy.", "difficulty": "medium"}}
]"""

    response = generate_content(
        prompt,
        system_instruction="You are an expert at creating effective study flashcards. Focus on key concepts, terms, and facts. Return only valid JSON.",
        temperature=0.5,
    )

    try:
        cards = parse_json_response(response)
        if not isinstance(cards, list):
            return {"status": "error", "message": "Failed to parse flashcards"}
    except (json.JSONDecodeError, ValueError) as e:
        return {"status": "error", "message": f"Failed to parse flashcards: {e}"}

    return store_flashcards_tool(document_id=document_id, cards_json=json.dumps(cards))


flashcard_agent = Agent(
    model=settings.model_name,
    name="flashcard_agent",
    description="Generates study flashcards from uploaded documents.",
    instruction="""You are the Flashcard Agent for StudyMate AI.
Your role is to create effective study flashcards from uploaded documents.
Use the create_flashcards tool to generate cards with clear front/back content
and appropriate difficulty levels. Focus on the most important concepts.""",
    tools=[create_flashcards],
)

root_agent = flashcard_agent
