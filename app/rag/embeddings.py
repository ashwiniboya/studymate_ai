"""Embedding generation for RAG."""

import hashlib
import random
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the sentence-transformer model lazily."""
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(settings.embedding_model)
    except Exception:
        # In constrained serverless runtimes (for example Vercel), the
        # transformer stack may be unavailable or too heavy to initialize.
        return None


def _fallback_embedding(text: str, dims: int = 384) -> list[float]:
    """Deterministic lightweight embedding fallback for serverless runtimes."""
    seed = int(hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(dims)]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    if not texts:
        return []
    model = get_embedding_model()
    if model is None:
        return [_fallback_embedding(text) for text in texts]

    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings


def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query."""
    return embed_texts([query])[0]
