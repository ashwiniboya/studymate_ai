"""Tests for MCP tools."""

import json
import tempfile
from pathlib import Path

from app.mcp.tools.parse_text import parse_text
from app.mcp.tools.read_docx import read_docx
from app.mcp.tools.read_pdf import read_pdf
from app.mcp.tools.save_notes import save_notes
from app.mcp.tools.generate_quiz import generate_quiz
from app.mcp.tools.store_flashcards import store_flashcards_tool
from app.mcp.tools.track_progress import track_progress_tool
from app.database import crud


def test_parse_text():
    result = parse_text("  Hello   world.\n\n\nThis is a test.  ")
    assert result["status"] == "success"
    assert result["word_count"] == 6
    assert "Hello world" in result["text"]


def test_parse_text_empty():
    result = parse_text("")
    assert result["status"] == "error"


def test_read_pdf_not_found():
    result = read_pdf("/nonexistent/file.pdf")
    assert result["status"] == "error"


def test_read_docx_not_found():
    result = read_docx("/nonexistent/file.docx")
    assert result["status"] == "error"


def test_save_notes(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    result = save_notes(doc.id, "Test Notes", "Note content here")
    assert result["status"] == "success"
    assert "note_id" in result


def test_save_notes_empty(db_session):
    result = save_notes(1, "", "")
    assert result["status"] == "error"


def test_generate_quiz(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    questions = json.dumps(
        [
            {
                "question": "Test?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because",
            }
        ]
    )
    result = generate_quiz(doc.id, "Test Quiz", questions)
    assert result["status"] == "success"
    assert result["question_count"] == 1


def test_store_flashcards(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    cards = json.dumps([{"front": "Q", "back": "A"}])
    result = store_flashcards_tool(doc.id, cards)
    assert result["status"] == "success"
    assert result["count"] == 1


def test_track_progress(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    result = track_progress_tool(doc.id, "document_uploaded", details="Test upload")
    assert result["status"] == "success"


def test_track_progress_invalid_type(db_session):
    result = track_progress_tool(1, "invalid_type")
    assert result["status"] == "error"
