"""Tests for database CRUD operations."""

from app.database import crud


def test_create_and_get_document(db_session):
    doc = crud.create_document(
        db_session,
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        file_type="pdf",
        title="Test Document",
        content_preview="Preview text",
    )
    assert doc.id is not None
    assert doc.title == "Test Document"

    fetched = crud.get_document(db_session, doc.id)
    assert fetched is not None
    assert fetched.filename == "test.pdf"


def test_list_documents(db_session):
    crud.create_document(
        db_session, "a.pdf", "/a.pdf", "pdf", "Doc A"
    )
    crud.create_document(
        db_session, "b.pdf", "/b.pdf", "pdf", "Doc B"
    )
    docs = crud.list_documents(db_session)
    assert len(docs) == 2


def test_save_and_get_notes(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    note = crud.save_note(db_session, doc.id, "My Notes", "Content here")
    assert note.id is not None

    notes = crud.get_notes(db_session, doc.id)
    assert len(notes) == 1
    assert notes[0].title == "My Notes"


def test_store_flashcards(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    cards = crud.store_flashcards(
        db_session,
        doc.id,
        [{"front": "Q1", "back": "A1"}, {"front": "Q2", "back": "A2"}],
    )
    assert len(cards) == 2
    assert cards[0].front == "Q1"


def test_create_quiz(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    quiz = crud.create_quiz(
        db_session,
        doc.id,
        "Test Quiz",
        [
            {
                "question": "What is photosynthesis?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because...",
            }
        ],
    )
    assert quiz.id is not None
    assert len(quiz.questions) == 1


def test_track_progress(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    record = crud.track_progress(
        db_session, doc.id, "quiz_completed", score=85.0, details="8/10 correct"
    )
    assert record.score == 85.0
    assert record.activity_type == "quiz_completed"


def test_progress_summary(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    crud.track_progress(db_session, doc.id, "notes_generated")
    crud.save_note(db_session, doc.id, "Notes", "Content")

    summary = crud.get_progress_summary(db_session)
    assert summary["total_documents"] == 1
    assert summary["total_notes"] == 1
    assert summary["total_activities"] == 1


def test_delete_document(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    assert crud.delete_document(db_session, doc.id) is True
    assert crud.get_document(db_session, doc.id) is None
