"""Shared utilities for ADK agents."""

import json
import os
from typing import Any

from google import genai
from google.genai import types

from app.config import settings
from app.rag.vector_store import get_vector_store


def get_genai_client() -> genai.Client:
    """Create a Gemini API client."""
    api_key = settings.google_api_key or os.environ.get("GOOGLE_API_KEY", "")
    return genai.Client(api_key=api_key)


def generate_content(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.7,
) -> str:
    """Generate text using Gemini model."""
    client = get_genai_client()
    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction or None,
    )
    response = client.models.generate_content(
        model=settings.model_name,
        contents=prompt,
        config=config,
    )
    return response.text or ""


def retrieve_context(query: str, document_id: int | None = None, top_k: int = 5) -> str:
    """Retrieve relevant document chunks for RAG context."""
    store = get_vector_store()
    chunks = store.search(query, document_id=document_id, top_k=top_k)
    if not chunks:
        return ""
    return "\n\n---\n\n".join(c["text"] for c in chunks)


def parse_json_response(text: str) -> Any:
    """Extract and parse JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    return json.loads(text)
