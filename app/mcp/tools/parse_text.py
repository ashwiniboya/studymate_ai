"""Parse Text tool - cleans and structures raw text."""

import re


def parse_text(text: str, max_length: int = 50000) -> dict:
    """Clean, normalize, and structure raw text for processing.

    Args:
        text: Raw text content to parse.
        max_length: Maximum character length to return.

    Returns:
        Dictionary with cleaned text, word count, and summary stats.
    """
    if not text or not text.strip():
        return {"status": "error", "message": "No text provided"}

    cleaned = text.strip()
    cleaned = re.sub(r"\r\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r" \n", "\n", cleaned)

    words = cleaned.split()
    word_count = len(words)
    sentences = [s.strip() for s in re.split(r"[.!?]+", cleaned) if s.strip()]

    truncated = cleaned[:max_length]
    was_truncated = len(cleaned) > max_length

    return {
        "status": "success",
        "text": truncated,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "char_count": len(cleaned),
        "truncated": was_truncated,
        "preview": " ".join(words[:50]) + ("..." if word_count > 50 else ""),
    }
