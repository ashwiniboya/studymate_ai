"""Tests for text chunking."""

from app.rag.chunker import chunk_text


def test_chunk_short_text():
    text = "Short text."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_chunk_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_long_text():
    text = "Word " * 500
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 250


def test_chunk_preserves_content():
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunk_text(text, chunk_size=1000)
    combined = " ".join(chunks)
    assert "First sentence" in combined
    assert "Third sentence" in combined
