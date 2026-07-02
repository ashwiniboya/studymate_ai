"""Embedding generation for RAG using Gemini text-embedding-004."""

import hashlib
import random

from app.config import settings

EMBEDDING_DIMS = 768


def _gemini_embed_texts(texts: list[str]) -> list[list[float]]:
    from google import genai
    client = genai.Client(api_key=settings.google_api_key)
    result = client.models.embed_content(
        model=settings.embedding_model,
        contents=texts,
    )
    return [e.values for e in result.embeddings]


def _fallback_embedding(text: str, dims: int = EMBEDDING_DIMS) -> list[float]:
    seed = int(hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(dims)]


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    try:
        return _gemini_embed_texts(texts)
    except Exception as e:
        print(f"[embeddings] Gemini API failed, using fallback: {e}")
        return [_fallback_embedding(t) for t in texts]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]