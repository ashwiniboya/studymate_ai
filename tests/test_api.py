"""Tests for FastAPI endpoints."""

import io
from unittest.mock import patch

from app.database import crud


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "StudyMate AI"


def test_list_documents_empty(client):
    response = client.get("/api/documents/")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_txt_file(client, sample_txt_file):
    with open(sample_txt_file, "rb") as f:
        response = client.post(
            "/api/documents/upload",
            files={"file": ("biology.txt", f, "text/plain")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["document_id"] is not None


def test_upload_unsupported_file(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("test.xyz", io.BytesIO(b"data"), "application/octet-stream")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"


def test_get_document(client, db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test Doc")
    response = client.get(f"/api/documents/{doc.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Doc"


def test_get_document_not_found(client):
    response = client.get("/api/documents/999")
    assert response.status_code == 404


def test_list_notes_empty(client):
    response = client.get("/api/notes/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_flashcards_empty(client):
    response = client.get("/api/flashcards/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_quizzes_empty(client):
    response = client.get("/api/quiz/")
    assert response.status_code == 200
    assert response.json() == []


def test_progress_records_empty(client):
    response = client.get("/api/progress/records")
    assert response.status_code == 200
    assert response.json() == []


@patch("app.api.routes.chat.agent_service.chat")
def test_chat_endpoint(mock_chat, client):
    mock_chat.return_value = {
        "status": "success",
        "response": "Photosynthesis converts light to energy.",
        "context_used": True,
    }
    response = client.post(
        "/api/chat/",
        json={"message": "What is photosynthesis?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "photosynthesis" in data["response"].lower()


@patch("app.api.routes.notes.agent_service.generate_notes")
def test_generate_notes_endpoint(mock_gen, client, db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    mock_gen.return_value = {
        "status": "success",
        "note_id": 1,
        "content": "## Notes",
        "message": "Notes saved",
    }
    response = client.post(
        "/api/notes/generate",
        json={"document_id": doc.id, "focus_area": ""},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_submit_quiz(client, db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    quiz = crud.create_quiz(
        db_session,
        doc.id,
        "Test Quiz",
        [
            {
                "question": "Q1?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because A",
            },
            {
                "question": "Q2?",
                "options": ["X", "Y", "Z", "W"],
                "correct_answer": "Y",
                "explanation": "Because Y",
            },
        ],
    )
    q_ids = [q.id for q in quiz.questions]
    response = client.post(
        f"/api/quiz/{quiz.id}/submit",
        json={"answers": {str(q_ids[0]): "A", str(q_ids[1]): "Y"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["score"] == 100.0


def test_flashcard_review(client, db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    cards = crud.store_flashcards(db_session, doc.id, [{"front": "Q", "back": "A"}])
    response = client.post(
        f"/api/flashcards/{cards[0].id}/review",
        json={"correct": True},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_frontend_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "StudyMate AI" in response.text
