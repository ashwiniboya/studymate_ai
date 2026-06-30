"""Integration tests for end-to-end workflows."""

import io
from unittest.mock import patch

from app.database import crud


@patch("app.agents.notes.agent.generate_content")
@patch("app.agents.notes.agent.retrieve_context")
def test_upload_and_generate_notes_flow(mock_ctx, mock_gen, client, db_session):
    mock_ctx.return_value = "Biology content about cells and organelles."
    mock_gen.return_value = "## Cell Biology\n- Nucleus controls cell activities\n- Mitochondria produce energy"

    content = (
        "The cell is the basic unit of life. The nucleus contains genetic material. "
        "Mitochondria are the powerhouses of the cell."
    )
    upload_resp = client.post(
        "/api/documents/upload",
        files={"file": ("biology.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    assert upload_resp.json()["status"] == "success"
    doc_id = upload_resp.json()["data"]["document_id"]

    notes_resp = client.post(
        "/api/notes/generate",
        json={"document_id": doc_id, "focus_area": "Cell Biology"},
    )
    assert notes_resp.json()["status"] == "success"

    notes_list = client.get("/api/notes/").json()
    assert len(notes_list) >= 1


@patch("app.agents.quiz.agent.generate_content")
@patch("app.agents.quiz.agent.retrieve_context")
def test_upload_and_quiz_flow(mock_ctx, mock_gen, client):
    import json

    mock_ctx.return_value = "Quiz content."
    mock_gen.return_value = json.dumps(
        [
            {
                "question": "What is the basic unit of life?",
                "options": ["Atom", "Cell", "Molecule", "Organ"],
                "correct_answer": "Cell",
                "explanation": "The cell is the basic unit of life.",
            },
            {
                "question": "What contains genetic material?",
                "options": ["Membrane", "Nucleus", "Cytoplasm", "Ribosome"],
                "correct_answer": "Nucleus",
                "explanation": "The nucleus contains DNA.",
            },
            {
                "question": "What produces energy in the cell?",
                "options": ["Mitochondria", "Golgi", "Lysosome", "Cell wall"],
                "correct_answer": "Mitochondria",
                "explanation": "Mitochondria are the powerhouse of the cell.",
            },
        ]
    )

    content = "The cell is the basic unit of life."
    upload_resp = client.post(
        "/api/documents/upload",
        files={"file": ("bio.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    doc_id = upload_resp.json()["data"]["document_id"]

    quiz_resp = client.post(
        "/api/quiz/generate",
        json={"document_id": doc_id, "num_questions": 3, "difficulty": "easy"},
    )
    assert quiz_resp.json()["status"] == "success"

    quizzes = client.get("/api/quiz/").json()
    assert len(quizzes) >= 1


def test_document_lifecycle(client, db_session):
    doc = crud.create_document(db_session, "test.txt", "/tmp/test.txt", "txt", "Lifecycle Test")
    crud.save_note(db_session, doc.id, "Notes", "Content")
    crud.store_flashcards(db_session, doc.id, [{"front": "Q", "back": "A"}])
    crud.track_progress(db_session, doc.id, "notes_generated")

    docs = client.get("/api/documents/").json()
    assert any(d["id"] == doc.id for d in docs)

    notes = client.get("/api/notes/").json()
    assert len(notes) >= 1

    cards = client.get("/api/flashcards/").json()
    assert len(cards) >= 1

    records = client.get("/api/progress/records").json()
    assert len(records) >= 1

    delete_resp = client.delete(f"/api/documents/{doc.id}")
    assert delete_resp.json()["status"] == "success"
