"""Text chunking utilities for RAG."""

from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split text into overlapping chunks for vector storage."""
    size = chunk_size or settings.chunk_size
    ovlp = overlap or settings.chunk_overlap

    if not text or not text.strip():
        return []

    text = text.strip()
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]

        if end < len(text):
            last_break = max(chunk.rfind("\n"), chunk.rfind(". "), chunk.rfind(" "))
            if last_break > size // 2:
                chunk = chunk[: last_break + 1]
                end = start + last_break + 1

        chunks.append(chunk.strip())
        start = end - ovlp if end < len(text) else end

    return [c for c in chunks if c]
