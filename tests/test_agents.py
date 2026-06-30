"""Tests for ADK agents."""

import json
from unittest.mock import patch

import pytest

from app.agents.planner.agent import create_study_plan, planner_agent
from app.agents.notes.agent import generate_notes, notes_agent
from app.agents.quiz.agent import create_quiz, quiz_agent
from app.agents.flashcard.agent import create_flashcards, flashcard_agent
from app.agents.progress.agent import get_learning_progress, progress_agent, record_activity
from app.agents.utils import parse_json_response
from app.database import crud


def test_planner_agent_exists():
    assert planner_agent.name == "planner_agent"
    assert len(planner_agent.tools) == 1


def test_notes_agent_exists():
    assert notes_agent.name == "notes_agent"
    assert len(notes_agent.tools) == 1


def test_quiz_agent_exists():
    assert quiz_agent.name == "quiz_agent"
    assert len(quiz_agent.tools) == 1


def test_flashcard_agent_exists():
    assert flashcard_agent.name == "flashcard_agent"
    assert len(flashcard_agent.tools) == 1


def test_progress_agent_exists():
    assert progress_agent.name == "progress_agent"
    assert len(progress_agent.tools) == 2


def test_parse_json_array():
    text = 'Here are the questions:\n[{"question": "Q?", "options": ["A"], "correct_answer": "A"}]'
    result = parse_json_response(text)
    assert isinstance(result, list)
    assert result[0]["question"] == "Q?"


def test_parse_json_codeblock():
    text = '```json\n[{"front": "Q", "back": "A"}]\n```'
    result = parse_json_response(text)
    assert result[0]["front"] == "Q"


@patch("app.agents.planner.agent.retrieve_context")
@patch("app.agents.planner.agent.generate_content")
def test_create_study_plan(mock_gen, mock_ctx, db_session):
    mock_ctx.return_value = "Study material about photosynthesis."
    mock_gen.return_value = "## Study Plan\n1. Read chapter 1\n2. Practice quiz"

    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Biology")
    result = create_study_plan(doc.id, "Learn photosynthesis")
    assert result["status"] == "success"
    assert "plan_content" in result


@patch("app.agents.planner.agent.retrieve_context")
def test_create_study_plan_no_content(mock_ctx, db_session):
    mock_ctx.return_value = ""
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Empty")
    result = create_study_plan(doc.id)
    assert result["status"] == "error"


@patch("app.agents.notes.agent.retrieve_context")
@patch("app.agents.notes.agent.generate_content")
def test_generate_notes(mock_gen, mock_ctx, db_session):
    mock_ctx.return_value = "Content about cells."
    mock_gen.return_value = "## Cell Notes\n- Nucleus\n- Membrane"

    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Biology")
    result = generate_notes(doc.id)
    assert result["status"] == "success"
    assert "content" in result


@patch("app.agents.quiz.agent.retrieve_context")
@patch("app.agents.quiz.agent.generate_content")
def test_create_quiz(mock_gen, mock_ctx, db_session):
    mock_ctx.return_value = "Quiz material."
    mock_gen.return_value = json.dumps(
        [
            {
                "question": "What is X?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because",
            }
        ]
    )

    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    result = create_quiz(doc.id, num_questions=1)
    assert result["status"] == "success"


@patch("app.agents.flashcard.agent.retrieve_context")
@patch("app.agents.flashcard.agent.generate_content")
def test_create_flashcards(mock_gen, mock_ctx, db_session):
    mock_ctx.return_value = "Flashcard material."
    mock_gen.return_value = json.dumps(
        [{"front": "Term", "back": "Definition", "difficulty": "easy"}]
    )

    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    result = create_flashcards(doc.id, num_cards=1)
    assert result["status"] == "success"


def test_get_learning_progress(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    crud.track_progress(db_session, doc.id, "notes_generated")

    with patch("app.agents.progress.agent.generate_content") as mock_gen:
        mock_gen.return_value = "Great progress!"
        result = get_learning_progress()
        assert result["status"] == "success"
        assert "summary" in result
        assert "analysis" in result


def test_record_activity(db_session):
    doc = crud.create_document(db_session, "t.pdf", "/t.pdf", "pdf", "Test")
    result = record_activity(doc.id, "quiz_completed", score=90.0)
    assert result["status"] == "success"
