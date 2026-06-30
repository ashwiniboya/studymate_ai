"""Database CRUD operations."""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import (
    Document,
    Flashcard,
    Note,
    ProgressRecord,
    Quiz,
    QuizQuestion,
    StudyPlan,
)


# --- Documents ---


def create_document(
    db: Session,
    filename: str,
    file_path: str,
    file_type: str,
    title: str,
    content_preview: str = "",
    chunk_count: int = 0,
) -> Document:
    doc = Document(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        title=title,
        content_preview=content_preview,
        chunk_count=chunk_count,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, document_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def delete_document(db: Session, document_id: int) -> bool:
    doc = get_document(db, document_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True


# --- Notes ---


def save_note(db: Session, document_id: int, title: str, content: str) -> Note:
    note = Note(document_id=document_id, title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes(db: Session, document_id: int | None = None) -> list[Note]:
    query = db.query(Note)
    if document_id is not None:
        query = query.filter(Note.document_id == document_id)
    return query.order_by(Note.created_at.desc()).all()


def get_note(db: Session, note_id: int) -> Note | None:
    return db.query(Note).filter(Note.id == note_id).first()


# --- Flashcards ---


def store_flashcards(
    db: Session, document_id: int, cards: list[dict[str, str]]
) -> list[Flashcard]:
    created = []
    for card in cards:
        fc = Flashcard(
            document_id=document_id,
            front=card["front"],
            back=card["back"],
            difficulty=card.get("difficulty", "medium"),
        )
        db.add(fc)
        created.append(fc)
    db.commit()
    for fc in created:
        db.refresh(fc)
    return created


def get_flashcards(db: Session, document_id: int | None = None) -> list[Flashcard]:
    query = db.query(Flashcard)
    if document_id is not None:
        query = query.filter(Flashcard.document_id == document_id)
    return query.order_by(Flashcard.created_at.desc()).all()


def update_flashcard_review(db: Session, flashcard_id: int, correct: bool) -> Flashcard | None:
    fc = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not fc:
        return None
    fc.times_reviewed += 1
    if correct:
        fc.times_correct += 1
    db.commit()
    db.refresh(fc)
    return fc


# --- Quizzes ---


def create_quiz(
    db: Session,
    document_id: int,
    title: str,
    questions: list[dict[str, Any]],
) -> Quiz:
    quiz = Quiz(document_id=document_id, title=title)
    db.add(quiz)
    db.flush()
    for q in questions:
        qq = QuizQuestion(
            quiz_id=quiz.id,
            question=q["question"],
            options=json.dumps(q["options"]),
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation", ""),
        )
        db.add(qq)
    db.commit()
    db.refresh(quiz)
    return quiz


def get_quizzes(db: Session, document_id: int | None = None) -> list[Quiz]:
    query = db.query(Quiz)
    if document_id is not None:
        query = query.filter(Quiz.document_id == document_id)
    return query.order_by(Quiz.created_at.desc()).all()


def get_quiz(db: Session, quiz_id: int) -> Quiz | None:
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


# --- Progress ---


def track_progress(
    db: Session,
    document_id: int,
    activity_type: str,
    score: float = 0.0,
    details: str = "",
) -> ProgressRecord:
    record = ProgressRecord(
        document_id=document_id,
        activity_type=activity_type,
        score=score,
        details=details,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_progress(db: Session, document_id: int | None = None) -> list[ProgressRecord]:
    query = db.query(ProgressRecord)
    if document_id is not None:
        query = query.filter(ProgressRecord.document_id == document_id)
    return query.order_by(ProgressRecord.created_at.desc()).all()


def get_progress_summary(db: Session) -> dict[str, Any]:
    records = db.query(ProgressRecord).all()
    docs = db.query(Document).count()
    notes_count = db.query(Note).count()
    flashcards_count = db.query(Flashcard).count()
    quizzes_count = db.query(Quiz).count()

    activity_counts: dict[str, int] = {}
    total_score = 0.0
    for r in records:
        activity_counts[r.activity_type] = activity_counts.get(r.activity_type, 0) + 1
        total_score += r.score

    avg_score = total_score / len(records) if records else 0.0

    return {
        "total_documents": docs,
        "total_notes": notes_count,
        "total_flashcards": flashcards_count,
        "total_quizzes": quizzes_count,
        "total_activities": len(records),
        "activity_breakdown": activity_counts,
        "average_score": round(avg_score, 2),
    }


# --- Study Plans ---


def save_study_plan(db: Session, document_id: int, plan_content: str) -> StudyPlan:
    plan = StudyPlan(document_id=document_id, plan_content=plan_content)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_study_plans(db: Session, document_id: int | None = None) -> list[StudyPlan]:
    query = db.query(StudyPlan)
    if document_id is not None:
        query = query.filter(StudyPlan.document_id == document_id)
    return query.order_by(StudyPlan.created_at.desc()).all()
